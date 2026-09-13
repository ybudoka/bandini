"""Le parc automobile de Baie-des-Brumes — source unique des stats.

Le navigateur ne connait aucune de ces valeurs : il recoit ce catalogue et
conduit avec. Les unites sont celles du moteur : pixels par image (60 images
par seconde), radians par image pour le braquage, points de vie.

`phase` : 1 = present dans la premiere version (le navigateur a son sprite),
2 = vague suivante. Un test verifie que chaque vehicule de phase 1 a un sprite.

Depuis M9, une fiche porte aussi ce que le char SAIT FAIRE, et le navigateur
n'a pas a le deviner de son slug :

    cercles   la chaine de cercles qui le represente (3 par defaut)
    defonce   0 = rien ; sinon la fraction de vitesse gardee en cassant un
              obstacle bas (cloture, borne-fontaine, poubelle)
    soigne    PV par seconde rendus a qui le conduit (l'ambulance)
    crochet   il peut trainer un autre char — un seul a la fois
    boulot    le boulot qu'on prend au klaxon (`taxi`, `pizza`, `ambulance`,
              `remorquage`), sur le patron du taxi de la v1
"""

from __future__ import annotations

from typing import TypedDict


class Vehicule(TypedDict):
    slug: str
    nom: str
    classe: str
    longueur: int
    largeur: int
    vitesse_max: float
    vitesse_recul: float
    acceleration: float
    frein: float
    friction: float
    braquage: float
    adherence: float
    adherence_frein: float
    masse: float
    vie: int
    places: int
    prix: int
    frequence: float
    couleurs: list[str]
    sprite: str
    police: bool
    sirene: bool
    alarme: bool
    ejecte: bool
    eau: bool
    cercles: int
    defonce: float
    soigne: float
    crochet: bool
    boulot: str | None
    radio: str | None
    phase: int


def _v(slug, nom, classe, lon, lat, vmax, accel, braquage, vie, places, prix, freq, couleurs,
       sprite, *, police=False, sirene=False, alarme=False, ejecte=False, eau=False,
       masse=1.0, cercles=3, defonce=0.0, soigne=0.0, crochet=False, boulot=None,
       radio=None, phase=1) -> Vehicule:
    return Vehicule(
        slug=slug, nom=nom, classe=classe, longueur=lon, largeur=lat,
        vitesse_max=vmax, vitesse_recul=round(vmax * 0.33, 2), acceleration=accel,
        frein=round(accel * 2, 3), friction=0.995 if eau else 0.985,
        braquage=braquage, adherence=0.12 if not eau else 0.05, adherence_frein=0.035,
        masse=masse, vie=vie, places=places, prix=prix, frequence=freq,
        couleurs=couleurs, sprite=sprite, police=police, sirene=sirene, alarme=alarme,
        ejecte=ejecte, eau=eau, cercles=cercles, defonce=defonce, soigne=soigne,
        crochet=crochet, boulot=boulot, radio=radio, phase=phase,
    )


#: ⚠️ L'auto est la reference (vitesse 100 %). Les prix sont ceux du garage
#: clandestin de Ti-Guy pour un vehicule PROPRE ; la revente d'un vehicule vole
#: rapporte `economie.VENTE_FRACTION` de ce prix.
CATALOGUE: list[Vehicule] = [
    _v("auto", "Berline", "auto", 28, 14, 4.0, 0.06, 0.045, 100, 4, 600, 0.40,
       ["#c0392b", "#2c3e50", "#ecf0f1", "#27ae60", "#8e44ad", "#d35400"], "auto",
       alarme=False, radio="la_brume"),
    _v("taxi", "Taxi", "auto", 28, 14, 3.8, 0.058, 0.047, 110, 4, 700, 0.12,
       ["#f1c40f"], "taxi", boulot="taxi", radio="taxi_radio"),
    # ⚠️ La pizza se livre en moto, et c'est ce qui fait le boulot : le char le
    # plus rapide du jeu est aussi celui dont on tombe au premier choc.
    _v("moto", "Moto", "moto", 20, 8, 5.2, 0.09, 0.07, 40, 2, 450, 0.15,
       ["#1a1a1a", "#c0392b", "#2980b9"], "moto", ejecte=True, boulot="pizza",
       radio="le_choc"),
    # ⚠️ Le velo est un vehicule comme un autre : il suit la rue, on peut le
    # prendre a son cycliste (qui temoigne), on en tombe au premier choc.
    _v("velo", "Vélo", "velo", 16, 8, 2.0, 0.05, 0.085, 30, 1, 120, 0.18,
       ["#2980b9", "#c0392b", "#27ae60", "#f1c40f"], "velo", ejecte=True),
    _v("police", "Auto-patrouille", "auto", 28, 14, 4.4, 0.07, 0.05, 150, 4, 2500, 0.0,
       ["#ffffff"], "police", police=True, sirene=True, alarme=True, radio="dix_quatre"),
    # --- M9, le parc automobile ------------------------------------------
    # ⚠️ `cercles` n'est pas un reglage de confort : la chaine doit COUVRIR la
    # carrosserie, sinon deux cercles voisins laissent un trou par lequel une
    # moto entre dans l'autobus. Il en faut au moins `longueur / largeur`
    # (juge `test_la_chaine_de_cercles_ne_laisse_aucun_trou`) — d'ou les cinq
    # de l'autobus, « deux de plus » que les trois de tout le monde.
    _v("camion", "Camion", "camion", 40, 16, 2.8, 0.03, 0.03, 300, 2, 1200, 0.08,
       ["#7f8c8d", "#c0392b", "#2c3e50"], "camion", masse=3.0, cercles=4,
       defonce=0.75, radio="station_camion"),
    _v("autobus", "Autobus", "camion", 48, 16, 2.6, 0.028, 0.025, 250, 12, 1500, 0.04,
       ["#2980b9"], "autobus", masse=3.2, cercles=5, defonce=0.7),
    # ⚠️ L'ambulance SOIGNE (2 PV par seconde au volant) — elle ne ressuscite
    # personne : un blesse mort reste mort, et le boulot est perdu.
    _v("ambulance", "Ambulance", "auto", 32, 15, 3.6, 0.05, 0.04, 180, 3, 1400, 0.04,
       ["#ffffff"], "ambulance", sirene=True, alarme=True, masse=1.4, soigne=2.0,
       boulot="ambulance"),
    _v("remorqueuse", "Remorqueuse", "camion", 36, 15, 3.0, 0.04, 0.035, 220, 2, 1300, 0.05,
       ["#d98324", "#2c3e50", "#7f8c8d"], "remorqueuse", masse=2.2, cercles=4,
       defonce=0.6, crochet=True, boulot="remorquage", radio="station_remorqueuse"),
    # ⚠️ Le bateau reste en phase 2 : il demande une physique a part (l'eau n'a
    # ni voie ni trottoir) et des quais ou embarquer. Le plan le dit lui-meme —
    # « s'il coute plus qu'il ne donne, il tombe en v3 » — et le traversier de
    # M12 suffit a l'eau. Il garde donc sa fiche, sans sprite et sans trafic.
    _v("bateau", "Chaloupe", "bateau", 30, 12, 3.2, 0.02, 0.025, 120, 4, 2000, 0.05,
       ["#ecf0f1", "#2c3e50"], "bateau", eau=True, cercles=3, phase=2),
]

