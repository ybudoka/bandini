"""La musique du jeu, ecrite en notes plutot qu'enregistree.

⚠️ Pourquoi des notes et pas un mp3 : un fichier de musique de menu pese plus
lourd que tout le reste du paquet reuni, coute des credits a generer, et ne se
teste pas (on ne peut pas juger un son). Un theme ecrit en notes pese 3 Ko,
se relit, se corrige a la note pres, et se juge : la tonalite, la longueur de
la boucle, les collisions entre voix. Le jour ou Martin veut une vraie piece
jouee par de vrais instruments, elle se posera par-dessus comme les radios —
c'est la meme regle que partout dans `audio.py` : l'echantillon quand il
existe, la synthese sinon.

Python decide (le catalogue : notes, tempo, formes d'onde), JS calcule (les
frequences, l'ordonnancement, les enveloppes).

Une note est `[pas, hauteur, duree, volume?]` :
  - `pas`     : quand, en pas depuis le debut du motif (ici la croche) ;
  - `hauteur` : un numero MIDI (60 = do du milieu) — ou, pour une voix
                « bruit », la frequence de coupure du filtre en Hz ;
  - `duree`   : combien de pas la note tient ;
  - `volume`  : facultatif, relatif a celui de la voix (1 par defaut).

Une voix qui porte `motif` se repete tous les `motif` pas jusqu'au bout du
morceau : la basse tourne sur huit mesures, la batterie sur une seule, et on
ne recopie pas quatre-vingt-seize fois le meme charleston.
"""

import math
from typing import NotRequired, TypedDict

#: 8 pas par mesure : la croche est notre plus petite unite.
PAS_PAR_MESURE = 8
PAS_PAR_TEMPS = 2


class Voix(TypedDict):
    role: str
    forme: str
    volume: float
    motif: NotRequired[int]
    notes: list[list[float]]


class Morceau(TypedDict):
    slug: str
    nom: str
    bpm: int
    pas_par_temps: int
    pas: int
    volume: float
    voix: list[Voix]


def _mesures(*accords: tuple[int, ...]) -> list[list[float]]:
    """Une note de basse par temps, en marchant : 4 par mesure, tenues jusqu'a
    la suivante. `accords` donne les quatre hauteurs de chaque mesure."""
    notes: list[list[float]] = []
    for m, quatre in enumerate(accords):
        for t, hauteur in enumerate(quatre):
            notes.append([m * PAS_PAR_MESURE + t * PAS_PAR_TEMPS, hauteur, PAS_PAR_TEMPS])
    return notes


def _accords(*mesures: tuple[int, ...]) -> list[list[float]]:
    """Deux attaques par mesure (le 1 et le 3), chacune plaquant tout l'accord.
    ⚠️ Duree 3 et non 4 : les accords se taisent juste avant le suivant, sinon
    la nappe devient une bouillie ou plus rien ne se detache."""
    notes: list[list[float]] = []
    for m, accord in enumerate(mesures):
        for depart in (0, 4):
            for hauteur in accord:
                notes.append([m * PAS_PAR_MESURE + depart, hauteur, 3])
    return notes


#: La grille : huit mesures qui tournent (Am7 Dm7 G7 Cmaj7 Fmaj7 Bm7b5 E7 Am7).
#: C'est le tour de chant le plus banal du jazz — et c'est voulu : il doit
#: pouvoir tourner sous un menu sans jamais accrocher l'oreille.
_BASSE = _mesures(
    (45, 52, 55, 52),   # Am7  : la, mi, sol, mi
    (50, 45, 48, 52),   # Dm7  : re, la, do, mi
    (43, 50, 53, 50),   # G7   : sol, re, fa, re
    (48, 43, 52, 43),   # Cmaj7: do, sol, mi, sol
    (41, 48, 52, 48),   # Fmaj7: fa, do, mi, do
    (47, 53, 45, 50),   # Bm7b5: si, fa, la, re
    (40, 47, 50, 56),   # E7   : mi, si, re, sol#
    (45, 52, 48, 52),   # Am7  : la, mi, do, mi
)

_NAPPE = _accords(
    (60, 64, 67),       # Am7
    (62, 65, 69),       # Dm7
    (59, 62, 65),       # G7
    (64, 67, 71),       # Cmaj7
    (57, 60, 64),       # Fmaj7
    (57, 62, 65),       # Bm7b5
    (56, 59, 62),       # E7
    (57, 60, 64),       # Am7
)

#: La melodie ne se repete pas : seize mesures, une premiere fois basse et
#: retenue, une seconde plus haut. C'est la seule voix qui raconte quelque
#: chose — les autres tournent.
_CHANT: list[list[float]] = [
    # Huit premieres mesures : elle reste dans le grave, elle traine.
    [0, 64, 4], [4, 67, 2], [6, 69, 2],
    [8, 72, 6], [14, 69, 2],
    [16, 71, 4], [20, 67, 4],
    [24, 64, 6],
    [32, 69, 3], [35, 72, 3], [38, 69, 2],
    [40, 65, 4], [44, 62, 4],
    [48, 68, 4], [52, 71, 4],
    [56, 69, 8],
    # Huit suivantes : la meme idee, une quarte plus haut, plus ouverte.
    [64, 69, 2], [66, 72, 2], [68, 76, 4],
    [72, 74, 4], [76, 72, 4],
    [80, 71, 2], [82, 74, 2], [84, 77, 4],
    [88, 76, 6],
    [96, 72, 4], [100, 69, 4],
    [104, 74, 4], [108, 65, 4],
    [112, 68, 2], [114, 71, 2], [116, 74, 4],
    [120, 69, 8],
]

