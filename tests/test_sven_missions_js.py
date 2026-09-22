"""Les trois missions de Sven (m52-m54) : ce que le nouveau moteur leur doit — un donneur
posé sur son mouillage, un véhicule qui naît à la bonne place sur l'eau, avec le bon cap et
prêté par lui, et une récompense qui tombe à la fin. Le piratage lui-même a ses juges
(`test_piratage_js.py`) ; ceux-ci portent sur ce qui est PROPRE aux missions."""


def test_sven_nait_sur_son_poste_pres_du_porte_conteneurs(banc):
    """⚠️ Sur le POSTE (`carte.mouillages[…].poste`), pas sur le centre de la coque — et pas
    PILE dessus non plus : un personnage planté là volerait le bouton ACTION au bateau
    (`Histoire.poserDonneurMouillage`)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const sven = L.B.entites.find(function (e) { return e.personnage === 'sven'; });
        const mo = L.B.defs.carte.mouillages.find(function (m) { return m.slug === 'porte_conteneurs'; });
        return { sven: sven && { x: sven.x, y: sven.y }, poste: mo.poste,
                 surLePoste: sven && sven.x === mo.poste.x && sven.y === mo.poste.y,
                 marchable: sven && L.Monde.marchablePieton(Math.floor(sven.x / 16), Math.floor(sven.y / 16)) };
    }""")
    assert r["sven"], "le décor du juge est faux : Sven n'est pas né"
    assert r["marchable"], "Sven flotte : il n'est pas sur une tuile marchable"
    assert not r["surLePoste"], "Sven se tient pile sur le poste : il bouche l'accès au bateau"


def test_m52_prend_la_chaloupe_amarree_pres_de_sven(banc):
    """`amarrage:sven` : la chaloupe amarrée le plus près de son mouillage — prêtée, hors
    de la naissance décorative habituelle (`Vehicules.majMouillages`/`majAmarrages`)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Histoire.commencer('m52');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        const v = L.B.mission.vehicule;
        const am = L.Histoire.resoudre('amarrage:sven', L.Histoire.courante());
        return { slug: v && v.slug, aQui: v && v.aQui, etat: v && v.etat,
                 surLeau: v && !L.Vehicules.tuileInterdite(v, Math.floor(v.x / 16), Math.floor(v.y / 16)),
                 place: v && { x: v.x, y: v.y }, amarrage: am };
    }""")
    assert r["slug"] == "bateau", r
    assert r["aQui"] == "sven"
    assert r["etat"] == "stationne"
    assert r["surLeau"], "la chaloupe de m52 ne naît pas sur l'eau"
    assert r["place"] == r["amarrage"] or (abs(r["place"]["x"] - r["amarrage"]["x"]) < 20
                                            and abs(r["place"]["y"] - r["amarrage"]["y"]) < 20)


def test_m52_va_jusqu_au_bout_et_paie(banc):
    """La chaîne complète (les étapes qui ne dépendent pas du piratage) : sauter au dernier
    objectif, réussir, encaisser — comme les juges existants le font pour m4/m5."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const avant = L.B.partie.argent;
        L.Histoire.commencer('m52');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        L.B.partie.mission.etape = 6;                  // `retourner`, déjà fait ailleurs
        L.Histoire.reussir();
        return { argent: L.B.partie.argent - avant, mission: L.B.partie.mission,
                 faite: L.B.partie.missionsFaites && L.B.partie.missionsFaites.m52 };
    }""")
    assert r["argent"] == 350, r
    assert r["mission"] is None, "la mission reste ouverte après reussir()"
    assert r["faite"]


def test_m53_les_deux_quais_de_chalutier_sont_distincts(banc):
    """`mouillage:chalutier:0` et `:1` : deux places différentes — sinon `monter` et
    `livrer` de m53 visent la même coque et le trajet n'existe pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const a = L.Histoire.resoudre('mouillage:chalutier:0', { donneur: 'sven' });
        const b = L.Histoire.resoudre('mouillage:chalutier:1', { donneur: 'sven' });
        return { a: a, b: b, distincts: a.x !== b.x || a.y !== b.y };
    }""")
    assert r["a"] and r["b"], "le décor du juge est faux : moins de deux chalutiers"
    assert r["distincts"], "les deux quais de chalutier se confondent"


