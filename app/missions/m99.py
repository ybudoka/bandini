"""La mission m99 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m99", "titre": "Le dernier traversier", "donneur": "berube", "prerequis": ["m6"],
    "recompense": 0, "phase": 1, "echec": ["mort", "arrete", "etoile"],
    # _Sacrer son camp_ (M13) : la fin qu'on choisit quand on en a assez. Quinze mille piastres en
    # poche — ce que Rocco devait à Sal, qu'on l'ait payé ou non (l'arc D ne l'exige pas : on peut
    # partir sans payer Rocco).
    "exige": {"argent_min": 15000},
    # ⚠️ `generique` : après la fin, le narrateur du Clairon ferme le jeu comme il l'a ouvert, puis le
    # BILAN. La partie continue : le traversier arrive à La Pointe, et la ville reste.
    "donne": {"generique": True},
    # De nuit, sans une étoile, au bout du quai des Quais ; le passage se paie comptant ; on monte sur
    # le pont, en char ou à pied, et c'est le DÉPART qui accomplit la mission — manquer le traversier,
    # c'est attendre le suivant, deux heures plus tard.
    "objectifs": [
        {"type": "aller", "lieu": "traversier:quais", "rayon": 6, "nuit": True, "sans_etoile": True,
         "texte": "REVIENS AU QUAI DU TRAVERSIER, DE NUIT"},
        {"type": "payer", "montant": 500, "texte": "PAIE LE PASSAGE — 500 $"},
        {"type": "embarquer", "escale": "quais", "sans_etoile": True,
         "texte": "MONTE SUR LE PONT DU TRAVERSIER"},
    ],
    # L'intro : la coupe montre le traversier à quai, Bérubé fait son prix les bras croisés. La fin se
    # joue sur le pont qui s'écarte du quai : le capitaine vient te voir, dit ses deux phrases, et rentre
    # dans sa cabine (`entrer` vers toi : il disparaît là où tu es, c'est-à-dire à bord). Chaque geste
    # en `ensemble`, PUIS sa `dire` : c'est la voix qui retient la scène.
    #
    # ⚠️ LE GÉNÉRIQUE ne connaît que des portes de la ville et le joueur : la ville est figée sous une
    # scène, et le traversier avec elle. Il repasse par où l'histoire est passée — le terminus où l'on
    # est descendu du car, le garage, la planque, le bar de Josée, le phare — et finit sur le pont, au
    # large, où les chiffres montent un à un.
    "scenes": {
        # ⚠️ La coupe `ensemble`, PUIS la `dire` : c'est la voix qui retient la scène. Dans l'autre
        # ordre, la coupe (3 s) finissait avant la première réplique (6 s) et la seconde la coupait.
        "intro": [
            {"type": "coupe", "vers": "traversier:quais", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
        "fin": [
            {"type": "marcher", "acteur": "donneur", "vers": "joueur", "pres": 22, "duree": 60},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "hausser", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "entrer", "acteur": "donneur", "dans": "joueur", "duree": 40},
        ],
        "generique": [
            {"type": "coupe", "vers": "joueur", "ferme": 60, "ouvre": 0, "tient": 30},
            {"type": "son", "musique": "generique"},
            {"type": "dire", "ensemble": True},
            {"type": "coupe", "vers": ["porte:terminus", "porte:garage", "porte:planque", "porte:bar", "porte:phare"],
             "ferme": 40, "ouvre": 40, "tient": 220},
            {"type": "coupe", "vers": "joueur", "ferme": 40, "ouvre": 60, "tient": 30},
            {"type": "titre", "texte": "{fortune} $", "sous": "FORTUNE", "monte": 20, "tenu": 100, "descend": 20},
            {"type": "titre", "texte": "{missions}", "sous": "MISSIONS", "monte": 20, "tenu": 100, "descend": 20},
            {"type": "titre", "texte": "{proprietes}", "sous": "PROPRIÉTÉS", "monte": 20, "tenu": 100, "descend": 20},
            {"type": "titre", "texte": "{jours}", "sous": "JOURS À BAIE-DES-BRUMES", "monte": 20, "tenu": 100,
             "descend": 20},
            {"type": "titre", "texte": "{dette}", "sous": "LA DETTE DE ROCCO", "monte": 20, "tenu": 120, "descend": 20},
            {"type": "titre", "logo": True, "sous": "SACRER SON CAMP", "monte": 30, "tenu": 200, "descend": 40},
        ],
    },
    # Le jeu de chaque réplique (`jeu=`) — Bérubé : un vieux capitaine qui a tout fait passer, sans
    # juger ni presser ; il vouvoie personne et ne sourit qu'à la fin. Le narrateur referme l'ouverture :
    # le même car, le même billet, dans l'autre sens.
    "dialogue": {
        "appel": [_l("berube", "Capitaine Bérubé, du traversier. Paraît que tu cherches à partir sans bruit.",
                     jeu="[calm] Capitaine Bérubé, du traversier. [knowingly] Paraît que tu cherches à partir… sans bruit.")],
        "intro": [
            _l("berube", "Le dernier départ, c'est la nuit. Pas de police sur mon pont, pas de questions sur ton bagage.",
               jeu="[matter-of-fact] Le dernier départ, c'est la nuit. Pas de police sur mon pont… pas de questions sur ton bagage."),
            _l("berube", "Reviens quand il fera noir, personne à tes trousses. Pis apporte de quoi payer.",
               jeu="[firmly] Reviens quand il fera noir, personne à tes trousses. [deadpan] Pis apporte de quoi payer."),
        ],
        "fin": [
            _l("berube", "J'en ai fait passer, du monde, sur cette eau-là. Ton oncle aussi, une fois.",
               jeu="[gravely] J'en ai fait passer, du monde, sur cette eau-là… [softly] Ton oncle aussi, une fois."),
            _l("berube", "Lui, il est revenu. Toi, regarde pas en arrière.",
               jeu="[wryly] Lui, il est revenu. [warmly] Toi… regarde pas en arrière."),
        ],
        "echec": [_l("berube", "Je fais pas traverser les sirènes. Reviens quand t'auras la paix.",
                     jeu="[coldly] Je fais pas traverser les sirènes. Reviens quand t'auras la paix.")],
        "pendant": [
            _p("berube", "Je t'attends au bout du quai. La nuit, pis pas une étoile derrière toi.", 0,
               jeu="[calm] Je t'attends au bout du quai. [quietly] La nuit… pis pas une étoile derrière toi."),
            _p("berube", "Cinq cents. C'est le prix du silence, pas celui du billet.", 1,
               jeu="[deadpan] Cinq cents. [knowingly] C'est le prix du silence, pas celui du billet."),
            _p("berube", "Monte sur le pont. À l'heure pile, on largue les amarres.", 2,
               jeu="[firmly] Monte sur le pont. À l'heure pile… on largue les amarres."),
        ],
        "generique": [
            _l("narrateur", "Il était arrivé par le car de six heures, avec cinquante piastres pis un billet aller simple.",
               jeu="[softly] Il était arrivé par le car de six heures, avec cinquante piastres… pis un billet aller simple."),
            _l("narrateur", "Il repart par le dernier traversier, de nuit, sans une sirène derrière lui.",
               jeu="[quietly] Il repart par le dernier traversier, de nuit… sans une sirène derrière lui."),
            _l("narrateur", "La ville, elle, se mêle encore de ses affaires. Le brouillard aussi.",
               jeu="[wryly] La ville, elle, se mêle encore de ses affaires. [sighs] Le brouillard aussi."),
            _l("narrateur", "Le Clairon, le lendemain : le neveu de Rocco a sacré son camp. Bonne chance, le jeune.",
               jeu="[dramatic] Le Clairon, le lendemain : le neveu de Rocco a sacré son camp. [warmly] Bonne chance… le jeune."),
        ],
    },
}
