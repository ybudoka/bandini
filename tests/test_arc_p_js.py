"""L'arc P : La Pointe, un CHAPITRE de six actes (30 sept. 2026, docs/jalons/des-missions-en-chapitres.md) — joué au
bouton, acte par acte, sur le modèle de `test_arc_q_js.py`.

Chaque juge commence le chapitre là où une vieille partie le reprendrait : les missions des actes d'avant sont faites
(`faites`), et `Chapitres.depart` pose l'étape au marqueur de l'acte. Ce sont les gestes des juges de p02, p05, p04,
p10, p09 et p11 d'avant, plus ce qui fait durer (les renforts du pont, le phare à tenir, l'auto des Skateux).

- acte 1 (p02) : trois Skateux au pont, deux de renfort, puis leur grand au cône ;
- acte 2 (p05) : le saut à la nuit au phare, deux Skateux au bois ; la fronde du Trappeur ;
- acte 3 (p04) : **la première `course` d'une mission** — quatre points dans l'ordre, à pied, sous le chrono de Zed ;
  trop lent, c'est l'ACTE qui rate (REPRENDRE L'ACTE 3) ; `calme: skateux` ;
- acte 4 (p10) : la moto de Zed, 80 px de vol ;
- acte 5 (p09) : le phare à tenir 90 s contre trois vagues, puis Ovila qui rallume, dedans ; la manchette ;
- acte 6 (p11) : Zed mené au Brouillard (`proteger`), une auto de Skateux au pare-chocs, ceux qui refusent la paix ;
  et **La Pointe libérée, dans le monde** — une seule prime, et la durée de chaque acte au carnet."""

import re

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_q_js import ESCORTE

AVANT_P = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'p01']
#: Les missions remplacées, dans l'ordre des actes.
ACTES = ['p02', 'p05', 'p04', 'p10', 'p09', 'p11']

#: Recharger la partie : les donneurs qui n'ARRIVENT qu'après une mission (`arrive_apres`) se posent au chargement.
RECHARGER = """
  function recharger(L) { L.Jeu.retourTitre(); L.Jeu.commencer(); L.B.joueur.invincible = 1e6; return L.B.joueur; }
  function versLui(L, slug) { const d = L.Histoire.donneur(slug), j = L.B.joueur; aPied(L); j.x = d.x - 16; j.y = d.y; L.Entites.indexer(); }
  // Jouer jusqu'à l'étape `e` (les marqueurs, leurs répliques, un saut à la nuit), sans jamais passer par-dessus.
  function jusqua(L, o, e) {
    for (let k = 0; k < 2400 && etape(L) !== null && etape(L) < e; k++) { if (L.B.transition) o.fondu(); o.frame(1); ecouter(L); }
    return etape(L);
  }
"""


def _avant(acte):
    """La partie telle qu'une vieille partie l'aurait au début de l'acte `acte` (1 à 6)."""
    return repr(AVANT_P + ACTES[:acte - 1])


