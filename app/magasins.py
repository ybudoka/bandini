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
AMBULANTS: list[dict] = [
    {"slug": "hotdog", "nom": "Kiosque à hot-dogs", "sprite": "kiosque_hotdog",
     "service": "manger", "tarif": "hotdog", "gain_pv": "hotdog_pv",
     "gain_souffle": "hotdog_souffle", "effet": None,
     "nombre": 3, "sur": "trottoir", "heures": None, "phase": 1},
    {"slug": "journaux", "nom": "Kiosque à journaux", "sprite": "kiosque_journaux",
     "service": "journal", "tarif": "journal", "gain_pv": None,
     "gain_souffle": None, "effet": None,
     "nombre": 2, "sur": "trottoir", "heures": [0.25, 0.75], "phase": 1},
    {"slug": "cafe", "nom": "Roulotte à café", "sprite": "roulotte_cafe",
     "service": "manger", "tarif": "cafe", "gain_pv": "cafe_pv",
     "gain_souffle": "cafe_souffle", "effet": "cafe",
     "nombre": 2, "sur": "trottoir", "heures": [0.2, 0.6], "phase": 1},
    {"slug": "camion_cuisine", "nom": "Camion-restaurant", "sprite": "camion_cuisine",
     "service": "manger", "tarif": "poutine", "gain_pv": "poutine_pv",
     "gain_souffle": "poutine_souffle", "effet": None,
     "nombre": 2, "sur": "stationnement", "heures": None, "phase": 1},
]

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


COMPTOIRS: dict[str, dict] = {
    "bouffe": {"nom": "Le comptoir", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("sandwich", "Sandwich", "sandwich", pv="sandwich_pv", souffle="sandwich_souffle"),
        _art("cafe", "Café", "cafe", pv="cafe_pv", souffle="cafe_souffle", effet="cafe"),
    ]},
    "service": {"nom": "Le comptoir", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("cafe", "Café", "cafe", pv="cafe_pv", souffle="cafe_souffle", effet="cafe"),
        _art("journal", "Le Clairon de la Baie", "journal", journal=True),
    ]},
    # La quincaillerie : les memes batons que Chez Gus, au prix du voisin.
    "artisan": {"nom": "La quincaillerie", "marge": 1.3, "rabais": 1.0, "articles": [
        _art("batte", "Bâton", arme="batte"),
        _art("couteau", "Couteau", arme="couteau"),
    ]},
    "nuit": {"nom": "Le bar", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("biere", "Grosse bière", "biere", pv="biere_pv", souffle="biere_souffle"),
        _art("cafe", "Café", "cafe", pv="cafe_pv", souffle="cafe_souffle", effet="cafe"),
    ]},
    "commerce": {"nom": "Le magasin", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("sandwich", "Sandwich", "sandwich", pv="sandwich_pv", souffle="sandwich_souffle"),
        _art("journal", "Le Clairon de la Baie", "journal", journal=True),
    ]},
    "marine": {"nom": "La poissonnerie", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("friture", "Poisson frit", "friture", pv="friture_pv", souffle="friture_souffle"),
    ]},
    "industrie": {"nom": "Le magasin", "marge": 1.25, "rabais": 1.0, "articles": [
        _art("extincteur", "Extincteur", arme="extincteur"),
        _art("cafe", "Café", "cafe", pv="cafe_pv", souffle="cafe_souffle", effet="cafe"),
    ]},
    "sante": {"nom": "La pharmacie", "marge": 1.0, "rabais": 1.0, "articles": [
        _art("pilules", "Pilules", "pilules", pv="pilules_pv"),
    ]},
    # La friperie : du linge d'occasion. Changer de linge fait oublier ta tete
    # (`porterTenue` remet la police a zero) — a ce prix-la, ca vaut le detour.
    "mode": {"nom": "La friperie", "marge": 1.0, "rabais": 0.6, "articles": [
        _art("coupe_vent", "Coupe-vent bleu", tenue="coupe_vent"),
        _art("chemise_hawai", "Chemise hawaïenne", tenue="chemise_hawai"),
    ]},
}


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


TENUES = [
    {"slug": "chandail", "nom": "Chandail de Rocco", "prix": 0, "couleur": "#c0392b"},
    {"slug": "coupe_vent", "nom": "Coupe-vent bleu", "prix": 80, "couleur": "#2980b9"},
    {"slug": "veste_cuir", "nom": "Veste de cuir", "prix": 200, "couleur": "#2c2c2c"},
    {"slug": "complet", "nom": "Complet gris", "prix": 500, "couleur": "#7f8c8d"},
    {"slug": "chemise_hawai", "nom": "Chemise hawaïenne", "prix": 120, "couleur": "#f39c12"},
]

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
     "articles": ["fronde", "batte", "couteau", "extincteur", "pistolet", "fusil"],
     "munitions": ["fronde", "pistolet", "fusil"], "tenues": [], "services": [], "phase": 1},
    {"slug": "vetements", "nom": "Boutique Rosa", "type": "vetements", "lieu": "vetements",
     "articles": [], "munitions": [], "tenues": TENUES, "services": [], "phase": 1},
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
#: memes armes que Chez Gus, mais a ce prix-la — et sans facture.
MARCHE_NOIR: dict = {"apres": "m5", "rabais": 0.7, "articles": ["couteau", "pistolet", "fusil"],
                     "munitions": ["pistolet", "fusil"]}
