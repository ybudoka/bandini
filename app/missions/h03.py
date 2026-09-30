"""La mission h03 — voir app/missions/__init__.py pour le moteur.

Le docteur a une dette (M16, arc H, 30 sept. 2026). Le Dr Lachance ne dort jamais : il joue aux cartes, la nuit,
à la table que Sal Ferraro tient au terminus — et il perd. Deux mille piasses. Il va payer la moitié ce soir, et il
ne veut pas marcher seul avec l'argent dans la poche de son sarrau. On l'escorte au terminus ; deux Cravates sans
job depuis m5 ont entendu parler de l'enveloppe ; il paie Sal, et il nous attend à la porte : son quart commence.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "h03",
    "titre": "Le docteur a une dette",
    "donneur": "lachance",
    "prerequis": ["h02", "d01"],
    "recompense": 250,
    "donne": {"message": "LA MOITIÉ DE LA DETTE DU DOCTEUR EST PAYÉE"},

    # ⚠️ Lachance est DEDANS (`point:lachance`) : `proteger` le pose à la porte de l'hôpital, et il nous suit toute
    # la mission (`majProtege`), jusqu'au retour. Les deux Cravates arrivent de loin (`loin`), à l'étape 1 : jamais
    # là où la fin se joue (l'hôpital). Pas de second `proteger` pour le retour : il reposerait « chez lui » à
    # l'endroit où il est. ⚠️ Et on finit DEVANT LUI (`retourner` : il attend à la porte du terminus, l'escorte
    # est `donneur(lachance)`) — un `aller` à l'hôpital faisait dire sa fin en personne (il nous suit) quand la scène
    # par défaut la croyait au combiné (`fin_chez_le_donneur` ne connaît que les portes).
    "objectifs": [
        {"type": "proteger", "texte": "MÈNE LE DOCTEUR AU TERMINUS : IL A L'ARGENT",
         "cible": "lachance", "lieu": "terminus", "rayon": 5},

        {"type": "tuer", "texte": "DEUX CRAVATES VEULENT L'ENVELOPPE : COUCHE-LES",
         "groupe": "cravates", "n": 2, "loin": 10},

        {"type": "parler", "texte": "LE DOCTEUR PAIE : VA VOIR SAL, DEDANS", "cible": "sal"},

        {"type": "retourner", "texte": "LE DOCTEUR T'ATTEND DEVANT LE TERMINUS"},
    ],

    # Intention (intro) : Lachance dans son bureau, gêné pour la première fois — un geste, sa première réplique qui
    # tient la scène ; puis la coupe vers le terminus (l'intro jouée DEDANS doit aller voir la ville), sous la
    # deuxième. La fin : il vient à nous sur le trottoir du terminus, montre l'hôpital, et retourne au travail.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "coupe", "vers": "porte:terminus", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "marcher", "acteur": "donneur", "vers": "joueur", "pres": 22, "duree": 50},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "porte:hopital", "duree": 70,
             "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Lachance : pour la première fois, le médecin est le patient. Il garde son
    # vocabulaire de salle d'urgence pour ne pas avoir à dire « j'ai honte » ; la voix reste calme, la phrase
    # s'arrête plus tôt. Sal, à la poignée de main : doux, content, et jamais un chiffre rond.
    "dialogue": {
        "appel": [
            _l("lachance", "Lachance, de l'hôpital. C'est personnel, cette fois. Passe à mon bureau, discrètement.",
               jeu="[serious] Lachance, de l'hôpital. [firmly] C'est personnel, cette fois. Passe à mon bureau, discrètement.")
        ],
        "intro": [
            _l("lachance", "Je joue aux cartes la nuit, chez Sal. Mauvais diagnostic : deux mille piasses de retard.",
               jeu="[quietly] Je joue aux cartes la nuit, chez Sal. [deadpan] Mauvais diagnostic : deux mille piasses de retard."),
            _l("lachance", "J'apporte la moitié ce soir. Mille piasses dans un sarrau, ça se voit de loin.",
               jeu="[matter-of-fact] J'apporte la moitié ce soir. [concerned] Mille piasses dans un sarrau… ça se voit de loin."),
            _l("lachance", "Marche avec moi jusqu'au terminus. Pis pas un mot à Ginette.",
               jeu="[firmly] Marche avec moi jusqu'au terminus. [quietly] Pis pas un mot à Ginette.")
        ],
        "pendant": [
            _p("lachance", "Pas trop vite. Un médecin qui court, ça inquiète le monde.", 0,
               jeu="[calm] Pas trop vite. [wryly] Un médecin qui court, ça inquiète le monde."),
            _p("lachance", "Ces deux-là, je les ai recousus le mois passé. Ils ont la mémoire courte.", 1,
               jeu="[concerned] Ces deux-là, je les ai recousus le mois passé. [bitterly] Ils ont la mémoire courte."),
            _p("lachance", "Je t'attends dehors. Je n'aime pas l'odeur de la lotion à barbe de Sal.", 2,
               jeu="[quietly] Je t'attends dehors. [wryly] Je n'aime pas l'odeur de la lotion à barbe de Sal."),
            _p("lachance", "Mon quart commence dans dix minutes. Le poker, lui, attendra.", 3,
               jeu="[matter-of-fact] Mon quart commence dans dix minutes. [somber] Le poker, lui, attendra.")
        ],
        "accueil": [
            _a("sal", "Son garde du corps? Neuf cent quatre-vingt-quinze, pis cinq de pourboire. Sa table est fermée.", 2,
               jeu="[amused] Son garde du corps? [satisfied] Neuf cent quatre-vingt-quinze, pis cinq de pourboire. [softly] Sa table est fermée.")
        ],
        "fin": [
            _l("lachance", "La moitié de payée. Le reste, je trouverai bien comment.",
               jeu="[relieved] La moitié de payée. [quietly] Le reste… je trouverai bien comment."),
            _l("lachance", "Tiens. Pour ton temps, pis pour ton silence.",
               jeu="[matter-of-fact] Tiens. [firmly] Pour ton temps, pis pour ton silence."),
            _l("lachance", "Si Ginette demande, j'étais en consultation. Ce n'est même pas un mensonge.",
               jeu="[deadpan] Si Ginette demande, j'étais en consultation. [wryly] Ce n'est même pas un mensonge.")
        ],
        "echec": [
            _l("lachance", "L'enveloppe est partie, et moi avec presque. Je dirai à Sal qu'il attende.",
               jeu="[somber] L'enveloppe est partie, et moi avec presque. [quietly] Je dirai à Sal qu'il attende.")
        ]
    }
}
