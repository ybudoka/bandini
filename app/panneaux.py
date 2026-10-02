"""Les panneaux drôles de la rue (le décor, les bêtes et les gens répondent — deuxième vague, 2 oct. 2026).

Tranché par Martin : « des panneaux drôles écrits à lire en ville, un ou deux par district, posés sans
dé, et lisibles au bouton ». On se plante devant, ACTION, et on lit — UNE ligne par pression, la
suivante à la prochaine, comme la plaque d'une statue (`interactions.LIRE`). Le ton est celui de
`docs/ecrire-drole.md` : québécois, on frappe en haut (la Ville, le comité, le casino, les gangs),
jamais sur le monde qui passe.

⚠️ **RIEN ICI NE TOUCHE LA VILLE.** Les panneaux se placent sur la ville FINIE, sans un dé, et ne
vont ni dans `ville["decor"]` ni dans la carte : ils voyagent dans la SUITE du paquet
(`definitions.DANS_LA_SUITE`, après l'écran titre), et le navigateur les peint lui-même
(`static/js/panneaux.js`) — sans entité, donc sans numéro : la suite des identifiants de la ville
(`Entites.creer`) ne bouge pas d'un cran. Un poteau mince, comme le panneau d'arrêt : il n'arrête
personne, et la foule marche comme avant.

⚠️ **OÙ** : sur l'ABORD (`_`, là où la ville range déjà son mobilier pour laisser le trottoir
libre) — à défaut, sur l'herbe —, collé à un trottoir, dans le district et hors du territoire d'un gang ; jamais devant une
porte (`devants.portes`, trois tuiles), jamais au coin d'un croisement (la plaque de rue y est,
elle a son ACTION), jamais à côté d'un autre décor. Le premier panneau d'un district est la place
libre la plus proche de son centre ; le second, la plus proche qui soit à `ECART_TUILES` du premier.
"""

from __future__ import annotations

#: Les panneaux, dans l'ordre où chaque district les reçoit. `genre` : `ville` (la tôle blanche à
#: bord rouge de la Ville) ou `carton` (le contreplaqué peint à la main). ⚠️ Une ligne tient dans le
#: toast du HUD (`test_panneaux_js`) : on la lit d'un coup d'œil, pas en défilant.
PANNEAUX: tuple[dict, ...] = (
    {"district": "faubourg", "genre": "ville", "lignes": (
        "STATIONNEMENT INTERDIT DE 8 H À 18 H",
        "SAUF LE MARDI, SAUF LES JOURS FÉRIÉS,",
        "SAUF SI TU CONNAIS SAL.",
    )},
    {"district": "faubourg", "genre": "ville", "lignes": (
        "ATTENTION : NIDS-DE-POULE",
        "LE PLUS GROS A UN NOM.",
        "IL S’APPELLE GÉRARD. SOYEZ POLIS.",
    )},
    {"district": "erables", "genre": "ville", "lignes": (
        "VOISINAGE SOUS SURVEILLANCE",
        "PAR MADAME GAUTHIER,",
        "DE SA FENÊTRE, DEPUIS 1987.",
    )},
    {"district": "erables", "genre": "carton", "lignes": (
        "DÉFENSE DE TONDRE LE DIMANCHE.",
        "DÉFENSE DE RIRE FORT LE SAMEDI.",
        "— LE COMITÉ DES BOÎTES AUX LETTRES",
    )},
    {"district": "shop", "genre": "ville", "lignes": (
        "USINE PRÉVOST : 0 JOUR SANS ACCIDENT",
        "RECORD À BATTRE : 2 JOURS (1996)",
    )},
    {"district": "shop", "genre": "ville", "lignes": (
        "ENTRÉE DES CAMIONS",
        "SORTIE DES CAMIONS",
        "PIÉTONS : BONNE CHANCE",
    )},
    {"district": "quais", "genre": "ville", "lignes": (
        "DÉFENSE DE NOURRIR LES GOÉLANDS",
        "ILS SONT DÉJÀ ASSEZ GROS.",
        "PIS ILS SAVENT OÙ TU RESTES.",
    )},
    {"district": "quais", "genre": "carton", "lignes": (
        "POISSON FRAIS DU JOUR",
        "LE JOUR, ON LE DIT PAS.",
    )},
    {"district": "pointe", "genre": "ville", "lignes": (
        "BAIGNADE INTERDITE",
        "BAIGNADE TOLÉRÉE EN JUILLET",
        "BAIGNADE CONSEILLÉE QUAND IL FAIT 30",
    )},
    {"district": "pointe", "genre": "carton", "lignes": (
        "PHARE DE LA POINTE : 2 KM",
        "À PIED : 2 KM.",
        "EN SKATE : ÇA DÉPEND DES GENOUX.",
    )},
    {"district": "canton", "genre": "ville", "lignes": (
        "DRAGON D’OR : LA MAISON GAGNE TOUJOURS",
        "C’EST ÉCRIT EN PETIT.",
        "MAIS C’EST ÉCRIT.",
    )},
    {"district": "canton", "genre": "ville", "lignes": (
        "STATIONNEMENT INTERDIT — ÉCOLE LA MANTE",
        "PAS DE CONTRAVENTION.",
        "UNE DÉMONSTRATION.",
    )},
    {"district": "friches", "genre": "carton", "lignes": (
        "TERRAIN À VENDRE",
        "VUE SUR LES CARCASSES",
        "PROPRIO MOTIVÉ. TRÈS MOTIVÉ.",
    )},
    {"district": "gare", "genre": "carton", "lignes": (
        "CUEILLETTE DE SCRAP INTERDITE",
        "— LES BOULONNEUX",
        "LA CUEILLETTE, C’EST NOUS.",
    )},
)

