"""Le vrai dérapage (`static/js/derapage.js`, les quatre saisons, lot 6) : au sec, la même conduite au
pixel ; sur la glace, le char sous-vire, le frein à main fait partir l'arrière, le contre-braquage
rattrape, les roues bloquées ne dirigent pas, et les pneus d'hiver rendent une part de tout ça."""

#: Un char lancé, piloté image par image par un script, sur une adhérence donnée (la neige, bouchée).
#: `script(k)` rend la commande de l'image k. On mesure la rotation CUMULÉE (`cap`), l'écart entre le cap
#: et la direction réelle (`derive`) et le lacet.
PILOTE = """
    function piloter(L, adherence, script, n, opts) {
        const j = L.B.joueur, V = L.Vehicules, N = L.Neige;
        const vraie = N.adherence, vraiFrein = N.frein, P = L.Pluie, M = L.Monde;
        const vraiesP = [P.adherence, P.frein], vraiesM = [M.adherenceMouillee, M.freinMouille];
        // ⚠️ Le char ne bouge pas (on juge son cap et sa vitesse, pas ou il va) : pose en janvier sur un banc de neige,
        // il s'y planterait (les saisons, vague 6c). Les bancs coupes : on juge le sol.
        L.BancsDeNeige.couper(true);
        N.adherence = function () { return adherence; }; N.frein = function () { return 1; };
        // La pluie et l'arroseuse bouchees : seule la neige dit ce que le sol tient (la meteo du jour ne joue pas).
        P.adherence = P.frein = M.adherenceMouillee = M.freinMouille = function () { return 1; };
        const v = V.creer((opts && opts.slug) || 'auto', j.x + 400, j.y + 400, 0, { etat: 'stationne', couleur: '#3a6fb0' });
        v.conducteur = opts && opts.ia ? 'police' : j;       // le JOUEUR conduit, sauf un char de l'IA
        if (opts && opts.pneus) v.mods = { pneus: true };
        v.vitesse = (opts && opts.vitesse) || 3.4; v.vx = v.vitesse; v.vy = 0;
        const traj = [];
        let tourne = 0, prec = v.angle, deriveMax = 0;
        for (let k = 0; k < n; k++) {
            V.majPhysique(v, Object.assign({ gaz: 0, frein: 0, direction: 0, freinMain: false }, script(k)));
            tourne += Math.atan2(Math.sin(v.angle - prec), Math.cos(v.angle - prec)); prec = v.angle;   // l'angle est ramene entre -pi et pi
            traj.push([v.angle, v.vx, v.vy, v.lacet || 0, v.vitesse]);
            if (Math.hypot(v.vx, v.vy) > 0.5) deriveMax = Math.max(deriveMax, Math.abs(Math.atan2(Math.sin(v.angle - Math.atan2(v.vy, v.vx)), Math.cos(v.angle - Math.atan2(v.vy, v.vx)))));
        }
        N.adherence = vraie; N.frein = vraiFrein; L.BancsDeNeige.couper(false);
        P.adherence = vraiesP[0]; P.frein = vraiesP[1]; M.adherenceMouillee = vraiesM[0]; M.freinMouille = vraiesM[1];
        L.Entites.retirer(v);
        const f = traj[traj.length - 1];
        const rot = function (a, b) { let r = 0; for (let k = a + 1; k <= b && k < traj.length; k++) r += Math.atan2(Math.sin(traj[k][0] - traj[k - 1][0]), Math.cos(traj[k][0] - traj[k - 1][0])); return Math.abs(r); };
        return { traj: traj, cap: Math.abs(tourne), deriveMax: deriveMax, fin: rot(n - 15, n - 1), vitesse: Math.hypot(v.vx, v.vy), lacet: v.lacet || 0, derive: Math.abs(Math.atan2(Math.sin(f[0] - Math.atan2(f[2], f[1])), Math.cos(f[0] - Math.atan2(f[2], f[1])))), lacet: f[3] };
    }
"""


def test_au_sec_la_conduite_ne_change_pas_d_un_pixel(banc):
    r = banc("function (L, o) {" + PILOTE + """
        L.Jeu.commencer();
        const script = function (k) { return { gaz: k % 20 < 12 ? 1 : 0, direction: k < 30 ? 1 : k < 50 ? -1 : 0.5, frein: k > 70 ? 1 : 0, freinMain: k > 40 && k < 55 }; };
        const avec = piloter(L, 1, script, 90);
        L.Derapage.couper(true);
        const sans = piloter(L, 1, script, 90);
        L.Derapage.couper(false);
        const mouille = piloter(L, 0.8, script, 90);
        L.Derapage.couper(true); const mouilleSans = piloter(L, 0.8, script, 90); L.Derapage.couper(false);
        return { pareil: JSON.stringify(avec.traj) === JSON.stringify(sans.traj), different: JSON.stringify(mouille.traj) !== JSON.stringify(mouilleSans.traj) };
    }""")
    assert r["pareil"], "au sec, le dérapage change la conduite"
    assert r["different"], "sous la pluie, le dérapage ne s'éveille pas"


