"""Le caddie qu'on fouille, qu'on redresse et qu'on pousse ; la plaque de rue et les panneaux drôles — au
bouton (docs/jalons/le-decor-les-betes-et-les-gens-repondent.md, deuxième vague, 2 oct. 2026).

⚠️ **CHAQUE GESTE SE JUGE PAR LE BOUTON** (`o.tape('KeyE')`, `o.touche('KeyW')`) : la chaîne d'ACTION affame
ce qui la suit, et un juge qui appelle `Caddies.redresser` ne voit jamais le bouton cassé. Le panneau d'un
défi, plus haut dans la chaîne, garde le sien : un juge le dit.
"""

import json
import re

import pytest

import villes

from app import autobus, interactions, panneaux

#: ⚠️ On se plante À CÔTÉ du caddie (ni porte, ni arme par terre, ni char sous la main) et on efface les
#: passants et les chars d'alentour : un juge du caddie ne mesure pas la foule qui passait par là.
OUTILS = """
    L.Jeu.commencer();
    const j = L.B.joueur, p = L.B.partie, TT = L.TT;
    j.invincible = 1e9;
    function nettoyer() {
        for (const e of L.Entites.autour(j.x, j.y, 160, function (q) { return (q.type === 'pieton' && !q.temoinDuJuge) || (q.type === 'vehicule' && !q.duJuge); })) L.Entites.retirer(e);
        L.Entites.indexer();
    }
    function invite() { L.Missions.majInvite(j); return L.B.invite; }
    function suivant() { const t = L.B.t; for (let k = 0; k < 6 && L.B.t === t; k++) o.frame(1); nettoyer(); }
    function figer(v, f) { const r = L.B.rng; L.B.rng = function () { return v; }; try { return f(); } finally { L.B.rng = r; } }
    // Les quatre sens : la touche, et le pas qu'elle fait faire.
    const SENS = [['KeyW', 0, -1], ['KeyS', 0, 1], ['KeyA', -1, 0], ['KeyD', 1, 0]];
    function libreDevant(d, dx, dy, px) {
        for (let k = 4; k <= px; k += 4) if (!L.Entites.decorPeutAller(d, d.x + dx * k, d.y + dy * k)) return false;
        return true;
    }
    function personneSousLaMain() {
        return !L.Monde.porteDevant(j) && !L.Combat.objetSousLaMain(j) && !L.Vehicules.vehiculeSousLaMain(j);
    }
    /** Un caddie couché, une ligne libre de `px` devant lui dans un sens, et le joueur DERRIÈRE, qui le regarde. */
    function caddieAPousser(px) {
        for (const d of L.Caddies.liste()) {
            if (d.decor !== 'caddie' || d.brise) continue;
            for (const s of SENS) {
                const dx = s[1], dy = s[2];
                if (!libreDevant(d, dx, dy, px)) continue;
                j.x = d.x - dx * 15; j.y = d.y - dy * 10; j.vx = 0; j.vy = 0; j.roule = 0;
                if (!L.Monde.marchablePieton(Math.floor(j.x / TT), Math.floor(j.y / TT))) continue;
                L.Monde.centrerCamera(j.x, j.y); nettoyer(); o.viser(d);
                if (!personneSousLaMain()) continue;
                return { d: d, touche: s[0], dx: dx, dy: dy };
            }
        }
        return null;
    }
    /** Fouiller (une pression), puis redresser (la suivante) : le caddie est debout, prêt à pousser. */
    function redresse(px) {
        const c = caddieAPousser(px);
        if (!c) return null;
        figer(0.99, function () { o.tape('KeyE'); });
        suivant();
        o.tape('KeyE');
        suivant();
        return c;
    }
    function pousser(touche, images, sprint) {
        if (sprint) o.touche('ShiftLeft');
        o.touche(touche);
        for (let k = 0; k < images; k++) o.frame(1);
        o.relacher(touche);
        if (sprint) o.relacher('ShiftLeft');
    }
"""


def jouer(banc, corps):
    return banc("function (L, o) {" + OUTILS + corps + "}")


