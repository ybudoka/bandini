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
        # ⚠️ Un îlot PAR TERRE FERME : l'île n'a pas de chantier, et elle est
        # un îlot à elle (`carte.composantes_par_terre`).
        terres = carte.composantes_par_terre(_ville_a(sol))
        groupes = terres["ville"]
        assert len(groupes) == 1, f"chantier {ch['id']}, phase {numero} : {len(groupes)} îlots"
        principal = groupes[0] | terres["ile"][0]
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
    assert all(len(groupes) == 1 for groupes in carte.composantes_par_terre(_ville_a(sol)).values())


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
        assert phase["panneau"] == "À LOUER"
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
    un arbre, pas un paquet, pas une enseigne n'a bougé.

    ⚠️ La saleté se déplace APRÈS les chantiers (`salete.deplacer`) et ne jette
    rien dans leur enceinte : on la retire des deux villes."""
    from app import mobilier, salete
    monkeypatch.setattr(salete, "deplacer", lambda chantier, ville, graine: {})
    # Et les lampadaires du mobilier (`eclairer`), qui évitent les enceintes.
    monkeypatch.setattr(mobilier, "eclairer", lambda chantier, bords, solides: {})
    avec = carte.generer()
    monkeypatch.setattr(chantiers, "tirer", lambda ville, batiments, graine: [])
    sans = carte.generer()
    assert sans["chantiers"] == []
    for cle, valeur in avec.items():
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
            groupes = carte.composantes_par_terre({**ville, "sol": sol})["ville"]
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


# --- 2e vague : la boule frappe pour vrai ------------------------------------------------


@pytest.mark.parametrize("graine", [None, 7, 99, 2026])
def test_la_boule_se_pose_la_ou_elle_frappe_le_mur_debout(graine):
    """⚠️ La boule frappe POUR VRAI : à deux tuiles de la moitié debout et tournée
    vers elle, avec du mur sur sa rangée ET sur celle du dessus — la boule pend
    en l'air, une tuile plus haut à l'écran. Sans ça, elle cogne le vide pendant
    trois jours."""
    ville = VILLE if graine is None else carte.generer(graine=graine)
    # ⚠️ Sans chantier, le juge passerait à vide : c'est ce qui arrive quand la
    # boule ne trouve JAMAIS sa place (le sens inversé, par exemple).
    assert len(ville["chantiers"]) == chantiers.NOMBRE, graine
    for ch in ville["chantiers"]:
        (boule,) = ch["phases"][1]["machines"]
        assert boule["type"] == chantiers.FRAPPE
        sens, (mx, my) = boule["sens"], boule["frappe"]
        assert sens in (1, -1)
        assert (mx, my) == (boule["x"] + chantiers.PORTEE_BOULE * sens, boule["y"]), boule
        siennes = set(chantiers.tuiles(ch))
        base, demolie = ch["phases"][0]["sol"], ch["phases"][1]["sol"]
        for y in (my, my - 1):
            assert (mx, y) in siennes, (graine, ch["id"], "la boule frappe hors du bâtiment")
            glyphe = demolie[y - ch["y"]][mx - ch["x"]]
            assert glyphe == base[y - ch["y"]][mx - ch["x"]], (graine, ch["id"], "le mur frappé est tombé")
            assert carte.LEGENDE[glyphe]["solide"] == 1, (graine, ch["id"], glyphe)
        entre = chantiers.appliquer(ville["sol"], ch, 1)[my][boule["x"] + sens]
        assert carte.marchable(entre), (graine, ch["id"], "entre la boule et le mur, il reste un mur")
        # Tournée vers la moitié DEBOUT : de l'autre côté, tout est tombé.
        derriere = boule["x"] - sens
        if (derriere, my) in siennes:
            assert demolie[my - ch["y"]][derriere - ch["x"]] == chantiers.GRAVATS, (graine, ch["id"])


#: Une maison ÉCHANCRÉE : les colonnes 5 et 6 n'ont qu'une tuile, au
#: rez-de-chaussée. La moitié ouest tombée, les deux seules places d'où la boule
#: atteint la moitié est — (3, 3) et (4, 3) — frapperaient un mur d'une tuile de
#: haut : à l'écran, la boule pend une tuile plus haut et cogne le vide.
_MAISON_ECHANCREE = [
    "BBBBBBBBBB",
    "BPPPP..PPB",
    "BPPPP..PPB",
    "BFFFFFFFFB",
    "..........",
    "..........",
]


def test_la_boule_ne_frappe_pas_un_mur_sans_rien_au_dessus():
    """⚠️ La garde de la rangée du dessus : aucune maison de la graine livrée ne
    l'exerce, d'où la carte écrite à la main."""
    tuiles = [(x, y) for y in (1, 2) for x in (1, 2, 3, 4, 7, 8)] + [(x, 3) for x in range(1, 9)]
    ville = {"sol": _MAISON_ECHANCREE}
    libres = chantiers.libres(ville, [{"tuiles": tuiles, "genre": "maisons"}])
    assert len(libres) == 1, "la maison échancrée devrait être démolissable"
    assert chantiers._phases(ville["sol"], libres[0], _DeFixe(est=False)) is None, \
        "la boule frapperait un mur d'une tuile de haut"
    phases = chantiers._phases(ville["sol"], libres[0], _DeFixe(est=True))
    assert phases is not None, "l'autre moitié tombée, la boule a son mur entier"
    (boule,) = phases[1]["machines"]
    assert (boule["x"], boule["y"], boule["sens"], boule["frappe"]) == (6, 3, -1, [4, 3])


# --- 3e vague : la tranchée et l'équipe -----------------------------------------------

#: La graine livrée et trois autres : sur chacune, chaque chantier trouve sa rue.
GRAINES_DE_LA_RUE = (carte.GRAINE, 7, 99, 2026)


def _villes_de_la_rue():
    return [(g, VILLE if g == carte.GRAINE else carte.generer(graine=g)) for g in GRAINES_DE_LA_RUE]


def _facade_du_bas(ville: dict, ch: dict) -> int:
    tuiles = set(chantiers.tuiles(ch))
    return max(y for x, y in tuiles
               if (x, y + 1) not in tuiles and carte.marchable(ville["sol"][y + 1][x]))


def test_les_chantiers_ont_leur_tranchee():
    """⚠️ Une tranchée est facultative (une rue fermée devant la façade n'en laisse
    pas la place), mais un juge qui ne la verrait jamais laisserait la règle mourir
    sans rougir : la graine livrée les a toutes, et deux chantiers sur trois
    partout ailleurs."""
    for ch in VILLE["chantiers"]:
        assert len(ch["tranchee"]) == chantiers.TRANCHEE_TUILES, ch["id"]
    creusees = tous = 0
    for _graine, ville in _villes_de_la_rue():
        for ch in ville["chantiers"]:
            tous += 1
            creusees += len(ch["tranchee"]) == chantiers.TRANCHEE_TUILES
            assert len(ch["tranchee"]) in (0, chantiers.TRANCHEE_TUILES), ch["tranchee"]
    assert creusees * 3 >= tous * 2, (creusees, tous)


def test_la_tranchee_est_de_l_asphalte_ou_rien_d_autre_ne_parle():
    """⚠️ Deux tuiles de suite, sur la même rangée, d'asphalte nu — et jamais là où
    quelque chose d'autre parle déjà : croisement, ligne d'arrêt, nid, entrave,
    pont, barrière, bris d'aqueduc."""
    for graine, ville in _villes_de_la_rue():
        sol = ville["sol"]
        boites = [(r["x"], r["y"], r["l"], r["h"])
                  for cle in ("intersections", "entraves", "fermetures", "ponts", "barrieres")
                  for r in ville[cle]]
        arrets = {tuple(int(n) for n in cle.split(",")) for cle in ville["arrets"]}
        nids = {(n["x"], n["y"]) for n in ville["nids_de_poule"]}
        for ch in ville["chantiers"]:
            tuiles = set(chantiers.tuiles(ch))
            bas = _facade_du_bas(ville, ch)
            if not ch["tranchee"]:
                continue
            assert len({y for _, y in ch["tranchee"]}) == 1, "la tranchée change de rangée"
            xs = sorted(x for x, _ in ch["tranchee"])
            assert xs == list(range(xs[0], xs[0] + len(xs))), "la tranchée a un trou"
            for x, y in ch["tranchee"]:
                clef = (graine, ch["id"], x, y)
                assert sol[y][x] == chantiers.ASPHALTE, clef
                assert (x, y) not in tuiles, clef
                assert bas < y <= bas + chantiers.TRANCHEE_PORTEE, ("loin de la façade", clef)
                assert (x, y) not in arrets and (x, y) not in nids, clef
                assert not any(bx <= x < bx + bl and by <= y < by + bh for bx, by, bl, bh in boites), clef
                for a in ville["aqueducs"]:
                    assert max(abs(x - a["x"]), abs(y - a["y"])) > chantiers.RAYON_AQUEDUC, clef


