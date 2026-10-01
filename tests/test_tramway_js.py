"""Le tramway (M12) au banc : une ligne sur rails, qui n'attend personne, ne s'arrête pas
pour toi, et à qui le trafic cède.

⚠️ Une rame est un autobus marqué `rails` sur la ligne `T` : `RAME` la fait naître comme
l'horaire le ferait — l'heure réglée pour que la rame `rang` soit à la tuile voulue, le
joueur dans la bulle, hors de l'écran — puis rend la main au juge.
"""

RAME = """
    function ligneT(L) { return L.Autobus.donnees().lignes.find(function (l) { return l.rails; }); }
    function rame(L, o, i) {
        const T = ligneT(L), h = T.horaire, jour = L.B.defs.economie.jour_secondes * 60;
        // La rame 0 a la tuile i : temps = i tuiles / vitesse (modulo la boucle).
        let t = ((i * L.TT) % T.longueurPx) / h.vitesse_px;
        while (t / jour < 0.45) t += T.longueurPx / h.vitesse_px;
        // ⚠️ Le PREMIER jour : `tempsDeLaPartie` compte les jours d'avant, et un jour de
        // plus deplace la rame de 40 000 px — un tour et demi de boucle.
        L.B.partie.jour = 1; L.B.partie.heure = t / jour;
        const p = L.Autobus.placeALHeure(T, 0, L.Autobus.tempsDeLaPartie());
        const j = L.B.joueur; j.intouchable = true;
        // Dans la bulle, hors de l'ecran : a 360 px, de cote.
        const nx = -Math.sin(p.angle), ny = Math.cos(p.angle);
        j.x = p.x + nx * 360; j.y = p.y + ny * 360; L.Monde.centrerCamera(j.x, j.y);
        let v = null;
        for (let k = 0; k < 120 && !v; k++) { o.frame(1); v = L.B.entites.find(function (q) { return q.rails && q.rang === 0; }); }
        return { T: T, v: v, p: p };
    }
"""


def test_la_ligne_t_roule_sur_ses_rails_et_nait_hors_de_l_ecran(banc):
    r = banc("function (L, o) {" + RAME + """
        L.Jeu.commencer();
        const m = rame(L, o, 60);
        const v = m.v;
        if (!v) return { nee: false };
        const t60 = m.T.tuiles[60];
        const out = { nee: true, sprite: v.sprite, couleur: v.couleur, conducteur: v.conducteur, ligne: v.ligne,
                      ecartALHeure: Math.hypot(v.x - (t60[0] * L.TT + 8), v.y - (t60[1] * L.TT + 8)),
                      visible: L.Entites.visibleAEcran(v.x, v.y, 0), rames: m.T.autobus, arrets: m.T.ordre.length,
                      fiche: L.SPRITES.tramway.couleur };
        const x0 = v.x, y0 = v.y;
        o.frame(240);
        out.roule = Math.hypot(v.x - x0, v.y - y0);
        return out;
    }""")
    assert r["nee"], "aucune rame n'est née"
    assert r["sprite"] == "tramway" and r["couleur"] == r["fiche"], r
    assert r["conducteur"] == "ligne" and r["ligne"] == "T"
    assert r["visible"] is False, "la rame est née sous les yeux"
    assert r["rames"] >= 2 and r["arrets"] >= 4
    assert r["roule"] > 40, f"la rame n'avance pas ({r['roule']:.0f} px)"
    # ⚠️ Sa place vient de SON horaire (la vitesse de la ligne T), pas de celui des autobus.
    assert r["ecartALHeure"] < 3 * 16, f"la rame est née à {r['ecartALHeure']:.0f} px de sa place à l'heure"


