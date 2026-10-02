"""Le chapitre du lot de Gilles — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague S). La Shop (vague S) commence chez Gilles, à la guérite de la fourrière : s01 (la remorqueuse volée par les Boulonneux) et
s08 (le lot qu'on vide la nuit) — quatre étapes chacune — deviennent deux ACTES : Gilles et ses Boulonneux, de jour
puis de nuit. Rien d'ajouté : deux bagarres, une nuit, deux chars à ramener (6 à 8 minutes). s12 (le dernier char du
lot, cinq remorquages) reste une mission : 423 s au chronomètre de Martin, elle dure déjà.

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : l'appel de s08 perd « C'est Gilles, de la fourrière. » — la même voix,
  coupée au silence ;
- l'échec `vehicule_detruit` (la remorqueuse, l'auto reprise) vaut pour les deux actes, comme pour les deux missions.
- s02 (et Ti-Loup, qui arrive après s01) attend s01, l'acte 1 ; s12 attend s08, l'acte 2.
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "lot_de_gilles",
    "titre": "Le lot de Gilles",
    "donneur": "gilles",
    "prerequis": ["m6"],
    "remplace": ["s01", "s08"],
    "recompense": 200,
    "donne": {"message": "GILLES VA DORMIR POUR VRAI"},
    "echec": ["mort", "arrete", "vehicule_detruit"],

    "objectifs": [
        # --- Acte 1 (s01, « Gilles à la guérite »).
        {"type": "acte", "texte": "ACTE 1 — GILLES À LA GUÉRITE", "donneur": "gilles"},  # 0
        {"type": "parler", "texte": "DEMANDE À TI-PAUL OÙ ELLE EST PASSÉE", "cible": "tipaul"},  # 1
        {"type": "monter", "texte": "REPRENDS LA REMORQUEUSE", "vehicule": "remorqueuse", "ou": "zone:boulonneux"},  # 2
        {"type": "tuer", "texte": "LES BOULONNEUX REVIENNENT LA CHERCHER", "groupe": "boulonneux", "n": 3, "ou": "zone:boulonneux", "loin": 10},  # 3
        {"type": "livrer", "texte": "RAMÈNE-LA À LA FOURRIÈRE", "lieu": "fourriere", "rayon": 4, "donne": {"rabais": {"fourriere": 0.8}, "message": "LE RACHAT AU LOT, MOINS CHER", "prime": 250}},  # 4
        # --- Acte 2 (s08, « Le lot se fait vider »).
        {"type": "acte", "texte": "ACTE 2 — LE LOT SE FAIT VIDER", "donneur": "gilles"},  # 5
        {"type": "aller", "texte": "ATTENDS LA NUIT À LA FOURRIÈRE", "lieu": "fourriere", "rayon": 6, "nuit": True},  # 6
        {"type": "tuer", "texte": "TROIS BOULONNEUX VIDENT LE LOT — COUCHE-LES", "groupe": "boulonneux", "n": 3, "ou": "donneur", "loin": 8},  # 7
        {"type": "monter", "texte": "UN QUATRIÈME EST PARTI AVEC UNE AUTO — REPRENDS-LA", "vehicule": "auto", "ou": "zone:boulonneux"},  # 8
        {"type": "livrer", "texte": "RAMÈNE-LA AU LOT", "lieu": "fourriere", "rayon": 4},  # 9
    ],

    # s01 — Le jeu de chaque réplique (`jeu=`) — Gilles : las, proche de la retraite, mais
    # encore fier de son lot ; jamais pressé, sauf quand on touche à SA remorqueuse.
    # s08 — Le jeu de chaque réplique (`jeu=`) — Gilles : las, lent, fier de son lot ; la nuit
    # l'inquiète plus qu'il ne le dit, et le soulagement vient avec la dernière case pleine.
    "dialogue": {
        "appel": [
            _l("gilles", "C'est Gilles, de la fourrière. Un Boulonneux est parti avec ma remorqueuse. J'ai besoin d'un coup de main.", jeu="[gravely] C'est Gilles, de la fourrière. Un Boulonneux est parti avec ma remorqueuse. [matter-of-fact] J'ai besoin d'un coup de main."),
        ],
        "intro": [
            _l("gilles", "Ils l'ont garée dans leur coin, en zone des Boulonneux. Trente ans que je la conduis, cette machine-là.", jeu="[somber] Ils l'ont garée dans leur coin, en zone des Boulonneux. [tenderly] Trente ans que je la conduis, cette machine-là."),
            _l("gilles", "Ramène-la icitte, au lot. Je pars bientôt à la retraite, je veux pas la perdre avant.", jeu="[firmly] Ramène-la icitte, au lot. [quietly] Je pars bientôt à la retraite… je veux pas la perdre avant."),
            _l("gilles", "Passe voir Ti-Paul avant, au dépanneur. Rien passe dans cette ville-là sans qu'il le sache.", jeu="[matter-of-fact] Passe voir Ti-Paul avant, au dépanneur. [wryly] Rien passe dans cette ville-là sans qu'il le sache."),
        ],
        "fin": [
            _l("gilles", "Toutes dans leurs cases. Je vais dormir pour vrai, à soir.", jeu="[relieved] Toutes dans leurs cases. [tenderly] Je vais dormir pour vrai, à soir."),
            _l("gilles", "Encore un hiver, pis je rends les clés. Mais pas à des Boulonneux.", jeu="[somber] Encore un hiver, pis je rends les clés. [firmly] Mais pas à des Boulonneux."),
        ],
        "echec": [
            _e("gilles", "Perdue, ma remorqueuse... Trente ans, pis ça finit de même.", 0, jeu="[disappointed] Perdue, ma remorqueuse… [somber] Trente ans, pis ça finit de même."),
            _e("gilles", "Le lot est plus vide que ma retraite. C'est pas une belle nuit.", 5, jeu="[somber] Le lot est plus vide que ma retraite. [gravely] C'est pas une belle nuit."),
        ],
        "pendant": [
            _p("gilles", "Fais attention en la sortant de là. Elle est vieille, mais elle est encore à moi.", 2, jeu="[gravely] Fais attention en la sortant de là. [tenderly] Elle est vieille, mais elle est encore à moi."),
            _p("gilles", "Ils reviennent la chercher. Tiens-leur tête, le jeune, trente ans, ça se laisse pas voler deux fois.", 3, jeu="[worried] Ils reviennent la chercher. [firmly] Tiens-leur tête, le jeune… trente ans, ça se laisse pas voler deux fois."),
            # Acte 2 : la fin de s01, en personne ; puis l'appel et l'intro de s08.
            _p("gilles", "Ma vieille remorqueuse. Pas une égratignure de plus.", 5, jeu="[relieved] Ma vieille remorqueuse. [warmly] Pas une égratignure de plus."),
            _p("gilles", "Merci, le jeune. Reviens icitte, je te ferai un prix sur le rachat.", 5, jeu="[satisfied] Merci, le jeune. [matter-of-fact] Reviens icitte, je te ferai un prix sur le rachat."),
            # ⚠️ Coupée (2 oct. 2026) : « C'est Gilles, de la fourrière. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("gilles", "Des chars disparaissent du lot la nuit, pis c'est pas ma remorqueuse.", 5, jeu="[somber] Des chars disparaissent du lot la nuit… pis c'est pas ma remorqueuse."),
            _p("gilles", "Trente ans que je garde ce lot-là. J'ai jamais perdu un char, pis j'commencerai pas à la fin.", 5, jeu="[somber] Trente ans que je garde ce lot-là. [firmly] J'ai jamais perdu un char… pis j'commencerai pas à la fin."),
            _p("gilles", "Les Boulonneux passent par la clôture quand je cogne des clous. Attends-les avec moi, à soir.", 5, jeu="[gravely] Les Boulonneux passent par la clôture quand je cogne des clous. [tenderly] Attends-les avec moi, à soir."),
            _p("gilles", "La nuit tombe. Moi, je fais semblant de dormir, j'suis bon là-dedans.", 6, jeu="[quietly] La nuit tombe. [amused] Moi, je fais semblant de dormir… j'suis bon là-dedans."),
            _p("gilles", "Les v'là, par la clôture! Fais-les repartir comme ils sont venus.", 7, jeu="[gravely] Les v'là, par la clôture! [firmly] Fais-les repartir… comme ils sont venus."),
            _p("gilles", "Le quatrième a pris une auto! Elle est à la ville, le jeune, pas à eux.", 8, jeu="[worried] Le quatrième a pris une auto! [firmly] Elle est à la ville, le jeune… pas à eux."),
            _p("gilles", "Ramène-la icitte. Je la veux dans sa case, pas dans leur cour.", 9, jeu="[gravely] Ramène-la icitte. [somber] Je la veux dans sa case… pas dans leur cour."),
        ],
        "accueil": [
            _a("tipaul", "Salut, l'ami, c'est Ti-Paul! Les gars de la remorqueuse ont pris douze caisses icitte. À crédit!", 1, jeu="[cheerful] Salut, l'ami, c'est Ti-Paul! [knowingly] Les gars de la remorqueuse ont pris douze caisses icitte… à crédit!"),
        ],
    },
}
