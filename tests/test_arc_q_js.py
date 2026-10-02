"""L'arc Q jusqu'à sa libération (M16, 29 sept. 2026) — q05, q06 et q13 JOUÉES au bouton, de l'appel à la
prime, sur le modèle de `test_arc_f_js.py`.

- q05, _Cindy veut sortir_ : `proteger` (elle attend, nous suit jusqu'à l'hôtel), puis les deux gars du Beau
  Denis ARRIVENT là où elle est ; couchée, c'est raté (`protege_mort`) ; elle quitte la rue après (`parti_apres`).
- q06, _Le Beau Denis_ : `sans_arme`, enfin lue — la ligne dit « RANGE TON ARME », et une arme au poing chez les
  Morues fait rater ; à mains nues, Denis tombe et `calme: morues` s'inscrit.
- q13, _La nuit des Morues_ : offerte après q06 ET l'un des deux côtés du choix (`exige.une_de`) ; les matelots
  de Sven (`pieton: matelot`) débarquent en deux vagues puis leur bosco ; et **les Quais sont libérés, dans le
  monde** — le gang ne sort plus, ne saute plus, ne prend plus de coin, rend ceux qu'il tenait, sa cour
  redevient « Les Quais » sous la mini-carte, _Le Boss_ compte un district de plus, et la sauvegarde le garde.

⚠️ Depuis le 2 oct. 2026 (docs/jalons/des-missions-en-chapitres.md, vague Q), q05 et q06 sont les actes 1 et 2 de
_Cindy et le Beau Denis_ (marqueurs 0 et 3) ; q13 reste une mission."""

from outils_missions import OUTILS, PLUS_LONGUES

AVANT_Q05 = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01', 'q02', 'q04', 'v01']"

#: Aller chercher le protégé, puis arriver ensemble au lieu.
ESCORTE = """
  function rejoindre(L, o, c) {
    const j = L.B.joueur;
    j.x = c.x + 18; j.y = c.y; L.Entites.indexer(); jouer(L, o, 4);
    return !!c.suit;
  }
  function arriverAvec(L, o, c, lieu) {
    const j = L.B.joueur, l = L.Histoire.lieu(lieu);
    j.x = l.x; j.y = l.y; c.x = l.x + 14; c.y = l.y; c.piste = []; L.Entites.indexer(); jouer(L, o, 4);
  }
"""


