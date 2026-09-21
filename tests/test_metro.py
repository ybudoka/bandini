"""Le métro, jugé en Python : les édicules, la ligne, l'horaire, le quai et la rame.

Demande de Martin (16 sept. 2026) : « je veux aussi un métro » — souterrain.

⚠️ **Tout ce qui peut rater en surface se juge ici** : un édicule qu'on ne peut
pas atteindre à pied, planté devant une porte ou sur le parvis du terminus, une
station trop loin de son lieu, une rame qui ne passe qu'une fois par minute.
"""

import pytest

from app import autobus, carte, metro, mobilier


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


#: Le dessin de l'édicule selon le côté du trottoir. ⚠️ En toutes lettres, pas
#: relu dans `metro.EDICULES` : un juge qui relit la table qu'il juge ne rougit pas.
REGARDE = {1: "edicule", -1: "edicule_nord"}


def test_six_stations_dans_l_ordre_de_la_boucle(ville):
    stations = ville["metro"]["stations"]
    assert [s["nom"] for s in stations] == [nom for _slug, nom in metro.LIGNE["stations"]]
    assert "Faubourg" in [s["nom"] for s in stations] and "La Pointe" in [s["nom"] for s in stations]


def test_chaque_station_a_son_edicule_qui_regarde_la_rue(ville):
    decor = {(d["x"], d["y"]): d["type"] for d in ville["decor"]}
    for rang, s in enumerate(ville["metro"]["stations"]):
        sx, sy = metro.sortie(ville, rang)
        assert ville["sol"][sy][sx] == ".", f"{s['nom']} : on n'attend pas sur un trottoir"
        assert ville["sol"][s["y"]][s["x"]] == "_", f"{s['nom']} : l'édicule n'est pas sur l'abord"
        rue = sy - s["y"]
        assert ville["voie"][sy + rue][sx] != ".", f"{s['nom']} : pas de rue derrière le trottoir"
        assert decor.get((s["x"], s["y"])) == REGARDE[rue], f"{s['nom']} : {decor.get((s['x'], s['y']))}"


def test_chaque_station_est_pres_de_son_lieu(ville):
    lieux = {p["slug"]: p for p in ville["points_interet"]}
    for (slug, nom), s in zip(metro.LIGNE["stations"], ville["metro"]["stations"]):
        lieu = lieux[slug]
        ecart = abs(s["x"] - lieu["x"]) + abs(s["y"] - lieu["y"])
        assert ecart <= 2 * metro.RAYON, f"{nom} : à {ecart} tuiles de {lieu['nom']}"


def test_on_atteint_chaque_edicule_a_pied(ville):
    """Depuis le terminus, sans enjamber de clôture, en contournant tout le décor
    solide — édicules et mobilier compris."""
    sol, largeur, hauteur = ville["sol"], ville["largeur"], ville["hauteur"]
    bloque = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] in carte.DECOR_SOLIDE}
    depart = tuple(autobus.detail(ville, 0)["quai"])
    vus, pile = {depart}, [depart]
    while pile:
        x, y = pile.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (0 <= n[0] < largeur and 0 <= n[1] < hauteur and n not in vus
                    and carte.marchable(sol[n[1]][n[0]]) and n not in bloque):
                vus.add(n)
                pile.append(n)
    for rang, s in enumerate(ville["metro"]["stations"]):
        assert metro.sortie(ville, rang) in vus, f"{s['nom']} : on n'atteint pas l'escalier à pied"


def test_un_edicule_n_est_ni_devant_une_porte_ni_sur_le_parvis(ville):
    devant = {(p["x"] + i, p["y"] + j) for p in ville["portes"] for j in (1, 2, 3) for i in (-1, 0, 1)}
    nus = autobus.parvis(ville)
    for s in ville["metro"]["stations"]:
        assert (s["x"], s["y"]) not in devant, f"{s['nom']} : devant une porte"
        assert (s["x"], s["y"]) not in nus, f"{s['nom']} : sur le parvis du terminus"


