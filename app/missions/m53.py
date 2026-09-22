"""La mission m53 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m53",
    "titre": "Sous pavillon",
    "donneur": "sven",
    "prerequis": ["m52"],
    "recompense": 500,
    "echec": ["mort", "arrete", "vehicule_detruit", "etoile", "alarme"],
    "donne": {"message": "LE RELAIS DE JOSÉE EST MUET"},

    # ⚠️ **PREMIER USAGE DU PIRATAGE** (type `pirater` : une séquence de 4 directions, le même
    # axe unifié que la marche — Combat.creneauVise, la roue d'armes). Deux quais de chalutier
    # existent dans chaque ville (`navires.FLOTTE`) : on prend celui-ci, on pirate l'autre — un
    # chalutier ne se remarque pas comme une chaloupe qui traverse toute la baie de nuit.
    "objectifs": [
        {"type": "monter", "texte": "PRENDS LE CHALUTIER, AU QUAI DE SVEN",
         "vehicule": "chalutier", "ou": "mouillage:chalutier:0", "prete": "sven"},

        {"type": "livrer", "texte": "MÈNE-LE À L'AUTRE QUAI, SANS ATTIRER L'ŒIL",
         "lieu": "mouillage:chalutier:1", "rayon": 5, "sans_etoile": True},

        {"type": "pirater", "texte": "PIRATE LE RELAIS — SUIS LA SÉQUENCE",
         "ou": "mouillage:chalutier:1", "rayon": 5, "longueur": 4, "essais": 3},

        # ⚠️ **Plus long, plus loin** (Martin, 22 sept. 2026 : « des missions plus longues ») : le
        # relais a crié avant de se taire — deux Morues accourent (`loin` : elles naissent hors
        # champ et courent sur toi) ; puis on suit son fil jusqu'au clocher de l'Île-aux-Corneilles,
        # à l'autre bout de la baie, en chalutier. `ou` et pas `lieu` pour l'île : elle ne se
        # rejoint pas à pied (`test_barrieres.py`).
        {"type": "tuer", "texte": "DEUX MORUES ACCOURENT — LE RELAIS A CRIÉ",
         "groupe": "morues", "n": 2, "ou": "donneur", "loin": 12},

        {"type": "pirater", "texte": "LE RELAIS PARLAIT AU CLOCHER DE L'ÎLE — PIRATE-LE AUSSI",
         "ou": "chapelle", "rayon": 4, "longueur": 4, "essais": 3},

        {"type": "livrer", "texte": "RAMÈNE LE CHALUTIER, SANS UNE ÉGRATIGNURE",
         "lieu": "mouillage:chalutier:0", "rayon": 5, "sans_degats": True},

        {"type": "retourner", "texte": "RETOURNE VOIR SVEN"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Sven, sous pavillon : le même calcul froid que le
    # repérage, un peu de sécheresse en plus (« ça me plaît, et ça me coûte cher ») — la
    # confiance monte d'un cran, jamais la chaleur.
    "dialogue": {
        "appel": [
            _l("sven", "C'est encore Sven. Un chalutier passe partout. Aujourd'hui, il travaille pour moi.",
               jeu="[Norwegian accent][calm] C'est encore Sven. [wryly] Un chalutier passe… partout. [firmly] Aujourd'hui, il travaille… pour moi.")
        ],
        "intro": [
            _l("sven", "L'autre quai porte un relais. Il écoute la baie pour le compte de Josée.",
               jeu="[Norwegian accent][matter-of-fact] L'autre quai porte… un relais. [coldly] Il écoute la baie… pour le compte de Josée."),
            _l("sven", "Fais-le taire. Une bonne pêche ne pose jamais de questions.",
               jeu="[Norwegian accent][firmly] Fais-le taire. [wryly] Une bonne pêche… ne pose jamais de questions."),
            _l("sven", "Le chalutier s'appelle la Belle-Josée. Je n'ai pas encore eu le temps de le rebaptiser.",
               jeu="[Norwegian accent][coldly] Le chalutier s'appelle… la Belle-Josée. [wryly] Je n'ai pas encore eu le temps… de le rebaptiser.")
        ],
        "pendant": [
            _p("sven", "Doucement. Un chalutier pressé, ça se remarque.", 1,
               jeu="[Norwegian accent][gravely] Doucement. [quietly] Un chalutier pressé… ça se remarque."),
            _p("sven", "Le boîtier est sur le quai. Reproduis ce qu'il montre, rien de plus.", 2,
               jeu="[Norwegian accent][calm] Le boîtier est… sur le quai. [matter-of-fact] Reproduis ce qu'il montre… rien de plus."),
            _p("sven", "Le relais a crié avant de se taire. Deux hommes viennent voir pourquoi.", 3,
               jeu="[Norwegian accent][gravely] Le relais a crié… avant de se taire. [coldly] Deux hommes viennent voir… pourquoi."),
            _p("sven", "Un relais ne parle jamais seul. Au clocher de l'île, quelqu'un l'écoutait encore.", 4,
               jeu="[Norwegian accent][knowingly] Un relais ne parle jamais… seul. [quietly] Au clocher de l'île… quelqu'un l'écoutait encore.")
        ],
        "fin": [
            _l("sven", "Le relais est muet. Josée regarde une baie qui ne lui dit plus rien.",
               jeu="[Norwegian accent][satisfied] Le relais est… muet. [wryly] Josée regarde une baie… qui ne lui dit plus rien."),
            _l("sven", "Tu apprends vite. Ça me plaît, et ça me coûte cher.",
               jeu="[Norwegian accent][calm] Tu apprends… vite. [wryly] Ça me plaît… et ça me coûte cher."),
            _l("sven", "Et la Belle-Josée est rentrée au quai. Elle, au moins, m'obéit.",
               jeu="[Norwegian accent][satisfied] Et la Belle-Josée est rentrée… au quai. [wryly] Elle, au moins… m'obéit.")
        ],
        "echec": [
            _l("sven", "Le relais parle encore. Recommence, avant que Josée n'écoute trop bien.",
               jeu="[Norwegian accent][coldly] Le relais parle… encore. [firmly] Recommence… avant que Josée n'écoute trop bien.")
        ]
    }

    # ⚠️ ELLE N'ÉCRIT AUCUNE SCÈNE : le premier objectif nomme `mouillage:chalutier:0`, c'est
    # lui que l'intro montre ; la fin referme chez Sven (dernier objectif `retourner`).
}
