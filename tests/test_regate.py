"""Le tour de l'île (`app/regate.py`, M16 vague 17) : six bouées sur la baie, posées en tout dernier, sans un dé et sans
rien poser — la ville d'avant est la même, clé par clé, et le parcours se court en chaloupe d'un bout à l'autre."""

import json
from unittest import mock

import villes

from app import carte, regate


def _eau(sol, x, y):
    return 0 <= y < len(sol) and 0 <= x < len(sol[0]) and sol[y][x] == "~"


def _eau_autour(sol, x, y, r):
    """⚠️ Le juge lit l'eau lui-même : un juge qui demande au module s'il a raison ne mord pas (muté, il restait vert)."""
    return all(_eau(sol, x + dx, y + dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1))


def test_la_ville_d_avant_est_la_meme_cle_par_cle():
    """⚠️ La ville témoin se génère sous `mock.patch` : jamais par `villes`."""
    avec = json.loads(json.dumps(villes.generer(), sort_keys=True))
    with mock.patch.object(regate, "poser", lambda ville: None):
        sans = json.loads(json.dumps(carte.generer(), sort_keys=True))
    assert sorted(k for k in set(avec) | set(sans) if avec.get(k) != sans.get(k)) == ["regate"]


def test_six_bouees_autour_de_l_ile_sur_de_l_eau_profonde():
    v = villes.generer()
    b = v["regate"]["bouees"]
    ile = v["ile"]
    assert len(b) == len(regate.ANCRES) == 6
    for x, y in b:
        assert _eau_autour(v["sol"], x, y, 2), (x, y)
        dehors = x < ile["x"] or x >= ile["x"] + ile["l"] or y < ile["y"] or y >= ile["y"] + ile["h"]
        assert dehors, f"une bouée sur l'île : {(x, y)}"
        assert all(max(abs(x - a["x"]), abs(y - a["y"])) > regate.LOIN_D_UN_AMARRAGE for a in v["amarrages"])
    # Le sens des aiguilles d'une montre, du sud-est : sud, puis ouest, puis nord.
    cx, cy = ile["x"] + ile["l"] / 2, ile["y"] + ile["h"] / 2
    assert b[0][0] > cx and b[0][1] > cy and b[3][0] < cx and b[3][1] < cy, b


def test_chaque_bord_du_parcours_est_de_l_eau_libre():
    v = villes.generer()
    b = [tuple(p) for p in v["regate"]["bouees"]]
    for a, c in zip(b, b[1:] + b[:1]):
        n = max(abs(c[0] - a[0]), abs(c[1] - a[1]))
        for k in range(n + 1):
            x, y = round(a[0] + (c[0] - a[0]) * k / n), round(a[1] + (c[1] - a[1]) * k / n)
            assert _eau_autour(v["sol"], x, y, 1), (a, c, (x, y))


def test_sans_place_le_parcours_ne_se_pose_pas():
    """Une île entourée de terre (une autre ville) : pas de bouées, et rien ne plante."""
    v = villes.generer()
    v["sol"] = [ligne.replace("~", ".") for ligne in v["sol"]]
    assert regate.bouees(v) is None and regate.poser(v) is None and v["regate"] is None
