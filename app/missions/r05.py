"""La mission r05 — voir app/missions/__init__.py pour le moteur.

La salle des pièces (M16, arc R, 30 sept. 2026). Les armes saisies au Faubourg — celles des Cravates, et quelques-unes
à toi — partent cette nuit pour Québec dans le camion des pièces à conviction. Bouchard aimerait mieux qu'elles ne
témoignent jamais : on vole le camion dans la ruelle du poste, deux étoiles, on les sème, et on le mène au garage de
Rocco, où un camion peut disparaître.

⚠️ La fiche voulait « ramasser trois armes dans la salle des pièces, dedans » : un objectif ne se joue pas dans une
pièce (`majObjectif` dort dedans) — la salle des pièces part en camion.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "r05",
    "titre": "La salle des pièces",
    "donneur": "bouchard",
    "prerequis": ["r01"],
    "recompense": 250,
    "donne": {"message": "LES PIÈCES À CONVICTION N'ARRIVERONT JAMAIS À QUÉBEC"},

    "objectifs": [
        {"type": "aller", "texte": "À LA NUIT, AU POSTE : LE CAMION PART POUR QUÉBEC",
         "lieu": "poste", "rayon": 8, "nuit": True},

        {"type": "monter", "texte": "LE CAMION DES PIÈCES À CONVICTION : PRENDS-LE",
         "vehicule": "camion", "ou": "ruelle:poste:12"},

        {"type": "semer", "texte": "DEUX ÉTOILES : UN CAMION DE LA POLICE, ÇA SE CHERCHE", "etoiles": 2},

        {"type": "livrer", "texte": "LE CAMION AU GARAGE DE TON ONCLE", "lieu": "garage", "rayon": 5},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "ruelle:poste:12", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Bouchard : un service entre complices, dit en bourru ; la pointe
    # d'inquiétude qu'il cache mal quand il parle de Québec.
    "dialogue": {
        "appel": [
            _l("bouchard", "Bouchard. Les armes du Faubourg partent pour Québec cette nuit. Y en a des tiennes dedans.",
               jeu="[gruffly] Bouchard. Les armes du Faubourg partent pour Québec cette nuit. [knowingly] Y en a des tiennes dedans.")
        ],
        "intro": [
            _l("bouchard", "À Québec, ils font des tests. Pis les tests, ça raconte des histoires à des juges.",
               jeu="[nervously] À Québec, ils font des tests. [gruffly] Pis les tests, ça raconte des histoires à des juges."),
            _l("bouchard", "Le camion attend dans la ruelle du poste. Le chauffeur prend son café à onze heures.",
               jeu="[matter-of-fact] Le camion attend dans la ruelle du poste. [deadpan] Le chauffeur prend son café à onze heures."),
            _l("bouchard", "Amène-le au garage de ton oncle. Là, un camion peut disparaître.",
               jeu="[knowingly] Amène-le au garage de ton oncle. [gruffly] Là, un camion peut disparaître.")
        ],
        "pendant": [
            _p("bouchard", "La nuit, le jeune. Personne vole un camion en plein jour.", 0,
               jeu="[gruffly] La nuit, le jeune. [deadpan] Personne vole un camion en plein jour."),
            _p("bouchard", "Le camion gris, les portes arrière cadenassées. Le cadenas, c'est pas ton problème.", 1,
               jeu="[matter-of-fact] Le camion gris, les portes arrière cadenassées. [wryly] Le cadenas, c'est pas ton problème."),
            _p("bouchard", "Ça crie sur la radio. Perds-les avant le pont, après c'est la Sûreté.", 2,
               jeu="[nervously] Ça crie sur la radio. [firmly] Perds-les avant le pont, après c'est la Sûreté."),
            _p("bouchard", "Au garage, astheure. La baie est ouverte, personne regarde.", 3,
               jeu="[matter-of-fact] Au garage, astheure. [gruffly] La baie est ouverte, personne regarde.")
        ],
        "fin": [
            _l("bouchard", "Propre. Les pièces à conviction ont eu un accident de parcours.",
               jeu="[satisfied] Propre. [deadpan] Les pièces à conviction ont eu un accident de parcours."),
            _l("bouchard", "Tes vieilles affaires sont au garage. Le reste, on l'a jamais vu.",
               jeu="[knowingly] Tes vieilles affaires sont au garage. [gruffly] Le reste, on l'a jamais vu.")
        ],
        "echec": [
            _l("bouchard", "Le camion est parti pour Québec. On va prier, le jeune.",
               jeu="[nervously] Le camion est parti pour Québec. [gruffly] On va prier, le jeune.")
        ]
    }
}
