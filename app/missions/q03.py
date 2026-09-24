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
    # ⚠️ Plus longue (Martin, 22 sept. 2026, « des missions plus longues ») : Prévost a
    # payé des Boulonneux pour escorter son camion — ils ARRIVENT (`loin`) sur le joueur
    # devant l'usine ; le camion qui brûle amène la police (`semer`, deux étoiles) ; puis
    # le retour chez Gégé, à la cantine, à l'autre bout de la ville (≈ 250 tuiles).
    "objectifs": [
        {"type": "detruire", "texte": "DÉTRUIS LE CAMION AVANT L'USINE",
         "vehicule": "camion", "ou": "ruelle:usine:20", "chrono_s": 120},

        {"type": "tuer", "texte": "LES BOULONNEUX DE PRÉVOST — COUCHE-LES",
         "groupe": "boulonneux", "n": 3, "ou": "donneur", "loin": 10},

        {"type": "semer", "texte": "LA POLICE S'EN VIENT — SÈME-LA", "etoiles": 2},

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
               jeu="[firmly] Une fois cassé… plus personne remplace les gars du syndicat aujourd'hui."),
            _l("gege", "Prévost paie du monde pour garder son camion. Attends-toi à de la visite.",
               jeu="[gravely] Prévost paie du monde pour garder son camion. [firmly] Attends-toi à de la visite.")
        ],
        "pendant": [
            _p("gege", "Le camion approche! Fais ça vite, avant qu'il passe la guérite.", 0,
               jeu="[gravely] Le camion approche! [firmly] Fais ça vite… avant qu'il passe la guérite."),
            _p("gege", "Prévost a payé des Boulonneux pour garder son camion. Montre-leur où passe la ligne.", 1,
               jeu="[gravely] Prévost a payé des Boulonneux pour garder son camion. [firmly] Montre-leur où passe la ligne."),
            _p("gege", "La police s'en vient. Un débardeur a jamais rien vu, apprends ça vite.", 2,
               jeu="[firmly] La police s'en vient. [gruffly] Un débardeur a jamais rien vu… apprends ça vite."),
            _p("gege", "Reviens à la cantine. Les gars veulent voir la face de celui qui a fait ça.", 3,
               jeu="[satisfied] Reviens à la cantine. [gruffly] Les gars veulent voir la face de celui qui a fait ça.")
        ],
        "fin": [
            _l("gege", "Le camion brûle sur le boulevard. Les scabs resteront chez eux, à soir.",
               jeu="[satisfied] Le camion brûle sur le boulevard. [firmly] Les scabs resteront chez eux… à soir."),
            _l("gege", "Les gars vont s'en souvenir. T'as du cran.",
               jeu="[impressed] Les gars vont s'en souvenir. [gruffly] T'as du cran."),
            _l("gege", "Pis ses Boulonneux vont boiter jusqu'à la paie. Bon débarras.",
               jeu="[amused] Pis ses Boulonneux vont boiter jusqu'à la paie. [gruffly] Bon débarras.")
        ],
        "echec": [
            _l("gege", "Le camion est passé... Les gars vont pas aimer ça.",
               jeu="[annoyed] Le camion est passé… [gravely] Les gars vont pas aimer ça.")
        ]
    }
}
