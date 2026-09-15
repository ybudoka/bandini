"""Le parc automobile de Baie-des-Brumes — source unique des stats.

Le navigateur ne connait aucune de ces valeurs : il recoit ce catalogue et
conduit avec. Les unites sont celles du moteur : pixels par image (60 images
par seconde), radians par image pour le braquage, points de vie.

`phase` : 1 = present dans la premiere version (le navigateur a son sprite),
2 = vague suivante. Un test verifie que chaque vehicule de phase 1 a un sprite.

Depuis M9, une fiche porte aussi ce que le char SAIT FAIRE, et le navigateur
n'a pas a le deviner de son slug :

    cercles   la chaine de cercles qui le represente (3 par defaut)
    reservoir ce qui n'en a pas ne brule pas et n'explose pas — le velo, et
              lui seul aujourd'hui. C'est PYTHON qui le decide : le navigateur
              n'a pas a reconnaitre un velo a son slug
    defonce   0 = rien ; sinon la fraction de vitesse gardee en cassant un
              obstacle bas (cloture, borne-fontaine, poubelle)
    soigne    PV par seconde rendus a qui le conduit (l'ambulance)
    crochet   il peut trainer un autre char — un seul a la fois
    plateau   il ne se leve pas par l'avant : il MONTE EN ENTIER sur la
              remorqueuse (la moto, le velo). ⚠️ C'est ici et pas dans le JS :
              le jour ou une trottinette arrive, elle le dit elle-meme, au lieu
              qu'un `classe === 'moto'` cache quelque part decide pour elle —
              c'est la lecon de `reservoir`, `defonce` et `sirene`
    boulot    le boulot qu'on prend au klaxon (`taxi`, `pizza`, `ambulance`,
              `remorquage`), sur le patron du taxi de la v1
    rare      il ne nait QUE dans les districts qui le declarent (`rares` de
              `carte.DISTRICTS`). Un char rare qu'on croise partout n'est plus
              rare — et c'est tout ce qui fait qu'on le VEUT
    alarme_s  la duree de son alarme, en secondes ; 0 = celle de tout le monde
              (`PHYSIQUE.alarme_secondes`)
"""

from __future__ import annotations

import math
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
    reservoir: bool
    rare: bool
    alarme_s: float
    defonce: float
    soigne: float
    crochet: bool
    plateau: bool
    boulot: str | None
    radio: str | None
    phase: int
    portieres: bool
    klaxon: str


#: Les classes dont on claque la portiere. ⚠️ Une moto et un velo n'en ont
#: pas : on les enfourche — le bruit de la montee vient d'ici, pas d'un
#: `slug === 'velo'` dans le JS. La chaloupe non plus, quand elle roulera.
CLASSES_A_PORTIERES = ("auto", "camion")

#: Ce qu'un char fait entendre au bouton du klaxon : un effet de `Son.SFX`.
#: ⚠️ Le velo a une SONNETTE — demande de Martin — et c'est la fiche qui le
#: dit, pas un `slug === 'velo'` dans `vehicules.js`. Les velos du trafic
#: sonnaient deja en passant ; c'est le meme son, desormais aussi sous le
#: pouce.
AVERTISSEURS = ("klaxon", "sonnette")


