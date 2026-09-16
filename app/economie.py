"""L'argent de Baie-des-Brumes : ce qu'on gagne, ce qu'on perd, ce qu'on achete.

Toutes les formules sont ICI et testees ici ; le navigateur recoit des tables
deja calculees (`exporter()`) et ne fait qu'y lire. Une regle d'equilibrage
qui vivrait dans le JS ne serait ni testee ni relue.

Horloge : un jour de jeu = 8 minutes reelles. Une session de 15 a 30 minutes
vaut donc 2 a 4 jours ; « devenir le boss » demande 3 a 5 heures.
"""

from __future__ import annotations

from typing import TypedDict

ARGENT_DEPART = 50
FORTUNE_MAX = 50_000_000
JOUR_SECONDES = 480

#: Un joueur qui ne fait que gagner de l'argent plafonne autour de 2 000 $/h
#: (0,6 $/s). Cette borne de VRAISEMBLANCE sert au tableau des scores : un score
#: qui l'explose n'est pas une performance, c'est un navigateur bidouille.
GAIN_MAX_PAR_SECONDE = 500

# --- Prison et hopital ----------------------------------------------------

#: Base de l'amende, par nombre d'etoiles (1 a 5).
AMENDE_BASE = (60, 150, 300, 600, 1000)
AMENDE_PAR_CASIER = 0.5
CASIER_MAX = 20

POT_DE_VIN_BASE = 40
#: Chance qu'un policier accepte le pot-de-vin, par nombre d'etoiles.
POT_DE_VIN_ACCEPTE = (0.0, 0.9, 0.6, 0.3, 0.0, 0.0)
#: Un sergent « ami » accepte toujours jusqu'a ce nombre d'etoiles.
POT_DE_VIN_AMI_MAX = 2

HOPITAL = {"fraction": 0.10, "minimum": 30, "maximum": 500}

# --- Les boulots montent en grade -----------------------------------------

#: ⚠️ **Un boulot qui paie et rien d'autre n'est pas une activite, c'est un
#: distributeur.** Dans les classiques vus d'en haut, le taxi, l'ambulance et
#: les pompiers donnent des recompenses PERMANENTES par paliers : c'est ce qui
#: transforme « je fais trois courses pour manger » en « je fais cinquante
#: courses parce qu'au bout il y a quelque chose ».
#:
#: ⚠️ **Et les recompenses ne sont presque jamais de l'argent.** Un palier qui
#: paie mieux rend le boulot meilleur que la mission, et le jeu se joue tout
#: seul (`test_paliers`). Ce qu'on gagne ici, ce sont des CAPACITES : des
#: points de vie, un char gare a la planque, un lot qui ne te fait plus payer,
#: une facture d'hopital coupee en deux. Un seul palier touche a l'argent — la
#: prime du boulot — et il est borne par les memes juges que les boulots
#: eux-memes.
#:
#: `type` dit ce que le navigateur doit faire, `valeur` avec quelle force.
#: ⚠️ Quand deux paliers portent le meme `type`, c'est le PLUS FORT qui compte
#: — ils ne s'additionnent pas. Sans cette regle, « +10 % puis +25 % de vie »
#: ferait +35 %, et la fiche dirait une chose pendant que le jeu en ferait une
#: autre.
PALIERS_TYPES = ("prime", "vie", "char", "fourriere", "hopital", "rabais")

PALIERS: dict[str, tuple[dict, ...]] = {
    "taxi": (
        {"compte": 10, "type": "prime", "valeur": 1.3,
         "nom": "ON TE RECONNAIT", "detail": "+30 % DE POURBOIRE"},
        {"compte": 25, "type": "rabais", "valeur": 0.75, "cle": "kiosque",
         "nom": "LE CAFE DU CHAUFFEUR", "detail": "-25 % AUX KIOSQUES"},
        {"compte": 50, "type": "char", "valeur": "taxi",
         "nom": "TON PROPRE TAXI", "detail": "GARE A LA PLANQUE"},
    ),
    "pizza": (
        {"compte": 10, "type": "prime", "valeur": 1.3,
         "nom": "LIVREUR DU MOIS", "detail": "+30 % DE PRIME"},
        {"compte": 25, "type": "hopital", "valeur": 0.5,
         "nom": "TU CONNAIS TOUT LE MONDE", "detail": "HOPITAL A MOITIE PRIX"},
        {"compte": 50, "type": "char", "valeur": "moto",
         "nom": "LA MOTO DU LIVREUR", "detail": "GAREE A LA PLANQUE"},
    ),
    "ambulance": (
        {"compte": 10, "type": "vie", "valeur": 1.10,
         "nom": "TU AS VU PIRE", "detail": "+10 % DE VIE"},
        {"compte": 25, "type": "vie", "valeur": 1.25,
         "nom": "PLUS RIEN NE T'ECOEURE", "detail": "+25 % DE VIE"},
        {"compte": 50, "type": "char", "valeur": "ambulance",
         "nom": "L'AMBULANCE EST A TOI", "detail": "GAREE A LA PLANQUE"},
    ),
    "remorquage": (
        {"compte": 10, "type": "fourriere", "valeur": 0.5,
         "nom": "LES GARS DU LOT TE CONNAISSENT", "detail": "RACHAT A MOITIE PRIX"},
        {"compte": 25, "type": "fourriere", "valeur": 0.0,
         "nom": "LE LOT NE TE FAIT PLUS PAYER", "detail": "RACHAT GRATUIT"},
        {"compte": 50, "type": "char", "valeur": "remorqueuse",
         "nom": "LA DEPANNEUSE EST A TOI", "detail": "GAREE A LA PLANQUE"},
    ),
}


