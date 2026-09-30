"""L'arc H, l'hôpital (M16, vague 7, 30 sept. 2026) — h03 à h07 JOUÉES au bouton, sur le modèle de
`test_arc_d_js.py`.

- h03 : on prend la mission chez Lachance (dedans), on l'escorte au terminus, deux Cravates arrivent, il paie
  Sal (la poignée de main de Sal dite), et il nous attend à la porte du terminus (`retourner`).
- h04 : l'ambulance, la glacière posée devant le terminus (ramassée à pied), l'urgence sous le chrono ; et trop
  lent, c'est raté.
- h05 : le patient file en ambulance (parti de devant l'hôpital), on reprend la trousse, ses deux gars, Ginette.
- h06 : trois comptoirs par leur enseigne, dans l'ordre, Sal, Lachance ; une étoile en chemin, c'est raté.
- h07 : pas avant deux districts libérés ; la nuit, l'ambulance, cinq blessés, trois Cravates, Ginette."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_d_js import CHEZ_SAL
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER
from test_arc_q_js import ESCORTE
from test_quatre_missions_js import RATTRAPER

AVANT_H = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'h01', 'h02', 'd01']

#: Prendre la mission du docteur comme un joueur : entrer à l'hôpital, lui serrer la main, écouter, ressortir.
CHEZ_LACHANCE = """
  function chezLachance(L, o) {
    const piece = dedans(L, o, 'hopital');
    const la = !!L.B.entites.find(function (e) { return e.personnage === 'lachance'; });
    if (la) serrer(L, o, 'lachance');
    const mission = L.B.partie.mission ? L.B.partie.mission.slug : null;
    passer(L, o); ecouter(L);
    sortir(L, o);
    return { piece: piece, la: la, mission: mission };
  }
  function prendre(L, o, slugs) {
    faites(L, slugs);
    const j = recharger(L);
    return j;
  }
"""


def _avant(*plus):
    return str(AVANT_H + list(plus))


def test_h03_le_docteur_paie_sal_et_on_le_ramene(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + ESCORTE + CHEZ_SAL + CHEZ_LACHANCE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = prendre(L, o, """ + _avant() + """);
        const dispo = (L.Histoire.disponibleDe('lachance') || {}).slug || null;
        const argent = paiements(L);
        const chez = chezLachance(L, o);
        const c = B.mission.protege;
        const suit = rejoindre(L, o, c);
        arriverAvec(L, o, c, 'terminus');
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const cravates = { etape: etape(L), n: eux.length };
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const avantSal = etape(L);
        dedans(L, o, 'terminus'); serrer(L, o, 'sal'); sortir(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), toujours: !!(c && c.vivant),
                         porte: c ? Math.round(Math.hypot(c.x - L.Histoire.lieu('terminus').x, c.y - L.Histoire.lieu('terminus').y) / 16) : null };
        versLui(L, 'lachance');
        finir(L, o);
        return { dispo: dispo, chez: chez, personnage: c && c.personnage, suit: suit, cravates: cravates, avantSal: avantSal,
                 retour: retour, dites: dites, fait: !!p.missionsFaites.h03, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "h03", r
    assert r["chez"] == {"piece": "hopital", "la": True, "mission": "h03"}, r["chez"]
    assert r["personnage"] == "lachance" and r["suit"] is True, r
    assert r["cravates"] == {"etape": 1, "n": 2}, r["cravates"]
    assert r["avantSal"] == 2
    # En sortant du terminus on est déjà devant lui : le `retourner` peut tomber dans la même image.
    assert r["retour"]["etape"] in (3, None), r["retour"]
    assert r["retour"]["toujours"] and r["retour"]["porte"] <= 6, f"le docteur attend à la porte du terminus : {r['retour']}"
    for dite in ("pendant:lachance:0", "pendant:lachance:1", "accueil:sal:2", "pendant:lachance:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [250], r


def _h04(banc, lent=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_LACHANCE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = prendre(L, o, """ + _avant("h03") + """);
        const argent = paiements(L);
        const chez = chezLachance(L, o);
        const v = B.mission.vehicule, h = L.Histoire.lieu('hopital');
        const ambulance = { slug: v && v.slug, hopital: v ? Math.round(Math.hypot(v.x - h.x, v.y - h.y) / 16) : null };
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const monte = etape(L);
        // Au terminus en ambulance ; au volant, la glacière ne se ramasse pas.
        const t = L.Histoire.lieu('terminus');
        const place = L.Histoire.tuileDeRue(t.x, t.y, 12) || t;
        v.x = place.x; v.y = place.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); jouer(L, o, 10);
        const glaciere = B.entites.find(function (e) { return e.objetDeMission === 'glaciere_du_coeur'; });
        const posee = glaciere ? Math.round(Math.hypot(glaciere.x - t.x, glaciere.y - t.y) / 16) : null;
        const auVolant = etape(L);
        aPied(L); j.x = glaciere.x; j.y = glaciere.y; L.Entites.indexer(); jouer(L, o, 4);
        const prise = { etape: etape(L), sac: !!(p.objets && p.objets.glaciere_du_coeur) };
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        if (""" + ("true" if lent else "false") + """) {
            for (let k = 0; k < 95 * 60 && p.mission; k++) o.frame(1);
            return { rate: !p.mission, echecs: p.stats.echecs || 0, fait: !!p.missionsFaites.h04 };
        }
        const baie = L.Histoire.lieuDeLivraison('hopital');
        v.x = baie.x; v.y = baie.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer();
        finir(L, o);
        return { chez: chez, ambulance: ambulance, monte: monte, posee: posee, auVolant: auVolant, prise: prise, dites: dites,
                 fait: !!p.missionsFaites.h04, argent: argent.map(function (a) { return a.montant; }) };
    }""")


