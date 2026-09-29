"""La pluie au banc (`static/js/pluie.js`) : une pure fonction du jour et de l'heure — des averses au
printemps et à l'automne, des orages le soir l'été, jamais l'hiver ; la rue reste mouillée un moment."""


def test_il_ne_pleut_jamais_l_hiver_et_l_ete_c_est_l_orage(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const P = L.Pluie, C = L.Calendrier, par = { hiver: 0, printemps: 0, ete: 0, automne: 0 }, jours = { hiver: 0, printemps: 0, ete: 0, automne: 0 };
        let orageHorsEte = 0, averseEte = 0;
        for (let j = 1; j <= 120; j++) {
            const s = C.saison(j), a = P.journee(j);
            jours[s]++;
            if (a) { par[s]++; if (a.orage && s !== 'ete') orageHorsEte++; if (!a.orage && s === 'ete') averseEte++; }
        }
        return { par: par, jours: jours, orageHorsEte: orageHorsEte, averseEte: averseEte,
                 pareil: JSON.stringify(P.journee(52)) === JSON.stringify(P.journee(52)) };
    }""")
    assert r["par"]["hiver"] == 0, "il pleut l'hiver"
    for s in ("printemps", "automne"):
        assert 0.3 <= r["par"][s] / r["jours"][s] <= 0.7, f"{s} : {r['par'][s]} jours de pluie sur {r['jours'][s]}"
    assert 0.15 <= r["par"]["ete"] / r["jours"]["ete"] <= 0.5
    assert r["orageHorsEte"] == 0 and r["averseEte"] == 0
    assert r["pareil"]


def test_l_averse_monte_tient_et_la_rue_seche_apres(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const P = L.Pluie;
        let j = 11; while (!P.journee(j) || P.journee(j).orage) j++;
        const a = P.journee(j), i = function (h) { return P.intensiteA(j, h / 24); }, m = function (h) { return P.mouilleeA(j, h / 24); };
        const d = L.B.defs.pluie.effets.seche_h;
        return { avant: i(a.debut - 0.1), milieu: i((a.debut + a.fin) / 2), apres: i(a.fin + 0.01),
                 mouilleeApres: m(a.fin + d / 2), secheApres: m(a.fin + d + 0.01), mouilleeMilieu: m((a.debut + a.fin) / 2) };
    }""")
    assert r["avant"] == 0 and r["milieu"] == 1 and r["apres"] == 0
    assert r["mouilleeMilieu"] == 1 and 0 < r["mouilleeApres"] < 1 and r["secheApres"] == 0


#: Un jour et une heure de pleine averse (printemps ou automne, selon `saison`), ou un jour sec.
MOMENTS = """
    function pleine(L, saison) {
        const P = L.Pluie;
        for (let j = 1; j < 200; j++) {
            const a = P.journee(j);
            if (a && !a.orage && L.Calendrier.saison(j) === saison) { L.B.partie.jour = j; L.B.partie.heure = (a.debut + a.fin) / 2 / 24; return j; }
        }
    }
    function sec(L) { L.B.partie.jour = 21; while (L.Pluie.journee(L.B.partie.jour)) L.B.partie.jour++; L.B.partie.heure = 0.5; }
"""


def test_la_rue_mouillee_glisse_et_la_rue_seche_ne_change_rien(banc):
    r = banc("function (L, o) {" + MOMENTS + """
        L.Jeu.commencer();
        const j = L.B.joueur, P = L.Pluie;
        const v = L.Vehicules.creer('auto', j.x + 400, j.y + 400, 0, { etat: 'stationne', couleur: '#3a6fb0' });
        const mesure = function () { return { adh: P.adherence(v), frein: P.frein(v), trafic: P.vitesseTrafic(), i: P.intensite() }; };
        sec(L); const auSec = mesure();
        pleine(L, 'printemps'); const printemps = mesure();
        pleine(L, 'automne'); const automne = mesure();
        return { sec: auSec, printemps: printemps, automne: automne, reglage: L.B.defs.pluie.effets };
    }""")
    e = r["reglage"]
    assert r["sec"] == {"adh": 1, "frein": 1, "trafic": 1, "i": 0}, "au sec, la pluie change quelque chose"
    assert r["printemps"]["i"] == 1 and abs(r["printemps"]["adh"] - e["adherence"]) < 1e-9
    assert abs(r["printemps"]["frein"] - e["frein"]) < 1e-9 and abs(r["printemps"]["trafic"] - e["vitesse_trafic"]) < 1e-9
    assert abs(r["automne"]["adh"] - e["feuilles_adherence"]) < 1e-9, "les feuilles mouillées ne glissent pas plus"