#: Le balai sur la caisse claire : le contretemps (2 et 4) marque, le temps
#: fort a peine effleure. Une seule mesure, repetee cent vingt-huit fois.
_BALAI: list[list[float]] = [
    [0, 4200, 1, 0.30],
    [2, 6800, 1, 1.00],
    [4, 4200, 1, 0.30],
    [6, 6800, 1, 1.00],
]

#: L'OUVERTURE — le car de six heures entre dans la ville.
#:
#: ⚠️ Elle n'est PAS le theme du menu ralenti : le menu tourne en rond sans
#: accrocher l'oreille (c'est sa job), l'ouverture doit RACONTER quelque chose
#: en trente secondes et se taire. Elle marche donc sur une grille qui ne se
#: resout pas — Am F C G, puis Am F Dm E7, qui laisse la question ouverte au
#: moment exact ou le bonhomme descend du car.
#:
#: ⚠️ Trois voix, et rien d'autre : une basse qui tient la note comme un moteur
#: au ralenti, une nappe, et un chant de corne de brume. Une batterie ici
#: mettrait un rythme sous une scene ou personne ne marche encore.
_OUV_BASSE: list[list[float]] = [
    [0, 33, 4], [4, 40, 4],      # Am  : la, mi
    [8, 29, 4], [12, 36, 4],     # F   : fa, do
    [16, 36, 4], [20, 43, 4],    # C   : do, sol
    [24, 31, 4], [28, 38, 4],    # G   : sol, re
    [32, 33, 4], [36, 40, 4],    # Am
    [40, 29, 4], [44, 36, 4],    # F
    [48, 38, 4], [52, 45, 4],    # Dm  : re, la
    [56, 40, 4], [60, 47, 4],    # E7  : mi, si
]

_OUV_NAPPE = _accords(
    (57, 60, 64),       # Am
    (57, 60, 65),       # F
    (55, 60, 64),       # C
    (55, 59, 62),       # G
    (57, 60, 64),       # Am
    (57, 60, 65),       # F
    (57, 62, 65),       # Dm
    (56, 59, 64),       # E7
)

#: La corne de brume : des notes longues, peu nombreuses, et des silences. Elle
#: ne repete pas — elle descend, exactement comme la ville qui se referme.
_OUV_CHANT: list[list[float]] = [
    [0, 69, 6], [8, 72, 6],
    [16, 76, 4], [20, 72, 4],
    [24, 71, 8],
    [32, 69, 4], [36, 67, 4],
    [40, 65, 8],
    [48, 69, 6],
    [56, 64, 8],
]

MORCEAUX: list[Morceau] = [
    {
        "slug": "ouverture",
        "nom": "L'autobus de six heures",
        "bpm": 64,
        "pas_par_temps": PAS_PAR_TEMPS,
        "pas": 8 * PAS_PAR_MESURE,
        "volume": 0.85,
        "voix": [
            {"role": "basse", "forme": "triangle", "volume": 0.40, "notes": _OUV_BASSE},
            {"role": "nappe", "forme": "sine", "volume": 0.12, "notes": _OUV_NAPPE},
            {"role": "chant", "forme": "sine", "volume": 0.16, "notes": _OUV_CHANT},
        ],
    },
    {
        "slug": "titre",
        "nom": "Baie-des-Brumes",
        "bpm": 92,
        "pas_par_temps": PAS_PAR_TEMPS,
        "pas": 16 * PAS_PAR_MESURE,
        "volume": 0.85,
        "voix": [
            {"role": "basse", "forme": "triangle", "volume": 0.45,
             "motif": 8 * PAS_PAR_MESURE, "notes": _BASSE},
            {"role": "nappe", "forme": "sine", "volume": 0.13,
             "motif": 8 * PAS_PAR_MESURE, "notes": _NAPPE},
            {"role": "chant", "forme": "square", "volume": 0.14, "notes": _CHANT},
            {"role": "balai", "forme": "bruit", "volume": 0.08,
             "motif": PAS_PAR_MESURE, "notes": _BALAI},
        ],
    },
]


def par_slug(slug: str) -> Morceau | None:
    """N'importe quel morceau du jeu, ecrit a la main ou genere.

    ⚠️ Il ne cherchait que dans `MORCEAUX` — c'est-a-dire le seul theme ecrit a
    la main. Les stations, les ambiances et les pieces de rue etaient donc
    INECOUTABLES avec `scripts/musique_apercu.py`, alors que c'est exactement ce
    a quoi il sert : juger une musique a l'oreille avant de la deployer. Cinq
    pieces de rue qu'on ne peut pas ecouter, ce sont cinq pieces qu'on livre en
    esperant.
    """
    for morceau in MORCEAUX:
        if morceau["slug"] == slug:
            return morceau
    for style in STATIONS:
        if style["slug"] == slug:
            return generer_station(style)
    for style in AMBIANCES:
        if style["slug"] == slug:
            return generer_station(style, station=False)
    # ⚠️ Et les commerces AUSSI : le juge qui tient cette fonction dit exactement
    # pourquoi — « une piece qu'on ne peut pas ecouter, c'est une piece qu'on
    # livre en esperant ». Il a attrape les quatre tounes de boutique le jour ou
    # elles sont nees, pour la meme raison qu'il avait attrape les cinq pieces
    # de rue.
    for style in COMMERCES:
        if style["slug"] == slug:
            return generer_station(style, station=False)
    return rue_par_slug(slug)


