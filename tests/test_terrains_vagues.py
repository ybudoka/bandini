"""Plus de champs : des terrains vagues sales, et des parcs de quartier.

⚠️ **Mesure d'abord**, et c'est elle qui donne raison à Martin (« au lieu des
champs, mets des terrains vague un peu salle et avec des déchets, mais aussi
des parcs ») : **24 lots** de la ville — **1 328 tuiles** — se peignaient avec
`,`, le gazon des parcs et des cours de banlieue, et il n'y avait qu'**un objet
par 17 tuiles** dessus. Dix étaient des terrains nus (406 tuiles, un arbre ou un
buisson par 16 tuiles) ; quatorze étaient des **terrains vagues** (922 tuiles)
dont le seul décor était le gravat. Vu d'en haut, de la ferraille derrière un
barbelé avait donc exactement la surface d'un parterre entretenu.

Ce que ces juges tiennent : la friche est une surface **à elle** (et pas verte
sur la mini-carte), un terrain vague est **sale**, un parc de quartier a un
**sentier** — et le générateur ne sait plus poser de pelouse rase.
"""

from __future__ import annotations

import pytest

from app import carte

#: Le sol d'un terrain vague.
FRICHE = ";"

#: Ce qu'un parc de quartier pose, et qu'un gazon nu ne posait pas.
#: ⚠️ Pas de `table_pique_nique` : c'est un meuble de GREVE, et `test_greve`
#: tient que toute table de la ville est au bord de l'eau.
MEUBLES_DE_PARC = ("banc", "arbre", "buisson")


@pytest.fixture(scope="module")
def ville_et_lots():
    """La ville, et la BOÎTE de chaque lot que le générateur a meublé.

    ⚠️ Le paquet ne porte pas les parcelles — il porte des glyphes — et un juge
    qui les redevinerait à partir du sol jugerait sa propre devinette : un
    sentier de parc de quartier et une allée de `_parc` sont le même `g`, et
    rien dans l'export ne les distingue. On regarde donc le générateur poser,
    ce qui coûte une génération de plus (0,9 s) et ne suppose rien.
    """
    lots: dict[str, list[tuple[int, int, int, int]]] = {"parc": [], "vague": []}
    chantier = carte._Chantier
    parc, vague = chantier._parc_de_quartier, chantier._terrain_vague

    def note(quoi, quelle):
        def pose(self, x, y, largeur, hauteur, *reste, **nommes):
            lots[quoi].append((x, y, largeur, hauteur))
            return quelle(self, x, y, largeur, hauteur, *reste, **nommes)
        return pose

    chantier._parc_de_quartier = note("parc", parc)
    chantier._terrain_vague = note("vague", vague)
    try:
        ville = carte.generer()
    finally:
        chantier._parc_de_quartier, chantier._terrain_vague = parc, vague
    return ville, lots


@pytest.fixture(scope="module")
def ville(ville_et_lots):
    return ville_et_lots[0]


def decor_dans(ville, boite):
    x, y, largeur, hauteur = boite
    return [d for d in ville["decor"]
            if x <= d["x"] < x + largeur and y <= d["y"] < y + hauteur]


# --- La friche --------------------------------------------------------------


def test_la_friche_est_une_surface_a_elle():
    """⚠️ Et surtout : **pas `herbe`**. La mini-carte peint le vert avec cette
    propriété-là (`couleurMini`, monde.js) ; une friche verte sur la carte, c'est
    un parc de plus — soit l'inverse de ce qu'on vient de dessiner. Elle tombe
    dans la couleur de terre, avec le sable et l'allée de parc.

    ⚠️ `terre`, en revanche : un arbre pousse dans une friche sans qu'on lui
    creuse une fosse de béton (`Monde.carte.fosses`). Une fosse au milieu des
    gravats, c'est un arbre de rue."""
    fiche = carte.LEGENDE[FRICHE]
    assert carte.solidite(FRICHE) == 0, "on traverse un terrain vague"
    assert carte.marchable(FRICHE)
    assert not carte.routier(FRICHE), "un terrain vague n'est pas une chaussée"
    assert fiche.get("terre"), "un arbre y aurait une fosse de béton"
    assert not fiche.get("herbe"), "la mini-carte repeindrait la friche en vert"
    assert fiche["nom"] != carte.LEGENDE[","]["nom"], "friche et gazon se confondent"


