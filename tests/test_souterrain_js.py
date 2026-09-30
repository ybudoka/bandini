"""Le grand garage souterrain, JOUÉ (docs/jalons/le-grand-garage-souterrain.md) : on descend, on se gare, on
remonte la rampe et on ressort devant le rideau de Ti-Guy ; les chars rangés y sont encore au retour et au
rechargement ; le rideau et l'ascenseur, au bouton. Voir `static/js/souterrain.js`."""

import pytest

OUTILS = """
  const TT = 16;
  function proprio(L) { L.B.partie.proprietes.garage = { jour: L.B.partie.jour, caisse: 0 }; }
  // La rue devant le rideau vidée (le trafic et les passants du hasard ne sont pas ce qu'on juge).
  function viderLaBaie(L) {
    const j = L.B.joueur, pg = L.Monde.porteDeGarage('garage'), baie = L.Monde.baieDeLaPorteDeGarage(pg);
    L.B.entites.filter(function (e) { return (e.type === 'vehicule' || e.type === 'pieton') && e !== j
        && Math.hypot(e.x - baie.x, e.y - baie.y) < 300; }).forEach(function (e) { L.Entites.retirer(e); });
    L.B.defs.conduite.trafic.vehicules_max = 0;
    return { pg: pg, baie: baie };
  }
  async function attendreLeBloc(L, o, slug) {
    for (let i = 0; i < 400 && !(L.B.bloc && L.B.bloc.slug === slug && !L.B.transition); i++) {
      o.frame(1); if (i % 10 === 0) await o.attendre();
    }
  }
  async function attendreLaVille(L, o) {
    for (let i = 0; i < 400 && (L.B.bloc || L.B.transition); i++) { o.frame(1); if (i % 10 === 0) await o.attendre(); }
  }
  // Un char à soi, garé nez au rideau, le joueur au volant.
  function auVolantDevant(L, slug, options) {
    const j = L.B.joueur, a = viderLaBaie(L);
    const v = L.Vehicules.creer(slug || 'auto', a.baie.x, a.baie.y, -Math.PI / 2,
                                Object.assign({ etat: 'stationne', couleur: '#c0392b' }, options || {}));
    j.x = v.x; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Monde.centrerCamera(j.x, j.y);
    v.aToi = true;
    return Object.assign({ v: v }, a);
  }
  // Remonter la rampe au gaz, depuis le bas, nez au nord.
  async function remonterLaRampe(L, o, v) {
    const r = L.B.bloc.def.bloc.retour;
    v.x = (r.de + r.l / 2) * TT; v.y = 5 * TT; v.angle = -Math.PI / 2; v.vitesse = 0;
    const j = L.B.joueur; j.x = v.x; j.y = v.y;
    o.touche('KeyW');
    for (let i = 0; i < 300 && !L.B.transition; i++) o.frame(1);
    o.relacher('KeyW');
    await attendreLaVille(L, o);
  }
"""


