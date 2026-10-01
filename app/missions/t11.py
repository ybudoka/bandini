"""La mission t11 — voir app/missions/__init__.py pour le moteur.

Le feu de camp (M16, arc T, les petites jobs — 1er oct. 2026). Un promeneur de La Pointe : des jeunes ont fait un feu
de camp « pour se réchauffer » collé sur la remise du phare, et ça prend. L'extincteur qu'il traîne dans son sac à
dos (« on sait jamais »), le feu (`eteindre`, le feu de la mission), puis lui. Un passant qui donne une job
(`passant`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t11",
    "titre": "Le feu de camp",
    "donneur": "passant",
    "prerequis": ["m6"],
    "recompense": 50,
    "passant": {"archetype": "promeneur", "district": "pointe", "nom": "Le promeneur"},
    "donne": {"message": "LA REMISE DU PHARE EST SAUVÉE"},

    # Le feu de la mission prend sur la façade la plus proche du phare (un lieu de mission déjà : rien ne bouge), et le
    # promeneur te met son extincteur dans les mains (`remet`, le patron de f13).
    "objectifs": [
        {"type": "eteindre", "texte": "LE FEU DE CAMP PREND SUR LA REMISE DU PHARE : ÉTEINS-LE", "ou": "phare",
         "remet": "extincteur"},
        {"type": "retourner", "texte": "RENDS SON EXTINCTEUR AU PROMENEUR"},
    ],

    # Le jeu (`jeu=`) — le promeneur : prévoyant jusqu'au ridicule, et ravi qu'enfin, ça serve.
    "dialogue": {
        "hele": [
            _l("passant", "Au feu! Toi!", jeu="[worried] Au feu! Toi!")
        ],
        "intro": [
            _l("passant", "Des jeunes ont fait un feu de camp collé sur la remise du phare. Pour se réchauffer, qu'ils disent.",
               jeu="[worried] Des jeunes ont fait un feu de camp collé sur la remise du phare. [sarcastic] Pour se réchauffer, qu'ils disent."),
            _l("passant", "Tiens, mon extincteur. Je le traîne dans mon sac à dos depuis neuf ans. On sait jamais.",
               jeu="[excited] Tiens, mon extincteur. [confident] Je le traîne dans mon sac à dos depuis neuf ans. On sait jamais.")
        ],
        "pendant": [
            _p("passant", "Vise le bas des flammes! C'est écrit sur l'étiquette, je l'ai lue souvent.", 0,
               jeu="[shouting] Vise le bas des flammes! [playfully] C'est écrit sur l'étiquette, je l'ai lue souvent."),
            _p("passant", "Neuf ans que j'attendais ça. Rapporte-le, il a une valeur sentimentale.", 1,
               jeu="[happy] Neuf ans que j'attendais ça. [tenderly] Rapporte-le, il a une valeur sentimentale.")
        ],
        "fin": [
            _l("passant", "Il a servi! Ma femme disait que j'étais fou. Cinquante piasses, pis j'en rachète un.",
               jeu="[excited] Il a servi! [amused] Ma femme disait que j'étais fou. [warmly] Cinquante piasses, pis j'en rachète un.")
        ],
        "echec": [
            _l("passant", "La remise est partie en fumée. Neuf ans pour rien.",
               jeu="[somber] La remise est partie en fumée. [sighs] Neuf ans pour rien.")
        ]
    }
}
