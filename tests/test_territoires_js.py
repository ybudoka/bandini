"""Les territoires des gangs bougent, au banc (docs/jalons/les-territoires-des-gangs-bougent.md, vague 1).

Martin : un coin par nuit ; coucher ses membres l'affaiblit ; il garde son cœur."""

OUTILS = """
    function tuileDe(L, ilot) {
        const d = L.Territoires.donnees(), r = L.Territoires.rectangle(d, ilot);
        return { x: (r.x0 + 4) * 16 + 8, y: (r.y0 + 4) * 16 + 8 };
    }
    function ilots(L, gang) {
        const d = L.Territoires.donnees();
        return Object.keys(d.ilots).map(function (k) { return d.ilots[k]; })
            .filter(function (i) { return L.Territoires.tenuPar(i) === gang; });
    }
"""


def test_une_partie_neuve_n_a_rien_de_pris_et_la_cour_reste_la_cour(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const T = L.Territoires, d = T.donnees(), p = L.B.partie;
        const coeur = Object.keys(d.ilots).map(function (k) { return d.ilots[k]; }).find(function (i) { return i.coeur && i.gang === 'cravates'; });
        const autre = ilots(L, 'cravates').find(function (i) { return !i.coeur; });
        const c = tuileDe(L, coeur), a = tuileDe(L, autre);
        return { pris: Object.keys(p.territoires).length, force: T.force('cravates'),
                 dansLaCour: T.gangA(c.x, c.y), ailleurs: T.gangA(a.x, a.y), gangs: d.gangs.length };
    }""")
    assert r["pris"] == 0 and r["force"] == 100 and r["gangs"] == 6, r
    assert r["dansLaCour"] == "cravates" and r["ailleurs"] is None, r


def test_un_membre_couche_compte_une_fois(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const T = L.Territoires, j = L.B.joueur;
        const m = L.Entites.creerPieton(j.x + 30, j.y, L.Entites.archetype('cravate'));
        L.Entites.blesser(m, 999, j, { assomme: true });
        L.Entites.blesser(m, 999, j, { assomme: true });
        const apres = T.force('cravates');
        const passant = L.Entites.creerPieton(j.x - 30, j.y, null);
        L.Entites.blesser(passant, 999, j, { assomme: true });
        return { gang: m.gang, apres: apres, toujours: T.force('cravates'), coup: T.donnees().regles.coup };
    }""")
    assert r["gang"] == "cravates", r
    assert r["apres"] == 100 - r["coup"] and r["toujours"] == r["apres"], r


def test_la_nuit_le_plus_fort_prend_un_coin_jamais_le_coeur(banc):
    """Les Cravates affaiblies : chaque nuit, un de leurs îlots passe à un voisin — un seul par voisin plus fort ;
    au bout de soixante nuits, leur cœur est toujours à elles. ⚠️ Le témoin : à forces égales, rien ne bouge."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie, d = T.donnees();
        const egales = T.nuit().length;
        const avant = ilots(L, 'cravates').length;
        p.forcesDesGangs.cravates = 0;
        p.jour = 7;
        const prises = T.nuit();
        const une = { prises: prises.map(function (q) { return q.gang + '>' + q.a; }), apres: ilots(L, 'cravates').length,
                      ligne: T.ligneDuClairon(prises), prise: prises[0] && d.ilots[prises[0].k] };
        for (let n = 0; n < 60; n++) { p.forcesDesGangs.cravates = 0; p.jour++; T.nuit(); }
        const coeur = Object.keys(d.ilots).map(function (k) { return d.ilots[k]; }).filter(function (i) { return i.coeur && i.gang === 'cravates'; });
        const g = une.prise && tuileDe(L, une.prise);
        return { egales: egales, avant: avant, une: une, coeurGarde: coeur.every(function (i) { return T.tenuPar(i) === 'cravates'; }),
                 restent: ilots(L, 'cravates').length, gangIci: g ? T.gangA(g.x, g.y) : null };
    }""")
    assert r["egales"] == 0, "à forces égales, un îlot a changé de mains"
    u = r["une"]
    assert u["prises"] and all(p.endswith(">cravates") for p in u["prises"]), u
    assert len(set(u["prises"])) == len(u["prises"]), "deux îlots pris par le même voisin la même nuit"
    assert u["apres"] == r["avant"] - len(u["prises"]), u
    assert u["prise"]["coeur"] is False and u["ligne"] and "CRAVATES" in u["ligne"], u
    assert r["coeurGarde"] and r["restent"] >= 4, r
    assert r["gangIci"] and r["gangIci"] != "cravates", "l'îlot pris n'est pas à son nouveau gang"


