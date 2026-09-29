"""La ville s'agrandit au nord : les Friches, la place du Petit-Canton, la Gare de triage
(docs/jalons/la-ville-s-agrandit-au-nord.md).

Martin (26 sept. 2026) : « au nord, on décale », « comme le Faubourg », « du terrain vague et des voies
ferrées », et l'approche A — la bande est une DEUXIÈME VILLE, bâtie par le même chantier sur sa trame et sa
graine, puis collée au-dessus de la ville d'avant, qui descend de `DECALAGE_NORD` rangées sans qu'un tirage
bouge. `poser` est appelé EN TOUT DERNIER par `carte.generer`.

⚠️ LES MÊMES COLONNES que la ville : chaque rue nord-sud de la bande tombe en face d'une rue de la ville. Et
PAS DE RUE AU SUD : la dernière rue de la trame (6 de large) est le boulevard qui bordait la ville au nord ; on
la bâtit pour que les croisements s'y ouvrent, et on ne la colle pas.
"""

from __future__ import annotations

import copy
import zlib

from . import carte, casino, devantures

DECALAGE_NORD = 110
GRAINE_NORD = 20260926
RANGEES_NORD = (11, 11, 11, 12, 11, 11, 11)
RUES_H_NORD = (6, 4, 4, 6, 4, 4, 4, 6)           # la dernière : la couture, jamais collée
assert sum(RANGEES_NORD) + sum(RUES_H_NORD[:-1]) == DECALAGE_NORD

#: `z` friche, `b` terrain à bâtir, `v` la cour à scrap de la gare (c'étaient ses voies ferrées), `y` ses hangars :
#: des lettres de plan que seule la bande emploie
#: (`carte.USAGE_DU_PLAN` les connaît ; la ville d'avant n'en a aucune).
#: ⚠️ UN AGENT PAR DISTRICT, comme aux Érables et à La Shop : à `police: 0`, la police retirait ses autos
#: en entrant dans la bande — un refuge au bout de la rue (`test_police_js` l'a vu).
#: ⚠️ LES GANGS SONT CEUX DU VOISIN DU SUD, en attendant les Mantes (étape 4) : un district sans gang existe
#: (la baie), mais personne n'y marche — on n'ouvre pas ce chemin ici.
DISTRICTS_NORD: tuple[dict, ...] = (
    {"slug": "friches", "nom": "Les Friches", "bx": 0, "by": 0,
     "gang": "chevreuils", "gang_nom": "Les Chevreuils", "brume": False,
     "pietons": 4, "vehicules": 1, "police": 1, "rythme": (0.2, 1.0, 0.5), "rares": (),
     "plan": ("z<<<<", "^<<<<", "^<<<<", "z<<<<", "^<<<<", "^<<<<", "^<<<<"),
     "standing": ("-----",) * 7},
    # ⚠️ LE PETIT-CANTON, ÉTAPE 2 (27 sept. 2026) : ses terrains à bâtir sont bâtis. Martin : « rue principale
    # + place » — la rue commerçante descend entre la 4e et la 5e colonne d'îlots jusqu'à la couture (c'est là
    # que l'arche l'ouvrira, vague B), des logements tout autour, et la place du marché au cœur, sur la rue.
    # ⚠️ Chaque îlot du quartier se bâtit avec SES dés (`_ChantierNord._a_ses_des`) : les Friches et la Gare
    # gardent leurs tirages à l'unité près.
    {"slug": "canton", "nom": "Le Petit-Canton", "bx": 5, "by": 0,
     "gang": "cravates", "gang_nom": "Les Cravates", "brume": False,
     "pietons": 16, "vehicules": 5, "police": 1, "rythme": (0.3, 1.0, 0.9), "rares": (),
     "plan": ("hhhcchhh",
              "hhccchhh",
              "hhcc¤<hh",                   # le casino du Dragon d'or, au nord de la place (`casino.py`)
              "hhcco<hh",
              "hhccchhh",
              "hhhccchh",
              "hhhcchhh"),
     "standing": ("-==++==-",
                  "-=+++==-",
                  "==++++==",
                  "==++++==",
                  "-=+++==-",
                  "-==++=--",
                  "--=++=--")},
    # ⚠️ LE BIDONVILLE DE LA GARE (28 sept. 2026). Martin : « dans le quartier des trains, je veux plus un
    # bidonville et des maisons pauvres pour la partie est ». Les voies gardent les quatre colonnes de l'ouest
    # (le poste d'aiguillage ne bouge pas ; le soir même, la cour à scrap et le bureau du ferrailleur les
    # remplacent) et les hangars le sud ; à l'est, le bidonville (`t`) sur trois
    # rangées, un seul lot, et dessous deux rangées de maisons pauvres (`h`, standing `-`).
    # ⚠️ Ses îlots neufs se bâtissent avec LEURS dés (`_ChantierNord._a_ses_des`), comme le Petit-Canton.
    {"slug": "gare", "nom": "La Gare de triage", "bx": 13, "by": 0,
     "gang": "boulonneux", "gang_nom": "Les Boulonneux", "brume": False,
     "pietons": 9, "vehicules": 3, "police": 1, "rythme": (0.3, 1.0, 0.8), "rares": (),
     "plan": ("v<<<t<<",
              "^<<<^<<",
              "^<<<^<<",
              "^<<<hhh",
              "^<<<hhh",
              "y<y<y<y",
              "^<^<^<^"),
     "standing": ("-------",) * 7},
)
PLAN_NORD: tuple[str, ...] = carte._assembler(DISTRICTS_NORD)
TRAME_NORD = {"colonnes": carte.COLONNES, "rangees": RANGEES_NORD, "rues_v": carte.RUES_V,
              "rues_h": RUES_H_NORD, "districts": DISTRICTS_NORD, "ponts": frozenset(),
              "standing": carte._assembler_le_standing(DISTRICTS_NORD, PLAN_NORD)}


def district(slug: str) -> dict:
    return next(d for d in DISTRICTS_NORD if d["slug"] == slug)


# --- Les trois bâtisseurs --------------------------------------------------------------------

