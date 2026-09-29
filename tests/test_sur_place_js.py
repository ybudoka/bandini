"""Des missions sur place — le saut, puis la frontière, joués au banc.

Le saut : fondu au noir, l'horloge avance (jamais en arrière), on se relève au lieu, sans étoile.
"""

from tests.outils_missions import OUTILS, PLUS_LONGUES

MISSION = """
  function mission(L, slug) { return L.B.defs.missions.find(function (m) { return m.slug === slug; }); }
  function sauter(L, o, m) {
    let fini = 0;
    L.SurPlace.sauter(m, function () { fini += 1; });
    o.fondu();
    for (let k = 0; k < 400 && L.B.transition; k++) o.frame(1);
    return fini;
  }
"""


def test_le_saut_avance_l_horloge_jusqu_a_la_nuit_et_pose_au_lieu(banc):
    r = banc("function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur;
        commencer(L, o, 'q13');
        p.heure = 0.40; const jour = p.jour;
        B.recherche.etoiles = 2;
        const m = Object.assign({}, mission(L, 'q13'), { sur_place: { lieu: 'hotel', heure: 'nuit' } });
        const fini = sauter(L, o, m);
        const h = L.Histoire.lieu('hotel');
        return { fini: fini, heure: p.heure, jour: p.jour - jour, nuit: L.Monde.estNuit(p.heure),
                 loin: Math.hypot(j.x - h.x, j.y - h.y), etoiles: B.recherche.etoiles,
                 gardee: !!p.mission.gardee };
    }""")
    assert r["fini"] == 1
    assert r["nuit"] and r["jour"] == 0 and abs(r["heure"] - 0.865) < 1e-6
    assert r["loin"] < 4 * 16
    assert r["etoiles"] == 0
    assert r["gardee"]


def test_le_saut_ne_recule_jamais_l_horloge(banc):
    r = banc("function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const p = L.B.partie; commencer(L, o, 'q13');
        p.heure = 0.93; const jour = p.jour;
        sauter(L, o, Object.assign({}, mission(L, 'q13'), { sur_place: { lieu: 'hotel', heure: 'nuit' } }));
        return { heure: p.heure, jour: p.jour - jour };
    }""")
    assert r["jour"] == 0 and r["heure"] >= 0.93


def test_une_fenetre_de_demain_passe_minuit_pour_vrai(banc):
    r = banc("function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const p = L.B.partie; commencer(L, o, 'q13');
        p.heure = 0.60; const jour = p.jour;
        let nouveaux = 0; const vrai = L.Missions.nouveauJour;
        L.Missions.nouveauJour = function () { nouveaux += 1; return vrai.apply(this, arguments); };
        sauter(L, o, Object.assign({}, mission(L, 'q13'), { sur_place: { lieu: 'hotel', heure: [0.25, 0.30] } }));
        L.Missions.nouveauJour = vrai;
        return { heure: p.heure, jour: p.jour - jour, nouveaux: nouveaux };
    }""")
    assert r["jour"] == 1 and r["nouveaux"] == 1
    assert abs(r["heure"] - 0.25) < 1e-6


def test_le_saut_sort_de_la_piece_et_du_char(banc):
    r = banc("function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; commencer(L, o, 'q13');
        const porte = L.Monde.carte.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10; o.entrer(porte);
        const dedans = !!B.interieur;
        sauter(L, o, Object.assign({}, mission(L, 'q13'), { sur_place: { lieu: 'hotel', heure: 'nuit' } }));
        return { dedans: dedans, apres: !!B.interieur, char: !!j.dansVehicule };
    }""")
    assert r["dedans"] and not r["apres"] and not r["char"]


def test_un_lieu_de_bloc_fait_entrer_dans_le_bloc(banc):
    # ⚠️ La carte du bloc arrive par le réseau : le banc ne la sert qu'entre deux `await o.attendre()`
    # (le noir tient pendant ce temps, `attente` de `Jeu.transiter`).
    r = banc("async function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; commencer(L, o, 'q13');
        L.SurPlace.sauter(Object.assign({}, mission(L, 'q13'), { sur_place: { lieu: 'villa_chemin', heure: 'nuit' } }), function () {});
        for (let k = 0; k < 400 && B.transition; k++) { o.frame(1); await o.attendre(); }
        const l = L.Histoire.lieu('villa_chemin');
        return { bloc: B.bloc && B.bloc.slug, loin: l ? Math.hypot(j.x - l.x, j.y - l.y) : -1 };
    }""")
    assert r["bloc"] == "villa"
    assert 0 <= r["loin"] < 4 * 16


def test_une_mission_sans_sur_place_ne_bouge_rien(banc):
    r = banc("function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; commencer(L, o, 'q13');
        p.heure = 0.40; const x = j.x, y = j.y;
        const m = Object.assign({}, mission(L, 'q13')); delete m.sur_place;
        let fini = 0; L.SurPlace.sauter(m, function () { fini += 1; });
        return { fini: fini, heure: p.heure, bouge: j.x !== x || j.y !== y, transition: !!B.transition,
                 gardee: !!p.mission.gardee };
    }""")
    assert r == {"fini": 1, "heure": 0.40, "bouge": False, "transition": False, "gardee": True}


