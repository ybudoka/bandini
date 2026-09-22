"""La mission m52 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m52",
    "titre": "Le repérage",
    "donneur": "sven",
    "prerequis": ["m6"],
    "recompense": 350,
    "echec": ["mort", "arrete", "vehicule_detruit", "etoile"],
    "donne": {"message": "SVEN T'A À L'ŒIL"},

    # ⚠️ **Le premier acte n'utilise pas encore le piratage** (Martin, 21 sept. 2026 : « de
    # l'infiltration et du hacking ») : Sven vérifie d'abord qu'on sait se taire avant de
    # confier un terminal à quelqu'un. La chaloupe amarrée le plus près de son
    # porte-conteneurs (`amarrage:sven`) n'est à personne — c'est celle qu'il prête.
    "objectifs": [
        {"type": "monter", "texte": "PRENDS LA CHALOUPE, PRÈS DU QUAI DE SVEN",
         "vehicule": "bateau", "ou": "amarrage:sven", "prete": "sven"},

        {"type": "survivre", "texte": "PATROUILLE LA BAIE SANS TE FAIRE VOIR — 45 S",
         "secondes": 45, "sans_etoile": True},

        {"type": "tuer", "texte": "UN GUETTEUR DES MORUES T'A REPÉRÉ — COUCHE-LE",
         "groupe": "morues", "n": 1, "ou": "amarrage:sven"},

        {"type": "livrer", "texte": "RAMÈNE LA CHALOUPE AU QUAI DE SVEN, INTACTE",
         "lieu": "mouillage:porte_conteneurs", "rayon": 6, "sans_degats": True},

        {"type": "retourner", "texte": "RETOURNE VOIR SVEN"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Sven, le repérage : une précision froide, des phrases
    # courtes, jamais un mot de trop. Pas de colère, jamais de familiarité — l'arc va du calcul
    # (l'appel) à une satisfaction sèche (la fin), et l'échec ne hausse même pas le ton.
    "dialogue": {
        "appel": [
            _l("sven", "Sven. J'ai du travail pour quelqu'un de discret. Le quai, ce soir.",
               jeu="[Norwegian accent][calm] Sven. [matter-of-fact] J'ai du travail pour quelqu'un de discret… [firmly] le quai, ce soir.")
        ],
        "intro": [
            _l("sven", "Une chaloupe t'attend. Fais le tour de la baie, sans bruit, sans lumière.",
               jeu="[Norwegian accent][quietly] Une chaloupe t'attend. [firmly] Fais le tour de la baie… sans bruit, sans lumière."),
            _l("sven", "Josée regarde son port de trop près. Je veux savoir qui regarde, et quand.",
               jeu="[Norwegian accent][coldly] Josée regarde son port de trop près. [calm] Je veux savoir qui regarde… et quand.")
        ],
        "pendant": [
            _p("sven", "Lentement. Un moteur trop pressé s'entend de loin.", 1,
               jeu="[Norwegian accent][gravely] Lentement. [quietly] Un moteur trop pressé… s'entend de loin."),
            _p("sven", "Quelqu'un t'a vu. Règle ça vite, et sans un mot.", 2,
               jeu="[Norwegian accent][dramatic] Quelqu'un t'a vu. [firmly] Règle ça vite… et sans un mot.")
        ],
        "fin": [
            _l("sven", "Parfait. C'est tout ce que je demande.",
               jeu="[Norwegian accent][satisfied] Parfait. [calm] C'est tout ce que je demande."),
            _l("sven", "Tiens. La prochaine fois, le travail sera moins tranquille.",
               jeu="[Norwegian accent][deadpan] Tiens. [knowingly] La prochaine fois… le travail sera moins tranquille.")
        ],
        "echec": [
            _l("sven", "Tu n'étais pas prêt. Reviens quand tu le seras.",
               jeu="[Norwegian accent][coldly] Tu n'étais pas prêt. [firmly] Reviens… quand tu le seras.")
        ]
    }

    # ⚠️ ELLE N'ÉCRIT AUCUNE SCÈNE : `scene_par_defaut` montre déjà la chaloupe (le premier
    # objectif nomme `amarrage:sven`) et referme chez Sven, qui reprend/donne — les deux
    # formes que `lieu_a_montrer`/`fin_chez_le_donneur` déduisent sans un mot de plus ici.
}
