"""Une amélioration générale des toits, au banc (docs/jalons/une-amelioration-generale-des-toits.md).

Vague 1 — une teinte par bâtiment : chaque toit a la sienne, tirée à l'empreinte du bâtiment dans les teintes de
son quartier ; deux toits voisins de même matière ne se ressemblent pas ; rien au dé."""

TOITS = """
    function toits(L) {
        const M = L.Monde, c = M.carte;
        c.teintes = null;
        const t0 = Date.now();
        const t = M.teintesDesToits();
        return { t: t, ms: Date.now() - t0, c: c };
    }
"""


def test_chaque_toit_a_sa_teinte_la_meme_d_une_partie_a_l_autre(banc):
    """Recompter les toits rend les mêmes teintes, et la tuile porte celle de son bâtiment dans sa variante.
    ⚠️ Le témoin : les teintes varient — au moins quatre par matière dans la ville, pas une."""
    r = banc("function (L, o) {" + TOITS + """
        L.Jeu.commencer();
        const a = toits(L), un = Array.from(a.t.teintes).join(','), qui = a.t.qui;
        const b = toits(L), deux = Array.from(b.t.teintes).join(',');
        const parGlyphe = {};
        b.t.teintes.forEach(function (x, n) { (parGlyphe[b.t.glyphes[n]] = parGlyphe[b.t.glyphes[n]] || new Set()).add(x); });
        // Une tuile de toit plat au milieu d'un bâtiment : sa variante porte la teinte.
        const c = b.c, M = L.Monde;
        let mal = 0, vues = 0;
        for (let ty = 1; ty < c.h - 1 && vues < 2000; ty += 3) {
            for (let tx = 1; tx < c.w - 1 && vues < 2000; tx += 3) {
                const g = M.glyphe(tx, ty), n = b.t.qui[ty * c.w + tx];
                if (n < 0) continue;
                vues++;
                const v = M.varianteDeTuile(g, tx, ty);
                const teinte = 'BEO'.indexOf(g) >= 0 ? v >> 7 : v >> 6;
                if (teinte !== b.t.teintes[n]) mal++;
            }
        }
        return { memes: un === deux, n: b.t.teintes.length, mal: mal, vues: vues,
                 parGlyphe: Object.fromEntries(Object.keys(parGlyphe).map(function (g) { return [g, parGlyphe[g].size]; })) };
    }""")
    assert r["memes"], "les teintes changent d'un compte à l'autre"
    assert r["n"] >= 300 and r["vues"] >= 500 and r["mal"] == 0, r
    assert all(n >= 4 for n in r["parGlyphe"].values()) and len(r["parGlyphe"]) == 4, r


