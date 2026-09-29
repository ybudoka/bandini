"""La mission p05 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "p05",
    "titre": "Les collets du Trappeur",
    "donneur": "trappeur",
    "prerequis": ["p01"],
    "recompense": 120,
    # La fronde du Trappeur (`armes.CATALOGUE`), ses billes comprises : un chargeur plein au sac.
    "donne": {"arme": "fronde", "message": "LA FRONDE DU TRAPPEUR, ET SES BILLES"},

    # De nuit, derrière le stationnement des Skateux, là où le bois commence : deux Skateux viennent relever ses
    # collets. ⚠️ Pas `ou: bois` : `Histoire.tuileDeBois` cherche le glyphe `n`, que la carte n'a plus — il rend
    # `null`, et les deux gars naissaient SUR le joueur, devant le phare (le banc l'a vu, comme `ou: quai` en q11).
    "objectifs": [
        {"type": "aller", "texte": "ATTENDS LA NUIT PRÈS DU PHARE",
         "lieu": "phare", "rayon": 6, "nuit": True},

        {"type": "tuer", "texte": "DEUX SKATEUX RELÈVENT SES COLLETS — COUCHE-LES",
         "groupe": "skateux", "n": 2, "ou": "zone:skateux"},

        {"type": "retourner", "texte": "RETOURNE VOIR LE TRAPPEUR"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Armand : l'ermite qui parle bas, parce que le bois écoute. Il n'aime ni la
    # police ni la ville ; il t'aime bien, toi, parce que tu marches doucement. Des phrases de conteur, des silences.
    "dialogue": {
        "appel": [
            _l("trappeur", "C'est Armand. Le Trappeur, qu'ils disent en ville. Quelqu'un vole mes collets.",
               jeu="[quietly] C'est Armand. [wryly] Le Trappeur, qu'ils disent en ville… [serious] Quelqu'un vole mes collets.")
        ],
        "intro": [
            _l("trappeur", "Chaque matin, mes collets sont vides, pis coupés. C'est pas un renard qui a un couteau.",
               jeu="[gravely] Chaque matin, mes collets sont vides, pis coupés. [wryly] C'est pas un renard qui a un couteau."),
            _l("trappeur", "Ils viennent la nuit. Attends la noirceur, pis va voir dans le bois.",
               jeu="[quietly] Ils viennent la nuit. [calm] Attends la noirceur… pis va voir dans le bois."),
            _l("trappeur", "Pas de police. La police, ça fait peur au gibier.",
               jeu="[deadpan] Pas de police. [amused] La police, ça fait peur au gibier.")
        ],
        "pendant": [
            _p("trappeur", "La nuit tombe. Écoute : le bois devient plus fort que la ville.", 0,
               jeu="[softly] La nuit tombe. [mysteriously] Écoute… le bois devient plus fort que la ville."),
            _p("trappeur", "Deux lampes de poche dans le bois. C'est eux. Vas-y doucement.", 1,
               jeu="[quietly] Deux lampes de poche dans le bois. C'est eux. [calm] Vas-y doucement."),
            _p("trappeur", "Reviens au phare. J'ai quelque chose pour toi.", 2,
               jeu="[warmly] Reviens au phare. [mysteriously] J'ai quelque chose pour toi.")
        ],
        "fin": [
            _l("trappeur", "Des Skateux. Des enfants de la ville qui jouent aux coureurs des bois.",
               jeu="[wryly] Des Skateux. [bitterly] Des enfants de la ville… qui jouent aux coureurs des bois."),
            _l("trappeur", "Tiens, ma fronde. Elle fait pas de bruit, pis la police l'entend pas.",
               jeu="[warmly] Tiens, ma fronde. [knowingly] Elle fait pas de bruit… pis la police l'entend pas.")
        ],
        "echec": [
            _l("trappeur", "Mes collets sont vides encore. Le bois va avoir faim cet hiver.",
               jeu="[somber] Mes collets sont vides encore. [gravely] Le bois va avoir faim cet hiver.")
        ]
    }
}
