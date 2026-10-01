"""La glace noire de l'hiver (`static/js/glace.js`, les quatre saisons, lot 6, vague 6b), au banc.

Où et quand : des plaques à l'empreinte de leur cellule (la chaussée, souvent à la ligne d'arrêt, les
trottoirs, le tablier du pont), tout l'hiver ; en avril et en novembre, le gel et le dégel. Ce qu'elle fait :
le char y dérape (le modèle de la vague 6a) et freine long, les pneus d'hiver en rendent une part ; le trafic
y patine et freine long sur ses rails sans jamais les quitter ; la police y arrive quand même ; le joueur qui
y court glisse et tombe, un passant qui s'y sauve aussi. Rien de posé, aucun dé : la ville ne glisse pas.

⚠️ Chaque juge de conduite se mesure sur PLUSIEURS plaques (ou plusieurs graines) : un juge de conduite tient
parfois par la chance d'une seule (la mémoire « juge vert par chance de graine »).
"""

#: Janvier (l'hiver : la glace tout le jour) et juillet. ⚠️ Le 22, pas le 21 : le 21, le joueur déménage.
JANVIER, JUILLET = 1, 22

OUTILS = """
  const TT = 16;
  function saison(L, jour, heure) { L.B.partie.jour = jour; L.B.partie.heure = heure === undefined ? 0.5 : heure; }
  //: Toutes les plaques de la ville (et celles du pont), triees par distance au joueur.
  function plaques(L, filtre) {
    const G = L.Glace, c = L.Monde.carte, n = G.reglages().cellule, j = L.B.joueur, out = [];
    for (let cy = 0; cy * n < c.h; cy++) for (let cx = 0; cx * n < c.w; cx++) { const p = G.plaqueDe(cx, cy); if (p && (!filtre || filtre(p))) out.push(p); }
    return out.sort(function (a, b) { return Math.hypot(a.x - j.x, a.y - j.y) - Math.hypot(b.x - j.x, b.y - j.y); });
  }
  //: Une plaque de chaussee longue, et le cap qui la traverse dans sa longueur.
  function longues(L, combien) {
    return plaques(L, function (p) { return !p.trottoir && Math.max(p.rx, p.ry) >= 26; }).slice(0, combien);
  }
  function capDe(p) { return p.rx >= p.ry ? 0 : Math.PI / 2; }
  //: Un char lance dans l'axe de la plaque, depuis son bord ; `script(k)` : les commandes ; on l'avance a la main
  //: (pas de murs : on juge le sol). Rend la rotation cumulee, la distance et la vitesse au bout.
  function traverser(L, p, script, n, opts) {
    const V = L.Vehicules, j = L.B.joueur, a = capDe(p), l = Math.max(p.rx, p.ry);
    const v = V.creer('auto', p.x - Math.cos(a) * l * 0.85, p.y - Math.sin(a) * l * 0.85, a, { etat: 'stationne', couleur: '#3a6fb0' });
    v.conducteur = j; if (opts && opts.pneus) v.mods = { pneus: true };
    const s0 = (opts && opts.vitesse) || 3.4;
    v.vitesse = s0; v.vx = Math.cos(a) * s0; v.vy = Math.sin(a) * s0;
    const traj = []; let tourne = 0, prec = v.angle, dist = 0;
    for (let k = 0; k < n; k++) {
      const x0 = v.x, y0 = v.y;
      V.majPhysique(v, Object.assign({ gaz: 0, frein: 0, direction: 0, freinMain: false }, script(k)));
      v.x += v.vx; v.y += v.vy;
      dist += Math.hypot(v.x - x0, v.y - y0);
      tourne += Math.atan2(Math.sin(v.angle - prec), Math.cos(v.angle - prec)); prec = v.angle;
      traj.push([v.x, v.y, v.angle, v.vx, v.vy]);
      if (opts && opts.arret && Math.abs(v.vitesse) < 0.15) break;
    }
    L.Entites.retirer(v);
    return { tourne: Math.abs(tourne), dist: dist, traj: traj, images: traj.length };
  }
"""


def test_la_glace_suit_le_calendrier_sans_saut(banc):
    """Pleine tout le jour l'hiver ; rien l'été ; en avril et en novembre, la glace du matin fond vers midi et
    regèle le soir si le lendemain gèle — et jamais de saut, ni à minuit, ni d'une saison à l'autre."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const G = L.Glace, i = function (j, h) { return +G.intensiteA(j, h / 24).toFixed(3); };
        let saut = 0;
        for (let k = 0; k < 80 * 96; k++) {
            const a = G.intensiteA(1 + Math.floor(k / 96), (k % 96) / 96), b = G.intensiteA(1 + Math.floor((k + 1) / 96), ((k + 1) % 96) / 96);
            saut = Math.max(saut, Math.abs(a - b));
        }
        return { janvier: [i(1, 3), i(1, 14), i(1, 23)], mars: i(10, 15), juillet: [i(22, 6), i(22, 23)],
                 avril: [i(11, 6), i(11, 10), i(11, 14), i(11, 22)], finAvril: [i(13, 6), i(13, 22), i(14, 3)],
                 novembre: [i(34, 6), i(34, 22), i(35, 6), i(35, 14)], octobre: i(33, 6), annee2: i(41, 14), saut: saut };
    }""")
    assert r["janvier"] == [1, 1, 1] and r["mars"] == 1 and r["annee2"] == 1, r
    assert r["juillet"] == [0, 0] and r["octobre"] == 0, r
    a = r["avril"]
    assert a[0] == 1 and 0 < a[1] < 1 and a[2] == 0 and 0 < a[3] < 1, f"le gel et le dégel d'avril : {a}"
    assert r["finAvril"][0] == 1 and r["finAvril"][1] == 0 and r["finAvril"][2] == 0, "le dernier soir d'avril regèle vers mai"
    n = r["novembre"]
    assert n[0] == 0 and 0 < n[1] < 1 and n[2] == 1 and n[3] == 0, f"les premiers gels de novembre : {n}"
    assert r["saut"] <= 0.07, f"la glace saute de {r['saut']:.2f} en un quart d'heure"


