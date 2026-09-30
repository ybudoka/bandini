"""Des missions en chapitres (docs/jalons/des-missions-en-chapitres.md) — le moteur, joué au banc sur une mission
de banc (`zz`) greffée au catalogue, comme `test_sur_place_js.py` greffe la sienne."""

from tests.outils_missions import OUTILS, PLUS_LONGUES

#: Deux actes : M. Bilodeau au pont, puis le Trappeur ; chacun finit par un `retourner`.
ZZ = """
  function greffer(L) {
    const m = { slug: 'zz', titre: 'Zz', donneur: 'bilodeau', recompense: 500, prerequis: [], phase: 1,
      echec: ['mort', 'arrete'], donne: {}, remplace: ['za', 'zb'],
      objectifs: [
        { type: 'acte', texte: 'ACTE 1 — LE PONT', donneur: 'bilodeau' },
        { type: 'aller', texte: 'VA AU PONT', lieu: 'phare', rayon: 5 },
        { type: 'retourner', texte: 'RETOURNE VOIR M. BILODEAU', donne: { calme: 'skateux' } },
        { type: 'acte', texte: 'ACTE 2 — LES COLLETS', donneur: 'trappeur' },
        { type: 'aller', texte: 'VA AU BOIS', lieu: 'casse_croute', rayon: 5 },
        { type: 'retourner', texte: 'RETOURNE VOIR LE TRAPPEUR' } ],
      dialogue: { appel: [], intro: [], pendant: [], fin: [], echec: [] }, scenes: {} };
    L.B.defs.missions.push(m);
    return m;
  }
  // M. Bilodeau et le Trappeur n'arrivent qu'après p01 (`arrive_apres`) : la partie les a rencontrés, on recharge.
  function ouvrir(L) {
    L.Jeu.commencer(); L.graine(6);
    // Et les six de la Pointe : le chapitre de banc est le seul que M. Bilodeau, le Trappeur ou Zed aient à donner.
    ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'p01', 'p02', 'p04', 'p05', 'p09', 'p10', 'p11'].forEach(function (s) { L.B.partie.missionsFaites[s] = 1; });
    L.Jeu.retourTitre(); L.Jeu.commencer(); L.B.joueur.invincible = 1e6;
    return greffer(L);
  }
  function a(L, slug) { const d = L.Histoire.donneur(slug), j = L.B.joueur; j.x = d.x - 16; j.y = d.y; L.Entites.indexer(); }
"""


def test_un_acte_pose_son_carton_et_sa_reprise_puis_avance_seul(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        ouvrir(L); commencer(L, o, 'zz'); jouer(L, o);
        const pm = L.B.partie.mission;
        return { etape: pm.etape, reprise: pm.reprise && pm.reprise.etape, acte: L.Chapitres.acteA(L.Histoire.courante(), pm.etape),
                 chapitre: L.B.partie.chapitres.zz, donneur: L.Chapitres.donneurDe(L.Histoire.courante()) };
    }""")
    assert r == {"etape": 1, "reprise": 0, "acte": 0, "chapitre": 0, "donneur": "bilodeau"}


def test_retourner_au_milieu_avance_a_l_acte_suivant_sans_payer(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        ouvrir(L);
        const B = L.B, p = B.partie;
        const argent = paiements(L);
        commencer(L, o, 'zz'); jouer(L, o);
        const ph = L.Histoire.lieu('phare'); B.joueur.x = ph.x; B.joueur.y = ph.y; L.Entites.indexer(); jouer(L, o);
        a(L, 'bilodeau'); jouer(L, o);
        return { etape: p.mission && p.mission.etape, donneur: L.Chapitres.donneurDe(L.Histoire.courante()),
                 paye: argent.length, calmes: p.calmes.slice(), za: !!p.missionsFaites.za, reprise: p.mission.reprise.etape };
    }""")
    assert r["etape"] == 4 and r["donneur"] == "trappeur", r
    assert r["paye"] == 0, "un retourner au milieu ne paie pas la prime"
    assert "skateux" in r["calmes"], "le donne de l'objectif est accordé quand il est fait"
    assert r["za"] is True, "l'acte fini marque sa mission remplacée faite"
    assert r["reprise"] == 3


