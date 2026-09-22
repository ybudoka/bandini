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

        {"type": "sauter", "texte": "SAUTE LA RAMPE DES ÉRABLES, 40 PX DE VOL",
         "ou": "rampe:erables", "vol_px": 40},

        {"type": "retourner", "texte": "RETOURNE VOIR XAVIER"}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Xavier : excité, vite, un peu naïf — il
    # applaudit avant que le saut soit fini, puis il en rit une fois la peur passée.
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
            _p("xavier", "Envoye, fonce! Prends de l'élan avant la rampe!", 1,
               jeu="[excited] Envoye, fonce! [enthusiastic] Prends de l'élan avant la rampe!")
        ],
        "fin": [
            _l("xavier", "T'as volé, genre, full haut! J'ai tout sur vidéo!",
               jeu="[excited] T'as volé, genre, full haut! [laughs] J'ai tout sur vidéo!"),
            _l("xavier", "Mes amis vont capoter. Merci, t'es stylé.",
               jeu="[happy] Mes amis vont capoter. [warmly] Merci, t'es stylé.")
        ],
        "echec": [
            _l("xavier", "Ah non... Pas de photo, pas de char.",
               jeu="[disappointed] Ah non… [sighs] Pas de photo, pas de char.")
        ]
    }
}
