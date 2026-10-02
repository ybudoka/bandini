"""Le chapitre du retour du maître — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague C). Les quatre jobs du
retour de Victor Tam (c05 à c08, deux étapes chacune) deviennent quatre ACTES : Irène l'a fait revenir de Floride,
puis le vieux maître reprend ses élèves un par un — les trois frimeurs du mah-jong, Kenny, Monsieur Bois, et les
portes ouvertes. Visée : 8 à 10 minutes, rien d'ajouté. Il attend la chute du Pouce (`chute_du_pouce`, dont c04 est
le dernier acte) : le maître arrive en ville après c04.

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de c05
  (Irène) restent ceux du chapitre ; la fin de chaque job se dit à l'ouverture de l'acte suivant, suivie de l'appel
  et de l'intro du job suivant ; la fin de c08 reste la fin du chapitre ; chaque job garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : le maître se nomme à son accueil de l'acte 1 (« Victor Tam. Sifu… ») ;
  ses trois appels suivants perdent « Sifu Tam, petit scarabée », « C'est Sifu Tam » et « Sifu Tam » — la même
  voix, coupée au silence ; la fin de c06 perd aussi « Reviens me voir demain » : le mannequin, c'est tout de suite ;
- chaque acte paie sa prime et accorde ce que sa mission accordait en finissant (la main de la mante à l'acte 3) ;
  l'école rouvre à la fin du chapitre (`mantes.REPRISE`, `apres: c08` ; `calme: mantes`, la une du Clairon) ;
- l'échec `vehicule_detruit` de c07 vaut pour le chapitre : seul le camion de Gilles est un char de mission ;
- la scène d'intro de c05 reste celle du chapitre, la scène de fin de c08 celle de sa fin ; les scènes écrites des
  actes du milieu tombent (leurs répliques se disent au marqueur), comme au pilote.
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "retour_du_maitre",
    "titre": "Le retour du maître",
    "donneur": "irene",
    "prerequis": ["c04"],
    "remplace": ["c05", "c06", "c07", "c08"],
    "recompense": 1200,
    "donne": {"calme": "mantes", "manchette": "ecole_rouverte", "message": "L'ÉCOLE LA MANTE ROUVRE SES COURS"},
    "echec": ["mort", "arrete", "vehicule_detruit"],

    "objectifs": [
        # --- Acte 1 (c05, « Le droit de table »).
        # Le retour du vieux maître (docs/jalons/l-ecole-rivale.md, vague 2 — Martin, 29 sept. 2026 : « les deux »). Le Pouce
        # tombé, Irène a un autre compte à régler : trois Mantes veulent un « droit de table » au club de mah-jong. Elle a appelé
        # en Floride. Victor Tam, le vieux maître de l'ÉCOLE LA MANTE — le seul qui l'ait jamais battue au mah-jong — est revenu
        # hier soir par l'autobus, bronzé. On va le voir à son école ; il t'envoie chercher ses trois frimeurs par l'oreille.
        {"type": "acte", "texte": "ACTE 1 — LE DROIT DE TABLE", "donneur": "irene"},  # 0
        {"type": "parler", "texte": "VA VOIR LEUR VIEUX MAÎTRE, À L'ÉCOLE LA MANTE", "cible": "maitre"},  # 1
        {"type": "tuer", "texte": "RAMÈNE LES TROIS FRIMEURS PAR L'OREILLE", "groupe": "mantes", "n": 3, "ou": "zone:mantes", "arme": "", "vie": 70, "donne": {"message": "LE CLUB DE MAH-JONG A RAVOIR SES TUILES", "prime": 500}},  # 2
        # --- Acte 2 (c06, « Le chemin de chez Gus »).
        # Le premier élève (docs/jalons/l-ecole-rivale.md, vague 2). Kenny, le meilleur élève du vieux maître — le grand écart
        # à huit ans —, est devenu le caïd des Mantes, et ce soir il va s'acheter un fusil chez Gus. On le file dans son char de
        # frime jusqu'à l'armurerie ; quand il descend, on règle ça comme à l'école : un duel, à mains nues. Le lendemain, Kenny
        # balaie le plancher de l'école.
        {"type": "acte", "texte": "ACTE 2 — LE CHEMIN DE CHEZ GUS", "donneur": "maitre"},  # 3
        {"type": "suivre", "texte": "SUIS LE CHAR DE KENNY SANS TE FAIRE VOIR", "vehicule": "sport", "loin": 10, "proche": 3, "lieu": "armurerie"},  # 4
        {"type": "tuer", "texte": "UN DUEL À MAINS NUES AVEC KENNY, DEVANT CHEZ GUS", "groupe": "mantes", "n": 1, "chef": True, "ou": "porte:armurerie", "arme": "", "vie": 160, "donne": {"message": "KENNY EST RETOURNÉ À L'ÉCOLE", "prime": 700}},  # 5
        # --- Acte 3 (c07, « Monsieur Bois »).
        # Monsieur Bois (docs/jalons/l-ecole-rivale.md, vague 2). Les élèves ont vendu le vieux mannequin de l'école — 1976, du
        # vrai érable — à la fourrière, pour quarante piasses. Gilles l'a gardé dans la boîte de son camion, et te le prête : on
        # ramène Monsieur Bois à l'école sans une égratignure. En échange, le vieux maître t'apprend la main de la mante
        # (`donne.technique` : le retournement du poignet, comme une leçon réussie au DOJO DION, sans la payer).
        {"type": "acte", "texte": "ACTE 3 — MONSIEUR BOIS", "donneur": "maitre"},  # 6
        {"type": "monter", "texte": "MONSIEUR BOIS EST DANS LE CAMION DE GILLES, À LA FOURRIÈRE", "vehicule": "camion", "ou": "porte:fourriere", "prete": "gilles"},  # 7
        {"type": "livrer", "texte": "RAMÈNE MONSIEUR BOIS À L'ÉCOLE SANS UNE ÉGRATIGNURE", "lieu": "ecole_mante", "rayon": 6, "sans_degats": True, "donne": {"technique": "retournement_poignet", "message": "LE MAÎTRE T'APPREND LA MAIN DE LA MANTE", "prime": 600}},  # 8
        # --- Acte 4 (c08, « Les portes ouvertes »).
        # Les portes ouvertes — la dernière de l'arc du vieux maître (docs/jalons/l-ecole-rivale.md, vague 2). L'école rouvre
        # demain matin, et Victor Tam va le crier dans tout le quartier : on l'escorte à pied jusqu'au Dragon d'or, où Irène
        # pose son affiche, et on repousse les derniers frimeurs qui veulent lui faire peur.
        #
        # ⚠️ **L'ÉCOLE ROUVRE** (`mantes.REPRISE`, `apres: c08`) : dans la salle, les élèves ne sont plus du gang et font face au
        # maître ; dans la rue, beaucoup moins de Mantes ; et le gang est CALME (`donne.calme`). Le lendemain matin, le Clairon
        # en fait sa une (`donne.manchette`, `journal.SPECIALES`).
        {"type": "acte", "texte": "ACTE 4 — LES PORTES OUVERTES", "donneur": "maitre"},  # 9
        {"type": "proteger", "texte": "ESCORTE LE MAÎTRE JUSQU'AU DRAGON D'OR", "cible": "maitre", "lieu": "nord_casino", "rayon": 6},  # 10
        {"type": "tuer", "texte": "LES DERNIERS FRIMEURS ARRIVENT — PROTÈGE LE MAÎTRE", "groupe": "mantes", "n": 4, "ou": "donneur", "loin": 10, "arme": "", "vie": 80},  # 11
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "chez:maitre", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
            {"type": "dire", "repliques": [4]},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:maitre", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "coupe", "vers": "chez:irene", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # c05 — Le jeu de chaque réplique (`jeu=`) — Irène : la taquinerie d'abord, puis une vraie colère de voisine (le
    # mah-jong, c'est sa maison), et, en parlant de Victor, une tendresse qu'elle cache sous une gageure. Elle se
    # nomme à l'appel, sèche. Le maître, qu'on entend pour la première fois : la bonhomie d'un homme bronzé qui a
    # trop dormi au soleil, et, sous la blague, la honte d'avoir laissé ses élèves — il se nomme à la poignée de
    # main, à sa façon (« Sifu, pour mes élèves »).
    # c06 — Le jeu de chaque réplique (`jeu=`) — le maître : l'orgueil du vieux prof qui parle de son meilleur élève, puis
    # la peine, franche, quand il dit « un fusil » ; au duel, la politesse du salut dite comme une règle sacrée et
    # drôle à la fois ; à la fin, la fatigue joyeuse d'un homme qui a gagné une manche et qui en voit dix autres. Il se
    # nomme à l'appel, une fois : « Sifu Tam ».
    # c07 — Le jeu de chaque réplique (`jeu=`) — le maître : une tendresse ridicule et sincère pour un morceau de bois, dite
    # le plus sérieusement du monde (c'est ce qui la rend drôle) ; au volant, l'inquiétude d'un vieux pour un autre
    # vieux ; à la fin, la gratitude, puis le ton du professeur qui enseigne pour de vrai — lent, net, trois temps —,
    # et une dernière pointe contre Irène. Il se nomme à l'appel, une fois.
    # c08 — Le jeu de chaque réplique (`jeu=`) — le maître : l'entrain d'un homme qui rouvre sa maison, avec ses affiches ;
    # la bravade comique quand il parle de peur (l'alligator) ; dans la rue, la lenteur heureuse d'un snowbird ; sous
    # l'attaque, le calme du professeur ; à la fin, la joie simple, et la gratitude dite une fois. Irène, à la porte du
    # Dragon d'or : sa gageure, pour la dernière fois tendre — elle ne se renomme pas, on la connaît.
    "dialogue": {
        "appel": [
            _l("irene", "Irène Lam. Les Mantes ont renversé la table du club de mah-jong, pis ça, mon pigeon, c'est personnel.", jeu="[coldly] Irène Lam. [bitterly] Les Mantes ont renversé la table du club de mah-jong… pis ça, mon pigeon, c'est personnel."),
        ],
        "intro": [
            _l("irene", "Trois frimeurs en pyjama vert qui veulent un droit de table. Au mah-jong. Chez nous!", jeu="[sarcastic] Trois frimeurs en pyjama vert qui veulent un droit de table. [annoyed] Au mah-jong. Chez nous!"),
            _l("irene", "J'ai appelé en Floride. Leur vieux maître, Victor Tam, est revenu hier soir par l'autobus.", jeu="[knowingly] J'ai appelé en Floride. [matter-of-fact] Leur vieux maître, Victor Tam, est revenu hier soir par l'autobus."),
            _l("irene", "Trente ans que je joue contre lui. C'est le seul qui m'a jamais battue, pis il le sait.", jeu="[wryly] Trente ans que je joue contre lui. [tenderly] C'est le seul qui m'a jamais battue… pis il le sait."),
            _l("irene", "Va le voir à son école. Il est bronzé comme une galette, fais pas le saut.", jeu="[amused] Va le voir à son école. [teasing] Il est bronzé comme une galette… fais pas le saut."),
        ],
        "fin": [
            _l("maitre", "Premier cours demain, sept heures. Kenny fait le café, pis Monsieur Bois fait l'accueil.", jeu="[happy] Premier cours demain, sept heures. [amused] Kenny fait le café… pis Monsieur Bois fait l'accueil."),
            _l("irene", "Victor, je gage cinq piasses que t'en as dix au cours. Pis le pigeon, lui, il paye pas.", jeu="[teasing] Victor, je gage cinq piasses que t'en as dix au cours. [warmly] Pis le pigeon, lui… il paye pas."),
            _l("maitre", "Irène a jamais perdu une gageure. Merci, petit scarabée. Reviens t'entraîner.", jeu="[laughs] [amused] Irène a jamais perdu une gageure. [tenderly] Merci, petit scarabée. [warmly] Reviens t'entraîner."),
        ],
        "echec": [
            _e("irene", "Trois gamins en pyjama t'ont eu? J'ai encore perdu cinq piasses sur toi.", 0, jeu="[disappointed] Trois gamins en pyjama t'ont eu? [wryly] J'ai encore perdu cinq piasses sur toi."),
            _e("maitre", "Kenny a son fusil, astheure. En Floride, mes problèmes, c'étaient les alligators.", 3, jeu="[somber] Kenny a son fusil, astheure. [sighs] En Floride, mes problèmes, c'étaient les alligators."),
            _e("maitre", "Monsieur Bois a pas fait le voyage. Cinquante ans debout, pis c'est toi qui l'achèves.", 6, jeu="[somber] Monsieur Bois a pas fait le voyage. [bitterly] Cinquante ans debout… pis c'est toi qui l'achèves."),
            _e("maitre", "Les frimeurs ont gagné à soir. Mais la mante, c'est patient : on recommence demain.", 9, jeu="[disappointed] Les frimeurs ont gagné à soir. [calm] Mais la mante, c'est patient : on recommence demain."),
        ],
        "pendant": [
            _p("irene", "L'École La Mante, au nord du quartier. Cogne fort, il a pris le pli de la sieste en Floride.", 1, jeu="[teasing] L'École La Mante, au nord du quartier. [amused] Cogne fort… il a pris le pli de la sieste en Floride."),
            _p("maitre", "À mains nues, là. Un élève de la Mante, on le corrige, on le casse pas.", 2, jeu="[firmly] À mains nues, là. [warmly] Un élève de la Mante, on le corrige… on le casse pas."),
            # Acte 2 : la fin de c05, en personne ; puis l'appel et l'intro de c06.
            _p("irene", "Le club a ravoir ses tuiles, pis trois gamins ont une oreille plus longue que l'autre.", 3, jeu="[satisfied] Le club a ravoir ses tuiles… [amused] pis trois gamins ont une oreille plus longue que l'autre."),
            _p("irene", "Victor est revenu pour de bon, qu'il dit. Je gage cinq piasses qu'il repart en janvier.", 3, jeu="[wryly] Victor est revenu pour de bon, qu'il dit. [teasing] Je gage cinq piasses qu'il repart en janvier."),
            _p("irene", "Va le voir de temps en temps. Il te trouve de l'allure, pis il se trompe rarement.", 3, jeu="[warmly] Va le voir de temps en temps. [tenderly] Il te trouve de l'allure… pis il se trompe rarement."),
            # ⚠️ Coupée (2 oct. 2026) : « Sifu Tam, petit scarabée. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("maitre", "Oui, j'ai un cellulaire : ma fille me l'a acheté en Floride.", 3, jeu="[amused] Oui, j'ai un cellulaire : ma fille me l'a acheté en Floride."),
            _p("maitre", "Kenny, mon meilleur élève. À huit ans, il faisait le grand écart. À vingt-deux, il fait le caïd.", 3, jeu="[warmly] Kenny, mon meilleur élève. [wryly] À huit ans, il faisait le grand écart… À vingt-deux, il fait le caïd."),
            _p("maitre", "À soir, il s'en va chez Gus s'acheter un fusil. Un élève de la Mante, avec un fusil!", 3, jeu="[somber] À soir, il s'en va chez Gus s'acheter un fusil. [angry] Un élève de la Mante, avec un fusil!"),
            _p("maitre", "Suis-le sans klaxonner. Quand il descend, on règle ça comme à l'école : à mains nues.", 3, jeu="[firmly] Suis-le sans klaxonner. [serious] Quand il descend, on règle ça comme à l'école : à mains nues."),
            _p("maitre", "Il conduit comme dans les films, en regardant la caméra. Reste loin, il te verra pas.", 4, jeu="[amused] Il conduit comme dans les films, en regardant la caméra. [knowingly] Reste loin… il te verra pas."),
            _p("maitre", "Salue-le avant, le poing dans la paume. Après, tu le couches. C'est la politesse.", 5, jeu="[serious] Salue-le avant, le poing dans la paume. [firmly] Après, tu le couches. [playfully] C'est la politesse."),
            # Acte 3 : la fin de c06, en personne ; puis l'appel et l'intro de c07.
            _p("maitre", "Kenny balaie le plancher de l'école depuis une heure. Il chiale, mais il balaie.", 6, jeu="[satisfied] Kenny balaie le plancher de l'école depuis une heure. [amused] Il chiale… mais il balaie."),
            _p("maitre", "Un de rendu. Il en reste une gang, pis moi j'ai soixante-quatorze ans.", 6, jeu="[sighs] Un de rendu. [wryly] Il en reste une gang… pis moi j'ai soixante-quatorze ans."),
            # ⚠️ Coupée (2 oct. 2026) : « Reviens me voir demain. » — le mannequin, c'est tout de suite (l'appel de c07 suit), la même voix coupée.
            _p("maitre", "On a un mannequin de bois à aller chercher.", 6, jeu="[mysteriously] On a un mannequin de bois à aller chercher."),
            # ⚠️ Coupée (2 oct. 2026) : « C'est Sifu Tam. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("maitre", "Mes élèves ont vendu Monsieur Bois à la fourrière pour quarante piasses.", 6, jeu="[bitterly] Mes élèves ont vendu Monsieur Bois à la fourrière… pour quarante piasses."),
            _p("maitre", "Monsieur Bois, c'est le mannequin de l'école. Mille neuf cent soixante-seize, du vrai érable.", 6, jeu="[tenderly] Monsieur Bois, c'est le mannequin de l'école. [confident] Mille neuf cent soixante-seize… du vrai érable."),
            _p("maitre", "Il a mangé plus de coups que tous mes élèves ensemble. Pis il s'est jamais plaint.", 6, jeu="[warmly] Il a mangé plus de coups que tous mes élèves ensemble. [deadpan] Pis il s'est jamais plaint."),
            _p("maitre", "Gilles, à la fourrière, l'a gardé dans la boîte de son camion. Ramène-le sans une égratignure.", 6, jeu="[matter-of-fact] Gilles, à la fourrière, l'a gardé dans la boîte de son camion. [serious] Ramène-le sans une égratignure."),
            _p("maitre", "Gilles te prête son camion. Il m'a dit de te dire que c'est pas un char de course.", 7, jeu="[amused] Gilles te prête son camion. [deadpan] Il m'a dit de te dire que c'est pas un char de course."),
            _p("maitre", "Doucement dans les nids-de-poule. Monsieur Bois a mon âge, pis il a mal au dos lui aussi.", 8, jeu="[worried] Doucement dans les nids-de-poule. [wryly] Monsieur Bois a mon âge… pis il a mal au dos lui aussi."),
            # Acte 4 : la fin de c07, en personne ; puis l'appel et l'intro de c08.
            _p("maitre", "Monsieur Bois est à sa place. Regarde-le, il sourit, je te jure.", 9, jeu="[relieved] Monsieur Bois est à sa place. [amused] Regarde-le… il sourit, je te jure."),
            _p("maitre", "En échange, je t'apprends la main de la mante. Il frappe, tu accueilles, tu tournes.", 9, jeu="[serious] En échange, je t'apprends la main de la mante. [calm] Il frappe… tu accueilles… tu tournes."),
            _p("maitre", "Garde-la pour les frimeurs. Pis dis pas à Irène que c'était gratis, elle va vouloir la même.", 9, jeu="[knowingly] Garde-la pour les frimeurs. [mischievously] Pis dis pas à Irène que c'était gratis… elle va vouloir la même."),
            # ⚠️ Coupée (2 oct. 2026) : « Sifu Tam. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("maitre", "Demain matin, l'école rouvre, pis je vais le crier dans tout le quartier.", 9, jeu="[cheerful] Demain matin, l'école rouvre… pis je vais le crier dans tout le quartier."),
            _p("maitre", "J'ai imprimé des affiches. Irène en met une au Dragon d'or, entre la loto pis les dés.", 9, jeu="[confident] J'ai imprimé des affiches. [amused] Irène en met une au Dragon d'or… entre la loto pis les dés."),
            _p("maitre", "Tu marches avec moi. Les derniers frimeurs vont vouloir me faire peur.", 9, jeu="[serious] Tu marches avec moi. [knowingly] Les derniers frimeurs vont vouloir me faire peur."),
            _p("maitre", "Moi, j'ai eu peur une fois dans ma vie : un alligator dans la piscine du condo.", 9, jeu="[deadpan] Moi, j'ai eu peur une fois dans ma vie… [amused] un alligator dans la piscine du condo."),
            _p("maitre", "Marche à mon pas, petit scarabée. En Floride, personne court, il fait trop chaud.", 10, jeu="[casually] Marche à mon pas, petit scarabée. [amused] En Floride, personne court… il fait trop chaud."),
            _p("maitre", "Les voilà. Je tiens l'affiche, tu tiens le reste.", 11, jeu="[calm] Les voilà. [firmly] Je tiens l'affiche… tu tiens le reste."),
        ],
        "accueil": [
            _a("maitre", "Victor Tam. Sifu, pour mes élèves, pis pour toi aussi, tant qu'à faire.", 1, jeu="[cheerful] Victor Tam. [playfully] Sifu, pour mes élèves… pis pour toi aussi, tant qu'à faire."),
            _a("maitre", "Trois de mes élèves font les fanfarons au mah-jong. Ramène-les-moi par l'oreille, petit scarabée.", 1, jeu="[somber] Trois de mes élèves font les fanfarons au mah-jong. [amused] Ramène-les-moi par l'oreille… petit scarabée."),
        ],
    },
}
