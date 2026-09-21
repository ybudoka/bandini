"""La police : ce qu'elle voit, ce qu'elle retient, comment elle repond.

Regle de base : **rien n'est compte tant que ce n'est pas detecte**. Trois
canaux : le CONE (un policier voit directement), le TEMOIN (un pieton court
jusqu'a un policier et lui donne ta derniere position connue) et l'ALARME (un
son, dans un rayon, sans cone).
"""

from __future__ import annotations

from typing import TypedDict

TUILE_PX = 16


class Palier(TypedDict):
    etoiles: int
    agents_pied: int
    autos: int
    tirent: bool
    barrages: bool
    helico: bool
    decroissance_s: int


#: Index = nombre d'etoiles. `decroissance_s` : secondes hors de vue avant de
#: perdre UNE etoile.
PALIERS: list[Palier] = [
    {"etoiles": 0, "agents_pied": 0, "autos": 0, "tirent": False, "barrages": False,
     "helico": False, "decroissance_s": 0},
    {"etoiles": 1, "agents_pied": 1, "autos": 0, "tirent": False, "barrages": False,
     "helico": False, "decroissance_s": 15},
    {"etoiles": 2, "agents_pied": 2, "autos": 0, "tirent": False, "barrages": False,
     "helico": False, "decroissance_s": 25},
    {"etoiles": 3, "agents_pied": 2, "autos": 1, "tirent": True, "barrages": False,
     "helico": False, "decroissance_s": 40},
    {"etoiles": 4, "agents_pied": 2, "autos": 2, "tirent": True, "barrages": False,
     "helico": False, "decroissance_s": 60},
    {"etoiles": 5, "agents_pied": 3, "autos": 3, "tirent": True, "barrages": True,
     "helico": True, "decroissance_s": 90},
]

ETOILES_MAX = len(PALIERS) - 1

#: Chaleur ajoutee par point de gravite d'un crime VU ; a 100, une etoile.
CHALEUR_PAR_GRAVITE = 35
CHALEUR_ETOILE = 100

#: Etoiles ajoutees par delit (gravite), et si un temoin est necessaire.
#: `temoin: False` = le delit est BRUYANT : quiconque le percoit suffit, la
#: police le sait tout de suite. `temoin: True` = il faut qu'un agent le voie,
#: ou qu'un passant qui l'a vu aille le raconter (ou telephone) — d'ici la,
#: on peut acheter son silence.
DELITS: dict[str, dict] = {
    "pickpocket": {"etoiles": 1, "temoin": True},
    "vol_vehicule": {"etoiles": 1, "temoin": True},
    "carjacking": {"etoiles": 2, "temoin": False},
    "coup_pieton": {"etoiles": 1, "temoin": True},
    "mort_pieton": {"etoiles": 2, "temoin": True},
    "renversement": {"etoiles": 1, "temoin": True},
    "renversement_mortel": {"etoiles": 2, "temoin": True},
    "arme_sortie": {"etoiles": 1, "temoin": False},
    "coup_policier": {"etoiles": 2, "temoin": False},
    "mort_policier": {"etoiles": 3, "temoin": False},
    "conduite_dangereuse": {"etoiles": 1, "temoin": False},
    "explosion": {"etoiles": 2, "temoin": False},
    "guichet": {"etoiles": 2, "temoin": False},
    # Defoncer une machine distributrice. ⚠️ Pas un guichet : une etoile, et
    # il faut qu'un passant aille le raconter — personne n'appelle la police
    # pour trois canettes, sauf s'il a tout vu.
    "distributrice": {"etoiles": 1, "temoin": True},
    "effraction": {"etoiles": 1, "temoin": True},
    "pot_de_vin_refuse": {"etoiles": 1, "temoin": False},
    # Sortir son char de la fourriere sans passer au comptoir. ⚠️ BRUYANT : les
    # gars du lot sont la pour ca, il n'y a pas de temoin a convaincre. Le
    # nombre d'etoiles est celui de `economie.FOURRIERE["etoiles_vol"]`, et un
    # juge tient les deux d'accord.
    "fourriere": {"etoiles": 1, "temoin": False},
    # Prendre quelqu'un en otage. ⚠️ BRUYANT : un bouclier humain se voit de
    # l'autre bout de la rue, et c'est tout l'interet — inutile de convaincre
    # un temoin de quelque chose que tout le monde regarde.
    "otage": {"etoiles": 2, "temoin": False},
}

