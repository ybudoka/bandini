"""Le rang : le chalet, le lac de la clairière et la cabane à sucre, un seul bloc au bout d'une rue
(docs/jalons/la-ville-s-agrandit-au-nord.md)."""

import pytest
import villes

from app import blocs, carte, nord
from app.blocs import rang


@pytest.fixture(scope="module")
def livree():
    """La ville du jeu — celle de `tests/villes.py`, générée une fois par processus."""
    return villes.generer()


#: La rue qui traverse, sur la carte FINIE : la ville a descendu de `nord.DECALAGE_NORD` rangées.
Y_RUE = carte.OUVERTURES_DE_RUE[0]["y"] + nord.DECALAGE_NORD


def test_les_blocs_tous_au_bord_ouest():
    """Quatre depuis la villa du maire (l'infiltration, 28 sept. 2026) — tous au bord ouest, et deux passages
    ne se chevauchent jamais."""
    slugs = [b["slug"] for b in blocs.BLOCS]
    assert sorted(slugs) == ["cineparc", "galeries", "rang", "villa"], slugs
    assert all(b["passage"]["bord"] == "ouest" for b in blocs.BLOCS)
    pris = [range(b["passage"]["de"], b["passage"]["de"] + b["passage"]["l"]) for b in blocs.BLOCS]
    for i, a in enumerate(pris):
        for b in pris[i + 1:]:
            assert not set(a) & set(b), "deux passages se chevauchent"


def test_l_entree_du_rang_est_une_rue_qui_va_jusqu_au_bord(livree):
    sol = livree["sol"]
    p = blocs.passage_en_ville(rang.BLOC)
    assert p["de"] == Y_RUE - 1, "le passage couvre la rue et ses deux trottoirs"
    tuiles = [sol[p["de"] + i][0] for i in range(p["l"])]
    assert tuiles == [".", "#", "+", "."], tuiles          # trottoir, deux voies, trottoir
    # La même rue, une tuile plus loin : c'est bien elle qui continue.
    assert [sol[Y_RUE][x] for x in range(1, 5)] == ["#"] * 4


def test_aucun_char_de_la_circulation_ne_s_engage_vers_le_bord(livree):
    voie = livree["voie"]
    assert voie[Y_RUE][0] == "." and voie[Y_RUE + 1][0] == ".", "l'ouverture n'est pas une voie de circulation"
    for inter in livree["intersections"]:
        if inter["x"] <= 1 and inter["y"] <= Y_RUE + 1 < inter["y"] + inter["h"]:
            assert "O" not in inter["bras"], inter


def test_depuis_l_arrivee_on_rejoint_les_deux_portes_le_char_et_le_quai(livree):
    assert blocs.erreurs(rang.BLOC, livree) == []
    plan = rang.BLOC["plan"]
    quai = [(x, y) for y, ligne in enumerate(plan) for x, g in enumerate(ligne) if g == "Q"]
    assert quai, "le lac de la clairière a perdu son quai"
    # Le quai est un plancher sur l'eau : on le rejoint par la grève, une tuile de sable à côté.
    a_pied = blocs.a_pied_depuis_l_arrivee(rang.BLOC)
    assert set(quai) & a_pied, "on ne rejoint pas le quai à pied"


def test_les_galeries_et_le_cine_parc_s_ouvrent_sur_un_chemin(livree):
    """Martin (27 sept. 2026) : « je veux des ouvertures de chemin pour ces endroits ». Le trottoir de ceinture
    s'ouvre au milieu du passage : un bout de trottoir, trois tuiles d'asphalte, un bout de trottoir — et le
    chemin rejoint la rue de l'ouest, sans que la circulation s'y engage."""
    sol, voie = livree["sol"], livree["voie"]
    for slug in ("galeries", "cineparc"):
        p = blocs.passage_en_ville(blocs.par_slug(slug))      # en coordonnées de la carte finie
        tuiles = [sol[p["de"] + i][0] for i in range(p["l"])]
        assert tuiles == [".", "#", "#", "#", "."], (slug, tuiles)
        for i in range(1, p["l"] - 1):
            y = p["de"] + i
            assert sol[y][1] == "#", (slug, y, "le chemin ne rejoint pas la rue")
            assert voie[y][0] == ".", (slug, y, "le chemin est une voie de circulation")


