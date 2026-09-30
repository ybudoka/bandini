"""La mission h08 — voir app/missions/__init__.py pour le moteur.

La traverse de l'urgence (M16, arc H, 30 sept. 2026). Un vieux pêcheur de l'île s'est ouvert la jambe sur un treuil ;
Sœur Jeanne l'a couché sur un banc de la chapelle et appelé le seul médecin qu'elle connaît. L'île n'a ni pont ni
traversier : Lachance a une chaloupe sous l'urgence, et pas de pilote. On traverse, la sœur confie le blessé, et on
revient à l'urgence en deux cents secondes.

⚠️ La fiche voulait le traversier (repli : la chaloupe) : le traversier ne dessert pas l'île — la chaloupe.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "h08",
    "titre": "La traverse de l'urgence",
    "donneur": "lachance",
    "prerequis": ["h04", "i01"],
    "recompense": 250,
    "donne": {"message": "LE PÊCHEUR DE L'ÎLE A GARDÉ SA JAMBE"},

    # ⚠️ Le patron de i01 : la chaloupe d'un amarrage à l'autre (`amarrage:hopital`, `amarrage:chapelle`) ; la poignée
    # de main de Sœur Jeanne (dehors, sur son parvis) confie le blessé ; le retour se livre sous l'urgence, au chrono.
    # Lachance est dedans : sa fin passe au combiné.
    "objectifs": [
        {"type": "monter", "texte": "LA CHALOUPE DE L'HÔPITAL, SOUS L'URGENCE", "vehicule": "bateau", "ou": "amarrage:hopital"},

        {"type": "livrer", "texte": "UN PÊCHEUR BLESSÉ À L'ÎLE : TRAVERSE", "lieu": "amarrage:chapelle", "rayon": 6},

        {"type": "parler", "texte": "SŒUR JEANNE A LE BLESSÉ, SUR LE PARVIS", "cible": "jeanne"},

        {"type": "livrer", "texte": "RAMÈNE-LE À L'URGENCE : DEUX CENTS SECONDES",
         "lieu": "amarrage:hopital", "rayon": 6, "chrono_s": 200},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "amarrage:chapelle", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    "dialogue": {
        "appel": [
            _l("lachance", "Ici Lachance. Un pêcheur blessé sur l'île, pis ma seule ambulance flotte pas.",
               jeu="[serious] Ici Lachance. [wryly] Un pêcheur blessé sur l'île, pis ma seule ambulance flotte pas.")
        ],
        "intro": [
            _l("lachance", "Une jambe ouverte sur un treuil. La religieuse a fait un garrot, elle sait ce qu'elle fait.",
               jeu="[gravely] Une jambe ouverte sur un treuil. [matter-of-fact] La religieuse a fait un garrot, elle sait ce qu'elle fait."),
            _l("lachance", "Il y a une chaloupe sous l'urgence. Traverse, ramène-le, pis va droit.",
               jeu="[firmly] Il y a une chaloupe sous l'urgence. Traverse, ramène-le, pis va droit."),
            _l("lachance", "Au retour, t'as deux cents secondes avant que le garrot devienne un problème.",
               jeu="[serious] Au retour, t'as deux cents secondes avant que le garrot devienne un problème.")
        ],
        "pendant": [
            _p("lachance", "La chaloupe est attachée sous le quai de l'urgence. Le moteur est chaud.", 0,
               jeu="[matter-of-fact] La chaloupe est attachée sous le quai de l'urgence. [calm] Le moteur est chaud."),
            _p("lachance", "Accoste sous la chapelle. Elle t'attend avec lui.", 1,
               jeu="[calm] Accoste sous la chapelle. [matter-of-fact] Elle t'attend avec lui."),
            _p("lachance", "Il est à bord? Alors le chrono part. Garde-le à l'abri des vagues.", 3,
               jeu="[gravely] Il est à bord? Alors le chrono part. [firmly] Garde-le à l'abri des vagues.")
        ],
        "accueil": [
            _a("jeanne", "Le voici, mon enfant. Il a juré trois fois, le bon Dieu lui pardonne. Va vite.", 2,
               jeu="[worried] Le voici, mon enfant. [wryly] Il a juré trois fois, le bon Dieu lui pardonne. [firmly] Va vite.")
        ],
        "fin": [
            _l("lachance", "Il garde sa jambe. Pis il jure encore, c'est bon signe.",
               jeu="[relieved] Il garde sa jambe. [wryly] Pis il jure encore, c'est bon signe."),
            _l("lachance", "L'île a un médecin, astheure, pis un pilote. Merci.",
               jeu="[warmly] L'île a un médecin, astheure, pis un pilote. [calm] Merci.")
        ],
        "echec": [
            _l("lachance", "Trop long. On fera ce qu'on pourra avec ce qui reste.",
               jeu="[somber] Trop long. [quietly] On fera ce qu'on pourra avec ce qui reste.")
        ]
    }
}
