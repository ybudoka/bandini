"""La mission h04 — voir app/missions/__init__.py pour le moteur.

Le cœur (M16, arc H, 30 sept. 2026). Un cœur à greffer arrive de Québec par l'autobus de nuit, dans une glacière de
pêcheur, et l'ambulance de l'hôpital est la seule assez vite. On la prend, on va chercher la glacière au quai des
autobus (à pied : elle est posée par terre, `obtenir`), et on la ramène à l'urgence en quatre-vingt-dix secondes,
DANS l'ambulance (`livrer` + `chrono_s`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "h04",
    "titre": "Le cœur",
    "donneur": "lachance",
    "prerequis": ["h03"],
    "recompense": 400,
    "donne": {"message": "LE CŒUR EST ARRIVÉ À TEMPS"},

    # ⚠️ `obtenir` dans la ville (le patron de c03, le livre du Pouce au terminus) : l'objet est posé devant la porte
    # du terminus, on le ramasse en marchant dessus — à pied, pas au volant (`Infiltration.majObjets`). Puis
    # `livrer` : le char de la mission (l'ambulance) à l'hôpital, sous le chrono.
    "objectifs": [
        {"type": "monter", "texte": "PRENDS L'AMBULANCE DEVANT L'HÔPITAL",
         "vehicule": "ambulance", "ou": "porte:hopital"},

        {"type": "obtenir", "texte": "LA GLACIÈRE ARRIVE AU TERMINUS : PRENDS-LA À PIED",
         "objet": "glaciere_du_coeur", "ou": "terminus", "dessin": "sac", "nom": "LA GLACIÈRE DU CŒUR"},

        {"type": "livrer", "texte": "LE CŒUR À L'URGENCE EN AMBULANCE, VITE",
         "lieu": "hopital", "rayon": 5, "chrono_s": 90},
    ],

    # Intention (intro) : la voix de Lachance ne monte pas, c'est le rythme qui accélère — sa réplique tient le
    # bureau, puis la coupe va montrer le quai des autobus sous la deuxième, puis l'ambulance sous la troisième.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:terminus", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "porte:hopital", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Lachance : l'urgence qu'il connaît le mieux, celle qui a un chrono. Il
    # compte en minutes, il parle comme on lit un protocole ; à la fin, une fatigue heureuse qu'il ne cache pas.
    "dialogue": {
        "appel": [
            _l("lachance", "Ici Lachance. Un cœur arrive par l'autobus de nuit, pis mes ambulanciers sont tous sortis.",
               jeu="[serious] Ici Lachance. [concerned] Un cœur arrive par l'autobus de nuit, pis mes ambulanciers sont tous sortis.")
        ],
        "intro": [
            _l("lachance", "Un cœur, dans une glacière de pêcheur. Il vient de Québec, il a quatre heures de vie.",
               jeu="[gravely] Un cœur, dans une glacière de pêcheur. [matter-of-fact] Il vient de Québec… il a quatre heures de vie."),
            _l("lachance", "Le chauffeur va la poser sur le trottoir du terminus. Tu la prends à la main, doucement.",
               jeu="[firmly] Le chauffeur va la poser sur le trottoir du terminus. [calm] Tu la prends à la main… doucement."),
            _l("lachance", "Prends l'ambulance. Au retour, t'as une minute et demie, pas une seconde de plus.",
               jeu="[matter-of-fact] Prends l'ambulance. [serious] Au retour, t'as une minute et demie, pas une seconde de plus.")
        ],
        "pendant": [
            _p("lachance", "Elle a le plein pis des freins neufs. Ménage-la quand même, c'est la seule.", 0,
               jeu="[matter-of-fact] Elle a le plein pis des freins neufs. [firmly] Ménage-la quand même, c'est la seule."),
            _p("lachance", "Une glacière bleue, avec du tape. Le chauffeur n'a pas voulu la garder sur ses genoux.", 1,
               jeu="[matter-of-fact] Une glacière bleue, avec du tape. [wryly] Le chauffeur n'a pas voulu la garder sur ses genoux."),
            _p("lachance", "La salle est prête, le patient est endormi. Il manque juste toi.", 2,
               jeu="[serious] La salle est prête, le patient est endormi. [firmly] Il manque juste toi.")
        ],
        "fin": [
            _l("lachance", "Il bat. Dans quelqu'un d'autre, mais il bat.",
               jeu="[relieved] Il bat. [softly] Dans quelqu'un d'autre… mais il bat."),
            _l("lachance", "Tu as conduit comme un ambulancier. C'est le plus beau compliment que je fais.",
               jeu="[warmly] Tu as conduit comme un ambulancier. [matter-of-fact] C'est le plus beau compliment que je fais.")
        ],
        "echec": [
            _l("lachance", "Trop tard. On le dira à la famille avec des mots doux, mais c'est trop tard.",
               jeu="[somber] Trop tard. [quietly] On le dira à la famille avec des mots doux, mais c'est trop tard.")
        ]
    }
}
