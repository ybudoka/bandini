"""La mission s09 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "s09",
    "titre": "L'explosion",
    "donneur": "boulon",
    "prerequis": ["s05"],
    "recompense": 600,
    "donne": {"message": "LE CAMION-CITERNE DE PRÉVOST A SAUTÉ"},

    # Le camion-citerne de Prévost attend dans la ruelle de l'usine (`detruire`, le patron de q03/q11) : au
    # pistolet, à la dynamite, en le percutant. L'explosion fait trois étoiles (`semer`), puis on revient.
    "objectifs": [
        {"type": "detruire", "texte": "FAIS SAUTER LE CAMION-CITERNE DE PRÉVOST",
         "vehicule": "camion", "ou": "ruelle:usine:14"},

        {"type": "semer", "texte": "TOUTE LA SHOP A ENTENDU — SÈME LA POLICE", "etoiles": 3},

        {"type": "retourner", "texte": "RETOURNE VOIR GROS-BOULON"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Gros-Boulon : pour une fois, il rit. Un camion qui saute, c'est deux ans de
    # colère qui sortent d'un coup ; ensuite il redevient sérieux — un homme qui sait ce que ça coûte.
    "dialogue": {
        "appel": [
            _l("boulon", "Gros-Boulon. Prévost remplit un camion-citerne pour vendre son usine en morceaux. Viens.",
               jeu="[gruffly] Gros-Boulon. [bitterly] Prévost remplit un camion-citerne pour vendre son usine en morceaux. [firmly] Viens.")
        ],
        "intro": [
            _l("boulon", "Il vide les cuves pour vendre le gaz avant de fermer pour de bon. Nos jobs partent en citerne.",
               jeu="[angry] Il vide les cuves pour vendre le gaz avant de fermer pour de bon. [bitterly] Nos jobs partent en citerne."),
            _l("boulon", "Le camion est derrière l'usine. Je le veux en feu. Personne dedans, personne autour.",
               jeu="[menacingly] Le camion est derrière l'usine. Je le veux en feu. [serious] Personne dedans, personne autour.")
        ],
        "pendant": [
            _p("boulon", "Vise la citerne. Pis recule, en masse.", 0,
               jeu="[firmly] Vise la citerne. [nervously] Pis recule… en masse."),
            _p("boulon", "Boum! Deux ans que j'attendais ça. Sauve-toi, la police arrive.", 1,
               jeu="[laughs] [excited] Boum! Deux ans que j'attendais ça. [serious] Sauve-toi, la police arrive."),
            _p("boulon", "T'es propre? Viens me voir, j'ai de quoi te payer.", 2,
               jeu="[calm] T'es propre? [warmly] Viens me voir, j'ai de quoi te payer.")
        ],
        "fin": [
            _l("boulon", "Prévost peut plus vendre. Il va devoir nous parler, astheure.",
               jeu="[satisfied] Prévost peut plus vendre. [confident] Il va devoir nous parler, astheure."),
            _l("boulon", "Six cents piastres. On a fait une collecte, les gars pis moi.",
               jeu="[gruffly] Six cents piastres. [warmly] On a fait une collecte… les gars pis moi.")
        ],
        "echec": [
            _l("boulon", "Le camion est parti. Nos jobs aussi, avec.",
               jeu="[bitterly] Le camion est parti. [somber] Nos jobs aussi, avec.")
        ]
    }
}