def test_les_plaques_sont_a_l_empreinte_sur_la_rue_et_le_pont(banc):
    """Les mêmes plaques à toutes les graines ; chacune sur sa surface (l'asphalte, ou le trottoir), jamais
    ailleurs ; des plaques sur la ligne d'arrêt, sur les trottoirs, et sur le tablier du pont de La Pointe."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const G = L.Glace, M = L.Monde, cles = [];
        for (const g of [1, 777, 4242]) { L.graine(g); G.oublier(); cles.push(plaques(L).map(function (p) { return p.cle + '@' + Math.round(p.x) + ',' + Math.round(p.y); }).join('|')); }
        const toutes = plaques(L);
        let hors = 0, points = 0;
        for (const p of toutes.slice(0, 120).concat(G.plaquesDuPont())) {
            for (let y = p.y - p.ry * 1.3; y <= p.y + p.ry * 1.3; y += 2) for (let x = p.x - p.rx * 1.3; x <= p.x + p.rx * 1.3; x += 2) {
                if (!G.dans(p, x, y)) continue;
                points++;
                const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
                if (p.trottoir ? !M.estTrottoir(tx, ty) : !M.estRoute(tx, ty)) hors++;
            }
        }
        const pont = L.B.defs.carte.ponts[0], surLePont = G.plaquesDuPont().filter(function (p) {
            return p.x >= pont.x * TT && p.x <= (pont.x + pont.l) * TT && p.y >= pont.y * TT && p.y <= (pont.y + pont.h) * TT; }).length;
        return { memes: cles[0] === cles[1] && cles[1] === cles[2], n: toutes.length, trottoir: toutes.filter(function (p) { return p.trottoir; }).length,
                 arret: toutes.filter(function (p) { return !p.trottoir && M.fleche(Math.floor(p.x / TT), Math.floor(p.y / TT)) === 'S'; }).length,
                 hors: hors, points: points, pont: G.plaquesDuPont().length, surLePont: surLePont };
    }""")
    assert r["memes"], "les plaques changent avec la graine"
    assert 200 <= r["n"] <= 1500, f"{r['n']} plaques dans la ville"
    assert r["trottoir"] >= 0.15 * r["n"] and r["arret"] >= 20, r
    assert r["points"] > 1000 and r["hors"] == 0, f"{r['hors']} points de glace hors de leur surface"
    assert r["pont"] >= 4 and r["surLePont"] == r["pont"], f"le tablier du pont n'a pas sa glace : {r}"


def test_la_glace_ne_tire_aucun_de_et_ne_pose_rien(banc):
    """Deux cents images de janvier peintes et roulées (la nuit comprise) entre deux tirages de `B.rng()` :
    la glace n'en a pas tiré un seul, et elle n'a créé aucune entité."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const G = L.Glace, B = L.B, j = B.joueur;
        saison(L, """ + str(JANVIER) + """, 0.9);
        const ctx = L.Base.nouveauCanvas(480, 270).getContext('2d'), p = plaques(L)[0];
        const vue = { x: p.x - 240, y: p.y - 135 };
        const n0 = B.entites.length, id0 = L.Entites.prochainId ? L.Entites.prochainId() : null;
        L.graine(9); const temoin = [B.rng(), B.rng()];
        L.graine(9);
        let peint = 0, luit = 0;
        for (let k = 0; k < 200; k++) {
            B.t++; B.image = (B.image || 0) + 1;
            ctx.traces = null; const avant = B.stats.images || 0; G.dessinerSol(ctx, vue); peint += (B.stats.images || 0) - avant;
            luit += G.lampes(vue, [{ cone: [3, 18], ox: p.x - 80, oy: p.y, ca: 1, sa: 0, r: 120, x: 0, y: 0 }]).length; G.dessinerReflets(ctx, vue);
            G.sous(p.x, p.y); G.adherence({ x: p.x, y: p.y, def: {} }); G.surRails({ x: p.x, y: p.y, def: {}, id: 3 });
        }
        return { temoin: temoin, apres: [B.rng(), B.rng()], peint: peint, luit: luit, n: B.entites.length - n0 };
    }""")
    assert r["peint"] > 0 and r["luit"] > 0, f"le juge n'a rien peint : {r}"
    assert r["apres"] == r["temoin"], "la glace a tiré au dé du jeu"
    assert r["n"] == 0, "la glace a posé des entités"


