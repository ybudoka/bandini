"""Le traversier (M12), jugé en Python : ses deux quais, son couloir d'eau, son horaire.

⚠️ `traversier.py` ne pose rien : il cherche. Ces juges ne relisent donc pas sa
recherche — ils vérifient ce qu'elle rend, avec leurs propres yeux : de l'eau sous la
coque, une rue au bout du pont, rien sur le chemin, et la ville inchangée.
"""

from __future__ import annotations

import math

import pytest

from app import carte, ile, traversier, vehicules


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def _zone_proche(ville, district, x, y, marge):
    return any(z["x"] - marge <= x < z["x"] + z["l"] + marge and z["y"] - marge <= y < z["y"] + z["h"] + marge
               for z in ville["zones"] if z.get("district") == district)


def test_deux_escales_les_quais_a_l_ouest_la_pointe_a_l_est(ville):
    t = ville["traversier"]
    assert t, "la baie n'a pas de traversier"
    a, b = t["escales"]
    assert (a["district"], b["district"]) == ("quais", "pointe")
    assert a["nom"] == "Les Quais" and b["nom"] == "La Pointe"
    assert a["x"] + traversier.LONGUEUR < b["x"], "les escales se chevauchent"


def test_a_quai_la_coque_est_dans_l_eau_et_le_pont_touche_une_rue(ville):
    """Sous la coque, de l'eau profonde ; au bout du pont, des tuiles de rive qu'un char
    roule, qui touchent le PONT (jamais la cabine) du côté annoncé, près d'une rue et
    près du quartier."""
    sol, t = ville["sol"], ville["traversier"]
    c = t["coque"]
    for q in t["escales"]:
        for r in range(c["largeur"]):
            for col in range(c["longueur"]):
                assert sol[q["y"] + r][q["x"] + col] == "~", f"{q['nom']} : la coque touche {sol[q['y'] + r][q['x'] + col]!r}"
        assert len(q["acces"]) >= traversier.ACCES_MIN
        for tx, ty in q["acces"]:
            g = sol[ty][tx]
            assert g != "~" and carte.solidite(g) == 0, f"{q['nom']} : un bout de quai en {g!r}"
            if q["cote"] == "nord":
                assert ty == q["y"] - 1 and q["x"] <= tx < q["x"] + c["longueur"]
            else:
                assert tx == (q["x"] - 1 if q["cote"] == "ouest" else q["x"] + c["longueur"])
                assert ty - q["y"] in range(c["largeur"]) and ty - q["y"] != c["cabine"], "on embarquerait par la cabine"
        assert any(carte.routier(sol[ty + dy][tx + dx]) for tx, ty in q["acces"]
                   for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))), f"{q['nom']} : aucune rue au bout du pont"
        assert any(_zone_proche(ville, q["district"], tx, ty, traversier.PRES_DU_QUARTIER) for tx, ty in q["acces"])


def test_le_couloir_est_de_l_eau_libre_loin_de_l_ile_et_des_chaloupes(ville):
    """La coque, glissée d'un quai à l'autre par pas d'un quart de tuile : chaque tuile
    qu'elle recouvre est de l'eau, hors de la ceinture de l'île, et à plus d'une tuile
    de tout amarrage."""
    sol, t = ville["sol"], ville["traversier"]
    c, (a, b) = t["coque"], t["escales"]
    i = ville["ile"]
    m = ile.ILE["ceinture"]
    amarrages = [(q["x"], q["y"]) for q in ville["amarrages"]] + [(q["x"], q["y"]) for q in i.get("amarrages", [])]
    n = 4 * max(abs(b["x"] - a["x"]), abs(b["y"] - a["y"]))
    for k in range(n + 1):
        fx, fy = a["x"] + (b["x"] - a["x"]) * k / n, a["y"] + (b["y"] - a["y"]) * k / n
        x0, y0 = math.floor(fx), math.floor(fy)
        x1, y1 = math.ceil(fx) + c["longueur"] - 1, math.ceil(fy) + c["largeur"] - 1
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                assert sol[y][x] == "~", f"la coque passe sur {sol[y][x]!r} en {(x, y)}"
                assert not (i["x"] - m <= x < i["x"] + i["l"] + m and i["y"] - m <= y < i["y"] + i["h"] + m), \
                    f"la coque frôle l'île en {(x, y)}"
        for ax, ay in amarrages:
            assert not (x0 - 1 <= ax <= x1 + 1 and y0 - 1 <= ay <= y1 + 1), f"la coque frôle l'amarrage {(ax, ay)}"


def test_la_ville_est_la_meme_avec_ou_sans_traversier(ville, monkeypatch):
    monkeypatch.setattr(traversier, "tracer", lambda v: None)
    sans = carte.generer()
    assert set(sans) == set(ville)
    for cle in ville:
        # ⚠️ Le tramway, lui, a son terminus au quai du traversier : sans traversier, il
        # s'arrête à la cantine. Il en dépend — ce qui ne bouge pas, c'est le reste.
        if cle in ("traversier", "tramway"):
            continue
        assert sans[cle] == ville[cle], f"« {cle} » a bougé"


def test_depart_a_l_heure_juste_et_jamais_plus_vite_qu_un_char(ville):
    """Des Quais aux heures paires, de La Pointe aux impaires : une traversée et une
    escale font exactement une heure. Et le traversier file au plus vite au milieu de
    sa traversée — pas plus vite qu'une berline : un bateau qui double les chars se
    lit comme un bogue."""
    h, (a, b) = ville["traversier"]["horaire"], ville["traversier"]["escales"]
    assert h["traversee_h"] + h["quai_h"] == pytest.approx(h["periode_h"] / 2)
    assert h["periode_h"] / 2 == pytest.approx(1.0)
    assert 0 < h["elan"] < 0.5
    tt = ville["tuile_px"]
    distance = math.hypot((b["x"] - a["x"]) * tt, (b["y"] - a["y"]) * tt)
    from app import economie
    images = h["traversee_h"] * economie.JOUR_SECONDES * 60 / 24
    pointe = distance / images / (1 - h["elan"])
    berline = next(v for v in vehicules.CATALOGUE if v["slug"] == "auto")
    assert pointe <= berline["vitesse_max"], f"{pointe:.2f} px/image, une berline fait {berline['vitesse_max']}"
    # Et il ne se traîne pas non plus : on doit le voir avancer.
    assert pointe >= 1.0


def test_le_paquet_porte_le_traversier():
    assert carte.exporter()["traversier"]["escales"]


def test_la_recherche_ne_ralentit_pas_la_ville(ville):
    """⚠️ `carte.generer` tourne des centaines de fois dans la suite. La recherche prend
    ~20 ms ; sans le filtre de la coque dans l'eau, elle prenait trois minutes et demie,
    et aucun autre juge ne le voyait (le couloir rejuge la coque à quai)."""
    import time
    debut = time.perf_counter()
    traversier.tracer(ville)
    assert time.perf_counter() - debut < 0.5
