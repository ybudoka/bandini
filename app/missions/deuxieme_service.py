"""Le chapitre du deuxième service — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague F). Martin a tranché
pour les arcs hors de la liste de M16 : le stool que Bouchard veut voir se taire (f06 : la filature, les 200 $, sa
copie démolie, la police à semer) et Marco qui veut sa part (f09 : l'escorte au kiosque, deux Cravates, le troisième
filé jusqu'à leur cache) deviennent deux ACTES — f09 n'attendait que f06, et les deux finissent l'affaire des
Cravates que f01 a ouverte. Visée : 7 à 9 minutes, rien d'ajouté. Le défi de la filature des Quais s'ouvre quand f06
est faite, à l'ouverture de l'acte 2 (`debloque`) ; f12 attend f09, le dernier acte.

Ce qui a bougé, et pourquoi (comme aux autres chapitres) :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la
  première mission restent ceux du chapitre ; la fin de la première se dit à l'ouverture de l'acte 2, suivie de
  l'appel et de l'intro de la seconde ; la fin de la seconde reste la fin du chapitre ; chacune garde son échec
  (`_e`, accroché à son acte) ;
- l'acte 1 paie sa prime et accorde ce que sa mission accordait en finissant (`donne` sur l'objectif qui le
  finit), et la mission qu'il remplace est faite à l'ouverture de l'acte 2 — ce qui l'attendait s'ouvre là ;
- la scène d'intro de la première reste celle du chapitre, la scène de fin de la seconde celle de sa fin ; les
  deux autres tombent (leurs répliques se disent au marqueur), comme au pilote.
- deux donneurs, un appel chacun : Bouchard se nomme au sien, Marco au sien ; personne ne se nomme deux fois. Marco
  ne part pas avant (`parti_apres: m97`, qui attend f12, qui attend f09).
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "deuxieme_service",
    "titre": "Deuxième service",
    "donneur": "bouchard",
    "prerequis": ["f01"],
    "remplace": ["f06", "f09"],
    "recompense": 250,
    "donne": {"message": "MARCO A VU OÙ EST L'ARGENT"},

    "objectifs": [
        # --- Acte 1 (f06, « Deuxième service »).
        {"type": "acte", "texte": "ACTE 1 — DEUXIÈME SERVICE", "donneur": "bouchard"},  # 0
        {"type": "suivre", "texte": "SUIS-LE SANS TE FAIRE REPÉRER", "vehicule": "auto", "loin": 10, "proche": 3, "par": ["garage", "terminus"], "lieu": "poste"},  # 1
        {"type": "payer", "texte": "PAIE-LUI 200 $ POUR SON SILENCE", "montant": 200},  # 2
        {"type": "detruire", "texte": "SA COPIE DORT DANS SON AUTRE CHAR : DÉMOLIS-LE", "vehicule": "auto", "ou": "ruelle:hotel"},  # 3
        {"type": "semer", "texte": "LE BOUM A RÉVEILLÉ LE QUARTIER : SÈME LA POLICE", "etoiles": 2, "donne": {"message": "LE STOOL SE TAIT", "prime": 300}},  # 4
        # --- Acte 2 (f09, « Marco veut sa part »).
        {"type": "acte", "texte": "ACTE 2 — MARCO VEUT SA PART", "donneur": "marco"},  # 5
        {"type": "proteger", "texte": "ESCORTE MARCO JUSQU'AU KIOSQUE", "cible": "marco", "lieu": "kiosque", "rayon": 5},  # 6
        {"type": "tuer", "texte": "REPOUSSE LES DEUX CRAVATES", "groupe": "cravates", "n": 2, "ou": "donneur", "loin": 10},  # 7
        {"type": "suivre", "texte": "SUIS LE TROISIÈME JUSQU'À LEUR CACHE", "vehicule": "auto", "loin": 10, "proche": 3, "lieu": "hotel"},  # 8
        {"type": "aller", "texte": "RAMÈNE MARCO AU GARAGE", "lieu": "garage", "rayon": 6},  # 9
    ],

    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "porte:poste", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
    },

    # f06 — Le jeu de chaque réplique (`jeu=`) — Bouchard : bourru, jamais un mot de trop, une
    # satisfaction sèche à la fin — il n'a pas besoin de sourire pour qu'on sache que
    # l'affaire est réglée.
    # f09 — Le jeu de chaque réplique (`jeu=`) — Marco : la désinvolture de qui a peur et le
    # cache, comme f01 ; il hausse les épaules sur l'embuscade, baisse la voix quand il
    # flaire l'argent des autres, puis se rengorge à la fin — la part qu'il n'a jamais eue.
    "dialogue": {
        "appel": [
            _l("bouchard", "Salut, le jeune, c'est Bouchard. Un témoin de l'affaire des Cravates parle trop, au casse-croûte.", jeu="[gruffly] Salut, le jeune, c'est Bouchard. [gravely] Un témoin de l'affaire des Cravates parle trop… au casse-croûte."),
        ],
        "intro": [
            _l("bouchard", "Suis-le jusqu'au poste sans qu'il te voie. Pas trop près, pas trop loin.", jeu="[firmly] Suis-le jusqu'au poste sans qu'il te voie. [gravely] Pas trop près, pas trop loin."),
            _l("bouchard", "Une fois là, tu lui paies son silence. Deux cents piastres, pas une de plus.", jeu="[matter-of-fact] Une fois là, tu lui paies son silence. [firmly] Deux cents piastres… pas une de plus."),
        ],
        "fin": [
            _l("marco", "On est arrivés en un morceau. J'ai ma part, pis j'ai vu où le reste de l'argent dort.", jeu="[relieved] On est arrivés en un morceau. [impressed] J'ai ma part… pis j'ai vu où le reste de l'argent dort."),
            _l("marco", "Ça pourrait servir, un jour. Merci, cousin.", jeu="[knowingly] Ça pourrait servir, un jour. [warmly] Merci, cousin."),
            _l("marco", "Pis l'hôtel, ça reste entre nous deux, cousin.", jeu="[quietly] Pis l'hôtel… ça reste entre nous deux, cousin."),
        ],
        "echec": [
            _e("bouchard", "Il t'a vu, hein? Astheure il va jaser à tout le Faubourg.", 0, jeu="[annoyed] Il t'a vu, hein? [gravely] Astheure il va jaser à tout le Faubourg."),
            _e("marco", "Ils m'ont eu presque... T'étais où, cousin?", 5, jeu="[coldly] Ils m'ont eu presque… [annoyed] T'étais où, cousin?"),
        ],
        "pendant": [
            _p("bouchard", "Reste loin de son pare-choc. Un stool nerveux, ça regarde dans son rétroviseur.", 1, jeu="[gravely] Reste loin de son pare-choc. [wryly] Un stool nerveux… ça regarde dans son rétroviseur."),
            _p("bouchard", "Un stool, ça garde toujours une copie. La sienne dort dans son autre char, derrière l'hôtel.", 3, jeu="[knowingly] Un stool, ça garde toujours une copie. [gruffly] La sienne dort dans son autre char… derrière l'hôtel."),
            _p("bouchard", "Mes gars s'en viennent. Je peux rien pour toi, le jeune, sème-les.", 4, jeu="[nervously] Mes gars s'en viennent. [matter-of-fact] Je peux rien pour toi, le jeune… sème-les."),
            # Acte 2 : la fin de f06, en personne ; puis l'appel et l'intro de f09.
            _p("bouchard", "Il se taira. Deux cents piastres achètent beaucoup de silence, par icitte.", 5, jeu="[satisfied] Il se taira. [wryly] Deux cents piastres achètent beaucoup de silence, par icitte.", cloture=True),
            _p("bouchard", "T'as fait ça proprement. C'est tout ce que je demande.", 5, jeu="[gruffly] T'as fait ça proprement. [matter-of-fact] C'est tout ce que je demande.", cloture=True),
            _p("bouchard", "Pis la copie, j'en ai jamais entendu parler.", 5, jeu="[deadpan] Pis la copie… j'en ai jamais entendu parler.", cloture=True),
            _p("marco", "Cousin, c'est Marco. J'ai ma part à aller chercher au kiosque, pis j'aime pas marcher seul.", 5, jeu="[casually] Cousin, c'est Marco. [wryly] J'ai ma part à aller chercher au kiosque… pis j'aime pas marcher seul."),
            _p("marco", "Les Cravates ont pas digéré la dernière fois. Reste collé sur moi jusqu'au kiosque.", 5, jeu="[casually] Les Cravates ont pas digéré la dernière fois. [firmly] Reste collé sur moi… jusqu'au kiosque."),
            _p("marco", "Si ça chauffe, tu t'en occupes. Moi, je marche vite pis je regarde pas en arrière.", 5, jeu="[wryly] Si ça chauffe, tu t'en occupes. [nervously] Moi, je marche vite… pis je regarde pas en arrière."),
            _p("marco", "Deux gars en cravate! Je le savais! Occupe-toi d'eux, cousin!", 7, jeu="[worried] Deux gars en cravate! [excited] Je le savais! Occupe-toi d'eux, cousin!"),
            _p("marco", "Y en a un troisième qui se pousse en char. Prends un char, cousin, je veux voir où il va.", 8, jeu="[quietly] Y en a un troisième qui se pousse en char. [firmly] Prends un char, cousin… je veux voir où il va."),
            _p("marco", "L'argent dort à l'hôtel. Ça s'invente pas. Ramène-moi au garage, cousin.", 9, jeu="[wryly] L'argent dort à l'hôtel. [laughs] Ça s'invente pas. [casually] Ramène-moi au garage, cousin."),
        ],
    },
}
