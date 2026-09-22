"""
La mission m1 — voir `app/missions/__init__.py` pour le moteur.
"""
from ._commun import _a, _l, _p

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
        # ⚠️ « Des missions plus longues » (Martin, 22 sept. 2026) : deux étapes de plus, chacune
        # une seule chose neuve et facile — c'est la première minute du joueur. Parler à
        # quelqu'un (ACTION, à côté de lui) : Marco se tient déjà devant le garage.
        {"type": "parler", "cible": "marco", "texte": "PARLE À MARCO, DEVANT LE GARAGE"},
        {"type": "monter", "vehicule": "auto", "ou": RUELLE_DU_CHAR_DE_M1, "texte": "PRENDS LE CHAR DANS LA RUELLE"},
        # Semer la police, à UNE étoile (15 s hors de vue) : le propriétaire « dont personne
        # va s'ennuyer » s'en ennuie. C'est la chute de la promesse de Ti-Guy.
        {"type": "semer", "etoiles": 1, "texte": "LE PROPRIO A APPELÉ LA POLICE — SÈME-LA"},
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
            # ⚠️ La 5e (« passe voir Marco ») suit les deux autres DANS le même `dire` : un
            # `dire` à part après la coupe couperait la 4e, qui joue encore sous elle.
            {"type": "dire", "repliques": [3, 4, 5], "ensemble": True},
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
            {"type": "dire", "repliques": [3]},
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
            _l("ti_guy", "Passe voir Marco au garage avant. Lui, y sait où il dort, le char!",
               jeu="[cheerful] Passe voir Marco au garage avant. [mischievously] Lui, y sait où il dort, le char!"),
        ],
        "fin": [
            _l("ti_guy", "Pas une bosse! T'es ben le neveu de Rocco.",
               jeu="[excited] Pas une bosse! [laughs] T'es ben le neveu de Rocco."),
            _l("ti_guy", "Tiens, la clé de la planque. Dors là, pis fais-toi pas pogner.",
               jeu="[warmly] Tiens, la clé de la planque. Dors là… pis fais-toi pas pogner."),
            _l("ti_guy", "Pis le propriétaire? On y enverra une carte de Noël!",
               jeu="[mischievously] Pis le propriétaire? [laughs] On y enverra une carte de Noël!"),
        ],
        "echec": [_l("ti_guy", "Ouain... On va dire que c'était un essai. Reviens me voir.",
                     jeu="[disappointed] Ouain… On va dire que c'était un essai. [sighs] Reviens me voir.")],
        # PENDANT (2e vague des scènes) : dite quand son objectif commence.
        "pendant": [
            _p("ti_guy", "Heille, le propriétaire s'en ennuie, finalement! Y a appelé les bœufs, sème-les.", 3,
               jeu="[surprised] Heille, le propriétaire s'en ennuie, finalement! [laughs] Y a appelé les bœufs… sème-les."),
            _p("ti_guy", "Beau char! Ramène-le au garage tranquillement, pis évite la police.", 4,
               jeu="[amused] Beau char! Ramène-le au garage tranquillement, pis évite la police."),
        ],
        # ACCUEIL : Marco, la première fois qu'on l'entend — il se nomme (une fois pour la mission),
        # et « le neveu », dit sec, est tout ce qu'il pense de l'héritage (docs/personnages/marco.md).
        "accueil": [
            _a("marco", "Le neveu. Moi, c'est Marco, le Cousin. Le char dort dans la ruelle, les clés dessus.", 1,
               jeu="[wryly] Le neveu. [casually] Moi, c'est Marco, le Cousin. [quietly] Le char dort dans la ruelle, les clés dessus."),
        ],
    },
}
