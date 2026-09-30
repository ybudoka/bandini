"""La mission l05 — voir app/missions/__init__.py pour le moteur.

Le Clairon brûle (M16, arc C, 30 sept. 2026 — la « c05 » de la fiche). Le lendemain du scoop (l04), le maire
répond comme il sait : un bidon d'essence contre la façade de la rédaction. Louise appelle du trottoir d'en face.
Un extincteur (elle en a un dans son char, « pour les cigarettes du typographe »), le feu à éteindre avant qu'il
prenne l'imprimerie, les trois incendiaires qui regardent de trop près, et Louise au kiosque.

⚠️ La fiche disait « survivre 120 s à l'intérieur » : un objectif ne se joue pas dedans (`majObjectif` dort dans
une pièce) et la rédaction n'a pas de porte. Le feu (`eteindre`) prend sur la façade la plus proche de l'enseigne
(`Incendies.allumerPourMission`, sans dé) — la ville ne change pas.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "l05",
    "titre": "Le Clairon brûle",
    "donneur": "louise",
    "prerequis": ["l04"],
    "recompense": 400,
    "donne": {"message": "LE CLAIRON SORT DEMAIN, COMME TOUS LES JOURS"},

    "objectifs": [
        {"type": "eteindre", "texte": "LE CLAIRON BRÛLE : ÉTEINS LA FAÇADE",
         "ou": "boutique:clairon", "remet": "extincteur", "chrono_s": 90},

        {"type": "tuer", "texte": "LES INCENDIAIRES REGARDENT : COUCHE-LES",
         "groupe": "cravates", "pieton": "gardien", "n": 3, "loin": 10},

        {"type": "retourner", "texte": "RASSURE LOUISE, AU KIOSQUE"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 60, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "boutique:clairon", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Louise : pour la première fois, elle a peur, et elle le dit vite pour ne
    # pas avoir le temps de pleurer ; la une revient dès que le feu tombe.
    "dialogue": {
        "appel": [
            _l("louise", "C'est Louise! Le Clairon brûle! Quelqu'un a vidé un bidon sur la façade!",
               jeu="[shouting] C'est Louise! [worried] Le Clairon brûle! Quelqu'un a vidé un bidon sur la façade!")
        ],
        "intro": [
            _l("louise", "Tiens, l'extincteur de mon char. Il servait pour les cigarettes du typographe.",
               jeu="[nervously] Tiens, l'extincteur de mon char. [wryly] Il servait pour les cigarettes du typographe."),
            _l("louise", "Si ça prend l'imprimerie, y aura plus de Clairon. Cent douze ans, pis c'est fini.",
               jeu="[worried] Si ça prend l'imprimerie, y aura plus de Clairon. [somber] Cent douze ans, pis c'est fini."),
            _l("louise", "Pis ceux qui ont fait ça sont encore dans la rue, à regarder. Ils veulent voir.",
               jeu="[angry] Pis ceux qui ont fait ça sont encore dans la rue, à regarder. [coldly] Ils veulent voir.")
        ],
        "pendant": [
            _p("louise", "Vise le bas des flammes! Le bas!", 0,
               jeu="[shouting] Vise le bas des flammes! [nervously] Le bas!"),
            _p("louise", "C'est éteint. Les trois de l'autre côté, ce sont eux. Ils rient.", 1,
               jeu="[relieved] C'est éteint. [angry] Les trois de l'autre côté, ce sont eux. Ils rient."),
            _p("louise", "Viens au kiosque. J'ai besoin d'un café, pis d'un titre.", 2,
               jeu="[softly] Viens au kiosque. [wryly] J'ai besoin d'un café, pis d'un titre.")
        ],
        "fin": [
            _l("louise", "L'imprimerie a rien. La façade est noire, mais les presses tournent.",
               jeu="[relieved] L'imprimerie a rien. [calm] La façade est noire, mais les presses tournent."),
            _l("louise", "Demain, on sort. Pis sur la une, y aura une photo de la façade. Qu'il la regarde.",
               jeu="[confident] Demain, on sort. [coldly] Pis sur la une, y aura une photo de la façade. Qu'il la regarde.")
        ],
        "echec": [
            _l("louise", "C'est fini. Cent douze ans de Clairon, en fumée.",
               jeu="[somber] C'est fini. [quietly] Cent douze ans de Clairon, en fumée.")
        ]
    }
}
