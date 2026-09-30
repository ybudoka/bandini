"""La mission v03 — voir app/missions/__init__.py pour le moteur.

La troisième infiltration de la villa du maire (`app/blocs/villa.py`) : la cave. Par la porte de
service et l'escalier de la cuisine, un dédale de caves, deux gardes, et la chambre forte — sa porte
ne s'ouvre qu'au code, et le code est dans un terminal qu'on pirate (le labyrinthe électrifié). Le
piratage réussi met le code dans le sac (`objet` sur `pirater`) : la serrure de la chambre forte
s'ouvre. Dedans, le grand livre du maire.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "v03",
    "titre": "La chambre forte",
    "donneur": "sven",
    "prerequis": ["v02"],
    # Sur place, de nuit, au chemin de la villa (30 sept. 2026) ; gardée dans la villa jusqu'au retour chez
    # Sven — la frontière tombe au premier `retourner`.
    "sur_place": {"lieu": "villa_chemin", "heure": "nuit"},
    "frontiere": "bloc:villa",
    "recompense": 1200,
    "echec": ["mort", "arrete", "etoile", "alarme"],
    "donne": {"message": "LE GRAND LIVRE DU MAIRE, CHEZ SVEN"},

    # ⚠️ Pendant le piratage, on est cloué au terminal (`B.piratage`) et les gardes, eux, marchent :
    # celui de l'antichambre longe le mur du sud, dos au terminal quand il passe. Choisir son moment.
    "objectifs": [
        {"type": "aller", "texte": "VA À LA VILLA DU MAIRE, DE NUIT",
         "lieu": "villa_chemin", "rayon": 6, "nuit": True},

        {"type": "pirater", "texte": "PIRATE LE TERMINAL DE LA CHAMBRE FORTE, À LA CAVE",
         "ou": "villa_terminal", "rayon": 2, "longueur": 5, "essais": 3,
         "objet": "code_voute", "sans_etoile": True},

        {"type": "obtenir", "texte": "PRENDS LE GRAND LIVRE DANS LA CHAMBRE FORTE",
         "objet": "grand_livre", "nom": "LE GRAND LIVRE DU MAIRE", "dessin": "registre",
         "ou": "villa_voute", "sans_etoile": True},

        # ⚠️ Rayon 6, pas 3 (comme v01) : la bande d'herbe à l'est de la palissade mène à la sortie sans
        # passer à trois tuiles du chemin, et sous la `frontiere` la mission ratait le butin en poche.
        {"type": "aller", "texte": "RESSORS PAR LE CHEMIN, SANS TE FAIRE VOIR",
         "lieu": "villa_chemin", "rayon": 6, "sans_etoile": True},

        {"type": "retourner", "texte": "RAPPORTE LE GRAND LIVRE À SVEN"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Sven : le calcul, toujours ; pas un mot d'ici, pas une
    # familiarité. Ici, quelque chose de plus : il sait ce que vaut un maire qui doit de l'argent, et ça
    # l'amuse à peine. `[satisfied]`, jamais chaleureux, à la fin.
    "dialogue": {
        "appel": [
            _l("sven", "Sven. Le maire de cette ville tient ses comptes dans une cave. J'aimerais les lire.",
               jeu="[Norwegian accent][calm] Sven. [matter-of-fact] Le maire de cette ville tient ses comptes… dans une cave. J'aimerais les lire.")
        ],
        "intro": [
            _l("sven", "Sous la villa, une chambre forte. Dedans, un grand livre : qui le maire paie, et qui le paie.",
               jeu="[Norwegian accent][quietly] Sous la villa, une chambre forte. [matter-of-fact] Dedans, un grand livre : qui le maire paie… et qui le paie."),
            _l("sven", "La porte obéit à un terminal. Tu connais ce genre de serrure, maintenant.",
               jeu="[Norwegian accent][calm] La porte obéit à un terminal. [wryly] Tu connais ce genre de serrure… maintenant."),
            _l("sven", "Personne ne doit savoir que le livre a été ouvert. Personne ne doit te voir.",
               jeu="[Norwegian accent][firmly] Personne ne doit savoir que le livre a été ouvert. [coldly] Personne ne doit te voir.")
        ],
        "pendant": [
            _p("sven", "L'escalier de la cave est dans la cuisine. Les gardes d'en bas s'ennuient ; ne les distrais pas.", 1,
               jeu="[Norwegian accent][quietly] L'escalier de la cave est dans la cuisine. [wryly] Les gardes d'en bas s'ennuient… ne les distrais pas."),
            _p("sven", "La porte est ouverte. Le livre est vert, relié de cuir.", 2,
               jeu="[Norwegian accent][calm] La porte est ouverte. [matter-of-fact] Le livre est vert… relié de cuir."),
            _p("sven", "Bien. Maintenant, sors comme si tu n'étais jamais entré.", 3,
               jeu="[Norwegian accent][satisfied] Bien. [firmly] Maintenant, sors… comme si tu n'étais jamais entré.")
        ],
        "fin": [
            _l("sven", "Le maire doit de l'argent à trois personnes que je connais. Maintenant, il m'en doit à moi.",
               jeu="[Norwegian accent][satisfied] Le maire doit de l'argent à trois personnes que je connais. [coldly] Maintenant… il m'en doit à moi."),
            _l("sven", "Travail propre. Je ne le paie qu'une fois, et je le paie bien.",
               jeu="[Norwegian accent][matter-of-fact] Travail propre. [calm] Je ne le paie qu'une fois… et je le paie bien.")
        ],
        "echec": [
            _l("sven", "Tu n'étais pas prêt. La chambre forte sera encore là ; toi, sois plus patient.",
               jeu="[Norwegian accent][calm] Tu n'étais pas prêt. [coldly] La chambre forte sera encore là… toi, sois plus patient.")
        ]
    },
}
