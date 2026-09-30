"""La mission r02 — voir app/missions/__init__.py pour le moteur.

Roy te convoque (M16, arc R « Roy contre Bouchard », 30 sept. 2026). L'inspectrice Claudine Roy sait qui a volé son
carnet (r01) et où Bouchard l'a caché : dans le coffre de l'Hôtel Bandini. Elle ne te fait pas arrêter ; elle veut
son carnet, et elle veut savoir de quel côté tu es. On va le chercher à l'hôtel — Norbert ouvre le coffre, en
vouvoyant —, on le lui rapporte au poste, et elle pose le marché : elle (r03) ou Bouchard (r04), pas les deux.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "r02",
    "titre": "Roy te convoque",
    "donneur": "roy",
    "prerequis": ["r01"],
    "recompense": 150,
    "donne": {"message": "ROY OU BOUCHARD : À TOI DE CHOISIR TA POLICE"},

    # ⚠️ Roy est DEDANS (`point:roy`, au poste) et Norbert aussi (`point:norbert`, à l'hôtel) : deux `parler`, pas de
    # `retourner`. Le carnet ne se ramasse pas (un objet ne se pose pas dans une pièce) : Norbert le rend à la
    # poignée de main.
    "objectifs": [
        {"type": "parler", "texte": "LE CARNET DORT AU COFFRE DE L'HÔTEL : VOIS NORBERT", "cible": "norbert"},

        {"type": "parler", "texte": "RAPPORTE LE CARNET À ROY, AU POSTE", "cible": "roy"},
    ],

    # Intention (intro) : Roy à son bureau, les mains à plat, sans colère — sa réplique tient le plan ; la coupe va
    # sur l'hôtel sous la deuxième (l'intro jouée dedans doit aller voir la ville).
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "coupe", "vers": "porte:hotel", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Roy : la police honnête, qui n'a pas besoin de crier ; précise, froide,
    # et une ironie sèche qu'elle ne s'autorise qu'une fois par mission. Norbert : le vouvoiement, jamais le nom d'un
    # client.
    "dialogue": {
        "appel": [
            _l("roy", "Inspectrice Roy, du poste. Je sais qui a pris mon carnet. Passe me voir, on va jaser.",
               jeu="[firmly] Inspectrice Roy, du poste. [coldly] Je sais qui a pris mon carnet. Passe me voir, on va jaser.")
        ],
        "intro": [
            _l("roy", "Assis-toi. Je t'arrête pas, je t'aurais déjà arrêté. Je veux mon carnet.",
               jeu="[calm] Assis-toi. Je t'arrête pas, je t'aurais déjà arrêté. [firmly] Je veux mon carnet."),
            _l("roy", "Bouchard l'a fait cacher dans le coffre de l'Hôtel Bandini. Le concierge a la clé.",
               jeu="[matter-of-fact] Bouchard l'a fait cacher dans le coffre de l'Hôtel Bandini. [knowingly] Le concierge a la clé."),
            _l("roy", "Ramène-le-moi. Après, on parlera de quel côté de la loi tu veux dormir.",
               jeu="[serious] Ramène-le-moi. [coldly] Après, on parlera de quel côté de la loi tu veux dormir.")
        ],
        "pendant": [
            _p("roy", "Le concierge s'appelle Norbert. Il vouvoie tout le monde, même les voleurs.", 0,
               jeu="[matter-of-fact] Le concierge s'appelle Norbert. [wryly] Il vouvoie tout le monde, même les voleurs."),
            _p("roy", "Pas de détour. Bouchard a des yeux dans toutes les vitrines du Faubourg.", 1,
               jeu="[serious] Pas de détour. [firmly] Bouchard a des yeux dans toutes les vitrines du Faubourg.")
        ],
        "accueil": [
            _a("norbert", "Le coffre de Monsieur le sergent? Je crains que Monsieur ne soit pas le seul à le chercher. Le voici.", 0,
               jeu="[quietly] Le coffre de Monsieur le sergent? [concerned] Je crains que Monsieur ne soit pas le seul à le chercher. [calm] Le voici.")
        ],
        "fin": [
            _l("roy", "Toutes les pages : des noms, des montants, des dates. Bouchard écrit bien, pour un croche.",
               jeu="[satisfied] Toutes les pages : des noms, des montants, des dates. [wryly] Bouchard écrit bien, pour un croche."),
            _l("roy", "Voilà le marché : tu travailles pour moi, ou tu retournes lui manger dans la main. Pas les deux.",
               jeu="[serious] Voilà le marché : tu travailles pour moi, ou tu retournes lui manger dans la main. [coldly] Pas les deux."),
            _l("roy", "Tiens, pour ton déplacement. Pense à ce que tu veux être dans dix ans.",
               jeu="[calm] Tiens, pour ton déplacement. [quietly] Pense à ce que tu veux être dans dix ans.")
        ],
        "echec": [
            _l("roy", "Le carnet a disparu, pis toi avec. Je vais m'en souvenir.",
               jeu="[coldly] Le carnet a disparu, pis toi avec. [firmly] Je vais m'en souvenir.")
        ]
    }
}
