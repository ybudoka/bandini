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
    # ⚠️ Trois familles de plus, et ce n'est pas de la decoration : avec sept
    # couleurs pour cent seize commerces, deux rues voisines finissaient en
    # rouge et bleu comme la premiere. La croix verte de la pharmacie, la
    # prune de la mercerie et l'encre du libraire se reconnaissent de loin.
    {"slug": "sante", "bandeau": "#1f5a4a", "lettres": "#c8f0dd", "auvent": "#2e7d66", "vitre": "#d8f5ea"},
    {"slug": "mode", "bandeau": "#5f2145", "lettres": "#ffc2dd", "auvent": "#8d3568", "vitre": "#ffd4e8"},
    {"slug": "savoir", "bandeau": "#33305c", "lettres": "#d4cfff", "auvent": "#4d4680", "vitre": "#e2ddff"},
]

INDEX_GENRE = {g["slug"]: i for i, g in enumerate(GENRES)}

#: ⚠️ Le nom d'une enseigne se lit a QUATRE pixels par lettre : une devanture de
#: quatre tuiles (64 px) tient seize caracteres, une de deux tuiles en tient
#: huit. `enseigne_qui_tient` coupe au plus long qui rentre — et les noms sont
#: ecrits ici assez courts pour qu'on n'ait jamais a couper.
LARGEUR_LETTRE = 4

