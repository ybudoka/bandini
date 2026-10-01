"""La Pointe après sa paix (M16, vague 20, 1er oct. 2026) — p06, p07, p08, p12 JOUÉES au bouton, de la poignée de
main chez le donneur à la prime.

- p06 (Ovila) : la nuit au phare, le camion des matelots filé jusqu'à la cantine, deux matelots couchés, la caisse
  prise à pied, Josée au Brouillard ; et le camion qui nous voit, c'est raté.
- p07 (M. Bilodeau) : l'autobus du club devant le phare, trois arrêts dans l'ordre, l'hôtel ; sans un choc, la prime ;
  un choc, pas de prime.
- p08 (Zed) : le camion de Lulu, le stationnement du phare, la police à semer, le party.
- p12 (Zed) : la chaloupe de Lulu menée par la baie au quai de La Pointe ; la chaloupe en épave, c'est raté."""

import json

from outils_missions import OUTILS, PLUS_LONGUES, outils
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER
from test_arc_s_js import FILER

from app import missions

VAGUE = ("p06", "p07", "p08", "p12")
#: Tout le catalogue avant la vague (et ses actes remplacés) : le donneur n'a plus qu'elle à donner.
AVANT = json.dumps([m["slug"] for m in missions.CATALOGUE if m["slug"] not in VAGUE + ("m97", "m98", "m99")]
                   + ["p02", "p05", "p04", "p10", "p09", "p11"])

AIDES = OUTILS + outils("images") + PLUS_LONGUES + RECHARGER + DEDANS + FILER + """
  // Une partie où tout est fait sauf la vague (et `plus`), rechargée : les donneurs sont à leur place.
  function partie(L, plus) { faites(L, """ + AVANT + """.concat(plus || [])); return recharger(L); }
  // Serrer la main du donneur DEHORS (devant le phare), écouter l'intro.
  function chezLui(L, o, slug) { const d = L.Histoire.disponibleDe(slug); serrer(L, o, slug); passer(L, o); ecouter(L);
    return { dispo: d && d.slug, mission: L.B.partie.mission ? L.B.partie.mission.slug : null }; }
  function monterDans(L, o, v) { const j = L.B.joueur; aPied(L); j.x = v.x + 12; j.y = v.y; L.Entites.indexer();
    L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o); }
  function poser(L, v, l) { const j = L.B.joueur; v.x = l.x; v.y = l.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); }
  function loin(a, l) { return a && l ? Math.round(Math.hypot(a.x - l.x, a.y - l.y) / 16) : null; }
  function montants(a) { return a.map(function (x) { return x.montant; }); }
"""


