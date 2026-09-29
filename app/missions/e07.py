"""La mission e07 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "e07",
    "titre": "La clé de la villa",
    "donneur": "diane",
    "prerequis": ["e06"],
    "recompense": 400,
    "echec": ["mort", "arrete", "etoile"],
    # Le dossier RESTE au sac : c'est lui que le maire voudra racheter (e11), ou Louise publier (c02).
    "donne": {"message": "LE DOSSIER DU MAIRE, DANS TON SAC"},

    # ⚠️ Le patron de v02 (la villa du maire, `app/blocs/villa.py`), mais la clé vient d'AILLEURS : le chauffeur
    # du maire fait le plein de cigarettes au dépanneur, et `pickpocket` lui vide les poches par-derrière —
    # `objet: cle_villa` met la clé de la porte de service au sac quand l'objectif est fait (la même serrure que
    # v02 et v03). Puis la nuit, la porte de service, le bureau d'en haut, et on ressort sans une étoile.
    "objectifs": [
        {"type": "pickpocket", "texte": "LE CHAUFFEUR DU MAIRE — VIDE SES POCHES, PAR-DERRIÈRE",
         "cible": "passant", "objet": "cle_villa"},

        {"type": "aller", "texte": "VA À LA VILLA DU MAIRE, DE NUIT",
         "lieu": "villa_chemin", "rayon": 6, "nuit": True},

        {"type": "aller", "texte": "ENTRE PAR LA PORTE DE SERVICE, AVEC SA CLÉ",
         "lieu": "villa_service", "rayon": 2, "sans_etoile": True},

        {"type": "obtenir", "texte": "LE DOSSIER DU MAIRE, DANS SON BUREAU D'EN HAUT",
         "objet": "dossier_maire", "nom": "LE DOSSIER DU MAIRE", "dessin": "dossier",
         "ou": "villa_bureau", "sans_etoile": True},

        {"type": "aller", "texte": "RESSORS PAR LE CHEMIN, SANS TE FAIRE VOIR",
         "lieu": "villa_chemin", "rayon": 3, "sans_etoile": True},

        {"type": "retourner", "texte": "APPORTE LE DOSSIER À DIANE"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Diane : elle monte d'un cran. Elle ne demande plus un service, elle
    # donne une adresse et une heure. La politesse reste, la patience s'en va.
    "dialogue": {
        "appel": [
            _l("diane", "Diane Larivière. Le maire a un dossier sur chaque conseiller. Je veux le mien, et les autres.",
               jeu="[coldly] Diane Larivière. [serious] Le maire a un dossier sur chaque conseiller. Je veux le mien… et les autres.")
        ],
        "intro": [
            _l("diane", "Son chauffeur achète ses cigarettes ici, à six heures. La clé de la porte de service est sur lui.",
               jeu="[matter-of-fact] Son chauffeur achète ses cigarettes ici, à six heures. [quietly] La clé de la porte de service est sur lui."),
            _l("diane", "Le dossier est dans le bureau d'en haut. Il y a des gardes, et ils ont des lampes.",
               jeu="[calm] Le dossier est dans le bureau d'en haut. [serious] Il y a des gardes… et ils ont des lampes."),
            _l("diane", "Une seule étoile et le maire saura qui l'a envoyé. Moi, je n'existe pas.",
               jeu="[menacingly] Une seule étoile et le maire saura qui l'a envoyé. [coldly] Moi, je n'existe pas.")
        ],
        "pendant": [
            _p("diane", "Le voilà, avec sa casquette. Passez derrière lui, les mains légères.", 0,
               jeu="[quietly] Le voilà, avec sa casquette. [calm] Passez derrière lui… les mains légères."),
            _p("diane", "Vous avez la clé. Attendez la nuit, les gardes changent à la noirceur.", 1,
               jeu="[satisfied] Vous avez la clé. [quietly] Attendez la nuit… les gardes changent à la noirceur."),
            _p("diane", "En haut, au fond. Ne touchez à rien d'autre, il compte ses stylos.", 3,
               jeu="[quietly] En haut, au fond. [wryly] Ne touchez à rien d'autre… il compte ses stylos."),
            _p("diane", "Sortez comme vous êtes entré. Doucement.", 4,
               jeu="[calm] Sortez comme vous êtes entré. [softly] Doucement.")
        ],
        "fin": [
            _l("diane", "Mon nom est dedans. Le vôtre aussi, d'ailleurs. Gardez-le, ce dossier : il vaut cher.",
               jeu="[surprised] Mon nom est dedans. [amused] Le vôtre aussi, d'ailleurs. [knowingly] Gardez-le, ce dossier : il vaut cher."),
            _l("diane", "Il y a une page sur les Chevreuils. Sur mon fils. Nous en reparlerons.",
               jeu="[quietly] Il y a une page sur les Chevreuils. [somber] Sur mon fils… Nous en reparlerons.")
        ],
        "echec": [
            _l("diane", "Un garde vous a vu. Je ne vous connais pas, et je ne vous ai jamais connu.",
               jeu="[coldly] Un garde vous a vu. [firmly] Je ne vous connais pas… et je ne vous ai jamais connu.")
        ]
    }
}
