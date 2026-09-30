"""La mission l03 — voir app/missions/__init__.py pour le moteur.

La source (M16, arc C, 30 sept. 2026 — la « c03 » de la fiche). La source de Louise, c'est Norbert : le concierge
de l'Hôtel Bandini voit passer toute la ville à sa réception, et il vend ce qu'il voit — poliment. Ce soir, il a
quelque chose sur le maire, et il ne veut pas le dire au téléphone. De nuit, on le prend à l'hôtel, on le mène au
kiosque ; deux hommes le suivaient déjà. La fiche disait « un commis du poste » : c'est Norbert, un personnage qui
existe, et qui se tient DEDANS (`point:norbert`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "l03",
    "titre": "La source",
    "donneur": "louise",
    "prerequis": ["l01", "f10"],
    "recompense": 300,
    "donne": {"message": "LOUISE A SA SOURCE — ET LE MAIRE, UN SOUCI DE PLUS"},

    # ⚠️ `proteger` d'un personnage DEDANS (le patron de d01, h03) : il est posé à la porte de l'hôtel et nous suit.
    # Les deux hommes arrivent de loin (`loin`) où l'on est ; le dernier objectif est un `retourner` (Louise est
    # dehors, au kiosque) — jamais un `tuer` là où la fin se joue.
    "objectifs": [
        {"type": "aller", "texte": "À LA NUIT, À L'HÔTEL BANDINI : NORBERT FINIT SON QUART",
         "lieu": "hotel", "rayon": 6, "nuit": True},

        {"type": "proteger", "texte": "MÈNE NORBERT AU KIOSQUE, OÙ LOUISE L'ATTEND",
         "cible": "norbert", "lieu": "kiosque", "rayon": 5},

        {"type": "tuer", "texte": "DEUX HOMMES LE SUIVAIENT : COUCHE-LES",
         "groupe": "cravates", "n": 2, "loin": 10},

        {"type": "retourner", "texte": "LOUISE ÉCOUTE NORBERT : VA LA VOIR"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:hotel", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Louise : pour une fois, elle baisse la voix ; une source, ça se protège.
    # Norbert : le vouvoiement, la troisième personne, jamais le nom d'un client — et une inquiétude très polie.
    "dialogue": {
        "appel": [
            _l("louise", "Louise. Ma source a quelque chose de gros, pis elle a peur. J'ai besoin de toi ce soir.",
               jeu="[quietly] Louise. [serious] Ma source a quelque chose de gros, pis elle a peur. J'ai besoin de toi ce soir.")
        ],
        "intro": [
            _l("louise", "Ma source, c'est Norbert, le concierge de l'hôtel. Il voit tout, pis il vend poliment.",
               jeu="[quietly] Ma source, c'est Norbert, le concierge de l'hôtel. [wryly] Il voit tout, pis il vend poliment."),
            _l("louise", "Il finit son quart à la noirceur. Ramène-le ici, à pied ou en char, mais ramène-le.",
               jeu="[serious] Il finit son quart à la noirceur. [firmly] Ramène-le ici, à pied ou en char, mais ramène-le."),
            _l("louise", "Quelqu'un l'a vu parler au maire. Ça fait deux jours qu'il dort pas.",
               jeu="[concerned] Quelqu'un l'a vu parler au maire. [quietly] Ça fait deux jours qu'il dort pas.")
        ],
        "pendant": [
            _p("louise", "La lumière de la réception s'éteint à minuit. C'est ton signal.", 0,
               jeu="[quietly] La lumière de la réception s'éteint à minuit. [serious] C'est ton signal."),
            _p("norbert", "Monsieur est ponctuel. Si Monsieur veut bien marcher du côté de la rue, je préfère le mur.", 1,
               jeu="[calm] Monsieur est ponctuel. [quietly] Si Monsieur veut bien marcher du côté de la rue, je préfère le mur."),
            _p("norbert", "Je crains que ces messieurs ne soient pas des clients. Je les ai vus avec le chauffeur du maire.", 2,
               jeu="[concerned] Je crains que ces messieurs ne soient pas des clients. [quietly] Je les ai vus avec le chauffeur du maire."),
            _p("louise", "Il est là, il tremble, pis il parle. Viens entendre ça.", 3,
               jeu="[excited] Il est là, il tremble, pis il parle. [quietly] Viens entendre ça.")
        ],
        "fin": [
            _l("louise", "Le maire a une chambre à l'année à l'hôtel. Payée par la ville. Norbert a les reçus.",
               jeu="[excited] Le maire a une chambre à l'année à l'hôtel. [serious] Payée par la ville. Norbert a les reçus."),
            _l("louise", "Il me manque juste une preuve qu'on peut imprimer. Je te rappelle, mon beau.",
               jeu="[knowingly] Il me manque juste une preuve qu'on peut imprimer. [teasing] Je te rappelle, mon beau.")
        ],
        "echec": [
            _l("louise", "Ma source s'est évaporée. Pis moi, je viens de perdre deux jours.",
               jeu="[disappointed] Ma source s'est évaporée. [bitterly] Pis moi, je viens de perdre deux jours.")
        ]
    }
}
