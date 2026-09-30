"""La mission i03 — voir app/missions/__init__.py pour le moteur.

Le hangar sans nom (M16, arc I, 30 sept. 2026). Le hangar de l'île n'a pas de nom sur sa porte, et Léo ne dit
jamais à qui il le loue : Sven y garde ce qu'il ne veut pas voir aux Quais. Josée veut deux de ses caisses. De nuit,
sans une étoile, en chaloupe : on traverse, on prend les caisses derrière le hangar pendant que Léo regarde
ailleurs, et on les ramène au Brouillard par l'eau.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "i03",
    "titre": "Le hangar sans nom",
    "donneur": "josee",
    "prerequis": ["q04", "i01"],
    "recompense": 400,
    "donne": {"message": "DEUX CAISSES DU NORVÉGIEN DORMENT AU BROUILLARD"},

    # ⚠️ Le patron de i01 (la chaloupe d'un amarrage à l'autre) et de c03 (`obtenir` posé devant une porte) ;
    # `sans_etoile` tout du long de l'île. Josée est dedans : on finit par lui parler, au bar.
    "objectifs": [
        {"type": "aller", "texte": "ATTENDS LA NUIT AU BROUILLARD", "lieu": "bar", "rayon": 8, "nuit": True},

        {"type": "monter", "texte": "LA CHALOUPE, AMARRÉE SOUS LE FAUBOURG", "vehicule": "bateau", "ou": "amarrage:bar"},

        {"type": "livrer", "texte": "JUSQU'AU HANGAR SANS NOM, SANS ÊTRE VU",
         "lieu": "amarrage:hangar_ile", "rayon": 6, "sans_etoile": True},

        {"type": "obtenir", "texte": "LES CAISSES DE SVEN, DEVANT LE HANGAR : PRENDS-LES",
         "objet": "caisses_de_sven", "ou": "hangar_ile", "dessin": "sac", "nom": "LES CAISSES DU NORVÉGIEN",
         "sans_etoile": True},

        {"type": "livrer", "texte": "RAMÈNE-LES SOUS LE FAUBOURG, PAR L'EAU", "lieu": "amarrage:bar", "rayon": 6},

        {"type": "parler", "texte": "JOSÉE COMPTE LES CAISSES, AU BAR", "cible": "josee"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "amarrage:hangar_ile", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    "dialogue": {
        "appel": [
            _l("josee", "Josée. Le Norvégien cache des affaires sur l'île, pis j'en veux deux. Viens au bar.",
               jeu="[coldly] Josée. Le Norvégien cache des affaires sur l'île, [matter-of-fact] pis j'en veux deux. Viens au bar.")
        ],
        "intro": [
            _l("josee", "Le hangar de l'île a pas de nom sur la porte. Sven y met ce qu'il veut pas voir aux Quais.",
               jeu="[mysteriously] Le hangar de l'île a pas de nom sur la porte. [coldly] Sven y met ce qu'il veut pas voir aux Quais."),
            _l("josee", "De nuit, en chaloupe. Deux caisses, derrière le hangar. Léo regardera ailleurs, il est payé pour.",
               jeu="[matter-of-fact] De nuit, en chaloupe. Deux caisses, derrière le hangar. [wryly] Léo regardera ailleurs, il est payé pour."),
            _l("josee", "Pas une étoile. Une sirène sur l'eau, ça s'entend jusqu'au cargo.",
               jeu="[firmly] Pas une étoile. [coldly] Une sirène sur l'eau, ça s'entend jusqu'au cargo.")
        ],
        "pendant": [
            _p("josee", "La lune se couche vers une heure. C'est là que tu pars.", 0,
               jeu="[quietly] La lune se couche vers une heure. [matter-of-fact] C'est là que tu pars."),
            _p("josee", "La chaloupe est sous le Faubourg, attachée à un pieu. Rame pas, le moteur suffit.", 1,
               jeu="[matter-of-fact] La chaloupe est sous le Faubourg, attachée à un pieu. [wryly] Rame pas, le moteur suffit."),
            _p("josee", "Tous feux éteints. Suis la côte, pas la lumière du phare.", 2,
               jeu="[quietly] Tous feux éteints. [firmly] Suis la côte, pas la lumière du phare."),
            _p("josee", "Deux caisses, avec une ancre peinte dessus. Pas une de plus.", 3,
               jeu="[coldly] Deux caisses, avec une ancre peinte dessus. [firmly] Pas une de plus."),
            _p("josee", "Reviens par où t'es venu. Mes gars t'attendent au pieu.", 4,
               jeu="[calm] Reviens par où t'es venu. [matter-of-fact] Mes gars t'attendent au pieu."),
            _p("josee", "Entre. On ouvre ça ensemble.", 5,
               jeu="[quietly] Entre. [mysteriously] On ouvre ça ensemble.")
        ],
        "fin": [
            _l("josee", "Des montres suisses, pis des cartes marines de la Garde côtière. Sven a de l'ambition.",
               jeu="[knowingly] Des montres suisses, pis des cartes marines de la Garde côtière. [coldly] Sven a de l'ambition."),
            _l("josee", "Garde ça pour toi. Le reste, on le vendra au Norvégien lui-même, un jour.",
               jeu="[matter-of-fact] Garde ça pour toi. [mysteriously] Le reste, on le vendra au Norvégien lui-même, un jour.")
        ],
        "echec": [
            _l("josee", "Vu sur l'eau. Sven va déménager son hangar, pis on saura plus où.",
               jeu="[coldly] Vu sur l'eau. [matter-of-fact] Sven va déménager son hangar, pis on saura plus où.")
        ]
    }
}
