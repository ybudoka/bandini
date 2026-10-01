"""La mission t04 — voir app/missions/__init__.py pour le moteur.

Mon BMX (M16, arc T, les petites jobs — 1er oct. 2026). Un ado de La Pointe : un Skateux lui a pris son BMX, en plein
hiver, « juste pour l'avoir ». Le reprendre au Skateux (`tuer`, un qui arrive), le lui rendre. Un passant qui donne
une job (`passant`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t04",
    "titre": "Mon BMX",
    "donneur": "passant",
    "prerequis": ["m6"],
    "recompense": 25,
    "passant": {"archetype": "ado", "district": "pointe", "nom": "Le jeune de La Pointe"},
    "donne": {"message": "LE BMX EST RENTRÉ AU GARAGE DE SA MÈRE"},

    "objectifs": [
        {"type": "tuer", "texte": "UN SKATEUX A SON BMX : VA LE CHERCHER", "groupe": "skateux", "n": 1, "loin": 9},
        {"type": "retourner", "texte": "RENDS SON BMX AU JEUNE"},
    ],

    # Le jeu (`jeu=`) — l'ado : outré, la voix qui casse, et une logique d'adolescent imparable.
    "dialogue": {
        "hele": [
            _l("passant", "Heille! Toi, là!", jeu="[excited] Heille! Toi, là!")
        ],
        "intro": [
            _l("passant", "Un Skateux m'a pris mon BMX. En janvier! Il peut même pas en faire!",
               jeu="[angry] Un Skateux m'a pris mon BMX. [shouting] En janvier! Il peut même pas en faire!"),
            _l("passant", "Il le promène pour le fun, il va repasser. T'as l'air de quelqu'un qui fesse.",
               jeu="[annoyed] Il le promène pour le fun, il va repasser. [curious] T'as l'air de quelqu'un qui fesse.")
        ],
        "pendant": [
            _p("passant", "C'est lui! Celui avec ma bécique pis la tuque de sa grand-mère!", 0,
               jeu="[excited] C'est lui! [shouting] Celui avec ma bécique pis la tuque de sa grand-mère!"),
            _p("passant", "Malade! Ramène-le avant que ma mère s'en rende compte.", 1,
               jeu="[happy] Malade! [nervously] Ramène-le avant que ma mère s'en rende compte.")
        ],
        "fin": [
            _l("passant", "Mon BMX! Vingt-cinq piasses, c'est mes économies de l'année. Garde pas tout.",
               jeu="[happy] Mon BMX! [playfully] Vingt-cinq piasses, c'est mes économies de l'année. Garde pas tout.")
        ],
        "echec": [
            _l("passant", "Laisse faire. Je vais dire à ma mère que je l'ai vendu.",
               jeu="[disappointed] Laisse faire. [sighs] Je vais dire à ma mère que je l'ai vendu.")
        ]
    }
}
