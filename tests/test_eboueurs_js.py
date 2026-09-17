"""Les éboueurs (M12) au banc : le camion de la tournée, ses bacs, son bras.

⚠️ On ne fait pas attendre le banc une matinée de jeu : l'horaire est une fonction de
l'heure (`Autobus.parcoursDuJour`), et `AMENER` règle l'heure pour que le camion soit
à quelques tuiles EN AMONT d'un bac — hors de l'écran, dans la bulle — et le joueur à
vingt-deux tuiles du trottoir.
"""

AMENER = """
    function amener(L, rang, avance) {
        L.Jeu.commencer();
        const T = L.Autobus.donnees().tournee, h = T.horaire;
        const pt = T.points[rang];
        const idx = (pt.i - avance + T.n) % T.n;
        const parJour = L.B.defs.economie.jour_secondes * 60;
        L.B.partie.jour = 2;
        L.B.partie.heure = h.debut + (idx * L.TT) / (parJour * h.vitesse_px);
        const tuile = T.tuiles[pt.i], suivante = T.tuiles[(pt.i + 1) % T.n];
        const dx = suivante[0] - tuile[0], dy = suivante[1] - tuile[1];
        // Le joueur à vingt-deux tuiles du bac, du côté du trottoir : hors de l'écran.
        const j = L.B.joueur;
        j.intouchable = true;
        const loin = { x: pt.x * L.TT + 8 - dy * 22 * L.TT, y: pt.y * L.TT + 8 + dx * 22 * L.TT };
        j.x = loin.x; j.y = loin.y; L.Monde.centrerCamera(j.x, j.y);
        return { T: T, h: h, pt: pt, j: j, loin: loin };
    }
    function tenir(L, a) { a.j.x = a.loin.x; a.j.y = a.loin.y; L.Monde.centrerCamera(a.j.x, a.j.y); }
    function camion(L) { return L.B.entites.find(function (v) { return v.type === 'vehicule' && v.collecte; }) || null; }
"""


def test_le_camion_nait_hors_de_l_ecran_aux_heures_de_la_collecte(banc):
    """Le matin, hors de l'écran ; ⚠️ pas à l'écran quand la caméra a pris de
    l'avance (au volant) ; et l'après-midi, pas du tout — le joueur posé là où
    l'horaire mettrait le camion s'il roulait encore."""
    r = banc("function (L, o) {" + AMENER + """
        // Où l'horaire met le camion à cette heure, qu'il soit en service ou non.
        function placeDuCamion(T, h, heure) {
            const parJour = L.B.defs.economie.jour_secondes * 60;
            const s = ((heure - h.debut) * parJour * h.vitesse_px) % T.longueurPx;
            const i = Math.floor(s / L.TT) % T.n, t = T.tuiles[i], u = T.tuiles[(i + 1) % T.n];
            return { x: t[0] * L.TT + 8, y: t[1] * L.TT + 8, dx: u[0] - t[0], dy: u[1] - t[1] };
        }
        const a = amener(L, 5, 6);
        // 1. La caméra en avance, posée sur la place du camion : il ne naît pas.
        const ici = placeDuCamion(a.T, a.h, L.B.partie.heure);
        let sousLesYeux = false;
        for (let i = 0; i < 90; i++) { o.frame(1); a.j.x = a.loin.x; a.j.y = a.loin.y; L.Monde.centrerCamera(ici.x, ici.y); if (camion(L)) sousLesYeux = true; }
        // 2. La caméra rendue au joueur : il naît, hors de l'écran.
        let v = null, naissance = null;
        for (let i = 0; i < 120 && !v; i++) {
            o.frame(1); tenir(L, a);
            v = camion(L);
            if (v) naissance = { visible: L.Entites.visibleAEcran(v.x, v.y, 0), sprite: v.sprite, conducteur: v.conducteur };
        }
        // 3. L'après-midi, le joueur là où le camion serait : aucun ne naît.
        if (v) L.Entites.retirer(v);
        L.B.partie.heure = 0.7;
        const la = placeDuCamion(a.T, a.h, 0.7);
        a.loin = { x: la.x - la.dy * 22 * L.TT, y: la.y + la.dx * 22 * L.TT };
        let apres = false;
        for (let i = 0; i < 120; i++) { o.frame(1); tenir(L, a); if (camion(L)) apres = true; }
        return { sousLesYeux: sousLesYeux, naissance: naissance, apres: apres };
    }""")
    assert r["sousLesYeux"] is False, "la caméra sur la place du camion, et il y est né"
    assert r["naissance"], "aucun camion n'est né pendant la collecte"
    assert r["naissance"]["visible"] is False, "le camion est né sous les yeux"
    assert r["naissance"]["sprite"] == "camion_benne" and r["naissance"]["conducteur"] == "ligne"
    assert r["apres"] is False, "un camion de collecte l'après-midi"