def test_une_rame_ne_s_arrete_pas_pour_toi_un_autobus_oui(banc):
    """Le char du joueur arrêté sur les rails, devant : l'autobus le voit comme un
    obstacle, la rame non — et elle sonne."""
    r = banc("function (L, o) {" + RAME + """
        L.Jeu.commencer();
        const m = rame(L, o, 60), v = m.v, j = L.B.joueur;
        const cx = Math.cos(v.angle), cy = Math.sin(v.angle);
        const x = v.x + cx * (v.def.longueur / 2 + 30), y = v.y + cy * (v.def.longueur / 2 + 30);
        const char = L.Vehicules.creer('auto', x, y, v.angle, { etat: 'stationne', couleur: '#3a6fb0' });
        L.Entites.indexer();
        L.Vehicules.monter(j, char);
        L.Monde.centrerCamera(j.x, j.y);             // la cloche d'une rame hors champ se tait
        // Un autobus a la place de la rame, le temps d'une mesure.
        const bus = L.Vehicules.creer('autobus', v.x, v.y, v.angle, { etat: 'stationne', couleur: '#2980b9', sprite: 'autobus' });
        L.Entites.indexer();
        const pourLaRame = L.Vehicules.obstacleDevant(v);
        const pourLAutobus = L.Vehicules.obstacleDevant(bus);
        L.Entites.retirer(bus); L.Entites.indexer();
        let cloches = 0;
        const avant = L.Son.SFX.cloche_tram;
        L.Son.SFX.cloche_tram = function () { cloches++; };
        const fil = [];
        for (let k = 0; k < 60; k++) { o.frame(1); fil.push(Math.abs(v.vitesse)); }
        L.Son.SFX.cloche_tram = avant;
        return { rienPourLaRame: pourLaRame === Infinity, pourLAutobus: pourLAutobus, cloches: cloches,
                 jamaisArretee: fil.slice(5, 40).every(function (s) { return s > 0.2; }) };
    }""")
    assert r["pourLAutobus"] < 60, f"l'autobus ne voit pas le char devant lui : {r['pourLAutobus']}"
    assert r["rienPourLaRame"], "la rame voit le char du joueur comme un obstacle"
    assert r["cloches"] >= 1, "la rame ne sonne pas"
    assert r["jamaisArretee"], "la rame s'est arrêtée devant le joueur"


def test_a_l_arret_elle_n_attend_personne(banc):
    """Portes ouvertes le temps de l'horaire, ni plus quand le joueur court vers elle, ni
    moins quand personne n'attend et qu'on ne la voit pas. L'autobus, lui, passe."""
    r = banc("function (L, o) {" + RAME + """
        L.Jeu.commencer();
        const m = rame(L, o, 60), v = m.v, T = m.T, d = L.Autobus.donnees();
        const a = d.arrets[T.ordre[3].arret], j = L.B.joueur;
        j.x = j.x + 2000; L.Monde.centrerCamera(j.x, j.y);
        const seule = L.Autobus.dureeDArret(v, a.id);
        j.x = a.quai[0] * L.TT + 8; j.y = a.quai[1] * L.TT + 8;
        const attendue = L.Autobus.dureeDArret(v, a.id);
        const bus = { rails: false, ligne: 2, bord: [], passager: null, x: v.x + 3000, y: v.y };
        j.x += 3000; L.Monde.centrerCamera(j.x, j.y);
        const busSeul = L.Autobus.dureeDArret(bus, d.lignes.find(function (l) { return l.numero === 2; }).ordre[1].arret);
        return { seule: seule, attendue: attendue, horaire: T.horaire.arret_images, busSeul: busSeul };
    }""")
    assert r["seule"] == r["horaire"] == r["attendue"], r
    assert r["busSeul"] == 0, "le juge ne compare à rien : l'autobus s'arrête aussi"