def test_on_descend_au_noir_et_on_ressort_devant_le_rideau_le_nez_vers_la_rue(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, j = B.joueur, a = auVolantDevant(L);
        L.Blocs.sauter('souterrain', null, null);
        await attendreLeBloc(L, o, 'souterrain');
        const def = B.bloc && B.bloc.def.bloc;
        const dedans = { bloc: B.bloc && B.bloc.slug, auVolant: j.dansVehicule === a.v,
                         tuile: [Math.floor(a.v.x / TT), Math.floor(a.v.y / TT)], cap: +a.v.angle.toFixed(2),
                         arrivee: def && [def.arrivee.x, def.arrivee.y], sortie: B.bloc && B.bloc.ville.sortie,
                         passage: B.bloc && B.bloc.ville.passage };
        await remonterLaRampe(L, o, a.v);
        return { dedans: dedans, apres: { bloc: !!B.bloc, auVolant: j.dansVehicule === a.v, enVille: B.entites.indexOf(a.v) >= 0,
                 x: a.v.x, y: a.v.y, cap: +a.v.angle.toFixed(2), attendu: { x: a.baie.x, y: a.baie.y + 2 * TT + 8 },
                 menu: !!B.menu } };
    }""")
    d, a = r["dedans"], r["apres"]
    assert d["bloc"] == "souterrain" and d["auVolant"], d
    assert d["tuile"] == d["arrivee"], f"on arrive au bas de la rampe : {d}"
    assert d["cap"] == 1.57, f"le nez vers l'allée (le sud) : {d}"
    assert d["passage"] is None and d["sortie"], d
    assert a["bloc"] is False and a["auVolant"] and a["enVille"], a
    assert abs(a["x"] - a["attendu"]["x"]) < 1 and abs(a["y"] - a["attendu"]["y"]) < 20, a
    assert a["cap"] == 1.57, f"on ressort le nez vers la rue : {a}"
    assert a["menu"] is False, "ressortir ne rouvre pas le menu du garage"


def test_aucune_plaque_ni_passage_en_ville_pour_le_sous_sol(banc):
    """Un sous-sol n'a pas de passage : aucune plaque en ville ne le montre, et le GPS n'y vise rien."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const b = L.Blocs.liste().find(function (q) { return q.slug === 'souterrain'; });
        o.frame(5);
        return { liste: !!b, passage: b && b.passage, seuil: b && b.seuil, bloc: !!L.B.bloc,
                 gps: L.Histoire.passageDuBloc('souterrain') };
    }""")
    assert r["liste"] and r["passage"] is None and r["seuil"] == "garage", r
    assert r["bloc"] is False and r["gps"] is None, r


GARER = """
  // Garer le char sur la case k (0 = P1), nez au mur, et en descendre.
  function garerSur(L, v, k) {
    const q = L.B.bloc.def.bloc.souterrain.cases[k], j = L.B.joueur;
    if (j.dansVehicule !== v) { j.x = v.x; j.y = v.y; L.Vehicules.monter(j, v); }
    v.x = (q.x + q.l / 2) * TT; v.y = (q.y + q.h / 2) * TT; v.angle = -Math.PI / 2; v.vitesse = 0; v.vx = 0; v.vy = 0;
    L.Vehicules.descendre(j, true);
    j.x = 15 * TT + 8; j.y = 8 * TT + 8;
    L.Entites.indexer();
  }
"""


def test_un_char_gare_sur_une_case_y_est_encore_au_retour_avec_sa_couleur_ses_pieces_et_ses_bosses(banc):
    r = banc("async function (L, o) {" + OUTILS + GARER + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, j = B.joueur, a = auVolantDevant(L, 'auto', { couleur: '#2e86de' });
        L.Garage.poser(a.v, { moteur: true }); a.v.vie = 40; a.v.vole = true;
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        garerSur(L, a.v, 2);
        // On remonte à pied par la rampe, on redescend.
        L.Jeu.sortirDuBloc(); await attendreLaVille(L, o);
        const ecrit = B.partie.souterrain.cases[2];
        const enVille = B.entites.indexOf(a.v) >= 0;
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        const q = B.bloc.def.bloc.souterrain.cases[2];
        const revenu = B.entites.filter(function (e) { return e.type === 'vehicule'; });
        const v = revenu[0];
        return { ecrit: ecrit, enVille: enVille, n: revenu.length,
                 v: v && { slug: v.slug, couleur: v.couleur, mods: v.mods, vie: v.vie, vole: v.vole, aToi: v.aToi,
                           x: v.x, y: v.y, cx: (q.x + q.l / 2) * TT, cy: (q.y + q.h / 2) * TT } };
    }""")
    assert r["ecrit"] and r["ecrit"]["couleur"] == "#2e86de" and r["ecrit"]["mods"] == {"moteur": True}, r
    assert r["enVille"] is False, "le char rangé ne remonte pas en ville"
    assert r["n"] == 1, f"un seul char, pas un double de mémoire : {r['n']}"
    v = r["v"]
    assert (v["slug"], v["couleur"], v["mods"], v["vie"], v["vole"], v["aToi"]) == ("auto", "#2e86de", {"moteur": True}, 40, True, True), v
    assert abs(v["x"] - v["cx"]) < 1 and abs(v["y"] - v["cy"]) < 1, "il revient sur SA case"


