"""La mission q05 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "q05",
    # ⚠️ « Mireille veut sortir » dans la fiche M16 : le slug `mireille` est Mireille Dion, du DOJO DION
    # (29 sept. 2026). La fille de la Brume s'appelle Cindy.
    "titre": "Cindy veut sortir",
    "donneur": "cindy",
    "prerequis": ["q04"],
    "recompense": 100,
    "donne": {"message": "CINDY DORT DANS UN VRAI LIT, À L'HÔTEL"},

    # ⚠️ Le patron de p14 (`proteger`, puis `tuer` `ou: donneur`) : Cindy ATTEND qu'on vienne la chercher
    # devant la cantine, nous suit à pied — ou monte, si on s'arrête en char près d'elle — jusqu'à l'hôtel ;
    # arrivée, les deux gars du Beau Denis arrivent sur NOUS (`loin`), là où elle est, pas à la cantine qu'on
    # a quittée. Morte ou couchée, c'est raté (`protege_mort`). Denis lui-même ne se montre pas : c'est q06.
    "objectifs": [
        {"type": "proteger", "texte": "ESCORTE CINDY JUSQU'À L'HÔTEL BANDINI",
         "cible": "cindy", "lieu": "hotel", "rayon": 5},

        {"type": "tuer", "texte": "LES GARS DU BEAU DENIS — COUCHE-LES",
         "groupe": "morues", "n": 2, "ou": "donneur", "loin": 10},
    ],

    # La fin se dit DEVANT elle : elle vient à nous, sur le trottoir de l'hôtel (la règle « on n'entend jamais
    # quelqu'un qui n'est pas là »), puis elle regarde la porte qu'elle va passer.
    "scenes": {
        "fin": [
            {"type": "marcher", "acteur": "donneur", "vers": "joueur", "pres": 22, "duree": 50},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "porte:hotel", "duree": 60,
             "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Cindy : elle blague pour ne pas avoir peur, et la peur passe quand
    # même. Elle rit trop fort à l'appel, se tait sur le trajet, et à l'hôtel elle ne sait plus quoi dire :
    # « merci » ne sort pas, alors elle parle du lit.
    "dialogue": {
        "appel": [
            _l("cindy", "C'est Cindy, la fille devant la cantine. Josée dit que t'es correct. J'ai besoin de toi, ce soir.",
               jeu="[nervously] C'est Cindy, la fille devant la cantine. [quietly] Josée dit que t'es correct… J'ai besoin de toi, ce soir.")
        ],
        "intro": [
            _l("cindy", "Norbert, à l'hôtel, cherche une fille pour la réception. Une vraie job, avec une paye pis un lit.",
               jeu="[warmly] Norbert, à l'hôtel, cherche une fille pour la réception. [softly] Une vraie job… avec une paye pis un lit."),
            _l("cindy", "Denis le sait. Si je marche jusque-là toute seule, j'arrive pas.",
               jeu="[worried] Denis le sait. [quietly] Si je marche jusque-là toute seule… j'arrive pas."),
            _l("cindy", "Marche à côté de moi. Juste ça. Je m'occupe de pas pleurer.",
               jeu="[nervously] Marche à côté de moi. Juste ça. [wryly] Je m'occupe de pas pleurer.")
        ],
        "pendant": [
            _p("cindy", "Pas trop vite. Mes talons sont faits pour attendre, pas pour marcher.", 0,
               jeu="[wryly] Pas trop vite. [nervously] Mes talons sont faits pour attendre… pas pour marcher."),
            _p("cindy", "C'est ses gars! Denis les a envoyés, je te l'avais dit!", 1,
               jeu="[shouting] C'est ses gars! [worried] Denis les a envoyés, je te l'avais dit!")
        ],
        "fin": [
            _l("cindy", "On est rendus. Je pensais jamais voir cette porte-là de l'autre bord.",
               jeu="[relieved] On est rendus. [softly] Je pensais jamais voir cette porte-là… de l'autre bord."),
            _l("cindy", "Norbert m'attend à huit heures. Il a dit « mademoiselle ». Personne m'a jamais dit ça.",
               jeu="[surprised] Norbert m'attend à huit heures. [tenderly] Il a dit « mademoiselle »… Personne m'a jamais dit ça."),
            _l("cindy", "Denis va être en maudit. Dis-le à Josée avant qu'il le dise, lui.",
               jeu="[worried] Denis va être en maudit. [firmly] Dis-le à Josée… avant qu'il le dise, lui.")
        ],
        "echec": [
            _l("cindy", "C'est correct. Je retourne devant la cantine. J'ai l'habitude.",
               jeu="[sighs] C'est correct. [bitterly] Je retourne devant la cantine… J'ai l'habitude.")
        ]
    }
}
