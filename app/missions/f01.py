"""La mission f01 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "f01",
    "titre": "Les Cravates reviennent",
    "donneur": "marco",
    # ⚠️ Après m50 et pas m6 : c'est la suite de Marco (le Cargo de Minuit), et ça garde le téléphone
    # calme — m6 ouvre déjà m50 et e01, il ne sonne pas cinq fois de suite.
    "prerequis": ["m50"],
    "recompense": 300,
    "donne": {"message": "LE GARAGE RESPIRE"},

    # ⚠️ Les Cravates gardent leur fiche de rue (bâton, 90 PV) : ce sont elles qui ont tenu le
    # Faubourg en m5, et on n'en affaiblit pas une pour arranger une bagarre. Ce qui change, c'est
    # combien on en envoie : trois qui arrivent de loin, puis leur chef.
    "objectifs": [
        {"type": "aller", "texte": "ATTENDS LA NUIT AU GARAGE",
         "lieu": "garage", "rayon": 6, "nuit": True},

        {"type": "tuer", "texte": "REPOUSSE LES TROIS CRAVATES",
         "groupe": "cravates", "n": 3, "ou": "donneur", "loin": 14},

        {"type": "tuer", "texte": "COUCHE LEUR CHEF",
         "groupe": "cravates", "n": 1, "chef": True},

        # « Des missions plus longues » (22 sept. 2026) : leur chef couché, leur comptable file avec le
        # livre où la dette de Rocco est écrite. On le rattrape, la bagarre a fait venir la police, et
        # Marco ne veut plus jamais voir ce livre : il finit à la mer, chez Ovila, au bout de La Pointe
        # — l'autre bout de la ville.
        {"type": "ramasser", "texte": "RATTRAPE LE COMPTABLE ET SON LIVRE DE DETTES",
         "vehicule": "auto", "cible": "fuyard"},

        {"type": "semer", "texte": "SÈME LA POLICE, LE LIVRE DANS TES POCHES",
         "etoiles": 2},

        {"type": "parler", "texte": "DONNE LE LIVRE À OVILA, AU PHARE",
         "cible": "ovila"},

        {"type": "retourner", "texte": "RETOURNE VOIR MARCO"}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Marco, les Cravates reviennent : la désinvolture de qui
    # a peur et le cache. Il hausse les épaules sur « Rocco leur devait de l'argent », puis il se
    # dérobe (« je surveille la porte ») — le sous-texte est la lâcheté drôle ; à la fin, soulagé,
    # il paie et il se rengorge.
    "dialogue": {
        "appel": [
            _l("marco", "Cousin, c'est Marco. Les Cravates rôdent autour du garage. Viens, pis apporte ton bâton.",
               jeu="[casually] Cousin, c'est Marco. Les Cravates rôdent autour du garage. [firmly] Viens, pis apporte ton bâton.")
        ],
        "intro": [
            _l("marco", "Ils disent que Rocco leur devait de l'argent.",
               jeu="[casually] Ils disent que Rocco leur devait de l'argent."),
            _l("marco", "Ils veulent le collecter sur toi, à la noirceur. Moi, je surveille la porte.",
               jeu="[wryly] Ils veulent le collecter sur toi… à la noirceur. Moi, je surveille la porte."),
            _l("marco", "Pis si ça tourne mal, je dirai que t'étais pas de la famille.",
               jeu="[casually] Pis si ça tourne mal… [wryly] je dirai que t'étais pas de la famille.")
        ],
        "pendant": [
            _p("marco", "Leur chef est là! Couche-le, pis ils oublieront le chemin du garage.", 2,
               jeu="[firmly] Leur chef est là! Couche-le… pis ils oublieront le chemin du garage."),
            _p("marco", "Leur comptable se sauve avec le livre de dettes! Rocco est écrit dedans.", 3,
               jeu="[worried] Leur comptable se sauve avec le livre de dettes! [firmly] Rocco est écrit dedans."),
            # Là ou au combiné (`present`) : Marco est resté à sa porte, on a le livre et deux autos-patrouilles.
            _p("marco", "Deux autos-patrouilles, cousin. Perds-les, pis garde le livre au chaud.", 4,
               jeu="[quietly] Deux autos-patrouilles, cousin. [firmly] Perds-les, pis garde le livre au chaud."),
            _p("marco", "Va porter ça au vieux Ovila, au phare. La mer garde mieux les secrets que moi.", 5,
               jeu="[wryly] Va porter ça au vieux Ovila, au phare. La mer garde mieux les secrets… que moi.")
        ],
        "fin": [
            _l("marco", "Le garage respire. Personne va venir nous parler de dette avant longtemps.",
               jeu="[relieved] Le garage respire. [warmly] Personne va venir nous parler de dette… avant longtemps."),
            _l("marco", "Plus de livre, plus de dette. C'est comme ça que je fais mes comptes, moi.",
               jeu="[satisfied] Plus de livre, plus de dette. [wryly] C'est comme ça que je fais mes comptes, moi."),
            _l("marco", "Tiens, pour la peine. Je t'en dois une, cousin.",
               jeu="[warmly] Tiens, pour la peine… Je t'en dois une, cousin.")
        ],
        "echec": [
            _l("marco", "Ils t'ont eu… Repose-toi, cousin. Le garage tient encore debout.",
               jeu="[concerned] Ils t'ont eu… Repose-toi, cousin. [wryly] Le garage tient encore debout.")
        ],
        # La poignée de main du phare. Ovila vouvoie (le seul du jeu) et se nomme : f01 se joue après
        # m50, pas forcément après m6 — on peut le rencontrer ici.
        "accueil": [
            _a("ovila", "Ovila, au phare, bonsoir. Un livre de dettes? La mer en a avalé des pires que vous.", 5,
               jeu="[calm] Ovila, au phare, bonsoir. Un livre de dettes? [mysteriously] La mer en a avalé des pires… que vous.")
        ]
    },

    # Intention (intro) : le joueur comprend que Marco pousse le problème vers lui en haussant les
    # épaules — le geste tombe sur « Rocco leur devait de l'argent » (c'est pas mon affaire), un
    # battement, puis la vraie demande. Le défaut aurait montré le garage… où Marco se tient déjà.
    # Intention (fin) : Marco reprend de l'assurance (bras croisés : le garage est à lui), un battement,
    # puis il paie. Aucun plan ne tire de dé ni ne déplace le joueur.
    "scenes": {
        "intro": [
            { "type": "geste", "acteur": "donneur", "geste": "hausser", "duree": 70, "ensemble": True },
            { "type": "dire", "repliques": [1] },
            { "type": "attendre", "duree": 30 },
            { "type": "dire", "repliques": [2] },
            # Sa lâcheté drôle, dite en haussant les épaules — la même que sur Rocco.
            { "type": "geste", "acteur": "donneur", "geste": "hausser", "duree": 60, "ensemble": True },
            { "type": "dire", "repliques": [3] }
        ],
        "fin": [
            { "type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 70, "ensemble": True },
            { "type": "dire", "repliques": [1] },
            { "type": "attendre", "duree": 20 },
            { "type": "geste", "acteur": "donneur", "geste": "hausser", "duree": 50, "ensemble": True },
            { "type": "dire", "repliques": [2] },
            { "type": "attendre", "duree": 30 },
            { "type": "geste", "acteur": "donneur", "geste": "donner", "vers": "joueur", "duree": 60,
              "ensemble": True },
            { "type": "dire", "repliques": [3] }
        ]
    }
}