FRONTIERE = """
  // ⚠️ Une réplique ouverte (l'intro, une `pendant`) fige la ville et le compte avec elle : on la
  // ferme à chaque image, sinon un juge « rien ne bouge » passe à vide.
  function vivre(L, o, n) { for (let k = 0; k < n; k++) { o.frame(1); fermer(L); } }
  function garder(L, o, slug, f) {
    commencer(L, o, slug);
    L.Histoire.courante().frontiere = f;
    L.B.partie.mission.gardee = true;
    vivre(L, o, 2);
  }
  function a(L, lieu) { const l = L.Histoire.lieu(lieu), j = L.B.joueur; j.x = l.x; j.y = l.y + 24; L.Entites.indexer(); }
"""


def test_sortir_lance_le_compte_et_zero_fait_rater(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        a(L, 'hotel'); vivre(L, o, 30);
        const dedans = L.B.mission.hors || 0;
        a(L, 'bar'); vivre(L, o, 60);
        const ligne = L.SurPlace.suffixe();
        vivre(L, o, L.SurPlace.HORS_IMAGES);
        return { dedans: dedans, ligne: ligne, mission: L.B.partie.mission && L.B.partie.mission.slug,
                 echecs: L.B.partie.stats.echecs || 0 };
    }""")
    assert r["dedans"] == 0
    assert "REVIENS" in r["ligne"] and "9 S" in r["ligne"]
    assert r["mission"] is None and r["echecs"] == 1


def test_revenir_annule_le_compte(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        a(L, 'bar'); vivre(L, o, L.SurPlace.HORS_IMAGES - 60);
        a(L, 'hotel'); vivre(L, o, 2);
        const remis = L.B.mission.hors;
        a(L, 'bar'); vivre(L, o, L.SurPlace.HORS_IMAGES - 60);
        return { remis: remis, mission: !!L.B.partie.mission };
    }""")
    assert r == {"remis": 0, "mission": True}


def test_la_pause_fige_le_compte(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        a(L, 'bar'); vivre(L, o, 60);
        const avant = L.B.mission.hors;
        L.Jeu.pause(); const figee = L.B.etat; vivre(L, o, L.SurPlace.HORS_IMAGES); L.Jeu.reprendre();
        return { figee: figee, avant: avant, apres: L.B.mission.hors, mission: !!L.B.partie.mission };
    }""")
    assert r["figee"] == "pause"
    assert r["mission"] and r["avant"] > 0 and r["apres"] == r["avant"]


PIECE = """
  // Entre dans la pièce du lieu, puis remet le compte à zéro : ce qui compte, c'est DEDANS.
  function entrerChez(L, o, lieu) {
    const B = L.B, j = B.joueur;
    const porte = L.Monde.carte.portes.find(function (p) { return p.lieu === lieu; });
    j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10; o.entrer(porte);
    for (let k = 0; k < 400 && B.transition; k++) o.frame(1);
    B.mission.hors = 0;
    return !!B.interieur;
  }
"""


def test_une_piece_hors_de_la_frontiere_compte_dehors(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + PIECE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        const dedans = entrerChez(L, o, 'planque');   // la planque est au Faubourg
        vivre(L, o, 60);
        return { dedans: dedans && !!L.B.interieur, compte: L.B.mission.hors || 0 };
    }""")
    assert r["dedans"] and r["compte"] >= 55


