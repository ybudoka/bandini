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
#: on court DEUX FOIS PLUS LONGTEMPS, jamais plus vite. La vitesse, c'est ce
#: qui separe le joueur (2,1) du policier (1,9) et de la foule ; y toucher
#: pour 4 $ casserait toutes les poursuites du jeu. La duree, non : elle
#: s'ecoule meme au volant, et elle ne s'empile pas (un deuxieme cafe repart
#: la minuterie).
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
    }
