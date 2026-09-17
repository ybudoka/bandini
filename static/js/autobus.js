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
    prepare = { lignes: lignes, arrets: arrets, horaire: brut.horaire };
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
    return d ? d.lignes.find(function (l) { return l.numero === numero; }) || null : null;
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
          passager: null, demande: false, bloqueT: 0,
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
    if (v.passager) return v.demande ? h.arret_images : 0;
    if (j && a && !j.dansVehicule && Math.abs(Math.floor(j.x / TT) - a.quai[0]) + Math.abs(Math.floor(j.y / TT) - a.quai[1]) <= 3) return h.arret_images;
    return Entites.visibleAEcran(v.x, v.y, 40) ? Math.round(h.arret_images * 0.6) : 0;
  }

  /** L'autobus d'une ligne, a chaque image. */
  function conduire(v) {
    const L = ligne(v.ligne);
    if (!L) { v.conducteur = null; v.etat = 'stationne'; Vehicules.rouler(v, 0); return; }
    const t = B.defs.conduite.trafic, h = donnees().horaire;
    if (v.arretT > 0) {
      v.arretT--;
      v.attendFeu = true;
      Vehicules.rouler(v, 0);
      const j = v.passager;
      if (j && v.demande && h.arret_images - v.arretT >= DESCENTE_IMAGES) descendre(j, false);
      if (v.arretT === 0) { v.attendFeu = false; v.demande = false; }
      return;
    }
    let cible = centre(L.tuiles[v.etape]);
    if (dist2(cible.x, cible.y, v.x, v.y) < 36) {
      const ici = v.etape;
      // L'abribus : on s'arrete, portes ouvertes, une fois par passage.
      if (L.arretA.has(ici) && v.servi !== ici) {
        v.servi = ici;
        const duree = dureeDArret(v, L.arretA.get(ici));
        if (duree > 0) {
          v.arret = L.arretA.get(ici);
          v.arretT = duree;
          v.attendFeu = true;
          if (Entites.visibleAEcran(v.x, v.y, 40) || v.passager) Son.SFX.porte_vehicule();
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
      if (v.conducteur !== 'ligne' || !(v.arretT > 0) || v.etat === 'epave' || v.passager) continue;
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

  function maj() {
    faireNaitre();
    majPassager();
  }

  return {
    donnees, derouler, ligne, arret, tempsDeLaPartie, placeALHeure, enService, faireNaitre,
    conduire, peutEntrer, autobusSousLaMain, prochainArret, monter, descendre, majPassager,
    invite, inviteMonter, ligneDuHud, abribusIci, attenteDe, texteDAttente, maj,
  };
})();