def test_deux_toits_voisins_de_meme_matiere_n_ont_pas_la_meme_teinte(banc):
    """Deux bâtiments de même matière à trois tuiles ou moins l'un de l'autre : jamais la même teinte, sauf quand
    leur quartier n'en a plus à offrir (un toit entouré de quatre voisins pareils). Et chaque toit tire dans les
    teintes de son quartier : un cossu n'a jamais la plus délavée, un pauvre jamais la plus neuve."""
    r = banc("function (L, o) {" + TOITS + """
        L.Jeu.commencer();
        const a = toits(L), t = a.t, c = a.c, M = L.Monde, w = c.w;
        const paires = new Set(), pareilles = new Set(), voisins = {};
        for (let ty = 0; ty < c.h; ty++) {
            for (let tx = 0; tx < w; tx++) {
                const n = t.qui[ty * w + tx];
                if (n < 0) continue;
                for (let dy = 0; dy <= 3; dy++) {
                    for (let dx = -3; dx <= 3; dx++) {
                        const xx = tx + dx, yy = ty + dy;
                        if (xx < 0 || yy >= c.h || xx >= w || (dy === 0 && dx <= 0)) continue;
                        const m = t.qui[yy * w + xx];
                        if (m < 0 || m === n || t.glyphes[m] !== t.glyphes[n]) continue;
                        const k = Math.min(n, m) + ',' + Math.max(n, m);
                        paires.add(k);
                        (voisins[n] = voisins[n] || new Set()).add(m);
                        (voisins[m] = voisins[m] || new Set()).add(n);
                        if (t.teintes[m] === t.teintes[n]) pareilles.add(k);
                    }
                }
            }
        }
        // Une paire pareille n'est permise que si l'un des deux avait déjà quatre voisins de sa matière.
        const fautives = Array.from(pareilles).filter(function (k) {
            const [n, m] = k.split(',').map(Number);
            return voisins[n].size < 4 && voisins[m].size < 4;
        });
        const horsQuartier = [];
        const offre = { cossu: [0, 1, 2, 3], ordinaire: [1, 2, 3, 4], pauvre: [2, 3, 4, 5] };
        const premiere = {};
        for (let i = 0; i < t.qui.length; i++) { const n = t.qui[i]; if (n >= 0 && premiere[n] === undefined) premiere[n] = i; }
        Object.keys(premiere).forEach(function (n) {
            const i = premiere[n], tx = i % w, ty = (i / w) | 0;
            const st = M.standingA(tx, ty) || 'ordinaire';
            if ((offre[st] || offre.ordinaire).indexOf(t.teintes[n]) < 0) horsQuartier.push([n, st, t.teintes[n]]);
        });
        return { paires: paires.size, pareilles: pareilles.size, fautives: fautives.slice(0, 5), nf: fautives.length,
                 horsQuartier: horsQuartier.slice(0, 5), ms: a.ms };
    }""")
    assert r["paires"] >= 50, r
    assert r["nf"] == 0, r
    assert r["horsQuartier"] == [], r


def test_les_teintes_ne_tirent_aucun_de_et_se_comptent_vite(banc):
    """Le compte ne tire pas `B.rng()` (sinon tout le hasard du jeu glisse), et il tient dans son budget : une fois
    par carte, au premier morceau peint."""
    r = banc("function (L, o) {" + TOITS + """
        L.Jeu.commencer();
        let tirages = 0;
        const vrai = L.B.rng;
        L.B.rng = function () { tirages++; return vrai.apply(this, arguments); };
        const a = toits(L), b = toits(L), c = toits(L);
        L.B.rng = vrai;
        return { tirages: tirages, ms: Math.min(a.ms, b.ms, c.ms), n: a.t.teintes.length, w: a.c.w, h: a.c.h };
    }""")
    assert r["tirages"] == 0, r
    assert r["ms"] < 400, r


# --- Vague 2 : les bords, les gouttières et l'ombre --------------------------------------------------------------

PEINDRE = """
    function peindre(L, glyphe, v) {
        const c = L.Base.nouveauCanvas(16, 16), ctx = c.getContext('2d');
        ctx.traces = [];
        L.TUILES[glyphe](ctx, v, 16);
        return ctx.traces;
    }
"""


def test_le_parapet_d_un_toit_plat_suit_le_soleil(banc):
    """Le soleil vient du nord-ouest : le parapet du nord jette son ombre sur le toit, celui du sud prend la lumière
    sur sa face intérieure. ⚠️ Le témoin : un plein toit, sans bord, n'a ni l'une ni l'autre."""
    r = banc("function (L, o) {" + PEINDRE + """
        const ombre = 'rgba(12,10,20,0.34)', lumiere = 'rgba(255,248,230,0.16)';
        const a = function (t, c) { return t.filter(function (q) { return q[4] === c; }); };
        const nord = peindre(L, 'B', 1), sud = peindre(L, 'B', 4), plein = peindre(L, 'B', 0), ouest = peindre(L, 'O', 8);
        return { nordOmbre: a(nord, ombre).map(function (q) { return q.slice(0, 4); }),
                 nordLumiere: a(nord, lumiere).length, sudLumiere: a(sud, lumiere).map(function (q) { return q.slice(0, 4); }),
                 sudOmbre: a(sud, ombre).length, plein: a(plein, ombre).length + a(plein, lumiere).length,
                 ouestOmbre: a(ouest, ombre).map(function (q) { return q.slice(0, 4); }) };
    }""")
    assert r["nordOmbre"] == [[0, 3, 16, 2]] and r["nordLumiere"] == 0, r
    assert r["sudLumiere"] == [[0, 11, 16, 2]] and r["sudOmbre"] == 0, r
    assert r["ouestOmbre"] == [[3, 0, 2, 16]] and r["plein"] == 0, r


