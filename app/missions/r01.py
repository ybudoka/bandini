"""La mission r01 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "r01",
    "titre": "La nouvelle inspectrice",
    "donneur": "bouchard",
    "prerequis": ["m6"],
    "recompense": 300,
    "echec": ["mort", "arrete", "etoile"],
    "donne": {"message": "LE CARNET, EN LIEU SÛR"},

    # ⚠️ Un fuyard à pattes plutôt qu'un objet posé dedans — `ramasser`/`cible:
    # "fuyard"` (m2/m50/m97, jamais un objet statique : `majObjectif` ne connaît
    # que le fuyard qui tombe, ou une `caisse` posée par un fuyard tombé). `sans_etoile`
    # (M16, 2e preuve) sur le rattrapage : une étoile là, et c'est un autre flic qui te
    # voit fouiller le poste. Bouchard est DEDANS (`point:sergent`) : pas de
    # `retourner`, sa fin se dit au casse-croûte comme f06.
    "objectifs": [
        {"type": "aller", "texte": "VA AU POSTE, DE NUIT",
         "lieu": "poste", "rayon": 6, "nuit": True},

        {"type": "ramasser", "texte": "RATTRAPE-LE AVANT QU'IL DISPARAISSE",
         "cible": "fuyard", "vehicule": "auto", "sans_etoile": True},

        # « Des missions plus longues » (Martin, 22 sept. 2026) : l'inspectrice t'a vu
        # partir (`semer`, 1★), puis le carnet va dormir dans le coffre de l'Hôtel
        # Bandini — au bout sud-ouest, loin du poste — sans une étoile en chemin.
        {"type": "semer", "texte": "ROY T'A VU PARTIR, SÈME-LA", "etoiles": 1},

        {"type": "aller", "texte": "CACHE LE CARNET À L'HÔTEL, SANS ÉTOILE",
         "lieu": "hotel", "rayon": 4, "sans_etoile": True},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Bouchard : bourru, jamais un mot de trop,
    # une satisfaction sèche — comme f06, il n'a pas besoin de sourire pour qu'on
    # sache que l'affaire est réglée.
    "dialogue": {
        "appel": [
            _l("bouchard", "Bouchard. Une nouvelle inspectrice, Roy, fouille dans mes affaires. Un jeune agent véreux lui vend mon carnet.",
               jeu="[gruffly] Bouchard. Une nouvelle inspectrice, Roy, fouille dans mes affaires. [gravely] Un jeune agent véreux lui vend mon carnet.")
        ],
        "intro": [
            _l("bouchard", "Il sort du poste à la noirceur, mon carnet dans sa mallette. Rattrape-le, discret.",
               jeu="[firmly] Il sort du poste à la noirceur, mon carnet dans sa mallette. [gravely] Rattrape-le, discret."),
            _l("bouchard", "Pas d'étoile là-dedans. Un gars qui court après un char au poste, ça pose des questions.",
               jeu="[serious] Pas d'étoile là-dedans. [matter-of-fact] Un gars qui court après un char au poste… ça pose des questions."),
            _l("bouchard", "Si ça tourne mal, je te connais pas. C'est comme ça qu'on devient vieux dans la police.",
               jeu="[deadpan] Si ça tourne mal, je te connais pas. [knowingly] C'est comme ça qu'on devient vieux dans la police.")
        ],
        "pendant": [
            _p("bouchard", "Il roule vers le pont. Reste collé, mais reste invisible.", 1,
               jeu="[gravely] Il roule vers le pont. [firmly] Reste collé, mais reste invisible."),
            _p("bouchard", "Roy t'a vu partir. Sème-la, le jeune, une inspectrice ça lâche pas un os.", 2,
               jeu="[nervously] Roy t'a vu partir. [firmly] Sème-la, le jeune… une inspectrice ça lâche pas un os."),
            _p("bouchard", "Pas au poste, pas chez nous : le coffre de l'Hôtel Bandini. Personne fouille chez un mort.", 3,
               jeu="[gravely] Pas au poste, pas chez nous… le coffre de l'Hôtel Bandini. [deadpan] Personne fouille chez un mort.")
        ],
        "fin": [
            _l("bouchard", "Mon carnet. Vingt ans de petites affaires, dedans. Ça reste entre nous deux.",
               jeu="[relieved] Mon carnet. [gravely] Vingt ans de petites affaires, dedans. Ça reste entre nous deux."),
            _l("bouchard", "Roy va devoir fouiller ailleurs. T'as fait ça proprement.",
               jeu="[satisfied] Roy va devoir fouiller ailleurs. [gruffly] T'as fait ça proprement.")
        ],
        "echec": [
            _l("bouchard", "Vu, hein? Astheure Roy va savoir que je fais nettoyer mes traces. Sacrament.",
               jeu="[annoyed] Vu, hein? [gravely] Astheure Roy va savoir que je fais nettoyer mes traces. Sacrament.")
        ]
    },

    # Intention (intro) : celle du défaut (dedans) — une coupe sur `porte:poste`, il croise les bras, il
    # finit. ⚠️ SAUF que la coupe part `ensemble` avec la première réplique au lieu de la retenir (forme
    # de q02/m51) : la voix dure 6,0 s, la coupe du défaut 3,2 s, et la seconde réplique la coupait.
    # Le `dire` retient la scène jusqu'au bout de sa voix.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "porte:poste", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
    },
}
