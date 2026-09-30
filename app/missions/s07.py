"""La mission s07 — voir app/missions/__init__.py pour le moteur.

Le camion de Prévost (M16, arc S, 30 sept. 2026). La Shop est libre (s11) et Prévost rembauche ; il a signé un
contrat avec un armateur de Rimouski, et un camion de pièces doit être au quai des Quais avant que le cargo largue
les amarres. Ses chauffeurs sont tous au syndicat. Le neveu travaille pour les deux bords — c'est le propos.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "s07",
    "titre": "Le camion de Prévost",
    "donneur": "prevost",
    "prerequis": ["s11"],
    "recompense": 350,
    "donne": {"message": "LE CARGO DE RIMOUSKI EST PARTI À L'HEURE"},

    # ⚠️ L'usine n'est jamais un `lieu` (sa cour ferme la nuit : barrière d'heure) : le camion attend dans sa ruelle
    # (`ou: ruelle:usine:10`, le patron de s05). On le livre devant la cantine, au bord du quai. Prévost est dedans :
    # sa fin passe au combiné.
    "objectifs": [
        {"type": "monter", "texte": "LE CAMION DE PIÈCES, DERRIÈRE L'USINE",
         "vehicule": "camion", "ou": "ruelle:usine:10"},

        {"type": "livrer", "texte": "AU QUAI AVANT LE DÉPART DU CARGO : DEUX MINUTES ET DEMIE",
         "lieu": "cantine", "rayon": 6, "chrono_s": 150},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "ruelle:usine:10", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Prévost : le patron qui a perdu et fait comme s'il avait gagné ; des phrases
    # de conseil d'administration, un sourire en coin sur « les deux bords ».
    "dialogue": {
        "appel": [
            _l("prevost", "Réjean Prévost. J'ai un contrat qui part par bateau, pis mes chauffeurs sont en assemblée syndicale.",
               jeu="[matter-of-fact] Réjean Prévost. [coldly] J'ai un contrat qui part par bateau, pis mes chauffeurs sont en assemblée syndicale.")
        ],
        "intro": [
            _l("prevost", "Un armateur de Rimouski. Des pièces de treuil, six mois de travail pour La Shop.",
               jeu="[matter-of-fact] Un armateur de Rimouski. [smugly] Des pièces de treuil, six mois de travail pour La Shop."),
            _l("prevost", "Le camion est chargé, derrière. Le cargo largue à la marée : deux minutes et demie.",
               jeu="[coldly] Le camion est chargé, derrière. [matter-of-fact] Le cargo largue à la marée : deux minutes et demie."),
            _l("prevost", "Vous avez travaillé contre moi, vous travaillez pour moi. C'est ce qu'on appelle un marché.",
               jeu="[smugly] Vous avez travaillé contre moi, vous travaillez pour moi. [coldly] C'est ce qu'on appelle un marché.")
        ],
        "pendant": [
            _p("prevost", "Les clés sont dessus. Mes camions, je les paie, je ne les verrouille pas.", 0,
               jeu="[matter-of-fact] Les clés sont dessus. [smugly] Mes camions, je les paie, je ne les verrouille pas."),
            _p("prevost", "Le quai des Quais, devant la cantine. Le capitaine attend, et il déteste attendre.", 1,
               jeu="[coldly] Le quai des Quais, devant la cantine. [matter-of-fact] Le capitaine attend, et il déteste attendre.")
        ],
        "fin": [
            _l("prevost", "Le cargo est parti à l'heure. Six mois de paie pour La Shop, grâce à un voleur de chars.",
               jeu="[satisfied] Le cargo est parti à l'heure. [smugly] Six mois de paie pour La Shop, grâce à un voleur de chars."),
            _l("prevost", "Votre enveloppe. Ne la montrez pas à Raymonde, elle croirait que je suis devenu gentil.",
               jeu="[matter-of-fact] Votre enveloppe. [wryly] Ne la montrez pas à Raymonde, elle croirait que je suis devenu gentil.")
        ],
        "echec": [
            _l("prevost", "Le cargo est parti sans mes pièces. Rimouski ne rappellera pas.",
               jeu="[coldly] Le cargo est parti sans mes pièces. [matter-of-fact] Rimouski ne rappellera pas.")
        ]
    }
}
