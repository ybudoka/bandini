"""La suite des districts (M16, vague 12, 30 sept. 2026) — ce qui restait des arcs S, E et Q, JOUÉ au bouton.

- s07 : Prévost (dedans, à l'usine), le camion de pièces derrière l'usine, au quai en 150 s.
- s12 : Gilles, sa remorqueuse, cinq remorquages, et elle finit garée à la planque.
- s14 : Ti-Loup, trois autos-patrouilles devant le poste — trois fois voler, semer, livrer au lot.
- e13 : Diane, sa berline reprise au lot, semée, garée devant le dépanneur.
- q12 : Josée, l'ambulance, sa mère au dépanneur, l'urgence en deux minutes.
- q09 : Gégé, le camion de la cantine, trois points dans l'ordre, et le chrono."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER
from test_quatre_missions_js import RATTRAPER

BASE = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']

AIDES = """
  function monterDans(L, o, v) {
    const j = L.B.joueur;
    j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
  }
  function semerEtRemonter(L, o, v) {
    const B = L.B;
    const avant = { etape: etape(L), etoiles: B.recherche.etoiles };
    const cache = seCacher(L, o);
    monterDans(L, o, v);
    return { avant: avant, apres: cache.apres };
  }
"""


def _faites(*plus):
    return str(BASE + list(plus))


def test_s07_le_camion_de_prevost_au_quai(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + RATTRAPER + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("e01", "q02", "s01", "s02", "s03", "s05", "s06", "s09", "s10", "s11") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const piece = dedans(L, o, 'usine');
        serrer(L, o, 'prevost'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        sortir(L, o);
        const v = B.mission.vehicule;
        monterDans(L, o, v);
        const quai = { etape: etape(L), slug: v.slug, ligne: L.Histoire.ligneObjectif() };
        conduireA(L, o, v, 'cantine');
        finir(L, o);
        return { piece: piece, mission: mission, quai: quai, dites: dites, fait: !!p.missionsFaites.s07,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    # s07 est l'acte 1 des _Commandes de Prévost_ (2 oct. 2026) : tout se décale d'un (le marqueur).
    assert r["piece"] == "usine" and r["mission"] == "commandes_de_prevost", r
    assert r["quai"]["etape"] == 2 and r["quai"]["slug"] == "camion", r["quai"]
    for dite in ("pendant:prevost:1", "pendant:prevost:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [350], r


def test_s12_cinq_remorquages_et_la_remorqueuse_a_la_planque(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("s01", "s08") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = (L.Histoire.disponibleDe('gilles') || {}).slug || null;
        serrer(L, o, 'gilles'); passer(L, o); ecouter(L);
        const v = B.mission.vehicule;
        monterDans(L, o, v);
        const b = L.Missions.boulot;
        const boulots = { etape: etape(L), slug: v.slug, ligne: L.Histoire.ligneObjectif() };
        b.faits.remorquage = B.mission.boulotsDepart + 5; jouer(L, o);
        const retour = etape(L);
        L.Vehicules.descendre(j, true); versLui(L, 'gilles'); finir(L, o);
        return { dispo: dispo, boulots: boulots, retour: retour, dites: dites, planque: p.vehiculePlanque,
                 fait: !!p.missionsFaites.s12, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "s12", r
    assert r["boulots"]["etape"] == 1 and r["boulots"]["slug"] == "remorqueuse" and r["boulots"]["ligne"].endswith("0/5"), r
    assert r["retour"] == 2, r
    for dite in ("pendant:gilles:0", "pendant:gilles:1", "pendant:gilles:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [150], r
    assert r["planque"] and r["planque"]["slug"] == "remorqueuse", "la remorqueuse de Gilles, garée à la planque"


def test_s14_trois_autos_patrouilles_au_compacteur(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + RATTRAPER + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("s01", "s02", "s05") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = (L.Histoire.disponibleDe('tiloup') || {}).slug || null;
        serrer(L, o, 'tiloup'); passer(L, o); ecouter(L);
        const po = L.Histoire.lieu('poste');
        j.x = po.x; j.y = po.y; L.Entites.indexer();
        laNuit(L, o); jouer(L, o);
        const tours = [];
        for (let k = 0; k < 3 && p.mission; k++) {
            const v = B.mission.vehicule;
            const debut = etape(L);
            monterDans(L, o, v);
            const s = semerEtRemonter(L, o, v);
            conduireA(L, o, v, 'fourriere');
            tours.push({ debut: debut, slug: v.slug, semer: s.avant.etape, etoiles: s.avant.etoiles, apres: s.apres,
                         fin: etape(L) });
        }
        finir(L, o);
        return { dispo: dispo, tours: tours, dites: dites, fait: !!p.missionsFaites.s14,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "s14", r
    assert [t["debut"] for t in r["tours"]] == [1, 4, 7], r["tours"]
    for t in r["tours"]:
        assert t["slug"] == "police" and t["etoiles"] >= 1 and t["apres"] == 0, t
    for dite in ("pendant:tiloup:0", "pendant:tiloup:3", "pendant:tiloup:6", "pendant:tiloup:9"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [450], r


def test_e13_la_berline_de_diane_reprise_au_lot(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + RATTRAPER + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("e01", "e04", "e06", "e07", "e10") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = (L.Histoire.disponibleDe('diane') || {}).slug || null;
        serrer(L, o, 'diane'); passer(L, o); ecouter(L);
        const v = B.mission.vehicule, f = L.Histoire.lieu('fourriere');
        const berline = { slug: v.slug, lot: Math.round(Math.hypot(v.x - f.x, v.y - f.y) / 16) };
        monterDans(L, o, v);
        const s = semerEtRemonter(L, o, v);
        conduireA(L, o, v, 'depanneur');
        finir(L, o);
        return { dispo: dispo, berline: berline, semer: s, dites: dites, fait: !!p.missionsFaites.e13,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    # e13 est l'acte 1 de _Diane et Jo_ (2 oct. 2026) : tout se décale d'un (le marqueur).
    assert r["dispo"] == "diane_et_jo", r
    assert r["berline"]["slug"] == "luxe" and r["berline"]["lot"] <= 16, r["berline"]
    assert r["semer"]["avant"]["etape"] == 2 and r["semer"]["apres"] == 0, r["semer"]
    for dite in ("pendant:diane:1", "pendant:diane:2", "pendant:diane:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300], r


def _q12(banc, lent=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + RATTRAPER + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("e01", "q02", "q04", "q05", "q06", "q11", "q13", "v01") + """);
        const j = recharger(L);
        const argent = paiements(L);
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        sortir(L, o);
        const v = B.mission.vehicule;
        monterDans(L, o, v);
        const d = L.Histoire.lieu('depanneur');
        const place = L.Histoire.tuileDeRue(d.x, d.y, 12) || d;
        v.x = place.x; v.y = place.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); jouer(L, o, 10);
        const mere = etape(L);
        if (""" + ("true" if lent else "false") + """) {
            for (let k = 0; k < 125 * 60 && p.mission; k++) o.frame(1);
            return { mission: mission, rate: !p.mission, echecs: p.stats.echecs || 0, fait: !!p.missionsFaites.q12 };
        }
        const baie = L.Histoire.lieuDeLivraison('hopital');
        v.x = baie.x; v.y = baie.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer();
        finir(L, o);
        return { mission: mission, slug: v.slug, mere: mere, dites: dites, fait: !!p.missionsFaites.q12,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")


def test_q12_la_mere_de_josee_a_l_urgence(banc):
    r = _q12(banc)
    # q12 est l'acte 3 de _Cindy et le Beau Denis_ (2 oct. 2026, marqueur 8).
    assert r["mission"] == "cindy_et_le_beau_denis" and r["slug"] == "ambulance" and r["mere"] == 11, r
    for dite in ("pendant:josee:8", "pendant:josee:9", "pendant:josee:10", "pendant:josee:11"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300], r


def test_q12_trop_lent_c_est_rate(banc):
    r = _q12(banc, lent=True)
    assert r["mission"] == "cindy_et_le_beau_denis"
    assert r["rate"] is True and r["echecs"] == 1 and r["fait"] is False, r


def test_q09_trois_points_autour_des_quais_en_camion(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("q03") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = (L.Histoire.disponibleDe('gege') || {}).slug || null;
        serrer(L, o, 'gege'); passer(L, o); ecouter(L);
        const v = B.mission.vehicule;
        monterDans(L, o, v);
        const pts = B.mission.course ? B.mission.course.points : [];
        const passes = [];
        for (let i = 0; i < pts.length; i++) {
            v.x = pts[i].x; v.y = pts[i].y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); jouer(L, o, 4);
            passes.push(B.mission && B.mission.course ? B.mission.course.i : null);
        }
        L.Vehicules.descendre(j, true); versLui(L, 'gege'); finir(L, o);
        return { dispo: dispo, slug: v.slug, n: pts.length, passes: passes, dites: dites, fait: !!p.missionsFaites.q09,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    # q09 est l'acte 2 de _Gégé et les débardeurs_ (2 oct. 2026, marqueur 5).
    assert r["dispo"] == "gege_et_les_debardeurs", r
    assert r["slug"] == "camion" and r["n"] == 3 and r["passes"][:2] == [1, 2], r
    for dite in ("pendant:gege:5", "pendant:gege:6", "pendant:gege:7", "pendant:gege:8"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300], r
