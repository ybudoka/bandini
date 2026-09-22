"""La mission f04 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "f04",
    "titre": "Le Grand Mo sait tout",
    "donneur": "mo",
    "prerequis": ["m6"],
    "recompense": 150,
    "donne": {"message": "TROIS PAQUETS DE ROCCO, RETROUVÉS"},

    # ⚠️ `acheter` (M16) : `B.partie.armes[article]` est ce que le juge regarde
    # (`histoire.js`) — un article `arme` (`magasins.COMPTOIRS`) le remplit vraiment à
    # l'achat (`Combat.ramasserArme`) ; une bouchée (bière, café) se mange sur place et
    # ne laisse rien dans le sac. `boutique:artisan` vend déjà "couteau".
    "objectifs": [
        {"type": "acheter", "texte": "ACHÈTE-LUI UN COUTEAU À LA QUINCAILLERIE",
         "article": "couteau", "ou": "boutique:artisan"},

        {"type": "tuer", "texte": "CHASSE LES DEUX CRAVATES DE SA CACHE",
         "groupe": "cravates", "n": 2, "ou": "donneur", "loin": 12},

        {"type": "retourner", "texte": "RETOURNE VOIR LE GRAND MO"}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Le Grand Mo : lent, qui traîne ses phrases et
    # fait durer le mystère, puis chaleureux une fois servi — le contraire de sa lenteur
    # habituelle, comme un homme qui a enfin quelqu'un à qui parler.
    "dialogue": {
        "appel": [
            _l("mo", "Le Grand Mo, on m'appelle de même. Viens t'asseoir un peu, j'ai de quoi te dire.",
               jeu="[knowingly] Le Grand Mo, on m'appelle de même. [amused] Viens t'asseoir un peu… j'ai de quoi te dire.")
        ],
        "intro": [
            _l("mo", "J'ai tout vu passer icitte, pis j'oublie rien.",
               jeu="[somber] J'ai tout vu passer icitte… pis j'oublie rien."),
            _l("mo", "Mon vieux couteau a rendu l'âme. Amène-m'en un de la quincaillerie, pis je te dis ce que je sais.",
               jeu="[amused] Mon vieux couteau a rendu l'âme. [knowingly] Amène-m'en un de la quincaillerie… pis je te dis ce que je sais.")
        ],
        "pendant": [
            _p("mo", "Deux gars en cravate traînent encore près d'où Rocco cachait ses affaires. Va falloir les convaincre.", 1,
               jeu="[wryly] Deux gars en cravate traînent encore… près d'où Rocco cachait ses affaires. [firmly] Va falloir les convaincre.")
        ],
        "fin": [
            _l("mo", "Trois paquets, retrouvés. Rocco aurait aimé ça, te voir faire le ménage.",
               jeu="[warmly] Trois paquets, retrouvés. [somber] Rocco aurait aimé ça… te voir faire le ménage."),
            _l("mo", "Reviens t'asseoir, un de ces jours. J'ai d'autres histoires.",
               jeu="[amused] Reviens t'asseoir, un de ces jours. [warmly] J'ai d'autres histoires.")
        ],
        "echec": [
            _l("mo", "Ben... reviens quand t'auras le temps. Les paquets partiront pas tout seuls, remarque.",
               jeu="[wryly] Ben… reviens quand t'auras le temps. [amused] Les paquets partiront pas tout seuls, remarque.")
        ]
    },

    # Intention (intro) : Mo ne montre rien — il n'a que sa mémoire, un haussement
    # d'épaules et l'air de celui qui sait plus qu'il n'en dit. ⚠️ `boutique:artisan`
    # (le comptoir de l'objectif) n'est écrit nulle part ici à dessein : le défaut irait
    # le montrer par une caméra, et rien ne garantit qu'une quincaillerie se trouve à
    # portée d'une rue filmable depuis le terminus.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "hausser", "duree": 70, "ensemble": True},
            {"type": "dire"},
        ],
    },
}
