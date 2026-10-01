"""Les Érables et La Shop, la suite (M16, vague 21, 1er oct. 2026) — e08, e09, e11, s04, s13 JOUÉES au bouton, de la
poignée de main chez le donneur à la prime.

- e08 (Diane) : son coupé, deux paquets de Jo à La Pointe (à pied, sous le chrono), un char des Skateux qui colle ; et
  trop lent, c'est raté.
- e09 (Ti-Paul) : le camion, trois poutines chaudes aux enseignes des Érables ; et froides, c'est raté.
- e11 (le maire) : la question dans sa chambre — vendu (la planque, puis lui : 1 000 $), ou à Louise (la planque, le
  kiosque, ses gardes : 300 $).
- s04 (Raymonde) : la paie à la caisse pop, trois Cravates et leurs renforts, leur chef au couteau, Raymonde.
- s13 (Prévost) : le prototype chez les Skateux, la rampe, un char des Chevreuils, la fourrière sans une égratignure."""

import json

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER

from app import missions

VAGUE = ("e08", "e09", "e11", "s04", "s13")
AVANT = json.dumps([m["slug"] for m in missions.CATALOGUE if m["slug"] not in VAGUE + ("m97", "m98", "m99")]
                   + ["p02", "p05", "p04", "p10", "p09", "p11"])

AIDES = OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + """
  function partie(L, plus) { faites(L, """ + AVANT + """.concat(plus || [])); return recharger(L); }
  function chezLui(L, o, slug) { const d = L.Histoire.disponibleDe(slug); serrer(L, o, slug); passer(L, o); ecouter(L);
    return { dispo: d && d.slug, mission: L.B.partie.mission ? L.B.partie.mission.slug : null }; }
  function monterDans(L, o, v) { const j = L.B.joueur; aPied(L); j.x = v.x + 12; j.y = v.y; L.Entites.indexer();
    L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o); }
  function poser(L, v, l) { const j = L.B.joueur; v.x = l.x; v.y = l.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); }
  function rue(L, l) { return L.Histoire.tuileDeRue(l.x, l.y, 10) || l; }
  // La tuile où un char roule la plus proche d'un point (une rue, un stationnement, un trottoir) — pas un mur.
  function roulable(L, l) {
    const M = L.Monde, tx = Math.floor(l.x / 16), ty = Math.floor(l.y / 16);
    for (let r = 0; r < 12; r++) for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
      if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
      if (!M.bloque(tx + dx, ty + dy, M.MASQUE_VEHICULE) && !M.estEau(tx + dx, ty + dy)) return { x: (tx + dx) * 16 + 8, y: (ty + dy) * 16 + 8 };
    }
    return l;
  }
  function loin(a, l) { return a && l ? Math.round(Math.hypot(a.x - l.x, a.y - l.y) / 16) : null; }
  function montants(a) { return a.map(function (x) { return x.montant; }); }
  // Ramasser à pied l'objet de mission `objet` : on descend, on marche dessus.
  function ramasser(L, o, objet) {
    const e = L.B.entites.find(function (q) { return q.objetDeMission === objet; });
    if (!e) return null;
    const j = L.B.joueur; aPied(L); j.x = e.x; j.y = e.y; L.Entites.indexer(); jouer(L, o, 4);
    return { x: e.x, y: e.y };
  }
"""


