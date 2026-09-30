"""La mission l04 — voir app/missions/__init__.py pour le moteur.

Le scoop du maire (M16, arc C, 30 sept. 2026 — la « c02 » de la fiche). Norbert a donné les reçus (l03) ; il
manquait une preuve qu'on imprime. Elle dort dans le sac du neveu depuis e07 : le dossier volé à la villa. On le
porte à la rédaction du Clairon (la façade peinte, `boutique:clairon`), les hommes du maire arrivent trop tard pour
le reprendre et trop tôt pour s'en aller, et Louise a sa une : _Le maire dort à l'hôtel_.

⚠️ La fiche voulait le dossier « gardé » par un choix de e11 (le vendre au maire). e11 n'existe pas — le maire ne se
tient en ville qu'entre m97 et m98 — : l04 vient après e07, qui laisse le dossier au sac.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "l04",
    "titre": "Le scoop du maire",
    "donneur": "louise",
    "prerequis": ["l03", "e07"],
    "recompense": 800,
    "donne": {"manchette": "maire_hotel", "message": "LE MAIRE DORT À L'HÔTEL — ET TOUTE LA VILLE LE SAIT"},

    # ⚠️ La rédaction n'a pas de porte (la façade « LE CLAIRON » est peinte) : une `course` d'un point sur son enseigne
    # (`boutique:clairon`, que `Histoire.resoudre` trouve par le texte) — aucune porte ne devient lieu de mission. Les
    # hommes du maire sont des gardiens loués (`pieton: gardien`, comme ceux de Prévost en s10).
    "objectifs": [
        {"type": "course", "texte": "LE DOSSIER DU MAIRE À LA RÉDACTION DU CLAIRON",
         "points": ["boutique:clairon"], "rayon": 4},

        {"type": "tuer", "texte": "LES HOMMES DU MAIRE VEULENT LE DOSSIER",
         "groupe": "cravates", "pieton": "gardien", "n": 3, "loin": 10},

        {"type": "retourner", "texte": "LA PREUVE EST IMPRIMÉE : VA VOIR LOUISE"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "boutique:clairon", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Louise : la journaliste qui tient enfin l'histoire qu'on lui avait tuée ;
    # l'excitation, et une colère ancienne qui passe dessous.
    "dialogue": {
        "appel": [
            _l("louise", "Louise, au Clairon. Norbert m'a donné les reçus. Il me manque le dossier que t'as dans ton sac.",
               jeu="[excited] Louise, au Clairon. Norbert m'a donné les reçus. [knowingly] Il me manque le dossier que t'as dans ton sac.")
        ],
        "intro": [
            _l("louise", "Le maire m'a déjà tué une histoire, y a trois ans. Celle-là, il la tuera pas.",
               jeu="[bitterly] Le maire m'a déjà tué une histoire, y a trois ans. [firmly] Celle-là, il la tuera pas."),
            _l("louise", "Porte le dossier à la rédaction. Le typographe t'attend, les presses sont chaudes.",
               jeu="[excited] Porte le dossier à la rédaction. [confident] Le typographe t'attend, les presses sont chaudes."),
            _l("louise", "Le maire a des amis partout. S'ils arrivent, ils arrivent trop tard. Arrange-toi pour ça.",
               jeu="[serious] Le maire a des amis partout. [firmly] S'ils arrivent, ils arrivent trop tard. Arrange-toi pour ça.")
        ],
        "pendant": [
            _p("louise", "La rédaction, c'est la vieille façade avec l'enseigne du Clairon. La porte d'en arrière est ouverte.", 0,
               jeu="[matter-of-fact] La rédaction, c'est la vieille façade avec l'enseigne du Clairon. [quietly] La porte d'en arrière est ouverte."),
            _p("louise", "Les presses roulent! Pis les hommes du maire aussi. Tiens-les loin.", 1,
               jeu="[excited] Les presses roulent! [concerned] Pis les hommes du maire aussi. Tiens-les loin."),
            _p("louise", "Six mille copies. Viens chercher la tienne au kiosque, mon beau.", 2,
               jeu="[satisfied] Six mille copies. [teasing] Viens chercher la tienne au kiosque, mon beau.")
        ],
        "fin": [
            _l("louise", "« Le maire dort à l'hôtel. » Aux frais de la ville, depuis trois ans. Tout est là.",
               jeu="[excited] « Le maire dort à l'hôtel. » Aux frais de la ville, depuis trois ans. [satisfied] Tout est là."),
            _l("louise", "Ça, c'est ta part. Pis garde ton sac fermé : il va vouloir savoir d'où ça vient.",
               jeu="[warmly] Ça, c'est ta part. [serious] Pis garde ton sac fermé : il va vouloir savoir d'où ça vient.")
        ],
        "echec": [
            _l("louise", "Le dossier est reparti chez le maire. Trois ans d'attente pour rien.",
               jeu="[bitterly] Le dossier est reparti chez le maire. [disappointed] Trois ans d'attente pour rien.")
        ]
    }
}
