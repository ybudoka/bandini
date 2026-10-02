"""S'asseoir, attendre, se coucher (P4) — vague 1, au banc : dedans, on s'assoit sur une chaise, une berçante ou le
sofa de la planque ; et le lit à soi nous couche avant d'ouvrir son menu.

⚠️ **Par le bouton** (`o.tape('KeyE')`), comme `test_interactions_js.py` : la chaîne d'ACTION affame ce qui la suit,
et dans une pièce le comptoir d'à côté attrape ACTION dans 1,6 tuile — un juge qui appellerait `Repos.sAsseoir`
ne verrait pas le catalogue de la planque voler la chaise.

La planque de Rocco (`carte._piece("planque")`) : le lit de deux places en (1-2, 1-2), deux chaises en (3, 3) et
(3, 4) contre la table, le catalogue sur la table en (2, 4) ; le sofa, une fois livré, en (8, 4), face à la télé.
"""

from app import interactions

DEDANS = interactions.ASSEOIR["dedans"]
INVITE = interactions.ASSEOIR["invite"]
MATIN = "DORMIR JUSQU’AU MATIN"

OUTILS = """
    L.Jeu.commencer();
    if (L.B.menu) L.Hud.fermerMenu();
    const j = L.B.joueur, p = L.B.partie, TT = L.TT;
    function entrer() {
        const porte = L.Monde.carte.portes.find(function (q) { return q.lieu === 'planque'; });
        j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 10;
        o.entrer(porte);
        if (L.B.menu) L.Hud.fermerMenu();
    }
    // Debout au milieu de la tuile (tx, ty), le regard vers la tuile (vx, vy).
    function planter(tx, ty, vx, vy) {
        j.x = tx * TT + 8; j.y = ty * TT + 8; j.vx = 0; j.vy = 0;
        o.viser({ x: vx * TT + 8, y: vy * TT + 8 });
    }
    function invite() { L.Missions.majInvite(j); return L.B.invite; }
    function suivant() { const t = L.B.t; for (let k = 0; k < 6 && L.B.t === t; k++) o.frame(1); }
    function pousser(code, n) { o.touche(code); o.frame(n || 2); o.relacher(code); o.frame(1); }
    function libelles() { return L.B.menu ? L.B.menu.items.map(function (i) { return i.libelle; }) : null; }
    function tuile() { return { x: Math.floor(j.x / TT), y: Math.floor(j.y / TT) }; }
"""


def jouer(banc, corps):
    return banc("function (L, o) {" + OUTILS + corps + "}")


def test_on_s_assoit_sur_une_chaise_de_la_piece_et_le_stick_leve(banc):
    """Sous la chaise (3, 4), le regard au nord : l'invite dit S'ASSEOIR, et ACTION nous y pose, pieds au bord de
    l'assise, comme le patient. On y reste ; le stick nous rend où l'on se tenait."""
    r = jouer(banc, """
        entrer();
        planter(3, 5, 3, 4);
        const avant = { x: j.x, y: j.y }, inv = invite();
        o.tape('KeyE');
        const assis = !!j.assis, face = j.face, ou = { x: j.x, y: j.y };
        for (let k = 0; k < 30; k++) o.frame(1);
        const encore = !!j.assis, invAssis = invite();
        pousser('KeyS');
        return { inv: inv, assis: assis, face: face, ou: ou, encore: encore, invAssis: invAssis,
                 leve: !j.assis, ici: { x: j.x, y: j.y }, avant: avant };
    """)
    assert r["inv"] == INVITE, "devant une chaise, l'invite doit le dire (et le catalogue d'à côté ne la vole pas)"
    assert r["assis"] and r["face"] == DEDANS["h"]["pose"]
    assert r["ou"] == {"x": 3 * 16 + 8, "y": 4 * 16 + 8 + DEDANS["h"]["dy"]}, "le corps se pose SUR la chaise"
    assert r["encore"], "dans une pièce, on reste assis (le banc de la rue se levait dès qu'on était dedans)"
    assert r["invAssis"] == interactions.ATTENDRE["invite"], "assis, ACTION ouvre le menu de l'attente (vague 2)"
    assert r["leve"], "le stick lève"
    assert abs(r["ici"]["x"] - r["avant"]["x"]) < 3 and r["ici"]["y"] > r["avant"]["y"] - 1, \
        "on se relève là où l'on se tenait, et le pas qui suit est le nôtre"


