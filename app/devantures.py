"""Les devantures : ce qui fait qu'un commerce se lit depuis la rue.

⚠️ Avant, tous les commerces de Baie-des-Brumes etaient le meme mur beige perce
d'une porte. On savait qu'un batiment etait « un commerce » parce que le
generateur le disait, pas parce qu'on le voyait. Une devanture, c'est quatre
choses qui se voient d'en haut : un BANDEAU au-dessus de la porte, le NOM
ecrit dessus, des VITRINES de chaque cote (elles s'allument la nuit) et une
PANCARTE qui depasse du mur sur le trottoir.

⚠️ Une devanture ne change RIEN a la geometrie : elle se peint par-dessus des
tuiles qui existent deja, avec la meme solidite. On peut en ajouter, en retirer
ou en repeindre sans toucher a un seul mur — et aucun juge de carte ne bouge.

Python decide (qui, ou, quel nom, quelles couleurs), JS calcule (le dessin).
"""

from __future__ import annotations

from typing import TypedDict


class Genre(TypedDict):
    slug: str
    bandeau: str
    lettres: str
    auvent: str
    vitre: str


#: Les familles de commerce, par couleur. ⚠️ Le bandeau est toujours SOMBRE et
#: les lettres CLAIRES : a cinq pixels de haut, un texte fonce sur fond clair
#: disparaît des que la nuit tombe et que la lampe de la vitrine l'eclaire.
GENRES: list[Genre] = [
    {"slug": "bouffe", "bandeau": "#7a2420", "lettres": "#ffd98a", "auvent": "#a8352c", "vitre": "#ffe6a8"},
    {"slug": "service", "bandeau": "#1f3f63", "lettres": "#cfe4ff", "auvent": "#2c5d8f", "vitre": "#d8ecff"},
    {"slug": "artisan", "bandeau": "#5a3a1c", "lettres": "#f0d2a0", "auvent": "#8a5a2c", "vitre": "#ffdfae"},
    {"slug": "nuit", "bandeau": "#3a1f52", "lettres": "#ff9de0", "auvent": "#5c2f7a", "vitre": "#ffb8ec"},
    {"slug": "commerce", "bandeau": "#1f4a32", "lettres": "#bff0cf", "auvent": "#2e6b46", "vitre": "#d2f5de"},
    {"slug": "marine", "bandeau": "#14454a", "lettres": "#a8e6e0", "auvent": "#1d666d", "vitre": "#c2f0ea"},
    {"slug": "industrie", "bandeau": "#4a4030", "lettres": "#e8c98a", "auvent": "#6b5a40", "vitre": "#f0d9a8"},
]

INDEX_GENRE = {g["slug"]: i for i, g in enumerate(GENRES)}

#: ⚠️ Le nom d'une enseigne se lit a QUATRE pixels par lettre : une devanture de
#: quatre tuiles (64 px) tient seize caracteres, une de deux tuiles en tient
#: huit. `enseigne_qui_tient` coupe au plus long qui rentre — et les noms sont
#: ecrits ici assez courts pour qu'on n'ait jamais a couper.
LARGEUR_LETTRE = 4

#: Les commerces ordinaires : ceux qu'on ne visite pas, mais qui font la ville.
#: Ils sont ranges par district pour que chaque quartier se reconnaisse a ses
#: vitrines — une poissonnerie aux Quais, un atelier de soudure a La Shop.
COMMERCES: dict[str, tuple[tuple[str, str], ...]] = {
    "faubourg": (
        ("TABAGIE DUBOIS", "commerce"), ("EPICERIE MARCEL", "bouffe"),
        ("BARBIER GILLES", "service"), ("SALON MIREILLE", "service"),
        ("QUINCAILLERIE", "artisan"), ("PHARMACIE ROY", "service"),
        ("BOULANGERIE", "bouffe"), ("CORDONNERIE", "artisan"),
        ("DISQUES VOGUE", "nuit"), ("TAVERNE CHEZ GO", "nuit"),
        ("BIJOUTERIE", "commerce"), ("PHOTO EXPRESS", "service"),
        ("CLUB VIDEO", "nuit"), ("CAISSE POP", "service"),
        ("MEUBLES GAGNON", "artisan"), ("FRIPERIE", "commerce"),
        ("LIBRAIRIE", "commerce"), ("SALLE DE POOL", "nuit"),
    ),
    "erables": (
        ("DEPANNEUR", "bouffe"), ("FLEURISTE ROSE", "commerce"),
        ("NETTOYEUR", "service"), ("CASSE-CROUTE", "bouffe"),
        ("GARDERIE", "service"), ("CREMERIE", "bouffe"),
        ("COIFFURE LINE", "service"), ("ANIMALERIE", "commerce"),
    ),
    "shop": (
        ("SOUDURE PELLETIER", "industrie"), ("PIECES USAGEES", "industrie"),
        ("ATELIER 12", "industrie"), ("PNEUS BEAULIEU", "industrie"),
        ("FERRAILLE", "industrie"), ("ELECTRIQUE", "industrie"),
        ("OUTILLAGE", "artisan"), ("PEINTURE AUTO", "industrie"),
    ),
    "quais": (
        ("POISSONNERIE", "marine"), ("APPATS ET LIGNES", "marine"),
        ("CORDAGES", "marine"), ("TAVERNE DU PORT", "nuit"),
        ("CANTINE", "bouffe"), ("MOTEURS MARINS", "marine"),
        ("CHANTIER NAVAL", "marine"), ("GLACE ET SEL", "marine"),
    ),
    "pointe": (
        ("LOCATION VELOS", "commerce"), ("CASSE-CROUTE", "bouffe"),
        ("SOUVENIRS", "commerce"), ("CREMERIE", "bouffe"),
    ),
}

