"""La mission s10 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "s10",
    "titre": "Raymonde négocie",
    "donneur": "raymonde",
    "prerequis": ["s06"],
    "recompense": 300,
    "donne": {"message": "LE MAIRE A ENTENDU RAYMONDE"},

    # Raymonde va voir le maire — qui dort à l'Hôtel Bandini, pas à sa villa (e06) — pour qu'il force Prévost à
    # négocier. On la mène (`proteger`, le patron de p14) ; arrivés, deux gardiens de Prévost qui la suivaient
    # arrivent sur nous (`pieton: gardien`, les hommes du lot : Prévost les loue). La fiche disait « la villa, et
    # retour » : un `lieu` de bloc ne se rejoint pas avec quelqu'un qui te suit, et l'usine n'est jamais un `lieu`.
    "objectifs": [
        {"type": "proteger", "texte": "MÈNE RAYMONDE À L'HÔTEL, OÙ DORT LE MAIRE",
         "cible": "raymonde", "lieu": "hotel", "rayon": 5},

        {"type": "tuer", "texte": "LES GARDIENS DE PRÉVOST L'ONT SUIVIE — COUCHE-LES",
         "groupe": "boulonneux", "pieton": "gardien", "n": 2, "ou": "donneur", "loin": 10},
    ],

    # La fin se dit devant elle : elle vient à nous, sur le trottoir de l'hôtel.
    "scenes": {
        "fin": [
            {"type": "marcher", "acteur": "donneur", "vers": "joueur", "pres": 22, "duree": 50},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Raymonde : elle s'habille pour négocier, et elle a peur pour la première
    # fois, sans le dire. Elle parle plus que d'habitude sur le trajet ; ça s'entend.
    "dialogue": {
        "appel": [
            _l("raymonde", "Raymonde, du syndicat. Je vais voir le maire ce soir. Prévost a des hommes qui me suivent.",
               jeu="[firmly] Raymonde, du syndicat. [serious] Je vais voir le maire ce soir. [quietly] Prévost a des hommes qui me suivent.")
        ],
        "intro": [
            _l("raymonde", "Le maire dort à l'hôtel, tout le monde le sait astheure. Il va m'écouter, en robe de chambre.",
               jeu="[wryly] Le maire dort à l'hôtel, tout le monde le sait astheure. [amused] Il va m'écouter, en robe de chambre."),
            _l("raymonde", "Marche avec moi. Si les hommes de Prévost s'approchent, t'occupes-toi d'eux.",
               jeu="[firmly] Marche avec moi. [serious] Si les hommes de Prévost s'approchent… t'occupes-toi d'eux.")
        ],
        "pendant": [
            _p("raymonde", "Trente ans d'usine, pis j'ai jamais marché aussi loin pour parler à un maire.", 0,
               jeu="[wryly] Trente ans d'usine… [bitterly] pis j'ai jamais marché aussi loin pour parler à un maire."),
            _p("raymonde", "Les v'là, ses gardiens. Laisse-moi pas toute seule avec eux.", 1,
               jeu="[nervously] Les v'là, ses gardiens. [firmly] Laisse-moi pas toute seule avec eux.")
        ],
        "fin": [
            _l("raymonde", "Le maire m'a reçue en pantoufles. Il va appeler Prévost demain matin.",
               jeu="[amused] Le maire m'a reçue en pantoufles. [satisfied] Il va appeler Prévost demain matin."),
            _l("raymonde", "Merci d'être venu. Mes gars le sauront.",
               jeu="[warmly] Merci d'être venu. [firmly] Mes gars le sauront.")
        ],
        "echec": [
            _l("raymonde", "Ils m'ont eue. Le maire va dormir tranquille, lui.",
               jeu="[bitterly] Ils m'ont eue. [somber] Le maire va dormir tranquille, lui.")
        ]
    }
}
