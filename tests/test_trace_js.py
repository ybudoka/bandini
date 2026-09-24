"""Le mode TRACE : le jeu dessine les trajets du trafic et se surveille lui-meme.

Idee de Martin : quand les chars restent pris dans un croisement, plutot que
de le deviner au banc, le jeu note l'anomalie sur place (chien de garde,
tour en rond, hors voie) et garde le trajet. Ici, on verifie que la
surveillance voit ce qu'elle doit voir — et que le trafic normal ne la
declenche pas.
"""


def test_le_trafic_normal_ne_declenche_aucune_anomalie(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(5);
        L.B.options.trace = true;
        L.Vehicules.monter(L.B.joueur, o.char('auto', 0, 0, 0));   // en char, immobile : le trafic vit autour
        o.frame(2400);
        const bilan = L.Vehicules.bilanTrace();
        return { bilan: bilan, anomalies: L.B.trace.anomalies.map(function (a) { return a.quoi + ' ' + a.tx + ',' + a.ty + ' ' + a.etat; }),
                 traces: L.B.entites.filter(function (v) { return v.conducteur === 'trafic' && v.trace && v.trace.length > 10; }).length };
    }""")
    assert r["bilan"]["chars"] > 0 and r["traces"] > 0, "les chars du trafic ont un trajet"
    assert r["anomalies"] == [], "le trafic normal a declenche la surveillance"


def test_la_trace_voit_un_char_hors_voie_et_le_chien_de_garde(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.options.trace = true;
        const j = L.B.joueur;
        // ⚠️ Le char se pose a 32 px du joueur et roule : il l'ecrasait, et
        // l'hopital FIGE la ville le temps de son fondu (`Jeu.transiter`) —
        // 120 images de surveillance qui ne surveillaient plus rien. Ce test
        // juge le trafic, pas la sante du joueur : il est intouchable ici.
        j.invincible = 9999;
        // Un char de trafic pose sur le trottoir, sans voie a suivre.
        const v = o.char('auto', 32, 0, 0);
        v.conducteur = 'trafic'; v.etat = 'roule';
        L.Entites.indexer();
        o.frame(120);
        const horsVoie = L.B.trace.anomalies.filter(function (a) { return a.quoi === 'HORS VOIE' && a.id === v.id; }).length;
        // Le chien de garde l'a-t-il deplace ? On force le compteur pour ne pas attendre dix secondes.
        v.immobileT = 700; v.vx = 0; v.vy = 0;
        o.frame(30);
        const chien = L.B.trace.anomalies.filter(function (a) { return a.quoi === 'CHIEN DE GARDE' && a.id === v.id; }).length;
        const a = L.B.trace.anomalies[0];
        L.Jeu.rendre();                                  // le dessin ne plante pas
        return { horsVoie: horsVoie, chien: chien, points: a ? a.points.length : 0, etat: a ? a.etat : null,
                 bilan: L.Vehicules.bilanTrace() };
    }""")
    assert r["horsVoie"] == 1, "un char de trafic hors de la chaussee doit etre releve"
    assert r["chien"] == 1, "le chien de garde qui se declenche est une anomalie a montrer"
    assert r["points"] > 0 and r["etat"], "l'anomalie garde le trajet et l'etat du char"
    assert r["bilan"]["total"] >= 2


def test_l_adresse_allume_la_trace(banc):
    r = banc("""function (L, o) {
        return { trace: L.B.options.trace, perf: !!L.B.options.perf };
    }""")
    assert r["trace"] is False, "sans ?trace=1, la trace reste eteinte"


