"""Le chapitre de Lulu et le poisson — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague Q). Lulu, à sa cantine des Quais : q02 (le camion de poisson du vendredi, livré sans une bosse au casse-croûte du sergent)
et q01 (les Morues qui mangent sans payer, et le quatrième parti avec la caisse) — cinq et trois étapes, deux ACTES
(6 à 8 minutes).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : l'appel de q01 perd « Allô, mon grand, c'est Lulu! » — la même voix,
  coupée au silence ;
- le bonus « sans une bosse » de q02 se paie à la fin de l'acte 1, avec sa prime (`Histoire.avancer`) ;
- ⚠️ ÉCART : q02 ne ratait pas à la mort (son échec : arrêté, le camion détruit) ; le chapitre rate aussi quand on meurt.
- Ce qui attendait q02 l'attend encore — l'acte 1 (le chapitre de Raymonde, m51, q04) : un prérequis peut viser un acte.
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "lulu_et_le_poisson",
    "titre": "Lulu et le poisson",
    "donneur": "lulu",
    "prerequis": ["e01"],
    "remplace": ["q02", "q01"],
    "recompense": 150,
    "donne": {"rabais": {"cantine": 0.75}, "message": "LA CANTINE, −25 % POUR TOI"},
    "echec": ["arrete", "vehicule_detruit", "mort"],

    "objectifs": [
        # --- Acte 1 (q02, « Le poisson du vendredi »).
        {"type": "acte", "texte": "ACTE 1 — LE POISSON DU VENDREDI", "donneur": "lulu"},  # 0
        {"type": "monter", "texte": "PRENDS LE CAMION DE POISSON DANS LA RUELLE", "vehicule": "camion", "ou": "ruelle:cantine:10"},  # 1
        {"type": "parler", "texte": "ARRÊTE CHERCHER DE LA GLACE CHEZ TI-PAUL", "cible": "tipaul"},  # 2
        {"type": "livrer", "texte": "LIVRE LE POISSON AU CASSE-CROÛTE, SANS BOSSE", "lieu": "casse_croute", "rayon": 4, "sans_degats": True},  # 3
        {"type": "parler", "texte": "FAIS PAYER LE SERGENT, AU CASSE-CROÛTE", "cible": "bouchard"},  # 4
        {"type": "aller", "texte": "RAPPORTE L'ARGENT À LULU, À LA CANTINE", "lieu": "cantine", "rayon": 4, "donne": {"message": "LE POISSON EST ARRIVÉ ENTIER", "prime": 250}},  # 5
        # --- Acte 2 (q01, « La cantine de Lulu »).
        {"type": "acte", "texte": "ACTE 2 — LA CANTINE DE LULU", "donneur": "lulu"},  # 6
        {"type": "tuer", "texte": "VA PRÉSENTER LA FACTURE AUX TROIS MORUES", "groupe": "morues", "n": 3, "ou": "zone:morues", "arme": "", "vie": 60},  # 7
        {"type": "ramasser", "texte": "LE QUATRIÈME EST PARTI AVEC LA CAISSE DU MIDI", "cible": "fuyard", "vehicule": "auto"},  # 8
        {"type": "aller", "texte": "RAPPORTE LA CAISSE À LA CANTINE", "lieu": "cantine", "rayon": 6},  # 9
    ],

    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "ruelle:cantine:10", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
    },

    # q02 — Le jeu de chaque réplique (`jeu=`) — Lulu, le poisson du vendredi : la cantinière qui
    # materne et qui taquine — l'urgence est drôle (un camion de morue), jamais grave. La fin
    # passe la main à Raymonde, avec un clin d'œil.
    # q01 — Le jeu de chaque réplique (`jeu=`) — Lulu : fâchée pour de rire, puis pour de vrai
    # quand la caisse part ; elle materne en se moquant, et finit en nourrissant.
    "dialogue": {
        "appel": [
            _l("lulu", "Allô, mon grand, c'est Lulu! J'ai un camion de poisson sans chauffeur, pis c'est vendredi. Viens vite!", jeu="[excited] Allô, mon grand, c'est Lulu! J'ai un camion de poisson sans chauffeur… pis c'est vendredi. Viens vite!"),
        ],
        "intro": [
            _l("lulu", "Le camion est dans une ruelle, plein de morue. Le chauffeur s'est pogné la main dans sa glacière.", jeu="[warmly] Le camion est dans une ruelle, plein de morue. [amused] Le chauffeur s'est pogné la main… dans sa glacière."),
            _l("lulu", "Livre-le au casse-croûte du Faubourg. Pis conduis doucement: le poisson, ça se bosse pas.", jeu="[firmly] Livre-le au casse-croûte du Faubourg. [teasing] Pis conduis doucement… le poisson, ça se bosse pas."),
        ],
        "fin": [
            _l("lulu", "Toute la caisse, pis même le pourboire! T'es mieux qu'un chien de garde, toi.", jeu="[relieved] Toute la caisse, pis même le pourboire! [amused] T'es mieux qu'un chien de garde, toi."),
            _l("lulu", "Pour toi, c'est moins cher à partir d'astheure. Mange, t'as encore l'air d'un fantôme.", jeu="[warmly] Pour toi, c'est moins cher à partir d'astheure. [teasing] Mange… t'as encore l'air d'un fantôme."),
        ],
        "echec": [
            _e("lulu", "Mon poisson… Ben tant pis, on va le faire en soupe. Reviens quand tu conduis mieux.", 0, jeu="[disappointed] Mon poisson… Ben tant pis, on va le faire en soupe. [teasing] Reviens quand tu conduis mieux."),
            _e("lulu", "Ma caisse est partie, pis mon dessert avec. Reviens quand t'auras mangé.", 6, jeu="[disappointed] Ma caisse est partie… pis mon dessert avec. [warmly] Reviens quand t'auras mangé."),
        ],
        "pendant": [
            _p("lulu", "Oublie pas la glace chez Ti-Paul! Sans glace, ma morue va se sauver toute seule.", 2, jeu="[worried] Oublie pas la glace chez Ti-Paul! [teasing] Sans glace, ma morue va se sauver… toute seule."),
            _p("lulu", "Doucement dans les tournants! Le sergent veut son poisson frais, pas en purée.", 3, jeu="[worried] Doucement dans les tournants! [playfully] Le sergent veut son poisson frais… pas en purée."),
            _p("lulu", "Fais-le payer, le sergent! Pis compte les billets devant lui, hein.", 4, jeu="[firmly] Fais-le payer, le sergent! [teasing] Pis compte les billets devant lui, hein."),
            _p("lulu", "Rapporte-moi ça vite, mon grand. Pis mange en chemin, t'as l'air d'un fantôme.", 5, jeu="[warmly] Rapporte-moi ça vite, mon grand. [teasing] Pis mange en chemin… t'as l'air d'un fantôme."),
            # Acte 2 : la fin de q02, en personne ; puis l'appel et l'intro de q01.
            _p("lulu", "Pas une écaille de perdue! Le sergent va être content, pis moi, j'suis payée.", 6, jeu="[relieved] Pas une écaille de perdue! [cheerful] Le sergent va être content, pis moi, j'suis payée."),
            _p("lulu", "Pis le sergent a payé? Ben coudonc. Y va pleuvoir des poissons.", 6, jeu="[surprised] Pis le sergent a payé? [amused] Ben coudonc… Y va pleuvoir des poissons."),
            _p("lulu", "Passe voir Raymonde, à l'usine. Elle cherche quelqu'un qui conduit bien, pis qui pose pas de questions.", 6, jeu="[knowingly] Passe voir Raymonde, à l'usine. Elle cherche quelqu'un qui conduit bien… pis qui pose pas de questions."),
            # ⚠️ Coupée (2 oct. 2026) : « Allô, mon grand, c'est Lulu! » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("lulu", "J'ai trois Morues qui mangent chez nous depuis lundi, pis pas une cenne.", 6, jeu="[teasing] J'ai trois Morues qui mangent chez nous depuis lundi… pis pas une cenne."),
            _p("lulu", "C'est les gars de ma sœur. Josée dit qu'une Morue, ça paie pas dans la famille.", 6, jeu="[wryly] C'est les gars de ma sœur. [annoyed] Josée dit qu'une Morue… ça paie pas dans la famille."),
            _p("lulu", "Moi, je dis que c'est mes assiettes. Va leur porter la facture, dans leur coin du port.", 6, jeu="[firmly] Moi, je dis que c'est mes assiettes. [teasing] Va leur porter la facture… dans leur coin du port."),
            _p("lulu", "Pis dis rien à Josée. Ce qu'elle sait pas, ça la fâche pas.", 6, jeu="[playfully] Pis dis rien à Josée. [knowingly] Ce qu'elle sait pas… ça la fâche pas."),
            _p("lulu", "Ils digèrent mon dessert au bout du quai! Vas-y, mon grand.", 7, jeu="[excited] Ils digèrent mon dessert au bout du quai! [warmly] Vas-y, mon grand."),
            _p("lulu", "Le quatrième est parti avec la caisse du midi! Rattrape-le avant qu'il la mange.", 8, jeu="[worried] Le quatrième est parti avec la caisse du midi! [teasing] Rattrape-le… avant qu'il la mange."),
            _p("lulu", "Rapporte-moi ça. Je te garde une assiette chaude.", 9, jeu="[warmly] Rapporte-moi ça. [cheerful] Je te garde une assiette chaude."),
        ],
        "accueil": [
            _a("tipaul", "Ta glace, l'ami! Dis à Lulu qu'a me doit deux sacs, pis un café.", 2, jeu="[cheerful] Ta glace, l'ami! [mischievously] Dis à Lulu qu'a me doit deux sacs… pis un café."),
            _a("bouchard", "Le jeune. Tiens, pour Lulu. Pis dis-lui que le pourboire, c'est ma protection.", 4, jeu="[gruffly] Le jeune. Tiens, pour Lulu. [deadpan] Pis dis-lui que le pourboire… c'est ma protection."),
        ],
    },
}
