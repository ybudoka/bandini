"""Le chapitre de Diane et Jo — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague E). Après la paix des Érables, Diane a deux services : e13 (sa berline reprise au lot) et e08 (la cachette de Jo, deux
paquets, un char de Skateux collé derrière) — trois et quatre étapes, deux ACTES (5 à 6 minutes).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : l'appel de e08 perd « Diane Larivière. » — la même voix, coupée ;
- la scène d'intro de e13 reste celle du chapitre.
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "diane_et_jo",
    "titre": "Diane et Jo",
    "donneur": "diane",
    "prerequis": ["e10"],
    "remplace": ["e13", "e08"],
    "recompense": 250,
    "donne": {"message": "LES PAQUETS DE JO ONT DISPARU"},

    "objectifs": [
        # --- Acte 1 (e13, « Le char de Diane »).
        # Le char de Diane (M16, arc E, 30 sept. 2026). Les Érables sont libres (e10), et la conseillère se prépare à la
        # mairie ; mais sa berline dort au lot de la fourrière — un stationnement « interdit aux citoyens » devant l'hôtel de
        # ville, posé par les hommes du maire. Elle ne paiera pas une amende de Tanguay. On la reprend au lot sans payer, on
        # sème la police que Gilles appelle « par principe », et on la gare devant le dépanneur, sans une bosse.
        {"type": "acte", "texte": "ACTE 1 — LE CHAR DE DIANE", "donneur": "diane"},  # 0
        {"type": "monter", "texte": "SA BERLINE DORT AU LOT : REPRENDS-LA SANS PAYER", "vehicule": "luxe", "ou": "porte:fourriere"},  # 1
        {"type": "semer", "texte": "GILLES APPELLE LA POLICE, PAR PRINCIPE : SÈME-LA", "etoiles": 1},  # 2
        {"type": "livrer", "texte": "LA BERLINE DEVANT LE DÉPANNEUR, SANS UNE BOSSE", "lieu": "depanneur", "rayon": 6, "donne": {"message": "LA BERLINE DE DIANE EST DEVANT LE DÉPANNEUR — SANS AMENDE", "prime": 300}},  # 3
        # --- Acte 2 (e08, « La cachette de Jo »).
        # La cachette de Jo (M16, arc E, 1er oct. 2026). Jo est parti (e04) ; c'était lui, le chef des Chevreuils (e10). Sa mère
        # a trouvé, dans sa chambre, un plan dessiné au crayon : deux paquets cachés à La Pointe, au stationnement des Skateux.
        # Elle ne veut pas savoir ce qu'il y a dedans — elle veut qu'ils disparaissent avant que les Skateux, ou un
        # journaliste, les trouvent. Le coupé de Diane (`monter`), le premier paquet au pied de la rampe des Skateux sous le
        # chrono (`obtenir`, à pied — un `ou` en `rampe:`), le second sous le phare, puis Diane (`retourner`) — un char des Skateux te colle
        # (`poursuite`).
        # ⚠️ Écarts à la fiche (« Jo a un problème ») : Jo est parti après e04 — c'est sa mère qui donne la job ; et le chrono
        # (200 s) court jusqu'au premier paquet, le plus loin.
        {"type": "acte", "texte": "ACTE 2 — LA CACHETTE DE JO", "donneur": "diane"},  # 4
        {"type": "monter", "texte": "LE COUPÉ DE DIANE, DEVANT LE DÉPANNEUR", "vehicule": "sport", "ou": "porte:depanneur", "prete": "diane"},  # 5
        {"type": "obtenir", "texte": "LE PREMIER PAQUET, AU PIED DE LA RAMPE DES SKATEUX", "objet": "paquet_de_jo", "ou": "rampe:pointe", "dessin": "sac", "nom": "UN PAQUET DE JO", "chrono_s": 200},  # 6
        {"type": "obtenir", "texte": "LE DEUXIÈME, SOUS LE PHARE", "objet": "autre_paquet_de_jo", "ou": "phare", "dessin": "sac", "nom": "L'AUTRE PAQUET DE JO"},  # 7
        {"type": "retourner", "texte": "RAPPORTE LES DEUX PAQUETS À DIANE", "poursuite": {"groupe": "skateux", "chars": 1}},  # 8
    ],

    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:fourriere", "ferme": 20, "ouvre": 20, "tient": 160, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # e13 — Le jeu de chaque réplique (`jeu=`) — Diane : la politicienne qui vouvoie, un sourire dans la voix ; elle parle
    # des « citoyens » pour ne pas parler d'elle.
    # e08 — Le jeu de chaque réplique (`jeu=`) — Diane : elle vouvoie, pèse ses mots ; ici la mère passe sous la
    # conseillère (`[somber]` pour Jo), et elle se reprend chaque fois.
    "dialogue": {
        "appel": [
            _l("diane", "Diane Larivière. Le maire m'a fait remorquer. Venez me voir au dépanneur, j'ai un service.", jeu="[confident] Diane Larivière. [wryly] Le maire m'a fait remorquer. [calm] Venez me voir au dépanneur, j'ai un service."),
        ],
        "intro": [
            _l("diane", "Un stationnement « interdit aux citoyens » devant l'hôtel de ville. Posé hier, par ses hommes.", jeu="[wryly] Un stationnement « interdit aux citoyens » devant l'hôtel de ville. [knowingly] Posé hier, par ses hommes."),
            _l("diane", "Ma berline est au lot. Je ne paierai pas une amende signée Tanguay, par principe.", jeu="[calm] Ma berline est au lot. [confident] Je ne paierai pas une amende signée Tanguay, par principe."),
            _l("diane", "Ramenez-la ici, sans une bosse. Les citoyens me regardent conduire, maintenant.", jeu="[firmly] Ramenez-la ici, sans une bosse. [wryly] Les citoyens me regardent conduire, maintenant."),
        ],
        "fin": [
            _l("diane", "Je les brûlerai moi-même. Merci. Jo ne saura jamais que c'était vous.", jeu="[somber] Je les brûlerai moi-même. [softly] Merci. [calm] Jo ne saura jamais que c'était vous."),
            _l("diane", "Ni que c'était moi. Ça, c'est ma façon d'être une mère.", jeu="[quietly] Ni que c'était moi. [somber] Ça, c'est ma façon d'être une mère."),
        ],
        "echec": [
            _e("diane", "Ma berline est encore au lot. Je vais devoir payer l'amende. Quelle humiliation.", 0, jeu="[disappointed] Ma berline est encore au lot. Je vais devoir payer l'amende. [coldly] Quelle humiliation."),
            _e("diane", "Les Skateux les ont trouvés. Demain, ce sera dans le Clairon. Tant pis pour nous deux.", 4, jeu="[coldly] Les Skateux les ont trouvés. [somber] Demain, ce sera dans le Clairon. Tant pis pour nous deux."),
        ],
        "pendant": [
            _p("diane", "Gilles est un homme honnête. Ne lui faites pas de peine, prenez-la, c'est tout.", 1, jeu="[calm] Gilles est un homme honnête. [knowingly] Ne lui faites pas de peine, prenez-la, c'est tout."),
            _p("diane", "Il a appelé la police, évidemment. Par principe, lui aussi.", 2, jeu="[wryly] Il a appelé la police, évidemment. [calm] Par principe, lui aussi."),
            _p("diane", "Devant le dépanneur, en face des pompes. C'est là qu'on me voit le mieux.", 3, jeu="[confident] Devant le dépanneur, en face des pompes. [wryly] C'est là qu'on me voit le mieux."),
            # Acte 2 : la fin de e13, en personne ; puis l'appel et l'intro de e08.
            _p("diane", "Pas une bosse. Vous conduisez mieux que mon chauffeur, et vous parlez moins.", 4, jeu="[satisfied] Pas une bosse. [wryly] Vous conduisez mieux que mon chauffeur, et vous parlez moins."),
            _p("diane", "Pour votre peine. Et quand je serai mairesse, le lot aura un nouveau règlement.", 4, jeu="[calm] Pour votre peine. [confident] Et quand je serai mairesse, le lot aura un nouveau règlement."),
            # ⚠️ Coupée (2 oct. 2026) : « Diane Larivière. » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("diane", "J'ai besoin de vous, et de votre discrétion. C'est au sujet de Jo.", 4, jeu="[quietly] J'ai besoin de vous, et de votre discrétion. [somber] C'est au sujet de Jo."),
            _p("diane", "J'ai trouvé un plan dans sa chambre. Deux paquets, cachés au stationnement des Skateux.", 4, jeu="[somber] J'ai trouvé un plan dans sa chambre. [quietly] Deux paquets, cachés au stationnement des Skateux."),
            _p("diane", "Je ne veux pas savoir ce qu'il y a dedans. Je veux qu'ils disparaissent avant qu'on les trouve.", 4, jeu="[firmly] Je ne veux pas savoir ce qu'il y a dedans. [calm] Je veux qu'ils disparaissent avant qu'on les trouve."),
            _p("diane", "Prenez mon coupé. Et si un journaliste vous pose une question, vous ne m'avez jamais vue.", 4, jeu="[confident] Prenez mon coupé. [wryly] Et si un journaliste vous pose une question… vous ne m'avez jamais vue."),
            _p("diane", "Mon coupé est devant le dépanneur. Il va vite, ne me le ramenez pas en morceaux.", 5, jeu="[matter-of-fact] Mon coupé est devant le dépanneur. [wryly] Il va vite, ne me le ramenez pas en morceaux."),
            _p("diane", "Les Skateux font leur ronde au coucher du soleil. Vous avez trois minutes, pas plus.", 6, jeu="[serious] Les Skateux font leur ronde au coucher du soleil. [firmly] Vous avez trois minutes, pas plus."),
            _p("diane", "Sur le plan, il y a une croix sous le phare. Il dessinait comme ça à six ans.", 7, jeu="[matter-of-fact] Sur le plan, il y a une croix sous le phare. [somber] Il dessinait comme ça à six ans."),
            _p("diane", "Un char vous suit? Ne venez pas au dépanneur avec lui. Semez-le d'abord.", 8, jeu="[nervously] Un char vous suit? [firmly] Ne venez pas au dépanneur avec lui. Semez-le d'abord."),
        ],
    },
}
