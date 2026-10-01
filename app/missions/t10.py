"""La mission t10 — voir app/missions/__init__.py pour le moteur.

Le quart commence (M16, arc T, les petites jobs — 1er oct. 2026). Un machiniste de La Shop, son char mort dans la
neige, son quart qui commence : Prévost met dehors ceux qui pointent en retard, il en a déjà mis la moitié de La Shop
(les Boulonneux). Il te suit à pied ou monte avec toi (`proteger`), jusqu'à la porte de l'usine, sous le chrono. Un
passant qui donne une job (`passant`).

⚠️ LA RÈGLE DE L'USINE (`missions.barriere_d_heure`) : la porte de l'usine est derrière la chaîne de sa cour, qui ferme
la nuit — on ne pointe pas pour un quart qu'on ne peut pas atteindre. Cette job ne s'offre que le jour, et prise, elle
tient la chaîne ouverte jusqu'à sa fin.

⚠️ Écart à la fiche : 75 s, pas 45. Il se présente n'importe où dans La Shop, à 7–11 tuiles du joueur : du coin le plus
loin, 228 tuiles à pied jusqu'à l'usine (mesuré sur la ville, 1er oct. 2026), 33 s à l'allure de l'étalon des courses
(110 px/s) — plus le temps de trouver un char et de le faire monter.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t10",
    "titre": "Le quart commence",
    "donneur": "passant",
    "prerequis": ["m6"],
    "recompense": 40,
    "passant": {"archetype": "machiniste", "district": "shop", "nom": "Le machiniste"},
    "donne": {"message": "IL A POINTÉ À L'HEURE"},

    # ⚠️ `proteger` : il est déjà là (le passant qui hèle), il te suit ou monte ; la fin se dit devant lui, à l'usine.
    "objectifs": [
        {"type": "proteger", "texte": "AMÈNE LE MACHINISTE À L'USINE — SON QUART COMMENCE", "cible": "passant",
         "lieu": "usine", "rayon": 5, "chrono_s": 75},
    ],

    # Le jeu (`jeu=`) — le machiniste : vingt ans de quarts, et la peur toute neuve de finir comme les autres ; il
    # compte les secondes à voix haute. Il ne dit pas son nom.
    "dialogue": {
        "hele": [
            _l("passant", "Le jeune! Vite!", jeu="[nervously] Le jeune! Vite!")
        ],
        "intro": [
            _l("passant", "Mon char est mort dans le banc de neige, pis mon quart commence dans une minute.",
               jeu="[nervously] Mon char est mort dans le banc de neige, [worried] pis mon quart commence dans une minute."),
            _l("passant", "Prévost met dehors ceux qui pointent en retard. La moitié de la rue est Boulonneux à cause de ça.",
               jeu="[gravely] Prévost met dehors ceux qui pointent en retard. [bitterly] La moitié de la rue est Boulonneux à cause de ça.")
        ],
        "pendant": [
            _p("passant", "Pèse dessus! Je pointe, ou je deviens un gars de ruelle!", 0,
               jeu="[shouting] Pèse dessus! [worried] Je pointe, ou je deviens un gars de ruelle!")
        ],
        "fin": [
            _l("passant", "Pointé à la seconde! Tiens, quarante piasses. Prévost saura jamais qu'il a failli me perdre.",
               jeu="[relieved] Pointé à la seconde! [cheerful] Tiens, quarante piasses. [smugly] Prévost saura jamais qu'il a failli me perdre.")
        ],
        "echec": [
            _l("passant", "C'est fait. Bon ben, je vais aller voir si les Boulonneux engagent.",
               jeu="[disappointed] C'est fait. [sarcastic] Bon ben, je vais aller voir si les Boulonneux engagent.")
        ]
    }
}