# --- Fouiller, puis redresser ---------------------------------------------------------------------------


def test_le_caddie_se_fouille_d_abord_puis_se_redresse_au_bouton(banc):
    c = interactions.CADDIE
    r = jouer(banc, """
        const k = caddieAPousser(40);
        if (!k) return { aucun: true };
        const d = k.d, cle = L.Caddies.cle(d);
        const avant = { invite: invite(), argent: p.argent, collections: JSON.stringify(p.collections || {}) };
        // La table tire la monnaie en premier : un dé à zéro, c'est elle (1 $ au plus bas).
        figer(0, function () { o.tape('KeyE'); });
        const fouille = { msg: L.B.msg, gain: p.argent - avant.argent, decor: d.decor, jour: (p.fouilles || {})['cad:' + cle] === p.jour };
        suivant();
        const ensuite = invite();
        o.tape('KeyE');
        const debout = { decor: d.decor, msg: L.B.msg, garde: (p.caddies || {})[cle], x: d.x, y: d.y };
        suivant();
        return { avant: avant, fouille: fouille, ensuite: ensuite, debout: debout,
                 collections: JSON.stringify(p.collections || {}) === avant.collections, apres: invite() };
    """)
    assert not r.get("aucun"), "la ville n'a pas un caddie couché devant lequel se planter"
    assert r["avant"]["invite"] == c["invite_fouiller"], "le caddie couché annonce qu'il se fouille"
    assert r["fouille"]["decor"] == "caddie", "fouillé, il est encore couché"
    assert r["fouille"]["jour"], "la fouille du jour se retient, comme celle d'un bac"
    assert r["fouille"]["gain"] == interactions.FOUILLER["trouvailles"]["monnaie"]["argent"][0]
    assert r["ensuite"] == c["invite_redresser"], "fouillé, ACTION le redresse"
    assert r["debout"]["decor"] == c["debout"], "la deuxième pression le remet sur ses roues"
    assert r["debout"]["msg"] == c["redresse"]
    assert r["debout"]["garde"][:2] == [round(r["debout"]["x"]), round(r["debout"]["y"])], "la partie s'en souvient"
    assert r["collections"], "un caddie ne remplit aucune collection"
    assert r["apres"] != c["invite_redresser"] and r["apres"] != c["invite_fouiller"], "debout, il ne se fouille plus"


def test_un_caddie_peut_ne_rendre_qu_un_objet_drole_qu_on_laisse_la(banc):
    c = interactions.CADDIE
    r = jouer(banc, """
        const k = caddieAPousser(40);
        if (!k) return { aucun: true };
        const argent = p.argent;
        figer(0.99, function () { o.tape('KeyE'); });
        return { msg: L.B.msg, gain: p.argent - argent, decor: k.d.decor };
    """)
    assert not r.get("aucun")
    assert r["msg"] in c["droles"], f"« {r['msg']} » n'est pas un objet drôle du caddie"
    assert r["gain"] == 0 and r["decor"] == "caddie"


# --- Le pousser ------------------------------------------------------------------------------------------


