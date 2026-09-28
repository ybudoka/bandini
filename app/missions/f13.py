"""La mission f13 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "f13",
    "titre": "Les volontaires",
    "donneur": "mado",
    "prerequis": ["f11"],
    "recompense": 250,
    "donne": {"message": "LE FAUBOURG A SES POMPIERS VOLONTAIRES"},
    "echec": ["mort", "arrete", "chrono"],

    # ⚠️ LA PREMIÈRE MISSION QUI ALLUME SON FEU (28 sept. 2026). `eteindre` attendait
    # qu'aucun feu de l'heure ne brûle — il passait dans la même image. Chaque objectif
    # `eteindre` allume maintenant LE SIEN sur la façade la plus proche de son `ou`
    # (`Incendies.allumerPourMission`, une spirale sans dé), et il résiste un tiers de
    # seconde au jet. Les trois portes sont déjà des lieux de mission (le kiosque, Rosa,
    # le terminus) : nommer une porte neuve élargirait son devant, et la ville glisserait.
    #
    # `remet` : Mado te met l'extincteur de sa cuisine dans les mains, plein — sans lui,
    # rien ne garantissait qu'on en ait un, ni qu'il reste de quoi éteindre trois feux.
    # Les Cravates qu'on a chassées en f11 se vengent : celui qui craque les allumettes
    # file en berline après le troisième (`ramasser` + `fuyard`, le patron de f03).
    "objectifs": [
        {"type": "eteindre", "texte": "ÉTEINS LE FEU DU KIOSQUE",
         "ou": "porte:kiosque", "remet": "extincteur", "chrono_s": 90},

        {"type": "eteindre", "texte": "LA BOUTIQUE DE ROSA BRÛLE",
         "ou": "porte:vetements", "chrono_s": 90},

        {"type": "eteindre", "texte": "LE TERMINUS AUSSI, VITE",
         "ou": "porte:terminus", "chrono_s": 90},

        {"type": "ramasser", "texte": "RATTRAPE LE PYROMANE ET SON BIDON",
         "cible": "fuyard", "vehicule": "auto"},

        {"type": "retourner", "texte": "RAPPORTE LE BIDON À MADO"},
    ],

    # L'intro : la caméra va voir le kiosque qui brûle PENDANT qu'elle le dit (le feu est posé
    # avant la scène), revient, et Mado te tend l'extincteur sur « tiens ». La voix retient
    # chaque plan (`dire` sans `ensemble`) : rien ne se coupe, quelle que soit sa durée.
    "scenes": {
        "intro": [
            {"type": "camera", "vers": "porte:kiosque", "duree": 50, "courbe": "freine", "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "camera", "vers": "joueur", "duree": 40, "courbe": "freine"},
            {"type": "geste", "acteur": "donneur", "geste": "donner", "vers": "joueur", "duree": 60, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Mado, les volontaires : l'inquiétude à l'appel
    # (le Faubourg brûle, et il n'a pas de caserne), la fermeté d'une femme qui distribue
    # les tâches comme des assiettes, puis la colère froide quand elle comprend qui a mis
    # le feu — et la chaleur à la fin, qui n'est pas du soulagement : de la fierté.
    "dialogue": {
        "appel": [
            _l("mado", "C'est Mado! Ça sent la fumée partout dans le Faubourg, pis la caserne est à l'autre bout de la baie.",
               jeu="[worried] C'est Mado! Ça sent la fumée partout dans le Faubourg… [firmly] pis la caserne est à l'autre bout de la baie.")
        ],
        "intro": [
            _l("mado", "Le kiosque de Madame Thibodeau pogne en feu. Tiens, l'extincteur de ma cuisine, il est plein.",
               jeu="[worried] Le kiosque de Madame Thibodeau pogne en feu. [firmly] Tiens, l'extincteur de ma cuisine… il est plein."),
            _l("mado", "Vise le pied des flammes, pas la fumée. Pis garde-en pour les autres, j'ai l'impression que c'est pas fini.",
               jeu="[firmly] Vise le pied des flammes, pas la fumée. [worried] Pis garde-en pour les autres… j'ai l'impression que c'est pas fini.")
        ],
        "pendant": [
            _p("mado", "Cours, mon grand! Une minute et demie pis le toit y passe.", 0,
               jeu="[worried] Cours, mon grand! [firmly] Une minute et demie… pis le toit y passe."),
            _p("mado", "Ça brûle chez Rosa, astheure! Quelqu'un fait le tour du quartier avec des allumettes.", 1,
               jeu="[surprised] Ça brûle chez Rosa, astheure! [angry] Quelqu'un fait le tour du quartier avec des allumettes."),
            _p("mado", "Le terminus! Fern a des passagers qui attendent dedans, dépêche!", 2,
               jeu="[worried] Le terminus! [firmly] Fern a des passagers qui attendent dedans… dépêche!"),
            _p("mado", "Je le vois, c'est une Cravate avec un bidon! Il part en char, lâche-le pas.", 3,
               jeu="[angry] Je le vois, c'est une Cravate avec un bidon! [firmly] Il part en char… lâche-le pas."),
            _p("mado", "Apporte-moi son bidon. Je vais l'accrocher au mur, à côté du menu.", 4,
               jeu="[coldly] Apporte-moi son bidon. [wryly] Je vais l'accrocher au mur… à côté du menu.")
        ],
        "fin": [
            _l("mado", "Trois feux pis un pyromane, avant que le café soit prêt. Le Faubourg a ses pompiers, astheure.",
               jeu="[impressed] Trois feux pis un pyromane… avant que le café soit prêt. [warmly] Le Faubourg a ses pompiers, astheure."),
            _l("mado", "Garde l'extincteur, mon grand. Quand ça sentira la fumée, c'est toi qu'on va appeler.",
               jeu="[warmly] Garde l'extincteur, mon grand. [tenderly] Quand ça sentira la fumée… c'est toi qu'on va appeler.")
        ],
        "echec": [
            _l("mado", "Ouain... Le feu va plus vite que nous autres. Reviens, on va recommencer.",
               jeu="[disappointed] Ouain… Le feu va plus vite que nous autres. [firmly] Reviens, on va recommencer.")
        ]
    }
}
