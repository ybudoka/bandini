"""La patinoire du parc, au banc (docs/jalons/la-patinoire-du-parc.md ; `static/js/patinoire.js`) : l'hiver la
glace et ses bandes, l'été rien ; les bandes arrêtent les gens (sauf aux portes) et les chars ; sur la glace on
glisse — l'élan, l'arrêt qui prend du temps — et courir sans patins fait tomber. Rien de posé, aucun dé."""

from pathlib import Path


RACINE = Path(__file__).resolve().parent.parent

#: Janvier (la neige tient) et juillet. ⚠️ Le 22, pas le 21 : le 21, le joueur déménage.
JANVIER, JUILLET = 2, 22

OUTILS = """
  function saison(L, jour) { L.B.partie.jour = jour; L.B.partie.heure = 0.5; }
  function poser(L, x, y) {
    const j = L.B.joueur; j.x = x; j.y = y; j.vx = 0; j.vy = 0; j.gx = 0; j.gy = 0; j.auSol = 0; j.face = 'bas';
    j.endurance = 999; j.invincible = 1e6; L.Entites.indexer();
  }
  function peindre(L) {
    const g = L.Patinoire.geo(), ctx = L.Base.nouveauCanvas(512, 256).getContext('2d'); ctx.traces = [];
    L.Patinoire.dessinerSol(ctx, { x: g.x0 - 40, y: g.y0 - 40 });
    return ctx.traces.length;
  }
"""


def test_la_glace_l_hiver_seulement(banc):
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const P = L.Patinoire, g = P.geo(), mx = (g.x0 + g.x1) / 2, my = (g.y0 + g.y1) / 2;
        saison(L, """ + str(JANVIER) + """); const hiver = { ouverte: P.ouverte(), glace: P.surLaGlace(mx, my), traits: peindre(L) };
        saison(L, """ + str(JUILLET) + """); const ete = { ouverte: P.ouverte(), glace: P.surLaGlace(mx, my), traits: peindre(L) };
        return { hiver: hiver, ete: ete, bandes: g.bandes.length, portes: g.portes.length };
    }""")
    assert r["hiver"]["ouverte"] and r["hiver"]["glace"] and r["hiver"]["traits"] > 20, r["hiver"]
    assert not r["ete"]["ouverte"] and not r["ete"]["glace"] and r["ete"]["traits"] == 0, r["ete"]
    assert r["bandes"] >= 4 + r["portes"] - 1, "les portes ne coupent pas les bandes"


def test_les_bandes_arretent_le_passant_et_la_porte_le_laisse_entrer(banc):
    """Le joueur pousse vers la glace par le sud, au milieu de la bande : il reste dehors. Par la porte, il
    entre. L'été, la bande n'est plus là."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const P = L.Patinoire, g = P.geo(), p = g.p, j = L.B.joueur;
        const porte = g.portes.find(function (q) { return q.cote === 'nord'; }) || g.portes[0];
        const mx = (g.x0 + g.x1) / 2;
        const pousser = function (touche, n) { o.touche(touche); o.frame(n); o.relacher(touche); o.frame(1); };
        saison(L, """ + str(JANVIER) + """);
        poser(L, mx + 5, g.y1 + 10); pousser('KeyW', 90); const sud = { y: j.y, dedans: P.surLaGlace(j.x, j.y) };
        // ⚠️ On regarde PENDANT la marche : la porte de service d'en face (deuxième vague) laisse ressortir.
        poser(L, porte.x * 16 + 8, porte.y * 16 - 12);
        let entre = false;
        o.touche('KeyS'); for (let k = 0; k < 150 && !entre; k++) { o.frame(1); entre = P.surLaGlace(j.x, j.y); } o.relacher('KeyS'); o.frame(1);
        const parLaPorte = { y: j.y, dedans: entre };
        saison(L, """ + str(JUILLET) + """);
        poser(L, mx + 5, g.y1 + 10); pousser('KeyW', 60); const ete = { y: j.y };
        return { sud: sud, porte: parLaPorte, ete: ete, y1: g.y1, cote: porte.cote };
    }""")
    assert not r["sud"]["dedans"] and r["sud"]["y"] > r["y1"], f"le joueur a traversé la bande sud : {r['sud']}"
    assert r["porte"]["dedans"], f"la porte ({r['cote']}) ne laisse pas entrer : {r['porte']}"
    assert r["ete"]["y"] < r["y1"] - 20, "l'été, une bande invisible arrête encore"


def test_un_char_n_entre_pas_sur_la_glace_l_hiver(banc):
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const P = L.Patinoire, g = P.geo(), p = g.p, M = L.Monde;
        const v = { type: 'vehicule', x: (p.x + 3) * 16 + 8, y: (p.y + p.h + 2) * 16 + 8 };
        const dedans = { type: 'vehicule', x: (p.x + 3) * 16 + 8, y: (p.y + 2) * 16 + 8 };
        const tx = p.x + 3, ty = p.y + p.h - 1;
        saison(L, """ + str(JANVIER) + """); const hiver = [M.barriereBloque(v, tx, ty), M.barriereBloque(dedans, tx, ty)];
        saison(L, """ + str(JUILLET) + """); const ete = M.barriereBloque(v, tx, ty);
        return { hiver: hiver, ete: ete };
    }""")
    assert r["hiver"] == [True, False], "l'hiver, un char entre sur la glace (ou celui qui y est ne peut plus en sortir)"
    assert r["ete"] is False, "l'été, la clairière arrête un char"


