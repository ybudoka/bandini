"""Les juges de banc des mécaniques neuves de la deuxième tranche de dix missions
(22 sept. 2026) — sur le modèle de `test_dix_missions_js.py` : `sans_etoile` (déclarée
depuis le premier commit de M16, jamais jouée par une mission avant `q04`) et le nouveau
résolveur de lieu `foire` (`histoire.js::lieuFoire`/`poserDonneurFoire`), qui pose le
Bonimenteur vivant à l'arche — pas `point:` — et prouve qu'un donneur `foire` héle,
répond au GPS et se retrouve par `retourner`. Les sept autres missions du lot ne
réutilisent que des types déjà prouvés (v1, ou `suivre`/`pickpocket`/`proteger` de la
première tranche) ; `scripts/verifier_missions.py --detail` les couvre statiquement.
"""

OUTILS = """
  function passer(L, o) {
    let n = 0;
    while ((L.B.scene || L.B.cinema) && n < 6000) { o.frame(1); if (L.B.cinema && n % 30 === 0) L.Histoire.suivante(); n++; }
  }
  function etape(L) { return L.B.partie.mission ? L.B.partie.mission.etape : null; }
  function fermer(L) { let g = 0; while (L.B.cinema && g < 100) { L.Histoire.suivante(); g++; } }
  function faites(L, slugs) { slugs.forEach(function (s) { L.B.partie.missionsFaites[s] = 1; }); }
  function paiements(L) {
    const liste = [], vrai = L.Missions.encaisser;
    L.Missions.encaisser = function (montant, raison) { liste.push({ montant: montant, raison: raison || null }); return vrai.apply(null, arguments); };
    return liste;
  }
  function commencer(L, o, slug) {
    L.Histoire.commencer(slug);
    L.B.cinema = null; L.B.scene = null;
  }
  function finir(L, o) { for (let k = 0; k < 400 && L.B.partie.mission; k++) o.frame(1); passer(L, o); }
"""


#: Les missions allongées — le même outil que `test_dix_missions_js.py` (22 sept. 2026, Martin : « des missions plus longues ») : ce que
#: leurs juges partagent — la nuit, se cacher pour semer, parler au bouton, et les
#: répliques qu'on a entendues (`dites`), pour juger que chaque étape neuve PARLE.
PLUS_LONGUES = """
  const dites = [];
  function ecouter(L) {
    let g = 0;
    while (L.B.cinema && g < 100) {
      const c = L.B.cinema;
      if (c.partie) c.lignes.forEach(function (l) { const k = c.partie + ':' + l.qui + ':' + (l.objectif === undefined ? '' : l.objectif); if (dites.indexOf(k) < 0) dites.push(k); });
      L.Histoire.suivante(); g++;
    }
  }
  // Quelques images, en passant les répliques qui s'ouvrent : un `pendant` part une image
  // APRÈS le changement d'étape, et tant qu'il parle, aucun objectif n'avance.
  function jouer(L, o, n) { for (let k = 0; k < (n || 6); k++) { o.frame(1); ecouter(L); } }
  function laNuit(L, o) {
    let h = L.B.partie.heure;
    for (let k = 0; k < 400 && !L.Monde.estNuit(h); k++) h = (h + 0.005) % 1;
    L.B.partie.heure = h; o.frame(2);
  }
  function aPied(L) { if (L.B.joueur.dansVehicule) L.Vehicules.descendre(L.B.joueur, true); }
  // Serrer la main au BOUTON : à deux pas de lui, ACTION.
  function serrer(L, o, slug) {
    aPied(L);
    const d = L.Histoire.donneur(slug), j = L.B.joueur;
    j.x = d.x - 16; j.y = d.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
    o.frame(1); j.angle = 0; j.face = 'droite'; L.Missions.majInvite(j); o.tape('KeyE', 2);
    const partie = L.B.cinema ? L.B.cinema.partie : null;
    ecouter(L); jouer(L, o);
    return partie;
  }
  // Semer : à pied, dans la pièce la plus proche, jusqu'à zéro étoile — puis ressortir.
  function seCacher(L, o) {
    const B = L.B, j = B.joueur;
    aPied(L);
    const avant = B.recherche.etoiles;
    let p = null, d = 1e12;
    (L.Monde.carte.def.portes || []).forEach(function (q) {
      if (!q.interieur) return;
      const dd = Math.pow(q.x * 16 + 8 - j.x, 2) + Math.pow((q.y + 1) * 16 + 8 - j.y, 2);
      if (dd < d) { d = dd; p = q; }
    });
    j.x = p.x * 16 + 8; j.y = (p.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(p); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    const dedans = !!B.interieur;
    let n = 0;
    for (; n < 9000 && B.recherche.etoiles > 0; n++) o.frame(1);
    L.Jeu.sortir(); o.fondu();
    for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
    jouer(L, o);
    return { avant: avant, dedans: dedans, images: n, porte: p.lieu, apres: B.recherche.etoiles };
  }
  function loinDe(L, a, b) { const p = L.Histoire.lieu(a), q = L.Histoire.lieu(b); return Math.round(Math.hypot(p.x - q.x, p.y - q.y) / 16); }
"""



