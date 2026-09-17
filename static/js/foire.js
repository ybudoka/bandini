/* Bandini — la foire qui roule : le petit train et la montagne russe.

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
   derrière, selon sa rangée. */

const Foire = (function () {
  'use strict';

  //: Ce qui arrête le train : quelqu'un de debout sur la voie, ou un char.
  const CORPS = { joueur: 1, pieton: 1, agent: 1, vehicule: 1 };
  //: Ce qu'un wagon repousse : les gens à pied (un char a sa propre physique).
  const PIETONS = { joueur: 1, pieton: 1, agent: 1 };
  //: Les demi-mesures d'un wagon, vu d'en haut : la locomotive est plus longue.
  const LOCO = { l: 7, w: 5 };
  const WAGON = { l: 6, w: 5 };
  //: Un numéro de tri hors de portée de celui des entités (`creer` compte de 1).
  const ID_TRI = 900000000;

  let train = null;
  let mr = null;

  // --- Le petit train -----------------------------------------------------------------

  /** La voie en pixels, un point par pixel de rail : droit au milieu d'une tuile,
      un quart de cercle de rayon 8 autour du COIN dans une courbe — la même
      courbe que peint la tuile (`TUILES.T`). */
  function construireTrain(d) {
    const tuiles = d.voie, n = tuiles.length, xs = [], ys = [];
    for (let i = 0; i < n; i++) {
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
             boite: [x0 - 16, y0 - 16, x1 + 16, y1 + 16] };
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

  function majTrain() {
    const d = train.def;
    if (train.sifflet > 0) train.sifflet--;
    const devant = quelquUnDevant();
    train.bloque = !!devant;
    if (devant) {
      train.v = 0;
      // Il siffle, et il resiffle tant qu'on reste planté là.
      if (train.sifflet <= 0) {
        train.sifflet = d.sifflet_images;
        const j = B.joueur, loco = pointDuTrain(train.s);
        if (j && dist2(j.x, j.y, loco.x, loco.y) < 260 * 260) Son.SFX.sifflet_train();
      }
    } else {
      train.v = Math.min(d.vitesse, train.v + d.reprise);
    }
    train.s = (train.s + train.v) % train.n;
  }

  /** ⚠️ ON NE PASSE PAS À TRAVERS UN WAGON. Appelé à la fin de chaque pas d'un
      piéton (`Entites.bloquerParDecor`) : une boîte orientée par wagon, et on
      ressort par le côté le moins enfoncé — la même règle que le décor. */
  function bloquer(e) {
    if (!train || B.interieur || !PIETONS[e.type]) return;
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
      sGare: d.gare[1] * pas, parcouru: 0, tours: 0,
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
  }

  function maj() {
    if (train) majTrain();
    if (mr) majMontagne();
  }

  // --- Le dessin ----------------------------------------------------------------------

  //: Vu d'en haut, le nez vers l'est (+x) : la rotation se fait à la cuisson.
  const GRILLE_LOCO = [
    '.kkkkk.........',
    'kRRRRRkkkkkkkk.',
    'kRrrrRkgGgggGgk',
    'kRrrrRkgGgcgGgky',
    'kRrrrRkgGgcgGgky',
    'kRrrrRkgGgggGgk',
    'kRRRRRkkkkkkkk.',
    '.kkkkk.........',
  ];
  const GRILLE_WAGON = [
    '.kkkkkkkkkk.',
    'kccccccccccK',
    'kcsh1scsh2ck',
    'kcsh1scsh2ck',
    'kccccccccccK',
    '.kkkkkkkkkk.',
  ];
  //: Un chariot de montagne russe : deux rangées, deux têtes, et des bras levés
  //: quand ça plonge (la variante `bras`).
  const GRILLE_CHARIOT = [
    '..kkkkkkkk.',
    '.krrrrrrrrk',
    'krh1rh2rrrk',
    'krh1rh2rrrk',
    '.krrrrrrrrk',
    '..kkkkkkkk.',
  ];
  const GRILLE_CHARIOT_BRAS = [
    '..kakkkakk.',
    '.krrrrrrrrk',
    'krh1rh2rrrk',
    'krh1rh2rrrk',
    '.krrrrrrrrk',
    '..kakkkakk.',
  ];
  const PALETTE = {
    k: '#2a1a14', K: '#1b1210', R: '#b3342a', r: '#d9534a', g: '#2f7d4f', G: '#e2b33c',
    c: '#3f7fc4', y: '#f2d34f', s: '#6b4a2e', h: '#f0c9a0', a: '#f0c9a0',
    '1': '#3b2a20', '2': '#d8b36a',
  };
  const COULEURS_WAGONS = ['#e8a33a', '#d9534a', '#3f7fc4', '#5fb87a'];
  const CHEVEUX = [['#3b2a20', '#d8b36a'], ['#1b1b1f', '#a0522d'], ['#d8b36a', '#3b2a20'], ['#7a4a2a', '#1b1b1f']];

  /** Une grille tournée à `cap` seizièmes de tour, cuite une fois : rotation au
      plus proche voisin, sans flou et sans trou (on part de chaque pixel
      d'ARRIVÉE et on remonte à la grille). */
  function tournee(cle, grille, pal, cap) {
    const h = grille.length, w = grille[0].length;
    const cote = Math.ceil(Math.hypot(w, h)) + 2;
    return Atlas.cuirePeintre(cle + '|' + cap, cote, cote, function (g) {
      const a = cap * Math.PI / 8, c = Math.cos(a), s = Math.sin(a), m = cote / 2;
      for (let y = 0; y < cote; y++) {
        for (let x = 0; x < cote; x++) {
          const dx = x + 0.5 - m, dy = y + 0.5 - m;
          const gx = Math.floor(dx * c + dy * s + w / 2), gy = Math.floor(-dx * s + dy * c + h / 2);
          if (gy < 0 || gy >= h || gx < 0 || gx >= grille[gy].length) continue;
          const ch = grille[gy][gx];
          if (ch === '.' || !pal[ch]) continue;
          g.fillStyle = pal[ch];
          g.fillRect(x, y, 1, 1);
        }
      }
    });
  }

  function capDe(a) { return ((Math.round(a / (Math.PI / 8)) % 16) + 16) % 16; }

  function peindreWagon(ctx, p, k, cx, cy) {
    ctx.fillStyle = 'rgba(20,18,26,0.25)';
    ctx.fillRect(Math.round(p.x - 6 - cx), Math.round(p.y + 2 - cy), 12, 4);
    const cap = capDe(p.a);
    let image;
    if (k === 0) {
      image = tournee('foire|loco', GRILLE_LOCO, PALETTE, cap);
    } else {
      const pal = Object.assign({}, PALETTE, {
        c: COULEURS_WAGONS[(k - 1) % COULEURS_WAGONS.length],
        '1': CHEVEUX[(k - 1) % CHEVEUX.length][0], '2': CHEVEUX[(k - 1) % CHEVEUX.length][1],
      });
      image = tournee('foire|wagon' + ((k - 1) % COULEURS_WAGONS.length), GRILLE_WAGON, pal, cap);
    }
    ctx.drawImage(image, Math.round(p.x - image.width / 2 - cx), Math.round(p.y - image.height / 2 - 1 - cy));
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

  function peindreChariots(ctx, moitie, cx, cy) {
    const d = mr.def;
    for (let k = 0; k < d.chariots; k++) {
      const s = mr.s - k * d.ecart_px, p = pointDeMontagne(s);
      if ((p.y < mr.ymid) !== (moitie === 0)) continue;
      const av = pointDeMontagne(s + 2), ar = pointDeMontagne(s - 2);
      const a = Math.atan2((av.y - av.z) - (ar.y - ar.z), av.x - ar.x);
      // Les bras se lèvent quand ça PLONGE, et tout le long du looping.
      const bras = (av.z - ar.z) < -1.2 || dans(d.boucle, p.i);
      const pal = Object.assign({}, PALETTE, { '1': CHEVEUX[k % 4][0], '2': CHEVEUX[k % 4][1] });
      const image = tournee('foire|chariot' + k + (bras ? 'b' : ''), bras ? GRILLE_CHARIOT_BRAS : GRILLE_CHARIOT, pal, capDe(a));
      if (p.z > 8) {
        ctx.fillStyle = 'rgba(20,18,26,0.22)';
        ctx.fillRect(Math.round(p.x - 4 - cx), Math.round(p.y + 1 - cy), 8, 3);
      }
      ctx.drawImage(image, Math.round(p.x - image.width / 2 - cx), Math.round(p.y - p.z - image.height / 2 - 1 - cy));
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
    if (train) {
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
    get train() { return train; }, get montagne() { return mr; },
  };
})();
