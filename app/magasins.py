"""Les comptoirs : ce qu'on y achete, a quel prix.

Les prix des armes et des vehicules viennent de leur catalogue ; un magasin ne
fait que dire ce qu'il tient. Les tenues sont les seules choses qui n'existent
qu'ici.
"""

from __future__ import annotations

from typing import TypedDict

TYPES = ("armurerie", "vetements", "garage", "casse_croute")

#: Les commerces qui n'ont pas de porte : on les sert sur le trottoir.
#: `service` dit ce qu'on y achete, `tarif`/`gain_pv`/`gain_souffle` pointent
#: dans `economie.TARIFS` — les prix ne vivent jamais en double. `effet` nomme
#: ce qui dure apres la bouchee : seul le cafe en a un (`economie.CAFE`).
#:
#: `districts` ENFERME un commerce chez lui (None = partout) : une cabane a
#: fruits de mer a La Shop, et le port n'est plus le port. `reclame` est le
#: boniment que crie l'homme-sandwich qui travaille pour lui (None = il n'en a
#: pas) ; il s'ecrit en pancarte, donc court — voir `RECLAME`.
AMBULANTS: list[dict] = [
    {"slug": "hotdog", "nom": "Kiosque à hot-dogs", "sprite": "kiosque_hotdog",
     "service": "manger", "tarif": "hotdog", "gain_pv": "hotdog_pv",
     "gain_souffle": "hotdog_souffle", "effet": None,
     "nombre": 3, "sur": "trottoir", "heures": None, "phase": 1,
     "districts": None, "reclame": "HOT-DOG MOITIÉ PRIX"},
    {"slug": "journaux", "nom": "Kiosque à journaux", "sprite": "kiosque_journaux",
     "service": "journal", "tarif": "journal", "gain_pv": None,
     "gain_souffle": None, "effet": None,
     "nombre": 2, "sur": "trottoir", "heures": [0.25, 0.75], "phase": 1,
     "districts": None, "reclame": None},
    {"slug": "cafe", "nom": "Roulotte à café", "sprite": "roulotte_cafe",
     "service": "manger", "tarif": "cafe", "gain_pv": "cafe_pv",
     "gain_souffle": "cafe_souffle", "effet": "cafe",
     "nombre": 2, "sur": "trottoir", "heures": [0.2, 0.6], "phase": 1,
     "districts": None, "reclame": None},
    {"slug": "camion_cuisine", "nom": "Camion-restaurant", "sprite": "camion_cuisine",
     "service": "manger", "tarif": "poutine", "gain_pv": "poutine_pv",
     "gain_souffle": "poutine_souffle", "effet": None,
     "nombre": 2, "sur": "stationnement", "heures": None, "phase": 1,
     "districts": None, "reclame": "POUTINE MOITIÉ PRIX"},
    # La cabane a fruits de mer : une guedille au homard sur un lit de glace,
    # aux Quais et a La Pointe seulement — c'est le port qu'on mange.
    # ⚠️ ET ELLE FERME L'HIVER (`froid_max`, docs/jalons/la-foire-fermee-l-hiver.md, vague 2) : une cabane
    # de port est saisonniere ; au grand froid, personne au comptoir, « FERMÉ POUR L'HIVER ».
    {"slug": "fruits_de_mer", "nom": "Cabane à fruits de mer", "sprite": "cabane_fruits_de_mer",
     "service": "manger", "tarif": "guedille", "gain_pv": "guedille_pv",
     "gain_souffle": "guedille_souffle", "effet": None,
     "nombre": 3, "sur": "trottoir", "heures": [0.3, 0.85], "phase": 1,
     "districts": ("quais", "pointe"), "reclame": "GUÉDILLE MOITIÉ PRIX", "froid_max": 0.75},
    # La cale du Norvegien : la contrebande de Sven, aux Quais seulement. Pas
    # une bouchee — un COMPTOIR (`service: "contrebande"`, ses prix dans
    # `economie.CONTREBANDE`) : les caisses vont dans le coffre du char gare a
    # cote, et se revendent au prix du jour dans quatre commerces de la ville.
    {"slug": "contrebande", "nom": "La cale du Norvégien", "sprite": "cale",
     "service": "contrebande", "tarif": None, "gain_pv": None,
     "gain_souffle": None, "effet": None,
     "nombre": 1, "sur": "quai", "heures": None, "phase": 1,
     "districts": ("quais",), "reclame": None},
]

