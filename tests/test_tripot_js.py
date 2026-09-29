"""Le tripot du sous-sol du Dragon d'or, JOUÉ au banc (docs/jalons/le-casino-du-petit-canton.md, vague 4).

La porte du sous-sol, gardée tant que c01 n'est pas faite ; l'escalier qu'on descend à ACTION ; la barbotte du
Pouce au bouton ; ses dés pipés qu'on VOIT (plus jaunes), qu'on dénonce ou qu'on retourne contre lui ; sa méfiance,
les gros bras qui te sortent, l'escalier fermé une semaine — sans une étoile. Le navigateur joue les mêmes règles que
Python (`tripot.py`), et rien de tout ça ne tire un dé du jeu."""

import json
import random

from app import tripot

OUTILS = """
  function dansLeCasino(L, o) {
    const B = L.B, j = B.joueur, M = L.Monde;
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === 'nord_casino' && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    return B.interieur ? B.interieur.slug : null;
  }
  function poser(L, o, tx, ty, face) {
    const j = L.B.joueur, a = { haut: -Math.PI / 2, bas: Math.PI / 2, gauche: Math.PI, droite: 0 }[face];
    j.x = tx * 16 + 8; j.y = ty * 16 + 8; j.angle = a; j.face = face; L.Entites.indexer();
    o.frame(1); j.angle = a; j.face = face; L.Missions.majInvite(j);
  }
  // Descendre AU BOUTON : devant la marche, dans l'alcôve derrière la porte, et ACTION.
  function descendre(L, o) {
    const B = L.B, esc = B.interieur.points.find(function (p) { return p.type === 'escalier'; });
    poser(L, o, esc.x, esc.y - 1, 'bas');
    const invite = B.invite;
    o.tape('KeyE', 2); o.fondu();
    for (let k = 0; k < 200 && B.interieur && B.interieur.slug !== 'nord_tripot'; k++) o.frame(1);
    return invite;
  }
  // La barbotte AU BOUTON : sous la table, face à elle, ACTION ouvre son menu.
  function aLaTable(L, o) {
    const B = L.B, pt = B.interieur.points.find(function (p) { return p.type === 'barbotte'; });
    poser(L, o, pt.x, pt.y + 1, 'haut');
    const invite = B.invite;
    o.tape('KeyE', 2);
    return invite;
  }
  // Une ligne du menu, au bouton : le curseur dessus, ACTION.
  function choisir(L, o, libelle) {
    const m = L.B.menu, i = m ? m.items.findIndex(function (x) { return x.libelle === libelle; }) : -1;
    if (i < 0) return false;
    m.curseur = i; o.tape('KeyE', 2);
    return true;
  }
  function auSousSol(L, o) {
    L.B.partie.missionsFaites.c01 = 1;
    dansLeCasino(L, o); descendre(L, o);
    return L.B.interieur && L.B.interieur.slug;
  }
"""