def _q05(banc, tuer_cindy=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ESCORTE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, """ + AVANT_Q05 + """);
        // ⚠️ Cindy n'ARRIVE qu'après q04 (`arrive_apres`) : les donneurs se posent au chargement.
        const absente = !L.Histoire.donneur('cindy');
        L.Jeu.retourTitre(); L.Jeu.commencer(); j.invincible = 1e6;
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('cindy');
        const devant = L.Histoire.donneur('cindy'), cantine = L.Histoire.lieu('cantine');
        const poste = devant ? Math.round(Math.hypot(devant.x - cantine.x, devant.y - cantine.y) / 16) : null;
        commencer(L, o, 'cindy_et_le_beau_denis'); jouer(L, o);
        const c = B.mission.protege;
        const attend = { etape: etape(L), c: !!c, suit: !!(c && c.suit), personnage: c && c.personnage };
        const suit = rejoindre(L, o, c);
        if (""" + ("true" if tuer_cindy else "false") + """) {
            L.Entites.assommer(c); jouer(L, o, 4);
            return { rate: !B.partie.mission, fait: !!B.partie.missionsFaites.q05, echecs: B.partie.stats.echecs || 0 };
        }
        arriverAvec(L, o, c, 'hotel');
        const arrivee = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        jouer(L, o, 30);
        const gars = B.mission.entites.filter(function (e) { return e.cible && e.etape === 2; });
        const h = L.Histoire.lieu('hotel');
        const bagarre = { n: gars.length, arch: gars.map(function (e) { return e.arch; }),
                          courent: gars.every(function (e) { return e.etat === 'attaque_joueur'; }),
                          loin: Math.max.apply(null, gars.map(function (e) { return Math.round(Math.hypot(e.x - h.x, e.y - h.y) / 16); })) };
        gars.forEach(function (e) { L.Entites.assommer(e); });
        finir(L, o);
        L.Jeu.retourTitre(); L.Jeu.commencer();
        return { absente: absente, dispo: dispo && dispo.slug, poste: poste, attend: attend, suit: suit, arrivee: arrivee, bagarre: bagarre,
                 dites: dites, fait: !!B.partie.missionsFaites.q05, argent: argent.map(function (a) { return a.montant; }),
                 partie: !L.Histoire.donneur('cindy') };
    }""")


def test_q05_cindy_nous_suit_jusqu_a_l_hotel_puis_les_gars_de_denis_et_elle_quitte_la_rue(banc):
    r = _q05(banc)
    assert r["absente"] is True, "Cindy n'est pas devant la cantine avant q04 (et ne décale rien à l'ouverture)"
    assert r["dispo"] == "cindy_et_le_beau_denis", "Cindy donne le chapitre après la cargaison du Norvégien"
    assert r["poste"] is not None and r["poste"] <= 6, f"Cindy se tient devant la cantine : {r['poste']}"
    assert r["attend"] == {"etape": 1, "c": True, "suit": False, "personnage": "cindy"}, r["attend"]
    assert r["suit"] is True, "rejointe, elle nous suit"
    assert r["arrivee"]["etape"] == 2 and r["arrivee"]["ligne"].startswith("LES GARS DU BEAU DENIS"), r["arrivee"]
    assert r["bagarre"]["n"] == 2 and r["bagarre"]["courent"] and r["bagarre"]["loin"] <= 20, r["bagarre"]
    for dite in ("pendant:cindy:1", "pendant:cindy:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [100]
    assert r["partie"] is True, "Cindy travaille à l'hôtel : elle ne se tient plus devant la cantine"


def test_q05_cindy_couchee_c_est_rate(banc):
    r = _q05(banc, tuer_cindy=True)
    assert r["rate"] is True and r["fait"] is False and r["echecs"] == 1, r


def _q06(banc, arme):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; j.invincible = 1e6;
        faites(L, """ + AVANT_Q05 + """.concat(['q05']));
        const argent = paiements(L);
        // ⚠️ Josée a d'autres missions ouvertes avant elle dans le catalogue (q11, le choix) : on juge que q06 est
        // OFFERTE, pas qu'elle passe la première.
        const dispo = L.Histoire.disponibles().find(function (m) { return m.slug === 'cindy_et_le_beau_denis' && L.Chapitres.donneurDe(m) === 'josee'; });
        p.armes.pistolet = { mun: 12, usure: 0 }; j.arme = 'pistolet'; p.arme = 'pistolet';
        commencer(L, o, 'cindy_et_le_beau_denis'); jouer(L, o);
        const bar = L.Histoire.lieu('bar');
        j.x = bar.x; j.y = bar.y + 8; L.Entites.indexer(); jouer(L, o);
        const armee = { ligne: L.Histoire.ligneObjectif(), etape: etape(L) };
        const coin = L.Histoire.resoudre('zone:morues', null);
        const gardes = B.mission.entites.filter(function (e) { return e.cible && e.etape === 4; });
        const pose = { n: gardes.length, mains: gardes.every(function (e) { return !e.arme; }),
                       coin: Math.max.apply(null, gardes.map(function (e) { return Math.round(Math.hypot(e.x - coin.x, e.y - coin.y) / 16); })) };
        if (""" + ("true" if arme else "false") + """) {
            j.x = gardes[0].x + 30; j.y = gardes[0].y; L.Entites.indexer(); jouer(L, o, 4);
            return { dispo: dispo && dispo.slug, armee: armee, pose: pose, rate: !p.mission,
                     echecs: p.stats.echecs || 0, calmes: p.calmes.slice() };
        }
        j.arme = 'poings'; p.arme = 'poings';
        const rangee = L.Histoire.ligneObjectif();
        j.x = gardes[0].x + 30; j.y = gardes[0].y; L.Entites.indexer(); jouer(L, o, 4);
        gardes.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o);
        const denis = B.mission.entites.find(function (e) { return e.cible && e.etape === 5; });
        const chef = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), chef: !!(denis && denis.chef),
                       mains: denis && !denis.arme, vie: denis && denis.vieMax };
        L.Entites.assommer(denis); jouer(L, o);
        const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        j.x = bar.x; j.y = bar.y; L.Entites.indexer();
        finir(L, o);
        return { dispo: dispo && dispo.slug, armee: armee, pose: pose, rangee: rangee, chef: chef, semer: semer,
                 cache: cache, dites: dites, fait: !!p.missionsFaites.q06, argent: argent.map(function (a) { return a.montant; }),
                 calmes: p.calmes.slice(), calmeMorues: L.Entites.gangCalme('morues') };
    }""")


