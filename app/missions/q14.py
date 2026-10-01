"""La mission q14 — voir app/missions/__init__.py pour le moteur.

La liste du Norvégien (M16, arc Q, 1er oct. 2026). Sven a gagné les Quais (q10) ; son cargo repart vers Bergen avec
une cale de chars d'ici, et l'ardoise de la passerelle porte deux modèles. Une berline derrière l'hôtel (`monter`),
livrée au quai sans une bosse (`livrer`, `sans_degats`) ; Sven la charge, on revient le soir (`attendre`, douze
heures de jeu) ; puis un coupé sport derrière le casse-croûte de Mado, au quai lui aussi ; et Sven paie à sa
passerelle (`retourner`).

⚠️ Écarts à la fiche : deux modèles, pas quatre, et une demi-journée entre les deux plutôt qu'un par jour ; et
seulement si on a choisi Sven (q10) : la variante de Ti-Loup (après q11) est q15.

Sa récompense, c'est « la liste du quai » (l'activité, `economie.LISTE_DU_QUAI["ouvre"]`, Martin, 1er oct. 2026) :
quatre modèles qui changent tous les quatre jours, un par jour à la jetée de Sven — fermée avant elle.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "q14",
    "titre": "La liste du Norvégien",
    "donneur": "sven",
    "prerequis": ["q10", "v03"],
    "recompense": 250,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"message": "SVEN T'OUVRE L'ARDOISE DU QUAI"},

    "objectifs": [
        {"type": "monter", "texte": "LE PREMIER MODÈLE : UNE BERLINE, DERRIÈRE L'HÔTEL", "vehicule": "luxe",
         "ou": "ruelle:hotel:12"},

        {"type": "livrer", "texte": "AU QUAI, DERRIÈRE LA CANTINE — SANS UNE BOSSE", "lieu": "cantine", "rayon": 6,
         "sans_degats": True},

        {"type": "attendre", "texte": "SVEN LA CHARGE — LE DEUXIÈME, CE SOIR", "heures": 12},

        {"type": "monter", "texte": "LE DEUXIÈME : UN COUPÉ SPORT, DERRIÈRE CHEZ MADO", "vehicule": "sport",
         "ou": "ruelle:casse_croute:12"},

        {"type": "livrer", "texte": "AU QUAI, LUI AUSSI — SANS UNE BOSSE", "lieu": "cantine", "rayon": 6,
         "sans_degats": True},

        {"type": "retourner", "texte": "SVEN PAIE À SA PASSERELLE"},
    ],

    # Intention (intro) : Sven à sa passerelle, l'ardoise à la main, qui commande des chars comme on commande du bois ;
    # la caméra va voir la ruelle de l'hôtel (la berline y dort), puis revient pour la règle — une bosse, il la refuse.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:hotel", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Sven : précis, froid, économe ; un français correct, jamais québécois ;
    # `[satisfied]` à la fin d'un travail propre, jamais chaleureux.
    "dialogue": {
        "appel": [
            _l("sven", "Sven. Le cargo repart pour Bergen, et la cale est vide. J'ai une liste.",
               jeu="[calm] Sven. [matter-of-fact] Le cargo repart pour Bergen, et la cale est vide. J'ai une liste.")
        ],
        "intro": [
            _l("sven", "Deux modèles sur l'ardoise. Une berline allemande, puis un coupé sport.",
               jeu="[matter-of-fact] Deux modèles sur l'ardoise. [calm] Une berline allemande, puis un coupé sport."),
            _l("sven", "La berline dort derrière l'hôtel. Le coupé, ce soir, derrière le casse-croûte.",
               jeu="[calm] La berline dort derrière l'hôtel. [matter-of-fact] Le coupé, ce soir, derrière le casse-croûte."),
            _l("sven", "À Bergen, on paie pour du neuf. Une bosse, et je la laisse sur le quai.",
               jeu="[firmly] À Bergen, on paie pour du neuf. [coldly] Une bosse, et je la laisse sur le quai.")
        ],
        "pendant": [
            _p("sven", "La berline grise. Le portier de l'hôtel regarde ailleurs, il est payé pour.", 0,
               jeu="[matter-of-fact] La berline grise. [calm] Le portier de l'hôtel regarde ailleurs, il est payé pour."),
            _p("sven", "Au quai, derrière la cantine. Doucement dans les nids-de-poule.", 1,
               jeu="[calm] Au quai, derrière la cantine. [firmly] Doucement dans les nids-de-poule."),
            _p("sven", "Bien. Je la charge. Le deuxième sera prêt ce soir, pas avant.", 2,
               jeu="[satisfied] Bien. [matter-of-fact] Je la charge. Le deuxième sera prêt ce soir, pas avant."),
            _p("sven", "Le coupé rouge, derrière le casse-croûte. Son propriétaire mange lentement.", 3,
               jeu="[matter-of-fact] Le coupé rouge, derrière le casse-croûte. [calm] Son propriétaire mange lentement."),
            _p("sven", "Au quai, lui aussi. La marée n'attend pas.", 4,
               jeu="[firmly] Au quai, lui aussi. [calm] La marée n'attend pas."),
            _p("sven", "La cale est pleine. Viens chercher ton dû, à la passerelle.", 5,
               jeu="[satisfied] La cale est pleine. [matter-of-fact] Viens chercher ton dû, à la passerelle.")
        ],
        "fin": [
            _l("sven", "Deux modèles, sans une marque. Tu travailles proprement.",
               jeu="[satisfied] Deux modèles, sans une marque. [calm] Tu travailles proprement."),
            _l("sven", "Le cargo part à la marée. La prochaine liste, je te l'enverrai.",
               jeu="[matter-of-fact] Le cargo part à la marée. [calm] La prochaine liste, je te l'enverrai.")
        ],
        "echec": [
            _l("sven", "Tu n'étais pas prêt. Le cargo partira à moitié vide.",
               jeu="[coldly] Tu n'étais pas prêt. [matter-of-fact] Le cargo partira à moitié vide.")
        ]
    }
}
