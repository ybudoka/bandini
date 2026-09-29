"""La palette du moment (`static/js/saisons.js`) : une pure fonction du jour et de l'heure, la même
pour tout le monde, qui glisse d'une saison à l'autre en huit paliers, sans saut."""


def test_la_palette_suit_l_annee(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const S = L.Saisons, p = function (j, h) { return S.paletteA(j, h); };
        return {
            janvier: p(1, 0.5).gazon.fond, juillet: p(21, 0.5).gazon.fond, octobre: p(32, 0.5).arbre.teintes[0][0],
            halloween: S.cleA(33, 0.9), an2: S.cleA(41 + 32, 0.5), an3: S.cleA(81 + 32, 0.5), an1: S.cleA(33, 0.5),
            memeJour: JSON.stringify(p(15, 0.3)) === JSON.stringify(p(15, 0.3)),
            neigeJanvier: p(2, 0.5).neige, neigeJuillet: p(21, 0.5).neige,
        };
    }""")
    assert r["janvier"] == "#e8edf2" and r["juillet"] == "#4f8d3e" and r["octobre"] == "#b8321f"
    assert r["halloween"] == "automne"
    assert r["an1"] == r["an2"] == r["an3"], "la deuxième année n'a pas les couleurs de la première"
    assert r["memeJour"] and r["neigeJanvier"] == 0.7 and r["neigeJuillet"] == 0


def test_la_palette_glisse_sans_saut(banc):
    """Toutes les demi-heures d'une année : d'un moment au suivant, la palette ne change que d'un
    palier (1/8 de l'écart entre deux saisons) au plus — et la clé ne change qu'avec la palette."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const S = L.Saisons, rgb = function (c) { return [1, 3, 5].map(function (i) { return parseInt(c.substr(i, 2), 16); }); };
        let pire = 0, cles = 0, prec = null, cprec = null, faux = 0;
        for (let j = 1; j <= 41; j++) for (let k = 0; k < 48; k++) {
            const h = k / 48, g = rgb(S.paletteA(j, h).gazon.fond), c = S.cleA(j, h);
            if (prec) {
                const d = Math.max.apply(null, g.map(function (v, i) { return Math.abs(v - prec[i]); }));
                pire = Math.max(pire, d);
                if (c !== cprec) cles++; else if (d !== 0) faux++;
            }
            prec = g; cprec = c;
        }
        // Le plus grand ecart d'un canal entre deux palettes voisines : un palier en fait le huitieme.
        const d = L.B.defs.saisons; let ecart = 0;
        for (let i = 0; i < d.cles.length - 1; i++) {
            const x = rgb(d.palettes[d.cles[i][1]].gazon.fond), y = rgb(d.palettes[d.cles[i + 1][1]].gazon.fond);
            x.forEach(function (v, k) { ecart = Math.max(ecart, Math.abs(v - y[k])); });
        }
        return { pire: pire, cles: cles, faux: faux, borne: Math.ceil(ecart / d.paliers) + 1 };
    }""")
    assert r["faux"] == 0, "la couleur change sans que la clé change : le cache ne se repeindrait pas"
    # Un palier fait au plus le huitième du plus grand écart entre deux palettes voisines (le bleu de la
    # neige contre le gazon d'avril : 0xf2 − 0x45 = 173, soit 22), plus l'arrondi.
    assert r["pire"] <= r["borne"] <= 24, f"un saut de {r['pire']} (borne {r['borne']})"
    assert 30 <= r["cles"] <= 60, f"{r['cles']} changements de palier dans l'année"


def test_enneiger_blanchit_l_hiver_seulement(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const S = L.Saisons, st = { fond: '#9a9689', tole: true };
        L.B.partie.jour = 21; const ete = S.enneiger(st);
        L.B.partie.jour = 2; const hiver = S.enneiger(st), encore = S.enneiger(st);
        return { ete: ete.fond, hiver: hiver.fond, tole: hiver.tole, meme: hiver === encore };
    }""")
    assert r["ete"] == "#9a9689" and r["hiver"] != "#9a9689" and r["tole"] is True and r["meme"]
    assert int(r["hiver"][1:3], 16) > 0xd0, "un trottoir de janvier n'est pas blanchi"