def test_le_trafic_cede_a_la_rame(banc):
    """Une rame qui roule vers une boîte la réserve à quatre tuiles : un char ne s'y
    engage pas. Arrêtée à son arrêt, ou qui s'en éloigne, elle ne réserve rien — et une
    rame ne se cède pas le passage à elle-même."""
    r = banc("function (L, o) {" + RAME + """
        L.Jeu.commencer();
        const c = L.Monde.carte, T = ligneT(L);
        // Une boite sur la ligne, et la tuile de la ligne trois tuiles avant elle.
        let i = -1, inter = null;
        for (let k = 20; k < T.n && !inter; k++) {
            const t = T.tuiles[k];
            const b = L.Monde.intersectionA(t[0], t[1]);
            if (b) { inter = b; i = k - 3; }
        }
        const m = rame(L, o, 0), v = m.v;
        const t = T.tuiles[i], u = T.tuiles[i + 1];
        v.x = t[0] * L.TT + 8; v.y = t[1] * L.TT + 8; v.angle = Math.atan2(u[1] - t[1], u[0] - t[0]); v.arretT = 0;
        // Personne d'autre autour de la boite : on ne mesure que la rame.
        for (const q of L.B.entites.slice()) if (q.type === 'vehicule' && q !== v) L.Entites.retirer(q);
        const char = L.Vehicules.creer('auto', (inter.x - 6) * L.TT, (inter.y - 6) * L.TT, 0, { etat: 'stationne', couleur: '#3a6fb0' });
        L.Entites.indexer();
        const arrive = L.Vehicules.croisementLibre(inter, char);
        // Une deuxieme rame, sur l'autre voie, qui roule vers la meme boite : les deux
        // se cedaient le passage et restaient plantees.
        const autre = L.Vehicules.creer('autobus', (inter.x + inter.l / 2) * L.TT + 3 * L.TT, (inter.y + inter.h / 2) * L.TT, Math.PI,
                                        { etat: 'roule', conducteur: 'ligne', ligne: 'T', rails: true, rang: 1, couleur: '#e9e3d0', sprite: 'tramway', arretT: 0 });
        L.Entites.indexer();
        const pourElle = L.Vehicules.croisementLibre(inter, v);
        L.Entites.retirer(autre); L.Entites.indexer();
        v.arretT = 50;
        const aLArret = L.Vehicules.croisementLibre(inter, char);
        v.arretT = 0; v.angle += Math.PI;
        const repart = L.Vehicules.croisementLibre(inter, char);
        return { arrive: arrive, pourElle: pourElle, aLArret: aLArret, repart: repart, trouve: !!inter };
    }""")
    assert r["trouve"]
    assert r["arrive"] is False, "un char s'engage devant une rame qui arrive"
    assert r["pourElle"] is True, "deux rames qui arrivent à la même boîte se cèdent le passage"
    assert r["aLArret"] is True and r["repart"] is True, r


def test_on_monte_a_l_arret_et_on_ne_vole_pas_une_rame(banc):
    r = banc("function (L, o) {" + RAME + """
        L.Jeu.commencer();
        const m = rame(L, o, 60), v = m.v, j = L.B.joueur;
        j.intouchable = true;
        const cx = Math.cos(v.angle), cy = Math.sin(v.angle);
        j.x = v.x - cy * 14; j.y = v.y + cx * 14; L.Monde.centrerCamera(j.x, j.y);
        L.Entites.indexer();
        const volable = L.Vehicules.vehiculeSousLaMain(j);
        v.arretT = 80; v.arret = m.T.ordre[1].arret;
        const argent = L.B.partie.argent;
        const sousLaMain = L.Autobus.autobusSousLaMain(j) === v;
        L.Autobus.monter(j, v);
        return { volable: !!volable, sousLaMain: sousLaMain, passager: j.passager === v, paye: argent - L.B.partie.argent,
                 tarif: L.Autobus.donnees().horaire.tarif };
    }""")
    assert r["volable"] is False, "on peut voler une rame"
    assert r["sousLaMain"] and r["passager"], r
    assert r["paye"] == r["tarif"]


def test_les_rails_et_les_poteaux_se_peignent(banc):
    r = banc("function (L, o) {" + RAME + """
        L.Jeu.commencer();
        const T = ligneT(L), d = L.Autobus.donnees();
        const a = d.arrets[T.ordre[2].arret];
        function peindre(cam) {
            const ctx = { fillStyle: '', h: 0, v: 0, n: 0, fillRect: function (x, y, w, hh) { this.n++; if (w === L.TT && hh === 1) this.h++; if (w === 1 && hh === L.TT) this.v++; } };
            L.Autobus.dessinerRails(ctx, cam);
            return ctx;
        }
        const sur = peindre({ x: a.x * L.TT - L.VW / 2, y: a.y * L.TT - L.VH / 2 }).n;
        const loin = peindre({ x: 390 * L.TT, y: 5 * L.TT }).n;
        // Une tuile de la ligne est-ouest, une nord-sud : chacune a ses filets dans son sens.
        const r = L.Autobus.railsParTuile();
        let est = null, nord = null;
        r.forEach(function (bits, cle) { if (bits === 1 && !est) est = cle; if (bits === 2 && !nord) nord = cle; });
        function autour(cle) { const t = cle.split(',').map(Number); return peindre({ x: t[0] * L.TT - 8, y: t[1] * L.TT - 8 }); }
        const pe = autour(est), pn = autour(nord);
        return { sur: sur, loin: loin, tuiles: r.size, estH: pe.h, nordV: pn.v };
    }""")
    assert r["sur"] > 20, "aucun rail peint autour d'un arrêt de la ligne"
    assert r["loin"] == 0
    assert r["tuiles"] > 100
    assert r["estH"] >= 2 and r["nordV"] >= 2, f"les rails ne suivent pas le sens de la voie : {r}"