def test_une_chaise_prise_ou_la_police_aux_fesses(banc):
    """Quelqu'un est assis dessus : pas d'invite, ACTION ne nous y pose pas. Avec une étoile : le refus du banc."""
    r = jouer(banc, """
        entrer();
        planter(3, 5, 3, 4);
        const q = L.Entites.creerPieton(3 * TT + 8, 4 * TT + 14, L.Entites.archetype('touriste'));
        q.etat = 'fige'; q.plante = { x: q.x, y: q.y }; L.Entites.indexer();
        const invPrise = invite();
        o.tape('KeyE');
        const prise = !!j.assis;
        L.Entites.retirer(q); L.Entites.indexer();
        if (L.B.menu) L.Hud.fermerMenu();
        planter(3, 5, 3, 4); suivant();
        L.B.recherche.etoiles = 1;
        const invPolice = invite();
        o.tape('KeyE');
        return { invPrise: invPrise, prise: prise, invPolice: invPolice, police: !!j.assis };
    """)
    assert r["invPrise"] != INVITE and not r["prise"], "une chaise occupée ne s'offre pas"
    assert r["invPolice"] == interactions.ASSEOIR["refus"]["police"] and not r["police"]


def test_le_sofa_de_la_planque_face_a_la_tele(banc):
    """Livré, le sofa à carreaux s'offre : on s'y assoit le regard au nord, vers la télé, posé sur son assise."""
    r = jouer(banc, """
        p.meubles = { planque: { sofa: { jour: p.jour - 1 } } };
        entrer();
        const sofa = L.B.entites.find(function (e) { return e.type === 'decor' && e.decor === 'sofa'; });
        planter(8, 3, 8, 4);
        const inv = invite();
        o.tape('KeyE');
        const assis = !!j.assis, face = j.face, ou = { x: j.x - sofa.x, y: j.y - sofa.y };
        for (let k = 0; k < 20; k++) o.frame(1);
        return { sofa: !!sofa, inv: inv, assis: assis, face: face, ou: ou, encore: !!j.assis };
    """)
    assert r["sofa"], "le sofa livré doit être dans la planque"
    assert r["inv"] == INVITE
    assert r["assis"] and r["face"] == DEDANS["sofa"]["pose"] and r["encore"]
    assert r["ou"] == {"x": DEDANS["sofa"]["dx"], "y": DEDANS["sofa"]["dy"]}


def test_le_lit_couche_avant_le_menu_et_on_y_reste(banc):
    """ACTION au lit : on se couche dedans (la tête sur l'oreiller, au milieu des deux places), le menu s'ouvre avec
    SE LEVER au bout. Fermé, on reste couché ; ACTION le rouvre ; SE LEVER nous met debout, sur le plancher."""
    r = jouer(banc, """
        entrer();
        const lit = L.B.interieur.points.find(function (q) { return q.type === 'lit'; });
        planter(lit.x, lit.y + 1, lit.x, lit.y);
        j.y = lit.y * TT + 8 + 12;
        o.tape('KeyE');
        const couche = !!j.alite, face = j.face, ou = { x: j.x, y: j.y }, menu = libelles();
        L.Hud.fermerMenu();
        for (let k = 0; k < 30; k++) o.frame(1);
        const encore = !!j.alite, inv = invite();
        o.tape('KeyE');
        const rouvert = libelles();
        const lever = L.B.menu.items.find(function (i) { return i.libelle === 'SE LEVER'; });
        if (lever.faire()) L.Hud.fermerMenu();
        const t = tuile();
        return { couche: couche, face: face, ou: ou, menu: menu, encore: encore, inv: inv, rouvert: rouvert,
                 debout: !j.alite, meuble: L.Monde.estMeuble(t.x, t.y), marche: L.Monde.marchablePieton(t.x, t.y) };
    """)
    assert r["couche"] and r["face"] == "alite", "ACTION au lit doit nous coucher dedans"
    assert r["ou"]["x"] == 1 * 16 + 16 - 0.5, "couché au milieu du lit de deux places"
    assert r["menu"] and r["menu"][0] == MATIN and r["menu"][-1] == "SE LEVER"
    assert r["encore"], "le menu fermé, on reste couché"
    assert r["inv"] == "DORMIR"
    assert r["rouvert"] == r["menu"], "couché, ACTION rouvre le menu du lit"
    assert r["debout"] and not r["meuble"] and r["marche"], "SE LEVER met debout, à côté du lit"


