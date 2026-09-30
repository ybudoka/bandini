"""La mission s14 — voir app/missions/__init__.py pour le moteur.

La casse à Ti-Loup (M16, arc S, 30 sept. 2026). Ti-Loup a un acheteur en Beauce pour trois autos-patrouilles en
cubes — « le métal de la police, c'est du bon métal ». Trois dans la même nuit, devant le poste : chacune coûte une
étoile, et il faut la semer avant de la mener au compacteur du lot. La plus longue nuit de La Shop.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "s14",
    "titre": "La casse à Ti-Loup",
    "donneur": "tiloup",
    "prerequis": ["s02", "s05"],
    "recompense": 450,
    "donne": {"message": "TROIS AUTOS-PATROUILLES EN CUBES, POUR LA BEAUCE"},

    # ⚠️ Trois fois le même trio (`monter`, `semer`, `livrer`) : chaque `monter` pose SON char devant le poste. Ti-Loup
    # se tient dans la cour du lot (`dans_la_cour`) : la fin se dit devant lui, là où l'on livre la troisième.
    "objectifs": [
        {"type": "aller", "texte": "À LA NUIT, AU POSTE : TROIS AUTOS DORMENT DEVANT",
         "lieu": "poste", "rayon": 8, "nuit": True},

        {"type": "monter", "texte": "LA PREMIÈRE AUTO-PATROUILLE : PRENDS-LA",
         "vehicule": "police", "ou": "porte:poste"},
        {"type": "semer", "texte": "UNE ÉTOILE : SÈME-LA AVANT LE LOT", "etoiles": 1},
        {"type": "livrer", "texte": "AU COMPACTEUR DE TI-LOUP, AU LOT", "lieu": "fourriere", "rayon": 6},

        {"type": "monter", "texte": "LA DEUXIÈME, DEVANT LE POSTE", "vehicule": "police", "ou": "porte:poste"},
        {"type": "semer", "texte": "ILS T'ONT VU : SÈME-LES ENCORE", "etoiles": 1},
        {"type": "livrer", "texte": "AU COMPACTEUR, ET DE DEUX", "lieu": "fourriere", "rayon": 6},

        {"type": "monter", "texte": "LA TROISIÈME : LA DERNIÈRE AVANT LE MATIN", "vehicule": "police", "ou": "porte:poste"},
        {"type": "semer", "texte": "UNE DERNIÈRE ÉTOILE : SÈME-LA", "etoiles": 1},
        {"type": "livrer", "texte": "AU COMPACTEUR : LA BEAUCE ATTEND", "lieu": "fourriere", "rayon": 6},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:poste", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Ti-Loup : des chiffres, « comptant », un plaisir d'artisan pour le bon
    # métal ; il compte les cubes comme d'autres comptent les moutons.
    "dialogue": {
        "appel": [
            _l("tiloup", "Ti-Loup, la ferraille. J'ai un acheteur en Beauce pour trois autos-patrouilles. En cubes.",
               jeu="[gruffly] Ti-Loup, la ferraille. J'ai un acheteur en Beauce pour trois autos-patrouilles. [deadpan] En cubes.")
        ],
        "intro": [
            _l("tiloup", "Le métal de la police, c'est du bon métal. Épais, pas de rouille, pis personne en vend.",
               jeu="[wryly] Le métal de la police, c'est du bon métal. [matter-of-fact] Épais, pas de rouille, pis personne en vend."),
            _l("tiloup", "Trois, devant le poste, la même nuit. Chaque fois, ils vont t'avoir à l'œil.",
               jeu="[matter-of-fact] Trois, devant le poste, la même nuit. [deadpan] Chaque fois, ils vont t'avoir à l'œil."),
            _l("tiloup", "Sème-les avant d'entrer au lot. Un char suivi, je le compacte pas, c'est une règle.",
               jeu="[gruffly] Sème-les avant d'entrer au lot. [firmly] Un char suivi, je le compacte pas, c'est une règle.")
        ],
        "pendant": [
            _p("tiloup", "La nuit, les agents dorment dans le poste. Les chars, eux, dorment dehors.", 0,
               jeu="[deadpan] La nuit, les agents dorment dans le poste. [wryly] Les chars, eux, dorment dehors."),
            _p("tiloup", "Un. Le compacteur chante. Retourne en chercher une autre.", 3,
               jeu="[satisfied] Un. Le compacteur chante. [gruffly] Retourne en chercher une autre."),
            _p("tiloup", "Deux. La Beauce va être contente. Une dernière.", 6,
               jeu="[satisfied] Deux. La Beauce va être contente. [matter-of-fact] Une dernière."),
            _p("tiloup", "La dernière. Si tu la ramènes entière, je t'offre un café.", 9,
               jeu="[wryly] La dernière. [gruffly] Si tu la ramènes entière, je t'offre un café.")
        ],
        "fin": [
            _l("tiloup", "Trois cubes bleus et blancs. Les plus beaux de ma carrière.",
               jeu="[satisfied] Trois cubes bleus et blancs. [wryly] Les plus beaux de ma carrière."),
            _l("tiloup", "Comptant, comme d'habitude. Pis le café, c'est vrai, passe quand tu veux.",
               jeu="[gruffly] Comptant, comme d'habitude. [matter-of-fact] Pis le café, c'est vrai, passe quand tu veux.")
        ],
        "echec": [
            _l("tiloup", "Pas de cubes, pas de Beauce. Je retourne à mes carcasses.",
               jeu="[deadpan] Pas de cubes, pas de Beauce. [gruffly] Je retourne à mes carcasses.")
        ]
    }
}
