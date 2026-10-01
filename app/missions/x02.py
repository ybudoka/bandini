"""La mission x02 — voir app/missions/__init__.py pour le moteur.

Le char qui part vite (M16, arc X, 1er oct. 2026) — le premier préparatif du coup. Josée a passé la commande à Gus :
un touriste de l'Hôtel Bandini se promène en coupé sport, garé dans la ruelle derrière l'hôtel. On le vole (il crie,
deux étoiles), on le fait repeindre — le garage de Ti-Guy ou une carrosserie, ce qui efface le vol et remet la police
à zéro — et on le gare à la planque. Le jour du coup (x04), il attend dans la ruelle de la caisse (`monter`, `si: x02`).

⚠️ **Gus, et pas Josée** (écart à la fiche) : un donneur donne la PREMIÈRE mission disponible de sa liste
(`disponibleDe`) — Josée, qui donne déjà le coup (x04), aurait offert le coupé à tout jamais avant lui, et le coup
ne se serait jamais joué sans ce préparatif. Gus vend à tout le monde, et connaît les chars qu'on ne déclare pas.

⚠️ `repeint` (1er oct. 2026) : `livrer` ne prend le char qu'une fois REPEINT depuis qu'on y est monté
(`Missions.repeindre` le marque) — la ligne d'objectif dit quoi faire tant qu'il ne l'est pas.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "x02",
    "titre": "Le char qui part vite",
    "donneur": "gus",
    "prerequis": ["x01"],
    "recompense": 150,
    "donne": {"message": "LE COUPÉ DORT À LA PLANQUE, REPEINT"},

    "objectifs": [
        {"type": "monter", "texte": "LE COUPÉ D'UN TOURISTE, DERRIÈRE L'HÔTEL : PRENDS-LE",
         "vehicule": "sport", "ou": "ruelle:hotel:6"},

        {"type": "livrer", "texte": "FAIS-LE REPEINDRE, PUIS GARE-LE À LA PLANQUE",
         "lieu": "planque", "rayon": 5, "repeint": True, "etoiles": 2},
    ],

    # Intention (intro) : Gus derrière son comptoir, les bras croisés ; la caméra va voir la ruelle de l'hôtel sous sa
    # première phrase, et revient pour le prix — il ne donne jamais un ordre, il pose un prix.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "ruelle:hotel:6", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Gus : sec, transactionnel, une phrase, un prix, la porte. Il bougonne qu'on
    # le dérange pour une commande de Josée, et le seul fond de chaleur est pour le char, pas pour toi.
    "dialogue": {
        "appel": [
            _l("gus", "Gus, de l'armurerie. Josée veut un char qui part vite, pis c'est moi qui fournis. Passe.",
               jeu="[gruffly] Gus, de l'armurerie. [annoyed] Josée veut un char qui part vite, pis c'est moi qui fournis. Passe.")
        ],
        "intro": [
            _l("gus", "Un touriste de l'hôtel se promène en coupé sport. Il le gare dans la ruelle, derrière.",
               jeu="[matter-of-fact] Un touriste de l'hôtel se promène en coupé sport. Il le gare dans la ruelle, derrière."),
            _l("gus", "Tu le prends, tu le fais repeindre, chez Ti-Guy ou ailleurs. Pis tu le gares à ta planque.",
               jeu="[gruffly] Tu le prends, tu le fais repeindre, chez Ti-Guy ou ailleurs. [matter-of-fact] Pis tu le gares à ta planque."),
            _l("gus", "Un char volé, ça se cherche. Un char repeint, c'est un char neuf. C'est cent cinquante pour ta peine.",
               jeu="[matter-of-fact] Un char volé, ça se cherche. Un char repeint, c'est un char neuf. [gruffly] C'est cent cinquante pour ta peine.")
        ],
        "pendant": [
            _p("gus", "Le coupé, derrière l'hôtel. Le touriste dort jusqu'à midi, il a fêté en masse.", 0,
               jeu="[matter-of-fact] Le coupé, derrière l'hôtel. [deadpan] Le touriste dort jusqu'à midi… il a fêté en masse."),
            _p("gus", "Y s'est réveillé, ton touriste. Une couche de peinture, pis la police cherchera un autre char.", 1,
               jeu="[annoyed] Y s'est réveillé, ton touriste. [gruffly] Une couche de peinture, pis la police cherchera un autre char.")
        ],
        "fin": [
            _l("gus", "Repeint, à la planque. Le jour du coup, un gars de Josée va le parquer derrière la caisse.",
               jeu="[satisfied] Repeint, à la planque. [matter-of-fact] Le jour du coup, un gars de Josée va le parquer derrière la caisse."),
            _l("gus", "D'ici là, pas de balade. Un char qui part vite, ça se garde comme une bonne bouteille.",
               jeu="[gruffly] D'ici là, pas de balade. [deadpan] Un char qui part vite, ça se garde comme une bonne bouteille.")
        ],
        "echec": [
            _l("gus", "Le coupé est fini. Josée va me demander pourquoi, pis je vais lui donner ton nom.",
               jeu="[annoyed] Le coupé est fini. [gruffly] Josée va me demander pourquoi… pis je vais lui donner ton nom.")
        ]
    }
}
