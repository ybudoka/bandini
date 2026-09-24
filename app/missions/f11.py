"""La mission f11 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "f11",
    "titre": "Mado tient tête",
    "donneur": "mado",
    "prerequis": ["m6"],
    "recompense": 200,
    "donne": {"message": "LE CASSE-CROÛTE TIENT UN JOUR DE PLUS"},

    # ⚠️ `survivre`, déclaré depuis M6 et jamais utilisé, sert enfin : tenir le temps
    # que la menace parle avant qu'elle ne dégénère. La bagarre vient après, pas pendant.
    #
    # « Des missions plus longues » (Martin, 22 sept. 2026) : pendant qu'on se bat, un
    # troisième file avec la caisse de Mado dans une berline (`ramasser` + `fuyard`,
    # le patron de m2/f03) ; on la lui rapporte (`retourner`, elle se tient dehors).
    "objectifs": [
        {"type": "survivre", "texte": "TIENS BON, ILS NÉGOCIENT ENCORE", "secondes": 30},

        {"type": "tuer", "texte": "REPOUSSE LES DEUX CRAVATES",
         "groupe": "cravates", "n": 2, "ou": "donneur", "loin": 10},

        {"type": "ramasser", "texte": "LE TROISIÈME FILE AVEC LA CAISSE",
         "cible": "fuyard", "vehicule": "auto"},

        {"type": "retourner", "texte": "RAPPORTE LA CAISSE À MADO"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Mado : inquiète mais jamais soumise à l'appel,
    # ferme pendant la menace, puis chaleureuse et increvable une fois les gars partis.
    "dialogue": {
        "appel": [
            _l("mado", "C'est Mado, du casse-croûte! Deux gars en cravate menacent de casser mes vitrines si je paie pas.",
               jeu="[worried] C'est Mado, du casse-croûte! [bitterly] Deux gars en cravate menacent de casser mes vitrines… si je paie pas.")
        ],
        "intro": [
            _l("mado", "Ils sont là, dehors, à me regarder avec leurs belles cravates. Reste avec moi une minute.",
               jeu="[firmly] Ils sont là, dehors, à me regarder avec leurs belles cravates. [worried] Reste avec moi une minute."),
            _l("mado", "Après ça, tu leur fais comprendre que le Faubourg paie pas de protection à personne.",
               jeu="[firmly] Après ça, tu leur fais comprendre… que le Faubourg paie pas de protection à personne."),
            _l("mado", "Pis garde un œil sur ma caisse. Ces gars-là repartent jamais les mains vides.",
               jeu="[worried] Pis garde un œil sur ma caisse. [bitterly] Ces gars-là repartent jamais les mains vides.")
        ],
        "pendant": [
            _p("mado", "Bougez pas de ma porte, les gars, sinon ça va mal virer pour vous.", 1,
               jeu="[firmly] Bougez pas de ma porte, les gars… [menacingly] sinon ça va mal virer pour vous."),
            _p("mado", "Le troisième se sauve avec ma caisse! Rattrape-le, mon grand, c'est ma semaine au complet!", 2,
               jeu="[worried] Le troisième se sauve avec ma caisse! [firmly] Rattrape-le, mon grand, c'est ma semaine au complet!"),
            _p("mado", "Reviens au casse-croûte avec ça. Pis compte pas les billets, y en a des collés au ketchup.", 3,
               jeu="[relieved] Reviens au casse-croûte avec ça. [playfully] Pis compte pas les billets… y en a des collés au ketchup.")
        ],
        "fin": [
            _l("mado", "C'est réglé. Mon casse-croûte va respirer encore un bout.",
               jeu="[relieved] C'est réglé. [warmly] Mon casse-croûte va respirer encore un bout."),
            _l("mado", "Assis-toi, mon grand, j't'en garde une portion — pas question que tu repartes le ventre vide.",
               jeu="[warmly] Assis-toi, mon grand… [tenderly] j't'en garde une portion, pas question que tu repartes le ventre vide.")
        ],
        "echec": [
            _l("mado", "Ouain... Reviens, j't'en garde une portion pareil.",
               jeu="[disappointed] Ouain… [warmly] Reviens, j't'en garde une portion pareil.")
        ]
    }
}
