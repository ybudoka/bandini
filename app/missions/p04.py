"""La mission p04 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "p04",
    "titre": "Zed veut un défi",
    "donneur": "zed",
    "prerequis": ["p02"],
    "recompense": 200,
    # ⚠️ `calme` (M16) : les Skateux te respectent — tu as battu le temps de leur chef, à pied, dans leur coin.
    "donne": {"calme": "skateux", "message": "LES SKATEUX TE RESPECTENT"},

    # ⚠️ LA PREMIÈRE `course` D'UNE MISSION (29 sept. 2026) : quatre points de La Pointe dans l'ordre — le
    # stationnement des Skateux, l'arche de la foire, le pont, le phare —, à pied (`a_pied`), sous le chrono de Zed
    # (`chrono_s`) : 80 s pour ≈ 324 tuiles de sentiers (mesuré au banc, un parcours en largeur sur les tuiles où l'on
    # marche) — 33 s au sprint, 43 à la course, 72 au pas : il faut courir, pas voler. La fiche voulait Zed qui court à côté (`contre`) : `contre` n'est lu par personne, et un coureur
    # qui suit les sentiers est un moteur à lui seul. On bat donc SON temps : c'est lui qui l'a fixé.
    "objectifs": [
        {"type": "course", "texte": "BATS LE TEMPS DE ZED, À PIED",
         "points": ["zone:skateux", "foire", "pont", "phare"], "a_pied": True, "chrono_s": 80},

        {"type": "retourner", "texte": "RETOURNE VOIR ZED, DEVANT LE PHARE"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Zed : le rieur. Tout est drôle, surtout ce qui ne l'est pas ; il dit
    # « man », il ricane en finissant ses phrases. Il perd bien — c'est ce qui en fait un chef.
    "dialogue": {
        "appel": [
            _l("zed", "Yo, c'est Zed, des Skateux. Paraît que t'as nettoyé le pont. Viens voir si tu cours aussi vite que tu frappes.",
               jeu="[playfully] Yo, c'est Zed, des Skateux. [amused] Paraît que t'as nettoyé le pont… Viens voir si tu cours aussi vite que tu frappes.")
        ],
        "intro": [
            _l("zed", "Notre parcours : le stationnement, la foire, le pont, pis retour au phare. À pied, man.",
               jeu="[excited] Notre parcours : le stationnement, la foire, le pont, pis retour au phare. [teasing] À pied, man."),
            _l("zed", "Mon record, c'est une minute vingt. Personne l'a jamais battu.",
               jeu="[smugly] Mon record, c'est une minute vingt. [laughs] Personne l'a jamais battu."),
            _l("zed", "Tu le bats, les Skateux te laissent tranquille. Go!",
               jeu="[mischievously] Tu le bats, les Skateux te laissent tranquille. [shouting] Go!")
        ],
        "pendant": [
            _p("zed", "Cours, man! Le chrono attend personne!", 0,
               jeu="[excited] Cours, man! [laughs] Le chrono attend personne!"),
            _p("zed", "Non! T'as battu mon temps? Reviens au phare, faut que je voie ta face.", 1,
               jeu="[surprised] Non! T'as battu mon temps? [amused] Reviens au phare, faut que je voie ta face.")
        ],
        "fin": [
            _l("zed", "Ha! Un vieux qui court. Les gars vont rire de moi une semaine.",
               jeu="[laughs] [amused] Ha! Un vieux qui court. Les gars vont rire de moi une semaine."),
            _l("zed", "Correct, man. Les Skateux te toucheront plus. Parole de Skateux.",
               jeu="[warmly] Correct, man. [confident] Les Skateux te toucheront plus. Parole de Skateux.")
        ],
        "echec": [
            _l("zed", "Trop lent, man! Reviens quand t'auras des souliers.",
               jeu="[laughs] [teasing] Trop lent, man! Reviens quand t'auras des souliers.")
        ]
    }
}