#: Les machines distributrices : trois sortes, et chacune dit ce qu'elle vend.
#:
#: ⚠️ `decor` est le nom de sa fiche de DESSIN (`DECORS`, sprites.js) — c'est
#: sous ce nom qu'elle est posee dans la rue (`carte.distributrices`). Celle
#: d'une salle d'attente est un MEUBLE (`b`) dont le point porte la sorte :
#: meme catalogue, pas de decor.
#:
#: `familles` : devant quelles devantures (`devantures.GENRES`) elle se pose.
#: Une machine a cafe devant la soudure, une machine a liqueur devant la
#: taverne. ⚠️ Chaque famille en nomme au moins une — un juge le tient.
#:
#: `coincee` et `tombe` : ce que dit le HUD quand l'achat reste pris, puis
#: quand la secousse le fait tomber. `recrache` : defoncee, elle crache sa
#: marchandise en plus de sa monnaie (la machine a cafe, elle, ne crache que
#: de l'eau chaude).
DISTRIBUTRICES: dict[str, dict] = {
    "liqueur": {"nom": "Machine à liqueur", "decor": "distributrice_liqueur", "objet": "canette",
                "coincee": "LA CANETTE EST RESTÉE PRISE", "tombe": "LA CANETTE TOMBE",
                "recrache": True,
                "familles": ("bouffe", "commerce", "nuit", "marine", "mode", "savoir"),
                "articles": [
                    {"slug": "liqueur", "nom": "Liqueur", "tarif": "liqueur",
                     "gain_pv": "liqueur_pv", "gain_souffle": "liqueur_souffle", "effet": None},
                    {"slug": "jus", "nom": "Jus d'orange", "tarif": "jus",
                     "gain_pv": "jus_pv", "gain_souffle": "jus_souffle", "effet": None},
                ]},
    "grignotines": {"nom": "Machine à grignotines", "decor": "distributrice_grignotines", "objet": "sac",
                    "coincee": "LE SAC EST RESTÉ ACCROCHÉ", "tombe": "LE SAC TOMBE",
                    "recrache": True,
                    "familles": ("commerce", "service", "sante", "savoir", "nuit", "mode"),
                    "articles": [
                        {"slug": "chips", "nom": "Chips", "tarif": "chips",
                         "gain_pv": "chips_pv", "gain_souffle": "chips_souffle", "effet": None},
                        {"slug": "chocolat", "nom": "Barre de chocolat", "tarif": "chocolat",
                         "gain_pv": "chocolat_pv", "gain_souffle": "chocolat_souffle", "effet": None},
                    ]},
    "cafe": {"nom": "Machine à café", "decor": "distributrice_cafe", "objet": None,
             "coincee": "LA MACHINE A GARDÉ TON ARGENT", "tombe": "LE GOBELET SE REMPLIT",
             "recrache": False,
             "familles": ("industrie", "artisan", "service"),
             "articles": [
                 {"slug": "cafe", "nom": "Café", "tarif": "cafe",
                  "gain_pv": "cafe_pv", "gain_souffle": "cafe_souffle", "effet": "cafe"},
                 {"slug": "soupe", "nom": "Soupe en gobelet", "tarif": "soupe",
                  "gain_pv": "soupe_pv", "gain_souffle": "soupe_souffle", "effet": None},
             ]},
}


def sortes_devant(famille: str) -> tuple[str, ...]:
    """Les sortes de machine qu'on pose devant cette famille de devanture."""
    return tuple(s for s, fiche in DISTRIBUTRICES.items() if famille in fiche["familles"])


