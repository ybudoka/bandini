"""La mission p09 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "p09",
    "titre": "Le phare s'éteint",
    "donneur": "ovila",
    "prerequis": ["p05"],
    "recompense": 300,
    "donne": {"manchette": "phare_a_tenu", "message": "LE PHARE A TENU"},

    # Des Skateux ont grimpé au phare et coupé la lampe ; un bateau approche. Ils sont AUTOUR du phare (pas `loin` :
    # ils courraient sur le joueur où qu'il soit, et le banc les a vus naître à 322 tuiles du phare) ; une minute et
    # demie pour les chasser (`chrono_s`), puis on monte rallumer avec Ovila (`parler`, il est dedans).
    "objectifs": [
        {"type": "tuer", "texte": "DES SKATEUX ONT ÉTEINT LE PHARE — CHASSE-LES, VITE",
         "groupe": "skateux", "n": 3, "ou": "phare", "chrono_s": 90},

        {"type": "parler", "texte": "MONTE RALLUMER LA LAMPE AVEC OVILA",
         "cible": "ovila"},
    ],

    # ⚠️ L'INTRO EST ÉCRITE (la recette de q11) : Ovila est DEDANS, et sous la coupe du défaut sa première réplique
    # était coupée par la seconde (le juge des voix coupées, une fois les mp3 générés). La coupe en `ensemble`,
    # puis la voix.
    "scenes": {
        "intro": [
            {"type": "coupe", "vers": "porte:phare", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Ovila : pour une fois, l'urgence. Il ne crie pas — il n'a jamais crié —
    # mais il presse, et sa voix tremble sur « le bateau ». À la poignée de main, le soulagement d'un vieil homme.
    "dialogue": {
        "appel": [
            _l("ovila", "Bonsoir. Ici Ovila, au phare. La lampe est éteinte, et il y a un bateau dans la brume.",
               jeu="[worried] Bonsoir. Ici Ovila, au phare. [gravely] La lampe est éteinte… et il y a un bateau dans la brume.")
        ],
        "intro": [
            _l("ovila", "Des Skateux sont montés à la lampe. Ils ont tout coupé, pour rire.",
               jeu="[somber] Des Skateux sont montés à la lampe. [bitterly] Ils ont tout coupé… pour rire."),
            _l("ovila", "Ce bateau-là ne voit pas les récifs sans nous. Vous avez une minute et demie, peut-être moins.",
               jeu="[worried] Ce bateau-là ne voit pas les récifs sans nous. [firmly] Vous avez une minute et demie… peut-être moins.")
        ],
        "pendant": [
            _p("ovila", "Ils sont encore autour du phare. Je vous en prie, dépêchez-vous.", 0,
               jeu="[worried] Ils sont encore autour du phare. [gravely] Je vous en prie… dépêchez-vous.")
        ],
        "accueil": [
            _a("ovila", "Tournez la manette, là. La lampe revient. Le bateau tourne.", 1,
               jeu="[quietly] Tournez la manette, là. [relieved] La lampe revient… Le bateau tourne.")
        ],
        "fin": [
            _l("ovila", "Il est passé. Il ne saura jamais qu'il a failli ne pas passer.",
               jeu="[relieved] Il est passé. [softly] Il ne saura jamais… qu'il a failli ne pas passer."),
            _l("ovila", "Demain, le Clairon dira que le phare a tenu. Il aura raison, grâce à vous.",
               jeu="[warmly] Demain, le Clairon dira que le phare a tenu. [tenderly] Il aura raison… grâce à vous.")
        ],
        "echec": [
            _l("ovila", "Trop tard. J'entends la coque sur les roches. Dieu le garde.",
               jeu="[somber] Trop tard. [gravely] J'entends la coque sur les roches… Dieu le garde.")
        ]
    }
}
