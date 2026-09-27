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
        ("BARBIER GILLES", "service"), ("SALON LOUISE", "service"),
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
    # Le Petit-Canton (étape 2, 27 sept. 2026) : un quartier chinois de Baie-des-Brumes — des noms
    # français et des noms de famille cantonais en lettres latines (Martin : « bilingues »). ⚠️ Le
    # ton de la fiche : un quartier à ses habitants — restos, épiceries, herboriste, tailleur,
    # notaire —, jamais un décor de carton-pâte ; et l'école de kung-fu n'est PAS ici (étape 4).
    "canton": (
        ("JARDIN DE JADE", "bouffe"), ("DIM SUM LOTUS", "bouffe"),
        ("MARCHÉ KAM FUNG", "bouffe"), ("PÂTISSERIE WAH", "bouffe"),
        ("BOULANGER HUNG", "bouffe"), ("CANARD LAQUÉ", "bouffe"),
        ("NOUILLES WONG", "bouffe"), ("POISSONS LAM", "bouffe"),
        ("FRUITERIE TAM", "bouffe"), ("THÉ CHEZ YAN", "bouffe"),
        ("BBQ CANTONAIS", "bouffe"), ("TRAITEUR HO", "bouffe"),
        ("HERBORISTE CHAN", "sante"), ("ACUPUNCTURE LEE", "sante"),
        ("PHARMACIE TANG", "sante"), ("DENTISTE DR LO", "sante"),
        ("BARBIER WONG", "service"), ("COIFFURE JENNY", "service"),
        ("BUANDERIE SUN", "service"), ("NOTAIRE LEUNG", "service"),
        ("ASSOCIATION LI", "service"), ("STUDIO LAU", "service"),
        ("CAISSE POP", "service"), ("BIJOUX CHEUNG", "commerce"),
        ("RADIO-TV KWOK", "commerce"), ("LANTERNES FUNG", "commerce"),
        ("IMPORT YIP", "commerce"), ("CERFS-VOLANTS", "commerce"),
        ("FLEURISTE MEI", "commerce"), ("SOIERIE MEI", "mode"),
        ("TAILLEUR NG", "mode"), ("TISSUS ET SOIES", "mode"),
        ("LIBRAIRIE CHUNG", "savoir"), ("JOURNAUX YEE", "savoir"),
        ("FERRONNERIE YU", "artisan"), ("VAISSELLE CHOW", "artisan"),
        ("CLUB MAH-JONG", "nuit"), ("KARAOKÉ PERLE", "nuit"),
    ),
}

#: Les IDÉOGRAMMES des plaques verticales du Petit-Canton (Martin, 27 sept. 2026 : « avec idéogrammes
#: stylisés »). ⚠️ De VRAIS caractères, les plus simples qui soient, lisibles à cinq pixels sur cinq —
#: pas des traits au hasard qui « font chinois ». Une plaque en porte deux, empilés (`PAIRES`), tirés à la
#: POSITION de la devanture (`nord._ChantierNord`), sans dé.
IDEOGRAMMES: dict[str, tuple[str, ...]] = {
    "中": ("..#..", "#####", "#.#.#", "#####", "..#.."),
    "山": ("..#..", "#.#.#", "#.#.#", "#.#.#", "#####"),
    "大": ("..#..", "#####", "..#..", ".#.#.", "#...#"),
    "米": ("#.#.#", ".###.", "#####", ".###.", "#.#.#"),
    "日": (".###.", ".#.#.", ".###.", ".#.#.", ".###."),
    "月": (".###.", ".#.#.", ".###.", ".#.#.", "#..##"),
    "王": ("#####", "..#..", ".###.", "..#..", "#####"),
}
#: Les paires : Zhongshan (le nom de mille rues), le riz, le soleil et la lune, le grand roi.
PAIRES: tuple[str, ...] = ("中山", "大米", "日月", "大王")

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

# --- La taille ---------------------------------------------------------------

#: ⚠️ **LE COMMERCE A LA MESURE DE SON BATIMENT** (27 sept. 2026, Martin : « valide
#: la grandeur des batiments avec ce qu'il y a comme commerce, il faut que ce soit
#: logique »). Le nom etait tire sans regarder le mur : un HOTEL DES QUAIS dans 24
#: tuiles, un CHANTIER NAVAL dans 42, un TATOUAGE dans un hangar de 90. La taille se
#: lit en TUILES DE BATIMENT derriere la vitrine (la « part » de `carte`), bornes
#: comprises : un comptoir tient dans une boutique, une salle de quilles non.
TAILLES: dict[str, tuple[int, int]] = {
    "petit": (0, 49),
    "moyen": (0, 130),
    "grand": (60, 10 ** 6),
    # Ce qui va partout : un garage ou l'on rentre son char (sa place est choisie
    # par la baie, `poser_les_carrosseries` — un atelier d'une baie comme de six est
    # logique) et le local vide.
    "libre": (0, 10 ** 6),
}

