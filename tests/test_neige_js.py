"""La tempête de neige (M12) au banc : derrière son option, elle fait glisser, ralentit le
trafic, se peint, et la charrue déblaie en poussant les chars mal garés.

⚠️ L'heure se règle à la main (`TEMPETE`) : un soir de tempête, en pleine tempête.
"""

TEMPETE = """
    function soir(L, pleine) {
        const t = L.Neige.donnees().tempete;
        L.B.partie.jour = t.premier;
        const h = pleine ? (t.debut_h + t.fin_h) / 2 : t.debut_h - 1;
        L.B.partie.heure = h / 24;
    }
"""


def test_sans_l_option_il_ne_neige_rien(banc):
    """⚠️ Le jeu d'avant, octet pour octet : un soir de tempête, sans l'option, pas un
    flocon, pas un coefficient, pas une charrue."""
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        L.B.options.neige = false;
        soir(L, true);
        const j = L.B.joueur;
        const v = L.Vehicules.creer('auto', j.x + 30, j.y, 0, { etat: 'stationne', couleur: '#3a6fb0' });
        const ctx = { fillStyle: '', n: 0, fillRect: function () { this.n++; } };
        L.Neige.dessinerSol(ctx, { x: j.x - 240, y: j.y - 135 });
        L.Neige.dessinerTempete(ctx);
        return { i: L.Neige.intensite(), adh: L.Neige.adherence(v), frein: L.Neige.frein(v), trafic: L.Neige.vitesseTrafic(),
                 rects: ctx.n, prevue: L.Neige.intensiteA(L.B.partie.jour, L.B.partie.heure) };
    }""")
    assert r["prevue"] == 1, "le juge n'est pas un soir de tempête"
    assert r["i"] == 0 and r["adh"] == 1 and r["frein"] == 1 and r["trafic"] == 1
    assert r["rects"] == 0


def test_la_tempete_monte_et_retombe_a_l_heure(banc):
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        const t = L.Neige.donnees().tempete, N = L.Neige;
        const a = function (jour, h) { return N.intensiteA(jour, h / 24); };
        return { avant: a(t.premier, t.debut_h - 0.01), debut: a(t.premier, t.debut_h), mi: a(t.premier, (t.debut_h + t.fin_h) / 2),
                 montee: a(t.premier, t.debut_h + t.montee_h / 2), fin: a(t.premier, t.fin_h), veille: a(t.premier - 1, 20),
                 suivante: a(t.premier + t.tous_les, (t.debut_h + t.fin_h) / 2), lendemain: a(t.premier + 1, (t.debut_h + t.fin_h) / 2),
                 premierJour: a(1, (t.debut_h + t.fin_h) / 2),
                 // ⚠️ Un premier soir qui tomberait « au rythme » : le jour 1 est un multiple
                 // de la periode avant `premier`, et seul le garde-fou l'empeche de neiger.
                 avantLePremier: (function () { const p = t.premier; t.premier = 1 + t.tous_les; const r = a(1, (t.debut_h + t.fin_h) / 2); t.premier = p; return r; })() };
    }""")
    assert r["avant"] == 0 and r["debut"] == 0 and r["fin"] == 0
    assert r["mi"] == 1 and abs(r["montee"] - 0.5) < 1e-9
    assert r["suivante"] == 1 and r["lendemain"] == 0 and r["veille"] == 0 and r["premierJour"] == 0
    assert r["avantLePremier"] == 0, "il neige avant le premier soir de tempête"


def test_sur_la_neige_un_char_glisse_et_freine_mal(banc):
    """Le même coup de volant à la même vitesse : sur la neige, la vitesse réelle reste
    plus longtemps loin du cap, et le même freinage s'arrête plus loin. Déblayée, la rue
    rend l'essentiel."""
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        const j = L.B.joueur;
        function essai(neige, deblaye) {
            L.B.options.neige = neige;
            soir(L, true);
            const v = L.Vehicules.creer('auto', j.x + 400, j.y + 400, 0, { etat: 'stationne', couleur: '#3a6fb0' });
            if (deblaye) L.Neige.deneiger(Math.floor(v.x / L.TT), Math.floor(v.y / L.TT), 3);
            v.vitesse = 3; v.vx = 3; v.vy = 0;
            let derive = 0;
            for (let k = 0; k < 20; k++) {
                L.Vehicules.majPhysique(v, { gaz: 0.5, frein: 0, direction: 1, freinMain: false });
                const cap = Math.atan2(Math.sin(v.angle), Math.cos(v.angle)), reel = Math.atan2(v.vy, v.vx);
                derive += Math.abs(Math.atan2(Math.sin(cap - reel), Math.cos(cap - reel)));
            }
            v.vitesse = 3;
            let freinage = 0;
            while (v.vitesse > 0.15 && freinage < 400) { L.Vehicules.majPhysique(v, { gaz: 0, frein: 1, direction: 0, freinMain: false }); freinage++; }
            L.Entites.retirer(v);
            return { derive: derive, freinage: freinage };
        }
        return { sec: essai(false, false), neige: essai(true, false), deblaye: essai(true, true) };
    }""")
    assert r["neige"]["derive"] > 1.5 * r["sec"]["derive"], r
    assert r["neige"]["freinage"] > 1.3 * r["sec"]["freinage"], r
    assert r["deblaye"]["derive"] < r["neige"]["derive"] and r["deblaye"]["freinage"] < r["neige"]["freinage"], r


def test_la_neige_se_peint_sauf_derriere_la_charrue(banc):
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        L.B.options.neige = true;
        soir(L, true);
        const j = L.B.joueur, tx = Math.floor(j.x / L.TT), ty = Math.floor(j.y / L.TT);
        function surface() {
            const ctx = { fillStyle: '', aire: 0, n: 0, fillRect: function (x, y, w, h) { this.aire += w * h; this.n++; } };
            L.Neige.dessinerSol(ctx, { x: j.x - L.VW / 2, y: j.y - L.VH / 2 });
            return ctx;
        }
        const blanche = surface();
        L.Neige.deneiger(tx, ty, 2);
        const deblayee = surface();
        const voile = { fillStyle: '', n: 0, fillRect: function () { this.n++; } };
        L.Neige.dessinerTempete(voile);
        return { blanche: blanche.aire, deblayee: deblayee.aire, rects: blanche.n, flocons: voile.n };
    }""")
    assert r["blanche"] > 0 and r["rects"] < 200, r
    assert r["blanche"] - r["deblayee"] >= 20 * 16 * 16, "la charrue ne laisse pas de trace"
    assert r["flocons"] > 50


