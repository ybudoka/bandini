"""L'arc D, la dette de Rocco (M16, vague 6, 30 sept. 2026) — d01 à d04 JOUÉES au bouton, sur le modèle de
`test_arc_s_js.py`.

- Sal Ferraro se tient DEDANS, à sa chaise au milieu du terminus (`point:sal`), après m6 seulement.
- d01 : on lui serre la main (l'intro), puis on le mène au garage (`proteger`) ; couché en chemin, c'est raté.
- d02 : Momo le taxi (le fuyard, posé depuis la rue devant le terminus — pas du coin de la ville), la police à semer,
  l'enveloppe rapportée à Sal : la dette baisse de 500.
- d03 : les faux Ciseaux devant l'hôtel, la police, Sal : la dette baisse de 300.
- d04 : la collecte chez Ti-Paul (dehors), Lulu et Ovila (dedans), chacun son mot à la poignée de main, et Sal : la
  dette baisse de 800."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER
from test_arc_q_js import ESCORTE
from test_quatre_missions_js import RATTRAPER

AVANT_D = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6']"

#: Prendre la mission de Sal comme un joueur : entrer au terminus, lui serrer la main, écouter l'intro, ressortir.
CHEZ_SAL = """
  function chezSal(L, o) {
    const piece = dedans(L, o, 'terminus');
    const la = !!L.B.entites.find(function (e) { return e.personnage === 'sal'; });
    if (la) serrer(L, o, 'sal');
    const mission = L.B.partie.mission ? L.B.partie.mission.slug : null;
    const intro = !!(L.B.scene || L.B.cinema);
    passer(L, o); ecouter(L);
    return { piece: piece, la: la, intro: intro, mission: mission };
  }
