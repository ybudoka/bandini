"""Le chapitre du garage de Rocco — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague D). La suite de
_La dette de Rocco_ : Sal veut le garage que l'oncle lui avait mis en garantie. d05 (Josée, l'avocat) et d06 (Gus,
les Ciseaux de nuit) — trois et quatre étapes, 78 s pour d05 au chronomètre de Martin — deviennent deux ACTES : les
papiers, puis la nuit où Sal perd patience. Ce qui fait durer : des Ciseaux de RENFORT aux deux bagarres (Sal veut
ses papiers ; Sal a vidé son salon), chacun annoncé par une réplique neuve.

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de d05
  restent ceux du chapitre ; sa fin se dit à l'ouverture de l'acte 2, au Brouillard, en personne, suivie de l'appel
  et de l'intro de Gus — au combiné : il est à son comptoir ; la fin de d06 reste la fin du chapitre ; chaque mission
  garde son échec (`_e`) ;
- la scène d'intro de d05 reste celle du chapitre ; celle de d06 tombe (Gus parle au combiné, à l'ouverture de l'acte).
- Le CHOIX qui suit (d07, le coffre de Sal avec Josée, ou d08, la dernière coupe, la dette payée) reste en missions :
  un acte ne sait pas fermer l'autre bord. Elles attendent d06 (le dernier acte), comme x01 ; i08 attend d05 (le
  premier) : un prérequis peut viser un acte.
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "garage_de_rocco",
    "titre": "Le garage de Rocco",
    "donneur": "josee",
    "prerequis": ["d04"],
    "remplace": ["d05", "d06"],
    "recompense": 250,
    "donne": {"message": "LE GARAGE TIENT DEBOUT — SAL A COMPRIS"},

    "objectifs": [
        # --- Acte 1 (d05, « L'avocat du Carré »).
        # L'avocat du Carré (M16, arc D, 30 sept. 2026). Sal a mis un huissier sur le garage (la garantie de d01) ; Josée
        # connaît le seul homme de la ville qui gagne contre un huissier : Me Desjardins, qui tient sa table au fond du
        # Brouillard. Il lui faut les papiers de Rocco — l'acte du garage, caché par l'oncle derrière la porte de la baie.
        # On les prend, deux Ciseaux de Sal veulent les mêmes, et on les porte au Brouillard. Le casier y perd deux pages
        # (Me Desjardins ne travaille jamais pour rien : il efface ce qu'il peut).
        {"type": "acte", "texte": "ACTE 1 — L'AVOCAT DU CARRÉ", "donneur": "josee"},  # 0
        {"type": "obtenir", "texte": "LES PAPIERS DE ROCCO SONT CACHÉS AU GARAGE", "objet": "papiers_de_rocco", "ou": "garage", "dessin": "dossier", "nom": "L'ACTE DU GARAGE"},  # 1
        # Ce qui fait durer : deux Ciseaux de plus, quand il n'en reste qu'un debout.
        {"type": "tuer", "texte": "DEUX CISEAUX DE SAL VEULENT LES PAPIERS", "groupe": "cravates", "n": 2, "loin": 10, "arme": "poing_americain",
         "renforts": {"vagues": 1, "n": 2}},  # 2
        {"type": "parler", "texte": "LES PAPIERS AU BROUILLARD, POUR ME DESJARDINS", "cible": "josee", "donne": {"casier": -2, "message": "LE GARAGE RESTE À TON NOM — ET DEUX PAGES DE MOINS", "prime": 150}},  # 3
        # --- Acte 2 (d06, « Sal perd patience »).
        # Sal perd patience (M16, arc D, 30 sept. 2026). L'huissier est reparti les mains vides (d05) : Sal envoie ses
        # Ciseaux, les vrais, casser le garage. Gus les a vus aiguiser leurs bagues au terminus ; l'armurerie est à deux coins
        # de rue, et il n'aime pas le bruit. La nuit au garage, une première vague, puis une deuxième avec leur contremaître
        # — et on va dire à Gus que c'est fini (il est dehors, à sa porte : `retourner`).
        {"type": "acte", "texte": "ACTE 2 — SAL PERD PATIENCE", "donneur": "gus"},  # 4
        {"type": "aller", "texte": "ATTENDS LES CISEAUX AU GARAGE, À LA NUIT", "lieu": "garage", "rayon": 6, "nuit": True},  # 5
        # Ce qui fait durer : deux vagues de deux, avant leur contremaître.
        {"type": "tuer", "texte": "LES CISEAUX DE SAL ARRIVENT : DÉFENDS LE GARAGE", "groupe": "cravates", "n": 3, "ou": "garage", "loin": 12, "arme": "poing_americain",
         "renforts": {"vagues": 2, "n": 2}},  # 6
        {"type": "tuer", "texte": "LEUR CONTREMAÎTRE, AVEC SES CISEAUX : COUCHE-LE", "groupe": "cravates", "n": 1, "chef": True, "arme": "couteau", "vie": 200, "loin": 10},  # 7
        {"type": "retourner", "texte": "DIS À GUS QUE C'EST FINI"},  # 8
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:garage", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # d05 — Le jeu de chaque réplique (`jeu=`) — Josée : le ton des affaires, sec, le « on » des chefs ; une seule
    # chaleur, rangée à la fin. Elle méprise les huissiers plus que les gangs.
    # d06 — Le jeu de chaque réplique (`jeu=`) — Gus : bourru, commercial jusque dans l'entraide ; il ne donne jamais un
    # ordre, il pose un prix. Il ne dit merci qu'une fois — et c'est lui qui paie.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. Sal a envoyé un huissier sur ton garage. Viens au bar, on a un avocat.", jeu="[coldly] Josée. Sal a envoyé un huissier sur ton garage. [matter-of-fact] Viens au bar, on a un avocat."),
        ],
        "intro": [
            _l("josee", "Un huissier, c'est un voleur avec un papier. Contre un papier, il faut un meilleur papier.", jeu="[matter-of-fact] Un huissier, c'est un voleur avec un papier. [confident] Contre un papier, il faut un meilleur papier."),
            _l("josee", "L'acte du garage. Rocco le cachait derrière la porte de la baie, dans une boîte à outils.", jeu="[knowingly] L'acte du garage. [quietly] Rocco le cachait derrière la porte de la baie, dans une boîte à outils."),
            _l("josee", "Apporte-le ici. Me Desjardins a sa table au fond. Il coûte cher, pis il perd jamais.", jeu="[matter-of-fact] Apporte-le ici. Me Desjardins a sa table au fond. [coldly] Il coûte cher, pis il perd jamais."),
        ],
        "fin": [
            _l("gus", "Pas une vitre cassée. Sal va comprendre que ton garage coûte plus cher que ta dette.", jeu="[satisfied] Pas une vitre cassée. [knowingly] Sal va comprendre que ton garage coûte plus cher que ta dette."),
            _l("gus", "Tiens. Pis merci. Dis-le à personne, j'ai une réputation.", jeu="[gruffly] Tiens. [quietly] Pis merci. [matter-of-fact] Dis-le à personne, j'ai une réputation."),
        ],
        "echec": [
            _e("josee", "Pas de papier, pas d'avocat. Le garage est à Sal tant qu'on prouve rien.", 0, jeu="[coldly] Pas de papier, pas d'avocat. [matter-of-fact] Le garage est à Sal tant qu'on prouve rien."),
            _e("gus", "Ils ont eu le garage, pis mes vitres. Je t'envoie la facture, jeune.", 4, jeu="[annoyed] Ils ont eu le garage, pis mes vitres. [gruffly] Je t'envoie la facture, jeune."),
        ],
        "pendant": [
            _p("josee", "Une boîte rouge, pleine de graisse. Rocco pensait que personne fouillerait là.", 1, jeu="[matter-of-fact] Une boîte rouge, pleine de graisse. [wryly] Rocco pensait que personne fouillerait là."),
            _p("josee", "Sal a eu la même idée. Ses Ciseaux arrivent, pis ils frappent avec des bagues.", 2, jeu="[coldly] Sal a eu la même idée. [menacingly] Ses Ciseaux arrivent, pis ils frappent avec des bagues."),
            # Neuf (2 oct. 2026) : les renforts.
            _p("josee", "Il en enverra d'autres. Sal tient à ses papiers plus qu'à sa clientèle.", 2, jeu="[coldly] Il en enverra d'autres. [wryly] Sal tient à ses papiers plus qu'à sa clientèle."),
            _p("josee", "Viens au bar. L'avocat a commandé un deuxième scotch sur ton compte.", 3, jeu="[calm] Viens au bar. [wryly] L'avocat a commandé un deuxième scotch sur ton compte."),
            # Acte 2 : la fin de d05, en personne ; puis l'appel et l'intro de d06.
            _p("josee", "Desjardins a lu, il a souri. L'huissier retourne chez Sal les mains vides.", 4, jeu="[satisfied] Desjardins a lu, il a souri. [coldly] L'huissier retourne chez Sal les mains vides."),
            _p("josee", "Pis il a déchiré deux pages de ton casier en passant. Il appelle ça un cadeau d'ouverture.", 4, jeu="[matter-of-fact] Pis il a déchiré deux pages de ton casier en passant. [warmly] Il appelle ça un cadeau d'ouverture."),
            _p("gus", "Gus, de l'armurerie. Les Ciseaux de Sal aiguisent leurs bagues au terminus. Pour ton garage, jeune.", 4, jeu="[gruffly] Gus, de l'armurerie. Les Ciseaux de Sal aiguisent leurs bagues au terminus. [matter-of-fact] Pour ton garage, jeune."),
            _p("gus", "Sal a perdu devant l'avocat. Un barbier qui perd, ça coupe autre chose que des cheveux.", 4, jeu="[gruffly] Sal a perdu devant l'avocat. [wryly] Un barbier qui perd, ça coupe autre chose que des cheveux."),
            _p("gus", "Ils viennent à la noirceur. Ton garage est à deux coins de mon magasin, pis j'aime pas les vitres cassées.", 4, jeu="[annoyed] Ils viennent à la noirceur. [matter-of-fact] Ton garage est à deux coins de mon magasin, pis j'aime pas les vitres cassées."),
            _p("gus", "Tiens-les dehors. Je paie pour la tranquillité, c'est rare, profites-en.", 4, jeu="[gruffly] Tiens-les dehors. [matter-of-fact] Je paie pour la tranquillité, c'est rare, profites-en."),
            _p("gus", "Attends la nuit. Ces gars-là travaillent pas de jour, ils ont des clients.", 5, jeu="[matter-of-fact] Attends la nuit. [wryly] Ces gars-là travaillent pas de jour, ils ont des clients."),
            _p("gus", "Les v'là. Trois, avec des bagues. Vise les mains, jeune.", 6, jeu="[gruffly] Les v'là. Trois, avec des bagues. [firmly] Vise les mains, jeune."),
            # Neuf (2 oct. 2026) : les renforts.
            _p("gus", "Y en a d'autres derrière. Sal a vidé son salon, sacrament.", 6, jeu="[annoyed] Y en a d'autres derrière. [gruffly] Sal a vidé son salon, sacrament."),
            _p("gus", "Le gros, c'est leur contremaître. Il se promène avec les vrais ciseaux de Sal.", 7, jeu="[concerned] Le gros, c'est leur contremaître. [matter-of-fact] Il se promène avec les vrais ciseaux de Sal."),
            _p("gus", "C'est tranquille. Viens me voir à ma porte, j'ai de quoi pour toi.", 8, jeu="[satisfied] C'est tranquille. [gruffly] Viens me voir à ma porte, j'ai de quoi pour toi."),
        ],
    },
}
