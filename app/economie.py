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
    "taxi_base": 15,
    "taxi_par_tuile": 0.25,
    "taxi_pourboire_max": 15,
    "pizza": 25,
    "pizza_prime_rapide": 10,
    "ambulance": 40,
    "ambulance_vivant": 60,
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
    "poutine": 18,
    "poutine_pv": 45,
    "journal": 2,
    "cafe": 4,
    "cafe_pv": 10,
    # ⚠️ La compagnie se paie et ne se montre pas : un fondu, une replique,
    # de la vie qui revient. Elle refuse quand la police te cherche.
    "compagnie": 60,
    "compagnie_pv": 40,
}

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
        "vente_fraction": VENTE_FRACTION,
        "vente_malus_doublon": VENTE_MALUS_DOUBLON,
        "reparation_par_pv": REPARATION_PAR_PV,
        "repeinte": REPEINTE,
        "proprietes": PROPRIETES,
        "caisse_jours_max": CAISSE_JOURS_MAX,
    }