def _p06(banc, vu=False):
    return banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L);
        const dispo = (L.Histoire.disponibleDe('ovila') || {}).slug || null;
        const argent = paiements(L);
        dedans(L, o, 'phare'); serrer(L, o, 'ovila');
        const mission = p.mission ? p.mission.slug : null;
        passer(L, o); ecouter(L); sortir(L, o);
        const jour = etape(L);
        laNuit(L, o); jouer(L, o);
        const nuit = etape(L);
        const c = B.mission.suivi;
        const camion = { slug: c && c.slug, phare: loin(c, L.Histoire.lieu('phare')) };
        if (""" + ("true" if vu else "false") + """) {
          // Collé sur son pare-chocs : il nous voit dans son miroir.
          const mien = L.Vehicules.creer('auto', c.x - Math.cos(c.angle) * 30, c.y - Math.sin(c.angle) * 30, c.angle, { etat: 'stationne' });
          monterDans(L, o, mien);
          for (let k = 0; k < 2000 && p.mission; k++) {
            if (!c.attendLeJoueur) { mien.x = c.x - Math.cos(c.angle) * 30; mien.y = c.y - Math.sin(c.angle) * 30; mien.vitesse = 0; j.x = mien.x; j.y = mien.y; }
            o.frame(1); ecouter(L);
          }
          return { dispo: dispo, mission: mission, rate: !p.mission, echecs: p.stats.echecs || 0, fait: !!p.missionsFaites.p06 };
        }
        const duree = filer(L, o, c);
        const file = { etape: etape(L), cantine: loin(c, L.Histoire.lieu('cantine')), images: duree };
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 2; });
        const matelots = { n: eux.length, cantine: eux.length ? loin(eux[0], L.Histoire.lieu('cantine')) : null };
        aPied(L); eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 6);
        const couches = etape(L);
        const caisse = B.entites.find(function (e) { return e.objetDeMission === 'caisse_des_matelots'; });
        const posee = loin(caisse, L.Histoire.lieu('cantine'));
        j.x = caisse.x; j.y = caisse.y; L.Entites.indexer(); jouer(L, o, 4);
        const prise = { etape: etape(L), sac: !!(p.objets && p.objets.caisse_des_matelots) };
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); finir(L, o);
        return { dispo: dispo, mission: mission, jour: jour, nuit: nuit, camion: camion, file: file, matelots: matelots,
                 couches: couches, posee: posee, prise: prise, dites: dites, fait: !!p.missionsFaites.p06, argent: montants(argent) };
    }""")


def test_p06_ovila_les_matelots_files_jusqu_a_la_cantine_puis_josee(banc):
    r = _p06(banc)
    assert r["dispo"] == "p06" and r["mission"] == "p06", r
    assert r["jour"] == 0 and r["nuit"] == 1, "on attend la nuit au phare avant que le camion parte"
    assert r["camion"]["slug"] == "camion" and r["camion"]["phare"] <= 16, r["camion"]
    assert r["file"]["etape"] == 2 and r["file"]["cantine"] < 12, r["file"]
    assert r["matelots"]["n"] == 2 and r["matelots"]["cantine"] <= 8, r["matelots"]
    assert r["couches"] == 3 and r["posee"] is not None and r["posee"] <= 4, r
    assert r["prise"] == {"etape": 4, "sac": True}, r["prise"]
    for dite in ("pendant:ovila:0", "pendant:ovila:1", "pendant:ovila:2", "pendant:ovila:3", "pendant:ovila:4"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300], r


def test_p06_colle_sur_le_camion_il_nous_voit_et_c_est_rate(banc):
    r = _p06(banc, vu=True)
    assert r["mission"] == "p06"
    assert r["rate"] is True and r["echecs"] == 1 and r["fait"] is False, r


def _p07(banc, choc=False):
    return banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L);
        const argent = paiements(L);
        const pris = chezLui(L, o, 'bilodeau');
        const v = B.mission.vehicule;
        const bus = { slug: v && v.slug, phare: loin(v, L.Histoire.lieu('phare')) };
        monterDans(L, o, v);
        const monte = etape(L);
        const pts = B.mission.course ? B.mission.course.points.slice() : [];
        const arrets = [];
        for (const q of pts) {
          // Sur la RUE la plus proche de l'arrêt : l'autobus ne monte pas sur le trottoir (les enseignes sont à six et
          // sept tuiles de la rue — le rayon de l'arrêt est de huit).
          poser(L, v, L.Histoire.tuileDeRue(q.x, q.y, 10) || q); jouer(L, o, 6); arrets.push(B.mission.course ? B.mission.course.i : etape(L));
        }
        const apres = etape(L);
        if (""" + ("true" if choc else "false") + """) { v.chocs = (v.chocs || 0) + 1; v.vie -= 10; }
        poser(L, v, L.Histoire.lieuDeLivraison('hotel'));
        finir(L, o);
        return { pris: pris, bus: bus, monte: monte, n: pts.length, arrets: arrets, apres: apres, dites: dites,
                 fait: !!p.missionsFaites.p07, argent: montants(argent) };
    }""")


