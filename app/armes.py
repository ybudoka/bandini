"""Les armes — de la premiere (les poings, gratuits) a la derniere.

Unites du moteur : degats en points de vie, portee en pixels, cadence et
anticipation en images (60 par seconde). `etoiles_usage` : ce que coute le
simple fait de la sortir sous les yeux d'un policier.

Trois types : `melee` (arc devant soi), `tir` (projectile), `jet` (cone de
particules, l'extincteur). Les armes improvisees (`usures` > 0) se cassent
apres ce nombre de coups.

`son` : le bruitage que fait l'arme quand on s'en sert (un slug de
`audio.CATALOGUE`). ⚠️ Jusqu'au 13 sept. 2026 tout jouait le coup de poing,
le pistolet et le fusil compris — une arme qu'on n'entend pas, on ne sait
pas qu'on la tient.

Les armes a feu (14 sept. 2026) :

- `auto` : on TIENT le bouton, et la cadence rythme la rafale. La dispersion
  s'ouvre de `dispersion` a `dispersion_max` en `REGLES["rafale_images"]`
  images de bouton tenu, et se referme des qu'on lache — c'est ce qui fait
  de la rafale courte un choix, et de l'arrosage un gaspillage.
- `bruit` : le rayon, en tuiles, dans lequel un agent ENTEND le coup — sans
  cone, sans ligne de vue. Un tireur embusque evite d'etre vu, jamais d'etre
  cherche : la distance achete du temps, pas l'impunite. 0 = pas de
  detonation (la fronde, la bouteille qui part).
- `feu_s` : ce que la bouteille laisse derriere elle, en secondes de flaque
  de feu (le Molotov). Ce que la flaque mord est dans `REGLES["incendie"]`.
- `assomme` : ce qu'elle couche se RELEVE. Un coup de poing assomme, il ne
  tue pas : c'est ce qui fait taire un temoin sans en faire un meurtre, et
  la difference vaut deux etoiles.
- ⚠️ Aucune portee ne depasse ce que l'ecran montre : la vue fait 480 px et
  le joueur est au milieu, donc 240 px devant lui. Au-dela, on tire sur ce
  qu'on ne voit pas — `test_armes` lit la borne dans `base.js`.
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
    son: str
    auto: bool
    dispersion_max: float
    bruit: int
    feu_s: int
    assomme: bool


def _a(slug, nom, type_, degats, portee, cadence, prix, *, arc=0.9, anticipation=5, actif=4,
       renverse=False, saigne=0, chargeur=None, munitions_max=None, vproj=0.0,
       dispersion=0.0, cloche=False, plombs=1, prix_munitions=None, etoiles=0, usures=0,
       sprite=None, phase=1, son=None, auto=False, dispersion_max=None, bruit=0,
       feu_s=0, assomme=False) -> Arme:
    return Arme(
        slug=slug, nom=nom, type=type_, degats=degats, portee=portee, arc=arc,
        cadence=cadence, anticipation=anticipation, actif=actif, renverse=renverse,
        saigne=saigne, chargeur=chargeur, munitions_max=munitions_max,
        vitesse_projectile=vproj, dispersion=dispersion, cloche=cloche, plombs=plombs, prix=prix,
        prix_munitions=prix_munitions, etoiles_usage=etoiles, usures=usures,
        sprite=sprite or slug, phase=phase, son=son or slug, auto=auto,
        dispersion_max=dispersion if dispersion_max is None else dispersion_max,
        bruit=bruit, feu_s=feu_s, assomme=assomme,
    )


#: Ce qui n'appartient a aucune arme en particulier, et que le navigateur lit
#: dans `B.defs.armes_regles`.
REGLES: dict = {
    # Une rafale ouvre la dispersion : de `dispersion` a `dispersion_max` en ce
    # nombre d'images de bouton tenu (trois quarts de seconde). Lacher referme
    # tout d'un coup.
    "rafale_images": 45,
    # La flaque de feu d'un Molotov : son rayon, et ce qu'elle mord PAR SECONDE
    # a qui reste dedans — passant, joueur, char. ⚠️ 12/s : un passant de
    # 100 PV y meurt en huit secondes s'il ne bouge pas ; il bouge (il fuit,
    # et le feu le pousse dehors). Un char qui reste dessus tombe sous le
    # cinquieme de sa vie et brule ensuite tout seul (`vehicules.PHYSIQUE`).
    "incendie": {"rayon_px": 20, "degats_par_seconde": 12},
}


#: ⚠️ La premiere entree est TOUJOURS les poings, a 0 $ : c'est ce que le
#: joueur a quand la prison lui a tout pris. Les prix des armes achetables
#: montent dans l'ordre du catalogue (ordre d'achat naturel).
#:
#: ⚠️ `son` vaut le slug de l'arme par defaut ; seuls les poings font `coup`.
#: `test_armes` verifie que chaque son existe au catalogue audio, et
#: `test_audio` que le navigateur a un effet (avec son repli) pour chacun.
CATALOGUE: list[Arme] = [
    _a("poings", "Poings", "melee", 8, 12, 18, 0, anticipation=5, actif=4, son="coup",
       assomme=True),
    # Celui des hommes de Sal (16 sept. 2026, demande de Martin : « a main nue
    # ou poing americain, un peu plus fort »). UN PEU : entre les poings et le
    # baton. Et ca reste un coup de poing — il assomme, il ne tue pas. On le
    # ramasse sur celui qu'on a couche, ou on le paie chez Gus (17 sept. 2026,
    # Martin : « on devrait aussi pouvoir l'acheter ») : la moins chere de la
    # vitrine, sous la fronde, parce qu'elle cogne a peine plus que les poings.
    _a("poing_americain", "Poing américain", "melee", 12, 12, 18, 25, anticipation=5,
       actif=4, assomme=True),
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
       vproj=7.0, dispersion=0.03, prix_munitions=40, etoiles=1, bruit=14),
    _a("fusil", "Fusil à pompe", "tir", 12, 90, 45, 600, chargeur=8, munitions_max=24,
       vproj=6.0, dispersion=0.18, plombs=6, prix_munitions=60, etoiles=1, bruit=18),
    # ⚠️ Les trois qui suivent ne se vendent qu'au MARCHE NOIR (`magasins`) :
    # ce qui fait du bruit se vend sans facture. Chacune repond a une question
    # que les deux autres ne savent pas regler.
    #
    # « Ils sont groupes, et je veux que ca dure. » La bouteille part EN
    # CLOCHE, comme la bille de fronde, et la ou elle casse, une flaque de feu
    # brule `feu_s` secondes. Elle ne fait pas de detonation (`bruit` 0) : ce
    # qu'on entend, c'est le verre qui casse — a l'arrivee, pas au depart.
    _a("molotov", "Cocktail Molotov", "tir", 6, 140, 40, 700, chargeur=3, munitions_max=9,
       vproj=3.4, cloche=True, prix_munitions=90, etoiles=1, feu_s=5),
    # « Ils sont trois. » Automatique : on TIENT. Peu de degats par balle, une
    # cadence quatre fois celle du pistolet, et la dispersion qui s'ouvre tant
    # qu'on tient. ⚠️ Les munitions font l'equilibre, pas les degats : le
    # chargeur de trente part en trois secondes, et il coute.
    _a("mitraillette", "Mitraillette", "tir", 9, 150, 5, 900, chargeur=30, munitions_max=120,
       vproj=7.0, dispersion=0.04, dispersion_max=0.22, auto=True, prix_munitions=80,
       etoiles=1, bruit=16),
    # « Il est loin. » Lente, sans dispersion, un passant d'une balle — et la
    # plus longue portee du jeu, PLAFONNEE a ce que l'ecran montre (230 px, la
    # demi-vue fait 240). C'est aussi celle qu'on entend de plus loin.
    _a("carabine", "Carabine", "tir", 60, 230, 55, 1200, chargeur=5, munitions_max=25,
       vproj=10.0, prix_munitions=50, etoiles=1, bruit=22),
]

ORDRE_CYCLE = [a["slug"] for a in CATALOGUE]


def par_slug(slug: str) -> Arme | None:
    for arme in CATALOGUE:
        if arme["slug"] == slug:
            return arme
    return None


def achetables() -> list[Arme]:
    return [a for a in CATALOGUE if a["prix"] > 0]