#: Les lieux garantis (`carte.SPECIAUX`) : leur vrai nom est long (« Dépanneur
#: Chez Ti-Paul »), l'enseigne est courte. Un slug absent d'ici prend son nom.
ENSEIGNES: dict[str, tuple[str, str]] = {
    "terminus": ("TERMINUS", "service"),
    "armurerie": ("CHEZ GUS", "industrie"),
    "vetements": ("BOUTIQUE ROSA", "commerce"),
    "garage": ("GARAGE BANDINI", "industrie"),
    "poste": ("POLICE", "service"),
    "hopital": ("HOPITAL", "service"),
    "bar": ("LE BROUILLARD", "nuit"),
    "casse_croute": ("CASSE-CROUTE", "bouffe"),
    "depanneur": ("CHEZ TI-PAUL", "bouffe"),
    "hotel": ("HOTEL BANDINI", "nuit"),
    "cantine": ("CANTINE", "bouffe"),
    "usine": ("USINE PREVOST", "industrie"),
    "phare": ("LE PHARE", "marine"),
    "kiosque": ("KIOSQUE", "commerce"),
}

#: ⚠️ La planque n'a PAS d'enseigne : une planque avec son nom sur le mur n'est
#: plus une planque. Meme chose pour les portes condamnees.
SANS_ENSEIGNE = frozenset({"planque"})

# --- Les graffitis ----------------------------------------------------------

#: Les couleurs de bombe. Volontairement salissantes : un tag n'est pas une
#: enseigne, il doit avoir l'air pose a la va-vite.
COULEURS_TAG: tuple[str, ...] = (
    "#d34f3a", "#3a7fd3", "#e0c341", "#8f42c9", "#3fae62", "#e08a2e", "#c9c9d4",
)

#: Ce qu'on ecrit sur les murs. Les noms de gang marquent le TERRITOIRE : voir
#: « CRAVATES » sur un mur dit au joueur chez qui il est, sans un mot de HUD.
TAGS_GANG: dict[str, tuple[str, ...]] = {
    "cravates": ("CRAVATES", "LES CRAVATES", "CRV"),
    "chevreuils": ("CHEVREUILS", "CHVR"),
    "boulonneux": ("BOULONNEUX", "BLNX", "LA SHOP"),
    "morues": ("MORUES", "LES MORUES", "MRS"),
    "skateux": ("SKATEUX", "SKTX", "LA POINTE"),
}

#: Et le reste : ce que taggent ceux qui ne sont d'aucun gang.
TAGS_LIBRES: tuple[str, ...] = (
    "ROCCO", "BANDINI", "ICITTE", "1975", "TI-GUY", "ZUT", "BAIE",
    "TABARNAK", "LA VILLE DORT", "RIEN A FAIRE", "PAS DE JOBS",
)

#: 0 = ecrit a la bombe (un mot), 1 = barbouillage, 2 = ecrit + barbouillage.
MOTIFS = (0, 1, 2)


def genre_index(slug: str) -> int:
    """L'index du genre visuel, ou celui de « commerce » si on ne connaît pas."""
    return INDEX_GENRE.get(slug, INDEX_GENRE["commerce"])


def enseigne_speciale(slug: str, nom: str) -> tuple[str, int] | None:
    """Le texte et le genre d'un lieu garanti. None s'il n'en veut pas."""
    if slug in SANS_ENSEIGNE:
        return None
    court, genre = ENSEIGNES.get(slug, (nom.upper(), "commerce"))
    return court, genre_index(genre)


def commerces_du_district(district: str) -> tuple[tuple[str, str], ...]:
    """Les enseignes ordinaires d'un quartier ; celles du Faubourg par defaut."""
    return COMMERCES.get(district, COMMERCES["faubourg"])


def largeur_texte_px(texte: str) -> int:
    """La largeur du nom en pixels, comme `Atlas.largeurTexte` a l'echelle 1."""
    return max(0, len(texte) * LARGEUR_LETTRE - 1)


def tient_en(texte: str, tuiles: int, tuile_px: int = 16, marge: int = 4) -> bool:
    """Ce nom tient-il sur une enseigne de `tuiles` tuiles de large ?

    ⚠️ Deux pixels de marge de chaque cote par defaut : coller les lettres au
    bord du bandeau les rend illisibles contre le mur voisin. Un TAG, lui, a le
    droit d'aller jusqu'au bord (`marge=0`) — c'est meme ce qui lui donne son
    air de chose faite a la sauvette.
    """
    return largeur_texte_px(texte) <= tuiles * tuile_px - marge


def exporter() -> dict:
    return {
        "genres": [dict(g) for g in GENRES],
        "couleurs_tag": list(COULEURS_TAG),
        "motifs": list(MOTIFS),
    }
