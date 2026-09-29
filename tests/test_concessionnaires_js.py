"""Les chars des concessionnaires, au banc (docs/jalons/les-concessionnaires-le-neuf-aux-erables-l-usage-dans-les-friches.md).

La ville (les lots, leurs places, leur stock) se juge dans `test_concessionnaires.py`. Ici, ce qui vit : les chars
qui naissent dans le lot, hors champ et sans un dé du jeu, qui ne comptent pas comme chars garés de la rue, et qui
se volent — le neuf en sonnant, l'usagé en silence et à moitié mort.
"""

IMAGES_DE_PEUPLER = 80

#: Aller au lot sans le voir : le joueur à `decalage` pixels à l'est du milieu du lot, la caméra sur lui.
ALLER = """
    function lotDe(L, slug) { return L.Monde.carte.def.concessionnaires.find(function (l) { return l.slug === slug; }); }
    function milieu(L, lot) {
        const TT = L.TT, c = lot.cour;
        return { x: (c.x + c.l / 2) * TT, y: (c.y + c.h / 2) * TT };
    }
    function aller(L, lot, decalage) {
        const j = L.B.joueur, m = milieu(L, lot);
        j.x = m.x + decalage; j.y = m.y; L.Monde.centrerCamera(j.x, j.y);
        return m;
    }
    function duLot(L, lot) {
        return L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.placeDeLot && lot.places.indexOf(e.placeDeLot) >= 0; });
    }
"""


def test_les_chars_du_salon_naissent_hors_champ_sans_de(banc):
    """Devant le lot, sous les yeux : rien ne pousse. À une demi-bulle, hors champ : chaque place garnie a son char,
    celui du stock, garé, sans conducteur, à cheval sur sa case — et aucun dé du jeu n'a été tiré."""
    r = banc("""function (L, o) {
        %(aller)s
        L.Jeu.commencer();
        const lot = lotDe(L, 'prestige'), TT = L.TT;
        const m = aller(L, lot, 0);
        const dansLeChamp = L.Entites.visibleAEcran(m.x, m.y, 24);
        o.frame(%(images)d);
        const sousLesYeux = duLot(L, lot).length;
        aller(L, lot, 330);
        const visible = L.Entites.visibleAEcran(m.x, m.y - 2 * TT, 24);
        duLot(L, lot).forEach(function (e) { L.Entites.retirer(e); });
        let des = 0;
        const rng = L.B.rng;
        L.B.rng = function () { des++; return rng.apply(null, arguments); };
        const nees = L.Vehicules.majLotsDeConcession();
        L.B.rng = rng;
        const chars = duLot(L, lot).map(function (e) {
            const i = lot.places.indexOf(e.placeDeLot), p = lot.places[i];
            return { i: i, slug: e.slug, sprite: e.sprite, etat: e.etat, conducteur: e.conducteur,
                     dx: e.x / TT - (p.x + 0.5), dy: e.y / TT - (p.y + 1), angle: e.angle,
                     vie: e.vie, vieMax: e.vieMax, alarmeDuLot: !!e.alarmeDuLot };
        });
        return { dansLeChamp: dansLeChamp, sousLesYeux: sousLesYeux, visible: visible, nees: nees, des: des,
                 garees: lot.garees, stock: lot.stock, chars: chars };
    }""" % {"aller": ALLER, "images": IMAGES_DE_PEUPLER})
    assert r["dansLeChamp"] is True, "le juge devait avoir le lot sous les yeux"
    assert r["sousLesYeux"] == 0, "un char est né dans le lot, à l'écran"
    assert r["visible"] is False, "le juge devait regarder ailleurs"
    assert r["des"] == 0, f"{r['des']} dés du jeu tirés pour garnir le lot"
    assert r["nees"] == len(r["garees"]) == len(r["chars"]) >= 6
    assert sorted(c["i"] for c in r["chars"]) == sorted(r["garees"])
    for c in r["chars"]:
        assert c["slug"] == r["stock"][c["i"]]["slug"] and c["sprite"] == r["stock"][c["i"]]["sprite"], c
        assert c["etat"] == "stationne" and c["conducteur"] is None, c
        assert abs(c["dx"]) < 1e-6 and abs(c["dy"]) < 1e-6 and abs(c["angle"] + 3.14159265 / 2) < 1e-6, c
        assert c["vie"] == c["vieMax"] and c["alarmeDuLot"] is True, c