def test_acte_1_le_pont_trois_skateux_deux_de_renfort_puis_leur_grand(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        recharger(L);
        const avant = !!L.Histoire.donneur('bilodeau');
        faites(L, """ + _avant(1) + """);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('bilodeau');
        commencer(L, o, 'la_pointe'); jouer(L, o);
        const pont = L.Histoire.resoudre('pont', null);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const pose = { etape: etape(L), n: eux.length, pont: Math.max.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - pont.x, e.y - pont.y) / 16); })) };
        j.x = pont.x; j.y = pont.y; L.Entites.indexer();
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const renfort = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1 && e.etat !== 'assomme'; });
        const vague = { etape: etape(L), n: renfort.length };
        renfort.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const g = B.mission.entites.find(function (e) { return e.cible && e.etape === 2; });
        const grand = { etape: etape(L), chef: !!(g && g.chef), arme: g && g.arme };
        L.Entites.assommer(g); jouer(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        versLui(L, 'bilodeau'); jouer(L, o, 20);
        return { avant: avant, dispo: dispo && dispo.slug, pose: pose, vague: vague, grand: grand, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.p02, apres: etape(L), argent: argent.map(function (a) { return a.montant; }),
                 zed: !!L.Histoire.donneur('zed') };
    }""")
    assert r["avant"] is False, "M. Bilodeau n'est pas devant le phare avant p01"
    assert r["dispo"] == "la_pointe"
    assert r["pose"]["etape"] == 1 and r["pose"]["n"] == 3 and r["pose"]["pont"] <= 10, r["pose"]
    assert r["vague"] == {"etape": 1, "n": 2}, f"deux de renfort : {r['vague']}"
    assert r["grand"] == {"etape": 2, "chef": True, "arme": "cone"}, r["grand"]
    assert r["retour"]["etape"] == 3 and r["retour"]["ligne"].startswith("RETOURNE VOIR M. BILODEAU"), r["retour"]
    for dite in ("pendant:bilodeau:1", "pendant:bilodeau:2", "pendant:bilodeau:3", "pendant:bilodeau:4", "pendant:trappeur:4"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["apres"] >= 4, "l'acte fini marque p02 faite, le chapitre continue"
    assert r["argent"] == [150], "l'acte paie la prime de sa mission d'origine"
    assert r["zed"] is True, "Zed arrive après p02 : il est devant le phare sans recharger"


def test_acte_1_les_skateux_tiennent_le_pont_pendant_qu_on_y_va(banc):
    """Martin, 30 sept. 2026 : « les skateux s'en vont et ne bloquent pas le pont ». On attend 90 s au phare, le
    temps d'y marcher : pas une seconde ils ne s'éloignent du pont."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B;
        faites(L, """ + _avant(1) + """);
        const j = recharger(L);
        commencer(L, o, 'la_pointe'); jouer(L, o);
        const pont = L.Histoire.resoudre('pont', null);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const loin = function () { return eux.map(function (e) { return Math.round(Math.hypot(e.x - pont.x, e.y - pont.y) / 16); }); };
        const au_depart = loin();
        const joueur = Math.round(Math.hypot(j.x - pont.x, j.y - pont.y) / 16);
        let pire = au_depart.slice();
        for (let s = 0; s < 90; s++) { jouer(L, o, 60); pire = loin().map(function (d, i) { return Math.max(d, pire[i]); }); }
        return { etape: etape(L), au_depart: au_depart, pire: pire, joueur: joueur, etats: eux.map(function (e) { return e.etat; }) };
    }""")
    assert r["etape"] == 1 and len(r["au_depart"]) == 3, r
    assert r["joueur"] > 12, f"le juge veut un joueur loin du pont : {r}"
    assert max(r["au_depart"]) <= 10, r
    assert max(r["pire"]) <= 6, f"les Skateux ont quitté le pont : {r}"


def test_acte_2_la_nuit_au_phare_deux_skateux_puis_la_fronde(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant(2) + """);
        const j = recharger(L);
        let hh = p.heure;
        for (let k = 0; k < 400 && L.Monde.estNuit(hh); k++) hh = (hh + 0.005) % 1;
        p.heure = hh;
        const dispo = L.Histoire.disponibleDe('trappeur');
        commencer(L, o, 'la_pointe'); jouer(L, o);
        jusqua(L, o, 6);
        const ph = L.Histoire.lieu('phare');
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 6; });
        const bois = { etape: etape(L), nuit: L.Monde.estNuit(p.heure), n: eux.length,
                       phare: Math.min.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - ph.x, e.y - ph.y) / 16); })) };
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o);
        const retour = { etape: etape(L) };
        versLui(L, 'trappeur'); jouer(L, o, 20);
        return { dispo: dispo && dispo.slug, bois: bois, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.p05, fronde: !!p.armes.fronde };
    }""")
    assert r["dispo"] == "la_pointe", "une vieille partie qui a fait p02 : le Trappeur donne le chapitre, à l'acte 2"
    assert r["bois"]["etape"] == 6 and r["bois"]["nuit"], f"le marqueur saute à la nuit : {r['bois']}"
    assert r["bois"]["n"] == 2 and 6 < r["bois"]["phare"] <= 20, f"deux Skateux au bois : {r['bois']}"
    assert r["retour"]["etape"] == 7
    for dite in ("pendant:trappeur:4", "pendant:trappeur:6", "pendant:trappeur:7", "pendant:trappeur:8"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["fronde"] is True, r


def _acte_3(banc, lent=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant(3) + """);
        const j = recharger(L);
        const dispo = L.Histoire.disponibleDe('zed');
        commencer(L, o, 'la_pointe'); jouer(L, o);
        jusqua(L, o, 9);
        const c = B.mission.course;
        const depart = { etape: etape(L), n: c ? c.points.length : 0, ligne: L.Histoire.ligneObjectif(), gps: L.Histoire.cible() };
        if (""" + ("true" if lent else "false") + """) {
            for (let k = 0; k < 81 * 60 && p.mission; k++) o.frame(1);
            for (let k = 0; k < 900 && (B.transition || B.cinema || !B.menu); k++) { o.frame(1); ecouter(L); }
            return { rate: !p.mission, fait: !!p.missionsFaites.p04, calmes: p.calmes.slice(),
                     menu: B.menu ? B.menu.items.map(function (i) { return i.libelle; }) : null };
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
        versLui(L, 'zed'); jouer(L, o, 20);
        return { dispo: dispo && dispo.slug, depart: depart, auVolant: auVolant, passes: passes, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.p04, calmes: p.calmes.slice() };
    }""")


def test_acte_3_la_course_de_zed_quatre_points_a_pied_dans_l_ordre(banc):
    r = _acte_3(banc)
    assert r["dispo"] == "la_pointe", "Zed (devant le phare après p02) donne le chapitre, à l'acte 3"
    assert r["depart"]["etape"] == 9 and r["depart"]["n"] == 4, r["depart"]
    assert r["depart"]["ligne"].startswith("BATS LE TEMPS DE ZED, À PIED 0/4"), r["depart"]
    assert r["depart"]["gps"], "la flèche vise le premier point"
    assert r["auVolant"]["i"] == 0 and "À PIED" in r["auVolant"]["ligne"], f"au volant, un point ne compte pas : {r['auVolant']}"
    assert [q["i"] for q in r["passes"][:3]] == [1, 2, 3] and r["passes"][3]["etape"] == 10, r["passes"]
    assert r["retour"]["ligne"].startswith("RETOURNE VOIR ZED"), r["retour"]
    for dite in ("pendant:zed:8", "pendant:zed:9", "pendant:zed:10"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["calmes"] == ["skateux"], r


def test_acte_3_trop_lent_l_acte_rate_et_se_reprend(banc):
    r = _acte_3(banc, lent=True)
    assert r["rate"] is True and r["fait"] is False and r["calmes"] == [], r
    assert r["menu"][:2] == ["REPRENDRE L'ACTE 3", "PLUS TARD"], r


def test_acte_4_la_moto_de_zed_quatre_vingts_pixels(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant(4) + """);
        const j = recharger(L);
        const dispo = L.Histoire.disponibleDe('zed');
        commencer(L, o, 'la_pointe'); jouer(L, o);
        jusqua(L, o, 12);
        const v = B.mission.vehicule || (B.mission.chars && B.mission.chars[0]);
        const ph = L.Histoire.lieu('phare');
        const moto = { etape: etape(L), slug: v && v.slug, phare: v ? Math.round(Math.hypot(v.x - ph.x, v.y - ph.y) / 16) : null };
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const saut = { etape: etape(L) };
        let k = 0;
        for (; k < 60 && etape(L) === 13; k++) { v.z = 60; v.vx = 3; v.vy = 0; o.frame(1); ecouter(L); }
        saut.images = k; saut.apres = etape(L);
        v.vx = 0; v.vy = 0; v.vitesse = 0; v.z = 0; jouer(L, o);
        versLui(L, 'zed'); jouer(L, o, 20);
        return { dispo: dispo && dispo.slug, moto: moto, saut: saut, dites: dites, fait: !!p.missionsFaites.p10 };
    }""")
    assert r["dispo"] == "la_pointe"
    # « Pas de moto l'hiver » : la machine de Zed est une motoneige quand la saison le veut.
    assert r["moto"]["etape"] == 12 and r["moto"]["slug"] in ("moto", "motoneige") and r["moto"]["phare"] <= 8, r["moto"]
    assert r["saut"]["etape"] == 13 and r["saut"]["apres"] == 14 and r["saut"]["images"] >= 20, (
        f"80 px de vol, pas un trottoir : {r['saut']}")
    for dite in ("pendant:zed:11", "pendant:zed:13", "pendant:zed:14", "pendant:zed:15", "pendant:ovila:15"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True


def test_acte_5_le_phare_a_tenir_contre_les_vagues_puis_ovila_rallume(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant(5) + """);
        const j = recharger(L);
        commencer(L, o, 'la_pointe'); jouer(L, o);
        jusqua(L, o, 16);
        const ph = L.Histoire.lieu('phare');
        j.x = ph.x; j.y = ph.y + 8; L.Entites.indexer(); jouer(L, o, 20);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 16; });
        const pose = { etape: etape(L), n: eux.length, ligne: L.Histoire.ligneObjectif() };
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const vague = B.mission.entites.filter(function (e) { return e.cible && e.etape === 16 && e.etat !== 'assomme'; }).length;
        const tenu = B.mission.tenu;
        B.mission.tenu = 90 * 60 - 5; jouer(L, o, 20);
        const lampe = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        const piece = dedans(L, o, 'phare');
        const accueil = serrer(L, o, 'ovila');
        jouer(L, o, 20);
        return { pose: pose, vague: vague, tenu: tenu, lampe: lampe, piece: piece, accueil: accueil, dites: dites,
                 fait: !!p.missionsFaites.p09, manchette: p.manchetteForcee || null };
    }""")
    assert r["pose"]["etape"] == 16 and r["pose"]["n"] == 3, r["pose"]
    assert re.search(r" \d+ S$", r["pose"]["ligne"]), f"la ligne compte à rebours : {r['pose']}"
    assert r["vague"] == 2, "le phare se tient contre des vagues"
    assert r["tenu"] > 0, "au phare, le compte monte"
    assert r["lampe"]["etape"] == 17 and r["lampe"]["ligne"].startswith("MONTE RALLUMER"), r["lampe"]
    assert r["piece"] == "phare" and r["accueil"] == "accueil", r
    assert r["fait"] is True and r["manchette"] == "phare_a_tenu", r


def test_acte_6_zed_mene_a_la_chef_puis_la_pointe_est_libre_quatre_districts(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + ESCORTE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant(6) + """);
        const j = recharger(L);
        p.libere = ['faubourg', 'quais', 'erables']; p.faubourgLibere = true;
        const bossAvant = L.Histoire.exigeTenu({ liberes: 4 });
        const argent = paiements(L);
        commencer(L, o, 'la_pointe'); jouer(L, o);
        jusqua(L, o, 19);
        const c = B.mission.protege;
        const auto = B.entites.some(function (e) { return e.type === 'vehicule' && e.conducteur === 'poursuivant' && e.gang === 'skateux'; });
        const zed = { etape: etape(L), personnage: c && c.personnage, suit: rejoindre(L, o, c) };
        arriverAvec(L, o, c, 'bar');
        jouer(L, o, 30);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 20; });
        const bar = L.Histoire.lieu('bar');
        const bagarre = { etape: etape(L), n: eux.length, courent: eux.every(function (e) { return e.etat === 'attaque_joueur'; }),
                          loin: Math.max.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - bar.x, e.y - bar.y) / 16); })) };
        eux.forEach(function (e) { L.Entites.assommer(e); });
        finir(L, o);
        const cour = L.Histoire.resoudre('zone:skateux', null);
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), B.defs);
        return { bossAvant: bossAvant, zed: zed, auto: auto, bagarre: bagarre, dites: dites,
                 fait: !!p.missionsFaites.la_pointe, p11: !!p.missionsFaites.p11,
                 argent: argent.map(function (a) { return a.montant; }), libere: p.libere.slice(), relue: relue.libere,
                 manchette: p.manchetteForcee || null, chasse: L.Entites.gangChasse('skateux'),
                 horsJeu: L.Territoires.horsJeu('skateux'), nom: L.Hud.nomIci(j, L.Monde.zoneA(cour.x, cour.y)),
                 boss: L.Histoire.exigeTenu({ liberes: 4 }), duree: p.durees && p.durees.la_pointe };
    }""")
    assert r["bossAvant"] is False
    assert r["zed"] == {"etape": 19, "personnage": "zed", "suit": True}, r["zed"]
    assert r["auto"], "une auto de Skateux vous colle jusqu'au Brouillard"
    assert r["bagarre"]["etape"] == 20 and r["bagarre"]["n"] == 3 and r["bagarre"]["courent"] and r["bagarre"]["loin"] <= 20, r["bagarre"]
    for dite in ("pendant:zed:19", "pendant:zed:20", "pendant:josee:18"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["p11"] is True and r["argent"] == [500]
    assert r["libere"] == ["faubourg", "quais", "erables", "pointe"] and r["relue"] == r["libere"], r
    assert r["manchette"] == "pointe_liberee" and r["chasse"] and r["horsJeu"], r
    assert r["nom"] == {"nom": "La Pointe", "gang": None}, r["nom"]
    assert r["boss"] is True, "quatre districts libérés : ce que _Le Boss_ demande"
    assert r["duree"] and len(r["duree"]["actes"]) == 1, "la durée du chapitre, par acte joué ici"


def test_une_vieille_partie_qui_a_tout_fait_a_fait_le_chapitre(banc):
    r = banc("function (L, o) {" + OUTILS + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        faites(L, """ + repr(AVANT_P + ACTES) + """);
        recharger(L);
        return { dispo: L.Histoire.disponibles().some(function (m) { return m.slug === 'la_pointe'; }),
                 faite: L.Histoire.exigeTenu({ une_de: ['la_pointe'] }) };
    }""")
    assert r == {"dispo": False, "faite": True}