def test_sur_la_glace_le_char_lance_sous_vire(banc):
    r = banc("function (L, o) {" + PILOTE + """
        L.Jeu.commencer();
        const tourne = function () { return { gaz: 1, direction: 1 }; };
        return { sec: piloter(L, 1, tourne, 30).cap, glace: piloter(L, 0.3, tourne, 30).cap };
    }""")
    assert r["glace"] < 0.7 * r["sec"], f"sur la glace, le char tourne comme au sec : {r}"


def test_le_frein_a_main_en_courbe_fait_partir_l_arriere_et_le_tete_a_queue(banc):
    r = banc("function (L, o) {" + PILOTE + """
        L.Jeu.commencer();
        const courbe = function () { return { gaz: 0.6, direction: 1 }; };
        const fm = function () { return { gaz: 0.6, direction: 1, freinMain: true }; };
        return { sansFm: piloter(L, 0.3, courbe, 40), avecFm: piloter(L, 0.3, fm, 40), secFm: piloter(L, 1, fm, 40) };
    }""")
    assert r["avecFm"]["cap"] > 1.3 * r["sansFm"]["cap"], "le frein à main ne fait pas partir l'arrière"
    assert r["avecFm"]["deriveMax"] > 1.2, f"pas de tête-à-queue : le char reste dans l'axe ({r['avecFm']['deriveMax']:.2f})"
    assert r["secFm"]["deriveMax"] < r["avecFm"]["deriveMax"], "au sec, le frein à main dérape autant que sur la glace"


def test_le_contre_braquage_rattrape(banc):
    r = banc("function (L, o) {" + PILOTE + """
        L.Jeu.commencer();
        const lache = function (k) { return k < 20 ? { gaz: 0.6, direction: 1, freinMain: true } : { gaz: 0.3, direction: 0 }; };
        const contre = function (k) { return k < 20 ? { gaz: 0.6, direction: 1, freinMain: true } : { gaz: 0.3, direction: -1 }; };
        const a = piloter(L, 0.3, lache, 50), b = piloter(L, 0.3, contre, 50);
        return { lache: a, contre: b };
    }""")
    assert abs(r["contre"]["lacet"]) < 0.5 * abs(r["lache"]["lacet"]) + 1e-9, r
    assert r["contre"]["derive"] < r["lache"]["derive"], "le contre-braquage ne remet pas le char dans l'axe"


def test_les_roues_bloquees_ne_dirigent_pas(banc):
    r = banc("function (L, o) {" + PILOTE + """
        L.Jeu.commencer();
        const bloque = function () { return { frein: 1, direction: 1 }; };
        const doux = function () { return { frein: 0.5, direction: 1 }; };
        const pompe = function (k) { return { frein: k % 10 < 5 ? 1 : 0, direction: 1 }; };
        const o2 = { vitesse: 4 };
        // Les images 19 a 33 : apres que le frein tenu bloque les roues, avant l'arret.
        return { bloque: piloter(L, 0.3, bloque, 34, o2).fin, doux: piloter(L, 0.3, doux, 34, o2).fin, pompe: piloter(L, 0.3, pompe, 34, o2).fin,
                 sec: piloter(L, 1, bloque, 34, o2).fin, ia: piloter(L, 0.3, bloque, 34, Object.assign({ ia: true }, o2)).fin };
    }""")
    # Les 20 dernières images d'un freinage de 45 : tenu, le volant ne dirige plus ; pompé, il dirige encore.
    # ⚠️ Même freinage des deux côtés : un char qui freine fort roule lentement à la fin, au sec aussi.
    assert r["bloque"] < 0.3 * r["sec"], r
    assert r["ia"] > 2 * r["bloque"], "la police bloque ses roues (elle doit pouvoir faire demi-tour)"


def test_des_coups_de_frein_gardent_le_volant(banc):
    """Le clavier n'a pas de demi-frein : un frein TENU bloque les roues, des coups de frein non (on pompe,
    comme en vrai l'hiver) ; la police ne bloque jamais."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const D = L.Derapage, j = L.B.joueur;
        const v = { vitesse: 3, def: { longueur: 30 }, conducteur: j, volant: 1 };
        const f = function (frein, ia) { v.conducteur = ia ? 'police' : j; D.majLacet(v, { frein: frein }, 0.7, 0.3, 0.8); return D.volant(v, { frein: frein }, 0.7, 0.8); };
        const tenu = []; v.freinT = 0; for (let k = 0; k < 30; k++) tenu.push(f(1));
        const pompe = []; v.freinT = 0; for (let k = 0; k < 30; k++) pompe.push(f(k % 10 < 5 ? 1 : 0));
        const ia = []; v.freinT = 0; for (let k = 0; k < 30; k++) ia.push(f(1, true));
        return { tenuDebut: tenu[3], tenuFin: tenu[29], pompeMin: Math.min.apply(null, pompe), iaMin: Math.min.apply(null, ia) };
    }""")
    assert r["tenuDebut"] > 0.2 and r["tenuFin"] < 0.1, r
    assert r["pompeMin"] > 0.2, f"des coups de frein bloquent les roues : {r}"
    assert r["iaMin"] > 0.2, r


