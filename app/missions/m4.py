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
    # ⚠️ **ELLE N'ÉCRIT AUCUNE SCÈNE, et elle en a deux** — le bloc Lego
    # (`scene_par_defaut`, dans `__init__.py`). Bouchard parle dedans : le défaut
    # sort voir le poste par une coupe (le lieu que nomme son premier objectif —
    # l'auto-patrouille, elle, est le deuxième), il croise les bras, il finit sa
    # phrase. À la fin on est au garage et lui au casse-croûte : le défaut va chez
    # lui, et il parle au combiné. C'est exactement ce qui était écrit ici, plan
    # pour plan.
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
