"""Les missions et les defis — donneur, prerequis, objectifs types, recompense.

⚠️ M0 : catalogue vide ; les cinq missions du Faubourg et les trois defis
arrivent au jalon M6, quand la ville et les vehicules existent. Les types
d'objectifs, eux, sont la source unique que le navigateur respecte.
"""

from __future__ import annotations

from typing import TypedDict

TYPES_OBJECTIFS = (
    "aller",       # atteindre un point (x, y, rayon)
    "parler",      # toucher un PNJ
    "monter",      # monter dans un vehicule (type, marque)
    "livrer",      # amener le vehicule courant a un point, chrono, sans degats
    "ramasser",    # ramasser un objet
    "tuer",        # mettre KO n ennemis d'un groupe dans une zone
    "survivre",    # tenir n secondes
    "course",      # passer des points de passage dans l'ordre, chrono
    "semer",       # redescendre a 0 etoile
    "retourner",   # revenir au donneur
)

ECHECS = ("mort", "arrete", "vehicule_detruit", "chrono")


class Mission(TypedDict):
    slug: str
    titre: str
    donneur: dict
    prerequis: list[str]
    recompense: int
    objectifs: list[dict]
    echec: list[str]
    dialogue: dict
    phase: int


CATALOGUE: list[Mission] = []

DEFIS: list[dict] = []

NB_MISSIONS = len(CATALOGUE)


def par_slug(slug: str) -> Mission | None:
    for mission in CATALOGUE:
        if mission["slug"] == slug:
            return mission
    return None


def ordre_topologique() -> list[str]:
    """Les slugs dans un ordre ou chaque prerequis precede sa mission.

    Leve ValueError sur un cycle ou un prerequis inconnu.
    """
    restantes = {m["slug"]: set(m["prerequis"]) for m in CATALOGUE}
    for slug, prerequis in restantes.items():
        inconnus = prerequis - set(restantes)
        if inconnus:
            raise ValueError(f"{slug} : prerequis inconnus {sorted(inconnus)}")
    ordre: list[str] = []
    while restantes:
        pretes = sorted(s for s, p in restantes.items() if not p)
        if not pretes:
            raise ValueError(f"cycle de prerequis parmi {sorted(restantes)}")
        for slug in pretes:
            ordre.append(slug)
            del restantes[slug]
        for prerequis in restantes.values():
            prerequis.difference_update(pretes)
    return ordre
