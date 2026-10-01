"""La mission p07 — voir app/missions/__init__.py pour le moteur.

Le souper dansant (M16, arc P, 1er oct. 2026). Le club de l'âge d'or de La Pointe a son souper dansant à l'Hôtel
Bandini ; le chauffeur de leur vieil autobus a la grippe, et M. Bilodeau a promis à sa femme qu'elle danserait. On
prend l'autobus devant le phare (`monter`), on ramasse les voisins du bout — aux Souvenirs, aux Planches, au pied du
pont (`course`, trois arrêts dans l'ordre) — et on les livre à l'hôtel sans les brasser (`livrer`, `sans_degats` :
la prime).

⚠️ Écarts à la fiche (« Les Bilodeau déménagent ») : un souper dansant plutôt qu'un déménagement — les mêmes
retraités, le même autobus, la même adresse ; trois arrêts, pas quatre (La Pointe n'a que deux enseignes et un pont,
et une porte neuve ferait glisser la ville) ; et les chocs coûtent la prime, pas la mission. ⚠️ Le rayon des arrêts
est de huit tuiles : les deux enseignes sont à six et sept tuiles de la rue, et l'autobus ne monte pas sur le trottoir.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "p07",
    "titre": "Le souper dansant",
    "donneur": "bilodeau",
    "prerequis": ["la_pointe"],
    "recompense": 250,
    "donne": {"message": "LE CLUB DE L'ÂGE D'OR DANSE"},

    "objectifs": [
        {"type": "monter", "texte": "LE VIEIL AUTOBUS DU CLUB, DEVANT LE PHARE",
         "vehicule": "autobus", "ou": "porte:phare", "prete": "bilodeau"},

        {"type": "course", "texte": "LES VOISINS DU BOUT : TROIS ARRÊTS, DANS L'ORDRE",
         "points": ["boutique:souvenirs", "boutique:planches", "pont"], "rayon": 8},

        {"type": "livrer", "texte": "LE SOUPER DANSANT, À L'HÔTEL BANDINI — DOUCEMENT",
         "lieu": "hotel", "rayon": 6, "sans_degats": True},
    ],

    # Intention (intro) : M. Bilodeau, endimanché, qui s'excuse de demander ; la caméra va voir l'autobus du club,
    # vieux et jaune, puis revient pour la vraie raison — sa femme, qui n'a pas dansé depuis dix ans.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "vehicule", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Bilodeau : poli, il vouvoie, il dit « monsieur » ; un peu gêné de
    # demander, fier de sa femme, et il s'emporte une fois (les chocs) avant de se reprendre.
    "dialogue": {
        "appel": [
            _l("bilodeau", "Roméo Bilodeau, du bout de La Pointe. Savez-vous conduire un autobus, monsieur?",
               jeu="[warmly] Roméo Bilodeau, du bout de La Pointe. [softly] Savez-vous conduire un autobus, monsieur?")
        ],
        "intro": [
            _l("bilodeau", "Le club de l'âge d'or a son souper dansant à l'Hôtel Bandini, pis notre chauffeur a la grippe.",
               jeu="[sighs] Le club de l'âge d'or a son souper dansant à l'Hôtel Bandini, [annoyed] pis notre chauffeur a la grippe."),
            _l("bilodeau", "L'autobus est là. Il est vieux, mais il démarre si on lui parle poliment.",
               jeu="[matter-of-fact] L'autobus est là. [playfully] Il est vieux, mais il démarre si on lui parle poliment."),
            _l("bilodeau", "Ma femme a pas dansé depuis dix ans. J'y ai promis, monsieur.",
               jeu="[softly] Ma femme a pas dansé depuis dix ans. [warmly] J'y ai promis, monsieur.")
        ],
        "pendant": [
            _p("bilodeau", "Doucement avec la clutch. Elle a connu Duplessis.", 0,
               jeu="[nervously] Doucement avec la clutch. [playfully] Elle a connu Duplessis."),
            _p("bilodeau", "Madame Gagnon aux Souvenirs, les Thériault aux Planches, pis Ernest au pied du pont.", 1,
               jeu="[matter-of-fact] Madame Gagnon aux Souvenirs, les Thériault aux Planches, [warmly] pis Ernest au pied du pont."),
            _p("bilodeau", "Tout le monde est à bord! Pas de trous, pas de freins secs, ils ont des hanches neuves.", 2,
               jeu="[cheerful] Tout le monde est à bord! [gruffly] Pas de trous, pas de freins secs, ils ont des hanches neuves.")
        ],
        "fin": [
            _l("bilodeau", "Ils sont arrivés! Ma femme a appelé de l'hôtel, l'orchestre joue déjà.",
               jeu="[relieved] Ils sont arrivés! [warmly] Ma femme a appelé de l'hôtel, l'orchestre joue déjà."),
            _l("bilodeau", "Tenez, monsieur. Pis gardez-vous une valse pour la fin de la soirée.",
               jeu="[warmly] Tenez, monsieur. [playfully] Pis gardez-vous une valse pour la fin de la soirée.")
        ],
        "echec": [
            _l("bilodeau", "Pas de souper dansant, d'abord. Ma femme a remis ses souliers dans la boîte.",
               jeu="[disappointed] Pas de souper dansant, d'abord. [sighs] Ma femme a remis ses souliers dans la boîte.")
        ]
    }
}
