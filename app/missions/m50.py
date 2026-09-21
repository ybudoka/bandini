"""La mission m50 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p, _r

MISSION = {
    "slug": "m50",
    "titre": "Le Cargo de Minuit",
    "donneur": "marco",
    "prerequis": ["m5"],
    "recompense": 450,
    "phase": 1,
    "echec": ["mort", "arrete"],
    "donne": {"message": "LE PORT À MINUIT"},

    "objectifs": [
        { "type": "aller", "texte": "ALLER À LA CANTINE DES QUAIS, DE NUIT",
          "lieu": "cantine", "rayon": 4, "nuit": True },

        { "type": "parler", "texte": "PARLER À LULU, À LA CANTINE",
          "cible": "lulu" },

        { "type": "ramasser", "texte": "RATTRAPER LE FUYARD ET SON COLIS",
          "vehicule": "auto", "cible": "fuyard" },

        { "type": "retourner", "texte": "RETOURNER AU GARAGE" }
    ],

    "dialogue": {
        "appel": [
            _l("marco", "Cousin, j’ai une faveur. Passe au port, discret.")
        ],
        "intro": [
            _l("marco", "Un colis arrive ce soir, sur le cargo."),
            _l("marco", "Va le chercher. Personne doit savoir que ça vient de moi.")
        ],
        "pendant": [
            # ⚠️ C'est Lulu qui le crie : elle est à la cantine quand le docker file.
            _p("lulu", "Le docker va essayer de filer. Rattrape-le!", 2)
        ],
        "client": [],
        # ⚠️ Lulu renvoie qui vient trop tôt : de jour, l'objectif 0 attend la noirceur et « parler à
        # Lulu » ne compte pas encore. Sans cette réplique elle disait le texte de repos de tout le
        # monde (« le Faubourg est tranquille »), sans voix, et le joueur ne savait pas quoi attendre.
        "renvoi": [
            _r("lulu", "Le cargo arrive à la noirceur, pas avant. Reviens me voir ce soir.", 0)
        ],
        "fin": [
            _l("marco", "Parfait. Personne t’a vu? Bon."),
            _l("marco", "Tiens, pour le trouble.")
        ],
        "echec": [
            _l("marco", "T’es censé être discret, pas mort.")
        ]
    },

    "scenes": {
        "intro": [
            { "type": "camera", "vers": "porte:garage", "duree": 90 },
            { "type": "marcher", "acteur": "donneur", "vers": "joueur", "duree": 60 },
            { "type": "geste", "acteur": "donneur", "geste": "montrer", "duree": 40 },
            { "type": "dire", "repliques": [1, 2] }
        ],
        "fin": [
            { "type": "marcher", "acteur": "donneur", "vers": "joueur", "duree": 50 },
            { "type": "geste", "acteur": "donneur", "geste": "prendre", "duree": 40 },
            { "type": "dire", "repliques": [1, 2] }
        ]
    }
}
