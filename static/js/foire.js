/* Bandini — la foire qui roule : le petit train, la montagne russe et les
   nacelles de la grande roue.

   Martin : « ajoute un petit train qui fait le tour de la foire et une énorme
   montagne russe ».

   ⚠️ Python décide (`carte.FOIRE`, `carte.voie_de_montagne_russe`) : la voie du
   train tuile par tuile, la voie de la montagne russe point par point (x, y, z),
   ses pieds, et toute la conduite — vitesses, gravité, temps en gare. Ce script
   ne fait que les faire ROULER et les PEINDRE.

   ⚠️ Rien ne tire au dé ici : chaque dé consommé décale tous ceux qui suivent,
   et la leçon a déjà fait tomber des juges sans rapport cinq fois cette semaine.

   ⚠️ Ni le train ni les chariots ne sont dans `B.entites` — la leçon des bêtes :
   ce qui ne compte pour rien ne doit pas être dans la liste de ce qui compte (ni
   parcouru par la foule, ni indexé, ni oublié). Ils se TRIENT pourtant avec le
   reste au dessin (`ajouterVisibles`) : un wagon passe devant un passant ou
   derrière, selon sa rangée.

   ⚠️ **EN VOLUME, COMME LES VÉHICULES** (Martin : « dans le même style que les
   véhicules ») : wagons, chariots et nacelles sont des machines (`FOIRE_EN_VOLUME`,
   `sprites.js`) cuites au cap par `Atlas.cuireCap` — et un chariot PENCHE.

   ⚠️ **ON Y FAIT UN TOUR** (« qu'on puisse y faire un tour », « pareil pour la
   montagne russe et la grande roue »). Le petit train et le Colosse marquent
   l'arrêt à leur gare à chaque tour, la grande roue ne s'arrête pas ; à ACTION
   près d'un siège, on s'y assoit (`j.manege`), on fait un tour complet, et on
   descend là où l'on est monté. Assis, le joueur n'est pas « dans un véhicule » : il ne
   conduit rien, la police ne le sort de rien — il est À PIED ET PORTÉ, comme à
   bord du traversier (`j.aBord`), et c'est `Foire` qui le pose à chaque image
   là où est son siège. On ne monte pas recherché : un manège où la police ne
   peut pas te suivre serait la meilleure cachette du jeu. */

