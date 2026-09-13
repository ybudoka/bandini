/* Bandini — sprites : donnees seulement (palettes + grilles), et peintres de tuiles.

   Convention : le personnage fait 12x16, ancre au pied (6, 15). Trois vues
   dessinees (bas, haut, cote) ; « gauche » est le miroir de « cote ».
   Chaque pose a 3 images : repos, pas 1, pas 2 (cycle 0 1 0 2). */

const SPRITES = {
  joueur: {
    w: 12, h: 16, ancre: [6, 15],
    pal: { k: '#101018', s: '#e8b088', h: '#3a2a1a', c: '#c0392b', p: '#2a2a3a', o: '#ffffff', b: '#5a3a1a' },
    swaps: ['c', 'h', 's', 'p'],
    // La main qui tient l'arme, par pose : [x, y] dans la grille, et l'angle
    // de l'arme (0 = vers la droite, PI/2 = vers nous). Les poses « cote »
    // valent pour « droite » ; « gauche » se miroite.
    mains: {
      bas: [10, 10, Math.PI / 2 + 0.6], haut: [10, 10, -Math.PI / 2 + 0.4], droite: [8, 10, 0.9],
      frappe_bas: [6, 9, Math.PI / 2], frappe_haut: [10, 3, -Math.PI / 2], frappe_droite: [11, 8, 0],
    },
    poses: {
      bas: [
        ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..',
         '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.'],
        ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..',
         '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kppk..kpk.', '..kbbk..kbk.', '..kkkk..kk..'],
        ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..',
         '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kpk..kppk.', '..kbk..kbbk.', '..kk..kkkk..'],
      ],
      haut: [
        ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..',
         '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.'],
        ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..',
         '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kppk..kpk.', '..kbbk..kbk.', '..kkkk..kk..'],
        ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..',
         '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kpk..kppk.', '..kbk..kbbk.', '..kk..kkkk..'],
      ],
      // ⚠️ Le coup est une VRAIE pose : le bras du sprite se tend vers la
      // cible. Un bras dessine par-dessus faisait un troisieme bras (Martin).
      // Une image par direction ; « cote » se miroite comme la marche.
      frappe_bas: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '.kckksskckc.', '.kckksskckc.', '.kskkkkkksc.', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      frappe_haut: [['....kkkk....', '...khhhhk...', '..khhhhhhkss', '..khhhhhhkss', '..khhhhhhkck', '..khsssshkck', '...ksssskck.', '..kcccccckck', '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      frappe_cote: [['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khssssk..', '...khsssk...', '....kssk....', '...kcccck...', '...kccccccss', '...kcckkkkkk', '...kcck.....', '...kppppk...', '...kppppk...', '...kpkkpk...', '...kbk.kbk..', '...kkk.kkk..']],
      // ⚠️ Une seule image, et l'entite pose `face = 'couche'` : c'est ainsi
      // qu'un KO et un mort se dessinent sans faire tourner un canevas.
      couche: [
        ['............', '............', '............', '............', '............', '............', '............',
         '..kkkkkk....', '.kpppppkkkk.', 'kppppppccccs', 'kppppppcccck', '.kpppppkccsk', '..kbbkk.kkk.', '..kkk.......', '............', '............'],
      ],
      cote: [
        ['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khssssk..', '...khsssk...', '....kssk....', '...kcccck...',
         '...kcccck...', '...kcckck...', '...kccksk...', '...kppppk...', '...kppppk...', '...kpkkpk...', '...kbk.kbk..', '...kkk.kkk..'],
        ['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khssssk..', '...khsssk...', '....kssk....', '...kcccck...',
         '...kcccck...', '...kcckck...', '...kccksk...', '...kppppk...', '...kppppk...', '..kpk..kpk..', '..kbk..kbk..', '..kkk..kkk..'],
        ['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khssssk..', '...khsssk...', '....kssk....', '...kcccck...',
         '...kcccck...', '...kcckck...', '...kccksk...', '...kppppk...', '...kppppk...', '....kppk....', '....kbbk....', '....kkkk....'],
      ],
    },
  },
};

/* L'enfant : 10x13, la tete plus grosse et deux poses par direction. Il ne
   sert jamais de cible (`intouchable` dans le catalogue) — il court, c'est
   tout. */