def test_marcher_dans_le_caddie_le_pousse_il_roule_puis_s_arrete_et_la_partie_s_en_souvient(banc):
    r = jouer(banc, """
        const k = redresse(160);
        if (!k) return { aucun: true };
        const d = k.d, cle = L.Caddies.cle(d), x0 = d.x, y0 = d.y;
        // Reculer : on s'en éloigne, il ne bouge pas.
        const recule = SENS.find(function (s) { return s[1] === -k.dx && s[2] === -k.dy; })[0];
        pousser(recule, 20);
        const immobile = Math.hypot(d.x - x0, d.y - y0);
        // Marcher vers lui : il part devant.
        pousser(k.touche, 50);
        const pousse = (d.x - x0) * k.dx + (d.y - y0) * k.dy;
        const devant = (d.x - j.x) * k.dx + (d.y - j.y) * k.dy;
        const lache = (d.x - x0) * k.dx + (d.y - y0) * k.dy;
        nettoyer();
        for (let i = 0; i < 20; i++) o.frame(1);
        const roule = (d.x - x0) * k.dx + (d.y - y0) * k.dy - lache;
        for (let i = 0; i < 300; i++) o.frame(1);
        return { immobile: immobile, pousse: pousse, devant: devant, roule: roule, arrete: !d.vx && !d.vy,
                 garde: p.caddies[cle], x: d.x, y: d.y };
    """)
    assert not r.get("aucun"), "aucun caddie n'a une rue libre devant lui"
    assert r["immobile"] < 1, "on s'en éloigne : il ne bouge pas"
    assert r["pousse"] > 40, f"poussé cinquante images, il n'a fait que {r['pousse']:.0f} px"
    assert r["devant"] > 0, "il roule DEVANT qui le pousse"
    assert r["roule"] > 2, "lâché, il roule encore sur sa lancée"
    assert r["arrete"], "et il finit par s'arrêter"
    assert r["garde"][:2] == [round(r["x"]), round(r["y"])], "la partie le garde là où on l'a laissé"


def test_un_mur_l_arrete_sans_qu_il_y_entre(banc):
    r = jouer(banc, """
        const k = redresse(40);
        if (!k) return { aucun: true };
        const d = k.d, sol = L.DECORS[d.decor].sol, libres = [];
        // On le pousse au bout de la rue libre et contre ce qu'il y a au bout (vingt secondes de pas, au plus).
        for (let i = 0; i < 6; i++) { pousser(k.touche, 200); nettoyer(); }
        for (const sx of [-1, 1]) for (const sy of [-1, 1]) libres.push(L.Monde.solidite(Math.floor((d.x + sx * sol[0]) / TT), Math.floor((d.y + sy * sol[1]) / TT)));
        return { libres: libres, devantUnMur: !L.Entites.decorPeutAller(d, d.x + k.dx * 6, d.y + k.dy * 6) };
    """)
    assert not r.get("aucun")
    assert r["devantUnMur"], "poussé deux cents images de suite, il aurait dû finir contre quelque chose"
    assert r["libres"] == [0, 0, 0, 0], "sa boîte est entrée dans une tuile solide"


BELIER = """
    const k = redresse(200);
    if (!k) return { aucun: true };
    const d = k.d;
    j.endurance = 100;
"""


@pytest.mark.parametrize("sprint", [True, False])
def test_en_belier_il_bouscule_un_passant_sans_le_blesser_et_pas_a_la_course(banc, sprint):
    c = interactions.CADDIE
    r = jouer(banc, BELIER + """
        const e = L.Entites.creerPieton(d.x + k.dx * 70, d.y + k.dy * 70, null);
        e.temoinDuJuge = true; e.etat = 'arret'; e.minuterie = 1e6; e.vx = 0; e.vy = 0;
        const vie = e.vie, crimes = L.B.crimes.length;
        let bouscule = false, mot = null;
        const sprint = %(sprint)s;
        if (sprint) o.touche('ShiftLeft');
        o.touche(k.touche);
        for (let i = 0; i < 70 && !bouscule; i++) { o.frame(1); if (e.recul > 0) { bouscule = true; mot = e.bulle && e.bulle.texte; } }
        o.relacher(k.touche);
        if (sprint) o.relacher('ShiftLeft');
        return { bouscule: bouscule, mot: mot, blesse: vie - e.vie, crimes: L.B.crimes.length - crimes,
                 etoiles: L.B.recherche.etoiles, vivant: e.vivant };
    """ % {"sprint": "true" if sprint else "false"})
    assert not r.get("aucun")
    if sprint:
        assert r["bouscule"], "lancé au sprint, le caddie doit bousculer le passant qu'il touche"
        assert r["mot"] in c["bouscule"], f"le passant bousculé dit « {r['mot']} »"
        assert r["blesse"] == 0 and r["vivant"], "un bélier de caddie ne blesse personne"
        assert r["crimes"] == 0 and r["etoiles"] == 0, "bousculer n'est pas un délit"
    else:
        assert not r["bouscule"], "poussé à la course, il ne bouscule personne : le bélier est un sprint"