def test_le_dernier_retourner_paie_et_le_chapitre_est_fait(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        ouvrir(L);
        const B = L.B, p = B.partie;
        const argent = paiements(L);
        commencer(L, o, 'zz'); jouer(L, o);
        p.mission.etape = 4; jouer(L, o);                         // au bois : on saute le premier acte
        const cc = L.Histoire.lieu('casse_croute'); B.joueur.x = cc.x; B.joueur.y = cc.y; L.Entites.indexer(); jouer(L, o);
        a(L, 'trappeur'); finir(L, o);
        return { fait: !!p.missionsFaites.zz, zb: !!p.missionsFaites.zb, argent: argent.map(function (x) { return x.montant; }),
                 chapitre: p.chapitres.zz === undefined };
    }""")
    assert r == {"fait": True, "zb": True, "argent": [500], "chapitre": True}


def test_une_vieille_partie_commence_au_premier_acte_pas_fait(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        const m = ouvrir(L), p = L.B.partie;
        p.missionsFaites.za = 1;
        const depart = L.Chapitres.depart(m), donneur = L.Chapitres.donneurDe(m), dispo = L.Histoire.disponibleDe('trappeur');
        commencer(L, o, 'zz'); jouer(L, o);
        return { depart: depart, donneur: donneur, dispo: dispo && dispo.slug, etape: p.mission.etape };
    }""")
    assert r == {"depart": 3, "donneur": "trappeur", "dispo": "zz", "etape": 4}


def test_toutes_ses_missions_faites_le_chapitre_est_fait(banc):
    r = banc("function (L, o) {" + OUTILS + ZZ + """
        const m = ouvrir(L), p = L.B.partie;
        p.missionsFaites.za = 1; p.missionsFaites.zb = 1;
        return { fait: L.Chapitres.fait(m), dispo: L.Histoire.disponibles().some(function (x) { return x.slug === 'zz'; }) };
    }""")
    assert r == {"fait": True, "dispo": False}


def test_sans_ses_objectifs_le_catalogue_sait_le_donneur_de_l_acte(banc):
    # Dans le vrai jeu, les objectifs arrivent par `/api/mission/<slug>` : le téléphone et les bulles lisent le
    # catalogue, qui porte `actes` (l'étape et le donneur de chaque acte).
    r = banc("function (L, o) {" + OUTILS + ZZ + """
        const m = ouvrir(L), p = L.B.partie;
        m.actes = [[0, 'bilodeau'], [3, 'trappeur']]; delete m.objectifs;
        p.missionsFaites.za = 1;
        return { donneur: L.Chapitres.donneurDe(m), depart: L.Chapitres.depart(m) };
    }""")
    assert r == {"donneur": "trappeur", "depart": 3}


def test_plus_tard_puis_recharger_repart_a_l_acte_atteint_sans_rejouer_l_intro(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        ouvrir(L);
        const B = L.B;
        B.partie.chapitres = { zz: 3 }; B.partie.appels.zz = true;
        L.Jeu.retourTitre(); L.Jeu.commencer(); B.joueur.invincible = 1e6; greffer(L);
        const dispo = L.Histoire.disponibleDe('trappeur');
        L.Histoire.parler('trappeur');
        const intro = !!B.cinema && B.cinema.partie === 'intro';
        jouer(L, o);
        return { dispo: dispo && dispo.slug, etape: B.partie.mission && B.partie.mission.etape, intro: intro };
    }""")
    assert r["dispo"] == "zz" and r["etape"] == 4 and r["intro"] is False, r


#: Mourir (ou se faire pogner) et attendre le menu de la reprise ; choisir une ligne comme ACTION la choisit.
REPRENDRE = """
  function attendreLeMenu(L, o) {
    for (let k = 0; k < 900 && (L.B.transition || L.B.cinema || !L.B.menu); k++) { o.frame(1); ecouter(L); }
    return L.B.menu ? L.B.menu.items.map(function (i) { return i.libelle; }) : null;
  }
  function choisir(L, o, libelle) {
    const m = L.B.menu, item = m.items.find(function (x) { return x.libelle.indexOf(libelle) === 0; });
    if (item.faire(item) !== false && L.B.menu === m) L.Hud.fermerMenu();
    o.fondu();
    for (let k = 0; k < 400 && L.B.transition; k++) o.frame(1);
    jouer(L, o);
  }
