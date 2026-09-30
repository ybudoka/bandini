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
- `lance` (28 sept. 2026, « les explosifs ») : la grenade et la dynamite. On
  les ALLUME (la `meche`, en images, brule des cet instant, dans la main), on
  les lance en cloche, et elles sautent au bout de la meche par l'explosion
  commune (`explosions.js`) : `souffle` est son rayon en pixels, `degats` ce
  qu'elle mord au centre. `rebond` : la grenade rebondit sur les murs et au
  sol, la dynamite tombe et roule un peu. ⚠️ `bruit` 0 : ce qu'on entend,
  c'est l'EXPLOSION (`REGLES["explosion"]`), pas le lancer.
- ⚠️ Aucune portee ne depasse ce que l'ecran montre : la vue fait 480 px et
  le joueur est au milieu, donc 240 px devant lui. Au-dela, on tire sur ce
  qu'on ne voit pas — `test_armes` lit la borne dans `base.js`.
"""

from __future__ import annotations

from typing import TypedDict

TYPES = ("melee", "tir", "jet", "lance")


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
    foire: bool
    meche: int
    souffle: int
    rebond: bool


def _a(slug, nom, type_, degats, portee, cadence, prix, *, arc=0.9, anticipation=5, actif=4,
       renverse=False, saigne=0, chargeur=None, munitions_max=None, vproj=0.0,
       dispersion=0.0, cloche=False, plombs=1, prix_munitions=None, etoiles=0, usures=0,
       sprite=None, phase=1, son=None, auto=False, dispersion_max=None, bruit=0,
       feu_s=0, assomme=False, foire=False, meche=0, souffle=0, rebond=False) -> Arme:
    return Arme(
        slug=slug, nom=nom, type=type_, degats=degats, portee=portee, arc=arc,
        cadence=cadence, anticipation=anticipation, actif=actif, renverse=renverse,
        saigne=saigne, chargeur=chargeur, munitions_max=munitions_max,
        vitesse_projectile=vproj, dispersion=dispersion, cloche=cloche, plombs=plombs, prix=prix,
        prix_munitions=prix_munitions, etoiles_usage=etoiles, usures=usures,
        sprite=sprite or slug, phase=phase, son=son or slug, auto=auto,
        dispersion_max=dispersion if dispersion_max is None else dispersion_max,
        bruit=bruit, feu_s=feu_s, assomme=assomme, foire=foire,
        meche=meche, souffle=souffle, rebond=rebond,
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
    # Ce qui se lance (`lance`) et ce qui saute. `bruit_tuiles` : le rayon dans
    # lequel un agent ENTEND l'explosion — plus loin qu'une carabine (22) : une
    # detonation de chantier s'entend a l'autre bout du quartier. Le reste est
    # la physique du vol : la gravite (celle de la bille de fronde), ce qu'un
    # rebond garde de la vitesse, et ce que le sol en laisse a chaque image.
    # ⚠️ `tombe_amorti` : ce que garde de sa vitesse ce qui NE rebondit pas en
    # touchant le sol (la dynamite tombe, roule un peu, s'arrete). Sans lui — et
    # sans l'amorti du rebond sur la vitesse AU SOL — une grenade lancee pour
    # 150 px roulait jusqu'a 228 (l'essai du 29 sept. 2026).
    "explosion": {"bruit_tuiles": 30, "gravite": 0.12, "rebond_amorti": 0.45,
                  "tombe_amorti": 0.3, "roule_friction": 0.9},
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
    # Le parapluie de Rosa (`magasins.TENUES`, `main`) : une arme TANT QU'ON L'A A LA MAIN
    # (`Combat.suivreLaMain`), jamais chez Gus (prix 0). Un coup faible ; au dixieme, il se revire.
    _a("parapluie", "Parapluie", "melee", 8, 16, 20, 0, anticipation=5, actif=4, usures=10),
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
    # ⚠️ Les cinq qui suivent ne se vendent qu'au MARCHE NOIR (`magasins`) :
    # ce qui fait du bruit se vend sans facture. Chacune repond a une question
    # que les deux autres ne savent pas regler.
    #
    # « Ils sont groupes, et je veux que ca dure. » La bouteille part EN
    # CLOCHE, comme la bille de fronde, et la ou elle casse, une flaque de feu
    # brule `feu_s` secondes. Elle ne fait pas de detonation (`bruit` 0) : ce
    # qu'on entend, c'est le verre qui casse — a l'arrivee, pas au depart.
    # « Ils sont derriere le mur. » Elle part en cloche, TOMBE et roule un peu —
    # elle ne rebondit pas — et saute au bout d'une meche qu'on voit gresiller.
    # Moins chere que la grenade, plus lente, un souffle plus large. On en trouve
    # aussi sur les chantiers (`chantiers.js`).
    _a("dynamite", "Dynamite", "lance", 140, 110, 45, 650, chargeur=3, munitions_max=6,
       vproj=3.0, cloche=True, prix_munitions=90, etoiles=1, son="meche", meche=240, souffle=64),
    _a("molotov", "Cocktail Molotov", "tir", 6, 140, 40, 700, chargeur=3, munitions_max=9,
       vproj=3.4, cloche=True, prix_munitions=90, etoiles=1, feu_s=5),
    # « Ils sont au coin. » Elle rebondit sur les murs et roule ; la meche
    # (2,5 s) brule DES qu'on la degoupille : la tenir, c'est la « cuire ».
    # Son son est la GOUPILLE, pas la meche : une grenade ne s'allume pas.
    # ⚠️ 150 au centre, pas 110 : a 110, tombee a 14 px d'un char, elle le laissait
    # a 23/100, sans feu (l'essai du 29 sept. 2026). Un passant meurt a 16 px.
    _a("grenade", "Grenade", "lance", 150, 150, 40, 800, chargeur=3, munitions_max=9,
       vproj=3.6, cloche=True, prix_munitions=120, etoiles=1, son="goupille", meche=150, souffle=48,
       rebond=True),
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
    # ⚠️ **LA CARABINE À BOUCHON de la galerie de tir** — jamais achetée, jamais
    # dans le sac : le forain la PRÊTE le temps du défi (`Histoire.commencerDefi`),
    # puis la reprend. `foire` est la défense qui la rend inoffensive dans
    # `combat.js` : pas de crime signalé, personne ne fuit, aucun agent
    # n'entend, et le bouchon ne blesse QUE les cibles — jamais un passant.
    # C'est un jeu d'adresse, pas un stand de tir ; un joueur sans arme à feu
    # pouvait jusque-là se baisser les bras devant la galerie (les poings
    # n'atteignent pas les décors).
    _a("carabine_foire", "Carabine à bouchon", "tir", 10, 160, 20, 0,
       chargeur=999, munitions_max=999, vproj=6.0, sprite="carabine",
       son="carabine_foire", foire=True),
]

ORDRE_CYCLE = [a["slug"] for a in CATALOGUE]


def par_slug(slug: str) -> Arme | None:
    for arme in CATALOGUE:
        if arme["slug"] == slug:
            return arme
    return None


def achetables() -> list[Arme]:
    return [a for a in CATALOGUE if a["prix"] > 0]
