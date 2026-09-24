"""La mission p13 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "p13",
    "titre": "La caisse de l'arche",
    "donneur": "bonimenteur",
    "prerequis": ["m6"],
    "recompense": 200,
    "donne": {"message": "LA FOIRE RESPIRE"},

    # ⚠️ **La foire devient un vrai lieu de mission** (22 sept. 2026) : le
    # Bonimenteur est posé `ou: "foire"` (`histoire.js::poserDonneurFoire`,
    # `lieuFoire`), vivant à l'arche — contrairement à un donneur `point:`, il est
    # hélable, le GPS le trouve, et `retourner` marche vraiment. `pickpocket`
    # réutilise le patron de f07 : l'archétype dédié, jamais un archétype de gang.
    # ⚠️ Plus longue (Martin, 22 sept. 2026, « des missions plus longues ») : le voleur
    # n'avait que la moitié de la recette — son complice file en moto avec le reste
    # (`ramasser` + `fuyard`, le patron de m2/m50 : on le rattrape, une Cravate en descend
    # avec la caisse, on la couche, on ramasse) ; ses chums des Cravates arrivent (`tuer`,
    # `loin`) ; et on rapporte le tout à l'arche, d'où que la moto nous ait menés.
    "objectifs": [
        {"type": "pickpocket", "texte": "REPRENDS LA CAISSE, PAR-DERRIÈRE", "cible": "pickpocket"},

        {"type": "ramasser", "texte": "LE COMPLICE FILE AVEC LE RESTE — RATTRAPE-LE",
         "cible": "fuyard", "vehicule": "moto"},

        {"type": "tuer", "texte": "SES CHUMS DES CRAVATES — COUCHE-LES",
         "groupe": "cravates", "n": 2, "ou": "donneur", "loin": 10},

        {"type": "retourner", "texte": "RAPPORTE-LA AU BONIMENTEUR"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — le Bonimenteur : jovial en public, la voix
    # qui vend les trois jeux d'adresse ; ici, il perd un peu de sa faconde, inquiet
    # pour sa recette.
    "dialogue": {
        "appel": [
            _l("bonimenteur", "Hé, le jeune! C'est le Bonimenteur, à l'arche de la foire. Un petit voleur a vidé ma caisse dans la cohue!",
               jeu="[worried] Hé, le jeune! C'est le Bonimenteur, à l'arche de la foire. [annoyed] Un petit voleur a vidé ma caisse dans la cohue!")
        ],
        "intro": [
            _l("bonimenteur", "Toute la recette du jour, envolée! Il se perd déjà dans le monde, entre les kiosques.",
               jeu="[annoyed] Toute la recette du jour, envolée! [worried] Il se perd déjà dans le monde, entre les kiosques."),
            _l("bonimenteur", "Reprends-la par-derrière, pis rapporte-la-moi avant qu'il file par la palissade.",
               jeu="[firmly] Reprends-la par-derrière, pis rapporte-la-moi… avant qu'il file par la palissade."),
            _l("bonimenteur", "Pis méfie-toi, jeune : un voleur de foire travaille jamais tout seul.",
               jeu="[knowingly] Pis méfie-toi, jeune : [worried] un voleur de foire travaille jamais tout seul.")
        ],
        "pendant": [
            _p("bonimenteur", "Il se sauvera au premier bruit. Approche-toi comme un chat!", 0,
               jeu="[nervously] Il se sauvera au premier bruit. [quietly] Approche-toi comme un chat!"),
            _p("bonimenteur", "Y en manque la moitié! Son complice se sauve en moto avec le reste, cours-y après!", 1,
               jeu="[annoyed] Y en manque la moitié! [worried] Son complice se sauve en moto avec le reste… cours-y après!"),
            _p("bonimenteur", "Des Cravates, astheure? Mon doux, dans quoi je t'ai embarqué, toi?", 2,
               jeu="[nervously] Des Cravates, astheure? [worried] Mon doux… dans quoi je t'ai embarqué, toi?"),
            _p("bonimenteur", "Reviens à l'arche, jeune, pis tiens ma caisse à deux mains!", 3,
               jeu="[relieved] Reviens à l'arche, jeune… [cheerful] pis tiens ma caisse à deux mains!")
        ],
        "fin": [
            _l("bonimenteur", "Ma caisse! T'es de la vraie graine, toi. Reviens quand tu veux, la foire est à toi.",
               jeu="[relieved] Ma caisse! [warmly] T'es de la vraie graine, toi. Reviens quand tu veux, la foire est à toi."),
            _l("bonimenteur", "Tiens, pour ta peine. Pis un tour de grande roue gratuit, si le cœur t'en dit.",
               jeu="[cheerful] Tiens, pour ta peine. [playfully] Pis un tour de grande roue gratuit, si le cœur t'en dit.")
        ],
        "echec": [
            _l("bonimenteur", "Perdue... Toute une journée de recette, envolée dans la foule.",
               jeu="[disappointed] Perdue… [sighs] Toute une journée de recette, envolée dans la foule.")
        ]
    }
}
