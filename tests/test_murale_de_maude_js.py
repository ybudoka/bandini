"""La murale de Maude (M16, la toute fin, 1er oct. 2026) — p03 JOUÉE au bouton, de la poignée de main à la prime.

- Maude, devant le phare après m6 : sa moto (sa motoneige l'hiver) ; trois bombes de peinture qui attendent devant
  l'atelier de peinture de La Shop (`boutique:peinture`), qu'on ramasse à pied ; dès qu'on les a, elle étend son
  apprêt : deux minutes pour les lui rapporter, à moto ; elle paie.
- Trop lent : l'apprêt sèche, et elle le dit."""

import json

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_p_js import RECHARGER

from app import missions

AVANT = json.dumps([m["slug"] for m in missions.CATALOGUE if m["slug"] not in ("p03", "m97", "m98", "m99")]
                   + ["p02", "p05", "p04", "p10", "p09", "p11"])

AIDES = OUTILS + PLUS_LONGUES + RECHARGER + """
  function partie(L) { faites(L, """ + AVANT + """); return recharger(L); }
  function monterDans(L, o, v) { const j = L.B.joueur; aPied(L); j.x = v.x + 12; j.y = v.y; L.Entites.indexer();
    L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o); }
  function poser(L, v, l) { const j = L.B.joueur; v.x = l.x; v.y = l.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); }
  function roulable(L, l) {
    const M = L.Monde, tx = Math.floor(l.x / 16), ty = Math.floor(l.y / 16);
    for (let r = 0; r < 14; r++) for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
      if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
      if (!M.bloque(tx + dx, ty + dy, M.MASQUE_VEHICULE) && !M.estEau(tx + dx, ty + dy)) return { x: (tx + dx) * 16 + 8, y: (ty + dy) * 16 + 8 };
    }
    return l;
  }
  function tuiles(a, b) { return a && b ? Math.round(Math.hypot(a.x - b.x, a.y - b.y) / 16) : null; }
  // Jusqu'aux bombes : la moto devant l'atelier, on descend, on marche dessus.
  function lesBombes(L, o, v) {
    const B = L.B, j = B.joueur;
    const atelier = L.Histoire.resoudre('boutique:peinture', null);
    poser(L, v, roulable(L, atelier)); jouer(L, o, 4);
    const b = B.entites.find(function (e) { return e.objetDeMission === 'bombes_de_maude'; });
    const pose = { posee: !!b, dessin: b && b.objet, atelier: tuiles(b, atelier), district: b ? L.Monde.zoneA(b.x, b.y).district : null };
    aPied(L); j.x = b.x; j.y = b.y; L.Entites.indexer(); jouer(L, o, 4);
    pose.etape = etape(L); pose.sac = (B.partie.objets || {}).bombes_de_maude || 0;
    return pose;
  }
"""


def test_p03_trois_bombes_rapportees_a_maude_avant_que_l_appret_seche(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('maude');
        serrer(L, o, 'maude'); passer(L, o); ecouter(L);
        const pris = p.mission && p.mission.slug;
        const v = B.mission.vehicule, phare = L.Histoire.lieu('phare');
        const bolide = { slug: v && v.slug, phare: tuiles(v, phare) };
        monterDans(L, o, v);
        const monte = etape(L);
        const bombes = lesBombes(L, o, v);
        // Le chrono court au RETOUR : la ligne affiche le temps qui reste.
        const ligne = L.Histoire.ligneObjectif();
        monterDans(L, o, v);
        poser(L, v, roulable(L, phare)); jouer(L, o, 10);
        L.Vehicules.descendre(j, true);
        finir(L, o);
        return { dispo: dispo && dispo.slug, pris: pris, bolide: bolide, monte: monte, bombes: bombes, ligne: ligne, dites: dites,
                 fait: !!p.missionsFaites.p03, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "p03" and r["pris"] == "p03", r
    assert r["bolide"]["slug"] in ("moto", "motoneige") and r["bolide"]["phare"] <= 12, r["bolide"]
    b = r["bombes"]
    assert r["monte"] == 1 and b["posee"] and b["dessin"] == "bombes" and b["atelier"] <= 8 and b["district"] == "shop", b
    assert b["etape"] == 2 and b["sac"] == 1, b
    assert ":" in r["ligne"], f"le chrono du retour s'affiche : {r['ligne']}"
    for dite in ("pendant:maude:0", "pendant:maude:1", "pendant:maude:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [150], r


def test_p03_trop_lent_l_appret_seche(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        partie(L);
        const textes = [];
        const DIALOGUE = L.Hud.dialogue;
        L.Hud.dialogue = function (qui, lignes) { textes.push(lignes.join(' ')); return DIALOGUE.apply(null, arguments); };
        serrer(L, o, 'maude'); passer(L, o); ecouter(L);
        const v = B.mission.vehicule;
        monterDans(L, o, v);
        lesBombes(L, o, v);
        // On traîne devant l'atelier : deux minutes, et un peu.
        let n = 0;
        for (; n < 9000 && p.mission; n++) { o.frame(1); if (B.cinema) L.Histoire.suivante(); }
        passer(L, o);
        return { n: n, rate: textes.some(function (t) { return t.indexOf('apprêt a séché') >= 0; }), fait: !!p.missionsFaites.p03, mission: p.mission };
    }""")
    assert r["mission"] is None and r["fait"] is False, r
    assert 120 * 60 - 200 <= r["n"] <= 120 * 60 + 200, f"deux minutes au retour : {r}"
    assert r["rate"] is True, f"raté, elle le dit : {r}"