GENRES = ("ville", "carton")

#: Deux panneaux d'un même district se tiennent au moins à cette distance (en tuiles, au plus grand
#: écart) : deux blagues dans la même rue se liraient l'une pour l'autre.
ECART_TUILES = 30

#: Ce qu'il faut de vide autour, en tuiles (au plus grand écart) : une porte (son devant), un coin de
#: croisement (la plaque de rue et ses feux), un décor, un kiosque ambulant.
LOIN_DES_PORTES = 3
LOIN_DES_COINS = 3
LOIN_DU_DECOR = 1
LOIN_DES_AMBULANTS = 2

#: Le sol où un poteau se plante, dans l'ordre où on le préfère : l'ABORD d'abord (le mobilier de la
#: ville s'y range déjà), puis l'herbe au bord d'un trottoir — les Friches n'ont aucun abord, pas un
#: mur à border.
SOLS = ("_", ",")


def _occupe(points: set[tuple[int, int]], x: int, y: int, rayon: int) -> bool:
    return any((x + dx, y + dy) in points for dy in range(-rayon, rayon + 1) for dx in range(-rayon, rayon + 1))


def _places(ville: dict, district: str) -> list[tuple[int, int]]:
    """Les tuiles d'ABORD où un panneau de ce district peut se planter, de la plus proche du centre du
    district à la plus loin (puis par rangée, puis par colonne : sans un dé)."""
    from . import devants

    zone = next((z for z in ville["zones"] if z["slug"] == district and not z.get("gang")), None)
    if zone is None:
        return []
    gangs = [z for z in ville["zones"] if z.get("gang")]
    sol = ville["sol"]
    hauteur, largeur = len(sol), len(sol[0])
    portes = set(devants.portes(ville))
    decor = {(d["x"], d["y"]) for d in ville["decor"]}
    ambulants = {(a["x"], a["y"]) for a in ville.get("ambulants", [])}
    coins: set[tuple[int, int]] = set()
    for i in ville["intersections"]:
        for y in range(i["y"] - LOIN_DES_COINS, i["y"] + i["h"] + LOIN_DES_COINS):
            for x in range(i["x"] - LOIN_DES_COINS, i["x"] + i["l"] + LOIN_DES_COINS):
                coins.add((x, y))
    cx, cy = zone["x"] + zone["l"] / 2, zone["y"] + zone["h"] / 2
    places = []
    for y in range(max(1, zone["y"]), min(hauteur - 1, zone["y"] + zone["h"])):
        for x in range(max(1, zone["x"]), min(largeur - 1, zone["x"] + zone["l"])):
            if sol[y][x] not in SOLS or (x, y) in coins:
                continue
            if not any(sol[y + dy][x + dx] == "." for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            if any(g["x"] <= x < g["x"] + g["l"] and g["y"] <= y < g["y"] + g["h"] for g in gangs):
                continue
            if (_occupe(portes, x, y, LOIN_DES_PORTES) or _occupe(decor, x, y, LOIN_DU_DECOR)
                    or _occupe(ambulants, x, y, LOIN_DES_AMBULANTS)):
                continue
            places.append((SOLS.index(sol[y][x]), (x - cx) ** 2 + (y - cy) ** 2, y, x))
    places.sort()
    return [(x, y) for _s, _d, y, x in places]


def placer(ville: dict) -> list[dict]:
    """Chaque panneau du catalogue à sa place sur la ville finie : `{x, y, genre, lignes}` (en tuiles).
    Un panneau qui ne trouve pas de place n'est pas posé (un juge exige qu'il n'y en ait aucun)."""
    poses: list[dict] = []
    for district in dict.fromkeys(p["district"] for p in PANNEAUX):
        places = _places(ville, district)
        pris: list[tuple[int, int]] = []
        for p in (p for p in PANNEAUX if p["district"] == district):
            place = next((q for q in places
                          if all(max(abs(q[0] - a), abs(q[1] - b)) >= ECART_TUILES for a, b in pris)), None)
            if place is None:
                continue
            pris.append(place)
            poses.append({"x": place[0], "y": place[1], "genre": p["genre"], "lignes": list(p["lignes"])})
    return poses


def pour_le_navigateur(ville: dict) -> list[list]:
    """Ce qui part dans la suite : `[x, y, genre, lignes]` par panneau — des listes, pas des objets,
    la suite voyage à quelques centaines d'octets de son plafond (`test_definitions`)."""
    return [[p["x"], p["y"], GENRES.index(p["genre"]), p["lignes"]] for p in placer(ville)]
