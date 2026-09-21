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
    "objectifs": [
        {"type": "aller", "lieu": "garage", "rayon": 4, "texte": "VA AU GARAGE — MARCO T'ATTEND"},
        {"type": "semer", "etoiles": 5, "texte": "SÈME LA POLICE — 5 ÉTOILES"},
        {"type": "ramasser", "cible": "fuyard", "vehicule": "taxi", "texte": "RATTRAPE LE TAXI DE MARCO"},
    ],
    # Marco t'attend sur le pas du garage, le téléphone sonne, et c'est un
    # guet-apens : la coupe montre la rue du garage, la caméra revient sur
    # toi. La fin laisse filer le taxi de Marco — le choix « le coucher ou
    # le laisser filer » est dans les répliques, pas dans un bouton.
    "scenes": {
        "intro": [
            {"type": "dire", "repliques": [1], "ensemble": True},
            {"type": "coupe", "vers": "porte:garage", "ferme": 20, "ouvre": 20, "tient": 150},
            {"type": "geste", "acteur": "donneur", "geste": "hausser", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "joueur", "ferme": 20, "ouvre": 20, "tient": 60},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:marco", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
    },
    # Le jeu de chaque réplique (`jeu=`) — Marco trahit : froid, amer, puis qui se rend a l'evidence.
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
            _l("marco", "Marco. T'es plus dur que les chiens qu'il a lâchés. Garde le taxi, il est à toi.",
               jeu="[impressed] Marco. T'es plus dur que les chiens qu'il a lâchés. Garde le taxi… il est à toi."),
            _l("marco", "Moi, je disparais. La ville est à toi, cousin.",
               jeu="[somber] Moi, je disparais… La ville est à toi, cousin."),
        ],
        "echec": [_l("marco", "Encore en vie? Marco. Tiens-toi prêt, on va régler ça bien comme il faut.",
                     jeu="[coldly] Encore en vie? Marco. Tiens-toi prêt… on va régler ça bien comme il faut.")],
        "pendant": [_p("marco", "Cours, cousin. Ceux-là ne font pas de quartier.", 1,
                       jeu="[worried] Cours, cousin… Ceux-là ne font pas de quartier.")],
    },
}
