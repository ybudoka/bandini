"""Le Clairon de la Baie — la manchette du matin, selon ce qu'on a fait hier.

Le navigateur compare les statistiques d'aujourd'hui a celles d'hier et prend
la PREMIERE regle qui passe : l'ordre est donc du plus grave au plus banal, et
la derniere regle sert de repli (rien a signaler).
"""

from __future__ import annotations

from typing import TypedDict


class Regle(TypedDict):
    cle: str
    min: int
    titre: str
    texte: str


REGLES: list[Regle] = [
    {"cle": "tues", "min": 3, "titre": "NUIT ROUGE AU FAUBOURG",
     "texte": "TROIS CORPS EN UNE NUIT. LA POLICE PROMET DES RENFORTS."},
    {"cle": "tues", "min": 1, "titre": "UN MORT DANS LA RUE",
     "texte": "UN PASSANT RETROUVE SANS VIE. TEMOINS RECHERCHES."},
    {"cle": "hospitalisations", "min": 1, "titre": "UN BLESSE A L'HOPITAL",
     "texte": "LE DR LACHANCE PARLE D'UNE NUIT AGITEE AUX URGENCES."},
    {"cle": "volees", "min": 3, "titre": "VAGUE DE VOLS D'AUTOS",
     "texte": "TROIS VEHICULES DISPARUS. « ON A NOS SOUPCONS », DIT LE SERGENT."},
    {"cle": "volees", "min": 1, "titre": "UN CHAR VOLE AU FAUBOURG",
     "texte": "LE PROPRIETAIRE L'AVAIT LAISSE TOURNER. IL NE TOURNE PLUS."},
    {"cle": "courses", "min": 3, "titre": "LE TAXI QUI NE DORT PAS",
     "texte": "UN CHAUFFEUR ENCHAINE LES COURSES. LES CLIENTS PARLENT DE BROUILLARD."},
    {"cle": "crimes", "min": 5, "titre": "LE FAUBOURG S'INQUIETE",
     "texte": "LES COMMERCANTS DEMANDENT PLUS DE PATROUILLES."},
    {"cle": "crimes", "min": 0, "titre": "BRUME SUR LE BASSIN",
     "texte": "LE TRAVERSIER A PRIS DU RETARD. RIEN A SIGNALER."},
]


def manchette(hier: dict, aujourd_hui: dict) -> Regle:
    """La premiere regle dont le delta depasse le minimum ; la derniere sinon."""
    for regle in REGLES:
        if aujourd_hui.get(regle["cle"], 0) - hier.get(regle["cle"], 0) >= regle["min"]:
            return regle
    return REGLES[-1]
