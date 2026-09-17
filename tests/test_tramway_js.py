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
