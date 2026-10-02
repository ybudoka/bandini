"""Le chapitre du Grand Mo et du kiosque — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague F). Martin a tranché
pour les arcs hors de la liste de M16 : le Grand Mo qui sait tout (f04 : le couteau, sa cache, les trois paquets de
Rocco) et la caisse de Madame Thibodeau, vidée pendant le grabuge (f07 : le pickpocket de la cantine et son complice)
deviennent deux ACTES — f07 n'attendait que f04. Visée : 7 à 9 minutes, rien d'ajouté. Le défi de l'esquive du Grand
Mo s'ouvre quand f04 est faite, à l'ouverture de l'acte 2 (`debloque`).

Ce qui a bougé, et pourquoi (comme aux autres chapitres) :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la
  première mission restent ceux du chapitre ; la fin de la première se dit à l'ouverture de l'acte 2, suivie de
  l'appel et de l'intro de la seconde ; la fin de la seconde reste la fin du chapitre ; chacune garde son échec
  (`_e`, accroché à son acte) ;
- l'acte 1 paie sa prime et accorde ce que sa mission accordait en finissant (`donne` sur l'objectif qui le
  finit), et la mission qu'il remplace est faite à l'ouverture de l'acte 2 — ce qui l'attendait s'ouvre là ;
- la scène d'intro de la première reste celle du chapitre, la scène de fin de la seconde celle de sa fin ; les
  deux autres tombent (leurs répliques se disent au marqueur), comme au pilote.
- deux donneurs, un appel chacun : Madame Thibodeau se nomme à son appel, le Grand Mo au sien ; personne ne se
  nomme deux fois.
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "grand_mo_et_le_kiosque",
    "titre": "Le Grand Mo et le kiosque",
    "donneur": "mo",
    "prerequis": ["m6"],
    "remplace": ["f04", "f07"],
    "recompense": 200,
    "donne": {"message": "LA CLÉ DU KIOSQUE, RETROUVÉE"},

    "objectifs": [
        # --- Acte 1 (f04, « Le Grand Mo sait tout »).
        {"type": "acte", "texte": "ACTE 1 — LE GRAND MO SAIT TOUT", "donneur": "mo"},  # 0
        {"type": "acheter", "texte": "ACHÈTE-LUI UN COUTEAU À LA QUINCAILLERIE", "article": "couteau", "ou": "boutique:artisan"},  # 1
        {"type": "tuer", "texte": "CHASSE LES DEUX CRAVATES DE SA CACHE", "groupe": "cravates", "n": 2, "ou": "donneur", "loin": 12},  # 2
        {"type": "aller", "texte": "LE PREMIER PAQUET : DERRIÈRE L'HÔTEL BANDINI", "lieu": "hotel", "rayon": 6},  # 3
        {"type": "aller", "texte": "LE DEUXIÈME : AU PIED DU PHARE DE LA POINTE", "lieu": "phare", "rayon": 6},  # 4
        {"type": "ramasser", "texte": "LE TROISIÈME FILE EN MOTO : RATTRAPE-LE", "hiver": "LE TROISIÈME FILE EN MOTONEIGE : RATTRAPE-LE", "cible": "fuyard", "vehicule": "moto"},  # 5
        {"type": "retourner", "texte": "RETOURNE VOIR LE GRAND MO", "donne": {"message": "TROIS PAQUETS DE ROCCO, RETROUVÉS", "prime": 150}},  # 6
        # --- Acte 2 (f07, « La caisse, encore »).
        {"type": "acte", "texte": "ACTE 2 — LA CAISSE, ENCORE", "donneur": "thibodeau"},  # 7
        {"type": "aller", "texte": "VA À LA CANTINE DES QUAIS : IL BOIT MON ARGENT", "lieu": "cantine", "rayon": 6},  # 8
        {"type": "pickpocket", "texte": "VIDE SES POCHES, PAR-DERRIÈRE", "cible": "pickpocket"},  # 9
        {"type": "ramasser", "texte": "SON COMPLICE FILE AVEC LA CAISSE : RATTRAPE-LE", "cible": "fuyard", "vehicule": "moto"},  # 10
        {"type": "retourner", "texte": "RETOURNE VOIR MADAME THIBODEAU"},  # 11
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "hausser", "duree": 70, "ensemble": True},
            {"type": "dire"},
        ],
    },

    # f04 — Le jeu de chaque réplique (`jeu=`) — Le Grand Mo : lent, qui traîne ses phrases et
    # fait durer le mystère, puis chaleureux une fois servi — le contraire de sa lenteur
    # habituelle, comme un homme qui a enfin quelqu'un à qui parler.
    # f07 — Le jeu de chaque réplique (`jeu=`) — Mme Thibodeau : en colère qu'on la vole encore,
    # puis soulagée sèchement — elle ne s'attendrit jamais longtemps, même contente.
    "dialogue": {
        "appel": [
            _l("mo", "Le Grand Mo, on m'appelle de même. Viens t'asseoir un peu, j'ai de quoi te dire.", jeu="[knowingly] Le Grand Mo, on m'appelle de même. [amused] Viens t'asseoir un peu… j'ai de quoi te dire."),
        ],
        "intro": [
            _l("mo", "J'ai tout vu passer icitte, pis j'oublie rien.", jeu="[somber] J'ai tout vu passer icitte… pis j'oublie rien."),
            _l("mo", "Mon vieux couteau a rendu l'âme. Amène-m'en un de la quincaillerie, pis je te dis ce que je sais.", jeu="[amused] Mon vieux couteau a rendu l'âme. [knowingly] Amène-m'en un de la quincaillerie… pis je te dis ce que je sais."),
        ],
        "fin": [
            _l("thibodeau", "Ma clé! T'es un bon garçon, toi, encore une fois.", jeu="[relieved] Ma clé! [warmly] T'es un bon garçon, toi… encore une fois."),
            _l("thibodeau", "Prends ça pour ta peine, pis dis-moi pas que c'est trop.", jeu="[tenderly] Prends ça pour ta peine… [firmly] pis dis-moi pas que c'est trop."),
            _l("thibodeau", "Deux fois volée, deux fois rapportée. Je devrais t'engager, toi.", jeu="[amused] Deux fois volée, deux fois rapportée. [warmly] Je devrais t'engager, toi."),
        ],
        "echec": [
            _e("mo", "Ben... reviens quand t'auras le temps. Les paquets partiront pas tout seuls, remarque.", 0, jeu="[wryly] Ben… reviens quand t'auras le temps. [amused] Les paquets partiront pas tout seuls, remarque."),
            _e("thibodeau", "Encore ratée... Ma pauvre caisse va rester fermée un bon bout.", 7, jeu="[disappointed] Encore ratée… [sighs] Ma pauvre caisse va rester fermée un bon bout."),
        ],
        "pendant": [
            _p("mo", "Deux gars en cravate traînent encore près d'où Rocco cachait ses affaires. Va falloir les convaincre.", 2, jeu="[wryly] Deux gars en cravate traînent encore… près d'où Rocco cachait ses affaires. [firmly] Va falloir les convaincre."),
            _p("mo", "Rocco cachait ses affaires à trois places. La première, derrière l'hôtel qui porte son nom.", 3, jeu="[knowingly] Rocco cachait ses affaires à trois places. [amused] La première… derrière l'hôtel qui porte son nom."),
            _p("mo", "La deuxième, au pied du phare. Il aimait ça, les places où on voit venir le monde.", 4, jeu="[somber] La deuxième, au pied du phare. [knowingly] Il aimait ça, les places où on voit venir le monde."),
            _p("mo", "Le troisième s'en va en moto? Ah ben. Y a d'autre monde qui a de la mémoire, faut croire.", 5, jeu="[surprised] Le troisième s'en va en moto? [amused] Ah ben. Y a d'autre monde qui a de la mémoire, faut croire.", hiver=("Le troisième s'en va en motoneige? Ah ben. Y a d'autre monde qui a de la mémoire, faut croire.", "[surprised] Le troisième s'en va en motoneige? [amused] Ah ben. Y a d'autre monde qui a de la mémoire, faut croire.")),
            _p("mo", "Rapporte-moi ça au banc. Prends ton temps, moi, j'ai rien que ça.", 6, jeu="[warmly] Rapporte-moi ça au banc. [amused] Prends ton temps… moi, j'ai rien que ça."),
            # Acte 2 : la fin de f04, en personne ; puis l'appel et l'intro de f07.
            _p("mo", "Trois paquets, retrouvés. Rocco aurait aimé ça, te voir faire le ménage.", 7, jeu="[warmly] Trois paquets, retrouvés. [somber] Rocco aurait aimé ça… te voir faire le ménage."),
            _p("mo", "Reviens t'asseoir, un de ces jours. J'ai d'autres histoires.", 7, jeu="[amused] Reviens t'asseoir, un de ces jours. [warmly] J'ai d'autres histoires."),
            _p("thibodeau", "C'est Madame Thibodeau, du kiosque. Un petit voleur a profité du grabuge pour vider ma caisse, encore!", 7, jeu="[angry] C'est Madame Thibodeau, du kiosque. [bitterly] Un petit voleur a profité du grabuge pour vider ma caisse… encore!"),
            _p("thibodeau", "Il a ma clé dans sa poche. Sans elle, mon tiroir-caisse reste fermé jusqu'au printemps.", 7, jeu="[bitterly] Il a ma clé dans sa poche. [worried] Sans elle, mon tiroir-caisse reste fermé… jusqu'au printemps."),
            _p("thibodeau", "Approche-toi par-derrière. Fouille-le. Pis reviens vite, mon p'tit.", 7, jeu="[firmly] Approche-toi par-derrière. Fouille-le. [warmly] Pis reviens vite, mon p'tit."),
            _p("thibodeau", "Il boit mon argent à la cantine des Quais. À ma santé, j'imagine.", 8, jeu="[bitterly] Il boit mon argent à la cantine des Quais. [wryly] À ma santé, j'imagine."),
            _p("thibodeau", "Il se sauvera au premier bruit. Approche-toi comme un chat.", 9, jeu="[worried] Il se sauvera au premier bruit. [quietly] Approche-toi comme un chat."),
            _p("thibodeau", "Ma clé, mais pas ma caisse? Son complice file avec! Rattrape-le, mon p'tit!", 10, jeu="[angry] Ma clé, mais pas ma caisse? Son complice file avec! [firmly] Rattrape-le, mon p'tit!"),
            _p("thibodeau", "Rapporte-la-moi, veux-tu? Pis secoue-la pas trop, elle est plus toute jeune.", 11, jeu="[relieved] Rapporte-la-moi, veux-tu? [amused] Pis secoue-la pas trop… elle est plus toute jeune."),
        ],
    },
}
