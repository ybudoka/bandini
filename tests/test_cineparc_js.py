"""Le ciné-parc, au banc (docs/jalons/le-cine-parc.md) : on y entre par le bord ouest des Érables ; le film
ne joue que les soirs d'été ; des spectateurs sont garés dans les rangées pendant la séance et repartent
après ; le trafic n'y entre pas ; rouler phares allumés pendant le film fait klaxonner, se garer dans une
case les éteint. Le casse-croûte est au milieu du terrain, dans l'axe de l'écran, et vend de quoi grignoter
l'été ; c'est aussi la cabine du projecteur, dont le faisceau va jusqu'à la toile pendant la séance
(docs/jalons/le-casse-croute-du-cine-parc-au-centre-et-le-projecteur.md)."""

from app import magasins
from app.blocs import cineparc

OUTILS = """
  const TT = 16;
  function passage(L) { return L.B.defs.blocs.find(function (b) { return b.slug === 'cineparc'; }).passage; }
  async function laisserArriver(L, o) { for (let i = 0; i < 6; i++) { o.frame(1); await o.attendre(); } }
  async function entrer(L, o, jour, heure) {
    const B = L.B, j = B.joueur, p = passage(L);
    B.partie.jour = jour; B.partie.heure = heure / 24;
    if (B.menu) L.Hud.fermerMenu();
    j.x = TT + 8; j.y = (p.de + 2) * TT + 8; L.Entites.indexer();
    await laisserArriver(L, o);
    o.touche('KeyA');
    for (let i = 0; i < 120 && !B.transition; i++) o.frame(1);
    o.relacher('KeyA');
    for (let i = 0; i < 100; i++) o.frame(1);
    await laisserArriver(L, o);
    for (let i = 0; i < 20; i++) o.frame(1);
  }
  // Un jour d'ete, un jour d'hiver (l'annee du jeu).
  function ete(L) { return L.B.defs.calendrier.dates.saint_jean + 3; }
  function entrerAuCasseCroute(L, o) {
    const B = L.B, j = B.joueur, porte = L.Monde.carte.def.portes.find(function (q) { return q.interieur === 'casse_croute_cineparc'; });
    if (!porte) return null;
    j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    return B.interieur && B.interieur.points.find(function (q) { return q.type === 'emplettes'; });
  }
  function libelles(m) { return m ? m.items.map(function (i) { return i.libelle; }) : null; }
  // Un faux pinceau : il note les points des cones et compte ce qu'il peint.
  function pinceau() {
    const p = { points: [], remplis: 0, grains: 0 };
    p.save = p.restore = p.beginPath = p.closePath = function () {};
    p.moveTo = p.lineTo = function (x, y) { p.points.push([x, y]); };
    p.fill = function () { p.remplis++; };
    p.fillRect = function () { p.grains++; };
    return p;
  }
"""


def test_le_casse_croute_est_au_milieu_du_terrain_dans_l_axe_de_l_ecran():
    """Martin : « la cabane doit être au centre ». Le seul bâtiment du stationnement est centré sur l'écran (à la
    tuile près), entre la première et la dernière rangée de cases ; sa porte mène à son comptoir, et la fenêtre
    de la cabine est sur son toit, dans le même axe."""
    plan, b = cineparc.PLAN, cineparc.BLOC
    rangees = [y for y, ligne in enumerate(plan) if "^" in ligne]
    bati = [(x, y) for y, ligne in enumerate(plan) for x, g in enumerate(ligne)
            if g in "OFWDd" and rangees[0] <= y <= rangees[-1]]
    assert bati, "pas de casse-croûte dans le stationnement"
    xs, ys = [x for x, _ in bati], [y for _, y in bati]
    centre = (min(xs) + max(xs) + 1) / 2
    e = b["ecran"]
    assert abs(centre - (e["x"] + e["l"] / 2)) <= 0.5, (centre, e)
    assert rangees[0] < min(ys) and max(ys) < rangees[-1], (ys, rangees)
    assert len(bati) == (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1), "un seul bâtiment, d'un bloc"
    porte = b["portes"][0]
    assert (porte["x"], porte["y"]) in bati
    piece = b["pieces"][porte["interieur"]]
    assert [p.get("genre") for p in piece["points"] if p["type"] == "emplettes"] == ["cineparc"]
    c = b["cabine"]
    assert c["y"] == min(ys) and c["x"] == e["x"] + e["l"] / 2, c


def test_le_rialto_et_le_casse_croute_vendent_le_grignotage_du_cinema():
    for genre in ("rialto", "cineparc"):
        slugs = [a["slug"] for a in magasins.COMPTOIRS[genre]["articles"]]
        assert {"mais", "chips", "nachos", "liqueur"} <= set(slugs), (genre, slugs)


