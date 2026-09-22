"""La mission m2 — voir `app/missions/__init__.py` pour le moteur."""

from ._commun import _a, _l, _p

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
        # ⚠️ **ILS ARRIVENT, ET APRES SON INTRO.** Ils naissaient a 40 px du kiosque —
        # donc du joueur — des la pose de la mission : collés a elle pendant qu'elle
        # parlait (Martin, 20 sept. 2026). `loin` : ils naissent quand elle a fini,
        # a 15 tuiles (juste hors de l'ecran), et courent sur le joueur.
        {"type": "tuer", "groupe": "cravates", "n": 2, "ou": "donneur", "arme": "", "vie": 55, "loin": 15,
         "texte": "METS LES DEUX CRAVATES K.-O."},
        {"type": "ramasser", "cible": "fuyard", "vehicule": "moto", "texte": "RATTRAPE LE FUYARD EN MOTO"},
        # ⚠️ « Des missions plus longues » (Martin, 22 sept. 2026) : trois étapes de plus.
        # Le fuyard a sifflé ses chums — deux de plus, aux poings eux aussi, qui ARRIVENT où
        # l'on est (`loin`) : la même bagarre que la première, sans rien de neuf à apprendre.
        {"type": "tuer", "groupe": "cravates", "n": 2, "ou": "donneur", "arme": "", "vie": 55, "loin": 12,
         "texte": "DEUX AUTRES CRAVATES ARRIVENT — COUCHE-LES"},
        # Puis l'hôpital, à l'autre bout du Faubourg : c'est là qu'on se soigne, et Madame
        # Thibodeau ne veut « pas de sang sur ses journaux ». Ginette se tient à la porte.
        {"type": "aller", "lieu": "hopital", "rayon": 6, "texte": "VA TE FAIRE SOIGNER À L'HÔPITAL"},
        {"type": "parler", "cible": "ginette", "texte": "PARLE À GINETTE, À L'HÔPITAL"},
        {"type": "retourner", "texte": "RAPPORTE LA CAISSE À MADAME THIBODEAU"},
    ],
    # Elle montre le coin, et la caméra va le voir — VIDE : les deux Cravates n'y
    # naissent qu'une fois qu'elle a fini de parler (`loin`). À la fin, elle reprend
    # sa caisse et tend le bâton de son défunt.
    # ⚠️ Elle n'écrit QUE son intro : la caméra va voir la `cible` — le point d'où
    # les Cravates vont arriver (`Histoire.jouerOuDire` le nomme tant qu'ils
    # n'existent pas, puis l'homme lui-même), que le défaut ne vise jamais : c'est
    # un acteur que seule une partie en cours pose. Sa fin (elle reprend sa caisse,
    # elle tend le bâton de son défunt) est **mot pour mot** celle que
    # `scene_par_defaut` bâtit : on l'a donc effacée.
    "scenes": {
        "intro": [
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "cible", "duree": 60,
             "ensemble": True},
            {"type": "camera", "vers": "cible", "duree": 45, "courbe": "freine", "ensemble": True},
            {"type": "dire", "repliques": [2, 3]},
            {"type": "camera", "vers": "joueur", "duree": 40, "courbe": "freine"},
            {"type": "dire", "repliques": [4]},
        ],
    },
    # Le jeu de chaque réplique (`jeu=`) — Madame Thibodeau : inquiete, puis en colere, puis tendre.
    "dialogue": {
        "appel": [_l("thibodeau", "C'est Madame Thibodeau, du kiosque. Les Cravates me font des misères. Viens me voir, veux-tu?",
                     jeu="[worried] C'est Madame Thibodeau, du kiosque. Les Cravates me font des misères… Viens me voir, veux-tu?")],
        "intro": [
            _l("thibodeau", "Deux Cravates sont venus me « protéger ». Ils ont vidé ma caisse.",
               jeu="[bitterly] Deux Cravates sont venus me « protéger ». [angry] Ils ont vidé ma caisse."),
            _l("thibodeau", "Ils rôdent encore au coin. Fais-leur comprendre. Avec tes poings, pas plus.",
               jeu="[quietly] Ils rôdent encore au coin. Fais-leur comprendre… avec tes poings, pas plus."),
            _l("thibodeau", "Le troisième s'est sauvé en moto avec mon argent. Rattrape-le.",
               jeu="[angry] Le troisième s'est sauvé en moto avec mon argent. Rattrape-le."),
            _l("thibodeau", "Fais attention à toi, veux-tu? Ces grands escogriffes-là ont toujours des amis.",
               jeu="[concerned] Fais attention à toi, veux-tu? [bitterly] Ces grands escogriffes-là ont toujours des amis."),
        ],
        "fin": [
            _l("thibodeau", "Mon argent! T'es un bon garçon, toi.",
               jeu="[relieved] Mon argent! [warmly] T'es un bon garçon, toi."),
            _l("thibodeau", "Tiens, le bâton de mon défunt. Pis au kiosque, c'est moins cher pour toi.",
               jeu="[tenderly] Tiens… le bâton de mon défunt. Pis au kiosque, c'est moins cher pour toi."),
            _l("thibodeau", "Les Cravates vont parler de toi, astheure. Moi aussi, mais en bien.",
               jeu="[knowingly] Les Cravates vont parler de toi, astheure. [warmly] Moi aussi… mais en bien."),
        ],
        "echec": [_l("thibodeau", "Ils t'ont eu, hein? Repose-toi, pis reviens.",
                     jeu="[concerned] Ils t'ont eu, hein? Repose-toi… pis reviens.")],
        # PENDANT (2e vague des scènes) : dite quand son objectif commence.
        "pendant": [
            _p("thibodeau", "Il se sauve avec ma caisse! Lâche-le pas!", 1,
               jeu="[worried] Il se sauve avec ma caisse! Lâche-le pas!"),
            _p("thibodeau", "Ils ont sifflé leurs amis! Y en a deux autres qui s'en viennent, fais-leur la leçon.", 2,
               jeu="[worried] Ils ont sifflé leurs amis! [angry] Y en a deux autres qui s'en viennent, fais-leur la leçon."),
            _p("thibodeau", "T'as le visage en compote. Passe à l'hôpital avant, pas de sang sur mes journaux.", 3,
               jeu="[concerned] T'as le visage en compote. [wryly] Passe à l'hôpital avant… pas de sang sur mes journaux."),
            _p("thibodeau", "Reviens-t'en au kiosque, mon p'tit. J'ai mis de l'eau à bouillir pour le thé.", 5,
               jeu="[warmly] Reviens-t'en au kiosque, mon p'tit. [tenderly] J'ai mis de l'eau à bouillir pour le thé."),
        ],
        # ACCUEIL : Ginette, la première fois qu'on l'entend dans le jeu — elle se nomme et dit
        # d'où elle parle, une fois, sèche comme un pouls (docs/personnages/ginette.md).
        "accueil": [
            _a("ginette", "C'est Ginette, de l'hôpital. Assis-toi. Bon, t'en mourras pas, arrête de te battre avec ta face.", 4,
               jeu="[matter-of-fact] C'est Ginette, de l'hôpital. Assis-toi. [firmly] Bon, t'en mourras pas… arrête de te battre avec ta face."),
        ],
    },
}
