"""Les Mantes du Petit-Canton dans le jeu des territoires, au banc (docs/jalons/les-territoires-des-gangs-bougent.md,
vague 4) : le Canton se lit dans la trame du nord, ses îlots touchent ceux du Faubourg par la couture, les Mantes et
les Cravates s'y prennent des coins la nuit, jamais le cœur de l'autre, et un coin pris se peuple et se tague."""

from tests.test_territoires_js import OUTILS

PLUS = """
    function tous(L) { const d = L.Territoires.donnees(); return Object.keys(d.ilots).map(function (k) { return d.ilots[k]; }); }
    function centre(L, i) { const r = L.Territoires.rectangle(L.Territoires.donnees(), i); return { tx: Math.floor((r.x0 + r.x1) / 2), ty: Math.floor((r.y0 + r.y1) / 2) }; }
"""


def test_le_canton_se_lit_dans_la_trame_du_nord(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS + """
        L.Jeu.commencer();
        const T = L.Territoires, d = T.donnees(), canton = tous(L).filter(function (i) { return i.district === 'canton'; });
        // Chaque îlot du Canton : le centre de son rectangle le désigne, au-dessus de la couture.
        const allerRetour = canton.every(function (i) { const c = centre(L, i); return T.ilotA(c.tx, c.ty) === i && c.ty < d.y0; });
        const ecole = L.B.defs.carte.zones.find(function (z) { return z.gang === 'mantes'; });
        // Le milieu de leur coin (il commence au milieu de la rue, côté ouest : son bord est dans l'îlot voisin).
        const e = T.ilotA(ecole.x + Math.floor(ecole.l / 2), ecole.y + Math.floor(ecole.h / 2));
        // Les rectangles d'une colonne du Canton couvrent la bande sans trou : du bord nord (0) à la couture (y0).
        const col = canton.filter(function (i) { return i.bx === 7; }).sort(function (a, b) { return a.by - b.by; })
            .map(function (i) { return T.rectangle(d, i); });
        const pave = col[0].y0 === 0 && col[col.length - 1].y1 === d.y0
            && col.every(function (q, k) { return k === 0 || col[k - 1].y1 === q.y0; });
        const friches = L.B.defs.carte.zones.find(function (z) { return z.slug === 'friches'; });
        return { n: canton.length, rangees: canton.map(function (i) { return i.by; }).filter(function (v, k, a) { return a.indexOf(v) === k; }).sort(),
                 allerRetour: allerRetour, pave: pave, ecole: e && { gang: e.gang, coeur: e.coeur },
                 friches: T.ilotA(friches.x + 3, friches.y + 3), gangs: d.gangs.indexOf('mantes') >= 0 };
    }""")
    assert r["n"] == 56 and r["rangees"] == [-1, -2, -3, -4, -5, -6, -7] and r["allerRetour"] and r["pave"], r
    assert r["ecole"] == {"gang": "mantes", "coeur": True} and r["friches"] is None and r["gangs"], r


def test_la_couture_le_bas_du_canton_touche_le_haut_du_faubourg(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS + """
        L.Jeu.commencer();
        const d = L.Territoires.donnees();
        const bas = tous(L).filter(function (i) { return i.by === -1; });
        return bas.map(function (i) { const v = d.ilots[i.bx + ',0']; return v ? v.gang : null; });
    }""")
    assert r and all(g == "cravates" for g in r), r