#: L'homme-sandwich : un SOLLICITEUR. Il porte l'enseigne d'un kiosque sur le
#: ventre et sur le dos, il fait les cent pas a quelques tuiles de son
#: commerce (`poste_tuiles`) et, quand il te voit passer, il vient vers toi
#: pour te tenir le crachoir (`boniment_images`) et te glisser un COUPON :
#: la prochaine bouchee a ce kiosque-la coute `rabais` fois le prix, une fois,
#: et le coupon expire au bout de `coupon_s` secondes — le temps d'y aller.
#:
#: ⚠️ C'est un solliciteur, pas un mur : il s'arrete a `portee_px` de toi,
#: il ne court jamais, et une fois son boniment fait il te laisse tranquille
#: `repos_images` images. Sans le repos, il te suivait d'un bout a l'autre de
#: la rue en repetant la meme phrase — un personnage qu'on veut frapper n'est
#: pas de la vie de rue, c'est une plaie. Sans le coupon, son boniment ne
#: promettait rien : maintenant il vaut la peine de s'arreter l'ecouter.
RECLAME = {
    "rabais": 0.5,            # le coupon : moitie prix, une seule fois
    "coupon_s": 180,          # trois minutes pour aller manger
    "rayon_tuiles": 6,        # d'ou il te repere et vient vers toi
    "portee_px": 22,          # ou il s'arrete pour te parler
    "boniment_images": 180,   # il te tient le crachoir trois secondes
    "repos_images": 1200,     # puis vingt secondes de paix
    "poste_tuiles": (5, 14),  # a quelle distance de son kiosque il se poste
    "poste_rayon_px": 96,     # jusqu'ou il s'ecarte de son poste (six tuiles)
}

#: Ce qu'un `effet` sait faire. Un kiosque qui en nommerait un autre serait une
#: promesse que le navigateur ne tient pas — un juge le refuse.
EFFETS = ("cafe",)


def ambulant(slug: str) -> dict | None:
    for commerce in AMBULANTS:
        if commerce["slug"] == slug:
            return commerce
    return None


# --- Les comptoirs des commerces ordinaires --------------------------------

#: ⚠️ « Un comptoir qui ne donne rien est une porte qu'on ouvre pour rien. »
#: Depuis qu'un commerce ordinaire sur cinq s'ouvre, il fallait repondre a la
#: question : et qu'est-ce qu'on y fait ? Un comptoir par FAMILLE de devanture
#: (`devantures.GENRES`), et chaque article fait quelque chose qui se mesure —
#: des points de vie, du souffle, une arme, une tenue.
#:
#: Les prix pointent dans `economie.TARIFS` : ils ne vivent jamais en double.
#: Une arme prend son prix au catalogue des armes, fois `marge` (le
#: quincaillier n'est pas un armurier) ; une tenue prend le sien fois `rabais`
#: (la friperie vend de l'usage).


class Article(TypedDict):
    slug: str
    nom: str
    tarif: str | None          # la cle dans economie.TARIFS
    gain_pv: str | None
    gain_souffle: str | None
    effet: str | None
    arme: str | None           # un slug de armes.CATALOGUE
    tenue: str | None          # un slug de TENUES
    journal: bool


def _art(slug: str, nom: str, tarif: str | None = None, *, pv: str | None = None,
         souffle: str | None = None, effet: str | None = None, arme: str | None = None,
         tenue: str | None = None, journal: bool = False) -> Article:
    return Article(slug=slug, nom=nom, tarif=tarif, gain_pv=pv, gain_souffle=souffle,
                   effet=effet, arme=arme, tenue=tenue, journal=journal)


#: ⚠️ De quoi manger et boire dans TOUS les comptoirs ou ca a du sens
#: (demande de Martin, 13 sept. 2026) : un depanneur qui ne vend qu'un
#: sandwich n'est pas un depanneur, et une taverne sans ailes de poulet n'est
#: pas une taverne. La friperie, elle, n'en vend pas — ca ne « fitte » pas, et
#: un comptoir qui vend n'importe quoi ne dit plus ou l'on est.
#: Ce qu'on grignote devant un film, au Rialto comme au ciné-parc.
_CINEMA: tuple[Article, ...] = (
    _art("mais", "Maïs éclaté", "mais", pv="mais_pv", souffle="mais_souffle"),
    _art("chips", "Chips", "chips", pv="chips_pv", souffle="chips_souffle"),
    _art("nachos", "Nachos", "nachos", pv="nachos_pv", souffle="nachos_souffle"),
    _art("liqueur", "Liqueur", "liqueur", pv="liqueur_pv", souffle="liqueur_souffle"),
    _art("chocolat", "Barre de chocolat", "chocolat", pv="chocolat_pv", souffle="chocolat_souffle"),
)

