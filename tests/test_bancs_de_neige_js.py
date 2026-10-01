"""Les bancs de neige qui enlisent (`static/js/bancs_de_neige.js`, les quatre saisons, lot 6, vague 6c), au banc.

Le banc que la rue des saisons peint (vague 4b) TIENT : effleuré, il freine un peu ; abordé au pas, on le monte ; abordé
vite, le char s'y plante — ses roues patinent, la neige gicle — et s'en sort en marche arrière, plus vite en berçant ; le
4 roues et les camions le poussent, la motoneige n'en sait rien, l'IA hors des rails n'y reste jamais prise. Le dessin
et les roues lisent le même profil ; il grossit aux tempêtes et fond au dégel ; aucun dé, rien de posé.

⚠️ Chaque juge de conduite se mesure sur PLUSIEURS bancs et plusieurs graines (la mémoire « juge vert par chance de
graine »). Le trafic est coupé autour : on juge le banc, pas un char qui passe.
"""

#: Janvier (la neige qui tient, avant la tempête du soir du 2), et juillet. ⚠️ Le 22, pas le 21 : le 21, le joueur déménage.
JANVIER, JUILLET = 2, 22

OUTILS = """
  const TT = 16;
  function saison(L, jour, heure) { L.B.partie.jour = jour; L.B.partie.heure = heure === undefined ? 0.5 : heure; }
  //: Le joueur tranquille, et personne autour : ni trafic, ni passant.
  function calme(L) {
    const B = L.B; B.partie.dette = 0; B.joueur.invincible = 1e9;
    B.defs.conduite.trafic.vehicules_max = 0;
    B.entites.slice().forEach(function (e) { if ((e.type === 'vehicule' && e.conducteur !== B.joueur) || e.type === 'pieton') L.Entites.retirer(e); });
  }
  //: Des bordures droites au NORD d'une rue (le trottoir au-dessus) : la tuile de rue et ses deux voisines ont un banc
  //: au nord, deux tuiles de rue en dessous (la voie d'ou l'on vient), du trottoir au-dessus. Une par cellule de 12
  //: tuiles, par distance au joueur.
  function bordures(L, combien) {
    const M = L.Monde, c = M.carte, R = L.RueDesSaisons, j = L.B.joueur, out = [], vues = new Set();
    const route = function (x, y) { return M.estRoute(x, y) && !M.estPassage(x, y); };
    for (let ty = 2; ty < c.h - 4; ty++) for (let tx = 3; tx < c.w - 3; tx++) {
      if (R.bancsDe(tx, ty).indexOf(0) < 0 || R.bancsDe(tx - 1, ty).indexOf(0) < 0 || R.bancsDe(tx + 1, ty).indexOf(0) < 0) continue;
      if (!route(tx, ty + 1) || !route(tx, ty + 2) || !route(tx - 1, ty + 1) || !route(tx + 1, ty + 1)) continue;
      if (!M.estTrottoir(tx, ty - 1) || !M.estTrottoir(tx, ty - 2)) continue;
      const k = Math.floor(tx / 12) + ',' + Math.floor(ty / 12);
      if (vues.has(k)) continue;
      vues.add(k);
      out.push({ tx: tx, ty: ty, bord: ty * TT, d: Math.hypot(tx * TT - j.x, ty * TT - j.y) });
    }
    return out.sort(function (a, b) { return a.d - b.d; }).slice(0, combien);
  }
  //: Un char lance vers la bordure (au nord) depuis la voie, a `vitesse`, de biais de `biais` rad (vers l'est).
  function lancer(L, b, slug, vitesse, opts) {
    const V = L.Vehicules, a = -Math.PI / 2 + ((opts && opts.biais) || 0);
    const v = V.creer(slug || 'auto', b.tx * TT + 8, b.ty * TT + 16 + 22, a, { etat: 'stationne', couleur: '#3a6fb0' });
    v.conducteur = (opts && opts.conducteur) || L.B.joueur;
    v.vitesse = vitesse; v.vx = Math.cos(a) * vitesse; v.vy = Math.sin(a) * vitesse;
    return v;
  }
  //: `n` images de conduite : la physique, puis le pas (les tuiles, comme en jeu). Rend la trace.
  function rouler(L, v, script, n) {
    const V = L.Vehicules, traj = [];
    for (let k = 0; k < n; k++) {
      V.majPhysique(v, Object.assign({ gaz: 0, frein: 0, direction: 0, freinMain: false }, script(k, v)));
      if (Math.abs(v.vx) + Math.abs(v.vy) > 0.01) V.avancer(v);
      L.B.t++;
      traj.push({ x: v.x, y: v.y, pris: L.BancsDeNeige.estPris(v), banc: !!v.banc, vit: Math.hypot(v.vx, v.vy), vitesse: v.vitesse });
    }
    return traj;
  }
  const GAZ = function () { return { gaz: 1 }; }, RECUL = function () { return { frein: 1 }; };
  const BERCER = function (k) { return (Math.floor(k / 15) % 2) ? { frein: 1 } : { gaz: 1 }; };
  //: Au pas : un filet de gaz tant qu'on roule sous 0,5 px/image.
  const AU_PAS = function (k, v) { return Math.abs(v.vitesse) < 0.5 ? { gaz: 0.6 } : {}; };
  //: Plante dans le banc `b` (lance a 3 px/image, gaz a fond), puis le pied leve dix images : rend le char.
  function planter(L, b) {
    const v = lancer(L, b, 'auto', 3.0);
    rouler(L, v, GAZ, 30); rouler(L, v, function () { return {}; }, 10);
    return v;
  }
"""


