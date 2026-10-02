"""Ce que ACTION fait devant le décor, les bêtes et ceux qui travaillent dans la rue (P4).

Dix gestes, et aucun n'est un menu : on regarde la chose (`faceA`, comme pour
tout le reste) et on appuie.

- **s'asseoir** sur un banc : le souffle revient, les forces un peu, la première
  poussée du stick nous relève ;
- **fouiller** une poubelle, une benne, un bac : quelques sous, une canette, un
  reste — ou un rat. Une fois par jour et par bac, et le quartier compte ;
- **boire** à la fontaine de la place ;
- **lire la plaque** d'une statue de parc (28 sept. 2026, `statues.py`) : une ligne
  par pression, et la suivante à la prochaine — ne rapporte rien, comme le chat ;
- **manger au barbecue** (deuxième vague, 22 sept. 2026) — un décor déjà posé
  devant les maisons de banlieue, jamais encore servi : quelques PV et un peu
  de souffle, une fois par jour et par barbecue, toujours sous le hot-dog acheté ;
- **caresser le chat** (deuxième vague, 22 sept. 2026) — une BÊTE, pas un décor
  ni un passant : il laisse approcher qui marche doucement et sans arme
  (`pietons.BETES["chat"]["confiance_px"]`), au lieu de s'envoler à 74 px. Ne
  rapporte rien — c'est le seul geste qui ne rapporte rien ;
- **vider un parcomètre** (deuxième vague, 22 sept. 2026) — déjà posé devant les
  commerces (`mobilier.py`), jamais interactif : de la monnaie, et un DÉLIT
  (`recherche.DELITS`) — un passant qui voit peut aller le raconter ;
- **fouiller le caddie couché**, puis le **redresser** et le **pousser** (deuxième vague,
  2 oct. 2026) : il roule, il heurte, il sert de bélier (`static/js/caddies.js`) ;
- **lire la plaque d'un coin de rue**, et **un panneau drôle** (`panneaux.py`) — une ligne par
  pression, comme la plaque d'une statue ;
- **ouvrir la borne-fontaine** : la gerbe que la ville connaît déjà quand un char
  défonce une borne, mais à la main — on s'y rafraîchit ;
- **un pourboire** à l'artiste de rue : la pièce change vraiment de poche ;
- **la photo du touriste** : il nous tend son appareil, il paie de sa poche.

⚠️ **Python décide, le navigateur joue** : quel décor donne quel geste, ce que
chacun rend, et les mots qu'il dit, sont ici — `static/js/interactions.js` ne
garde aucun nombre. Et **rien ici ne rapporte gros** : le plus gros butin d'un
bac reste sous le dixième de la plus petite prime de mission
(`test_interactions.py`). Ces gestes sont de la ville, pas un métier.
"""

from __future__ import annotations

from . import statues

#: La portée d'un geste sur le décor, en pixels du centre du décor : celle du guichet
#: et de la machine distributrice — une machine et un banc se prennent de la même main.
PORTEE_PX = 22

# --- S'asseoir ------------------------------------------------------------------

