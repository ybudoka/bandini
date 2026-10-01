"""La mission t13 — voir app/missions/__init__.py pour le moteur.

La pelle du vieux (M16, arc T, les petites jobs — 1er oct. 2026). Un itinérant des Quais, sa pelle, son gagne-pain
de l'hiver : une Morue la lui a prise « pour rire ». La reprendre (`tuer` : une Morue qui arrive), la lui rendre — et
il te la laisse : il en a une autre. Un passant qui donne une job (`passant`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t13",
    "titre": "La pelle du vieux",
    "donneur": "passant",
    "prerequis": ["m6"],
    "recompense": 20,
    "passant": {"archetype": "itinerant", "district": "quais", "nom": "Le vieux"},
    "donne": {"arme": "pelle", "message": "LA PELLE DU VIEUX : GARDE-LA"},

    # Une Morue qui ARRIVE (`loin`) : elle naît hors champ à la fin de l'intro et vient à toi — pas de lieu neuf, et
    # rien de posé là où la fin se joue (devant le vieux, `retourner`).
    "objectifs": [
        {"type": "tuer", "texte": "UNE MORUE A PRIS SA PELLE : VA LA CHERCHER", "groupe": "morues", "n": 1, "loin": 9},
        {"type": "retourner", "texte": "RENDS SA PELLE AU VIEUX"},
    ],

    # Le jeu (`jeu=`) — le vieux : digne, lent, et un sens de l'humour qui a vu passer pas mal d'hivers.
    "dialogue": {
        "hele": [
            _l("passant", "Psst! Le jeune!", jeu="[mysteriously] Psst! Le jeune!")
        ],
        "intro": [
            _l("passant", "Une Morue m'a pris ma pelle. Pour rire, qu'il a dit. Moi, l'hiver, je pellette pour manger.",
               jeu="[gravely] Une Morue m'a pris ma pelle. [sarcastic] Pour rire, qu'il a dit. [somber] Moi, l'hiver, je pellette pour manger."),
            _l("passant", "Il s'en vient par icitte, il revient toujours rire de moi. Reprends-la-lui.",
               jeu="[knowingly] Il s'en vient par icitte, il revient toujours rire de moi. [firmly] Reprends-la-lui.")
        ],
        "pendant": [
            _p("passant", "Le voilà, avec ma pelle sur l'épaule comme un roi.", 0,
               jeu="[annoyed] Le voilà, avec ma pelle sur l'épaule comme un roi."),
            _p("passant", "Il rit moins, hein? Ramène-moi ça.", 1,
               jeu="[amused] Il rit moins, hein? [warmly] Ramène-moi ça.")
        ],
        "fin": [
            _l("passant", "Garde-la, mon gars. J'en ai une autre, pis toi, t'en as besoin plus que moi.",
               jeu="[warmly] Garde-la, mon gars. [amused] J'en ai une autre, pis toi, t'en as besoin plus que moi."),
            _l("passant", "Vingt piasses. C'est tout ce que j'ai, mais c'est de bon cœur.",
               jeu="[softly] Vingt piasses. [tenderly] C'est tout ce que j'ai, mais c'est de bon cœur.")
        ],
        "echec": [
            _l("passant", "Laisse faire, le jeune. L'hiver va être long, c'est tout.",
               jeu="[somber] Laisse faire, le jeune. [sighs] L'hiver va être long, c'est tout.")
        ]
    }
}