def test_les_bancs_grossissent_aux_tempetes_et_fondent_au_degel(banc):
    """La grosseur est une pure fonction du jour et de l'heure : la neige qui tient, plus chaque tempête de l'hiver (pendant
    qu'elle tombe, peu à peu), jusqu'à un plafond ; au dégel, elle fond ; rien l'été. Le banc s'élargit sur le trottoir,
    jamais au-delà de sa lèvre dans la rue ; et les morceaux ne se repeignent qu'au palier, pas à chaque image."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const BN = L.BancsDeNeige, g = function (j, h) { return BN.grosseurA(j, h / 24); }, c0 = function () { return L.Monde.carte; };
        // Un jour calme et un jour de tempete, au quart d'heure : combien de paliers (donc de repeintes) ?
        const paliers = function (jour) { let n = 0, p = g(jour, 0); for (let q = 1; q < 96; q++) { const x = g(jour, q / 4); if (x !== p) n++; p = x; } return n; };
        let saut = 0;
        for (let k = 0; k < 80 * 96; k++) saut = Math.max(saut, Math.abs(g(1 + Math.floor(k / 96), (k % 96) / 4) - g(1 + Math.floor((k + 1) / 96), ((k + 1) % 96) / 4)));
        // Les morceaux se repeignent quand la tempete fait grossir les bancs (la palette, elle, ne bouge pas en janvier).
        saison(L, 2, 0.5); L.Jeu.rendre(); const m0 = Array.from(c0().morceaux.values())[0];
        saison(L, 2, 0.51); L.Jeu.rendre(); const garde = Array.from(c0().morceaux.values())[0] === m0;
        saison(L, 2, 0.99); L.Jeu.rendre(); const repeint = garde && Array.from(c0().morceaux.values())[0] !== m0;
        // Le profil : la levre dans la rue et le gros sur le trottoir, selon la grosseur, sur toutes les bordures.
        const c = L.Monde.carte, R = L.RueDesSaisons;
        let rueMax = 0, trottoir1 = 0, trottoir16 = 0, n = 0;
        for (let ty = 0; ty < c.h; ty++) for (let tx = 0; tx < c.w; tx++) for (const cote of R.bancsDe(tx, ty)) for (let p = 0; p < 16; p += 2) {
            const a = BN.largeurs(tx, ty, cote, p, 1), b = BN.largeurs(tx, ty, cote, p, 1.6);
            rueMax = Math.max(rueMax, a.rue, b.rue); trottoir1 += a.trottoir; trottoir16 += b.trottoir; n++;
        }
        return { janvier: [g(1, 12), g(2, 12), g(2, 20), g(2, 23.6), g(5, 23.6), g(7, 12)], verglas: g(10, 12),
                 degel: [g(11, 6), g(11, 20), g(13, 12)], ete: [g(22, 12), g(30, 12)], decembre: [g(37, 12), g(38, 23.6), g(41, 12)],
                 plafond: Math.max.apply(null, Array.from({ length: 160 }, function (_, k) { return g(1 + k, 23.9); })),
                 calme: paliers(3), tempete: paliers(5), saut: saut, rueMax: rueMax, trottoir1: trottoir1 / n, trottoir16: trottoir16 / n,
                 repeint: repeint };
    }""")
    j = r["janvier"]
    assert j[0] == 1 and j[1] == 1, f"janvier, la neige pleine : le banc de la charrue, à sa largeur de la vague 4b : {j}"
    assert j[1] < j[2] < j[3], f"la tempête du 2 au soir fait grossir les bancs peu à peu : {j}"
    assert j[3] < j[4] == j[5], f"une deuxième tempête (le 5), puis rien ne bouge entre deux : {j}"
    assert r["verglas"] == j[5], "le verglas de fin mars n'est pas une tempête de neige"
    d = r["degel"]
    assert 0 < d[1] < d[0] < r["verglas"] and d[2] == 0, f"au dégel, le banc fond peu à peu : {d}"
    assert r["ete"] == [0, 0], "un banc de neige l'été"
    dc = r["decembre"]
    assert 0 < dc[0] and dc[0] < dc[1] <= dc[2], f"décembre : les bancs reviennent et grossissent dès la première tempête : {dc}"
    # Le deuxième hiver a quatre tempêtes (38, 41, 44, 47) : le plafond (trois) s'y voit.
    assert r["plafond"] == 1.45, f"les bancs n'ont pas de plafond, ou ne l'atteignent jamais : {r['plafond']}"
    assert r["calme"] == 0 and 0 < r["tempete"] <= 6, f"repeintes des morceaux : {r['calme']} un jour calme, {r['tempete']} un jour de tempête"
    # Au plus un palier de palette (la neige qui tient glisse en huit paliers au dégel et en décembre), jamais d'un coup.
    assert r["saut"] <= 0.2 + 1e-9, f"la grosseur saute de {r['saut']} en un quart d'heure"
    assert r["rueMax"] <= 3, f"la lèvre du banc mange la voie : {r['rueMax']} px dans la rue"
    assert r["trottoir16"] > 1.3 * r["trottoir1"], "après les tempêtes, le banc ne s'élargit pas sur le trottoir"
    assert r["repeint"], "la tempête fait grossir les bancs, mais les morceaux peints ne bougent pas (ou se repeignent à chaque image)"


