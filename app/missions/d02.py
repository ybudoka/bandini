"""La mission d02 — voir app/missions/__init__.py pour le moteur.

Le premier versement (M16, arc D, 30 sept. 2026). Sal veut cinq cents piasses ; tu ne les as pas — ou tu ne veux
pas les lui donner. Il a mieux : Momo, un chauffeur de taxi du terminus, lui doit exactement ça, et il se sauve
chaque fois qu'il voit la chaise de barbier. On le rattrape (le fuyard en taxi, le patron de m97), l'enveloppe
tombe, un témoin appelle la police, et on rapporte l'argent à Sal : c'est ton premier versement (`donne.dette`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "d02",
    "titre": "Le premier versement",
    "donneur": "sal",
    "prerequis": ["d01"],
    "recompense": 100,
    "donne": {"dette": -500, "message": "L'ENVELOPPE DE MOMO PAIE TON PREMIER VERSEMENT"},

    # ⚠️ `ramasser` + `cible: fuyard` depuis une pièce : `poserLeFuyard` part de la rue devant la porte
    # (`ouEstLeJoueurEnVille`, m50) — pas du coin de la ville. Sal est DEDANS (`point:sal`) : pas de `retourner`
    # (il ne se règle qu'avec un donneur dans la rue) ; on revient lui PARLER, et la fin se dit dans le terminus.
    "objectifs": [
        {"type": "ramasser", "texte": "MOMO LE TAXI DOIT 500 $ À SAL : RATTRAPE-LE",
         "cible": "fuyard", "vehicule": "taxi"},

        {"type": "semer", "texte": "UN TÉMOIN A APPELÉ LA POLICE : SÈME-LA", "etoiles": 1},

        {"type": "parler", "texte": "RAPPORTE L'ENVELOPPE DE MOMO À SAL, AU TERMINUS", "cible": "sal"},
    ],

    # Intention (intro) : Sal parle en coupant les cheveux — un geste, puis chaque réplique tient la scène (la voix
    # retient le plan ; l'intro par défaut les disait en `ensemble`, et la suivante coupait la première).
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "coupe", "vers": "porte:terminus", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "dire", "repliques": [3]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Sal : le prêteur amusé, qui sait tout de ses débiteurs et en parle comme
    # d'enfants turbulents. Au combiné, il est plus sec ; à la fin, le compte se dit comme une caresse — pis la
    # leçon, froidement : on ne se sauve pas de Sal.
    "dialogue": {
        "appel": [
            _l("sal", "C'est Sal, au terminus. Ton premier versement tombe aujourd'hui, le neveu. Passe me voir.",
               jeu="[calm] C'est Sal, au terminus. [matter-of-fact] Ton premier versement tombe aujourd'hui, le neveu. Passe me voir.")
        ],
        "intro": [
            _l("sal", "Cinq cents piasses. Tu les as pas? Je le savais, personne les a dans ta famille.",
               jeu="[amused] Cinq cents piasses. Tu les as pas? [wryly] Je le savais, personne les a dans ta famille."),
            _l("sal", "Momo, un chauffeur d'icitte, me doit justement ça. Il se sauve chaque fois qu'il voit ma chaise.",
               jeu="[knowingly] Momo, un chauffeur d'icitte, me doit justement ça. [amused] Il se sauve chaque fois qu'il voit ma chaise."),
            _l("sal", "Ramène-moi son enveloppe, pis on dira que c'est toi qui as payé.",
               jeu="[softly] Ramène-moi son enveloppe… [warmly] pis on dira que c'est toi qui as payé.")
        ],
        "pendant": [
            _p("sal", "Le v'là qui démarre. Il conduit comme il paie, le neveu : en retard pis tout croche.", 0,
               jeu="[amused] Le v'là qui démarre. [wryly] Il conduit comme il paie, le neveu : en retard pis tout croche."),
            _p("sal", "Les madames du terminus appellent la police pour un rien. Fais-toi oublier.", 1,
               jeu="[annoyed] Les madames du terminus appellent la police pour un rien. [calm] Fais-toi oublier."),
            _p("sal", "L'enveloppe, pas le taxi. Je coupe des cheveux, moi, je vends pas de chars.", 2,
               jeu="[matter-of-fact] L'enveloppe, pas le taxi. [wryly] Je coupe des cheveux, moi… je vends pas de chars.")
        ],
        "fin": [
            _l("sal", "Cinq cents, juste. Momo compte mieux qu'il conduit.",
               jeu="[satisfied] Cinq cents, juste. [amused] Momo compte mieux qu'il conduit."),
            _l("sal", "Je te les marque dans mon livre. Pis ça, c'est pour ta peine : on travaille pas pour rien chez nous.",
               jeu="[warmly] Je te les marque dans mon livre. [knowingly] Pis ça, c'est pour ta peine : on travaille pas pour rien chez nous.")
        ],
        "echec": [
            _l("sal", "Momo court encore. Pis toi, le neveu, t'as toujours ta dette.",
               jeu="[disappointed] Momo court encore. [coldly] Pis toi, le neveu… t'as toujours ta dette.")
        ]
    }
}
