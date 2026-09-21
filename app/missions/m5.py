"""La mission m5 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m5", "titre": "La Chef des Quais", "donneur": "josee", "prerequis": ["m4"],
    "recompense": 800, "phase": 1, "echec": ["mort", "arrete"],
    "donne": {"propriete": "bar", "faubourg_libere": True, "manchette": "cravates_chassees",
              "message": "LE BAR EST À TOI"},
    "objectifs": [
        {"type": "tuer", "groupe": "cravates", "n": 6, "ou": "zone:cravates", "coins": 3, "texte": "VIDE LES TROIS COINS DES CRAVATES"},
        {"type": "tuer", "groupe": "cravates", "n": 1, "chef": True, "texte": "COUCHE LE CHEF"},
        {"type": "semer", "etoiles": 3, "texte": "SÈME LA POLICE"},
        {"type": "aller", "lieu": "planque", "rayon": 4, "texte": "RENTRE À LA PLANQUE"},
    ],
    # Josée parle au Brouillard : la caméra sort voir le coin des Cravates (un
    # lieu — dedans, rien ne se pose avant la sortie). À la fin, on est à la
    # planque : la caméra va voir le Brouillard, qui est à toi.
    # ⚠️ Son intro est celle du défaut (Josée parle au Brouillard, la caméra sort
    # voir le coin des Cravates par une coupe : dedans, rien ne se pose avant la
    # sortie) — effacée. Sa fin, elle, tient VINGT IMAGES DE PLUS que le défaut :
    # on reste sur le Brouillard, qui est à toi. Une scène écrite gagne toujours
    # sur celle qu'on lui bâtirait, et c'est à ça qu'elle sert.
    "scenes": {
        "fin": [
            {"type": "coupe", "vers": "chez:josee", "ferme": 20, "ouvre": 20, "tient": 180, "ensemble": True},
            {"type": "dire"},
        ],
    },
    # Le jeu de chaque réplique (`jeu=`) — Josee : froide, et elle pese chaque ordre.
    "dialogue": {
        "appel": [_l("josee", "Tu me connais pas encore. Josée, on m'appelle la Chef. Viens au Brouillard, j'ai à te parler.",
                     jeu="[coldly] Tu me connais pas encore. Josée, on m'appelle la Chef. Viens au Brouillard… j'ai à te parler.")],
        "intro": [
            _l("josee", "Les Cravates tiennent trois coins de rue. Je les veux vides avant la nuit.",
               jeu="[coldly] Les Cravates tiennent trois coins de rue. Je les veux vides… avant la nuit."),
            _l("josee", "Leur chef va sortir quand ses gars vont tomber. Lui, je le veux couché.",
               jeu="[menacingly] Leur chef va sortir quand ses gars vont tomber. Lui, je le veux couché."),
            _l("josee", "Un témoin va appeler la police, c'est sûr. Sème-les, pis rentre à ta planque.",
               jeu="[matter-of-fact] Un témoin va appeler la police, c'est sûr. Sème-les, pis rentre à ta planque."),
        ],
        "fin": [
            _l("josee", "Josée. Le Faubourg respire. Le bar est à toi, pis toute la ville va le lire demain matin.",
               jeu="[satisfied] Josée. Le Faubourg respire. Le bar est à toi… pis toute la ville va le lire demain matin."),
            _l("josee", "On va se reparler. Y a plus grand que le Faubourg.",
               jeu="[mysteriously] On va se reparler. Y a plus grand… que le Faubourg."),
        ],
        "echec": [_l("josee", "Josée. Les Cravates sont encore là. Reviens quand tu seras prêt.",
                     jeu="[disappointed] Josée. Les Cravates sont encore là. Reviens quand tu seras prêt.")],
        # PENDANT (2e vague des scènes) : dite quand son objectif commence.
        "pendant": [_p("josee", "C'est Josée. Leur chef vient de sortir. Couche-le, pis le Faubourg est à nous.", 1,
                       jeu="[menacingly] C'est Josée. Leur chef vient de sortir. Couche-le, pis le Faubourg est à nous.")],
    },
}