#: Les commerces ordinaires : ceux qui font la ville, qu'on les visite ou non.
#: Ils sont ranges par district pour que chaque quartier se reconnaisse a ses
#: vitrines — une poissonnerie aux Quais, un atelier de soudure a La Shop.
#:
#: ⚠️ Un catalogue COURT se voit : a huit noms pour vingt-quatre vitrines, La
#: Shop affichait sept fois « FERRAILLE » et la rue devenait un papier peint
#: (mesure du 13 sept. 2026 : sept doublons pour quatre noms, sur 116
#: devantures). Chaque quartier en porte donc trois a quatre fois plus, et
#: `_Chantier.choisir_enseigne` refuse le meme nom a moins de
#: `DISTANCE_DOUBLON` tuiles : on n'en voit jamais deux du meme trottoir.
COMMERCES: dict[str, tuple[tuple[str, str], ...]] = {
    # Le Faubourg : le centre-ville ouvrier, celui qui a de tout et rien de neuf.
    "faubourg": (
        ("TABAGIE DUBOIS", "commerce"), ("ÉPICERIE MARCEL", "bouffe"),
        ("BARBIER GILLES", "service"), ("SALON MIREILLE", "service"),
        ("QUINCAILLERIE", "artisan"), ("PHARMACIE ROY", "sante"),
        ("BOULANGERIE", "bouffe"), ("CORDONNERIE", "artisan"),
        ("DISQUES VOGUE", "savoir"), ("TAVERNE CHEZ GO", "nuit"),
        ("BIJOUTERIE", "commerce"), ("PHOTO EXPRESS", "service"),
        ("CLUB VIDÉO", "nuit"), ("CAISSE POP", "service"),
        ("MEUBLES GAGNON", "artisan"), ("FRIPERIE", "mode"),
        ("LIBRAIRIE", "savoir"), ("SALLE DE POOL", "nuit"),
        ("BOUCHERIE PARÉ", "bouffe"), ("RÔTISSERIE", "bouffe"),
        ("PÂTISSERIE", "bouffe"), ("FRUITERIE", "bouffe"),
        ("PIZZERIA NAPOLI", "bouffe"), ("LAITERIE", "bouffe"),
        ("5-10-15", "commerce"), ("RADIO-TV DUMAS", "commerce"),
        ("SPORTS BEAULIEU", "commerce"), ("JOUETS ET TRAINS", "commerce"),
        ("BUANDERIE", "service"), ("ASSURANCES", "service"),
        ("BANQUE", "service"), ("NOTAIRE BÉLIVEAU", "service"),
        ("OPTICIEN", "sante"), ("DENTISTE", "sante"),
        ("CLINIQUE", "sante"), ("TAILLEUR ROMÉO", "mode"),
        ("CHAUSSURES LÉO", "mode"), ("MERCERIE", "mode"),
        ("LE CLAIRON", "savoir"), ("PAPETERIE", "savoir"),
        ("IMPRIMERIE", "artisan"), ("PLOMBERIE", "artisan"),
        ("SERRURIER", "artisan"), ("TAPISSIER", "artisan"),
        ("CINÉMA RIALTO", "nuit"), ("SALLE DE QUILLES", "nuit"),
        ("BRASSERIE", "nuit"), ("DISCO LE MIRAGE", "nuit"),
    ),
    # Les Erables : la banlieue. Ce qu'on trouve a pied quand on a un char.
    "erables": (
        ("DÉPANNEUR", "bouffe"), ("FLEURISTE ROSE", "commerce"),
        ("NETTOYEUR", "service"), ("CASSE-CROÛTE", "bouffe"),
        ("GARDERIE", "service"), ("CRÉMERIE", "bouffe"),
        ("COIFFURE LINE", "service"), ("ANIMALERIE", "commerce"),
        ("PHARMACIE", "sante"), ("VÉTÉRINAIRE", "sante"),
        ("BOULANGERIE", "bouffe"), ("MARCHÉ BEAUDOIN", "bouffe"),
        ("BEIGNES CHEZ TI", "bouffe"), ("POULET BBQ", "bouffe"),
        ("ÉCOLE DE DANSE", "savoir"), ("BIBLIOTHÈQUE", "savoir"),
        ("MUSIQUE LAROSE", "savoir"), ("QUINCAILLERIE", "artisan"),
        ("PÉPINIÈRE", "artisan"), ("COUTURE CHEZ EVA", "mode"),
        ("BOUTIQUE DIANE", "mode"), ("CAISSE POP", "service"),
        ("BUREAU DE POSTE", "service"), ("TAXI DIAMANT", "service"),
        ("PHOTOGRAPHE", "service"), ("LAVE-AUTO", "industrie"),
        ("PNEUS DESCHAMPS", "industrie"), ("CLUB VIDÉO", "nuit"),
    ),
    # La Shop : l'industriel. Rien ne s'achete ici qui ne serve a reparer.
    "shop": (
        ("SOUDURE PELLETIER", "industrie"), ("PIÈCES USAGÉES", "industrie"),
        ("ATELIER 12", "industrie"), ("PNEUS BEAULIEU", "industrie"),
        ("FERRAILLE", "industrie"), ("ÉLECTRIQUE", "industrie"),
        ("OUTILLAGE", "artisan"), ("PEINTURE AUTO", "industrie"),
        ("MACHINERIE", "industrie"), ("ACIER DU NORD", "industrie"),
        ("PIÈCES D'AUTO", "industrie"), ("SABLAGE AU JET", "industrie"),
        ("TRANSMISSION", "industrie"), ("DÉBOSSELAGE", "industrie"),
        ("SILENCIEUX", "industrie"), ("RADIATEURS", "industrie"),
        ("ENTREPÔT 7", "commerce"), ("PALETTES", "artisan"),
        ("BOIS DE SCIAGE", "artisan"), ("FERBLANTIER", "artisan"),
        ("LOCATION D'OUTILS", "artisan"), ("SALOPETTES", "mode"),
        ("CANTINE MOBILE", "bouffe"), ("CAFÉ DU MATIN", "bouffe"),
        ("TAVERNE LA SHOP", "nuit"), ("BOTTES DE TRAVAIL", "mode"),
    ),
    # Les Quais : le port. Tout sent le sel, meme la buanderie.
    "quais": (
        ("POISSONNERIE", "marine"), ("APPÂTS ET LIGNES", "marine"),
        ("CORDAGES", "marine"), ("TAVERNE DU PORT", "nuit"),
        ("CANTINE", "bouffe"), ("MOTEURS MARINS", "marine"),
        ("CHANTIER NAVAL", "marine"), ("GLACE ET SEL", "marine"),
        ("POISSON FRAIS", "marine"), ("FUMOIR", "marine"),
        # Les fruits de mer : ce que le port vend quand le poisson est parti.
        ("FRUITS DE MER", "marine"), ("HOMARD VIVANT", "marine"),
        ("CREVETTES", "marine"), ("HUÎTRES ET CIE", "marine"),
        ("CRABE DES NEIGES", "marine"), ("MOULES ET FRITES", "bouffe"),
        ("VOILERIE", "marine"), ("ACCASTILLAGE", "marine"),
        ("CAPITAINERIE", "marine"), ("LOCATION CHALOUPE", "marine"),
        ("DOUANES", "service"), ("BUANDERIE", "service"),
        ("BUREAU DE PAIE", "service"), ("TABAGIE DU PORT", "commerce"),
        ("BINERIE", "bouffe"), ("BOULANGERIE", "bouffe"),
        ("ÉPICERIE DU QUAI", "bouffe"), ("BAR LE MATELOT", "nuit"),
        ("HÔTEL DES QUAIS", "nuit"), ("CIRE ET HUILE", "industrie"),
        ("MISSION DU PORT", "sante"), ("BOTTES ET CIRES", "mode"),
    ),
    # La Pointe : le parc au bout de la ville. On y vient l'ete.
    "pointe": (
        ("LOCATION VÉLOS", "commerce"), ("CASSE-CROÛTE", "bouffe"),
        ("SOUVENIRS", "commerce"), ("CRÉMERIE", "bouffe"),
        ("CANTINE DU PARC", "bouffe"), ("PATATES FRITES", "bouffe"),
        ("DÉPANNEUR", "bouffe"), ("MOTEL LA POINTE", "nuit"),
        ("SALLE DE JEUX", "nuit"), ("ARTISANAT", "artisan"),
        ("PÊCHE ET CHASSE", "commerce"), ("PLANCHES", "commerce"),
        ("PHOTO SOUVENIR", "service"), ("CHALOUPES", "marine"),
        ("FRUITS DE MER", "marine"), ("CABANE À HOMARD", "marine"),
    ),
}

