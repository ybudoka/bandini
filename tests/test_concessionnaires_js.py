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
