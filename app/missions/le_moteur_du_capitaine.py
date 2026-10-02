"""Le chapitre du moteur du capitaine — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague I). L'île commence au bout du quai : q08 (le moteur volé du capitaine Bérubé, rattrapé) et i01 (la chaloupe qui tourne,
la première traversée jusqu'au hangar de Léo) — deux et trois étapes, deux ACTES (5 à 6 minutes).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : l'appel de i01 perd « Bérubé. » — la même voix, coupée au silence ;
- la scène d'intro de q08 reste celle du chapitre ; la fin de i01 (Léo, devant son hangar) reste celle du chapitre.
- Ce qui attendait i01 l'attend encore — l'acte 2 (le reste de l'île, h08, d09, p12) : un prérequis peut viser un acte.
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "le_moteur_du_capitaine",
    "titre": "Le moteur du capitaine",
    "donneur": "berube",
    "prerequis": ["m6"],
    "remplace": ["q08", "i01"],
    "recompense": 120,
    "donne": {"message": "L'ÎLE-AUX-CORNEILLES : LÉO TE CONNAÎT"},

    "objectifs": [
        # --- Acte 1 (q08, « Le moteur du capitaine »).
        # Le moteur du capitaine (M16, arc Q, 30 sept. 2026). Le capitaine Bérubé garde, en plus de son traversier, une vieille
        # chaloupe à moteur pour « aller voir l'île quand le bon Dieu le permet ». Deux jeunes lui ont volé le moteur hors-bord
        # et filent avec, dans la boîte d'un pick-up. On les rattrape, le moteur tombe, on le rapporte au bout du quai. C'est
        # elle, la chaloupe, qui ouvre l'arc de l'île (i01).
        {"type": "acte", "texte": "ACTE 1 — LE MOTEUR DU CAPITAINE", "donneur": "berube"},  # 0
        {"type": "ramasser", "texte": "DEUX JEUNES FILENT AVEC LE MOTEUR : RATTRAPE-LES", "cible": "fuyard", "vehicule": "auto"},  # 1
        {"type": "retourner", "texte": "RAPPORTE LE MOTEUR AU CAPITAINE, AU BOUT DU QUAI", "donne": {"message": "LA CHALOUPE DU CAPITAINE A RETROUVÉ SON MOTEUR", "prime": 200}},  # 2
        # --- Acte 2 (i01, « Le moteur tourne »).
        # Le moteur tourne (M16, arc I « L'Île-aux-Corneilles », 30 sept. 2026). La chaloupe du capitaine marche enfin (q08).
        # Il a une caisse d'outils promise depuis l'été à Léo, qui garde le hangar de l'île ; ses jambes, elles, ne font plus
        # la traversée. On prend la chaloupe, on traverse la baie, on accoste près du hangar, et on met pour la première fois
        # le pied sur l'île — Léo ne pose pas de questions, et il n'en répond pas non plus.
        {"type": "acte", "texte": "ACTE 2 — LE MOTEUR TOURNE", "donneur": "berube"},  # 3
        {"type": "monter", "texte": "LA CHALOUPE DU CAPITAINE, AMARRÉE SOUS LE FAUBOURG", "vehicule": "bateau", "ou": "amarrage:bar", "prete": "berube"},  # 4
        {"type": "livrer", "texte": "TRAVERSE LA BAIE JUSQU'AU HANGAR DE L'ÎLE", "lieu": "amarrage:hangar_ile", "rayon": 6},  # 5
        {"type": "parler", "texte": "LA CAISSE D'OUTILS À LÉO, DEVANT SON HANGAR", "cible": "leo"},  # 6
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # q08 — Le jeu de chaque réplique (`jeu=`) — Bérubé : posé, un peu solennel, des images de marin ; il ne pose pas de
    # question, et il ne se fâche pas — il constate.
    "dialogue": {
        "appel": [
            _l("berube", "Capitaine Bérubé, du traversier. On m'a volé un moteur, pis je cours plus assez vite.", jeu="[calm] Capitaine Bérubé, du traversier. [wryly] On m'a volé un moteur, pis je cours plus assez vite."),
        ],
        "intro": [
            _l("berube", "Ma chaloupe, c'est pour aller voir l'île, quand le bon Dieu et la marée le permettent.", jeu="[calm] Ma chaloupe, c'est pour aller voir l'île, quand le bon Dieu et la marée le permettent."),
            _l("berube", "Deux jeunes ont dévissé le moteur à l'aube. Il est dans la boîte d'un pick-up, qui file.", jeu="[matter-of-fact] Deux jeunes ont dévissé le moteur à l'aube. [firmly] Il est dans la boîte d'un pick-up, qui file."),
            _l("berube", "Ramène-le-moi. Je te demanderai pas comment.", jeu="[knowingly] Ramène-le-moi. [calm] Je te demanderai pas comment."),
        ],
        "fin": [
            _l("berube", "Léo a eu sa caisse? Alors l'île te connaît, astheure. Elle oublie pas vite.", jeu="[warmly] Léo a eu sa caisse? [knowingly] Alors l'île te connaît, astheure. Elle oublie pas vite."),
            _l("berube", "Tiens, pour l'essence. La chaloupe, elle, boit plus que moi.", jeu="[wryly] Tiens, pour l'essence. [calm] La chaloupe, elle, boit plus que moi."),
        ],
        "echec": [
            _e("berube", "Le moteur est parti. La chaloupe restera au quai, comme moi.", 0, jeu="[somber] Le moteur est parti. [calm] La chaloupe restera au quai, comme moi."),
            _e("berube", "La caisse est au fond de la baie. Léo attendra encore un été.", 3, jeu="[somber] La caisse est au fond de la baie. [calm] Léo attendra encore un été."),
        ],
        "pendant": [
            _p("berube", "Ils ont pris le chemin du pont. Un moteur, ça pèse ; ils iront pas loin.", 1, jeu="[matter-of-fact] Ils ont pris le chemin du pont. [calm] Un moteur, ça pèse ; ils iront pas loin."),
            _p("berube", "Je t'attends au bout du quai. Mets-le pas à l'eau, il nage pas mieux que moi.", 2, jeu="[calm] Je t'attends au bout du quai. [wryly] Mets-le pas à l'eau, il nage pas mieux que moi."),
            # Acte 2 : la fin de q08, en personne ; puis l'appel et l'intro de i01.
            _p("berube", "Un Johnson de cinquante-huit. Il a plus de milles que moi, pis il tourne encore.", 3, jeu="[warmly] Un Johnson de cinquante-huit. [calm] Il a plus de milles que moi, pis il tourne encore.", cloture=True),
            _p("berube", "Merci. La chaloupe est à ta disposition, quand tu voudras voir l'île.", 3, jeu="[warmly] Merci. [matter-of-fact] La chaloupe est à ta disposition, quand tu voudras voir l'île.", cloture=True),
            # ⚠️ Coupée (2 oct. 2026) : « Bérubé. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("berube", "Le moteur tourne comme au premier jour. J'ai une commission pour l'île.", 3, jeu="[calm] Le moteur tourne comme au premier jour. J'ai une commission pour l'île."),
            _p("berube", "Une caisse d'outils pour Léo, au hangar. Je la lui promets depuis l'été.", 3, jeu="[matter-of-fact] Une caisse d'outils pour Léo, au hangar. [calm] Je la lui promets depuis l'été."),
            _p("berube", "L'île, c'est là-bas, derrière la brume. Trente tuiles d'eau, pis pas une police.", 3, jeu="[calm] L'île, c'est là-bas, derrière la brume. [knowingly] Trente tuiles d'eau, pis pas une police."),
            _p("berube", "Léo parle peu. Réponds-lui pareil, vous allez bien vous entendre.", 3, jeu="[wryly] Léo parle peu. [calm] Réponds-lui pareil, vous allez bien vous entendre."),
            _p("berube", "Elle est amarrée sous le Faubourg. Tire la corde deux fois, elle est capricieuse.", 4, jeu="[matter-of-fact] Elle est amarrée sous le Faubourg. [wryly] Tire la corde deux fois, elle est capricieuse."),
            _p("berube", "Garde le phare à ta gauche. Le hangar, c'est le grand toit de tôle.", 5, jeu="[calm] Garde le phare à ta gauche. [matter-of-fact] Le hangar, c'est le grand toit de tôle."),
            _p("berube", "Accoste doucement, pis marche jusqu'à lui. Il t'attend sans t'attendre.", 6, jeu="[calm] Accoste doucement, pis marche jusqu'à lui. [knowingly] Il t'attend sans t'attendre."),
        ],
        "accueil": [
            _a("leo", "Léo, du hangar. La caisse du capitaine? Pose-la là, j'ai rien vu pis rien reçu.", 6, jeu="[deadpan] Léo, du hangar. La caisse du capitaine? [mysteriously] Pose-la là, j'ai rien vu pis rien reçu."),
        ],
    },
}
