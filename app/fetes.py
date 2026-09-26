"""Le temps des Fêtes (docs/jalons/le-temps-des-fetes.md).

En décembre (l'année du jeu, `calendrier`), la ville s'allume : des guirlandes sur les maisons — les
fenêtres et les vitrines prennent des couleurs la nuit —, un grand sapin sur la place du Faubourg, et des
dindes à livrer en camion.

⚠️ **UNE PURE FONCTION DU JOUR, RIEN DE POSÉ** : les guirlandes sont la COULEUR des lampes qui existent
déjà (à l'empreinte de la lampe), le sapin est PEINT sur une scène de la carte ; rien ne bouche une porte,
rien ne reste en janvier. Le sapin se LIT sur la ville finie : une place libre à côté de la scène la mieux
cotée du Faubourg.
"""

from __future__ import annotations

from . import calendrier

#: Les couleurs des guirlandes (rouge, vert, or, bleu), et leur force la nuit (l'opacité de la lampe).
GUIRLANDES = {"couleurs": [[224, 69, 58], [63, 174, 90], [255, 210, 63], [58, 123, 213]], "force": 0.42,
              "sortes": ["fenetre", "vitrine"]}

CLAIRON = "LE TEMPS DES FÊTES : LE SAPIN EST ALLUMÉ SUR LA PLACE DU FAUBOURG. ON CHERCHE DES CAMIONNEURS POUR LES DINDES."


def jours() -> list[int]:
    """Les jours de l'année (1 à 40) du temps des Fêtes : décembre."""
    return [j for j in range(1, calendrier.ANNEE + 1) if calendrier.mois(j) == "decembre"]


#: Le gabarit du sapin autour de son tronc (dx, dy) : trois tuiles de large, ses branches montent de deux
#: rangées et son ombre déborde d'une. ⚠️ Rien ne s'y tient — ni décor, ni scène, ni devant de porte :
#: posé tel quel sur la scène de la place, il plantait ses branches dans un banc et dans la fontaine
#: (Martin, 26 sept. 2026, capture).
GABARIT = tuple((dx, dy) for dy in range(-2, 2) for dx in range(-1, 2))
#: Et une tuile d'air autour du gabarit, vide elle aussi et loin de la rue : on en fait le tour à pied.
AIR = 1
#: Jusqu'où, autour de la scène la mieux cotée, on cherche sa place.
PORTEE = 8
#: Pas plus près d'une scène que ça : l'amuseur y joue, sa foule se tient autour.
LOIN_D_UNE_SCENE = 3


def sapin(ville: dict) -> dict | None:
    """La place du sapin : sur la place de la scène la mieux cotée du Faubourg (puis la plus au nord, la plus
    à l'ouest), la tuile libre la plus proche d'elle où tout son gabarit est du même sol, sans rien dessus,
    loin des scènes et de la rue. Sans dé. None si la place n'a pas d'endroit libre."""
    from . import carte, devants

    scenes = [s for s in ville.get("scenes", []) if s.get("district") == "faubourg"]
    if not scenes:
        return None
    s = min(scenes, key=lambda q: (-q.get("valeur", 0), q["y"], q["x"]))
    sol = ville["sol"]
    h, lg = len(sol), len(sol[0])
    sol_de_la_place = sol[s["y"]][s["x"]]
    pris = {(d["x"], d["y"]) for d in ville["decor"]}
    for couche in ("ambulants", "reclames", "paquets", "scenes"):
        pris |= {(o["x"], o["y"]) for o in ville.get(couche, [])}
    pris |= devants.devants(ville)[0]
    toutes = ville.get("scenes", [])

    def libre(x: int, y: int) -> bool:
        if any(max(abs(q["x"] - x), abs(q["y"] - y)) < LOIN_D_UNE_SCENE for q in toutes):
            return False
        for dy in range(-2 - AIR, 2 + AIR):
            for dx in range(-1 - AIR, 2 + AIR):
                tx, ty = x + dx, y + dy
                if not (0 <= tx < lg and 0 <= ty < h) or carte.routier(sol[ty][tx]) or (tx, ty) in pris:
                    return False
                if (dx, dy) in GABARIT and sol[ty][tx] != sol_de_la_place:
                    return False
        return True

    candidates = [(max(abs(x - s["x"]), abs(y - s["y"])), abs(x - s["x"]) + abs(y - s["y"]), y, x)
                  for y in range(s["y"] - PORTEE, s["y"] + PORTEE + 1)
                  for x in range(s["x"] - PORTEE, s["x"] + PORTEE + 1)]
    for *_, y, x in sorted(candidates):
        if libre(x, y):
            return {"x": x, "y": y}
    return None


def pour_le_navigateur(ville: dict) -> dict:
    return {"jours": jours(), "guirlandes": {**GUIRLANDES, "couleurs": [list(c) for c in GUIRLANDES["couleurs"]],
                                             "sortes": list(GUIRLANDES["sortes"])},
            "sapin": sapin(ville), "clairon": CLAIRON}
