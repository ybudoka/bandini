"""La mission f09 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "f09",
    "titre": "Marco veut sa part",
    "donneur": "marco",
    "prerequis": ["f06"],
    "recompense": 250,
    "donne": {"message": "MARCO A VU OÙ EST L'ARGENT"},

    # ⚠️ `proteger` (M16) : Marco te suit à pied (`e.suit`, le mécanisme du petit qui
    # colle à sa mère) jusqu'au kiosque ; `lieu`+`rayon` font avancer l'objectif comme
    # un `aller`, tant qu'il reste vivant. Deux Cravates tendent une embuscade en route.
    "objectifs": [
        {"type": "proteger", "texte": "ESCORTE MARCO JUSQU'AU KIOSQUE",
         "cible": "marco", "lieu": "kiosque", "rayon": 5},

        {"type": "tuer", "texte": "REPOUSSE LES DEUX CRAVATES",
         "groupe": "cravates", "n": 2, "ou": "donneur", "loin": 10}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Marco : la désinvolture de qui a peur et le
    # cache, comme f01 ; il hausse les épaules sur l'embuscade, puis se rengorge à la fin.
    "dialogue": {
        "appel": [
            _l("marco", "Cousin, c'est Marco. J'ai ma part à aller chercher au kiosque, pis j'aime pas marcher seul.",
               jeu="[casually] Cousin, c'est Marco. [wryly] J'ai ma part à aller chercher au kiosque… pis j'aime pas marcher seul.")
        ],
        "intro": [
            _l("marco", "Les Cravates ont pas digéré la dernière fois. Reste collé sur moi jusqu'au kiosque.",
               jeu="[casually] Les Cravates ont pas digéré la dernière fois. [firmly] Reste collé sur moi… jusqu'au kiosque."),
            _l("marco", "Si ça chauffe, tu t'en occupes. Moi, je marche vite pis je regarde pas en arrière.",
               jeu="[wryly] Si ça chauffe, tu t'en occupes. [nervously] Moi, je marche vite… pis je regarde pas en arrière.")
        ],
        "pendant": [
            _p("marco", "Deux gars en cravate! Je le savais! Occupe-toi d'eux, cousin!", 1,
               jeu="[worried] Deux gars en cravate! [excited] Je le savais! Occupe-toi d'eux, cousin!")
        ],
        "fin": [
            _l("marco", "On est arrivés en un morceau. J'ai ma part, pis j'ai vu où le reste de l'argent dort.",
               jeu="[relieved] On est arrivés en un morceau. [impressed] J'ai ma part… pis j'ai vu où le reste de l'argent dort."),
            _l("marco", "Ça pourrait servir, un jour. Merci, cousin.",
               jeu="[knowingly] Ça pourrait servir, un jour. [warmly] Merci, cousin.")
        ],
        "echec": [
            _l("marco", "Ils m'ont eu presque... T'étais où, cousin?",
               jeu="[coldly] Ils m'ont eu presque… [annoyed] T'étais où, cousin?")
        ]
    }
}
