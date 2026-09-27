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

    # ⚠️ **PREMIER USAGE DU PIRATAGE** (type `pirater` : un labyrinthe électrifié depuis le
    # 27 sept. 2026, `circuit.js` — l'étincelle au stick, le même axe que la marche). Deux quais de chalutier
    # existent dans chaque ville (`navires.FLOTTE`) : on prend celui-ci, on pirate l'autre — un
    # chalutier ne se remarque pas comme une chaloupe qui traverse toute la baie de nuit.
    "objectifs": [
        {"type": "monter", "texte": "PRENDS LE CHALUTIER, AU QUAI DE SVEN",
         "vehicule": "chalutier", "ou": "mouillage:chalutier:0", "prete": "sven"},

        # ⚠️ **Le titre, c'est ça** : l'autre quai n'est qu'à une dizaine de tuiles (les deux
        # chalutiers se rangent autour du cargo, `navires.amarrer`) — on n'y va pas en bateau pour
        # la distance, mais parce qu'un chalutier au nom de Josée s'amarre à SON relais sans que
        # personne regarde. Naviguer sous pavillon.
        {"type": "livrer", "texte": "AMARRE-LE AU RELAIS — SOUS SON NOM, PERSONNE NE REGARDE",
         "lieu": "mouillage:chalutier:1", "rayon": 5, "sans_etoile": True},

        {"type": "pirater", "texte": "PIRATE LE RELAIS — SANS TOUCHER LES FILS",
         "ou": "mouillage:chalutier:1", "rayon": 5, "longueur": 4, "essais": 3},

        # ⚠️ **Plus long, plus loin** (Martin, 22 sept. 2026 : « des missions plus longues ») : le
        # relais a crié avant de se taire — deux Morues accourent (`loin` : elles naissent hors
        # champ et courent sur toi) ; puis on suit son fil jusqu'au clocher de l'Île-aux-Corneilles,
        # à l'autre bout de la baie, en chalutier. `ou` et pas `lieu` pour l'île : elle ne se
        # rejoint pas à pied (`test_barrieres.py`).
        {"type": "tuer", "texte": "DEUX MORUES ACCOURENT — LE RELAIS A CRIÉ",
         "groupe": "morues", "n": 2, "ou": "donneur", "loin": 12},

        {"type": "pirater", "texte": "EN CHALUTIER JUSQU'AU CLOCHER DE L'ÎLE — PIRATE SON RELAIS",
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
            _l("sven", "Le chalutier s'appelle la Belle-Josée. Sous ce nom-là, personne ne le regarde.",
               jeu="[Norwegian accent][coldly] Le chalutier s'appelle… la Belle-Josée. [wryly] Sous ce nom-là… personne ne le regarde.")
        ],
        "pendant": [
            _p("sven", "Doucement. Un chalutier pressé, ça se remarque.", 1,
               jeu="[Norwegian accent][gravely] Doucement. [quietly] Un chalutier pressé… ça se remarque."),
            _p("sven", "Le boîtier est sur le quai. Suis le courant jusqu'au bout, sans toucher les fils.", 2,
               jeu="[Norwegian accent][calm] Le boîtier est… sur le quai. [matter-of-fact] Suis le courant jusqu'au bout… sans toucher les fils."),
            _p("sven", "Le relais a crié avant de se taire. Deux hommes viennent voir pourquoi.", 3,
               jeu="[Norwegian accent][gravely] Le relais a crié… avant de se taire. [coldly] Deux hommes viennent voir… pourquoi."),
            _p("sven", "La lunette du clocher n'était pas seule. Un relais y écoute encore.", 4,
               jeu="[Norwegian accent][knowingly] La lunette du clocher… n'était pas seule. [quietly] Un relais y écoute… encore.")
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
            _l("sven", "Josée écoute encore la baie. Recommence, avant qu'elle écoute trop bien.",
               jeu="[Norwegian accent][coldly] Josée écoute encore… la baie. [firmly] Recommence… avant qu'elle écoute trop bien.")
        ]
    }

    # ⚠️ ELLE N'ÉCRIT AUCUNE SCÈNE : le premier objectif nomme `mouillage:chalutier:0`, c'est
    # lui que l'intro montre ; la fin referme chez Sven (dernier objectif `retourner`).
}
