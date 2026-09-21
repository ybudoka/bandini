"""La mission m51 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "m51",
    "titre": "La tournée du sergent",
    "donneur": "bouchard",
    # ⚠️ Après e01 ET q02 : Ti-Paul et Lulu nous connaissent — c'est pour ça qu'ils paient.
    "prerequis": ["e01", "q02"],
    "recompense": 350,
    "donne": {"message": "TROIS ENVELOPPES, ZÉRO PLAINTE"},

    # La forme de m6 (serrer la main), le ton de m4 (le sergent et ses combines). Chaque objectif
    # `parler` nomme sa CIBLE : on l'accomplit en lui serrant la main, jamais en s'approchant de sa
    # tuile. Le dernier est un `aller` : Bouchard se tient DEDANS, il n'y a pas de `retourner`.
    "objectifs": [
        {"type": "parler", "texte": "PARLE À MADAME THIBODEAU, AU KIOSQUE",
         "cible": "thibodeau"},

        {"type": "parler", "texte": "PARLE À LULU, À LA CANTINE",
         "cible": "lulu"},

        {"type": "parler", "texte": "PARLE À TI-PAUL, AU DÉPANNEUR",
         "cible": "tipaul"},

        {"type": "aller", "texte": "RAPPORTE LES ENVELOPPES AU CASSE-CROÛTE",
         "lieu": "casse_croute", "rayon": 3}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Bouchard, la tournée : bourru même quand il plaisante.
    # Il ne hausse jamais le ton — le cynisme se joue à plat (`deadpan`, `matter-of-fact`), et la
    # poignée de main de chacun garde son registre : la vieille râle et donne, la cantinière
    # grogne, le bavard en profite.
    "dialogue": {
        "appel": [
            _l("bouchard", "Salut, le jeune, c'est Bouchard. J'ai une petite tournée à te confier. Passe au casse-croûte.",
               jeu="[gruffly] Salut, le jeune, c'est Bouchard. J'ai une petite tournée à te confier. Passe au casse-croûte.")
        ],
        "intro": [
            _l("bouchard", "C'est bientôt la cotisation de la Fraternité des policiers. Les commerçants donnent volontiers.",
               jeu="[matter-of-fact] C'est bientôt la cotisation de la Fraternité des policiers. [knowingly] Les commerçants donnent… volontiers."),
            _l("bouchard", "Passe voir Madame Thibodeau, Lulu pis Ti-Paul. Pis souris: ça les rend généreux.",
               jeu="[gruffly] Passe voir Madame Thibodeau, Lulu pis Ti-Paul. [deadpan] Pis souris… ça les rend généreux.")
        ],
        "pendant": [
            # Au combiné : il est dans son casse-croûte, on a les poches pleines.
            _p("bouchard", "Trois enveloppes? Rapporte-les-moi. Pis touche à rien, je sais combien y en a.", 3,
               jeu="[gruffly] Trois enveloppes? Rapporte-les-moi. [menacingly] Pis touche à rien… je sais combien y en a.")
        ],
        "fin": [
            _l("bouchard", "Trois enveloppes, pas une plainte. Tu commences à comprendre comment ça marche, ici.",
               jeu="[satisfied] Trois enveloppes, pas une plainte. [knowingly] Tu commences à comprendre comment ça marche… ici."),
            _l("bouchard", "Ta part est dans ta poche. Pis si on te demande, c'était pour les orphelins.",
               jeu="[matter-of-fact] Ta part est dans ta poche. [deadpan] Pis si on te demande… c'était pour les orphelins.")
        ],
        "echec": [
            _l("bouchard", "Ça, c'est de la tournée ratée. Reviens quand tu sauras marcher droit.",
               jeu="[annoyed] Ça, c'est de la tournée ratée. [gruffly] Reviens quand tu sauras marcher droit.")
        ],
        # La poignée de main, dite : chacun paie à sa façon — la vieille qui râle mais donne, la
        # cantinière qui grogne, le bavard qui en profite pour se plaindre. Comptées APRÈS `pendant`
        # (`PARTIES`) : `thibodeau-m51-8`, `lulu-m51-9`, `tipaul-m51-10`.
        "accueil": [
            _a("thibodeau", "Le sergent, encore? Tiens, mon p'tit. Dis-lui que j'ai une famille à nourrir, moi aussi.", 0,
               jeu="[annoyed] Le sergent, encore? [softly] Tiens, mon p'tit… Dis-lui que j'ai une famille à nourrir, moi aussi."),
            _a("lulu", "Il mange chez moi depuis dix ans sans payer! Bon, tiens, pour la police.", 1,
               jeu="[annoyed] Il mange chez moi depuis dix ans sans payer! [warmly] Bon… tiens, pour la police."),
            _a("tipaul", "Une enveloppe pour Bouchard? Tiens! Pis dis-lui que mon parking a besoin d'une patrouille.", 2,
               jeu="[cheerful] Une enveloppe pour Bouchard? Tiens! [mischievously] Pis dis-lui que mon parking a besoin d'une patrouille.")
        ]
    },

    # Intention (intro) : le joueur comprend que « la cotisation » n'est pas volontaire — Bouchard croise
    # les bras (l'autorité, sa gestuelle depuis m4) en la nommant, puis la caméra sort voir le kiosque
    # de Madame Thibodeau au moment où il dit son nom : la première porte de la tournée.
    # ⚠️ Il parle DEDANS : `coupe` (et non `camera`), et la première réplique n'est PAS `ensemble` — la
    # seconde ne la coupe pas. La fin est celle du défaut : on est à sa porte, il est dedans, une coupe
    # chez lui.
    "scenes": {
        "intro": [
            { "type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True },
            { "type": "dire", "repliques": [1] },
            { "type": "coupe", "vers": "chez:thibodeau", "ferme": 20, "ouvre": 20, "tient": 130, "ensemble": True },
            { "type": "dire", "repliques": [2] }
        ]
    }
}
