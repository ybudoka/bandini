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

/* La fille de la Brume : 12x16 comme tout le monde, mais une SILHOUETTE a
   elle. Un echange de palette ne suffisait pas — de loin, sous la teinte de
   nuit, elle etait un passant rose de plus (retour de Martin : « on ne les
   distingue plus, elles sont trop pareilles que tout le monde »). Ce qui se
   reconnait a douze pixels de large, ce n'est pas une couleur, c'est un
   contour : la jupe s'evase PLUS LARGE QUE LES EPAULES (la seule du jeu),
   les jambes sont nues entre l'ourlet et les talons, et les cheveux tombent
   de chaque cote du cou. Rien de plus ne se montre : c'est un contour, pas
   une tenue.

   Meme alphabet que `joueur` (`c` le bustier, `p` la jupe, `h` les cheveux,
   `s` la peau, `b` les talons) : les echanges du catalogue marchent pareil.
   Pas de pose de coup — elle ne frappe personne ; `couche` est celle du
   joueur, un corps par terre est un corps par terre. */
SPRITES.racoleuse = {
  w: 12, h: 16, ancre: [6, 15],
  pal: { k: '#101018', s: '#f0c098', h: '#f2d27a', c: '#ff3d8e', p: '#c2185b', o: '#ffffff', b: '#1a1a22' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..khsssshk..', '..khksskhk..', '..kcccccck..',
       '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '.kppppppppk.', 'kppppppppppk', '..kssk.kssk.', '..kssk.kssk.', '..kbbk.kbbk.'],
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..khsssshk..', '..khksskhk..', '..kcccccck..',
       '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '.kppppppppk.', 'kppppppppppk', '..kssk.kssk.', '..kssk..ksk.', '..kbbk..kbk.'],
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..khsssshk..', '..khksskhk..', '..kcccccck..',
       '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '.kppppppppk.', 'kppppppppppk', '..kssk.kssk.', '..ksk..kssk.', '..kbk..kbbk.'],
    ],
    haut: [
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..kcccccck..',
       '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '.kppppppppk.', 'kppppppppppk', '..kssk.kssk.', '..kssk.kssk.', '..kbbk.kbbk.'],
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..kcccccck..',
       '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '.kppppppppk.', 'kppppppppppk', '..kssk.kssk.', '..kssk..ksk.', '..kbbk..kbk.'],
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..kcccccck..',
       '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '.kppppppppk.', 'kppppppppppk', '..kssk.kssk.', '..ksk..kssk.', '..kbk..kbbk.'],
    ],
    cote: [
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhssosk..', '..khhssssk..', '..khhsssk...', '..khhkssk...', '..khkcccck..',
       '...kcccck...', '...kcckck...', '...kccksk...', '..kppppppk..', '.kpppppppk..', '...ksksk....', '...kbk.kbk..', '...kkk.kkk..'],
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhssosk..', '..khhssssk..', '..khhsssk...', '..khhkssk...', '..khkcccck..',
       '...kcccck...', '...kcckck...', '...kccksk...', '..kppppppk..', '.kpppppppk..', '..ksk..ksk..', '..kbk..kbk..', '..kkk..kkk..'],
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhssosk..', '..khhssssk..', '..khhsssk...', '..khhkssk...', '..khkcccck..',
       '...kcccck...', '...kcckck...', '...kccksk...', '..kppppppk..', '.kpppppppk..', '....kssk....', '....kbbk....', '....kkkk....'],
    ],
    couche: [
      ['............', '............', '............', '............', '............', '............', '............',
       '..kkkkkk....', '.kpppppkkkk.', 'kppppppccccs', 'kppppppcccck', '.kpppppkccsk', '..kbbkk.kkk.', '..kkk.......', '............', '............'],
    ],
  },
};

/* L'homme-sandwich : 14 x 16, deux pixels plus large que tout le monde, et
   c'est la pancarte qui les prend. Meme lecon que la fille de la Brume : a
   douze pixels de large, une couleur ne distingue personne — un CONTOUR, oui.
   La pancarte deborde des epaules, elle cache les bras et le haut des jambes,
   elle porte une bande rouge et deux lignes d'ecriture qu'on ne lit pas mais
   qu'on reconnait. De cote, c'est un « A » de deux planches qui l'encadre.

   Meme alphabet que `joueur` : `c` est la PANCARTE (pas un chandail — le
   catalogue lui donne un creme), `p` le pantalon, `h`, `s`, `b` comme
   d'habitude ; `r` la bande rouge et `d` l'encre sont a lui et ne se
   troquent pas. Pas de pose de coup : il crie, il ne frappe pas ; `couche`
   est celle du joueur, un corps par terre est un corps par terre. */
SPRITES.homme_sandwich = {
  w: 14, h: 16, ancre: [7, 15],
  pal: { k: '#101018', s: '#e8b088', h: '#4a3320', c: '#f4ead2', p: '#4a4a5a', o: '#ffffff', b: '#3a2a1a', r: '#c0392b', d: '#1a1a22' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['.....kkkk.....', '....khhhhk....', '...khhhhhhk...', '...khsssshk...', '...ksossosk...', '...kssssssk...', '....kssssk....', '.kkkkkkkkkkkk.',
       '.krrrrrrrrrrk.', '.kcdcddcdcdck.', '.kccdcdccdcck.', '.kcccccccccck.', '.kkkkkkkkkkkk.', '...kppk.kppk..', '...kbbk.kbbk..', '...kkkk.kkkk..'],
      ['.....kkkk.....', '....khhhhk....', '...khhhhhhk...', '...khsssshk...', '...ksossosk...', '...kssssssk...', '....kssssk....', '.kkkkkkkkkkkk.',
       '.krrrrrrrrrrk.', '.kcdcddcdcdck.', '.kccdcdccdcck.', '.kcccccccccck.', '.kkkkkkkkkkkk.', '...kppk..kpk..', '...kbbk..kbk..', '...kkkk..kk...'],
      ['.....kkkk.....', '....khhhhk....', '...khhhhhhk...', '...khsssshk...', '...ksossosk...', '...kssssssk...', '....kssssk....', '.kkkkkkkkkkkk.',
       '.krrrrrrrrrrk.', '.kcdcddcdcdck.', '.kccdcdccdcck.', '.kcccccccccck.', '.kkkkkkkkkkkk.', '...kpk..kppk..', '...kbk..kbbk..', '...kk..kkkk...'],
    ],
    haut: [
      ['.....kkkk.....', '....khhhhk....', '...khhhhhhk...', '...khhhhhhk...', '...khhhhhhk...', '...khsssshk...', '....kssssk....', '.kkkkkkkkkkkk.',
       '.krrrrrrrrrrk.', '.kcdcddcdcdck.', '.kccdcdccdcck.', '.kcccccccccck.', '.kkkkkkkkkkkk.', '...kppk.kppk..', '...kbbk.kbbk..', '...kkkk.kkkk..'],
      ['.....kkkk.....', '....khhhhk....', '...khhhhhhk...', '...khhhhhhk...', '...khhhhhhk...', '...khsssshk...', '....kssssk....', '.kkkkkkkkkkkk.',
       '.krrrrrrrrrrk.', '.kcdcddcdcdck.', '.kccdcdccdcck.', '.kcccccccccck.', '.kkkkkkkkkkkk.', '...kppk..kpk..', '...kbbk..kbk..', '...kkkk..kk...'],
      ['.....kkkk.....', '....khhhhk....', '...khhhhhhk...', '...khhhhhhk...', '...khhhhhhk...', '...khsssshk...', '....kssssk....', '.kkkkkkkkkkkk.',
       '.krrrrrrrrrrk.', '.kcdcddcdcdck.', '.kccdcdccdcck.', '.kcccccccccck.', '.kkkkkkkkkkkk.', '...kpk..kppk..', '...kbk..kbbk..', '...kk..kkkk...'],
    ],
    cote: [
      ['.....kkkk.....', '....khhhhk....', '....khhhhhk...', '....khssosk...', '....khssssk...', '....khsssk....', '.....kssk.....', '..kkkkkkkkkk..',
       '..krkcccckrk..', '..kckcckckck..', '..kckcckskck..', '..kckppppkck..', '..kkkkkkkkkk..', '....kpkkpk....', '....kbk.kbk...', '....kkk.kkk...'],
      ['.....kkkk.....', '....khhhhk....', '....khhhhhk...', '....khssosk...', '....khssssk...', '....khsssk....', '.....kssk.....', '..kkkkkkkkkk..',
       '..krkcccckrk..', '..kckcckckck..', '..kckcckskck..', '..kckppppkck..', '..kkkkkkkkkk..', '...kpk..kpk...', '...kbk..kbk...', '...kkk..kkk...'],
      ['.....kkkk.....', '....khhhhk....', '....khhhhhk...', '....khssosk...', '....khssssk...', '....khsssk....', '.....kssk.....', '..kkkkkkkkkk..',
       '..krkcccckrk..', '..kckcckckck..', '..kckcckskck..', '..kckppppkck..', '..kkkkkkkkkk..', '.....kppk.....', '.....kbbk.....', '.....kkkk.....'],
    ],
    couche: [
      ['..............', '..............', '..............', '..............', '..............', '..............', '..............',
       '...kkkkkk.....', '..kpppppkkkk..', '.kppppppccccs.', '.kppppppcccck.', '..kpppppkccsk.', '...kbbkk.kkk..', '...kkk........', '..............', '..............'],
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

/* --- Trois sortes de gens, pas trois palettes -------------------------------

   ⚠️ La ville avait 24 archetypes pour QUATRE corps : vingt et un portaient
   celui du joueur avec un echange de palette. Le depot a deja paye ce defaut
   une fois — les filles de la Brume « n'etaient qu'un echange de palette sur
   le corps commun », et on ne les distinguait plus de personne.

   La regle : UNE SORTE = UN CORPS + UNE ROUTINE. Le corps est ici ; la
   routine est dans `entites.js`, accrochee au `metier` de la fiche. Sans la
   routine, ce ne serait qu'un costume de plus. */
// ⚠️ La GUITARE en travers du corps (`g`) : a douze pixels, c'est elle
// qui le nomme, pas sa palette.
SPRITES.musicien = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#e8b088', h: '#3a2a1a', c: '#6b4b8a', p: '#2a2a3a', o: '#ffffff', g: '#c98d3a', b: '#3a2a1a' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kkkkkk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '.kcggggggck.', '.kcggggggck.', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '.kcggggggck.', '.kcggggggck.', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    haut: [
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '.kcccccccck.', '.kcgggggck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '.kcccccccck.', '.kcgggggck..', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    cote: [
      ['...kkkkkk...', '...khhhhhk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kccccck..', '..kcgggggk..', '..kcgggggk..', '...kccccck..', '....kppppk..', '...kppk.kk..', '...kkk......'],
      ['...kkkkkk...', '...khhhhhk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kccccck..', '..kcgggggk..', '..kcgggggk..', '...kccccck..', '....kppppk..', '....kpk.kk..', '....kk......'],
    ],
  },
};
// Le mime : chapeau melon, visage blanc, chandail raye. Trois formes
// qu'aucun autre corps de la ville n'a.
SPRITES.amuseur = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#e8b088', h: '#2a2a2a', c: '#efe6d0', p: '#1a1a22', o: '#ffffff', d: '#1a1a22', b: '#1a1a22' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kkkkkk...', '..kkkkkkkk..', '...koooook..', '...kokkook..', '...koooook..', '....kook....', '.kkcccccckk.', 'kckdcdcdckck', 'kckcdcdcdckc', '.kkcdcdckkk.', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..kkkkkkkk..', '...koooook..', '...kokkook..', '...koooook..', '....kook....', '.kckccccckk.', '.kkdcdcdck..', 'kckcdcdcdck.', '.kkcdcdckkk.', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    haut: [
      ['...kkkkkk...', '..kkkkkkkk..', '...khhhhhk..', '...khhhhhk..', '...khhhhhk..', '....kook....', '.kkcccccckk.', 'kckdcdcdckck', 'kckcdcdcdckc', '.kkcdcdckkk.', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..kkkkkkkk..', '...khhhhhk..', '...khhhhhk..', '...khhhhhk..', '....kook....', '.kckccccckk.', '.kkdcdcdck..', 'kckcdcdcdck.', '.kkcdcdckkk.', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    cote: [
      ['...kkkkkk...', '..kkkkkkkk..', '...koooook..', '...kokkook..', '...kooook...', '....kok.....', '..kcccccck..', '.kcdcdcdck..', '.kcdcdcdck..', '..kcdcdck...', '...kppppk...', '..kppk.kk...', '..kkk.......'],
      ['...kkkkkk...', '..kkkkkkkk..', '...koooook..', '...kokkook..', '...kooook...', '....kok.....', '..kcccccck..', '.kcdcdcdck..', '.kcdcdcdck..', '..kcdcdck...', '...kppppk...', '...kpk.kk...', '...kk.......'],
    ],
  },
};
// ⚠️ DEUX images qui ne sont pas une marche : manteau ferme, manteau
// OUVERT. C'est son geste, et le moteur choisit la deuxieme (voir
// `majSortes`).
SPRITES.exhibitionniste = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#e8b088', h: '#4a3320', c: '#7a5a3a', p: '#2a2a3a', o: '#ffffff', b: '#3a3a4a' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kkkkkk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '...kbbbbk...', '...kk..kk...'],
      ['...kkkkkk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '.kckssssckk.', '.kcksssskck.', '.kcksssskck.', '.kckssssckc.', '.kckssssckc.', '..kk.bb.kk..', '..kk....kk..'],
    ],
    haut: [
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '...kbbbbk...', '...kk..kk...'],
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '...kbbbbk...', '...kk..kk...'],
    ],
    cote: [
      ['...kkkkkk...', '...khhhhhk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kccccck..', '...kccccck..', '...kccccck..', '...kccccck..', '...kccccck..', '....kbbbk...', '....kk.k....'],
      ['...kkkkkk...', '...khhhhhk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kccccck..', '...kccccck..', '...kccccck..', '...kccccck..', '...kccccck..', '....kbbbk...', '....k.kk....'],
    ],
  },
};

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

