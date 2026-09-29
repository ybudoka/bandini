"""La mission e06 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "e06",
    "titre": "Le maire ne dort pas chez lui",
    "donneur": "diane",
    # ⚠️ Après e01 et pas m6 : Diane n'est devant le dépanneur qu'après les drifts (`arrive_apres`).
    "prerequis": ["e01"],
    "recompense": 300,
    "donne": {"message": "LE MAIRE DORT À L'HÔTEL, ET DIANE LE SAIT"},

    # La berline du maire sort de la villa (au bout de la rue du dépanneur) et va dormir à l'Hôtel Bandini, aux
    # Quais — toute la ville à traverser. `suivre` (le patron de f06) : trop près, il te voit dans son rétroviseur ;
    # trop loin, tu le perds. Elle attend que tu sois au volant pour partir. Puis on revient raconter.
    "objectifs": [
        {"type": "suivre", "texte": "FILE LA BERLINE DU MAIRE, SANS QU'IL TE VOIE",
         "vehicule": "luxe", "loin": 12, "proche": 3, "lieu": "hotel"},

        {"type": "retourner", "texte": "RACONTE TOUT À DIANE, AU DÉPANNEUR"},
    ],

    # L'intro montre la villa (le passage du bloc, au bout de la rue) pendant qu'elle parle.
    "scenes": {
        "intro": [
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "bloc:villa", "duree": 60, "ensemble": True},
            {"type": "camera", "vers": "bloc:villa", "duree": 45, "courbe": "freine", "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
            {"type": "camera", "vers": "joueur", "duree": 40, "courbe": "freine"},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Diane : la politicienne qui sourit en disant non. Elle vouvoie, elle
    # pèse chaque mot, et ne dit jamais ce qu'elle veut — elle dit ce que « les citoyens » veulent. Un seul
    # `[satisfied]`, à la fin : c'est là qu'on voit qu'elle joue une partie.
    "dialogue": {
        "appel": [
            _l("diane", "Diane Larivière, conseillère municipale. J'ai un service à vous demander, discrètement.",
               jeu="[confident] Diane Larivière, conseillère municipale. [quietly] J'ai un service à vous demander… discrètement.")
        ],
        "intro": [
            _l("diane", "Le maire Tanguay dit aux citoyens qu'il dort à la villa. Sa voiture dit autre chose.",
               jeu="[knowingly] Le maire Tanguay dit aux citoyens qu'il dort à la villa. [wryly] Sa voiture dit autre chose."),
            _l("diane", "Ce soir, sa berline va sortir. Suivez-la jusqu'où elle s'arrête.",
               jeu="[calm] Ce soir, sa berline va sortir. [firmly] Suivez-la jusqu'où elle s'arrête."),
            _l("diane", "Pas trop près. Un maire qui se sait suivi dort chez lui pendant un mois.",
               jeu="[serious] Pas trop près. [wryly] Un maire qui se sait suivi… dort chez lui pendant un mois.")
        ],
        "pendant": [
            _p("diane", "Elle sort. Laissez-lui de l'avance, il regarde toujours dans son rétroviseur.", 0,
               jeu="[quietly] Elle sort. [calm] Laissez-lui de l'avance… il regarde toujours dans son rétroviseur."),
            _p("diane", "L'Hôtel Bandini. Évidemment. Revenez me voir, je veux chaque détail.", 1,
               jeu="[amused] L'Hôtel Bandini. Évidemment. [firmly] Revenez me voir… je veux chaque détail.")
        ],
        "fin": [
            _l("diane", "Trois nuits par semaine à l'hôtel, aux frais de la ville. Les citoyens vont adorer.",
               jeu="[wryly] Trois nuits par semaine à l'hôtel, aux frais de la ville. [satisfied] Les citoyens vont adorer."),
            _l("diane", "Gardez ça pour vous. Une information se vend mieux quand personne d'autre ne l'a.",
               jeu="[knowingly] Gardez ça pour vous. [calm] Une information se vend mieux… quand personne d'autre ne l'a.")
        ],
        "echec": [
            _l("diane", "Il vous a vu. Le maire va dormir chez lui un bon moment, maintenant.",
               jeu="[disappointed] Il vous a vu. [coldly] Le maire va dormir chez lui un bon moment, maintenant.")
        ]
    }
}
