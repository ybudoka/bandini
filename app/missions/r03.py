"""La mission r03 — voir app/missions/__init__.py pour le moteur.

Le stool, c'est toi (M16, arc R, 30 sept. 2026) — un côté du CHOIX de l'arc (`ferme: r04`). On travaille pour Roy.
Chaque midi, Mado glisse une enveloppe au sergent avec son café — le « loyer » du casse-croûte. Roy veut savoir où
elle va. On fait jaser Mado (elle en a assez de payer), on file le char de Bouchard sans qu'il nous voie — il porte
l'enveloppe au maire, à l'Hôtel Bandini —, et on revient le dire à Roy. Elle efface cinq pages du casier ; le
sergent, lui, ne sera plus jamais ton ami.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "r03",
    "titre": "Le stool, c'est toi",
    "donneur": "roy",
    "prerequis": ["r02"],
    "ferme": "r04",
    "recompense": 500,
    "donne": {"casier": -5, "message": "ROY EFFACE CINQ PAGES — BOUCHARD NE T'OUBLIERA PAS"},

    # ⚠️ `suivre` (le patron de h02 et e06) : son `lieu` est l'hôtel, déjà lieu de mission — la ville ne glisse pas.
    # Mado se tient dehors (`porte:casse_croute`) : sa poignée de main se dit. Roy est dedans : la fin, au poste.
    "objectifs": [
        {"type": "parler", "texte": "MADO PAIE LE SERGENT CHAQUE MIDI : FAIS-LA JASER", "cible": "mado"},

        {"type": "suivre", "texte": "SUIS LE CHAR DU SERGENT SANS TE FAIRE VOIR",
         "vehicule": "police", "loin": 10, "proche": 3, "lieu": "hotel"},

        {"type": "parler", "texte": "L'ENVELOPPE VA AU MAIRE : DIS-LE À ROY", "cible": "roy"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:casse_croute", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Roy : le plaisir contenu de tenir enfin un fil ; précise. Mado : la
    # colère d'une femme qui paie depuis trop longtemps, et qui se soulage en le disant.
    "dialogue": {
        "appel": [
            _l("roy", "C'est Roy. T'as choisi le bon bord, astheure prouve-le. Viens au poste.",
               jeu="[firmly] C'est Roy. [calm] T'as choisi le bon bord, astheure prouve-le. Viens au poste.")
        ],
        "intro": [
            _l("roy", "Chaque midi, la patronne du casse-croûte glisse une enveloppe à Bouchard, avec son café.",
               jeu="[matter-of-fact] Chaque midi, la patronne du casse-croûte glisse une enveloppe à Bouchard, avec son café."),
            _l("roy", "Fais-la parler. Ensuite, suis le sergent. Je veux savoir qui finit avec l'argent.",
               jeu="[serious] Fais-la parler. Ensuite, suis le sergent. [coldly] Je veux savoir qui finit avec l'argent."),
            _l("roy", "S'il te voit, c'est fini pour toi pis pour mon enquête. Reste loin.",
               jeu="[firmly] S'il te voit, c'est fini pour toi pis pour mon enquête. [quietly] Reste loin.")
        ],
        "pendant": [
            _p("roy", "Elle a peur de lui. Sois doux, c'est une bonne femme.", 0,
               jeu="[softly] Elle a peur de lui. [calm] Sois doux, c'est une bonne femme."),
            _p("roy", "Il part. Garde deux coins de rue entre vous deux.", 1,
               jeu="[quietly] Il part. [firmly] Garde deux coins de rue entre vous deux."),
            _p("roy", "L'hôtel? Évidemment. Reviens me voir, pis parle à personne en chemin.", 2,
               jeu="[wryly] L'hôtel? Évidemment. [serious] Reviens me voir, pis parle à personne en chemin.")
        ],
        "accueil": [
            _a("mado", "L'enveloppe? Deux cents par semaine, mon grand, depuis six ans. Il appelle ça la protection.", 0,
               jeu="[worried] L'enveloppe? Deux cents par semaine, mon grand, depuis six ans. [bitterly] Il appelle ça la protection.")
        ],
        "fin": [
            _l("roy", "Le sergent paie le maire avec l'argent de Mado. Ça, c'est une enquête.",
               jeu="[satisfied] Le sergent paie le maire avec l'argent de Mado. [serious] Ça, c'est une enquête."),
            _l("roy", "Je t'efface cinq pages. Pis dorénavant, marche loin du casse-croûte : Bouchard sait.",
               jeu="[calm] Je t'efface cinq pages. [serious] Pis dorénavant, marche loin du casse-croûte : Bouchard sait.")
        ],
        "echec": [
            _l("roy", "Il t'a vu. Mon enquête vient de reculer de six mois.",
               jeu="[coldly] Il t'a vu. [disappointed] Mon enquête vient de reculer de six mois.")
        ]
    }
}
