"""Les territoires des gangs bougent, au banc (docs/jalons/les-territoires-des-gangs-bougent.md, vague 1).

Martin : un coin par nuit ; coucher ses membres l'affaiblit ; il garde son cœur."""

OUTILS = """
    function tuileDe(L, ilot) {
        const d = L.Territoires.donnees();
        return { x: (d.x[ilot.bx] + 4) * 16 + 8, y: (d.y[ilot.by] + d.y0 + 4) * 16 + 8 };
    }
    function ilots(L, gang) {
        const d = L.Territoires.donnees();
        return Object.keys(d.ilots).map(function (k) { return d.ilots[k]; })
            .filter(function (i) { return L.Territoires.tenuPar(i) === gang; });
    }
"""


def test_une_partie_neuve_n_a_rien_de_pris_et_la_cour_reste_la_cour(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const T = L.Territoires, d = T.donnees(), p = L.B.partie;
        const coeur = Object.keys(d.ilots).map(function (k) { return d.ilots[k]; }).find(function (i) { return i.coeur && i.gang === 'cravates'; });
        const autre = ilots(L, 'cravates').find(function (i) { return !i.coeur; });
        const c = tuileDe(L, coeur), a = tuileDe(L, autre);
        return { pris: Object.keys(p.territoires).length, force: T.force('cravates'),
                 dansLaCour: T.gangA(c.x, c.y), ailleurs: T.gangA(a.x, a.y), gangs: d.gangs.length };
    }""")
    assert r["pris"] == 0 and r["force"] == 100 and r["gangs"] == 5, r
    assert r["dansLaCour"] == "cravates" and r["ailleurs"] is None, r


def test_un_membre_couche_compte_une_fois(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const T = L.Territoires, j = L.B.joueur;
        const m = L.Entites.creerPieton(j.x + 30, j.y, L.Entites.archetype('cravate'));
        L.Entites.blesser(m, 999, j, { assomme: true });
        L.Entites.blesser(m, 999, j, { assomme: true });
        const apres = T.force('cravates');
        const passant = L.Entites.creerPieton(j.x - 30, j.y, null);
        L.Entites.blesser(passant, 999, j, { assomme: true });
        return { gang: m.gang, apres: apres, toujours: T.force('cravates'), coup: T.donnees().regles.coup };
    }""")
    assert r["gang"] == "cravates", r
    assert r["apres"] == 100 - r["coup"] and r["toujours"] == r["apres"], r


def test_la_nuit_le_plus_fort_prend_un_coin_jamais_le_coeur(banc):
    """Les Cravates affaiblies : chaque nuit, un de leurs îlots passe à un voisin — un seul par voisin plus fort ;
    au bout de soixante nuits, leur cœur est toujours à elles. ⚠️ Le témoin : à forces égales, rien ne bouge."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie, d = T.donnees();
        const egales = T.nuit().length;
        const avant = ilots(L, 'cravates').length;
        p.forcesDesGangs.cravates = 0;
        p.jour = 7;
        const prises = T.nuit();
        const une = { prises: prises.map(function (q) { return q.gang + '>' + q.a; }), apres: ilots(L, 'cravates').length,
                      ligne: T.ligneDuClairon(prises), prise: prises[0] && d.ilots[prises[0].k] };
        for (let n = 0; n < 60; n++) { p.forcesDesGangs.cravates = 0; p.jour++; T.nuit(); }
        const coeur = Object.keys(d.ilots).map(function (k) { return d.ilots[k]; }).filter(function (i) { return i.coeur && i.gang === 'cravates'; });
        const g = une.prise && tuileDe(L, une.prise);
        return { egales: egales, avant: avant, une: une, coeurGarde: coeur.every(function (i) { return T.tenuPar(i) === 'cravates'; }),
                 restent: ilots(L, 'cravates').length, gangIci: g ? T.gangA(g.x, g.y) : null };
    }""")
    assert r["egales"] == 0, "à forces égales, un îlot a changé de mains"
    u = r["une"]
    assert u["prises"] and all(p.endswith(">cravates") for p in u["prises"]), u
    assert len(set(u["prises"])) == len(u["prises"]), "deux îlots pris par le même voisin la même nuit"
    assert u["apres"] == r["avant"] - len(u["prises"]), u
    assert u["prise"]["coeur"] is False and u["ligne"] and "CRAVATES" in u["ligne"], u
    assert r["coeurGarde"] and r["restent"] >= 4, r
    assert r["gangIci"] and r["gangIci"] != "cravates", "l'îlot pris n'est pas à son nouveau gang"


def test_un_district_libere_sort_du_jeu(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie;
        p.libere = ['faubourg'];
        p.forcesDesGangs.cravates = 0;
        const prises = T.nuit();
        return prises.filter(function (q) { return q.a === 'cravates' || q.gang === 'cravates'; }).length;
    }""")
    assert r == 0, "on grignote un district libéré"


def test_l_ilot_pris_se_peuple_de_son_nouveau_gang_et_survit_a_la_sauvegarde(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const T = L.Territoires, B = L.B, p = B.partie;
        p.forcesDesGangs.cravates = 0; p.jour = 3;
        const q = T.nuit()[0], i = T.donnees().ilots[q.k], t = tuileDe(L, i);
        B.joueur.x = t.x; B.joueur.y = t.y; L.Monde.centrerCamera(t.x, t.y); L.Entites.indexer();
        let vus = 0;
        for (let k = 0; k < 900 && !vus; k++) {
            o.frame(1);
            vus = B.entites.filter(function (e) { return e.gang === q.gang; }).length;
        }
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), B.defs);
        return { gang: q.gang, vus: vus, relu: relue.territoires[q.k], force: relue.forcesDesGangs.cravates };
    }""")
    assert r["vus"] > 0, f"aucun membre des {r['gang']} dans l'îlot qu'ils ont pris"
    assert r["relu"] == r["gang"] and r["force"] is not None, r
