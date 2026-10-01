"""La mission x01 — voir app/missions/__init__.py pour le moteur.

Le repérage (M16, arc X, _Le coup de la Caisse populaire_, 1er oct. 2026). Le jeudi, un fourgon dépose la paie de
l'usine Prévost à la caisse populaire de La Shop (`caisse.py`, la caisse des ouvriers) ; elle y dort une nuit. Josée
la veut. D'abord, on regarde : la voûte de près (`obtenir`, `table: caisse` — `caisse.js` met le plan dans le sac
quand on a compté ses boulons), puis le fourgon qu'on file jusqu'au casse-croûte de Mado, où ses gars dînent avec
Bouchard. Ouvre les trois autres : le char (x02), le linge (x03), le coup (x04).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "x01",
    "titre": "Repérer la caisse",
    "donneur": "josee",
    "prerequis": ["d06"],
    # Après l'un ou l'autre côté du choix de Sven (q10 ou q11) : la fiche le veut, un prérequis ne dit que « et ».
    "exige": {"une_de": ["q10", "q11"]},
    "recompense": 100,
    "donne": {"message": "LA CAISSE POP EST REPÉRÉE — LE COUP SE PRÉPARE"},

    # ⚠️ Dedans, `majObjectif` dort : le plan entre au sac DANS la caisse (`caisse.js`, le repérage) et l'objectif
    # avance à la sortie. Le fourgon naît alors à la porte, et file au casse-croûte (`suivre`, un lieu de mission
    # qui l'était déjà : la ville ne bouge pas).
    "objectifs": [
        {"type": "aller", "texte": "LA CAISSE POP DE LA SHOP : VA VOIR", "lieu": "caisse_pop", "rayon": 6},

        {"type": "obtenir", "texte": "ENTRE, ET REGARDE LA VOÛTE DE PRÈS",
         "objet": "plan_caisse", "nom": "LA VOÛTE, DE PRÈS", "dessin": "dossier", "ou": "caisse_pop",
         "table": "caisse"},

        {"type": "suivre", "texte": "LE FOURGON DE LA PAIE REPART : SUIS-LE DE LOIN",
         "vehicule": "camion", "lieu": "casse_croute", "proche": 3, "loin": 16},
    ],

    # Intention (intro) : Josée ne bouge pas de son bar ; la caméra part à La Shop voir la façade, sous la deuxième
    # réplique — c'est là que tout se passera. ⚠️ La coupe part `ensemble`, la voix la retient (forme de d07).
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:caisse_pop", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Josée : la Chef qui prépare un coup de loin, comme v01. Pas un mot de
    # trop, pas un de pressé ; la phrase de mystère ouvre (la paie qui « dort »), le seul `[warmly]` ferme.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. La paie de l'usine Prévost dort une nuit par semaine dans une caisse pop. Viens au bar.",
               jeu="[calm] Josée. [mysteriously] La paie de l'usine Prévost dort une nuit par semaine… dans une caisse pop. Viens au bar.")
        ],
        "intro": [
            _l("josee", "Le jeudi, un fourgon dépose la paie de l'usine à la caisse populaire de La Shop. Toute la paie.",
               jeu="[matter-of-fact] Le jeudi, un fourgon dépose la paie de l'usine à la caisse populaire de La Shop. [quietly] Toute la paie."),
            _l("josee", "Va voir. Regarde la voûte, compte les gardes, pis suis le fourgon quand il repart.",
               jeu="[firmly] Va voir. Regarde la voûte, compte les gardes… pis suis le fourgon quand il repart."),
            _l("josee", "Pas d'arme, pas d'étoile. Aujourd'hui, t'es un gars qui vient ouvrir un compte.",
               jeu="[coldly] Pas d'arme, pas d'étoile. [wryly] Aujourd'hui, t'es un gars qui vient ouvrir un compte.")
        ],
        "pendant": [
            _p("josee", "Une caisse de quartier, avec un vigile qui a connu la guerre. Rentre comme un client.", 0,
               jeu="[matter-of-fact] Une caisse de quartier, avec un vigile qui a connu la guerre. [quietly] Rentre comme un client."),
            _p("josee", "La voûte est au fond, derrière les guichets. Approche-toi, pis regarde comment elle ferme.", 1,
               jeu="[quietly] La voûte est au fond, derrière les guichets. [calm] Approche-toi… pis regarde comment elle ferme."),
            _p("josee", "Le fourgon repart. Reste loin : ces gars-là regardent leurs miroirs plus que la route.", 2,
               jeu="[serious] Le fourgon repart. [firmly] Reste loin : ces gars-là regardent leurs miroirs plus que la route.")
        ],
        "fin": [
            _l("josee", "Le casse-croûte de Mado. Ils dînent avec Bouchard pendant que la paie dort dans la voûte.",
               jeu="[knowingly] Le casse-croûte de Mado. [coldly] Ils dînent avec Bouchard… pendant que la paie dort dans la voûte."),
            _l("josee", "Une minuterie d'une minute. Gus va te trouver un char, Rosa un linge que le vigile regarde pas. Bon travail.",
               jeu="[matter-of-fact] Une minuterie d'une minute. Gus va te trouver un char, Rosa un linge que le vigile regarde pas. [warmly] Bon travail.")
        ],
        "echec": [
            _l("josee", "T'as été vu. On attend qu'ils oublient ta face.",
               jeu="[coldly] T'as été vu. [matter-of-fact] On attend qu'ils oublient ta face.")
        ]
    }
}