def palier_prime(slug: str) -> float:
    """Le meilleur multiplicateur de prime qu'un boulot puisse donner."""
    return max([1.0] + [p["valeur"] for p in PALIERS.get(slug, ()) if p["type"] == "prime"])


def gain_avec_paliers(slug: str, tuiles: float | None = None) -> int:
    """Ce que le boulot rapporte a quelqu'un qui a TOUT debloque.

    ⚠️ C'est ce nombre-la que les juges d'equilibrage doivent regarder, pas
    celui du debutant : un palier qui fait passer un boulot devant tous les
    autres est un desequilibre qu'on a mis cinquante courses a fabriquer, et
    il ne se verrait nulle part si on ne mesurait que le premier jour.
    """
    boulot = BOULOTS[slug]
    if tuiles is None:
        tuiles = TUILES_TYPE
    par_etape = boulot["base"] + boulot["par_tuile"] * tuiles + boulot["prime"] * palier_prime(slug)
    return round(par_etape * boulot["etapes"])


# --- La dette de Rocco : une raison de se lever le matin -------------------

#: ⚠️ **Elle ne se rembourse pas a un comptoir**, et ce n'est pas une economie
#: de geographie : un shylock n'attend pas derriere une caisse, il ENVOIE DU
#: MONDE. Les rappels arrivent au telephone, puis les hommes de Sal te trouvent
#: ou que tu sois — et c'est a eux qu'on paie. La collecte est une scene, pas
#: un menu de plus dans une piece.
#:
#: ⚠️ **Deux bornes, et elles se tiennent.** La dette MONTE (sinon elle n'est
#: pas une dette, c'est une facture qu'on oublie) mais elle ne monte pas
#: indefiniment (`plafond`) : une dette qui double pendant qu'on dort n'est
#: plus une pression, c'est une partie perdue au reveil. Et l'interet d'une
#: seule journee doit rester sous ce qu'une journee de travail honnete
#: rapporte (`test_dette`) — sinon le taxi ne sert plus a rien et il n'y a
#: plus de decision, seulement une descente.
DETTE = {
    "montant": 15000,          # ce que Rocco devait a Sal « Le Barbier »
    "interet_par_jour": 0.02,  # 2 % par nuit, compose
    "plafond": 1.5,            # ... et jamais plus d'une fois et demie le capital
    "rappel_jour": 3,          # le telephone commence a sonner
    "collecte_jour": 6,        # ... puis ils viennent, et ils reviennent
    "hommes": 2,               # combien se presentent a la fois
    "prend": 0.30,             # ce qu'ils prennent dans tes poches s'ils t'attrapent
    "acompte_min": 500,        # le plus petit versement qu'ils acceptent
    "repit_s": 120,            # apres une visite, deux minutes de paix
}


def dette_du_lendemain(dette: int) -> int:
    """Ce que la nuit ajoute. ⚠️ Bornee : `plafond` fois le capital, jamais plus."""
    if dette <= 0:
        return 0
    plafond = round(DETTE["montant"] * DETTE["plafond"])
    return max(0, min(plafond, round(dette * (1 + DETTE["interet_par_jour"]))))


def jours_avant_le_plafond() -> int:
    """Combien de nuits il faut pour que la dette atteigne son plafond.

    ⚠️ Un juge exige que ce soit LONG : la dette doit peser sur une partie
    entiere, pas sur une nuit. Sinon ce n'est pas une raison de se lever le
    matin, c'est une partie perdue au reveil."""
    dette, plafond, jours = DETTE["montant"], round(DETTE["montant"] * DETTE["plafond"]), 0
    while dette < plafond and jours < 1000:
        dette = dette_du_lendemain(dette)
        jours += 1
    return jours


#: Ce que les proprietes rapportent en une journee, toutes reunies. ⚠️ C'est
#: l'etalon du travail honnete : le juge de la dette s'y compare, parce que
#: c'est le seul revenu du jeu qui se compte en dollars PAR JOUR et qui ne
#: depend pas de l'habilete du joueur.
def revenu_honnete_par_jour() -> int:
    return sum(p["revenu_par_jour"] for p in PROPRIETES)


# --- Les guichets : au camion, ou au skimmer -------------------------------

