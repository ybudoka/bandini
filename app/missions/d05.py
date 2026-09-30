"""La mission d05 — voir app/missions/__init__.py pour le moteur.

L'avocat du Carré (M16, arc D, 30 sept. 2026). Sal a mis un huissier sur le garage (la garantie de d01) ; Josée
connaît le seul homme de la ville qui gagne contre un huissier : Me Desjardins, qui tient sa table au fond du
Brouillard. Il lui faut les papiers de Rocco — l'acte du garage, caché par l'oncle derrière la porte de la baie.
On les prend, deux Ciseaux de Sal veulent les mêmes, et on les porte au Brouillard. Le casier y perd deux pages
(Me Desjardins ne travaille jamais pour rien : il efface ce qu'il peut).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "d05",
    "titre": "L'avocat du Carré",
    "donneur": "josee",
    "prerequis": ["d04"],
    "recompense": 150,
    "donne": {"casier": -2, "message": "LE GARAGE RESTE À TON NOM — ET DEUX PAGES DE MOINS"},

    # ⚠️ `obtenir` dans la ville (le patron de c03 et h04) : les papiers sont posés devant le garage, on les ramasse
    # à pied. Les deux Ciseaux arrivent de loin (`loin`) où l'on est. ⚠️ Me Desjardins est un PIÉTON à menu (sa
    # table au Brouillard), pas un personnage : on ne lui « parle » pas en objectif — on rapporte les papiers à
    # Josée, dans le même bar, et c'est elle qui les lui passe. Josée est DEDANS : pas de `retourner`.
    "objectifs": [
        {"type": "obtenir", "texte": "LES PAPIERS DE ROCCO SONT CACHÉS AU GARAGE",
         "objet": "papiers_de_rocco", "ou": "garage", "dessin": "dossier", "nom": "L'ACTE DU GARAGE"},

        {"type": "tuer", "texte": "DEUX CISEAUX DE SAL VEULENT LES PAPIERS",
         "groupe": "cravates", "n": 2, "loin": 10, "arme": "poing_americain"},

        {"type": "parler", "texte": "LES PAPIERS AU BROUILLARD, POUR ME DESJARDINS", "cible": "josee"},
    ],

    # Intention (intro) : Josée derrière son bar, le verre qu'elle essuie — un geste, sa réplique tient le plan ; la
    # coupe montre le garage sous la deuxième ; la troisième, sur le noir qui revient au bar, où l'avocat attend.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:garage", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Josée : le ton des affaires, sec, le « on » des chefs ; une seule
    # chaleur, rangée à la fin. Elle méprise les huissiers plus que les gangs.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. Sal a envoyé un huissier sur ton garage. Viens au bar, on a un avocat.",
               jeu="[coldly] Josée. Sal a envoyé un huissier sur ton garage. [matter-of-fact] Viens au bar, on a un avocat.")
        ],
        "intro": [
            _l("josee", "Un huissier, c'est un voleur avec un papier. Contre un papier, il faut un meilleur papier.",
               jeu="[matter-of-fact] Un huissier, c'est un voleur avec un papier. [confident] Contre un papier, il faut un meilleur papier."),
            _l("josee", "L'acte du garage. Rocco le cachait derrière la porte de la baie, dans une boîte à outils.",
               jeu="[knowingly] L'acte du garage. [quietly] Rocco le cachait derrière la porte de la baie, dans une boîte à outils."),
            _l("josee", "Apporte-le ici. Me Desjardins a sa table au fond. Il coûte cher, pis il perd jamais.",
               jeu="[matter-of-fact] Apporte-le ici. Me Desjardins a sa table au fond. [coldly] Il coûte cher, pis il perd jamais.")
        ],
        "pendant": [
            _p("josee", "Une boîte rouge, pleine de graisse. Rocco pensait que personne fouillerait là.", 0,
               jeu="[matter-of-fact] Une boîte rouge, pleine de graisse. [wryly] Rocco pensait que personne fouillerait là."),
            _p("josee", "Sal a eu la même idée. Ses Ciseaux arrivent, pis ils frappent avec des bagues.", 1,
               jeu="[coldly] Sal a eu la même idée. [menacingly] Ses Ciseaux arrivent, pis ils frappent avec des bagues."),
            _p("josee", "Viens au bar. L'avocat a commandé un deuxième scotch sur ton compte.", 2,
               jeu="[calm] Viens au bar. [wryly] L'avocat a commandé un deuxième scotch sur ton compte.")
        ],
        "fin": [
            _l("josee", "Desjardins a lu, il a souri. L'huissier retourne chez Sal les mains vides.",
               jeu="[satisfied] Desjardins a lu, il a souri. [coldly] L'huissier retourne chez Sal les mains vides."),
            _l("josee", "Pis il a déchiré deux pages de ton casier en passant. Il appelle ça un cadeau d'ouverture.",
               jeu="[matter-of-fact] Pis il a déchiré deux pages de ton casier en passant. [warmly] Il appelle ça un cadeau d'ouverture.")
        ],
        "echec": [
            _l("josee", "Pas de papier, pas d'avocat. Le garage est à Sal tant qu'on prouve rien.",
               jeu="[coldly] Pas de papier, pas d'avocat. [matter-of-fact] Le garage est à Sal tant qu'on prouve rien.")
        ]
    }
}
