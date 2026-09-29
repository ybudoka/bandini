"""La mission p10 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "p10",
    "titre": "Le saut de La Pointe",
    "donneur": "zed",
    "prerequis": ["p04"],
    "recompense": 250,
    "donne": {"message": "LES SKATEUX PARLENT DE TON SAUT"},

    # La moto de Zed dort devant le phare (`monter`) — une motoneige l'hiver, la saison le veut (« pas de moto l'hiver ») :
    # les répliques disent « ma machine », qui va aux deux ; la rampe est dans le stationnement des Skateux (`sauter`, le
    # vol compté comme le Grand Saut — `ou` ne sert qu'au GPS) : 80 px, le double du selfie de Xavier (e12).
    "objectifs": [
        {"type": "monter", "texte": "MONTE SUR LA MACHINE DE ZED", "vehicule": "moto", "ou": "porte:phare"},

        {"type": "sauter", "texte": "SAUTE LA RAMPE DES SKATEUX — 80 PX DE VOL",
         "ou": "rampe:pointe", "vol_px": 80},

        {"type": "retourner", "texte": "RAMÈNE SA MACHINE À ZED"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Zed : il a perdu la course, il veut gagner le saut. Il rit moins, il
    # regarde plus ; à la fin, il rit de nouveau — de lui-même.
    "dialogue": {
        "appel": [
            _l("zed", "Yo, c'est Zed. T'as battu mon temps, correct. Mais sauter, man, ça s'apprend pas en courant.",
               jeu="[teasing] Yo, c'est Zed. [amused] T'as battu mon temps, correct. [mischievously] Mais sauter, man… ça s'apprend pas en courant.")
        ],
        "intro": [
            _l("zed", "Ma machine est devant le phare. La rampe est au stationnement, tu la connais.",
               jeu="[casually] Ma machine est devant le phare. [confident] La rampe est au stationnement, tu la connais."),
            _l("zed", "Quatre-vingts pixels de vol, man. Moins que ça, c'est un trottoir.",
               jeu="[smugly] Quatre-vingts pixels de vol, man. [laughs] Moins que ça, c'est un trottoir.")
        ],
        "pendant": [
            _p("zed", "Prends ton élan. Le plus loin possible, pis lâche rien.", 1,
               jeu="[excited] Prends ton élan. [shouting] Le plus loin possible, pis lâche rien!"),
            _p("zed", "Malade! Ramène-moi ma machine avant que tu la brises, man.", 2,
               jeu="[impressed] Malade! [laughs] Ramène-moi ma machine avant que tu la brises, man.")
        ],
        "fin": [
            _l("zed", "Quatre-vingts pixels. Les gars l'ont filmé, t'es sur toutes les cassettes.",
               jeu="[impressed] Quatre-vingts pixels. [amused] Les gars l'ont filmé… t'es sur toutes les cassettes."),
            _l("zed", "La Chef veut me voir, paraît. Si tu y vas, je viens.",
               jeu="[nervously] La Chef veut me voir, paraît. [warmly] Si tu y vas… je viens.")
        ],
        "echec": [
            _l("zed", "Ma machine! Man, t'es meilleur à pied.",
               jeu="[annoyed] Ma machine! [laughs] Man, t'es meilleur à pied.")
        ]
    }
}