def test_sous_la_pluie_un_char_glisse_et_freine_mal(banc):
    """Le même coup de volant à la même vitesse : sous la pluie, le char dérive plus et freine plus long."""
    r = banc("function (L, o) {" + MOMENTS + """
        L.Jeu.commencer();
        const j = L.B.joueur;
        function essai(mouille) {
            if (mouille) pleine(L, 'printemps'); else sec(L);
            const v = L.Vehicules.creer('auto', j.x + 400, j.y + 400, 0, { etat: 'stationne', couleur: '#3a6fb0' });
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
        return { sec: essai(false), pluie: essai(true) };
    }""")
    assert r["pluie"]["derive"] > 1.15 * r["sec"]["derive"], r
    assert r["pluie"]["freinage"] > r["sec"]["freinage"], r


def test_la_gadoue_d_avril_glisse_un_peu(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const P = L.Pluie, M = L.Monde, c = M.carte, g = L.B.defs.pluie.effets.gadoue;
        L.B.partie.jour = 12; L.B.partie.heure = 0.5;            // en plein dans la fonte (avril : jour 11)
        let tuile = null, seche = null;
        for (let y = 0; y < c.h && (!tuile || !seche); y++) for (let x = 0; x < c.w; x++) {
            if (!M.estRoute(x, y) && !M.estTrottoir(x, y)) continue;
            if (P.gadoueSur(x, y)) { if (!tuile) tuile = [x, y]; } else if (!seche) seche = [x, y];
        }
        const v = { x: tuile[0] * 16 + 8, y: tuile[1] * 16 + 8 }, w = { x: seche[0] * 16 + 8, y: seche[1] * 16 + 8 };
        const avril = P.adherence(v), ailleurs = P.adherence(w);
        L.B.partie.jour = 21; const juillet = P.adherence(v);
        L.B.partie.jour = 12;
        return { avril: avril, ailleurs: ailleurs, juillet: juillet, reglage: g.adherence, gadoue: P.gadoue(),
                 mouillee: P.adherence({ x: -9999, y: -9999 }) };
    }""")
    assert r["gadoue"] == 1, "le juge n'est pas en pleine fonte"
    base = r["mouillee"]
    assert abs(r["avril"] - r["reglage"] * base) < 1e-9, r
    assert r["juillet"] == 1, "la gadoue reste en juillet (un midi d'été est sec : l'orage, c'est le soir)"
    assert abs(r["ailleurs"] - base) < 1e-9, r


def test_la_pluie_se_peint_seulement_quand_il_pleut(banc):
    r = banc("function (L, o) {" + MOMENTS + """
        L.Jeu.commencer();
        const j = L.B.joueur, cam = { x: j.x - L.VW / 2, y: j.y - L.VH / 2 };
        function peindre() {
            const haut = { fillStyle: '', n: 0, fillRect: function () { this.n++; } }, sol = { fillStyle: '', n: 0, fillRect: function () { this.n++; } };
            L.Pluie.dessiner(haut); L.Pluie.dessinerSol(sol, cam);
            return { haut: haut.n, sol: sol.n };
        }
        sec(L); const auSec = peindre();
        pleine(L, 'printemps'); const averse = peindre();
        let jo = 17; while (!(L.Pluie.journee(jo) && L.Pluie.journee(jo).orage)) jo++;
        const a = L.Pluie.journee(jo); L.B.partie.jour = jo; L.B.partie.heure = (a.debut + a.fin) / 2 / 24;
        const orage = peindre();
        return { sec: auSec, averse: averse, orage: orage, e: L.B.defs.pluie.effets };
    }""")
    assert r["sec"] == {"haut": 0, "sol": 0}, "il pleut à l'écran par temps sec"
    assert r["averse"]["haut"] >= r["e"]["gouttes"] * 0.9 and r["averse"]["sol"] > 0
    assert r["orage"]["haut"] > r["averse"]["haut"], "l'orage n'est pas plus dense que l'averse"
    assert r["averse"]["haut"] < 3 * r["e"]["gouttes_orage"], "trop de rectangles : le rythme"


def test_les_flaques_sont_sur_la_rue_et_le_trottoir_a_l_empreinte(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const P = L.Pluie, M = L.Monde, c = M.carte;
        let flaques = 0, pavees = 0, ailleurs = 0;
        for (let y = 0; y < c.h; y++) for (let x = 0; x < c.w; x++) {
            const pave = M.estRoute(x, y) || M.estTrottoir(x, y), f = P.flaqueSur(x, y);
            if (pave) { pavees++; if (f) flaques++; } else if (f) ailleurs++;
        }
        return { part: flaques / pavees, ailleurs: ailleurs, reglage: L.B.defs.pluie.effets.flaques.part };
    }""")
    assert r["ailleurs"] == 0, "une flaque hors de la rue et du trottoir"
    assert abs(r["part"] - r["reglage"]) < 0.01, r


