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
    // Et ce qu'ils donnent APRÈS la paix de La Pointe (p07 chez M. Bilodeau, p08 et p12 chez Zed — vague 20) : faites
    // aussi, sinon `parler` ouvre la leur au lieu du chapitre de banc.
    L.B.defs.missions.forEach(function (x) {
      if (['bilodeau', 'trappeur', 'zed'].indexOf(x.donneur) >= 0) L.B.partie.missionsFaites[x.slug] = 1;
    });
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
        const nait = Math.round(Math.hypot(v.x - j.x, v.y - j.y)), horsChamp = !L.Entites.visibleAEcran(v.x, v.y, 0), gang = v.gang;
        for (let k = 0; k < 900; k++) o.frame(1);
        const pres = Math.round(Math.hypot(v.x - j.x, v.y - j.y));
        const ph = L.Histoire.lieu('phare'); j.x = ph.x; j.y = ph.y; L.Entites.indexer(); jouer(L, o);
        return { v: true, nait: nait, horsChamp: horsChamp, pres: pres, apres: v.conducteur, gang: gang };
    }""")
    assert r["v"], "un char du gang naît quand l'objectif commence"
    assert r["horsChamp"] and r["nait"] >= 300, r
    assert r["pres"] < r["nait"] - 100, f"il s'approche : {r}"
    assert r["gang"] == "skateux" and r["apres"] == "trafic", r


def _tenir(banc, sortir, strict=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        const m = ouvrir(L), B = L.B, p = B.partie, j = B.joueur;
        m.objectifs[1] = { type: 'tenir', texte: 'TIENS LE PHARE', lieu: 'phare', rayon: 6, secondes: 10, strict: """
                + ("true" if strict else "false") + """ };
        commencer(L, o, 'zz'); jouer(L, o);
        const ph = L.Histoire.lieu('phare'); j.x = ph.x; j.y = ph.y; L.Entites.indexer();
        for (let k = 0; k < 360; k++) o.frame(1);
        const ligne = L.Histoire.ligneObjectif();
        if (""" + ("true" if sortir else "false") + """) { j.x = ph.x + 16 * 12; L.Entites.indexer(); o.frame(2); j.x = ph.x; L.Entites.indexer(); }
        for (let k = 0; k < 360; k++) o.frame(1);
        return { etape: p.mission ? p.mission.etape : null, ligne: ligne, gps: !!L.Histoire.cible() };
    }""")


def test_tenir_dix_secondes_sans_sortir_avance(banc):
    r = _tenir(banc, sortir=False)
    assert r["etape"] == 2, r
    assert "TIENS LE PHARE" in r["ligne"] and " S" in r["ligne"], "la ligne d'objectif compte à rebours"


def test_tenir_sortir_remet_le_compte_a_zero(banc):
    r = _tenir(banc, sortir=True)
    assert r["etape"] == 1 and r["gps"], r


def test_tenir_strict_sortir_fait_rater(banc):
    assert _tenir(banc, sortir=True, strict=True)["etape"] is None


