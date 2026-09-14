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

MORCEAUX: list[Morceau] = [
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
    for morceau in MORCEAUX:
        if morceau["slug"] == slug:
            return morceau
    return None


def duree_s(morceau: Morceau) -> float:
    """La longueur de la boucle, en secondes."""
    return morceau["pas"] * 60.0 / morceau["bpm"] / morceau["pas_par_temps"]


def exporter() -> list[Morceau]:
    return [dict(m) for m in MORCEAUX] + stations()  # type: ignore[misc]


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


def generer_station(style: Style) -> Morceau:
    """Un morceau complet a partir d'une graine. Deux appels donnent le meme."""
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
        "station": True,
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


def stations() -> list[Morceau]:
    return [generer_station(style) for style in STATIONS]
