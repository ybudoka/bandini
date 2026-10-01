"""La mission i04 — voir app/missions/__init__.py pour le moteur.

Laisser refroidir (M16, arc I, 1er oct. 2026) — la règle de l'île, comprise en char. La police ne nage pas et ne
prend pas la navette (`Police.auRefuge`) : un char trop chaud, Léo le garde une journée dans son hangar, et le
lendemain il a une autre couleur et d'autres plaques. On vole une berline derrière la cantine (trois étoiles), on
l'embarque sur la NAVETTE DE L'ÎLE aux Quais (`embarquer`, `bateau: navette` — elle prend les chars), on la mène
au hangar par le chemin de gravelle (`livrer`, `ile:hangar_ile`, `rentre` : Léo la rentre), on attend une journée
de jeu (`attendre`), on la reprend, et la navette du retour la ramène en ville jusqu'à la planque.

⚠️ `ile:<lieu>` : un lieu DE L'ÎLE qu'on rejoint par l'eau — les juges des barrières savent qu'on n'y marche pas
depuis la ville (`test_barrieres.py`), et `poserLeChar` y cherche de la terre, pas une rue (l'île n'en a aucune).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "i04",
    "titre": "Laisser refroidir",
    "donneur": "leo",
    "prerequis": ["i01"],
    "recompense": 100,
    "donne": {"message": "L'ÎLE FAIT OUBLIER : UN CHAR CHAUD Y REFROIDIT"},

    "objectifs": [
        {"type": "monter", "texte": "UN CHAR CHAUD : LA BERLINE DERRIÈRE LA CANTINE",
         "vehicule": "luxe", "ou": "ruelle:cantine:6"},

        {"type": "embarquer", "texte": "LA NAVETTE DE L'ÎLE, AVEC LE CHAR — AUX HEURES IMPAIRES",
         "escale": "quais", "bateau": "navette", "etoiles": 3},

        {"type": "livrer", "texte": "DÉBARQUE, PIS ROULE JUSQU'AU HANGAR DE LÉO",
         "lieu": "ile:hangar_ile", "rayon": 5, "rentre": True},

        {"type": "attendre", "texte": "LAISSE-LE REFROIDIR UNE JOURNÉE", "heures": 24},

        {"type": "monter", "texte": "TON CHAR EST PRÊT, DEVANT LE HANGAR",
         "vehicule": "luxe", "ou": "ile:hangar_ile"},

        {"type": "embarquer", "texte": "LA NAVETTE DU RETOUR, AVEC LE CHAR",
         "escale": "ile", "bateau": "navette"},

        {"type": "livrer", "texte": "À TA PLANQUE : PERSONNE NE LE CHERCHE", "lieu": "planque", "rayon": 5},
    ],

    # Intention (intro) : Léo ne regarde jamais celui qui lui parle ; la caméra, elle, va voir le quai de la navette
    # aux Quais — le chemin du char chaud — sous sa deuxième réplique, et revient pour la règle.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "navette:quais", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Léo : pince-sans-rire, lent, des phrases courtes qui nient tout. Il ne dit
    # aucun nom ; il ne dit pas « merci ». Le comique est dans le constat (`[deadpan]`), jamais dans un clin d'œil.
    "dialogue": {
        "appel": [
            _l("leo", "Léo, de l'île. Si t'as un char trop chaud, j'ai un hangar qui pose pas de questions.",
               jeu="[deadpan] Léo, de l'île. [matter-of-fact] Si t'as un char trop chaud… j'ai un hangar qui pose pas de questions.")
        ],
        "intro": [
            _l("leo", "La police nage pas, pis elle prend pas la navette. Un char chaud, icitte, ça refroidit.",
               jeu="[deadpan] La police nage pas, pis elle prend pas la navette. [matter-of-fact] Un char chaud, icitte… ça refroidit."),
            _l("leo", "Prends-en un en ville, embarque-le sur la navette, pis amène-le-moé au hangar.",
               jeu="[matter-of-fact] Prends-en un en ville, embarque-le sur la navette… pis amène-le-moé au hangar."),
            _l("leo", "Une journée. Le lendemain, y a une autre couleur pis d'autres plaques. J'ai rien vu.",
               jeu="[mysteriously] Une journée. Le lendemain, y a une autre couleur pis d'autres plaques. [deadpan] J'ai rien vu.")
        ],
        "pendant": [
            _p("leo", "Derrière la cantine, y a une berline qui fait envie. J'ai rien dit.", 0,
               jeu="[matter-of-fact] Derrière la cantine, y a une berline qui fait envie. [deadpan] J'ai rien dit."),
            _p("leo", "Le proprio a appelé la police. La navette part aux heures impaires : sois dessus.", 1,
               jeu="[deadpan] Le proprio a appelé la police. [matter-of-fact] La navette part aux heures impaires : sois dessus."),
            _p("leo", "Débarque pis suis le chemin jusqu'au hangar. Doucement, c'est de la gravelle.", 2,
               jeu="[matter-of-fact] Débarque pis suis le chemin jusqu'au hangar. [deadpan] Doucement… c'est de la gravelle."),
            _p("leo", "Laisse-le-moé. Reviens demain. Va dormir, ou va te faire oublier.", 3,
               jeu="[deadpan] Laisse-le-moé. Reviens demain. [matter-of-fact] Va dormir… ou va te faire oublier."),
            _p("leo", "Ton char est prêt, devant le hangar. Je l'ai jamais vu de ma vie.", 4,
               jeu="[matter-of-fact] Ton char est prêt, devant le hangar. [deadpan] Je l'ai jamais vu de ma vie."),
            _p("leo", "La navette du retour. En ville, personne cherche ce char-là.", 5,
               jeu="[matter-of-fact] La navette du retour. [mysteriously] En ville, personne cherche ce char-là."),
            _p("leo", "Range-le à ta planque. Si on te demande, l'île, tu connais pas.", 6,
               jeu="[matter-of-fact] Range-le à ta planque. [deadpan] Si on te demande… l'île, tu connais pas.")
        ],
        "fin": [
            _l("leo", "Un char propre, pis personne qui le cherche. C'est ça, l'île.",
               jeu="[matter-of-fact] Un char propre, pis personne qui le cherche. [amused] C'est ça, l'île."),
            _l("leo", "Reviens quand tu veux. J'serai pas là, comme d'habitude.",
               jeu="[deadpan] Reviens quand tu veux. [amused] J'serai pas là… comme d'habitude.")
        ],
        "echec": [
            _l("leo", "J'étais pas là. Pis toi non plus.",
               jeu="[deadpan] J'étais pas là. [matter-of-fact] Pis toi non plus.")
        ]
    }
}
