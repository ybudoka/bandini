"""La mission t08 — voir app/missions/__init__.py pour le moteur.

Une job de bras (M16, arc T, les petites jobs — 1er oct. 2026). Un ouvrier de La Shop, le dos barré : le camion de
pièces a tout débarqué au coin de la ruelle, trois boîtes, et le contremaître les veut dans l'usine avant de les voir
traîner dehors. Elles sont lourdes, on marche (`a_pied` : au volant, rien ne compte) ; chaque boîte posée à la porte
quitte le sac (`depose`), la suivante attend au coin. Un passant qui donne une job (`passant`).

⚠️ LA RÈGLE DE L'USINE (`missions.barriere_d_heure`) : la porte de l'usine est derrière la chaîne de sa cour, qui ferme
la nuit. Cette job ne s'offre donc que le jour (`Jobs.aLHeure`), et prise, elle tient la chaîne ouverte jusqu'à sa fin
(`Monde.barriereFermee`) : on ne finit pas devant une porte fermée.
"""

from ._commun import _l, _p

#: Le coin où le camion a tout débarqué : la ruelle de l'usine, à dix tuiles de sa porte, hors de la chaîne.
CAMION = "ruelle:usine:10"


def _boite(rang: str) -> list[dict]:
    """Une boîte : la ramasser au coin (à pied, `obtenir`), la porter à la porte de l'usine (`aller`, à pied)."""
    return [
        {"type": "obtenir", "texte": f"LA {rang} BOÎTE, AU COIN DE LA RUELLE", "objet": "boite", "ou": CAMION,
         "dessin": "boite", "nom": "UNE BOÎTE DE PIÈCES"},
        {"type": "aller", "texte": "PORTE-LA À LA PORTE DE L'USINE", "lieu": "usine", "rayon": 3, "a_pied": True,
         "depose": "boite"},
    ]


MISSION = {
    "slug": "t08",
    "titre": "Une job de bras",
    "donneur": "passant",
    "prerequis": ["m6"],
    "recompense": 45,
    "passant": {"archetype": "ouvrier", "district": "shop", "nom": "L'ouvrier"},
    "donne": {"message": "TROIS BOÎTES, UN DOS SAUVÉ"},

    "objectifs": _boite("PREMIÈRE") + _boite("DEUXIÈME") + _boite("TROISIÈME") + [
        {"type": "retourner", "texte": "RETOURNE VOIR L'OUVRIER"},
    ],

    # Le jeu (`jeu=`) — l'ouvrier : le dos barré, la fierté plus barrée encore ; il ne demande jamais rien, alors il le
    # demande mal. Il ne dit pas son nom (un passant ne se présente pas).
    "dialogue": {
        "hele": [
            _l("passant", "Hé! T'es fort?", jeu="[gruffly] Hé! T'es fort?")
        ],
        "intro": [
            _l("passant", "Le camion a tout débarqué au coin de la ruelle. Trois boîtes de pièces, pis mon dos vient de lâcher.",
               jeu="[groans] Le camion a tout débarqué au coin de la ruelle. [annoyed] Trois boîtes de pièces, pis mon dos vient de lâcher."),
            _l("passant", "Rentre-les à la porte de l'usine avant que le contremaître les voie dehors. À pied, c'est pas des oreillers.",
               jeu="[nervously] Rentre-les à la porte de l'usine avant que le contremaître les voie dehors. [wryly] À pied, c'est pas des oreillers.")
        ],
        "pendant": [
            _p("passant", "Plie les genoux, pas le dos. Regarde-moi pas, fais ce que je dis.", 0,
               jeu="[gruffly] Plie les genoux, pas le dos. [wryly] Regarde-moi pas, fais ce que je dis."),
            _p("passant", "Une de faite. Lâche pas, la deuxième est plus pesante.", 2,
               jeu="[satisfied] Une de faite. [teasing] Lâche pas, la deuxième est plus pesante."),
            _p("passant", "La dernière. C'est celle avec les boulons, bonne chance.", 4,
               jeu="[amused] La dernière. [deadpan] C'est celle avec les boulons, bonne chance."),
            _p("passant", "Viens-t'en, que je te paie avant que mon dos se souvienne de moi.", 6,
               jeu="[relieved] Viens-t'en, que je te paie avant que mon dos se souvienne de moi.")
        ],
        "fin": [
            _l("passant", "Trois boîtes, pas une échappée. Tiens, quarante-cinq piasses, pis va t'acheter une ceinture lombaire.",
               jeu="[impressed] Trois boîtes, pas une échappée. [teasing] Tiens, quarante-cinq piasses, pis va t'acheter une ceinture lombaire.")
        ],
        "echec": [
            _l("passant", "Laisse faire. Je vais les rentrer à quatre pattes, comme un homme.",
               jeu="[disappointed] Laisse faire. [sarcastic] Je vais les rentrer à quatre pattes, comme un homme.")
        ]
    }
}
