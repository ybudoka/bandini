"""La mission q02 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "q02",
    "titre": "Le poisson du vendredi",
    "donneur": "lulu",
    # ⚠️ Après e01 (Ti-Paul dit d'aller la voir) : le plan la voulait après q01, qui n'existe pas encore.
    "prerequis": ["e01"],
    "recompense": 250,
    "echec": ["arrete", "vehicule_detruit"],
    "donne": {"message": "LE POISSON EST ARRIVÉ ENTIER"},

    # ⚠️ Lulu se tient DEDANS (cantine) : rien de la ville ne se pose avant la sortie, mais un char
    # de mission se pose dès le début (`Histoire.poser`) — la coupe de l'intro (celle du défaut : le
    # premier lieu que nomme un objectif) filme donc la ruelle et son camion, pas une ruelle vide.
    # `sans_degats` : une prime de moitié en plus si le camion n'a pas une bosse.
    "objectifs": [
        {"type": "monter", "texte": "PRENDS LE CAMION DE POISSON DANS LA RUELLE",
         "vehicule": "camion", "ou": "ruelle:cantine:10"},

        {"type": "livrer", "texte": "LIVRE LE POISSON AU CASSE-CROÛTE, SANS BOSSE",
         "lieu": "casse_croute", "rayon": 4, "sans_degats": True}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Lulu, le poisson du vendredi : la cantinière qui
    # materne et qui taquine — l'urgence est drôle (un camion de morue), jamais grave. La fin
    # passe la main à Raymonde, avec un clin d'œil.
    "dialogue": {
        "appel": [
            _l("lulu", "Lulu, à la cantine! J'ai un camion de poisson sans chauffeur, pis c'est vendredi. Viens vite!",
               jeu="[excited] Lulu, à la cantine! J'ai un camion de poisson sans chauffeur… pis c'est vendredi. Viens vite!")
        ],
        "intro": [
            _l("lulu", "Le camion est dans une ruelle, plein de morue. Le chauffeur s'est pogné la main dans sa glacière.",
               jeu="[warmly] Le camion est dans une ruelle, plein de morue. [amused] Le chauffeur s'est pogné la main… dans sa glacière."),
            _l("lulu", "Livre-le au casse-croûte du Faubourg. Pis conduis doucement: le poisson, ça se bosse pas.",
               jeu="[firmly] Livre-le au casse-croûte du Faubourg. [teasing] Pis conduis doucement… le poisson, ça se bosse pas.")
        ],
        "pendant": [
            # Au combiné : elle est à la cantine, on est au volant.
            _p("lulu", "Doucement dans les tournants! Le sergent veut son poisson frais, pas en purée.", 1,
               jeu="[worried] Doucement dans les tournants! [playfully] Le sergent veut son poisson frais… pas en purée.")
        ],
        "fin": [
            _l("lulu", "Pas une écaille de perdue! Le sergent va être content, pis moi, j'suis payée.",
               jeu="[relieved] Pas une écaille de perdue! [cheerful] Le sergent va être content, pis moi, j'suis payée."),
            _l("lulu", "Passe voir Raymonde, à l'usine. Elle cherche quelqu'un qui conduit bien, pis qui pose pas de questions.",
               jeu="[knowingly] Passe voir Raymonde, à l'usine. Elle cherche quelqu'un qui conduit bien… pis qui pose pas de questions.")
        ],
        "echec": [
            _l("lulu", "Mon poisson… Ben tant pis, on va le faire en soupe. Reviens quand tu conduis mieux.",
               jeu="[disappointed] Mon poisson… Ben tant pis, on va le faire en soupe. [teasing] Reviens quand tu conduis mieux.")
        ]
    },

    # Intention (intro) : le joueur voit le camion pendant que Lulu le nomme (« dans une ruelle, plein
    # de morue »), et la caméra revient à la cantine pour la blague du chauffeur ; elle croise les bras,
    # elle donne l'ordre. ⚠️ Elle parle DEDANS : c'est la forme du défaut, SAUF que la coupe part
    # `ensemble` avec la première réplique au lieu de la retenir — la voix dure 9,3 s, la coupe 4 s, et
    # la seconde réplique la coupait en plein « pogné la main ». Le `dire` retient la scène jusqu'au bout
    # de sa voix. La coupe (240 images) revient juste avant « Le chauffeur » (4,1 s).
    # La fin reste celle du défaut : on est au casse-croûte et elle à sa cantine, une coupe chez elle.
    "scenes": {
        "intro": [
            { "type": "coupe", "vers": "ruelle:cantine:10", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True },
            { "type": "dire", "repliques": [1] },
            { "type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True },
            { "type": "dire", "repliques": [2] }
        ]
    }
}