def _e08(banc, lent=False):
    return banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L);
        const argent = paiements(L);
        const pris = chezLui(L, o, 'diane');
        const v = B.mission.vehicule;
        const coupe = { slug: v && v.slug, depanneur: loin(v, L.Histoire.lieu('depanneur')) };
        monterDans(L, o, v);
        const monte = etape(L);
        if (""" + ("true" if lent else "false") + """) {
          for (let k = 0; k < 205 * 60 && p.mission; k++) o.frame(1);
          return { pris: pris, rate: !p.mission, echecs: p.stats.echecs || 0, fait: !!p.missionsFaites.e08 };
        }
        const sk = L.Histoire.resoudre('rampe:pointe', null);
        poser(L, v, rue(L, sk)); jouer(L, o, 4);
        const un = ramasser(L, o, 'paquet_de_jo');
        const premier = { etape: etape(L), skateux: loin(un, sk) };
        const deux = ramasser(L, o, 'autre_paquet_de_jo');
        const second = { etape: etape(L), rampe: loin(deux, L.Histoire.lieu('phare')) };
        jouer(L, o, 30);
        const colle = B.entites.filter(function (e) { return e.type === 'vehicule' && e.poursuivant; }).length;
        versLui(L, 'diane'); finir(L, o);
        return { pris: pris, coupe: coupe, monte: monte, premier: premier, second: second, colle: colle, dites: dites,
                 fait: !!p.missionsFaites.e08, argent: montants(argent) };
    }""")


def test_e08_les_deux_paquets_de_jo_a_la_pointe_et_diane(banc):
    r = _e08(banc)
    assert r["pris"] == {"dispo": "e08", "mission": "e08"}, r["pris"]
    assert r["coupe"]["slug"] == "sport" and r["coupe"]["depanneur"] <= 12, r["coupe"]
    assert r["monte"] == 1 and r["premier"]["etape"] == 2 and r["premier"]["skateux"] <= 12, r
    assert r["second"]["etape"] == 3 and r["second"]["rampe"] <= 6, r["second"]
    for dite in ("pendant:diane:0", "pendant:diane:1", "pendant:diane:2", "pendant:diane:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [250], r


def test_e08_trop_lent_les_skateux_les_trouvent(banc):
    r = _e08(banc, lent=True)
    assert r["pris"]["mission"] == "e08"
    assert r["rate"] is True and r["echecs"] == 1 and r["fait"] is False, r


def _e09(banc, lent=False):
    return banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L);
        const argent = paiements(L);
        const pris = chezLui(L, o, 'tipaul');
        const v = B.mission.vehicule;
        const camion = { slug: v && v.slug, depanneur: loin(v, L.Histoire.lieu('depanneur')) };
        monterDans(L, o, v);
        const monte = etape(L);
        if (""" + ("true" if lent else "false") + """) {
          for (let k = 0; k < 125 * 60 && p.mission; k++) o.frame(1);
          return { pris: pris, rate: !p.mission, echecs: p.stats.echecs || 0, fait: !!p.missionsFaites.e09 };
        }
        const pts = B.mission.course ? B.mission.course.points.slice() : [];
        const arrets = [];
        const ecarts = [];
        for (const q of pts) { const t = roulable(L, q); ecarts.push(loin(t, q)); poser(L, v, t); jouer(L, o, 6); arrets.push(B.mission.course ? B.mission.course.i : etape(L)); }
        const apres = etape(L);
        versLui(L, 'tipaul'); finir(L, o);
        return { pris: pris, camion: camion, monte: monte, n: pts.length, arrets: arrets, apres: apres, dites: dites, ecarts: ecarts,
                 fait: !!p.missionsFaites.e09, argent: montants(argent) };
    }""")


