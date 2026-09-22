"""La mission h01 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "h01",
    "titre": "L'ambulance de nuit",
    "donneur": "lachance",
    "prerequis": ["m6"],
    "recompense": 300,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"message": "LE BOULOT AMBULANCE, AU KLAXON"},

    # ⚠️ `boulots` (M16) : `sorte: "ambulance"` existe déjà (`economie.BOULOTS`,
    # `SORTES` côté JS) — le premier boulot de nuit du carnet.
    # ⚠️ Pas de `retourner` après : Lachance se tient DEDANS (`point:lachance`) — voir
    # la même note dans `f06.py`. `boulots`, dernier objectif, ferme la mission tout
    # seul, et sa fin se dit au combiné.
    "objectifs": [
        {"type": "aller", "texte": "VA À L'HÔPITAL ET ATTENDS LA NUIT",
         "lieu": "hopital", "rayon": 6, "nuit": True},

        {"type": "monter", "texte": "MONTE DANS L'AMBULANCE", "vehicule": "ambulance", "ou": "porte:hopital"},

        {"type": "boulots", "texte": "FAIS TROIS TRANSPORTS, DE NUIT", "n": 3, "sorte": "ambulance"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Dr Lachance : clinique et posé, jamais de
    # panique dans la voix, même fatigué — le ton d'une salle d'urgence qui roule
    # depuis trop longtemps.
    "dialogue": {
        "appel": [
            _l("lachance", "Ici le docteur Lachance, de l'hôpital. J'ai besoin d'une ambulance en état de rouler, cette nuit.",
               jeu="[calm] Ici le docteur Lachance, de l'hôpital. [gravely] J'ai besoin d'une ambulance en état de rouler… cette nuit.")
        ],
        "intro": [
            _l("lachance", "L'urgence manque de bras entre minuit et six heures. Trois transports, pas plus.",
               jeu="[matter-of-fact] L'urgence manque de bras entre minuit et six heures. [firmly] Trois transports… pas plus."),
            _l("lachance", "Klaxonne pour prendre chaque blessé. Conduis vite, mais conduis droit.",
               jeu="[gravely] Klaxonne pour prendre chaque blessé. [firmly] Conduis vite, mais conduis droit.")
        ],
        "pendant": [
            _p("lachance", "Un blessé qui attend trop longtemps, on ne le récupère pas au triage.", 2,
               jeu="[gravely] Un blessé qui attend trop longtemps… [serious] on ne le récupère pas au triage.")
        ],
        "fin": [
            _l("lachance", "Trois de plus qui dorment dans un vrai lit, cette nuit. Ça compte.",
               jeu="[relieved] Trois de plus qui dorment dans un vrai lit, cette nuit. [calm] Ça compte."),
            _l("lachance", "L'hôpital te doit une faveur. Reviens si tu en as besoin.",
               jeu="[matter-of-fact] L'hôpital te doit une faveur. [warmly] Reviens si tu en as besoin.")
        ],
        "echec": [
            _l("lachance", "On fera avec ce qu'on a... Reviens si tu peux, une autre nuit.",
               jeu="[somber] On fera avec ce qu'on a… [calm] Reviens si tu peux, une autre nuit.")
        ]
    },

    # Intention (intro) : celle du défaut (dedans) — une coupe sur `porte:hopital`, il croise les bras, il
    # finit. ⚠️ SAUF que la coupe part `ensemble` avec la première réplique au lieu de la retenir (forme
    # de q02/m51) : la voix dure 6,5 s, la coupe du défaut 3,2 s, et la seconde réplique la coupait.
    # Le `dire` retient la scène jusqu'au bout de sa voix.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "porte:hopital", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
    },
}