"""


def test_mort_a_l_acte_2_reprendre_rend_l_etape_le_char_et_l_arme(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        ouvrir(L);
        const B = L.B, p = B.partie, j = B.joueur;
        p.armes.fronde = { mun: 12 }; L.Combat.degainer(j, 'fronde');
        const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        const rue = L.Histoire.tuileDeRue(j.x, j.y, 12);
        const v = L.Vehicules.creer('taxi', rue.x, rue.y, CAP[rue.sens], { etat: 'stationne' });
        j.x = v.x + 10; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer();
        commencer(L, o, 'zz'); jouer(L, o);
        const monte = !!j.dansVehicule;
        p.mission.etape = 2; L.Histoire.avancer(); jouer(L, o);   // le marqueur de l'acte 2
        const reprise = { x: p.mission.reprise.x, y: p.mission.reprise.y };
        L.Missions.hopital('banc');
        const menu = attendreLeMenu(L, o);
        choisir(L, o, 'REPRENDRE');
        const pres = Math.round(Math.hypot(j.x - reprise.x, j.y - reprise.y) / 16);
        const moto = B.entites.find(function (e) { return e.type === 'vehicule' && e.def.slug === 'taxi' && e !== v; });
        return { menu: menu, etape: p.mission && p.mission.etape, pres: pres, arme: j.arme, moto: !!moto, dedans: !!B.interieur, monte: monte };
    }""")
    assert r["menu"][:2] == ["REPRENDRE L'ACTE 2", "PLUS TARD"], r
    assert r["etape"] == 4 and r["pres"] <= 6 and r["arme"] == "fronde", r
    assert r["monte"], "le juge part bien en taxi (la moto est remisée en janvier)"
    assert r["moto"], "un char neuf du même modèle attend sur la rue d'à côté"
    assert not r["dedans"], "on reprend en ville, pas dans la chambre de l'hôpital"


def test_arrete_la_prison_prend_l_arme_la_reprise_la_rend(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        ouvrir(L);
        const B = L.B, p = B.partie, j = B.joueur;
        p.armes.pistolet = { mun: 30 }; L.Combat.degainer(j, 'pistolet');
        commencer(L, o, 'zz'); jouer(L, o);
        B.recherche.etoiles = 1; L.Missions.prison(null);
        attendreLeMenu(L, o);
        const sans = !p.armes.pistolet;
        choisir(L, o, 'REPRENDRE');
        return { sans: sans, arme: j.arme, mun: p.armes.pistolet && p.armes.pistolet.mun };
    }""")
    assert r == {"sans": True, "arme": "pistolet", "mun": 30}


def test_mourir_puis_se_faire_arreter_dans_le_fondu_ne_fait_qu_un_menu(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        ouvrir(L);
        const B = L.B; commencer(L, o, 'zz'); jouer(L, o);
        L.Missions.hopital('banc'); B.recherche.etoiles = 1; L.Missions.prison(null);
        let menus = 0, avant = null;
        for (let k = 0; k < 1200; k++) { o.frame(1); ecouter(L); if (B.menu && B.menu !== avant) { menus++; avant = B.menu; } }
        return { menus: menus, titre: B.menu && B.menu.titre };
    }""")
    assert r == {"menus": 1, "titre": "MISSION RATÉE"}


def test_plus_tard_garde_l_acte_et_le_telephone_rappellera(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        ouvrir(L);
        const B = L.B, p = B.partie; commencer(L, o, 'zz'); jouer(L, o);
        p.appels.zz = true;
        p.mission.etape = 2; L.Histoire.avancer(); jouer(L, o);
        L.Missions.hopital('banc'); attendreLeMenu(L, o); choisir(L, o, 'PLUS TARD');
        return { mission: p.mission, chapitre: p.chapitres.zz, appel: !!p.appels.zz };
    }""")
    assert r == {"mission": None, "chapitre": 3, "appel": False}


def test_une_mission_ordinaire_ratee_n_ouvre_aucun_menu(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        const m = ouvrir(L);
        m.objectifs = m.objectifs.filter(function (x) { return x.type !== 'acte'; }); delete m.remplace;
        commencer(L, o, 'zz'); jouer(L, o);
        L.Missions.hopital('banc');
        for (let k = 0; k < 900; k++) { o.frame(1); ecouter(L); }
        return { menu: !!L.B.menu, mission: L.B.partie.mission };
    }""")
    assert r == {"menu": False, "mission": None}


def test_le_chronometre_compte_le_jeu_pas_la_pause_ni_les_menus(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        ouvrir(L);
        const B = L.B, p = B.partie; commencer(L, o, 'zz'); jouer(L, o);
        const t0 = p.mission.images || 0;
        for (let k = 0; k < 600; k++) o.frame(1);                   // 10 s de jeu
        L.Jeu.pause(); for (let k = 0; k < 600; k++) o.frame(1); L.Jeu.reprendre();
        L.Hud.ouvrirMenu({ titre: 'X', items: [{ libelle: 'OK', faire: function () { return true; } }] });
        for (let k = 0; k < 600; k++) o.frame(1); L.Hud.fermerMenu();
        return { s: Math.round(((p.mission.images || 0) - t0) / 60) };
    }""")
    assert r["s"] == 10


def test_la_duree_s_ecrit_a_la_reussite_par_acte_et_au_carnet(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        ouvrir(L);
        const B = L.B, p = B.partie; commencer(L, o, 'zz'); jouer(L, o);
        for (let k = 0; k < 1200; k++) o.frame(1);
        p.mission.etape = 2; L.Histoire.avancer(); jouer(L, o);
        for (let k = 0; k < 600; k++) o.frame(1);
        p.mission.etape = 5; L.Histoire.avancer(); finir(L, o);
        const fiche = L.Hud.menuCarnetFiche('bilodeau').items.find(function (i) { return i.libelle.indexOf('ZZ') >= 0; });
        return { d: p.durees.zz, carnet: fiche && fiche.detail };
    }""")
    d = r["d"]
    assert d["actes"][0] >= 20 and d["actes"][1] >= 10, d
    assert d["dernier"] == sum(d["actes"]) and d["meilleur"] == d["dernier"], d
    assert r["carnet"] == f"FAITE · {d['dernier'] // 60}:{d['dernier'] % 60:02d}", r


