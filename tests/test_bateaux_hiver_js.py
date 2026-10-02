"""Les bateaux ne sont pas des chars, vague 5 — le sillage, et l'hiver de la baie.

Une coque qui file laisse son sillage (deux bras d'écume qui s'ouvrent, le bouillon de l'hélice), le traversier
aussi. L'hiver (une partie commence en janvier) : la glace de rive, les glaces flottantes qui dérivent, le chenal
du traversier, les chaloupes de plaisance sur leurs bers à quai, les bouées de la régate retirées — et une coque qui
entre dans la glace la croque et y perd son erre.

⚠️ Chaque juge POSE SA SAISON (`jour = 2` : janvier ; `jour = 22` : juillet, le 21 est le déménagement)."""

import pytest

AIDES = """
    function pleinLarge(L, r) {
        const c = L.Monde.carte; r = r || 4;
        for (let ty = 8; ty < c.h - 8; ty++) for (let tx = 8; tx < c.w - 8; tx++) {
            let plein = true;
            for (let dy = -r; dy <= r && plein; dy++) for (let dx = -r; dx <= r && plein; dx++) if (!L.Monde.estEau(tx + dx, ty + dy)) plein = false;
            if (plein) return { x: tx * L.TT + 8, y: ty * L.TT + 8, tx: tx, ty: ty };
        }
        return null;
    }
    function saison(L, jour, heure) {
        const p = L.B.partie; p.jour = jour; p.heure = heure === undefined ? 11 / 24 : heure; p.dette = 0;
        L.B.joueur.invincible = 1e9;
    }
    /** Un faux contexte 2D qui note ce qu'on y peint. */
    function toile() {
        const t = { rects: [], images: 0, remplis: 0, fillStyle: '', globalAlpha: 1, strokeStyle: '', lineWidth: 1, font: '', textAlign: '' };
        t.fillRect = function (x, y, w, h) { t.rects.push([x, y, w, h, t.fillStyle]); };
        t.drawImage = function () { t.images++; };
        t.rect = function (x, y, w, h) { t.rects.push([x, y, w, h, t.fillStyle]); };      // les lots : un chemin de rectangles
        t.fill = function () { t.remplis++; };
        ['save', 'restore', 'beginPath', 'closePath', 'clip', 'moveTo', 'lineTo', 'arc', 'fillText', 'stroke'].forEach(function (k) { t[k] = function () {}; });
        return t;
    }
    /** Compter les dés tirés pendant `f`. */
    function des(L, f) {
        const vrai = L.B.rng; let n = 0;
        L.B.rng = function () { n++; return vrai.apply(this, arguments); };
        try { f(); } finally { L.B.rng = vrai; }
        return n;
    }
"""


# --- Le sillage -------------------------------------------------------------------------------------------------


def test_une_coque_qui_file_laisse_un_sillage_qui_s_ouvre(banc):
    """L'été, une chaloupe lancée au plein large : des points derrière sa poupe, et plus ils sont vieux, plus les
    deux bras s'écartent. Arrêtée, elle n'en laisse aucun."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); saison(L, 22, 13 / 24);
        const p = pleinLarge(L, 6), j = L.B.joueur;
        const v = L.Vehicules.creer('bateau', p.x - 60, p.y, 0, { etat: 'stationne' });
        j.x = v.x; j.y = v.y; L.Vehicules.monter(j, v); v.vole = true;
        v.vitesse = 3; v.vx = 3; v.vy = 0;
        const w = L.Vehicules.creer('bateau', p.x, p.y + 40, 0, { etat: 'stationne' });
        o.frame(40);
        const pts = L.Sillage.points(v), immobile = L.Sillage.points(w).length;
        const S = L.Sillage, vieux = pts[0], jeune = pts[pts.length - 1];
        const ecart = function (q) { const a = S.bras(q, L.B.t - q.n, 1), b = S.bras(q, L.B.t - q.n, -1); return Math.hypot(a.x - b.x, a.y - b.y); };
        const derriere = pts.every(function (q) { return (q.x - v.x) * Math.cos(v.angle) + (q.y - v.y) * Math.sin(v.angle) < 0; });
        return { n: pts.length, immobile: immobile, derriere: derriere, vieux: ecart(vieux), jeune: ecart(jeune) };
    }""")
    assert r["n"] >= 10, f"une coque qui file ne laisse pas de sillage : {r}"
    assert r["derriere"], f"le sillage n'est pas derrière la poupe : {r}"
    assert r["vieux"] > r["jeune"] + 4, f"les bras du sillage ne s'ouvrent pas : {r}"
    assert r["immobile"] == 0, f"une coque arrêtée laisse un sillage : {r}"


