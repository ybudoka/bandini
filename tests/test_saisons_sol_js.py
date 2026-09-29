"""Le sol suit la saison : le gazon et la friche prennent la palette du moment, les trottoirs et les
toits blanchissent l'hiver ; les morceaux ne se repeignent qu'au changement de palier."""


def test_le_gazon_change_avec_l_annee(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        function peindre(g, v) { const ctx = L.Base.nouveauCanvas(L.TT, L.TT).getContext('2d'); ctx.traces = []; L.TUILES[g](ctx, v, L.TT); return ctx.traces.map(function (t) { return t[4]; }); }
        const out = {};
        [['janvier', 2], ['juillet', 21], ['octobre', 32]].forEach(function (m) {
            L.B.partie.jour = m[1]; L.B.partie.heure = 0.5;
            let gazon = [];
            for (let v = 0; v < 16; v++) gazon = gazon.concat(peindre(',', v));
            out[m[0]] = { gazon: gazon, friche: peindre(';', 3), trottoir: peindre('.', 0), toit: peindre('B', 0) };
        });
        return out;
    }""")
    assert r["juillet"]["gazon"][0] == "#4f8d3e", "l'été n'a plus le gazon d'avant"
    assert "#7d6c4c" in r["juillet"]["gazon"], "le gazon pelé de l'été a perdu sa tache (terre2)"
    assert r["janvier"]["gazon"][0] == "#e8edf2"
    assert r["juillet"]["trottoir"] != r["janvier"]["trottoir"] and r["juillet"]["toit"] != r["janvier"]["toit"]
    assert r["octobre"]["friche"][0] != r["juillet"]["friche"][0]
    assert {"#c0392b", "#e67e22"} & set(r["octobre"]["gazon"]), "pas une feuille rouge dans le gazon d'octobre"
    assert not {"#c0392b", "#e67e22"} & set(r["juillet"]["gazon"])


def test_les_morceaux_ne_se_repeignent_qu_au_palier(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie, c = L.Monde.carte;
        p.jour = 21; p.heure = 0.5; L.Jeu.rendre();
        const avant = c.morceaux.size;
        // Un temoin cuit dans l'atlas, hors des tuiles et des arbres : un char, un passant.
        const peintre = function () {}, temoin = L.Atlas.cuirePeintre('vehicule|temoin', 4, 4, peintre);
        const m0 = Array.from(c.morceaux.values())[0];
        p.heure = 0.6; L.Jeu.rendre();
        const memeHeure = Array.from(c.morceaux.values())[0] === m0;
        p.jour = 32; L.Jeu.rendre();
        const autreSaison = Array.from(c.morceaux.values())[0] !== m0;
        return { avant: avant, memeHeure: memeHeure, autreSaison: autreSaison, palier: c.palier,
                 garde: L.Atlas.cuirePeintre('vehicule|temoin', 4, 4, peintre) === temoin };
    }""")
    assert r["avant"] > 0 and r["memeHeure"], "un morceau repeint sans changement de palier"
    assert r["autreSaison"] and r["palier"] == "automne"
    assert r["garde"], "on a jeté tout l'atlas (les chars, les passants) au lieu des tuiles"


def test_la_ville_repeint_en_sortant_d_une_piece(banc):
    """On entre dans une pièce en été, le palier change dedans, on ressort : la ville se repeint."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie, j = L.B.joueur, ville = L.Monde.carte;
        p.jour = 21; p.heure = 0.5; L.Jeu.rendre();
        const m0 = Array.from(ville.morceaux.values())[0];
        const porte = (ville.def.portes || []).find(function (q) { return q.interieur; });
        j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
        L.Jeu.entrer(porte); o.fondu();
        for (let k = 0; k < 200 && !L.B.interieur; k++) o.frame(1);
        const dedans = !!L.B.interieur;
        p.jour = 32; L.Jeu.rendre();
        L.Jeu.sortir(); o.fondu();
        for (let k = 0; k < 200 && L.B.interieur; k++) o.frame(1);
        L.Jeu.rendre();
        return { dedans: dedans, repeint: Array.from(L.Monde.carte.morceaux.values())[0] !== m0,
                 palier: L.Monde.carte.palier, ville: L.Monde.carte === ville };
    }""")
    assert r["dedans"], "le juge n'est jamais entré"
    assert r["ville"] and r["repeint"] and r["palier"] == "automne"


def test_aucune_tuile_ne_garde_le_vert_d_ete_en_janvier(banc):
    """La bande de gazon devant les maisons, le gazon sous les clôtures et la piscine : tout ce qui
    peint du gazon le peint de la saison — une ville blanche rayée de vert ne se lit pas."""
    r = banc("""function (L) {
        L.Jeu.commencer(); L.B.partie.jour = 2; L.B.partie.heure = 0.5;
        const ete = ['#4f8d3e', '#5a9c47', '#427a33'], fautifs = {};
        for (const g in L.TUILES) {
            for (let v = 0; v < 1024; v++) {
                const ctx = L.Base.nouveauCanvas(L.TT, L.TT).getContext('2d'); ctx.traces = [];
                try { L.TUILES[g](ctx, v, L.TT); } catch (e) { break; }
                if (ctx.traces.some(function (t) { return ete.indexOf(t[4]) >= 0; })) { fautifs[g] = v; break; }
            }
        }
        return fautifs;
    }""")
    assert r == {}, f"du gazon d'été en janvier (glyphe: variante) : {r}"


def test_une_carte_neuve_ne_prend_pas_les_tuiles_de_l_ancien_palier(banc):
    """Le palier change sans qu'aucune image ne soit peinte, puis une carte NAÎT (une pièce, le bloc du
    chalet) : elle n'a pas de palier à elle, mais l'atlas, lui, a les tuiles de l'ancien — elles
    doivent partir quand même, sinon la pièce garde l'été jusqu'à la saison suivante."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const p = L.B.partie, c = L.Monde.carte;
        p.jour = 21; p.heure = 0.5; L.Jeu.rendre();
        const t0 = L.Atlas.cuireTuile(',', 3, L.TUILES[',']);
        p.jour = 32;
        delete c.palier;                 // comme une carte qui nait
        L.Jeu.rendre();
        return { neuve: L.Atlas.cuireTuile(',', 3, L.TUILES[',']) !== t0, palier: c.palier };
    }""")
    assert r["palier"] == "automne" and r["neuve"], "la carte neuve a gardé les tuiles de l'été"