def duree_s(morceau: Morceau) -> float:
    """La longueur de la boucle, en secondes."""
    return morceau["pas"] * 60.0 / morceau["bpm"] / morceau["pas_par_temps"]



def exporter() -> list[Morceau]:
    return ([dict(m) for m in MORCEAUX] + stations() + ambiances()  # type: ignore[misc]
            + rues() + commerces() + [orgue()])


# --- Les stations procedurales (M9) ----------------------------------------

#: ⚠️ Une station par char, ecrite par une GRAINE plutot qu'a la main. Le
#: camion a sa toune, la remorqueuse la sienne, et aucune ne coute un mp3 ni
#: un credit ElevenLabs. C'est le meme sequenceur trois voix que le theme du
#: menu (`Son.Mus`) : le navigateur n'apprend rien de neuf, il recoit un
#: morceau de plus dans `musiques`.
#:
#: ⚠️ Pourquoi generer en Python et non dans le navigateur : ici, pytest lit
#: chaque note. Le juge verifie que TOUTES les hauteurs tombent dans la gamme
#: — une seule note a cote s'entend, et personne ne debogue une fausse note a
#: l'oreille en conduisant un camion.


class _Des:
    """Le meme des que `carte.Des` : une graine, une suite, aucune surprise."""

    def __init__(self, graine: int) -> None:
        self.etat = graine & 0xFFFFFFFF

    def suivant(self) -> int:
        self.etat = (self.etat * 1664525 + 1013904223) & 0xFFFFFFFF
        return self.etat

    def entier(self, a: int, b: int) -> int:
        return a + self.suivant() % (b - a + 1)

    def chance(self, p: float) -> bool:
        return (self.suivant() % 1000) / 1000.0 < p

    def choix(self, options):
        return options[self.suivant() % len(options)]


class Style(TypedDict):
    slug: str
    nom: str
    graine: int
    bpm: int
    tonique: int
    gamme: tuple[int, ...]
    grille: tuple[int, ...]
    forme_chant: str
    forme_nappe: str
    volume: float


#: `gamme` = les demi-tons au-dessus de la tonique ; `grille` = un degre de
#: cette gamme par mesure (l'accord se batit dessus en tierces). Tout ce qui
#: sonne vient donc de la gamme, par construction.
MAJEURE = (0, 2, 4, 5, 7, 9, 11)
MINEURE = (0, 2, 3, 5, 7, 8, 10)

STATIONS: list[Style] = [
    # Le camion : country-rock de grand-route, do majeur, quatre accords qui
    # tournent (I-V-vi-IV), le genre de toune qui passe a 4 h du matin.
    {"slug": "station_camion", "nom": "CB-88 La Route", "graine": 20260913,
     "bpm": 104, "tonique": 48, "gamme": MAJEURE, "grille": (0, 4, 5, 3),
     "forme_chant": "square", "forme_nappe": "triangle", "volume": 0.7},
    # La remorqueuse : blues de cour a ferraille, la mineur, lent, trois
    # accords et un balai qui traine.
    {"slug": "station_remorqueuse", "nom": "Le Lot 900 AM", "graine": 19870411,
     "bpm": 84, "tonique": 45, "gamme": MINEURE, "grille": (0, 3, 4, 0),
     "forme_chant": "sawtooth", "forme_nappe": "sine", "volume": 0.62},
]

#: Huit mesures de grille (la grille de quatre, jouee deux fois) et seize de
#: chant : la boucle dure assez pour qu'on ne l'entende pas se mordre la queue
#: le temps d'une course.
STATION_MESURES = 16


def _hauteur(style: Style, degre: int) -> int:
    """Le degre `degre` de la gamme (negatif = en dessous de la tonique)."""
    octave, index = divmod(degre, len(style["gamme"]))
    return style["tonique"] + 12 * octave + style["gamme"][index]


