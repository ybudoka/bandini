"""La planque qu'on décore (P4, des choses à collectionner, vague 2) : chaque objet à sa place écrite, sur le bon
genre de tuile, et une planque pleine où l'on circule encore.

⚠️ Les règles sont écrites ICI (le mur au-dessus d'un cadre, la table sous la coupe, une tuile de plancher sous un
meuble debout) : un juge qui relirait `decoration.POSES` pour décider changerait avec la constante qu'il garde.
"""

import json
from collections import deque

import pytest

from app import carte, collectionner, decoration
from app.blocs import rang

PIECES = {"planque": carte.INTERIEURS["planque"], "chalet": rang.PIECE_CHALET,
          "planque_arriere": carte.INTERIEURS["planque_arriere"]}


def _bloque(piece, x, y):
    g = piece["sol"][y][x]
    fiche = carte.LEGENDE.get(g, {})
    return not carte.marchable(g) or bool(fiche.get("meuble"))


@pytest.mark.parametrize("slug", sorted(PIECES))
def test_chaque_objet_est_pose_sur_le_bon_genre_de_tuile(slug):
    piece, places = PIECES[slug], decoration.PLACES[slug]
    tout = {t["slug"] for t in decoration.TROPHEES} | {m["slug"] for m in decoration.MEUBLES}
    # Ce qui ne va que dans certaines planques (`SEULEMENT`, le chalet est plein) : ailleurs, pas de place.
    tout = {s for s in tout if slug in decoration.SEULEMENT.get(s, decoration.PARTOUT)}
    assert set(places) == tout, f"{slug} : il manque une place à {tout - set(places)}, ou il y en a une de trop"
    vus = set()
    # ⚠️ Un objet large (`l`, l'étagère des bebelles : deux tuiles) : CHAQUE tuile qu'il couvre suit la règle.
    for objet, o, x, y in ((s, o, o["x"] + i, o["y"]) for s, o in places.items() for i in range(o.get("l", 1))):
        assert 0 < x < piece["largeur"] - 1 and 0 < y < piece["hauteur"] - 1, (slug, objet)
        assert (x, y) not in vus, f"{slug} : deux objets sur ({x},{y})"
        vus.add((x, y))
        g, pose = piece["sol"][y][x], decoration.POSES[objet]
        if pose == "mur":
            # Sous le mur du haut : le cadre se peint SUR lui.
            assert y == 1 and piece["sol"][0][x] == "B", f"{slug} : {objet} n'a pas de mur au-dessus"
        elif pose == "table":
            assert g == "a", f"{slug} : {objet} n'est pas sur une table (« {g} »)"
        else:
            # Debout ou à plat : sur le plancher, jamais sur un meuble ni devant un point.
            assert not _bloque(piece, x, y), f"{slug} : {objet} sur « {g} »"
            assert all((p["x"], p["y"]) != (x, y) for p in piece["points"]), f"{slug} : {objet} sur un point"
            assert (x, y) != (piece["apparition"]["x"], piece["apparition"]["y"]) or pose == "plat", \
                f"{slug} : {objet} bouche l'entrée"


@pytest.mark.parametrize("slug", sorted(PIECES))
def test_toute_la_planque_pleine_on_rejoint_encore_chaque_point(slug):
    """Tout posé d'un coup — les trois trophées et les six meubles : de la porte, chaque point de la pièce (le
    lit, le coffre, la garde-robe, le catalogue) reste à portée de main, et chaque meuble debout aussi. (Et
    l'étagère des bebelles ferme ses DEUX tuiles.)"""
    piece, places = PIECES[slug], decoration.PLACES[slug]
    fermes = {(o["x"] + i, o["y"]) for s, o in places.items() if s in decoration.SOLIDES for i in range(o.get("l", 1))}
    depart = (piece["apparition"]["x"], piece["apparition"]["y"])
    vus, file = {depart}, deque([depart])
    while file:
        x, y = file.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) in vus or (nx, ny) in fermes or _bloque(piece, nx, ny):
                continue
            vus.add((nx, ny))
            file.append((nx, ny))

    def a_portee(x, y):
        # La règle de `Missions.pointSousLaMain` : à moins d'une tuile et demie, on y touche.
        return any(((vx - x) ** 2 + (vy - y) ** 2) ** 0.5 < 1.6 for vx, vy in vus)

    for p in piece["points"]:
        assert a_portee(p["x"], p["y"]), f"{slug} : le point {p['type']} n'est plus à portée, tout posé"
    # (La pièce d'en arrière n'a pas de juke-box : il est dans les deux planques, `decoration.PARTOUT`.)
    if "jukebox" in places:
        assert a_portee(places["jukebox"]["x"], places["jukebox"]["y"]), f"{slug} : le juke-box hors de portée"


def test_le_catalogue_est_sur_la_table_des_deux_planques():
    for slug, piece in PIECES.items():
        if slug not in decoration.PARTOUT:
            continue                     # la pièce d'en arrière : on y pose ce qu'on achète en ville
        cat = [p for p in piece["points"] if p["type"] == "catalogue"]
        assert len(cat) == 1 and piece["sol"][cat[0]["y"]][cat[0]["x"]] == "a", f"{slug} : pas de catalogue sur la table"


def test_le_catalogue_se_lit_et_se_vend():
    for m in decoration.MEUBLES:
        # `photographe` : le portrait, qui ne se vend qu'au studio (le rayon du photographe, `rayons.RAYONS`).
        # `ville` : ce qui se vend aux comptoirs de la ville (les rayons, vague 4b), pour la pièce d'en arrière.
        assert m["prix"] > 0 and set(m["ou"]) <= {"catalogue", "puces", "photographe", "ville"} and m["ou"], m
        assert len(m["texte"]) <= 44 and m["texte"] == m["texte"].upper(), m["texte"]
    # Les trophées des cartes suivent les paliers de l'album : pas un de plus, pas un de moins. Les bebelles ont
    # UN trophée, dès la première : l'étagère où elles se posent.
    paliers = {int(k) for k in collectionner.REGLE["paliers"]}
    assert {t["palier"] for t in decoration.TROPHEES if t["famille"] == "cartes"} == paliers
    assert [t["palier"] for t in decoration.TROPHEES if t["famille"] == "bebelles"] == [1]


def test_le_catalogue_voyage_avec_les_collections(paquets):
    col = json.loads(paquets.collections.corps)
    assert col["planque"] == json.loads(json.dumps(decoration.exporter()))
    assert "planque" not in json.loads(paquets.definitions.corps)
