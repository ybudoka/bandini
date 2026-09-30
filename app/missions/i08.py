"""La mission i08 — voir app/missions/__init__.py pour le moteur.

La cache de Rocco (M16, arc I, 30 sept. 2026). Les papiers de Rocco (d05) parlaient d'une île, d'une chapelle et d'un
« trou sous le troisième banc ». Josée les a lus avant l'avocat. On traverse, on prend la cache sous la chapelle — et
deux matelots de Sven, qui avaient lu la même chose, arrivent trop tard pour la prendre et trop tôt pour s'en aller.
On la ramène au bar par l'eau : mille deux cents piastres de l'oncle.

⚠️ Ti-Guy devait la donner : il a quitté la ville après m1 (`parti_apres`) — c'est Josée.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "i08",
    "titre": "La cache de Rocco",
    "donneur": "josee",
    "prerequis": ["i01", "d05"],
    "recompense": 1200,
    "donne": {"message": "LA CACHE DE L'ONCLE EST AU BROUILLARD"},

    # ⚠️ `obtenir` posé devant la chapelle (l'île se marche une fois accosté) ; les matelots arrivent de loin (`loin`)
    # là où l'on est, pas où la fin se joue (Josée, au bar).
    "objectifs": [
        {"type": "monter", "texte": "LA CHALOUPE, SOUS LE FAUBOURG", "vehicule": "bateau", "ou": "amarrage:bar"},

        {"type": "livrer", "texte": "TRAVERSE JUSQU'À LA CHAPELLE DE L'ÎLE", "lieu": "amarrage:chapelle", "rayon": 6},

        {"type": "obtenir", "texte": "SOUS LE TROISIÈME BANC : LA CACHE DE ROCCO",
         "objet": "cache_de_rocco", "ou": "chapelle", "dessin": "sac", "nom": "LA CACHE DE L'ONCLE"},

        {"type": "tuer", "texte": "DEUX MATELOTS LA CHERCHAIENT AUSSI : COUCHE-LES",
         "groupe": "morues", "pieton": "matelot", "n": 2, "loin": 10},

        {"type": "livrer", "texte": "RAMÈNE LA CACHE SOUS LE FAUBOURG, PAR L'EAU", "lieu": "amarrage:bar", "rayon": 6},

        {"type": "parler", "texte": "JOSÉE COMPTE L'HÉRITAGE, AU BAR", "cible": "josee"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "amarrage:chapelle", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    "dialogue": {
        "appel": [
            _l("josee", "Josée. Les papiers de ton oncle parlent d'une île, pis j'ai lu avant l'avocat. Viens.",
               jeu="[mysteriously] Josée. Les papiers de ton oncle parlent d'une île, [knowingly] pis j'ai lu avant l'avocat. Viens.")
        ],
        "intro": [
            _l("josee", "« Sous le troisième banc de la chapelle. » Rocco écrivait comme il parlait : peu.",
               jeu="[mysteriously] « Sous le troisième banc de la chapelle. » [wryly] Rocco écrivait comme il parlait : peu."),
            _l("josee", "Traverse, prends ce qu'il y a, pis reviens par l'eau. C'est ton héritage, pas le mien.",
               jeu="[matter-of-fact] Traverse, prends ce qu'il y a, pis reviens par l'eau. [warmly] C'est ton héritage, pas le mien."),
            _l("josee", "Sven a lu les mêmes papiers, je pense. Dépêche.",
               jeu="[serious] Sven a lu les mêmes papiers, je pense. [firmly] Dépêche.")
        ],
        "pendant": [
            _p("josee", "La chaloupe, sous le Faubourg. Tu la connais.", 0,
               jeu="[calm] La chaloupe, sous le Faubourg. [matter-of-fact] Tu la connais."),
            _p("josee", "Accoste sous la chapelle. La sœur dira rien, elle a vu Rocco jeune.", 1,
               jeu="[quietly] Accoste sous la chapelle. [knowingly] La sœur dira rien, elle a vu Rocco jeune."),
            _p("josee", "Le troisième banc, côté fenêtre. Une latte qui sonne creux.", 2,
               jeu="[mysteriously] Le troisième banc, côté fenêtre. [quietly] Une latte qui sonne creux."),
            _p("josee", "Je te l'avais dit. Les gars du Norvégien. Couche-les, pis pars.", 3,
               jeu="[coldly] Je te l'avais dit. Les gars du Norvégien. [firmly] Couche-les, pis pars."),
            _p("josee", "Reviens par l'eau. Personne suit une chaloupe, la nuit.", 4,
               jeu="[calm] Reviens par l'eau. [matter-of-fact] Personne suit une chaloupe, la nuit."),
            _p("josee", "Entre. On l'ouvre ensemble.", 5,
               jeu="[quietly] Entre. [warmly] On l'ouvre ensemble.")
        ],
        "fin": [
            _l("josee", "Mille deux cents piastres, pis une photo. Ton oncle, jeune, devant son garage neuf.",
               jeu="[quietly] Mille deux cents piastres, pis une photo. [softly] Ton oncle, jeune, devant son garage neuf."),
            _l("josee", "L'argent est à toi. La photo aussi. Rocco savait où il les laissait.",
               jeu="[matter-of-fact] L'argent est à toi. La photo aussi. [knowingly] Rocco savait où il les laissait.")
        ],
        "echec": [
            _l("josee", "Les matelots ont la cache. L'héritage de ton oncle part chez le Norvégien.",
               jeu="[coldly] Les matelots ont la cache. [bitterly] L'héritage de ton oncle part chez le Norvégien.")
        ]
    }
}
