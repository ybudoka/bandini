"""Ça travaille : les juges des chantiers.

⚠️ Une ville qui change casse ce qui comptait sur elle. Les juges de la carte
(`test_carte.py`) regardent la ville du premier matin, une fois. Ceux-ci les
REJOUENT à chaque phase de chaque chantier — c'est la leçon de la tentative du
trottoir : neuf juges rougissent d'un coup quand la ville bouge, et c'est à ça
qu'ils servent.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from app import carte, chantiers

VILLE = carte.generer()
RACINE = Path(__file__).resolve().parent.parent


def _machines_en_murs(sol: list[str], machines: list[dict]) -> list[str]:
    """Une machine est un MUR pour qui marche : on la pose dans le sol comme un
    toit, et la ville doit tenir quand même."""
    lignes = list(sol)
    for m in machines:
        ligne = lignes[m["y"]]
        lignes[m["y"]] = ligne[:m["x"]] + "B" + ligne[m["x"] + 1:]
    return lignes


def _ville_a(sol: list[str]) -> dict:
    return {**VILLE, "sol": sol}


def test_la_ville_a_ses_chantiers():
    assert 2 <= len(VILLE["chantiers"]) <= chantiers.NOMBRE, len(VILLE["chantiers"])


def test_un_chantier_ne_touche_jamais_a_ce_qui_sert():
    """⚠️ Le piège 1 du plan : on ne démolit pas la quincaillerie le jour où une
    mission y envoie. Ni sur le bâtiment, ni sur les deux tuiles devant lui."""
    sert = chantiers.cases_qui_servent(VILLE)
    for ch in VILLE["chantiers"]:
        siennes = set(chantiers.tuiles(ch))
        devant = {(x, y + j) for x, y in siennes if (x, y + 1) not in siennes for j in (1, 2)}
        assert not (siennes | devant) & sert, f"le chantier {ch['id']} tombe sur ce qui sert"
        for porte in VILLE["portes"]:
            assert (porte["x"], porte["y"]) not in siennes, (ch["id"], porte)
        for point in VILLE["points_interet"]:
            assert (point["x"], point["y"]) not in siennes | devant, (ch["id"], point)


def test_on_ne_demolit_ni_un_commerce_ni_un_logement_qu_on_visite():
    portes = {(p["x"], p["y"]) for p in VILLE["portes"]}
    for ch in VILLE["chantiers"]:
        siennes = set(chantiers.tuiles(ch))
        for d in VILLE["devantures"]:
            assert not {(d["x"] + i, d["y"]) for i in range(d["l"])} & siennes, (ch["id"], d)
        for r in VILLE["residences"]:
            cases = {(r["x"] + i, r["y"]) for i in range(r["l"])}
            if cases & portes:
                assert not cases & siennes, f"un logement visitable passe en chantier : {r}"


def test_jamais_dans_une_cour_de_gang():
    for ch in VILLE["chantiers"]:
        assert ch["genre"] in chantiers.GENRES, ch["genre"]


@pytest.mark.parametrize("numero", range(chantiers.DERNIERE + 1))
def test_a_chaque_phase_la_ville_reste_d_un_seul_tenant(numero):
    """⚠️ Le piège 3 : les juges de géométrie se rejouent à CHAQUE phase. Une
    maison rasée au fond d'une cour murée serait une poche où l'on naît sans
    pouvoir sortir — et ses machines comptent comme des murs."""
    depart = VILLE["apparition"]["joueur"]
    for ch in VILLE["chantiers"]:
        phase = ch["phases"][numero]
        sol = _machines_en_murs(chantiers.appliquer(VILLE["sol"], ch, numero), phase["machines"])
        groupes = carte.composantes_marchables(_ville_a(sol))
        assert len(groupes) == 1, f"chantier {ch['id']}, phase {numero} : {len(groupes)} îlots"
        principal = groupes[0]
        assert (depart["x"], depart["y"]) in principal
        for point in VILLE["points_interet"]:
            assert (point["x"], point["y"]) in principal, (ch["id"], numero, point)
        for porte in VILLE["portes"]:
            assert (porte["x"], porte["y"] + 1) in principal, (ch["id"], numero, porte)


def test_au_premier_matin_tous_les_chantiers_ensemble_tiennent():
    """Les phases du premier matin, toutes posées en même temps — la ville que le
    joueur découvre vraiment."""
    sol = VILLE["sol"]
    for ch in VILLE["chantiers"]:
        numero = chantiers.phase_du_jour(ch, 1, 1)
        sol = _machines_en_murs(chantiers.appliquer(sol, ch, numero), ch["phases"][numero]["machines"])
    assert len(carte.composantes_marchables(_ville_a(sol))) == 1


def test_les_phases_sont_des_rectangles_de_glyphes_connus():
    for ch in VILLE["chantiers"]:
        assert len(ch["phases"]) == len(chantiers.PHASES)
        assert len(ch["masque"]) == ch["h"] and all(len(r) == ch["l"] for r in ch["masque"])
        for numero, phase in enumerate(ch["phases"]):
            assert len(phase["sol"]) == ch["h"], (ch["id"], numero)
            for rangee in phase["sol"]:
                assert len(rangee) == ch["l"], (ch["id"], numero)
                assert set(rangee) <= set(carte.LEGENDE), set(rangee) - set(carte.LEGENDE)


def test_la_phase_zero_est_la_ville_du_generateur():
    """Rien ne bouge avant que l'horloge ne tourne : la phase 0 est la ville telle
    que `generer` l'a posée, tuile pour tuile."""
    for ch in VILLE["chantiers"]:
        assert chantiers.appliquer(VILLE["sol"], ch, 0) == VILLE["sol"], ch["id"]


