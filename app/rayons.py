"""Des comptoirs qui vendent ce que dit l'enseigne (docs/jalons/des-comptoirs-qui-vendent-ce-que-dit-l-enseigne.md).

Demande de Martin (3 oct. 2026) : « assure-toi qu'on puisse acheter des choses cohérentes dans les commerces qui
vendent des choses ». Jusqu'ici, la COULEUR d'une enseigne décidait seule de son comptoir (`magasins.COMPTOIRS`, un
par famille de devanture) : on lisait « BOULANGERIE » au-dessus d'un pâté chinois, et les restos chinois servaient
de la tarte au sucre. Sur les 177 enseignes de la ville, 53 vendaient ce que leur nom promet.

Ici, le RAYON de chaque enseigne, écrit à la main, nom par nom :

- `RAYONS` : les comptoirs qui disent leur nom (la boulangerie, la boucherie, le BBQ cantonais…). Les articles sont
  ceux de `magasins` (`_art`) ; leurs prix sont dans `economie.TARIFS`, ou ici (`BOUCHEES`) pour ceux que seul un
  rayon vend — jamais dans les deux (un juge le tient).
- `ENSEIGNES` : le rayon de chaque enseigne DÉCIDÉE — un slug de `RAYONS`, ou le comptoir de famille quand il dit
  déjà juste (la taverne sert `nuit`, la poissonnerie `marine`), ou le point qui n'est pas un comptoir (`salon` chez
  le barbier, `journal` au Clairon).
- `EN_ATTENTE` : les enseignes qui vendent encore au comptoir de leur famille, et ce qu'elles vendront — les
  marchandises (vague 2) et les services (vague 3 : Martin, 3 oct. 2026, « un service à lui »). Un juge veut que
  chaque enseigne soit dans l'un OU l'autre : une enseigne neuve sans rayon fait rougir la suite.

⚠️ **RIEN NE BOUGE DANS LA VILLE.** Le rayon ne se pose pas sur la carte : il voyage dans les définitions, rangé par
nom d'enseigne, et le navigateur le lit au comptoir (`Missions.comptoirDuPoint`) — c'est le nom de la porte qui
distingue dix-huit commerces d'une même pièce (`Monde.entrer`). Ni tuile, ni porte, ni dé.

⚠️ Le comptoir de FAMILLE garde ce qui n'est pas la marchandise : les heures (`HEURES_DES_COMPTOIRS`), la saison,
la pièce et son mobilier. Le rayon ne change que ce qu'on achète.
"""

from __future__ import annotations

from . import devantures, economie
from .magasins import _CINEMA, _art

#: Les bouchées que seul un rayon vend : (prix, PV, souffle). ⚠️ Pas dans `economie.TARIFS` : elles voyagent dans
#: la SUITE du paquet avec leurs rayons (`definitions.DANS_LA_SUITE`) — le paquet d'avant l'écran titre était à
#: deux cents octets de son plafond (Martin, 3 oct. 2026 : relever la suite). La règle du trottoir tenue : 4 à 5 au
#: dollar, jamais mieux que le hot-dog (6,5 : `test_rayons`).
BOUCHEES: dict[str, tuple[int, int, int]] = {
    "pain": (4, 10, 10),
    "croissant": (3, 6, 8),
    "eclair": (4, 8, 10),
    "tarte_oeufs": (3, 6, 9),
    "brioche_ananas": (3, 6, 8),
    "brioche_porc": (4, 10, 10),
    "the": (2, 2, 8),
    "tourtiere": (10, 30, 20),
    "saucisses": (8, 22, 16),
    "cretons": (5, 12, 12),
    "pizza": (5, 12, 12),
    "pizza_garnie": (16, 40, 40),
    "egg_roll": (3, 7, 8),
    "chop_suey": (10, 28, 22),
    "riz_frit": (8, 20, 18),
    "dim_sum": (9, 22, 22),
    "canard_laque": (16, 45, 30),
    "porc_bbq": (10, 28, 20),
    "soupe_wonton": (7, 16, 18),
    "nouilles": (9, 24, 20),
    "nouilles_instant": (2, 4, 6),
    "litchis": (3, 5, 9),
    "poulet": (12, 35, 25),
    "frites": (4, 8, 12),
    "moules_frites": (14, 36, 30),
    "lait": (2, 4, 6),
    "lait_chocolat": (2, 3, 7),
    "creme_glacee": (3, 4, 10),
    "fromage_grains": (5, 12, 10),
    "cheddar": (7, 16, 14),
    "pomme": (1, 2, 3),
    "fraises": (4, 8, 10),
    "truffes": (12, 20, 30),
    "vin": (14, 10, 50),
    "steak_frites": (22, 60, 45),
    "soupe_oignon": (8, 20, 18),
}

