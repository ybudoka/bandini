"""Les velos : la bordure, le virage a gauche, le trottoir, le parc — et les enfants a velo.

Demande de Martin (21 sept. 2026) : « les velos peuvent passer dans les parcs, les
trottoirs, et restent souvent sur la bordure de la route, sauf pour virage a gauche.
Je veux aussi des enfants a velo, seulement sur trottoir, casque, parc. »

Le velo du trafic reste un char sur des rails : ces juges regardent OU il roule
(l'ecart au centre de sa voie, les tuiles qu'il foule hors de la rue) et ce qu'il ne
tire pas (aucun de). L'enfant a velo est un passant : on juge ou il nait, quand, et
qu'il ne pose jamais une roue sur la rue — pas meme sur la traverse.
"""

import pytest

from app import pietons, vehicules

# Le decor commun : le joueur a l'ecart (invincible, il ne juge rien), la rue videe de
# ses chars, et de quoi faire naitre un velo du trafic ou l'on veut.
DECOR = """
        L.Jeu.commencer();
        L.graine(5);
        const T = L.TT, M = L.Monde, V = L.Vehicules;
        const PAS = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] };
        const f = L.B.defs.conduite.trafic.velo;
        const j = L.B.joueur; j.invincible = 99999;
        const poserJoueur = function (x, y) { j.x = x; j.y = y; M.centrerCamera(x, y); };
        const viderLaRue = function () { L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; }); };
        const velo = function (tx, ty, sens, options) {
            const p = PAS[sens];
            const v = V.creer('velo', tx * T + 8, ty * T + 8, Math.atan2(p[1], p[0]),
                              Object.assign({ conducteur: 'trafic', etat: 'roule', sens: sens }, options || {}));
            L.Entites.indexer();
            return v;
        };
        // L'ecart a DROITE du centre de sa voie (le cote du trottoir), en pixels.
        const aDroite = function (v, sens) {
            const p = PAS[sens], tx = Math.floor(v.x / T), ty = Math.floor(v.y / T);
            return (v.x - (tx * T + 8)) * -p[1] + (v.y - (ty * T + 8)) * p[0];
        };
"""


def test_le_velo_roule_a_la_bordure_et_l_auto_au_milieu(banc):
    """Le velo se tasse vers le trottoir (`bord_px`) ; l'auto, a cote, garde le
    milieu de sa voie — c'est la classe qui decide, pas la rue."""
    r = banc("""function (L, o) {""" + DECOR + """
        const b = o.boulevard(false);
        poserJoueur(b.x, b.y - 3 * T);
        viderLaRue();
        const v = velo(b.tx, b.ty, '>');
        const a = V.creer('auto', b.x, b.y + 0.01, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        a.x -= 3 * T;
        L.Entites.indexer();
        const ecarts = [], auto = [];
        for (let i = 0; i < 160; i++) {
            o.frame(1);
            if (i < 40 || i % 10) continue;
            if (M.fleche(Math.floor(v.x / T), Math.floor(v.y / T)) === '>') ecarts.push(aDroite(v, '>'));
            if (M.fleche(Math.floor(a.x / T), Math.floor(a.y / T)) === '>') auto.push(aDroite(a, '>'));
        }
        return { bord: f.bord_px, ecarts: ecarts, auto: auto };
    }""")
    assert len(r["ecarts"]) >= 6 and len(r["auto"]) >= 6
    assert all(abs(e - r["bord"]) < 0.6 for e in r["ecarts"]), \
        f"le velo n'est pas a la bordure ({r['bord']} px a droite) : {r['ecarts']}"
    assert all(abs(e) < 0.6 for e in r["auto"]), f"l'auto a quitte le milieu de sa voie : {r['auto']}"


