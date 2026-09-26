"""Le 1er juillet, au banc (docs/jalons/le-1er-juillet-jour-du-demenagement.md) : le jour venu, les camions
sont là devant les maisons et les meubles sur le trottoir, sans un dé ; le lendemain, partis ; le camion
prend le boulot de déménageur ; le Clairon l'annonce."""

OUTILS = """
  const TT = 16;
  function jour(L, n) { L.B.partie.jour = n; L.B.partie.heure = 13 / 24; }
  function pres(L, o, c) {
    const j = L.B.joueur; j.x = c[0] * TT + 8; j.y = (c[1] + 3) * TT + 8; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
    for (let k = 0; k < 45; k++) o.frame(1);
  }
"""


def test_le_jour_venu_les_camions_sont_la_et_le_lendemain_partis(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, D = L.Demenagement, d = B.defs.demenagement, c = d.camions[0];
        jour(L, d.jour - 1); pres(L, o, c);
        const veille = D.camions().length, claironVeille = D.ligneDuClairon();
        jour(L, d.jour);
        L.graine(4); const temoin = [B.rng(), B.rng()]; L.graine(4);
        // Les camions naissent (le joueur est a cote) : entre deux tirages, aucun de.
        B.t = Math.ceil(B.t / 20) * 20; D.maj();
        const nes = D.camions().length;
        const apres = [B.rng(), B.rng()];
        pres(L, o, c);
        const le = D.camions().find(function (v) { return v.demenageur === 0; });
        B.stats.rects = 0; const ctx = L.Base.debut(); D.dessiner(ctx, B.cam); const peints = B.stats.rects;
        const matin = { camions: D.camions().length, pres: le ? [Math.floor(le.x / TT), Math.floor(le.y / TT)] : null,
                        reste: le && le.resteGare, clairon: D.ligneDuClairon(), peints: peints };
        jour(L, d.jour + 1); pres(L, o, c);
        B.stats.rects = 0; D.dessiner(ctx, B.cam);
        return { veille: veille, claironVeille: claironVeille, matin: matin, c: c, nes: nes, de: apres[0] === temoin[0] && apres[1] === temoin[1],
                 lendemain: D.camions().length, peintsLendemain: B.stats.rects };
    }""")
    assert r["veille"] == 0 and "DEMAIN" in r["claironVeille"], r
    m = r["matin"]
    assert m["camions"] >= 1 and m["pres"] == r["c"] and m["reste"], r
    assert m["clairon"] and "DÉMÉNAGEMENT" in m["clairon"], r
    assert m["peints"] > 0, "aucun meuble peint le 1er juillet"
    assert r["nes"] >= 1 and r["de"], f"les camions ont tiré au dé du jeu : {r}"
    assert r["lendemain"] == 0 and r["peintsLendemain"] == 0, r


def test_le_camion_prend_le_boulot_de_demenageur_le_1er_juillet(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, j = B.joueur, d = B.defs.demenagement;
        if (B.menu) L.Hud.fermerMenu();
        o.frame(2);
        const v = o.char('camion', 30, 0, 0);
        L.Vehicules.monter(j, v);
        o.frame(30);
        function klaxon(n) {
            if (M.boulot.etape) M.boulot.abandonner('');
            jour(L, n); o.frame(5); B.dialogue = null; if (B.menu) L.Hud.fermerMenu();
            o.tape('KeyJ', 2);
            return M.boulot.slug;
        }
        return { juillet: klaxon(d.jour), lendemain: klaxon(d.jour + 1) };
    }""")
    assert r == {"juillet": "demenagement", "lendemain": None}, r
