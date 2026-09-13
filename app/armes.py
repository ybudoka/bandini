"""Les armes — de la premiere (les poings, gratuits) a la derniere.

Unites du moteur : degats en points de vie, portee en pixels, cadence et
anticipation en images (60 par seconde). `etoiles_usage` : ce que coute le
simple fait de la sortir sous les yeux d'un policier.

Trois types : `melee` (arc devant soi), `tir` (projectile), `jet` (cone de
particules, l'extincteur). Les armes improvisees (`usures` > 0) se cassent
apres ce nombre de coups.
"""

from __future__ import annotations

from typing import TypedDict

TYPES = ("melee", "tir", "jet")


class Arme(TypedDict):
    slug: str
    nom: str
    type: str
    degats: int
    portee: int
    arc: float
    cadence: int
    anticipation: int
    actif: int
    renverse: bool
    saigne: int
    chargeur: int | None
    munitions_max: int | None
    vitesse_projectile: float
    dispersion: float
    cloche: bool
    plombs: int
    prix: int
    prix_munitions: int | None
    etoiles_usage: int
    usures: int
    sprite: str
    phase: int


def _a(slug, nom, type_, degats, portee, cadence, prix, *, arc=0.9, anticipation=5, actif=4,
       renverse=False, saigne=0, chargeur=None, munitions_max=None, vproj=0.0,
       dispersion=0.0, cloche=False, plombs=1, prix_munitions=None, etoiles=0, usures=0,
       sprite=None, phase=1) -> Arme:
    return Arme(
        slug=slug, nom=nom, type=type_, degats=degats, portee=portee, arc=arc,
        cadence=cadence, anticipation=anticipation, actif=actif, renverse=renverse,
        saigne=saigne, chargeur=chargeur, munitions_max=munitions_max,
        vitesse_projectile=vproj, dispersion=dispersion, cloche=cloche, plombs=plombs, prix=prix,
        prix_munitions=prix_munitions, etoiles_usage=etoiles, usures=usures,
        sprite=sprite or slug, phase=phase,
    )


#: ⚠️ La premiere entree est TOUJOURS les poings, a 0 $ : c'est ce que le
#: joueur a quand la prison lui a tout pris. Les prix des armes achetables
#: montent dans l'ordre du catalogue (ordre d'achat naturel).
CATALOGUE: list[Arme] = [
    _a("poings", "Poings", "melee", 8, 12, 18, 0, anticipation=5, actif=4),
    _a("cone", "Cône orange", "melee", 12, 16, 22, 0, anticipation=6, actif=5, usures=4,
       sprite="cone"),
    _a("bouteille", "Bouteille", "melee", 14, 12, 16, 0, anticipation=5, actif=4, usures=3,
       saigne=45),
    _a("pelle", "Pelle", "melee", 22, 20, 30, 0, anticipation=10, actif=5, renverse=True,
       usures=5),
    # ⚠️ La seule arme qui tire EN CLOCHE : la bille passe par-dessus une
    # cloture et retombe. Le navigateur lui donne un `z` et une gravite.
    _a("fronde", "Fronde", "tir", 10, 140, 30, 30, chargeur=30, munitions_max=90,
       vproj=5.0, cloche=True, prix_munitions=5, etoiles=0),
    _a("batte", "Bâton", "melee", 18, 18, 26, 40, arc=1.1, anticipation=8, actif=5,
       renverse=True),
    _a("couteau", "Couteau", "melee", 25, 12, 12, 60, arc=0.7, anticipation=4, actif=3,
       saigne=90),
    _a("extincteur", "Extincteur", "jet", 3, 40, 1, 80, chargeur=100, munitions_max=100,
       etoiles=0),
    _a("pistolet", "Pistolet", "tir", 30, 180, 20, 250, chargeur=12, munitions_max=48,
       vproj=7.0, dispersion=0.03, prix_munitions=40, etoiles=1),
    _a("fusil", "Fusil à pompe", "tir", 12, 90, 45, 600, chargeur=8, munitions_max=24,
       vproj=6.0, dispersion=0.18, plombs=6, prix_munitions=60, etoiles=1),
]

ORDRE_CYCLE = [a["slug"] for a in CATALOGUE]


def par_slug(slug: str) -> Arme | None:
    for arme in CATALOGUE:
        if arme["slug"] == slug:
            return arme
    return None


def achetables() -> list[Arme]:
    return [a for a in CATALOGUE if a["prix"] > 0]