const Foire = (function () {
  'use strict';

  //: Ce qui arrête le train : quelqu'un de debout sur la voie, ou un char.
  const CORPS = { joueur: 1, pieton: 1, agent: 1, vehicule: 1 };
  //: Ce qu'un wagon repousse : les gens à pied (un char a sa propre physique).
  const PIETONS = { joueur: 1, pieton: 1, agent: 1 };
  //: Les demi-mesures d'un wagon, vu d'en haut : la locomotive est plus longue.
  //: ⚠️ Celles des MACHINES (`FOIRE_EN_VOLUME`) : 20 px et 16 de long, 10 de large.
  const LOCO = { l: 10, w: 5 };
  const WAGON = { l: 8, w: 5 };
  //: Qui est assis dans le train quand on n'y est pas, banc par banc (un indice de
  //: `VOYAGEURS`, ou null : banc vide). ⚠️ Écrit à la main, jamais tiré au dé.
  const PLACES = [[0, 1], [2, null], [null, 3], [4, 5]];
  //: Des gens de la foire : les couleurs d'un passant (`pietons.py`).
  const VOYAGEURS = [
    { c: '#d9534a', h: '#3b2a20', s: '#e8b088', p: '#2a2a3a' },
    { c: '#f2d34f', h: '#d8b36a', s: '#f0c9a0', p: '#3a4a6a' },
    { c: '#3f7fc4', h: '#1b1b1f', s: '#8d5a3b', p: '#2a2a3a' },
    { c: '#5fb87a', h: '#a0522d', s: '#e8b088', p: '#5a4a3a' },
    { c: '#9b59b6', h: '#1b1b1f', s: '#c68a5e', p: '#2a2a3a' },
    { c: '#efe6d0', h: '#7a4a2a', s: '#f0c9a0', p: '#3a4a6a' },
  ];
  //: Le machiniste, sa casquette de toile bleue.
  const MACHINISTE = { c: '#2c4a78', h: '#2c4a78', s: '#e8b088', p: '#1f2a3a' };
  //: Un numéro de tri hors de portée de celui des entités (`creer` compte de 1).
  const ID_TRI = 900000000;

  let train = null;
  let mr = null;
  let roue = null;

  // --- Le petit train -----------------------------------------------------------------

  /** La voie en pixels, un point par pixel de rail : droit au milieu d'une tuile,
      un quart de cercle de rayon 8 autour du COIN dans une courbe — la même
      courbe que peint la tuile (`TUILES.T`). */
  function construireTrain(d) {
    const tuiles = d.voie, n = tuiles.length, xs = [], ys = [];
    let sGare = null;
    for (let i = 0; i < n; i++) {
      // ⚠️ La gare est une tuile DROITE : son milieu est à huit pixels de son entrée.
      if (i === d.gare) sGare = xs.length + 8;
      const p = tuiles[(i + n - 1) % n], c = tuiles[i], s = tuiles[(i + 1) % n];
      const cx = c[0] * TT + 8, cy = c[1] * TT + 8;
      const ax = cx + (p[0] - c[0]) * 8, ay = cy + (p[1] - c[1]) * 8;   // l'entrée
      const bx = cx + (s[0] - c[0]) * 8, by = cy + (s[1] - c[1]) * 8;   // la sortie
      if (p[0] + s[0] === 2 * c[0] && p[1] + s[1] === 2 * c[1]) {
        for (let k = 0; k < 16; k++) { xs.push(ax + (bx - ax) * k / 16); ys.push(ay + (by - ay) * k / 16); }
        continue;
      }
      const ox = ax + bx - cx, oy = ay + by - cy;                         // le coin
      const a0 = Math.atan2(ay - oy, ax - ox);
      let da = Math.atan2(by - oy, bx - ox) - a0;
      if (da > Math.PI) da -= 2 * Math.PI;
      if (da < -Math.PI) da += 2 * Math.PI;
      for (let k = 0; k < 13; k++) {
        const a = a0 + da * k / 13;
        xs.push(ox + 8 * Math.cos(a)); ys.push(oy + 8 * Math.sin(a));
      }
    }
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (let i = 0; i < xs.length; i++) {
      x0 = Math.min(x0, xs[i]); x1 = Math.max(x1, xs[i]); y0 = Math.min(y0, ys[i]); y1 = Math.max(y1, ys[i]);
    }
    return { def: d, xs: xs, ys: ys, n: xs.length, s: 0, v: d.vitesse, sifflet: 0, bloque: false,
             boite: [x0 - 16, y0 - 16, x1 + 16, y1 + 16],
             // La gare : où la locomotive s'arrête, combien de temps il reste à quai,
             // combien de fois il y est passé, et le wagon où le joueur est assis.
             sGare: sGare, attente: 0, tours: 0, passager: null };
  }

  /** Le point de la voie à l'abscisse `s` (en px, modulo la boucle), et le cap. */
  function pointDuTrain(s) {
    const n = train.n, i = ((Math.floor(s) % n) + n) % n, j = (i + 1) % n, t = s - Math.floor(s);
    const x = train.xs[i] + (train.xs[j] - train.xs[i]) * t, y = train.ys[i] + (train.ys[j] - train.ys[i]) * t;
    const a = (i + n - 2) % n, b = (i + 2) % n;
    return { x: x, y: y, a: Math.atan2(train.ys[b] - train.ys[a], train.xs[b] - train.xs[a]) };
  }

  /** Les wagons, de la locomotive (0) au dernier. */
  function wagons() {
    const d = train.def, out = [];
    for (let k = 0; k <= d.wagons; k++) out.push(pointDuTrain(train.s - k * d.ecart_px));
    return out;
  }

  /** ⚠️ UN TRAIN DE FOIRE NE RENVERSE PERSONNE. La locomotive surveille la voie
      devant elle, courbes comprises (on sonde LE LONG des rails, pas en ligne
      droite), et s'arrête devant quiconque s'y tient. */
  function quelquUnDevant() {
    const d = train.def, sondes = [];
    for (let a = 10; a <= d.regard_px; a += 8) sondes.push(pointDuTrain(train.s + a));
    const loco = pointDuTrain(train.s);
    for (const e of B.entites) {
      if (!CORPS[e.type] || !e.vivant || e.dansVehicule) continue;
      if (Math.abs(e.x - loco.x) > d.regard_px + 16 || Math.abs(e.y - loco.y) > d.regard_px + 16) continue;
      const r = (e.r || 5) + WAGON.w;
      for (const p of sondes) if (dist2(e.x, e.y, p.x, p.y) < r * r) return e;
    }
    return null;
  }

  function siffler() {
    const j = B.joueur, loco = pointDuTrain(train.s);
    train.sifflet = train.def.sifflet_images;
    if (j && dist2(j.x, j.y, loco.x, loco.y) < 260 * 260) Son.SFX.sifflet_train();
  }

  function majTrain() {
    const d = train.def;
    if (train.sifflet > 0) train.sifflet--;
    // ⚠️ À QUAI : il attend qu'on monte, puis il siffle et repart. Le compte se
    // fait ici, pas au départ : quelqu'un planté devant lui le retient ensuite
    // comme n'importe où sur la voie.
    if (train.attente > 0) {
      train.v = 0;
      train.bloque = false; train.bloquePar = null;
      if (--train.attente === 0) siffler();
      return;
    }
    const devant = quelquUnDevant();
    train.bloque = !!devant;
    train.bloquePar = devant;                // qui : la foule marche aussi sur la voie
    if (devant) {
      train.v = 0;
      // Il siffle, et il resiffle tant qu'on reste planté là.
      if (train.sifflet <= 0) siffler();
    } else {
      train.v = Math.min(d.vitesse, train.v + d.reprise);
    }
    const avant = train.s;
    train.s = (train.s + train.v) % train.n;
    // La gare : la locomotive passe son point d'arrêt dans cette image, elle s'y pose.
    if (train.sGare !== null && train.v > 0) {
      const ecart = (train.sGare - avant + train.n) % train.n;
      if (ecart > 0 && ecart <= train.v) {
        train.s = train.sGare; train.v = 0; train.attente = d.gare_images; train.tours++;
      }
    }
  }

  // --- Faire un tour ------------------------------------------------------------------

  //: Ce que dit chaque manège : l'invite, le refus (recherché), l'accueil, l'arrivée.
  const TOURS = {
    train: { invite: 'UN TOUR DE PETIT TRAIN', refus: 'LE MACHINISTE NE T’ATTEND PAS',
             accueil: 'LE PETIT TRAIN — UN TOUR DE LA FOIRE', arrivee: 'TERMINUS — TOUT LE MONDE DESCEND' },
    montagne: { invite: 'UN TOUR DE MONTAGNE RUSSE', refus: 'LE COLOSSE NE T’ATTEND PAS',
                accueil: 'LE COLOSSE — ACCROCHE-TOI', arrivee: 'LE COLOSSE — ON RECOMMENCE ?' },
    roue: { invite: 'UN TOUR DE GRANDE ROUE', refus: 'LE FORAIN NE T’OUVRE PAS',
            accueil: 'LA GRANDE ROUE — REGARDE LA BAIE', arrivee: 'LA GRANDE ROUE — UN TOUR COMPLET' },
  };

  /** Debout, libre de ses mouvements, dehors : quelqu'un qui peut monter. */
  function libre(j) {
    return !!j && j.vivant && !j.manege && !j.dansVehicule && !j.aBord && !j.enjambe && !B.interieur;
  }

  function machineDe(quoi) { return quoi === 'train' ? train : quoi === 'roue' ? roue : mr; }

  /** Où est assis celui du siège `m` : { x, y } au sol, et `z` sa hauteur. ⚠️ Dans
      la roue, le « sol » est devant le portique, là où l'on descend : la nacelle
      monte et descend AU-DESSUS de lui, et la caméra la suit par `z`. */
  function siege(m) {
    if (m.quoi === 'train') { const p = wagons()[m.k]; return { x: p.x, y: p.y, z: 0 }; }
    if (m.quoi === 'roue') {
      const a = attache(m.k), y = roue.y + roue.devant;
      return { x: a.x, y: y, z: y - (a.y + 8) };
    }
    const p = pointDeMontagne(mr.s - m.k * mr.def.ecart_px);
    return { x: p.x, y: p.y, z: p.z };
  }

  /** Le wagon arrêté en gare dont on est assez près pour y monter : `{ quoi, k }`,
      ou null. Jamais la locomotive — c'est la place du machiniste. */
  function trainSousLaMain(j) {
    if (!train || !(train.attente > 0) || train.passager !== null || !libre(j)) return null;
    const liste = wagons(), r = train.def.rayon_monter_px;
    let meilleur = null, dMin = r;
    for (let k = 1; k < liste.length; k++) {
      const e = Math.hypot(liste[k].x - j.x, liste[k].y - j.y);
      if (e <= dMin && faceA(j, liste[k].x, liste[k].y)) { dMin = e; meilleur = k; }
    }
    return meilleur === null ? null : { quoi: 'train', k: meilleur };
  }

  /** Le chariot arrêté en gare au pied du Colosse : on s'y assoit depuis le quai. */
  function montagneSousLaMain(j) {
    if (!mr || !(mr.attente > 0) || mr.passager !== null || !libre(j)) return null;
    const d = mr.def;
    let meilleur = null, dMin = d.rayon_monter_px;
    for (let k = 0; k < d.chariots; k++) {
      const p = pointDeMontagne(mr.s - k * d.ecart_px);
      const e = Math.hypot(p.x - j.x, p.y - j.y);
      if (e <= dMin && faceA(j, p.x, p.y)) { dMin = e; meilleur = k; }
    }
    return meilleur === null ? null : { quoi: 'montagne', k: meilleur };
  }

  /** Au pied de la grande roue, devant son portique : la nacelle la plus basse.
      ⚠️ Une grande roue ne s'arrête pas pour qu'on monte — elle tourne au pas. */
  function roueSousLaMain(j) {
    if (!roue || roue.passager !== null || !libre(j)) return null;
    if (Math.hypot(j.x - roue.x, j.y - (roue.y + roue.devant)) > roue.rayonMonter) return null;
    if (!faceA(j, roue.x, roue.y + roue.devant)) return null;
    let meilleur = 0, dMin = Infinity;
    for (let k = 0; k < roue.n; k++) {
      const e = Math.abs(ecartAngle(angleDeNacelle(k), Math.PI / 2));
      if (e < dMin) { dMin = e; meilleur = k; }
    }
    return { quoi: 'roue', k: meilleur };
  }

  function sousLaMain(j) { return trainSousLaMain(j) || montagneSousLaMain(j) || roueSousLaMain(j); }

  // --- Les trois jeux d'adresse ---------------------------------------------------------
  //
  // ⚠️ **UN JEU D'ADRESSE EST UN DÉFI, PAS UN MOTEUR** (la fiche du plan l'écrit
  // en majuscules) : ce qui suit ne sert qu'à répondre « quel comptoir est sous
  // la main » et « où sont les cibles ». La règle du jeu, le compte, le chrono
  // et la prime vivent dans `missions.DEFIS` et `Histoire`, avec les trois défis
  // de char de la v1 — rien de neuf n'entre dans le moteur pour eux.

  //: Un comptoir de jeu se lit d'aussi près qu'un étal d'ambulant : on est
  //: DEVANT, et la baraque nous arrête déjà (`solide`).
  const PORTEE_JEU = 30;

  function jeux() { return (Monde.carte && Monde.carte.def && Monde.carte.def.jeux_de_foire) || []; }

  /** Les comptoirs où l'on JOUE : les trois jeux d'adresse, et les kiosques
      qu'un défi nomme (`foire:<kiosque>`, les dix-huit défis du 23 sept. 2026 —
      le lance-anneaux, les peluches, les ballons ne servaient qu'à vendre).
      ⚠️ Nommé ne veut pas dire ouvert : c'est `Histoire.defiDuComptoir` qui
      dit si le défi est débloqué, et ACTION passe au suivant sinon. */
  function comptoirs() {
    const def = Monde.carte && Monde.carte.def;
    if (!def) return [];
    const nommes = ((B.defs && B.defs.defis) || []).filter(function (d) { return d.ou && d.ou.indexOf('foire:') === 0; })
      .map(function (d) { return d.ou.slice(6); });
    const siens = jeux().slice();
    for (const k of def.kiosques_de_foire || []) {
      if (nommes.indexOf(k.slug) >= 0 && !siens.some(function (q) { return q.slug === k.slug; })) siens.push(k);
    }
    return siens;
  }

  /** Le décor d'un jeu, tel qu'il vit dans le monde (il peut être CASSÉ). */
  function kiosqueDuJeu(slug) {
    const j = comptoirs().find(function (q) { return q.slug === slug; });
    if (!j) return null;
    return Entites.decorAutour(j.x * TT + 8, j.y * TT + 15, 10).find(function (e) {
      return e.decor === slug;
    }) || null;
  }

  /** Les trois cibles de la galerie de tir, cassées ou debout. */
  function cibles() {
    return B.entites.filter(function (e) { return e.type === 'decor' && e.decor === 'cible_foire'; });
  }

  /** Le comptoir de jeu sous la main du joueur : son slug, ou null. ⚠️ Le plus
      proche, et à pied seulement — au volant, ACTION fait descendre. */
  function jeuSousLaMain(j) {
    if (!j || j.dansVehicule || j.manege || B.interieur) return null;
    let meilleur = null, dMin = PORTEE_JEU;
    for (const q of comptoirs()) {
      const d = Math.hypot(q.x * TT + 8 - j.x, q.y * TT + 15 - j.y);
      if (d <= dMin && faceA(j, q.x * TT + 8, q.y * TT + 15)) { dMin = d; meilleur = q; }
    }
    return meilleur ? meilleur.slug : null;
  }

  function inviteMonter(j) {
    const m = sousLaMain(j);
    return m ? TOURS[m.quoi].invite : null;
  }

  /** Monter : rend vrai, la pression d'ACTION est dépensée même quand on refuse. */
  function monter(j, m) {
    if (B.recherche && B.recherche.etoiles > 0) {
      Hud.message(TOURS[m.quoi].refus);
      Son.SFX.erreur();
      return true;
    }
    const machine = machineDe(m.quoi);
    machine.passager = m.k;
    // ⚠️ `cran` : la roue ne marque pas d'arrêt, elle compte ses crans — un tour,
    // c'est `n * 6` crans depuis celui où l'on est monté.
    j.manege = { quoi: m.quoi, k: m.k, tours: machine.tours, cran: cranDeRoue(), monteT: B.t, z: 0 };
    j.dessine = false; j.vx = 0; j.vy = 0;
    const s = siege(j.manege);
    j.x = s.x; j.y = s.y; j.manege.z = s.z;
    Hud.message(TOURS[m.quoi].accueil);
    return true;
  }

  /** Descendre, de retour en gare : sur le quai, à côté de son siège — celui du
      petit train au nord de la voie, celui du Colosse au sud (ses planches).
      `force` : ailleurs qu'en gare (le joueur est mort, on l'a sorti de la carte)
      — on le lâche où il est. */
  function descendre(j, force) {
    const m = j && j.manege;
    if (!m) return false;
    const machine = machineDe(m.quoi);
    if (machine) machine.passager = null;
    if (!force && machine) {
      const s = siege(m);
      j.x = m.quoi === 'roue' ? roue.x : s.x;
      j.y = m.quoi === 'train' ? train.def.quai[2] * TT + 8 : m.quoi === 'roue' ? s.y : s.y + 12;
    }
    j.manege = null;
    j.dessine = true; j.vx = 0; j.vy = 0;
    j.descenduT = B.t;
    Entites.dansLaCarte(j);
    if (!force) Hud.message(TOURS[m.quoi].arrivee);
    return true;
  }

  /** Assis, à chaque image : on suit son siège, et on descend de retour en gare. */
  function majPassager() {
    const j = B.joueur, m = j && j.manege;
    if (!m) return;
    // ⚠️ `j.manege` est le nom que TOUTES les gardes du jeu connaissent (combat, marche, invites) :
    // la cabine d'une grue de chantier s'en sert (`Chantiers.monterDansLaGrue`), et ce n'est pas un
    // manège — sans cette ligne, la foire éjecterait aussitôt quelqu'un qu'elle ne connaît pas.
    if (m.quoi === 'grue') return;
    const machine = machineDe(m.quoi);
    if (!j.vivant || B.interieur || !machine) { descendre(j, true); return; }
    const s = siege(m);
    j.x = s.x; j.y = s.y; m.z = s.z; j.vx = 0; j.vy = 0;
    if (m.quoi === 'roue') { if (cranDeRoue() - m.cran >= roue.n * roue.variantes) descendre(j, false); return; }
    if (machine.attente > 0 && machine.tours > m.tours) descendre(j, false);
  }

  // --- La grande roue -----------------------------------------------------------------

  /** La roue, lue dans son décor : où elle est, et comment elle tourne. ⚠️ Elle
      tourne par CRANS, ceux de son dessin (`DECORS.grande_roue` : un cran toutes
      les `anime` images, `variantes` crans d'une nacelle à l'autre) — une nacelle
      peinte entre deux crans décrocherait du bout de son rayon. */
  function construireRoue(tuile) {
    const f = DECORS.grande_roue;
    return { x: tuile.x * TT + 8, y: tuile.y * TT + 15, f: f, n: f.nacelles, variantes: f.variantes,
             devant: f.sol[1] + 6, rayonMonter: 26, passager: null };
  }

  //: `t` : l'image (par défaut, celle-ci). ⚠️ `Foire.maj` tourne AVANT que l'image
  //: n'avance (`B.t++`, à la fin de `Jeu.maj`) : un juge qui mesure après doit
  //: demander l'image d'avant.
  function cranDeRoue(t) { return roue ? Math.floor((t === undefined ? B.t : t) / roue.f.anime) : 0; }

  function angleDeNacelle(k, t) {
    return (k / roue.n + cranDeRoue(t) / (roue.n * roue.variantes)) * Math.PI * 2;
  }

  function ecartAngle(a, b) { return ((a - b) % (Math.PI * 2) + Math.PI * 3) % (Math.PI * 2) - Math.PI; }

  /** L'attache de la nacelle `k` dans le monde : le bout de son rayon. */
  function attache(k, image) {
    const f = roue.f, t = angleDeNacelle(k, image);
    return { x: Math.round(roue.x - f.ancre[0] + f.moyeu[0] + Math.cos(t) * f.rayon),
             y: Math.round(roue.y - f.ancre[1] + f.moyeu[1] + Math.sin(t) * f.rayon) };
  }

  //: Les couleurs des nacelles (celles du dessin d'avant), et qui y est assis : un
  //: rang de `RANGEES`, ou null pour une nacelle vide. ⚠️ Écrit à la main.
  const COULEURS_NACELLES = ['#2f6fb5', '#d98324', '#2f8d6a', '#c0392b', '#9b59b6', '#efd06a'].map(nuances);
  const OCCUPEES = [0, null, 1, 2, null, 3, 0, 2, null, 1, 3, null];

  /** Les couleurs d'une nacelle : sa caisse, et ses deux passagers s'il y en a.
      ⚠️ Gardées, comme celles d'un chariot : un objet neuf par image, c'est un
      `JSON.stringify` de plus par nacelle pour une cuisson déjà faite. */
  function couleursDeNacelle(k, rang, lui) {
    const caisse = COULEURS_NACELLES[k % COULEURS_NACELLES.length];
    if (rang === null) return caisse;
    const cache = (roue.couleurs || (roue.couleurs = {}));
    const cle = rang + (lui ? '|' + JSON.stringify(B.joueur.swaps || null) : '');
    if (!cache[k] || cache[k].cle !== cle) cache[k] = { cle: cle, swaps: Object.assign({}, caisse, passagers(RANGEES[rang], lui)) };
    return cache[k].swaps;
  }

  function peindreNacelles(ctx, cx, cy) {
    const j = B.joueur, fiche = FOIRE_EN_VOLUME.nacelle, vide = FOIRE_EN_VOLUME.nacelle_vide;
    const cap = Vehicules.capDe(Math.PI / 2);
    for (let k = 0; k < roue.n; k++) {
      const a = attache(k), lui = j && j.manege && j.manege.quoi === 'roue' && j.manege.k === k;
      const rang = lui ? 0 : OCCUPEES[k % OCCUPEES.length];
      const couleurs = couleursDeNacelle(k, rang, lui);
      const nom = rang === null ? 'foire_nacelle_vide' : 'foire_nacelle';
      const image = Atlas.cuireCap(nom, rang === null ? vide : fiche, couleurs, Vehicules.ROTATIONS, cap, [0, 0]);
      ctx.drawImage(image, Math.round(a.x - image.width / 2 - cx), Math.round(a.y - image.height / 2 - cy));
      B.stats.images++;
    }
  }

  /** ⚠️ ON NE PASSE PAS À TRAVERS UN WAGON. Appelé à la fin de chaque pas d'un
      piéton (`Entites.bloquerParDecor`) : une boîte orientée par wagon, et on
      ressort par le côté le moins enfoncé — la même règle que le décor. */
  function bloquer(e) {
    if (!train || B.interieur || !PIETONS[e.type] || e.manege) return;
    const b = train.boite;
    if (e.x < b[0] || e.x > b[2] || e.y < b[1] || e.y > b[3]) return;
    const liste = wagons();
    for (let k = 0; k < liste.length; k++) {
      const p = liste[k], m = k === 0 ? LOCO : WAGON;
      const c = Math.cos(p.a), s = Math.sin(p.a), dx = e.x - p.x, dy = e.y - p.y;
      let lx = dx * c + dy * s, ly = -dx * s + dy * c;
      const px = m.l + e.r - Math.abs(lx), py = m.w + e.r - Math.abs(ly);
      if (px <= 0 || py <= 0) continue;
      if (px < py) lx = (lx < 0 ? -1 : 1) * (m.l + e.r);
      else ly = (ly < 0 ? -1 : 1) * (m.w + e.r);
      e.x = p.x + lx * c - ly * s;
      e.y = p.y + lx * s + ly * c;
    }
  }

  // --- La montagne russe --------------------------------------------------------------

  function construireMontagne(d) {
    const v = d.voie, pas = d.pas_px;
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const p of v) {
      x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0]);
      y0 = Math.min(y0, p[1] - p[2]); y1 = Math.max(y1, p[1]);
    }
    const ox = Math.floor(x0) - 24, oy = Math.floor(y0) - 16;
    const z = d.zone;
    return {
      def: d, n: v.length, L: v.length * pas, s: d.gare[1] * pas, v: 0, attente: d.gare_images,
      sGare: d.gare[1] * pas, parcouru: 0, tours: 0, passager: null,
      // Le cap du looping : celui de la voie qui y entre. ⚠️ Dans le looping, la
      // voie avance dans un plan vertical et son cap au sol RETOURNE au sommet —
      // le chariot, lui, garde celui de l'entrée et PENCHE jusqu'à la tête en bas.
      capBoucle: Math.atan2(v[d.boucle[0]][1] - v[d.boucle[0] - 1][1], v[d.boucle[0]][0] - v[d.boucle[0] - 1][0]),
      ox: ox, oy: oy, w: Math.ceil(x1) + 24 - ox, h: Math.ceil(y1) + 24 - oy,
      // ⚠️ DEUX MOITIÉS, triées chacune à sa rangée : l'aller (au sud) passe
      // DEVANT quelqu'un qui marche entre les deux lignes, le retour (au nord)
      // derrière lui.
      ymid: (z.y + z.h / 2) * TT,
      yNord: z.y * TT + 15, ySud: (z.y + z.h - 1) * TT + 15,
    };
  }

  function pointDeMontagne(s) {
    const d = mr.def, v = d.voie, n = mr.n, f = s / d.pas_px;
    const i = ((Math.floor(f) % n) + n) % n, j = (i + 1) % n, t = f - Math.floor(f);
    const a = v[i], b = v[j];
    return { x: a[0] + (b[0] - a[0]) * t, y: a[1] + (b[1] - a[1]) * t, z: a[2] + (b[2] - a[2]) * t, i: i };
  }

  function dans(tranche, i) { return i >= tranche[0] && i <= tranche[1]; }

  /** ⚠️ L'ÉNERGIE, pas un tableau de vitesses : v²/2 + g·z se conserve, moins un
      frottement. Le chariot monte la chaîne au pas, file au creux, ralentit en
      haut du looping — et la même règle le fait rouler partout. La vitesse
      plancher n'est qu'une ceinture : mesuré, il passe le haut du looping bien
      au-dessus d'elle (le juge le tient). */
  function majMontagne() {
    const d = mr.def, pas = d.pas_px;
    if (mr.attente > 0) {
      if (--mr.attente === 0) mr.v = d.depart;
      return;
    }
    const ici = pointDeMontagne(mr.s);
    if (dans(d.chaine, ici.i)) {
      mr.v = d.vitesse_chaine;
    } else {
      const pente = (pointDeMontagne(mr.s + 1).z - pointDeMontagne(mr.s - 1).z) / 2;
      mr.v += -d.gravite * pente - d.frottement * mr.v * mr.v;
      mr.v = Math.max(d.vitesse_min, Math.min(d.vitesse_max, mr.v));
    }
    // Le frein de la gare : on s'approche du point d'arrêt en douceur.
    if (dans(d.gare, ici.i) && mr.s <= mr.sGare) mr.v = Math.min(mr.v, Math.max(0.35, (mr.sGare - mr.s) * 0.06));
    const avant = mr.s;
    mr.s += mr.v;
    mr.parcouru += mr.v;
    if (avant < mr.sGare && mr.s >= mr.sGare) {
      mr.s = mr.sGare; mr.v = 0; mr.attente = d.gare_images; mr.tours++;
    }
    if (mr.s >= mr.L) mr.s -= mr.L;
  }

  // --- La boucle ----------------------------------------------------------------------

  function demarrer() {
    const def = Monde.carte && Monde.carte.def;
    train = def && def.train_de_foire ? construireTrain(def.train_de_foire) : null;
    mr = def && def.montagne_russe ? construireMontagne(def.montagne_russe) : null;
    roue = def && def.roue && typeof DECORS !== 'undefined' && DECORS.grande_roue ? construireRoue(def.roue) : null;
  }

  function maj() {
    if (train) majTrain();
    if (mr) majMontagne();
    // ⚠️ APRÈS les machines : le joueur assis prend la place de son banc de CETTE
    // image, et la caméra (`Monde.majCamera`, plus loin dans la boucle) le suit.
    majPassager();
    laFoireSEntend();
  }

  // --- Ce qu'on entend d'une foire ------------------------------------------------------
  //
  // ⚠️ **UNE FOIRE MUETTE EST UNE PEINTURE** — la fiche du plan l'écrit en
  // majuscules, et c'est le seul morceau de cette vague qui s'entende de
  // l'extérieur de la palissade.

  /** Le milieu de l'enceinte : la source des deux sons. */
  function centre() {
    const f = Monde.carte && Monde.carte.def && Monde.carte.def.foire;
    return f ? { x: (f.x + f.l / 2) * TT, y: (f.y + f.h / 2) * TT, f: f } : null;
  }

  /** L'orgue et les cris, DOSÉS À LA DISTANCE, une fois par image.

      ⚠️ PAS une image sur quinze : le volume suit la distance, et un volume qui
      ne se recalcule que quatre fois par seconde saute par marches quand on
      marche vers la foire. C'est mot pour mot la raison qui sort la musique du
      musicien de rue de `majSortes` (`entites.js`).

      ⚠️ L'orgue passe par `Son.Rue` — « une musique qui sort de QUELQU'UN »,
      avec ici une source FIXE. Il ne prend donc le rang de personne : il joue
      par-dessus l'ambiance du district, et il se tasse tout seul sous une
      poursuite. Les cris, eux, sont une boucle de bruitage, comme la rumeur
      d'un chantier. */
  function laFoireSEntend() {
    const c = centre(), j = B.joueur;
    if (!c || !j || typeof Son === 'undefined') return;
    // ⚠️ Dedans, on n'entend pas la foire : une porte, c'est une porte.
    if (B.interieur) { Son.SFX.rumeur_foire(0); return; }
    const d = Math.hypot(j.x - c.x, j.y - c.y);
    const plein = c.f.orgue_plein_px || 150, portee = c.f.orgue_portee_px || 460;
    if (d < portee) {
      const pres = d <= plein ? 1 : 1 - (d - plein) / (portee - plein);
      Son.Rue.demander(c.f.orgue || 'foire_orgue', pres * (c.f.orgue_volume === undefined ? 0.7 : c.f.orgue_volume));
    }
    const pc = c.f.cris_portee_px || 400;
    Son.SFX.rumeur_foire(d >= pc ? 0 : (1 - d / pc) * (c.f.cris_volume === undefined ? 0.9 : c.f.cris_volume));
  }

  // --- Le dessin ----------------------------------------------------------------------

  //: La caisse de chaque wagon, et ses deux tons (`nuances`, comme un char du trafic).
  const COULEURS_WAGONS = ['#e8a33a', '#d9534a', '#3f7fc4', '#5fb87a'].map(nuances);
  //: Chaque banc, prêt pour `Vehicules.imageDuCavalier` : la selle se tire du banc
  //: comme celle d'un deux-roues (`deuxRoues`), et la posture est celle de la
  //: chaloupe — assis au fond, les mains devant.
  function assises(fiche, longueur) {
    return fiche.machine.bancs.map(function (b) {
      return { u: b[0], def: { selle: [b[1], -b[0] - longueur / 2], posture: 'volant', machine: fiche.machine } };
    });
  }
  let ASSISES = null;

  /** Un wagon (k > 0) ou la locomotive (k = 0) : son ombre orientée, la machine
      cuite au cap, et ceux qui y sont assis — le joueur à sa place s'il y est. */
  function peindreWagon(ctx, p, k, cx, cy) {
    const loco = k === 0, fiche = loco ? FOIRE_EN_VOLUME.loco : FOIRE_EN_VOLUME.wagon;
    const m = loco ? LOCO : WAGON;
    if (!ASSISES) ASSISES = { loco: assises(FOIRE_EN_VOLUME.loco, 20), wagon: assises(FOIRE_EN_VOLUME.wagon, 16) };
    // L'ombre, orientée comme la machine et écrasée comme le sol (`Vehicules.dessinerUn`).
    ctx.save();
    ctx.translate(Math.round(p.x - cx), Math.round(p.y - cy));
    ctx.scale(1, fiche.machine.profondeur);
    ctx.rotate(p.a);
    ctx.fillStyle = 'rgba(20,18,26,0.25)';
    ctx.fillRect(-m.l - 1, -m.w - 1, 2 * m.l + 2, 2 * m.w + 2);
    ctx.restore();
    const swaps = loco ? null : COULEURS_WAGONS[(k - 1) % COULEURS_WAGONS.length];
    const image = Atlas.cuireCap(loco ? 'foire_loco' : 'foire_wagon', fiche, swaps, Vehicules.ROTATIONS, Vehicules.capDe(p.a), [0, 0]);
    ctx.drawImage(image, Math.round(p.x - image.width / 2 - cx), Math.round(p.y - image.height / 2 - cy));
    B.stats.images++;
    // Les gens assis, du banc du fond au banc de devant — de devant, c'est le plus
    // au SUD qui cache l'autre.
    const bancs = loco ? ASSISES.loco : ASSISES.wagon;
    const j = B.joueur, lui = j && j.manege && j.manege.quoi === 'train' && j.manege.k === k;
    const faux = { x: p.x, y: p.y, angle: p.a, def: { longueur: loco ? 20 : 16 } };
    const ordre = bancs.map(function (b, i) { return i; }).sort(function (a, b) {
      return (bancs[a].u - bancs[b].u) * Math.sin(p.a);
    });
    for (const i of ordre) {
      let tenue;
      if (loco) tenue = MACHINISTE;
      else if (lui && i === 0) tenue = j.swaps || {};
      else if (PLACES[(k - 1) % PLACES.length][i] !== null) tenue = VOYAGEURS[PLACES[(k - 1) % PLACES.length][i]];
      else continue;
      const assis = Vehicules.imageDuCavalier(bancs[i].def, faux, tenue);
      if (!assis) continue;
      ctx.drawImage(assis.canvas, Math.round(assis.x - cx), Math.round(assis.y - cy));
      B.stats.images++;
    }
  }

  /** La gare du petit train : une pancarte sur deux poteaux, au bout du quai. */
  function peindreGare(ctx, cx, cy) {
    const q = train.def.quai, TEXTE = 'PETIT TRAIN';
    const large = Atlas.largeurTexte(TEXTE) + 6;
    const x0 = Math.round((q[0] + q[1] + 1) / 2 * TT - large / 2 - cx), y0 = Math.round(q[2] * TT + 2 - cy);
    ctx.fillStyle = '#5e626a';
    ctx.fillRect(x0 + 2, y0 - 16, 1, 17); ctx.fillRect(x0 + large - 3, y0 - 16, 1, 17);
    ctx.fillStyle = '#1b1b1f'; ctx.fillRect(x0, y0 - 22, large, 9);
    ctx.fillStyle = '#2f7d4f'; ctx.fillRect(x0 + 1, y0 - 21, large - 2, 7);
    Atlas.texte(ctx, TEXTE, x0 + 3, y0 - 20, '#ffe58a');
    B.stats.images++;
  }

  /** La structure d'une moitié, cuite UNE fois : l'ombre au sol, la gare, les
      pieds, puis la voie par-dessus. ⚠️ Une montagne russe est un dessin de
      quatre cents points et de vingt-quatre pieds : la repeindre à chaque image
      coûterait des milliers de rectangles ; cuite, c'est une image par moitié. */
  function peindreStructure(g, moitie) {
    const d = mr.def, v = d.voie, n = v.length, ox = mr.ox, oy = mr.oy;
    const ici = function (y) { return (y < mr.ymid) === (moitie === 0); };
    // 1. L'ombre de la voie, au sol : c'est elle qui dit qu'elle est EN L'AIR.
    // ⚠️ Pale : a 20 %, un trait sombre de trois pixels sur le gazon se lisait
    // comme un cable couche par terre.
    g.fillStyle = 'rgba(20,18,26,0.09)';
    for (let i = 0; i < n; i++) {
      const a = v[i], b = v[(i + 1) % n];
      if (!ici(a[1]) || a[2] < 8) continue;
      for (let k = 0; k < 4; k++) {
        g.fillRect(Math.round(a[0] + (b[0] - a[0]) * k / 4 - ox) - 1, Math.round(a[1] + (b[1] - a[1]) * k / 4 - oy) + 1, 3, 2);
      }
    }
    // 2. La gare, au sud : un quai de planches, des poteaux, un auvent rayé
    // AU-DESSUS de la voie, et le nom de la bête.
    if (moitie === 1) {
      const g0 = v[d.gare[0]], g1 = v[d.gare[1]];
      const xa = Math.round(Math.min(g0[0], g1[0]) - ox) - 6, xb = Math.round(Math.max(g0[0], g1[0]) - ox) + 6;
      const yq = Math.round(g0[1] - oy);
      g.fillStyle = '#7a5a3a'; g.fillRect(xa, yq + 3, xb - xa, 9);
      g.fillStyle = '#8f6c47';
      for (let x = xa; x < xb; x += 4) g.fillRect(x, yq + 4, 3, 7);
      g.fillStyle = '#5e626a';
      for (const x of [xa + 1, xb - 2]) { g.fillRect(x, yq - 26, 2, 36); }
      for (let x = xa - 2; x < xb + 2; x++) {
        g.fillStyle = (Math.floor((x - xa) / 4) % 2) ? '#efe6d0' : '#c0392b';
        g.fillRect(x, yq - 32, 1, 8);
      }
      g.fillStyle = '#1b1b1f'; g.fillRect(xa + 6, yq - 45, 44, 11);
      g.fillStyle = '#ffe58a'; g.fillRect(xa + 7, yq - 44, 42, 1); g.fillRect(xa + 7, yq - 36, 42, 1);
      Atlas.texte(g, 'LE COLOSSE', xa + 9, yq - 42, '#ffe58a');
      g.fillStyle = '#5e626a'; g.fillRect(xa + 10, yq - 34, 1, 2); g.fillRect(xa + 45, yq - 34, 1, 2);
    }
    // 3. Les pieds : deux TUBES d'acier blanc qui se rejoignent sous la voie, et
    // une entretoise de loin en loin. ⚠️ Le premier dessin les croisillonnait
    // serre, et vu d'en haut une foret de treillis se lit comme une ligne a
    // haute tension — pas comme une montagne russe.
    for (const s of d.supports) {
      const p = v[s[0]], fx = s[1] * TT + 8, fy = s[2] * TT + 12;
      if (!ici(fy)) continue;
      const haut = p[1] - p[2], hauteur = fy - haut;
      const base = 1 + Math.min(4, Math.floor(hauteur / 30));
      g.fillStyle = '#7b7f86'; g.fillRect(fx - base - 2 - ox, fy - 1 - oy, 2 * base + 5, 3);
      for (let y = fy - 1; y > haut + 2; y--) {
        const t = (fy - y) / hauteur, demi = base * (1 - t) + 0.5 * t, xx = fx + (p[0] - fx) * t;
        const xg = Math.round(xx - demi - ox), xd = Math.round(xx + demi - ox);
        g.fillStyle = '#f1efe8'; g.fillRect(xg, y - oy, 1, 1);
        g.fillStyle = '#b9bcc1'; g.fillRect(xd, y - oy, 1, 1);
        if ((fy - y) % 18 === 9 && xd - xg > 1) { g.fillStyle = '#d6d5cf'; g.fillRect(xg, y - oy, xd - xg, 1); }
      }
    }
    // 4. La voie : un longeron sombre, deux rails rouges, une traverse sur deux
    // points et une ampoule sur quatre.
    for (let i = 0; i < n; i++) {
      const a = v[i], b = v[(i + 1) % n];
      if (!ici((a[1] + b[1]) / 2)) continue;
      let nx = -(b[1] - a[1]), ny = b[0] - a[0];
      const l = Math.hypot(nx, ny);
      // ⚠️ Dans le looping la voie avance dans le plan x-z : les rails s'y
      // écartent en y, toujours du même côté (sinon ils se croisent au sommet).
      if (Math.abs(b[1] - a[1]) < 0.2 || l < 0.3) { nx = 0; ny = 1; } else { nx /= l; ny /= l; }
      for (let k = 0; k < 4; k++) {
        const t = k / 4;
        const sx = a[0] + (b[0] - a[0]) * t - ox, sy = a[1] + (b[1] - a[1]) * t - (a[2] + (b[2] - a[2]) * t) - oy;
        g.fillStyle = '#6e1d17'; g.fillRect(Math.round(sx), Math.round(sy + 2), 1, 2);
        g.fillStyle = '#c0392b'; g.fillRect(Math.round(sx + nx * 2), Math.round(sy + ny * 2), 1, 1);
        g.fillStyle = '#e8604e'; g.fillRect(Math.round(sx - nx * 2), Math.round(sy - ny * 2), 1, 1);
      }
      const sx = a[0] - ox, sy = a[1] - a[2] - oy;
      if (i % 2 === 0) {
        g.fillStyle = '#3a2a22';
        for (let k = -1; k <= 1; k++) g.fillRect(Math.round(sx + nx * k), Math.round(sy + ny * k), 1, 1);
      }
      if (i % 4 === 0) { g.fillStyle = '#ffe58a'; g.fillRect(Math.round(sx + nx * 3), Math.round(sy + ny * 3), 1, 1); }
    }
  }

  //: Un cran de tangage sur 32, comme le cap (`Atlas.cuireCap`).
  function cranDeTangage(a) { const n = Vehicules.ROTATIONS; return ((Math.round(a / (Math.PI * 2) * n) % n) + n) % n; }

  /** Le cap et le tangage d'un chariot à l'abscisse `s` : la voie vue en 3D. */
  function allureDuChariot(s) {
    const d = mr.def, p = pointDeMontagne(s), av = pointDeMontagne(s + 2), ar = pointDeMontagne(s - 2);
    const dx = av.x - ar.x, dy = av.y - ar.y, dz = av.z - ar.z;
    if (dans(d.boucle, p.i)) {
      const c = mr.capBoucle;
      return { p: p, cap: c, tangage: Math.atan2(dz, dx * Math.cos(c) + dy * Math.sin(c)) };
    }
    return { p: p, cap: Math.atan2(dy, dx), tangage: Math.atan2(dz, Math.hypot(dx, dy)) };
  }

  //: Qui est assis dans chaque chariot : deux passants, gauche et droite (`VOYAGEURS`).
  const RANGEES = [[0, 1], [2, 3], [4, 5], [1, 2]];

  /** Les lettres de deux passagers côte à côte (`a` `b` `g` à gauche, `d` `e` `f`
      à droite, voir `chariotDeMontagne`) — le joueur à gauche quand c'est lui. */
  function passagers(rang, lui) {
    const g = lui ? Object.assign({}, SPRITES.joueur.pal, B.joueur.swaps || {}) : VOYAGEURS[rang[0]];
    const dr = VOYAGEURS[rang[1]];
    return { a: g.c, b: g.h, g: g.s, d: dr.c, e: dr.h, f: dr.s };
  }

  /** Les couleurs d'un chariot : ses deux passagers. ⚠️ Un seul objet par chariot,
      gardé : l'atlas range ses cuissons par couleurs (`JSON.stringify`). */
  function couleursDuChariot(k) {
    const j = B.joueur, lui = !!(j && j.manege && j.manege.quoi === 'montagne' && j.manege.k === k);
    const cache = (mr.couleurs || (mr.couleurs = {}));
    const cle = lui ? JSON.stringify(j.swaps || null) : '';
    if (!cache[k] || cache[k].cle !== cle) cache[k] = { cle: cle, swaps: passagers(RANGEES[k % RANGEES.length], lui) };
    return cache[k].swaps;
  }

  function peindreChariots(ctx, moitie, cx, cy) {
    const d = mr.def;
    for (let k = 0; k < d.chariots; k++) {
      const s = mr.s - k * d.ecart_px, al = allureDuChariot(s), p = al.p;
      if ((p.y < mr.ymid) !== (moitie === 0)) continue;
      // Les bras se lèvent quand ça PLONGE, et tout le long du looping.
      const av = pointDeMontagne(s + 2), ar = pointDeMontagne(s - 2);
      const bras = (av.z - ar.z) < -1.2 || dans(d.boucle, p.i);
      const fiche = bras ? FOIRE_EN_VOLUME.chariot_bras : FOIRE_EN_VOLUME.chariot;
      if (p.z > 8) {
        ctx.fillStyle = 'rgba(20,18,26,0.22)';
        ctx.fillRect(Math.round(p.x - 6 - cx), Math.round(p.y + 1 - cy), 12, 3);
      }
      const image = Atlas.cuireCap(bras ? 'foire_chariot_bras' : 'foire_chariot', fiche, couleursDuChariot(k),
                                   Vehicules.ROTATIONS, Vehicules.capDe(al.cap), [0, 0], cranDeTangage(al.tangage));
      ctx.drawImage(image, Math.round(p.x - image.width / 2 - cx), Math.round(p.y - p.z - image.height / 2 - cy));
      B.stats.images++;
    }
  }

  function peindreMoitie(ctx, moitie, cx, cy) {
    const image = Atlas.cuirePeintre('foire|montagne|' + moitie, mr.w, mr.h, function (g) { peindreStructure(g, moitie); });
    ctx.drawImage(image, mr.ox - cx, mr.oy - cy);
    B.stats.images++;
    peindreChariots(ctx, moitie, cx, cy);
  }

  /** Ce qui se trie avec les entités, s'il est à l'écran. ⚠️ La montagne russe
      se juge à sa BOÎTE ENTIÈRE, pas à son pied : son sommet dépasse de neuf
      tuiles au-dessus de sa rangée, et le tri des entités (40 px de marge)
      l'aurait effacée dès que son pied sort du bas de l'écran. */
  function ajouterVisibles(visibles, cx, cy) {
    if (mr && mr.ox < cx + VW && mr.ox + mr.w > cx && mr.oy < cy + VH && mr.oy + mr.h > cy) {
      visibles.push({ id: ID_TRI, vivant: true, x: mr.ox, y: mr.yNord, peindreFoire: function (ctx) { peindreMoitie(ctx, 0, cx, cy); } });
      visibles.push({ id: ID_TRI + 1, vivant: true, x: mr.ox, y: mr.ySud, peindreFoire: function (ctx) { peindreMoitie(ctx, 1, cx, cy); } });
    }
    if (roue) {
      const f = roue.f, x0 = roue.x - f.ancre[0], y0 = roue.y - f.ancre[1];
      if (x0 < cx + VW && x0 + f.w > cx && y0 < cy + VH && y0 + f.h + 12 > cy) {
        // ⚠️ Un cheveu plus au sud que la roue : ses nacelles pendent DEVANT ses rayons.
        visibles.push({ id: ID_TRI + 60, vivant: true, x: roue.x, y: roue.y + 0.5, peindreFoire: function (ctx) { peindreNacelles(ctx, cx, cy); } });
      }
    }
    if (train) {
      const q = train.def.quai;
      if (q) {
        const gx = (q[0] + q[1] + 1) / 2 * TT, gy = q[2] * TT + 2;
        if (gx > cx - 40 && gx < cx + VW + 40 && gy > cy - 8 && gy < cy + VH + 30) {
          // ⚠️ Un numéro à part des wagons (`+ 2 + k`), et au-delà des deux moitiés
          // de la montagne : un juge compte celles-ci par `id < ID_TRI + 2`.
          visibles.push({ id: ID_TRI + 50, vivant: true, x: gx, y: gy, peindreFoire: function (ctx) { peindreGare(ctx, cx, cy); } });
        }
      }
      const liste = wagons();
      liste.forEach(function (p, k) {
        if (p.x < cx - 16 || p.x > cx + VW + 16 || p.y < cy - 16 || p.y > cy + VH + 16) return;
        visibles.push({ id: ID_TRI + 2 + k, vivant: true, x: p.x, y: p.y + 4,
                        peindreFoire: function (ctx) { peindreWagon(ctx, p, k, cx, cy); } });
      });
    }
  }

  return {
    demarrer, maj, bloquer, ajouterVisibles, wagons, pointDuTrain, pointDeMontagne,
    sousLaMain, inviteMonter, monter, descendre,
    jeux, comptoirs, jeuSousLaMain, kiosqueDuJeu, cibles, centre, PORTEE_JEU,
    MACHINES: FOIRE_EN_VOLUME,
    get train() { return train; }, get montagne() { return mr; }, get roue() { return roue; }, attache,
  };
})();
