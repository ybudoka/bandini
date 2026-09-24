"""La mission f03 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "f03",
    "titre": "La robe de Rosa",
    "donneur": "rosa",
    "prerequis": ["f01"],
    "recompense": 250,
    "donne": {"rabais": {"vetements": 0.75}, "message": "BOUTIQUE ROSA, MOINS CHER POUR TOI"},

    # ⚠️ Le patron déjà prouvé (m2/m50/m97) : `ramasser` + `cible: "fuyard"` fait
    # naître un fuyard en voiture ; une fois rattrapé, la caisse tombe et se
    # ramasse. Rosa se tient DEHORS (`porte:vetements`) : `retourner` fonctionne.
    #
    # « Des missions plus longues » (Martin, 22 sept. 2026) : ses chums arrivent de loin
    # pour reprendre la caisse (`tuer`, des Chevreuils à mains nues, comme e01), puis la
    # robe de mariée part à l'Hôtel Bandini — au bout sud-ouest de la ville, la
    # boutique est au nord-est — avant de rapporter le reste à Rosa.
    "objectifs": [
        {"type": "ramasser", "texte": "RATTRAPE LE CHEVREUIL EN BERLINE",
         "cible": "fuyard", "vehicule": "auto"},

        {"type": "tuer", "texte": "SES CHUMS VEULENT LA CAISSE",
         "groupe": "chevreuils", "n": 2, "ou": "donneur", "loin": 10, "arme": "", "vie": 60},

        {"type": "aller", "texte": "PORTE LA ROBE DE MARIÉE À L'HÔTEL",
         "lieu": "hotel", "rayon": 4},

        {"type": "retourner", "texte": "RAPPORTE LA CAISSE À ROSA"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Rosa : chic, jamais surprise de rien, l'ex
    # de Rocco qui en a trop vu pour s'énerver ; un sourire en coin, pas un cri.
    "dialogue": {
        "appel": [
            _l("rosa", "Rosa, de la boutique. Un Chevreuil vient de partir avec ma livraison, dans une belle berline. Viens me voir.",
               jeu="[calm] Rosa, de la boutique. Un Chevreuil vient de partir avec ma livraison… dans une belle berline. [matter-of-fact] Viens me voir.")
        ],
        "intro": [
            _l("rosa", "Une caisse de robes cousues sur mesure. Il file vers le nord, il connaît pas mon quartier.",
               jeu="[wryly] Une caisse de robes cousues sur mesure. [knowingly] Il file vers le nord… il connaît pas mon quartier."),
            _l("rosa", "Rattrape-le, pis ramène-moi ça propre. J'ai pas le temps de recoudre trois jours d'ouvrage.",
               jeu="[firmly] Rattrape-le, pis ramène-moi ça propre. [annoyed] J'ai pas le temps de recoudre trois jours d'ouvrage.")
        ],
        "pendant": [
            _p("rosa", "Il roule vite pour un gars qui connaît pas la ville. Reste sur lui.", 0,
               jeu="[amused] Il roule vite pour un gars qui connaît pas la ville. [firmly] Reste sur lui."),
            _p("rosa", "Ses petits amis veulent la caisse. Des Chevreuils en jogging, ça se couche vite.", 1,
               jeu="[wryly] Ses petits amis veulent la caisse. [amused] Des Chevreuils en jogging, ça se couche vite."),
            _p("rosa", "Tant qu'à y être, la robe de mariée va à l'hôtel. La mariée attend, le marié, moins.", 2,
               jeu="[knowingly] Tant qu'à y être, la robe de mariée va à l'hôtel. [wryly] La mariée attend… le marié, moins."),
            _p("rosa", "La mariée a appelé, elle pleure de joie. Rapporte-moi le reste de la caisse.", 3,
               jeu="[amused] La mariée a appelé, elle pleure de joie. [calm] Rapporte-moi le reste de la caisse.")
        ],
        "fin": [
            _l("rosa", "Impeccable. Pas une couture de défaite.",
               jeu="[satisfied] Impeccable. [amused] Pas une couture de défaite."),
            _l("rosa", "Tiens, un rabais pour toi. Rocco payait toujours plein prix, lui. T'es différent.",
               jeu="[knowingly] Tiens, un rabais pour toi. [softly] Rocco payait toujours plein prix, lui. T'es différent.")
        ],
        "echec": [
            _l("rosa", "Trois jours d'ouvrage, envolés... Reviens quand t'auras la tête à ça.",
               jeu="[disappointed] Trois jours d'ouvrage, envolés… [wryly] Reviens quand t'auras la tête à ça.")
        ]
    }
}
