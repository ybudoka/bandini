"""La mission q09 — voir app/missions/__init__.py pour le moteur.

La course des débardeurs (M16, arc Q, 30 sept. 2026). Le vendredi, après la paie, les débardeurs font la course
autour des Quais en camion — le perdant paie la bière. Gégé veut voir si le neveu tient la route : trois points,
dans l'ordre, deux minutes et demie, avec un camion de la cantine.

⚠️ La fiche voulait la course `contre` deux débardeurs : `contre` n'est lu par personne (p04 et e04 l'ont vu) ; c'est
une course contre la montre, le temps que les débardeurs ont fait l'an passé.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "q09",
    "titre": "La course des débardeurs",
    "donneur": "gege",
    "prerequis": ["q03"],
    "recompense": 300,
    "donne": {"message": "LES DÉBARDEURS TE PAIENT LA BIÈRE"},

    # ⚠️ Des points que `Histoire.resoudre` connaît et qui sont déjà des lieux de mission (l'hôtel, le coin des Morues,
    # la cantine) : la ville ne glisse pas. La course finit à la cantine, où Gégé se tient : la fin se dit devant lui
    # (`retourner`, dans la même image).
    "objectifs": [
        {"type": "monter", "texte": "LE CAMION DE LA CANTINE, DERRIÈRE", "vehicule": "camion", "ou": "ruelle:cantine:12"},

        {"type": "course", "texte": "L'HÔTEL, LES MORUES, LA CANTINE : DEUX MINUTES ET DEMIE",
         "points": ["hotel", "zone:morues", "cantine"], "rayon": 4, "chrono_s": 150},

        {"type": "retourner", "texte": "GÉGÉ A CHRONOMÉTRÉ : VA LE VOIR"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "porte:hotel", "duree": 70,
             "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    "dialogue": {
        "appel": [
            _l("gege", "Gégé, des débardeurs. Vendredi, c'est la course des camions. Les gars veulent te voir chauffer.",
               jeu="[firmly] Gégé, des débardeurs. Vendredi, c'est la course des camions. [amused] Les gars veulent te voir chauffer.")
        ],
        "intro": [
            _l("gege", "Le perdant paie la bière. Ça fait trois ans que c'est moi, ça va faire.",
               jeu="[gruffly] Le perdant paie la bière. [amused] Ça fait trois ans que c'est moi, ça va faire."),
            _l("gege", "L'hôtel, le coin des Morues, pis la cantine. Dans l'ordre, en camion.",
               jeu="[firmly] L'hôtel, le coin des Morues, pis la cantine. [matter-of-fact] Dans l'ordre, en camion."),
            _l("gege", "Deux minutes et demie, c'est le record des gars. Bats-le, pis la bière est pour eux.",
               jeu="[matter-of-fact] Deux minutes et demie, c'est le record des gars. [amused] Bats-le, pis la bière est pour eux.")
        ],
        "pendant": [
            _p("gege", "Le camion de la cantine, derrière. Lulu le prête, elle le sait pas.", 0,
               jeu="[matter-of-fact] Le camion de la cantine, derrière. [amused] Lulu le prête, elle le sait pas."),
            _p("gege", "Go! Pis ménage les freins, c'est des freins de syndicat.", 1,
               jeu="[shouting] Go! [amused] Pis ménage les freins, c'est des freins de syndicat."),
            _p("gege", "Arrêté! Viens voir le chrono, les gars en reviennent pas.", 2,
               jeu="[excited] Arrêté! [amused] Viens voir le chrono, les gars en reviennent pas.")
        ],
        "fin": [
            _l("gege", "Record battu. Les gars paient la bière, pis ils chialent déjà.",
               jeu="[satisfied] Record battu. [amused] Les gars paient la bière, pis ils chialent déjà."),
            _l("gege", "T'es un débardeur honoraire, astheure. Ça donne rien, mais c'est un honneur.",
               jeu="[firmly] T'es un débardeur honoraire, astheure. [wryly] Ça donne rien, mais c'est un honneur.")
        ],
        "echec": [
            _l("gege", "Trop lent. C'est toi qui paies la bière, astheure.",
               jeu="[amused] Trop lent. [firmly] C'est toi qui paies la bière, astheure.")
        ]
    }
}
