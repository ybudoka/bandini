"""La mission m2 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m2", "titre": "Le kiosque de Madame Thibodeau", "donneur": "thibodeau", "prerequis": ["m1"],
    "recompense": 150, "phase": 1, "echec": ["mort", "arrete"],
    "donne": {"arme": "batte", "rabais": {"kiosque": 0.75}, "message": "LE BÂTON, ET −25 % AU KIOSQUE"},
    "objectifs": [
        # ⚠️ **LA PREMIERE BAGARRE DU JEU, ET ELLE SE GAGNE AUX POINGS.** Ces
        # deux-la sont venus racketter une dame au kiosque, pas casser un
        # homme : ils arrivent LES MAINS VIDES, comme Madame Thibodeau le
        # promet deux lignes plus bas (« Avec tes poings, pas plus »).
        # Mesure d'avant : ils portaient le baton de l'archetype — 18 de
        # degats et `renverse`, contre 100 PV et des poings a 8. Un joueur
        # passif tombait en 3 s, et les coucher demandait 4,3 s de coups
        # sans une image perdue : la premiere bagarre exigeait un jeu
        # parfait. ⚠️ Et le baton est la RECOMPENSE de cette mission-ci :
        # on le rencontrait avant de l'avoir.
        {"type": "tuer", "groupe": "cravates", "n": 2, "ou": "donneur", "arme": "", "vie": 55,
         "texte": "METS LES DEUX CRAVATES K.-O."},
        {"type": "ramasser", "cible": "fuyard", "vehicule": "moto", "texte": "RATTRAPE LE FUYARD EN MOTO"},
        {"type": "retourner", "texte": "RAPPORTE LA CAISSE À MADAME THIBODEAU"},
    ],
    # Elle montre le coin, et la caméra va voir les deux Cravates — qui existent :
    # la mission est posée avant son intro. À la fin, elle reprend sa caisse et
    # tend le bâton de son défunt.
    # ⚠️ Elle n'écrit QUE son intro : la caméra va voir les deux Cravates —
    # `cible`, qui existe parce que la mission est posée avant son intro, et que
    # le défaut, lui, ne vise jamais un acteur qu'une partie en cours pose. Sa fin
    # (elle reprend sa caisse, elle tend le bâton de son défunt) est **mot pour
    # mot** celle que `scene_par_defaut` bâtit : on l'a donc effacée.
    "scenes": {
        "intro": [
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "cible", "duree": 60,
             "ensemble": True},
            {"type": "camera", "vers": "cible", "duree": 45, "courbe": "freine", "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
            {"type": "camera", "vers": "joueur", "duree": 40, "courbe": "freine"},
        ],
    },
    "dialogue": {
        "appel": [_l("thibodeau", "C'est Madame Thibodeau, du kiosque. Les Cravates me font des misères. Viens me voir, veux-tu?")],
        "intro": [
            _l("thibodeau", "Deux Cravates sont venus me « protéger ». Ils ont vidé ma caisse."),
            _l("thibodeau", "Ils rôdent encore au coin. Fais-leur comprendre. Avec tes poings, pas plus."),
            _l("thibodeau", "Le troisième s'est sauvé en moto avec mon argent. Rattrape-le."),
        ],
        "fin": [
            _l("thibodeau", "Mon argent! T'es un bon garçon, toi."),
            _l("thibodeau", "Tiens, le bâton de mon défunt. Pis au kiosque, c'est moins cher pour toi."),
        ],
        "echec": [_l("thibodeau", "Ils t'ont eu, hein? Repose-toi, pis reviens.")],
        # PENDANT (2e vague des scènes) : dite quand son objectif commence.
        "pendant": [_p("thibodeau", "Il se sauve avec ma caisse! Lâche-le pas!", 1)],
    },
}
