"""La mission e11 — voir app/missions/__init__.py pour le moteur.

Le maire te reçoit (M16, arc E, 1er oct. 2026) — un CHOIX DANS UN DIALOGUE. Le dossier volé à la villa (e07) dort à la
planque. Le maire Tanguay, dans sa chambre de l'Hôtel Bandini (il n'y est qu'entre m97 et m98), le rachète mille
piastres. C'est toi qui réponds :

- « VENDU, MONSIEUR LE MAIRE. » — la planque, puis sa chambre : mille piastres, et il garde son quatrième mandat en tête.
- « IL EST PAS À VENDRE. » — la planque, puis Louise au kiosque ; les gardes du maire arrivent trop tard pour la une, et
  on remonte lui dire non en pleine face (la fin se dit devant lui, d'un bord comme de l'autre).
"""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "e11",
    "titre": "Le maire te reçoit",
    "donneur": "maire",
    "prerequis": ["e07", "m97"],
    "recompense": 1000,
    "donne": {"message": "LE MAIRE A RACHETÉ SON DOSSIER"},
    "branches": {
        "garder": {"recompense": 300, "donne": {"message": "LOUISE A SA UNE : LE DOSSIER DU MAIRE"}},
    },

    # ⚠️ La question se pose à la poignée de main (`parler`, son `accueil`), pas dans l'intro : une scène d'intro se joue
    # seule, sans qu'on y réponde (`test_missions_en_scene_js`) — le patron de d09.
    "objectifs": [
        {"type": "parler", "texte": "RÉPONDS AU MAIRE : MILLE PIASTRES, OU TA JOURNALISTE", "cible": "maire"},

        {"type": "aller", "texte": "LE DOSSIER DU MAIRE EST À LA PLANQUE", "lieu": "planque", "rayon": 4},

        {"type": "parler", "texte": "PORTE LE DOSSIER À LOUISE, AU KIOSQUE", "cible": "louise", "branche": "garder"},

        {"type": "tuer", "texte": "LES GARDES DU MAIRE ARRIVENT — COUCHE-LES", "branche": "garder",
         "groupe": "chevreuils", "pieton": "garde", "n": 2, "loin": 10},

        {"type": "parler", "texte": "VA LUI DIRE NON EN PLEINE FACE, À L'HÔTEL", "cible": "maire", "branche": "garder"},

        {"type": "parler", "texte": "RAPPORTE LE DOSSIER AU MAIRE, À L'HÔTEL", "cible": "maire", "branche": "vendre"},
    ],

    # Intention (intro, dedans) : le maire en robe de chambre, jovial, qui achète comme il respire ; la caméra sort voir
    # la planque (le dossier y dort), puis revient pour la question — et c'est le joueur qui y répond.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:planque", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3, 4]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — le maire : jovial, lisse, « mon garçon » ; il ne menace jamais, il prévient.
    # Louise (l'autre côté) : vite, en phrases de manchette, « mon beau ».
    "dialogue": {
        "appel": [
            _l("maire", "Réal Tanguay, maire de Baie-des-Brumes. Monte donc à ma chambre, mon garçon, qu'on se parle.",
               jeu="[cheerful] Réal Tanguay, maire de Baie-des-Brumes. [smugly] Monte donc à ma chambre, mon garçon, qu'on se parle.")
        ],
        "intro": [
            _l("maire", "Mon dossier, mon garçon. Celui qui est parti de ma villa. Je te le rachète, mille piastres.",
               jeu="[amused] Mon dossier, mon garçon. [knowingly] Celui qui est parti de ma villa. [smugly] Je te le rachète, mille piastres."),
            _l("maire", "Ou tu le donnes à ta journaliste, pis je perds mon quatrième mandat. Toi, t'y gagnes quoi?",
               jeu="[wryly] Ou tu le donnes à ta journaliste, pis je perds mon quatrième mandat. [knowingly] Toi, t'y gagnes quoi?"),
            _l("maire", "Prends ton temps, mon garçon. Un verre de champagne, pis tu me réponds.",
               jeu="[amused] Prends ton temps, mon garçon. [smugly] Un verre de champagne, pis tu me réponds."),
            _l("maire", "Mais réponds-moi avant de sortir. Un maire, ça déteste attendre.",
               jeu="[cheerful] Mais réponds-moi avant de sortir. [wryly] Un maire, ça déteste attendre.")
        ],
        "pendant": [
            _p("maire", "Il est dans ta planque, je le sais. Je sais toujours où sont mes affaires.", 1,
               jeu="[smugly] Il est dans ta planque, je le sais. [amused] Je sais toujours où sont mes affaires."),
            _p("maire", "Monte, monte. Le champagne est au frais, pis la porte est pas barrée.", 5,
               jeu="[cheerful] Monte, monte. [amused] Le champagne est au frais, pis la porte est pas barrée.",
               branche="vendre"),
            _p("louise", "Le dossier du maire? Au kiosque, mon beau, tout de suite! J'arrête les presses!", 2,
               jeu="[excited] Le dossier du maire? [firmly] Au kiosque, mon beau, tout de suite! J'arrête les presses!",
               branche="garder"),
            _p("louise", "Des gros bras en complet! Couche-les, mon beau, j'ai mon kodak.", 3,
               jeu="[nervously] Des gros bras en complet! [excited] Couche-les, mon beau, j'ai mon kodak.",
               branche="garder"),
            _p("louise", "La une est sous presse. Va donc y dire en pleine face, mon beau, ça va le réveiller.", 4,
               jeu="[playfully] La une est sous presse. [excited] Va donc y dire en pleine face, mon beau, ça va le réveiller.",
               branche="garder")
        ],
        "fin": [
            _l("maire", "Mille piastres, pis on se connaît pas. Ton oncle aussi savait compter.",
               jeu="[smugly] Mille piastres, pis on se connaît pas. [knowingly] Ton oncle aussi savait compter.",
               branche="vendre"),
            _l("maire", "Prends un verre en sortant, mon garçon. C'est la ville qui paie.",
               jeu="[cheerful] Prends un verre en sortant, mon garçon. [amused] C'est la ville qui paie.",
               branche="vendre"),
            _l("maire", "Elle aura sa une, pis moi j'aurai mes avocats. On verra qui lit le plus vite.",
               jeu="[wryly] Elle aura sa une, pis moi j'aurai mes avocats. [smugly] On verra qui lit le plus vite.",
               branche="garder"),
            _l("maire", "T'as du front, mon garçon. Ton oncle en avait aussi. Regarde où ça l'a mené.",
               jeu="[impressed] T'as du front, mon garçon. [knowingly] Ton oncle en avait aussi. Regarde où ça l'a mené.",
               branche="garder")
        ],
        # ⚠️ LA QUESTION (`choix`), à la poignée de main ; ses deux réponses, chacune sur sa branche.
        "accueil": [
            _a("maire", "Alors, mon garçon? Mille piastres, ou ta journaliste?", 0,
               jeu="[smugly] Alors, mon garçon? [knowingly] Mille piastres, ou ta journaliste?",
               choix=[("vendre", "VENDU, MONSIEUR LE MAIRE."),
                      ("garder", "IL EST PAS À VENDRE.")]),
            _a("maire", "Un homme raisonnable! Va le chercher, je fais monter du champagne.", 0,
               jeu="[cheerful] Un homme raisonnable! [amused] Va le chercher, je fais monter du champagne.",
               branche="vendre"),
            _a("maire", "Dommage. J'ai des amis qui aiment pas les journaux, mon garçon. Je te préviens, c'est tout.", 0,
               jeu="[wryly] Dommage. [knowingly] J'ai des amis qui aiment pas les journaux, mon garçon. [smugly] Je te préviens, c'est tout.",
               branche="garder")
        ],
        "echec": [
            _l("maire", "T'as perdu mon dossier? Ben voyons. Dans cette ville, tout le monde perd, à la fin.",
               jeu="[amused] T'as perdu mon dossier? Ben voyons. [smugly] Dans cette ville, tout le monde perd, à la fin.")
        ]
    }
}