def test_elle_se_voit_le_jour_et_luit_la_nuit_sous_la_lumiere(banc):
    """Le jour, les plaques à l'écran se peignent ; l'été, dedans, rien. La nuit, une plaque sous un vrai
    lampadaire, ou dans le faisceau d'un phare, renvoie une lueur froide ; loin de toute lumière, rien, et un feu
    de circulation ne compte pas ; le jour, aucune lueur."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const G = L.Glace, B = L.B, M = L.Monde, c = M.carte;
        const allumees = c.lampes.filter(function (l) { return !l.panne && !l.eteinte && l.c !== 'fenetre' && !l.sorte; });
        const pres = function (q, r) { return allumees.some(function (l) { return Math.hypot(l.x - q.x, l.y - q.y) < r; }); };
        const p = plaques(L, function (q) { return !q.trottoir && pres(q, 40); })[0];
        const seule = plaques(L, function (q) { return !q.trottoir && !pres(q, 400); })[0];
        const vue = { x: p.x - 240, y: p.y - 135 }, vueSeule = { x: seule.x - 240, y: seule.y - 135 };
        const ctx = L.Base.nouveauCanvas(480, 270).getContext('2d');
        function images() { const a = B.stats.images || 0; G.dessinerSol(ctx, vue); return (B.stats.images || 0) - a; }
        // Le jour, meme un phare braque sur une plaque n'y allume rien.
        const conePlein = [{ cone: [3, 18], ox: seule.x - 80, oy: seule.y, ca: 1, sa: 0, r: 120, x: 0, y: 0 }];
        saison(L, """ + str(JANVIER) + """, 0.5); const jour = images(), lueurJour = G.lampes(vue, []).length + G.lampes(vueSeule, conePlein).length;
        saison(L, """ + str(JUILLET) + """, 0.5); const ete = images();
        saison(L, """ + str(JANVIER) + """, 0.95);
        const lampadaire = G.lampes(vue, []).length;
        // Loin de tout lampadaire : rien — meme sous un feu de circulation (une lampe sans cone, deja ramassee).
        const feu = { x: seule.x - vueSeule.x + 10, y: seule.y - vueSeule.y, r: 30, c: 'rgba(255,40,40,0.5)' };
        const loin = G.lampes(vueSeule, [feu]).length;
        // Un phare : 80 px avant la plaque, qui la regarde ; puis, juste passe la plaque, qui lui tourne le dos.
        const phare = function (dx, ca) { return G.lampes(vueSeule, [{ cone: [3, 18], ox: seule.x + dx, oy: seule.y, ca: ca, sa: 0, r: 120, x: 0, y: 0 }]).length; };
        const dansLePhare = phare(-80, 1), dos = phare(10, 1);
        B.interieur = { slug: 'essai' }; const dedans = images(); B.interieur = null;
        return { jour: jour, ete: ete, lueurJour: lueurJour, lampadaire: lampadaire, loin: loin, dansLePhare: dansLePhare, dos: dos, dedans: dedans };
    }""")
    assert r["jour"] >= 1 and r["ete"] == 0 and r["dedans"] == 0, r
    assert r["lueurJour"] == 0, "le jour, la glace luit"
    assert r["lampadaire"] >= 1 and r["loin"] == 0, f"sous le lampadaire : {r}"
    assert r["dansLePhare"] >= 1 and r["dos"] == 0, f"dans le phare : {r}"


