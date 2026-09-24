"""Deux bateaux de plus : le chalutier et le porte-conteneurs (demande de Martin,
21 sept. 2026 : « nouveau bateau : chalutier + porte-conteneurs »).

⚠️ Ce que ces juges tiennent : deux fiches de plus qui obéissent à la règle de la
chaloupe (l'eau, hors du trafic), des mouillages à QUAI d'où l'on repart en avant, et
une ville qui ne bouge pas d'une tuile pour les accueillir.
"""

import math

import pytest

from app import carte, navires, traversier, vehicules


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def _rect(m: dict) -> tuple[int, int, int, int]:
    """Le rectangle de tuiles d'un mouillage, relu de son centre et de son cap."""
    longueur, largeur = navires.dimensions(m["slug"])
    couche = abs(math.sin(m["angle"])) < 0.5
    lx, ly = (longueur, largeur) if couche else (largeur, longueur)
    x0, y0 = m["x"] / carte.TUILE_PX - lx / 2, m["y"] / carte.TUILE_PX - ly / 2
    assert x0 == int(x0) and y0 == int(y0), f"{m['slug']} n'est pas posé sur la trame : {m}"
    return int(x0), int(y0), int(x0) + lx, int(y0) + ly


def test_deux_bateaux_de_plus_et_ce_sont_des_bateaux():
    """La règle de la chaloupe, et rien d'autre : l'eau, hors du trafic. Et chacun a
    son caractère — plus il est long, plus il est lent, lourd et dur à abîmer."""
    chaloupe, chalutier, cargo = (vehicules.par_slug(s) for s in ("bateau", "chalutier", "porte_conteneurs"))
    for v in (chalutier, cargo):
        assert v["classe"] == "bateau" and v["eau"] is True, v["slug"]
        assert v["frequence"] == 0, f"{v['slug']} est entré dans le trafic de rue"
        assert v["klaxon"] == "corne", f"{v['slug']} n'a pas la corne"
    assert chaloupe["longueur"] < chalutier["longueur"] < cargo["longueur"]
    assert chaloupe["vitesse_max"] > chalutier["vitesse_max"] > cargo["vitesse_max"]
    assert chaloupe["acceleration"] > chalutier["acceleration"] > cargo["acceleration"]
    assert chaloupe["masse"] < chalutier["masse"] < cargo["masse"]
    assert chaloupe["vie"] < chalutier["vie"] < cargo["vie"]
    # ⚠️ Plus long que le traversier : c'est un porte-conteneurs.
    assert cargo["longueur"] > traversier.LONGUEUR * carte.TUILE_PX


def test_la_ville_a_son_cargo_et_ses_chalutiers(ville):
    """Un porte-conteneurs, deux chalutiers — et le cargo mouille au quai du cargo :
    le quai avait sa chaîne et sa cale, il lui manquait le bateau."""
    mouillages = ville["mouillages"]
    assert [m["slug"] for m in mouillages] == ["porte_conteneurs", "chalutier", "chalutier"], mouillages
    cargo = next(b for b in ville["barrieres"] if b["slug"] == "cargo")
    x0, y0, x1, y1 = _rect(mouillages[0])
    ecart = max(cargo["x"] - x1, x0 - (cargo["x"] + cargo["l"]), 0) + max(cargo["y"] - y1, y0 - (cargo["y"] + cargo["h"]), 0)
    assert ecart <= 6, f"le porte-conteneurs mouille à {ecart} tuiles de la chaîne du cargo"


