"""La mission i01 — voir app/missions/__init__.py pour le moteur.

Le moteur tourne (M16, arc I « L'Île-aux-Corneilles », 30 sept. 2026). La chaloupe du capitaine marche enfin (q08).
Il a une caisse d'outils promise depuis l'été à Léo, qui garde le hangar de l'île ; ses jambes, elles, ne font plus
la traversée. On prend la chaloupe, on traverse la baie, on accoste près du hangar, et on met pour la première fois
le pied sur l'île — Léo ne pose pas de questions, et il n'en répond pas non plus.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "i01",
    "titre": "Le moteur tourne",
    "donneur": "berube",
    "prerequis": ["q08"],
    "recompense": 120,
    "donne": {"message": "L'ÎLE-AUX-CORNEILLES : LÉO TE CONNAÎT"},

    # ⚠️ L'île ne se rejoint pas à pied (`test_barrieres.py`) : pas de `lieu` sur l'île. La chaloupe se prend à un
    # amarrage de la rive (`amarrage:bar`, le patron de m52) et se livre à celui du hangar (`amarrage:hangar_ile`) ;
    # Léo se tient dehors, devant son hangar — on lui parle à pied.
    "objectifs": [
        {"type": "monter", "texte": "LA CHALOUPE DU CAPITAINE, AMARRÉE SOUS LE FAUBOURG",
         "vehicule": "bateau", "ou": "amarrage:bar", "prete": "berube"},

        {"type": "livrer", "texte": "TRAVERSE LA BAIE JUSQU'AU HANGAR DE L'ÎLE",
         "lieu": "amarrage:hangar_ile", "rayon": 6},

        {"type": "parler", "texte": "LA CAISSE D'OUTILS À LÉO, DEVANT SON HANGAR", "cible": "leo"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "amarrage:hangar_ile", "duree": 70,
             "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    "dialogue": {
        "appel": [
            _l("berube", "Bérubé. Le moteur tourne comme au premier jour. J'ai une commission pour l'île.",
               jeu="[warmly] Bérubé. [calm] Le moteur tourne comme au premier jour. J'ai une commission pour l'île.")
        ],
        "intro": [
            _l("berube", "Une caisse d'outils pour Léo, au hangar. Je la lui promets depuis l'été.",
               jeu="[matter-of-fact] Une caisse d'outils pour Léo, au hangar. [calm] Je la lui promets depuis l'été."),
            _l("berube", "L'île, c'est là-bas, derrière la brume. Trente tuiles d'eau, pis pas une police.",
               jeu="[calm] L'île, c'est là-bas, derrière la brume. [knowingly] Trente tuiles d'eau, pis pas une police."),
            _l("berube", "Léo parle peu. Réponds-lui pareil, vous allez bien vous entendre.",
               jeu="[wryly] Léo parle peu. [calm] Réponds-lui pareil, vous allez bien vous entendre.")
        ],
        "pendant": [
            _p("berube", "Elle est amarrée sous le Faubourg. Tire la corde deux fois, elle est capricieuse.", 0,
               jeu="[matter-of-fact] Elle est amarrée sous le Faubourg. [wryly] Tire la corde deux fois, elle est capricieuse."),
            _p("berube", "Garde le phare à ta gauche. Le hangar, c'est le grand toit de tôle.", 1,
               jeu="[calm] Garde le phare à ta gauche. [matter-of-fact] Le hangar, c'est le grand toit de tôle."),
            _p("berube", "Accoste doucement, pis marche jusqu'à lui. Il t'attend sans t'attendre.", 2,
               jeu="[calm] Accoste doucement, pis marche jusqu'à lui. [knowingly] Il t'attend sans t'attendre.")
        ],
        "accueil": [
            _a("leo", "Léo, du hangar. La caisse du capitaine? Pose-la là, j'ai rien vu pis rien reçu.", 2,
               jeu="[deadpan] Léo, du hangar. La caisse du capitaine? [mysteriously] Pose-la là, j'ai rien vu pis rien reçu.")
        ],
        "fin": [
            _l("berube", "Léo a eu sa caisse? Alors l'île te connaît, astheure. Elle oublie pas vite.",
               jeu="[warmly] Léo a eu sa caisse? [knowingly] Alors l'île te connaît, astheure. Elle oublie pas vite."),
            _l("berube", "Tiens, pour l'essence. La chaloupe, elle, boit plus que moi.",
               jeu="[wryly] Tiens, pour l'essence. [calm] La chaloupe, elle, boit plus que moi.")
        ],
        "echec": [
            _l("berube", "La caisse est au fond de la baie. Léo attendra encore un été.",
               jeu="[somber] La caisse est au fond de la baie. [calm] Léo attendra encore un été.")
        ]
    }
}