def test_sur_une_plaque_le_char_sous_vire_et_freine_long(banc):
    """Six plaques de chaussée, dans leur longueur, lancé à 3,4 px/image : volant à fond, le char tourne moins
    en janvier qu'en juillet (le dérapage de la vague 6a s'éveille) ; frein à fond, il s'arrête plus loin ; et
    les pneus d'hiver rendent une part du virage. Hors de toute plaque, janvier se conduit comme juillet."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const out = [];
        for (const p of longues(L, 6)) {
            const vire = function () { return { gaz: 0.5, direction: 1 }; }, freine = function () { return { frein: 1 }; };
            saison(L, """ + str(JUILLET) + """); const ete = traverser(L, p, vire, 14), arretEte = traverser(L, p, freine, 200, { arret: true });
            saison(L, """ + str(JANVIER) + """); const hiver = traverser(L, p, vire, 14), arretHiver = traverser(L, p, freine, 200, { arret: true });
            const pneus = traverser(L, p, vire, 14, { pneus: true });
            out.push({ ete: +ete.tourne.toFixed(3), hiver: +hiver.tourne.toFixed(3), pneus: +pneus.tourne.toFixed(3),
                       arretEte: Math.round(arretEte.dist), arretHiver: Math.round(arretHiver.dist),
                       rouesEte: arretEte.images, rouesHiver: arretHiver.images });
        }
        // Loin de toute plaque : la meme trajectoire, au pixel, avec et sans la glace.
        const G = L.Glace, j = L.B.joueur, V = L.Vehicules;
        let sec = null;
        for (let k = 0; k < 400 && !sec; k++) {
            const x = j.x + (k % 20) * 64 - 640, y = j.y + Math.floor(k / 20) * 64 - 640;
            let libre = true;
            for (let dy = -200; dy <= 200 && libre; dy += 8) for (let dx = -200; dx <= 260 && libre; dx += 8) if (G.sous(x + dx, y + dy)) libre = false;
            if (libre) sec = { x: x, y: y, rx: 40, ry: 10 };
        }
        const script = function (k) { return { gaz: k % 20 < 12 ? 1 : 0, direction: k < 20 ? 1 : -0.5, frein: k > 30 ? 1 : 0, freinMain: k > 24 && k < 30 }; };
        const avec = traverser(L, sec, script, 40); G.couper(true); const sans = traverser(L, sec, script, 40); G.couper(false);
        return { plaques: out, pareil: JSON.stringify(avec.traj) === JSON.stringify(sans.traj) };
    }""")
    assert len(r["plaques"]) == 6, r
    for p in r["plaques"]:
        assert p["hiver"] < 0.8 * p["ete"], f"sur la glace, le char tourne comme au sec : {p}"
        assert p["arretHiver"] > 1.2 * p["arretEte"], f"sur la glace, le char s'arrête aussi court qu'au sec : {p}"
        # Les ROUES (la vitesse du char, pas la caisse qui glisse) : le frein mord moins sur la glace.
        assert p["rouesHiver"] > 1.2 * p["rouesEte"], f"sur la glace, le frein mord comme au sec : {p}"
        assert p["pneus"] > p["hiver"] * 1.1, f"les pneus d'hiver ne se sentent pas sur la glace : {p}"
    assert r["pareil"], "hors de toute plaque, la glace change la conduite"


def test_la_police_arrive_sur_la_glace_sans_tourner_en_rond(banc):
    """Une auto de patrouille lancée de cinq façons autour du joueur (de dos, de côté, à pleine vitesse), sur la
    glace du verglas puis sur une plaque : elle l'atteint toujours, plus tard qu'au sec peut-être, sans faire
    un tour sur elle-même — elle rattrape son arrière (vague 6a), elle ne tourne pas autour de lui."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, V = L.Vehicules, M = L.Monde, j = B.joueur, c = M.carte;
        let site = null;
        chercher: for (let ty = (B.defs.decalage_nord || 0) + 10; ty < c.h - 30; ty += 2) for (let tx = 4; tx < c.w - 30; tx += 2) {
            let ok = true;
            for (let dy = 0; dy < 26 && ok; dy++) for (let dx = 0; dx < 26 && ok; dx++) if (M.solidite(tx + dx, ty + dy) !== 0) ok = false;
            if (ok) { site = { x: (tx + 13) * TT, y: (ty + 13) * TT }; break chercher; }
        }
        for (const e of B.entites.slice()) if (e !== j && (e.type === 'vehicule' || e.type === 'pieton')) L.Entites.retirer(e);
        const cible = V.creer('auto', site.x, site.y, 0, { etat: 'stationne' });
        V.monter(j, cible); j.intouchable = true;
        L.Police.ajouterChaleur(6);
        const G = L.Glace, vraieSous = G.adherence;
        function essai(sol, depart) {
            if (sol === 'verglas') saison(L, B.defs.verglas.tempete.premier + 1); else saison(L, """ + str(JUILLET) + """);
            // « plaque » : tout le terrain est une plaque de glace noire (on juge la conduite, pas la carte).
            if (sol === 'plaque') G.adherence = function () { return G.reglages().adherence; };
            const v = V.creer('police', site.x + depart[0], site.y + depart[1], depart[2], { conducteur: 'police', etat: 'roule', sirene: true, poursuite: true });
            v.vitesse = depart[3]; v.vx = Math.cos(depart[2]) * depart[3]; v.vy = Math.sin(depart[2]) * depart[3];
            let tourne = 0, prec = v.angle, atteint = -1;
            for (let k = 0; k < 300; k++) {
                const cmd = L.Police.commandes(v);
                if (cmd === 'rails') break;
                V.majPhysique(v, cmd);
                v.x += v.vx; v.y += v.vy; B.t++;
                tourne += Math.abs(Math.atan2(Math.sin(v.angle - prec), Math.cos(v.angle - prec))); prec = v.angle;
                if (Math.hypot(v.x - cible.x, v.y - cible.y) < 34) { atteint = k; break; }
            }
            G.adherence = vraieSous;
            L.Entites.retirer(v);
            return { atteint: atteint, tourne: +tourne.toFixed(2) };
        }
        const departs = [[0, -60, 0, 4.5], [80, 0, Math.PI / 2, 4.5], [0, 50, Math.PI, 5], [-60, 0, -Math.PI / 2, 4], [40, 40, 2.4, 5]];
        const out = {};
        for (const sol of ['sec', 'verglas', 'plaque']) out[sol] = departs.map(function (d) { return essai(sol, d); });
        return out;
    }""")
    for sol in ("sec", "verglas", "plaque"):
        for k, e in enumerate(r[sol]):
            assert e["atteint"] >= 0, f"{sol}, départ {k} : la police n'arrive jamais ({e})"
            assert e["tourne"] < 2 * 3.1416, f"{sol}, départ {k} : la police tourne en rond ({e})"
    lent = sum(e["atteint"] for e in r["verglas"]) > sum(e["atteint"] for e in r["sec"])
    assert lent, f"sur le verglas, la police arrive aussi vite qu'au sec : le juge ne mesure pas la glace ({r})"


