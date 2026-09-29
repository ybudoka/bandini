"""La mission c08 — voir app/missions/__init__.py pour le moteur.

Les portes ouvertes — la dernière de l'arc du vieux maître (docs/jalons/l-ecole-rivale.md, vague 2). L'école rouvre
demain matin, et Victor Tam va le crier dans tout le quartier : on l'escorte à pied jusqu'au Dragon d'or, où Irène
pose son affiche, et on repousse les derniers frimeurs qui veulent lui faire peur.

⚠️ **L'ÉCOLE ROUVRE** (`mantes.REPRISE`, `apres: c08`) : dans la salle, les élèves ne sont plus du gang et font face au
maître ; dans la rue, beaucoup moins de Mantes ; et le gang est CALME (`donne.calme`). Le lendemain matin, le Clairon
en fait sa une (`donne.manchette`, `journal.SPECIALES`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "c08",
    "titre": "Les portes ouvertes",
    "donneur": "maitre",
    "prerequis": ["c07"],
    "recompense": 1200,
    "donne": {"calme": "mantes", "manchette": "ecole_rouverte", "message": "L'ÉCOLE LA MANTE ROUVRE SES COURS"},

    # ⚠️ Le maître est DEDANS : l'escorte (`proteger`) le pose à la porte de son école quand on sort (un personnage
    # neuf, puisqu'il ne se tient pas en ville), et il nous suit sur nos pas jusqu'au Dragon d'or (DÉJÀ un lieu de
    # mission). Puis les derniers frimeurs arrivent sur LUI (`ou: "donneur"`, `loin` : ils naissent hors de l'écran et
    # courent) — le patron de p14. La mission finie, il reste planté devant le Dragon d'or à jaser avec Irène : il ne
    # se sauve pas avec les figurants (`Histoire.nettoyer`).
    "objectifs": [
        {"type": "proteger", "texte": "ESCORTE LE MAÎTRE JUSQU'AU DRAGON D'OR",
         "cible": "maitre", "lieu": "nord_casino", "rayon": 6},

        {"type": "tuer", "texte": "LES DERNIERS FRIMEURS ARRIVENT — PROTÈGE LE MAÎTRE",
         "groupe": "mantes", "n": 4, "ou": "donneur", "loin": 10, "arme": "", "vie": 80},
    ],

    # Le jeu de chaque réplique (`jeu=`) — le maître : l'entrain d'un homme qui rouvre sa maison, avec ses affiches ;
    # la bravade comique quand il parle de peur (l'alligator) ; dans la rue, la lenteur heureuse d'un snowbird ; sous
    # l'attaque, le calme du professeur ; à la fin, la joie simple, et la gratitude dite une fois. Irène, à la porte du
    # Dragon d'or : sa gageure, pour la dernière fois tendre — elle ne se renomme pas, on la connaît.
    "dialogue": {
        "appel": [
            _l("maitre", "Sifu Tam. Demain matin, l'école rouvre, pis je vais le crier dans tout le quartier.",
               jeu="[excited] Sifu Tam. [cheerful] Demain matin, l'école rouvre… pis je vais le crier dans tout le quartier.")
        ],
        "intro": [
            _l("maitre", "J'ai imprimé des affiches. Irène en met une au Dragon d'or, entre la loto pis les dés.",
               jeu="[confident] J'ai imprimé des affiches. [amused] Irène en met une au Dragon d'or… entre la loto pis les dés."),
            _l("maitre", "Tu marches avec moi. Les derniers frimeurs vont vouloir me faire peur.",
               jeu="[serious] Tu marches avec moi. [knowingly] Les derniers frimeurs vont vouloir me faire peur."),
            _l("maitre", "Moi, j'ai eu peur une fois dans ma vie : un alligator dans la piscine du condo.",
               jeu="[deadpan] Moi, j'ai eu peur une fois dans ma vie… [amused] un alligator dans la piscine du condo.")
        ],
        "pendant": [
            _p("maitre", "Marche à mon pas, petit scarabée. En Floride, personne court, il fait trop chaud.", 0,
               jeu="[casually] Marche à mon pas, petit scarabée. [amused] En Floride, personne court… il fait trop chaud."),
            _p("maitre", "Les voilà. Je tiens l'affiche, tu tiens le reste.", 1,
               jeu="[calm] Les voilà. [firmly] Je tiens l'affiche… tu tiens le reste.")
        ],
        "fin": [
            _l("maitre", "Premier cours demain, sept heures. Kenny fait le café, pis Monsieur Bois fait l'accueil.",
               jeu="[happy] Premier cours demain, sept heures. [amused] Kenny fait le café… pis Monsieur Bois fait l'accueil."),
            _l("irene", "Victor, je gage cinq piasses que t'en as dix au cours. Pis le pigeon, lui, il paye pas.",
               jeu="[teasing] Victor, je gage cinq piasses que t'en as dix au cours. [warmly] Pis le pigeon, lui… il paye pas."),
            _l("maitre", "Irène a jamais perdu une gageure. Merci, petit scarabée. Reviens t'entraîner.",
               jeu="[laughs] [amused] Irène a jamais perdu une gageure. [tenderly] Merci, petit scarabée. [warmly] Reviens t'entraîner.")
        ],
        "echec": [
            _l("maitre", "Les frimeurs ont gagné à soir. Mais la mante, c'est patient : on recommence demain.",
               jeu="[disappointed] Les frimeurs ont gagné à soir. [calm] Mais la mante, c'est patient : on recommence demain.")
        ]
    },

    # Intention (intro) : dans sa salle, le maître tient ses affiches comme un trophée ; la caméra va voir la porte du
    # Dragon d'or, où l'affiche ira ; puis la bravade, et l'alligator. ⚠️ La coupe en `ensemble`, PUIS la réplique.
    # Intention (fin) : la caméra va voir l'école qui rouvre demain pendant qu'il le dit — la joie du professeur —,
    # puis la porte du Dragon d'or, où Irène sort sa gageure, et il a le dernier mot, tendre. ⚠️ Des COUPES, pas un
    # `marcher` : il est là quand on la joue (l'escorte l'a mené au Dragon d'or), mais une fin se juge aussi jouée
    # seule, sans l'escorte — et Irène, elle, parle de derrière son bar.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "joueur", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "chez:irene", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:maitre", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "coupe", "vers": "chez:irene", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
        ],
    },
}
