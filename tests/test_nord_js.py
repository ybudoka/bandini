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


def test_une_vieille_partie_descend_avec_la_ville(banc):
    """Écrite avant l'agrandissement (sans `decalage_nord`) : sa position, le char de la planque de Rocco et
    ses skimmers descendent de 110 rangées ; une partie déjà décalée ne redescend pas."""
    r = banc("""function (L, o) {
        const n = L.B.defs.decalage_nord;
        const p = L.Sauvegarde.completer({ x: 100, y: 200, planque: { vehicule: { slug: 'pickup', x: 5, y: 6 } },
            skimmers: [{ cle: '12,34', x: 200, y: 552, jour: 1, monte: 0, pret: false }] }, L.B.defs);
        const encore = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), L.B.defs);
        const neuve = L.Sauvegarde.completer(null, L.B.defs);
        return { y: p.y, vy: p.planque.vehicule.y, cle: p.skimmers[0].cle, sy: p.skimmers[0].y,
                 d: p.decalage_nord, n: n, encore: encore.y, neuve: neuve.decalage_nord };
    }""")
    n = r["n"]
    assert r["y"] == 200 + n * 16 and r["vy"] == 6 + n * 16, r
    assert r["cle"] == f"12,{34 + n}" and r["sy"] == 552 + n * 16, r
    assert r["d"] == n and r["encore"] == r["y"], "une partie déjà décalée ne redescend pas"
    assert r["neuve"] == n, "une partie neuve naît dans la ville d'aujourd'hui"
