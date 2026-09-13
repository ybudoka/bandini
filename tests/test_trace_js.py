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
