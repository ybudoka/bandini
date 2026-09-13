"""Le Clairon de la Baie — la manchette du matin, selon ce qu'on a fait hier.

Le navigateur compare les statistiques d'aujourd'hui a celles d'hier et prend
la PREMIERE regle qui passe : l'ordre est donc du plus grave au plus banal, et
la derniere regle sert de repli (rien a signaler).
"""

from __future__ import annotations

from typing import TypedDict


class Regle(TypedDict):
    slug: str
    cle: str
    min: int
    titre: str
    texte: str
    lu: str      # ce que le narrateur DIT : en casse naturelle, sinon le TTS epelle les majuscules


REGLES: list[Regle] = [
    {"slug": "nuit_rouge", "cle": "tues", "min": 3, "titre": "NUIT ROUGE AU FAUBOURG",
     "texte": "TROIS CORPS EN UNE NUIT. LA POLICE PROMET DES RENFORTS.",
     "lu": "Nuit rouge au Faubourg. Trois corps en une nuit ; la police promet des renforts."},
    {"slug": "un_mort", "cle": "tues", "min": 1, "titre": "UN MORT DANS LA RUE",
     "texte": "UN PASSANT RETROUVE SANS VIE. TEMOINS RECHERCHES.",
     "lu": "Un mort dans la rue. Un passant retrouvé sans vie ; témoins recherchés."},
    {"slug": "un_blesse", "cle": "hospitalisations", "min": 1, "titre": "UN BLESSE A L'HOPITAL",
     "texte": "LE DR LACHANCE PARLE D'UNE NUIT AGITEE AUX URGENCES.",
     "lu": "Un blessé à l'hôpital. Le docteur Lachance parle d'une nuit agitée aux urgences."},
    {"slug": "vague_de_vols", "cle": "volees", "min": 3, "titre": "VAGUE DE VOLS D'AUTOS",
     "texte": "TROIS VEHICULES DISPARUS. « ON A NOS SOUPCONS », DIT LE SERGENT.",
     "lu": "Vague de vols d'autos. Trois véhicules disparus. « On a nos soupçons », dit le sergent."},
    {"slug": "un_char_vole", "cle": "volees", "min": 1, "titre": "UN CHAR VOLE AU FAUBOURG",
     "texte": "LE PROPRIETAIRE L'AVAIT LAISSE TOURNER. IL NE TOURNE PLUS.",
     "lu": "Un char volé au Faubourg. Le propriétaire l'avait laissé tourner. Il ne tourne plus."},
    {"slug": "taxi_qui_ne_dort_pas", "cle": "courses", "min": 3, "titre": "LE TAXI QUI NE DORT PAS",
     "texte": "UN CHAUFFEUR ENCHAINE LES COURSES. LES CLIENTS PARLENT DE BROUILLARD.",
     "lu": "Le taxi qui ne dort pas. Un chauffeur enchaîne les courses ; les clients parlent de brouillard."},
    {"slug": "faubourg_inquiet", "cle": "crimes", "min": 5, "titre": "LE FAUBOURG S'INQUIETE",
     "texte": "LES COMMERCANTS DEMANDENT PLUS DE PATROUILLES.",
     "lu": "Le Faubourg s'inquiète. Les commerçants demandent plus de patrouilles."},
    {"slug": "brume", "cle": "crimes", "min": 0, "titre": "BRUME SUR LE BASSIN",
     "texte": "LE TRAVERSIER A PRIS DU RETARD. RIEN A SIGNALER.",
     "lu": "Brume sur le bassin. Le traversier a pris du retard. Rien à signaler."},
]

#: Les manchettes que l'histoire impose (une mission finie fait la une, une fois).
SPECIALES: list[dict] = [
    {"slug": "cravates_chassees", "titre": "LES CRAVATES CHASSEES DU FAUBOURG",
     "texte": "TROIS COINS DE RUE LIBERES EN UNE NUIT. TOUTE LA VILLE EN PARLE.",
     "lu": "Les Cravates chassées du Faubourg. Trois coins de rue libérés en une nuit ; toute la ville en parle."},
]


def speciale(slug: str) -> dict | None:
    for m in SPECIALES:
        if m["slug"] == slug:
            return m
    return None


def manchette(hier: dict, aujourd_hui: dict) -> Regle:
    """La premiere regle dont le delta depasse le minimum ; la derniere sinon."""
    for regle in REGLES:
        if aujourd_hui.get(regle["cle"], 0) - hier.get(regle["cle"], 0) >= regle["min"]:
            return regle
    return REGLES[-1]