def _v(slug, nom, classe, lon, lat, vmax, accel, braquage, vie, places, prix, freq, couleurs,
       sprite, *, police=False, sirene=False, alarme=False, ejecte=False, eau=False,
       masse=1.0, cercles=3, reservoir=True, defonce=0.0, soigne=0.0, crochet=False,
       plateau=False, boulot=None,
       radio=None, phase=1, klaxon="klaxon", rare=False, adherence=None, alarme_s=0.0) -> Vehicule:
    return Vehicule(
        slug=slug, nom=nom, classe=classe, longueur=lon, largeur=lat,
        vitesse_max=vmax, vitesse_recul=round(vmax * 0.33, 2), acceleration=accel,
        frein=round(accel * 2, 3), friction=0.995 if eau else 0.985,
        braquage=braquage,
        adherence=adherence if adherence is not None else (0.12 if not eau else 0.05),
        adherence_frein=0.035,
        masse=masse, vie=vie, places=places, prix=prix, frequence=freq,
        couleurs=couleurs, sprite=sprite, police=police, sirene=sirene, alarme=alarme,
        ejecte=ejecte, eau=eau, cercles=cercles, reservoir=reservoir, rare=rare, alarme_s=alarme_s,
        defonce=defonce, soigne=soigne,
        crochet=crochet, plateau=plateau, boulot=boulot, radio=radio, phase=phase,
        portieres=classe in CLASSES_A_PORTIERES, klaxon=klaxon,
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
       radio="le_choc", plateau=True),
    # ⚠️ Le velo est un vehicule comme un autre : il suit la rue, on peut le
    # prendre a son cycliste (qui temoigne), on en tombe au premier choc.
    # ⚠️ `reservoir=False` : un velo n'a pas d'essence, donc il ne brule pas et
    # n'explose pas. C'est le SEUL du catalogue dans ce cas, et c'est le seul
    # endroit ou ca se decide.
    _v("velo", "Vélo", "velo", 16, 8, 2.0, 0.05, 0.085, 30, 1, 120, 0.18,
       ["#2980b9", "#c0392b", "#27ae60", "#f1c40f"], "velo", ejecte=True, reservoir=False,
       klaxon="sonnette", plateau=True),
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
    # --- Le haut de gamme : deux chars qu'on vole EXPRES ------------------
    # ⚠️ Tout le reste du parc est utilitaire — on le prend parce qu'il sert.
    # Ces deux-la, on les prend parce qu'on les VEUT, et ils s'opposent en
    # tout : la vitesse contre l'argent, la carrosserie mince contre la
    # lourde. Deux fiches, pas dix.
    #
    # ⚠️ `rare=True` : ils ne naissent que dans les districts qui les
    # declarent. C'est la, et pas dans ces nombres, que se joue leur rarete.
    _v("sport", "Coupé sport", "auto", 26, 13, 4.8, 0.085, 0.055, 75, 2, 3200, 0.02,
       ["#c0392b", "#ecf0f1", "#f1c40f", "#16a085"], "sport",
       alarme=True, rare=True, masse=0.85,
       # L'adherence basse est TOUT le caractere du char : il part en travers
       # au frein a main la ou une berline se contente de ralentir.
       adherence=0.055),
    _v("luxe", "Berline de luxe", "auto", 32, 15, 3.6, 0.042, 0.038, 220, 4, 5200, 0.02,
       ["#101014", "#2c3e50", "#6b4b2c"], "luxe",
       alarme=True, rare=True, masse=1.8,
       # ⚠️ Elle encaisse ET elle colle a la route : elle ne recompense pas la
       # conduite, elle recompense le vol. C'est la meilleure revente du jeu,
       # et `economie.prix_vente` le fait toute seule — le prix neuf suffit.
       adherence=0.16, alarme_s=30.0),
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
    # ⚠️ LE DEGAGEMENT : le blanc du pieton s'eteint AVANT que les chars
    # repartent. Un vrai feu pieton ne s'allume pas au rouge — il laisse le
    # temps de finir la traverse. Sans ce temps-la, celui qui s'engage a la
    # derniere image se fait cueillir par le premier char du vert suivant, et
    # c'est le jeu qui a l'air injuste, pas le pieton qui a l'air imprudent.
    # Deux secondes : la traverse fait deux tuiles, on marche a 0,45 px par
    # image, il en faut 71 pour la franchir.
    "feu_pieton_degagement_images": 120,
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
    # ⚠️ LE SAUT DOIT SE VOIR. Avec 0,42 et 0,18, une berline montait de
    # 7,8 px pendant 0,31 s et une moto de 13,2 px — sur des tuiles de 16 px,
    # pour un char dessine 32 x 16. Ce n'est pas un saut, c'est une bosse :
    # « les rampes n'ont pas l'air de fonctionner », et elles fonctionnaient.
    #
    # La hauteur vaut `(vitesse * impulsion)^2 / (2 * gravite)` et la portee
    # `2 * vitesse^2 * impulsion / gravite`. Monter l'impulsion SEULE allonge
    # le vol autant qu'elle le grandit ; c'est le RAPPORT `impulsion / gravite`
    # qui tient la portee, et `impulsion` seule qui donne la hauteur. On monte
    # donc les deux : une berline grimpe maintenant de 17 px (sa propre
    # hauteur) et la moto de 29.
    "rampe_impulsion": 0.75,      # vz = vitesse * ca en sortant d'une rampe
    "gravite": 0.26,
    # ⚠️ Sous cette hauteur, on ne decolle pas du tout. Un velo a 2 px/image
    # montait de deux pixels — moins que l'epaisseur de son ombre. Un char qui
    # « saute » sans que rien ne bouge est pire qu'un char qui refuse la rampe :
    # le seuil de vitesse s'en DEDUIT (voir `saut_vitesse_min`), il ne se
    # choisit pas.
    "saut_hauteur_min": 8,
    "portee_monter_px": 30,       # a quelle distance on peut ouvrir une portiere
    # ⚠️ Ce qu'un lourd defonce : les obstacles BAS (cloture, borne-fontaine,
    # poubelle, caisse) et eux seuls. Jamais une facade : la ville tient par
    # ses murs — les juges de connexite, les interieurs et les devantures en
    # dependent, et un trou dans un mur ouvrirait sur un toit. Le `defonce` de
    # la fiche dit ce qu'il RESTE de vitesse une fois passe au travers.
    "defonce_vitesse_min": 1.4,
    "defonce_degats": 6,          # ce que la carrosserie y laisse
    # ⚠️ UNE FOURCHE, PAS UNE CORDE. Le lien etait un ressort — le char
    # remorque roulait a plat au bout d'un elastique, pointe VERS la
    # remorqueuse, et il lachait quand on l'etirait. C'est ce qui faisait
    # qu'une remorqueuse ressemblait a une auto qui en tire une autre.
    #
    # ⚠️ Un lien rigide change la reponse a la seule question qui compte : que
    # se passe-t-il quand la charge est bloquee par une tuile ? Ce n'est plus le
    # cable qui s'allonge, c'est LA REMORQUEUSE QUI NE PASSE PAS. Elle teste
    # donc les DEUX corps avant d'avancer.
    "crochet_portee_px": 46,      # a quelle distance on accroche
    "crochet_jeu_px": 2,          # ce qui reste entre les deux : presque rien
    "crochet_leve_px": 2,         # de combien l'avant monte (l'ombre reste au sol)
    "plateau_leve_px": 3,         # de combien monte ce qui charge en entier
    # ⚠️ LE GARDE-FOU (demande de Martin : « que mon vehicule ne coince plus
    # dans un mur ou un objet »). Le deplacement teste les tuiles AVANT chaque
    # pas, mais rien ne regardait ou le char EST : pousse par un autre char,
    # tourne sur place contre une facade, ou retombe d'un saut, il se retrouve
    # DANS le mur — et de la, chaque direction est bloquee, meme celle qui
    # sort. A chaque image, un char enfonce est POUSSE hors des tuiles qu'il
    # chevauche ; si ca ne suffit pas (un coin, une ruelle plus etroite que
    # lui, le milieu d'un toit), il est POSE a la place libre la plus proche,
    # cherchee par anneaux de `degagement_pas_px` jusqu'a `degagement_px`.
    # Au-dela, on ne cherche plus : six tuiles couvrent n'importe quel mur de
    # la ville, et un char pose plus loin ne serait plus « degage », il serait
    # teleporte.
    "degagement_px": 96,
    "degagement_pas_px": 2,
}