"""


def test_sal_n_est_au_terminus_qu_apres_m6(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + """
        L.Jeu.commencer(); L.graine(6);
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5']);
        recharger(L);
        dedans(L, o, 'terminus');
        const avant = !!L.B.entites.find(function (e) { return e.personnage === 'sal'; });
        sortir(L, o);
        faites(L, ['m6']);
        recharger(L);
        const piece = dedans(L, o, 'terminus');
        const s = L.B.entites.find(function (e) { return e.personnage === 'sal'; });
        return { avant: avant, piece: piece, apres: !!s, dispo: (L.Histoire.disponibleDe('sal') || {}).slug || null };
    }""")
    assert r["avant"] is False, "pas de Sal au terminus avant m6 (`arrive_apres`)"
    assert r["piece"] == "terminus" and r["apres"] is True and r["dispo"] == "d01", r


def _d01(banc, coucher_sal=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + ESCORTE + CHEZ_SAL + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D + """);
        const j = recharger(L);
        const argent = paiements(L);
        const chez = chezSal(L, o);
        sortir(L, o);
        const c = B.mission && B.mission.protege;
        const t = L.Histoire.lieu('terminus');
        const pose = c ? Math.round(Math.hypot(c.x - t.x, c.y - t.y) / 16) : null;
        const suit = rejoindre(L, o, c);
        if (""" + ("true" if coucher_sal else "false") + """) {
            L.Entites.assommer(c); jouer(L, o, 4);
            return { chez: chez, rate: !p.mission, echecs: p.stats.echecs || 0, fait: !!p.missionsFaites.d01 };
        }
        arriverAvec(L, o, c, 'garage');
        finir(L, o);
        return { chez: chez, personnage: c && c.personnage, pose: pose, suit: suit, dites: dites,
                 fait: !!p.missionsFaites.d01, argent: argent.map(function (a) { return a.montant; }) };
    }""")


def test_d01_sal_te_fait_asseoir_puis_veut_voir_le_garage(banc):
    r = _d01(banc)
    assert r["chez"] == {"piece": "terminus", "la": True, "intro": True, "mission": "d01"}, r["chez"]
    assert r["personnage"] == "sal" and r["suit"] is True and r["pose"] <= 6, r
    assert "pendant:sal:0" in r["dites"], r["dites"]
    assert r["fait"] is True and r["argent"] == [100], r


def test_d01_sal_couche_en_chemin_c_est_rate(banc):
    r = _d01(banc, coucher_sal=True)
    assert r["chez"]["mission"] == "d01"
    assert r["rate"] is True and r["echecs"] == 1 and r["fait"] is False, r


def test_d02_l_enveloppe_de_momo_paie_le_premier_versement(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + RATTRAPER + CHEZ_SAL + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D + """.concat(['d01']));
        const j = recharger(L);
        p.dette = 15000;
        const argent = paiements(L);
        const chez = chezSal(L, o);
        sortir(L, o);
        const f = B.mission.fuyard, t = L.Histoire.lieu('terminus');
        const taxi = { slug: f && f.slug, terminus: f ? Math.round(Math.hypot(f.x - t.x, f.y - t.y) / 16) : null };
        j.x = f.x + 40; j.y = f.y; L.Entites.indexer(); jouer(L, o, 300);
        rattraper(L, o);
        const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        dedans(L, o, 'terminus'); serrer(L, o, 'sal'); finir(L, o);
        return { chez: chez, taxi: taxi, semer: semer, cache: cache, retour: retour, dites: dites, dette: p.dette,
                 fait: !!p.missionsFaites.d02, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"]["mission"] == "d02", r["chez"]
    assert r["taxi"]["slug"] == "taxi" and r["taxi"]["terminus"] <= 40, f"Momo part de devant le terminus : {r['taxi']}"
    assert r["semer"]["etape"] == 1 and r["semer"]["etoiles"] >= 1 and r["cache"]["apres"] == 0, r
    assert r["retour"]["etape"] == 2 and r["retour"]["ligne"].startswith("RAPPORTE L'ENVELOPPE"), r["retour"]
    for dite in ("pendant:sal:0", "pendant:sal:1", "pendant:sal:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [100] and r["dette"] == 14500, r


def test_d03_les_faux_ciseaux_devant_l_hotel(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_SAL + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D + """.concat(['d01', 'd02']));
        const j = recharger(L);
        p.dette = 15000;
        const argent = paiements(L);
        const chez = chezSal(L, o);
        sortir(L, o);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 0; });
        const h = L.Histoire.lieu('hotel');
        const faux = { n: eux.length, chef: eux.some(function (e) { return e.chef; }),
                       hotel: Math.max.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - h.x, e.y - h.y) / 16); })) };
        j.x = h.x; j.y = h.y; L.Entites.indexer();
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        dedans(L, o, 'terminus'); serrer(L, o, 'sal'); finir(L, o);
        return { chez: chez, faux: faux, semer: semer, cache: cache, dites: dites, dette: p.dette,
                 fait: !!p.missionsFaites.d03, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"]["mission"] == "d03", r["chez"]
    assert r["faux"]["n"] >= 3 and r["faux"]["chef"] and r["faux"]["hotel"] <= 12, r["faux"]
    assert r["semer"]["etape"] == 1 and r["semer"]["etoiles"] >= 2 and r["cache"]["apres"] == 0, r
    for dite in ("pendant:sal:0", "pendant:sal:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300] and r["dette"] == 14700, r


def test_d04_la_collecte_chez_ti_paul_lulu_et_ovila(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_SAL + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D + """.concat(['d01', 'd02', 'd03']));
        const j = recharger(L);
        p.dette = 15000;
        const argent = paiements(L);
        const chez = chezSal(L, o);
        sortir(L, o);
        const etapes = [];
        serrer(L, o, 'tipaul'); etapes.push(etape(L));
        dedans(L, o, 'cantine'); serrer(L, o, 'lulu'); sortir(L, o); etapes.push(etape(L));
        dedans(L, o, 'phare'); serrer(L, o, 'ovila'); sortir(L, o); etapes.push(etape(L));
        const ligne = L.Histoire.ligneObjectif();
        dedans(L, o, 'terminus'); serrer(L, o, 'sal'); finir(L, o);
        return { chez: chez, etapes: etapes, ligne: ligne, dites: dites, dette: p.dette,
                 fait: !!p.missionsFaites.d04, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"]["mission"] == "d04", r["chez"]
    assert r["etapes"] == [1, 2, 3] and r["ligne"].startswith("RAPPORTE LA COLLECTE"), r
    for dite in ("accueil:tipaul:0", "accueil:lulu:1", "accueil:ovila:2", "pendant:sal:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [400] and r["dette"] == 14200, r


# --- La fin de l'arc D (vague 8, 30 sept. 2026) : l'avocat, les Ciseaux au garage, puis le CHOIX — le coffre de Sal
# (d07, avec Josée) ou la dernière coupe (d08, la dette payée). Chacune ferme l'autre.

AVANT_D5 = AVANT_D[:-1] + ", 'd01', 'd02', 'd03', 'd04']"

CHEZ_JOSEE = """
  function chezJosee(L, o) {
    const piece = dedans(L, o, 'bar');
    const la = !!L.B.entites.find(function (e) { return e.personnage === 'josee'; });
    if (la) serrer(L, o, 'josee');
    const mission = L.B.partie.mission ? L.B.partie.mission.slug : null;
    passer(L, o); ecouter(L);
    sortir(L, o);
    return { piece: piece, la: la, mission: mission };
  }
"""


def test_d05_l_acte_du_garage_pour_l_avocat_du_brouillard(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_JOSEE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D5 + """);
        const j = recharger(L);
        p.casier = 5;
        const argent = paiements(L);
        const chez = chezJosee(L, o);
        const g = L.Histoire.lieu('garage');
        const acte = B.entites.find(function (e) { return e.objetDeMission === 'papiers_de_rocco'; });
        const pose = acte ? Math.round(Math.hypot(acte.x - g.x, acte.y - g.y) / 16) : null;
        aPied(L); j.x = acte.x; j.y = acte.y; L.Entites.indexer(); jouer(L, o, 4);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const ciseaux = { etape: etape(L), n: eux.length, bagues: eux.every(function (e) { return e.arme === 'poing_americain'; }) };
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const bar = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); finir(L, o);
        return { chez: chez, pose: pose, ciseaux: ciseaux, bar: bar, dites: dites, casier: p.casier,
                 fait: !!p.missionsFaites.d05, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"] == {"piece": "bar", "la": True, "mission": "d05"}, r["chez"]
    assert r["pose"] is not None and r["pose"] <= 3, r
    assert r["ciseaux"] == {"etape": 1, "n": 2, "bagues": True}, r["ciseaux"]
    assert r["bar"]["etape"] == 2 and r["bar"]["ligne"].startswith("LES PAPIERS AU BROUILLARD"), r["bar"]
    for dite in ("pendant:josee:0", "pendant:josee:1", "pendant:josee:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [150] and r["casier"] == 3, r


def test_d06_les_ciseaux_de_sal_au_garage_puis_gus(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D5[:-1] + """, 'd05']);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = (L.Histoire.disponibleDe('gus') || {}).slug || null;
        serrer(L, o, 'gus'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        const g = L.Histoire.lieu('garage');
        j.x = g.x; j.y = g.y; L.Entites.indexer();
        laNuit(L, o); jouer(L, o);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const vague = { etape: etape(L), n: eux.length,
                        garage: Math.max.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - g.x, e.y - g.y) / 16); })) };
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const c = B.mission.entites.find(function (e) { return e.cible && e.etape === 2; });
        const chef = { etape: etape(L), chef: !!(c && c.chef), arme: c && c.arme };
        j.x += 300; L.Entites.indexer();
        L.Entites.assommer(c); jouer(L, o, 10);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        versLui(L, 'gus'); finir(L, o);
        return { dispo: dispo, mission: mission, vague: vague, chef: chef, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.d06, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "d06" and r["mission"] == "d06", r
    assert r["vague"]["etape"] == 1 and r["vague"]["n"] == 3, r["vague"]
    assert r["chef"] == {"etape": 2, "chef": True, "arme": "couteau"}, r["chef"]
    assert r["retour"]["etape"] == 3 and r["retour"]["ligne"].startswith("DIS À GUS"), r["retour"]
    for dite in ("pendant:gus:0", "pendant:gus:1", "pendant:gus:2", "pendant:gus:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [250], r


def test_d07_le_coffre_de_sal_ferme_la_derniere_coupe(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_JOSEE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D5[:-1] + """, 'd05', 'd06']);
        const j = recharger(L);
        p.dette = 0;
        const argent = paiements(L);
        const les_deux = ['d07', 'd08'].map(function (s) { return L.Histoire.disponibles().some(function (m) { return m.slug === s; }); });
        const chez = chezJosee(L, o);
        const t = L.Histoire.lieu('terminus');
        j.x = t.x; j.y = t.y; L.Entites.indexer();
        laNuit(L, o); jouer(L, o);
        const v = B.mission.vehicule;
        const berline = { etape: etape(L), slug: v && v.slug, terminus: v ? Math.round(Math.hypot(v.x - t.x, v.y - t.y) / 16) : null };
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const baie = L.Histoire.lieuDeLivraison('bar');
        v.x = baie.x; v.y = baie.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); jouer(L, o, 10);
        const livre = etape(L);
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); finir(L, o);
        return { les_deux: les_deux, chez: chez, berline: berline, semer: semer, cache: cache, livre: livre, dites: dites,
                 fermees: p.fermees, d08: (L.Histoire.disponibleDe('sal') || {}).slug || null,
                 fait: !!p.missionsFaites.d07, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["les_deux"] == [True, True], "la dette payée, les deux côtés du choix sont offerts"
    assert r["chez"]["mission"] == "d07", r["chez"]
    assert r["berline"]["etape"] == 1 and r["berline"]["slug"] == "luxe" and r["berline"]["terminus"] <= 16, r["berline"]
    assert r["semer"]["etape"] == 2 and r["semer"]["etoiles"] >= 2 and r["cache"]["apres"] == 0, r
    assert r["livre"] == 4, r
    for dite in ("pendant:josee:1", "pendant:josee:2", "pendant:josee:3", "pendant:josee:4"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [2000], r
    assert "d08" in r["fermees"] and r["d08"] is None, "le coffre volé, plus jamais de dernière coupe"


def test_d08_la_derniere_coupe_attend_la_dette_payee(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + ESCORTE + CHEZ_SAL + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D5[:-1] + """, 'd05', 'd06']);
        const j = recharger(L);
        p.dette = 12800;
        const endettee = (L.Histoire.disponibleDe('sal') || {}).slug || null;
        p.dette = 0;
        const argent = paiements(L);
        const chez = chezSal(L, o);
        sortir(L, o);
        const c = B.mission.protege;
        const suit = rejoindre(L, o, c);
        arriverAvec(L, o, c, 'planque');
        const planque = etape(L);
        arriverAvec(L, o, c, 'bar');
        finir(L, o);
        return { endettee: endettee, chez: chez, personnage: c && c.personnage, suit: suit, planque: planque, dites: dites,
                 fermees: p.fermees, fait: !!p.missionsFaites.d08, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["endettee"] is None, "tant que la dette court, pas de dernière coupe"
    assert r["chez"]["mission"] == "d08", r["chez"]
    assert r["personnage"] == "sal" and r["suit"] is True and r["planque"] == 1, r
    for dite in ("pendant:sal:0", "pendant:sal:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and "d07" in r["fermees"], r


def test_d05_mourir_la_fait_rater_meme_sans_echec_au_paquet(banc):
    """Le paquet ne porte plus l'échec par défaut (`missions.PAR_DEFAUT_AU_NAVIGATEUR`) : mort, la mission rate quand
    même (`Histoire.echecsDe`)."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_JOSEE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D5 + """);
        recharger(L);
        const defs = L.Histoire.mission('d05');
        const chez = chezJosee(L, o);
        L.Histoire.evenement('mort'); jouer(L, o, 4);
        return { paquet: defs && defs.echec === undefined, chez: chez.mission, rate: !p.mission, echecs: p.stats.echecs || 0 };
    }""")
    assert r["paquet"] is True and r["chez"] == "d05", r
    assert r["rate"] is True and r["echecs"] == 1, r