def test_sur_la_glace_on_glisse(banc):
    """Au milieu de la glace, pousser à droite une demi-seconde puis lâcher : on part moins vite qu'au sec,
    et on continue sur son élan — au sec, on s'arrête net."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const P = L.Patinoire, g = P.geo(), j = L.B.joueur;
        const essai = function (jour) {
            saison(L, jour);
            poser(L, g.x0 + 30, (g.y0 + g.y1) / 2);
            const x0 = j.x;
            o.touche('KeyD'); o.frame(30); o.relacher('KeyD');
            const pousse = j.x - x0, x1 = j.x;
            o.frame(40);
            return { pousse: pousse, erre: j.x - x1, auSol: j.auSol || 0 };
        };
        return { glace: essai(""" + str(JANVIER) + """), sec: essai(""" + str(JUILLET) + """) };
    }""")
    glace, sec = r["glace"], r["sec"]
    assert glace["auSol"] == 0 and sec["auSol"] == 0, r
    assert glace["pousse"] < sec["pousse"] * 0.8, f"sur la glace on part aussi vite qu'au sec : {r}"
    assert glace["erre"] > 12 and sec["erre"] < 1, f"on ne glisse pas sur son élan : {r}"


def test_courir_sans_patins_fait_tomber(banc):
    """ESQUIVE tenue en poussant, sur la glace : on tombe (`auSol`) — sans un dé. En marchant, jamais."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const P = L.Patinoire, g = P.geo(), j = L.B.joueur, my = (g.y0 + g.y1) / 2;
        saison(L, """ + str(JANVIER) + """);
        const essai = function (courir) {
            poser(L, g.x0 + 20, my);
            let tombe = false;
            if (courir) o.touche('ShiftLeft');
            o.touche('KeyD');
            for (let k = 0; k < 110 && !tombe; k++) { o.frame(1); tombe = j.auSol > 0; if (j.x > g.x1 - 30) { j.x = g.x0 + 20; } }
            o.relacher('KeyD'); if (courir) o.relacher('ShiftLeft');
            o.frame(80);
            return { tombe: tombe, releve: !(j.auSol > 0) };
        };
        return { marche: essai(false), court: essai(true) };
    }""")
    assert not r["marche"]["tombe"], "on tombe en marchant"
    assert r["court"]["tombe"] and r["court"]["releve"], f"courir sans patins ne fait pas tomber, ou on reste par terre : {r}"