def test_le_navigateur_joue_la_barbotte_comme_python(banc):
    """Deux mille suites de tirages, lancées honnêtes et avec chaque paire de pipés : les mêmes paires, le même
    côté ; les mêmes gains ; les mêmes faces ; la même décision de piper ; la même méfiance."""
    rng = random.Random(29)
    suites = [[rng.random() for _ in range(2 * tripot.RELANCES)] for _ in range(2000)]
    poids = [None, list(tripot.PIPES["pour"]), list(tripot.PIPES["contre"])]
    us = [rng.random() for _ in range(500)]
    attendu = {
        "jets": [[list(tripot.jet(s, tuple(p) if p else None)) for p in poids] for s in suites[:700]],
        "faces": [[tripot.face(u, tuple(p) if p else None) for p in poids] for u in us],
        "gains": [tripot.gain(pa, c, m) for pa in tripot.COTES for c in ("pour", "contre", None) for m in tripot.MISES],
        "pipe": [tripot.pipe(m, u) for m in tripot.MISES for u in us[:50]],
        "mef": [tripot.mefiance_apres(m, e) for m in (0, 30, 95, 140) for e in ("retourner", "gagne", "denoncer")],
        "contre": [list(tripot.poids_contre(pa)) for pa in tripot.COTES],
    }
    r = banc("function (L, o) {" + """
        L.Jeu.commencer();
        const T = L.Tripot, P = POIDS, S = SUITES, U = US;
        return {
            jets: S.slice(0, 700).map(function (s) { return P.map(function (p) { const j = T.jet(s, p); return [j.cote, j.paires]; }); }),
            faces: U.map(function (u) { return P.map(function (p) { return T.face(u, p); }); }),
            gains: [].concat.apply([], ['pour', 'contre'].map(function (pa) { return [].concat.apply([], ['pour', 'contre', null].map(function (c) {
                return T.regles().mises.map(function (m) { return T.gain(pa, c, m); }); })); })),
            pipe: [].concat.apply([], T.regles().mises.map(function (m) { return U.slice(0, 50).map(function (u) { return T.pipe(m, u); }); })),
            mef: [].concat.apply([], [0, 30, 95, 140].map(function (m) { return ['retourner', 'gagne', 'denoncer'].map(function (e) { return T.mefianceApres(m, e); }); })),
            contre: ['pour', 'contre'].map(function (pa) { return T.poidsContre(pa); }),
        };
    }""".replace("POIDS", json.dumps(poids)).replace("SUITES", json.dumps(suites)).replace("US", json.dumps(us)))
    assert r["jets"] == json.loads(json.dumps(attendu["jets"]))
    assert r["faces"] == attendu["faces"]
    assert r["gains"] == attendu["gains"] and r["pipe"] == attendu["pipe"]
    assert r["mef"] == attendu["mef"] and r["contre"] == attendu["contre"]


def test_la_porte_du_sous_sol_attend_c01_puis_on_descend_au_bouton(banc):
    """Avant c01, la porte (une barrière de la pièce) arrête le joueur, dit sa raison, et le gros bras le dit
    aussi ; après, elle est ouverte : on marche jusqu'à la marche, ACTION, et on est au tripot — le Pouce, ses gros
    bras, et la barbotte ouvre son menu au bouton. On remonte par le même escalier."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, M = L.Monde;
        dansLeCasino(L, o);
        const pb = L.Tripot.porte();
        // Fermée : on s'y bute en venant de la salle.
        poser(L, o, pb.x, pb.y - 1, 'bas');
        B.buteMsgT = -999;
        const bloque = M.barriereBloque(j, pb.x, pb.y);
        const msg = B.msg || null;
        for (let k = 0; k < 4; k++) o.frame(1);
        const gb = B.entites.find(function (e) { return e.grosBras; });
        const bulle = gb && gb.bulle ? gb.bulle.texte || gb.bulle : null;
        // Marcher dessus au clavier : on ne passe pas.
        poser(L, o, pb.x, pb.y - 1, 'bas');
        o.touche('KeyS'); for (let k = 0; k < 40; k++) o.frame(1); o.relacher('KeyS');
        const passeFermee = Math.floor(j.y / 16) >= pb.y;
        // Ouverte : c01 faite.
        B.partie.missionsFaites.c01 = 1;
        poser(L, o, pb.x, pb.y - 1, 'bas');
        o.touche('KeyS'); for (let k = 0; k < 40; k++) o.frame(1); o.relacher('KeyS');
        const passeOuverte = Math.floor(j.y / 16) >= pb.y;
        const invite = descendre(L, o);
        const ici = B.interieur && B.interieur.slug;
        const pouce = B.entites.filter(function (e) { return e.pouce; }).length;
        const gros = B.entites.filter(function (e) { return e.grosBras; }).length;
        B.partie.argent = 1000;
        const inviteTable = aLaTable(L, o);
        const menu = B.menu ? { titre: B.menu.titre, aide: B.menu.aide, lignes: B.menu.items.map(function (x) { return x.libelle; }) } : null;
        L.Hud.fermerMenu();
        // Remonter.
        const esc = B.interieur.points.find(function (p) { return p.type === 'escalier'; });
        poser(L, o, esc.x + 1, esc.y, 'gauche');
        o.tape('KeyE', 2); o.fondu();
        for (let k = 0; k < 200 && B.interieur.slug !== 'nord_casino'; k++) o.frame(1);
        return { bloque: bloque, msg: msg, bulle: bulle, passeFermee: passeFermee, passeOuverte: passeOuverte, invite: invite,
                 ici: ici, pouce: pouce, gros: gros, inviteTable: inviteTable, menu: menu, remonte: B.interieur.slug,
                 etoiles: B.recherche.etoiles };
    }""")
    assert r["bloque"] is True and r["msg"] == tripot.PORTE["raison"], r
    assert r["passeFermee"] is False, "la porte fermée laisse passer au clavier"
    assert r["passeOuverte"] is True, "la porte ouverte ne laisse pas passer"
    assert r["invite"] == "MONTER" and r["ici"] == "nord_tripot", r
    assert r["pouce"] == 1 and r["gros"] == 2, r
    assert r["inviteTable"] == "LA BARBOTTE" and r["menu"]["titre"] == "LA BARBOTTE DU POUCE", r
    assert r["menu"]["lignes"] == ["PARI", "MISE", "MISER"] and "RETOUR 97 %" in r["menu"]["aide"], r
    assert r["remonte"] == "nord_casino" and r["etoiles"] == 0, r