def test_chaque_coque_est_a_quai_sur_l_eau_et_repart_en_avant(ville):
    """⚠️ **Le juge qui compte.** Tout le rectangle est de l'eau de la baie ; un long
    flanc touche le QUAI sur la moitié au moins de sa longueur ; et devant l'étrave,
    une longueur de coque d'eau libre — le premier porte-conteneurs s'était couché
    dans un bassin, le nez à quatre tuiles d'une jetée, et il ne sortait plus."""
    sol = ville["sol"]
    for m in ville["mouillages"]:
        x0, y0, x1, y1 = _rect(m)
        for y in range(y0, y1):
            for x in range(x0, x1):
                assert sol[y][x] == "~", f"{m['slug']} : ({x}, {y}) n'est pas de l'eau"
        couche = x1 - x0 > y1 - y0
        flancs = ([[(x, y0 - 1) for x in range(x0, x1)], [(x, y1) for x in range(x0, x1)]] if couche
                  else [[(x0 - 1, y) for y in range(y0, y1)], [(x1, y) for y in range(y0, y1)]])
        assert any(2 * sum(sol[y][x] == "Q" for x, y in f) >= len(f) for f in flancs), f"{m['slug']} n'est pas à quai : {m}"
        longueur = navires.dimensions(m["slug"])[0]
        dx, dy = round(math.cos(m["angle"])), round(math.sin(m["angle"]))
        devant = navires.chenal({"x0": x0, "y0": y0, "l": x1 - x0, "h": y1 - y0}, (dx, dy), longueur)
        for y in range(devant[1], devant[3]):
            for x in range(devant[0], devant[2]):
                assert sol[y][x] == "~", f"{m['slug']} : son chenal bute en ({x}, {y}) — il ne repart pas en avant"


def test_ni_sur_une_chaloupe_ni_sur_un_autre_ni_dans_un_chenal(ville):
    """Deux grands bateaux ne se touchent pas, aucun ne mouille dans le chenal d'un
    autre, et une chaloupe amarrée n'a pas une coque de dix tuiles sur le dos."""
    rects = [(m, _rect(m)) for m in ville["mouillages"]]
    amarrages = ville["amarrages"] + ville["ile"]["amarrages"]
    for m, (x0, y0, x1, y1) in rects:
        for a in amarrages:
            loin = (a["x"] < x0 - navires.MARGE_AMARRAGE or a["x"] >= x1 + navires.MARGE_AMARRAGE
                    or a["y"] < y0 - navires.MARGE_AMARRAGE or a["y"] >= y1 + navires.MARGE_AMARRAGE)
            assert loin, f"{m['slug']} mouille sur la chaloupe de ({a['x']}, {a['y']})"
    for i, (m, a) in enumerate(rects):
        for n, b in rects[i + 1:]:
            e = navires.ECART
            separes = a[2] + e <= b[0] or b[2] + e <= a[0] or a[3] + e <= b[1] or b[3] + e <= a[1]
            assert separes, f"{m['slug']} et {n['slug']} se touchent"
        dx, dy = round(math.cos(m["angle"])), round(math.sin(m["angle"]))
        p = {"x0": a[0], "y0": a[1], "l": a[2] - a[0], "h": a[3] - a[1]}
        c = navires.chenal(p, (dx, dy), navires.dimensions(m["slug"])[0])
        for n, b in rects:
            if n is m:
                continue
            assert c[2] <= b[0] or b[2] <= c[0] or c[3] <= b[1] or b[3] <= c[1], f"{n['slug']} bouche le chenal de {m['slug']}"


def test_loin_de_la_route_du_traversier(ville):
    """Un traversier qui frôle une coque la coule (`traversier.MARGE_AMARRAGE`) :
    aucun mouillage dans le rectangle de ses deux escales."""
    t = ville["traversier"]
    xa = min(e["x"] for e in t["escales"]) - navires.MARGE_TRAVERSIER
    ya = min(e["y"] for e in t["escales"]) - navires.MARGE_TRAVERSIER
    xb = max(e["x"] for e in t["escales"]) + t["coque"]["longueur"] + navires.MARGE_TRAVERSIER
    yb = max(e["y"] for e in t["escales"]) + t["coque"]["largeur"] + navires.MARGE_TRAVERSIER
    for m in ville["mouillages"]:
        x0, y0, x1, y1 = _rect(m)
        assert x1 <= xa or xb <= x0 or y1 <= ya or yb <= y0, f"{m['slug']} mouille sur la route du traversier"


def test_la_ville_est_la_meme_sans_les_grands_bateaux(monkeypatch, ville):
    """⚠️ Ce qu'on AJOUTE se pose en dernier : les mouillages ne posent rien, ne
    tirent aucun dé, et rien de ce qui précède ne les lit. La ville sans eux est la
    même, clé par clé."""
    monkeypatch.setattr(navires, "amarrer", lambda chantier, v: [])
    sans = carte.generer()
    assert set(sans) == set(ville)
    differentes = [k for k in ville if k != "mouillages" and ville[k] != sans[k]]
    assert differentes == [], f"les grands bateaux ont déplacé : {differentes}"
