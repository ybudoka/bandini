"""Quatre missions de plus (25 sept. 2026) — q01, q10, q11, s08 — JOUÉES au bouton, de
l'appel à la prime, sur le modèle de `test_dix_missions_deux_js.py`. Plus le choix que
q10 et q11 portent (`ferme`) : faire l'une ferme l'autre, pour de bon."""

from test_dix_missions_deux_js import OUTILS, PLUS_LONGUES

#: Le fuyard d'un `ramasser` (le patron de `test_cinq_missions_js.py`) : le char casse, le
#: porteur tombe, on ramasse la caisse à pied.
RATTRAPER = """
  function rattraper(L, o) {
    const B = L.B, j = B.joueur, f = B.mission.fuyard;
    if (!f) return null;
    const d = Math.round(Math.hypot(f.x - j.x, f.y - j.y) / 16);
    L.Vehicules.endommager(f, 999, j); jouer(L, o, 2);
    const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
    L.Entites.assommer(porteur); jouer(L, o, 2);
    const caisse = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
    j.x = caisse.x; j.y = caisse.y; L.Entites.indexer(); jouer(L, o);
    return d;
  }
  // Au point du lieu s'il se roule (la cour du lot : la rue fléchée la plus proche est à
  // seize tuiles, mais une auto y entre), sinon à la rue la plus proche.
  function conduireA(L, o, v, lieu) {
    const j = L.B.joueur, l = L.Histoire.lieu(lieu), M = L.Monde;
    const roule = !M.bloque(Math.floor(l.x / 16), Math.floor(l.y / 16), M.MASQUE_VEHICULE);
    const place = roule ? l : (L.Histoire.tuileDeRue(l.x, l.y, 24) || { x: l.x, y: l.y + 32 });
    v.x = place.x; v.y = place.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer();
    jouer(L, o);
  }
"""

AVANT_LES_QUAIS = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01', 'q02', 'q04']"


