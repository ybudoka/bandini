/* Bandini — sprites : donnees seulement (palettes + grilles), et peintres de tuiles.

   Convention : le personnage fait 12x16, ancre au pied (6, 15). Trois vues
   dessinees (bas, haut, cote) ; « gauche » est le miroir de « cote ».
   Chaque pose a 3 images : repos, pas 1, pas 2 (cycle 0 1 0 2). */

const SPRITES = {
  joueur: {
    w: 12, h: 16, ancre: [6, 15],
    pal: { k: '#101018', s: '#e8b088', h: '#3a2a1a', c: '#c0392b', p: '#2a2a3a', o: '#ffffff', b: '#5a3a1a' },
    swaps: ['c', 'h', 's', 'p'],
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
    '=': function (ctx, v, T) { asphalte(ctx, v, T); ctx.fillStyle = '#e8e6de'; for (let x = 1; x < T; x += 5) ctx.fillRect(x, 0, 3, T); },
    ':': function (ctx, v, T) { asphalte(ctx, v, T); ctx.fillStyle = '#e8e6de'; for (let y = 1; y < T; y += 5) ctx.fillRect(0, y, T, 3); },
    'p': function (ctx, v, T) { asphalte(ctx, v, T); ctx.fillStyle = '#d9d6cc'; ctx.fillRect(0, 0, 1, T); },
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
  ombre: { w: 12, h: 6, ancre: [6, 3], r: 0, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(0,0,0,0.30)'; ctx.fillRect(2, 0, 8, 6); ctx.fillRect(0, 1, 12, 4);
  } },
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
};