@pytest.mark.parametrize("sprint", [True, False])
def test_en_belier_il_cogne_un_char_et_a_la_course_il_s_arrete_contre(banc, sprint):
    c = interactions.CADDIE
    r = jouer(banc, BELIER + """
        // Un char garé en travers de sa route, à quatre-vingts pixels.
        const angle = k.dx ? Math.PI / 2 : 0;
        const v = L.Vehicules.creer('auto', d.x + k.dx * 80, d.y + k.dy * 80, angle, { etat: 'stationne', couleur: '#3a6ea5' });
        v.duJuge = true;
        const vie = v.vie;
        const sprint = %(sprint)s;
        if (sprint) o.touche('ShiftLeft');
        o.touche(k.touche);
        let touche = false;
        for (let i = 0; i < 90; i++) {
            o.frame(1);
            if (L.Vehicules.cercles(v).some(function (q) { return L.Entites.boiteTouche(d, q.x, q.y, q.r + 1); })) touche = true;
        }
        o.relacher(k.touche);
        if (sprint) o.relacher('ShiftLeft');
        return { touche: touche, degats: vie - v.vie, alarme: v.alarme > 0, aAlarme: !!v.def.alarme,
                 avant: (v.x - d.x) * k.dx + (v.y - d.y) * k.dy };
    """ % {"sprint": "true" if sprint else "false"})
    assert not r.get("aucun")
    assert r["touche"], "le caddie n'a jamais atteint le char"
    assert r["avant"] > 0, "il ne passe pas à travers le char"
    if sprint:
        assert r["degats"] >= c["degats_char"], "lancé en bélier, il cogne la tôle"
        assert r["degats"] <= c["degats_char"] * 5, "il cogne, il ne démolit pas"
        if r["aAlarme"]:
            assert r["alarme"], "un char garé qui a une alarme la fait entendre"
    else:
        assert r["degats"] == 0, "poussé à la course, il s'arrête contre le char sans le cogner"


def test_la_partie_rouverte_le_retrouve_debout_la_ou_on_l_a_laisse(banc):
    r = jouer(banc, """
        const k = redresse(120);
        if (!k) return { aucun: true };
        pousser(k.touche, 40);
        for (let i = 0; i < 300; i++) o.frame(1);
        const d = k.d, cle = L.Caddies.cle(d), ou = { x: Math.round(d.x), y: Math.round(d.y) };
        const autres = L.Caddies.liste().filter(function (q) { return q !== d; }).map(function (q) { return L.Caddies.cle(q); });
        // Une partie qu'on rouvre : la même, passée par le JSON de la sauvegarde.
        L.B.partie = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), L.B.defs);
        L.Jeu.commencer();
        const lui = L.Caddies.liste().find(function (q) { return L.Caddies.cle(q) === cle; });
        const couches = L.Caddies.liste().filter(function (q) { return autres.indexOf(L.Caddies.cle(q)) >= 0 && q.decor === 'caddie'; }).length;
        return { ou: ou, lui: lui && { x: lui.x, y: lui.y, decor: lui.decor }, couches: couches, autres: autres.length,
                 indexe: !!lui && L.Entites.decorAutour(lui.x, lui.y, 2).indexOf(lui) >= 0 };
    """)
    assert not r.get("aucun")
    assert r["lui"] and r["lui"]["decor"] == interactions.CADDIE["debout"], "rouverte, la partie l'a recouché"
    assert (round(r["lui"]["x"]), round(r["lui"]["y"])) == (r["ou"]["x"], r["ou"]["y"]), "il n'est plus là où on l'a laissé"
    assert r["indexe"], "remis à sa place, il doit être dans l'index du décor (la foule bute sur lui là où il est)"
    assert r["couches"] == r["autres"], "les caddies qu'on n'a pas touchés restent couchés"


