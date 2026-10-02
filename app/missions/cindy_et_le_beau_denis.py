"""Le chapitre de Cindy et du Beau Denis — voir app/missions/__init__.py pour le moteur, et `static/js/chapitres.js`.

⚠️ UN CHAPITRE (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, « les autres arcs », vague Q). Les Morues, avant leur nuit : q05 (Cindy escortée hors de la rue, jusqu'à l'hôtel), q06 (le Beau Denis couché à mains
nues — `calme: morues`) et q12 (la mère de Josée à l'urgence) — deux à quatre étapes, trois ACTES (7 à 8 minutes).
La nuit des Morues (q13, la libération des Quais) reste une mission : elle attend l'un OU l'autre bord du choix de Sven
(`exige.une_de`), et cet `exige` bloquerait Cindy dès le premier acte.

Ce qui a bougé, et pourquoi :
- les répliques d'origine sont gardées mot pour mot (et leurs voix payées, renommées) : l'appel et l'intro de la première
  mission restent ceux du chapitre ; la fin de chacune se dit à l'ouverture de l'acte suivant, suivie de l'appel et
  de l'intro de la suivante ; la fin de la dernière reste la fin du chapitre ; chaque mission garde son échec (`_e`) ;
- QUI PARLE SE NOMME une fois par chapitre : Josée se nomme à l'acte 2 ; son appel de q12 perd « Josée. » — et
  « Viens au bar, vite. » : on y est déjà (q06 finit au bar) — la même voix, coupée au silence ;
- Cindy (`parti_apres: q05`) quitte la ville dès son acte fait (`Histoire.partirApres`) ;
- l'échec `arme` de q06 voyage avec le chapitre : il ne se déclenche que par `sans_arme`, sur ses deux bagarres ;
- la scène d'intro de q05 reste celle du chapitre.
- q13 attend q06 (l'acte 2) : un prérequis peut viser un acte.
"""

from ._commun import _e, _l, _p

