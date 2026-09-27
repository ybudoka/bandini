"""Le ciné-parc, au banc (docs/jalons/le-cine-parc.md) : on y entre par le bord ouest des Érables ; le film
ne joue que les soirs d'été ; des spectateurs sont garés dans les rangées pendant la séance et repartent
après ; le trafic n'y entre pas ; rouler phares allumés pendant le film fait klaxonner, se garer dans une
case les éteint."""

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
"""


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