def test_la_tranchee_est_la_premiere_chaussee_sous_la_facade():
    """Pas la dixième : une tranchée au bout de la rue n'est plus celle du chantier.
    Aucune rangée plus près de la façade n'offrait deux tuiles d'asphalte libres."""
    for graine, ville in _villes_de_la_rue():
        for ch in ville["chantiers"]:
            if not ch["tranchee"]:
                continue
            y = ch["tranchee"][0][1]
            bas = _facade_du_bas(ville, ch)
            libres = chantiers._tranchee(ville, {"tuiles": chantiers.tuiles(ch), "sur_rue": [(ch["x"], bas)]},
                                         carte.Des(1))
            assert libres and libres[0][1] == y, (graine, ch["id"], libres, y)


def test_la_tranchee_ne_change_aucune_tuile():
    """⚠️ Elle se PEINT et se SENT : la ville qu'un juge de géométrie a validée à
    chaque phase est exactement celle du jeu."""
    for _graine, ville in _villes_de_la_rue():
        for ch in ville["chantiers"]:
            rue = {tuple(t) for t in ch["tranchee"]}
            for numero in range(chantiers.DERNIERE + 1):
                sol = chantiers.appliquer(ville["sol"], ch, numero)
                touchees = {(x, y) for y, ligne in enumerate(sol)
                            for x, glyphe in enumerate(ligne) if glyphe != ville["sol"][y][x]}
                assert not touchees & rue, (ch["id"], numero)


