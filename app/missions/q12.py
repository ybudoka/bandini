"""La mission q12 — voir app/missions/__init__.py pour le moteur.

La Chef a un cœur (M16, arc Q, 30 sept. 2026). La mère de Josée et de Lulu fait une crise, chez elle, aux Érables ;
l'ambulance de l'hôpital est sortie, et Josée ne demande jamais rien à personne. Elle le demande au neveu : prendre
l'ambulance à l'hôpital, aller chercher sa mère au dépanneur de Ti-Paul, où Lulu l'a assise, et la mener à
l'urgence en deux minutes — sans secousse.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "q12",
    "titre": "La Chef a un cœur",
    "donneur": "josee",
    "prerequis": ["q06"],
    "recompense": 300,
    "donne": {"message": "LA MÈRE DE JOSÉE DORT À L'HÔPITAL — JOSÉE TE DOIT UNE FAVEUR"},

    # ⚠️ Le patron de h01 et h04 : l'ambulance devant l'hôpital (`monter`), un `aller` au dépanneur (la mère y attend
    # avec Lulu), et `livrer` à l'urgence sous le chrono. Josée est dedans, au bar : sa fin passe au combiné.
    "objectifs": [
        {"type": "monter", "texte": "L'AMBULANCE, DEVANT L'HÔPITAL", "vehicule": "ambulance", "ou": "porte:hopital"},

        {"type": "aller", "texte": "SA MÈRE ATTEND AU DÉPANNEUR, AVEC LULU", "lieu": "depanneur", "rayon": 6},

        {"type": "livrer", "texte": "À L'URGENCE EN DEUX MINUTES, SANS SECOUSSE",
         "lieu": "hopital", "rayon": 5, "chrono_s": 120},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 30},
            {"type": "coupe", "vers": "porte:hopital", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Josée : pour une fois, la Chef a peur. Elle le cache sous des ordres courts,
    # et la voix se casse une fois, sur « ma mère ». Son `[warmly]` de la mission va au merci, à la fin.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. C'est ma mère. Viens au bar, vite.",
               jeu="[worried] Josée. [quietly] C'est ma mère. [firmly] Viens au bar, vite.")
        ],
        "intro": [
            _l("josee", "Elle a fait une crise aux Érables. Lulu l'a assise au dépanneur de Ti-Paul.",
               jeu="[worried] Elle a fait une crise aux Érables. [matter-of-fact] Lulu l'a assise au dépanneur de Ti-Paul."),
            _l("josee", "L'ambulance est devant l'hôpital, pis leurs gars sont tous sortis. Prends-la.",
               jeu="[firmly] L'ambulance est devant l'hôpital, pis leurs gars sont tous sortis. Prends-la."),
            _l("josee", "Deux minutes jusqu'à l'urgence. Pis tu la brasses pas. C'est ma mère.",
               jeu="[serious] Deux minutes jusqu'à l'urgence. Pis tu la brasses pas. [quietly] C'est ma mère.")
        ],
        "pendant": [
            _p("josee", "Les clés sont dedans. J'ai appelé Ginette, elle sait.", 0,
               jeu="[matter-of-fact] Les clés sont dedans. [calm] J'ai appelé Ginette, elle sait."),
            _p("josee", "Elle est sur le banc devant le dépanneur, avec Lulu. Arrête-toi à côté.", 1,
               jeu="[worried] Elle est sur le banc devant le dépanneur, avec Lulu. [firmly] Arrête-toi à côté."),
            _p("josee", "Elle respire. Lulu lui tient la main. Roule doux, mais roule.", 2,
               jeu="[quietly] Elle respire. Lulu lui tient la main. [firmly] Roule doux, mais roule.")
        ],
        "fin": [
            _l("josee", "Le docteur dit qu'elle va s'en remettre. Elle a demandé c'était qui, le chauffeur.",
               jeu="[relieved] Le docteur dit qu'elle va s'en remettre. [softly] Elle a demandé c'était qui, le chauffeur."),
            _l("josee", "Merci. Je le dirai pas deux fois, alors garde-le.",
               jeu="[warmly] Merci. [matter-of-fact] Je le dirai pas deux fois, alors garde-le.")
        ],
        "echec": [
            _l("josee", "L'ambulance est arrivée trop tard. On en reparlera jamais.",
               jeu="[coldly] L'ambulance est arrivée trop tard. [quietly] On en reparlera jamais.")
        ]
    }
}
