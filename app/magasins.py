"""Les comptoirs : ce qu'on y achete, a quel prix.

Les prix des armes et des vehicules viennent de leur catalogue ; un magasin ne
fait que dire ce qu'il tient. Les tenues sont les seules choses qui n'existent
qu'ici.
"""

from __future__ import annotations

from typing import TypedDict

TYPES = ("armurerie", "vetements", "garage", "casse_croute")

#: Les commerces qui n'ont pas de porte : on les sert sur le trottoir.
#: `service` dit ce qu'on y achete, `tarif`/`gain_pv` pointent dans
#: `economie.TARIFS` — les prix ne vivent jamais en double.
AMBULANTS: list[dict] = [
    {"slug": "hotdog", "nom": "Kiosque à hot-dogs", "sprite": "kiosque_hotdog",
     "service": "manger", "tarif": "hotdog", "gain_pv": "hotdog_pv",
     "nombre": 3, "sur": "trottoir", "heures": None, "phase": 1},
    {"slug": "journaux", "nom": "Kiosque à journaux", "sprite": "kiosque_journaux",
     "service": "journal", "tarif": "journal", "gain_pv": None,
     "nombre": 2, "sur": "trottoir", "heures": [0.25, 0.75], "phase": 1},
    {"slug": "cafe", "nom": "Roulotte à café", "sprite": "roulotte_cafe",
     "service": "manger", "tarif": "cafe", "gain_pv": "cafe_pv",
     "nombre": 2, "sur": "trottoir", "heures": [0.2, 0.6], "phase": 1},
    {"slug": "camion_cuisine", "nom": "Camion-restaurant", "sprite": "camion_cuisine",
     "service": "manger", "tarif": "poutine", "gain_pv": "poutine_pv",
     "nombre": 2, "sur": "stationnement", "heures": None, "phase": 1},
]


def ambulant(slug: str) -> dict | None:
    for commerce in AMBULANTS:
        if commerce["slug"] == slug:
            return commerce
    return None


class Magasin(TypedDict):
    slug: str
    nom: str
    type: str
    lieu: str
    articles: list[str]
    munitions: list[str]
    tenues: list[dict]
    services: list[str]
    phase: int


TENUES = [
    {"slug": "chandail", "nom": "Chandail de Rocco", "prix": 0, "couleur": "#c0392b"},
    {"slug": "coupe_vent", "nom": "Coupe-vent bleu", "prix": 80, "couleur": "#2980b9"},
    {"slug": "veste_cuir", "nom": "Veste de cuir", "prix": 200, "couleur": "#2c2c2c"},
    {"slug": "complet", "nom": "Complet gris", "prix": 500, "couleur": "#7f8c8d"},
    {"slug": "chemise_hawai", "nom": "Chemise hawaïenne", "prix": 120, "couleur": "#f39c12"},
]

CATALOGUE: list[Magasin] = [
    {"slug": "armurerie", "nom": "Chez Gus", "type": "armurerie", "lieu": "armurerie",
     "articles": ["fronde", "batte", "couteau", "extincteur", "pistolet", "fusil"],
     "munitions": ["fronde", "pistolet", "fusil"], "tenues": [], "services": [], "phase": 1},
    {"slug": "vetements", "nom": "Boutique Rosa", "type": "vetements", "lieu": "vetements",
     "articles": [], "munitions": [], "tenues": TENUES, "services": [], "phase": 1},
    {"slug": "garage", "nom": "Garage Rocco Bandini", "type": "garage", "lieu": "garage",
     "articles": ["moto", "auto", "taxi"], "munitions": [], "tenues": [],
     "services": ["vendre", "reparer", "repeindre"], "phase": 1},
    {"slug": "casse_croute", "nom": "Casse-croûte du Faubourg", "type": "casse_croute",
     "lieu": "casse_croute", "articles": [], "munitions": [], "tenues": [],
     "services": ["hotdog"], "phase": 1},
]


def par_slug(slug: str) -> Magasin | None:
    for magasin in CATALOGUE:
        if magasin["slug"] == slug:
            return magasin
    return None


#: Le marche noir : Josee, au bar, une fois le Faubourg libere (M5). Les
#: memes armes que Chez Gus, mais a ce prix-la — et sans facture.
MARCHE_NOIR: dict = {"apres": "m5", "rabais": 0.7, "articles": ["couteau", "pistolet", "fusil"],
                     "munitions": ["pistolet", "fusil"]}