def test_il_se_range_a_gauche_pour_tourner_a_gauche_et_tourne(banc):
    """A `virage_tuiles` de la ligne, celui qui va tourner a gauche se range a
    gauche (vers la ligne du milieu), attend la, et tourne ; les autres restent a
    la bordure jusqu'a la ligne."""
    r = banc("""function (L, o) {""" + DECOR + """
        const b = o.boulevard(false);
        poserJoueur(b.x, b.y - 3 * T);
        viderLaRue();
        const suivre = function (voulu) {
            for (let essai = 0; essai < 60; essai++) {
                const v = velo(b.tx + 8, b.ty, '>');
                let n = 0;
                while (!v.intention && n++ < 400) o.frame(1);
                if (v.intention && v.intention.ordre[0] === voulu) {
                    const approche = [];
                    let sortie = null;
                    for (let i = 0; i < 900 && !sortie; i++) {
                        o.frame(1);
                        const fl = M.fleche(Math.floor(v.x / T), Math.floor(v.y / T));
                        if ((fl === '>' || fl === 'S') && v.sens === '>' && i % 5 === 0) approche.push(aDroite(v, '>'));
                        if (v.sens !== '>' && PAS[fl]) sortie = v.sens;
                        if (v.sens === '>' && PAS[fl] && v.intention === null && i > 60) sortie = '>';
                    }
                    L.Entites.retirer(v);
                    return { approche: approche, sortie: sortie };
                }
                L.Entites.retirer(v);
            }
            return null;
        };
        return { bord: f.bord_px, gauche: suivre('gauche'), droit: suivre('droit') };
    }""")
    assert r["gauche"] and r["droit"], "aucun cycliste de chaque sorte trouve en soixante essais"
    g, d = r["gauche"], r["droit"]
    # Il glisse vers la gauche en une tuile, puis il y reste jusqu'a la ligne.
    fin = g["approche"][len(g["approche"]) // 2:]
    assert fin and all(abs(e + r["bord"]) < 0.8 for e in fin), \
        f"celui qui tourne a gauche n'est pas range a gauche : {g['approche']}"
    assert g["sortie"] == "^", f"il s'est range a gauche puis est sorti par {g['sortie']!r}"
    assert d["approche"] and all(abs(e - r["bord"]) < 0.8 for e in d["approche"]), \
        f"celui qui va tout droit a quitte la bordure : {d['approche']}"


def test_l_intention_se_lit_a_l_empreinte_sans_un_de(banc):
    """⚠️ Aucun de : un de de plus decale tout ce qui nait apres. L'intention se lit
    a l'empreinte du cycliste et du croisement — la meme a chaque lecture — et elle
    commence par un bras qui existe."""
    r = banc("""function (L, o) {""" + DECOR + """
        const b = o.boulevard(false);
        poserJoueur(b.x, b.y - 3 * T);
        viderLaRue();
        const rng = L.B.rng; let des = 0;
        const lues = [];
        for (let k = 0; k < 40; k++) {
            // A une tuile de la ligne d'arret : on la voit a coup sur.
            let tx = b.tx; while (M.fleche(tx + 1, b.ty) === '>') tx++;
            const v = velo(tx, b.ty, '>');
            L.B.rng = function () { des++; return rng(); };
            const i1 = V.intentionDuVelo(v, tx, b.ty, [1, 0]);
            v.intention = null;
            const i2 = V.intentionDuVelo(v, tx, b.ty, [1, 0]);
            L.B.rng = rng;
            lues.push({ a: i1 && i1.ordre.join(), b: i2 && i2.ordre.join(), bras: i1 && i1.inter.bras });
            L.Entites.retirer(v);
        }
        return { des: des, lues: lues };
    }""")
    assert r["des"] == 0, f"l'intention du cycliste a tire {r['des']} de(s)"
    assert all(q["a"] and q["a"] == q["b"] for q in r["lues"]), "l'intention change d'une lecture a l'autre"
    premiers = {q["a"].split(",")[0] for q in r["lues"]}
    assert len(premiers) >= 2, f"tous les cyclistes vont au meme endroit : {premiers}"


def test_sur_une_rue_a_deux_voies_il_revient_a_celle_du_trottoir(banc):
    """Ne dans la voie du milieu, sans virage a gauche en vue, il se tasse dans la
    voie du trottoir — et y reste a la bordure."""
    r = banc("""function (L, o) {""" + DECOR + """
        const b = o.boulevard(true);            // b : la voie du trottoir ; celle du nord va dans le meme sens
        if (!b) return null;
        poserJoueur(b.x, b.y - 4 * T);
        viderLaRue();
        const v = velo(b.tx, b.ty - 1, '>');
        for (let i = 0; i < 200; i++) o.frame(1);
        return { ty: Math.floor(v.y / T), attendu: b.ty, ecart: aDroite(v, '>'), bord: f.bord_px, gauche: v.intention && v.intention.ordre[0] };
    }""")
    assert r is not None, "la carte n'a pas de rue a deux voies par sens"
    if r["gauche"] != "gauche":
        assert r["ty"] == r["attendu"], f"le velo est reste dans la voie du milieu : {r}"
        assert abs(r["ecart"] - r["bord"]) < 0.8, f"revenu dans la voie du trottoir, mais pas a la bordure : {r}"


def _parc(banc, corps):
    """Un velo sur la voie du bord d'un parc, `parc_chance` a 1 : il y entre."""
    return banc("""function (L, o) {""" + DECOR + """
        let d = null;
        const c = M.carte;
        for (let y = 5; y < c.h - 5 && !d; y++) for (let x = 5; x < c.w - 5 && !d; x++) {
            const fl = M.fleche(x, y), p = PAS[fl];
            if (!p) continue;
            const q = [-p[1], p[0]];
            if (!M.estTrottoir(x + q[0], y + q[1]) || M.glyphe(x + 2 * q[0], y + 2 * q[1]) !== 'g') continue;
            d = { tx: x - 3 * p[0], ty: y - 3 * p[1], sens: fl, q: q };
        }
        poserJoueur(d.tx * T + 8 - d.q[0] * 60, d.ty * T + 8 - d.q[1] * 60);      // de l'autre cote de la rue
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' && e.type !== 'pieton'; });
        L.B.options.trace = true;
        f.parc_chance = 1;
        const v = velo(d.tx, d.ty, d.sens);
    """ + corps + "}")


def test_un_velo_traverse_le_parc_par_ses_allees_et_redescend(banc):
    """Il entre, ne foule que le trottoir et les ALLEES (jamais la pelouse ou l'on
    seme les arbres), passe par au moins `parc_allees_min` tuiles d'allee, et
    redescend dans une voie ou le trottoir est a sa droite — sans que la trace du
    trafic ne crie au hors-voie."""
    r = _parc(banc, """
        const foules = [], allees = new Set();
        let parti = false, revenu = null;
        for (let i = 0; i < 2400 && !revenu; i++) {
            o.frame(1);
            if (v.horsRue) {
                parti = true;
                const tx = Math.floor(v.x / T), ty = Math.floor(v.y / T), g = M.glyphe(tx, ty);
                foules.push(g);
                if (g === 'g') allees.add(tx + ',' + ty);
            } else if (parti && PAS[M.fleche(Math.floor(v.x / T), Math.floor(v.y / T))]) {
                revenu = { sens: v.sens, fleche: M.fleche(Math.floor(v.x / T), Math.floor(v.y / T)) };
            }
        }
        const pelouse = foules.filter(function (g) { return g === ','; }).length;
        // Ce qu'il a roule de trottoir APRES la derniere allee, avant de redescendre.
        const apres = foules.slice(foules.lastIndexOf('g') + 1).filter(function (g) { return g === '.'; }).length;
        return { parti: parti, allees: allees.size, pelouse: pelouse, foules: foules.length, revenu: revenu, apres: apres,
                 min: f.parc_allees_min, conducteur: v.conducteur,
                 anomalies: L.B.trace.anomalies.map(function (a) { return a.quoi; }) };
    """)
    assert r["parti"], "le velo n'est jamais entre dans le parc"
    assert r["allees"] >= r["min"], f"il n'a roule que sur {r['allees']} tuiles d'allee"
    # Le lissage coupe un coin de place de biais : quelques relevés a cheval, pas plus.
    assert r["pelouse"] <= r["foules"] * 0.05, f"{r['pelouse']} releves sur la pelouse (sur {r['foules']})"
    assert r["revenu"] and r["revenu"]["sens"] == r["revenu"]["fleche"], f"il n'est pas redescendu dans une voie : {r}"
    # ⚠️ Il redescend A LA SORTIE de l'allee : pas cinq tuiles de trottoir a rebours.
    assert r["apres"] <= 40, f"{r['apres']} images sur le trottoir entre la sortie du parc et la voie"
    assert r["conducteur"] == "trafic"
    assert r["anomalies"] == [], f"la trace a crie : {r['anomalies']}"


def test_sur_le_trottoir_il_va_au_pas_cede_au_passant_et_sonne(banc):
    """⚠️ Au pas, et en cedant : il ne depasse jamais `trottoir_vitesse`, s'arrete
    derriere un passant plante sur son chemin, sonne — et ne blesse personne."""
    r = banc("""function (L, o) {""" + DECOR + """
        const b = o.boulevard(false);
        poserJoueur(b.x, b.y - 4 * T);
        viderLaRue();
        f.trottoir_chance = 1; f.trottoir_tuiles = [5, 10];
        const v = velo(b.tx, b.ty, '>');
        o.frame(2);
        if (!v.horsRue) return { parti: false };
        // Un passant plante sur le trottoir, quatre tuiles plus loin.
        const t = v.horsRue.chemin[Math.min(3, v.horsRue.chemin.length - 1)];
        const p = L.Entites.creerPieton(t.x, t.y, L.Entites.archetype('passant'));
        p.etat = 'fige'; p.plante = { x: t.x, y: t.y };
        L.Entites.indexer();
        let vmax = 0, dmin = Infinity, sonne = false;
        for (let i = 0; i < 180; i++) {
            o.frame(1);
            if (v.horsRue) vmax = Math.max(vmax, Math.hypot(v.vx, v.vy));
            dmin = Math.min(dmin, Math.hypot(v.x - p.x, v.y - p.y));
            if (v.klaxonT > 0) sonne = true;
        }
        return { parti: true, vmax: vmax, dmin: dmin, sonne: sonne, vie: p.vie, vieMax: p.vieMax,
                 pas: f.trottoir_vitesse, renverse: L.B.defs.conduite.physique.renverse_vitesse_min };
    }""")
    assert r["parti"], "le velo n'est pas monte sur le trottoir"
    assert r["vmax"] <= r["pas"] + 1e-6 < r["renverse"], f"il roule a {r['vmax']} px/image sur le trottoir"
    assert r["dmin"] > 16, f"il est rentre dans le passant ({r['dmin']:.1f} px)"
    assert r["sonne"], "il ne sonne pas au passant qu'il a devant"
    assert r["vie"] == r["vieMax"], "le passant a ete blesse"


def test_coince_derriere_un_char_arrete_un_cycliste_sur_deux_monte_sur_le_trottoir(banc):
    """Un char arrete bouche la voie : certains cyclistes (`coince_part`, a
    l'empreinte) montent sur le trottoir et le longent ; les autres attendent."""
    r = banc("""function (L, o) {""" + DECOR + """
        const b = o.boulevard(false);
        poserJoueur(b.x, b.y - 4 * T);
        let montes = 0, attendent = 0;
        f.trottoir_chance = 0; f.parc_chance = 0;      // seul le bouchon fait monter
        for (let k = 0; k < 16; k++) {
            viderLaRue();
            const bouchon = V.creer('auto', (b.tx + 4) * T + 8, b.y, 0, { etat: 'stationne' });
            const v = velo(b.tx, b.ty, '>');
            let monte = false;
            for (let i = 0; i < 160 && !monte; i++) {
                o.frame(1);
                if (v.horsRue) monte = true;
            }
            if (monte) montes++; else attendent++;
            L.Entites.retirer(v); L.Entites.retirer(bouchon);
        }
        return { montes: montes, attendent: attendent };
    }""")
    assert r["montes"] > 0, "aucun cycliste coince n'est monte sur le trottoir"
    assert r["attendent"] > 0, "tous les cyclistes coinces montent sur le trottoir : ce n'est plus un sur deux"


@pytest.mark.parametrize("graine", [
    1,
    # ⚠️ DEUX FACONS DE RESTER HORS VOIE EN REDESCENDANT DU TROTTOIR (26 sept. 2026, ligne du plan
    # « Un velo qui redescend du trottoir reste plante »). Graine 5 : une remorqueuse arretee au feu
    # pile sur la tuile de retour ; le velo attendait quatre secondes, rendait son tour de trottoir
    # et restait plante sur la bordure (HORS VOIE, puis le chien de garde) — il attend maintenant
    # avec la file (`attendVoie`). Graine 23 : la voie libre au bout du trottoir, puis un char qui
    # arrive pendant qu'il descend ; il cede en bordure, et la trace le croyait perdu — il
    # `redescend`, jusqu'a toucher la voie. Mesure : 40 graines sur 40 propres (base : 39).
    5,
    23,
])
def test_la_ville_roule_avec_ses_velos_sans_une_anomalie(banc, graine):
    """Toute la ville, la trace allumee, des velos qui montent souvent : la
    surveillance du trafic ne releve ni hors-voie, ni chien de garde, ni tour en rond."""
    r = banc("""function (L, o) {""" + DECOR.replace("L.graine(5)", "L.graine(%d)" % graine) + """
        L.B.options.trace = true;
        f.trottoir_chance = 0.2; f.parc_chance = 0.5;
        L.Vehicules.monter(L.B.joueur, o.char('auto', 0, 0, 0));
        const velos = new Set(), partis = new Set();
        for (let i = 0; i < 3000; i++) {
            o.frame(1);
            if (i % 20) continue;
            L.B.entites.forEach(function (v) {
                if (v.type !== 'vehicule' || v.conducteur !== 'trafic' || v.def.classe !== 'velo') return;
                velos.add(v.id);
                if (v.horsRues) partis.add(v.id);
            });
        }
        return { velos: velos.size, partis: partis.size,
                 anomalies: L.B.trace.anomalies.map(function (a) { return a.quoi + ' ' + a.slug + ' ' + a.etat; }) };
    }""")
    assert r["velos"] > 0 and r["partis"] > 0, f"aucun velo n'a quitte la rue : {r}"
    assert r["anomalies"] == [], f"la trace a releve : {r['anomalies']}"


# --- Les enfants a velo -------------------------------------------------------------------

ENFANTS = """
        const E = L.Entites, a = E.archetype('enfant_velo');
        const aller = function (district, heure) {
            const z = M.carte.zones.find(function (q) { return q.district === district; });
            const tr = E.trottoirLePlusProche(Math.floor((z.x + z.l / 2)), Math.floor((z.y + z.h / 2)));
            poserJoueur(tr ? tr.x : (z.x + z.l / 2) * T, tr ? tr.y : (z.y + z.h / 2) * T);
            L.B.partie.heure = heure;
            L.B.entites = L.B.entites.filter(function (e) { return e.arch !== 'enfant_velo'; });
        };
        const enfants = function () { return L.B.entites.filter(function (e) { return e.type === 'pieton' && e.arch === 'enfant_velo' && e.vivant; }); };
"""


def test_les_enfants_a_velo_naissent_le_jour_dans_leurs_quartiers_sans_un_de(banc):
    r = banc("""function (L, o) {""" + DECOR + ENFANTS + """
        const rng = L.B.rng; let des = 0;
        aller('erables', 0.5);
        L.B.rng = function () { des++; return rng(); };
        let nes = 0;
        for (let k = 0; k < 6; k++) nes += E.naitreLesEnfantsAVelo();
        L.B.rng = rng;
        const fiche = function (e) {
            const z = M.zoneA(e.x, e.y);
            return { casque: e.swaps.e, route: M.estRoute(Math.floor(e.x / T), Math.floor(e.y / T)),
                     vu: E.visibleAEcran(e.x, e.y, 0), intouchable: e.intouchable, sprite: e.sprite,
                     district: z ? z.district : null };
        };
        const jour = enfants().map(fiche);
        aller('erables', 0.95);
        let nuit = 0; for (let k = 0; k < 4; k++) nuit += E.naitreLesEnfantsAVelo();
        // Dans La Shop, s'il en nait, c'est au bord d'un quartier qui en veut.
        aller('shop', 0.5);
        for (let k = 0; k < 4; k++) E.naitreLesEnfantsAVelo();
        const shop = enfants().map(fiche);
        return { des: des, nes: nes, jour: jour, nuit: nuit, shop: shop, combien: L.B.defs.pietons.enfants_a_velo.combien,
                 casques: L.B.defs.pietons.enfants_a_velo.casques, districts: a.districts };
    }""")
    assert r["des"] == 0, f"la naissance d'un enfant a velo a tire {r['des']} de(s)"
    assert r["nes"] == r["combien"] == len(r["jour"]), f"il en nait {r['nes']}, on en veut {r['combien']}"
    for e in r["jour"]:
        assert e["sprite"] == "enfant_velo" and e["intouchable"], e
        assert not e["route"], "un enfant a velo est ne sur la rue"
        assert not e["vu"], "un enfant a velo est ne sous les yeux du joueur"
        assert e["casque"] in r["casques"], e
    assert r["nuit"] == 0, "des enfants a velo naissent la nuit"
    assert all(e["district"] in r["districts"] for e in r["jour"] + r["shop"]), \
        f"un enfant a velo est ne hors de ses quartiers : {[e['district'] for e in r['jour'] + r['shop']]}"


def test_l_enfant_a_velo_ne_pose_jamais_une_roue_sur_la_rue(banc):
    """Ni la chaussee, ni la traverse : le trottoir, l'abord, la pelouse et l'allee.
    ⚠️ Meme en detalant — on lui fait peur toutes les deux secondes."""
    r = banc("""function (L, o) {""" + DECOR + ENFANTS + """
        aller('erables', 0.5);
        for (let k = 0; k < 2; k++) E.naitreLesEnfantsAVelo();
        const les = enfants();
        let releves = 0, rue = 0, bouge = 0, fuites = 0;
        const sols = {};
        for (let i = 0; i < 2400; i++) {
            if (i % 120 === 60) les.forEach(function (e) { if (e.vivant) { e.etat = 'fuit'; e.menace = { x: e.x + 30, y: e.y + 5 }; e.minuterie = 90; fuites++; } });
            o.frame(1);
            if (i % 6) continue;
            les.forEach(function (e) {
                if (!e.vivant || !e.actif) return;
                const tx = Math.floor(e.x / T), ty = Math.floor(e.y / T);
                releves++;
                if (M.estRoute(tx, ty)) rue++;
                if (Math.abs(e.vx) + Math.abs(e.vy) > 0.3) bouge++;
                const g = M.glyphe(tx, ty); sols[g] = (sols[g] || 0) + 1;
            });
        }
        return { releves: releves, rue: rue, bouge: bouge, fuites: fuites, sols: sols };
    }""")
    assert r["releves"] > 300, r
    assert r["rue"] == 0, f"{r['rue']} releves d'enfant a velo sur la rue : {r['sols']}"
    assert r["bouge"] > r["releves"] * 0.3, f"il ne roule presque pas : {r}"


def test_face_a_la_traverse_l_enfant_a_velo_fait_demi_tour(banc):
    """Pose au bord d'un passage pieton, tourne vers lui, au feu des pietons ou pas :
    il ne s'y engage jamais. Et aucune traverse de la ville n'est roulable pour lui."""
    r = banc("""function (L, o) {""" + DECOR + ENFANTS + """
        const c = M.carte;
        let passages = 0, roulables = 0;
        for (let y = 0; y < c.h; y++) for (let x = 0; x < c.w; x++) {
            if (!M.estPassage(x, y)) continue;
            passages++;
            if (E.roulableEnfant(x, y)) roulables++;
        }
        // Des coins de trottoir qui touchent un passage, a l'est ou a l'ouest.
        const coins = [];
        // ⚠️ `:` traverse une rue nord-sud : c'est lui qui borde un trottoir a l'est ou a l'ouest.
        for (let y = 5; y < c.h - 5 && coins.length < 6; y++) for (let x = 5; x < c.w - 5 && coins.length < 6; x += 7) {
            if (M.glyphe(x, y) !== '.' || M.estRoute(x, y)) continue;
            if (M.glyphe(x + 1, y) === ':') coins.push({ x: x, y: y, dir: 0 });
            else if (M.glyphe(x - 1, y) === ':') coins.push({ x: x, y: y, dir: 2 });
        }
        let releves = 0, rue = 0;
        L.B.partie.heure = 0.5;
        coins.forEach(function (k) {
            poserJoueur(k.x * T + 8, (k.y - 6) * T);
            const e = E.creerPieton(k.x * T + 8, k.y * T + 8, a);
            e.dir = k.dir; e.butT = 999;
            for (let i = 0; i < 240; i++) {
                o.frame(1);
                releves++;
                if (M.estRoute(Math.floor(e.x / T), Math.floor(e.y / T))) rue++;
            }
            E.retirer(e);
        });
        return { passages: passages, roulables: roulables, coins: coins.length, releves: releves, rue: rue };
    }""")
    assert r["passages"] > 0 and r["roulables"] == 0, f"{r['roulables']} tuiles de traverse roulables pour l'enfant"
    assert r["coins"] >= 3, r
    assert r["rue"] == 0, f"face a la traverse, il s'y est engage ({r['rue']} releves sur {r['releves']})"


def test_l_enfant_a_velo_a_un_casque_et_un_corps_a_lui(banc):
    """Le casque se voit sur les trois faces (les rangees du haut portent la
    lettre du casque), deux images par face pour les pedales, et le casque
    change d'un enfant a l'autre."""
    r = banc("""function (L, o) {""" + DECOR + """
        const s = L.SPRITES.enfant_velo;
        const faces = {};
        ['bas', 'haut', 'cote'].forEach(function (n) {
            faces[n] = s.poses[n].map(function (g) {
                return { casque: g.slice(0, 3).join('').split('e').length - 1, h: g.length,
                         w: Math.max.apply(null, g.map(function (l) { return l.length; })) };
            });
        });
        const cuit = L.Atlas.cuire('enfant_velo', s, null);
        return { faces: faces, w: s.w, h: s.h, swaps: s.swaps, poses: Object.keys(cuit.poses) };
    }""")
    for nom, images in r["faces"].items():
        assert len(images) == 2, f"{nom} : {len(images)} image(s), il en faut deux (les pedales)"
        for i in images:
            assert i["casque"] >= 8, f"{nom} : le casque ne se voit pas ({i['casque']} pixels en haut)"
            assert i["h"] == r["h"] and i["w"] == r["w"], f"{nom} : grille de {i['w']}x{i['h']}"
    assert {"e", "v", "c"} <= set(r["swaps"]), r["swaps"]
    assert {"bas", "haut", "droite", "gauche"} <= set(r["poses"]), r["poses"]


def test_de_face_et_de_dos_on_voit_le_velo_et_il_est_assis_dessus(banc):
    """Martin (22 sept. 2026) : « ameliore les images de face et de dos ». La
    premiere version etait un enfant en croix au-dessus d'une barre noire. Ce qui
    dit « un enfant ASSIS sur un velo » : de face le phare ; de dos le
    catadioptre, seul (colle au cadre rouge, il disparaissait) ; des deux cotes
    la couleur du cadre autour de la roue ; chaque chaussure sur sa pedale, et
    au sol la roue seule — les pieds en l'air."""
    r = banc("""function (L, o) {
        return L.SPRITES.enfant_velo.poses;
    }""")
    for face in ("bas", "haut"):
        for i, g in enumerate(r[face]):
            nom = f"{face}[{i}]"
            assert set(g[-1]) <= {".", "r"}, f"{nom} : au sol, autre chose que la roue : {g[-1]!r}"
            assert any("v" in rang for rang in g[9:]), f"{nom} : la couleur du cadre ne se voit pas autour de la roue"
            chaussures = [(y, x) for y, rang in enumerate(g) for x, c in enumerate(rang) if c == "b"]
            assert chaussures, f"{nom} : pas de pieds"
            for y, x in chaussures:
                assert g[y + 1][x] == "m", f"{nom} : la chaussure en ({x}, {y}) n'est pas sur sa pedale"
            if face == "bas":
                assert any("l" in rang for rang in g[7:12]), f"{nom} : pas de phare au guidon"
            else:
                reflets = [(y, x) for y, rang in enumerate(g) for x, c in enumerate(rang) if c == "t"]
                assert reflets, f"{nom} : pas de catadioptre"
                for y, x in reflets:
                    assert g[y][x - 1] != "v" and g[y][x + 1] != "v", f"{nom} : le catadioptre colle au cadre"


def test_la_fiche_de_l_enfant_a_velo():
    """Il ne se tire pas dans la foule, il est intouchable, il ne temoigne pas —
    et le jour, dans les quartiers qui ont des parcs."""
    a = next(p for p in pietons.CATALOGUE if p["slug"] == "enfant_velo")
    assert a["frequence"] == 0.0 and a["metier"] == "cycliste" and a["sprite"] == "enfant_velo"
    assert a["intouchable"] and a["temoin"] == 0.0
    assert set(a["districts"]) <= {"erables", "pointe", "faubourg"}
    assert 0.2 < a["heures"][0] < a["heures"][1] < 0.85
    f = pietons.exporter()["enfants_a_velo"]
    assert f["combien"] >= 1 and len(f["casques"]) >= 4


def test_la_fiche_du_velo_du_trafic():
    """Au pas sur le trottoir (sous la vitesse qui renverse), a la bordure sans
    sortir de sa voie, et des chances qui gardent le velo SURTOUT sur la rue."""
    f = vehicules.TRAFIC["velo"]
    demi_voie = 8 - [v for v in vehicules.CATALOGUE if v["slug"] == "velo"][0]["largeur"] / 2
    assert 0 < f["bord_px"] <= demi_voie
    assert f["trottoir_vitesse"] < vehicules.PHYSIQUE["renverse_vitesse_min"]
    assert f["trottoir_chance"] <= 0.02 and f["parc_chance"] <= 0.1
    assert f["trottoir_tuiles"][0] <= f["trottoir_tuiles"][1]