def test_h04_le_coeur_arrive_par_l_autobus_de_nuit(banc):
    r = _h04(banc)
    assert r["chez"]["mission"] == "h04", r["chez"]
    assert r["ambulance"]["slug"] == "ambulance" and r["ambulance"]["hopital"] <= 12, r["ambulance"]
    assert r["monte"] == 1 and r["posee"] is not None and r["posee"] <= 3, r
    assert r["auVolant"] == 1, "au volant, on ne ramasse pas la glacière"
    assert r["prise"] == {"etape": 2, "sac": True}, r["prise"]
    for dite in ("pendant:lachance:0", "pendant:lachance:1", "pendant:lachance:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [400], r


def test_h04_trop_lent_le_coeur_est_perdu(banc):
    r = _h04(banc, lent=True)
    assert r["rate"] is True and r["echecs"] == 1 and r["fait"] is False, r


def test_h05_le_patient_file_en_ambulance_et_ginette_reprend_sa_trousse(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + RATTRAPER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant("h03", "h04") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = (L.Histoire.disponibleDe('ginette') || {}).slug || null;
        serrer(L, o, 'ginette');
        const mission = p.mission ? p.mission.slug : null;
        passer(L, o); ecouter(L);
        const f = B.mission.fuyard, h = L.Histoire.lieu('hopital');
        const fuyard = { slug: f && f.slug, hopital: f ? Math.round(Math.hypot(f.x - h.x, f.y - h.y) / 16) : null };
        j.x = f.x + 40; j.y = f.y; L.Entites.indexer(); jouer(L, o, 300);
        rattraper(L, o);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const gars = { etape: etape(L), n: eux.length };
        j.x += 300; L.Entites.indexer();
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        versLui(L, 'ginette'); finir(L, o);
        return { dispo: dispo, mission: mission, fuyard: fuyard, gars: gars, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.h05, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "h05" and r["mission"] == "h05", r
    assert r["fuyard"]["slug"] == "ambulance" and r["fuyard"]["hopital"] <= 30, r["fuyard"]
    assert r["gars"] == {"etape": 1, "n": 2}, r["gars"]
    assert r["retour"]["etape"] == 2 and r["retour"]["ligne"].startswith("RAPPORTE LA TROUSSE"), r["retour"]
    for dite in ("pendant:ginette:0", "pendant:ginette:1", "pendant:ginette:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [200], r


def _h06(banc, etoile=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_LACHANCE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = prendre(L, o, """ + _avant("h03", "h04", "h05") + """);
        const argent = paiements(L);
        const chez = chezLachance(L, o);
        const pts = B.mission.course ? B.mission.course.points : [];
        const noms = ['boutique:pharmacie', 'boutique:mission', 'boutique:dentiste'].map(function (s) {
            const l = L.Histoire.resoudre(s, null); return l ? l.nom : null; });
        const etapes = [];
        for (let i = 0; i < pts.length; i++) {
            if (""" + ("true" if etoile else "false") + """ && i === 1) {
                B.recherche.etoiles = 1; jouer(L, o, 4);
                return { chez: chez, rate: !p.mission, echecs: p.stats.echecs || 0, fait: !!p.missionsFaites.h06 };
            }
            j.x = pts[i].x; j.y = pts[i].y; L.Entites.indexer(); jouer(L, o, 6);
            etapes.push(B.mission.course ? B.mission.course.i : null);
        }
        const apres = etape(L);
        dedans(L, o, 'terminus'); serrer(L, o, 'sal'); sortir(L, o);
        const chezSal = etape(L);
        dedans(L, o, 'hopital'); serrer(L, o, 'lachance'); finir(L, o);
        return { chez: chez, n: pts.length, noms: noms, etapes: etapes, apres: apres, chezSal: chezSal, dites: dites,
                 fait: !!p.missionsFaites.h06, argent: argent.map(function (a) { return a.montant; }) };
    }""")


def test_h06_trois_comptoirs_par_leur_enseigne_puis_sal_et_le_docteur(banc):
    r = _h06(banc)
    assert r["chez"]["mission"] == "h06", r["chez"]
    assert r["n"] == 3 and r["noms"] == ["PHARMACIE TANG", "MISSION DU PORT", "DENTISTE"], r
    assert r["etapes"][:2] == [1, 2] and r["apres"] == 1, r
    assert r["chezSal"] == 2, r
    for dite in ("pendant:lachance:0", "accueil:sal:1", "pendant:lachance:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [350], r


def test_h06_une_etoile_en_chemin_c_est_rate(banc):
    r = _h06(banc, etoile=True)
    assert r["chez"]["mission"] == "h06"
    assert r["rate"] is True and r["echecs"] == 1 and r["fait"] is False, r


def test_h07_la_nuit_des_urgences_attend_deux_districts_libres(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_LACHANCE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        let j = prendre(L, o, """ + _avant("h03", "h04", "h05", "h06") + """);
        p.libere = ['faubourg'];
        const fermee = (L.Histoire.disponibleDe('lachance') || {}).slug || null;
        p.libere.push('quais');
        const ouverte = (L.Histoire.disponibleDe('lachance') || {}).slug || null;
        const argent = paiements(L);
        const chez = chezLachance(L, o);
        const h = L.Histoire.lieu('hopital');
        j.x = h.x; j.y = h.y + 20; L.Entites.indexer();
        laNuit(L, o); jouer(L, o);
        const nuit = etape(L);
        const v = B.mission.vehicule;
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const b = L.Missions.boulot;
        const blesses = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        b.faits.ambulance = B.mission.boulotsDepart + 5; jouer(L, o);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 3; });
        const cravates = { etape: etape(L), n: eux.length };
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const cles = etape(L);
        const accueil = serrer(L, o, 'ginette');
        finir(L, o);
        return { fermee: fermee, ouverte: ouverte, chez: chez, nuit: nuit, blesses: blesses, cravates: cravates, cles: cles, accueil: accueil,
                 dites: dites, fait: !!p.missionsFaites.h07, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["fermee"] is None, "un seul district libéré (le Faubourg) : pas encore la nuit des urgences"
    assert r["ouverte"] == "h07", "deux districts libérés : Lachance appelle"
    assert r["chez"]["mission"] == "h07", r["chez"]
    assert r["nuit"] == 1
    assert r["blesses"]["etape"] == 2 and r["blesses"]["ligne"].endswith("0/5"), r["blesses"]
    assert r["cravates"] == {"etape": 3, "n": 3}, r["cravates"]
    assert r["cles"] == 4 and r["accueil"] == "accueil", r
    for dite in ("pendant:lachance:2", "pendant:lachance:3", "accueil:ginette:4"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [500], r
