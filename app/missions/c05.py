"""La mission c05 — voir app/missions/__init__.py pour le moteur.

Le retour du vieux maître (docs/jalons/l-ecole-rivale.md, vague 2 — Martin, 29 sept. 2026 : « les deux »). Le Pouce
tombé, Irène a un autre compte à régler : trois Mantes veulent un « droit de table » au club de mah-jong. Elle a appelé
en Floride. Victor Tam, le vieux maître de l'ÉCOLE LA MANTE — le seul qui l'ait jamais battue au mah-jong — est revenu
hier soir par l'autobus, bronzé. On va le voir à son école ; il t'envoie chercher ses trois frimeurs par l'oreille.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "c05",
    "titre": "Le droit de table",
    "donneur": "irene",
    "prerequis": ["c04"],
    "recompense": 500,
    "donne": {"message": "LE CLUB DE MAH-JONG A RAVOIR SES TUILES"},

    # ⚠️ Irène est DEDANS (`point:irene`), et le maître aussi (`point:maitre`, dans son école) : `parler` le trouve dans
    # sa salle, comme Norbert à l'hôtel (c03) — sa poignée de main se dit (`accueil`), et il se nomme là, la première
    # fois qu'on l'entend. Les trois frimeurs attendent sur LEUR territoire (`zone:mantes`, le coin de l'école) : des
    # poings seulement, et moins de vie qu'un Mante de rue — ce sont des gamins qui font les fanfarons, pas des
    # champions. La fin se dit chez Irène, par une coupe.
    "objectifs": [
        {"type": "parler", "texte": "VA VOIR LEUR VIEUX MAÎTRE, À L'ÉCOLE LA MANTE", "cible": "maitre"},

        {"type": "tuer", "texte": "RAMÈNE LES TROIS FRIMEURS PAR L'OREILLE",
         "groupe": "mantes", "n": 3, "ou": "zone:mantes", "arme": "", "vie": 70},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Irène : la taquinerie d'abord, puis une vraie colère de voisine (le
    # mah-jong, c'est sa maison), et, en parlant de Victor, une tendresse qu'elle cache sous une gageure. Elle se
    # nomme à l'appel, sèche. Le maître, qu'on entend pour la première fois : la bonhomie d'un homme bronzé qui a
    # trop dormi au soleil, et, sous la blague, la honte d'avoir laissé ses élèves — il se nomme à la poignée de
    # main, à sa façon (« Sifu, pour mes élèves »).
    "dialogue": {
        "appel": [
            _l("irene", "Irène Lam. Les Mantes ont renversé la table du club de mah-jong, pis ça, mon pigeon, c'est personnel.",
               jeu="[coldly] Irène Lam. [bitterly] Les Mantes ont renversé la table du club de mah-jong… pis ça, mon pigeon, c'est personnel.")
        ],
        "intro": [
            _l("irene", "Trois frimeurs en pyjama vert qui veulent un droit de table. Au mah-jong. Chez nous!",
               jeu="[sarcastic] Trois frimeurs en pyjama vert qui veulent un droit de table. [annoyed] Au mah-jong. Chez nous!"),
            _l("irene", "J'ai appelé en Floride. Leur vieux maître, Victor Tam, est revenu hier soir par l'autobus.",
               jeu="[knowingly] J'ai appelé en Floride. [matter-of-fact] Leur vieux maître, Victor Tam, est revenu hier soir par l'autobus."),
            _l("irene", "Trente ans que je joue contre lui. C'est le seul qui m'a jamais battue, pis il le sait.",
               jeu="[wryly] Trente ans que je joue contre lui. [tenderly] C'est le seul qui m'a jamais battue… pis il le sait."),
            _l("irene", "Va le voir à son école. Il est bronzé comme une galette, fais pas le saut.",
               jeu="[amused] Va le voir à son école. [teasing] Il est bronzé comme une galette… fais pas le saut.")
        ],
        "pendant": [
            _p("irene", "L'École La Mante, au nord du quartier. Cogne fort, il a pris le pli de la sieste en Floride.", 0,
               jeu="[teasing] L'École La Mante, au nord du quartier. [amused] Cogne fort… il a pris le pli de la sieste en Floride."),
            _p("maitre", "À mains nues, là. Un élève de la Mante, on le corrige, on le casse pas.", 1,
               jeu="[firmly] À mains nues, là. [warmly] Un élève de la Mante, on le corrige… on le casse pas.")
        ],
        "accueil": [
            _a("maitre", "Victor Tam. Sifu, pour mes élèves, pis pour toi aussi, tant qu'à faire.", 0,
               jeu="[cheerful] Victor Tam. [playfully] Sifu, pour mes élèves… pis pour toi aussi, tant qu'à faire."),
            _a("maitre", "Trois de mes élèves font les fanfarons au mah-jong. Ramène-les-moi par l'oreille, petit scarabée.", 0,
               jeu="[somber] Trois de mes élèves font les fanfarons au mah-jong. [amused] Ramène-les-moi par l'oreille… petit scarabée.")
        ],
        "fin": [
            _l("irene", "Le club a ravoir ses tuiles, pis trois gamins ont une oreille plus longue que l'autre.",
               jeu="[satisfied] Le club a ravoir ses tuiles… [amused] pis trois gamins ont une oreille plus longue que l'autre."),
            _l("irene", "Victor est revenu pour de bon, qu'il dit. Je gage cinq piasses qu'il repart en janvier.",
               jeu="[wryly] Victor est revenu pour de bon, qu'il dit. [teasing] Je gage cinq piasses qu'il repart en janvier."),
            _l("irene", "Va le voir de temps en temps. Il te trouve de l'allure, pis il se trompe rarement.",
               jeu="[warmly] Va le voir de temps en temps. [tenderly] Il te trouve de l'allure… pis il se trompe rarement.")
        ],
        "echec": [
            _l("irene", "Trois gamins en pyjama t'ont eu? J'ai encore perdu cinq piasses sur toi.",
               jeu="[disappointed] Trois gamins en pyjama t'ont eu? [wryly] J'ai encore perdu cinq piasses sur toi.")
        ]
    },

    # Intention (intro) : Irène au bout du bar, les bras croisés, fâchée pour de vrai — le mah-jong, c'est sa maison ;
    # la caméra va voir l'école au bout du quartier pendant qu'elle parle de Victor, et revient sur sa gageure.
    # ⚠️ La coupe en `ensemble`, PUIS la réplique : c'est la voix qui retient la scène (« caler une scène »).
    # Intention (fin) : à sa porte, la gageure de toujours, et la tendresse qu'elle cache dessous.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "chez:maitre", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
            {"type": "dire", "repliques": [4]},
        ],
        "fin": [
            {"type": "coupe", "vers": "chez:irene", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 30},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },
}