#: Le bureau du ferrailleur, à l'entrée de la cour à scrap (28 sept. 2026 ; c'était le poste d'aiguillage) : le
#: comptoir où l'on pèse et paie, le classeur des reçus qu'on fouille, l'étagère des pièces, la chaise et le poêle.
#: ⚠️ À LA MESURE DE SON BÂTIMENT (cinq sur quatre dedans, comme dehors) : `test_carte` le tient pour toute
#: la ville. Une porte de MAISON : personne au comptoir, il n'y en a pas.
PIECE_FERRAILLEUR = carte._piece("nord_ferrailleur", "Le bureau du ferrailleur", porte="maison", plan="""
BBWWWBB
Bcc  kB
B     B
Bh   zB
Be    B
BBBDBBB
""", points=(carte._pt("fouiller", 4, 1),))
BUREAU = {"slug": "nord_ferrailleur", "nom": "Le bureau du ferrailleur", "interieur": "nord_ferrailleur",
          "famille": "repere", "genre": "industriel"}

#: Ce qu'on a laissé rouiller dans les Friches, et ce qui y a poussé tout seul.
EPAVES = ("carcasse", "carcasse", "cabanon", "pneu", "baril", "caddie", "arbre", "arbre", "buisson", "buisson")


def _terrain_vague(ch, x, y, largeur, hauteur):
    """Un terrain vague de la bande : terre sèche, les déchets de la ville (`carte.DECHETS`), et un grillage en
    U — ouvert au nord, une trouée de deux tuiles au MILIEU du côté sud. ⚠️ Pas `_Chantier._terrain_vague` :
    sa trouée peut tomber contre un coin (le côté ouest reste alors une barre qui ne tourne jamais,
    `test_carte`), et le corriger là changerait les tirages de toute la ville d'avant."""
    ch.rect(x, y, largeur, hauteur, ";")
    for j in range(1, hauteur):
        ch.sol[y + j][x] = carte.GRILLAGE
        ch.sol[y + j][x + largeur - 1] = carte.GRILLAGE
    milieu = x + largeur // 2
    # ⚠️ UNE tuile de trouée sous six de large : deux, dans un lot de cinq (le Petit-Canton en a), touchent
    # forcément un coin, et le côté ne tourne plus (`test_carte`). Les lots des Friches font plus de six.
    trouee = 2 if largeur >= 6 else 1
    for i in range(largeur):
        if not milieu - trouee + 1 <= x + i <= milieu:
            ch.sol[y + hauteur - 1][x + i] = carte.GRILLAGE
    for _ in range(max(2, largeur * hauteur // 10)):
        ch.poser_decor(ch.des.choix(carte.DECHETS), x + ch.des.entier(1, largeur - 2),
                       y + ch.des.entier(0, hauteur - 2))


def _friche(ch, x, y, largeur, hauteur):
    """Des herbes hautes, un sentier de gravier en croix, et dans chaque quart UN terrain vague (terre sèche,
    grillage en U, déchets), de taille modeste ; autour, des épaves, des
    arbres et des buissons. Les dés sont ceux de la BANDE (`GRAINE_NORD`) : la ville d'avant n'en perd pas un.
    ⚠️ Un usage INDUSTRIEL (`carte.USAGE_DU_PLAN["z"]`), pas un parc : ce n'est pas un parc de quartier
    (ni allées continues, ni obligation d'arbres), et de la terre sèche dans un parc est un défaut jugé."""
    ch.rect(x, y, largeur, hauteur, ",")
    mx, my = x + largeur // 2, y + hauteur // 2
    ch.rect(x, my, largeur, 1, "g")                      # le sentier est-ouest
    ch.rect(mx, y, 1, hauteur, "g")                      # et le nord-sud
    for qx0, qx1 in ((x + 2, mx - 2), (mx + 3, x + largeur - 2)):
        for qy0, qy1 in ((y + 2, my - 2), (my + 3, y + hauteur - 2)):
            ql, qh = min(14, qx1 - qx0), min(8, qy1 - qy0)
            if ql > 6 and qh > 5:
                _terrain_vague(ch, qx0 + (qx1 - qx0 - ql) // 2, qy0 + (qy1 - qy0 - qh) // 2, ql, qh)
    for _ in range(max(10, largeur * hauteur // 90)):
        quoi = ch.des.choix(EPAVES)
        ch.poser_decor(quoi, x + ch.des.entier(1, largeur - 2), y + ch.des.entier(1, hauteur - 2))


def _terrain_a_batir(ch, x, y, largeur, hauteur):
    """Un grillage de chantier tout autour, ouvert au sud ; du gravier dedans ; la pancarte « À BÂTIR » devant
    l'entrée. ⚠️ En attendant le Petit-Canton (étape 2), qui y posera ses bâtiments sans toucher ses rues.
    ⚠️ Du GRILLAGE, pas de la palissade de bois : le bois est l'image de la banlieue (`test_carte`)."""
    ch.rect(x, y, largeur, hauteur, "g")
    ch.clore(x, y, largeur, hauteur, carte.GRILLAGE, cote_ouvert="S", ouverture=2)
    ch.poser_decor("pancarte_a_batir", x + largeur // 2 + 1, y + hauteur)


#: Ce qui s'empile dans les rangées de la cour à scrap, à poids : des chars surtout, puis des cubes de
#: ferraille compactée et des pneus. ⚠️ UNE PILE PAR TROIS TUILES, pas une carcasse par tuile : la carte n'a
#: que quelques centaines d'octets gzip sous son plafond (`test_definitions`), et chaque décor en coûte.
PILES_DE_SCRAP = ("pile_de_carcasses", "pile_de_carcasses", "pile_de_carcasses", "cubes_de_ferraille",
                  "cubes_de_ferraille", "tas_de_pneus")
#: Le pas d'une pile dans sa rangée (tuiles), et celui des rangées : une rangée, puis trois tuiles d'allée.
PAS_PILE, PAS_RANGEE = 3, 4


def _empreinte(*n: int) -> int:
    """Un tirage À LA POSITION, sans dé (`crc32`, pas `hash` : celui des chaînes change d'un processus à
    l'autre) : la cour se bâtit pareil à chaque génération et ne prend rien aux dés de la bande."""
    return zlib.crc32(",".join(map(str, n)).encode())


def _cour_a_scrap(ch, x, y, largeur, hauteur):
    """La cour à scrap des Boulonneux (docs/jalons/la-cour-a-scrap-de-la-gare.md) : l'ouest de la Gare de triage.

    Martin (28 sept. 2026) : « je n'aime pas la partie avec les morceaux de train » — des wagons de 6 × 1 posés
    sur des voies tous les trois rangs, d'un bord à l'autre. Il en reste UNE voie, rouillée, au nord ; dessous,
    une cour de barbelé : des rangées de piles (carcasses, cubes, pneus) entre des allées de trois tuiles, une
    allée maîtresse du portail jusqu'au fond, une allée en travers et la grue à aimant sur sa place. Le bureau
    du ferrailleur garde la place du poste d'aiguillage, au coin sud-ouest, sa porte au sud.

    ⚠️ Les piles se tirent À LA POSITION (`_empreinte`) ; la clôture tire dans les dés de la gare
    (`_ChantierNord._a_ses_des`), qui rend ceux de la bande intacts : les hangars n'ont pas bougé d'une palette.
    ⚠️ Une TROUÉE DANS CHAQUE RANGÉE entre deux allées : sans elle, une allée ne se rejoint que par ses bouts.
    """
    ch.rect(x, y, largeur, hauteur, ",")
    ch.rect(x, y, largeur, 1, "T")                        # la voie qui reste
    px, py = x + 2, y + hauteur - 6
    ch.rect(px - 1, py - 1, 7, 7, ",")                   # le bureau a son terrain
    ch.rect(px, py, 5, 3, "O")                           # 5 × 4 avec sa façade : sa pièce en a autant
    facades = [(px + i, py + 3) for i in range(5)]
    for fx, fy in facades:
        ch.sol[fy][fx] = "F"
    ch.rect(px, py + 4, 5, 1, ".")
    ch.poser_porte(facades, special=BUREAU)

    # La cour : de la voie (deux rangs d'herbe) jusqu'au-dessus du terrain du bureau.
    cx, cy, cl, cht = x + 1, y + 3, largeur - 2, hauteur - 11
    portail = px + 8 - cx                                # quatre tuiles, juste à l'est du bureau
    ch.rect(cx, cy, cl, cht, ";")
    ch.clore(cx, cy, cl, cht, carte.BARBELE, cote_ouvert="S", ouverture=4, depart=portail)
    gx = cx + portail
    ch.rect(gx, cy + cht - 1, 4, y + hauteur - (cy + cht - 1), "g")   # du portail à la rue
    ix, iy, il, ih = cx + 2, cy + 2, cl - 4, cht - 4     # une allée de ronde le long du barbelé
    ch.rect(gx, iy, 4, ih, "g")                          # l'allée maîtresse
    travers = iy + (ih // 2 // PAS_RANGEE) * PAS_RANGEE + 1
    ch.rect(ix, travers, il, 3, "g")                     # l'allée en travers
    grue_x = ix + il * 2 // 3
    ch.rect(grue_x - 4, travers - 3, 9, 9, "g")          # la place de la grue
    libre = {(gx + i, j) for i in range(-1, 5) for j in range(iy, iy + ih)}
    libre |= {(i, travers + j) for i in range(ix, ix + il) for j in range(-1, 4)}
    libre |= {(grue_x + i, travers + j) for i in range(-5, 6) for j in range(-4, 7)}
    ch.poser_decor("grue_aimant", grue_x, travers + 1)
    for ry in range(iy + PAS_RANGEE - 1, iy + ih - 1, PAS_RANGEE):
        # La trouée de la rangée : trois tuiles, une par segment de part et d'autre de l'allée maîtresse.
        for x0, x1 in ((ix, gx - 1), (gx + 5, ix + il)):
            if x1 - x0 < 2 * PAS_PILE:
                continue
            trou = x0 + PAS_PILE + _empreinte(x0, ry) % max(1, x1 - x0 - 2 * PAS_PILE)
            for px_ in range(x0, x1 - PAS_PILE + 1, PAS_PILE):
                if (px_, ry) in libre or any((px_ + k, ry) in libre for k in (1, 2)):
                    continue
                if trou - PAS_PILE < px_ <= trou + 1:
                    continue
                quoi = PILES_DE_SCRAP[_empreinte(px_, ry, 7) % len(PILES_DE_SCRAP)]
                ch.poser_decor(quoi, px_ + 1, ry)


def _hangars(ch, x, y, largeur, hauteur):
    """Les hangars de tôle de la gare : un long toit, une façade aveugle et ses portes CONDAMNÉES (`d`), des
    palettes et des barils autour. ⚠️ Pas un îlot de la ville : ceux-là bâtissent des devantures, et la gare
    n'a qu'une pièce, le bureau du ferrailleur (une clinique et une disco poussaient entre les wagons)."""
    ch.rect(x, y, largeur, hauteur, ",")
    hx, hy, hl, hh = x + 2, y + 2, largeur - 4, hauteur - 6
    if hl < 6 or hh < 4:
        return
    ch.rect(hx, hy, hl, hh - 1, "B")
    ch.rect(hx, hy + hh - 1, hl, 1, "F")
    for i in range(3, hl - 2, 7):
        ch.sol[hy + hh - 1][hx + i] = "d"
    # ⚠️ RIEN DEVANT LES PORTES, même condamnées (`test_devants`, `test_carte`) : les palettes et les
    # barils vont sur les côtés du hangar, jamais au pied de sa façade.
    for dx in (0, 1, largeur - 2, largeur - 1):
        ch.poser_decor(ch.des.choix(("palettes", "baril", "caisse")), x + dx, hy + ch.des.entier(0, hh - 2))


#: Ce qui traîne entre les cabanes du bidonville : le linge qui sèche, ce qu'on a rapporté, ce qu'on n'a pas jeté.
#: ⚠️ Une liste A POIDS, comme `carte.DECHETS` : du linge et des sacs d'abord, une carcasse de temps en temps.
BRIC_A_BRAC = ("corde_a_linge", "corde_a_linge", "matelas", "caddie", "pneu", "pneu", "palettes",
               "ordures", "ordures", "debris", "debris", "poubelle_pleine", "caisse", "carcasse")
#: Ce qui tient la tôle d'une cabane, vu d'en haut (`sprites.js`, `TOITURES`) : des pneus, une bâche, une pièce.
SUR_LA_TOLE = ("pneus", "pneus", "bache", "bache", "tole")
#: Le baril où l'on fait du feu : sa lueur, la nuit (`monde.js`, `SORTES_DE_LAMPE.feu`).
FEU_RAYON = 22


def _entre(ch, a: int, b: int) -> int:
    """Entre a et b, bornes comprises, par les bits FORTS du dé. ⚠️ `Des.entier` prend le reste de l'état d'un
    LCG, dont les bits faibles alternent : deux tirages de parité à la suite sont liés, et toutes les cabanes
    d'une rangée finissaient leur façade sur la même ligne."""
    return a + int(ch.des.flottant() * (b - a + 1))


def _parmi(ch, options):
    return options[_entre(ch, 0, len(options) - 1)]


def _bidonville(ch, x, y, largeur, hauteur):
    """Le bidonville de la gare : des cabanes de tôle serrées sur de la terre battue, en rangées qui ne
    s'alignent jamais, trois tuiles d'allée devant chaque rangée ; une porte condamnée (`d`) à chaque cabane
    — on n'y entre pas —, des pneus et des bâches sur la tôle, du linge et du bric-à-brac entre elles, et
    des barils où brûle un feu, qui éclairent la nuit.

    ⚠️ RIEN DEVANT UNE PORTE (`devants.DEVANT`, `test_devants`) : chaque cabane réserve le devant de la
    sienne avant qu'on sème quoi que ce soit, et une rangée laisse `DEVANT_PROFONDEUR` tuiles d'allée
    sous ses façades. ⚠️ Bâti avec SES dés (`_ChantierNord._a_ses_des`) : la bande n'en perd pas un."""
    from . import devants as devants_mod
    ch.rect(x, y, largeur, hauteur, ";")
    allee = devants_mod.DEVANT_PROFONDEUR
    interdit: set[tuple[int, int]] = set()
    cours: list[tuple[int, int]] = []                    # les trous laissés dans les rangées
    # Une rangée : des cabanes de hauteur et de recul inégaux (jamais un alignement de lotissement) ; la
    # suivante commence sous la plus basse façade, plus l'allée.
    cy = y + 1
    while cy + 2 + allee <= y + hauteur:
        bas = cy
        cx = x + 1 + _entre(ch, 0, 2)
        while cx + 3 <= x + largeur - 1:
            large = min(_entre(ch, 3, 5), x + largeur - 1 - cx)
            if large < 3:
                break
            recul, haut = _entre(ch, 0, 1), _entre(ch, 2, 3)       # la tôle, puis la façade
            # La rangée du bas : deux tuiles d'allée, et l'accotement de la rue fait la troisième.
            haut = min(haut, y + hauteur - allee - cy - recul)
            if haut < 2 or ch.des.chance(0.1):
                cours.append((cx + large // 2, cy + 1))
            else:
                _cabane(ch, cx, cy + recul, large, haut, interdit)
                bas = max(bas, cy + recul + haut)
            cx += large + (2 if ch.des.chance(0.3) else 1)                # serrées : une tuile, parfois deux
        cy = bas + 1 + allee
    # Le feu : un baril par cour, et quelques-uns dans les allées.
    feux = cours + [(x + _entre(ch, 2, largeur - 3), y + _entre(ch, 2, hauteur - 3))
                    for _ in range(max(3, largeur * hauteur // 250))]
    for fx, fy in feux:
        if (fx, fy) not in interdit and ch.poser_decor("baril_feu", fx, fy):
            ch.lampes.append({"x": fx, "y": fy, "r": FEU_RAYON, "c": "feu"})
    for _ in range(largeur * hauteur // 18):
        bx, by = x + _entre(ch, 1, largeur - 2), y + _entre(ch, 1, hauteur - 2)
        quoi = _parmi(ch, BRIC_A_BRAC)
        if (bx, by) not in interdit:
            ch.poser_decor(quoi, bx, by)


def _cabane(ch, x, y, largeur, haut, interdit):
    """Une cabane : `haut` rangées de tôle rapiécée (`{`), un mur de planches dessous (`}`) et sa porte — un
    `d`, un logement —, un ou deux objets sur la tôle. Le devant de la porte va dans `interdit`."""
    from . import devants as devants_mod
    ch.rect(x, y, largeur, haut, "{")
    fy = y + haut
    ch.rect(x, fy, largeur, 1, "}")
    porte = x + _entre(ch, 1, largeur - 2)
    ch.sol[fy][porte] = "d"
    interdit.update((porte + dx, fy + dy) for dx, dy in devants_mod.DEVANT)
    # ⚠️ Jamais deux collés (`test_carte`, le juge des toits) : deux objets l'un contre l'autre font une tache.
    poses: list[tuple[int, int]] = []
    for _ in range(_entre(ch, 1, 2)):
        tx, ty, quoi = x + _entre(ch, 0, largeur - 1), y + _entre(ch, 0, haut - 1), _parmi(ch, SUR_LA_TOLE)
        if all(max(abs(tx - a), abs(ty - b)) > 1 for a, b in poses):
            poses.append((tx, ty))
            ch.toits.append({"x": tx, "y": ty, "type": quoi})


#: Combien de choses traînent au pied des murs d'un îlot de maisons pauvres de la gare, par cent tuiles.
#: ⚠️ Peu : Martin a renvoyé « trop de saleté partout » le 16 sept. 2026 (`salete.py`). Ce qu'on veut, c'est
#: que la rue se LISE pauvre en y entrant, pas un dépotoir.
SALETE_PAR_CENT_TUILES = 2


def _salir_les_maisons(ch, x, y, largeur, hauteur):
    """Ce que `salete.deplacer` pose au pied des murs pauvres de la ville d'avant — il passe avant que la bande
    se colle, et ne l'a jamais vue : des sacs, des gravats, un matelas, un caddie, contre un mur, jamais devant
    une porte ni à moins de `salete.ECART_DECHET` l'un de l'autre. Et la poubelle y déborde."""
    from . import devants as devants_mod, salete as salete_mod
    portes = {(i, j) for j in range(y, y + hauteur) for i in range(x, x + largeur)
              if ch.sol[j][i] in carte.PORTES_DE_FACADE}
    portes |= {(r["x"] + i, r["y"]) for r in ch.residences for i, m in enumerate(r["motifs"]) if m == "P"}
    interdit = {(px + dx, py + dy) for px, py in portes for dx, dy in devants_mod.DEVANT}
    poses: list[tuple[int, int]] = []
    for _ in range(largeur * hauteur * SALETE_PAR_CENT_TUILES // 100 * 4):
        if len(poses) >= largeur * hauteur * SALETE_PAR_CENT_TUILES // 100:
            break
        tx, ty = x + _entre(ch, 0, largeur - 1), y + _entre(ch, 0, hauteur - 1)
        quoi = _parmi(ch, salete_mod.AU_PIED_DES_MURS)
        if ((tx, ty) in interdit or not salete_mod._contre_un_mur(ch, tx, ty)
                or any(abs(tx - a) + abs(ty - b) < salete_mod.ECART_DECHET for a, b in poses)):
            continue
        if ch.poser_decor(quoi, tx, ty):
            poses.append((tx, ty))
    for d in ch.decor:
        if d["type"] == "poubelle" and x <= d["x"] < x + largeur and y <= d["y"] < y + hauteur:
            d["type"] = "poubelle_pleine"


#: La graine du Petit-Canton : chaque îlot en tire la sienne, mêlée à sa position (`_a_ses_des`).
GRAINE_CANTON = 20260927
#: Celle des îlots neufs de la gare, le bidonville et ses maisons pauvres (`_a_ses_des`).
GRAINE_GARE = 20260928
#: Les districts de la bande dont chaque îlot bâti tire SES dés, et la graine qu'ils mêlent à sa position.
GRAINES_A_PART = {"canton": GRAINE_CANTON, "gare": GRAINE_GARE}


class _ChantierNord(carte._Chantier):
    BATISSEURS = {"z": _friche, "b": _terrain_a_batir, "y": _hangars,
                  "v": lambda ch, x, y, large, h: ch._a_ses_des(x, y, lambda: _cour_a_scrap(ch, x, y, large, h)),
                  "t": lambda ch, x, y, large, h: ch._a_ses_des(x, y, lambda: _bidonville(ch, x, y, large, h)),
                  casino.CASINO_DU_PLAN: casino.batir}
    A_ABORD = carte._Chantier.A_ABORD | {"b", casino.CASINO_DU_PLAN}

    def _a_ses_des(self, x: int, y: int, batir) -> None:
        """Bâtit un îlot du Petit-Canton avec SES dés, puis rend ceux de la bande tels qu'il les a trouvés.

        ⚠️ C'est ce qui laisse les Friches et la Gare à l'unité près : bâtis avec les dés de la bande, les
        56 îlots du quartier en auraient mangé des milliers, et tout ce qui se tire après eux — les
        épaves, les hangars, les lampadaires — aurait changé de place. Tous les flux du chantier
        (`des`, `des_devanture`, `des_toit`…) sont remplacés le temps de l'îlot : chacun par un dé
        neuf, de la graine du quartier mêlée à la position de l'îlot et au NOM du flux (`crc32`, pas
        `hash` : celui des chaînes change d'un processus à l'autre).
        """
        district = self.district_en(x, y)
        graine = GRAINES_A_PART[district]
        flux = {k: v for k, v in vars(self).items() if isinstance(v, carte.Des)}
        for nom in flux:
            setattr(self, nom, carte.Des(graine ^ (x * 7919 + y * 104729) ^ zlib.crc32(nom.encode())))
        avant = len(self.devantures)
        try:
            batir()
        finally:
            for nom, d in flux.items():
                setattr(self, nom, d)
        # La plaque verticale de chaque commerce du quartier : deux idéogrammes (`devantures.PAIRES`),
        # choisis à la POSITION de la devanture — aucun dé.
        for d in (self.devantures[avant:] if district == "canton" else ()):
            d["ideo"] = zlib.crc32(f"{d['x']},{d['y']}".encode()) % len(devantures.PAIRES)

    def _ilot_bati(self, x, y, largeur, hauteur, **options):
        district = self.district_en(x, y)
        if district not in GRAINES_A_PART:
            return super()._ilot_bati(x, y, largeur, hauteur, **options)

        def batir():
            super(_ChantierNord, self)._ilot_bati(x, y, largeur, hauteur, **options)
            if district == "gare":                   # les maisons pauvres de l'est (le bidonville)
                _salir_les_maisons(self, x, y, largeur, hauteur)
        return self._a_ses_des(x, y, batir)

    def poser_la_piece(self, famille, part, ancre, *args, **options):
        """⚠️ À LA GARE, ON N'ENTRE PAS : ni dans une cabane du bidonville, ni dans ses maisons pauvres — la
        seule pièce de la gare reste le bureau du ferrailleur. Pas un choix de décor seulement : le logement
        visitable se décide sur un état commun à toute la bande (`premiere_du_genre`, le compteur `visites`),
        et le Petit-Canton décidait alors quelles portes de la gare s'ouvraient (`test_canton`, le témoin)."""
        if self.district_en(*ancre) == "gare":
            return None
        return super().poser_la_piece(famille, part, ancre, *args, **options)

    def bornes(self):
        """Les bornes-fontaines de la bande : la règle de la ville, mais UN DÉ PAR CROISEMENT, tiré de sa position.

        ⚠️ La ville tire un dé par croisement, à la file : fusionner deux îlots du Petit-Canton (le casino du
        Dragon d'or) retire un bout de rue, donc un croisement, et toutes les bornes de la bande glissaient d'un
        cran jusqu'à la Gare (`test_canton`, la bande ne bouge pas). Tiré à la position, un croisement de plus
        ou de moins ne touche que le sien.
        """
        # ⚠️ La boucle de `carte._Chantier.bornes`, recopiée : on ne peut pas lui passer un croisement à la fois,
        # ses coins réservés aux feux se calculent sur TOUS les croisements.
        reserves = self._coins_reserves_aux_feux()
        for inter in self.intersections:
            de = carte.Des(GRAINE_NORD ^ (inter["x"] * 7919 + inter["y"] * 104729) ^ zlib.crc32(b"borne"))
            if not de.chance(0.30):
                continue
            x, y = inter["x"] + inter["l"], inter["y"] - 1
            for dy in (-1, -2, 1):
                cx, cy = x, y + dy
                if (cx, cy) in reserves:
                    continue
                if 0 <= cx < self.largeur and 0 <= cy < self.hauteur and self.sol[cy][cx] == ".":
                    if self.poser_decor("borne_fontaine", cx, cy):
                        break

    def _terrain_vague(self, x, y, largeur, hauteur):
        """Un lot abandonné du Petit-Canton : celui de la bande (`_terrain_vague`, sa trouée au MILIEU du côté
        sud), pas celui de la ville, dont la trouée peut tomber contre un coin et laisser une clôture droite
        qui ne tourne jamais (`test_carte` l'a vu deux fois au quartier)."""
        if self.district_en(x, y) != "canton":
            return super()._terrain_vague(x, y, largeur, hauteur)
        return _terrain_vague(self, x, y, largeur, hauteur)

    def _place(self, x, y, largeur, hauteur):
        if self.district_en(x, y) != "canton":
            return super()._place(x, y, largeur, hauteur)
        return self._a_ses_des(x, y, lambda: super(_ChantierNord, self)._place(x, y, largeur, hauteur))


def batir_la_bande() -> _ChantierNord:
    """La bande, bâtie à part : 419 × 116 (ses rangées 110 à 115 sont le boulevard de la couture)."""
    ch = _ChantierNord(PLAN_NORD, GRAINE_NORD, trame=TRAME_NORD)
    # ⚠️ LA SALLE DU CASINO AVANT DE BÂTIR : son bâtiment se taille à elle (`_ilot_bati` lit ses mesures dans
    # les pièces du chantier), et une pièce inconnue donnait un casino de trois tuiles sur trois.
    ch.pieces[casino.PIECE["slug"]] = casino.PIECE
    for etape in ("eaux", "rues", "croisements", "ilots", "ponts", "lampadaires", "bornes"):
        getattr(ch, etape)()
    ch.pieces["nord_ferrailleur"] = PIECE_FERRAILLEUR
    # ⚠️ LE STANDING DES LOGEMENTS : `vitrines.monter_et_descendre` le marque, mais pour la ville d'avant
    # seulement. Sans lui, les maisons pauvres de la gare n'avaient ni fer rouillé ni planches — des maisons
    # ordinaires dans un quartier écrit `-`. Les devantures, elles, gardent leurs noms (le Petit-Canton a les
    # siens, `devantures.COMMERCES["canton"]`).
    for r in ch.residences:
        standing = ch.standing_en(r["x"], r["y"])
        if standing in carte.STANDING_LETTRE:
            r["standing"] = carte.STANDING_LETTRE[standing]
    # ⚠️ UNE FOIS : `feux_pietons` réserve ses tuiles (`occupe`) et un deuxième appel n'en rend plus
    # aucun ; or la bande est gardée pour tout le processus (`_bande`).
    ch.feux_nord = ch.feux_pietons()
    # ⚠️ LES NOMS DE LA BANDE : `logement_1` existe déjà en ville.
    renomme = {k: (k if k.startswith("nord_") else "nord_" + k) for k in ch.pieces}
    # ⚠️ ET CE QUE LES PIÈCES SE DISENT ENTRE ELLES : le `slug` de chacune, et le `vers` de ses escaliers.
    # Oubliés, un logement à étage du Petit-Canton montait à l'étage de `logement_27` de la VILLE D'AVANT
    # — un 7 × 5 au-dessus d'une cabane de 3 × 3 (`test_carte`, la pièce à la mesure de son bâtiment).
    pieces = {}
    for k, v in ch.pieces.items():
        v = dict(v, slug=renomme.get(v.get("slug", k), v.get("slug", k)))
        v["points"] = [dict(pt, vers=renomme.get(pt["vers"], pt["vers"])) if pt.get("vers") else pt
                       for pt in v.get("points", [])]
        pieces[renomme[k]] = v
    ch.pieces = pieces
    for p in ch.portes:
        p["interieur"] = renomme.get(p["interieur"], p["interieur"])
        p["lieu"] = renomme.get(p["lieu"], "nord_" + p["lieu"] if not p["lieu"].startswith("nord_") else p["lieu"])
    return ch


# --- La translation : toute la ville descend de `DECALAGE_NORD` rangées ------------------------------
#
# ⚠️ UNE ENTRÉE PAR CLÉ DE LA CARTE, et une clé inconnue LÈVE : une autre session qui ajoute une clé à
# `carte.generer` doit dire ici comment elle descend, sinon elle resterait 110 rangées trop haut, en silence.
# Les objets `{x, y}` descendent par `_y` (à toute profondeur) ; les PAIRES `[x, y]` et les tuples ont
# chacune leur fonction, qui dit l'index du y — lu dans le module qui les produit.

PX = carte.TUILE_PX

#: ⚠️ UN OBJET NE DESCEND QU'UNE FOIS : la ville PARTAGE des objets entre ses listes (les amarrages de l'île
#: sont aussi dans `amarrages`) ; les décaler deux fois les poserait 220 rangées plus bas. `decaler` vide ce
#: registre à chaque appel, et chaque objet ou paire décalé y inscrit son `id`.
_VUS: set[int] = set()


def _une_fois(o) -> bool:
    if id(o) in _VUS:
        return False
    _VUS.add(id(o))
    return True


def _y(o, n):
    """Tout entier sous une clé `y`, à toute profondeur."""
    if isinstance(o, dict):
        if not _une_fois(o):
            return
        for k, v in o.items():
            if k == "y" and isinstance(v, int):
                o[k] = v + n
            else:
                _y(v, n)
    elif isinstance(o, list):
        for v in o:
            _y(v, n)


def _paire(p, n, i=1):
    if _une_fois(p):
        p[i] += n


def _paires(liste, n, i=1):
    for p in liste or ():
        _paire(p, n, i)


def _rien(v, n):
    pass


def _aeroport(a, n):
    _y(a, n)
    _paire(a["plan"], n)                                 # [x0, y0, largeur, hauteur]
    for s in a["axes"]:                                  # [x0, y0, x1, y1]
        if _une_fois(s):
            s[1] += n
            s[3] += n
    _paires(a["balises"], n)
    _paires(a["peints"], n, 2)                           # [type, x, y]
    _paires(a["portes_peintes"], n)                      # [x, y, sens]
    _paires(a["pont"]["piles"], n)
    a["masque"]["carte_h"] += n                          # la hauteur de la ville au-dessus de lui


def _chantiers(liste, n):
    _y(liste, n)
    for c in liste:
        if isinstance(c.get("tranchee"), list):
            _paires(c["tranchee"], n)
        for cle in ("signaleur", "conteneur"):
            if c.get(cle):
                _paire(c[cle], n)
        for ph in c["phases"]:
            _paires(ph.get("equipe"), n)
            if isinstance(ph.get("porte"), list):
                _paire(ph["porte"], n)
            for m in ph.get("machines", ()):
                if m.get("frappe"):
                    _paire(m["frappe"], n)


def _autobus(a, n):
    _y(a, n)
    for ligne in a["lignes"]:
        _paires(ligne["trace"], n)                       # `arrets` y est [id, rang] : des indices


def _eboueurs(e, n):
    _paires(e["trace"], n)
    _paires(e["points"], n, 2)                           # [rang, x, y]


def _tramway(t, n):
    _paires(t["trace"], n)
    _paires(t["arrets"], n, 2)                           # [rang, x, y, nom]


def _neige(v, n):
    _paires(v["charrue"]["trace"], n)
    for paires in v["deneigement"]["panneaux"].values():
        _paires(paires, n)


def _traversier(t, n):
    _y(t, n)
    for e in t["escales"]:
        _paires(e["acces"], n)


def _train(t, n):
    _paires(t["voie"], n)
    _paire(t["quai"], n, 2)                              # [x0, x1, y]


def _montagne_russe(m, n):
    _paires(m["voie"], n * PX)                           # [x, y, z] en PIXELS
    _paires(m["supports"], n, 2)                         # [rang, x, y]
    _y(m["zone"], n)


def _jeux_de_foire(v, n):
    _y(v, n)
    for jeu in v:
        _paires(jeu.get("cibles"), n)                    # [x, y] : les cibles de la galerie de tir


def _relief(r, n):
    if r.get("montagnes"):
        r["montagnes"]["h"] += n                             # elles montent jusqu'en haut de la bande


def _foire_enclos(v, n):
    _paires(v, n, 0)                                     # [y, x0, x1]


def _mouillages(v, n):
    _y(v, n * PX)                                        # en PIXELS, eux aussi


DECALAGES = {
    "aeroport": _aeroport, "amarrages": _y, "ambulants": _y, "apparition": _y, "aqueduc": _rien,
    "aqueducs": _y, "arrets": None, "autobus": _autobus, "barrieres": _y, "chantiers": _chantiers,
    "chemins_des_bois": _paires, "concessionnaires": _y, "decalage_nord": _rien, "decor": _y, "decor_solide": _rien,
    "devant": _rien, "devantures": _y, "districts": _rien, "eboueurs": _eboueurs, "entrave": _rien,
    "entraves": _y, "fermeture": _rien, "fermetures": _y, "feux_pietons": _y, "flottants": _rien, "foire": _y,
    "foire_enclos": _foire_enclos, "fourriere": _y, "frenesies": _y, "frenesies_regle": _rien, "graffitis": _y, "graine": _rien, "grille": None,
    "grille_nord": _rien, "hauteur": None, "ile": _y, "incendies": _y, "interieurs": _rien,
    "intersections": _y, "jeux_de_foire": _jeux_de_foire, "kiosques_de_foire": _y, "lampes": _y, "lave_auto": _y, "largeur": _rien,
    "metro": _y, "montagne_russe": _montagne_russe, "mouillages": _mouillages, "neige": _neige,
    "nids_de_poule": _y, "nom": _rien, "paquets": _y, "plages": _y, "points_interet": _y, "ponts": _y,
    "portes": _y, "portes_garage": _y, "rampes": _y, "reclames": _y, "relief": _relief, "residences": _y,
    "roue": _y, "scenes": _y, "slug": _rien, "sol": None, "stationnement_du_poste": _y, "toits": _y,
    "train_de_foire": _train, "tramway": _tramway, "traversier": _traversier, "tuile_px": _rien,
    "tuiles_bouchees": _rien, "voie": None, "zones": _y,
}


def decaler(ville: dict, n: int) -> None:
    """Toute la ville descend de `n` rangées ; les `n` rangées du haut restent inertes (`M`) en attendant la
    bande. ⚠️ Une clé que `DECALAGES` ne connaît pas LÈVE, en la nommant."""
    inconnues = sorted(set(ville) - set(DECALAGES))
    if inconnues:
        raise KeyError(f"nord.decaler ne sait pas décaler {inconnues} : ajoute-les à nord.DECALAGES")
    _VUS.clear()
    try:
        for cle, f in DECALAGES.items():
            # ⚠️ `None` : ce que cette graine n'a pas (des éboueurs sans tournée, p. ex.) ne descend pas.
            if f is not None and ville.get(cle) is not None:
                f(ville[cle], n)
    finally:
        _VUS.clear()
    ville["arrets"] = {f"{k.split(',')[0]},{int(k.split(',')[1]) + n}": v for k, v in ville["arrets"].items()}
    ville["sol"][:0] = ["M" * ville["largeur"]] * n
    ville["voie"][:0] = ["." * ville["largeur"]] * n
    ville["hauteur"] += n
    ville["grille"]["y0"] = n
    ville["decalage_nord"] = n


# --- La pose : décaler, coller, coudre ---------------------------------------------------------------

_CACHE: dict = {}


def _bande() -> _ChantierNord:
    """La bande ne dépend que de sa trame et de sa graine : bâtie une fois par processus."""
    if "bande" not in _CACHE:
        _CACHE["bande"] = batir_la_bande()
    return _CACHE["bande"]


def colonnes_de_la_couture() -> list[int]:
    """Les x où une voie nord-sud de la bande débouche sur le boulevard de la couture."""
    ch = _bande()
    return [x for x in range(ch.largeur) if ch.voie[DECALAGE_NORD - 1][x] != "."]


def poser(ville: dict) -> None:
    """Toute la ville descend de `DECALAGE_NORD` rangées, et la bande se colle au-dessus. Sans un dé de la
    ville : ce qui suit ne lit que la ville finie et la bande, bâtie avec sa graine à elle."""
    n, ch = DECALAGE_NORD, _bande()
    decaler(ville, n)
    est = ville["sol"][n][ch.largeur:]                   # la falaise et les montagnes de l'est
    for y in range(n):
        ville["sol"][y] = "".join(ch.sol[y]) + est
        ville["voie"][y] = "".join(ch.voie[y]) + "." * len(est)
    # LA COUTURE : là où une voie de la bande débouche, le trottoir nord du boulevard s'ouvre comme un
    # croisement — la rangée 110 de la bande, qui l'a bâti ouvert — et le croisement gagne son bras nord.
    couture = colonnes_de_la_couture()
    for x in couture:
        for cle, grille in (("sol", ch.sol), ("voie", ch.voie)):
            ligne = ville[cle][n]
            ville[cle][n] = ligne[:x] + grille[n][x] + ligne[x + 1:]
    for inter in ville["intersections"]:
        if (inter["y"] <= n + carte.TROTTOIR < inter["y"] + inter["h"]
                and any(inter["x"] <= x < inter["x"] + inter["l"] for x in couture)):
            inter["bras"] = "".join(c for c in "NSOE" if c in inter["bras"] or c == "N")
            # ⚠️ Le navigateur doit savoir que ce croisement a CHANGÉ (un T à arrêt devenu un carrefour à
            # feux) : il en numérote les feux à part, pour que la ville d'avant se joue pareil.
            inter["couture"] = True
    def haut(o):
        # ⚠️ Pas de borne-fontaine au pied de la couture : ses croisements ont maintenant quatre bras, et
        # leurs coins sont aux feux (`Moteur`, `test_trafic_js`).
        return o["y"] < n and not (o.get("type") == "borne_fontaine" and o["y"] >= n - 2)
    for cle, source in (("portes", ch.portes), ("decor", ch.decor), ("lampes", ch.lampes),
                        ("residences", ch.residences), ("devantures", ch.devantures), ("toits", ch.toits),
                        ("points_interet", ch.points), ("intersections", ch.intersections),
                        ("feux_pietons", ch.feux_nord)):
        # ⚠️ DES COPIES : la bande est bâtie une fois par processus (`_bande`), et la ville qu'on rend
        # est à qui la lit (le paquet la modifie) ; partager ses objets rendait le deuxième paquet autre.
        ville[cle].extend(copy.deepcopy([o for o in source if haut(o)]))
    # ⚠️ LES PORTES DU PETIT-CANTON DONNENT SUR LA COUTURE : leur devant est le boulevard de la ville d'avant,
    # où `devants.deplacer` (passé avant la bande) n'a rien vu. Un bris d'aqueduc y tombait devant une porte
    # (`test_devants`, graine 1). On MARQUE ce qui s'y tient (`ecartee`), on ne retire rien : le jeu tire
    # dans ces listes par `hash % longueur`.
    from . import devants as devants_mod
    larges = {(x + dx, y + dy) for (x, y) in devants_mod.portes(ville) if y < n for dx, dy in devants_mod.DEVANT}
    devants_mod._ecarter_les_evenements(ville, larges)
    ville["arrets"].update({k: v for k, v in ch.arrets.items() if int(k.split(",")[1]) < n})
    ville["interieurs"].update(copy.deepcopy(ch.pieces))
    slugs = {d["slug"] for d in DISTRICTS_NORD}
    ville["zones"].extend(copy.deepcopy({**z, "h": min(z["h"], n - z["y"])}) for z in ch.zones()
                          if z["district"] in slugs and not z.get("gang"))
    ville["districts"].extend({"slug": d["slug"], "nom": d["nom"], "gang": d["gang"], "eau": False}
                              for d in DISTRICTS_NORD)
    # LE PETIT-CANTON, ÉTAPE 2, VAGUE B : son arche et ses lanternes, sur la carte finie, sans un dé.
    from . import canton as canton_mod
    ville["canton"] = canton_mod.poser(ville, ch, district("canton"), n)
    ville["grille_nord"] = {"colonnes": list(carte.COLONNES), "rangees": list(RANGEES_NORD),
                            "rues_v": list(carte.RUES_V), "rues_h": list(RUES_H_NORD),
                            "trottoir": carte.TROTTOIR, "standing": list(ch.standing),
                            "usage": list(ch.usage), "y0": 0}


# --- Lire la carte FINIE ------------------------------------------------------------------------------

class _Lecteur:
    """Le quartier, le standing et l'usage d'une tuile de la carte FINIE : la bande nord au-dessus de
    `DECALAGE_NORD`, la ville d'avant en dessous, chacune dans sa trame — le miroir Python de
    `Monde.lettreDuBloc`. ⚠️ Un `_Chantier` neuf, lui, ne connaît que la ville d'avant, dans son repère."""

    def __init__(self) -> None:
        self._ville = None

    def _qui(self, y: int):
        if y < DECALAGE_NORD:
            return _bande(), y
        if self._ville is None:
            self._ville = carte._Chantier(carte.PLAN, carte.GRAINE)
        return self._ville, y - DECALAGE_NORD

    def standing_en(self, x: int, y: int):
        ch, y = self._qui(y)
        return ch.standing_en(x, y)

    def usage_en(self, x: int, y: int):
        ch, y = self._qui(y)
        return ch.usage_en(x, y)

    def district_en(self, x: int, y: int) -> str:
        ch, y = self._qui(y)
        return ch.district_en(x, y)


LECTEUR = _Lecteur()