# --- Le standing -------------------------------------------------------------

#: ⚠️ **LE STANDING CHANGE L'ENSEIGNE** (des quartiers qu'on reconnait, 3e vague) :
#: la rue chic du Faubourg et le coin de la cour des Cravates sont du meme
#: district, et ne vendent pas la meme chose. `vitrines.monter_et_descendre`
#: RENOMME, sur la ville finie, les commerces d'un bloc cossu ou pauvre — un nom de
#: la meme famille (la piece derriere ne change pas) et qui tient dans le meme
#: bandeau (le mur ne change pas).
#: ⚠️ Un juge interdit une enseigne cossue dans un bloc pauvre, et l'inverse : la
#: BIJOUTERIE du catalogue du Faubourg se renomme si elle tombe en pauvre.
COMMERCES_COSSUS: tuple[tuple[str, str], ...] = (
    ("BIJOUTERIE", "commerce"), ("FLEURISTE", "commerce"), ("BISTRO", "bouffe"),
    ("GALERIE D'ART", "savoir"), ("TAILLEUR", "mode"), ("CHOCOLATIER", "bouffe"),
    ("BOUTIQUE DE VIN", "bouffe"), ("PARFUMERIE", "mode"), ("ANTIQUAIRE", "artisan"),
    ("FROMAGERIE", "bouffe"), ("SALON DE THÉ", "bouffe"), ("HAUTE COUTURE", "mode"),
    ("MAROQUINERIE", "mode"), ("ENCADREUR", "artisan"), ("TRAITEUR", "bouffe"),
    ("SPA", "service"),
)
COMMERCES_PAUVRES: tuple[tuple[str, str], ...] = (
    ("PRÊT SUR GAGES", "commerce"), ("CHÈQUES CASH", "service"), ("BINGO", "nuit"),
    ("DÉPANNEUR 24 H", "bouffe"), ("À LOUER", "commerce"), ("TOUT À 1 $", "commerce"),
    ("BRIC-À-BRAC", "commerce"), ("PRÊTS RAPIDES", "service"), ("VIDÉO POKER", "nuit"),
    ("LIQUIDATION", "commerce"), ("TATOUAGE", "mode"), ("BIÈRE ET VIN", "bouffe"),
)