def test_la_tranchee_suit_les_phases():
    """Rien tant que le terrain n'est pas rasé, des plaques tant qu'on y travaille,
    et l'asphalte refait quand le neuf est debout."""
    for _graine, ville in _villes_de_la_rue():
        for ch in ville["chantiers"]:
            vues = [p["tranchee"] for p in ch["phases"]]
            attendues = [None, None, "plaques", "plaques", "rapiece"] if ch["tranchee"] else [None] * 5
            assert vues == attendues, (ch["id"], vues)


def test_une_ville_sans_rue_devant_n_a_pas_de_tranchee():
    """La garde du refus : sans deux tuiles libres, le chantier n'a pas de
    tranchée — et ne s'en trouve pas refusé."""
    sol = ["BBBBBBBB", "BPPPPPPB", "BFFFFFFB", "........", "........"]
    libre = {"tuiles": [(x, y) for y in (1, 2) for x in range(1, 7)], "sur_rue": [(x, 2) for x in range(1, 7)]}
    ville = {"sol": sol, "arrets": {}, "intersections": [], "nids_de_poule": [], "aqueducs": []}
    assert chantiers._tranchee(ville, libre, carte.Des(1)) == []


@pytest.mark.parametrize("de_la_rue", ["intersections", "entraves", "ponts", "barrieres", "fermetures"])
def test_la_tranchee_evite_ce_qui_parle_deja(de_la_rue):
    """Chaque exclusion a sa carte : sur une rue d'asphalte, on la couvre d'un de
    ces endroits et la tranchée n'y tombe plus — il n'y a plus nulle part où aller."""
    sol = ["BBBBBBBB", "BPPPPPPB", "BFFFFFFB", "........", "........", "########", "########"]
    libre = {"tuiles": [(x, y) for y in (1, 2) for x in range(1, 7)], "sur_rue": [(x, 2) for x in range(1, 7)]}
    base = {"sol": sol, "arrets": {}, "intersections": [], "nids_de_poule": [], "aqueducs": []}
    assert chantiers._tranchee(base, libre, carte.Des(1)), "sans obstacle, la rue est libre"
    couvert = {**base, de_la_rue: [{"x": 0, "y": 5, "l": 8, "h": 2}]}
    assert chantiers._tranchee(couvert, libre, carte.Des(1)) == []


def test_la_tranchee_evite_les_lignes_d_arret_les_nids_et_les_bris():
    sol = ["BBBBBBBB", "BPPPPPPB", "BFFFFFFB", "........", "........", "########", "########"]
    libre = {"tuiles": [(x, y) for y in (1, 2) for x in range(1, 7)], "sur_rue": [(x, 2) for x in range(1, 7)]}
    base = {"sol": sol, "arrets": {}, "intersections": [], "nids_de_poule": [], "aqueducs": []}
    toute_la_rue = {f"{x},{y}": "<" for x in range(8) for y in (5, 6)}
    assert chantiers._tranchee({**base, "arrets": toute_la_rue}, libre, carte.Des(1)) == []
    tous_les_nids = [{"x": x, "y": y} for x in range(8) for y in (5, 6)]
    assert chantiers._tranchee({**base, "nids_de_poule": tous_les_nids}, libre, carte.Des(1)) == []
    assert chantiers._tranchee({**base, "aqueducs": [{"x": 3, "y": 5}]}, libre, carte.Des(1)) == []


