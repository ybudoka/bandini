"""Le −2 du garage souterrain, JOUÉ (docs/jalons/le-grand-garage-souterrain.md, vague 2) : la grille tant qu'il n'est
pas acheté, AGRANDIR LE SOUS-SOL au comptoir de Ti-Guy, la rampe intérieure au volant dans les deux sens, P11 à P20
rangées et garnies à part du −1, l'ascenseur à trois arrêts, et les sons."""

from tests.test_souterrain_js import OUTILS

PLUS = """
  // Pousser au gaz contre la rampe est du niveau où l'on est, nez à l'est, depuis le milieu de l'allée.
  async function prendreLaRampe(L, o, v) {
    const j = L.B.joueur;
    v.x = 12 * TT; v.y = 7 * TT + 8; v.angle = 0; v.vitesse = 0; j.x = v.x; j.y = v.y;
    o.touche('KeyW');
    for (let i = 0; i < 200 && !L.B.transition; i++) o.frame(1);
    o.relacher('KeyW');
    const parti = !!L.B.transition;
    for (let i = 0; i < 400 && L.B.transition; i++) { o.frame(1); if (i % 10 === 0) await o.attendre(); }
    return parti;
  }
  async function enBas(L, o, niveaux, avant) {
    L.Jeu.commencer(); while (L.B.menu) L.Hud.fermerMenu();
    proprio(L); L.B.partie.souterrain.niveaux = niveaux;
    if (avant) avant(L.B.partie);
    const a = auVolantDevant(L);
    L.Blocs.sauter('souterrain', null, null);
    await attendreLeBloc(L, o, 'souterrain');
    return a.v;
  }
"""


def test_la_grille_ferme_la_rampe_tant_que_le_moins_deux_n_est_pas_achete(banc):
    r = banc("async function (L, o) {" + OUTILS + PLUS + """
        const v = await enBas(L, o, 1);
        const parti = await prendreLaRampe(L, o, v);
        let peinte = 0; const t = L.Atlas.texte;
        L.Atlas.texte = function (ctx, s) { if (s === '−2') peinte++; return t.apply(this, arguments); };
        L.Jeu.rendre(); L.Atlas.texte = t;
        return { parti: parti, bloc: L.B.bloc && L.B.bloc.slug, peinte: peinte };
    }""")
    assert r == {"parti": False, "bloc": "souterrain", "peinte": 1}, r


def test_agrandir_au_comptoir_ouvre_le_moins_deux(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); while (L.B.menu) L.Hud.fermerMenu();
        const p = L.B.partie, prix = L.B.defs.economie.tarifs.sous_sol_2;
        const sansGarage = L.Souterrain.itemAgrandir();
        proprio(L);
        p.argent = prix - 1;
        const pauvre = L.Souterrain.itemAgrandir();
        p.argent = prix + 500;
        const item = L.Souterrain.itemAgrandir();
        item.faire();
        return { prix: prix, sansGarage: sansGarage, pauvre: pauvre && pauvre.actif, niveaux: p.souterrain.niveaux,
                 argent: p.argent, apres: L.Souterrain.itemAgrandir(), ouvertes: L.Souterrain.ouvertes() };
    }""")
    assert r["prix"] == 10000 and r["sansGarage"] is None and r["pauvre"] is False, r
    assert r["niveaux"] == 2 and r["argent"] == 500 and r["apres"] is None and r["ouvertes"] == 20, r


def test_au_comptoir_de_ti_guy_la_ligne_y_est(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); while (L.B.menu) L.Hud.fermerMenu();
        proprio(L); L.B.partie.argent = 20000;
        const porte = L.Monde.carte.portes.find(function (q) { return q.lieu === 'garage' && q.interieur; });
        o.entrer(porte);
        const items = []; L.Missions.menuGarage(items);
        return items.map(function (i) { return i.libelle; });
    }""")
    assert "AGRANDIR LE SOUS-SOL" in r, r


def test_la_rampe_interieure_au_volant_dans_les_deux_sens(banc):
    r = banc("async function (L, o) {" + OUTILS + PLUS + """
        const v = await enBas(L, o, 2), j = L.B.joueur;
        let rampes = 0; const s = L.Son.SFX.rampe; L.Son.SFX.rampe = function () { rampes++; return s.apply(this, arguments); };
        const parti = await prendreLaRampe(L, o, v);
        const enBas2 = { bloc: L.B.bloc && L.B.bloc.slug, auVolant: j.dansVehicule === v, cap: +v.angle.toFixed(2),
                         tuile: [Math.floor(v.x / TT), Math.floor(v.y / TT)] };
        const remonte = await prendreLaRampe(L, o, v);
        return { parti: parti, enBas2: enBas2, remonte: remonte, bloc: L.B.bloc && L.B.bloc.slug,
                 auVolant: j.dansVehicule === v, rampes: rampes };
    }""")
    assert r["parti"] and r["enBas2"]["bloc"] == "souterrain_2" and r["enBas2"]["auVolant"], r
    assert r["enBas2"]["cap"] == 3.14 and r["enBas2"]["tuile"] == [14, 7], "on arrive au bas de la rampe, tourné vers l'allée"
    assert r["remonte"] and r["bloc"] == "souterrain" and r["auVolant"] and r["rampes"] == 2, r


