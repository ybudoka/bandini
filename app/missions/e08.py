"""La mission e08 — voir app/missions/__init__.py pour le moteur.

La cachette de Jo (M16, arc E, 1er oct. 2026). Jo est parti (e04) ; c'était lui, le chef des Chevreuils (e10). Sa mère
a trouvé, dans sa chambre, un plan dessiné au crayon : deux paquets cachés à La Pointe, au stationnement des Skateux.
Elle ne veut pas savoir ce qu'il y a dedans — elle veut qu'ils disparaissent avant que les Skateux, ou un
journaliste, les trouvent. Le coupé de Diane (`monter`), le premier paquet au pied de la rampe des Skateux sous le
chrono (`obtenir`, à pied — un `ou` en `rampe:`), le second sous le phare, puis Diane (`retourner`) — un char des Skateux te colle
(`poursuite`).

⚠️ Écarts à la fiche (« Jo a un problème ») : Jo est parti après e04 — c'est sa mère qui donne la job ; et le chrono
(200 s) court jusqu'au premier paquet, le plus loin.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "e08",
    "titre": "La cachette de Jo",
    "donneur": "diane",
    "prerequis": ["e10"],
    "recompense": 250,
    "donne": {"message": "LES PAQUETS DE JO ONT DISPARU"},

    "objectifs": [
        {"type": "monter", "texte": "LE COUPÉ DE DIANE, DEVANT LE DÉPANNEUR", "vehicule": "sport",
         "ou": "porte:depanneur", "prete": "diane"},

        {"type": "obtenir", "texte": "LE PREMIER PAQUET, AU PIED DE LA RAMPE DES SKATEUX",
         "objet": "paquet_de_jo", "ou": "rampe:pointe", "dessin": "sac", "nom": "UN PAQUET DE JO", "chrono_s": 200},

        {"type": "obtenir", "texte": "LE DEUXIÈME, SOUS LE PHARE",
         "objet": "autre_paquet_de_jo", "ou": "phare", "dessin": "sac", "nom": "L'AUTRE PAQUET DE JO"},

        {"type": "retourner", "texte": "RAPPORTE LES DEUX PAQUETS À DIANE",
         "poursuite": {"groupe": "skateux", "chars": 1}},
    ],

    # Intention (intro) : la politicienne qui ne baisse jamais la voix, et qui la baisse — une mère qui a trouvé quelque
    # chose dans la chambre de son fils. La caméra va voir La Pointe, au bout de la ville ; elle revient pour la règle.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "rampe:pointe", "ferme": 20, "ouvre": 20, "tient": 150, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Diane : elle vouvoie, pèse ses mots ; ici la mère passe sous la
    # conseillère (`[somber]` pour Jo), et elle se reprend chaque fois.
    "dialogue": {
        "appel": [
            _l("diane", "Diane Larivière. J'ai besoin de vous, et de votre discrétion. C'est au sujet de Jo.",
               jeu="[calm] Diane Larivière. [quietly] J'ai besoin de vous, et de votre discrétion. [somber] C'est au sujet de Jo.")
        ],
        "intro": [
            _l("diane", "J'ai trouvé un plan dans sa chambre. Deux paquets, cachés au stationnement des Skateux.",
               jeu="[somber] J'ai trouvé un plan dans sa chambre. [quietly] Deux paquets, cachés au stationnement des Skateux."),
            _l("diane", "Je ne veux pas savoir ce qu'il y a dedans. Je veux qu'ils disparaissent avant qu'on les trouve.",
               jeu="[firmly] Je ne veux pas savoir ce qu'il y a dedans. [calm] Je veux qu'ils disparaissent avant qu'on les trouve."),
            _l("diane", "Prenez mon coupé. Et si un journaliste vous pose une question, vous ne m'avez jamais vue.",
               jeu="[confident] Prenez mon coupé. [wryly] Et si un journaliste vous pose une question… vous ne m'avez jamais vue.")
        ],
        "pendant": [
            _p("diane", "Mon coupé est devant le dépanneur. Il va vite, ne me le ramenez pas en morceaux.", 0,
               jeu="[matter-of-fact] Mon coupé est devant le dépanneur. [wryly] Il va vite, ne me le ramenez pas en morceaux."),
            _p("diane", "Les Skateux font leur ronde au coucher du soleil. Vous avez trois minutes, pas plus.", 1,
               jeu="[serious] Les Skateux font leur ronde au coucher du soleil. [firmly] Vous avez trois minutes, pas plus."),
            _p("diane", "Sur le plan, il y a une croix sous le phare. Il dessinait comme ça à six ans.", 2,
               jeu="[matter-of-fact] Sur le plan, il y a une croix sous le phare. [somber] Il dessinait comme ça à six ans."),
            _p("diane", "Un char vous suit? Ne venez pas au dépanneur avec lui. Semez-le d'abord.", 3,
               jeu="[nervously] Un char vous suit? [firmly] Ne venez pas au dépanneur avec lui. Semez-le d'abord.")
        ],
        "fin": [
            _l("diane", "Je les brûlerai moi-même. Merci. Jo ne saura jamais que c'était vous.",
               jeu="[somber] Je les brûlerai moi-même. [softly] Merci. [calm] Jo ne saura jamais que c'était vous."),
            _l("diane", "Ni que c'était moi. Ça, c'est ma façon d'être une mère.",
               jeu="[quietly] Ni que c'était moi. [somber] Ça, c'est ma façon d'être une mère.")
        ],
        "echec": [
            _l("diane", "Les Skateux les ont trouvés. Demain, ce sera dans le Clairon. Tant pis pour nous deux.",
               jeu="[coldly] Les Skateux les ont trouvés. [somber] Demain, ce sera dans le Clairon. Tant pis pour nous deux.")
        ]
    }
}