#: ⚠️ **Un guichet, c'est la caisse d'une banque posee dans la rue.** Deux
#: facons d'y toucher, et elles se repondent comme l'avocat et le hacker : le
#: CAMION est bruyant et immediat (deux etoiles, la caisse par terre, tout le
#: monde a vu) ; le SKIMMER est silencieux et lent (on paie d'avance chez
#: Josee, on revient le lendemain, et il peut avoir ete trouve entre-temps).
#:
#: ⚠️ `lourd` : il ne cede qu'a un char d'AU MOINS cette masse. Un camion (3,0)
#: ou un autobus (3,2) le defonce ; une berline (1,0), une luxe (1,8) et meme
#: la remorqueuse (2,2) s'y arretent — `test_argent_sale` tient la fiche des
#: chars et celle-ci d'accord. Sans cette borne, la premiere auto volee du
#: coin ouvrait un guichet, et « au camion » ne voulait plus rien dire.
#:
#: ⚠️ **Et ni l'un ni l'autre ne bat le taxi a l'heure** (`test_argent_sale`) :
#: la caisse d'un guichet vaut moins qu'une journee de travail honnete, et
#: trois skimmers poses ne rapportent pas, en moyenne, ce que le taxi fait
#: dans la meme journee. Sinon le jeu se joue tout seul.
GUICHET: dict = {
    "caisse": (300, 900),       # ce qui tombe par terre quand il cede
    "liasses": 6,               # ... en combien de liasses
    "lourd": 2.5,               # la masse qu'il faut pour le defoncer
    "ecart": 18,                # deux guichets ne se voisinent pas (tuiles)
    "par_ville": (10, 28),      # ce qu'une ville en pose — un juge le compte
    "skimmer": {
        "prix": 350,            # au marche noir, chez Josee
        "rendement": (350, 900),   # ce qu'il a lu pendant la nuit
        "trouve": 0.30,         # ... s'il n'a pas ete trouve entre-temps
        "max_poses": 3,         # pas plus a la fois : c'est un pari, pas un parc
    },
}


def esperance_skimmer() -> float:
    """Ce qu'un skimmer rapporte EN MOYENNE, prix paye et risque compris."""
    s = GUICHET["skimmer"]
    return (1 - s["trouve"]) * (s["rendement"][0] + s["rendement"][1]) / 2 - s["prix"]


# --- Les machines distributrices -------------------------------------------

#: ⚠️ **La petite soeur honnete du guichet.** La meme place dans la rue — contre
#: une devanture, sur l'abord, servie depuis la dalle — mais ce qu'elle garde,
#: c'est de la MONNAIE et des canettes, pas la caisse d'une banque. Ce qu'elle
#: vend pointe dans `TARIFS` (`magasins.DISTRIBUTRICES`) : une liqueur coute le
#: meme 3 $ a la machine qu'a la glaciere du depanneur, et la regle du
#: trottoir tient toute seule — au dollar, jamais mieux que le hot-dog.
#:
#: ⚠️ `coincee` : la chance qu'un achat reste pris dans la spirale. On a paye,
#: rien ne tombe, et l'invite devient BRASSER LA MACHINE — qui le fait tomber
#: une fois sur `brasser`. C'est ca, une machine distributrice : tout le monde
#: en a deja brasse une.
#:
#: ⚠️ Defoncee, elle crache sa `monnaie` en `tas` et `canettes` de sa
#: marchandise. Un delit a UNE etoile, et seulement si quelqu'un regarde
#: (`recherche.DELITS["distributrice"]`) : c'est du vandalisme, pas une banque.
#: Et un juge tient qu'une nuit a defoncer TOUTES les machines de la ville
#: rapporte moins qu'une journee honnete — la monnaie, c'est de la monnaie.
DISTRIBUTRICE: dict = {
    "monnaie": (4, 22),         # ce qui tombe quand elle cede, en $
    "tas": 3,                   # ... en combien de tas
    "canettes": 2,              # ce qu'elle recrache de sa marchandise
    "coincee": 0.15,            # un achat sur sept reste pris
    "brasser": 0.5,             # ... et une secousse sur deux le fait tomber
    "ecart": 10,                # deux machines ne se voisinent pas (tuiles)
    "ecart_guichet": 3,         # ni collees a un guichet : ACTION ne saurait pas lequel
    "par_district": 9,          # ... et pas toutes dans le meme quartier
    "par_ville": (16, 40),      # ce qu'une ville en pose — un juge le compte
}


# --- L'assurance : la fraude, et l'assureur qui enquete --------------------

#: Ti-Guy assure ce qui est gare devant sa porte, sans demander a qui c'est.
#: On paie la prime, le char disparait — brule, plie, coule — et on revient
#: ENCAISSER AU GARAGE : la fraude est une scene en trois actes, pas un menu.
#:
#: ⚠️ **Trois reclamations et l'assureur enquete** : plus de police pendant
#: `enquete_jours`, et une page au casier. C'est ce qui empeche la boucle
#: « voler, assurer, bruler » de tourner toute la journee.
#:
#: ⚠️ **La valeur couverte est BORNEE** (`valeur_max`) : sans ce plafond, une
#: luxe volee et assuree rapportait plus a l'heure que n'importe quel boulot
#: honnete. Et elle reste SOUS le prix neuf : frauder avec un char qu'on a
#: paye perd de l'argent — ce n'est payant qu'avec un char vole, et c'est
#: exactement ce qu'on veut dire. `cycle_s` est ce qu'une fraude prend AU
#: MOINS (voler, se rendre au garage, faire disparaitre, revenir) : c'est
#: l'horloge du juge, pas celle du jeu.
ASSURANCE: dict = {
    "valeur_fraction": 0.5,     # ce que la police couvre : la moitie du prix neuf...
    "valeur_max": 900,          # ... et jamais plus que ca
    "prime_fraction": 0.3,      # la prime, sur la valeur couverte
    "reclamations_max": 3,      # a la troisieme, l'assureur enquete
    "enquete_jours": 4,         # ... pendant ce temps, personne n'assure rien
    "enquete_pages": 1,         # ... et ca s'ecrit au casier
    "cycle_s": 300,             # ce qu'une fraude prend au moins (le juge)
}


