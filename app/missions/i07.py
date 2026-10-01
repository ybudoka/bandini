"""La mission i07 — voir app/missions/__init__.py pour le moteur.

Le tour de l'île (M16, arc I, 1er oct. 2026) — une course sur l'eau, CONTRE quelqu'un. Six bouées autour de
l'Île-aux-Corneilles (`regate.py`, le parcours de la baie : `bouee:<n>`), dans le sens des aiguilles d'une montre,
puis retour à la première ; Léo court dans le bateau de son père, toi dans la vieille chaloupe de l'usine. Le premier
revenu paie la bière : s'il passe la dernière bouée avant toi, c'est raté (`contre`, l'échec `battu`).

⚠️ `contre` était déclaré depuis la v1 et lu par personne : le RIVAL (`regate.js`) court les mêmes points, en ligne
droite d'une bouée à l'autre, à son `allure` — un pilote honnête, qu'on bat en coupant serré. Et `vehicule` : la
course se court en chaloupe, pas à la nage.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "i07",
    "titre": "Le tour de l'île",
    "donneur": "leo",
    "prerequis": ["i04"],
    "recompense": 200,
    "echec": ["mort", "arrete", "battu", "vehicule_detruit"],
    "donne": {"message": "LE TOUR DE L'ÎLE : LÉO PAIE LA BIÈRE"},

    "objectifs": [
        {"type": "monter", "texte": "LA VIEILLE CHALOUPE DE L'USINE, SOUS LE HANGAR",
         "vehicule": "bateau", "ou": "amarrage:hangar_ile", "prete": "leo"},

        {"type": "course", "texte": "LE TOUR DE L'ÎLE : LES SIX BOUÉES, CONTRE LÉO",
         "points": ["bouee:0", "bouee:1", "bouee:2", "bouee:3", "bouee:4", "bouee:5", "bouee:0"], "rayon": 3,
         "vehicule": "bateau", "contre": {"qui": "leo", "vehicule": "bateau", "allure": 0.75}},

        {"type": "livrer", "texte": "RAMÈNE LA CHALOUPE SOUS LE HANGAR", "lieu": "amarrage:hangar_ile", "rayon": 6},
    ],

    # Intention (intro) : Léo devant son hangar, qui ne regarde pas celui qui lui parle ; la caméra part voir la
    # première bouée sous la règle, et revient pour l'enjeu (la bière, et le bateau de son père).
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "coupe", "vers": "bouee:0", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Léo : pince-sans-rire, et pour une fois il VEUT quelque chose (gagner) ; il
    # ne le dit pas. Le `[amused]` est pour sa défaite, qu'il avoue sans l'avouer.
    "dialogue": {
        "appel": [
            _l("leo", "Léo, de l'île. T'as une chaloupe pis du temps? Moé, j'ai le bateau de mon père.",
               jeu="[deadpan] Léo, de l'île. [matter-of-fact] T'as une chaloupe pis du temps? [mysteriously] Moé, j'ai le bateau de mon père.")
        ],
        "intro": [
            _l("leo", "Six bouées autour de l'île. Le premier revenu au hangar paye la bière.",
               jeu="[matter-of-fact] Six bouées autour de l'île. [deadpan] Le premier revenu au hangar paye la bière."),
            _l("leo", "Tu prends la vieille chaloupe de l'usine. Moé, le bateau de mon père. Touches-y pas.",
               jeu="[matter-of-fact] Tu prends la vieille chaloupe de l'usine. Moé, le bateau de mon père. [firmly] Touches-y pas."),
            _l("leo", "Pis si tu gagnes, j'ai rien vu. Comme d'habitude.",
               jeu="[deadpan] Pis si tu gagnes… j'ai rien vu. [amused] Comme d'habitude.")
        ],
        "pendant": [
            _p("leo", "La chaloupe est sous le hangar. Le moteur tousse, c'est normal.", 0,
               jeu="[matter-of-fact] La chaloupe est sous le hangar. [deadpan] Le moteur tousse… c'est normal."),
            _p("leo", "À trois, on part. Les bouées, dans le sens des aiguilles d'une montre.", 1,
               jeu="[matter-of-fact] À trois, on part. [deadpan] Les bouées… dans le sens des aiguilles d'une montre."),
            _p("leo", "Ramène la chaloupe sous le hangar. Pis essuie-la, elle a de l'âge.", 2,
               jeu="[deadpan] Ramène la chaloupe sous le hangar. [matter-of-fact] Pis essuie-la, elle a de l'âge.")
        ],
        "fin": [
            _l("leo", "T'as gagné. Je l'avoue pas, mais t'as gagné.",
               jeu="[deadpan] T'as gagné. [amused] Je l'avoue pas… mais t'as gagné."),
            _l("leo", "La bière est à moé, d'abord. Reviens la boire.",
               jeu="[matter-of-fact] La bière est à moé, d'abord. [amused] Reviens la boire.")
        ],
        "echec": [
            _l("leo", "Mon père aurait dit que t'as navigué comme une roche. Moé, j'ai rien dit.",
               jeu="[deadpan] Mon père aurait dit que t'as navigué comme une roche. [amused] Moé, j'ai rien dit.")
        ]
    }
}
