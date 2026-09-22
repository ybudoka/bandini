"""La mission f05 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "f05",
    "titre": "Le dernier autobus",
    "donneur": "fern",
    "prerequis": ["m6"],
    "recompense": 200,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"message": "LE BOULOT AUTOBUS, AU KLAXON"},

    # ⚠️ `boulots` (M16) : généralise `courses` — `sorte` nomme le compteur
    # (`economie.BOULOTS`, `SORTES` côté JS). L'autobus n'avait pas de boulot avant
    # cette mission ; `vehicules.py` et `economie.py` lui en donnent un.
    "objectifs": [
        {"type": "monter", "texte": "MONTE DANS L'AUTOBUS", "vehicule": "autobus", "ou": "porte:terminus"},

        {"type": "boulots", "texte": "FAIS QUATRE ARRÊTS AU KLAXON", "n": 4, "sorte": "autobus"},

        {"type": "livrer", "texte": "RAMÈNE L'AUTOBUS AU TERMINUS",
         "lieu": "terminus", "rayon": 5, "sans_degats": True}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Fern : bref, chronométré, jamais deux mots
    # de trop — puis, une fois l'horaire tenu, un soulagement qu'il ne montre presque pas.
    "dialogue": {
        "appel": [
            _l("fern", "Fern, le chauffeur. Monte, le jeune, on est en retard sur l'horaire!",
               jeu="[matter-of-fact] Fern, le chauffeur. [firmly] Monte, le jeune, on est en retard sur l'horaire!")
        ],
        "intro": [
            _l("fern", "Quatre arrêts, pis tu ramènes l'autobus icitte. Klaxonne pour prendre le monde.",
               jeu="[firmly] Quatre arrêts… pis tu ramènes l'autobus icitte. [matter-of-fact] Klaxonne pour prendre le monde.")
        ],
        "pendant": [
            _p("fern", "Doucement dans les tournants. Un autobus, ça se conduit pas comme un char.", 1,
               jeu="[firmly] Doucement dans les tournants. [wryly] Un autobus, ça se conduit pas comme un char.")
        ],
        "fin": [
            _l("fern", "Quatre arrêts, pas un de manqué. L'horaire est sauf.",
               jeu="[relieved] Quatre arrêts, pas un de manqué. [warmly] L'horaire est sauf."),
            _l("fern", "T'as le tour. Reviens quand tu veux, y'a toujours une run qui traîne.",
               jeu="[impressed] T'as le tour. [warmly] Reviens quand tu veux… y'a toujours une run qui traîne.")
        ],
        "echec": [
            _l("fern", "L'horaire est fichu... Reviens demain, p't-être.",
               jeu="[disappointed] L'horaire est fichu… [wryly] Reviens demain, p't-être.")
        ]
    }
}
