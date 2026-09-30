"""La mission d01 — voir app/missions/__init__.py pour le moteur.

Le barbier (M16, arc D — la dette de Rocco, 30 sept. 2026). La dette court depuis la première nuit
(`economie.DETTE` : quinze mille, 2 % par nuit, les rappels, puis ses hommes) ; ici, elle prend un visage. Sal
Ferraro coupe les cheveux au milieu du terminus : il te fait asseoir, te fait la barbe en te racontant ce que ton
oncle lui devait, puis il veut voir sa garantie — le garage de Rocco. On l'y mène (`proteger`, le patron de s10) :
il le regarde comme on regarde un char qu'on va acheter.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "d01",
    "titre": "Le barbier",
    "donneur": "sal",
    "prerequis": ["m6"],
    "recompense": 100,
    "donne": {"message": "SAL T'A À L'ŒIL"},

    # ⚠️ `proteger` d'un donneur DEDANS (`point:sal`) : on sort, il est posé à la porte du terminus et suit tout de
    # suite (le vieux maître, c05). Le garage est déjà un lieu de mission (Marco, m1) : rien ne bouge. La fin se dit
    # devant lui, sur le trottoir du garage — il vient à nous (s10).
    "objectifs": [
        {"type": "proteger", "texte": "SAL VEUT VOIR SA GARANTIE : MÈNE-LE AU GARAGE",
         "cible": "sal", "lieu": "garage", "rayon": 5},
    ],

    # Intention (intro) : Sal parle en coupant les cheveux — un geste, puis chaque réplique tient la scène (la voix
    # retient le plan ; l'intro par défaut les disait en `ensemble`, et la suivante coupait la première).
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "porte:garage", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "marcher", "acteur": "donneur", "vers": "joueur", "pres": 22, "duree": 50},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "porte:garage", "duree": 70,
             "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Sal : la douceur de qui n'a jamais eu besoin d'élever la voix. Il parle
    # bas, lentement, en coupant les cheveux ; il appelle le joueur « le neveu », et la menace ne se dit jamais, elle
    # se sous-entend. L'arc : l'hospitalité (l'appel, le fauteuil), les affaires (le compte), l'œil du prêteur (le
    # garage) — et un sourire qui ne réchauffe rien.
    "dialogue": {
        "appel": [
            _l("sal", "Salut, le neveu. Sal Ferraro, le barbier du terminus. Ton oncle pis moi, on avait un compte.",
               jeu="[warmly] Salut, le neveu. Sal Ferraro, le barbier du terminus. [quietly] Ton oncle pis moi, on avait un compte.")
        ],
        "intro": [
            _l("sal", "Assis-toi. Une coupe, c'est gratis pour la famille. Le reste, par exemple, ça se paie.",
               jeu="[warmly] Assis-toi. Une coupe, c'est gratis pour la famille. [softly] Le reste, par exemple… ça se paie."),
            _l("sal", "Rocco me devait quinze mille piasses. Il est parti, mais le compte, lui, est resté icitte.",
               jeu="[calm] Rocco me devait quinze mille piasses. [knowingly] Il est parti… mais le compte, lui, est resté icitte."),
            _l("sal", "Il m'avait mis son garage en garantie. Viens me le montrer, j'aime savoir ce qui m'appartient.",
               jeu="[matter-of-fact] Il m'avait mis son garage en garantie. [smugly] Viens me le montrer… j'aime savoir ce qui m'appartient.")
        ],
        "pendant": [
            _p("sal", "Marche pas trop vite, le neveu. À mon âge, on court juste après l'argent.", 0,
               jeu="[amused] Marche pas trop vite, le neveu. [wryly] À mon âge, on court juste après l'argent.")
        ],
        "fin": [
            _l("sal", "Belle bâtisse. Ton oncle avait du goût pour les affaires qu'il payait pas.",
               jeu="[impressed] Belle bâtisse. [wryly] Ton oncle avait du goût… pour les affaires qu'il payait pas."),
            _l("sal", "Tant que tu paies, le garage reste à ton nom. Mes hommes passent chaque semaine, tu les connais.",
               jeu="[calm] Tant que tu paies, le garage reste à ton nom. [menacingly] Mes hommes passent chaque semaine… tu les connais."),
            _l("sal", "Tiens, pour le taxi. Reviens me voir quand t'auras envie de travailler ta dette.",
               jeu="[warmly] Tiens, pour le taxi. [knowingly] Reviens me voir quand t'auras envie de travailler ta dette.")
        ],
        "echec": [
            _l("sal", "Tu m'as laissé tomber en chemin, le neveu. Rocco aussi me faisait ça. Regarde où il est.",
               jeu="[disappointed] Tu m'as laissé tomber en chemin, le neveu. [coldly] Rocco aussi me faisait ça. Regarde où il est.")
        ]
    }
}