SPRITES.enfant = {
  w: 10, h: 13, ancre: [5, 12],
  pal: { k: '#101018', s: '#f0c098', h: '#6b4b2c', c: '#f1c40f', p: '#2f6b8a', o: '#ffffff', b: '#5a3a1a' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kkkk...', '..khhhhk..', '.khhhhhhk.', '.khsssshk.', '.ksossosk.', '.kssssssk.', '..kssssk..',
       '..kcccck..', '.kcccccck.', '.kskccksk.', '..kppppk..', '..kppkppk.', '..kk..kk..'],
      ['...kkkk...', '..khhhhk..', '.khhhhhhk.', '.khsssshk.', '.ksossosk.', '.kssssssk.', '..kssssk..',
       '..kcccck..', '.kcccccck.', '.kskccksk.', '..kppppk..', '..kpppk...', '..kkbk....'],
    ],
    haut: [
      ['...kkkk...', '..khhhhk..', '.khhhhhhk.', '.khhhhhhk.', '.khhhhhhk.', '.kssssssk.', '..kssssk..',
       '..kcccck..', '.kcccccck.', '.kskccksk.', '..kppppk..', '..kppkppk.', '..kk..kk..'],
      ['...kkkk...', '..khhhhk..', '.khhhhhhk.', '.khhhhhhk.', '.khhhhhhk.', '.kssssssk.', '..kssssk..',
       '..kcccck..', '.kcccccck.', '.kskccksk.', '..kppppk..', '...kppk...', '....kbk...'],
    ],
    cote: [
      ['...kkkk...', '..khhhhk..', '..khhhhhk.', '..khssosk.', '..khsssk..', '...kssk...', '...kssk...',
       '...kcccck.', '...kcccck.', '...kcckck.', '...kpppk..', '...kppk...', '...kbbk...'],
      ['...kkkk...', '..khhhhk..', '..khhhhhk.', '..khssosk.', '..khsssk..', '...kssk...', '...kssk...',
       '...kcccck.', '...kcccck.', '...kcckck.', '...kpppk..', '..kpk.kpk.', '..kbk.kbk.'],
    ],
  },
};

/* Les vehicules, vus de dessus, l'AVANT A DROITE (angle 0 = est). Un seul
   dessin par type : l'atlas le fait tourner en 32 caps a la cuisson. `c` est
   la carrosserie (echangee par couleur), `x`/`y` les accents de toit (enseigne
   du taxi, gyrophare de la police), `l` les phares, `t` les feux arriere. */
const GRILLE_AUTO = [
      '.....rrrr.............rrrr......',
      '.....rrrr.............rrrr......',
      '..kkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
      '.kcccccccccccccccccccccccssssck.',
      '.ktccccvvkccccccccccvvvkccccclk.',
      '.ktccccvvkccccccccccvvvkccccclk.',
      '.kcccccvvkcxxxcyyyccvvvkcccccck.',
      '.kcccccvvkcxxxcyyyccvvvkcccccck.',
      '.kcccccvvkcxxxcyyyccvvvkcccccck.',
      '.kcccccvvkcxxxcyyyccvvvkcccccck.',
      '.ktccccvvkccccccccccvvvkccccclk.',
      '.ktccccvvkccccccccccvvvkccccclk.',
      '.kcccccccccccccccccccccccssssck.',
      '..kkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
      '.....rrrr.............rrrr......',
      '.....rrrr.............rrrr......',
    ];
const GRILLE_MOTO = [
      '....................',
      '....................',
      '........hhh..k......',
      '.rrrrkkkpppkkklrrrr.',
      '.rrrrtccpppcckcrrrr.',
      '.rrrrtccpppcckcrrrr.',
      '.rrrrkkkpppkkklrrrr.',
      '........hhh..k......',
      '....................',
      '....................',
    ];