def test_le_dessin_et_les_roues_lisent_le_meme_banc(banc):
    """Pixel par pixel, sur des morceaux de rue bordés de bancs : la neige peinte (le corps blanc du banc) est exactement
    là où une roue sent le banc — en janvier, et après deux tempêtes (plus gros)."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const BN = L.BancsDeNeige, R = L.RueDesSaisons, d = L.B.defs.saisons.rue.bancs, out = [];
        const morceaux = [], vus = new Set();
        for (const b of bordures(L, 12)) { const k = Math.floor(b.tx / 16) + ',' + Math.floor(b.ty / 16); if (!vus.has(k)) { vus.add(k); morceaux.push([Math.floor(b.tx / 16), Math.floor(b.ty / 16)]); } }
        for (const jour of [2, 7]) {
            saison(L, jour);
            for (const m of morceaux.slice(0, 3)) {
                const ctx = L.Base.nouveauCanvas(256, 256).getContext('2d'); ctx.traces = [];
                R.peindre(ctx, L.Monde.carte, m[0], m[1], 16, 16);
                const peint = new Uint8Array(256 * 256);
                ctx.traces.forEach(function (t) {
                    if (t[4] !== d.neige) return;
                    for (let y = Math.max(0, t[1]); y < Math.min(256, t[1] + t[3]); y++) for (let x = Math.max(0, t[0]); x < Math.min(256, t[0] + t[2]); x++) peint[y * 256 + x] = 1;
                });
                const g = BN.grosseur(); let faux = 0, blancs = 0, exemple = null;
                for (let y = 0; y < 256; y++) for (let x = 0; x < 256; x++) {
                    const roue = !!BN.sous(m[0] * 256 + x + 0.5, m[1] * 256 + y + 0.5, g);
                    if (peint[y * 256 + x]) blancs++;
                    if (roue !== !!peint[y * 256 + x]) { faux++; if (!exemple) exemple = [x, y, roue]; }
                }
                out.push({ jour: jour, m: m, g: g, blancs: blancs, faux: faux, exemple: exemple });
            }
        }
        return out;
    }""")
    assert len(r) == 6, r
    for m in r:
        assert m["blancs"] > 200, f"le juge ne voit pas de banc dans ce morceau : {m}"
        assert m["faux"] == 0, f"le dessin et les roues ne disent pas le même banc : {m}"


