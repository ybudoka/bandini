"""La mission t15 — voir app/missions/__init__.py pour le moteur.

L'autobus manqué (M16, arc T, les petites jobs — 1er oct. 2026). Un passant du Faubourg a vu partir son autobus : il
commence son quart à la fourrière dans une minute et demie, et Gilles ne pardonne pas les retards. Le mener
(`proteger` : il te suit, ou monte dans ton char) avant le chrono. Un passant qui donne une job (`passant`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t15",
    "titre": "L'autobus manqué",
    "donneur": "passant",
    "prerequis": ["m6"],
    "recompense": 40,
    "passant": {"archetype": "passant", "district": "faubourg", "nom": "Le retardataire"},
    "donne": {"message": "IL A POINÇONNÉ À L'HEURE"},

    # ⚠️ Pas l'usine (sa cour ferme la nuit : jamais un lieu de mission) : la fourrière, déjà un lieu de mission.
    "objectifs": [
        {"type": "proteger", "texte": "MÈNE-LE À LA FOURRIÈRE AVANT SON QUART", "cible": "passant",
         "lieu": "fourriere", "rayon": 6, "chrono_s": 100},
    ],

    # Le jeu (`jeu=`) — le retardataire : paniqué, essoufflé, et une excuse de prête pour chaque minute.
    "dialogue": {
        "hele": [
            _l("passant", "Attends-moi!", jeu="[nervously] Attends-moi!")
        ],
        "intro": [
            _l("passant", "Mon autobus est parti sous mon nez. Mon quart à la fourrière commence dans une minute et demie!",
               jeu="[nervously] Mon autobus est parti sous mon nez. [worried] Mon quart à la fourrière commence dans une minute et demie!"),
            _l("passant", "Gilles pardonne pas les retards. La dernière fois, il m'a fait laver la remorqueuse à la brosse à dents.",
               jeu="[worried] Gilles pardonne pas les retards. [sighs] La dernière fois, il m'a fait laver la remorqueuse à la brosse à dents.")
        ],
        "pendant": [
            _p("passant", "Plus vite! Non, moins vite! Non, plus vite!", 0,
               jeu="[shouting] Plus vite! [nervously] Non, moins vite! [shouting] Non, plus vite!")
        ],
        "fin": [
            _l("passant", "Huit heures pile! Tiens, quarante piasses. Ma brosse à dents te remercie.",
               jeu="[relieved] Huit heures pile! [amused] Tiens, quarante piasses. Ma brosse à dents te remercie.")
        ],
        "echec": [
            _l("passant", "En retard. Bon. Je vais aller me chercher une brosse à dents.",
               jeu="[disappointed] En retard. [sighs] Bon. Je vais aller me chercher une brosse à dents.")
        ]
    }
}
