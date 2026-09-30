"""Les bebelles (P4, des choses à collectionner, vague 3) : douze curiosités dans les endroits durs — où elles
dorment, ce qu'elles disent, ce qu'elles pèsent — et la ville qui ne bouge pas d'un octet quand on les pose.

⚠️ Les règles sont écrites ICI en toutes lettres (le sol d'une cachette, le bord, la voie du train, le chemin, les
barrières qu'une mission ouvre) : un juge qui relirait `collectionner.SOLS_BEBELLE` changerait avec la constante qu'il
garde.
"""

import json
from collections import deque

import pytest

from app import blocs, carte, collectionner, decoration

#: Le sol d'une cachette : ruelle, friche, herbe, quai, allée de pierre, sable.
SOLS = {"x", ";", ",", "Q", "g", "s"}


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def _chemins(ville):
    """La distance à pied depuis la planque, les amarrages de l'île et le bout du pont de l'aéroport ; les barrières
    piétonnes fermées, sauf celles qu'une mission ouvre (`condition.apres`)."""
    sol = ville["sol"]
    murs = set()
    for b in ville["barrieres"]:
        if "pieton" in b["arrete"] and not b["existant"] and "apres" not in (b["condition"] or {}):
            for y in range(b["y"], b["y"] + b["h"]):
                for x in range(b["x"], b["x"] + b["l"]):
                    if x in (b["x"], b["x"] + b["l"] - 1) or y in (b["y"], b["y"] + b["h"] - 1):
                        murs.add((x, y))
    planque = next(p for p in ville["points_interet"] if p["slug"] == "planque")
    pont = ville["aeroport"]["pont"]
    departs = [(planque["x"], planque["y"]), (pont["x"] + 1, pont["y"] + pont["nord"] + pont["trou"])]
    departs += [(a["x"], a["y"]) for a in ville["ile"]["amarrages"]]
    dist = {d: 0 for d in departs}
    file = deque(departs)
    while file:
        x, y = file.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= ny < len(sol) and 0 <= nx < len(sol[ny]) and (nx, ny) not in dist and (nx, ny) not in murs \
                    and carte.marchable(sol[ny][nx]):
                dist[(nx, ny)] = dist[(x, y)] + 1
                file.append((nx, ny))
    return dist


def _zone(ville, slug):
    return next(z for z in ville["zones"] if z["slug"] == slug and not z.get("gang"))


def _dans(z, x, y):
    return z["x"] <= x < z["x"] + z["l"] and z["y"] <= y < z["y"] + z["h"]


def test_douze_bebelles_qui_se_lisent_et_se_dessinent():
    bs = collectionner.BEBELLES
    assert len(bs) == 12 and len({b["slug"] for b in bs}) == 12
    for b in bs:
        assert len(b["nom"]) <= 34 and b["nom"] == b["nom"].upper(), b["nom"]
        assert len(b["lignes"]) == 2 and all(len(q) <= 44 and q == q.upper() for q in b["lignes"]), b["lignes"]
        # 6 × 7, et chaque couleur de la grille est dans sa palette.
        assert len(b["grille"]) == 7 and all(len(r) == 6 for r in b["grille"]), b["slug"]
        assert set("".join(b["grille"])) - {"."} <= set(b["palette"]), b["slug"]
        assert all(c.startswith("#") and len(c) == 7 for c in b["palette"].values()), b["slug"]
    # Les endroits durs de la fiche : le bout de l'île, l'aéroport, le fond du rang — et un bloc de plus.
    ou = [b["ou"] for b in bs]
    assert {"zone": "ile"} in ou and {"zone": "aeroport", "enclos": True} in ou and {"bloc": "rang"} in ou and {"bloc": "cineparc"} in ou


def test_chaque_bebelle_de_la_ville_dort_au_bout_de_sa_zone(ville):
    """Dans sa zone, sur un sol de cachette, rejointe à pied — et au BOUT : au moins aux neuf dixièmes du plus long
    chemin qui mène à un sol de cachette de sa zone."""
    dist = _chemins(ville)
    places = {p["slug"]: p for p in ville["collections"]["bebelles"]}
    de_la_ville = [b for b in collectionner.BEBELLES if "zone" in b["ou"]]
    assert set(places) == {b["slug"] for b in de_la_ville}, "une bebelle de la ville n'a pas de place"
    for b in de_la_ville:
        p, z = places[b["slug"]], _zone(ville, b["ou"]["zone"])
        x, y = p["x"], p["y"]
        assert _dans(z, x, y), f"{b['slug']} hors de {z['slug']}"
        assert ville["sol"][y][x] in SOLS, f"{b['slug']} sur « {ville['sol'][y][x]} »"
        assert (x, y) in dist, f"{b['slug']} ({x},{y}) ne se rejoint pas"
        plus_long = max(d for (tx, ty), d in dist.items() if _dans(z, tx, ty) and ville["sol"][ty][tx] in SOLS)
        assert dist[(x, y)] >= 0.9 * plus_long, f"{b['slug']} : {dist[(x, y)]} pas, le bout est à {plus_long}"
        assert p["indice"] == z["nom"].replace("'", "’").upper()