def test_un_char_laisse_dans_l_allee_ti_guy_le_gare_sur_la_premiere_case_libre(banc):
    r = banc("async function (L, o) {" + OUTILS + GARER + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, j = B.joueur, a = auVolantDevant(L);
        B.partie.souterrain.cases[0] = { slug: 'auto', sprite: undefined, couleur: '#f1c40f', vie: 100, vole: false, aToi: true };
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        // En plein milieu de l'allée, et on remonte à pied.
        a.v.x = 20 * TT; a.v.y = 9 * TT; L.Vehicules.descendre(j, true); j.x = 15 * TT + 8; j.y = 6 * TT;
        L.Jeu.sortirDuBloc(); await attendreLaVille(L, o);
        return B.partie.souterrain.cases.slice(0, 3).map(function (c) { return c && c.couleur; });
    }""")
    assert r == ["#f1c40f", "#c0392b", None], f"le jaune garde P1, le rouge de l'allée prend P2 : {r}"


def test_le_char_qu_on_remonte_quitte_le_sous_sol_et_un_vole_reste_vole(banc):
    r = banc("async function (L, o) {" + OUTILS + GARER + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, j = B.joueur;
        viderLaBaie(L);
        B.partie.souterrain.cases[4] = { slug: 'auto', couleur: '#8e44ad', vie: 90, vole: true, aToi: false };
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        const v = B.entites.find(function (e) { return e.type === 'vehicule'; });
        j.x = v.x; j.y = v.y; L.Vehicules.monter(j, v);
        await remonterLaRampe(L, o, v);
        return { case4: B.partie.souterrain.cases[4], enVille: B.entites.indexOf(v) >= 0, vole: v.vole, auVolant: j.dansVehicule === v };
    }""")
    assert r["case4"] is None, "la case se libère quand on remonte avec son char"
    assert r["enVille"] and r["auVolant"], r
    assert r["vole"] is True, "le sous-sol cache, il ne lave pas"


def test_sauvegardee_au_sous_sol_la_partie_s_y_rouvre_avec_ses_chars_et_celui_qu_on_conduisait(banc):
    r = banc("async function (L, o) {" + OUTILS + GARER + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, a = auVolantDevant(L, 'auto', { couleur: '#16a085' });
        B.partie.souterrain.cases[7] = { slug: 'camion', couleur: '#d35400', vie: 120, vole: false, aToi: true };
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        // Toujours au volant, au milieu de l'allée : on sauvegarde.
        a.v.x = 12 * TT; a.v.y = 9 * TT; B.joueur.x = a.v.x; B.joueur.y = a.v.y;
        L.Missions.sauvegarderPartie();
        B.partie = L.Sauvegarde.completer(JSON.parse(o.store['bandini-partie-v1']), B.defs);
        L.Jeu.commencer();
        await attendreLeBloc(L, o, 'souterrain');
        const chars = B.entites.filter(function (e) { return e.type === 'vehicule'; })
          .map(function (e) { return e.couleur; }).sort();
        return { bloc: B.bloc && B.bloc.slug, chars: chars, cases: B.partie.souterrain.cases.filter(Boolean).length };
    }""")
    assert r["bloc"] == "souterrain", "on se réveille au sous-sol"
    assert r["chars"] == ["#16a085", "#d35400"], f"le camion rangé ET le char qu'on conduisait : {r}"
    assert r["cases"] == 2, r


def test_garnir_ne_tire_aucun_de(banc):
    """⚠️ Un char né sans couleur tire un dé et fait glisser tout le hasard de la partie : même graine, même tirage
    suivant, qu'on ait garni le sous-sol ou pas."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B;
        B.partie.souterrain.cases[0] = { slug: 'auto', couleur: '#c0392b', vie: 100, vole: false, aToi: true };
        B.partie.souterrain.cases[1] = { slug: 'moto', couleur: '#2c3e50', vie: 60, vole: false, aToi: true };
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        const def = B.bloc.def;
        B.entites = B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        L.graine(7); L.Souterrain.garnir(def); const avec = B.rng();
        L.graine(7); const sans = B.rng();
        return { avec: avec, sans: sans };
    }""")
    assert r["avec"] == r["sans"], r


def test_une_vieille_partie_sans_sous_sol_se_complete(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const p = L.Sauvegarde.completer({ argent: 5 }, L.B.defs);
        const q = L.Sauvegarde.completer({ souterrain: { niveaux: 9, cases: [{ slug: 'auto', couleur: '#fff' }, 'x'] } }, L.B.defs);
        return { p: p.souterrain, q: q.souterrain };
    }""")
    assert r["p"] == {"niveaux": 1, "cases": [None] * 20}, r
    assert r["q"]["niveaux"] == 1 and len(r["q"]["cases"]) == 20, r
    assert r["q"]["cases"][0]["slug"] == "auto" and r["q"]["cases"][1] is None, r


