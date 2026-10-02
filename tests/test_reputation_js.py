"""La réputation par quartier au banc (`docs/jalons/la-reputation-et-la-lecture-des-passants.md`, vague 2) : les
missions la montent, les crimes vus la descendent, elle revient vers 0 chaque matin et survit à la sauvegarde ; elle
ne change que la délation — bien vu, personne ne parle ; mal vu, tout le monde — sans changer le hasard."""

PRELUDE = """
    L.Jeu.commencer(); if (L.B.menu) L.Hud.fermerMenu();
    L.B.partie.jour = 22; L.B.partie.heure = 13 / 24;
    const j = L.B.joueur;
    j.intouchable = true;
    const ligne = o.ligneDroite(); j.x = ligne.x; j.y = ligne.y; j.angle = 0; j.face = 'droite';
    L.Monde.centrerCamera(j.x, j.y);
    for (const e of L.B.entites.slice()) if ((e.type === 'pieton' || e.type === 'vehicule') && Math.hypot(e.x - j.x, e.y - j.y) < 400) L.Entites.retirer(e);
    L.Entites.indexer();
    const R = L.Reputation, q = R.quartierA(j.x, j.y);
    function rep() { return (L.B.partie.reputation || {})[q] || 0; }
    /** Trois passants qui regardent le joueur, à 30-50 px, avec ce cœur-là. */
    function trois(proba) {
        return [30, 40, 50].map(function (dx, k) {
            const p = o.poser('passant', dx, k * 6 - 6); p.angle = Math.PI; p.probaTemoin = proba; return p;
        });
    }
    function temoins(ps) { return ps.filter(function (p) { return p.etat === 'temoin'; }).length; }
"""


def test_bien_vu_personne_ne_parle_mal_vu_tout_le_monde(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const out = { q: q };
        function essai(valeur, proba) {
            for (const e of L.B.entites.slice()) if (e.type === 'pieton') L.Entites.retirer(e);
            L.Entites.indexer();
            L.B.partie.reputation = {}; L.B.partie.reputation[q] = valeur;
            const ps = trois(proba);
            L.Police.signalerCrime('coup_pieton', j.x, j.y, true);
            return temoins(ps);
        }
        out.bien = essai(60, 1); out.mal = essai(-60, 0);
        out.neutreCoeur = essai(0, 1); out.neutreSansCoeur = essai(0, 0);
        return out;
    }""")
    assert r["q"], r
    assert r["bien"] == 0, f"bien vu, on te dénonce quand même : {r}"
    assert r["mal"] == 3, f"mal vu, des passants se taisent : {r}"
    assert r["neutreCoeur"] == 3 and r["neutreSansCoeur"] == 0, f"entre les deux, le cœur de chacun ne décide plus : {r}"


def test_mal_vu_un_homme_de_gang_ne_parle_pas_pour_autant(banc):
    """« Mal vu, tout le monde » : tout le monde qui parle à la police. Un Cravate n'y parle jamais (son `temoin` est
    0 au catalogue) — le 1er oct. 2026, celui qu'on battait à la rixe partait témoigner au lieu de se battre, et
    `test_rixe_js::test_il_esquive_parfois_ton_coup` est tombé sur 38 graines sur 40."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.B.partie.reputation = {}; L.B.partie.reputation[q] = -60;
        const ps = trois(0); ps.forEach(function (p) { p.gang = 'cravates'; p.courage = 0; p.etat = 'flane'; });
        L.Police.signalerCrime('coup_pieton', j.x, j.y, true);
        const police = temoins(ps);
        for (const e of L.B.entites.slice()) if (e.type === 'pieton') L.Entites.retirer(e);
        L.Entites.indexer();
        const ps2 = trois(0); ps2.forEach(function (p) { p.gang = 'cravates'; p.courage = 0; p.etat = 'flane'; });
        L.Entites.alerter(j.x, j.y, j, 0);
        return { police: police, alerte: temoins(ps2) };
    }""")
    assert r == {"police": 0, "alerte": 0}, f"mal vu, un homme de gang va voir la police : {r}"


def test_la_reputation_ne_change_pas_le_hasard(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const des = []; const rng = L.B.rng;
        function compter(valeur) {
            for (const e of L.B.entites.slice()) if (e.type === 'pieton') L.Entites.retirer(e);
            L.Entites.indexer();
            L.B.partie.reputation = {}; L.B.partie.reputation[q] = valeur;
            trois(0.5);
            let n = 0; L.B.rng = function () { n++; return rng.apply(this, arguments); };
            L.Police.signalerCrime('coup_pieton', j.x, j.y, true);
            L.B.rng = rng;
            return n;
        }
        return { bien: compter(60), neutre: compter(0), mal: compter(-60) };
    }""")
    assert r["bien"] == r["neutre"] == r["mal"] >= 3, r


