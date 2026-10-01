"""La mission x04 — voir app/missions/__init__.py pour le moteur.

Le coup (M16, arc X, _Le coup de la Caisse populaire_, 1er oct. 2026). C'est jeudi : la paie de l'usine Prévost dort
dans la voûte de la caisse populaire de La Shop. On entre, on fait partir la minuterie (`obtenir`, `table: caisse` —
`caisse.js`, le coup : l'alarme, trois étoiles, une minute à tenir pendant que les gardes du fourgon entrent par la
porte, puis les sacs), on sort, on sème quatre étoiles, on rapporte les sacs au Brouillard. Sal voulait sa part :
il ne l'aura pas, et plus de dernière coupe (`ferme: d08`) — ni de préparatif à faire après coup (x02, x03).

⚠️ **CE QU'ON A PRÉPARÉ CHANGE LE COUP** — et le coup se joue quand même sans rien, plus mal :
- sans l'uniforme de livreur (x03 : on le porte, ou pas — `caisse.js` le lit sur toi), Fernand te reconnaît en
  entrant : deux étoiles et un vigile sur le dos avant même la voûte ;
- sans le coupé repeint (x02), rien n'attend dans la ruelle : l'objectif `monter` est `si: x02`, il se saute, et on
  sème avec ce qu'on trouve ;
- sans arme à feu, la minute se fait aux poings.
Chaque préparatif fait ou manquant se DIT au premier objectif (`_p(…, si=…)` / `sauf=…`).
"""

from ._commun import _l, _p