def test_q01_trois_morues_dehors_la_caisse_du_midi_puis_la_cantine_moins_chere(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RATTRAPER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01', 'q02']);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('lulu');
        commencer(L, o, 'q01'); jouer(L, o);
        const cantine = L.Histoire.lieu('cantine');
        const morues = B.mission.entites.filter(function (e) { return e.cible && e.etape === 0; });
        const coin = L.Histoire.resoudre('zone:morues', null);
        const galerie = { n: morues.length, ligne: L.Histoire.ligneObjectif(),
            coin: Math.max.apply(null, morues.map(function (e) { return Math.round(Math.hypot(e.x - coin.x, e.y - coin.y) / 16); })),
            cantine: Math.min.apply(null, morues.map(function (e) { return Math.round(Math.hypot(e.x - cantine.x, e.y - cantine.y) / 16); })),
            mains: morues.every(function (e) { return !e.arme; }) };
        j.x = morues[0].x + 24; j.y = morues[0].y; L.Entites.indexer();
        morues.forEach(function (e) { L.Entites.assommer(e); });
        jouer(L, o);
        // Il démarre : on le laisse prendre de l'avance, comme au jeu — sinon la caisse
        // tomberait devant la cantine et le retour se ferait dans la même image.
        const f = B.mission.fuyard, depart = f ? { x: f.x, y: f.y } : null;
        jouer(L, o, 300);
        const fuite = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), fuyard: !!f,
                        avance: f ? Math.round(Math.hypot(f.x - depart.x, f.y - depart.y) / 16) : 0 };
        const d = rattraper(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        j.x = cantine.x; j.y = cantine.y; L.Entites.indexer();
        finir(L, o);
        return { dispo: dispo && dispo.slug, galerie: galerie, fuite: fuite, d: d, retour: retour, dites: dites,
                 fait: !!B.partie.missionsFaites.q01, argent: argent.map(function (a) { return a.montant; }),
                 rabais: B.partie.rabais.cantine };
    }""")
    assert r["dispo"] == "q01", "Lulu donne q01 après le poisson du vendredi"
    assert r["galerie"]["n"] == 3 and r["galerie"]["mains"] and r["galerie"]["ligne"].startswith("VA PRÉSENTER"), (
        f"trois Morues, les mains vides : {r['galerie']}")
    # ⚠️ Dans leur coin, LOIN de la cantine : la fin se joue là (voir q01.py).
    assert r["galerie"]["cantine"] > 20, f"les Morues sont posées trop près de la cantine : {r['galerie']}"
    assert r["fuite"]["etape"] == 1 and r["fuite"]["fuyard"] and r["fuite"]["ligne"].startswith("LE QUATRIÈME"), r["fuite"]
    assert r["fuite"]["avance"] > 10, f"le fuyard doit filer avec la caisse : {r['fuite']}"
    assert r["retour"]["etape"] == 2 and r["retour"]["ligne"].startswith("RAPPORTE"), r["retour"]
    for dite in ("pendant:lulu:1", "pendant:lulu:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [150]
    assert r["rabais"] == 0.75, "le rabais de la cantine est promis : il doit être inscrit"


def _q10(banc, bosse=False, lent=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RATTRAPER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, """ + AVANT_LES_QUAIS + """.concat(['m52', 'm53', 'm54']));
        const argent = paiements(L);
        const avant = L.Histoire.disponibles().map(function (m) { return m.slug; });
        commencer(L, o, 'q10'); jouer(L, o);
        const v = B.mission.vehicule, pont = L.Histoire.resoudre('pont', null);
        const moto = { slug: v.slug, pont: Math.round(Math.hypot(v.x - pont.x, v.y - pont.y) / 16) };
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const route = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        if (""" + ("true" if lent else "false") + """) {
            for (let k = 0; k < 61 * 60 && B.partie.mission; k++) o.frame(1);
            return { rate: !B.partie.mission, raison: B.mission ? B.mission.raison : null,
                     fait: !!B.partie.missionsFaites.q10, fermees: B.partie.fermees.slice() };
        }
        if (""" + ("true" if bosse else "false") + """) { v.vie = v.vieMax - 10; }
        conduireA(L, o, v, 'phare');
        const livre = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        aPied(L);
        const sven = L.Histoire.donneur('sven');
        j.x = sven.x - 16; j.y = sven.y; L.Entites.indexer();
        finir(L, o);
        return { avant: avant, moto: moto, route: route, livre: livre, dites: dites,
                 fait: !!B.partie.missionsFaites.q10, argent: argent.map(function (a) { return a.montant; }),
                 fermees: B.partie.fermees.slice(),
                 apres: L.Histoire.disponibles().map(function (m) { return m.slug; }) };
    }""")


def test_q10_la_moto_du_pont_le_phare_puis_sven_et_q11_se_ferme(banc):
    r = _q10(banc)
    assert "q10" in r["avant"] and "q11" in r["avant"], "les deux côtés du choix sont offerts"
    assert r["moto"] == {"slug": "moto", "pont": r["moto"]["pont"]} and r["moto"]["pont"] <= 3, r["moto"]
    assert r["route"]["etape"] == 1 and r["route"]["ligne"].startswith("AU PHARE"), r["route"]
    assert r["livre"]["etape"] == 2 and r["livre"]["ligne"].startswith("REVIENS VOIR SVEN"), r["livre"]
    assert "pendant:sven:1" in r["dites"] and "pendant:sven:2" in r["dites"], r["dites"]
    assert r["fait"] is True and r["argent"] == [900], f"sans une bosse, la moitié de plus : {r['argent']}"
    assert "q11" in r["fermees"] and "q11" not in r["apres"], "Sven choisi : Josée ne rappellera pas pour ses camions"


def test_q10_une_bosse_et_sven_paie_le_prix_convenu(banc):
    r = _q10(banc, bosse=True)
    assert r["fait"] is True and r["argent"] == [600], r["argent"]


def test_q10_une_minute_passee_et_la_moto_n_est_pas_arrivee(banc):
    r = _q10(banc, lent=True)
    assert r["rate"] is True and r["fait"] is False, r
    assert "q11" not in r["fermees"], "une mission ratée ne ferme rien"