def test_un_crime_vu_la_descend_un_crime_que_personne_n_a_vu_non(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.B.partie.reputation = {};
        L.Police.signalerCrime('coup_pieton', j.x, j.y, false);
        const pasVu = rep();
        L.Police.signalerCrime('coup_pieton', j.x, j.y, true);
        const coup = rep();
        L.Police.signalerCrime('mort_pieton', j.x, j.y, true);
        const mort = rep();
        // Un carambolage est un délit, pas trois : le répit du délit vaut ici aussi.
        L.Police.signalerCrime('conduite_dangereuse', j.x, j.y, true);
        L.Police.signalerCrime('conduite_dangereuse', j.x, j.y, true);
        const conduite = rep();
        L.B.partie.reputation[q] = -98;
        L.Police.signalerCrime('mort_policier', j.x, j.y, true);
        return { pasVu: pasVu, coup: coup, mort: mort, conduite: conduite, plancher: rep(), regle: L.B.defs.recherche.reputation };
    }""")
    g = r["regle"]["par_etoile"]
    assert r["pasVu"] == 0, r
    assert r["coup"] == -g and r["mort"] == -3 * g and r["conduite"] == -4 * g, r
    assert r["plancher"] == r["regle"]["min"], r


def test_une_mission_monte_le_quartier_de_son_donneur_une_job_moins(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.B.partie.reputation = {};
        // Le joueur au Faubourg : c'est le quartier du DONNEUR qui compte, pas celui où l'on se tient.
        const fb = L.B.defs.carte.zones.find(function (z) { return z.slug === 'faubourg'; });
        j.x = (fb.x + 20) * L.TT; j.y = (fb.y + 20) * L.TT; L.Entites.indexer();
        const ici = R.quartierA(j.x, j.y);
        const ou = L.Histoire.lieuDuPersonnage('tipaul');
        const chezTiPaul = R.quartierDeLaVille(ou.x, ou.y);
        L.Histoire.commencer('ti_paul_et_ses_amis'); L.B.cinema = null; L.B.scene = null;   // e01, son acte 1
        L.Histoire.reussir(); L.Histoire.finir();
        const apresMission = Object.assign({}, L.B.partie.reputation);
        L.Histoire.commencer('t01'); L.B.cinema = null; L.B.scene = null;
        L.Histoire.reussir(); L.Histoire.finir();
        return { ici: ici, chezTiPaul: chezTiPaul, mission: apresMission, job: L.B.partie.reputation, regle: L.B.defs.recherche.reputation };
    }""")
    g = r["regle"]
    assert r["chezTiPaul"] == "erables" and r["ici"] == "faubourg", r
    assert r["mission"] == {"erables": g["mission"]}, r
    assert r["job"] == {"erables": g["mission"] + g["job"]}, r


