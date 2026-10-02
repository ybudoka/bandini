"""Le chapitre des commandes de Prévost — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague S). La Shop (vague S), après la paix : Réjean Prévost, rembauché, a deux commandes — s07 (le camion de pièces au quai
avant le cargo) et s13 (le prototype chez les Skateux, pas une égratignure) — deux et trois étapes, deux ACTES (5 à
6 minutes, une auto des Chevreuils au pare-chocs à l'acte 2, comme dans s13).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : l'appel de s13 perd « Réjean Prévost. » — la même voix, coupée au
  silence ;
- la scène d'intro de s07 reste celle du chapitre ; celle de s13 tombe.
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "commandes_de_prevost",
    "titre": "Les commandes de Prévost",
    "donneur": "prevost",
    "prerequis": ["s11"],
    "remplace": ["s07", "s13"],
    "recompense": 400,
    "donne": {"message": "PRÉVOST A SON PROTOTYPE"},

    "objectifs": [
        # --- Acte 1 (s07, « Le camion de Prévost »).
        # Le camion de Prévost (M16, arc S, 30 sept. 2026). La Shop est libre (s11) et Prévost rembauche ; il a signé un
        # contrat avec un armateur de Rimouski, et un camion de pièces doit être au quai des Quais avant que le cargo largue
        # les amarres. Ses chauffeurs sont tous au syndicat. Le neveu travaille pour les deux bords — c'est le propos.
        {"type": "acte", "texte": "ACTE 1 — LE CAMION DE PRÉVOST", "donneur": "prevost"},  # 0
        {"type": "monter", "texte": "LE CAMION DE PIÈCES, DERRIÈRE L'USINE", "vehicule": "camion", "ou": "ruelle:usine:10"},  # 1
        {"type": "livrer", "texte": "AU QUAI AVANT LE DÉPART DU CARGO : DEUX MINUTES ET DEMIE", "lieu": "cantine", "rayon": 6, "chrono_s": 150, "donne": {"message": "LE CARGO DE RIMOUSKI EST PARTI À L'HEURE", "prime": 350}},  # 2
        # --- Acte 2 (s13, « Le prototype »).
        # Le prototype (M16, arc S, 1er oct. 2026). Un coupé sport que l'usine Prévost a monté pour une foire de Détroit a
        # disparu de la cour ; il dort au stationnement des Skateux, à La Pointe. Prévost le veut sans une égratignure et sans
        # police dans sa cour : on le reprend (`monter`), on saute la rampe des Skateux pour sortir du stationnement
        # (`sauter`, 30 px de vol), et on le laisse chez Gilles, à la fourrière, où ses hommes le prendront (`livrer`,
        # `sans_degats` : la prime) — un char des Chevreuils te colle tout le long (`poursuite`).
        # ⚠️ Écarts à la fiche : livré à la fourrière, pas à l'usine (sa cour ferme la nuit, elle n'est jamais un lieu de
        # mission) ; le pont n'est pas bloqué — les Chevreuils te suivent.
        {"type": "acte", "texte": "ACTE 2 — LE PROTOTYPE", "donneur": "prevost"},  # 3
        {"type": "monter", "texte": "LE PROTOTYPE DORT CHEZ LES SKATEUX", "vehicule": "sport", "ou": "zone:skateux", "prete": "prevost"},  # 4
        {"type": "sauter", "texte": "SORS DU STATIONNEMENT PAR LA RAMPE — 30 PX", "vol_px": 30},  # 5
        {"type": "livrer", "texte": "À LA FOURRIÈRE, CHEZ GILLES — PAS UNE ÉGRATIGNURE", "lieu": "fourriere", "rayon": 6, "sans_degats": True, "poursuite": {"groupe": "chevreuils", "chars": 1}},  # 6
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "ruelle:usine:10", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # s07 — Le jeu de chaque réplique (`jeu=`) — Prévost : le patron qui a perdu et fait comme s'il avait gagné ; des phrases
    # de conseil d'administration, un sourire en coin sur « les deux bords ».
    # s13 — Le jeu de chaque réplique (`jeu=`) — Prévost : des phrases de conseil d'administration ; froid, sûr de lui,
    # et pour une fois il a besoin de quelqu'un — il ne le dira pas.
    "dialogue": {
        "appel": [
            _l("prevost", "Réjean Prévost. J'ai un contrat qui part par bateau, pis mes chauffeurs sont en assemblée syndicale.", jeu="[matter-of-fact] Réjean Prévost. [coldly] J'ai un contrat qui part par bateau, pis mes chauffeurs sont en assemblée syndicale."),
        ],
        "intro": [
            _l("prevost", "Un armateur de Rimouski. Des pièces de treuil, six mois de travail pour La Shop.", jeu="[matter-of-fact] Un armateur de Rimouski. [smugly] Des pièces de treuil, six mois de travail pour La Shop."),
            _l("prevost", "Le camion est chargé, derrière. Le cargo largue à la marée : deux minutes et demie.", jeu="[coldly] Le camion est chargé, derrière. [matter-of-fact] Le cargo largue à la marée : deux minutes et demie."),
            _l("prevost", "Vous avez travaillé contre moi, vous travaillez pour moi. C'est ce qu'on appelle un marché.", jeu="[smugly] Vous avez travaillé contre moi, vous travaillez pour moi. [coldly] C'est ce qu'on appelle un marché."),
        ],
        "fin": [
            _l("prevost", "Gilles m'a appelé. Le prototype est intact. Votre facture sera honorée.", jeu="[matter-of-fact] Gilles m'a appelé. Le prototype est intact. [coldly] Votre facture sera honorée."),
            _l("prevost", "Détroit ne saura jamais qu'il a dormi chez des enfants.", jeu="[smugly] Détroit ne saura jamais… [coldly] qu'il a dormi chez des enfants."),
        ],
        "echec": [
            _e("prevost", "Le cargo est parti sans mes pièces. Rimouski ne rappellera pas.", 0, jeu="[coldly] Le cargo est parti sans mes pièces. [matter-of-fact] Rimouski ne rappellera pas."),
            _e("prevost", "Le prototype est perdu. Je passerai ça aux pertes, avec vous dedans.", 3, jeu="[coldly] Le prototype est perdu. [matter-of-fact] Je passerai ça aux pertes… avec vous dedans."),
        ],
        "pendant": [
            _p("prevost", "Les clés sont dessus. Mes camions, je les paie, je ne les verrouille pas.", 1, jeu="[matter-of-fact] Les clés sont dessus. [smugly] Mes camions, je les paie, je ne les verrouille pas."),
            _p("prevost", "Le quai des Quais, devant la cantine. Le capitaine attend, et il déteste attendre.", 2, jeu="[coldly] Le quai des Quais, devant la cantine. [matter-of-fact] Le capitaine attend, et il déteste attendre."),
            # Acte 2 : la fin de s07, en personne ; puis l'appel et l'intro de s13.
            _p("prevost", "Le cargo est parti à l'heure. Six mois de paie pour La Shop, grâce à un voleur de chars.", 3, jeu="[satisfied] Le cargo est parti à l'heure. [smugly] Six mois de paie pour La Shop, grâce à un voleur de chars."),
            _p("prevost", "Votre enveloppe. Ne la montrez pas à Raymonde, elle croirait que je suis devenu gentil.", 3, jeu="[matter-of-fact] Votre enveloppe. [wryly] Ne la montrez pas à Raymonde, elle croirait que je suis devenu gentil."),
            # ⚠️ Coupée (2 oct. 2026) : « Réjean Prévost. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("prevost", "Un bien de l'usine a quitté la cour sans facture. Je veux le récupérer.", 3, jeu="[matter-of-fact] Un bien de l'usine a quitté la cour sans facture. Je veux le récupérer."),
            _p("prevost", "Un prototype. Monté ici, pour la foire de Détroit. Il dort chez les Skateux, à La Pointe.", 3, jeu="[matter-of-fact] Un prototype. Monté ici, pour la foire de Détroit. [coldly] Il dort chez les Skateux, à La Pointe."),
            _p("prevost", "Leur stationnement n'a qu'une sortie qui vaille : la rampe. Je ne veux pas savoir comment.", 3, jeu="[matter-of-fact] Leur stationnement n'a qu'une sortie qui vaille : la rampe. [smugly] Je ne veux pas savoir comment."),
            _p("prevost", "Laissez-le chez Gilles, à la fourrière. Pas de police dans ma cour. Pas une égratignure.", 3, jeu="[coldly] Laissez-le chez Gilles, à la fourrière. [firmly] Pas de police dans ma cour. Pas une égratignure."),
            _p("prevost", "Le coupé gris, au fond du stationnement. Les clés sont dessus, ils ne savent pas conduire.", 4, jeu="[matter-of-fact] Le coupé gris, au fond du stationnement. [smugly] Les clés sont dessus, ils ne savent pas conduire."),
            _p("prevost", "La rampe. Trente pieds de vol, c'est dans ses spécifications.", 5, jeu="[coldly] La rampe. [matter-of-fact] Trente pieds de vol, c'est dans ses spécifications."),
            _p("prevost", "Les Chevreuils vous suivent. Un concurrent, sans doute. Ne leur laissez rien.", 6, jeu="[coldly] Les Chevreuils vous suivent. [wryly] Un concurrent, sans doute. [firmly] Ne leur laissez rien."),
        ],
    },
}