#: Les mêmes, à plat comme `economie.TARIFS` (`pain`, `pain_pv`, `pain_souffle`) : ce que `_art` pointe.
TARIFS: dict[str, int] = {}
for _slug, (_prix, _pv, _souffle) in BOUCHEES.items():
    TARIFS.update({_slug: _prix, f"{_slug}_pv": _pv, f"{_slug}_souffle": _souffle})


def tarif(cle: str) -> int | None:
    """Le prix ou le gain d'un article de rayon : ici, sinon dans `economie.TARIFS`."""
    return TARIFS.get(cle, economie.TARIFS.get(cle))


def _bouchee(slug: str, nom: str, tarif: str | None = None, *, effet: str | None = None):
    """Un article qui se mange : son prix et ses deux gains sous le même nom dans `economie.TARIFS`."""
    t = tarif or slug
    return _art(slug, nom, t, pv=f"{t}_pv", souffle=f"{t}_souffle", effet=effet)


_CAFE = _bouchee("cafe", "Café", effet="cafe")
_THE = _bouchee("the", "Thé au jasmin")
_LIQUEUR = _bouchee("liqueur", "Liqueur")
_BIERE = _bouchee("biere", "Grosse bière")


def _rayon(nom: str, *articles) -> dict:
    return {"nom": nom, "marge": 1.0, "rabais": 1.0, "articles": list(articles)}