def valeur_assuree(prix_neuf: int) -> int:
    """Ce que la police couvre, plafond compris."""
    return int(min(ASSURANCE["valeur_max"], round(prix_neuf * ASSURANCE["valeur_fraction"])))


def prime_assurance(prix_neuf: int) -> int:
    """Ce que Ti-Guy demande pour couvrir ce char."""
    return int(round(valeur_assuree(prix_neuf) * ASSURANCE["prime_fraction"]))


# --- La run : la contrebande de Sven, d'un district a l'autre -------------

#: ⚠️ **Acheter bas, vendre haut — c'est le coeur de Chinatown Wars**, et ici
#: il ne demande ni marchandise neuve ni personnage neuf : des caisses de
#: cigarettes et de boisson (⚠️ pas de drogue : le jeu se moque de la ville,
#: il ne vend pas ca), achetees a la cale du Norvegien sur les Quais et
#: revendues au comptoir de quatre commerces de la ville, au PRIX DU JOUR de
#: leur district — tire du jour et du district, le meme pour tous les
#: comptoirs d'un district, et il bouge chaque nuit.
#:
#: ⚠️ **Les caisses vont dans le COFFRE du char gare a cote** (`rayon_px`) :
#: la cale ne se porte pas, un char qui brule brule la run avec, et un char
#: saisi part au lot fouille — arrete avec des caisses, on les perd en entier.
#:
#: ⚠️ **Ce qui empeche la machine a argent** (`test_contrebande`) : le prix
#: d'achat MONTE avec ce qu'on a deja pris dans la journee (`hausse`), le
#: mauvais district fait PERDRE de l'argent (`facteur[0]` fois le prix de
#: vente reste sous le prix d'achat), et la marge d'une run complete — le
#: coffre plein, vendu au meilleur prix possible — reste sous la prime de la
#: plus grosse mission de l'arc, et sous le taxi a l'heure sur les `cycle_s`
#: qu'une run prend au moins. Un commerce qui paie mieux que l'histoire vide
#: l'histoire.
CONTREBANDE: dict = {
    "nom": "La cale du Norvégien",
    "marchandises": {
        "cigarettes": {"nom": "Cigarettes", "achat": 120, "vente": 170},
        "boisson": {"nom": "Boisson", "achat": 80, "vente": 110},
    },
    "hausse": 0.10,             # +10 % par caisse deja achetee dans la journee
    "caisses_max": 8,           # ce qu'un coffre prend
    "facteur": (0.7, 1.3),      # le prix du jour, en fraction du prix de vente
    "comptoirs": ("depanneur", "bar", "cantine", "casse_croute"),   # qui en prend
    "rayon_px": 90,             # le char doit etre gare a ca de la cale
    "cycle_s": 240,             # ce qu'une run prend au moins (le juge)
}


def prix_achat(slug: str, deja: int) -> int:
    """Le prix d'une caisse a la cale, `deja` caisses achetees aujourd'hui."""
    m = CONTREBANDE["marchandises"][slug]
    return int(round(m["achat"] * (1 + CONTREBANDE["hausse"] * max(0, deja))))


def marge_max_run() -> int:
    """La meilleure run possible : le coffre plein d'une seule marchandise,
    vendu au meilleur prix du jour qui existe."""
    haut, meilleur = CONTREBANDE["facteur"][1], 0
    for slug, m in CONTREBANDE["marchandises"].items():
        gain = sum(int(round(m["vente"] * haut)) - prix_achat(slug, k)
                   for k in range(CONTREBANDE["caisses_max"]))
        meilleur = max(meilleur, gain)
    return meilleur


# --- Effacer le casier : la certitude, ou le pari -------------------------

