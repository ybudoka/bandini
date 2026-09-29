"""La mission e04 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "e04",
    "titre": "La course des Chevreuils",
    "donneur": "jo",
    "prerequis": ["e01"],
    "recompense": 300,
    # ⚠️ `calme` (M16) : les Chevreuils te respectent — tu as rattrapé leur meilleur pilote. Plus un ne te saute
    # dessus pour une arme au poing (`Entites.gangCalme`).
    "donne": {"calme": "chevreuils", "message": "LES CHEVREUILS TE RESPECTENT"},

    # ⚠️ RÉÉCRITE (29 sept. 2026). La fiche disait « une `course` `contre` trois Chevreuils » : ni `course` ni
    # `contre` ne sont lus par `histoire.js` (une `course` avancerait dans la même image). La course se joue donc
    # avec ce qui roule déjà : le pilote des Chevreuils part devant en sport (`ramasser`, `cible: fuyard` — le
    # patron de m2, m50, f03), on le rattrape ou on le casse, et ses clés tombent ; on les rapporte à Jo.
    "objectifs": [
        {"type": "ramasser", "texte": "LEUR PILOTE FILE EN SPORT — RATTRAPE-LE",
         "vehicule": "sport", "cible": "fuyard"},

        {"type": "retourner", "texte": "RAPPORTE SES CLÉS À JO"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Jo : le fils de bonne famille qui joue au dur ; il parle vite, fort, et
    # rit de ses propres phrases. Il appelle tout le monde « le vieux ». À la fin, il perd, et il le prend en riant —
    # trop fort, parce que ses gars regardent.
    "dialogue": {
        "appel": [
            _l("jo", "C'est Jo, des Chevreuils. Paraît que t'as couché mes petits frères. Viens au dépanneur, le vieux.",
               jeu="[mischievously] C'est Jo, des Chevreuils. [teasing] Paraît que t'as couché mes petits frères… Viens au dépanneur, le vieux.")
        ],
        "intro": [
            _l("jo", "Tu frappes fort. Mais icitte, on se respecte au volant, pas aux poings.",
               jeu="[smugly] Tu frappes fort. [confident] Mais icitte, on se respecte au volant… pas aux poings."),
            _l("jo", "Mon meilleur pilote part devant, en sport. Tu le rattrapes, ses clés sont à toi.",
               jeu="[excited] Mon meilleur pilote part devant, en sport. [playfully] Tu le rattrapes… ses clés sont à toi."),
            _l("jo", "Tu le rattrapes pas, tu retournes chez vous en autobus. Go!",
               jeu="[teasing] Tu le rattrapes pas, tu retournes chez vous en autobus. [shouting] Go!")
        ],
        "pendant": [
            _p("jo", "Y est parti! Colle-lui au pare-chocs, le vieux!", 0,
               jeu="[excited] Y est parti! [shouting] Colle-lui au pare-chocs, le vieux!"),
            _p("jo", "OK, OK, t'es capable. Apporte-moi ses clés, qu'on en finisse.", 1,
               jeu="[impressed] OK, OK… t'es capable. [casually] Apporte-moi ses clés, qu'on en finisse.")
        ],
        "fin": [
            _l("jo", "Ses clés. Ha! Il va entendre parler de ça jusqu'à Noël.",
               jeu="[laughs] [amused] Ses clés. Ha! Il va entendre parler de ça jusqu'à Noël."),
            _l("jo", "Les Chevreuils te toucheront pas, le vieux. Pis dis rien à ma mère, OK?",
               jeu="[confident] Les Chevreuils te toucheront pas, le vieux. [nervously] Pis dis rien à ma mère, OK?")
        ],
        "echec": [
            _l("jo", "T'as même pas fini la course! L'autobus passe à six heures, le vieux.",
               jeu="[laughs] [teasing] T'as même pas fini la course! L'autobus passe à six heures, le vieux.")
        ]
    }
}