def test_une_rame_ne_tire_aucun_de(banc):
    r = banc("function (L, o) {" + RAME + """
        L.Jeu.commencer();
        L.graine(5);
        const tirage = L.B.rng;
        let des = 0;
        const m = rame(L, o, 60);
        L.B.rng = function () {
            const pile = String(new Error().stack);
            if (pile.indexOf('autobus.js') >= 0) des++;
            return tirage();
        };
        for (let k = 0; k < 400; k++) o.frame(1);
        L.B.rng = tirage;
        return { des: des, nee: !!m.v };
    }""")
    assert r["nee"]
    assert r["des"] == 0, f"{r['des']} dés tirés par la ligne"


# --- Les bouchons aux coins de la ligne T (retour de Martin, 30 sept. 2026) ---------------
#
# Capture à l'appui : deux rames et un autobus enfoncés les uns dans les autres dans une boîte.
# Quatre causes, une par juge : le coin coupé, celui d'en face qui attend dans sa voie, la rame
# arrêtée au rouge qui gelait la boîte, et la rame qu'on poussait hors de ses rails.

COIN = """
    // Le premier coin de la ligne : une boite ou l'aller entre et sort par deux cotes qui ne
    // se font pas face. `i` = l'index de l'aller dans la boite.
    function coin(L) {
        const T = ligneT(L);
        for (let i = 1; i < T.aller; i++) {
            const t = T.tuiles[i], inter = L.Monde.intersectionA(t[0], t[1]);
            if (!inter || L.Monde.intersectionA(T.tuiles[i - 1][0], T.tuiles[i - 1][1])) continue;
            let j = i; while (L.Monde.intersectionA(T.tuiles[j + 1][0], T.tuiles[j + 1][1]) === inter) j++;
            const a = T.tuiles[i - 1], b = T.tuiles[j + 1];
            if (a[0] !== b[0] && a[1] !== b[1]) return { inter: inter, i: i };
        }
        return null;
    }
"""


def test_deux_rames_qui_se_croisent_au_coin_ne_s_impassent_pas(banc):
    """Les rames sont espacées d'un tiers de boucle : au premier coin, l'aller et le retour
    s'y croisent à presque chaque passage. Celle qui tournait coupait le coin et gardait le
    nez de biais dans la voie d'en face, où l'autre attendait la boîte qu'elle tenait :
    mille quatre cents images d'impasse, puis tout le monde forçait. Et celle qui roulait,
    poussée par celle qui attendait, sortait de ses rails."""
    r = banc("function (L, o) {" + RAME + COIN + """
        L.Jeu.commencer();
        // ⚠️ La glace noire de janvier (les saisons, lot 6, vague 6b) ralentit le trafic devant les rames : ce juge
        // tient deja par la graine sur la base (douze graines : 2 impasses de 387 images, 2 fois aucune croisee), et en
        // janvier les rames ne se croisaient plus au coin dans les 4 200 images. Il juge le coin, pas l'hiver.
        L.Glace.couper(true);
        const c = coin(L), T = ligneT(L), inter = c.inter;
        const m = rame(L, o, c.i - 24);
        const j = L.B.joueur;
        j.x = (inter.x - 3) * L.TT + 8; j.y = (inter.y - 3) * L.TT + 8; L.Monde.centrerCamera(j.x, j.y);
        const cx = (inter.x + inter.l / 2) * L.TT, cy = (inter.y + inter.h / 2) * L.TT;
        let pris = 0, pire = 0, horsRails = 0, croisees = 0;
        for (let k = 0; k < 4200; k++) {
            o.frame(1);
            const rames = L.B.entites.filter(function (e) { return e.rails; });
            if (rames.filter(function (e) { return Math.hypot(e.x - cx, e.y - cy) < 5 * L.TT; }).length >= 2) croisees++;
            for (const e of rames) {
                const a = T.tuiles[(e.etape + T.n - 1) % T.n], b = T.tuiles[e.etape];
                const ax = a[0] * L.TT + 8, ay = a[1] * L.TT + 8, lx = b[0] * L.TT + 8 - ax, ly = b[1] * L.TT + 8 - ay;
                const u = Math.max(0, Math.min(1, ((e.x - ax) * lx + (e.y - ay) * ly) / (lx * lx + ly * ly || 1)));
                horsRails = Math.max(horsRails, Math.hypot(e.x - ax - u * lx, e.y - ay - u * ly));
            }
            // Pris : arrete pres de la boite, sans feu, sans arret, sans boite a attendre.
            const bloque = L.B.entites.some(function (e) {
                return e.type === 'vehicule' && e.conducteur === 'ligne' && Math.hypot(e.x - cx, e.y - cy) < 6 * L.TT
                    && Math.abs(e.vitesse) < 0.05 && !(e.arretT > 0) && !e.attendFeu;
            });
            pris = bloque ? pris + 1 : 0; pire = Math.max(pire, pris);
        }
        return { nee: !!m.v, pire: pire, horsRails: horsRails, croisees: croisees };
    }""")
    assert r["nee"]
    assert r["croisees"] > 0, "les deux rames ne se sont jamais croisées au coin : le juge ne mesure rien"
    assert r["pire"] < 300, f"une rame ou un autobus reste pris {r['pire']} images au coin"
    assert r["horsRails"] < 3, f"une rame sort de {r['horsRails']:.1f} px de ses rails"