def test_on_dort_couche_et_le_stick_leve_au_reveil(banc):
    """DORMIR JUSQU'AU MATIN depuis le lit : le lendemain, on est encore couché ; le stick nous lève au pied du lit."""
    r = jouer(banc, """
        entrer();
        const lit = L.B.interieur.points.find(function (q) { return q.type === 'lit'; });
        planter(lit.x, lit.y + 1, lit.x, lit.y);
        j.y = lit.y * TT + 8 + 12;
        const jour = p.jour;
        o.tape('KeyE');
        L.B.menu.items.find(function (i) { return i.libelle === '%s'; }).faire();
        L.Hud.fermerMenu();
        o.fondu();
        const lendemain = p.jour === jour + 1, couche = !!j.alite;
        pousser('KeyS', 3);
        const t = tuile();
        return { lendemain: lendemain, couche: couche, debout: !j.alite,
                 meuble: L.Monde.estMeuble(t.x, t.y), marche: L.Monde.marchablePieton(t.x, t.y) };
    """ % MATIN)
    assert r["lendemain"], "on a dormi jusqu'au lendemain"
    assert r["couche"], "on se réveille dans son lit"
    assert r["debout"] and not r["meuble"] and r["marche"], "le stick lève, sur le plancher"


def test_au_chalet_on_se_leve_du_cote_libre_du_lit(banc):
    """Au chalet du rang, le classeur bouche le pied de la colonne de gauche du lit : on ne se levait que par là, et
    l'on restait debout SUR le lit. Le lit de deux places se quitte par n'importe quel bord libre.

    ⚠️ Le chalet doit être à soi : celui à vendre ne propose que de l'acheter, sans coucher."""
    from tests.test_chalet_js import OUTILS as CHALET
    r = banc("async function (L, o) {" + CHALET + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        if (B.partie.planques.indexOf('rang') < 0) B.partie.planques.push('rang');
        await auChalet(L, o);
        const piece = entrerDansLeChalet(L, o);
        const lit = B.interieur.points.find(function (q) { return q.type === 'lit'; });
        j.x = lit.x * TT + 8; j.y = (lit.y + 1) * TT + 8; j.vx = 0; j.vy = 0;
        o.viser({ x: lit.x * TT + 8, y: lit.y * TT + 8 });
        o.tape('KeyE');
        const couche = !!j.alite;
        fermer(L);
        o.touche('KeyS'); o.frame(3); o.relacher('KeyS'); o.frame(1);
        const tx = Math.floor(j.x / TT), ty = Math.floor(j.y / TT);
        return { piece: piece, couche: couche, debout: !j.alite, meuble: L.Monde.estMeuble(tx, ty),
                 marche: L.Monde.marchablePieton(tx, ty) };
    }""")
    assert r["piece"] == "chalet"
    assert r["couche"], "au chalet acheté, le lit couche aussi"
    assert r["debout"] and not r["meuble"] and r["marche"], "debout sur le plancher, pas sur le lit"


# --- Vague 2 : attendre, assis ---------------------------------------------------------------------------------

ATTENDRE = interactions.ATTENDRE

#: Assis sur la chaise (3, 4) de la planque, à l'heure `heure` ; ACTION ouvre le menu de l'assis.
ASSIS = """
    function asseoirALaPlanque(heure) {
        entrer();
        planter(3, 5, 3, 4);
        o.tape('KeyE');
        p.heure = heure;
    }
    function choisir(libelle) {
        o.tape('KeyE');
        const i = L.B.menu && L.B.menu.items.find(function (q) { return q.libelle === libelle; });
        if (!i) return null;
        if (i.actif !== false && i.faire()) L.Hud.fermerMenu();
        return i;
    }
