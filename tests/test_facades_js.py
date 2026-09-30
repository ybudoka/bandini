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


def test_les_plex_ont_leur_galerie_jamais_sur_la_chaussee(banc):
    """Vague 2 : un plancher de galerie sur la tuile du devant d'un plex (deux étages et plus), là où ce n'est ni la
    chaussée, ni l'eau, ni un mur ; jamais devant un bungalow d'un étage ni une maison de pêcheur."""
    r = banc("function (L, o) {" + PEINDRE + """
        const M = L.Monde, c = M.carte, PLANCHERS = ['#d9d4c6', '#8a6a44'];
        let avec = 0, peintes = 0, coupees = 0, fautes = [];
        for (const r of c.def.residences) {
            const e = M.logementElargi(r);
            if (!e.galerie) {
                if (r.etages >= 2 && r.declin == null) {
                    // Sans galerie : tout le devant est chaussee, eau ou mur.
                    for (let i = 0; i < e.l; i++) if (!M.estRoute(e.x + i, r.y + 1) && !M.estEau(e.x + i, r.y + 1) && M.solidite(e.x + i, r.y + 1) === 0) fautes.push(['oubliee', r.x, r.y]);
                }
                continue;
            }
            if (r.etages < 2 || r.declin != null) fautes.push(['bungalow', r.x, r.y]);
            avec++;
            e.galerie.forEach(function (oui, i) {
                const x = e.x + i, y = r.y + 1;
                if (oui && (M.estRoute(x, y) || M.estEau(x, y) || M.solidite(x, y) !== 0)) fautes.push(['devant', x, y]);
            });
            if (e.galerie.some(function (oui) { return !oui; })) coupees++;
            if (peindre(L, o, e).some(function (q) { return PLANCHERS.indexOf(q[4]) >= 0 && q[1] === 16; })) peintes++;
        }
        // ⚠️ Dans la ville livree, aucun logement ne donne sur la chaussee : un logement FICTIF, devant une rue, garde
        // la regle honnete (sans lui, elle ne se jugerait jamais).
        let rue = null;
        for (let y = 2; y < c.h - 1 && !rue; y++) for (let x = 2; x < c.w - 2 && !rue; x++) {
            if (M.estRoute(x, y + 1) && M.estRoute(x + 1, y + 1)) rue = { x: x, y: y };
        }
        const fictif = M.logementElargi({ x: rue.x, y: rue.y, l: 2, etages: 2, motifs: 'FF', porte: 0, escalier: 0, mur: 0, balcon: 0 });
        return { avec: avec, peintes: peintes, coupees: coupees, fautes: fautes.slice(0, 5), fictif: fictif.galerie || null };
    }""")
    assert r["avec"] >= 30 and r["peintes"] == r["avec"], r
    assert r["fictif"] is None, f"une galerie sur la chaussée : {r['fictif']}"
    assert r["fautes"] == [], r


def test_chaque_standing_a_ses_fenetres(banc):
    """Vague 2 : le cossu a sa grande fenêtre à battants (12 px, son meneau) et sa corniche ornée, l'ordinaire ses
    rideaux et sa boîte aux lettres ; le pauvre n'a ni rideau ni boîte."""
    r = banc("function (L, o) {" + PEINDRE + """
        const RIDEAUX = ['#c9a35a', '#b85c4a', '#6f8fa8', '#8fa86f', '#d9c9a8', '#9a7fa8'], BOITE = '#2a2d34';
        const out = { '+': { n: 0, battants: 0, boite: 0 }, '=': { n: 0, rideaux: 0, boite: 0 }, '-': { n: 0, rideaux: 0, boite: 0 } };
        for (const r of L.B.defs.carte.residences) {
            if (r.declin != null) continue;
            const s = r.standing || '=', t = peindre(L, o, r), o2 = out[s];
            o2.n++;
            if (s === '+' && r.etages >= 2 && t.some(function (q) { return q[2] === 12 && q[3] === 3; })) o2.battants++;
            if (s === '+' && r.etages < 2) o2.battants++;
            if (s !== '+' && t.some(function (q) { return RIDEAUX.indexOf(q[4]) >= 0; })) o2.rideaux++;
            if (t.some(function (q) { return q[4] === BOITE && q[2] === 2; })) o2.boite++;
        }
        return out;
    }""")
    assert r["+"]["battants"] == r["+"]["n"] > 0, r
    assert r["="]["rideaux"] == r["="]["n"] > 0, r
    assert r["-"]["rideaux"] == 0 and r["-"]["boite"] == 0 and r["-"]["n"] > 0, r
    assert r["="]["boite"] > r["="]["n"] * 0.8, r


def test_le_battant_d_une_porte_de_logement_reste_dans_le_rez(banc):
    """Martin (30 sept. 2026) : « les portes qui ouvrent passent souvent par-dessus des fenêtres peintes ». Le battant
    d'un logement ne prend que la porte du rez (les étages ont leurs fenêtres au-dessus) ; celui d'une devanture, dont
    la porte monte de l'auvent au trottoir, garde toute la tuile — le témoin."""
    r = banc("function (L, o) {" + """
        const M = L.Monde, B = L.B, c = M.carte;
        const logement = c.def.residences.find(function (q) { return q.motifs[q.porte] === 'D'; });
        const devanture = c.def.portes.find(function (p) { return !c.def.residences.some(function (q) { return q.x + q.porte === p.x && q.y === p.y; }); });
        function traces(tx, ty) {
            M.ouvrirPorte(tx, ty);
            for (let k = 0; k < 20; k++) M.majBattants();
            const ctx = o.doc.createElement('canvas').getContext('2d');
            ctx.traces = [];
            M.dessinerBattants(ctx, { x: tx * 16 - 100, y: ty * 16 - 100 });
            return ctx.traces.map(function (q) { return q[1] - 100; });   // le haut de chaque trace, dans la tuile
        }
        return { logement: traces(logement.x + logement.porte, logement.y), devanture: traces(devanture.x, devanture.y),
                 rez: L.FACADES.PORTE_DE_LOGEMENT };
    }""")
    assert r["logement"] and min(r["logement"]) >= r["rez"]["y"], r
    assert r["devanture"] and min(r["devanture"]) < r["rez"]["y"], "le témoin : la porte d'une devanture prend la tuile"
