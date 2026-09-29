"""La mission s02 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "s02",
    "titre": "La ferraille de Ti-Loup",
    "donneur": "tiloup",
    # ⚠️ Après s01 et pas m6 : c'est Gilles qui te présente Ti-Loup, et il n'est devant la fourrière qu'après
    # (`arrive_apres` : un personnage posé dès l'ouverture décalerait les identifiants de la ville).
    "prerequis": ["s01"],
    "recompense": 250,
    "donne": {"message": "TI-LOUP ACHÈTE TES ÉPAVES"},

    # Sa remorqueuse dort devant la fourrière (`monter`) ; trois épaves remorquées au lot (`boulots`, la sorte
    # `remorquage` — le klaxon trouve le contrat), c'est lui qui les compacte.
    "objectifs": [
        {"type": "monter", "texte": "PRENDS LA REMORQUEUSE DE TI-LOUP", "vehicule": "remorqueuse", "ou": "porte:fourriere"},

        {"type": "boulots", "texte": "TROIS ÉPAVES AU LOT — KLAXONNE POUR UN CONTRAT",
         "sorte": "remorquage", "n": 3},

        {"type": "retourner", "texte": "RETOURNE VOIR TI-LOUP, À LA FOURRIÈRE"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Ti-Loup : le ferrailleur qui ne pose pas de questions, et qui en répond
    # encore moins. Il parle de tôle comme d'autres parlent de vin ; il rit rarement, et toujours de quelqu'un.
    "dialogue": {
        "appel": [
            _l("tiloup", "Ti-Loup, la ferraille. Gilles dit que tu conduis sans poser de questions. J'aime ça.",
               jeu="[gruffly] Ti-Loup, la ferraille. [knowingly] Gilles dit que tu conduis sans poser de questions… J'aime ça.")
        ],
        "intro": [
            _l("tiloup", "Trois carcasses traînent en ville. Moi, j'en fais des cubes, pis les cubes, ça se vend.",
               jeu="[matter-of-fact] Trois carcasses traînent en ville. [wryly] Moi, j'en fais des cubes… pis les cubes, ça se vend."),
            _l("tiloup", "Prends ma remorqueuse. Klaxonne, le répartiteur te donne une adresse.",
               jeu="[casually] Prends ma remorqueuse. [firmly] Klaxonne, le répartiteur te donne une adresse."),
            _l("tiloup", "À qui elles sont? Ça me regarde pas. Ça te regarde pas non plus.",
               jeu="[deadpan] À qui elles sont? Ça me regarde pas. [coldly] Ça te regarde pas non plus.")
        ],
        "pendant": [
            _p("tiloup", "Klaxonne. Une épave, c'est comme un client : ça attend pas.", 1,
               jeu="[gruffly] Klaxonne. [wryly] Une épave, c'est comme un client : ça attend pas."),
            _p("tiloup", "Trois. Reviens, j'ai de l'argent qui sent l'huile.", 2,
               jeu="[satisfied] Trois. [amused] Reviens… j'ai de l'argent qui sent l'huile.")
        ],
        "fin": [
            _l("tiloup", "Trois cubes. Du beau métal, pas une question. On va bien s'entendre, toi pis moi.",
               jeu="[satisfied] Trois cubes. Du beau métal, pas une question. [warmly] On va bien s'entendre, toi pis moi."),
            _l("tiloup", "Gros-Boulon veut te parler. Les gars de l'usine, ceux que Prévost a mis dehors.",
               jeu="[quietly] Gros-Boulon veut te parler. [serious] Les gars de l'usine… ceux que Prévost a mis dehors.")
        ],
        "echec": [
            _l("tiloup", "Pas de tôle, pas d'argent. C'est simple, la tôle.",
               jeu="[coldly] Pas de tôle, pas d'argent. [deadpan] C'est simple, la tôle.")
        ]
    }
}
