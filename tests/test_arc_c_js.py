"""L'arc C, le Clairon (M16, vague 9, 30 sept. 2026) — l01 à l06 JOUÉES au bouton, sur le modèle de
`test_arc_h_js.py`. ⚠️ Les slugs `c01`–`c08` sont pris (Irène, le vieux maître) : l'arc de Louise s'écrit `l`.

- l01 : Louise nous suit au poste, ses agents à semer, puis la lumière du soir au port — la fin devant elle.
- l02 : devant le poste, trois étoiles à semer en 90 s ; trop lent, c'est raté ; la manchette du lendemain.
- l03 : la nuit à l'hôtel, Norbert escorté au kiosque (il parle en chemin), deux hommes, Louise.
- l04 : le dossier du maire à la rédaction — une façade peinte (`boutique:clairon`) —, ses hommes, Louise.
- l05 : le feu de la rédaction à l'extincteur que Louise met dans les mains, les incendiaires, Louise.
- l06 : fermée avant trois districts libérés ; Louise au phare, et la une du lendemain."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER
from test_arc_q_js import ESCORTE

AVANT_C = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']

CHEZ_LOUISE = """
  function chezLouise(L, o) {
    const la = !!L.Histoire.donneur('louise');
    if (la) serrer(L, o, 'louise');
    const mission = L.B.partie.mission ? L.B.partie.mission.slug : null;
    passer(L, o); ecouter(L);
    return { la: la, mission: mission };
  }
