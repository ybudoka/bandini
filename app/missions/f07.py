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
    # ⚠️ Des missions plus longues (Martin, 22 sept. 2026) : le voleur boit l'argent de la
    # caisse à la cantine des Quais, à l'autre bout de la ville — `pickpocket` le pose près du
    # joueur, donc LÀ-BAS, une fois l'`aller` fait. Sa clé prise, la caisse file avec son
    # complice, un Cravate en moto (`ramasser` + `fuyard`, le patron de m2) : on la rapporte
    # au kiosque. `cantine` est déjà un lieu de mission : la ville ne bouge pas.
    "objectifs": [
        {"type": "aller", "texte": "VA À LA CANTINE DES QUAIS : IL BOIT MON ARGENT",
         "lieu": "cantine", "rayon": 6},

        {"type": "pickpocket", "texte": "VIDE SES POCHES, PAR-DERRIÈRE", "cible": "pickpocket"},

        {"type": "ramasser", "texte": "SON COMPLICE FILE AVEC LA CAISSE : RATTRAPE-LE",
         "cible": "fuyard", "vehicule": "moto"},

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
            _p("thibodeau", "Il se sauvera au premier bruit. Approche-toi comme un chat.", 1,
               jeu="[worried] Il se sauvera au premier bruit. [quietly] Approche-toi comme un chat."),
            _p("thibodeau", "Il boit mon argent à la cantine des Quais. À ma santé, j'imagine.", 0,
               jeu="[bitterly] Il boit mon argent à la cantine des Quais. [wryly] À ma santé, j'imagine."),
            _p("thibodeau", "Ma clé, mais pas ma caisse? Son complice file avec! Rattrape-le, mon p'tit!", 2,
               jeu="[angry] Ma clé, mais pas ma caisse? Son complice file avec! [firmly] Rattrape-le, mon p'tit!"),
            _p("thibodeau", "Rapporte-la-moi, veux-tu? Pis secoue-la pas trop, elle est plus toute jeune.", 3,
               jeu="[relieved] Rapporte-la-moi, veux-tu? [amused] Pis secoue-la pas trop… elle est plus toute jeune.")
        ],
        "fin": [
            _l("thibodeau", "Ma clé! T'es un bon garçon, toi, encore une fois.",
               jeu="[relieved] Ma clé! [warmly] T'es un bon garçon, toi… encore une fois."),
            _l("thibodeau", "Prends ça pour ta peine, pis dis-moi pas que c'est trop.",
               jeu="[tenderly] Prends ça pour ta peine… [firmly] pis dis-moi pas que c'est trop."),
            _l("thibodeau", "Deux fois volée, deux fois rapportée. Je devrais t'engager, toi.",
               jeu="[amused] Deux fois volée, deux fois rapportée. [warmly] Je devrais t'engager, toi.")
        ],
        "echec": [
            _l("thibodeau", "Encore ratée... Ma pauvre caisse va rester fermée un bon bout.",
               jeu="[disappointed] Encore ratée… [sighs] Ma pauvre caisse va rester fermée un bon bout.")
        ]
    }
}