def test_le_camion_s_arrete_au_bac_le_leve_le_vide_et_le_repose(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, 5, 6);
        let v = null, bac = null, arret = null;
        for (let i = 0; i < 3000 && !arret; i++) {
            o.frame(1); tenir(L, a);
            v = v || camion(L);
            bac = bac || L.Autobus.bacDe(a.pt.k);
            if (v && v.arretT > 0 && v.arret === a.pt.k) arret = i;
        }
        if (!arret) return { v: !!v, bac: !!bac, arret: false };
        const pied = { x: bac.x, y: bac.y }, plein = !bac.vide;
        let haut = 0, duree = 0;
        for (let i = 0; i < 400 && v.arretT > 0; i++) { o.frame(1); tenir(L, a); haut = Math.max(haut, bac.altitude || 0); duree++; }
        return { v: true, bac: true, arret: true, plein: plein, haut: haut, duree: duree,
                 repose: Math.hypot(bac.x - pied.x, bac.y - pied.y), altitude: bac.altitude, vide: bac.vide,
                 arretImages: a.h.arret_images, sePasse: v.vitesse };
    }""")
    assert r["v"] and r["bac"], r
    assert r["arret"], "le camion ne s'est pas arrêté au bac"
    assert r["plein"], "le bac était déjà vide : le juge ne mesure rien"
    assert r["duree"] >= r["arretImages"] - 2, f"arrêté {r['duree']} images seulement"
    assert r["haut"] >= 15, f"le bac n'a pas quitté le trottoir ({r['haut']} px)"
    assert r["repose"] < 0.5 and r["altitude"] == 0, "le bac n'est pas reposé là où il était"
    assert r["vide"] is True


def test_pas_d_arret_devant_un_bac_vide_ou_absent(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, 5, 6);
        for (let i = 0; i < 60; i++) { o.frame(1); tenir(L, a); }
        const bac = L.Autobus.bacDe(a.pt.k);
        const plein = L.Autobus.dureeDeCollecte(a.pt.k);
        bac.vide = true;
        const vide = L.Autobus.dureeDeCollecte(a.pt.k);
        // Un bac défoncé par un char : il n'y a plus rien à lever.
        bac.vide = false;
        L.Entites.briser(bac);
        const defonce = L.Autobus.dureeDeCollecte(a.pt.k);
        L.Entites.retirer(bac);
        return { plein: plein, vide: vide, defonce: defonce, brise: !!bac.brise,
                 absent: L.Autobus.dureeDeCollecte(a.pt.k), images: a.h.arret_images };
    }""")
    assert r["plein"] == r["images"]
    assert r["brise"] is True, "le juge n'a pas défoncé le bac"
    assert r["vide"] == 0 and r["absent"] == 0 and r["defonce"] == 0