#: La taille de chaque nom qui n'est pas `moyen` — un nom absent de la table est
#: moyen. ⚠️ Un nom neuf au catalogue se range ici s'il est une boutique ou une
#: grande salle : sinon il ira partout ou va un magasin ordinaire.
TAILLE_DU_NOM: dict[str, str] = {
    **{nom: "petit" for nom in (
        # Un comptoir, une chaise, une vitrine : la boutique de coin de rue.
        "TABAGIE DUBOIS", "BARBIER GILLES", "SALON LOUISE", "CORDONNERIE", "BIJOUTERIE",
        "PHOTO EXPRESS", "OPTICIEN", "TAILLEUR ROMÉO", "MERCERIE", "SERRURIER",
        "NOTAIRE BÉLIVEAU", "FLEURISTE ROSE", "NETTOYEUR", "COIFFURE LINE", "CRÉMERIE",
        "BEIGNES CHEZ TI", "COUTURE CHEZ EVA", "TAXI DIAMANT", "PHOTOGRAPHE", "DÉPANNEUR",
        "CASSE-CROÛTE", "CAFÉ DU MATIN", "CANTINE MOBILE", "APPÂTS ET LIGNES",
        "TABAGIE DU PORT", "HUÎTRES ET CIE", "SOUVENIRS", "PHOTO SOUVENIR", "PATATES FRITES",
        "CABANE À HOMARD",
        # Le cossu vend petit et cher ; le pauvre prete au guichet.
        "FLEURISTE", "TAILLEUR", "CHOCOLATIER", "PARFUMERIE", "ENCADREUR",
        "PRÊT SUR GAGES", "CHÈQUES CASH", "DÉPANNEUR 24 H", "PRÊTS RAPIDES", "TATOUAGE",
        "BIÈRE ET VIN", "VIDÉO POKER",
    )},
    **{nom: "grand" for nom in (
        # Une salle, un plancher de vente ou une cour : ca ne tient pas dans une boutique.
        "MEUBLES GAGNON", "CINÉMA RIALTO", "SALLE DE QUILLES", "BRASSERIE", "DISCO LE MIRAGE",
        "MARCHÉ BEAUDOIN", "BIBLIOTHÈQUE", "PÉPINIÈRE", "MACHINERIE", "ACIER DU NORD",
        "BOIS DE SCIAGE", "FERRAILLE", "ENTREPÔT 7", "PALETTES", "SABLAGE AU JET",
        "CHANTIER NAVAL", "HÔTEL DES QUAIS", "MOTEL LA POINTE", "QUILLES",
    )},
    **{nom: "libre" for nom in ("CARROSSERIE", "PEINTURE MINUTE", "PEINTURE AUTO", "LAVE-AUTO",
                                "À LOUER")},
}

#: ⚠️ **LA RESERVE** : des noms de chaque taille pour chaque famille, que SEUL
#: `vitrines.a_la_mesure` pioche, apres le standing et le catalogue du district. Sans
#: elle, La Shop n'a que deux noms de bouffe, petits tous les deux (CANTINE MOBILE,
#: CAFE DU MATIN), et une cantine tombee dans un entrepot de cent tuiles ne savait
#: pas quoi devenir (graine 1). ⚠️ Pas dans `COMMERCES` : un catalogue qui s'allonge
#: change le tirage de `choisir_enseigne`, et toute la ville change de noms.
#: Chaque famille a un nom de SEPT lettres au plus par taille : il tient sur un
#: bandeau de deux tuiles, le plus etroit qu'on pose.
RESERVE: dict[str, tuple[str, ...]] = {
    "bouffe": ("FRITES", "RESTO", "ÉPICERIE", "MARCHÉ", "SUPERMARCHÉ", "CONSERVERIE"),
    "service": ("BARBIER", "BUREAU", "DÉPÔT", "ENTREPOSAGE"),
    "artisan": ("VITRIER", "ATELIER", "SCIERIE", "MENUISERIE"),
    "nuit": ("BAR", "TAVERNE", "DANCING", "SALLE DE BAL"),
    "commerce": ("TABAGIE", "MAGASIN", "SURPLUS", "GROSSISTE"),
    "marine": ("APPÂTS", "MARINA", "CRIÉE", "CALE SÈCHE"),
    "industrie": ("SOUDURE", "MOTEURS", "USINAGE", "FONDERIE"),
    "sante": ("OPTIQUE", "DOCTEUR", "HOSPICE", "POLYCLINIQUE"),
    "mode": ("MODISTE", "HABITS", "TEXTILE", "MANUFACTURE"),
    "savoir": ("KIOSQUE", "LIVRES", "ÉCOLE", "ARCHIVES"),
}
TAILLE_DU_NOM.update({nom: "petit" for nom in (
    "FRITES", "BARBIER", "VITRIER", "BAR", "TABAGIE", "APPÂTS", "SOUDURE", "OPTIQUE", "MODISTE",
    "KIOSQUE")})
