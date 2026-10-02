"""Le chapitre du scoop du maire — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague L). La suite du
Clairon : l03 (la source, Norbert), l04 (le scoop du maire) et l05 (le Clairon brûle) — trois à quatre étapes
chacune — deviennent trois ACTES : une source, une preuve imprimée, et la vengeance du maire. Ce qui fait durer : deux
hommes du maire de RENFORT à la rédaction (acte 2).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de l03
  restent ceux du chapitre ; la fin de chaque mission se dit à l'ouverture de l'acte suivant, suivie de l'appel et de
  l'intro de la suivante ; la fin de l05 reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : Louise se nomme à l'appel de l03 ; ses appels de l04 et l05 perdent
  « Louise, au Clairon. » et « C'est Louise! » — la même voix, coupée au silence ;
- la scène d'intro de l03 reste celle du chapitre ; celles de l04 et l05 tombent (leurs répliques se disent au
  marqueur), comme au pilote.
- ⚠️ ÉCART : le chapitre attend ce que ses trois actes attendaient — l01, f10 ET e07 : l03 n'attendait pas e07 (le
  maire suivi à l'hôtel), c'est l04 qui l'attendait. l06 attend l05 (le dernier acte).
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "scoop_du_maire",
    "titre": "Le scoop du maire",
    "donneur": "louise",
    "prerequis": ["l01", "f10", "e07"],
    "remplace": ["l03", "l04", "l05"],
    "recompense": 400,
    "donne": {"message": "LE CLAIRON SORT DEMAIN, COMME TOUS LES JOURS"},

    "objectifs": [
        # --- Acte 1 (l03, « La source »).
        # La source (M16, arc C, 30 sept. 2026 — la « c03 » de la fiche). La source de Louise, c'est Norbert : le concierge
        # de l'Hôtel Bandini voit passer toute la ville à sa réception, et il vend ce qu'il voit — poliment. Ce soir, il a
        # quelque chose sur le maire, et il ne veut pas le dire au téléphone. De nuit, on le prend à l'hôtel, on le mène au
        # kiosque ; deux hommes le suivaient déjà. La fiche disait « un commis du poste » : c'est Norbert, un personnage qui
        # existe, et qui se tient DEDANS (`point:norbert`).
        {"type": "acte", "texte": "ACTE 1 — LA SOURCE", "donneur": "louise"},  # 0
        {"type": "aller", "texte": "À LA NUIT, À L'HÔTEL BANDINI : NORBERT FINIT SON QUART", "lieu": "hotel", "rayon": 6, "nuit": True},  # 1
        {"type": "proteger", "texte": "MÈNE NORBERT AU KIOSQUE, OÙ LOUISE L'ATTEND", "cible": "norbert", "lieu": "kiosque", "rayon": 5},  # 2
        {"type": "tuer", "texte": "DEUX HOMMES LE SUIVAIENT : COUCHE-LES", "groupe": "cravates", "n": 2, "loin": 10},  # 3
        {"type": "retourner", "texte": "LOUISE ÉCOUTE NORBERT : VA LA VOIR", "donne": {"message": "LOUISE A SA SOURCE — ET LE MAIRE, UN SOUCI DE PLUS", "prime": 300}},  # 4
        # --- Acte 2 (l04, « Le scoop du maire »).
        # Le scoop du maire (M16, arc C, 30 sept. 2026 — la « c02 » de la fiche). Norbert a donné les reçus (l03) ; il
        # manquait une preuve qu'on imprime. Elle dort dans le sac du neveu depuis e07 : le dossier volé à la villa. On le
        # porte à la rédaction du Clairon (la façade peinte, `boutique:clairon`), les hommes du maire arrivent trop tard pour
        # le reprendre et trop tôt pour s'en aller, et Louise a sa une : _Le maire dort à l'hôtel_.
        # ⚠️ La fiche voulait le dossier « gardé » par un choix de e11 (le vendre au maire). e11 n'existe pas — le maire ne se
        # tient en ville qu'entre m97 et m98 — : l04 vient après e07, qui laisse le dossier au sac.
        {"type": "acte", "texte": "ACTE 2 — LE SCOOP DU MAIRE", "donneur": "louise"},  # 5
        {"type": "course", "texte": "LE DOSSIER DU MAIRE À LA RÉDACTION DU CLAIRON", "points": ["boutique:clairon"], "rayon": 4},  # 6
        # Ce qui fait durer : deux hommes du maire de plus, quand il n'en reste qu'un debout.
        {"type": "tuer", "texte": "LES HOMMES DU MAIRE VEULENT LE DOSSIER", "groupe": "cravates", "pieton": "gardien", "n": 3, "loin": 10,
         "renforts": {"vagues": 1, "n": 2}},  # 7
        {"type": "retourner", "texte": "LA PREUVE EST IMPRIMÉE : VA VOIR LOUISE", "donne": {"manchette": "maire_hotel", "message": "LE MAIRE DORT À L'HÔTEL — ET TOUTE LA VILLE LE SAIT", "prime": 800}},  # 8
        # --- Acte 3 (l05, « Le Clairon brûle »).
        # Le Clairon brûle (M16, arc C, 30 sept. 2026 — la « c05 » de la fiche). Le lendemain du scoop (l04), le maire
        # répond comme il sait : un bidon d'essence contre la façade de la rédaction. Louise appelle du trottoir d'en face.
        # Un extincteur (elle en a un dans son char, « pour les cigarettes du typographe »), le feu à éteindre avant qu'il
        # prenne l'imprimerie, les trois incendiaires qui regardent de trop près, et Louise au kiosque.
        # ⚠️ La fiche disait « survivre 120 s à l'intérieur » : un objectif ne se joue pas dedans (`majObjectif` dort dans
        # une pièce) et la rédaction n'a pas de porte. Le feu (`eteindre`) prend sur la façade la plus proche de l'enseigne
        # (`Incendies.allumerPourMission`, sans dé) — la ville ne change pas.
        {"type": "acte", "texte": "ACTE 3 — LE CLAIRON BRÛLE", "donneur": "louise"},  # 9
        {"type": "eteindre", "texte": "LE CLAIRON BRÛLE : ÉTEINS LA FAÇADE", "ou": "boutique:clairon", "remet": "extincteur", "chrono_s": 90},  # 10
        {"type": "tuer", "texte": "LES INCENDIAIRES REGARDENT : COUCHE-LES", "groupe": "cravates", "pieton": "gardien", "n": 3, "loin": 10},  # 11
        {"type": "retourner", "texte": "RASSURE LOUISE, AU KIOSQUE"},  # 12
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:hotel", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # l03 — Le jeu de chaque réplique (`jeu=`) — Louise : pour une fois, elle baisse la voix ; une source, ça se protège.
    # Norbert : le vouvoiement, la troisième personne, jamais le nom d'un client — et une inquiétude très polie.
    # l04 — Le jeu de chaque réplique (`jeu=`) — Louise : la journaliste qui tient enfin l'histoire qu'on lui avait tuée ;
    # l'excitation, et une colère ancienne qui passe dessous.
    # l05 — Le jeu de chaque réplique (`jeu=`) — Louise : pour la première fois, elle a peur, et elle le dit vite pour ne
    # pas avoir le temps de pleurer ; la une revient dès que le feu tombe.
    "dialogue": {
        "appel": [
            _l("louise", "Louise. Ma source a quelque chose de gros, pis elle a peur. J'ai besoin de toi ce soir.", jeu="[quietly] Louise. [serious] Ma source a quelque chose de gros, pis elle a peur. J'ai besoin de toi ce soir."),
        ],
        "intro": [
            _l("louise", "Ma source, c'est Norbert, le concierge de l'hôtel. Il voit tout, pis il vend poliment.", jeu="[quietly] Ma source, c'est Norbert, le concierge de l'hôtel. [wryly] Il voit tout, pis il vend poliment."),
            _l("louise", "Il finit son quart à la noirceur. Ramène-le ici, à pied ou en char, mais ramène-le.", jeu="[serious] Il finit son quart à la noirceur. [firmly] Ramène-le ici, à pied ou en char, mais ramène-le."),
            _l("louise", "Quelqu'un l'a vu parler au maire. Ça fait deux jours qu'il dort pas.", jeu="[concerned] Quelqu'un l'a vu parler au maire. [quietly] Ça fait deux jours qu'il dort pas."),
        ],
        "fin": [
            _l("louise", "L'imprimerie a rien. La façade est noire, mais les presses tournent.", jeu="[relieved] L'imprimerie a rien. [calm] La façade est noire, mais les presses tournent."),
            _l("louise", "Demain, on sort. Pis sur la une, y aura une photo de la façade. Qu'il la regarde.", jeu="[confident] Demain, on sort. [coldly] Pis sur la une, y aura une photo de la façade. Qu'il la regarde."),
        ],
        "echec": [
            _e("louise", "Ma source s'est évaporée. Pis moi, je viens de perdre deux jours.", 0, jeu="[disappointed] Ma source s'est évaporée. [bitterly] Pis moi, je viens de perdre deux jours."),
            _e("louise", "Le dossier est reparti chez le maire. Trois ans d'attente pour rien.", 5, jeu="[bitterly] Le dossier est reparti chez le maire. [disappointed] Trois ans d'attente pour rien."),
            _e("louise", "C'est fini. Cent douze ans de Clairon, en fumée.", 9, jeu="[somber] C'est fini. [quietly] Cent douze ans de Clairon, en fumée."),
        ],
        "pendant": [
            _p("louise", "La lumière de la réception s'éteint à minuit. C'est ton signal.", 1, jeu="[quietly] La lumière de la réception s'éteint à minuit. [serious] C'est ton signal."),
            _p("norbert", "Monsieur est ponctuel. Si Monsieur veut bien marcher du côté de la rue, je préfère le mur.", 2, jeu="[calm] Monsieur est ponctuel. [quietly] Si Monsieur veut bien marcher du côté de la rue, je préfère le mur."),
            _p("norbert", "Je crains que ces messieurs ne soient pas des clients. Je les ai vus avec le chauffeur du maire.", 3, jeu="[concerned] Je crains que ces messieurs ne soient pas des clients. [quietly] Je les ai vus avec le chauffeur du maire."),
            _p("louise", "Il est là, il tremble, pis il parle. Viens entendre ça.", 4, jeu="[excited] Il est là, il tremble, pis il parle. [quietly] Viens entendre ça."),
            # Acte 2 : la fin de l03, en personne ; puis l'appel et l'intro de l04.
            _p("louise", "Le maire a une chambre à l'année à l'hôtel. Payée par la ville. Norbert a les reçus.", 5, jeu="[excited] Le maire a une chambre à l'année à l'hôtel. [serious] Payée par la ville. Norbert a les reçus."),
            _p("louise", "Il me manque juste une preuve qu'on peut imprimer. Je te rappelle, mon beau.", 5, jeu="[knowingly] Il me manque juste une preuve qu'on peut imprimer. [teasing] Je te rappelle, mon beau."),
            # ⚠️ Coupée : « Louise, au Clairon. »
            _p("louise", "Norbert m'a donné les reçus. Il me manque le dossier que t'as dans ton sac.", 5, jeu="[excited] Norbert m'a donné les reçus. [knowingly] Il me manque le dossier que t'as dans ton sac."),
            _p("louise", "Le maire m'a déjà tué une histoire, y a trois ans. Celle-là, il la tuera pas.", 5, jeu="[bitterly] Le maire m'a déjà tué une histoire, y a trois ans. [firmly] Celle-là, il la tuera pas."),
            _p("louise", "Porte le dossier à la rédaction. Le typographe t'attend, les presses sont chaudes.", 5, jeu="[excited] Porte le dossier à la rédaction. [confident] Le typographe t'attend, les presses sont chaudes."),
            _p("louise", "Le maire a des amis partout. S'ils arrivent, ils arrivent trop tard. Arrange-toi pour ça.", 5, jeu="[serious] Le maire a des amis partout. [firmly] S'ils arrivent, ils arrivent trop tard. Arrange-toi pour ça."),
            _p("louise", "La rédaction, c'est la vieille façade avec l'enseigne du Clairon. La porte d'en arrière est ouverte.", 6, jeu="[matter-of-fact] La rédaction, c'est la vieille façade avec l'enseigne du Clairon. [quietly] La porte d'en arrière est ouverte."),
            _p("louise", "Les presses roulent! Pis les hommes du maire aussi. Tiens-les loin.", 7, jeu="[excited] Les presses roulent! [concerned] Pis les hommes du maire aussi. Tiens-les loin."),
            _p("louise", "Six mille copies. Viens chercher la tienne au kiosque, mon beau.", 8, jeu="[satisfied] Six mille copies. [teasing] Viens chercher la tienne au kiosque, mon beau."),
            # Acte 3 : la fin de l04, en personne ; puis l'appel et l'intro de l05.
            _p("louise", "« Le maire dort à l'hôtel. » Aux frais de la ville, depuis trois ans. Tout est là.", 9, jeu="[excited] « Le maire dort à l'hôtel. » Aux frais de la ville, depuis trois ans. [satisfied] Tout est là."),
            _p("louise", "Ça, c'est ta part. Pis garde ton sac fermé : il va vouloir savoir d'où ça vient.", 9, jeu="[warmly] Ça, c'est ta part. [serious] Pis garde ton sac fermé : il va vouloir savoir d'où ça vient."),
            # ⚠️ Coupée : « C'est Louise! »
            _p("louise", "Le Clairon brûle! Quelqu'un a vidé un bidon sur la façade!", 9, jeu="[worried] Le Clairon brûle! Quelqu'un a vidé un bidon sur la façade!"),
            _p("louise", "Tiens, l'extincteur de mon char. Il servait pour les cigarettes du typographe.", 9, jeu="[nervously] Tiens, l'extincteur de mon char. [wryly] Il servait pour les cigarettes du typographe."),
            _p("louise", "Si ça prend l'imprimerie, y aura plus de Clairon. Cent douze ans, pis c'est fini.", 9, jeu="[worried] Si ça prend l'imprimerie, y aura plus de Clairon. [somber] Cent douze ans, pis c'est fini."),
            _p("louise", "Pis ceux qui ont fait ça sont encore dans la rue, à regarder. Ils veulent voir.", 9, jeu="[angry] Pis ceux qui ont fait ça sont encore dans la rue, à regarder. [coldly] Ils veulent voir."),
            _p("louise", "Vise le bas des flammes! Le bas!", 10, jeu="[shouting] Vise le bas des flammes! [nervously] Le bas!"),
            _p("louise", "C'est éteint. Les trois de l'autre côté, ce sont eux. Ils rient.", 11, jeu="[relieved] C'est éteint. [angry] Les trois de l'autre côté, ce sont eux. Ils rient."),
            _p("louise", "Viens au kiosque. J'ai besoin d'un café, pis d'un titre.", 12, jeu="[softly] Viens au kiosque. [wryly] J'ai besoin d'un café, pis d'un titre."),
        ],
    },
}