def test_les_bacs_sortent_le_matin_et_rentrent_l_apres_midi_hors_de_l_ecran(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, 5, 6);
        // ⚠️ La caméra en avance, posée sur la place du bac : il ne sort pas sous les yeux.
        const place = L.Autobus.placeDuBac(a.pt), qx = place.x, qy = place.y;
        let sousLesYeux = false;
        for (let i = 0; i < 70; i++) { o.frame(1); a.j.x = a.loin.x; a.j.y = a.loin.y; L.Monde.centrerCamera(qx, qy); if (L.Autobus.bacDe(a.pt.k)) sousLesYeux = true; }
        const naissances = [];
        const vus = new Set();
        for (let i = 0; i < 90; i++) {
            o.frame(1); tenir(L, a);
            for (const e of L.B.entites) if (e.bac && !vus.has(e)) { vus.add(e); naissances.push(L.Entites.visibleAEcran(e.x, e.y, 0)); }
        }
        const matin = L.B.entites.filter(function (e) { return e.bac; }).length;
        // L'après-midi : ceux qu'on ne voit pas rentrent ; celui qu'on regarde reste.
        const regarde = L.B.entites.find(function (e) { return e.bac; });
        L.B.partie.heure = 0.7;
        L.Monde.centrerCamera(regarde.x, regarde.y);
        for (let i = 0; i < 40; i++) { o.frame(1); a.j.x = a.loin.x; a.j.y = a.loin.y; L.Monde.centrerCamera(regarde.x, regarde.y); }
        const restent = L.B.entites.filter(function (e) { return e.bac; });
        const horsDeVue = restent.filter(function (e) { return !L.Entites.visibleAEcran(e.x, e.y, 40); }).length;
        return { sousLesYeux: sousLesYeux, naissances: naissances, matin: matin, horsDeVue: horsDeVue, regardeReste: restent.indexOf(regarde) >= 0 };
    }""")
    assert r["sousLesYeux"] is False, "la caméra sur la place du bac, et il y est sorti"
    assert r["matin"] >= 1, "aucun bac au bord du trottoir le matin"
    assert not any(r["naissances"]), "un bac est sorti sous les yeux"
    assert r["regardeReste"] is True, "un bac a disparu sous les yeux"
    assert r["horsDeVue"] == 0, f"l'après-midi, {r['horsDeVue']} bacs hors de vue encore dehors"


def test_ni_le_camion_ni_les_bacs_ne_tirent_un_de_du_jeu(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, 5, 6);
        L.graine(123);
        const tirage = L.B.rng;
        let dansLAutobus = 0;
        L.B.rng = function () {
            if (String(new Error().stack).indexOf('autobus.js') >= 0) dansLAutobus++;
            return tirage();
        };
        let collecte = false, bacs = 0;
        for (let i = 0; i < 2500 && !collecte; i++) {
            o.frame(1); tenir(L, a);
            const v = camion(L);
            if (v && v.arretT > 0) collecte = true;
            bacs = Math.max(bacs, L.B.entites.filter(function (e) { return e.bac; }).length);
        }
        return { collecte: collecte, bacs: bacs, dansLAutobus: dansLAutobus };
    }""")
    assert r["collecte"] and r["bacs"] >= 1, f"le juge ne mesure rien : {r}"
    assert r["dansLAutobus"] == 0, f"{r['dansLAutobus']} dés tirés par la tournée"


