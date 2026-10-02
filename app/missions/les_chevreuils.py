"""Le chapitre des Chevreuils — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague E). La libération des Érables : e04 (Jo et sa course), e06 (Diane, le maire filé à l'hôtel), e07 (la clé de la villa, le
dossier du maire) et e10 (les Chevreuils vidés, et leur chef : c'était Jo) — deux à six étapes — quatre ACTES (9 à
10 minutes), de la course de Jo à la paix de Diane (`libere: erables`, à la fin du chapitre comme de e10).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : Diane se nomme à l'acte 2 ; ses appels de e07 et e10 perdent
  « Diane Larivière. » — la même voix, coupée au silence ;
- Jo (`parti_apres: e04`) reste pour tout le chapitre : il est le donneur de l'acte 1 — il part à la fin ;
- l'échec `etoile` de e07 voyage avec le chapitre : il ne se déclenche que par `sans_etoile`, à la villa ;
- rater un acte ne fait retomber que ce que CET acte a fait prendre (`Infiltration.rendre`) : le dossier du maire reste
  au sac si l'on tombe à l'acte 4 ;
- la scène d'intro de e04 reste celle du chapitre.
- l04 et e14 attendent e07 (l'acte 3), _Diane et Jo_ attend e10 (le dernier) : un prérequis peut viser un acte.
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "les_chevreuils",
    "titre": "Les Chevreuils",
    "donneur": "jo",
    "prerequis": ["e01"],
    "remplace": ["e04", "e06", "e07", "e10"],
    "recompense": 600,
    "donne": {"libere": "erables", "manchette": "erables_liberes", "message": "LES ÉRABLES SONT LIBRES"},
    "echec": ["mort", "arrete", "etoile"],

    "objectifs": [
        # --- Acte 1 (e04, « La course des Chevreuils »).
        {"type": "acte", "texte": "ACTE 1 — LA COURSE DES CHEVREUILS", "donneur": "jo"},  # 0
        {"type": "ramasser", "texte": "LEUR PILOTE FILE EN SPORT — RATTRAPE-LE", "vehicule": "sport", "cible": "fuyard"},  # 1
        {"type": "retourner", "texte": "RAPPORTE SES CLÉS À JO", "donne": {"calme": "chevreuils", "message": "LES CHEVREUILS TE RESPECTENT", "prime": 300}},  # 2
        # --- Acte 2 (e06, « Le maire ne dort pas chez lui »).
        {"type": "acte", "texte": "ACTE 2 — LE MAIRE NE DORT PAS CHEZ LUI", "donneur": "diane"},  # 3
        {"type": "suivre", "texte": "FILE LA BERLINE DU MAIRE, SANS QU'IL TE VOIE", "vehicule": "luxe", "loin": 12, "proche": 3, "lieu": "hotel"},  # 4
        {"type": "retourner", "texte": "RACONTE TOUT À DIANE, AU DÉPANNEUR", "donne": {"message": "LE MAIRE DORT À L'HÔTEL, ET DIANE LE SAIT", "prime": 300}},  # 5
        # --- Acte 3 (e07, « La clé de la villa »).
        {"type": "acte", "texte": "ACTE 3 — LA CLÉ DE LA VILLA", "donneur": "diane"},  # 6
        {"type": "pickpocket", "texte": "LE CHAUFFEUR DU MAIRE — VIDE SES POCHES, PAR-DERRIÈRE", "cible": "passant", "objet": "cle_villa"},  # 7
        {"type": "aller", "texte": "VA À LA VILLA DU MAIRE, DE NUIT", "lieu": "villa_chemin", "rayon": 6, "nuit": True},  # 8
        {"type": "aller", "texte": "ENTRE PAR LA PORTE DE SERVICE, AVEC SA CLÉ", "lieu": "villa_service", "rayon": 2, "sans_etoile": True},  # 9
        {"type": "obtenir", "texte": "LE DOSSIER DU MAIRE, DANS SON BUREAU D'EN HAUT", "objet": "dossier_maire", "nom": "LE DOSSIER DU MAIRE", "dessin": "dossier", "ou": "villa_bureau", "sans_etoile": True},  # 10
        {"type": "aller", "texte": "RESSORS PAR LE CHEMIN, SANS TE FAIRE VOIR", "lieu": "villa_chemin", "rayon": 3, "sans_etoile": True},  # 11
        {"type": "retourner", "texte": "APPORTE LE DOSSIER À DIANE", "donne": {"message": "LE DOSSIER DU MAIRE, DANS TON SAC", "prime": 400}},  # 12
        # --- Acte 4 (e10, « Diane veut la paix »).
        {"type": "acte", "texte": "ACTE 4 — DIANE VEUT LA PAIX", "donneur": "diane"},  # 13
        {"type": "tuer", "texte": "VIDE LES DEUX COINS DES CHEVREUILS", "groupe": "chevreuils", "n": 6, "coins": 2, "ou": "zone:chevreuils"},  # 14
        {"type": "tuer", "texte": "LEUR CHEF ARRIVE — COUCHE-LE", "groupe": "chevreuils", "n": 1, "chef": True},  # 15
        {"type": "semer", "texte": "LES VOISINS ONT APPELÉ LA POLICE — SÈME-LA", "etoiles": 2},  # 16
        {"type": "retourner", "texte": "REVIENS VOIR DIANE, AU DÉPANNEUR"},  # 17
    ],

    # e04 — Le jeu de chaque réplique (`jeu=`) — Jo : le fils de bonne famille qui joue au dur ; il parle vite, fort, et
    # rit de ses propres phrases. Il appelle tout le monde « le vieux ». À la fin, il perd, et il le prend en riant —
    # trop fort, parce que ses gars regardent.
    # e06 — Le jeu de chaque réplique (`jeu=`) — Diane : la politicienne qui sourit en disant non. Elle vouvoie, elle
    # pèse chaque mot, et ne dit jamais ce qu'elle veut — elle dit ce que « les citoyens » veulent. Un seul
    # `[satisfied]`, à la fin : c'est là qu'on voit qu'elle joue une partie.
    # e07 — Le jeu de chaque réplique (`jeu=`) — Diane : elle monte d'un cran. Elle ne demande plus un service, elle
    # donne une adresse et une heure. La politesse reste, la patience s'en va.
    # e10 — Le jeu de chaque réplique (`jeu=`) — Diane : la paix, et le pouvoir — jusqu'à ce que le chef couché ait un
    # nom. Elle a tout prévu sauf ça. La politicienne reste droite dans les mots ; la voix, elle, casse une fois,
    # à la fin, et se reprend tout de suite.
    "dialogue": {
        "appel": [
            _l("jo", "C'est Jo, des Chevreuils. Paraît que t'as couché mes petits frères. Viens au dépanneur, le vieux.", jeu="[mischievously] C'est Jo, des Chevreuils. [teasing] Paraît que t'as couché mes petits frères… Viens au dépanneur, le vieux."),
        ],
        "intro": [
            _l("jo", "Tu frappes fort. Mais icitte, on se respecte au volant, pas aux poings.", jeu="[smugly] Tu frappes fort. [confident] Mais icitte, on se respecte au volant… pas aux poings."),
            _l("jo", "Mon meilleur pilote part devant, en sport. Tu le rattrapes, ses clés sont à toi.", jeu="[excited] Mon meilleur pilote part devant, en sport. [playfully] Tu le rattrapes… ses clés sont à toi."),
            _l("jo", "Tu le rattrapes pas, tu retournes chez vous en autobus. Go!", jeu="[teasing] Tu le rattrapes pas, tu retournes chez vous en autobus. [shouting] Go!"),
        ],
        "fin": [
            _l("diane", "C'était Jo. Je le savais depuis le dossier. Je voulais me tromper.", jeu="[somber] C'était Jo. [quietly] Je le savais depuis le dossier. [sighs] Je voulais me tromper."),
            _l("diane", "Il va s'en remettre, et il va m'en vouloir. Les Érables, eux, vont dormir.", jeu="[softly] Il va s'en remettre… et il va m'en vouloir. [firmly] Les Érables, eux, vont dormir."),
            _l("diane", "Jeudi, je vote la paix. Personne ne saura ce qu'elle m'a coûté.", jeu="[confident] Jeudi, je vote la paix. [bitterly] Personne ne saura ce qu'elle m'a coûté."),
        ],
        "echec": [
            _e("jo", "T'as même pas fini la course! L'autobus passe à six heures, le vieux.", 0, jeu="[laughs] [teasing] T'as même pas fini la course! L'autobus passe à six heures, le vieux."),
            _e("diane", "Il vous a vu. Le maire va dormir chez lui un bon moment, maintenant.", 3, jeu="[disappointed] Il vous a vu. [coldly] Le maire va dormir chez lui un bon moment, maintenant."),
            _e("diane", "Un garde vous a vu. Je ne vous connais pas, et je ne vous ai jamais connu.", 6, jeu="[coldly] Un garde vous a vu. [firmly] Je ne vous connais pas… et je ne vous ai jamais connu."),
            _e("diane", "Les Chevreuils tiennent encore. Jeudi, je voterai contre moi-même.", 13, jeu="[disappointed] Les Chevreuils tiennent encore. [bitterly] Jeudi, je voterai contre moi-même."),
        ],
        "pendant": [
            _p("jo", "Y est parti! Colle-lui au pare-chocs, le vieux!", 1, jeu="[excited] Y est parti! [shouting] Colle-lui au pare-chocs, le vieux!"),
            _p("jo", "OK, OK, t'es capable. Apporte-moi ses clés, qu'on en finisse.", 2, jeu="[impressed] OK, OK… t'es capable. [casually] Apporte-moi ses clés, qu'on en finisse."),
            # Acte 2 : la fin de e04, en personne ; puis l'appel et l'intro de e06.
            _p("jo", "Ses clés. Ha! Il va entendre parler de ça jusqu'à Noël.", 3, jeu="[laughs] [amused] Ses clés. Ha! Il va entendre parler de ça jusqu'à Noël."),
            _p("jo", "Les Chevreuils te toucheront pas, le vieux. Pis dis rien à ma mère, OK?", 3, jeu="[confident] Les Chevreuils te toucheront pas, le vieux. [nervously] Pis dis rien à ma mère, OK?"),
            _p("diane", "Diane Larivière, conseillère municipale. J'ai un service à vous demander, discrètement.", 3, jeu="[confident] Diane Larivière, conseillère municipale. [quietly] J'ai un service à vous demander… discrètement."),
            _p("diane", "Le maire Tanguay dit aux citoyens qu'il dort à la villa. Sa voiture dit autre chose.", 3, jeu="[knowingly] Le maire Tanguay dit aux citoyens qu'il dort à la villa. [wryly] Sa voiture dit autre chose."),
            _p("diane", "Ce soir, sa berline va sortir. Suivez-la jusqu'où elle s'arrête.", 3, jeu="[calm] Ce soir, sa berline va sortir. [firmly] Suivez-la jusqu'où elle s'arrête."),
            _p("diane", "Pas trop près. Un maire qui se sait suivi dort chez lui pendant un mois.", 3, jeu="[serious] Pas trop près. [wryly] Un maire qui se sait suivi… dort chez lui pendant un mois."),
            _p("diane", "Elle sort. Laissez-lui de l'avance, il regarde toujours dans son rétroviseur.", 4, jeu="[quietly] Elle sort. [calm] Laissez-lui de l'avance… il regarde toujours dans son rétroviseur."),
            _p("diane", "L'Hôtel Bandini. Évidemment. Revenez me voir, je veux chaque détail.", 5, jeu="[amused] L'Hôtel Bandini. Évidemment. [firmly] Revenez me voir… je veux chaque détail."),
            # Acte 3 : la fin de e06, en personne ; puis l'appel et l'intro de e07.
            _p("diane", "Trois nuits par semaine à l'hôtel, aux frais de la ville. Les citoyens vont adorer.", 6, jeu="[wryly] Trois nuits par semaine à l'hôtel, aux frais de la ville. [satisfied] Les citoyens vont adorer."),
            _p("diane", "Gardez ça pour vous. Une information se vend mieux quand personne d'autre ne l'a.", 6, jeu="[knowingly] Gardez ça pour vous. [calm] Une information se vend mieux… quand personne d'autre ne l'a."),
            # ⚠️ Coupée (2 oct. 2026) : « Diane Larivière. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("diane", "Le maire a un dossier sur chaque conseiller. Je veux le mien, et les autres.", 6, jeu="[serious] Le maire a un dossier sur chaque conseiller. Je veux le mien… et les autres."),
            _p("diane", "Son chauffeur achète ses cigarettes ici, à six heures. La clé de la porte de service est sur lui.", 6, jeu="[matter-of-fact] Son chauffeur achète ses cigarettes ici, à six heures. [quietly] La clé de la porte de service est sur lui."),
            _p("diane", "Le dossier est dans le bureau d'en haut. Il y a des gardes, et ils ont des lampes.", 6, jeu="[calm] Le dossier est dans le bureau d'en haut. [serious] Il y a des gardes… et ils ont des lampes."),
            _p("diane", "Une seule étoile et le maire saura qui l'a envoyé. Moi, je n'existe pas.", 6, jeu="[menacingly] Une seule étoile et le maire saura qui l'a envoyé. [coldly] Moi, je n'existe pas."),
            _p("diane", "Le voilà, avec sa casquette. Passez derrière lui, les mains légères.", 7, jeu="[quietly] Le voilà, avec sa casquette. [calm] Passez derrière lui… les mains légères."),
            _p("diane", "Vous avez la clé. Attendez la nuit, les gardes changent à la noirceur.", 8, jeu="[satisfied] Vous avez la clé. [quietly] Attendez la nuit… les gardes changent à la noirceur."),
            _p("diane", "En haut, au fond. Ne touchez à rien d'autre, il compte ses stylos.", 10, jeu="[quietly] En haut, au fond. [wryly] Ne touchez à rien d'autre… il compte ses stylos."),
            _p("diane", "Sortez comme vous êtes entré. Doucement.", 11, jeu="[calm] Sortez comme vous êtes entré. [softly] Doucement."),
            # Acte 4 : la fin de e07, en personne ; puis l'appel et l'intro de e10.
            _p("diane", "Mon nom est dedans. Le vôtre aussi, d'ailleurs. Gardez-le, ce dossier : il vaut cher.", 13, jeu="[surprised] Mon nom est dedans. [amused] Le vôtre aussi, d'ailleurs. [knowingly] Gardez-le, ce dossier : il vaut cher."),
            _p("diane", "Il y a une page sur les Chevreuils. Sur mon fils. Nous en reparlerons.", 13, jeu="[quietly] Il y a une page sur les Chevreuils. [somber] Sur mon fils… Nous en reparlerons."),
            # ⚠️ Coupée (2 oct. 2026) : « Diane Larivière. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("diane", "Le conseil vote la paix dans les Érables jeudi. Aidez-moi à la rendre vraie.", 13, jeu="[serious] Le conseil vote la paix dans les Érables jeudi. [firmly] Aidez-moi à la rendre vraie."),
            _p("diane", "Les Chevreuils tiennent deux coins derrière le boulevard. Je les veux vides.", 13, jeu="[matter-of-fact] Les Chevreuils tiennent deux coins derrière le boulevard. [coldly] Je les veux vides."),
            _p("diane", "Ensuite, leur chef viendra. Il vient toujours quand on touche à ses gars.", 13, jeu="[calm] Ensuite, leur chef viendra. [knowingly] Il vient toujours… quand on touche à ses gars."),
            _p("diane", "Ne me dites pas son nom. Je ne veux pas le savoir avant jeudi.", 13, jeu="[quietly] Ne me dites pas son nom. [serious] Je ne veux pas le savoir… avant jeudi."),
            _p("diane", "Deux coins, six garçons. Des enfants de bonne famille qui jouent aux bandits.", 14, jeu="[coldly] Deux coins, six garçons. [bitterly] Des enfants de bonne famille… qui jouent aux bandits."),
            _p("diane", "Le voilà. Faites vite, je vous en prie.", 15, jeu="[nervously] Le voilà. [quietly] Faites vite… je vous en prie."),
            _p("diane", "Les voisins ont appelé la police. Évidemment, ce soir, ils sont réveillés.", 16, jeu="[wryly] Les voisins ont appelé la police. [annoyed] Évidemment, ce soir, ils sont réveillés."),
            _p("diane", "Revenez au dépanneur. Seul.", 17, jeu="[somber] Revenez au dépanneur. [quietly] Seul."),
        ],
    },
}
