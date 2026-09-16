"""Le bord de l'eau, 1re vague — la grève se meuble.

⚠️ **Mesure d'abord** : la ville posait 2 507 tuiles de sable (dont 782 touchent
l'eau) et 1 818 de quai, et personne ne s'y asseyait jamais. Ce qui manquait
n'était pas le terrain — c'est que le bord de l'eau était un décor qu'on
*traverse*. Six fiches et un semis, aucun moteur neuf.
"""

import pytest

from app import carte

#: Ce que la grève sème. ⚠️ `bouee` est à part : c'est le seul qui flotte.
MEUBLES = ("parasol", "serviette", "table_pique_nique", "chateau_sable",
           "poteau_amarrage", "belvedere", "bouee")


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


@pytest.fixture(scope="module")
def plage(ville):
    return [d for d in ville["decor"] if d["type"] in MEUBLES]


def eau_a_portee(ville, x, y, portee):
    """⚠️ En CROIX, comme le semis : une grève se mesure vers le large, et un
    coin de diagonale ferait passer pour riverain un carré de sable qui ne
    touche l'eau que par la pointe."""
    sol, largeur, hauteur = ville["sol"], ville["largeur"], ville["hauteur"]
    for d in range(1, portee + 1):
        for cx, cy in ((x + d, y), (x - d, y), (x, y + d), (x, y - d)):
            if 0 <= cx < largeur and 0 <= cy < hauteur and sol[cy][cx] == "~":
                return True
    return False


def test_la_fiche_de_la_greve_se_tient():
    f = carte.GREVE
    assert f["bord"] >= 1
    # ⚠️ Le château se bâtit là où le sable est mouillé : plus près que le reste.
    assert f["chateau_bord"] <= f["bord"], "un château de sable à sec"
    assert f["ecart"] >= 2, "deux meubles de plage se colleraient"
    mini, maxi = f["belvederes"]
    assert 0 < mini <= maxi
    assert f["belvedere_ecart"] > f["ecart"], "des belvédères en enfilade"
    for quoi, chance in f["chances"].items():
        assert 0 < chance < 0.2, f"{quoi} : une grève n'est pas un entrepôt"


def test_la_greve_est_meublee(plage):
    """Une plage vide est exactement ce qu'on avait avant la vague."""
    poses = {}
    for d in plage:
        poses[d["type"]] = poses.get(d["type"], 0) + 1
    for quoi in MEUBLES:
        assert poses.get(quoi, 0) > 0, f"pas un seul {quoi} dans toute la ville"


def test_tout_ce_qui_meuble_la_greve_est_au_bord_de_l_eau(ville, plage):
    """⚠️ **Une plage suit la côte ; elle ne suit pas une boîte.** La phrase est
    déjà dans `_eau()`, et elle y a coûté douze bancs de sable en pleine baie.
    Le semis marche tuile par tuile : un parasol planté au milieu d'un sentier
    du bois dit le contraire de ce qu'on veut."""
    portee = carte.GREVE["bord"] + 1
    for d in plage:
        assert eau_a_portee(ville, d["x"], d["y"], portee), (
            f"un {d['type']} en ({d['x']}, {d['y']}) est loin de toute eau")


def test_le_chateau_se_batit_sur_le_sable_mouille(ville):
    """Un château de sable à huit tuiles de l'eau n'est pas un château de
    sable : c'est un tas de terre."""
    bord = carte.GREVE["chateau_bord"]
    for d in ville["decor"]:
        if d["type"] != "chateau_sable":
            continue
        assert ville["sol"][d["y"]][d["x"]] == "s", "un château hors du sable"
        assert eau_a_portee(ville, d["x"], d["y"], bord), (
            f"un château en ({d['x']}, {d['y']}) est loin de l'eau")


def test_seule_la_bouee_flotte(ville):
    """⚠️ **`poser_decor` refuse le solide, et l'eau EN EST** (`solide: 2`) —
    c'est pour ça qu'aucun décor n'avait jamais flotté. La bouée est le premier
    qui ait raison de le faire ; on le lui a accordé par demande explicite
    (`sur_eau`) plutôt qu'en ouvrant l'eau à tout le catalogue.

    """
    for d in ville["decor"]:
        sur_eau = ville["sol"][d["y"]][d["x"]] == "~"
        if d["type"] == "bouee":
            assert sur_eau, f"une bouée au sec en ({d['x']}, {d['y']})"
        else:
            assert not sur_eau, f"un {d['type']} flotte en ({d['x']}, {d['y']})"