def test_le_trafic_patine_et_freine_long_sans_quitter_ses_rails(banc):
    """Un char du trafic sur une plaque, qui doit s'arrêter : il glisse plus loin qu'en juillet, la caisse chasse
    un peu, il finit ARRÊTÉ et repart en patinant ; la police en poursuite n'y glisse pas. Et à la LIGNE D'ARRÊT
    glacée (six plaques posées sur une ligne `S`) : il arrive plus vite qu'au sec, mais s'arrête pile sur son point
    d'arrêt, jamais au-delà, sur l'axe de sa voie, le cap droit."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const V = L.Vehicules, M = L.Monde, out = [], lignes = [];
        for (const p of longues(L, 6)) {
            const a = capDe(p), l = Math.max(p.rx, p.ry);
            function freinage(jour, poursuite) {
                saison(L, jour);
                const v = V.creer('auto', p.x - Math.cos(a) * l * 0.8, p.y - Math.sin(a) * l * 0.8, a, { conducteur: 'trafic', etat: 'roule', couleur: '#777' });
                v.poursuite = !!poursuite;
                v.cible = { x: v.x + Math.cos(a) * 200, y: v.y + Math.sin(a) * 200 };
                v.vitesse = 2.2;
                const x0 = v.x, y0 = v.y;
                let k = 0, roulis = 0;
                while (v.vitesse > 0 && k < 300) {
                    V.rouler(v, 0); v.x += v.vx; v.y += v.vy; k++;
                    roulis = Math.max(roulis, Math.abs(Math.atan2(Math.sin(v.angle - a), Math.cos(v.angle - a))));
                }
                const glisse = Math.hypot(v.x - x0, v.y - y0), arrete = v.vitesse === 0;
                // Il repart : combien d'images pour reprendre 1 px/image.
                let repart = 0; while (v.vitesse < 1 && repart < 300) { V.rouler(v, 2.2); v.x += v.vx; v.y += v.vy; repart++; }
                L.Entites.retirer(v);
                return { glisse: +glisse.toFixed(1), roulis: +roulis.toFixed(3), arrete: arrete, repart: repart };
            }
            out.push({ ete: freinage(""" + str(JUILLET) + """), hiver: freinage(""" + str(JANVIER) + """), poursuite: freinage(""" + str(JANVIER) + """, true) });
        }
        const PAS = { '>': [1, 0], '<': [-1, 0], 'v': [0, 1], '^': [0, -1] };
        for (const p of plaques(L, function (q) { const t = [Math.floor(q.x / TT), Math.floor(q.y / TT)]; return !q.trottoir && M.fleche(t[0], t[1]) === 'S' && PAS[M.sensArret(t[0], t[1])]; }).slice(0, 10)) {
            const sx = Math.floor(p.x / TT), sy = Math.floor(p.y / TT), d = PAS[M.sensArret(sx, sy)], a = Math.atan2(d[1], d[0]);
            function aLaLigne(jour) {
                saison(L, jour);
                const v = V.creer('auto', (sx - 5 * d[0]) * TT + 8, (sy - 5 * d[1]) * TT + 8, a, { conducteur: 'trafic', etat: 'roule', couleur: '#777' });
                const ligne = V.pointDArret(v, sx, sy, d);
                v.cible = ligne; v.vitesse = 2.2;
                let k = 0, depasse = 0, ecart = 0, arrivee = null, glace = 0;
                for (; k < 400; k++) {
                    V.rouler(v, V.approcheDeLaLigne(v)); v.x += v.vx; v.y += v.vy;
                    if (L.Glace.surRails(v)) glace++;
                    depasse = Math.max(depasse, (v.x - ligne.x) * d[0] + (v.y - ligne.y) * d[1]);
                    ecart = Math.max(ecart, Math.abs((v.x - ligne.x) * d[1] - (v.y - ligne.y) * d[0]));
                    if (arrivee === null && Math.hypot(v.x - ligne.x, v.y - ligne.y) < 1) arrivee = +Math.abs(v.vitesse).toFixed(2);
                    if (arrivee !== null && Math.hypot(v.vx, v.vy) === 0 && k > 3) break;
                }
                const cap = Math.abs(Math.atan2(Math.sin(v.angle - a), Math.cos(v.angle - a)));
                L.Entites.retirer(v);
                return { depasse: +depasse.toFixed(3), ecart: +ecart.toFixed(3), arrivee: arrivee, cap: +cap.toFixed(4), glace: glace };
            }
            lignes.push({ ete: aLaLigne(""" + str(JUILLET) + """), hiver: aLaLigne(""" + str(JANVIER) + """) });
        }
        return { out: out, lignes: lignes };
    }""")
    # Les lignes dont la plaque est sur le chemin du char (une plaque de travers peut tomber a cote de sa voie).
    sur = [e for e in r["lignes"] if e["hiver"]["glace"] > 3]
    assert len(r["out"]) == 6 and len(sur) >= 4, r
    for e in r["out"]:
        h, s = e["hiver"], e["ete"]
        assert h["glisse"] > 1.4 * s["glisse"], f"sur la glace, le trafic freine comme au sec : {e}"
        assert h["arrete"], f"le trafic ne s'arrête pas sur la glace : {e}"
        assert 0 < h["roulis"] <= 0.15 and s["roulis"] == 0, f"la caisse ne chasse pas (ou trop) : {e}"
        assert h["repart"] > s["repart"], f"il repart sur la glace comme au sec : {e}"
        assert e["poursuite"] == s, f"la police en poursuite glisse sur ses rails : {e}"
    for e in r["lignes"]:
        h, s = e["hiver"], e["ete"]
        assert h["arrivee"] is not None and h["depasse"] <= 0.01 and h["cap"] <= 0.02, f"il passe la ligne, ou reste de travers : {e}"
    for e in sur:
        h, s = e["hiver"], e["ete"]
        assert h["arrivee"] is not None and h["depasse"] <= 0.01 and h["ecart"] <= 0.01, f"il passe la ligne glacée, ou sort de sa voie : {e}"
        assert h["cap"] <= 0.02, f"arrêté à la ligne glacée, il reste de travers : {e}"
        assert h["arrivee"] > s["arrivee"], f"il n'arrive pas plus vite à la ligne glacée : {e}"


