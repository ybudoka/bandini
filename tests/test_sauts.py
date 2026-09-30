"""Les sauts de Rocco (P4, des choses à collectionner, vague 4) : vingt sauts, les huit rampes de la ville et douze
tremplins neufs — où ils se posent, et ce qu'il faut autour pour qu'ils servent.

⚠️ Les règles sont écrites ICI (l'élan de sept tuiles, la réception de dix, le sol rapide, la voie du train, l'écart) :
un juge qui relirait `carte.ELAN_RAMPE` changerait avec la constante qu'il garde.
"""

import json

import pytest

from app import carte, collectionner, pliage

ELAN, RECEPTION = 7, 10
QUOTAS = {"faubourg": 3, "erables": 3, "shop": 3, "quais": 3, "pointe": 3, "friches": 2, "canton": 1, "gare": 2}


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def _zone(ville, slug):
    return next(z for z in ville["zones"] if z["slug"] == slug and not z.get("gang"))


def _dans(z, x, y):
    return z["x"] <= x < z["x"] + z["l"] and z["y"] <= y < z["y"] + z["h"]


def test_vingt_sauts_leur_compte_par_district(ville):
    sauts = ville["collections"]["sauts"]
    assert len(sauts) == 20 and len({s["slug"] for s in sauts}) == 20
    assert {d: sum(1 for s in sauts if s["district"] == d) for d in QUOTAS} == QUOTAS
    assert all(len(s["nom"]) <= 34 and s["nom"] == s["nom"].upper() for s in sauts)
    # ⚠️ Le SLUG est le nom : le district et son rang, pas une position.
    assert [s["slug"] for s in sauts if s["district"] == "faubourg"] == ["faubourg_1", "faubourg_2", "faubourg_3"]


def test_les_rampes_de_la_ville_en_sont(ville):
    rampes = {(r["x"], r["y"]) for r in ville["rampes"]}
    miennes = {(s["x"], s["y"]) for s in ville["collections"]["sauts"] if s["rampe"]}
    assert miennes == rampes, "une rampe de la ville n'est pas un saut (ou un saut prétend être une rampe)"
    for s in ville["collections"]["sauts"]:
        assert _dans(_zone(ville, s["district"]), s["x"], s["y"]), s


def test_chaque_tremplin_a_son_elan_et_sa_reception(ville):
    sol, voie = ville["sol"], ville["voie"]
    rang = ville["train"]["rang"]
    decor = {(d["x"], d["y"]) for d in ville["decor"]}
    ponts = {(p["x"] + i, p["y"] + k) for p in ville["ponts"] for i in range(p["l"]) for k in range(p["h"])}

    def libre(x, y):
        return carte.solidite(sol[y][x]) == 0 and (x, y) not in decor

    def rapide(x, y, quatre_roues):
        f = carte.LEGENDE[sol[y][x]]
        if quatre_roues:
            return libre(x, y)
        # L'asphalte, le stationnement, le quai, l'abord — ou la ruelle ; jamais la terre, où une auto plafonne sous
        # la vitesse qu'il faut pour décoller.
        # Ni l'abord (la bande de brique le long du trottoir) ni les planches d'un pont : un couloir, pas un élan.
        return libre(x, y) and not f.get("terre") and not f.get("abord") and (x, y) not in ponts \
            and bool(f.get("route") or f.get("ruelle") or sol[y][x] == "Q")

    neufs = [s for s in ville["collections"]["sauts"] if not s["rampe"]]
    assert len(neufs) == 12
    for s in neufs:
        x, y, dx, dy, q = s["x"], s["y"], s["dx"], s["dy"], bool(s.get("quatre_roues"))
        for k in range(-ELAN, 2):
            assert rapide(x + dx * k, y + dy * k, q), f"{s['slug']} : l'élan bute en {k}"
        for k in range(2, RECEPTION + 2):
            assert libre(x + dx * k, y + dy * k), f"{s['slug']} : la réception bute en {k}"
        for k in (0, 1):
            tx, ty = x + dx * k, y + dy * k
            assert voie[ty][tx] == "." and not carte.LEGENDE[sol[ty][tx]].get("trottoir"), f"{s['slug']} sur une voie"
        for k in range(-ELAN, RECEPTION + 2):
            assert abs(y + dy * k - rang) > 3, f"{s['slug']} sur la voie du train"
            for c in (-1, 1):
                assert libre(x + dx * k + dy * c, y + dy * k + dx * c), f"{s['slug']} : un décor ou un mur au bord de la piste"
        assert not (x < 9 and y < 9), s
        if q:
            assert ville["quatre_roues"], "un saut en 4 roues dans une ville sans 4 roues"


def test_deux_tremplins_jamais_voisins(ville):
    tous = ville["collections"]["sauts"]
    for s in tous:
        if s["rampe"]:
            continue
        for t in tous:
            if t is not s:
                assert max(abs(s["x"] - t["x"]), abs(s["y"] - t["y"])) >= 20, (s["slug"], t["slug"])


def test_ni_les_cartes_ni_les_bebelles_n_ont_bouge(ville):
    v = json.loads(json.dumps({k: val for k, val in ville.items() if k != "collections"}))
    a, b = collectionner.poser(v), collectionner.poser(v)
    assert a == b == ville["collections"], "la pose des sauts varie"
    assert a["cartes"] == ville["collections"]["cartes"] and a["bebelles"] == ville["collections"]["bebelles"]


def test_ils_voyagent_avec_les_collections(paquets):
    col = json.loads(paquets.collections.corps)
    assert len(col["sauts"]["liste"]) == 20 and col["sauts"]["regle"]["vol_min_px"] == 40
    assert "sauts" not in json.loads(paquets.definitions.corps)
    ville = pliage.deplier(json.loads(paquets.carte.corps))   # la carte voyage pliée
    tremplins = {(s["x"], s["y"]) for s in col["sauts"]["liste"] if not s["rampe"]}
    assert not tremplins & {(r["x"], r["y"]) for r in ville["rampes"]}, "un tremplin neuf est dans la carte"
    assert all(ville["sol"][y][x] not in "RJ" for x, y in tremplins), "un tremplin neuf a changé la carte"


def test_un_tremplin_ne_se_pose_pas_pres_d_une_rampe():
    """⚠️ Sur la graine livrée, « le plus loin possible » écarte déjà les tremplins : un terrain de 36 × 20 tout
    d'asphalte, une rampe au milieu — tout y est à moins de vingt tuiles d'elle, la Gare n'aura que sa rampe."""
    sol = ["#" * 36 for _ in range(20)]
    v = {"sol": sol, "voie": ["." * 36 for _ in range(20)], "decor": [], "lampes": [], "chantiers": [], "portes": [],
         "zones": [{"slug": "gare", "nom": "La Gare", "x": 0, "y": 0, "l": 36, "h": 20}],
         "rampes": [{"x": 18, "y": 10, "dx": 1, "dy": 0}]}
    sauts = collectionner.poser_sauts(v, [])
    assert [(s["x"], s["y"]) for s in sauts] == [(18, 10)], sauts
