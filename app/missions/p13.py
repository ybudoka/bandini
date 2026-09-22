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
    "objectifs": [
        {"type": "pickpocket", "texte": "REPRENDS LA CAISSE, PAR-DERRIÈRE", "cible": "pickpocket"},

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
               jeu="[firmly] Reprends-la par-derrière, pis rapporte-la-moi… avant qu'il file par la palissade.")
        ],
        "pendant": [
            _p("bonimenteur", "Il se sauvera au premier bruit. Approche-toi comme un chat!", 0,
               jeu="[nervously] Il se sauvera au premier bruit. [quietly] Approche-toi comme un chat!")
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
