"""La mission r07 — voir app/missions/__init__.py pour le moteur.

L'auto banalisée (M16, arc R, 30 sept. 2026). Du côté de Bouchard (après r04). Le sergent a un service à rendre à un
ami : trois Ciseaux de Sal traînent au Faubourg, et « un policier en civil » va les ramasser. Le policier en civil,
c'est le neveu, dans l'auto banalisée du sergent. On la prend devant le poste, on couche les trois Ciseaux, et on la
ramène au poste avant que quelqu'un ne note le numéro de plaque.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "r07",
    "titre": "L'auto banalisée",
    "donneur": "bouchard",
    "prerequis": ["r04"],
    "recompense": 400,
    "donne": {"message": "LE SERGENT A UN AMI DE PLUS, ET SAL TROIS CISEAUX DE MOINS"},

    # ⚠️ Les Ciseaux attendent au terminus (`ou`, sans `loin` : venus sur nous devant le poste, le `livrer` qui suit
    # tombait dans la même image) ; le dernier objectif ramène l'auto au poste, jamais un `tuer` là où la fin se joue. Bouchard est dedans, au casse-croûte : sa fin passe au combiné.
    "objectifs": [
        {"type": "monter", "texte": "L'AUTO BANALISÉE DU SERGENT, DEVANT LE POSTE",
         "vehicule": "police", "ou": "porte:poste"},

        {"type": "tuer", "texte": "TROIS CISEAUX DE SAL AU TERMINUS : « ARRÊTE-LES »",
         "groupe": "cravates", "n": 3, "ou": "porte:terminus", "arme": "poing_americain"},

        {"type": "livrer", "texte": "RAMÈNE L'AUTO AU POSTE, SANS UN MOT", "lieu": "poste", "rayon": 5},
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
            _l("bouchard", "Bouchard. J'ai un service à rendre, pis toi t'as une face de policier en civil. Viens me voir.",
               jeu="[gruffly] Bouchard. [deadpan] J'ai un service à rendre, pis toi t'as une face de policier en civil. Viens me voir.")
        ],
        "intro": [
            _l("bouchard", "Trois Ciseaux de Sal traînent au Faubourg. Un ami veut qu'ils disparaissent un bout.",
               jeu="[matter-of-fact] Trois Ciseaux de Sal traînent au Faubourg. [knowingly] Un ami veut qu'ils disparaissent un bout."),
            _l("bouchard", "Mon auto banalisée est devant le poste. Personne regarde une auto grise.",
               jeu="[gruffly] Mon auto banalisée est devant le poste. [deadpan] Personne regarde une auto grise."),
            _l("bouchard", "Couche-les, pis ramène-la au poste avant qu'un voisin note la plaque.",
               jeu="[firmly] Couche-les, pis ramène-la au poste avant qu'un voisin note la plaque.")
        ],
        "pendant": [
            _p("bouchard", "Les clés sont dans le pare-soleil. Comme toujours.", 0,
               jeu="[matter-of-fact] Les clés sont dans le pare-soleil. [deadpan] Comme toujours."),
            _p("bouchard", "Les v'là. Ils pensent que t'es de la police. T'es presque de la police.", 1,
               jeu="[gruffly] Les v'là. Ils pensent que t'es de la police. [wryly] T'es presque de la police."),
            _p("bouchard", "Au poste, astheure. Stationne-la à reculons, comme un vrai.", 2,
               jeu="[matter-of-fact] Au poste, astheure. [gruffly] Stationne-la à reculons, comme un vrai.")
        ],
        "fin": [
            _l("bouchard", "Propre. Mon ami est content, pis quand mon ami est content, moi aussi.",
               jeu="[satisfied] Propre. [knowingly] Mon ami est content, pis quand mon ami est content, moi aussi."),
            _l("bouchard", "T'as fait une belle carrière dans la police, le jeune. Une heure, mais belle.",
               jeu="[deadpan] T'as fait une belle carrière dans la police, le jeune. [gruffly] Une heure, mais belle.")
        ],
        "echec": [
            _l("bouchard", "Mon auto, pis les Ciseaux qui courent encore. J'ai rien vu.",
               jeu="[annoyed] Mon auto, pis les Ciseaux qui courent encore. [gruffly] J'ai rien vu.")
        ]
    }
}