def test_l_equipe_tient_ses_postes():
    """Personne sur une maison condamnée ni sur le neuf ; à chaque phase des
    hommes sur du sol libre, à portée de leur machine, jamais dans un couloir."""
    # ⚠️ En toutes lettres, pas relu dans la constante : un juge qui lit ce qu'il
    # juge ne rougit jamais.
    assert set(chantiers.EQUIPE) == {1, 2, 3}, "du monde sur une maison condamnée ou sur le neuf"
    for graine, ville in _villes_de_la_rue():
        for ch in ville["chantiers"]:
            tuiles = set(chantiers.tuiles(ch))
            for numero, phase in enumerate(ch["phases"]):
                postes = [tuple(p) for p in phase["equipe"]]
                clef = (graine, ch["id"], numero)
                assert len(postes) <= chantiers.EQUIPE.get(numero, 0), clef
                if numero not in chantiers.EQUIPE:
                    assert not postes, ("un homme sur un chantier fermé", clef)
                sol = chantiers.appliquer(ville["sol"], ch, numero)
                machines = {(m["x"], m["y"]) for m in phase["machines"]}
                for x, y in postes:
                    assert (x, y) in tuiles, clef
                    assert carte.marchable(sol[y][x]) and (x, y) not in machines, clef
                    for vx, vy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        assert carte.marchable(sol[y + vy][x + vx]) and (x + vx, y + vy) not in machines, \
                            ("dans un couloir", clef)
                    ecart = min(max(abs(x - mx), abs(y - my)) for mx, my in machines)
                    assert chantiers.POSTE_MIN <= ecart <= chantiers.POSTE_MAX, (ecart, clef)
                for a in range(len(postes)):
                    for b in range(a + 1, len(postes)):
                        assert max(abs(postes[a][0] - postes[b][0]), abs(postes[a][1] - postes[b][1])) >= 2, clef


def test_le_terrain_a_son_equipe():
    """⚠️ Sans cette mesure, une équipe toujours vide passerait tous les juges :
    sur la graine livrée, la pelle et la grue ont chacune leurs deux hommes."""
    for ch in VILLE["chantiers"]:
        for numero in (2, 3):
            assert len(ch["phases"][numero]["equipe"]) == chantiers.EQUIPE[numero], (ch["id"], numero)
    assert any(ch["phases"][1]["equipe"] for ch in VILLE["chantiers"]), "personne à la démolition"


def test_un_poste_ne_se_prend_pas_dans_un_couloir():
    """La garde des quatre voisines : sur un terrain d'une seule rangée, chaque
    tuile est un couloir, et personne n'y est planté."""
    sol = ["BBBBBBBB", "B;;;;;;B", "BBBBBBBB"]
    tuiles = {(x, 1) for x in range(1, 7)}
    phase = {"sol": ["".join(";" for _ in range(6))], "machines": [{"x": 1, "y": 1}]}
    assert chantiers._postes(sol, 1, 1, phase, tuiles, 2, carte.Des(1)) == []
    large = ["BBBBBBBB", "B;;;;;;B", "B;;;;;;B", "B;;;;;;B", "BBBBBBBB"]
    tuiles = {(x, y) for y in (1, 2, 3) for x in range(1, 7)}
    phase = {"sol": [";;;;;;"] * 3, "machines": [{"x": 1, "y": 2}]}
    postes = chantiers._postes(large, 1, 1, phase, tuiles, 2, carte.Des(1))
    assert len(postes) == 2 and all(chantiers.POSTE_MIN <= max(abs(x - 1), abs(y - 2)) <= chantiers.POSTE_MAX
                                    for x, y in postes), postes


def test_tirer_tranchee_et_equipe_ne_deplace_pas_les_chantiers(monkeypatch):
    """⚠️ Leur PROPRE dé : les chantiers, leurs machines et leurs phases sont ceux
    d'avant la 3e vague. Sans elle, la graine livrée aurait changé de chantiers."""
    def sans(ville, libre, phases, graine, numero):
        return []
    avec = [(c["x"], c["y"], c["decalage"], c["pas"], [p["machines"] for p in c["phases"]],
             [p["sol"] for p in c["phases"]]) for c in carte.generer()["chantiers"]]
    monkeypatch.setattr(chantiers, "_annexes", sans)
    sans_eux = [(c["x"], c["y"], c["decalage"], c["pas"], [p["machines"] for p in c["phases"]],
                 [p["sol"] for p in c["phases"]]) for c in carte.generer()["chantiers"]]
    assert avec == sans_eux