def test_une_reprise_garde_la_duree_des_actes_d_avant(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        ouvrir(L);
        const B = L.B, p = B.partie; commencer(L, o, 'zz'); jouer(L, o);
        for (let k = 0; k < 1200; k++) o.frame(1);
        p.mission.etape = 2; L.Histoire.avancer(); jouer(L, o);
        L.Missions.hopital('banc'); attendreLeMenu(L, o); choisir(L, o, 'REPRENDRE');
        return p.mission.actes;
    }""")
    assert len(r) == 1 and r[0] >= 20, r


#: Coucher ceux de l'étape encore DEBOUT (un K.-O. reste `vivant` : l'aide commune de `outils_missions` les
#: recompterait à chaque vague).
DEBOUT = """
  function coucherDebout(L, o) {
    const e0 = L.B.partie.mission.etape;
    const eux = L.B.mission.entites.filter(function (e) { return e.cible && e.etape === e0 && e.vivant && e.etat !== 'assomme'; });
    eux.forEach(function (e) { L.Entites.assommer(e); });
    for (let k = 0; k < 30; k++) { o.frame(1); ecouter(L); }
    return eux.length;
  }
"""


def test_renforts_deux_vagues_avant_que_l_objectif_tombe(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + DEBOUT + """
        const m = ouvrir(L), p = L.B.partie;
        m.objectifs[1] = { type: 'tuer', texte: 'DÉGAGE LE PHARE', groupe: 'skateux', n: 3, ou: 'phare',
                           renforts: { vagues: 2, n: 2 } };
        commencer(L, o, 'zz'); jouer(L, o);
        const vagues = [];
        for (let k = 0; k < 5 && p.mission.etape === 1; k++) vagues.push(coucherDebout(L, o));
        return { vagues: vagues, etape: p.mission.etape };
    }""")
    assert r["vagues"] == [3, 2, 2] and r["etape"] == 2, r


def test_sans_renforts_un_tuer_tombe_d_un_coup(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + DEBOUT + """
        const m = ouvrir(L), p = L.B.partie;
        m.objectifs[1] = { type: 'tuer', texte: 'DÉGAGE LE PHARE', groupe: 'skateux', n: 3, ou: 'phare' };
        commencer(L, o, 'zz'); jouer(L, o);
        return { n: coucherDebout(L, o), etape: p.mission.etape };
    }""")
    assert r == {"n": 3, "etape": 2}


def test_etoiles_sur_un_aller(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        const m = ouvrir(L); m.objectifs[1].etoiles = 2;
        commencer(L, o, 'zz'); jouer(L, o);
        return L.B.recherche.etoiles;
    }""")
    assert r == 2


def test_une_poursuite_nait_hors_champ_colle_et_lache_a_la_fin_de_l_objectif(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        const m = ouvrir(L), B = L.B, j = B.joueur;
        m.objectifs[1].poursuite = { groupe: 'skateux', chars: 1 };
        commencer(L, o, 'zz'); jouer(L, o);
        const v = B.entites.find(function (e) { return e.type === 'vehicule' && e.conducteur === 'poursuivant'; });
        if (!v) return { v: false };
        const nait = Math.round(Math.hypot(v.x - j.x, v.y - j.y)), horsChamp = !L.Entites.visibleAEcran(v.x, v.y, 0);
        for (let k = 0; k < 900; k++) o.frame(1);
        const pres = Math.round(Math.hypot(v.x - j.x, v.y - j.y));
        const ph = L.Histoire.lieu('phare'); j.x = ph.x; j.y = ph.y; L.Entites.indexer(); jouer(L, o);
        return { v: true, nait: nait, horsChamp: horsChamp, pres: pres, apres: v.conducteur, gang: v.gang };
    }""")
    assert r["v"], "un char du gang naît quand l'objectif commence"
    assert r["horsChamp"] and r["nait"] >= 300, r
    assert r["pres"] < r["nait"] - 100, f"il s'approche : {r}"
    assert r["gang"] == "skateux" and r["apres"] == "trafic", r
