"""La mission q03 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "q03",
    "titre": "Les briseurs de grève",
    "donneur": "gege",
    "prerequis": ["m6"],
    "recompense": 300,
    "donne": {"message": "LES SCABS RESTENT CHEZ EUX"},

    # ⚠️ `detruire` (M16) : réutilise `poserLeChar` comme `monter`, mais c'est
    # `B.mission.chars` qui le surveille — on le casse, on ne roule pas dedans.
    "objectifs": [
        {"type": "detruire", "texte": "DÉTRUIS LE CAMION AVANT L'USINE",
         "vehicule": "camion", "ou": "ruelle:usine:20", "chrono_s": 120},

        {"type": "retourner", "texte": "RETOURNE VOIR GÉGÉ"}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Gégé : sec, sans détour, une satisfaction
    # brève une fois le camion arrêté — il ne remercie jamais deux fois.
    "dialogue": {
        "appel": [
            _l("gege", "Gégé, chef des débardeurs. Prévost fait venir des scabs par camion — arrête-le avant l'usine.",
               jeu="[firmly] Gégé, chef des débardeurs. [gravely] Prévost fait venir des scabs par camion… arrête-le avant l'usine.")
        ],
        "intro": [
            _l("gege", "Le camion vient par le boulevard, du côté de l'usine. T'as pas beaucoup de temps.",
               jeu="[gravely] Le camion vient par le boulevard, du côté de l'usine. [firmly] T'as pas beaucoup de temps."),
            _l("gege", "Une fois cassé, plus personne remplace les gars du syndicat aujourd'hui.",
               jeu="[firmly] Une fois cassé… plus personne remplace les gars du syndicat aujourd'hui.")
        ],
        "pendant": [
            _p("gege", "Le camion approche! Fais ça vite, avant qu'il passe la guérite.", 0,
               jeu="[gravely] Le camion approche! [firmly] Fais ça vite… avant qu'il passe la guérite.")
        ],
        "fin": [
            _l("gege", "Le camion brûle sur le boulevard. Les scabs resteront chez eux, à soir.",
               jeu="[satisfied] Le camion brûle sur le boulevard. [firmly] Les scabs resteront chez eux… à soir."),
            _l("gege", "Les gars vont s'en souvenir. T'as du cran.",
               jeu="[impressed] Les gars vont s'en souvenir. [gruffly] T'as du cran.")
        ],
        "echec": [
            _l("gege", "Le camion est passé... Les gars vont pas aimer ça.",
               jeu="[annoyed] Le camion est passé… [gravely] Les gars vont pas aimer ça.")
        ]
    }
}