MISSION = {
    "slug": "x04",
    "titre": "Le coup",
    "donneur": "josee",
    "prerequis": ["x01"],
    "ferme": ["d08", "x02", "x03"],
    "recompense": 2500,
    "donne": {"message": "LA PAIE DE L'USINE EST AU BROUILLARD — SAL N'AURA PAS SA PART"},

    "objectifs": [
        {"type": "aller", "texte": "C'EST JEUDI : À LA CAISSE POP", "lieu": "caisse_pop", "rayon": 6},

        {"type": "obtenir", "texte": "LA VOÛTE : LA MINUTERIE, UNE MINUTE À TENIR, PUIS LES SACS",
         "objet": "sacs_caisse", "nom": "LES SACS DE LA PAIE", "dessin": "sac", "ou": "caisse_pop",
         "table": "caisse"},

        {"type": "monter", "texte": "LE COUPÉ REPEINT, DANS LA RUELLE : DÉMARRE",
         "vehicule": "sport", "ou": "ruelle:caisse_pop:4", "si": "x02"},

        {"type": "semer", "texte": "QUATRE ÉTOILES : SÈME-LES", "etoiles": 4},

        {"type": "aller", "texte": "LES SACS AU BROUILLARD", "lieu": "bar", "rayon": 5},

        {"type": "parler", "texte": "JOSÉE COMPTE, DEDANS", "cible": "josee"},
    ],

    # Intention (intro) : la seule fois où Josée parle de temps — une minute. La caméra va voir la porte de la caisse
    # sous la règle de la minuterie, et revient à elle pour l'ordre. ⚠️ La coupe part `ensemble`, la voix la retient.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 80, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:caisse_pop", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # Le jeu de chaque réplique (`jeu=`) — Josée : la Chef le jour du coup. Plus lente que d'habitude, pas plus
    # forte (`docs/jeu-d-acteur.md` § 3.2). Ce qui manque, elle le dit froidement ; ce qui est prêt, avec un fond de
    # fierté. Le seul `[warmly]`, à la fin, pour le neveu.
    "dialogue": {
        "appel": [
            _l("josee", "Josée. C'est jeudi, pis la paie est dans la voûte. Viens au bar, on fait ça aujourd'hui.",
               jeu="[quietly] Josée. C'est jeudi, pis la paie est dans la voûte. [firmly] Viens au bar… on fait ça aujourd'hui.")
        ],
        "intro": [
            _l("josee", "La voûte a une minuterie. Le gérant la part, pis elle s'ouvre une minute plus tard. Une longue minute.",
               jeu="[matter-of-fact] La voûte a une minuterie. Le gérant la part, pis elle s'ouvre une minute plus tard. [gravely] Une longue minute."),
            _l("josee", "L'alarme sonne au premier mot, pis les gardes du fourgon entrent. Si t'as un fusil, c'est le temps.",
               jeu="[serious] L'alarme sonne au premier mot, pis les gardes du fourgon entrent. [coldly] Si t'as un fusil, c'est le temps."),
            _l("josee", "Après, tu sèmes tout le monde pis tu me ramènes les sacs. Sal va vouloir sa part. Qu'il vienne la chercher.",
               jeu="[firmly] Après, tu sèmes tout le monde pis tu me ramènes les sacs. [coldly] Sal va vouloir sa part. [menacingly] Qu'il vienne la chercher.")
        ],
        "pendant": [
            _p("josee", "T'as l'uniforme de Rosa sur le dos? Fernand va te tenir la porte.", 0, si="x03",
               jeu="[knowingly] T'as l'uniforme de Rosa sur le dos? [wryly] Fernand va te tenir la porte."),
            _p("josee", "Pas d'uniforme. Fernand va te reconnaître en entrant : t'entres avec la police dans le dos.", 0, sauf="x03",
               jeu="[coldly] Pas d'uniforme. [serious] Fernand va te reconnaître en entrant : t'entres avec la police dans le dos."),
            _p("josee", "Le coupé repeint est dans la ruelle, les clés dessus. C'est ton chemin pour sortir.", 0, si="x02",
               jeu="[confident] Le coupé repeint est dans la ruelle, les clés dessus. [matter-of-fact] C'est ton chemin pour sortir."),
            _p("josee", "Pas de char à toi derrière la caisse. En sortant, prends ce qui roule, pis prie.", 0, sauf="x02",
               jeu="[coldly] Pas de char à toi derrière la caisse. [wryly] En sortant, prends ce qui roule… pis prie."),
            _p("josee", "La voûte est au fond. Fais partir la minuterie, pis compte jusqu'à soixante sans tomber.", 1,
               jeu="[quietly] La voûte est au fond. [firmly] Fais partir la minuterie… pis compte jusqu'à soixante sans tomber."),
            _p("josee", "Le coupé. Démarre, pis pense pas à moi avant d'être tout seul.", 2,
               jeu="[firmly] Le coupé. [serious] Démarre, pis pense pas à moi avant d'être tout seul."),
            _p("josee", "Quatre étoiles. Perds-les avant de venir, ou viens pas.", 3,
               jeu="[coldly] Quatre étoiles. [menacingly] Perds-les avant de venir… ou viens pas."),
            _p("josee", "Personne te suit? Amène les sacs au Brouillard, par la porte d'en avant.", 4,
               jeu="[calm] Personne te suit? [matter-of-fact] Amène les sacs au Brouillard, par la porte d'en avant.")
        ],
        "fin": [
            _l("josee", "Deux mille cinq cents pour toi. Le reste va à la famille, pis à des gens qui en ont plus besoin que l'usine.",
               jeu="[satisfied] Deux mille cinq cents pour toi. [matter-of-fact] Le reste va à la famille… pis à des gens qui en ont plus besoin que l'usine."),
            _l("josee", "Sal va savoir que c'est nous, pis il aura pas une cenne. T'as été bon, le neveu.",
               jeu="[coldly] Sal va savoir que c'est nous, pis il aura pas une cenne. [warmly] T'as été bon, le neveu.")
        ],
        "echec": [
            _l("josee", "Les sacs sont retournés à la caisse. Pis toi, t'as une face connue, astheure.",
               jeu="[coldly] Les sacs sont retournés à la caisse. [matter-of-fact] Pis toi, t'as une face connue, astheure.")
        ]
    }
}
