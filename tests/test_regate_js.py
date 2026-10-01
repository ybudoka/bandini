"""Le tour de l'île (M16, vague 17, 1er oct. 2026) : des bouées sur la baie, une course qui les lit en chaloupe, et un
rival qui les court — i07 jouée au bouton, gagnée et perdue."""

import json

from outils_ile_en_char import PILOTE
from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_p_js import RECHARGER

from app import missions

AVANT_I07 = json.dumps([m["slug"] for m in missions.CATALOGUE if m["slug"] not in ("i07", "m97", "m98", "m99")])

COURSE = """
  // Mener la chaloupe au bouton, bouée après bouée, en ligne droite (le parcours est de l'eau libre d'une bouée à la
  // suivante) ; rend le nombre d'images de toute la course.
  function courir(L, o, v) {
    const c = L.B.mission.course;
    let images = 0;
    for (let g = 0; g < 20 && L.B.partie.mission && L.B.mission.course === c && c.i < c.points.length; g++) {
      const p = c.points[c.i];
      images += piloter(L, o, v, [p], 3000, 40, 3.2).images;
      ecouter(L);
    }
    return images;
  }
  function preparer(L, o) {
    const B = L.B, p = B.partie;
    faites(L, """ + AVANT_I07 + """);
    const j = recharger(L);
    p.heure = 10 / 24;
    serrer(L, o, 'leo'); passer(L, o); ecouter(L);
    const v = B.mission.vehicule;
    aPied(L); j.x = v.x; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o, 4);
    return v;
  }
"""


def test_les_bouees_du_tour_se_lisent_et_se_peignent(banc):
    r = banc("function (L, o) {" + """
        L.Jeu.commencer();
        const b = L.B.defs.carte.regate.bouees;
        const p = L.Histoire.resoudre('bouee:3', null);
        const peint = [];
        const ctx = { fillStyle: '', font: '', textAlign: '', fillRect: function (x, y) { peint.push([x, y]); },
                      beginPath: function () {}, arc: function () {}, fill: function () {}, fillText: function () {} };
        L.Regate.dessiner(ctx, { x: b[3][0] * 16 - 200, y: b[3][1] * 16 - 150 });
        return { n: b.length, p: p, b3: b[3], eau: b.map(function (q) { return L.Monde.estEau(q[0], q[1]); }), peint: peint.length };
    }""")
    assert r["n"] == 6 and all(r["eau"]), r
    assert r["p"]["x"] == r["b3"][0] * 16 + 8 and r["p"]["y"] == r["b3"][1] * 16 + 8, r
    assert r["peint"] >= 6 * 5, "six bouées peintes, chacune sa coque, sa bande, son mât, son fanion"


def test_i07_le_tour_de_l_ile_on_bat_leo(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + PILOTE + COURSE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const argent = paiements(L);
        // Au bout du fil ou en personne, réplique par réplique (`telephone`, tranché à la ligne par `present`).
        const fil = {}, suivante = L.Histoire.suivante;
        L.Histoire.suivante = function () {
          const c = L.B.cinema, l = c && c.lignes[c.i];
          if (l && c.partie) fil[c.partie + ':' + l.qui + ':' + (l.objectif === undefined ? '' : l.objectif)] = !!l.telephone;
          return suivante.apply(this, arguments);
        };
        const v = preparer(L, o), j = B.joueur;
        const c = B.mission.course, rival = c && c.rival;
        const depart = { etape: etape(L), points: c ? c.points.length : null, rival: rival && rival.slug,
                         conducteur: rival && rival.conducteur, eauRival: rival ? L.Monde.estEau(Math.floor(rival.x / 16), Math.floor(rival.y / 16)) : null };
        const images = courir(L, o, v);
        const apres = { etape: etape(L), rivalBouee: rival.regate.i, mission: p.mission && p.mission.slug, i: B.mission && B.mission.course ? B.mission.course.i : null };
        if (!p.mission) return { depart: depart, images: images, apres: apres };
        const baie = L.Histoire.lieuDeLivraison('amarrage:hangar_ile');
        v.x = baie.x; v.y = baie.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y; L.Entites.indexer();
        jouer(L, o, 10); finir(L, o);
        return { depart: depart, images: images, apres: apres, dites: dites, fil: fil, fait: !!p.missionsFaites.i07,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["depart"] == {"etape": 1, "points": 7, "rival": "bateau", "conducteur": "regate", "eauRival": True}, r["depart"]
    assert r["apres"]["etape"] == 2 and r["apres"]["rivalBouee"] < 7, f"Léo est arrivé avant : {r}"
    for dite in ("pendant:leo:0", "pendant:leo:1", "pendant:leo:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    # Martin (1er oct. 2026) : « À trois, on part » se disait au téléphone — Léo est à la barre, à côté de toi.
    assert r["fil"].get("pendant:leo:1") is False, f"Léo, dans son bateau à côté, parle au combiné : {r['fil']}"
    assert r["fait"] is True and r["argent"] == [200], r


def test_i07_qui_reste_au_quai_perd_contre_leo(banc):
    """Le rival court pour vrai : immobile au départ, on le voit passer les six bouées — et c'est raté (`battu`)."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + PILOTE + COURSE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const v = preparer(L, o);
        const rival = B.mission.course.rival;
        const echecs = p.stats.echecs || 0;
        let i = 0;
        for (; i < 12000 && p.mission; i++) { o.frame(1); if (L.B.cinema) L.Histoire.suivante(); }
        return { images: i, mission: p.mission && p.mission.slug, echecs: (p.stats.echecs || 0) - echecs,
                 bouees: rival.regate.i, fait: !!p.missionsFaites.i07 };
    }""")
    assert r["mission"] is None and r["fait"] is False and r["echecs"] == 1, r
    assert r["bouees"] == 7 and 30 * 60 < r["images"] < 12000, f"Léo a fait le tour en {r['images']} images : {r}"
