"""La mission s04 — voir app/missions/__init__.py pour le moteur.

Le quart de nuit (M16, arc S, 1er oct. 2026). La Shop est en paix (s11), l'usine a rouvert, et la paie du quart de
nuit arrive en argent comptant à la caisse populaire — Prévost n'a jamais cru aux chèques. Raymonde t'envoie la
chercher (`aller`) ; les Cravates, chassés du Faubourg, ont flairé l'enveloppe et arrivent de partout (`tuer`, `loin`,
`renforts`) ; leur chef a un couteau ; puis la paie à Raymonde, à la porte de l'usine (`retourner`).

⚠️ Écarts à la fiche : Bob Sauvé n'est pas un personnage (et il a vendu le syndicat, s06) — Raymonde donne la job ;
huit hommes, oui, mais en trois vagues et leur chef ; on ne « survit » pas à la porte de l'usine (elle n'est jamais un
lieu de mission : sa cour ferme la nuit) — on porte la paie.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "s04",
    "titre": "Le quart de nuit",
    "donneur": "raymonde",
    "prerequis": ["s11"],
    "recompense": 300,
    "donne": {"message": "LE QUART DE NUIT A SA PAIE"},

    "objectifs": [
        {"type": "aller", "texte": "LA PAIE DU QUART DE NUIT, À LA CAISSE POP", "lieu": "caisse_pop", "rayon": 6},

        {"type": "tuer", "texte": "DES CRAVATES ONT FLAIRÉ L'ENVELOPPE — COUCHE-LES",
         "groupe": "cravates", "n": 3, "loin": 12, "renforts": {"vagues": 2, "n": 2}},

        {"type": "tuer", "texte": "LEUR CHEF A UN COUTEAU — COUCHE-LE",
         "groupe": "cravates", "n": 1, "chef": True, "arme": "couteau", "vie": 180, "loin": 10},

        {"type": "retourner", "texte": "LA PAIE À RAYMONDE, À LA PORTE DE L'USINE"},
    ],

    # Intention (intro) : Raymonde qui compte déjà les heures du quart de nuit ; la caméra va voir la caisse populaire
    # (l'enveloppe y attend), puis revient pour ce qu'elle sait sans le dire — l'argent comptant attire les rats.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:caisse_pop", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Raymonde : ferme, sèche, l'ironie de la vieille militante ; elle ne
    # remercie pas, elle constate.
    "dialogue": {
        "appel": [
            _l("raymonde", "Raymonde Fortin. Le quart de nuit a pas été payé depuis deux semaines. Ça finit ce soir.",
               jeu="[firmly] Raymonde Fortin. [annoyed] Le quart de nuit a pas été payé depuis deux semaines. [firmly] Ça finit ce soir.")
        ],
        "intro": [
            _l("raymonde", "Prévost croit pas aux chèques. La paie arrive en argent comptant, à la caisse pop.",
               jeu="[wryly] Prévost croit pas aux chèques. [matter-of-fact] La paie arrive en argent comptant, à la caisse pop."),
            _l("raymonde", "Une enveloppe brune, quarante-deux noms dessus. Va la chercher au guichet.",
               jeu="[matter-of-fact] Une enveloppe brune, quarante-deux noms dessus. [firmly] Va la chercher au guichet."),
            _l("raymonde", "Pis ouvre l'œil. De l'argent comptant dans La Shop, ça attire les rats.",
               jeu="[serious] Pis ouvre l'œil. [wryly] De l'argent comptant dans La Shop, ça attire les rats.")
        ],
        "pendant": [
            _p("raymonde", "La caisse pop, au bout de la rue des pièces d'auto. Le gérant t'attend.", 0,
               jeu="[matter-of-fact] La caisse pop, au bout de la rue des pièces d'auto. [firmly] Le gérant t'attend."),
            _p("raymonde", "Des Cravates? Ici? Ils ont perdu leur quartier, pas leur flair.", 1,
               jeu="[annoyed] Des Cravates? Ici? [wryly] Ils ont perdu leur quartier, pas leur flair."),
            _p("raymonde", "Leur chef a sorti un couteau. Garde tes distances, pis l'enveloppe.", 2,
               jeu="[serious] Leur chef a sorti un couteau. [firmly] Garde tes distances, pis l'enveloppe."),
            _p("raymonde", "Amène-moi ça à la porte. Le quart commence dans dix minutes.", 3,
               jeu="[firmly] Amène-moi ça à la porte. [matter-of-fact] Le quart commence dans dix minutes.")
        ],
        "fin": [
            _l("raymonde", "Quarante-deux noms, quarante-deux enveloppes. Pas une cenne de moins.",
               jeu="[satisfied] Quarante-deux noms, quarante-deux enveloppes. [firmly] Pas une cenne de moins."),
            _l("raymonde", "Tiens, ta part. Le syndicat paie ses dettes, lui.",
               jeu="[matter-of-fact] Tiens, ta part. [wryly] Le syndicat paie ses dettes, lui.")
        ],
        "echec": [
            _l("raymonde", "Pas de paie, pas de quart. Prévost va dire que c'est notre faute, comme d'habitude.",
               jeu="[bitterly] Pas de paie, pas de quart. [wryly] Prévost va dire que c'est notre faute, comme d'habitude.")
        ]
    }
}
