"""La mission f02 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "f02",
    "titre": "Le stock de Gus",
    "donneur": "gus",
    "prerequis": ["f01"],
    "recompense": 350,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"rabais": {"armurerie": 0.85}, "message": "GUS TE FAIT CONFIANCE, UN PEU"},

    # ⚠️ Le camion dort à la fourrière (`porte:fourriere`, un lieu SPECIAUX déjà
    # dessiné) : `poserLeChar` le fait naître au bord de rue le plus proche de sa
    # porte, comme l'ambulance de h01 à l'hôpital — aucune fourrière n'a besoin
    # d'une baie de garage pour ça.
    #
    # « Des missions plus longues » (Martin, 22 sept. 2026) : Gus a déjà acheté le
    # gardien — on passe voir Gilles à la guérite (`parler`, sa poignée de main dite),
    # et les Boulonneux de la Shop, qui sentent la poudre, arrivent de loin sur le
    # camion au sortir du lot (`tuer`, `loin`, comme f01/e01).
    "objectifs": [
        {"type": "aller", "texte": "VA À LA FOURRIÈRE, DE NUIT",
         "lieu": "fourriere", "rayon": 6, "nuit": True},

        {"type": "parler", "texte": "PARLE À GILLES, À LA GUÉRITE",
         "cible": "gilles"},

        {"type": "monter", "texte": "PRENDS LE CAMION DE MUNITIONS",
         "vehicule": "camion", "ou": "porte:fourriere"},

        {"type": "tuer", "texte": "LES BOULONNEUX VEULENT TES CAISSES",
         "groupe": "boulonneux", "n": 3, "ou": "porte:fourriere", "loin": 10},

        {"type": "livrer", "texte": "LIVRE-LE À L'ARMURERIE SANS BOSSE",
         "lieu": "armurerie", "rayon": 4, "sans_degats": True},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Gus : bourru, transactionnel, jamais un mot
    # de plus que nécessaire ; une satisfaction sèche à la fin, pas un sourire.
    "dialogue": {
        "appel": [
            _l("gus", "Gus, de l'armurerie. Mon camion de munitions dort à la fourrière depuis une descente. Viens me voir.",
               jeu="[gruffly] Gus, de l'armurerie. Mon camion de munitions dort à la fourrière depuis une descente. [matter-of-fact] Viens me voir.")
        ],
        "intro": [
            _l("gus", "La police l'a saisi la semaine passée. Prends-le de nuit, personne a besoin de le savoir.",
               jeu="[gruffly] La police l'a saisi la semaine passée. [firmly] Prends-le de nuit… personne a besoin de le savoir."),
            _l("gus", "Ramène-le à mon comptoir sans une bosse. Une caisse de calibre, ça se magane pas en chemin.",
               jeu="[matter-of-fact] Ramène-le à mon comptoir sans une bosse. [gravely] Une caisse de calibre, ça se magane pas en chemin.")
        ],
        "pendant": [
            _p("gus", "Roule comme du monde. J'ai pas besoin d'un autre trou dans mon inventaire.", 4,
               jeu="[annoyed] Roule comme du monde. [gruffly] J'ai pas besoin d'un autre trou dans mon inventaire."),
            _p("gus", "Passe voir Gilles à la guérite. Il est déjà payé, parle-lui pas de prix.", 1,
               jeu="[matter-of-fact] Passe voir Gilles à la guérite. [gruffly] Il est déjà payé, parle-lui pas de prix."),
            _p("gus", "Des Boulonneux? Ils sentent la poudre de loin. Couche-les, pis touche pas à mes caisses.", 3,
               jeu="[annoyed] Des Boulonneux? Ils sentent la poudre de loin. [gruffly] Couche-les, pis touche pas à mes caisses.")
        ],
        # Gilles, à sa guérite : il se nomme (la première fois qu'on l'entend dans cette
        # mission), las, complice sans le moindre remords.
        "accueil": [
            _a("gilles", "C'est Gilles, le gardien. Gus m'a payé pour regarder ailleurs, fait que je regarde ailleurs.", 1,
               jeu="[wryly] C'est Gilles, le gardien. [deadpan] Gus m'a payé pour regarder ailleurs… fait que je regarde ailleurs.")
        ],
        "fin": [
            _l("gus", "Bon. Tout est là. T'es pas juste un autre neveu, toi.",
               jeu="[satisfied] Bon. Tout est là. [gruffly] T'es pas juste un autre neveu, toi."),
            _l("gus", "Reviens icitte, je te ferai un prix. Pas trop souvent, par exemple.",
               jeu="[matter-of-fact] Reviens icitte, je te ferai un prix. [wryly] Pas trop souvent, par exemple.")
        ],
        "echec": [
            _l("gus", "Perdu mon camion ET ma marchandise... Sacrament. Reviens quand t'es sérieux.",
               jeu="[annoyed] Perdu mon camion ET ma marchandise… [gruffly] Sacrament. Reviens quand t'es sérieux.")
        ]
    }
}
