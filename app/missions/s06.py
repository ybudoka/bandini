"""La mission s06 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "s06",
    "titre": "Le rat de l'usine",
    "donneur": "raymonde",
    "prerequis": ["s03"],
    "recompense": 250,
    "donne": {"message": "BOB SAUVÉ VEND LE SYNDICAT À PRÉVOST"},

    # Quelqu'un a vendu la liste du syndicat. Raymonde soupçonne Bob Sauvé, le contremaître : son char sort de
    # l'usine, on le file (`suivre`, le patron de f06) jusqu'au Brouillard — où Prévost l'attend. Puis on revient.
    "objectifs": [
        {"type": "suivre", "texte": "FILE LE CHAR DE BOB SAUVÉ, SANS QU'IL TE VOIE",
         "vehicule": "auto", "loin": 12, "proche": 3, "lieu": "bar"},

        {"type": "retourner", "texte": "RACONTE TOUT À RAYMONDE, À L'USINE"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Raymonde : elle sait déjà, elle veut en être sûre. Ferme, sèche ; le
    # `[bitterly]` est pour Sauvé, pas pour Prévost — un patron, on s'y attend ; un contremaître, c'est des nôtres.
    "dialogue": {
        "appel": [
            _l("raymonde", "Raymonde, du syndicat. Prévost connaît le nom de chacun de mes gars. Quelqu'un lui a vendu la liste.",
               jeu="[firmly] Raymonde, du syndicat. [serious] Prévost connaît le nom de chacun de mes gars. [bitterly] Quelqu'un lui a vendu la liste.")
        ],
        "intro": [
            _l("raymonde", "Bob Sauvé. Contremaître le jour, syndiqué le soir. Il joue sur deux tableaux.",
               jeu="[matter-of-fact] Bob Sauvé. [wryly] Contremaître le jour, syndiqué le soir. [bitterly] Il joue sur deux tableaux."),
            _l("raymonde", "Son char va sortir. Suis-le. Je veux savoir qui il voit, pas ce qu'il dit.",
               jeu="[firmly] Son char va sortir. Suis-le. [serious] Je veux savoir qui il voit… pas ce qu'il dit.")
        ],
        "pendant": [
            _p("raymonde", "Il part. Reste loin, Bob regarde toujours derrière lui, il a de quoi.", 0,
               jeu="[quietly] Il part. [firmly] Reste loin… [wryly] Bob regarde toujours derrière lui, il a de quoi."),
            _p("raymonde", "Le Brouillard. Pis Prévost à la table du fond, je gage. Reviens me voir.", 1,
               jeu="[bitterly] Le Brouillard. Pis Prévost à la table du fond, je gage. [firmly] Reviens me voir.")
        ],
        "fin": [
            _l("raymonde", "Sauvé pis Prévost, au même bar, le même soir. Ça me suffit.",
               jeu="[coldly] Sauvé pis Prévost, au même bar, le même soir. [firmly] Ça me suffit."),
            _l("raymonde", "Mes gars vont l'apprendre de ma bouche. Pas du Clairon.",
               jeu="[serious] Mes gars vont l'apprendre de ma bouche. [warmly] Pas du Clairon.")
        ],
        "echec": [
            _l("raymonde", "Il t'a vu. Bob va être propre comme un sou neuf, astheure.",
               jeu="[bitterly] Il t'a vu. [wryly] Bob va être propre comme un sou neuf, astheure.")
        ]
    }
}
