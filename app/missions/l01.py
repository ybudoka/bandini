"""La mission l01 — voir app/missions/__init__.py pour le moteur.

Une photo pour la une (M16, arc C « Le Clairon », 30 sept. 2026). Louise n'a plus de photographe ni de char : le
Clairon ne paie ni l'un ni l'autre. Elle veut une série — « Baie-des-Brumes, une journée » — et commence par la
plus risquée : le sergent Bouchard devant son poste. Il n'aime pas les photos ; ses agents non plus. On la mène au
poste, on sème ceux qui la reconnaissent, et on finit au port, où la lumière du soir tombe sur la cantine.

⚠️ L'arc C de la fiche s'écrit `l01`–`l06` : les slugs `c01`–`c08` sont pris (Irène, le vieux maître).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "l01",
    "titre": "Une photo pour la une",
    "donneur": "louise",
    "prerequis": ["m6"],
    "recompense": 150,
    "donne": {"message": "LA UNE DE DEMAIN EST DANS L'APPAREIL DE LOUISE"},

    # ⚠️ Louise est DEHORS (`porte:kiosque`) : `proteger` reprend la même entité (le Bonimenteur de p14), elle nous
    # suit toute la mission. Le retour n'est pas un `retourner` (elle est à côté de nous) : on finit au port, et la
    # fin se dit devant elle.
    "objectifs": [
        {"type": "proteger", "texte": "MÈNE LOUISE AU POSTE : ELLE VEUT BOUCHARD EN PHOTO",
         "cible": "louise", "lieu": "poste", "rayon": 5},

        {"type": "semer", "texte": "LES AGENTS N'AIMENT PAS LES PHOTOS : SÈME-LES", "etoiles": 1},

        {"type": "aller", "texte": "LA LUMIÈRE DU SOIR AU PORT : LA CANTINE",
         "lieu": "cantine", "rayon": 6},
    ],

    # Intention (intro) : Louise au kiosque, l'appareil au cou, qui parle en manchettes — sa réplique tient le plan ;
    # la coupe montre le poste sous la deuxième. La fin, au port : elle vient à nous, montre la cantine, sourit.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:poste", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
        "fin": [
            {"type": "marcher", "acteur": "donneur", "vers": "joueur", "pres": 22, "duree": 50},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "porte:cantine", "duree": 70,
             "ensemble": True},
            {"type": "dire", "repliques": [2]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Louise : vive, pince-sans-rire, en phrases de manchette ; « mon beau »
    # quand elle taquine. Elle a peur de Bouchard et le dit en riant.
    "dialogue": {
        "appel": [
            _l("louise", "Louise, du Clairon. J'ai une série à faire pis pas de chauffeur. T'es libre, mon beau?",
               jeu="[confident] Louise, du Clairon. J'ai une série à faire pis pas de chauffeur. [teasing] T'es libre, mon beau?")
        ],
        "intro": [
            _l("louise", "« Baie-des-Brumes, une journée. » Six photos, six coins de ville. On commence par le pire.",
               jeu="[excited] « Baie-des-Brumes, une journée. » Six photos, six coins de ville. [wryly] On commence par le pire."),
            _l("louise", "Le sergent Bouchard devant son poste, la bedaine au soleil. Il va détester ça.",
               jeu="[amused] Le sergent Bouchard devant son poste, la bedaine au soleil. [mischievously] Il va détester ça."),
            _l("louise", "Tu conduis, je shoote. Pis si ça tourne mal, tu conduis plus vite.",
               jeu="[confident] Tu conduis, je shoote. [wryly] Pis si ça tourne mal, tu conduis plus vite.")
        ],
        "pendant": [
            _p("louise", "Arrête-toi pas trop près. Une photo volée, c'est de loin.", 0,
               jeu="[quietly] Arrête-toi pas trop près. [knowingly] Une photo volée, c'est de loin."),
            _p("louise", "Il m'a vue! Pis il a pas aimé son profil. Décolle!", 1,
               jeu="[excited] Il m'a vue! [amused] Pis il a pas aimé son profil. [shouting] Décolle!"),
            _p("louise", "Au port, astheure. La lumière du soir sur la cantine, c'est ma dernière de la journée.", 2,
               jeu="[calm] Au port, astheure. [warmly] La lumière du soir sur la cantine, c'est ma dernière de la journée.")
        ],
        "fin": [
            _l("louise", "Regarde-moi ça. Bouchard en furie, pis le port qui dort. C'est la une.",
               jeu="[excited] Regarde-moi ça. Bouchard en furie, pis le port qui dort. [satisfied] C'est la une."),
            _l("louise", "Tiens, pour l'essence. Le Clairon paie mal, mais il paie comptant.",
               jeu="[wryly] Tiens, pour l'essence. [confident] Le Clairon paie mal, mais il paie comptant.")
        ],
        "echec": [
            _l("louise", "Pas de photo, pas de une. Demain, le Clairon imprime la météo en gros.",
               jeu="[disappointed] Pas de photo, pas de une. [sarcastic] Demain, le Clairon imprime la météo en gros.")
        ]
    }
}