def test_au_milieu_de_sa_voie_les_roues_ne_touchent_jamais_le_banc(banc):
    """Toutes les bordures de la ville, plus gros que le plafond (1,6) : un char au milieu de sa voie (la tuile de rue
    qui longe le trottoir — là où roule le trafic), le long de la bordure, n'a aucune roue dans la neige. Une auto, un
    camion (16 px de large), une moto. Le trafic ne s'y jette donc jamais."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const BN = L.BancsDeNeige, R = L.RueDesSaisons, c = L.Monde.carte, V = L.Vehicules;
        const defs = ['auto', 'camion', 'moto'].map(function (s) { return V.vehiculeDef(s); });
        let essais = 0, touches = 0, exemple = null;
        const route = function (x, y) { return L.Monde.estRoute(x, y); };
        for (let ty = 0; ty < c.h; ty++) for (let tx = 0; tx < c.w; tx++) for (const cote of R.bancsDe(tx, ty)) for (const def of defs) {
            // Une VOIE : la rue continue devant et derriere, le long de la bordure (pas le coin ou elle tourne).
            if (cote < 2 ? !(route(tx - 1, ty) && route(tx + 1, ty)) : !(route(tx, ty - 1) && route(tx, ty + 1))) continue;
            const v = { x: tx * TT + 8, y: ty * TT + 8, angle: cote < 2 ? 0 : Math.PI / 2, def: def };
            essais++;
            if (BN.contacts(v, 1.6).length) { touches++; if (!exemple) exemple = [tx, ty, cote, def.slug]; }
        }
        return { essais: essais, touches: touches, exemple: exemple };
    }""")
    assert r["essais"] > 3000, r
    assert r["touches"] == 0, f"au milieu de sa voie, une roue touche le banc : {r}"