def test_un_district_libere_sort_du_jeu(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie;
        p.libere = ['faubourg'];
        p.forcesDesGangs.cravates = 0;
        const prises = T.nuit();
        return prises.filter(function (q) { return q.a === 'cravates' || q.gang === 'cravates'; }).length;
    }""")
    assert r == 0, "on grignote un district libéré"


def test_l_ilot_pris_se_peuple_de_son_nouveau_gang_et_survit_a_la_sauvegarde(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const T = L.Territoires, B = L.B, p = B.partie;
        p.forcesDesGangs.cravates = 0; p.jour = 3;
        const q = T.nuit()[0], i = T.donnees().ilots[q.k], t = tuileDe(L, i);
        B.joueur.x = t.x; B.joueur.y = t.y; L.Monde.centrerCamera(t.x, t.y); L.Entites.indexer();
        let vus = 0;
        for (let k = 0; k < 900 && !vus; k++) {
            o.frame(1);
            vus = B.entites.filter(function (e) { return e.gang === q.gang; }).length;
        }
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), B.defs);
        return { gang: q.gang, vus: vus, relu: relue.territoires[q.k], force: relue.forcesDesGangs.cravates };
    }""")
    assert r["vus"] > 0, f"aucun membre des {r['gang']} dans l'îlot qu'ils ont pris"
    assert r["relu"] == r["gang"] and r["force"] is not None, r


# --- Vague 2 : reprendre un coin, le nom sous la mini-carte, la légende --------------------------------------

PRENDRE = """
    function prendre(L) {
        const T = L.Territoires, p = L.B.partie;
        p.forcesDesGangs.cravates = 0; p.jour = 3;
        const q = T.nuit()[0], i = T.donnees().ilots[q.k];
        const d = T.donnees();
        return { q: q, i: i, x: (d.x[i.bx] + 4) * 16 + 8, y: (d.y[i.by] + d.y0 + 4) * 16 + 8 };
    }
    function coucher(L, gang, x, y) {
        const g = L.B.defs.pietons.gangs.find(function (q) { return q.slug === gang; });
        const m = L.Entites.creerPieton(x, y, L.Entites.archetype(g.pieton));
        L.Entites.blesser(m, 999, L.B.joueur, { assomme: true });
    }
"""