def test_un_bac_ne_sort_pas_sur_un_passant(banc):
    """⚠️ La leçon des voyageurs de l'abribus : on ne naît pas dans quelqu'un. Un
    passant planté sur la place du bac : le bac attend qu'il s'en aille."""
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, 5, 6);
        const place = L.Autobus.placeDuBac(a.pt), x = place.x, y = place.y;
        const p = L.Entites.creerPieton(x, y, L.Entites.archetype('passant'));
        p.etat = 'fige'; p.plante = { x: x, y: y };
        L.Entites.indexer();
        for (let i = 0; i < 70; i++) { o.frame(1); tenir(L, a); }
        const pendant = !!L.Autobus.bacDe(a.pt.k);
        L.Entites.retirer(p); L.Entites.indexer();
        for (let i = 0; i < 70; i++) { o.frame(1); tenir(L, a); }
        return { pendant: pendant, apres: !!L.Autobus.bacDe(a.pt.k) };
    }""")
    assert r["pendant"] is False, "le bac est sorti sur le passant"
    assert r["apres"] is True, "le passant parti, le bac ne sort pas : le juge ne mesure rien"


def test_un_bac_ne_barre_ni_le_trottoir_ni_la_voie(banc):
    """⚠️ Le trottoir de la banlieue fait UNE tuile. Un bac solide tous les cinq pas
    en faisait une suite de cages : les passants rebroussaient chemin devant chacun
    (mesuré : l'ivrogne et le musicien de `test_moteur_js.py` sont tombés, leurs
    passants coincés). Et posé au bas de la tuile, un bac de trottoir nord était à
    onze pixels de la voie : le camion (rayon 8) le touche à douze.

    1. Un passant qui marche le long du trottoir passe à travers le bac exactement
       comme s'il n'y était pas — même défoncé puis réparé le lendemain, quand c'est
       la fiche qui dit s'il est solide.
    2. Aucune place de bac n'est à portée d'un char qui roule au centre de la voie
       d'à côté."""
    r = banc("function (L, o) {" + AMENER + """
        function marcher(bac, dx, dy) {
            const p = L.Entites.creerPieton(bac.x - dx * 20, bac.y - dy * 20, L.Entites.archetype('passant'));
            const x0 = p.x, y0 = p.y;
            for (let i = 0; i < 40; i++) L.Entites.deplacerCercle(p, dx, dy, L.Monde.MASQUE_PIETON);
            const avance = (p.x - x0) * dx + (p.y - y0) * dy;
            L.Entites.retirer(p);
            return avance;
        }
        let mesure = null;
        for (let rang = 5; rang < 25 && !mesure; rang++) {
            const a = amener(L, rang, 6);
            for (let i = 0; i < 70 && !L.Autobus.bacDe(a.pt.k); i++) { o.frame(1); tenir(L, a); }
            const bac = L.Autobus.bacDe(a.pt.k);
            if (!bac) continue;
            const t = a.T.tuiles[a.pt.i], u = a.T.tuiles[(a.pt.i + 1) % a.T.n];
            const dx = u[0] - t[0], dy = u[1] - t[1];
            const avec = marcher(bac, dx, dy);
            // Défoncé la veille et remis le lendemain : c'est la FICHE qui dit alors s'il est solide.
            L.Entites.briser(bac); L.Entites.reparerLeDecor();
            const repare = marcher(bac, dx, dy);
            L.Entites.retirer(bac); L.Entites.reindexerDecor();
            const sans = marcher(bac, dx, dy);
            // Un lampadaire ou une borne sur le chemin : ce trottoir-là ne dit rien.
            if (sans < 38) continue;
            mesure = { rang: rang, avec: avec, repare: repare, sans: sans };
        }
        const T = L.Autobus.donnees().tournee;
        const rayon = Math.max.apply(null, L.B.defs.vehicules.filter(function (v) { return !v.eau; })
                                                              .map(function (v) { return v.largeur / 2; }));
        let plusPres = Infinity;
        for (const pt of T.points) {
            const t = T.tuiles[pt.i], u = T.tuiles[(pt.i + 1) % T.n];
            const dx = u[0] - t[0], dy = u[1] - t[1];
            const place = L.Autobus.placeDuBac(pt);
            const cx = t[0] * L.TT + 8, cy = t[1] * L.TT + 8;
            plusPres = Math.min(plusPres, Math.abs((place.x - cx) * dy - (place.y - cy) * dx));
        }
        return { mesure: mesure, plusPres: plusPres, contact: rayon + L.DECORS.bac.r, points: T.points.length };
    }""")
    m = r["mesure"]
    assert m, "aucun trottoir dégagé autour d'un bac : le juge ne mesure rien"
    assert m["avec"] == m["sans"], f"le bac barre le trottoir : {m}"
    assert m["repare"] == m["sans"], f"réparé le lendemain, le bac barre le trottoir : {m}"
    assert r["plusPres"] >= r["contact"] + 2, (
        f"un bac à {r['plusPres']} px du centre de la voie : un char le touche à {r['contact']}")