def test_on_ne_touche_que_les_tuiles_du_batiment():
    """⚠️ Le rectangle d'un chantier déborde du bâtiment quand celui-ci est en L :
    ce qui n'est pas à lui ne change à aucune phase."""
    for ch in VILLE["chantiers"]:
        siennes = set(chantiers.tuiles(ch))
        base = ch["phases"][0]["sol"]
        for numero, phase in enumerate(ch["phases"]):
            for j, rangee in enumerate(phase["sol"]):
                for i, glyphe in enumerate(rangee):
                    if (ch["x"] + i, ch["y"] + j) not in siennes:
                        assert glyphe == base[j][i], (ch["id"], numero, i, j)


def test_la_demolition_garde_debout_une_moitie_entiere():
    """La phase 1 : la moitié qui tient n'a pas bougé d'une tuile — sinon on verrait
    le dos d'un toit là où il y avait une façade."""
    for ch in VILLE["chantiers"]:
        siennes = set(chantiers.tuiles(ch))
        base, demolie = ch["phases"][0]["sol"], ch["phases"][1]["sol"]
        debout = tombees = 0
        colonnes_tombees = set()
        for j in range(ch["h"]):
            for i in range(ch["l"]):
                if (ch["x"] + i, ch["y"] + j) not in siennes:
                    continue
                if demolie[j][i] == chantiers.GRAVATS:
                    tombees += 1
                    colonnes_tombees.add(i)
                else:
                    assert demolie[j][i] == base[j][i]
                    debout += 1
        assert debout and tombees, f"chantier {ch['id']} : pas une moitié"
        # Chaque colonne tombe entière ou pas du tout.
        for i in colonnes_tombees:
            for j in range(ch["h"]):
                if (ch["x"] + i, ch["y"] + j) in siennes:
                    assert demolie[j][i] == chantiers.GRAVATS, (ch["id"], i, j)


def test_raser_puis_couler_libere_tout_le_batiment():
    for ch in VILLE["chantiers"]:
        for j, (rase, dalle) in enumerate(zip(ch["phases"][2]["sol"], ch["phases"][3]["sol"])):
            for i in range(ch["l"]):
                if ch["masque"][j][i] == "X":
                    assert rase[i] == chantiers.GRAVATS and dalle[i] == chantiers.DALLE
                    assert carte.marchable(rase[i]) and carte.marchable(dalle[i])


def test_le_neuf_reprend_exactement_l_empreinte():
    """La ville revient à la même géométrie : même murs, aux mêmes tuiles."""
    for ch in VILLE["chantiers"]:
        for j, (avant, apres) in enumerate(zip(ch["phases"][0]["sol"], ch["phases"][4]["sol"])):
            for i in range(ch["l"]):
                assert carte.solidite(avant[i]) == carte.solidite(apres[i]), (ch["id"], i, j)


def test_une_porte_demolie_ne_reste_pas_debout():
    """⚠️ Le piège 2 : une porte sur un terrain rasé mène à un intérieur qui
    flotte. Pendant la démolition, plus aucune porte dans le bâtiment tombé."""
    for ch in VILLE["chantiers"]:
        for numero in (2, 3):
            for j, rangee in enumerate(ch["phases"][numero]["sol"]):
                for i, glyphe in enumerate(rangee):
                    if ch["masque"][j][i] == "X":
                        assert glyphe not in carte.PORTES_DE_FACADE, (ch["id"], numero, glyphe)


