"""La mission q04 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "q04",
    "titre": "La cargaison du Norvégien",
    "donneur": "josee",
    "prerequis": ["q02"],
    "recompense": 400,
    "echec": ["mort", "arrete", "vehicule_detruit", "etoile"],
    "donne": {"message": "LE BAR RESPIRE, UN SOIR DE PLUS"},

    # ⚠️ Première vraie preuve de `sans_etoile` (M16, déclaré depuis le premier
    # commit, jamais encore joué par une mission) : `majObjectif` échoue net
    # (`etoile`) dès que `B.recherche.etoiles > 0`, tant que l'objectif marqué
    # tient. Posé sur les deux : le camion se prend ET se livre à l'abri des
    # regards. Josée est DEDANS (`point:contact`) : pas de `retourner` après
    # `livrer`, sa fin se dit au bar comme celle de f06/h01.
    "objectifs": [
        {"type": "monter", "texte": "PRENDS LE CAMION, SANS TE FAIRE REMARQUER",
         "vehicule": "camion", "ou": "porte:cantine", "sans_etoile": True},

        {"type": "livrer", "texte": "LIVRE-LE AU BAR",
         "lieu": "bar", "rayon": 4, "sans_etoile": True},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Josée : la Chef, directe, jamais un mot de
    # trop ; elle donne un ordre comme elle sert un verre, sans y penser deux fois.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. Le cargo du Norvégien décharge cette nuit, discret. J'ai une part qui m'attend.",
               jeu="[calm] Josée. Le cargo du Norvégien décharge cette nuit, discret. [firmly] J'ai une part qui m'attend.")
        ],
        "intro": [
            _l("josee", "Un camion sort du quai, caché derrière la cantine de Lulu. Prends-le sans attirer l'œil.",
               jeu="[firmly] Un camion sort du quai, caché derrière la cantine de Lulu. [gravely] Prends-le sans attirer l'œil."),
            _l("josee", "Une étoile sur toi, pis c'est toute la cargaison qui coule. Amène-le au bar, tranquille.",
               jeu="[serious] Une étoile sur toi, pis c'est toute la cargaison qui coule. [matter-of-fact] Amène-le au bar, tranquille.")
        ],
        "pendant": [
            _p("josee", "Roule normal. Un camion qui se presse, ça se remarque.", 1,
               jeu="[calm] Roule normal. [firmly] Un camion qui se presse, ça se remarque.")
        ],
        "fin": [
            _l("josee", "Propre. Sven va croire que sa cargaison s'est envolée toute seule.",
               jeu="[satisfied] Propre. [amused] Sven va croire que sa cargaison s'est envolée toute seule."),
            _l("josee", "Le bar respire un soir de plus. C'est de même que Les Quais nous appartiennent.",
               jeu="[confident] Le bar respire un soir de plus. [firmly] C'est de même que Les Quais nous appartiennent.")
        ],
        "echec": [
            _l("josee", "Repéré... Le Norvégien va savoir qu'on rôde autour de son quai. Reviens quand t'es plus fin.",
               jeu="[annoyed] Repéré… [gravely] Le Norvégien va savoir qu'on rôde autour de son quai. Reviens quand t'es plus fin.")
        ]
    }
}