def test_le_fuyard_saute_dans_un_autre_char_avant_de_tomber(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        const m = ouvrir(L), B = L.B;
        m.objectifs[1] = { type: 'ramasser', texte: 'RATTRAPE LE VOLEUR', cible: 'fuyard', vehicule: 'auto', relais: 1 };
        commencer(L, o, 'zz'); jouer(L, o);
        const premier = B.mission.fuyard; premier.vie = 1; jouer(L, o);
        const second = B.mission.fuyard, tombe1 = !!B.mission.fuyardTombe;
        const pres = second ? Math.round(Math.hypot(second.x - premier.x, second.y - premier.y) / 16) : null;
        if (second) { second.vie = 1; jouer(L, o); }
        return { autre: !!second && second !== premier, tombe1: tombe1, tombe2: !!B.mission.fuyardTombe, pres: pres,
                 premierGare: premier.conducteur === null && !premier.fuite };
    }""")
    assert r["autre"] and not r["tombe1"], r
    assert r["tombe2"], "le dernier relais fait, il tombe"
    assert r["pres"] is not None and r["pres"] <= 12, "il saute dans un char tout près du premier"
    assert r["premierGare"], r


def test_le_donneur_qui_arrive_apres_un_acte_est_la_pour_l_acte_suivant(banc):
    # Zed n'arrive qu'après p02 (`arrive_apres`) : l'acte 1 qui la remplace fini, il est devant le phare — sans
    # recharger la partie. Et le `message` du `donne` de l'objectif s'affiche.
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'p01'].forEach(function (s) { L.B.partie.missionsFaites[s] = 1; });
        L.Jeu.retourTitre(); L.Jeu.commencer(); L.B.joueur.invincible = 1e6;
        const m = greffer(L), B = L.B;
        m.remplace = ['p02', 'zb']; m.objectifs[3].donneur = 'zed';
        m.objectifs[2].donne = { message: 'LE PONT DE LA POINTE EST OUVERT' };
        const avant = !!L.Histoire.donneur('zed');
        const vus = []; const vrai = L.Hud.message; L.Hud.message = function (t) { vus.push(t); return vrai.apply(null, arguments); };
        commencer(L, o, 'zz'); jouer(L, o);
        const ph = L.Histoire.lieu('phare'); B.joueur.x = ph.x; B.joueur.y = ph.y; L.Entites.indexer(); jouer(L, o);
        a(L, 'bilodeau'); jouer(L, o);
        return { avant: avant, apres: !!L.Histoire.donneur('zed'), etape: B.partie.mission.etape,
                 message: vus.indexOf('LE PONT DE LA POINTE EST OUVERT') >= 0 };
    }""")
    assert r == {"avant": False, "apres": True, "etape": 4, "message": True}


# --- La relecture finale (30 sept. 2026) : ce que les juges d'avant ne voyaient pas ----------------------------------


def test_reprendre_un_acte_ne_redonne_pas_le_donne_de_l_acte_d_avant(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        const p = L.B.partie; ouvrir(L);
        p.missionsFaites.za = 1;                                   // une vieille partie : l'acte 1 est fait
        commencer(L, o, 'zz'); jouer(L, o);
        return { etape: p.mission.etape, calmes: p.calmes.slice() };
    }""")
    assert r["etape"] == 4 and "skateux" not in r["calmes"], r


def test_la_prime_d_un_acte_se_paie_et_s_affiche_avec_son_message(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        const m = ouvrir(L), B = L.B;
        m.objectifs[2].donne = { prime: 150, message: 'LE PONT EST OUVERT' };
        const argent = paiements(L), bandeaux = [];
        const vrai = L.Hud.prime; L.Hud.prime = function (b) { bandeaux.push({ montant: b.montant, titre: b.titre, quoi: b.quoi }); return vrai.apply(null, arguments); };
        commencer(L, o, 'zz'); jouer(L, o);
        const ph = L.Histoire.lieu('phare'); B.joueur.x = ph.x; B.joueur.y = ph.y; L.Entites.indexer(); jouer(L, o);
        a(L, 'bilodeau'); jouer(L, o);
        return { argent: argent.map(function (x) { return x.montant; }), bandeaux: bandeaux, etape: B.partie.mission.etape };
    }""")
    assert r["argent"] == [150] and r["etape"] == 4, r
    assert r["bandeaux"] == [{"montant": 150, "titre": "LE PONT EST OUVERT", "quoi": "ACTE RÉUSSI"}], r


def test_le_gps_d_un_chapitre_a_reprendre_mene_au_donneur_de_l_acte(banc):
    r = banc("function (L, o) {" + OUTILS + ZZ + """
        ouvrir(L); const p = L.B.partie;
        p.chapitres = { zz: 3 }; p.appels.zz = true;
        const g = L.Histoire.cible();
        return { nom: g && g.nom, trappeur: L.Histoire.personnage('trappeur').nom };
    }""")
    assert r["nom"] == r["trappeur"], r


