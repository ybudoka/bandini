"""Les Mantes, au banc : un gang qui sait se battre (docs/jalons/l-ecole-rivale.md).

Les juges de la fiche : un Mante finit par projeter le joueur ; le joueur projeté retombe sur une tuile
libre, couché sans être assommé ; aucun dé consommé. Et ce qui les rend « plus durs » : ils parent ton coup,
ils tiennent plus longtemps qu'un autre gang au même duel, et ils couchent les Cravates à la frontière.

⚠️ Le joueur se joue AU BOUTON (FRAPPE `KeyJ`, ESQUIVE `ShiftLeft`, SAISIR `KeyU`) ; le Mante, lui, joue
sa propre tête (`attaque_joueur`, `bagarre`). La rue est vidée et le trafic coupé : un passant de plus ou
un char qui passe changeraient ce qu'on mesure.
"""

import pytest

#: Une partie, la rue vide, un homme de `arch` posé à `dx` du joueur, qui l'attaque.
PREPARER = """
    function preparer(L, o, arch, dx) {
        L.Jeu.commencer();
        L.B.defs.conduite.trafic.vehicules_max = 0;
        for (let i = L.B.entites.length - 1; i >= 0; i--) {
            const q = L.B.entites[i];
            if (q.type === 'pieton' || q.type === 'vehicule') L.Entites.retirer(q);
        }
        const m = o.poser(arch, dx === undefined ? 40 : dx, 0);
        m.etat = 'attaque_joueur';
        return m;
    }
    function tuileLibre(L, x, y) {
        return L.Monde.solidite(Math.floor(x / L.TT), Math.floor(y / L.TT)) === 0;
    }
"""


def test_un_mante_finit_par_projeter_le_joueur_qui_se_couche_sans_etre_assomme(banc):
    """Le juge de la fiche. Le joueur ne fait rien ; le Mante le saisit, le projette, et le joueur
    retombe sur une tuile libre — couché le temps de reprendre son souffle, pas assommé —, puis se relève
    et marche."""
    r = banc("""function (L, o) {
        %s
        const m = preparer(L, o, 'mante'), j = L.B.joueur;
        let saisi = 0, vol = null, couche = null, releve = null, vieAvant = j.vie;
        for (let t = 0; t < 900 && releve === null; t++) {
            o.frame(1);
            if (j.saisiPar === m) saisi++;
            if (j.vol && !vol) vol = { t: t, tech: j.vol.tech };
            if (vol && !j.vol && couche === null) couche = { t: t, auSol: j.auSol, face: j.face, etat: j.etat,
                                                             libre: tuileLibre(L, j.x, j.y), vie: j.vie };
            if (couche && !(j.auSol > 0)) releve = t;
        }
        // Relevé, il marche : un pas vers la droite.
        const x0 = j.x;
        o.touche('KeyD'); o.frame(20); o.relacher('KeyD'); o.frame(1);
        return { saisi: saisi, vol: vol, couche: couche, releve: releve, vieAvant: vieAvant, marche: j.x - x0 };
    }""" % PREPARER)
    assert r["vol"], f"le Mante n'a jamais projeté le joueur : {r}"
    assert r["vol"]["tech"] in ("projection_hanche", "grand_fauchage", "retournement_poignet"), r
    assert r["saisi"] >= 15, f"la prise n'a pas tenu le temps d'une roulade : {r}"
    c = r["couche"]
    assert c and c["libre"], f"le joueur est retombé dans un mur : {r}"
    assert c["auSol"] > 0 and c["face"] == "couche" and c["etat"] != "assomme", r
    assert c["vie"] < r["vieAvant"], "la chute n'a pas fait mal"
    assert r["releve"] is not None and r["releve"] - c["t"] <= 60, f"il ne s'est pas relevé : {r}"
    assert r["marche"] > 10, f"relevé, il ne marche plus : {r}"