def test_m53_prend_le_chalutier_au_bon_quai(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Histoire.commencer('m53');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        const v = L.B.mission.vehicule;
        const cible = L.Histoire.resoudre('mouillage:chalutier:0', L.Histoire.courante());
        return { slug: v && v.slug, aQui: v && v.aQui, angle: v && v.angle, cibleAngle: cible.mouillage.angle,
                 place: v && { x: v.x, y: v.y }, cible: { x: cible.x, y: cible.y } };
    }""")
    assert r["slug"] == "chalutier"
    assert r["aQui"] == "sven"
    assert r["place"] == r["cible"], "le chalutier ne naît pas au centre exact de son mouillage"
    assert r["angle"] == r["cibleAngle"], "il ne part pas dans le sens de son chenal"


def test_m53_va_jusqu_au_bout_et_paie(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const avant = L.B.partie.argent;
        L.Histoire.commencer('m53');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        L.B.partie.mission.etape = 6;                  // `retourner`
        L.Histoire.reussir();
        return { argent: L.B.partie.argent - avant };
    }""")
    assert r["argent"] == 500, r


def test_m54_prend_la_coque_decorative_sans_la_dedoubler(banc):
    """⚠️ « PRENDRE LA COQUE, PAS LA DÉDOUBLER » (`Histoire.poserLeChar`) : objectif 0 est
    `pirater`, pas `monter` — quand la mission ATTEINT `monter`, si le porte-conteneurs
    décoratif (`Vehicules.majMouillages`) est déjà né à son mouillage, c'est LUI qu'on
    prend, pas un second par-dessus. Il ne naît qu'à portée du joueur (comme tout
    décor, `test_navires_js.py`) : on s'en approche d'abord, hors mission."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const mo = L.B.defs.carte.mouillages.find(function (m) { return m.slug === 'porte_conteneurs'; });
        const j = L.B.joueur;
        // ⚠️ Assez près pour naître (`portee_px` 560, moins `GAREES_MARGE` 60), assez loin
        // de l'écran (270 px de haut, marge 104) pour ne pas être le pop-in
        // qu'`Entites.visibleAEcran` refuse (`Vehicules.majMouillages`) : 450 px droit au
        // nord passe les deux bornes.
        j.x = mo.x; j.y = mo.y - 450; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        o.frame(21);
        const decoratif = L.B.entites.find(function (e) { return e.slug === 'porte_conteneurs'; });
        L.Histoire.commencer('m54');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        L.Histoire.avancer();                          // de `pirater` (0) à `monter` (1) — `poser()` s'exécute
        o.frame(2);
        const v = L.B.mission.vehicule;
        const tous = L.B.entites.filter(function (e) { return e.slug === 'porte_conteneurs'; });
        return { decoratif: !!decoratif, meme: v === decoratif, aQui: v && v.aQui, combien: tous.length };
    }""")
    assert r["decoratif"], "le décor du juge est faux : le porte-conteneurs n'est jamais né"
    assert r["meme"], "la mission a fait naître un second porte-conteneurs au lieu de prendre celui qui dormait"
    assert r["aQui"] == "sven"
    assert r["combien"] == 1, "deux porte-conteneurs collés au même quai"


