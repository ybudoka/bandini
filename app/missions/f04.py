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

        # ⚠️ Des missions plus longues (Martin, 22 sept. 2026) : la fin disait « trois paquets,
        # retrouvés » sans qu'on en ramasse un. Les trois caches de Rocco, aux trois coins de la
        # ville : l'hôtel (au sud-ouest), le phare (à l'est), et le troisième qui file en moto —
        # un Cravate s'en rappelait aussi (`ramasser` + `fuyard`, posé près de toi, au phare).
        # Des lieux déjà de mission : la ville ne bouge pas.
        {"type": "aller", "texte": "LE PREMIER PAQUET : DERRIÈRE L'HÔTEL BANDINI",
         "lieu": "hotel", "rayon": 6},

        {"type": "aller", "texte": "LE DEUXIÈME : AU PIED DU PHARE DE LA POINTE",
         "lieu": "phare", "rayon": 6},

        {"type": "ramasser", "texte": "LE TROISIÈME FILE EN MOTO : RATTRAPE-LE",
         "cible": "fuyard", "vehicule": "moto"},

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
               jeu="[wryly] Deux gars en cravate traînent encore… près d'où Rocco cachait ses affaires. [firmly] Va falloir les convaincre."),
            _p("mo", "Rocco cachait ses affaires à trois places. La première, derrière l'hôtel qui porte son nom.", 2,
               jeu="[knowingly] Rocco cachait ses affaires à trois places. [amused] La première… derrière l'hôtel qui porte son nom."),
            _p("mo", "La deuxième, au pied du phare. Il aimait ça, les places où on voit venir le monde.", 3,
               jeu="[somber] La deuxième, au pied du phare. [knowingly] Il aimait ça, les places où on voit venir le monde."),
            _p("mo", "Le troisième s'en va en moto? Ah ben. Y a d'autre monde qui a de la mémoire, faut croire.", 4,
               jeu="[surprised] Le troisième s'en va en moto? [amused] Ah ben. Y a d'autre monde qui a de la mémoire, faut croire."),
            _p("mo", "Rapporte-moi ça au banc. Prends ton temps, moi, j'ai rien que ça.", 5,
               jeu="[warmly] Rapporte-moi ça au banc. [amused] Prends ton temps… moi, j'ai rien que ça.")
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