def test_une_piece_dans_la_frontiere_ne_compte_pas(banc):
    """⚠️ Une pièce n'a pas de zones : sans la porte, on y serait « nulle part », donc dehors."""
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + PIECE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        const dedans = entrerChez(L, o, 'hotel');     // l'hôtel est aux Quais
        vivre(L, o, 60);
        return { dedans: dedans && !!L.B.interieur, compte: L.B.mission.hors || 0 };
    }""")
    assert r["dedans"] and r["compte"] == 0


def test_un_bloc_hors_du_district_compte_dehors_et_bloc_dedans(banc):
    r = banc("async function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6);
        garder(L, o, 'q13', 'bloc:villa');
        a(L, 'hotel'); vivre(L, o, 10);
        const enVille = L.SurPlace.dedans('bloc:villa');
        L.Blocs.sauter('villa'); for (let k = 0; k < 400 && L.B.transition; k++) { o.frame(1); await o.attendre(); }
        return { enVille: enVille, dansLeBloc: L.SurPlace.dedans('bloc:villa'),
                 quaisDepuisLeBloc: L.SurPlace.dedans('quais'), erablesDepuisLeBloc: L.SurPlace.dedans('erables') };
    }""")
    assert r == {"enVille": False, "dansLeBloc": True, "quaisDepuisLeBloc": False, "erablesDepuisLeBloc": True}


def test_une_partie_rechargee_garde_sa_frontiere(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        L.B.mission = null;                        // ce que fait un rechargement : B.mission se refait vide
        a(L, 'bar'); vivre(L, o, 60);
        return { compte: L.B.mission ? L.B.mission.hors || 0 : -1 };
    }""")
    assert r["compte"] > 0


def test_pas_de_frontiere_pas_de_compte(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        commencer(L, o, 'q13'); delete L.Histoire.courante().frontiere; L.B.partie.mission.gardee = true;
        a(L, 'bar'); vivre(L, o, L.SurPlace.HORS_IMAGES + 10);
        return { compte: L.B.mission.hors || 0, mission: !!L.B.partie.mission };
    }""")
    assert r == {"compte": 0, "mission": True}


def test_les_districts_hors_de_la_frontiere_se_grisent(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6);
        const avant = L.SurPlace.zonesHors(L.Monde.carte).length;
        garder(L, o, 'q13', 'quais');
        const z = L.SurPlace.zonesHors(L.Monde.carte);
        return { avant: avant, n: z.length, quais: z.some(function (q) { return q.slug === 'quais'; }),
                 faubourg: z.some(function (q) { return q.slug === 'faubourg'; }) };
    }""")
    assert r["avant"] == 0
    assert r["n"] >= 8 and not r["quais"] and r["faubourg"]


def test_les_deux_cartes_peignent_le_gris(banc):
    """Le HUD appelle bien le gris : la mini-carte en jeu, la grande carte ouverte."""
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6);
        garder(L, o, 'q13', 'quais');
        const vus = { mini: 0, carte: 0 }, sp = L.SurPlace;
        const mini = sp.dessinerMini, carte = sp.dessinerSurLaCarte;
        sp.dessinerMini = function () { vus.mini += 1; return mini.apply(this, arguments); };
        sp.dessinerSurLaCarte = function () { vus.carte += 1; return carte.apply(this, arguments); };
        L.Jeu.rendre();
        L.Jeu.ouvrirCarte(); L.Jeu.rendre(); L.Jeu.fermerCarte();
        sp.dessinerMini = mini; sp.dessinerSurLaCarte = carte;
        return vus;
    }""")
    assert r["mini"] >= 1 and r["carte"] >= 1


def test_q13_se_joue_sur_place_et_gardee(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; j.invincible = 1e6;
        faites(L, ['q06']); p.heure = 0.40;
        L.Histoire.demarrer('q13');
        for (let k = 0; k < 40 && !(p.mission && p.mission.gardee); k++) { ecouter(L); o.frame(10); if (B.transition) o.fondu(); }
        const h = L.Histoire.lieu('hotel');
        return { gardee: !!(p.mission && p.mission.gardee), nuit: L.Monde.estNuit(p.heure),
                 loin: Math.hypot(j.x - h.x, j.y - h.y), frontiere: L.Histoire.courante().frontiere };
    }""")
    assert r["gardee"] and r["nuit"] and r["loin"] < 6 * 16 and r["frontiere"] == "quais"


def test_v01_finit_au_bord_sans_rater(banc):
    """⚠️ Le dernier objectif (« RESSORS PAR LE CHEMIN ») se joue au bord du bloc : la mission est
    gagnée avant que le passage ne ramène en ville, et rien ne la fait rater après."""
    r = banc("async function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; j.invincible = 1e6;
        faites(L, ['q04']); p.heure = 0.90;
        commencer(L, o, 'v01'); p.mission.gardee = true;
        L.Blocs.sauter('villa'); for (let k = 0; k < 400 && B.transition; k++) { o.frame(1); await o.attendre(); }
        p.mission.etape = 1; L.Histoire.avancer(true);   // avancer passe a la SUIVANTE : la 2, « RESSORS »
        const depart = p.mission && p.mission.etape;
        const l = L.Histoire.lieu('villa_chemin'); j.x = l.x; j.y = l.y; L.Entites.indexer();
        const echecs = p.stats.echecs || 0;
        for (let k = 0; k < 900; k++) { o.frame(1); if (B.transition) o.fondu(); }
        return { depart: depart, faite: !!p.missionsFaites.v01, echecs: (p.stats.echecs || 0) - echecs };
    }""")
    assert r == {"depart": 2, "faite": True, "echecs": 0}


