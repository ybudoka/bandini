"""La mission q13 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "q13",
    "titre": "La nuit des Morues",
    "donneur": "josee",
    # ⚠️ APRÈS LE CHOIX, QUEL QU'IL SOIT : q10 (Sven) ou q11 (Josée) — l'autre est fermée pour de bon. Un
    # prérequis ne sait dire que « et » : `exige.une_de` dit « l'un ou l'autre » (`Histoire.exigeTenu`).
    # Sven a eu son argent ou a perdu ses camions : dans les deux cas, il revient chercher le port.
    "prerequis": ["q06"],
    "exige": {"une_de": ["q10", "q11"]},
    "recompense": 500,
    # ⚠️ LA PREMIÈRE LIBÉRATION DE M16 (`libere: quais`) : les Morues rangent leurs couteaux — plus une ne
    # traîne dans leur coin du port (`Entites.gangChasse`), ni ne te saute dessus (`gangCalme`), ni ne prend
    # ou ne perd un coin la nuit (`Territoires.horsJeu`), et ce qu'elles avaient pris ailleurs revient
    # (`Territoires.liberer`) ; sous la mini-carte, leur cour redevient « Les Quais ». Et le Clairon en parle.
    "donne": {"libere": "quais", "manchette": "quais_liberes", "message": "LES QUAIS SONT LIBRES"},

    # L'hôtel, de nuit : deux vagues de matelots de Sven qui débarquent (`pieton: matelot`, un piéton de
    # mission — ni une Morue ni un passant), puis leur bosco. Ils ARRIVENT (`loin`) : ils naissent hors de
    # l'écran une fois la réplique dite, et courent sur toi. Le bosco est un chef (couteau, 200 de vie).
    "objectifs": [
        {"type": "aller", "texte": "ATTENDS LA NUIT DEVANT L'HÔTEL BANDINI",
         "lieu": "hotel", "rayon": 6, "nuit": True},

        {"type": "tuer", "texte": "LES MATELOTS DE SVEN DÉBARQUENT — TIENS L'HÔTEL",
         "groupe": "morues", "pieton": "matelot", "n": 3, "ou": "hotel", "loin": 12},

        {"type": "tuer", "texte": "UNE DEUXIÈME CHALOUPE — ILS REVIENNENT",
         "groupe": "morues", "pieton": "matelot", "n": 3, "ou": "hotel", "loin": 12},

        {"type": "tuer", "texte": "LE BOSCO DE SVEN — COUCHE-LE",
         "groupe": "morues", "pieton": "matelot", "n": 1, "chef": True, "arme": "couteau", "vie": 200,
         "loin": 10},
    ],

    # ⚠️ L'INTRO EST ÉCRITE (la recette de q11 : Josée est DEDANS) ; la FIN aussi : elle va voir le port
    # tranquille (le coin des Morues, vide), puis la Chef chez elle — on n'entend personne qui n'est pas là.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "porte:hotel", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
        ],
        "fin": [
            {"type": "coupe", "vers": "zone:morues", "ferme": 25, "ouvre": 25, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "chez:josee", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Josée, la nuit où tout se joue : elle ne hausse pas le ton, même
    # quand Sven tire. C'est la seule mission où elle dit « merci », et elle le dit mal, parce qu'elle ne l'a
    # jamais dit. Sven, au combiné : poli, froid, un homme d'affaires qui a perdu une affaire.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. Sven a fini de négocier. Il débarque cette nuit, à l'hôtel.",
               jeu="[coldly] Josée. Sven a fini de négocier. [gravely] Il débarque cette nuit, à l'hôtel.")
        ],
        "intro": [
            _l("josee", "L'hôtel, c'est la porte du port. Qui tient l'hôtel tient les Quais.",
               jeu="[matter-of-fact] L'hôtel, c'est la porte du port. [firmly] Qui tient l'hôtel… tient les Quais."),
            _l("josee", "Mes Morues gardent la ruelle. Toi, tu tiens la porte d'en avant.",
               jeu="[calm] Mes Morues gardent la ruelle. [confident] Toi, tu tiens la porte d'en avant."),
            _l("josee", "Après cette nuit, plus personne décide des Quais à notre place. Ni Sven, ni moi.",
               jeu="[serious] Après cette nuit, plus personne décide des Quais à notre place. [quietly] Ni Sven… ni moi.")
        ],
        "pendant": [
            _p("josee", "La nuit tombe. Reste devant la porte, il viendra par là.", 0,
               jeu="[quietly] La nuit tombe. [calm] Reste devant la porte… il viendra par là."),
            _p("sven", "Sven. Tu as choisi ton quai, mon ami. Moi, je reprends le mien.", 1,
               jeu="[Norwegian accent][coldly] Sven. Tu as choisi ton quai… mon ami. [menacingly] Moi, je reprends le mien."),
            _p("josee", "Une deuxième chaloupe. Il a vidé son bateau pour nous.", 2,
               jeu="[matter-of-fact] Une deuxième chaloupe. [wryly] Il a vidé son bateau pour nous."),
            _p("josee", "Son bosco. Couche-le, pis Sven a plus personne à envoyer.", 3,
               jeu="[menacingly] Son bosco. [firmly] Couche-le… pis Sven a plus personne à envoyer.")
        ],
        "fin": [
            _l("josee", "Regarde le port. Pas une Morue avec un couteau. Pas un matelot.",
               jeu="[quietly] Regarde le port. [satisfied] Pas une Morue avec un couteau. Pas un matelot."),
            _l("josee", "Les Quais sont libres. Le Clairon va l'écrire, pis pour une fois il aura raison.",
               jeu="[confident] Les Quais sont libres. [wryly] Le Clairon va l'écrire, pis pour une fois il aura raison."),
            _l("josee", "Merci. Je le dis pas souvent, fait que retiens-le.",
               jeu="[warmly] Merci. [softly] Je le dis pas souvent… fait que retiens-le.")
        ],
        "echec": [
            _l("josee", "Sven a pris l'hôtel. Demain, il va vouloir le reste.",
               jeu="[coldly] Sven a pris l'hôtel. [gravely] Demain… il va vouloir le reste.")
        ]
    }
}
