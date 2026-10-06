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

from . import armes, decoration, devantures, economie, garage
from .magasins import _CINEMA, TENUES, _art

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


def _tenue(slug: str):
    """Une tenue du catalogue de Rosa (`magasins.TENUES`), sous SON nom : le menu l'affiche ainsi (`itemTenue`)."""
    t = next(t for t in TENUES if t["slug"] == slug)
    return _art(slug, t["nom"], tenue=slug)


def _arme(slug: str):
    """Une arme du catalogue de Chez Gus, sous son nom : son prix est le sien, fois la `marge` du rayon."""
    return _art(slug, armes.par_slug(slug)["nom"], arme=slug)


def _piece(slug: str):
    """Une pièce de Ti-Guy (`garage.PIECES`), posée sur le char garé devant la porte : son prix fois la `marge`."""
    q = next(q for q in garage.PIECES if q["slug"] == slug)
    return {**_art(slug, q["nom"]), "piece": slug}


def _meuble(slug: str):
    """Un meuble du catalogue Beausoleil (`decoration.MEUBLES`), livré le lendemain à la planque de Rocco, comme
    chez Gisèle aux puces : son prix fois la `marge` du rayon."""
    m = next(m for m in decoration.MEUBLES if m["slug"] == slug)
    return {**_art(slug, m["nom"]), "meuble": slug}


#: Les SERVICES : ce qu'un comptoir FAIT plutôt que vendre (`Missions.itemsDuService`). `nom` : la ligne du menu
#: (un service qui en fait plusieurs, comme le coffre, n'en a pas) ; `prix` : son prix de base, fois la `marge` du
#: rayon (None : il le calcule — la réparation au PV, l'assurance à la valeur du char) ; `char` : il travaille sur le
#: char garé devant la porte (`Missions.charDevant`), comme Ti-Guy (`menuGarage`).
#:
#: ⚠️ Vague 3 (Martin, 6 oct. 2026 : « un service à lui ») : chacun réutilise une mécanique qui existe — le lit de la
#: planque, `soigner`, la police qui lâche une étoile, le coffre, l'assurance et la vente de Ti-Guy, la dette de Sal,
#: le film du Rialto, les tables du Dragon d'or. Aucun n'a d'état à lui.
SERVICES: dict[str, dict] = {
    # Les commerces de l'auto (vague 2b, 3a).
    "reparer": {"nom": "Réparer le char", "prix": None, "char": True},
    "repeindre": {"nom": "Repeindre (efface le vol)", "prix": economie.REPEINTE, "char": True},
    "assurer": {"nom": "Assurer le char", "prix": None, "char": True},
    # Le lavage du lave-auto (`enseignes.REGLES`), au comptoir : le char repart propre, la police le cherche un peu moins.
    "laver": {"nom": "Laver le char (une étoile de moins)", "prix": 12, "char": True},
    # La ferraille rachète TOUT ce qui roule encore ou plus, épave comprise, au prix de la tôle.
    "epave": {"nom": "Vendre le char à la ferraille", "prix": None, "char": True},
    # L'hôtel : le lit de la planque, payé — dormir jusqu'au matin (la partie se sauve), ou jusqu'au soir.
    # ⚠️ Les libellés du lit de la planque : ce sont deux départs, et le menu se referme (`test_un_comptoir_reste_ouvert`).
    "nuit": {"nom": "Dormir jusqu’au matin", "prix": 40},
    "sieste": {"nom": "Dormir jusqu’au soir", "prix": 20},
    # Les soins, au PV manquant : un peu plus cher que les pilules (0,40 $ le PV), mais jusqu'au bout.
    "soins": {"nom": "Te faire soigner", "prix": None},
    # Le linge lavé : celui qu'on cherchait n'a plus de taches — une étoile de moins, comme le lave-auto.
    "linge": {"nom": "Laver ton linge (une étoile de moins)", "prix": 15},
    # Le coffre de la planque, au guichet : ce qui y est ne part pas en prison (`Missions.menuCoffre`).
    "coffre": {"nom": None, "prix": None},
    # La dette de Rocco : les versements se font aussi au comptoir des prêteurs (`Missions.menuDette`).
    "dette": {"nom": None, "prix": None},
    # Le prêt sur gages rachète tes armes, à 40 % du prix de Chez Gus.
    "gages": {"nom": None, "prix": None},
    # Une cassette au club vidéo : le film du Rialto, regardé dans l'arrière-boutique (deux heures, `repos_pv`).
    "film": {"nom": "Louer un film", "prix": 4},
    # Une table du Dragon d'or, ailleurs : le sic bo au club de mah-jong, la machine à sous à la salle de jeux. Leurs
    # limites du jour sont celles du casino (`Tables`, `Casino`).
    "sic_bo": {"nom": "La table de sic bo", "prix": None},
    "machine": {"nom": "La machine à sous", "prix": None},
}

