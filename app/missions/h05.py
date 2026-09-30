"""La mission h05 — voir app/missions/__init__.py pour le moteur.

Le patient qui s'est sauvé (M16, arc H, 30 sept. 2026). Le chef des Cravates de m5, recousu à l'hôpital, se lève
à trois heures du matin, vole l'ambulance — avec la trousse de morphine dedans — et file. Ginette veut sa trousse.
On le rattrape (le fuyard en ambulance, le patron de m97/d02) ; il sort avec la trousse, on la reprend ; ses deux
gars arrivent le chercher ; on rapporte la trousse à Ginette, à son comptoir (`retourner` : elle est DEHORS).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "h05",
    "titre": "Le patient qui s'est sauvé",
    "donneur": "ginette",
    "prerequis": ["h04"],
    "recompense": 200,
    "donne": {"message": "LA TROUSSE EST REVENUE À LA PHARMACIE"},

    # ⚠️ Le fuyard part de la rue devant l'hôpital (`ouEstLeJoueurEnVille`) : Ginette se tient dehors, on y est.
    # Les deux gars arrivent de loin (`loin`) là où l'on est, pas à la porte de l'hôpital : la fin s'y joue.
    "objectifs": [
        {"type": "ramasser", "texte": "LE PATIENT FILE EN AMBULANCE : RATTRAPE-LE",
         "cible": "fuyard", "vehicule": "ambulance"},

        {"type": "tuer", "texte": "SES GARS VIENNENT LE CHERCHER : COUCHE-LES",
         "groupe": "cravates", "n": 2, "loin": 10},

        {"type": "retourner", "texte": "RAPPORTE LA TROUSSE À GINETTE"},
    ],

    # Intention (intro) : Ginette à son comptoir, bras croisés — elle a déjà décidé que c'est toi qui y vas. Sa
    # première réplique tient le plan ; la coupe va montrer la baie vide de l'ambulance sous la deuxième.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:hopital", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Ginette : une colère froide d'infirmière-chef (on a volé les malades), qui
    # passe par l'ironie. Elle ne dit pas le nom du patient : le secret professionnel, même en colère.
    "dialogue": {
        "appel": [
            _l("ginette", "C'est Ginette, de l'hôpital. Un patient est parti sans signer son congé. Avec mon ambulance.",
               jeu="[annoyed] C'est Ginette, de l'hôpital. Un patient est parti sans signer son congé. [sarcastic] Avec mon ambulance.")
        ],
        "intro": [
            _l("ginette", "Je te dirai pas son nom. Disons que tu l'as déjà couché une fois, dans le Faubourg.",
               jeu="[firmly] Je te dirai pas son nom. [knowingly] Disons que tu l'as déjà couché une fois, dans le Faubourg."),
            _l("ginette", "Vingt-deux points de suture, pis il repart avec la trousse de morphine. Quel remerciement.",
               jeu="[annoyed] Vingt-deux points de suture, pis il repart avec la trousse de morphine. [sarcastic] Quel remerciement."),
            _l("ginette", "Arrête l'ambulance, reprends la trousse. Lui, il se recoudra tout seul.",
               jeu="[firmly] Arrête l'ambulance, reprends la trousse. [coldly] Lui, il se recoudra tout seul.")
        ],
        "pendant": [
            _p("ginette", "Il conduit avec des points dans le ventre. Il va finir par s'arrêter, aide-le.", 0,
               jeu="[matter-of-fact] Il conduit avec des points dans le ventre. [wryly] Il va finir par s'arrêter, aide-le."),
            _p("ginette", "Ses amis arrivent. Des Cravates, encore. On va manquer de fil, à ce rythme-là.", 1,
               jeu="[annoyed] Ses amis arrivent. Des Cravates, encore. [deadpan] On va manquer de fil, à ce rythme-là."),
            _p("ginette", "La trousse, fermée, à mon comptoir. Pis touche pas au contenu.", 2,
               jeu="[firmly] La trousse, fermée, à mon comptoir. [coldly] Pis touche pas au contenu.")
        ],
        "fin": [
            _l("ginette", "Scellée, complète. Il a même pas su l'ouvrir, le pauvre.",
               jeu="[satisfied] Scellée, complète. [sarcastic] Il a même pas su l'ouvrir, le pauvre."),
            _l("ginette", "Tiens. Pis la prochaine fois qu'il se présente à l'urgence, c'est toi qui le recouds.",
               jeu="[matter-of-fact] Tiens. [wryly] Pis la prochaine fois qu'il se présente à l'urgence, c'est toi qui le recouds.")
        ],
        "echec": [
            _l("ginette", "Partie, la trousse. Je vais remplir le formulaire de perte, en trois copies.",
               jeu="[disappointed] Partie, la trousse. [annoyed] Je vais remplir le formulaire de perte, en trois copies.")
        ]
    }
}