def test_p13_le_bonimenteur_existe_pickpocket_le_complice_les_cravates_puis_retourner(banc):
    """La foire devient un vrai lieu de mission (22 sept. 2026) : le Bonimenteur est posé
    `ou: "foire"`, vivant à l'arche — contrairement à un donneur `point:` (Bouchard,
    Lachance), il est hélable, le GPS le trouve, et `retourner` fonctionne vraiment.
    `pickpocket` reprend le patron déjà prouvé de f07. ⚠️ Plus longue (22 sept. 2026) : le
    complice file en moto avec l'autre moitié (`ramasser` + `fuyard`) — on l'abîme, une
    Cravate en descend avec la caisse, on la couche, on ramasse ; ses chums arrivent
    (`tuer`, `loin`) ; puis on rapporte le tout à l'arche."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        // Posé dès le début de partie par `poserDonneurFoire` — avant même d'avoir la mission.
        const avantMission = L.Histoire.donneur('bonimenteur');
        j.x = avantMission.x - 16; j.y = avantMission.y; L.Entites.indexer();
        commencer(L, o, 'p13');
        o.frame(1); fermer(L);   // le « pendant » de l'objectif 0 ouvre une boîte
        const victime = B.mission.entites.find(function (e) { return e.pickpocket === true; });
        victime.angle = 0;
        j.x = victime.x - 12; j.y = victime.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
        const vole = L.Combat.pickpocket(j);
        jouer(L, o);
        const apresVol = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        // Le complice file : on le laisse prendre de l'avance, puis on l'abîme (un char
        // qui lui rentre dedans, un coup de feu) — à moitié cassée, la moto tombe.
        const moto = B.mission.fuyard, depart = { x: moto.x, y: moto.y };
        jouer(L, o, 240);
        const fuite = Math.round(Math.hypot(moto.x - depart.x, moto.y - depart.y) / 16);
        moto.vie = Math.floor(moto.vieMax * 0.4);
        jouer(L, o);
        const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
        const aLaCaisse = !!porteur;
        L.Entites.assommer(porteur);
        jouer(L, o);
        const caisse = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
        const tombee = !!caisse;
        j.x = caisse.x; j.y = caisse.y; L.Entites.indexer();
        jouer(L, o);
        const chums = B.mission.entites.filter(function (e) { return e.cible && e.etape === 2; });
        const bagarre = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), n: chums.length,
                          courent: chums.every(function (e) { return e.etat === 'attaque_joueur'; }) };
        chums.forEach(function (e) { L.Entites.assommer(e); });
        jouer(L, o);
        const bon = L.Histoire.donneur('bonimenteur');
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), loin: Math.round(Math.hypot(bon.x - j.x, bon.y - j.y) / 16) };
        j.x = bon.x - 16; j.y = bon.y; L.Entites.indexer();
        finir(L, o);
        return { existeAvant: !!avantMission, vole: vole, apresVol: apresVol, fuite: fuite, aLaCaisse: aLaCaisse,
                 tombee: tombee, bagarre: bagarre, retour: retour, bonTrouve: !!bon, dites: dites,
                 fait: !!B.partie.missionsFaites.p13, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["existeAvant"] is True, "le Bonimenteur est posé à l'arche dès le début de partie"
    assert r["vole"] is True, "par-derrière, à portée : le vol réussit"
    assert r["apresVol"]["etape"] == 1 and r["apresVol"]["ligne"].startswith("LE COMPLICE"), r["apresVol"]
    assert r["fuite"] > 5, f"le complice file pour vrai : {r['fuite']} tuiles en quatre secondes"
    assert r["aLaCaisse"] and r["tombee"], "la moto tombe, une Cravate en descend avec la caisse, couchée elle la lâche"
    assert r["bagarre"]["etape"] == 2 and r["bagarre"]["n"] == 2 and r["bagarre"]["courent"], r["bagarre"]
    assert r["retour"]["etape"] == 3 and r["retour"]["ligne"].startswith("RAPPORTE"), r["retour"]
    assert r["bonTrouve"] is True, "vivant en ville : `Histoire.donneur` le retrouve toujours"
    for dite in ("pendant:bonimenteur:1", "pendant:bonimenteur:2", "pendant:bonimenteur:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and 200 in r["argent"], (
        "`retourner` referme la mission — impossible avec un donneur `point:` (voir f06/h01)")


#: Les Skateux de la première étape de p14 (22 sept. 2026, « des missions plus longues ») :
#: déjà à la foire quand il finit de parler — les coucher, c'est ce qui ouvre l'escorte.
CHASSER = """
  function chasser(L, o) {
    const gars = L.B.mission.entites.filter(function (e) { return e.cible && e.etape === 0; });
    gars.forEach(function (e) { L.Entites.assommer(e); });
    for (let k = 0; k < 6; k++) { o.frame(1); fermer(L); }
    return gars.length;
  }