def generer_station(style: Style, station: bool = True) -> Morceau:
    """Un morceau complet a partir d'une graine. Deux appels donnent le meme.

    `station` : une RADIO (le bouton d'un char peut tomber dessus) ou une
    AMBIANCE (le chef d'orchestre la choisit, jamais le bouton radio)."""
    des = _Des(style["graine"])
    grille = style["grille"]
    basse: list[list[float]] = []
    nappe: list[list[float]] = []
    chant: list[list[float]] = []
    for mesure in range(STATION_MESURES):
        depart = mesure * PAS_PAR_MESURE
        racine = grille[mesure % len(grille)]
        # La basse marche : la fondamentale sur le 1 et le 3, la quinte entre.
        for temps, degre in enumerate((racine, racine + 4, racine, racine + 2)):
            basse.append([depart + temps * PAS_PAR_TEMPS, _hauteur(style, degre - 7),
                          PAS_PAR_TEMPS])
        # L'accord, en tierces de la gamme : jamais une note etrangere.
        for attaque in (0, 4):
            for degre in (racine, racine + 2, racine + 4):
                nappe.append([depart + attaque, _hauteur(style, degre), 3])
        # Le chant : quatre a six notes tirees dans l'accord et ses voisines.
        for _ in range(des.entier(4, 6)):
            pas = des.entier(0, PAS_PAR_MESURE - 1)
            degre = racine + des.choix((7, 9, 11, 8, 10, 12))
            duree = des.choix((1, 1, 2, 2, 3))
            volume = 1.0 if des.chance(0.7) else 0.6
            chant.append([depart + pas, _hauteur(style, degre), duree, volume])
    chant.sort(key=lambda n: (n[0], n[1]))
    # La batterie tourne sur une mesure : grosse caisse sur les temps forts,
    # caisse claire sur le contretemps, et un charleston tire au sort.
    batterie: list[list[float]] = [[0, 1800, 1, 1.0], [2, 5200, 1, 0.9],
                                   [4, 1800, 1, 0.8], [6, 5200, 1, 1.0]]
    for pas in range(PAS_PAR_MESURE):
        if des.chance(0.5):
            batterie.append([pas, 9000, 1, 0.25])
    batterie.sort(key=lambda n: (n[0], n[1]))
    return {
        "slug": style["slug"],
        "nom": style["nom"],
        # ⚠️ `station` distingue une RADIO d'un theme : le menu joue `titre`,
        # le bouton RADIO d'un char ne doit jamais tomber dessus. C'est Python
        # qui le dit — le navigateur n'a pas a reconnaitre une station a son
        # slug.
        "station": station,
        "bpm": style["bpm"],
        "pas_par_temps": PAS_PAR_TEMPS,
        "pas": STATION_MESURES * PAS_PAR_MESURE,
        "volume": style["volume"],
        "voix": [
            {"role": "basse", "forme": "triangle", "volume": 0.40,
             "motif": len(grille) * PAS_PAR_MESURE, "notes": basse[:len(grille) * 4]},
            {"role": "nappe", "forme": style["forme_nappe"], "volume": 0.11,
             "motif": len(grille) * PAS_PAR_MESURE, "notes": nappe[:len(grille) * 6]},
            {"role": "chant", "forme": style["forme_chant"], "volume": 0.13, "notes": chant},
            {"role": "batterie", "forme": "bruit", "volume": 0.09,
             "motif": PAS_PAR_MESURE, "notes": batterie},
        ],
    }


# --- Les cinq pieces du musicien de rue -------------------------------------

#: ⚠️ Demande de Martin : « je veux que le musicien fasse vraiment de la
#: musique, 5 musiques differentes ». La fiche « des sortes de gens » le
#: promettait deja — « il joue, et CA S'ENTEND » — et ce qui a ete livre est un
#: corps avec une guitare dessinee dessus et ZERO note. Le jeu a un sequenceur,
#: dix morceaux ecrits en notes et un chef d'orchestre ; l'homme a la guitare
#: est muet depuis le premier jour.
#:
#: ⚠️ DEUX VOIX, PAS QUATRE. Une station de radio a une basse, une nappe, un
#: chant et une batterie — c'est un groupe dans un studio. Un gars tout seul sur
#: un trottoir a SIX CORDES : il gratte un accord de la main droite et chante la
#: melodie par-dessus. `generer_rue` ne produit donc que l'accompagnement et le
#: chant, et le morceau sonne comme ce qu'on voit.
#:
#: `mesure` : combien de croches dans une mesure. C'est ce qui donne la VALSE —
#: six croches au lieu de huit, trois temps au lieu de quatre. Aucune autre
#: musique du jeu n'est a trois temps, et c'est ce qui la fait reconnaitre en
#: deux secondes.
class StyleRue(TypedDict):
    slug: str
    nom: str
    graine: int
    bpm: int
    tonique: int
    gamme: tuple[int, ...]
    grille: tuple[int, ...]
    mesure: int
    forme_chant: str
    forme_gratte: str
    volume: float


