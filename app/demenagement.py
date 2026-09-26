"""Le 1er juillet, jour du déménagement (docs/jalons/le-1er-juillet-jour-du-demenagement.md).

Un jour par année du jeu (`calendrier.DATES["demenagement"]`, le 1er juillet), la moitié de la ville
déménage : des camions de déménagement garés à cheval sur le trottoir devant les maisons, des meubles
sur le trottoir d'à côté — le sofa, le matelas, les boîtes, la lampe torchère —, et un boulot de plus au
volant d'un camion (`economie.BOULOTS["demenagement"]`, trois livraisons, sans une bosse).

⚠️ **LU SUR LA VILLE FINIE, SANS DÉ** : les places sont les façades de logement des rues qui ne sont pas
cossues (on déménage au Faubourg, aux Érables, aux Quais), une sur deux au plus, à `ECART` tuiles l'une
de l'autre ; la sorte d'un meuble est l'empreinte de sa tuile. Rien n'est posé dans la ville : le
navigateur fait naître les camions à l'approche, le jour venu, et peint les meubles.

⚠️ **À CHEVAL SUR LE TROTTOIR, PAS EN DOUBLE FILE** : la plupart des maisons donnent sur une rue d'une
voie par sens, et un camion arrêté dans la voie la bouchait pour de bon (le trafic klaxonne, puis force).
Sur le trottoir, à côté de la porte et jamais devant une autre, il ne ferme ni une rue ni un lieu.
"""

from __future__ import annotations

from . import calendrier

JOUR = calendrier.DATES["demenagement"]

#: Les quartiers qui déménagent (le standing `+` n'y est pas : on ne déménage pas une rue chic en camion
#: loué), combien de camions au plus, et à combien de tuiles l'un de l'autre.
QUARTIERS = ("faubourg", "erables", "quais", "shop", "pointe")
CAMIONS_MAX = 18
ECART = 10

#: Les meubles du trottoir, par sorte (le navigateur les peint).
MEUBLES = ("sofa", "matelas", "boites", "lampe", "frigo", "chaise")

CLAIRON = {
    "veille": "DEMAIN, LE 1ER JUILLET : LA MOITIÉ DE LA VILLE DÉMÉNAGE. PRUDENCE SUR LES TROTTOIRS.",
    "jour": "BON DÉMÉNAGEMENT! CAMIONS SUR LES TROTTOIRS, SOFAS SUR LE BORD DU CHEMIN.",
}


def places(ville: dict, legende: dict) -> dict:
    """`camions` : (x, y) de la tuile du milieu, sur le trottoir, le long de la façade ; `meubles` : (x, y,
    sorte), de l'autre côté de la porte. Sans dé."""
    sol = ville["sol"]
    hauteur = len(sol)
    decor = {(d["x"], d["y"]) for d in ville["decor"]}
    portes = {(x, y) for y, rangee in enumerate(sol) for x, g in enumerate(rangee) if g in "Dd"}

    def trottoir(x: int, y: int) -> bool:
        if not (0 <= y < hauteur and 0 <= x < len(sol[y])):
            return False
        fiche = legende.get(sol[y][x], {})
        return bool(fiche.get("trottoir")) and not fiche.get("route") and (x, y) not in decor \
            and (x, y - 1) not in portes

    zones = [z for z in ville["zones"] if z.get("district") in QUARTIERS]

    def quartier(x: int, y: int) -> bool:
        return any(z["x"] <= x < z["x"] + z["l"] and z["y"] <= y < z["y"] + z["h"] for z in zones)

    camions: list[list[int]] = []
    meubles: list[list] = []
    for q in sorted(ville["residences"], key=lambda r: (r["y"], r["x"])):
        if len(camions) >= CAMIONS_MAX or q.get("standing") == "+":
            continue
        porte, y = q["x"] + q["porte"], q["y"] + 1
        if not quartier(porte, y) or any(abs(cx - porte) + abs(cy - y) < ECART for cx, cy in camions):
            continue
        for cote in (1, -1):
            tuiles = [porte + cote * k for k in (1, 2, 3)]
            autre = porte - cote
            if all(trottoir(x, y) for x in tuiles) and trottoir(autre, y):
                camions.append([tuiles[1], y])
                meubles.append([autre, y, MEUBLES[(autre * 31 + y * 17) % len(MEUBLES)]])
                if trottoir(autre - cote, y):
                    meubles.append([autre - cote, y, MEUBLES[((autre - cote) * 31 + y * 17) % len(MEUBLES)]])
                break
    return {"camions": camions, "meubles": meubles}


def pour_le_navigateur(ville: dict, legende: dict) -> dict:
    return {"jour": JOUR, **places(ville, legende), "clairon": dict(CLAIRON)}
