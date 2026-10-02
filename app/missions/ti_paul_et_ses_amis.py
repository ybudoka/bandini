"""Le chapitre de Ti-Paul et ses amis — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague E). Ti-Paul, au dépanneur des Érables, a trois services : e01 (les drifts des Chevreuils dans son parking), e02 (sa bière
restée aux Quais, livrée sans une bosse) et e09 (les poutines du barbecue de janvier, sous le chrono) — six, quatre et
trois étapes — trois ACTES d'une amitié de dépanneur (8 à 10 minutes).

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : les appels de e02 et e09 perdent « C'est Ti-Paul! » et « C'est Ti-Paul,
  du dépanneur! » — la même voix, coupée au silence ;
- l'échec `vehicule_detruit` de e02 (le camion de bière) vaut pour le chapitre ;
- la scène d'intro de e01 reste celle du chapitre ; celle de fin de e09 aussi, si elle est écrite.
- Ce qui attendait e01 l'attend encore — l'acte 1 (q02, m51, les Chevreuils, e05 ; Diane et Jo arrivent après lui) :
  un prérequis peut viser un acte.
"""

from ._commun import _a, _e, _l, _p

MISSION = {
    "slug": "ti_paul_et_ses_amis",
    "titre": "Ti-Paul et ses amis",
    "donneur": "tipaul",
    "prerequis": ["m6"],
    "remplace": ["e01", "e02", "e09"],
    "recompense": 150,
    "donne": {"message": "LE BARBECUE DE TI-PAUL"},
    "echec": ["mort", "arrete", "vehicule_detruit"],

    "objectifs": [
        # --- Acte 1 (e01, « Les drifts de Ti-Paul »).
        {"type": "acte", "texte": "ACTE 1 — LES DRIFTS DE TI-PAUL", "donneur": "tipaul"},  # 0
        {"type": "aller", "texte": "VA AU DÉPANNEUR ET ATTENDS LA NUIT", "lieu": "depanneur", "rayon": 6, "nuit": True},  # 1
        {"type": "tuer", "texte": "REPOUSSE LES TROIS CHEVREUILS", "groupe": "chevreuils", "n": 3, "ou": "donneur", "arme": "", "vie": 60, "loin": 14},  # 2
        {"type": "tuer", "texte": "LEUR GRAND FRÈRE ARRIVE — COUCHE-LE", "groupe": "chevreuils", "n": 1, "chef": True},  # 3
        {"type": "semer", "texte": "SÈME LA POLICE QUE LES VOISINS ONT APPELÉE", "etoiles": 1},  # 4
        {"type": "parler", "texte": "DEMANDE UNE PATROUILLE À BOUCHARD, AU CASSE-CROÛTE", "cible": "bouchard"},  # 5
        {"type": "retourner", "texte": "RETOURNE VOIR TI-PAUL", "donne": {"message": "TI-PAUL TE DOIT UNE BIÈRE", "prime": 150}},  # 6
        # --- Acte 2 (e02, « La bière de Ti-Paul »).
        {"type": "acte", "texte": "ACTE 2 — LA BIÈRE DE TI-PAUL", "donneur": "tipaul"},  # 7
        {"type": "monter", "texte": "PRENDS LE CAMION DE BIÈRE", "vehicule": "camion", "ou": "porte:cantine"},  # 8
        {"type": "aller", "texte": "LAISSE DEUX CAISSES AU PHARE", "lieu": "phare", "rayon": 6},  # 9
        {"type": "semer", "texte": "UNE PATROUILLE TE SUIT, SÈME-LA", "etoiles": 1},  # 10
        {"type": "livrer", "texte": "LIVRE-LE AU DÉPANNEUR SANS BOSSE", "lieu": "depanneur", "rayon": 4, "sans_degats": True, "donne": {"message": "LE DÉPANNEUR EST STOCKÉ POUR UN MOIS", "prime": 250}},  # 11
        # --- Acte 3 (e09, « Le barbecue de janvier »).
        # Le barbecue de janvier (M16, arc E, 1er oct. 2026). Tous les hivers, Ti-Paul fait un barbecue dans son stationnement
        # pour les gars de la rue — en janvier, parce que « l'été, tout le monde en fait ». Les poutines du dépanneur doivent
        # arriver chaudes à trois commerces des Érables (la quincaillerie, le lave-auto, Prestige Autos), sous le chrono
        # (`course`, `chrono_s`), dans le camion de Ti-Paul (`monter`) ; puis le barbecue (`retourner`).
        # ⚠️ Écarts à la fiche (« Le barbecue », en vélo) : le vélo est remisé l'hiver et une partie commence en janvier — le
        # camion de Ti-Paul ; trois arrêts aux enseignes de la rue (une porte neuve ferait glisser la ville), à huit tuiles (les
        # enseignes sont loin de la chaussée).
        {"type": "acte", "texte": "ACTE 3 — LE BARBECUE DE JANVIER", "donneur": "tipaul"},  # 12
        {"type": "monter", "texte": "LE CAMION DE TI-PAUL, DERRIÈRE LE DÉPANNEUR", "vehicule": "camion", "ou": "ruelle:depanneur:12", "prete": "tipaul"},  # 13
        {"type": "course", "texte": "TROIS POUTINES CHAUDES : QUINCAILLERIE, LAVE-AUTO, PRESTIGE", "points": ["boutique:quincaillerie", "boutique:lave-auto", "boutique:prestige"], "rayon": 8, "chrono_s": 120},  # 14
        {"type": "retourner", "texte": "REVIENS AU DÉPANNEUR, LE BARBECUE COMMENCE"},  # 15
    ],

    "scenes": {
        "intro": [
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "vers": "zone:chevreuils", "duree": 60, "ensemble": True},
            {"type": "camera", "vers": "zone:chevreuils", "duree": 45, "courbe": "freine", "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "camera", "vers": "joueur", "duree": 40, "courbe": "freine"},
            {"type": "dire", "repliques": [3]},
        ],
    },

    # e01 — Le jeu de chaque réplique (`jeu=`) — Ti-Paul, les drifts : le bavard qui s'énerve pour son
    # parking, puis qui jubile. Sa voix est celle de Marco (« Québec Tremblay ») — jamais dans le
    # même dialogue, et lui, plus vif.
    # e02 — Le jeu de chaque réplique (`jeu=`) — Ti-Paul, comme e01 : bavard, s'énerve vite,
    # jubile encore plus vite. Sa voix (Québec Tremblay) est celle de Marco — jamais
    # dans le même dialogue.
    # e09 — Le jeu de chaque réplique (`jeu=`) — Ti-Paul : jovial, bavard, il parle de son parking comme d'un pays.
    "dialogue": {
        "appel": [
            _l("tipaul", "C'est Ti-Paul, du dépanneur! Les Chevreuils font des drifts dans mon parking. Viens vite!", jeu="[worried] C'est Ti-Paul, du dépanneur! Les Chevreuils font des drifts dans mon parking. [excited] Viens vite!"),
        ],
        "intro": [
            _l("tipaul", "Tous les soirs, des drifts dans mon parking. Pis après, ils entrent se servir en bière.", jeu="[annoyed] Tous les soirs, des drifts dans mon parking. Pis après… ils entrent se servir en bière."),
            _l("tipaul", "Ils viennent de là-bas. Attends la noirceur icitte, pis explique-leur que c'est pas un bar.", jeu="[knowingly] Ils viennent de là-bas. [mischievously] Attends la noirceur icitte… pis explique-leur que c'est pas un bar."),
            _l("tipaul", "Pis frappe pas trop fort, hein: leurs parents achètent leurs gratteux icitte.", jeu="[nervously] Pis frappe pas trop fort, hein… [mischievously] leurs parents achètent leurs gratteux icitte."),
        ],
        "fin": [
            _l("tipaul", "Trois livraisons, trois poutines chaudes! T'es plus rapide que mon ancien livreur.", jeu="[excited] Trois livraisons, trois poutines chaudes! [playfully] T'es plus rapide que mon ancien livreur."),
            _l("tipaul", "Tiens, ta paye, pis une saucisse. Elle est un peu brûlée, c'est la tradition.", jeu="[cheerful] Tiens, ta paye, pis une saucisse. [laughs] Elle est un peu brûlée, c'est la tradition."),
        ],
        "echec": [
            _e("tipaul", "Ils t'ont eu? Bon… le parking est à eux ce soir. Reviens quand t'auras dormi.", 0, jeu="[disappointed] Ils t'ont eu? Bon… le parking est à eux ce soir. [wryly] Reviens quand t'auras dormi."),
            _e("tipaul", "Envolée, ma bière... Un mois à sec, à cause de ça.", 7, jeu="[disappointed] Envolée, ma bière… [sighs] Un mois à sec, à cause de ça."),
            _e("tipaul", "Elles sont arrivées froides. Les gars de Prestige m'appellent pus, astheure.", 12, jeu="[disappointed] Elles sont arrivées froides. [sighs] Les gars de Prestige m'appellent pus, astheure."),
        ],
        "pendant": [
            _p("tipaul", "Les v'là! Pas dans mes vitrines, hein? Ça se répare mal, une vitrine.", 2, jeu="[nervously] Les v'là! Pas dans mes vitrines, hein? [worried] Ça se répare mal, une vitrine."),
            _p("tipaul", "Oh non, c'est leur grand frère! Lui, il a son permis de conduire, pis un bâton.", 3, jeu="[nervously] Oh non, c'est leur grand frère! [worried] Lui, il a son permis de conduire… pis un bâton."),
            _p("tipaul", "Les voisins ont appelé la police! Pas pour les drifts, hein: pour toi.", 4, jeu="[worried] Les voisins ont appelé la police! [wryly] Pas pour les drifts, hein… pour toi."),
            _p("tipaul", "Passe voir Bouchard, au casse-croûte. Dis-lui que mon parking a besoin d'une patrouille!", 5, jeu="[cheerful] Passe voir Bouchard, au casse-croûte. [mischievously] Dis-lui que mon parking a besoin d'une patrouille!"),
            # Acte 2 : la fin de e01, en personne ; puis l'appel et l'intro de e02.
            _p("tipaul", "Trois Chevreuils étendus, pis mon parking est vide. T'es un artiste!", 7, jeu="[impressed] Trois Chevreuils étendus, pis mon parking est vide. [cheerful] T'es un artiste!"),
            _p("tipaul", "Pas de patrouille? Ben c'est toi, ma patrouille, l'ami!", 7, jeu="[amused] Pas de patrouille? [cheerful] Ben c'est toi, ma patrouille, l'ami!"),
            _p("tipaul", "Lulu, à la cantine, a un camion de poisson qui poireaute. Va la voir de ma part.", 7, jeu="[knowingly] Lulu, à la cantine, a un camion de poisson qui poireaute. Va la voir… de ma part."),
            # ⚠️ Coupée (2 oct. 2026) : « C'est Ti-Paul! » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("tipaul", "Mon stock de bière est resté au quai des Quais. Va donc me le chercher!", 7, jeu="[worried] Mon stock de bière est resté au quai des Quais. [excited] Va donc me le chercher!"),
            _p("tipaul", "Le camion est caché derrière la cantine de Lulu. Prends-le, pis roule tranquille jusqu'ici.", 7, jeu="[matter-of-fact] Le camion est caché derrière la cantine de Lulu. [firmly] Prends-le, pis roule tranquille jusqu'ici."),
            _p("tipaul", "Pas une caisse de cassée! J'ai des clients qui comptent leurs bouteilles.", 7, jeu="[annoyed] Pas une caisse de cassée! [playfully] J'ai des clients qui comptent leurs bouteilles."),
            _p("tipaul", "Pis en passant, laisse deux caisses au gardien du phare. Il paie en retard, mais il paie en poisson.", 7, jeu="[mischievously] Pis en passant, laisse deux caisses au gardien du phare. [amused] Il paie en retard, mais il paie en poisson."),
            _p("tipaul", "Douce, douce! C'est pas une course, c'est de la bière!", 8, jeu="[nervously] Douce, douce! [firmly] C'est pas une course, c'est de la bière!"),
            _p("tipaul", "Tout au bout de La Pointe, l'ami! Deux caisses, pas trois : il compte juste quand ça l'arrange.", 9, jeu="[cheerful] Tout au bout de La Pointe, l'ami! [knowingly] Deux caisses, pas trois… il compte juste quand ça l'arrange."),
            _p("tipaul", "Une patrouille te suit? Ma bière a pas de permis, pis toi non plus. Sème-les!", 10, jeu="[nervously] Une patrouille te suit? Ma bière a pas de permis, pis toi non plus. [firmly] Sème-les!"),
            # Acte 3 : la fin de e02, en personne ; puis l'appel et l'intro de e09.
            _p("tipaul", "Pas une bosse, pas une caisse de cassée! T'es un vrai chauffeur, toi.", 12, jeu="[impressed] Pas une bosse, pas une caisse de cassée! [happy] T'es un vrai chauffeur, toi."),
            _p("tipaul", "Un mois de stock, grâce à toi. Tiens, pour la peine.", 12, jeu="[warmly] Un mois de stock, grâce à toi. [satisfied] Tiens, pour la peine."),
            # ⚠️ Coupée (2 oct. 2026) : « C'est Ti-Paul, du dépanneur! » — le nom redit (une fois par chapitre), la même voix coupée.
            _p("tipaul", "C'est le barbecue de janvier, pis j'ai besoin d'un chauffeur!", 12, jeu="[cheerful] C'est le barbecue de janvier, pis j'ai besoin d'un chauffeur!"),
            _p("tipaul", "Un barbecue en janvier, l'ami. L'été, tout le monde en fait, ça a pas de mérite.", 12, jeu="[cheerful] Un barbecue en janvier, l'ami. [playfully] L'été, tout le monde en fait, ça a pas de mérite."),
            _p("tipaul", "Les gars de la quincaillerie, du lave-auto pis de Prestige veulent leurs poutines.", 12, jeu="[matter-of-fact] Les gars de la quincaillerie, du lave-auto pis de Prestige veulent leurs poutines."),
            _p("tipaul", "Deux minutes, pas plus. Une poutine froide, dans les Érables, c'est une déclaration de guerre.", 12, jeu="[firmly] Deux minutes, pas plus. [laughs] Une poutine froide, dans les Érables, c'est une déclaration de guerre."),
            _p("tipaul", "Le camion est derrière. Les poutines sont sur le siège, sous la couverte.", 13, jeu="[cheerful] Le camion est derrière. [matter-of-fact] Les poutines sont sur le siège, sous la couverte."),
            _p("tipaul", "Envoye, envoye! Le fromage fait encore squick-squick, profites-en!", 14, jeu="[excited] Envoye, envoye! [laughs] Le fromage fait encore squick-squick, profites-en!"),
            _p("tipaul", "Tout le monde a mangé chaud? Viens-t'en, les saucisses brûlent!", 15, jeu="[cheerful] Tout le monde a mangé chaud? [excited] Viens-t'en, les saucisses brûlent!"),
        ],
        "accueil": [
            _a("bouchard", "Une patrouille? T'en avais deux au cul y a dix minutes. Ça, c'était sa patrouille.", 5, jeu="[deadpan] Une patrouille? T'en avais deux au cul y a dix minutes. [gruffly] Ça, c'était sa patrouille."),
        ],
    },
}
