"""La mission d09 — voir app/missions/__init__.py pour le moteur.

Un compte sur l'île (M16, arc D, 1er oct. 2026) — LE PREMIER CHOIX DANS UN DIALOGUE. Léo, qui garde le hangar de
l'île, doit huit cents piastres à Sal depuis le printemps ; il ne sait plus trop pour quoi. Sal t'envoie les chercher
dans la chaloupe du capitaine. Devant le hangar, Léo n'a rien — et c'est TOI qui réponds :

- « SAL VEUT SON ARGENT. TOUT DE SUITE. » — Léo siffle les deux matelots qui traînent au hangar ; couchés, il retrouve
  l'argent dans sa boîte à pêche. Sal paie la commission (250 $).
- « LAISSE FAIRE. JE PAIE SES 800 $. » — tu les sors de ta poche ; Sal, qui ne refuse jamais l'argent d'où qu'il
  vienne, les enlève de la dette de l'oncle. Pas une cenne pour toi, et Léo ne l'oubliera pas.
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "d09",
    "titre": "Un compte sur l'île",
    "donneur": "sal",
    "prerequis": ["d04", "i01"],
    "recompense": 250,
    "donne": {"message": "LÉO A PAYÉ — SAL A SES 800 $"},
    # ⚠️ Ce que chaque réponse change à la fin (`branches`) : la commission, ou la dette de l'oncle.
    "branches": {
        "payer": {"recompense": 0, "donne": {"dette": -800, "message": "SAL EFFACE 800 $ — LÉO NE L'OUBLIERA PAS"}},
    },

    # ⚠️ L'île ne se rejoint pas à pied (`test_barrieres.py`) : la chaloupe se prend sous le Faubourg (le patron d'i01)
    # et s'accoste sous le hangar ; Léo se tient dehors, devant. La QUESTION se pose à sa poignée de main (l'accueil de
    # l'étape 2) : les étapes 3 et 4 sont celles de « tout de suite », la 5 celle de « je paie ». Sal est dedans, au
    # terminus : on revient lui PARLER (pas de `retourner`, le patron de d04).
    "objectifs": [
        {"type": "monter", "texte": "LA CHALOUPE DU CAPITAINE, SOUS LE FAUBOURG",
         "vehicule": "bateau", "ou": "amarrage:bar", "prete": "berube"},

        {"type": "livrer", "texte": "TRAVERSE JUSQU'AU HANGAR DE L'ÎLE", "lieu": "amarrage:hangar_ile", "rayon": 6},

        {"type": "parler", "texte": "LÉO DOIT 800 $ À SAL : VA LUI PARLER", "cible": "leo"},

        {"type": "tuer", "texte": "LES GARS DU HANGAR S'EN MÊLENT : COUCHE-LES", "branche": "coucher",
         "groupe": "morues", "pieton": "matelot", "n": 2, "loin": 8},

        {"type": "parler", "texte": "LÉO A RETROUVÉ L'ARGENT : VA LE CHERCHER", "cible": "leo", "branche": "coucher"},

        {"type": "payer", "texte": "PAIE LES 800 $ DE LÉO", "montant": 800, "branche": "payer"},

        {"type": "livrer", "texte": "RAMÈNE LA CHALOUPE SOUS LE FAUBOURG", "lieu": "amarrage:bar", "rayon": 6},

        {"type": "parler", "texte": "RAPPORTE À SAL, AU TERMINUS", "cible": "sal"},
    ],

    # Intention (intro) : Sal parle en coupant — un client de plus, un compte de plus ; la coupe montre l'île, et sa
    # dernière phrase (« fais ça propre ») laisse le choix ouvert sans le dire.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "amarrage:hangar_ile", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Sal : un compte de plus, dit comme on parle de la température ; il ne menace
    # jamais en toutes lettres. Léo : pince-sans-rire, il nie tout, même d'avoir une dette ; il ne nomme personne. À la
    # fin, Sal compte — content de l'argent, et, sur l'autre branche, ému sans le dire de voir l'oncle dans le neveu.
    "dialogue": {
        "appel": [
            _l("sal", "Ici Sal. Un client de l'île me doit huit cents. Mes Ciseaux, eux, ont le mal de mer.",
               jeu="[calm] Ici Sal. [matter-of-fact] Un client de l'île me doit huit cents. [amused] Mes Ciseaux, eux, ont le mal de mer.")
        ],
        "intro": [
            _l("sal", "Léo, au hangar de l'île. Huit cents piasses depuis le printemps, pis il sait plus pour quoi.",
               jeu="[knowingly] Léo, au hangar de l'île. [amused] Huit cents piasses depuis le printemps, pis il sait plus pour quoi."),
            _l("sal", "Prends la chaloupe du capitaine, sous le Faubourg. Ramène-moi l'argent, ou une bonne raison.",
               jeu="[matter-of-fact] Prends la chaloupe du capitaine, sous le Faubourg. [softly] Ramène-moi l'argent… ou une bonne raison."),
            _l("sal", "Pis le neveu? Fais ça propre. L'île a la mémoire longue.",
               jeu="[softly] Pis le neveu? [serious] Fais ça propre. [knowingly] L'île a la mémoire longue.")
        ],
        "pendant": [
            _p("sal", "La chaloupe est amarrée sous le Faubourg. Le capitaine sait que tu l'empruntes.", 0,
               jeu="[calm] La chaloupe est amarrée sous le Faubourg. [wryly] Le capitaine sait que tu l'empruntes."),
            _p("sal", "Le hangar, c'est le grand toit de tôle. Léo bouge jamais de devant.", 1,
               jeu="[matter-of-fact] Le hangar, c'est le grand toit de tôle. [amused] Léo bouge jamais de devant."),
            _p("leo", "Les gars! Le jeune veut de l'argent, pis moé j'ai juste des bras!", 3,
               jeu="[deadpan] Les gars! [mischievously] Le jeune veut de l'argent, pis moé j'ai juste des bras!"),
            _p("sal", "Reviens sous le Faubourg. Le capitaine compte ses chaloupes, lui aussi.", 6,
               jeu="[calm] Reviens sous le Faubourg. [amused] Le capitaine compte ses chaloupes, lui aussi.")
        ],
        "accueil": [
            # ⚠️ LA QUESTION : c'est à toi de répondre (`choix`). Léo ne dit ni « Sal » ni son propre nom (sa fiche).
            _a("leo", "Huit cents? J'ai un hangar vide pis une chaloupe qui prend l'eau. Tu veux quoi, au juste?", 2,
               jeu="[deadpan] Huit cents? [matter-of-fact] J'ai un hangar vide pis une chaloupe qui prend l'eau. [mysteriously] Tu veux quoi, au juste?",
               choix=[("coucher", "SAL VEUT SON ARGENT. TOUT DE SUITE."),
                      ("payer", "LAISSE FAIRE. JE PAIE TES 800 $.")]),
            _a("leo", "Tout de suite? Ben les gars du hangar vont avoir leur mot à dire.", 2,
               jeu="[deadpan] Tout de suite? [mischievously] Ben les gars du hangar vont avoir leur mot à dire.",
               branche="coucher"),
            _a("leo", "Toé? Pour moé? J'ai rien vu, pis j'oublierai pas.", 2,
               jeu="[surprised] Toé? Pour moé? [softly] J'ai rien vu… pis j'oublierai pas.",
               branche="payer"),
            _a("leo", "Correct, correct. Huit cents, dans ma boîte à pêche. J'étais pas là, moé.", 4,
               jeu="[sighs] Correct, correct. [matter-of-fact] Huit cents, dans ma boîte à pêche. [deadpan] J'étais pas là, moé.")
        ],
        "fin": [
            _l("sal", "Huit cents, pis pas une cenne de moins. L'île va se rappeler de toi, le neveu.",
               jeu="[satisfied] Huit cents, pis pas une cenne de moins. [knowingly] L'île va se rappeler de toi, le neveu.",
               branche="coucher"),
            _l("sal", "Tiens, ta part. Chez nous, tout se paie, même le mal de mer.",
               jeu="[warmly] Tiens, ta part. [amused] Chez nous, tout se paie, même le mal de mer.",
               branche="coucher"),
            _l("sal", "Huit cents de ta poche, pour un homme qui te doit rien. Ton oncle faisait pareil.",
               jeu="[softly] Huit cents de ta poche, pour un homme qui te doit rien. [tenderly] Ton oncle faisait pareil.",
               branche="payer"),
            _l("sal", "Je les enlève de ta dette. Pis la prochaine fois, laisse-moi mes clients.",
               jeu="[calm] Je les enlève de ta dette. [knowingly] Pis la prochaine fois, laisse-moi mes clients.",
               branche="payer")
        ],
        "echec": [
            _l("sal", "L'île t'a mangé, le neveu? Je mettrai ça sur ta dette, avec le reste.",
               jeu="[coldly] L'île t'a mangé, le neveu? [softly] Je mettrai ça sur ta dette, avec le reste.")
        ]
    }
}
