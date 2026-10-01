"""Un char dans la piscine (M16, la toute fin, 1er oct. 2026) — `static/js/piscine.js`, e05 et e14 JOUÉES au bouton.

- e05 (Diane) : la remorqueuse de Gilles au lot ; l'auto est PRISE dans la piscine de Diane (sous l'eau, sans ombre,
  elle ne roule pas, on n'y monte pas) ; au treuil — klaxon, la haie entre les deux — elle remonte, dégoulinante,
  sur la fourche ; accrochée, on l'amène au lot ; Diane paie.
- e14 (Diane) : la berline du maire derrière l'hôtel, conduite au bord de sa piscine ; au volant rien ne se passe ;
  on descend, elle roule dedans et y reste ; la photo de Louise, la manchette, la prime.
- Ce que le module ne touche pas : un char ordinaire au bord d'une piscine n'y tombe pas."""

import json

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER

from app import missions

AVANT = json.dumps([m["slug"] for m in missions.CATALOGUE if m["slug"] not in ("e05", "e14", "m97", "m98", "m99")]
                   + ["p02", "p05", "p04", "p10", "p09", "p11"])

AIDES = OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + """
  function partie(L, moins) { faites(L, """ + AVANT + """.filter(function (s) { return (moins || []).indexOf(s) < 0; })); return recharger(L); }
  function chezElle(L, o) { serrer(L, o, 'diane'); passer(L, o); ecouter(L); return L.B.partie.mission ? L.B.partie.mission.slug : null; }
  function monterDans(L, o, v) { const j = L.B.joueur; aPied(L); j.x = v.x + 12; j.y = v.y; L.Entites.indexer();
    L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o); }
  function poser(L, v, l, angle) { const j = L.B.joueur; v.x = l.x; v.y = l.y; v.vitesse = 0; v.vx = 0; v.vy = 0;
    if (angle !== undefined) v.angle = angle; j.x = v.x; j.y = v.y; L.Entites.indexer(); }
  // La tuile où un char roule la plus proche d'un point — pas un mur, pas l'eau, pas la piscine.
  function roulable(L, l) {
    const M = L.Monde, tx = Math.floor(l.x / 16), ty = Math.floor(l.y / 16);
    for (let r = 0; r < 14; r++) for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
      if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
      if (!M.bloque(tx + dx, ty + dy, M.MASQUE_VEHICULE) && !M.estEau(tx + dx, ty + dy)) return { x: (tx + dx) * 16 + 8, y: (ty + dy) * 16 + 8 };
    }
    return l;
  }
  function tuiles(a, b) { return a && b ? Math.round(Math.hypot(a.x - b.x, a.y - b.y) / 16) : null; }
  function glypheSous(L, v) { return L.Monde.glyphe(Math.floor(v.x / 16), Math.floor(v.y / 16)); }
"""