def test_e09_trois_poutines_chaudes_aux_enseignes_des_erables(banc):
    r = _e09(banc)
    assert r["pris"] == {"dispo": "e09", "mission": "e09"}, r["pris"]
    assert r["camion"]["slug"] == "camion" and r["camion"]["depanneur"] <= 16, r["camion"]
    assert r["monte"] == 1 and r["n"] == 3 and r["arrets"][:2] == [1, 2] and r["apres"] == 2, r
    for dite in ("pendant:tipaul:0", "pendant:tipaul:1", "pendant:tipaul:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [150], r


def test_e09_des_poutines_froides_c_est_rate(banc):
    r = _e09(banc, lent=True)
    assert r["pris"]["mission"] == "e09"
    assert r["rate"] is True and r["echecs"] == 1 and r["fait"] is False, r


def _e11(banc, garder):
    return banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L, ['m97']);
        const argent = paiements(L);
        const dispo = (L.Histoire.disponibleDe('maire') || {}).slug || null;
        dedans(L, o, 'hotel'); L.Jeu.changerEtage('hotel_chambre'); o.fondu();
        for (let q = 0; q < 200 && !(B.interieur && B.interieur.slug === 'hotel_chambre'); q++) o.frame(1);
        serrer(L, o, 'maire');
        const mission = p.mission ? p.mission.slug : null;
        passer(L, o); ecouter(L);
        // La question, à la poignée de main qui suit l'intro (`accueil`, le patron de d09).
        serrer(L, o, 'maire');
        for (let k = 0; k < 3000 && !(B.menu && B.menu.choix); k++) { o.frame(1); if (B.cinema && !B.cinema.question && k % 30 === 0) L.Histoire.suivante(); }
        const question = { menu: !!(B.menu && B.menu.choix), reponses: B.menu ? B.menu.items.map(function (i) { return i.libelle; }) : null };
        o.frame(20);
        if (""" + ("true" if garder else "false") + """) o.tape('ArrowDown', 2);
        o.tape('KeyE', 2); o.frame(2);
        const branche = p.mission && p.mission.branche;
        passer(L, o); ecouter(L);
        L.Jeu.sortir(); o.fondu(); for (let q = 0; q < 300 && B.interieur; q++) o.frame(1);
        L.Jeu.sortir(); o.fondu(); for (let q = 0; q < 300 && B.interieur; q++) o.frame(1);
        jouer(L, o);
        const pl = L.Histoire.lieu('planque');
        j.x = pl.x; j.y = pl.y + 8; L.Entites.indexer(); jouer(L, o, 6);
        const planque = etape(L);
        let suite = {};
        if (""" + ("true" if garder else "false") + """) {
          versLui(L, 'louise'); serrer(L, o, 'louise'); jouer(L, o, 10);
          const gardes = B.mission.entites.filter(function (e) { return e.cible && e.vivant; });
          suite = { louise: etape(L), gardes: gardes.length, arch: gardes.map(function (e) { return e.arch; }) };
          gardes.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
          suite.couches = etape(L);
        }
        // D'un bord comme de l'autre, la fin se dit dans sa chambre : il paie, ou il encaisse.
        dedans(L, o, 'hotel'); L.Jeu.changerEtage('hotel_chambre'); o.fondu();
        for (let q = 0; q < 200 && !(B.interieur && B.interieur.slug === 'hotel_chambre'); q++) o.frame(1);
        suite.chambre = { etape: etape(L), piece: B.interieur && B.interieur.slug };
        serrer(L, o, 'maire'); finir(L, o);
        return { dispo: dispo, mission: mission, question: question, branche: branche, planque: planque, suite: suite,
                 dites: dites, fait: !!p.missionsFaites.e11, choix: p.choix && p.choix.e11, argent: montants(argent) };
    }""")


def test_e11_le_dossier_vendu_au_maire_mille_piastres(banc):
    r = _e11(banc, garder=False)
    assert r["dispo"] == "e11" and r["mission"] == "e11", r
    assert r["question"]["menu"] is True and len(r["question"]["reponses"]) == 2, r["question"]
    assert r["branche"] == "vendre" and r["planque"] == 5, f"la branche « vendre » saute Louise et les gardes : {r}"
    assert r["suite"]["chambre"] == {"etape": 5, "piece": "hotel_chambre"}, r["suite"]
    assert "pendant:maire:5" in r["dites"] and "pendant:louise:2" not in r["dites"], r["dites"]
    assert r["fait"] is True and r["choix"] == "vendre" and r["argent"] == [1000], r


def test_e11_le_dossier_garde_pour_louise_et_les_gardes_du_maire(banc):
    r = _e11(banc, garder=True)
    assert r["branche"] == "garder" and r["planque"] == 2, r
    assert r["suite"]["louise"] == 3 and r["suite"]["gardes"] == 2 and set(r["suite"]["arch"]) == {"garde"}, r["suite"]
    assert r["suite"]["couches"] == 4 and r["suite"]["chambre"]["etape"] == 4, r["suite"]
    assert "pendant:louise:2" in r["dites"] and "pendant:louise:4" in r["dites"] and "pendant:maire:5" not in r["dites"], r["dites"]
    assert r["fait"] is True and r["choix"] == "garder" and r["argent"] == [300], r


def test_s04_la_paie_du_quart_trois_cravates_leurs_renforts_et_leur_chef(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L);
        const argent = paiements(L);
        const pris = chezLui(L, o, 'raymonde');
        const c = L.Histoire.lieu('caisse_pop');
        j.x = c.x; j.y = c.y + 8; L.Entites.indexer(); jouer(L, o, 6);
        const caisse = etape(L);
        let vagues = 0, couches = 0;
        for (let k = 0; k < 8 && etape(L) === 1; k++) {
          for (let q = 0; q < 60; q++) { o.frame(1); ecouter(L); }
          const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1 && e.vivant && e.etat !== 'assomme'; });
          if (eux.length) vagues++;
          eux.forEach(function (e) { L.Entites.assommer(e); couches++; }); jouer(L, o, 6);
        }
        const apresVagues = etape(L);
        for (let q = 0; q < 60; q++) { o.frame(1); ecouter(L); }
        const chef = B.mission.entites.find(function (e) { return e.cible && e.etape === 2; });
        const leChef = { arme: chef && chef.arme, vie: chef && chef.vie };
        if (chef) L.Entites.assommer(chef); jouer(L, o, 6);
        const apresChef = etape(L);
        versLui(L, 'raymonde'); finir(L, o);
        return { pris: pris, caisse: caisse, vagues: vagues, couches: couches, apresVagues: apresVagues, chef: leChef,
                 apresChef: apresChef, dites: dites, fait: !!p.missionsFaites.s04, argent: montants(argent) };
    }""")
    assert r["pris"] == {"dispo": "s04", "mission": "s04"}, r["pris"]
    assert r["caisse"] == 1 and r["apresVagues"] == 2, r
    assert r["couches"] >= 3 + 4 and r["vagues"] >= 2, f"trois Cravates, puis deux vagues de deux : {r}"
    assert r["chef"]["arme"] == "couteau" and r["apresChef"] == 3, r
    for dite in ("pendant:raymonde:0", "pendant:raymonde:1", "pendant:raymonde:2", "pendant:raymonde:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300], r


def _s13(banc, bosse=False):
    return banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partie(L);
        const argent = paiements(L);
        const dispo = (L.Histoire.disponibleDe('prevost') || {}).slug || null;
        dedans(L, o, 'usine'); serrer(L, o, 'prevost');
        const mission = p.mission ? p.mission.slug : null;
        passer(L, o); ecouter(L); sortir(L, o);
        const v = B.mission.vehicule;
        const proto = { slug: v && v.slug, skateux: loin(v, L.Histoire.resoudre('zone:skateux', null)) };
        monterDans(L, o, v);
        const monte = etape(L);
        // Le saut : le char en l'air, comme le Grand Saut (`v.z` haut, sinon la gravité le pose avant la lecture).
        v.z = 60; v.vz = 2; v.vx = 3; v.vy = 0; v.vitesse = 3;
        for (let k = 0; k < 40 && etape(L) === 1; k++) { if (v.z <= 0) v.z = 60; o.frame(1); ecouter(L); }
        const saute = etape(L);
        jouer(L, o, 30);
        const colle = B.entites.filter(function (e) { return e.type === 'vehicule' && e.poursuivant; }).length;
        if (""" + ("true" if bosse else "false") + """) { v.chocs = (v.chocs || 0) + 1; v.vie -= 10; }
        else { v.vie = v.vieMax; }
        poser(L, v, L.Histoire.lieuDeLivraison('fourriere'));
        finir(L, o);
        return { dispo: dispo, mission: mission, proto: proto, monte: monte, saute: saute, colle: colle, dites: dites,
                 fait: !!p.missionsFaites.s13, argent: montants(argent) };
    }""")


def test_s13_le_prototype_la_rampe_et_la_fourriere_sans_une_egratignure(banc):
    r = _s13(banc)
    assert r["dispo"] == "s13" and r["mission"] == "s13", r
    assert r["proto"]["slug"] == "sport" and r["proto"]["skateux"] <= 14, r["proto"]
    assert r["monte"] == 1 and r["saute"] == 2, r
    for dite in ("pendant:prevost:0", "pendant:prevost:1", "pendant:prevost:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [600], r["argent"]


def test_s13_une_egratignure_coute_la_prime(banc):
    r = _s13(banc, bosse=True)
    assert r["fait"] is True and r["argent"] == [400], r["argent"]