def test_une_rame_arretee_au_rouge_ne_gele_pas_la_boite(banc):
    """Le trafic cède à une rame qui ROULE vers la boîte ; arrêtée — à son feu, ou derrière
    un char —, elle ne roule vers rien : elle réservera la boîte le jour où elle s'y engage.
    Sans ça, toute la phase verte de la rue qui la croise passait à l'attendre."""
    r = banc("function (L, o) {" + RAME + COIN + """
        L.Jeu.commencer();
        const c = coin(L), T = ligneT(L), inter = c.inter;
        const m = rame(L, o, 0), v = m.v;
        const t = T.tuiles[c.i - 3], u = T.tuiles[c.i - 2];
        v.x = t[0] * L.TT + 8; v.y = t[1] * L.TT + 8; v.angle = Math.atan2(u[1] - t[1], u[0] - t[0]); v.arretT = 0;
        for (const q of L.B.entites.slice()) if (q.type === 'vehicule' && q !== v) L.Entites.retirer(q);
        const char = L.Vehicules.creer('auto', (inter.x - 6) * L.TT, (inter.y - 6) * L.TT, 0, { etat: 'stationne', couleur: '#3a6fb0' });
        L.Entites.indexer();
        v.attendFeu = false; v.vitesse = 1;
        const roule = L.Vehicules.croisementLibre(inter, char);
        v.attendFeu = true; v.vitesse = 0;
        const auRouge = L.Vehicules.croisementLibre(inter, char);
        // Arretee derriere un char qui attend a la ligne : ni feu, ni boite — elle attend lui.
        v.attendFeu = false; v.vitesse = 0;
        const derriere = L.Vehicules.croisementLibre(inter, char);
        return { roule: roule, auRouge: auRouge, derriere: derriere };
    }""")
    assert r["roule"] is False, "un char s'engage devant une rame qui arrive"
    assert r["auRouge"] is True, "une rame arrêtée à son feu gèle la boîte pour la rue qui la croise"
    assert r["derriere"] is True, "une rame arrêtée derrière un char gèle la boîte : il lui cède, elle l'attend"