COMPTOIRS: dict[str, dict] = {
    "bouffe": {"nom": "Le comptoir", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("sandwich", "Sandwich", "sandwich", pv="sandwich_pv", souffle="sandwich_souffle"),
        _art("soupe", "Soupe aux pois", "soupe", pv="soupe_pv", souffle="soupe_souffle"),
        _art("pate_chinois", "Pâté chinois", "pate_chinois", pv="pate_chinois_pv", souffle="pate_chinois_souffle"),
        _art("tarte", "Pointe de tarte au sucre", "tarte", pv="tarte_pv", souffle="tarte_souffle"),
        _art("cafe", "Café", "cafe", pv="cafe_pv", souffle="cafe_souffle", effet="cafe"),
        _art("liqueur", "Liqueur", "liqueur", pv="liqueur_pv", souffle="liqueur_souffle"),
    ]},
    "service": {"nom": "Le comptoir", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("cafe", "Café", "cafe", pv="cafe_pv", souffle="cafe_souffle", effet="cafe"),
        _art("beigne", "Beigne", "beigne", pv="beigne_pv", souffle="beigne_souffle"),
        _art("liqueur", "Liqueur", "liqueur", pv="liqueur_pv", souffle="liqueur_souffle"),
        _art("journal", "Le Clairon de la Baie", "journal", journal=True),
    ]},
    # La quincaillerie : les memes batons que Chez Gus, au prix du voisin — et
    # le presentoir a cote de la caisse, comme dans toutes : une liqueur, une
    # barre de chocolat, rien qui demande une cuisine.
    "artisan": {"nom": "La quincaillerie", "marge": 1.3, "rabais": 1.0, "articles": [
        _art("batte", "Bâton", arme="batte"),
        _art("couteau", "Couteau", arme="couteau"),
        _art("liqueur", "Liqueur", "liqueur", pv="liqueur_pv", souffle="liqueur_souffle"),
        _art("chocolat", "Barre de chocolat", "chocolat", pv="chocolat_pv", souffle="chocolat_souffle"),
    ]},
    "nuit": {"nom": "Le bar", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("biere", "Grosse bière", "biere", pv="biere_pv", souffle="biere_souffle"),
        _art("shooter", "Shooter de rye", "shooter", pv="shooter_pv", souffle="shooter_souffle"),
        _art("ailes", "Ailes de poulet", "ailes", pv="ailes_pv", souffle="ailes_souffle"),
        _art("chips", "Chips", "chips", pv="chips_pv", souffle="chips_souffle"),
        _art("cafe", "Café", "cafe", pv="cafe_pv", souffle="cafe_souffle", effet="cafe"),
    ]},
    "commerce": {"nom": "Le magasin", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("sandwich", "Sandwich", "sandwich", pv="sandwich_pv", souffle="sandwich_souffle"),
        _art("chips", "Chips", "chips", pv="chips_pv", souffle="chips_souffle"),
        _art("chocolat", "Barre de chocolat", "chocolat", pv="chocolat_pv", souffle="chocolat_souffle"),
        _art("liqueur", "Liqueur", "liqueur", pv="liqueur_pv", souffle="liqueur_souffle"),
        _art("journal", "Le Clairon de la Baie", "journal", journal=True),
    ]},
    # La poissonnerie sert aussi les fruits de mer : ce qui fait qu'on entre
    # aux Quais pour autre chose qu'un poisson frit.
    "marine": {"nom": "La poissonnerie", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("friture", "Poisson frit", "friture", pv="friture_pv", souffle="friture_souffle"),
        _art("guedille", "Guédille au homard", "guedille", pv="guedille_pv", souffle="guedille_souffle"),
        _art("crevettes", "Crevettes de Matane", "crevettes", pv="crevettes_pv", souffle="crevettes_souffle"),
        _art("chaudree", "Chaudrée de palourdes", "chaudree", pv="chaudree_pv", souffle="chaudree_souffle"),
    ]},
    # La shop : la cantine du fond, un sandwich et une liqueur entre deux quarts.
    "industrie": {"nom": "Le magasin", "marge": 1.25, "rabais": 1.0, "articles": [
        _art("extincteur", "Extincteur", arme="extincteur"),
        _art("sandwich", "Sandwich", "sandwich", pv="sandwich_pv", souffle="sandwich_souffle"),
        _art("cafe", "Café", "cafe", pv="cafe_pv", souffle="cafe_souffle", effet="cafe"),
        _art("liqueur", "Liqueur", "liqueur", pv="liqueur_pv", souffle="liqueur_souffle"),
    ]},
    "sante": {"nom": "La pharmacie", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("pilules", "Pilules", "pilules", pv="pilules_pv"),
        _art("jus", "Jus d'orange", "jus", pv="jus_pv", souffle="jus_souffle"),
        _art("chocolat", "Barre de chocolat", "chocolat", pv="chocolat_pv", souffle="chocolat_souffle"),
    ]},
    # La friperie : du linge d'occasion. Changer de linge fait oublier ta tete
    # (`porterTenue` remet la police a zero) — a ce prix-la, ca vaut le detour.
    # LA CABANE À SUCRE (docs/jalons/la-cabane-a-sucre.md) : le repas des sucres, au printemps seulement
    # (`saison` : hors saison, le comptoir se dit fermé — pas un menu vide) ; et le défi de la tire.
    # ⚠️ `bloc` : ce comptoir n'est pas une famille de devantures (il n'y en a qu'un, dans un bloc de carte, le rang) —
    # en ajouter une ferait glisser la ville (`devantures.GENRES` se tire à l'empreinte des bâtiments).
    "sucre": {"nom": "La cabane à sucre", "marge": 1.0, "rabais": 1.0, "saison": "printemps", "defi": "tire",
              "hors_saison": "FERMÉ — ON OUVRE AU TEMPS DES SUCRES", "bloc": "rang",
              "articles": [
        _art("oreilles", "Oreilles de crisse", "oreilles", pv="oreilles_pv", souffle="oreilles_souffle"),
        _art("feves", "Fèves au lard", "feves", pv="feves_pv", souffle="feves_souffle"),
        _art("tire", "Tire sur la neige", "tire", pv="tire_pv", souffle="tire_souffle"),
    ]},
    # LES ENSEIGNES QUI OUVRENT POUR VRAI (docs/jalons/les-enseignes-qui-ouvrent-pour-vrai.md) : quatre
    # comptoirs qui ne sont pas une famille de devantures (`enseigne`, comme le `bloc` de la cabane — une
    # famille de plus ferait glisser la ville). `joue` : ce que le comptoir fait jouer (⚠️ pas `jeu` : ce mot-là est
    # le jeu d'acteur, et il ne part jamais au navigateur — `test_interpretation`) en plus de ce qu'il
    # vend (`Enseignes.itemDuComptoir`) ; `defi` : le défi qu'il propose, comme la tire à la cabane.
    "bingo": {"nom": "Le bingo du sous-sol", "marge": 1.0, "rabais": 1.0, "enseigne": True, "joue": "bingo",
              "articles": [
        _art("cafe", "Café", "cafe", pv="cafe_pv", souffle="cafe_souffle", effet="cafe"),
        _art("beigne", "Beigne", "beigne", pv="beigne_pv", souffle="beigne_souffle"),
    ]},
    # Le Rialto et le casse-croûte du ciné-parc vendent la même chose (Martin, 27 sept. 2026 : « popcorn, chips,
    # liqueur, nachos etc. », « cinéma aussi ») : `_CINEMA`, une seule liste.
    "rialto": {"nom": "Le cinéma Rialto", "marge": 1.0, "rabais": 1.0, "enseigne": True, "joue": "film",
               "articles": list(_CINEMA)},
    # LE CASSE-CROÛTE DU CINÉ-PARC (docs/jalons/le-casse-croute-du-cine-parc-au-centre-et-le-projecteur.md) : la
    # cabane au milieu du terrain, qui est aussi la cabine du projecteur. L'été seulement, comme le film ; le
    # soir, comme les séances. ⚠️ `bloc`, comme la cabane à sucre : pas une famille de devantures.
    "cineparc": {"nom": "Le casse-croûte du ciné-parc", "marge": 1.0, "rabais": 1.0, "saison": "ete",
                 "hors_saison": "FERMÉ — ON ROUVRE L'ÉTÉ", "bloc": "cineparc", "articles": list(_CINEMA)},
    "quilles": {"nom": "La salle de quilles", "marge": 1.0, "rabais": 1.0, "enseigne": True, "defi": "quilles",
                "articles": [
        _art("biere", "Grosse bière", "biere", pv="biere_pv", souffle="biere_souffle"),
        _art("hotdog", "Hot-dog steamé", "hotdog", pv="hotdog_pv", souffle="hotdog_souffle"),
        _art("liqueur", "Liqueur", "liqueur", pv="liqueur_pv", souffle="liqueur_souffle"),
    ]},
    "lave_auto": {"nom": "Le lave-auto", "marge": 1.0, "rabais": 1.0, "enseigne": True, "joue": "lave_auto",
                  "articles": [
        _art("cafe", "Café", "cafe", pv="cafe_pv", souffle="cafe_souffle", effet="cafe"),
        _art("liqueur", "Liqueur", "liqueur", pv="liqueur_pv", souffle="liqueur_souffle"),
    ]},
    "mode": {"nom": "La friperie", "marge": 1.0, "rabais": 0.6, "articles": [
        _art("coupe_vent", "Coupe-vent bleu", tenue="coupe_vent"),
        _art("chemise_hawai", "Chemise hawaïenne", tenue="chemise_hawai"),
    ]},
}

