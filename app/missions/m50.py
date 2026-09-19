"""La mission m50 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m50",
    "titre": "Le Cargo de Minuit",
    "donneur": "marco",
    "prerequis": ["m49"],
    "recompense": 450,
    "phase": 1,
    "echec": ["mort", "arrete"],
    "donne": {"message": "LE PORT À MINUIT"},

    "objectifs": [
        { "type": "aller", "texte": "ALLER AU CARGO DES QUAIS",
          "lieu": "cargo", "rayon": 4, "nuit": True },

        { "type": "parler", "texte": "PARLER AU GARDE DU CARGO",
          "cible": "gardien" },

        { "type": "ramasser", "texte": "RAMASSER LE COLIS SUR LE QUAI",
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
            _p("marco", "Le cargo est là. Bouge pas trop les lumières.", 0),
            _p("marco", "Parle au garde, il sait quoi faire.", 1),
            _p("marco", "Le docker va essayer de filer. Rattrape-le!", 2),
            _p("marco", "Ramène ça au garage, vite.", 3)
        ],
        "client": [],
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
