"""La police : ce qu'elle voit, ce qu'elle retient, comment elle repond.

Regle de base : **rien n'est compte tant que ce n'est pas detecte**. Trois
canaux : le CONE (un policier voit directement), le TEMOIN (un pieton court
jusqu'a un policier et lui donne ta derniere position connue) et l'ALARME (un
son, dans un rayon, sans cone).
"""

from __future__ import annotations

from typing import TypedDict

TUILE_PX = 16


class Palier(TypedDict):
    etoiles: int
    agents_pied: int
    autos: int
    tirent: bool
    barrages: bool
    helico: bool
    decroissance_s: int


#: Index = nombre d'etoiles. `decroissance_s` : secondes hors de vue avant de
#: perdre UNE etoile.
PALIERS: list[Palier] = [
    {"etoiles": 0, "agents_pied": 0, "autos": 0, "tirent": False, "barrages": False,
     "helico": False, "decroissance_s": 0},
    {"etoiles": 1, "agents_pied": 1, "autos": 0, "tirent": False, "barrages": False,
     "helico": False, "decroissance_s": 15},
    {"etoiles": 2, "agents_pied": 2, "autos": 0, "tirent": False, "barrages": False,
     "helico": False, "decroissance_s": 25},
    {"etoiles": 3, "agents_pied": 2, "autos": 1, "tirent": True, "barrages": False,
     "helico": False, "decroissance_s": 40},
    {"etoiles": 4, "agents_pied": 2, "autos": 2, "tirent": True, "barrages": False,
     "helico": False, "decroissance_s": 60},
    {"etoiles": 5, "agents_pied": 3, "autos": 3, "tirent": True, "barrages": True,
     "helico": True, "decroissance_s": 90},
]

ETOILES_MAX = len(PALIERS) - 1

#: Chaleur ajoutee par point de gravite d'un crime VU ; a 100, une etoile.
CHALEUR_PAR_GRAVITE = 35
CHALEUR_ETOILE = 100

#: Etoiles ajoutees par delit (gravite), et si un temoin est necessaire.
DELITS: dict[str, dict] = {
    "pickpocket": {"etoiles": 1, "temoin": True},
    "vol_vehicule": {"etoiles": 1, "temoin": True},
    "carjacking": {"etoiles": 2, "temoin": False},
    "coup_pieton": {"etoiles": 1, "temoin": True},
    "mort_pieton": {"etoiles": 2, "temoin": True},
    "renversement": {"etoiles": 1, "temoin": True},
    "renversement_mortel": {"etoiles": 2, "temoin": True},
    "arme_sortie": {"etoiles": 1, "temoin": False},
    "coup_policier": {"etoiles": 2, "temoin": False},
    "mort_policier": {"etoiles": 3, "temoin": False},
    "conduite_dangereuse": {"etoiles": 1, "temoin": False},
    "explosion": {"etoiles": 2, "temoin": True},
    "guichet": {"etoiles": 2, "temoin": False},
    "effraction": {"etoiles": 1, "temoin": True},
    "pot_de_vin_refuse": {"etoiles": 1, "temoin": False},
}

#: Cones de vision : demi-angle en degres et portee en tuiles, jour / nuit.
VISION = {
    "policier": {"angle": 45, "jour": 9, "nuit": 6},
    "auto_police": {"angle": 30, "jour": 14, "nuit": 12},
    "pieton": {"angle": 60, "jour": 6, "nuit": 4},
    "helico": {"angle": 180, "jour": 25, "nuit": 20},
    "alarme_rayon": 12,
    "explosion_rayon": 15,
    "delai_reperage_s": 0.6,
}

TEMOINS = {
    "rayon_tuiles": 9,
    "proba_fuit": 0.6,
    "proba_temoin": 0.3,
    "proba_fige": 0.1,
    "cherche_policier_tuiles": 40,
    "oubli_s": 30,
    "proba_telephone": 0.3,
    "delai_depeche_s": 8,
}

#: Changer de vehicule hors de vue pendant ce temps : -1 etoile. Changer de
#: linge : remise a zero jusqu'a `vetements_remise_max`, sinon -2.
DEGUISEMENT = {"vehicule_s": 3, "vehicule_etoiles": 1, "vetements_remise_max": 3,
               "vetements_etoiles": 2}

#: Le pieton court a 1,7 px/image et le policier a 1,9 : le joueur (2,1 en
#: sprint) peut fuir, mais son endurance (100, -0,4/image) ne dure que 4 s.
VITESSES = {"joueur_marche": 1.2, "joueur_sprint": 2.1, "pieton": 0.8, "pieton_course": 1.7,
            "policier": 1.9, "endurance": 100, "endurance_par_image": 0.4}


def exporter() -> dict:
    return {
        "tuile_px": TUILE_PX,
        "paliers": PALIERS,
        "etoiles_max": ETOILES_MAX,
        "chaleur_par_gravite": CHALEUR_PAR_GRAVITE,
        "chaleur_etoile": CHALEUR_ETOILE,
        "delits": DELITS,
        "vision": VISION,
        "temoins": TEMOINS,
        "deguisement": DEGUISEMENT,
        "vitesses": VITESSES,
    }