RIDEAU = """
  // Garé nez au rideau, on attend le menu de Ti-Guy, et on choisit la ligne au bouton.
  function menuDuRideau(L, o) { for (let k = 0; k < 240 && !L.B.menu; k++) o.frame(1); return L.B.menu; }
  function choisir(L, o, libelle) {
    const k = L.B.menu.items.findIndex(function (i) { return i.libelle === libelle; });
    if (k < 0) return false;
    L.B.menu.curseur = k; o.tape('KeyE', 2);
    return true;
  }
"""


def test_au_rideau_descendre_au_sous_sol_au_bouton_et_le_rideau_ne_remonte_pas_pendant_le_fondu(banc):
    r = banc("async function (L, o) {" + OUTILS + RIDEAU + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, a = auVolantDevant(L);
        const menu = menuDuRideau(L, o);
        const libelles = menu ? menu.items.map(function (i) { return i.libelle; }) : [];
        choisir(L, o, 'DESCENDRE AU SOUS-SOL');
        // Le fondu : le menu ne revient pas.
        let menuPendant = false;
        for (let i = 0; i < 400 && !(B.bloc && !B.transition); i++) {
          o.frame(1); if (i % 10 === 0) await o.attendre();
          if (!B.bloc) menuPendant = menuPendant || !!B.menu;
        }
        return { libelles: libelles, bloc: B.bloc && B.bloc.slug, auVolant: B.joueur.dansVehicule === a.v,
                 menuPendant: menuPendant };
    }""")
    assert r["libelles"][:2] == ["REPARTIR", "DESCENDRE AU SOUS-SOL"], f"REPARTIR reste en tête : {r['libelles']}"
    assert r["bloc"] == "souterrain" and r["auVolant"], r
    assert r["menuPendant"] is False, "le menu de Ti-Guy s'est rouvert pendant la descente"


@pytest.mark.parametrize("cas", ["pas_proprio", "etoiles", "mission", "plein"])
def test_le_sous_sol_refuse_et_le_dit(banc, cas):
    r = banc("async function (L, o) {" + OUTILS + RIDEAU + """
        L.Jeu.commencer();
        const B = L.B, cas = '""" + cas + """';
        if (cas !== 'pas_proprio') proprio(L);
        const a = auVolantDevant(L);
        if (cas === 'etoiles') { B.recherche.etoiles = 1; B.recherche.chaleur = 20; }
        if (cas === 'mission') a.v.mission = true;
        if (cas === 'plein') for (let k = 0; k < 10; k++) B.partie.souterrain.cases[k] = { slug: 'auto', couleur: '#fff', vie: 100 };
        const menu = menuDuRideau(L, o);
        const ligne = menu && menu.items.find(function (i) { return i.libelle === 'DESCENDRE AU SOUS-SOL'; });
        if (ligne) choisir(L, o, 'DESCENDRE AU SOUS-SOL');
        for (let i = 0; i < 60; i++) o.frame(1);
        return { ligne: ligne ? { actif: ligne.actif !== false, detail: ligne.detail } : null,
                 bloc: !!B.bloc, transition: !!B.transition };
    }""")
    if cas == "mission":
        # Le char d'une mission se livre DEVANT le rideau : le menu ne s'ouvre pas du tout.
        assert r["ligne"] is None and not r["bloc"], r
        return
    assert r["ligne"] and r["ligne"]["actif"] is False, r
    attendu = {"pas_proprio": "GARAGE", "etoiles": "POLICE", "plein": "10/10"}[cas]
    assert attendu in r["ligne"]["detail"], r
    assert not r["bloc"] and not r["transition"], r
