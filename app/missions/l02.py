"""La mission l02 — voir app/missions/__init__.py pour le moteur.

La manchette sur toi (M16, arc C, 30 sept. 2026 — la « c04 » de la fiche). Louise a trouvé sa une : le neveu de
Rocco lui-même. Elle attend devant le poste, l'appareil prêt ; il suffit de faire parler de soi — trois étoiles —
puis de les semer en moins d'une minute et demie. Si on y arrive, le Clairon titre _Bandini l'insaisissable_ ; si
on se fait prendre, elle a quand même sa photo, et c'est une autre une.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "l02",
    "titre": "La manchette sur toi",
    "donneur": "louise",
    "prerequis": ["l01"],
    "recompense": 200,
    "donne": {"manchette": "insaisissable", "message": "DEMAIN, TU FAIS LA UNE DU CLAIRON"},

    # ⚠️ `semer` pose ses étoiles quand il commence (`etoiles: 3`) : pas besoin de faire un crime, le poste te voit
    # passer devant l'appareil de Louise. Le chrono est l'option transverse `chrono_s`. Louise est DEHORS, à son
    # kiosque : `retourner`.
    "objectifs": [
        {"type": "aller", "texte": "LOUISE T'ATTEND DEVANT LE POSTE, L'APPAREIL PRÊT",
         "lieu": "poste", "rayon": 5},

        {"type": "semer", "texte": "TROIS ÉTOILES : SÈME-LES EN 90 SECONDES",
         "etoiles": 3, "chrono_s": 90},

        {"type": "retourner", "texte": "RETOURNE VOIR LOUISE AU KIOSQUE"},
    ],

    # Intention (intro) : Louise ravie de son idée, qui la raconte comme un titre — sa réplique tient le plan ; la
    # coupe montre le poste sous la deuxième.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:poste", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Louise : le plaisir de la une qui s'écrit toute seule ; elle taquine, et
    # elle prend des notes en parlant.
    "dialogue": {
        "appel": [
            _l("louise", "C'est Louise. J'ai trouvé ma une de demain, pis c'est toi. Viens au kiosque.",
               jeu="[excited] C'est Louise. [teasing] J'ai trouvé ma une de demain, pis c'est toi. Viens au kiosque.")
        ],
        "intro": [
            _l("louise", "Tout le monde parle du neveu de Rocco. Personne l'a jamais vu. Je veux la photo.",
               jeu="[confident] Tout le monde parle du neveu de Rocco. Personne l'a jamais vu. [excited] Je veux la photo."),
            _l("louise", "Passe devant le poste. Fais-toi voir. Trois étoiles, pis je déclenche.",
               jeu="[mischievously] Passe devant le poste. Fais-toi voir. [excited] Trois étoiles, pis je déclenche."),
            _l("louise", "Après, t'as une minute et demie pour disparaître. Sinon, la une, c'est ton procès.",
               jeu="[wryly] Après, t'as une minute et demie pour disparaître. [teasing] Sinon, la une, c'est ton procès.")
        ],
        "pendant": [
            _p("louise", "Je suis de l'autre côté de la rue. Souris, mon beau.", 0,
               jeu="[teasing] Je suis de l'autre côté de la rue. [amused] Souris, mon beau."),
            _p("louise", "Clic! Je l'ai! Astheure, disparais, je chronomètre.", 1,
               jeu="[excited] Clic! Je l'ai! [firmly] Astheure, disparais, je chronomètre."),
            _p("louise", "Plus une sirène. Reviens au kiosque, j'ai mon titre.", 2,
               jeu="[impressed] Plus une sirène. [confident] Reviens au kiosque, j'ai mon titre.")
        ],
        "fin": [
            _l("louise", "« Bandini l'insaisissable. » Trois étoiles, pis pouf. Le monde va adorer.",
               jeu="[excited] « Bandini l'insaisissable. » Trois étoiles, pis pouf. [amused] Le monde va adorer."),
            _l("louise", "Pis Bouchard va la découper pour son babillard. Tiens, ta part des ventes.",
               jeu="[wryly] Pis Bouchard va la découper pour son babillard. [warmly] Tiens, ta part des ventes.")
        ],
        "echec": [
            _l("louise", "Pogné en moins de deux. Ma une va s'appeler « Le neveu au poste ».",
               jeu="[disappointed] Pogné en moins de deux. [sarcastic] Ma une va s'appeler « Le neveu au poste ».")
        ]
    }
}
