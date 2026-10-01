"""La mission e05 — voir app/missions/__init__.py pour le moteur.

Le char dans la piscine (M16, arc E, les Érables — 1er oct. 2026). Cette nuit, les Chevreuils ont poussé une auto
volée dans la piscine de Diane Larivière : le toit dépasse, l'eau est huileuse, et la conseillère reçoit le comité de
quartier à midi. La remorqueuse de Gilles attend au lot ; le treuil sort l'auto de l'eau par-dessus la haie
(`remorquer`, `static/js/piscine.js`), et on la livre au lot, accrochée, avant de revenir le dire à Diane.

⚠️ La piscine de Diane est la piscine de villa la plus proche du dépanneur (`piscine:depanneur`) : la ville ne bouge
pas d'une tuile, aucun lieu neuf.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "e05",
    "titre": "Le char dans la piscine",
    "donneur": "diane",
    "prerequis": ["e01"],
    "recompense": 200,
    "donne": {"message": "LA PISCINE DE DIANE EST LIBRE — LE COMITÉ PEUT VENIR"},

    "objectifs": [
        {"type": "monter", "texte": "LA REMORQUEUSE DE GILLES T'ATTEND AU LOT",
         "vehicule": "remorqueuse", "ou": "porte:fourriere", "prete": "gilles"},

        {"type": "remorquer", "texte": "SORS L'AUTO DE LA PISCINE DE DIANE, AU TREUIL",
         "vehicule": "auto", "ou": "piscine:depanneur", "lieu": "fourriere", "rayon": 6},

        {"type": "retourner", "texte": "DIS-LE À DIANE, AU DÉPANNEUR"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Diane : la politicienne qui vouvoie, et qui se retient de dire « mon fils ».
    # Elle se nomme une fois, au téléphone.
    "dialogue": {
        "appel": [
            _l("diane", "Diane Larivière. Il y a une auto dans ma piscine. Venez au dépanneur, discrètement.",
               jeu="[calm] Diane Larivière. [wryly] Il y a une auto dans ma piscine. [quietly] Venez au dépanneur, discrètement.")
        ],
        "intro": [
            _l("diane", "Les Chevreuils l'ont poussée cette nuit. Le toit dépasse, et l'eau sent l'huile à moteur.",
               jeu="[coldly] Les Chevreuils l'ont poussée cette nuit. [annoyed] Le toit dépasse, et l'eau sent l'huile à moteur."),
            _l("diane", "Le comité de quartier vient à midi. Gilles vous prête sa remorqueuse : le treuil va la chercher.",
               jeu="[firmly] Le comité de quartier vient à midi. [calm] Gilles vous prête sa remorqueuse : le treuil va la chercher.")
        ],
        "pendant": [
            _p("diane", "La remorqueuse est au lot. Gilles ne pose pas de questions, c'est sa qualité.", 0,
               jeu="[calm] La remorqueuse est au lot. [wryly] Gilles ne pose pas de questions, c'est sa qualité."),
            _p("diane", "Approchez de la haie, reculez, klaxonnez : le câble fera le reste. Pas sur mes cèdres.", 1,
               jeu="[matter-of-fact] Approchez de la haie, reculez, klaxonnez : le câble fera le reste. [firmly] Pas sur mes cèdres."),
            _p("diane", "Au lot. Gilles saura quoi faire d'une auto volée qui sent le chlore.", 2,
               jeu="[satisfied] Au lot. [wryly] Gilles saura quoi faire d'une auto volée qui sent le chlore.")
        ],
        "fin": [
            _l("diane", "Ma piscine est vide d'autos. Le comité ne verra que des cèdres et du chlore.",
               jeu="[relieved] Ma piscine est vide d'autos. [wryly] Le comité ne verra que des cèdres et du chlore."),
            _l("diane", "Pour votre peine. Et si vous croisez ces jeunes, dites-leur que je sais compter.",
               jeu="[calm] Pour votre peine. [coldly] Et si vous croisez ces jeunes, dites-leur que je sais compter.")
        ],
        "echec": [
            _l("diane", "Le comité arrive, et l'auto est encore dans l'eau. Je vais parler de piscine flottante.",
               jeu="[disappointed] Le comité arrive, et l'auto est encore dans l'eau. [sarcastic] Je vais parler de piscine flottante.")
        ]
    }
}
