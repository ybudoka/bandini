"""La mission t12 — voir app/missions/__init__.py pour le moteur.

Une gageure avec le livreur (M16, arc T, les petites jobs — 1er oct. 2026). Un livreur du Faubourg, très sûr de lui :
« vingt piasses que tu te rends pas à l'hôpital en moins d'une minute ». Une course (`course`, un point, le chrono),
puis revenir chercher son dû. Un passant qui donne une job (`passant`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t12",
    "titre": "Une gageure avec le livreur",
    "donneur": "passant",
    "prerequis": ["m6"],
    "recompense": 70,
    "passant": {"archetype": "livreur", "district": "faubourg", "nom": "Le livreur"},
    "donne": {"message": "LE LIVREUR A PERDU SA GAGEURE"},

    # L'hôpital est un lieu de mission (rien ne bouge). ⚠️ `contre` n'est lu par personne : on court contre la montre
    # — la gageure, c'est le chrono.
    "objectifs": [
        {"type": "course", "texte": "L'HÔPITAL EN MOINS D'UNE MINUTE ET QUART", "points": ["hopital"], "rayon": 4,
         "chrono_s": 75},
        {"type": "retourner", "texte": "VA CHERCHER TA GAGEURE AU LIVREUR"},
    ],

    # Le jeu (`jeu=`) — le livreur : fanfaron, puis mauvais perdant, puis beau joueur malgré lui.
    "dialogue": {
        "hele": [
            _l("passant", "Hé, le pilote!", jeu="[teasing] Hé, le pilote!")
        ],
        "intro": [
            _l("passant", "Moi, je livre l'hôpital en une minute et quart, avec la soupe chaude. Toi?",
               jeu="[smugly] Moi, je livre l'hôpital en une minute et quart, avec la soupe chaude. [teasing] Toi?"),
            _l("passant", "Soixante-dix piasses que t'es pas capable. Je chronomètre, vas-y!",
               jeu="[playfully] Soixante-dix piasses que t'es pas capable. [excited] Je chronomètre, vas-y!")
        ],
        "pendant": [
            _p("passant", "Le chrono roule! Pis prends pas les trottoirs, c'est de la triche.", 0,
               jeu="[shouting] Le chrono roule! [teasing] Pis prends pas les trottoirs, c'est de la triche."),
            _p("passant", "Hein? Déjà? Viens chercher ton argent, avant que je change d'idée.", 1,
               jeu="[surprised] Hein? Déjà? [annoyed] Viens chercher ton argent, avant que je change d'idée.")
        ],
        "fin": [
            _l("passant", "Soixante-dix. Dis-le à personne, j'ai une réputation dans le Faubourg.",
               jeu="[annoyed] Soixante-dix. [nervously] Dis-le à personne, j'ai une réputation dans le Faubourg.")
        ],
        "echec": [
            _l("passant", "Ha! Trop lent! Garde ton argent, la leçon est gratuite.",
               jeu="[amused] Ha! Trop lent! [smugly] Garde ton argent, la leçon est gratuite.")
        ]
    }
}
