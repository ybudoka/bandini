"""La mission t03 — voir app/missions/__init__.py pour le moteur.

Un lift au terminus (M16, arc T, les petites jobs — 1er oct. 2026). Une dame du Faubourg, sa valise, son autobus de
Rimouski qui part dans une minute et demie. Elle te suit à pied ou monte dans ton char (`proteger`), et elle commente
la conduite. Un passant qui donne une job (`passant`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t03",
    "titre": "Un lift au terminus",
    "donneur": "passante",
    "prerequis": ["m6"],
    "recompense": 40,
    "passant": {"archetype": "dame", "district": "faubourg", "nom": "La dame à la valise"},
    "donne": {"message": "ELLE A EU SON AUTOBUS"},

    # ⚠️ `proteger` : elle est déjà là (le passant qui hèle), elle te suit ou monte ; le terminus est un lieu de mission
    # (Ti-Guy, Sal). La fin se dit devant elle, au terminus : elle est avec toi.
    "objectifs": [
        {"type": "proteger", "texte": "AMÈNE LA DAME AU TERMINUS — SON AUTOBUS PART", "cible": "passante",
         "lieu": "terminus", "rayon": 5, "chrono_s": 90},
    ],

    # Le jeu (`jeu=`) — la dame : polie, pressée, et une opinion sur chaque coin de rue.
    "dialogue": {
        "hele": [
            _l("passante", "Ouhou! Monsieur!", jeu="[worried] Ouhou! Monsieur!")
        ],
        "intro": [
            _l("passante", "Mon autobus pour Rimouski part dans une minute et demie, pis mes jambes, elles, partent pas.",
               jeu="[nervously] Mon autobus pour Rimouski part dans une minute et demie, [sighs] pis mes jambes, elles, partent pas."),
            _l("passante", "Amène-moi au terminus, veux-tu? Je te paierai, je suis pas une quêteuse.",
               jeu="[softly] Amène-moi au terminus, veux-tu? [firmly] Je te paierai, je suis pas une quêteuse.")
        ],
        "pendant": [
            _p("passante", "Pas trop vite, là! J'ai des œufs dans ma valise.", 0,
               jeu="[worried] Pas trop vite, là! [nervously] J'ai des œufs dans ma valise.")
        ],
        "fin": [
            _l("passante", "Juste à temps! T'es ben fin. Tiens, quarante piasses, pis lave ton char.",
               jeu="[relieved] Juste à temps! T'es ben fin. [teasing] Tiens, quarante piasses, pis lave ton char.")
        ],
        "echec": [
            _l("passante", "Il est parti sans moi. Bon. Je vais aller voir ma sœur une autre fois.",
               jeu="[disappointed] Il est parti sans moi. [sighs] Bon. Je vais aller voir ma sœur une autre fois.")
        ]
    }
}