def test_la_ville_porte_de_la_friche_et_elle_est_derriere_une_cloture(ville):
    """Un terrain vague, c'est ce qu'on a fermé et laissé à l'abandon : chaque
    étendue de friche est CEINTURÉE (`clore`), sinon rien ne dit qu'elle est à
    quelqu'un — c'est la règle que `_terrain_vague` tient déjà pour sa clôture,
    et la friche ne se pose nulle part ailleurs."""
    sol, largeur, hauteur = ville["sol"], ville["largeur"], ville["hauteur"]
    tuiles = [(x, y) for y in range(hauteur) for x in range(largeur)
              if sol[y][x] == FRICHE]
    assert len(tuiles) > 400, f"presque pas de friche dans la ville : {len(tuiles)}"

    vu: set[tuple[int, int]] = set()
    etendues = []
    for depart in tuiles:
        if depart in vu:
            continue
        pile, region = [depart], []
        vu.add(depart)
        while pile:
            x, y = pile.pop()
            region.append((x, y))
            for cx, cy in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (cx, cy) in vu or not (0 <= cx < largeur and 0 <= cy < hauteur):
                    continue
                if sol[cy][cx] == FRICHE:
                    vu.add((cx, cy))
                    pile.append((cx, cy))
        etendues.append(region)
    assert len(etendues) >= 10, f"{len(etendues)} terrains vagues dans toute la ville"

    #: ⚠️ **Pas « toutes », et c'est `clore` qui le dit** : « tout ou rien —
    #: mieux vaut un terrain ouvert qu'un moignon de clôture ». Un lot coincé
    #: entre deux murs voit son enceinte refusée en entier, et le voisin bâti
    #: après lui en mange ce qui restait. Ce qu'on tient, c'est que ça reste
    #: l'exception : les GRANDS terrains sont ceinturés sans faute, et la ville
    #: n'a pas de nappe de friche ouverte au milieu d'un pâté de maisons.
    CEINTURE_MINIMUM, GRAND_LOT = 0.85, 20
    derriere_une_cloture = 0
    for region in etendues:
        tour = {(x + dx, y + dy) for x, y in region for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
        clotures = sum(1 for x, y in tour - set(region)
                       if 0 <= x < largeur and 0 <= y < hauteur
                       and sol[y][x] in carte.CLOTURES)
        if clotures >= 3:
            derriere_une_cloture += len(region)
        else:
            assert len(region) < GRAND_LOT, (
                f"une friche de {len(region)} tuiles en {region[0]} sans une clôture autour")
    part = derriere_une_cloture / len(tuiles)
    assert part >= CEINTURE_MINIMUM, (
        f"seulement {part:.0%} de la friche est derrière une clôture")


def test_aucune_friche_dans_un_parc(ville, ville_et_lots):
    """Une friche est l'image d'un lot abandonné : posée dans un parc de
    quartier, elle dit le contraire de ce que le parc dit."""
    sol = ville["sol"]
    for x, y, largeur, hauteur in ville_et_lots[1]["parc"]:
        for cy in range(y, y + hauteur):
            for cx in range(x, x + largeur):
                assert sol[cy][cx] != FRICHE, f"de la friche dans un parc, en {(cx, cy)}"


# --- Les déchets ------------------------------------------------------------


def test_la_liste_des_dechets_se_tient():
    """⚠️ Une liste À POIDS : ce qu'on voit d'abord dans un lot abandonné, c'est
    du gravat et des sacs. Un baril par dix tuiles n'a plus l'air abandonné, il a
    l'air rempli — d'où les répétitions dans la liste, qui sont le poids."""
    dechets = carte.DECHETS
    assert len(set(dechets)) >= 4, "un terrain vague à une seule sorte de saleté"
    assert dechets.count("debris") > dechets.count("baril"), (
        "le baril est aussi fréquent que le gravat")
    # ⚠️ **UNE BORNE DES DEUX CÔTÉS.** Une sur six a été livrée et Martin l'a
    # renvoyée le jour même : « il y a trop de saleté partout ». En dessous de
    # dix, un lot a l'air d'un dépôt et se referme sur lui-même ; au-delà de
    # seize, on le traverse sans rien contourner, et c'est un gazon sec.
    assert 10 <= carte.PART_DECHET <= 16, f"une tuile sur {carte.PART_DECHET} : sale ou dépôt ?"
    assert carte.PART_MAUVAISE_HERBE > carte.PART_DECHET, (
        "autant de buissons que de déchets : on ne verrait plus la friche")


def test_un_terrain_vague_est_sale(ville, ville_et_lots):
    """⚠️ **Le défaut, en un chiffre** : le terrain vague semait un gravat par
    douze tuiles et n'en posait qu'un par DIX-SEPT — le reste tombait sur du
    réservé ou de l'occupé. Treize lots sur quatorze se traversaient sans rien
    contourner. Et c'est la VARIÉTÉ qui fait la saleté autant que le nombre :
    trois tas de gravats se lisent comme un motif, un sac crevé à côté d'un pneu
    se lit comme un dépotoir."""
    lots = ville_et_lots[1]["vague"]
    assert lots, "pas un seul terrain vague dans la ville"
    tuiles = sum(largeur * hauteur for _, _, largeur, hauteur in lots)
    poses: dict[str, int] = {}
    nus = []
    for boite in lots:
        dedans = decor_dans(ville, boite)
        for d in dedans:
            poses[d["type"]] = poses.get(d["type"], 0) + 1
        if not dedans:
            nus.append(boite)
    total = sum(poses.values())
    assert not nus, f"des terrains vagues sans rien dessus : {nus}"
    # ⚠️ Une fourchette, pas un plancher : « trop de saleté partout » a eu raison
    # d'un objet par six tuiles. Mesure livrée : un par 9,8.
    assert 7 <= tuiles / total <= 16, (
        f"un objet par {tuiles / total:.1f} tuiles : ni un dépôt, ni un gazon")
    for quoi in set(carte.DECHETS):
        assert poses.get(quoi, 0) > 0, f"pas un seul {quoi} dans toute la ville"
    assert poses.get("buisson", 0) > 0, "une friche où rien ne repousse"


# --- Les parcs de quartier --------------------------------------------------


def test_des_parcs_de_quartier_et_ils_ont_un_sentier(ville, ville_et_lots):
    """⚠️ **Ce qui fait un parc, c'est le sentier**, pas les arbres : un carré
    de gazon planté d'arbres reste un terrain ; le jour où quelque chose le
    TRAVERSE, c'est un endroit où l'on va. Le sentier va donc d'un bord à
    l'autre, et il est LIBRE — il se réserve en se traçant, exactement comme
    les allées de `_parc`, qui avaient appris que le parc sème ses arbres
    par-dessus ses propres sentiers."""
    lots = ville_et_lots[1]["parc"]
    assert len(lots) >= 5, f"{len(lots)} parcs de quartier dans toute la ville"
    sol = ville["sol"]
    pave = carte._Chantier.SENTIER_DE_PARC
    occupe = {(d["x"], d["y"]) for d in ville["decor"]}
    for x, y, largeur, hauteur in lots:
        dans_la_largeur = largeur >= hauteur
        if dans_la_largeur:
            sentier = [(cx, y + hauteur // 2) for cx in range(x, x + largeur)]
        else:
            sentier = [(x + largeur // 2, cy) for cy in range(y, y + hauteur)]
        for cx, cy in sentier:
            assert sol[cy][cx] == pave, f"le sentier du parc en {(x, y)} est coupé en {(cx, cy)}"
            assert carte.marchable(sol[cy][cx])
            assert (cx, cy) not in occupe, f"un décor bouche le sentier en {(cx, cy)}"


def test_un_parc_de_quartier_est_meuble_et_ne_se_cloture_pas(ville, ville_et_lots):
    """Une cour se ferme, un parc s'ouvre : la palissade que le gazon nu posait
    une fois sur deux en banlieue disait « c'est à quelqu'un », ce qui est le
    contraire de ce qu'on veut lire ici."""
    lots = ville_et_lots[1]["parc"]
    sol = ville["sol"]
    poses: dict[str, int] = {}
    for boite in lots:
        dedans = decor_dans(ville, boite)
        sortes = {d["type"] for d in dedans}
        for d in dedans:
            poses[d["type"]] = poses.get(d["type"], 0) + 1
        assert "arbre" in sortes, f"un parc sans un arbre, en {boite[:2]}"
        x, y, largeur, hauteur = boite
        for cy in range(y, y + hauteur):
            for cx in range(x, x + largeur):
                assert sol[cy][cx] not in carte.CLOTURES, (
                    f"une clôture dans un parc de quartier, en {(cx, cy)}")
    for quoi in MEUBLES_DE_PARC:
        assert poses.get(quoi, 0) > 0, f"pas un seul {quoi} dans les parcs de quartier"
    tuiles = sum(largeur * hauteur for _, _, largeur, hauteur in lots)
    total = sum(poses.values())
    assert tuiles / total <= 8, (
        f"un objet par {tuiles / total:.1f} tuiles : c'est encore une pelouse")


# --- Et le générateur ne sait plus poser de pelouse rase --------------------


def test_le_generateur_ne_pose_plus_de_gazon_nu():
    """⚠️ Le juge du CHAMP. `_contenu` rendait `jardin` — du gazon, quatre
    arbres, et en banlieue une palissade autour — pour 18 % des parcelles du
    vieux quartier et 22 % de celles de la banlieue. C'est UNE SORTE POUR UNE
    SORTE : ces parts-là sont passées au parc de quartier, et la part de bâti
    comme celle de stationnement n'ont pas bougé d'un centième. On ne change pas
    combien de terrains la ville laisse vides, on change ce qu'on y voit.

    ⚠️ Et pas une part de terrain vague de plus en banlieue, même si ça aurait
    été tentant : le semis d'un terrain vague ne tire pas le même nombre de dés
    que celui du gazon, et le dé est COMMUN — en déplacer un seul lot rebat la
    ville entière (mesuré : dix juges tombés d'un coup, aucun ne parlant de
    terrain vague). Les terrains vagues restent où ils étaient ; ils changent de
    surface, pas de place."""
    connus = {"bati", "vague", "parc", "stationnement"}
    chantier = carte._Chantier.__new__(carte._Chantier)
    parts: dict[str, dict[str, int]] = {}
    for genre in ("maisons", "banlieue", "commerces", "hangars", "industriel", "gang"):
        chantier.des = carte.Des(12345)
        compte: dict[str, int] = {}
        for _ in range(20000):
            quoi = chantier._contenu(genre)
            assert quoi in connus, f"contenu inconnu pour {genre} : {quoi!r}"
            compte[quoi] = compte.get(quoi, 0) + 1
        parts[genre] = compte
    for genre in ("maisons", "banlieue"):
        assert parts[genre].get("parc", 0) > 500, (
            f"presque aucun parc en {genre} : {parts[genre]}")
        assert not parts[genre].get("vague"), (
            f"un terrain vague en {genre} : le dé commun se décale ({parts[genre]})")
    for genre in ("commerces", "hangars", "industriel", "gang"):
        assert parts[genre].get("vague", 0) > 200, (
            f"presque aucun terrain vague en {genre} : {parts[genre]}")
    # Les parts de bâti d'avant, au centième près (elles ne devaient pas bouger).
    for genre, attendu in (("maisons", 0.74), ("banlieue", 0.72), ("commerces", 0.88),
                           ("hangars", 0.80), ("industriel", 0.60), ("gang", 0.70)):
        part = parts[genre]["bati"] / 20000
        assert abs(part - attendu) < 0.02, f"{genre} : {part:.2f} de bâti au lieu de {attendu}"