def test_les_chars_du_lot_ne_comptent_pas_comme_gares(banc):
    """Un char de lot n'est pas un char garé de la rue : `peupler` en ferait naître un de moins, et les dés de toute
    la suite glissent. `compteCommeGare` (ce que `peupler` compte) les écarte ; un char garé ordinaire, non."""
    r = banc("""function (L, o) {
        %(aller)s
        L.Jeu.commencer();
        const lot = lotDe(L, 'prestige');
        aller(L, lot, 330);
        L.Vehicules.majLotsDeConcession();
        const garnis = duLot(L, lot);
        const ordinaire = L.Vehicules.creer('auto', L.B.joueur.x, L.B.joueur.y + 200, 0, { etat: 'stationne', couleur: '#c0392b' });
        return { garnis: garnis.length, comptes: garnis.filter(L.Vehicules.compteCommeGare).length,
                 ordinaire: L.Vehicules.compteCommeGare(ordinaire) };
    }""" % {"aller": ALLER})
    assert r["garnis"] >= 6
    assert r["comptes"] == 0, r
    assert r["ordinaire"] is True, r


def test_voler_un_neuf_sonne_voler_un_usage_non(banc):
    r = banc("""function (L, o) {
        %(aller)s
        L.Jeu.commencer();
        const j = L.B.joueur, resultats = {};
        ['prestige', 'ti_pout'].forEach(function (slug) {
            const lot = lotDe(L, slug);
            aller(L, lot, 330);
            L.Vehicules.majLotsDeConcession();
            // Chez le neuf, la BERLINE : la sport et la luxe sonnent déjà par leur fiche (`def.alarme`).
            const v = duLot(L, lot).find(function (e) { return slug === 'ti_pout' || e.slug === 'auto'; });
            if (j.dansVehicule) L.Vehicules.descendre(j, true);
            j.x = v.x; j.y = v.y;
            L.Vehicules.monter(j, v);
            resultats[slug] = { slug: v.slug, alarme: v.alarme, vole: v.vole, vie: v.vie, vieMax: v.vieMax, usure: v.usure || 1 };
        });
        return resultats;
    }""" % {"aller": ALLER})
    assert r["prestige"]["vole"] is True and r["prestige"]["alarme"] > 0, r["prestige"]
    assert r["ti_pout"]["vole"] is True and r["ti_pout"]["alarme"] == 0, r["ti_pout"]
    assert r["ti_pout"]["usure"] == 0.6
    assert r["ti_pout"]["vie"] == max(1, round(r["ti_pout"]["vieMax"] * 0.6)), r["ti_pout"]


def test_un_char_pris_ne_se_double_pas(banc):
    """On prend un char du lot et on l'emmène : tant qu'il existe, sa place ne se regarnit pas."""
    r = banc("""function (L, o) {
        %(aller)s
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT, lot = lotDe(L, 'ti_pout');
        aller(L, lot, 330);
        L.Vehicules.majLotsDeConcession();
        const v = duLot(L, lot)[0], place = v.placeDeLot;
        j.x = v.x; j.y = v.y;
        L.Vehicules.monter(j, v);
        v.x += 200; v.y += 6 * TT; j.x = v.x; j.y = v.y;
        aller(L, lot, 330);
        const nees = L.Vehicules.majLotsDeConcession();
        const surLaPlace = L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.placeDeLot === place; }).length;
        return { nees: nees, surLaPlace: surLaPlace };
    }""" % {"aller": ALLER})
    assert r == {"nees": 0, "surLaPlace": 1}, r


ACHETER = """
    function acheter(L, o, slug, argent) {
        const j = L.B.joueur, lot = lotDe(L, slug);
        aller(L, lot, 330);
        L.Vehicules.majLotsDeConcession();
        const porte = L.Monde.carte.portes.find(function (p) { return p.interieur === slug; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        L.B.partie.argent = argent;
        L.Jeu.entrer(porte); o.fondu();
        for (let k = 0; k < 200 && !L.B.interieur; k++) o.frame(1);
        const point = L.B.interieur.points.find(function (p) { return p.type === 'concession'; });
        const menu = L.Missions.menuDuPoint(point);
        return { lot: lot, porte: porte, point: point, menu: menu };
    }
"""


