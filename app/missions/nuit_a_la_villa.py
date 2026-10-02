"""Le chapitre de la villa du maire — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague V). Martin a tranché
pour les arcs hors de la liste de M16 : les trois infiltrations de la villa (v01 Josée, v02 Bouchard, v03 Sven, M16 —
la villa du maire, `app/blocs/villa.py`) deviennent trois ACTES d'UNE SEULE NUIT. Avant, chacune refaisait le même
trajet : le saut au chemin de la villa (`sur_place`), le jardin, puis la sortie — trois fois. Maintenant on vole la
clé du garde, on ressort au chemin, Bouchard appelle (« Paraît que t'as une clé qui m'intéresse »), on rentre par la
porte de service jusqu'au bureau, on ressort, Sven appelle, et l'on descend à la chambre forte avant de rapporter le
grand livre. L'horloge tient la nuit dans la villa (`nuit_tient`). Visée : 10 minutes, rien d'ajouté. Mourir au
sous-sol fait reprendre la chambre forte, la clé et le dossier en poche.

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de v01
  restent ceux du chapitre ; la fin de chaque infiltration se dit à l'ouverture de l'acte suivant, au chemin,
  suivie de l'appel et de l'intro de la suivante ; la fin de v03 (chez Sven) reste la fin du chapitre ; chaque
  infiltration garde son échec (`_e`, à son acte). Personne ne se nomme deux fois : trois donneurs, un appel chacun ;
- `sur_place` passe sur le marqueur de chaque acte : dans la nuit déjà tombée, le saut ne bouge pas l'horloge et
  repose au chemin ; c'est lui qui ramène à la villa quand on REPREND L'ACTE après l'hôpital ou le poste ;
- `frontiere` reste au niveau du chapitre (les trois infiltrations avaient la même) : la villa ne se quitte pas
  avant le premier `retourner`, celui qui rapporte le grand livre à Sven ;
- LE SAC : la clé de v01 ouvre la porte de service aux actes 2 et 3 ; rater un acte ne fait retomber que ce que
  CET acte a fait prendre (`Infiltration.rendre`, borné à l'acte), et une partie qui a perdu la clé la retrouve au
  chargement par l'acte qui la donne (`cles_des_serrures` nomme v01) ;
- chaque acte paie sa prime et accorde ce que sa mission accordait en finissant (les deux pages de casier de
  Bouchard à l'acte 2) ; q14 attend v03, le dernier acte.
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "nuit_a_la_villa",
    "titre": "Une nuit à la villa",
    "donneur": "josee",
    "prerequis": ["q04"],
    "remplace": ["v01", "v02", "v03"],
    "recompense": 1200,
    "donne": {"message": "LE GRAND LIVRE DU MAIRE, CHEZ SVEN"},
    "echec": ["mort", "arrete", "etoile", "alarme"],
    # La villa ne se quitte pas avant de rapporter le grand livre (`SurPlace.tient` : jusqu'au premier `retourner`).
    "frontiere": "bloc:villa",

    "objectifs": [
        # --- Acte 1 (v01, « La clé du maire »).
        # La première des trois infiltrations de la villa du maire (`app/blocs/villa.py`,
        # docs/jalons/infiltration-portes-verrouillees-et-gardes-prives.md) : on n'y entre pas encore, on
        # vole la clé. Le garde du jardin fait le tour de la maison, la clé de la porte de service dans la
        # poche ; on la lui prend PAR-DERRIÈRE (`obtenir`, `garde`), et on ressort comme on est venu.
        {"type": "acte", "texte": "ACTE 1 — LA CLÉ DU MAIRE", "donneur": "josee", "sur_place": {"lieu": "villa_chemin", "heure": "nuit"}},  # 0
        {"type": "aller", "texte": "VA À LA VILLA DU MAIRE, DE NUIT", "lieu": "villa_chemin", "rayon": 6, "nuit": True},  # 1
        {"type": "obtenir", "texte": "VOLE LA CLÉ DU GARDE : ACTION DANS SON DOS, SANS ÊTRE VU", "objet": "cle_villa", "nom": "LA CLÉ DE LA PORTE DE SERVICE", "dessin": "cle", "garde": "jardin", "ou": "villa_chemin", "sans_etoile": True},  # 2
        {"type": "aller", "texte": "RESSORS PAR LE CHEMIN, SANS TE FAIRE VOIR", "lieu": "villa_chemin", "rayon": 6, "sans_etoile": True, "donne": {"message": "LA CLÉ DE LA PORTE DE SERVICE, DANS TA POCHE", "prime": 500}},  # 3
        # --- Acte 2 (v02, « Le dossier du sergent »).
        # La deuxième infiltration de la villa du maire (`app/blocs/villa.py`) : avec la clé de v01, on entre
        # par la porte de service (une serrure du bloc, condition `objet`), on traverse le rez-de-chaussée,
        # on monte le grand escalier du hall, on traverse l'étage jusqu'à l'escalier de la bibliothèque, et on
        # trouve au 2e étage le dossier que le maire garde sur le sergent, dans son bureau — des gardes à chaque
        # étage (`villa.GARDES`).
        {"type": "acte", "texte": "ACTE 2 — LE DOSSIER DU SERGENT", "donneur": "bouchard", "sur_place": {"lieu": "villa_chemin", "heure": "nuit"}},  # 4
        {"type": "aller", "texte": "VA À LA VILLA DU MAIRE, DE NUIT", "lieu": "villa_chemin", "rayon": 6, "nuit": True},  # 5
        {"type": "aller", "texte": "ENTRE PAR LA PORTE DE SERVICE, AVEC TA CLÉ", "lieu": "villa_service", "rayon": 2, "sans_etoile": True},  # 6
        {"type": "obtenir", "texte": "TROUVE LE DOSSIER, DANS LE BUREAU D'EN HAUT", "objet": "dossier_bouchard", "nom": "LE DOSSIER DU SERGENT", "dessin": "dossier", "ou": "villa_bureau", "sans_etoile": True},  # 7
        {"type": "aller", "texte": "RESSORS PAR LE CHEMIN, SANS TE FAIRE VOIR", "lieu": "villa_chemin", "rayon": 6, "sans_etoile": True, "donne": {"message": "DEUX PAGES DE MOINS À TON CASIER", "casier": -2, "prime": 700}},  # 8
        # --- Acte 3 (v03, « La chambre forte »).
        # La troisième infiltration de la villa du maire (`app/blocs/villa.py`) : sous la cave. Par la porte de
        # service et l'escalier de la cuisine, un dédale de caves, l'escalier de l'antichambre, le sous-sol et ses
        # gardes, et la chambre forte au fond — sa porte
        # ne s'ouvre qu'au code, et le code est dans un terminal qu'on pirate (le labyrinthe électrifié). Le
        # piratage réussi met le code dans le sac (`objet` sur `pirater`) : la serrure de la chambre forte
        # s'ouvre. Dedans, le grand livre du maire.
        {"type": "acte", "texte": "ACTE 3 — LA CHAMBRE FORTE", "donneur": "sven", "sur_place": {"lieu": "villa_chemin", "heure": "nuit"}},  # 9
        {"type": "aller", "texte": "VA À LA VILLA DU MAIRE, DE NUIT", "lieu": "villa_chemin", "rayon": 6, "nuit": True},  # 10
        {"type": "pirater", "texte": "PIRATE LE TERMINAL DE LA CHAMBRE FORTE, AU SOUS-SOL", "ou": "villa_terminal", "rayon": 2, "longueur": 5, "essais": 3, "objet": "code_voute", "sans_etoile": True},  # 11
        {"type": "obtenir", "texte": "PRENDS LE GRAND LIVRE DANS LA CHAMBRE FORTE", "objet": "grand_livre", "nom": "LE GRAND LIVRE DU MAIRE", "dessin": "registre", "ou": "villa_voute", "sans_etoile": True},  # 12
        {"type": "aller", "texte": "RESSORS PAR LE CHEMIN, SANS TE FAIRE VOIR", "lieu": "villa_chemin", "rayon": 6, "sans_etoile": True},  # 13
        {"type": "retourner", "texte": "RAPPORTE LE GRAND LIVRE À SVEN"},  # 14
    ],

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

    # v01 — Le jeu de chaque réplique (`jeu=`) — Josée : la Chef qui prépare un coup de loin. Rien de pressé,
    # rien d'expliqué de trop : elle veut une clé, pas une histoire. Le « pourquoi » reste dans sa poche,
    # comme la clé dans celle du garde — une seule phrase de mystère, et un `[warmly]`, à la fin.
    # v02 — Le jeu de chaque réplique (`jeu=`) — Bouchard : un homme qui a peur et qui commande pour ne pas
    # le montrer. Il ne dit pas « s'il te plaît », mais il appelle lui-même, et il parle trop vite. Le
    # `[nervously]` monte d'une réplique à l'autre ; `[satisfied]` et « Propre. » à la fin, et rien d'autre.
    # v03 — Le jeu de chaque réplique (`jeu=`) — Sven : le calcul, toujours ; pas un mot d'ici, pas une
    # familiarité. Ici, quelque chose de plus : il sait ce que vaut un maire qui doit de l'argent, et ça
    # l'amuse à peine. `[satisfied]`, jamais chaleureux, à la fin.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. J'ai besoin d'une clé que personne doit savoir perdue.", jeu="[calm] Josée. [mysteriously] J'ai besoin d'une clé… que personne doit savoir perdue."),
        ],
        "intro": [
            _l("josee", "Le maire Tanguay a une villa au bout des Érables. Gardée comme une banque, la nuit.", jeu="[matter-of-fact] Le maire Tanguay a une villa au bout des Érables. [coldly] Gardée comme une banque, la nuit."),
            _l("josee", "Le garde du jardin porte la clé de la porte de service. Je la veux, sans qu'il sache qu'elle est partie.", jeu="[firmly] Le garde du jardin porte la clé de la porte de service. [quietly] Je la veux, sans qu'il sache qu'elle est partie."),
            _l("josee", "Pas de bagarre, pas d'étoile. Un garde qui te voit, pis le maire change ses serrures.", jeu="[serious] Pas de bagarre, pas d'étoile. [menacingly] Un garde qui te voit… pis le maire change ses serrures."),
        ],
        "fin": [
            _l("sven", "Le maire doit de l'argent à trois personnes que je connais. Maintenant, il m'en doit à moi.", jeu="[Norwegian accent][satisfied] Le maire doit de l'argent à trois personnes que je connais. [coldly] Maintenant… il m'en doit à moi."),
            _l("sven", "Travail propre. Je ne le paie qu'une fois, et je le paie bien.", jeu="[Norwegian accent][matter-of-fact] Travail propre. [calm] Je ne le paie qu'une fois… et je le paie bien."),
        ],
        "echec": [
            _e("josee", "Vu. Le maire va doubler ses gardes. Reviens quand tu sauras marcher dans le noir.", 0, jeu="[coldly] Vu. [annoyed] Le maire va doubler ses gardes. Reviens quand tu sauras marcher dans le noir."),
            _e("bouchard", "J'ai rien vu, j'ai rien entendu. Pis le maire, lui, a tout vu.", 4, jeu="[nervously] J'ai rien vu, j'ai rien entendu. [gravely] Pis le maire, lui, a tout vu."),
            _e("sven", "Tu n'étais pas prêt. La chambre forte sera encore là ; toi, sois plus patient.", 9, jeu="[Norwegian accent][calm] Tu n'étais pas prêt. [coldly] La chambre forte sera encore là… toi, sois plus patient."),
        ],
        "pendant": [
            _p("josee", "Passe pas par la grille, elle a son garde. Fais le tour : au nord, il manque une planche à la palissade.", 2, jeu="[quietly] Passe pas par la grille… elle a son garde. [matter-of-fact] Fais le tour : au nord, il manque une planche à la palissade."),
            _p("josee", "Attends dehors, collé sur la palissade. Tant que t'es pas sur son terrain, il a rien à te dire.", 2, jeu="[calm] Attends dehors, collé sur la palissade. [coldly] Tant que t'es pas sur son terrain… il a rien à te dire."),
            _p("josee", "Celui du jardin fait le tour de la maison. À chaque coin, il s'arrête, pis il se retourne.", 2, jeu="[matter-of-fact] Celui du jardin fait le tour de la maison. [gravely] À chaque coin… il s'arrête, pis il se retourne."),
            _p("josee", "Suis-le dans une longue ligne droite, loin des coins. Colle-toi dans son dos, pis sers-toi dans sa poche.", 2, jeu="[quietly] Suis-le dans une longue ligne droite… loin des coins. [mischievously] Colle-toi dans son dos, pis sers-toi dans sa poche."),
            _p("josee", "Ils ont des lampes de poche. S'il regarde de ton bord, recule dans le noir. Tout de suite.", 2, jeu="[serious] Ils ont des lampes de poche. [firmly] S'il regarde de ton bord, recule dans le noir. Tout de suite."),
            _p("josee", "La clé est à toi. Sors par où t'es entré, pas plus vite qu'un chat.", 3, jeu="[satisfied] La clé est à toi. [quietly] Sors par où t'es entré… pas plus vite qu'un chat."),
            # Acte 2 : la fin de v01, en personne ; puis l'appel et l'intro de v02.
            _p("josee", "Une clé, pis personne l'a vue partir. Garde-la, un jour on va entrer chez le maire sans sonner.", 4, jeu="[satisfied] Une clé, pis personne l'a vue partir. [mysteriously] Garde-la… un jour on va entrer chez le maire sans sonner.", cloture=True),
            _p("josee", "T'as les mains fines. C'est plus rare que des gros bras.", 4, jeu="[warmly] T'as les mains fines. [matter-of-fact] C'est plus rare que des gros bras.", cloture=True),
            _p("bouchard", "Salut, le jeune, c'est Bouchard. Paraît que t'as une clé qui m'intéresse.", 4, jeu="[gruffly] Salut, le jeune, c'est Bouchard. [knowingly] Paraît que t'as une clé qui m'intéresse."),
            _p("bouchard", "Le maire garde un dossier sur moi. Des enveloppes, des dates, des photos.", 4, jeu="[gravely] Le maire garde un dossier sur moi. [nervously] Des enveloppes, des dates… des photos."),
            _p("bouchard", "Il est dans son bureau, en haut de la villa. Tu rentres par la porte de service, tu le prends.", 4, jeu="[firmly] Il est dans son bureau, en haut de la villa. [matter-of-fact] Tu rentres par la porte de service, tu le prends."),
            _p("bouchard", "Si un garde te voit, je te connais pas. Pis toi non plus, tu me connais pas.", 4, jeu="[nervously] Si un garde te voit, je te connais pas. [menacingly] Pis toi non plus, tu me connais pas."),
            _p("bouchard", "La porte de service, derrière la cuisine. Ta clé fait le reste.", 6, jeu="[quietly] La porte de service, derrière la cuisine. [matter-of-fact] Ta clé fait le reste."),
            _p("bouchard", "Le grand escalier est dans le hall. Le gars du hall regarde la porte d'en avant, pas son dos.", 7, jeu="[quietly] Le grand escalier est dans le hall. [knowingly] Le gars du hall regarde la porte d'en avant, pas son dos."),
            _p("bouchard", "Tu l'as? Sors de là. Tranquille, comme un gars qui a rien vu.", 8, jeu="[nervously] Tu l'as? [firmly] Sors de là. Tranquille, comme un gars qui a rien vu."),
            # Acte 3 : la fin de v02, en personne ; puis l'appel et l'intro de v03.
            _p("bouchard", "Propre. Ce dossier-là va faire une belle flamme dans le poêle du poste.", 9, jeu="[satisfied] Propre. [deadpan] Ce dossier-là va faire une belle flamme dans le poêle du poste.", cloture=True),
            _p("bouchard", "Pis ton casier maigrit de deux pages. Entre nous, ça s'appelle de la gratitude.", 9, jeu="[knowingly] Pis ton casier maigrit de deux pages. [deadpan] Entre nous, ça s'appelle de la gratitude.", cloture=True),
            _p("sven", "Sven. Le maire de cette ville tient ses comptes dans une cave. J'aimerais les lire.", 9, jeu="[Norwegian accent][calm] Sven. [matter-of-fact] Le maire de cette ville tient ses comptes… dans une cave. J'aimerais les lire."),
            _p("sven", "Sous la villa, une chambre forte. Dedans, un grand livre : qui le maire paie, et qui le paie.", 9, jeu="[Norwegian accent][quietly] Sous la villa, une chambre forte. [matter-of-fact] Dedans, un grand livre : qui le maire paie… et qui le paie."),
            _p("sven", "La porte obéit à un terminal. Tu connais ce genre de serrure, maintenant.", 9, jeu="[Norwegian accent][calm] La porte obéit à un terminal. [wryly] Tu connais ce genre de serrure… maintenant."),
            _p("sven", "Personne ne doit savoir que le livre a été ouvert. Personne ne doit te voir.", 9, jeu="[Norwegian accent][firmly] Personne ne doit savoir que le livre a été ouvert. [coldly] Personne ne doit te voir."),
            _p("sven", "L'escalier de la cave est dans la cuisine. Les gardes d'en bas s'ennuient ; ne les distrais pas.", 11, jeu="[Norwegian accent][quietly] L'escalier de la cave est dans la cuisine. [wryly] Les gardes d'en bas s'ennuient… ne les distrais pas."),
            _p("sven", "La porte est ouverte. Le livre est vert, relié de cuir.", 12, jeu="[Norwegian accent][calm] La porte est ouverte. [matter-of-fact] Le livre est vert… relié de cuir."),
            _p("sven", "Bien. Maintenant, sors comme si tu n'étais jamais entré.", 13, jeu="[Norwegian accent][satisfied] Bien. [firmly] Maintenant, sors… comme si tu n'étais jamais entré."),
        ],
    },
}
