"""La mission m54 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _l, _p

MISSION = {
    "slug": "m54",
    "titre": "Le grand soir",
    "donneur": "sven",
    "prerequis": ["m53"],
    "recompense": 900,
    "echec": ["mort", "arrete", "vehicule_detruit", "alarme"],
    "donne": {"message": "LE PORT NE L'A JAMAIS VU PARTIR"},

    # ⚠️ **LE GROS LOT DU FIL.** Le registre du quai note chaque sortie — l'effacer avant de
    # partir (le piratage le plus dur des trois : `longueur` 5, `essais` 2) — puis le
    # porte-conteneurs lui-même, le plus lent et le plus lourd du parc (`vehicules.py`) : une
    # poursuite dessus est un vrai test de pilotage, pas une formalité.
    "objectifs": [
        {"type": "pirater", "texte": "PIRATE LE REGISTRE DU QUAI, AVANT LE DÉPART",
         "ou": "mouillage:porte_conteneurs", "rayon": 5, "longueur": 5, "essais": 2},

        {"type": "monter", "texte": "PRENDS LE PORTE-CONTENEURS",
         "vehicule": "porte_conteneurs", "ou": "mouillage:porte_conteneurs", "prete": "sven"},

        {"type": "semer", "texte": "SÈME LA POLICE, LE PORT RÉVEILLÉ",
         "etoiles": 2},

        # ⚠️ **Plus long, plus loin** (Martin, 22 sept. 2026 : « des missions plus longues ») : la
        # cargaison va au hangar sans nom de l'Île-aux-Corneilles (`ile.py`, le hangar que l'arc I
        # donnera à Sven), à l'autre bout de la baie — son cadenas se pirate ; les Morues ont
        # suivi le sillage (`loin` : elles arrivent en courant) ; et au retour, le registre qui
        # note les sorties note aussi les retours. `ou` et pas `lieu` pour l'île : elle ne se
        # rejoint pas à pied (`test_barrieres.py`).
        {"type": "pirater", "texte": "SUR L'ÎLE, PIRATE LE CADENAS DU HANGAR SANS NOM",
         "ou": "hangar_ile", "rayon": 4, "longueur": 5, "essais": 3},

        {"type": "tuer", "texte": "DES MORUES ONT NAGÉ JUSQU'À L'ÎLE — PAS UNE NE REPART",
         "groupe": "morues", "n": 3, "ou": "hangar_ile", "loin": 12},

        {"type": "livrer", "texte": "RAMÈNE-LE À QUAI, EN UNE PIÈCE",
         "lieu": "mouillage:porte_conteneurs", "rayon": 6, "sans_degats": True},

        {"type": "pirater", "texte": "LE REGISTRE NOTE AUSSI LES RETOURS — EFFACE CELUI-LÀ",
         "ou": "mouillage:porte_conteneurs", "rayon": 5, "longueur": 5, "essais": 2},

        {"type": "retourner", "texte": "RETOURNE VOIR SVEN"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Sven, le grand soir : le même calcul, à peine
    # pressé par l'urgence (le « pendant » du `semer` est sa seule réplique qui hausse le
    # ton) ; la fin referme l'arc sur Josée, sans jamais élever la voix.
    "dialogue": {
        "appel": [
            _l("sven", "Sven, une dernière fois. Ce soir, mon bateau prend la mer, avec ou sans registre.",
               jeu="[Norwegian accent][calm] Sven… une dernière fois. [firmly] Ce soir, mon bateau prend la mer… avec ou sans registre.")
        ],
        "intro": [
            _l("sven", "Un registre note chaque sortie du quai. Efface la mienne avant que j'appareille.",
               jeu="[Norwegian accent][matter-of-fact] Un registre note… chaque sortie du quai. [firmly] Efface la mienne… avant que j'appareille."),
            _l("sven", "Ensuite, tu le mènes toi-même. Un porte-conteneurs ne se pilote pas à moitié.",
               jeu="[Norwegian accent][calm] Ensuite, tu le mènes… toi-même. [firmly] Un porte-conteneurs… ne se pilote pas à moitié."),
            _l("sven", "Il y a un hangar sur l'île. Ce qu'il contiendra ne regarde que moi.",
               jeu="[Norwegian accent][quietly] Il y a un hangar… sur l'île. [coldly] Ce qu'il contiendra… ne regarde que moi.")
        ],
        "pendant": [
            _p("sven", "Le boîtier est sur la jetée. Prends ton temps, mais pas trop.", 0,
               jeu="[Norwegian accent][calm] Le boîtier est… sur la jetée. [wryly] Prends ton temps… mais pas trop."),
            _p("sven", "Le port s'est réveillé! Perds-les dans le brouillard, pas dans un quai.", 2,
               jeu="[Norwegian accent][dramatic] Le port s'est… réveillé! [firmly] Perds-les dans le brouillard… pas dans un quai."),
            _p("sven", "Sur l'île, un hangar sans nom. Son cadenas est plus malin que son gardien.", 3,
               jeu="[Norwegian accent][calm] Sur l'île, un hangar… sans nom. [wryly] Son cadenas est plus malin… que son gardien."),
            _p("sven", "Des Morues qui nagent jusqu'à l'île. Pour une fois, le nom leur va bien.", 4,
               jeu="[Norwegian accent][deadpan] Des Morues qui nagent… jusqu'à l'île. [wryly] Pour une fois… le nom leur va bien."),
            _p("sven", "Le registre note aussi les retours. Il est plus consciencieux que la police.", 6,
               jeu="[Norwegian accent][matter-of-fact] Le registre note aussi… les retours. [wryly] Il est plus consciencieux… que la police.")
        ],
        "fin": [
            _l("sven", "Il flotte, il est à moi, et personne ne l'a noté. Parfait.",
               jeu="[Norwegian accent][satisfied] Il flotte, il est… à moi… et personne ne l'a noté. [calm] Parfait."),
            _l("sven", "Josée avait le port. Maintenant, j'ai un bateau qu'elle n'a jamais vu partir.",
               jeu="[Norwegian accent][coldly] Josée avait… le port. [firmly] Maintenant… j'ai un bateau qu'elle n'a jamais vu partir."),
            _l("sven", "Et le registre dira que je ne suis jamais parti. C'est presque vrai.",
               jeu="[Norwegian accent][satisfied] Et le registre dira… que je ne suis jamais parti. [wryly] C'est presque vrai.")
        ],
        "echec": [
            _l("sven", "Le registre me trahit, ou la police m'a vu. Ce n'est pas terminé.",
               jeu="[Norwegian accent][coldly] Le registre me trahit… ou la police m'a vu. [firmly] Ce n'est pas… terminé.")
        ]
    }

    # ⚠️ ELLE N'ÉCRIT AUCUNE SCÈNE : le premier objectif (`pirater`) nomme déjà
    # `mouillage:porte_conteneurs`, c'est lui que l'intro montre ; la fin referme chez Sven.
}