#: Cones de vision : demi-angle en degres et portee en tuiles, jour / nuit.
VISION = {
    "policier": {"angle": 45, "jour": 9, "nuit": 6},
    "auto_police": {"angle": 30, "jour": 14, "nuit": 12},
    "pieton": {"angle": 60, "jour": 6, "nuit": 4},
    "helico": {"angle": 180, "jour": 25, "nuit": 20},
    "alarme_rayon": 12,
    "explosion_rayon": 15,
    "delai_reperage_s": 0.6,
    # ⚠️ UN CASIER EPAIS SE VOIT DE LOIN. C'est la premiere ligne de M11 — « le
    # carnet du poste : plus il est epais, plus les agents te reconnaissent de
    # loin » — et c'est la seule facon de faire PESER un casier autrement qu'au
    # comptoir des amendes. Vingt pages ne changent rien a ce qu'on voit du
    # HUD ; elles changent la distance a laquelle on se fait reconnaitre.
    #
    # ⚠️ Et ca ne s'applique qu'au JOUEUR. Un casier epais n'aide pas la police
    # a voir les passants : c'est un signalement, une photo au mur, pas une
    # paire de jumelles.
    #
    # ⚠️ LE PLAFOND EST LA REGLE, pas le detail. A 4 % la page et vingt pages,
    # le cone ferait 1,8 fois sa portee : la police verrait a seize tuiles en
    # pleine nuit, et il n'y aurait plus de ruelle ou souffler. Un casier plein
    # ajoute donc la moitie, jamais plus — et un juge le tient a casier absurde.
    "casier_portee_par_page": 0.04,
    "casier_portee_max": 1.5,
}

TEMOINS = {
    "rayon_tuiles": 9,
    "proba_fuit": 0.6,
    "proba_temoin": 0.3,
    "proba_fige": 0.1,
    "cherche_policier_tuiles": 40,
    "oubli_s": 30,
    "proba_telephone": 0.3,
    "delai_depeche_s": 8,
}

#: ⚠️ LE CRIME D'AUTRUI (M12) : « un crime qu'on n'a pas commis peut te tomber dessus si
#: tu es au mauvais endroit — un témoin qui te confond. C'est risqué, donc c'est RARE et
#: LISIBLE (on voit le vrai coupable), et un juge vérifie qu'aucune étoile ne tombe sur
#: un joueur immobile à plus de N tuiles. »
#:
#: La ville vole, cogne et part avec des chars toute seule (le pickpocket, la rixe, le
#: voleur de char) ; parfois, un passant qui a vu la scène de loin désigne le joueur
#: qui passait TOUT PRÈS. `chance` : la part des crimes vus d'assez près qui trouvent
#: quelqu'un pour te confondre (tirée à l'empreinte, jamais au dé) ; `rayon_px` : jamais
#: au-delà ; `repos_s` : pas deux méprises coup sur coup. La suite est la machine des
#: témoins : il court le dire à un agent, et on peut lui acheter le silence.
AUTRUI = {
    "chance": 0.35,
    "rayon_px": 72,
    "temoin_px": 140,
    "repos_s": 90,
    "cri": "C'EST LUI!",
}