def test_le_cendrier_est_dans_la_cloture_de_l_aeroport(ville):
    """Pas dans l'herbe autour : DEDANS, là où la guérite (le laissez-passer, a02) fait entrer."""
    p = next(q for q in ville["collections"]["bebelles"] if q["slug"] == "cendrier_expo")
    z = _zone(ville, "aeroport")
    x_ = [(x, y) for y in range(z["y"], z["y"] + z["h"]) for x in range(z["x"], z["x"] + z["l"]) if ville["sol"][y][x] == "X"]
    assert min(x for x, _ in x_) < p["x"] < max(x for x, _ in x_) and min(y for _, y in x_) < p["y"] < max(y for _, y in x_), p


def test_jamais_sous_la_mini_carte_ni_sur_la_voie_du_train(ville):
    """Vu à la capture : le bonhomme au coin des Friches, sous la mini-carte, puis entre les rails du train."""
    rang = ville["train"]["rang"]
    L, H = ville["largeur"], ville["hauteur"]
    for p in ville["collections"]["bebelles"]:
        x, y = p["x"], p["y"]
        assert not (x < 9 and y < 9), f"{p['slug']} dans le coin de la mini-carte"
        assert 2 <= x < L - 2 and 3 <= y < H - 2, f"{p['slug']} collée au bord"
        assert abs(y - rang) > 3, f"{p['slug']} sur la voie du train"


def test_loin_des_autres_trouvailles(ville):
    col = ville["collections"]
    autres = [(q["x"], q["y"]) for q in ville["paquets"] + ville["frenesies"] + col["cartes"]]
    bs = col["bebelles"]
    for i, p in enumerate(bs):
        for x, y in autres + [(q["x"], q["y"]) for q in bs[i + 1:]]:
            assert max(abs(p["x"] - x), abs(p["y"] - y)) >= 6, f"{p['slug']} collée à ({x},{y})"


def test_celles_des_blocs_se_rejoignent_sans_traverser_un_arbre():
    for p in collectionner.places_des_blocs():
        bloc = blocs.par_slug(p["bloc"])
        arbres = {(d["x"], d["y"]) for d in blocs.decor_du_bloc(bloc)}
        sol = blocs.sol_du_bloc(bloc)
        depart = (bloc["arrivee"]["x"], bloc["arrivee"]["y"])
        vus, file = {depart}, deque([depart])
        while file:
            x, y = file.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= ny < len(sol) and 0 <= nx < len(sol[ny]) and (nx, ny) not in vus and (nx, ny) not in arbres \
                        and carte.marchable(sol[ny][nx]):
                    vus.add((nx, ny))
                    file.append((nx, ny))
        assert (p["x"], p["y"]) in vus and (p["x"], p["y"]) not in arbres, p
        assert sol[p["y"]][p["x"]] in SOLS and not (p["x"] < 9 and p["y"] < 9), p
        assert p["indice"] == bloc["nom"].upper()
    assert {p["bloc"] for p in collectionner.places_des_blocs()} == {"rang", "cineparc"}


def test_les_cartes_n_ont_pas_bouge_d_une_tuile(ville):
    """Les bebelles se posent APRÈS les cartes : les cartes sont celles de la vague 1, à la tuile près."""
    v = json.loads(json.dumps({k: val for k, val in ville.items() if k != "collections"}))
    sans = collectionner.poser(v)
    assert sans["cartes"] == ville["collections"]["cartes"]
    assert collectionner.poser(v)["bebelles"] == ville["collections"]["bebelles"], "la pose des bebelles varie"


def test_elles_voyagent_avec_les_collections(paquets):
    col = json.loads(paquets.collections.corps)
    liste = col["bebelles"]["liste"]
    assert [b["slug"] for b in liste] == [b["slug"] for b in collectionner.BEBELLES], "l'ordre de l'étagère a changé"
    assert all("x" in b for b in liste), "une bebelle voyage sans sa place"
    assert {b["bloc"] for b in liste if "bloc" in b} == {"rang", "cineparc"}
    assert col["bebelles"]["regle"]["paliers"] == {"6": 500, "12": 2500}
    defs = json.loads(paquets.definitions.corps)
    assert "bebelles" not in defs and "bebelles" not in json.loads(paquets.carte.corps)


def test_l_etagere_a_sa_place_dans_les_deux_planques():
    for piece in ("planque", "chalet"):
        o = decoration.PLACES[piece]["etagere_bebelles"]
        assert o.get("l") == 2 and decoration.POSES["etagere_bebelles"] == "sol"


def test_la_regle_fuit_le_coin_de_la_mini_carte():
    """⚠️ Sur la graine livrée, la voie du train couvre déjà le coin des Friches : un pré de 20 × 20 où le bout du
    chemin EST le coin nord-ouest sépare les deux règles."""
    sol = ["," * 20 for _ in range(20)]
    dist = collectionner._depuis({"sol": sol}, [(19, 19)])
    x, y = collectionner._au_bout(sol, None, dist, [], 0)
    assert not (x < 9 and y < 9), (x, y)
    assert x >= 2 and y >= 3, (x, y)


def test_un_rideau_d_arbres_ne_se_traverse_pas(monkeypatch):
    """Un bloc de 30 × 12 coupé par une rangée d'arbres (des décors) : la bebelle reste du côté de l'arrivée."""
    plan = [",,,,,,,,,,,,,,,T,,,,,,,,,,,,,," for _ in range(12)]
    faux = {"slug": "rang", "nom": "Le faux rang", "plan": plan, "decors": {"T": [",", "sapin"]},
            "arrivee": {"x": 28, "y": 6}}
    monkeypatch.setattr(blocs, "par_slug", lambda s: faux if s == "rang" else None)
    places = collectionner.places_des_blocs()
    assert len(places) == 1 and places[0]["x"] > 15, places
