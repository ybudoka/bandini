"""La mission q15 — voir app/missions/__init__.py pour le moteur.

La liste de Ti-Loup (M16, arc Q, 1er oct. 2026) — la variante de q14 pour qui a choisi Josée (q11). Les camions de Sven
ont sauté, son cargo ne charge plus rien ; mais ses clients de Bergen ont encore faim, et c'est Ti-Loup qu'ils appellent :
pas pour des chars, pour des PIÈCES. Un taxi derrière le terminus (`monter`), livré au lot de la fourrière sans une bosse
(`livrer`, `sans_degats`) ; Ti-Loup le démonte, on revient une demi-journée plus tard (`attendre`) ; puis le cabriolet
rose d'un dentiste, derrière le dépanneur des Érables — son alarme crie —, au lot lui aussi ; et Ti-Loup paie dans sa cour
(`retourner`).

Après elle, l'ardoise du quai est à lui (`economie.LISTE_DU_QUAI["brule"]`) : quatre modèles, un par jour, livrés à
son lot. C'est la fiche : « Sven — ou Ti-Loup si on l'a brûlé — affiche quatre modèles ».
"""

from ._commun import _l, _p

MISSION = {
    "slug": "q15",
    "titre": "La liste de Ti-Loup",
    "donneur": "tiloup",
    # ⚠️ q11, pas q10 : c'est l'envers de q14 (Sven), et les deux ne s'offrent jamais à la même partie (`ferme` de q10/q11).
    # s02 : Ti-Loup te connaît (sa première mission), et il est arrivé au lot (`arrive_apres: s01`).
    "prerequis": ["q11", "s02"],
    "recompense": 250,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"message": "TI-LOUP TIENT L'ARDOISE DU QUAI"},

    "objectifs": [
        {"type": "monter", "texte": "LE PREMIER : UN TAXI, DERRIÈRE LE TERMINUS", "vehicule": "taxi",
         "ou": "ruelle:terminus:10"},

        {"type": "livrer", "texte": "AU LOT DE TI-LOUP — SANS UNE BOSSE", "lieu": "fourriere", "rayon": 6,
         "sans_degats": True},

        {"type": "attendre", "texte": "TI-LOUP LE DÉMONTE — LE DEUXIÈME DANS UNE DEMI-JOURNÉE", "heures": 12},

        {"type": "monter", "texte": "LE DEUXIÈME : LE CABRIOLET ROSE, DERRIÈRE LE DÉPANNEUR", "vehicule": "cabriolet",
         "ou": "ruelle:depanneur:12"},

        {"type": "livrer", "texte": "AU LOT, LUI AUSSI — SANS UNE ÉGRATIGNURE", "lieu": "fourriere", "rayon": 6,
         "sans_degats": True},

        {"type": "retourner", "texte": "TI-LOUP PAIE DANS SA COUR"},
    ],

    # Intention (intro) : Ti-Loup dans sa cour, les bras croisés devant ses chevalets vides — un artisan qui a une
    # commande ; la caméra va voir le terminus (le taxi y dort), puis revient pour la règle : une pièce bossée ne vaut rien.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:terminus", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Ti-Loup : sec, des chiffres, « comptant » ; il parle de tôle comme d'autres
    # parlent de vin. `[wryly]` pour ce qui le fait rire tout seul, `[satisfied]` devant du beau métal, jamais chaleureux.
    "dialogue": {
        "appel": [
            _l("tiloup", "Ti-Loup, la ferraille. Le Norvégien a plus de cale, mais ses clients ont encore faim.",
               jeu="[gruffly] Ti-Loup, la ferraille. [wryly] Le Norvégien a plus de cale, mais ses clients ont encore faim.")
        ],
        "intro": [
            _l("tiloup", "C'est moi qu'ils appellent, astheure. Pas pour des chars : pour des pièces.",
               jeu="[matter-of-fact] C'est moi qu'ils appellent, astheure. [wryly] Pas pour des chars : pour des pièces."),
            _l("tiloup", "Un taxi derrière le terminus. Pis après, un cabriolet rose aux Érables.",
               jeu="[matter-of-fact] Un taxi derrière le terminus. [deadpan] Pis après, un cabriolet rose aux Érables."),
            _l("tiloup", "Une pièce bossée, ça vaut rien. Ramène-les-moi comme au salon.",
               jeu="[firmly] Une pièce bossée, ça vaut rien. [gruffly] Ramène-les-moi comme au salon.")
        ],
        "pendant": [
            _p("tiloup", "Le taxi dort derrière le terminus. Un moteur de taxi, ça roule un million.", 0,
               jeu="[deadpan] Le taxi dort derrière le terminus. [wryly] Un moteur de taxi, ça roule un million."),
            _p("tiloup", "Au lot, doucement. Je démonte pas des accordéons.", 1,
               jeu="[gruffly] Au lot, doucement. [wryly] Je démonte pas des accordéons."),
            _p("tiloup", "Beau moteur. Je le démonte cette nuit, le cabriolet viendra après.", 2,
               jeu="[satisfied] Beau moteur. [matter-of-fact] Je le démonte cette nuit, le cabriolet viendra après."),
            _p("tiloup", "Le cabriolet du dentiste, derrière le dépanneur. Son alarme crie, mais elle mord pas.", 3,
               jeu="[deadpan] Le cabriolet du dentiste, derrière le dépanneur. [wryly] Son alarme crie, mais elle mord pas."),
            _p("tiloup", "Au lot, sans une égratignure. Le cuir rose, ça se vend cher à Bergen.", 4,
               jeu="[firmly] Au lot, sans une égratignure. [matter-of-fact] Le cuir rose, ça se vend cher à Bergen."),
            _p("tiloup", "Les deux sont sur mes chevalets. Viens chercher ton argent.", 5,
               jeu="[satisfied] Les deux sont sur mes chevalets. [gruffly] Viens chercher ton argent.")
        ],
        "fin": [
            _l("tiloup", "Deux chars, pas une bosse. T'aurais fait un bon débosseleur.",
               jeu="[satisfied] Deux chars, pas une bosse. [wryly] T'aurais fait un bon débosseleur."),
            _l("tiloup", "L'ardoise du quai, c'est moi qui la tiens, astheure. Un modèle par jour, à mon lot, comptant.",
               jeu="[matter-of-fact] L'ardoise du quai, c'est moi qui la tiens, astheure. [gruffly] Un modèle par jour, à mon lot, comptant.")
        ],
        "echec": [
            _l("tiloup", "Des pièces bossées, c'est bon pour le compacteur. Pis des cubes, j'en ai plein.",
               jeu="[deadpan] Des pièces bossées, c'est bon pour le compacteur. [gruffly] Pis des cubes, j'en ai plein.")
        ]
    }
}
