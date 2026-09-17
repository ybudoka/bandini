"""On attend l'autobus (M12, 17 sept. 2026) : des passants attendent à l'abribus,
montent quand il s'arrête, et descendent quelques arrêts plus loin.

⚠️ Juges : personne ne naît sous les yeux ; l'autobus s'arrête VRAIMENT pour qui
attend, même sans personne pour le regarder ; ceux qui montent quittent le trottoir
et redescendent à l'arrêt qu'ils ont en tête ; à bord, l'autobus ne s'arrête que
pour qui descend ; et pas un dé du jeu tiré dans tout ça.
"""

#: Un arrêt au milieu de la ligne 2, une heure de jour où quelqu'un y attend, et le
#: joueur à vingt et une tuiles du trottoir : hors de l'écran, dans la bulle.
PREPARER = """
    function preparer(L, o) {
        L.Jeu.commencer();
        const d = L.Autobus.donnees();
        const ligne = d.lignes.find(function (l) { return l.numero === 2; });
        const rang = Math.floor(ligne.ordre.length / 2);
        const a = d.arrets[ligne.ordre[rang].arret];
        L.B.partie.jour = 2;
        let h = 0.42;
        for (let k = 0; k < 200 && L.Autobus.combienAttendent(a) === 0; k++) { L.B.partie.heure = h; h += 1 / 96; }
        const j = L.B.joueur;
        // ⚠️ Intouchable : le juge le plante où la rue l'exige, et un joueur fauché
        // par le trafic part a l'hopital — le juge mesurerait un fondu.
        j.intouchable = true;
        const loin = { x: a.quai[0] * L.TT + 8, y: a.quai[1] * L.TT + 8 + 21 * L.TT };
        j.x = loin.x; j.y = loin.y; L.Monde.centrerCamera(j.x, j.y);
        return { d: d, ligne: ligne, rang: rang, a: a, j: j, loin: loin };
    }
    function tenir(L, p) { p.j.x = p.loin.x; p.j.y = p.loin.y; L.Monde.centrerCamera(p.j.x, p.j.y); }
"""


def test_des_gens_attendent_a_l_abribus_et_personne_ne_nait_sous_les_yeux(banc):
    r = banc("function (L, o) {" + PREPARER + """
        const p = preparer(L, o);
        const voulu = L.Autobus.combienAttendent(p.a);
        // ⚠️ AU VOLANT, LA CAMÉRA PREND DE L'AVANCE : le joueur à vingt et une tuiles,
        // l'abribus peut être à l'écran. Personne n'y naît tant qu'on le voit.
        const qa = { x: p.a.quai[0] * 16 + 8, y: p.a.quai[1] * 16 + 8 };
        for (let i = 0; i < 90; i++) { o.frame(1); p.j.x = p.loin.x; p.j.y = p.loin.y; L.Monde.centrerCamera(qa.x, qa.y); }
        const sousLesYeux = L.Autobus.quiAttend(p.a.id).length;
        const vus = new Set(), naissances = [];
        for (let i = 0; i < 90; i++) {
            o.frame(1); tenir(L, p);
            for (const e of L.B.entites) {
                if (e.attend === undefined || vus.has(e)) continue;
                vus.add(e);
                naissances.push({ visible: L.Entites.visibleAEcran(e.x, e.y, 0),
                                  distance: Math.hypot(e.x - p.j.x, e.y - p.j.y) });
            }
        }
        const la = L.Autobus.quiAttend(p.a.id);
        return { voulu: voulu, sousLesYeux: sousLesYeux, la: la.length, max: p.d.attente.par_abri, naissances: naissances,
                 foule: la.every(function (e) { return e.metier === 'autobus'; }),
                 trottoir: la.every(function (e) { const tx = Math.floor(e.x / 16), ty = Math.floor(e.y / 16);
                                                   return L.Monde.marchablePieton(tx, ty) && !L.Monde.estChaussee(tx, ty); }),
                 regardent: la.map(function (e) { return e.face; }), attente: p.d.attente };
    }""")
    assert r["voulu"] >= 1, "le juge n'a trouvé aucune heure où quelqu'un attend"
    assert r["sousLesYeux"] == 0, "la caméra sur l'abribus, quelqu'un y est né sous les yeux"
    assert r["la"] == r["voulu"] and r["la"] <= r["max"], r
    assert r["foule"], "qui attend n'est pas la foule : il a un but, comme l'ouvrier à son chantier"
    assert r["trottoir"], "on attend sur le trottoir, pas dans la rue"
    for n in r["naissances"]:
        assert not n["visible"], f"quelqu'un est né sous les yeux ({n})"
        assert r["attente"]["naissance_min_px"] - 40 <= n["distance"] <= r["attente"]["naissance_max_px"] + 40, n


