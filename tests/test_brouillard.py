"""Le brouillard de Baie-des-Brumes : les règles (docs/jalons/le-brouillard-de-baie-des-brumes.md).
Le banc (`test_brouillard_js.py`) juge ce qu'il fait à la ville."""

from app import brouillard


def test_un_matin_de_brouillard_monte_a_l_aube_et_se_leve_avant_midi():
    m = brouillard.MATINS
    assert 0 < m["chance"] < 0.5, "un brouillard qui revient plus d'un matin sur deux n'est plus un événement"
    assert 0 < m["debut_h"] < m["plein_h"] < m["leve_h"] < m["fin_h"] <= 12


def test_il_raccourcit_la_vue_sans_l_eteindre():
    e = brouillard.EFFETS
    assert 0.2 < e["vision"] < 1, "la police voit moins loin — pas plus, et pas du tout n'est pas un brouillard"
    assert e["voile_centre"] < e["voile_bord"] < 1, "on voit autour de soi, pas au bout de la rue"
    assert set(e["pres_de_l_eau"]) == {"quais", "pointe"}
    assert 0 < e["ailleurs"] < 1
    assert brouillard.ANNONCE.isupper() and len(brouillard.ANNONCE) <= 60
