"""Le chapitre de Sœur Jeanne — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague I). L'île, Sœur Jeanne : i02 (sa cloche rachetée chez Ti-Loup et ramenée par l'eau) et i05 (la conserverie qui brûle,
les matelots de Sven) — cinq et trois étapes, deux ACTES (6 à 7 minutes).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : l'appel de i05 perd « Sœur Jeanne, du quai de l'île! » — la même voix,
  coupée au silence ;
- la scène d'intro de i02 reste celle du chapitre.
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "soeur_jeanne",
    "titre": "Sœur Jeanne",
    "donneur": "jeanne",
    "prerequis": ["i01", "s02"],
    "remplace": ["i02", "i05"],
    "recompense": 200,
    "donne": {"message": "L'ÎLE N'A PLUS DE SQUATTEURS — ET SA CONSERVERIE TIENT DEBOUT"},

    "objectifs": [
        # --- Acte 1 (i02, « La cloche de Sœur Jeanne »).
        # La cloche de Sœur Jeanne (M16, arc I, 30 sept. 2026). La cloche de la chapelle de l'île a été volée l'hiver passé —
        # elle a fini chez Ti-Loup, au lot, à côté de son compacteur. Sœur Jeanne n'a pas de char et pas de colère : elle a
        # deux cents piastres de la quête. On va voir Ti-Loup, on paie, on charge la cloche dans une chaloupe, on traverse, et
        # on la rend à la chapelle.
        # ⚠️ La fiche offrait de « la racheter ou la reprendre » : un objectif facultatif n'existe pas — on paie.
        {"type": "acte", "texte": "ACTE 1 — LA CLOCHE DE SŒUR JEANNE", "donneur": "jeanne"},  # 0
        {"type": "parler", "texte": "LA CLOCHE EST CHEZ TI-LOUP, AU LOT : VA LE VOIR", "cible": "tiloup"},  # 1
        {"type": "payer", "texte": "RACHÈTE-LA : DEUX CENTS, COMPTANT", "montant": 200},  # 2
        {"type": "monter", "texte": "LA CLOCHE EST DANS UNE CHALOUPE, AU BORD DE L'EAU", "vehicule": "bateau", "ou": "amarrage:fourriere"},  # 3
        {"type": "livrer", "texte": "TRAVERSE JUSQU'À LA CHAPELLE DE L'ÎLE", "lieu": "amarrage:chapelle", "rayon": 6},  # 4
        {"type": "retourner", "texte": "RENDS SA CLOCHE À SŒUR JEANNE", "donne": {"message": "LA CLOCHE SONNE À L'ÎLE-AUX-CORNEILLES", "prime": 150}},  # 5
        # --- Acte 2 (i05, « L'usine à poisson »).
        # L'usine à poisson (M16, arc I, 30 sept. 2026). Derrière le hangar de l'île, la vieille conserverie brûle : des
        # matelots de Sven y dormaient en squatteurs, et un fanal renversé a fait le reste. Sœur Jeanne est sur le parvis, le
        # seul extincteur de l'île dans les bras. On éteint la façade avant que le feu prenne le hangar, on chasse les
        # matelots, et on rend l'extincteur à la sœur.
        {"type": "acte", "texte": "ACTE 2 — L'USINE À POISSON", "donneur": "jeanne"},  # 6
        {"type": "eteindre", "texte": "LA CONSERVERIE BRÛLE, DERRIÈRE LE HANGAR : ÉTEINS-LA", "ou": "porte:hangar_ile", "remet": "extincteur", "chrono_s": 90},  # 7
        {"type": "tuer", "texte": "TROIS MATELOTS DE SVEN Y DORMAIENT : CHASSE-LES", "groupe": "morues", "pieton": "matelot", "n": 3, "ou": "porte:hangar_ile"},  # 8
        {"type": "retourner", "texte": "RENDS SON EXTINCTEUR À SŒUR JEANNE"},  # 9
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

    # i02 — Le jeu de chaque réplique (`jeu=`) — Sœur Jeanne : « mon enfant », le bon Dieu qui a de l'humour ; elle ne
    # demande rien, elle raconte, et on finit par faire. Ti-Loup : des chiffres, « comptant ».
    "dialogue": {
        "appel": [
            _l("jeanne", "C'est Sœur Jeanne, du téléphone du quai de l'île. Le bon Dieu a retrouvé ma cloche, mon enfant.", jeu="[warmly] C'est Sœur Jeanne, du téléphone du quai de l'île. [tenderly] Le bon Dieu a retrouvé ma cloche, mon enfant."),
        ],
        "intro": [
            _l("jeanne", "On me l'a volée l'hiver passé. Elle a fini chez un ferrailleur, à côté d'un compacteur.", jeu="[gravely] On me l'a volée l'hiver passé. [wryly] Elle a fini chez un ferrailleur, à côté d'un compacteur."),
            _l("jeanne", "J'ai deux cents piastres de la quête. Le bon Dieu dit que c'est un prix honnête.", jeu="[tenderly] J'ai deux cents piastres de la quête. [wryly] Le bon Dieu dit que c'est un prix honnête."),
            _l("jeanne", "Ramène-la par l'eau, mon enfant. Une cloche, ça n'aime pas les autobus.", jeu="[warmly] Ramène-la par l'eau, mon enfant. [wryly] Une cloche, ça n'aime pas les autobus."),
        ],
        "fin": [
            _l("jeanne", "La conserverie tient debout, pis le hangar de Léo aussi. Le bon Dieu est content.", jeu="[relieved] La conserverie tient debout, pis le hangar de Léo aussi. [tenderly] Le bon Dieu est content."),
            _l("jeanne", "Prends ça, mon enfant. Pis garde l'extincteur, t'en auras plus besoin que moi.", jeu="[warmly] Prends ça, mon enfant. [wryly] Pis garde l'extincteur, t'en auras plus besoin que moi."),
        ],
        "echec": [
            _e("jeanne", "La cloche est au fond de la baie. Le bon Dieu sonnera autrement.", 0, jeu="[gravely] La cloche est au fond de la baie. [tenderly] Le bon Dieu sonnera autrement."),
            _e("jeanne", "Le hangar a pris. On prie, pis on rebâtira.", 6, jeu="[gravely] Le hangar a pris. [tenderly] On prie, pis on rebâtira."),
        ],
        "pendant": [
            _p("jeanne", "Ti-Loup a bon cœur sous la graisse. Parle-lui doucement.", 1, jeu="[tenderly] Ti-Loup a bon cœur sous la graisse. [warmly] Parle-lui doucement."),
            _p("jeanne", "Deux cents, pas un sou de plus. Le bon Dieu compte aussi.", 2, jeu="[wryly] Deux cents, pas un sou de plus. [tenderly] Le bon Dieu compte aussi."),
            _p("jeanne", "Il l'a mise dans une vieille chaloupe, au bord de l'eau. Elle est lourde, va doucement.", 3, jeu="[warmly] Il l'a mise dans une vieille chaloupe, au bord de l'eau. [gravely] Elle est lourde, va doucement."),
            _p("jeanne", "Accoste sous la chapelle. Les corneilles vont te faire une haie d'honneur.", 4, jeu="[tenderly] Accoste sous la chapelle. [wryly] Les corneilles vont te faire une haie d'honneur."),
            # Acte 2 : la fin de i02, en personne ; puis l'appel et l'intro de i05.
            _p("jeanne", "Elle est revenue. Ce soir, elle sonne les vêpres, pis toute la baie va l'entendre.", 6, jeu="[tenderly] Elle est revenue. [warmly] Ce soir, elle sonne les vêpres, pis toute la baie va l'entendre."),
            _p("jeanne", "Prends ça, mon enfant. Pis si un jour tu pars en traversier, écoute-la sonner.", 6, jeu="[warmly] Prends ça, mon enfant. [tenderly] Pis si un jour tu pars en traversier, écoute-la sonner."),
            # ⚠️ Coupée (2 oct. 2026) : « Sœur Jeanne, du quai de l'île! » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("jeanne", "La vieille conserverie brûle, mon enfant, viens vite.", 6, jeu="[firmly] La vieille conserverie brûle, mon enfant, viens vite."),
            _p("jeanne", "Des matelots dormaient dedans, avec un fanal. Le bon Dieu leur a donné une leçon, trop fort.", 6, jeu="[worried] Des matelots dormaient dedans, avec un fanal. [wryly] Le bon Dieu leur a donné une leçon, trop fort."),
            _p("jeanne", "Voici l'extincteur de la chapelle. Le seul de l'île, alors vise bien.", 6, jeu="[firmly] Voici l'extincteur de la chapelle. [tenderly] Le seul de l'île, alors vise bien."),
            _p("jeanne", "Si le feu prend le hangar, c'est toute la pointe de l'île qui part.", 6, jeu="[gravely] Si le feu prend le hangar, c'est toute la pointe de l'île qui part."),
            _p("jeanne", "Le bas des flammes, mon enfant! Le bas!", 7, jeu="[worried] Le bas des flammes, mon enfant! [firmly] Le bas!"),
            _p("jeanne", "Ils sont encore là, les trois, à se chicaner pour le fanal. Qu'ils s'en aillent.", 8, jeu="[gravely] Ils sont encore là, les trois, à se chicaner pour le fanal. [firmly] Qu'ils s'en aillent."),
            _p("jeanne", "C'est fini. Viens sur le parvis, j'ai du thé pis des biscuits.", 9, jeu="[relieved] C'est fini. [warmly] Viens sur le parvis, j'ai du thé pis des biscuits."),
        ],
        "accueil": [
            _a("tiloup", "La cloche de la sœur? Deux cents, comptant. Je la compacte pas, c'est le bon Dieu.", 1, jeu="[gruffly] La cloche de la sœur? Deux cents, comptant. [deadpan] Je la compacte pas, c'est le bon Dieu."),
        ],
    },
}
