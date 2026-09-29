"""La mission c01 — voir app/missions/__init__.py pour le moteur.

La première du Petit-Canton (docs/jalons/le-quartier-chinois.md, étape 3 ; docs/jalons/le-casino-du-petit-canton.md,
vague 4). Irène Lam, trente ans croupière au Dragon d'or, t'envoie prendre un jeton de laiton aux rabatteurs du
Pouce Vachon — le jeton qui ouvre la porte du sous-sol, où le Pouce tient sa barbotte aux dés pipés. La porte
(`tripot.PORTE`, une barrière de la grande salle) s'ouvre quand la mission est faite (`apres: c01`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "c01",
    "titre": "La barbotte du Pouce",
    "donneur": "irene",
    "prerequis": ["m6"],
    "recompense": 400,
    "donne": {"message": "LA PORTE DU SOUS-SOL T'EST OUVERTE"},

    # ⚠️ Irène se tient DEDANS (`point:irene`, au bout du bar du Dragon d'or) : ni `retourner` vers elle, ni rien de
    # posé « près du joueur » (la pose relative au joueur, dedans, part au coin de la ville). Les rabatteurs attendent
    # à la porte du terminus (`porte:terminus`, un lieu déjà de mission) ; on revient ensuite au Dragon d'or, par la
    # rue (un `aller` sur le lieu du donneur veut un rayon de six tuiles).
    "objectifs": [
        {"type": "tuer", "texte": "LES RABATTEURS DU POUCE, AU TERMINUS",
         "groupe": "cravates", "n": 2, "ou": "porte:terminus", "arme": "", "vie": 70},

        {"type": "aller", "texte": "RAPPORTE UN JETON AU DRAGON D'OR", "lieu": "nord_casino", "rayon": 6},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Irène : l'aplomb amusé de qui a vu passer trente ans de joueurs, qui
    # gage sur tout et taquine le neveu (« mon pigeon ») ; la colère froide quand elle parle des voisins que le
    # Pouce a plumés ; et, à la fin, le ton d'une professeure qui livre le truc du métier. Elle se nomme à l'appel,
    # une fois, à sa façon : « Madame Lam pour toi ».
    "dialogue": {
        "appel": [
            _l("irene", "Irène Lam, du Dragon d'or. Madame Lam pour toi, tant que tu m'as pas battue au mah-jong.",
               jeu="[amused] Irène Lam, du Dragon d'or. [teasing] Madame Lam pour toi… tant que tu m'as pas battue au mah-jong.")
        ],
        "intro": [
            _l("irene", "Sous nos pieds, le Pouce Vachon tient une barbotte. Il a loué la cave pour entreposer des chaises.",
               jeu="[quietly] Sous nos pieds, le Pouce Vachon tient une barbotte. [wryly] Il a loué la cave pour entreposer des chaises."),
            _l("irene", "Ses dés sont pipés. Le vieux Chan y a laissé sa pension, pis la boulangère son camion.",
               jeu="[bitterly] Ses dés sont pipés. [somber] Le vieux Chan y a laissé sa pension… pis la boulangère son camion."),
            _l("irene", "On y entre avec un jeton de laiton. Ses rabatteurs en ont plein les poches, au terminus.",
               jeu="[knowingly] On y entre avec un jeton de laiton. [firmly] Ses rabatteurs en ont plein les poches, au terminus.")
        ],
        "pendant": [
            _p("irene", "Deux gars en cravate qui offrent des jetons aux perdants de l'autobus. Tu peux pas les manquer.", 0,
               jeu="[wryly] Deux gars en cravate qui offrent des jetons aux perdants de l'autobus. [amused] Tu peux pas les manquer."),
            _p("irene", "Un jeton, c'est assez. Reviens au Dragon d'or, je gage cinq piasses que t'as pas un bleu.", 1,
               jeu="[satisfied] Un jeton, c'est assez. [teasing] Reviens au Dragon d'or… je gage cinq piasses que t'as pas un bleu.")
        ],
        "fin": [
            _l("irene", "Montre le jeton au gros de l'escalier. En bas, joue gros, pis regarde les mains du Pouce.",
               jeu="[knowingly] Montre le jeton au gros de l'escalier. [firmly] En bas, joue gros… pis regarde les mains du Pouce."),
            _l("irene", "Quand ses dés sont plus jaunes que les vrais, c'est de la vieille ivoire pipée. Change de côté, ou crie-le.",
               jeu="[quietly] Quand ses dés sont plus jaunes que les vrais, c'est de la vieille ivoire pipée. [amused] Change de côté… ou crie-le."),
            _l("irene", "Pis perds pas tout. La chance, ça existe pas, y a juste du monde qui sait compter.",
               jeu="[warmly] Pis perds pas tout. [knowingly] La chance, ça existe pas… y a juste du monde qui sait compter.")
        ],
        "echec": [
            _l("irene", "Les rabatteurs courent encore. Pis moi, j'ai perdu cinq piasses sur toi.",
               jeu="[disappointed] Les rabatteurs courent encore. [wryly] Pis moi, j'ai perdu cinq piasses sur toi.")
        ]
    },

    # Intention (intro) : Irène au bout du bar, les bras croisés comme une croupière qui surveille la salle ; elle
    # parle du sous-sol sans le regarder, puis la caméra va voir le terminus, où les rabatteurs attendent l'autobus.
    # ⚠️ La coupe en `ensemble`, PUIS la réplique : c'est la voix qui retient la scène (« caler une scène »).
    # Intention (fin) : la caméra va la voir à sa porte, et elle livre le truc du métier — les dés jaunes.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "porte:terminus", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:irene", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },
}