RAYONS: dict[str, dict] = {
    # Le pain du matin, et le beigne pour le café.
    "boulangerie": _rayon("La boulangerie", _bouchee("pain", "Pain de ménage"), _bouchee("croissant", "Croissant"),
                          _bouchee("beigne", "Beigne"), _CAFE),
    "patisserie": _rayon("La pâtisserie", _bouchee("eclair", "Éclair au chocolat"),
                         _bouchee("tarte", "Pointe de tarte au sucre"), _bouchee("croissant", "Croissant"), _THE, _CAFE),
    # La pâtisserie du Petit-Canton : la tartelette aux œufs et la brioche à l'ananas, avec le thé.
    "patisserie_chinoise": _rayon("La pâtisserie", _bouchee("tarte_oeufs", "Tartelette aux œufs"),
                                  _bouchee("brioche_ananas", "Brioche à l'ananas"),
                                  _bouchee("brioche_porc", "Brioche au porc"), _THE),
    "beignerie": _rayon("Le comptoir", _bouchee("beigne", "Beigne"), _bouchee("croissant", "Croissant"),
                        _bouchee("chocolat_chaud", "Chocolat chaud"), _CAFE),
    "boucherie": _rayon("La boucherie", _bouchee("tourtiere", "Pointe de tourtière"),
                        _bouchee("saucisses", "Saucisses maison"), _bouchee("cretons", "Cretons sur toasts")),
    "traiteur": _rayon("Le traiteur", _bouchee("tourtiere", "Pointe de tourtière"),
                       _bouchee("sandwich", "Sandwichs pas de croûte"), _bouchee("pate_chinois", "Pâté chinois"),
                       _bouchee("tarte", "Pointe de tarte au sucre")),
    "pizzeria": _rayon("La pizzeria", _bouchee("pizza", "Pointe de pizza"),
                       _bouchee("pizza_garnie", "Pizza toute garnie"), _LIQUEUR),
    "chinois": _rayon("Le restaurant", _bouchee("egg_roll", "Egg roll"), _bouchee("chop_suey", "Chop suey"),
                      _bouchee("riz_frit", "Riz frit"), _bouchee("soupe_wonton", "Soupe won-ton"), _THE),
    "dim_sum": _rayon("Le dim sum", _bouchee("dim_sum", "Panier de dim sum"),
                      _bouchee("brioche_porc", "Brioche au porc"), _bouchee("tarte_oeufs", "Tartelette aux œufs"), _THE),
    "bbq_cantonais": _rayon("Le BBQ cantonais", _bouchee("canard_laque", "Canard laqué"),
                            _bouchee("porc_bbq", "Porc BBQ sur riz"), _bouchee("riz_frit", "Riz frit"), _THE),
    "nouilles": _rayon("Le comptoir à nouilles", _bouchee("nouilles", "Nouilles sautées"),
                       _bouchee("soupe_wonton", "Soupe won-ton"), _bouchee("egg_roll", "Egg roll"), _THE),
    "rotisserie": _rayon("La rôtisserie", _bouchee("poulet", "Quart de poulet BBQ"), _bouchee("frites", "Frites"),
                         _LIQUEUR),
    "casse_croute": _rayon("Le casse-croûte", _bouchee("hotdog", "Hot-dog steamé"), _bouchee("frites", "Frites"),
                           _bouchee("poutine", "Poutine"), _LIQUEUR),
    "binerie": _rayon("La binerie", _bouchee("feves", "Fèves au lard"), _bouchee("soupe", "Soupe aux pois"),
                      _bouchee("pate_chinois", "Pâté chinois"), _bouchee("tarte", "Pointe de tarte au sucre"), _CAFE),
    "moules": _rayon("Le comptoir", _bouchee("moules_frites", "Moules et frites"), _bouchee("frites", "Frites"),
                     _BIERE),
    "epicerie": _rayon("L'épicerie", _bouchee("pain", "Pain de ménage"), _bouchee("lait", "Pinte de lait"),
                       _bouchee("chips", "Chips"), _bouchee("chocolat", "Barre de chocolat"), _LIQUEUR),
    "epicerie_chinoise": _rayon("L'épicerie", _bouchee("nouilles_instant", "Nouilles instantanées"),
                                _bouchee("litchis", "Litchis"), _bouchee("brioche_porc", "Brioche au porc"), _THE),
    "fruiterie": _rayon("La fruiterie", _bouchee("pomme", "Pomme McIntosh"), _bouchee("fraises", "Casseau de fraises"),
                        _bouchee("litchis", "Litchis"), _bouchee("jus", "Jus d'orange")),
    "laiterie": _rayon("La laiterie", _bouchee("creme_glacee", "Cornet de crème glacée"),
                       _bouchee("lait_chocolat", "Lait au chocolat"), _bouchee("lait", "Pinte de lait"),
                       _bouchee("fromage_grains", "Fromage en grains")),
    "fromagerie": _rayon("La fromagerie", _bouchee("fromage_grains", "Fromage en grains"),
                         _bouchee("cheddar", "Cheddar fort"), _bouchee("pain", "Pain de ménage")),
    "chocolatier": _rayon("Le chocolatier", _bouchee("truffes", "Boîte de truffes"),
                          _bouchee("chocolat_chaud", "Chocolat chaud"), _bouchee("chocolat", "Barre de chocolat")),
    "vins": _rayon("Le comptoir", _bouchee("vin", "Bouteille de vin"), _BIERE, _bouchee("cheddar", "Cheddar fort")),
    "bistro": _rayon("Le bistro", _bouchee("steak_frites", "Steak frites"),
                     _bouchee("soupe_oignon", "Soupe à l'oignon gratinée"), _bouchee("vin", "Bouteille de vin"), _CAFE),
    # Un CINÉMA RIALTO qui n'est pas LE Rialto (la porte qu'`enseignes` a renommée garde son comptoir) : le
    # comptoir à grignotines, sans la séance.
    "cinema": _rayon("Le comptoir du cinéma", *_CINEMA),
}