def test_le_caddie_ne_fait_naitre_personne(banc):
    """Redressé, poussé, c'est le MÊME décor : aucune entité de plus, aucun numéro de la suite de la ville."""
    r = jouer(banc, """
        const ids = function () { return L.B.entites.filter(function (e) { return e.type === 'decor' || e.type === 'stop' || e.type === 'feu'; }).map(function (e) { return e.id; }).sort(function (a, b) { return a - b; }).join(','); };
        const avant = ids();
        const k = redresse(120);
        if (!k) return { aucun: true };
        pousser(k.touche, 40);
        return { meme: ids() === avant, panneaux: L.B.entites.filter(function (e) { return /panneau_drole|plaque/.test(e.type + '|' + (e.decor || '')); }).length };
    """)
    assert not r.get("aucun")
    assert r["meme"], "redresser ou pousser un caddie a fait naître ou mourir un décor"
    assert r["panneaux"] == 0, "un panneau drôle ou une plaque est devenu une entité"


# --- La plaque de rue ------------------------------------------------------------------------------------


PLAQUE = """
    function sousLaPlaque(filtre) {
        for (const e of L.B.entites) {
            if (!e.plaque || !filtre(e)) continue;
            for (const s of [[0, 12], [0, -12], [12, 0], [-12, 0]]) {
                j.x = e.x + s[0]; j.y = e.y + s[1]; j.vx = 0; j.vy = 0;
                if (!L.Monde.marchablePieton(Math.floor(j.x / TT), Math.floor(j.y / TT))) continue;
                L.Monde.centrerCamera(j.x, j.y); nettoyer(); o.viser(e);
                if (!personneSousLaMain() || L.Interactions.decorSousLaMain(j) === null) continue;
                if (L.Interactions.decorSousLaMain(j).decor !== e) continue;
                return e;
            }
        }
        return null;
    }
"""


def _attendu(ville, inter):
    """Le nom d'un coin, par la règle des arrêts d'autobus (`autobus.nom_de_coin`)."""
    g, y0 = ville["grille"], ville["grille"]["y0"]
    cx, cy = inter["x"] + (inter["l"] - 1) / 2, inter["y"] + (inter["h"] - 1) / 2
    rue, avenue = re.match(r"(\d+\w+) Rue / (\d+\w+) Avenue", autobus.nom_de_coin(g, cx, cy - y0, "<")).groups()
    # Le quartier, par la règle de `Reputation.quartierA` : la DERNIÈRE zone qui tient le point, en pixels.
    px, py = cx * 16 + 8, cy * 16 + 8
    zone = [z for z in ville["zones"] if z["x"] * 16 <= px < (z["x"] + z["l"]) * 16 and z["y"] * 16 <= py < (z["y"] + z["h"]) * 16][-1]
    nom = next(d["nom"] for d in ville["districts"] if d["slug"] == (zone.get("district") or zone["slug"]))
    return f"COIN {rue} RUE ET {avenue} AVENUE — {nom.upper()}"


@pytest.mark.parametrize("poteau", ["stop", "feu"])
def test_action_sous_une_plaque_dit_le_coin(banc, poteau):
    ville = villes.exporter()
    r = jouer(banc, PLAQUE + """
        const e = sousLaPlaque(function (q) { return q.type === '%s' && q.y > (L.B.defs.carte.grille.y0 || 0) * TT; });
        if (!e) return { aucun: true };
        const inv = invite();
        o.tape('KeyE');
        const lu = { msg: L.B.msg, reste: L.B.msgT };
        // Le dos tourné, on ne lit rien.
        suivant(); L.B.msg = null;
        L.Entites.regarder(j, j.x - e.x, j.y - e.y);
        o.tape('KeyE');
        return { invite: inv, lu: lu, dos: L.B.msg, inter: { x: e.inter.x, y: e.inter.y, l: e.inter.l, h: e.inter.h } };
    """ % poteau)
    assert not r.get("aucun"), f"aucun {poteau} à plaque sous lequel se planter"
    assert r["invite"] == interactions.PLAQUE["invite"]
    assert r["lu"]["msg"] == _attendu(ville, r["inter"])
    assert r["lu"]["reste"] >= interactions.PLAQUE["duree_images"] - 5, "le temps de la lire"
    assert r["dos"] != r["lu"]["msg"], "le dos tourné, ACTION ne lit pas la plaque"


