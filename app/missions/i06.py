"""La mission i06 — voir app/missions/__init__.py pour le moteur.

Le dernier bateau du Norvégien (M16, arc I, 30 sept. 2026). Josée a vu ce que Sven cachait sur l'île (i03) et ce
qu'il a fait au port (q11) : il lui reste un chalutier, à quai, pour repartir avec. Josée veut qu'il reparte à la
rame. On prend la chaloupe, on coule le chalutier à quai — au pistolet qu'elle met dans les mains —, trois étoiles
sur l'eau (« la police ne nage pas vite »), on les sème, et on revient au bar.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "i06",
    "titre": "Le dernier bateau du Norvégien",
    "donneur": "josee",
    "prerequis": ["i03", "q11"],
    "recompense": 500,
    "donne": {"message": "LE NORVÉGIEN N'A PLUS DE BATEAU — IL REPARTIRA À LA RAME"},

    # ⚠️ `detruire` pose le chalutier à son mouillage (le patron de q11, sur l'eau) ; `remet` met le pistolet dans les
    # mains, chargé. Josée est dedans : on finit par lui parler, au bar.
    "objectifs": [
        {"type": "monter", "texte": "LA CHALOUPE, AMARRÉE SOUS LE FAUBOURG", "vehicule": "bateau", "ou": "amarrage:bar"},

        {"type": "detruire", "texte": "LE CHALUTIER DE SVEN, À QUAI : COULE-LE",
         "vehicule": "chalutier", "ou": "mouillage:chalutier:1", "remet": "pistolet"},

        {"type": "semer", "texte": "TROIS ÉTOILES SUR L'EAU : SÈME-LES", "etoiles": 3},

        {"type": "parler", "texte": "JOSÉE VEUT L'ENTENDRE DE TA BOUCHE, AU BAR", "cible": "josee"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "mouillage:chalutier:1", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    "dialogue": {
        "appel": [
            _l("josee", "Josée. Il reste un bateau au Norvégien, pis il en aura plus. Viens au bar.",
               jeu="[coldly] Josée. Il reste un bateau au Norvégien, [menacingly] pis il en aura plus. Viens au bar.")
        ],
        "intro": [
            _l("josee", "Son chalutier dort à quai, avec ce qu'il a volé au port dans la cale.",
               jeu="[matter-of-fact] Son chalutier dort à quai, avec ce qu'il a volé au port dans la cale."),
            _l("josee", "Tiens. Vise la ligne de flottaison, pas le capitaine. On coule un bateau, on tue personne.",
               jeu="[firmly] Tiens. Vise la ligne de flottaison, pas le capitaine. [coldly] On coule un bateau, on tue personne."),
            _l("josee", "Après, ça va sonner partout. Sur l'eau, la police nage pas vite.",
               jeu="[matter-of-fact] Après, ça va sonner partout. [wryly] Sur l'eau, la police nage pas vite.")
        ],
        "pendant": [
            _p("josee", "La chaloupe t'attend sous le Faubourg. Tu connais le chemin, astheure.", 0,
               jeu="[calm] La chaloupe t'attend sous le Faubourg. [matter-of-fact] Tu connais le chemin, astheure."),
            _p("josee", "Le chalutier bleu, au deuxième quai. Coule-le.", 1,
               jeu="[coldly] Le chalutier bleu, au deuxième quai. [firmly] Coule-le."),
            _p("josee", "Il coule. Astheure, perds la police, pis reviens-moi entier.", 2,
               jeu="[satisfied] Il coule. [firmly] Astheure, perds la police, pis reviens-moi entier."),
            _p("josee", "Viens au bar. Je veux l'entendre de ta bouche.", 3,
               jeu="[calm] Viens au bar. [quietly] Je veux l'entendre de ta bouche.")
        ],
        "fin": [
            _l("josee", "Le Norvégien regardait son bateau couler du bout du quai. Il a enlevé sa tuque.",
               jeu="[satisfied] Le Norvégien regardait son bateau couler du bout du quai. [wryly] Il a enlevé sa tuque."),
            _l("josee", "Les Quais sont à nous, pour vrai. Ça, c'est ta part.",
               jeu="[warmly] Les Quais sont à nous, pour vrai. [matter-of-fact] Ça, c'est ta part.")
        ],
        "echec": [
            _l("josee", "Le chalutier flotte encore. Sven va nous le faire payer.",
               jeu="[coldly] Le chalutier flotte encore. [matter-of-fact] Sven va nous le faire payer.")
        ]
    }
}