def test_la_rame_passe_souvent_et_le_plus_long_trajet_est_sous_la_baie(ville):
    m = ville["metro"]
    h = m["horaire"]
    assert len(m["trajets"]) == len(m["stations"])
    assert all(t >= metro.HORAIRE["trajet_min"] for t in m["trajets"])
    periode = sum(m["trajets"]) + len(m["trajets"]) * h["arret_images"]
    attente = periode / h["rames"] / 60
    assert attente < 40, f"une rame toutes les {attente:.0f} s"
    noms = [s["nom"] for s in m["stations"]]
    long = m["trajets"].index(max(m["trajets"]))
    assert (noms[long], noms[(long + 1) % len(noms)]) == ("La Pointe", "Les Quais"), "le tunnel sous la baie"
    assert m["trajets"] == metro.trajets(m["stations"])


def test_le_quai_a_son_tunnel_et_la_rame_sa_porte(ville):
    """Le quai : deux rangées de tunnel que `metro.js` peint, la barrière vitrée,
    et l'escalier en bas. La rame : ses vitres en haut, sa porte en bas. Un point
    `rame` dans les deux : c'est lui qu'ACTION sert."""
    quai, rame = ville["interieurs"]["metro_quai"], ville["interieurs"]["metro_rame"]
    assert set(quai["sol"][0]) == {"B"} and set(quai["sol"][1]) == {"B"}
    assert set(quai["sol"][2][1:-1]) == {"W"}
    assert set(rame["sol"][0][1:-1]) <= {"W", "B"} and "W" in rame["sol"][0]
    for piece in (quai, rame):
        assert [p for p in piece["points"] if p["type"] == "rame"], f"{piece['slug']} : pas de point rame"
    point = next(p for p in quai["points"] if p["type"] == "rame")
    assert point["y"] == 3, "on monte depuis le bord du quai, contre la barrière"


def test_le_metro_ne_deplace_rien_de_la_ville(monkeypatch):
    """⚠️ Son propre ordre : sans le métro (et sans le mobilier, qui vient après
    lui), la ville est la même tuile pour tuile, et les édicules ne font que
    s'ajouter au bout du décor.

    ⚠️ La saleté se déplace APRÈS le métro (`salete.deplacer`) et contourne ses
    édicules, comme le mobilier : on la retire des deux villes."""
    from app import devants, salete
    monkeypatch.setattr(salete, "deplacer", lambda chantier, ville, graine: {})
    monkeypatch.setattr(mobilier, "semer", lambda chantier, ville, graine: {})
    # ⚠️ Le devant des portes vient APRES tout et lit les edicules pour n'y rien poser : il part
    # des deux villes, comme la saleté.
    monkeypatch.setattr(devants, "deplacer", lambda chantier, ville: {})
    avec = carte.generer()
    monkeypatch.setattr(metro, "creuser", lambda chantier, ville: {})
    sans = carte.generer()
    for cle in sans:
        if cle in ("decor", "metro"):
            continue
        assert avec[cle] == sans[cle], f"« {cle} » a bougé"
    assert avec["decor"][:len(sans["decor"])] == sans["decor"]
    assert {d["type"] for d in avec["decor"][len(sans["decor"]):]} <= set(REGARDE.values())
    assert len(avec["decor"]) - len(sans["decor"]) == len(metro.LIGNE["stations"])


@pytest.mark.parametrize("graine", [1, 7, 99])
def test_le_metro_se_creuse_sur_d_autres_graines(graine):
    ville = carte.generer(graine=graine)
    assert len(ville["metro"]["stations"]) == len(metro.LIGNE["stations"])
    for rang in range(len(ville["metro"]["stations"])):
        sx, sy = metro.sortie(ville, rang)
        assert ville["sol"][sy][sx] == "."
    assert sum(1 for d in ville["decor"] if d["type"].startswith("edicule")) == len(metro.LIGNE["stations"])
