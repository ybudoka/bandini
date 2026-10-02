"""Le chapitre de la chute du Pouce — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague C). Martin a tranché
pour les arcs hors de la liste de M16 : les quatre jobs d'Irène contre le Pouce (c01 à c04, une à trois étapes
chacune) deviennent quatre ACTES — le jeton du sous-sol, les dés pipés, le livre de comptes, la caisse du quartier.
Visée : 8 à 10 minutes. Rien d'ajouté pour faire durer : la barbotte, la filature et le chrono du livre tiennent
déjà leur part. Mourir en filant le comptable fait reprendre la suite royale, pas la barbotte.

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de c01
  restent ceux du chapitre ; la fin de chaque job se dit à l'ouverture de l'acte suivant, suivie de l'appel et de
  l'intro du job suivant ; la fin de c04 reste la fin du chapitre ; chaque job garde son échec (`_e`, à son acte) ;
- QUI PARLE SE NOMME une fois par chapitre : Irène se nomme à l'appel de c01 ; ses trois appels suivants perdent
  « C'est Irène Lam, mon pigeon », « Irène Lam, mon pigeon » et « Irène Lam » — la même voix, coupée au silence ;
- chaque acte paie sa prime en finissant (`donne` sur l'objectif qui le finit), et la mission qu'il remplace est
  faite à l'ouverture de l'acte suivant : LA PORTE DU SOUS-SOL s'ouvre à l'acte 2 (`tripot.PORTE`, `apres: c01`),
  et LE TRIPOT CHANGE DE MAINS à la fin du chapitre (`tripot.REPRISE`, `apres: c04`), avec la une du Clairon ; le
  vieux maître arrive après c04 (`arrive_apres`) : il est là pour le chapitre suivant, `retour_du_maitre` ;
- ⚠️ L'`exige` de c02 (500 $ en poche) tombe : il aurait fermé le chapitre dès l'acte 1. La ligne d'objectif dit
  « MISE 500 $ », et Irène le redit à l'objectif (« Cinq cents piasses, pas moins ») : sous 500 $, le Pouce ne
  sort pas ses pipés, et l'acte attend qu'on revienne avec de quoi miser ;
- l'acte 4 commence au terminus, où l'acte 3 finit : le chauffeur du Pouce file de là (le fuyard naît près du
  joueur), et la caisse se rapporte au Dragon d'or comme avant ;
- la scène d'intro de c01 reste celle du chapitre, la scène de fin de c04 celle de sa fin ; les scènes écrites de
  c02, c03 et c04 (intro) et de c01 à c03 (fin) tombent : leurs répliques se disent au marqueur, comme au pilote.
"""

from ._commun import _a, _e, _l, _p, _r

