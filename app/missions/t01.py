"""La mission t01 — voir app/missions/__init__.py pour le moteur.

Mon char est au lot (M16, arc T, les petites jobs — 1er oct. 2026). Un banlieusard des Érables : la ville lui a
remorqué son auto devant sa propre maison (« un dimanche! »). La reprendre au lot de la fourrière — sans payer, on
ne paie pas la ville pour un dimanche —, semer Gilles qui appelle la police par principe, la ramener au dépanneur,
et revenir lui dire. Un passant qui donne une job (`passant`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t01",
    "titre": "Mon char est au lot",
    "donneur": "passant",
    "prerequis": ["m6"],
    "recompense": 80,
    "passant": {"archetype": "banlieusard", "district": "erables", "nom": "Le banlieusard"},
    "donne": {"message": "SON AUTO EST REVENUE AUX ÉRABLES"},

    # Le patron d'e13 : l'auto se prend au lot (`porte:fourriere`), Gilles appelle la police, on la livre devant le
    # dépanneur (un lieu de mission déjà) ; il attend là où il t'a hélé — `retourner`.
    "objectifs": [
        {"type": "monter", "texte": "SON AUTO DORT AU LOT DE LA FOURRIÈRE : REPRENDS-LA", "vehicule": "auto",
         "ou": "porte:fourriere", "prete": "passant"},
        {"type": "semer", "texte": "GILLES APPELLE LA POLICE, PAR PRINCIPE : SÈME-LA", "etoiles": 1},
        {"type": "livrer", "texte": "GARE-LA DEVANT LE DÉPANNEUR DES ÉRABLES", "lieu": "depanneur", "rayon": 6},
        {"type": "retourner", "texte": "DIS AU BANLIEUSARD QUE SON AUTO EST REVENUE"},
    ],

    # Le jeu (`jeu=`) — le banlieusard : outré, poli jusqu'à l'os, et fier de sa pelouse même sous la neige.
    "dialogue": {
        "hele": [
            _l("passant", "Hé! Monsieur!", jeu="[annoyed] Hé! Monsieur!")
        ],
        "intro": [
            _l("passant", "La ville m'a remorqué mon auto devant ma propre maison. Un dimanche!",
               jeu="[angry] La ville m'a remorqué mon auto devant ma propre maison. [shouting] Un dimanche!"),
            _l("passant", "Elle est au lot de la fourrière. Moi, je paie pas la ville pour un dimanche.",
               jeu="[firmly] Elle est au lot de la fourrière. [smugly] Moi, je paie pas la ville pour un dimanche.")
        ],
        "pendant": [
            _p("passant", "Une auto grise, propre, avec un sapin qui sent la vanille. Tu peux pas la manquer.", 0,
               jeu="[matter-of-fact] Une auto grise, propre, avec un sapin qui sent la vanille. [confident] Tu peux pas la manquer."),
            _p("passant", "La police? Pour une auto qui est à moi? Ben voyons donc.", 1,
               jeu="[surprised] La police? Pour une auto qui est à moi? [sarcastic] Ben voyons donc."),
            _p("passant", "Devant le dépanneur, à l'ombre. Ti-Paul la surveille pour moi.", 2,
               jeu="[calm] Devant le dépanneur, à l'ombre. [knowingly] Ti-Paul la surveille pour moi.")
        ],
        "fin": [
            _l("passant", "Pas une égratignure? T'es un ange. Quatre-vingts, pis pas un mot à ma femme.",
               jeu="[relieved] Pas une égratignure? T'es un ange. [whispers] Quatre-vingts, pis pas un mot à ma femme.")
        ],
        "echec": [
            _l("passant", "Bon. Je vais payer la ville, comme un cave. Merci pareil.",
               jeu="[disappointed] Bon. Je vais payer la ville, comme un cave. [sighs] Merci pareil.")
        ]
    }
}