def test_e05_l_auto_sort_de_la_piscine_au_treuil_et_va_au_lot(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L);
        const argent = paiements(L);
        const pris = chezElle(L, o);
        const rem = B.mission.vehicule;
        const lot = L.Histoire.lieu('fourriere');
        const aLot = { slug: rem && rem.slug, lot: tuiles(rem, lot) };
        monterDans(L, o, rem);
        jouer(L, o, 4);
        const c = B.mission.chars[1], pi = L.Histoire.resoudre('piscine:depanneur', null);
        const prise = { slug: c && c.slug, dedans: L.Piscine.dedans(c), glyphe: glypheSous(L, c), piscine: tuiles(c, pi),
                        depanneur: tuiles(c, L.Histoire.lieu('depanneur')), ligne: L.Histoire.ligneObjectif() };
        // Elle ne bouge pas, et on n'y monte pas.
        const x0 = c.x; jouer(L, o, 30);
        aPied(L); j.x = c.x + 10; j.y = c.y; L.Entites.indexer();
        const monte = L.Vehicules.monter(j, c);
        const figee = { bouge: Math.abs(c.x - x0) > 0.5, monte: monte, msg: B.msg };
        // La remorqueuse au bord : la rue la plus proche de la piscine, à portée du treuil.
        monterDans(L, o, rem);
        poser(L, rem, roulable(L, pi));
        jouer(L, o, 2);
        const bord = { treuil: Math.round(Math.hypot(rem.x - c.x, rem.y - c.y)), ligne: L.Histoire.ligneObjectif() };
        o.tape('Space', 2); jouer(L, o, 4);
        const treuil = { accroche: rem.remorque === c, dedans: !!c.piscine, degoutte: c.degoutte > 0, etape: etape(L),
                         derriere: Math.round(Math.hypot(rem.x - c.x, rem.y - c.y)) };
        // Accrochée, au lot.
        poser(L, rem, roulable(L, lot)); c.x = rem.x - 30; c.y = rem.y; jouer(L, o, 10);
        const livre = { etape: etape(L), decroche: !rem.remorque, auLot: tuiles(c, lot) };
        L.Vehicules.descendre(j, true); versLui(L, 'diane'); finir(L, o);
        return { pris: pris, aLot: aLot, prise: prise, figee: figee, bord: bord, treuil: treuil, livre: livre, dites: dites,
                 fait: !!p.missionsFaites.e05, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["pris"] == "e05", r
    assert r["aLot"]["slug"] == "remorqueuse" and r["aLot"]["lot"] <= 12, r["aLot"]
    pr = r["prise"]
    assert pr["slug"] == "auto" and pr["dedans"] is True and pr["glyphe"] == "?" and pr["piscine"] == 0, pr
    assert pr["depanneur"] <= 70 and "TREUIL" in pr["ligne"], pr
    assert r["figee"]["bouge"] is False and r["figee"]["monte"] is False and "PISCINE" in r["figee"]["msg"], r["figee"]
    assert r["bord"]["treuil"] <= 7 * 16, f"la rue la plus proche est à portée du treuil : {r['bord']}"
    t = r["treuil"]
    assert t["accroche"] and not t["dedans"] and t["degoutte"] and t["etape"] == 1 and t["derriere"] < 50, t
    assert r["livre"]["etape"] == 2 and r["livre"]["decroche"] and r["livre"]["auLot"] <= 8, r["livre"]
    for dite in ("pendant:diane:0", "pendant:diane:1", "pendant:diane:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [200], r


def test_e14_la_berline_du_maire_roule_dans_sa_piscine(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L);
        p.missionsFaites.e05 = 1;
        const argent = paiements(L);
        const pris = chezElle(L, o);
        const v = B.mission.vehicule;
        const hotel = { slug: v && v.slug, hotel: tuiles(v, L.Histoire.lieu('hotel')) };
        monterDans(L, o, v);
        jouer(L, o, 4);
        const pi = L.Histoire.resoudre('piscine:bloc:villa', null);
        const autre = L.Histoire.resoudre('piscine:depanneur', null);
        // Au volant, au bord : rien ne se passe — la ligne dit de descendre.
        poser(L, v, roulable(L, pi));
        jouer(L, o, 20);
        const auVolant = { piscine: !!v.piscine, ligne: L.Histoire.ligneObjectif(), bord: tuiles(v, pi) };
        // On descend : elle roule dedans, et y reste.
        L.Vehicules.descendre(j, true); j.x = v.x + 30; j.y = v.y; L.Entites.indexer();
        jouer(L, o, 3);
        const tombe = { piscine: !!v.piscine, dedans: L.Piscine.dedans(v) };
        jouer(L, o, 60);
        const auFond = { dedans: L.Piscine.dedans(v), glyphe: glypheSous(L, v), etape: etape(L), ombre: L.Vehicules.ombreDe(v) ? true : false };
        jouer(L, o, 120);
        const reste = { glyphe: glypheSous(L, v), dedans: L.Piscine.dedans(v) };
        versLui(L, 'diane'); finir(L, o);
        return { pris: pris, hotel: hotel, deux: Math.round(Math.hypot(pi.x - autre.x, pi.y - autre.y) / 16), auVolant: auVolant,
                 tombe: tombe, dedans: auFond, reste: reste, dites: dites, fait: !!p.missionsFaites.e14,
                 manchette: p.manchetteForcee || null,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["pris"] == "e14", r
    assert r["hotel"]["slug"] == "luxe" and r["hotel"]["hotel"] <= 16, r["hotel"]
    assert r["deux"] > 5, f"la piscine du maire n'est pas celle de Diane : {r}"
    assert r["auVolant"]["piscine"] is False and "DESCENDS" in r["auVolant"]["ligne"], r["auVolant"]
    assert r["tombe"] == {"piscine": True, "dedans": False}, f"elle tombe, elle n'y est pas d'un coup : {r['tombe']}"
    assert r["dedans"]["dedans"] and r["dedans"]["glyphe"] == "?" and r["dedans"]["etape"] == 2, r["dedans"]
    assert r["reste"] == {"glyphe": "?", "dedans": True}, f"elle reste prise : {r['reste']}"
    assert "pendant:diane:1" in r["dites"] and "pendant:diane:2" in r["dites"], r["dites"]
    assert r["fait"] is True and r["argent"] == [300], r
    assert r["manchette"] == "maire_a_la_piscine", f"Louise a sa photo : la une du lendemain — {r['manchette']}"


def test_un_char_ordinaire_ne_tombe_pas_dans_une_piscine(banc):
    """Le module ne touche qu'à ce qu'il pose (`v.piscine`) : un char garé au bord d'une piscine, sans mission, n'y
    roule pas. (La baie, elle, noie comme avant : `test_naufrage_js` — `piscine.js` ne lit pas l'eau.)"""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B;
        const pi = L.Piscine.piscines()[0];
        const v = L.Vehicules.creer('auto', 0, 0, 0, { etat: 'stationne', couleur: '#777777' });
        const l = roulable(L, pi); v.x = l.x; v.y = l.y; L.Entites.indexer();
        for (let k = 0; k < 120; k++) o.frame(1);
        const bord = { piscine: !!v.piscine, glyphe: glypheSous(L, v) };
        return { n: L.Piscine.piscines().length, bord: bord };
    }""")
    assert r["n"] >= 2, r
    assert r["bord"]["piscine"] is False and r["bord"]["glyphe"] != "?", r