def test_y_foncer_plante_le_char_les_roues_patinent_et_la_neige_gicle(banc):
    """Six bancs, trois graines : lancé à 3 px/image vers la bordure, le char s'y plante (la neige gicle, le son, le HUD
    dit comment s'en sortir) ; gaz à fond deux secondes, il reste pris, ses roues patinent et la neige gicle derrière,
    et un peu de neige se peint sur son nez. Effleuré de biais (13°) à pleine vitesse, il ne s'y plante pas."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, BN = L.BancsDeNeige, couleurs = BN.reglages().gicle.couleurs, out = [];
        const sons = []; const s0 = L.Son.SFX.banc_de_neige;
        L.Son.SFX.banc_de_neige = function () { sons.push(1); return s0.apply(null, arguments); };
        for (const graine of [1, 7, 4242]) {
            L.graine(graine); calme(L); saison(L, """ + str(JANVIER) + """);
            for (const b of bordures(L, 6)) {
                B.msg = ''; B.particules.length = 0;
                const v = lancer(L, b, 'auto', 3.0);
                const t1 = rouler(L, v, GAZ, 20);
                const entre = t1.findIndex(function (s) { return s.pris; }), msg = B.msg, neige = B.particules.filter(function (p) { return couleurs.indexOf(p.c) >= 0; }).length;
                const ax = v.x, ay = v.y; B.particules.length = 0;
                const t2 = rouler(L, v, GAZ, 120);
                const bouge = Math.max.apply(null, t2.map(function (s) { return Math.hypot(s.x - ax, s.y - ay); }));
                const gicle = B.particules.filter(function (p) { return couleurs.indexOf(p.c) >= 0; }).length;
                const ctx = L.Base.nouveauCanvas(480, 270).getContext('2d'); ctx.traces = [];
                const cam = { x: v.x - 240, y: v.y - 135 };
                BN.dessiner(ctx, cam);
                out.push({ graine: graine, b: [b.tx, b.ty], entre: entre, msg: msg, neige: neige, pris: t2.every(function (s) { return s.pris; }),
                           patine: !!(v.banc && v.banc.patine), bouge: +bouge.toFixed(2), gicle: gicle, nez: ctx.traces.length });
                L.Entites.retirer(v);
                const m = lancer(L, b, 'auto', 3.4, { biais: 1.35 });
                const t3 = rouler(L, m, function () { return { gaz: 1 }; }, 40);
                out[out.length - 1].biais = { pris: t3.some(function (s) { return s.pris; }), vit: +t3[39].vit.toFixed(2), bord: +(b.bord - Math.min.apply(null, t3.map(function (s) { return s.y; }))).toFixed(1) };
                L.Entites.retirer(m);
            }
        }
        L.Son.SFX.banc_de_neige = s0;
        return { essais: out, sons: sons.length };
    }""")
    e = r["essais"]
    assert len(e) == 18, e
    for x in e:
        assert 0 <= x["entre"] <= 15, f"lancé droit dessus, le char ne s'y plante pas : {x}"
        assert "BANC" in x["msg"] and x["neige"] >= 10, f"l'impact ne se voit pas (la gerbe, le HUD) : {x}"
        assert x["pris"] and x["bouge"] <= 2, f"gaz à fond, le char pris est reparti : {x}"
        assert x["patine"] and x["gicle"] >= 40, f"les roues ne patinent pas, la neige ne gicle pas : {x}"
        assert x["nez"] > 20, f"pas de neige sur le nez du char pris : {x}"
        assert not x["biais"]["pris"] and x["biais"]["vit"] > 2.5, f"effleuré de biais, le char s'y plante ou y perd tout : {x}"
    assert r["sons"] == 18, f"{r['sons']} sons d'impact pour 18 chars plantés"


def test_on_s_en_sort_en_reculant_et_plus_vite_en_bercant(banc):
    """Six bancs, deux graines : planté, le gaz seul ne le sort jamais (400 images) ; la marche arrière le sort, et il
    revient dans la rue ; bercer (avancer, reculer, quinze images chacun) le sort nettement plus vite."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const out = [];
        for (const graine of [3, 11]) {
            L.graine(graine); calme(L); saison(L, """ + str(JANVIER) + """);
            for (const b of bordures(L, 6)) {
                const essai = function (script, n) {
                    const v = planter(L, b);
                    const pris0 = L.BancsDeNeige.estPris(v);
                    const t = rouler(L, v, script, n), sorti = t.findIndex(function (s) { return !s.pris; });
                    const apres = sorti >= 0 ? rouler(L, v, RECUL, 60) : [];
                    L.Entites.retirer(v);
                    return { pris0: pris0, sorti: sorti, rue: apres.length ? +(apres[59].y - b.bord).toFixed(1) : null };
                };
                out.push({ b: [b.tx, b.ty], gaz: essai(GAZ, 400), recul: essai(RECUL, 400), berce: essai(BERCER, 400) });
            }
        }
        return out;
    }""")
    assert len(r) == 12, r
    for x in r:
        assert x["gaz"]["pris0"] and x["gaz"]["sorti"] < 0, f"le gaz seul sort le char du banc : {x}"
        assert 0 < x["recul"]["sorti"] <= 400, f"la marche arrière ne le sort pas : {x}"
        assert x["recul"]["rue"] > 12, f"sorti en reculant, il ne revient pas dans la rue : {x}"
        assert 0 < x["berce"]["sorti"] < 0.75 * x["recul"]["sorti"], f"bercer ne le sort pas plus vite : {x}"