#: Le rayon de chaque enseigne décidée. ⚠️ Écrit nom par nom : rien n'est déduit du genre.
ENSEIGNES: dict[str, str] = {
    # --- La bouffe (vague 1) : chacune son rayon.
    "BOULANGERIE": "boulangerie",
    "PÂTISSERIE": "patisserie", "SALON DE THÉ": "patisserie",
    "PÂTISSERIE WAH": "patisserie_chinoise", "BOULANGER HUNG": "patisserie_chinoise",
    "THÉ CHEZ YAN": "patisserie_chinoise",
    "BEIGNES CHEZ TI": "beignerie", "CAFÉ DU MATIN": "beignerie",
    "BOUCHERIE PARÉ": "boucherie",
    "TRAITEUR": "traiteur",
    "PIZZERIA NAPOLI": "pizzeria",
    "JARDIN DE JADE": "chinois", "TRAITEUR HO": "chinois",
    "DIM SUM LOTUS": "dim_sum",
    "BBQ CANTONAIS": "bbq_cantonais", "CANARD LAQUÉ": "bbq_cantonais",
    "NOUILLES WONG": "nouilles",
    "RÔTISSERIE": "rotisserie", "POULET BBQ": "rotisserie",
    "CASSE-CROÛTE": "casse_croute", "PATATES FRITES": "casse_croute", "FRITES": "casse_croute",
    "CANTINE": "casse_croute", "CANTINE DU PARC": "casse_croute", "CANTINE MOBILE": "casse_croute",
    "BINERIE": "binerie",
    "MOULES ET FRITES": "moules",
    "ÉPICERIE MARCEL": "epicerie", "ÉPICERIE DU QUAI": "epicerie", "ÉPICERIE": "epicerie",
    "MARCHÉ BEAUDOIN": "epicerie", "MARCHÉ": "epicerie", "SUPERMARCHÉ": "epicerie", "CONSERVERIE": "epicerie",
    "MARCHÉ KAM FUNG": "epicerie_chinoise",
    "FRUITERIE": "fruiterie", "FRUITERIE TAM": "fruiterie",
    "LAITERIE": "laiterie", "CRÉMERIE": "laiterie",
    "FROMAGERIE": "fromagerie",
    "CHOCOLATIER": "chocolatier",
    "BOUTIQUE DE VIN": "vins", "BIÈRE ET VIN": "vins",
    "BISTRO": "bistro",
    "CINÉMA RIALTO": "cinema",
    # Le restaurant d'ici : sandwich, soupe aux pois, pâté chinois, tarte — le comptoir `bouffe` le dit déjà.
    "RESTO": "bouffe",
    # Le dépanneur : sandwich, chips, chocolat, liqueur et le Clairon — le comptoir `commerce` le dit déjà.
    "DÉPANNEUR": "commerce", "DÉPANNEUR 24 H": "commerce",
    "POISSONS LAM": "marine",
    # --- Celles dont le comptoir de famille dit déjà juste.
    "TABAGIE DUBOIS": "commerce", "TABAGIE DU PORT": "commerce", "TABAGIE": "commerce", "5-10-15": "commerce",
    "TOUT À 1 $": "commerce", "MAGASIN": "commerce",
    "BAR LE MATELOT": "nuit", "BRASSERIE": "nuit", "DISCO LE MIRAGE": "nuit", "KARAOKÉ PERLE": "nuit",
    "SALLE DE POOL": "nuit", "TAVERNE CHEZ GO": "nuit", "TAVERNE DU PORT": "nuit", "TAVERNE LA SHOP": "nuit",
    "BAR": "nuit", "TAVERNE": "nuit", "DANCING": "nuit", "SALLE DE BAL": "nuit", "VIDÉO POKER": "nuit",
    "SALLE DE QUILLES": "nuit",
    "POISSONNERIE": "marine", "POISSON FRAIS": "marine", "FRUITS DE MER": "marine", "CABANE À HOMARD": "marine",
    "HOMARD VIVANT": "marine", "CRABE DES NEIGES": "marine", "CREVETTES": "marine", "HUÎTRES ET CIE": "marine",
    "FUMOIR": "marine", "CRIÉE": "marine",
    "PHARMACIE": "sante", "PHARMACIE ROY": "sante", "PHARMACIE TANG": "sante", "HERBORISTE CHAN": "sante",
    "QUINCAILLERIE": "artisan", "OUTILLAGE": "artisan", "LOCATION D'OUTILS": "artisan",
    "FRIPERIE": "mode", "HABITS": "mode",
    # Ce qui n'est pas un comptoir : le fauteuil du barbier, le présentoir du journal.
    "BARBIER GILLES": "salon", "BARBIER WONG": "salon", "BARBIER": "salon", "COIFFURE JENNY": "salon",
    "COIFFURE LINE": "salon", "SALON LOUISE": "salon",
    "LE CLAIRON": "journal", "JOURNAUX YEE": "journal", "KIOSQUE": "journal",
}

#: Les points qui ne sont pas un comptoir d'emplettes (`carte.MOBILIER[genre]["point"]`) : une enseigne décidée
#: vers l'un d'eux garde son point.
POINTS = ("salon", "journal")