def test_l_orage_a_ses_eclairs_et_la_pluie_ne_tire_aucun_de(banc):
    r = banc("function (L, o) {" + MOMENTS + """
        L.Jeu.commencer();
        let jo = 17; while (!(L.Pluie.journee(jo) && L.Pluie.journee(jo).orage)) jo++;
        const a = L.Pluie.journee(jo); L.B.partie.jour = jo; L.B.partie.heure = (a.debut + a.fin) / 2 / 24;
        L.graine(3);
        const tirage = L.B.rng; let des = 0;
        L.B.rng = function () { if (String(new Error().stack).indexOf('pluie.js') >= 0) des++; return tirage(); };
        let eclairs = 0;
        const ctx = { fillStyle: '', fillRect: function () {} };
        for (let k = 0; k < 60 * L.B.defs.pluie.effets.eclair_s * 3; k++) {
            L.B.t++; if (L.Pluie.eclair() > 0) eclairs++;
            if (k % 10 === 0) { L.Pluie.maj(); L.Pluie.dessiner(ctx); }
        }
        L.B.rng = tirage;
        return { eclairs: eclairs, des: des };
    }""")
    assert r["eclairs"] > 0, "un orage sans éclair"
    assert r["des"] == 0


#: Un char lancé sur une flaque, un passant à côté.
FLAQUE = """
    function surUneFlaque(L, vitesse) {
        const M = L.Monde, P = L.Pluie, c = M.carte, n = (L.B.defs.carte.nord && L.B.defs.carte.nord.decalage) || 0;
        let t = null;
        for (let y = n + 20; y < c.h && !t; y++) for (let x = 0; x < c.w; x++) if (M.estRoute(x, y) && P.flaqueSur(x, y)) { t = [x, y]; break; }
        L.B.entites = L.B.entites.filter(function (e) { return e === L.B.joueur || (e.type !== 'vehicule' && e.type !== 'pieton'); });
        const j = L.B.joueur; j.x = t[0] * 16 + 8; j.y = t[1] * 16 + 8 - 120; L.Monde.centrerCamera(j.x, j.y);
        const v = L.Vehicules.creer('auto', t[0] * 16 + 8, t[1] * 16 + 8, 0, { etat: 'stationne', couleur: '#3a6fb0' });
        v.vx = vitesse; v.vy = 0; v.vitesse = vitesse;
        L.Entites.indexer();
        return v;
    }
"""


def test_un_char_qui_passe_dans_une_flaque_eclabousse(banc):
    r = banc("function (L, o) {" + MOMENTS + FLAQUE + """
        L.Jeu.commencer();
        pleine(L, 'printemps');
        const v = surUneFlaque(L, 3);
        const avant = L.B.particules.length;
        L.Pluie.majChar(v);
        const vite = { gouttes: L.B.particules.length - avant, repit: v.flaqueT };
        L.Pluie.majChar(v);
        const encore = L.B.particules.length - avant - vite.gouttes;
        const w = surUneFlaque(L, 0.5); const avant2 = L.B.particules.length; L.Pluie.majChar(w);
        const lent = L.B.particules.length - avant2;
        sec(L); L.B.partie.heure = 0.5; const x = surUneFlaque(L, 3); const avant3 = L.B.particules.length; L.Pluie.majChar(x);
        return { vite: vite, encore: encore, lent: lent, sec: L.B.particules.length - avant3, mots: L.B.defs.pluie.eclabousses };
    }""")
    assert r["vite"]["gouttes"] >= 6 and r["vite"]["repit"] > 0, r
    assert r["encore"] == 0, "la même flaque éclabousse à chaque image"
    assert r["lent"] == 0, "un char au pas éclabousse"
    assert r["sec"] == 0, "une flaque éclabousse par temps sec"