def test_chaque_croisement_a_une_plaque_et_une_seule(banc):
    r = jouer(banc, """
        const par = {};
        for (const e of L.B.entites) if (e.plaque) { const k = e.inter.x + ',' + e.inter.y; par[k] = (par[k] || 0) + 1; }
        const sans = L.Monde.carte.intersections.filter(function (i) { return (i.feux || i.stop) && !par[i.x + ',' + i.y]; }).length;
        return { doubles: Object.keys(par).filter(function (k) { return par[k] > 1; }).length, sans: sans, n: Object.keys(par).length };
    """)
    assert r["n"] > 100
    assert r["doubles"] == 0, "un croisement porte deux plaques"
    assert r["sans"] == 0, "un croisement à feux ou à arrêt n'a pas sa plaque"


def test_la_plaque_et_l_arret_d_autobus_disent_le_meme_coin(banc):
    """La même règle des deux côtés : chaque arrêt nommé d'après son coin (« 4e Rue / 7e Avenue ») est au
    coin que la plaque lirait là."""
    ville = villes.exporter()
    arrets = []
    for a in ville["autobus"]["arrets"]:
        m = re.match(r"(\d+\w+) (Rue|Avenue) / (\d+\w+) (Rue|Avenue)", a["nom"])
        if m:
            noms = {m.group(2): m.group(1), m.group(4): m.group(3)}
            arrets.append({"x": a["x"], "y": a["y"], "rue": noms["Rue"] + " RUE", "avenue": noms["Avenue"] + " AVENUE"})
    assert len(arrets) > 20
    r = jouer(banc, """
        return %s.map(function (a) { return L.Panneaux.coin(a.x, a.y); });
    """ % json.dumps(arrets))
    for a, lu in zip(arrets, r):
        assert (lu["rue"], lu["avenue"]) == (a["rue"], a["avenue"]), f"l'arrêt en ({a['x']}, {a['y']}) : {lu}"


def test_dans_la_bande_du_nord_les_rues_se_comptent_depuis_la_couture(banc):
    ville = villes.exporter()
    r = jouer(banc, """
        const y0 = L.B.defs.carte.grille.y0;
        return { couture: L.Panneaux.coin(40, y0 + 2).rue, juste: L.Panneaux.coin(40, y0 - 14).rue, haut: L.Panneaux.coin(40, 2).rue };
    """)
    n = len(ville["grille_nord"]["rues_h"])
    assert r["couture"] == "1re RUE", "la couture est la 1re Rue de la ville"
    assert r["juste"] == "1re RUE NORD", "la première rue au nord de la couture"
    assert r["haut"] == f"{n - 1}e RUE NORD"


# --- Les panneaux drôles -----------------------------------------------------------------------------------


PANNEAU = """
    function devantLePanneau(p) {
        const x = p[0] * TT + 8, y = p[1] * TT + 15;
        for (const s of [[0, 14], [0, -10], [12, 0], [-12, 0]]) {
            j.x = x + s[0]; j.y = y + s[1]; j.vx = 0; j.vy = 0;
            if (!L.Monde.marchablePieton(Math.floor(j.x / TT), Math.floor(j.y / TT))) continue;
            L.Monde.centrerCamera(j.x, j.y); nettoyer(); o.viser({ x: x, y: y });
            if (!personneSousLaMain()) continue;
            return { x: x, y: y };
        }
        return null;
    }
"""