def test_le_sillage_ne_se_peint_que_sur_l_eau_et_ne_tire_aucun_de(banc):
    """Une chaloupe qui longe un quai : aucune goutte d'écume sur la terre ; et ni la trace ni le dessin ne tirent
    un dé (le décor ne décale pas le hasard de la ville)."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); saison(L, 22, 13 / 24);
        const c = L.Monde.carte, M = L.Monde, TT = L.TT, j = L.B.joueur;
        // Une rangée d'eau franche, la terre juste au nord : on y file vers l'est, à ras du quai.
        let p = null;
        for (let ty = 10; ty < c.h - 10 && !p; ty++) for (let tx = 10; tx < c.w - 20 && !p; tx++) {
            let ok = true;
            for (let k = 0; k < 24 && ok; k++) ok = !M.estEau(tx + k, ty - 1) && M.estEau(tx + k, ty) && M.estEau(tx + k, ty + 1) && M.estEau(tx + k, ty + 2);
            if (ok) p = { x: tx * TT + 8, y: ty * TT + 10 };
        }
        const v = L.Vehicules.creer('bateau', p.x, p.y, 0, { etat: 'stationne' });
        j.x = v.x; j.y = v.y; L.Vehicules.monter(j, v); v.vole = true;
        let n = 0;
        for (let k = 0; k < 90; k++) { v.vitesse = 3; v.vx = 3; v.vy = 0; n += des(L, function () { L.Sillage.maj(); }); o.frame(1); }
        L.Monde.centrerCamera(v.x, v.y);
        const t = toile(), vue = { x: L.B.cam.x, y: L.B.cam.y };
        n += des(L, function () { L.Sillage.dessiner(t, vue); });
        const surTerre = t.rects.filter(function (q) { return !M.estEau(Math.floor((q[0] + vue.x) / TT), Math.floor((q[1] + vue.y) / TT)); });
        return { gouttes: t.rects.length, surTerre: surTerre.length, des: n };
    }""")
    assert r["gouttes"] > 20, f"le sillage ne se peint pas : {r}"
    assert r["surTerre"] == 0, f"de l'écume sur le quai : {r}"
    assert r["des"] == 0, f"le sillage tire des dés : {r}"