#: LE STOOL — celui qui n'a RIEN VU, et qui te reconnait quand meme.
#:
#: ⚠️ **Ce n'est pas un temoin, et la difference est tout le personnage.** Le
#: temoin a vu un delit : il porte un crime, il court le raconter, et son
#: silence s'achete vingt piastres. Le stool, lui, n'a rien vu — il a reconnu
#: ta FACE, parce que ta face est dans le journal et sur les affiches. Il n'a
#: besoin d'aucun crime, il part telephoner, et ce qu'il donne au poste n'est
#: pas de la chaleur : c'est un SIGNALEMENT, donc un PLANCHER d'etoiles
#: (`etoilesAuMoins`). La difference entre « quelqu'un a vu » et « quelqu'un a
#: appele » etait deja ecrite dans `police.js` ; il lui manquait un corps.
#:
#: ⚠️ **C'est le casier qui le fait naitre**, et c'est ce qui referme M11 :
#: la premiere vague a fait que le dossier allonge le cone des agents, la
#: troisieme fait qu'il transforme les passants en delateurs. Un dossier mince
#: (`casier_minimum`) ne dit rien a personne — on n'est pas encore quelqu'un.
#:
#: ⚠️ **Il ne naît jamais dans le dos d'un joueur immobile** (`devant_degres`,
#: juge de la fiche M11) : il faut qu'on PUISSE le voir se retourner et partir.
#: Une denonciation qu'on ne peut pas voir venir n'est pas une regle, c'est une
#: taxe. Et `repit_s` empeche la rue entiere de se relayer au telephone.
STOOL = {
    "casier_minimum": 3,       # en dessous, personne ne te connait
    "chance_par_page": 0.02,   # par page au dossier, a chaque occasion
    "chance_max": 0.20,
    "occasion_images": 300,    # une occasion toutes les cinq secondes
    "rayon_tuiles": 7,         # d'ou il te reconnait
    "devant_degres": 100,      # ... et il doit etre DEVANT toi
    "etoiles": 2,              # le plancher que son appel pose
    "prix": 300,               # ce que coute son silence
    "prix_par_page": 120,      # ... et il sait ce que tu vaux
    "repit_s": 90,             # apres un appel ou un achat, la rue se tait
    # ⚠️ ET CHANGER DE TETE FAIT PLUS QUE CALMER LA POLICE. Le stool reconnait
    # une FACE ; du linge neuf et une coupe, c'est exactement ce qui la defait
    # — et c'est le seul levier que le joueur ait vraiment contre lui, puisque
    # le casier, lui, ne redescend qu'en payant. Sans ca, un gros dossier
    # n'etait plus une regle : c'etait une taxe qu'on paie jusqu'a la fin de la
    # partie. La friperie et le barbier s'en trouvent doublement utiles.
    "repit_deguisement_s": 240,
    # ⚠️ SES MOTS SONT ICI, ET PAS DANS `pietons.PAROLES`. Cette table-la range
    # ce qu'une SORTE de gens dit — un metier, un corps, une routine. Le stool
    # n'est aucune sorte : c'est un ETAT que n'importe quel passant peut
    # prendre, et c'est precisement ce qui le rend inquietant. Ses deux
    # repliques vivent donc avec la regle qui les produit.
    #
    # ⚠️ Et « reconnait » doit se lire comme une RECONNAISSANCE, pas comme une
    # accusation : c'est ce qui fait froid dans le dos.
    "dit": {"reconnait": "AH BEN, TOÉ...", "achete": "J'AI RIEN VU"},
}

#: LE BOUCLIER HUMAIN — la sortie de secours qui coute cher.
#:
#: ⚠️ **Elle doit rester une SORTIE, jamais un abri.** Un otage qu'on tient
#: indefiniment, c'est l'invincibilite : on traverse la ville derriere un
#: bonhomme et la police regarde. Trois choses l'en empechent, et elles vont
#: ensemble : il SE DEBAT (`debat_s`), il se degage tout seul au bout de
#: `tenue_max_s`, et le compteur MONTE tant qu'on le tient (`chaleur_par_s`).
#: On gagne du temps, on ne gagne pas la partie — et on ressort plus recherche
#: qu'on est entre.
#:
#: ⚠️ **Et la police ne se contente pas de ne plus tirer : elle RECULE**
#: (`police.bouclier_recul_px`). Sans ca, les agents cessaient de tirer et
#: venaient te cueillir a la main — le bouclier ne servait a rien du tout.
#:
#: ⚠️ **Et elle se TIENT** (`saisie_s`) : c'est le seul geste d'ACTION qui
#: demande qu'on insiste, parce que c'est le dernier de la chaine — celui que
#: le bouton faisait quand il n'avait rien trouve d'autre a faire, donc par
#: accident.
BOUCLIER = {
    "portee_px": 26,           # a bout portant, pas a travers la rue
    # ⚠️ ON TIENT LE BOUTON, on ne le tape pas. Remarque de Martin en jouant :
    # une pression suffisait, et le bouclier est LE DERNIER de la chaine
    # d'ACTION — celui que le bouton fait quand il n'a rien trouve d'autre.
    # On visait une porte d'un pas trop loin, une arme par terre, un char, et
    # on se retrouvait avec un bonhomme dans les bras et DEUX ETOILES qu'on
    # n'avait pas demandees. Le geste le plus grave que ce bouton sache faire
    # est maintenant le seul qui demande qu'on insiste.
    #
    # La demi-seconde se juge des deux cotes : plus longue qu'une pression (le
    # coup fort, l'autre bouton qu'on tient, en demande un tiers) et plus
    # courte que la cadence de tir de la police (1,2 s) — une sortie de secours
    # doit s'ouvrir avant la deuxieme balle.
    "saisie_s": 0.5,
    "devant_px": 13,           # ou il se tient : DEVANT toi, entre toi et eux
    "debat_s": 3,              # il commence a se debattre au bout de ce temps
    "tenue_max_s": 12,         # ... et il se degage pour de bon a celui-la
    "chaleur_par_s": 1.2,      # le compteur monte tant qu'on le tient
    "vitesse": 0.75,           # on marche moins vite avec quelqu'un dans les bras
    # ⚠️ Ses mots sont ici pour la meme raison que ceux du stool : ce n'est pas
    # une SORTE de gens, c'est ce qui arrive a n'importe qui.
    "dit": {"pris": "LÂCHE-MOÉ!", "libre": "AU S'COURS!"},
}