#: ⚠️ **Deux comptoirs qui n'ont de sens que l'un contre l'autre.** Un seul
#: serait un bouton « annuler la partie » ; deux, c'est un choix, et c'est le
#: choix qui est le jeu. L'avocat est LEGAL, CHER, SUR : une page, tout de
#: suite, une fois par jour. Le hacker est LE PARI : moins cher a sortir de
#: sa poche, mais on paie D'AVANCE, on revient LE LENDEMAIN, et on ne sait
#: pas ce qu'on aura achete — de rien du tout a trois pages d'un coup, et
#: parfois une page DE PLUS parce qu'il s'est fait prendre les doigts dedans.
#:
#: ⚠️ **Le prix monte avec l'epaisseur du dossier** (`par_page`) : sans ca,
#: un casier de vingt pages se nettoyait au meme tarif qu'un casier de deux,
#: et les vingt pages ne voulaient plus rien dire. C'est la meme regle que
#: l'amende, et c'est voulu : tout ce qui touche au casier se paie au poids.
#:
#: ⚠️ **Et effacer coute TOUJOURS plus cher que ce que la page coute**
#: (`test_effacer`) : le jour ou nettoyer son dossier revient moins cher que
#: de le porter, plus personne ne le porte, et tout M11 tombe avec.
EFFACER: dict = {
    # Me Desjardins, au fond du Brouillard. Il ne travaille pas deux fois le
    # meme jour — c'est ce qui empeche d'acheter vingt pages d'affilee.
    "avocat": {
        "nom": "ME DESJARDINS",
        "prix": 1200,
        "par_page": 400,
        "pages": 1,
        "par_jour": 1,
        # ⚠️ L'AUTRE MOITIE DE CE QU'IL VEND : « il efface une page du casier
        # OU te sort de prison sans amende ». Une provision retenue d'avance,
        # qui efface l'amende de la PROCHAINE arrestation — une seule.
        #
        # ⚠️ Elle ne touche a rien d'autre : la page s'ajoute quand meme, les
        # armes partent quand meme, le char va quand meme au lot, et la nuit
        # passe quand meme. Un avocat sort son client de prison ; il ne le
        # rend pas innocent. Sans ca, se faire arreter exprès deviendrait un
        # trajet gratuit vers le poste.
        #
        # ⚠️ Et elle coute plus cher qu'une arrestation ordinaire (`test_effacer`) :
        # elle n'est payante que pour les grosses nuits, celles a quatre ou
        # cinq etoiles. Une assurance qui rapporte toujours n'est pas une
        # assurance, c'est un salaire.
        "provision": 800,
        "provision_par_page": 300,
    },
    # Le hacker de La Shop. Le tirage se lit « autant de pages, autant de
    # chances » — un nombre NEGATIF est une page de PLUS au dossier.
    "hacker": {
        "nom": "LA SHOP",
        "prix": 700,
        # ⚠️ Une pente PLUS RAIDE que celle de l'avocat, et ce n'est pas un
        # detail de tarif : a 200 $ la page, le rapport se retournait vers le
        # haut du dossier — a vingt pages le pari devenait la meilleure affaire
        # au dollar, et l'avocat ne servait plus a rien pile au moment ou l'on
        # a le plus besoin de lui. Plus le dossier est epais, plus la certitude
        # vaut son prix : c'est ce que dit cette pente.
        "par_page": 260,
        "delai_jours": 1,
        "tirage": ((-1, 0.20), (0, 0.32), (1, 0.28), (2, 0.14), (3, 0.06)),
    },
}


def prix_effacer(quoi: str, casier: int) -> int:
    """Ce que le comptoir demande, dossier en main. Jamais negatif."""
    fiche = EFFACER[quoi]
    casier = max(0, min(CASIER_MAX, casier))
    return max(0, round(fiche["prix"] + fiche["par_page"] * casier))


def prix_provision(casier: int) -> int:
    """Ce que l'avocat demande pour etre la a la prochaine arrestation."""
    fiche = EFFACER["avocat"]
    casier = max(0, min(CASIER_MAX, casier))
    return max(0, round(fiche["provision"] + fiche["provision_par_page"] * casier))


def esperance_hacker() -> float:
    """Les pages qu'il efface EN MOYENNE — la page ajoutee comptee en moins."""
    return sum(pages * chance for pages, chance in EFFACER["hacker"]["tirage"])



def amende(argent: int, etoiles: int, casier: int) -> int:
    """Ce que la prison prend. Jamais plus que ce qu'on a, jamais negatif."""
    etoiles = max(1, min(len(AMENDE_BASE), etoiles))
    casier = max(0, min(CASIER_MAX, casier))
    montant = round(AMENDE_BASE[etoiles - 1] * (1 + AMENDE_PAR_CASIER * casier))
    return max(0, min(argent, montant))


def pot_de_vin(etoiles: int, casier: int) -> int:
    etoiles = max(1, min(5, etoiles))
    casier = max(0, min(CASIER_MAX, casier))
    return round(POT_DE_VIN_BASE * etoiles * (1 + AMENDE_PAR_CASIER * casier))


def facture_hopital(argent: int) -> int:
    montant = round(argent * HOPITAL["fraction"])
    return max(0, min(argent, max(HOPITAL["minimum"], min(HOPITAL["maximum"], montant))))


# --- Revenus ---------------------------------------------------------------