def test_les_pneus_d_hiver_rattrapent_mieux(banc):
    r = banc("function (L, o) {" + PILOTE + """
        L.Jeu.commencer();
        const tourne = function () { return { gaz: 1, direction: 1 }; };
        return { sans: piloter(L, 0.3, tourne, 30).cap, avec: piloter(L, 0.3, tourne, 30, { pneus: true }).cap, sec: piloter(L, 1, tourne, 30).cap };
    }""")
    assert r["avec"] > 1.2 * r["sans"], f"les pneus d'hiver ne se sentent pas : {r}"
    assert r["avec"] <= r["sec"] + 1e-9


def test_les_traces_au_sec_les_sillons_dans_la_neige_et_le_crissement(banc):
    r = banc("function (L, o) {" + PILOTE + """
        L.Jeu.commencer();
        const D = L.Derapage, S = L.Son; let crisse = 0;
        S.SFX.crissement = function () { crisse++; };
        const fm = function () { return { gaz: 1, direction: 1, freinMain: true }; };
        D.oublier(); piloter(L, 1, fm, 60);
        const sec = { n: D.traces().length, types: Array.from(new Set(D.traces().map(function (t) { return t.type; }))), crisse: crisse };
        crisse = 0; D.oublier(); piloter(L, 0.3, fm, 60);
        const glace = { n: D.traces().length, crisse: crisse };
        const couv = L.Neige.couverture; L.Neige.couverture = function () { return 1; };
        D.oublier(); piloter(L, 0.5, fm, 60);
        const neige = Array.from(new Set(D.traces().map(function (t) { return t.type; })));
        L.Neige.couverture = couv;
        const bateau = L.B.defs.vehicules.find(function (q) { return q.eau; }).slug;
        crisse = 0; D.oublier(); const coque = piloter(L, 1, fm, 60, { slug: bateau });
        const eau = { n: D.traces().length, crisse: crisse, lacet: piloter(L, 0.6, fm, 30, { slug: bateau }).lacet };
        D.oublier(); for (let k = 0; k < 30; k++) piloter(L, 1, fm, 60);
        return { sec: sec, glace: glace, neige: neige, eau: eau, borne: D.traces().length, max: L.Derapage.donnees().traces.max };
    }""")
    assert r["sec"]["n"] > 0 and r["sec"]["types"] == ["trace"] and r["sec"]["crisse"] > 0, r["sec"]
    assert r["glace"]["crisse"] == 0, "la glace crisse (elle devrait se taire)"
    assert r["neige"] == ["sillon"], f"pas de sillon dans la neige : {r['neige']}"
    assert r["eau"]["n"] == 0 and r["eau"]["crisse"] == 0 and r["eau"]["lacet"] == 0, f"un bateau marque l'eau ou dérape : {r['eau']}"
    assert r["borne"] <= r["max"], "les traces ne sont pas bornées"


def test_un_char_arrete_ne_tourne_plus(banc):
    """La relecture : le lacet durait plus longtemps que la vitesse, et le char pivotait sur place une fois
    arrêté (trois quarts de tour sur la neige)."""
    r = banc("function (L, o) {" + PILOTE + """
        L.Jeu.commencer();
        const script = function (k) { return k < 25 ? { gaz: 0.6, direction: 1, freinMain: true } : k < 70 ? { frein: 0.6 } : {}; };
        const a = piloter(L, 0.3, script, 130);
        // L'arret des ROUES (la vitesse du char) : sur la glace, la caisse glisse encore un peu apres.
        let arret = -1; for (let k = 25; k < a.traj.length; k++) if (Math.abs(a.traj[k][4]) < 0.02) { arret = k; break; }
        let rot = 0; for (let k = arret + 1; k < a.traj.length; k++) rot += Math.abs(Math.atan2(Math.sin(a.traj[k][0] - a.traj[k - 1][0]), Math.cos(a.traj[k][0] - a.traj[k - 1][0])));
        return { arret: arret, rot: rot };
    }""")
    assert r["arret"] > 0, "le char ne s'est jamais arrêté"
    assert r["rot"] < 0.05, f"arrêté, le char tourne encore de {r['rot']:.2f} rad"


def test_la_police_rattrape_son_arriere(banc):
    r = banc("function (L, o) {" + PILOTE + """
        L.Jeu.commencer();
        const fm = function (k) { return k < 20 ? { gaz: 0.6, direction: 1, freinMain: true } : { gaz: 0.4, direction: 0 }; };
        return { joueur: piloter(L, 0.3, fm, 40).lacet, ia: piloter(L, 0.3, fm, 40, { ia: true }).lacet };
    }""")
    assert abs(r["ia"]) < 0.3 * abs(r["joueur"]), f"la police part en tête-à-queue comme un débutant : {r}"