def test_le_traversier_a_son_sillage_quand_il_traverse(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); saison(L, 22, 0);
        const T = L.Traversier, d = T.donnees();
        // Une heure en pleine traversée : la moitié du trajet aller.
        let h = 0;
        for (let k = 0; k < 2400; k++) { const e = T.etatA(k / 2400); if (e && e.phase === 'traverse' && e.u > 0.4 && e.u < 0.6) { h = k / 2400; break; } }
        L.B.partie.heure = h;
        const ici = T.placeA(h), j = L.B.joueur; j.x = ici.x + d.largeurPx / 2; j.y = ici.y - 60; L.Monde.centrerCamera(j.x, j.y);
        o.frame(30);
        const aQuai = T.etatA(L.B.partie.heure).phase;
        return { n: L.Sillage.points('traversier').length, phase: aQuai };
    }""")
    assert r["phase"] == "traverse", r
    assert r["n"] >= 5, f"le traversier traverse sans sillage : {r}"


# --- L'hiver : la glace ------------------------------------------------------------------------------------------


def test_la_glace_ne_prend_la_baie_que_l_hiver_et_derive_sans_de(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const B = L.BaieDHiver, p = pleinLarge(L, 6), M = L.Monde, TT = L.TT;
        const out = {};
        for (const jour of [2, 5, 9, 14, 22, 32, 38]) { saison(L, jour); out[jour] = B.couverture(); }
        saison(L, 2, 11 / 24);
        const zone = [p.x - 600, p.y - 600, p.x + 600, p.y + 600];
        let n = 0, a = null, b = null;
        n += des(L, function () { a = B.glacesDans.apply(null, zone); b = B.glacesDans.apply(null, zone); });
        L.B.partie.heure += 1 / 24;
        const c = B.glacesDans.apply(null, zone);
        const surTerre = a.filter(function (g) { return !M.estEau(Math.floor(g.x / TT), Math.floor(g.y / TT)); }).length;
        // Le chenal du traversier : à mi-chemin entre ses quais, les glaces s'écartent de sa route.
        const sg = B.leChenal().segments[0], mx = (sg.a[0] + sg.b[0]) / 2, my = (sg.a[1] + sg.b[1]) / 2;
        const autour = B.glacesDans(mx - 400, my - 300, mx + 400, my + 300);
        const dansLeChenal = autour.filter(function (g) { return B.dansLeChenal(g.x, g.y, 0); }).length;
        return { cov: out, n: a.length, autour: autour.length, pareil: JSON.stringify(a) === JSON.stringify(b), bouge: JSON.stringify(a) !== JSON.stringify(c),
                 des: n, surTerre: surTerre, chenal: dansLeChenal };
    }""")
    cov = {int(k): v for k, v in r["cov"].items()}
    assert cov[2] > 0.3 and cov[5] > cov[38] > 0 and cov[9] > 0, f"la baie ne prend pas l'hiver : {cov}"
    assert cov[14] == cov[22] == cov[32] == 0, f"de la glace hors de l'hiver : {cov}"
    assert r["n"] > 10, r
    assert r["pareil"] and r["des"] == 0, f"les glaces ne sont pas une pure fonction de l'heure : {r}"
    assert r["bouge"], f"les glaces ne dérivent pas : {r}"
    assert r["autour"] > 10, r
    assert r["surTerre"] == 0 and r["chenal"] == 0, f"une glace sur la terre ou dans le chenal du traversier : {r}"


