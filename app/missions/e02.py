"""La mission e02 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "e02",
    "titre": "La bière de Ti-Paul",
    "donneur": "tipaul",
    "prerequis": ["e01"],
    "recompense": 250,
    "echec": ["mort", "arrete", "vehicule_detruit"],
    "donne": {"message": "LE DÉPANNEUR EST STOCKÉ POUR UN MOIS"},

    # ⚠️ Le camion attend derrière la cantine des Quais (`porte:cantine`, un lieu
    # SPECIAUX déjà dessiné) : `poserLeChar` le pose au bord de rue le plus proche,
    # comme q04. La traversée Quais → Érables fait tout le trajet — le plan
    # d'origine le disait déjà (« à travers la ville »).
    "objectifs": [
        {"type": "monter", "texte": "PRENDS LE CAMION DE BIÈRE",
         "vehicule": "camion", "ou": "porte:cantine"},

        {"type": "livrer", "texte": "LIVRE-LE AU DÉPANNEUR SANS BOSSE",
         "lieu": "depanneur", "rayon": 4, "sans_degats": True},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Ti-Paul, comme e01 : bavard, s'énerve vite,
    # jubile encore plus vite. Sa voix (Québec Tremblay) est celle de Marco — jamais
    # dans le même dialogue.
    "dialogue": {
        "appel": [
            _l("tipaul", "C'est Ti-Paul! Mon stock de bière est resté au quai des Quais. Va donc me le chercher!",
               jeu="[worried] C'est Ti-Paul! Mon stock de bière est resté au quai des Quais. [excited] Va donc me le chercher!")
        ],
        "intro": [
            _l("tipaul", "Le camion est caché derrière la cantine de Lulu. Prends-le, pis roule tranquille jusqu'ici.",
               jeu="[matter-of-fact] Le camion est caché derrière la cantine de Lulu. [firmly] Prends-le, pis roule tranquille jusqu'ici."),
            _l("tipaul", "Pas une caisse de cassée! J'ai des clients qui comptent leurs bouteilles.",
               jeu="[annoyed] Pas une caisse de cassée! [playfully] J'ai des clients qui comptent leurs bouteilles.")
        ],
        "pendant": [
            _p("tipaul", "Douce, douce! C'est pas une course, c'est de la bière!", 0,
               jeu="[nervously] Douce, douce! [firmly] C'est pas une course, c'est de la bière!")
        ],
        "fin": [
            _l("tipaul", "Pas une bosse, pas une caisse de cassée! T'es un vrai chauffeur, toi.",
               jeu="[impressed] Pas une bosse, pas une caisse de cassée! [happy] T'es un vrai chauffeur, toi."),
            _l("tipaul", "Un mois de stock, grâce à toi. Tiens, pour la peine.",
               jeu="[warmly] Un mois de stock, grâce à toi. [satisfied] Tiens, pour la peine.")
        ],
        "echec": [
            _l("tipaul", "Envolée, ma bière... Un mois à sec, à cause de ça.",
               jeu="[disappointed] Envolée, ma bière… [sighs] Un mois à sec, à cause de ça.")
        ]
    }
}
