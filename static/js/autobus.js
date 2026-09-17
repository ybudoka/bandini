/* Bandini — autobus : les lignes, leur horaire, et le joueur qui monte a bord.

   Demande de Martin (16 sept. 2026) : « des arrets d'autobus pour se deplacer
   reellement d'un arret a l'autre selon un trace, et des bus qui passent aux
   arrets aussi ».

   ⚠️ PYTHON TRACE, ICI ON ROULE. Le trace de chaque ligne, ses arrets et son
   horaire viennent du paquet (`carte.autobus`, calcule par `app/autobus.py`) :
   un autobus ne choisit jamais une rue. Il suit sa boucle tuile par tuile,
   obeit aux feux et aux stops comme le trafic, s'arrete a chaque abribus, et
   repart.

   ⚠️ UN AUTOBUS QU'ON NE VOIT PAS EST UNE HEURE, PAS UNE ENTITE. Garder douze
   autobus vivants dans toute la ville couterait douze chars de trafic a chaque
   image, pour rien. Chaque autobus a donc une place sur sa boucle qui ne depend
   que de l'heure de la partie (`placeALHeure`) ; il ne devient un char que
   lorsque cette place entre dans la bulle, HORS DE L'ECRAN — et le trafic
   l'oublie comme les autres quand il en sort. Ce qu'on voit passer a l'arret
   est donc toujours a l'heure a peu pres, et ne coute rien le reste du temps.

   ⚠️ C'EST UN CONDUCTEUR A PART (`conducteur: 'ligne'`), jamais une exception
   glissee dans `majConducteur` : le plan le demande pour tout ce qui sort des
   rails du trafic. Il emprunte au trafic ce qui ne depend pas du choix de la
   rue — le regard devant (`obstacleDevant`), la boite a reserver
   (`croisementLibre`), les rails (`rouler`).

   ⚠️ LE PASSAGER EST « DANS UN VEHICULE » (`j.dansVehicule`) SANS LE CONDUIRE.
   Tout le jeu lit `dansVehicule` comme « pas a pied » : les pietons ne le
   frappent plus, la camera prend de l'avance, l'invite des portes se tait.
   C'est exactement ce qu'on veut d'un passager. Ce qui distingue le volant du
   siege, c'est `v.conducteur === j` — et il reste a `'ligne'`. */