def test_projete_contre_un_mur_il_retombe_sur_une_tuile_libre(banc):
    """Le joueur dos à un mur, le Mante devant : la projection de hanche l'enverrait dans la façade. Il
    retombe sur la dernière tuile libre avant elle."""
    r = banc("""function (L, o) {
        %s
        const m = preparer(L, o, 'mante', 200), j = L.B.joueur, TT = L.TT;
        // Un mur plein est a trois tuiles et plus a l'est d'une tuile libre, avec des tuiles libres entre.
        let place = null;
        const tx0 = Math.floor(j.x / TT), ty0 = Math.floor(j.y / TT);
        for (let r = 0; r < 40 && !place; r++) {
            for (let dy = -r; dy <= r && !place; dy++) {
                for (let dx = -r; dx <= r && !place; dx++) {
                    const tx = tx0 + dx, ty = ty0 + dy;
                    if (L.Monde.solidite(tx, ty) !== 0 || L.Monde.solidite(tx - 1, ty) !== 0) continue;
                    if (L.Monde.solidite(tx + 1, ty) === 0 && L.Monde.solidite(tx + 2, ty) !== 0) place = { tx: tx, ty: ty };
                }
            }
        }
        if (!place) return { place: null };
        j.x = place.tx * TT + 8; j.y = place.ty * TT + 8;
        m.x = j.x - 12; m.y = j.y; m.etat = 'fige';
        L.Entites.indexer();
        L.Techniques.saisir(m, 'projection_hanche', j);
        let fin = null;
        for (let t = 0; t < 200 && !fin; t++) {
            o.frame(1);
            if (j.auSol > 0) fin = { x: j.x, y: j.y, libre: tuileLibre(L, j.x, j.y) };
        }
        return { place: place, fin: fin, mur: (place.tx + 2) * TT };
    }""" % PREPARER)
    assert r["place"], "aucun mur près du terminus"
    assert r["fin"], "le joueur n'a pas été projeté"
    assert r["fin"]["libre"] and r["fin"]["x"] < r["mur"], r


def test_esquive_degage_la_prise(banc):
    """Saisi, le joueur roule (ESQUIVE) : le Mante lâche, et personne ne vole."""
    r = banc("""function (L, o) {
        %s
        const m = preparer(L, o, 'mante', 12), j = L.B.joueur;
        m.etat = 'fige';
        L.Techniques.saisir(m, 'grand_fauchage', j);
        o.frame(4);
        const tenu = j.saisiPar === m;
        o.touche('ShiftLeft'); o.frame(1); o.relacher('ShiftLeft');
        const roule = j.roule > 0, libre = !j.saisiPar, lache = m.techCible !== j;
        let vol = false;
        for (let t = 0; t < 40; t++) { o.frame(1); if (j.vol) vol = true; }
        return { tenu: tenu, roule: roule, libre: libre, lache: lache, vol: vol };
    }""" % PREPARER)
    assert r == {"tenu": True, "roule": True, "libre": True, "lache": True, "vol": False}, r


def test_saisi_sans_esquive_frappe_ne_fait_rien(banc):
    """Le témoin du juge d'avant : saisi, FRAPPE ne dégage pas — et la projection part."""
    r = banc("""function (L, o) {
        %s
        const m = preparer(L, o, 'mante', 12), j = L.B.joueur;
        m.etat = 'fige';
        L.Techniques.saisir(m, 'grand_fauchage', j);
        let vol = false, coup = false;
        for (let t = 0; t < 60; t++) {
            if (t %% 6 === 0) o.touche('KeyJ'); if (t %% 6 === 2) o.relacher('KeyJ');
            o.frame(1);
            if (j.vol) vol = true;
            if (j.etat === 'attaque') coup = true;
        }
        return { vol: vol, coup: coup };
    }""" % PREPARER)
    assert r == {"vol": True, "coup": False}, r


def test_le_retournement_du_poignet_renverse_la_prise(banc):
    """La parade-contre prend tout son sens contre eux : saisi, le joueur qui connaît le retournement du
    poignet appuie sur SAISIR — c'est le Mante qui vole."""
    r = banc("""function (L, o) {
        %s
        const m = preparer(L, o, 'mante', 12), j = L.B.joueur;
        L.B.partie.techniques = { retournement_poignet: true };
        m.etat = 'fige';
        o.viser(m);
        L.Techniques.saisir(m, 'projection_hanche', j);
        o.frame(3);
        o.touche('KeyU'); o.frame(1); o.relacher('KeyU');
        let volM = false, volJ = false;
        for (let t = 0; t < 60; t++) { o.frame(1); if (m.vol) volM = true; if (j.vol) volJ = true; }
        return { volM: volM, volJ: volJ, saisi: !!j.saisiPar, m: m.etat };
    }""" % PREPARER)
    assert r["volM"] and not r["volJ"] and not r["saisi"], r
    assert r["m"] == "assomme", r


