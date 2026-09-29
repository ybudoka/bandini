"""La mission q06 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "q06",
    "titre": "Le Beau Denis",
    "donneur": "josee",
    "prerequis": ["q05"],
    "recompense": 350,
    "echec": ["mort", "arrete", "arme"],
    # ⚠️ `calme` (M16) : les Morues te laissent passer — tu as couché leur lieutenant à la loyale, chez eux, et la
    # Chef l'a voulu. Plus une ne te saute dessus pour une arme au poing (`Entites.gangCalme`).
    "donne": {"calme": "morues", "message": "LES MORUES TE LAISSENT PASSER"},

    # ⚠️ `sans_arme` (enfin lue, 29 sept. 2026) : une arme AU POING dans leur coin, c'est raté — la ligne
    # d'objectif dit « RANGE TON ARME » tant qu'on en tient une, avant d'y entrer. Les deux gardes et Denis se
    # battent aux poings eux aussi (`arme: ""`) : c'est une affaire entre hommes de la Chef, pas une guerre.
    # Tout se joue dans le coin des Morues, loin du bar où la fin se dit (la règle « un `tuer` à l'étape 0 ne se
    # pose pas là où la mission finit »).
    "objectifs": [
        {"type": "tuer", "texte": "SES DEUX GARDES, CHEZ LES MORUES — À MAINS NUES",
         "groupe": "morues", "n": 2, "ou": "zone:morues", "arme": "", "sans_arme": True},

        {"type": "tuer", "texte": "LE BEAU DENIS — À MAINS NUES",
         "groupe": "morues", "n": 1, "chef": True, "ou": "zone:morues", "arme": "", "vie": 180,
         "sans_arme": True},

        {"type": "semer", "texte": "LE PORT A TOUT VU — SÈME LA POLICE",
         "etoiles": 2},

        {"type": "aller", "texte": "VIENS AU BAR, LA CHEF T'ATTEND",
         "lieu": "bar", "rayon": 4},
    ],

    # ⚠️ L'INTRO EST ÉCRITE (la recette de q11) : Josée est DEDANS, et sous la coupe du défaut sa première
    # réplique serait coupée par la suivante. La coupe en `ensemble`, puis la voix.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "zone:morues", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Josée : furieuse, et ça ne s'entend qu'au calme. Denis est à elle, et
    # il a envoyé ses gars sur quelqu'un qu'elle protège : c'est ça, l'affront. Elle ne dit pas « tue-le » : elle
    # dit « à mains nues », parce qu'elle veut qu'il se relève et qu'il s'en souvienne. Un seul `[warmly]`, pour
    # Cindy, à la fin.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. Denis a envoyé ses gars sur une fille que je t'avais confiée. Viens au bar.",
               jeu="[coldly] Josée. Denis a envoyé ses gars sur une fille que je t'avais confiée. [firmly] Viens au bar.")
        ],
        "intro": [
            _l("josee", "Denis est à moi depuis dix ans. Il pense que ça lui donne des droits.",
               jeu="[matter-of-fact] Denis est à moi depuis dix ans. [coldly] Il pense que ça lui donne des droits."),
            _l("josee", "Va le voir chez nous, au port. Pas d'arme. Je veux qu'il se relève, pis qu'il s'en souvienne.",
               jeu="[menacingly] Va le voir chez nous, au port. [firmly] Pas d'arme. Je veux qu'il se relève… pis qu'il s'en souvienne."),
            _l("josee", "Si t'arrives là un fusil à la main, mes Morues vont penser que c'est la guerre. Ça en est pas une.",
               jeu="[serious] Si t'arrives là un fusil à la main, mes Morues vont penser que c'est la guerre. [calm] Ça en est pas une.")
        ],
        "pendant": [
            _p("josee", "Ses deux gardes d'abord. Ils sont payés pour recevoir les premiers coups.", 0,
               jeu="[coldly] Ses deux gardes d'abord. [wryly] Ils sont payés pour recevoir les premiers coups."),
            _p("josee", "Le v'là. Il est beau parce qu'on l'a jamais frappé au visage.", 1,
               jeu="[knowingly] Le v'là. [menacingly] Il est beau… parce qu'on l'a jamais frappé au visage."),
            _p("josee", "Quelqu'un a appelé la police. Pas un des miens. Disparais.", 2,
               jeu="[matter-of-fact] Quelqu'un a appelé la police. [coldly] Pas un des miens. Disparais."),
            _p("josee", "Viens au bar. Les Morues ont quelque chose à te dire.", 3,
               jeu="[calm] Viens au bar. [mysteriously] Les Morues ont quelque chose à te dire.")
        ],
        "fin": [
            _l("josee", "Denis s'est relevé. Il boite, pis il a compris. Toute la Morue l'a vu.",
               jeu="[satisfied] Denis s'est relevé. Il boite, pis il a compris. [coldly] Toute la Morue l'a vu."),
            _l("josee", "Mes gars te laissent passer, astheure. T'as frappé à la loyale, chez eux.",
               jeu="[matter-of-fact] Mes gars te laissent passer, astheure. [confident] T'as frappé à la loyale, chez eux."),
            _l("josee", "Pis la petite, à l'hôtel. Dis-lui que la Chef paie son premier loyer.",
               jeu="[warmly] Pis la petite, à l'hôtel. [quietly] Dis-lui que la Chef paie son premier loyer.")
        ],
        "echec": [
            _l("josee", "T'as sorti une arme, ou tu t'es fait coucher. Dans les deux cas, Denis rit.",
               jeu="[coldly] T'as sorti une arme, ou tu t'es fait coucher. [bitterly] Dans les deux cas… Denis rit.")
        ]
    }
}
