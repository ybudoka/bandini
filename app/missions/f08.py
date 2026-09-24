"""La mission f08 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "f08",
    "titre": "Le char de Rocco",
    "donneur": "marco",
    "prerequis": ["f02", "f03"],
    "recompense": 300,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"message": "LA BERLINE DE LUXE, AU GARAGE"},

    # ⚠️ Même patron que f02 : un char dort à la fourrière (`porte:fourriere`),
    # `poserLeChar` le fait naître au bord de rue. `semer` (v1, prouvé m4/m5) fait
    # le reste — un lot gardé, ça réagit quand on en sort une berline sans papiers.
    #
    # « Des missions plus longues » (Martin, 22 sept. 2026) : la clé d'abord, chez Rosa —
    # l'ancienne blonde de Rocco l'a gardée (`parler`, sa poignée de main dite) ; et,
    # la police semée, un dernier tour par le phare de La Pointe, où Rocco allait le
    # dimanche — le bout est de la ville, le garage est au centre nord.
    "objectifs": [
        {"type": "parler", "texte": "VA CHERCHER LA CLÉ CHEZ ROSA",
         "cible": "rosa"},

        {"type": "aller", "texte": "VA À LA FOURRIÈRE, DE NUIT",
         "lieu": "fourriere", "rayon": 6, "nuit": True},

        {"type": "monter", "texte": "PRENDS LA BERLINE DE ROCCO",
         "vehicule": "luxe", "ou": "porte:fourriere"},

        {"type": "semer", "texte": "SÈME LA POLICE", "etoiles": 1},

        {"type": "aller", "texte": "UN DERNIER TOUR PAR LE PHARE",
         "lieu": "phare", "rayon": 6},

        {"type": "livrer", "texte": "LIVRE-LA AU GARAGE",
         "lieu": "garage", "rayon": 4},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Marco : la désinvolture de qui a peur et le
    # cache, comme f01/f09 ; il hausse les épaules sur la fourrière, puis se rengorge.
    "dialogue": {
        "appel": [
            _l("marco", "Cousin, c'est Marco. La belle berline de Rocco croupit à la fourrière. Ça me fend le cœur.",
               jeu="[casually] Cousin, c'est Marco. [somber] La belle berline de Rocco croupit à la fourrière. Ça me fend le cœur.")
        ],
        "intro": [
            _l("marco", "Ils l'ont saisie après sa mort, pis personne l'a réclamée. Va la chercher, de nuit.",
               jeu="[casually] Ils l'ont saisie après sa mort, pis personne l'a réclamée. [firmly] Va la chercher… de nuit."),
            _l("marco", "Le lot est gardé, mais tes vieux réflexes vont faire l'affaire. Ramène-la au garage, je la repeins.",
               jeu="[wryly] Le lot est gardé, mais tes vieux réflexes vont faire l'affaire. [confident] Ramène-la au garage… je la repeins."),
            _l("marco", "La clé, par exemple, c'est Rosa qui l'a. Sois poli, cousin, elle a connu Rocco mieux que nous.",
               jeu="[casually] La clé, par exemple, c'est Rosa qui l'a. [wryly] Sois poli, cousin, elle a connu Rocco mieux que nous.")
        ],
        "pendant": [
            _p("marco", "Ça klaxonne fort derrière toi! Perds-les avant le garage!", 3,
               jeu="[worried] Ça klaxonne fort derrière toi! [firmly] Perds-les avant le garage!"),
            _p("marco", "Fais-y faire un tour par le phare, cousin. Rocco y allait le dimanche, pour rien, juste pour y aller.", 4,
               jeu="[tenderly] Fais-y faire un tour par le phare, cousin. [somber] Rocco y allait le dimanche, pour rien… juste pour y aller.")
        ],
        # Rosa, à sa boutique : elle se nomme (la première fois qu'on l'entend dans cette
        # mission), et Rocco n'a jamais son nom sans une pointe d'ironie.
        "accueil": [
            _a("rosa", "C'est Rosa. La clé de Rocco? Je la gardais pour la lui lancer par la tête.", 0,
               jeu="[wryly] C'est Rosa. La clé de Rocco? [amused] Je la gardais pour la lui lancer par la tête.")
        ],
        "fin": [
            _l("marco", "Regarde-moi cette carrosserie. Rocco aurait pleuré de la voir chez nous, astheure.",
               jeu="[amused] Regarde-moi cette carrosserie. [tenderly] Rocco aurait pleuré de la voir chez nous, astheure."),
            _l("marco", "Elle dormira ici, en attendant qu'on lui trouve un habit neuf.",
               jeu="[satisfied] Elle dormira ici, en attendant qu'on lui trouve un habit neuf.")
        ],
        "echec": [
            _l("marco", "Perdu la berline de Rocco... Ah, cousin. Ça, ça me fait mal.",
               jeu="[disappointed] Perdu la berline de Rocco… [somber] Ah, cousin. Ça, ça me fait mal.")
        ]
    }
}