#: Le duel joué au bouton : face à lui, FRAPPE toutes les 14 images (la chaîne de rue — on n'a rien appris).
DUEL = """function (L, o) {
    %s
    const m = preparer(L, o, '%s'), j = L.B.joueur;
    // ⚠️ Il TIENT jusqu'au bout, comme un homme de mission (`cible`) : depuis la vague 3 des bagarres de gangs
    // (`rixe.js`), un blesse fuit — et le duel mesure qui tombe le dernier, pas qui detale. (`cible` l'empeche aussi
    // de degainer l'arme de son gang : le duel reste au corps a corps.)
    m.cible = true;
    let ko = null, hopital = null, paradees = 0, vols = 0, enVol = false, avant = null;
    const des = { techniques: 0 };
    const rng = L.B.rng;
    // ⚠️ L'APPELANT IMMEDIAT, pas toute la pile : un coup qui porte passe par `Entites.blesser`, qui tire
    // la reaction du blesse — ce de-la est celui de tous les coups de la ville, pas un choix du Mante.
    L.B.rng = function () {
        const pile = (new Error().stack || '').split(String.fromCharCode(10));
        if ((pile[2] || '').indexOf('techniques.js') >= 0) des.techniques++;
        return rng.apply(this, arguments);
    };
    for (let t = 0; t < 2400; t++) {
        if (!j.vol && !(j.auSol > 0)) o.viser(m);
        if (t %% 14 === 0) o.touche('KeyJ'); if (t %% 14 === 2) o.relacher('KeyJ');
        o.frame(1);
        if (m.technique === 'retournement_poignet' && avant !== 'retournement_poignet') paradees++;
        avant = m.technique;
        if (j.vol && !enVol) vols++;
        enVol = !!j.vol;
        if (L.B.interieur) { hopital = t; break; }
        if (!m.vivant || m.etat === 'assomme') { ko = t; break; }
    }
    return { ko: ko, hopital: hopital, perdu: 100 - j.vie, paradees: paradees, vols: vols, des: des.techniques };
}"""


@pytest.fixture(scope="module")
def duels(banc):
    return {arch: banc(DUEL % (PREPARER, arch))
            for arch in ("mante", "cravate", "morue", "chevreuil", "boulonneux", "skateux")}


def test_un_mante_tient_plus_longtemps_que_tout_autre_gang_et_fait_mal(duels):
    """« Plus durs qu'un gang ordinaire » : au même duel, joué au bouton, un Mante tombe le DERNIER — et il
    a fait mal, là où les autres, pris dans la chaîne de coups, n'arrivent même pas à frapper."""
    mante = duels["mante"]
    assert mante["ko"] is not None, f"le joueur n'a jamais couché le Mante : {mante}"
    for arch, d in duels.items():
        if arch == "mante":
            continue
        assert d["ko"] is not None and d["ko"] < mante["ko"], (arch, d, mante)
        assert d["perdu"] < mante["perdu"], (arch, d, mante)
    assert mante["perdu"] > 0, mante


def test_un_mante_pare_ton_coup_et_les_autres_jamais(duels):
    """La parade du Mante : le joueur qui cogne à la chaîne se fait retourner le poignet — et projeter."""
    assert duels["mante"]["paradees"] >= 1 and duels["mante"]["vols"] >= 1, duels["mante"]
    for arch, d in duels.items():
        if arch != "mante":
            assert d["paradees"] == 0 and d["vols"] == 0, (arch, d)


def test_les_mantes_ne_tirent_aucun_de(duels):
    """Leurs choix — le pied, la prise, la parade — se tirent à l'EMPREINTE : `techniques.js` n'appelle
    jamais `B.rng()`, sinon tout le hasard de la ville glisserait derrière eux."""
    assert duels["mante"]["des"] == 0, duels["mante"]


