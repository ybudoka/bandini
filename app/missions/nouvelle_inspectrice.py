"""Le chapitre de la nouvelle inspectrice — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague R). Roy contre
Bouchard commence par trois missions qui se suivent : r01 (Bouchard, le carnet volé, sans une étoile), r05 (Bouchard,
le camion des pièces à conviction) et r02 (Roy te convoque) — deux à quatre étapes chacune. Trois ACTES : on couvre
le sergent deux fois, puis l'inspectrice te tend sa main. Rien d'ajouté : deux nuits au poste, une filature sans
étoile, deux polices à semer (7 à 9 minutes).

Ce qui a bougé, et pourquoi :
- r05 passe AVANT r02 : il n'attendait que r01, et le sergent te demande deux services avant que Roy te convoque ;
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de r01
  restent ceux du chapitre ; la fin de chaque mission se dit à l'ouverture de l'acte suivant, suivie de l'appel et de
  l'intro de la suivante ; la fin de r02 reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : l'appel de r05 perd « Bouchard. » ; et l'intro de Roy, dite au combiné
  (elle est au poste, tu es au garage), perd « Assis-toi. » — la même voix, coupée au silence ;
- l'échec `etoile` de r01 voyage avec le chapitre : il ne se déclenche que par `sans_etoile`, sur ses objectifs ;
- la scène d'intro de r01 reste celle du chapitre.
- Le CHOIX qui suit (r03, le stool, ou r04, le sergent contre-attaque — chacune ferme l'autre) reste en missions, avec
  leurs suites (r06, r08 ; r07) : un acte ne sait pas fermer l'autre bord. Elles attendent r02 (le dernier acte).
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "nouvelle_inspectrice",
    "titre": "La nouvelle inspectrice",
    "donneur": "bouchard",
    "prerequis": ["m6"],
    "remplace": ["r01", "r05", "r02"],
    "recompense": 150,
    "donne": {"message": "ROY OU BOUCHARD : À TOI DE CHOISIR TA POLICE"},
    "echec": ["mort", "arrete", "etoile"],

    "objectifs": [
        # --- Acte 1 (r01, « La nouvelle inspectrice »).
        {"type": "acte", "texte": "ACTE 1 — LA NOUVELLE INSPECTRICE", "donneur": "bouchard"},  # 0
        {"type": "aller", "texte": "VA AU POSTE, DE NUIT", "lieu": "poste", "rayon": 6, "nuit": True},  # 1
        {"type": "ramasser", "texte": "RATTRAPE-LE AVANT QU'IL DISPARAISSE", "cible": "fuyard", "vehicule": "auto", "sans_etoile": True},  # 2
        {"type": "semer", "texte": "ROY T'A VU PARTIR, SÈME-LA", "etoiles": 1},  # 3
        {"type": "aller", "texte": "CACHE LE CARNET À L'HÔTEL, SANS ÉTOILE", "lieu": "hotel", "rayon": 4, "sans_etoile": True, "donne": {"message": "LE CARNET, EN LIEU SÛR", "prime": 300}},  # 4
        # --- Acte 2 (r05, « La salle des pièces »).
        # La salle des pièces (M16, arc R, 30 sept. 2026). Les armes saisies au Faubourg — celles des Cravates, et quelques-unes
        # à toi — partent cette nuit pour Québec dans le camion des pièces à conviction. Bouchard aimerait mieux qu'elles ne
        # témoignent jamais : on vole le camion dans la ruelle du poste, deux étoiles, on les sème, et on le mène au garage de
        # Rocco, où un camion peut disparaître.
        # ⚠️ La fiche voulait « ramasser trois armes dans la salle des pièces, dedans » : un objectif ne se joue pas dans une
        # pièce (`majObjectif` dort dedans) — la salle des pièces part en camion.
        {"type": "acte", "texte": "ACTE 2 — LA SALLE DES PIÈCES", "donneur": "bouchard"},  # 5
        {"type": "aller", "texte": "À LA NUIT, AU POSTE : LE CAMION PART POUR QUÉBEC", "lieu": "poste", "rayon": 8, "nuit": True},  # 6
        {"type": "monter", "texte": "LE CAMION DES PIÈCES À CONVICTION : PRENDS-LE", "vehicule": "camion", "ou": "ruelle:poste:12"},  # 7
        {"type": "semer", "texte": "DEUX ÉTOILES : UN CAMION DE LA POLICE, ÇA SE CHERCHE", "etoiles": 2},  # 8
        {"type": "livrer", "texte": "LE CAMION AU GARAGE DE TON ONCLE", "lieu": "garage", "rayon": 5, "donne": {"message": "LES PIÈCES À CONVICTION N'ARRIVERONT JAMAIS À QUÉBEC", "prime": 250}},  # 9
        # --- Acte 3 (r02, « Roy te convoque »).
        # Roy te convoque (M16, arc R « Roy contre Bouchard », 30 sept. 2026). L'inspectrice Claudine Roy sait qui a volé son
        # carnet (r01) et où Bouchard l'a caché : dans le coffre de l'Hôtel Bandini. Elle ne te fait pas arrêter ; elle veut
        # son carnet, et elle veut savoir de quel côté tu es. On va le chercher à l'hôtel — Norbert ouvre le coffre, en
        # vouvoyant —, on le lui rapporte au poste, et elle pose le marché : elle (r03) ou Bouchard (r04), pas les deux.
        {"type": "acte", "texte": "ACTE 3 — ROY TE CONVOQUE", "donneur": "roy"},  # 10
        {"type": "parler", "texte": "LE CARNET DORT AU COFFRE DE L'HÔTEL : VOIS NORBERT", "cible": "norbert"},  # 11
        {"type": "parler", "texte": "RAPPORTE LE CARNET À ROY, AU POSTE", "cible": "roy"},  # 12
    ],

    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "porte:poste", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # r01 — Le jeu de chaque réplique (`jeu=`) — Bouchard : bourru, jamais un mot de trop,
    # une satisfaction sèche — comme f06, il n'a pas besoin de sourire pour qu'on
    # sache que l'affaire est réglée.
    # r05 — Le jeu de chaque réplique (`jeu=`) — Bouchard : un service entre complices, dit en bourru ; la pointe
    # d'inquiétude qu'il cache mal quand il parle de Québec.
    # r02 — Le jeu de chaque réplique (`jeu=`) — Roy : la police honnête, qui n'a pas besoin de crier ; précise, froide,
    # et une ironie sèche qu'elle ne s'autorise qu'une fois par mission. Norbert : le vouvoiement, jamais le nom d'un
    # client.
    "dialogue": {
        "appel": [
            _l("bouchard", "Bouchard. Une nouvelle inspectrice, Roy, fouille dans mes affaires. Un jeune agent véreux lui vend mon carnet.", jeu="[gruffly] Bouchard. Une nouvelle inspectrice, Roy, fouille dans mes affaires. [gravely] Un jeune agent véreux lui vend mon carnet."),
        ],
        "intro": [
            _l("bouchard", "Il sort du poste à la noirceur, mon carnet dans sa mallette. Rattrape-le, discret.", jeu="[firmly] Il sort du poste à la noirceur, mon carnet dans sa mallette. [gravely] Rattrape-le, discret."),
            _l("bouchard", "Pas d'étoile là-dedans. Un gars qui court après un char au poste, ça pose des questions.", jeu="[serious] Pas d'étoile là-dedans. [matter-of-fact] Un gars qui court après un char au poste… ça pose des questions."),
            _l("bouchard", "Si ça tourne mal, je te connais pas. C'est comme ça qu'on devient vieux dans la police.", jeu="[deadpan] Si ça tourne mal, je te connais pas. [knowingly] C'est comme ça qu'on devient vieux dans la police."),
        ],
        "fin": [
            _l("roy", "Toutes les pages : des noms, des montants, des dates. Bouchard écrit bien, pour un croche.", jeu="[satisfied] Toutes les pages : des noms, des montants, des dates. [wryly] Bouchard écrit bien, pour un croche."),
            _l("roy", "Voilà le marché : tu travailles pour moi, ou tu retournes lui manger dans la main. Pas les deux.", jeu="[serious] Voilà le marché : tu travailles pour moi, ou tu retournes lui manger dans la main. [coldly] Pas les deux."),
            _l("roy", "Tiens, pour ton déplacement. Pense à ce que tu veux être dans dix ans.", jeu="[calm] Tiens, pour ton déplacement. [quietly] Pense à ce que tu veux être dans dix ans."),
        ],
        "echec": [
            _e("bouchard", "Vu, hein? Astheure Roy va savoir que je fais nettoyer mes traces. Sacrament.", 0, jeu="[annoyed] Vu, hein? [gravely] Astheure Roy va savoir que je fais nettoyer mes traces. Sacrament."),
            _e("bouchard", "Le camion est parti pour Québec. On va prier, le jeune.", 5, jeu="[nervously] Le camion est parti pour Québec. [gruffly] On va prier, le jeune."),
            _e("roy", "Le carnet a disparu, pis toi avec. Je vais m'en souvenir.", 10, jeu="[coldly] Le carnet a disparu, pis toi avec. [firmly] Je vais m'en souvenir."),
        ],
        "pendant": [
            _p("bouchard", "Il roule vers le pont. Reste collé, mais reste invisible.", 2, jeu="[gravely] Il roule vers le pont. [firmly] Reste collé, mais reste invisible."),
            _p("bouchard", "Roy t'a vu partir. Sème-la, le jeune, une inspectrice ça lâche pas un os.", 3, jeu="[nervously] Roy t'a vu partir. [firmly] Sème-la, le jeune… une inspectrice ça lâche pas un os."),
            _p("bouchard", "Pas au poste, pas chez nous : le coffre de l'Hôtel Bandini. Personne fouille chez un mort.", 4, jeu="[gravely] Pas au poste, pas chez nous… le coffre de l'Hôtel Bandini. [deadpan] Personne fouille chez un mort."),
            # Acte 2 : la fin de r01, en personne ; puis l'appel et l'intro de r05.
            _p("bouchard", "Mon carnet. Vingt ans de petites affaires, dedans. Ça reste entre nous deux.", 5, jeu="[relieved] Mon carnet. [gravely] Vingt ans de petites affaires, dedans. Ça reste entre nous deux.", cloture=True),
            _p("bouchard", "Roy va devoir fouiller ailleurs. T'as fait ça proprement.", 5, jeu="[satisfied] Roy va devoir fouiller ailleurs. [gruffly] T'as fait ça proprement.", cloture=True),
            # ⚠️ Coupée (2 oct. 2026) : « Bouchard. » — il s'est nommé à l'appel du chapitre.
            _p("bouchard", "Les armes du Faubourg partent pour Québec cette nuit. Y en a des tiennes dedans.", 5, jeu="[gruffly] Les armes du Faubourg partent pour Québec cette nuit. [knowingly] Y en a des tiennes dedans."),
            _p("bouchard", "À Québec, ils font des tests. Pis les tests, ça raconte des histoires à des juges.", 5, jeu="[nervously] À Québec, ils font des tests. [gruffly] Pis les tests, ça raconte des histoires à des juges."),
            _p("bouchard", "Le camion attend dans la ruelle du poste. Le chauffeur prend son café à onze heures.", 5, jeu="[matter-of-fact] Le camion attend dans la ruelle du poste. [deadpan] Le chauffeur prend son café à onze heures."),
            _p("bouchard", "Amène-le au garage de ton oncle. Là, un camion peut disparaître.", 5, jeu="[knowingly] Amène-le au garage de ton oncle. [gruffly] Là, un camion peut disparaître."),
            _p("bouchard", "La nuit, le jeune. Personne vole un camion en plein jour.", 6, jeu="[gruffly] La nuit, le jeune. [deadpan] Personne vole un camion en plein jour."),
            _p("bouchard", "Le camion gris, les portes arrière cadenassées. Le cadenas, c'est pas ton problème.", 7, jeu="[matter-of-fact] Le camion gris, les portes arrière cadenassées. [wryly] Le cadenas, c'est pas ton problème."),
            _p("bouchard", "Ça crie sur la radio. Perds-les avant le pont, après c'est la Sûreté.", 8, jeu="[nervously] Ça crie sur la radio. [firmly] Perds-les avant le pont, après c'est la Sûreté."),
            _p("bouchard", "Au garage, astheure. La baie est ouverte, personne regarde.", 9, jeu="[matter-of-fact] Au garage, astheure. [gruffly] La baie est ouverte, personne regarde."),
            # Acte 3 : la fin de r05, en personne ; puis l'appel et l'intro de r02.
            _p("bouchard", "Propre. Les pièces à conviction ont eu un accident de parcours.", 10, jeu="[satisfied] Propre. [deadpan] Les pièces à conviction ont eu un accident de parcours.", cloture=True),
            _p("bouchard", "Tes vieilles affaires sont au garage. Le reste, on l'a jamais vu.", 10, jeu="[knowingly] Tes vieilles affaires sont au garage. [gruffly] Le reste, on l'a jamais vu.", cloture=True),
            _p("roy", "Inspectrice Roy, du poste. Je sais qui a pris mon carnet. Passe me voir, on va jaser.", 10, jeu="[firmly] Inspectrice Roy, du poste. [coldly] Je sais qui a pris mon carnet. Passe me voir, on va jaser."),
            # ⚠️ Coupée : « Assis-toi. » — elle parle au combiné.
            _p("roy", "Je t'arrête pas, je t'aurais déjà arrêté. Je veux mon carnet.", 10, jeu="[calm] Je t'arrête pas, je t'aurais déjà arrêté. [firmly] Je veux mon carnet."),
            _p("roy", "Bouchard l'a fait cacher dans le coffre de l'Hôtel Bandini. Le concierge a la clé.", 10, jeu="[matter-of-fact] Bouchard l'a fait cacher dans le coffre de l'Hôtel Bandini. [knowingly] Le concierge a la clé."),
            _p("roy", "Ramène-le-moi. Après, on parlera de quel côté de la loi tu veux dormir.", 10, jeu="[serious] Ramène-le-moi. [coldly] Après, on parlera de quel côté de la loi tu veux dormir."),
            _p("roy", "Le concierge s'appelle Norbert. Il vouvoie tout le monde, même les voleurs.", 11, jeu="[matter-of-fact] Le concierge s'appelle Norbert. [wryly] Il vouvoie tout le monde, même les voleurs."),
            _p("roy", "Pas de détour. Bouchard a des yeux dans toutes les vitrines du Faubourg.", 12, jeu="[serious] Pas de détour. [firmly] Bouchard a des yeux dans toutes les vitrines du Faubourg."),
        ],
        "accueil": [
            _a("norbert", "Le coffre de Monsieur le sergent? Je crains que Monsieur ne soit pas le seul à le chercher. Le voici.", 11, jeu="[quietly] Le coffre de Monsieur le sergent? [concerned] Je crains que Monsieur ne soit pas le seul à le chercher. [calm] Le voici."),
        ],
    },
}