#: ⚠️ CINQ TONALITES, CINQ TEMPOS, CINQ GRILLES. Deux pieces qui partagent
#: l'un des trois se ressemblent assez pour que le joueur croie en entendre une
#: seule — et cinq morceaux qu'on prend pour un seul, c'est quatre morceaux
#: payes pour rien. Un juge le verifie.
RUE: list[StyleRue] = [
    # La plainte du gars qui joue pour manger : mineure, lente, quatre accords
    # qui tournent sans jamais se resoudre.
    {"slug": "rue_complainte", "nom": "La complainte du Faubourg", "graine": 19610223,
     "bpm": 76, "tonique": 52, "gamme": MINEURE, "grille": (0, 5, 3, 4), "mesure": 8,
     "forme_chant": "triangle", "forme_gratte": "sine", "volume": 0.52},
    # Le reel : majeure, vite, et ca tape du pied. La seule des cinq ou la
    # melodie court en croches — c'est ce qui fait un reel.
    {"slug": "rue_reel", "nom": "Le reel du trottoir", "graine": 19340708,
     "bpm": 132, "tonique": 55, "gamme": MAJEURE, "grille": (0, 0, 4, 0), "mesure": 8,
     "forme_chant": "square", "forme_gratte": "triangle", "volume": 0.48},
    # Le blues du coin : douze mesures, la vraie grille (I-I-I-I IV-IV-I-I
    # V-IV-I-V). ⚠️ C'est la SEULE du jeu a ne pas tourner sur quatre mesures,
    # et c'est ce qui l'empeche de sonner comme les quatre autres.
    {"slug": "rue_blues", "nom": "Le blues du coin", "graine": 19490915,
     "bpm": 92, "tonique": 45, "gamme": MINEURE,
     "grille": (0, 0, 0, 0, 3, 3, 0, 0, 4, 3, 0, 4), "mesure": 8,
     "forme_chant": "sawtooth", "forme_gratte": "triangle", "volume": 0.5},
    # ⚠️ LA SEULE A TROIS TEMPS DE TOUT LE JEU (`mesure: 6`). Six croches par
    # mesure : la basse sur le 1, deux grattes sur le 2 et le 3. Un joueur qui
    # ne connait rien a la musique entend qu'elle n'est pas comme les autres.
    {"slug": "rue_valse", "nom": "La valse de la Baie", "graine": 19271104,
     "bpm": 116, "tonique": 50, "gamme": MAJEURE, "grille": (0, 4, 5, 4), "mesure": 6,
     "forme_chant": "sine", "forme_gratte": "triangle", "volume": 0.5},
    # La ballade : la plus lente, la plus haute, et presque rien dedans — c'est
    # celle qu'on entend d'un coin de rue sans savoir d'ou elle vient.
    {"slug": "rue_ballade", "nom": "La ballade des brumes", "graine": 20050612,
     "bpm": 68, "tonique": 57, "gamme": MINEURE, "grille": (0, 6, 3, 5), "mesure": 8,
     "forme_chant": "sine", "forme_gratte": "sine", "volume": 0.46},
]

#: Combien de temps la boucle doit tenir avant de se mordre la queue, en
#: secondes. ⚠️ CE N'EST PAS UN NOMBRE DE TOURS, et c'est la difference qui
#: compte : a deux tours fixes, le reel (132 a la noire) bouclait en 14 s et la
#: valse en 12 — on s'arrete devant un musicien plus longtemps que ca, et on
#: l'entend recommencer. Le nombre de tours se CALCULE donc a partir du tempo.
RUE_SECONDES_MIN = 24
#: ⚠️ Deux tours au moins, meme pour le blues qui dure deja une minute : c'est
#: le deuxieme tour qui porte une AUTRE melodie sur la meme grille. Sans lui, on
#: entend la melodie tourner deux fois plus souvent que les accords.
RUE_TOURS_MIN = 2


def generer_rue(style: StyleRue) -> Morceau:
    """Une piece de rue : une gratte et une melodie, rien d'autre.

    Deux appels sur la meme graine donnent la meme piece — c'est ce qui permet
    de la corriger, et c'est ce qui garde l'ETag du paquet stable.
    """
    des = _Des(style["graine"])
    grille = style["grille"]
    mesure = style["mesure"]
    pas_grille = len(grille) * mesure
    tour_s = pas_grille * 60.0 / style["bpm"] / PAS_PAR_TEMPS
    tours = max(RUE_TOURS_MIN, math.ceil(RUE_SECONDES_MIN / tour_s))
    gratte: list[list[float]] = []
    chant: list[list[float]] = []
    for m, racine in enumerate(grille):
        depart = m * mesure
        # LA GRATTE. ⚠️ Un accord plaque sur chaque temps, pas une basse qui
        # marche : une main droite sur six cordes ne fait pas de walking bass.
        # La fondamentale en bas, la tierce et la quinte au-dessus.
        temps = [0, 2, 4] if mesure == 6 else [0, 2, 4, 6]
        for i, t in enumerate(temps):
            # Le 1 est plein (trois notes), les autres sont plus legers : c'est
            # ce qui fait entendre le DEBUT de la mesure, donc la mesure.
            degres = (racine - 7, racine - 3, racine) if i == 0 else (racine - 3, racine)
            for degre in degres:
                gratte.append([depart + t, _hauteur(style, degre), 2 if i == 0 else 1,
                               1.0 if i == 0 else 0.7])
    # LA MELODIE, sur les deux tours : elle ne se repete pas, sinon on entend la
    # boucle deux fois plus souvent que la grille.
    for tour in range(tours):
        for m, racine in enumerate(grille):
            depart = (tour * len(grille) + m) * mesure
            combien = des.entier(3, 5) if mesure == 8 else des.entier(2, 3)
            occupe: set[int] = set()
            for _ in range(combien):
                pas = des.entier(0, mesure - 1)
                if pas in occupe:
                    continue
                occupe.add(pas)
                # Les notes de l'accord, plus ses voisines : tout sort de la
                # gamme par construction, une fausse note est impossible.
                degre = racine + des.choix((7, 9, 11, 7, 8, 10, 12))
                duree = des.choix((1, 2, 2, 3))
                chant.append([depart + pas, _hauteur(style, degre), duree,
                              1.0 if des.chance(0.65) else 0.65])
    chant.sort(key=lambda n: (n[0], n[1]))
    # ⚠️ On raccourcit les notes qui se mordent : un oscillateur par note, deux
    # notes qui se recouvrent dans la MEME voix sonnent comme un accord qu'on
    # n'a pas ecrit (le juge du theme le refuse depuis le premier jour).
    for avant, apres in zip(chant, chant[1:]):
        avant[2] = min(avant[2], apres[0] - avant[0])
    chant = [n for n in chant if n[2] > 0]
    return {
        "slug": style["slug"],
        "nom": style["nom"],
        # ⚠️ Pas une station : le bouton RADIO d'un char ne doit jamais tomber
        # sur le gars du trottoir.
        "station": False,
        "bpm": style["bpm"],
        "pas_par_temps": PAS_PAR_TEMPS,
        "pas": tours * pas_grille,
        "volume": style["volume"],
        "voix": [
            {"role": "gratte", "forme": style["forme_gratte"], "volume": 0.16,
             "motif": pas_grille, "notes": gratte},
            {"role": "chant", "forme": style["forme_chant"], "volume": 0.15, "notes": chant},
        ],
    }