def test_m54_semer_puis_le_hangar_et_ca_paie(banc):
    """Le `semer` (2 étoiles) avance vers le hangar de l'île, puis la chaîne jusqu'au bout paie.
    ⚠️ En sautant `monter`, aucun véhicule de mission n'existe : `livrer` le refuserait
    (`vehicule_detruit`, à raison — sans char, rien à livrer) — on en pose un factice,
    comme `poser()` l'aurait fait pour de vrai."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const avant = L.B.partie.argent;
        L.Histoire.commencer('m54');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        L.B.partie.mission.etape = 2;                  // `semer`
        L.B.mission.vehicule = { etat: 'stationne', mission: 'm54' };
        L.B.recherche.etoiles = 2;
        const enCoursDePoursuite = L.Histoire.objectif().type === 'semer';
        L.B.recherche.etoiles = 0;                      // semée
        o.frame(4);                                      // le pas fixe : jamais fier d'une seule image
        const apresSemer = L.B.partie.mission.etape;
        L.B.partie.mission.etape = 7;                  // `retourner`
        L.Histoire.reussir();
        return { argent: L.B.partie.argent - avant, enCoursDePoursuite: enCoursDePoursuite,
                 apresSemer: apresSemer };
    }""")
    assert r["enCoursDePoursuite"]
    assert r["apresSemer"] == 3, "semer à 0 étoile ne fait pas avancer vers le hangar de l'île"
    assert r["argent"] == 900, r


# --- Les trois actes joués jusqu'au bout (22 sept. 2026, « des missions plus longues ») ---------
#
# ⚠️ Chaque étape neuve se JOUE : le bateau navigue tuile d'eau par tuile d'eau jusqu'à l'île
# (un chemin que sa coque tient — `Vehicules.bloqueParLesTuiles`, au cap du pas), le joueur
# débarque et marche jusqu'au clocher ou au hangar, le piratage se fait au clavier, les
# Morues arrivent et tombent. Seuls `survivre` (du temps) et le `semer` (des étoiles) se
# raccourcissent : ce ne sont pas des étapes neuves, et leurs juges sont ailleurs.