"""


def _avant(*plus):
    return str(AVANT_C + list(plus))


def test_l01_une_photo_de_bouchard_puis_le_port(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + ESCORTE + DEDANS + CHEZ_LOUISE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant() + """);
        const j = recharger(L);
        const argent = paiements(L);
        const chez = chezLouise(L, o);
        const c = B.mission.protege;
        const suit = rejoindre(L, o, c);
        arriverAvec(L, o, c, 'poste');
        const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        const port = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        arriverAvec(L, o, c, 'cantine');
        finir(L, o);
        return { chez: chez, personnage: c && c.personnage, suit: suit, semer: semer, cache: cache, port: port,
                 dites: dites, fait: !!p.missionsFaites.l01, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"] == {"la": True, "mission": "l01"}, r["chez"]
    assert r["personnage"] == "louise" and r["suit"] is True, r
    assert r["semer"]["etape"] == 1 and r["semer"]["etoiles"] >= 1 and r["cache"]["apres"] == 0, r
    assert r["port"]["etape"] == 2 and r["port"]["ligne"].startswith("LA LUMIÈRE DU SOIR"), r["port"]
    for dite in ("pendant:louise:0", "pendant:louise:1", "pendant:louise:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [150], r



def test_l01_louise_dans_l_auto_ne_se_fait_pas_renverser(banc):
    """⚠️ LE PASSAGER N'EST PAS RENVERSÉ PAR SON CHAR (Martin, 30 sept. 2026) : dès que Louise montait, ça cognait
    sans arrêt, avec du bruit, et la police montait à cinq étoiles, même après la peinture. Assise, elle est
    collée au centre du char à chaque image, et `heurterPietons` ne sautait que le JOUEUR assis : lancé, le char
    la « renversait » à chaque image — `blesser` refusait le coup, mais le coup sourd, la secousse, le char freiné
    et le crime `renversement` passaient."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + ESCORTE + CHEZ_LOUISE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B;
        faites(L, """ + _avant() + """);
        const j = recharger(L);
        chezLouise(L, o);
        const c = B.mission.protege;
        const suit = rejoindre(L, o, c);
        const a = L.Histoire.tuileDeRue(j.x, j.y, 10);
        const v = L.Vehicules.creer('auto', a.x, a.y, 0, { etat: 'stationne' });
        j.x = v.x + 10; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v);
        c.x = v.x + 14; c.y = v.y + 14; c.piste = []; L.Entites.indexer();
        for (let k = 0; k < 30 && c.dansVehicule !== v; k++) { v.vitesse = 0; o.frame(1); ecouter(L); }
        const monte = c.dansVehicule === v;
        // Seul le passager au bord : aucun autre passant à renverser.
        B.entites.filter(function (e) { return e.type === 'pieton' && e !== c; }).forEach(function (e) { L.Entites.retirer(e); });
        B.recherche.etoiles = 0;
        let crimes = 0, coups = 0, vmax = 0;
        const signaler = L.Police.signalerCrime, blesser = L.Entites.blesser;
        // ⚠️ Le renversement seul : lancé à fond, le banc conduit aussi dangereusement (`conduite_dangereuse`).
        L.Police.signalerCrime = function (t) { if (/^renversement/.test(t)) crimes++; return signaler.apply(this, arguments); };
        L.Entites.blesser = function (e) { if (e === c) coups++; return blesser.apply(this, arguments); };
        o.touche('KeyW');
        for (let k = 0; k < 180; k++) { v.vie = v.vieMax; o.frame(1); ecouter(L); vmax = Math.max(vmax, Math.hypot(v.vx, v.vy)); }
        o.relacher('KeyW');
        L.Police.signalerCrime = signaler; L.Entites.blesser = blesser;
        return { suit: suit, monte: monte, vmax: vmax, coups: coups, crimes: crimes, etoiles: B.recherche.etoiles,
                 toujours: c.dansVehicule === v, vivant: c.vivant };
    }""")
    assert r["suit"] and r["monte"], r
    assert r["vmax"] > 1.2, f"le char roule plus vite que le seuil de renverse : {r}"
    assert r["coups"] == 0 and r["crimes"] == 0 and r["etoiles"] == 0, f"le char a cogné sa passagère : {r}"
    assert r["toujours"] and r["vivant"], r

def _l02(banc, lent=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + CHEZ_LOUISE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant("l01") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const chez = chezLouise(L, o);
        const po = L.Histoire.lieu('poste');
        j.x = po.x; j.y = po.y; L.Entites.indexer(); jouer(L, o, 10);
        const vu = { etape: etape(L), etoiles: B.recherche.etoiles };
        if (""" + ("true" if lent else "false") + """) {
            L.Police.maj = function () {};
            for (let k = 0; k < 95 * 60 && p.mission; k++) { B.recherche.etoiles = 3; o.frame(1); }
            return { chez: chez, rate: !p.mission, echecs: p.stats.echecs || 0, fait: !!p.missionsFaites.l02 };
        }
        B.recherche.etoiles = 0; jouer(L, o, 10);
        const seme = etape(L);
        versLui(L, 'louise'); finir(L, o);
        return { chez: chez, vu: vu, seme: seme, dites: dites, manchette: p.manchetteForcee,
                 fait: !!p.missionsFaites.l02, argent: argent.map(function (a) { return a.montant; }) };
    }""")


def test_l02_trois_etoiles_semees_font_la_une(banc):
    r = _l02(banc)
    assert r["chez"]["mission"] == "l02", r["chez"]
    assert r["vu"] == {"etape": 1, "etoiles": 3}, r["vu"]
    assert r["seme"] == 2, r
    for dite in ("pendant:louise:0", "pendant:louise:1", "pendant:louise:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [200] and r["manchette"] == "insaisissable", r


def test_l02_trop_lent_c_est_rate(banc):
    r = _l02(banc, lent=True)
    assert r["chez"]["mission"] == "l02"
    assert r["rate"] is True and r["echecs"] == 1 and r["fait"] is False, r


def test_l03_norbert_escorte_de_nuit_jusqu_au_kiosque(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + ESCORTE + CHEZ_LOUISE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant("l01", "l02", "m50", "f01", "f03", "f10") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const chez = chezLouise(L, o);
        const h = L.Histoire.lieu('hotel');
        j.x = h.x; j.y = h.y + 16; L.Entites.indexer();
        laNuit(L, o); jouer(L, o);
        const c = B.mission.protege;
        const escorte = { etape: etape(L), personnage: c && c.personnage };
        const suit = rejoindre(L, o, c);
        arriverAvec(L, o, c, 'kiosque');
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 2; });
        const hommes = { etape: etape(L), n: eux.length };
        j.x += 300; L.Entites.indexer();
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const retour = etape(L);
        versLui(L, 'louise'); finir(L, o);
        return { chez: chez, escorte: escorte, suit: suit, hommes: hommes, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.l03, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"]["mission"] == "l03", r["chez"]
    assert r["escorte"] == {"etape": 1, "personnage": "norbert"} and r["suit"] is True, r
    assert r["hommes"] == {"etape": 2, "n": 2}, r["hommes"]
    assert r["retour"] == 3, r
    for dite in ("pendant:norbert:1", "pendant:norbert:2", "pendant:louise:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300], r


def test_l04_le_dossier_du_maire_a_la_redaction(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + CHEZ_LOUISE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant("l01", "l02", "l03", "m50", "f01", "f03", "f10", "e01", "e06", "e07") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const chez = chezLouise(L, o);
        const pt = B.mission.course ? B.mission.course.points[0] : null;
        const redaction = L.Histoire.resoudre('boutique:clairon', null);
        j.x = pt.x; j.y = pt.y; L.Entites.indexer(); jouer(L, o, 10);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const hommes = { etape: etape(L), n: eux.length, arch: eux.map(function (e) { return e.arch; }) };
        j.x += 300; L.Entites.indexer();
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const retour = etape(L);
        versLui(L, 'louise'); finir(L, o);
        return { chez: chez, nom: redaction && redaction.nom, hommes: hommes, retour: retour, dites: dites,
                 manchette: p.manchetteForcee, fait: !!p.missionsFaites.l04,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"]["mission"] == "l04", r["chez"]
    assert r["nom"] == "LE CLAIRON", r
    assert r["hommes"]["etape"] == 1 and r["hommes"]["n"] == 3 and set(r["hommes"]["arch"]) == {"gardien"}, r["hommes"]
    assert r["retour"] == 2, r
    for dite in ("pendant:louise:0", "pendant:louise:1", "pendant:louise:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [800] and r["manchette"] == "maire_hotel", r


def test_l05_le_clairon_brule_et_l_extincteur_de_louise(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + CHEZ_LOUISE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant("l01", "l02", "l03", "l04", "m50", "f01", "f03", "f10", "e01", "e06", "e07") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const chez = chezLouise(L, o);
        const feu = B.mission.feu, redaction = L.Histoire.resoudre('boutique:clairon', null);
        const ou = feu ? L.Incendies.position(feu) : null;
        const brule = { feu: !!feu, arme: j.arme, pres: ou && redaction ? Math.round(Math.hypot(ou.x - redaction.x, ou.y - redaction.y) / 16) : null };
        // Le jet tenu au bouton, face au feu (le patron de test_eteindre_js).
        aPied(L); o.touche('KeyJ');
        for (let k = 0; k < 400 && etape(L) === 0; k++) { j.x = ou.x; j.y = ou.y + 18; j.angle = -Math.PI / 2; o.frame(1); ecouter(L); }
        o.relacher('KeyJ'); o.frame(1);
        const eteint = etape(L);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        j.x += 300; L.Entites.indexer();
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const retour = etape(L);
        versLui(L, 'louise'); finir(L, o);
        return { chez: chez, brule: brule, eteint: eteint, n: eux.length, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.l05, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"]["mission"] == "l05", r["chez"]
    assert r["brule"]["feu"] and r["brule"]["arme"] == "extincteur" and r["brule"]["pres"] <= 8, r["brule"]
    assert r["eteint"] == 1 and r["n"] == 3 and r["retour"] == 2, r
    for dite in ("pendant:louise:0", "pendant:louise:1", "pendant:louise:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [400], r


def test_l06_l_entrevue_attend_trois_districts_puis_le_phare(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + ESCORTE + CHEZ_LOUISE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant("l01", "l02", "l03", "l04", "l05", "m50", "f01", "f03", "f10", "e01", "e06", "e07") + """);
        let j = recharger(L);
        p.libere = ['faubourg', 'quais'];
        const fermee = (L.Histoire.disponibleDe('louise') || {}).slug || null;
        p.libere.push('erables');
        const argent = paiements(L);
        const chez = chezLouise(L, o);
        const c = B.mission.protege;
        const suit = rejoindre(L, o, c);
        arriverAvec(L, o, c, 'phare');
        finir(L, o);
        return { fermee: fermee, chez: chez, personnage: c && c.personnage, suit: suit, dites: dites,
                 manchette: p.manchetteForcee, fait: !!p.missionsFaites.l06,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["fermee"] is None, "deux districts libérés : pas encore d'entrevue"
    assert r["chez"]["mission"] == "l06", r["chez"]
    assert r["personnage"] == "louise" and r["suit"] is True, r
    assert "pendant:louise:0" in r["dites"], r["dites"]
    assert r["fait"] is True and r["argent"] == [100] and r["manchette"] == "le_neveu_parle", r