def saut_vitesse_min() -> float:
    """La vitesse en dessous de laquelle on ne decolle pas d'une rampe.

    ⚠️ Elle se CALCULE sur `saut_hauteur_min` : c'est la vitesse a partir de
    laquelle le saut atteint la hauteur qu'on a jugee visible. Le navigateur
    la recoit toute faite et n'a aucun seuil ecrit dedans — l'ancien `1.5`
    laissait sauter le velo de deux pixels.
    """
    ph = PHYSIQUE
    return round((2 * ph["gravite"] * ph["saut_hauteur_min"]) ** 0.5 / ph["rampe_impulsion"], 3)


def saut(vehicule: Vehicule, vitesse: float | None = None) -> dict:
    """La geometrie d'un saut : hauteur, duree, portee, freinage — en pixels et
    en images. Une seule source pour la physique, le generateur de ville et
    les juges ; personne ne refait le calcul dans son coin."""
    ph = PHYSIQUE
    v = vehicule["vitesse_max"] if vitesse is None else vitesse
    if v < saut_vitesse_min():
        return {"hauteur": 0.0, "duree": 0.0, "portee": 0.0,
                "freinage": 0.0, "degage": 0.0}
    vz = v * ph["rampe_impulsion"]
    duree = 2 * vz / ph["gravite"]
    portee = v * duree
    freinage = v * v / (2 * vehicule["frein"])
    return {
        "hauteur": round(vz * vz / (2 * ph["gravite"]), 2),
        "duree": round(duree, 2),
        "portee": round(portee, 2),
        "freinage": round(freinage, 2),
        # ⚠️ Ce qu'il faut de ROULABLE apres la levre : le vol, la longueur du
        # char (il retombe sur son nez, pas sur son centre), et de quoi se
        # remettre droit. Pas le freinage complet : on atterrit et on CONTINUE,
        # on ne s'arrete pas — exiger l'arret complet ne laisserait presque
        # aucune place ou poser une rampe.
        "degage": round(portee + vehicule["longueur"] + 2 * 16, 2),
    }


