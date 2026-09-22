"""La mission q04 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

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
    # ⚠️ Plus longue (Martin, 22 sept. 2026, « des missions plus longues ») : le cargo
    # décharge la NUIT (l'appel le disait) — on l'attend près de la cantine (`aller`,
    # `nuit`) ; et un camion du Norvégien ne rentre pas au bar avec ses plaques :
    # détour par la fourrière, à l'autre bout de la ville (≈ 270 tuiles), où Gilles les
    # change (`parler`, sa poignée de main dite — sa première réplique du catalogue :
    # il se nomme). Toujours `sans_etoile`, du camion jusqu'au bar. On descend parler à
    # Gilles et on remonte : `livrer` regarde `B.mission.vehicule`, le camion.
    "objectifs": [
        {"type": "aller", "texte": "ATTENDS LA NUIT PRÈS DE LA CANTINE",
         "lieu": "cantine", "rayon": 6, "nuit": True},

        {"type": "monter", "texte": "PRENDS LE CAMION, SANS TE FAIRE REMARQUER",
         "vehicule": "camion", "ou": "porte:cantine", "sans_etoile": True},

        {"type": "parler", "texte": "FAIS CHANGER LES PLAQUES PAR GILLES",
         "cible": "gilles", "sans_etoile": True},

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
               jeu="[serious] Une étoile sur toi, pis c'est toute la cargaison qui coule. [matter-of-fact] Amène-le au bar, tranquille."),
            _l("josee", "Le cargo décharge à la noirceur. Attends la nuit près de la cantine.",
               jeu="[matter-of-fact] Le cargo décharge à la noirceur. [calm] Attends la nuit près de la cantine.")
        ],
        "pendant": [
            _p("josee", "La nuit est tombée. Le chauffeur est à la cantine, le nez dans sa bière.", 1,
               jeu="[calm] La nuit est tombée. [knowingly] Le chauffeur est à la cantine… le nez dans sa bière."),
            _p("josee", "Pas au bar tout de suite. Gilles, à la fourrière, change des plaques sans poser de questions.", 2,
               jeu="[matter-of-fact] Pas au bar tout de suite. [knowingly] Gilles, à la fourrière, change des plaques sans poser de questions."),
            _p("josee", "Roule normal. Un camion qui se presse, ça se remarque.", 3,
               jeu="[calm] Roule normal. [firmly] Un camion qui se presse, ça se remarque.")
        ],
        "accueil": [
            _a("gilles", "C'est Gilles, de la fourrière. Trente ans que je change des plaques, le jeune, pis jamais les miennes.", 2,
               jeu="[somber] C'est Gilles, de la fourrière. [wryly] Trente ans que je change des plaques, le jeune… pis jamais les miennes.")
        ],
        "fin": [
            _l("josee", "Propre. Sven va croire que sa cargaison s'est envolée toute seule.",
               jeu="[satisfied] Propre. [amused] Sven va croire que sa cargaison s'est envolée toute seule."),
            _l("josee", "Le bar respire un soir de plus. C'est de même que Les Quais nous appartiennent.",
               jeu="[confident] Le bar respire un soir de plus. [firmly] C'est de même que Les Quais nous appartiennent."),
            _l("josee", "Gilles a fait ça propre. Même le Norvégien reconnaîtrait pas son camion.",
               jeu="[satisfied] Gilles a fait ça propre. [amused] Même le Norvégien reconnaîtrait pas son camion.")
        ],
        "echec": [
            _l("josee", "Repéré... Le Norvégien va savoir qu'on rôde autour de son quai. Reviens quand t'es plus fin.",
               jeu="[annoyed] Repéré… [gravely] Le Norvégien va savoir qu'on rôde autour de son quai. Reviens quand t'es plus fin.")
        ]
    },

    # Intention (intro) : celle du défaut (dedans) — une coupe sur `porte:cantine`, il croise les bras, il
    # finit. ⚠️ SAUF que la coupe part `ensemble` avec la première réplique au lieu de la retenir (forme
    # de q02/m51) : la voix dure 5,7 s, la coupe du défaut 3,2 s, et la seconde réplique la coupait.
    # Le `dire` retient la scène jusqu'au bout de sa voix.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "porte:cantine", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            # La troisième réplique (des missions plus longues, 22 sept. 2026) : l'étape de plus qu'elle annonce.
            {"type": "dire", "repliques": [3]},
        ],
    },
}
