"""La ville s'agrandit au nord, au banc (docs/jalons/la-ville-s-agrandit-au-nord.md)."""


def test_le_quartier_se_lit_des_deux_cotes_de_la_couture(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const n = L.B.defs.decalage_nord;
        return { n: n, bande: L.Monde.standingA(10, 10), dessous: L.Monde.standingA(10, n + 10),
                 canton: L.Monde.usageA(140, 20), faubourg: L.Monde.usageA(140, n + 20) };
    }""")
    assert r["n"] == 110, r
    assert r["bande"] == "pauvre" and r["dessous"] == "cossu", r
    assert r["canton"] == "commercial", r