#: Changer de vehicule hors de vue pendant ce temps : -1 etoile. Changer de
#: linge : remise a zero jusqu'a `vetements_remise_max`, sinon -2.
DEGUISEMENT = {"vehicule_s": 3, "vehicule_etoiles": 1, "vetements_remise_max": 3,
               "vetements_etoiles": 2}

#: ⚠️ Un passant MARCHE : 0,55 px/image, soit deux tuiles a la seconde. A 0,8
#: il avait l'air de courir tout le temps — remarque de Martin en jouant, et
#: c'est le genre de defaut qu'aucun test ne voit. Quand il fuit (1,5) il
#: reste plus lent que le joueur au sprint (2,1) et que le policier (1,9) :
#: c'est ce qui rend une poursuite gagnable.
#: ⚠️ TROIS vitesses a pied, pas deux — et la course est GRATUITE.
#:
#: Le modele d'avant avait ete regle pour le Faubourg de 157 tuiles ; M8 a
#: quintuple la ville et personne n'y etait revenu. Mesure : un souffle complet
#: valait 4,2 s de course, soit 33 tuiles sur 421 de large ; la vitesse qu'on
#: pouvait TENIR (courir, puis marcher pour souffler) tombait a 1,54 — sous les
#: 1,9 du policier. Autrement dit, la barre ne recompensait rien : elle taxait
#: le deplacement, et fuir a pied ne marchait de toute facon pas.
#:
#:   marche   1,2   rien
#:   course   2,0   RIEN — la vitesse de voyage, de La Pointe aux Quais
#:   sprint   2,6   de l'endurance, par bouffees
#:
#: ⚠️ Et le policier court a la vitesse de la COURSE, pas en dessous. Une
#: course gratuite plus rapide que lui, c'est s'echapper a pied, toujours, sans
#: rien depenser. La regle que le depot s'est deja donnee deux fois — le char
#: rapide, les armes a feu — vaut ici aussi : la vitesse achete de la
#: DISTANCE, jamais l'impunite. On seme la police en cassant la ligne de vue,
#: en montant dans un char, ou en payant du souffle.
VITESSES = {"joueur_marche": 1.2, "joueur_course": 2.0, "joueur_sprint": 2.6,
            "pieton": 0.45, "pieton_course": 1.35,
            "policier": 2.0, "endurance": 100, "endurance_par_image": 0.4}

#: NAGER — et les deux nombres se jugent CONTRE LA GEOGRAPHIE, pas au gout.
#:
#: ⚠️ Le vrai enjeu de l'eau n'est pas la noyade, c'est le PONT. M8 a bati sa
#: geographie sur une regle : une rue dont tous les blocs voisins sont de l'eau
#: est noyee, et le pont fait l'unique exception. Si l'on nage, La Pointe cesse
#: d'etre une ile — a moins que le souffle ne s'en charge. C'est donc lui qui
#: tient la geographie, et il se MESURE :
#:
#:   une tuile d'eau = 16 px / `vitesse` images x `souffle_par_image`
#:                   = 16 / 1,0 x 0,5 = 8 points de souffle
#:
#:   le chenal du pont     11 tuiles =   88 points — un PARI (on a 100)
#:   la baie              124 tuiles =  992 points — impossible, et de loin
#:
#: Avec le cafe (la depense de moitie) et le surplus plein (160), le plafond
#: monte a 40 tuiles : le chenal devient confortable, la baie reste hors de
#: portee par trois fois. Le juge refait ce calcul sur la carte livree — si
#: quelqu'un elargit le chenal ou ralentit la nage, c'est la que ca tombe.
#:
#: ⚠️ Et le pont reste le seul lien CARROSSABLE. Un homme traverse un chenal a
#: la nage, une auto non : c'est plus vrai qu'avant, pas moins.
NAGE = {
    "vitesse": 1.0,            # px par image — plus lent que la marche (1,2)
    "souffle_par_image": 0.5,  # ce que nager coute ; a zero, on coule
    "coule_s": 3.0,            # un char dans l'eau : le temps qu'il s'enfonce
    "cout_chemin_tuiles": 8,   # ce que l'A* paie pour une tuile d'eau
}