OUTILS = """
  function fermer(L) { let g = 0; while (L.B.cinema && g < 200) { L.Histoire.suivante(); g++; } }
  function passer(L, o) {
    let n = 0;
    while ((L.B.scene || L.B.cinema) && n < 6000) { o.frame(1); if (L.B.cinema && n % 30 === 0) L.Histoire.suivante(); n++; }
  }
  function etape(L) { return L.B.partie.mission ? L.B.partie.mission.etape : null; }
  function images(L, o, n) { for (let k = 0; k < n; k++) { o.frame(1); fermer(L); } }
  // Un chemin de tuiles (4-voisins) de la tuile du départ jusqu'à la première qui est dans
  // `rayon` px de `cible`, par les tuiles que `ok(de, vers)` laisse passer.
  function chemin(L, x0, y0, cible, rayon, ok, rive) {
    const W = L.Monde.carte.w, H = L.Monde.carte.h;
    const d = new Int32Array(W * H).fill(-1);
    const sx = Math.floor(x0 / 16), sy = Math.floor(y0 / 16);
    const file = [sx + sy * W]; d[file[0]] = file[0];
    for (let k = 0; k < file.length; k++) {
      const i = file[k], x = i % W, y = (i - x) / W;
      const cx = x * 16 + 8, cy = y * 16 + 8;
      if ((cx - cible.x) * (cx - cible.x) + (cy - cible.y) * (cy - cible.y) < rayon * rayon && (!rive || rive(x, y))) {
        const pas = []; let c = i;
        while (c !== d[c]) { pas.push(c); c = d[c]; }
        return pas.reverse().map(function (q) { const qx = q % W; return { x: qx * 16 + 8, y: (q - qx) / W * 16 + 8 }; });
      }
      [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (s) {
        const nx = x + s[0], ny = y + s[1], j = nx + ny * W;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H || d[j] >= 0) return;
        if (!ok({ x: cx, y: cy }, { x: nx * 16 + 8, y: ny * 16 + 8 }, nx, ny)) return;
        d[j] = i; file.push(j);
      });
    }
    return null;
  }
  // Mener le bateau où l'on est jusqu'à `cible`, sur un chemin que SA coque tient.
  // `accoster` : s'arrêter à trois tuiles d'une terre où l'on marche — on débarque à la nage.
  function naviguer(L, o, cible, rayon, bilan, accoster) {
    const j = L.B.joueur, v = j.dansVehicule;
    const rive = accoster ? function (x, y) {
      for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) {
        if (!L.Monde.estEau(x + dx, y + dy) && !L.Monde.bloque(x + dx, y + dy, L.Monde.MASQUE_PIETON)) return true;
      }
      return false;
    } : null;
    const p = chemin(L, v.x, v.y, cible, rayon, function (a, b, nx, ny) {
      return L.Monde.estEau(nx, ny) && !L.Vehicules.bloqueParLesTuiles(v, b.x, b.y, Math.atan2(b.y - a.y, b.x - a.x));
    }, rive);
    if (!p) return false;
    for (let k = 0; k < p.length; k++) {
      const a = k ? p[k - 1] : { x: v.x, y: v.y };
      v.angle = Math.atan2(p[k].y - a.y, p[k].x - a.x);
      v.x = p[k].x; v.y = p[k].y; v.vitesse = 0.3; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y;
      if (k % 4 === 3) { o.frame(1); fermer(L); if (!L.B.partie.mission) break; }
    }
    v.vitesse = 0; v.vx = 0; v.vy = 0;
    if (bilan) bilan.eau = (bilan.eau || 0) + p.length * 16 / v.def.vitesse_max / 60;
    images(L, o, 3);
    return true;
  }
  // Marcher (à pied) jusqu'à `cible`, par la terre ferme.
  function marcher(L, o, cible, rayon, bilan) {
    const j = L.B.joueur;
    // ⚠️ On nage jusqu'à la rive (sept tuiles au plus : `descendre` pose le joueur à l'eau, du
    // côté de la coque qu'il trouve, quand aucun bord n'est à pied sec) — jamais plus : l'île se
    // rejoint en bateau, pas à la nage. Et autant pour remonter à bord d'une coque au large.
    const x0 = j.x, y0 = j.y;
    const p = chemin(L, j.x, j.y, cible, rayon, function (a, b, nx, ny) {
      if (L.Monde.estEau(nx, ny)) return Math.hypot(b.x - x0, b.y - y0) < 7 * 16 || Math.hypot(b.x - cible.x, b.y - cible.y) < 5 * 16;
      return !L.Monde.bloque(nx, ny, L.Monde.MASQUE_PIETON);
    });
    if (!p) return false;
    for (let k = 0; k < p.length; k++) {
      j.x = p[k].x; j.y = p[k].y; j.vx = 0; j.vy = 0;
      if (k % 4 === 3) { L.Entites.indexer(); o.frame(1); fermer(L); if (!L.B.partie.mission) break; }
    }
    if (bilan) bilan.pied = (bilan.pied || 0) + p.length * 16 / 1.4 / 60;
    L.Entites.indexer(); images(L, o, 3);
    return true;
  }
  // Débarquer sur la rive la plus proche : le bateau s'arrête, on en descend, on nage s'il le faut.
  function debarquer(L, o) {
    const j = L.B.joueur;
    L.Vehicules.descendre(j, true); L.Entites.indexer(); images(L, o, 2);
    return !j.dansVehicule;
  }
  function embarquer(L, o, v) {
    const j = L.B.joueur;
    j.x = v.x; j.y = v.y; L.Vehicules.monter(j, v); L.Entites.indexer(); images(L, o, 3);
    return j.dansVehicule === v;
  }
  // Coucher les hommes de l'étape en cours (les K.-O. se font au poing ailleurs : ici, c'est
  // l'enchaînement qu'on juge — qu'ils naissent, qu'on les trouve, que l'étape avance).
  function coucher(L, o) {
    const e0 = etape(L);
    const eux = L.B.mission.entites.filter(function (e) { return e.cible && e.etape === e0 && e.vivant; });
    eux.forEach(function (e) { L.Entites.assommer(e); });
    images(L, o, 4);
    return eux.length;
  }
  // Pirater au clavier : ACTION ouvre, la séquence au stick, un cran par flick.
  function pirater(L, o) {
    o.tape('KeyE', 2);
    if (!L.B.piratage) return false;
    const TOUCHE = { haut: 'KeyW', bas: 'KeyS', gauche: 'KeyA', droite: 'KeyD' };
    L.B.piratage.sequence.slice().forEach(function (dir) { o.touche(TOUCHE[dir]); o.frame(3); o.relacher(TOUCHE[dir]); o.frame(3); });
    fermer(L); images(L, o, 2);
    return !L.B.piratage;
  }
  function paiements(L) {
    const liste = [], vrai = L.Missions.encaisser;
    L.Missions.encaisser = function (montant) { liste.push(montant); return vrai.apply(null, arguments); };
    return liste;
  }
"""


