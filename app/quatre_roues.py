"""Les 4 roues garés (docs/jalons/les-4-roues.md, vague 1) : leurs places dans les Friches.

Martin (28 sept. 2026) : on les trouve « dans les Friches » (et au chalet du rang : sa place est dans le bloc,
`blocs/rang.py`). Posés À CÔTÉ DES CABANONS, sur la terre, comme on range un 4 roues près de son abri.

⚠️ **SUR LA CARTE FINIE, SANS UN DÉ** : lu après la bande (`nord.poser`), rien n'est tiré et rien n'est ajouté à
une liste que la ville lit — c'est une clé à part, `quatre_roues`, que le navigateur lit pour les faire naître
à l'approche (`QuatreRoues.maj`). La ville d'avant et la bande restent les mêmes à la tuile près.
"""

from __future__ import annotations

#: Combien de 4 roues attendent dans les Friches.
COMBIEN = 3

#: Où chercher, autour d'un cabanon, la tuile libre où le garer : à l'est, puis à l'ouest, puis au sud.
AUTOUR = ((1, 0), (-1, 0), (0, 1), (2, 0), (-2, 0))


def poser(ville: dict) -> list[dict]:
    """Les places des 4 roues des Friches : `[{"x", "y"}]`, en tuiles, triées. Une par cabanon, les
    cabanons pris d'un bout à l'autre des Friches (le premier, celui du milieu, le dernier)."""
    from . import nord

    x0, y0, large, haut = nord._bande().rect_district(nord.district("friches"))
    dans = lambda x, y: x0 <= x < x0 + large and y0 <= y < min(y0 + haut, nord.DECALAGE_NORD)  # noqa: E731
    cabanons = sorted((d["x"], d["y"]) for d in ville["decor"] if d["type"] == "cabanon" and dans(d["x"], d["y"]))
    if not cabanons:
        return []
    choisis = [cabanons[round(k * (len(cabanons) - 1) / max(1, COMBIEN - 1))] for k in range(COMBIEN)]
    pris = {(d["x"], d["y"]) for d in ville["decor"]}
    legende = __import__("app.carte", fromlist=["LEGENDE"]).LEGENDE
    places = []
    for cx, cy in dict.fromkeys(choisis):
        for dx, dy in AUTOUR:
            x, y = cx + dx, cy + dy
            fiche = legende.get(ville["sol"][y][x], {})
            if dans(x, y) and (x, y) not in pris and fiche.get("terre") and not fiche.get("solide"):
                places.append({"x": x, "y": y})
                pris.add((x, y))
                break
    return places