def test_q06_une_arme_au_poing_chez_les_morues_c_est_rate(banc):
    r = _q06(banc, arme=True)
    assert r["dispo"] == "cindy_et_le_beau_denis", "Josée donne l'acte 2 après Cindy"
    assert r["armee"]["etape"] == 4 and r["armee"]["ligne"].endswith("— RANGE TON ARME"), (
        f"la ligne doit dire de ranger l'arme avant d'y entrer : {r['armee']}")
    assert r["pose"]["n"] == 2 and r["pose"]["mains"] and r["pose"]["coin"] <= 12, r["pose"]
    assert r["rate"] is True and r["echecs"] == 1, f"un pistolet au poing chez les Morues doit faire rater : {r}"
    assert r["calmes"] == [], "une mission ratée ne calme personne"


def test_q06_a_mains_nues_denis_tombe_et_les_morues_te_laissent_passer(banc):
    r = _q06(banc, arme=False)
    assert "RANGE TON ARME" not in r["rangee"], r["rangee"]
    assert r["chef"]["etape"] == 5 and r["chef"]["chef"] and r["chef"]["mains"] and r["chef"]["vie"] == 180, r["chef"]
    assert r["semer"]["etape"] == 6 and r["semer"]["etoiles"] >= 2, r["semer"]
    assert r["cache"]["dedans"] and r["cache"]["apres"] == 0, r["cache"]
    for dite in ("pendant:josee:3", "pendant:josee:5", "pendant:josee:6", "pendant:josee:7"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [350]
    assert r["calmes"] == ["morues"] and r["calmeMorues"] is True


def test_q13_s_ouvre_apres_l_un_ou_l_autre_cote_du_choix(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        faites(L, """ + AVANT_Q05 + """.concat(['q05', 'q06']));
        const ouvertes = function () { return L.Histoire.disponibles().map(function (m) { return m.slug; }); };
        const sans = ouvertes().indexOf('q13') >= 0;
        B.partie.missionsFaites.q11 = 1;
        const avecQ11 = ouvertes().indexOf('q13') >= 0;
        delete B.partie.missionsFaites.q11; B.partie.missionsFaites.q10 = 1;
        const avecQ10 = ouvertes().indexOf('q13') >= 0;
        return { sans: sans, avecQ11: avecQ11, avecQ10: avecQ10 };
    }""")
    assert r == {"sans": False, "avecQ11": True, "avecQ10": True}, r


def test_q13_la_nuit_des_morues_trois_vagues_puis_les_quais_sont_libres_dans_le_monde(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; j.invincible = 1e6;
        faites(L, """ + AVANT_Q05 + """.concat(['q05', 'q06', 'q11']));
        p.libere = ['faubourg']; p.faubourgLibere = true;
        // Un coin que les Morues avaient PRIS aux Cravates, la nuit, et un autre pris AUX Morues : le premier
        // doit revenir, le second non (ce n'est pas elles qui le tiennent).
        const T = L.Territoires, d = T.donnees();
        const aCravates = Object.keys(d.ilots).find(function (k) { return d.ilots[k].gang === 'cravates' && !d.ilots[k].coeur; });
        const aMorues = Object.keys(d.ilots).find(function (k) { return d.ilots[k].gang === 'morues' && !d.ilots[k].coeur; });
        p.territoires = {}; p.territoires[aCravates] = 'morues'; p.territoires[aMorues] = 'chevreuils';
        const avant = { chasse: L.Entites.gangChasse('morues'), horsJeu: T.horsJeu('morues'),
                        boss: L.Histoire.exigeTenu({ liberes: 2 }) };
        const argent = paiements(L);
        commencer(L, o, 'q13'); jouer(L, o);
        const h = L.Histoire.lieu('hotel');
        let hh = p.heure;
        for (let k = 0; k < 400 && L.Monde.estNuit(hh); k++) hh = (hh + 0.005) % 1;
        p.heure = hh;
        j.x = h.x; j.y = h.y + 8; L.Entites.indexer(); jouer(L, o, 30);
        const deJour = etape(L);
        laNuit(L, o); jouer(L, o, 30);
        const vagues = [];
        for (let v = 1; v <= 3; v++) {
            jouer(L, o, 30);
            const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === v && e.vivant; });
            vagues.push({ etape: etape(L), n: eux.length, arch: eux.map(function (e) { return e.arch; }),
                          courent: eux.every(function (e) { return e.etat === 'attaque_joueur'; }),
                          chef: eux.some(function (e) { return e.chef; }), ligne: L.Histoire.ligneObjectif() });
            eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o);
        }
        finir(L, o);
        const coin = L.Histoire.resoudre('zone:morues', null);
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), B.defs);
        return { deJour: deJour, vagues: vagues, dites: dites, avant: avant,
                 fait: !!p.missionsFaites.q13, argent: argent.map(function (a) { return a.montant; }),
                 libere: p.libere.slice(), manchette: p.manchetteForcee || null,
                 chasse: L.Entites.gangChasse('morues'), calme: L.Entites.gangCalme('morues'),
                 horsJeu: T.horsJeu('morues'), autres: T.horsJeu('chevreuils'),
                 rendu: p.territoires[aCravates] || null, garde: p.territoires[aMorues] || null,
                 nom: L.Hud.nomIci(j, L.Monde.zoneA(coin.x, coin.y)),
                 boss: L.Histoire.exigeTenu({ liberes: 2 }),
                 relue: relue.libere };
    }""")
    assert r["avant"]["chasse"] is False and r["avant"]["horsJeu"] is False and r["avant"]["boss"] is False, r["avant"]
    assert r["deJour"] == 0, "de jour, on attend la nuit devant l'hôtel"
    v1, v2, v3 = r["vagues"]
    for v, n in ((v1, 3), (v2, 3)):
        assert v["n"] == n and set(v["arch"]) == {"matelot"} and v["courent"], f"une vague de matelots : {v}"
    assert v1["etape"] == 1 and v2["etape"] == 2 and v3["etape"] == 3, r["vagues"]
    assert v3["n"] == 1 and v3["chef"] and v3["arch"] == ["matelot"], f"le bosco : {v3}"
    for dite in ("pendant:josee:0", "pendant:sven:1", "pendant:josee:2", "pendant:josee:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [500]
    # Les Quais sont libres — et ça se voit.
    assert r["libere"] == ["faubourg", "quais"] and r["relue"] == ["faubourg", "quais"], r
    assert r["manchette"] == "quais_liberes"
    assert r["chasse"] and r["calme"] and r["horsJeu"], "les Morues sortent du jeu"
    assert r["autres"] is False, "les Chevreuils, eux, tiennent encore les Érables"
    assert r["rendu"] is None, "le coin que les Morues avaient pris aux Cravates leur revient"
    assert r["garde"] == "chevreuils", "un coin pris AUX Morues n'est pas à elles : il ne bouge pas"
    assert r["nom"] == {"nom": "Les Quais", "gang": None}, f"sous la mini-carte, leur cour redevient le quartier : {r['nom']}"
    assert r["boss"] is True, "_Le Boss_ compte deux districts : le Faubourg et les Quais"