def elan_pour_voler(vehicule: Vehicule, vol_px: float) -> int:
    """Combien de PIXELS d'elan il faut a ce char, parti d'arret, pour que son
    saut porte au moins `vol_px`.

    ⚠️ On integre l'acceleration et la friction image par image, exactement
    comme le moteur : une formule fermee donnerait un chiffre qui ne serait pas
    celui du jeu. C'est ce qui permet de DEDUIRE l'elan d'une rampe au lieu de
    le choisir — et de le rededuire tout seul le jour ou l'on touche a
    l'impulsion ou a la moto.
    """
    vitesse = distance = 0.0
    for _ in range(3600):                       # une minute : bien au-dela
        vitesse = (vitesse + vehicule["acceleration"]) * vehicule["friction"]
        distance += vitesse
        if saut(vehicule, vitesse)["portee"] >= vol_px:
            return math.ceil(distance)
    raise ValueError(f"{vehicule['slug']} ne volera jamais {vol_px} px")


#: L'OMBRE AU SOL — le filet de la refonte des vehicules.
#:
#: ⚠️ **Elle existe des maintenant, avant que les dessins changent**, et c'est
#: voulu : le jour ou le char sera dessine de profil, il ne montrera plus ses
#: 28 px de longueur quand il s'eloignera — un objet de 14 px de large, et son
#: encombrement disparait de l'ecran. Or se garer dans une case, juger l'espace
#: entre deux chars, reculer dans une ruelle, tout ca se joue A L'OEIL. L'ombre
#: rend a l'oeil la longueur que le dessin ne montrera plus.
#:
#: ⚠️ Et elle a l'EMPREINTE DU CATALOGUE, orientee comme le char : une tache
#: ronde ou carree ne dirait rien de ce qu'il prend comme place. C'est la meme
#: empreinte que la physique (`longueur` x `largeur`), donc ce qu'on voit est
#: exactement ce qui bloque.
#:
#: ⚠️ Les nombres etaient ECRITS EN DUR dans `dessinerUn` (0,30, 0,14, 0,35,
#: 30). Une ombre qu'on ne peut pas regler depuis la fiche est un dessin qui
#: decide de lui-meme comment la ville est eclairee.
OMBRE = {
    "part": 0.28,          # sa noirceur, pose au sol
    "part_en_vol": 0.14,   # ce qu'elle perd en montant, au plus haut
    "ecart_sol": 1,        # de combien elle deborde au sud-est, au sol
    "ecart_par_z": 0.35,   # ... et de combien de plus par pixel d'altitude
    "retrait_max": 0.35,   # ce qu'elle retrecit tout en haut
    "z_haut": 30,          # l'altitude ou elle est « tout en haut »
}


def exporter_conduite() -> dict:
    return {"trafic": dict(TRAFIC), "physique": dict(PHYSIQUE),
            "ombre": dict(OMBRE),
            "saut_vitesse_min": saut_vitesse_min()}


def par_slug(slug: str) -> Vehicule | None:
    for vehicule in CATALOGUE:
        if vehicule["slug"] == slug:
            return vehicule
    return None


def de_phase(phase: int) -> list[Vehicule]:
    return [v for v in CATALOGUE if v["phase"] <= phase]