ASSEOIR: dict = {
    "invite": "S’ASSEOIR",
    "portee_px": PORTEE_PX,
    # Où le corps se pose, depuis l'ancre du banc (le milieu du bas de la tuile), et
    # de quel côté il regarde. ⚠️ Le banc de face (`banc`) regarde le sud : l'assis
    # est DEVANT le dossier, il se dessine par-dessus. Le banc vu de dos
    # (`banc_nord`) regarde le nord : le dossier est devant l'assis, qui se dessine
    # avant lui (`y` plus petit) pour que la planche lui couvre les jambes. Les deux
    # bancs de profil sont longs (18 px) : l'assis se dessine PAR-DESSUS (`y` plus grand),
    # sinon la planche de l'assise lui coupe le corps en deux.
    "sieges": {
        "banc": {"pose": "assis_bas", "dx": 0, "dy": 2},
        "banc_nord": {"pose": "assis_haut", "dx": 0, "dy": -5},
        "banc_est": {"pose": "assis_droite", "dx": 1, "dy": 1},
        "banc_ouest": {"pose": "assis_gauche", "dx": -1, "dy": 1},
    },
    # DEDANS (`repos.js`, 2 oct. 2026 — Martin : « il faut pouvoir s'asseoir sur les sofas ») : la chaise (`h`) et
    # la berçante (`V`) d'une pièce, depuis le milieu de leur tuile — le corps pose ses pieds au bord de l'assise,
    # comme le patient et l'avocat (`entites.peuplerInterieur`) ; toutes deux ont le dossier au nord. Et le sofa à
    # carreaux de la planque, depuis son ancre : il tourne le dos au mur du bas, face à la télé — l'assis regarde
    # le nord et se dessine AVANT lui, comme au banc vu de dos.
    "dedans": {
        "h": {"pose": "assis_bas", "dx": 0, "dy": 6},
        "V": {"pose": "assis_bas", "dx": 0, "dy": 6},
        "sofa": {"pose": "assis_haut", "dx": 0, "dy": -5},
    },
    # ⚠️ Le souffle remonte plus vite assis : deux fois et demie la reprise
    # debout (`endurance_par_image * 0,6` — c'est le facteur de plus, pas le taux).
    "souffle_x": 2.5,
    # Les forces reviennent lentement (une PV toutes les trois secondes), et pas
    # au-delà des trois cinquièmes de la barre : un banc repose, il ne soigne pas —
    # la bouffe et l'hôpital gardent leur raison d'être.
    "pv_images": 180,
    "pv_plafond": 0.6,
    # Ce qui nous empêche de nous asseoir, et ce que l'invite en dit.
    "refus": {
        "police": "PAS AVEC LA POLICE AUX FESSES",
        "saigne": "TU SAIGNES ENCORE",
    },
}

# --- Fouiller -------------------------------------------------------------------

#: Les trouvailles. `argent` = (min, max) ; `pv` et `souffle` se prennent ; un `pv`
#: négatif est une morsure, et elle ne tue jamais (il reste toujours un point).
TROUVAILLES: dict[str, dict] = {
    "rien": {"texte": "RIEN QUE DES ORDURES"},
    "monnaie": {"texte": "DE LA MONNAIE", "argent": (1, 3)},
    "canettes": {"texte": "DES CANETTES CONSIGNÉES", "argent": (2, 4)},
    "reste": {"texte": "UN RESTE DE POUTINE", "pv": 4, "souffle": 6},
    "rat": {"texte": "UN RAT !", "pv": -3},
    # La nuit, c'est lui qui est dans la poubelle (voir `FOUILLER["la_nuit"]`).
    "raton": {"texte": "UN RATON LAVEUR !", "pv": -4},
}

FOUILLER: dict = {
    "invite": "FOUILLER",
    "deja": "DÉJÀ FOUILLÉ",
    "portee_px": PORTEE_PX,
    # Quel décor se fouille, et quelle table il tire. ⚠️ `poubelle_pleine` et les
    # ordures sont ce que le quartier pauvre laisse traîner (`salete.py`) : c'est
    # là qu'il y a quelque chose.
    "decors": {
        "poubelle": "ordinaire",
        "bac": "ordinaire",
        "poubelle_pleine": "pleine",
        "ordures": "pleine",
        "benne": "pleine",
        "bac_recyclage": "recyclage",
    },
    # (poids, trouvaille). Le tirage est UN `B.rng()`, ordonné comme écrit.
    "tables": {
        "ordinaire": ((50, "rien"), (26, "monnaie"), (10, "canettes"), (7, "reste"), (7, "rat")),
        "pleine": ((30, "rien"), (30, "monnaie"), (16, "canettes"), (12, "reste"), (12, "rat")),
        "recyclage": ((35, "rien"), (10, "monnaie"), (55, "canettes")),
    },
    # ⚠️ Le quartier dit la poubelle : ce facteur multiplie le poids de « rien ». Un
    # bac de quartier cossu est presque toujours vide, celui d'un quartier pauvre
    # déborde (`Monde.standingA`). Sans standing (une ruelle hors quartier) : 1.
    "standing": {"cossu": 3.0, "ordinaire": 1.0, "pauvre": 0.6},
    # ⚠️ LA NUIT A SES HABITUDES : la nuit, le rat de la table est un RATON LAVEUR,
    # et il y en a plus (son poids fois `poids`). Le tirage reste UN `B.rng()` : la
    # nuit ne tire pas un de de plus, elle change ce qu'il rend. Et le raton se
    # sauve de la poubelle — on le voit filer (`Entites.fairePartirUnRaton`).
    "la_nuit": {"remplace": "rat", "par": "raton", "poids": 2.0},
    "trouvailles": {slug: dict(t) for slug, t in TROUVAILLES.items()},
}