def test_un_coup_au_bouton_miser_lancer_et_le_gain_paye(banc):
    """PARI, MISE (100 à 1 000 $), MISER : la main du Pouce pose les dés ; LANCER : les dés roulent, relances
    comprises, et le coup est réglé — payé tout de suite, annoncé à l'arrêt. Vingt coups par jour."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tripot;
        auSousSol(L, o);
        B.partie.argent = 100000;
        aLaTable(L, o);
        const e = T.etat();
        const mises = [];
        for (let k = 0; k < 4; k++) { mises.push(e.mise); B.menu.curseur = 1; o.tape('ArrowRight', 2); }
        e.mise = 100;
        const avant = B.partie.argent;
        choisir(L, o, 'MISER');
        const t = T.enCours();
        const joue = { phase: t.phase, lignes: B.menu.items.map(function (x) { return x.libelle; }), curseur: B.menu.curseur };
        choisir(L, o, 'LANCER');
        const fin = { phase: t.phase, gain: t.resultat.gain, argent: B.partie.argent, paires: t.paires.length };
        for (let k = 0; k < 20; k++) { choisir(L, o, 'MISER'); choisir(L, o, 'LANCER'); }
        const ligne = B.menu.items.find(function (x) { return x.libelle === 'MISER'; });
        const refus = T.miser();
        return { mises: mises, avant: avant, joue: joue, fin: fin, coups: e.coups, actif: ligne.actif, refus: refus, msg: B.msg || null };
    }""")
    assert r["mises"] == list(tripot.MISES), r
    assert r["joue"]["phase"] == "joue" and r["joue"]["lignes"] == ["LANCER", "CHANGER DE CÔTÉ", "DÉNONCER LES DÉS"], r
    assert r["joue"]["curseur"] == 0, "le curseur va sur LANCER"
    assert r["fin"]["phase"] == "fin" and r["fin"]["paires"] >= 1
    assert r["fin"]["argent"] == r["avant"] - 100 + r["fin"]["gain"] and r["fin"]["gain"] in (0, 100, 195), r
    assert r["coups"] == tripot.COUPS_PAR_JOUR and r["actif"] is False, r
    assert r["refus"] is False and "FERME SA TABLE" in (r["msg"] or ""), r


