"""La mission s12 — voir app/missions/__init__.py pour le moteur.

Le dernier char du lot (M16, arc S, 30 sept. 2026). Gilles prend sa retraite. Trente ans à la guérite de la
fourrière ; il veut finir en beauté : cinq remorquages dans la journée, comme dans le temps. Puis il donne sa
vieille remorqueuse au neveu — « elle connaît toutes les rues, pis moi, je m'en vais au lac ».
"""

from ._commun import _l, _p

MISSION = {
    "slug": "s12",
    "titre": "Le dernier char du lot",
    "donneur": "gilles",
    "prerequis": ["s08"],
    "recompense": 150,
    "donne": {"vehicule": "remorqueuse", "message": "LA REMORQUEUSE DE GILLES EST GARÉE À LA PLANQUE"},

    # ⚠️ `boulots` remorquage (le patron de s02) : seuls les chars remorqués pendant la mission comptent. Gilles se tient
    # dans la cour du lot (`dans_la_cour`), dehors : `retourner` le trouve. `donne.vehicule` gare la remorqueuse à la
    # planque (le taxi de m97).
    "objectifs": [
        {"type": "monter", "texte": "LA VIEILLE REMORQUEUSE DE GILLES, AU LOT",
         "vehicule": "remorqueuse", "ou": "porte:fourriere"},

        {"type": "boulots", "texte": "CINQ REMORQUAGES, COMME DANS LE TEMPS", "n": 5, "sorte": "remorquage"},

        {"type": "retourner", "texte": "RAMÈNE-LA À GILLES, UNE DERNIÈRE FOIS"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Gilles : la mélancolie tranquille d'un homme qui compte les années ; la
    # fierté, une fois, sur « comme dans le temps ».
    "dialogue": {
        "appel": [
            _l("gilles", "C'est Gilles, de la fourrière. Vendredi, je rends mes clés. Viens me voir, le jeune.",
               jeu="[somber] C'est Gilles, de la fourrière. Vendredi, je rends mes clés. [tenderly] Viens me voir, le jeune.")
        ],
        "intro": [
            _l("gilles", "Trente ans à la guérite. Je veux finir comme j'ai commencé : dans la remorqueuse.",
               jeu="[somber] Trente ans à la guérite. [tenderly] Je veux finir comme j'ai commencé : dans la remorqueuse."),
            _l("gilles", "Cinq chars dans la journée. Je conduis plus, mes yeux veulent pas. Toi, tu conduis.",
               jeu="[gravely] Cinq chars dans la journée. Je conduis plus, mes yeux veulent pas. [firmly] Toi, tu conduis."),
            _l("gilles", "Pis après, elle est à toi. Elle connaît toutes les rues, moi je m'en vais au lac.",
               jeu="[tenderly] Pis après, elle est à toi. [relieved] Elle connaît toutes les rues, moi je m'en vais au lac.")
        ],
        "pendant": [
            _p("gilles", "Elle tire à droite quand elle freine. On se fait une raison.", 0,
               jeu="[gravely] Elle tire à droite quand elle freine. [tenderly] On se fait une raison."),
            _p("gilles", "Klaxonne, le répartiteur te donne une adresse. Comme dans le temps.", 1,
               jeu="[matter-of-fact] Klaxonne, le répartiteur te donne une adresse. [relieved] Comme dans le temps."),
            _p("gilles", "Cinq. Reviens au lot, j'ai quelque chose à te dire avant de partir.", 2,
               jeu="[somber] Cinq. [tenderly] Reviens au lot, j'ai quelque chose à te dire avant de partir.")
        ],
        "fin": [
            _l("gilles", "Cinq chars, pas une égratignure. Ton oncle conduisait comme un pied, lui.",
               jeu="[relieved] Cinq chars, pas une égratignure. [tenderly] Ton oncle conduisait comme un pied, lui."),
            _l("gilles", "Elle est garée à ta planque. Prends-en soin, pis passe me voir au lac.",
               jeu="[tenderly] Elle est garée à ta planque. [somber] Prends-en soin, pis passe me voir au lac.")
        ],
        "echec": [
            _l("gilles", "Bon. On dira que la retraite a commencé un peu plus tôt.",
               jeu="[somber] Bon. [gravely] On dira que la retraite a commencé un peu plus tôt.")
        ]
    }
}
