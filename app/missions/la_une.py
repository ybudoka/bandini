"""Le chapitre de la une — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague L). Le Clairon
(l'arc C de M16, écrit `l` pour Louise) commence par deux missions de trois étapes : l01 (la série de photos, 213 s
au chronomètre de Martin) et l02 (la une sur toi). Deux ACTES d'une même journée de Louise : la photo de Bouchard,
puis Louise qui fait du neveu sa une. Rien d'ajouté : deux polices à semer, dont trois étoiles sous le chrono, tiennent
la visée (5 à 6 minutes).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de l01
  restent ceux du chapitre ; sa fin se dit à l'ouverture de l'acte 2, en personne (Louise est dans le char), suivie
  de l'appel et de l'intro de l02 ; la fin de l02 reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : l'appel de l02 perd « C'est Louise. » et « Viens au kiosque. » (elle est
  à côté de toi) — la même voix, coupée au silence ;
- la scène d'intro de l01 reste celle du chapitre.
- _Le scoop du maire_ attend l01 (le premier acte) : un prérequis peut viser un acte.
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "la_une",
    "titre": "La une",
    "donneur": "louise",
    "prerequis": ["m6"],
    "remplace": ["l01", "l02"],
    "recompense": 200,
    "donne": {"manchette": "insaisissable", "message": "DEMAIN, TU FAIS LA UNE DU CLAIRON"},

    "objectifs": [
        # --- Acte 1 (l01, « Une photo pour la une »).
        # Une photo pour la une (M16, arc C « Le Clairon », 30 sept. 2026). Louise n'a plus de photographe ni de char : le
        # Clairon ne paie ni l'un ni l'autre. Elle veut une série — « Baie-des-Brumes, une journée » — et commence par la
        # plus risquée : le sergent Bouchard devant son poste. Il n'aime pas les photos ; ses agents non plus. On la mène au
        # poste, on sème ceux qui la reconnaissent, et on finit au port, où la lumière du soir tombe sur la cantine.
        # ⚠️ L'arc C de la fiche s'écrit `l01`–`l06` : les slugs `c01`–`c08` sont pris (Irène, le vieux maître).
        {"type": "acte", "texte": "ACTE 1 — UNE PHOTO POUR LA UNE", "donneur": "louise"},  # 0
        {"type": "proteger", "texte": "MÈNE LOUISE AU POSTE : ELLE VEUT BOUCHARD EN PHOTO", "cible": "louise", "lieu": "poste", "rayon": 5},  # 1
        {"type": "semer", "texte": "LES AGENTS N'AIMENT PAS LES PHOTOS : SÈME-LES", "etoiles": 1},  # 2
        {"type": "aller", "texte": "LA LUMIÈRE DU SOIR AU PORT : LA CANTINE", "lieu": "cantine", "rayon": 6, "donne": {"message": "LA UNE DE DEMAIN EST DANS L'APPAREIL DE LOUISE", "prime": 150}},  # 3
        # --- Acte 2 (l02, « La manchette sur toi »).
        # La manchette sur toi (M16, arc C, 30 sept. 2026 — la « c04 » de la fiche). Louise a trouvé sa une : le neveu de
        # Rocco lui-même. Elle attend devant le poste, l'appareil prêt ; il suffit de faire parler de soi — trois étoiles —
        # puis de les semer en moins d'une minute et demie. Si on y arrive, le Clairon titre _Bandini l'insaisissable_ ; si
        # on se fait prendre, elle a quand même sa photo, et c'est une autre une.
        {"type": "acte", "texte": "ACTE 2 — LA MANCHETTE SUR TOI", "donneur": "louise"},  # 4
        {"type": "aller", "texte": "LOUISE T'ATTEND DEVANT LE POSTE, L'APPAREIL PRÊT", "lieu": "poste", "rayon": 5},  # 5
        {"type": "semer", "texte": "TROIS ÉTOILES : SÈME-LES EN 90 SECONDES", "etoiles": 3, "chrono_s": 90},  # 6
        {"type": "retourner", "texte": "RETOURNE VOIR LOUISE AU KIOSQUE"},  # 7
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:poste", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # l01 — Le jeu de chaque réplique (`jeu=`) — Louise : vive, pince-sans-rire, en phrases de manchette ; « mon beau »
    # quand elle taquine. Elle a peur de Bouchard et le dit en riant.
    # l02 — Le jeu de chaque réplique (`jeu=`) — Louise : le plaisir de la une qui s'écrit toute seule ; elle taquine, et
    # elle prend des notes en parlant.
    "dialogue": {
        "appel": [
            _l("louise", "Louise, du Clairon. J'ai une série à faire pis pas de chauffeur. T'es libre, mon beau?", jeu="[confident] Louise, du Clairon. J'ai une série à faire pis pas de chauffeur. [teasing] T'es libre, mon beau?"),
        ],
        "intro": [
            _l("louise", "« Baie-des-Brumes, une journée. » Six photos, six coins de ville. On commence par le pire.", jeu="[excited] « Baie-des-Brumes, une journée. » Six photos, six coins de ville. [wryly] On commence par le pire."),
            _l("louise", "Le sergent Bouchard devant son poste, la bedaine au soleil. Il va détester ça.", jeu="[amused] Le sergent Bouchard devant son poste, la bedaine au soleil. [mischievously] Il va détester ça."),
            _l("louise", "Tu conduis, je shoote. Pis si ça tourne mal, tu conduis plus vite.", jeu="[confident] Tu conduis, je shoote. [wryly] Pis si ça tourne mal, tu conduis plus vite."),
        ],
        "fin": [
            _l("louise", "« Bandini l'insaisissable. » Trois étoiles, pis pouf. Le monde va adorer.", jeu="[excited] « Bandini l'insaisissable. » Trois étoiles, pis pouf. [amused] Le monde va adorer."),
            _l("louise", "Pis Bouchard va la découper pour son babillard. Tiens, ta part des ventes.", jeu="[wryly] Pis Bouchard va la découper pour son babillard. [warmly] Tiens, ta part des ventes."),
        ],
        "echec": [
            _e("louise", "Pas de photo, pas de une. Demain, le Clairon imprime la météo en gros.", 0, jeu="[disappointed] Pas de photo, pas de une. [sarcastic] Demain, le Clairon imprime la météo en gros."),
            _e("louise", "Pogné en moins de deux. Ma une va s'appeler « Le neveu au poste ».", 4, jeu="[disappointed] Pogné en moins de deux. [sarcastic] Ma une va s'appeler « Le neveu au poste »."),
        ],
        "pendant": [
            _p("louise", "Arrête-toi pas trop près. Une photo volée, c'est de loin.", 1, jeu="[quietly] Arrête-toi pas trop près. [knowingly] Une photo volée, c'est de loin."),
            _p("louise", "Il m'a vue! Pis il a pas aimé son profil. Décolle!", 2, jeu="[excited] Il m'a vue! [amused] Pis il a pas aimé son profil. [shouting] Décolle!"),
            _p("louise", "Au port, astheure. La lumière du soir sur la cantine, c'est ma dernière de la journée.", 3, jeu="[calm] Au port, astheure. [warmly] La lumière du soir sur la cantine, c'est ma dernière de la journée."),
            # Acte 2 : la fin de l01, en personne ; puis l'appel et l'intro de l02.
            _p("louise", "Regarde-moi ça. Bouchard en furie, pis le port qui dort. C'est la une.", 4, jeu="[excited] Regarde-moi ça. Bouchard en furie, pis le port qui dort. [satisfied] C'est la une.", cloture=True),
            _p("louise", "Tiens, pour l'essence. Le Clairon paie mal, mais il paie comptant.", 4, jeu="[wryly] Tiens, pour l'essence. [confident] Le Clairon paie mal, mais il paie comptant.", cloture=True),
            # ⚠️ Coupée (2 oct. 2026) : « C'est Louise. » et « Viens au kiosque. » — elle s'est nommée, et elle est là.
            _p("louise", "J'ai trouvé ma une de demain, pis c'est toi.", 4, jeu="[teasing] J'ai trouvé ma une de demain, pis c'est toi."),
            _p("louise", "Tout le monde parle du neveu de Rocco. Personne l'a jamais vu. Je veux la photo.", 4, jeu="[confident] Tout le monde parle du neveu de Rocco. Personne l'a jamais vu. [excited] Je veux la photo."),
            _p("louise", "Passe devant le poste. Fais-toi voir. Trois étoiles, pis je déclenche.", 4, jeu="[mischievously] Passe devant le poste. Fais-toi voir. [excited] Trois étoiles, pis je déclenche."),
            _p("louise", "Après, t'as une minute et demie pour disparaître. Sinon, la une, c'est ton procès.", 4, jeu="[wryly] Après, t'as une minute et demie pour disparaître. [teasing] Sinon, la une, c'est ton procès."),
            _p("louise", "Je suis de l'autre côté de la rue. Souris, mon beau.", 5, jeu="[teasing] Je suis de l'autre côté de la rue. [amused] Souris, mon beau."),
            _p("louise", "Clic! Je l'ai! Astheure, disparais, je chronomètre.", 6, jeu="[excited] Clic! Je l'ai! [firmly] Astheure, disparais, je chronomètre."),
            _p("louise", "Plus une sirène. Reviens au kiosque, j'ai mon titre.", 7, jeu="[impressed] Plus une sirène. [confident] Reviens au kiosque, j'ai mon titre."),
        ],
    },
}
