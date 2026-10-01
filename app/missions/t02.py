"""La mission t02 — voir app/missions/__init__.py pour le moteur.

Le lunch des gars (M16, arc T, les petites jobs — 1er oct. 2026). Un débardeur des Quais, qui ne peut pas lâcher son
quai : les gars ont faim, le contremaître les surveille. Trois hot-dogs à la cantine, rapportés chauds. Un passant qui
donne une job (`passant`) : il te hèle dans la rue, et tout se dit en personne.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t02",
    "titre": "Le lunch des gars",
    "donneur": "passant",
    "prerequis": ["m6"],
    "recompense": 30,
    "passant": {"archetype": "docker", "district": "quais", "nom": "Le débardeur"},
    "donne": {"message": "UN HOT-DOG ALL DRESSED POUR LA PEINE"},

    # La cantine est déjà un lieu de mission (Lulu) : rien ne bouge. Il attend là où il t'a hélé — `retourner`.
    "objectifs": [
        {"type": "aller", "texte": "TROIS HOT-DOGS À LA CANTINE DES QUAIS", "lieu": "cantine", "rayon": 4},
        {"type": "retourner", "texte": "RAPPORTE LE LUNCH AU DÉBARDEUR — ÇA REFROIDIT", "chrono_s": 90},
    ],

    # Le jeu (`jeu=`) — le débardeur : pressé, affamé, et sérieux comme un pape au sujet de la moutarde.
    "dialogue": {
        "hele": [
            _l("passant", "Hé! Le jeune!", jeu="[cheerful] Hé! Le jeune!")
        ],
        "intro": [
            _l("passant", "T'as des jambes? Les gars ont faim, pis le contremaître nous lâche pas d'une semelle.",
               jeu="[casually] T'as des jambes? [annoyed] Les gars ont faim, pis le contremaître nous lâche pas d'une semelle."),
            _l("passant", "Trois hot-dogs à la cantine, moutarde, chou. Pas de ketchup, on n'est pas des sauvages.",
               jeu="[matter-of-fact] Trois hot-dogs à la cantine, moutarde, chou. [serious] Pas de ketchup, on n'est pas des sauvages.")
        ],
        "pendant": [
            _p("passant", "Grouille! Un hot-dog froid, c'est une insulte au quai.", 1,
               jeu="[shouting] Grouille! [playfully] Un hot-dog froid, c'est une insulte au quai.")
        ],
        "fin": [
            _l("passant", "Encore chauds! T'es un vrai. Trente piasses, pis garde-toi un hot-dog.",
               jeu="[happy] Encore chauds! T'es un vrai. [warmly] Trente piasses, pis garde-toi un hot-dog.")
        ],
        "echec": [
            _l("passant", "Laisse faire. Les gars vont manger leurs bottes, astheure.",
               jeu="[disappointed] Laisse faire. [sarcastic] Les gars vont manger leurs bottes, astheure.")
        ]
    }
}