def test_quatre_membres_couches_le_meme_jour_reprennent_le_coin(banc):
    """Dans l'îlot qu'un gang a pris : trois de ses membres couchés, le coin est encore à lui ; le quatrième, et il
    revient au gang de son district. ⚠️ Les témoins : trois un jour et un le lendemain ne suffisent pas ; un
    membre couché hors de l'îlot ne compte pas, ni un d'un autre gang que l'occupant."""
    r = banc("function (L, o) {" + PRENDRE + """
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie;
        const a = prendre(L), out = {};
        // Le lendemain remet le compte à zéro.
        for (let n = 0; n < 3; n++) coucher(L, a.q.gang, a.x, a.y);
        p.jour++;
        coucher(L, a.q.gang, a.x, a.y);
        out.lendemain = p.territoires[a.q.k] || null;
        // Hors de l'îlot : rien.
        coucher(L, a.q.gang, 20 * 16, (L.B.defs.decalage_nord + 20) * 16);
        out.dehors = p.territoires[a.q.k] || null;
        // D'un autre gang que l'occupant : rien, même quatre.
        p.jour++;
        const autre = a.q.gang === 'cravates' ? 'morues' : 'cravates';
        for (let n = 0; n < 4; n++) coucher(L, autre, a.x, a.y);
        out.autre = p.territoires[a.q.k] || null;
        // Le même jour : trois, puis le quatrième.
        p.jour++;
        for (let n = 0; n < 3; n++) coucher(L, a.q.gang, a.x, a.y);
        out.trois = p.territoires[a.q.k] || null;
        out.message3 = L.B.msg;
        coucher(L, a.q.gang, a.x, a.y);
        out.quatre = p.territoires[a.q.k] || null;
        out.message4 = L.B.msg;
        out.gang = a.q.gang;
        return out;
    }""")
    g = r["gang"]
    assert r["lendemain"] == g and r["dehors"] == g and r["autre"] == g and r["trois"] == g, r
    assert "COIN DISPUTÉ" in (r["message3"] or ""), r
    assert r["quatre"] is None, "quatre membres couchés et le coin n'est pas repris"
    assert "LE COIN EST REPRIS" in (r["message4"] or ""), r


def test_le_nom_sous_la_mini_carte_et_la_legende_disent_qui_tient_le_coin(banc):
    r = banc("function (L, o) {" + PRENDRE + """
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie, j = L.B.joueur;
        const a = prendre(L);
        j.x = a.x; j.y = a.y;
        const ici = L.Hud.nomIci(j);
        const c = o.doc.createElement('canvas').getContext('2d');
        c.traces = [];
        T.dessinerLaLegende(c, 8, 30);
        const couleur = T.couleurDe(a.q.gang);
        const puce = c.traces.some(function (t) { return t[4] === couleur; });
        p.territoires = {};
        const vide = o.doc.createElement('canvas').getContext('2d');
        vide.traces = [];
        T.dessinerLaLegende(vide, 8, 30);
        return { ici: ici, nom: T.nomDe(a.q.gang), puce: puce, videRien: vide.traces.length === 0, apres: L.Hud.nomIci(j) };
    }""")
    assert r["ici"] == {"nom": r["nom"], "gang": r["ici"]["gang"]} and r["ici"]["gang"], r
    assert r["puce"] and r["videRien"], r
    assert r["apres"]["gang"] is None, "un coin rendu se dit encore comme un territoire de gang"


# --- Vague 3 : les graffitis suivent la frontière ------------------------------------------------------------------