def test_l_autobus_s_arrete_pour_eux_ils_montent_et_descendent_plus_loin(banc):
    """⚠️ Sans personne pour le voir : l'autobus s'arrête parce que quelqu'un attend,
    pas parce que le joueur regarde. Et ceux qui montent redescendent à l'arrêt
    qu'ils ont en tête, deux à quatre arrêts plus loin."""
    r = banc("function (L, o) {" + PREPARER + """
        const p = preparer(L, o);
        for (let i = 0; i < 40; i++) { o.frame(1); tenir(L, p); }
        // ⚠️ **QUI ATTEND QUAND L'AUTOBUS ARRIVE**, pas qui attendait a la 40e
        // image. L'abribus se remplit par QUART D'HEURE, et l'autobus met ce
        // qu'il met pour venir : compter au depart, c'etait comparer la file
        // d'un quart d'heure aux montees d'un autre. Le 17 sept. 2026, un
        // changement de rythme du trafic a decale son arrivee, et le juge a dit
        // « quatre sont montes pour deux qui attendaient » — alors que les
        // quatre attendaient bel et bien quand il a ouvert ses portes.
        let ids = L.Autobus.quiAttend(p.a.id).map(function (e) { return e.id; });
        let bus = null, arretVu = null;
        for (let i = 0; i < 9000 && !bus; i++) {
            const avant = L.Autobus.quiAttend(p.a.id).map(function (e) { return e.id; });
            o.frame(1); tenir(L, p);
            for (const v of L.B.entites) {
                if (v.conducteur === 'ligne' && v.arretT > 0 && v.arret === p.a.id) {
                    bus = v; arretVu = { visible: L.Entites.visibleAEcran(v.x, v.y, 0) }; ids = avant;
                }
            }
        }
        if (!bus) return { attendaient: ids.length, bus: false };
        let bord0 = bus.bord.length;
        for (let i = 0; i < 160 && bus.arretT > 0; i++) { o.frame(1); tenir(L, p); }
        const restent = L.B.entites.filter(function (e) { return ids.indexOf(e.id) >= 0; }).length;
        const montes = bus.bord.slice();
        // ⚠️ L'abribus ne se remplit pas derrière l'autobus dans le même quart d'heure :
        // l'autobus le marque servi.
        const vide = { servi: (L.B.abribusServis || {})[p.a.id], quart: L.Autobus.quartDHeure() };
        // On suit l'autobus jusqu'à ce que ceux d'ICI soient tous descendus (d'autres
        // montent en route : ils ne sont pas le sujet).
        const descentes = [];
        const pietons0 = new Set(L.B.entites.filter(function (e) { return e.type === 'pieton'; }));
        const dIci = function () { return bus.bord.filter(function (b) { return b.depuis === p.a.id; }).length; };
        for (let i = 0; i < 12000 && dIci() && L.B.entites.indexOf(bus) >= 0; i++) {
            const avant = dIci();
            const attendus = bus.bord.filter(function (b) { return b.depuis === p.a.id; }).map(function (b) { return b.arret; });
            p.j.x = bus.x; p.j.y = bus.y + 3 * 16; L.Monde.centrerCamera(p.j.x, p.j.y);
            o.frame(1);
            if (dIci() < avant) {
                const a = L.Autobus.arret(bus.arret);
                const nes = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.descenduDe !== undefined && !pietons0.has(e); });
                nes.forEach(function (e) { pietons0.add(e); });
                descentes.push({ arret: bus.arret, attendu: attendus,
                                 nes: nes.map(function (e) { return Math.round(Math.hypot(e.x - (a.quai[0] * 16 + 8), e.y - (a.quai[1] * 16 + 8))); }) });
            }
        }
        const ordre = p.ligne.ordre.map(function (x) { return x.arret; });
        return { attendaient: ids.length, bus: true, arretVu: arretVu, bord0: bord0, restent: restent, vide: vide,
                 montes: montes.filter(function (b) { return b.depuis === p.a.id; }).map(function (b) { return b.arret; }),
                 descentes: descentes, ordre: ordre, depart: p.a.id,
                 attente: p.d.attente, resteABord: dIci() };
    }""")
    assert r["attendaient"] >= 1
    assert r["bus"], "aucun autobus ne s'est arrêté à l'abribus où l'on attendait"
    assert r["arretVu"]["visible"] is False, "le juge doit regarder un arrêt HORS de l'écran"
    assert r["restent"] == 0, "l'autobus est reparti et il reste du monde sur le trottoir"
    assert r["vide"]["servi"] == r["vide"]["quart"], "l'autobus n'a pas marqué l'abribus servi"
    assert len(r["montes"]) == r["attendaient"], f"{r['attendaient']} attendaient, {len(r['montes'])} sont montés"
    ordre, depart = r["ordre"], r["depart"]
    for sortie in r["montes"]:
        ecart = (ordre.index(sortie) - ordre.index(depart)) % len(ordre)
        assert r["attente"]["arrets_min"] <= ecart <= r["attente"]["arrets_max"], (sortie, ecart)
    assert r["resteABord"] == 0, f"personne n'est descendu : {r['descentes']}"
    for d in r["descentes"]:
        assert d["arret"] in d["attendu"], d
        assert d["nes"] and all(n < 48 for n in d["nes"]), f"descendu loin du trottoir de l'arrêt : {d}"


