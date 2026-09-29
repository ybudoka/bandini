"""La mission p11 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "p11",
    "titre": "Zed et la Chef",
    "donneur": "josee",
    "prerequis": ["p09", "p10"],
    "recompense": 500,
    # ⚠️ LA TROISIÈME LIBÉRATION DE CES VAGUES (`libere: pointe`) : les Skateux rangent leurs planches — plus un ne
    # traîne dans leur coin (`Entites.gangChasse`), ni ne prend ou ne perd un coin la nuit (`Territoires.horsJeu`), ce
    # qu'ils avaient pris revient (`Territoires.liberer`), et leur cour redevient « La Pointe ».
    "donne": {"libere": "pointe", "manchette": "pointe_liberee", "message": "LA POINTE EST LIBRE"},

    # Zed attend devant le phare (`proteger`, le donneur n'est pas lui : c'est Josée — `cible` le pose, lui, qui se
    # tient déjà en ville) ; on le mène au Brouillard, par le pont — à pied ou en char. Au bar, les Skateux qui ne
    # veulent pas de la paix arrivent (`loin`), là où il est.
    "objectifs": [
        {"type": "proteger", "texte": "AMÈNE ZED AU BROUILLARD, SAIN ET SAUF",
         "cible": "zed", "lieu": "bar", "rayon": 5},

        {"type": "tuer", "texte": "LES SKATEUX QUI REFUSENT LA PAIX — COUCHE-LES",
         "groupe": "skateux", "n": 3, "ou": "bar", "loin": 10},
    ],

    # ⚠️ L'INTRO EST ÉCRITE (la recette de q11 : Josée est DEDANS) — elle montre le phare, où Zed attend.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "porte:phare", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Josée : elle ne rencontre pas un chef de gang, elle rencontre un gamin qui
    # rit trop. Elle le prend au sérieux quand même — c'est ça, sa politesse. Zed, au bar, ne rit plus du tout.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. Le chef des Skateux veut me parler. Amène-le-moi, entier.",
               jeu="[calm] Josée. [matter-of-fact] Le chef des Skateux veut me parler. [firmly] Amène-le-moi… entier.")
        ],
        "intro": [
            _l("josee", "Il attend devant le phare. Il a peur de traverser la ville tout seul, et il a raison.",
               jeu="[knowingly] Il attend devant le phare. [calm] Il a peur de traverser la ville tout seul… et il a raison."),
            _l("josee", "Ses gars ne veulent pas tous la paix. Ceux qui la refusent vont vous suivre.",
               jeu="[serious] Ses gars ne veulent pas tous la paix. [coldly] Ceux qui la refusent… vont vous suivre."),
            _l("josee", "Au Brouillard, je lui offre La Pointe. Sans guerre, sans nous.",
               jeu="[confident] Au Brouillard, je lui offre La Pointe. [quietly] Sans guerre… sans nous.")
        ],
        "pendant": [
            _p("zed", "Man, j'ai jamais passé le pont à pied. C'est grand, la ville.", 0,
               jeu="[nervously] Man, j'ai jamais passé le pont à pied. [quietly] C'est grand, la ville."),
            _p("zed", "C'est Ti-Kid pis sa bande. Ils veulent pas que je signe. Couche-les, man!", 1,
               jeu="[worried] C'est Ti-Kid pis sa bande. Ils veulent pas que je signe. [shouting] Couche-les, man!")
        ],
        "fin": [
            _l("josee", "Zed a signé. La Pointe est aux gens de La Pointe, astheure.",
               jeu="[satisfied] Zed a signé. [confident] La Pointe est aux gens de La Pointe, astheure."),
            _l("josee", "Il voulait te dire merci. Il a ri, à la place. C'est pareil, chez lui.",
               jeu="[amused] Il voulait te dire merci. Il a ri, à la place. [warmly] C'est pareil, chez lui.")
        ],
        "echec": [
            _l("josee", "Zed n'est pas arrivé. La Pointe va se battre encore longtemps.",
               jeu="[coldly] Zed n'est pas arrivé. [gravely] La Pointe va se battre encore longtemps.")
        ]
    }
}
