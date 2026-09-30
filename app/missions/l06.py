"""La mission l06 — voir app/missions/__init__.py pour le moteur.

L'entrevue (M16, arc C, 30 sept. 2026 — la « c06 » de la fiche). Trois quartiers ont changé de mains, et toute la
ville se demande qui est le neveu de Rocco. Louise veut l'entrevue — la vraie, pas une photo volée —, et elle la
veut au bout de la ville, au phare, là où personne n'écoute. On l'y mène ; au pied du phare, trois questions,
trois réponses. Le Clairon du lendemain titre _Le neveu parle_ : c'est la dernière de l'arc.

⚠️ La fiche voulait « trois réponses au choix » : le moteur ne connaît pas de choix dans un dialogue (seulement
`ferme`, entre deux missions). Les trois réponses sont écrites, et le Clairon les imprime.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "l06",
    "titre": "L'entrevue",
    "donneur": "louise",
    "prerequis": ["l05"],
    "exige": {"liberes": 3},
    "recompense": 100,
    "donne": {"manchette": "le_neveu_parle", "message": "DEMAIN, LE CLAIRON PUBLIE TON ENTREVUE"},

    # ⚠️ Louise est dehors : `proteger` la reprend telle quelle, elle nous suit jusqu'au phare, et la fin se dit devant
    # elle (le patron de d01) — ses trois questions, la réponse du neveu est la prime.
    "objectifs": [
        {"type": "proteger", "texte": "L'ENTREVUE SE FAIT AU PHARE : MÈNE LOUISE",
         "cible": "louise", "lieu": "phare", "rayon": 5},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:phare", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "marcher", "acteur": "donneur", "vers": "joueur", "pres": 22, "duree": 50},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 40},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 40},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "porte:phare", "duree": 60,
             "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Louise : pas de taquinerie, pour une fois ; la journaliste au travail,
    # lente, qui laisse des silences (les `attendre` de la fin, jamais dans le mp3).
    "dialogue": {
        "appel": [
            _l("louise", "C'est Louise. Trois quartiers ont changé de mains, pis tout le monde me demande qui t'es. L'entrevue?",
               jeu="[serious] C'est Louise. Trois quartiers ont changé de mains, pis tout le monde me demande qui t'es. [curious] L'entrevue?")
        ],
        "intro": [
            _l("louise", "Pas une photo volée, cette fois. Une vraie entrevue, avec ton nom en bas.",
               jeu="[serious] Pas une photo volée, cette fois. [warmly] Une vraie entrevue, avec ton nom en bas."),
            _l("louise", "Au phare. Au bout du monde, personne écoute, même pas la police.",
               jeu="[quietly] Au phare. [calm] Au bout du monde, personne écoute, même pas la police."),
            _l("louise", "Trois questions. Tu réponds ce que tu veux, j'imprime ce que tu dis.",
               jeu="[firmly] Trois questions. [serious] Tu réponds ce que tu veux, j'imprime ce que tu dis.")
        ],
        "pendant": [
            _p("louise", "Prends le chemin long. J'aime ça, voir la ville que tu as changée.", 0,
               jeu="[calm] Prends le chemin long. [softly] J'aime ça, voir la ville que tu as changée.")
        ],
        "fin": [
            _l("louise", "Un : pourquoi t'es resté? Deux : Rocco, il te manque? Trois : qu'est-ce que tu veux?",
               jeu="[serious] Un : pourquoi t'es resté? [softly] Deux : Rocco, il te manque? [curious] Trois : qu'est-ce que tu veux?"),
            _l("louise", "Parce que la ville était à personne, oui des fois, pis qu'on me laisse travailler. C'est noté.",
               jeu="[quietly] Parce que la ville était à personne, oui des fois, pis qu'on me laisse travailler. [calm] C'est noté."),
            _l("louise", "Demain matin, « Le neveu parle ». Merci. Pis ça, c'est pour ton temps.",
               jeu="[warmly] Demain matin, « Le neveu parle ». Merci. [softly] Pis ça, c'est pour ton temps.")
        ],
        "echec": [
            _l("louise", "Pas d'entrevue. Le Clairon va continuer à inventer ta légende.",
               jeu="[disappointed] Pas d'entrevue. [wryly] Le Clairon va continuer à inventer ta légende.")
        ]
    }
}