#: La part du prix de Chez Gus que le prêteur sur gages donne pour une arme.
GAGES = 0.4
#: La part de `VENTE_FRACTION` que la ferraille donne pour un char, quel que soit son état.
FERRAILLE = 0.5
#: Le prix d'un PV aux soins (fois la `marge` : le spa coûte plus cher que la clinique).
SOINS_PV = 0.5


def _service(slug: str):
    return {**_art(slug, SERVICES[slug]["nom"] or slug), "service": slug}


def _rayon(nom: str, *articles, marge: float = 1.0, rabais: float = 1.0) -> dict:
    """`marge` : ce que le rayon prend en plus sur une arme (le quincaillier n'est pas un armurier) ; `rabais` : la
    part du prix de Rosa qu'il demande pour une tenue (la liquidation vend des fins de série)."""
    return {"nom": nom, "marge": marge, "rabais": rabais, "articles": list(articles)}


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
    # --- Vague 2a : les tenues et les armes — ce que Rosa et Chez Gus vendent déjà, chez qui le dit.
    "bottes": _rayon("Les chaussures", _tenue("bottes_hiver"), _tenue("loup_marin")),
    "cordonnerie": _rayon("La cordonnerie", _tenue("bottes_hiver"), _tenue("loup_marin"), _tenue("ceinture")),
    "salopettes": _rayon("Le linge de travail", _tenue("salopette"), _tenue("camisole"), _tenue("tuque_chantier")),
    "boutique": _rayon("La boutique", _tenue("chemise_hawai"), _tenue("coupe_vent"), _tenue("camisole"),
                       _tenue("parapluie")),
    "tailleur": _rayon("Le tailleur", _tenue("complet"), _tenue("veste_cuir"), _tenue("ceinture")),
    "haute_couture": _rayon("La haute couture", _tenue("complet"), _tenue("veste_cuir"), _tenue("feutre"),
                            _tenue("canotier"), rabais=1.4),
    "chapeaux": _rayon("Les chapeaux", _tenue("beret"), _tenue("canotier"), _tenue("feutre"), _tenue("cowboy"),
                       _tenue("casquette")),
    "mercerie": _rayon("La mercerie", _tenue("tuque"), _tenue("tuque_pompon"), _tenue("tuque_oreilles"),
                       _tenue("ceinture"), _tenue("parapluie")),
    # Le magasin d'usine : ce qui sort de la manufacture, au prix d'usine.
    "manufacture": _rayon("Le magasin d'usine", _tenue("coupe_vent"), _tenue("camisole"), _tenue("salopette"),
                          rabais=0.8),
    "maroquinerie": _rayon("La maroquinerie", _tenue("veste_cuir"), _tenue("ceinture")),
    # Le bâton de hockey et la tuque du Canadien.
    "sports": _rayon("Les sports", _arme("batte"), _tenue("tuque_bbr"), _tenue("casquette"), marge=1.2),
    "chasse": _rayon("La chasse et la pêche", _arme("couteau"), _arme("fronde"), _tenue("loup_marin"),
                     _tenue("tuque_oreilles"), marge=1.2),
    "surplus": _rayon("Le surplus d'armée", _arme("couteau"), _tenue("bottes_hiver"), _tenue("tuque_chantier"),
                      _tenue("coupe_vent"), marge=1.1, rabais=0.7),
    # Les fins de série : ce que personne n'a voulu, à moitié prix.
    "liquidation": _rayon("La liquidation", _tenue("chemise_hawai"), _tenue("canotier"), _tenue("cowboy"),
                          _tenue("parapluie"), rabais=0.5),
    "bric_a_brac": _rayon("Le bric-à-brac", _tenue("tuque_phentex"), _tenue("parapluie"), _arme("poing_americain"),
                          _arme("fronde"), rabais=0.6),
    "souvenirs": _rayon("Les souvenirs", _tenue("ceinture_flechee"), _tenue("tuque_bbr"), _tenue("tuque_pompon")),
    # --- Vague 2d : le neuf qui se porte au cou et sur les yeux (`magasins.TENUES`, `en_ville` : pas chez Rosa).
    "bijouterie": _rayon("La bijouterie", _tenue("chaine_or"), _tenue("chaine_plaquee")),
    "opticien": _rayon("L'opticien", _tenue("lunettes_fumees")),
    "soierie": _rayon("La soierie", _tenue("foulard_soie"), _tenue("chemise_hawai")),
    # --- Vague 2b : les commerces de l'auto font au char garé devant la porte ce que fait Ti-Guy, chacun son métier.
    # Le café de la salle d'attente, partout.
    "pneus": _rayon("Les pneus", _piece("pneus"), _CAFE),
    "soudure": _rayon("La soudure", _piece("blindage"), _service("reparer"), _CAFE),
    "moteurs": _rayon("Les moteurs", _piece("moteur"), _piece("nitro"), _CAFE),
    "pieces_auto": _rayon("Les pièces d'auto", _piece("moteur"), _piece("blindage"), _piece("pneus"), _piece("nitro"),
                          _CAFE),
    # Les pièces usagées : les mêmes, tombées d'une épave, à 0,7.
    "pieces_usagees": _rayon("Les pièces usagées", _piece("moteur"), _piece("blindage"), _piece("pneus"), _CAFE,
                             marge=0.7),
    "peinture_auto": _rayon("La peinture", _service("repeindre"), _CAFE),
    "carrosserie": _rayon("La carrosserie", _service("reparer"), _CAFE),
    # --- Vague 3a : les services dont la mécanique existe (`SERVICES`).
    "hotel": _rayon("L'hôtel", _service("nuit"), _service("sieste"), _CAFE),
    # Le motel : la même chambre, les draps en moins.
    "motel": _rayon("Le motel", _service("nuit"), _service("sieste"), _LIQUEUR, marge=0.6),
    "clinique": _rayon("La clinique", _service("soins")),
    "dentiste": _rayon("Le dentiste", _service("soins"), marge=1.2),
    "acupuncture": _rayon("L'acupuncture", _service("soins"), _THE, marge=0.8),
    # Le spa soigne aussi, et c'est le prix qui fait du bien.
    "spa": _rayon("Le spa", _service("soins"), _THE, marge=2.0),
    "buanderie": _rayon("La buanderie", _service("linge"), _LIQUEUR),
    "nettoyeur": _rayon("Le nettoyeur", _service("linge"), marge=1.5),
    "banque": _rayon("Le guichet", _service("coffre")),
    "assurances": _rayon("Les assurances", _service("assurer"), _CAFE),
    "lavage": _rayon("Le lavage", _service("laver"), _CAFE),
    "ferraille": _rayon("La ferraille", _service("epave")),
    "club_video": _rayon("Le club vidéo", _service("film"), _bouchee("mais", "Maïs éclaté"), _LIQUEUR),
    "mah_jong": _rayon("Le club", _service("sic_bo"), _THE),
    "salle_de_jeux": _rayon("La salle de jeux", _service("machine"), _LIQUEUR, _bouchee("chips", "Chips")),
    "preteur": _rayon("Le comptoir", _service("dette")),
    # Le prêt sur gages rachète tes armes, et revend celles des autres un peu moins cher que Gus.
    "gages": _rayon("Le prêt sur gages", _service("gages"), _arme("poing_americain"), _arme("couteau"), marge=0.8),
    # --- Vague 2c : les meubles de la planque, livrés le lendemain (`Decoration`), chez qui les vend.
    "radio_tv": _rayon("La radio-télé", _meuble("televiseur"), _meuble("jukebox")),
    "meubles": _rayon("Les meubles", _meuble("sofa"), _meuble("tapis_tresse"), _meuble("lampe_lave")),
    # Le tapissier refait les sofas : le sien est un peu moins cher.
    "tapissier": _rayon("Le tapissier", _meuble("sofa"), _meuble("tapis_tresse"), marge=0.9),
    # L'aquarium : poisson rouge inclus, il s'appelle Gérald. Et la nourriture du chat, un jour.
    "animalerie": _rayon("L'animalerie", _meuble("aquarium")),
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
    # --- Les tenues et les armes (vague 2a).
    "BOTTES DE TRAVAIL": "bottes", "BOTTES ET CIRES": "bottes", "CHAUSSURES LÉO": "bottes",
    "CORDONNERIE": "cordonnerie",
    "SALOPETTES": "salopettes",
    "BOUTIQUE DIANE": "boutique", "COUTURE CHEZ EVA": "boutique",
    "TAILLEUR NG": "tailleur", "TAILLEUR ROMÉO": "tailleur", "TAILLEUR": "tailleur",
    "HAUTE COUTURE": "haute_couture",
    "MODISTE": "chapeaux", "MERCERIE": "mercerie",
    "TEXTILE": "manufacture", "MANUFACTURE": "manufacture",
    "MAROQUINERIE": "maroquinerie",
    "SPORTS BEAULIEU": "sports", "PÊCHE ET CHASSE": "chasse", "SURPLUS": "surplus",
    "LIQUIDATION": "liquidation", "BRIC-À-BRAC": "bric_a_brac", "SOUVENIRS": "souvenirs",
    # L'atelier vend les outils de la quincaillerie : le comptoir `artisan` le dit déjà.
    "ATELIER": "artisan",
    # --- Les commerces de l'auto (vague 2b).
    "PNEUS BEAULIEU": "pneus", "PNEUS DESCHAMPS": "pneus",
    "SOUDURE PELLETIER": "soudure", "SOUDURE": "soudure",
    "TRANSMISSION": "moteurs", "MOTEURS": "moteurs",
    "ATELIER 12": "pieces_auto", "PIÈCES D'AUTO": "pieces_auto", "PIÈCES USAGÉES": "pieces_usagees",
    "PEINTURE AUTO": "peinture_auto", "SABLAGE AU JET": "peinture_auto",
    "DÉBOSSELAGE": "carrosserie", "RADIATEURS": "carrosserie",
    # --- Les services (vague 3a).
    "HÔTEL DES QUAIS": "hotel", "MOTEL LA POINTE": "motel",
    "CLINIQUE": "clinique", "DOCTEUR": "clinique", "POLYCLINIQUE": "clinique",
    "DENTISTE": "dentiste", "DENTISTE DR LO": "dentiste", "ACUPUNCTURE LEE": "acupuncture", "SPA": "spa",
    "BUANDERIE": "buanderie", "BUANDERIE SUN": "buanderie", "NETTOYEUR": "nettoyeur",
    "BANQUE": "banque", "CAISSE POP": "banque", "ASSURANCES": "assurances",
    "LAVE-AUTO": "lavage", "CIRE ET HUILE": "lavage", "FERRAILLE": "ferraille",
    "CLUB VIDÉO": "club_video", "CLUB MAH-JONG": "mah_jong", "SALLE DE JEUX": "salle_de_jeux",
    "PRÊTS RAPIDES": "preteur", "CHÈQUES CASH": "preteur", "PRÊT SUR GAGES": "gages",
    # --- Le neuf (vague 2d).
    "BIJOUTERIE": "bijouterie", "BIJOUX CHEUNG": "bijouterie", "OPTICIEN": "opticien", "OPTIQUE": "opticien",
    "SOIERIE MEI": "soierie", "TISSUS ET SOIES": "soierie",
    # --- Les meubles de la planque (vague 2c).
    "RADIO-TV DUMAS": "radio_tv", "RADIO-TV KWOK": "radio_tv",
    "MEUBLES GAGNON": "meubles", "TAPISSIER": "tapissier", "ANIMALERIE": "animalerie",
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
    # --- Les marchandises qui demandent une mécanique neuve.
    "FLEURISTE": "un bouquet", "FLEURISTE MEI": "un bouquet", "FLEURISTE ROSE": "un bouquet",
    "JOUETS ET TRAINS": "des jouets", "CERFS-VOLANTS": "un cerf-volant",
    "LANTERNES FUNG": "une lanterne pour la planque", "LOCATION VÉLOS": "un vélo", "PLANCHES": "une planche",
    "IMPORT YIP": "des importations", "ENTREPÔT 7": "le gros", "GROSSISTE": "le gros",
    "À LOUER": "rien : un local vide", "PARFUMERIE": "du parfum", "TATOUAGE": "un tatouage",
    "ACIER DU NORD": "des pièces", "MACHINERIE": "des pièces", "SILENCIEUX": "un silencieux",
    "ÉLECTRIQUE": "des pièces", "USINAGE": "des pièces", "FONDERIE": "des pièces",
    "ARTISANAT": "de l'artisanat", "BOIS DE SCIAGE": "du bois", "FERBLANTIER": "de la tôle",
    "FERRONNERIE YU": "du fer forgé", "IMPRIMERIE": "des affiches", "PALETTES": "des palettes",
    "PLOMBERIE": "de la plomberie", "PÉPINIÈRE": "les plantes de la planque", "SERRURIER": "des clés, un crochet",
    "VAISSELLE CHOW": "la vaisselle de la planque", "ANTIQUAIRE": "des antiquités", "ENCADREUR": "un cadre",
    "VITRIER": "une vitre", "SCIERIE": "du bois", "MENUISERIE": "du bois",
    "ACCASTILLAGE": "le gréement du bateau", "APPÂTS ET LIGNES": "la canne et les appâts", "APPÂTS": "des appâts",
    "CORDAGES": "des cordages", "GLACE ET SEL": "de la glace", "MOTEURS MARINS": "le moteur du bateau",
    "VOILERIE": "une voile", "CHALOUPES": "une chaloupe", "CHANTIER NAVAL": "réparer le bateau",
    "CALE SÈCHE": "réparer le bateau", "MARINA": "un mouillage",
    "DISQUES VOGUE": "des disques", "MUSIQUE LAROSE": "un instrument", "LIBRAIRIE": "des livres",
    "LIBRAIRIE CHUNG": "des livres", "LIVRES": "des livres", "PAPETERIE": "de la papeterie",
    "GALERIE D'ART": "un tableau",
    # --- Les services qui restent (Martin, 6 oct. 2026) : 3b la course de taxi, 3c le photographe (le rachat, le
    # portrait, les photos de voyage), 3d la soupe de qui est cassé et les répliques de ceux qui ne vendent rien.
    "TAXI DIAMANT": "une course",
    "PHOTO EXPRESS": "le photographe", "PHOTO SOUVENIR": "le photographe", "PHOTOGRAPHE": "le photographe",
    "STUDIO LAU": "le photographe",
    "MISSION DU PORT": "une soupe pour qui est cassé", "HOSPICE": "une soupe pour qui est cassé",
    "BINGO": "le café du bingo, et le chemin du sous-sol", "LOCATION CHALOUPE": "une réplique",
    "CAPITAINERIE": "une réplique", "VÉTÉRINAIRE": "une réplique", "ASSOCIATION LI": "une réplique",
    "BUREAU DE PAIE": "une réplique", "BUREAU DE POSTE": "une réplique", "DOUANES": "une réplique",
    "GARDERIE": "une réplique", "NOTAIRE BÉLIVEAU": "une réplique", "NOTAIRE LEUNG": "une réplique",
    "BUREAU": "une réplique", "DÉPÔT": "une réplique", "ENTREPOSAGE": "une réplique",
    "ÉCOLE DE DANSE": "une réplique", "ÉCOLE": "une réplique", "BIBLIOTHÈQUE": "une réplique",
    "ARCHIVES": "une réplique",
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


