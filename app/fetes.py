"""Le temps des Fêtes (docs/jalons/le-temps-des-fetes.md).

En décembre (l'année du jeu, `calendrier`), la ville s'allume : des guirlandes sur les maisons — les
fenêtres et les vitrines prennent des couleurs la nuit —, un grand sapin sur la place du Faubourg, et des
dindes à livrer en camion.

⚠️ **UNE PURE FONCTION DU JOUR, RIEN DE POSÉ** : les guirlandes sont la COULEUR des lampes qui existent
déjà (à l'empreinte de la lampe), le sapin est PEINT sur une scène de la carte ; rien ne bouche une porte,
rien ne reste en janvier. Le sapin se LIT sur la ville finie : la scène la mieux cotée du Faubourg.
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


def sapin(ville: dict) -> dict | None:
    """La place du sapin : la scène la mieux cotée du Faubourg (puis la plus au nord, la plus à l'ouest)."""
    scenes = [s for s in ville.get("scenes", []) if s.get("district") == "faubourg"]
    if not scenes:
        return None
    s = min(scenes, key=lambda q: (-q.get("valeur", 0), q["y"], q["x"]))
    return {"x": s["x"], "y": s["y"]}


def pour_le_navigateur(ville: dict) -> dict:
    return {"jours": jours(), "guirlandes": {**GUIRLANDES, "couleurs": [list(c) for c in GUIRLANDES["couleurs"]],
                                             "sortes": list(GUIRLANDES["sortes"])},
            "sapin": sapin(ville), "clairon": CLAIRON}