def test_les_pipes_se_voient_plus_jaunes_et_seulement_quand_la_mise_grossit(banc):
    """LA MAISON TRICHE, ET ÇA SE VOIT : sous 500 $, jamais de pipés ; à 1 000 $, souvent. Et le feutre du menu
    peint les dés dans l'IVOIRE JAUNE quand ce sont les pipés, BLANCS sinon — c'est ce qu'Irène t'apprend à voir.
    (La mutation qui peint les pipés en blanc fait rougir ce juge.)"""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tripot;
        auSousSol(L, o);
        B.partie.argent = 1e7;
        aLaTable(L, o);
        const e = T.etat();
        const couleurs = function () {
            const vus = new Set(), ctx = o.ctx, vrai = ctx.fillRect;
            // Le corps des dés : les carrés de 20 × 20 (le texte du feutre a aussi du blanc).
            ctx.fillRect = function (x, y, w, h) { if (w === 20 && h === 20) vus.add(ctx.fillStyle); return vrai.apply(ctx, arguments); };
            try { B.menu.dessiner(ctx, 20, 20); } finally { ctx.fillRect = vrai; }
            return vus;
        };
        const compte = { 100: 0, 200: 0, 500: 0, 1000: 0 }, vus = { pipe: 0, vrai: 0, faux: 0 };
        for (let k = 0; k < 160; k++) {
            e.mise = [100, 200, 500, 1000][k % 4]; e.coups = 0; e.mefiance = 0; e.tranquille = -1;
            choisir(L, o, 'MISER');
            const t = T.enCours(), c = couleurs();
            if (t.pipes) compte[e.mise]++;
            if (t.pipes) { if (c.has(T.IVOIRE.pipe) && !c.has(T.IVOIRE.vrai)) vus.pipe++; else vus.faux++; }
            else { if (c.has(T.IVOIRE.vrai) && !c.has(T.IVOIRE.pipe)) vus.vrai++; else vus.faux++; }
            choisir(L, o, 'LANCER');
        }
        return { compte: compte, vus: vus };
    }""")
    c = r["compte"]
    assert c["100"] == 0 and c["200"] == 0, c
    assert 10 <= c["500"] <= 34 and 10 <= c["1000"] <= 34, f"une fois sur {tripot.PIPES['chance']} environ : {c}"
    assert r["vus"]["faux"] == 0 and r["vus"]["pipe"] == c["500"] + c["1000"], r


def test_denoncer_juste_rend_la_mise_et_la_paix_du_jour_denoncer_faux_te_sort(banc):
    """Dénoncer des pipés : la mise rendue, la méfiance qui monte, et plus un pipé de la journée ; le lendemain, il
    recommence. Dénoncer des dés honnêtes : les gros bras te sortent (dehors, devant le Dragon d'or), la mise est
    perdue, l'escalier refusé jusqu'au lendemain — et pas une étoile."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tripot, j = B.joueur;
        auSousSol(L, o);
        B.partie.argent = 1e6;
        aLaTable(L, o);
        const e = T.etat();
        e.mise = 1000;
        let t;
        for (let k = 0; k < 40; k++) { choisir(L, o, 'MISER'); t = T.enCours(); if (t.pipes) break; choisir(L, o, 'LANCER'); }
        const avant = B.partie.argent;
        choisir(L, o, 'DÉNONCER LES DÉS');
        const juste = { argent: B.partie.argent - avant, mef: e.mefiance, phase: t.phase, nom: t.resultat.nom,
                        ici: B.interieur && B.interieur.slug };
        let pipesApres = 0;
        for (let k = 0; k < 15; k++) { choisir(L, o, 'MISER'); if (T.enCours().pipes) pipesApres++; choisir(L, o, 'LANCER'); }
        // Le lendemain : il recommence.
        B.partie.jour++; e.coups = 0;
        let pipesDemain = 0;
        for (let k = 0; k < 15; k++) { choisir(L, o, 'MISER'); if (T.enCours().pipes) pipesDemain++; choisir(L, o, 'LANCER'); }
        // Faux : des dés honnêtes.
        e.mise = 100;
        const argentFaux = B.partie.argent;
        choisir(L, o, 'MISER');
        const honnete = !T.enCours().pipes;
        choisir(L, o, 'DÉNONCER LES DÉS');
        o.fondu(); for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
        const faux = { argent: B.partie.argent - argentFaux, dehors: !B.interieur, barre: T.barre(), etoiles: B.recherche.etoiles };
        // L'escalier, refusé jusqu'au lendemain.
        dansLeCasino(L, o);
        const esc = B.interieur.points.find(function (p) { return p.type === 'escalier'; });
        poser(L, o, esc.x, esc.y - 1, 'bas');
        o.tape('KeyE', 2); o.fondu(); for (let k = 0; k < 60; k++) o.frame(1);
        const refuse = { ici: B.interieur.slug, msg: B.msg || null };
        B.partie.jour++;
        descendre(L, o);
        return { juste: juste, pipesApres: pipesApres, pipesDemain: pipesDemain, honnete: honnete, faux: faux,
                 refuse: refuse, lendemain: B.interieur.slug };
    }""")
    j = r["juste"]
    assert j["argent"] == 1000 and j["mef"] == tripot.MEFIANCE["denoncer"] and "PIPÉS" in j["nom"], j
    assert j["ici"] == "nord_tripot", "dénoncer juste ne te sort pas"
    assert r["pipesApres"] == 0 and r["pipesDemain"] > 0, r
    assert r["honnete"] and r["faux"]["argent"] == -100 and r["faux"]["dehors"] and r["faux"]["barre"], r
    assert r["faux"]["etoiles"] == 0, "dans un tripot, on n'appelle pas la police"
    assert r["refuse"]["ici"] == "nord_casino" and "NE VEUT PLUS TE VOIR" in (r["refuse"]["msg"] or ""), r
    assert r["lendemain"] == "nord_tripot", r


def test_changer_de_cote_retourne_les_pipes_contre_le_pouce_jusqu_a_ce_qu_il_te_sorte(banc):
    """Changer de côté une fois ses pipés posés : ils jouent pour toi — sur deux mille coups (le hasard du navigateur,
    la méfiance remise à zéro), la table rend plus qu'on y met, et près de 135 %. Mais le Pouce le voit : la méfiance
    monte à chaque fois, et à cent, à la mise suivante, les gros bras te raccompagnent — l'escalier fermé une semaine,
    pas une étoile. (Changer de côté sur des dés honnêtes ne se remarque pas.)"""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tripot;
        auSousSol(L, o);
        B.partie.argent = 1e9;
        const e = T.etat();
        e.mise = 1000;
        let mise = 0, rendu = 0, n = 0, honnetesRemarques = 0, vusAutrement = 0;
        for (let k = 0; k < 6000 && n < 2000; k++) {
            e.coups = 0; e.mefiance = 0;
            T.miser();
            const t = T.enCours();
            T.changer();
            if (!t.pipes) { if (e.mefiance > 0) honnetesRemarques++; T.lancer(); continue; }
            if (e.mefiance !== T.regles().mefiance.retourner) vusAutrement++;
            n++; mise += t.mise;
            T.lancer(); rendu += t.resultat.gain;
        }
        // La méfiance, pour vrai : jusqu'à la sortie.
        e.mefiance = 0; e.coups = 0;
        const suite = [];
        aLaTable(L, o);
        for (let k = 0; k < 200 && B.interieur && B.interieur.slug === 'nord_tripot'; k++) {
            if (!B.menu) aLaTable(L, o);
            if (!choisir(L, o, 'MISER')) break;
            if (!T.enCours() || T.enCours().phase !== 'joue') break;
            if (T.enCours().pipes) choisir(L, o, 'CHANGER DE CÔTÉ');
            choisir(L, o, 'LANCER');
            suite.push(e.mefiance);
        }
        o.fondu(); for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
        return { retour: rendu / mise, n: n, honnetesRemarques: honnetesRemarques, vusAutrement: vusAutrement, suite: suite, dehors: !B.interieur,
                 barreJours: e.barre - B.partie.jour, etoiles: B.recherche.etoiles, msg: B.msg || null };
    }""")
    assert r["n"] == 2000 and 1.25 < r["retour"] < 1.45, r
    assert r["honnetesRemarques"] == 0 and r["vusAutrement"] == 0, "le Pouce voit qu'on change de côté sur SES dés"
    assert r["suite"][-1] >= tripot.MEFIANCE["sortir"] and r["dehors"], r
    assert r["barreJours"] == tripot.MEFIANCE["barre_jours"] and r["etoiles"] == 0, r
    assert "UNE SEMAINE" in (r["msg"] or ""), r


