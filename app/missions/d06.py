"""La mission d06 — voir app/missions/__init__.py pour le moteur.

Sal perd patience (M16, arc D, 30 sept. 2026). L'huissier est reparti les mains vides (d05) : Sal envoie ses
Ciseaux, les vrais, casser le garage. Gus les a vus aiguiser leurs bagues au terminus ; l'armurerie est à deux coins
de rue, et il n'aime pas le bruit. La nuit au garage, une première vague, puis une deuxième avec leur contremaître
— et on va dire à Gus que c'est fini (il est dehors, à sa porte : `retourner`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "d06",
    "titre": "Sal perd patience",
    "donneur": "gus",
    "prerequis": ["d05"],
    "recompense": 250,
    "donne": {"message": "LE GARAGE TIENT DEBOUT — SAL A COMPRIS"},

    # ⚠️ Ti-Guy devait la donner : il a quitté la ville après m1 (`parti_apres`). Marco non plus — il s'en va après
    # m97, qu'on peut jouer avant l'arc D. Gus, lui, ne bouge jamais de sa porte. Les Ciseaux arrivent de loin
    # (`loin`) sur le garage ; la fin se dit chez Gus (`retourner`), pas au garage.
    "objectifs": [
        {"type": "aller", "texte": "ATTENDS LES CISEAUX AU GARAGE, À LA NUIT",
         "lieu": "garage", "rayon": 6, "nuit": True},

        {"type": "tuer", "texte": "LES CISEAUX DE SAL ARRIVENT : DÉFENDS LE GARAGE",
         "groupe": "cravates", "n": 3, "ou": "garage", "loin": 12, "arme": "poing_americain"},

        {"type": "tuer", "texte": "LEUR CONTREMAÎTRE, AVEC SES CISEAUX : COUCHE-LE",
         "groupe": "cravates", "n": 1, "chef": True, "arme": "couteau", "vie": 200, "loin": 10},

        {"type": "retourner", "texte": "DIS À GUS QUE C'EST FINI"},
    ],

    # Intention (intro) : Gus à sa porte, il ne regarde pas le neveu, il regarde la rue — sa réplique tient le plan ;
    # la coupe va sur le garage sous la deuxième.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:garage", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Gus : bourru, commercial jusque dans l'entraide ; il ne donne jamais un
    # ordre, il pose un prix. Il ne dit merci qu'une fois — et c'est lui qui paie.
    "dialogue": {
        "appel": [
            _l("gus", "Gus, de l'armurerie. Les Ciseaux de Sal aiguisent leurs bagues au terminus. Pour ton garage, jeune.",
               jeu="[gruffly] Gus, de l'armurerie. Les Ciseaux de Sal aiguisent leurs bagues au terminus. [matter-of-fact] Pour ton garage, jeune.")
        ],
        "intro": [
            _l("gus", "Sal a perdu devant l'avocat. Un barbier qui perd, ça coupe autre chose que des cheveux.",
               jeu="[gruffly] Sal a perdu devant l'avocat. [wryly] Un barbier qui perd, ça coupe autre chose que des cheveux."),
            _l("gus", "Ils viennent à la noirceur. Ton garage est à deux coins de mon magasin, pis j'aime pas les vitres cassées.",
               jeu="[annoyed] Ils viennent à la noirceur. [matter-of-fact] Ton garage est à deux coins de mon magasin, pis j'aime pas les vitres cassées."),
            _l("gus", "Tiens-les dehors. Je paie pour la tranquillité, c'est rare, profites-en.",
               jeu="[gruffly] Tiens-les dehors. [matter-of-fact] Je paie pour la tranquillité, c'est rare, profites-en.")
        ],
        "pendant": [
            _p("gus", "Attends la nuit. Ces gars-là travaillent pas de jour, ils ont des clients.", 0,
               jeu="[matter-of-fact] Attends la nuit. [wryly] Ces gars-là travaillent pas de jour, ils ont des clients."),
            _p("gus", "Les v'là. Trois, avec des bagues. Vise les mains, jeune.", 1,
               jeu="[gruffly] Les v'là. Trois, avec des bagues. [firmly] Vise les mains, jeune."),
            _p("gus", "Le gros, c'est leur contremaître. Il se promène avec les vrais ciseaux de Sal.", 2,
               jeu="[concerned] Le gros, c'est leur contremaître. [matter-of-fact] Il se promène avec les vrais ciseaux de Sal."),
            _p("gus", "C'est tranquille. Viens me voir à ma porte, j'ai de quoi pour toi.", 3,
               jeu="[satisfied] C'est tranquille. [gruffly] Viens me voir à ma porte, j'ai de quoi pour toi.")
        ],
        "fin": [
            _l("gus", "Pas une vitre cassée. Sal va comprendre que ton garage coûte plus cher que ta dette.",
               jeu="[satisfied] Pas une vitre cassée. [knowingly] Sal va comprendre que ton garage coûte plus cher que ta dette."),
            _l("gus", "Tiens. Pis merci. Dis-le à personne, j'ai une réputation.",
               jeu="[gruffly] Tiens. [quietly] Pis merci. [matter-of-fact] Dis-le à personne, j'ai une réputation.")
        ],
        "echec": [
            _l("gus", "Ils ont eu le garage, pis mes vitres. Je t'envoie la facture, jeune.",
               jeu="[annoyed] Ils ont eu le garage, pis mes vitres. [gruffly] Je t'envoie la facture, jeune.")
        ]
    }
}