CLASSES = ("auto", "moto", "velo", "camion", "bateau")

#: Le trafic : combien de chars vivent dans la bulle du joueur, et comment un
#: conducteur regarde devant lui. Les feux durent en images (60 par seconde).
TRAFIC = {
    "vehicules_max": 9,           # en circulation, dans la bulle
    "stationnes_max": 6,          # a l'arret sur les stationnements
    "regard_tuiles": 4,           # a quelle distance un conducteur regarde devant
    "distance_securite_px": 34,   # plus pres que ca, il freine
    "vitesse_ville": 0.55,        # fraction de la vitesse max en circulation
    "depassement_tuiles": 5,      # la voie d'a cote doit etre libre sur ce tant
    "depassement_images": 90,     # apres un deport, on ne se redeporte pas avant
    "patience_images": 200,       # bloque plus longtemps : il force le passage
    "arret_images": 45,           # au STOP : on s'immobilise ce temps-la
    "priorite_pieton_px": 70,     # un pieton engage sur le passage : on attend
    "feu_vert_images": 420,
    "feu_orange_images": 60,
    "naissance_px": 300,          # comme les pietons : hors ecran, dans la bulle
    "oubli_px": 560,
}

#: Ce qui arrive quand un char touche quelque chose. ⚠️ Les degats se
#: calculent sur la VITESSE RELATIVE : un choc a 4 px/image contre un mur fait
#: aussi mal que deux chars a 2 px/image l'un contre l'autre.
PHYSIQUE = {
    "sous_pas_px": 3.0,           # au-dessus, on decoupe le deplacement
    "cercles": 3,                 # la chaine de cercles qui represente un char
    "choc_vitesse_min": 1.0,      # sous ca, un contact n'est pas un choc
    "choc_degats_par_px": 7,
    "choc_rebond": 0.35,
    "renverse_vitesse_min": 1.2,  # sous ca, un pieton est bouscule, pas renverse
    "renverse_degats_par_px": 28,
    "fumee_sous": 0.5,            # fraction des PV
    "feu_sous": 0.2,
    "feu_degats_par_seconde": 4,
    "explosion_rayon_px": 60,
    "explosion_degats": 90,
    "epave_secondes": 40,
    "alarme_secondes": 12,
    "ejection_vitesse_min": 2.6,  # moto : au-dessus, le choc ejecte le pilote
    "rampe_impulsion": 0.42,      # vz = vitesse * ca en sortant d'une rampe
    "gravite": 0.18,
    "portee_monter_px": 30,       # a quelle distance on peut ouvrir une portiere
    # ⚠️ Ce qu'un lourd defonce : les obstacles BAS (cloture, borne-fontaine,
    # poubelle, caisse) et eux seuls. Jamais une facade : la ville tient par
    # ses murs — les juges de connexite, les interieurs et les devantures en
    # dependent, et un trou dans un mur ouvrirait sur un toit. Le `defonce` de
    # la fiche dit ce qu'il RESTE de vitesse une fois passe au travers.
    "defonce_vitesse_min": 1.4,
    "defonce_degats": 6,          # ce que la carrosserie y laisse
    # Le crochet de la remorqueuse : a quelle distance on accroche, et a
    # quelle longueur le cable tient le char remorque.
    "crochet_portee_px": 46,
    "crochet_cable_px": 30,
    "crochet_raideur": 0.35,
}


def exporter_conduite() -> dict:
    return {"trafic": dict(TRAFIC), "physique": dict(PHYSIQUE)}


def par_slug(slug: str) -> Vehicule | None:
    for vehicule in CATALOGUE:
        if vehicule["slug"] == slug:
            return vehicule
    return None


def de_phase(phase: int) -> list[Vehicule]:
    return [v for v in CATALOGUE if v["phase"] <= phase]
