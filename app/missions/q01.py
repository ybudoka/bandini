"""La mission q01 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "q01",
    "titre": "La cantine de Lulu",
    "donneur": "lulu",
    "prerequis": ["q02"],
    "recompense": 150,
    # ⚠️ `rabais.cantine` : le comptoir de la cantine le lit (`Missions.rabais`, le slug de
    # la pièce) — `test_rabais_js.py` refuse une clé que personne ne lit.
    "donne": {"rabais": {"cantine": 0.75}, "message": "LA CANTINE, −25 % POUR TOI"},

    # Les Morues sont les gars de Josée : Lulu est la seule, aux Quais, qui puisse leur
    # dire non (docs/personnages/lulu.md). Trois qui mangent sans payer, sur la galerie ;
    # le quatrième saute dans une auto avec la caisse du midi (`ramasser`, le fuyard) ;
    # on rapporte la caisse chez elle — elle est DEDANS (`point:lulu`), pas de
    # `retourner` : un `aller` sur son lieu, au rayon de 6 du donneur.
    "objectifs": [
        {"type": "tuer", "texte": "TROIS MORUES MANGENT SANS PAYER — METS-LES DEHORS",
         "groupe": "morues", "n": 3, "ou": "porte:cantine", "arme": "", "vie": 60},

        {"type": "ramasser", "texte": "LE QUATRIÈME EST PARTI AVEC LA CAISSE DU MIDI",
         "cible": "fuyard", "vehicule": "auto"},

        {"type": "aller", "texte": "RAPPORTE LA CAISSE À LA CANTINE",
         "lieu": "cantine", "rayon": 6},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Lulu : fâchée pour de rire, puis pour de vrai
    # quand la caisse part ; elle materne en se moquant, et finit en nourrissant.
    "dialogue": {
        "appel": [
            _l("lulu", "Allô, mon grand, c'est Lulu! J'ai trois Morues qui mangent chez nous depuis lundi, pis pas une cenne.",
               jeu="[annoyed] Allô, mon grand, c'est Lulu! [teasing] J'ai trois Morues qui mangent chez nous depuis lundi… pis pas une cenne.")
        ],
        "intro": [
            _l("lulu", "C'est les gars de ma sœur. Josée dit qu'une Morue, ça paie pas dans la famille.",
               jeu="[wryly] C'est les gars de ma sœur. [annoyed] Josée dit qu'une Morue… ça paie pas dans la famille."),
            _l("lulu", "Moi, je dis que c'est mes assiettes. Sors-les de ma galerie, pis casse pas mes chaises.",
               jeu="[firmly] Moi, je dis que c'est mes assiettes. [teasing] Sors-les de ma galerie… pis casse pas mes chaises."),
            _l("lulu", "Pis dis rien à Josée. Ce qu'elle sait pas, ça la fâche pas.",
               jeu="[playfully] Pis dis rien à Josée. [knowingly] Ce qu'elle sait pas… ça la fâche pas.")
        ],
        "pendant": [
            _p("lulu", "Ils sont sur la galerie, avec mon dessert! Vas-y, mon grand.", 0,
               jeu="[excited] Ils sont sur la galerie, avec mon dessert! [warmly] Vas-y, mon grand."),
            _p("lulu", "Le quatrième est parti avec la caisse du midi! Rattrape-le avant qu'il la mange.", 1,
               jeu="[worried] Le quatrième est parti avec la caisse du midi! [teasing] Rattrape-le… avant qu'il la mange."),
            _p("lulu", "Rapporte-moi ça. Je te garde une assiette chaude.", 2,
               jeu="[warmly] Rapporte-moi ça. [cheerful] Je te garde une assiette chaude.")
        ],
        "fin": [
            _l("lulu", "Toute la caisse, pis même le pourboire! T'es mieux qu'un chien de garde, toi.",
               jeu="[relieved] Toute la caisse, pis même le pourboire! [amused] T'es mieux qu'un chien de garde, toi."),
            _l("lulu", "Pour toi, c'est moins cher à partir d'astheure. Mange, t'as encore l'air d'un fantôme.",
               jeu="[warmly] Pour toi, c'est moins cher à partir d'astheure. [teasing] Mange… t'as encore l'air d'un fantôme.")
        ],
        "echec": [
            _l("lulu", "Ma caisse est partie, pis mes chaises avec. Reviens quand t'auras mangé.",
               jeu="[disappointed] Ma caisse est partie… pis mes chaises avec. [warmly] Reviens quand t'auras mangé.")
        ]
    }
}
