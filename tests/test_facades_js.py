"""Une revue des façades des résidences, vague 1 (docs/jalons/une-revue-des-facades-des-residences.md) : le mur
tiré se peint (brique rouge, brique jaune, bardeau gris) jusqu'au bout de son bâtiment, et la porte condamnée n'a
ses planches qu'en rue pauvre."""

PEINDRE = """
  function peindre(L, o, r) {
    const def = L.B.defs, murs = def.devantures.murs, c = o.doc.createElement('canvas').getContext('2d');
    c.traces = [];
    L.FACADES.residence(c, r, murs[r.mur % murs.length], def.devantures.fer, 0, 0, null);
    return c.traces;
  }
"""


def test_le_mur_tire_se_peint_sur_toute_la_facade(banc):
    """⚠️ Avant la revue, `m.brique` n'était jamais peint : toute la ville était en brique rouge."""
    r = banc("function (L, o) {" + PEINDRE + """
        const def = L.B.defs, murs = def.devantures.murs, out = {};
        for (const r of def.carte.residences) {
            if (r.declin != null) continue;
            const m = murs[r.mur % murs.length], t = peindre(L, o, r);
            const couvre = t.some(function (q) { return q[4] === m.brique && q[0] === 0 && q[2] === r.l * 16 && q[3] === 16; });
            out[m.slug] = out[m.slug] || { n: 0, peints: 0 };
            out[m.slug].n++; if (couvre) out[m.slug].peints++;
        }
        return out;
    }""")
    assert set(r) == {"brique_rouge", "brique_jaune", "bardeau_gris"}, r
    for slug, c in r.items():
        assert c["peints"] == c["n"] > 0, f"{slug} : {c}"


def test_la_porte_condamnee_n_a_ses_planches_qu_en_rue_pauvre(banc):
    r = banc("function (L, o) {" + PEINDRE + """
        const PLANCHE = '#6b5a48', out = { '+': [0, 0], '=': [0, 0], '-': [0, 0] };
        for (const r of L.B.defs.carte.residences) {
            if (r.declin != null || (r.motifs || '')[r.porte] !== 'd') continue;
            const s = r.standing || '=', planches = peindre(L, o, r).some(function (q) { return q[4] === PLANCHE; });
            out[s][0]++; if (planches) out[s][1]++;
        }
        return out;
    }""")
    assert r["+"][0] > 0 and r["+"][1] == 0, f"des planches dans une rue cossue : {r}"
    assert r["="][0] > 0 and r["="][1] == 0, f"des planches dans une rue ordinaire : {r}"
    assert r["-"][0] > 0 and r["-"][1] == r["-"][0], f"la rue pauvre a perdu ses planches : {r}"


def test_le_mur_va_au_bout_du_batiment_sans_mordre_ailleurs(banc):
    """Élargi sur les tuiles de mur nu (`F`, `W`) de la même rangée dont le toit est le même bâtiment : jamais sur
    une devanture, un autre logement ou le voisin."""
    r = banc("function (L, o) {" + """
        const M = L.Monde, c = M.carte, t = M.teintesDesToits(), w = c.w;
        const prises = new Set(), autres = new Set();
        for (const d of c.def.devantures) for (let i = 0; i < d.l; i++) prises.add((d.x + i) + ',' + d.y);
        let elargis = 0, fautes = [];
        for (const r of c.def.residences) {
            const e = M.logementElargi(r);
            if (e.l > r.l) elargis++;
            const lui = t.qui[(r.y - 1) * w + r.x];
            for (let x = e.x; x < e.x + e.l; x++) {
                const dedans = x >= r.x && x < r.x + r.l;
                if (dedans) continue;
                if (prises.has(x + ',' + r.y)) fautes.push(['devanture', x, r.y]);
                if (t.qui[(r.y - 1) * w + x] !== lui) fautes.push(['voisin', x, r.y]);
                if ('FW'.indexOf(c.sol[r.y][x]) < 0) fautes.push(['glyphe', x, r.y, c.sol[r.y][x]]);
                if (c.def.residences.some(function (q) { return q !== r && q.y === r.y && x >= q.x && x < q.x + q.l; })) fautes.push(['logement', x, r.y]);
            }
            if (e.motifs.length !== e.l || e.motifs[e.porte] !== r.motifs[r.porte]) fautes.push(['porte', r.x, r.y]);
        }
        return { elargis: elargis, fautes: fautes.slice(0, 5), total: c.def.residences.length };
    }""")
    assert r["elargis"] >= 10, f"presque aucun mur élargi — le juge ne mord pas : {r}"
    assert r["fautes"] == [], r
