"""La mission e12 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "e12",
    "titre": "Le selfie de Xavier",
    "donneur": "xavier",
    "prerequis": ["m6"],
    "recompense": 200,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"message": "XAVIER A SA VIDÉO"},

    # ⚠️ `sauter` (M16) : le vol se compte comme le défi Le Grand Saut (`vol_px`),
    # dans N'IMPORTE QUEL véhicule en l'air — `ou` ne sert qu'à pointer le GPS.
    "objectifs": [
        {"type": "monter", "texte": "MONTE DANS UN COUPÉ SPORT", "vehicule": "sport", "ou": "porte:depanneur"},

        # ⚠️ Des missions plus longues (Martin, 22 sept. 2026) : le saut se filme à l'autre bout
        # de la ville, le phare en arrière-plan ; le saut attire la police ; et le coupé retourne
        # où il dormait — c'est le char de l'oncle de Xavier, qui n'en sait rien. Des lieux déjà
        # de mission (`phare`, `depanneur`) : la ville ne bouge pas. ⚠️ `rampe:erables` ne se
        # résolvait pas (aucune rampe aux Érables : le GPS ne montrait rien) ; celle de La Pointe
        # est au pied du phare.
        {"type": "aller", "texte": "VA AU PHARE DE LA POINTE, POUR LE DÉCOR",
         "lieu": "phare", "rayon": 6},

        {"type": "sauter", "texte": "SAUTE LA RAMPE DE LA POINTE, 40 PX DE VOL",
         "ou": "rampe:pointe", "vol_px": 40},

        {"type": "semer", "texte": "UN COUPÉ QUI VOLE, ÇA SE REMARQUE : SÈME LA POLICE", "etoiles": 2},

        {"type": "livrer", "texte": "RAMÈNE LE COUPÉ AU DÉPANNEUR, SANS UNE ÉGRATIGNURE",
         "lieu": "depanneur", "rayon": 5, "sans_degats": True},

        {"type": "retourner", "texte": "RETOURNE VOIR XAVIER"}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Xavier : excité, vite, un peu naïf — il
    # applaudit avant que le saut soit fini, panique à la première sirène (c'était pas
    # dans son script), puis en rit une fois la peur passée — même celle de son oncle.
    "dialogue": {
        "appel": [
            _l("xavier", "Xavier! Tu me replaces pas? J'ai besoin d'un coupé sport, pis de te voir sauter la rampe avec.",
               jeu="[excited] Xavier! Tu me replaces pas? [enthusiastic] J'ai besoin d'un coupé sport, pis de te voir sauter la rampe avec.")
        ],
        "intro": [
            _l("xavier", "Un coupé sport, genre, le plus stylé que tu trouves. Amène-le au dépanneur.",
               jeu="[excited] Un coupé sport, genre, le plus stylé que tu trouves. [playfully] Amène-le au dépanneur."),
            _l("xavier", "Après ça, tu sautes la rampe. Faut que ça soit assez haut pour ma vidéo!",
               jeu="[enthusiastic] Après ça, tu sautes la rampe. [excited] Faut que ça soit assez haut pour ma vidéo!")
        ],
        "pendant": [
            _p("xavier", "Envoye, fonce! Prends de l'élan avant la rampe!", 2,
               jeu="[excited] Envoye, fonce! [enthusiastic] Prends de l'élan avant la rampe!"),
            _p("xavier", "Le phare au coucher du soleil, genre, en arrière-plan. Ça va être full stylé.", 1,
               jeu="[enthusiastic] Le phare au coucher du soleil, genre, en arrière-plan. [playfully] Ça va être full stylé."),
            _p("xavier", "La police! Genre, c'était pas dans le script, ça! Sème-les!", 3,
               jeu="[nervously] La police! [excited] Genre, c'était pas dans le script, ça! Sème-les!"),
            _p("xavier", "Ramène-le au dépanneur sans une égratignure. C'est le char de mon oncle, y le sait pas.", 4,
               jeu="[nervously] Ramène-le au dépanneur sans une égratignure. [laughs] C'est le char de mon oncle… y le sait pas.")
        ],
        "fin": [
            _l("xavier", "T'as volé, genre, full haut! J'ai tout sur vidéo!",
               jeu="[excited] T'as volé, genre, full haut! [laughs] J'ai tout sur vidéo!"),
            _l("xavier", "Mes amis vont capoter. Merci, t'es stylé.",
               jeu="[happy] Mes amis vont capoter. [warmly] Merci, t'es stylé."),
            _l("xavier", "Mon oncle va jamais le savoir. Sauf s'il regarde mes vidéos.",
               jeu="[playfully] Mon oncle va jamais le savoir. [laughs] Sauf s'il regarde mes vidéos.")
        ],
        "echec": [
            _l("xavier", "Ah non... Pas de photo, pas de char.",
               jeu="[disappointed] Ah non… [sighs] Pas de photo, pas de char.")
        ]
    }
}