def test_de_chaque_tuile_de_chaque_boite_la_cascade_sort(banc):
    """⚠️ Le juge des boites. Depuis CHAQUE tuile de CHAQUE croisement, dans les
    quatre sens, avec chacune des trois preferences (tout droit, a droite, a
    gauche), la cascade de `prochaineCible` doit rejoindre une voie en moins
    de 40 pas. Une preference relative relue a chaque tuile faisait faire le
    tour de la boite sans fin (1858 departs sur 21 744) — Martin l'a vu en
    jouant, deux fois."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, TT = L.TT;
        const PREFERENCES = [0.1, 0.6, 0.9];        // le tirage qui donne tout droit / a droite / a gauche
        const ANGLE = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        const rates = [];
        let boites = 0, departs = 0;
        for (const inter of c.def.intersections) {
            boites++;
            for (let ty = inter.y - 2; ty < inter.y + inter.h + 2; ty++) for (let tx = inter.x - 2; tx < inter.x + inter.l + 2; tx++) {
                if (L.Monde.fleche(tx, ty) !== '+') continue;
                for (const sens0 of ['>', '<', '^', 'v']) for (const tirage of PREFERENCES) {
                    departs++;
                    L.B.rng = function () { return tirage; };
                    const v = { x: tx * TT + 8, y: ty * TT + 8, sens: sens0, sortie: null, angle: ANGLE[sens0], attendFeu: false,
                                attenteBoite: 0, stopT: undefined, enBoite: null, poursuite: false, vitesse: 1, def: { vitesse_max: 4 } };
                    const chemin = [tx + ',' + ty + sens0];
                    let sorti = false;
                    for (let pas = 0; pas < 40; pas++) {
                        const cible = L.Vehicules.prochaineCible(v);
                        if (!cible) break;
                        v.x = cible.x; v.y = cible.y;
                        const f = L.Monde.fleche(cible.tx, cible.ty);
                        chemin.push(cible.tx + ',' + cible.ty + v.sens);
                        if (f === '>' || f === '<' || f === '^' || f === 'v') { sorti = true; break; }
                        if (f !== '+') break;
                    }
                    if (!sorti && rates.length < 5) rates.push(chemin.slice(0, 10).join(' '));
                    if (!sorti) departs += 1000;                  // un rate se voit dans le compte
                }
            }
        }
        return { boites: boites, departs: departs, rates: rates };
    }""")
    assert r["boites"] >= 40, "la carte du banc a bien des dizaines de croisements"
    assert r["rates"] == [], f"des departs qui tournent en rond : {r['rates']}"
    assert r["departs"] < 100000


