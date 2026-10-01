"""La mission t14 — voir app/missions/__init__.py pour le moteur.

Les mariés (M16, arc T, les petites jobs — 1er oct. 2026). Une dame des Érables, en robe blanche sous son manteau : le
chauffeur de la noce n'est jamais venu, et les photos se prennent au phare. La belle auto (`monter`, une berline de
luxe que son oncle prête), la mariée qui monte (`proteger`), le phare. Un passant qui donne une job (`passant`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t14",
    "titre": "Les mariés",
    "donneur": "passante",
    "prerequis": ["m6"],
    "recompense": 120,
    "passant": {"archetype": "dame", "district": "erables", "nom": "La mariée"},
    "donne": {"message": "LES PHOTOS DE NOCES SE PRENNENT AU PHARE"},

    # La berline de l'oncle dort devant le dépanneur (un lieu de mission : rien ne bouge) ; la mariée monte quand on
    # s'arrête près d'elle, et descend au phare (`proteger`, cible : elle).
    "objectifs": [
        {"type": "monter", "texte": "LA BERLINE DE SON ONCLE, DEVANT LE DÉPANNEUR", "vehicule": "luxe",
         "ou": "porte:depanneur", "prete": "passante"},
        {"type": "proteger", "texte": "LA MARIÉE AU PHARE — LES PHOTOS ATTENDENT", "cible": "passante",
         "lieu": "phare", "rayon": 6},
    ],

    # Le jeu (`jeu=`) — la mariée : au bord des larmes, puis du fou rire ; elle se marie quand même, chauffeur ou pas.
    "dialogue": {
        "hele": [
            _l("passante", "Toi! Tu conduis?", jeu="[worried] Toi! Tu conduis?")
        ],
        "intro": [
            _l("passante", "Je me marie dans une heure, pis le chauffeur de la noce est jamais venu. Jamais!",
               jeu="[worried] Je me marie dans une heure, pis le chauffeur de la noce est jamais venu. [shouting] Jamais!"),
            _l("passante", "La berline de mon oncle est devant le dépanneur. Amène-moi au phare, c'est là qu'on fait les photos.",
               jeu="[nervously] La berline de mon oncle est devant le dépanneur. [softly] Amène-moi au phare, c'est là qu'on fait les photos.")
        ],
        "pendant": [
            _p("passante", "Les clés sont sur le pare-soleil. Mon oncle a confiance en tout le monde.", 0,
               jeu="[matter-of-fact] Les clés sont sur le pare-soleil. [amused] Mon oncle a confiance en tout le monde."),
            _p("passante", "Doucement dans les bosses! Ma coiffure a coûté plus cher que la robe.", 1,
               jeu="[worried] Doucement dans les bosses! [playfully] Ma coiffure a coûté plus cher que la robe.")
        ],
        "fin": [
            _l("passante", "On est arrivés! Cent vingt piasses, pis t'es invité au buffet. Y a des pets-de-sœur.",
               jeu="[happy] On est arrivés! [warmly] Cent vingt piasses, pis t'es invité au buffet. [playfully] Y a des pets-de-sœur.")
        ],
        "echec": [
            _l("passante", "Ben voyons. Je vais me marier en autobus, d'abord.",
               jeu="[disappointed] Ben voyons. [sighs] Je vais me marier en autobus, d'abord.")
        ]
    }
}