def test_chaque_matin_elle_revient_vers_zero(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.B.partie.reputation = { faubourg: 12, quais: -3, erables: 0 };
        L.Missions.nouveauJour();
        return L.B.partie.reputation;
    }""")
    assert r == {"faubourg": 7, "quais": 0, "erables": 0}, r


def test_elle_survit_a_la_sauvegarde(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.B.partie.reputation = { faubourg: 40, quais: -35 };
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(L.B.partie)), L.B.defs).reputation;
        const vieille = JSON.parse(JSON.stringify(L.B.partie)); delete vieille.reputation;
        return { relue: relue, vieille: L.Sauvegarde.completer(vieille, L.B.defs).reputation };
    }""")
    assert r == {"relue": {"faubourg": 40, "quais": -35}, "vieille": {}}, r


def test_l_alerte_contre_le_joueur_suit_le_quartier_pas_celle_contre_un_autre(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.B.partie.reputation = {}; L.B.partie.reputation[q] = 60;
        const ps = trois(1); ps.forEach(function (p) { p.courage = 0; p.gang = null; p.etat = 'flane'; });
        L.Entites.alerter(j.x, j.y, j, 1);
        const contreMoi = temoins(ps);
        for (const e of L.B.entites.slice()) if (e.type === 'pieton') L.Entites.retirer(e);
        L.Entites.indexer();
        const brute = o.poser('ouvrier', -20, 0);
        const ps2 = trois(1); ps2.forEach(function (p) { p.courage = 0; p.gang = null; p.etat = 'flane'; });
        L.Entites.alerter(j.x, j.y, brute, 1);
        return { contreMoi: contreMoi, contreUnAutre: temoins(ps2) };
    }""")
    assert r == {"contreMoi": 0, "contreUnAutre": 3}, r


def test_le_carnet_la_chiffre_et_la_jauge(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.B.partie.reputation = {}; L.B.partie.reputation[q] = 40;
        while (L.B.menu) o.tape('Escape', 2);
        o.tape('Escape', 2);
        L.Hud.ouvrirOnglet('carnet');
        const item = L.B.menu.items.find(function (i) { return i.libelle === 'RÉPUTATION'; });
        const sous = function () { const m = L.B.menu; return m && m.items[m.curseur].libelle; };
        for (let k = 0; k < 20 && sous() !== 'RÉPUTATION'; k++) o.tape('ArrowDown', 2);
        o.tape('KeyE', 2);
        let jauges = []; const d = L.Reputation.dessinerJauge;
        L.Reputation.dessinerJauge = function (ctx, x, y, l, qq) { jauges.push(qq); return d.apply(this, arguments); };
        L.Jeu.rendre();
        L.Reputation.dessinerJauge = d;
        return { detail: item && item.detail, titre: L.B.menu && L.B.menu.titre,
                 lignes: L.B.menu.items.length, quartiers: R.quartiers().length, jauges: jauges.length,
                 ici: L.B.menu.items.some(function (i) { return i.detail === '+40 · BIEN VU'; }) };
    }""")
    assert r["detail"] == "+40 · BIEN VU", r
    assert r["titre"] == "LA RÉPUTATION" and r["lignes"] == r["quartiers"] + 1 and r["ici"], r
    assert r["jauges"] >= min(r["quartiers"], 8), f"les jauges ne se dessinent pas au carnet : {r}"


def test_la_carte_montre_chaque_quartier_et_sa_jauge(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        while (L.B.menu) o.tape('Escape', 2);
        const ecrits = []; const t = L.Atlas.texte;
        L.Atlas.texte = function (ctx, s) { ecrits.push(s); return t.apply(this, arguments); };
        L.Jeu.ouvrirCarte(); o.frame(2);
        L.Atlas.texte = t; L.Jeu.fermerCarte();
        const noms = L.B.defs.carte.zones.filter(function (z) { return !z.gang && z.district === z.slug && R.quartiers().indexOf(z.slug) >= 0; })
            .map(function (z) { return z.nom.toUpperCase(); });
        return { noms: noms, vus: noms.filter(function (n) { return ecrits.indexOf(n) >= 0; }) };
    }""")
    assert len(r["vus"]) >= 6, f"la carte ne nomme pas les quartiers : {r}"