def test_celui_d_en_face_qui_attend_dans_sa_voie_n_est_pas_un_obstacle(banc):
    """Un autobus qui sort d'une boîte a encore le nez de biais ; celui d'en face, arrêté dans
    SA voie, n'est pas devant lui. À contresens dans NOTRE voie, il l'est."""
    r = banc("function (L, o) {" + RAME + """
        L.Jeu.commencer();
        const T = ligneT(L);
        // Six tuiles droites de l'aller : notre voie ; la voie d'en face est a sa gauche.
        let k = 1;
        for (; k < T.aller - 8; k++) {
            let droit = true;
            for (let d = 0; d < 7 && droit; d++) {
                const a = T.tuiles[k + d], b = T.tuiles[k + d + 1];
                droit = b[0] - a[0] === T.tuiles[k + 1][0] - T.tuiles[k][0] && b[1] - a[1] === T.tuiles[k + 1][1] - T.tuiles[k][1]
                    && !L.Monde.intersectionA(a[0], a[1]) && !L.Monde.intersectionA(b[0], b[1]);
            }
            if (droit) break;
        }
        const t = T.tuiles[k], p = [T.tuiles[k + 1][0] - t[0], T.tuiles[k + 1][1] - t[1]], g = [p[1], -p[0]];
        for (const q of L.B.entites.slice()) if (q.type === 'vehicule') L.Entites.retirer(q);
        const cap = Math.atan2(p[1], p[0]);
        // Le nez de biais vers la voie d'en face, comme au sortir d'un virage.
        const bus = L.Vehicules.creer('autobus', t[0] * L.TT + 8, t[1] * L.TT + 8, cap - 0.3, { etat: 'roule', conducteur: 'ligne', couleur: '#2980b9', sprite: 'autobus' });
        const ex = (t[0] + 3 * p[0]) * L.TT + 8, ey = (t[1] + 3 * p[1]) * L.TT + 8;
        const enFace = L.Vehicules.creer('autobus', ex + g[0] * L.TT, ey + g[1] * L.TT, cap + Math.PI,
                                         { etat: 'roule', conducteur: 'ligne', couleur: '#2980b9', sprite: 'autobus' });
        enFace.vitesse = 0;
        L.Entites.indexer();
        const dansSaVoie = L.Vehicules.obstacleDevant(bus);
        // Le meme, a contresens dans notre voie.
        enFace.x = ex; enFace.y = ey; L.Entites.indexer();
        bus.angle = cap;
        const dansLaNotre = L.Vehicules.obstacleDevant(bus);
        return { dansSaVoie: Math.min(dansSaVoie, 9999), dansLaNotre: Math.min(dansLaNotre, 9999), securite: L.B.defs.conduite.trafic.distance_securite_px };
    }""")
    assert r["dansSaVoie"] > r["securite"], f"arrêté dans sa voie, celui d'en face arrête l'autobus ({r['dansSaVoie']:.0f} px)"
    assert r["dansLaNotre"] < r["securite"], "à contresens dans notre voie, il n'arrête plus personne"


def test_une_rame_ne_se_pousse_pas(banc):
    """Sur ses rails, une rame ne glisse pas : contre un char, c'est lui qui encaisse, même
    s'il attend son feu ; entre deux rames qui se frôlent sur deux voies voisines, personne."""
    r = banc("function (L, o) {" + RAME + """
        L.Jeu.commencer();
        for (const q of L.B.entites.slice()) if (q.type === 'vehicule') L.Entites.retirer(q);
        const j = L.B.joueur, x = j.x + 200, y = j.y + 200;
        function rame(xx, yy, a) { return L.Vehicules.creer('autobus', xx, yy, a, { etat: 'roule', conducteur: 'ligne', ligne: 'T', rails: true, couleur: '#e9e3d0', sprite: 'tramway' }); }
        const a = rame(x, y, Math.PI / 2), b = rame(x + 15, y + 30, -Math.PI / 2);
        b.attendFeu = true;
        L.Entites.indexer();
        L.Vehicules.heurterVehicules(a);
        const deuxRames = Math.hypot(a.x - x, a.y - y) + Math.hypot(b.x - x - 15, b.y - y - 30);
        L.Entites.retirer(b);
        const char = L.Vehicules.creer('auto', x + 12, y, 0, { etat: 'roule', conducteur: 'trafic', couleur: '#3a6fb0' });
        char.attendFeu = true;
        L.Entites.indexer();
        L.Vehicules.heurterVehicules(a);
        return { deuxRames: deuxRames, rame: Math.hypot(a.x - x, a.y - y), char: Math.hypot(char.x - x - 12, char.y - y) };
    }""")
    assert r["deuxRames"] == 0, f"deux rames se poussent de {r['deuxRames']:.1f} px"
    assert r["rame"] == 0, f"un char qui attend son feu pousse la rame de {r['rame']:.1f} px"
    assert r["char"] > 0, "rien n'a séparé la rame et le char : le juge ne mesure rien"