#: Le local vide : ses vitrines sont TOUTES placardees, sa porte ne s'ouvre pas,
#: et sa vitrine ne s'allume pas la nuit. Une enseigne « A LOUER » derriere
#: laquelle on trouve un magasin meuble ment deux fois.
A_LOUER = "À LOUER"

#: La part des vitrines PLACARDEES d'une rue pauvre (le motif `B` des devantures).
PART_PLACARDEE = 1 / 3


# --- Les residences ---------------------------------------------------------

#: ⚠️ Un logement n'a pas d'enseigne : ce qui le fait lire, c'est la BRIQUE, les
#: ETAGES de fenetres et l'escalier de fer. Trois briques suffisent a casser la
#: rangee — au-dela, la rue perd son unite et chaque maison a l'air d'un
#: batiment public.
class Mur(TypedDict):
    slug: str
    brique: str
    joint: str
    cadre: str
    vitre: str
    allumee: str
    porte: str


MURS: list[Mur] = [
    {"slug": "brique_rouge", "brique": "#8c4a3c", "joint": "#6f392e", "cadre": "#d3c8b4",
     "vitre": "#3f4d5c", "allumee": "#ffd98a", "porte": "#4a2f1e"},
    {"slug": "brique_jaune", "brique": "#9a8352", "joint": "#7d6a41", "cadre": "#e0d8c2",
     "vitre": "#3a4653", "allumee": "#ffe0a0", "porte": "#3c3524"},
    {"slug": "bardeau_gris", "brique": "#6f7176", "joint": "#5b5d62", "cadre": "#c9ccd2",
     "vitre": "#36414d", "allumee": "#ffe6b8", "porte": "#2f3a44"},
]

#: Le fer des escaliers exterieurs et des balcons — le meme pour toute la ville.
#: ⚠️ Un escalier de couleur differente par maison ferait un decor de carton :
#: dans un vrai quartier, c'est le meme ferblantier qui les a tous poses.
FER = {"barreau": "#3d4348", "marche": "#8a8f94", "arete": "#adb2b6",
       "ombre": "rgba(0,0,0,0.35)"}


def mur(index: int) -> Mur:
    return MURS[index % len(MURS)]


#: A quelle distance (en tuiles) deux enseignes ont le droit de porter le meme
#: nom. ⚠️ Mesure sur l'ecran, pas au gout : la vue fait 26 tuiles de large, et
#: une rue se lit sur deux ecrans. En deca, on voit le doublon du meme
#: trottoir, et la ville a l'air d'une seule rue copiee-collee.
DISTANCE_DOUBLON = 40

#: Les lieux garantis (`carte.SPECIAUX`) : leur vrai nom est long (« Dépanneur
#: Chez Ti-Paul »), l'enseigne est courte. Un slug absent d'ici prend son nom.
ENSEIGNES: dict[str, tuple[str, str]] = {
    "terminus": ("TERMINUS", "service"),
    "armurerie": ("CHEZ GUS", "industrie"),
    "vetements": ("BOUTIQUE ROSA", "commerce"),
    "garage": ("GARAGE BANDINI", "industrie"),
    "poste": ("POLICE", "service"),
    "hopital": ("HÔPITAL", "service"),
    "bar": ("LE BROUILLARD", "nuit"),
    "casse_croute": ("CASSE-CROÛTE", "bouffe"),
    "depanneur": ("CHEZ TI-PAUL", "bouffe"),
    "hotel": ("HÔTEL BANDINI", "nuit"),
    "cantine": ("CANTINE", "bouffe"),
    "usine": ("USINE PRÉVOST", "industrie"),
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
    "TABARNAK", "LA VILLE DORT", "RIEN À FAIRE", "PAS DE JOBS",
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
        "murs": [dict(m) for m in MURS],
        "fer": dict(FER),
        "couleurs_tag": list(COULEURS_TAG),
        "motifs": list(MOTIFS),
    }