def rues() -> list[Morceau]:
    """Les cinq pieces du musicien de rue."""
    return [generer_rue(style) for style in RUE]


def rue_par_slug(slug: str) -> Morceau | None:
    for style in RUE + [ORGUE]:
        if style["slug"] == slug:
            return generer_rue(style)
    return None


# --- L'orgue de la foire ----------------------------------------------------

#: ⚠️ **UNE MUSIQUE QUI SORT D'UN ENDROIT.** Le musicien de rue est « une
#: musique qui sort de QUELQU'UN » — son gain a lui, par-dessus l'ambiance du
#: district, sans prendre le rang de personne (`MUSIQUE.rue_sous_etat`). L'orgue
#: de la foire est le MEME code avec une source FIXE : le milieu de l'allee. Et
#: surtout pas une ambiance de district de plus — une ambiance se joue PARTOUT
#: dans son district, et la foire tient dans 52 x 31 tuiles de La Pointe.
#:
#: ⚠️ Il passe donc par `generer_rue` et non par `generer_station` : ce qu'il
#: faut ici, c'est une VALSE (`mesure: 6`, trois temps), et le generateur de
#: stations ne sait compter qu'en quatre. Deux voix : la basse-accords de la
#: main gauche (l'oum-pa-pa d'un limonaire) et la ritournelle par-dessus.
#:
#: ⚠️ MAJEURE, HAUTE ET VITE — le contraire des cinq pieces de rue, dont quatre
#: sont mineures et lentes. Un orgue de manège qui sonne comme le gars a la
#: guitare du Faubourg, c'est une foire qu'on n'entend pas arriver.
ORGUE: StyleRue = {
    "slug": "foire_orgue", "nom": "L'orgue de la foire", "graine": 19230601,
    "bpm": 150, "tonique": 62, "gamme": MAJEURE, "grille": (0, 4, 0, 4, 3, 4, 0, 0),
    "mesure": 6, "forme_chant": "square", "forme_gratte": "triangle", "volume": 0.55,
}


def orgue() -> Morceau:
    """La ritournelle de la foire, en notes — le filet, comme partout : si le
    mp3 n'est pas la, le sequenceur la joue telle qu'elle est ecrite ici."""
    return generer_rue(ORGUE)