def test_acheter_au_comptoir_rend_le_char_a_toi(banc):
    """Au comptoir du Salon, le menu vend les chars du lot à leur prix ; on paie, et celui de dehors est à toi :
    on sort, on monte, et ce n'est pas un vol — pas d'alarme, pas de crime."""
    r = banc("""function (L, o) {
        %(aller)s
        %(acheter)s
        L.Jeu.commencer();
        const a = acheter(L, o, 'prestige', 100000);
        const items = a.menu.items.filter(function (it) { return it.faire; });
        const libelles = items.map(function (it) { return it.libelle + ' ' + it.detail; });
        const exterieur = L.B.exterieur ? L.B.exterieur.entites : L.B.entites;
        const berline = exterieur.find(function (e) { return e.placeDeLot && e.slug === 'auto' && a.lot.places.indexOf(e.placeDeLot) >= 0; });
        const i = a.lot.places.indexOf(berline.placeDeLot), prix = a.lot.stock[i].prix;
        const item = items.find(function (it) { return it.place === i; });
        item.faire();
        const apres = L.B.partie.argent;
        const menuApres = L.Missions.menuDuPoint(a.point).items.filter(function (it) { return it.place === i; }).length;
        L.Jeu.sortir(); o.fondu();
        for (let k = 0; k < 200 && L.B.interieur; k++) o.frame(1);
        const j = L.B.joueur;
        j.x = berline.x; j.y = berline.y;
        const volees = L.B.partie.stats.volees;
        L.Vehicules.monter(j, berline);
        return { titre: a.menu.titre, n: items.length, garees: a.lot.garees.length, libelles: libelles, prix: prix,
                 apres: apres, aToi: berline.aToi, vole: berline.vole, alarme: berline.alarme, menuApres: menuApres,
                 volees: L.B.partie.stats.volees - volees, conducteur: berline.conducteur === j };
    }""" % {"aller": ALLER, "acheter": ACHETER})
    assert r["n"] == r["garees"], r["libelles"]
    assert r["apres"] == 100000 - r["prix"], r
    assert r["aToi"] is True and r["conducteur"] is True, r
    assert r["vole"] is False and r["alarme"] == 0 and r["volees"] == 0, r
    assert r["menuApres"] == 0, "le char vendu est encore au menu"


def test_sans_argent_on_regarde(banc):
    r = banc("""function (L, o) {
        %(aller)s
        %(acheter)s
        L.Jeu.commencer();
        const a = acheter(L, o, 'ti_pout', 10);
        return a.menu.items.filter(function (it) { return it.faire; }).map(function (it) { return it.actif; });
    }""" % {"aller": ALLER, "acheter": ACHETER})
    assert r and not any(r), r


def test_la_place_vendue_se_regarnit_le_lendemain(banc):
    """Le char vendu parti (oublié loin de la bulle), sa place reste vide le jour même — pas de char gratuit à
    revenir chercher — et le lendemain, le lot en rentre un neuf."""
    r = banc("""function (L, o) {
        %(aller)s
        L.Jeu.commencer();
        const p = L.B.partie, lot = lotDe(L, 'prestige'), i = lot.garees[0], place = lot.places[i];
        aller(L, lot, 330);
        L.Vehicules.majLotsDeConcession();
        p.concession = {}; p.concession['prestige:' + i] = p.jour;
        duLot(L, lot).filter(function (e) { return e.placeDeLot === place; }).forEach(function (e) { L.Entites.retirer(e); });
        L.Vehicules.majLotsDeConcession();
        const leJour = duLot(L, lot).filter(function (e) { return e.placeDeLot === place; }).length;
        p.jour += 1;
        L.Vehicules.majLotsDeConcession();
        const lendemain = duLot(L, lot).filter(function (e) { return e.placeDeLot === place; }).length;
        return { leJour: leJour, lendemain: lendemain, reste: p.concession['prestige:' + i] === undefined };
    }""" % {"aller": ALLER})
    assert r == {"leJour": 0, "lendemain": 1, "reste": True}, r