def test_des_milliers_de_coups_au_hasard_du_navigateur(banc):
    """Vingt mille coups joués par le navigateur, sous le seuil : la barbotte honnête rend ses 97,5 % ; au-dessus,
    le naïf qui lance quoi qu'il voie en perd le quart (autour de 75 %)."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tripot;
        auSousSol(L, o);
        B.partie.argent = 1e12;
        const e = T.etat(), mesure = {};
        [200, 1000].forEach(function (m) {
            let mise = 0, rendu = 0;
            e.mise = m;
            for (let k = 0; k < 20000; k++) { e.coups = 0; e.mefiance = 0; T.miser(); T.lancer(); mise += m; rendu += T.enCours().resultat.gain; }
            mesure[m] = rendu / mise;
        });
        return mesure;
    }""")
    assert 0.96 < r["200"] < 0.99, r
    assert 0.72 < r["1000"] < 0.78, r


def test_jouer_au_tripot_ne_touche_pas_au_hasard_du_jeu(banc):
    """Trente coups — miser, changer, dénoncer, lancer — et le tirage suivant du jeu est le même que sans eux."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tripot;
        auSousSol(L, o);
        B.partie.argent = 1e6;
        const e = T.etat();
        L.graine(77);
        const temoin = [B.rng(), B.rng(), B.rng()];
        L.graine(77);
        for (let k = 0; k < 30; k++) {
            e.coups = 0; e.mefiance = 0; e.mise = k % 2 ? 1000 : 200;
            T.miser();
            if (k % 3 === 0) T.changer();
            if (k % 5 === 0) T.denoncer(); else T.lancer();
            if (!B.interieur) break;
        }
        const apres = [B.rng(), B.rng(), B.rng()];
        return { temoin: temoin, apres: apres };
    }""")
    assert r["apres"] == r["temoin"]


