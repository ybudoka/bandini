"""La mission c04 — voir app/missions/__init__.py pour le moteur.

La chute du Pouce, pour de bon (Martin, 29 sept. 2026). Il a vu que son livre manquait : ce soir, il vide la caisse
du sous-sol — la paye du quartier — et il sort par la porte d'en arrière, celle des descentes de police. Son
chauffeur file avec elle (`ramasser`, `cible: fuyard`) ; on l'accroche, on reprend la caisse, et le Pouce, lui, prend
l'autobus de Sorel en jurant qu'il déménage. On la rapporte au Dragon d'or.

⚠️ **LE TRIPOT CHANGE DE MAINS** (`tripot.REPRISE`, `apres: c04`) : le Pouce et ses gros bras ne sont plus là, le
vieux Chan tient la barbotte pour Irène, les dés sont blancs pour de vrai, plus de méfiance ni de semaine barrée, et
la piastre va au quartier. Le lendemain matin, le Clairon en fait sa une (`donne.manchette`, `journal.SPECIALES`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "c04",
    "titre": "La barbotte change de mains",
    "donneur": "irene",
    "prerequis": ["c03"],
    "recompense": 1500,
    "donne": {"message": "LE TRIPOT EST À IRÈNE · LES DÉS SONT BLANCS", "manchette": "pouce_parti"},

    # ⚠️ Irène est DEDANS : le fuyard naît sur la rue la plus proche de la porte du Dragon d'or (`poserLeFuyard`,
    # comme m50 depuis la cantine) — posé avant l'intro, et il ne roule qu'à la fin des répliques. Accroché ou
    # cassé, son chauffeur (une Cravate que le Pouce paie, et mal : c03) en descend avec la caisse ; couché, il la
    # lâche. On la rapporte à la porte du Dragon d'or (six tuiles : le lieu du donneur).
    "objectifs": [
        {"type": "ramasser", "texte": "LE CHAUFFEUR DU POUCE FILE AVEC LA CAISSE — ACCROCHE-LE",
         "cible": "fuyard", "vehicule": "auto"},

        {"type": "aller", "texte": "RAPPORTE LA CAISSE DU QUARTIER AU DRAGON D'OR", "lieu": "nord_casino", "rayon": 6},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Irène : ce soir, plus de taquinerie d'abord ; la croupière devient
    # sérieuse, pressée, froide envers le Pouce — puis, la caisse rentrée, la tendresse qu'elle cachait sous les
    # gages, et une dernière taquinerie pour la route. Le Pouce : un beau parleur qui perd, et qui fait encore le
    # fier en se sauvant — la mauvaise foi joviale, jamais la menace. Irène se nomme à l'appel ; le Pouce, qu'on
    # entend pour la première fois, se nomme lui-même, à la troisième personne, comme un homme qui s'aime.
    "dialogue": {
        "appel": [
            _l("irene", "Irène Lam. Le Pouce a vu que son livre manquait, pis il fait ses valises à soir.",
               jeu="[serious] Irène Lam. [quietly] Le Pouce a vu que son livre manquait… pis il fait ses valises à soir.")
        ],
        "intro": [
            _l("irene", "Il vide la caisse du sous-sol. Cette caisse-là, mon pigeon, c'est la paye du quartier.",
               jeu="[serious] Il vide la caisse du sous-sol. [somber] Cette caisse-là, mon pigeon… c'est la paye du quartier."),
            _l("irene", "Il va sortir par la porte d'en arrière, celle des descentes de police. Il connaît le chemin.",
               jeu="[knowingly] Il va sortir par la porte d'en arrière, celle des descentes de police. [wryly] Il connaît le chemin."),
            _l("irene", "Rattrape-la. Moi, je descends lui dire deux mots, avec ses dés pis son livre.",
               jeu="[firmly] Rattrape-la. [coldly] Moi, je descends lui dire deux mots… avec ses dés pis son livre.")
        ],
        "pendant": [
            _p("irene", "C'est son chauffeur qui a la caisse! Une Cravate qu'il paye, pis mal. Accroche-le!", 0,
               jeu="[surprised] C'est son chauffeur qui a la caisse! [wryly] Une Cravate qu'il paye, pis mal. [firmly] Accroche-le!"),
            _p("pouce", "Réal Vachon se sauve pas, le jeune, il déménage! Garde-la, ta caisse, j'ai un autobus pour Sorel.", 1,
               jeu="[smugly] Réal Vachon se sauve pas, le jeune… il déménage! [sarcastic] Garde-la, ta caisse, j'ai un autobus pour Sorel."),
            _p("irene", "Laisse-le courir, il court mal. Ramène la caisse au Dragon d'or, le monde attend.", 1,
               jeu="[amused] Laisse-le courir, il court mal. [warmly] Ramène la caisse au Dragon d'or… le monde attend.")
        ],
        "fin": [
            _l("irene", "Le vieux Chan a sa pension, pis la boulangère s'achète un camion. Usagé, mais neuf pour elle.",
               jeu="[warmly] Le vieux Chan a sa pension, pis la boulangère s'achète un camion. [amused] Usagé… mais neuf pour elle."),
            _l("irene", "La barbotte d'en bas, c'est à moi, astheure. Des dés blancs, pis la piastre au quartier.",
               jeu="[satisfied] La barbotte d'en bas, c'est à moi, astheure. [firmly] Des dés blancs… pis la piastre au quartier."),
            _l("irene", "Pis toi, t'as une place à ma table de mah-jong. Tu vas perdre, mais t'as une place.",
               jeu="[tenderly] Pis toi, t'as une place à ma table de mah-jong. [teasing] Tu vas perdre… mais t'as une place.")
        ],
        "echec": [
            _l("irene", "La caisse est partie avec lui. Le quartier va se souvenir du Pouce longtemps.",
               jeu="[bitterly] La caisse est partie avec lui. [somber] Le quartier va se souvenir du Pouce… longtemps.")
        ]
    },

    # Intention (intro) : Irène ne croise plus les bras — elle MONTRE le fond de la salle, l'escalier du sous-sol,
    # sur « la caisse du sous-sol » ; la caméra sort voir la rue du Dragon d'or, où le char du chauffeur attend
    # moteur en marche, pendant « la porte d'en arrière » ; et elle se lève pour descendre. ⚠️ La coupe en
    # `ensemble`, PUIS la réplique. Intention (fin) : à sa porte, au combiné, la tendresse enfin dite.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "joueur", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:nord_casino", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:irene", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 40},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [3]},
        ],
    },
}