def test_un_coin_pris_porte_les_tags_de_qui_le_tient_sur_ses_murs_nus(banc):
    """Un îlot pris se tague aux mots de son nouveau gang : sur un mur nu (`F`, `d`) qu'on voit du trottoir, jamais
    sur une vitrine, une résidence ou un tag déjà là, au plus trois par îlot. ⚠️ Les témoins : rien de pris, rien de
    tagué ; et rendu puis repris, les mêmes tags aux mêmes murs (l'empreinte, pas un dé)."""
    r = banc("function (L, o) {" + PRENDRE + """
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie, carte = L.B.carte, def = L.B.defs.carte;
        const rien = T.tagsDeLaFrontiere(carte).length;
        const a = prendre(L);
        const tags = T.tagsDeLaFrontiere(carte);
        const reserves = new Set();
        (def.devantures || []).concat(def.residences || []).forEach(function (d) {
            for (let i = 0; i < d.l; i++) reserves.add((d.x + i) + ',' + d.y);
        });
        def.graffitis.forEach(function (g) { reserves.add(g.x + ',' + g.y); });
        const pres = function (t) {
            return def.graffitis.some(function (g) { return Math.abs(g.x - t.x) + Math.abs(g.y - t.y) < 4; });
        };
        const mots = L.B.defs.pietons.territoires.tags;
        const parIlot = {}, mal = [];
        const avant = JSON.stringify(tags), pris = Object.assign({}, p.territoires);
        const dansLaPrise = tags.filter(function (t) { return T.ilotA(t.x, t.y).k === a.q.k; }).length;
        // Puis TOUTE la ville prise (chaque îlot au gang d'à côté) : des centaines de murs à juger, pas trois.
        const d = T.donnees();
        Object.keys(d.ilots).forEach(function (k) {
            const i = d.ilots[k];
            p.territoires[k] = d.gangs[(d.gangs.indexOf(i.gang) + 1) % d.gangs.length];
        });
        const tous = T.tagsDeLaFrontiere(carte);
        tous.forEach(function (t) {
            const i = T.ilotA(t.x, t.y), g = carte.sol[t.y][t.x];
            if (i) parIlot[i.k] = (parIlot[i.k] || 0) + 1;
            if (!i || p.territoires[i.k] !== t.gang) mal.push(['pas chez lui', t]);
            else if (g !== 'F' && g !== 'd') mal.push(['pas un mur', g, t]);
            else if (carte.solide[(t.y + 1) * carte.w + t.x]) mal.push(['mur qui ne se voit pas', t]);
            else if (reserves.has(t.x + ',' + t.y)) mal.push(['mur deja pris', t]);
            else if (pres(t)) mal.push(['colle a un vieux tag', t]);
            else if (!mots[t.gang].some(function (m) { return m[0] === t.texte; })) mal.push(['pas son mot', t]);
        });
        p.territoires = {};
        const rendu = T.tagsDeLaFrontiere(carte).length;
        p.territoires = pris;
        return { rien: rien, n: tous.length, dansLaPrise: dansLaPrise, max: Math.max.apply(null, Object.values(parIlot)),
                 mal: mal.slice(0, 5), rendu: rendu, memes: JSON.stringify(T.tagsDeLaFrontiere(carte)) === avant };
    }""")
    assert r["rien"] == 0, "une partie neuve tague déjà la frontière"
    assert r["mal"] == [], r["mal"]
    assert r["dansLaPrise"] >= 1 and r["max"] <= 3 and r["n"] >= 100, r
    assert r["rendu"] == 0 and r["memes"], r


def test_le_tag_du_perdant_est_barre_a_la_couleur_de_qui_tient_le_coin(banc):
    """Un tag de gang cuit dans la ville, dans un îlot qu'un AUTRE gang tient : barré, à la couleur du tenant.
    ⚠️ Les témoins : l'îlot rendu, ou tenu par le gang qui a signé, ou un tag libre — pas de trait."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie;
        const tags = L.B.defs.carte.graffitis;
        const g = tags.find(function (t) { return t.motif !== 1 && T.gangDuTag(t.texte) && T.ilotA(t.x, t.y); });
        const libre = tags.find(function (t) { return t.motif !== 1 && !T.gangDuTag(t.texte) && T.ilotA(t.x, t.y); });
        const signe = T.gangDuTag(g.texte), i = T.ilotA(g.x, g.y);
        const autre = T.donnees().gangs.find(function (q) { return q !== signe; });
        const vierge = T.barre(g);
        p.territoires[i.k] = autre;
        const barre = T.barre(g);
        p.territoires[T.ilotA(libre.x, libre.y).k] = autre;
        const libreBarre = T.barre(libre);
        p.territoires[i.k] = signe;
        const siens = T.barre(g);
        return { vierge: vierge, barre: barre, couleur: T.bombeDe(autre), libreBarre: libreBarre, siens: siens,
                 texte: g.texte };
    }""")
    assert r["vierge"] is None and r["siens"] is None and r["libreBarre"] is None, r
    assert r["barre"] and r["barre"]["couleur"] == r["couleur"] and 1 <= r["barre"]["tuiles"] <= 3, r