def test_sur_la_glace_le_trafic_ne_fauche_pas_un_pieton(banc):
    """La relecture : sur une plaque, le frein à 45 % amenait l'auto sur le passant planté dans sa voie
    au-dessus de la vitesse qui renverse. Devant quelqu'un à pied, le trafic garde son frein plein : sur six
    plaques de voie, le passant n'est jamais blessé, et l'auto s'arrête derrière lui."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, V = L.Vehicules, M = L.Monde, E = L.Entites, j = B.joueur, out = [];
        const PAS = { '>': [1, 0], '<': [-1, 0], 'v': [0, 1], '^': [0, -1] };
        B.defs.conduite.trafic.vehicules_max = 0;
        j.invincible = 1e9; B.partie.dette = 0;
        saison(L, """ + str(JANVIER) + """);
        const voies = plaques(L, function (q) { return !q.trottoir && Math.max(q.rx, q.ry) >= 24 && PAS[M.fleche(Math.floor(q.x / TT), Math.floor(q.y / TT))]; }).slice(0, 6);
        for (const p of voies) {
            const tx = Math.floor(p.x / TT), ty = Math.floor(p.y / TT), d = PAS[M.fleche(tx, ty)];
            for (const e of B.entites.slice()) if (e !== j && (e.type === 'vehicule' || e.type === 'pieton')) E.retirer(e);
            j.x = p.x + 300; j.y = p.y + 300;
            const l = Math.max(p.rx, p.ry);
            const lx = function (k) { return d[0] ? p.x + d[0] * k : tx * TT + 8; }, ly = function (k) { return d[1] ? p.y + d[1] * k : ty * TT + 8; };
            // ⚠️ Il SURGIT a 38 px devant l'auto lancee sur la plaque (il sort d'entre deux chars) : de loin, la
            // demi-vitesse de la distance de securite suffisait, meme sur la glace.
            const passant = E.creerPieton(lx(-l * 0.6 + 38), ly(-l * 0.6 + 38), null);
            passant.etat = 'fige';
            const v = V.creer('auto', lx(-l * 0.6), ly(-l * 0.6), Math.atan2(d[1], d[0]), { conducteur: 'trafic', etat: 'roule', couleur: '#777', sens: M.fleche(tx, ty) });
            v.vitesse = 2.2;
            E.indexer();
            let glace = 0, vmax = 0;
            for (let k = 0; k < 150; k++) {
                o.frame(1);
                if (L.Glace.sous(v.x, v.y)) glace++;
                if (Math.hypot(v.x - passant.x, v.y - passant.y) < 40) vmax = Math.max(vmax, Math.abs(v.vitesse));
            }
            out.push({ glace: glace, vivant: passant.vivant, vie: passant.vie, vieMax: passant.vieMax, vmax: +vmax.toFixed(2),
                       arrete: Math.hypot(v.vx, v.vy) < 0.05, devant: Math.hypot(v.x - passant.x, v.y - passant.y) > 10 });
            E.retirer(v); E.retirer(passant);
        }
        return out;
    }""")
    # Celles qui ont freiné SUR la glace jusqu'à l'arrêt (une autre a pu doubler par la voie d'à côté : c'est permis).
    for e in r:
        assert e["vivant"] and e["vie"] == e["vieMax"] and e["devant"], f"sur la glace, le trafic a fauché le passant : {e}"
    sur = [e for e in r if e["glace"] > 3 and e["arrete"]]
    assert len(sur) >= 3, f"les autos ne s'arrêtent pas sur la glace : le juge ne prouve rien ({r})"


