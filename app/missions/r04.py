"""La mission r04 — voir app/missions/__init__.py pour le moteur.

Le sergent contre-attaque (M16, arc R, 30 sept. 2026) — l'autre côté du CHOIX de l'arc (`ferme: r03`). On reste avec
Bouchard. Il veut qu'on lui débarrasse de l'inspectrice : sans auto-patrouille, une inspectrice n'enquête plus.
De nuit, on vole la sienne dans la ruelle du poste, on sème ses collègues, et on la laisse au lot de Gilles, sous
un faux nom — elle y dormira des semaines. Le sergent paie, et il ne l'oubliera pas non plus.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "r04",
    "titre": "Le sergent contre-attaque",
    "donneur": "bouchard",
    "prerequis": ["r02"],
    "ferme": "r03",
    "recompense": 500,
    "donne": {"sergent_ami": True, "message": "LE SERGENT BOUCHARD TE DOIT UNE FAVEUR, POUR DE BON"},

    # ⚠️ `monter` dans une ruelle d'un lieu déjà lieu de mission (`ruelle:poste:10`, le patron de s05) ; la fourrière
    # se livre en entrant dans la cour (s01, s08). Bouchard est dedans, au casse-croûte : sa fin passe au combiné.
    "objectifs": [
        {"type": "aller", "texte": "À LA NUIT, AU POSTE : L'AUTO DE ROY DORT DERRIÈRE",
         "lieu": "poste", "rayon": 8, "nuit": True},

        {"type": "monter", "texte": "VOLE L'AUTO-PATROUILLE DE ROY, DANS LA RUELLE",
         "vehicule": "police", "ou": "ruelle:poste:10"},

        {"type": "semer", "texte": "SES COLLÈGUES T'ONT VU : SÈME-LES", "etoiles": 2},

        {"type": "livrer", "texte": "AU LOT DE GILLES, SOUS UN FAUX NOM", "lieu": "fourriere", "rayon": 6},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "ruelle:poste:10", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Bouchard : bourru, et pour une fois inquiet — il le cache en donnant des
    # ordres. `[menacingly]` une fois, sur Roy.
    "dialogue": {
        "appel": [
            _l("bouchard", "Salut, le jeune, c'est Bouchard. L'inspectrice t'a parlé, je le sais. Viens au casse-croûte.",
               jeu="[gruffly] Salut, le jeune, c'est Bouchard. [knowingly] L'inspectrice t'a parlé, je le sais. Viens au casse-croûte.")
        ],
        "intro": [
            _l("bouchard", "Roy a mon carnet. Pas de char, pas d'enquête : elle marche pas vite, l'inspectrice.",
               jeu="[gruffly] Roy a mon carnet. [menacingly] Pas de char, pas d'enquête : elle marche pas vite, l'inspectrice."),
            _l("bouchard", "Son auto dort dans la ruelle du poste. Les clés sont au tableau, personne vole la police.",
               jeu="[matter-of-fact] Son auto dort dans la ruelle du poste. [deadpan] Les clés sont au tableau, personne vole la police."),
            _l("bouchard", "Laisse-la chez Gilles, au lot, sous un faux nom. Il pose pas de questions.",
               jeu="[knowingly] Laisse-la chez Gilles, au lot, sous un faux nom. [gruffly] Il pose pas de questions.")
        ],
        "pendant": [
            _p("bouchard", "Attends que le quart de nuit parte prendre son café. Vers onze heures.", 0,
               jeu="[matter-of-fact] Attends que le quart de nuit parte prendre son café. [deadpan] Vers onze heures."),
            _p("bouchard", "La blanche, avec le gyrophare cassé. C'est la sienne.", 1,
               jeu="[gruffly] La blanche, avec le gyrophare cassé. [knowingly] C'est la sienne."),
            _p("bouchard", "Mes gars te courent après. Ils savent pas que c'est pour moi. Perds-les.", 2,
               jeu="[nervously] Mes gars te courent après. Ils savent pas que c'est pour moi. [firmly] Perds-les."),
            _p("bouchard", "Gilles est au courant. Rentre dans la cour, pis va-t'en à pied.", 3,
               jeu="[matter-of-fact] Gilles est au courant. [gruffly] Rentre dans la cour, pis va-t'en à pied.")
        ],
        "fin": [
            _l("bouchard", "Propre. L'inspectrice va faire ses rondes en autobus pendant un mois.",
               jeu="[satisfied] Propre. [deadpan] L'inspectrice va faire ses rondes en autobus pendant un mois."),
            _l("bouchard", "T'es de mon bord, le jeune. Pour de bon, astheure. Ça se paie, pis ça s'oublie pas.",
               jeu="[gruffly] T'es de mon bord, le jeune. Pour de bon, astheure. [knowingly] Ça se paie, pis ça s'oublie pas.")
        ],
        "echec": [
            _l("bouchard", "J'ai rien vu, j'ai rien entendu. Pis toi non plus.",
               jeu="[nervously] J'ai rien vu, j'ai rien entendu. [gruffly] Pis toi non plus.")
        ]
    }
}
