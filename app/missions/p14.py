"""La mission p14 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "p14",
    "titre": "La taxe des Skateux",
    "donneur": "bonimenteur",
    "prerequis": ["p13"],
    "recompense": 350,
    "donne": {"message": "LA FOIRE, TRANQUILLE POUR DE BON"},

    # ⚠️ `proteger` (même patron que f09 : `cible`+`lieu`+`rayon` fait avancer
    # l'objectif à l'arrivée) puis `tuer` `ou: "donneur"` (les adversaires
    # arrivent près de LUI, pas de l'arche vide qu'on a quittée) — même patron
    # que f09, deuxième fois pour les deux types dans ce lot-ci.
    # ⚠️ Plus longue (Martin, 22 sept. 2026, « des missions plus longues ») : les Skateux
    # sont DÉJÀ à la foire quand il finit de parler (`tuer` en premier, `loin` : ils
    # naissent après l'intro et courent sur le joueur) ; puis l'escorte ; puis
    # l'embuscade devant le poste ; puis leur chef (`chef`, le patron de m5 : bâton,
    # 160 de vie) — sous les fenêtres de la police, qui ne sort pas.
    "objectifs": [
        {"type": "tuer", "texte": "CHASSE LES SKATEUX DE LA FOIRE",
         "groupe": "skateux", "n": 2, "ou": "donneur", "loin": 10},

        {"type": "proteger", "texte": "ESCORTE-LE JUSQU'AU POSTE",
         "cible": "bonimenteur", "lieu": "poste", "rayon": 5},

        {"type": "tuer", "texte": "REPOUSSE LES SKATEUX",
         "groupe": "skateux", "n": 2, "ou": "donneur", "loin": 10},

        {"type": "tuer", "texte": "LEUR CHEF S'EN MÊLE — COUCHE-LE",
         "groupe": "skateux", "n": 1, "chef": True},
    ],

    # Le jeu de chaque réplique (`jeu=`) — le Bonimenteur : sa faconde publique
    # tombe tout à fait, ici — un homme qui a peur et qui le dit, pour une fois.
    "dialogue": {
        "appel": [
            _l("bonimenteur", "C'est encore le Bonimenteur. Les Skateux veulent une « taxe » sur mes trois jeux, sinon ils cassent tout.",
               jeu="[worried] C'est encore le Bonimenteur. Les Skateux veulent une « taxe » sur mes trois jeux… sinon ils cassent tout.")
        ],
        "intro": [
            _l("bonimenteur", "Je dois aller voir la police, au poste, avant qu'ils reviennent avec le reste de la gang.",
               jeu="[nervously] Je dois aller voir la police, au poste, avant qu'ils reviennent avec le reste de la gang."),
            _l("bonimenteur", "Reste avec moi jusque-là. J'ai pas le cœur à me battre, moi, je fais juste vendre des tours de manège.",
               jeu="[worried] Reste avec moi jusque-là. [quietly] J'ai pas le cœur à me battre, moi… je fais juste vendre des tours de manège."),
            _l("bonimenteur", "Ah ben, les v'là déjà, pour leur taxe! Chasse-les de ma foire, jeune, je tiens la caisse.",
               jeu="[nervously] Ah ben, les v'là déjà, pour leur taxe! [firmly] Chasse-les de ma foire, jeune… [worried] je tiens la caisse.")
        ],
        "pendant": [
            _p("bonimenteur", "Pas trop vite, jeune! J'ai des souliers de vendeur, pas des souliers de coureur.", 1,
               jeu="[nervously] Pas trop vite, jeune! [wryly] J'ai des souliers de vendeur… pas des souliers de coureur."),
            _p("bonimenteur", "Les v'là! Occupe-toi d'eux, moi je reste collé sur toi!", 2,
               jeu="[worried] Les v'là! [nervously] Occupe-toi d'eux, moi je reste collé sur toi!"),
            _p("bonimenteur", "C'est leur chef, avec son bâton! Vas-y, moi je te tiens le manteau.", 3,
               jeu="[worried] C'est leur chef, avec son bâton! [nervously] Vas-y… moi je te tiens le manteau.")
        ],
        "fin": [
            _l("bonimenteur", "Au poste, enfin. La police va s'en mêler, astheure.",
               jeu="[relieved] Au poste, enfin. [satisfied] La police va s'en mêler, astheure."),
            _l("bonimenteur", "T'as sauvé ma foire, pis mes recettes avec. Je l'oublierai pas.",
               jeu="[warmly] T'as sauvé ma foire, pis mes recettes avec. [tenderly] Je l'oublierai pas."),
            _l("bonimenteur", "Pis leur chef, avec son bâton? Je vais le mettre en prix au tir aux canards.",
               jeu="[relieved] Pis leur chef, avec son bâton? [playfully] Je vais le mettre en prix au tir aux canards.")
        ],
        "echec": [
            _l("bonimenteur", "Ils m'ont eu... La foire au grand complet va payer, astheure.",
               jeu="[disappointed] Ils m'ont eu… [somber] La foire au grand complet va payer, astheure.")
        ]
    }
}
