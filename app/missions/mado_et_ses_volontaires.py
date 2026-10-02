"""Le chapitre de Mado — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague F). Martin a tranché
pour les arcs hors de la liste de M16 : Mado qui tient tête aux Cravates (f11) puis ses trois feux et le pyromane
(f13, les volontaires — elle n'attendait que f11) deviennent deux ACTES. Visée : 6 à 8 minutes, rien d'ajouté.
L'échec `chrono` de f13 (chaque feu a 90 s) vaut pour le chapitre : f11 n'a pas de chrono.

Ce qui a bougé, et pourquoi (comme aux autres chapitres) :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la
  première mission restent ceux du chapitre ; la fin de la première se dit à l'ouverture de l'acte 2, suivie de
  l'appel et de l'intro de la seconde ; la fin de la seconde reste la fin du chapitre ; chacune garde son échec
  (`_e`, accroché à son acte) ;
- l'acte 1 paie sa prime et accorde ce que sa mission accordait en finissant (`donne` sur l'objectif qui le
  finit), et la mission qu'il remplace est faite à l'ouverture de l'acte 2 — ce qui l'attendait s'ouvre là ;
- la scène d'intro de la première reste celle du chapitre, la scène de fin de la seconde celle de sa fin ; les
  deux autres tombent (leurs répliques se disent au marqueur), comme au pilote.
- QUI PARLE SE NOMME une fois par chapitre : l'appel de f13 perd « C'est Mado! » — la même voix, coupée au silence
  (on sort de son casse-croûte, la portion promise encore chaude).
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "mado_et_ses_volontaires",
    "titre": "Mado et ses volontaires",
    "donneur": "mado",
    "prerequis": ["m6"],
    "remplace": ["f11", "f13"],
    "recompense": 250,
    "donne": {"message": "LE FAUBOURG A SES POMPIERS VOLONTAIRES"},
    "echec": ["mort", "arrete", "chrono"],

    "objectifs": [
        # --- Acte 1 (f11, « Mado tient tête »).
        {"type": "acte", "texte": "ACTE 1 — MADO TIENT TÊTE", "donneur": "mado"},  # 0
        {"type": "survivre", "texte": "TIENS BON, ILS NÉGOCIENT ENCORE", "secondes": 30},  # 1
        {"type": "tuer", "texte": "REPOUSSE LES DEUX CRAVATES", "groupe": "cravates", "n": 2, "ou": "donneur", "loin": 10},  # 2
        {"type": "ramasser", "texte": "LE TROISIÈME FILE AVEC LA CAISSE", "cible": "fuyard", "vehicule": "auto"},  # 3
        {"type": "retourner", "texte": "RAPPORTE LA CAISSE À MADO", "donne": {"message": "LE CASSE-CROÛTE TIENT UN JOUR DE PLUS", "prime": 200}},  # 4
        # --- Acte 2 (f13, « Les volontaires »).
        {"type": "acte", "texte": "ACTE 2 — LES VOLONTAIRES", "donneur": "mado"},  # 5
        {"type": "eteindre", "texte": "ÉTEINS LE FEU DU KIOSQUE", "ou": "porte:kiosque", "remet": "extincteur", "chrono_s": 90},  # 6
        {"type": "eteindre", "texte": "LA BOUTIQUE DE ROSA BRÛLE", "ou": "porte:vetements", "chrono_s": 90},  # 7
        {"type": "eteindre", "texte": "LE TERMINUS AUSSI, VITE", "ou": "porte:terminus", "chrono_s": 90},  # 8
        {"type": "ramasser", "texte": "RATTRAPE LE PYROMANE ET SON BIDON", "cible": "fuyard", "vehicule": "auto"},  # 9
        {"type": "retourner", "texte": "RAPPORTE LE BIDON À MADO"},  # 10
    ],

    # f11 — Le jeu de chaque réplique (`jeu=`) — Mado : inquiète mais jamais soumise à l'appel,
    # ferme pendant la menace, puis chaleureuse et increvable une fois les gars partis.
    # f13 — Le jeu de chaque réplique (`jeu=`) — Mado, les volontaires : l'inquiétude à l'appel
    # (le Faubourg brûle, et il n'a pas de caserne), la fermeté d'une femme qui distribue
    # les tâches comme des assiettes, puis la colère froide quand elle comprend qui a mis
    # le feu — et la chaleur à la fin, qui n'est pas du soulagement : de la fierté.
    "dialogue": {
        "appel": [
            _l("mado", "C'est Mado, du casse-croûte! Deux gars en cravate menacent de casser mes vitrines si je paie pas.", jeu="[worried] C'est Mado, du casse-croûte! [bitterly] Deux gars en cravate menacent de casser mes vitrines… si je paie pas."),
        ],
        "intro": [
            _l("mado", "Ils sont là, dehors, à me regarder avec leurs belles cravates. Reste avec moi une minute.", jeu="[firmly] Ils sont là, dehors, à me regarder avec leurs belles cravates. [worried] Reste avec moi une minute."),
            _l("mado", "Après ça, tu leur fais comprendre que le Faubourg paie pas de protection à personne.", jeu="[firmly] Après ça, tu leur fais comprendre… que le Faubourg paie pas de protection à personne."),
            _l("mado", "Pis garde un œil sur ma caisse. Ces gars-là repartent jamais les mains vides.", jeu="[worried] Pis garde un œil sur ma caisse. [bitterly] Ces gars-là repartent jamais les mains vides."),
        ],
        "fin": [
            _l("mado", "Trois feux pis un pyromane, avant que le café soit prêt. Le Faubourg a ses pompiers, astheure.", jeu="[impressed] Trois feux pis un pyromane… avant que le café soit prêt. [warmly] Le Faubourg a ses pompiers, astheure."),
            _l("mado", "Garde l'extincteur, mon grand. Quand ça sentira la fumée, c'est toi qu'on va appeler.", jeu="[warmly] Garde l'extincteur, mon grand. [tenderly] Quand ça sentira la fumée… c'est toi qu'on va appeler."),
        ],
        "echec": [
            _e("mado", "Ouain... Reviens, j't'en garde une portion pareil.", 0, jeu="[disappointed] Ouain… [warmly] Reviens, j't'en garde une portion pareil."),
            _e("mado", "Ouain... Le feu va plus vite que nous autres. Reviens, on va recommencer.", 5, jeu="[disappointed] Ouain… Le feu va plus vite que nous autres. [firmly] Reviens, on va recommencer."),
        ],
        "pendant": [
            _p("mado", "Bougez pas de ma porte, les gars, sinon ça va mal virer pour vous.", 2, jeu="[firmly] Bougez pas de ma porte, les gars… [menacingly] sinon ça va mal virer pour vous."),
            _p("mado", "Le troisième se sauve avec ma caisse! Rattrape-le, mon grand, c'est ma semaine au complet!", 3, jeu="[worried] Le troisième se sauve avec ma caisse! [firmly] Rattrape-le, mon grand, c'est ma semaine au complet!"),
            _p("mado", "Reviens au casse-croûte avec ça. Pis compte pas les billets, y en a des collés au ketchup.", 4, jeu="[relieved] Reviens au casse-croûte avec ça. [playfully] Pis compte pas les billets… y en a des collés au ketchup."),
            # Acte 2 : la fin de f11, en personne ; puis l'appel et l'intro de f13.
            _p("mado", "C'est réglé. Mon casse-croûte va respirer encore un bout.", 5, jeu="[relieved] C'est réglé. [warmly] Mon casse-croûte va respirer encore un bout."),
            _p("mado", "Assis-toi, mon grand, j't'en garde une portion — pas question que tu repartes le ventre vide.", 5, jeu="[warmly] Assis-toi, mon grand… [tenderly] j't'en garde une portion, pas question que tu repartes le ventre vide."),
            # ⚠️ Coupée (2 oct. 2026) : « C'est Mado! » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("mado", "Ça sent la fumée partout dans le Faubourg, pis la caserne est à l'autre bout de la baie.", 5, jeu="[worried] Ça sent la fumée partout dans le Faubourg… [firmly] pis la caserne est à l'autre bout de la baie."),
            _p("mado", "Le kiosque de Madame Thibodeau pogne en feu. Tiens, l'extincteur de ma cuisine, il est plein.", 5, jeu="[worried] Le kiosque de Madame Thibodeau pogne en feu. [firmly] Tiens, l'extincteur de ma cuisine… il est plein."),
            _p("mado", "Vise le pied des flammes, pas la fumée. Pis garde-en pour les autres, j'ai l'impression que c'est pas fini.", 5, jeu="[firmly] Vise le pied des flammes, pas la fumée. [worried] Pis garde-en pour les autres… j'ai l'impression que c'est pas fini."),
            _p("mado", "Cours, mon grand! Une minute et demie pis le toit y passe.", 6, jeu="[worried] Cours, mon grand! [firmly] Une minute et demie… pis le toit y passe."),
            _p("mado", "Ça brûle chez Rosa, astheure! Quelqu'un fait le tour du quartier avec des allumettes.", 7, jeu="[surprised] Ça brûle chez Rosa, astheure! [angry] Quelqu'un fait le tour du quartier avec des allumettes."),
            _p("mado", "Le terminus! Fern a des passagers qui attendent dedans, dépêche!", 8, jeu="[worried] Le terminus! [firmly] Fern a des passagers qui attendent dedans… dépêche!"),
            _p("mado", "Je le vois, c'est une Cravate avec un bidon! Il part en char, lâche-le pas.", 9, jeu="[angry] Je le vois, c'est une Cravate avec un bidon! [firmly] Il part en char… lâche-le pas."),
            _p("mado", "Apporte-moi son bidon. Je vais l'accrocher au mur, à côté du menu.", 10, jeu="[coldly] Apporte-moi son bidon. [wryly] Je vais l'accrocher au mur… à côté du menu."),
        ],
    },
}
