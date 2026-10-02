"""Le chapitre de Raymonde et du syndicat — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague S). La Shop (vague S) : Raymonde se bat pour ses gars — s03 (la paie de la Prévost), s06 (le rat de l'usine, Bob Sauvé
filé) et s10 (Raymonde menée au maire) — six, deux et deux étapes — deviennent trois ACTES (7 à 9 minutes). La paix
qui suit (s11, l'accord porté SANS ARME à Gros-Boulon) reste une mission : elle attend aussi s09 (l'explosion, l'autre
fil, celui de Gros-Boulon) — en acte, elle ferait attendre s03 jusque-là.

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : les appels de s06 et s10 perdent « Raymonde, du syndicat. » — la même
  voix, coupée au silence ;
- ⚠️ ÉCART : s03 ne ratait pas à la mort (son échec : arrêté, le camion de paie détruit) ; le chapitre rate aussi
  quand on meurt — et REPRENDRE L'ACTE 1 rend la paie à reprendre ;
- la scène de fin de s10 (Raymonde vient à toi devant l'hôtel) reste celle du chapitre ; la scène d'intro de s03 aussi.
- Prévost (qui arrive après s10) est posé à la fin du chapitre ; s11 attend s10, le dernier acte.
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "raymonde_et_le_syndicat",
    "titre": "Raymonde et le syndicat",
    "donneur": "raymonde",
    "prerequis": ["q02"],
    "remplace": ["s03", "s06", "s10"],
    "recompense": 300,
    "donne": {"message": "LE MAIRE A ENTENDU RAYMONDE"},
    "echec": ["arrete", "vehicule_detruit", "mort"],

    "objectifs": [
        # --- Acte 1 (s03, « La paie de la Prévost »).
        {"type": "acte", "texte": "ACTE 1 — LA PAIE DE LA PRÉVOST", "donneur": "raymonde"},  # 0
        {"type": "monter", "texte": "PRENDS LE CAMION DE PAIE PRÈS DE L'HÔTEL", "vehicule": "camion", "ou": "ruelle:hotel:12"},  # 1
        {"type": "tuer", "texte": "LES GARDIENS DE PRÉVOST T'ONT VU — COUCHE-LES", "groupe": "boulonneux", "n": 2, "ou": "ruelle:hotel:12", "loin": 12},  # 2
        {"type": "semer", "texte": "SÈME LA POLICE, LA PAIE À BORD", "etoiles": 2},  # 3
        {"type": "livrer", "texte": "LIVRE LA PAIE AU BAR DE JOSÉE", "lieu": "bar", "rayon": 4},  # 4
        {"type": "tuer", "texte": "PRÉVOST ENVOIE SES BOULONNEUX — TIENS LE BAR", "groupe": "boulonneux", "n": 3, "ou": "donneur", "loin": 14},  # 5
        {"type": "parler", "texte": "REMETS LA PAIE À JOSÉE, AU BAR", "cible": "josee", "donne": {"message": "LA PAIE EST AU SYNDICAT", "prime": 450}},  # 6
        # --- Acte 2 (s06, « Le rat de l'usine »).
        {"type": "acte", "texte": "ACTE 2 — LE RAT DE L'USINE", "donneur": "raymonde"},  # 7
        {"type": "suivre", "texte": "FILE LE CHAR DE BOB SAUVÉ, SANS QU'IL TE VOIE", "vehicule": "auto", "loin": 12, "proche": 3, "lieu": "bar"},  # 8
        {"type": "retourner", "texte": "RACONTE TOUT À RAYMONDE, À L'USINE", "donne": {"message": "BOB SAUVÉ VEND LE SYNDICAT À PRÉVOST", "prime": 250}},  # 9
        # --- Acte 3 (s10, « Raymonde négocie »).
        {"type": "acte", "texte": "ACTE 3 — RAYMONDE NÉGOCIE", "donneur": "raymonde"},  # 10
        {"type": "proteger", "texte": "MÈNE RAYMONDE À L'HÔTEL, OÙ DORT LE MAIRE", "cible": "raymonde", "lieu": "hotel", "rayon": 5},  # 11
        {"type": "tuer", "texte": "LES GARDIENS DE PRÉVOST L'ONT SUIVIE — COUCHE-LES", "groupe": "boulonneux", "pieton": "gardien", "n": 2, "ou": "donneur", "loin": 10},  # 12
    ],

    "scenes": {
        "fin": [
            {"type": "marcher", "acteur": "donneur", "vers": "joueur", "pres": 22, "duree": 50},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
    },

    # s03 — Le jeu de chaque réplique (`jeu=`) — Raymonde, la paie de la Prévost : Nadine est rauque,
    # elle ne crie jamais — elle est plus dure posée. Le ton passe de l'amertume (l'intro) à un
    # soulagement qu'elle ne montre qu'à moitié.
    # s06 — Le jeu de chaque réplique (`jeu=`) — Raymonde : elle sait déjà, elle veut en être sûre. Ferme, sèche ; le
    # `[bitterly]` est pour Sauvé, pas pour Prévost — un patron, on s'y attend ; un contremaître, c'est des nôtres.
    # s10 — Le jeu de chaque réplique (`jeu=`) — Raymonde : elle s'habille pour négocier, et elle a peur pour la première
    # fois, sans le dire. Elle parle plus que d'habitude sur le trajet ; ça s'entend.
    "dialogue": {
        "appel": [
            _l("raymonde", "Raymonde, du syndicat. Prévost retient la paie de mes gars. Viens à l'usine, j'ai une idée pas très légale.", jeu="[firmly] Raymonde, du syndicat. Prévost retient la paie de mes gars. [knowingly] Viens à l'usine… j'ai une idée pas très légale."),
        ],
        "intro": [
            _l("raymonde", "Le camion de paie de Prévost dort près de l'Hôtel Bandini. Il le garde pour nous faire plier.", jeu="[bitterly] Le camion de paie de Prévost dort près de l'Hôtel Bandini. Il le garde… pour nous faire plier."),
            _l("raymonde", "Prends-le, sème la police, pis amène ça au bar de Josée. Mon usine, elle, est surveillée.", jeu="[firmly] Prends-le, sème la police… pis amène ça au bar de Josée. [matter-of-fact] Mon usine, elle, est surveillée."),
            _l("raymonde", "Prévost a mis deux Boulonneux dessus. Des gars de La Shop qui ont oublié d'où ils viennent.", jeu="[bitterly] Prévost a mis deux Boulonneux dessus. [wryly] Des gars de La Shop… qui ont oublié d'où ils viennent."),
        ],
        "fin": [
            _l("raymonde", "Le maire m'a reçue en pantoufles. Il va appeler Prévost demain matin.", jeu="[amused] Le maire m'a reçue en pantoufles. [satisfied] Il va appeler Prévost demain matin."),
            _l("raymonde", "Merci d'être venu. Mes gars le sauront.", jeu="[warmly] Merci d'être venu. [firmly] Mes gars le sauront."),
        ],
        "echec": [
            _e("raymonde", "Prévost garde sa paie, pis mes gars gardent leur faim. Reviens quand t'auras réfléchi.", 0, jeu="[coldly] Prévost garde sa paie… pis mes gars gardent leur faim. [firmly] Reviens quand t'auras réfléchi."),
            _e("raymonde", "Il t'a vu. Bob va être propre comme un sou neuf, astheure.", 7, jeu="[bitterly] Il t'a vu. [wryly] Bob va être propre comme un sou neuf, astheure."),
            _e("raymonde", "Ils m'ont eue. Le maire va dormir tranquille, lui.", 10, jeu="[bitterly] Ils m'ont eue. [somber] Le maire va dormir tranquille, lui."),
        ],
        "pendant": [
            _p("raymonde", "Les chiens de garde de Prévost! Couche-les avant qu'ils lisent ta plaque.", 2, jeu="[firmly] Les chiens de garde de Prévost! [bitterly] Couche-les avant qu'ils lisent ta plaque."),
            _p("raymonde", "Perds-les avant le bar! Josée aime pas les visiteurs en uniforme.", 3, jeu="[firmly] Perds-les avant le bar! [sarcastic] Josée aime pas les visiteurs… en uniforme."),
            _p("raymonde", "Prévost a su! Il envoie ses Boulonneux au bar. Tiens la porte, Josée te regarde.", 5, jeu="[firmly] Prévost a su! Il envoie ses Boulonneux au bar. [matter-of-fact] Tiens la porte… Josée te regarde."),
            # Acte 2 : la fin de s03, en personne ; puis l'appel et l'intro de s06.
            _p("raymonde", "Toutes les enveloppes y sont. Mes gars vont manger cette semaine.", 7, jeu="[relieved] Toutes les enveloppes y sont… [warmly] Mes gars vont manger cette semaine.", cloture=True),
            _p("raymonde", "Dix pour cent pour Josée? Josée pis Prévost, c'est la même école.", 7, jeu="[bitterly] Dix pour cent pour Josée? [wryly] Josée pis Prévost… c'est la même école.", cloture=True),
            _p("raymonde", "Prévost va hurler. Laisse-le hurler, moi j'ai jamais eu peur d'un patron.", 7, jeu="[firmly] Prévost va hurler. Laisse-le hurler… [wryly] moi j'ai jamais eu peur d'un patron.", cloture=True),
            # ⚠️ Coupée (2 oct. 2026) : « Raymonde, du syndicat. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("raymonde", "Prévost connaît le nom de chacun de mes gars. Quelqu'un lui a vendu la liste.", 7, jeu="[serious] Prévost connaît le nom de chacun de mes gars. [bitterly] Quelqu'un lui a vendu la liste."),
            _p("raymonde", "Bob Sauvé. Contremaître le jour, syndiqué le soir. Il joue sur deux tableaux.", 7, jeu="[matter-of-fact] Bob Sauvé. [wryly] Contremaître le jour, syndiqué le soir. [bitterly] Il joue sur deux tableaux."),
            _p("raymonde", "Son char va sortir. Suis-le. Je veux savoir qui il voit, pas ce qu'il dit.", 7, jeu="[firmly] Son char va sortir. Suis-le. [serious] Je veux savoir qui il voit… pas ce qu'il dit."),
            _p("raymonde", "Il part. Reste loin, Bob regarde toujours derrière lui, il a de quoi.", 8, jeu="[quietly] Il part. [firmly] Reste loin… [wryly] Bob regarde toujours derrière lui, il a de quoi."),
            _p("raymonde", "Le Brouillard. Pis Prévost à la table du fond, je gage. Reviens me voir.", 9, jeu="[bitterly] Le Brouillard. Pis Prévost à la table du fond, je gage. [firmly] Reviens me voir."),
            # Acte 3 : la fin de s06, en personne ; puis l'appel et l'intro de s10.
            _p("raymonde", "Sauvé pis Prévost, au même bar, le même soir. Ça me suffit.", 10, jeu="[coldly] Sauvé pis Prévost, au même bar, le même soir. [firmly] Ça me suffit.", cloture=True),
            _p("raymonde", "Mes gars vont l'apprendre de ma bouche. Pas du Clairon.", 10, jeu="[serious] Mes gars vont l'apprendre de ma bouche. [warmly] Pas du Clairon.", cloture=True),
            # ⚠️ Coupée (2 oct. 2026) : « Raymonde, du syndicat. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("raymonde", "Je vais voir le maire ce soir. Prévost a des hommes qui me suivent.", 10, jeu="[serious] Je vais voir le maire ce soir. [quietly] Prévost a des hommes qui me suivent."),
            _p("raymonde", "Le maire dort à l'hôtel, tout le monde le sait astheure. Il va m'écouter, en robe de chambre.", 10, jeu="[wryly] Le maire dort à l'hôtel, tout le monde le sait astheure. [amused] Il va m'écouter, en robe de chambre."),
            _p("raymonde", "Marche avec moi. Si les hommes de Prévost s'approchent, t'occupes-toi d'eux.", 10, jeu="[firmly] Marche avec moi. [serious] Si les hommes de Prévost s'approchent… t'occupes-toi d'eux."),
            _p("raymonde", "Trente ans d'usine, pis j'ai jamais marché aussi loin pour parler à un maire.", 11, jeu="[wryly] Trente ans d'usine… [bitterly] pis j'ai jamais marché aussi loin pour parler à un maire."),
            _p("raymonde", "Les v'là, ses gardiens. Laisse-moi pas toute seule avec eux.", 12, jeu="[nervously] Les v'là, ses gardiens. [firmly] Laisse-moi pas toute seule avec eux."),
        ],
        "accueil": [
            _a("josee", "Toute la paie. Le Brouillard garde dix pour cent, pour le dérangement.", 6, jeu="[coldly] Toute la paie. [matter-of-fact] Le Brouillard garde dix pour cent… pour le dérangement."),
        ],
    },
}
