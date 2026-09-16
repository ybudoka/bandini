"""M12, 8e vague — le bris d'aqueduc.

⚠️ **Ce n'est pas un chantier.** L'entrave du jour et la rue barrée sont tirées
à l'aube et tiennent la journée ; celui-ci arrive à une **heure**, comme le char
en panne — on roulait, la rue était libre, elle ne l'est plus. Ni cônes, ni
panneau DÉTOUR : une gerbe d'eau et un trou.
"""

import pytest

from app import carte


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


def test_la_fiche_du_bris_se_tient():
    """Des chiffres qui se contredisent font une conduite qui ne lâche jamais."""
    f = carte.AQUEDUCS
    mini, maxi = f["par_ville"]
    assert 0 < mini <= maxi
    assert 0 < f["chance_par_heure"] <= 1
    # ⚠️ Il coule moins d'une heure : au-delà, deux bris se chevaucheraient et
    # « une conduite lâche » deviendrait « la ville fuit de partout ».
    assert 0 < f["minutes"] < 60, "un bris déborde sur le suivant"
    assert f["flaque"] >= 1, "un bris sans eau autour est un nid-de-poule"
    assert f["ecart"] > f["flaque"] * 2, "deux flaques se toucheraient"
    assert f["raison"].strip() and f["degats"] > 0


def test_le_paquet_porte_les_bris_et_leur_fiche(ville):
    """⚠️ « Une fiche que le navigateur ne lisait pas » — le dépôt a payé ce
    défaut huit fois. La liste ET la fiche : l'une dit *où*, l'autre dit *ce que
    ça coûte et ce que ça affiche*. Le navigateur lisait déjà une liste en y
    cherchant la raison, une fois."""
    assert ville["aqueducs"], "le navigateur ne reçoit aucun endroit où une conduite peut lâcher"
    f = ville["aqueduc"]
    for cle in ("raison", "degats", "chance_par_heure", "minutes", "flaque"):
        assert cle in f, cle
    mini, maxi = carte.AQUEDUCS["par_ville"]
    assert mini <= len(ville["aqueducs"]) <= maxi


def test_un_bris_est_sur_une_voie_avec_une_voisine_parallele(ville):
    """⚠️ **C'est l'argument qui rend le bris inoffensif**, et il est le même que
    celui des entraves du jour : le trou ne couvre qu'UNE tuile, et cette tuile a
    une voisine **parallèle qui va dans le même sens** — celle qui restera
    ouverte. Le champ de direction ne bouge donc pas d'une flèche."""
    voie = ville["voie"]
    arrets = {tuple(int(n) for n in cle.split(",")) for cle in ville["arrets"]}
    boites = [(i["x"], i["y"], i["l"], i["h"]) for i in ville["intersections"]]
    pas = {">": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}
    for c in ville["aqueducs"]:
        x, y = c["x"], c["y"]
        fleche = voie[y][x]
        assert fleche in pas, f"({x}, {y}) n'est pas une voie dirigée : {fleche!r}"
        assert (x, y) not in arrets, f"({x}, {y}) est une ligne d'arrêt"
        assert not any(bx <= x < bx + bl and by <= y < by + bh
                       for bx, by, bl, bh in boites), f"({x}, {y}) est dans un croisement"
        dx, dy = pas[fleche]
        assert any(voie[y + ny][x + nx] == fleche for nx, ny in ((-dy, dx), (dy, -dx))), (
            f"({x}, {y}) n'a pas de voie de rechange à côté")


def test_deux_bris_ne_se_voisinent_pas(ville):
    """Deux flaques collées ne font pas deux bris : elles font un quartier
    inondé, et le joueur croit à une inondation scriptée."""
    ecart = carte.AQUEDUCS["ecart"]
    points = [(c["x"], c["y"]) for c in ville["aqueducs"]]
    for i, (x, y) in enumerate(points):
        for px, py in points[i + 1:]:
            assert abs(px - x) + abs(py - y) >= ecart, f"({x}, {y}) et ({px}, {py})"


PAS = {">": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}


def test_un_bris_se_contourne_par_la_voie_d_a_cote(ville):
    """⚠️ **LE JUGE QUI COMPTE** — et il a fallu jeter le premier, qui ne
    mesurait rien de bon.

    La tentation était d'appliquer le standard de la **rue barrée** : effacer la
    flèche et redemander à `voies_bloquees` si les rues sont encore fortement
    connexes. Mesuré : les **trente** candidates échouent, et ce n'est pas un
    défaut — c'est la leçon de la 3e vague relue à l'envers. Une voie est un
    couloir dirigé d'une tuile de large : boucher une tuile laisse toujours le
    reste du tronçon en cul-de-sac dans les deux sens, jusqu'au croisement
    suivant. C'est exactement pourquoi une rue barrée doit couvrir **tout** son
    tronçon.

    Un bris n'est pas une rue barrée : il ne touche pas au champ de direction, et
    ce qui le rend franchissable n'est pas le graphe des flèches, c'est **le
    changement de voie**. La vraie garantie, celle dont le trafic se sert, est
    donc la manœuvre : on se déporte une tuile avant, on passe à côté du trou, on
    continue. Ce juge la vérifie sur les trois tuiles qu'elle emprunte."""
    voie, sol = ville["voie"], ville["sol"]
    largeur, hauteur = ville["largeur"], ville["hauteur"]

    def fleche_en(x, y):
        return voie[y][x] if 0 <= x < largeur and 0 <= y < hauteur else "."

    def roulable(x, y):
        return (0 <= x < largeur and 0 <= y < hauteur
                and bool(carte.LEGENDE[sol[y][x]].get("route")))

    for c in ville["aqueducs"]:
        x, y = c["x"], c["y"]
        dx, dy = PAS[voie[y][x]]
        sens = voie[y][x]
        # La voie d'à côté doit porter le même sens, ET mener quelque part des
        # deux bouts : une voisine qui commence ou finit pile au trou n'est pas
        # un détour, c'est une impasse d'une tuile.
        assert any(
            fleche_en(x + px, y + py) == sens
            and (fleche_en(x + px - dx, y + py - dy) == sens or roulable(x + px - dx, y + py - dy))
            and (fleche_en(x + px + dx, y + py + dy) == sens or roulable(x + px + dx, y + py + dy))
            for px, py in ((-dy, dx), (dy, -dx))
        ), f"un bris en ({x}, {y}) ne se contourne pas : la voie d'à côté ne mène nulle part"
