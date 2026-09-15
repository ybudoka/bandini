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
        "boulots": {k: dict(v) for k, v in BOULOTS.items()},
        "fourriere": dict(FOURRIERE),
        "tuiles_type": TUILES_TYPE,
        "vente_fraction": VENTE_FRACTION,
        "vente_malus_doublon": VENTE_MALUS_DOUBLON,
        "reparation_par_pv": REPARATION_PAR_PV,
        "repeinte": REPEINTE,
        "proprietes": PROPRIETES,
        "caisse_jours_max": CAISSE_JOURS_MAX,
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
