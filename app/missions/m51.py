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

        # « Des missions plus longues » (22 sept. 2026) : un jeune agent qui croit encore au règlement a
        # vu passer l'enveloppe de Ti-Paul — on le sème (DEHORS, aux Érables : jamais une étoile posée
        # dedans, `dernierVu` serait en coordonnées de pièce). Puis Bouchard tente sa chance au
        # Brouillard : Josée ne donne pas — le seul « non » de la tournée, et il le sait.
        {"type": "semer", "texte": "UN AGENT HONNÊTE TE SUIT — SÈME-LE",
         "etoiles": 1},

        {"type": "parler", "texte": "PASSE SALUER JOSÉE, AU BAR",
         "cible": "josee"},

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
            _p("bouchard", "Trois enveloppes? Rapporte-les-moi. Pis touche à rien, je sais combien y en a.", 5,
               jeu="[gruffly] Trois enveloppes? Rapporte-les-moi. [menacingly] Pis touche à rien… je sais combien y en a."),
            # Au combiné, eux aussi : il est dans son casse-croûte, et il a peur d'un seul agent.
            _p("bouchard", "Y a un jeune agent qui croit encore au règlement. Perds-le, pis vite.", 3,
               jeu="[nervously] Y a un jeune agent qui croit encore au règlement. [gruffly] Perds-le, pis vite."),
            _p("bouchard", "Arrête au Brouillard. Josée donne jamais, mais je lui demande pareil.", 4,
               jeu="[matter-of-fact] Arrête au Brouillard. [deadpan] Josée donne jamais… mais je lui demande pareil.")
        ],
        "fin": [
            _l("bouchard", "Trois enveloppes, pas une plainte. Tu commences à comprendre comment ça marche, ici.",
               jeu="[satisfied] Trois enveloppes, pas une plainte. [knowingly] Tu commences à comprendre comment ça marche… ici."),
            _l("bouchard", "Josée a rien donné? Ben, on va dire qu'elle a donné.",
               jeu="[nervously] Josée a rien donné? [deadpan] Ben… on va dire qu'elle a donné."),
            _l("bouchard", "Ta part est dans ta poche. Pis si on te demande, c'était pour les orphelins.",
               jeu="[matter-of-fact] Ta part est dans ta poche. [deadpan] Pis si on te demande… c'était pour les orphelins.")
        ],
        "echec": [
            _l("bouchard", "Ça, c'est de la tournée ratée. Reviens quand tu sauras marcher droit.",
               jeu="[annoyed] Ça, c'est de la tournée ratée. [gruffly] Reviens quand tu sauras marcher droit.")
        ],
        # La poignée de main, dite : chacun paie à sa façon — la vieille qui râle mais donne, la
        # cantinière qui grogne, le bavard qui en profite pour se plaindre. Comptées APRÈS `pendant`
        # (`PARTIES`) : `thibodeau-m51-11`, `lulu-m51-12`, `tipaul-m51-13`, `josee-m51-14` (22 sept. 2026 :
        # une fin et deux `pendant` de plus les ont décalées ; les mp3 se renomment par leur texte).
        "accueil": [
            _a("thibodeau", "Le sergent, encore? Tiens, mon p'tit. Dis-lui que j'ai une famille à nourrir, moi aussi.", 0,
               jeu="[annoyed] Le sergent, encore? [softly] Tiens, mon p'tit… Dis-lui que j'ai une famille à nourrir, moi aussi."),
            _a("lulu", "Il mange chez moi depuis dix ans sans payer! Bon, tiens, pour la police.", 1,
               jeu="[annoyed] Il mange chez moi depuis dix ans sans payer! [warmly] Bon… tiens, pour la police."),
            _a("tipaul", "Une enveloppe pour Bouchard? Tiens! Pis dis-lui que mon parking a besoin d'une patrouille.", 2,
               jeu="[cheerful] Une enveloppe pour Bouchard? Tiens! [mischievously] Pis dis-lui que mon parking a besoin d'une patrouille."),
            # Le seul « non » : Josée ne hausse pas le ton, elle le connaît.
            _a("josee", "Bouchard t'envoie quêter chez moi. Dis-lui que je connais son prix.", 4,
               jeu="[coldly] Bouchard t'envoie quêter chez moi. [menacingly] Dis-lui que je connais son prix.")
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