"""


def test_p14_chasser_les_skateux_escorter_repousser_puis_leur_chef(banc):
    """`proteger` une deuxième fois (le Bonimenteur, posé `ou: "foire"`, monte avec le
    joueur) : arrivée au poste, l'objectif avance ; les Skateux tendent une embuscade
    près de lui — même patron que f09. ⚠️ Plus longue (22 sept. 2026) : deux Skateux
    arrivent d'abord à la foire, sur le joueur (`loin`) ; et après l'embuscade, leur chef
    (`chef` : bâton, 160 de vie) sort à côté du joueur."""
    r = banc("function (L, o) {" + OUTILS + CHASSER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'p13']);
        const argent = paiements(L);
        const bon = L.Histoire.donneur('bonimenteur');
        j.x = bon.x - 16; j.y = bon.y; L.Entites.indexer();
        commencer(L, o, 'p14');
        const premiers = B.mission.entites.filter(function (e) { return e.cible && e.etape === 0; });
        const foire = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), n: premiers.length,
                        courent: premiers.every(function (e) { return e.etat === 'attaque_joueur'; }),
                        pres: Math.max.apply(null, premiers.map(function (e) { return Math.round(Math.hypot(e.x - bon.x, e.y - bon.y) / 16); })) };
        chasser(L, o);
        const protege = B.mission.protege;
        const avant = { etape: etape(L), protege: !!protege, vivant: protege && protege.vivant, leDonneur: protege === bon };
        const poste = L.Histoire.lieu('poste');
        j.x = poste.x; j.y = poste.y; protege.x = poste.x; protege.y = poste.y; protege.suit = true; L.Entites.indexer();
        for (let k = 0; k < 6; k++) { o.frame(1); fermer(L); }   // l'arrivée ouvre le « pendant » de l'objectif 2 (tuer)
        const arrive = etape(L), ligne = L.Histoire.ligneObjectif();
        const cibles = B.mission.entites.filter(function (e) { return e.cible && e.etape === 2; });
        cibles.forEach(function (e) { L.Entites.assommer(e); });
        for (let k = 0; k < 6; k++) { o.frame(1); fermer(L); }
        const chef = B.mission.entites.find(function (e) { return e.cible && e.etape === 3; });
        const leChef = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), existe: !!chef, chef: !!(chef && chef.chef),
                         vie: chef ? chef.vieMax : null, pres: chef ? Math.round(Math.hypot(chef.x - j.x, chef.y - j.y) / 16) : null };
        if (chef) L.Entites.assommer(chef);
        finir(L, o);
        return { foire: foire, avant: avant, arrive: arrive, ligne: ligne, leChef: leChef, fait: !!B.partie.missionsFaites.p14,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    f = r["foire"]
    assert f["etape"] == 0 and f["ligne"].startswith("CHASSE") and f["n"] == 2 and f["courent"] and f["pres"] <= 12, (
        f"deux Skateux arrivent à la foire, à la course : {f}")
    assert r["avant"] == {"etape": 1, "protege": True, "vivant": True, "leDonneur": True}, r["avant"]
    assert r["arrive"] == 2 and r["ligne"].startswith("REPOUSSE"), "arrivé au poste, vivant : l'objectif avance"
    c = r["leChef"]
    assert c["etape"] == 3 and c["ligne"].startswith("LEUR CHEF") and c["existe"] and c["chef"] and c["vie"] == 160, c
    assert c["pres"] <= 6, f"le chef sort à côté du joueur : {c}"
    assert r["fait"] is True and 350 in r["argent"]


ESCORTE = """
  // Un chemin de piéton, tuile par tuile (BFS) — qui contourne aussi le décor
  // solide : un poteau d'amarrage sur le quai arrête le joueur, pas la grille.
  function chemin(L, de, a) {
    const TT = 16, M = L.Monde, W = M.carte.w, H = M.carte.h;
    const sx = Math.floor(de.x / TT), sy = Math.floor(de.y / TT), gx = Math.floor(a.x / TT), gy = Math.floor(a.y / TT);
    const plein = new Set();
    for (const e of L.B.entites) if (e.type === 'decor' && e.solide) {
      const r = (e.r || 4) + 6;
      for (let y = Math.floor((e.y - r) / TT); y <= Math.floor((e.y + r) / TT); y++)
        for (let x = Math.floor((e.x - r) / TT); x <= Math.floor((e.x + r) / TT); x++) plein.add(y * W + x);
    }
    const prev = new Int32Array(W * H).fill(-1), q = [sy * W + sx];
    prev[sy * W + sx] = sy * W + sx;
    let bout = -1, meilleur = 1e9;
    for (let i = 0; i < q.length; i++) {
      const k = q[i], x = k % W, y = (k / W) | 0, d = Math.abs(x - gx) + Math.abs(y - gy);
      if (d < meilleur) { meilleur = d; bout = k; }
      if (d === 0) break;
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = x + dx, ny = y + dy, n = ny * W + nx;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H || prev[n] >= 0) continue;
        if (M.bloque(nx, ny, M.MASQUE_PIETON) || (plein.has(n) && !(nx === gx && ny === gy))) continue;
        prev[n] = k; q.push(n);
      }
    }
    const pts = [];
    for (let k = bout; k !== prev[k]; k = prev[k]) pts.push({ x: (k % W) * TT + 8, y: ((k / W) | 0) * TT + 8 });
    return pts.reverse();
  }
  // Le joueur COURT (`joueur_course`) le long du chemin ; on mesure l'écart.
  function courir(L, o, j, pts, lui) {
    const pas = L.B.defs.recherche.vitesses.joueur_course;
    let max = 0, n = 0;
    for (const p of pts) {
      for (let k = 0; Math.hypot(p.x - j.x, p.y - j.y) > 6 && k < 60; k++) {
        const d = Math.hypot(p.x - j.x, p.y - j.y);
        j.x += (p.x - j.x) / d * Math.min(pas, d); j.y += (p.y - j.y) / d * Math.min(pas, d);
        o.frame(1); n++; if (L.B.cinema) fermer(L);
        max = Math.max(max, Math.hypot(lui.x - j.x, lui.y - j.y));
      }
    }
    return { images: n, max: Math.round(max) };
  }
  function bonimenteurs(L) {
    return L.B.entites.filter(function (e) { return e.personnage === 'bonimenteur' && e.vivant; });
  }
