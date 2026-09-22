"""La mission q02 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "q02",
    "titre": "Le poisson du vendredi",
    "donneur": "lulu",
    # ⚠️ Après e01 (Ti-Paul dit d'aller la voir) : le plan la voulait après q01, qui n'existe pas encore.
    "prerequis": ["e01"],
    "recompense": 250,
    "echec": ["arrete", "vehicule_detruit"],
    "donne": {"message": "LE POISSON EST ARRIVÉ ENTIER"},

    # ⚠️ Lulu se tient DEDANS (cantine) : rien de la ville ne se pose avant la sortie, mais un char
    # de mission se pose dès le début (`Histoire.poser`) — la coupe de l'intro (celle du défaut : le
    # premier lieu que nomme un objectif) filme donc la ruelle et son camion, pas une ruelle vide.
    # `sans_degats` : une prime de moitié en plus si le camion n'a pas une bosse.
    "objectifs": [
        {"type": "monter", "texte": "PRENDS LE CAMION DE POISSON DANS LA RUELLE",
         "vehicule": "camion", "ou": "ruelle:cantine:10"},

        # « Des missions plus longues » (22 sept. 2026) : la morue voyage sur de la glace — un détour aux
        # Érables, chez Ti-Paul, à l'autre bout de la ville (on descend du camion, on lui parle, on
        # remonte : `livrer` attend le même camion). Puis le sergent paie (pour une fois), et on rapporte
        # l'argent à Lulu. La prime sans bosse se décide à la livraison, et tient jusqu'à la fin.
        {"type": "parler", "texte": "ARRÊTE CHERCHER DE LA GLACE CHEZ TI-PAUL",
         "cible": "tipaul"},

        {"type": "livrer", "texte": "LIVRE LE POISSON AU CASSE-CROÛTE, SANS BOSSE",
         "lieu": "casse_croute", "rayon": 4, "sans_degats": True},

        {"type": "parler", "texte": "FAIS PAYER LE SERGENT, AU CASSE-CROÛTE",
         "cible": "bouchard"},

        {"type": "aller", "texte": "RAPPORTE L'ARGENT À LULU, À LA CANTINE",
         "lieu": "cantine", "rayon": 4}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Lulu, le poisson du vendredi : la cantinière qui
    # materne et qui taquine — l'urgence est drôle (un camion de morue), jamais grave. La fin
    # passe la main à Raymonde, avec un clin d'œil.
    "dialogue": {
        "appel": [
            _l("lulu", "Allô, mon grand, c'est Lulu! J'ai un camion de poisson sans chauffeur, pis c'est vendredi. Viens vite!",
               jeu="[excited] Allô, mon grand, c'est Lulu! J'ai un camion de poisson sans chauffeur… pis c'est vendredi. Viens vite!")
        ],
        "intro": [
            _l("lulu", "Le camion est dans une ruelle, plein de morue. Le chauffeur s'est pogné la main dans sa glacière.",
               jeu="[warmly] Le camion est dans une ruelle, plein de morue. [amused] Le chauffeur s'est pogné la main… dans sa glacière."),
            _l("lulu", "Livre-le au casse-croûte du Faubourg. Pis conduis doucement: le poisson, ça se bosse pas.",
               jeu="[firmly] Livre-le au casse-croûte du Faubourg. [teasing] Pis conduis doucement… le poisson, ça se bosse pas.")
        ],
        "pendant": [
            # Au combiné : elle est à la cantine, on est au volant.
            _p("lulu", "Oublie pas la glace chez Ti-Paul! Sans glace, ma morue va se sauver toute seule.", 1,
               jeu="[worried] Oublie pas la glace chez Ti-Paul! [teasing] Sans glace, ma morue va se sauver… toute seule."),
            _p("lulu", "Doucement dans les tournants! Le sergent veut son poisson frais, pas en purée.", 2,
               jeu="[worried] Doucement dans les tournants! [playfully] Le sergent veut son poisson frais… pas en purée."),
            _p("lulu", "Fais-le payer, le sergent! Pis compte les billets devant lui, hein.", 3,
               jeu="[firmly] Fais-le payer, le sergent! [teasing] Pis compte les billets devant lui, hein."),
            _p("lulu", "Rapporte-moi ça vite, mon grand. Pis mange en chemin, t'as l'air d'un fantôme.", 4,
               jeu="[warmly] Rapporte-moi ça vite, mon grand. [teasing] Pis mange en chemin… t'as l'air d'un fantôme.")
        ],
        "fin": [
            _l("lulu", "Pas une écaille de perdue! Le sergent va être content, pis moi, j'suis payée.",
               jeu="[relieved] Pas une écaille de perdue! [cheerful] Le sergent va être content, pis moi, j'suis payée."),
            _l("lulu", "Pis le sergent a payé? Ben coudonc. Y va pleuvoir des poissons.",
               jeu="[surprised] Pis le sergent a payé? [amused] Ben coudonc… Y va pleuvoir des poissons."),
            _l("lulu", "Passe voir Raymonde, à l'usine. Elle cherche quelqu'un qui conduit bien, pis qui pose pas de questions.",
               jeu="[knowingly] Passe voir Raymonde, à l'usine. Elle cherche quelqu'un qui conduit bien… pis qui pose pas de questions.")
        ],
        "echec": [
            _l("lulu", "Mon poisson… Ben tant pis, on va le faire en soupe. Reviens quand tu conduis mieux.",
               jeu="[disappointed] Mon poisson… Ben tant pis, on va le faire en soupe. [teasing] Reviens quand tu conduis mieux.")
        ],
        # Les poignées de main du détour : Ti-Paul (dehors, au dépanneur) et le sergent (dedans, au
        # casse-croûte) sont connus depuis m6 et m4 — ils ne se nomment pas.
        "accueil": [
            _a("tipaul", "Ta glace, l'ami! Dis à Lulu qu'a me doit deux sacs, pis un café.", 1,
               jeu="[cheerful] Ta glace, l'ami! [mischievously] Dis à Lulu qu'a me doit deux sacs… pis un café."),
            _a("bouchard", "Le jeune. Tiens, pour Lulu. Pis dis-lui que le pourboire, c'est ma protection.", 3,
               jeu="[gruffly] Le jeune. Tiens, pour Lulu. [deadpan] Pis dis-lui que le pourboire… c'est ma protection.")
        ]
    },

    # Intention (intro) : le joueur voit le camion pendant que Lulu le nomme (« dans une ruelle, plein
    # de morue »), et la caméra revient à la cantine pour la blague du chauffeur ; elle croise les bras,
    # elle donne l'ordre. ⚠️ Elle parle DEDANS : c'est la forme du défaut, SAUF que la coupe part
    # `ensemble` avec la première réplique au lieu de la retenir — la voix dure 9,3 s, la coupe 4 s, et
    # la seconde réplique la coupait en plein « pogné la main ». Le `dire` retient la scène jusqu'au bout
    # de sa voix. La coupe (240 images) revient juste avant « Le chauffeur » (4,1 s).
    # La fin reste celle du défaut : on est au casse-croûte et elle à sa cantine, une coupe chez elle.
    "scenes": {
        "intro": [
            { "type": "coupe", "vers": "ruelle:cantine:10", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True },
            { "type": "dire", "repliques": [1] },
            { "type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True },
            { "type": "dire", "repliques": [2] }
        ]
    }
}