def test_q11_deux_camions_le_port_brule_on_seme_puis_le_bar_et_q10_se_ferme(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RATTRAPER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, """ + AVANT_LES_QUAIS + """.concat(['m52', 'm53', 'm54']));
        const argent = paiements(L);
        commencer(L, o, 'q11'); jouer(L, o);
        const cantine = L.Histoire.lieu('cantine'), pont = L.Histoire.resoudre('pont', null);
        const c0 = B.mission.chars[0];
        const premier = { slug: c0.slug, cantine: Math.round(Math.hypot(c0.x - cantine.x, c0.y - cantine.y) / 16), gps: !!L.Histoire.cible() };
        j.x = c0.x + 60; j.y = c0.y; L.Entites.indexer();
        c0.etat = 'epave'; jouer(L, o);
        const c1 = B.mission.chars[1];
        const second = { etape: etape(L), slug: c1 && c1.slug, pont: c1 ? Math.round(Math.hypot(c1.x - pont.x, c1.y - pont.y) / 16) : null };
        j.x = c1.x + 60; j.y = c1.y; L.Entites.indexer();
        c1.etat = 'epave'; jouer(L, o);
        const semer = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        const bar = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        const b = L.Histoire.lieu('bar');
        j.x = b.x; j.y = b.y; L.Entites.indexer();
        finir(L, o);
        return { premier: premier, second: second, semer: semer, cache: cache, bar: bar, dites: dites,
                 fait: !!B.partie.missionsFaites.q11, argent: argent.map(function (a) { return a.montant; }),
                 fermees: B.partie.fermees.slice(),
                 apres: L.Histoire.disponibles().map(function (m) { return m.slug; }) };
    }""")
    assert r["premier"]["slug"] == "camion" and r["premier"]["cantine"] <= 16 and r["premier"]["gps"], r["premier"]
    assert r["second"]["etape"] == 1 and r["second"]["slug"] == "camion" and r["second"]["pont"] <= 3, r["second"]
    assert r["semer"]["etape"] == 2 and r["semer"]["etoiles"] >= 3, r["semer"]
    assert r["cache"]["dedans"] and r["cache"]["apres"] == 0, r["cache"]
    assert r["bar"]["etape"] == 3 and r["bar"]["ligne"].startswith("VIENS AU BAR"), r["bar"]
    for dite in ("pendant:josee:1", "pendant:josee:2", "pendant:josee:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [700]
    assert "q10" in r["fermees"] and "q10" not in r["apres"], "Josée choisie : Sven ne rappellera pas"


def test_s08_la_nuit_au_lot_trois_boulonneux_l_auto_volee_puis_sa_case(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RATTRAPER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 's01']);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('gilles');
        commencer(L, o, 's08');
        const f = L.Histoire.lieu('fourriere');
        j.x = f.x; j.y = f.y + 20; L.Entites.indexer();
        let hh = B.partie.heure;
        for (let k = 0; k < 400 && L.Monde.estNuit(hh); k++) hh = (hh + 0.005) % 1;
        B.partie.heure = hh; jouer(L, o);
        const deJour = etape(L);
        laNuit(L, o); jouer(L, o);
        const gars = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const bagarre = { etape: etape(L), n: gars.length,
                          courent: gars.every(function (e) { return e.etat === 'attaque_joueur'; }) };
        gars.forEach(function (e) { L.Entites.assommer(e); });
        jouer(L, o);
        const v = B.mission.vehicule;
        const volee = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), slug: v && v.slug,
                        loin: v ? Math.round(Math.hypot(v.x - f.x, v.y - f.y) / 16) : null };
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const route = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        conduireA(L, o, v, 'fourriere');
        finir(L, o);
        return { dispo: dispo && dispo.slug, deJour: deJour, bagarre: bagarre, volee: volee, route: route, dites: dites,
                 fait: !!B.partie.missionsFaites.s08, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "s08", "Gilles donne s08 après sa remorqueuse"
    assert r["deJour"] == 0, "de jour, on attend la nuit"
    assert r["bagarre"]["etape"] == 1 and r["bagarre"]["n"] == 3 and r["bagarre"]["courent"], r["bagarre"]
    assert r["volee"]["etape"] == 2 and r["volee"]["slug"] == "auto" and r["volee"]["loin"] > 20, r["volee"]
    assert r["route"]["etape"] == 3 and r["route"]["ligne"].startswith("RAMÈNE"), r["route"]
    for dite in ("pendant:gilles:1", "pendant:gilles:2", "pendant:gilles:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [200]
