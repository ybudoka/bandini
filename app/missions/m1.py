"""
La mission m1 — voir `app/missions/__init__.py` pour le moteur.
"""
from ._commun import _l, _p

#: Ou dort le char de M1. ⚠️ Demande de Martin (17 sept. 2026) : la ruelle la
#: plus proche du garage est a six tuiles — le char naissait DANS l'ecran, sous
#: les yeux du joueur, et le ramener tenait en trois secondes. A vingt-quatre, il
#: faut le chercher au GPS et rouler pour de vrai. ⚠️ UNE constante, parce que
#: DEUX lecteurs : l'objectif qui y pose le char, et la coupe de l'intro qui va
#: le montrer. Deux chaines, et la camera filmerait une ruelle vide.
RUELLE_DU_CHAR_DE_M1 = "ruelle:garage:24"

MISSION = {
    "slug": "m1", "titre": "Bienvenue en ville", "donneur": "ti_guy", "prerequis": [],
    "recompense": 100, "phase": 1, "echec": ["arrete", "vehicule_detruit"],
    "donne": {"message": "LA CLÉ DE LA PLANQUE"},
    "objectifs": [
        {"type": "aller", "lieu": "garage", "rayon": 4, "texte": "VA AU GARAGE"},
        {"type": "monter", "vehicule": "auto", "ou": RUELLE_DU_CHAR_DE_M1, "texte": "PRENDS LE CHAR DANS LA RUELLE"},
        {"type": "livrer", "lieu": "garage", "rayon": 4, "sans_degats": True, "texte": "RAMÈNE-LE AU GARAGE, SANS BOSSE"},
    ],
    # Ti-Guy montre le garage, et la caméra va voir la ruelle où dort le char.
    # ⚠️ Il y DORT DÉJÀ : les chars des objectifs `monter` d'une mission se posent
    # à son début (`Histoire.poser`), pas au tour de leur objectif — sinon la
    # coupe filme une ruelle vide. À la fin, Ti-Guy sort du garage, tend la clé et
    # y rentre : c'est ce qui le fait quitter le terminus (`parti_apres`), plus un
    # `if` dans `reussir()`.
    "scenes": {
        "intro": [
            {"type": "dire", "repliques": [1, 2]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "porte:garage", "duree": 70,
             "ensemble": True},
            {"type": "dire", "repliques": [3, 4], "ensemble": True},
            {"type": "attendre", "duree": 30},
            {"type": "coupe", "vers": RUELLE_DU_CHAR_DE_M1, "ferme": 20, "ouvre": 20, "tient": 150},
        ],
        "fin": [
            {"type": "sortir", "acteur": "ti_guy", "de": "porte:garage", "vers": "joueur"},
            {"type": "marcher", "acteur": "ti_guy", "vers": "joueur", "pres": 22, "duree": 50},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "ti_guy", "geste": "donner", "vers": "joueur", "duree": 60,
             "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "entrer", "acteur": "ti_guy", "dans": "porte:garage", "duree": 50},
        ],
    },
    # Le jeu de chaque réplique (`jeu=`) — Ti-Guy : content de te voir, puis complice.
    "dialogue": {
        "appel": [],
        "intro": [
            _l("ti_guy", "Heille, le neveu de Rocco! C'est moi, Ti-Guy, tu me replaces pas? T'as fait bon voyage?",
               jeu="[excited] Heille, le neveu de Rocco! C'est moi, Ti-Guy, tu me replaces pas? [warmly] T'as fait bon voyage?"),
            _l("ti_guy", "Rocco est parti se faire oublier. Le garage, c'est toi qui le tiens, astheure.",
               jeu="[quietly] Rocco est parti se faire oublier. Le garage… c'est toi qui le tiens, astheure."),
            _l("ti_guy", "Y a un char qui traîne dans une ruelle, un peu plus loin. Personne va s'en ennuyer.",
               jeu="[mischievously] Y a un char qui traîne dans une ruelle, un peu plus loin. Personne va s'en ennuyer."),
            _l("ti_guy", "Ramène-le au garage sans le bosser, pis sans que personne te voie.",
               jeu="[serious] Ramène-le au garage sans le bosser… pis sans que personne te voie."),
        ],
        "fin": [
            _l("ti_guy", "Pas une bosse! T'es ben le neveu de Rocco.",
               jeu="[excited] Pas une bosse! [laughs] T'es ben le neveu de Rocco."),
            _l("ti_guy", "Tiens, la clé de la planque. Dors là, pis fais-toi pas pogner.",
               jeu="[warmly] Tiens, la clé de la planque. Dors là… pis fais-toi pas pogner."),
        ],
        "echec": [_l("ti_guy", "Ouain... On va dire que c'était un essai. Reviens me voir.",
                     jeu="[disappointed] Ouain… On va dire que c'était un essai. [sighs] Reviens me voir.")],
        # PENDANT (2e vague des scènes) : dite quand son objectif commence.
        "pendant": [_p("ti_guy", "Beau char! Ramène-le au garage tranquillement, pis évite la police.", 2,
                       jeu="[amused] Beau char! Ramène-le au garage tranquillement, pis évite la police.")],
    },
}
