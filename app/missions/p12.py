"""La mission p12 — voir app/missions/__init__.py pour le moteur.

Le radeau de Zed (M16, arc P, 1er oct. 2026). Les Skateux ont vu l'île par-dessus la baie, et Zed veut « une flotte ».
Lulu vend la vieille chaloupe derrière la cantine ; on la prend (`monter`), on la mène au quai de La Pointe sans la
couler (`livrer` à un `amarrage:` — couler, c'est `vehicule_detruit`), et on va dire à Zed que sa flotte est arrivée
(`retourner`).

⚠️ Écart à la fiche : le « quai de La Pointe » est l'amarrage le plus proche du phare (`amarrage:phare`), au nord du
district — aucune porte neuve, la ville ne bouge pas.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "p12",
    "titre": "La flotte de Zed",
    "donneur": "zed",
    "prerequis": ["p08", "i01"],
    "recompense": 150,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"message": "LA FLOTTE DES SKATEUX"},

    "objectifs": [
        {"type": "monter", "texte": "LA VIEILLE CHALOUPE DE LULU, DERRIÈRE LA CANTINE",
         "vehicule": "bateau", "ou": "amarrage:cantine"},

        {"type": "livrer", "texte": "AMÈNE-LA AU QUAI DE LA POINTE — SANS LA COULER", "lieu": "amarrage:phare", "rayon": 4},

        {"type": "retourner", "texte": "DIS À ZED QUE SA FLOTTE EST ARRIVÉE"},
    ],

    # Intention (intro) : Zed qui regarde l'île en riant, persuadé qu'une chaloupe fait une flotte ; la caméra va voir
    # la chaloupe de Lulu, puis revient pour ce qu'il ne dit pas : il n'a jamais mis les pieds dans un bateau.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "amarrage:cantine", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "amarrage:cantine", "ferme": 20, "ouvre": 20, "tient": 140, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Zed : il rit de ce qui lui fait peur, et l'eau lui fait peur.
    "dialogue": {
        "appel": [
            _l("zed", "Yo, c'est Zed. T'as vu l'île, man? Les Skateux veulent une flotte.",
               jeu="[excited] Yo, c'est Zed. [playfully] T'as vu l'île, man? Les Skateux veulent une flotte.")
        ],
        "intro": [
            _l("zed", "Une flotte, man. Pour aller rider sur l'île, là où la police va jamais.",
               jeu="[laughs] Une flotte, man. [mischievously] Pour aller rider sur l'île, là où la police va jamais."),
            _l("zed", "Lulu vend sa vieille chaloupe, derrière la cantine. Elle flotte, qu'elle dit.",
               jeu="[playfully] Lulu vend sa vieille chaloupe, derrière la cantine. [laughs] Elle flotte, qu'elle dit."),
            _l("zed", "Amène-la au quai de la Pointe. Moi, je nage pas. Je l'ai jamais dit à personne, man.",
               jeu="[nervously] Amène-la au quai de la Pointe. [quietly] Moi, je nage pas. Je l'ai jamais dit à personne, man.")
        ],
        "pendant": [
            _p("zed", "Lulu dit qu'il faut écoper un peu. Un peu, man, pas beaucoup.", 0,
               jeu="[playfully] Lulu dit qu'il faut écoper un peu. [nervously] Un peu, man, pas beaucoup."),
            _p("zed", "Le quai de la Pointe, au nord du phare. Fais le tour par la baie, pas de roches.", 1,
               jeu="[matter-of-fact] Le quai de la Pointe, au nord du phare. [nervously] Fais le tour par la baie, pas de roches."),
            _p("zed", "Elle flotte encore? Viens me le dire en personne, man, je veux voir ta face.", 2,
               jeu="[excited] Elle flotte encore? [laughs] Viens me le dire en personne, man, je veux voir ta face.")
        ],
        "fin": [
            _l("zed", "Une flotte! Bon, un bateau. Mais une flotte, man, ça commence de même.",
               jeu="[excited] Une flotte! [laughs] Bon, un bateau. [playfully] Mais une flotte, man, ça commence de même."),
            _l("zed", "La gang va apprendre à ramer. Moi, je vais apprendre à nager. Un jour.",
               jeu="[cheerful] La gang va apprendre à ramer. [nervously] Moi, je vais apprendre à nager. [laughs] Un jour.")
        ],
        "echec": [
            _l("zed", "Elle a coulé? Ouin, c'est un signe, man. Les Skateux restent sur l'asphalte.",
               jeu="[disappointed] Elle a coulé? Ouin, [laughs] c'est un signe, man. Les Skateux restent sur l'asphalte.")
        ]
    }
}
