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


# --- La course des Friches (vague 2) ---------------------------------------------------------------------

#: La course : à combien de tuiles on passe un fanion, et à quelle allure on la juge faisable (le 4 roues à
#: pleine vitesse, en tuiles par seconde : 4,4 px par image × 60 ÷ 16).
COURSE = {"rayon_tuiles": 2, "allure_tuiles_s": 16.5}


def _croix(ville: dict) -> list[set[tuple[int, int]]]:
    """Les sentiers en croix des Friches : les composantes de tuiles d'allée (`g`) du district, les plus
    grandes d'abord. ⚠️ Pas la cour de Ti-Pout (le lot d'usagés, en allée lui aussi) : une croix a quatre
    bras, donc s'étend loin dans les deux sens — on garde les deux composantes les plus ÉTENDUES."""
    from . import nord
    x0, y0, large, haut = nord._bande().rect_district(nord.district("friches"))
    tuiles = {(x, y) for y in range(y0, min(y0 + haut, nord.DECALAGE_NORD)) for x in range(x0, x0 + large)
              if ville["sol"][y][x] == "g"}
    composantes, vues = [], set()
    for t in sorted(tuiles):
        if t in vues:
            continue
        pile, comp = [t], set()
        while pile:
            c = pile.pop()
            if c in comp:
                continue
            comp.add(c)
            pile += [(c[0] + dx, c[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                     if (c[0] + dx, c[1] + dy) in tuiles]
        vues |= comp
        composantes.append(comp)
    def etendue(c):
        xs, ys = [t[0] for t in c], [t[1] for t in c]
        return min(max(xs) - min(xs), max(ys) - min(ys))
    return sorted(composantes, key=lambda c: (-etendue(c), min(c)))[:2]


def _bouts(croix: set[tuple[int, int]]) -> dict[str, tuple[int, int]]:
    """Les quatre bouts d'une croix : le plus à l'ouest, au nord, à l'est et au sud."""
    return {"ouest": min(croix), "est": max(croix),
            "nord": min(croix, key=lambda t: (t[1], t[0])), "sud": max(croix, key=lambda t: (t[1], t[0]))}


def course(ville: dict) -> dict | None:
    """La course des Friches : `depart` (où attend le 4 roues : le bout sud de la croix du bas, près de la
    ville), `balises` (les fanions, dans l'ordre : les bras de la croix du bas, ceux de celle du haut, et retour
    au départ), `longueur` (en tuiles, à vol d'oiseau d'un fanion au suivant). ⚠️ Lue sur la carte finie, sans
    dé : deux joueurs courent la même course."""
    croix = _croix(ville)
    if len(croix) < 2:
        return None
    haut, bas = sorted(croix, key=lambda c: min(t[1] for t in c))
    b, h = _bouts(bas), _bouts(haut)
    depart = b["sud"]
    balises = [b["ouest"], b["nord"], h["ouest"], h["nord"], h["est"], h["sud"], b["est"], depart]
    trajet = [depart] + balises
    longueur = sum(abs(p[0] - q[0]) + abs(p[1] - q[1]) for p, q in zip(trajet, trajet[1:]))
    return {"depart": list(depart), "balises": [list(t) for t in balises], "longueur": longueur}


def pour_le_navigateur(ville: dict) -> dict:
    return {"course": course(ville), "regles": dict(COURSE)}