#: ⚠️ **LA NUIT A SES HABITUDES : LES COMPTOIRS ONT LEURS HEURES.** Jusqu'ici, on
#: achetait une pointe de tarte à 4 h du matin partout en ville. Chaque famille ouvre
#: au plus tard à 7 h (le jeu commence à 8 h 24 : le jour ne change pas) et ferme
#: entre 20 h et 23 h selon son métier. La TAVERNE ouvre à 8 h et ferme à 3 h — l'heure
#: du last call (`nuit.LAST_CALL`). Le DÉPANNEUR ne ferme jamais, lui : il vend sous
#: la famille « bouffe », alors c'est la PIÈCE qui le dit (`nuit.COMPTOIRS`).
HEURES_DES_COMPTOIRS: dict[str, tuple[float, float]] = {
    "bouffe": (6 / 24, 23 / 24),
    "service": (7 / 24, 21 / 24),
    "artisan": (7 / 24, 21 / 24),
    "nuit": (8 / 24, 3 / 24),
    "commerce": (7 / 24, 22 / 24),
    "marine": (5 / 24, 20 / 24),       # la poissonnerie : les bateaux rentrent tôt
    "industrie": (6 / 24, 20 / 24),
    "sante": (7 / 24, 22 / 24),
    "mode": (7 / 24, 21 / 24),
    "sucre": (7 / 24, 22 / 24),
    # ⚠️ Le Rialto vend son maïs éclaté le jour ; ses SÉANCES, elles, sont le soir (`enseignes.REGLES`).
    "bingo": (8 / 24, 23 / 24),
    "rialto": (8 / 24, 23 / 24),
    # Le casse-croûte du ciné-parc ouvre avant la brunante et ferme après la dernière bobine.
    "cineparc": (17 / 24, 2 / 24),
    "quilles": (8 / 24, 23 / 24),
    "lave_auto": (7 / 24, 20 / 24),
}
for _famille, _heures in HEURES_DES_COMPTOIRS.items():
    COMPTOIRS[_famille]["heures"] = _heures