def test_les_passants_ne_tirent_pas_leur_porte_chez_les_concessionnaires(banc):
    """⚠️ `portesFermees` est une liste TIRÉE par index (`entites.js`, un passant qui sort d'une porte) et relevée
    sur le sol dans l'ordre de lecture : une porte neuve, en haut de la carte, décalait tous les tirages de la ville
    (`test_parole`, `test_police_js` rougissaient au terminus). Les portes des concessionnaires n'y entrent pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, lots = c.def.concessionnaires;
        const dedans = lots.filter(function (l) {
            return c.portesFermees.some(function (p) { return p.x === l.porte.x && p.y === l.porte.y; });
        }).map(function (l) { return l.slug; });
        return { dedans: dedans, lots: lots.length };
    }""")
    assert r["lots"] == 2 and r["dedans"] == [], r


def test_un_char_achete_garde_a_la_planque_reste_a_toi(banc):
    """Relecture finale : la sauvegarde gardait `vole`, pas `aToi` — un char PAYÉ garé devant la planque redevenait,
    au rechargement, un char à voler (l'alarme de la sport, une étoile)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const TT = L.TT, p = L.B.partie;
        const porte = L.Monde.carte.def.portes.find(function (q) { return q.lieu === 'planque'; });
        const v = L.Vehicules.creer('sport', porte.x * TT + 8, (porte.y + 2) * TT, 0, { etat: 'stationne', couleur: '#16a085' });
        v.aToi = true;
        L.Missions.sauvegarderPartie();
        const garde = Object.assign({}, p.planque.vehicule);
        L.Sauvegarde.ecrire(p);
        L.B.partie = L.Sauvegarde.completer(L.Sauvegarde.lire(), L.B.defs);
        L.Jeu.commencer();
        const j = L.B.joueur;
        const w = L.B.entites.find(function (e) { return e.type === 'vehicule' && e.couleur === '#16a085'; });
        if (j.dansVehicule) L.Vehicules.descendre(j, true);
        j.x = w.x; j.y = w.y;
        const volees = L.B.partie.stats.volees;
        L.Vehicules.monter(j, w);
        return { garde: garde.aToi, aToi: w.aToi, vole: w.vole, alarme: w.alarme, volees: L.B.partie.stats.volees - volees };
    }""")
    assert r == {"garde": True, "aToi": True, "vole": False, "alarme": 0, "volees": 0}, r


def test_un_passant_ne_vole_ni_le_char_paye_ni_ceux_du_lot(banc):
    """Relecture finale : le vol de char d'un passant (`majVolDeChar`) prenait le char qu'on venait de payer, et les
    neufs du lot sans que l'alarme sonne. Seul candidat à l'écran : le char payé, puis un char du lot."""
    r = banc("""function (L, o) {
        %(aller)s
        L.Jeu.commencer();
        const lot = lotDe(L, 'ti_pout'), j = L.B.joueur, f = L.B.defs.pietons.vol_de_char;
        aller(L, lot, 330);
        L.Vehicules.majLotsDeConcession();
        const duLotLa = duLot(L, lot)[0];
        f.chance_par_minute = 1;
        function essayer(cible) {
            L.B.entites.filter(function (e) { return e.type === 'vehicule' && e !== cible; }).forEach(function (e) { L.Entites.retirer(e); });
            j.x = cible.x + 40; j.y = cible.y; L.Monde.centrerCamera(j.x, j.y);
            const pieton = L.Entites.creerPieton(cible.x + 20, cible.y + 20);
            pieton.etat = 'flane';
            L.Entites.indexer();
            L.B.volMinute = null;
            const vise = L.Entites.majVolDeChar();
            L.Entites.retirer(pieton);
            return vise;
        }
        const paye = L.Vehicules.creer('auto', duLotLa.x + 200, duLotLa.y, 0, { etat: 'stationne', couleur: '#c0392b' });
        paye.aToi = true;
        const surLePaye = essayer(paye);
        const surLeLot = essayer(duLotLa);
        const temoin = L.Vehicules.creer('auto', duLotLa.x + 200, duLotLa.y, 0, { etat: 'stationne', couleur: '#2c3e50' });
        const surUnAutre = essayer(temoin);
        return { paye: surLePaye, lot: surLeLot, temoin: surUnAutre };
    }""" % {"aller": ALLER})
    assert r["temoin"] == 1, f"le juge ne voit pas le vol d'un char ordinaire : {r}"
    assert r["paye"] == 0 and r["lot"] == 0, r


