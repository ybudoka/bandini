"""La mission v02 — voir app/missions/__init__.py pour le moteur.

La deuxième infiltration de la villa du maire (`app/blocs/villa.py`) : avec la clé de v01, on entre
par la porte de service (une serrure du bloc, condition `objet`), on traverse le rez-de-chaussée,
on monte le grand escalier du hall, on traverse l'étage jusqu'à l'escalier de la bibliothèque, et on
trouve au 2e étage le dossier que le maire garde sur le sergent, dans son bureau — des gardes à chaque
étage (`villa.GARDES`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "v02",
    "titre": "Le dossier du sergent",
    "donneur": "bouchard",
    "prerequis": ["v01"],
    # Sur place, de nuit, au chemin de la villa (30 sept. 2026), et gardée dans la villa.
    "sur_place": {"lieu": "villa_chemin", "heure": "nuit"},
    "frontiere": "bloc:villa",
    "recompense": 700,
    "echec": ["mort", "arrete", "etoile"],
    # ⚠️ `casier: -2` : Bouchard efface deux pages de ton casier — c'est ce qu'un sergent paie en
    # plus, quand c'est sa propre peau qu'on vient de sauver.
    "donne": {"message": "DEUX PAGES DE MOINS À TON CASIER", "casier": -2},

    # ⚠️ Le dossier se pose au bureau (`villa_bureau`) quand on est dans la villa, et se ramasse en
    # marchant dessus (`Infiltration`). Raté, il retombe (`Infiltration.rendre`) : la mission se
    # refait du début.
    "objectifs": [
        {"type": "aller", "texte": "VA À LA VILLA DU MAIRE, DE NUIT",
         "lieu": "villa_chemin", "rayon": 6, "nuit": True},

        {"type": "aller", "texte": "ENTRE PAR LA PORTE DE SERVICE, AVEC TA CLÉ",
         "lieu": "villa_service", "rayon": 2, "sans_etoile": True},

        {"type": "obtenir", "texte": "TROUVE LE DOSSIER, DANS LE BUREAU D'EN HAUT",
         "objet": "dossier_bouchard", "nom": "LE DOSSIER DU SERGENT", "dessin": "dossier",
         "ou": "villa_bureau", "sans_etoile": True},

        # ⚠️ Rayon 6, pas 3 (comme v01) : la bande d'herbe à l'est de la palissade mène à la sortie sans
        # passer à trois tuiles du chemin, et sous la `frontiere` la mission ratait le butin en poche.
        {"type": "aller", "texte": "RESSORS PAR LE CHEMIN, SANS TE FAIRE VOIR",
         "lieu": "villa_chemin", "rayon": 6, "sans_etoile": True},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Bouchard : un homme qui a peur et qui commande pour ne pas
    # le montrer. Il ne dit pas « s'il te plaît », mais il appelle lui-même, et il parle trop vite. Le
    # `[nervously]` monte d'une réplique à l'autre ; `[satisfied]` et « Propre. » à la fin, et rien d'autre.
    "dialogue": {
        "appel": [
            _l("bouchard", "Salut, le jeune, c'est Bouchard. Paraît que t'as une clé qui m'intéresse.",
               jeu="[gruffly] Salut, le jeune, c'est Bouchard. [knowingly] Paraît que t'as une clé qui m'intéresse.")
        ],
        "intro": [
            _l("bouchard", "Le maire garde un dossier sur moi. Des enveloppes, des dates, des photos.",
               jeu="[gravely] Le maire garde un dossier sur moi. [nervously] Des enveloppes, des dates… des photos."),
            _l("bouchard", "Il est dans son bureau, en haut de la villa. Tu rentres par la porte de service, tu le prends.",
               jeu="[firmly] Il est dans son bureau, en haut de la villa. [matter-of-fact] Tu rentres par la porte de service, tu le prends."),
            _l("bouchard", "Si un garde te voit, je te connais pas. Pis toi non plus, tu me connais pas.",
               jeu="[nervously] Si un garde te voit, je te connais pas. [menacingly] Pis toi non plus, tu me connais pas.")
        ],
        "pendant": [
            _p("bouchard", "La porte de service, derrière la cuisine. Ta clé fait le reste.", 1,
               jeu="[quietly] La porte de service, derrière la cuisine. [matter-of-fact] Ta clé fait le reste."),
            _p("bouchard", "Le grand escalier est dans le hall. Le gars du hall regarde la porte d'en avant, pas son dos.", 2,
               jeu="[quietly] Le grand escalier est dans le hall. [knowingly] Le gars du hall regarde la porte d'en avant, pas son dos."),
            _p("bouchard", "Tu l'as? Sors de là. Tranquille, comme un gars qui a rien vu.", 3,
               jeu="[nervously] Tu l'as? [firmly] Sors de là. Tranquille, comme un gars qui a rien vu.")
        ],
        "fin": [
            _l("bouchard", "Propre. Ce dossier-là va faire une belle flamme dans le poêle du poste.",
               jeu="[satisfied] Propre. [deadpan] Ce dossier-là va faire une belle flamme dans le poêle du poste."),
            _l("bouchard", "Pis ton casier maigrit de deux pages. Entre nous, ça s'appelle de la gratitude.",
               jeu="[knowingly] Pis ton casier maigrit de deux pages. [deadpan] Entre nous, ça s'appelle de la gratitude.")
        ],
        "echec": [
            _l("bouchard", "J'ai rien vu, j'ai rien entendu. Pis le maire, lui, a tout vu.",
               jeu="[nervously] J'ai rien vu, j'ai rien entendu. [gravely] Pis le maire, lui, a tout vu.")
        ]
    },

    # Intention (intro) : Bouchard dans son casse-croûte, les bras croisés comme un homme qui attend un
    # verdict ; la caméra va voir le bout du chemin des Érables pendant qu'il parle du dossier.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "bloc:villa", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [3]},
        ],
    },
}