def test_le_passant_eclabousse_proteste(banc):
    r = banc("function (L, o) {" + MOMENTS + FLAQUE + """
        L.Jeu.commencer();
        pleine(L, 'printemps');
        const v = surUneFlaque(L, 3);
        const p = L.Entites.creerPieton(v.x, v.y + 18, L.Entites.archetypeDeRue());
        L.Entites.indexer();
        L.Pluie.majChar(v);
        return { bulle: p.bulle ? p.bulle.texte : null, mots: L.B.defs.pluie.eclabousses };
    }""")
    assert r["bulle"] in r["mots"], r


def test_en_octobre_un_char_souleve_des_feuilles(banc):
    r = banc("function (L, o) {" + MOMENTS + FLAQUE + """
        L.Jeu.commencer();
        function compte(jour) {
            L.B.partie.jour = jour; L.B.partie.heure = 0.5;
            const v = surUneFlaque(L, 3), avant = L.B.particules.length;
            for (let k = 0; k < 40; k++) { L.B.t++; v.flaqueT = 999; L.Pluie.majChar(v); }
            return L.B.particules.length - avant;
        }
        return { octobre: compte(32), juillet: compte(21) };
    }""")
    assert 4 <= r["octobre"] <= 15, r
    assert r["juillet"] == 0, "des feuilles mortes en juillet"


def test_la_boucle_du_jeu_fait_eclabousser(banc):
    """Pas seulement `majChar` appelé à la main : un char qui roule, image par image, dans une flaque."""
    r = banc("function (L, o) {" + MOMENTS + FLAQUE + """
        L.Jeu.commencer();
        if (L.Hud.fermerMenu) L.Hud.fermerMenu();
        pleine(L, 'printemps');
        const v = surUneFlaque(L, 3);
        const j = L.B.joueur; L.Vehicules.monter(j, v);
        let repit = 0;
        o.touche('KeyW');
        for (let k = 0; k < 30 && !repit; k++) { v.x = Math.floor(v.x / 16) * 16 + 8; o.frame(1); repit = v.flaqueT || 0; }
        o.relacher('KeyW');
        return { repit: repit };
    }""")
    assert r["repit"] > 0, "la boucle du jeu ne fait pas éclabousser"


def test_la_pluie_s_entend_et_le_tonnerre_suit_l_eclair(banc):
    r = banc("function (L, o) {" + MOMENTS + """
        L.Jeu.commencer();
        const S = L.Son, appels = { lieux: [], boucle: [], tonnerres: [] };
        S.Lieu.charger = function (l) { appels.lieux.push(l); };
        const boucle = S.boucle; S.boucle = function (slug, actif) { if (slug === 'pluie') appels.boucle.push(actif); };
        S.reglerBoucle = function () {};
        S.SFX.tonnerre = function () { appels.tonnerres.push(L.B.t); };
        sec(L); L.Pluie.maj();
        const auSec = { lieux: appels.lieux.length, boucle: appels.boucle.length };
        let jo = 17; while (!(L.Pluie.journee(jo) && L.Pluie.journee(jo).orage)) jo++;
        const a = L.Pluie.journee(jo); L.B.partie.jour = jo; L.B.partie.heure = (a.debut + a.fin) / 2 / 24;
        const eclairs = [];
        for (let k = 0; k < 60 * L.B.defs.pluie.effets.eclair_s * 3; k++) { L.B.t++; if (L.Pluie.eclairA(L.B.t) === 1) eclairs.push(L.B.t); L.Pluie.maj(); }
        sec(L); L.Pluie.maj();
        S.boucle = boucle;
        return { auSec: auSec, lieux: appels.lieux, boucle: appels.boucle, tonnerres: appels.tonnerres, eclairs: eclairs,
                 apres: L.B.defs.pluie.effets.tonnerre_apres };
    }""")
    assert r["auSec"] == {"lieux": 0, "boucle": 0}, "le son de la pluie par temps sec"
    assert "pluie" in r["lieux"], "les sons de la pluie ne se chargent pas à la première averse"
    assert r["boucle"][0] is True and r["boucle"][-1] is False, "la boucle ne démarre pas ou ne se tait pas"
    assert r["tonnerres"], "l'orage n'a pas de tonnerre"
    lo, hi = r["apres"]
    for t in r["tonnerres"]:
        assert any(lo <= t - e <= hi for e in r["eclairs"]), f"un tonnerre sans éclair avant lui ({t})"