def test_l_autobus_s_arrete_pour_qui_attend_et_a_bord_pour_qui_descend(banc):
    """La règle d'arrêt : sans le joueur à bord, on s'arrête pour qui attend, vu ou
    pas ; avec lui, seulement pour qui descend — une demande d'arrêt comme la
    sienne — et pas pour qui attend (il prendra le suivant)."""
    r = banc("function (L, o) {" + PREPARER + """
        const p = preparer(L, o);
        for (let i = 0; i < 40; i++) { o.frame(1); tenir(L, p); }
        const h = p.d.horaire.arret_images;
        const bus = { passager: null, demande: false, bord: [] };
        const vide = p.d.arrets.find(function (a) {
            return L.Autobus.combienAttendent(a) === 0 && L.Autobus.quiAttend(a.id).length === 0 &&
                   !L.Entites.visibleAEcran(a.x * 16 + 8, a.y * 16 + 8, 40) &&
                   Math.hypot(a.quai[0] * 16 - p.j.x, a.quai[1] * 16 - p.j.y) > 200;
        });
        const sortie = {
            attendent: L.Autobus.quiAttend(p.a.id).length,
            pourQuiAttend: L.Autobus.dureeDArret(bus, p.a.id),
            arretVide: L.Autobus.dureeDArret(bus, vide.id),
        };
        bus.passager = p.j;
        sortie.aBordQuiAttend = L.Autobus.dureeDArret(bus, p.a.id);
        bus.bord = [{ arret: vide.id, depuis: p.a.id }];
        sortie.aBordQuiDescend = L.Autobus.dureeDArret(bus, vide.id);
        bus.passager = null;
        sortie.sansLuiQuiDescend = L.Autobus.dureeDArret(bus, vide.id);
        sortie.h = h;
        return sortie;
    }""")
    assert r["attendent"] >= 1
    assert r["pourQuiAttend"] == r["h"], "quelqu'un attend : l'autobus s'arrête"
    assert r["arretVide"] == 0, "personne, pas vu : il passe"
    assert r["aBordQuiAttend"] == 0, "à bord, il ne s'arrête pas pour qui attend"
    assert r["aBordQuiDescend"] == r["h"], "à bord, il s'arrête pour qui descend"
    assert r["sansLuiQuiDescend"] == r["h"]


