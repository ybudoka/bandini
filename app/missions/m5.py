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
        # « Des missions plus longues » (22 sept. 2026) : leur chef couché, leur trésorier file en char
        # avec la caisse — une POURSUITE (le fuyard de m97 : on le rattrape, un Cravate en descend
        # avec la caisse, on le couche, on la ramasse). Puis, la police semée, la caisse ne va pas
        # au bar (c'est chez Josée qu'on cherchera d'abord) : à l'AUTRE BOUT de la ville, derrière la
        # cantine des Quais — celle de sa sœur, qu'on rencontrera à m6.
        {"type": "ramasser", "cible": "fuyard", "vehicule": "auto", "texte": "RATTRAPE LA CAISSE DES CRAVATES"},
        {"type": "semer", "etoiles": 3, "texte": "SÈME LA POLICE"},
        {"type": "aller", "lieu": "cantine", "rayon": 4, "texte": "CACHE LA CAISSE À LA CANTINE DES QUAIS"},
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
    # Le jeu de chaque réplique (`jeu=`) — Josee : froide, et elle pese chaque ordre ; un seul trait
    # d'esprit, sec, quand c'est fini (le Faubourg « sans cravate »).
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
            _l("josee", "Le Faubourg respire. Le bar est à toi, pis toute la ville va le lire demain matin.",
               jeu="[satisfied] Le Faubourg respire. Le bar est à toi… pis toute la ville va le lire demain matin."),
            _l("josee", "On va se reparler. Y a plus grand que le Faubourg.",
               jeu="[mysteriously] On va se reparler. Y a plus grand… que le Faubourg."),
        ],
        "echec": [_l("josee", "Les Cravates sont encore là. Reviens quand tu seras prêt.",
                     jeu="[disappointed] Les Cravates sont encore là. Reviens quand tu seras prêt.")],
        # PENDANT (2e vague des scènes) : dite quand son objectif commence.
        "pendant": [
            _p("josee", "Leur chef vient de sortir. Couche-le, pis le Faubourg est à nous.", 1,
               jeu="[menacingly] Leur chef vient de sortir. Couche-le, pis le Faubourg est à nous."),
            _p("josee", "Leur trésorier se sauve avec la caisse. Ce qu'ils ont pris au Faubourg, je le reprends.", 2,
               jeu="[coldly] Leur trésorier se sauve avec la caisse. [firmly] Ce qu'ils ont pris au Faubourg… je le reprends."),
            _p("josee", "Pas au Brouillard, c'est chez moi qu'ils vont chercher. Laisse la caisse derrière la cantine des Quais.", 4,
               jeu="[matter-of-fact] Pas au Brouillard, c'est chez moi qu'ils vont chercher. [quietly] Laisse la caisse derrière la cantine des Quais."),
            _p("josee", "Ma sœur l'a trouvée. Rentre, demain le Faubourg se réveille sans cravate.", 5,
               jeu="[satisfied] Ma sœur l'a trouvée. [wryly] Rentre… demain le Faubourg se réveille sans cravate."),
        ],
    },
}