/* --- M9, le parc automobile ---------------------------------------------------

   ⚠️ Vu d'en haut, un char est un TOIT. C'est ce qui decide de ces quatre
   dessins : ce n'est pas le pare-brise qui nomme un vehicule a douze pixels de
   large, c'est ce qu'il porte sur le dos — les nervures d'une caisse, les
   trappes d'un autobus, une croix rouge, un bras de levage et son crochet.
   Chacun est plus long que l'auto, et la marge reste la meme (longueur + 4,
   largeur + 2) : le sprite depasse de deux pixels pour les roues. */
// Une caisse a nervures et une cabine : c'est la caisse qui le nomme d'en haut.
SPRITES.camion = {
  w: 44, h: 18, ancre: [22, 9], rotations: 32,
  pal: { k: '#101018', c: '#7f8c8d', b: '#8d99a6', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', s: '#565c63' },
  swaps: ['c'], poses: { base: [[
    '.....rrrrr.....rrrrr.............rrrrr......',
    '.....rrrrr.....rrrrr.............rrrrr......',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '.kbbbbbbbbbbbbbbbbbbbbbbbbbbbkccccccccccccc.',
    '.kbbbbbkbbbbbkbbbbbkbbbbbkbbbkccccccvvvcccc.',
    '.kttbbbkbbbbbkbbbbbkbbbbbkbbbkccccccvvvcllc.',
    '.kttbbbkbbbbbkbbbbbkbbbbbkbbbkccccccvvvcllc.',
    '.kbbbbbkbbbbbkbbbbbkbbbbbkbbbkccccccvvvcccc.',
    '.kbbbbbkbbbbbkbbbbbkbbbbbkbbbkssssscvvvcccc.',
    '.kbbbbbkbbbbbkbbbbbkbbbbbkbbbkssssscvvvcccc.',
    '.kbbbbbkbbbbbkbbbbbkbbbbbkbbbkccccccvvvcccc.',
    '.kttbbbkbbbbbkbbbbbkbbbbbkbbbkccccccvvvcllc.',
    '.kttbbbkbbbbbkbbbbbkbbbbbkbbbkccccccvvvcllc.',
    '.kbbbbbkbbbbbkbbbbbkbbbbbkbbbkccccccvvvcccc.',
    '.kbbbbbbbbbbbbbbbbbbbbbbbbbbbkccccccccccccc.',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '.....rrrrr.....rrrrr.............rrrrr......',
    '.....rrrrr.....rrrrr.............rrrrr......',
  ]] },
};
// Le plus long du parc — cinq cercles de collision, et un toit a trappes.
SPRITES.autobus = {
  w: 52, h: 18, ancre: [26, 9], rotations: 32,
  pal: { k: '#101018', c: '#2980b9', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', s: '#1f5f8b' },
  swaps: ['c'], poses: { base: [[
    '......rrrrr...........rrrrr.............rrrrr.......',
    '......rrrrr...........rrrrr.............rrrrr.......',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '.kcvvvkvvvvvkvvvvvkvvvvvkvvvvvkvvvvvkvvvvvkkcccccck.',
    '.kcccccccccccccccccccccccccccccccccccccccckkvvvvcck.',
    '.kttcccccccccccccccccccccccccccccccccccccckkvvvvllk.',
    '.kttccssssssssssscccccsssssssssssccccccccckkvvvvllk.',
    '.kccccssssssssssscccccsssssssssssccccccccckkvvvvcck.',
    '.kccccssssssssssscccccsssssssssssccccccccckkvvvvcck.',
    '.kccccssssssssssscccccsssssssssssccccccccckkvvvvcck.',
    '.kccccssssssssssscccccsssssssssssccccccccckkvvvvcck.',
    '.kttccssssssssssscccccsssssssssssccccccccckkvvvvllk.',
    '.kttcccccccccccccccccccccccccccccccccccccckkvvvvllk.',
    '.kcccccccccccccccccccccccccccccccccccccccckkvvvvcck.',
    '.kcvvvkvvvvvkvvvvvkvvvvvkvvvvvkvvvvvkvvvvvkkcccccck.',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '......rrrrr...........rrrrr.............rrrrr.......',
    '......rrrrr...........rrrrr.............rrrrr.......',
  ]] },
};
// ⚠️ La croix se lit d'EN HAUT : vue de dessus, c'est elle qui la nomme.
SPRITES.ambulance = {
  w: 36, h: 17, ancre: [18, 8], rotations: 32,
  pal: { k: '#101018', c: '#ffffff', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', x: '#e0312a', y: '#2f6fd8', s: '#f39c12' },
  swaps: ['c'], poses: { base: [[
    '.....rrrrr................rrrrr.....',
    '.....rrrrr................rrrrr.....',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '.kcvvvvvvvvvvvvvvvvvkkcccccccccccck.',
    '.kcccccccccccccccccckkcvvvcyyyyccck.',
    '.kttccccccxxxxcccccckkcvvvcyyyyccck.',
    '.kttssssssxxxxsssssskkcvvvcccccllck.',
    '.kccccccxxxxxxxxcccckkcvvvcccccllck.',
    '.kccccccxxxxxxxxcccckkcvvvcccccccck.',
    '.kccccccxxxxxxxxcccckkcvvvcccccllck.',
    '.kttssssssxxxxsssssskkcvvvcccccllck.',
    '.kttccccccxxxxcccccckkcvvvcyyyyccck.',
    '.kcccccccccccccccccckkcvvvcyyyyccck.',
    '.kcvvvvvvvvvvvvvvvvvkkcccccccccccck.',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '.....rrrrr................rrrrr.....',
    '.....rrrrr................rrrrr.....',
  ]] },
};
// Le bras couche sur le plateau, et le crochet qui depasse a l'arriere.
SPRITES.remorqueuse = {
  w: 40, h: 17, ancre: [20, 8], rotations: 32,
  pal: { k: '#101018', c: '#d98324', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', h: '#6b7078', p: '#c9cdd4', y: '#f39c12', s: '#3a3d44' },
  swaps: ['c'], poses: { base: [[
    '.......rrrrr.....rrrrr........rrrrr.....',
    '.......rrrrr.....rrrrr........rrrrr.....',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '.kcccccccccccccccccccccckkccccyyyycccck.',
    '.kcccccccccccccccccccccckkvvvcyyyycccck.',
    '.kttccsssssssssssssssssskkvvvcccclllcck.',
    '.kttcccccccccccccccccccckkvvvcccclllcck.',
    '.kpppphhhhhhhhhhhhhhhhhhkkvvvccccccccck.',
    '.k..ppkkkkkkkkkkkkkkkkkhkkvvvccccccccck.',
    '.kpppphhhhhhhhhhhhhhhhhhkkvvvccccccccck.',
    '.kttcccccccccccccccccccckkvvvcccclllcck.',
    '.kttccsssssssssssssssssskkvvvcccclllcck.',
    '.kcccccccccccccccccccccckkvvvccccccccck.',
    '.kcccccccccccccccccccccckkcccccccccccck.',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '.......rrrrr.....rrrrr........rrrrr.....',
    '.......rrrrr.....rrrrr........rrrrr.....',
  ]] },
};


/* --- M9, le haut de gamme : deux chars qu'on vole expres ----------------------

   ⚠️ Ils doivent s'opposer JUSQUE DANS LE DESSIN, sinon ce sont deux lignes de
   catalogue de plus. Le sport est le seul char du parc dont l'habitacle est
   OUVERT — un trou dans le toit, deux sieges dedans ; le luxe est le seul dont
   le toit est plein, lisse et cerne de chrome. Vu d'en haut, c'est tout ce
   qu'on a pour les nommer, et ca suffit. */
// ⚠️ Vu d'en haut, ce qui nomme un coupe sport c'est LE TROU : decapotable,
// on voit les deux sieges. Aucun autre char du parc n'a d'habitacle ouvert.
SPRITES.sport = {
  w: 30, h: 15, ancre: [15, 7], rotations: 32,
  pal: { k: '#101018', c: '#c0392b', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', i: '#2a2028', u: '#6b4b2c', s: '#8e2b20' },
  swaps: ['c'], poses: { base: [[
    '....rrrrr............rrrrr....',
    '....rrrrr............rrrrr....',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '.kcccccccccccccccccccccccccck.',
    '.kccccccccckkkkkkkkkkvvvcccck.',
    '.kttccccccckiiiiiiiikvvvclllk.',
    '.kttssssssckiuuuiuuukvvvclllk.',
    '.kccccccccckiuuuiuuukvvvcccck.',
    '.kccssssssckiuuuiuuukvvvcccck.',
    '.kttccccccckiiiiiiiikvvvclllk.',
    '.kttccccccckkkkkkkkkkvvvclllk.',
    '.kcccccccccccccccccccccccccck.',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '....rrrrr............rrrrr....',
    '....rrrrr............rrrrr....',
  ]] },
};
// L'inverse exact du sport : rien ne depasse, rien ne s'ouvre. Un long
// rectangle sombre, deux vitres fines et du chrome tout autour.
SPRITES.luxe = {
  w: 36, h: 17, ancre: [18, 8], rotations: 32,
  pal: { k: '#101018', c: '#101014', v: '#5f7f99', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', m: '#b9bcc4', s: '#26262e' },
  swaps: ['c'], poses: { base: [[
    '.....rrrrr................rrrrr.....',
    '.....rrrrr................rrrrr.....',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '.kcmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmck.',
    '.kcccccccccccccccccccccccccccccccck.',
    '.ktttcccvvvcccccccccccccvvvccclllck.',
    '.ktttcccvvvccsssssssssccvvvccclllck.',
    '.kccccccvvvccsssssssssccvvvcmmcccck.',
    '.kccccccvvvccsssssssssccvvvcmmcccck.',
    '.kccccccvvvccsssssssssccvvvcmmcccck.',
    '.ktttcccvvvccsssssssssccvvvccclllck.',
    '.ktttcccvvvcccccccccccccvvvccclllck.',
    '.kcccccccccccccccccccccccccccccccck.',
    '.kcmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmck.',
    '..kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..',
    '.....rrrrr................rrrrr.....',
    '.....rrrrr................rrrrr.....',
  ]] },
};

/* Peintres de tuiles 16x16 : (ctx, variante, T). Le bruit vient de la variante,
   un entier stable par position (hash2), pour que la ville ne scintille pas. */
const TUILES = (function () {
  // ⚠️ Un vrai melange, pas une suite lineaire. Avec `v * A + i * B`, deux
  // points voisins (i, i+1) avancent du MEME pas en x et en y : les grains se
  // rangent en diagonale, la meme diagonale dans chaque tuile, et un grand
  // stationnement se met a ressembler a du papier peint. Ca se voyait sur
  // toute la ville — sauf qu'ailleurs il n'y a jamais vingt tuiles de suite
  // du meme glyphe pour le montrer.
  function bruit(v, i) { return hash2(v, i) % 1000 / 1000; }
  function plein(ctx, c, T) { ctx.fillStyle = c; ctx.fillRect(0, 0, T, T); }
  function points(ctx, v, T, couleur, n, i0) {
    ctx.fillStyle = couleur;
    for (let i = 0; i < n; i++) {
      ctx.fillRect(Math.floor(bruit(v, i0 + i) * T), Math.floor(bruit(v, i0 + i + 50) * T), 1, 1);
    }
  }
  function asphalte(ctx, v, T) { plein(ctx, '#2f3138', T); points(ctx, v, T, '#383a42', 10, 0); points(ctx, v, T, '#26282e', 6, 100); }

  /* --- Le stationnement ---------------------------------------------------

     L'asphalte d'un stationnement n'est pas celui de la rue : il n'est jamais
     refait, alors il est plus pale, plus gris, tache d'huile la ou les autos
     s'arretent et fendu ailleurs. C'est cette usure — autant que les lignes —
     qui fait qu'on le reconnait d'un coup d'oeil.

     ⚠️ Aucune usure ne touche le BORD de la tuile : une tache ou une fissure
     coupee net au 16e pixel dessine la grille, et la ville entiere devient un
     quadrillage. */
  function bitume(ctx, v, T) {
    plein(ctx, '#35373d', T);
    points(ctx, v, T, '#3d3f46', 14, 0);
    points(ctx, v, T, '#2b2d33', 10, 100);
  }

  function tacheDHuile(ctx, v, T) {
    const cx = 5 + Math.floor(bruit(v, 11) * 4), cy = 5 + Math.floor(bruit(v, 12) * 4);
    ctx.fillStyle = 'rgba(16,16,20,0.26)';
    ctx.fillRect(cx - 2, cy - 1, 5, 3); ctx.fillRect(cx - 1, cy - 2, 3, 5);
    ctx.fillStyle = 'rgba(16,16,20,0.14)';
    ctx.fillRect(cx - 3, cy, 7, 1); ctx.fillRect(cx, cy - 3, 1, 7);
  }

  function fissure(ctx, v, T) {
    ctx.fillStyle = '#292b31';
    let x = 3 + Math.floor(bruit(v, 21) * 9);
    for (let y = 2; y < T - 2; y += 2) {
      ctx.fillRect(x, y, 1, 2);
      x += bruit(v, 30 + y) < 0.5 ? -1 : 1;
      x = Math.max(2, Math.min(T - 3, x));
    }
  }

  /** Une ligne de peinture usee : jamais pleine, jamais deux fois la meme. */
  function peinture(ctx, v, x, y, l, h, i0) {
    ctx.fillStyle = '#c4c1b6';
    ctx.fillRect(x, y, l, h);
    ctx.fillStyle = 'rgba(53,55,61,0.55)';       // l'asphalte qui remonte
    const long = Math.max(l, h);
    for (let i = 0; i < 2; i++) {
      const d = Math.floor(bruit(v, i0 + i) * (long - 2)) + 1;
      if (l > h) ctx.fillRect(x + d, y, 1, h); else ctx.fillRect(x, y + d, l, 1);
    }
  }

  /** Un butoir de beton au fond de la case : le bloc qui arrete la roue.
      Vu d'en haut, une barre claire et son ombre portee.

      ⚠️ C'est LUI qui ferme la case, pas une ligne peinte : une ligne de nez
      fait toute la largeur de la tuile, alors elle se soude a celle des cases
      voisines et la rangee devient un trait continu d'un bout a l'autre du
      terrain. Le butoir, lui, laisse quatre pixels de chaque cote — et on
      compte les cases une a une. */
  function butoir(ctx, T, cote) {
    const d = 4;                                  // a un quart de tuile du nez
    ctx.fillStyle = '#86837a';
    if (cote === 'N') { ctx.fillRect(4, d, 8, 2); ctx.fillStyle = '#5a5852'; ctx.fillRect(4, d + 2, 8, 1); }
    else if (cote === 'S') { ctx.fillRect(4, T - d - 2, 8, 2); ctx.fillStyle = '#5a5852'; ctx.fillRect(4, T - d, 8, 1); }
    else if (cote === 'O') { ctx.fillRect(d, 4, 2, 8); ctx.fillStyle = '#5a5852'; ctx.fillRect(d + 2, 4, 1, 8); }
    else { ctx.fillRect(T - d - 2, 4, 2, 8); ctx.fillStyle = '#5a5852'; ctx.fillRect(T - d, 4, 1, 8); }
  }

  /** Une case de stationnement. `cote` = ou pointe le NEZ de l'auto.

      La variante vient de Monde.varianteDeCase :
      bit 0 = tuile du FOND (c'est elle qui porte le butoir),
      bit 1 = derniere case de la rangee (elle ferme son cote),
      bits 2 et au-dela = l'usure (huit), stable par position.

      ⚠️ Chaque case ne peint QUE sa ligne de gauche (ou du haut) : deux cases
      voisines qui peignent chacune leurs deux cotes font une ligne double,
      deux fois trop grasse, et la rangee ressemble a une echelle. */
  function caseAuto(ctx, v, T, cote) {
    const fond = (v & 1) !== 0, derniere = (v & 2) !== 0, usure = v >> 2;
    bitume(ctx, v, T);
    if (usure === 3 || usure === 5) tacheDHuile(ctx, v, T);   // l'huile tombe ou l'on se gare
    else if (usure === 7) fissure(ctx, v, T);
    const vertical = cote === 'N' || cote === 'S';
    if (vertical) {
      peinture(ctx, v, 0, 0, 1, T, 40);
      if (derniere) peinture(ctx, v, T - 1, 0, 1, T, 44);
    } else {
      peinture(ctx, v, 0, 0, T, 1, 40);
      if (derniere) peinture(ctx, v, 0, T - 1, T, 1, 44);
    }
    if (fond) butoir(ctx, T, cote);
  }
  function trottoir(ctx, v, T) {
    plein(ctx, '#9a9689', T);
    ctx.fillStyle = '#8b877b'; ctx.fillRect(0, 0, T, 1); ctx.fillRect(0, 0, 1, T);
    ctx.fillStyle = '#a5a194'; ctx.fillRect(1, 1, T - 2, 1);
    points(ctx, v, T, '#8f8b7f', 5, 7);
  }
  /* La rampe : DEUX tuiles, le pied et la levre. La variante porte le sens ou
     ca grimpe (0 est, 1 sud, 2 ouest, 3 nord) et laquelle des deux moities on
     peint — v = sens * 2 + levre (voir `Monde.varianteDeRampe`).

     ⚠️ Elle se dessine TOUJOURS grimpant vers l'est, puis on tourne le canvas :
     quatre pentes dessinees a la main, ce serait quatre occasions de les
     dessiner differemment.

     ⚠️ C'est le DEGRADE qui fait la pente ; les chevrons ne font que la nommer.
     L'ancienne rampe n'avait ni l'un ni l'autre — quatre tirets jaunes plats,
     que Martin a pris pour un marquage efface, et il avait raison. */
  const BOIS_RAMPE = ['#5a4530', '#6a5138', '#7a5e40', '#8a6b48',
                      '#9a7850', '#aa8558', '#b89163', '#c79d6d'];
  function rampe(ctx, v, T) {
    const levre = (v & 1) === 1;
    asphalte(ctx, v, T);
    ctx.save();
    ctx.translate(T / 2, T / 2);
    ctx.rotate(((v >> 1) & 3) * Math.PI / 2);
    ctx.translate(-T / 2, -T / 2);
    for (let i = 0; i < 4; i++) {
      ctx.fillStyle = BOIS_RAMPE[(levre ? 4 : 0) + i];
      ctx.fillRect(i * 4, 1, 4, T - 2);
    }
    // Les joues : une caisse posee sur l'asphalte, pas une peinture au sol.
    ctx.fillStyle = 'rgba(0,0,0,0.45)';
    ctx.fillRect(0, 0, T, 1);
    ctx.fillRect(0, T - 1, T, 1);
    // Les chevrons montrent la montee — jaunes, comme tout le marquage du jeu.
    ctx.fillStyle = '#d8b83a';
    for (const x0 of [2, 9]) {
      for (let k = 0; k < 4; k++) {
        ctx.fillRect(x0 + k, 3 + k, 1, 2);
        ctx.fillRect(x0 + k, T - 5 - k, 1, 2);
      }
    }
    if (levre) {
      // L'arete d'ou l'on decolle, et son ombre juste derriere : sans elle, la
      // planche a l'air posee a plat.
      ctx.fillStyle = 'rgba(0,0,0,0.35)';
      ctx.fillRect(T - 3, 1, 1, T - 2);
      ctx.fillStyle = '#fff3b0';
      ctx.fillRect(T - 2, 1, 2, T - 2);
    } else {
      ctx.fillStyle = 'rgba(0,0,0,0.45)';
      ctx.fillRect(0, 1, 1, T - 2);
    }
    ctx.restore();
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
  /* --- Les trois clotures -------------------------------------------------

     ⚠️ Le SENS vient des voisines (`varianteDeCloture`, monde.js) : `v` est le
     masque des quatre cotes ou la cloture continue — 1 nord, 2 est, 4 sud,
     8 ouest. Sans lui, les trois peintres ne savaient dessiner qu'est-ouest,
     et une cloture qui descend du nord au sud etait une PILE DE PANNEAUX VUS
     DE FACE. « Les clotures qui sont nord-sud ne sont pas dans le bon sens » :
     c'etait exactement ca.

     Le dessin se fait en BRAS — un bras du centre vers chaque cote ou la
     cloture continue — et tout passe par `trait`/`bloc`, qui echangent les
     axes selon le sens. Les trois clotures partagent donc la MEME geometrie et
     ne different que par leur palette et par ce qu'elles portent en haut :
     sinon on corrige un sens sur une cloture et on recommence a la prochaine.

     ⚠️ Elles doivent aussi se distinguer d'un coup d'oeil, parce qu'elles ne
     veulent pas dire la meme chose : le grillage et le bois s'enjambent, le
     barbele ne se passe pas. Le grillage est clair et maille ; le bois est
     brun, en planches serrees ; le barbele est sombre, ses poteaux montent
     plus haut et il porte ses trois fils et leurs epines. */

  /** Un rectangle dans le repere du brin : `u` le long de la cloture, `w` en
      travers. En est-ouest c'est (x, y) ; en nord-sud, les deux s'echangent —
      et c'est tout le correctif. */
  function bloc(ctx, sens, u, w, lu, lw) {
    if (sens === 'h') ctx.fillRect(u, w, lu, lw); else ctx.fillRect(w, u, lw, lu);
  }
  function trait(ctx, sens, u0, u1, w, ep) { bloc(ctx, sens, u0, w, u1 - u0, ep); }

  /** Un brin NORD-SUD : vu d'en haut, on le prend PAR LA TRANCHE.

      ⚠️ Ce n'est pas le brin est-ouest tourne, et c'est tout le propos. La
      camera regarde d'en haut avec juste assez de face au SUD — c'est la regle
      des facades de la ville (« on voit toujours le mur avant, jamais le dos
      d'un toit ») et celle des meubles. Une cloture est-ouest montre donc sa
      hauteur : lisses, maille, poteaux. Une cloture nord-sud n'a rien a
      montrer d'autre que son EPAISSEUR — deux ou trois pixels, un liseré
      d'ombre a l'est, et le chapeau des poteaux. Tournee, elle faisait un
      panneau de sept pixels pose a plat. */
  function brinMince(ctx, u0, u1, style) {
    const e = style.epaisseur, x = 8 - (e >> 1), lg = u1 - u0;
    ctx.fillStyle = style.ombre; ctx.fillRect(x + e, u0, 1, lg);
    ctx.fillStyle = style.planches || style.lisse; ctx.fillRect(x, u0, e, lg);
    // Le barbele garde ses fils : de haut, c'est le brin clair sur le sombre.
    if (style.fils) { ctx.fillStyle = style.fils; ctx.fillRect(x, u0, 1, lg); }
    // Les poteaux ne montrent que leur chapeau, un peu plus large que le brin.
    ctx.fillStyle = style.poteau;
    for (const u of [2, 13]) if (u >= u0 && u < u1) ctx.fillRect(x - 1, u, e + 2, 2);
  }

  /** Un brin de cloture, du centre vers un cote (ou d'un bord a l'autre). */
  function brinDeCloture(ctx, sens, u0, u1, T, style) {
    if (sens === 'v') { brinMince(ctx, u0, u1, style); return; }
    ctx.fillStyle = style.ombre; trait(ctx, sens, u0, u1, 12, 2);        // l'ombre au pied
    ctx.fillStyle = style.lisse;
    trait(ctx, sens, u0, u1, style.rails[0], 1);
    trait(ctx, sens, u0, u1, style.rails[1], 1);
    if (style.planches) {
      // Le bois : des planches EN TRAVERS du brin, jamais deux de la meme
      // hauteur — c'est ce qui se lit comme une palissade et pas comme une
      // barriere de metal.
      ctx.fillStyle = style.planches;
      for (let u = u0; u < u1; u += 3) {
        // ⚠️ La hauteur se tire sur `u` SEUL : le meme brin tourne doit donner
        // le meme dessin tourne — c'est ce que le juge compare, trait par trait.
        const h = 9 + (hash2(u, 7) % 3);
        bloc(ctx, sens, u, 13 - h, 2, h);
      }
    } else {
      ctx.fillStyle = style.maille;
      for (let u = u0; u < u1; u++) {
        for (let w = style.rails[0] + 1; w < style.rails[1]; w++) {
          if ((u + w) % 4 === 0 || (u - w + 16) % 4 === 0) bloc(ctx, sens, u, w, 1, 1);
        }
      }
    }
    if (style.fils) {
      // Les trois fils du barbele, et leurs epines : au-dessus de tout.
      ctx.fillStyle = style.fils;
      for (const w of [1, 3, 5]) trait(ctx, sens, u0, u1, w, 1);
      for (let u = u0 + 1; u < u1; u += 5) {
        bloc(ctx, sens, u, 0, 1, 6);
        bloc(ctx, sens, u - 1, 2, 3, 1);
        bloc(ctx, sens, u - 1, 4, 3, 1);
      }
    }
    ctx.fillStyle = style.poteau;
    for (const u of [2, 13]) if (u >= u0 && u < u1) bloc(ctx, sens, u, style.poteau0, 1, 13 - style.poteau0);
  }

  function clotureTuile(ctx, v, T, style) {
    plein(ctx, '#4f8d3e', T);
    const N = (v & 1) !== 0, E = (v & 2) !== 0, S = (v & 4) !== 0, O = (v & 8) !== 0;
    // ⚠️ Une cloture toute seule se peint quand meme, est-ouest : sans ca,
    // elle n'aurait aucun bras a dessiner et le terrain vague montrerait un
    // trou dans son grillage.
    const seule = !N && !E && !S && !O;
    if (E || seule) brinDeCloture(ctx, 'h', 8, T, T, style);
    if (O || seule) brinDeCloture(ctx, 'h', 0, 8, T, style);
    if (N) brinDeCloture(ctx, 'v', 0, 8, T, style);
    if (S) brinDeCloture(ctx, 'v', 8, T, T, style);
    // Un poteau au centre des que ce n'est pas une ligne droite : au tournant
    // la maille flotterait sans lui, et une cloture qui s'arrete net au milieu
    // d'un terrain aurait l'air coupee au couteau.
    const bras = (N ? 1 : 0) + (E ? 1 : 0) + (S ? 1 : 0) + (O ? 1 : 0);
    if (!(bras === 2 && ((E && O) || (N && S)))) {
      ctx.fillStyle = style.poteau;
      // ⚠️ Le poteau se montre comme ce qui l'entoure : debout quand un bras
      // est-ouest donne sa face, en CHAPEAU quand la tuile est toute en
      // nord-sud. Un poteau de douze pixels au bout d'un brin qui en fait
      // deux, ce n'est plus un poteau, c'est un piquet planté de travers.
      if (E || O || seule) ctx.fillRect(7, style.poteau0, 2, 14 - style.poteau0);
      else ctx.fillRect(8 - (style.epaisseur >> 1) - 1, 7, style.epaisseur + 2, 2);
    }
  }

  //: `epaisseur` : ce qu'il reste d'une cloture quand on la prend par la
  //: tranche (voir `brinMince`). Un grillage est un fil tendu, une palissade a
  //: l'epaisseur de ses planches, le barbele n'est que des fils.
  const CLOTURE_GRILLAGE = { ombre: '#3f7331', lisse: '#9aa0a6', maille: '#7a7d82', poteau: '#b0b6bc',
                     rails: [4, 11], poteau0: 2, epaisseur: 2 };
  const CLOTURE_BOIS = { ombre: '#3f7331', lisse: '#6d5232', planches: '#8a6a42', poteau: '#a3814f',
                 rails: [3, 11], poteau0: 2, epaisseur: 3 };
  const CLOTURE_BARBELE = { ombre: '#3a6c2d', lisse: '#5d5852', maille: '#6b655c', poteau: '#7d766a',
                    fils: '#d8d2c4', rails: [6, 11], poteau0: 0, epaisseur: 2 };

  /* --- Les toits ----------------------------------------------------------

     ⚠️ Un toit etait peint TUILE PAR TUILE, chacune ignorant les autres : un
     carre de couleur et des points tires de `hash2`. C'est une TEXTURE, pas un
     toit — et une texture uniforme ne peut pas etre realiste, parce qu'un vrai
     toit vu d'en haut ne se lit ni par son grain ni par sa couleur. Il se lit
     par son BORD : parapet, corniche, gouttiere, la ligne d'ombre au pourtour.
     Sans bord, deux batiments mitoyens couverts pareil n'en font plus qu'un.

     `v` porte donc ce que le voisinage apprend a la tuile (`varianteDeToit`,
     monde.js) : les quatre bits des cotes ou le toit S'ARRETE (1 nord, 2 est,
     4 sud, 8 ouest), et au-dessus le grain (ou le versant, pour une pente). */
  const TOIT_TOLE = { fond: '#5b4a4a', clair: '#7a6464', sombre: '#402f2f', grain: '#655252',
                      tole: true };
  const TOIT_ARDOISE = { fond: '#4a4f5e', clair: '#69708a', sombre: '#343845', grain: '#545a6b',
                         rangs: 4 };
  const TOIT_GRAVIER = { fond: '#6d6152', clair: '#8b7d6a', sombre: '#4f4539', grain: '#7b6e5d',
                         gravier: true };
  const TOIT_BARDEAU = { fond: '#6b5a4a', clair: '#8e7862', sombre: '#4a3d32', grain: '#7a6752',
                         faite: '#a08a72' };

  /** Le champ d'un toit plat : sa matiere, avant le bord. */
  function champDeToit(ctx, bruitDe, T, style) {
    plein(ctx, style.fond, T);
    if (style.rangs) {
      ctx.fillStyle = style.sombre;
      for (let y = 0; y < T; y += style.rangs) ctx.fillRect(0, y, T, 1);
    }
    if (style.tole) {
      ctx.fillStyle = style.grain;
      for (let x = 2; x < T; x += 5) ctx.fillRect(x, 0, 1, T);     // les joints de la tole
    }
    points(ctx, bruitDe, T, style.grain, style.gravier ? 16 : 8, 3);
    points(ctx, bruitDe, T, style.sombre, style.gravier ? 10 : 5, 90);
  }

  /** Le bord : un parapet clair au ras du vide, et sa ligne d'ombre a
      l'interieur. C'est le premier repere d'un toit — celui qui dit ou finit
      le batiment. */
  function bordDeToit(ctx, v, T, style) {
    const cotes = [[1, 0, -1], [2, 1, 0], [4, 0, 1], [8, -1, 0]];
    for (const [bit, dx, dy] of cotes) {
      if (!(v & bit)) continue;
      ctx.fillStyle = style.clair;
      if (dy) ctx.fillRect(0, dy < 0 ? 0 : T - 2, T, 2);
      else ctx.fillRect(dx < 0 ? 0 : T - 2, 0, 2, T);
      ctx.fillStyle = style.sombre;
      if (dy) ctx.fillRect(0, dy < 0 ? 2 : T - 3, T, 1);
      else ctx.fillRect(dx < 0 ? 2 : T - 3, 0, 1, T);
    }
  }

  function toitPlat(ctx, v, T, style) {
    champDeToit(ctx, (v >> 4) + 1, T, style);
    bordDeToit(ctx, v & 15, T, style);
  }

  /** Le toit a deux versants : le bardeau, et une pente qui s'eclaircit vers la
      LIGNE DE FAITE. ⚠️ Le versant vient du voisinage (`varianteDePente`
      compte les tuiles de toit au nord et au sud) : c'est ce qui permet a la
      faite d'apparaitre toute seule la ou les deux pentes se rencontrent, sans
      qu'une tuile ait besoin de savoir qu'elle est au milieu. */
  function toitEnPente(ctx, v, T, style) {
    const versant = (v >> 4) & 3;           // 0 nord, 1 faite, 2 sud
    plein(ctx, style.fond, T);
    for (let y = 0; y < T; y++) {
      // Vers la faite, la pente prend la lumiere ; vers le bas, elle la perd.
      const part = versant === 0 ? y / (T - 1) : versant === 2 ? 1 - y / (T - 1) : 1 - Math.abs(y - T / 2) / (T / 2);
      const dose = Math.round(part * 3);
      if (dose >= 2) { ctx.fillStyle = style.grain; ctx.fillRect(0, y, T, 1); }
      else if (dose === 0) { ctx.fillStyle = style.sombre; ctx.fillRect(0, y, T, 1); }
    }
    ctx.fillStyle = style.sombre;
    for (let y = 2; y < T; y += 4) ctx.fillRect(0, y, T, 1);        // les rangs de bardeaux
    if (versant === 1) { ctx.fillStyle = style.faite; ctx.fillRect(0, T / 2 - 1, T, 2); }
    else if (versant === 0) { ctx.fillStyle = style.faite; ctx.fillRect(0, T - 1, T, 1); }
    else { ctx.fillStyle = style.faite; ctx.fillRect(0, 0, T, 1); }
    bordDeToit(ctx, v & 15, T, style);
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
    // L'allee de manoeuvre : de l'asphalte pale et fendu, sans une ligne.
    'p': function (ctx, v, T) { bitume(ctx, v, T); if (v === 7) fissure(ctx, v, T); },
    // L'ilot de beton au bout d'une rangee : une bordure tout autour, usee aux
    // coins — c'est elle qu'on accroche en reculant.
    'I': function (ctx, v, T) {
      plein(ctx, '#8f8b7f', T);
      points(ctx, v, T, '#847f74', 6, 11);
      ctx.fillStyle = '#a8a498';
      ctx.fillRect(0, 0, T, 1); ctx.fillRect(0, 0, 1, T);
      ctx.fillStyle = '#6f6b62';
      ctx.fillRect(0, T - 1, T, 1); ctx.fillRect(T - 1, 0, 1, T);
    },
    '^': function (ctx, v, T) { caseAuto(ctx, v, T, 'N'); },
    'v': function (ctx, v, T) { caseAuto(ctx, v, T, 'S'); },
    '<': function (ctx, v, T) { caseAuto(ctx, v, T, 'O'); },
    '>': function (ctx, v, T) { caseAuto(ctx, v, T, 'E'); },
    'R': rampe,
    'J': rampe,
    'Q': function (ctx, v, T) { plein(ctx, '#8a6a3f', T); ctx.fillStyle = '#6e5330'; for (let y = 0; y < T; y += 4) ctx.fillRect(0, y, T, 1); },
    's': function (ctx, v, T) { plein(ctx, '#d8c48a', T); points(ctx, v, T, '#c9b576', 10, 4); },
    '~': function (ctx, v, T) { plein(ctx, '#2c5f8a', T); ctx.fillStyle = '#3b73a3'; ctx.fillRect(2 + (v % 5), 4, 6, 1); ctx.fillRect(7 - (v % 4), 11, 5, 1); },
    'B': function (ctx, v, T) { toitPlat(ctx, v, T, TOIT_TOLE); },
    'E': function (ctx, v, T) { toitPlat(ctx, v, T, TOIT_ARDOISE); },
    'O': function (ctx, v, T) { toitPlat(ctx, v, T, TOIT_GRAVIER); },
    'P': function (ctx, v, T) { toitEnPente(ctx, v, T, TOIT_BARDEAU); },
    'F': function (ctx, v, T) { facade(ctx, v, T); },
    'W': function (ctx, v, T) { facade(ctx, v, T); ctx.fillStyle = '#243447'; ctx.fillRect(3, 3, 10, 9); ctx.fillStyle = '#7fb3d8'; ctx.fillRect(4, 4, 3, 3); ctx.fillStyle = '#4d7ea3'; ctx.fillRect(8, 4, 4, 7); ctx.fillRect(4, 8, 3, 3); },
    'D': function (ctx, v, T) { facade(ctx, v, T); ctx.fillStyle = '#3d2a1c'; ctx.fillRect(4, 3, 8, 13); ctx.fillStyle = '#d8b83a'; ctx.fillRect(10, 9, 1, 1); },
    'd': function (ctx, v, T) { facade(ctx, v, T); ctx.fillStyle = '#2e2118'; ctx.fillRect(4, 4, 8, 12); ctx.fillStyle = '#3a2a1e'; ctx.fillRect(5, 5, 6, 10); ctx.fillStyle = '#6b5a48'; ctx.fillRect(4, 8, 8, 1); },
    'G': function (ctx, v, T) { facade(ctx, v, T); ctx.fillStyle = '#7a7d82'; ctx.fillRect(1, 3, 14, 13); ctx.fillStyle = '#5f6267'; for (let y = 5; y < 16; y += 3) ctx.fillRect(1, y, 14, 1); },
    'b': function (ctx, v, T) { trottoir(ctx, v, T); ctx.fillStyle = '#d8b83a'; ctx.fillRect(6, 4, 4, 10); ctx.fillStyle = '#101018'; ctx.fillRect(6, 8, 4, 1); },
    'f': function (ctx, v, T) { clotureTuile(ctx, v, T, CLOTURE_GRILLAGE); },
    'w': function (ctx, v, T) { clotureTuile(ctx, v, T, CLOTURE_BOIS); },
    'X': function (ctx, v, T) { clotureTuile(ctx, v, T, CLOTURE_BARBELE); },

    /* --- Dedans : le plancher et les meubles ------------------------------

       ⚠️ Un meuble se dessine VU D'EN HAUT, avec juste assez de face au sud
       pour qu'on lise son volume : c'est la meme regle que les facades de la
       ville. Un dessin a plat (l'ancien comptoir : un rectangle brun barre
       d'un trait clair) se lit comme une tache de peinture au sol, et c'est
       exactement pour ca qu'une piece meublee avait l'air vide.

       ⚠️ Aucun meuble ne touche les quatre bords de sa tuile : il faut voir le
       plancher entre deux, sinon une rangee d'etageres devient un mur — et le
       joueur, lui, passe a travers (solidite 3). */

    't': function (ctx, v, T) {
      plein(ctx, '#b0a083', T);
      ctx.fillStyle = '#a08f72';                       // les joints des planches
      for (let y = (v % 2) * 4; y < T; y += 8) ctx.fillRect(0, y, T, 1);
      ctx.fillStyle = '#bcac8f';
      for (let y = (v % 2) * 4 + 1; y < T; y += 8) ctx.fillRect(0, y, T, 1);
      points(ctx, v, T, '#a89979', 6, 30);             // le grain du bois
    },
    'u': function (ctx, v, T) {
      plein(ctx, '#cfd3cb', T);
      ctx.fillStyle = '#bcc1b9';                       // un carreau sur deux
      ctx.fillRect(0, 0, 8, 8); ctx.fillRect(8, 8, 8, 8);
      ctx.fillStyle = 'rgba(0,0,0,0.10)';              // les joints
      ctx.fillRect(0, 7, T, 1); ctx.fillRect(7, 0, 1, T);
      ctx.fillRect(0, 15, T, 1); ctx.fillRect(15, 0, 1, T);
    },
    /* Le tapis. ⚠️ `v & 15` est le masque des cotes ou le tapis CONTINUE
       (`varianteDeBloc`, monde.js) : le galon n'allait qu'en haut et en bas de
       CHAQUE tuile, donc un tapis de trois sur trois etait trois chemins de
       couloir empiles. Le galon ne borde que les cotes ou le tapis s'arrete,
       et les rayures tombent sur la meme grille de quatre pixels d'une tuile a
       l'autre. Le grain (`v >> 4`), lui, change par tuile. */
    'y': function (ctx, v, T) {
      const nord = !(v & 1), est = !(v & 2), sud = !(v & 4), ouest = !(v & 8);   // ou le tapis S'ARRETE
      plein(ctx, '#8a3f3a', T);
      ctx.fillStyle = '#9c4f46';
      for (let y = 2; y < T; y += 4) ctx.fillRect(0, y, T, 2);
      points(ctx, v >> 4, T, '#7a3531', 5, 12);
      ctx.fillStyle = '#c9a24a';                       // le galon, sur les bords seulement
      if (nord) ctx.fillRect(0, 0, T, 1);
      if (sud) ctx.fillRect(0, T - 1, T, 1);
      if (ouest) ctx.fillRect(0, 0, 1, T);
      if (est) ctx.fillRect(T - 1, 0, 1, T);
    },
    // Le comptoir : un dessus clair, une arete, et la joue sombre au sud.
    'c': function (ctx, v, T) {
      plein(ctx, '#8a6a3f', T);
      ctx.fillStyle = '#a8834f';
      ctx.fillRect(0, 1, T, 9);
      ctx.fillStyle = '#c2a06a';
      ctx.fillRect(0, 1, T, 1);
      ctx.fillStyle = '#5e4326';                       // la joue, face au client
      ctx.fillRect(0, 10, T, 5);
      ctx.fillStyle = 'rgba(0,0,0,0.30)';
      ctx.fillRect(0, T - 1, T, 1);
    },
    // L'etagere : des boites de couleur sur deux tablettes. La variante change
    // la marchandise — sans ca, une allee entiere est le meme paquet.
    'e': function (ctx, v, T) {
      plein(ctx, '#7a6244', T);
      ctx.fillStyle = '#6a5238';
      ctx.fillRect(0, 0, T, 1); ctx.fillRect(0, 7, T, 1);
      const teintes = ['#b8503f', '#3f7ab8', '#d8b83a', '#4f9e5a', '#c2762c', '#8f5fb0'];
      for (let k = 0; k < 4; k++) {
        const i = (v * 3 + k) % teintes.length;
        ctx.fillStyle = teintes[i];
        ctx.fillRect(1 + (k % 2) * 8, 2 + Math.floor(k / 2) * 7, 6, 4);
        ctx.fillStyle = 'rgba(0,0,0,0.25)';
        ctx.fillRect(1 + (k % 2) * 8, 6 + Math.floor(k / 2) * 7, 6, 1);
      }
    },
    /* La table : un plateau CLAIR sur un piétement sombre. ⚠️ Le bois sombre
       d'avant faisait un trou noir dans le plancher : a l'ecran, une table et
       un billard se lisaient comme deux caisses posees la.

       ⚠️ `v & 15` est le masque des cotes ou la table CONTINUE
       (`varianteDeBloc`, monde.js). Le billard du bar fait quatre tuiles sur
       deux, et c'etait huit tabourets : chaque tuile avait son plateau, ses
       bords rentres et son ombre. Le plateau ne rentre ses bords, ne montre
       son chant et ne porte son ombre que la ou la table s'arrete, et le
       vernis court le long du bord nord. Une table d'une tuile n'a pas change. */
    'a': function (ctx, v, T) {
      const nord = !(v & 1), est = !(v & 2), sud = !(v & 4), ouest = !(v & 8);   // ou la table S'ARRETE
      const x0 = ouest ? 2 : 0, x1 = est ? T - 2 : T;
      ctx.fillStyle = 'rgba(0,0,0,0.20)';               // l'ombre portee, vers le sud-est
      ctx.fillRect(ouest ? 3 : 0, nord ? 5 : 0, (est ? T - 1 : T) - (ouest ? 3 : 0), T - (nord ? 5 : 0));
      ctx.fillStyle = '#5b3f26';                        // le piétement
      ctx.fillRect(x0, nord ? 3 : 0, x1 - x0, (sud ? T - 2 : T) - (nord ? 3 : 0));
      ctx.fillStyle = '#a0784a';                        // le plateau
      ctx.fillRect(x0, nord ? 2 : 0, x1 - x0, (sud ? T - 4 : T) - (nord ? 2 : 0));
      if (nord) {                                       // le vernis qui accroche, le long du bord
        ctx.fillStyle = '#bb9160';
        ctx.fillRect(ouest ? 3 : 0, 3, (est ? T - 3 : T) - (ouest ? 3 : 0), 2);
      }
      if (sud) { ctx.fillStyle = 'rgba(0,0,0,0.22)'; ctx.fillRect(x0, T - 5, x1 - x0, 1); }   // le chant
    },
    // La chaise : plus petite que la table, dossier au nord (on s'assoit face
    // au sud). On doit voir le plancher tout autour, sinon deux chaises collees
    // font une banquette.
    'h': function (ctx, v, T) {
      ctx.fillStyle = 'rgba(0,0,0,0.18)';
      ctx.fillRect(5, 8, 8, 6);
      ctx.fillStyle = '#7a5230';
      ctx.fillRect(4, 3, 8, 2);                        // le dossier
      ctx.fillStyle = '#96683c';
      ctx.fillRect(4, 6, 8, 7);                        // l'assise
      ctx.fillStyle = '#ab7b4c';
      ctx.fillRect(5, 7, 6, 3);
    },
    /* Le lit : UN lit, pas une tuile.

       ⚠️ `v & 15` est le masque des cotes ou le lit CONTINUE (`varianteDeBloc`,
       monde.js) — 1 nord, 2 est, 4 sud, 8 ouest. Sans lui, chaque tuile
       dessinait son oreiller et sa couverture, et un lit de deux tuiles sur
       deux etait quatre lits d'une place colles (« 2 ou 4 cases avec chacune
       leur oreiller »). Ici la tete de lit et l'oreiller ne vont qu'aux tuiles
       sans lit au nord, l'oreiller et la couverture courent d'une tuile a
       l'autre sans couture, et le cadre ne se ferme que la ou le lit s'arrete
       — avec un pixel de plancher devant, comme tous les meubles. */
    'l': function (ctx, v, T) {
      const nord = !(v & 1), est = !(v & 2), sud = !(v & 4), ouest = !(v & 8);   // ou le lit S'ARRETE
      const x0 = ouest ? 1 : 0, x1 = est ? T - 1 : T;   // le cadre, un pixel de plancher devant
      const y0 = nord ? 1 : 0, y1 = sud ? T - 1 : T;
      if (sud) { ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.fillRect(x0, T - 1, x1 - x0, 1); }   // l'ombre au pied
      ctx.fillStyle = '#5b3f26';                        // le bois du cadre
      ctx.fillRect(x0, y0, x1 - x0, y1 - y0);
      const mx0 = ouest ? 2 : 0, mx1 = est ? T - 2 : T; // le matelas, dans le cadre
      const my0 = nord ? 3 : 0, my1 = sud ? T - 2 : T;  // la tete de lit prend deux pixels
      ctx.fillStyle = '#d8d2c4';
      ctx.fillRect(mx0, my0, mx1 - mx0, my1 - my0);
      if (nord) {
        const ox0 = ouest ? 3 : 0, ox1 = est ? T - 3 : T;
        ctx.fillStyle = '#efeae0';                      // l'oreiller : un seul, d'un bord a l'autre
        ctx.fillRect(ox0, 4, ox1 - ox0, 4);
        ctx.fillStyle = '#c9c2b2';
        ctx.fillRect(ox0, 7, ox1 - ox0, 1);             // son ombre, pour le volume
        ctx.fillStyle = '#efeae0';                      // le drap rabattu sur la couverture
        ctx.fillRect(mx0, 9, mx1 - mx0, 2);
      }
      const cy0 = nord ? 11 : 0, cy1 = sud ? T - 3 : T; // la couverture, jusqu'au pied
      ctx.fillStyle = '#3f6b8a';
      ctx.fillRect(mx0, cy0, mx1 - mx0, cy1 - cy0);
      ctx.fillStyle = '#4d7ea3';                        // le pique, continu d'une tuile a l'autre
      for (let y = nord ? 14 : 2; y < cy1; y += 4) ctx.fillRect(mx0, y, mx1 - mx0, 1);
      if (sud) { ctx.fillStyle = '#2f5670'; ctx.fillRect(mx0, T - 3, mx1 - mx0, 1); }   // l'ourlet du pied
    },
    // Le frigo (ou la vitrine refrigeree) : blanc, une poignee, un reflet.
    'j': function (ctx, v, T) {
      plein(ctx, '#b9c2c4', T);
      ctx.fillStyle = '#d8e0e2';
      ctx.fillRect(1, 1, T - 2, 11);
      ctx.fillStyle = '#8fa3a8';
      ctx.fillRect(1, 12, T - 2, 3);                   // la face
      ctx.fillStyle = '#5f6f74';
      ctx.fillRect(11, 3, 2, 7);                       // la poignee
      ctx.fillStyle = 'rgba(255,255,255,0.45)';
      ctx.fillRect(3, 3, 4, 1);
    },
    /* La machine : de la tole, des boulons, une courroie.

       ⚠️ `v & 15` est le masque des cotes ou la machine CONTINUE
       (`varianteDeBloc`, monde.js) : les presses de l'usine font quatre tuiles
       sur deux, et chacune etait huit petites machines avec leurs boulons. La
       tole court d'une tuile a l'autre, les boulons ne vont qu'aux quatre
       coins du bloc, la face et l'ombre au pied seulement. La courroie suit le
       sens du bloc — le long d'une machine large, debout dans une machine
       etroite — et une machine d'une tuile tire au sort (`v >> 4`) : deux
       tours de suite ne sont pas le meme tour. */
    'm': function (ctx, v, T) {
      const nord = !(v & 1), est = !(v & 2), sud = !(v & 4), ouest = !(v & 8);   // ou la machine S'ARRETE
      plein(ctx, '#6f7378', T);
      const x0 = ouest ? 1 : 0, x1 = est ? T - 1 : T;
      ctx.fillStyle = '#82868c';                       // la tole
      ctx.fillRect(x0, nord ? 1 : 0, x1 - x0, (sud ? T - 4 : T) - (nord ? 1 : 0));
      if (sud) { ctx.fillStyle = '#5a5e63'; ctx.fillRect(x0, T - 4, x1 - x0, 3); }   // la face
      ctx.fillStyle = '#3f4347';                       // la courroie
      const couchee = !(est && ouest) ? true : (!(nord && sud) ? false : (v >> 4) % 2 === 1);
      if (couchee) ctx.fillRect(ouest ? 3 : 0, 4, (est ? T - 3 : T) - (ouest ? 3 : 0), 3);
      else ctx.fillRect(4, nord ? 3 : 0, 3, (sud ? T - 5 : T) - (nord ? 3 : 0));
      ctx.fillStyle = '#d8b83a';                       // les boulons, aux coins du bloc
      if (nord && ouest) ctx.fillRect(2, 2, 1, 1);
      if (nord && est) ctx.fillRect(T - 3, 2, 1, 1);
      if (sud && ouest) ctx.fillRect(2, T - 6, 1, 1);
      if (sud && est) ctx.fillRect(T - 3, T - 6, 1, 1);
      if (sud) { ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fillRect(0, T - 1, T, 1); }
    },
    // La plante verte : un pot et trois touffes. Rien d'autre ne dit « on
    // s'occupe de cette piece-la ».
    'n': function (ctx, v, T) {
      ctx.fillStyle = 'rgba(0,0,0,0.20)';
      ctx.fillRect(5, 11, 8, 4);
      ctx.fillStyle = '#8a5a3a';
      ctx.fillRect(5, 10, 7, 5);
      ctx.fillStyle = '#a06c46';
      ctx.fillRect(5, 10, 7, 1);
      ctx.fillStyle = '#2f7a44';
      ctx.fillRect(4, 3, 9, 7);
      ctx.fillStyle = '#3f9a56';
      ctx.fillRect(6, 2, 5, 4); ctx.fillRect(3, 5, 3, 3);
      ctx.fillStyle = '#256238';
      ctx.fillRect(8, 6, 4, 3);
    },
    // Le classeur (ou le coffre) : deux tiroirs et leurs poignees.
    'k': function (ctx, v, T) {
      plein(ctx, '#5a6470', T);
      ctx.fillStyle = '#6e7a88';
      ctx.fillRect(1, 1, T - 2, 6); ctx.fillRect(1, 8, T - 2, 6);
      ctx.fillStyle = '#c9ccd2';
      ctx.fillRect(6, 3, 4, 1); ctx.fillRect(6, 10, 4, 1);
      ctx.fillStyle = 'rgba(0,0,0,0.25)';
      ctx.fillRect(0, T - 1, T, 1);
    },
    // Le poele : quatre ronds et la porte du four.
    'z': function (ctx, v, T) {
      plein(ctx, '#c4c7c2', T);
      ctx.fillStyle = '#3a3a3e';
      for (let k = 0; k < 4; k++) ctx.fillRect(2 + (k % 2) * 7, 2 + Math.floor(k / 2) * 5, 5, 3);
      ctx.fillStyle = '#8f9490';
      ctx.fillRect(1, 12, T - 2, 3);
      ctx.fillStyle = '#d8b83a';
      ctx.fillRect(3, 13, 1, 1); ctx.fillRect(6, 13, 1, 1);
    },
    // L'escalier : des marches et deux limons. Il MENE quelque part — c'est le
    // seul meuble dont on attend qu'il fasse quelque chose quand on est
    // dessus, et il doit donc se reconnaitre du premier coup d'oeil.
    '/': function (ctx, v, T) {
      plein(ctx, '#6b5a44', T);
      for (let k = 0; k < 4; k++) {
        ctx.fillStyle = ['#8a7458', '#9c8566', '#ae9674', '#c0a782'][k];
        ctx.fillRect(2, k * 4, T - 4, 3);
        ctx.fillStyle = 'rgba(0,0,0,0.30)';
        ctx.fillRect(2, k * 4 + 3, T - 4, 1);
      }
      ctx.fillStyle = '#4a3d2e';                       // les limons
      ctx.fillRect(0, 0, 2, T); ctx.fillRect(T - 2, 0, 2, T);
    },
  };
})();

/* Les devantures et les graffitis : une COUCHE peinte par-dessus les tuiles.

   ⚠️ Rien ici n'est solide et rien ne bouge : ces dessins vivent dans le
   morceau de decor, cuit une fois et garde en cache. Une rue commercante ne
   coute donc pas une image de plus a l'affichage — c'est ce qui permet d'en
   mettre partout.

   ⚠️ Le repere est celui du MORCEAU : (ox, oy) est le coin haut-gauche de la
   tuile d'ancrage dans le canvas du morceau, et il peut etre negatif ou
   depasser — une enseigne a cheval sur deux morceaux est peinte DANS LES DEUX,
   et chacun garde la moitie qui le regarde. */
const FACADES = (function () {
  'use strict';

  const T = 16;

  //: Hauteurs, sur les 16 px du mur vu d'en haut. Le bandeau prend la moitie
  //: haute (le nom doit se lire sans s'arreter de rouler), l'auvent la fait
  //: reculer, et la vitre au pied du mur est ce qui s'allume la nuit.
  const BANDEAU_Y = 1, BANDEAU_H = 8;
  const AUVENT_Y = 9, AUVENT_H = 4;
  const VITRE_Y = 13, VITRE_H = 3;

  function eclaircir(couleur, dose) {
    const n = parseInt(couleur.slice(1), 16);
    const r = Math.min(255, ((n >> 16) & 255) + dose);
    const v = Math.min(255, ((n >> 8) & 255) + dose);
    const b = Math.min(255, (n & 255) + dose);
    return 'rgb(' + r + ',' + v + ',' + b + ')';
  }

  /** Le bandeau, le nom, l'auvent raye, la vitre et la pancarte.
      `d` = { x, y, l, genre, texte, pancarte, porte }, `g` = le genre. */
  function devanture(ctx, d, g, ox, oy) {
    const large = d.l * T;

    // Le bandeau : fond sombre, une arete claire en haut pour le detacher du toit.
    ctx.fillStyle = g.bandeau;
    ctx.fillRect(ox, oy + BANDEAU_Y, large, BANDEAU_H);
    ctx.fillStyle = eclaircir(g.bandeau, 26);
    ctx.fillRect(ox, oy + BANDEAU_Y, large, 1);
    ctx.fillStyle = 'rgba(0,0,0,0.35)';
    ctx.fillRect(ox, oy + BANDEAU_Y + BANDEAU_H - 1, large, 1);

    // Le nom, centre. ⚠️ Arrondi a l'entier : un texte pose sur un demi-pixel
    // est floute par le canvas, et a cinq pixels de haut il devient illisible.
    const larg = Atlas.largeurTexte(d.texte, 1);
    Atlas.texte(ctx, d.texte, Math.round(ox + (large - larg) / 2), oy + BANDEAU_Y + 2, g.lettres, 1);

    // ⚠️ Sous le bandeau, chaque tuile est ce que `motifs` dit qu'elle est.
    // Une porte NE PREND PAS l'auvent et la vitrine : elle garde toute sa
    // hauteur, sinon on lit le nom du commerce sans voir par ou entrer.
    const motifs = d.motifs || '';
    for (let i = 0; i < d.l; i++) {
      const x = ox + i * T;
      const quoi = motifs[i] || 'W';
      if (quoi === 'W') { auvent(ctx, g, x, oy); vitrine(ctx, g, x, oy, i, d.l, motifs); }
      else porte(ctx, g, x, oy, quoi);
    }

    if (d.pancarte) pancarte(ctx, d, g, ox, oy);
  }

  function auvent(ctx, g, x, oy) {
    ctx.fillStyle = g.auvent;
    ctx.fillRect(x, oy + AUVENT_Y, T, AUVENT_H);
    ctx.fillStyle = eclaircir(g.auvent, 34);
    for (let k = 0; k < T; k += 6) ctx.fillRect(x + k, oy + AUVENT_Y, 3, AUVENT_H);
    ctx.fillStyle = 'rgba(0,0,0,0.28)';
    ctx.fillRect(x, oy + AUVENT_Y + AUVENT_H - 1, T, 1);
  }

  /** La vitre au pied du mur : c'est elle qu'on voit briller de loin la nuit.
      Les montants ne se posent qu'entre deux vitrines — pas contre une porte,
      qui a deja son propre encadrement. */
  function vitrine(ctx, g, x, oy, i, total, motifs) {
    ctx.fillStyle = g.vitre;
    ctx.fillRect(x, oy + VITRE_Y, T, VITRE_H);
    ctx.fillStyle = 'rgba(0,0,0,0.30)';
    if (i > 0 && (motifs[i - 1] || 'W') === 'W') ctx.fillRect(x - 1, oy + VITRE_Y, 2, VITRE_H);
    if (i === 0) ctx.fillRect(x, oy + VITRE_Y, 1, VITRE_H);
    if (i === total - 1) ctx.fillRect(x + T - 1, oy + VITRE_Y, 1, VITRE_H);
  }

  //: ⚠️ Une porte OUVRABLE se distingue d'une porte fermee, et ca ne tient qu'a
  //: deux details : sa vitre est claire, et elle a une poignee doree. C'est la
  //: seule chose qui dit au joueur, de loin, qu'il peut entrer ici — le reste
  //: de la devanture est identique. « D » on entre ; « d » condamnee (planches)
  //: et « P » simplement fermee ; « G » le rideau du garage.
  function porte(ctx, g, x, oy, quoi) {
    const y = oy + AUVENT_Y;                 // la porte prend l'auvent ET la vitre
    const h = AUVENT_H + VITRE_H;
    ctx.fillStyle = 'rgba(0,0,0,0.45)';      // le renfoncement
    ctx.fillRect(x + 1, y, T - 2, h);

    if (quoi === 'G') {
      ctx.fillStyle = '#7a7d82';
      ctx.fillRect(x + 2, y + 1, T - 4, h - 1);
      ctx.fillStyle = '#5f6267';
      for (let k = y + 2; k < y + h; k += 2) ctx.fillRect(x + 2, k, T - 4, 1);
      return;
    }

    const ouvrable = quoi === 'D';
    ctx.fillStyle = g.bandeau;                // l'encadrement, aux couleurs du commerce
    ctx.fillRect(x + 2, y, T - 4, h);
    ctx.fillStyle = eclaircir(g.bandeau, 22); // une arete claire : le chambranle
    ctx.fillRect(x + 2, y, T - 4, 1);
    // ⚠️ Une porte fermee n'est pas un trou noir : assez sombre pour qu'on voie
    // qu'elle ne s'ouvre pas, assez claire pour qu'on la lise comme une porte.
    ctx.fillStyle = ouvrable ? g.vitre : '#2b2734';
    ctx.fillRect(x + 3, y + 1, T - 6, h - 2);
    ctx.fillStyle = 'rgba(0,0,0,0.35)';       // les deux battants
    ctx.fillRect(x + T / 2 - 1, y + 1, 1, h - 2);

    if (quoi === 'd') {                       // condamnee : deux planches en travers
      ctx.fillStyle = '#6b5a48';
      ctx.fillRect(x + 3, y + 2, T - 6, 1);
      ctx.fillRect(x + 3, y + h - 3, T - 6, 1);
    } else if (ouvrable) {
      ctx.fillStyle = '#d8b83a';               // la poignee : on entre ici
      ctx.fillRect(x + T / 2 + 1, y + Math.floor(h / 2), 2, 1);
      ctx.fillStyle = eclaircir(g.vitre, 20);  // un rai de lumiere au seuil
      ctx.fillRect(x + 3, y + h - 2, T - 6, 1);
    } else {
      ctx.fillStyle = 'rgba(255,255,255,0.10)';  // un reflet, pour qu'elle ne soit pas un trou
      ctx.fillRect(x + 4, y + 2, 2, h - 4);
    }
  }

  /** L'enseigne perpendiculaire : elle DEPASSE du mur sur le trottoir, c'est
      ce qui la rend lisible quand on arrive par le cote. */
  function pancarte(ctx, d, g, ox, oy) {
    const x = d.pancarte < 0 ? ox + 2 : ox + d.l * T - 9;
    const y = oy + T + 1;                       // la tuile de trottoir, sous le mur
    ctx.fillStyle = 'rgba(0,0,0,0.30)';
    ctx.fillRect(x + 1, y + 1, 7, 10);          // l'ombre portee au sol
    ctx.fillStyle = g.bandeau;
    ctx.fillRect(x, y, 7, 10);
    ctx.fillStyle = eclaircir(g.bandeau, 30);
    ctx.fillRect(x, y, 7, 1);
    ctx.fillStyle = g.lettres;
    ctx.fillRect(x + 2, y + 2, 3, 1);
    ctx.fillRect(x + 2, y + 4, 3, 1);
    ctx.fillRect(x + 2, y + 6, 2, 1);
    ctx.fillStyle = g.auvent;                    // la potence qui la tient au mur
    ctx.fillRect(x + 3, y - 2, 1, 2);
  }

  /* --- Les residences ---------------------------------------------------

     ⚠️ Un logement se lit a trois choses, et aucune n'est un nom : les ETAGES
     (des rangees de fenetres, pas un mur nu), le BALCON, et l'ESCALIER DE FER
     qui descend sur le trottoir. C'est ce qui separe une rue ou l'on habite
     d'une rue d'entrepots — avant, les deux etaient le meme mur de brique.

     ⚠️ Vu d'en haut, on ne voit pas la hauteur : ce sont les RANGEES de
     fenetres qui la disent. Une rangee par etage au-dessus du rez-de-chaussee,
     et le rez prend le bas de la tuile, la ou le passant marche. */

  const CORNICHE_H = 2;
  const RDC_Y = 11, RDC_H = 5;

  function fenetre(ctx, m, x, y, l, h) {
    ctx.fillStyle = m.cadre;
    ctx.fillRect(x, y, l, h);
    ctx.fillStyle = m.vitre;
    ctx.fillRect(x + 1, y + 1, l - 2, h - 2);
    ctx.fillStyle = 'rgba(255,255,255,0.16)';
    ctx.fillRect(x + 1, y + 1, 1, h - 2);
  }

  /** La rangee de fenetres d'un etage, deux par tuile. */
  function etage(ctx, r, m, ox, oy, y) {
    for (let i = 0; i < r.l; i++) {
      const x = ox + i * T;
      fenetre(ctx, m, x + 2, y, 5, 3);
      fenetre(ctx, m, x + 9, y, 5, 3);
    }
  }

  /** Le garde-corps du balcon : des barreaux et une main courante. */
  function balcon(ctx, fer, ox, oy, large, y) {
    ctx.fillStyle = fer.ombre;
    ctx.fillRect(ox, oy + y + 3, large, 1);
    ctx.fillStyle = fer.barreau;
    for (let x = 0; x < large; x += 3) ctx.fillRect(ox + x, oy + y, 1, 3);
    ctx.fillStyle = fer.arete;
    ctx.fillRect(ox, oy + y, large, 1);
  }

  /** L'escalier exterieur, sur la tuile de trottoir sous la porte. `sens` :
      0 tout droit, -1 il tourne vers l'ouest, +1 vers l'est. */
  function escalier(ctx, fer, x, y, sens) {
    ctx.fillStyle = fer.ombre;
    ctx.fillRect(x + 2, y + 1, 12, 13);
    for (let k = 0; k < 5; k++) {
      ctx.fillStyle = fer.marche;
      ctx.fillRect(x + 3, y + 1 + k * 3, 10, 2);
      ctx.fillStyle = fer.arete;
      ctx.fillRect(x + 3, y + 1 + k * 3, 10, 1);
    }
    ctx.fillStyle = fer.barreau;                  // les deux limons
    ctx.fillRect(x + 2, y, 1, 15);
    ctx.fillRect(x + 13, y, 1, 15);
    if (sens) {                                   // le palier du bas, en biais
      const bx = sens < 0 ? x - 4 : x + 10;
      ctx.fillStyle = fer.marche;
      ctx.fillRect(bx, y + 12, 8, 3);
      ctx.fillStyle = fer.barreau;
      ctx.fillRect(bx, y + 11, 8, 1);
    }
  }

  /** La porte d'un logement : bois sombre, une imposte, des sonnettes. */
  function porteDeLogement(ctx, m, fer, x, y, h, quoi) {
    ctx.fillStyle = 'rgba(0,0,0,0.40)';
    ctx.fillRect(x + 1, y, T - 2, h);
    ctx.fillStyle = m.porte;
    ctx.fillRect(x + 2, y, T - 4, h);
    ctx.fillStyle = quoi === 'D' ? m.allumee : m.vitre;   // l'imposte
    ctx.fillRect(x + 4, y + 1, T - 8, 2);
    if (quoi === 'd') {
      ctx.fillStyle = '#6b5a48';
      ctx.fillRect(x + 2, y + 1, T - 4, 1);
      ctx.fillRect(x + 2, y + h - 2, T - 4, 1);
      return;
    }
    ctx.fillStyle = fer.arete;                            // les sonnettes
    ctx.fillRect(x + 3, y + 3, 1, 1); ctx.fillRect(x + 3, y + 5, 1, 1);
    if (quoi === 'D') {
      ctx.fillStyle = '#d8b83a';                          // la poignee : on entre
      ctx.fillRect(x + T - 5, y + Math.floor(h / 2), 2, 1);
    }
  }

  /** `r` = { x, y, l, etages, motifs, escalier, porte, mur, balcon }. */
  function residence(ctx, r, m, fer, ox, oy) {
    const large = r.l * T;
    ctx.fillStyle = 'rgba(0,0,0,0.22)';                   // l'ombre de la corniche
    ctx.fillRect(ox, oy, large, CORNICHE_H);
    ctx.fillStyle = m.joint;
    ctx.fillRect(ox, oy, large, 1);

    const hauts = Math.max(0, r.etages - 1);
    for (let e = 0; e < hauts; e++) etage(ctx, r, m, ox, oy, oy + 2 + e * 4);
    if (r.balcon && hauts) balcon(ctx, fer, ox, oy, large, 2 + (hauts - 1) * 4 + 3);

    const motifs = r.motifs || '';
    for (let i = 0; i < r.l; i++) {
      const x = ox + i * T;
      const quoi = motifs[i] || 'F';
      if (quoi === 'D' || quoi === 'd' || quoi === 'P' || quoi === 'G') {
        porteDeLogement(ctx, m, fer, x, oy + RDC_Y, RDC_H, quoi);
      } else {
        fenetre(ctx, m, x + 3, oy + RDC_Y + 1, 10, 4);
        ctx.fillStyle = 'rgba(0,0,0,0.18)';               // le soubassement
        ctx.fillRect(x, oy + T - 1, T, 1);
      }
    }
    if (r.etages >= 2) escalier(ctx, fer, ox + r.porte * T, oy + T, r.escalier);
  }

  //: Trois facons de salir un mur. 0 = le mot seul, 1 = le barbouillage seul,
  //: 2 = les deux. ⚠️ Un tag est TOUJOURS un peu de travers et deborde un peu :
  //: pose bien droit dans sa tuile, il a l'air d'un panneau officiel.
  function graffiti(ctx, gr, couleur, ox, oy) {
    const h = hash(gr.x, gr.y);
    if (gr.motif !== 1) {
      const dx = 1 + (h % 3), dy = 3 + ((h >> 3) % 4);
      if (gr.penche) {
        ctx.save();
        ctx.translate(ox + dx, oy + dy);
        ctx.rotate(-0.14);
        ctx.fillStyle = 'rgba(0,0,0,0.40)';
        Atlas.texte(ctx, gr.texte, 1, 1, 'rgba(0,0,0,0.40)', 1);
        Atlas.texte(ctx, gr.texte, 0, 0, couleur, 1);
        ctx.restore();
      } else {
        Atlas.texte(ctx, gr.texte, ox + dx + 1, oy + dy + 1, 'rgba(0,0,0,0.40)', 1);
        Atlas.texte(ctx, gr.texte, ox + dx, oy + dy, couleur, 1);
      }
    }
    if (gr.motif !== 0) {
      ctx.fillStyle = couleur;
      for (let i = 0; i < 7; i++) {
        const b = hash(gr.x + i * 7, gr.y - i * 3);
        ctx.fillRect(ox + (b % 14), oy + 2 + ((b >> 4) % 12), 1 + (b % 3), 1);
      }
      ctx.fillStyle = 'rgba(255,255,255,0.12)';
      ctx.fillRect(ox + 2 + (h % 6), oy + 4 + ((h >> 5) % 6), 4, 1);
    }
  }

  function hash(x, y) {
    let n = (x * 374761393 + y * 668265263) >>> 0;
    n = (n ^ (n >>> 13)) * 1274126177 >>> 0;
    return (n ^ (n >>> 16)) >>> 0;
  }

  /* --- Ce qu'un toit PORTE ------------------------------------------------

     Vu d'en haut, ce qui rend un toit credible, c'est son encombrement :
     sorties de ventilation, unites de climatisation, cheminee, cage
     d'escalier, reservoir d'eau, antennes. La ville n'en avait aucun.

     ⚠️ Ce n'est PAS du decor : `poser_decor` refuse les tuiles solides, et il a
     raison — le decor est une entite qu'on heurte. Ce qui est sur un toit n'est
     heurte par personne : c'est du dessin, il voyage dans le paquet et se peint
     dans le morceau, une fois, comme les enseignes. Le budget d'image n'y
     touche jamais.

     ⚠️ Chacun porte son OMBRE, au sud-est : sans elle, une boite grise posee sur
     un toit gris se lit comme une tache de peinture — c'est exactement ce qui
     est arrive aux premiers comptoirs, et la lecon est deja ecrite plus haut. */
  const TOITURES = {
    ventilation: function (ctx, x, y, h) {
      ctx.fillStyle = 'rgba(11,10,18,0.35)'; ctx.fillRect(x + 6, y + 7, 7, 6);
      ctx.fillStyle = '#8f8b84'; ctx.fillRect(x + 4, y + 5, 7, 6);
      ctx.fillStyle = '#6a6660'; ctx.fillRect(x + 5, y + 6, 5, 4);
      ctx.fillStyle = '#a8a49c'; ctx.fillRect(x + 5, y + 6, 5, 1);
      if (h % 2) { ctx.fillStyle = '#8f8b84'; ctx.fillRect(x + 12, y + 9, 3, 3); }
    },
    clim: function (ctx, x, y) {
      ctx.fillStyle = 'rgba(11,10,18,0.35)'; ctx.fillRect(x + 4, y + 6, 11, 9);
      ctx.fillStyle = '#9aa0a6'; ctx.fillRect(x + 2, y + 4, 11, 9);
      ctx.fillStyle = '#7a7f85'; ctx.fillRect(x + 3, y + 5, 9, 7);
      ctx.fillStyle = '#5f6469';
      for (let i = 0; i < 4; i++) ctx.fillRect(x + 4, y + 6 + i * 2, 7, 1);
      ctx.fillStyle = '#b4bac0'; ctx.fillRect(x + 2, y + 4, 11, 1);
    },
    cheminee: function (ctx, x, y) {
      ctx.fillStyle = 'rgba(11,10,18,0.35)'; ctx.fillRect(x + 7, y + 6, 6, 8);
      ctx.fillStyle = '#8a5a4a'; ctx.fillRect(x + 5, y + 3, 6, 9);
      ctx.fillStyle = '#6e4438'; for (let i = 0; i < 4; i++) ctx.fillRect(x + 5, y + 5 + i * 2, 6, 1);
      ctx.fillStyle = '#b0a89c'; ctx.fillRect(x + 4, y + 2, 8, 2);
      ctx.fillStyle = '#2b2620'; ctx.fillRect(x + 6, y + 3, 4, 1);
    },
    cage: function (ctx, x, y) {
      ctx.fillStyle = 'rgba(11,10,18,0.35)'; ctx.fillRect(x + 5, y + 6, 11, 10);
      ctx.fillStyle = '#6d6a63'; ctx.fillRect(x + 2, y + 3, 12, 11);
      ctx.fillStyle = '#57544e'; ctx.fillRect(x + 3, y + 4, 10, 9);
      ctx.fillStyle = '#8a867e'; ctx.fillRect(x + 2, y + 3, 12, 1);
      ctx.fillStyle = '#3a3732'; ctx.fillRect(x + 5, y + 9, 6, 4);      // la porte du toit
      ctx.fillStyle = '#b0aca4'; ctx.fillRect(x + 10, y + 10, 1, 1);
    },
    reservoir: function (ctx, x, y) {
      ctx.fillStyle = 'rgba(11,10,18,0.35)'; ctx.fillRect(x + 5, y + 7, 11, 8);
      ctx.fillStyle = '#7a6144'; ctx.fillRect(x + 3, y + 2, 10, 11);
      ctx.fillStyle = '#5f4b34'; ctx.fillRect(x + 4, y + 3, 8, 9);
      ctx.fillStyle = '#93795a';
      ctx.fillRect(x + 3, y + 4, 10, 1); ctx.fillRect(x + 3, y + 9, 10, 1);
      ctx.fillStyle = '#3f3226'; ctx.fillRect(x + 4, y + 13, 2, 2); ctx.fillRect(x + 10, y + 13, 2, 2);
    },
    antenne: function (ctx, x, y, h) {
      ctx.fillStyle = 'rgba(11,10,18,0.3)'; ctx.fillRect(x + 8, y + 8, 5, 1);
      ctx.fillStyle = '#b4b0a8';
      ctx.fillRect(x + 7, y + 2, 1, 10);
      for (let i = 0; i < 3; i++) ctx.fillRect(x + 5, y + 4 + i * 3, 5, 1);
      ctx.fillStyle = '#6a6660'; ctx.fillRect(x + 6, y + 11, 3, 2);
      if (h % 3 === 0) { ctx.fillStyle = '#c4362f'; ctx.fillRect(x + 7, y + 1, 1, 1); }
    },
  };

  /** Ce qu'un toit porte, a sa tuile. `t` = { x, y, type }. */
  function toiture(ctx, t, ox, oy) {
    const peintre = TOITURES[t.type];
    if (!peintre) return;
    peintre(ctx, ox, oy, hash(t.x, t.y));
  }

  /** L'ombre d'un batiment sur la rue : une bande sombre au sud d'une facade.

      ⚠️ C'est ce qui donne de la HAUTEUR a toute la ville d'un coup — sans elle,
      un mur vu d'en haut est une tuile comme une autre, et la ville est plate.
      Elle se peint SOUS les enseignes : une ombre par-dessus une pancarte
      donnerait une pancarte sale. */
  function ombreDeMur(ctx, ox, oy) {
    ctx.fillStyle = 'rgba(11,10,18,0.42)';
    ctx.fillRect(ox, oy, T, 5);
    ctx.fillStyle = 'rgba(11,10,18,0.22)';
    ctx.fillRect(ox, oy + 5, T, 3);
    ctx.fillStyle = 'rgba(11,10,18,0.10)';
    ctx.fillRect(ox, oy + 8, T, 2);
  }

  return { devanture: devanture, residence: residence, graffiti: graffiti,
           toiture: toiture, ombreDeMur: ombreDeMur, TOITURES: TOITURES, T: T };
})();

/* Decor procedural : (ctx, w, h). `r` = rayon au sol, `solide` = on s'y cogne.
   ⚠️ Un poteau ou un buisson n'est PAS solide : un trottoir de 32 px ou l'on
   reste coince sur une poubelle est un trottoir qu'on n'emprunte plus.

   `sol` = [demi-largeur, demi-profondeur] de l'EMPREINTE AU SOL, centree sur
   l'ancre (les pieds), pour ce qui est carre. Sans `sol`, c'est `r` qui sert.
   ⚠️ Un cercle ne sait pas tenir un camion-restaurant : 44 px de large, 8 px
   de profond. Le cercle qui tient dans la profondeur (r 16) laisse SIX PIXELS
   de carrosserie ou le joueur se tient debout, dans le dessin — c'est la
   capture que Martin a envoyee ; le cercle qui couvre la largeur (r 22) pose
   un mur invisible de 22 px devant et derriere. Il faut une boite.
   ⚠️ L'arbre, lui, garde son cercle : son tronc fait 3 px et sa cime est
   PEINTE EN HAUTEUR. On passe sous une cime, on ne passe pas dans un comptoir. */

/* Un decor dessine en grille, comme un personnage, quand des fillRect ne
   suffisent plus a le lire : une lettre par pixel, `.` = transparent. */
function peindreGrilleDecor(ctx, pal, grille) {
  for (let y = 0; y < grille.length; y++) {
    const ligne = grille[y];
    let x = 0;
    while (x < ligne.length) {
      const ch = ligne[x];
      let fin = x + 1;
      while (fin < ligne.length && ligne[fin] === ch) fin++;
      if (ch !== '.') { ctx.fillStyle = pal[ch]; ctx.fillRect(x, y, fin - x, 1); }
      x = fin;
    }
  }
}

/* L'etoile de recherche, DESSINEE et non ecrite.

   ⚠️ C'etait un caractere « ★ » de la police 5 x 7 tire a l'echelle 1, range
   dans la colonne du coin haut-droit — sous un montant d'argent trace a
   l'echelle 2. La chose la plus importante d'une poursuite etait donc le plus
   petit element de l'ecran, dans un coin, en blanc. C'etait a l'envers.

   Un « ★ » agrandi donne une bouillie de blocs : il faut une vraie grille.
   `p` est la pointe (le clair), `c` le corps, `k` le contour — trois lettres
   pour qu'une etoile ALLUMEE et une etoile ETEINTE partagent le meme dessin
   et ne different que par leur palette. On doit lire « trois sur cinq » d'un
   coup d'oeil, sans compter : l'eteinte est donc CREUSE, pas un point. */
const ETOILE = [
  '.....k.....',
  '....kpk....',
  '....kpk....',
  '...kkpkk...',
  'kkkkccckkkk',
  '.kccccccck.',
  '..kccccck..',
  '...kccck...',
  '..kcckcck..',
  '.kck...kck.',
  'kk.......kk',
];

/* Le camion-restaurant, vu de trois quarts : un fourgon a caisse, l'enseigne
   sur le toit, la cheminee de la hotte qui fume, l'auvent raye au-dessus du
   guichet, le menu a la craie, le comptoir avec les frites et le gobelet, la
   cabine et son phare, deux vraies roues.

   ⚠️ Le guichet est TROUE. Le marchand est une vraie entite, dessinee AVANT
   le camion (tri par y), les pieds 11 px au-dessus de l'ancre
   (`Entites.creerAmbulants`). Peindre l'interieur du guichet, c'etait le
   cacher : on ne voyait que trois pixels de cheveux au-dessus du toit. Les
   dix colonnes vides (17..26, rangees 11..18) sont exactement sa tete et ses
   epaules ; l'auvent couvre le haut de sa tete, le comptoir ses jambes. Le
   bitume qui passe dans les coins du trou fait l'ombre de la cuisine. */
const PAL_CAMION_CUISINE = {
  k: '#101018', g: '#27ae60', d: '#1e8e4f', G: '#4cc47e', r: '#c0392b', c: '#efe6d0',
  v: '#7fb3d8', V: '#b8dcf0', m: '#9aa0a8', M: '#6f757c', t: '#1a1a1e', h: '#8a8f96',
  l: '#fff3b0', y: '#e8b33c', o: '#d98324', b: '#2c2c2c', s: '#dfe4e8',
};
const GRILLE_CAMION_CUISINE = [
  '...kkkkkkkkkkkkkkkkkkkkkkkkkkkkk.....ss.....',
  '...kccccccccccccccccccccccccccck....ss......',
  '...kccccccccccccccccccccccccccck...ss.......',
  '...kccccccccccccccccccccccccccck..MMMM......',
  '...kccccccccccccccccccccccccccck...mm.......',
  '...kccccccccccccccccccccccccccck...mm.......',
  '...kkkkkkkkkkkkkkkkkkkkkkkkkkkkk....mm......',
  '..GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG.',
  '..dggggggggggrrccrrccrrccrrccrrggggggggggdd.',
  '..dggggggggggrrccrrccrrccrrccrrgddddddddddd.',
  '..dggggggggggrrccrrccrrccrrccrrgdVVvvvvvddd.',
  '..dgggggggggggggk..........kggggdVvvvvvvddd.',
  '..dgbbbbbbbbggggk..........kggggdvvvvvvvddd.',
  '..dgbyyyybcbggggk..........kggggdvvvvvvvddd.',
  '..dgbbbbbbbbggggk..........kggggdvvvvvvvdll.',
  '..dgbyyybbcbggggk..........kggggdvvvvvvvdll.',
  '..dgbbbbbbbbggggk..........kggggddddddddddd.',
  '..dgbyyyybcbggyyk..........kccggdggggggggdd.',
  '..dgbbbbbbbbggook..........kccggdgggggmmgdd.',
  '..dgggggggggggmmmmmmmmmmmmmmmmggdggggggggdd.',
  '..dgggggggggggMMMMMMMMMMMMMMMMggdggggggggdd.',
  '..dgggggggggggggggggggggggggggggdggggggggdd.',
  '..dgggggggggggggggggggggggggggggdggggggggdd.',
  '..dcccccccccccccccccccccccccccccdccccccccdd.',
  '..dgggggggggggggggggggggggggggggdggggggggdd.',
  '..dgggggggggggggggggggggggggggggdggggggggdd.',
  '..dgggggggggggggggggggggggggggggdggggggggdd.',
  '.mmmddddddddddddddddddddddddddddddddddddmmm.',
  '.mmmddddddddddddddddddddddddddddddddddddmmm.',
  '......ttttt.......................ttttt.....',
  '.....ttttttt.....................ttttttt....',
  '.....tthhhtt.....................tthhhtt....',
  '.....tthhhtt.....................tthhhtt....',
  '.....ttttttt.....................ttttttt....',
  '......ttttt.......................ttttt.....',
];

/* ⚠️ `arrete` et `casse` : c'est LA FICHE qui decide ce qu'un char fait d'un
   decor, comme `vehicules.py` decide ce qu'un char sait faire. Avant, le decor
   etait solide pour les pietons et FANTOME pour les chars : un autobus
   traversait un arbre, un kiosque et une fontaine sans ralentir, et le
   lampadaire etait fantome pour tout le monde.

     `arrete: n`  il ARRETE un char, comme un mur — sauf au-dessus de la masse
                  `n` : un camion (3,0) deracine un arbre, une berline (1,0)
                  s'y ecrase.
     `casse: f`   il CEDE sous n'importe quel char lance, qui garde la
                  fraction `f` de sa vitesse. Un banc, un cone, un lampadaire.

   Un decor sans l'un ni l'autre reste ce qu'il etait : solide pour les gens,
   invisible pour les chars (les feux, les panneaux — on ne renverse pas la
   signalisation, sinon un croisement se demonte au premier virage rate). */
const DECORS = {
  arbre: { arrete: 2.0, w: 18, h: 26, ancre: [9, 25], r: 5, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#5a3a1a'; ctx.fillRect(8, 16, 3, 9);
    ctx.fillStyle = '#2f6b2a'; ctx.fillRect(2, 4, 14, 13); ctx.fillRect(5, 1, 8, 3); ctx.fillRect(0, 7, 18, 7);
    ctx.fillStyle = '#3f8d38'; ctx.fillRect(4, 3, 6, 5); ctx.fillRect(2, 9, 5, 4);
    ctx.fillStyle = '#204d1e'; ctx.fillRect(10, 10, 6, 6); ctx.fillRect(6, 14, 8, 3);
  } },
  lampadaire: { casse: 0.7, w: 8, h: 30, ancre: [3, 29], r: 2, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(2, 4, 2, 26); ctx.fillRect(0, 28, 6, 2);
    ctx.fillStyle = '#4a4d55'; ctx.fillRect(2, 2, 6, 2);
    ctx.fillStyle = '#ffe9a8'; ctx.fillRect(6, 3, 2, 3);
  } },
  poubelle: { casse: 0.85, w: 10, h: 14, ancre: [5, 13], r: 4, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#3f4a3c'; ctx.fillRect(1, 3, 8, 11);
    ctx.fillStyle = '#4c5a48'; ctx.fillRect(2, 4, 6, 9);
    ctx.fillStyle = '#2b332a'; ctx.fillRect(0, 1, 10, 3); ctx.fillRect(4, 5, 1, 8);
  } },
  banc: { casse: 0.8, w: 18, h: 12, ancre: [9, 11], r: 5, sol: [8, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(1, 4, 16, 3); ctx.fillRect(1, 0, 16, 3);
    ctx.fillStyle = '#523a22'; ctx.fillRect(2, 7, 2, 5); ctx.fillRect(14, 7, 2, 5);
    ctx.fillStyle = '#7d5a36'; ctx.fillRect(1, 4, 16, 1);
  } },
  caisse: { casse: 0.8, w: 16, h: 16, ancre: [8, 15], r: 6, sol: [7, 4], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#8a6a3f'; ctx.fillRect(1, 2, 14, 14);
    ctx.fillStyle = '#a07c4b'; ctx.fillRect(2, 3, 12, 5);
    ctx.fillStyle = '#6e5330'; ctx.fillRect(1, 8, 14, 1); ctx.fillRect(7, 2, 2, 14);
  } },
  buisson: { casse: 0.9, w: 16, h: 12, ancre: [8, 11], r: 5, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#2f6b2a'; ctx.fillRect(1, 3, 14, 8); ctx.fillRect(3, 1, 10, 3);
    ctx.fillStyle = '#3f8d38'; ctx.fillRect(3, 3, 5, 4); ctx.fillRect(9, 5, 4, 3);
    ctx.fillStyle = '#204d1e'; ctx.fillRect(2, 8, 12, 3);
  } },
  debris: { w: 14, h: 10, ancre: [7, 9], r: 4, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#6b6258'; ctx.fillRect(1, 5, 12, 5);
    ctx.fillStyle = '#807768'; ctx.fillRect(3, 2, 4, 4); ctx.fillRect(8, 4, 3, 3);
    ctx.fillStyle = '#544c44'; ctx.fillRect(2, 7, 3, 2); ctx.fillRect(9, 7, 4, 2);
  } },
  fontaine: { arrete: 9, w: 34, h: 30, ancre: [17, 27], r: 13, sol: [15, 6], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#8b877b'; ctx.fillRect(2, 10, 30, 17); ctx.fillRect(6, 7, 22, 21);
    ctx.fillStyle = '#a5a194'; ctx.fillRect(4, 12, 26, 3);
    ctx.fillStyle = '#2c5f8a'; ctx.fillRect(6, 14, 22, 11);
    ctx.fillStyle = '#3b73a3'; ctx.fillRect(9, 16, 7, 2); ctx.fillRect(19, 20, 6, 2);
    ctx.fillStyle = '#9a9689'; ctx.fillRect(15, 2, 4, 14);
    ctx.fillStyle = '#cfe6f5'; ctx.fillRect(14, 0, 6, 3); ctx.fillRect(13, 3, 2, 4); ctx.fillRect(19, 3, 2, 4);
  } },
  kiosque_hotdog: { arrete: 2.2, w: 26, h: 26, ancre: [13, 25], r: 10, sol: [9, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#c0392b'; ctx.fillRect(1, 2, 24, 5);              // parasol
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(4, 2, 4, 5); ctx.fillRect(13, 2, 4, 5);
    ctx.fillStyle = '#7a7d82'; ctx.fillRect(12, 7, 2, 6);              // mat
    ctx.fillStyle = '#9aa0a8'; ctx.fillRect(4, 13, 18, 9);             // comptoir
    ctx.fillStyle = '#6f757c'; ctx.fillRect(4, 13, 18, 2);
    ctx.fillStyle = '#d98324'; ctx.fillRect(7, 16, 5, 2); ctx.fillRect(14, 16, 5, 2);
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(5, 22, 3, 4); ctx.fillRect(18, 22, 3, 4);
  } },
  kiosque_journaux: { casse: 0.6, w: 24, h: 26, ancre: [12, 25], r: 9, sol: [10, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#2f6b8a'; ctx.fillRect(2, 4, 20, 18);
    ctx.fillStyle = '#24506f'; ctx.fillRect(2, 4, 20, 3);
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(4, 9, 7, 9); ctx.fillRect(13, 9, 7, 9);
    ctx.fillStyle = '#8a8698'; ctx.fillRect(5, 11, 5, 1); ctx.fillRect(5, 13, 5, 1);
    ctx.fillRect(14, 11, 5, 1); ctx.fillRect(14, 13, 5, 1);
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(3, 22, 18, 4);
  } },
  roulotte_cafe: { arrete: 2.6, w: 28, h: 24, ancre: [14, 23], r: 11, sol: [12, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(2, 4, 24, 14);
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 4, 24, 3);
    ctx.fillStyle = '#2c2c2c'; ctx.fillRect(6, 9, 16, 6);
    ctx.fillStyle = '#d98324'; ctx.fillRect(8, 11, 4, 2); ctx.fillRect(16, 11, 4, 2);
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(5, 18, 5, 5); ctx.fillRect(18, 18, 5, 5);
    ctx.fillStyle = '#101018'; ctx.fillRect(6, 20, 3, 3); ctx.fillRect(19, 20, 3, 3);
  } },
  // La boite au sol n'a pas bouge : la caisse va toujours de x 2 a 42.
  camion_cuisine: { arrete: 3.4, w: 44, h: 35, ancre: [22, 34], r: 16, sol: [20, 4], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(0,0,0,0.28)'; ctx.fillRect(3, 32, 38, 3);     // l'ombre sous la caisse
    peindreGrilleDecor(ctx, PAL_CAMION_CUISINE, GRILLE_CAMION_CUISINE);
    // ⚠️ Des lettres NOIRES : en rouge sur le creme, a 3 px de large, le mot
    // ne se lisait plus a l'echelle du jeu. Le rouge, c'est l'auvent qui le porte.
    Atlas.texte(ctx, 'POUTINE', 4, 1, '#101018', 1);                     // 7 lettres = 27 px, pile dans l'enseigne
  } },
  // La cabane a fruits de mer : un toit de toles rayees sur deux poteaux, un
  // comptoir de planches avec la glace et ce qu'il y a dessus (deux homards,
  // des crevettes), et l'enseigne au pied. ⚠️ Le toit s'arrete a la rangee 3 :
  // le marchand a les pieds 11 px au-dessus de l'ancre (`creerAmbulants`),
  // ses yeux tombent donc a la rangee 5 — un toit plus bas les cachait, et on
  // se faisait servir par un chapeau. Le comptoir, lui, couvre ses jambes.
  cabane_fruits_de_mer: { arrete: 2.6, w: 30, h: 28, ancre: [15, 27], r: 11, sol: [13, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#1d666d'; ctx.fillRect(0, 0, 30, 4);                                   // le toit
    ctx.fillStyle = '#c2f0ea'; for (let x = 2; x < 30; x += 6) ctx.fillRect(x, 0, 3, 4);     // ses rayures
    ctx.fillStyle = '#14454a'; ctx.fillRect(0, 4, 30, 1);
    ctx.fillStyle = '#6b4520'; ctx.fillRect(1, 5, 2, 9); ctx.fillRect(27, 5, 2, 9);           // les poteaux
    ctx.fillStyle = '#8a5a2c'; ctx.fillRect(1, 14, 28, 8);                                   // le comptoir
    ctx.fillStyle = '#6b4520'; ctx.fillRect(1, 14, 28, 1); ctx.fillRect(1, 21, 28, 1);
    ctx.fillStyle = '#dff6f4'; ctx.fillRect(3, 15, 24, 5);                                   // le lit de glace
    ctx.fillStyle = '#c0392b'; ctx.fillRect(5, 16, 6, 3); ctx.fillRect(19, 16, 6, 3);         // deux homards
    ctx.fillStyle = '#7a2420'; ctx.fillRect(5, 16, 1, 3); ctx.fillRect(24, 16, 1, 3);         // leurs pinces
    ctx.fillStyle = '#f3a683'; ctx.fillRect(13, 16, 4, 2);                                   // les crevettes
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(2, 22, 26, 6);                                   // l'enseigne
    ctx.fillStyle = '#14454a'; ctx.fillRect(2, 22, 26, 1);
    Atlas.texte(ctx, 'HOMARD', 4, 23, '#7a2420', 1);                                         // 6 lettres = 23 px
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
