"""Un véhicule de ligne poussé hors de son rail le reprend plus loin — il ne fait pas demi-tour.

L'autobus accroché au carrefour des Quais (passe de qualité du 2 oct. 2026) et l'arroseuse qui
tourne à 180° (Martin, 8 oct. 2026) : la même racine. `Autobus.conduire` ne passait à la tuile
suivante que posé PILE sur le centre de celle qu'il visait (à un demi-pixel). Un choc le pousse
de quelques pixels — au carrefour des Quais, son nez balaie la voie d'en face en pivotant et
touche le char arrêté à la ligne d'arrêt (73, 282) : il n'atteint plus jamais ce centre. Poussé
au-delà, la cible passe derrière lui, et il se retourne pour y revenir : le demi-tour de
l'arroseuse, puis l'autobus à contresens sur le trottoir, pris 2 612 images (graine 19 du juge
de l'abribus, trafic laissé en place).
"""

import pytest

#: Un véhicule de ligne posé sur un bout droit de sa boucle, hors de l'écran mais dans la bulle,
#: le trafic coupé ; on le pousse au-delà de la tuile qu'il vise, et de côté.
POSER = """
    function poser(L, numero, modele, options) {
        const d = L.Autobus.donnees();
        const ligne = numero === 'arroseuse' ? d.arroseuse : d.lignes.find(function (l) { return l.numero === numero; });
        L.B.defs.conduite.trafic.vehicules_max = 0;
        L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(function (e) { L.Entites.retirer(e); });
        // Un bout droit de six tuiles, sans boîte ni ligne d'arrêt, loin de l'abribus.
        const T = ligne.tuiles, n = ligne.n;
        let k = -1;
        for (let i = 0; i < n && k < 0; i++) {
            let droit = true;
            for (let m = 0; m < 6 && droit; m++) {
                const a = T[(i + m) % n], b = T[(i + m + 1) % n], c = T[(i + m + 2) % n];
                if (b[0] - a[0] !== c[0] - b[0] || b[1] - a[1] !== c[1] - b[1]) droit = false;
                if (L.Monde.fleche(b[0], b[1]) !== L.Monde.fleche(a[0], a[1])) droit = false;
                if (ligne.arretA.has((i + m) % n)) droit = false;
            }
            if (droit && i > n / 3) k = i;
        }
        const a = T[k], b = T[(k + 1) % n], dir = [b[0] - a[0], b[1] - a[1]];
        const angle = Math.atan2(dir[1], dir[0]);
        const v = L.Vehicules.creer(modele, a[0] * L.TT + 8, a[1] * L.TT + 8, angle, Object.assign({
            conducteur: 'ligne', etat: 'roule', ligne: numero, rang: 0, etape: (k + 1) % n, servi: -1, arretT: 0,
            arret: null, passager: null, demande: false, bloqueT: 0, bord: [],
        }, options));
        // Le joueur à dix tuiles, de côté : la bulle, pas l'écran.
        const j = L.B.joueur;
        j.intouchable = true;
        j.x = v.x - dir[1] * 10 * L.TT; j.y = v.y + dir[0] * 10 * L.TT;
        return { v: v, k: k, dir: dir, angle: angle, ligne: ligne };
    }
"""


@pytest.mark.parametrize("vehicule", ["autobus", "arroseuse"])
def test_pousse_au_dela_de_sa_tuile_il_ne_fait_pas_demi_tour(banc, vehicule):
    """⚠️ Poussé de six pixels au-delà de la tuile qu'il vise, et de cinq de côté : il continue
    sa route et reprend sa voie, le nez toujours vers l'avant."""
    r = banc("function (L, o) {" + POSER + """
        L.Jeu.commencer();
        L.Glace.couper(true);
        // L'arroseuse ne sort qu'entre 1 h et 5 h, et pas l'hiver quand la charrue est dehors : un soir d'été.
        L.B.partie.jour = 200; L.B.partie.heure = 2 / 24;
        const p = '%s' === 'arroseuse' ? poser(L, 'arroseuse', 'camion', { sprite: 'camion_arroseuse', arrose: true })
                                       : poser(L, 2, 'autobus', {});
        const v = p.v;
        for (let i = 0; i < 4; i++) o.frame(1);
        // Le choc : au-delà du centre de la tuile visée, et de côté.
        const vise = p.ligne.tuiles[v.etape];
        v.x = vise[0] * L.TT + 8 + p.dir[0] * 6 - p.dir[1] * 5;
        v.y = vise[1] * L.TT + 8 + p.dir[1] * 6 + p.dir[0] * 5;
        const depart = v.etape;
        let pire = 1;
        for (let i = 0; i < 90; i++) {
            o.frame(1);
            if (L.B.entites.indexOf(v) < 0) break;
            pire = Math.min(pire, Math.cos(v.angle - p.angle));
        }
        const fin = L.B.entites.indexOf(v) >= 0;
        const ecart = fin ? Math.abs((v.x - (p.ligne.tuiles[v.etape][0] * L.TT + 8)) * p.dir[1]
                                     - (v.y - (p.ligne.tuiles[v.etape][1] * L.TT + 8)) * p.dir[0]) : null;
        return { pire: pire, avance: (v.etape - depart + p.ligne.n) %% p.ligne.n, la: fin, ecart: ecart };
    }""" % vehicule)
    assert r["la"], f"le {vehicule} a quitté la ville : le juge ne mesure rien ({r})"
    assert r["pire"] > 0.5, f"le {vehicule} poussé s'est retourné vers la tuile dépassée : {r}"
    assert r["avance"] >= 3, f"le {vehicule} poussé n'a pas repris sa route : {r}"
    assert r["ecart"] < 1, f"le {vehicule} n'a pas repris sa voie : {r}"