def test_une_vieille_partie_qui_a_fait_p04_et_p10_sans_p05_saute_les_actes_faits(banc):
    # Les vieux prérequis : p04 ← p02, p10 ← p04, p09 ← p05. Une partie a pu faire p02, p04 et p10 sans p05 : le
    # chapitre part à l'acte 2, puis saute les actes 3 et 4 (ni rejoués, ni repayés) jusqu'au phare.
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + repr(AVANT_P + ["p02", "p04", "p10"]) + """);
        recharger(L);
        const argent = paiements(L);
        commencer(L, o, 'la_pointe'); jouer(L, o);
        jusqua(L, o, 6);
        const acte2 = etape(L);
        B.mission.entites.filter(function (e) { return e.cible && e.etape === 6; }).forEach(function (e) { L.Entites.assommer(e); });
        jouer(L, o);
        versLui(L, 'trappeur'); jouer(L, o, 20);
        jusqua(L, o, 16);
        return { acte2: acte2, apres: etape(L), argent: argent.map(function (a) { return a.montant; }), p05: !!p.missionsFaites.p05,
                 calmes: p.calmes.slice() };
    }""")
    assert r["acte2"] == 6 and r["apres"] == 16, f"les actes 3 et 4 (faits) se sautent : {r}"
    assert r["argent"] == [120] and r["p05"] is True, r
    assert r["calmes"] == [], "le donne de p04 n'est pas redonné — la vieille partie l'avait déjà (ou pas)"