def test_un_passant_glisse_aussi(banc):
    """Un passant sur la glace ne prend pas sa vitesse d'un coup ; au sec, si."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const P = L.Patinoire, g = P.geo(), B = L.B;
        saison(L, """ + str(JANVIER) + """);
        const e = { type: 'pieton', x: (g.x0 + g.x1) / 2, y: (g.y0 + g.y1) / 2, vx: 1, vy: 0, gx: 0, gy: 0, gt: B.t - 1 };
        P.glisser(e, false);
        const sec = { type: 'pieton', x: g.x0 - 60, y: g.y0 - 60, vx: 1, vy: 0, gx: 0, gy: 0, gt: B.t - 1 };
        P.glisser(sec, false);
        return { glace: e.vx, sec: sec.vx, elan: B.defs.patinoire.glisse.pieton.elan };
    }""")
    assert abs(r["glace"] - r["elan"]) < 1e-9 and r["sec"] == 1, r


def test_rien_n_est_tire_au_de():
    """La patinoire ne tire aucun dé : un `B.rng()` de plus décalerait tout ce que la ville tire ensuite."""
    source = (RACINE / "static" / "js" / "patinoire.js").read_text(encoding="utf-8")
    assert "rng(" not in source and "Math.random" not in source


# --- Vague 2 : les patineurs -------------------------------------------------------------------------------

#: Le joueur à 300 px sous la patinoire : assez près pour qu'elle se peuple, et elle hors de l'écran.
APPROCHER = """
  function approcher(L, o, jour, heure) {
    const B = L.B, g = L.Patinoire.geo();
    saison(L, jour); B.partie.heure = heure;
    poser(L, (g.x0 + g.x1) / 2, g.y1 + 300);
    o.frame(30);
    return g;
  }
"""


def test_ils_naissent_hors_de_l_ecran_a_l_heure_de_patiner(banc):
    """L'après-midi d'hiver, en approchant : la glace se peuple, hors de l'écran, sur la glace. L'été, et à trois
    heures du matin, personne."""
    r = banc("function (L, o) {" + OUTILS + APPROCHER + """
        L.Jeu.commencer();
        const P = L.Patinoire, B = L.B;
        const compte = function () {
            const e = P.enCours();
            return { n: e.length, glace: e.filter(function (q) { return P.surLaGlace(q.x, q.y); }).length,
                     vrais: e.filter(function (q) { return B.entites.indexOf(q) >= 0 && q.type === 'pieton'; }).length,
                     enfants: e.filter(function (q) { return q.arch === 'enfant'; }).length };
        };
        const g = approcher(L, o, """ + str(JANVIER) + """, 14 / 24);
        const apresMidi = compte(), voulu = P.voulus(14 / 24), aLEcran = L.Entites.visibleAEcran((g.x0 + g.x1) / 2, (g.y0 + g.y1) / 2, 0);
        approcher(L, o, """ + str(JANVIER) + """, 3 / 24); const nuit = compte();
        approcher(L, o, """ + str(JANVIER) + """, 14 / 24);
        approcher(L, o, """ + str(JUILLET) + """, 14 / 24); const ete = compte();
        return { apresMidi: apresMidi, voulu: voulu, aLEcran: aLEcran, nuit: nuit, ete: ete };
    }""")
    a = r["apresMidi"]
    assert not r["aLEcran"], "le juge regarde la patinoire : personne ne doit y naître sous ses yeux"
    assert r["voulu"] >= 6 and a["n"] == r["voulu"] and a["glace"] == a["n"] and a["vrais"] == a["n"], r
    assert r["nuit"]["n"] == 0, f"on patine à trois heures du matin : {r['nuit']}"
    assert r["ete"]["n"] == 0, f"on patine en juillet : {r['ete']}"


