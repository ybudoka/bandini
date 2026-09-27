"""Le rang : le chalet, le lac de la clairière et la cabane à sucre, un seul bloc au bout d'une rue
(docs/jalons/la-ville-s-agrandit-au-nord.md)."""

from app import blocs, carte
from app.blocs import rang

VILLE = carte.generer()


def test_trois_blocs_tous_au_bord_ouest():
    slugs = [b["slug"] for b in blocs.BLOCS]
    assert sorted(slugs) == ["cineparc", "galeries", "rang"], slugs
    assert all(b["passage"]["bord"] == "ouest" for b in blocs.BLOCS)
    pris = [range(b["passage"]["de"], b["passage"]["de"] + b["passage"]["l"]) for b in blocs.BLOCS]
    for i, a in enumerate(pris):
        for b in pris[i + 1:]:
            assert not set(a) & set(b), "deux passages se chevauchent"


def test_l_entree_du_rang_est_une_rue_qui_va_jusqu_au_bord():
    sol = VILLE["sol"]
    p = rang.BLOC["passage"]
    tuiles = [sol[p["de"] + i][0] for i in range(p["l"])]
    assert tuiles == [".", "#", "+", "."], tuiles          # trottoir, deux voies, trottoir
    # La même rue, une tuile plus loin : c'est bien elle qui continue.
    assert [sol[172][x] for x in range(1, 5)] == ["#"] * 4


def test_aucun_char_de_la_circulation_ne_s_engage_vers_le_bord():
    voie = VILLE["voie"]
    assert voie[172][0] == "." and voie[173][0] == ".", "l'ouverture n'est pas une voie de circulation"
    for inter in VILLE["intersections"]:
        if inter["x"] <= 1 and inter["y"] <= 173 < inter["y"] + inter["h"]:
            assert "O" not in inter["bras"], inter


def test_depuis_l_arrivee_on_rejoint_les_deux_portes_le_char_et_le_quai():
    assert blocs.erreurs(rang.BLOC, VILLE) == []
    plan = rang.BLOC["plan"]
    quai = [(x, y) for y, ligne in enumerate(plan) for x, g in enumerate(ligne) if g == "Q"]
    assert quai, "le lac de la clairière a perdu son quai"
    # Le quai est un plancher sur l'eau : on le rejoint par la grève, une tuile de sable à côté.
    a_pied = blocs.a_pied_depuis_l_arrivee(rang.BLOC)
    assert set(quai) & a_pied, "on ne rejoint pas le quai à pied"
