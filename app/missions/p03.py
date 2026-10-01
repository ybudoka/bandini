"""La mission p03 — voir app/missions/__init__.py pour le moteur.

La murale de Maude (M16, arc P, La Pointe — 1er oct. 2026). Maude peint le grand mur au pied du phare : la ville
qu'on lui laisse. Il lui manque trois couleurs ; l'atelier de peinture de La Shop les lui garde. On prend sa moto (sa
motoneige, l'hiver), on va chercher les bombes à pied devant l'atelier, et on les rapporte avant que l'apprêt sèche.

⚠️ Écart à la fiche : le chrono (120 s) court au RETOUR seulement — Maude étend son apprêt dès qu'on a les bombes (elle
le dit au téléphone) ; l'aller est libre. De l'atelier au phare, à l'allure de l'étalon des courses (110 px/s), il y a
moins d'une minute. L'atelier est une ENSEIGNE (`boutique:peinture`, « PEINTURE AUTO ») : aucune porte neuve.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "p03",
    "titre": "La murale de Maude",
    "donneur": "maude",
    "prerequis": ["m6"],
    "recompense": 150,
    "donne": {"message": "LA MURALE DU PHARE A SES COULEURS"},

    "objectifs": [
        {"type": "monter", "texte": "LE BOLIDE DE MAUDE, DEVANT LE PHARE",
         "vehicule": "moto", "ou": "porte:phare", "prete": "maude"},

        {"type": "obtenir", "texte": "TROIS BOMBES À L'ATELIER DE PEINTURE, À LA SHOP", "objet": "bombes_de_maude",
         "ou": "boutique:peinture", "dessin": "bombes", "nom": "TROIS BOMBES DE PEINTURE"},

        {"type": "livrer", "texte": "RAPPORTE-LES À MAUDE AVANT QUE L'APPRÊT SÈCHE",
         "lieu": "phare", "rayon": 6, "chrono_s": 120},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Maude : vingt-quatre ans, la tête dans son mur, le tutoiement facile ; elle
    # parle des couleurs comme de gens. Elle se nomme une fois, au téléphone.
    "dialogue": {
        "appel": [
            _l("maude", "Salut, c'est Maude, la fille qui peint le mur du phare! J'ai pus de rouge, pis le soleil tourne.",
               jeu="[excited] Salut, c'est Maude, la fille qui peint le mur du phare! [annoyed] J'ai pus de rouge, pis le soleil tourne.")
        ],
        "intro": [
            _l("maude", "Trois bombes à l'atelier de peinture de La Shop. Le gars me les garde, il m'en doit une.",
               jeu="[cheerful] Trois bombes à l'atelier de peinture de La Shop. [knowingly] Le gars me les garde, il m'en doit une."),
            _l("maude", "Prends ma moto. Dès que t'as les bombes, j'étends l'apprêt : t'auras deux minutes.",
               jeu="[excited] Prends ma moto. [serious] Dès que t'as les bombes, j'étends l'apprêt : t'auras deux minutes.",
               hiver=("Prends ma motoneige. Dès que t'as les bombes, j'étends l'apprêt : t'auras deux minutes.",
                      "[excited] Prends ma motoneige. [serious] Dès que t'as les bombes, j'étends l'apprêt : t'auras deux minutes."))
        ],
        "pendant": [
            _p("maude", "Elle tousse au démarrage, mais elle est fidèle. Comme moi.", 0,
               jeu="[amused] Elle tousse au démarrage, mais elle est fidèle. [playfully] Comme moi."),
            _p("maude", "Rouge pompier, bleu de la baie, pis un jaune qui crie. Dis que c'est pour la fille du phare.", 1,
               jeu="[enthusiastic] Rouge pompier, bleu de la baie, pis un jaune qui crie. [cheerful] Dis que c'est pour la fille du phare."),
            _p("maude", "J'étends l'apprêt! Grouille, le mur le boit comme un débardeur sa bière.", 2,
               jeu="[excited] J'étends l'apprêt! [teasing] Grouille, le mur le boit comme un débardeur sa bière.")
        ],
        "fin": [
            _l("maude", "Juste à temps! Regarde le mur demain : t'es dedans, en petit, dans le coin d'en bas.",
               jeu="[happy] Juste à temps! [playfully] Regarde le mur demain : t'es dedans, en petit, dans le coin d'en bas."),
            _l("maude", "Tiens, cent cinquante. Pis laisse ma bécane là, je la connais par cœur.",
               jeu="[warmly] Tiens, cent cinquante. [amused] Pis laisse ma bécane là, je la connais par cœur.")
        ],
        "echec": [
            _l("maude", "L'apprêt a séché. Bon, je vais peindre un mur gris. C'est de l'art aussi, paraît.",
               jeu="[disappointed] L'apprêt a séché. [sarcastic] Bon, je vais peindre un mur gris. C'est de l'art aussi, paraît.")
        ]
    }
}