SPRITES.auto = {
  w: 32, h: 16, ancre: [16, 8], rotations: 32,
  pal: { k: '#101018', c: '#c0392b', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', x: '#c0392b', y: '#c0392b', s: '#00000030' },
  swaps: ['c'], poses: { base: [GRILLE_AUTO] },
};
SPRITES.taxi = {
  w: 32, h: 16, ancre: [16, 8], rotations: 32,
  pal: { k: '#101018', c: '#f1c40f', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', x: '#101018', y: '#101018', s: '#00000030' },
  swaps: ['c'], poses: { base: [GRILLE_AUTO] },
};
SPRITES.police = {
  w: 32, h: 16, ancre: [16, 8], rotations: 32,
  pal: { k: '#101018', c: '#ffffff', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', x: '#e0312a', y: '#2f6fd8', s: '#00000030' },
  swaps: ['c'], poses: { base: [GRILLE_AUTO] },
};
SPRITES.velo = {
  w: 16, h: 8, ancre: [8, 4], rotations: 32,
  pal: { k: '#101018', c: '#2980b9', r: '#2a2a2e', h: '#3a2a1a', p: '#c0392b', s: '#e8b088', l: '#fff3b0', t: '#ff4b3e' },
  swaps: ['c'], poses: { base: [[
    '................',
    '......hhh.......',
    '.kk...sss...kk..',
    'krrk.kpppk.krrk.',
    'krrkcccccccrrkl.',
    'krrk.kpppk.krrk.',
    '.kk...sss...kk..',
    '................',
  ]] },
};
SPRITES.moto = {
  w: 20, h: 10, ancre: [10, 5], rotations: 32,
  pal: { k: '#101018', c: '#1a1a1a', r: '#1a1a1e', h: '#2c2c2c', p: '#3a3a4a', l: '#fff3b0', t: '#ff4b3e' },
  swaps: ['c'], poses: { base: [GRILLE_MOTO] },
};

/* Peintres de tuiles 16x16 : (ctx, variante, T). Le bruit vient de la variante,
   un entier stable par position (hash2), pour que la ville ne scintille pas. */
const TUILES = (function () {
  function bruit(v, i) { return ((v * 1103515245 + i * 12345) >>> 0) % 1000 / 1000; }
  function plein(ctx, c, T) { ctx.fillStyle = c; ctx.fillRect(0, 0, T, T); }
  function points(ctx, v, T, couleur, n, i0) {
    ctx.fillStyle = couleur;
    for (let i = 0; i < n; i++) {
      ctx.fillRect(Math.floor(bruit(v, i0 + i) * T), Math.floor(bruit(v, i0 + i + 50) * T), 1, 1);
    }
  }
  function asphalte(ctx, v, T) { plein(ctx, '#2f3138', T); points(ctx, v, T, '#383a42', 10, 0); points(ctx, v, T, '#26282e', 6, 100); }
  function trottoir(ctx, v, T) {
    plein(ctx, '#9a9689', T);
    ctx.fillStyle = '#8b877b'; ctx.fillRect(0, 0, T, 1); ctx.fillRect(0, 0, 1, T);
    ctx.fillStyle = '#a5a194'; ctx.fillRect(1, 1, T - 2, 1);
    points(ctx, v, T, '#8f8b7f', 5, 7);
  }
  function facade(ctx, v, T, teinte) {
    plein(ctx, teinte || '#8c4a3c', T);
    ctx.fillStyle = 'rgba(0,0,0,0.18)';
    for (let y = 0; y < T; y += 4) {
      ctx.fillRect(0, y + 3, T, 1);
      const d = (y / 4) % 2 ? 4 : 0;
      for (let x = d; x < T; x += 8) ctx.fillRect(x, y, 1, 3);
    }
  }
  return {
    ',': function (ctx, v, T) { plein(ctx, '#4f8d3e', T); points(ctx, v, T, '#5a9c47', 12, 3); points(ctx, v, T, '#427a33', 8, 60); },
    '.': trottoir,
    'x': function (ctx, v, T) { plein(ctx, '#55524c', T); points(ctx, v, T, '#4a4741', 8, 9); },
    '#': asphalte,
    // ⚠️ Le marquage se peint sur le BORD NORD (ou OUEST) de la tuile, jamais au
    // milieu : une ligne centrale doit tomber ENTRE les deux sens, sinon elle a
    // l'air peinte sur une voie et la rue devient illisible.
    '-': function (ctx, v, T) { asphalte(ctx, v, T); ctx.fillStyle = '#d9d6cc'; for (let x = 0; x < T; x += 8) ctx.fillRect(x, 0, 5, 1); },
    '|': function (ctx, v, T) { asphalte(ctx, v, T); ctx.fillStyle = '#d9d6cc'; for (let y = 0; y < T; y += 8) ctx.fillRect(0, y, 1, 5); },
    '+': function (ctx, v, T) { asphalte(ctx, v, T); ctx.fillStyle = '#d8b83a'; ctx.fillRect(0, 0, T, 2); },
    '*': function (ctx, v, T) { asphalte(ctx, v, T); ctx.fillStyle = '#d8b83a'; ctx.fillRect(0, 0, 2, T); },
    // ⚠️ Les bandes d'un passage sont PARALLELES a la circulation : le pieton
    // les enjambe une a une. Rue est-ouest : bandes horizontales. C'etait a
    // l'envers — Martin l'a vu du premier coup d'oeil.
    // La variante vient de Monde.varianteDePassage : 0 pleine, 1 exterieure
    // ouest/nord (un bout de 5 px du cote est/sud), 2 exterieure est/sud.
    // Deux tiers de 32 px = 21 px de bandes : Martin les trouvait trop larges.
    '=': function (ctx, v, T) {
      asphalte(ctx, v, T); ctx.fillStyle = '#e8e6de';
      const x0 = v === 1 ? T - 5 : 0, l = v === 0 ? T : 5;
      for (let y = 1; y < T; y += 5) ctx.fillRect(x0, y, l, 3);
    },
    ':': function (ctx, v, T) {
      asphalte(ctx, v, T); ctx.fillStyle = '#e8e6de';
      const y0 = v === 1 ? T - 5 : 0, h = v === 0 ? T : 5;
      for (let x = 1; x < T; x += 5) ctx.fillRect(x, y0, 3, h);
    },
    // Une ligne de case tous les trois pas : a chaque tuile, le stationnement
    // ressemblait a un code-barres.
    'p': function (ctx, v, T) { asphalte(ctx, v, T); if (v % 3 === 0) { ctx.fillStyle = '#c9c6bc'; ctx.fillRect(0, 2, 1, T - 4); } },
    'R': function (ctx, v, T) { asphalte(ctx, v, T); ctx.fillStyle = '#d8b83a'; for (let i = 0; i < T; i += 4) ctx.fillRect(i, T - 4 - i / 2, 3, 2); },
    'Q': function (ctx, v, T) { plein(ctx, '#8a6a3f', T); ctx.fillStyle = '#6e5330'; for (let y = 0; y < T; y += 4) ctx.fillRect(0, y, T, 1); },
    's': function (ctx, v, T) { plein(ctx, '#d8c48a', T); points(ctx, v, T, '#c9b576', 10, 4); },
    '~': function (ctx, v, T) { plein(ctx, '#2c5f8a', T); ctx.fillStyle = '#3b73a3'; ctx.fillRect(2 + (v % 5), 4, 6, 1); ctx.fillRect(7 - (v % 4), 11, 5, 1); },
    'B': function (ctx, v, T) { plein(ctx, '#5b4a4a', T); points(ctx, v, T, '#655252', 10, 2); points(ctx, v, T, '#4e3f3f', 8, 80); },
    'E': function (ctx, v, T) { plein(ctx, '#4a4f5e', T); ctx.fillStyle = '#424656'; for (let y = 0; y < T; y += 4) ctx.fillRect(0, y, T, 1); points(ctx, v, T, '#545a6b', 6, 20); },
    'O': function (ctx, v, T) { plein(ctx, '#6d6152', T); points(ctx, v, T, '#7b6e5d', 14, 40); points(ctx, v, T, '#5d5346', 10, 90); },
    'F': function (ctx, v, T) { facade(ctx, v, T); },
    'W': function (ctx, v, T) { facade(ctx, v, T); ctx.fillStyle = '#243447'; ctx.fillRect(3, 3, 10, 9); ctx.fillStyle = '#7fb3d8'; ctx.fillRect(4, 4, 3, 3); ctx.fillStyle = '#4d7ea3'; ctx.fillRect(8, 4, 4, 7); ctx.fillRect(4, 8, 3, 3); },
    'D': function (ctx, v, T) { facade(ctx, v, T); ctx.fillStyle = '#3d2a1c'; ctx.fillRect(4, 3, 8, 13); ctx.fillStyle = '#d8b83a'; ctx.fillRect(10, 9, 1, 1); },
    'd': function (ctx, v, T) { facade(ctx, v, T); ctx.fillStyle = '#2e2118'; ctx.fillRect(4, 4, 8, 12); ctx.fillStyle = '#3a2a1e'; ctx.fillRect(5, 5, 6, 10); ctx.fillStyle = '#6b5a48'; ctx.fillRect(4, 8, 8, 1); },
    'G': function (ctx, v, T) { facade(ctx, v, T); ctx.fillStyle = '#7a7d82'; ctx.fillRect(1, 3, 14, 13); ctx.fillStyle = '#5f6267'; for (let y = 5; y < 16; y += 3) ctx.fillRect(1, y, 14, 1); },
    'b': function (ctx, v, T) { trottoir(ctx, v, T); ctx.fillStyle = '#d8b83a'; ctx.fillRect(6, 4, 4, 10); ctx.fillStyle = '#101018'; ctx.fillRect(6, 8, 4, 1); },
    'f': function (ctx, v, T) { plein(ctx, '#4f8d3e', T); ctx.fillStyle = '#7a7d82'; ctx.fillRect(0, 6, T, 1); ctx.fillRect(0, 10, T, 1); ctx.fillRect(2, 3, 1, 11); ctx.fillRect(13, 3, 1, 11); },
    't': function (ctx, v, T) { plein(ctx, '#b8a98a', T); ctx.fillStyle = '#a89979'; ctx.fillRect(0, 0, T, 1); ctx.fillRect(0, 0, 1, T); },
    'c': function (ctx, v, T) { plein(ctx, '#6b4b2c', T); ctx.fillStyle = '#8a6a3f'; ctx.fillRect(0, 0, T, 4); },
  };
})();

/* Decor procedural : (ctx, w, h). `r` = rayon au sol, `solide` = on s'y cogne.
   ⚠️ Un poteau ou un buisson n'est PAS solide : un trottoir de 32 px ou l'on
   reste coince sur une poubelle est un trottoir qu'on n'emprunte plus. */
const DECORS = {
  arbre: { w: 18, h: 26, ancre: [9, 25], r: 5, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#5a3a1a'; ctx.fillRect(8, 16, 3, 9);
    ctx.fillStyle = '#2f6b2a'; ctx.fillRect(2, 4, 14, 13); ctx.fillRect(5, 1, 8, 3); ctx.fillRect(0, 7, 18, 7);
    ctx.fillStyle = '#3f8d38'; ctx.fillRect(4, 3, 6, 5); ctx.fillRect(2, 9, 5, 4);
    ctx.fillStyle = '#204d1e'; ctx.fillRect(10, 10, 6, 6); ctx.fillRect(6, 14, 8, 3);
  } },
  lampadaire: { w: 8, h: 30, ancre: [3, 29], r: 2, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(2, 4, 2, 26); ctx.fillRect(0, 28, 6, 2);
    ctx.fillStyle = '#4a4d55'; ctx.fillRect(2, 2, 6, 2);
    ctx.fillStyle = '#ffe9a8'; ctx.fillRect(6, 3, 2, 3);
  } },
  poubelle: { w: 10, h: 14, ancre: [5, 13], r: 4, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#3f4a3c'; ctx.fillRect(1, 3, 8, 11);
    ctx.fillStyle = '#4c5a48'; ctx.fillRect(2, 4, 6, 9);
    ctx.fillStyle = '#2b332a'; ctx.fillRect(0, 1, 10, 3); ctx.fillRect(4, 5, 1, 8);
  } },
  banc: { w: 18, h: 12, ancre: [9, 11], r: 5, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(1, 4, 16, 3); ctx.fillRect(1, 0, 16, 3);
    ctx.fillStyle = '#523a22'; ctx.fillRect(2, 7, 2, 5); ctx.fillRect(14, 7, 2, 5);
    ctx.fillStyle = '#7d5a36'; ctx.fillRect(1, 4, 16, 1);
  } },
  caisse: { w: 16, h: 16, ancre: [8, 15], r: 6, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#8a6a3f'; ctx.fillRect(1, 2, 14, 14);
    ctx.fillStyle = '#a07c4b'; ctx.fillRect(2, 3, 12, 5);
    ctx.fillStyle = '#6e5330'; ctx.fillRect(1, 8, 14, 1); ctx.fillRect(7, 2, 2, 14);
  } },
  buisson: { w: 16, h: 12, ancre: [8, 11], r: 5, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#2f6b2a'; ctx.fillRect(1, 3, 14, 8); ctx.fillRect(3, 1, 10, 3);
    ctx.fillStyle = '#3f8d38'; ctx.fillRect(3, 3, 5, 4); ctx.fillRect(9, 5, 4, 3);
    ctx.fillStyle = '#204d1e'; ctx.fillRect(2, 8, 12, 3);
  } },
  debris: { w: 14, h: 10, ancre: [7, 9], r: 4, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#6b6258'; ctx.fillRect(1, 5, 12, 5);
    ctx.fillStyle = '#807768'; ctx.fillRect(3, 2, 4, 4); ctx.fillRect(8, 4, 3, 3);
    ctx.fillStyle = '#544c44'; ctx.fillRect(2, 7, 3, 2); ctx.fillRect(9, 7, 4, 2);
  } },
  fontaine: { w: 34, h: 30, ancre: [17, 27], r: 13, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#8b877b'; ctx.fillRect(2, 10, 30, 17); ctx.fillRect(6, 7, 22, 21);
    ctx.fillStyle = '#a5a194'; ctx.fillRect(4, 12, 26, 3);
    ctx.fillStyle = '#2c5f8a'; ctx.fillRect(6, 14, 22, 11);
    ctx.fillStyle = '#3b73a3'; ctx.fillRect(9, 16, 7, 2); ctx.fillRect(19, 20, 6, 2);
    ctx.fillStyle = '#9a9689'; ctx.fillRect(15, 2, 4, 14);
    ctx.fillStyle = '#cfe6f5'; ctx.fillRect(14, 0, 6, 3); ctx.fillRect(13, 3, 2, 4); ctx.fillRect(19, 3, 2, 4);
  } },
  kiosque_hotdog: { w: 26, h: 26, ancre: [13, 25], r: 10, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#c0392b'; ctx.fillRect(1, 2, 24, 5);              // parasol
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(4, 2, 4, 5); ctx.fillRect(13, 2, 4, 5);
    ctx.fillStyle = '#7a7d82'; ctx.fillRect(12, 7, 2, 6);              // mat
    ctx.fillStyle = '#9aa0a8'; ctx.fillRect(4, 13, 18, 9);             // comptoir
    ctx.fillStyle = '#6f757c'; ctx.fillRect(4, 13, 18, 2);
    ctx.fillStyle = '#d98324'; ctx.fillRect(7, 16, 5, 2); ctx.fillRect(14, 16, 5, 2);
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(5, 22, 3, 4); ctx.fillRect(18, 22, 3, 4);
  } },
  kiosque_journaux: { w: 24, h: 26, ancre: [12, 25], r: 9, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#2f6b8a'; ctx.fillRect(2, 4, 20, 18);
    ctx.fillStyle = '#24506f'; ctx.fillRect(2, 4, 20, 3);
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(4, 9, 7, 9); ctx.fillRect(13, 9, 7, 9);
    ctx.fillStyle = '#8a8698'; ctx.fillRect(5, 11, 5, 1); ctx.fillRect(5, 13, 5, 1);
    ctx.fillRect(14, 11, 5, 1); ctx.fillRect(14, 13, 5, 1);
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(3, 22, 18, 4);
  } },
  roulotte_cafe: { w: 28, h: 24, ancre: [14, 23], r: 11, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(2, 4, 24, 14);
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 4, 24, 3);
    ctx.fillStyle = '#2c2c2c'; ctx.fillRect(6, 9, 16, 6);
    ctx.fillStyle = '#d98324'; ctx.fillRect(8, 11, 4, 2); ctx.fillRect(16, 11, 4, 2);
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(5, 18, 5, 5); ctx.fillRect(18, 18, 5, 5);
    ctx.fillStyle = '#101018'; ctx.fillRect(6, 20, 3, 3); ctx.fillRect(19, 20, 3, 3);
  } },
  camion_cuisine: { w: 44, h: 28, ancre: [22, 27], r: 16, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#27ae60'; ctx.fillRect(2, 4, 40, 16);             // caisse
    ctx.fillStyle = '#1e8e4f'; ctx.fillRect(2, 4, 40, 3);
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(6, 9, 20, 8);              // guichet
    ctx.fillStyle = '#2c2c2c'; ctx.fillRect(8, 11, 16, 4);
    ctx.fillStyle = '#d8b83a'; ctx.fillRect(28, 9, 10, 3); ctx.fillRect(28, 14, 10, 2);
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(4, 20, 8, 7); ctx.fillRect(30, 20, 8, 7);
    ctx.fillStyle = '#101018'; ctx.fillRect(6, 22, 4, 5); ctx.fillRect(32, 22, 4, 5);
    ctx.fillStyle = '#9aa0a8'; ctx.fillRect(2, 18, 40, 2);
  } },
  feu: { w: 10, h: 24, ancre: [5, 23], r: 2, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#2c2c30'; ctx.fillRect(0, 1, 10, 5);         // boitier, deux lanternes peintes a la volee
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(4, 6, 2, 17); ctx.fillRect(2, 22, 6, 2);
  } },
  panneau: { w: 14, h: 22, ancre: [7, 21], r: 3, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#6f757c'; ctx.fillRect(6, 8, 2, 14);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(0, 0, 14, 9);
    ctx.fillStyle = '#101018'; ctx.fillRect(2, 2, 10, 2); ctx.fillRect(2, 5, 6, 2);
    ctx.fillStyle = '#c0392b'; ctx.fillRect(10, 5, 2, 2);
  } },
  stop: { w: 10, h: 22, ancre: [5, 21], r: 2, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#c0392b'; ctx.fillRect(1, 0, 8, 8); ctx.fillRect(0, 1, 10, 6);
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(2, 3, 6, 2);
    ctx.fillStyle = '#6f757c'; ctx.fillRect(4, 8, 2, 14);
  } },
  affiche: { w: 10, h: 12, ancre: [5, 11], r: 0, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(0, 0, 10, 12);
    ctx.fillStyle = '#101018'; ctx.fillRect(1, 1, 8, 2); ctx.fillRect(3, 4, 4, 4); ctx.fillRect(2, 9, 6, 1);
    ctx.fillStyle = '#c0392b'; ctx.fillRect(1, 10, 8, 1);
  } },
  paquet: { w: 12, h: 10, ancre: [6, 9], r: 4, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#8a6a3f'; ctx.fillRect(1, 2, 10, 8);
    ctx.fillStyle = '#a07c4b'; ctx.fillRect(2, 3, 8, 3);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(5, 2, 2, 8); ctx.fillRect(1, 5, 10, 2);
    ctx.fillStyle = '#101018'; ctx.fillRect(1, 9, 10, 1);
  } },
  ombre: { w: 12, h: 6, ancre: [6, 3], r: 0, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(0,0,0,0.30)'; ctx.fillRect(2, 0, 8, 6); ctx.fillRect(0, 1, 12, 4);
  } },
};