def test_le_neuf_a_une_porte_peinte_qui_donne_sur_la_rue():
    """Une porte, toujours — mais peinte et fermée : le neuf n'a pas d'intérieur,
    donc il ne promet pas qu'on y entre."""
    for ch in VILLE["chantiers"]:
        phase = ch["phases"][chantiers.DERNIERE]
        assert phase["porte"], ch["id"]
        px, py = phase["porte"]
        i, j = px - ch["x"], py - ch["y"]
        assert ch["masque"][j][i] == "X"
        assert phase["sol"][j][i] == "F", "une porte peinte sur une vitrine"
        assert carte.marchable(VILLE["sol"][py + 1][px]), "la porte du neuf donne sur un mur"
        assert phase["panneau"] == "A LOUER"
    for ch in VILLE["chantiers"]:
        assert all(p["porte"] is None for p in ch["phases"][:chantiers.DERNIERE])


def test_les_machines_travaillent_sur_le_sol_de_leur_phase():
    for ch in VILLE["chantiers"]:
        for numero, phase in enumerate(ch["phases"]):
            attendues = chantiers.MACHINES.get(numero, ())
            assert tuple(m["type"] for m in phase["machines"]) == attendues, (ch["id"], numero)
            sol = chantiers.appliquer(VILLE["sol"], ch, numero)
            for m in phase["machines"]:
                assert ch["masque"][m["y"] - ch["y"]][m["x"] - ch["x"]] == "X", m
                assert carte.marchable(sol[m["y"]][m["x"]]), m
                for vx, vy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    assert carte.marchable(sol[m["y"] + vy][m["x"] + vx]), (m, "coincée")
            places = [(m["x"], m["y"]) for m in phase["machines"]]
            assert len(places) == len(set(places)), "deux machines sur la même tuile"


def test_les_phases_avancent_avec_les_jours():
    """⚠️ Un chantier est une HORLOGE : une phase tous les `pas` jours, à partir de
    son décalage, jamais en arrière, et le neuf ne se redémolit pas."""
    for ch in VILLE["chantiers"]:
        assert ch["pas"] in chantiers.PAS_JOURS
        vues = [chantiers.phase_du_jour(ch, jour, 1) for jour in range(1, 40)]
        assert vues[0] == ch["decalage"]
        assert vues == sorted(vues), "un chantier recule"
        assert vues[-1] == chantiers.DERNIERE
        for jour in range(1, 30):
            avant = chantiers.phase_du_jour(ch, jour, 1)
            if avant < chantiers.DERNIERE:
                assert chantiers.phase_du_jour(ch, jour + ch["pas"], 1) == avant + 1
        # Une partie commencée plus tard repart du même premier matin.
        assert chantiers.phase_du_jour(ch, 50, 50) == ch["decalage"]
        # Et une sauvegarde bricolée ne fait pas reculer le temps.
        assert chantiers.phase_du_jour(ch, 3, 10) == ch["decalage"]


def test_au_premier_matin_les_chantiers_ne_sont_pas_au_meme_stade():
    """Sinon il faut trois jours de jeu avant de voir la moindre machine."""
    phases = [chantiers.phase_du_jour(ch, 1, 1) for ch in VILLE["chantiers"]]
    assert len(set(phases)) == len(phases), phases
    assert any(chantiers.MACHINES.get(p) for p in phases), "aucune machine au premier matin"


def test_la_ville_est_neuve_au_bout_de_vingt_jours():
    for ch in VILLE["chantiers"]:
        assert chantiers.phase_du_jour(ch, 1 + 20, 1) == chantiers.DERNIERE, ch


def test_deux_chantiers_ne_se_voisinent_pas():
    centres = [(ch["x"] + ch["l"] / 2, ch["y"] + ch["h"] / 2) for ch in VILLE["chantiers"]]
    for a in range(len(centres)):
        for b in range(a + 1, len(centres)):
            ecart = max(abs(centres[a][0] - centres[b][0]), abs(centres[a][1] - centres[b][1]))
            assert ecart >= chantiers.ECART_MIN, (a, b, ecart)


def test_la_ville_avec_ou_sans_chantiers_est_la_meme(monkeypatch):
    """⚠️ Les chantiers tirent dans LEUR dé, après toute la ville : sans eux, pas
    un arbre, pas un paquet, pas une enseigne n'a bougé."""
    monkeypatch.setattr(chantiers, "tirer", lambda ville, batiments, graine: [])
    sans = carte.generer()
    assert sans["chantiers"] == []
    for cle, valeur in VILLE.items():
        if cle != "chantiers":
            assert sans[cle] == valeur, f"« {cle} » change quand on ajoute les chantiers"