# --- Boire ----------------------------------------------------------------------

BOIRE: dict = {
    "invite": "BOIRE",
    "encore": "PLUS SOIF",
    "message": "L’EAU EST FRAÎCHE",
    "decors": ("fontaine",),
    # Une fontaine de place est plus grosse qu'un banc : on la touche de plus loin.
    "portee_px": 28,
    "souffle": 40,
    # On ne rebuvait pas dix fois de suite : dix secondes avant d'avoir soif.
    "repit_images": 600,
    # ⚠️ L'hiver, la Ville coupe l'eau (docs/jalons/la-foire-fermee-l-hiver.md, vague 2) : ACTION le dit.
    "hiver": "À SEC POUR L’HIVER",
}

# --- Lire la plaque d'une statue -------------------------------------------------

#: ⚠️ **UNE LIGNE PAR PRESSION** : le toast du HUD tient une ligne (`Hud.message`), et une plaque en
#: a quatre. La première pression lit la première, la suivante la suite, et on recommence au bout —
#: comme on lit une plaque de bronze, en se penchant. Les mots sont dans `statues.MODELES`.
LIRE: dict = {
    "invite": "LIRE LA PLAQUE",
    "decors": statues.TYPES,
    # Le socle est large : on lit de devant, pas le nez sur le granit.
    "portee_px": 26,
    # Une ligne reste à l'écran le temps de la LIRE, pas de la voir passer : sept secondes (Martin,
    # 29 sept. 2026 : « affiche plus longtemps les textes » — 200 images, 3,3 s, filaient trop vite). La
    # pression suivante la remplace aussitôt : on n'attend jamais la fin pour lire la suite.
    "duree_images": 420,
    "plaques": statues.exporter(),
}

# --- Manger au barbecue -----------------------------------------------------------

#: ⚠️ **AUCUNE PLACE NEUVE À TROUVER** (deuxième vague, 22 sept. 2026) : `bbq` est déjà
#: posé par `carte.py` (devant les maisons de banlieue, `DECOR_SOLIDE`) — c'est pour ça
#: qu'il ouvre la vague, avant le chat (une confiance à écrire) et le buisson (la police
#: à équilibrer). Un reste de poutine ramassé dans une poubelle vaut 4 PV/6 de souffle
#: (`FOUILLER`) ; un repas assis au barbecue en vaut un peu plus — jamais dix, jamais le
#: hot-dog du kiosque (25 PV/40 de souffle, `economie.TARIFS`) : on grignote, on n'achète
#: rien.
BARBECUE: dict = {
    "invite": "MANGER",
    "deja": "DÉJÀ MANGÉ",
    "message": "ÇA SENT BON",
    "decors": ("bbq",),
    "portee_px": PORTEE_PX,
    "pv": 8,
    "souffle": 15,
    # ⚠️ L'hiver, il dort sous sa housse (docs/jalons/la-foire-fermee-l-hiver.md, vague 2).
    "hiver": "SOUS SA HOUSSE POUR L’HIVER",
}

# --- Vider un parcomètre -----------------------------------------------------------

#: ⚠️ **AUCUNE PLACE NEUVE NON PLUS** (deuxième vague, 22 sept. 2026) : `parcometre` est déjà
#: posé (`mobilier.MEUBLES_PAR_USAGE["commercial"]`, devant les commerces), juste jamais
#: interactif — contrairement au buisson (annulé, § plus bas), rien ici ne touche
#: `Police.voit`. ⚠️ **C'est un DÉLIT** (`recherche.DELITS["parcometre"]`, le même gabarit
#: qu'une distributrice défoncée) : un passant qui voit ACTION le forcer peut aller le
#: raconter à un agent.
PARCOMETRE: dict = {
    "invite": "FORCER LE PARCOMÈTRE",
    "deja": "DÉJÀ VIDÉ",
    "message": "LA MONNAIE TOMBE",
    "decors": ("parcometre",),
    "portee_px": PORTEE_PX,
    # Plus qu'une poubelle (au pire 4 $, `FOUILLER["trouvailles"]["canettes"]`) — une journée
    # de quartiers qui paient pour se garer — mais loin d'une distributrice défoncée (4-22 $) :
    # c'est de la monnaie, pas un coffre. ⚠️ 8 $ au plus (9 jusqu'au 1er oct. 2026) : au dixième de la plus petite
    # prime d'une mission (`test_interactions`), et e03 paie 80 $ — Mme Beaulieu le dit à voix haute.
    "argent": (4, 8),
}

