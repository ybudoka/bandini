"""Le derby de démolition à la foire (docs/jalons/le-derby-de-demolition-a-la-foire.md).

Une arène de terre battue à côté de la foire, fermée par des pneus : cinq bazous, et le dernier qui
roule gagne. Les règles du défi sont au catalogue (`missions.DEFIS`, `derby`) ; ce module dit OÙ.

⚠️ **ON NE POSE RIEN DANS LA VILLE.** L'arène se LIT sur la ville finie (`arene`) : un rectangle de
gazon libre à l'est de la palissade de la foire — là où la foire ne s'étend pas, pour laisser l'élan
du pont. Ni tuile, ni décor, ni dé : les pneus se peignent au sol et l'arène ne retient que les
bazous du derby (`Conduite`). La ville ne bouge pas d'une tuile.
"""

from __future__ import annotations

#: La taille de l'arène, en tuiles ; `marge` : les tuiles libres qu'on veut autour (les pneus, et un
#: pas entre elle et la palissade) ; `portee` : jusqu'où on la cherche à l'est de la foire.
ARENE = {"l": 16, "h": 11, "marge": 2, "portee": 30}

#: Les couleurs des bazous — le premier est celui du joueur. Données : `Vehicules.creer` ne tire
#: alors aucun dé.
BAZOUS = ["#c9772b", "#6b8f3a", "#8a3b3b", "#3b5f8a", "#b89a2c"]


def arene(ville: dict) -> dict | None:
    """Le rectangle de l'arène (en tuiles), et la tuile de son panneau — ou None.

    Le premier rectangle de gazon libre (marge comprise) à l'est de la foire, le plus proche du
    milieu de sa hauteur, puis de la palissade. Sans dé : deux joueurs ont la même."""
    f = ville.get("foire")
    if not f:
        return None
    sol, a = ville["sol"], ARENE
    occupe = {(d["x"], d["y"]) for d in ville["decor"]}
    for p in ville.get("ponts", []):
        for y in range(p["y"], p["y"] + p["h"]):
            for x in range(p["x"], p["x"] + p["l"]):
                occupe.add((x, y))
    hauteur, largeur = len(sol), len(sol[0])

    def libre(x: int, y: int) -> bool:
        return 0 <= y < hauteur and 0 <= x < largeur and sol[y][x] == "," and (x, y) not in occupe

    milieu = f["y"] + f["h"] // 2
    candidats = []
    for y in range(f["y"] - a["h"], f["y"] + f["h"]):
        for x in range(f["x"] + f["l"], f["x"] + f["l"] + a["portee"]):
            candidats.append((abs(y + a["h"] // 2 - milieu), x, y))
    m = a["marge"]
    for _, x, y in sorted(candidats):
        if all(libre(tx, ty) for ty in range(y - m, y + a["h"] + m) for tx in range(x - m, x + a["l"] + m)):
            return {"x": x, "y": y, "l": a["l"], "h": a["h"],
                    "panneau": {"x": x + a["l"] // 2, "y": y + a["h"] + 1}}
    return None


def pour_le_navigateur(ville: dict) -> dict:
    return {"arene": arene(ville), "bazous": list(BAZOUS)}
