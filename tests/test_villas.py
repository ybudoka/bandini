"""Des maisons vraiment de luxe (docs/jalons/des-etages-pour-vrai-des-maisons-de-luxe-et-des-terrains-clotures.md,
vague 3) : `app/villas.py`. Une villa est un cossu des Érables qui s'élargit sur sa pelouse libre et ferme sa cour
d'une haie — posée sur la ville finie, sans un dé. La façade (la pierre, le portique, le toit à quatre versants) :
`test_facades_js.py`."""

from collections import deque

import pytest

from app import carte, clotures, villas

#: La table d'ici, pas celle du module : un juge qui relit la table qu'il juge ne rougit jamais.
FACADE = set("FWDdPG")
TOLERES = {"frenesies", "collections"}
JARDIN = {"fontaine_villa", "pilier_portail_o", "pilier_portail_e"}


@pytest.fixture(scope="module")
def deux_villes():
    """La même ville, avec et sans les villas. ⚠️ Les clôtures, posées après, lisent la ville aux villas : on
    les retire des deux."""
    avec_villas = villas.poser
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(clotures, "poser", lambda ville: [])
        posees = []
        mp.setattr(villas, "poser", lambda ville: posees.extend(avec_villas(ville)) or posees)
        avec = carte.generer()
        mp.setattr(villas, "poser", lambda ville: [])
        sans = carte.generer()
    return sans, avec, posees


def test_le_temoin_a_ses_villas(deux_villes):
    """Mesure du 30 sept. 2026 : sept villas. Un juge qui n'en verrait aucune passerait tous les autres."""
    _, avec, posees = deux_villes
    assert len(posees) >= 4, posees
    assert sum(1 for r in avec["residences"] if r.get("villa")) == len(posees)


def test_seule_l_herbe_devient_villa_ou_haie(deux_villes):
    sans, avec, _ = deux_villes
    for cle in avec:
        if cle not in {"sol", "residences", "decor"} | TOLERES:
            assert avec[cle] == sans[cle], f"« {cle} » a changé : les villas déplacent la ville"
    # Le décor : celui d'avant, dans le même ordre, et le jardin des villas AU BOUT (ses numéros à part).
    assert avec["decor"][:len(sans["decor"])] == sans["decor"]
    assert {d["type"] for d in avec["decor"][len(sans["decor"]):]} <= JARDIN
    annexes = clotures.chantiers(avec)[1]
    for y, (a, b) in enumerate(zip(sans["sol"], avec["sol"])):
        for x, (ga, gb) in enumerate(zip(a, b)):
            if ga != gb:
                assert ga == "," and gb in "PF`?", f"la tuile {x, y} : {ga} -> {gb}"
                assert (x, y) not in annexes, f"une villa sur l'annexe d'un chantier en {x, y}"
    assert len(sans["residences"]) == len(avec["residences"])
    for a, b in zip(sans["residences"], avec["residences"]):
        if not b.get("villa"):
            assert a == b


def test_une_villa_est_un_cossu_des_erables_elargi_sous_son_toit(deux_villes):
    sans, avec, _ = deux_villes
    district = clotures._district(avec)
    sol = avec["sol"]
    for a, r in zip(sans["residences"], avec["residences"]):
        if not r.get("villa"):
            continue
        assert r["standing"] == "+" and district(r["x"], r["y"]) == "erables", r
        assert 6 <= r["l"] <= 8 and r["l"] > a["l"], (a, r)
        assert r["x"] <= a["x"] and r["x"] + r["l"] >= a["x"] + a["l"], (a, r)
        # La porte ne bouge pas : la même tuile, le même motif.
        assert r["x"] + r["porte"] == a["x"] + a["porte"] and r["motifs"][r["porte"]] == a["motifs"][a["porte"]]
        assert len(r["motifs"]) == r["l"]
        assert all(sol[r["y"]][x] in FACADE for x in range(r["x"], r["x"] + r["l"])), r
        # Son toit, sur toute sa largeur (deux rangées au moins).
        assert all(sol[r["y"] - k][x] == "P" for k in (1, 2) for x in range(r["x"], r["x"] + r["l"])), r
        # Une colonne de pelouse de marge, de chaque côté où elle s'est élargie : elle ne se colle à rien.
        for x in ([r["x"] - 1] if r["x"] < a["x"] else []) + ([r["x"] + r["l"]] if r["x"] + r["l"] > a["x"] + a["l"] else []):
            for k in (0, 1, 2):
                assert sol[r["y"] - k][x] not in FACADE | {"P"}, f"la villa {r['x'], r['y']} se colle en {x, r['y'] - k}"