def test_frapper_les_gens_du_pouce_ferme_l_escalier_une_semaine_sans_police(banc):
    """Le Pouce et ses gros bras ne se frappent pas : l'escalier te reste fermé une semaine. Pas d'étoile — un tripot
    n'appelle pas la police."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tripot, j = B.joueur;
        auSousSol(L, o);
        const gb = B.entites.find(function (e) { return e.grosBras; });
        gb.vie = gb.vieMax - 10; gb.menace = j;
        for (let k = 0; k < 3; k++) o.frame(1);
        o.fondu(); for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
        return { barre: T.etat().barre - B.partie.jour, dehors: !B.interieur, etoiles: B.recherche.etoiles };
    }""")
    assert r == {"barre": tripot.MEFIANCE["barre_jours"], "dehors": True, "etoiles": 0}, r


def test_la_salle_enfumee_s_entend_et_se_voit(banc):
    """La rumeur du tripot joue au sous-sol, et se tait en remontant ; la fumée se peint par-dessus les gens au
    sous-sol (des nappes grises translucides, le noir des coins), jamais dans la grande salle."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tripot;
        const volumes = [];
        const vrai = L.Son.SFX.tripot_salle;
        L.Son.SFX.tripot_salle = function (v) { volumes.push(v); return vrai.apply(null, arguments); };
        const peint = function () {
            const ctx = o.ctx, styles = [], f = ctx.fillRect;
            ctx.fillRect = function () { styles.push(String(ctx.fillStyle)); return f.apply(ctx, arguments); };
            try { T.dessinerFumee(ctx, B.cam); } finally { ctx.fillRect = f; }
            return styles.filter(function (s) { return s.indexOf('rgba(190,184,176') === 0; }).length;
        };
        dansLeCasino(L, o);
        const enHaut = peint(); volumes.length = 0; o.frame(2);
        const volHaut = volumes.slice();
        B.partie.missionsFaites.c01 = 1;
        descendre(L, o);
        volumes.length = 0; o.frame(2);
        return { enHaut: enHaut, enBas: peint(), volHaut: volHaut, volBas: volumes.slice() };
    }""")
    assert r["enHaut"] == 0 and r["enBas"] >= 9, r
    assert set(r["volHaut"]) == {0} and set(r["volBas"]) == {1}, r