def test_la_glace_de_rive_colle_aux_quais_l_hiver(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const B = L.BaieDHiver, M = L.Monde, TT = L.TT, c = M.carte, quais = B.leChenal().quais;
        // Une tuile d'eau dont la voisine du nord est de la terre (hors des quais du traversier) : on lit au ras du bord.
        let t = null;
        for (let ty = 10; ty < c.h - 10 && !t; ty++) for (let tx = 10; tx < c.w - 10 && !t; tx++) {
            if (M.estEau(tx, ty) && !M.estEau(tx, ty - 1) && M.estEau(tx, ty + 1) && M.estEau(tx, ty + 2) && !quais.has(ty * c.w + tx)) t = { tx: tx, ty: ty };
        }
        const x = t.tx * TT + 8, bord = t.ty * TT + 1, large = t.ty * TT + 30;
        saison(L, 2);
        const hiver = { bord: B.surLaRive(x, bord), large: B.surLaRive(x, large) };
        saison(L, 22);
        const ete = { bord: B.surLaRive(x, bord), large: B.surLaRive(x, large) };
        return { hiver: hiver, ete: ete };
    }""")
    assert r["hiver"]["bord"], f"pas de glace de rive au ras du quai en janvier : {r}"
    assert not r["hiver"]["large"], f"la glace de rive s'étend à deux tuiles du bord : {r}"
    assert not r["ete"]["bord"], f"de la glace de rive en juillet : {r}"


@pytest.mark.parametrize("graine", [0x1A2B3C4D, 7, 2026])
def test_a_la_barre_la_glace_croque_et_prend_l_erre(banc, graine):
    """Janvier : la chaloupe du joueur, lancée droit sur une glace flottante — elle la croque une fois (le son, la
    barre qui tremble), et elle y perd son erre bien plus vite qu'en eau libre. Juillet, au même endroit : rien.
    ⚠️ Le trafic coupé : un juge qui CONDUIT ne laisse rien lui rentrer dedans."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        L.B.defs.conduite.trafic.vehicules_max = 0;
        const B = L.BaieDHiver, V = L.Vehicules, j = L.B.joueur, p = pleinLarge(L, 6);
        saison(L, 2, 11 / 24);
        // Une glace flottante de bonne taille, en eau franche autour : on part 34 px à l'ouest, cap plein est.
        const g = B.glacesDans(p.x - 900, p.y - 900, p.x + 900, p.y + 900).filter(function (q) {
            for (let dx = -60; dx <= 0; dx += 4) if (dx < -q.rx - 2 && B.dansLaGlace(q.x + dx, q.y)) return false;
            return q.rx > 12 && B.dansLaGlace(q.x - q.rx + 4, q.y) && !B.surLaRive(q.x - 40, q.y);
        })[0];
        function essai() {
            const v = V.creer('bateau', g.x - g.rx - 34, g.y, 0, { etat: 'stationne' });
            j.x = v.x; j.y = v.y; V.monter(j, v); v.vole = true;
            v.vitesse = 2.6; v.vx = 2.6; v.vy = 0; L.B.cam.secousse = 0;
            let croque = 0, secousse = 0; const vrai = L.Son.SFX.glaceCoque;
            L.Son.SFX.glaceCoque = function () { croque++; };
            const vitesses = [];
            for (let k = 0; k < 24; k++) {
                V.majPhysique(v, { gaz: 0, frein: 0, direction: 0, freinMain: false }); V.avancer(v);
                secousse = Math.max(secousse, L.B.cam.secousse || 0); vitesses.push(v.vitesse);
            }
            L.Son.SFX.glaceCoque = vrai;
            V.descendre(j, true); L.Entites.retirer(v);
            return { croque: croque, secousse: secousse, fin: v.vitesse, x: v.x };
        }
        const hiver = essai();
        saison(L, 22, 13 / 24);
        const ete = essai();
        return { hiver: hiver, ete: ete, g: g && { rx: g.rx } };
    }""", graine=graine)
    h, e = r["hiver"], r["ete"]
    assert h["croque"] == 1, f"la coque entre dans la glace sans la croquer (ou la croque à chaque image) : {r}"
    assert h["secousse"] > 0.2, f"la barre ne tremble pas : {r}"
    assert h["fin"] < e["fin"] * 0.75, f"la glace ne prend pas d'erre à la coque : {r}"
    assert e["croque"] == 0 and e["secousse"] < 0.05, f"de la glace en juillet : {r}"


# --- L'hiver : les chaloupes sur leurs bers, les bouées --------------------------------------------------------


def test_l_hiver_les_chaloupes_de_plaisance_sont_sur_leurs_bers(banc):
    """À portée d'un amarrage (hors champ) : l'été, une chaloupe y naît ; l'hiver, aucune — et celle du décor qui y
    dormait rentre ; celle d'une mission et celle du joueur restent à l'eau. Le ber se peint l'hiver, pas l'été, et pas
    à côté d'une coque à l'eau."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const V = L.Vehicules, B = L.BaieDHiver, j = L.B.joueur, TT = L.TT;
        const ber = B.lesBers()[0], place = ber.place;
        const ici = function () { return L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.amarrage === place; }); };
        function loin() { j.x = place.x * TT + 8 + 420; j.y = place.y * TT + 8; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer(); }
        saison(L, 22, 13 / 24); loin();
        ici().forEach(function (e) { L.Entites.retirer(e); });
        V.majAmarrages();
        const ete = ici().length;
        ici().forEach(function (e) { L.Entites.retirer(e); });      // le ber se juge sans coque à l'eau
        const vue = { x: ber.x - 200, y: ber.y - 130 };
        let t = toile(); B.dessinerBers(t, vue); const berEte = t.images;
        saison(L, 2); V.majAmarrages();
        const hiverDecor = ici().length;
        t = toile(); B.dessinerBers(t, vue); const berHiver = t.images;
        // Une mission y a sa chaloupe : elle reste, et le ber ne se peint pas à côté d'elle.
        const m = V.creer('bateau', place.x * TT + 8, place.y * TT + 8, 0, { etat: 'stationne', mission: 'm52', couleur: '#ecf0f1' });
        m.amarrage = place; V.majAmarrages();
        const mission = ici().indexOf(m) >= 0;
        t = toile(); B.dessinerBers(t, vue); const berAvecCoque = t.images;
        return { ete: ete, berEte: berEte, hiverDecor: hiverDecor, berHiver: berHiver, mission: mission, berAvecCoque: berAvecCoque, n: B.lesBers().length };
    }""")
    assert r["ete"] == 1, f"l'été, pas de chaloupe à l'amarrage : {r}"
    assert r["berEte"] == 0, f"un ber peint en juillet : {r}"
    assert r["hiverDecor"] == 0, f"l'hiver, la chaloupe du décor reste à l'eau : {r}"
    assert r["berHiver"] >= 1, f"l'hiver, pas de ber à quai : {r}"
    assert r["mission"], f"l'hiver, la chaloupe d'une mission est remisée : {r}"
    assert r["berAvecCoque"] == r["berHiver"] - 1, f"un ber vide peint à côté de la chaloupe à l'eau : {r}"
    assert r["n"] >= 10, f"trop peu de bers dans la ville : {r}"


def test_les_bers_sont_sur_un_quai_ou_une_greve_jamais_sur_un_trottoir(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const c = L.Monde.carte;
        return L.BaieDHiver.lesBers().map(function (b) {
            const tx = Math.floor(b.x / 16), ty = Math.floor(b.y / 16);
            return { g: L.Monde.glyphe(tx, ty), route: c.route[ty * c.w + tx], solide: c.solide[ty * c.w + tx],
                     loin: Math.max(Math.abs(tx - b.place.x), Math.abs(ty - b.place.y)) };
        });
    }""")
    assert r, "aucun ber"
    for b in r:
        assert b["g"] in ("Q", "s", "g", ","), b
        assert not b["route"] and b["solide"] == 0 and b["loin"] <= 2, b