/* Decalques au sol : sang, gouttes, impacts. Cuits une fois par variante. */
const DECALS = {
  sang: function (ctx, v, w, h) {
    ctx.fillStyle = 'rgba(110,18,18,0.72)';
    ctx.fillRect(4 + (v % 3), 4, 7, 4); ctx.fillRect(3, 5, 10, 2); ctx.fillRect(6, 3, 4, 6);
    ctx.fillStyle = 'rgba(80,12,12,0.6)';
    ctx.fillRect(1 + (v % 4), 2, 2, 2); ctx.fillRect(12 - (v % 3), 7, 2, 2);
  },
  goutte: function (ctx, v, w, h) {
    ctx.fillStyle = 'rgba(110,18,18,0.55)';
    ctx.fillRect(7 + (v % 2), 5, 2, 2); ctx.fillRect(6 - (v % 2), 7, 1, 1);
  },
  impact: function (ctx, v, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.5)';
    ctx.fillRect(7, 5, 2, 2); ctx.fillRect(6 + (v % 3), 4, 1, 1);
  },
};

/* Objets poses par terre (armes lachees). 16x10, ancre au centre. */
const OBJETS = {
  defaut: function (ctx) { ctx.fillStyle = '#9a9689'; ctx.fillRect(4, 4, 8, 3); },
  batte: function (ctx) { ctx.fillStyle = '#8a6a3f'; ctx.fillRect(2, 5, 12, 2); ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 5, 4, 2); },
  couteau: function (ctx) { ctx.fillStyle = '#c9cdd4'; ctx.fillRect(5, 5, 8, 2); ctx.fillStyle = '#3d2a1c'; ctx.fillRect(2, 5, 3, 2); },
  pistolet: function (ctx) { ctx.fillStyle = '#3a3d44'; ctx.fillRect(3, 4, 8, 3); ctx.fillRect(4, 6, 3, 3); },
  fusil: function (ctx) { ctx.fillStyle = '#3a3d44'; ctx.fillRect(2, 4, 12, 2); ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 4, 4, 3); },
  fronde: function (ctx) { ctx.fillStyle = '#6b4b2c'; ctx.fillRect(6, 3, 2, 6); ctx.fillRect(4, 3, 6, 2); ctx.fillStyle = '#c0392b'; ctx.fillRect(4, 6, 6, 1); },
  extincteur: function (ctx) { ctx.fillStyle = '#c0392b'; ctx.fillRect(5, 2, 5, 7); ctx.fillStyle = '#3a3d44'; ctx.fillRect(6, 0, 3, 2); },
  pelle: function (ctx) { ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 5, 9, 2); ctx.fillStyle = '#9aa0a8'; ctx.fillRect(11, 3, 4, 6); },
  cone: function (ctx) { ctx.fillStyle = '#d98324'; ctx.fillRect(6, 2, 4, 7); ctx.fillRect(4, 8, 8, 2); ctx.fillStyle = '#efe6d0'; ctx.fillRect(6, 5, 4, 1); },
  bouteille: function (ctx) { ctx.fillStyle = '#2f6b2a'; ctx.fillRect(5, 3, 4, 6); ctx.fillRect(6, 1, 2, 2); },
};