def test_ils_tournent_a_contre_sens_des_aiguilles_sur_la_glace(banc):
    """Pendant dix secondes, chacun tourne à contre-sens des aiguilles d'une montre (à l'écran, l'angle autour
    du centre DÉCROÎT) et aucun ne quitte la glace."""
    r = banc("function (L, o) {" + OUTILS + APPROCHER + """
        L.Jeu.commencer();
        const P = L.Patinoire;
        const g = approcher(L, o, """ + str(JANVIER) + """, 14 / 24);
        const cx = (g.x0 + g.x1) / 2, cy = (g.y0 + g.y1) / 2, rx = (g.x1 - g.x0) / 2, ry = (g.y1 - g.y0) / 2;
        const angle = function (e) { return Math.atan2((e.y - cy) / ry, (e.x - cx) / rx); };
        const suivis = P.enCours().slice(), tour = suivis.map(function () { return 0; }), avant = suivis.map(angle);
        let dehors = 0;
        for (let k = 0; k < 600; k++) {
            o.frame(1);
            suivis.forEach(function (e, i) {
                if (e.face === 'couche') return;
                let d = angle(e) - avant[i];
                if (d > Math.PI) d -= 2 * Math.PI; if (d < -Math.PI) d += 2 * Math.PI;
                tour[i] += d; avant[i] = angle(e);
                if (!P.surLaGlace(e.x, e.y)) dehors++;
            });
        }
        return { tour: tour, dehors: dehors, restent: P.enCours().length, n: suivis.length };
    }""")
    assert r["n"] >= 6 and r["restent"] == r["n"], r
    assert r["dehors"] == 0, f"des patineurs sortent de la glace : {r['dehors']} images"
    assert all(t < -1.0 for t in r["tour"]), f"des patineurs ne tournent pas (ou à l'envers) : {r['tour']}"


def test_un_patineur_bouscule_n_est_plus_mene(banc):
    """Qu'il fuie : la patinoire le lâche — c'est un passant comme un autre, et il glisse en se sauvant."""
    r = banc("function (L, o) {" + OUTILS + APPROCHER + """
        L.Jeu.commencer();
        const P = L.Patinoire;
        approcher(L, o, """ + str(JANVIER) + """, 14 / 24);
        const e = P.enCours().find(function (q) { return q.arch !== 'enfant'; });
        e.etat = 'fuit'; e.minuterie = 600;
        o.frame(20);
        return { mene: P.enCours().indexOf(e) >= 0, patineur: e.patineur, etat: e.etat };
    }""")
    assert not r["mene"] and r["patineur"] is False, r


def test_un_enfant_tombe_parfois(banc):
    """Sur deux minutes d'après-midi, un enfant finit par tomber (couché), et se relève."""
    r = banc("function (L, o) {" + OUTILS + APPROCHER + """
        L.Jeu.commencer();
        const P = L.Patinoire;
        approcher(L, o, """ + str(JANVIER) + """, 14 / 24);
        const enfants = P.enCours().filter(function (q) { return q.arch === 'enfant'; });
        let tombe = null, releve = false;
        for (let k = 0; k < 7200 && !releve; k++) {
            o.frame(1);
            for (const e of enfants) {
                if (!tombe && e.face === 'couche') tombe = e;
            }
            if (tombe && tombe.face !== 'couche') releve = true;
        }
        return { enfants: enfants.length, tombe: !!tombe, releve: releve };
    }""")
    assert r["enfants"] >= 1, "aucun enfant sur la glace"
    assert r["tombe"] and r["releve"], r


# --- Vague 3 : les patins à louer --------------------------------------------------------------------------

#: Le joueur sur la glace, au guichet, face à lui.
AU_GUICHET = """
  function auGuichet(L) {
    const P = L.Patinoire, q = P.guichet(), g = P.geo();
    const dx = { est: -10, ouest: 10, nord: 0, sud: 0 }[q.cote], dy = { nord: 10, sud: -10, est: 0, ouest: 0 }[q.cote];
    poser(L, q.x + dx, q.y + dy);
    L.Entites.regarder(L.B.joueur, -dx, -dy);
    return q;
  }
"""


