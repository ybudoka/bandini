"""Le chapitre de Ti-Loup et Gros-Boulon — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague S). La Shop (vague S) : s02 (Ti-Loup, trois épaves au lot) et s05 (Gros-Boulon, la berline de Prévost au compacteur)
— trois étapes chacune — deviennent deux ACTES : la ferraille mène au chef des Boulonneux. Rien d'ajouté (6 à 7
minutes). s09 (l'explosion, 317 s chez Martin) reste une mission, comme s14 (la casse à Ti-Loup, 373 s).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- Gros-Boulon (qui arrive après s02) est posé entre les deux actes (`arriverApres`) ; le respect des Boulonneux
  (`calme`) vient avec le chapitre, à la fin de l'acte 2, comme à la fin de s05.
- s09 et s14 attendent s05, le dernier acte ; i02 et q15 attendent s02, le premier.
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "ti_loup_et_gros_boulon",
    "titre": "Ti-Loup et Gros-Boulon",
    "donneur": "tiloup",
    "prerequis": ["s01"],
    "remplace": ["s02", "s05"],
    "recompense": 400,
    "donne": {"calme": "boulonneux", "message": "LES BOULONNEUX TE LAISSENT VIVRE"},

    "objectifs": [
        # --- Acte 1 (s02, « La ferraille de Ti-Loup »).
        {"type": "acte", "texte": "ACTE 1 — LA FERRAILLE DE TI-LOUP", "donneur": "tiloup"},  # 0
        {"type": "monter", "texte": "PRENDS LA REMORQUEUSE DE TI-LOUP", "vehicule": "remorqueuse", "ou": "porte:fourriere"},  # 1
        {"type": "boulots", "texte": "TROIS ÉPAVES AU LOT — KLAXONNE POUR UN CONTRAT", "sorte": "remorquage", "n": 3},  # 2
        {"type": "retourner", "texte": "RETOURNE VOIR TI-LOUP, À LA FOURRIÈRE", "donne": {"message": "TI-LOUP ACHÈTE TES ÉPAVES", "prime": 250}},  # 3
        # --- Acte 2 (s05, « Gros-Boulon te parle »).
        {"type": "acte", "texte": "ACTE 2 — GROS-BOULON TE PARLE", "donneur": "boulon"},  # 4
        {"type": "monter", "texte": "VOLE LA BERLINE DE PRÉVOST, DERRIÈRE L'USINE", "vehicule": "luxe", "ou": "ruelle:usine:10"},  # 5
        {"type": "livrer", "texte": "LIVRE-LA AU COMPACTEUR DE TI-LOUP", "lieu": "fourriere", "rayon": 4},  # 6
        {"type": "retourner", "texte": "RETOURNE VOIR GROS-BOULON"},  # 7
    ],

    # s02 — Le jeu de chaque réplique (`jeu=`) — Ti-Loup : le ferrailleur qui ne pose pas de questions, et qui en répond
    # encore moins. Il parle de tôle comme d'autres parlent de vin ; il rit rarement, et toujours de quelqu'un.
    # s05 — Le jeu de chaque réplique (`jeu=`) — Gros-Boulon : un gros homme en colère depuis deux ans, qui a appris à la
    # garder pour les bonnes occasions. Il parle lentement, il cogne les mots. Il ne remercie pas : il paie.
    "dialogue": {
        "appel": [
            _l("tiloup", "Ti-Loup, la ferraille. Gilles dit que tu conduis sans poser de questions. J'aime ça.", jeu="[gruffly] Ti-Loup, la ferraille. [knowingly] Gilles dit que tu conduis sans poser de questions… J'aime ça."),
        ],
        "intro": [
            _l("tiloup", "Trois carcasses traînent en ville. Moi, j'en fais des cubes, pis les cubes, ça se vend.", jeu="[matter-of-fact] Trois carcasses traînent en ville. [wryly] Moi, j'en fais des cubes… pis les cubes, ça se vend."),
            _l("tiloup", "Prends ma remorqueuse. Klaxonne, le répartiteur te donne une adresse.", jeu="[casually] Prends ma remorqueuse. [firmly] Klaxonne, le répartiteur te donne une adresse."),
            _l("tiloup", "À qui elles sont? Ça me regarde pas. Ça te regarde pas non plus.", jeu="[deadpan] À qui elles sont? Ça me regarde pas. [coldly] Ça te regarde pas non plus."),
        ],
        "fin": [
            _l("boulon", "Prévost va chercher sa berline toute la semaine. Moi, je vais dormir.", jeu="[laughs] [satisfied] Prévost va chercher sa berline toute la semaine. [amused] Moi, je vais dormir."),
            _l("boulon", "T'es des nôtres, astheure. Dans La Shop, personne te touche.", jeu="[warmly] T'es des nôtres, astheure. [firmly] Dans La Shop, personne te touche."),
        ],
        "echec": [
            _e("tiloup", "Pas de tôle, pas d'argent. C'est simple, la tôle.", 0, jeu="[coldly] Pas de tôle, pas d'argent. [deadpan] C'est simple, la tôle."),
            _e("boulon", "Sa berline roule encore. Mes gars vont rire de moi.", 4, jeu="[angry] Sa berline roule encore. [bitterly] Mes gars vont rire de moi."),
        ],
        "pendant": [
            _p("tiloup", "Klaxonne. Une épave, c'est comme un client : ça attend pas.", 2, jeu="[gruffly] Klaxonne. [wryly] Une épave, c'est comme un client : ça attend pas."),
            _p("tiloup", "Trois. Reviens, j'ai de l'argent qui sent l'huile.", 3, jeu="[satisfied] Trois. [amused] Reviens… j'ai de l'argent qui sent l'huile."),
            # Acte 2 : la fin de s02, en personne ; puis l'appel et l'intro de s05.
            _p("tiloup", "Trois cubes. Du beau métal, pas une question. On va bien s'entendre, toi pis moi.", 4, jeu="[satisfied] Trois cubes. Du beau métal, pas une question. [warmly] On va bien s'entendre, toi pis moi."),
            _p("tiloup", "Gros-Boulon veut te parler. Les gars de l'usine, ceux que Prévost a mis dehors.", 4, jeu="[quietly] Gros-Boulon veut te parler. [serious] Les gars de l'usine… ceux que Prévost a mis dehors."),
            _p("boulon", "Gros-Boulon, Marcel pour ma mère. Ti-Loup dit que t'es correct, on va voir.", 4, jeu="[gruffly] Gros-Boulon… [wryly] Marcel pour ma mère. [coldly] Ti-Loup dit que t'es correct… on va voir."),
            _p("boulon", "Prévost nous a mis dehors, deux cents gars, un vendredi. Lui, il a gardé sa berline.", 4, jeu="[bitterly] Prévost nous a mis dehors, deux cents gars, un vendredi. [angry] Lui, il a gardé sa berline."),
            _p("boulon", "Elle dort derrière l'usine. Je la veux en cube, chez Ti-Loup.", 4, jeu="[menacingly] Elle dort derrière l'usine. [firmly] Je la veux en cube, chez Ti-Loup."),
            _p("boulon", "Fais ça, pis mes gars vont arrêter de te regarder de travers.", 4, jeu="[calm] Fais ça… [serious] pis mes gars vont arrêter de te regarder de travers."),
            _p("boulon", "Du cuir, pis de l'air climatisé. Payé avec nos paies.", 5, jeu="[bitterly] Du cuir, pis de l'air climatisé. [angry] Payé avec nos paies."),
            _p("boulon", "Au compacteur. Ti-Loup t'attend, la mâchoire ouverte.", 6, jeu="[satisfied] Au compacteur. [amused] Ti-Loup t'attend, la mâchoire ouverte."),
            _p("boulon", "Un cube. Viens me voir, faut que je te regarde.", 7, jeu="[gruffly] Un cube. [quietly] Viens me voir… faut que je te regarde."),
        ],
    },
}