"""


def test_p14_un_seul_bonimenteur_qui_attend_puis_court_sur_nos_pas_jusqu_au_poste(banc):
    """Martin, 22 sept. 2026 : « il y a 2 Marcel Dumouchel et je ne sais pas comment
    l'escorter ». `proteger` posait un SECOND Bonimenteur à côté de celui de l'arche, et
    le second ne bougeait pas (`fige` sortait avant `suit`). Le juge d'avant téléportait
    le protégé au poste : il n'a jamais vu qu'il restait planté. Ici, personne ne se
    téléporte — le joueur court de l'arche au poste (215 tuiles à vol d'oiseau), et le
    VRAI donneur l'attend, puis le suit sur ses pas."""
    r = banc("function (L, o) {" + OUTILS + ESCORTE + CHASSER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'p13']);
        const avant = bonimenteurs(L).length;
        commencer(L, o, 'p14');
        chasser(L, o);   // les Skateux de la foire d'abord : l'escorte est l'objectif 1
        const lui = B.mission.protege, arche = { x: lui.x, y: lui.y };
        const pendant = bonimenteurs(L).length, leDonneur = lui === L.Histoire.donneur('bonimenteur');
        // Loin de lui : il attend à l'arche, et le GPS mène à LUI, pas au poste.
        for (let k = 0; k < 60; k++) o.frame(1);
        fermer(L);
        const gps = L.Histoire.cible();
        const attend = { bouge: Math.round(Math.hypot(lui.x - arche.x, lui.y - arche.y)), suit: !!lui.suit,
                         gpsSurLui: Math.hypot(gps.x - lui.x, gps.y - lui.y) < 16 };
        // Seul au poste, sans lui : l'escorte n'est pas faite.
        const poste = L.Histoire.lieu('poste'), retour = { x: j.x, y: j.y };
        j.x = poste.x; j.y = poste.y; L.Entites.indexer();
        o.frame(2); fermer(L);
        attend.seulAuPoste = etape(L);
        j.x = retour.x; j.y = retour.y; L.Entites.indexer();
        // Rejoint : il suit, et le GPS passe au poste.
        j.x = lui.x + 20; j.y = lui.y; L.Entites.indexer();
        o.frame(1); fermer(L);
        const gps2 = L.Histoire.cible();
        const rejoint = { suit: !!lui.suit, gpsAuPoste: Math.hypot(gps2.x - poste.x, gps2.y - poste.y) < 16 };
        const course = courir(L, o, j, chemin(L, j, poste), lui);
        for (let k = 0; k < 120 && etape(L) === 1; k++) { o.frame(1); fermer(L); }
        return { avant: avant, pendant: pendant, leDonneur: leDonneur, attend: attend, rejoint: rejoint,
                 images: course.images, max: course.max, etape: etape(L),
                 luiAuPoste: Math.round(Math.hypot(lui.x - poste.x, lui.y - poste.y)) };
    }""")
    assert r["avant"] == 1 and r["pendant"] == 1, f"un seul Bonimenteur, avant ET pendant l'escorte : {r}"
    assert r["leDonneur"] is True, "on escorte le donneur qui était là, pas un second"
    assert r["attend"] == {"bouge": 0, "suit": False, "gpsSurLui": True, "seulAuPoste": 1}, (
        f"pas rejoint : il attend à l'arche, le GPS mène à lui, et le poste sans lui ne compte pas : {r['attend']}")
    assert r["rejoint"] == {"suit": True, "gpsAuPoste": True}, f"rejoint : il suit, le GPS mène au poste : {r['rejoint']}"
    assert r["images"] > 2000, f"le joueur a vraiment couru jusqu'au poste : {r['images']} images"
    assert r["max"] < 8 * 16, f"il ne s'est jamais laissé distancer de plus de 8 tuiles : {r['max']} px"
    assert r["etape"] == 2 and r["luiAuPoste"] < 7 * 16, f"arrivés ENSEMBLE au poste, l'objectif avance : {r}"


def test_p14_il_monte_dans_le_char_descend_au_poste_puis_rentre_a_l_arche(banc):
    """Le char : arrêté près de lui, il monte (caché, porté par le char) ; au poste, il
    descend — c'est près de LUI que les Skateux arrivent, et la fin se dit en personne.
    Mission finie, il lâche le joueur et rentre à l'arche, remis à neuf dès que ni lui
    ni l'arche ne sont à l'écran — le même (un neuf tirerait des dés), un seul, toujours."""
    r = banc("function (L, o) {" + OUTILS + ESCORTE + CHASSER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'p13']);
        const argent = paiements(L);
        commencer(L, o, 'p14');
        chasser(L, o);   // les Skateux de la foire d'abord : l'escorte est l'objectif 1
        const lui = B.mission.protege, arche = { x: lui.x, y: lui.y };
        const v = L.Vehicules.creer('auto', lui.x + 30, lui.y, 0, { etat: 'stationne' });
        j.x = v.x; j.y = v.y + 12; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        let n = 0;
        for (; n < 180 && !lui.dansVehicule; n++) { o.frame(1); fermer(L); }
        const aBord = { images: n, dedans: lui.dansVehicule === v, cache: lui.dessine === false };
        // En route : il va où le char va.
        const poste = L.Histoire.lieu('poste');
        v.x = poste.x; v.y = poste.y; v.vitesse = 0; j.x = v.x; j.y = v.y;
        for (let k = 0; k < 10 && etape(L) === 1; k++) o.frame(1);
        const arrive = { etape: etape(L), dehors: !lui.dansVehicule && lui.dessine !== false,
                         pres: Math.round(Math.hypot(lui.x - v.x, lui.y - v.y)), present: L.Histoire.present('bonimenteur') };
        fermer(L);
        const skateux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 2; });
        const pres = skateux.every(function (e) {
          return Math.hypot(e.x - lui.x, e.y - lui.y) < Math.hypot(e.x - arche.x, e.y - arche.y);
        });
        skateux.forEach(function (e) { L.Entites.assommer(e); });
        for (let k = 0; k < 6; k++) { o.frame(1); fermer(L); }
        // Leur chef sort à son tour (l'objectif 3), près du joueur : le coucher aussi.
        B.mission.entites.filter(function (e) { return e.cible && e.etape === 3; }).forEach(function (e) { L.Entites.assommer(e); });
        finir(L, o);
        const lache = { suit: !!lui.suit, rentre: !!lui.rentre, fait: !!B.partie.missionsFaites.p14 };
        // Toujours à l'écran : il ne disparaît pas sous nos yeux.
        for (let k = 0; k < 60; k++) o.frame(1);
        const vu = Math.hypot(lui.x - poste.x, lui.y - poste.y) < 6 * 16 && !!lui.rentre;
        // On s'en va ailleurs — au point de départ de la partie : ni le poste ni
        // l'arche à l'écran.
        L.Vehicules.descendre(j, true);
        const depart = L.Monde.carte.apparition.joueur;
        j.x = depart.x; j.y = depart.y; L.Entites.indexer();
        const loin = Math.min(Math.hypot(j.x - poste.x, j.y - poste.y), Math.hypot(j.x - arche.x, j.y - arche.y)) / 16;
        for (let k = 0; k < 90; k++) o.frame(1);
        const tous = bonimenteurs(L), neuf = tous[0] || {};
        return { aBord: aBord, arrive: arrive, nSkateux: skateux.length, skateuxPresDeLui: pres, lache: lache, vu: vu,
                 argent: argent.map(function (a) { return a.montant; }),
                 retour: { n: tous.length, lui: neuf === lui, auPoste: Math.round(Math.hypot(neuf.x - arche.x, neuf.y - arche.y)),
                           intouchable: neuf.intouchable === true, fige: neuf.etat === 'fige', suit: !!neuf.suit },
                 loin: Math.round(loin) };
    }""")
    assert r["aBord"]["dedans"] and r["aBord"]["cache"] and r["aBord"]["images"] < 120, (
        f"char arrêté près de lui : il vient, il monte, on ne le voit plus : {r['aBord']}")
    assert r["arrive"]["etape"] == 2 and r["arrive"]["dehors"] and r["arrive"]["pres"] < 40, (
        f"au poste, en char : l'objectif avance, et il descend à côté : {r['arrive']}")
    assert r["arrive"]["present"] is True, "descendu au poste, il est LÀ : la fin se dit en personne, pas au téléphone"
    assert r["nSkateux"] == 2 and r["skateuxPresDeLui"] is True, (
        "les Skateux arrivent près de lui, au poste — plus à la foire, où restait le premier Bonimenteur")
    assert r["lache"] == {"suit": False, "rentre": True, "fait": True} and 350 in r["argent"], f"mission faite : il nous lâche : {r}"
    assert r["vu"] is True, "sous nos yeux, il reste où il est"
    assert r["loin"] > 40, f"le point de départ est loin du poste et de l'arche : {r['loin']} tuiles"
    assert r["retour"] == {"n": 1, "lui": True, "auPoste": 0, "intouchable": True, "fige": True, "suit": False}, (
        f"hors champ, il est rentré à l'arche — le même, remis à neuf, un seul : {r['retour']}")


