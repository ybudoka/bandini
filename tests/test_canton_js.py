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
                 paires: def.devantures.ideogrammes.paires.length };
    }""")
    assert r["n"] >= 15 and r["paires"] >= 4, r
    assert r["rouge"] == 1 and r["dore"] >= 12, f"la plaque ne se peint pas : {r}"
    assert r["temoin"] == 0 and r["ville"] == 0, r
