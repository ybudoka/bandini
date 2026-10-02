"""Le chapitre de Gégé et les débardeurs — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague Q). Gégé, le chef des débardeurs : q03 (les briseurs de grève de Prévost, leur camion détruit avant l'usine) et q09 (la
course des camions du vendredi) — quatre et trois étapes, deux ACTES (5 à 6 minutes).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : l'appel de q09 perd « Gégé, des débardeurs. » — la même voix, coupée ;
- la scène d'intro de q03 reste celle du chapitre.
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "gege_et_les_debardeurs",
    "titre": "Gégé et les débardeurs",
    "donneur": "gege",
    "prerequis": ["m6"],
    "remplace": ["q03", "q09"],
    "recompense": 300,
    "donne": {"message": "LES DÉBARDEURS TE PAIENT LA BIÈRE"},

    "objectifs": [
        # --- Acte 1 (q03, « Les briseurs de grève »).
        {"type": "acte", "texte": "ACTE 1 — LES BRISEURS DE GRÈVE", "donneur": "gege"},  # 0
        {"type": "detruire", "texte": "DÉTRUIS LE CAMION AVANT L'USINE", "vehicule": "camion", "ou": "ruelle:usine:20", "chrono_s": 120},  # 1
        {"type": "tuer", "texte": "LES BOULONNEUX DE PRÉVOST — COUCHE-LES", "groupe": "boulonneux", "n": 3, "ou": "donneur", "loin": 10},  # 2
        {"type": "semer", "texte": "LA POLICE S'EN VIENT — SÈME-LA", "etoiles": 2},  # 3
        {"type": "retourner", "texte": "RETOURNE VOIR GÉGÉ", "donne": {"message": "LES SCABS RESTENT CHEZ EUX", "prime": 300}},  # 4
        # --- Acte 2 (q09, « La course des débardeurs »).
        # La course des débardeurs (M16, arc Q, 30 sept. 2026). Le vendredi, après la paie, les débardeurs font la course
        # autour des Quais en camion — le perdant paie la bière. Gégé veut voir si le neveu tient la route : trois points,
        # dans l'ordre, deux minutes et demie, avec un camion de la cantine.
        # ⚠️ La fiche voulait la course `contre` deux débardeurs : `contre` n'est lu par personne (p04 et e04 l'ont vu) ; c'est
        # une course contre la montre, le temps que les débardeurs ont fait l'an passé.
        {"type": "acte", "texte": "ACTE 2 — LA COURSE DES DÉBARDEURS", "donneur": "gege"},  # 5
        {"type": "monter", "texte": "LE CAMION DE LA CANTINE, DERRIÈRE", "vehicule": "camion", "ou": "ruelle:cantine:12"},  # 6
        {"type": "course", "texte": "L'HÔTEL, LES MORUES, LA CANTINE : DEUX MINUTES ET DEMIE", "points": ["hotel", "zone:morues", "cantine"], "rayon": 4, "chrono_s": 150},  # 7
        {"type": "retourner", "texte": "GÉGÉ A CHRONOMÉTRÉ : VA LE VOIR"},  # 8
    ],

    # q03 — Le jeu de chaque réplique (`jeu=`) — Gégé : sec, sans détour, une satisfaction
    # brève une fois le camion arrêté — il ne remercie jamais deux fois.
    "dialogue": {
        "appel": [
            _l("gege", "Gégé, chef des débardeurs. Prévost fait venir des scabs par camion — arrête-le avant l'usine.", jeu="[firmly] Gégé, chef des débardeurs. [gravely] Prévost fait venir des scabs par camion… arrête-le avant l'usine."),
        ],
        "intro": [
            _l("gege", "Le camion vient par le boulevard, du côté de l'usine. T'as pas beaucoup de temps.", jeu="[gravely] Le camion vient par le boulevard, du côté de l'usine. [firmly] T'as pas beaucoup de temps."),
            _l("gege", "Une fois cassé, plus personne remplace les gars du syndicat aujourd'hui.", jeu="[firmly] Une fois cassé… plus personne remplace les gars du syndicat aujourd'hui."),
            _l("gege", "Prévost paie du monde pour garder son camion. Attends-toi à de la visite.", jeu="[gravely] Prévost paie du monde pour garder son camion. [firmly] Attends-toi à de la visite."),
        ],
        "fin": [
            _l("gege", "Record battu. Les gars paient la bière, pis ils chialent déjà.", jeu="[satisfied] Record battu. [amused] Les gars paient la bière, pis ils chialent déjà."),
            _l("gege", "T'es un débardeur honoraire, astheure. Ça donne rien, mais c'est un honneur.", jeu="[firmly] T'es un débardeur honoraire, astheure. [wryly] Ça donne rien, mais c'est un honneur."),
        ],
        "echec": [
            _e("gege", "Le camion est passé... Les gars vont pas aimer ça.", 0, jeu="[annoyed] Le camion est passé… [gravely] Les gars vont pas aimer ça."),
            _e("gege", "Trop lent. C'est toi qui paies la bière, astheure.", 5, jeu="[amused] Trop lent. [firmly] C'est toi qui paies la bière, astheure."),
        ],
        "pendant": [
            _p("gege", "Le camion approche! Fais ça vite, avant qu'il passe la guérite.", 1, jeu="[gravely] Le camion approche! [firmly] Fais ça vite… avant qu'il passe la guérite."),
            _p("gege", "Prévost a payé des Boulonneux pour garder son camion. Montre-leur où passe la ligne.", 2, jeu="[gravely] Prévost a payé des Boulonneux pour garder son camion. [firmly] Montre-leur où passe la ligne."),
            _p("gege", "La police s'en vient. Un débardeur a jamais rien vu, apprends ça vite.", 3, jeu="[firmly] La police s'en vient. [gruffly] Un débardeur a jamais rien vu… apprends ça vite."),
            _p("gege", "Reviens à la cantine. Les gars veulent voir la face de celui qui a fait ça.", 4, jeu="[satisfied] Reviens à la cantine. [gruffly] Les gars veulent voir la face de celui qui a fait ça."),
            # Acte 2 : la fin de q03, en personne ; puis l'appel et l'intro de q09.
            _p("gege", "Le camion brûle sur le boulevard. Les scabs resteront chez eux, à soir.", 5, jeu="[satisfied] Le camion brûle sur le boulevard. [firmly] Les scabs resteront chez eux… à soir.", cloture=True),
            _p("gege", "Les gars vont s'en souvenir. T'as du cran.", 5, jeu="[impressed] Les gars vont s'en souvenir. [gruffly] T'as du cran.", cloture=True),
            _p("gege", "Pis ses Boulonneux vont boiter jusqu'à la paie. Bon débarras.", 5, jeu="[amused] Pis ses Boulonneux vont boiter jusqu'à la paie. [gruffly] Bon débarras.", cloture=True),
            # ⚠️ Coupée (2 oct. 2026) : « Gégé, des débardeurs. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("gege", "Vendredi, c'est la course des camions. Les gars veulent te voir chauffer.", 5, jeu="[firmly] Vendredi, c'est la course des camions. [amused] Les gars veulent te voir chauffer."),
            _p("gege", "Le perdant paie la bière. Ça fait trois ans que c'est moi, ça va faire.", 5, jeu="[gruffly] Le perdant paie la bière. [amused] Ça fait trois ans que c'est moi, ça va faire."),
            _p("gege", "L'hôtel, le coin des Morues, pis la cantine. Dans l'ordre, en camion.", 5, jeu="[firmly] L'hôtel, le coin des Morues, pis la cantine. [matter-of-fact] Dans l'ordre, en camion."),
            _p("gege", "Deux minutes et demie, c'est le record des gars. Bats-le, pis la bière est pour eux.", 5, jeu="[matter-of-fact] Deux minutes et demie, c'est le record des gars. [amused] Bats-le, pis la bière est pour eux."),
            _p("gege", "Le camion de la cantine, derrière. Lulu le prête, elle le sait pas.", 6, jeu="[matter-of-fact] Le camion de la cantine, derrière. [amused] Lulu le prête, elle le sait pas."),
            _p("gege", "Go! Pis ménage les freins, c'est des freins de syndicat.", 7, jeu="[shouting] Go! [amused] Pis ménage les freins, c'est des freins de syndicat."),
            _p("gege", "Arrêté! Viens voir le chrono, les gars en reviennent pas.", 8, jeu="[excited] Arrêté! [amused] Viens voir le chrono, les gars en reviennent pas."),
        ],
    },
}
