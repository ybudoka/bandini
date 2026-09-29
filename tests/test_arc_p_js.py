"""L'arc P jusqu'à sa libération (M16, 29 sept. 2026) — p02, p04, p05, p09, p10 et p11 JOUÉES au bouton, sur le
modèle de `test_arc_q_js.py`.

- p02 : M. Bilodeau (devant le phare après p01 seulement) ; trois Skateux au pont, leur grand au cône.
- p04 : **la première `course` d'une mission** — quatre points dans l'ordre, à pied (`a_pied` : au volant, rien ne
  compte), sous le chrono de Zed ; trop lent, c'est raté ; `calme: skateux`.
- p05 : la nuit, deux Skateux dans le bois ; la fronde du Trappeur.
- p09 : le phare éteint, trois Skateux à chasser en 90 s, puis Ovila qui rallume, dedans ; la manchette.
- p10 : la moto de Zed, 80 px de vol.
- p11 : Zed mené au Brouillard (`proteger`), les Skateux qui refusent la paix ; et **La Pointe libérée, dans le
  monde** — quatre districts : ce que _Le Boss_ demande."""

import re

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_q_js import ESCORTE

AVANT_P = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'p01']"

#: Recharger la partie : les donneurs qui n'ARRIVENT qu'après une mission (`arrive_apres`) se posent au chargement.
RECHARGER = """
  function recharger(L) { L.Jeu.retourTitre(); L.Jeu.commencer(); L.B.joueur.invincible = 1e6; return L.B.joueur; }
  function versLui(L, slug) { const d = L.Histoire.donneur(slug), j = L.B.joueur; aPied(L); j.x = d.x - 16; j.y = d.y; L.Entites.indexer(); }
"""