MONTRE = """
    function enMontre(L, lot) {
        return L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.placeDeLot === lot.montre; });
    }
    // Loin de la dalle ELLE-MÊME (à l'ouest), hors champ mais dans la portée du lot.
    function allerPresDeLaMontre(L, lot) {
        const j = L.B.joueur, m = lot.montre, TT = L.TT;
        j.x = (m.x + 1) * TT - 340; j.y = (m.y + 1) * TT; L.Monde.centrerCamera(j.x, j.y);
        if (L.Entites.visibleAEcran((m.x + 1) * TT, (m.y + 1) * TT, 24)) throw new Error('la dalle est a l ecran');
    }
"""


def test_le_char_en_montre_nait_en_diagonale_le_modele_du_jour(banc):
    r = banc("""function (L, o) {
        %(aller)s
        %(montre)s
        L.Jeu.commencer();
        const out = {};
        ['prestige', 'ti_pout'].forEach(function (slug) {
            const lot = lotDe(L, slug), m = lot.montre, TT = L.TT, p = L.B.partie;
            allerPresDeLaMontre(L, lot);
            enMontre(L, lot).forEach(function (e) { L.Entites.retirer(e); });
            let des = 0;
            const rng = L.B.rng;
            L.B.rng = function () { des++; return rng.apply(null, arguments); };
            L.Vehicules.majLotsDeConcession();
            L.B.rng = rng;
            const v = enMontre(L, lot);
            const attendu = m.modeles[(p.jour - 1) %% m.modeles.length];
            out[slug] = { n: v.length, des: des, slug: v[0] && v[0].slug, sprite: v[0] && v[0].sprite, attendu: attendu,
                          dx: v[0] && v[0].x - (m.x + 1) * TT, dy: v[0] && v[0].y - (m.y + 1) * TT,
                          angle: v[0] && v[0].angle, voulu: m.angle, alarme: v[0] && !!v[0].alarmeDuLot };
        });
        return out;
    }""" % {"aller": ALLER, "montre": MONTRE})
    for slug, x in r.items():
        assert x["n"] == 1 and x["des"] == 0, (slug, x)
        assert x["slug"] == x["attendu"]["slug"] and x["sprite"] == x["attendu"]["sprite"], (slug, x)
        assert abs(x["dx"]) < 1e-6 and abs(x["dy"]) < 1e-6 and abs(x["angle"] - x["voulu"]) < 1e-6, (slug, x)
    assert r["prestige"]["alarme"] is True and r["ti_pout"]["alarme"] is False


def test_le_char_en_montre_change_le_lendemain_mais_pas_sous_les_yeux(banc):
    r = banc("""function (L, o) {
        %(aller)s
        %(montre)s
        L.Jeu.commencer();
        const lot = lotDe(L, 'prestige'), m = lot.montre, p = L.B.partie, j = L.B.joueur, TT = L.TT;
        allerPresDeLaMontre(L, lot);
        L.Vehicules.majLotsDeConcession();
        const hier = enMontre(L, lot)[0];
        p.jour += 1;
        // Sous les yeux : il reste celui d'hier.
        j.x = (m.x + 1) * TT; j.y = (m.y + 3) * TT; L.Monde.centrerCamera(j.x, j.y);
        L.Vehicules.majLotsDeConcession();
        const vu = enMontre(L, lot);
        const resteSousLesYeux = vu.length === 1 && vu[0] === hier;
        // Hors champ : celui du jour le remplace.
        allerPresDeLaMontre(L, lot);
        L.Vehicules.majLotsDeConcession();
        const auj = enMontre(L, lot);
        const attendu = m.modeles[(p.jour - 1) %% m.modeles.length];
        return { resteSousLesYeux: resteSousLesYeux, n: auj.length, nouveau: auj[0] !== hier, hierParti: L.B.entites.indexOf(hier) < 0,
                 slug: auj[0] && auj[0].slug, sprite: auj[0] && auj[0].sprite, attendu: attendu,
                 hierModele: hier.sprite };
    }""" % {"aller": ALLER, "montre": MONTRE})
    assert r["resteSousLesYeux"] is True, r
    assert r["n"] == 1 and r["nouveau"] and r["hierParti"], r
    assert r["slug"] == r["attendu"]["slug"] and r["sprite"] == r["attendu"]["sprite"], r
    assert r["sprite"] != r["hierModele"], "le modèle n'a pas changé d'un jour à l'autre"


