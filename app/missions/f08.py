"""La mission f08 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

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
    "objectifs": [
        {"type": "aller", "texte": "VA À LA FOURRIÈRE, DE NUIT",
         "lieu": "fourriere", "rayon": 6, "nuit": True},

        {"type": "monter", "texte": "PRENDS LA BERLINE DE ROCCO",
         "vehicule": "luxe", "ou": "porte:fourriere"},

        {"type": "semer", "texte": "SÈME LA POLICE", "etoiles": 1},

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
               jeu="[wryly] Le lot est gardé, mais tes vieux réflexes vont faire l'affaire. [confident] Ramène-la au garage… je la repeins.")
        ],
        "pendant": [
            _p("marco", "Ça klaxonne fort derrière toi! Perds-les avant le garage!", 2,
               jeu="[worried] Ça klaxonne fort derrière toi! [firmly] Perds-les avant le garage!")
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