def test_l_hiver_les_bouees_de_la_regate_sont_retirees_sauf_pendant_une_course(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const b = L.Regate.parcours(), vue = { x: b[0][0] * 16 - 240, y: b[0][1] * 16 - 135 };
        const compte = function () { const t = toile(); L.Regate.dessiner(t, vue); return t.rects.length; };
        saison(L, 22, 13 / 24); const ete = compte();
        saison(L, 2); const hiver = compte();
        L.B.mission = { course: { i: 0, points: [] } }; const course = compte(); L.B.mission = null;
        return { ete: ete, hiver: hiver, course: course };
    }""")
    assert r["ete"] > 0, r
    assert r["hiver"] == 0, f"les bouées de course restent sur la baie en janvier : {r}"
    assert r["course"] > 0, f"une course d'hiver n'a plus ses bouées : {r}"


def test_la_baie_d_hiver_se_peint_sans_un_de(banc):
    """La glace et les bers se peignent à l'écran en janvier, et pas en juillet — sans un dé."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const B = L.BaieDHiver, p = pleinLarge(L, 6), vue = { x: p.x - 240, y: p.y - 135 };
        saison(L, 2);
        const t = toile(); let n = des(L, function () { B.dessiner(t, vue); B.dessinerBers(t, vue); });
        saison(L, 22, 13 / 24);
        const u = toile(); n += des(L, function () { B.dessiner(u, vue); B.dessinerBers(u, vue); });
        return { hiver: t.rects.length + t.remplis, ete: u.rects.length + u.remplis + u.images, des: n };
    }""")
    assert r["hiver"] > 30, f"la baie ne se peint pas l'hiver : {r}"
    assert r["ete"] == 0, f"de la glace peinte en juillet : {r}"
    assert r["des"] == 0, r