def test_m52_joue_jusqu_au_bout_par_l_ile(banc):
    """Le repérage, sept étapes : la chaloupe, la patrouille, le guetteur au clocher de l'île (à
    l'autre bout de la baie, à pied depuis le quai de l'île), l'antenne de l'autre quai au
    retour, le guetteur du quai de Sven, la chaloupe rendue, Sven. Chaque étape neuve se joue."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        const argent = paiements(L), bilan = {}, vu = {};
        L.Histoire.commencer('m52'); passer(L, o);
        const v = B.mission.vehicule;
        vu.monter = embarquer(L, o, v) && etape(L);                       // 1 : survivre
        B.partie.mission.debutT -= 46 * 60; images(L, o, 3);                // 45 s de patrouille
        vu.lunette = etape(L);                                              // 2 : le clocher
        const guetteur = B.mission.entites.find(function (e) { return e.cible && e.etape === 2; });
        const chapelle = L.Histoire.resoudre('chapelle', L.Histoire.courante());
        vu.guetteurPres = guetteur && Math.hypot(guetteur.x - chapelle.x, guetteur.y - chapelle.y);
        vu.gps = L.Histoire.cible && L.Histoire.cible();
        vu.navigueIle = naviguer(L, o, chapelle, 20 * 16, bilan, true);
        vu.debarque = debarquer(L, o);
        vu.marcheIle = marcher(L, o, guetteur, 24, bilan);
        vu.couches = coucher(L, o);
        vu.antenne = etape(L);                                              // 3 : l'autre quai
        vu.rembarque = embarquer(L, o, v);
        const quai = L.Histoire.resoudre('mouillage:chalutier:1', L.Histoire.courante()).mouillage.poste;
        vu.navigueQuai = naviguer(L, o, quai, 4 * 16, bilan);
        vu.guetteurQuai = etape(L);                                         // 4 : le guetteur du quai
        const mo = L.Histoire.resoudre('mouillage:porte_conteneurs', L.Histoire.courante());
        vu.navigueSven = naviguer(L, o, mo, 5 * 16, bilan);
        vu.couches2 = coucher(L, o);                                        // 5 : livrer — la chaloupe est déjà à quai
        images(L, o, 6);
        vu.retourner = etape(L);                                            // 6 : retourner
        const sven = L.Histoire.donneur('sven');
        vu.marcheSven = marcher(L, o, sven, 14, bilan);
        images(L, o, 400); passer(L, o);
        return { vu: vu, bilan: bilan, fait: !!B.partie.missionsFaites.m52, argent: argent,
                 mission: B.partie.mission && B.partie.mission.etape, msg: B.msg };
    }""")
    vu = r["vu"]
    assert vu["monter"] == 1, r
    assert vu["lunette"] == 2, r
    assert vu["guetteurPres"] is not None and vu["guetteurPres"] < 8 * 16, "le guetteur ne guette pas au clocher : %s" % r
    assert vu["navigueIle"] and vu["debarque"] and vu["marcheIle"], "la chaloupe ne mène pas au clocher de l'île : %s" % r
    assert vu["couches"] == 1 and vu["antenne"] == 3, r
    assert vu["rembarque"] and vu["navigueQuai"] and vu["guetteurQuai"] == 4, "l'autre quai ne se longe pas : %s" % r
    assert vu["navigueSven"] and vu["couches2"] == 1 and vu["retourner"] == 6, r
    assert r["fait"] and r["argent"] in ([350], [525]), "350 $, ou 525 avec la prime sans dégâts : %s" % r
    assert r["bilan"]["eau"] > 25, "l'île est à l'autre bout de la baie : %s s d'eau à fond" % r["bilan"]


