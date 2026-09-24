"""La mission f09 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "f09",
    "titre": "Marco veut sa part",
    "donneur": "marco",
    "prerequis": ["f06"],
    "recompense": 250,
    "donne": {"message": "MARCO A VU OÙ EST L'ARGENT"},

    # ⚠️ `proteger` (M16) : Marco te suit à pied (`e.suit`, le mécanisme du petit qui
    # colle à sa mère) jusqu'au kiosque ; `lieu`+`rayon` font avancer l'objectif comme
    # un `aller`, tant qu'il reste vivant. Deux Cravates tendent une embuscade en route.
    "objectifs": [
        {"type": "proteger", "texte": "ESCORTE MARCO JUSQU'AU KIOSQUE",
         "cible": "marco", "lieu": "kiosque", "rayon": 5},

        {"type": "tuer", "texte": "REPOUSSE LES DEUX CRAVATES",
         "groupe": "cravates", "n": 2, "ou": "donneur", "loin": 10},

        # ⚠️ Des missions plus longues (Martin, 22 sept. 2026) : la fin disait « j'ai vu où le
        # reste de l'argent dort » sans qu'on l'ait vu. Un troisième Cravate se pousse en char
        # vers leur cache — l'hôtel Bandini, à l'autre bout de la ville : l'argent y DORT. On le
        # file (`suivre`), Marco monte avec toi (`proteger` le garde collé toute la mission),
        # puis on le ramène au garage : la fin se dit devant lui (`fin_chez_le_donneur`).
        # `hotel` et `garage` sont déjà des lieux de mission : la ville ne bouge pas.
        {"type": "suivre", "texte": "SUIS LE TROISIÈME JUSQU'À LEUR CACHE",
         "vehicule": "auto", "loin": 10, "proche": 3, "lieu": "hotel"},

        {"type": "aller", "texte": "RAMÈNE MARCO AU GARAGE", "lieu": "garage", "rayon": 6}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Marco : la désinvolture de qui a peur et le
    # cache, comme f01 ; il hausse les épaules sur l'embuscade, baisse la voix quand il
    # flaire l'argent des autres, puis se rengorge à la fin — la part qu'il n'a jamais eue.
    "dialogue": {
        "appel": [
            _l("marco", "Cousin, c'est Marco. J'ai ma part à aller chercher au kiosque, pis j'aime pas marcher seul.",
               jeu="[casually] Cousin, c'est Marco. [wryly] J'ai ma part à aller chercher au kiosque… pis j'aime pas marcher seul.")
        ],
        "intro": [
            _l("marco", "Les Cravates ont pas digéré la dernière fois. Reste collé sur moi jusqu'au kiosque.",
               jeu="[casually] Les Cravates ont pas digéré la dernière fois. [firmly] Reste collé sur moi… jusqu'au kiosque."),
            _l("marco", "Si ça chauffe, tu t'en occupes. Moi, je marche vite pis je regarde pas en arrière.",
               jeu="[wryly] Si ça chauffe, tu t'en occupes. [nervously] Moi, je marche vite… pis je regarde pas en arrière.")
        ],
        "pendant": [
            _p("marco", "Deux gars en cravate! Je le savais! Occupe-toi d'eux, cousin!", 1,
               jeu="[worried] Deux gars en cravate! [excited] Je le savais! Occupe-toi d'eux, cousin!"),
            _p("marco", "Y en a un troisième qui se pousse en char. Prends un char, cousin, je veux voir où il va.", 2,
               jeu="[quietly] Y en a un troisième qui se pousse en char. [firmly] Prends un char, cousin… je veux voir où il va."),
            _p("marco", "L'argent dort à l'hôtel. Ça s'invente pas. Ramène-moi au garage, cousin.", 3,
               jeu="[wryly] L'argent dort à l'hôtel. [laughs] Ça s'invente pas. [casually] Ramène-moi au garage, cousin.")
        ],
        "fin": [
            _l("marco", "On est arrivés en un morceau. J'ai ma part, pis j'ai vu où le reste de l'argent dort.",
               jeu="[relieved] On est arrivés en un morceau. [impressed] J'ai ma part… pis j'ai vu où le reste de l'argent dort."),
            _l("marco", "Ça pourrait servir, un jour. Merci, cousin.",
               jeu="[knowingly] Ça pourrait servir, un jour. [warmly] Merci, cousin."),
            _l("marco", "Pis l'hôtel, ça reste entre nous deux, cousin.",
               jeu="[quietly] Pis l'hôtel… ça reste entre nous deux, cousin.")
        ],
        "echec": [
            _l("marco", "Ils m'ont eu presque... T'étais où, cousin?",
               jeu="[coldly] Ils m'ont eu presque… [annoyed] T'étais où, cousin?")
        ]
    }
}