#: --- La musique qui dit ou tu es et ce qui t'arrive -------------------------
#:
#: ⚠️ ECRITES EN NOTES, comme le theme du menu et les stations du camion — et
#: pour la meme raison, ecrite noir sur blanc dans ce fichier depuis le premier
#: jour : « le jour ou Martin veut une vraie piece jouee par de vrais
#: instruments, elle se posera PAR-DESSUS comme les radios ». Huit pistes de
#: 60 s a 64 kbit/s pesent 4 Mo, autant que tout le dossier audio ; en notes,
#: elles pesent quelques kilo-octets et ne coutent aucun credit. Le jour ou un
#: mp3 arrive, il se pose dessus et celles-ci redeviennent le filet.
#:
#: Un district = une ambiance, et c'est LA MUSIQUE qui connait les districts,
#: pas l'inverse : `carte.py` n'a pas a savoir ce qu'on entend.
#: **LA MUSIQUE DES COMMERCES** (demande de Martin, 16 sept. 2026 : « nouvelle
#: musique pour quand on entre dans les commerces, des chansons différentes,
#: contextuelles »).
#:
#: ⚠️ **C'EST LE LIEU QUI CHOISIT, PAS LE HASARD.** Entrer chez l'armurier et
#: entrer dans une boutique de linge ne se ressemblent pas ; une seule musique
#: « d'interieur » aurait ete un rideau tire sur seize pieces differentes. Quatre
#: morceaux, et une fiche qui dit lequel joue ou — le navigateur lit, il ne
#: devine pas.
#:
#: ⚠️ **45 s comme les autres.** J'avais d'abord ecrit 20 s pour tenir sous un
#: plafond de 6 Mo ; Martin a tranche — ce plafond-la etait le NOTRE, pas celui
#: du telephone. Les musiques ne se telechargent qu'a l'entree de la piece,
#: jamais au demarrage : la seule chose qu'un plafond serre y gagnait, c'etait
#: une boucle de 20 s qu'on entend reboucler.
#:
#: ⚠️ Et comme tout le reste : **le fichier d'abord, les notes en filet**. Chaque
#: morceau a sa graine, donc sa version sequencee ; un mp3 manquant ne fait pas
#: un silence.
COMMERCES: list[Style] = [
    # Chez Gus, l'armurier. Sourd, tendu, presque immobile : on n'entre pas
    # acheter un fusil sur une valse.
    {"slug": "com_armurerie", "nom": "Le comptoir de Gus", "graine": 19680412,
     "bpm": 72, "tonique": 40, "gamme": MINEURE, "grille": (0, 0, 5, 5),
     "forme_chant": "triangle", "forme_nappe": "sawtooth", "volume": 0.30},
    # Boutique Rosa. Leger, clair, un peu chic — la radio du magasin.
    {"slug": "com_boutique", "nom": "Boutique Rosa", "graine": 19730921,
     "bpm": 104, "tonique": 57, "gamme": MAJEURE, "grille": (0, 3, 4, 3),
     "forme_chant": "sine", "forme_nappe": "triangle", "volume": 0.32},
    # Le casse-croute : le jukebox dans le coin, chaud et un peu use.
    {"slug": "com_casse_croute", "nom": "Le jukebox du coin", "graine": 19591225,
     "bpm": 96, "tonique": 52, "gamme": MAJEURE, "grille": (0, 5, 3, 4),
     "forme_chant": "square", "forme_nappe": "sine", "volume": 0.33},
    # Le garage de Rocco : le rock graisseux qui sort d'un poste tache de
    # peinture, au fond de l'atelier.
    {"slug": "com_garage", "nom": "Le poste de l'atelier", "graine": 19810307,
     "bpm": 118, "tonique": 45, "gamme": MINEURE, "grille": (0, 0, 3, 4),
     "forme_chant": "sawtooth", "forme_nappe": "square", "volume": 0.31},
]

#: Quel morceau joue dans quelle piece. ⚠️ **Une piece sans entree ici reste
#: SILENCIEUSE**, et c'est voulu : le poste de police, l'hopital et la planque ne
#: sont pas des commerces — on n'y met pas de musique d'ambiance, et le silence
#: y dit quelque chose qu'aucune toune ne dirait. La chambre d'hotel non plus :
#: c'est la qu'on sauvegarde, et le calme y a un sens.
MUSIQUES_DE_COMMERCE: dict[str, str] = {
    "armurerie": "com_armurerie",
    "usine": "com_armurerie",
    "vetements": "com_boutique",
    "electronique": "com_boutique",
    "kiosque": "com_boutique",
    "casse_croute": "com_casse_croute",
    "cantine": "com_casse_croute",
    "depanneur": "com_casse_croute",
    "garage": "com_garage",
}


def commerces() -> list[Morceau]:
    """Les quatre musiques d'interieur, en notes. ⚠️ `station=False` : le bouton
    RADIO d'un char ne doit jamais tomber sur la toune d'une boutique."""
    return [generer_station(style, station=False) for style in COMMERCES]


AMBIANCES_DE_DISTRICT: dict[str, str] = {
    "faubourg": "amb_faubourg",
    "erables": "amb_erables",
    "shop": "amb_shop",
    "quais": "amb_quais",
    "pointe": "amb_pointe",
    "baie": "amb_quais",        # l'eau : la meme corne que le port
    # ⚠️ L'ile EMPRUNTE le vent de La Pointe, et ca s'entend : c'est le choix
    # d'une premiere vague, pas une musique a elle (trente credits la seconde).
    "ile": "amb_pointe",
}

