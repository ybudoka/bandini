"""La mission q08 — voir app/missions/__init__.py pour le moteur.

Le moteur du capitaine (M16, arc Q, 30 sept. 2026). Le capitaine Bérubé garde, en plus de son traversier, une vieille
chaloupe à moteur pour « aller voir l'île quand le bon Dieu le permet ». Deux jeunes lui ont volé le moteur hors-bord
et filent avec, dans la boîte d'un pick-up. On les rattrape, le moteur tombe, on le rapporte au bout du quai. C'est
elle, la chaloupe, qui ouvre l'arc de l'île (i01).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "q08",
    "titre": "Le moteur du capitaine",
    "donneur": "berube",
    "prerequis": ["m6"],
    "recompense": 200,
    "donne": {"message": "LA CHALOUPE DU CAPITAINE A RETROUVÉ SON MOTEUR"},

    # ⚠️ Le fuyard (le patron de m50, d02) part de la rue devant le quai du traversier, où se tient Bérubé
    # (`traversier:quais`, dehors) : `retourner` le trouve.
    "objectifs": [
        {"type": "ramasser", "texte": "DEUX JEUNES FILENT AVEC LE MOTEUR : RATTRAPE-LES",
         "cible": "fuyard", "vehicule": "auto"},

        {"type": "retourner", "texte": "RAPPORTE LE MOTEUR AU CAPITAINE, AU BOUT DU QUAI"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Bérubé : posé, un peu solennel, des images de marin ; il ne pose pas de
    # question, et il ne se fâche pas — il constate.
    "dialogue": {
        "appel": [
            _l("berube", "Capitaine Bérubé, du traversier. On m'a volé un moteur, pis je cours plus assez vite.",
               jeu="[calm] Capitaine Bérubé, du traversier. [wryly] On m'a volé un moteur, pis je cours plus assez vite.")
        ],
        "intro": [
            _l("berube", "Ma chaloupe, c'est pour aller voir l'île, quand le bon Dieu et la marée le permettent.",
               jeu="[calm] Ma chaloupe, c'est pour aller voir l'île, quand le bon Dieu et la marée le permettent."),
            _l("berube", "Deux jeunes ont dévissé le moteur à l'aube. Il est dans la boîte d'un pick-up, qui file.",
               jeu="[matter-of-fact] Deux jeunes ont dévissé le moteur à l'aube. [firmly] Il est dans la boîte d'un pick-up, qui file."),
            _l("berube", "Ramène-le-moi. Je te demanderai pas comment.",
               jeu="[knowingly] Ramène-le-moi. [calm] Je te demanderai pas comment.")
        ],
        "pendant": [
            _p("berube", "Ils ont pris le chemin du pont. Un moteur, ça pèse ; ils iront pas loin.", 0,
               jeu="[matter-of-fact] Ils ont pris le chemin du pont. [calm] Un moteur, ça pèse ; ils iront pas loin."),
            _p("berube", "Je t'attends au bout du quai. Mets-le pas à l'eau, il nage pas mieux que moi.", 1,
               jeu="[calm] Je t'attends au bout du quai. [wryly] Mets-le pas à l'eau, il nage pas mieux que moi.")
        ],
        "fin": [
            _l("berube", "Un Johnson de cinquante-huit. Il a plus de milles que moi, pis il tourne encore.",
               jeu="[warmly] Un Johnson de cinquante-huit. [calm] Il a plus de milles que moi, pis il tourne encore."),
            _l("berube", "Merci. La chaloupe est à ta disposition, quand tu voudras voir l'île.",
               jeu="[warmly] Merci. [matter-of-fact] La chaloupe est à ta disposition, quand tu voudras voir l'île.")
        ],
        "echec": [
            _l("berube", "Le moteur est parti. La chaloupe restera au quai, comme moi.",
               jeu="[somber] Le moteur est parti. [calm] La chaloupe restera au quai, comme moi.")
        ]
    }
}