def test_un_toit_en_pente_a_ses_gouttieres_et_ses_rives(banc):
    """Au bas de chaque versant (nord, sud), la gouttière de métal ; aux pignons (est, ouest), la rive, plus sombre
    que le bardeau. ⚠️ Le témoin : au milieu du toit, ni gouttière ni rive."""
    r = banc("function (L, o) {" + PEINDRE + """
        const metal = '#8d9297';
        const g = function (v) { return peindre(L, 'P', v).filter(function (q) { return q[4] === metal; }).map(function (q) { return q.slice(0, 4); }); };
        const sombre = function (v) { return peindre(L, 'P', v + 128).filter(function (q) { return q[2] === 3 && q[3] === 16; }).map(function (q) { return q[0]; }); };
        return { sud: g(4 + 32), nord: g(1), milieu: g(16), est: sombre(2), ouest: sombre(8), rien: sombre(0) };
    }""")
    assert r["sud"] == [[0, 13, 16, 3]] and r["nord"] == [[0, 0, 16, 2]] and r["milieu"] == [], r
    assert r["est"] == [13] and r["ouest"] == [0] and r["rien"] == [], r


def test_un_batiment_jette_son_ombre_sur_le_sol_a_son_est(banc):
    """Le sol collé au flanc est d'un bâtiment porte une bande d'ombre ; la pointe se pose au pied de son coin
    sud-est. ⚠️ Les témoins : un sol sans bâtiment à l'ouest n'en a pas ; et dans une pièce, aucune."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const M = L.Monde, c = M.carte;
        const bat = function (x, y) { return M.estToit(x, y) || 'FWDdG}H'.indexOf(M.glyphe(x, y)) >= 0; };
        const sol = function (x, y) { return !bat(x, y) && M.solidite(x, y) !== 1; };
        let flanc = null, libre = null, coin = null;
        for (let ty = 150; ty < c.h - 2 && !(flanc && libre && coin); ty++) {
            for (let tx = 2; tx < c.w - 2 && !(flanc && libre && coin); tx++) {
                if (!sol(tx, ty) || tx % 16 === 0) continue;
                if (!flanc && bat(tx - 1, ty) && bat(tx - 1, ty - 1)) flanc = { x: tx, y: ty };
                if (!coin && !bat(tx - 1, ty) && bat(tx - 1, ty - 1) && !bat(tx, ty - 1)) coin = { x: tx, y: ty };
                if (!libre && !bat(tx - 1, ty) && !bat(tx - 1, ty - 1) && !bat(tx, ty - 1) && sol(tx - 1, ty)) libre = { x: tx, y: ty };
            }
        }
        const traces = [], vrai = L.Base.nouveauCanvas;
        L.Base.nouveauCanvas = function () { const k = vrai.apply(this, arguments); k.getContext('2d').traces = traces; return k; };
        const bande = function (t, h) {
            traces.length = 0;
            c.morceaux.clear();
            M.dessinerSol(o.doc.createElement('canvas').getContext('2d'), { x: t.x * 16 - 240, y: t.y * 16 - 135 });
            return traces.filter(function (q) { return q[4] === 'rgba(11,10,18,0.34)' && q[2] === 4 && q[3] === (h || 16)
                && q[0] === (t.x % 16) * 16 && q[1] === (t.y % 16) * 16; }).length;
        };
        const auFlanc = bande(flanc), aLibre = bande(libre) + bande(libre, 6), auCoin = bande(coin, 6);
        c.interieur = { slug: 'banc' };
        const dedans = bande(flanc);
        delete c.interieur;
        L.Base.nouveauCanvas = vrai;
        return { flanc: flanc, auFlanc: auFlanc, aLibre: aLibre, dedans: dedans, coin: coin, auCoin: auCoin };
    }""")
    assert r["flanc"] and r["auFlanc"] == 1 and r["coin"] and r["auCoin"] == 1, r
    assert r["aLibre"] == 0 and r["dedans"] == 0, r
