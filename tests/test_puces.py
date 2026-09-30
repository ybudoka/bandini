"""Le marché aux puces du dimanche : où il se monte, ce qu'il vend, ce qu'il pèse — et la ville qui ne bouge pas.

⚠️ Les règles sont écrites ICI (un terrain de 8 × 4 d'herbe ou de friche, libre, loin des trouvailles et des pistes
des sauts) : un juge qui relirait `puces.TERRAIN` changerait avec la constante qu'il garde.
"""

import json

import pytest

from app import carte, collectionner, decoration, puces


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def test_le_terrain_est_un_terrain_vague_libre(ville):
    m = ville["collections"]["puces"]
    assert m and (m["l"], m["h"]) == (8, 4)
    decor = {(d["x"], d["y"]) for d in ville["decor"]}
    for j in range(4):
        for i in range(8):
            x, y = m["x"] + i, m["y"] + j
            assert ville["sol"][y][x] in (",", ";"), f"({x},{y}) : « {ville['sol'][y][x]} »"
            assert (x, y) not in decor, f"un décor sur le marché en ({x},{y})"
    for e in m["etals"]:
        assert m["x"] <= e["x"] and e["x"] + 1 < m["x"] + 8 and m["y"] <= e["y"] < m["y"] + 4, e
    # Loin des trouvailles et de la piste de chaque saut.
    col = ville["collections"]
    for q in col["cartes"] + col["bebelles"]:
        assert not (m["x"] - 6 <= q["x"] < m["x"] + 14 and m["y"] - 6 <= q["y"] < m["y"] + 10), q
    for s in col["sauts"]:
        for k in range(-7, 12):
            x, y = s["x"] + s["dx"] * k, s["y"] + s["dy"] * k
            assert not (m["x"] <= x < m["x"] + 8 and m["y"] <= y < m["y"] + 4), f"la piste de {s['slug']} traverse le marché"


def test_le_plus_proche_de_la_planque(ville):
    """Il n'existe pas de terrain libre de 8 × 4 plus près de la planque, à pied : on déplace le marché d'une rangée
    en y posant un décor — il part ailleurs, jamais plus près."""
    m = ville["collections"]["puces"]
    v = json.loads(json.dumps({k: val for k, val in ville.items() if k != "collections"}))
    v["decor"] = v["decor"] + [{"type": "buisson", "x": m["x"] + 3, "y": m["y"] + 1}]
    autre = collectionner.poser(v)["puces"]
    assert autre and (autre["x"], autre["y"]) != (m["x"], m["y"]), "un décor sur le terrain n'a pas déplacé le marché"


def test_rien_d_autre_n_a_bouge(ville):
    v = json.loads(json.dumps({k: val for k, val in ville.items() if k != "collections"}))
    assert collectionner.poser(v) == ville["collections"], "la pose varie"


def test_ce_qu_il_vend(paquets):
    col = json.loads(paquets.collections.corps)
    p = col["puces"]
    assert [e["vend"] for e in p["etals"]] == ["cartes", "meubles"]
    assert all("x" in e and e["marchand"]["dit"] for e in p["etals"])
    r = p["regle"]
    assert r["prix_carte"] > collectionner.REGLE["prime"], "une carte des puces coûte moins que ce qu'elle rapporte"
    assert 0 < r["rabais_meubles"] < 1 and 0 < r["offre"] < 1 and 0 < r["humeur"] < 100
    assert {m["slug"] for m in decoration.MEUBLES if "puces" in m["ou"]} == {"jukebox", "sofa", "televiseur", "tapis_tresse"}
    for e in puces.ETALS:
        assert all(len(q) <= 44 and q == q.upper() for q in e["marchand"]["dit"]), e["marchand"]["dit"]
    assert "puces" not in json.loads(paquets.definitions.corps)


def test_jamais_sur_une_trouvaille():
    """⚠️ Sur la graine livrée, le terrain le plus proche est déjà loin de tout : un pré synthétique de 30 × 12, une carte
    au coin d'où l'on part — le marché se pose à six tuiles d'elle au moins."""
    sol = ["," * 30 for _ in range(12)]
    dist = {(x, y): x + y for y in range(12) for x in range(30)}
    m = puces.poser({"sol": sol}, dist, [(2, 2)])
    assert m and not (m["x"] - 6 <= 2 < m["x"] + 14 and m["y"] - 6 <= 2 < m["y"] + 10), m