#: Les enseignes qui vendent ENCORE au comptoir de leur famille : ce qu'elles vendront, et à quelle vague.
#: ⚠️ Cette table ne doit que rapetisser : chaque vague en sort des lignes vers `ENSEIGNES`.
EN_ATTENTE: dict[str, str] = {
    # --- Vague 2 : les marchandises qui existent déjà (tenues, armes, déco de la planque, options du garage).
    "BIJOUTERIE": "des bijoux à porter", "BIJOUX CHEUNG": "des bijoux à porter",
    "FLEURISTE": "un bouquet", "FLEURISTE MEI": "un bouquet", "FLEURISTE ROSE": "un bouquet",
    "ANIMALERIE": "de quoi nourrir le chat", "RADIO-TV DUMAS": "la déco de la planque",
    "RADIO-TV KWOK": "la déco de la planque", "SPORTS BEAULIEU": "le bâton, le casque",
    "PÊCHE ET CHASSE": "le couteau, la canne", "JOUETS ET TRAINS": "des jouets", "CERFS-VOLANTS": "un cerf-volant",
    "LANTERNES FUNG": "la déco de la planque", "LOCATION VÉLOS": "un vélo", "PLANCHES": "une planche",
    "SOUVENIRS": "des souvenirs", "IMPORT YIP": "des importations", "ENTREPÔT 7": "le gros",
    "PRÊT SUR GAGES": "racheter, revendre", "BRIC-À-BRAC": "du bric-à-brac", "LIQUIDATION": "des fins de série",
    "SURPLUS": "le surplus d'armée", "GROSSISTE": "le gros", "À LOUER": "rien : un local vide",
    "BOTTES DE TRAVAIL": "des bottes", "BOTTES ET CIRES": "des bottes", "CHAUSSURES LÉO": "des chaussures",
    "SALOPETTES": "une salopette", "BOUTIQUE DIANE": "des tenues", "COUTURE CHEZ EVA": "des tenues",
    "TAILLEUR NG": "un habit", "TAILLEUR ROMÉO": "un habit", "TAILLEUR": "un habit", "MERCERIE": "des chapeaux",
    "SOIERIE MEI": "des tenues", "TISSUS ET SOIES": "des tenues", "MODISTE": "des chapeaux",
    "TEXTILE": "des tenues", "MANUFACTURE": "des tenues", "PARFUMERIE": "du parfum",
    "HAUTE COUTURE": "des tenues", "MAROQUINERIE": "une ceinture", "TATOUAGE": "un tatouage",
    "ACIER DU NORD": "des pièces", "ATELIER 12": "les options du garage", "CIRE ET HUILE": "un lavage, une vidange",
    "DÉBOSSELAGE": "réparer le char", "FERRAILLE": "revendre une épave", "LAVE-AUTO": "un lavage",
    "MACHINERIE": "des pièces", "PEINTURE AUTO": "repeindre le char", "PIÈCES D'AUTO": "les options du garage",
    "PIÈCES USAGÉES": "les options du garage", "PNEUS BEAULIEU": "des pneus d'hiver",
    "PNEUS DESCHAMPS": "des pneus d'hiver", "RADIATEURS": "réparer le char", "SABLAGE AU JET": "repeindre le char",
    "SILENCIEUX": "un silencieux", "SOUDURE PELLETIER": "le blindage", "TRANSMISSION": "le moteur gonflé",
    "ÉLECTRIQUE": "des pièces", "SOUDURE": "le blindage", "MOTEURS": "le moteur gonflé", "USINAGE": "des pièces",
    "FONDERIE": "des pièces",
    "ARTISANAT": "de l'artisanat", "BOIS DE SCIAGE": "du bois", "CORDONNERIE": "des bottes",
    "FERBLANTIER": "de la tôle", "FERRONNERIE YU": "du fer forgé", "IMPRIMERIE": "des affiches",
    "MEUBLES GAGNON": "les meubles de la planque", "PALETTES": "des palettes", "PLOMBERIE": "de la plomberie",
    "PÉPINIÈRE": "les plantes de la planque", "SERRURIER": "des clés, un crochet", "TAPISSIER": "les meubles de la planque",
    "VAISSELLE CHOW": "la vaisselle de la planque", "ANTIQUAIRE": "des antiquités", "ENCADREUR": "un cadre",
    "VITRIER": "une vitre", "ATELIER": "des outils", "SCIERIE": "du bois", "MENUISERIE": "du bois",
    "ACCASTILLAGE": "le gréement du bateau", "APPÂTS ET LIGNES": "la canne et les appâts", "APPÂTS": "des appâts",
    "CORDAGES": "des cordages", "GLACE ET SEL": "de la glace", "MOTEURS MARINS": "le moteur du bateau",
    "VOILERIE": "une voile", "CHALOUPES": "une chaloupe", "CHANTIER NAVAL": "réparer le bateau",
    "CALE SÈCHE": "réparer le bateau", "MARINA": "un mouillage",
    "OPTICIEN": "des lunettes fumées", "OPTIQUE": "des lunettes fumées",
    "DISQUES VOGUE": "des disques", "MUSIQUE LAROSE": "un instrument", "LIBRAIRIE": "des livres",
    "LIBRAIRIE CHUNG": "des livres", "LIVRES": "des livres", "PAPETERIE": "de la papeterie",
    "GALERIE D'ART": "un tableau",
    "CLUB VIDÉO": "louer un film",
    # --- Vague 3 : les services (Martin, 3 oct. 2026 : chacun le sien).
    "HÔTEL DES QUAIS": "une chambre pour dormir", "MOTEL LA POINTE": "une chambre pour dormir",
    "CLUB MAH-JONG": "une partie", "SALLE DE JEUX": "une partie", "BINGO": "une carte de bingo",
    "LOCATION CHALOUPE": "louer une chaloupe", "CAPITAINERIE": "les nouvelles du port",
    "DENTISTE": "des soins", "DENTISTE DR LO": "des soins", "CLINIQUE": "des soins", "DOCTEUR": "des soins",
    "POLYCLINIQUE": "des soins", "VÉTÉRINAIRE": "soigner une bête", "ACUPUNCTURE LEE": "des soins",
    "MISSION DU PORT": "une soupe pour qui est cassé", "HOSPICE": "un lit", "SPA": "des soins",
    "ASSOCIATION LI": "un service du quartier", "ASSURANCES": "une assurance", "BANQUE": "le change, un dépôt",
    "CAISSE POP": "le change, un dépôt", "CHÈQUES CASH": "encaisser", "PRÊTS RAPIDES": "un prêt",
    "BUREAU DE PAIE": "la paie", "BUREAU DE POSTE": "envoyer un colis", "BUANDERIE": "laver son linge",
    "BUANDERIE SUN": "laver son linge", "NETTOYEUR": "laver son linge", "DOUANES": "un service des douanes",
    "GARDERIE": "un service du quartier", "NOTAIRE BÉLIVEAU": "un acte", "NOTAIRE LEUNG": "un acte",
    "PHOTO EXPRESS": "un portrait", "PHOTO SOUVENIR": "un portrait", "PHOTOGRAPHE": "un portrait",
    "STUDIO LAU": "un portrait", "TAXI DIAMANT": "une course", "BUREAU": "un service du quartier",
    "DÉPÔT": "un service du quartier", "ENTREPOSAGE": "un casier", "ÉCOLE DE DANSE": "un cours",
    "ÉCOLE": "un cours", "BIBLIOTHÈQUE": "lire", "ARCHIVES": "lire",
}


