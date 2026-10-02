"""Le lave-auto qu'on traverse, en vitre (docs/jalons/le-lave-auto-qu-on-traverse.md) : le tunnel, en Python. Il
traverse son bâtiment de la façade à la ruelle, sur la ville finie, sans une tuile ni un dé ; le bureau garde la porte
des piétons et une pièce à sa mesure ; et rien d'autre ne bouge."""

from app import carte, lave_auto
from tests import villes


def _tunnel_et_porte(ville):
    return ville["lave_auto"], next(p for p in ville["portes"] if p.get("lieu") == "lave_auto")


def test_le_tunnel_traverse_son_batiment_de_la_facade_a_la_ruelle():
    ville = villes.exporter()
    t, porte = _tunnel_et_porte(ville)
    sol = ville["sol"]
    assert t and t["l"] == 2 and t["entree"] == porte["y"], t
    cols = range(t["x"], t["x"] + t["l"])
    assert lave_auto.PROFONDEUR_MIN <= t["entree"] - t["sortie"] + 1 <= lave_auto.PROFONDEUR_MAX
    assert all(sol[t["entree"]][x] in "WF" for x in cols) and porte["x"] not in cols, "la façade, jamais la porte des piétons"
    toit = sol[t["sortie"]][t["x"]]
    assert all(sol[y][x] == toit for y in range(t["sortie"], t["entree"]) for x in cols), "le toit d'un seul bâtiment"
    assert carte.LEGENDE[toit].get("solide"), "le toit reste un toit : un mur pour tout autre char"
    # Derrière la sortie : du roulable jusqu'à la ruelle ; devant l'entrée : le trottoir et la chaussée.
    y = t["sortie"] - 1
    while sol[y][t["x"]] != "x":
        assert all(carte.LEGENDE[sol[y][x]].get("solide", 0) == 0 for x in cols), y
        y -= 1
    assert all(sol[y][x] == "x" for x in cols) and t["sortie"] - y <= lave_auto.DERRIERE_MAX
    for k in (1, 2):
        assert all(carte.LEGENDE[sol[t["entree"] + k][x]].get("solide", 0) == 0 for x in cols)
    decors = {(d["x"], d["y"]) for d in ville["decor"]}
    assert not any((x, yy) in decors for x in cols for yy in list(range(y, t["sortie"])) + [t["entree"] + 1, t["entree"] + 2])


def test_le_bureau_garde_la_porte_des_pietons_et_sa_mesure():
    ville = villes.exporter()
    t, porte = _tunnel_et_porte(ville)
    x0, large = porte["vitrine"]
    assert not set(range(t["x"], t["x"] + t["l"])) & set(range(x0, x0 + large)), "la vitrine du bureau ne mord pas sur le tunnel"
    assert x0 <= porte["x"] < x0 + large and large >= lave_auto.BUREAU_MIN
    piece = ville["interieurs"]["lave_auto"]
    assert piece["largeur"] - 2 == large and 1 <= piece["sortie"]["x"] <= large
    assert x0 + piece["sortie"]["x"] - 1 == porte["x"], "la porte de la pièce est en face de celle de la rue"
    assert any(q.get("genre") == "lave_auto" for q in piece["points"]), "le comptoir du lavage"


def test_la_baie_de_chaussee_n_existe_plus():
    t = villes.exporter()["lave_auto"]
    assert set(t) == {"x", "l", "entree", "sortie"}, t


def test_le_tunnel_ne_deplace_rien_d_autre(monkeypatch):
    """Sur la ville finie, sans une tuile ni un dé : sans le tunnel, la ville est la même, hors du lave-auto (son tunnel,
    la vitrine de sa porte, sa pièce)."""
    avec = carte.generer()
    monkeypatch.setattr(lave_auto, "poser", lambda ville: None)
    sans = carte.generer()
    autres = [k for k in set(avec) | set(sans) if k not in ("lave_auto", "interieurs", "portes") and avec.get(k) != sans.get(k)]
    assert not autres, autres
    assert {n for n in avec["interieurs"] if avec["interieurs"][n] != sans["interieurs"].get(n)} == {"lave_auto"}
    assert [(a, b) for a, b in zip(avec["portes"], sans["portes"]) if a != b and a.get("lieu") != "lave_auto"] == []


#: Un bâtiment de huit sur quatre (façade comprise), la porte des piétons au milieu, la dalle puis la ruelle derrière.
PLAN = ["xxxxxxxxxx",
        "..........",
        ".OOOOOOOO.",
        ".OOOOOOOO.",
        ".OOOOOOOO.",
        ".FWWWDWFF.",
        "..........",
        "__________"]
PORTE = {"x": 5, "y": 5, "vitrine": [1, 8]}


def test_un_plan_dessine_a_la_main():
    t = lave_auto.tunnel(PLAN, set(), PORTE)
    assert t == {"x": 1, "l": 2, "entree": 5, "sortie": 2, "vitrine": [3, 6]}, t


def test_pas_de_tunnel_sans_ruelle_ni_avec_quelque_chose_devant():
    sans_ruelle = ["." * 10] + PLAN[1:]
    assert lave_auto.tunnel(sans_ruelle, set(), PORTE) is None
    # Une distributrice devant la colonne de gauche : le tunnel passe à droite, sans rien enlever.
    t = lave_auto.tunnel(PLAN, {(1, 6)}, PORTE)
    assert t and t["x"] == 7 and t["vitrine"] == [1, 6], t
    assert lave_auto.tunnel(PLAN, {(1, 6), (8, 1)}, PORTE) is None