def comptoir(genre: str) -> dict | None:
    return COMPTOIRS.get(genre)


class Magasin(TypedDict):
    slug: str
    nom: str
    type: str
    lieu: str
    articles: list[str]
    munitions: list[str]
    tenues: list[dict]
    services: list[str]
    phase: int


#: ⚠️ Depuis la garde-robe (22 sept. 2026, `garderobe.py`), une tenue est une PIÈCE qu'on enfile
#: sur le squelette du joueur, plus seulement une couleur de chandail : `emplacement` dit où elle
#: va (`corps` : le haut ; `tete` : un chapeau), `piece` ce qu'elle est (`haut` et son `motif`,
#: ses `accessoires`, ou le `chapeau`). On porte un corps ET une tête à la fois.
TENUES = [
    {"slug": "chandail", "nom": "Chandail de Rocco", "prix": 0, "couleur": "#c0392b",
     "emplacement": "corps", "piece": {"haut": "chandail"}},
    {"slug": "coupe_vent", "nom": "Coupe-vent bleu", "prix": 80, "couleur": "#2980b9",
     "emplacement": "corps", "piece": {"haut": "coton_ouate"}},
    {"slug": "veste_cuir", "nom": "Veste de cuir", "prix": 200, "couleur": "#2c2c2c",
     "emplacement": "corps", "piece": {"haut": "veston"}},
    {"slug": "complet", "nom": "Complet gris", "prix": 500, "couleur": "#7f8c8d",
     "emplacement": "corps", "piece": {"haut": "veston", "accessoires": ["cravate"]}},
    {"slug": "chemise_hawai", "nom": "Chemise hawaïenne", "prix": 120, "couleur": "#f39c12",
     "emplacement": "corps", "piece": {"haut": "chemise", "motif": "carreaute"}},
    {"slug": "camisole", "nom": "Camisole blanche", "prix": 40, "couleur": "#e8e8e8",
     "emplacement": "corps", "piece": {"haut": "camisole"}},
    {"slug": "salopette", "nom": "Salopette de mécano", "prix": 150, "couleur": "#e8e8e8",
     "emplacement": "corps", "piece": {"haut": "salopette"}},
    # Les chapeaux : ils se portent PAR-DESSUS le linge, et en changer aussi fait oublier ta tête.
    {"slug": "tuque", "nom": "Tuque rouge", "prix": 30, "couleur": "#c0392b",
     "emplacement": "tete", "piece": {"chapeau": "tuque"}},
    {"slug": "casquette", "nom": "Casquette bleue", "prix": 40, "couleur": "#2980b9",
     "emplacement": "tete", "piece": {"chapeau": "casquette"}},
    {"slug": "beret", "nom": "Béret noir", "prix": 60, "couleur": "#1a1a22",
     "emplacement": "tete", "piece": {"chapeau": "beret"}},
    {"slug": "canotier", "nom": "Canotier de paille", "prix": 90, "couleur": "#e8d8a0",
     "emplacement": "tete", "piece": {"chapeau": "canotier"}},
    {"slug": "cowboy", "nom": "Chapeau de cowboy", "prix": 120, "couleur": "#7a5a2a",
     "emplacement": "tete", "piece": {"chapeau": "cowboy"}},
    {"slug": "feutre", "nom": "Feutre de gangster", "prix": 150, "couleur": "#3a2a1a",
     "emplacement": "tete", "piece": {"chapeau": "feutre"}},
    # ⚠️ **LA SEULE QUI NE SE VEND PAS** : le lot du troisieme jeu d'adresse de
    # la foire (`missions.CASQUETTE_DE_LA_FOIRE`). `prime` dit d'ou elle vient,
    # et c'est ce qui la tient hors de la boutique de Rosa tant qu'on ne l'a pas
    # gagnee — un lot qu'on peut acheter n'est plus un lot. Une fois a soi, elle
    # s'y range comme les autres : c'est la qu'on vient la remettre.
    {"slug": "casquette_foire", "nom": "Casquette de la foire", "prix": None,
     "couleur": "#e8a33a", "prime": "foire", "emplacement": "tete", "piece": {"chapeau": "casquette"}},
    # L'hiver chez Rosa (`docs/jalons/rosa-habille-l-hiver.md`) : cinq tuques de plus, et trois
    # places neuves où tout se cumule — `pieds` (des `souliers` du squelette), `taille` (un
    # accessoire) et `main` (un `objet`). ⚠️ La vieille tuque de Rocco ne se vend pas (`prime`) :
    # une partie commence le 1er janvier, et c'est lui qui te la donne.
    {"slug": "tuque_rocco", "nom": "Vieille tuque de Rocco", "prix": None, "couleur": "#6a5a4a",
     "prime": "rocco", "emplacement": "tete", "piece": {"chapeau": "tuque_chantier"}},
    {"slug": "tuque_pompon", "nom": "Tuque à pompon", "prix": 35, "couleur": "#2c3e50",
     "emplacement": "tete", "piece": {"chapeau": "tuque_pompon"}},
    {"slug": "tuque_bbr", "nom": "Tuque bleu-blanc-rouge", "prix": 45, "couleur": "#1f4e9c",
     "emplacement": "tete", "piece": {"chapeau": "tuque_rayee"}},
    {"slug": "tuque_chantier", "nom": "Tuque de chantier", "prix": 25, "couleur": "#8a8a8a",
     "emplacement": "tete", "piece": {"chapeau": "tuque_chantier"}},
    {"slug": "tuque_phentex", "nom": "Tuque en Phentex de matante", "prix": 20, "couleur": "#e67e22",
     "emplacement": "tete", "piece": {"chapeau": "tuque_phentex"}},
    {"slug": "tuque_oreilles", "nom": "Tuque à oreilles", "prix": 50, "couleur": "#7d3c98",
     "emplacement": "tete", "piece": {"chapeau": "tuque_oreilles"}},
    {"slug": "bottes_hiver", "nom": "Bottes d'hiver", "prix": 90, "couleur": "#4a3222",
     "emplacement": "pieds", "piece": {"souliers": "bottes_hiver"}},
    {"slug": "loup_marin", "nom": "Bottes de loup marin", "prix": 350, "couleur": "#8a8f94",
     "emplacement": "pieds", "piece": {"souliers": "loup_marin"}},
    {"slug": "ceinture", "nom": "Ceinture de cuir", "prix": 25, "couleur": "#3a2616",
     "emplacement": "taille", "piece": {"accessoires": ["ceinture"]}},
    {"slug": "ceinture_flechee", "nom": "Ceinture fléchée", "prix": 120, "couleur": "#b8322a",
     "emplacement": "taille", "piece": {"accessoires": ["ceinture_flechee"]}},
    {"slug": "parapluie", "nom": "Parapluie", "prix": 35, "couleur": "#1a1a22",
     "emplacement": "main", "piece": {"objet": "parapluie"}},
]