def noms_des_enseignes() -> dict[str, set[str]]:
    """Chaque nom d'enseigne que la ville peut peindre, et son ou ses genres : les trois catalogues
    (`devantures.COMMERCES`, `COMMERCES_COSSUS`, `COMMERCES_PAUVRES`) et la réserve (`RESERVE`)."""
    g: dict[str, set[str]] = {}
    paires = [p for liste in devantures.COMMERCES.values() for p in liste]
    paires += list(devantures.COMMERCES_COSSUS + devantures.COMMERCES_PAUVRES)
    paires += [(nom, genre) for genre, noms in devantures.RESERVE.items() for nom in noms]
    for nom, genre in paires:
        g.setdefault(nom, set()).add(genre)
    return g


def exporter() -> dict:
    """Ce qui part au navigateur, COMPACT (la suite a un plafond : 6 Ko bruts au lieu de 20) :
    `rayons` — slug : [nom, [[article, nom] ou [article, nom, effet], …]] (le tarif d'un article est son slug, ses
    gains `<slug>_pv` et `<slug>_souffle` : `_bouchee`, et un juge le tient) ; `enseignes` — rayon : [noms] ;
    `tarifs` — les `BOUCHEES`, slug : [prix, PV, souffle]. `Missions.rayons` le déplie une fois."""
    par_rayon: dict[str, list[str]] = {}
    for nom, slug in ENSEIGNES.items():
        par_rayon.setdefault(slug, []).append(nom)
    return {
        "rayons": {slug: [r["nom"], [[a["slug"], a["nom"]] + ([a["effet"]] if a["effet"] else []) for a in r["articles"]]]
                   for slug, r in RAYONS.items()},
        "enseignes": par_rayon,
        "tarifs": {slug: list(t) for slug, t in BOUCHEES.items()},
    }