# --- 4e vague : le signaleur ------------------------------------------------------------


def _rue_mini(sens: str = "<", trottoir: str = "."):
    """Une chaussée d'une voie sous un trottoir : la tranchée est en (3..4, 2)."""
    ville = {"sol": ["BBBBBBBB", trottoir * 8, "########"],
             "voie": ["........", "........", sens * 8]}
    return ville, [[3, 2], [4, 2]]


def test_chaque_tranchee_de_la_graine_livree_a_son_signaleur():
    """⚠️ Sans cette mesure, un signaleur qui ne se pose jamais passerait tous les
    juges : la graine livrée les a tous, et la tranchée est toujours sur une voie
    horizontale."""
    for ch in VILLE["chantiers"]:
        assert ch["signaleur"], f"le chantier {ch['id']} n'a pas de signaleur"


def test_le_signaleur_tient_la_voie_de_la_tranchee_depuis_le_trottoir():
    for graine, ville in _villes_de_la_rue():
        sol = ville["sol"]
        for ch in ville["chantiers"]:
            s = ch["signaleur"]
            if not ch["tranchee"]:
                assert s is None, (graine, ch["id"])
                continue
            if s is None:
                continue
            clef = (graine, ch["id"])
            (x0, y), (x1, _) = ch["tranchee"][0], ch["tranchee"][-1]
            sx, sy = s
            sens = ville["voie"][y][x0]
            assert sens in chantiers.SIGNAUX, clef
            assert sy == y - 1, clef
            assert all(ville["voie"][y][x] == sens for x in range(x0, x1 + 1)), ("pas sa voie", clef)
            # Là d'où l'on vient, sur le trottoir : jamais dans la chaussée.
            assert sx == (x1 if sens == "<" else x0), ("pas au bout amont", clef)
            glyphe = sol[sy][sx]
            assert carte.marchable(glyphe) and not carte.LEGENDE[glyphe].get("route"), ("dans la chaussée", clef)
            tuile = (sx, sy)
            for cle in chantiers.OCCUPENT:
                for objet in ville.get(cle) or []:
                    assert tuile not in chantiers._cases(objet), (cle, objet, clef)


def test_le_signaleur_n_existe_que_sur_une_tranchee():
    """⚠️ Il ne sert que pendant les plaques — et cela se lit dans `tranchee` de chaque phase,
    pas dans un drapeau de plus : le paquet de la carte est à quelques octets de son plafond."""
    for _graine, ville in _villes_de_la_rue():
        for ch in ville["chantiers"]:
            if ch["signaleur"]:
                assert ch["tranchee"], ch["id"]
                assert [p["tranchee"] for p in ch["phases"]] == [None, None, "plaques", "plaques", "rapiece"]
            assert all("signaleur" not in p for p in ch["phases"]), "un drapeau par phase : le paquet enfle"
            assert ch["signaleur"] is None or len(ch["signaleur"]) == 2, ch["signaleur"]


def test_le_signaleur_se_met_a_l_amont_de_chaque_sens():
    """Les graines livrées n'ont que des voies « < » : la carte écrite à la main
    juge l'autre bout."""
    ville, rue = _rue_mini("<")
    assert chantiers._signaleur(ville, rue) == [4, 1]
    ville, rue = _rue_mini(">")
    assert chantiers._signaleur(ville, rue) == [3, 1]


@pytest.mark.parametrize("cas", ["nord_sud", "voies_mixtes", "chaussee", "meuble", "sans_tranchee"])
def test_le_signaleur_a_ses_refus(cas):
    """Chaque refus a sa carte : une voie qui ne va pas de l'est à l'ouest, une voie
    à deux sens sous la tranchée, un trottoir qui est une chaussée, une tuile déjà
    prise par un meuble — et le chantier n'en est pas refusé pour autant."""
    ville, rue = _rue_mini("<")
    assert chantiers._signaleur(ville, rue), "sans refus, il se pose"
    if cas == "nord_sud":
        ville["voie"][2] = "v" * 8
    elif cas == "voies_mixtes":
        ville["voie"][2] = "<<<<>>>>"   # la tranchée est sur les colonnes 3 et 4
    elif cas == "chaussee":
        ville["sol"][1] = "#" * 8
    elif cas == "meuble":
        ville["decor"] = [{"type": "banc", "x": 4, "y": 1}]
    elif cas == "sans_tranchee":
        rue = []
    assert chantiers._signaleur(ville, rue) is None
