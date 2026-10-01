"""La mission e09 — voir app/missions/__init__.py pour le moteur.

Le barbecue de janvier (M16, arc E, 1er oct. 2026). Tous les hivers, Ti-Paul fait un barbecue dans son stationnement
pour les gars de la rue — en janvier, parce que « l'été, tout le monde en fait ». Les poutines du dépanneur doivent
arriver chaudes à trois commerces des Érables (la quincaillerie, le lave-auto, Prestige Autos), sous le chrono
(`course`, `chrono_s`), dans le camion de Ti-Paul (`monter`) ; puis le barbecue (`retourner`).

⚠️ Écarts à la fiche (« Le barbecue », en vélo) : le vélo est remisé l'hiver et une partie commence en janvier — le
camion de Ti-Paul ; trois arrêts aux enseignes de la rue (une porte neuve ferait glisser la ville), à huit tuiles (les
enseignes sont loin de la chaussée).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "e09",
    "titre": "Le barbecue de janvier",
    "donneur": "tipaul",
    "prerequis": ["e02"],
    "recompense": 150,
    "donne": {"message": "LE BARBECUE DE TI-PAUL"},

    "objectifs": [
        {"type": "monter", "texte": "LE CAMION DE TI-PAUL, DERRIÈRE LE DÉPANNEUR", "vehicule": "camion",
         "ou": "ruelle:depanneur:12", "prete": "tipaul"},

        {"type": "course", "texte": "TROIS POUTINES CHAUDES : QUINCAILLERIE, LAVE-AUTO, PRESTIGE",
         "points": ["boutique:quincaillerie", "boutique:lave-auto", "boutique:prestige"], "rayon": 8, "chrono_s": 120},

        {"type": "retourner", "texte": "REVIENS AU DÉPANNEUR, LE BARBECUE COMMENCE"},
    ],

    # Intention (intro) : Ti-Paul, fier de sa tradition absurde ; la caméra va voir la rue des commerces sous la neige,
    # et revient pour la seule chose sérieuse — une poutine froide, c'est une insulte.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "hausser", "duree": 60, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "boutique:quincaillerie", "ferme": 20, "ouvre": 20, "tient": 140, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Ti-Paul : jovial, bavard, il parle de son parking comme d'un pays.
    "dialogue": {
        "appel": [
            _l("tipaul", "C'est Ti-Paul, du dépanneur! C'est le barbecue de janvier, pis j'ai besoin d'un chauffeur!",
               jeu="[excited] C'est Ti-Paul, du dépanneur! [cheerful] C'est le barbecue de janvier, pis j'ai besoin d'un chauffeur!")
        ],
        "intro": [
            _l("tipaul", "Un barbecue en janvier, l'ami. L'été, tout le monde en fait, ça a pas de mérite.",
               jeu="[cheerful] Un barbecue en janvier, l'ami. [playfully] L'été, tout le monde en fait, ça a pas de mérite."),
            _l("tipaul", "Les gars de la quincaillerie, du lave-auto pis de Prestige veulent leurs poutines.",
               jeu="[matter-of-fact] Les gars de la quincaillerie, du lave-auto pis de Prestige veulent leurs poutines."),
            _l("tipaul", "Deux minutes, pas plus. Une poutine froide, dans les Érables, c'est une déclaration de guerre.",
               jeu="[firmly] Deux minutes, pas plus. [laughs] Une poutine froide, dans les Érables, c'est une déclaration de guerre.")
        ],
        "pendant": [
            _p("tipaul", "Le camion est derrière. Les poutines sont sur le siège, sous la couverte.", 0,
               jeu="[cheerful] Le camion est derrière. [matter-of-fact] Les poutines sont sur le siège, sous la couverte."),
            _p("tipaul", "Envoye, envoye! Le fromage fait encore squick-squick, profites-en!", 1,
               jeu="[excited] Envoye, envoye! [laughs] Le fromage fait encore squick-squick, profites-en!"),
            _p("tipaul", "Tout le monde a mangé chaud? Viens-t'en, les saucisses brûlent!", 2,
               jeu="[cheerful] Tout le monde a mangé chaud? [excited] Viens-t'en, les saucisses brûlent!")
        ],
        "fin": [
            _l("tipaul", "Trois livraisons, trois poutines chaudes! T'es plus rapide que mon ancien livreur.",
               jeu="[excited] Trois livraisons, trois poutines chaudes! [playfully] T'es plus rapide que mon ancien livreur."),
            _l("tipaul", "Tiens, ta paye, pis une saucisse. Elle est un peu brûlée, c'est la tradition.",
               jeu="[cheerful] Tiens, ta paye, pis une saucisse. [laughs] Elle est un peu brûlée, c'est la tradition.")
        ],
        "echec": [
            _l("tipaul", "Elles sont arrivées froides. Les gars de Prestige m'appellent pus, astheure.",
               jeu="[disappointed] Elles sont arrivées froides. [sighs] Les gars de Prestige m'appellent pus, astheure.")
        ]
    }
}