TARIFS = {
    "pickpocket_min": 5,
    "pickpocket_max": 25,
    "cash_sol_min": 5,
    "cash_sol_max": 25,
    "paquet": 50,
    "paquets_prime_10": 500,
    "paquets_prime_20": 1500,
    "silence_temoin": 20,
    "sergent_efface_etoile": 150,
    "hotdog": 10,
    "hotdog_pv": 25,
    "hotdog_souffle": 40,
    "poutine": 18,
    "poutine_pv": 45,
    "poutine_souffle": 70,
    "journal": 2,
    # Les comptoirs des commerces ordinaires (`magasins.COMPTOIRS`). ⚠️ Tous
    # moins bons au dollar que le kiosque a hot-dogs : un depanneur depanne, il
    # ne nourrit pas. Ce qu'on achete ici, on l'achete parce qu'on est DEVANT,
    # pas parce que c'est une aubaine — c'est la porte a cote qui a de la
    # valeur, pas le sandwich.
    "sandwich": 8,
    "sandwich_pv": 20,
    "sandwich_souffle": 30,
    "biere": 8,
    "biere_pv": 8,
    "biere_souffle": 35,
    "friture": 14,
    "friture_pv": 35,
    "friture_souffle": 55,
    # Les fruits de mer (la cabane du port et le comptoir des poissonneries).
    # ⚠️ Meme regle que le reste du trottoir : au dollar, jamais mieux que le
    # hot-dog (6,5 points par dollar) — la guedille vaut 6,25, les crevettes
    # 6,25. On les achete parce qu'on est aux Quais, pas parce que c'est
    # une aubaine. Et c'est sur EUX que porte le coupon de l'homme-sandwich
    # (`magasins.RECLAME`) : a moitie prix, ils deviennent la meilleure bouchee
    # de la ville — pour une fois, et a trois minutes de marche.
    "guedille": 16,
    "guedille_pv": 40,
    "guedille_souffle": 60,
    "crevettes": 12,
    "crevettes_pv": 30,
    "crevettes_souffle": 45,
    "chaudree": 10,
    "chaudree_pv": 28,
    "chaudree_souffle": 35,
    # De quoi manger et boire PARTOUT ou ca a du sens (demande de Martin) : la
    # soupe et le pate chinois du casse-croute, la pointe de tarte, la liqueur
    # de la glaciere a cote de la caisse (meme chez le quincaillier), les
    # chips et la barre de chocolat du depanneur, les ailes et le shooter du
    # bar, le jus d'orange de la pharmacie. Toujours la meme borne : au dollar,
    # jamais mieux que le hot-dog (6,5) — un juge fait la division.
    "soupe": 7,
    "soupe_pv": 20,
    "soupe_souffle": 25,
    "pate_chinois": 12,
    "pate_chinois_pv": 35,
    "pate_chinois_souffle": 40,
    "tarte": 5,
    "tarte_pv": 12,
    "tarte_souffle": 18,
    "liqueur": 3,
    "liqueur_pv": 4,
    "liqueur_souffle": 15,
    "chips": 3,
    "chips_pv": 6,
    "chips_souffle": 12,
    "chocolat": 2,
    "chocolat_pv": 4,
    "chocolat_souffle": 8,
    "beigne": 3,
    "beigne_pv": 8,
    "beigne_souffle": 10,
    "ailes": 12,
    "ailes_pv": 30,
    "ailes_souffle": 45,
    "shooter": 5,
    "shooter_pv": 3,
    "shooter_souffle": 25,
    "jus": 4,
    "jus_pv": 12,
    "jus_souffle": 12,
    "pilules": 20,
    "pilules_pv": 50,
    "coupe": 12,
    # Les tiroirs d'un logement ou l'on n'habite pas. Une fois par adresse.
    "fouille_min": 10,
    "fouille_max": 60,
    "cafe": 4,
    "cafe_pv": 10,
    "cafe_souffle": 30,
    # ⚠️ La compagnie se paie et ne se montre pas : un fondu, une replique,
    # de la vie qui revient. Elle refuse quand la police te cherche.
    "compagnie": 60,
    "compagnie_pv": 40,
}

#: Manger rend des PV *et* du souffle (`*_souffle`, sur les 100 d'endurance de
#: `recherche.VITESSES`) : une poutine a 18 $ vaut deux hot-dogs, en vie comme
#: en jambes. Sans ca, le seul moyen de reprendre son souffle etait d'arreter
#: de courir — un kiosque ne servait a rien quand on est poursuivi.
#:
#: ⚠️ Le cafe, lui, ne nourrit pas : il TIENT DEBOUT. Pendant `duree_s`
#: secondes, le sprint ne coute que `depense` de ce qu'il coute d'habitude —
#: on sprinte DEUX FOIS PLUS LONGTEMPS, jamais plus vite.
#:
#: ⚠️ La vitesse, c'est ce qui separe le joueur du policier, et y toucher
#: casserait toutes les poursuites du jeu. Depuis que la COURSE est gratuite
#: et que le policier court aussi vite (2,0), le cafe ne sert plus a « courir
#: un peu plus longtemps » : il sert a S'ECHAPPER. C'est une bien meilleure
#: raison de s'arreter au kiosque.
CAFE = {"duree_s": 90, "depense": 0.5}

#: Le souffle en SURPLUS : ce que manger ajoute PAR-DESSUS les 100 points de la
#: barre quand elle est deja pleine.
#:
#: ⚠️ Sans lui, manger ne servait a rien — et le depot s'etait deja donne la
#: raison inverse sans qu'elle tienne un jour. Le sprint coute 0,4 par image, et
#: des qu'on arrete de courir le souffle remonte de 0,4 x 0,6 = 0,24 : une barre
#: vide se remplit TOUTE SEULE en sept secondes. Une poutine a 18 $ rendait donc
#: 70 points qu'on aurait eus gratuitement en s'arretant quatre secondes.
#:
#: Le surplus est exactement ce que la regeneration ne peut pas donner : il se
#: depense EN PREMIER, il ne revient JAMAIS tout seul, et il se perd en dormant,
#: a l'hopital et en prison — comme tout ce qui est passager.
#:
#: ⚠️ `surplus_max` est un reglage de POURSUITE, pas de confort. Le joueur
#: sprinte a 2,1 et le policier court a 1,9 : chaque point de surplus est de
#: l'avance qu'on ne peut pas lui reprendre. A 0,4 par image, 60 points valent
#: 2,5 s de sprint de plus — et 5 s sous cafe, qui divise la depense par deux.
#: `surplus_secondes_max` est le budget qu'on s'autorise, cafe compris, et un
#: juge refait le calcul a chaque fois qu'on touche a l'un des trois nombres.
SOUFFLE = {"surplus_max": 60, "surplus_secondes_max": 6}