# --- Caresser le chat -------------------------------------------------------------

#: ⚠️ **AUCUN NOMBRE, ET C'EST VOULU** (deuxième vague, 22 sept. 2026) : pas de PV,
#: pas de souffle, pas d'argent — on ne caresse pas un chat pour en tirer quelque
#: chose, c'est le seul des sept gestes qui ne rapporte RIEN. Ce qui le rend
#: possible vit dans `pietons.BETES["chat"]["confiance_px"]` (marcher doucement,
#: sans arme, laisse approcher) et `Entites.majBete` (JS) : ici, seulement
#: l'invite et le mot dit.
CARESSER: dict = {
    "invite": "CARESSER",
    "espece": "chat",
    "portee_px": PORTEE_PX,
    "mots": ("RONRON", "MIAOU", "IL SE FROTTE CONTRE TOI"),
}

# --- La borne-fontaine -----------------------------------------------------------

BORNE: dict = {
    "invite_ouvrir": "OUVRIR LA BORNE",
    "invite_fermer": "FERMER LA BORNE",
    # Une borne que les enfants du quartier ont ouverte pour la canicule (les saisons, vague 4c) : on la
    # laisse couler.
    "enfants": "LES ENFANTS JOUENT : ON LA LAISSE COULER",
    "decors": ("borne_fontaine",),
    "portee_px": PORTEE_PX,
    # ⚠️ La même gerbe que celle d'une borne défoncée (`Entites.JET_EAU_IMAGES`, dix
    # secondes), mais on la ferme : vingt secondes, et elle se referme seule.
    "duree_images": 1200,
    # Se rafraîchir : à ce rayon de la gerbe, le souffle revient plus vite qu'à
    # l'ordinaire — le facteur de plus, comme pour le banc.
    "rayon_px": 34,
    "souffle_x": 2.0,
}

# --- Le pourboire ---------------------------------------------------------------

POURBOIRE: dict = {
    "invite": "UN POURBOIRE",
    "montant": 1,
    "metiers": ("musicien", "amuseur", "jongleur", "echassier"),
    "portee_px": 26,
    # Ce que l'artiste répond. ⚠️ Le musicien a déjà son mot (`pietons.PAROLES`,
    # « chapeau ») : on ne le redit pas, on le reprend ici avec ceux des autres.
    "merci": {
        "musicien": ("MERCI M’SIEUR-DAME", "ÇA VA À LA GUITARE"),
        "amuseur": ("HA! MERCI, PATRON", "T’ES UN VRAI"),
        "jongleur": ("ET HOP! MERCI", "UNE DE PLUS!"),
        "echassier": ("MERCI D’EN BAS!", "ÇA MONTE AU CHAPEAU"),
    },
}

# --- La photo du touriste --------------------------------------------------------

PHOTO: dict = {
    "invite": "PRENDRE SA PHOTO",
    "metier": "touriste",
    "portee_px": 26,
    "pose_images": 100,
    # Il paie de SA poche (`argent` du passant), pas d'un puits sans fond.
    "pourboire": (2, 5),
    "merci": ("THANK YOU!", "VERY NICE!", "MERCI BEAUCOUP!", "SO NICE, BAIE-DES-BRUMES!"),
}


#: ARRACHER UNE AFFICHE « Recherché » (2e vague du décor, 26 sept. 2026). La police en colle a partir
#: de deux etoiles (`police.majAffiches`) ; ta face est dessus, et c'est pour ca que le STOOL te
#: reconnait (`recherche.STOOL`). En arracher une :
#:   - la police en recolle UNE DE MOINS jusqu'a la fin de la poursuite (`affiches_max` moins les
#:     arrachees) — sans ce plafond, elle les reposait sans fin et le geste ne valait rien ;
#:   - et la rue t'oublie un moment : le prochain stool attend `repit_stool_s` de plus.
#: ⚠️ Ce n'est pas un delit — mais c'est un geste qu'on fait EN FUITE, sous les yeux de la rue.
AFFICHE: dict = {
    "invite": "ARRACHER L'AFFICHE",
    "portee_px": 22,
    "repit_stool_s": 60,
    "dit": "UNE FACE DE MOINS SUR LES MURS",
}

