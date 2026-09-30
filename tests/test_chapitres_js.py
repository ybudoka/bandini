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
