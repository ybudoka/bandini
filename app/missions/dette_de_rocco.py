"""Le chapitre de la dette de Rocco — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague D). Martin, après La
Pointe : « c'est bon : on y va ». Les quatre jobs de Sal (d01 à d04, M16, arc D — une à quatre étapes chacune, de
22 s à 4 min 23 au chronomètre de la partie de Martin) deviennent quatre ACTES : la dette prend un visage, puis
Sal la fait travailler — Momo, les faux Ciseaux, la collecte. Mesuré chez Martin : 522 s pour les quatre, rien
d'ajouté pour faire durer. Mourir chez Ti-Paul fait reprendre la collecte, pas la coupe de cheveux.

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de d01
  restent ceux du chapitre ; la fin de chaque job se dit à l'ouverture de l'acte suivant — en personne : chaque acte
  finit chez Sal (le garage, puis le terminus) —, suivie de l'appel et de l'intro du job suivant ; la fin de d04
  reste la fin du chapitre ; chaque job garde son échec (`_e`, accroché à son acte) ;
- QUI PARLE SE NOMME une fois par chapitre : Sal se nomme à l'appel de d01 ; ses trois appels suivants perdent
  « C'est Sal, au terminus », « Sal, le barbier » et « Ici Sal » — la même voix, coupée au silence (`ffmpeg`) ; celui
  de d02 perd aussi « Passe me voir » (il est à côté de toi, devant le garage) ;
- chaque acte paie sa prime et efface sa part de dette en finissant (`donne` sur l'objectif qui le finit) ;
- la scène d'intro de d01 (le fauteuil, puis le garage) reste celle du chapitre ; les scènes d'intro écrites de d02,
  d03 et d04 tombent (leurs répliques se disent au marqueur), comme au pilote.
- h03 attend d01 (le premier acte), d09 attend d04, et la suite (`garage_de_rocco`) attend d04 : un prérequis peut
  viser un acte.
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "dette_de_rocco",
    "titre": "La dette de Rocco",
    "donneur": "sal",
    "prerequis": ["m6"],
    "remplace": ["d01", "d02", "d03", "d04"],
    "recompense": 400,
    "donne": {"dette": -800, "message": "LA COLLECTE EST FAITE — SAL EFFACE 800 $"},

    "objectifs": [
        # --- Acte 1 (d01, « Le barbier »).
        # Le barbier (M16, arc D — la dette de Rocco, 30 sept. 2026). La dette court depuis la première nuit
        # (`economie.DETTE` : quinze mille, 2 % par nuit, les rappels, puis ses hommes) ; ici, elle prend un visage. Sal
        # Ferraro coupe les cheveux au milieu du terminus : il te fait asseoir, te fait la barbe en te racontant ce que ton
        # oncle lui devait, puis il veut voir sa garantie — le garage de Rocco. On l'y mène (`proteger`, le patron de s10) :
        # il le regarde comme on regarde un char qu'on va acheter.
        {"type": "acte", "texte": "ACTE 1 — LE BARBIER", "donneur": "sal"},  # 0
        {"type": "proteger", "texte": "SAL VEUT VOIR SA GARANTIE : MÈNE-LE AU GARAGE", "cible": "sal", "lieu": "garage", "rayon": 5, "donne": {"message": "SAL T'A À L'ŒIL", "prime": 100}},  # 1
        # --- Acte 2 (d02, « Le premier versement »).
        # Le premier versement (M16, arc D, 30 sept. 2026). Sal veut cinq cents piasses ; tu ne les as pas — ou tu ne veux
        # pas les lui donner. Il a mieux : Momo, un chauffeur de taxi du terminus, lui doit exactement ça, et il se sauve
        # chaque fois qu'il voit la chaise de barbier. On le rattrape (le fuyard en taxi, le patron de m97), l'enveloppe
        # tombe, un témoin appelle la police, et on rapporte l'argent à Sal : c'est ton premier versement (`donne.dette`).
        {"type": "acte", "texte": "ACTE 2 — LE PREMIER VERSEMENT", "donneur": "sal"},  # 2
        {"type": "ramasser", "texte": "MOMO LE TAXI DOIT 500 $ À SAL : RATTRAPE-LE", "cible": "fuyard", "vehicule": "taxi"},  # 3
        {"type": "semer", "texte": "UN TÉMOIN A APPELÉ LA POLICE : SÈME-LA", "etoiles": 1},  # 4
        {"type": "parler", "texte": "RAPPORTE L'ENVELOPPE DE MOMO À SAL, AU TERMINUS", "cible": "sal", "donne": {"dette": -500, "message": "L'ENVELOPPE DE MOMO PAIE TON PREMIER VERSEMENT", "prime": 100}},  # 5
        # --- Acte 3 (d03, « Les Ciseaux »).
        # Les Ciseaux (M16, arc D, 30 sept. 2026). Les hommes de Sal, on les appelle les Ciseaux : ils coupent ce qui
        # dépasse. Mais aux Quais, trois gars collectent EN SON NOM, et gardent tout. Sal ne peut pas envoyer les siens
        # régler ça — ça ferait une guerre ; toi, t'es « la famille ». On couche les faux Ciseaux devant l'Hôtel Bandini,
        # on sème la police qui s'en mêle, et on revient au terminus.
        {"type": "acte", "texte": "ACTE 3 — LES CISEAUX", "donneur": "sal"},  # 6
        {"type": "tuer", "texte": "DE FAUX CISEAUX COLLECTENT AUX QUAIS : COUCHE-LES", "groupe": "cravates", "n": 3, "ou": "hotel", "arme": "poing_americain", "chef": True},  # 7
        {"type": "semer", "texte": "LA POLICE DES QUAIS S'EN MÊLE : SÈME-LA", "etoiles": 2},  # 8
        {"type": "parler", "texte": "DIS À SAL QUE C'EST RÉGLÉ, AU TERMINUS", "cible": "sal", "donne": {"dette": -300, "message": "LES CISEAUX, LES VRAIS, TE SALUENT", "prime": 300}},  # 9
        # --- Acte 4 (d04, « La collecte du barbier »).
        # La collecte du barbier (M16, arc D, 30 sept. 2026). Sal te confie sa tournée : trois débiteurs dans trois
        # districts — Ti-Paul (les Érables), Lulu (les Quais), Ovila (La Pointe). Les trois que Josée t'a présentés au
        # tour du propriétaire (m6), et que tu croyais connaître : chacun cache une dette chez le barbier (leurs fiches, dans
        # `docs/personnages/`). On passe les voir, ils paient chacun à leur façon, et on rapporte le tout au terminus.
        {"type": "acte", "texte": "ACTE 4 — LA COLLECTE DU BARBIER", "donneur": "sal"},  # 10
        {"type": "parler", "texte": "TI-PAUL DOIT À SAL : VA COLLECTER AU DÉPANNEUR", "cible": "tipaul"},  # 11
        {"type": "parler", "texte": "LULU AUSSI : VA COLLECTER À LA CANTINE", "cible": "lulu"},  # 12
        {"type": "parler", "texte": "PIS OVILA : VA COLLECTER AU PHARE", "cible": "ovila"},  # 13
        {"type": "parler", "texte": "RAPPORTE LA COLLECTE À SAL, AU TERMINUS", "cible": "sal"},  # 14
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "porte:garage", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # d01 — Le jeu de chaque réplique (`jeu=`) — Sal : la douceur de qui n'a jamais eu besoin d'élever la voix. Il parle
    # bas, lentement, en coupant les cheveux ; il appelle le joueur « le neveu », et la menace ne se dit jamais, elle
    # se sous-entend. L'arc : l'hospitalité (l'appel, le fauteuil), les affaires (le compte), l'œil du prêteur (le
    # garage) — et un sourire qui ne réchauffe rien.
    # d02 — Le jeu de chaque réplique (`jeu=`) — Sal : le prêteur amusé, qui sait tout de ses débiteurs et en parle comme
    # d'enfants turbulents. Au combiné, il est plus sec ; à la fin, le compte se dit comme une caresse — pis la
    # leçon, froidement : on ne se sauve pas de Sal.
    # d03 — Le jeu de chaque réplique (`jeu=`) — Sal : pour la première fois, il est vexé, et ça le rend plus doux encore.
    # On parle de son NOM : il y tient plus qu'à l'argent. À la fin, une fierté de patriarche, vite rangée.
    # d04 — Le jeu de chaque réplique (`jeu=`) — Sal : il donne sa tournée comme on donne les clés de la maison, et il
    # connaît chaque débiteur par sa faiblesse. Ti-Paul paie en jasant (gêné, il ne parle jamais de lui) ; Lulu paie
    # en te grondant, pour se donner une contenance ; Ovila paie en vouvoyant, avec ce qu'il a. À la fin, Sal compte
    # et comprend que tu as vu les visages — il te le reproche doucement.
    "dialogue": {
        "appel": [
            _l("sal", "Salut, le neveu. Sal Ferraro, le barbier du terminus. Ton oncle pis moi, on avait un compte.", jeu="[warmly] Salut, le neveu. Sal Ferraro, le barbier du terminus. [quietly] Ton oncle pis moi, on avait un compte."),
        ],
        "intro": [
            _l("sal", "Assis-toi. Une coupe, c'est gratis pour la famille. Le reste, par exemple, ça se paie.", jeu="[warmly] Assis-toi. Une coupe, c'est gratis pour la famille. [softly] Le reste, par exemple… ça se paie."),
            _l("sal", "Rocco me devait quinze mille piasses. Il est parti, mais le compte, lui, est resté icitte.", jeu="[calm] Rocco me devait quinze mille piasses. [knowingly] Il est parti… mais le compte, lui, est resté icitte."),
            _l("sal", "Il m'avait mis son garage en garantie. Viens me le montrer, j'aime savoir ce qui m'appartient.", jeu="[matter-of-fact] Il m'avait mis son garage en garantie. [smugly] Viens me le montrer… j'aime savoir ce qui m'appartient."),
        ],
        "fin": [
            _l("sal", "Trois cents, trois cents, pis une montre. Le vieux Ovila, toujours le même.", jeu="[amused] Trois cents, trois cents, pis une montre. [softly] Le vieux Ovila… toujours le même."),
            _l("sal", "T'as vu leurs faces, hein? C'est pour ça que j'envoie pas mes Ciseaux chez les amis.", jeu="[knowingly] T'as vu leurs faces, hein? [serious] C'est pour ça que j'envoie pas mes Ciseaux chez les amis."),
            _l("sal", "Huit cents de moins sur ta dette, tu vois? Chez nous, tout se paie. Même la gêne.", jeu="[warmly] Huit cents de moins sur ta dette, tu vois? [smugly] Chez nous, tout se paie. Même la gêne."),
        ],
        "echec": [
            _e("sal", "Tu m'as laissé tomber en chemin, le neveu. Rocco aussi me faisait ça. Regarde où il est.", 0, jeu="[disappointed] Tu m'as laissé tomber en chemin, le neveu. [coldly] Rocco aussi me faisait ça. Regarde où il est."),
            _e("sal", "Momo court encore. Pis toi, le neveu, t'as toujours ta dette.", 2, jeu="[disappointed] Momo court encore. [coldly] Pis toi, le neveu… t'as toujours ta dette."),
            _e("sal", "Ils collectent encore, pis ils disent que le barbier a envoyé un enfant. Merci bien.", 6, jeu="[coldly] Ils collectent encore, pis ils disent que le barbier a envoyé un enfant. [sarcastic] Merci bien."),
            _e("sal", "Une collecte à moitié faite, c'est une collecte que je fais moi-même. Pis ça, personne aime ça.", 10, jeu="[coldly] Une collecte à moitié faite, c'est une collecte que je fais moi-même. [menacingly] Pis ça, personne aime ça."),
        ],
        "pendant": [
            _p("sal", "Marche pas trop vite, le neveu. À mon âge, on court juste après l'argent.", 1, jeu="[amused] Marche pas trop vite, le neveu. [wryly] À mon âge, on court juste après l'argent."),
            # Acte 2 : la fin de d01, en personne ; puis l'appel et l'intro de d02.
            _p("sal", "Belle bâtisse. Ton oncle avait du goût pour les affaires qu'il payait pas.", 2, jeu="[impressed] Belle bâtisse. [wryly] Ton oncle avait du goût… pour les affaires qu'il payait pas."),
            _p("sal", "Tant que tu paies, le garage reste à ton nom. Mes hommes passent chaque semaine, tu les connais.", 2, jeu="[calm] Tant que tu paies, le garage reste à ton nom. [menacingly] Mes hommes passent chaque semaine… tu les connais."),
            _p("sal", "Tiens, pour le taxi. Reviens me voir quand t'auras envie de travailler ta dette.", 2, jeu="[warmly] Tiens, pour le taxi. [knowingly] Reviens me voir quand t'auras envie de travailler ta dette."),
            # ⚠️ Coupée (2 oct. 2026) : « C'est Sal, au terminus. » et « Passe me voir. » — il est là, et il s'est nommé.
            _p("sal", "Ton premier versement tombe aujourd'hui, le neveu.", 2, jeu="[matter-of-fact] Ton premier versement tombe aujourd'hui, le neveu."),
            _p("sal", "Cinq cents piasses. Tu les as pas? Je le savais, personne les a dans ta famille.", 2, jeu="[amused] Cinq cents piasses. Tu les as pas? [wryly] Je le savais, personne les a dans ta famille."),
            _p("sal", "Momo, un chauffeur d'icitte, me doit justement ça. Il se sauve chaque fois qu'il voit ma chaise.", 2, jeu="[knowingly] Momo, un chauffeur d'icitte, me doit justement ça. [amused] Il se sauve chaque fois qu'il voit ma chaise."),
            _p("sal", "Ramène-moi son enveloppe, pis on dira que c'est toi qui as payé.", 2, jeu="[softly] Ramène-moi son enveloppe… [warmly] pis on dira que c'est toi qui as payé."),
            _p("sal", "Le v'là qui démarre. Il conduit comme il paie, le neveu : en retard pis tout croche.", 3, jeu="[amused] Le v'là qui démarre. [wryly] Il conduit comme il paie, le neveu : en retard pis tout croche."),
            _p("sal", "Les madames du terminus appellent la police pour un rien. Fais-toi oublier.", 4, jeu="[annoyed] Les madames du terminus appellent la police pour un rien. [calm] Fais-toi oublier."),
            _p("sal", "L'enveloppe, pas le taxi. Je coupe des cheveux, moi, je vends pas de chars.", 5, jeu="[matter-of-fact] L'enveloppe, pas le taxi. [wryly] Je coupe des cheveux, moi… je vends pas de chars."),
            # Acte 3 : la fin de d02, en personne ; puis l'appel et l'intro de d03.
            _p("sal", "Cinq cents, juste. Momo compte mieux qu'il conduit.", 6, jeu="[satisfied] Cinq cents, juste. [amused] Momo compte mieux qu'il conduit."),
            _p("sal", "Je te les marque dans mon livre. Pis ça, c'est pour ta peine : on travaille pas pour rien chez nous.", 6, jeu="[warmly] Je te les marque dans mon livre. [knowingly] Pis ça, c'est pour ta peine : on travaille pas pour rien chez nous."),
            # ⚠️ Coupée : « Sal, le barbier. »
            _p("sal", "J'ai un problème de réputation, le neveu. Pis toi, t'as une dette.", 6, jeu="[annoyed] J'ai un problème de réputation, le neveu. [calm] Pis toi, t'as une dette."),
            _p("sal", "Mes hommes, on les appelle les Ciseaux. Ils coupent ce qui dépasse.", 6, jeu="[calm] Mes hommes, on les appelle les Ciseaux. [menacingly] Ils coupent ce qui dépasse."),
            _p("sal", "Aux Quais, trois gars collectent en mon nom, devant l'hôtel. Pis ils gardent tout.", 6, jeu="[annoyed] Aux Quais, trois gars collectent en mon nom, devant l'hôtel. [bitterly] Pis ils gardent tout."),
            _p("sal", "Si j'envoie les miens, ça fait une guerre. Toi, t'es la famille. Va leur couper les cheveux.", 6, jeu="[matter-of-fact] Si j'envoie les miens, ça fait une guerre. [softly] Toi, t'es la famille… [menacingly] Va leur couper les cheveux."),
            _p("sal", "Le plus grand, c'est leur chef. Il se promène avec un bâton comme si c'était une canne.", 7, jeu="[wryly] Le plus grand, c'est leur chef. [amused] Il se promène avec un bâton comme si c'était une canne."),
            _p("sal", "La police des Quais dort d'habitude. Faut croire que t'as fait du bruit.", 8, jeu="[amused] La police des Quais dort d'habitude. [knowingly] Faut croire que t'as fait du bruit."),
            # Acte 4 : la fin de d03, en personne ; puis l'appel et l'intro de d04.
            _p("sal", "Trois gars de moins qui disent mon nom. Mon nom, le neveu, c'est tout ce que j'ai.", 10, jeu="[satisfied] Trois gars de moins qui disent mon nom. [serious] Mon nom, le neveu… c'est tout ce que j'ai."),
            _p("sal", "Ton oncle aurait négocié. Toi, tu règles. Je sais pas encore si c'est mieux.", 10, jeu="[impressed] Ton oncle aurait négocié. Toi, tu règles. [wryly] Je sais pas encore si c'est mieux."),
            # ⚠️ Coupée : « Ici Sal. »
            _p("sal", "J'ai une tournée pour toi, le neveu. Trois clients, trois quartiers.", 10, jeu="[warmly] J'ai une tournée pour toi, le neveu. [matter-of-fact] Trois clients, trois quartiers."),
            _p("sal", "Ti-Paul au dépanneur, Lulu à la cantine, Ovila au phare. Tu les connais, je pense.", 10, jeu="[knowingly] Ti-Paul au dépanneur, Lulu à la cantine, Ovila au phare. [wryly] Tu les connais, je pense."),
            _p("sal", "Tout le monde doit quelque chose à quelqu'un, dans cette ville. Moi, j'ai juste un meilleur livre.", 10, jeu="[amused] Tout le monde doit quelque chose à quelqu'un, dans cette ville. [smugly] Moi, j'ai juste un meilleur livre."),
            _p("sal", "Sois poli. Un client qui paie, ça se garde comme un client qui se fait couper les cheveux.", 10, jeu="[softly] Sois poli. [calm] Un client qui paie, ça se garde comme un client qui se fait couper les cheveux."),
            _p("sal", "Ti-Paul va te parler de la température. Laisse-le faire, il finit toujours par payer.", 11, jeu="[amused] Ti-Paul va te parler de la température. [knowingly] Laisse-le faire… il finit toujours par payer."),
            _p("sal", "Lulu va te chicaner. C'est sa façon de dire qu'elle a honte.", 12, jeu="[knowingly] Lulu va te chicaner. [softly] C'est sa façon de dire qu'elle a honte."),
            _p("sal", "Le vieux au phare, lui, prends ce qu'il te donne. Il a jamais rien de plus.", 13, jeu="[calm] Le vieux au phare, lui, prends ce qu'il te donne. [serious] Il a jamais rien de plus."),
            _p("sal", "Reviens avec tout, le neveu. Je compte, moi, le soir, avant de dormir.", 14, jeu="[matter-of-fact] Reviens avec tout, le neveu. [softly] Je compte, moi… le soir, avant de dormir."),
        ],
        "accueil": [
            _a("tipaul", "Sal t'envoie? Eh ben, tiens, l'ami, trois cents. Pis tu diras rien à Josée, hein?", 11, jeu="[nervously] Sal t'envoie? Eh ben… [knowingly] tiens, l'ami, trois cents. [worried] Pis tu diras rien à Josée, hein?"),
            _a("lulu", "Toi, collecteur pour Sal? Mon grand, t'as pas honte? Tiens, prends, pis va-t'en.", 12, jeu="[annoyed] Toi, collecteur pour Sal? [teasing] Mon grand, t'as pas honte? [softly] Tiens, prends… pis va-t'en."),
            _a("ovila", "Je n'ai que ceci. La montre de mon père. Dites-lui qu'elle retarde un peu.", 13, jeu="[softly] Je n'ai que ceci. La montre de mon père. [calm] Dites-lui qu'elle retarde un peu."),
        ],
    },
}
