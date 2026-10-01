"""Le tour de l'île : six bouées de course sur la baie (M16, vague 17, 1er oct. 2026 — la mission i07).

Martin : « une course sur l'eau ». Une `course` de mission passait par des LIEUX ; sur l'eau, il n'y en a pas — deux
amarrages autour de l'île, et rien entre eux. Ce module pose un PARCOURS : six bouées autour de l'Île-aux-Corneilles,
dans l'ordre des aiguilles d'une montre, en partant du sud-est (le hangar de Léo, son bateau, la ligne d'arrivée).

⚠️ **SUR LA VILLE FINIE, EN TOUT DERNIER, SANS UN DÉ, ET RIEN DE POSÉ** : une bouée n'est ni une tuile ni un décor —
un décor de plus au chargement décale l'identifiant de tout ce qui naît après (`decor-eager-decale-les-identifiants`).
C'est une liste de points (`ville["regate"]`) que le navigateur PEINT (`static/js/regate.js`) et que `course` lit
(`bouee:<n>`). La ville d'avant est la même, clé par clé.

Le choix est une MESURE : pour chaque coin et le milieu des côtés nord et sud, à `ECART` tuiles de la rive de l'île, la
première tuile en spirale (dans un ordre fixe) qui est de l'eau PROFONDE — de l'eau à `DEGAGEMENT` tuiles tout autour —,
loin des amarrages ; et chaque bord du parcours, d'une bouée à la suivante, est de l'eau libre sur toute sa longueur.
"""

from __future__ import annotations

#: À combien de tuiles de la rive de l'île (son rectangle) on pose les ancres : la ceinture d'eau (4) et trois de plus.
ECART = 7
#: De l'eau tout autour de la bouée, sur tant de tuiles : une chaloupe y tourne sans racler un fond.
DEGAGEMENT = 2
#: Jusqu'où chercher autour d'une ancre, en tuiles.
PORTEE = 8
#: Loin des amarrages (une chaloupe de décor y dort), en tuiles.
LOIN_D_UN_AMARRAGE = 4
#: Combien de bouées, et dans quel ordre : (fraction de la largeur, fraction de la hauteur, côté) — les aiguilles d'une
#: montre en partant du sud-est.
ANCRES: tuple[tuple[float, float], ...] = (
    (1.0, 1.0),     # le sud-est : sous le hangar de Léo
    (0.5, 1.0),     # le milieu du sud
    (0.0, 1.0),     # le sud-ouest : la vieille jetée, l'usine
    (0.0, 0.0),     # le nord-ouest : le quai et sa jetée
    (0.5, 0.0),     # le milieu du nord : la chapelle
    (1.0, 0.0),     # le nord-est
)


def _eau(sol: list[str], x: int, y: int) -> bool:
    return 0 <= y < len(sol) and 0 <= x < len(sol[0]) and sol[y][x] == "~"


def _profonde(sol: list[str], x: int, y: int) -> bool:
    return all(_eau(sol, x + dx, y + dy) for dy in range(-DEGAGEMENT, DEGAGEMENT + 1)
               for dx in range(-DEGAGEMENT, DEGAGEMENT + 1))


def _bord_libre(sol: list[str], a: tuple[int, int], b: tuple[int, int]) -> bool:
    """Le segment de `a` à `b` ne touche que de l'eau, à une tuile près de chaque côté."""
    n = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
    for k in range(n + 1):
        x = round(a[0] + (b[0] - a[0]) * k / n)
        y = round(a[1] + (b[1] - a[1]) * k / n)
        if not all(_eau(sol, x + dx, y + dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
            return False
    return True


def _spirale(cx: int, cy: int):
    """Les tuiles autour de (cx, cy), de la plus proche à la plus lointaine, dans l'ordre de lecture."""
    for r in range(PORTEE + 1):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if max(abs(dx), abs(dy)) == r:
                    yield cx + dx, cy + dy


def bouees(ville: dict) -> list[tuple[int, int]] | None:
    """Les six bouées, ou None si l'île n'en a pas la place (une autre graine : rien ne plante)."""
    ile = ville.get("ile")
    if not isinstance(ile, dict):
        return None
    sol = ville["sol"]
    amarrages = [(a["x"], a["y"]) for a in ville.get("amarrages") or []]
    x0, y0, x1, y1 = ile["x"] - ECART, ile["y"] - ECART, ile["x"] + ile["l"] - 1 + ECART, ile["y"] + ile["h"] - 1 + ECART
    poses: list[tuple[int, int]] = []
    for fx, fy in ANCRES:
        cx, cy = round(x0 + (x1 - x0) * fx), round(y0 + (y1 - y0) * fy)
        place = next(((x, y) for x, y in _spirale(cx, cy) if _profonde(sol, x, y)
                      and all(max(abs(x - ax), abs(y - ay)) > LOIN_D_UN_AMARRAGE for ax, ay in amarrages)), None)
        if place is None:
            return None
        poses.append(place)
    for a, b in zip(poses, poses[1:] + poses[:1]):
        if not _bord_libre(sol, a, b):
            return None
    return poses


def poser(ville: dict) -> dict | None:
    """`ville["regate"]` : les bouées, dans l'ordre du tour. Rien d'autre ne change."""
    b = bouees(ville)
    ville["regate"] = {"bouees": [list(p) for p in b]} if b else None
    return ville["regate"]
