"""La mission d08 — voir app/missions/__init__.py pour le moteur.

La dernière coupe (M16, arc D, 30 sept. 2026) — l'autre côté du CHOIX de l'arc (`ferme: d07`). On a tout payé
(`exige.dette: 0`) : les quinze mille de Rocco, jusqu'au dernier vingt. Sal appelle — pas pour de l'argent. Il
coupe les cheveux du neveu, gratis, puis il veut voir où dormait son vieil ami (la planque), et lever un verre à
lui au Brouillard. Au bout, il sort de sa poche la bague de Rocco, qu'il gardait en gage depuis dix ans.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "d08",
    "titre": "La dernière coupe",
    "donneur": "sal",
    "prerequis": ["d06"],
    "exige": {"dette": 0},
    "ferme": "d07",
    "recompense": 95,
    "donne": {"message": "LA BAGUE DE ROCCO, À TON DOIGT"},

    # ⚠️ Sal est DEDANS (`point:sal`) : `proteger` le pose à la porte du terminus, et il nous suit toute la mission
    # (le patron de d01). Un seul `proteger` : le second le reposerait « chez lui » à la planque. La fin se dit
    # devant lui, à la porte du bar.
    "objectifs": [
        {"type": "proteger", "texte": "SAL VEUT VOIR OÙ DORMAIT ROCCO : À LA PLANQUE",
         "cible": "sal", "lieu": "planque", "rayon": 5},

        {"type": "aller", "texte": "UN VERRE À ROCCO, AU BROUILLARD", "lieu": "bar", "rayon": 6},
    ],

    # Intention (intro) : la coupe elle-même — Sal derrière la chaise, les ciseaux qui parlent pour lui ; puis la
    # coupe vers la planque. La fin, devant le Brouillard : il vient à nous, montre la porte, et la bague.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "porte:planque", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "marcher", "acteur": "donneur", "vers": "joueur", "pres": 22, "duree": 50},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "porte:bar", "duree": 70,
             "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Sal : pour une fois, pas un prêteur. La douceur est la même, mais elle ne
    # cache plus rien ; il parle de Rocco comme d'un frère qu'on engueulait. Pas un chiffre rond, jamais.
    "dialogue": {
        "appel": [
            _l("sal", "Ici Sal. Ton livre est fermé, le neveu. Passe au terminus, la chaise t'attend.",
               jeu="[warmly] Ici Sal. [softly] Ton livre est fermé, le neveu. Passe au terminus, la chaise t'attend.")
        ],
        "intro": [
            _l("sal", "Assis-toi. Aujourd'hui, c'est une vraie coupe. Pas de compte à la fin.",
               jeu="[warmly] Assis-toi. [softly] Aujourd'hui, c'est une vraie coupe. Pas de compte à la fin."),
            _l("sal", "Rocco venait icitte tous les samedis. Il payait jamais, pis il parlait tout le long.",
               jeu="[amused] Rocco venait icitte tous les samedis. [tenderly] Il payait jamais, pis il parlait tout le long."),
            _l("sal", "Montre-moi où il dormait. Pis après, on lève un verre à lui, chez la Chef.",
               jeu="[quietly] Montre-moi où il dormait. [warmly] Pis après, on lève un verre à lui, chez la Chef.")
        ],
        "pendant": [
            _p("sal", "Marche pas trop vite. Aujourd'hui, j'ai pas de rendez-vous.", 0,
               jeu="[calm] Marche pas trop vite. [amused] Aujourd'hui, j'ai pas de rendez-vous."),
            _p("sal", "Un lit, un coffre pis une garde-robe. Il est mort comme il a vécu, le vieux : léger.", 1,
               jeu="[softly] Un lit, un coffre pis une garde-robe. [tenderly] Il est mort comme il a vécu, le vieux : léger.")
        ],
        "fin": [
            _l("sal", "Tiens. La bague de Rocco. Il me l'avait laissée en gage, y a dix ans.",
               jeu="[softly] Tiens. La bague de Rocco. [quietly] Il me l'avait laissée en gage, y a dix ans."),
            _l("sal", "La dette est payée. Le gage retourne à la famille, c'est la règle.",
               jeu="[warmly] La dette est payée. [calm] Le gage retourne à la famille, c'est la règle."),
            _l("sal", "Pis si tu veux une coupe, le neveu, la chaise est libre. Gratis, pour toujours.",
               jeu="[warmly] Pis si tu veux une coupe, le neveu, la chaise est libre. [amused] Gratis, pour toujours.")
        ],
        "echec": [
            _l("sal", "On se reprendra, le neveu. Les morts sont patients, pis moi aussi.",
               jeu="[somber] On se reprendra, le neveu. [softly] Les morts sont patients, pis moi aussi.")
        ]
    }
}
