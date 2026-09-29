"""La mission q07 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "q07",
    "titre": "La chambre 12",
    "donneur": "norbert",
    "prerequis": ["f10"],
    "recompense": 500,
    "echec": ["mort", "arrete", "vehicule_detruit", "etoile"],
    "donne": {"a_vendre": "hotel", "message": "L'HÔTEL BANDINI EST À VENDRE"},

    # ⚠️ C'EST ELLE QUI MET L'HÔTEL EN VENTE (`donne.a_vendre`, 28 sept. 2026) : la
    # quatrième propriété de _Le Boss_ (M13) était de phase 2, vendue nulle part. Un comptable
    # de Prévost est mort dans la chambre 12 ; les propriétaires veulent vendre avant que ça
    # se sache.
    #
    # Le plan d'origine livrait le « colis » à la cour de Ti-Loup — un lieu pas encore
    # dessiné. Il va à la fourrière, chez Gilles, qui compacte sans regarder (s01, q04 : il
    # connaît le chemin). Norbert est DEDANS (`point:norbert`) : pas de `retourner` vers lui,
    # la fin se dit par une coupe chez lui. `sans_etoile` du camion jusqu'à Gilles : un
    # camion de buanderie qui roule avec un mort dedans ne se fait pas remarquer.
    "objectifs": [
        {"type": "aller", "texte": "ATTENDS LA NUIT DEVANT L'HÔTEL",
         "lieu": "hotel", "rayon": 6, "nuit": True},

        {"type": "monter", "texte": "LE COLIS EST DANS LE CAMION DE BUANDERIE",
         "vehicule": "camion", "ou": "ruelle:hotel", "sans_etoile": True},

        {"type": "livrer", "texte": "À LA FOURRIÈRE, SANS TE FAIRE REMARQUER",
         "lieu": "fourriere", "rayon": 5, "sans_etoile": True},

        {"type": "parler", "texte": "GILLES S'OCCUPE DU RESTE",
         "cible": "gilles", "sans_etoile": True},
    ],

    # ⚠️ L'INTRO EST ÉCRITE (la recette de q11 : Norbert est DEDANS, et sous la coupe du défaut sa première
    # réplique était coupée par la seconde) — elle montre la ruelle de l'hôtel, où le camion attendra.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "ruelle:hotel", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Norbert, la chambre 12 : le même calme qu'en f10,
    # mais le vouvoiement se serre ; il parle d'un mort comme d'une réservation annulée, et
    # c'est ce qui fait peur. Gilles, lui, a tout vu passer à la fourrière : il soupire.
    "dialogue": {
        "appel": [
            _l("norbert", "Ici Norbert, de l'Hôtel Bandini. Un client de la chambre douze ne descendra pas déjeuner. Jamais.",
               jeu="[quietly] Ici Norbert, de l'Hôtel Bandini. [calm] Un client de la chambre douze ne descendra pas déjeuner… Jamais.")
        ],
        "intro": [
            _l("norbert", "Un comptable de Monsieur Prévost. Les propriétaires préfèrent que la police l'apprenne dans un an.",
               jeu="[calm] Un comptable de Monsieur Prévost. [knowingly] Les propriétaires préfèrent que la police l'apprenne… dans un an."),
            _l("norbert", "Le colis sera dans le camion de la buanderie, à la nuit. Monsieur conduira doucement.",
               jeu="[quietly] Le colis sera dans le camion de la buanderie, à la nuit. [firmly] Monsieur conduira doucement.")
        ],
        "pendant": [
            _p("norbert", "Le chasseur termine de plier les draps. À la nuit, pas avant.", 0,
               jeu="[calm] Le chasseur termine de plier les draps. [quietly] À la nuit… pas avant."),
            _p("norbert", "Le camion est derrière, les clés sur le contact. Le colis ne fait pas de bruit.", 1,
               jeu="[quietly] Le camion est derrière, les clés sur le contact. [deadpan] Le colis ne fait pas de bruit."),
            _p("norbert", "La fourrière, Monsieur. Gilles a l'habitude des choses qu'on ne réclame pas.", 2,
               jeu="[knowingly] La fourrière, Monsieur. [calm] Gilles a l'habitude des choses qu'on ne réclame pas."),
            _p("norbert", "Laissez parler Gilles. Il pose moins de questions que moi.", 3,
               jeu="[quietly] Laissez parler Gilles. [wryly] Il pose moins de questions que moi.")
        ],
        "accueil": [
            _a("gilles", "Un camion de buanderie à trois heures du matin. Le compacteur est chaud, le jeune.", 3,
               jeu="[somber] Un camion de buanderie à trois heures du matin. [gravely] Le compacteur est chaud, le jeune.")
        ],
        "fin": [
            _l("norbert", "La chambre douze est libre. Les propriétaires, eux, veulent partir avant le printemps.",
               jeu="[calm] La chambre douze est libre. [knowingly] Les propriétaires, eux… veulent partir avant le printemps."),
            _l("norbert", "L'hôtel est à vendre, Monsieur. Je reste avec les murs, si le nouveau patron veut de moi.",
               jeu="[quietly] L'hôtel est à vendre, Monsieur. [warmly] Je reste avec les murs… si le nouveau patron veut de moi.")
        ],
        "echec": [
            _l("norbert", "Je crains que Monsieur ait été remarqué. Nous reprendrons quand la rue se sera calmée.",
               jeu="[concerned] Je crains que Monsieur ait été remarqué. [calm] Nous reprendrons quand la rue se sera calmée.")
        ]
    }
}