def test_ni_attendre_ni_monter_ni_descendre_ne_tire_un_de_du_jeu(banc):
    """⚠️ `creerPieton` tire deux dés : les voyageurs jouent avec un dé PRÊTÉ. On compte
    les dés tirés pendant le code des autobus, sur un arrêt servi."""
    r = banc("function (L, o) {" + PREPARER + """
        const p = preparer(L, o);
        L.graine(91);
        const tirage = L.B.rng;
        let dansLesAutobus = 0;
        L.B.rng = function () {
            if (String(new Error().stack).indexOf('autobus.js') >= 0) dansLesAutobus++;
            return tirage();
        };
        let nes = 0, montes = 0;
        const vus = new Set();
        for (let i = 0; i < 6000 && montes === 0; i++) {
            o.frame(1); tenir(L, p);
            for (const e of L.B.entites) if (e.attend !== undefined && !vus.has(e)) { vus.add(e); nes++; }
            for (const v of L.B.entites) if (v.conducteur === 'ligne' && v.bord) montes = Math.max(montes, v.bord.length);
        }
        return { nes: nes, montes: montes, dansLesAutobus: dansLesAutobus };
    }""")
    assert r["nes"] >= 1 and r["montes"] >= 1, f"le juge ne mesure rien : {r}"
    assert r["dansLesAutobus"] == 0, f"{r['dansLesAutobus']} dés tirés par les voyageurs"


def test_un_abribus_servi_ne_se_remplit_pas_dans_le_quart_d_heure(banc):
    r = banc("function (L, o) {" + PREPARER + """
        const p = preparer(L, o);
        const avant = L.Autobus.combienAttendent(p.a);
        L.B.abribusServis = {}; L.B.abribusServis[p.a.id] = L.Autobus.quartDHeure();
        const servi = L.Autobus.combienAttendent(p.a);
        L.B.abribusServis[p.a.id] = L.Autobus.quartDHeure() - 1;
        return { avant: avant, servi: servi, quartSuivant: L.Autobus.combienAttendent(p.a) };
    }""")
    assert r["avant"] >= 1
    assert r["servi"] == 0, "un autobus vient d'y passer : personne n'y attend avant le quart d'heure suivant"
    assert r["quartSuivant"] == r["avant"]


def test_on_attend_sur_le_trottoir_a_chaque_abribus(banc):
    """Aux cinquante-trois abribus, chaque place d'attente est sur le trottoir, hors
    de la chaussée et d'aucun meuble. ⚠️ Et un mur posé exactement là refuse la
    place : sur cette ville aucune n'y tombe, mais une autre graine le pourrait."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = L.Autobus.donnees();
        const mauvaises = [];
        let poses = 0;
        for (const a of d.arrets) {
          for (let k = 0; k < d.attente.par_abri; k++) {
            const e = L.Autobus.naitreUnVoyageur(a, k);
            if (!e) { mauvaises.push([a.id, k, 'refusee']); continue; }
            poses++;
            const tx = Math.floor(e.x / 16), ty = Math.floor(e.y / 16);
            if (L.Monde.estChaussee(tx, ty) || !L.Monde.marchablePieton(tx, ty)) mauvaises.push([a.id, k, 'rue']);
            if (L.Entites.decorAutour(e.x, e.y, 8).some(function (q) { return q.solide && Math.hypot(q.x - e.x, q.y - e.y) < 10; })) mauvaises.push([a.id, k, 'meuble']);
            L.Entites.retirer(e); L.Entites.indexer();
          }
        }
        // Un mur à la première place du premier abribus.
        const a = d.arrets[0], c = L.Monde.carte;
        const essai = L.Autobus.naitreUnVoyageur(a, 0);
        const tx = Math.floor(essai.x / 16), ty = Math.floor(essai.y / 16);
        L.Entites.retirer(essai); L.Entites.indexer();
        const k = ty * c.w + tx, avant = c.solide[k];
        c.solide[k] = 1;
        const refusee = L.Autobus.naitreUnVoyageur(a, 0) === null;
        c.solide[k] = avant;
        // Et un passant planté sur la place : on ne naît pas dans quelqu'un.
        const passant = L.Entites.creerPieton(essai.x, essai.y, L.Entites.archetype('passant'));
        L.Entites.indexer();
        const occupee = L.Autobus.naitreUnVoyageur(a, 0) === null;
        L.Entites.retirer(passant); L.Entites.indexer();
        return { poses: poses, mauvaises: mauvaises, refusee: refusee, occupee: occupee };
    }""")
    assert r["poses"] >= 100, r
    assert r["mauvaises"] == [], r["mauvaises"][:10]
    assert r["refusee"], "un mur à la place d'attente, et quelqu'un y naît quand même"
    assert r["occupee"], "un passant sur la place d'attente, et quelqu'un naît dedans"
