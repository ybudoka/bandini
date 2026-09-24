"""La mission m97 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m97", "titre": "Marco te vend", "donneur": "marco", "prerequis": ["m5"],
    "recompense": 150, "phase": 1, "echec": ["mort", "arrete"],
    # ⚠️ `exige` : la condition de « dans quel état », distincte du prérequis
    # « après quoi ». Pas encore lue par le navigateur — elle vaut au juge
    # dès aujourd'hui et au téléphone le jour où il triera.
    "exige": {"liberes": 3},
    "donne": {"message": "LE TAXI DE MARCO EST GARÉ À LA PLANQUE", "vehicule": "taxi"},
    # « Des missions plus longues » (22 sept. 2026) : « Tiens, les voilà » — les chiens de Bouchard
    # ARRIVENT (`loin`) dès la fin de l'intro, avant la police ; les cinq étoiles semées, Ovila appelle
    # du phare : le taxi a passé le pont, à l'AUTRE BOUT de la ville ; on le rattrape, puis on retourne
    # régler ça avec Marco — la fin se dit devant lui, plus au combiné.
    # ⚠️ L'ancien premier objectif (« VA AU GARAGE — MARCO T'ATTEND ») est parti : on y est, on vient de
    # lui parler, et il s'accomplissait dans l'image où l'intro finit — une image plus tôt ou plus tard
    # selon qu'on regarde la scène ou qu'on la passe, et les chiens naissaient (deux dés chacun) à un
    # autre moment du hasard (`test_une_scene_de_mission_ne_tire_aucun_de[m97]`). Premiers, ils naissent
    # à la fin de l'intro, par `faireArriver`, des deux façons.
    "objectifs": [
        {"type": "tuer", "groupe": "cravates", "n": 4, "ou": "donneur", "loin": 12,
         "texte": "COUCHE LES CHIENS DE BOUCHARD"},
        {"type": "semer", "etoiles": 5, "texte": "SÈME LA POLICE — 5 ÉTOILES"},
        {"type": "aller", "lieu": "phare", "rayon": 5, "texte": "VA AU PHARE — LE TAXI A PASSÉ LE PONT"},
        {"type": "ramasser", "cible": "fuyard", "vehicule": "taxi", "texte": "RATTRAPE LE TAXI DE MARCO"},
        {"type": "retourner", "texte": "RETOURNE RÉGLER ÇA AVEC MARCO"},
    ],
    # Marco t'attend sur le pas du garage, le téléphone sonne, et c'est un
    # guet-apens : la coupe montre la rue du garage, la caméra revient sur
    # toi. La fin se joue DEVANT lui (`retourner`) : il hausse les épaules, il
    # croise les bras, il s'en va — le choix « le coucher ou le laisser filer »
    # est dans les répliques, pas dans un bouton. Chaque geste en `ensemble`, PUIS
    # sa `dire` : c'est la voix qui retient la scène, aucune n'est coupée.
    "scenes": {
        "intro": [
            {"type": "dire", "repliques": [1], "ensemble": True},
            {"type": "coupe", "vers": "porte:garage", "ferme": 20, "ouvre": 20, "tient": 150},
            {"type": "geste", "acteur": "donneur", "geste": "hausser", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "joueur", "ferme": 20, "ouvre": 20, "tient": 60},
        ],
        "fin": [
            {"type": "geste", "acteur": "donneur", "geste": "hausser", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [1, 2]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
    },
    # Le jeu de chaque réplique (`jeu=`) — Marco trahit : froid, amer, puis qui se rend a l'evidence ;
    # Ovila, qui a tout vu du phare, vouvoie et chuchote.
    "dialogue": {
        "appel": [_l("marco", "Marco. Viens au garage, cousin. On a à se parler, toi pis moi.",
                     jeu="[coldly] Marco. Viens au garage, cousin. On a à se parler… toi pis moi.")],
        "intro": [
            _l("marco", "Bouchard m'a montré ton dossier. T'as bâti un nom sur mon dos.",
               jeu="[bitterly] Bouchard m'a montré ton dossier. T'as bâti un nom… sur mon dos."),
            _l("marco", "Pis il paie pour te voir tomber. Tiens, les voilà.",
               jeu="[menacingly] Pis il paie pour te voir tomber… Tiens, les voilà."),
        ],
        "fin": [
            _l("marco", "Tu me couches pas? Rocco, lui, m'aurait couché.",
               jeu="[surprised] Tu me couches pas? [bitterly] Rocco, lui… m'aurait couché."),
            _l("marco", "T'es plus dur que les chiens qu'il a lâchés. Garde le taxi, il est à toi.",
               jeu="[impressed] T'es plus dur que les chiens qu'il a lâchés. Garde le taxi… il est à toi."),
            _l("marco", "Moi, je disparais. La ville est à toi, cousin.",
               jeu="[somber] Moi, je disparais… La ville est à toi, cousin."),
        ],
        "echec": [_l("marco", "Tiens-toi prêt. On va régler ça bien comme il faut.",
                     jeu="[coldly] Tiens-toi prêt… On va régler ça bien comme il faut.")],
        "pendant": [
            _p("marco", "Cours, cousin. Ceux-là ne font pas de quartier.", 1,
               jeu="[worried] Cours, cousin… Ceux-là ne font pas de quartier."),
            _p("marco", "Rien de personnel, cousin. Bouchard paye comptant.", 0,
               jeu="[coldly] Rien de personnel, cousin. [bitterly] Bouchard paye comptant."),
            _p("ovila", "Pardonnez-moi. Ici Ovila, au phare : le taxi de votre cousin vient de passer le pont.", 2,
               jeu="[softly] Pardonnez-moi. Ici Ovila, au phare : [mysteriously] le taxi de votre cousin vient de passer le pont."),
            _p("ovila", "Il vous a vu. Il repart vers la ville, tous feux éteints.", 3,
               jeu="[calm] Il vous a vu. [quietly] Il repart vers la ville… tous feux éteints."),
            _p("marco", "T'as repris mon taxi. Viens au garage, qu'on finisse ça entre nous.", 4,
               jeu="[bitterly] T'as repris mon taxi. [coldly] Viens au garage… qu'on finisse ça entre nous."),
        ],
    },
}
