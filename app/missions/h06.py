"""La mission h06 — voir app/missions/__init__.py pour le moteur.

Les ordonnances (M16, arc H, 30 sept. 2026). Le reste de la dette du docteur (h03), Sal le veut en pilules : trois
ordonnances de calmants, signées Lachance, pour des patients qui n'existent pas. On les fait remplir à trois
comptoirs de trois quartiers — la pharmacie Tang au Petit-Canton, la Mission du port, le dentiste — sans une
étoile (un gars recherché qui remplit une ordonnance, ça se remarque), on porte les sacs à Sal, et on revient dire
au docteur que c'est fini. Il n'est pas fier ; il le dit.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "h06",
    "titre": "Les ordonnances",
    "donneur": "lachance",
    "prerequis": ["h05"],
    "recompense": 350,
    "donne": {"message": "LE DOCTEUR NE DOIT PLUS RIEN À SAL"},

    # ⚠️ Trois comptoirs par le texte de leur enseigne (`boutique:<mot>`, `Histoire.boutiquex`) : aucune porte
    # neuve ne devient un lieu de mission, la ville ne glisse pas. La `course` les passe dans l'ordre, au volant
    # ou à pied, `sans_etoile` tout du long. Sal et Lachance sont DEDANS : on leur parle, pas de `retourner`.
    "objectifs": [
        {"type": "course", "texte": "TROIS ORDONNANCES, TROIS COMPTOIRS, ZÉRO ÉTOILE",
         "points": ["boutique:pharmacie", "boutique:mission", "boutique:dentiste"], "rayon": 3,
         "sans_etoile": True},

        {"type": "parler", "texte": "LES TROIS SACS DE PILULES À SAL, AU TERMINUS", "cible": "sal"},

        {"type": "parler", "texte": "DIS AU DOCTEUR QUE C'EST RÉGLÉ", "cible": "lachance"},
    ],

    # Intention (intro) : Lachance signe à son bureau, sans lever les yeux — la réplique tient le plan ; la coupe
    # montre le terminus (Sal) sous la deuxième ; la troisième se dit sur le noir qui revient.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "coupe", "vers": "porte:terminus", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Lachance : la honte d'un homme droit, dite au vocabulaire de l'hôpital
    # pour ne pas avoir à la nommer ; la voix ne tremble pas, elle ralentit. Sal : content, et presque tendre avec
    # le docteur — un bon client, c'est de la famille.
    "dialogue": {
        "appel": [
            _l("lachance", "Lachance, à l'appareil. Sal veut le reste en pilules. Viens, avant que je change d'idée.",
               jeu="[somber] Lachance, à l'appareil. [quietly] Sal veut le reste en pilules. [firmly] Viens, avant que je change d'idée.")
        ],
        "intro": [
            _l("lachance", "Trois ordonnances de calmants, trois patients qui n'existent pas. Ma signature, par exemple, est vraie.",
               jeu="[quietly] Trois ordonnances de calmants, trois patients qui n'existent pas. [bitterly] Ma signature, par exemple, est vraie."),
            _l("lachance", "La pharmacie Tang, la Mission du port, pis le dentiste. Sal a ses habitudes partout.",
               jeu="[matter-of-fact] La pharmacie Tang, la Mission du port, pis le dentiste. [wryly] Sal a ses habitudes partout."),
            _l("lachance", "Pas de police. Un pharmacien qui voit une étoile, il rappelle le médecin.",
               jeu="[serious] Pas de police. [firmly] Un pharmacien qui voit une étoile, il rappelle le médecin.")
        ],
        "pendant": [
            _p("lachance", "Souris au comptoir. Les gens malades sourient pas, les gens qui font une commission, oui.", 0,
               jeu="[deadpan] Souris au comptoir. [wryly] Les gens malades sourient pas, les gens qui font une commission, oui."),
            _p("lachance", "Les trois sacs à Sal. Je veux pas savoir à qui il les revend.", 1,
               jeu="[quietly] Les trois sacs à Sal. [somber] Je veux pas savoir à qui il les revend."),
            _p("lachance", "Reviens me voir. J'ai besoin de l'entendre dire par quelqu'un.", 2,
               jeu="[softly] Reviens me voir. [quietly] J'ai besoin de l'entendre dire par quelqu'un.")
        ],
        "accueil": [
            _a("sal", "Trois sacs. Le docteur a une belle main d'écriture, le neveu. Son compte est fermé.", 1,
               jeu="[satisfied] Trois sacs. [amused] Le docteur a une belle main d'écriture, le neveu. [warmly] Son compte est fermé.")
        ],
        "fin": [
            _l("lachance", "Fermé. Vingt ans de médecine, pis c'est un barbier qui me fait signer n'importe quoi.",
               jeu="[bitterly] Fermé. [somber] Vingt ans de médecine, pis c'est un barbier qui me fait signer n'importe quoi."),
            _l("lachance", "Prends ça. Pis si tu me vois à une table de cartes, sors-moi par le collet.",
               jeu="[matter-of-fact] Prends ça. [firmly] Pis si tu me vois à une table de cartes, sors-moi par le collet.")
        ],
        "echec": [
            _l("lachance", "Une étoile, pis tout le monde regarde ma signature. On arrête ça là.",
               jeu="[concerned] Une étoile, pis tout le monde regarde ma signature. [firmly] On arrête ça là.")
        ]
    }
}