#: La rixe à la frontière des Mantes et des Cravates : la couture, entre le Petit-Canton et le Faubourg.
RIXE = """function (L, o) {
    L.Jeu.commencer();
    L.B.defs.conduite.trafic.vehicules_max = 0;
    const f = L.B.defs.pietons.bagarre, TT = L.TT, j = L.B.joueur;
    const ligne = L.B.defs.pietons.frontieres.find(function (q) { return q.a === 'mantes' || q.b === 'mantes'; });
    if (!ligne) return { ligne: null };
    const d = (f.trop_pres_px + f.rayon_px) / 2;
    let nes = 0;
    for (let k = 3; k < ligne.long - 3 && nes < f.membres * 2; k += 2) {
        for (const sens of [-1, 1]) {
            j.x = (ligne.x + k) * TT + 8; j.y = ligne.y * TT + 8 + sens * d;
            L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
            nes = L.Entites.allumerLaBagarre(f);
            if (nes >= f.membres * 2) break;
            for (let i = L.B.entites.length - 1; i >= 0; i--) if (L.B.entites[i].bagarre) L.Entites.retirer(L.B.entites[i]);
            nes = 0;
        }
    }
    const gens = L.B.entites.filter(function (e) { return e.bagarre; });
    const kos = {}, techs = {}, etat = new Map();
    for (let t = 0; t < 1500; t++) {
        o.frame(1);
        for (const e of gens) {
            if (e.technique) techs[e.technique] = true;
            const now = e.vivant ? e.etat : 'mort';
            if ((now === 'assomme' || now === 'mort') && etat.get(e) !== now) kos[e.gang] = (kos[e.gang] || 0) + 1;
            etat.set(e, now);
        }
    }
    return { ligne: ligne, nes: nes, kos: kos, techs: Object.keys(techs).sort(),
             tenus: L.B.entites.filter(function (e) { return e.tenu; }).length };
}"""


def test_a_leur_frontiere_les_mantes_couchent_les_cravates(banc):
    """Ils se battent autrement dans une rixe aussi : ils viennent au contact, projettent, retournent le
    poignet de celui qui arme sa batte — et les trois Cravates finissent au sol. Personne ne reste tenu."""
    r = banc(RIXE)
    assert r["ligne"] and {r["ligne"]["a"], r["ligne"]["b"]} == {"mantes", "cravates"}, r
    assert r["nes"] == 6, r
    assert r["kos"].get("cravates", 0) == 3 and r["kos"].get("mantes", 0) < 3, r
    assert {"retournement_poignet"} & set(r["techs"]) or {"projection_hanche", "grand_fauchage"} & set(r["techs"]), r
    assert r["tenus"] == 0, r


def test_chez_eux_ce_sont_des_mantes_qui_trainent_dehors(banc):
    """Leur territoire, autour de l'école : sur leur zone, la moitié de ceux qui naissent sont des Mantes —
    vêtus de la veste de kung-fu, et armés du répertoire."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.defs.conduite.trafic.vehicules_max = 0;
        const z = L.Monde.carte.def.zones.find(function (q) { return q.gang === 'mantes'; });
        const j = L.B.joueur, TT = L.TT;
        // Un trottoir au milieu de leur territoire.
        let place = null;
        const cx = z.x + Math.floor(z.l / 2), cy = z.y + Math.floor(z.h / 2);
        for (let r = 0; r < 20 && !place; r++) for (let dy = -r; dy <= r && !place; dy++) for (let dx = -r; dx <= r && !place; dx++) {
            if (L.Monde.marchablePieton(cx + dx, cy + dy)) place = { x: (cx + dx) * TT + 8, y: (cy + dy) * TT + 8 };
        }
        j.x = place.x; j.y = place.y;
        L.Monde.centrerCamera(j.x, j.y);
        for (let i = L.B.entites.length - 1; i >= 0; i--) if (L.B.entites[i].type === 'pieton') L.Entites.retirer(L.B.entites[i]);
        L.Entites.indexer();
        o.frame(900);
        const mantes = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.gang === 'mantes'; });
        return { zone: L.Monde.zoneA(j.x, j.y).slug, n: mantes.length,
                 hauts: mantes.map(function (e) { return e.tenue && e.tenue.haut; }).filter(function (h, i, a) { return a.indexOf(h) === i; }),
                 savent: mantes.every(function (e) { return e.techniques && e.techniques.indexOf('projection_hanche') >= 0; }),
                 armes: mantes.filter(function (e) { return e.arme; }).length };
    }""")
    assert r["zone"] == "mantes", r
    assert r["n"] >= 3, r
    assert r["hauts"] == ["veste_kungfu"] and r["savent"] and r["armes"] == 0, r