def test_p07_l_autobus_du_club_trois_arrets_puis_l_hotel_sans_un_choc(banc):
    r = _p07(banc)
    assert r["pris"] == {"dispo": "p07", "mission": "p07"}, r["pris"]
    assert r["bus"]["slug"] == "autobus" and r["bus"]["phare"] <= 10, r["bus"]
    assert r["monte"] == 1 and r["n"] == 3, r
    assert r["arrets"][:2] == [1, 2] and r["apres"] == 2, f"trois arrêts, dans l'ordre : {r}"
    for dite in ("pendant:bilodeau:0", "pendant:bilodeau:1", "pendant:bilodeau:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [375], f"250 et la moitié de prime, sans un choc : {r['argent']}"


def test_p07_un_choc_coute_la_prime(banc):
    r = _p07(banc, choc=True)
    assert r["fait"] is True and r["argent"] == [250], r["argent"]


def test_p08_le_camion_de_lulu_le_party_et_la_police_a_semer(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L);
        const argent = paiements(L);
        const pris = chezLui(L, o, 'zed');
        const v = B.mission.vehicule;
        const camion = { slug: v && v.slug, cantine: loin(v, L.Histoire.lieu('cantine')) };
        monterDans(L, o, v);
        const monte = etape(L);
        poser(L, v, L.Histoire.lieuDeLivraison('phare')); jouer(L, o, 8);
        const livre = { etape: etape(L), etoiles: B.recherche.etoiles, aPied: !j.dansVehicule };
        const cache = seCacher(L, o);
        const seme = etape(L);
        versLui(L, 'zed'); finir(L, o);
        return { pris: pris, camion: camion, monte: monte, livre: livre, cache: cache, seme: seme, dites: dites,
                 fait: !!p.missionsFaites.p08, argent: montants(argent) };
    }""")
    assert r["pris"] == {"dispo": "p08", "mission": "p08"}, r["pris"]
    assert r["camion"]["slug"] == "camion" and r["camion"]["cantine"] <= 16, r["camion"]
    assert r["monte"] == 1 and r["livre"] == {"etape": 2, "etoiles": 1, "aPied": True}, r
    assert r["cache"]["apres"] == 0 and r["seme"] == 3, r
    for dite in ("pendant:zed:0", "pendant:zed:1", "pendant:zed:2", "pendant:zed:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300], r["argent"]


def _p12(banc, coule=False):
    return banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L, ['p08']);
        const argent = paiements(L);
        const pris = chezLui(L, o, 'zed');
        const v = B.mission.vehicule;
        const a = L.Histoire.resoudre('amarrage:cantine', null);
        const chaloupe = { slug: v && v.slug, amarrage: loin(v, a), eau: v ? L.Monde.estEau(Math.floor(v.x / 16), Math.floor(v.y / 16)) : null };
        monterDans(L, o, v);
        const monte = etape(L);
        if (""" + ("true" if coule else "false") + """) {
          v.etat = 'epave'; v.vie = 0; jouer(L, o, 6);
          return { pris: pris, rate: !p.mission, echecs: p.stats.echecs || 0, fait: !!p.missionsFaites.p12 };
        }
        poser(L, v, L.Histoire.lieuDeLivraison('amarrage:phare')); jouer(L, o, 8);
        const livre = { etape: etape(L), aPied: !j.dansVehicule };
        versLui(L, 'zed'); finir(L, o);
        return { pris: pris, chaloupe: chaloupe, monte: monte, livre: livre, dites: dites,
                 fait: !!p.missionsFaites.p12, argent: montants(argent) };
    }""")


def test_p12_la_chaloupe_de_lulu_au_quai_de_la_pointe(banc):
    r = _p12(banc)
    assert r["pris"] == {"dispo": "p12", "mission": "p12"}, r["pris"]
    assert r["chaloupe"]["slug"] == "bateau" and r["chaloupe"]["amarrage"] <= 4 and r["chaloupe"]["eau"] is True, r
    assert r["monte"] == 1 and r["livre"] == {"etape": 2, "aPied": True}, r
    for dite in ("pendant:zed:0", "pendant:zed:1", "pendant:zed:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [150], r["argent"]


def test_p12_la_chaloupe_en_epave_c_est_rate(banc):
    r = _p12(banc, coule=True)
    assert r["pris"]["mission"] == "p12"
    assert r["rate"] is True and r["echecs"] == 1 and r["fait"] is False, r