"""


def test_assis_on_attend_deux_heures_en_accelere(banc):
    """ATTENDRE 2 H : l'horloge arrive à l'heure dite (pas une minute plus loin), la ville fait ses pas de plus
    (`vitesse` par image), et ça dure ce que Martin a voulu — deux secondes par heure. On reste assis."""
    r = jouer(banc, ASSIS + """
        asseoirALaPlanque(0.40);
        o.tape('KeyE');
        const menu = libelles();
        L.Hud.fermerMenu();
        const h0 = p.heure, jour = p.jour;
        const i = choisir('%s 2 H');
        const t0 = L.B.t;
        let images = 0;
        while (L.B.attente && images < 2000) { o.frame(1); images++; }
        return { menu: menu, detail: i && i.detail, avance: (p.heure - h0) * 24, jour: p.jour - jour, images: images,
                 pas: L.B.t - t0, assis: !!j.assis, msg: L.B.msg };
    """ % ATTENDRE["invite"])
    inv = ATTENDRE["invite"]
    assert r["menu"] == ["%s %d H" % (inv, h) for h in ATTENDRE["heures"]] + ["SE LEVER"]
    assert r["detail"] == "11:36", "l'heure d'arrivée se lit dans le menu (9 h 36 + 2 h)"
    assert abs(r["avance"] - 2) < 0.01, "on arrive à l'heure dite, pas plus loin"
    attendu = 2 * ATTENDRE["secondes_par_heure"] * 60
    assert attendu * 0.9 <= r["images"] <= attendu * 1.1, "deux secondes réelles par heure"
    assert r["pas"] >= r["images"] * (ATTENDRE["vitesse"] - 0.5), "la ville tourne plus vite : ses pas de plus"
    assert r["assis"], "on reste assis après l'attente"
    assert r["msg"].startswith("IL EST 11:3"), r["msg"]


def test_le_stick_ou_un_coup_coupent_l_attente(banc):
    """Au stick, on se lève et l'attente cesse ; un coup reçu aussi. L'horloge reprend son pas d'ordinaire."""
    r = jouer(banc, ASSIS + """
        asseoirALaPlanque(0.40);
        choisir('%s 3 H');
        o.frame(30);
        pousser('KeyS');
        const stick = { attente: !!L.B.attente, assis: !!j.assis, avance: (p.heure - 0.40) * 24 };
        planter(3, 5, 3, 4); suivant();
        o.tape('KeyE'); p.heure = 0.40;
        choisir('%s 3 H');
        o.frame(30);
        j.invincible = 0; L.Entites.blesser(j, 5, null); o.frame(3);
        const coup = { attente: !!L.B.attente, assis: !!j.assis, avance: (p.heure - 0.40) * 24 };
        return { stick: stick, coup: coup };
    """ % (ATTENDRE["invite"], ATTENDRE["invite"]))
    for k in ("stick", "coup"):
        assert not r[k]["attente"] and not r[k]["assis"], k
        # Trente images d'attente : un quart d'heure ; trois heures si rien ne l'avait coupée.
        assert 0.2 < r[k]["avance"] < 0.5, "%s : l'attente a filé, puis s'est arrêtée (%s h)" % (k, r[k]["avance"])


def test_on_n_attend_pas_ce_qui_compte_le_temps(banc):
    """En plein boulot, ou la police aux fesses : l'attente se montre grisée, avec sa raison, et rien ne file. Une
    étoile en cours d'attente l'arrête."""
    r = jouer(banc, ASSIS + """
        asseoirALaPlanque(0.40);
        L.Missions.boulot.etape = 'route';
        o.tape('KeyE');
        const i = L.B.menu.items[0], grise = { actif: i.actif, detail: i.detail };
        i.actif === false || i.faire();
        L.Hud.fermerMenu();
        L.Missions.boulot.etape = null;
        const rien = !L.B.attente;
        choisir('%s 3 H');
        o.frame(10);
        L.B.recherche.etoiles = 1; o.frame(2);
        return { grise: grise, rien: rien, coupe: !L.B.attente, msg: L.B.msg };
    """ % ATTENDRE["invite"])
    assert r["grise"] == {"actif": False, "detail": ATTENDRE["refus"]["boulot"]}
    assert r["rien"]
    assert r["coupe"] and r["msg"] == interactions.ASSEOIR["refus"]["police"]


def test_minuit_passe_en_attendant_est_un_vrai_jour(banc):
    """À 23 h 30, ATTENDRE 1 H mène au lendemain, 0 h 30 : un vrai jour (`nouveauJour`), comme l'horloge
    ordinaire."""
    r = jouer(banc, ASSIS + """
        asseoirALaPlanque(23.5 / 24);
        const jour = p.jour;
        choisir('%s 1 H');
        let n = 0;
        while (L.B.attente && n < 1000) { o.frame(1); n++; }
        return { jour: p.jour - jour, heure: p.heure * 24 };
    """ % ATTENDRE["invite"])
    assert r["jour"] == 1
    assert abs(r["heure"] - 0.5) < 0.02
