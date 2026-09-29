"""La lumière suit la saison, les règles gardent l'horloge : en décembre il fait noir à 17 h 30, en
juin il fait clair à 21 h ; `Monde.estNuit` (les commerces, la police, les missions) ne bouge pas."""


def test_la_nuit_tombe_plus_tot_en_decembre(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const p = L.B.partie, M = L.Monde, out = {};
        [['decembre', 39], ['juin', 19], ['mars', 10]].forEach(function (m) {
            p.jour = m[1];
            out[m[0]] = [17.5, 21, 12].map(function (h) { p.heure = h / 24; return [M.estNuitVue(), M.estNuit(), M.ambianceVue().alpha]; });
        });
        return out;
    }""")
    assert r["decembre"][0][0] is True, "il ne fait pas noir à 17 h 30 en décembre"
    assert r["juin"][1][0] is False, "il fait noir à 21 h en juin"
    assert r["decembre"][2][2] == 0 and r["juin"][2][2] == 0, "midi n'est plus clair"
    # L'horloge des règles : la même d'un mois à l'autre.
    assert [x[1] for x in r["decembre"]] == [x[1] for x in r["juin"]] == [x[1] for x in r["mars"]]


def test_la_lumiere_glisse_sans_saut_d_un_jour_a_l_autre(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const S = L.Saisons; let pire = 0, prec = null;
        for (let k = 0; k < 40 * 96; k++) {
            const j = 1 + Math.floor(k / 96), h = (k % 96) / 96, v = S.heureDeLumiere(j, h);
            if (prec !== null) { let d = Math.abs(v - prec); d = Math.min(d, 1 - d); pire = Math.max(pire, d); }
            prec = v;
        }
        return pire;
    }""")
    assert r < 0.03, f"la lumière saute de {r * 24:.2f} h d'un quart d'heure à l'autre"


def test_les_lampadaires_suivent_la_lumiere(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const p = L.B.partie; p.heure = 17.5 / 24;
        const l = L.Monde.carte.lampes.find(function (q) { return !q.panne && !q.eteinte && !q.demolie; });
        const cam = { x: l.x - L.VW / 2, y: l.y - L.VH / 2 };
        p.jour = 39; const hiver = L.Monde.lampesVisibles(cam).length;
        p.jour = 19; const ete = L.Monde.lampesVisibles(cam).length;
        return { hiver: hiver, ete: ete };
    }""")
    assert r["hiver"] > 0 and r["ete"] == 0
