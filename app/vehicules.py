"""Le parc automobile de Baie-des-Brumes — source unique des stats.

Le navigateur ne connait aucune de ces valeurs : il recoit ce catalogue et
conduit avec. Les unites sont celles du moteur : pixels par image (60 images
par seconde), pixels pour le rayon de braquage, points de vie.

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
    au_volant le slug du passant (`pietons.CATALOGUE`) qui la mene TOUJOURS : le
              trafic la fait naitre avec lui, elle ne se gare jamais (une
              voiture qu'on lui a laissee n'aurait plus personne a faire
              descendre), et le carjacking sort CELUI-LA de la voiture, pas
              un passant tire au hasard. ⚠️ C'est la fiche qui le dit — le
              navigateur n'a pas a reconnaitre un cabriolet a son slug
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
    rayon_braquage: int
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
    au_volant: str | None
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
#: ⚠️ Et la CORNE des grands bateaux (le chalutier, le porte-conteneurs) : la
#: meme que celle du traversier, jouee la ou l'on est quand on la tient.
AVERTISSEURS = ("klaxon", "sonnette", "corne")

#: La friction de la rue et celle de l'eau : ce que perd, a chaque image, un
#: char qu'on ne pousse plus.
FRICTION_RUE = 0.985
FRICTION_EAU = 0.995


def friction_pour(vitesse_max: float, acceleration: float, base: float) -> float:
    """La friction d'un char : celle de la rue (ou de l'eau), sauf si elle lui
    vole la `vitesse_max` que sa fiche promet.

    ⚠️ **LA FICHE NE MENT PAS SUR LA VITESSE** (21 sept. 2026, retour de Martin :
    « la paie de la Prevost est presque impossible, le camion va trop lentement
    pour les policiers »). A fond, le moteur fait `vitesse = (vitesse +
    acceleration) x friction` a chaque image : la vitesse plafonne la ou la
    friction mange tout ce que le moteur ajoute, a `acceleration x friction /
    (1 - friction)`. A 0,985, un moteur faible n'atteignait JAMAIS sa
    `vitesse_max` : le camion plafonnait a 1,97 px/image au lieu de 2,8 — moins
    qu'un agent a pied (2,0), qui le suivait a 40 px jusqu'au bar, et les deux
    etoiles de s03 ne tombaient jamais. La berline de luxe roulait a 2,76 au
    lieu de 3,6, le porte-conteneurs a la moitie de sa fiche, et le compteur du
    HUD n'affichait jamais 120.

    ⚠️ C'est donc la FRICTION qui se deduit, juste assez faible pour que la
    pointe soit la `vitesse_max` — pas l'acceleration, qui dit comment le char
    DEMARRE : le camion part toujours en camion. Et le trafic ne voit rien : il
    roule sur ses rails (`rouler`), sans friction, et son acceleration n'a pas
    bouge d'un cheveu. Un char qui atteint deja sa vitesse garde la friction de
    la rue : la moto, la police, le taxi ne changent pas.
    """
    juste = vitesse_max / (vitesse_max + acceleration)
    # Arrondie VERS LE HAUT : arrondie au plus pres, la pointe retombait d'un
    # cheveu sous la fiche.
    return max(base, math.ceil(juste * 100_000) / 100_000)


def _v(slug, nom, classe, lon, lat, vmax, accel, rayon, vie, places, prix, freq, couleurs,
       sprite, *, police=False, sirene=False, alarme=False, ejecte=False, eau=False,
       masse=1.0, cercles=3, reservoir=True, defonce=0.0, soigne=0.0, crochet=False,
       plateau=False, boulot=None,
       radio=None, phase=1, klaxon="klaxon", rare=False, adherence=None, alarme_s=0.0,
       au_volant=None) -> Vehicule:
    return Vehicule(
        slug=slug, nom=nom, classe=classe, longueur=lon, largeur=lat,
        vitesse_max=vmax, vitesse_recul=round(vmax * 0.33, 2), acceleration=accel,
        frein=round(accel * 2, 3),
        friction=friction_pour(vmax, accel, FRICTION_EAU if eau else FRICTION_RUE),
        rayon_braquage=rayon,
        adherence=adherence if adherence is not None else (0.30 if not eau else 0.05),
        adherence_frein=0.035,
        masse=masse, vie=vie, places=places, prix=prix, frequence=freq,
        couleurs=couleurs, sprite=sprite, police=police, sirene=sirene, alarme=alarme,
        ejecte=ejecte, eau=eau, cercles=cercles, reservoir=reservoir, rare=rare, alarme_s=alarme_s,
        au_volant=au_volant,
        defonce=defonce, soigne=soigne,
        crochet=crochet, plateau=plateau, boulot=boulot, radio=radio, phase=phase,
        portieres=classe in CLASSES_A_PORTIERES, klaxon=klaxon,
    )


#: ⚠️ L'auto est la reference (vitesse 100 %). Les prix sont ceux du garage
#: clandestin de Ti-Guy pour un vehicule PROPRE ; la revente d'un vehicule vole
#: rapporte `economie.VENTE_FRACTION` de ce prix.
CATALOGUE: list[Vehicule] = [
    _v("auto", "Berline", "auto", 28, 14, 4.0, 0.06, 22, 100, 4, 600, 0.40,
       ["#c0392b", "#2c3e50", "#ecf0f1", "#27ae60", "#8e44ad", "#d35400"], "auto",
       alarme=False, radio="la_brume"),
    _v("taxi", "Taxi", "auto", 28, 14, 3.8, 0.058, 21, 110, 4, 700, 0.12,
       ["#f1c40f"], "taxi", boulot="taxi", radio="taxi_radio"),
    # ⚠️ La pizza se livre en moto, et c'est ce qui fait le boulot : le char le
    # plus rapide du jeu est aussi celui dont on tombe au premier choc.
    _v("moto", "Moto", "moto", 20, 8, 5.2, 0.09, 14, 40, 2, 450, 0.15,
       ["#1a1a1a", "#c0392b", "#2980b9"], "moto", ejecte=True, boulot="pizza",
       radio="le_choc", plateau=True),
    # ⚠️ Le velo est un vehicule comme un autre : il suit la rue, on peut le
    # prendre a son cycliste (qui temoigne), on en tombe au premier choc.
    # ⚠️ `reservoir=False` : un velo n'a pas d'essence, donc il ne brule pas et
    # n'explose pas. C'est le SEUL du catalogue dans ce cas, et c'est le seul
    # endroit ou ca se decide.
    _v("velo", "Vélo", "velo", 16, 8, 2.0, 0.05, 12, 30, 1, 120, 0.18,
       ["#2980b9", "#c0392b", "#27ae60", "#f1c40f"], "velo", ejecte=True, reservoir=False,
       klaxon="sonnette", plateau=True),
    _v("police", "Auto-patrouille", "auto", 28, 14, 4.4, 0.07, 20, 150, 4, 2500, 0.0,
       ["#ffffff"], "police", police=True, sirene=True, alarme=True, radio="dix_quatre"),
    # --- M9, le parc automobile ------------------------------------------
    # ⚠️ `cercles` n'est pas un reglage de confort : la chaine doit COUVRIR la
    # carrosserie, sinon deux cercles voisins laissent un trou par lequel une
    # moto entre dans l'autobus. Il en faut au moins `longueur / largeur`
    # (juge `test_la_chaine_de_cercles_ne_laisse_aucun_trou`) — d'ou les cinq
    # de l'autobus, « deux de plus » que les trois de tout le monde.
    _v("camion", "Camion", "camion", 40, 16, 2.8, 0.03, 33, 300, 2, 1200, 0.08,
       ["#7f8c8d", "#c0392b", "#2c3e50"], "camion", masse=3.0, cercles=4,
       defonce=0.75, radio="station_camion", adherence=0.22),
    _v("autobus", "Autobus", "camion", 48, 16, 2.6, 0.028, 40, 250, 12, 1500, 0.04,
       ["#2980b9"], "autobus", masse=3.2, cercles=5, defonce=0.7, adherence=0.22,
       boulot="autobus"),
    # ⚠️ L'ambulance SOIGNE (2 PV par seconde au volant) — elle ne ressuscite
    # personne : un blesse mort reste mort, et le boulot est perdu.
    _v("ambulance", "Ambulance", "auto", 32, 15, 3.6, 0.05, 25, 180, 3, 1400, 0.04,
       ["#ffffff"], "ambulance", sirene=True, alarme=True, masse=1.4, soigne=2.0,
       boulot="ambulance"),
    _v("remorqueuse", "Remorqueuse", "camion", 36, 15, 3.0, 0.04, 29, 220, 2, 1300, 0.05,
       ["#d98324", "#2c3e50", "#7f8c8d"], "remorqueuse", masse=2.2, cercles=4, adherence=0.24,
       defonce=0.6, crochet=True, boulot="remorquage", radio="station_remorqueuse"),
    # ⚠️ **LA PELLE QU'ON CONDUIT** (« Ça travaille », 8e vague : l'étage 2 du plan, que la refonte
    # des véhicules avait retardé). Elle ne naît JAMAIS dans la rue (`frequence` 0) : c'est celle du
    # chantier, `chantiers.js` la sort de son décor quand on monte dedans. Elle roule à 12 km/h
    # (1,3 — l'auto de référence fait 4,0), tourne court, et ne s'arrête devant rien : `defonce`
    # 0,95, elle garde presque toute sa vitesse en traversant ce qu'un autre char casse en
    # ralentissant — et le seuil de vitesse pour défoncer une clôture se règle sur SA vitesse
    # (`vehicules.js`), pas sur celle d'un camion.
    # ⚠️ **Masse 3,3, et pas plus** : plus lourde que l'autobus (3,2), sous le camion-cuisine (3,4) —
    # une pelle qui déracinerait un commerce en roulant à 12 km/h n'est plus une farce — et très
    # loin sous les machines du chantier (6, 8, 9) : elle ne détruit pas les siennes.
    # ⚠️ **16 de large, comme le camion** : les bacs des éboueurs se tiennent à 14 px du centre de la
    # voie, et `test_eboueurs_js` calcule cette marge sur le char le plus LARGE du parc — à 20 (rayon
    # 10), la pelle frôlait un bac que le camion ne touche pas. On ne déplace pas les bacs de la ville
    # pour un char qui n'est jamais dans le trafic.
    _v("pelleteuse", "Pelleteuse", "camion", 38, 16, 1.3, 0.022, 30, 320, 1, 1500, 0.0,
       ["#e8b33c"], "pelleteuse", masse=3.3, cercles=4, defonce=0.95, adherence=0.22),
    # --- Le haut de gamme : deux chars qu'on vole EXPRES ------------------
    # ⚠️ Tout le reste du parc est utilitaire — on le prend parce qu'il sert.
    # Ces deux-la, on les prend parce qu'on les VEUT, et ils s'opposent en
    # tout : la vitesse contre l'argent, la carrosserie mince contre la
    # lourde. Deux fiches, pas dix.
    #
    # ⚠️ `rare=True` : ils ne naissent que dans les districts qui les
    # declarent. C'est la, et pas dans ces nombres, que se joue leur rarete.
    _v("sport", "Coupé sport", "auto", 26, 13, 4.8, 0.085, 18, 75, 2, 3200, 0.02,
       ["#c0392b", "#ecf0f1", "#f1c40f", "#16a085"], "sport",
       alarme=True, rare=True, masse=0.85,
       # L'adherence basse est TOUT le caractere du char : il part en travers
       # au frein a main la ou une berline se contente de ralentir.
       adherence=0.18),
    _v("luxe", "Berline de luxe", "auto", 32, 15, 3.6, 0.042, 26, 220, 4, 5200, 0.02,
       ["#101014", "#2c3e50", "#6b4b2c"], "luxe",
       alarme=True, rare=True, masse=1.8,
       # ⚠️ Elle encaisse ET elle colle a la route : elle ne recompense pas la
       # conduite, elle recompense le vol. C'est la meilleure revente du jeu,
       # et `economie.prix_vente` le fait toute seule — le prix neuf suffit.
       adherence=0.40, alarme_s=30.0),
    # ⚠️ **LE CABRIOLET ROSE** (demande de Martin, 21 sept. 2026 : « une voiture
    # type corvette, rose, avec une femme en robe rose qui la pilote et en descend
    # si volee. Elle va plus vite »). Le troisieme char qu'on vole EXPRES, et le
    # seul du parc qui a SA conductrice (`au_volant`).
    #
    # ⚠️ **Elle va plus vite que le sport — pas plus vite que la moto.** Le
    # garde-fou d'`exploitation.md` tient toujours : un char qui roule bien au-dela
    # de l'auto-patrouille (4,4) rend la police decorative. Elle depasse le sport
    # (4,8) d'un cran et la patrouille de 14 %, jamais la moto (5,2) ; la parade
    # est la meme que la sienne — la carrosserie mince (80 PV : un barrage l'arrete
    # pour de bon), l'alarme, et une adherence qui la fait partir en travers.
    # `frequence` est plus haute que celle du sport : on la VEUT, mais on veut
    # d'abord la VOIR — et c'est la carte qui decide ou (`rares` de `carte.py`).
    _v("cabriolet", "Cabriolet rose", "auto", 27, 13, 5.0, 0.09, 18, 80, 2, 3800, 0.04,
       ["#ff77b7"], "cabriolet", alarme=True, rare=True, masse=0.9,
       adherence=0.20, au_volant="conductrice"),
    # ⚠️ **LA DETTE DE M3, PAYEE LE 16 SEPT. 2026.** « Phase 2 » voulait dire
    # « sans sprite et sans trafic » : la fiche existait depuis M3 — eau,
    # friction 0,995, adherence 0,05, trois cercles — et rien ne l'avait jamais
    # fait flotter. Il ne manquait que deux choses, et aucune n'etait une
    # physique a part : un DESSIN, et une regle de tuile.
    #
    # ⚠️ **Un char et une coque ne sont pas arretes par les memes choses**, et
    # c'est la seule difference entre les deux mondes : le char est arrete par
    # les murs et PASSE sur l'eau (il coule, `majNoyade` s'en charge depuis que
    # l'eau n'est plus un mur) ; la coque est arretee par TOUT CE QUI N'EST PAS
    # DE L'EAU. Une ligne dans `tuileInterdite`, pas une classe.
    #
    # ⚠️ `frequence: 0` — elle ne nait PAS dans le trafic : une chaloupe qui
    # roule sur la rue Principale est exactement ce que la regle ci-dessus
    # interdit, et le trafic suit des voies qui n'existent pas sur l'eau. On la
    # trouve amarree au quai (`carte.amarrages`), et nulle part ailleurs.
    _v("bateau", "Chaloupe", "bateau", 30, 12, 3.2, 0.02, 40, 120, 4, 2000, 0.0,
       ["#ecf0f1", "#2c3e50"], "bateau", eau=True, cercles=3, phase=1),
    # --- Deux bateaux de plus (demande de Martin, 21 sept. 2026) -----------
    # ⚠️ « nouveau bateau : chalutier + porte-conteneurs ». La meme regle que la
    # chaloupe, et rien d'autre : `eau`, hors du trafic, et la coque arretee par
    # tout ce qui n'est pas de l'eau. Ils mouillent a quai (`navires.py`), pas aux
    # amarrages : une chaloupe se glisse contre n'importe quelle rive batie, un
    # chalutier demande trois tuiles de quai, un porte-conteneurs dix.
    #
    # ⚠️ **LA CORNE, PAS LE KLAXON** : c'est la fiche qui le dit (`klaxon`), et
    # c'est l'echantillon du traversier. Une chaloupe hors-bord garde son klaxon
    # — personne ne met une corne de brume sur un 9,9 forces.
    #
    # ⚠️ **Le prix reste sous celui du luxe** (le juge : « la meilleure revente du
    # jeu »). Ce n'est pas ce que vaut un navire : c'est ce que Ti-Guy en donnerait,
    # et un porte-conteneurs ne passe pas la porte de son garage.
    #
    # Le chalutier : trois tuiles et demie, plus lent et plus lourd que la
    # chaloupe, et il encaisse — c'est un outil de travail.
    _v("chalutier", "Chalutier", "bateau", 56, 18, 2.6, 0.012, 56, 300, 3, 3000, 0.0,
       ["#c0392b", "#1f4e79", "#2e7d4f", "#e8e2d0"], "chalutier", eau=True, masse=3.0,
       cercles=4, klaxon="corne"),
    # Le porte-conteneurs : dix tuiles, deux de plus que le traversier. Il met cinq
    # secondes a prendre son erre, il vire le plus large que le juge permette (six
    # tuiles), il glisse (`adherence` de l'eau) et il pousse tout ce qui flotte
    # (`masse`). Cinq cercles : il en faut `longueur / largeur`, soit quatre.
    _v("porte_conteneurs", "Porte-conteneurs", "bateau", 160, 40, 1.9, 0.005, 96, 1500, 2, 5000, 0.0,
       ["#1f3a5f", "#7a1f1f", "#2b2b30", "#1d5c4a"], "porte_conteneurs", eau=True, masse=12.0,
       cercles=5, klaxon="corne"),
]

CLASSES = ("auto", "moto", "velo", "camion", "bateau")

#: Le trafic : combien de chars vivent dans la bulle du joueur, et comment un
#: conducteur regarde devant lui. Les feux durent en images (60 par seconde).
TRAFIC = {
    "vehicules_max": 9,           # en circulation, dans la bulle
    "stationnes_max": 6,          # a l'arret sur les stationnements
    # ⚠️ **LA NUIT, LES CHARS RENTRENT A LA MAISON** (Martin, 21 sept. 2026 : « la
    # nuit, plus de vehicules stationnes »). Le jour, six chars gares ou que ce
    # soit ; la nuit, le monde est rentre : DEUX FOIS plus, et d'abord dans les
    # rues ou l'on habite (`Monde.usageA` = `usage`). Une fois sur quelques-unes
    # (`ailleurs`), devant un commerce quand meme : le bar et le depanneur ont
    # leurs clients de nuit — et un quartier sans une seule rue a logements (La
    # Shop) garde ses chars de nuit dans ses cours. ⚠️ Le JOUR ne change pas
    # d'un de : le banc joue a 8 h 24, et chaque naissance deplacee decale tous
    # les des qui suivent (`Vehicules.peupler`).
    "garer_la_nuit": {"max": 12, "usage": "residentiel", "ailleurs": 0.15},
    "regard_tuiles": 4,           # a quelle distance un conducteur regarde devant
    "distance_securite_px": 34,   # plus pres que ca, il freine
    "vitesse_ville": 0.55,        # fraction de la vitesse max en circulation
    "depassement_tuiles": 5,      # la voie d'a cote doit etre libre sur ce tant
    "depassement_images": 90,     # apres un deport, on ne se redeporte pas avant
    "patience_images": 200,       # bloque plus longtemps : il force le passage
    "arret_images": 45,           # au STOP : on s'immobilise ce temps-la
    "priorite_pieton_px": 70,     # un pieton engage sur le passage : on attend
    # ⚠️ **LE NEZ A LA LIGNE, PAS LE CENTRE.** Depuis `TROTTOIR = 1`, la traverse
    # fait UNE tuile, toute peinte, collee a la ligne d'arret. Un char qui
    # attend LE CENTRE sur la ligne mord donc dans les bandes de tout ce qui
    # depasse ses huit pixels d'avant : 4,9 px pour une berline, 10 pour une
    # remorqueuse, 12 pour un camion, et l'autobus couvre la traverse entiere.
    # Il attend maintenant la ou son NEZ touche la ligne — ce qui oblige un long
    # char a freiner UNE TUILE PLUS TOT, exactement ce que l'autobus de M9
    # faisait deja tout seul (sa caisse fait trois tuiles, et l'arret au centre
    # de la tuile d'avant lui posait le nez pile sur la ligne : c'est cette
    # trouvaille-la qui est ici generalisee a tout le parc).
    #
    # ⚠️ Et on ne freine pas SEC a la vue du rouge : la vitesse voulue fond avec
    # ce qui reste a parcourir (`approche_part` de la distance, au plus
    # `approche_vitesse`). Sans ca, un char qui voit le feu une tuile avant la
    # ligne s'arreterait la ou il l'a vu — au milieu de la rue, a une tuile de
    # la ligne — et la file entiere reculerait d'autant.
    "approche_vitesse": 1.1,      # au plus, en glissant vers la ligne d'arret
    "approche_part": 0.25,        # ... et on ne comble que cette part du reste
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
    # ⚠️ **LA NUIT, LES FEUX CLIGNOTENT.** Vrai partout au Quebec, et presque
    # gratuit ici : `feuDeCirculation` est une pure fonction de l'heure, et
    # tout en decoule (le dessin de la lanterne, ce que le trafic respecte).
    # A partir de `clignotant_depuis`, l'ARTERE clignote jaune (on passe sans
    # s'arreter) et la rue secondaire clignote rouge (un STOP). Le trafic de
    # nuit, qui n'a plus personne a croiser, cesse d'attendre devant un feu
    # rouge pour rien — et sur une ville deserte, ca se voit de loin.
    #
    # ⚠️ Les deux heures tombent DANS la nuit du rythme (`DISTRICTS[].rythme`,
    # 0,82 → 0,25) : un juge le tient. Des feux qui clignotent pendant que la
    # rue est encore pleine, ce n'est pas la nuit, c'est une panne.
    "clignotant_depuis": 0.86,     # ~20 h 40
    "clignotant_jusqu_a": 0.25,    # 6 h
    "clignotant_images": 36,       # une pulsation : on la voit sans qu'elle agace
    # ⚠️ **LES HEURES DE POINTE ONT UNE DIRECTION.** Le rythme dit COMBIEN de
    # chars roulent ; il ne dit pas OU ils vont. Le matin le trafic converge
    # vers le coeur de la ville, le soir il s'en disperse. ⚠️ Et pas en touchant
    # au champ de direction, qui est fixe et juge : en PONDERANT le choix de
    # sortie aux croisements. `penchant` est la part des chars qui suivent le
    # mouvement — le reste tire au sort comme toujours, sinon la ville entiere
    # roule dans le meme sens et ce n'est plus une heure de pointe, c'est une
    # evacuation.
    # ⚠️ **LE CHAR EN PANNE** — une entrave qui n'etait PAS prevue, et c'est
    # tout son interet : elle n'a ni cones, ni panneau, ni liste validee par
    # Python. Un camion s'arrete en travers d'une voie, ses feux de detresse
    # battent, et il repart au bout d'une heure de jeu. Le trafic sait deja
    # quoi en faire : il se deporte (`obstacleDevant`), exactement comme
    # devant un pieton plante sur la chaussee.
    #
    # ⚠️ Elle dure UNE HEURE, pas un jour : une entrave du jour change la
    # ville, une panne ne fait que la contrarier. Et elle ne se tire qu'une
    # fois par heure de jeu — sinon la ville est un garage.
    "panne": {
        "chance_par_heure": 0.35,
        "minutes": 40,             # en minutes de jeu
        "slugs": ["camion", "autobus", "remorqueuse", "auto"],
        "detresse_images": 26,     # ses feux battent a ce rythme
        # ⚠️ **JAMAIS CONTRE UNE TRAVERSE.** Une panne se pose sur une voie, donc
        # jamais sur la ligne d'arret ni dans le croisement — mais la voie qui
        # PRECEDE un passage cloute est une voie comme une autre, et la caisse,
        # elle, deborde : l'autobus fait 48 px, trois tuiles. Un char qui attend
        # au feu repart ; celui-la reste quarante minutes de jeu en travers du
        # seul endroit ou l'on traverse. Deux tuiles de degagement de chaque
        # bord couvrent le plus long de la liste.
        "ecart_traverse_tuiles": 2,
    },
    "pointe": {
        "matin": [0.27, 0.42],     # 6 h 30 → 10 h : on rentre travailler
        "soir": [0.68, 0.84],      # 16 h 20 → 20 h : on en sort
        "penchant": 0.45,
        "vers": "faubourg",        # le coeur : le district ou l'on converge
    },
    "naissance_px": 300,          # comme les pietons : hors ecran, dans la bulle
    "oubli_px": 560,
    # ⚠️ **LE VELO ROULE A LA BORDURE** — Martin (21 sept. 2026) : « les velos
    # peuvent passer dans les parcs, les trottoirs, et restent souvent sur la
    # bordure de la route, sauf pour virage a gauche ». Il roulait au MILIEU de
    # sa voie, comme une auto de huit pixels de large.
    #
    # ⚠️ Rien ici ne se tire au de du jeu : l'intention de tourner, le trottoir
    # et le parc se lisent a l'EMPREINTE du cycliste et de l'endroit (`hash2`).
    # C'est la lecon du pilote des deux-roues — un de de plus decale tout ce
    # qui nait apres, et un juge de police voit son auto-patrouille ailleurs.
    "velo": {
        "bord_px": 4,             # il se tasse de ca vers le trottoir, depuis le centre de sa voie
        # A cette distance de la ligne d'arret, il SAIT ou il va : s'il tourne a
        # gauche, il se range a gauche (la voie du milieu, s'il y en a une), et
        # tourne de la. Cinq tuiles : assez pour se tasser en diagonale.
        "virage_tuiles": 5,
        # --- Hors de la rue : le trottoir et le parc ------------------------
        # ⚠️ **AU PAS, ET EN CEDANT.** Un velo qui fauche les pietons du trottoir
        # n'est plus un cycliste, c'est une arme : il roule sous la vitesse qui
        # renverse (`PHYSIQUE.renverse_vitesse_min`), s'arrete derriere un
        # passant et sonne.
        "trottoir_vitesse": 0.8,  # en px/image (une auto de ville : 2,2 ; un passant : 0,45)
        "parc_chance": 0.05,      # par tuile longee au bord d'un parc : il entre le traverser
        "trottoir_chance": 0.01,  # par tuile de voie : il monte faire un bout de trottoir
        "trottoir_tuiles": [4, 10],  # la longueur d'un bout de trottoir, au plus ce qu'il y a
        # Coince derriere un char arrete ce temps-la, un cycliste sur deux monte
        # sur le trottoir et le longe — l'autre attend comme une auto.
        "coince_images": 45,
        "coince_part": 0.5,
        "parc_allees_min": 6,     # une traversee de parc passe par au moins autant d'allee
        "noeuds_max": 2500,       # le budget de la recherche d'une traversee
        "attente_images": 240,    # au bout du trottoir, il attend un trou dans la voie, pas plus
        "sonnette_images": 150,   # entre deux coups de sonnette a un passant
        "repos_images": 900,      # redescendu, il ne remonte pas avant ce temps
    },
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
    # ⚠️ **UN NID-DE-POULE**, et toute la ville prend un accent. La carte dit
    # OU ils sont (`carte.NIDS_DE_POULE`) ; ici, ce qu'ils coutent. Deux points
    # de carrosserie : on les sent, on ne les craint pas — c'est du decor
    # sonore et tactile, pas un piege.
    "nid_degats": 2,
    "nid_secousse": 0.35,
    "nid_repit_images": 30,       # on ne le paie pas deux fois en le traversant
    # ⚠️ **UNE PLAQUE D'ACIER** (la tranchée d'un chantier, `chantiers.py`) : elle
    # claque et elle secoue, elle ne coûte RIEN — un nid-de-poule est un accident,
    # une plaque est un décor qu'on sent. Plus doux : ce n'est pas un trou.
    "plaque_secousse": 0.28,
    "plaque_repit_images": 30,
    # ⚠️ **UN TAS DE TERRE** (le chantier, `chantiers.py`) est une rampe NATURELLE : plus
    # douce que celle des défis, et elle ne se mesure pas — elle se PLAFONNE. La vitesse
    # qui compte est bornée (`tas_vitesse_max`) et le saut ne monte jamais au-dessus de
    # `tas_hauteur_max` px : c'est sous le seuil (6 px) où un char passe AU-DESSUS des
    # tuiles, donc un mur retient toujours ce qui retombe. Un juge REJOUE le saut d'ici, image
    # par image (l'intégration est discrète : `z += vz; vz -= gravité` monte de `vz / 2` de
    # plus que la formule continue — 6,3 px mesurés à 0,42, la moto).
    "tas_impulsion": 0.38,        # vz = vitesse * ca, en sortant sur le tas
    "tas_vitesse_min": 1.2,       # plus lent, on monte dessus sans décoller
    "tas_vitesse_max": 4.0,       # la moto (5,2) ne vole pas plus haut que la berline
    "tas_hauteur_max": 6,         # px : jamais plus haut qu'un char qui passe au-dessus d'un mur
    "tas_repit_images": 30,       # on ne rebondit pas dix fois en roulant sur le même tas
    "tas_secousse": 0.18,
    # ⚠️ **UNE BENNE QU'ON POUSSE** (`chantiers.py`) : elle ralentit le char qui la pousse, d'autant
    # plus qu'il est léger — `poussee_frein` x la masse de la benne / celle du char, par image de
    # contact, au plus `poussee_frein_max`. Une berline (1,0) pousse une benne (1,8) à petite
    # vitesse ; l'autobus (3,2) la sent à peine ; un char plus léger que le vélo serait borné.
    "poussee_frein": 0.04,
    "poussee_frein_max": 0.4,
    # ⚠️ **LE BRAQUAGE EST UN RAYON, PAS UNE VITESSE DE ROTATION** (15 sept.
    # 2026, demande de Martin : « ameliore les virages »). Le char tournait de
    # `braquage` RADIANS PAR IMAGE, quelle que soit sa vitesse : le rayon du
    # cercle qu'il decrit valait donc `vitesse / braquage` — il GRANDISSAIT
    # avec la vitesse. Mesure sur une berline : 1,7 tuile au pas, **DIX TUILES
    # a fond**. Un coin de rue en demande une et demie ; a pleine vitesse le
    # coin etait tout simplement impossible, et `majTrafic` l'ecrivait deja
    # noir sur blanc (« il ratait son virage et finissait sur le trottoir d'en
    # face »).
    #
    # Une vraie auto ne marche pas comme ca : a volant fixe, elle decrit
    # TOUJOURS LE MEME CERCLE, vite ou lentement. La rotation est donc
    # proportionnelle a la vitesse (`vitesse / rayon_braquage`), et le rayon
    # est ce que la fiche declare — en pixels, un nombre qu'on peut se figurer
    # (22 px pour une berline : une tuile et demie).
    #
    # ⚠️ Le volant garde un peu plus de prise au pas (`braquage_lent`) et en
    # perd a fond (`braquage_vite`) — c'est vrai d'une vraie auto, et c'est ce
    # qui empeche la pleine vitesse de devenir un pivot.
    "braquage_plein_a": 0.35,     # la fraction de vitesse ou le volant donne tout
    "braquage_lent": 1.15,        # ce qu'il a de prise en plus, au pas
    "braquage_vite": 0.42,        # ... et ce qu'il en reste a fond
    # ⚠️ **UN VOLANT SE TOURNE, il ne se claque pas.** La direction passait de
    # 0 a 1 en une image : au clavier, chaque appui etait un coup de butee a
    # butee. Il prend (`volant_prise`), il se recentre quand on lache
    # (`volant_retour`) — un dixieme de seconde, et la courbe devient une courbe.
    "volant_prise": 0.22,
    "volant_retour": 0.30,
    # ⚠️ **UN CHAR PIVOTE SUR SON ARRIERE**, pas sur son nombril. En tournant
    # autour de son centre, il balayait son coffre dans le mur derriere lui et
    # le nez ne « rentrait » jamais dans le virage. Le point de pivot recule
    # d'une fraction de la longueur : le nez balaie, le train arriere suit.
    # ⚠️ Et jamais dans un mur : le decalage n'est pris que s'il est libre.
    "pivot_arriere": 0.28,
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
#: ⚠️ **LE SOL SE VOIT DE BIAIS** (`profondeur`, 15 sept. 2026, retour de
#: Martin : « corrige les ombres pour les vehicules en nord-sud »). L'empreinte
#: est celle du catalogue — 28 px de long pour une berline —, mais un char
#: DEBOUT ne montre plus sa longueur quand il roule vers le nord : son dessin
#: fait 16 px de large et 11 px de haut. L'ombre, elle, s'etalait sur les 28 px
#: pleins : une langue noire de QUINZE pixels devant un char haut de onze, qu'on
#: lisait comme une remorque. Une ombre ne peut pas etre plus longue que ce qui
#: la jette.
#:
#: La regle est celle que le jeu applique deja a tout ce qui se tient debout :
#: l'axe qui S'ENFONCE dans l'ecran (le nord-sud) est ECRASE. L'ombre d'un
#: passant le disait depuis toujours — `DECORS.ombre` fait 12 x 6 pour un corps
#: rond — et un juge de banc tient maintenant les deux d'accord : un seul biais
#: pour toute la ville. L'empreinte en X, elle, ne bouge pas d'un pixel : c'est
#: l'axe que le dessin montre.
#:
#: ⚠️ Et l'ecart a DEUX composantes depuis le meme retour. La lumiere vient du
#: nord-ouest, donc l'ombre tombe vers l'EST ; vers le SUD, elle ne tombe pas
#: au sol — un char pose n'a rien devant ses roues —, elle ne s'echappe qu'en
#: MONTANT (`ecart_par_z`), et c'est exactement ce qui fait qu'un saut se voit.
OMBRE = {
    "part": 0.28,          # sa noirceur, pose au sol
    "part_en_vol": 0.14,   # ce qu'elle perd en montant, au plus haut
    "profondeur": 0.75,    # l'ecrasement de l'axe nord-sud — le MEME que le dessin (`BIAIS_DU_SOL`)
    "ecart_est": 2,        # ou elle tombe au sol : a l'est (la lumiere est au nord-ouest)
    "ecart_sud": 0,        # ... et pas au sud : rien ne depasse devant les roues
    "ecart_par_z": 0.35,   # ce qu'elle s'echappe en plus, par pixel d'altitude
    "retrait_max": 0.35,   # ce qu'elle retrecit tout en haut
    "z_haut": 30,          # l'altitude ou elle est « tout en haut »
}


#: ⚠️ **CE QUI EST GARE DIT LE STANDING** (4e vague des quartiers). `rares` : le
#: haut de gamme peut-il naitre ici ? Une decapotable devant un preteur sur gages
#: n'est plus une decapotable, c'est une auto de plus — et c'est la rue chic du
#: Faubourg qui la rend desirable. `usure` : la part de carrosserie qu'un char de
#: la rue a encore — en pauvre, on roule une minoune, et elle casse plus vite.
#: ⚠️ Pas d'epave sur des blocs (le plan la proposait) : une epave s'efface au bout
#: de `PHYSIQUE["epave_secondes"]`, elle ne peut pas decorer une rue.
STANDING_DU_PARC: dict[str, dict] = {
    "cossu": {"rares": 1, "usure": 1.0},
    "ordinaire": {"rares": 1, "usure": 1.0},
    "pauvre": {"rares": 0, "usure": 0.6},
}


def exporter_conduite() -> dict:
    return {"trafic": dict(TRAFIC), "physique": dict(PHYSIQUE),
            "ombre": dict(OMBRE),
            "standing": {nom: dict(fiche) for nom, fiche in STANDING_DU_PARC.items()},
            "saut_vitesse_min": saut_vitesse_min()}


def par_slug(slug: str) -> Vehicule | None:
    for vehicule in CATALOGUE:
        if vehicule["slug"] == slug:
            return vehicule
    return None


def de_phase(phase: int) -> list[Vehicule]:
    return [v for v in CATALOGUE if v["phase"] <= phase]