def test_mantes_fortes_prennent_un_coin_du_faubourg_par_la_couture(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS + """
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie;
        const prises = [];
        for (let n = 0; n < 60; n++) {
            p.jour = 100 + n;
            ['chevreuils', 'boulonneux', 'morues', 'skateux', 'mantes'].forEach(function (g) { p.forcesDesGangs[g] = 100; });
            p.forcesDesGangs.cravates = 40;
            T.nuit().forEach(function (q) { if (q.gang === 'mantes') prises.push(q.k); });
        }
        const d = T.donnees();
        const faubourg = prises.map(function (k) { return d.ilots[k]; });
        return { n: prises.length, tous: faubourg.every(function (i) { return i.district === 'faubourg' && !(i.coeur && i.gang === 'cravates'); }),
                 premier: faubourg.length && faubourg[0].by, gangA: (function () {
                     const i = faubourg[0]; if (!i) return null; const c = centre(L, i); return T.gangA(c.tx * 16 + 8, c.ty * 16 + 8); })() };
    }""")
    assert r["n"] >= 1 and r["tous"], f"les Mantes ne prennent rien, ou le cœur des Cravates : {r}"
    assert r["premier"] == 0, "le premier coin pris est à la couture"
    assert r["gangA"] == "mantes", "le coin pris est chez elles"


def test_cravates_fortes_prennent_le_canton_jamais_l_ecole(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS + """
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie;
        let mantesPrises = 0;
        for (let n = 0; n < 60; n++) {
            p.jour = 300 + n;
            ['cravates', 'chevreuils', 'boulonneux', 'morues', 'skateux'].forEach(function (g) { p.forcesDesGangs[g] = 100; });
            p.forcesDesGangs.mantes = 40;
            T.nuit().forEach(function (q) { if (q.a === 'mantes') mantesPrises++; });
        }
        const d = T.donnees();
        const canton = tous(L).filter(function (i) { return i.district === 'canton'; });
        const pris = canton.filter(function (i) { return T.tenuPar(i) === 'cravates'; });
        const coeur = canton.filter(function (i) { return i.coeur; });
        return { pris: pris.length, mantesPrises: mantesPrises, coeurIntact: coeur.every(function (i) { return T.tenuPar(i) === 'mantes'; }),
                 coeur: coeur.length };
    }""")
    assert r["pris"] >= 5 and r["mantesPrises"] == r["pris"], r
    assert r["coeur"] == 4 and r["coeurIntact"], f"les Cravates ont pris l'école : {r}"


def test_a_forces_egales_rien_ne_bouge_a_la_couture(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const p = L.B.partie;
        for (let n = 0; n < 20; n++) { p.jour = 500 + n; L.Territoires.nuit(); }
        return Object.keys(p.territoires).length;
    }""")
    assert r == 0, r


def test_un_coin_du_faubourg_aux_mantes_porte_leurs_mots(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS + """
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie;
        tous(L).filter(function (i) { return i.district === 'faubourg' && !i.coeur; }).forEach(function (i) { p.territoires[i.k] = 'mantes'; });
        const tags = T.tagsDeLaFrontiere(L.Monde.carte);
        return { n: tags.length, mots: tags.map(function (t) { return t.texte; }).filter(function (v, k, a) { return a.indexOf(v) === k; }).sort(),
                 gangs: tags.every(function (t) { return t.gang === 'mantes'; }) };
    }""")
    assert r["n"] > 0 and r["gangs"] and set(r["mots"]) <= {"MANTES", "MNT"}, r


def test_la_carte_peint_un_coin_du_canton_au_dessus_de_la_couture(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS + """
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie, d = T.donnees();
        const i = tous(L).find(function (q) { return q.district === 'canton' && q.by === -1; });
        p.territoires[i.k] = 'cravates';
        const rects = [];
        const ctx = { fillRect: function (x, y, w, h) { rects.push([x, y, w, h]); }, set fillStyle(v) {}, set globalAlpha(v) {} };
        T.dessinerSurLaCarte(ctx, function (x, y) { return { x: x / 16, y: y / 16 }; });
        const r = T.rectangle(d, i);
        return { rects: rects, attendu: [r.x0, r.y0, r.x1 - r.x0, r.y1 - r.y0], y0: d.y0 };
    }""")
    assert r["rects"] == [r["attendu"]] and r["attendu"][1] + r["attendu"][3] <= r["y0"], r