def test_la_frontiere_qui_bouge_recuit_les_morceaux_de_la_ville(banc):
    """Les tags sont peints DANS les morceaux de carte : quand un îlot change de mains, le morceau déjà peint se
    repeint — le tag neuf y paraît, et le vieux tag de gang de l'îlot passe par le trait. ⚠️ Le témoin : sans
    changement, le morceau reste en cache (rien ne se repeint)."""
    r = banc("function (L, o) {" + PRENDRE + """
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie, carte = L.B.carte, M = L.Monde;
        const a = prendre(L);
        const t = T.tagsDeLaFrontiere(carte).find(function (q) { return T.ilotA(q.x, q.y).k === a.q.k; });
        const pris = Object.assign({}, p.territoires);
        p.territoires = {};
        const vus = [], vraiGraffiti = L.FACADES.graffiti;
        L.FACADES.graffiti = function (ctx, gr) { vus.push(gr); return vraiGraffiti.apply(this, arguments); };
        const ctx = o.doc.createElement('canvas').getContext('2d');
        const cam = { x: t.x * 16 - 240, y: t.y * 16 - 135 };
        M.dessinerSol(ctx, cam);
        const avant = vus.filter(function (q) { return q === t; }).length;
        vus.length = 0;
        M.dessinerSol(ctx, cam);
        const enCache = vus.length;
        p.territoires = pris;
        M.dessinerSol(ctx, cam);
        const apres = vus.filter(function (q) { return q.x === t.x && q.y === t.y && q.gang === t.gang; }).length;
        L.FACADES.graffiti = vraiGraffiti;
        return { avant: avant, enCache: enCache, apres: apres, laVille: carte.laVille };
    }""")
    assert r["laVille"] is True, r
    assert r["avant"] == 0 and r["enCache"] == 0, r
    assert r["apres"] >= 1, "la frontière a bougé et le morceau garde son ancienne peinture"


def test_le_morceau_peint_le_trait_sur_le_vieux_tag(banc):
    """Le trait se PEINT : le morceau qui porte un vieux tag de gang, dans un îlot qu'un autre tient, passe un trait
    de bombe (des carrés de deux, à la couleur du tenant) en travers. ⚠️ Le témoin : l'îlot rendu, pas de trait."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const T = L.Territoires, p = L.B.partie, M = L.Monde;
        const g = L.B.defs.carte.graffitis.find(function (t) { return t.motif !== 1 && T.gangDuTag(t.texte) && T.ilotA(t.x, t.y); });
        const autre = T.donnees().gangs.find(function (q) { return q !== T.gangDuTag(g.texte); });
        const couleur = T.bombeDe(autre);
        const traces = [], vrai = L.Base.nouveauCanvas;
        L.Base.nouveauCanvas = function () { const c = vrai.apply(this, arguments); c.getContext('2d').traces = traces; return c; };
        const ctx = o.doc.createElement('canvas').getContext('2d');
        const cam = { x: g.x * 16 - 240, y: g.y * 16 - 135 };
        const traits = function () {
            return traces.filter(function (t) { return t[4] === couleur && t[2] === 2 && t[3] === 2
                && t[0] >= (g.x % 16) * 16 && t[0] < (g.x % 16) * 16 + 48 && t[1] >= (g.y % 16) * 16 && t[1] < (g.y % 16) * 16 + 16; }).length;
        };
        p.territoires[T.ilotA(g.x, g.y).k] = autre;
        M.dessinerSol(ctx, cam);
        const barre = traits();
        traces.length = 0;
        p.territoires = {};
        M.dessinerSol(ctx, cam);
        const rendu = traits();
        L.Base.nouveauCanvas = vrai;
        return { barre: barre, rendu: rendu };
    }""")
    assert r["barre"] >= 6, r
    assert r["rendu"] == 0, r