def test_aux_quais_l_autobus_accroche_par_le_camion_d_en_face_reprend_la_rue(banc):
    """⚠️ Le carrefour des Quais tel que la suite complète l'a trouvé (graine 19 du juge de l'abribus, trafic
    laissé en place, image 4 647) : l'autobus de la ligne 2 a monté la voie (71, y) et tourné à droite dans
    la rue des Quais ; en sortant du virage, sa caisse a frôlé le camion arrêté au rouge à la ligne d'arrêt
    d'en face (73, 282) — un reste de cap de 0,02 rad, un demi-pixel — et le choc l'a poussé de treize pixels
    vers le trottoir, le nez vers sa tuile. Il y restait 2 612 images, puis se retournait. Le juge le reprend
    là, dans cet état, le camion toujours tenu par le rouge : il reprend la rue sans se retourner."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Glace.couper(true);
        const d = L.Autobus.donnees(), ligne = d.lignes.find(function (l) { return l.numero === 2; });
        const T = ligne.tuiles, n = ligne.n;
        const k = T.findIndex(function (t, i) { const a = T[(i + n - 1) % n]; return t[0] === 73 && t[1] === 283 && a[0] === 72 && a[1] === 283; });
        if (k < 0) return { trace: false };
        L.B.defs.conduite.trafic.vehicules_max = 0;
        L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(function (e) { L.Entites.retirer(e); });
        // Le camion du trafic à la ligne d'arrêt d'en face, tenu là à chaque image comme le rouge le tenait.
        // ⚠️ Pas un char garé laissé à lui-même — celui-là se laisse pousser et s'écarte ; le trafic, lui,
        // revient sur sa ligne d'arrêt, et c'est l'autobus qui cède.
        const c0 = L.Vehicules.creer('camion', 74 * L.TT + 8, 282 * L.TT + 8, Math.PI, { conducteur: null, etat: 'stationne' });
        const pa = L.Vehicules.pointDArret(c0, 73, 282, [-1, 0]);
        // L'autobus juste après le choc, tel que la partie l'avait.
        const bus = L.Vehicules.creer('autobus', 1171, 4549, 5.29, {
            conducteur: 'ligne', etat: 'roule', ligne: 2, rang: 0, etape: k, servi: -1, arretT: 0,
            arret: null, passager: null, demande: false, bloqueT: 0, bord: [], sens: '>',
        });
        bus.vitesse = 0.85;
        const j = L.B.joueur;
        j.intouchable = true; j.x = 60 * L.TT; j.y = 270 * L.TT;
        let pire = 1, images = 0;
        for (let i = 0; i < 900; i++) {
            c0.x = pa.x; c0.y = pa.y; c0.angle = Math.PI; c0.vitesse = 0; c0.vx = 0; c0.vy = 0;
            o.frame(1); images = i;
            if (L.B.entites.indexOf(bus) < 0) break;
            pire = Math.min(pire, Math.cos(bus.angle));
            if (Math.floor(bus.x / L.TT) >= 79) break;
        }
        return { trace: true, la: L.B.entites.indexOf(bus) >= 0, tx: Math.floor(bus.x / L.TT), ty: Math.floor(bus.y / L.TT),
                 y: Math.round(bus.y), pire: pire, images: images, camion: [Math.round(c0.x), Math.round(c0.y)] };
    }""")
    assert r["trace"], "la ligne 2 ne tourne plus de (72, 283) à (73, 283) aux Quais : le juge ne mesure rien"
    assert r["la"], f"l'autobus a quitté la ville (le chien de garde) : il était pris ({r})"
    assert r["camion"] == [1188, 4520], f"le camion n'est pas à sa ligne d'arrêt : le juge ne mesure rien ({r})"
    assert r["pire"] > 0, f"l'autobus s'est retourné dans le carrefour : {r}"
    assert r["tx"] >= 79 and r["ty"] == 283, f"l'autobus n'a pas repris la rue des Quais : {r}"