def test_la_boucle_monte_avec_l_averse_image_par_image(banc):
    """L'averse monte sur `montee_h` : image par image, le volume de la boucle doit suivre jusqu'au plein
    (la relecture l'a trouvé figé à son volume de départ, presque muet)."""
    r = banc("function (L, o) {" + MOMENTS + """
        L.Jeu.commencer();
        const S = L.Son, P = L.Pluie; let regle = 0, charges = 0;
        S.Lieu.charger = function () { charges++; };
        S.boucle = function () {};
        S.reglerBoucle = function (slug, v) { if (slug === 'pluie') regle = v; };
        let j = 11; while (!P.journee(j) || P.journee(j).orage) j++;
        const a = P.journee(j), parImage = 1 / (L.B.defs.economie.jour_secondes * 60);
        L.B.partie.jour = j; L.B.partie.heure = a.debut / 24;
        const n = Math.ceil((a.montee / 24) / parImage) + 60;
        for (let k = 0; k < n; k++) { L.B.partie.heure += parImage; L.B.t++; P.maj(); }
        return { regle: regle, charges: charges, images: n };
    }""")
    assert r["regle"] > 0.5, f"la boucle est restée à {r['regle']:.3f} au plein de l'averse"
    assert r["charges"] <= 1 + r["images"] // 300, f"les sons de la pluie redemandés {r['charges']} fois"


def test_le_passager_ne_proteste_pas_et_une_bulle_en_cours_reste(banc):
    r = banc("function (L, o) {" + MOMENTS + FLAQUE + """
        L.Jeu.commencer();
        pleine(L, 'printemps');
        const v = surUneFlaque(L, 3), A = L.Entites.archetypeDeRue();
        const passager = L.Entites.creerPieton(v.x, v.y, A); passager.dansVehicule = v;
        const occupe = L.Entites.creerPieton(v.x + 8, v.y + 10, A); L.Entites.bulle(occupe, 'JE PARLE', { duree: 200 });
        const passant = L.Entites.creerPieton(v.x, v.y + 20, A);
        L.Entites.indexer();
        L.Pluie.majChar(v);
        const mot = function (e) { return e.bulle ? e.bulle.texte : null; };
        return { passager: mot(passager), occupe: mot(occupe), passant: mot(passant), mots: L.B.defs.pluie.eclabousses };
    }""")
    assert r["passager"] is None, "le passager du char proteste"
    assert r["occupe"] == "JE PARLE", "l'éclaboussure a écrasé une bulle en cours"
    assert r["passant"] in r["mots"], r


def test_l_eclair_se_peint_par_dessus_la_nuit(banc):
    """Le flash n'est plus dans la couche de pluie (sous le voile de nuit) : `dessinerEclair`, sur l'écran."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const P = L.Pluie;
        let jo = 17; while (!(P.journee(jo) && P.journee(jo).orage)) jo++;
        const a = P.journee(jo); L.B.partie.jour = jo; L.B.partie.heure = (a.debut + a.fin) / 2 / 24;
        while (P.eclair() < 1) L.B.t++;
        const pluie = { fillStyle: '', grands: 0, fillRect: function (x, y, w, h) { if (w >= L.VW && h >= L.VH && this.fillStyle.indexOf('236,241,255') >= 0) this.grands++; } };
        const ecran = { fillStyle: '', grands: 0, fillRect: pluie.fillRect };
        P.dessiner(pluie); P.dessinerEclair(ecran);
        return { pluie: pluie.grands, ecran: ecran.grands };
    }""")
    assert r["pluie"] == 0 and r["ecran"] == 1, r