def test_l_auto_de_poursuite_se_vole_et_s_oublie(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        const m = ouvrir(L), B = L.B, j = B.joueur;
        m.objectifs[1].poursuite = { groupe: 'skateux', chars: 1 };
        commencer(L, o, 'zz'); jouer(L, o);
        const v = B.entites.find(function (e) { return e.type === 'vehicule' && e.conducteur === 'poursuivant'; });
        const w = B.entites.filter(function (e) { return e.type === 'vehicule' && e.conducteur === 'poursuivant'; });
        j.x = v.x + 12; j.y = v.y; v.vitesse = 0; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer();
        const vole = { dedans: j.dansVehicule === v, mission: v.mission || null, gang: v.gang || null };
        return { vole: vole };
    }""")
    assert r["vole"] == {"dedans": True, "mission": None, "gang": None}, r


def test_relachee_l_auto_de_poursuite_n_est_plus_a_la_mission(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        const m = ouvrir(L), B = L.B, j = B.joueur;
        m.objectifs[1].poursuite = { groupe: 'skateux', chars: 1 };
        commencer(L, o, 'zz'); jouer(L, o);
        const v = B.entites.find(function (e) { return e.type === 'vehicule' && e.conducteur === 'poursuivant'; });
        const ph = L.Histoire.lieu('phare'); j.x = ph.x; j.y = ph.y; L.Entites.indexer(); jouer(L, o);
        return { conducteur: v.conducteur, mission: v.mission || null, gang: v.gang || null, poursuite: !!v.poursuite };
    }""")
    assert r == {"conducteur": "trafic", "mission": None, "gang": None, "poursuite": False}


def test_le_chronometre_compte_aussi_les_repliques(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        const m = ouvrir(L), B = L.B, p = B.partie;
        m.dialogue.pendant = [{ qui: 'bilodeau', texte: 'Les voyez-vous? Trois, sur le pont, avec leurs planches.', objectif: 1 }];
        commencer(L, o, 'zz');
        let k = 0; const t0 = p.mission.images || 0;
        for (; k < 600 && !B.cinema; k++) o.frame(1);
        const avant = p.mission.images || 0; let n = 0;
        for (; n < 60 && B.cinema; n++) o.frame(1);
        return { cinema: n, compte: (p.mission.images || 0) - avant };
    }""")
    assert r["cinema"] > 10 and r["compte"] >= r["cinema"] - 1, r


def test_mourir_deux_fois_dans_le_meme_acte_garde_le_char(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        ouvrir(L);
        const B = L.B, p = B.partie, j = B.joueur;
        const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        const rue = L.Histoire.tuileDeRue(j.x, j.y, 12);
        const v = L.Vehicules.creer('taxi', rue.x, rue.y, CAP[rue.sens], { etat: 'stationne' });
        j.x = v.x + 10; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer();
        commencer(L, o, 'zz'); jouer(L, o);
        L.Missions.hopital('banc'); attendreLeMenu(L, o); choisir(L, o, 'REPRENDRE');
        const reprise = p.mission.reprise;
        return { char: reprise.char && reprise.char.slug };
    }""")
    assert r["char"] == "taxi", r


