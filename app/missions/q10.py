"""La mission q10 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "q10",
    "titre": "Le Norvégien te reçoit",
    "donneur": "sven",
    "prerequis": ["q04", "m54"],
    # ⚠️ LE CHOIX (M16, `ferme`) : Sven ou Josée, pas les deux. Faire celle-ci ferme q11
    # pour de bon — elle n'apparaît plus ni au téléphone ni au carnet — et l'inverse.
    "ferme": "q11",
    "recompense": 600,
    "echec": ["mort", "arrete", "vehicule_detruit", "chrono"],
    "donne": {"message": "SVEN PAIE CE QU'IL PROMET"},

    # Après m54 : Sven avait dit « une dernière fois », et il le sait. La moto attend à la
    # barrière du pont (`ou: pont`) ; le phare en une minute (`chrono_s` sur le
    # `livrer` : 81 tuiles à vol d'oiseau, une moto en fait 19 à la seconde) ; sans une bosse, la prime de la moitié (`sans_degats`, `sansBosse`) —
    # le texte de l'objectif le dit tel quel, c'est une prime et pas une condition.
    "objectifs": [
        {"type": "monter", "texte": "PRENDS LA MOTO QUI T'ATTEND AU PONT",
         "vehicule": "moto", "ou": "pont"},

        {"type": "livrer", "texte": "AU PHARE EN 1 MIN — SANS BOSSE, IL PAIE PLUS",
         "lieu": "phare", "rayon": 4, "sans_degats": True, "chrono_s": 60},

        {"type": "retourner", "texte": "REVIENS VOIR SVEN SUR LA JETÉE"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Sven : précis, froid, un français correct ; il
    # ne hausse jamais le ton, il pose une offre comme on pose une pièce sur un échiquier.
    "dialogue": {
        "appel": [
            _l("sven", "Sven. Je sais, j'avais dit une dernière fois. J'ai une meilleure offre que celle de Josée.",
               jeu="[Norwegian accent][calm] Sven. Je sais… j'avais dit une dernière fois. [knowingly] J'ai une meilleure offre… que celle de Josée.")
        ],
        "intro": [
            _l("sven", "Une moto attend près du pont. Ce qu'elle transporte n'a pas de nom.",
               jeu="[Norwegian accent][matter-of-fact] Une moto attend… près du pont. [coldly] Ce qu'elle transporte… n'a pas de nom."),
            _l("sven", "Le phare, en une minute. Sans une rayure, je paie la moitié de plus.",
               jeu="[Norwegian accent][firmly] Le phare… en une minute. [calm] Sans une rayure… je paie la moitié de plus."),
            _l("sven", "Josée te demandera de choisir. Choisis maintenant, c'est plus élégant.",
               jeu="[Norwegian accent][wryly] Josée te demandera de choisir. [calm] Choisis maintenant… c'est plus élégant.")
        ],
        "pendant": [
            _p("sven", "Elle est à toi pour une minute. Ne la regarde pas trop.", 0,
               jeu="[Norwegian accent][calm] Elle est à toi… pour une minute. [wryly] Ne la regarde pas trop."),
            _p("sven", "Le phare. À cette heure, seuls les goélands regardent.", 1,
               jeu="[Norwegian accent][matter-of-fact] Le phare. [calm] À cette heure… seuls les goélands regardent."),
            _p("sven", "Reviens sur la jetée. Je paie comme je l'ai dit.", 2,
               jeu="[Norwegian accent][calm] Reviens sur la jetée. [firmly] Je paie comme je l'ai dit.")
        ],
        "fin": [
            _l("sven", "Livré à l'heure. Tu vois, la discrétion se paie mieux que la loyauté.",
               jeu="[Norwegian accent][satisfied] Livré à l'heure. [coldly] Tu vois… la discrétion se paie mieux que la loyauté."),
            _l("sven", "Josée l'apprendra demain. Elle n'aime pas apprendre.",
               jeu="[Norwegian accent][wryly] Josée l'apprendra demain. [calm] Elle n'aime pas apprendre.")
        ],
        "echec": [
            _l("sven", "La moto n'est pas arrivée. Tu n'étais pas prêt.",
               jeu="[Norwegian accent][coldly] La moto n'est pas arrivée. [calm] Tu n'étais pas prêt.")
        ]
    }
}