def test_p11_a_p20_se_rangent_et_se_garnissent_a_part_du_moins_un(banc):
    r = banc("async function (L, o) {" + OUTILS + PLUS + """
        // Une moto sur P1 (au −1), un camion sur P16 (au −2), rangés avant de descendre.
        const v = await enBas(L, o, 2, function (p) {
            p.souterrain.cases[0] = { slug: 'moto', couleur: '#2c3e50', vie: 60, vole: false, aToi: true };
            p.souterrain.cases[15] = { slug: 'camion', couleur: '#d35400', vie: 120, vole: false, aToi: true };
        });
        const j = L.B.joueur, p = L.B.partie;
        await prendreLaRampe(L, o, v);
        // Au −2 : le camion de P16 dort sur sa case.
        const def = L.B.bloc.def.bloc, q16 = def.souterrain.cases.find(function (q) { return q.n === 16; });
        const camion = L.B.entites.find(function (e) { return e.type === 'vehicule' && e.slug === 'camion'; });
        const garni = !!camion && Math.floor(camion.x / TT) >= q16.x && Math.floor(camion.x / TT) < q16.x + q16.l;
        // On laisse SON char sur P13, et l'on remonte à pied par la rampe.
        const q13 = def.souterrain.cases.find(function (q) { return q.n === 13; });
        L.Vehicules.descendre(j, true);
        v.x = (q13.x + 1) * TT; v.y = (q13.y + 1.5) * TT; v.vitesse = 0;
        j.x = 15 * TT + 8; j.y = 7 * TT + 8; j.angle = 0; L.Entites.indexer();
        o.touche('KeyD');
        for (let i = 0; i < 200 && !L.B.transition; i++) o.frame(1);
        o.relacher('KeyD');
        for (let i = 0; i < 400 && L.B.transition; i++) { o.frame(1); if (i % 10 === 0) await o.attendre(); }
        return { garni: garni, bloc: L.B.bloc && L.B.bloc.slug, p1: p.souterrain.cases[0] && p.souterrain.cases[0].slug,
                 p13: p.souterrain.cases[12] && p.souterrain.cases[12].couleur, p16: p.souterrain.cases[15] && p.souterrain.cases[15].slug };
    }""")
    assert r["garni"], f"le camion de P16 n'est pas sur sa case au −2 : {r}"
    assert r["bloc"] == "souterrain", r
    assert r == {"garni": True, "bloc": "souterrain", "p1": "moto", "p13": "#c0392b", "p16": "camion"}, r


def test_l_ascenseur_dessert_trois_arrets_une_fois_le_moins_deux_ouvert(banc):
    r = banc("async function (L, o) {" + OUTILS + PLUS + """
        const v = await enBas(L, o, 2), j = L.B.joueur;
        L.Vehicules.descendre(j, true);
        const s = L.B.bloc.def.bloc.souterrain.ascenseur;
        j.x = (s.x + 1) * TT; j.y = s.y * TT + 8; L.Entites.indexer();
        let dings = 0; const d = L.Son.SFX.ascenseur; L.Son.SFX.ascenseur = function () { dings++; return d.apply(this, arguments); };
        L.Souterrain.agir(j);
        const menu = L.B.menu && L.B.menu.items.map(function (i) { return [i.libelle, i.actif !== false]; });
        L.B.menu.items[2].faire();
        for (let i = 0; i < 400 && (L.B.transition || !L.B.bloc || L.B.bloc.slug !== 'souterrain_2'); i++) { o.frame(1); if (i % 10 === 0) await o.attendre(); }
        const s2 = L.B.bloc.def.bloc.souterrain.ascenseur;
        return { menu: menu, bloc: L.B.bloc.slug, devant: Math.floor(j.y / TT) === s2.y, dings: dings };
    }""")
    assert r["menu"] == [["GARAGE", True], ["SOUS-SOL −1", False], ["SOUS-SOL −2", True]], r
    assert r["bloc"] == "souterrain_2" and r["devant"] and r["dings"] == 1, r


def test_un_seul_niveau_l_ascenseur_reste_un_aller_simple(banc):
    r = banc("async function (L, o) {" + OUTILS + PLUS + """
        const v = await enBas(L, o, 1), j = L.B.joueur;
        L.Vehicules.descendre(j, true);
        const s = L.B.bloc.def.bloc.souterrain.ascenseur;
        j.x = (s.x + 1) * TT; j.y = s.y * TT + 8; L.Entites.indexer();
        L.Souterrain.agir(j);
        const menu = !!L.B.menu;
        await attendreLaVille(L, o);
        return { menu: menu, piece: L.B.interieur && L.B.interieur.slug };
    }""")
    assert r == {"menu": False, "piece": "garage"}, r


def test_les_neons_bourdonnent_en_bas_seulement(banc):
    r = banc("async function (L, o) {" + OUTILS + PLUS + """
        const vus = []; const n = L.Son.SFX.neons;
        L.Son.SFX.neons = function (v) { vus.push(v); return n.apply(this, arguments); };
        L.Jeu.commencer(); while (L.B.menu) L.Hud.fermerMenu();
        o.frame(2);
        const enVille = vus.slice(-1)[0];
        await enBas(L, o, 1);
        o.frame(2);
        return { enVille: enVille, enBas: vus.slice(-1)[0] };
    }""")
    assert r == {"enVille": 0, "enBas": 1}, r


def test_une_partie_endormie_au_moins_deux_s_y_reveille(banc):
    r = banc("async function (L, o) {" + OUTILS + PLUS + """
        await enBas(L, o, 2);
        L.Jeu.revenirEnVille();
        L.Blocs.reprendre({ slug: 'souterrain_2', x: 8 * TT, y: 7 * TT + 8 });
        await attendreLeBloc(L, o, 'souterrain_2');
        return { bloc: L.B.bloc && L.B.bloc.slug, sortie: !!(L.B.bloc && L.B.bloc.ville.sortie) };
    }""")
    assert r == {"bloc": "souterrain_2", "sortie": True}, r