def test_c01_jouee_au_bouton_d_irene_a_la_porte_ouverte(banc):
    """c01, _La barbotte du Pouce_, jouée de l'appel à la porte : après m6, Irène appelle ; elle se tient au bout du
    bar du Dragon d'or (on lui serre la main au bouton, elle dit l'intro) ; en sortant, deux rabatteurs attendent à
    la porte du terminus ; couchés, la ligne dit de rapporter le jeton au Dragon d'or ; arrivé devant, la mission
    se ferme (400 $), et la porte du sous-sol est ouverte : on descend au bouton."""
    from outils_missions import OUTILS as OUTILS_MISSIONS, PLUS_LONGUES
    r = banc("function (L, o) {" + OUTILS + OUTILS_MISSIONS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('irene');
        // Dedans : Irène au bout du bar. Sa bulle, puis ACTION : l'intro.
        dansLeCasino(L, o); jouer(L, o);
        const irene = L.Histoire.donneur('irene');
        const bar = irene ? { x: Math.floor(irene.x / 16), y: Math.floor(irene.y / 16) } : null;
        serrer(L, o, 'irene');
        let intro = 0;
        for (let k = 0; k < 6000 && (B.scene || B.cinema); k++) { if (B.scene) intro++; o.frame(1); ecouter(L); }
        jouer(L, o);
        const debut = { mission: B.partie.mission && B.partie.mission.slug, etape: etape(L) };
        L.Jeu.sortir(); o.fondu(); for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
        jouer(L, o, 20);
        const t = L.Histoire.lieu('terminus');
        const gars = B.mission.entites.filter(function (e) { return e.cible && e.etape === 0; });
        const bagarre = { n: gars.length, loin: Math.max.apply(null, gars.map(function (e) { return Math.round(Math.hypot(e.x - t.x, e.y - t.y) / 16); })) };
        const porteFermee = { etape: etape(L) };
        // Au terminus (le GPS y mène) : on les couche là, loin du Dragon d'or.
        j.x = t.x + 40; j.y = t.y + 8; L.Entites.indexer(); jouer(L, o, 5);
        gars.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        const c = L.Histoire.lieu('nord_casino');
        j.x = c.x; j.y = c.y + 8; L.Entites.indexer(); jouer(L, o, 30);
        let fin = 0;
        for (let k = 0; k < 6000 && (B.partie.mission || B.scene || B.cinema); k++) { if (B.scene) fin++; o.frame(1); ecouter(L); }
        const fait = !!B.partie.missionsFaites.c01;
        const ici = auSousSol(L, o);
        return { dispo: dispo && dispo.slug, bar: bar, debut: debut, intro: intro, fin: fin, bagarre: bagarre, retour: retour,
                 fait: fait, argent: argent.map(function (a) { return a.montant; }), dites: dites, ici: ici };
    }""")
    assert r["dispo"] == "c01", "Irène donne c01 après m6"
    # Son point est au bout du bar (31, 1) ; elle se tient debout à la tuile libre voisine la plus proche du milieu
    # de la salle (`placeDebout`) — au coin du comptoir.
    assert abs(r["bar"]["x"] - 31) <= 1 and abs(r["bar"]["y"] - 1) <= 1, f"Irène se tient au bout du bar : {r['bar']}"
    assert r["debut"] == {"mission": "c01", "etape": 0}, r
    assert r["intro"] > 60 and r["fin"] > 60, "l'intro et la fin se jouent (leurs scènes)"
    assert r["bagarre"]["n"] == 2 and r["bagarre"]["loin"] <= 8, r["bagarre"]
    assert r["retour"]["etape"] == 1 and r["retour"]["ligne"].startswith("RAPPORTE UN JETON"), r["retour"]
    for dite in ("pendant:irene:0", "pendant:irene:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [400], r
    assert r["ici"] == "nord_tripot", "la porte du sous-sol reste fermée après c01"
