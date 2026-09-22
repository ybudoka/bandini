"""La mission h02 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "h02",
    "titre": "Les pilules",
    "donneur": "ginette",
    "prerequis": ["h01"],
    "recompense": 250,
    "donne": {"message": "LA PHARMACIE EST AU COMPLET"},

    # ⚠️ `suivre` (même patron que f06 : `vehicule`, `loin`/`proche`) puis
    # `pickpocket` (même patron que f07 : l'archétype dédié, jamais un archétype
    # de gang). Ginette se tient DEHORS (`porte:hopital`) : `retourner` fonctionne.
    "objectifs": [
        {"type": "suivre", "texte": "SUIS-LE SANS TE FAIRE REPÉRER",
         "vehicule": "auto", "loin": 10, "proche": 3},

        {"type": "pickpocket", "texte": "REPRENDS LES PILULES, PAR-DERRIÈRE", "cible": "pickpocket"},

        {"type": "retourner", "texte": "RAPPORTE-LES À GINETTE"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Ginette : sèche, elle sait tout ce qui se
    # passe dans son hôpital et n'a pas de patience pour ceux qui en profitent.
    "dialogue": {
        "appel": [
            _l("ginette", "C'est Ginette, de l'hôpital. Un commis vide notre pharmacie depuis des semaines. J'ai besoin de toi.",
               jeu="[annoyed] C'est Ginette, de l'hôpital. Un commis vide notre pharmacie depuis des semaines. [firmly] J'ai besoin de toi.")
        ],
        "intro": [
            _l("ginette", "Il sort dans dix minutes. Suis-le sans qu'il te voie, il va vendre ça au dépanneur.",
               jeu="[matter-of-fact] Il sort dans dix minutes. [firmly] Suis-le sans qu'il te voie… il va vendre ça au dépanneur."),
            _l("ginette", "Une fois la vente faite, reprends nos pilules par-derrière. Discret, comme toujours.",
               jeu="[knowingly] Une fois la vente faite, reprends nos pilules par-derrière. [quietly] Discret, comme toujours.")
        ],
        "pendant": [
            _p("ginette", "Il regarde dans son rétroviseur souvent. Garde tes distances.", 0,
               jeu="[gravely] Il regarde dans son rétroviseur souvent. [firmly] Garde tes distances.")
        ],
        "fin": [
            _l("ginette", "Toutes là. Ce commis-là ne remettra plus les pieds dans ma pharmacie.",
               jeu="[satisfied] Toutes là. [firmly] Ce commis-là ne remettra plus les pieds dans ma pharmacie."),
            _l("ginette", "Bon travail. L'hôpital s'en souviendra, la prochaine fois que t'en auras besoin.",
               jeu="[matter-of-fact] Bon travail. [warmly] L'hôpital s'en souviendra, la prochaine fois que t'en auras besoin.")
        ],
        "echec": [
            _l("ginette", "Perdues... Il va continuer à vider mes tablettes. Reviens quand t'es prêt.",
               jeu="[disappointed] Perdues… [annoyed] Il va continuer à vider mes tablettes. Reviens quand t'es prêt.")
        ]
    }
}