def test_la_haie_ne_passe_ni_devant_une_porte_ni_sur_un_chemin(deux_villes):
    sans, avec, _ = deux_villes
    haies = [(x, y) for y, (a, b) in enumerate(zip(sans["sol"], avec["sol"]))
             for x, (ga, gb) in enumerate(zip(a, b)) if gb == "`" and ga != gb]
    assert len(haies) >= 20, "le témoin : une haie par villa, ou presque"
    for x, y in haies:
        assert sans["sol"][y][x] == ",", (x, y)
        assert sans["sol"][y - 1][x] not in "DdG", f"une haie devant une porte en {x, y}"


def _atteintes(sol: list[str]) -> set[tuple[int, int]]:
    """Ce qu'un piéton rejoint depuis le trottoir, sans jamais traverser un solide."""
    h, w = len(sol), len(sol[0])
    vus = {(x, y) for y in range(h) for x in range(w) if carte.LEGENDE.get(sol[y][x], {}).get("trottoir")}
    file = deque(vus)
    while file:
        x, y = file.popleft()
        for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            qx, qy = q
            if 0 <= qy < h and 0 <= qx < len(sol[qy]) and q not in vus and not carte.LEGENDE.get(sol[qy][qx], {}).get("solide"):
                vus.add(q)
                file.append(q)
    return vus


def test_rien_ne_s_enferme_derriere_une_haie(deux_villes):
    """Ce qu'on rejoignait à pied depuis le trottoir, on le rejoint encore — hors de ce que la villa a bâti."""
    sans, avec, _ = deux_villes
    perdues = {(x, y) for x, y in _atteintes(sans["sol"]) - _atteintes(avec["sol"])
               if not carte.LEGENDE.get(avec["sol"][y][x], {}).get("solide")}
    assert not perdues, sorted(perdues)[:10]


def test_le_jardin_de_la_villa(deux_villes):
    """Le jardin (vague 4) : une fontaine par villa, jamais dans la colonne du sentier ; le portail — ses deux
    piliers de part et d'autre du sentier, dans la haie ; la piscine creusée, deux rangées contre la haie, un
    rectangle d'herbe changée en eau. Le témoin : toutes les fontaines, des portails et des piscines."""
    sans, avec, posees = deux_villes
    sol = avec["sol"]
    fontaines = portails = piscines = 0
    for v in posees:
        r = next(q for q in avec["residences"] if q.get("villa") and (q["x"], q["y"]) == (v["x"], v["y"]))
        porte = r["x"] + r["porte"]
        jardin = v.get("jardin") or []
        f = [d for d in jardin if d["type"] == "fontaine_villa"]
        assert len(f) == 1, (v["x"], v["y"], jardin)
        assert abs(f[0]["x"] - porte) >= 2 and r["x"] <= f[0]["x"] < r["x"] + r["l"] and f[0]["y"] > r["y"]
        assert sans["sol"][f[0]["y"]][f[0]["x"]] == ","
        fontaines += 1
        piliers = sorted((d["x"], d["y"], d["type"]) for d in jardin if d["type"].startswith("pilier"))
        if piliers:
            (xo, yo, to), (xe, ye, te) = piliers
            assert (to, te) == ("pilier_portail_o", "pilier_portail_e") and yo == ye
            assert (xo, xe) == (porte - 1, porte + 1) and sol[yo][porte] == ".", piliers
            assert sol[yo][xo - 1] == "`" or sol[yo][xe + 1] == "`", "un portail dans la haie"
            portails += 1
        eau = {(d["x"], d["y"]) for d in jardin if d["type"] == "?"}
        if eau:
            xs, ys = {x for x, _ in eau}, {y for _, y in eau}
            assert len(ys) == 2 and len(eau) == len(xs) * 2 and max(xs) - min(xs) == len(xs) - 1, eau
            assert porte not in xs and all(sol[y][x] == "?" and sans["sol"][y][x] == "," for x, y in eau)
            assert sol[max(ys) + 1][min(xs)] == "`", "la piscine contre la haie"
            piscines += 1
    assert fontaines == len(posees) and portails >= 3 and piscines >= 3, (fontaines, portails, piscines)