def test_la_charrue_sort_avec_la_tempete_deblaie_et_pousse_un_char_mal_gare(banc):
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        L.B.options.neige = true;
        soir(L, true);
        const T = L.Autobus.ligne('charrue');
        // Le joueur dans la bulle, a cote de la place de la charrue a l'heure.
        const p = L.Autobus.placeALHeure(T, 0, L.Autobus.tempsDeLaPartie());
        const j = L.B.joueur; j.intouchable = true;
        j.x = p.x - Math.sin(p.angle) * 360; j.y = p.y + Math.cos(p.angle) * 360; L.Monde.centrerCamera(j.x, j.y);
        let v = null;
        for (let k = 0; k < 200 && !v; k++) { o.frame(1); v = L.B.entites.find(function (q) { return q.charrue; }); }
        if (!v) return { nee: false };
        const out = { nee: true, sprite: v.sprite, visible: L.Entites.visibleAEcran(v.x, v.y, 0) };
        // ⚠️ **ON ATTEND UN BOUT DROIT.** Le char se pose devant le capot : si la
        // charrue tourne avant d'y arriver, elle ne le touche jamais et le juge
        // conclut « il n'a pas bougé ». Son tracé a changé le 17 sept. 2026 (la
        // trame a bougé, et les boucles avec elle), et c'est exactement ce qui est
        // arrivé. On la suit jusqu'à ce qu'elle tienne son cap une seconde.
        for (let essai = 0; essai < 20; essai++) {
            const a0 = v.angle;
            for (let k = 0; k < 60; k++) o.frame(1);
            if (Math.abs(Math.cos(v.angle - a0) - 1) < 0.001) break;
        }
        // Un char gare dans sa voie, devant elle.
        const cx = Math.cos(v.angle), cy = Math.sin(v.angle);
        const gare = L.Vehicules.creer('auto', v.x + cx * 48, v.y + cy * 48, v.angle, { etat: 'stationne', couleur: '#3a6fb0' });
        gare.laisse = true;
        L.Entites.indexer();
        const g0 = { x: gare.x, y: gare.y };
        const avant = L.Neige.deneigees;
        const x0 = v.x, y0 = v.y;
        for (let k = 0; k < 300; k++) o.frame(1);
        out.roule = Math.hypot(v.x - x0, v.y - y0);
        out.deblaye = L.Neige.deneigees - avant;
        out.pousse = Math.hypot(gare.x - g0.x, gare.y - g0.y);
        return out;
    }""")
    assert r["nee"], "la charrue n'est pas sortie"
    assert r["sprite"] == "camion_charrue" and r["visible"] is False
    assert r["roule"] > 80, f"la charrue s'est arrêtée devant le char mal garé ({r['roule']:.0f} px)"
    assert r["pousse"] > 8, "le char mal garé n'a pas bougé"
    assert r["deblaye"] > 10, "la charrue ne déblaie rien"


def test_le_trafic_leve_le_pied(banc):
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        L.B.options.neige = true;
        soir(L, true);
        const tempete = L.Neige.vitesseTrafic();
        L.B.options.neige = false;
        return { tempete: tempete, sec: L.Neige.vitesseTrafic(), reglage: L.Neige.donnees().effets.vitesse_trafic };
    }""")
    assert r["sec"] == 1 and abs(r["tempete"] - r["reglage"]) < 1e-9


def test_la_neige_ne_tire_aucun_de(banc):
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        L.B.options.neige = true;
        soir(L, true);
        L.graine(3);
        const tirage = L.B.rng;
        let des = 0;
        L.B.rng = function () { if (String(new Error().stack).indexOf('neige.js') >= 0) des++; return tirage(); };
        const ctx = { fillStyle: '', fillRect: function () {} };
        for (let k = 0; k < 300; k++) { o.frame(1); L.Neige.dessinerTempete(ctx); }
        L.B.rng = tirage;
        return { des: des };
    }""")
    assert r["des"] == 0