def test_les_chantiers_ne_dependent_pas_de_l_empreinte_des_chaines():
    """⚠️ La leçon de `PYTHONHASHSEED` : un ensemble de chaînes parcouru, et la
    ville change d'un processus à l'autre. Deux processus, deux graines de
    hachage, les mêmes chantiers."""
    code = ("import json; from app import carte; "
            "print(json.dumps(carte.generer()['chantiers'], sort_keys=True))")
    sorties = []
    for graine in ("1", "4242"):
        env = {**os.environ, "PYTHONHASHSEED": graine}
        r = subprocess.run([sys.executable, "-c", code], cwd=RACINE, env=env,
                           capture_output=True, text=True, check=True)
        sorties.append(json.loads(r.stdout))
    assert sorties[0] == sorties[1]


@pytest.mark.parametrize("graine", [7, 99, 2026])
def test_les_regles_tiennent_sur_d_autres_graines(graine):
    ville = carte.generer(graine=graine)
    assert ville["chantiers"], f"aucun chantier pour la graine {graine}"
    sert = chantiers.cases_qui_servent(ville)
    for ch in ville["chantiers"]:
        assert not set(chantiers.tuiles(ch)) & sert, (graine, ch["id"])
        for numero, phase in enumerate(ch["phases"]):
            sol = _machines_en_murs(chantiers.appliquer(ville["sol"], ch, numero), phase["machines"])
            groupes = carte.composantes_marchables({**ville, "sol": sol})
            assert len(groupes) == 1, (graine, ch["id"], numero, len(groupes))


class _DeFixe:
    """Un dé qui répond toujours la même chose : pour choisir QUELLE moitié tombe."""

    def __init__(self, est: bool) -> None:
        self.est = est

    def chance(self, p: float) -> bool:
        return self.est

    def entier(self, a: int, b: int) -> int:
        return a


#: Une maison dont la moitié OUEST est murée de trois côtés : au nord, à l'ouest
#: et au sud, des murs ; à l'est, l'autre moitié. Seule la moitié est donne sur
#: la rue. Démolir l'ouest d'abord ferait une poche où l'on naît sans sortir.
_COUR_MUREE = [
    "BBBBBBBBBB",
    "BPPPPPPPPB",
    "BPPPPPPPPB",
    "BFFFFFFFFB",
    "BBBBB....B",
    "..........",
]


def _maison_de_la_cour():
    tuiles = [(x, y) for y in (1, 2, 3) for x in range(1, 9)]
    ville = {"sol": _COUR_MUREE}
    libres = chantiers.libres(ville, [{"tuiles": tuiles, "genre": "maisons"}])
    assert len(libres) == 1, "la maison de la cour devrait être démolissable"
    return ville, libres[0]


def test_une_demolition_qui_murerait_une_poche_est_refusee():
    """⚠️ La garde que la ville du jeu n'exerce pas (aucun bâtiment de la graine
    livrée ne tombe dans ce cas) : sans ce cas écrit à la main, on pourrait la
    retirer sans qu'aucun juge ne rougisse."""
    ville, libre = _maison_de_la_cour()
    assert chantiers._phases(ville["sol"], libre, _DeFixe(est=False)) is None, \
        "la moitié murée tombe et fait une poche"
    phases = chantiers._phases(ville["sol"], libre, _DeFixe(est=True))
    assert phases is not None, "la moitié qui donne sur la rue doit pouvoir tomber"
    for numero, phase in enumerate(phases):
        sol = _machines_en_murs(chantiers.appliquer(
            ville["sol"], {"x": 1, "y": 1, "phases": phases}, numero), phase["machines"])
        assert len(carte.composantes_marchables({"sol": sol})) == 1, numero


def test_une_machine_qui_coupe_un_couloir_est_refusee():
    """Une machine est un mur : posée en travers du seul passage, elle enferme ce
    qui est derrière elle."""
    sol = ["BBBBBB",
           "B;;;;B",
           "BBBBBB",
           "......"]
    tuiles = {(1, 1), (2, 1), (3, 1), (4, 1)}
    # Le couloir de friche ne touche la rue que par (4,1)... qui n'a rien au sud :
    # sans machine il est déjà enfermé.
    assert not chantiers._touche_la_ville(sol, tuiles, set(), tuiles)
    ouvert = ["BBBBBB",
              "B;;;;.",
              "BBBBBB",
              "......"]
    assert chantiers._touche_la_ville(ouvert, tuiles, set(), tuiles)
    # Une machine au bout du couloir, et le reste ne sort plus.
    assert not chantiers._touche_la_ville(ouvert, tuiles, {(4, 1)}, tuiles)