#: La sieste : DORMIR JUSQU'AU SOIR, sur le lit de la planque, de l'hotel ou
#: du phare. On se reveille a `reveil` (20 h 45) le MEME jour, avec `soin` de
#: la vie maximum en plus — une sieste n'est pas une nuit, elle ne rend pas tout.
#:
#: ⚠️ `reveil` tombe APRES `clignotant_depuis` (vehicules.py) : c'est l'heure ou
#: la ville a fini de passer a la nuit — lampadaires allumes, feux au
#: clignotant, `estNuit()` vrai. Un reveil a la brune laisserait le joueur
#: devant « ATTENDS LA NUIT » encore une minute, et c'est exactement l'attente
#: qu'on voulait supprimer. Trop tard, et la sieste mangerait la nuit qu'elle
#: est venue chercher. Un juge tient les deux bouts.
SIESTE = {"reveil": 0.865, "soin": 0.25}

# --- Les boulots au klaxon (M9) -------------------------------------------

#: ⚠️ UN boulot = UNE fiche. La v1 avait les trois nombres du taxi perdus dans
#: `TARIFS` ; a quatre boulots, ca faisait douze nombres sans parente qu'aucun
#: test ne pouvait comparer entre eux. Ici, chaque boulot se lit en une ligne
#: et le juge d'equilibrage les met cote a cote.
#:
#: `base`        ce qu'on touche en finissant, quoi qu'il arrive
#: `par_tuile`   ce que la DISTANCE ajoute (a parcourir, pas a vol d'oiseau)
#: `prime`       le bonus qu'on perd en route (pourboire, pizza froide, mort)
#: `etapes`      combien de fois de suite (la pizza : trois livraisons)
#: `chrono_s`    0 = pas de chrono ; sinon le temps avant que la prime fonde
#: `malus_choc`  ce qu'un choc mange de la prime (le taxi : trois chocs, rien)


class Boulot(TypedDict):
    slug: str
    nom: str
    vehicule: str
    base: int
    par_tuile: float
    prime: int
    etapes: int
    chrono_s: int
    malus_choc: float


BOULOTS: dict[str, Boulot] = {
    "taxi": {"slug": "taxi", "nom": "Course", "vehicule": "taxi",
             "base": 15, "par_tuile": 0.25, "prime": 15,
             "etapes": 1, "chrono_s": 0, "malus_choc": 0.34},
    # ⚠️ La pizza refroidit : la prime fond du depart de la livraison jusqu'a
    # `chrono_s`, puis il ne reste que la base. C'est la seule pression du
    # boulot — il n'y a rien a perdre d'autre qu'un pourboire.
    "pizza": {"slug": "pizza", "nom": "Livraison", "vehicule": "moto",
              "base": 20, "par_tuile": 0.2, "prime": 14,
              "etapes": 3, "chrono_s": 50, "malus_choc": 0.0},
    # Le blesse, lui, se perd pour de bon : la prime est sa vie.
    "ambulance": {"slug": "ambulance", "nom": "Ambulance", "vehicule": "ambulance",
                  "base": 40, "par_tuile": 0.3, "prime": 60,
                  "etapes": 1, "chrono_s": 100, "malus_choc": 0.2},
    # La fourriere paie pour les epaves : pas de prime, mais la meilleure base.
    "remorquage": {"slug": "remorquage", "nom": "Remorquage", "vehicule": "remorqueuse",
                   "base": 70, "par_tuile": 0.4, "prime": 0,
                   "etapes": 1, "chrono_s": 0, "malus_choc": 0.0},
}

#: La course type qui sert a COMPARER les boulots entre eux (en tuiles). Elle
#: ne sert a rien en jeu : le paiement se calcule sur la vraie distance.
TUILES_TYPE = 60


def gain_boulot(boulot: Boulot, tuiles: float = TUILES_TYPE, parfait: bool = True) -> int:
    """Ce qu'un boulot rapporte, toutes etapes faites."""
    par_etape = boulot["base"] + boulot["par_tuile"] * tuiles + (boulot["prime"] if parfait else 0)
    return round(par_etape * boulot["etapes"])


# --- La fourriere ----------------------------------------------------------

#: Un char mal gare, ou saisi a l'arrestation, part au lot. On le rachete au
#: comptoir — ou on le reprend par-dessus la cloture, et le lot appelle.
#:
#: ⚠️ Le rachat DOIT couter plus cher que la revente du meme char au garage
#: (`VENTE_FRACTION`), sinon la fourriere devient une machine a argent : on y
#: fait saisir un char pour le racheter moins cher qu'il ne se revend.
FOURRIERE = {
    "rachat_fraction": 0.40,
    "rachat_minimum": 150,
    "places": 6,              # ce que le lot garde ; au-dela, le plus vieux part
    "etoiles_vol": 1,         # reprendre son char sans payer
    "gardiens": 2,            # les gars du lot, qui ripostent
    # ⚠️ Le temps qu'on laisse a un char MAL GARE avant que la remorqueuse
    # passe. Il n'est pas la pour etre gentil : sans delai, descendre deux
    # secondes sur un passage pieton couterait le prix d'un rachat, et plus
    # personne n'oserait s'arreter. Assez long pour faire une course, assez
    # court pour qu'on sente qu'on est mal gare.
    "remorquage_s": 45,
}


def prix_rachat(prix_neuf: int) -> int:
    return max(FOURRIERE["rachat_minimum"], round(prix_neuf * FOURRIERE["rachat_fraction"]))


#: Vente d'un vehicule vole au garage clandestin : fraction du prix neuf, en
#: proportion des points de vie restants, moins 20 % par doublon du meme jour.
VENTE_FRACTION = 0.25
VENTE_MALUS_DOUBLON = 0.20
REPARATION_PAR_PV = 2
REPEINTE = 100


