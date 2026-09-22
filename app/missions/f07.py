"""La mission f07 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "f07",
    "titre": "La caisse, encore",
    "donneur": "thibodeau",
    "prerequis": ["f04"],
    "recompense": 200,
    "donne": {"message": "LA CLÉ DU KIOSQUE, RETROUVÉE"},

    # ⚠️ `pickpocket` (M16) : `cible` nomme l'ARCHÉTYPE (`pietons.py`), pas un personnage —
    # le mécanisme de m2 (`Combat.pickpocket`) vide les poches par-derrière. ⚠️ Jamais un
    # archétype de GANG (`gang="cravates"` sur "cravate", `pietons.py`) : `pochesAPrendre`
    # refuse net quiconque porte `.gang` — un Cravate ne se pickpocket pas, il se bat.
    "objectifs": [
        {"type": "pickpocket", "texte": "VIDE SES POCHES, PAR-DERRIÈRE", "cible": "pickpocket"},

        {"type": "retourner", "texte": "RETOURNE VOIR MADAME THIBODEAU"}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Mme Thibodeau : en colère qu'on la vole encore,
    # puis soulagée sèchement — elle ne s'attendrit jamais longtemps, même contente.
    "dialogue": {
        "appel": [
            _l("thibodeau", "C'est Madame Thibodeau, du kiosque. Un petit voleur a profité du grabuge pour vider ma caisse, encore!",
               jeu="[angry] C'est Madame Thibodeau, du kiosque. [bitterly] Un petit voleur a profité du grabuge pour vider ma caisse… encore!")
        ],
        "intro": [
            _l("thibodeau", "Il a ma clé dans sa poche. Sans elle, mon tiroir-caisse reste fermé jusqu'au printemps.",
               jeu="[bitterly] Il a ma clé dans sa poche. [worried] Sans elle, mon tiroir-caisse reste fermé… jusqu'au printemps."),
            _l("thibodeau", "Approche-toi par-derrière. Fouille-le. Pis reviens vite, mon p'tit.",
               jeu="[firmly] Approche-toi par-derrière. Fouille-le. [warmly] Pis reviens vite, mon p'tit.")
        ],
        "pendant": [
            _p("thibodeau", "Il se sauvera au premier bruit. Approche-toi comme un chat.", 0,
               jeu="[worried] Il se sauvera au premier bruit. [quietly] Approche-toi comme un chat.")
        ],
        "fin": [
            _l("thibodeau", "Ma clé! T'es un bon garçon, toi, encore une fois.",
               jeu="[relieved] Ma clé! [warmly] T'es un bon garçon, toi… encore une fois."),
            _l("thibodeau", "Prends ça pour ta peine, pis dis-moi pas que c'est trop.",
               jeu="[tenderly] Prends ça pour ta peine… [firmly] pis dis-moi pas que c'est trop.")
        ],
        "echec": [
            _l("thibodeau", "Encore ratée... Ma pauvre caisse va rester fermée un bon bout.",
               jeu="[disappointed] Encore ratée… [sighs] Ma pauvre caisse va rester fermée un bon bout.")
        ]
    }
}
