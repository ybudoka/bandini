"""La mission m98 — voir `app/missions/__init__.py` pour le moteur.

_Le Boss_ (M13), la fin qu'on GAGNE : quatre districts libérés, quatre propriétés, et Josée te donne la
dernière nuit — comme elle t'a donné le Faubourg (m5), puis la ville (m6). Le maire Tanguay envoie tout ce
qu'il a sur le Brouillard ; la ville se bat à tes côtés ; Bouchard rappelle ses chiens ; et le maire, qui dort
dans TON hôtel, cède — avec le billet de Rocco, qu'il avait racheté à Sal : la dette qui ouvrait le jeu finit
déchirée. Puis le générique, et une ville qui a changé de couleur (`donne.boss`).
"""

from .. import economie
from ._commun import _a, _l, _p

#: Les gangs qui se battent pour toi : ceux des quatre districts que tu as libérés, moins les Chevreuils — Jo
#: les a couchés avec toi (e10), ils ne sortent plus pour personne. Les Cravates, eux, sont au maire.
ALLIES = ["morues", "skateux", "boulonneux"]

MISSION = {
    "slug": "m98", "titre": "Le Boss", "donneur": "josee", "prerequis": ["m97"],
    "recompense": 0, "phase": 1, "echec": ["mort", "arrete"],
    # ⚠️ Les deux conditions de M13, qui se GAGNENT en jouant depuis le 29 sept. 2026 : les quatre libérations de
    # M16 (q13, e10, p11, s11 — et le Faubourg de m5 compte) et les quatre propriétés (l'hôtel, en vente après q07).
    "exige": {"liberes": 4, "proprietes": 4},
    # ⚠️ `boss` : la ville change de couleur (`Histoire.reussir`, `partie.boss`). `dette` : le billet ENTIER,
    # plafond compris — il n'en reste rien, qu'on ait payé Sal ou non. `generique` : l'autre fin, puis le BILAN, et
    # la partie continue.
    "donne": {"generique": True, "boss": True, "manchette": "le_boss", "message": "LA VILLE EST À TOI",
              "dette": -round(economie.DETTE["montant"] * economie.DETTE["plafond"])},
    # Le siège du Brouillard, puis la maison du maire — qui est la tienne.
    # ⚠️ 0 : on sort. L'intro se dit DEDANS (Josée), et un `tuer` posé dedans naîtrait devant la porte, pas « de la
    # rue » : l'`aller` d'abord, et les hommes du maire arrivent quand on est dehors (`loin`).
    # ⚠️ 1-2 : `allies` — deux Morues, deux Skateux, deux Boulonneux arrivent en courant de l'autre bout de la rue,
    # visent les Cravates du maire et jamais toi ; ils restent pour la police, puis rentrent chez eux (`avancer`).
    # ⚠️ 2 : `survivre` + `etoiles` — TENIR à cinq étoiles, pas les semer. Se cacher dedans fait tomber les étoiles
    # comme partout ; le chrono, lui, court.
    # ⚠️ 3 : `treve` — Bouchard rappelle ses chiens : les étoiles tombent à zéro quand l'objectif commence.
    # ⚠️ 5 : le maire se tient DEDANS, dans la chambre de l'hôtel (`point:maire`) ; la poignée de main (`accueil`)
    # accomplit la mission, et la fin se joue devant lui.
    "objectifs": [
        {"type": "aller", "lieu": "bar", "rayon": 4, "texte": "SORS DEVANT LE BROUILLARD"},
        {"type": "tuer", "groupe": "cravates", "n": 6, "ou": "bar", "loin": 12, "allies": ALLIES,
         "texte": "LES CRAVATES DU MAIRE — TIENS LE BROUILLARD"},
        {"type": "survivre", "secondes": 90, "etoiles": 5, "allies": ALLIES,
         "texte": "LA POLICE DU MAIRE — TIENS 90 SECONDES"},
        {"type": "aller", "lieu": "hotel", "rayon": 6, "treve": True,
         "texte": "VA À L'HÔTEL BANDINI — LE MAIRE DORT CHEZ TOI"},
        {"type": "tuer", "groupe": "cravates", "pieton": "garde", "n": 4, "ou": "hotel", "loin": 10,
         "texte": "LA GARDE DU MAIRE BLOQUE TA PORTE"},
        {"type": "parler", "cible": "maire", "texte": "MONTE À LA CHAMBRE — LE MAIRE T'ATTEND"},
    ],
    # L'INTRO (dedans, au Brouillard) — Intention : le joueur sait que c'est la dernière nuit, où elle se joue, et
    # que la ville se bat pour lui. On voit : Josée qui croise les bras ; la caméra sort voir la porte du
    # Brouillard (là où ils viendront), puis l'Hôtel Bandini (là où dort le maire) ; elle montre la sortie. On
    # entend : trois répliques, et un silence après « la police de Bouchard ».
    # LA FIN (dedans, dans la chambre de l'hôtel, devant le maire) — Intention : le joueur ressent qu'il a gagné,
    # et que la dette qui ouvrait le jeu se referme. On voit : le maire hausse les épaules, tend le billet ; un
    # silence ; la caméra va chez Josée — et quand elle revient, le maire est parti. On entend : le maire qui
    # perd avec élégance, puis Josée, une seule fois chaleureuse.
    # ⚠️ Chaque coupe en `ensemble`, PUIS sa `dire` : c'est la voix qui retient la scène (`caler une scène sur les
    # voix`). Le maire `entre` pendant que la caméra est chez Josée : on ne le voit pas partir, on voit qu'il
    # n'est plus là (`parti_apres`).
    # LE GÉNÉRIQUE ne connaît que des portes de la ville et le joueur : les quatre quartiers libérés — la cantine
    # des Quais, le dépanneur des Érables, la fourrière de La Shop, le phare de La Pointe —, puis l'Hôtel Bandini,
    # où la caméra reste pendant que les chiffres montent un à un.
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "coupe", "vers": "porte:bar", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 35},
            {"type": "coupe", "vers": "porte:hotel", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [3]},
            {"type": "geste", "acteur": "donneur", "geste": "montrer", "duree": 70},
        ],
        "fin": [
            {"type": "geste", "acteur": "maire", "geste": "hausser", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "geste", "acteur": "maire", "geste": "donner", "duree": 70, "ensemble": True},
            {"type": "dire", "repliques": [2]},
            {"type": "attendre", "duree": 45},
            {"type": "coupe", "vers": "chez:josee", "ferme": 25, "ouvre": 25, "tient": 260, "ensemble": True},
            {"type": "entrer", "acteur": "maire", "dans": "joueur", "duree": 40, "ensemble": True},
            {"type": "dire", "repliques": [3, 4]},
        ],
        "generique": [
            {"type": "coupe", "vers": "joueur", "ferme": 60, "ouvre": 0, "tient": 30},
            {"type": "son", "musique": "generique_boss"},
            {"type": "dire", "ensemble": True},
            {"type": "coupe", "vers": ["porte:cantine", "porte:depanneur", "porte:fourriere", "porte:phare"],
             "ferme": 40, "ouvre": 40, "tient": 220},
            {"type": "coupe", "vers": "porte:hotel", "ferme": 40, "ouvre": 40, "tient": 1180, "ensemble": True},
            {"type": "attendre", "duree": 90},
            {"type": "titre", "texte": "{fortune} $", "sous": "FORTUNE", "monte": 20, "tenu": 100, "descend": 20},
            {"type": "titre", "texte": "{liberes}", "sous": "QUARTIERS À TOI", "monte": 20, "tenu": 100, "descend": 20},
            {"type": "titre", "texte": "{proprietes}", "sous": "PROPRIÉTÉS", "monte": 20, "tenu": 100, "descend": 20},
            {"type": "titre", "texte": "{missions}", "sous": "MISSIONS", "monte": 20, "tenu": 100, "descend": 20},
            {"type": "titre", "texte": "{jours}", "sous": "JOURS À BAIE-DES-BRUMES", "monte": 20, "tenu": 100,
             "descend": 20},
            {"type": "titre", "texte": "DÉCHIRÉE", "sous": "LA DETTE DE ROCCO", "monte": 20, "tenu": 120, "descend": 20},
            {"type": "titre", "logo": True, "sous": "LE BOSS", "monte": 30, "tenu": 200, "descend": 40},
        ],
    },
    # Le jeu de chaque réplique (`jeu=`) — Josée, la dernière nuit : froide, précise, le « on » des chefs ; son
    # `[warmly]` de la mission est le dernier mot du jeu, et il est pour toi. Zed rigole même en courant ;
    # Gros-Boulon parle lent et lourd ; Bouchard a peur et commande pour ne pas le montrer — cette fois, il change
    # de camp ; Norbert vouvoie, et ne dit jamais le nom d'un client, pas même celui du maire. Le maire Tanguay :
    # jovial, lisse, un politicien qui perd avec élégance parce qu'il a toujours perdu avec l'argent des autres — il
    # ne s'excuse pas, il négocie encore.
    "dialogue": {
        "appel": [_l("josee", "Josée. Quatre quartiers, quatre propriétés. Viens au Brouillard, c'est cette nuit.",
                     jeu="[coldly] Josée. Quatre quartiers, quatre propriétés. [mysteriously] Viens au Brouillard… c'est cette nuit.")],
        "intro": [
            _l("josee", "Le maire a compris qui tient la ville. Il reste une chose qu'il sait faire : payer du monde.",
               jeu="[matter-of-fact] Le maire a compris qui tient la ville. [wryly] Il reste une chose qu'il sait faire… payer du monde."),
            _l("josee", "Cette nuit, il envoie ses Cravates sur le Brouillard. Pis la police de Bouchard derrière.",
               jeu="[menacingly] Cette nuit, il envoie ses Cravates sur le Brouillard. [gravely] Pis la police de Bouchard derrière."),
            _l("josee", "Les Morues, les Skateux pis les Boulonneux sont avec toi. Après, on va réveiller le maire.",
               jeu="[confident] Les Morues, les Skateux pis les Boulonneux sont avec toi. [coldly] Après, on va réveiller le maire."),
        ],
        # La fin, dans la chambre : le maire (1, 2), puis Josée chez elle (3, 4).
        "fin": [
            _l("maire", "Trois mandats pour avoir cette ville-là. Toi, t'as pris un mois.",
               jeu="[amused] Trois mandats pour avoir cette ville-là. [impressed] Toi, t'as pris un mois."),
            _l("maire", "Le billet de ton oncle. Je l'avais racheté à Sal, pour te tenir en laisse.",
               jeu="[smugly] Le billet de ton oncle. [knowingly] Je l'avais racheté à Sal… pour te tenir en laisse."),
            _l("josee", "Le maire est sorti par la porte de service. Le Clairon aura sa une demain.",
               jeu="[satisfied] Le maire est sorti par la porte de service. [wryly] Le Clairon aura sa une demain."),
            _l("josee", "Y avait plus grand que le Faubourg. Bienvenue chez toi, Boss.",
               jeu="[quietly] Y avait plus grand que le Faubourg. [warmly] Bienvenue chez toi… Boss."),
        ],
        "echec": [_l("josee", "Le maire a gagné la nuit. Il gagnera pas la prochaine.",
                     jeu="[coldly] Le maire a gagné la nuit. [firmly] Il gagnera pas la prochaine.")],
        "pendant": [
            _p("josee", "Sors. Ils arrivent par la grande rue, les nôtres par l'autre bout.", 0,
               jeu="[firmly] Sors. [matter-of-fact] Ils arrivent par la grande rue… les nôtres par l'autre bout."),
            _p("zed", "Yo, c'est Zed, man! On arrive, pis les Morues courent plus vite que nous autres!", 1,
               jeu="[playfully] Yo, c'est Zed, man! [laughs] On arrive, pis les Morues courent plus vite que nous autres!"),
            _p("boulon", "Gros-Boulon. Mes gars ont barré le boulevard de l'usine. La police va faire le grand tour.", 2,
               jeu="[gruffly] Gros-Boulon. Mes gars ont barré le boulevard de l'usine. [deadpan] La police va faire le grand tour."),
            _p("bouchard", "Salut, le jeune, c'est Bouchard. J'ai rappelé mes gars. Le maire paye plus personne.", 3,
               jeu="[nervously] Salut, le jeune, c'est Bouchard. [gruffly] J'ai rappelé mes gars. Le maire paye plus personne."),
            _p("norbert", "Ici Norbert, de l'Hôtel Bandini. Quatre messieurs bloquent la porte de Monsieur.", 4,
               jeu="[calm] Ici Norbert, de l'Hôtel Bandini. [concerned] Quatre messieurs bloquent la porte de Monsieur."),
            _p("norbert", "La chambre douze, Monsieur. Le client attend en robe de chambre, avec du champagne.", 5,
               jeu="[knowingly] La chambre douze, Monsieur. [wryly] Le client attend en robe de chambre… avec du champagne."),
        ],
        # La poignée de main : le maire se présente — la première fois qu'on l'entend.
        "accueil": [
            _a("maire", "Réal Tanguay, maire de Baie-des-Brumes. Pour encore cinq minutes, j'imagine.", 5,
               jeu="[cheerful] Réal Tanguay, maire de Baie-des-Brumes. [wryly] Pour encore cinq minutes, j'imagine."),
        ],
        # Le narrateur du Clairon referme l'ouverture, dans l'AUTRE sens que m99 : le jeune n'est pas reparti.
        "generique": [
            _l("narrateur", "Il était arrivé par le car de six heures, avec cinquante piastres pis la dette d'un mort.",
               jeu="[softly] Il était arrivé par le car de six heures, avec cinquante piastres… pis la dette d'un mort."),
            _l("narrateur", "Les Quais, les Érables, La Shop, La Pointe. Un quartier à la fois, pis sans demander la permission.",
               jeu="[serious] Les Quais, les Érables, La Shop, La Pointe. [wryly] Un quartier à la fois, pis sans demander la permission."),
            _l("narrateur", "Le billet de Rocco a fini dans le poêle de l'Hôtel Bandini. Quinze mille piastres, en fumée.",
               jeu="[matter-of-fact] Le billet de Rocco a fini dans le poêle de l'Hôtel Bandini. [amused] Quinze mille piastres, en fumée."),
            _l("narrateur", "Le Clairon, le lendemain : le maire démissionne en robe de chambre.",
               jeu="[dramatic] Le Clairon, le lendemain : le maire démissionne… en robe de chambre."),
            _l("narrateur", "La ville se mêle encore de ses affaires. Mais c'est toi qu'elle salue, le Boss.",
               jeu="[wryly] La ville se mêle encore de ses affaires. [warmly] Mais c'est toi qu'elle salue… le Boss."),
        ],
    },
}
