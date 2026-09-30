"""La mission d07 — voir app/missions/__init__.py pour le moteur.

Le coffre de Sal (M16, arc D, 30 sept. 2026) — un côté du CHOIX de l'arc (`ferme: d08`). Sal a cassé le garage
(d06) ; Josée ne pardonne pas qu'on touche à ce qui est à la famille. Chaque nuit, Sal ferme sa chaise et range
la recette de la semaine dans le coffre de sa berline, garée dans la ruelle du terminus. On la vole, deux étoiles
(le terminus a des yeux), on les sème, et on la mène au Brouillard, où Josée compte. Deux mille piasses — et plus
jamais de dernière coupe : la dette reste, et Sal ne l'oubliera pas.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "d07",
    "titre": "Le coffre de Sal",
    "donneur": "josee",
    "prerequis": ["d06"],
    "ferme": "d08",
    "recompense": 2000,
    "donne": {"message": "LA RECETTE DE SAL EST AU BROUILLARD — SAL NE L'OUBLIERA PAS"},

    # ⚠️ « Vider le salon » ne se joue pas DANS la pièce du terminus (`majObjectif` dort dedans) : le coffre dort
    # dans la valise de sa berline, dans la ruelle (`monter`, `ruelle:terminus:10`, comme la berline de Prévost en
    # s05). Josée est dedans : on livre à la porte du bar, puis on va lui parler.
    "objectifs": [
        {"type": "aller", "texte": "À LA NUIT, AU TERMINUS : SAL FERME SA CAISSE",
         "lieu": "terminus", "rayon": 8, "nuit": True},

        {"type": "monter", "texte": "LA BERLINE DE SAL, DANS LA RUELLE : VOLE-LA",
         "vehicule": "luxe", "ou": "ruelle:terminus:10"},

        {"type": "semer", "texte": "LE TERMINUS A DES YEUX : SÈME LA POLICE", "etoiles": 2},

        {"type": "livrer", "texte": "LA BERLINE ET SON COFFRE AU BROUILLARD",
         "lieu": "bar", "rayon": 5},

        {"type": "parler", "texte": "JOSÉE COMPTE LA RECETTE, DEDANS", "cible": "josee"},
    ],

    # Intention (intro) : Josée ne lève pas la voix ; elle pose le plan comme une facture. Sa réplique tient le bar,
    # la coupe va sur la ruelle du terminus (la berline) sous la deuxième.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "ruelle:terminus:10", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Josée : la colère froide de la Chef, qui ne se venge pas, elle
    # « rééquilibre ». Le seul `[warmly]` de la mission va à la fin, pour le neveu.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. Sal a touché à ton garage, pis chez nous, on répond. Viens au bar.",
               jeu="[coldly] Josée. Sal a touché à ton garage, [menacingly] pis chez nous, on répond. Viens au bar.")
        ],
        "intro": [
            _l("josee", "Sal ferme sa chaise à minuit. La recette de la semaine dort dans la valise de sa berline.",
               jeu="[matter-of-fact] Sal ferme sa chaise à minuit. [knowingly] La recette de la semaine dort dans la valise de sa berline."),
            _l("josee", "Elle est garée dans la ruelle du terminus. Prends le char au complet, on ouvrira ici.",
               jeu="[coldly] Elle est garée dans la ruelle du terminus. [matter-of-fact] Prends le char au complet, on ouvrira ici."),
            _l("josee", "Penses-y avant de partir. Après ça, Sal te coupera plus jamais les cheveux.",
               jeu="[serious] Penses-y avant de partir. [mysteriously] Après ça, Sal te coupera plus jamais les cheveux.")
        ],
        "pendant": [
            _p("josee", "Attends que la dernière lumière s'éteigne. Sal compte deux fois avant de partir.", 0,
               jeu="[quietly] Attends que la dernière lumière s'éteigne. [wryly] Sal compte deux fois avant de partir."),
            _p("josee", "La berline noire, derrière. Les clés sont toujours dessus, il pense que personne oserait.", 1,
               jeu="[matter-of-fact] La berline noire, derrière. [coldly] Les clés sont toujours dessus, il pense que personne oserait."),
            _p("josee", "Les chauffeurs du terminus ont appelé. Perds-les, pis garde le char entier.", 2,
               jeu="[firmly] Les chauffeurs du terminus ont appelé. [matter-of-fact] Perds-les, pis garde le char entier."),
            _p("josee", "Stationne-la devant chez nous. Mes gars vont ouvrir la valise.", 3,
               jeu="[calm] Stationne-la devant chez nous. [confident] Mes gars vont ouvrir la valise."),
            _p("josee", "Viens me voir. J'ai jamais vu autant de billets de vingt.", 4,
               jeu="[satisfied] Viens me voir. [amused] J'ai jamais vu autant de billets de vingt.")
        ],
        "fin": [
            _l("josee", "Deux mille, en vingts propres. Sal lavait mieux son argent que ses serviettes.",
               jeu="[satisfied] Deux mille, en vingts propres. [wryly] Sal lavait mieux son argent que ses serviettes."),
            _l("josee", "C'est à toi. Garde un œil derrière ton épaule, astheure. Sal oublie jamais un visage.",
               jeu="[warmly] C'est à toi. [serious] Garde un œil derrière ton épaule, astheure. [coldly] Sal oublie jamais un visage.")
        ],
        "echec": [
            _l("josee", "La recette est repartie avec Sal. Il saura que c'était nous.",
               jeu="[coldly] La recette est repartie avec Sal. [matter-of-fact] Il saura que c'était nous.")
        ]
    }
}