def test_deux_meubles_de_plage_ne_se_collent_pas(plage):
    """Une grève qui porte un parasol tous les trois pas n'est pas une plage,
    c'est un stationnement de parasols."""
    ecart = carte.GREVE["ecart"]
    points = [(d["x"], d["y"]) for d in plage]
    for i, (x, y) in enumerate(points):
        for px, py in points[i + 1:]:
            assert abs(px - x) + abs(py - y) >= ecart, f"({x}, {y}) et ({px}, {py})"


def test_la_greve_ne_touche_pas_au_de_de_la_ville():
    """⚠️ **La leçon des dés, appliquée avant qu'elle ne coûte.** Un semis qui
    tire dans le dé PRINCIPAL décale toute la suite du hasard — le barbelé l'a
    déjà fait, et douze scènes d'amuseur ont disparu du Faubourg pour une
    histoire de clôture.

    La grève a son propre dé. Le juge le vérifie sur pièce : une baie de poche,
    l'état du dé de la ville noté avant, et meublé après — le dé de la ville
    n'a pas bougé d'un cran, celui de la grève oui, et il s'est posé du monde."""
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    # Une baie de poche : de l'eau au nord, une grève de sable en dessous.
    for y in range(4):
        for x in range(4, 40):
            chantier.sol[y][x] = "~"
    for y in range(4, 8):
        for x in range(4, 40):
            chantier.sol[y][x] = "s"
    avant_ville, avant_greve = chantier.des.etat, chantier.des_greve.etat
    poses = chantier.greve()
    assert poses > 0, "rien ne s'est posé : le juge ne mesure rien"
    assert chantier.des.etat == avant_ville, (
        "la grève a tiré dans le dé de la ville : tout ce qui suit est décalé")
    assert chantier.des_greve.etat != avant_greve, "la grève n'a pas tiré son propre dé"


def test_la_greve_se_meuble_en_dernier():
    """On ne meuble pas un terrain que la ville va encore retirer :
    `boucher_les_poches` noie les bancs de sable isolés, un par un.

    ⚠️ **Mesuré, pour ne pas faire passer une précaution pour un correctif** :
    sur huit graines et 1 139 meubles, semer *avant* n'en noie aujourd'hui aucun.
    Ce juge ne répare donc rien — il **épingle l'ordre**, pour que le jour où le
    bouchage noiera plus large, ça ne passe pas en silence."""
    import inspect
    recette = inspect.getsource(carte.generer)
    assert "chantier.greve(ponts)" in recette, "la grève n'est jamais semée"
    assert recette.index("boucher_les_poches") < recette.index("chantier.greve(ponts)"), (
        "la grève est semée avant que la ville ne noie ses bancs de sable")


def test_rien_ne_traine_au_pied_d_un_pont(ville):
    """⚠️ **Un quai n'est pas une plage, et le pied d'un pont non plus** —
    `FERMETURES` le disait déjà pour les rues barrées.

    Mesuré, et trouvé par un juge qui ne parle pas de plage : une serviette et
    deux bouées s'étaient posées à une tuile du tablier de La Pointe, et un char
    lancé qui traversait les accrochait. Le juge du pont a vu la carrosserie
    tomber à 90 sur 100 **après** l'ouverture du pont, et en a conclu que le pont
    coûtait encore."""
    garde = carte.GREVE["pont_ecart"]
    for pont in ville["ponts"]:
        x0, y0 = pont["x"] - garde, pont["y"] - garde
        x1, y1 = pont["x"] + pont["l"] + garde, pont["y"] + pont["h"] + garde
        for d in ville["decor"]:
            if d["type"] not in MEUBLES:
                continue
            assert not (x0 <= d["x"] < x1 and y0 <= d["y"] < y1), (
                f"un {d['type']} traîne au pied du pont {pont['sens']} "
                f"en ({d['x']}, {d['y']})")