TAILLE_DU_NOM.update({nom: "grand" for nom in (
    "MARCHÉ", "SUPERMARCHÉ", "CONSERVERIE", "DÉPÔT", "ENTREPOSAGE", "SCIERIE", "MENUISERIE",
    "DANCING", "SALLE DE BAL", "SURPLUS", "GROSSISTE", "CRIÉE", "CALE SÈCHE", "USINAGE", "FONDERIE",
    "HOSPICE", "POLYCLINIQUE", "TEXTILE", "MANUFACTURE", "ÉCOLE", "ARCHIVES")})


def taille_du_nom(nom: str) -> str:
    return TAILLE_DU_NOM.get(nom, "moyen")


def a_sa_taille(nom: str, aire: int) -> bool:
    """Ce nom tient-il dans une part de batiment de `aire` tuiles ?"""
    bas, haut = TAILLES[taille_du_nom(nom)]
    return bas <= aire <= haut


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

#: Le bois a clin des maisons de pecheur — l'Ile-aux-Corneilles seulement.
#: ⚠️ Pas dans `MURS` : la ville tire son mur par `entier(0, len(MURS) - 1)`,
#: et une brique de plus changerait la couleur de toutes ses fenetres. Une maison
#: de l'ile se peint de planches sur toute sa facade, dans une couleur que le
#: plan lui DONNE (`ile.BATIMENTS`) : c'est un village de bord de mer, chaque
#: maison a la sienne, et aucune n'est la brique de la ville.
class Declin(TypedDict):
    slug: str
    planche: str
    ombre: str
    coin: str


DECLINS: list[Declin] = [
    {"slug": "rouge_grange", "planche": "#9b3b2e", "ombre": "#74291f", "coin": "#e8e0cf"},
    {"slug": "jaune_beurre", "planche": "#c9a64a", "ombre": "#9c7f33", "coin": "#f0ead8"},
    {"slug": "bleu_large", "planche": "#4d6f8c", "ombre": "#39536a", "coin": "#e6e4dc"},
    {"slug": "vert_sapin", "planche": "#4f7552", "ombre": "#3a583c", "coin": "#e6e2d2"},
    {"slug": "blanc_chaux", "planche": "#d8d3c4", "ombre": "#aba592", "coin": "#5d6b5a"},
]


def declin(slug: str) -> int:
    """L'index d'un bois a clin par son nom — c'est l'index qui voyage."""
    return next(i for i, d in enumerate(DECLINS) if d["slug"] == slug)


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
    # L'aérogare (`aeroport.py`) : posée à la main, sans dé, sur sa façade vitrée.
    "aeroport": ("AÉROPORT", "service"),
}

#: ⚠️ **LES CARROSSERIES** (des garages où l'on entre, 21 sept. 2026) : un atelier par
#: district, pose sur la ville FINIE (`carte._Chantier.poser_les_carrosseries`). On y rentre
#: le char et il ressort d'une autre couleur. L'enseigne, puis le nom du point sur la carte.
#: ⚠️ La Shop en avait DEJA une (« PEINTURE AUTO », au catalogue) qui ne menait nulle part :
#: c'est elle qu'on ouvre d'abord, si sa facade le permet.
CARROSSERIES: dict[str, tuple[str, str]] = {
    "faubourg": ("CARROSSERIE", "Carrosserie du Faubourg"),
    "erables": ("PEINTURE MINUTE", "Peinture Minute"),
    "shop": ("PEINTURE AUTO", "Peinture Auto"),
    "quais": ("CARROSSERIE", "Carrosserie du port"),
    "pointe": ("PEINTURE MINUTE", "Peinture Minute de La Pointe"),
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
        "declins": [dict(d) for d in DECLINS],
        "ideogrammes": {"glyphes": {k: list(v) for k, v in IDEOGRAMMES.items()}, "paires": list(PAIRES)},
        "fer": dict(FER),
        "couleurs_tag": list(COULEURS_TAG),
        "motifs": list(MOTIFS),
    }
