"""La Saint-Jean sur la baie (docs/jalons/la-saint-jean-sur-la-baie.md).

Le soir du 24 juin (`calendrier.DATES["saint_jean"]`), un défilé de chars allégoriques remonte une rue du
Faubourg, fermée le temps qu'il passe ; puis des feux d'artifice partent du phare de La Pointe, vus de
partout.

⚠️ **LA RUE DU DÉFILÉ EST UNE RUE QU'ON SAIT DÉJÀ FERMER** : la plus longue des `fermetures` du Faubourg
(celles que `carte.py` a jugées sans couper la ville — le juge de connexité — et que `devants.py` n'a pas
écartées devant une porte). Le soir de la fête, elle PREND LA PLACE de l'entrave du jour
(`Monde.entraveDuJour`) : toujours une seule rue fermée à la fois, et c'est cette règle-là qui garantit
qu'aucun lieu de mission ni la planque ne se retrouvent enfermés.

⚠️ **RIEN AU DÉ** : l'heure dit où en est le défilé, l'image dit quelle fusée part ; les couleurs se
tirent à l'empreinte de la fusée.
"""

from __future__ import annotations

#: Le soir de la fête, en heures : le défilé, puis les feux.
HORAIRE = {"defile": [19.0, 21.5], "feux": [22.0, 22.6]}

#: Le défilé : combien de chars, à combien de tuiles l'un de l'autre.
DEFILE = {"chars": 4, "ecart_tuiles": 5}

#: Les feux : une fusée toutes les tant d'images, et leurs couleurs.
FEUX = {"images_entre": 18, "couleurs": ["#3a7bd5", "#ffffff", "#e0453a", "#ffd23f", "#7ee081"]}

RAISON = "RUE FERMÉE — DÉFILÉ DE LA SAINT-JEAN"

CLAIRON = {
    "veille": "DEMAIN SOIR, LA SAINT-JEAN : DÉFILÉ DANS LE FAUBOURG À 19 H, FEUX D'ARTIFICE DU PHARE À 22 H.",
    "jour": "BONNE SAINT-JEAN! DÉFILÉ À 19 H, FEUX DU PHARE À 22 H — LA RUE DU DÉFILÉ SERA FERMÉE.",
}


def rue_du_defile(ville: dict) -> dict | None:
    """La plus longue rue barrable du Faubourg (et pas écartée devant une porte), ou None."""
    z = next((q for q in ville["zones"] if q.get("district") == "faubourg" and q.get("slug") == "faubourg"), None)
    if not z:
        return None

    def dedans(f: dict) -> bool:
        return z["x"] <= f["x"] and f["x"] + f["l"] <= z["x"] + z["l"] and z["y"] <= f["y"] and f["y"] + f["h"] <= z["y"] + z["h"]

    rues = [f for f in ville.get("fermetures", []) if dedans(f) and not f.get("ecartee")]
    if not rues:
        return None
    r = max(rues, key=lambda f: (max(f["l"], f["h"]), -f["x"], -f["y"]))
    return {k: r[k] for k in ("x", "y", "l", "h")}


def pour_le_navigateur(ville: dict) -> dict:
    return {"rue": rue_du_defile(ville), "horaire": {k: list(v) for k, v in HORAIRE.items()},
            "defile": dict(DEFILE), "feux": {**FEUX, "couleurs": list(FEUX["couleurs"])}, "raison": RAISON,
            "clairon": dict(CLAIRON)}