def test_d_une_entree_de_boite_un_seul_virage_pris_au_plus_tot(banc):
    """⚠️ Le juge des coins en L (21 sept. 2026, retour de Martin au coin des Quais :
    « améliore les virages pour les situations complexes comme ça »). Le juge
    d'avant ne demandait qu'une chose : SORTIR. Un char peut sortir et avoir raté
    son virage : dans un coin en L, celui qui descendait du nord en voulant « tout
    droit » traversait jusqu'à la rangée du bord de l'eau, n'y trouvait rien, et
    zigzaguait — ouest, nord, ouest. 24 entrées de boîte sur 2 238 le faisaient,
    toutes dans les onze coins en L.

    Depuis CHAQUE ENTRÉE de chaque boîte (une voie ou une ligne d'arrêt qui y
    mène), avec les trois préférences, en poursuite (le joueur loin dans chacune
    des quatre directions), et à trois heures (les deux pointes et midi) :

    1. on sort ;
    2. UN virage au plus — deux, c'est un zigzag ;
    3. pris à la PREMIÈRE tuile d'où il mène : le char qui file au fond de la
       boîte avant de tourner a raté son virage, même s'il n'en fait qu'un ;
    4. et au pied d'un T, « tout droit » tourne À GAUCHE, comme il l'a toujours
       fait : le correctif ne déplace pas le trafic de la ville."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, TT = L.TT;
        const PREFERENCES = { droit: 0.1, droite: 0.6, gauche: 0.9, N: 'N', S: 'S', E: 'E', O: 'O' };
        const PAS = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] };
        const ANGLE = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        const GAUCHE = { '>': '^', '^': '<', '<': 'v', 'v': '>' };
        const BRAS = { '>': 'E', '<': 'O', '^': 'N', 'v': 'S' };
        // La meme lecture que `peutSortir`, refaite ici : le juge ne se fie pas a
        // la fonction qu'il juge pour dire ou le virage devait se prendre.
        const sortDe = function (x, y, sens) {
            const q = PAS[sens];
            for (let i = 0; i < 9; i++) {
                x += q[0]; y += q[1];
                const f = L.Monde.fleche(x, y);
                if (f === sens) return true;
                if (f !== '+') return false;
            }
            return false;
        };
        const fautes = [], coinsEnL = new Set();
        let entrees = 0, piedsDeT = 0;
        for (const heure of [0.35, 0.5, 0.75]) {
            L.B.partie.heure = heure;
            for (const inter of c.def.intersections) {
                if (inter.bras.length === 2 && inter.bras !== 'NS' && inter.bras !== 'OE') coinsEnL.add(inter.x + ',' + inter.y);
                for (let ty = inter.y - 2; ty < inter.y + inter.h + 2; ty++) for (let tx = inter.x - 2; tx < inter.x + inter.l + 2; tx++) {
                    if (L.Monde.fleche(tx, ty) !== '+') continue;
                    for (const sens0 of ['>', '<', '^', 'v']) {
                        const p = PAS[sens0], bx = tx - p[0], by = ty - p[1];
                        const fb = L.Monde.fleche(bx, by);
                        if (!(fb === sens0 || (fb === 'S' && L.Monde.sensArret(bx, by) === sens0))) continue;
                        for (const nom in PREFERENCES) {
                            entrees++;
                            const pref = PREFERENCES[nom], poursuite = typeof pref === 'string';
                            L.B.rng = function () { return poursuite ? 0.5 : pref; };
                            const mx = (inter.x + inter.l / 2) * TT, my = (inter.y + inter.h / 2) * TT;
                            L.B.joueur.x = mx + (pref === 'E' ? 3000 : pref === 'O' ? -3000 : 0);
                            L.B.joueur.y = my + (pref === 'S' ? 3000 : pref === 'N' ? -3000 : 0);
                            const v = { x: tx * TT + 8, y: ty * TT + 8, sens: sens0, sortie: null, angle: ANGLE[sens0],
                                        attendFeu: false, attenteBoite: 0, stopT: undefined, enBoite: null, poursuite: poursuite,
                                        vitesse: 1, def: { vitesse_max: 4, longueur: 28 } };
                            const chemin = [bx + ',' + by + sens0, tx + ',' + ty + sens0];
                            let x = tx, y = ty, sens = sens0, virages = 0, tourne = null, sortie = null;
                            for (let n = 0; n < 40 && !sortie; n++) {
                                const cible = L.Vehicules.prochaineCible(v);
                                if (!cible) break;
                                if (v.sens !== sens) { virages++; if (!tourne) tourne = { x: x, y: y, sens: v.sens }; sens = v.sens; }
                                v.x = cible.x; v.y = cible.y; x = cible.tx; y = cible.ty;
                                chemin.push(x + ',' + y + v.sens);
                                if (PAS[L.Monde.fleche(x, y)]) sortie = L.Monde.fleche(x, y);
                            }
                            let tot = null;                      // la tuile d'ou le virage menait deja
                            if (tourne) {
                                for (let ax = tx, ay = ty; !(ax === tourne.x && ay === tourne.y) && L.Monde.fleche(ax, ay) === '+'; ax += p[0], ay += p[1]) {
                                    if (sortDe(ax, ay, tourne.sens)) { tot = ax + ',' + ay; break; }
                                }
                            }
                            const tDuPied = inter.bras.length === 3 && inter.bras.indexOf(BRAS[sens0]) < 0
                                            && inter.bras.indexOf({ '>': 'O', '<': 'E', '^': 'S', 'v': 'N' }[sens0]) >= 0;
                            if (tDuPied && nom === 'droit' && heure === 0.5) piedsDeT++;
                            const faute = !sortie ? 'ne sort pas'
                                : virages > 1 ? virages + ' virages'
                                : tot ? 'tourne trop loin (il pouvait des ' + tot + ')'
                                : tDuPied && nom === 'droit' && heure === 0.5 && sortie !== GAUCHE[sens0] ? 'au pied du T, tout droit ne va plus a gauche'
                                : null;
                            if (faute && fautes.length < 8) fautes.push(inter.x + ',' + inter.y + ' ' + inter.bras + ' ' + nom + ' ' + heure + 'j : ' + faute + ' — ' + chemin.join(' '));
                            else if (faute) fautes.push('…');
                        }
                    }
                }
            }
        }
        return { entrees: entrees, coinsEnL: coinsEnL.size, piedsDeT: piedsDeT, fautes: fautes.length, exemples: fautes.slice(0, 8) };
    }""")
    assert r["coinsEnL"] >= 6, "la carte du banc a ses coins en L : sans eux, ce juge ne juge rien"
    assert r["piedsDeT"] >= 50, "la carte du banc a ses T"
    assert r["entrees"] >= 10000
    assert r["fautes"] == 0, f"{r['fautes']} entrées de boîte ratent leur virage : {r['exemples']}"