def test_m53_joue_jusqu_au_bout_par_le_clocher(banc):
    """Sous pavillon, sept étapes : le chalutier, l'autre quai, le relais, les deux Morues qui
    accourent, le clocher de l'île (à l'autre bout de la baie : on y mène le chalutier, on
    débarque, on pirate le jumeau du relais), le retour à quai, Sven."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        const argent = paiements(L), bilan = {}, vu = {};
        L.Histoire.commencer('m53'); passer(L, o);
        const v = B.mission.vehicule, m = L.Histoire.courante();
        vu.monter = embarquer(L, o, v) && etape(L);                         // 1 : l'autre quai
        vu.navigueQuai = naviguer(L, o, L.Histoire.resoudre('mouillage:chalutier:1', m), 4 * 16, bilan);
        vu.relais = etape(L);                                               // 2 : pirater le relais
        vu.marcheRelais = marcher(L, o, L.Histoire.resoudre('mouillage:chalutier:1', m).mouillage.poste, 24, bilan);
        vu.pirateRelais = pirater(L, o);
        vu.morues = etape(L);                                               // 3 : deux Morues
        vu.couches = coucher(L, o);
        vu.clocher = etape(L);                                              // 4 : le clocher de l'île
        const chapelle = L.Histoire.resoudre('chapelle', m);
        const gps = L.Histoire.cible();
        vu.gpsClocher = gps && Math.hypot(gps.x - chapelle.x, gps.y - chapelle.y);
        vu.rembarque = marcher(L, o, v, 20, bilan) && embarquer(L, o, v);
        vu.navigueIle = naviguer(L, o, chapelle, 20 * 16, bilan, true);
        vu.debarque = debarquer(L, o);
        vu.marcheIle = marcher(L, o, chapelle, 32, bilan);
        vu.pirateClocher = pirater(L, o);
        vu.retour = etape(L);                                               // 5 : ramener le chalutier
        vu.rembarque2 = marcher(L, o, v, 20, bilan) && embarquer(L, o, v);
        vu.navigueSven = naviguer(L, o, L.Histoire.resoudre('mouillage:chalutier:0', m), 4 * 16, bilan);
        vu.retourner = etape(L);                                            // 6 : Sven
        vu.marcheSven = marcher(L, o, L.Histoire.donneur('sven'), 14, bilan);
        images(L, o, 400); passer(L, o);
        return { vu: vu, bilan: bilan, fait: !!B.partie.missionsFaites.m53, argent: argent, msg: B.msg };
    }""")
    vu = r["vu"]
    assert vu["monter"] == 1 and vu["navigueQuai"] and vu["relais"] == 2, r
    assert vu["marcheRelais"] and vu["pirateRelais"] and vu["morues"] == 3, r
    assert vu["couches"] == 2 and vu["clocher"] == 4, "les deux Morues n'arrivent pas : %s" % r
    assert vu["gpsClocher"] is not None and vu["gpsClocher"] < 16, "la flèche ne mène pas au clocher : %s" % r
    assert vu["rembarque"] and vu["navigueIle"] and vu["debarque"] and vu["marcheIle"], "le chalutier ne mène pas à l'île : %s" % r
    assert vu["pirateClocher"] and vu["retour"] == 5, "le clocher ne se pirate pas : %s" % r
    assert vu["rembarque2"] and vu["navigueSven"] and vu["retourner"] == 6 and vu["marcheSven"], r
    assert r["fait"] and r["argent"] in ([500], [750]), "500 $, ou 750 avec la prime sans dégâts : %s" % r
    assert r["bilan"]["eau"] > 25, "l'île est à l'autre bout de la baie : %s s d'eau à fond" % r["bilan"]