#: Enjamber un grillage : ce que ca coute. ⚠️ Le meme prix POUR TOUT LE MONDE —
#: le joueur, un agent, un gardien de fourriere. Si franchir une cloture etait
#: une capacite du joueur seul, la premiere cloture venue deviendrait l'exploit
#: qui gagne toutes les poursuites : on enjambe, les agents restent plantes de
#: l'autre cote. C'est ici, en donnees, pour qu'on ne puisse pas l'oublier d'un
#: cote et pas de l'autre.
#: Les deux chiffres disent la MEME chose : 48 images en haut de la cloture,
#: c'est 3,5 tuiles de marche (1,2 px/image, 16 px la tuile) — d'ou les 5 tuiles
#: que l'A* paie pour traverser, l'exposition en plus.
CLOTURES = {
    "enjambe_images": 48,      # la pose : on ne frappe pas, on ne tire pas, on ne court pas
    "cout_chemin_tuiles": 5,   # ce que l'A* paie pour un grillage
    "hauteur_px": 5,           # de combien le corps se souleve au sommet (dessin)
}


#: FAIRE FACE : pour agir sur quelque chose (une porte, un char, un comptoir,
#: quelqu'un), le joueur doit le REGARDER. ⚠️ « Regarder » veut dire ce que le
#: sprite MONTRE — l'un des quatre regards dessines (`face`) — et pas l'angle
#: fin du stick : ce que le joueur voit est ce que le jeu juge. Quatre regards
#: a +/-50 degres se recouvrent de 10 degres a chaque diagonale : aucune
#: direction n'est hors de portee, et sur une diagonale on peut viser des deux.
#: ⚠️ Et ON N'A PAS A REGARDER CE QU'ON A SOUS LES PIEDS : a `dessus_px` d'un
#: point, la direction n'est plus definie (une arme tombee la ou l'on se tient).
#: Le meme calcul pour l'invite du HUD et pour ACTION — `faceA`, dans base.js —
#: pour que le bouton ne promette jamais ce qu'il refuserait.
REGARD = {
    "demi_cone_degres": 50,   # de part et d'autre du regard dessine
    "dessus_px": 8,           # sous les pieds : pas de regard a exiger
}


#: La police sur le terrain : patrouille, poursuite, arrestation, prison.
POLICE = {
    "patrouille_par_zone_max": 3,   # agents a pied dans la bulle, plafond (la zone dit combien)
    "regarde_toutes_les_images": 3, # un agent teste son cone une image sur trois (budget)
    "arrestation_px": 16,           # au contact : la main au collet
    "poursuite_abandon_s": 12,      # sans te voir pendant ce temps, l'agent retourne patrouiller
    "chemin_toutes_les_images": 30, # l'agent redemande son chemin (A*) a ce rythme
    "auto_vitesse": 0.85,           # fraction de la vitesse max de l'auto-patrouille en poursuite
    "auto_sortent_px": 60,          # si tu es a pied, les agents descendent a cette distance
    "tir_cadence_s": 1.2,           # a 3 etoiles et plus, un agent tire a ce rythme
    "tir_portee_tuiles": 9,
    "affiches_max": 6,              # affiches « Recherche » dans la bulle a partir de 2 etoiles
    "prison_heures": 6,             # le temps que la prison prend, en heures de jeu
    "silence_rayon_px": 30,         # a quelle distance on achete le silence d'un temoin
    # ⚠️ Avec un otage devant toi, l'agent ne tire plus ET N'ARRETE PLUS : il
    # se tient a cette distance. Sans le deuxieme, le bouclier ne servait a
    # rien — ils cessaient de tirer et venaient te cueillir a la main.
    "bouclier_recul_px": 90,
}


def exporter() -> dict:
    return {
        "tuile_px": TUILE_PX,
        "police": dict(POLICE),
        "paliers": PALIERS,
        "etoiles_max": ETOILES_MAX,
        "chaleur_par_gravite": CHALEUR_PAR_GRAVITE,
        "chaleur_etoile": CHALEUR_ETOILE,
        "delits": DELITS,
        "vision": VISION,
        "temoins": TEMOINS,
        "autrui": dict(AUTRUI),
        "stool": dict(STOOL),
        "bouclier": dict(BOUCLIER),
        "deguisement": DEGUISEMENT,
        "vitesses": VITESSES,
        "clotures": CLOTURES,
        "nage": NAGE,
        "regard": dict(REGARD),
    }