def test_la_ville_roule_l_hiver_sans_tourner_en_rond(banc):
    """Quatre graines, deux mille images de janvier autour du terminus, la trace du trafic allumée : des chars
    passent sur la glace, et la trace ne crie ni au char qui tourne en rond ni au hors-voie."""
    r = banc("function (L, o) {" + OUTILS + """
        const out = [];
        for (const g of [3, 11, 29, 57]) {
            L.Jeu.commencer();
            L.graine(g);
            const B = L.B; B.options.trace = true; B.joueur.invincible = 1e9; B.partie.dette = 0;
            saison(L, """ + str(JANVIER) + """, 0.45);
            o.frame(2);
            let surGlace = 0;
            for (let k = 0; k < 2000; k++) {
                o.frame(1);
                for (const v of B.entites) if (v.type === 'vehicule' && v.conducteur === 'trafic' && L.Glace.surRails(v)) surGlace++;
            }
            out.push({ graine: g, surGlace: surGlace, anomalies: B.trace.anomalies.map(function (a) { return a.quoi; }) });
        }
        return out;
    }""")
    for e in r:
        assert e["surGlace"] > 50, f"graine {e['graine']} : le trafic n'a pas touché la glace, le juge ne prouve rien ({e})"
        assert not [a for a in e["anomalies"] if a in ("TOURNE EN ROND", "HORS VOIE")], f"graine {e['graine']} : {e['anomalies']}"


def test_le_joueur_qui_court_sur_la_glace_glisse_et_tombe(banc):
    """Quatre plaques de trottoir : en courant (ESQUIVE tenue) dans leur longueur, le joueur tombe en janvier,
    pas en juillet ; en marchant, jamais ; avec des bottes d'hiver, il tient plus longtemps."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, G = L.Glace;
        j.invincible = 1e9; B.partie.dette = 0;
        const out = [];
        const S = B.defs.saisons.joueur, bottes = Object.keys(S.chaleur).find(function (k) { return S.chaleur[k] > 0; });
        const souliers = Object.keys(S.chaleur).find(function (k) { return !(S.chaleur[k] > 0); }) || 'souliers';
        for (const p of plaques(L, function (q) { return q.trottoir && Math.max(q.rx, q.ry) >= 24; }).slice(0, 4)) {
            const a = capDe(p), l = Math.max(p.rx, p.ry), touche = a === 0 ? 'KeyD' : 'KeyS';
            function essai(jour, courir, chaussures) {
                saison(L, jour);
                j.x = p.x - Math.cos(a) * l * 0.5; j.y = p.y - Math.sin(a) * l * 0.5; j.vx = 0; j.vy = 0; j.auSol = 0; j.face = 'bas'; j.endurance = 999; j.courseSurPlaque = 0;
                j.tenue = Object.assign({}, j.tenue, { souliers: chaussures || souliers });
                L.Entites.indexer();
                let tombe = -1, glace = 0;
                if (courir) o.touche('ShiftLeft');
                o.touche(touche);
                for (let k = 0; k < 40 && tombe < 0; k++) {
                    o.frame(1);
                    if (G.sous(j.x, j.y)) glace++;
                    if (j.auSol > 0) tombe = k;
                    // On le ramene au debut de la plaque : on juge la glace, pas la longueur du trottoir.
                    if (!G.sous(j.x, j.y) && glace > 3) { j.x = p.x - Math.cos(a) * l * 0.5; j.y = p.y - Math.sin(a) * l * 0.5; }
                }
                o.relacher(touche); if (courir) o.relacher('ShiftLeft');
                o.frame(70);
                return { tombe: tombe, glace: glace, releve: !(j.auSol > 0) };
            }
            out.push({ court: essai(""" + str(JANVIER) + """, true), marche: essai(""" + str(JANVIER) + """, false),
                       ete: essai(""" + str(JUILLET) + """, true), bottes: essai(""" + str(JANVIER) + """, true, bottes) });
        }
        return { out: out, bottes: bottes };
    }""")
    assert len(r["out"]) == 4, r
    for e in r["out"]:
        assert e["court"]["glace"] > 0, f"le juge ne passe pas sur la glace : {e}"
        assert e["court"]["tombe"] >= 0 and e["court"]["releve"], f"courir sur la glace ne fait pas tomber : {e}"
        assert e["marche"]["tombe"] < 0, f"on tombe en marchant : {e}"
        assert e["ete"]["tombe"] < 0, f"on tombe en juillet : {e}"
        assert e["bottes"]["tombe"] < 0 or e["bottes"]["tombe"] > e["court"]["tombe"], f"les bottes ne tiennent pas mieux : {e}"


