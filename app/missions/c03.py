"""La mission c03 — voir app/missions/__init__.py pour le moteur.

La chute du Pouce, deuxième temps (docs/jalons/le-quartier-chinois.md, étape 3). Les dés prouvent la triche ; Irène
veut maintenant l'ARGENT DU MONDE — et un tricheur écrit tout ce qu'il gagne. Le Pouce loge à l'Hôtel Bandini, dans
la suite royale (⚠️ pas la chambre 12 : c'est celle de q07, en brouillon). On fait jaser le concierge, qui ne dit
jamais le nom d'un client mais vend tout le reste ; on file le comptable du Pouce, qui porte le livre au terminus
pour les rabatteurs ; on le ramasse avant eux, sur le chrono.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "c03",
    "titre": "La suite royale",
    "donneur": "irene",
    "prerequis": ["c02"],
    "recompense": 600,
    "donne": {"message": "LE LIVRE DE COMPTES DU POUCE EST À TOI"},

    # ⚠️ Norbert se tient DEDANS (`point:norbert`, le hall de l'hôtel) : `parler` le trouve, comme f10. Le comptable
    # naît à bonne distance de la porte de l'hôtel et attend qu'on soit au volant (`suivre`) ; son `lieu`, le
    # terminus, est DÉJÀ un lieu de mission (c01, ses rabatteurs) — un lieu neuf élargirait son devant, et la ville
    # glisserait. Le livre se pose à la porte du terminus quand la filature finit (`obtenir`, sans `table` ni
    # `garde`) : trente secondes avant que les rabatteurs passent le prendre (`chrono_s`).
    "objectifs": [
        {"type": "parler", "texte": "À L'HÔTEL, FAIS JASER NORBERT SUR LA SUITE ROYALE", "cible": "norbert"},

        {"type": "suivre", "texte": "SUIS LE COMPTABLE DU POUCE SANS TE FAIRE REPÉRER",
         "vehicule": "auto", "loin": 10, "proche": 3, "lieu": "terminus"},

        {"type": "obtenir", "texte": "RAMASSE SON LIVRE AVANT LES RABATTEURS",
         "objet": "livre_du_pouce", "ou": "terminus", "dessin": "registre", "nom": "LE LIVRE DE COMPTES DU POUCE",
         "chrono_s": 30},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Irène : la joueuse qui a flairé la faille (« un tricheur écrit tout »),
    # le sourire en coin ; puis, en parlant du vieux Chan et de la boulangère, la colère froide qui la fait tenir ;
    # à la fin, en lisant le livre au combiné, le mépris amusé devant une si belle main d'écriture. Norbert : le
    # service qui dit tout en n'ayant rien dit — calme, bas, jamais surpris, et il ne nomme pas son client. Irène se
    # nomme à l'appel ; Norbert, connu depuis f10, ne se représente pas.
    "dialogue": {
        "appel": [
            _l("irene", "Irène Lam, mon pigeon. Le Pouce couche dans la suite royale de l'hôtel, pis je gage qu'il dort sur un livre.",
               jeu="[knowingly] Irène Lam, mon pigeon. [mischievously] Le Pouce couche dans la suite royale de l'hôtel… pis je gage qu'il dort sur un livre.")
        ],
        "intro": [
            _l("irene", "Un tricheur écrit tout ce qu'il gagne. Pas pour l'impôt : pour se le relire, le soir.",
               jeu="[knowingly] Un tricheur écrit tout ce qu'il gagne. [wryly] Pas pour l'impôt… pour se le relire, le soir."),
            _l("irene", "Le concierge de l'hôtel sait tout, pis il le vend. Va le faire jaser sur la suite royale.",
               jeu="[matter-of-fact] Le concierge de l'hôtel sait tout, pis il le vend. [firmly] Va le faire jaser sur la suite royale."),
            _l("irene", "Avec ce livre-là, le vieux Chan pis la boulangère ravoient leur argent. À la cenne.",
               jeu="[somber] Avec ce livre-là, le vieux Chan pis la boulangère ravoient leur argent. [firmly] À la cenne.")
        ],
        "pendant": [
            _p("irene", "Il regarde ses chiffres, pas son rétroviseur. Reste pas collé dessus quand même.", 1,
               jeu="[amused] Il regarde ses chiffres, pas son rétroviseur. [firmly] Reste pas collé dessus quand même."),
            _p("irene", "Il l'a laissé au terminus pour les rabatteurs? Ramasse-le avant eux, vite!", 2,
               jeu="[surprised] Il l'a laissé au terminus pour les rabatteurs? [firmly] Ramasse-le avant eux, vite!")
        ],
        "accueil": [
            _a("norbert", "Je crains que la suite royale ne soit pas libre. Son locataire paie d'avance, en billets pliés en quatre.", 0,
               jeu="[calm] Je crains que la suite royale ne soit pas libre. [knowingly] Son locataire paie d'avance… en billets pliés en quatre."),
            _a("norbert", "Son comptable sort par ici chaque soir, un livre sous le bras. Monsieur ne tient pas ce renseignement de moi.", 0,
               jeu="[quietly] Son comptable sort par ici chaque soir, un livre sous le bras. [calm] Monsieur ne tient pas ce renseignement de moi.")
        ],
        "fin": [
            _l("irene", "« Chan, trois mille deux cents. Boulangerie, un camion. » Il a une belle main d'écriture, pour un voleur.",
               jeu="[bitterly] « Chan, trois mille deux cents. Boulangerie, un camion. » [sarcastic] Il a une belle main d'écriture, pour un voleur."),
            _l("irene", "Pis en bas de la page, ce qu'il doit à ses rabatteurs. Il les paye même pas.",
               jeu="[amused] Pis en bas de la page, ce qu'il doit à ses rabatteurs. [wryly] Il les paye même pas."),
            _l("irene", "Garde le livre. Demain, on va lui présenter sa facture.",
               jeu="[firmly] Garde le livre. [satisfied] Demain… on va lui présenter sa facture.")
        ],
        "echec": [
            _l("irene", "Le livre nous a filé entre les doigts. La chance, ça existe pas : on était juste pas là.",
               jeu="[disappointed] Le livre nous a filé entre les doigts. [wryly] La chance, ça existe pas… on était juste pas là.")
        ]
    },

    # Intention (intro) : Irène au bout du bar, bras croisés, pose la règle du tricheur ; la caméra sort voir
    # l'hôtel — loin, au sud-ouest, où dort le Pouce — pendant qu'elle envoie le neveu chez le concierge ; et elle
    # finit sur les voisins, c'est pour eux. ⚠️ La coupe en `ensemble`, PUIS la réplique : la voix retient la scène.
    # Intention (fin) : à sa porte, au combiné, elle lit le livre à voix haute.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:hotel", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:irene", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },
}
