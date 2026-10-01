"""La mission s13 — voir app/missions/__init__.py pour le moteur.

Le prototype (M16, arc S, 1er oct. 2026). Un coupé sport que l'usine Prévost a monté pour une foire de Détroit a
disparu de la cour ; il dort au stationnement des Skateux, à La Pointe. Prévost le veut sans une égratignure et sans
police dans sa cour : on le reprend (`monter`), on saute la rampe des Skateux pour sortir du stationnement
(`sauter`, 30 px de vol), et on le laisse chez Gilles, à la fourrière, où ses hommes le prendront (`livrer`,
`sans_degats` : la prime) — un char des Chevreuils te colle tout le long (`poursuite`).

⚠️ Écarts à la fiche : livré à la fourrière, pas à l'usine (sa cour ferme la nuit, elle n'est jamais un lieu de
mission) ; le pont n'est pas bloqué — les Chevreuils te suivent.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "s13",
    "titre": "Le prototype",
    "donneur": "prevost",
    "prerequis": ["s07"],
    "recompense": 400,
    "donne": {"message": "PRÉVOST A SON PROTOTYPE"},

    "objectifs": [
        {"type": "monter", "texte": "LE PROTOTYPE DORT CHEZ LES SKATEUX", "vehicule": "sport", "ou": "zone:skateux",
         "prete": "prevost"},

        {"type": "sauter", "texte": "SORS DU STATIONNEMENT PAR LA RAMPE — 30 PX", "vol_px": 30},

        {"type": "livrer", "texte": "À LA FOURRIÈRE, CHEZ GILLES — PAS UNE ÉGRATIGNURE", "lieu": "fourriere",
         "rayon": 6, "sans_degats": True, "poursuite": {"groupe": "chevreuils", "chars": 1}},
    ],

    # Intention (intro, dedans) : le patron derrière son bureau, qui parle d'un char comme d'un actionnaire ; la caméra
    # sort voir La Pointe, au bout de la ville, puis revient pour ce qu'il exige — pas de police dans sa cour.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "rampe:pointe", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Prévost : des phrases de conseil d'administration ; froid, sûr de lui,
    # et pour une fois il a besoin de quelqu'un — il ne le dira pas.
    "dialogue": {
        "appel": [
            _l("prevost", "Réjean Prévost. Un bien de l'usine a quitté la cour sans facture. Je veux le récupérer.",
               jeu="[coldly] Réjean Prévost. [matter-of-fact] Un bien de l'usine a quitté la cour sans facture. Je veux le récupérer.")
        ],
        "intro": [
            _l("prevost", "Un prototype. Monté ici, pour la foire de Détroit. Il dort chez les Skateux, à La Pointe.",
               jeu="[matter-of-fact] Un prototype. Monté ici, pour la foire de Détroit. [coldly] Il dort chez les Skateux, à La Pointe."),
            _l("prevost", "Leur stationnement n'a qu'une sortie qui vaille : la rampe. Je ne veux pas savoir comment.",
               jeu="[matter-of-fact] Leur stationnement n'a qu'une sortie qui vaille : la rampe. [smugly] Je ne veux pas savoir comment."),
            _l("prevost", "Laissez-le chez Gilles, à la fourrière. Pas de police dans ma cour. Pas une égratignure.",
               jeu="[coldly] Laissez-le chez Gilles, à la fourrière. [firmly] Pas de police dans ma cour. Pas une égratignure.")
        ],
        "pendant": [
            _p("prevost", "Le coupé gris, au fond du stationnement. Les clés sont dessus, ils ne savent pas conduire.", 0,
               jeu="[matter-of-fact] Le coupé gris, au fond du stationnement. [smugly] Les clés sont dessus, ils ne savent pas conduire."),
            _p("prevost", "La rampe. Trente pieds de vol, c'est dans ses spécifications.", 1,
               jeu="[coldly] La rampe. [matter-of-fact] Trente pieds de vol, c'est dans ses spécifications."),
            _p("prevost", "Les Chevreuils vous suivent. Un concurrent, sans doute. Ne leur laissez rien.", 2,
               jeu="[coldly] Les Chevreuils vous suivent. [wryly] Un concurrent, sans doute. [firmly] Ne leur laissez rien.")
        ],
        "fin": [
            _l("prevost", "Gilles m'a appelé. Le prototype est intact. Votre facture sera honorée.",
               jeu="[matter-of-fact] Gilles m'a appelé. Le prototype est intact. [coldly] Votre facture sera honorée."),
            _l("prevost", "Détroit ne saura jamais qu'il a dormi chez des enfants.",
               jeu="[smugly] Détroit ne saura jamais… [coldly] qu'il a dormi chez des enfants.")
        ],
        "echec": [
            _l("prevost", "Le prototype est perdu. Je passerai ça aux pertes, avec vous dedans.",
               jeu="[coldly] Le prototype est perdu. [matter-of-fact] Je passerai ça aux pertes… avec vous dedans.")
        ]
    }
}