def test_au_pas_on_le_monte_sans_s_y_planter(banc):
    """Six bancs : abordé au pas (sous 0,5 px/image), le banc retient — on ne le franchit qu'au pas de tortue — mais on
    le monte, et on finit sur le trottoir : aucun trottoir n'est fermé au char qui y va doucement."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        calme(L); saison(L, """ + str(JANVIER) + """);
        const BN = L.BancsDeNeige, lim = BN.reglages().ramper, out = [];
        for (const b of bordures(L, 6)) {
            const v = lancer(L, b, 'auto', 0.4);
            const t = rouler(L, v, AU_PAS, 300);
            let dansLeBanc = 0;
            t.forEach(function (s) { if (s.banc) dansLeBanc = Math.max(dansLeBanc, s.vit); });
            out.push({ b: [b.tx, b.ty], pris: t.some(function (s) { return s.pris; }), passe: +(b.bord - Math.min.apply(null, t.map(function (s) { return s.y; }))).toFixed(1),
                       vitBanc: +dansLeBanc.toFixed(3), lim: lim });
            L.Entites.retirer(v);
        }
        return out;
    }""")
    assert len(r) == 6, r
    for x in r:
        assert not x["pris"], f"au pas, le char se plante : {x}"
        assert x["passe"] > 6, f"au pas, le char ne monte pas sur le trottoir : {x}"
        assert x["vitBanc"] <= x["lim"] + 0.05, f"le banc ne retient pas : {x}"


def test_le_4_roues_et_le_camion_le_poussent_la_motoneige_n_en_sait_rien(banc):
    """Six bancs : le 4 roues et le camion, lancés à 3 px/image, ne s'y plantent jamais et le franchissent — plus lentement
    que sans banc ; la motoneige le traverse au pixel comme s'il n'existait pas."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        calme(L); saison(L, """ + str(JANVIER) + """);
        const BN = L.BancsDeNeige, out = [];
        const passer = function (b, slug, couper) {
            BN.couper(couper);
            const v = lancer(L, b, slug, 3.0);
            const t = rouler(L, v, GAZ, 30);
            BN.couper(false);
            L.Entites.retirer(v);
            return { pris: t.some(function (s) { return s.pris; }), y: t[11].y, passe: b.bord - Math.min.apply(null, t.map(function (s) { return s.y; })),
                     traj: JSON.stringify(t.map(function (s) { return [s.x, s.y]; })) };
        };
        for (const b of bordures(L, 6)) {
            const q = passer(b, 'quatre_roues', false), q0 = passer(b, 'quatre_roues', true);
            const c = passer(b, 'camion', false), c0 = passer(b, 'camion', true);
            const m = passer(b, 'motoneige', false), m0 = passer(b, 'motoneige', true);
            out.push({ b: [b.tx, b.ty], quad: [q.pris, +q.passe.toFixed(1), q.y > q0.y], camion: [c.pris, +c.passe.toFixed(1), c.y > c0.y], moto: m.traj === m0.traj });
        }
        return out;
    }""")
    assert len(r) == 6, r
    for x in r:
        assert not x["quad"][0] and x["quad"][1] > 6, f"le 4 roues s'y plante, ou ne le franchit pas : {x}"
        assert x["quad"][2], f"le 4 roues ne sent pas le banc (il n'est pas plus lent) : {x}"
        assert not x["camion"][0] and x["camion"][1] > 0 and x["camion"][2], f"le camion s'y plante, ou ne le sent pas : {x}"
        assert x["moto"], f"la motoneige sent le banc : {x}"


def test_l_ia_y_perd_de_l_elan_mais_n_y_reste_jamais_prise(banc):
    """Six bancs, trois angles, deux graines : une auto-patrouille (la police hors des rails) ou un poursuivant lancés
    dans le banc, gaz à fond, n'y restent jamais pris — ils le franchissent, plus lentement que sans banc."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const BN = L.BancsDeNeige, out = [];
        for (const graine of [5, 13]) {
            L.graine(graine); calme(L); saison(L, """ + str(JANVIER) + """);
            for (const b of bordures(L, 6)) for (const biais of [0, 0.5, -0.5]) for (const qui of ['police', 'poursuivant']) {
                const essai = function (couper) {
                    BN.couper(couper);
                    const v = lancer(L, b, 'police', 3.0, { biais: biais, conducteur: qui });
                    const t = rouler(L, v, GAZ, 30);
                    BN.couper(false); L.Entites.retirer(v);
                    return { pris: t.some(function (s) { return s.pris; }), y: t[11].y, passe: b.bord - Math.min.apply(null, t.map(function (s) { return s.y; })) };
                };
                const avec = essai(false), sans = essai(true);
                out.push({ b: [b.tx, b.ty], biais: biais, qui: qui, pris: avec.pris, passe: +avec.passe.toFixed(1), freine: avec.y > sans.y });
            }
        }
        return out;
    }""")
    assert len(r) == 72, len(r)
    for x in r:
        assert not x["pris"], f"l'IA reste prise dans le banc : {x}"
        assert x["passe"] > 6 and x["freine"], f"l'IA ne franchit pas le banc, ou ne le sent pas : {x}"


