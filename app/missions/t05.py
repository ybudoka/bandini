"""La mission t05 — voir app/missions/__init__.py pour le moteur.

La sacoche (M16, arc T, les petites jobs — 1er oct. 2026). Une passante du Faubourg : un itinérant est parti avec sa
sacoche. Il ne court pas vite, et il ne se retourne jamais : la reprendre par-derrière (`pickpocket`), et la lui
rapporter. Un passant qui donne une job (`passant`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t05",
    "titre": "La sacoche",
    "donneur": "passante",
    "prerequis": ["m6"],
    "recompense": 50,
    "passant": {"archetype": "passante", "district": "faubourg", "nom": "La passante"},
    "donne": {"message": "LA SACOCHE EST RENTRÉE À LA MAISON"},

    "objectifs": [
        {"type": "pickpocket", "texte": "L'ITINÉRANT A SA SACOCHE : REPRENDS-LA PAR-DERRIÈRE", "cible": "itinerant"},
        {"type": "retourner", "texte": "RENDS SA SACOCHE À LA PASSANTE"},
    ],

    # Le jeu (`jeu=`) — la passante : fâchée, puis gênée d'être fâchée — c'est un itinérant, après tout.
    "dialogue": {
        "hele": [
            _l("passante", "Hé! Aide-moi!", jeu="[worried] Hé! Aide-moi!")
        ],
        "intro": [
            _l("passante", "Le monsieur, là, avec le manteau trois fois trop grand? Il est parti avec ma sacoche!",
               jeu="[angry] Le monsieur, là, avec le manteau trois fois trop grand? [shouting] Il est parti avec ma sacoche!"),
            _l("passante", "Fais-y pas mal, hein. Reprends-la par-derrière, il s'en rendra même pas compte.",
               jeu="[concerned] Fais-y pas mal, hein. [softly] Reprends-la par-derrière, il s'en rendra même pas compte.")
        ],
        "pendant": [
            _p("passante", "Doucement! Il entend rien, mais il sent tout.", 0,
               jeu="[whispers] Doucement! [nervously] Il entend rien, mais il sent tout."),
            _p("passante", "Tu l'as? Rapporte-la, mes clés sont dedans!", 1,
               jeu="[excited] Tu l'as? [relieved] Rapporte-la, mes clés sont dedans!")
        ],
        "fin": [
            _l("passante", "Mes clés, mon rouge à lèvres, mes billets de loto! Tiens, cinquante, pis merci.",
               jeu="[relieved] Mes clés, mon rouge à lèvres, mes billets de loto! [warmly] Tiens, cinquante, pis merci.")
        ],
        "echec": [
            _l("passante", "Ben voyons. Je vais faire changer mes serrures, d'abord.",
               jeu="[disappointed] Ben voyons. [sighs] Je vais faire changer mes serrures, d'abord.")
        ]
    }
}
