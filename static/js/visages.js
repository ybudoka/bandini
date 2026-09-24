/* Bandini — les visages des dialogues : le portrait de qui parle, a gauche de la boite.

   Demande de Martin (22 sept. 2026) : « je veux des visages dessines pour chaque dialogue ».

   Python decide (`app/visages.py` : quels traits, quelle humeur), ce fichier DESSINE. Un
   portrait fait 40 x 40, peint en lettres de palette sur une grille — comme les sprites —
   puis cuit une fois par (personnage, humeur, bouche, clin) : un dialogue ne repeint rien.

   La grille : l'axe du visage passe ENTRE x = 19 et x = 20 (le miroir de x est 39 - x). La
   tete va des rangees 7 a 30 ; les yeux sont a la rangee 18, la bouche a la 25, les epaules
   commencent a la 31. Les couleurs sont celles que le personnage a deja dans la rue (`c`
   chandail, `h` cheveux, `s` peau) : le portrait et le bonhomme de seize pixels sont la
   meme personne. */

const Visages = (function () {
  'use strict';

  const TAILLE = 40;

  //: Demi-largeur de la tete, rangee par rangee, de y = 7 (le haut du crane) a y = 30 (le menton).
  const TETES = {
    ronde:  [5, 7, 8, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 8, 8, 7, 6, 4],
    carree: [6, 8, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 8, 7, 6],
    longue: [5, 6, 7, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 8, 8, 8, 7, 7, 6, 5],
    fine:   [5, 7, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 8, 8, 7, 7, 6, 5, 4, 3],
    large:  [6, 8, 9, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 9, 8, 6],
  };
  const HAUT = 7, MENTON = 30;

  const HUMEURS = ['neutre', 'content', 'rire', 'fache', 'serieux', 'triste', 'inquiet', 'surpris', 'malin', 'froid'];

  // ---------------------------------------------------------------- couleurs

  function rgb(hex) {
    const n = parseInt(hex.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  function hex(c) {
    return '#' + c.map(function (v) { return Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0'); }).join('');
  }
  function melange(a, b, t) {
    const x = rgb(a), y = rgb(b);
    return hex([0, 1, 2].map(function (i) { return x[i] + (y[i] - x[i]) * t; }));
  }
  function sombre(a, f) { return melange(a, '#000000', 1 - f); }
  function clair(a, t) { return melange(a, '#ffffff', t); }

  /** La palette d'un visage : ses trois couleurs de rue, et ce qu'on en tire. */
  function palette(v) {
    const c = v.couleurs || {}, x = v.extra || {};
    const s = c.s || '#e8b088', h = c.h || '#3a2a1a', ch = c.c || '#7f8c8d';
    const b = x.b || h, t = x.t || sombre(ch, 0.6);
    return {
      k: '#101018',
      s: s, S: sombre(s, 0.8), Q: clair(s, 0.35), r: melange(s, '#d04040', 0.35),
      u: melange(s, h, 0.3), F: melange(s, '#8a3a1a', 0.45), z: melange(s, '#8a3a3a', 0.4),
      h: h, H: sombre(h, 0.7), g: clair(h, 0.3),
      b: b, B: sombre(b, 0.72),
      c: ch, C: sombre(ch, 0.72), q: clair(ch, 0.25),
      t: t, T: sombre(t, 0.7),
      w: '#efe6d0', W: '#fbf7ee', y: x.y || '#3a2414', V: '#b8c4d0',
      m: '#6a2020', l: x.l || '#b0283a', d: '#f4ecdc',
      o: '#e8b33c', a: '#b8c0c8', e: '#1a1a22', R: '#c0392b', i: '#6a8ab0',
      x: '#f0ead8', f: '#ff6a2a', j: '#d8c890',
    };
  }

  // ---------------------------------------------------------------- la grille

  function Grille() {
    const g = [];
    for (let y = 0; y < TAILLE; y++) g.push(new Array(TAILLE).fill('.'));
    this.g = g;
  }
  Grille.prototype.pose = function (x, y, ch) {
    if (x >= 0 && y >= 0 && x < TAILLE && y < TAILLE) this.g[y][x] = ch;
  };
  Grille.prototype.lit = function (x, y) {
    return (x >= 0 && y >= 0 && x < TAILLE && y < TAILLE) ? this.g[y][x] : '.';
  };
  /** Pose (x, y) et son miroir (39 - x, y). */
  Grille.prototype.deux = function (x, y, ch) { this.pose(x, y, ch); this.pose(TAILLE - 1 - x, y, ch); };
  Grille.prototype.rang = function (y, x0, x1, ch) { for (let x = x0; x <= x1; x++) this.pose(x, y, ch); };
  Grille.prototype.bloc = function (x0, y0, x1, y1, ch) { for (let y = y0; y <= y1; y++) this.rang(y, x0, x1, ch); };
  /** Une rangee centree de demi-largeur `hw` : de 20 - hw a 19 + hw. */
  Grille.prototype.centre = function (y, hw, ch) { this.rang(y, 20 - hw, 19 + hw, ch); };
  /** Des motifs en chaines : `'..kk'` pose a partir de (x, y), les points sautent. Avec
      `miroir`, la meme chose de l'autre cote de l'axe, retournee. */
  Grille.prototype.motif = function (x, y, lignes, miroir) {
    const self = this;
    lignes.forEach(function (l, dy) {
      for (let i = 0; i < l.length; i++) {
        if (l[i] === '.') continue;
        self.pose(x + i, y + dy, l[i]);
        if (miroir) self.pose(TAILLE - 1 - (x + i), y + dy, l[i]);
      }
    });
  };
  /** Remplace les cases `de` par `vers` (ou toutes, si `de` est null) dans un rectangle. */
  Grille.prototype.teint = function (x0, y0, x1, y1, de, vers, garde) {
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
      const v = this.lit(x, y);
      if (v === '.' || (de && de.indexOf(v) < 0)) continue;
      if (garde && !garde(x, y)) continue;
      this.pose(x, y, vers);
    }
  };

  /** Un petit de fixe (sans `Math.random` : le meme portrait a chaque cuisson). */
  function bruit(x, y, graine) {
    let n = (x * 374761393 + y * 668265263 + graine * 2147483647) | 0;
    n = (n ^ (n >>> 13)) * 1274126177 | 0;
    return ((n ^ (n >>> 16)) >>> 0) % 100;
  }
  function graineDe(slug) {
    let n = 7;
    for (let i = 0; i < slug.length; i++) n = (n * 31 + slug.charCodeAt(i)) | 0;
    return Math.abs(n) % 997;
  }

  // ---------------------------------------------------------------- la tete

  function demi(forme, y) {
    const t = TETES[forme] || TETES.ronde;
    return (y < HAUT || y > MENTON) ? 0 : t[y - HAUT];
  }

  function peindreTete(G, v) {
    for (let y = HAUT; y <= MENTON; y++) G.centre(y, demi(v.tete, y), 's');
    // Les oreilles, de la rangee 16 a 21 : un pixel de plus de chaque cote.
    for (let y = 16; y <= 21; y++) {
      const hw = demi(v.tete, y);
      G.deux(19 - hw, y, y === 16 || y === 21 ? 'S' : 's');
    }
    G.deux(19 - demi(v.tete, 18), 18, 'S');
    // La lumiere vient de la gauche : le bord droit de chaque rangee est dans l'ombre.
    for (let y = HAUT + 2; y <= MENTON; y++) {
      const hw = demi(v.tete, y);
      G.pose(19 + hw, y, 'S');
      if (y > 22) G.pose(18 + hw, y, 'S');
    }
    // Le cou : sous le menton, dans l'ombre de la machoire.
    G.bloc(17, MENTON + 1, 22, 33, 's');
    G.rang(MENTON + 1, 17, 22, 'S');
    G.bloc(21, MENTON + 1, 22, 33, 'S');
  }

  // ---------------------------------------------------------------- l'habit

  //: Les epaules : demi-largeur a partir de la rangee 31.
  const EPAULES = [7, 10, 13, 15, 16, 16, 16, 16, 16];

  function peindreHabit(G, v, sig) {
    for (let i = 0; i < EPAULES.length; i++) G.centre(31 + i, EPAULES[i], 'c');
    // L'ombre du cote droit, et les plis des bras.
    for (let i = 0; i < EPAULES.length; i++) {
      const hw = EPAULES[i];
      G.pose(19 + hw, 31 + i, 'C');
      if (hw > 12) G.pose(18 + hw, 31 + i, 'C');
    }
    G.teint(0, 35, 39, 39, 'c', 'C', function (x) { return x === 9 || x === 30; });
    const h = v.habit;
    if (h === 'chandail') {
      G.rang(31, 16, 23, 'C'); G.rang(32, 16, 17, 'C'); G.rang(32, 22, 23, 'C');
      G.bloc(17, 31, 22, 31, 'S');
    } else if (h === 'col_roule') {
      G.bloc(16, 31, 23, 33, 'c');
      G.rang(32, 16, 23, 'C'); G.bloc(22, 31, 23, 33, 'C');
    } else if (h === 'gilet') {
      G.bloc(18, 32, 21, 39, 'w'); G.rang(31, 17, 22, 'w');
      G.bloc(20, 32, 21, 39, 'V');
      G.teint(16, 32, 17, 39, 'cC', 'C'); G.teint(22, 32, 23, 39, 'cC', 'C');
      [34, 36, 38].forEach(function (y) { G.pose(17, y, 'q'); });
    } else if (h === 'veston' || h === 'sarrau') {
      // Les revers : un V de chemise, bordé du pli du revers.
      const chemise = h === 'sarrau' ? 'i' : 'w';
      [[31, 16, 23], [32, 17, 22], [33, 17, 22], [34, 18, 21], [35, 18, 21], [36, 19, 20], [37, 19, 20]].forEach(function (r) {
        G.rang(r[0], r[1], r[2], chemise);
        G.pose(r[1] - 1, r[0], 'C'); G.pose(r[2] + 1, r[0], 'C');
      });
      if (sig.noeud_pap) {
        G.motif(17, 31, ['RRkkRR', '.RRRR.']);
      } else {
        G.bloc(19, 31, 20, 36, h === 'sarrau' ? 'k' : 'R');
        G.rang(31, 19, 20, 'k');
      }
      if (h === 'sarrau') { G.bloc(26, 35, 29, 35, 'C'); G.pose(27, 34, 'a'); G.pose(28, 34, 'R'); }
    } else if (h === 'chemise_police' || h === 'uniforme') {
      // Le col en pointes, la patte de boutons, les rabats de poches, les epaulettes.
      G.motif(15, 31, ['qqq', '.qq', '..q']);
      G.motif(22, 31, ['qqq', 'qq.', 'q..']);
      G.bloc(18, 31, 21, 31, h === 'chemise_police' ? 'k' : 'S');
      for (let y = 33; y <= 39; y++) G.pose(19, y, 'C');
      [34, 37].forEach(function (y) { G.pose(20, y, 'q'); });
      G.rang(35, 11, 15, 'C'); G.rang(35, 24, 28, 'C');
      G.rang(33, 7, 10, 'C'); G.rang(33, 29, 32, 'C');
      if (h === 'uniforme') G.rang(36, 12, 14, 'w');
      if (sig.insigne) G.motif(25, 34, ['.o.', 'ooo', '.o.']);
    } else if (h === 'tablier') {
      G.rang(31, 16, 23, 'C');
      G.bloc(12, 34, 27, 39, 'W'); G.rang(34, 12, 27, 'w');
      G.bloc(14, 31, 14, 33, 'W'); G.bloc(25, 31, 25, 33, 'W');
      G.teint(26, 34, 27, 39, 'W', 'w');
    } else if (h === 'blouse') {
      // Le col en V : la peau descend jusqu'a la rangee 34.
      [[31, 17, 22], [32, 18, 21], [33, 18, 21], [34, 19, 20]].forEach(function (r) {
        G.rang(r[0], r[1], r[2], 's');
        G.pose(r[1] - 1, r[0], 'C'); G.pose(r[2] + 1, r[0], 'C');
      });
      G.pose(21, 32, 'S'); G.pose(21, 33, 'S');
    } else if (h === 'veste') {
      // Le col monte, la fermeture eclair, une poche.
      G.bloc(14, 31, 16, 33, 'C'); G.bloc(23, 31, 25, 33, 'C');
      G.bloc(15, 31, 15, 32, 'c'); G.bloc(24, 31, 24, 32, 'c');
      for (let y = 32; y <= 39; y++) G.pose(19, y, 'a');
      G.rang(36, 23, 27, 'C');
    }
    if (sig.stetho) {
      for (let y = 30; y <= 35; y++) { G.pose(16, y, 'a'); G.pose(23, y, 'a'); }
      G.rang(36, 17, 22, 'a'); G.motif(23, 36, ['aa', 'aa']);
    }
  }

  // ---------------------------------------------------------------- les cheveux

  /** Le casque de cheveux au-dessus du front : de `y0` a `frange` (inclus), deborde de `plus`. */
  function calotte(G, v, y0, frange, plus) {
    for (let y = y0; y <= frange; y++) {
      const hw = y < HAUT ? Math.max(demi(v.tete, HAUT) - (HAUT - y) * 2, 2) : demi(v.tete, y) + plus;
      G.centre(y, hw, 'h');
    }
  }
  /** Les tempes : les deux colonnes du bord, de `y0` a `y1`. */
  function tempes(G, v, y0, y1, large) {
    for (let y = y0; y <= y1; y++) {
      const hw = demi(v.tete, y);
      for (let k = 0; k < (large || 1); k++) G.deux(20 - hw + k, y, 'h');
    }
  }

  function arriereCheveux(G, v, graine) {
    const c = v.coiffure;
    if (c === 'longue') {
      for (let y = 8; y <= 37; y++) {
        const hw = Math.max(demi(v.tete, Math.min(y, 24)) + 3, 11);
        const w = y > 30 ? 4 - Math.min(2, (y - 31) >> 1) : hw;
        if (y > 30) { G.rang(y, 20 - hw, 20 - hw + w, 'h'); G.rang(y, 19 + hw - w, 19 + hw, 'h'); } else G.centre(y, hw, 'h');
      }
    } else if (c === 'carre') {
      for (let y = 8; y <= 28; y++) G.centre(y, Math.max(demi(v.tete, Math.min(y, 22)) + 2, 10), 'h');
      G.centre(28, 11, 'H');
    } else if (c === 'permanente') {
      for (let y = 3; y <= 25; y++) {
        const hw = y < 7 ? 7 + (y - 3) : (y > 21 ? 13 - (y - 21) : 13);
        for (let x = 20 - hw; x <= 19 + hw; x++) {
          if ((x === 20 - hw || x === 19 + hw) && bruit(x, y, graine) < 40) continue;
          G.pose(x, y, bruit(x, y, graine + 1) < 30 ? 'H' : 'h');
        }
      }
    } else if (c === 'hirsute') {
      for (let y = 5; y <= 27; y++) {
        const hw = demi(v.tete, Math.min(Math.max(y, HAUT), 24)) + 2 + (bruit(0, y, graine) % 2);
        G.centre(y, hw, bruit(1, y, graine) < 25 ? 'H' : 'h');
      }
    } else if (c === 'queue') {
      G.bloc(29, 10, 31, 12, 'h');
      for (let y = 12; y <= 27; y++) G.rang(y, 30 + (y > 20 ? 1 : 0), 32 + (y > 20 ? 1 : 0) - (y > 25 ? 1 : 0), y % 4 === 0 ? 'H' : 'h');
      G.rang(12, 29, 31, 'R');
    } else if (c === 'chignon') {
      G.motif(15, 1, ['..hhhhhh..', '.hhhhgghh.', 'hhhhhhhhhh', 'hhhHhhhhHh', '.hhHhhHhh.', '..hhhhhh..']);
    }
  }

  function devantCheveux(G, v, graine) {
    const c = v.coiffure, hw = function (y) { return demi(v.tete, y); };
    if (c === 'courte') {
      calotte(G, v, 5, 11, 1);
      for (let x = 20 - hw(12); x <= 19 + hw(12); x++) if (bruit(x, 12, graine) < 55) G.pose(x, 12, 'h');
      tempes(G, v, 12, 17, 2);
    } else if (c === 'brosse') {
      G.bloc(20 - hw(9), 5, 19 + hw(9), 11, 'h');
      for (let x = 20 - hw(9); x <= 19 + hw(9); x += 2) G.pose(x, 5, 'H');
      tempes(G, v, 12, 16, 1);
    } else if (c === 'degarnie') {
      tempes(G, v, 11, 19, 2);
      for (let y = 9; y <= 11; y++) G.deux(20 - hw(y), y, 'h');
      G.motif(15, 9, ['QQ', 'Q.']);
    } else if (c === 'chauve') {
      G.motif(14, 8, ['QQQ', 'QQ.', 'Q..']);
      tempes(G, v, 15, 19, 1);
    } else if (c === 'gominee') {
      calotte(G, v, 5, 10, 1);
      G.rang(11, 20 - hw(11), 19 + hw(11), 'h');
      G.rang(11, 16, 23, 's'); G.rang(11, 19, 20, 'h');
      G.motif(13, 6, ['..gg', '.gg.', 'gg..']);
      G.motif(23, 6, ['gg..', '.gg.']);
      tempes(G, v, 12, 17, 1);
    } else if (c === 'meche') {
      calotte(G, v, 5, 11, 1);
      [[12, 20 - hw(12), 22], [13, 20 - hw(13), 19], [14, 20 - hw(14), 17], [15, 20 - hw(15), 14]].forEach(function (r) {
        G.rang(r[0], r[1], r[2], 'h');
      });
      G.motif(15, 7, ['ggg']);
      tempes(G, v, 12, 17, 1);
    } else if (c === 'longue') {
      calotte(G, v, 5, 11, 1);
      G.rang(11, 19, 20, 's'); G.rang(12, 20 - hw(12), 17, 'h'); G.rang(12, 22, 19 + hw(12), 'h');
      tempes(G, v, 12, 24, 2);
      G.motif(14, 7, ['gg', '.gg']);
    } else if (c === 'queue' || c === 'chignon') {
      calotte(G, v, 5, 10, 1);
      G.rang(11, 20 - hw(11), 19 + hw(11), 'h');
      G.rang(11, 18, 21, 's');
      tempes(G, v, 12, 16, 1);
      G.motif(14, 7, ['ggg', '.gg']);
    } else if (c === 'permanente') {
      for (let y = 6; y <= 13; y++) {
        const w = y < 12 ? hw(Math.max(y, HAUT)) + 1 : hw(y);
        for (let x = 20 - w; x <= 19 + w; x++) {
          if (y >= 12 && bruit(x, y, graine) < 45 + (y - 12) * 30) continue;
          G.pose(x, y, bruit(x, y, graine + 2) < 30 ? 'H' : (bruit(x, y, graine + 3) < 12 ? 'g' : 'h'));
        }
      }
      tempes(G, v, 12, 22, 2);
    } else if (c === 'bouclee') {
      for (let y = 4; y <= 12; y++) {
        const w = y < HAUT ? 6 + (y - 4) * 2 : hw(y) + 1;
        for (let x = 20 - w; x <= 19 + w; x++) {
          if ((y === 4 || y === 12 || x === 20 - w || x === 19 + w) && bruit(x, y, graine) < 45) continue;
          G.pose(x, y, (x + y) % 3 === 0 ? 'H' : ((x * 2 + y) % 5 === 0 ? 'g' : 'h'));
        }
      }
      tempes(G, v, 13, 17, 1);
    } else if (c === 'carre') {
      calotte(G, v, 5, 13, 1);
      for (let x = 20 - hw(13); x <= 19 + hw(13); x += 3) G.pose(x, 13, 'H');
      tempes(G, v, 14, 26, 2);
      G.motif(14, 7, ['ggg', '.ggg']);
    } else if (c === 'hirsute') {
      calotte(G, v, 5, 11, 2);
      for (let x = 20 - hw(12) - 1; x <= 19 + hw(12) + 1; x++) {
        if (bruit(x, 12, graine) < 60) G.pose(x, 12, 'h');
        if (bruit(x, 13, graine) < 25) G.pose(x, 13, 'H');
      }
      tempes(G, v, 12, 21, 2);
    }
    // ⚠️ Les cheveux qui tombent CACHENT les oreilles : sans ca, la colonne de l'oreille
    // (un pixel hors de la tete) restait une raie de peau entre deux meches.
    if (['longue', 'carre', 'permanente', 'hirsute'].indexOf(c) >= 0) {
      for (let y = 16; y <= 21; y++) G.deux(19 - hw(y), y, 'h');
    }
    // L'ombre des cheveux sur le front : la rangee de peau juste sous une meche.
    for (let y = 8; y <= 24; y++) for (let x = 0; x < TAILLE; x++) {
      if (G.lit(x, y) === 's' && 'hHg'.indexOf(G.lit(x, y - 1)) >= 0) G.pose(x, y, 'S');
    }
  }

  // ---------------------------------------------------------------- l'humeur

  //: Les sourcils de GAUCHE (x 13 a 16) ; la droite est le miroir, sauf `malin` qui en
  //: leve un seul. Chaque ligne commence a la rangee 14.
  const SOURCILS = {
    neutre:  ['....', '....', 'hhhh'],
    content: ['....', '.hh.', 'h..h'],
    rire:    ['....', '.hh.', 'h..h'],
    fache:   ['....', 'hh..', '..hh', '...h'],
    serieux: ['....', '....', 'hhhh', '...h'],
    triste:  ['....', '..hh', 'hh..'],
    inquiet: ['....', '..hh', 'hh..'],
    surpris: ['.hh.', 'h..h'],
    malin:   ['....', '....', 'hhhh'],
    froid:   ['....', '....', 'hhhh'],
  };
  //: Les yeux de GAUCHE (x 13 a 17, rangees 17 a 19) : `k` la paupiere, `w` le blanc, `y` l'iris.
  const YEUX = {
    ouvert:  ['.....', '.kkk.', '.wyw.'],
    content: ['.....', '.kkk.', '.wyS.'],
    plisse:  ['.....', '.....', '.kyk.'],
    ferme:   ['.....', '.....', '.kkk.'],
    rire:    ['.....', '..k..', '.k.k.'],
    grand:   ['.kkk.', '.wyw.', '.www.'],
    triste:  ['.....', '..kk.', '.wyw.'],
  };
  const YEUX_DE = {
    neutre: 'ouvert', content: 'content', rire: 'rire', fache: 'ouvert', serieux: 'ouvert',
    triste: 'triste', inquiet: 'triste', surpris: 'grand', malin: 'plisse', froid: 'plisse',
  };
  //: La bouche, de x = 16 a 23, a partir de la rangee 24.
  const BOUCHES = {
    neutre:  ['........', '..mmmm..'],
    content: ['.m....m.', '..mmmm..'],
    rire:    ['.mmmmmm.', '.mddddm.', '..mmmm..'],
    fache:   ['........', '..mmmm..', '.m....m.'],
    serieux: ['........', '..mmmm..'],
    triste:  ['........', '...mm...', '..m..m..'],
    inquiet: ['........', '..mm....', '....mm..'],
    surpris: ['...mm...', '..mkkm..', '...mm...'],
    malin:   ['......m.', '..mmmm..'],
    froid:   ['........', '..mmm...'],
  };
  //: La bouche qui parle : deux ouvertures qu'on alterne pendant que la voix joue.
  const PARLE = [
    ['........', '..mmmm..', '...kk...'],
    ['..mmmm..', '.mkkkkm.', '..mkkm..'],
  ];
  const PARLE_RIRE = [
    ['.mmmmmm.', '.mddddm.', '..mkkm..'],
    ['.mmmmmm.', '.mddddm.', '.mkkkkm.', '..mmmm..'],
  ];

  function peindreYeux(G, v, humeur, sig, clin) {
    let forme = YEUX_DE[humeur] || 'ouvert';
    if (sig.yeux_plisses && (forme === 'ouvert' || forme === 'content')) forme = 'plisse';
    if (clin && forme !== 'rire' && forme !== 'ferme') forme = 'ferme';
    G.motif(13, 17, YEUX[forme], true);
    if (sig.yeux_voiles) G.teint(13, 17, 26, 19, 'y', 'V');
    // Les cils : un coin de plus a l'exterieur, pour qui porte du rouge.
    if (sig.rouge && forme !== 'rire') { G.pose(13, 17 + (forme === 'grand' ? 0 : 1), 'k'); G.pose(26, 17 + (forme === 'grand' ? 0 : 1), 'k'); }
    // Les sourcils. ⚠️ Couleur des CHEVEUX, meme sous un chapeau ; un chauve a les siens.
    const s = SOURCILS[humeur] || SOURCILS.neutre;
    const brun = sig.sourcils_epais ? 'H' : 'h';
    const ligne = function (l) { return l.replace(/h/g, brun); };
    G.motif(13, 14, s.map(ligne), humeur !== 'malin');
    if (humeur === 'malin') G.motif(23, 14, SOURCILS.surpris.map(ligne).map(function (l) { return l.split('').reverse().join(''); }));
    if (sig.sourcils_epais) {
      const epais = s.map(function (l, i) { return i + 1 < s.length ? '....' : l; });
      G.motif(13, 13, epais.map(ligne), humeur !== 'malin');
    }
  }

  function peindreNez(G, sig) {
    const n = sig.nez_rouge ? 'r' : 'S';
    G.pose(20, 20, n); G.pose(20, 21, n); G.pose(19, 22, n); G.pose(20, 22, n);
    if (sig.nez_rouge) { G.pose(19, 21, 'r'); G.pose(21, 21, 'r'); G.pose(21, 22, 'r'); }
  }

  function peindreBouche(G, humeur, bouche, sig) {
    let m = BOUCHES[humeur] || BOUCHES.neutre;
    if (bouche > 0) m = (humeur === 'rire' || humeur === 'content' ? PARLE_RIRE : PARLE)[bouche - 1];
    if (sig.rouge) m = m.map(function (l) { return l.replace(/m/g, 'l'); });
    G.motif(16, 24, m);
  }

  // ---------------------------------------------------------------- la barbe

  function peindreBarbe(G, v) {
    const p = v.pilosite, hw = function (y) { return demi(v.tete, y); };
    if (p === 'barbe' || p === 'barbe_courte' || p === 'bouc' || p === 'mal_rase') {
      const y0 = p === 'barbe' ? 21 : (p === 'bouc' ? 27 : 23);
      for (let y = y0; y <= MENTON + (p === 'barbe' ? 2 : 0); y++) {
        const w = y > MENTON ? hw(MENTON) - (y - MENTON) : hw(y);
        for (let x = 20 - w; x <= 19 + w; x++) {
          if (p === 'bouc' && (x < 17 || x > 22)) continue;
          // Sur les joues, la barbe ne monte que le long de la machoire.
          if (y < 24 && x > 20 - w + 2 && x < 19 + w - 2) continue;
          if (p === 'mal_rase') { if (bruit(x, y, 11) < 35) G.pose(x, y, 'u'); continue; }
          G.pose(x, y, x >= 17 + w ? 'B' : 'b');
        }
      }
      if (p === 'barbe') for (let y = 17; y <= 21; y++) G.deux(20 - hw(y), y, 'b');
    }
  }

  /** La moustache se pose APRES la bouche : elle mange la levre du haut. */
  function peindreMoustache(G, v) {
    const p = v.pilosite;
    if (p === 'moustache') G.motif(16, 23, ['.bbbbbb.', 'b......b']);
    else if (p === 'moustache_epaisse') G.motif(15, 22, ['...bbbb...', 'bbbbbbbbbb', 'bBB....BBb']);
    else if (p === 'barbe' || p === 'barbe_courte' || p === 'bouc') G.motif(16, 23, ['.bbbbbb.']);
  }

  // ---------------------------------------------------------------- lunettes et chapeaux

  function peindreLunettes(G, v) {
    const l = v.lunettes;
    if (!l || l === 'aucunes') return;
    const hw = demi(v.tete, 18);
    if (l === 'rondes') {
      G.motif(13, 16, ['.eee.', 'e...e', 'e...e', '.eee.'], true);
      G.rang(17, 18, 21, 'e');
    } else if (l === 'carrees' || l === 'epaisses') {
      G.motif(12, 16, ['eeeeee', 'e....e', 'e....e', 'eeeeee'], true);
      if (l === 'epaisses') G.motif(12, 16, ['eeeeee', 'e....e', 'e....e', 'eeeeee'].map(function (r, i) { return i === 0 || i === 3 ? r : 'ee..ee'; }), true);
      G.rang(17, 18, 21, 'e');
    } else if (l === 'demi') {
      G.motif(12, 19, ['e....e', '.eeee.'], true);
      G.rang(19, 18, 21, 'e');
    }
    for (let x = 20 - hw - 1; x < 12; x++) G.deux(x, 17, 'e');
  }

  function peindreChapeau(G, v) {
    const c = v.chapeau, hw = demi(v.tete, 10);
    if (!c || c === 'aucun') return;
    if (c === 'police' || c === 'casquette' || c === 'marin') {
      const haut = c === 'police' ? 2 : 4;
      for (let y = haut; y <= 10; y++) {
        const w = c === 'police' && y < 6 ? hw + 2 : (y === haut ? hw - 1 : hw + 1);
        G.centre(y, w, 't');
      }
      G.rang(haut, 20 - hw - 1, 19 + hw + 1, 'T');
      if (c === 'police') { G.centre(9, hw + 1, 'k'); G.motif(18, 5, ['.oo.', 'oooo', '.oo.']); }
      else if (c === 'casquette') { G.centre(9, hw + 1, 'T'); G.motif(19, 6, ['aa']); }
      else G.motif(20 - hw, 6, ['TT']);
      // La visiere : noire et vernie ; un peu plus courte pour le marin.
      G.centre(11, hw + (c === 'marin' ? 0 : 2), 'k');
      G.rang(11, 16, 18, 'e');
      G.centre(12, hw - 2, 'S');
    } else if (c === 'tuque') {
      G.motif(17, 0, ['.RRRR.', 'RRqRRR', '.RRRR.']);
      for (let y = 3; y <= 12; y++) {
        const w = y < 6 ? hw - 4 + (y - 3) * 2 : hw + 1;
        G.centre(y, w, y >= 10 ? ((y === 11) ? 'T' : 't') : 't');
      }
      for (let x = 20 - hw - 1; x <= 19 + hw + 1; x += 2) { G.pose(x, 10, 'T'); G.pose(x, 12, 'T'); }
      for (let y = 4; y <= 9; y++) for (let x = 20 - hw; x <= 19 + hw; x += 3) if (G.lit(x, y) === 't') G.pose(x, y, 'T');
      G.centre(13, hw - 1, 'S');
    } else if (c === 'canotier') {
      G.bloc(20 - hw + 1, 3, 19 + hw - 1, 7, 't');
      G.rang(3, 20 - hw + 1, 19 + hw - 1, 'T');
      G.rang(7, 20 - hw + 1, 19 + hw - 1, 'R');
      G.centre(8, hw + 4, 't');
      G.centre(9, hw + 4, 'T');
      for (let x = 20 - hw + 1; x <= 19 + hw - 1; x += 2) G.pose(x, 5, 'T');
      G.centre(10, hw - 1, 'S');
    } else if (c === 'coiffe') {
      G.motif(13, 3, ['...tttttttt...', '.tttttttttttt.', 'ttttttRRtttttt', 'tttttRRRRttttt', 'ttttttRRtttttt', 'TttttttttttttT']);
      G.rang(8, 14, 25, 'T');
    }
  }

  // ---------------------------------------------------------------- les petits signes

  function peindreSignes(G, v, sig) {
    const hw = function (y) { return demi(v.tete, y); };
    const peau = function (x, y, ch) { if ('sS'.indexOf(G.lit(x, y)) >= 0) G.pose(x, y, ch); };
    if (sig.rides) {
      [16, 17, 18, 21, 22, 23].forEach(function (x) { peau(x, 13, 'S'); });
      peau(12, 17, 'S'); peau(12, 19, 'S'); peau(27, 17, 'S'); peau(27, 19, 'S');
      peau(16, 23, 'S'); peau(23, 23, 'S');
    }
    if (sig.cernes) { [14, 15, 16, 23, 24, 25].forEach(function (x) { peau(x, 20, 'S'); }); }
    if (sig.fard) { [[13, 21], [14, 21], [15, 22], [26, 21], [25, 21], [24, 22]].forEach(function (p) { peau(p[0], p[1], 'r'); }); }
    if (sig.rousseur) { [[13, 21], [15, 21], [14, 22], [16, 21], [24, 21], [26, 21], [25, 22], [23, 21]].forEach(function (p) { peau(p[0], p[1], 'F'); }); }
    if (sig.cicatrice) { [[25, 20], [26, 21], [26, 22], [27, 23]].forEach(function (p) { peau(p[0], p[1], 'z'); }); }
    if (sig.grain) peau(24, 24, 'k');
    if (sig.boucles) { G.deux(19 - hw(21), 22, 'o'); G.deux(19 - hw(21), 23, 'o'); }
    if (sig.megot) { G.motif(22, 26, ['xxxf']); G.pose(26, 25, 'a'); G.pose(27, 23, 'a'); }
    if (sig.cure_dent) G.motif(22, 24, ['..jj', 'jj..']);
    if (sig.crayon) G.motif(27, 13, ['R...', '.oo.', '..oo', '...k']);
  }

  // ---------------------------------------------------------------- la cuisson

  /** Le contour : tout vide qui touche le dessin devient un trait sombre. */
  function contour(G) {
    const bord = [];
    for (let y = 0; y < TAILLE; y++) for (let x = 0; x < TAILLE; x++) {
      if (G.g[y][x] !== '.') continue;
      if (G.lit(x - 1, y) !== '.' || G.lit(x + 1, y) !== '.' || G.lit(x, y - 1) !== '.' || G.lit(x, y + 1) !== '.') bord.push([x, y]);
    }
    bord.forEach(function (p) { G.g[p[1]][p[0]] = 'k'; });
  }

  /** La grille d'un portrait, en lettres — ce que `cuire` peint, et ce que les juges lisent. */
  function grille(v, humeur, bouche, clin, slug) {
    const G = new Grille(), graine = graineDe(slug || '');
    const sig = {};
    (v.signes || []).forEach(function (s) { sig[s] = true; });
    arriereCheveux(G, v, graine);
    peindreTete(G, v);
    peindreHabit(G, v, sig);
    devantCheveux(G, v, graine);
    peindreSignes(G, v, sig);
    peindreBarbe(G, v);
    peindreNez(G, sig);
    peindreBouche(G, humeur, bouche, sig);
    peindreMoustache(G, v);
    peindreYeux(G, v, humeur, sig, clin);
    peindreLunettes(G, v);
    peindreChapeau(G, v);
    if (sig.megot || sig.cure_dent) peindreSignes(G, v, { megot: sig.megot, cure_dent: sig.cure_dent });
    contour(G);
    return G.g.map(function (r) { return r.join(''); });
  }

  const cache = new Map();

  function fiche(slug) {
    const defs = (typeof B !== 'undefined' && B.defs && B.defs.visages) || {};
    return defs[slug] || null;
  }

  /** Le portrait cuit (un canevas de 40 x 40, fond compris), ou null s'il n'a pas de visage. */
  function cuire(slug, humeur, bouche, clin) {
    const v = fiche(slug);
    if (!v) return null;
    if (HUMEURS.indexOf(humeur) < 0) humeur = 'neutre';
    const cle = slug + '|' + humeur + '|' + (bouche || 0) + '|' + (clin ? 1 : 0);
    if (cache.has(cle)) return cache.get(cle);
    const pal = palette(v);
    const lignes = grille(v, humeur, bouche || 0, clin, slug);
    const c = Base.nouveauCanvas(TAILLE, TAILLE);
    const ctx = c.getContext('2d');
    // Le fond : la couleur de son chandail, presque eteinte — chacun a sa lumiere.
    const fond = melange(pal.c, '#0b0a12', 0.82);
    ctx.fillStyle = fond; ctx.fillRect(0, 0, TAILLE, TAILLE);
    ctx.fillStyle = melange(pal.c, '#0b0a12', 0.7); ctx.fillRect(0, 0, TAILLE, 22);
    for (let y = 0; y < TAILLE; y++) for (let x = 0; x < TAILLE; x++) {
      const ch = lignes[y][x];
      if (ch === '.') continue;
      ctx.fillStyle = pal[ch] || '#ff00ff';
      ctx.fillRect(x, y, 1, 1);
    }
    cache.set(cle, c);
    return c;
  }

  //: Le clin d'oeil : une fois toutes les `CLIN` images, pendant `CLIN_DUREE`.
  const CLIN = 170, CLIN_DUREE = 7;

  /** L'image a montrer a l'instant `t` : la bouche bouge si `parle`, les yeux clignent. */
  function etat(slug, t, parle) {
    const decale = graineDe(slug) % CLIN;
    const clin = ((t + decale) % CLIN) < CLIN_DUREE;
    // La bouche : fermee, entrouverte, ouverte — un pas toutes les quatre images, dans un
    // ordre qui ne se repete pas trop vite (une voix ne bat pas la mesure).
    const PAS = [1, 2, 1, 0, 2, 1, 2, 0, 1, 1, 2, 0];
    const bouche = parle ? PAS[(t >> 2) % PAS.length] : 0;
    return { clin: clin, bouche: bouche };
  }

  /** Dessine le portrait de `slug` en (x, y), cadre compris (42 x 42). Rend false sans visage. */
  function dessiner(ctx, slug, x, y, humeur, t, parle) {
    const e = etat(slug, t || 0, parle);
    const img = cuire(slug, humeur || 'neutre', e.bouche, e.clin);
    if (!img) return false;
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(x, y, TAILLE + 2, TAILLE + 2);
    ctx.fillStyle = '#101018'; ctx.fillRect(x + 1, y + 1, TAILLE, TAILLE);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(img, x + 1, y + 1);
    return true;
  }

  function connait(slug) { return !!fiche(slug); }

  function vider() { cache.clear(); }

  return { TAILLE, HUMEURS, TETES, grille, cuire, dessiner, etat, connait, fiche, vider, palette };
})();