def test_p02_le_pont_trois_skateux_leur_grand_au_cone(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        recharger(L);
        const avant = !!L.Histoire.donneur('bilodeau');
        faites(L, ['p01']);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('bilodeau');
        commencer(L, o, 'p02'); jouer(L, o);
        const pont = L.Histoire.resoudre('pont', null);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 0; });
        const pose = { n: eux.length, pont: Math.max.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - pont.x, e.y - pont.y) / 16); })) };
        j.x = pont.x; j.y = pont.y; L.Entites.indexer();
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const g = B.mission.entites.find(function (e) { return e.cible && e.etape === 1; });
        const grand = { etape: etape(L), chef: !!(g && g.chef), arme: g && g.arme };
        L.Entites.assommer(g); jouer(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        versLui(L, 'bilodeau'); finir(L, o);
        return { avant: avant, dispo: dispo && dispo.slug, pose: pose, grand: grand, retour: retour, dites: dites,
                 fait: !!B.partie.missionsFaites.p02, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["avant"] is False, "M. Bilodeau n'est pas devant le phare avant p01"
    assert r["dispo"] == "p02"
    assert r["pose"]["n"] == 3 and r["pose"]["pont"] <= 10, r["pose"]
    assert r["grand"] == {"etape": 1, "chef": True, "arme": "cone"}, r["grand"]
    assert r["retour"]["etape"] == 2 and r["retour"]["ligne"].startswith("RETOURNE VOIR M. BILODEAU"), r["retour"]
    for dite in ("pendant:bilodeau:0", "pendant:bilodeau:1", "pendant:bilodeau:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [150]


def _p04(banc, lent=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_P + """.concat(['p02']));
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('zed');
        commencer(L, o, 'p04'); jouer(L, o);
        const c = B.mission.course;
        const depart = { n: c ? c.points.length : 0, ligne: L.Histoire.ligneObjectif(), gps: L.Histoire.cible() };
        if (""" + ("true" if lent else "false") + """) {
            for (let k = 0; k < 81 * 60 && p.mission; k++) o.frame(1);
            return { rate: !p.mission, fait: !!p.missionsFaites.p04, calmes: p.calmes.slice() };
        }
        // Au volant, un point ne compte pas.
        const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        const rue = L.Histoire.tuileDeRue(c.points[0].x, c.points[0].y, 12);
        const v = L.Vehicules.creer('auto', rue.x, rue.y, CAP[rue.sens], { etat: 'stationne' });
        j.x = v.x + 10; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer();
        v.x = c.points[0].x; v.y = c.points[0].y; j.x = v.x; j.y = v.y; v.vitesse = 0; L.Entites.indexer(); jouer(L, o, 3);
        const auVolant = { i: c.i, ligne: L.Histoire.ligneObjectif() };
        aPied(L);
        const passes = [];
        for (let k = 0; k < c.points.length; k++) {
            const pt = c.points[k];
            j.x = pt.x; j.y = pt.y; L.Entites.indexer(); jouer(L, o, 3);
            passes.push({ i: B.mission && B.mission.course ? B.mission.course.i : null, etape: etape(L) });
        }
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        versLui(L, 'zed'); finir(L, o);
        return { dispo: dispo && dispo.slug, depart: depart, auVolant: auVolant, passes: passes, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.p04, argent: argent.map(function (a) { return a.montant; }), calmes: p.calmes.slice() };
    }""")


def test_p04_la_course_de_zed_quatre_points_a_pied_dans_l_ordre(banc):
    r = _p04(banc)
    assert r["dispo"] == "p04", "Zed (devant le phare après p02) donne p04"
    assert r["depart"]["n"] == 4 and r["depart"]["ligne"].startswith("BATS LE TEMPS DE ZED, À PIED 0/4"), r["depart"]
    assert r["depart"]["gps"], "la flèche vise le premier point"
    assert r["auVolant"]["i"] == 0 and "À PIED" in r["auVolant"]["ligne"], f"au volant, un point ne compte pas : {r['auVolant']}"
    assert [q["i"] for q in r["passes"][:3]] == [1, 2, 3] and r["passes"][3]["etape"] == 1, r["passes"]
    assert r["retour"]["ligne"].startswith("RETOURNE VOIR ZED"), r["retour"]
    for dite in ("pendant:zed:0", "pendant:zed:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [200] and r["calmes"] == ["skateux"], r


def test_p04_trop_lent_c_est_rate(banc):
    r = _p04(banc, lent=True)
    assert r["rate"] is True and r["fait"] is False and r["calmes"] == [], r


def test_p05_la_nuit_dans_le_bois_puis_la_fronde_du_trappeur(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_P + """);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('trappeur');
        commencer(L, o, 'p05'); jouer(L, o);
        const ph = L.Histoire.lieu('phare');
        let hh = p.heure;
        for (let k = 0; k < 400 && L.Monde.estNuit(hh); k++) hh = (hh + 0.005) % 1;
        p.heure = hh; j.x = ph.x; j.y = ph.y + 8; L.Entites.indexer(); jouer(L, o, 20);
        const deJour = etape(L);
        laNuit(L, o); jouer(L, o, 10);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const bois = { etape: etape(L), n: eux.length,
                       phare: Math.min.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - ph.x, e.y - ph.y) / 16); })) };
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o);
        const retour = { etape: etape(L) };
        versLui(L, 'trappeur'); finir(L, o);
        return { dispo: dispo && dispo.slug, deJour: deJour, bois: bois, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.p05, argent: argent.map(function (a) { return a.montant; }), fronde: !!p.armes.fronde };
    }""")
    assert r["dispo"] == "p05" and r["deJour"] == 0, r
    assert r["bois"]["etape"] == 1 and r["bois"]["n"] == 2 and 6 < r["bois"]["phare"] <= 20, f"deux Skateux au bois : {r['bois']}"
    assert r["retour"]["etape"] == 2
    for dite in ("pendant:trappeur:0", "pendant:trappeur:1", "pendant:trappeur:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [120] and r["fronde"] is True, r


def test_p09_le_phare_s_eteint_trois_skateux_puis_ovila_rallume(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_P + """.concat(['p05']));
        const j = recharger(L);
        const argent = paiements(L);
        commencer(L, o, 'p09'); jouer(L, o, 20);
        const ph = L.Histoire.lieu('phare');
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 0; });
        const pose = { n: eux.length, ligne: L.Histoire.ligneObjectif(),
                       phare: Math.max.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - ph.x, e.y - ph.y) / 16); })) };
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o);
        const lampe = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        const piece = dedans(L, o, 'phare');
        const accueil = serrer(L, o, 'ovila');
        finir(L, o);
        return { pose: pose, lampe: lampe, piece: piece, accueil: accueil, dites: dites, fait: !!p.missionsFaites.p09,
                 argent: argent.map(function (a) { return a.montant; }), manchette: p.manchetteForcee || null };
    }""")
    assert r["pose"]["n"] == 3 and r["pose"]["phare"] <= 20, r["pose"]
    assert re.search(r" \d:\d\d$", r["pose"]["ligne"]), f"la ligne montre le chrono : {r['pose']}"
    assert r["lampe"]["etape"] == 1 and r["lampe"]["ligne"].startswith("MONTE RALLUMER"), r["lampe"]
    assert r["piece"] == "phare" and r["accueil"] == "accueil", r
    assert r["fait"] is True and r["argent"] == [300] and r["manchette"] == "phare_a_tenu", r


def test_p10_la_moto_de_zed_quatre_vingts_pixels(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_P + """.concat(['p02', 'p04']));
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('zed');
        commencer(L, o, 'p10'); jouer(L, o);
        const v = B.mission.vehicule || (B.mission.chars && B.mission.chars[0]);
        const ph = L.Histoire.lieu('phare');
        const moto = { slug: v && v.slug, phare: v ? Math.round(Math.hypot(v.x - ph.x, v.y - ph.y) / 16) : null };
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const saut = { etape: etape(L) };
        let k = 0;
        for (; k < 60 && etape(L) === 1; k++) { v.z = 60; v.vx = 3; v.vy = 0; o.frame(1); ecouter(L); }
        saut.images = k; saut.apres = etape(L);
        v.vx = 0; v.vy = 0; v.vitesse = 0; v.z = 0; jouer(L, o);
        versLui(L, 'zed'); finir(L, o);
        return { dispo: dispo && dispo.slug, moto: moto, saut: saut, dites: dites, fait: !!p.missionsFaites.p10,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "p10"
    # « Pas de moto l'hiver » : la machine de Zed est une motoneige quand la saison le veut.
    assert r["moto"]["slug"] in ("moto", "motoneige") and r["moto"]["phare"] <= 8, r["moto"]
    assert r["saut"]["etape"] == 1 and r["saut"]["apres"] == 2 and r["saut"]["images"] >= 20, (
        f"80 px de vol, pas un trottoir : {r['saut']}")
    for dite in ("pendant:zed:1", "pendant:zed:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [250]


def test_p11_zed_mene_a_la_chef_puis_la_pointe_est_libre_quatre_districts(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + ESCORTE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_P + """.concat(['p02', 'p04', 'p05', 'p09', 'p10']));
        const j = recharger(L);
        p.libere = ['faubourg', 'quais', 'erables']; p.faubourgLibere = true;
        const bossAvant = L.Histoire.exigeTenu({ liberes: 4 });
        const argent = paiements(L);
        commencer(L, o, 'p11'); jouer(L, o);
        const c = B.mission.protege;
        const zed = { personnage: c && c.personnage, suit: rejoindre(L, o, c) };
        arriverAvec(L, o, c, 'bar');
        jouer(L, o, 30);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const bar = L.Histoire.lieu('bar');
        const bagarre = { etape: etape(L), n: eux.length, courent: eux.every(function (e) { return e.etat === 'attaque_joueur'; }),
                          loin: Math.max.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - bar.x, e.y - bar.y) / 16); })) };
        eux.forEach(function (e) { L.Entites.assommer(e); });
        finir(L, o);
        const cour = L.Histoire.resoudre('zone:skateux', null);
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), B.defs);
        return { bossAvant: bossAvant, zed: zed, bagarre: bagarre, dites: dites, fait: !!p.missionsFaites.p11,
                 argent: argent.map(function (a) { return a.montant; }), libere: p.libere.slice(), relue: relue.libere,
                 manchette: p.manchetteForcee || null, chasse: L.Entites.gangChasse('skateux'),
                 horsJeu: L.Territoires.horsJeu('skateux'), nom: L.Hud.nomIci(j, L.Monde.zoneA(cour.x, cour.y)),
                 boss: L.Histoire.exigeTenu({ liberes: 4 }) };
    }""")
    assert r["bossAvant"] is False
    assert r["zed"] == {"personnage": "zed", "suit": True}, r["zed"]
    assert r["bagarre"]["etape"] == 1 and r["bagarre"]["n"] == 3 and r["bagarre"]["courent"] and r["bagarre"]["loin"] <= 20, r["bagarre"]
    for dite in ("pendant:zed:0", "pendant:zed:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [500]
    assert r["libere"] == ["faubourg", "quais", "erables", "pointe"] and r["relue"] == r["libere"], r
    assert r["manchette"] == "pointe_liberee" and r["chasse"] and r["horsJeu"], r
    assert r["nom"] == {"nom": "La Pointe", "gang": None}, r["nom"]
    assert r["boss"] is True, "quatre districts libérés : ce que _Le Boss_ demande"