MISSION = {
    "slug": "cindy_et_le_beau_denis",
    "titre": "Cindy et le Beau Denis",
    "donneur": "cindy",
    "prerequis": ["q04"],
    "remplace": ["q05", "q06", "q12"],
    "recompense": 300,
    "donne": {"message": "LA MÈRE DE JOSÉE DORT À L'HÔPITAL — JOSÉE TE DOIT UNE FAVEUR"},
    "echec": ["mort", "arrete", "arme"],

    "objectifs": [
        # --- Acte 1 (q05, « Cindy veut sortir »).
        {"type": "acte", "texte": "ACTE 1 — CINDY VEUT SORTIR", "donneur": "cindy"},  # 0
        {"type": "proteger", "texte": "ESCORTE CINDY JUSQU'À L'HÔTEL BANDINI", "cible": "cindy", "lieu": "hotel", "rayon": 5},  # 1
        {"type": "tuer", "texte": "LES GARS DU BEAU DENIS — COUCHE-LES", "groupe": "morues", "n": 2, "ou": "donneur", "loin": 10, "donne": {"message": "CINDY DORT DANS UN VRAI LIT, À L'HÔTEL", "prime": 100}},  # 2
        # --- Acte 2 (q06, « Le Beau Denis »).
        {"type": "acte", "texte": "ACTE 2 — LE BEAU DENIS", "donneur": "josee"},  # 3
        {"type": "tuer", "texte": "SES DEUX GARDES, CHEZ LES MORUES — À MAINS NUES", "groupe": "morues", "n": 2, "ou": "zone:morues", "arme": "", "sans_arme": True},  # 4
        {"type": "tuer", "texte": "LE BEAU DENIS — À MAINS NUES", "groupe": "morues", "n": 1, "chef": True, "ou": "zone:morues", "arme": "", "vie": 180, "sans_arme": True},  # 5
        {"type": "semer", "texte": "LE PORT A TOUT VU — SÈME LA POLICE", "etoiles": 2},  # 6
        {"type": "aller", "texte": "VIENS AU BAR, LA CHEF T'ATTEND", "lieu": "bar", "rayon": 4, "donne": {"calme": "morues", "message": "LES MORUES TE LAISSENT PASSER", "prime": 350}},  # 7
        # --- Acte 3 (q12, « La Chef a un cœur »).
        # La Chef a un cœur (M16, arc Q, 30 sept. 2026). La mère de Josée et de Lulu fait une crise, chez elle, aux Érables ;
        # l'ambulance de l'hôpital est sortie, et Josée ne demande jamais rien à personne. Elle le demande au neveu : prendre
        # l'ambulance à l'hôpital, aller chercher sa mère au dépanneur de Ti-Paul, où Lulu l'a assise, et la mener à
        # l'urgence en deux minutes — sans secousse.
        {"type": "acte", "texte": "ACTE 3 — LA CHEF A UN CŒUR", "donneur": "josee"},  # 8
        {"type": "monter", "texte": "L'AMBULANCE, DEVANT L'HÔPITAL", "vehicule": "ambulance", "ou": "porte:hopital"},  # 9
        {"type": "aller", "texte": "SA MÈRE ATTEND AU DÉPANNEUR, AVEC LULU", "lieu": "depanneur", "rayon": 6},  # 10
        {"type": "livrer", "texte": "À L'URGENCE EN DEUX MINUTES, SANS SECOUSSE", "lieu": "hopital", "rayon": 5, "chrono_s": 120},  # 11
    ],

    # q05 — Le jeu de chaque réplique (`jeu=`) — Cindy : elle blague pour ne pas avoir peur, et la peur passe quand
    # même. Elle rit trop fort à l'appel, se tait sur le trajet, et à l'hôtel elle ne sait plus quoi dire :
    # « merci » ne sort pas, alors elle parle du lit.
    # q06 — Le jeu de chaque réplique (`jeu=`) — Josée : furieuse, et ça ne s'entend qu'au calme. Denis est à elle, et
    # il a envoyé ses gars sur quelqu'un qu'elle protège : c'est ça, l'affront. Elle ne dit pas « tue-le » : elle
    # dit « à mains nues », parce qu'elle veut qu'il se relève et qu'il s'en souvienne. Un seul `[warmly]`, pour
    # Cindy, à la fin.
    # q12 — Le jeu de chaque réplique (`jeu=`) — Josée : pour une fois, la Chef a peur. Elle le cache sous des ordres courts,
    # et la voix se casse une fois, sur « ma mère ». Son `[warmly]` de la mission va au merci, à la fin.
    "dialogue": {
        "appel": [
            _l("cindy", "C'est Cindy, la fille devant la cantine. Josée dit que t'es correct. J'ai besoin de toi, ce soir.", jeu="[nervously] C'est Cindy, la fille devant la cantine. [quietly] Josée dit que t'es correct… J'ai besoin de toi, ce soir."),
        ],
        "intro": [
            _l("cindy", "Norbert, à l'hôtel, cherche une fille pour la réception. Une vraie job, avec une paye pis un lit.", jeu="[warmly] Norbert, à l'hôtel, cherche une fille pour la réception. [softly] Une vraie job… avec une paye pis un lit."),
            _l("cindy", "Denis le sait. Si je marche jusque-là toute seule, j'arrive pas.", jeu="[worried] Denis le sait. [quietly] Si je marche jusque-là toute seule… j'arrive pas."),
            _l("cindy", "Marche à côté de moi. Juste ça. Je m'occupe de pas pleurer.", jeu="[nervously] Marche à côté de moi. Juste ça. [wryly] Je m'occupe de pas pleurer."),
        ],
        "fin": [
            _l("josee", "Le docteur dit qu'elle va s'en remettre. Elle a demandé c'était qui, le chauffeur.", jeu="[relieved] Le docteur dit qu'elle va s'en remettre. [softly] Elle a demandé c'était qui, le chauffeur."),
            _l("josee", "Merci. Je le dirai pas deux fois, alors garde-le.", jeu="[warmly] Merci. [matter-of-fact] Je le dirai pas deux fois, alors garde-le."),
        ],
        "echec": [
            _e("cindy", "C'est correct. Je retourne devant la cantine. J'ai l'habitude.", 0, jeu="[sighs] C'est correct. [bitterly] Je retourne devant la cantine… J'ai l'habitude."),
            _e("josee", "T'as sorti une arme, ou tu t'es fait coucher. Dans les deux cas, Denis rit.", 3, jeu="[coldly] T'as sorti une arme, ou tu t'es fait coucher. [bitterly] Dans les deux cas… Denis rit."),
            _e("josee", "L'ambulance est arrivée trop tard. On en reparlera jamais.", 8, jeu="[coldly] L'ambulance est arrivée trop tard. [quietly] On en reparlera jamais."),
        ],
        "pendant": [
            _p("cindy", "Pas trop vite. Mes talons sont faits pour attendre, pas pour marcher.", 1, jeu="[wryly] Pas trop vite. [nervously] Mes talons sont faits pour attendre… pas pour marcher."),
            _p("cindy", "C'est ses gars! Denis les a envoyés, je te l'avais dit!", 2, jeu="[shouting] C'est ses gars! [worried] Denis les a envoyés, je te l'avais dit!"),
            # Acte 2 : la fin de q05, en personne ; puis l'appel et l'intro de q06.
            _p("cindy", "On est rendus. Je pensais jamais voir cette porte-là de l'autre bord.", 3, jeu="[relieved] On est rendus. [softly] Je pensais jamais voir cette porte-là… de l'autre bord."),
            _p("cindy", "Norbert m'attend à huit heures. Il a dit « mademoiselle ». Personne m'a jamais dit ça.", 3, jeu="[surprised] Norbert m'attend à huit heures. [tenderly] Il a dit « mademoiselle »… Personne m'a jamais dit ça."),
            _p("cindy", "Denis va être en maudit. Dis-le à Josée avant qu'il le dise, lui.", 3, jeu="[worried] Denis va être en maudit. [firmly] Dis-le à Josée… avant qu'il le dise, lui."),
            _p("josee", "Josée. Denis a envoyé ses gars sur une fille que je t'avais confiée. Viens au bar.", 3, jeu="[coldly] Josée. Denis a envoyé ses gars sur une fille que je t'avais confiée. [firmly] Viens au bar."),
            _p("josee", "Denis est à moi depuis dix ans. Il pense que ça lui donne des droits.", 3, jeu="[matter-of-fact] Denis est à moi depuis dix ans. [coldly] Il pense que ça lui donne des droits."),
            _p("josee", "Va le voir chez nous, au port. Pas d'arme. Je veux qu'il se relève, pis qu'il s'en souvienne.", 3, jeu="[menacingly] Va le voir chez nous, au port. [firmly] Pas d'arme. Je veux qu'il se relève… pis qu'il s'en souvienne."),
            _p("josee", "Si t'arrives là un fusil à la main, mes Morues vont penser que c'est la guerre. Ça en est pas une.", 3, jeu="[serious] Si t'arrives là un fusil à la main, mes Morues vont penser que c'est la guerre. [calm] Ça en est pas une."),
            _p("josee", "Ses deux gardes d'abord. Ils sont payés pour recevoir les premiers coups.", 4, jeu="[coldly] Ses deux gardes d'abord. [wryly] Ils sont payés pour recevoir les premiers coups."),
            _p("josee", "Le v'là. Il est beau parce qu'on l'a jamais frappé au visage.", 5, jeu="[knowingly] Le v'là. [menacingly] Il est beau… parce qu'on l'a jamais frappé au visage."),
            _p("josee", "Quelqu'un a appelé la police. Pas un des miens. Disparais.", 6, jeu="[matter-of-fact] Quelqu'un a appelé la police. [coldly] Pas un des miens. Disparais."),
            _p("josee", "Viens au bar. Les Morues ont quelque chose à te dire.", 7, jeu="[calm] Viens au bar. [mysteriously] Les Morues ont quelque chose à te dire."),
            # Acte 3 : la fin de q06, en personne ; puis l'appel et l'intro de q12.
            _p("josee", "Denis s'est relevé. Il boite, pis il a compris. Toute la Morue l'a vu.", 8, jeu="[satisfied] Denis s'est relevé. Il boite, pis il a compris. [coldly] Toute la Morue l'a vu."),
            _p("josee", "Mes gars te laissent passer, astheure. T'as frappé à la loyale, chez eux.", 8, jeu="[matter-of-fact] Mes gars te laissent passer, astheure. [confident] T'as frappé à la loyale, chez eux."),
            _p("josee", "Pis la petite, à l'hôtel. Dis-lui que la Chef paie son premier loyer.", 8, jeu="[warmly] Pis la petite, à l'hôtel. [quietly] Dis-lui que la Chef paie son premier loyer."),
            # ⚠️ Coupée (2 oct. 2026) : « Josée. » — le nom redit (une fois par chapitre) — et « Viens au bar, vite. » : on y est.
            _p("josee", "C'est ma mère.", 8, jeu="[quietly] C'est ma mère."),
            _p("josee", "Elle a fait une crise aux Érables. Lulu l'a assise au dépanneur de Ti-Paul.", 8, jeu="[worried] Elle a fait une crise aux Érables. [matter-of-fact] Lulu l'a assise au dépanneur de Ti-Paul."),
            _p("josee", "L'ambulance est devant l'hôpital, pis leurs gars sont tous sortis. Prends-la.", 8, jeu="[firmly] L'ambulance est devant l'hôpital, pis leurs gars sont tous sortis. Prends-la."),
            _p("josee", "Deux minutes jusqu'à l'urgence. Pis tu la brasses pas. C'est ma mère.", 8, jeu="[serious] Deux minutes jusqu'à l'urgence. Pis tu la brasses pas. [quietly] C'est ma mère."),
            _p("josee", "Les clés sont dedans. J'ai appelé Ginette, elle sait.", 9, jeu="[matter-of-fact] Les clés sont dedans. [calm] J'ai appelé Ginette, elle sait."),
            _p("josee", "Elle est sur le banc devant le dépanneur, avec Lulu. Arrête-toi à côté.", 10, jeu="[worried] Elle est sur le banc devant le dépanneur, avec Lulu. [firmly] Arrête-toi à côté."),
            _p("josee", "Elle respire. Lulu lui tient la main. Roule doux, mais roule.", 11, jeu="[quietly] Elle respire. Lulu lui tient la main. [firmly] Roule doux, mais roule."),
        ],
    },
}
