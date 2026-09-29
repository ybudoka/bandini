"""Des missions sur place — le saut, puis la frontière, joués au banc.

Le saut : fondu au noir, l'horloge avance (jamais en arrière), on se relève au lieu, sans étoile.
"""

from tests.outils_missions import OUTILS

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
