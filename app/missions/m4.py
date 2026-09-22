"""La mission m4 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m4", "titre": "Le lunch du sergent", "donneur": "bouchard", "prerequis": ["m3"],
    "recompense": 400, "phase": 1, "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"sergent_ami": True, "message": "LE SERGENT EST TON AMI"},
    "objectifs": [
        {"type": "aller", "lieu": "poste", "rayon": 5, "nuit": True, "texte": "VA AU POSTE, DE NUIT"},
        {"type": "monter", "vehicule": "police", "ou": "porte:poste", "texte": "PRENDS L'AUTO-PATROUILLE"},
        {"type": "semer", "etoiles": 2, "escorte": "ti_guy", "texte": "SÈME LA POLICE — TI-GUY TE SUIT"},
        # « Des missions plus longues » (22 sept. 2026) : trois étapes de plus, qui racontent. Une
        # auto-patrouille a des numéros — un DÉTOUR à l'autre bout de la ville, par la fourrière de La
        # Shop (un lieu de mission déjà : aucun devant de porte ne bouge). Au garage, deux Cravates
        # veulent l'auto (ils ARRIVENT, `loin` ; des petits, les poings nus : on est à m4). Puis on
        # rapporte les clés au casse-croûte — le lunch du titre, qu'il mange pendant qu'on vole.
        {"type": "aller", "lieu": "fourriere", "rayon": 5, "texte": "PASSE PAR LA FOURRIÈRE — ON DÉVISSE LES PLAQUES"},
        {"type": "livrer", "lieu": "garage", "rayon": 4, "texte": "LARGUE L'AUTO AU GARAGE"},
        {"type": "tuer", "groupe": "cravates", "n": 2, "ou": "porte:garage", "arme": "", "vie": 70, "loin": 12,
         "texte": "DEUX CRAVATES VEULENT L'AUTO — COUCHE-LES"},
        {"type": "aller", "lieu": "casse_croute", "rayon": 6, "texte": "RAPPORTE LES CLÉS AU SERGENT"},
    ],
    # ⚠️ **ELLE N'ÉCRIT AUCUNE SCÈNE, et elle en a deux** — le bloc Lego
    # (`scene_par_defaut`, dans `__init__.py`). Bouchard parle dedans : le défaut
    # sort voir le poste par une coupe (le lieu que nomme son premier objectif —
    # l'auto-patrouille, elle, est le deuxième), il croise les bras, il finit sa
    # phrase. À la fin on est à la porte du casse-croûte, et lui dedans, à table : le
    # défaut va chez lui par une coupe, et il parle au combiné (comme m51 : un donneur
    # `point:` ne sort pas, et `retourner` ne le trouverait pas en ville).
    # Le jeu de chaque réplique (`jeu=`) — le sergent Bouchard : bourru, et il baisse la voix pour le sale ;
    # pince-sans-rire sur son dîner (l'alibi, le pouding chômeur), jamais un merci.
    "dialogue": {
        "appel": [_l("bouchard", "Ici le sergent Bouchard. Marco m'a parlé de toi. Viens dîner au casse-croûte, j'ai une job.",
                     jeu="[gruffly] Ici le sergent Bouchard. Marco m'a parlé de toi. Viens dîner au casse-croûte… j'ai une job.")],
        "intro": [
            _l("bouchard", "Y a une auto-patrouille au poste que j'aimerais voir disparaître. Papiers pas propres.",
               jeu="[quietly] Y a une auto-patrouille au poste que j'aimerais voir disparaître. Papiers… pas propres."),
            _l("bouchard", "Prends-la de nuit, sans témoin. Ti-Guy va te suivre en char, pour faire diversion.",
               jeu="[serious] Prends-la de nuit, sans témoin. Ti-Guy va te suivre en char, pour faire diversion."),
            _l("bouchard", "Largue-la au garage. Pis si mes gars te courent après, sème-les.",
               jeu="[firmly] Largue-la au garage. Pis si mes gars te courent après… sème-les."),
        ],
        "fin": [
            _l("bouchard", "Laisse les clés au comptoir, le jeune. Moi, je finis mon pouding chômeur.",
               jeu="[gruffly] Laisse les clés au comptoir, le jeune. [deadpan] Moi, je finis mon pouding chômeur."),
            _l("bouchard", "Parfait. À partir d'aujourd'hui, si un de mes gars te pogne, tu dis mon nom.",
               jeu="[satisfied] Parfait. À partir d'aujourd'hui, si un de mes gars te pogne… tu dis mon nom."),
            _l("bouchard", "Un mot d'avertissement : Josée, au bar, cherche du monde comme toi. Fais attention.",
               jeu="[gravely] Un mot d'avertissement… Josée, au bar, cherche du monde comme toi. Fais attention."),
        ],
        "echec": [_l("bouchard", "J'ai rien vu, j'ai rien entendu. Reviens quand ça sera calme.",
                     jeu="[nervously] J'ai rien vu, j'ai rien entendu. [sighs] Reviens quand ça sera calme.")],
        # PENDANT (2e vague des scènes) : dite quand son objectif commence.
        "pendant": [
            _p("ti_guy", "C'est Ti-Guy, j'suis juste derrière toi. Roule, j'm'occupe des bœufs.", 2,
               jeu="[confident] C'est Ti-Guy, j'suis juste derrière toi. Roule, j'm'occupe des bœufs."),
            # Dit en personne, au casse-croûte, avant qu'on sorte : l'alibi.
            _p("bouchard", "Moi, je reste icitte à manger. Un sergent qui dîne, ça fait un bon alibi.", 0,
               jeu="[knowingly] Moi, je reste icitte à manger. [deadpan] Un sergent qui dîne… ça fait un bon alibi."),
            _p("bouchard", "Une auto-patrouille, ça a des numéros. Passe par la fourrière, le gardien va les dévisser.", 3,
               jeu="[quietly] Une auto-patrouille, ça a des numéros. [matter-of-fact] Passe par la fourrière… le gardien va les dévisser."),
            _p("ti_guy", "Heille, deux Cravates reniflent l'auto! Montre-leur que le garage est fermé.", 5,
               jeu="[excited] Heille, deux Cravates reniflent l'auto! [mischievously] Montre-leur que le garage est fermé."),
            _p("bouchard", "Propre. Astheure, rapporte-moi les clés au casse-croûte.", 6,
               jeu="[satisfied] Propre. [gruffly] Astheure, rapporte-moi les clés au casse-croûte."),
        ],
    },
}
