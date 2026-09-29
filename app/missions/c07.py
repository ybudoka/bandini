"""La mission c07 — voir app/missions/__init__.py pour le moteur.

Monsieur Bois (docs/jalons/l-ecole-rivale.md, vague 2). Les élèves ont vendu le vieux mannequin de l'école — 1976, du
vrai érable — à la fourrière, pour quarante piasses. Gilles l'a gardé dans la boîte de son camion, et te le prête : on
ramène Monsieur Bois à l'école sans une égratignure. En échange, le vieux maître t'apprend la main de la mante
(`donne.technique` : le retournement du poignet, comme une leçon réussie au DOJO DION, sans la payer).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "c07",
    "titre": "Monsieur Bois",
    "donneur": "maitre",
    "prerequis": ["c06"],
    "recompense": 600,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"technique": "retournement_poignet", "message": "LE MAÎTRE T'APPREND LA MAIN DE LA MANTE"},

    # ⚠️ Le camion de Gilles attend à la porte de la fourrière (`monter`, `prete` : il est à Gilles, il ne se vend
    # pas) — la fourrière est DÉJÀ un lieu de mission (Gilles, le défi de la Shop). On le livre à la porte de l'école
    # (`ecole_mante`, un lieu de la bande du nord posé par `mantes.poser`, comme le Dragon d'or) : la prime de
    # `sans_degats` si Monsieur Bois arrive sans une bosse. Le camion détruit, c'est raté (`vehicule_detruit`).
    "objectifs": [
        {"type": "monter", "texte": "MONSIEUR BOIS EST DANS LE CAMION DE GILLES, À LA FOURRIÈRE",
         "vehicule": "camion", "ou": "porte:fourriere", "prete": "gilles"},

        {"type": "livrer", "texte": "RAMÈNE MONSIEUR BOIS À L'ÉCOLE SANS UNE ÉGRATIGNURE",
         "lieu": "ecole_mante", "rayon": 6, "sans_degats": True},
    ],

    # Le jeu de chaque réplique (`jeu=`) — le maître : une tendresse ridicule et sincère pour un morceau de bois, dite
    # le plus sérieusement du monde (c'est ce qui la rend drôle) ; au volant, l'inquiétude d'un vieux pour un autre
    # vieux ; à la fin, la gratitude, puis le ton du professeur qui enseigne pour de vrai — lent, net, trois temps —,
    # et une dernière pointe contre Irène. Il se nomme à l'appel, une fois.
    "dialogue": {
        "appel": [
            _l("maitre", "C'est Sifu Tam. Mes élèves ont vendu Monsieur Bois à la fourrière pour quarante piasses.",
               jeu="[disappointed] C'est Sifu Tam. [bitterly] Mes élèves ont vendu Monsieur Bois à la fourrière… pour quarante piasses.")
        ],
        "intro": [
            _l("maitre", "Monsieur Bois, c'est le mannequin de l'école. Mille neuf cent soixante-seize, du vrai érable.",
               jeu="[tenderly] Monsieur Bois, c'est le mannequin de l'école. [confident] Mille neuf cent soixante-seize… du vrai érable."),
            _l("maitre", "Il a mangé plus de coups que tous mes élèves ensemble. Pis il s'est jamais plaint.",
               jeu="[warmly] Il a mangé plus de coups que tous mes élèves ensemble. [deadpan] Pis il s'est jamais plaint."),
            _l("maitre", "Gilles, à la fourrière, l'a gardé dans la boîte de son camion. Ramène-le sans une égratignure.",
               jeu="[matter-of-fact] Gilles, à la fourrière, l'a gardé dans la boîte de son camion. [serious] Ramène-le sans une égratignure.")
        ],
        "pendant": [
            _p("maitre", "Gilles te prête son camion. Il m'a dit de te dire que c'est pas un char de course.", 0,
               jeu="[amused] Gilles te prête son camion. [deadpan] Il m'a dit de te dire que c'est pas un char de course."),
            _p("maitre", "Doucement dans les nids-de-poule. Monsieur Bois a mon âge, pis il a mal au dos lui aussi.", 1,
               jeu="[worried] Doucement dans les nids-de-poule. [wryly] Monsieur Bois a mon âge… pis il a mal au dos lui aussi.")
        ],
        "fin": [
            _l("maitre", "Monsieur Bois est à sa place. Regarde-le, il sourit, je te jure.",
               jeu="[relieved] Monsieur Bois est à sa place. [amused] Regarde-le… il sourit, je te jure."),
            _l("maitre", "En échange, je t'apprends la main de la mante. Il frappe, tu accueilles, tu tournes.",
               jeu="[serious] En échange, je t'apprends la main de la mante. [calm] Il frappe… tu accueilles… tu tournes."),
            _l("maitre", "Garde-la pour les frimeurs. Pis dis pas à Irène que c'était gratis, elle va vouloir la même.",
               jeu="[knowingly] Garde-la pour les frimeurs. [mischievously] Pis dis pas à Irène que c'était gratis… elle va vouloir la même.")
        ],
        "echec": [
            _l("maitre", "Monsieur Bois a pas fait le voyage. Cinquante ans debout, pis c'est toi qui l'achèves.",
               jeu="[somber] Monsieur Bois a pas fait le voyage. [bitterly] Cinquante ans debout… pis c'est toi qui l'achèves.")
        ]
    },

    # Intention (intro) : le maître devant ses deux mannequins, la main sur le vide où était le troisième ; la caméra
    # va voir la fourrière pendant qu'il parle de Gilles. ⚠️ La coupe en `ensemble`, PUIS la réplique. Intention
    # (fin) : à sa porte, Monsieur Bois rentré — et la leçon, dite lentement, trois temps.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "porte:fourriere", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:maitre", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
        ],
    },
}
