"""La mission r06 — voir app/missions/__init__.py pour le moteur.

Une affiche de moins (M16, arc R, 30 sept. 2026). Du côté de Roy (après r03). Bouchard a fait coller la face du
neveu — RECHERCHÉ — sur cinq portes du Faubourg, pour lui rappeler à qui il a dit non. Roy ne peut pas les arracher
elle-même : c'est son poste qui les a imprimées. On les arrache avant que le Faubourg se réveille, trois minutes,
porte à porte, et on revient la voir : elle efface trois pages de plus.

⚠️ « Arracher » se joue en passant à chaque porte, dans l'ordre (`course`) : les affiches de la rue (le décor qu'on
arrache au bouton) sont tirées au hasard de la ville — une mission ne sait pas encore en poser une à une porte.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "r06",
    "titre": "Une affiche de moins",
    "donneur": "roy",
    "prerequis": ["r03"],
    "recompense": 100,
    "donne": {"casier": -3, "message": "TA FACE N'EST PLUS SUR LES PORTES DU FAUBOURG"},

    "objectifs": [
        {"type": "course", "texte": "CINQ AFFICHES, CINQ PORTES DU FAUBOURG, TROIS MINUTES",
         "points": ["kiosque", "casse_croute", "armurerie", "vetements", "terminus"], "rayon": 3, "chrono_s": 180},

        {"type": "parler", "texte": "LES AFFICHES SONT AUX POUBELLES : VA VOIR ROY", "cible": "roy"},
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:kiosque", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Roy : agacée par la mesquinerie du sergent, amusée malgré elle par la
    # photo ; son `[wryly]` de la mission va à la photo.
    "dialogue": {
        "appel": [
            _l("roy", "C'est Roy. Ta face est collée sur cinq portes du Faubourg. Pas par moi.",
               jeu="[matter-of-fact] C'est Roy. Ta face est collée sur cinq portes du Faubourg. [coldly] Pas par moi.")
        ],
        "intro": [
            _l("roy", "Bouchard a fait imprimer des affiches. RECHERCHÉ, avec ta photo de permis.",
               jeu="[coldly] Bouchard a fait imprimer des affiches. [wryly] RECHERCHÉ, avec ta photo de permis."),
            _l("roy", "Le kiosque, le casse-croûte, l'armurerie, chez Rosa, pis le terminus. Dans cet ordre-là.",
               jeu="[matter-of-fact] Le kiosque, le casse-croûte, l'armurerie, chez Rosa, pis le terminus. [firmly] Dans cet ordre-là."),
            _l("roy", "T'as trois minutes avant que les commerçants ouvrent. Moi, je vois rien.",
               jeu="[serious] T'as trois minutes avant que les commerçants ouvrent. [quietly] Moi, je vois rien.")
        ],
        "pendant": [
            _p("roy", "Arrache, pis continue. Une affiche, ça se recolle pas tout seul.", 0,
               jeu="[firmly] Arrache, pis continue. [matter-of-fact] Une affiche, ça se recolle pas tout seul."),
            _p("roy", "C'est fait. Viens me voir, j'ai ton casier ouvert sur mon bureau.", 1,
               jeu="[satisfied] C'est fait. [calm] Viens me voir, j'ai ton casier ouvert sur mon bureau.")
        ],
        "fin": [
            _l("roy", "Trois pages de moins. Pis j'ai gardé une affiche pour mon bureau, elle est drôle.",
               jeu="[calm] Trois pages de moins. [wryly] Pis j'ai gardé une affiche pour mon bureau, elle est drôle."),
            _l("roy", "Tiens. Pour le papier sablé que ça va te prendre pour ta réputation.",
               jeu="[matter-of-fact] Tiens. [quietly] Pour le papier sablé que ça va te prendre pour ta réputation.")
        ],
        "echec": [
            _l("roy", "Le Faubourg s'est réveillé avec ta face sur les portes. Tant pis.",
               jeu="[disappointed] Le Faubourg s'est réveillé avec ta face sur les portes. [coldly] Tant pis.")
        ]
    }
}