#: Où se porte une tenue, et le champ de la partie qui dit laquelle on porte (`B.partie[champ]`).
#: On porte une pièce de chaque place à la fois ; ⚠️ l'ordre est celui des sections chez Rosa.
PLACES = {"corps": "tenue", "tete": "chapeau", "pieds": "pieds", "taille": "taille", "main": "main"}

#: Chez le barbier (`boutique_service`) : la coupe change la COULEUR des cheveux
#: du sprite (`h`). ⚠️ Ce n'est pas de la coquetterie — changer de tete remet la
#: police a zero, exactement comme changer de linge. C'est ce qui fait d'un
#: salon de coiffure un endroit ou l'on entre en courant.
COIFFURES: list[dict] = [
    {"slug": "brun", "nom": "Brun", "couleur": "#3a2a1a"},
    {"slug": "noir", "nom": "Noir de jais", "couleur": "#101018"},
    {"slug": "blond", "nom": "Blond", "couleur": "#d8b46a"},
    {"slug": "roux", "nom": "Roux", "couleur": "#a8452a"},
    {"slug": "gris", "nom": "Poivre et sel", "couleur": "#b8b8b8"},
]

CATALOGUE: list[Magasin] = [
    {"slug": "armurerie", "nom": "Chez Gus", "type": "armurerie", "lieu": "armurerie",
     "articles": ["poing_americain", "fronde", "batte", "couteau", "extincteur", "pistolet", "fusil"],
     "munitions": ["fronde", "pistolet", "fusil"], "tenues": [], "services": [], "phase": 1},
    # ⚠️ Les tenues de Rosa voyagent UNE fois, sous `tenues` (`definitions.py`) : cette copie-ci, que
    # rien ne lisait, doublait leur poids au paquet — l'hiver chez Rosa l'aurait fait deborder.
    {"slug": "vetements", "nom": "Boutique Rosa", "type": "vetements", "lieu": "vetements",
     "articles": [], "munitions": [], "tenues": [], "services": [], "phase": 1},
    {"slug": "garage", "nom": "Garage Rocco Bandini", "type": "garage", "lieu": "garage",
     "articles": ["moto", "auto", "taxi"], "munitions": [], "tenues": [],
     "services": ["vendre", "reparer", "repeindre"], "phase": 1},
    {"slug": "casse_croute", "nom": "Casse-croûte du Faubourg", "type": "casse_croute",
     "lieu": "casse_croute", "articles": [], "munitions": [], "tenues": [],
     "services": ["hotdog"], "phase": 1},
]


def par_slug(slug: str) -> Magasin | None:
    for magasin in CATALOGUE:
        if magasin["slug"] == slug:
            return magasin
    return None


#: Le marche noir : Josee, au bar, une fois le Faubourg libere (M5). Les
#: armes de Chez Gus a ce prix-la, sans facture — et ⚠️ ce qui fait du bruit
#: (Molotov, mitraillette, carabine, dynamite, grenade) ne se vend QU'ICI, munitions
#: comprises : Gus a une vitrine, Josee n'en a pas. `test_armes` le verifie.
MARCHE_NOIR: dict = {"apres": "m5", "rabais": 0.7,
                     "articles": ["couteau", "pistolet", "fusil", "dynamite", "molotov", "grenade",
                                  "mitraillette", "carabine"],
                     "munitions": ["pistolet", "fusil", "dynamite", "molotov", "grenade",
                                   "mitraillette", "carabine"],
                     # ⚠️ Ce qui n'est pas une arme : le skimmer (`economie.GUICHET`),
                     # qu'on pose sur un guichet et qu'on revient vider le lendemain.
                     "objets": ["skimmer"]}
