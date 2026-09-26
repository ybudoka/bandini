"""La course de motoneige des bois de La Pointe (docs/jalons/la-motoneige.md).

Le véhicule lui-même est dans `vehicules.CATALOGUE` (`motoneige`, `hors_neige`) ; le défi, dans
`missions.DEFIS` (`motoneige`, l'épreuve `balises` de `Conduite`). Ce module dit OÙ il se court.

⚠️ **LU SUR LA VILLE FINIE, SANS DÉ** : le départ est le bout des chemins des bois (`chemins_des_bois`)
le plus proche du phare ; la piste file jusqu'au bout le plus lointain de CE réseau de sentiers (le plus
long chemin en largeur d'abord, départ fixe) ; les fanions s'égrènent le long, à pas réguliers. Deux
joueurs courent la même course.
"""

from __future__ import annotations

from collections import deque

#: Combien de fanions À L'ALLER (autant au retour, le dernier au départ), et à combien de tuiles on
#: passe un fanion. ⚠️ Un ALLER-RETOUR : le plus long sentier ne fait qu'une soixantaine de tuiles —
#: quatre secondes à pleine vitesse, pas une course.
COURSE = {"balises": 4, "rayon_tuiles": 2}


def course(ville: dict) -> dict | None:
    """`depart` (la tuile où attend la motoneige), `balises` (les tuiles des fanions, dans l'ordre : l'aller
    puis le retour, le dernier au départ), `longueur` (en tuiles, aller et retour) — ou None."""
    tuiles = {tuple(t) for t in ville.get("chemins_des_bois", [])}
    phare = next((p for p in ville["points_interet"] if p.get("slug") == "phare"), None)
    if not tuiles or not phare:
        return None
    depart = min(sorted(tuiles), key=lambda t: abs(t[0] - phare["x"]) + abs(t[1] - phare["y"]))
    parent = {depart: None}
    file = deque([depart])
    dernier = depart
    while file:
        t = file.popleft()
        dernier = t
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (t[0] + dx, t[1] + dy)
            if q in tuiles and q not in parent:
                parent[q] = t
                file.append(q)
    piste = []
    t = dernier
    while t is not None:
        piste.append(t)
        t = parent[t]
    piste.reverse()
    n = COURSE["balises"]
    if len(piste) < n * 3:
        return None
    aller = [list(piste[round((k + 1) * (len(piste) - 1) / n)]) for k in range(n)]
    retour = [list(piste[round((n - 1 - k) * (len(piste) - 1) / n)]) for k in range(n)]
    return {"depart": list(depart), "balises": aller + retour, "longueur": 2 * len(piste)}


def pour_le_navigateur(ville: dict) -> dict:
    return {"course": course(ville), "regles": dict(COURSE)}