def test_aucun_de_rien_de_pose_et_hors_du_banc_la_conduite_au_pixel(banc):
    """Planter, patiner, bercer, sortir : aucun dé tiré dans le module, pas une entité de plus. Et la même conduite au
    pixel, bancs coupés ou non : l'été contre la bordure, et l'hiver au milieu de la voie."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, BN = L.BancsDeNeige;
        calme(L); saison(L, """ + str(JANVIER) + """);
        const b = bordures(L, 1)[0];
        let des = 0, dedans = 0; const rng = B.rng, maj = BN.maj;
        B.rng = function () { if (dedans) des++; return rng(); };
        // ⚠️ On compte les des tires PENDANT le banc (la regle), pas ceux de la ville autour.
        const espion = function (v, cmd) { dedans++; try { return maj(v, cmd); } finally { dedans--; } };
        const n0 = B.entites.length;
        // L'espion : on remplace la fonction que majPhysique appelle (BancsDeNeige.maj est lue a chaque image).
        BN.maj = espion;
        const v = planter(L, b); rouler(L, v, BERCER, 200); rouler(L, v, RECUL, 60);
        const pris = !!(v.banc);
        L.Entites.retirer(v);
        BN.maj = maj; B.rng = rng;
        const meme = function (jour, opts, script) {
            saison(L, jour);
            const trace = function (couper) {
                BN.couper(couper);
                const w = lancer(L, b, 'auto', 3.0, opts), t = rouler(L, w, script, 60);
                BN.couper(false); L.Entites.retirer(w);
                return JSON.stringify(t.map(function (s) { return [s.x, s.y, s.vitesse]; }));
            };
            return trace(false) === trace(true);
        };
        return { des: des, entites: B.entites.length - n0, appels: pris,
                 ete: meme(""" + str(JUILLET) + """, {}, GAZ),
                 voie: meme(""" + str(JANVIER) + """, { biais: Math.PI / 2 }, GAZ) };
    }""")
    assert r["des"] == 0, f"{r['des']} dés tirés par les bancs de neige"
    assert r["entites"] == 0, "les bancs ont posé quelque chose"
    assert r["ete"], "l'été, contre la bordure, la conduite change avec les bancs"
    assert r["voie"], "l'hiver, au milieu de la voie, la conduite change avec les bancs"


def test_devant_un_rideau_de_garage_on_a_pellete(banc):
    """Devant chaque porte de garage (Ti-Guy, les carrosseries, les bungalows), la rue n'a pas de banc du côté du
    trottoir qui y mène : on y entre l'hiver sans s'y planter. Ailleurs, la bordure garde son banc."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const M = L.Monde, R = L.RueDesSaisons, fautes = [];
        let vues = 0;
        for (const pg of M.portesDeGarage()) for (let x = pg.x; x < pg.x + pg.l; x++) {
            // Descendre du rideau a travers le trottoir jusqu'a la rue.
            let y = pg.y + 1;
            while (y < pg.y + 8 && !M.estRoute(x, y)) y++;
            if (!M.estRoute(x, y) || !M.estTrottoir(x, y - 1)) continue;
            vues++;
            if (R.bancsDe(x, y).indexOf(0) >= 0) fautes.push([pg.lieu, x, y]);
        }
        return { vues: vues, fautes: fautes, bordures: bordures(L, 6).length };
    }""")
    assert r["vues"] >= 4, r
    assert r["fautes"] == [], f"un banc devant une porte de garage : {r['fautes']}"
    assert r["bordures"] == 6, "les bordures ont perdu leurs bancs"
