"""La mission r08 — voir app/missions/__init__.py pour le moteur.

La patrouille de Roy (M16, arc R, 30 sept. 2026). Du côté de Roy (après r03). Le poste manque de monde depuis que
Bouchard a « mis au repos » ses hommes les moins fiables. Roy prête une auto-patrouille au neveu, avec sa
bénédiction : trois suspects à rattraper (le boulot `patrouille` du klaxon), puis elle rend ce qu'elle a promis —
deux pages du casier.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "r08",
    "titre": "La patrouille de Roy",
    "donneur": "roy",
    "prerequis": ["r03"],
    "recompense": 250,
    "donne": {"casier": -2, "message": "ROY T'A PRÊTÉ UNE AUTO-PATROUILLE — ET DEUX PAGES DE MOINS"},

    # ⚠️ `boulots` (le patron de h01, s02) : le compte part de l'objectif — seuls les suspects rattrapés pendant la
    # mission comptent. L'auto-patrouille est posée devant le poste (`monter`).
    "objectifs": [
        {"type": "monter", "texte": "L'AUTO-PATROUILLE DE ROY, DEVANT LE POSTE",
         "vehicule": "police", "ou": "porte:poste"},

        {"type": "boulots", "texte": "TROIS SUSPECTS : KLAXONNE, RATTRAPE-LES", "n": 3, "sorte": "patrouille"},

        {"type": "parler", "texte": "RENDS LES CLÉS À ROY, AU POSTE", "cible": "roy"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:poste", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    "dialogue": {
        "appel": [
            _l("roy", "Roy. Il me manque trois agents ce soir, pis j'ai une auto qui dort. T'es libre?",
               jeu="[matter-of-fact] Roy. Il me manque trois agents ce soir, pis j'ai une auto qui dort. [curious] T'es libre?")
        ],
        "intro": [
            _l("roy", "Bouchard a mis ses hommes « au repos ». Moi, j'appelle ça une grève de la paresse.",
               jeu="[coldly] Bouchard a mis ses hommes « au repos ». [wryly] Moi, j'appelle ça une grève de la paresse."),
            _l("roy", "L'auto est devant. Klaxonne quand t'en vois un, pis rattrape-le. Vivant.",
               jeu="[firmly] L'auto est devant. Klaxonne quand t'en vois un, pis rattrape-le. [serious] Vivant."),
            _l("roy", "Trois, pis tu me rends les clés. Je t'efface deux pages, c'est ton salaire.",
               jeu="[matter-of-fact] Trois, pis tu me rends les clés. [calm] Je t'efface deux pages, c'est ton salaire.")
        ],
        "pendant": [
            _p("roy", "Les clés sont dessus. Pis la sirène, t'y touches pas pour le plaisir.", 0,
               jeu="[firmly] Les clés sont dessus. [matter-of-fact] Pis la sirène, t'y touches pas pour le plaisir."),
            _p("roy", "Un suspect, c'est un suspect. Tu le couches pas, tu l'arrêtes.", 1,
               jeu="[serious] Un suspect, c'est un suspect. [firmly] Tu le couches pas, tu l'arrêtes."),
            _p("roy", "Trois. C'est plus que Bouchard en un mois. Rapporte-moi les clés.", 2,
               jeu="[impressed] Trois. C'est plus que Bouchard en un mois. [calm] Rapporte-moi les clés.")
        ],
        "fin": [
            _l("roy", "Trois arrestations, zéro plainte. Deux pages de moins, comme promis.",
               jeu="[satisfied] Trois arrestations, zéro plainte. [calm] Deux pages de moins, comme promis."),
            _l("roy", "Si un jour tu veux faire ça pour vrai, l'école de police prend les vieux aussi.",
               jeu="[wryly] Si un jour tu veux faire ça pour vrai, [softly] l'école de police prend les vieux aussi.")
        ],
        "echec": [
            _l("roy", "Mon auto est cabossée, pis mes suspects courent. Donne-moi les clés.",
               jeu="[annoyed] Mon auto est cabossée, pis mes suspects courent. [coldly] Donne-moi les clés.")
        ]
    }
}
