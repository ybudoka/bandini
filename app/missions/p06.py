"""La mission p06 — voir app/missions/__init__.py pour le moteur.

Ovila voit des lumières (M16, arc P, 1er oct. 2026). De nuit, une chaloupe accoste sous le phare ; deux matelots de Sven
chargent une caisse dans un camion. Ovila ne voit plus grand-chose — mais il entend un moteur qui n'a rien à faire là.
On attend la nuit au phare, on file le camion (`suivre`) jusqu'à la cantine des Quais, on couche les deux matelots
(`tuer`, `pieton: matelot`), on prend la caisse (`obtenir`, à pied) et on l'apporte à Josée, au Brouillard (`parler`).

⚠️ Écarts à la fiche : la « cabane » des matelots est la ruelle de la cantine (un lieu de mission : la ville ne bouge
pas) ; et on ne les suit pas à pied — `suivre` file un char, ils chargent la caisse dans un camion.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "p06",
    "titre": "Ovila voit des lumières",
    "donneur": "ovila",
    "prerequis": ["p01", "q04"],
    "recompense": 300,
    "donne": {"message": "LA CAISSE DE SVEN EST À JOSÉE"},

    "objectifs": [
        {"type": "aller", "texte": "ATTENDS LA NUIT DEVANT LE PHARE", "lieu": "phare", "rayon": 6, "nuit": True},

        {"type": "suivre", "texte": "LE CAMION DES MATELOTS : FILE-LE SANS QU'ILS TE VOIENT",
         "vehicule": "camion", "loin": 12, "proche": 3, "lieu": "cantine"},

        {"type": "tuer", "texte": "LES DEUX MATELOTS GARDENT LA CAISSE — COUCHE-LES",
         "groupe": "morues", "pieton": "matelot", "n": 2, "ou": "cantine"},

        {"type": "obtenir", "texte": "PRENDS LA CAISSE QU'ILS ONT DÉBARQUÉE, À PIED",
         "objet": "caisse_des_matelots", "ou": "cantine", "dessin": "sac", "nom": "LA CAISSE DES MATELOTS"},

        {"type": "parler", "texte": "APPORTE LA CAISSE À JOSÉE, AU BROUILLARD", "cible": "josee"},
    ],

    # Intention (intro, dedans) : Ovila au pied de sa lampe, qui « voit » ce qu'il entend ; la caméra sort voir le quai
    # sous le phare, vide encore, puis revient pour ce qu'il demande — sans jamais dire qu'il n'y voit plus.
    # Intention (fin) : Josée ouvre la caisse et comprend que Sven n'a pas lâché les Quais ; la caméra va au phare, où
    # Ovila a déjà rallumé sa lampe.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:phare", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "geste", "acteur": "josee", "geste": "prendre", "duree": 60, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "coupe", "vers": "chez:ovila", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Ovila : lent, poli, il vouvoie ; il parle des lumières pour ne pas parler de
    # ses yeux. Jamais pressé, même quand un camion de contrebande passe sous sa fenêtre. Josée, à la fin : sèche, elle
    # compte déjà ce que Sven lui doit.
    "dialogue": {
        "appel": [
            _l("ovila", "Bonsoir. Ici Ovila, au phare. Il y a une lumière sur l'eau qui n'a rien à faire là.",
               jeu="[calm] Bonsoir. Ici Ovila, au phare. [mysteriously] Il y a une lumière sur l'eau… qui n'a rien à faire là.")
        ],
        "intro": [
            _l("ovila", "Trois nuits de suite, une chaloupe accoste sous ma lampe. Pas de feux de position.",
               jeu="[softly] Trois nuits de suite, une chaloupe accoste sous ma lampe. [mysteriously] Pas de feux de position."),
            _l("ovila", "J'entends deux hommes, une caisse lourde, et un camion qui démarre sans phares.",
               jeu="[calm] J'entends deux hommes… une caisse lourde… [mysteriously] et un camion qui démarre sans phares."),
            _l("ovila", "Suivez-les, voulez-vous? Moi, je reste à ma lampe. Elle est tout ce que je garde.",
               jeu="[softly] Suivez-les, voulez-vous? [calm] Moi, je reste à ma lampe. Elle est tout ce que je garde.")
        ],
        "pendant": [
            _p("ovila", "Ils viennent à la noirceur. Attendez-les dehors, sans bruit.", 0,
               jeu="[softly] Ils viennent à la noirceur. [calm] Attendez-les dehors, sans bruit."),
            _p("ovila", "Le camion part. Restez loin derrière : ces gens-là regardent dans leurs miroirs.", 1,
               jeu="[calm] Le camion part. [mysteriously] Restez loin derrière : ces gens-là regardent dans leurs miroirs."),
            _p("ovila", "Ils se sont arrêtés derrière la cantine. Deux hommes, si j'ai bien entendu.", 2,
               jeu="[softly] Ils se sont arrêtés derrière la cantine. [calm] Deux hommes, si j'ai bien entendu."),
            _p("ovila", "La caisse est par terre. Prenez-la à deux mains, elle n'est pas à eux non plus.", 3,
               jeu="[calm] La caisse est par terre. [mysteriously] Prenez-la à deux mains, elle n'est pas à eux non plus."),
            _p("ovila", "Portez-la à madame Josée. Elle saura de quel bateau elle vient.", 4,
               jeu="[softly] Portez-la à madame Josée. [calm] Elle saura de quel bateau elle vient.")
        ],
        "fin": [
            _l("josee", "Des moteurs hors-bord, neufs, pis l'étampe de Sven dessus. Il a pas lâché mes Quais, lui.",
               jeu="[coldly] Des moteurs hors-bord, neufs… pis l'étampe de Sven dessus. [annoyed] Il a pas lâché mes Quais, lui."),
            _l("ovila", "Merci. Ma lampe est rallumée, et la chaloupe ne reviendra pas ce soir.",
               jeu="[calm] Merci. [softly] Ma lampe est rallumée… et la chaloupe ne reviendra pas ce soir.")
        ],
        "echec": [
            _l("ovila", "Ils sont partis. Je ne les entends plus, et ce n'est jamais bon signe.",
               jeu="[softly] Ils sont partis. [sighs] Je ne les entends plus… et ce n'est jamais bon signe.")
        ]
    }
}