def test_l_intro_d_un_chapitre_trouve_les_hommes_du_premier_acte_poses(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        const m = ouvrir(L), B = L.B;
        m.dialogue.intro = [{ qui: 'bilodeau', texte: "C'est le seul pont, monsieur." }];
        m.objectifs[1] = { type: 'tuer', texte: 'DÉGAGE LE PHARE', groupe: 'skateux', n: 3, ou: 'phare' };
        L.Histoire.parler('bilodeau');
        const pendantLIntro = !!B.cinema || !!B.scene;
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; }).length;
        return { intro: pendantLIntro, etape: B.partie.mission.etape, eux: eux };
    }""")
    assert r == {"intro": True, "etape": 1, "eux": 3}, r


# --- Les autres arcs (2 oct. 2026) : ce que le moteur apprend pour eux -----------------------------------------------


def test_l_echec_dit_celui_de_l_acte_qui_a_rate(banc):
    """Chaque acte garde l'échec de sa mission d'origine (`_e`, l'étape de son marqueur) : on entend celui de l'acte
    qui a raté, jamais celui d'un autre — et une réplique sans `objectif` se dit à n'importe lequel."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        const m = ouvrir(L), p = L.B.partie;
        m.dialogue.echec = [{ qui: 'bilodeau', texte: 'Raté au pont.', objectif: 0 },
                            { qui: 'trappeur', texte: 'Raté au bois.', objectif: 3 },
                            { qui: 'trappeur', texte: 'Raté, tout court.' }];
        const vu = [], vrai = L.Hud.dialogue;
        L.Hud.dialogue = function (nom, lignes) { vu.push(lignes[0]); return vrai.apply(null, arguments); };
        commencer(L, o, 'zz'); jouer(L, o);
        p.mission.etape = 2; L.Histoire.avancer(); jouer(L, o);   // le marqueur de l'acte 2
        const acte = L.Chapitres.marqueurDe(L.Histoire.courante());
        L.Missions.hopital('banc');
        attendreLeMenu(L, o);
        return { acte: acte, echec: dites.filter(function (d) { return d.indexOf('echec:') === 0; }) };
    }""")
    assert r["acte"] == 3, r
    assert r["echec"] == ["echec:trappeur:3", "echec:trappeur:"], f"seul l'échec de l'acte 2 (et le commun) : {r}"


def test_un_prerequis_qui_vise_un_acte_s_ouvre_quand_l_acte_finit(banc):
    """h03 attend d01 — l'acte 1 de la dette, pas tout le chapitre : la mission s'offre dès que l'acte est fini (le
    chapitre laissé à l'acte 2, PLUS TARD — pendant une mission, rien d'autre ne s'offre)."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        ouvrir(L);
        const B = L.B, p = B.partie;
        B.defs.missions.push({ slug: 'zq', titre: 'Zq', donneur: 'ovila', recompense: 1, prerequis: ['za'], phase: 1,
                               echec: [], donne: {}, objectifs: [{ type: 'aller', texte: 'VA', lieu: 'phare', rayon: 5 }],
                               dialogue: { appel: [], intro: [], pendant: [], fin: [], echec: [] }, scenes: {} });
        const offerte = function () { return L.Histoire.disponibles().some(function (x) { return x.slug === 'zq'; }); };
        commencer(L, o, 'zz'); jouer(L, o);
        const pendantActe1 = offerte();
        const ph = L.Histoire.lieu('phare'); B.joueur.x = ph.x; B.joueur.y = ph.y; L.Entites.indexer(); jouer(L, o);
        a(L, 'bilodeau'); jouer(L, o);
        const acte2 = p.mission && p.mission.etape;
        L.Missions.hopital('banc'); attendreLeMenu(L, o); choisir(L, o, 'PLUS TARD');
        return { pendantActe1: pendantActe1, acte2: acte2, apres: offerte(), zz: !!p.missionsFaites.zz };
    }""")
    assert r == {"pendantActe1": False, "acte2": 4, "apres": True, "zz": False}, r


def test_chaque_acte_compte_pour_le_quartier_de_son_donneur(banc):
    """La réputation : le chapitre comptait une fois (son dernier donneur) là où ses missions comptaient chacune."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        ouvrir(L);
        const B = L.B, comptes = [], vrai = L.Reputation.reussite;
        L.Reputation.reussite = function (m) { comptes.push(L.Chapitres.donneurDe(m)); return vrai.apply(null, arguments); };
        commencer(L, o, 'zz'); jouer(L, o);
        const ph = L.Histoire.lieu('phare'); B.joueur.x = ph.x; B.joueur.y = ph.y; L.Entites.indexer(); jouer(L, o);
        a(L, 'bilodeau'); jouer(L, o);
        const apresActe1 = comptes.slice();
        const cc = L.Histoire.lieu('casse_croute'); B.joueur.x = cc.x; B.joueur.y = cc.y; L.Entites.indexer(); jouer(L, o);
        a(L, 'trappeur'); finir(L, o);
        return { apresActe1: apresActe1, fin: comptes };
    }""")
    assert r == {"apresActe1": ["bilodeau"], "fin": ["bilodeau", "trappeur"]}, r


def test_un_acte_dont_le_chapitre_est_fait_est_fait(banc):
    """Une partie (ou un juge) qui ne porte que le chapitre fait : ses actes le sont, et ce qui les attend s'ouvre."""
    r = banc("function (L, o) {" + OUTILS + ZZ + """
        ouvrir(L);
        const p = L.B.partie, avant = L.Histoire.faite('zb');
        p.missionsFaites.zz = 1;
        return { avant: avant, apres: L.Histoire.faite('zb'), autre: L.Histoire.faite('p03') };
    }""")
    assert r == {"avant": False, "apres": True, "autre": False}, r
