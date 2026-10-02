"""Le chapitre de la dette du docteur — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague H). Le Dr Lachance
joue aux cartes chez Sal : h03 (la moitié payée, escortée au terminus), h04 (le cœur de l'autobus de nuit), h05
(Ginette : le patient qui file avec la morphine) et h06 (le reste, en fausses ordonnances) — trois à quatre étapes
chacune, 99 s pour h03 au chronomètre de Martin — deviennent quatre ACTES : la dette d'un homme droit, entre deux
urgences. Ce qui fait durer : deux Cravates de RENFORT aux deux bagarres (l'enveloppe, puis le patient).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de h03
  restent ceux du chapitre ; la fin de chaque mission se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de h06 reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : le docteur se nomme à l'appel de h03 ; ses appels de h04 et h06
  perdent « Ici Lachance » et « Lachance, à l'appareil » — la même voix, coupée au silence. Ginette se nomme à
  l'acte 3 (sa première réplique du chapitre) ;
- la scène d'intro de h03 reste celle du chapitre ; celles de h04, h05 et h06 tombent (leurs répliques se disent au
  marqueur), comme au pilote.
- Il attend h02 (le dernier acte de _L'ambulance de nuit_) et d01 (le premier acte de _La dette de Rocco_). h07
  attend h06 (le dernier acte) et h08 attend h04 (l'acte 2) : un prérequis peut viser un acte.
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "dette_du_docteur",
    "titre": "La dette du docteur",
    "donneur": "lachance",
    "prerequis": ["h02", "d01"],
    "remplace": ["h03", "h04", "h05", "h06"],
    "recompense": 350,
    "donne": {"message": "LE DOCTEUR NE DOIT PLUS RIEN À SAL"},

    "objectifs": [
        # --- Acte 1 (h03, « Le docteur a une dette »).
        # Le docteur a une dette (M16, arc H, 30 sept. 2026). Le Dr Lachance ne dort jamais : il joue aux cartes, la nuit,
        # à la table que Sal Ferraro tient au terminus — et il perd. Deux mille piasses. Il va payer la moitié ce soir, et il
        # ne veut pas marcher seul avec l'argent dans la poche de son sarrau. On l'escorte au terminus ; deux Cravates sans
        # job depuis m5 ont entendu parler de l'enveloppe ; il paie Sal, et il nous attend à la porte : son quart commence.
        {"type": "acte", "texte": "ACTE 1 — LE DOCTEUR A UNE DETTE", "donneur": "lachance"},  # 0
        {"type": "proteger", "texte": "MÈNE LE DOCTEUR AU TERMINUS : IL A L'ARGENT", "cible": "lachance", "lieu": "terminus", "rayon": 5},  # 1
        # Ce qui fait durer : deux Cravates de plus, quand il n'en reste qu'un debout.
        {"type": "tuer", "texte": "DEUX CRAVATES VEULENT L'ENVELOPPE : COUCHE-LES", "groupe": "cravates", "n": 2, "loin": 10,
         "renforts": {"vagues": 1, "n": 2}},  # 2
        {"type": "parler", "texte": "LE DOCTEUR PAIE : VA VOIR SAL, DEDANS", "cible": "sal"},  # 3
        {"type": "retourner", "texte": "LE DOCTEUR T'ATTEND DEVANT LE TERMINUS", "donne": {"message": "LA MOITIÉ DE LA DETTE DU DOCTEUR EST PAYÉE", "prime": 250}},  # 4
        # --- Acte 2 (h04, « Le cœur »).
        # Le cœur (M16, arc H, 30 sept. 2026). Un cœur à greffer arrive de Québec par l'autobus de nuit, dans une glacière de
        # pêcheur, et l'ambulance de l'hôpital est la seule assez vite. On la prend, on va chercher la glacière au quai des
        # autobus (à pied : elle est posée par terre, `obtenir`), et on la ramène à l'urgence en quatre-vingt-dix secondes,
        # DANS l'ambulance (`livrer` + `chrono_s`).
        {"type": "acte", "texte": "ACTE 2 — LE CŒUR", "donneur": "lachance"},  # 5
        {"type": "monter", "texte": "PRENDS L'AMBULANCE DEVANT L'HÔPITAL", "vehicule": "ambulance", "ou": "porte:hopital"},  # 6
        {"type": "obtenir", "texte": "LA GLACIÈRE ARRIVE AU TERMINUS : PRENDS-LA À PIED", "objet": "glaciere_du_coeur", "ou": "terminus", "dessin": "sac", "nom": "LA GLACIÈRE DU CŒUR"},  # 7
        {"type": "livrer", "texte": "LE CŒUR À L'URGENCE EN AMBULANCE, VITE", "lieu": "hopital", "rayon": 5, "chrono_s": 90, "donne": {"message": "LE CŒUR EST ARRIVÉ À TEMPS", "prime": 400}},  # 8
        # --- Acte 3 (h05, « Le patient qui s'est sauvé »).
        # Le patient qui s'est sauvé (M16, arc H, 30 sept. 2026). Le chef des Cravates de m5, recousu à l'hôpital, se lève
        # à trois heures du matin, vole l'ambulance — avec la trousse de morphine dedans — et file. Ginette veut sa trousse.
        # On le rattrape (le fuyard en ambulance, le patron de m97/d02) ; il sort avec la trousse, on la reprend ; ses deux
        # gars arrivent le chercher ; on rapporte la trousse à Ginette, à son comptoir (`retourner` : elle est DEHORS).
        {"type": "acte", "texte": "ACTE 3 — LE PATIENT QUI S'EST SAUVÉ", "donneur": "ginette"},  # 9
        {"type": "ramasser", "texte": "LE PATIENT FILE EN AMBULANCE : RATTRAPE-LE", "cible": "fuyard", "vehicule": "ambulance"},  # 10
        # Ce qui fait durer : deux de plus.
        {"type": "tuer", "texte": "SES GARS VIENNENT LE CHERCHER : COUCHE-LES", "groupe": "cravates", "n": 2, "loin": 10,
         "renforts": {"vagues": 1, "n": 2}},  # 11
        {"type": "retourner", "texte": "RAPPORTE LA TROUSSE À GINETTE", "donne": {"message": "LA TROUSSE EST REVENUE À LA PHARMACIE", "prime": 200}},  # 12
        # --- Acte 4 (h06, « Les ordonnances »).
        # Les ordonnances (M16, arc H, 30 sept. 2026). Le reste de la dette du docteur (h03), Sal le veut en pilules : trois
        # ordonnances de calmants, signées Lachance, pour des patients qui n'existent pas. On les fait remplir à trois
        # comptoirs de trois quartiers — la pharmacie Tang au Petit-Canton, la Mission du port, le dentiste — sans une
        # étoile (un gars recherché qui remplit une ordonnance, ça se remarque), on porte les sacs à Sal, et on revient dire
        # au docteur que c'est fini. Il n'est pas fier ; il le dit.
        {"type": "acte", "texte": "ACTE 4 — LES ORDONNANCES", "donneur": "lachance"},  # 13
        {"type": "course", "texte": "TROIS ORDONNANCES, TROIS COMPTOIRS, ZÉRO ÉTOILE", "points": ["boutique:pharmacie", "boutique:mission", "boutique:dentiste"], "rayon": 3, "sans_etoile": True},  # 14
        {"type": "parler", "texte": "LES TROIS SACS DE PILULES À SAL, AU TERMINUS", "cible": "sal"},  # 15
        {"type": "parler", "texte": "DIS AU DOCTEUR QUE C'EST RÉGLÉ", "cible": "lachance"},  # 16
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "coupe", "vers": "porte:terminus", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # h03 — Le jeu de chaque réplique (`jeu=`) — Lachance : pour la première fois, le médecin est le patient. Il garde son
    # vocabulaire de salle d'urgence pour ne pas avoir à dire « j'ai honte » ; la voix reste calme, la phrase
    # s'arrête plus tôt. Sal, à la poignée de main : doux, content, et jamais un chiffre rond.
    # h04 — Le jeu de chaque réplique (`jeu=`) — Lachance : l'urgence qu'il connaît le mieux, celle qui a un chrono. Il
    # compte en minutes, il parle comme on lit un protocole ; à la fin, une fatigue heureuse qu'il ne cache pas.
    # h05 — Le jeu de chaque réplique (`jeu=`) — Ginette : une colère froide d'infirmière-chef (on a volé les malades), qui
    # passe par l'ironie. Elle ne dit pas le nom du patient : le secret professionnel, même en colère.
    # h06 — Le jeu de chaque réplique (`jeu=`) — Lachance : la honte d'un homme droit, dite au vocabulaire de l'hôpital
    # pour ne pas avoir à la nommer ; la voix ne tremble pas, elle ralentit. Sal : content, et presque tendre avec
    # le docteur — un bon client, c'est de la famille.
    "dialogue": {
        "appel": [
            _l("lachance", "Lachance, de l'hôpital. C'est personnel, cette fois. Passe à mon bureau, discrètement.", jeu="[serious] Lachance, de l'hôpital. [firmly] C'est personnel, cette fois. Passe à mon bureau, discrètement."),
        ],
        "intro": [
            _l("lachance", "Je joue aux cartes la nuit, chez Sal. Mauvais diagnostic : deux mille piasses de retard.", jeu="[quietly] Je joue aux cartes la nuit, chez Sal. [deadpan] Mauvais diagnostic : deux mille piasses de retard."),
            _l("lachance", "J'apporte la moitié ce soir. Mille piasses dans un sarrau, ça se voit de loin.", jeu="[matter-of-fact] J'apporte la moitié ce soir. [concerned] Mille piasses dans un sarrau… ça se voit de loin."),
            _l("lachance", "Marche avec moi jusqu'au terminus. Pis pas un mot à Ginette.", jeu="[firmly] Marche avec moi jusqu'au terminus. [quietly] Pis pas un mot à Ginette."),
        ],
        "fin": [
            _l("lachance", "Fermé. Vingt ans de médecine, pis c'est un barbier qui me fait signer n'importe quoi.", jeu="[bitterly] Fermé. [somber] Vingt ans de médecine, pis c'est un barbier qui me fait signer n'importe quoi."),
            _l("lachance", "Prends ça. Pis si tu me vois à une table de cartes, sors-moi par le collet.", jeu="[matter-of-fact] Prends ça. [firmly] Pis si tu me vois à une table de cartes, sors-moi par le collet."),
        ],
        "echec": [
            _e("lachance", "L'enveloppe est partie, et moi avec presque. Je dirai à Sal qu'il attende.", 0, jeu="[somber] L'enveloppe est partie, et moi avec presque. [quietly] Je dirai à Sal qu'il attende."),
            _e("lachance", "Trop tard. On le dira à la famille avec des mots doux, mais c'est trop tard.", 5, jeu="[somber] Trop tard. [quietly] On le dira à la famille avec des mots doux, mais c'est trop tard."),
            _e("ginette", "Partie, la trousse. Je vais remplir le formulaire de perte, en trois copies.", 9, jeu="[disappointed] Partie, la trousse. [annoyed] Je vais remplir le formulaire de perte, en trois copies."),
            _e("lachance", "Une étoile, pis tout le monde regarde ma signature. On arrête ça là.", 13, jeu="[concerned] Une étoile, pis tout le monde regarde ma signature. [firmly] On arrête ça là."),
        ],
        "pendant": [
            _p("lachance", "Pas trop vite. Un médecin qui court, ça inquiète le monde.", 1, jeu="[calm] Pas trop vite. [wryly] Un médecin qui court, ça inquiète le monde."),
            _p("lachance", "Ces deux-là, je les ai recousus le mois passé. Ils ont la mémoire courte.", 2, jeu="[concerned] Ces deux-là, je les ai recousus le mois passé. [bitterly] Ils ont la mémoire courte."),
            _p("lachance", "Je t'attends dehors. Je n'aime pas l'odeur de la lotion à barbe de Sal.", 3, jeu="[quietly] Je t'attends dehors. [wryly] Je n'aime pas l'odeur de la lotion à barbe de Sal."),
            _p("lachance", "Mon quart commence dans dix minutes. Le poker, lui, attendra.", 4, jeu="[matter-of-fact] Mon quart commence dans dix minutes. [somber] Le poker, lui, attendra."),
            # Acte 2 : la fin de h03, en personne ; puis l'appel et l'intro de h04.
            _p("lachance", "La moitié de payée. Le reste, je trouverai bien comment.", 5, jeu="[relieved] La moitié de payée. [quietly] Le reste… je trouverai bien comment.", cloture=True),
            _p("lachance", "Tiens. Pour ton temps, pis pour ton silence.", 5, jeu="[matter-of-fact] Tiens. [firmly] Pour ton temps, pis pour ton silence.", cloture=True),
            _p("lachance", "Si Ginette demande, j'étais en consultation. Ce n'est même pas un mensonge.", 5, jeu="[deadpan] Si Ginette demande, j'étais en consultation. [wryly] Ce n'est même pas un mensonge.", cloture=True),
            # ⚠️ Coupée : « Ici Lachance. »
            _p("lachance", "Un cœur arrive par l'autobus de nuit, pis mes ambulanciers sont tous sortis.", 5, jeu="[concerned] Un cœur arrive par l'autobus de nuit, pis mes ambulanciers sont tous sortis."),
            _p("lachance", "Un cœur, dans une glacière de pêcheur. Il vient de Québec, il a quatre heures de vie.", 5, jeu="[gravely] Un cœur, dans une glacière de pêcheur. [matter-of-fact] Il vient de Québec… il a quatre heures de vie."),
            _p("lachance", "Le chauffeur va la poser sur le trottoir du terminus. Tu la prends à la main, doucement.", 5, jeu="[firmly] Le chauffeur va la poser sur le trottoir du terminus. [calm] Tu la prends à la main… doucement."),
            _p("lachance", "Prends l'ambulance. Au retour, t'as une minute et demie, pas une seconde de plus.", 5, jeu="[matter-of-fact] Prends l'ambulance. [serious] Au retour, t'as une minute et demie, pas une seconde de plus."),
            _p("lachance", "Elle a le plein pis des freins neufs. Ménage-la quand même, c'est la seule.", 6, jeu="[matter-of-fact] Elle a le plein pis des freins neufs. [firmly] Ménage-la quand même, c'est la seule."),
            _p("lachance", "Une glacière bleue, avec du tape. Le chauffeur n'a pas voulu la garder sur ses genoux.", 7, jeu="[matter-of-fact] Une glacière bleue, avec du tape. [wryly] Le chauffeur n'a pas voulu la garder sur ses genoux."),
            _p("lachance", "La salle est prête, le patient est endormi. Il manque juste toi.", 8, jeu="[serious] La salle est prête, le patient est endormi. [firmly] Il manque juste toi."),
            # Acte 3 : la fin de h04, en personne ; puis l'appel et l'intro de h05.
            _p("lachance", "Il bat. Dans quelqu'un d'autre, mais il bat.", 9, jeu="[relieved] Il bat. [softly] Dans quelqu'un d'autre… mais il bat.", cloture=True),
            _p("lachance", "Tu as conduit comme un ambulancier. C'est le plus beau compliment que je fais.", 9, jeu="[warmly] Tu as conduit comme un ambulancier. [matter-of-fact] C'est le plus beau compliment que je fais.", cloture=True),
            _p("ginette", "C'est Ginette, de l'hôpital. Un patient est parti sans signer son congé. Avec mon ambulance.", 9, jeu="[annoyed] C'est Ginette, de l'hôpital. Un patient est parti sans signer son congé. [sarcastic] Avec mon ambulance."),
            _p("ginette", "Je te dirai pas son nom. Disons que tu l'as déjà couché une fois, dans le Faubourg.", 9, jeu="[firmly] Je te dirai pas son nom. [knowingly] Disons que tu l'as déjà couché une fois, dans le Faubourg."),
            _p("ginette", "Vingt-deux points de suture, pis il repart avec la trousse de morphine. Quel remerciement.", 9, jeu="[annoyed] Vingt-deux points de suture, pis il repart avec la trousse de morphine. [sarcastic] Quel remerciement."),
            _p("ginette", "Arrête l'ambulance, reprends la trousse. Lui, il se recoudra tout seul.", 9, jeu="[firmly] Arrête l'ambulance, reprends la trousse. [coldly] Lui, il se recoudra tout seul."),
            _p("ginette", "Il conduit avec des points dans le ventre. Il va finir par s'arrêter, aide-le.", 10, jeu="[matter-of-fact] Il conduit avec des points dans le ventre. [wryly] Il va finir par s'arrêter, aide-le."),
            _p("ginette", "Ses amis arrivent. Des Cravates, encore. On va manquer de fil, à ce rythme-là.", 11, jeu="[annoyed] Ses amis arrivent. Des Cravates, encore. [deadpan] On va manquer de fil, à ce rythme-là."),
            _p("ginette", "La trousse, fermée, à mon comptoir. Pis touche pas au contenu.", 12, jeu="[firmly] La trousse, fermée, à mon comptoir. [coldly] Pis touche pas au contenu."),
            # Acte 4 : la fin de h05, en personne ; puis l'appel et l'intro de h06.
            _p("ginette", "Scellée, complète. Il a même pas su l'ouvrir, le pauvre.", 13, jeu="[satisfied] Scellée, complète. [sarcastic] Il a même pas su l'ouvrir, le pauvre.", cloture=True),
            _p("ginette", "Tiens. Pis la prochaine fois qu'il se présente à l'urgence, c'est toi qui le recouds.", 13, jeu="[matter-of-fact] Tiens. [wryly] Pis la prochaine fois qu'il se présente à l'urgence, c'est toi qui le recouds.", cloture=True),
            # ⚠️ Coupée : « Lachance, à l'appareil. »
            _p("lachance", "Sal veut le reste en pilules. Viens, avant que je change d'idée.", 13, jeu="[quietly] Sal veut le reste en pilules. [firmly] Viens, avant que je change d'idée."),
            _p("lachance", "Trois ordonnances de calmants, trois patients qui n'existent pas. Ma signature, par exemple, est vraie.", 13, jeu="[quietly] Trois ordonnances de calmants, trois patients qui n'existent pas. [bitterly] Ma signature, par exemple, est vraie."),
            _p("lachance", "La pharmacie Tang, la Mission du port, pis le dentiste. Sal a ses habitudes partout.", 13, jeu="[matter-of-fact] La pharmacie Tang, la Mission du port, pis le dentiste. [wryly] Sal a ses habitudes partout."),
            _p("lachance", "Pas de police. Un pharmacien qui voit une étoile, il rappelle le médecin.", 13, jeu="[serious] Pas de police. [firmly] Un pharmacien qui voit une étoile, il rappelle le médecin."),
            _p("lachance", "Souris au comptoir. Les gens malades sourient pas, les gens qui font une commission, oui.", 14, jeu="[deadpan] Souris au comptoir. [wryly] Les gens malades sourient pas, les gens qui font une commission, oui."),
            _p("lachance", "Les trois sacs à Sal. Je veux pas savoir à qui il les revend.", 15, jeu="[quietly] Les trois sacs à Sal. [somber] Je veux pas savoir à qui il les revend."),
            _p("lachance", "Reviens me voir. J'ai besoin de l'entendre dire par quelqu'un.", 16, jeu="[softly] Reviens me voir. [quietly] J'ai besoin de l'entendre dire par quelqu'un."),
        ],
        "accueil": [
            _a("sal", "Son garde du corps? Neuf cent quatre-vingt-quinze, pis cinq de pourboire. Sa table est fermée.", 3, jeu="[amused] Son garde du corps? [satisfied] Neuf cent quatre-vingt-quinze, pis cinq de pourboire. [softly] Sa table est fermée."),
            _a("sal", "Trois sacs. Le docteur a une belle main d'écriture, le neveu. Son compte est fermé.", 15, jeu="[satisfied] Trois sacs. [amused] Le docteur a une belle main d'écriture, le neveu. [warmly] Son compte est fermé."),
        ],
    },
}
