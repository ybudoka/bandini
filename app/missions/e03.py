"""La mission e03 — voir app/missions/__init__.py pour le moteur.

Biscuit s'est sauvé (M16, arc E, les Érables — 1er oct. 2026). Mme Thérèse Beaulieu, la promeneuse des Érables : son
vieux chien a vu un écureuil et a pris la clé des champs jusqu'aux bois de La Pointe, au pied du phare. On le voit,
mais il joue à la tag : à pied, on l'approche, il détale ; trois fois, puis il se couche, la langue sortie, et se laisse
prendre (`chercher` avec `bete` et `se_sauve`). Il nous suit, à pied ou en char, et on le ramène à sa maîtresse.

Ce qu'elle donne : 80 $, et Biscuit à ses pieds devant le dépanneur — qui te suit, à pied, dans les Érables
(`chien` de sa fiche, `static/js/biscuit.js`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "e03",
    "titre": "Biscuit s'est sauvé",
    "donneur": "beaulieu",
    "prerequis": ["m6"],
    "recompense": 80,
    "donne": {"message": "BISCUIT EST RENTRÉ — IL T'A ADOPTÉ"},

    # Le phare est un lieu de mission depuis m6 : Biscuit court dans les bois autour, à quatre à dix tuiles.
    "objectifs": [
        {"type": "chercher", "texte": "RATTRAPE BISCUIT, AU BOIS DU PHARE", "bete": "chien", "ou": "phare",
         "rayon": 10, "se_sauve": 3, "nom": "BISCUIT"},
        {"type": "retourner", "texte": "RAMÈNE BISCUIT À MME BEAULIEU"},
    ],

    # Le jeu (`jeu=`) — Mme Beaulieu : vouvoie tout le monde sauf son chien, qu'elle appelle « mon bébé » ; inquiète,
    # mais elle connaît son vlimeux par cœur. Elle se nomme une fois, au téléphone.
    "dialogue": {
        "appel": [
            _l("beaulieu", "Allô? C'est Thérèse Beaulieu, des Érables. Mon Biscuit s'est sauvé, pis j'ai pus les jambes pour courir après.",
               jeu="[worried] Allô? C'est Thérèse Beaulieu, des Érables. [sighs] Mon Biscuit s'est sauvé, pis j'ai pus les jambes pour courir après.")
        ],
        "intro": [
            _l("beaulieu", "Il a vu un écureuil, pis il a couru jusqu'aux bois de La Pointe. Treize ans, pis il se pense encore un chiot.",
               jeu="[worried] Il a vu un écureuil, pis il a couru jusqu'aux bois de La Pointe. [amused] Treize ans, pis il se pense encore un chiot."),
            _l("beaulieu", "Approchez-le à pied. Il va se sauver trois fois, le vlimeux, pis après il va se coucher.",
               jeu="[knowingly] Approchez-le à pied. Il va se sauver trois fois, le vlimeux, [softly] pis après il va se coucher.")
        ],
        "pendant": [
            _p("beaulieu", "Il vous voit? Courez pas après, il pense que c'est un jeu.", 0,
               jeu="[nervously] Il vous voit? [softly] Courez pas après, il pense que c'est un jeu."),
            _p("beaulieu", "Vous l'avez! Ramenez-moi mon bébé, il connaît le chemin du biscuit.", 1,
               jeu="[relieved] Vous l'avez! [warmly] Ramenez-moi mon bébé, il connaît le chemin du biscuit.")
        ],
        "fin": [
            _l("beaulieu", "Biscuit, mon beau grand fou! Tenez, quatre-vingts piastres, pis regardez-le : il vous lâchera pus.",
               jeu="[happy] Biscuit, mon beau grand fou! [warmly] Tenez, quatre-vingts piastres, [amused] pis regardez-le : il vous lâchera pus.")
        ],
        "echec": [
            _l("beaulieu", "Laissez faire. Je vais mettre des affiches sur tous les poteaux de La Pointe.",
               jeu="[disappointed] Laissez faire. [sighs] Je vais mettre des affiches sur tous les poteaux de La Pointe.")
        ]
    }
}