def test_on_achete_le_char_en_montre(banc):
    r = banc("""function (L, o) {
        %(aller)s
        %(montre)s
        %(acheter)s
        L.Jeu.commencer();
        allerPresDeLaMontre(L, lotDe(L, 'prestige'));
        L.Vehicules.majLotsDeConcession();
        const a = acheter(L, o, 'prestige', 100000);
        const premier = a.menu.items.filter(function (it) { return it.faire; })[0];
        const exterieur = L.B.exterieur ? L.B.exterieur.entites : L.B.entites;
        const v = exterieur.find(function (e) { return e.placeDeLot === a.lot.montre; });
        const prix = a.lot.montre.modeles[(L.B.partie.jour - 1) %% a.lot.montre.modeles.length].prix;
        premier.faire();
        return { libelle: premier.libelle, detail: premier.detail, prix: prix, aToi: v.aToi, argent: L.B.partie.argent,
                 vendu: L.B.partie.concession['prestige:montre'] === L.B.partie.jour };
    }""" % {"aller": ALLER, "montre": MONTRE, "acheter": ACHETER})
    assert r["libelle"].startswith("EN MONTRE"), r
    assert r["detail"] == f"{r['prix']} $" and r["argent"] == 100000 - r["prix"], r
    assert r["aToi"] is True and r["vendu"] is True, r


def test_on_achete_un_4_roues_chez_ti_pout(banc):
    """Les 4 roues, vague 3 (docs/jalons/les-4-roues.md) : au comptoir de la roulotte, le 4 roues du lot se vend
    à son prix d'usagé ; payé, celui de dehors est à toi — pas un vol."""
    r = banc("""function (L, o) {
        %(aller)s
        %(acheter)s
        L.Jeu.commencer();
        const a = acheter(L, o, 'ti_pout', 100000);
        const items = a.menu.items.filter(function (it) { return it.faire; });
        const exterieur = L.B.exterieur ? L.B.exterieur.entites : L.B.entites;
        const quad = exterieur.find(function (e) { return e.placeDeLot && e.slug === 'quatre_roues' && a.lot.places.indexOf(e.placeDeLot) >= 0; });
        if (!quad) return { quad: false };
        const i = a.lot.places.indexOf(quad.placeDeLot), prix = a.lot.stock[i].prix;
        const item = items.find(function (it) { return it.place === i; });
        item.faire();
        const apres = L.B.partie.argent;
        L.Jeu.sortir(); o.fondu();
        for (let k = 0; k < 200 && L.B.interieur; k++) o.frame(1);
        const j = L.B.joueur;
        j.x = quad.x; j.y = quad.y;
        const volees = L.B.partie.stats.volees;
        L.Vehicules.monter(j, quad);
        return { quad: true, libelle: item.libelle, prix: prix, apres: apres, aToi: quad.aToi, vole: quad.vole,
                 volees: L.B.partie.stats.volees - volees, conducteur: quad.conducteur === j };
    }""" % {"aller": ALLER, "acheter": ACHETER})
    assert r["quad"], "pas de 4 roues dans le lot de Ti-Pout"
    assert r["apres"] == 100000 - r["prix"] and r["prix"] > 0, r
    assert r["aToi"] is True and r["conducteur"] is True and r["vole"] is False and r["volees"] == 0, r