def test_chaque_panneau_drole_se_lit_une_ligne_par_pression(banc):
    c = interactions.PANNEAU
    r = jouer(banc, PANNEAU + """
        const res = [];
        L.B.defs.panneaux.forEach(function (p) {
            const ou = devantLePanneau(p);
            if (!ou) { res.push(null); return; }
            const lu = { invite: invite(), lignes: [], restes: [] };
            for (let k = 0; k < 4; k++) { o.tape('KeyE'); lu.lignes.push(L.B.msg); lu.restes.push(L.B.msgT); suivant(); }
            const vus = [];
            L.Panneaux.ajouterVisibles(vus, L.B.cam.x, L.B.cam.y);
            lu.peint = vus.some(function (v) { return v.x === ou.x && v.y === ou.y && v.peindreFoire; });
            res.push(lu);
        });
        return res;
    """)
    poses = panneaux.placer(villes.exporter())
    assert len(r) == len(poses)
    for p, lu in zip(poses, r):
        nom = p["lignes"][0]
        assert lu, f"« {nom} » : aucune place pour s'y planter devant"
        assert lu["invite"] == c["invite"], f"« {nom} » : l'invite dit « {lu['invite']} »"
        attendu = [p["lignes"][k % len(p["lignes"])] for k in range(4)]
        assert lu["lignes"] == attendu, f"« {nom} » : {lu['lignes']}"
        assert all(reste >= c["duree_images"] - 5 for reste in lu["restes"])
        assert lu["peint"], f"« {nom} » ne se peint pas à l'écran"


def test_le_panneau_d_un_defi_garde_son_bouton(banc):
    """⚠️ La chaîne d'ACTION : un panneau drôle (ou une plaque) planté contre le panneau d'un défi ne lui
    vole ni son invite ni son bouton — le défi est servi plus haut (`Missions.interagir`)."""
    r = jouer(banc, """
        const panneau = L.B.entites.find(function (e) { return e.type === 'panneau' && e.defi; });
        if (!panneau) return { aucun: true };
        // Un panneau drôle sur la même tuile, plus près de nous que le défi.
        L.B.defs.panneaux.push([Math.floor(panneau.x / TT), Math.floor(panneau.y / TT), 0, ['LE PANNEAU DU JUGE']]);
        j.x = panneau.x; j.y = panneau.y + 10; j.vx = 0; j.vy = 0;
        L.Monde.centrerCamera(j.x, j.y); nettoyer(); o.viser(panneau);
        const sansLeDefi = L.Interactions.decorSousLaMain(j);
        const inv = invite();
        L.B.msg = null;
        o.tape('KeyE');
        return { invite: inv, menu: L.B.menu && L.B.menu.titre, msg: L.B.msg, lisible: !!(sansLeDefi && sansLeDefi.invite === %s) };
    """ % json.dumps(interactions.PANNEAU["invite"]))
    assert not r.get("aucun"), "aucun panneau de défi dans la ville"
    assert r["lisible"], "le juge n'a pas mis le panneau drôle à portée : il jugerait le vide"
    assert r["invite"] == "DÉFI", f"l'invite dit « {r['invite']} »"
    assert r["menu"], "ACTION devant le panneau d'un défi doit proposer le défi"
    assert r["msg"] != "LE PANNEAU DU JUGE", "le panneau drôle a volé le bouton du défi"


def test_chaque_ligne_lue_tient_dans_le_toast(banc):
    """Le toast du HUD est une ligne à l'échelle 2 (`Hud.dessinerMessage`) : une ligne plus large sortirait
    de l'écran. Les panneaux, les objets du caddie, et la plaque de chaque croisement de la ville."""
    lignes = [ligne for p in panneaux.PANNEAUX for ligne in p["lignes"]]
    lignes += list(interactions.CADDIE["droles"]) + [interactions.CADDIE["redresse"]]
    r = jouer(banc, """
        const lignes = %s;
        for (const e of L.B.entites) if (e.plaque) lignes.push(L.Panneaux.nomDuCroisement(e.inter));
        return lignes.map(function (l) { return { l: l, px: L.Atlas.largeurTexte(l, 2) + 12, ecran: L.VW }; });
    """ % json.dumps(lignes, ensure_ascii=False))
    assert len(r) > len(lignes) + 100
    for m in r:
        assert m["l"] and m["px"] <= m["ecran"], f"« {m['l']} » fait {m['px']} px, l'écran {m['ecran']}"
