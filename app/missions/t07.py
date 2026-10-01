"""La mission t07 — voir app/missions/__init__.py pour le moteur.

Le p'tit est perdu (M16, arc T, les petites jobs — 1er oct. 2026). Une mère, n'importe où en ville : son p'tit joue à
la cachette depuis vingt minutes et ne répond plus. Il est là, pas loin — caché contre un mur ou derrière un décor
(`chercher` : sa place vient de l'empreinte, sans un dé ; la ligne d'objectif dit FROID, TIÈDE, CHAUD, BRÛLANT). On le
trouve à pied, il nous suit, et on le ramène à sa mère (`retourner` : pas sans lui). Un passant qui donne une job
(`passant`, de partout).

⚠️ Écart à la fiche : on ne le « protège » pas jusqu'à elle — il nous suit (`majProtege`), et elle attend là où elle
t'a hélé.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "t07",
    "titre": "Le p'tit est perdu",
    "donneur": "passante",
    "prerequis": ["m6"],
    "recompense": 60,
    "passant": {"archetype": "mere", "district": None, "nom": "La mère inquiète"},
    "donne": {"message": "LE P'TIT EST RETROUVÉ"},

    "objectifs": [
        {"type": "chercher", "texte": "TROUVE LE P'TIT — IL JOUE À LA CACHETTE", "qui": "enfant", "ou": "donneur",
         "rayon": 10, "nom": "LE P'TIT"},
        {"type": "retourner", "texte": "RAMÈNE LE P'TIT À SA MÈRE"},
    ],

    # Le jeu (`jeu=`) — la mère : inquiète, puis en colère d'avoir eu peur, puis soulagée ; elle ne dit jamais son nom.
    "dialogue": {
        "hele": [
            _l("passante", "Aidez-moi, vous!", jeu="[worried] Aidez-moi, vous!")
        ],
        "intro": [
            _l("passante", "On jouait à la cachette, pis ça fait vingt minutes qu'il répond plus.",
               jeu="[worried] On jouait à la cachette, [nervously] pis ça fait vingt minutes qu'il répond plus."),
            _l("passante", "Il est pas loin, il va jamais loin. Il se colle aux murs, comme son père.",
               jeu="[nervously] Il est pas loin, il va jamais loin. [sighs] Il se colle aux murs, comme son père.")
        ],
        "pendant": [
            _p("passante", "Regarde derrière les poubelles, les marches, les clôtures. Il est petit, hein.", 0,
               jeu="[worried] Regarde derrière les poubelles, les marches, les clôtures. [softly] Il est petit, hein."),
            _p("passante", "Tu l'as! Ramène-le-moi, que je le chicane comme du monde.", 1,
               jeu="[relieved] Tu l'as! [annoyed] Ramène-le-moi, que je le chicane comme du monde.")
        ],
        "fin": [
            _l("passante", "Toi, mon petit vlimeux! Merci, monsieur. Tenez, pour votre peine.",
               jeu="[annoyed] Toi, mon petit vlimeux! [relieved] Merci, monsieur. Tenez, pour votre peine.")
        ],
        "echec": [
            _l("passante", "Laissez faire, j'appelle la police. Pis son père, ce qui est pire.",
               jeu="[worried] Laissez faire, j'appelle la police. [sighs] Pis son père, ce qui est pire.")
        ]
    }
}
