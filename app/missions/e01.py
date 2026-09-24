"""La mission e01 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "e01",
    "titre": "Les drifts de Ti-Paul",
    "donneur": "tipaul",
    "prerequis": ["m6"],
    "recompense": 150,
    "donne": {"message": "TI-PAUL TE DOIT UNE BIÈRE"},

    # ⚠️ `rayon` 6 et pas 4 : Ti-Paul se tient à 48 px du point du dépanneur, et le joueur qui lui parle à
    # 16 px de plus — 64,03 px, un cheveu de plus que quatre tuiles. On était AU dépanneur et la mission
    # demandait un pas de plus (mesuré au banc).
    # ⚠️ Des ados, pas des Cravates : ils arrivent les poings nus et à 60 PV, comme les deux hommes
    # de m2 (« avec tes poings, pas plus »). Le drift, lui, est dans les mots — ils n'ont pas de char.
    "objectifs": [
        {"type": "aller", "texte": "VA AU DÉPANNEUR ET ATTENDS LA NUIT",
         "lieu": "depanneur", "rayon": 6, "nuit": True},

        {"type": "tuer", "texte": "REPOUSSE LES TROIS CHEVREUILS",
         "groupe": "chevreuils", "n": 3, "ou": "donneur", "arme": "", "vie": 60, "loin": 14},

        # « Des missions plus longues » (22 sept. 2026) : les petits couchés, leur grand frère arrive (le
        # chef : 160 PV, un bâton) ; le vacarme fait appeler la police par les voisins ; et Ti-Paul, qui
        # veut SA patrouille, t'envoie la demander à Bouchard, au casse-croûte — à l'autre bout de la
        # ville. Bouchard répond que la patrouille, tu viens de l'avoir. Puis on revient au dépanneur.
        {"type": "tuer", "texte": "LEUR GRAND FRÈRE ARRIVE — COUCHE-LE",
         "groupe": "chevreuils", "n": 1, "chef": True},

        {"type": "semer", "texte": "SÈME LA POLICE QUE LES VOISINS ONT APPELÉE",
         "etoiles": 1},

        {"type": "parler", "texte": "DEMANDE UNE PATROUILLE À BOUCHARD, AU CASSE-CROÛTE",
         "cible": "bouchard"},

        {"type": "retourner", "texte": "RETOURNE VOIR TI-PAUL"}
    ],

    # Le jeu de chaque réplique (`jeu=`) — Ti-Paul, les drifts : le bavard qui s'énerve pour son
    # parking, puis qui jubile. Sa voix est celle de Marco (« Québec Tremblay ») — jamais dans le
    # même dialogue, et lui, plus vif.
    "dialogue": {
        "appel": [
            _l("tipaul", "C'est Ti-Paul, du dépanneur! Les Chevreuils font des drifts dans mon parking. Viens vite!",
               jeu="[worried] C'est Ti-Paul, du dépanneur! Les Chevreuils font des drifts dans mon parking. [excited] Viens vite!")
        ],
        "intro": [
            _l("tipaul", "Tous les soirs, des drifts dans mon parking. Pis après, ils entrent se servir en bière.",
               jeu="[annoyed] Tous les soirs, des drifts dans mon parking. Pis après… ils entrent se servir en bière."),
            _l("tipaul", "Ils viennent de là-bas. Attends la noirceur icitte, pis explique-leur que c'est pas un bar.",
               jeu="[knowingly] Ils viennent de là-bas. [mischievously] Attends la noirceur icitte… pis explique-leur que c'est pas un bar."),
            _l("tipaul", "Pis frappe pas trop fort, hein: leurs parents achètent leurs gratteux icitte.",
               jeu="[nervously] Pis frappe pas trop fort, hein… [mischievously] leurs parents achètent leurs gratteux icitte.")
        ],
        "pendant": [
            _p("tipaul", "Les v'là! Pas dans mes vitrines, hein? Ça se répare mal, une vitrine.", 1,
               jeu="[nervously] Les v'là! Pas dans mes vitrines, hein? [worried] Ça se répare mal, une vitrine."),
            _p("tipaul", "Oh non, c'est leur grand frère! Lui, il a son permis de conduire, pis un bâton.", 2,
               jeu="[nervously] Oh non, c'est leur grand frère! [worried] Lui, il a son permis de conduire… pis un bâton."),
            _p("tipaul", "Les voisins ont appelé la police! Pas pour les drifts, hein: pour toi.", 3,
               jeu="[worried] Les voisins ont appelé la police! [wryly] Pas pour les drifts, hein… pour toi."),
            # Là ou au combiné (`present`) : caché chez lui, il te le dit en personne ; semé plus loin, au bout du fil.
            _p("tipaul", "Passe voir Bouchard, au casse-croûte. Dis-lui que mon parking a besoin d'une patrouille!", 4,
               jeu="[cheerful] Passe voir Bouchard, au casse-croûte. [mischievously] Dis-lui que mon parking a besoin d'une patrouille!")
        ],
        "fin": [
            _l("tipaul", "Trois Chevreuils étendus, pis mon parking est vide. T'es un artiste!",
               jeu="[impressed] Trois Chevreuils étendus, pis mon parking est vide. [cheerful] T'es un artiste!"),
            _l("tipaul", "Pas de patrouille? Ben c'est toi, ma patrouille, l'ami!",
               jeu="[amused] Pas de patrouille? [cheerful] Ben c'est toi, ma patrouille, l'ami!"),
            _l("tipaul", "Lulu, à la cantine, a un camion de poisson qui poireaute. Va la voir de ma part.",
               jeu="[knowingly] Lulu, à la cantine, a un camion de poisson qui poireaute. Va la voir… de ma part.")
        ],
        "echec": [
            _l("tipaul", "Ils t'ont eu? Bon… le parking est à eux ce soir. Reviens quand t'auras dormi.",
               jeu="[disappointed] Ils t'ont eu? Bon… le parking est à eux ce soir. [wryly] Reviens quand t'auras dormi.")
        ],
        # La poignée de main du casse-croûte : Bouchard est connu depuis m4, il ne se nomme pas chez lui.
        "accueil": [
            _a("bouchard", "Une patrouille? T'en avais deux au cul y a dix minutes. Ça, c'était sa patrouille.", 4,
               jeu="[deadpan] Une patrouille? T'en avais deux au cul y a dix minutes. [gruffly] Ça, c'était sa patrouille.")
        ]
    },

    # Intention (intro) : le joueur sait d'où viennent les Chevreuils — « ils viennent de là-bas » :
    # Ti-Paul montre leur coin, la caméra y va (le mot fait le geste, la voix dit quoi faire de la nuit).
    # Le défaut aurait montré la porte du dépanneur, là où Ti-Paul se tient déjà.
    # Intention (fin) : la fin passe la main. Ti-Paul nomme Lulu (m6 nous l'a présentée), montre sa
    # direction, et la caméra va voir sa cantine — c'est ce qui fait de q02 la suite, pas une mission
    # de plus. ⚠️ Le `dire` de la première réplique n'est PAS `ensemble` : la seconde ne le coupe pas.
    "scenes": {
        "intro": [
            { "type": "dire", "repliques": [1] },
            { "type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "zone:chevreuils",
              "duree": 60, "ensemble": True },
            { "type": "camera", "vers": "zone:chevreuils", "duree": 45, "courbe": "freine", "ensemble": True },
            { "type": "dire", "repliques": [2] },
            { "type": "camera", "vers": "joueur", "duree": 40, "courbe": "freine" },
            { "type": "dire", "repliques": [3] }
        ],
        "fin": [
            { "type": "geste", "acteur": "donneur", "geste": "donner", "vers": "joueur", "duree": 60,
              "ensemble": True },
            { "type": "dire", "repliques": [1] },
            { "type": "attendre", "duree": 20 },
            { "type": "dire", "repliques": [2] },
            { "type": "attendre", "duree": 25 },
            { "type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "chez:lulu", "duree": 60,
              "ensemble": True },
            { "type": "coupe", "vers": "chez:lulu", "ferme": 20, "ouvre": 20, "tient": 130, "ensemble": True },
            { "type": "dire", "repliques": [3] }
        ]
    }
}
