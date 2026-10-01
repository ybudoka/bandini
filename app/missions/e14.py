"""La mission e14 — voir app/missions/__init__.py pour le moteur.

C'était un accident (M16, arc E, les Érables — 1er oct. 2026). Diane a le dossier du maire (e07) ; elle veut aussi
une image. La berline du maire dort derrière l'Hôtel Bandini, où il passe ses nuits : on la prend sans se faire voir
(`sans_etoile`), on la conduit au bout du chemin privé de Son Honneur, et on la laisse rouler dans sa propre piscine
(`plonger`, `static/js/piscine.js`). Louise attend avec son appareil : la une du lendemain.

⚠️ « Sa piscine » : la piscine de villa la plus proche du passage de son domaine (`piscine:bloc:villa`) — la maison
d'été au bout de son chemin privé. Aucun lieu neuf, la ville ne bouge pas.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "e14",
    "titre": "C'était un accident",
    "donneur": "diane",
    "prerequis": ["e07"],
    "recompense": 300,
    "echec": ["mort", "arrete", "vehicule_detruit", "etoile"],
    "donne": {"manchette": "maire_a_la_piscine", "message": "LOUISE A SA PHOTO — LE MAIRE À LA UNE"},

    "objectifs": [
        {"type": "monter", "texte": "LA BERLINE DU MAIRE, DERRIÈRE L'HÔTEL — PAS VU",
         "vehicule": "luxe", "ou": "ruelle:hotel", "sans_etoile": True},

        {"type": "plonger", "texte": "DANS SA PISCINE, AU BOUT DE SON CHEMIN — PAS VU",
         "lieu": "piscine:bloc:villa", "sans_etoile": True},

        {"type": "retourner", "texte": "LOUISE A SA PHOTO : VA LE DIRE À DIANE"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Diane : elle n'a jamais aimé le maire, et ce matin elle s'amuse un peu.
    # Elle se nomme une fois, au téléphone.
    "dialogue": {
        "appel": [
            _l("diane", "Diane Larivière. Le maire dort à l'hôtel, et sa berline s'ennuie. Passez au dépanneur.",
               jeu="[knowingly] Diane Larivière. [amused] Le maire dort à l'hôtel, et sa berline s'ennuie. [calm] Passez au dépanneur.")
        ],
        "intro": [
            _l("diane", "Un dossier, ça se lit. Une photo, ça se regarde. Les citoyens regardent plus qu'ils ne lisent.",
               jeu="[knowingly] Un dossier, ça se lit. Une photo, ça se regarde. [wryly] Les citoyens regardent plus qu'ils ne lisent."),
            _l("diane", "Sa berline, au fond de sa propre piscine. Personne ne vous voit, et c'était un accident.",
               jeu="[mischievously] Sa berline, au fond de sa propre piscine. [firmly] Personne ne vous voit, et c'était un accident.")
        ],
        "pendant": [
            _p("diane", "Derrière l'hôtel. Son chauffeur dort aussi, il est payé pour ça.", 0,
               jeu="[quietly] Derrière l'hôtel. [wryly] Son chauffeur dort aussi, il est payé pour ça."),
            _p("diane", "Au bord de la piscine, au bout de son chemin. Arrêtez, descendez, et laissez la pente travailler.", 1,
               jeu="[calm] Au bord de la piscine, au bout de son chemin. [mischievously] Arrêtez, descendez, et laissez la pente travailler."),
            _p("diane", "Louise a eu sa photo. Revenez me voir, on va lire le journal ensemble demain.", 2,
               jeu="[satisfied] Louise a eu sa photo. [amused] Revenez me voir, on va lire le journal ensemble demain.")
        ],
        "fin": [
            _l("diane", "Une berline de soixante mille piastres au fond d'une piscine chauffée. C'est presque de la poésie.",
               jeu="[amused] Une berline de soixante mille piastres au fond d'une piscine chauffée. [wryly] C'est presque de la poésie."),
            _l("diane", "Pour votre peine. Demain, le maire sera à la une, en maillot, à côté de son char.",
               jeu="[calm] Pour votre peine. [mischievously] Demain, le maire sera à la une, en maillot, à côté de son char.")
        ],
        "echec": [
            _l("diane", "On vous a vu. Le maire va crier au complot, et pour une fois il aura raison.",
               jeu="[coldly] On vous a vu. [disappointed] Le maire va crier au complot, et pour une fois il aura raison.")
        ]
    }
}