const Autobus = (function () {
  'use strict';

  const PAS = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] };
  const FLECHE_DE = { '1,0': '>', '-1,0': '<', '0,-1': '^', '0,1': 'v' };

  //: Toutes les combien d'images on regarde si un autobus doit naitre. Decale
  //: de `peupler` (qui tourne aux multiples de 20) : les deux ne cherchent pas
  //: une place libre dans la meme image.
  const REGARD_IMAGES = 20, REGARD_DECALAGE = 7;

  //: Un autobus pris depuis tant d'images, sans feu ni arret pour l'excuser,
  //: et que personne ne regarde, s'efface : l'horaire le refera naitre plus loin.
  const OUBLI_BLOQUE_IMAGES = 1500;

  //: Portes ouvertes depuis tant d'images, le passager qui a demande l'arret
  //: descend : on voit l'autobus s'arreter AVANT de voir quelqu'un en sortir.
  const DESCENTE_IMAGES = 24;

  let prepare = null, source = null;

  function donnees() {
    const def = B.defs && B.defs.carte;
    const brut = def && def.autobus;
    if (!brut) return null;
    if (source === brut) return prepare;
    source = brut;
    // ⚠️ Le paquet ne porte que le nom et la tuile d'un arret : le reste se DEDUIT,
    // exactement comme `autobus.detail` — le sens est la fleche de la voie, le
    // trottoir est a sa droite (on roule a droite), l'abri juste derriere.
    const arrets = brut.arrets.map(function (a, id) {
      const sens = def.voie[a.y][a.x], p = PAS[sens] || [1, 0];
      const rx = -p[1], ry = p[0];
      const lignesDeLArret = brut.lignes.filter(function (l) { return l.arrets.some(function (c) { return c[0] === id; }); })
        .map(function (l) { return l.numero; });
      return { id: id, nom: a.nom, x: a.x, y: a.y, sens: sens, lignes: lignesDeLArret,
               quai: [a.x + rx, a.y + ry], abri: [a.x + 2 * rx, a.y + 2 * ry] };
    });
    const lignes = brut.lignes.map(function (l) {
      const tuiles = derouler(l.trace);
      const arretA = new Map();
      for (const couple of l.arrets) arretA.set(couple[1], couple[0]);
      return {
        numero: l.numero, nom: l.nom, couleur: l.couleur, autobus: l.autobus,
        tuiles: tuiles, n: tuiles.length, longueurPx: tuiles.length * TT,
        arretA: arretA, ordre: l.arrets.map(function (c) { return { arret: c[0], i: c[1] }; }),
      };
    });
    // ⚠️ LA TOURNEE DES EBOUEURS (M12) roule comme une ligne : meme boucle, memes
    // feux, memes arrets en file — ses « arrets » sont les bacs du bord du trottoir.
    const e = def.eboueurs;
    let tournee = null;
    if (e) {
      const tuiles = derouler(e.trace);
      const arretA = new Map();
      e.points.forEach(function (pt, k) { arretA.set(pt[0], k); });
      tournee = { numero: 'tournee', nom: 'Les éboueurs', tuiles: tuiles, n: tuiles.length, longueurPx: tuiles.length * TT,
                  arretA: arretA, ordre: [], autobus: 1, horaire: e.horaire,
                  points: e.points.map(function (pt, k) { return { k: k, i: pt[0], x: pt[1], y: pt[2] }; }) };
    }
    prepare = { lignes: lignes, arrets: arrets, horaire: brut.horaire, attente: brut.attente || null, tournee: tournee };
    return prepare;
  }

  /** La boucle tuile par tuile, depuis ses coins (le contraire de `autobus.coins`). */
  function derouler(trace) {
    const tuiles = [];
    for (let i = 0; i < trace.length; i++) {
      let x = trace[i][0], y = trace[i][1];
      const suivant = trace[(i + 1) % trace.length];
      const dx = Math.sign(suivant[0] - x), dy = Math.sign(suivant[1] - y);
      while (x !== suivant[0] || y !== suivant[1]) { tuiles.push([x, y]); x += dx; y += dy; }
    }
    return tuiles;
  }

  function ligne(numero) {
    const d = donnees();
    if (!d) return null;
    if (numero === 'tournee') return d.tournee;
    return d.lignes.find(function (l) { return l.numero === numero; }) || null;
  }

  function arret(id) { const d = donnees(); return d ? d.arrets[id] || null : null; }

  function centre(t) { return { x: t[0] * TT + 8, y: t[1] * TT + 8, tx: t[0], ty: t[1] }; }

  // --- L'horaire --------------------------------------------------------------------

  /** Les images de jeu ecoulees depuis le premier matin. ⚠️ Lu dans la PARTIE
      (jour et heure, qui voyagent dans la sauvegarde), jamais dans `B.t` : un
      horaire qui repart de zero a chaque chargement ferait passer l'autobus a
      l'arret a une autre heure que la veille. */
  function tempsDeLaPartie() {
    const p = B.partie;
    if (!p) return 0;
    return ((p.jour - 1) + p.heure) * B.defs.economie.jour_secondes * 60;
  }

  /** Ou l'horaire met l'autobus `rang` de sa ligne a cet instant. */
  function placeALHeure(L, rang, temps) {
    const h = donnees().horaire;
    const s = (((temps * h.vitesse_px + rang * L.longueurPx / L.autobus) % L.longueurPx) + L.longueurPx) % L.longueurPx;
    const k = s / TT, i = Math.floor(k) % L.n, f = k - Math.floor(k);
    const a = L.tuiles[i], b = L.tuiles[(i + 1) % L.n];
    return {
      x: (a[0] + (b[0] - a[0]) * f) * TT + 8, y: (a[1] + (b[1] - a[1]) * f) * TT + 8,
      i: i, s: s, angle: Math.atan2(b[1] - a[1], b[0] - a[0]), sens: FLECHE_DE[(b[0] - a[0]) + ',' + (b[1] - a[1])],
    };
  }

  function enService(numero, rang) {
    for (const v of B.entites) {
      if (v.type === 'vehicule' && v.conducteur === 'ligne' && v.ligne === numero && v.rang === rang) return v;
    }
    return null;
  }

  /** Faire naitre, HORS DE L'ECRAN et dans la bulle, les autobus que l'horaire
      y met. ⚠️ Sans un seul de du jeu : sa place vient de l'heure, sa couleur
      de sa ligne, sa silhouette est donnee. Un decor qui tire un de decale tout
      ce qui nait apres — la lecon du char en panne. */
  function faireNaitre() {
    const d = donnees(), j = B.joueur;
    if (!d || !j || B.interieur || (B.t % REGARD_IMAGES) !== REGARD_DECALAGE) return;
    const t = B.defs.conduite.trafic, temps = tempsDeLaPartie();
    for (const L of d.lignes) {
      for (let rang = 0; rang < L.autobus; rang++) {
        if (enService(L.numero, rang)) continue;
        const p = placeALHeure(L, rang, temps);
        const d2 = dist2(p.x, p.y, j.x, j.y);
        if (d2 < t.naissance_px * t.naissance_px || d2 > (t.oubli_px - 80) * (t.oubli_px - 80)) continue;
        if (Entites.visibleAEcran(p.x, p.y, 60)) continue;
        if (Entites.autour(p.x, p.y, 48, function (q) { return q.type === 'vehicule' || q.type === 'joueur'; }).length) continue;
        const v = Vehicules.creer('autobus', p.x, p.y, p.angle, {
          conducteur: 'ligne', etat: 'roule', couleur: L.couleur, sprite: 'autobus', sens: p.sens,
          ligne: L.numero, rang: rang, etape: (p.i + 1) % L.n, servi: -1, arretT: 0, arret: null,
          passager: null, demande: false, bloqueT: 0, bord: [],
        });
        if (v) v.vitesse = v.def.vitesse_max * t.vitesse_ville * 0.5;
      }
    }
  }

  // --- La conduite ------------------------------------------------------------------

  /** A la ligne d'arret : le feu, le stop, la boite libre — le trafic fait la meme
      chose dans `prochaineCible`, et un autobus n'a pas de passe-droit. */
  function peutEntrer(v, tx, ty, sens) {
    const t = B.defs.conduite.trafic, p = PAS[sens];
    const inter = p && Monde.intersectionA(tx + p[0], ty + p[1]);
    if (!inter) return true;
    const feu = Monde.feuDeCirculation(inter, sens);
    if (feu === 'rouge' || feu === 'jaune') { v.attenteBoite = 0; return false; }
    if (inter.stop === sens || feu === 'clignote_rouge') {
      if (v.stopT === undefined) v.stopT = t.arret_images;
      if (Math.abs(v.vitesse) < 0.05) v.stopT = Math.max(0, v.stopT - 1);
      if (v.stopT > 0) return false;
    }
    if (!Vehicules.croisementLibre(inter, v)) {
      v.attenteBoite = (v.attenteBoite || 0) + 1;
      if (v.attenteBoite < t.patience_images * 2) return false;
    }
    v.attenteBoite = 0;
    v.stopT = undefined;
    v.enBoite = inter;
    return true;
  }

  /** Combien d'images l'autobus reste a cet abribus — 0 : il passe sans s'arreter.

      ⚠️ Avec le joueur a bord, on ne s'arrete QUE si l'arret est demande : un
      autobus qui s'arrete aux vingt abribus d'une ligne est plus lent qu'un
      pieton, et le prendre ne servait a rien. Sans lui, on s'arrete si quelqu'un
      attend (le joueur, sur le trottoir de l'abri), et pour la VILLE quand ca se
      voit — c'est ce qui fait qu'on voit les autobus passer aux arrets. Ce qu'on
      ne voit pas ne coute pas une seconde de retard. */
  function dureeDArret(v, id) {
    const h = donnees().horaire, j = B.joueur, a = arret(id);
    // ⚠️ Quelqu'un descend ICI : c'est une demande d'arret comme celle du joueur.
    const descend = (v.bord || []).some(function (b) { return b.arret === id; });
    if (v.passager) return (v.demande || descend) ? h.arret_images : 0;
    // Quelqu'un attend a l'abribus : on s'arrete pour lui, qu'on le voie ou non.
    if (descend || quiAttend(id).some(function (e) { return e.etat === 'fige'; })) return h.arret_images;
    if (j && a && !j.dansVehicule && Math.abs(Math.floor(j.x / TT) - a.quai[0]) + Math.abs(Math.floor(j.y / TT) - a.quai[1]) <= 3) return h.arret_images;
    return Entites.visibleAEcran(v.x, v.y, 40) ? Math.round(h.arret_images * 0.6) : 0;
  }

  /** L'autobus d'une ligne, a chaque image. */
  function conduire(v) {
    const L = ligne(v.ligne);
    if (!L) { v.conducteur = null; v.etat = 'stationne'; Vehicules.rouler(v, 0); return; }
    const t = B.defs.conduite.trafic, h = donnees().horaire;
    if (v.arretT > 0) {
      if (v.collecte) {
        v.arretT--;
        v.attendFeu = true;
        Vehicules.rouler(v, 0);
        majCollecte(v, v.arretT);
        if (v.arretT === 0) v.attendFeu = false;
        return;
      }
      v.arretT--;
      v.attendFeu = true;
      Vehicules.rouler(v, 0);
      const j = v.passager;
      if (j && v.demande && h.arret_images - v.arretT >= DESCENTE_IMAGES) descendre(j, false);
      majLesVoyageurs(v, h.arret_images - v.arretT);
      if (v.arretT === 0) { v.attendFeu = false; v.demande = false; }
      return;
    }
    let cible = centre(L.tuiles[v.etape]);
    if (dist2(cible.x, cible.y, v.x, v.y) < 36) {
      const ici = v.etape;
      // L'abribus : on s'arrete, portes ouvertes, une fois par passage.
      if (L.arretA.has(ici) && v.servi !== ici) {
        v.servi = ici;
        const duree = v.collecte ? dureeDeCollecte(L.arretA.get(ici)) : dureeDArret(v, L.arretA.get(ici));
        if (duree > 0) {
          v.arret = L.arretA.get(ici);
          v.arretT = duree;
          v.attendFeu = true;
          if (!v.collecte && (Entites.visibleAEcran(v.x, v.y, 40) || v.passager)) Son.SFX.porte_vehicule();
          Vehicules.rouler(v, 0);
          return;
        }
      }
      const suivante = L.tuiles[(ici + 1) % L.n];
      // ⚠️ LE FEU SE GUETTE UNE TUILE AVANT LA LIGNE D'ARRET. Le trafic s'arrete le
      // centre sur la ligne ; un autobus fait trois tuiles, et son nez depassait
      // alors de vingt-quatre pixels dans le carrefour — les chars qui tournaient
      // l'accrochaient, le faisaient pivoter, et il restait pris huit cents images.
      if (Monde.fleche(suivante[0], suivante[1]) === 'S') {
        const apres = L.tuiles[(ici + 2) % L.n];
        const sens = FLECHE_DE[(apres[0] - suivante[0]) + ',' + (apres[1] - suivante[1])];
        if (!peutEntrer(v, suivante[0], suivante[1], sens)) { v.attendFeu = true; v.cible = cible; Vehicules.rouler(v, 0); return; }
      }
      v.attendFeu = false;
      v.etape = (ici + 1) % L.n;
      // ⚠️ On oublie l'arret servi une tuile APRES l'avoir quitte : sans ca, au
      // tour suivant de la boucle, l'autobus passait devant l'abribus sans
      // s'arreter — il croyait l'avoir deja servi.
      if (v.servi !== ici) v.servi = -1;
      if (Monde.fleche(suivante[0], suivante[1]) !== '+') v.enBoite = null;
      cible = centre(suivante);
    }
    v.cible = cible;
    v.sens = FLECHE_DE[Math.sign(cible.tx - Math.floor(v.x / TT)) + ',' + Math.sign(cible.ty - Math.floor(v.y / TT))] || v.sens;
    // La vitesse : celle du trafic, qui ralentit avant un coin, une boite ou un arret.
    let voulue = v.def.vitesse_max * t.vitesse_ville;
    const devant1 = L.tuiles[(v.etape + 1) % L.n], devant2 = L.tuiles[(v.etape + 2) % L.n];
    const f0 = Monde.fleche(cible.tx, cible.ty), f1 = Monde.fleche(devant1[0], devant1[1]);
    if (f0 === '+' || f0 === 'S' || f1 === '+' || f1 === 'S') voulue = Math.min(voulue, 1.1);
    const tourne = (devant1[0] - cible.tx) * (devant2[1] - devant1[1]) - (devant1[1] - cible.ty) * (devant2[0] - devant1[0]);
    if (tourne !== 0) voulue = Math.min(voulue, 0.9);
    if (L.arretA.has(v.etape) || L.arretA.has((v.etape + 1) % L.n)) voulue = Math.min(voulue, 0.9);
    if (Math.abs(ecartAngle(v.angle, angleVers(v.x, v.y, cible.x, cible.y))) > 0.5) voulue = Math.min(voulue, 0.8);
    const obstacle = Vehicules.obstacleDevant(v);
    if (obstacle < t.distance_securite_px) {
      voulue = 0;
      // ⚠️ Deux fois la patience du trafic : un autobus ne force pas le passage
      // pour trois secondes derriere un char qui tourne.
      if (++v.patience > t.patience_images * 2) { v.force = 90; v.patience = 0; v.klaxonT = 30; }
    } else {
      if (obstacle < t.distance_securite_px * 2) voulue *= 0.5;
      v.patience = 0;
    }
    if (v.force > 0) { v.force--; voulue = Math.max(voulue, v.def.vitesse_max * 0.25); }
    Vehicules.rouler(v, voulue);
    // Le chien de garde : pris sans raison, hors de vue et sans personne a bord,
    // l'autobus rend sa place a l'horaire.
    v.bloqueT = Math.abs(v.vitesse) < 0.05 && !v.attendFeu ? (v.bloqueT || 0) + 1 : 0;
    if (v.bloqueT > OUBLI_BLOQUE_IMAGES && !v.passager && !Entites.visibleAEcran(v.x, v.y, 60)) Entites.retirer(v);
  }

  // --- Le passager --------------------------------------------------------------------

  /** L'autobus arrete a un abribus, dont on est assez pres de la caisse pour
      monter : a moins de `rayon_monter_px` de son axe, pas de son centre — il
      fait trois tuiles, et on l'attend a sa porte comme a son cul. */
  function autobusSousLaMain(j) {
    const d = donnees();
    if (!d || !j || j.dansVehicule || B.interieur) return null;
    const r = d.horaire.rayon_monter_px;
    let meilleur = null, dMin = Infinity;
    for (const v of Entites.autour(j.x, j.y, r + 30, function (q) { return q.type === 'vehicule'; })) {
      if (v.conducteur !== 'ligne' || v.collecte || !(v.arretT > 0) || v.etat === 'epave' || v.passager) continue;
      const cx = Math.cos(v.angle), cy = Math.sin(v.angle);
      const long = borner((j.x - v.x) * cx + (j.y - v.y) * cy, -v.def.longueur / 2, v.def.longueur / 2);
      const px = v.x + cx * long, py = v.y + cy * long;
      const d2 = dist2(px, py, j.x, j.y);
      if (d2 < r * r && d2 < dMin) { dMin = d2; meilleur = v; }
    }
    return meilleur;
  }

  function prochainArret(v) {
    const L = ligne(v.ligne);
    if (!L || !L.ordre.length) return null;
    // ⚠️ Arrete a un abribus, le « prochain », c'est CELUI-CI jusqu'a ce qu'on
    // reparte : l'invite dit ou l'on descend, pas l'arret d'apres.
    const depuis = v.arretT > 0 ? v.servi : v.etape;
    let meilleur = null, ecart = Infinity;
    for (const o of L.ordre) {
      const e = ((o.i - depuis) % L.n + L.n) % L.n;
      if (e < ecart) { ecart = e; meilleur = o; }
    }
    return meilleur ? arret(meilleur.arret) : null;
  }

  /** Monter : le chauffeur regarde qui monte, et on paie. Rend vrai : la
      pression d'ACTION est depensee, meme quand la porte reste fermee. */
  function monter(j, v) {
    const h = donnees().horaire, L = ligne(v.ligne);
    // ⚠️ RECHERCHE, ON NE MONTE PAS. Un autobus ou la police ne peut pas te
    // suivre serait la meilleure cachette du jeu, pour trois dollars.
    if (B.recherche.etoiles > 0) { Hud.message('LE CHAUFFEUR NE T’OUVRE PAS'); Son.SFX.erreur(); return true; }
    if (!Missions.payer(h.tarif, 'AUTOBUS')) { Hud.message(h.tarif + ' $ — PAS ASSEZ'); Son.SFX.erreur(); return true; }
    j.passager = v; j.dansVehicule = v; v.passager = j;
    j.dessine = false; j.vx = 0; j.vy = 0; j.x = v.x; j.y = v.y;
    // ⚠️ LA PRESSION QUI FAIT MONTER EST DEPENSEE. `Missions.interagir` monte
    // pendant `Combat.maj`, et `majPassager` lit ACTION plus tard DANS LA MEME
    // IMAGE : portes encore ouvertes, il faisait redescendre aussitot — trois
    // dollars pour rien, et le HUD nommait l'arret ou l'on etait deja.
    j.monteT = B.t;
    v.demande = false;
    Entree.contexte('vehicule');
    if (L) Hud.message('LIGNE ' + L.numero + ' — ' + L.nom.toUpperCase());
    return true;
  }

  /** Descendre. A l'arret, sur le trottoir de l'abribus ; ailleurs (un
      `Vehicules.descendre` force : l'hopital, un autobus en feu), a cote de la
      caisse, du cote du trottoir d'abord. */
  function descendre(j, force) {
    const v = j && j.passager;
    if (!v) return false;
    if (!force && !(v.arretT > 0)) return false;
    const a = v.arretT > 0 && v.arret !== null ? arret(v.arret) : null;
    let pose = false;
    if (a) { j.x = a.quai[0] * TT + 8; j.y = a.quai[1] * TT + 8; pose = true; }
    for (const ecart of [Math.PI / 2, -Math.PI / 2, Math.PI]) {
      if (pose) break;
      const x = v.x + Math.cos(v.angle + ecart) * (v.def.largeur / 2 + 10), y = v.y + Math.sin(v.angle + ecart) * (v.def.largeur / 2 + 10);
      if (!Monde.bloque(Math.floor(x / TT), Math.floor(y / TT), Monde.MASQUE_PIETON)) { j.x = x; j.y = y; pose = true; }
    }
    if (!pose) { j.x = v.x; j.y = v.y + v.def.largeur; }
    j.passager = null; j.dansVehicule = null; v.passager = null; v.demande = false;
    j.dessine = true; j.vx = 0; j.vy = 0;
    // ⚠️ Le meme appui ne doit pas nous faire remonter dans la meme image.
    j.descenduT = B.t;
    Entites.dansLaCarte(j);
    Entree.contexte('pied');
    if (a) Hud.message(a.nom.toUpperCase());
    return true;
  }

  /** A bord, a chaque image : on suit la caisse, et ACTION demande l'arret — ou
      descend, si les portes sont ouvertes. */
  function majPassager() {
    const j = B.joueur, v = j && j.passager;
    if (!v) return;
    if (B.entites.indexOf(v) < 0 || v.etat === 'epave' || v.conducteur !== 'ligne') { descendre(j, true); return; }
    j.x = v.x; j.y = v.y; j.angle = v.angle; j.vx = 0; j.vy = 0;
    if (!Entree.neuf('action') || j.monteT === B.t || B.menu || B.cinema || B.transition) return;
    if (v.arretT > 0) { descendre(j, false); return; }
    if (!v.demande) {
      v.demande = true;
      Son.SFX.sonnette();
      const a = prochainArret(v);
      Hud.message('ARRÊT DEMANDÉ' + (a ? ' — ' + a.nom.toUpperCase() : ''));
    }
  }

  function invite(j) {
    const v = j && j.passager;
    if (!v) return null;
    const a = prochainArret(v);
    const nom = a ? a.nom.toUpperCase() : '';
    if (v.arretT > 0) return 'DESCENDRE — ' + nom;
    return (v.demande ? 'ARRÊT DEMANDÉ — ' : 'DEMANDER L’ARRÊT — ') + nom;
  }

  function inviteMonter(j) {
    const v = autobusSousLaMain(j);
    if (!v) return null;
    return 'MONTER — LIGNE ' + v.ligne + ' — ' + donnees().horaire.tarif + ' $';
  }

  /** La ligne du HUD, a bord. */
  function ligneDuHud(j) {
    const v = j && j.passager, L = v && ligne(v.ligne);
    return L ? 'LIGNE ' + L.numero + ' — ' + L.nom.toUpperCase() : null;
  }

  // --- A l'arret : quand passe le prochain ? -----------------------------------------

  /** L'abribus dont on se tient sur le trottoir, ou null. */
  function abribusIci(j) {
    const d = donnees();
    if (!d || !j || j.dansVehicule || B.interieur) return null;
    const tx = Math.floor(j.x / TT), ty = Math.floor(j.y / TT);
    for (const a of d.arrets) {
      if (Math.abs(a.quai[0] - tx) + Math.abs(a.quai[1] - ty) <= 1 || (a.abri[0] === tx && a.abri[1] === ty)) return a;
    }
    return null;
  }

  /** Dans combien d'images le prochain autobus de cette ligne atteint cet arret. */
  function attenteDe(L, a) {
    const o = L.ordre.find(function (x) { return x.arret === a.id; });
    if (!o) return null;
    const h = donnees().horaire, temps = tempsDeLaPartie(), cible = o.i * TT;
    let mini = Infinity;
    for (let rang = 0; rang < L.autobus; rang++) {
      const v = enService(L.numero, rang);
      // Un autobus qu'on voit : sa vraie place ; un autre : celle de l'horaire.
      const s = v ? ((v.etape - 1 + L.n) % L.n) * TT : placeALHeure(L, rang, temps).s;
      if (v && v.arretT > 0 && v.arret === a.id) return 0;
      const ecart = ((cible - s) % L.longueurPx + L.longueurPx) % L.longueurPx;
      mini = Math.min(mini, ecart / h.vitesse_px);
    }
    return mini;
  }

  /** « ARRÊT HÔPITAL · 1 DANS 40 S · 3 DANS 1 MIN » — ou null. */
  function texteDAttente(j) {
    const a = abribusIci(j);
    if (!a) return null;
    const morceaux = [];
    for (const numero of a.lignes) {
      const L = ligne(numero);
      const images = L && attenteDe(L, a);
      if (images === null || images === undefined) continue;
      const s = Math.round(images / 60);
      const quand = images === 0 ? 'À QUAI' : s < 60 ? 'DANS ' + Math.max(5, Math.round(s / 5) * 5) + ' S' : 'DANS ' + Math.round(s / 60) + ' MIN';
      morceaux.push(numero + ' ' + quand);
    }
    return a.nom.toUpperCase() + (morceaux.length ? ' · ' + morceaux.join(' · ') : '');
  }

  // --- On attend l'autobus (M12) ------------------------------------------------------
  //
  // ⚠️ Des passants qui attendent a l'abribus, montent quand il s'arrete, et
  // descendent quelques arrets plus loin. PYTHON REGLE (`autobus.ATTENTE`), ICI ON
  // JOUE — et sans un de du jeu : qui attend se tire a l'empreinte de l'arret et du
  // quart d'heure, et `creerPieton`, qui en tire deux, joue avec un de prete.

  //: Toutes les combien d'images on regarde les abribus, decale des autobus et de
  //: `peupler` : trois naissances dans la meme image se disputeraient les places.
  const ATTENTE_REGARD = 30, ATTENTE_DECALAGE = 11;

  /** Le quart d'heure de la partie : l'empreinte de qui attend. */
  function quartDHeure() {
    const p = B.partie;
    return p ? Math.floor(((p.jour - 1) + p.heure) * 96) : 0;
  }

  /** `fn` jouee avec un de PRETE : la file du jeu ne bouge pas d'un tirage. */
  function sansLeDe(graine, fn) {
    const de = B.rng;
    let s = graine >>> 0;
    B.rng = function () { s = hash2(s + 1, 0x5EED); return (s % 100000) / 100000; };
    try { return fn(); } finally { B.rng = de; }
  }

  function quiAttend(id) {
    const out = [];
    for (const e of B.entites) if (e.attend === id && e.type === 'pieton' && e.vivant) out.push(e);
    return out;
  }

  /** Combien de gens attendent a cet arret, a ce quart d'heure. ⚠️ Zero s'il vient
      d'y passer un autobus qui les a pris : l'abribus ne se remplit pas derriere
      lui dans le meme quart d'heure. */
  function combienAttendent(a) {
    const r = donnees() && donnees().attente;
    if (!r || !B.partie) return 0;
    const quart = quartDHeure();
    if (B.abribusServis && B.abribusServis[a.id] === quart) return 0;
    const h = hash2(a.id * 7919 + quart, 0xAB12);
    const part = Monde.estNuit() ? r.part_nuit : r.part;
    if ((h % 1000) / 1000 >= part) return 0;
    return 1 + ((h >>> 10) % r.par_abri);
  }

  function faceVers(dx, dy) {
    return Math.abs(dx) >= Math.abs(dy) ? (dx > 0 ? 'droite' : 'gauche') : (dy > 0 ? 'bas' : 'haut');
  }

  /** Un voyageur qui attend a l'abribus : un passant du quartier, pas une mere
      avec son petit (le petit resterait sur le trottoir quand elle monte). */
  function naitreUnVoyageur(a, k) {
    const p = PAS[a.sens] || [1, 0], glisse = (k % 2 ? 1 : -1) * (6 + 6 * k);
    const x = a.quai[0] * TT + 8 + p[0] * glisse, y = a.quai[1] * TT + 8 + p[1] * glisse;
    if (!Monde.marchablePieton(Math.floor(x / TT), Math.floor(y / TT))) return null;
    // ⚠️ PERSONNE NE NAIT DANS QUELQU'UN : un passant qui longe le trottoir a ce
    // moment-la se retrouvait enfonce de 7 px dans la dame qui attend — le juge de
    // la foule l'a vu a l'image d'apres. Il attendra le regard suivant.
    if (Entites.autour(x, y, 11, Entites.deboutDansLaFoule).length) return null;
    const graine = hash2(a.id * 31 + k, quartDHeure());
    const e = sansLeDe(graine, function () {
      let arch = null;
      for (let essai = 0; essai < 6 && (!arch || arch.accompagne); essai++) {
        arch = Entites.archetypeDeRue(x, y, (hash2(graine, essai) % 997) / 997);
      }
      return arch && !arch.accompagne ? Entites.creerPieton(x, y, arch) : null;
    });
    if (!e) return null;
    // ⚠️ IL N'EST PAS LA FOULE : il attend, comme l'ouvrier a son chantier. Sans
    // cette marque, il passerait par-dessus le plafond de passants.
    e.metier = 'autobus';
    e.attend = a.id;
    e.etat = 'fige';
    e.plante = { x: e.x, y: e.y };
    e.face = faceVers(a.x * TT + 8 - x, a.y * TT + 8 - y);        // il regarde la rue
    return e;
  }

  /** Les abribus de la bulle, HORS DE L'ECRAN : qui doit attendre y attend. */
  function naitreALAbribus() {
    const d = donnees(), j = B.joueur, r = d && d.attente;
    if (!r || !j || B.interieur || (B.t % ATTENTE_REGARD) !== ATTENTE_DECALAGE) return;
    let nes = 0;
    for (const a of d.arrets) {
      const x = a.quai[0] * TT + 8, y = a.quai[1] * TT + 8, d2 = dist2(x, y, j.x, j.y);
      if (d2 < r.naissance_min_px * r.naissance_min_px || d2 > r.naissance_max_px * r.naissance_max_px) continue;
      if (Entites.visibleAEcran(x, y, 40)) continue;
      const voulu = combienAttendent(a);
      for (let k = quiAttend(a.id).length; k < voulu; k++) if (naitreUnVoyageur(a, k)) nes++;
    }
    if (nes) Entites.indexer();
  }

  //: Le pas de la porte, en pixels hors de la caisse. ⚠️ Plus qu'un rayon de passant
  //: (5) : un voyageur qui chevauche la tole POUSSE l'autobus hors de sa voie — mesure,
  //: 29 releves sur 1175 hors du trace avec un pas de 4 px.
  const PAS_DE_PORTE = 9;

  /** La porte de l'autobus, cote trottoir, au tiers avant de la caisse. */
  function porteDe(v) {
    const cx = Math.cos(v.angle), cy = Math.sin(v.angle);
    return { x: v.x + cx * v.def.longueur / 4 - cy * (v.def.largeur / 2 + PAS_DE_PORTE),
             y: v.y + cy * v.def.longueur / 4 + cx * (v.def.largeur / 2 + PAS_DE_PORTE) };
  }

  /** Portes ouvertes depuis `ouvert` images : ceux qui descendent ici descendent,
      puis ceux qui attendent s'avancent a la porte et montent. */
  function majLesVoyageurs(v, ouvert) {
    const d = donnees(), r = d && d.attente;
    if (!r || v.arret === null || v.arret === undefined) return;
    if (ouvert === DESCENTE_IMAGES) faireDescendre(v);
    if (ouvert < r.montee_images) return;
    const porte = porteDe(v);
    for (const e of quiAttend(v.arret)) {
      if (e.etat !== 'fige') continue;                       // bouscule, il a fui : il ne monte plus
      const dx = porte.x - e.x, dy = porte.y - e.y, loin = Math.hypot(dx, dy);
      if (loin < 5) { embarquer(v, e); continue; }
      const pas = Math.min(loin, r.pas_px);
      e.x += dx / loin * pas; e.y += dy / loin * pas;
      e.plante = { x: e.x, y: e.y };
      e.vx = dx / loin * pas; e.vy = dy / loin * pas;
      if (e.anim) e.anim.dist += pas;
      e.face = faceVers(dx, dy);
    }
  }

  function embarquer(v, e) {
    const d = donnees(), r = d.attente, L = ligne(v.ligne);
    const rang = L ? L.ordre.findIndex(function (o) { return o.arret === v.arret; }) : -1;
    if (!L || rang < 0) return;
    const k = r.arrets_min + (hash2(e.id, v.arret) % (r.arrets_max - r.arrets_min + 1));
    const sortie = L.ordre[(rang + k) % L.ordre.length].arret;
    v.bord = v.bord || [];
    v.bord.push({ arret: sortie, depuis: v.arret, arch: e.arch, swaps: e.swaps, graine: hash2(e.id, sortie) });
    B.abribusServis = B.abribusServis || {};
    B.abribusServis[v.arret] = quartDHeure();
    Entites.retirer(e);
  }

  /** Ceux dont c'est l'arret descendent sur le trottoir, et redeviennent des
      passants comme les autres : ils s'en vont a leurs affaires. */
  function faireDescendre(v) {
    const a = arret(v.arret);
    if (!a || !v.bord || !v.bord.length) return;
    const partent = v.bord.filter(function (b) { return b.arret === v.arret; });
    const porte = porteDe(v);
    partent.forEach(function (b, k) {
      const x = porte.x - Math.cos(v.angle) * 12 * k, y = porte.y - Math.sin(v.angle) * 12 * k;
      if (!Monde.marchablePieton(Math.floor(x / TT), Math.floor(y / TT))) return;
      // Quelqu'un sur le pas de la porte : on ne descend pas DANS lui, on descend
      // a l'arret suivant.
      if (Entites.autour(x, y, 11, Entites.deboutDansLaFoule).length) {
        const L = ligne(v.ligne), rang = L ? L.ordre.findIndex(function (o) { return o.arret === v.arret; }) : -1;
        if (rang >= 0) b.arret = L.ordre[(rang + 1) % L.ordre.length].arret;
        return;
      }
      v.bord.splice(v.bord.indexOf(b), 1);
      const e = sansLeDe(b.graine, function () {
        const arch = Entites.archetype(b.arch);
        return Entites.creerPieton(x, y, arch ? Object.assign({}, arch, { couleurs: b.swaps || arch.couleurs }) : null);
      });
      if (!e) return;
      e.descenduDe = v.ligne;
      e.face = faceVers(a.quai[0] * TT + 8 - v.x, a.quai[1] * TT + 8 - v.y);
    });
    Entites.indexer();
  }

  // --- Les eboueurs (M12) -------------------------------------------------------------
  //
  // ⚠️ Un camion a bras mecanique qui s'arrete a chaque bac, le leve, le vide, le
  // repose et repart : un obstacle qui BOUGE dans la rue, et une raison de le
  // depasser. PYTHON TRACE LA TOURNEE (`eboueurs.py`), ICI ON ROULE — comme un
  // autobus : sa place sur la boucle ne depend que de l'heure, il ne devient un
  // char qu'en entrant dans la bulle hors de l'ecran, et rien ne tire un de.

  const BACS_REGARD = 30, BACS_DECALAGE = 17, TOURNEE_DECALAGE = 3;
  //: Au-dela, un bac qu'on ne voit plus rentre (il sera ressorti par l'horaire).
  const BACS_OUBLI_PX = 600;

  function dansLaFenetre(heure, debut, fin) { return heure >= debut && heure < fin; }

  /** Ou en est le camion sur sa tournee : les pixels parcourus depuis le debut
      de la collecte, ou null hors des heures. */
  function parcoursDuJour() {
    const T = donnees() && donnees().tournee, p = B.partie;
    if (!T || !p) return null;
    const h = T.horaire;
    if (!dansLaFenetre(p.heure, h.debut, h.fin)) return null;
    return (p.heure - h.debut) * B.defs.economie.jour_secondes * 60 * h.vitesse_px;
  }

  /** Le bac de ce point a-t-il deja ete vide aujourd'hui ? */
  function dejaVide(pt) {
    const T = donnees().tournee, p = B.partie;
    if (p.heure >= T.horaire.fin) return true;
    const s = parcoursDuJour();
    return s !== null && s >= pt.i * TT;
  }

  /** La place d'un bac sur sa tuile de trottoir : au centre en largeur, le pied a
      `BAC_PIED_Y`. ⚠️ Pas plus pres de la rue : un char de la voie d'a cote passe a
      seize pixels du centre de la tuile, et le camion (rayon 8) touche un bac
      (rayon 4) a douze. Le pied au bas de la tuile (y + 13) mettait les bacs des
      trottoirs NORD a onze pixels de la voie — le premier char venu les
      defoncait en passant. */
  const BAC_PIED_Y = 10;
  function placeDuBac(pt) {
    return { x: pt.x * TT + 8, y: pt.y * TT + BAC_PIED_Y };
  }

  function bacDe(k) {
    for (const e of B.entites) if (e.bac && e.point === k) return e;
    return null;
  }

  /** Les bacs du bord du trottoir : sortis le matin, rentres l'apres-midi — et
      toujours hors de l'ecran, qu'ils sortent ou qu'ils rentrent. */
  function majLesBacs() {
    const d = donnees(), T = d && d.tournee, j = B.joueur, p = B.partie;
    if (!T || !j || !p || B.interieur || (B.t % BACS_REGARD) !== BACS_DECALAGE) return;
    const h = T.horaire, sortis = dansLaFenetre(p.heure, h.sortis_des, h.rentres_a);
    let change = false;
    for (const pt of T.points) {
      const place = placeDuBac(pt), x = place.x, y = place.y, d2 = dist2(x, y, j.x, j.y);
      const bac = bacDe(pt.k);
      if (bac) {
        if ((!sortis || d2 > BACS_OUBLI_PX * BACS_OUBLI_PX) && !Entites.visibleAEcran(bac.x, bac.y, 40)) { Entites.retirer(bac); change = true; }
        continue;
      }
      if (!sortis || d2 < h.naissance_min_px * h.naissance_min_px || d2 > h.naissance_max_px * h.naissance_max_px) continue;
      if (Entites.visibleAEcran(x, y, 40)) continue;
      // ⚠️ Pas SUR quelqu'un : la lecon des voyageurs de l'abribus, que le juge de
      // la foule a vus naitre dans un passant.
      if (Entites.autour(x, y, 10, Entites.deboutDansLaFoule).length) continue;
      const fiche = DECORS.bac;
      // ⚠️ PAS SOLIDE. Le trottoir de la banlieue fait UNE tuile : un bac solide
      // tous les cinq pas en faisait une suite de cages, et les passants
      // rebroussaient chemin devant chacun. On le traverse a pied comme un buisson ;
      // un char, lui, le defonce (`casse`, voir DECORS).
      Entites.creer('decor', x, y, { decor: 'bac', r: fiche.r, solide: false, dessine: true, v: 0,
                                     bac: true, point: pt.k, vide: dejaVide(pt), altitude: 0 });
      change = true;
    }
    if (change) Entites.reindexerDecor();
  }

  /** Le camion, s'il est en service et que sa place entre dans la bulle. */
  function faireNaitreLaTournee() {
    const d = donnees(), T = d && d.tournee, j = B.joueur;
    if (!T || !j || B.interieur || (B.t % REGARD_IMAGES) !== TOURNEE_DECALAGE) return;
    const s = parcoursDuJour();
    if (s === null || enService('tournee', 0)) return;
    const k = (s % T.longueurPx) / TT, i = Math.floor(k) % T.n, f = k - Math.floor(k);
    const a = T.tuiles[i], b = T.tuiles[(i + 1) % T.n];
    const x = (a[0] + (b[0] - a[0]) * f) * TT + 8, y = (a[1] + (b[1] - a[1]) * f) * TT + 8;
    const h = T.horaire, d2 = dist2(x, y, j.x, j.y);
    if (d2 < h.naissance_min_px * h.naissance_min_px || d2 > h.naissance_max_px * h.naissance_max_px) return;
    if (Entites.visibleAEcran(x, y, 60)) return;
    if (Entites.autour(x, y, 48, function (q) { return q.type === 'vehicule' || q.type === 'joueur'; }).length) return;
    const t = B.defs.conduite.trafic;
    // ⚠️ La silhouette et la couleur DONNEES : `creer` ne tire alors aucun de.
    const v = Vehicules.creer('camion', x, y, Math.atan2(b[1] - a[1], b[0] - a[0]), {
      conducteur: 'ligne', etat: 'roule', sprite: 'camion_benne', couleur: '#e6e1d3',
      sens: FLECHE_DE[(b[0] - a[0]) + ',' + (b[1] - a[1])],
      ligne: 'tournee', collecte: true, rang: 0, etape: (i + 1) % T.n, servi: -1, arretT: 0, arret: null,
      passager: null, demande: false, bloqueT: 0,
    });
    if (v) v.vitesse = v.def.vitesse_max * t.vitesse_ville * 0.4;
  }

  /** Combien d'images le camion reste a ce point : le temps d'un bac, s'il y en a
      un plein ; sinon il passe. */
  function dureeDeCollecte(k) {
    const T = donnees().tournee, bac = bacDe(k);
    return bac && !bac.vide && !bac.brise ? T.horaire.arret_images : 0;
  }

  /** Le bras : le bac monte du trottoir au-dessus de la benne, se vide, redescend,
      et se repose EXACTEMENT ou il etait. `reste` = images d'arret restantes. */
  function majCollecte(v, reste) {
    const T = donnees().tournee, h = T.horaire, bac = bacDe(v.arret);
    if (!bac || bac.brise) return;
    const ecoule = h.arret_images - reste, debut = Math.round((h.arret_images - h.leve_images) / 2);
    const u = (ecoule - debut) / h.leve_images;
    if (!bac.pied) bac.pied = { x: bac.x, y: bac.y };
    if (ecoule === debut) Son.SFX.chantier('benne', bac.x, bac.y, 360);
    if (u <= 0 || u >= 1) { bac.altitude = 0; bac.x = bac.pied.x; bac.y = bac.pied.y; if (u >= 1) bac.vide = true; return; }
    const haut = Math.sin(u * Math.PI);                      // monte, tient, redescend
    bac.altitude = Math.round(haut * 22);
    bac.x = bac.pied.x + (v.x - bac.pied.x) * haut * 0.45;
    bac.y = bac.pied.y + (v.y - bac.pied.y) * haut * 0.45;
    if (u > 0.45 && u < 0.55) bac.vide = true;
  }

  function maj() {
    faireNaitre();
    faireNaitreLaTournee();
    majLesBacs();
    naitreALAbribus();
    majPassager();
  }

  return {
    donnees, derouler, ligne, arret, tempsDeLaPartie, placeALHeure, enService, faireNaitre,
    conduire, peutEntrer, autobusSousLaMain, prochainArret, monter, descendre, majPassager,
    invite, inviteMonter, ligneDuHud, abribusIci, attenteDe, texteDAttente, maj,
    quiAttend, combienAttendent, naitreALAbribus, porteDe, quartDHeure, dureeDArret, naitreUnVoyageur,
    parcoursDuJour, dejaVide, bacDe, placeDuBac, majLesBacs, faireNaitreLaTournee, dureeDeCollecte,
  };
})();
