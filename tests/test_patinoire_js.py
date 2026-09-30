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
        poser(L, porte.x * 16 + 8, porte.y * 16 - 12); pousser('KeyS', 150);
        const parLaPorte = { y: j.y, dedans: P.surLaGlace(j.x, j.y) };
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
