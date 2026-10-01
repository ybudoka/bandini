"""La mission x03 — voir app/missions/__init__.py pour le moteur.

Le linge propre (M16, arc X, 1er oct. 2026) — le deuxième préparatif du coup. Un livreur des Livraisons Express a
oublié son uniforme chez Rosa (`magasins.TENUES`, `livreur` : il ne se vend pas, elle te le met dans les mains —
`remet`). On l'enfile, on porte un colis de carnets de chèques à la caisse populaire, monsieur Lemire signe le
bordereau (`obtenir`, `table: caisse`, en uniforme : `caisse.js`, la livraison) et Fernand, le vigile, s'habitue à ta
face. Le jour du coup (x04), en uniforme, il ne te reconnaît pas : on entre sans une étoile.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "x03",
    "titre": "Le linge propre",
    "donneur": "rosa",
    "prerequis": ["x01"],
    "recompense": 100,
    "donne": {"message": "FERNAND T'A DIT SALUT : T'ES UN LIVREUR, POUR LUI"},

    # ⚠️ « EN LE PORTANT » (`tenue`, comme f10) : on arrive à la caisse en uniforme, sinon la ligne dit quoi enfiler ;
    # et le gérant ne signe que pour un livreur (`caisse.js`). Rosa se tient dehors : on revient lui montrer.
    "objectifs": [
        {"type": "aller", "texte": "ENFILE L'UNIFORME DE LIVREUR, CHEZ ROSA",
         "lieu": "vetements", "rayon": 6, "remet": "livreur", "tenue": "livreur"},

        {"type": "aller", "texte": "LE COLIS DE LA CAISSE POP, À LA SHOP — EN UNIFORME",
         "lieu": "caisse_pop", "rayon": 6, "tenue": "livreur"},

        {"type": "obtenir", "texte": "LE COLIS À M. LEMIRE, LE GÉRANT : QU'IL SIGNE",
         "objet": "bordereau", "nom": "LE BORDEREAU SIGNÉ", "dessin": "registre", "ou": "caisse_pop",
         "table": "caisse"},

        {"type": "retourner", "texte": "RAPPORTE LE BORDEREAU À ROSA"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Rosa : amusée, précise, l'artisane qui juge le linge avant l'homme. Elle
    # sait ce que Josée prépare et ne le dit pas : elle parle de couleurs et de bonnes manières.
    "dialogue": {
        "appel": [
            _l("rosa", "Rosa, de la boutique. Josée m'a parlé de ton affaire. J'ai le linge qu'il te faut.",
               jeu="[knowingly] Rosa, de la boutique. [quietly] Josée m'a parlé de ton affaire. [amused] J'ai le linge qu'il te faut.")
        ],
        "intro": [
            _l("rosa", "Un livreur des Livraisons Express a oublié son uniforme ici. Une chemise brune, pis l'air pressé.",
               jeu="[amused] Un livreur des Livraisons Express a oublié son uniforme ici. [wryly] Une chemise brune… pis l'air pressé."),
            _l("rosa", "Enfile-la, pis va porter un colis à la caisse pop. Que le vigile s'habitue à ta face.",
               jeu="[calm] Enfile-la, pis va porter un colis à la caisse pop. [knowingly] Que le vigile s'habitue à ta face."),
            _l("rosa", "Le jour où tu reviendras pour vrai, il va te tenir la porte.",
               jeu="[teasing] Le jour où tu reviendras pour vrai… il va te tenir la porte.")
        ],
        "pendant": [
            _p("rosa", "Change-toi dans ma cabine. Le brun te fait un teint de facteur, c'est parfait.", 0,
               jeu="[amused] Change-toi dans ma cabine. [teasing] Le brun te fait un teint de facteur, c'est parfait."),
            _p("rosa", "Le colis, c'est des carnets de chèques. Ça pèse rien, marche comme si c'était lourd.", 1,
               jeu="[knowingly] Le colis, c'est des carnets de chèques. [wryly] Ça pèse rien… marche comme si c'était lourd."),
            _p("rosa", "Le gérant, c'est monsieur Lemire, dans son bureau du fond. Fais-le signer, pis salue Fernand.", 2,
               jeu="[calm] Le gérant, c'est monsieur Lemire, dans son bureau du fond. [amused] Fais-le signer… pis salue Fernand."),
            _p("rosa", "Reviens me montrer le bordereau. Je veux voir la signature de Lemire.", 3,
               jeu="[satisfied] Reviens me montrer le bordereau. [teasing] Je veux voir la signature de Lemire.")
        ],
        "fin": [
            _l("rosa", "Fernand t'a dit salut le jeune? Alors pour lui, t'es un livreur. Pour toujours.",
               jeu="[amused] Fernand t'a dit salut le jeune? [knowingly] Alors pour lui, t'es un livreur. Pour toujours."),
            _l("rosa", "Garde l'uniforme propre. Pis rapporte-le un jour, c'est quand même un vol.",
               jeu="[warmly] Garde l'uniforme propre. [teasing] Pis rapporte-le un jour… c'est quand même un vol.")
        ],
        "echec": [
            _l("rosa", "Fernand t'a regardé deux fois. C'est une fois de trop.",
               jeu="[disappointed] Fernand t'a regardé deux fois. [wryly] C'est une fois de trop.")
        ]
    }
}
