"""La mission s05 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "s05",
    "titre": "Gros-Boulon te parle",
    "donneur": "boulon",
    "prerequis": ["s02"],
    "recompense": 400,
    # ⚠️ `calme` (M16) : les Boulonneux te laissent vivre — la seule façon de marcher dans La Shop.
    "donne": {"calme": "boulonneux", "message": "LES BOULONNEUX TE LAISSENT VIVRE"},

    # La berline de luxe de Prévost dort dans la ruelle de l'usine (`ruelle:usine`, un `ou` : ⚠️ jamais `usine`
    # comme `lieu`, sa cour ferme la nuit) ; on la livre au compacteur de Ti-Loup, à la fourrière.
    "objectifs": [
        {"type": "monter", "texte": "VOLE LA BERLINE DE PRÉVOST, DERRIÈRE L'USINE", "vehicule": "luxe", "ou": "ruelle:usine:10"},

        {"type": "livrer", "texte": "LIVRE-LA AU COMPACTEUR DE TI-LOUP", "lieu": "fourriere", "rayon": 4},

        {"type": "retourner", "texte": "RETOURNE VOIR GROS-BOULON"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Gros-Boulon : un gros homme en colère depuis deux ans, qui a appris à la
    # garder pour les bonnes occasions. Il parle lentement, il cogne les mots. Il ne remercie pas : il paie.
    "dialogue": {
        "appel": [
            _l("boulon", "Gros-Boulon, Marcel pour ma mère. Ti-Loup dit que t'es correct, on va voir.",
               jeu="[gruffly] Gros-Boulon… [wryly] Marcel pour ma mère. [coldly] Ti-Loup dit que t'es correct… on va voir.")
        ],
        "intro": [
            _l("boulon", "Prévost nous a mis dehors, deux cents gars, un vendredi. Lui, il a gardé sa berline.",
               jeu="[bitterly] Prévost nous a mis dehors, deux cents gars, un vendredi. [angry] Lui, il a gardé sa berline."),
            _l("boulon", "Elle dort derrière l'usine. Je la veux en cube, chez Ti-Loup.",
               jeu="[menacingly] Elle dort derrière l'usine. [firmly] Je la veux en cube, chez Ti-Loup."),
            _l("boulon", "Fais ça, pis mes gars vont arrêter de te regarder de travers.",
               jeu="[calm] Fais ça… [serious] pis mes gars vont arrêter de te regarder de travers.")
        ],
        "pendant": [
            _p("boulon", "Du cuir, pis de l'air climatisé. Payé avec nos paies.", 0,
               jeu="[bitterly] Du cuir, pis de l'air climatisé. [angry] Payé avec nos paies."),
            _p("boulon", "Au compacteur. Ti-Loup t'attend, la mâchoire ouverte.", 1,
               jeu="[satisfied] Au compacteur. [amused] Ti-Loup t'attend, la mâchoire ouverte."),
            _p("boulon", "Un cube. Viens me voir, faut que je te regarde.", 2,
               jeu="[gruffly] Un cube. [quietly] Viens me voir… faut que je te regarde.")
        ],
        "fin": [
            _l("boulon", "Prévost va chercher sa berline toute la semaine. Moi, je vais dormir.",
               jeu="[laughs] [satisfied] Prévost va chercher sa berline toute la semaine. [amused] Moi, je vais dormir."),
            _l("boulon", "T'es des nôtres, astheure. Dans La Shop, personne te touche.",
               jeu="[warmly] T'es des nôtres, astheure. [firmly] Dans La Shop, personne te touche.")
        ],
        "echec": [
            _l("boulon", "Sa berline roule encore. Mes gars vont rire de moi.",
               jeu="[angry] Sa berline roule encore. [bitterly] Mes gars vont rire de moi.")
        ]
    }
}