def test_p14_distance_il_nous_retrouve_sur_nos_pas(banc):
    """On file devant sans l'attendre — en char, à 4 px par image, 120 tuiles de trajet —
    puis on s'arrête. En ligne droite, il fonçait dans la première façade entre lui et
    nous et y restait ; sur nos pas, il contourne ce qu'on a contourné, et il nous
    rejoint."""
    r = banc("function (L, o) {" + OUTILS + ESCORTE + CHASSER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'p13']);
        commencer(L, o, 'p14');
        chasser(L, o);   // les Skateux de la foire d'abord : l'escorte est l'objectif 1
        const lui = B.mission.protege;
        j.x = lui.x + 20; j.y = lui.y; L.Entites.indexer();
        o.frame(1); fermer(L);
        const pts = chemin(L, j, L.Histoire.lieu('poste')).slice(0, 120);
        for (const p of pts) {
          for (let k = 0; Math.hypot(p.x - j.x, p.y - j.y) > 4 && k < 20; k++) {
            const d = Math.hypot(p.x - j.x, p.y - j.y);
            j.x += (p.x - j.x) / d * Math.min(4, d); j.y += (p.y - j.y) / d * Math.min(4, d);
            o.frame(1); fermer(L);
          }
        }
        const ecart = Math.round(Math.hypot(lui.x - j.x, lui.y - j.y));
        let n = 0;
        for (; n < 1500 && Math.hypot(lui.x - j.x, lui.y - j.y) > 48; n++) { o.frame(1); fermer(L); }
        return { ecart: ecart, images: n, reste: Math.round(Math.hypot(lui.x - j.x, lui.y - j.y)) };
    }""")
    assert r["ecart"] > 20 * 16, f"on l'a vraiment laissé loin derrière : {r}"
    assert r["reste"] <= 48, f"arrêtés, il nous retrouve sur nos pas : {r}"


def test_p14_protege_assomme_la_mission_echoue_et_il_rentre_a_l_arche(banc):
    """Raté (le protégé couché) : `protege_mort`, et le donneur ne reste pas par terre à
    l'autre bout de la ville ni ne s'en va en passant — il est reposé à l'arche, debout,
    prêt à redonner la mission."""
    r = banc("function (L, o) {" + OUTILS + ESCORTE + CHASSER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'p13']);
        commencer(L, o, 'p14');
        chasser(L, o);   // les Skateux de la foire d'abord : l'escorte est l'objectif 1
        const lui = B.mission.protege, arche = { x: lui.x, y: lui.y };
        j.x = lui.x + 20; j.y = lui.y; L.Entites.indexer();
        o.frame(1); fermer(L);
        // Rejoint, mais le joueur file seul au poste : ça ne compte pas.
        const poste = L.Histoire.lieu('poste'), ici = { x: j.x, y: j.y };
        j.x = poste.x; j.y = poste.y; L.Entites.indexer();
        o.frame(1); fermer(L);
        const seul = { etape: etape(L), suit: !!lui.suit };
        j.x = ici.x; j.y = ici.y; lui.x = ici.x - 20; lui.y = ici.y; lui.piste = null; L.Entites.indexer();
        lui.x += 40 * 16; L.Entites.indexer();          // emmené loin de l'arche
        L.Entites.assommer(lui);
        o.frame(2); passer(L, o);
        const rate = !B.partie.mission;
        j.x = arche.x; j.y = arche.y - 60 * 16; L.Entites.indexer();
        for (let k = 0; k < 90; k++) o.frame(1);
        const tous = bonimenteurs(L);
        return { seul: seul, rate: rate, n: tous.length, debout: tous.length === 1 && tous[0].etat === 'fige',
                 aLArche: tous.length === 1 ? Math.round(Math.hypot(tous[0].x - arche.x, tous[0].y - arche.y)) : null };
    }""")
    assert r["seul"] == {"etape": 1, "suit": True}, f"rejoint, mais seul au poste : l'objectif attend qu'il y soit aussi : {r}"
    assert {k: r[k] for k in ("rate", "n", "debout", "aLArche")} == {"rate": True, "n": 1, "debout": True, "aLArche": 0}, (
        f"raté : il rentre à l'arche, debout, un seul : {r}")


