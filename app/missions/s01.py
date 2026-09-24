"""La mission s01 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "s01",
    "titre": "Gilles à la guérite",
    "donneur": "gilles",
    "prerequis": ["m6"],
    "recompense": 250,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"rabais": {"fourriere": 0.80}, "message": "LE RACHAT AU LOT, MOINS CHER"},

    # ⚠️ `zone:<slug>` (M16, résoudre() ligne 336) : une tuile marchable tirée dans
    # le territoire du gang — ici celui des Boulonneux (`pietons.py`, `gang:
    # "boulonneux"`). `poserLeChar` route la remorqueuse jusqu'à la rue la plus
    # proche de cette tuile, exactement comme un `porte:`.
    #
    # « Des missions plus longues » (Martin, 22 sept. 2026) : d'abord Ti-Paul, au bout
    # ouest des Érables — rien ne passe sans qu'il le sache (`parler`, sa poignée de
    # main dite) ; puis les Boulonneux reviennent chercher la remorqueuse et arrivent
    # de loin (`tuer`, `loin`) avant la route du lot.
    "objectifs": [
        {"type": "parler", "texte": "DEMANDE À TI-PAUL OÙ ELLE EST PASSÉE",
         "cible": "tipaul"},

        {"type": "monter", "texte": "REPRENDS LA REMORQUEUSE",
         "vehicule": "remorqueuse", "ou": "zone:boulonneux"},

        {"type": "tuer", "texte": "LES BOULONNEUX REVIENNENT LA CHERCHER",
         "groupe": "boulonneux", "n": 3, "ou": "zone:boulonneux", "loin": 10},

        {"type": "livrer", "texte": "RAMÈNE-LA À LA FOURRIÈRE",
         "lieu": "fourriere", "rayon": 4},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Gilles : las, proche de la retraite, mais
    # encore fier de son lot ; jamais pressé, sauf quand on touche à SA remorqueuse.
    "dialogue": {
        "appel": [
            _l("gilles", "C'est Gilles, de la fourrière. Un Boulonneux est parti avec ma remorqueuse. J'ai besoin d'un coup de main.",
               jeu="[gravely] C'est Gilles, de la fourrière. Un Boulonneux est parti avec ma remorqueuse. [matter-of-fact] J'ai besoin d'un coup de main.")
        ],
        "intro": [
            _l("gilles", "Ils l'ont garée dans leur coin, en zone des Boulonneux. Trente ans que je la conduis, cette machine-là.",
               jeu="[somber] Ils l'ont garée dans leur coin, en zone des Boulonneux. [tenderly] Trente ans que je la conduis, cette machine-là."),
            _l("gilles", "Ramène-la icitte, au lot. Je pars bientôt à la retraite, je veux pas la perdre avant.",
               jeu="[firmly] Ramène-la icitte, au lot. [quietly] Je pars bientôt à la retraite… je veux pas la perdre avant."),
            _l("gilles", "Passe voir Ti-Paul avant, au dépanneur. Rien passe dans cette ville-là sans qu'il le sache.",
               jeu="[matter-of-fact] Passe voir Ti-Paul avant, au dépanneur. [wryly] Rien passe dans cette ville-là sans qu'il le sache.")
        ],
        "pendant": [
            _p("gilles", "Fais attention en la sortant de là. Elle est vieille, mais elle est encore à moi.", 1,
               jeu="[gravely] Fais attention en la sortant de là. [tenderly] Elle est vieille, mais elle est encore à moi."),
            _p("gilles", "Ils reviennent la chercher. Tiens-leur tête, le jeune, trente ans, ça se laisse pas voler deux fois.", 2,
               jeu="[worried] Ils reviennent la chercher. [firmly] Tiens-leur tête, le jeune… trente ans, ça se laisse pas voler deux fois.")
        ],
        # Ti-Paul, devant son dépanneur : il se nomme (la première fois qu'on l'entend dans
        # cette mission), et il en sait toujours plus qu'on lui en demande.
        "accueil": [
            _a("tipaul", "Salut, l'ami, c'est Ti-Paul! Les gars de la remorqueuse ont pris douze caisses icitte. À crédit!", 0,
               jeu="[cheerful] Salut, l'ami, c'est Ti-Paul! [knowingly] Les gars de la remorqueuse ont pris douze caisses icitte… à crédit!")
        ],
        "fin": [
            _l("gilles", "Ma vieille remorqueuse. Pas une égratignure de plus.",
               jeu="[relieved] Ma vieille remorqueuse. [warmly] Pas une égratignure de plus."),
            _l("gilles", "Merci, le jeune. Reviens icitte, je te ferai un prix sur le rachat.",
               jeu="[satisfied] Merci, le jeune. [matter-of-fact] Reviens icitte, je te ferai un prix sur le rachat.")
        ],
        "echec": [
            _l("gilles", "Perdue, ma remorqueuse... Trente ans, pis ça finit de même.",
               jeu="[disappointed] Perdue, ma remorqueuse… [somber] Trente ans, pis ça finit de même.")
        ]
    }
}
