"""La mission m6 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m6", "titre": "Le tour du propriétaire", "donneur": "josee", "prerequis": ["m5"],
    "recompense": 300, "phase": 1, "echec": ["mort", "arrete"],
    "donne": {"message": "QUATRE CONTACTS AU TÉLÉPHONE",
              "contacts": ["tipaul", "lulu", "raymonde", "ovila"]},
    # Le tour de Josée : quatre districts, quatre portes, du dépanneur au
    # phare. Chaque objectif `parler` nomme sa CIBLE — ce qu'on accomplit en
    # lui parlant, jamais en s'approchant de sa tuile (`Histoire` lit la cible).
    "objectifs": [
        {"type": "parler", "cible": "tipaul", "texte": "PARLE À TI-PAUL, AU DÉPANNEUR"},
        {"type": "parler", "cible": "lulu", "texte": "PARLE À LULU, À LA CANTINE"},
        {"type": "parler", "cible": "raymonde", "texte": "PARLE À RAYMONDE, À L'USINE"},
        {"type": "parler", "cible": "ovila", "texte": "PARLE À OVILA, AU PHARE"},
    ],
    # Josée parle dedans : la caméra sort voir le dépanneur, la première
    # porte du tour. Il n'y a pas d'objectif `retourner` — la mission se
    # clôt après le dernier contact, et Josée est loin : la fin se dit
    # donc au combiné.
    # ⚠️ Elle n'écrit QUE son intro, qui montre la PREMIÈRE PORTE du tour alors
    # que le tour en compte quatre. Sa fin — une coupe chez Josée, qui est loin :
    # elle parle au combiné — est celle que `scene_par_defaut` bâtit, mot pour
    # mot, et elle est effacée.
    "scenes": {
        "intro": [
            {"type": "dire", "repliques": [1], "ensemble": True},
            {"type": "coupe", "vers": "porte:depanneur", "ferme": 20, "ouvre": 20, "tient": 150},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "porte:depanneur", "duree": 70,
             "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
        ],
    },
    "dialogue": {
        "appel": [_l("josee", "Josée. Le Faubourg est à nous. Viens au bar, je te présente la ville.")],
        "intro": [
            _l("josee", "Quatre coins, quatre personnes. Ti-Paul au dépanneur, ma sœur Lulu à la cantine."),
            _l("josee", "Raymonde tient le syndicat à l'usine, pis Ovila garde le phare."),
            _l("josee", "Va leur serrer la main. Dans cette ville, tout commence par là."),
        ],
        "fin": [
            _l("josee", "Quatre poignées de main. Le monde va t'appeler par ton nom, astheure."),
            _l("josee", "Garde l'œil ouvert. Il se passe plus de choses que t'en penses."),
        ],
        "echec": [_l("josee", "Tu reviendras quand tu auras le temps de faire le tour.")],
        "pendant": [_p("josee", "Le dépanneur d'abord. Ti-Paul en sait plus qu'il en a l'air.", 0)],
    },
}