def prix_vente(prix_neuf: int, vie: int, vie_max: int, doublons: int) -> int:
    if vie_max <= 0:
        return 0
    part = max(0.0, min(1.0, vie / vie_max))
    facteur = max(0.0, 1 - VENTE_MALUS_DOUBLON * doublons)
    return max(0, round(prix_neuf * VENTE_FRACTION * part * facteur))


# --- Proprietes -------------------------------------------------------------


class Propriete(TypedDict):
    slug: str
    nom: str
    district: str
    lieu: str
    prix: int
    revenu_par_jour: int
    phase: int


PROPRIETES: list[Propriete] = [
    {"slug": "kiosque", "nom": "Kiosque de Madame Thibodeau", "district": "faubourg",
     "lieu": "kiosque", "prix": 800, "revenu_par_jour": 80, "phase": 1},
    {"slug": "bar", "nom": "Bar Le Brouillard", "district": "faubourg",
     "lieu": "bar", "prix": 2500, "revenu_par_jour": 200, "phase": 1},
    {"slug": "garage", "nom": "Garage Rocco Bandini", "district": "faubourg",
     "lieu": "garage", "prix": 4500, "revenu_par_jour": 350, "phase": 1},
    {"slug": "hotel", "nom": "Hôtel Bandini", "district": "quais",
     "lieu": "hotel", "prix": 10000, "revenu_par_jour": 600, "phase": 2},
]

#: La caisse d'une propriete s'accumule sur place et plafonne : il faut aller
#: la chercher, ce qui cree des trajets, donc du risque.
CAISSE_JOURS_MAX = 3


def retour_sur_investissement_min(p: Propriete) -> float:
    """En minutes de jeu reel."""
    return p["prix"] / p["revenu_par_jour"] * JOUR_SECONDES / 60


def _table_des_dettes() -> list[int]:
    table, dette = [DETTE["montant"]], DETTE["montant"]
    for _ in range(jours_avant_le_plafond() + 2):
        dette = dette_du_lendemain(dette)
        table.append(dette)
    return table


def exporter() -> dict:
    return {
        "argent_depart": ARGENT_DEPART,
        "fortune_max": FORTUNE_MAX,
        "jour_secondes": JOUR_SECONDES,
        "casier_max": CASIER_MAX,
        # amendes[etoiles-1][casier] — deja calculees, le navigateur indexe.
        "amendes": [
            [amende(FORTUNE_MAX, e, c) for c in range(CASIER_MAX + 1)]
            for e in range(1, len(AMENDE_BASE) + 1)
        ],
        "pots_de_vin": [
            [pot_de_vin(e, c) for c in range(CASIER_MAX + 1)] for e in range(1, 6)
        ],
        "pot_de_vin_accepte": list(POT_DE_VIN_ACCEPTE),
        "pot_de_vin_ami_max": POT_DE_VIN_AMI_MAX,
        "hopital": dict(HOPITAL),
        "tarifs": dict(TARIFS),
        "cafe": dict(CAFE),
        "souffle": dict(SOUFFLE),
        "sieste": dict(SIESTE),
        "boulots": {k: dict(v) for k, v in BOULOTS.items()},
        "fourriere": dict(FOURRIERE),
        "tuiles_type": TUILES_TYPE,
        "vente_fraction": VENTE_FRACTION,
        "vente_malus_doublon": VENTE_MALUS_DOUBLON,
        "reparation_par_pv": REPARATION_PAR_PV,
        "repeinte": REPEINTE,
        "proprietes": PROPRIETES,
        "caisse_jours_max": CAISSE_JOURS_MAX,
        "dette": dict(DETTE),
        "guichet": {**GUICHET, "caisse": list(GUICHET["caisse"]), "par_ville": list(GUICHET["par_ville"]),
                    "skimmer": {**GUICHET["skimmer"], "rendement": list(GUICHET["skimmer"]["rendement"])}},
        "distributrice": {**DISTRIBUTRICE, "monnaie": list(DISTRIBUTRICE["monnaie"]),
                          "par_ville": list(DISTRIBUTRICE["par_ville"])},
        "assurance": dict(ASSURANCE),
        "contrebande": {**CONTREBANDE, "facteur": list(CONTREBANDE["facteur"]),
                        "comptoirs": list(CONTREBANDE["comptoirs"]),
                        "marchandises": {k: dict(v) for k, v in CONTREBANDE["marchandises"].items()}},
        "paliers": {slug: [dict(p) for p in liste] for slug, liste in PALIERS.items()},
        # dettes[n] = ce que la dette vaut apres n nuits sans payer — le
        # navigateur n'a plus qu'a indexer, et la borne est deja dedans.
        "dettes": _table_des_dettes(),
        "effacer": {
            quoi: {**fiche, "tirage": [list(t) for t in fiche["tirage"]]}
            if "tirage" in fiche else dict(fiche)
            for quoi, fiche in EFFACER.items()
        },
        "prix_provision": [prix_provision(c) for c in range(CASIER_MAX + 1)],
        # prix_effacer[quoi][casier] — deja calcule, le navigateur indexe.
        "prix_effacer": {
            quoi: [prix_effacer(quoi, c) for c in range(CASIER_MAX + 1)]
            for quoi in EFFACER
        },
    }
