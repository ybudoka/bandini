"""La mission c02 — voir app/missions/__init__.py pour le moteur.

La deuxième du Petit-Canton, la première de la chute du Pouce (docs/jalons/le-quartier-chinois.md, étape 3 ; Martin,
29 sept. 2026 : « on fait tomber le Pouce pour de bon »). Irène veut ses dés pipés DANS SA MAIN : « il a l'air
croche », ça ne fait tomber personne. Au sous-sol, on mise gros ; quand le Pouce glisse ses pipés sur le feutre, on
lui fait son propre truc — GLISSER TES DÉS : les siens dans ta manche, une paire honnête à la place
(`Tripot.glisser`, `tripot.PREUVE`). L'objectif `obtenir` a une `table` : l'objet ne se pose nulle part en ville,
il vient du feutre. Il avance à la sortie, comme tout objectif (dans une pièce, `majObjectif` dort).
"""

from ._commun import _l, _p, _r

MISSION = {
    "slug": "c02",
    "titre": "Une paire dans la manche",
    "donneur": "irene",
    "prerequis": ["c01"],
    "recompense": 500,
    # ⚠️ Le Pouce ne sort ses pipés qu'à partir de 500 $ (`tripot.PIPES["seuil"]`) : sans ça en poche, on ne
    # pourrait même pas le faire tricher. Le téléphone attend qu'on les ait.
    "exige": {"argent_min": 500},
    "donne": {"message": "LES DÉS DU POUCE SONT DANS TA POCHE"},

    # ⚠️ Irène se tient DEDANS (`point:irene`) : ni `retourner`, ni rien de posé « près du joueur ». `ou` ne dit que
    # où aller (le Dragon d'or, dont l'escalier descend au tripot) ; `table` : l'objet vient du feutre de la
    # barbotte (`Infiltration` ne le pose pas), et `nom`, ce que le HUD dit quand il entre dans la manche.
    "objectifs": [
        {"type": "obtenir", "texte": "EMPOCHE LES DÉS JAUNES DU POUCE — MISE 500 $",
         "objet": "des_pipes", "ou": "nord_casino", "table": "tripot", "nom": "LES DÉS PIPÉS DU POUCE"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Irène : la croupière qui passe un truc du métier à son élève, à voix
    # basse, avec le plaisir de qui attend ce moment depuis longtemps ; le « je gage » en taquinerie ; au combiné, à
    # la fin, l'émerveillement retenu d'une professionnelle devant un beau geste — puis elle pense déjà à l'argent
    # du monde. Elle se nomme à l'appel, une fois.
    "dialogue": {
        "appel": [
            _l("irene", "C'est Irène Lam, mon pigeon. J'ai un tour de passe-passe à te montrer, pis c'est pas avec des cartes.",
               jeu="[mischievously] C'est Irène Lam, mon pigeon. [teasing] J'ai un tour de passe-passe à te montrer… pis c'est pas avec des cartes.")
        ],
        "intro": [
            _l("irene", "Pour faire tomber le Pouce, « il a l'air croche », ça suffit pas. Il me faut ses dés jaunes, dans ma main.",
               jeu="[quietly] Pour faire tomber le Pouce, « il a l'air croche »… ça suffit pas. [firmly] Il me faut ses dés jaunes, dans ma main."),
            _l("irene", "Tiens, une paire honnête. Mise gros, pis quand ses pipés arrivent sur le feutre, glisse les tiens.",
               jeu="[knowingly] Tiens, une paire honnête. [quietly] Mise gros, pis quand ses pipés arrivent sur le feutre… glisse les tiens."),
            _l("irene", "C'est son truc à lui. Je gage cinq piasses qu'il a jamais pensé qu'on lui ferait.",
               jeu="[amused] C'est son truc à lui. [teasing] Je gage cinq piasses qu'il a jamais pensé qu'on lui ferait.")
        ],
        "pendant": [
            _p("irene", "Cinq cents piasses, pas moins. En bas de ça, il se donne même pas la peine de tricher.", 0,
               jeu="[matter-of-fact] Cinq cents piasses, pas moins. [wryly] En bas de ça, il se donne même pas la peine de tricher.")
        ],
        # ⚠️ Lui parler pendant l'objectif (au bar, avant ou après le coup) : elle renvoie au sous-sol, et dit de
        # sortir — c'est dehors que l'objectif avance.
        "renvoi": [
            _r("irene", "Pas ici, voyons! En bas, à la barbotte. Pis quand c'est fait, sors d'icitte sans courir.", 0,
               jeu="[surprised] Pas ici, voyons! [quietly] En bas, à la barbotte. [firmly] Pis quand c'est fait… sors d'icitte sans courir.")
        ],
        "fin": [
            _l("irene", "T'es sorti avec, pis il a rien vu? Trente ans que j'attends de voir ça.",
               jeu="[impressed] T'es sorti avec, pis il a rien vu? [amused] Trente ans que j'attends de voir ça."),
            _l("irene", "Garde-les dans ta poche. C'est la place la plus sûre du quartier, astheure.",
               jeu="[knowingly] Garde-les dans ta poche. [teasing] C'est la place la plus sûre du quartier, astheure."),
            _l("irene", "Mais des dés, c'est juste la triche. Moi, je veux savoir où dort l'argent du monde.",
               jeu="[serious] Mais des dés… c'est juste la triche. [firmly] Moi, je veux savoir où dort l'argent du monde.")
        ],
        "echec": [
            _l("irene", "Pas de dés, pas de preuve. Je vas finir par manquer de cinq piasses, avec toi.",
               jeu="[disappointed] Pas de dés, pas de preuve. [wryly] Je vas finir par manquer de cinq piasses, avec toi.")
        ]
    },

    # Intention (intro) : au bout du bar, Irène croise les bras comme une croupière qui surveille la salle, puis
    # elle te DONNE la paire honnête (le geste sur le mot « Tiens ») ; la caméra sort voir le Dragon d'or, sous
    # lequel ça se joue, pendant la chute du gage. ⚠️ La coupe en `ensemble`, PUIS la réplique : la voix retient.
    # Intention (fin) : on la voit à sa porte, au combiné — elle savoure, puis elle pense déjà à la suite.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "geste", "acteur": "donneur", "geste": "donner", "vers": "joueur", "duree": 60, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "porte:nord_casino", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:irene", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },
}