def test_au_guichet_deux_piastres_et_on_chausse(banc):
    """ACTION au guichet, sur la glace : l'invite le dit, deux piastres partent, on a ses patins. Sans le sou,
    on ne paie pas et on reste en bottes."""
    r = banc("function (L, o) {" + OUTILS + AU_GUICHET + """
        L.Jeu.commencer();
        const B = L.B, P = L.Patinoire, j = B.joueur;
        saison(L, """ + str(JANVIER) + """);
        auGuichet(L); B.partie.argent = 50; o.frame(2);
        const invite = B.invite;
        o.tape('KeyE', 2);
        const loue = { argent: B.partie.argent, patins: !!j.patins };
        j.patins = false; auGuichet(L); B.partie.argent = 1; o.frame(2);
        o.tape('KeyE', 2);
        const fauche = { argent: B.partie.argent, patins: !!j.patins };
        return { invite: invite, loue: loue, fauche: fauche };
    }""")
    assert r["invite"] and "PATINS" in r["invite"] and "2 $" in r["invite"], r
    assert r["loue"] == {"argent": 48, "patins": True}, r
    assert r["fauche"] == {"argent": 1, "patins": False}, r


def test_en_patins_plus_vite_mais_on_glisse_encore(banc):
    """En patins, une seconde de poussée mène plus loin qu'en bottes sur la même glace — et en lâchant, on file
    encore sur son élan : on glisse toujours (Martin)."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const P = L.Patinoire, g = P.geo(), j = L.B.joueur;
        saison(L, """ + str(JANVIER) + """);
        const essai = function (patins) {
            poser(L, g.x0 + 24, (g.y0 + g.y1) / 2); j.patins = patins;
            const x0 = j.x;
            o.touche('KeyD'); o.frame(60); o.relacher('KeyD');
            const pousse = j.x - x0, x1 = j.x;
            o.frame(30);
            return { pousse: pousse, erre: j.x - x1, patins: !!j.patins };
        };
        return { bottes: essai(false), patins: essai(true) };
    }""")
    b, p = r["bottes"], r["patins"]
    assert p["pousse"] > b["pousse"] * 1.2, f"en patins on ne va pas plus vite : {r}"
    assert p["erre"] > 15, f"en patins on ne glisse plus : {r}"