def test_v01_sortir_en_longeant_la_palissade_finit_la_mission(banc):
    """⚠️ Revue finale : la bande d'herbe à l'est mène à la sortie sans passer à trois tuiles du chemin.
    On ressort par le nord-est, comme Josée le dit — la mission doit être gagnée avant la ville, sinon la
    frontière la fait rater, la clé en poche."""
    r = banc("async function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur, T = L.TT; j.invincible = 1e6;
        faites(L, ['q04']); p.heure = 0.90;
        commencer(L, o, 'v01'); p.mission.gardee = true;
        L.Blocs.sauter('villa'); for (let k = 0; k < 400 && B.transition; k++) { o.frame(1); await o.attendre(); }
        // Le départ de la bande est AVANT l'étape : l'arrivée du bloc est à trois tuiles du chemin, et
        // l'objectif s'y ferait sur-le-champ.
        j.x = 70 * T + 8; j.y = 16 * T + 8; L.Entites.indexer();
        p.mission.etape = 1; L.Histoire.avancer(true);   // avancer passe a la SUIVANTE : la 2, « RESSORS »
        const depart = p.mission && p.mission.etape;
        const chemin = [[70, 16], [70, 18], [70, 19], [71, 20], [72, 20]];
        const echecs = p.stats.echecs || 0;
        for (let i = 0; i + 1 < chemin.length && B.bloc && !p.missionsFaites.v01; i++) {
          const a = chemin[i], b = chemin[i + 1], n = Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) * T / 4);
          for (let k = 0; k <= n && B.bloc && !p.missionsFaites.v01; k++) {
            j.x = (a[0] + (b[0] - a[0]) * k / n) * T + 8; j.y = (a[1] + (b[1] - a[1]) * k / n) * T + 8;
            L.Entites.indexer(); o.frame(1); ecouter(L);
          }
        }
        const auBord = { depart: depart, bloc: !!B.bloc, faite: !!p.missionsFaites.v01, hors: B.mission ? B.mission.hors || 0 : null };
        for (let k = 0; k < 900; k++) { o.frame(1); ecouter(L); if (B.transition) o.fondu(); }
        return { faite: !!p.missionsFaites.v01, echecs: (p.stats.echecs || 0) - echecs, auBord: auBord };
    }""")
    assert r["auBord"]["depart"] == 2
    assert {k: r[k] for k in ("faite", "echecs")} == {"faite": True, "echecs": 0}


def test_dans_une_piece_le_compte_se_lit(banc):
    """⚠️ Revue finale : la ligne d'objectif se tait dans une pièce ; le compte, lui, tourne. Il se dit."""
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + PIECE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        entrerChez(L, o, 'planque');
        vivre(L, o, 60);
        const ecrites = [], vraie = L.SurPlace.ligne;
        L.SurPlace.ligne = function () { const t = vraie.apply(this, arguments); ecrites.push(t); return t; };
        L.Jeu.rendre();
        L.SurPlace.ligne = vraie;
        return { dedans: !!L.B.interieur, ligne: L.SurPlace.ligne(null), dehors: L.SurPlace.ligne('TIENS L’HÔTEL'),
                 hud: ecrites.some(function (t) { return t && t.indexOf('RETOURNE DANS') === 0; }) };
    }""")
    assert r["dedans"]
    assert r["hud"], "le HUD écrit le compte dans la pièce"
    assert r["ligne"] and "RETOURNE DANS LES QUAIS" in r["ligne"] and "9 S" in r["ligne"]
    assert r["dehors"].startswith("TIENS L’HÔTEL — REVIENS !")