MISSION = {
    "slug": "chute_du_pouce",
    "titre": "La chute du Pouce",
    "donneur": "irene",
    "prerequis": ["m6"],
    "remplace": ["c01", "c02", "c03", "c04"],
    "recompense": 1500,
    "donne": {"message": "LE TRIPOT EST À IRÈNE · LES DÉS SONT BLANCS", "manchette": "pouce_parti"},

    "objectifs": [
        # --- Acte 1 (c01, « La barbotte du Pouce »).
        # La première du Petit-Canton (docs/jalons/le-quartier-chinois.md, étape 3 ; docs/jalons/le-casino-du-petit-canton.md,
        # vague 4). Irène Lam, trente ans croupière au Dragon d'or, t'envoie prendre un jeton de laiton aux rabatteurs du
        # Pouce Vachon — le jeton qui ouvre la porte du sous-sol, où le Pouce tient sa barbotte aux dés pipés. La porte
        # (`tripot.PORTE`, une barrière de la grande salle) s'ouvre quand la mission est faite (`apres: c01`).
        {"type": "acte", "texte": "ACTE 1 — LA BARBOTTE DU POUCE", "donneur": "irene"},  # 0
        {"type": "tuer", "texte": "LES RABATTEURS DU POUCE, AU TERMINUS", "groupe": "cravates", "n": 2, "ou": "porte:terminus", "arme": "", "vie": 70},  # 1
        {"type": "aller", "texte": "RAPPORTE UN JETON AU DRAGON D'OR", "lieu": "nord_casino", "rayon": 6, "donne": {"message": "LA PORTE DU SOUS-SOL T'EST OUVERTE", "prime": 400}},  # 2
        # --- Acte 2 (c02, « Une paire dans la manche »).
        # La deuxième du Petit-Canton, la première de la chute du Pouce (docs/jalons/le-quartier-chinois.md, étape 3 ; Martin,
        # 29 sept. 2026 : « on fait tomber le Pouce pour de bon »). Irène veut ses dés pipés DANS SA MAIN : « il a l'air
        # croche », ça ne fait tomber personne. Au sous-sol, on mise gros ; quand le Pouce glisse ses pipés sur le feutre, on
        # lui fait son propre truc — GLISSER TES DÉS : les siens dans ta manche, une paire honnête à la place
        # (`Tripot.glisser`, `tripot.PREUVE`). L'objectif `obtenir` a une `table` : l'objet ne se pose nulle part en ville,
        # il vient du feutre. Il avance à la sortie, comme tout objectif (dans une pièce, `majObjectif` dort).
        {"type": "acte", "texte": "ACTE 2 — UNE PAIRE DANS LA MANCHE", "donneur": "irene"},  # 3
        {"type": "obtenir", "texte": "EMPOCHE LES DÉS JAUNES DU POUCE — MISE 500 $", "objet": "des_pipes", "ou": "nord_casino", "table": "tripot", "nom": "LES DÉS PIPÉS DU POUCE", "donne": {"message": "LES DÉS DU POUCE SONT DANS TA POCHE", "prime": 500}},  # 4
        # --- Acte 3 (c03, « La suite royale »).
        # La chute du Pouce, deuxième temps (docs/jalons/le-quartier-chinois.md, étape 3). Les dés prouvent la triche ; Irène
        # veut maintenant l'ARGENT DU MONDE — et un tricheur écrit tout ce qu'il gagne. Le Pouce loge à l'Hôtel Bandini, dans
        # la suite royale (⚠️ pas la chambre 12 : c'est celle de q07, en brouillon). On fait jaser le concierge, qui ne dit
        # jamais le nom d'un client mais vend tout le reste ; on file le comptable du Pouce, qui porte le livre au terminus
        # pour les rabatteurs ; on le ramasse avant eux, sur le chrono.
        {"type": "acte", "texte": "ACTE 3 — LA SUITE ROYALE", "donneur": "irene"},  # 5
        {"type": "parler", "texte": "À L'HÔTEL, FAIS JASER NORBERT SUR LA SUITE ROYALE", "cible": "norbert"},  # 6
        {"type": "suivre", "texte": "SUIS LE COMPTABLE DU POUCE SANS TE FAIRE REPÉRER", "vehicule": "auto", "loin": 10, "proche": 3, "lieu": "terminus"},  # 7
        {"type": "obtenir", "texte": "RAMASSE SON LIVRE AVANT LES RABATTEURS", "objet": "livre_du_pouce", "ou": "terminus", "dessin": "registre", "nom": "LE LIVRE DE COMPTES DU POUCE", "chrono_s": 30, "donne": {"message": "LE LIVRE DE COMPTES DU POUCE EST À TOI", "prime": 600}},  # 8
        # --- Acte 4 (c04, « La barbotte change de mains »).
        # La chute du Pouce, pour de bon (Martin, 29 sept. 2026). Il a vu que son livre manquait : ce soir, il vide la caisse
        # du sous-sol — la paye du quartier — et il sort par la porte d'en arrière, celle des descentes de police. Son
        # chauffeur file avec elle (`ramasser`, `cible: fuyard`) ; on l'accroche, on reprend la caisse, et le Pouce, lui, prend
        # l'autobus de Sorel en jurant qu'il déménage. On la rapporte au Dragon d'or.
        #
        # ⚠️ **LE TRIPOT CHANGE DE MAINS** (`tripot.REPRISE`, `apres: c04`) : le Pouce et ses gros bras ne sont plus là, le
        # vieux Chan tient la barbotte pour Irène, les dés sont blancs pour de vrai, plus de méfiance ni de semaine barrée, et
        # la piastre va au quartier. Le lendemain matin, le Clairon en fait sa une (`donne.manchette`, `journal.SPECIALES`).
        {"type": "acte", "texte": "ACTE 4 — LA BARBOTTE CHANGE DE MAINS", "donneur": "irene"},  # 9
        {"type": "ramasser", "texte": "LE CHAUFFEUR DU POUCE FILE AVEC LA CAISSE — ACCROCHE-LE", "cible": "fuyard", "vehicule": "auto"},  # 10
        {"type": "aller", "texte": "RAPPORTE LA CAISSE DU QUARTIER AU DRAGON D'OR", "lieu": "nord_casino", "rayon": 6},  # 11
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "porte:terminus", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:irene", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 40},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # c01 — Le jeu de chaque réplique (`jeu=`) — Irène : l'aplomb amusé de qui a vu passer trente ans de joueurs, qui
    # gage sur tout et taquine le neveu (« mon pigeon ») ; la colère froide quand elle parle des voisins que le
    # Pouce a plumés ; et, à la fin, le ton d'une professeure qui livre le truc du métier. Elle se nomme à l'appel,
    # une fois, à sa façon : « Madame Lam pour toi ».
    # c02 — Le jeu de chaque réplique (`jeu=`) — Irène : la croupière qui passe un truc du métier à son élève, à voix
    # basse, avec le plaisir de qui attend ce moment depuis longtemps ; le « je gage » en taquinerie ; au combiné, à
    # la fin, l'émerveillement retenu d'une professionnelle devant un beau geste — puis elle pense déjà à l'argent
    # du monde. Elle se nomme à l'appel, une fois.
    # c03 — Le jeu de chaque réplique (`jeu=`) — Irène : la joueuse qui a flairé la faille (« un tricheur écrit tout »),
    # le sourire en coin ; puis, en parlant du vieux Chan et de la boulangère, la colère froide qui la fait tenir ;
    # à la fin, en lisant le livre au combiné, le mépris amusé devant une si belle main d'écriture. Norbert : le
    # service qui dit tout en n'ayant rien dit — calme, bas, jamais surpris, et il ne nomme pas son client. Irène se
    # nomme à l'appel ; Norbert, connu depuis f10, ne se représente pas.
    # c04 — Le jeu de chaque réplique (`jeu=`) — Irène : ce soir, plus de taquinerie d'abord ; la croupière devient
    # sérieuse, pressée, froide envers le Pouce — puis, la caisse rentrée, la tendresse qu'elle cachait sous les
    # gages, et une dernière taquinerie pour la route. Le Pouce : un beau parleur qui perd, et qui fait encore le
    # fier en se sauvant — la mauvaise foi joviale, jamais la menace. Irène se nomme à l'appel ; le Pouce, qu'on
    # entend pour la première fois, se nomme lui-même, à la troisième personne, comme un homme qui s'aime.
    "dialogue": {
        "appel": [
            _l("irene", "Irène Lam, du Dragon d'or. Madame Lam pour toi, tant que tu m'as pas battue au mah-jong.", jeu="[amused] Irène Lam, du Dragon d'or. [teasing] Madame Lam pour toi… tant que tu m'as pas battue au mah-jong."),
        ],
        "intro": [
            _l("irene", "Sous nos pieds, le Pouce Vachon tient une barbotte. Il a loué la cave pour entreposer des chaises.", jeu="[quietly] Sous nos pieds, le Pouce Vachon tient une barbotte. [wryly] Il a loué la cave pour entreposer des chaises."),
            _l("irene", "Ses dés sont pipés. Le vieux Chan y a laissé sa pension, pis la boulangère son camion.", jeu="[bitterly] Ses dés sont pipés. [somber] Le vieux Chan y a laissé sa pension… pis la boulangère son camion."),
            _l("irene", "On y entre avec un jeton de laiton. Ses rabatteurs en ont plein les poches, au terminus.", jeu="[knowingly] On y entre avec un jeton de laiton. [firmly] Ses rabatteurs en ont plein les poches, au terminus."),
        ],
        "fin": [
            _l("irene", "Le vieux Chan a sa pension, pis la boulangère s'achète un camion. Usagé, mais neuf pour elle.", jeu="[warmly] Le vieux Chan a sa pension, pis la boulangère s'achète un camion. [amused] Usagé… mais neuf pour elle."),
            _l("irene", "La barbotte d'en bas, c'est à moi, astheure. Des dés blancs, pis la piastre au quartier.", jeu="[satisfied] La barbotte d'en bas, c'est à moi, astheure. [firmly] Des dés blancs… pis la piastre au quartier."),
            _l("irene", "Pis toi, t'as une place à ma table de mah-jong. Tu vas perdre, mais t'as une place.", jeu="[tenderly] Pis toi, t'as une place à ma table de mah-jong. [teasing] Tu vas perdre… mais t'as une place."),
        ],
        "echec": [
            _e("irene", "Les rabatteurs courent encore. Pis moi, j'ai perdu cinq piasses sur toi.", 0, jeu="[disappointed] Les rabatteurs courent encore. [wryly] Pis moi, j'ai perdu cinq piasses sur toi."),
            _e("irene", "Pas de dés, pas de preuve. Je vas finir par manquer de cinq piasses, avec toi.", 3, jeu="[disappointed] Pas de dés, pas de preuve. [wryly] Je vas finir par manquer de cinq piasses, avec toi."),
            _e("irene", "Le livre nous a filé entre les doigts. La chance, ça existe pas : on était juste pas là.", 5, jeu="[disappointed] Le livre nous a filé entre les doigts. [wryly] La chance, ça existe pas… on était juste pas là."),
            _e("irene", "La caisse est partie avec lui. Le quartier va se souvenir du Pouce longtemps.", 9, jeu="[bitterly] La caisse est partie avec lui. [somber] Le quartier va se souvenir du Pouce… longtemps."),
        ],
        "pendant": [
            _p("irene", "Deux gars en cravate qui offrent des jetons aux perdants de l'autobus. Tu peux pas les manquer.", 1, jeu="[wryly] Deux gars en cravate qui offrent des jetons aux perdants de l'autobus. [amused] Tu peux pas les manquer."),
            _p("irene", "Un jeton, c'est assez. Reviens au Dragon d'or, je gage cinq piasses que t'as pas un bleu.", 2, jeu="[satisfied] Un jeton, c'est assez. [teasing] Reviens au Dragon d'or… je gage cinq piasses que t'as pas un bleu."),
            # Acte 2 : la fin de c01, en personne ; puis l'appel et l'intro de c02.
            _p("irene", "Montre le jeton au gros de l'escalier. En bas, joue gros, pis regarde les mains du Pouce.", 3, jeu="[knowingly] Montre le jeton au gros de l'escalier. [firmly] En bas, joue gros… pis regarde les mains du Pouce."),
            _p("irene", "Quand ses dés sont plus jaunes que les vrais, c'est de la vieille ivoire pipée. Change de côté, ou crie-le.", 3, jeu="[quietly] Quand ses dés sont plus jaunes que les vrais, c'est de la vieille ivoire pipée. [amused] Change de côté… ou crie-le."),
            _p("irene", "Pis perds pas tout. La chance, ça existe pas, y a juste du monde qui sait compter.", 3, jeu="[warmly] Pis perds pas tout. [knowingly] La chance, ça existe pas… y a juste du monde qui sait compter."),
            # ⚠️ Coupée (2 oct. 2026) : « C'est Irène Lam, mon pigeon. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("irene", "J'ai un tour de passe-passe à te montrer, pis c'est pas avec des cartes.", 3, jeu="[teasing] J'ai un tour de passe-passe à te montrer… pis c'est pas avec des cartes."),
            _p("irene", "Pour faire tomber le Pouce, « il a l'air croche », ça suffit pas. Il me faut ses dés jaunes, dans ma main.", 3, jeu="[quietly] Pour faire tomber le Pouce, « il a l'air croche »… ça suffit pas. [firmly] Il me faut ses dés jaunes, dans ma main."),
            _p("irene", "Tiens, une paire honnête. Mise gros, pis quand ses pipés arrivent sur le feutre, glisse les tiens.", 3, jeu="[knowingly] Tiens, une paire honnête. [quietly] Mise gros, pis quand ses pipés arrivent sur le feutre… glisse les tiens."),
            _p("irene", "C'est son truc à lui. Je gage cinq piasses qu'il a jamais pensé qu'on lui ferait.", 3, jeu="[amused] C'est son truc à lui. [teasing] Je gage cinq piasses qu'il a jamais pensé qu'on lui ferait."),
            _p("irene", "Cinq cents piasses, pas moins. En bas de ça, il se donne même pas la peine de tricher.", 4, jeu="[matter-of-fact] Cinq cents piasses, pas moins. [wryly] En bas de ça, il se donne même pas la peine de tricher."),
            # Acte 3 : la fin de c02, en personne ; puis l'appel et l'intro de c03.
            _p("irene", "T'es sorti avec, pis il a rien vu? Trente ans que j'attends de voir ça.", 5, jeu="[impressed] T'es sorti avec, pis il a rien vu? [amused] Trente ans que j'attends de voir ça."),
            _p("irene", "Garde-les dans ta poche. C'est la place la plus sûre du quartier, astheure.", 5, jeu="[knowingly] Garde-les dans ta poche. [teasing] C'est la place la plus sûre du quartier, astheure."),
            _p("irene", "Mais des dés, c'est juste la triche. Moi, je veux savoir où dort l'argent du monde.", 5, jeu="[serious] Mais des dés… c'est juste la triche. [firmly] Moi, je veux savoir où dort l'argent du monde."),
            # ⚠️ Coupée (2 oct. 2026) : « Irène Lam, mon pigeon. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("irene", "Le Pouce couche dans la suite royale de l'hôtel, pis je gage qu'il dort sur un livre.", 5, jeu="[mischievously] Le Pouce couche dans la suite royale de l'hôtel… pis je gage qu'il dort sur un livre."),
            _p("irene", "Un tricheur écrit tout ce qu'il gagne. Pas pour l'impôt : pour se le relire, le soir.", 5, jeu="[knowingly] Un tricheur écrit tout ce qu'il gagne. [wryly] Pas pour l'impôt… pour se le relire, le soir."),
            _p("irene", "Le concierge de l'hôtel sait tout, pis il le vend. Va le faire jaser sur la suite royale.", 5, jeu="[matter-of-fact] Le concierge de l'hôtel sait tout, pis il le vend. [firmly] Va le faire jaser sur la suite royale."),
            _p("irene", "Avec ce livre-là, le vieux Chan pis la boulangère ravoient leur argent. À la cenne.", 5, jeu="[somber] Avec ce livre-là, le vieux Chan pis la boulangère ravoient leur argent. [firmly] À la cenne."),
            _p("irene", "Il regarde ses chiffres, pas son rétroviseur. Reste pas collé dessus quand même.", 7, jeu="[amused] Il regarde ses chiffres, pas son rétroviseur. [firmly] Reste pas collé dessus quand même."),
            _p("irene", "Il l'a laissé au terminus pour les rabatteurs? Ramasse-le avant eux, vite!", 8, jeu="[surprised] Il l'a laissé au terminus pour les rabatteurs? [firmly] Ramasse-le avant eux, vite!"),
            # Acte 4 : la fin de c03, en personne ; puis l'appel et l'intro de c04.
            _p("irene", "« Chan, trois mille deux cents. Boulangerie, un camion. » Il a une belle main d'écriture, pour un voleur.", 9, jeu="[bitterly] « Chan, trois mille deux cents. Boulangerie, un camion. » [sarcastic] Il a une belle main d'écriture, pour un voleur."),
            _p("irene", "Pis en bas de la page, ce qu'il doit à ses rabatteurs. Il les paye même pas.", 9, jeu="[amused] Pis en bas de la page, ce qu'il doit à ses rabatteurs. [wryly] Il les paye même pas."),
            _p("irene", "Garde le livre. Demain, on va lui présenter sa facture.", 9, jeu="[firmly] Garde le livre. [satisfied] Demain… on va lui présenter sa facture."),
            # ⚠️ Coupée (2 oct. 2026) : « Irène Lam. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("irene", "Le Pouce a vu que son livre manquait, pis il fait ses valises à soir.", 9, jeu="[quietly] Le Pouce a vu que son livre manquait… pis il fait ses valises à soir."),
            _p("irene", "Il vide la caisse du sous-sol. Cette caisse-là, mon pigeon, c'est la paye du quartier.", 9, jeu="[serious] Il vide la caisse du sous-sol. [somber] Cette caisse-là, mon pigeon… c'est la paye du quartier."),
            _p("irene", "Il va sortir par la porte d'en arrière, celle des descentes de police. Il connaît le chemin.", 9, jeu="[knowingly] Il va sortir par la porte d'en arrière, celle des descentes de police. [wryly] Il connaît le chemin."),
            _p("irene", "Rattrape-la. Moi, je descends lui dire deux mots, avec ses dés pis son livre.", 9, jeu="[firmly] Rattrape-la. [coldly] Moi, je descends lui dire deux mots… avec ses dés pis son livre."),
            _p("irene", "C'est son chauffeur qui a la caisse! Une Cravate qu'il paye, pis mal. Accroche-le!", 10, jeu="[surprised] C'est son chauffeur qui a la caisse! [wryly] Une Cravate qu'il paye, pis mal. [firmly] Accroche-le!"),
            _p("pouce", "Réal Vachon se sauve pas, le jeune, il déménage! Garde-la, ta caisse, j'ai un autobus pour Sorel.", 11, jeu="[smugly] Réal Vachon se sauve pas, le jeune… il déménage! [sarcastic] Garde-la, ta caisse, j'ai un autobus pour Sorel."),
            _p("irene", "Laisse-le courir, il court mal. Ramène la caisse au Dragon d'or, le monde attend.", 11, jeu="[amused] Laisse-le courir, il court mal. [warmly] Ramène la caisse au Dragon d'or… le monde attend."),
        ],
        "renvoi": [
            _r("irene", "Pas ici, voyons! En bas, à la barbotte. Pis quand c'est fait, sors d'icitte sans courir.", 4, jeu="[surprised] Pas ici, voyons! [quietly] En bas, à la barbotte. [firmly] Pis quand c'est fait… sors d'icitte sans courir."),
        ],
        "accueil": [
            _a("norbert", "Je crains que la suite royale ne soit pas libre. Son locataire paie d'avance, en billets pliés en quatre.", 6, jeu="[calm] Je crains que la suite royale ne soit pas libre. [knowingly] Son locataire paie d'avance… en billets pliés en quatre."),
            _a("norbert", "Son comptable sort par ici chaque soir, un livre sous le bras. Monsieur ne tient pas ce renseignement de moi.", 6, jeu="[quietly] Son comptable sort par ici chaque soir, un livre sous le bras. [calm] Monsieur ne tient pas ce renseignement de moi."),
        ],
    },
}