# --- La cabane à sucre, pour vrai (docs/jalons/la-cabane-a-sucre-pour-vrai.md) ------------------------------

def _decors(type_: str) -> list[tuple[int, int]]:
    return [(d["x"], d["y"]) for d in blocs.decor_du_bloc(rang.BLOC) if d["type"] == type_]


def test_l_erabliere_a_ses_chaudieres_et_sa_tubulure_jusqu_a_la_cabane():
    seaux, tubes = _decors("erable_seau"), _decors("erable_tube")
    assert len(seaux) >= 40, f"une érablière de {len(seaux)} chaudières"
    assert len(tubes) >= 20, f"une tubulure de {len(tubes)} érables"
    t = rang.CABANE["tubulure"]
    # Chaque rang de tubulure a des érables des deux côtés du tuyau maître, qui ne tombe sur aucun arbre.
    for y in sorted({y for _, y in tubes}):
        xs = [x for x, yy in tubes if yy == y]
        assert min(xs) < t["x"] < max(xs), f"le rang {y} ne rejoint pas le maître des deux côtés"
    assert all(x != t["x"] for x, _ in tubes), "un érable planté sur le tuyau maître"
    sol = blocs.sol_du_bloc(rang.BLOC)
    assert sol[t["a"]][t["x"]] == "P", "le tuyau maître n'arrive pas au toit de la cabane"
    assert min(y for _, y in tubes) == t["de"], "le maître ne monte pas jusqu'au premier rang"


def test_le_sentier_de_la_caleche_est_libre_et_on_rejoint_son_arret():
    """La calèche roule sur la couture du milieu d'un sentier de deux tuiles : sous elle, du gravier ; à côté,
    aucun arbre (elle passerait au travers) ; la boucle se ferme ; et on rejoint son arrêt à pied."""
    sol = blocs.sol_du_bloc(rang.BLOC)
    arbres = [(x * 16 + 8, y * 16 + 15) for t in ("arbre", "erable_seau", "erable_tube", "corde_bois", "table_tire")
              for x, y in _decors(t)]
    ch = rang.CABANE["caleche"]["chemin"]
    assert ch[0] == ch[-1], "la boucle ne revient pas à son arrêt"
    for (x0, y0), (x1, y1) in zip(ch, ch[1:]):
        assert x0 == x1 or y0 == y1, "un tronçon de biais"
        n = max(abs(x1 - x0), abs(y1 - y0)) * 16
        for k in range(0, n + 1, 4):
            px, py = x0 * 16 + (x1 - x0) * 16 * k / n, y0 * 16 + (y1 - y0) * 16 * k / n
            for dx, dy in ((-8, -8), (7, -8), (-8, 7), (7, 7)):
                g = sol[int((py + dy) // 16)][int((px + dx) // 16)]
                assert g == "g", f"la calèche quitte le sentier en ({px}, {py}) : {g!r}"
            for ax, ay in arbres:
                assert abs(ax - px) > 18 or abs(ay - py) > 18, f"un arbre sur le sentier en ({ax}, {ay})"
    a_pied = blocs.a_pied_depuis_l_arrivee(rang.BLOC)
    x, y = ch[0]
    assert (x, y - 2) in a_pied or (x + 1, y - 2) in a_pied, "on ne rejoint pas l'arrêt de la calèche à pied"


def test_les_gens_de_la_cabane_se_tiennent_la_ou_l_on_marche_hors_du_sentier():
    sol = blocs.sol_du_bloc(rang.BLOC)
    a_pied = blocs.a_pied_depuis_l_arrivee(rang.BLOC)
    places = [(g["x"], g["y"]) for g in rang.CABANE["gens"]]
    assert len(set(places)) == len(places), "deux personnes sur la même tuile"
    for x, y in places:
        assert (x, y) in a_pied, f"({x}, {y}) : une place qu'on n'atteint pas"
        assert not (29 <= y <= 30 or 43 <= y <= 44), f"({x}, {y}) : planté sur le sentier de la calèche"
    t = rang.CABANE["table"]
    assert rang.PLAN[t["y"]][t["x"]] == "=", "la table de tire n'est pas où la cabane la cherche"
    assert sol[t["y"]][64] == "g" and abs(t["x"] * 16 + 8 - (64 * 16 + 8)) > 24 + 8, "la table bouche l'allée"
