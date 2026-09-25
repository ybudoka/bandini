"""La mission q11 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "q11",
    "titre": "Le cargo brûle",
    "donneur": "josee",
    "prerequis": ["q04"],
    # ⚠️ LE CHOIX (M16, `ferme`) : Josée ou Sven, pas les deux — l'envers de q10.
    "ferme": "q10",
    "recompense": 700,
    "donne": {"message": "LE NORVÉGIEN REGARDE SON QUAI BRÛLER"},

    # Deux camions de Sven : le premier derrière la cantine, au bord du quai
    # (`ruelle:cantine:12` — ⚠️ pas `ou: quai` : `Histoire.tuileDeQuai` cherche un glyphe
    # que la carte n'a plus, et rend `null` ; le camion ne naissait pas), le second qui attend
    # au pont (`ou: pont`) — posé quand son objectif commence, donc jamais sur l'épave du
    # premier. Un port en feu, trois étoiles (`semer`). Josée est DEDANS
    # (`point:contact`) : on finit au bar, sa fin se dit chez elle.
    "objectifs": [
        {"type": "detruire", "texte": "FAIS SAUTER LE CAMION DE SVEN, DERRIÈRE LA CANTINE",
         "vehicule": "camion", "ou": "ruelle:cantine:12"},

        {"type": "detruire", "texte": "LE DEUXIÈME ATTEND AU PONT — FAIS-LE SAUTER AUSSI",
         "vehicule": "camion", "ou": "pont"},

        {"type": "semer", "texte": "LE PORT BRÛLE, LA POLICE ARRIVE — SÈME-LA",
         "etoiles": 3},

        {"type": "aller", "texte": "VIENS AU BAR, LA CHEF T'ATTEND",
         "lieu": "bar", "rayon": 4},
    ],

    # ⚠️ L'INTRO EST ÉCRITE, comme celle de q01 : sous la coupe du défaut, la première
    # réplique était coupée par la deuxième. La coupe en `ensemble`, puis la voix.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "ruelle:cantine:12", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Josée : la Chef qui ne hausse jamais le ton ;
    # plus menaçante posée qu'en colère. Un seul `[warmly]` dans la mission, à la fin du
    # pendant — c'est ce qui le rend rare.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. Le Norvégien charge deux camions sur mon quai, ce soir. Je veux voir de la fumée.",
               jeu="[coldly] Josée. Le Norvégien charge deux camions sur mon quai, ce soir. [menacingly] Je veux voir de la fumée.")
        ],
        "intro": [
            _l("josee", "Sven pense que le port se loue. On va lui montrer qu'il se défend.",
               jeu="[matter-of-fact] Sven pense que le port se loue. [coldly] On va lui montrer qu'il se défend."),
            _l("josee", "Deux camions, sur le quai. Je les veux en morceaux, pas volés.",
               jeu="[firmly] Deux camions, sur le quai. [menacingly] Je les veux en morceaux… pas volés."),
            _l("josee", "Il t'a fait une offre, je le sais. Moi, je la double.",
               jeu="[knowingly] Il t'a fait une offre, je le sais. [confident] Moi, je la double.")
        ],
        "pendant": [
            _p("josee", "Le premier est chargé. Ce qui brûle bien, c'est ce qui coûte cher.", 0,
               jeu="[calm] Le premier est chargé. [wryly] Ce qui brûle bien… c'est ce qui coûte cher."),
            _p("josee", "Le deuxième attend au pont. Il ira pas plus loin.", 1,
               jeu="[coldly] Le deuxième attend au pont. [firmly] Il ira pas plus loin."),
            _p("josee", "Ça va s'entendre jusqu'au poste. Disparais un peu.", 2,
               jeu="[matter-of-fact] Ça va s'entendre jusqu'au poste. [calm] Disparais un peu."),
            _p("josee", "Viens au bar. On a à se parler.", 3,
               jeu="[warmly] Viens au bar. [mysteriously] On a à se parler.")
        ],
        "fin": [
            _l("josee", "Le Norvégien regarde son quai brûler depuis son bateau. C'est une belle soirée.",
               jeu="[satisfied] Le Norvégien regarde son quai brûler… depuis son bateau. [coldly] C'est une belle soirée."),
            _l("josee", "Il lèvera l'ancre ou il apprendra à nager. Les deux me vont.",
               jeu="[menacingly] Il lèvera l'ancre… ou il apprendra à nager. [matter-of-fact] Les deux me vont.")
        ],
        "echec": [
            _l("josee", "Ses camions roulent encore. Le Norvégien rit, ce soir.",
               jeu="[coldly] Ses camions roulent encore. [bitterly] Le Norvégien rit, ce soir.")
        ]
    }
}