#: ATTENDRE, assis (`repos.js`, vague 2 — Martin, 2 oct. 2026 : « s'asseoir doit aussi permettre d'attendre
#: quelques heures », et « accéléré sous tes yeux »). Assis, ACTION ouvre ATTENDRE 1 H · 2 H · 3 H · SE LEVER.
#:
#: Le temps FILE, il ne saute pas : la ville fait `vitesse` pas de simulation par image (les passants, les chars,
#: la police, tout ce qui compte en images), plafonnés à `budget_ms` par image pour ne pas geler un téléphone ; et
#: l'horloge avance d'une heure en `secondes_par_heure` secondes réelles (une heure de jeu en vaut 20 debout). Un
#: appareil trop lent pour ses `vitesse` pas attend un peu plus longtemps — l'horloge suit les pas, pas la montre.
#:
#: ⚠️ On n'attend pas ce qui COMPTE le temps : un défi, une frénésie, un boulot, un objectif à chrono (ils
#: compteraient au quadruple), ni la police aux fesses. Et l'attente cesse au stick, à un coup, à une étoile.
ATTENDRE: dict = {
    "invite": "ATTENDRE",
    # Le bandeau pendant l'attente, et l'heure qu'il est (« ATTENTE — 18:23 ») : un état, pas un ordre.
    "bandeau": "ATTENTE",
    "heures": [1, 2, 3],
    "secondes_par_heure": 2,
    "vitesse": 4,
    "budget_ms": 8,
    "refus": {
        "defi": "PAS EN PLEIN DÉFI",
        "boulot": "PAS EN PLEIN BOULOT",
        "chrono": "LE CHRONO TOURNE",
    },
}


# --- Le caddie ---------------------------------------------------------------------

#: LE CADDIE COUCHÉ de la ville (deuxième vague, tranché par Martin le 2 oct. 2026) : il se FOUILLE
#: d'abord, puis il se REDRESSE et se POUSSE à pied (`static/js/caddies.js`).
#:
#: ⚠️ **CE QU'ON Y TROUVE NE CASSE PAS LES COLLECTIONS** : de la monnaie, une canette consignée (les
#: trouvailles des bacs, `TROUVAILLES`), ou un objet drôle qu'on laisse là — jamais une carte de
#: hockey ni une bebelle, qui ont leurs places à elles (`collectionner.py`). Une fois par jour et par
#: caddie, comme un bac ; l'objet drôle se choisit à l'empreinte du caddie et du jour, sans un dé de plus.
#:
#: ⚠️ **IL ROULE, IL HEURTE, IL SERT DE BÉLIER** : poussé, il prend la vitesse de qui le pousse
#: (`pousse_x` de plus, il part devant) et roule ensuite sur sa lancée (`frottement` par image). LANCÉ AU
#: SPRINT (ESQUIVE tenue, pas la course de tous les jours), et tant qu'il garde `belier` de vitesse, il
#: bouscule le passant qu'il touche (un pas de côté et un mot, jamais un coup : ni PV, ni délit) et cogne
#: le char (`degats_char`, et l'alarme d'un char garé qui en a une) ; sinon, il s'arrête contre lui. ⚠️ Le
#: sprint, pas une vitesse : l'hiver, sans bottes, un sprint dans la neige (2,6 × 0,8) va moins vite que la
#: course de l'été — `belier` reste sous lui. Un mur le renvoie (`rebond`). Il reste là où on le laisse, et
#: la partie s'en souvient (`partie.caddies`).
CADDIE: dict = {
    "invite_fouiller": "FOUILLER LE CADDIE",
    "invite_redresser": "REDRESSER LE CADDIE",
    "redresse": "IL TIENT SUR SES ROUES — POUSSE-LE",
    "decors": ("caddie",),
    "debout": "caddie_debout",
    "portee_px": PORTEE_PX,
    # (poids, trouvaille) : UN `B.rng()`, ordonné comme écrit. `drole` : un des objets ci-dessous.
    "table": ((30, "monnaie"), (15, "canettes"), (55, "drole")),
    "droles": (
        "UN SOULIER DÉPAREILLÉ. LE GAUCHE.",
        "UN CIRCULAIRE DE 1994. LE BEURRE EST EN SPÉCIAL.",
        "UNE COUPE STANLEY EN PLASTIQUE",
        "UNE LISTE D’ÉPICERIE : « DU PAIN. »",
        "UN BAS DE LAINE. JUSTE UN.",
        "UN PIGEON. IL ÉTAIT LÀ AVANT TOI.",
    ),
    "pousse_x": 1.1,
    "frottement": 0.975,
    "vitesse_max": 3.2,
    "belier": 1.6,
    "rebond": 0.3,
    "degats_char": 3,
    "bouscule": ("R’GARDE OÙ TU POUSSES!", "C’EST PAS UN CHAR!", "AYOYE, MES ORTEILS!"),
}

