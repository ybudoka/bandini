"""La mission f06 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "f06",
    "titre": "Deuxième service",
    "donneur": "bouchard",
    # ⚠️ Après f01 (le Faubourg respire à nouveau, le sergent a le temps de régler ses comptes).
    "prerequis": ["f01"],
    "recompense": 300,
    "donne": {"message": "LE STOOL SE TAIT"},

    # ⚠️ `suivre` (M16) : le stool (`poserLeSuivi`) naît à bonne distance de la porte du
    # casse-croûte, attend que tu sois au volant, puis roule comme le trafic jusqu'au
    # `lieu` — c'est SON arrivée qui fait avancer l'objectif. `proche` (trop près, il te
    # repère) et `loin` (trop loin, on le perd) se tolèrent un moment. ⚠️ Plus le fuyard
    # de m50 : il naissait devant la porte, sous `proche`, et l'échec tombait à la sortie
    # (Martin, 22 sept. 2026).
    # ⚠️ `par` : le détour d'un stool nerveux, avant le poste — le garage, puis le
    # terminus. Sans lui, le poste est à deux coins de rue et la filature durait 15 s ;
    # Martin : « je veux que ce soit plus long ». Des lieux déjà de mission : la ville
    # ne bouge pas.
    # `payer` (M16) : `Missions.payer` déduit l'argent, sans UI de plus.
    # ⚠️ Pas de `retourner` après : Bouchard se tient DEDANS (`point:sergent`) — un
    # `retourner` ne se règle qu'avec un donneur en chair et en os dans la ville
    # (`Histoire.donneur`), et un `point:` n'en pose jamais. Le dernier objectif (`semer`)
    # ferme la mission tout seul (comme m51 : Bouchard se dit au combiné).
    "objectifs": [
        {"type": "suivre", "texte": "SUIS-LE SANS TE FAIRE REPÉRER",
         "vehicule": "auto", "loin": 10, "proche": 3, "par": ["garage", "terminus"], "lieu": "poste"},

        {"type": "payer", "texte": "PAIE-LUI 200 $ POUR SON SILENCE", "montant": 200},

        # ⚠️ Des missions plus longues (Martin, 22 sept. 2026) — APRÈS la filature, pas un
        # second détour : un stool garde toujours une copie. La sienne dort dans son autre char,
        # derrière l'hôtel Bandini, à l'autre bout de la ville (`detruire` le pose là). Le
        # boum attire la police : on sème les gars de Bouchard. `hotel` est déjà un lieu de
        # mission : la ville ne bouge pas.
        {"type": "detruire", "texte": "SA COPIE DORT DANS SON AUTRE CHAR : DÉMOLIS-LE",
         "vehicule": "auto", "ou": "ruelle:hotel"},

        {"type": "semer", "texte": "LE BOUM A RÉVEILLÉ LE QUARTIER : SÈME LA POLICE", "etoiles": 2},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Bouchard : bourru, jamais un mot de trop, une
    # satisfaction sèche à la fin — il n'a pas besoin de sourire pour qu'on sache que
    # l'affaire est réglée.
    "dialogue": {
        "appel": [
            _l("bouchard", "Salut, le jeune, c'est Bouchard. Un témoin de l'affaire des Cravates parle trop, au casse-croûte.",
               jeu="[gruffly] Salut, le jeune, c'est Bouchard. [gravely] Un témoin de l'affaire des Cravates parle trop… au casse-croûte.")
        ],
        "intro": [
            _l("bouchard", "Suis-le jusqu'au poste sans qu'il te voie. Pas trop près, pas trop loin.",
               jeu="[firmly] Suis-le jusqu'au poste sans qu'il te voie. [gravely] Pas trop près, pas trop loin."),
            _l("bouchard", "Une fois là, tu lui paies son silence. Deux cents piastres, pas une de plus.",
               jeu="[matter-of-fact] Une fois là, tu lui paies son silence. [firmly] Deux cents piastres… pas une de plus.")
        ],
        "pendant": [
            _p("bouchard", "Reste loin de son pare-choc. Un stool nerveux, ça regarde dans son rétroviseur.", 0,
               jeu="[gravely] Reste loin de son pare-choc. [wryly] Un stool nerveux… ça regarde dans son rétroviseur."),
            _p("bouchard", "Un stool, ça garde toujours une copie. La sienne dort dans son autre char, derrière l'hôtel.", 2,
               jeu="[knowingly] Un stool, ça garde toujours une copie. [gruffly] La sienne dort dans son autre char… derrière l'hôtel."),
            _p("bouchard", "Mes gars s'en viennent. Je peux rien pour toi, le jeune, sème-les.", 3,
               jeu="[nervously] Mes gars s'en viennent. [matter-of-fact] Je peux rien pour toi, le jeune… sème-les.")
        ],
        "fin": [
            _l("bouchard", "Il se taira. Deux cents piastres achètent beaucoup de silence, par icitte.",
               jeu="[satisfied] Il se taira. [wryly] Deux cents piastres achètent beaucoup de silence, par icitte."),
            _l("bouchard", "T'as fait ça proprement. C'est tout ce que je demande.",
               jeu="[gruffly] T'as fait ça proprement. [matter-of-fact] C'est tout ce que je demande."),
            _l("bouchard", "Pis la copie, j'en ai jamais entendu parler.",
               jeu="[deadpan] Pis la copie… j'en ai jamais entendu parler.")
        ],
        "echec": [
            _l("bouchard", "Il t'a vu, hein? Astheure il va jaser à tout le Faubourg.",
               jeu="[annoyed] Il t'a vu, hein? [gravely] Astheure il va jaser à tout le Faubourg.")
        ]
    },

    # Intention (intro) : celle du défaut (dedans) — une coupe sur `porte:poste`, il croise les bras, il
    # finit. ⚠️ SAUF que la coupe part `ensemble` avec la première réplique au lieu de la retenir (forme
    # de q02/m51) : la voix dure 6,3 s, la coupe du défaut 3,2 s, et la seconde réplique la coupait.
    # Le `dire` retient la scène jusqu'au bout de sa voix.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "porte:poste", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
    },
}
