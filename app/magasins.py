"""Les comptoirs : ce qu'on y achete, a quel prix.

Les prix des armes et des vehicules viennent de leur catalogue ; un magasin ne
fait que dire ce qu'il tient. Les tenues sont les seules choses qui n'existent
qu'ici.
"""

from __future__ import annotations

from typing import TypedDict

TYPES = ("armurerie", "vetements", "garage", "casse_croute")


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
