"""La mission p01 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "p01",
    "titre": "La lampe du phare",
    "donneur": "ovila",
    "prerequis": ["m6"],
    "recompense": 100,
    "donne": {"message": "OVILA TE CONNAÎT"},

    # ⚠️ `acheter` (M16) : un bâton solide à la quincaillerie (`boutique:artisan` vend
    # déjà "batte" — le mécanisme du gérant qui cale sa lampe avec ce qu'il trouve).
    "objectifs": [
        {"type": "acheter", "texte": "ACHÈTE UN BÂTON SOLIDE À LA QUINCAILLERIE",
         "article": "batte", "ou": "boutique:artisan"},

        # ⚠️ **Plus long** (Martin, 22 sept. 2026 : « des missions plus longues ») : un second
        # comptoir, à l'autre bout de la ville — l'extincteur ne se vend qu'à la Shop
        # (`magasins.COMPTOIRS["industrie"]`), le bâton à la quincaillerie. Et c'est la seule
        # arme que rien ne donne avant : `m2` donne déjà le bâton (`donne.arme`), si bien que
        # l'objectif 0 est fait d'avance pour qui a joué le tronc — celui-ci ne l'est jamais.
        {"type": "acheter", "texte": "ACHÈTE UN EXTINCTEUR À LA SHOP, AU CAS OÙ",
         "article": "extincteur", "ou": "boutique:industrie"},

        {"type": "tuer", "texte": "ÉLOIGNE LE SKATEUX QUI RÔDE AUTOUR DU PHARE",
         "groupe": "skateux", "n": 1, "ou": "donneur", "loin": 10},

        {"type": "aller", "texte": "RAPPORTE-LE AU PHARE, VITE",
         "lieu": "phare", "rayon": 6, "chrono_s": 180},

        # Arrivé au phare, le Skateux revient — avec ses amis (`loin` : ils naissent hors champ
        # et courent sur toi, à la porte d'Ovila).
        {"type": "tuer", "texte": "LE SKATEUX EST REVENU AVEC SES AMIS — DÉFENDS LE PHARE",
         "groupe": "skateux", "n": 3, "ou": "donneur", "loin": 12},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Ovila : formel, il vouvoie toujours, une
    # inquiétude posée plutôt que criée — un homme qui a passé sa vie à guetter la nuit.
    "dialogue": {
        "appel": [
            _l("ovila", "Ovila Saint-Onge, pour vous servir. Le mécanisme de ma lampe a besoin d'un bâton pour tenir, ce soir.",
               jeu="[gravely] Ovila Saint-Onge, pour vous servir. [worried] Le mécanisme de ma lampe a besoin d'un bâton pour tenir… ce soir.")
        ],
        "intro": [
            _l("ovila", "Un bâton solide, à la quincaillerie. Ma vue baisse, pis mes mains tremblent trop pour bricoler ça moi-même.",
               jeu="[gravely] Un bâton solide, à la quincaillerie. [somber] Ma vue baisse, pis mes mains tremblent trop pour bricoler ça moi-même."),
            _l("ovila", "Des Skateux traînent par icitte, la nuit. Faites attention en revenant.",
               jeu="[serious] Des Skateux traînent par icitte, la nuit. [gravely] Faites attention… en revenant.")
        ],
        "pendant": [
            _p("ovila", "Sans cette lampe, un bateau pourrait se briser sur les récifs. Dépêchez-vous.", 3,
               jeu="[gravely] Sans cette lampe, un bateau pourrait se briser sur les récifs. [firmly] Dépêchez-vous."),
            _p("ovila", "Et un extincteur, je vous prie. La dernière fois que j'ai bricolé la lampe, j'y ai laissé un sourcil.", 1,
               jeu="[serious] Et un extincteur, je vous prie. [somber] La dernière fois que j'ai bricolé la lampe… j'y ai laissé un sourcil."),
            _p("ovila", "Il est revenu avec ses amis. Je vous en prie, épargnez mes fenêtres.", 4,
               jeu="[worried] Il est revenu… avec ses amis. [gravely] Je vous en prie… épargnez mes fenêtres.")
        ],
        "fin": [
            _l("ovila", "La lampe tient. Vous m'avez rendu un fier service, ce soir.",
               jeu="[relieved] La lampe tient. [warmly] Vous m'avez rendu un fier service… ce soir."),
            _l("ovila", "Gardez l'extincteur. Avec moi, la lampe finit toujours par s'emporter.",
               jeu="[calm] Gardez l'extincteur. [wryly] Avec moi… la lampe finit toujours par s'emporter."),
            _l("ovila", "Je n'oublie pas un visage qui m'aide. Revenez me voir.",
               jeu="[tenderly] Je n'oublie pas un visage qui m'aide. [warmly] Revenez me voir.")
        ],
        "echec": [
            _l("ovila", "La lampe a flanché... J'espère qu'aucun bateau n'était sur l'eau, cette nuit.",
               jeu="[somber] La lampe a flanché… [worried] J'espère qu'aucun bateau n'était sur l'eau, cette nuit.")
        ]
    },

    # Intention (intro) : Ovila ne montre rien de précis — sa vue baisse, c'est tout
    # son propos. ⚠️ Le défaut (dedans) serait allé montrer `boutique:artisan` (le
    # comptoir de l'objectif) par une coupe ; rien ne garantit qu'une quincaillerie se
    # résout depuis le phare, à l'autre bout de la ville. On coupe chez lui à la place —
    # ce que le défaut ferait de toute façon si `ou` n'existait pas. Et la coupe part `ensemble` avec la
    # première réplique (forme de q02/m51) : sa voix dure 6,9 s, la coupe 3,2 s, et la seconde la coupait.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "chez:ovila", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
    },
}
