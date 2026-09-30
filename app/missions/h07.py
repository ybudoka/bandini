"""La mission h07 — voir app/missions/__init__.py pour le moteur.

La nuit des urgences (M16, arc H, 30 sept. 2026). La guerre des gangs a rempli l'urgence : le jour où un district
est libéré (`exige.liberes`), ceux qui l'ont perdu règlent leurs comptes dans les ruelles. Une nuit entière en
ambulance — cinq transports —, puis trois Cravates qui viennent « finir » un des leurs à la porte de l'urgence, et
les clés rendues à Ginette au petit matin. La dernière de l'arc : Lachance, pour une fois, remercie.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "h07",
    "titre": "La nuit des urgences",
    "donneur": "lachance",
    "prerequis": ["h06"],
    "exige": {"liberes": 2},
    "recompense": 500,
    "donne": {"message": "L'URGENCE A TENU TOUTE LA NUIT"},

    # ⚠️ Le patron de h01 (la nuit, l'ambulance, `boulots`), deux fois plus long, et une bagarre de plus : les trois
    # Cravates arrivent de loin (`loin`) où l'on est quand le cinquième blessé est livré. On finit chez Ginette, à
    # la porte de l'hôpital (elle est dehors) ; Lachance est dedans, et sa fin passe au combiné comme en h01.
    "objectifs": [
        {"type": "aller", "texte": "À L'HÔPITAL, LA NUIT VA ÊTRE LONGUE",
         "lieu": "hopital", "rayon": 6, "nuit": True},

        {"type": "monter", "texte": "MONTE DANS L'AMBULANCE", "vehicule": "ambulance", "ou": "porte:hopital"},

        {"type": "boulots", "texte": "CINQ BLESSÉS À RAMASSER CETTE NUIT", "n": 5, "sorte": "ambulance"},

        {"type": "tuer", "texte": "TROIS CRAVATES VIENNENT FINIR UN BLESSÉ : ARRÊTE-LES",
         "groupe": "cravates", "n": 3, "loin": 12},

        {"type": "parler", "texte": "RENDS LES CLÉS À GINETTE, AU PETIT MATIN", "cible": "ginette"},
    ],

    # Intention (intro) : Lachance ne donne pas d'ordre, il fait un bilan — sa réplique tient le bureau, la coupe
    # montre la porte de l'urgence sous la deuxième (la file des blessés), la troisième sur le retour.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:hopital", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Lachance : la nuit qu'il redoutait, dite comme un rapport de triage. Il
    # ne se plaint jamais de sa fatigue ; elle s'entend dans les silences. Ginette, au matin : sèche, et pour une
    # fois presque tendre.
    "dialogue": {
        "appel": [
            _l("lachance", "Ici Lachance. Les gangs se règlent leurs comptes, pis l'urgence déborde. J'ai besoin de toi toute la nuit.",
               jeu="[gravely] Ici Lachance. Les gangs se règlent leurs comptes, pis l'urgence déborde. [firmly] J'ai besoin de toi toute la nuit.")
        ],
        "intro": [
            _l("lachance", "Un quartier change de mains, pis ceux qui l'ont perdu se vengent dans les ruelles. Je connais la chanson.",
               jeu="[somber] Un quartier change de mains, pis ceux qui l'ont perdu se vengent dans les ruelles. [wryly] Je connais la chanson."),
            _l("lachance", "Cinq transports, peut-être plus. Klaxonne pour chaque blessé, comme la dernière fois.",
               jeu="[matter-of-fact] Cinq transports, peut-être plus. [firmly] Klaxonne pour chaque blessé, comme la dernière fois."),
            _l("lachance", "Pis si quelqu'un vient finir le travail à ma porte, tu l'en empêches.",
               jeu="[serious] Pis si quelqu'un vient finir le travail à ma porte… [coldly] tu l'en empêches.")
        ],
        "pendant": [
            _p("lachance", "Attends la noirceur. C'est là que ça commence, toujours.", 0,
               jeu="[quietly] Attends la noirceur. [gravely] C'est là que ça commence, toujours."),
            _p("lachance", "Les clés sont dessus. Le plein est fait, la civière est propre.", 1,
               jeu="[matter-of-fact] Les clés sont dessus. [calm] Le plein est fait, la civière est propre."),
            _p("lachance", "Premier appel. Un Chevreuil, une Morue, un Boulonneux, je ne fais plus la différence.", 2,
               jeu="[gravely] Premier appel. [somber] Un Chevreuil, une Morue, un Boulonneux, je ne fais plus la différence."),
            _p("lachance", "Trois hommes à la porte de l'urgence, avec des bâtons. Personne ne finit personne ici.", 3,
               jeu="[concerned] Trois hommes à la porte de l'urgence, avec des bâtons. [firmly] Personne ne finit personne ici."),
            _p("lachance", "Le soleil se lève. Ginette prend la relève, rends-lui les clés.", 4,
               jeu="[relieved] Le soleil se lève. [calm] Ginette prend la relève, rends-lui les clés.")
        ],
        "accueil": [
            _a("ginette", "Les clés. T'as une face de nuit blanche. Assis-toi deux minutes, c'est un ordre.", 4,
               jeu="[matter-of-fact] Les clés. [wryly] T'as une face de nuit blanche. [softly] Assis-toi deux minutes, c'est un ordre.")
        ],
        "fin": [
            _l("lachance", "Cinq blessés, zéro mort. Dans cet hôpital-là, c'est une bonne nuit.",
               jeu="[relieved] Cinq blessés, zéro mort. [warmly] Dans cet hôpital-là, c'est une bonne nuit."),
            _l("lachance", "Merci. Je le dis pas souvent, alors écoute-le comme il faut.",
               jeu="[softly] Merci. [wryly] Je le dis pas souvent, alors écoute-le comme il faut.")
        ],
        "echec": [
            _l("lachance", "On a perdu la nuit. Ça arrive. Va dormir, on recommencera.",
               jeu="[somber] On a perdu la nuit. Ça arrive. [calm] Va dormir, on recommencera.")
        ]
    }
}