def test_un_passant_qui_s_y_sauve_tombe_mais_pas_celui_d_une_mission(banc):
    """Un passant qui se sauve en courant à travers une plaque tombe (puis se relève et reprend sa fuite) ;
    en juillet, non ; un passant d'une mission, jamais. Sur quatre plaques."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, G = L.Glace, E = L.Entites;
        j.invincible = 1e9; B.partie.dette = 0;
        const out = [];
        for (const p of plaques(L, function (q) { return Math.max(q.rx, q.ry) >= 24; }).slice(0, 4)) {
            const a = capDe(p), l = Math.max(p.rx, p.ry);
            function essai(jour, drapeau) {
                saison(L, jour);
                for (const e of B.entites.slice()) if (e.type === 'pieton') E.retirer(e);
                const e = E.creerPieton(p.x - Math.cos(a) * l * 0.5, p.y - Math.sin(a) * l * 0.5, null);
                if (drapeau) e[drapeau] = drapeau === 'mission' ? { slug: 'essai' } : true;
                const menace = { x: e.x - Math.cos(a) * 60, y: e.y - Math.sin(a) * 60, vivant: true };
                e.etat = 'fuit'; e.menace = menace; e.minuterie = 600; e.allure = 1;
                j.x = p.x + 400; j.y = p.y + 400; E.indexer();
                let tombe = -1, reprend = false;
                for (let k = 0; k < 120; k++) {
                    E.majPieton ? E.majPieton(e) : o.frame(1);
                    e.x += 0; B.t++;
                    if (tombe < 0 && e.chuteGlace > 0) tombe = k;
                    if (tombe >= 0 && !(e.chuteGlace > 0) && e.etat === 'fuit' && Math.hypot(e.vx, e.vy) > 0.5) { reprend = true; break; }
                    // Ramene au debut de la plaque tant qu'il n'est pas tombe.
                    if (tombe < 0 && !G.sous(e.x, e.y) && Math.hypot(e.x - p.x, e.y - p.y) > l) { e.x = p.x - Math.cos(a) * l * 0.5; e.y = p.y - Math.sin(a) * l * 0.5; e.menace.x = e.x - Math.cos(a) * 60; e.menace.y = e.y - Math.sin(a) * 60; }
                }
                E.retirer(e);
                return { tombe: tombe, reprend: reprend };
            }
            out.push({ hiver: essai(""" + str(JANVIER) + """), ete: essai(""" + str(JUILLET) + """), mission: essai(""" + str(JANVIER) + """, 'mission') });
        }
        return { out: out, direct: typeof L.Entites.majPieton === 'function' };
    }""")
    assert r["direct"], "Entites.majPieton n'est pas exportée : le juge ne mène pas le passant"
    for e in r["out"]:
        assert e["hiver"]["tombe"] >= 0 and e["hiver"]["reprend"], f"le passant ne tombe pas, ou ne se relève pas : {e}"
        assert e["ete"]["tombe"] < 0, f"il tombe en juillet : {e}"
        assert e["mission"]["tombe"] < 0, f"le passant d'une mission tombe : {e}"


def test_assomme_pendant_sa_chute_il_reste_couche(banc):
    """La relecture : un passant tombé sur la glace, puis assommé avant de s'être relevé, se redessinait debout à
    la fin de sa chute. C'est le K.-O. qui le tient : il reste couché tant qu'il est assommé."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, E = L.Entites, j = B.joueur;
        saison(L, """ + str(JANVIER) + """);
        const e = E.creerPieton(j.x + 200, j.y + 200, null);
        e.chuteGlace = 10; e.face = 'couche';
        E.majPieton(e);
        E.assommer(e);
        const faces = [];
        for (let k = 0; k < 30; k++) { E.majPieton(e); B.t++; if (e.etat === 'assomme') faces.push(e.face); }
        return { faces: Array.from(new Set(faces)), chute: e.chuteGlace || 0 };
    }""")
    assert r["faces"] == ["couche"], f"assommé, il se redessine debout : {r}"
    assert r["chute"] == 0, r


def test_le_verglas_tombe_pour_tout_le_monde_les_derniers_jours_de_mars(banc):
    """Plus d'option (une vieille sauvegarde qui l'avait éteinte la perd) : le verglas tombe les trois derniers
    jours de mars, chaque année, et ces soirs-là la pluie verglaçante prend la place de la tempête de neige."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const V = L.Verglas, C = L.Calendrier, N = L.Neige, jours = [];
        for (let d = 1; d <= 120; d++) if (V.intensiteA(d, 0.5) > 0) jours.push(d);
        L.B.partie.jour = 9; L.B.partie.heure = 0.5;
        const neige = [];
        for (const d of jours) neige.push(N.intensiteA(d, 21 / 24));
        return { jours: jours, mois: jours.map(function (d) { return C.mois(d); }), maintenant: V.intensite(),
                 cle: 'verglas' in L.B.options, neige: neige, autreTempete: N.intensiteA(5, 21 / 24),
                 clairon: V.ligneDuClairon() };
    }""", stockage={"bandini-options-v1": '{"verglas": false, "brouillard": false}'})
    assert r["jours"] == [8, 9, 10, 48, 49, 50, 88, 89, 90], r["jours"]
    assert set(r["mois"]) == {"mars"}, r["mois"]
    assert r["maintenant"] == 1 and r["cle"] is False, "une vieille option éteinte empêche encore le verglas"
    assert r["neige"] == [0] * 9 and r["autreTempete"] > 0, "il neige un soir de verglas"
    assert r["clairon"] and r["clairon"].startswith("VERGLAS"), r


def test_le_menu_n_offre_plus_l_option_du_verglas():
    from pathlib import Path
    racine = Path(__file__).resolve().parent.parent
    assert "VERGLAS (ESSAI)" not in (racine / "static" / "js" / "hud.js").read_text(encoding="utf-8")