# --- La plaque de rue et le panneau drôle ---------------------------------------------

#: LA PLAQUE DE RUE (tranché par Martin le 2 oct. 2026) : la plaque bleue d'un coin, sur le poteau du
#: panneau d'arrêt ou sur le mât d'un feu (un par croisement, `Vehicules.creerSignalisation`) ; ACTION
#: dessous dit le coin. Le nom se lit sur la trame (`static/js/panneaux.js`, la même règle que
#: `autobus.nom_de_coin` — un juge les compare) : rien de neuf dans la carte.
PLAQUE: dict = {
    "invite": "LIRE LA PLAQUE",
    "portee_px": PORTEE_PX,
    "duree_images": 420,
    # Le coin, et le quartier où il est. ⚠️ Les ordinaux comme sur une plaque du Québec (`autobus.ordinal`) :
    # « 1re », puis « 2e », « 3e »… Les rues de la bande nord se comptent depuis la couture, vers le nord.
    "coin": "COIN {rue} ET {avenue} — {quartier}",
    "rue": "{n} RUE",
    "rue_nord": "{n} RUE NORD",
    "avenue": "{n} AVENUE",
}

#: LE PANNEAU DRÔLE (`panneaux.py`, qui voyage dans la suite) : une ligne par pression, comme une plaque.
PANNEAU: dict = {
    "invite": "LIRE LE PANNEAU",
    "portee_px": PORTEE_PX,
    "duree_images": 420,
}


def exporter() -> dict:
    """Le catalogue tel que le navigateur le tient : des listes, jamais des tuples."""
    return {
        "affiche": dict(AFFICHE),
        "attendre": {**ATTENDRE, "heures": list(ATTENDRE["heures"]), "refus": dict(ATTENDRE["refus"])},
        "asseoir": {**ASSEOIR, "sieges": {k: dict(v) for k, v in ASSEOIR["sieges"].items()},
                    "dedans": {k: dict(v) for k, v in ASSEOIR["dedans"].items()},
                    "refus": dict(ASSEOIR["refus"])},
        "fouiller": {**FOUILLER, "decors": dict(FOUILLER["decors"]),
                     "tables": {t: [list(e) for e in table] for t, table in FOUILLER["tables"].items()},
                     "standing": dict(FOUILLER["standing"]),
                     "trouvailles": {s: {k: (list(v) if isinstance(v, tuple) else v) for k, v in t.items()}
                                     for s, t in FOUILLER["trouvailles"].items()}},
        "boire": {**BOIRE, "decors": list(BOIRE["decors"])},
        "lire": {**LIRE, "decors": list(LIRE["decors"]), "plaques": dict(LIRE["plaques"])},
        "barbecue": {**BARBECUE, "decors": list(BARBECUE["decors"])},
        "parcometre": {**PARCOMETRE, "decors": list(PARCOMETRE["decors"]), "argent": list(PARCOMETRE["argent"])},
        "caresser": {**CARESSER, "mots": list(CARESSER["mots"])},
        "borne": {**BORNE, "decors": list(BORNE["decors"])},
        "pourboire": {**POURBOIRE, "metiers": list(POURBOIRE["metiers"]),
                      "merci": {m: list(mots) for m, mots in POURBOIRE["merci"].items()}},
        "photo": {**PHOTO, "pourboire": list(PHOTO["pourboire"]), "merci": list(PHOTO["merci"])},
        "caddie": {**CADDIE, "decors": list(CADDIE["decors"]), "table": [list(e) for e in CADDIE["table"]],
                   "droles": list(CADDIE["droles"]), "bouscule": list(CADDIE["bouscule"])},
        "plaque": dict(PLAQUE),
        "panneau": dict(PANNEAU),
    }
