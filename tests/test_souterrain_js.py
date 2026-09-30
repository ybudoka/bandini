"""Le grand garage souterrain, JOUÉ (docs/jalons/le-grand-garage-souterrain.md) : on descend, on se gare, on
remonte la rampe et on ressort devant le rideau de Ti-Guy ; les chars rangés y sont encore au retour et au
rechargement ; le rideau et l'ascenseur, au bouton. Voir `static/js/souterrain.js`."""

OUTILS = """
  const TT = 16;
  function proprio(L) { L.B.partie.proprietes.garage = { jour: L.B.partie.jour, caisse: 0 }; }
  // La rue devant le rideau vidée (le trafic et les passants du hasard ne sont pas ce qu'on juge).
  function viderLaBaie(L) {
    const j = L.B.joueur, pg = L.Monde.porteDeGarage('garage'), baie = L.Monde.baieDeLaPorteDeGarage(pg);
    L.B.entites.filter(function (e) { return (e.type === 'vehicule' || e.type === 'pieton') && e !== j
        && Math.hypot(e.x - baie.x, e.y - baie.y) < 300; }).forEach(function (e) { L.Entites.retirer(e); });
    L.B.defs.conduite.trafic.vehicules_max = 0;
    return { pg: pg, baie: baie };
  }
  async function attendreLeBloc(L, o, slug) {
    for (let i = 0; i < 400 && !(L.B.bloc && L.B.bloc.slug === slug && !L.B.transition); i++) {
      o.frame(1); if (i % 10 === 0) await o.attendre();
    }
  }
  async function attendreLaVille(L, o) {
    for (let i = 0; i < 400 && (L.B.bloc || L.B.transition); i++) { o.frame(1); if (i % 10 === 0) await o.attendre(); }
  }
  // Un char à soi, garé nez au rideau, le joueur au volant.
  function auVolantDevant(L, slug, options) {
    const j = L.B.joueur, a = viderLaBaie(L);
    const v = L.Vehicules.creer(slug || 'auto', a.baie.x, a.baie.y, -Math.PI / 2,
                                Object.assign({ etat: 'stationne', couleur: '#c0392b' }, options || {}));
    j.x = v.x; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Monde.centrerCamera(j.x, j.y);
    v.aToi = true;
    return Object.assign({ v: v }, a);
  }
  // Remonter la rampe au gaz, depuis le bas, nez au nord.
  async function remonterLaRampe(L, o, v) {
    const r = L.B.bloc.def.bloc.retour;
    v.x = (r.de + r.l / 2) * TT; v.y = 5 * TT; v.angle = -Math.PI / 2; v.vitesse = 0;
    const j = L.B.joueur; j.x = v.x; j.y = v.y;
    o.touche('KeyW');
    for (let i = 0; i < 300 && !L.B.transition; i++) o.frame(1);
    o.relacher('KeyW');
    await attendreLaVille(L, o);
  }
"""


def test_on_descend_au_noir_et_on_ressort_devant_le_rideau_le_nez_vers_la_rue(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, j = B.joueur, a = auVolantDevant(L);
        L.Blocs.sauter('souterrain', null, null);
        await attendreLeBloc(L, o, 'souterrain');
        const def = B.bloc && B.bloc.def.bloc;
        const dedans = { bloc: B.bloc && B.bloc.slug, auVolant: j.dansVehicule === a.v,
                         tuile: [Math.floor(a.v.x / TT), Math.floor(a.v.y / TT)], cap: +a.v.angle.toFixed(2),
                         arrivee: def && [def.arrivee.x, def.arrivee.y], sortie: B.bloc && B.bloc.ville.sortie,
                         passage: B.bloc && B.bloc.ville.passage };
        await remonterLaRampe(L, o, a.v);
        return { dedans: dedans, apres: { bloc: !!B.bloc, auVolant: j.dansVehicule === a.v, enVille: B.entites.indexOf(a.v) >= 0,
                 x: a.v.x, y: a.v.y, cap: +a.v.angle.toFixed(2), attendu: { x: a.baie.x, y: a.baie.y + 2 * TT + 8 },
                 menu: !!B.menu } };
    }""")
    d, a = r["dedans"], r["apres"]
    assert d["bloc"] == "souterrain" and d["auVolant"], d
    assert d["tuile"] == d["arrivee"], f"on arrive au bas de la rampe : {d}"
    assert d["cap"] == 1.57, f"le nez vers l'allée (le sud) : {d}"
    assert d["passage"] is None and d["sortie"], d
    assert a["bloc"] is False and a["auVolant"] and a["enVille"], a
    assert abs(a["x"] - a["attendu"]["x"]) < 1 and abs(a["y"] - a["attendu"]["y"]) < 20, a
    assert a["cap"] == 1.57, f"on ressort le nez vers la rue : {a}"
    assert a["menu"] is False, "ressortir ne rouvre pas le menu du garage"


def test_aucune_plaque_ni_passage_en_ville_pour_le_sous_sol(banc):
    """Un sous-sol n'a pas de passage : aucune plaque en ville ne le montre, et le GPS n'y vise rien."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const b = L.Blocs.liste().find(function (q) { return q.slug === 'souterrain'; });
        o.frame(5);
        return { liste: !!b, passage: b && b.passage, seuil: b && b.seuil, bloc: !!L.B.bloc,
                 gps: L.Histoire.passageDuBloc('souterrain') };
    }""")
    assert r["liste"] and r["passage"] is None and r["seuil"] == "garage", r
    assert r["bloc"] is False and r["gps"] is None, r