def test_m54_joue_jusqu_au_bout_par_le_hangar(banc):
    """Le grand soir, huit étapes : le registre, le porte-conteneurs, la police semée, le cadenas
    du hangar sans nom de l'île (on y mène le porte-conteneurs, on débarque), les trois Morues
    qui ont suivi à la nage, le retour à quai, le registre des retours, Sven."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        const sven0 = L.Histoire.donneur('sven');
        j.x = sven0.x; j.y = sven0.y + 16; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        const argent = paiements(L), bilan = {}, vu = {};
        L.Histoire.commencer('m54'); passer(L, o);
        const m = L.Histoire.courante(), mo = L.Histoire.resoudre('mouillage:porte_conteneurs', m);
        vu.marcheRegistre = marcher(L, o, mo.mouillage.poste, 24, bilan);
        vu.pirateRegistre = pirater(L, o);
        vu.monter = etape(L);                                               // 1 : monter
        const v = B.mission.vehicule;
        vu.embarque = embarquer(L, o, v) && etape(L);                       // 2 : semer
        vu.etoiles = B.recherche.etoiles;
        B.recherche.etoiles = 0; images(L, o, 4);
        vu.hangar = etape(L);                                               // 3 : le hangar de l'île
        const hangar = L.Histoire.resoudre('hangar_ile', m);
        const gps = L.Histoire.cible();
        vu.gpsHangar = gps && Math.hypot(gps.x - hangar.x, gps.y - hangar.y);
        vu.navigueIle = naviguer(L, o, hangar, 20 * 16, bilan, true);
        vu.coque = { x: v.x, y: v.y, a: v.angle };
        vu.debarque = debarquer(L, o);
        vu.pose = { x: j.x, y: j.y, eau: L.Monde.estEau(Math.floor(j.x / 16), Math.floor(j.y / 16)) };
        vu.marcheIle = marcher(L, o, hangar, 32, bilan);
        vu.pirateHangar = pirater(L, o);
        vu.morues = etape(L);                                               // 4 : trois Morues
        vu.couches = coucher(L, o);
        vu.retour = etape(L);                                               // 5 : ramener le bateau
        vu.rembarque = marcher(L, o, v, 40, bilan) && embarquer(L, o, v);
        vu.navigueSven = naviguer(L, o, mo, 5 * 16, bilan);
        vu.registreRetour = etape(L);                                       // 6 : le registre, encore
        vu.marcheRegistre2 = marcher(L, o, mo.mouillage.poste, 24, bilan);
        vu.pirateRegistre2 = pirater(L, o);
        vu.retourner = etape(L);                                            // 7 : Sven
        vu.marcheSven = marcher(L, o, L.Histoire.donneur('sven'), 14, bilan);
        images(L, o, 400); passer(L, o);
        return { vu: vu, bilan: bilan, fait: !!B.partie.missionsFaites.m54, argent: argent, msg: B.msg };
    }""")
    vu = r["vu"]
    assert vu["marcheRegistre"] and vu["pirateRegistre"] and vu["monter"] == 1, r
    assert vu["embarque"] == 2 and vu["etoiles"] == 2 and vu["hangar"] == 3, r
    assert vu["gpsHangar"] is not None and vu["gpsHangar"] < 16, "la flèche ne mène pas au hangar : %s" % r
    assert vu["navigueIle"] and vu["debarque"] and vu["marcheIle"], "le porte-conteneurs ne mène pas à l'île : %s" % r
    assert vu["pirateHangar"] and vu["morues"] == 4 and vu["couches"] == 3 and vu["retour"] == 5, r
    assert vu["rembarque"] and vu["navigueSven"] and vu["registreRetour"] == 6, r
    assert vu["marcheRegistre2"] and vu["pirateRegistre2"] and vu["retourner"] == 7 and vu["marcheSven"], r
    assert r["fait"] and r["argent"] in ([900], [1350]), "900 $, ou 1 350 avec la prime sans dégâts : %s" % r
    assert r["bilan"]["eau"] > 30, "l'île est à l'autre bout de la baie : %s s d'eau à fond" % r["bilan"]
