"""La mission t06 — voir app/missions/__init__.py pour le moteur.

La commande de la taverne (M16, arc T, les petites jobs — 1er oct. 2026). Le gérant d'une taverne, n'importe où en
ville : son livreur est malade, et les gars du quai attendent deux caisses de bière. Son camion, la cantine des Quais,
puis lui. Un passant qui donne une job (`passant`, de partout).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t06",
    "titre": "La commande de la taverne",
    "donneur": "passant",
    "prerequis": ["m6"],
    "recompense": 90,
    "passant": {"archetype": "passant", "district": None, "nom": "Le gérant de la taverne"},
    "donne": {"message": "LE QUAI A EU SA BIÈRE"},

    # Le camion dort dans la ruelle du bar (le patron de q09) ; la cantine est un lieu de mission (rien ne bouge) ; il
    # attend là où il t'a hélé — `retourner`.
    "objectifs": [
        {"type": "monter", "texte": "SON CAMION, DANS LA RUELLE DU BAR", "vehicule": "camion", "ou": "ruelle:bar:12",
         "prete": "passant"},
        {"type": "livrer", "texte": "DEUX CAISSES DE BIÈRE À LA CANTINE DES QUAIS", "lieu": "cantine", "rayon": 6},
        {"type": "retourner", "texte": "RAPPORTE SON CAMION AU GÉRANT — PIS LA FACTURE"},
    ],

    # Le jeu (`jeu=`) — le gérant : débordé, comptable jusqu'à la dernière bouteille, et une confiance aveugle en toi.
    "dialogue": {
        "hele": [
            _l("passant", "T'as ton permis?", jeu="[excited] T'as ton permis?")
        ],
        "intro": [
            _l("passant", "Mon livreur a la grippe, pis le quai attend deux caisses de bière depuis midi.",
               jeu="[nervously] Mon livreur a la grippe, [annoyed] pis le quai attend deux caisses de bière depuis midi."),
            _l("passant", "Le camion est dans la ruelle du bar. Brasse-les pas, la mousse se paie pas.",
               jeu="[matter-of-fact] Le camion est dans la ruelle du bar. [serious] Brasse-les pas, la mousse se paie pas.")
        ],
        "pendant": [
            _p("passant", "La cantine des Quais. Dis à Lulu que la facture suit, comme d'habitude.", 1,
               jeu="[calm] La cantine des Quais. [knowingly] Dis à Lulu que la facture suit, comme d'habitude."),
            _p("passant", "Livrées? Ramène-moi le camion, j'en ai juste un.", 2,
               jeu="[relieved] Livrées? [worried] Ramène-moi le camion, j'en ai juste un.")
        ],
        "fin": [
            _l("passant", "Pas une bouteille de cassée! Quatre-vingt-dix, pis une bière quand tu veux.",
               jeu="[happy] Pas une bouteille de cassée! [warmly] Quatre-vingt-dix, pis une bière quand tu veux.")
        ],
        "echec": [
            _l("passant", "Pas de bière au quai. Ils vont descendre la chercher eux-mêmes.",
               jeu="[disappointed] Pas de bière au quai. [worried] Ils vont descendre la chercher eux-mêmes.")
        ]
    }
}
