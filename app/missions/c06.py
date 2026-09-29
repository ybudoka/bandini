"""La mission c06 — voir app/missions/__init__.py pour le moteur.

Le premier élève (docs/jalons/l-ecole-rivale.md, vague 2). Kenny, le meilleur élève du vieux maître — le grand écart
à huit ans —, est devenu le caïd des Mantes, et ce soir il va s'acheter un fusil chez Gus. On le file dans son char de
frime jusqu'à l'armurerie ; quand il descend, on règle ça comme à l'école : un duel, à mains nues. Le lendemain, Kenny
balaie le plancher de l'école.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "c06",
    "titre": "Le chemin de chez Gus",
    "donneur": "maitre",
    "prerequis": ["c05"],
    "recompense": 700,
    "donne": {"message": "KENNY EST RETOURNÉ À L'ÉCOLE"},

    # ⚠️ Le maître est DEDANS (`point:maitre`) : le char de Kenny naît à bonne distance de la porte de l'école quand on
    # sort, et attend qu'on soit au volant (`suivre`, comme le comptable de c03). Son `lieu`, l'armurerie, est DÉJÀ un
    # lieu de mission (Gus) — un lieu neuf élargirait son devant, et la ville glisserait. Arrivé, Kenny descend et
    # attend à la porte de chez Gus : le chef des Mantes (`chef`), à mains nues (`arme: ""`), plus solide qu'un autre.
    "objectifs": [
        {"type": "suivre", "texte": "SUIS LE CHAR DE KENNY SANS TE FAIRE VOIR",
         "vehicule": "sport", "loin": 10, "proche": 3, "lieu": "armurerie"},

        {"type": "tuer", "texte": "UN DUEL À MAINS NUES AVEC KENNY, DEVANT CHEZ GUS",
         "groupe": "mantes", "n": 1, "chef": True, "ou": "porte:armurerie", "arme": "", "vie": 160},
    ],

    # Le jeu de chaque réplique (`jeu=`) — le maître : l'orgueil du vieux prof qui parle de son meilleur élève, puis
    # la peine, franche, quand il dit « un fusil » ; au duel, la politesse du salut dite comme une règle sacrée et
    # drôle à la fois ; à la fin, la fatigue joyeuse d'un homme qui a gagné une manche et qui en voit dix autres. Il se
    # nomme à l'appel, une fois : « Sifu Tam ».
    "dialogue": {
        "appel": [
            _l("maitre", "Sifu Tam, petit scarabée. Oui, j'ai un cellulaire : ma fille me l'a acheté en Floride.",
               jeu="[cheerful] Sifu Tam, petit scarabée. [amused] Oui, j'ai un cellulaire : ma fille me l'a acheté en Floride.")
        ],
        "intro": [
            _l("maitre", "Kenny, mon meilleur élève. À huit ans, il faisait le grand écart. À vingt-deux, il fait le caïd.",
               jeu="[warmly] Kenny, mon meilleur élève. [wryly] À huit ans, il faisait le grand écart… À vingt-deux, il fait le caïd."),
            _l("maitre", "À soir, il s'en va chez Gus s'acheter un fusil. Un élève de la Mante, avec un fusil!",
               jeu="[somber] À soir, il s'en va chez Gus s'acheter un fusil. [angry] Un élève de la Mante, avec un fusil!"),
            _l("maitre", "Suis-le sans klaxonner. Quand il descend, on règle ça comme à l'école : à mains nues.",
               jeu="[firmly] Suis-le sans klaxonner. [serious] Quand il descend, on règle ça comme à l'école : à mains nues.")
        ],
        "pendant": [
            _p("maitre", "Il conduit comme dans les films, en regardant la caméra. Reste loin, il te verra pas.", 0,
               jeu="[amused] Il conduit comme dans les films, en regardant la caméra. [knowingly] Reste loin… il te verra pas."),
            _p("maitre", "Salue-le avant, le poing dans la paume. Après, tu le couches. C'est la politesse.", 1,
               jeu="[serious] Salue-le avant, le poing dans la paume. [firmly] Après, tu le couches. [playfully] C'est la politesse.")
        ],
        "fin": [
            _l("maitre", "Kenny balaie le plancher de l'école depuis une heure. Il chiale, mais il balaie.",
               jeu="[satisfied] Kenny balaie le plancher de l'école depuis une heure. [amused] Il chiale… mais il balaie."),
            _l("maitre", "Un de rendu. Il en reste une gang, pis moi j'ai soixante-quatorze ans.",
               jeu="[sighs] Un de rendu. [wryly] Il en reste une gang… pis moi j'ai soixante-quatorze ans."),
            _l("maitre", "Reviens me voir demain. On a un mannequin de bois à aller chercher.",
               jeu="[warmly] Reviens me voir demain. [mysteriously] On a un mannequin de bois à aller chercher.")
        ],
        "echec": [
            _l("maitre", "Kenny a son fusil, astheure. En Floride, mes problèmes, c'étaient les alligators.",
               jeu="[somber] Kenny a son fusil, astheure. [sighs] En Floride, mes problèmes, c'étaient les alligators.")
        ]
    },

    # Intention (intro) : dans sa salle, le maître montre le mur des photos — l'orgueil — puis la caméra va voir la
    # porte de chez Gus pendant qu'il dit « un fusil », et revient sur la règle : à mains nues. ⚠️ La coupe en
    # `ensemble`, PUIS la réplique. Intention (fin) : à sa porte, Kenny rendu, et la fatigue joyeuse.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "joueur", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:armurerie", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:maitre", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },
}
