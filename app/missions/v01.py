"""La mission v01 — voir app/missions/__init__.py pour le moteur.

La première des trois infiltrations de la villa du maire (`app/blocs/villa.py`,
docs/jalons/infiltration-portes-verrouillees-et-gardes-prives.md) : on n'y entre pas encore, on
vole la clé. Le garde du jardin fait le tour de la maison, la clé de la porte de service dans la
poche ; on la lui prend PAR-DERRIÈRE (`obtenir`, `garde`), et on ressort comme on est venu.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "v01",
    "titre": "La clé du maire",
    "donneur": "josee",
    "prerequis": ["q04"],
    "recompense": 500,
    "echec": ["mort", "arrete", "etoile"],
    "donne": {"message": "LA CLÉ DE LA PORTE DE SERVICE, DANS TA POCHE"},

    # ⚠️ Toute la mission est `sans_etoile` une fois à la villa : un garde qui te reconnaît donne
    # l'alerte (une étoile, `Police.garder`), et c'est raté. La clé RESTE dans le sac à la fin : elle
    # ouvre la porte de service pour de bon (v02, v03) — une vraie clé ne se dépense pas.
    # ⚠️ `ou: villa_chemin` sur `obtenir` ne pose rien : l'objet est dans la poche du garde. Il dit
    # seulement où le chercher — en ville, la flèche vise le passage du bloc ; dans la villa, le garde.
    "objectifs": [
        {"type": "aller", "texte": "VA À LA VILLA DU MAIRE, DE NUIT",
         "lieu": "villa_chemin", "rayon": 6, "nuit": True},

        {"type": "obtenir", "texte": "VOLE LA CLÉ DU GARDE : ACTION DANS SON DOS, SANS ÊTRE VU",
         "objet": "cle_villa", "nom": "LA CLÉ DE LA PORTE DE SERVICE", "dessin": "cle",
         "garde": "jardin", "ou": "villa_chemin", "sans_etoile": True},

        {"type": "aller", "texte": "RESSORS PAR LE CHEMIN, SANS TE FAIRE VOIR",
         "lieu": "villa_chemin", "rayon": 3, "sans_etoile": True},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Josée : la Chef qui prépare un coup de loin. Rien de pressé,
    # rien d'expliqué de trop : elle veut une clé, pas une histoire. Le « pourquoi » reste dans sa poche,
    # comme la clé dans celle du garde — une seule phrase de mystère, et un `[warmly]`, à la fin.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. J'ai besoin d'une clé que personne doit savoir perdue.",
               jeu="[calm] Josée. [mysteriously] J'ai besoin d'une clé… que personne doit savoir perdue.")
        ],
        "intro": [
            _l("josee", "Le maire Tanguay a une villa au bout des Érables. Gardée comme une banque, la nuit.",
               jeu="[matter-of-fact] Le maire Tanguay a une villa au bout des Érables. [coldly] Gardée comme une banque, la nuit."),
            _l("josee", "Le garde du jardin porte la clé de la porte de service. Je la veux, sans qu'il sache qu'elle est partie.",
               jeu="[firmly] Le garde du jardin porte la clé de la porte de service. [quietly] Je la veux, sans qu'il sache qu'elle est partie."),
            _l("josee", "Pas de bagarre, pas d'étoile. Un garde qui te voit, pis le maire change ses serrures.",
               jeu="[serious] Pas de bagarre, pas d'étoile. [menacingly] Un garde qui te voit… pis le maire change ses serrures.")
        ],
        # ⚠️ LE MODE D'EMPLOI DU VOL, AU COMBINÉ (Martin, 29 sept. 2026 : « ajoute cette explication en
        # vocal dans le jeu ») : Josée le dit quand on arrive sur le chemin — la ville est figée tant qu'elle
        # parle, le garde n'avance pas. Ce qu'elle dit, c'est ce que le banc a montré : le trou au nord
        # (`blocs/villa.py`, la grille a son garde), le chemin public derrière la palissade, le garde qui se
        # TOURNE à chaque coin, le vol DANS LE DOS (`Combat.pochesAPrendre`), le « ? » avant l'alerte.
        # ⚠️ Un slug de voix se compte à sa place : la dernière réplique (l'objectif 2) a gardé sa voix,
        # renommée de `-9` à `-13`.
        "pendant": [
            _p("josee", "Passe pas par la grille, elle a son garde. Fais le tour : au nord, il manque une planche à la palissade.", 1,
               jeu="[quietly] Passe pas par la grille… elle a son garde. [matter-of-fact] Fais le tour : au nord, il manque une planche à la palissade."),
            _p("josee", "Attends dehors, collé sur la palissade. Tant que t'es pas sur son terrain, il a rien à te dire.", 1,
               jeu="[calm] Attends dehors, collé sur la palissade. [coldly] Tant que t'es pas sur son terrain… il a rien à te dire."),
            _p("josee", "Celui du jardin fait le tour de la maison. À chaque coin, il s'arrête, pis il se retourne.", 1,
               jeu="[matter-of-fact] Celui du jardin fait le tour de la maison. [gravely] À chaque coin… il s'arrête, pis il se retourne."),
            _p("josee", "Suis-le dans une longue ligne droite, loin des coins. Colle-toi dans son dos, pis sers-toi dans sa poche.", 1,
               jeu="[quietly] Suis-le dans une longue ligne droite… loin des coins. [mischievously] Colle-toi dans son dos, pis sers-toi dans sa poche."),
            _p("josee", "Ils ont des lampes de poche. S'il regarde de ton bord, recule dans le noir. Tout de suite.", 1,
               jeu="[serious] Ils ont des lampes de poche. [firmly] S'il regarde de ton bord, recule dans le noir. Tout de suite."),
            _p("josee", "La clé est à toi. Sors par où t'es entré, pas plus vite qu'un chat.", 2,
               jeu="[satisfied] La clé est à toi. [quietly] Sors par où t'es entré… pas plus vite qu'un chat.")
        ],
        "fin": [
            _l("josee", "Une clé, pis personne l'a vue partir. Garde-la, un jour on va entrer chez le maire sans sonner.",
               jeu="[satisfied] Une clé, pis personne l'a vue partir. [mysteriously] Garde-la… un jour on va entrer chez le maire sans sonner."),
            _l("josee", "T'as les mains fines. C'est plus rare que des gros bras.",
               jeu="[warmly] T'as les mains fines. [matter-of-fact] C'est plus rare que des gros bras.")
        ],
        "echec": [
            _l("josee", "Vu. Le maire va doubler ses gardes. Reviens quand tu sauras marcher dans le noir.",
               jeu="[coldly] Vu. [annoyed] Le maire va doubler ses gardes. Reviens quand tu sauras marcher dans le noir.")
        ]
    },

    # Intention (intro) : Josée ne bouge pas de son bar ; la caméra, elle, part voir le bout du chemin
    # des Érables — le panneau VILLA au bord de la ville, là où tout se passera. ⚠️ La coupe part
    # `ensemble` et la voix la retient (forme de q04/m51) : aucune réplique coupée.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "bloc:villa", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [3]},
        ],
    },
}
