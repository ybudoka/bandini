"""La mission m4 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m4", "titre": "Le lunch du sergent", "donneur": "bouchard", "prerequis": ["m3"],
    "recompense": 400, "phase": 1, "echec": ["arrete", "vehicule_detruit"],
    "donne": {"sergent_ami": True, "message": "LE SERGENT EST TON AMI"},
    "objectifs": [
        {"type": "aller", "lieu": "poste", "rayon": 5, "nuit": True, "texte": "VA AU POSTE, DE NUIT"},
        {"type": "monter", "vehicule": "police", "ou": "porte:poste", "texte": "PRENDS L'AUTO-PATROUILLE"},
        {"type": "semer", "etoiles": 2, "escorte": "ti_guy", "texte": "SÈME LA POLICE — TI-GUY TE SUIT"},
        {"type": "livrer", "lieu": "garage", "rayon": 4, "texte": "LARGUE L'AUTO AU GARAGE"},
    ],
    # Bouchard parle dedans : la caméra sort voir le poste. ⚠️ L'auto-patrouille
    # est le deuxième objectif, mais elle y attend déjà (`Histoire.poser`) — sauf
    # ici, où l'on parle DANS le casse-croûte : rien ne se pose avant la sortie, et
    # la coupe montre le poste seul. À la fin, on est au garage et lui au
    # casse-croûte : la caméra va chez lui, et il parle au combiné.
    "scenes": {
        "intro": [
            {"type": "dire", "repliques": [1], "ensemble": True},
            {"type": "coupe", "vers": "porte:poste", "ferme": 20, "ouvre": 20, "tient": 150},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:bouchard", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire"},
        ],
    },
    "dialogue": {
        "appel": [_l("bouchard", "Bouchard. Marco m'a parlé de toi. Viens dîner au casse-croûte, j'ai une job.")],
        "intro": [
            _l("bouchard", "Y a une auto-patrouille au poste que j'aimerais voir disparaître. Papiers pas propres."),
            _l("bouchard", "Prends-la de nuit, sans témoin. Ti-Guy va te suivre en char, pour faire diversion."),
            _l("bouchard", "Largue-la au garage. Pis si mes gars te courent après, sème-les."),
        ],
        "fin": [
            _l("bouchard", "Propre. À partir d'aujourd'hui, si un de mes gars te pogne, tu dis mon nom."),
            _l("bouchard", "Un mot d'avertissement : Josée, au bar, cherche du monde comme toi. Fais attention."),
        ],
        "echec": [_l("bouchard", "J'ai rien vu, j'ai rien entendu. Reviens quand ça sera calme.")],
        # PENDANT (2e vague des scènes) : dite quand son objectif commence.
        "pendant": [_p("ti_guy", "C'est Ti-Guy, j'suis juste derrière toi. Roule, j'm'occupe des bœufs.", 2)],
    },
}
