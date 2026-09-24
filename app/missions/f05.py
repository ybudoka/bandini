"""La mission f05 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "f05",
    "titre": "Le dernier autobus",
    "donneur": "fern",
    "prerequis": ["m6"],
    "recompense": 200,
    "echec": ["mort", "arrete", "vehicule_detruit", "chrono"],
    "donne": {"message": "LE BOULOT AUTOBUS, AU KLAXON"},

    # ⚠️ `boulots` (M16) : généralise `courses` — `sorte` nomme le compteur
    # (`economie.BOULOTS`, `SORTES` côté JS). L'autobus n'avait pas de boulot avant
    # cette mission ; `vehicules.py` et `economie.py` lui en donnent un.
    "objectifs": [
        {"type": "monter", "texte": "MONTE DANS L'AUTOBUS", "vehicule": "autobus", "ou": "porte:terminus"},

        {"type": "boulots", "texte": "FAIS QUATRE ARRÊTS AU KLAXON", "n": 4, "sorte": "autobus"},

        # ⚠️ Des missions plus longues (Martin, 22 sept. 2026) : la dernière run de la soirée
        # va au phare de La Pointe, à l'autre bout de la ville, à l'heure (`chrono_s`) — puis on
        # y attend Ovila, le gardien, qui la prend tous les soirs (Fern attend toujours « cinq
        # secondes de plus »). `phare` est déjà un lieu de mission : la ville ne bouge pas.
        {"type": "aller", "texte": "LA DERNIÈRE RUN : LE PHARE DE LA POINTE, À L'HEURE",
         "lieu": "phare", "rayon": 6, "chrono_s": 240},

        {"type": "survivre", "texte": "ATTENDS OVILA, LE GARDIEN DU PHARE", "secondes": 20},

        {"type": "livrer", "texte": "RAMÈNE L'AUTOBUS AU TERMINUS",
         "lieu": "terminus", "rayon": 5, "sans_degats": True}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Fern : bref, chronométré, jamais deux mots
    # de trop ; il ne s'attendrit qu'une fois, pour son autobus — puis, une fois l'horaire
    # tenu, un soulagement qu'il ne montre presque pas.
    "dialogue": {
        "appel": [
            _l("fern", "Fern, le chauffeur. Monte, le jeune, on est en retard sur l'horaire!",
               jeu="[matter-of-fact] Fern, le chauffeur. [firmly] Monte, le jeune, on est en retard sur l'horaire!")
        ],
        "intro": [
            _l("fern", "Quatre arrêts, pis tu ramènes l'autobus icitte. Klaxonne pour prendre le monde.",
               jeu="[firmly] Quatre arrêts… pis tu ramènes l'autobus icitte. [matter-of-fact] Klaxonne pour prendre le monde."),
            _l("fern", "Pis avant de rentrer, la run du phare. Le gardien compte sur nous depuis vingt ans.",
               jeu="[matter-of-fact] Pis avant de rentrer, la run du phare. [warmly] Le gardien compte sur nous depuis vingt ans.")
        ],
        "pendant": [
            _p("fern", "Doucement dans les tournants. Un autobus, ça se conduit pas comme un char.", 1,
               jeu="[firmly] Doucement dans les tournants. [wryly] Un autobus, ça se conduit pas comme un char."),
            _p("fern", "Le phare, astheure. Quatre minutes, pas une de plus.", 2,
               jeu="[firmly] Le phare, astheure. [matter-of-fact] Quatre minutes… pas une de plus."),
            _p("fern", "On attend Ovila. Cinq secondes de plus, disons vingt.", 3,
               jeu="[matter-of-fact] On attend Ovila. [wryly] Cinq secondes de plus… disons vingt."),
            _p("fern", "Ramène-la au terminus sans une bosse. On a vieilli ensemble, elle pis moi.", 4,
               jeu="[firmly] Ramène-la au terminus sans une bosse. [tenderly] On a vieilli ensemble, elle pis moi.")
        ],
        "fin": [
            _l("fern", "Quatre arrêts, pas un de manqué. L'horaire est sauf.",
               jeu="[relieved] Quatre arrêts, pas un de manqué. [warmly] L'horaire est sauf."),
            _l("fern", "T'as le tour. Reviens quand tu veux, y'a toujours une run qui traîne.",
               jeu="[impressed] T'as le tour. [warmly] Reviens quand tu veux… y'a toujours une run qui traîne."),
            _l("fern", "Ovila dit jamais merci. Moi non plus, remarque.",
               jeu="[deadpan] Ovila dit jamais merci. [wryly] Moi non plus, remarque.")
        ],
        "echec": [
            _l("fern", "L'horaire est fichu... Reviens demain, p't-être.",
               jeu="[disappointed] L'horaire est fichu… [wryly] Reviens demain, p't-être.")
        ]
    }
}