def test_on_rend_ses_patins_en_quittant_la_glace(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const P = L.Patinoire, g = P.geo(), j = L.B.joueur;
        const porte = g.portes.find(function (q) { return q.cote === 'nord'; }) || g.portes[0];
        saison(L, """ + str(JANVIER) + """);
        poser(L, porte.x * 16 + 8, porte.y * 16 + 14); j.patins = true;
        o.touche('KeyW'); o.frame(90); o.relacher('KeyW'); o.frame(2);
        return { dehors: !P.surLaGlace(j.x, j.y), patins: !!j.patins };
    }""")
    assert r["dehors"] and not r["patins"], r


# --- Deuxième vague : les chars par la porte de service -----------------------------------------------------

def test_un_char_entre_par_la_porte_de_service_et_pas_ailleurs(banc):
    """L'hiver, un char entre sur la glace par la porte de service (la surfaceuse) — et nulle part ailleurs ; sur la
    glace, il ne ressort pas par une bande, seulement par elle."""
    r = banc("function (L) {" + OUTILS + """
        L.Jeu.commencer();
        const P = L.Patinoire, g = P.geo(), p = g.p, M = L.Monde;
        const s = p.portes.filter(function (q) { return q.service; });
        const pas = { nord: [0, -1], sud: [0, 1], ouest: [-1, 0], est: [1, 0] }[s[0].cote];
        const px = function (tx) { return tx * 16 + 8; };
        saison(L, """ + str(JANVIER) + """);
        const dehors = { type: 'vehicule', x: px(s[0].x + pas[0]), y: px(s[0].y + pas[1]) };
        const entre = M.barriereBloque(dehors, s[0].x, s[0].y);
        const aCote = M.barriereBloque(dehors, s[0].x - 3 * Math.abs(pas[1]), s[0].y - 3 * Math.abs(pas[0]));
        const dedans = { type: 'vehicule', x: px(p.x + 3), y: px(p.y + 2) };
        const parLaBande = M.barriereBloque(dedans, p.x - 1, p.y + 2);
        const surLaPorte = { type: 'vehicule', x: px(s[0].x), y: px(s[0].y) };
        const sort = M.barriereBloque(surLaPorte, s[0].x + pas[0], s[0].y + pas[1]);
        return { n: s.length, entre: entre, aCote: aCote, parLaBande: parLaBande, sort: sort };
    }""")
    assert r["n"] == 2, r
    assert r["entre"] is False and r["sort"] is False, f"la porte de service ne laisse pas passer : {r}"
    assert r["aCote"] is True and r["parLaBande"] is True, f"un char passe à travers une bande : {r}"


#: Un char piloté par script sur la glace (l'hiver) ou au même endroit l'été — la neige, la pluie et la rue mouillée
#: bouchées : seule la glace de la patinoire fait la différence.
CHAR = """
  function conduire(L, jour, script, n) {
    const P = L.Patinoire, g = P.geo(), V = L.Vehicules, N = L.Neige, Pl = L.Pluie, M = L.Monde;
    saison(L, jour);
    const garde = [N.adherence, N.frein, Pl.adherence, Pl.frein, M.adherenceMouillee, M.freinMouille];
    N.adherence = N.frein = Pl.adherence = Pl.frein = M.adherenceMouillee = M.freinMouille = function () { return 1; };
    const v = V.creer('auto', g.x0 + 40, (g.y0 + g.y1) / 2, 0, { etat: 'stationne', couleur: '#3a6fb0' });
    v.conducteur = L.B.joueur; v.vitesse = 2.4; v.vx = 2.4; v.vy = 0;
    let tourne = 0, prec = v.angle;
    for (let k = 0; k < n; k++) {
      V.majPhysique(v, Object.assign({ gaz: 0, frein: 0, direction: 0, freinMain: false }, script(k)));
      tourne += Math.atan2(Math.sin(v.angle - prec), Math.cos(v.angle - prec)); prec = v.angle;
    }
    const out = { vitesse: Math.hypot(v.vx, v.vy), tourne: Math.abs(tourne), glace: P.adherence(v) };
    [N.adherence, N.frein, Pl.adherence, Pl.frein, M.adherenceMouillee, M.freinMouille] = garde;
    L.Entites.retirer(v);
    return out;
  }
"""


def test_sur_la_glace_un_char_glisse(banc):
    """Freiner une demi-seconde : sur la glace, le char file encore ; l'été, au même endroit, il s'arrête. Braquer :
    sur la glace, il tourne moins (il sous-vire)."""
    r = banc("function (L) {" + OUTILS + CHAR + """
        L.Jeu.commencer();
        const freine = function () { return { frein: 1 }; }, braque = function () { return { gaz: 0.5, direction: 1 }; };
        return { hiver: conduire(L, """ + str(JANVIER) + """, freine, 30), ete: conduire(L, """ + str(JUILLET) + """, freine, 30),
                 virageHiver: conduire(L, """ + str(JANVIER) + """, braque, 30), virageEte: conduire(L, """ + str(JUILLET) + """, braque, 30) };
    }""")
    assert r["hiver"]["glace"] < 1 and r["ete"]["glace"] == 1, r
    assert r["hiver"]["vitesse"] > r["ete"]["vitesse"] + 0.5, f"sur la glace le char freine comme au sec : {r}"
    assert r["virageHiver"]["tourne"] < r["virageEte"]["tourne"] * 0.8, f"sur la glace le char tourne comme au sec : {r}"