AMBIANCES: list[Style] = [
    # Le Faubourg : la brume et le piano. Mineure, lente, peu de notes.
    {"slug": "amb_faubourg", "nom": "Brume sur le Faubourg", "graine": 20260914,
     "bpm": 68, "tonique": 45, "gamme": MINEURE, "grille": (0, 5, 3, 4),
     "forme_chant": "sine", "forme_nappe": "triangle", "volume": 0.34},
    # Les Erables : le calme plat. Majeure, douce, presque rien.
    {"slug": "amb_erables", "nom": "Dimanche aux Érables", "graine": 19920604,
     "bpm": 74, "tonique": 50, "gamme": MAJEURE, "grille": (0, 3, 4, 0),
     "forme_chant": "triangle", "forme_nappe": "sine", "volume": 0.28},
    # La Shop : le fer et le vide. Mineure, basse, dure.
    {"slug": "amb_shop", "nom": "Fer et vide", "graine": 19771102,
     "bpm": 88, "tonique": 38, "gamme": MINEURE, "grille": (0, 0, 5, 4),
     "forme_chant": "square", "forme_nappe": "sawtooth", "volume": 0.30},
    # Les Quais : la corne et les mouettes. Mineure large, lente.
    {"slug": "amb_quais", "nom": "La corne des Quais", "graine": 19840317,
     "bpm": 64, "tonique": 41, "gamme": MINEURE, "grille": (0, 4, 5, 3),
     "forme_chant": "sine", "forme_nappe": "triangle", "volume": 0.32},
    # La Pointe : le vent et les arbres. Majeure aeree.
    {"slug": "amb_pointe", "nom": "Le vent de La Pointe", "graine": 20011225,
     "bpm": 80, "tonique": 52, "gamme": MAJEURE, "grille": (0, 5, 3, 4),
     "forme_chant": "triangle", "forme_nappe": "sine", "volume": 0.30},
    # ⚠️ Les deux musiques d'ETAT : elles couvrent l'ambiance, jamais l'inverse
    # (voir `ECHELLE`). Rapides, mineures, et plus fortes — c'est le seul
    # moment ou la musique a le droit de prendre toute la place.
    {"slug": "mus_poursuite", "nom": "Ils arrivent", "graine": 19990911,
     "bpm": 148, "tonique": 40, "gamme": MINEURE, "grille": (0, 0, 4, 4),
     "forme_chant": "square", "forme_nappe": "sawtooth", "volume": 0.46},
    {"slug": "mus_bagarre", "nom": "Corps a corps", "graine": 20080215,
     "bpm": 132, "tonique": 43, "gamme": MINEURE, "grille": (0, 5, 0, 3),
     "forme_chant": "sawtooth", "forme_nappe": "square", "volume": 0.42},
]

#: ⚠️ QUI GAGNE. C'est la question qu'aucune des demandes ne pose et dont tout
#: depend : il y a deja de la radio dans un char, l'ambiance a pied, la rumeur
#: de la foule, les sirenes et les voix. L'echelle est ECRITE UNE FOIS, ici,
#: et le navigateur la lit — il n'invente pas sa priorite.
#:
#: Le plus petit gagne. La rumeur de la foule passe dessous, toujours.
ECHELLE: dict[str, int] = {
    "histoire": 1,     # une replique : elle baisse deja tout le reste
    "poursuite": 2,
    "bagarre": 3,
    "ambiance": 4,     # la radio du char ou le district
}

#: ⚠️ Une musique d'ETAT a besoin d'une QUEUE. Les etoiles montent et
#: descendent, une bagarre s'arrete et reprend : sans duree minimale ni fondu,
#: la poursuite demarrerait et s'arreterait trois fois en dix secondes. Elle
#: continue quelques secondes apres la derniere etoile perdue — c'est ce qui
#: fait qu'on SOUFFLE.
#:
#: `hysteresis_px` : on traverse une frontiere en zigzag sur un boulevard, et
#: une musique qui bascule a chaque pas de cote est pire que pas de musique.
MUSIQUE = {
    "poursuite_etoiles": 2,     # une etoile, c'est un temoin qui a appele
    "poursuite_queue_s": 7,
    "bagarre_queue_s": 5,
    # ⚠️ LE FONDU ENCHAINE EST LA REGLE (Martin, 20 sept. 2026) : « les
    # transitions de musique doivent toujours se faire en crossover, a moins que
    # ce soit necessaire pour l'effet et l'ambiance ». Toute musique qui en
    # remplace une — ou qui s'eteint — le fait sur `fondu_s` secondes, l'ancienne
    # qui baisse pendant que la nouvelle monte, a puissance constante.
    #
    # `fondu_vif_s` : la SEULE exception de duree. Quand la musique d'ETAT
    # arrive (la poursuite, la bagarre), deux secondes de montee feraient
    # entendre le danger APRES l'avoir vu ; elle entre donc vite, mais elle
    # entre encore en fondu — et le musicien de rue, lui, s'eclipse ou change de
    # toune sur cette duree-la. Une coupure franche, c'est autre chose : elle
    # se demande a l'appel (`Mus.jouer(slug, 0)`) et se justifie a cet endroit.
    "fondu_s": 2,
    "fondu_vif_s": 0.7,
    "hysteresis_px": 96,        # six tuiles a franchir avant de changer de piste
    # ⚠️ LE MUSICIEN DE RUE N'EST PAS DANS L'ECHELLE, et c'est voulu : ce n'est
    # pas une piste, c'est un SON DU MONDE — il sort d'un gars qu'on voit, comme
    # un moteur sort d'un char. Il joue donc PAR-DESSUS l'ambiance du district,
    # et son volume vient de la distance, pas d'un rang.
    #
    # Mais il se tasse quand la musique d'ETAT prend toute la place : quand la
    # police te court apres, la toune du guitariste n'a plus d'importance. C'est
    # la seule regle de priorite dont il a besoin, et elle est ecrite ici comme
    # les autres.
    "rue_sous_etat": 0.25,
}


def ambiances() -> list[Morceau]:
    """Les cinq districts et les deux etats, en notes. ⚠️ `station=False` : le
    bouton RADIO d'un char ne doit jamais tomber dessus."""
    return [generer_station(style, station=False) for style in AMBIANCES]


def stations() -> list[Morceau]:
    return [generer_station(style) for style in STATIONS]
