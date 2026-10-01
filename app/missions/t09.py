"""La mission t09 — voir app/missions/__init__.py pour le moteur.

La tournée du Clairon (M16, arc T, les petites jobs — 1er oct. 2026). Le p'tit camelot du Faubourg s'est foulé la
cheville sur la glace : six journaux à six portes avant que les clients appellent le journal. Une tournée (`course`,
dans l'ordre, sous le chrono), puis revenir lui dire. Un passant qui donne une job (`passant`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t09",
    "titre": "La tournée du Clairon",
    "donneur": "passant",
    "prerequis": ["m6"],
    "recompense": 60,
    "passant": {"archetype": "ado", "district": "faubourg", "nom": "Le p'tit camelot"},
    "donne": {"message": "LE CLAIRON EST LIVRÉ — LES CLIENTS N'ONT RIEN VU"},

    # Six portes déjà lieux de mission (aucune ne bouge) : la tournée d'un camelot, dans l'ordre de son cahier.
    "objectifs": [
        {"type": "course", "texte": "SIX CLAIRONS À SIX PORTES : DEUX MINUTES ET DEMIE",
         "points": ["terminus", "armurerie", "vetements", "bar", "casse_croute", "garage"], "rayon": 4, "chrono_s": 150},
        {"type": "retourner", "texte": "DIS AU P'TIT CAMELOT QUE C'EST LIVRÉ"},
    ],

    # Le jeu (`jeu=`) — le p'tit camelot : une cheville foulée, et un sens des affaires de vieux routier.
    "dialogue": {
        "hele": [
            _l("passant", "Monsieur! Svp!", jeu="[worried] Monsieur! Svp!")
        ],
        "intro": [
            _l("passant", "Je me suis foulé la cheville sur la glace. Pis mes six clients attendent leur Clairon.",
               jeu="[nervously] Je me suis foulé la cheville sur la glace. [worried] Pis mes six clients attendent leur Clairon."),
            _l("passant", "Le terminus, Gus, Rosa, le bar, le casse-croûte, le garage. Dans l'ordre, sinon ça chiale.",
               jeu="[matter-of-fact] Le terminus, Gus, Rosa, le bar, le casse-croûte, le garage. [serious] Dans l'ordre, sinon ça chiale.")
        ],
        "pendant": [
            _p("passant", "Lance-le pas dans la neige, là. Sur le perron, pliée en trois.", 0,
               jeu="[firmly] Lance-le pas dans la neige, là. [matter-of-fact] Sur le perron, pliée en trois."),
            _p("passant", "Déjà? Ben voyons, t'as des patins dans tes bottes?", 1,
               jeu="[surprised] Déjà? [playfully] Ben voyons, t'as des patins dans tes bottes?")
        ],
        "fin": [
            _l("passant", "Pas une plainte au journal! Tiens, soixante piasses. Mon patron saura rien.",
               jeu="[relieved] Pas une plainte au journal! [knowingly] Tiens, soixante piasses. Mon patron saura rien.")
        ],
        "echec": [
            _l("passant", "Trop tard, le bar a déjà appelé le journal. Je suis cuit.",
               jeu="[disappointed] Trop tard, le bar a déjà appelé le journal. [sighs] Je suis cuit.")
        ]
    }
}
