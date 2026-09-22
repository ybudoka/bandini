"""La mission m3 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m3", "titre": "Le taxi de Marco", "donneur": "marco", "prerequis": ["m2"],
    "recompense": 200, "phase": 1, "echec": ["arrete", "vehicule_detruit"],
    "donne": {"message": "LE SERGENT BOUCHARD VEUT TE VOIR"},
    "objectifs": [
        {"type": "monter", "vehicule": "taxi", "ou": "porte:garage", "prete": "marco",
         "texte": "MONTE DANS LE TAXI DE MARCO"},
        {"type": "courses", "n": 3, "texte": "FAIS TROIS COURSES — KLAXONNE POUR UN CLIENT"},
        # ⚠️ « Des missions plus longues » (Martin, 22 sept. 2026) : la boîte « qui existe pas »
        # du coffre va au phare, à l'autre bout de la ville (le pont de La Pointe est ouvert
        # depuis m2) ; puis le client de la troisième course, qui était VRAIMENT de la police,
        # t'a suivi : une étoile à semer avant de ramener le taxi.
        {"type": "aller", "lieu": "phare", "rayon": 5, "texte": "PORTE LA BOÎTE DU COFFRE AU PHARE DE LA POINTE"},
        {"type": "semer", "etoiles": 1, "texte": "TON CLIENT ÉTAIT UN BŒUF — SÈME LA POLICE"},
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
            {"type": "dire", "repliques": [3]},
            {"type": "camera", "vers": "joueur", "duree": 40, "courbe": "freine"},
        ],
        # ⚠️ Chaque `dire` retient la scène jusqu'au bout de sa voix : le geste, puis la
        # coupe, partent AVEC la réplique qui les porte (`ensemble` sur eux, jamais sur
        # le `dire`). Avant, la 1re réplique était en `ensemble` sous un geste de
        # 60 images, et la coupe la tranchait (`DEJA_COUPEES`, « m3-fin »).
        "fin": [
            {"type": "marcher", "acteur": "donneur", "vers": "vehicule", "pres": 24, "duree": 50},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "chez:bouchard", "duree": 60,
             "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "chez:bouchard", "ferme": 20, "ouvre": 20, "tient": 130, "ensemble": True},
            {"type": "dire", "repliques": [3]},
            {"type": "marcher", "acteur": "donneur", "vers": "place:donneur", "duree": 50},
        ],
    },
    # Le jeu de chaque réplique (`jeu=`) — Marco : l'affaire d'abord, et la mise en garde a voix basse.
    "dialogue": {
        "appel": [_l("marco", "Salut, c'est Marco, le Cousin. J'ai un taxi qui dort au garage. Ça te tente de faire du cash?",
                     jeu="[casually] Salut, c'est Marco, le Cousin. J'ai un taxi qui dort au garage. [mischievously] Ça te tente de faire du cash?")],
        "intro": [
            _l("marco", "Trois clients, pas plus. Pis tu me ramènes le taxi entier.",
               jeu="[serious] Trois clients, pas plus. Pis tu me ramènes le taxi… entier."),
            _l("marco", "Ouvre l'œil. Y a du monde en ville qui pose des questions sur toi.",
               jeu="[quietly] Ouvre l'œil. Y a du monde en ville… qui pose des questions sur toi."),
            _l("marco", "Pis touche pas au coffre, cousin. Y a rien dedans, pis c'est à moi.",
               jeu="[firmly] Pis touche pas au coffre, cousin. [wryly] Y a rien dedans… pis c'est à moi."),
        ],
        "client": [_l("civil", "Roule, mon homme. Pis fais pas de folies : j'suis de la police.",
                      jeu="[smugly] Roule, mon homme. Pis fais pas de folies… j'suis de la police.")],
        "fin": [
            _l("marco", "Le coffre est vide, comme d'habitude. Parfait, cousin.",
               jeu="[wryly] Le coffre est vide… comme d'habitude. [satisfied] Parfait, cousin."),
            _l("marco", "Trois courses, un taxi entier. Le sergent Bouchard veut te voir au casse-croûte.",
               jeu="[impressed] Trois courses, un taxi entier. Le sergent Bouchard veut te voir au casse-croûte."),
            _l("marco", "Y mange là tous les midis. Sois poli, c'est un ami de la famille.",
               jeu="[casually] Y mange là tous les midis. Sois poli… c'est un ami de la famille."),
        ],
        "echec": [_l("marco", "Mon taxi... Bon. On efface, pis on recommence.",
                     jeu="[disappointed] Mon taxi… Bon. On efface… [groans] pis on recommence.")],
        # PENDANT : dites quand leur objectif commence, au combiné.
        "pendant": [
            _p("marco", "La boîte dans le coffre, cousin, celle qui existe pas. Va la porter au phare, au bout de La Pointe.", 2,
               jeu="[quietly] La boîte dans le coffre, cousin… celle qui existe pas. [serious] Va la porter au phare, au bout de La Pointe."),
            _p("marco", "Ton client de la police t'a suivi, cousin. Sème-le avant de revenir, j'veux pas le voir au garage.", 3,
               jeu="[worried] Ton client de la police t'a suivi, cousin. [firmly] Sème-le avant de revenir… j'veux pas le voir au garage."),
            _p("marco", "Bon. Ramène le taxi, cousin, pis roule comme un chauffeur, pas comme un neveu.", 4,
               jeu="[casually] Bon. [wryly] Ramène le taxi, cousin, pis roule comme un chauffeur… pas comme un neveu."),
        ],
    },
}
