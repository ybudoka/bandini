"""La mission i05 — voir app/missions/__init__.py pour le moteur.

L'usine à poisson (M16, arc I, 30 sept. 2026). Derrière le hangar de l'île, la vieille conserverie brûle : des
matelots de Sven y dormaient en squatteurs, et un fanal renversé a fait le reste. Sœur Jeanne est sur le parvis, le
seul extincteur de l'île dans les bras. On éteint la façade avant que le feu prenne le hangar, on chasse les
matelots, et on rend l'extincteur à la sœur.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "i05",
    "titre": "L'usine à poisson",
    "donneur": "jeanne",
    "prerequis": ["i02"],
    "recompense": 200,
    "donne": {"message": "L'ÎLE N'A PLUS DE SQUATTEURS — ET SA CONSERVERIE TIENT DEBOUT"},

    # ⚠️ `eteindre` allume SON feu sur la façade la plus proche de son `ou` (`Incendies.allumerPourMission`, sans dé),
    # une porte déjà lieu de mission (le hangar de Léo) : la ville ne glisse pas. Les matelots (`pieton: matelot`,
    # q13) attendent au hangar, pas à la chapelle où la fin se joue (`retourner`, Sœur Jeanne est dehors).
    "objectifs": [
        {"type": "eteindre", "texte": "LA CONSERVERIE BRÛLE, DERRIÈRE LE HANGAR : ÉTEINS-LA",
         "ou": "porte:hangar_ile", "remet": "extincteur", "chrono_s": 90},

        {"type": "tuer", "texte": "TROIS MATELOTS DE SVEN Y DORMAIENT : CHASSE-LES",
         "groupe": "morues", "pieton": "matelot", "n": 3, "ou": "porte:hangar_ile"},

        {"type": "retourner", "texte": "RENDS SON EXTINCTEUR À SŒUR JEANNE"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "porte:hangar_ile", "duree": 70,
             "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    "dialogue": {
        "appel": [
            _l("jeanne", "Sœur Jeanne, du quai de l'île! La vieille conserverie brûle, mon enfant, viens vite.",
               jeu="[worried] Sœur Jeanne, du quai de l'île! [firmly] La vieille conserverie brûle, mon enfant, viens vite.")
        ],
        "intro": [
            _l("jeanne", "Des matelots dormaient dedans, avec un fanal. Le bon Dieu leur a donné une leçon, trop fort.",
               jeu="[worried] Des matelots dormaient dedans, avec un fanal. [wryly] Le bon Dieu leur a donné une leçon, trop fort."),
            _l("jeanne", "Voici l'extincteur de la chapelle. Le seul de l'île, alors vise bien.",
               jeu="[firmly] Voici l'extincteur de la chapelle. [tenderly] Le seul de l'île, alors vise bien."),
            _l("jeanne", "Si le feu prend le hangar, c'est toute la pointe de l'île qui part.",
               jeu="[gravely] Si le feu prend le hangar, c'est toute la pointe de l'île qui part.")
        ],
        "pendant": [
            _p("jeanne", "Le bas des flammes, mon enfant! Le bas!", 0,
               jeu="[worried] Le bas des flammes, mon enfant! [firmly] Le bas!"),
            _p("jeanne", "Ils sont encore là, les trois, à se chicaner pour le fanal. Qu'ils s'en aillent.", 1,
               jeu="[gravely] Ils sont encore là, les trois, à se chicaner pour le fanal. [firmly] Qu'ils s'en aillent."),
            _p("jeanne", "C'est fini. Viens sur le parvis, j'ai du thé pis des biscuits.", 2,
               jeu="[relieved] C'est fini. [warmly] Viens sur le parvis, j'ai du thé pis des biscuits.")
        ],
        "fin": [
            _l("jeanne", "La conserverie tient debout, pis le hangar de Léo aussi. Le bon Dieu est content.",
               jeu="[relieved] La conserverie tient debout, pis le hangar de Léo aussi. [tenderly] Le bon Dieu est content."),
            _l("jeanne", "Prends ça, mon enfant. Pis garde l'extincteur, t'en auras plus besoin que moi.",
               jeu="[warmly] Prends ça, mon enfant. [wryly] Pis garde l'extincteur, t'en auras plus besoin que moi.")
        ],
        "echec": [
            _l("jeanne", "Le hangar a pris. On prie, pis on rebâtira.",
               jeu="[gravely] Le hangar a pris. [tenderly] On prie, pis on rebâtira.")
        ]
    }
}
