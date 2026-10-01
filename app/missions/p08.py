"""La mission p08 — voir app/missions/__init__.py pour le moteur.

Le party du stationnement (M16, arc P, 1er oct. 2026). La Pointe est libre, et les Skateux fêtent ça au
stationnement, devant le phare. Zed veut deux caisses de bière ; Lulu fait un prix pour la paix. Le camion de la
cantine (`monter`), les caisses au stationnement sans une bosse (`livrer`, `sans_degats`), la police qui arrive au
party (`semer`, une étoile), et retour au party (`retourner`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "p08",
    "titre": "Le party du stationnement",
    "donneur": "zed",
    "prerequis": ["la_pointe"],
    "recompense": 200,
    "donne": {"message": "LE PARTY DES SKATEUX"},

    "objectifs": [
        {"type": "monter", "texte": "LE CAMION DE LA CANTINE, DERRIÈRE", "vehicule": "camion", "ou": "ruelle:cantine:12"},

        {"type": "livrer", "texte": "DEUX CAISSES DE BIÈRE AU STATIONNEMENT DU PHARE",
         "lieu": "phare", "rayon": 6, "sans_degats": True},

        {"type": "semer", "texte": "LA POLICE ARRIVE AU PARTY — SÈME-LA", "etoiles": 1},

        {"type": "retourner", "texte": "REVIENS AU PARTY, ZED T'ATTEND"},
    ],

    # Intention (intro) : Zed qui rit, sur sa planche, et qui pour une fois demande quelque chose de simple ; la
    # caméra va voir le stationnement (la rampe, vide), puis revient pour la seule règle : pas une bouteille cassée.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "hausser", "duree": 60, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "rampe:pointe", "ferme": 20, "ouvre": 20, "tient": 140, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Zed : vite, en riant, « man » à chaque phrase ; une fête, enfin, et il a
    # peur que la police la gâche — il en rit.
    "dialogue": {
        "appel": [
            _l("zed", "Yo, c'est Zed. La Pointe est libre, man, pis on fête ça au stationnement!",
               jeu="[laughs] Yo, c'est Zed. [excited] La Pointe est libre, man, pis on fête ça au stationnement!")
        ],
        "intro": [
            _l("zed", "Il manque juste la bière, man. Lulu nous fait un prix, son camion est derrière la cantine.",
               jeu="[playfully] Il manque juste la bière, man. [cheerful] Lulu nous fait un prix, son camion est derrière la cantine."),
            _l("zed", "Le stationnement, ici, à côté du phare. La rampe, les haut-parleurs, toute la gang.",
               jeu="[excited] Le stationnement, ici, à côté du phare. [laughs] La rampe, les haut-parleurs, toute la gang."),
            _l("zed", "Une règle, man : pas une bouteille cassée. Pas une.",
               jeu="[mischievously] Une règle, man : [serious] pas une bouteille cassée. Pas une.")
        ],
        "pendant": [
            _p("zed", "Le camion de Lulu, derrière la cantine. Elle a dit de pas toucher au poisson.", 0,
               jeu="[playfully] Le camion de Lulu, derrière la cantine. [laughs] Elle a dit de pas toucher au poisson."),
            _p("zed", "Pas de trous, pas de bosses, man. Chaque bouteille compte.", 1,
               jeu="[nervously] Pas de trous, pas de bosses, man. [laughs] Chaque bouteille compte."),
            _p("zed", "Oh non, les bleus! Un voisin a appelé. Emmène-les ailleurs, man!", 2,
               jeu="[nervously] Oh non, les bleus! [laughs] Un voisin a appelé. Emmène-les ailleurs, man!"),
            _p("zed", "C'est beau, ils sont partis. Reviens, la musique part!", 3,
               jeu="[relieved] C'est beau, ils sont partis. [excited] Reviens, la musique part!")
        ],
        "fin": [
            _l("zed", "T'es le roi de la Pointe, man! Tiens, pis prends-en une, t'as soif.",
               jeu="[laughs] T'es le roi de la Pointe, man! [cheerful] Tiens, pis prends-en une, t'as soif."),
            _l("zed", "Pis si la police revient, toi, t'étais jamais là.",
               jeu="[mischievously] Pis si la police revient, toi… [laughs] t'étais jamais là.")
        ],
        "echec": [
            _l("zed", "Pas de bière, pas de party. La gang est déçue, man. Moi aussi, un peu.",
               jeu="[disappointed] Pas de bière, pas de party. [sighs] La gang est déçue, man. Moi aussi, un peu.")
        ]
    }
}
