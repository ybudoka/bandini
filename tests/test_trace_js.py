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