/* Bulles au-dessus de la tete : la peur, et le temoin qui a tout vu. */
const BULLES = {
  peur: function (ctx) {
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(3, 0, 2, 6); ctx.fillRect(3, 8, 2, 2);
  },
  temoin: function (ctx) {
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(2, 0, 4, 2); ctx.fillRect(5, 2, 2, 2);
    ctx.fillRect(3, 4, 2, 2); ctx.fillRect(3, 8, 2, 2);
  },
};

/* Police pixel 3x5 : 15 bits par glyphe, ligne par ligne. */
const POLICE_PIXEL = {
  'A': '010101111101101', 'B': '110101110101110', 'C': '011100100100011', 'D': '110101101101110',
  'E': '111100110100111', 'F': '111100110100100', 'G': '011100101101011', 'H': '101101111101101',
  'I': '111010010010111', 'J': '001001001101010', 'K': '101101110101101', 'L': '100100100100111',
  'M': '101111111101101', 'N': '110101101101101', 'O': '010101101101010', 'P': '110101110100100',
  'Q': '010101101110011', 'R': '110101110101101', 'S': '011100010001110', 'T': '111010010010010',
  'U': '101101101101011', 'V': '101101101101010', 'W': '101101111111101', 'X': '101101010101101',
  'Y': '101101010010010', 'Z': '111001010100111',
  '0': '010101101101010', '1': '010110010010111', '2': '110001010100111', '3': '110001010001110',
  '4': '101101111001001', '5': '111100110001110', '6': '011100110101010', '7': '111001010010010',
  '8': '010101010101010', '9': '010101011001110',
  ' ': '000000000000000', '.': '000000000000010', ',': '000000000010100', ':': '000010000010000',
  '!': '010010010000010', '?': '110001010000010', '-': '000000111000000', '/': '001001010100100',
  '$': '011110011011110', '+': '000010111010000', '*': '101010111010101', '(': '010100100100010',
  ')': '010001001001010', "'": '010010000000000', '"': '101101000000000', '%': '101001010100101',
  'É': '111100110100111', 'È': '111100110100111', 'À': '010101111101101', 'Ç': '011100100100011',
  '★': '010111111011101', '♥': '101111111010000',
  '>': '100010001010100', '<': '001010100010001', '·': '000000010000000', '=': '000111000111000',
  '|': '010010010010010', '_': '000000000000111', '[': '110100100100110', ']': '011001001001011',
};
