"""La mission s11 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "s11",
    "titre": "La paix des Boulonneux",
    "donneur": "prevost",
    "prerequis": ["s09", "s10"],
    "recompense": 500,
    "echec": ["mort", "arrete", "arme"],
    # ⚠️ LA QUATRIÈME LIBÉRATION DE CES VAGUES (`libere: shop`) : les Boulonneux redeviennent des machinistes — plus
    # un ne traîne dans leur coin (`Entites.gangChasse`), ni ne prend ou ne perd un coin la nuit
    # (`Territoires.horsJeu`), ce qu'ils avaient pris revient (`Territoires.liberer`), leur cour redevient
    # « La Shop ». Et le Clairon titre : la Prévost rembauche.
    "donne": {"libere": "shop", "manchette": "prevost_rembauche", "message": "LA SHOP EST LIBRE"},

    # Prévost plie : l'accord signé, on le porte à Gros-Boulon, devant la fourrière — à travers le coin des
    # Boulonneux, les mains vides (`sans_arme` : une arme au poing chez eux, et ils croient à un piège).
    "objectifs": [
        {"type": "parler", "texte": "PORTE L'ACCORD À GROS-BOULON — SANS ARME",
         "cible": "boulon", "sans_arme": True},
    ],

    # ⚠️ L'INTRO EST ÉCRITE (la recette de q11 : Prévost est DEDANS, et sous la coupe du défaut sa première
    # réplique était coupée par la seconde) — elle montre la fourrière, où Gros-Boulon attend.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "porte:fourriere", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Prévost : le patron qui perd, et qui fait comme s'il avait décidé de
    # perdre. Il vouvoie, il dit « mon usine », il ne prononce jamais le mot « syndicat ». Gros-Boulon, à la poignée
    # de main, ne dit presque rien : il lit.
    "dialogue": {
        "appel": [
            _l("prevost", "Réjean Prévost. J'ai une proposition pour vos amis de la fourrière. Passez à mon bureau.",
               jeu="[coldly] Réjean Prévost. [matter-of-fact] J'ai une proposition pour vos amis de la fourrière. [calm] Passez à mon bureau.")
        ],
        "intro": [
            _l("prevost", "Mon camion a sauté, le maire m'appelle en pantoufles. Je sais compter.",
               jeu="[bitterly] Mon camion a sauté, le maire m'appelle en pantoufles. [coldly] Je sais compter."),
            _l("prevost", "Cent cinquante postes, au salaire d'avant. Signé. Portez-le à Gros-Boulon.",
               jeu="[matter-of-fact] Cent cinquante postes, au salaire d'avant. Signé. [firmly] Portez-le à Gros-Boulon."),
            _l("prevost", "Sans arme. Ces gens-là prennent tout pour une insulte.",
               jeu="[wryly] Sans arme. [coldly] Ces gens-là prennent tout pour une insulte.")
        ],
        "accueil": [
            _a("boulon", "Cent cinquante postes. Au salaire d'avant. C'est sa signature, ça?", 0,
               jeu="[quietly] Cent cinquante postes. Au salaire d'avant. [surprised] C'est sa signature, ça?")
        ],
        "pendant": [
            _p("prevost", "Traversez leur coin les mains vides. Je ne paierai pas deux fois pour la même paix.", 0,
               jeu="[coldly] Traversez leur coin les mains vides. [matter-of-fact] Je ne paierai pas deux fois pour la même paix.")
        ],
        "fin": [
            _l("prevost", "Lundi, l'usine rouvre ses trois quarts. Mon usine, je précise.",
               jeu="[matter-of-fact] Lundi, l'usine rouvre ses trois quarts. [smugly] Mon usine, je précise."),
            _l("prevost", "Vous avez coûté cher. Mais moins cher qu'une grève. Bonne journée.",
               jeu="[coldly] Vous avez coûté cher. [wryly] Mais moins cher qu'une grève. [calm] Bonne journée.")
        ],
        "echec": [
            _l("prevost", "Une arme dans leur coin. Ils croient à un piège, et moi, je garde mon argent.",
               jeu="[coldly] Une arme dans leur coin. [smugly] Ils croient à un piège… et moi, je garde mon argent.")
        ]
    }
}
