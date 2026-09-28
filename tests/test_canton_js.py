"""Le Petit-Canton vu du jeu : la plaque verticale se peint, et seulement sur ses commerces."""


def test_la_plaque_se_peint_au_petit_canton_et_nulle_part_ailleurs(banc):
    """Le peintre de devanture pose la plaque rouge et ses deux idéogrammes quand la devanture
    porte `ideo`. ⚠️ Le témoin : la MÊME devanture, sans `ideo`, n'a pas un pixel de la plaque —
    et une devanture de la ville d'avant n'en a pas non plus."""
    r = banc("""function (L, o) {
        const def = L.B.defs, genres = def.devantures.genres;
        const peindre = function (d) {
            const c = o.doc.createElement('canvas').getContext('2d');
            c.traces = [];
            L.FACADES.devanture(c, d, genres[d.genre] || genres[0], 0, 0);
            return c.traces;
        };
        const rouge = function (t) { return t.filter(function (q) { return q[4] === '#a3201c'; }).length; };
        const dore = function (t) { return t.filter(function (q) { return q[4] === '#f2cc5a'; }).length; };
        const canton = def.carte.devantures.filter(function (d) { return d.ideo != null; });
        const d = canton[0], sans = Object.assign({}, d); delete sans.ideo;
        const ville = def.carte.devantures.find(function (x) { return x.ideo == null; });
        return { n: canton.length, rouge: rouge(peindre(d)), dore: dore(peindre(d)),
                 temoin: rouge(peindre(sans)), ville: rouge(peindre(ville)),
                 paires: def.carte.canton.ideogrammes.paires.length };
    }""")
    assert r["n"] >= 15 and r["paires"] >= 4, r
    assert r["rouge"] == 1 and r["dore"] >= 12, f"la plaque ne se peint pas : {r}"
    assert r["temoin"] == 0 and r["ville"] == 0, r


def test_l_arche_et_les_lanternes_se_peignent_au_dessus_des_gens_en_ville_seulement(banc):
    """`Canton.dessiner` peint le toit de l'arche et les lanternes quand la caméra est dessus — et rien quand
    elle est ailleurs (le témoin), ni dans une pièce. Et la lueur des lanternes est rouge, pas un lampadaire."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, d = L.Monde.carte.def.canton, a = d.arches[0], TT = L.TT;
        const peindre = function (cx, cy) {
            const c = o.doc.createElement('canvas').getContext('2d');
            c.traces = [];
            L.Canton.dessiner(c, { x: cx - 240, y: cy - 160 });
            return c.traces;
        };
        const couleurs = function (t) { const s = {}; t.forEach(function (q) { s[q[4]] = (s[q[4]] || 0) + 1; }); return s; };
        const ici = couleurs(peindre(a.x * TT, a.y * TT));
        const loin = peindre(20 * TT, 300 * TT).length;
        B.interieur = { slug: 'essai' };
        const dedans = peindre(a.x * TT, a.y * TT).length;
        B.interieur = null;
        const lueur = L.Monde.carte.lampes.find(function (l) { return l.sorte === 'lanterne'; });
        return { ici: ici, loin: loin, dedans: dedans, lueur: lueur ? lueur.c : null };
    }""")
    assert r["ici"].get("#2f7a4a", 0) >= 1 and r["ici"].get("#a3201c", 0) >= 2, f"l'arche ne se peint pas : {r['ici']}"
    assert r["ici"].get("#c8281e", 0) >= 3, f"pas de lanterne : {r['ici']}"
    assert r["loin"] == 0 and r["dedans"] == 0, r
    assert r["lueur"] and "255,90,60" in r["lueur"], r["lueur"]