def _compact(a) -> str:
    """Un article, compact : `"t:<slug>"` une tenue, `"a:<slug>"` une arme, `"p:<slug>"` une pièce du garage (leur
    nom est celui de leur catalogue — `_tenue`, `_arme`, `_piece`), `"s:<slug>"` un service au char
    (`SERVICES`), `"m:<slug>"` un meuble (son nom et son prix voyagent avec les collections : `Decoration`) ; une bouchée, son slug (son nom, et son effet, dans `noms` : `exporter`)."""
    if a["tenue"]:
        return f"t:{a['tenue']}"
    if a["arme"]:
        return f"a:{a['arme']}"
    if a.get("piece"):
        return f"p:{a['piece']}"
    if a.get("service"):
        return f"s:{a['service']}"
    if a.get("meuble"):
        return f"m:{a['meuble']}"
    return a["slug"]


def exporter() -> dict:
    """Ce qui part au navigateur, COMPACT (la suite a un plafond : 6 Ko bruts au lieu de 20) :

    - `rayons` — slug : [[article compact, …]] (`_compact`), suivi de `marge, rabais` quand l'un des deux n'est
      pas 1. ⚠️ Pas le nom du rayon : le menu porte celui de la porte (`Missions.menuComptoir`) ;
    - `noms` — le nom de chaque bouchée, UNE fois (`"pain": "Pain de ménage"`), ou `[nom, effet]` (le café) : une
      bouchée a le même nom dans tous les rayons qui la vendent (un juge le tient). Son tarif est son slug, ses
      gains `<slug>_pv` et `<slug>_souffle` (`_bouchee`) ;
    - `enseignes` — rayon : [noms]. ⚠️ Sans celles qui tomberaient au même endroit sans être nommées : le comptoir
      de leur propre famille (la TAVERNE sert `nuit`), ou un point qui n'est pas un comptoir (`POINTS` : le barbier,
      le Clairon) — le navigateur retombe sur le comptoir du genre (`Missions.comptoirDuPoint`) ;
    - `services` — chaque service : [nom, prix, char] (`SERVICES`), et `reglages` — `GAGES`, `FERRAILLE`, `SOINS_PV` ;
    - `tarifs` — les `BOUCHEES`, slug : [prix, PV, souffle].

    `Missions.rayons` le déplie une fois."""
    genres, par_rayon = noms_des_enseignes(), {}
    for nom, slug in ENSEIGNES.items():
        if slug not in POINTS and genres[nom] != {slug}:
            par_rayon.setdefault(slug, []).append(nom)
    rayons, noms = {}, {}
    for slug, r in RAYONS.items():
        rayons[slug] = [[_compact(a) for a in r["articles"]]]
        if (r["marge"], r["rabais"]) != (1.0, 1.0):
            rayons[slug] += [r["marge"], r["rabais"]]
        for a in r["articles"]:
            if a["tarif"]:
                noms[a["slug"]] = [a["nom"], a["effet"]] if a["effet"] else a["nom"]
    return {"rayons": rayons, "noms": noms, "enseignes": par_rayon, "services": {k: [v["nom"], v["prix"], 1 if v.get("char") else 0] for k, v in SERVICES.items()},
            "reglages": {"gages": GAGES, "ferraille": FERRAILLE, "soins_pv": SOINS_PV},
            "tarifs": {slug: list(t) for slug, t in BOUCHEES.items()}}
