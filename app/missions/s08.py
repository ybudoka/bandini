"""La mission s08 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "s08",
    "titre": "Le lot se fait vider",
    "donneur": "gilles",
    "prerequis": ["s01"],
    "recompense": 200,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"message": "GILLES VA DORMIR POUR VRAI"},

    # De nuit (`aller`, `nuit`, au rayon 6 : Gilles se tient à la guérite, à ~48 px du
    # point) ; les Boulonneux arrivent par la clôture (`tuer`, `loin`) ; le quatrième est
    # déjà reparti avec une auto, garée dans leur coin (`monter`, `zone:boulonneux`) ; on
    # la ramène au lot — chez Gilles, sa fin se dit sur place.
    "objectifs": [
        {"type": "aller", "texte": "ATTENDS LA NUIT À LA FOURRIÈRE",
         "lieu": "fourriere", "rayon": 6, "nuit": True},

        {"type": "tuer", "texte": "TROIS BOULONNEUX VIDENT LE LOT — COUCHE-LES",
         "groupe": "boulonneux", "n": 3, "ou": "donneur", "loin": 8},

        {"type": "monter", "texte": "UN QUATRIÈME EST PARTI AVEC UNE AUTO — REPRENDS-LA",
         "vehicule": "auto", "ou": "zone:boulonneux"},

        {"type": "livrer", "texte": "RAMÈNE-LA AU LOT",
         "lieu": "fourriere", "rayon": 4},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Gilles : las, lent, fier de son lot ; la nuit
    # l'inquiète plus qu'il ne le dit, et le soulagement vient avec la dernière case pleine.
    "dialogue": {
        "appel": [
            _l("gilles", "C'est Gilles, de la fourrière. Des chars disparaissent du lot la nuit, pis c'est pas ma remorqueuse.",
               jeu="[gravely] C'est Gilles, de la fourrière. [somber] Des chars disparaissent du lot la nuit… pis c'est pas ma remorqueuse.")
        ],
        "intro": [
            _l("gilles", "Trente ans que je garde ce lot-là. J'ai jamais perdu un char, pis j'commencerai pas à la fin.",
               jeu="[somber] Trente ans que je garde ce lot-là. [firmly] J'ai jamais perdu un char… pis j'commencerai pas à la fin."),
            _l("gilles", "Les Boulonneux passent par la clôture quand je cogne des clous. Attends-les avec moi, à soir.",
               jeu="[gravely] Les Boulonneux passent par la clôture quand je cogne des clous. [tenderly] Attends-les avec moi, à soir.")
        ],
        "pendant": [
            _p("gilles", "La nuit tombe. Moi, je fais semblant de dormir, j'suis bon là-dedans.", 0,
               jeu="[quietly] La nuit tombe. [amused] Moi, je fais semblant de dormir… j'suis bon là-dedans."),
            _p("gilles", "Les v'là, par la clôture! Fais-les repartir comme ils sont venus.", 1,
               jeu="[gravely] Les v'là, par la clôture! [firmly] Fais-les repartir… comme ils sont venus."),
            _p("gilles", "Le quatrième a pris une auto! Elle est à la ville, le jeune, pas à eux.", 2,
               jeu="[worried] Le quatrième a pris une auto! [firmly] Elle est à la ville, le jeune… pas à eux."),
            _p("gilles", "Ramène-la icitte. Je la veux dans sa case, pas dans leur cour.", 3,
               jeu="[gravely] Ramène-la icitte. [somber] Je la veux dans sa case… pas dans leur cour.")
        ],
        "fin": [
            _l("gilles", "Toutes dans leurs cases. Je vais dormir pour vrai, à soir.",
               jeu="[relieved] Toutes dans leurs cases. [tenderly] Je vais dormir pour vrai, à soir."),
            _l("gilles", "Encore un hiver, pis je rends les clés. Mais pas à des Boulonneux.",
               jeu="[somber] Encore un hiver, pis je rends les clés. [firmly] Mais pas à des Boulonneux.")
        ],
        "echec": [
            _l("gilles", "Le lot est plus vide que ma retraite. C'est pas une belle nuit.",
               jeu="[somber] Le lot est plus vide que ma retraite. [gravely] C'est pas une belle nuit.")
        ]
    }
}