def test_le_casse_croute_sert_l_ete_le_soir_et_se_dit_ferme_sinon(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions;
        await entrer(L, o, ete(L), 20);
        const pt = entrerAuCasseCroute(L, o);
        if (!pt) return { piece: B.interieur && B.interieur.slug };
        const soir = libelles(M.menuDuPoint(pt));
        B.partie.heure = 11 / 24; const matin = libelles(M.menuDuPoint(pt));
        B.partie.jour = 2; B.partie.heure = 20 / 24; const hiver = libelles(M.menuDuPoint(pt));
        return { piece: B.interieur.slug, soir: soir, matin: matin, hiver: hiver };
    }""")
    assert r["piece"] == "casse_croute_cineparc", r
    for nom in ("MAÏS SOUFFLÉ", "CHIPS", "NACHOS", "LIQUEUR"):
        assert nom in r["soir"], r["soir"]
    assert len(r["matin"]) == 1 and r["matin"][0].startswith("FERMÉ"), r["matin"]
    assert r["hiver"] == ["FERMÉ — ON ROUVRE L'ÉTÉ"], r["hiver"]


def test_le_projecteur_eclaire_la_toile_depuis_la_cabine_pendant_la_seance(banc):
    """Pendant la séance, le faisceau part de la fenêtre de la cabine et s'ouvre sur toute la largeur de la
    toile, et le rendu du jeu le peint ; le midi, rien."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cineparc;
        await entrer(L, o, ete(L), 21.5);
        const bloc = L.Monde.carte.def.bloc, e = bloc.ecran, c = bloc.cabine, vue = { x: 0, y: 0 };
        const soir = pinceau(); C.dessinerFaisceau(soir, vue);
        let appels = 0; const vrai = C.dessinerFaisceau;
        C.dessinerFaisceau = function () { appels++; return vrai.apply(null, arguments); };
        L.Jeu.rendre();
        C.dessinerFaisceau = vrai;
        B.partie.heure = 13 / 24; for (let i = 0; i < 5; i++) o.frame(1);
        const midi = pinceau(); C.dessinerFaisceau(midi, vue);
        return { soir: soir, midi: { remplis: midi.remplis, grains: midi.grains }, appels: appels,
                 lentille: [c.x * TT, c.y * TT], toile: [e.x * TT, (e.x + e.l) * TT, (e.y + e.h) * TT] };
    }""")
    s, (lx, ly), (x0, x1, ty) = r["soir"], r["lentille"], r["toile"]
    assert s["remplis"] >= 3 and s["grains"] >= 10, s
    haut = [p for p in s["points"] if abs(p[1] - ly) < 1]
    bas = [p for p in s["points"] if abs(p[1] - ty) < 1]
    assert haut and all(abs(x - lx) <= 2 for x, _ in haut), (haut, r["lentille"])
    assert bas and min(x for x, _ in bas) <= x0 + 1 and max(x for x, _ in bas) >= x1 - 1, (bas, r["toile"])
    assert r["appels"] >= 1, "le rendu du jeu ne peint pas le faisceau"
    assert r["midi"] == {"remplis": 0, "grains": 0}, r["midi"]


def test_le_film_ne_joue_que_les_soirs_d_ete_et_les_spectateurs_avec_lui(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cineparc;
        await entrer(L, o, ete(L), 21.5);
        const soir = { ici: C.ici(), bloc: B.bloc && B.bloc.slug, seance: C.seance(), spectateurs: C.spectateurs().length,
                       dansLesCases: C.spectateurs().every(function (v) { return C.dansUneCase(v.x, v.y - 4); }),
                       trafic: B.entites.filter(function (e) { return e.type === 'vehicule' && e.conducteur === 'trafic'; }).length,
                       lueur: C.lampes({ x: 0, y: 0 }).length };
        B.partie.heure = 13 / 24; for (let i = 0; i < 5; i++) o.frame(1);
        const midi = { seance: C.seance(), spectateurs: C.spectateurs().length, lueur: C.lampes({ x: 0, y: 0 }).length };
        B.partie.jour = 2; B.partie.heure = 21.5 / 24; for (let i = 0; i < 5; i++) o.frame(1);
        const hiver = { seance: C.seance(), spectateurs: C.spectateurs().length };
        return { soir: soir, midi: midi, hiver: hiver };
    }""")
    s = r["soir"]
    assert s["ici"] and s["bloc"] == "cineparc", r
    assert s["seance"] and s["spectateurs"] >= 4 and s["dansLesCases"] and s["lueur"] >= 1, s
    assert s["trafic"] == 0, "le trafic est entré au ciné-parc"
    assert r["midi"] == {"seance": False, "spectateurs": 0, "lueur": 0}, r["midi"]
    assert r["hiver"] == {"seance": False, "spectateurs": 0}, r["hiver"]


def test_les_phares_pendant_le_film(banc):
    """Au volant pendant la séance : rouler dans les rangées fait klaxonner ; garé dans une case et
    arrêté, les phares s'éteignent — et plus un faisceau ne part du char."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cineparc, V = L.Vehicules, j = B.joueur;
        await entrer(L, o, ete(L), 21.5);
        // Un char, dans l'allee derriere la derniere rangee.
        const cs = C.cases(), libre = cs.find(function (c) { return !C.spectateurs().some(function (v) { return Math.hypot(v.x - c.x, v.y - c.y - 4) < 20; }); });
        const v = V.creer('auto', libre.x - 60, libre.y + 32, 0, { etat: 'stationne', couleur: '#888' });
        V.monter(j, v); L.Entites.indexer();
        const msgs = [], hud = L.Hud.message; L.Hud.message = function (t) { msgs.push(t); return hud.apply(null, arguments); };
        o.touche('KeyW'); for (let i = 0; i < 25; i++) o.frame(1); o.relacher('KeyW');
        const roule = { klaxon: msgs.indexOf('ÉTEINS TES PHARES!') >= 0, eteints: !!v.pharesEteints };
        // Gare dans la case libre, arrete.
        v.x = libre.x; v.y = libre.y + 4; v.angle = -Math.PI / 2; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y;
        L.Entites.indexer();
        for (let i = 0; i < 40; i++) o.frame(1);
        L.Jeu.rendre && L.Jeu.rendre();
        const faisceaux = V.lampesDesPhares().filter(function (l) { return l.faisceau === v || l.phare === v; }).length;
        return { roule: roule, gare: !!v.pharesEteints, faisceaux: faisceaux };
    }""")
    assert r["roule"]["klaxon"] and not r["roule"]["eteints"], r
    assert r["gare"] and r["faisceaux"] == 0, r
