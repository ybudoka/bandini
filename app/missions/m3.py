"""La mission m3 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l

MISSION = {
    "slug": "m3", "titre": "Le taxi de Marco", "donneur": "marco", "prerequis": ["m2"],
    "recompense": 200, "phase": 1, "echec": ["arrete", "vehicule_detruit"],
    "donne": {"message": "LE SERGENT BOUCHARD VEUT TE VOIR"},
    "objectifs": [
        {"type": "monter", "vehicule": "taxi", "ou": "porte:garage", "prete": "marco",
         "texte": "MONTE DANS LE TAXI DE MARCO"},
        {"type": "courses", "n": 3, "texte": "FAIS TROIS COURSES — KLAXONNE POUR UN CLIENT"},
        {"type": "livrer", "lieu": "garage", "rayon": 4, "texte": "RAMÈNE LE TAXI AU GARAGE"},
    ],
    # Marco tend les clés, et la caméra va voir le taxi. À la fin, il fait le
    # tour du taxi, montre le casse-croûte, et la caméra y va : la fin passe la
    # main au sergent Bouchard.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "donner", "vers": "joueur", "duree": 60,
             "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "camera", "vers": "vehicule", "duree": 45, "courbe": "freine", "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "camera", "vers": "joueur", "duree": 40, "courbe": "freine"},
        ],
        "fin": [
            {"type": "marcher", "acteur": "donneur", "vers": "vehicule", "pres": 24, "duree": 50},
            {"type": "dire", "repliques": [1], "ensemble": True},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "chez:bouchard", "duree": 60},
            {"type": "coupe", "vers": "chez:bouchard", "ferme": 20, "ouvre": 20, "tient": 130, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "marcher", "acteur": "donneur", "vers": "place:donneur", "duree": 50},
        ],
    },
    # Le jeu de chaque réplique (`jeu=`) — Marco : l'affaire d'abord, et la mise en garde a voix basse.
    "dialogue": {
        "appel": [_l("marco", "Marco, le cousin. J'ai un taxi qui dort au garage. Ça te tente de faire du cash?",
                     jeu="[casually] Marco, le cousin. J'ai un taxi qui dort au garage. [mischievously] Ça te tente de faire du cash?")],
        "intro": [
            _l("marco", "Trois clients, pas plus. Pis tu me ramènes le taxi entier.",
               jeu="[serious] Trois clients, pas plus. Pis tu me ramènes le taxi… entier."),
            _l("marco", "Ouvre l'œil. Y a du monde en ville qui pose des questions sur toi.",
               jeu="[quietly] Ouvre l'œil. Y a du monde en ville… qui pose des questions sur toi."),
        ],
        "client": [_l("civil", "Roule, mon homme. Pis fais pas de folies : j'suis de la police.",
                      jeu="[smugly] Roule, mon homme. Pis fais pas de folies… j'suis de la police.")],
        "fin": [
            _l("marco", "Trois courses, un taxi entier. Le sergent Bouchard veut te voir au casse-croûte.",
               jeu="[impressed] Trois courses, un taxi entier. Le sergent Bouchard veut te voir au casse-croûte."),
            _l("marco", "Y mange là tous les midis. Sois poli, c'est un ami de la famille.",
               jeu="[casually] Y mange là tous les midis. Sois poli… c'est un ami de la famille."),
        ],
        "echec": [_l("marco", "Mon taxi... Bon. On efface, pis on recommence.",
                     jeu="[disappointed] Mon taxi… Bon. On efface… [groans] pis on recommence.")],
    },
}
