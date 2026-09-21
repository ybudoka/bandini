"""La mission s03 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "s03",
    "titre": "La paie de la Prévost",
    "donneur": "raymonde",
    # ⚠️ Après q02 (Lulu nous envoie à elle) : le plan la voulait après q03, qui n'existe pas encore.
    "prerequis": ["q02"],
    "recompense": 450,
    "echec": ["arrete", "vehicule_detruit"],
    "donne": {"message": "LA PAIE EST AU SYNDICAT"},

    # Le vol, la police, la livraison : la forme de m4 (une auto-patrouille de nuit), mais un camion de
    # jour et deux étoiles.
    # ⚠️ **ELLE NE SE TERMINE PAS À L'USINE, et c'est la règle de la ville qui le veut** : la cour de
    # l'usine ferme la nuit (chaîne, `carte.BARRIERES`), et `test_barrieres.py` refuse qu'un lieu de mission
    # soit enfermé par une barrière d'heure — on ne finirait pas la mission de nuit sans défoncer la
    # chaîne. La paie va donc au bar de Josée (qui garde la caisse), et le mot de Raymonde le dit :
    # « mon usine est surveillée ». Raymonde, elle, dit sa fin de chez elle (la coupe du défaut).
    "objectifs": [
        {"type": "monter", "texte": "PRENDS LE CAMION DE PAIE PRÈS DE L'HÔTEL",
         "vehicule": "camion", "ou": "ruelle:hotel:12"},

        {"type": "semer", "texte": "SÈME LA POLICE, LA PAIE À BORD",
         "etoiles": 2},

        {"type": "livrer", "texte": "LIVRE LA PAIE AU BAR DE JOSÉE",
         "lieu": "bar", "rayon": 4}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Raymonde, la paie de la Prévost : Nadine est rauque,
    # elle ne crie jamais — elle est plus dure posée. Le ton passe de l'amertume (l'intro) à un
    # soulagement qu'elle ne montre qu'à moitié.
    "dialogue": {
        "appel": [
            _l("raymonde", "Raymonde. Prévost retient la paie de mes gars. Viens à l'usine, j'ai une idée pas très légale.",
               jeu="[firmly] Raymonde. Prévost retient la paie de mes gars. [knowingly] Viens à l'usine… j'ai une idée pas très légale.")
        ],
        "intro": [
            _l("raymonde", "Le camion de paie de Prévost dort près de l'Hôtel Bandini. Il le garde pour nous faire plier.",
               jeu="[bitterly] Le camion de paie de Prévost dort près de l'Hôtel Bandini. Il le garde… pour nous faire plier."),
            _l("raymonde", "Prends-le, sème la police, pis amène ça au bar de Josée. Mon usine, elle, est surveillée.",
               jeu="[firmly] Prends-le, sème la police… pis amène ça au bar de Josée. [matter-of-fact] Mon usine, elle, est surveillée.")
        ],
        "pendant": [
            # Au combiné : elle est à l'usine, on est au volant, la police au cul.
            _p("raymonde", "Perds-les avant le bar! Josée aime pas les visiteurs en uniforme.", 1,
               jeu="[firmly] Perds-les avant le bar! [sarcastic] Josée aime pas les visiteurs… en uniforme.")
        ],
        "fin": [
            _l("raymonde", "Toutes les enveloppes y sont. Mes gars vont manger cette semaine.",
               jeu="[relieved] Toutes les enveloppes y sont… [warmly] Mes gars vont manger cette semaine."),
            _l("raymonde", "Prévost va hurler. Laisse-le hurler, moi j'ai jamais eu peur d'un patron.",
               jeu="[firmly] Prévost va hurler. Laisse-le hurler… [wryly] moi j'ai jamais eu peur d'un patron.")
        ],
        "echec": [
            _l("raymonde", "Prévost garde sa paie, pis mes gars gardent leur faim. Reviens quand t'auras réfléchi.",
               jeu="[coldly] Prévost garde sa paie… pis mes gars gardent leur faim. [firmly] Reviens quand t'auras réfléchi.")
        ]
    }

    # ⚠️ ELLE N'ÉCRIT AUCUNE SCÈNE (`scene_par_defaut`) : Raymonde dit un mot, montre le camion (le
    # premier lieu que nomme un objectif : la ruelle de l'hôtel), la caméra y va, elle finit, la
    # caméra revient. Et à la fin, on est au bar et elle à son usine : une coupe chez elle, sans quoi
    # on l'entendrait de nulle part.
}