def test_a_l_ecole_les_eleves_sont_des_mantes(banc):
    """L'ÉCOLE LA MANTE : on y entre, ses élèves s'entraînent — des Mantes, qui ne sautent pas sur qui entre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const porte = L.Monde.carte.def.portes.find(function (p) { return p.interieur === 'ecole_mante'; });
        const j = L.B.joueur, TT = L.TT;
        j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        o.entrer(porte);
        const gens = L.B.entites.filter(function (e) { return e.type === 'pieton'; });
        o.frame(120);
        return { piece: L.B.interieur && L.B.interieur.slug, n: gens.length,
                 mantes: gens.filter(function (e) { return e.arch === 'mante' && e.techniques; }).length,
                 hostiles: gens.filter(function (e) { return e.etat === 'attaque_joueur'; }).length };
    }""")
    assert r["piece"] == "ecole_mante", r
    assert r["n"] >= 2 and r["mantes"] == r["n"] and r["hostiles"] == 0, r


def test_fouiller_leurs_casiers_sous_leurs_yeux(banc):
    """Les casiers de l'école se fouillent (ACTION) — et les élèves le voient : ils te tombent dessus. Le
    témoin : entrer, rester, ne rien toucher, et personne ne bouge."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const porte = L.Monde.carte.def.portes.find(function (p) { return p.interieur === 'ecole_mante'; });
        const j = L.B.joueur, TT = L.TT;
        j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        o.entrer(porte);
        const pt = L.B.interieur.points.find(function (q) { return q.type === 'fouiller'; });
        const eleves = function () { return L.B.entites.filter(function (e) { return e.type === 'pieton' && e.gang === 'mantes'; }); };
        j.x = pt.x * TT + 8; j.y = (pt.y + 1) * TT + 8; j.angle = -Math.PI / 2; j.face = 'haut';
        L.Entites.indexer();
        o.frame(60);
        const avant = eleves().filter(function (e) { return e.etat === 'attaque_joueur'; }).length;
        const argent = L.B.partie.argent;
        o.tape('KeyE', 2);
        return { avant: avant, apres: eleves().filter(function (e) { return e.etat === 'attaque_joueur'; }).length,
                 n: eleves().length, gain: L.B.partie.argent - argent };
    }""")
    assert r["avant"] == 0 and r["gain"] > 0, r
    assert r["apres"] == r["n"] >= 2, r


def test_en_char_aucun_mante_ne_te_saisit(banc):
    """Le volant : assis dans un char, personne ne te prend par le collet — un passant ne blesse pas qui est
    dans un char, un Mante ne le projette pas non plus."""
    r = banc("""function (L, o) {
        %s
        const m = preparer(L, o, 'mante', 14), j = L.B.joueur;
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter ? L.Vehicules.monter(j, v) : null;
        if (!j.dansVehicule) { o.tape('KeyE', 2); }
        let saisi = 0, vol = 0;
        for (let t = 0; t < 400; t++) { o.frame(1); if (j.saisiPar) saisi++; if (j.vol) vol++; }
        return { dedans: !!j.dansVehicule, saisi: saisi, vol: vol };
    }""" % PREPARER)
    assert r == {"dedans": True, "saisi": 0, "vol": 0}, r


def test_en_l_air_la_camera_suit_et_action_ne_fait_rien(banc):
    """Projeté, le joueur passe par `vol` : la caméra le suit d'un bout à l'autre, et ACTION près d'un char
    ne le fait pas monter en plein vol."""
    r = banc("""function (L, o) {
        %s
        const m = preparer(L, o, 'mante', 12), j = L.B.joueur;
        m.etat = 'fige';
        o.char('auto', -40, 0, 0);
        L.Techniques.saisir(m, 'projection_hanche', j);
        // La camera garde le joueur au meme endroit de l'ecran d'un bout a l'autre du vol.
        let ecartMax = 0, monte = false, vu = 0, depart = null;
        for (let t = 0; t < 120; t++) {
            if (j.vol) { vu++; if (vu === 6) o.touche('KeyE'); if (vu === 8) o.relacher('KeyE'); }
            o.frame(1);
            if (j.vol) {
                const ex = j.x - L.B.cam.x, ey = j.y - L.B.cam.y;
                if (!depart) depart = { x: ex, y: ey };
                ecartMax = Math.max(ecartMax, Math.hypot(ex - depart.x, ey - depart.y));
            }
            if (j.dansVehicule) monte = true;
        }
        return { vu: vu, ecartMax: Math.round(ecartMax), monte: monte };
    }""" % PREPARER)
    assert r["vu"] > 10 and not r["monte"], r
    assert r["ecartMax"] <= 8, r