def test_q04_sans_etoile_la_nuit_les_plaques_chez_gilles_puis_le_bar(banc):
    """`sans_etoile` (M16, déclarée depuis le premier commit, jamais jouée par une
    mission avant celle-ci) : `majObjectif` échoue en `etoile` dès que
    `B.recherche.etoiles > 0`, tant que l'objectif la porte — posée ici sur `monter`,
    `parler` ET `livrer`. ⚠️ Plus longue (22 sept. 2026) : on attend la nuit près de la
    cantine (l'attente ne craint pas les étoiles), et le camion passe par la fourrière —
    Gilles change les plaques, au bouton, à l'autre bout de la ville — avant le bar."""
    def vu_a(etape):
        return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
            L.Jeu.commencer(); L.graine(6);
            const B = L.B, j = B.joueur; j.invincible = 1e6;
            faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'q02']);
            commencer(L, o, 'q04');
            const ETAPE = """ + str(etape) + """;
            if (ETAPE >= 1) {
                const c = L.Histoire.lieu('cantine');
                j.x = c.x; j.y = c.y + 20; L.Entites.indexer();
                laNuit(L, o); jouer(L, o);
            }
            if (ETAPE >= 2) {
                const v = B.mission.vehicule;
                j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
                L.Vehicules.monter(j, v); L.Entites.indexer();
                jouer(L, o);
            }
            const la = etape(L);
            B.recherche.etoiles = 1;
            jouer(L, o);
            return { la: la, rate: !B.partie.mission };
        }""")
    assert vu_a(0) == {"la": 0, "rate": False}, "en attendant la nuit, une étoile ne fait rien rater"
    assert vu_a(1) == {"la": 1, "rate": True}, "vu en prenant le camion : échec immédiat"
    assert vu_a(2) == {"la": 2, "rate": True}, "vu en route vers Gilles : échec immédiat"
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'q02']);
        const argent = paiements(L);
        commencer(L, o, 'q04');
        const c = L.Histoire.lieu('cantine');
        j.x = c.x; j.y = c.y + 20; L.Entites.indexer();
        let hh = B.partie.heure;
        for (let k = 0; k < 400 && L.Monde.estNuit(hh); k++) hh = (hh + 0.005) % 1;
        B.partie.heure = hh; jouer(L, o);
        const deJour = { etape: etape(L), attend: B.mission.attend };
        laNuit(L, o); jouer(L, o);
        const etapeNuit = etape(L);
        const v = B.mission.vehicule;
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        jouer(L, o);
        const etapeMonte = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), loin: loinDe(L, 'cantine', 'fourriere') };
        const gilles = L.Histoire.donneur('gilles');
        const pres = L.Histoire.tuileDeRue(gilles.x, gilles.y, 24) || { x: gilles.x, y: gilles.y + 32 };
        v.x = pres.x; v.y = pres.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer();
        jouer(L, o);
        const accueil = serrer(L, o, 'gilles');
        const etapeBar = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), aPied: !j.dansVehicule, loin: loinDe(L, 'fourriere', 'bar') };
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        jouer(L, o);
        const l = L.Histoire.lieu('bar');
        v.x = l.x; v.y = l.y; v.vitesse = 0; j.x = l.x; j.y = l.y; L.Entites.indexer();
        finir(L, o);
        return { deJour: deJour, etapeNuit: etapeNuit, etapeMonte: etapeMonte, accueil: accueil, etapeBar: etapeBar,
                 dites: dites, fait: !!B.partie.missionsFaites.q04, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["deJour"] == {"etape": 0, "attend": "ATTENDS LA NUIT"}, r["deJour"]
    assert r["etapeNuit"] == 1, "la nuit tombe près de la cantine : le camion"
    m = r["etapeMonte"]
    assert m["etape"] == 2 and m["ligne"].startswith("FAIS CHANGER LES PLAQUES") and m["loin"] > 200, m
    assert r["accueil"] == "accueil", "au bouton, Gilles parle (sa poignée de main)"
    assert r["etapeBar"]["etape"] == 3 and r["etapeBar"]["aPied"] and r["etapeBar"]["loin"] > 150, r["etapeBar"]
    for dite in ("pendant:josee:1", "pendant:josee:2", "accueil:gilles:2", "pendant:josee:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and 400 in r["argent"], "discret de bout en bout : la mission se rend"
