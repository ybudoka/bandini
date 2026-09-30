"""La mission i02 — voir app/missions/__init__.py pour le moteur.

La cloche de Sœur Jeanne (M16, arc I, 30 sept. 2026). La cloche de la chapelle de l'île a été volée l'hiver passé —
elle a fini chez Ti-Loup, au lot, à côté de son compacteur. Sœur Jeanne n'a pas de char et pas de colère : elle a
deux cents piastres de la quête. On va voir Ti-Loup, on paie, on charge la cloche dans une chaloupe, on traverse, et
on la rend à la chapelle.

⚠️ La fiche offrait de « la racheter ou la reprendre » : un objectif facultatif n'existe pas — on paie.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "i02",
    "titre": "La cloche de Sœur Jeanne",
    "donneur": "jeanne",
    "prerequis": ["i01", "s02"],
    "recompense": 150,
    "donne": {"message": "LA CLOCHE SONNE À L'ÎLE-AUX-CORNEILLES"},

    # ⚠️ Ti-Loup se tient au lot (`dans_la_cour`) : sa poignée de main se dit. `payer` prend l'argent de la poche.
    # La chaloupe attend à l'amarrage le plus près du lot, et se livre sous la chapelle ; Sœur Jeanne est dehors, sur
    # son parvis : `retourner`.
    "objectifs": [
        {"type": "parler", "texte": "LA CLOCHE EST CHEZ TI-LOUP, AU LOT : VA LE VOIR", "cible": "tiloup"},

        {"type": "payer", "texte": "RACHÈTE-LA : DEUX CENTS, COMPTANT", "montant": 200},

        {"type": "monter", "texte": "LA CLOCHE EST DANS UNE CHALOUPE, AU BORD DE L'EAU",
         "vehicule": "bateau", "ou": "amarrage:fourriere"},

        {"type": "livrer", "texte": "TRAVERSE JUSQU'À LA CHAPELLE DE L'ÎLE", "lieu": "amarrage:chapelle", "rayon": 6},

        {"type": "retourner", "texte": "RENDS SA CLOCHE À SŒUR JEANNE"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Sœur Jeanne : « mon enfant », le bon Dieu qui a de l'humour ; elle ne
    # demande rien, elle raconte, et on finit par faire. Ti-Loup : des chiffres, « comptant ».
    "dialogue": {
        "appel": [
            _l("jeanne", "C'est Sœur Jeanne, du téléphone du quai de l'île. Le bon Dieu a retrouvé ma cloche, mon enfant.",
               jeu="[warmly] C'est Sœur Jeanne, du téléphone du quai de l'île. [tenderly] Le bon Dieu a retrouvé ma cloche, mon enfant.")
        ],
        "intro": [
            _l("jeanne", "On me l'a volée l'hiver passé. Elle a fini chez un ferrailleur, à côté d'un compacteur.",
               jeu="[gravely] On me l'a volée l'hiver passé. [wryly] Elle a fini chez un ferrailleur, à côté d'un compacteur."),
            _l("jeanne", "J'ai deux cents piastres de la quête. Le bon Dieu dit que c'est un prix honnête.",
               jeu="[tenderly] J'ai deux cents piastres de la quête. [wryly] Le bon Dieu dit que c'est un prix honnête."),
            _l("jeanne", "Ramène-la par l'eau, mon enfant. Une cloche, ça n'aime pas les autobus.",
               jeu="[warmly] Ramène-la par l'eau, mon enfant. [wryly] Une cloche, ça n'aime pas les autobus.")
        ],
        "pendant": [
            _p("jeanne", "Ti-Loup a bon cœur sous la graisse. Parle-lui doucement.", 0,
               jeu="[tenderly] Ti-Loup a bon cœur sous la graisse. [warmly] Parle-lui doucement."),
            _p("jeanne", "Deux cents, pas un sou de plus. Le bon Dieu compte aussi.", 1,
               jeu="[wryly] Deux cents, pas un sou de plus. [tenderly] Le bon Dieu compte aussi."),
            _p("jeanne", "Il l'a mise dans une vieille chaloupe, au bord de l'eau. Elle est lourde, va doucement.", 2,
               jeu="[warmly] Il l'a mise dans une vieille chaloupe, au bord de l'eau. [gravely] Elle est lourde, va doucement."),
            _p("jeanne", "Accoste sous la chapelle. Les corneilles vont te faire une haie d'honneur.", 3,
               jeu="[tenderly] Accoste sous la chapelle. [wryly] Les corneilles vont te faire une haie d'honneur.")
        ],
        "accueil": [
            _a("tiloup", "La cloche de la sœur? Deux cents, comptant. Je la compacte pas, c'est le bon Dieu.", 0,
               jeu="[gruffly] La cloche de la sœur? Deux cents, comptant. [deadpan] Je la compacte pas, c'est le bon Dieu.")
        ],
        "fin": [
            _l("jeanne", "Elle est revenue. Ce soir, elle sonne les vêpres, pis toute la baie va l'entendre.",
               jeu="[tenderly] Elle est revenue. [warmly] Ce soir, elle sonne les vêpres, pis toute la baie va l'entendre."),
            _l("jeanne", "Prends ça, mon enfant. Pis si un jour tu pars en traversier, écoute-la sonner.",
               jeu="[warmly] Prends ça, mon enfant. [tenderly] Pis si un jour tu pars en traversier, écoute-la sonner.")
        ],
        "echec": [
            _l("jeanne", "La cloche est au fond de la baie. Le bon Dieu sonnera autrement.",
               jeu="[gravely] La cloche est au fond de la baie. [tenderly] Le bon Dieu sonnera autrement.")
        ]
    }
}
