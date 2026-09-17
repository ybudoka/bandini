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
      // ⚠️ LES SIX GESTES D'UNE SCENE (`Scenes`, plan `geste`), dessines UNE fois
      // pour tout le monde : les personnages de l'histoire portent tous ce sprite
      // repeint, ceux d'aujourd'hui et ceux de M16. Une image, sur la pose
      // immobile ; « cote » se miroite comme la marche. Aucun sprite par mission.
      geste_montrer_bas: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccckkk', '.kckcccccccs', '.kckccccckkk', '.kskccccck..', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_montrer_haut: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccckkk', '.kckcccccccs', '.kckccccckkk', '.kskccccck..', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_montrer_cote: [['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khssssk..', '...khsssk...', '....kssk....', '...kcccckkk.', '...kcccccccs', '...kcckkkkk.', '...kcck.....', '...kppppk...', '...kppppk...', '...kpkkpk...', '...kbk.kbk..', '...kkk.kkk..']],
      geste_donner_bas: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '.kckccccck..', '.kckcccccckk', '.kskccccccss', '..kppppppkkk', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_donner_haut: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '.kckccccck..', '.kckcccccck.', '.kskccccck..', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_donner_cote: [['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khssssk..', '...khsssk...', '....kssk....', '...kcccck...', '...kcccck...', '...kcccckkk.', '...kcccccss.', '...kppppkkk.', '...kppppk...', '...kpkkpk...', '...kbk.kbk..', '...kkk.kkk..']],
      geste_prendre_bas: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '.kkcccccckk.', '.kcckcckcck.', '.kssk..kssk.', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_prendre_haut: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_prendre_cote: [['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khssssk..', '...khsssk...', '....kssk....', '...kcccck...', '...kccccckk.', '...kcccccsk.', '...kccccss..', '...kppppkk..', '...kppppk...', '...kpkkpk...', '...kbk.kbk..', '...kkk.kkk..']],
      geste_bras_croises_bas: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '.kkkkkkkkkk.', '.ksccccccsk.', '..kkkkkkkk..', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_bras_croises_haut: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '.kckccccckc.', '.kkkccccckkk', '..kcccccck..', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_bras_croises_cote: [['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khssssk..', '...khsssk...', '....kssk....', '...kcccck...', '...kkkkkk...', '...kcccsk...', '...kkkkkk...', '...kppppk...', '...kppppk...', '...kpkkpk...', '...kbk.kbk..', '...kkk.kkk..']],
      geste_hausser_bas: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '.k.kssssk.k.', '.kkcccccckk.', 'sk.kcccck.ks', '...kcccck...', '...kcccck...', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_hausser_haut: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '.k.kssssk.k.', '.kkcccccckk.', 'sk.kcccck.ks', '...kcccck...', '...kcccck...', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_hausser_cote: [['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khssssk..', '...khsssk...', '....ksskk...', '...kcccck.s.', '...kcccckk..', '...kcccck...', '...kcccck...', '...kppppk...', '...kppppk...', '...kpkkpk...', '...kbk.kbk..', '...kkk.kkk..']],
      geste_telephone_bas: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshkk.', '..ksossoskkk', '..kssssssks.', '...ksssskck.', '..kccccccck.', '.kckccccck..', '.kckccccckc.', '.kskcccck...', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_telephone_haut: [['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhkk.', '..khhhhhhkkk', '..khsssshks.', '...ksssskck.', '..kccccccck.', '.kckccccck..', '.kckccccckc.', '.kskcccck...', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.']],
      geste_telephone_cote: [['....kkkk....', '...khhhhk...', '...khhhhhk..', '..kkhssosk..', '..kkhssssk..', '..ksksssk...', '...kkssk....', '...kcccck...', '...kcccck...', '...kcccck...', '...kcccck...', '...kppppk...', '...kppppk...', '...kpkkpk...', '...kbk.kbk..', '...kkk.kkk..']],
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
SPRITES.mascotte = {
  w: 16, h: 20, ancre: [8, 19],
  pal: { k: '#101018', h: '#8a5a2b', s: '#efe0c0', c: '#c0392b', p: '#4a3320', o: '#ffffff' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['..khk.kkkk.khk..', '.khhhkhhhhkhhhk.', 'khhshhhhhhhhshhk', '.khhhhhhhhhhhhk.', '..khhhhhhhhhhk..', '.khhhohhhhohhhk.', '.khhhksssskhhhk.', '.khhhsskksshhhk.', '..khsssssssshk..', '..khhsksskshhk..', '...khhskkshhk...', '....khhhhhhk....', '..kkhhcccchhkk..', '.khhhhhcchhhhhk.', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '.kskhhhhhhhhksk.', '..kkppphhpppkk..', '...kpppkkpppk...', '....kkk..kkk....'],
      ['..khk.kkkk.khk..', '.khhhkhhhhkhhhk.', 'khhshhhhhhhhshhk', '.khhhhhhhhhhhhk.', '..khhhhhhhhhhk..', '.khhhohhhhohhhk.', '.khhhksssskhhhk.', '.khhhsskksshhhk.', '..khsssssssshk..', '..khhsksskshhk..', '...khhskkshhk...', '....khhhhhhk....', '..kkhhcccchhkk..', '.khhhhhcchhhhhk.', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '.kskppphhhhhksk.', '..kkppphhpppkk..', '....kkkkkpppk...', '.........kkk....'],
      ['..khk.kkkk.khk..', '.khhhkhhhhkhhhk.', 'khhshhhhhhhhshhk', '.khhhhhhhhhhhhk.', '..khhhhhhhhhhk..', '.khhhohhhhohhhk.', '.khhhksssskhhhk.', '.khhhsskksshhhk.', '..khsssssssshk..', '..khhsksskshhk..', '...khhskkshhk...', '....khhhhhhk....', '..kkhhcccchhkk..', '.khhhhhcchhhhhk.', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '.kskhhhhhpppksk.', '..kkppphhpppkk..', '...kpppkkkkk....', '....kkk.........'],
      ['..khk.kkkk.khk..', '.khhhkhhhhkhhhk.', 'khhshhhhhhhhshhk', '.khhhhhhhhhhhhk.', '..khhhhhhhhhhk..', '.khhhohhhhohhhk.', '.khhhksssskhhhk.', '.khhhsskksshhhk.', 'kskhsssssssshksk', 'khkhhsksskshhkhk', 'khkkhhskkshhkkhk', 'khk.khhhhhhk.khk', '.k.khhcccchhk.k.', '..khhhhcchhhhk..', '..khhhhhhhhhhk..', '..khhhhhhhhhhk..', '...kppphhhhhk...', '...kppphhpppk...', '....kkkkkpppk...', '.........kkk....'],
      ['..khk.kkkk.khk..', '.khhhkhhhhkhhhk.', 'khhshhhhhhhhshhk', '.khhhhhhhhhhhhk.', '..khhhhhhhhhhk..', '.khhhohhhhohhhk.', '.khhhksssskhhhk.', '.khhhsskksshhhk.', 'kskhsssssssshksk', 'khkhhsksskshhkhk', 'khkkhhskkshhkkhk', 'khk.khhhhhhk.khk', '.k.khhcccchhk.k.', '..khhhhcchhhhk..', '..khhhhhhhhhhk..', '..khhhhhhhhhhk..', '...khhhhhpppk...', '...kppphhpppk...', '...kpppkkkkk....', '....kkk.........'],
    ],
    haut: [
      ['..khk.kkkk.khk..', '.khhhkhhhhkhhhk.', 'khhhhhhhhhhhhhhk', '.khhhhhhhhhhhhk.', '..khhhhhhhhhhk..', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '..khhhhhhhhhhk..', '..khhhhhhhhhhk..', '...khhhhhhhhk...', '....khhhhhhk....', '..kkhhcccchhkk..', '.khhhhhcchhhhhk.', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '.kskhhhhhhhhksk.', '..kkppphhpppkk..', '...kpppkkpppk...', '....kkk..kkk....'],
      ['..khk.kkkk.khk..', '.khhhkhhhhkhhhk.', 'khhhhhhhhhhhhhhk', '.khhhhhhhhhhhhk.', '..khhhhhhhhhhk..', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '..khhhhhhhhhhk..', '..khhhhhhhhhhk..', '...khhhhhhhhk...', '....khhhhhhk....', '..kkhhcccchhkk..', '.khhhhhcchhhhhk.', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '.kskppphhhhhksk.', '..kkppphhpppkk..', '....kkkkkpppk...', '.........kkk....'],
      ['..khk.kkkk.khk..', '.khhhkhhhhkhhhk.', 'khhhhhhhhhhhhhhk', '.khhhhhhhhhhhhk.', '..khhhhhhhhhhk..', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '..khhhhhhhhhhk..', '..khhhhhhhhhhk..', '...khhhhhhhhk...', '....khhhhhhk....', '..kkhhcccchhkk..', '.khhhhhcchhhhhk.', '.khhhhhhhhhhhhk.', '.khhhhhhhhhhhhk.', '.kskhhhhhpppksk.', '..kkppphhpppkk..', '...kpppkkkkk....', '....kkk.........'],
    ],
    cote: [
      ['.....khkk.......', '...kkhhhhkk.....', '..khhhhhhhhk....', '.khhhhhhhhhhk...', '.khhhhhhhhhhk...', '.khhhhhhhhohk...', 'khhhhhhhhskssk..', '.khhhhhhsssssk..', '.khhhhhhssssssk.', '.khhhhhhhssksk..', '..khhhhhhhhkk...', '...kkhhhhhk.....', '...khhhhhcck....', '..khhhhhhhhhk...', '..khhhhhhhhhk...', '..khhhhhhhhhk...', '...khhhhhhhk....', '....kpppppk.....', '....kpppppk.....', '.....kkkkk......'],
      ['.....khkk.......', '...kkhhhhkk.....', '..khhhhhhhhk....', '.khhhhhhhhhhk...', '.khhhhhhhhhhk...', '.khhhhhhhhohk...', 'khhhhhhhhskssk..', '.khhhhhhsssssk..', '.khhhhhhssssssk.', '.khhhhhhhssksk..', '..khhhhhhhhkk...', '...kkhhhhhk.....', '...khhhhhcck....', '..khhhhhhhhhk...', '..khhhhhhhhhk...', '..khhhhhhhhhk...', '...khhhhhhhk....', '...kppphhppk....', '...kpppkkppk....', '....kkk..kk.....'],
      ['.....khkk.......', '...kkhhhhkk.....', '..khhhhhhhhk....', '.khhhhhhhhhhk...', '.khhhhhhhhhhk...', '.khhhhhhhhohk...', 'khhhhhhhhskssk..', '.khhhhhhsssssk..', '.khhhhhhssssssk.', '.khhhhhhhssksk..', '..khhhhhhhhkk...', '...kkhhhhhk.....', '...khhhhhcck....', '..khhhhhhhhhk...', '..khhhhhhhhhk...', '..khhhhhhhhhk...', '...khhhhhhhk....', '....kpphpppk....', '....kppkpppk....', '.....kk.kkk.....'],
    ],
    couche: [
      ['................', '................', '................', '................', '................', '................', '................', '................', '................', '..kkkkkk........', '.khhhhhhk.kk....', 'khhhhhhhhkhhkkk.', 'khhkhhhhhhhhhhhk', 'khhhshhhhhhhhhhk', 'khhhhhhhhhhhhhhk', '.khhhhhhhhhhhhhk', '..kkkkkkkkhhkkk.', '..........kk....', '................', '................'],
    ],
  },
};
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

/* --- Le parc : trois dessins, et c'est LE TOIT QUI ROULE ---------------------

   ⚠️ **HISTOIRE, depuis le 16 sept. 2026** : plus aucun char ne roule sur son
   toit. Tout le parc est EN VOLUME et se projette au cap (`Atlas.projeter`,
   `MACHINE_BERLINE` et « le parc en volume », plus bas). Ce qui suit raconte
   pourquoi le toit avait remplace le profil — et c'est ce qui a mene au volume :
   un dessin qui tourne comme son ombre, mais qui montre un flanc de profil.

   ⚠️ **Le dessin qui roule dans la rue est `haut` — le char vu d'en haut, nez
   au NORD — et il TOURNE**, cap par cap, comme son ombre (`Atlas.toitDe` et
   `Atlas.cuireCap`, 32 crans). C'est la lecon du 15 septembre 2026 : un char
   qui n'a que quatre dessins pour un cap continu ne se conduit pas. Le volant
   tourne, l'ombre pivote, et la caisse attend 45 degres avant de bouger — on
   lisait son cap sur son ombre. Une ELEVATION (le profil) ne se laisse pas
   tourner : un dessin de flanc pivote de 40 degres, c'est un char qui cabre.
   Une vue d'en haut, oui — et c'est elle qu'on garde.

   `bas` sert encore, mais pour UN DETAIL : ses PHARES. Les deux vues d'en haut
   sont le meme toit lu dans l'autre sens — `haut` ne montre que les feux
   arriere, `bas` que les phares — et le dessin qui tourne les porte tous les
   deux (`Atlas.toitDe` retourne les phares de `bas` sur le nez de `haut`),
   sinon un char qui vient vers nous roule tous phares eteints.

   ⚠️ **`cote` n'est plus dessine dans la rue.** Il reste ici, entier : c'est
   une belle elevation, et le jour ou un char se montre de profil sans rouler
   (une fiche de garage, un ecran-titre), elle est prete. Mais elle ne coute
   rien tant que personne ne l'appelle — l'atlas ne cuit que ce qu'on lui
   demande.

   ⚠️ **L'ancre est la ligne de sol** — le bas des pneus — et elle est la meme
   pour les trois dessins. Ce n'est PAS le point autour duquel le char tourne :
   celui-la est le centre de l'empreinte du catalogue, et c'est
   `Vehicules.centreDuToit` qui va le chercher, a une demi-longueur au nord de
   l'ancre. ⚠️ **La caisse fait la largeur du catalogue** (14 px pour l'auto),
   centree dans la grille : les pixels perdus ne coutent rien.

   La palette, elle, ne bouge pas : `c` est la carrosserie (echangee par
   couleur a la naissance), `x` / `y` les accents de toit (l'enseigne du taxi,
   le gyrophare de la police), `l` les phares, `t` les feux arriere.

   ⚠️ Et le char est TRAPU, et il faut le vouloir : a l'echelle du passant
   (9,1 px/m), un toit d'auto de 1,45 m fait 13 px de haut pour 28 de long. On
   ne peut pas l'allonger — c'est la rue qui tient la longueur. Donc un char
   court et large, et un passant plus grand que le toit d'une auto : ce qui est
   vrai dans la vie. */

/** Les tons d'un char debout, par-dessus sa palette : le rehaut `C` et
    l'ombre `D` de sa couleur (par `nuances`, la meme formule qu'a la
    naissance), et quatre tons FIXES qui ne changent pas avec la carrosserie —
    `M` le moyeu, `B` le chrome du pare-chocs, `G` le reflet d'une vitre, `E`
    l'ombre derriere la vitre. ⚠️ Majuscules, expres : aucune palette n'en a,
    et une lettre reprise par un char (le `s` vaut ombre ici et orange la) est
    exactement le genre de collision qu'on ne voit qu'en jeu. */
function nuancer(pal) {
  return Object.assign({ M: '#9a9ea6', B: '#c9ccd1', G: '#e6f6ff', E: '#3b556c' }, pal, nuances(pal.c));
}

/* ⚠️ LE BIAIS DU SOL de tout le parc : de combien l'axe nord-sud est ecrase quand
   une machine se projette. C'est le MEME que celui de son ombre
   (`vehicules.OMBRE.profondeur`), et un juge les tient d'accord.
   ⚠️ **0,75, pas 0,5** (retour de Martin : « oui plus long »). A 0,5, une berline
   vue de dos occupait 21 rangees pour 28 px de long — plus courte que ce qui la
   bloque, et plus courte que le toit tourne qu'elle remplacait. A 0,75, elle en
   occupe 28 : sa longueur, a la rangee pres. */
const BIAIS_DU_SOL = 0.75;

/* --- La berline : la carrosserie de l'auto, du taxi et de la police, EN VOLUME -

   ⚠️ **Demande de Martin, apres le velo : « je veux que tu fasses une belle job
   comme ca avec les voitures, commence par une ».** Le char qui roulait etait
   son TOIT tourne (la pose `haut`) : vers l'est, un toit couche sur le flanc,
   pas une auto de profil. Comme le velo, la berline est maintenant une machine
   decrite dans l'espace, et `Atlas.projeter` la dessine au cap ou elle roule :
   de profil ses quatre roues dans leurs passages, ses vitres et sa ceinture ;
   de trois quarts son capot, son pare-brise et son flanc ; de dos son coffre et
   ses feux. Les 32 caps suivent toujours l'ombre au cran pres.

   A l'echelle du passant (9,1 px/m) : 28 px de long pour 3 m, 14 de large, un
   toit a 11 px (1,20 m) et des roues de 6 — c'est ce qui la pose a cote d'un
   passant de 16 sans en faire un jouet ni un autobus.

   ⚠️ **Le profil est une SILHOUETTE EXTRUDEE** (`profil`), pas une boite : un
   capot et un pare-brise en pente, et des passages de roue — une boite ne sait
   faire ni l'un ni l'autre. L'habitacle est une deuxieme silhouette, plus
   etroite et posee en arriere du milieu, comme sur les grilles d'avant.

   ⚠️ `contour` : la silhouette est cernee de `k`, comme tout ce qui est dessine
   a la main dans la ville. Le velo n'en a pas — ses tubes d'un pixel en
   feraient des barres. */
/* --- LA CAISSE ET L'HABITACLE : une auto, c'est les deux ----------------------

   ⚠️ **Demande de Martin : « je veux aussi avoir parfois des différences
   structurelles, pas juste la couleur ».** Toutes les autos de la ville etaient
   la meme berline repeinte. Ce qui fait la silhouette d'une auto, c'est son
   HABITACLE — ou finit le toit, comment tombe l'arriere — bien plus que sa
   caisse : une compacte, une familiale et une camionnette partagent le meme
   capot, les memes roues et la meme empreinte au sol (le catalogue n'en connait
   qu'une, `auto`, et la conduite ne change pas d'un pixel).

   `CAISSE` est donc commune : roues, caisse pincee, ceinture, portieres,
   pare-chocs, phares et feux. `habitacle` fabrique le reste d'apres quatre
   nombres — le pied du pare-brise, le debut et la fin du toit, le pied de la
   lunette — et tout ce qui en decoule se place tout seul : les montants, le
   cadre des vitres, le reflet. Deux habitacles ecrits a la main, c'est deux
   cadres a tenir d'accord. */
const CAISSE = [
    ['roue', 8.6, 3.0, 'r', 'M', 'M', 2, 6.2],
    ['roue', 8.6, 3.0, 'r', 'M', 'M', 2, -6.2],
    ['roue', -8.6, 3.0, 'r', 'M', 'M', 2, 6.2],
    ['roue', -8.6, 3.0, 'r', 'M', 'M', 2, -6.2],
    // La caisse : le nez, le capot, le coffre, et les deux passages de roue.
    ['profil', [[14, 1.6], [14, 4.4], [12.8, 5.8], [-12.6, 6.0], [-14, 5.0], [-14, 1.6],
                [-12.0, 1.6], [-11.8, 3.4], [-10.6, 4.6], [-8.6, 5.0], [-6.6, 4.6], [-5.4, 3.4], [-5.2, 1.6],
                [5.2, 1.6], [5.4, 3.4], [6.6, 4.6], [8.6, 5.0], [10.6, 4.6], [11.8, 3.4], [12.0, 1.6]],
     [[-14.5, 5.6], [-12.8, 6.7], [-11.2, 7], [11.2, 7], [12.8, 6.7], [14.5, 5.6]], 'c', 'DcccDDkkkkkkkkkkkkkkk'],
    ['tube', [11.2, 7, 5.9], [-11.2, 7, 6.0], 'C', 0.05],                 // la ligne de ceinture
    ['tube', [11.2, -7, 5.9], [-11.2, -7, 6.0], 'C', 0.05],
    ['tube', [12.8, 6.7, 5.9], [11.2, 7, 5.9], 'C', 0.05],                // ... qui suit le nez
    ['tube', [12.8, -6.7, 5.9], [11.2, -7, 5.9], 'C', 0.05],
    ['tube', [-12.6, 6.72, 6.0], [-11.2, 7, 6.0], 'C', 0.05],             // ... et la queue
    ['tube', [-12.6, -6.72, 6.0], [-11.2, -7, 6.0], 'C', 0.05],
    ['tube', [-0.2, 7.03, 1.8], [-0.2, 7.03, 5.6], 'D', 0.03],            // la fente des portieres
    ['tube', [-0.2, -7.03, 1.8], [-0.2, -7.03, 5.6], 'D', 0.03],
    ['bloc', [13.8, 14.5], [-5.6, 5.6], [1.6, 2.8], 'B', 'B', 'B', 0.1],  // pare-chocs
    ['bloc', [-14.5, -13.8], [-5.6, 5.6], [1.6, 2.8], 'B', 'B', 'B', 0.1],
    // ⚠️ Phares et feux ENVELOPPENT le coin : poses dans la caisse, ils ne se
    // voyaient que de face ou de dos (4 caps sur 32), et un char de profil
    // roulait tous feux eteints.
    ['bloc', [12.4, 14.4], [3.4, 6.8], [3.2, 4.6], 'l', 'l', 'l', 0.2],   // phares
    ['bloc', [12.4, 14.4], [-6.8, -3.4], [3.2, 4.6], 'l', 'l', 'l', 0.2],
    ['bloc', [-14.4, -12.4], [3.4, 6.8], [3.4, 4.8], 't', 't', 't', 0.2], // feux
    ['bloc', [-14.4, -12.4], [-6.8, -3.4], [3.4, 4.8], 't', 't', 't', 0.2],
];
/** L'habitacle d'une auto : `avant` le pied du pare-brise, `toit` son debut et
    sa fin, `arriere` le pied de la lunette, `montant` la ou tombe le montant du
    milieu (null : une seule portiere).

    ⚠️ LE CADRE DES VITRES (retour de Martin : « une légère séparation entre le
    pare-brise et le reste pour mieux démarquer de face et de dos »). Les
    montants bordent les cotes ; en haut et en bas, un trait `D` — l'ombre de la
    caisse, comme les montants — ferme le cadre sans cerner la vitre de noir.
    ⚠️ Celui du BAS monte un peu sur la vitre (7 % de sa hauteur au pare-brise,
    8 % a la lunette) et passe devant d'une avance de 1 : pose au pied de la
    vitre, le capot passait devant lui au meme pixel et il disparaissait. */
function habitacle(h) {
  const av = h.avant, ar = h.arriere, ta = h.toit[0], tr = h.toit[1];
  // ⚠️ Les HAUTEURS et la LARGEUR ont leurs valeurs de berline par defaut : le
  // pied du pare-brise a 5,9, celui de la lunette un dixieme plus haut, le toit
  // a 11, les vitres a 5,8 du milieu. Une sport est plus basse, un camion plus
  // haut et plus large — la meme recette, d'autres nombres.
  const bas = h.bas === undefined ? 5.9 : h.bas, haut = h.haut === undefined ? 11.0 : h.haut;
  const demi = h.demi === undefined ? 5.8 : h.demi, basAr = bas + 0.1;
  const pieces = [
    // Le pare-brise, le toit, la lunette ; ses flancs sont les vitres.
    ['profil', [[av, bas], [ta, haut], [tr, haut], [ar, basAr]], [-demi, demi], 'E', 'vCv.'],
    // Le reflet du pare-brise, au tiers de sa hauteur.
    ['tube', [av + (ta - av) / 3, -(demi - 0.8), bas + (haut - bas) / 3], [av + (ta - av) / 3, demi - 0.8, bas + (haut - bas) / 3], 'G', 0.3],
  ];
  const piedAv = [av + (ta - av) * 0.07, bas + (haut - bas) * 0.07], piedAr = [ar + (tr - ar) * 0.03, basAr + (haut - basAr) * 0.03];
  [-1, 1].forEach(function (s) {
    if (s < 0) {
      pieces.push(['tube', [piedAv[0], -demi, piedAv[1]], [piedAv[0], demi, piedAv[1]], 'D', 1.0]);   // pied du pare-brise
      pieces.push(['tube', [ta, -demi, haut], [ta, demi, haut], 'D', 0.6]);                           // haut du pare-brise
      pieces.push(['tube', [piedAr[0], -demi, piedAr[1]], [piedAr[0], demi, piedAr[1]], 'D', 1.6]);   // pied de la lunette
      pieces.push(['tube', [tr, -demi, haut], [tr, demi, haut], 'D', 0.6]);                           // haut de la lunette
    }
    const w = s * (demi + 0.1);
    pieces.push(['tube', [av, w, bas], [ta, w, haut], 'D', 0.05]);        // les montants
    if (h.montant !== null) pieces.push(['tube', [h.montant, w, basAr], [h.montant, w, haut], 'D', 0.05]);
    (h.custode ? [h.custode] : []).forEach(function (u) { pieces.push(['tube', [u, w, basAr], [u, w, haut], 'D', 0.05]); });
    pieces.push(['tube', [tr, w, haut], [ar, w, basAr], 'D', 0.05]);
    pieces.push(['tube', [ta, w, haut], [tr, w, haut], 'D', 0.05]);
  });
  return pieces;
}
const MACHINE_BERLINE = {
  profondeur: BIAIS_DU_SOL,
  contour: true,
  // ⚠️ ARRONDIE, et legerement (retour de Martin : « arrondit un peu (léger)
  // les véhicules ») : un pixel de moins aux coins vifs de la silhouette, et
  // une caisse qui se pince au nez et a la queue (le PLAN de la caisse, plus
  // bas). Une boite a angles vifs se lisait comme un pave peint.
  arrondi: true,
  pieces: CAISSE.concat(habitacle({ avant: 5.0, toit: [1.4, -6.2], arriere: -9.4, montant: -1.8 })),
};
/* ⚠️ **LA LIVREE N'EST PAS DE LA CARROSSERIE.** Elle etait peinte dans la grille
   commune, en `x` et `y`, et l'auto les rendait invisibles en les mettant a SA
   couleur de palette — le rouge. Mais une auto nait de n'importe quelle couleur
   du catalogue, et seul `c` change avec elle : une berline bleu marine aurait
   roule avec une bande et un damier ROUGES sur le flanc (ca ne se voyait pas
   tant que le flanc ne se dessinait pas). Le taxi et la police AJOUTENT donc
   leur livree a la carrosserie ; l'auto n'en porte pas. */
const LIVREE = [
  ['tube', [11.2, 7.02, 5.2], [-11.2, 7.02, 5.2], 'y', 0.03],             // la bande, sous la ceinture
  ['tube', [11.2, -7.02, 5.2], [-11.2, -7.02, 5.2], 'y', 0.03],
  ['damier', [4.8, -4.8], 4.4, 7.02, 'x'],                                // le damier, entre les roues
  ['damier', [4.8, -4.8], 4.4, -7.02, 'x'],
];
/* --- LE TOIT, COMME EN VRAI : l'enseigne du taxi, la rampe de la police ---------

   ⚠️ **Demande de Martin : « taxi et tous les véhicules qui en ont besoin
   doivent avoir des indicateurs ou gyrophare sur leur toit. comme en vrai. »**
   Aucun char n'en avait : la police n'a jamais eu de rampe, et les dessins de
   dos de l'ambulance et de la remorqueuse n'avaient ni gyrophare ni croix.

   L'enseigne du taxi est ALLUMEE (`e`, et `q` pour ses flancs), avec une ligne
   sombre en travers : a quatre pixels, c'est ce qui se lit « TAXI ». La rampe
   de la police est rouge a gauche (`a`) et bleue a droite (`b`) — ETEINTE dans
   la palette, et c'est la fiche (`gyrophares`) qui dit quand elle tourne. */
const ENSEIGNE_TAXI = [
  ['bloc', [-3.4, -1.4], [-2.6, 2.6], [11.0, 12.6], 'e', 'q', 'q', 0.2],
  ['tube', [-3.45, 2.65, 11.8], [-1.35, 2.65, 11.8], 'k', 0.3],
  ['tube', [-3.45, -2.65, 11.8], [-1.35, -2.65, 11.8], 'k', 0.3],
];
const RAMPE_POLICE = [
  ['bloc', [-3.0, -1.8], [-4.6, -0.3], [11.0, 11.9], 'a', 'a', 'a', 0.2],
  ['bloc', [-3.0, -1.8], [0.3, 4.6], [11.0, 11.9], 'b', 'b', 'b', 0.2],
  ['bloc', [-3.0, -1.8], [-0.3, 0.3], [11.0, 11.6], 'B', 'B', 'B', 0.2],
];
/* --- Les autos qui ne sont pas toutes la meme -------------------------------------

   Une COMPACTE : le toit file jusqu'au hayon, qui tombe presque droit.
   Une FAMILIALE : le toit va jusqu'au bout, une vitre de custode de plus et des
   barres de toit. Une CAMIONNETTE : une cabine courte, et une benne ouverte
   dont on voit le fond.
   ⚠️ Rien d'autre ne change : la meme caisse, les memes roues, la meme empreinte
   — c'est encore une `auto` du catalogue, et elle se conduit comme telle. */
const MACHINE_COMPACTE = Object.assign({}, MACHINE_BERLINE, {
  pieces: CAISSE.concat(habitacle({ avant: 5.0, toit: [1.4, -8.8], arriere: -12.2, montant: -2.2 })),
});
const MACHINE_FAMILIALE = Object.assign({}, MACHINE_BERLINE, {
  pieces: CAISSE.concat(habitacle({ avant: 5.0, toit: [1.4, -11.6], arriere: -12.6, montant: -2.2, custode: -7.4 }), [
    ['tube', [0.2, 4.8, 11.4], [-11.0, 4.8, 11.4], 'B', 0.1],           // les barres de toit
    ['tube', [0.2, -4.8, 11.4], [-11.0, -4.8, 11.4], 'B', 0.1],
  ]),
});
const MACHINE_CAMIONNETTE = Object.assign({}, MACHINE_BERLINE, {
  pieces: CAISSE.concat(habitacle({ avant: 5.0, toit: [1.4, -2.0], arriere: -2.8, montant: null }), [
    ['bloc', [-13.6, -3.4], [6.0, 6.8], [5.9, 7.6], 'c', 'c', 'D', 0.1],  // les ridelles
    ['bloc', [-13.6, -3.4], [-6.8, -6.0], [5.9, 7.6], 'c', 'c', 'D', 0.1],
    ['bloc', [-14.0, -13.4], [-6.0, 6.0], [5.9, 7.6], 'c', 'D', 'D', 0.1], // le hayon
    ['bloc', [-13.4, -3.4], [-6.0, 6.0], [6.0, 6.2], 'D', 'D', 'D', 0.05], // le fond de la benne, dans l'ombre des ridelles
  ]),
});
const MACHINE_TAXI = Object.assign({}, MACHINE_BERLINE, { pieces: MACHINE_BERLINE.pieces.concat(LIVREE, ENSEIGNE_TAXI) });
const MACHINE_POLICE = Object.assign({}, MACHINE_BERLINE, { pieces: MACHINE_BERLINE.pieces.concat(LIVREE, RAMPE_POLICE) });

/* --- Les deux-roues : decrits EN VOLUME, et projetes au cap -------------------

   ⚠️ **Retour de Martin, capture a l'appui : « il faut ameliorer ca ».** Le
   velo qui roulait etait son TOIT, tourne comme celui d'un char — et vu d'en
   haut, un velo est un baton avec une barre en travers. Le cycliste, lui, est
   de profil : on lisait un passant assis sur une echasse. Un toit d'auto dit
   ce qu'il est ; celui d'un velo ne dit rien.

   Alors la machine n'est plus une grille : c'est une liste de PIECES dans
   l'espace, et `Atlas.projeter` la dessine au cap ou elle roule. De profil,
   deux roues rondes et un cadre ; de dos, un trait, un guidon et un feu ; entre
   les deux, des roues en ellipse. Et elle suit toujours son ombre au cran pres.

   `u` vers l'avant, `w` vers la droite, `z` en haut, en pixels, le milieu de
   l'empreinte au sol en (0, 0, 0). ⚠️ A l'echelle du passant (9,1 px/m) : une
   roue de 70 cm fait 6,4 px, une selle a 80 cm monte a 7. C'est ce qui pose le
   cycliste — ses fesses sur la selle, ses mains au guidon, ses pieds aux
   pedales — et c'est pour ca que ces nombres ne se reglent pas a l'oeil.

   Les pieces :
     ['roue',  u, rayon, pneu, jante, moyeu, largeur]
     ['tube',  [u, w, z], [u, w, z], lettre, avance]
     ['point', [u, w, z], lettre, avance]
   ⚠️ Une lampe est un BLOC, pas un point : un point se cache derriere la
   premiere roue venue, et un deux-roues sans phare ni feu ne dit plus, de
   nuit, dans quel sens il roule. En bloc, les deux se voient a 28 caps sur 32.
     ['bloc',  [u0, u1], [w0, w1], [z0, z1], dessus, flanc, bout, avance]

   ⚠️ `profondeur` est le biais du sol, le MEME que celui de l'ombre
   (`vehicules.OMBRE`) : un juge les tient d'accord. */
const MACHINE_VELO = {
  profondeur: BIAIS_DU_SOL,
  // LES TROIS POINTS OU LE CORPS SE TIENT : ses fesses, sa main droite, son
  // pied droit. `assise` pose le cycliste (`deuxRoues` en tire la `selle`), et
  // les juges mesurent le corps dessine contre les trois.
  assise: [-2, 0, 7.2],
  guidon: [2.6, 2.6, 7.8],
  pedales: [-0.6, 1.6, 2.6],
  pieces: [
    ['roue', -4.8, 3.2, 'k', 'M', 'M'],
    ['roue', 4.8, 3.2, 'k', 'M', 'M'],
    ['tube', [-0.6, 0, 2.6], [-2.1, 0, 6.8], 'c'],        // tube de selle
    ['tube', [-2.0, 0, 6.3], [3.2, 0, 6.6], 'c'],         // tube horizontal
    ['tube', [-0.6, 0, 2.6], [3.3, 0, 5.6], 'c'],         // tube diagonal
    ['tube', [-0.6, 0, 2.6], [-4.8, 0, 3.2], 'D'],        // base
    ['tube', [-2.0, 0, 6.2], [-4.8, 0, 3.2], 'D'],        // hauban
    ['tube', [3.2, 0, 7.4], [4.8, 0, 3.2], 'B'],          // fourche
    ['tube', [2.6, -2.6, 7.8], [2.6, 2.6, 7.8], 'k', 0.4], // guidon
    ['tube', [2.6, 0, 7.8], [3.2, 0, 7.2], 'k', 0.4],     // potence
    ['tube', [-3.2, 0, 7.2], [-1.4, 0, 7.2], 'k', 0.4],   // selle
    ['tube', [-0.6, 0.6, 2.6], [0.6, 0.6, 1.6], 'M'],     // manivelle
    ['bloc', [3.6, 4.2], [-0.3, 0.3], [6.4, 7.0], 'l', 'l', 'l', 0.6], // le phare
    ['tube', [-2.2, 0, 6.4], [-5.4, 0, 6.4], 'D'],        // porte-bagages
    ['point', [-5.8, 0, 6.4], 't', 0.6],                  // le feu, au bout du porte-bagages
  ],
};
// ⚠️ La moto est plus LONGUE (20 px), pas plus haute : sa selle est a la meme
// hauteur que celle du velo, et le meme corps s'y assoit.
const MACHINE_MOTO = {
  profondeur: BIAIS_DU_SOL,
  assise: [-2, 0, 7.2],
  guidon: [2.8, 2.8, 8.2],
  pedales: [-1.0, 1.6, 3.0],
  pieces: [
    ['roue', -6.0, 3.4, 'k', 'M', 'M', 2],
    ['roue', 6.2, 3.4, 'k', 'M', 'M', 2],
    ['bloc', [-1.6, 2.4], [-1.2, 1.2], [2.2, 5.2], 'r', 'r', 'r'],      // moteur
    ['tube', [-1.2, 1.3, 4.6], [2.0, 1.3, 4.6], 'M', 0.2],               // ailettes
    ['tube', [-1.2, 1.3, 3.6], [2.0, 1.3, 3.6], 'M', 0.2],
    ['bloc', [0.4, 4.0], [-1.4, 1.4], [5.6, 7.6], 'c', 'D', 'D'],        // reservoir
    ['tube', [0.8, 0, 7.7], [3.6, 0, 7.7], 'C', 0.2],                    // son reflet
    ['bloc', [-4.8, 0.4], [-1.2, 1.2], [6.4, 7.2], 'k', 'k', 'k'],       // selle
    ['bloc', [-8.2, -4.8], [-0.9, 0.9], [5.8, 6.6], 'c', 'D', 'D'],      // queue
    ['tube', [-1.0, 1.7, 2.8], [-7.6, 1.7, 4.4], 'B'],                   // echappement
    ['tube', [-1.0, 1.0, 3.0], [-6.0, 0.8, 3.3], 'M'],                   // bras oscillant
    ['tube', [3.4, 0, 7.8], [6.2, 0, 3.3], 'B'],                         // fourche
    ['tube', [2.8, -2.8, 8.2], [2.8, 2.8, 8.2], 'k', 0.4],               // guidon
    ['bloc', [5.2, 6.4], [-0.8, 0.8], [6.6, 7.8], 'k', 'l', 'l', 0.2],   // phare
    ['bloc', [-8.6, -8.0], [-0.5, 0.5], [6.2, 6.8], 't', 't', 't', 0.3], // feu
  ],
};

const ASSIS_COTE = [
      '............',
      '............',
      '....kkkk....',
      '...khhhhk...',
      '...khhhhhk..',
      '...khssosk..',
      '...khssssk..',
      '...khsssk...',
      '....kssk....',
      '...kcccck...',
      '...kccccskk.',
      '...kcccccss.',
      '...kppppppk.',
      '...kpkkkppk.',
      '.......kbbk.',
      '.......kkk..',
    ];
const ASSIS_HAUT = [
      '............',
      '............',
      '....kkkk....',
      '...khhhhk...',
      '..khhhhhhk..',
      '..khhhhhhk..',
      '..khhhhhhk..',
      '..khsssshk..',
      '...kssssk...',
      '..kcccccck..',
      '.kckccccckc.',
      '.kskccccksk.',
      '..kppppppk..',
      '..kppkkppk..',
      '..kbbk.kbbk.',
      '..kkkk.kkkk.',
    ];
const ASSIS_BAS = [
      '............',
      '............',
      '....kkkk....',
      '...khhhhk...',
      '..khhhhhhk..',
      '..khsssshk..',
      '..ksossosk..',
      '..kssssssk..',
      '...kssssk...',
      '..kcccccck..',
      '.kckccccckc.',
      '.kskccccksk.',
      '..kppppppk..',
      '..kppkkppk..',
      '..kbbk.kbbk.',
      '..kkkk.kkkk.',
    ];

/* --- Le passant ASSIS ---------------------------------------------------------

   ⚠️ Le cycliste etait CUIT DANS LE VELO : la palette du velo portait une peau
   (`s`) et des cheveux (`h`), et tous les cyclistes de la ville avaient la meme
   tete pour toujours. Debout, le conducteur redevient ce qu'il aurait du etre :
   un passant assis dessus, avec ses propres couleurs — c'est le correctif des
   « sortes de gens » applique aux deux-roues. `Vehicules.dessinerUn` le pose
   sur la selle (`selle`, qui tourne avec la machine) avec les couleurs du
   joueur quand c'est lui, celles d'un archetype de rue quand c'est le trafic.

   Une pose de plus sur le corps du joueur, et une seule : `assis_cote` se
   miroite en `assis_gauche` / `assis_droite` par le suffixe, comme la marche.

   ⚠️ **Ce n'est plus la pose du deux-roues** (16 sept. 2026) : assis sur une
   chaise, il avait les fesses a la hauteur des moyeux et les pieds dans le
   vide. Sur une machine, c'est le passant qui ROULE (plus bas). Celle-ci reste
   la pose du patient qui attend dans une chaise. */
SPRITES.joueur.poses.assis_cote = [ASSIS_COTE];
SPRITES.joueur.poses.assis_haut = [ASSIS_HAUT];
SPRITES.joueur.poses.assis_bas = [ASSIS_BAS];

/* --- Le passant qui ROULE -------------------------------------------------------

   ⚠️ `assis` est un corps sur une CHAISE : les genoux devant, les pieds au sol.
   Pose sur une selle, il avait les fesses a la hauteur des moyeux et les pieds
   dans le vide. Celui-ci se tient sur la machine aux trois points qu'elle
   declare : les fesses sur la selle (a 7 px du sol), les mains au guidon, les
   pieds aux pedales.

   ⚠️ Le corps ne se PROJETTE pas comme la machine : c'est un corps, et il
   garde les quatre faces du passant. Mais chaque face est dessinee LA OU la
   projection met la selle et le guidon — de dos, le guidon est devant lui,
   donc plus HAUT a l'ecran : ses mains sont a hauteur d'epaules ; de face, il
   est plus BAS : ses mains tombent a la ceinture.

   Deux images par face : les pedales font un demi-tour de l'une a l'autre
   (`pedale` du sprite). La moto garde la premiere. */
SPRITES.joueur.poses.roule_cote = [
  ['.....kkkk...', '....khhhhk..', '....khhhhhk.', '....khhssok.', '....khssssk.', '...kkhsssk..', '..kcccckkk..', '..kccccsssk.',
   '..kppppkkk..', '...kkpppk...', '.....kppk...', '.....kpk....', '.....kpk....', '.....kbbk...', '.....kkk....', '............'],
  ['.....kkkk...', '....khhhhk..', '....khhhhhk.', '....khhssok.', '....khssssk.', '...kkhsssk..', '..kcccckkk..', '..kccccsssk.',
   '..kppppkkk..', '..kpppppk...', '...kkppk....', '....kpk.....', '...kpk......', '...kbbk.....', '...kkk......', '............'],
];
SPRITES.joueur.poses.roule_haut = [
  ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '.kkhhhhhhkk.', '.kskhhhhksk.', '.kckhhhhkck.', '.kckcccckck.', '..kcccccck..',
   '..kppppppk..', '..kpk..kpk..', '..kpk..kbk..', '..kbk..kkk..', '..kkk.......', '............', '............', '............'],
  ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '.kkhhhhhhkk.', '.kskhhhhksk.', '.kckhhhhkck.', '.kckcccckck.', '..kcccccck..',
   '..kppppppk..', '..kpk..kpk..', '..kbk..kpk..', '..kkk..kbk..', '.......kkk..', '............', '............', '............'],
];
SPRITES.joueur.poses.roule_bas = [
  ['............', '....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '...kssssk...', '..kcccccck..',
   '.kcccccccck.', '.ksccccccsk.', '..kppppppk..', '..kpk..kpk..', '..kpk..kbk..', '..kbk..kkk..', '..kkk.......', '............'],
  ['............', '....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '...kssssk...', '..kcccccck..',
   '.kcccccccck.', '.ksccccccsk.', '..kppppppk..', '..kpk..kpk..', '..kbk..kpk..', '..kkk..kbk..', '.......kkk..', '............'],
];

/* --- Le passant qui MENE UNE COQUE ---------------------------------------------

   ⚠️ Retour de Martin : « on devrait pouvoir voir le personnage ou un voleur assis
   dans la chaloupe ». Assis au fond d'une coque, on ne voit de lui que ce qui
   depasse du plat-bord : la tete, les epaules, les bras, les genoux. Les rangees du
   bas sont VIDES a dessein, comme celles du malade alite — c'est la coque qu'on
   doit y voir.

   Deux postures, dictees par la fiche (`posture`) : `barre`, la main derriere lui
   sur la barre franche du hors-bord ; `volant`, les deux mains devant, au volant
   de la console. Les fesses sur le banc, la main a la barre : les juges les
   mesurent contre les points que la coque declare (`assise`, `barre`). */
SPRITES.joueur.poses.barre_cote = [[
  '............', '....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khssssk..', '...khsssk...', '....kssk....',
  '..kkcccck...', '.kskcccck...', '..kkcccck...', '...kppppppk.', '...kkkkkkk..', '............', '............', '............']];
SPRITES.joueur.poses.barre_haut = [[
  '............', '....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...',
  '..kcccccck..', '.kckcccckck.', '.kskccccckk.', '..kccccsk...', '..kppppppk..', '............', '............', '............']];
SPRITES.joueur.poses.barre_bas = [[
  '............', '....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...',
  '..kcccccck..', '.kckcccckk..', '.kskcccck...', '..kcccccck..', '.kppppppppk.', '.kkkkkkkkkk.', '............', '............']];
SPRITES.joueur.poses.volant_cote = [[
  '............', '....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khssssk..', '...khsssk...', '....kssk....',
  '...kcccckk..', '...kcccccsk.', '...kcccckk..', '...kppppppk.', '...kkkkkkk..', '............', '............', '............']];
SPRITES.joueur.poses.volant_haut = [[
  '............', '....kkkk....', '...khhhhk...', '..khhhhhhk..', '.kkhhhhhhkk.', '.kckhhhhkck.', '.kckssssksk.', '.kckcccckck.',
  '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kppppppk..', '............', '............', '............']];
SPRITES.joueur.poses.volant_bas = [[
  '............', '....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...',
  '..kcccccck..', '.kcccccccck.', '.kcccccccck.', '..kssccssk..', '.kppppppppk.', '.kkkkkkkkkk.', '............', '............']];

/* --- Le malade ALITE -----------------------------------------------------------

   ⚠️ Pas `couche` : `couche` est un corps A TERRE, en travers (un KO, un mort),
   et un malade couche en travers d'un lit d'une place deborderait des deux
   cotes. Celui-ci est couche DANS le lit, la tete au nord sur l'oreiller : on
   voit ses cheveux, sa figure, les epaules de sa jaquette et ses deux mains
   posees sur la couverture — et rien en dessous, parce que c'est la COUVERTURE
   du lit (`'r'`, plus bas) qui le couvre. Les quatre rangees du bas sont donc
   vides a dessein : c'est le lit qu'on doit y voir. */
const ALITE = [
      '............',
      '............',
      '............',
      '....kkkk....',
      '...khhhhk...',
      '...khsshk...',
      '...kssssk...',
      '...kssssk...',
      '....kssk....',
      '..kcccccck..',
      '.kcccccccck.',
      '.kscccccsk..',
      '..kk....kk..',
      '............',
      '............',
      '............',
    ];
SPRITES.joueur.poses.alite = [ALITE];

/* --- L'avocat du Brouillard ------------------------------------------------------

   ⚠️ Me Desjardins tient la table du fond du Brouillard, et la table etait VIDE :
   le point `avocat` n'etait qu'un comptoir invisible, le meme defaut que Bouchard
   et Josee avant qu'on les voie (retour de Martin : « je ne vois pas d'image de
   l'avocat dans le bar »).

   ⚠️ Un corps A LUI, et pas le corps commun repeint : un complet fonce sur le
   corps commun, c'est une Cravate. Ce qui se lit a douze pixels, c'est le V de
   la CHEMISE BLANCHE (`o`) et la CRAVATE ROUGE (`t`) qui le coupe — personne
   d'autre en ville n'en porte — puis les cheveux gris et la moustache. Meme
   alphabet que `joueur` (`c` le veston, `p` le pantalon) : les echanges du
   catalogue marchent pareil.

   Sa pose a lui est `assis_bas`, sur la chaise de sa table
   (`carte.ASSIS_OU_COUCHE`), dessinee sur celle du patient. La marche (de face,
   de dos, de cote) sert le jour ou on le frappe : il se leve et il se sauve.
   Pas de pose de coup — il ne frappe personne, il poursuit. */
SPRITES.avocat = {
  w: 12, h: 16, ancre: [6, 15],
  pal: { k: '#101018', s: '#e8b088', h: '#b4b4b4', c: '#3b3f4c', p: '#2c2f38', o: '#ffffff', t: '#b3262e', b: '#1c1612' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kshhhhsk..', '...kssssk...', '..kccotock..',
       '.kckcotockc.', '.kckcctcckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.'],
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kshhhhsk..', '...kssssk...', '..kccotock..',
       '.kckcotockc.', '.kckcctcckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kppk..kpk.', '..kbbk..kbk.', '..kkkk..kk..'],
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kshhhhsk..', '...kssssk...', '..kccotock..',
       '.kckcotockc.', '.kckcctcckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kpk..kppk.', '..kbk..kbbk.', '..kk..kkkk..'],
    ],
    // De dos : le col de la chemise depasse du veston.
    haut: [
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kccoocck..',
       '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kppk.kppk.', '..kbbk.kbbk.', '..kkkk.kkkk.'],
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kccoocck..',
       '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kppk..kpk.', '..kbbk..kbk.', '..kkkk..kk..'],
      ['....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kccoocck..',
       '.kckccccckc.', '.kckccccckc.', '.kskccccksk.', '..kppppppk..', '..kpppkpppk.', '..kpk..kppk.', '..kbk..kbbk.', '..kk..kkkk..'],
    ],
    cote: [
      ['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khsshhk..', '...khsssk...', '....kssk....', '...kccotk...',
       '...kccctk...', '...kcckck...', '...kccksk...', '...kppppk...', '...kppppk...', '...kpkkpk...', '...kbk.kbk..', '...kkk.kkk..'],
      ['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khsshhk..', '...khsssk...', '....kssk....', '...kccotk...',
       '...kccctk...', '...kcckck...', '...kccksk...', '...kppppk...', '...kppppk...', '..kpk..kpk..', '..kbk..kbk..', '..kkk..kkk..'],
      ['....kkkk....', '...khhhhk...', '...khhhhhk..', '...khssosk..', '...khsshhk..', '...khsssk...', '....kssk....', '...kccotk...',
       '...kccctk...', '...kcckck...', '...kccksk...', '...kppppk...', '...kppppk...', '....kppk....', '....kbbk....', '....kkkk....'],
    ],
    assis_bas: [
      ['............', '............', '....kkkk....', '...khhhhk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kshhhhsk..',
       '...kssssk...', '..kccotock..', '.kckcotockc.', '.kskcctcksk.', '..kppppppk..', '..kppkkppk..', '..kbbk.kbbk.', '..kkkk.kkkk.'],
    ],
    couche: [
      ['............', '............', '............', '............', '............', '............', '............',
       '..kkkkkk....', '.kpppppkkkk.', 'kppppppctcos', 'kppppppcccck', '.kpppppkccsk', '..kbbkk.kkk.', '..kkk.......', '............', '............'],
    ],
  },
};
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
//
// ⚠️ TROIS IMAGES QUI NE SONT PAS UNE MARCHE : la main qui gratte, en haut, au
// milieu, en bas. Il est a `vitesse: 0` — `imageDe` choisit son image d'apres
// la DISTANCE PARCOURUE, il n'en parcourt aucune, et il tombait donc sur
// l'image zero toute la partie. Les deux images qu'il avait etaient deux pas ;
// un musicien plante a un coin de rue n'a jamais eu de pas a faire. C'est
// `poseFixe` qui les choisit maintenant, AU TEMPO du morceau qu'il joue.
SPRITES.musicien = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#e8b088', h: '#3a2a1a', c: '#6b4b8a', p: '#2a2a3a', o: '#ffffff', g: '#c98d3a', b: '#3a2a1a' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kkkkkk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '.kcgggssck..', '.kcggggggck.', '..kcggggck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '.kcggggggck.', '.kcgggssck..', '..kcggggck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '.kcggggggck.', '.kcggggggck.', '..kcgssgck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
    ],
    haut: [
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '.kcccccccck.', '.kcgggggck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '.kcccccccck.', '.kcggggsck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '.kcccccccck.', '.kcgggggck..', '..kccsscck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
    ],
    cote: [
      ['...kkkkkk...', '...khhhhhk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kccccck..', '..kcgssggk..', '..kcgggggk..', '...kcgggk...', '....kppppk..', '...kpp.ppk..', '...kk...kk..'],
      ['...kkkkkk...', '...khhhhhk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kccccck..', '..kcgggggk..', '..kcgssggk..', '...kcgggk...', '....kppppk..', '...kpp.ppk..', '...kk...kk..'],
      ['...kkkkkk...', '...khhhhhk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kccccck..', '..kcgggggk..', '..kcgggggk..', '...kssggk...', '....kppppk..', '...kpp.ppk..', '...kk...kk..'],
    ],
  },
};
// Le mime : chapeau melon, visage blanc, chandail raye. Trois formes
// qu'aucun autre corps de la ville n'a.
//
// ⚠️ QUATRE NUMEROS, PAS DEUX PAS. Ses deux images etaient une marche — et il
// ne marche pas : il tenait donc l'image zero toute la partie, bras le long du
// corps, immobile au milieu de son attroupement. Un mime qui ne mime rien est
// un homme en chapeau. Les quatre : repos, LE MUR invisible (les deux mains a
// plat devant lui), LA BOITE (les mains en l'air, de chaque cote de la tete),
// LE SALUT (il se plie en deux, le bras qui balaie). `poseFixe` les enchaine.
SPRITES.amuseur = {
  w: 12, h: 13, ancre: [6, 12],
  // ⚠️ Le `d` est le BLEU MARINE de la mariniere, pas le noir du contour : a
  // douze pixels, une raie noire sur du creme se confond avec le contour et le
  // mime redevient une silhouette blanche.
  pal: { k: '#101018', s: '#e8b088', h: '#2a2a2a', c: '#efe6d0', p: '#1a1a22', o: '#ffffff', d: '#2b3a6b', b: '#1a1a22' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kkkkkk...', '..kkkkkkkk..', '...koooook..', '...kokkook..', '...kooooko..', '....kook....', '..kcccccck..', '..kddddddk..', '..kcccccck..', '..kddddddk..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..kkkkkkkk..', '...koooook..', '...kokkook..', '...kooooko..', '....kook....', 'sskcccccckss', 'kkkddddddkkk', '..kcccccck..', '..kddddddk..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..kkkkkkkk..', 's..koooook.s', 's..kokkook.s', 'k..kooooko.k', 'k...kook...k', '.kkcccccckk.', '..kddddddk..', '..kcccccck..', '..kddddddk..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['............', '...kkkkkk...', '..kkkkkkkk..', '...koooook..', '...kokkook..', '...kooooko..', '..kcccccck..', '..kddddddk..', 'sskcccccck..', '..kddddddk..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
    ],
    haut: [
      ['...kkkkkk...', '..kkkkkkkk..', '...khhhhhk..', '...khhhhhk..', '...khhhhhk..', '....kook....', '..kcccccck..', '..kddddddk..', '..kcccccck..', '..kddddddk..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..kkkkkkkk..', '...khhhhhk..', '...khhhhhk..', '...khhhhhk..', '....kook....', 'sskcccccckss', 'kkkddddddkkk', '..kcccccck..', '..kddddddk..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..kkkkkkkk..', 's..khhhhhk.s', 's..khhhhhk.s', 'k..khhhhhk.k', 'k...kook...k', '.kkcccccckk.', '..kddddddk..', '..kcccccck..', '..kddddddk..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['............', '...kkkkkk...', '..kkkkkkkk..', '...khhhhhk..', '...khhhhhk..', '...khhhhhk..', '..kcccccck..', '..kddddddk..', 'sskcccccck..', '..kddddddk..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
    ],
    cote: [
      ['...kkkkkk...', '..kkkkkkkk..', '...koooook..', '...kokkook..', '...kooook...', '....kok.....', '..kcccccck..', '..kddddddk..', '..kcccccck..', '..kddddddk..', '...kppppk...', '..kpp.ppk...', '..kk...kk...'],
      ['...kkkkkk...', '..kkkkkkkk..', '...koooook..', '...kokkook..', '...kooook...', '....kok.....', '..kcccccckss', '..kddddddkkk', '..kcccccck..', '..kddddddk..', '...kppppk...', '..kpp.ppk...', '..kk...kk...'],
      ['...kkkkkk...', '..kkkkkkkk..', '...koooook.s', '...kokkook.s', '...kooook..k', '....kok....k', '..kcccccck..', '..kddddddk..', '..kcccccck..', '..kddddddk..', '...kppppk...', '..kpp.ppk...', '..kk...kk...'],
      ['............', '...kkkkkk...', '..kkkkkkkk..', '...koooook..', '...kokkook..', '...kooook...', '..kcccccck..', '..kddddddk..', 'sskcccccck..', '..kddddddk..', '...kppppk...', '..kpp.ppk...', '..kk...kk...'],
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


// --- Deux amuseurs de plus (demande de Martin) -------------------------------
//
// ⚠️ « Ils ne font rien et sont ennuyants. » Le mime etait le SEUL genre
// d'amuseur de la ville, et il tenait l'image zero de son sprite du debut a la
// fin de la partie (`imageDe` choisit son image d'apres la DISTANCE PARCOURUE,
// et un corps a `vitesse: 0` n'en parcourt aucune). Ces deux-la ne sont pas
// deux costumes de plus : ce sont deux spectacles qu'on reconnait DE LOIN,
// avant meme de voir l'artiste. C'est tout ce qu'on demande a un amuseur.

// LE JONGLEUR — et les balles sont DANS LE SPRITE. ⚠️ Les dessiner a part
// aurait voulu dire un deuxieme chemin de dessin pour une seule sorte, trois
// objets de plus a trier par `y`, et un decalage d'une image entre le corps et
// ses balles des que la camera bouge. Ici, l'atlas cuit les quatre images une
// fois : trois balles sur quatre positions de l'arc, decalees d'un cran — la
// case vide tourne, et c'est ce qui donne le mouvement.
// Le sprite fait 14 x 19 : deux colonnes et six rangees de plus que les autres,
// pour l'arc au-dessus de sa tete.
SPRITES.jongleur = {
  w: 14, h: 19, ancre: [7, 18],
  pal: { k: '#101018', s: '#e8b088', h: '#3a2a1a', c: '#d4442e', p: '#f2c94c', o: '#ffffff',
         d: '#f2c94c', b: '#3a2a1a',
         // ⚠️ Les trois balles ne sont PAS echangeables (`swaps` ne les
         // contient pas) : c'est a leurs trois couleurs qu'on reconnait le
         // numero d'un coin de rue a l'autre.
         j: '#f7e04a', v: '#3fae5a', r: '#e8453c' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['.......rr.....', '.......rr.....', '....vv........', '....vv........', '..jj..........', '..jj..........', '....kkkkkk....', '...khhhhhhk...', '...khsssshk...', '...ksossosk...', '...kssssssk...', '....kssssk....', '..skccccccks..', '.sskcdddckss..', '..kcdddddck...', '...kcccccck...', '....kppppk....', '...kpp..ppk...', '...kk....kk...'],
      ['.......vv.....', '.......vv.....', '....jj....rr..', '....jj....rr..', '..............', '..............', '....kkkkkk....', '...khhhhhhk...', '...khsssshk...', '...ksossosk...', '...kssssssk...', '....kssssk....', '..skccccccks..', '.sskcdddckss..', '..kcdddddck...', '...kcccccck...', '....kppppk....', '...kpp..ppk...', '...kk....kk...'],
      ['.......jj.....', '.......jj.....', '..........vv..', '..........vv..', '..rr..........', '..rr..........', '....kkkkkk....', '...khhhhhhk...', '...khsssshk...', '...ksossosk...', '...kssssssk...', '....kssssk....', '..skccccccks..', '.sskcdddckss..', '..kcdddddck...', '...kcccccck...', '....kppppk....', '...kpp..ppk...', '...kk....kk...'],
      ['..............', '..............', '....rr....jj..', '....rr....jj..', '..vv..........', '..vv..........', '....kkkkkk....', '...khhhhhhk...', '...khsssshk...', '...ksossosk...', '...kssssssk...', '....kssssk....', '..skccccccks..', '.sskcdddckss..', '..kcdddddck...', '...kcccccck...', '....kppppk....', '...kpp..ppk...', '...kk....kk...'],
    ],
    haut: [
      ['.......rr.....', '.......rr.....', '....vv........', '....vv........', '..jj..........', '..jj..........', '....kkkkkk....', '...khhhhhhk...', '...khhhhhhk...', '...khhhhhhk...', '...khsssshk...', '....kssssk....', '..skccccccks..', '.sskccccccss..', '..kcccccccck..', '...kcccccck...', '....kppppk....', '...kpp..ppk...', '...kk....kk...'],
      ['.......vv.....', '.......vv.....', '....jj....rr..', '....jj....rr..', '..............', '..............', '....kkkkkk....', '...khhhhhhk...', '...khhhhhhk...', '...khhhhhhk...', '...khsssshk...', '....kssssk....', '..skccccccks..', '.sskccccccss..', '..kcccccccck..', '...kcccccck...', '....kppppk....', '...kpp..ppk...', '...kk....kk...'],
      ['.......jj.....', '.......jj.....', '..........vv..', '..........vv..', '..rr..........', '..rr..........', '....kkkkkk....', '...khhhhhhk...', '...khhhhhhk...', '...khhhhhhk...', '...khsssshk...', '....kssssk....', '..skccccccks..', '.sskccccccss..', '..kcccccccck..', '...kcccccck...', '....kppppk....', '...kpp..ppk...', '...kk....kk...'],
      ['..............', '..............', '....rr....jj..', '....rr....jj..', '..vv..........', '..vv..........', '....kkkkkk....', '...khhhhhhk...', '...khhhhhhk...', '...khhhhhhk...', '...khsssshk...', '....kssssk....', '..skccccccks..', '.sskccccccss..', '..kcccccccck..', '...kcccccck...', '....kppppk....', '...kpp..ppk...', '...kk....kk...'],
    ],
    cote: [
      ['.......rr.....', '.......rr.....', '....vv........', '....vv........', '..jj..........', '..jj..........', '....kkkkkk....', '....khhhhhk...', '....khsssok...', '....khssssk...', '....khsssk....', '.....kssk.....', '...skcccccks..', '..sskcdddcks..', '....kcdddck...', '....kccccck...', '.....kppppk...', '....kppk.kk...', '....kkk.......'],
      ['.......vv.....', '.......vv.....', '....jj....rr..', '....jj....rr..', '..............', '..............', '....kkkkkk....', '....khhhhhk...', '....khsssok...', '....khssssk...', '....khsssk....', '.....kssk.....', '...skcccccks..', '..sskcdddcks..', '....kcdddck...', '....kccccck...', '.....kppppk...', '....kppk.kk...', '....kkk.......'],
      ['.......jj.....', '.......jj.....', '..........vv..', '..........vv..', '..rr..........', '..rr..........', '....kkkkkk....', '....khhhhhk...', '....khsssok...', '....khssssk...', '....khsssk....', '.....kssk.....', '...skcccccks..', '..sskcdddcks..', '....kcdddck...', '....kccccck...', '.....kppppk...', '....kppk.kk...', '....kkk.......'],
      ['..............', '..............', '....rr....jj..', '....rr....jj..', '..vv..........', '..vv..........', '....kkkkkk....', '....khhhhhk...', '....khsssok...', '....khssssk...', '....khsssk....', '.....kssk.....', '...skcccccks..', '..sskcdddcks..', '....kcdddck...', '....kccccck...', '.....kppppk...', '....kppk.kk...', '....kkk.......'],
    ],
  },
};
// L'ECHASSIER — ⚠️ LE SEUL CORPS DE LA VILLE A DEPASSER LA FOULE : 26 pixels
// de haut au lieu de 13. C'est exactement pour ca qu'il existe — on le voit
// PAR-DESSUS son propre attroupement, de l'autre bout de la rue, et c'est la
// seule chose qu'un echassier fait qu'un homme ne fait pas. Un echassier a
// hauteur d'homme serait un homme.
// Il tangue : trois images, et les PIEDS NE BOUGENT PAS — c'est le haut qui
// penche. Un corps qui glisse d'un pixel avec ses echasses n'est pas un
// echassier qui se rattrape, c'est un dessin qu'on a pousse.
SPRITES.echassier = {
  w: 12, h: 26, ancre: [6, 25],
  pal: { k: '#101018', s: '#e8b088', h: '#5a3a1a', c: '#2f7f6f', p: '#c94f3a', o: '#ffffff',
         b: '#3a2a1a', e: '#9a6b3a' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kkkkkk...', '..kcccccck..', '..kcccccck..', '.kkkkkkkkkk.', '...ksssssk..', '...ksossok..', '...kssssk...', '..kcccccck..', '.kcccccccck.', '.kcccccccck.', '..kcccccck..', '..kppppppk..', '..kppppppk..', '..kppkkppk..', '..kppkkppk..', '..kkkkkkkk..', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '..kkkkkkkk..'],
      ['..kkkkkk....', '.kcccccck...', '.kcccccck...', 'kkkkkkkkkk..', '..ksssssk...', '..ksossok...', '..kssssk....', '.kcccccck...', 'kcccccccck..', 'kcccccccck..', '.kcccccck...', '.kppppppk...', '.kppppppk...', '.kppkkppk...', '.kppkkppk...', '.kkkkkkkk...', '..ee..ee....', '..ee..ee....', '..ee..ee....', '..ee..ee....', '..ee..ee....', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '..kkkkkkkk..'],
      ['....kkkkkk..', '...kcccccck.', '...kcccccck.', '..kkkkkkkkkk', '....ksssssk.', '....ksossok.', '....kssssk..', '...kcccccck.', '..kcccccccck', '..kcccccccck', '...kcccccck.', '...kppppppk.', '...kppppppk.', '...kppkkppk.', '...kppkkppk.', '...kkkkkkkk.', '....ee..ee..', '....ee..ee..', '....ee..ee..', '....ee..ee..', '....ee..ee..', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '..kkkkkkkk..'],
    ],
    haut: [
      ['...kkkkkk...', '..kcccccck..', '..kcccccck..', '.kkkkkkkkkk.', '...khhhhhk..', '...khhhhhk..', '...khhhhk...', '..kcccccck..', '.kcccccccck.', '.kcccccccck.', '..kcccccck..', '..kppppppk..', '..kppppppk..', '..kppkkppk..', '..kppkkppk..', '..kkkkkkkk..', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '..kkkkkkkk..'],
      ['..kkkkkk....', '.kcccccck...', '.kcccccck...', 'kkkkkkkkkk..', '..khhhhhk...', '..khhhhhk...', '..khhhhk....', '.kcccccck...', 'kcccccccck..', 'kcccccccck..', '.kcccccck...', '.kppppppk...', '.kppppppk...', '.kppkkppk...', '.kppkkppk...', '.kkkkkkkk...', '..ee..ee....', '..ee..ee....', '..ee..ee....', '..ee..ee....', '..ee..ee....', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '..kkkkkkkk..'],
      ['....kkkkkk..', '...kcccccck.', '...kcccccck.', '..kkkkkkkkkk', '....khhhhhk.', '....khhhhhk.', '....khhhhk..', '...kcccccck.', '..kcccccccck', '..kcccccccck', '...kcccccck.', '...kppppppk.', '...kppppppk.', '...kppkkppk.', '...kppkkppk.', '...kkkkkkkk.', '....ee..ee..', '....ee..ee..', '....ee..ee..', '....ee..ee..', '....ee..ee..', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '..kkkkkkkk..'],
    ],
    cote: [
      ['...kkkkkk...', '...kccccck..', '...kccccck..', '..kkkkkkkk..', '...ksssssk..', '...kssssok..', '....ksssk...', '...kccccck..', '..kcccccck..', '..kcccccck..', '...kccccck..', '...kppppk...', '...kppppk...', '..kppkkppk..', '..kppkkppk..', '..kkkkkkkk..', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '..kkkkkkkk..'],
      ['..kkkkkk....', '..kccccck...', '..kccccck...', '.kkkkkkkk...', '..ksssssk...', '..kssssok...', '...ksssk....', '..kccccck...', '.kcccccck...', '.kcccccck...', '..kccccck...', '..kppppk....', '..kppppk....', '.kppkkppk...', '.kppkkppk...', '.kkkkkkkk...', '..ee..ee....', '..ee..ee....', '..ee..ee....', '..ee..ee....', '..ee..ee....', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '..kkkkkkkk..'],
      ['....kkkkkk..', '....kccccck.', '....kccccck.', '...kkkkkkkk.', '....ksssssk.', '....kssssok.', '.....ksssk..', '....kccccck.', '...kcccccck.', '...kcccccck.', '....kccccck.', '....kppppk..', '....kppppk..', '...kppkkppk.', '...kppkkppk.', '...kkkkkkkk.', '....ee..ee..', '....ee..ee..', '....ee..ee..', '....ee..ee..', '....ee..ee..', '...ee..ee...', '...ee..ee...', '...ee..ee...', '...ee..ee...', '..kkkkkkkk..'],
    ],
  },
};


/* --- Les sept qui viennent avec ----------------------------------------------

   ⚠️ MEME REGLE : une sorte = un corps + une routine. Celles-ci ne sont pas la
   pour remplir la rue — chacune sert une fiche deja livree : la contractuelle
   rend « mal gare » VISIBLE avant que la fourriere n'avale le char, le touriste
   est le meilleur temoin de la ville, l'ivrogne est le seul qui ne fuit pas
   devant une arme, le jogger ne temoigne de rien, et le facteur fait ouvrir les
   portes. */

// ⚠️ LA VISIERE qui deborde de la tete et LE CARNET BLANC sur la poitrine :
// a douze pixels, c'est ce qui la nomme. On doit la reconnaitre de loin —
// c'est elle qui decide si on a le temps d'aller faire sa course.
SPRITES.contractuelle = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#f0c098', h: '#3a2a1a', c: '#2e5f8a', p: '#26324a', o: '#ffffff', v: '#1a3550', b: '#1a3550' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kccccck..', '..kvvvvvvvk.', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '..kcooocck..', '..kcooocck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kccccck..', '..kvvvvvvvk.', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '..kcooocck..', '..kcooocck..', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    haut: [
      ['...kccccck..', '..kcccccck..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kccccck..', '..kcccccck..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    cote: [
      ['...kccccck..', '..kvvvvvvk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kccccck..', '...kcoock...', '...kcoock...', '...kccccck..', '....kppppk..', '...kppk.kk..', '...kkk......'],
      ['...kccccck..', '..kvvvvvvk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kccccck..', '...kcoock...', '...kcoock...', '...kccccck..', '....kppppk..', '....kpk.kk..', '....kk......'],
    ],
  },
};
// Le chapeau LARGE (il deborde des deux cotes, personne d'autre n'en a),
// l'appareil photo sur la poitrine et le sac a dos quand il s'eloigne.
SPRITES.touriste = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#e8b088', h: '#8a6a3a', c: '#f2e2a8', p: '#8a7a5a', o: '#ffffff', a: '#e8dcae', l: '#2a2a2a', b: '#b05a3a' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kaaaak...', '.kaaaaaaaak.', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '..kcolocck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kaaaak...', '.kaaaaaaaak.', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', '..kcolocck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    haut: [
      ['...kaaaak...', '.kaaaaaaaak.', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcbbbbck..', '..kcbbbbck..', '..kcbbbbck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kaaaak...', '.kaaaaaaaak.', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcbbbbck..', '..kcbbbbck..', '..kcbbbbck..', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    cote: [
      ['...kaaaak...', '.kaaaaaaaak.', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '..kbcccck...', '..kbcolck...', '..kbcccck...', '...kccccck..', '....kppppk..', '...kppk.kk..', '...kkk......'],
      ['...kaaaak...', '.kaaaaaaaak.', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '..kbcccck...', '..kbcolck...', '..kbcccck...', '...kccccck..', '....kppppk..', '....kpk.kk..', '....kk......'],
    ],
  },
};
// La BARBE qui mange le bas du visage et la BOUTEILLE au poing, en dehors
// de la silhouette : deux formes qu'aucun autre corps de la ville n'a.
SPRITES.ivrogne = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#d8a878', h: '#8a8a8a', c: '#6a5a4a', p: '#4a4438', o: '#ffffff', g: '#4a7a3a', b: '#4a4438' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kkkkkk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..khhsshhk..', '...khhhhk...', '..kcccccck..', '.gkcccccck..', '.gkcccccck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..khhsshhk..', '...khhhhk...', '..kcccccck..', '.gkcccccck..', '.gkcccccck..', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    haut: [
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    cote: [
      ['...kkkkkk...', '...khhhhhk..', '...khsssok..', '...khhsssk..', '...khhhhk...', '....khhk....', '...kccccck..', '..gkccccck..', '..gkccccck..', '...kccccck..', '....kppppk..', '...kppk.kk..', '...kkk......'],
      ['...kkkkkk...', '...khhhhhk..', '...khsssok..', '...khhsssk..', '...khhhhk...', '....khhk....', '...kccccck..', '..gkccccck..', '..gkccccck..', '...kccccck..', '....kppppk..', '....kpk.kk..', '....kk......'],
    ],
  },
};
// Le BANDEAU blanc et les JAMBES NUES : le seul de la ville a ne pas porter
// de pantalon, et ca se lit d'un coup d'oeil.
SPRITES.jogger = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#e8b088', h: '#2a2a2a', c: '#e04a3a', p: '#2a2a2a', o: '#ffffff', b: '#ffffff' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kkkkkk...', '..kbbbbbbk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '.skcccccks..', '.skcccccks..', '..kcccccck..', '...kppppk...', '...kssssk...', '..kss..ssk..', '..kk....kk..'],
      ['...kkkkkk...', '..kbbbbbbk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '.skcccccks..', '.skcccccks..', '..kcccccck..', '...kppppk...', '...kssssk...', '..kssk.ksk..', '..kkk...kk..'],
    ],
    haut: [
      ['...kkkkkk...', '..kbbbbbbk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '.skcccccks..', '.skcccccks..', '..kcccccck..', '...kppppk...', '...kssssk...', '..kss..ssk..', '..kk....kk..'],
      ['...kkkkkk...', '..kbbbbbbk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '.skcccccks..', '.skcccccks..', '..kcccccck..', '...kppppk...', '...kssssk...', '..kssk.ksk..', '..kkk...kk..'],
    ],
    cote: [
      ['...kkkkkk...', '...kbbbbbk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '..skccccck..', '..skccccck..', '...kccccck..', '....kpppk...', '....kssssk..', '...kssk.kk..', '...kkk......'],
      ['...kkkkkk...', '...kbbbbbk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '..skccccck..', '..skccccck..', '...kccccck..', '....kpppk...', '....kssssk..', '....ksk.kk..', '....kk......'],
    ],
  },
};
// La sacoche EN BANDOULIERE (une diagonale du haut de l'epaule a la hanche)
// et la lettre blanche au poing.
SPRITES.facteur = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#e8b088', h: '#3a2a1a', c: '#2e6b4a', p: '#1f2f24', o: '#ffffff', v: '#1a3f2b', b: '#8a5a2a' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kccccck..', '..kvvvvvvvk.', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kbccccck..', '..kcbcccck..', '..kccbcock..', '..kcccbbck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kccccck..', '..kvvvvvvvk.', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kbccccck..', '..kcbcccck..', '..kccbcock..', '..kcccbbck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    haut: [
      ['...kccccck..', '..kcccccck..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kbccccck..', '..kcbcccck..', '..kccbccck..', '..kcccbbck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kccccck..', '..kcccccck..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kbccccck..', '..kcbcccck..', '..kccbccck..', '..kcccbbck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    cote: [
      ['...kccccck..', '..kvvvvvvk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kbcccck..', '...kcbcock..', '...kccbbck..', '...kccccck..', '....kppppk..', '...kppk.kk..', '...kkk......'],
      ['...kccccck..', '..kvvvvvvk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kbcccck..', '...kcbcock..', '...kccbbck..', '...kccccck..', '....kppppk..', '....kpk.kk..', '....kk......'],
    ],
  },
};


/* --- Trois qui gagnent leur vie dans la rue ----------------------------------

   ⚠️ Troisieme vague, et la meme regle depuis la premiere : une sorte = un
   corps + une routine. Celles-ci ont ete choisies pour leur CROCHET — le
   crieur hurle ce que TU as fait hier (`journal.py`), le laveur ne travaille
   qu'au feu rouge (les feux qu'on vient de livrer), et le pickpocket vole les
   AUTRES : un crime que tu n'as pas commis. */

// ⚠️ LA LIASSE BRANDIE (`o`, en dehors de la silhouette) et la casquette
// de gavroche : a douze pixels, c'est le bras tendu qui le nomme. Un
// crieur les bras le long du corps est un passant en rouge.
SPRITES.crieur = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#e8b088', h: '#3a2a1a', c: '#c0392b', p: '#3a3a4a', o: '#f4f0e4', v: '#7a2a20', b: '#7a2a20' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['..kvvvvk....', '.kcccccck...', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '.okcccccck..', 'ookcccccckoo', '.okcccccck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['..kvvvvk....', '.kcccccck...', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '.okcccccck..', 'ookcccccckoo', '.okcccccck..', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    haut: [
      ['..kvvvvk....', '.kcccccck...', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['..kvvvvk....', '.kcccccck...', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    cote: [
      ['...kvvvvk...', '..kcccccck..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '..okccccck..', '.ookccccck..', '..okccccck..', '...kccccck..', '....kppppk..', '...kppk.kk..', '...kkk......'],
      ['...kvvvvk...', '..kcccccck..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '..okccccck..', '.ookccccck..', '..okccccck..', '...kccccck..', '....kppppk..', '....kpk.kk..', '....kk......'],
    ],
  },
};
// ⚠️ LA RACLETTE EN TRAVERS, plus large que lui, et le SEAU jaune au
// pied. Deux formes qui sortent de la silhouette — c'est la seule facon
// de nommer un metier a cette taille-la.
SPRITES.laveur = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#c98d66', h: '#2a2a2a', c: '#2f6b8a', p: '#3a4450', o: '#ffffff', l: '#9aa0a6', g: '#d8b83a', b: '#3a4450' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kkkkkk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', 'lllllllllll.', '..kcccccck..', '..kcccccck..', '..kppppppk..', '.gkpp..ppkg.', '.gkk....kkg.'],
      ['...kkkkkk...', '..khhhhhhk..', '..khsssshk..', '..ksossosk..', '..kssssssk..', '...kssssk...', '..kcccccck..', 'lllllllllll.', '..kcccccck..', '..kcccccck..', '..kppppppk..', '.gkpp..ppkg.', '.gkk....kkg.'],
    ],
    haut: [
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kppppppk..', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khsssshk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kppppppk..', '..kpp..ppk..', '..kk....kk..'],
    ],
    cote: [
      ['...kkkkkk...', '...khhhhhk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kccccck..', '..lllllll...', '...kccccck..', '...kccccck..', '...kppppk...', '..gkppk.kk..', '..gkkk......'],
      ['...kkkkkk...', '...khhhhhk..', '...khsssok..', '...khssssk..', '...khsssk...', '....kssk....', '...kccccck..', '..lllllll...', '...kccccck..', '...kccccck..', '...kppppk...', '..gkppk.kk..', '..gkkk......'],
    ],
  },
};
// Le capuchon qui mange le visage et les mains DANS les poches : une
// silhouette qui ne montre rien, et c'est exactement ce qu'on lui demande.
SPRITES.pickpocket = {
  w: 12, h: 13, ancre: [6, 12],
  pal: { k: '#101018', s: '#d8a878', h: '#1a1a1a', c: '#3a4450', p: '#26262e', o: '#2a2f38', b: '#26262e' },
  swaps: ['c', 'h', 's', 'p'],
  poses: {
    bas: [
      ['...kkkkkk...', '..khhhhhhk..', '..khhsshhk..', '..khsossk...', '..khssssk...', '...kssssk...', '..kcccccck..', '..kcooocck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..khhhhhhk..', '..khhsshhk..', '..khsossk...', '..khssssk...', '...kssssk...', '..kcccccck..', '..kcooocck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    haut: [
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kpp..ppk..', '..kk....kk..'],
      ['...kkkkkk...', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '..khhhhhhk..', '...kssssk...', '..kcccccck..', '..kcccccck..', '..kcccccck..', '..kcccccck..', '...kppppk...', '..kppk.kpk..', '..kkk...kk..'],
    ],
    cote: [
      ['...kkkkkk...', '...khhhhhk..', '...khhssok..', '...khsssk...', '...khssk....', '....kssk....', '...kccccck..', '...kcoock...', '...kccccck..', '...kccccck..', '....kppppk..', '...kppk.kk..', '...kkk......'],
      ['...kkkkkk...', '...khhhhhk..', '...khhssok..', '...khsssk...', '...khssk....', '....kssk....', '...kccccck..', '...kcoock...', '...kccccck..', '...kccccck..', '....kppppk..', '....kpk.kk..', '....kk......'],
    ],
  },
};

// ⚠️ Les trois de la carrosserie commune sont declares APRES les fonctions de
// fiche (`enVolume`), plus bas : c'est la qu'ils prennent leur machine.
/** Une fiche EN VOLUME : sa machine, et TROIS poses qui en sont tirees.

    ⚠️ Les poses `cote`, `haut`, `bas` ne sont plus dessinees a la main : ce
    sont les projections de la machine a l'est, au nord et au sud. Deux
    dessins d'un meme char, c'est deux chars qui finissent par diverger.

    ⚠️ La grille est CARREE et le point de sol est en son centre — c'est ce qui
    fait tourner le dessin sur son empreinte, comme l'ombre. L'`ancre` en est
    tiree pour que `Vehicules.centreDuToit` tombe au meme endroit : une demi-
    longueur sous le centre, la ou serait la ligne de sol d'un char. */
function enVolume(machine, longueur, cote, pal) {
  const vue = function (angle) { return [Atlas.projeter(machine, angle, cote)]; };
  return {
    w: cote, h: cote, ancre: [cote / 2, cote / 2 - 1 + longueur / 2], machine: machine, pal: nuancer(pal), swaps: ['c'],
    poses: { cote: vue(0), haut: vue(-Math.PI / 2), bas: vue(Math.PI / 2) },
  };
}
/** Un deux-roues : une fiche en volume, et la selle ou le passant s'assoit. */
function deuxRoues(machine, longueur, cote, pal) {
  return Object.assign(enVolume(machine, longueur, cote, pal), {
    // LA SELLE, en [dx, dy] depuis la ligne de sol du dessin vu d'en haut : la
    // ou l'ANCRE du passant assis se pose. ⚠️ Elle est TIREE de l'`assise` de
    // la machine — deux nombres pour un meme siege finissent par diverger — et
    // c'est un point DE LA MACHINE : elle tourne avec elle
    // (`Vehicules.imageDuCavalier`).
    selle: [0, -machine.assise[0] - longueur / 2],
  });
}
/** Une coque : une fiche en volume, le siege de celui qui la mene, et la POSTURE
    de son corps (`barre` ou `volant`, des poses du passant). ⚠️ La selle se tire
    de l'`assise` comme celle d'un deux-roues — la meme formule, pour le meme point
    qui tourne avec la machine (`Vehicules.imageDuCavalier`). */
function assisDedans(machine, longueur, cote, posture, pal) {
  return Object.assign(deuxRoues(machine, longueur, cote, pal), { posture: posture });
}
// La berline : 28 px de long, sur une toile de 44 (sa diagonale, et le toit qui
// monte au-dessus). ⚠️ Les trois ont la MEME carrosserie ; le taxi et la police
// y ajoutent leur livree, `x` le damier et `y` la bande.
const PALETTE_AUTO = { k: '#101018', c: '#c0392b', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e' };
SPRITES.auto = enVolume(MACHINE_BERLINE, 28, 48, PALETTE_AUTO);
SPRITES.auto_compacte = enVolume(MACHINE_COMPACTE, 28, 48, PALETTE_AUTO);
SPRITES.auto_familiale = enVolume(MACHINE_FAMILIALE, 28, 48, PALETTE_AUTO);
SPRITES.auto_camionnette = enVolume(MACHINE_CAMIONNETTE, 28, 48, PALETTE_AUTO);
/* ⚠️ LES VARIANTES, et leur poids : une auto sur deux est une berline. Le choix
   se fait a la naissance (`Vehicules.creer`) SANS TIRER DE DE — c'est la lecon
   de la tete du pilote : un de de plus decale tout ce qui nait apres. Le taxi
   et la police n'en ont pas : ce sont des flottes. */
SPRITES.auto.variantes = { auto: 5, auto_compacte: 2, auto_familiale: 2, auto_camionnette: 1 };
SPRITES.taxi = enVolume(MACHINE_TAXI, 28, 48, { k: '#101018', c: '#f1c40f', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', x: '#101018', y: '#101018', e: '#fff4c4', q: '#d8c37a' });
SPRITES.police = enVolume(MACHINE_POLICE, 28, 48, { k: '#101018', c: '#ffffff', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', x: '#e0312a', y: '#2f6fd8', a: '#7a2320', b: '#233f7a' });
/* ⚠️ LES GYROPHARES : les lettres qui tournent, [allumee, eteinte], et QUAND
   elles tournent — `sirene` (la police, l'ambulance) ou `remorque` (la
   remorqueuse, quand elle tire quelque chose). Eteints, ils gardent la couleur
   de leur boitier : un gyrophare qui brille tout le temps ne dit plus rien.
   C'est `Vehicules.swapsDuMoment` qui les fait battre, `a` et `b` en
   alternance. */
SPRITES.police.gyrophares = { quand: 'sirene', a: ['#ff4a3d', '#7a2320'], b: ['#4a9bff', '#233f7a'] };
SPRITES.velo = deuxRoues(MACHINE_VELO, 16, 32, { k: '#101018', c: '#2980b9', r: '#2a2a2e', l: '#fff3b0', t: '#ff4b3e' });
// ⚠️ LES PEDALES : un demi-tour tous les `pedale` pixels roules. C'est la fiche
// qui dit qu'on pedale, pas un `slug === 'velo'` — la moto n'en a pas, et son
// pilote garde les pieds sur les repose-pieds.
SPRITES.velo.pedale = 7;
SPRITES.moto = deuxRoues(MACHINE_MOTO, 20, 36, { k: '#101018', c: '#1a1a1a', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e' });

/* --- LE PARC EN VOLUME : le reste des chars, comme la berline ---------------------

   ⚠️ **Le go de Martin : « tu vas pouvoir faire pareil pour les autres types de
   véhicule ».** Ils roulaient encore sur leur TOIT tourne, dessine a la main.
   Chacun est maintenant une machine projetee au cap, et chacun garde ce qui le
   nomme — c'etait la regle des dessins d'avant, et elle tient toujours :

   - la SPORT est basse et DECAPOTABLE : le seul char du parc dont l'habitacle
     est ouvert, on voit ses deux sieges ;
   - la LUXE est l'inverse exact : longue, un toit plein, des vitres fumees, et
     du chrome tout autour (jonc, calandre, figurine) ;
   - l'AMBULANCE a sa caisse haute, sa croix sur les flancs ET sur le toit, sa
     bande rouge, et une rampe devant et deux feux derriere ;
   - la REMORQUEUSE a son plateau, le bras couche dessus et le crochet qui
     depasse a l'arriere, et sa rampe ambre sur la cabine ;
   - le CAMION a une cabine avancee et une caisse haute a nervures ;
   - l'AUTOBUS est la plus longue boite, une rangee de fenetres, une porte, une
     girouette et des trappes sur le toit ;
   - la CHALOUPE a une coque pincee en proue, un fond, deux bancs et un moteur
     hors-bord — et pas de roues.

   Les aides ci-dessous portent la geometrie commune : les passages de roue, le
   plan pince, les essieux, les pare-chocs, les phares et les feux. ⚠️ Leurs
   noms sont PREFIXES : ce fichier est charge dans l'espace global, et un
   `lampes` ou un `pince` nu finirait par croiser quelqu'un. */
/** Le bas de caisse, de l'arriere vers l'avant, avec un passage au-dessus de
    chaque essieu (`essieux` : les u, rayon de roue `r`, bas de caisse `bas`). */
function passagesDeRoue(essieux, r, bas, queue, nez) {
  const k = r / 3, pts = [];
  essieux.slice().sort(function (a, b) { return a - b; }).forEach(function (a) {
    [[-3.4, 0], [-3.2, 1.8], [-2.0, 3.0], [0, 3.4], [2.0, 3.0], [3.2, 1.8], [3.4, 0]].forEach(function (d) {
      pts.push([a + d[0] * k, bas + d[1] * k]);
    });
  });
  return pts.filter(function (p) { return p[0] > queue && p[0] < nez; });
}
/** Une caisse : sa ligne de dessus du nez a la queue, ses passages de roue, son
    plan pince. Rend la piece `profil`. */
function caisseDeChar(o) {
  const nez = o.dessus[0][0], queue = o.dessus[o.dessus.length - 1][0], bas = o.bas;
  const pts = [[nez, bas]].concat(o.dessus, [[queue, bas]], passagesDeRoue(o.essieux, o.r, bas, queue, nez));
  let lettres = 'D';
  for (let k = 0; k < o.dessus.length - 1; k++) lettres += (o.aretes && o.aretes[k]) || 'c';
  lettres += 'D';
  while (lettres.length < pts.length) lettres += 'k';
  return ['profil', pts, o.plan, o.flanc || 'c', lettres, o.avance];
}
/** Un plan pince : demi-largeur `demi` au milieu, `bout` aux deux bouts. */
function planPince(lon, demi, bout) {
  const L = lon / 2;
  return [[-L - 0.5, bout], [-L + 1.3, demi * 0.96], [-L + 2.9, demi], [L - 2.9, demi], [L - 1.3, demi * 0.96], [L + 0.5, bout]];
}
function essieuDeChar(u, r, w, larges) {
  return [['roue', u, r, 'r', 'M', 'M', larges || 2, w], ['roue', u, r, 'r', 'M', 'M', larges || 2, -w]];
}
function lampesDeChar(uAv, uAr, w0, w1, z0, z1) {
  return [
    ['bloc', [uAv - 2.4, uAv + 0.6], [w0, w1], [z0, z1], 'l', 'l', 'l', 0.2],
    ['bloc', [uAv - 2.4, uAv + 0.6], [-w1, -w0], [z0, z1], 'l', 'l', 'l', 0.2],
    ['bloc', [uAr - 0.6, uAr + 2.4], [w0, w1], [z0 + 0.2, z1 + 0.2], 't', 't', 't', 0.2],
    ['bloc', [uAr - 0.6, uAr + 2.4], [-w1, -w0], [z0 + 0.2, z1 + 0.2], 't', 't', 't', 0.2],
  ];
}
function parechocsDeChar(uAv, uAr, demi) {
  return [
    ['bloc', [uAv - 0.2, uAv + 0.5], [-demi, demi], [1.6, 2.8], 'B', 'B', 'B', 0.1],
    ['bloc', [uAr - 0.5, uAr + 0.2], [-demi, demi], [1.6, 2.8], 'B', 'B', 'B', 0.1],
  ];
}

// --- La sport : basse, DECAPOTABLE — on voit ses deux sieges ------------------
const MACHINE_SPORT = {
  profondeur: BIAIS_DU_SOL, contour: true, arrondi: true,
  pieces: [].concat(
    essieuDeChar(8.0, 3.0, 5.6), essieuDeChar(-8.4, 3.0, 5.6),
    // ⚠️ Le dessus de l'habitacle est OUVERT ('.') : ses flancs font les
    // portieres, et on voit dedans.
    [caisseDeChar({ dessus: [[13, 3.2], [11.6, 4.3], [4.4, 5.0], [-7.6, 5.1], [-10.8, 5.2], [-12.4, 5.1], [-13, 4.2]], bas: 1.4,
                    essieux: [8.0, -8.4], r: 3.0, plan: planPince(26, 6.5, 4.8), aretes: 'cc.ccc' })],
    [
      ['bloc', [-7.6, 4.4], [-6.0, 6.0], [3.0, 3.2], 'i', 'i', 'i', 0],                     // le plancher
      ['bloc', [-5.2, -2.6], [-5.2, -0.8], [3.2, 4.6], 'u', 'u', 'u', 0.05],                 // les deux sieges
      ['bloc', [-5.2, -2.6], [0.8, 5.2], [3.2, 4.6], 'u', 'u', 'u', 0.05],
      ['bloc', [-6.4, -5.2], [-5.2, -0.8], [3.2, 7.0], 'u', 'u', 'u', 0.05],                 // et leurs dossiers
      ['bloc', [-6.4, -5.2], [0.8, 5.2], [3.2, 7.0], 'u', 'u', 'u', 0.05],
      ['profil', [[4.6, 5.0], [2.6, 8.0], [2.0, 8.0], [4.0, 5.0]], [-5.4, 5.4], 'D', 'v.v.', 0.1],   // le pare-brise
      ['tube', [2.3, -5.4, 8.1], [2.3, 5.4, 8.1], 'D', 0.6],                               // son cadre
      ['tube', [4.45, -5.4, 5.25], [4.45, 5.4, 5.25], 'D', 1.0],
      ['tube', [3.9, -4.6, 6.0], [3.9, 4.6, 6.0], 'G', 0.3],                                // son reflet
      ['tube', [10.4, 6.52, 4.6], [-10.4, 6.52, 5.0], 'C', 0.05], ['tube', [10.4, -6.52, 4.6], [-10.4, -6.52, 5.0], 'C', 0.05],
      ['bloc', [-13.2, -11.2], [-5.4, 5.4], [5.9, 6.5], 'D', 'D', 'D', 0.2],                 // l'aileron
      ['tube', [-12.2, 4.2, 5.1], [-12.2, 4.2, 5.9], 'D', 0.1], ['tube', [-12.2, -4.2, 5.1], [-12.2, -4.2, 5.9], 'D', 0.1],
    ],
    parechocsDeChar(13, -13, 4.6), lampesDeChar(12.8, -12.8, 2.4, 6.0, 2.7, 4.1),
  ),
};
// --- La luxe : longue, un long capot, du chrome ---------------------------------
const MACHINE_LUXE = {
  profondeur: BIAIS_DU_SOL, contour: true, arrondi: true,
  pieces: [].concat(
    essieuDeChar(10.4, 3.3, 6.6), essieuDeChar(-10.2, 3.3, 6.6),
    [caisseDeChar({ dessus: [[16, 4.8], [15.0, 6.4], [-14.6, 6.6], [-16, 5.4]], bas: 1.6, essieux: [10.4, -10.2], r: 3.3,
              plan: planPince(32, 7.5, 6.0) })],
    habitacle({ avant: 3.2, toit: [-0.6, -8.6], arriere: -11.6, montant: -4.2, bas: 6.5, haut: 12.0, demi: 6.3 }),
    [
      ['tube', [14.6, 7.52, 6.4], [-14.2, 7.52, 6.6], 'B', 0.05], ['tube', [14.6, -7.52, 6.4], [-14.2, -7.52, 6.6], 'B', 0.05],  // le jonc chrome
      ['tube', [13.2, 7.54, 3.6], [-13.2, 7.54, 3.6], 'B', 0.05], ['tube', [13.2, -7.54, 3.6], [-13.2, -7.54, 3.6], 'B', 0.05],
      ['bloc', [15.8, 16.4], [-3.6, 3.6], [2.8, 5.2], 'B', 'M', 'B', 0.2],                 // la calandre
      ['bloc', [15.0, 15.6], [-0.3, 0.3], [6.4, 7.2], 'B', 'B', 'B', 0.3],                 // la figurine
      ['tube', [-1.1, 7.53, 1.8], [-1.1, 7.53, 6.2], 'D', 0.03], ['tube', [-1.1, -7.53, 1.8], [-1.1, -7.53, 6.2], 'D', 0.03],
      ['tube', [-7.4, 7.53, 1.8], [-7.4, 7.53, 6.2], 'D', 0.03], ['tube', [-7.4, -7.53, 1.8], [-7.4, -7.53, 6.2], 'D', 0.03],
    ],
    parechocsDeChar(16, -16, 6.0), lampesDeChar(15.8, -15.8, 3.4, 7.1, 3.2, 4.8),
  ),
};
// --- L'ambulance : une cabine, une caisse haute, la croix ------------------------
const CROIX_ROUGE = function (u, z, w) {
  return [['tube', [u, w, z - 2.6], [u, w, z + 2.6], 'x', 0.4], ['tube', [u - 2.6, w, z], [u + 2.6, w, z], 'x', 0.4],
          ['tube', [u + 0.5, w, z - 2.6], [u + 0.5, w, z + 2.6], 'x', 0.4], ['tube', [u - 2.6, w, z + 0.5], [u + 2.6, w, z + 0.5], 'x', 0.4]];
};
const MACHINE_AMBULANCE = {
  profondeur: BIAIS_DU_SOL, contour: true, arrondi: true,
  pieces: [].concat(
    essieuDeChar(9.8, 3.2, 6.4), essieuDeChar(-9.6, 3.2, 6.4),
    [caisseDeChar({ dessus: [[16, 5.4], [15.0, 7.0], [11.4, 7.3], [5.4, 7.3], [5.2, 15.8], [-15.4, 16.0], [-16, 15.2], [-16, 7.0]], bas: 1.6,
              essieux: [9.8, -9.6], r: 3.2, plan: planPince(32, 7.5, 6.2), aretes: 'cccDCCD' })],
    habitacle({ avant: 11.4, toit: [8.6, 5.4], arriere: 5.4, montant: null, bas: 7.3, haut: 13.0, demi: 6.4 }),
    CROIX_ROUGE(-5.4, 11.2, 7.54), CROIX_ROUGE(-5.4, 11.2, -7.54),
    [
      ['tube', [4.8, 7.53, 5.6], [-15.6, 7.53, 5.6], 'x', 0.4], ['tube', [4.8, -7.53, 5.6], [-15.6, -7.53, 5.6], 'x', 0.4],  // la bande
      ['tube', [-5.4, -3.0, 16.05], [-5.4, 3.0, 16.05], 'x', 0.1], ['tube', [-8.4, 0, 16.05], [-2.4, 0, 16.05], 'x', 0.1],       // la croix du toit
      ['tube', [-5.8, -3.0, 16.05], [-5.8, 3.0, 16.05], 'x', 0.1], ['tube', [-8.4, 0.5, 16.05], [-2.4, 0.5, 16.05], 'x', 0.1],
      ['bloc', [5.6, 7.4], [-5.2, -0.3], [13.0, 13.9], 'a', 'a', 'a', 0.2],                  // la rampe
      ['bloc', [5.6, 7.4], [0.3, 5.2], [13.0, 13.9], 'b', 'b', 'b', 0.2],
      ['bloc', [-15.8, -14.4], [-7.0, -4.6], [16.0, 16.8], 'a', 'a', 'a', 0.2],              // et deux feux au cul de la caisse
      ['bloc', [-15.8, -14.4], [4.6, 7.0], [16.0, 16.8], 'b', 'b', 'b', 0.2],
      ['tube', [-16.05, 0, 2.2], [-16.05, 0, 14.8], 'D', 0.05],                             // les portes arriere
    ],
    parechocsDeChar(16, -16, 6.2), lampesDeChar(15.8, -15.8, 3.4, 7.2, 3.4, 5.0),
  ),
};
// --- La remorqueuse : une cabine, un plateau, le bras et son crochet --------------
const MACHINE_REMORQUEUSE = {
  profondeur: BIAIS_DU_SOL, contour: true, arrondi: true,
  pieces: [].concat(
    essieuDeChar(10.6, 3.3, 6.4), essieuDeChar(-10.4, 3.3, 6.4),
    [caisseDeChar({ dessus: [[18, 5.4], [17.0, 7.2], [12.8, 7.6], [5.6, 7.6], [5.4, 6.8], [-18, 6.8]], bas: 1.8, essieux: [10.6, -10.4], r: 3.3,
              plan: planPince(36, 7.5, 6.2), aretes: 'cccDs' })],
    [['profil', [[12.8, 7.6], [12.6, 9.2], [5.6, 9.2], [5.6, 7.6]], [-6.9, 6.9], 'c', 'cc.c']],   // le bas de la cabine
    habitacle({ avant: 12.6, toit: [10.2, 5.6], arriere: 5.6, montant: null, bas: 9.2, haut: 13.6, demi: 6.4 }),
    [
      ['bloc', [-18, 5.0], [-7.2, 7.2], [6.8, 7.3], 'p', 's', 's', 0.05],                   // le plateau
      ['bloc', [-15.6, 3.6], [-1.0, 1.0], [7.3, 8.8], 'h', 'h', 'h', 0.1],                   // le bras, couche
      ['tube', [-15.4, 0, 8.4], [-19.6, 0, 6.2], 'h', 0.2], ['tube', [-15.4, 0.6, 8.4], [-19.6, 0.6, 6.2], 'h', 0.2],
      ['tube', [-19.6, 0, 6.2], [-19.6, 0, 4.0], 'k', 0.2], ['tube', [-19.6, 0, 4.0], [-18.8, 0, 4.0], 'k', 0.2],   // le crochet
      ['bloc', [6.0, 8.0], [-5.2, -0.3], [13.6, 14.5], 'a', 'a', 'a', 0.2],                  // la rampe ambre
      ['bloc', [6.0, 8.0], [0.3, 5.2], [13.6, 14.5], 'b', 'b', 'b', 0.2],
      ['bloc', [6.0, 8.0], [-5.4, 5.4], [13.55, 13.65], 'k', 'k', 'k', 0.1],
    ],
    parechocsDeChar(18, -18, 6.2), lampesDeChar(17.8, -17.8, 3.2, 7.6, 3.4, 5.4),
  ),
};
// --- Le camion : une cabine avancee, une caisse haute a nervures -----------------
const NERVURES_CAMION = [];
[-18, -13.5, -9, -4.5, 0, 4.5].forEach(function (u) {
  NERVURES_CAMION.push(['tube', [u, 8.05, 6.2], [u, 8.05, 17.8], 's', 0.05], ['tube', [u, -8.05, 6.2], [u, -8.05, 17.8], 's', 0.05],
                ['tube', [u, -8.0, 18.25], [u, 8.0, 18.25], 's', 0.05]);
});
const MACHINE_CAMION = {
  profondeur: BIAIS_DU_SOL, contour: true, arrondi: true,
  pieces: [].concat(
    essieuDeChar(13.2, 3.4, 6.8), essieuDeChar(-12.2, 3.4, 6.8),
    [caisseDeChar({ dessus: [[20, 5.6], [19.2, 8.4], [15.8, 8.8], [10.4, 8.8], [10.2, 5.6], [-20, 5.6]], bas: 1.8, essieux: [13.2, -12.2], r: 3.4,
              plan: planPince(40, 8.0, 6.8), aretes: 'cccDs' })],
    habitacle({ avant: 15.8, toit: [13.4, 10.4], arriere: 10.4, montant: null, bas: 8.8, haut: 15.0, demi: 7.0 }),
    // ⚠️ La caisse a SES tons (`b`, `n` son dessus, `s` ses bouts) : avec `C` et `D`, ceux de la cabine,
    // son toit prenait le rehaut d'une cabine rouge — rose.
    [['profil', [[9.8, 5.6], [9.8, 18.2], [-20.2, 18.2], [-20.2, 5.6]], [-8.0, 8.0], 'b', 'sns.', 0.02]],   // la caisse
    NERVURES_CAMION,
    [['tube', [-20.25, 0, 6.2], [-20.25, 0, 17.6], 's', 0.05]],
    parechocsDeChar(20, -20, 6.8), lampesDeChar(19.8, -19.8, 3.6, 8.3, 3.6, 5.2),
  ),
};
// --- L'autobus : une longue boite, une rangee de fenetres, une porte ---------------
const FENETRES_AUTOBUS = [];
[-19.5, -14, -8.5, -3, 2.5, 8].forEach(function (u) {
  [-1, 1].forEach(function (s) {
    const w = s * 8.02;
    FENETRES_AUTOBUS.push(['bloc', [u, u + 4.2], [w - 0.01, w + 0.01], [10.6, 15.0], 'v', 'v', 'v', 0.04]);
    // ⚠️ Le cadre passe DEVANT la vitre : a la meme rangee, un pixel de vitre plus
    // haut gagnait, et les fenetres de profil faisaient une seule bande.
    FENETRES_AUTOBUS.push(['tube', [u - 0.4, s * 8.04, 10.3], [u + 4.6, s * 8.04, 10.3], 'D', 0.5], ['tube', [u - 0.4, s * 8.04, 15.3], [u + 4.6, s * 8.04, 15.3], 'D', 0.5]);
    FENETRES_AUTOBUS.push(['tube', [u + 4.8, s * 8.04, 10.3], [u + 4.8, s * 8.04, 15.3], 'D', 0.5]);
  });
});
const MACHINE_AUTOBUS = {
  profondeur: BIAIS_DU_SOL, contour: true, arrondi: true,
  pieces: [].concat(
    essieuDeChar(15.0, 3.4, 6.8), essieuDeChar(-14.0, 3.4, 6.8),
    [caisseDeChar({ dessus: [[24, 17.0], [23.0, 18.2], [-23.0, 18.2], [-24, 17.0]], bas: 1.8, essieux: [15.0, -14.0], r: 3.4,
              plan: planPince(48, 8.0, 7.2), aretes: 'cCc' })],
    FENETRES_AUTOBUS,
    [
      ['bloc', [24.0, 24.08], [-6.6, 6.6], [9.4, 16.0], 'v', 'v', 'v', 0.05],               // le pare-brise
      ['tube', [24.1, -6.8, 9.2], [24.1, 6.8, 9.2], 'D', 0.5], ['tube', [24.1, -6.8, 16.2], [24.1, 6.8, 16.2], 'D', 0.5],
      ['tube', [24.12, -5.8, 12.0], [24.12, 5.8, 12.0], 'G', 0.3],
      ['bloc', [-24.08, -24.0], [-5.0, 5.0], [11.0, 15.4], 'v', 'v', 'v', 0.05],            // la lunette
      ['tube', [-24.1, -5.2, 10.8], [-24.1, 5.2, 10.8], 'D', 0.5], ['tube', [-24.1, -5.2, 15.6], [-24.1, 5.2, 15.6], 'D', 0.5],
      ['bloc', [18.2, 21.8], [8.02, 8.06], [2.4, 15.6], 'E', 'E', 'E', 0.05],               // la porte
      ['tube', [20.0, 8.08, 2.4], [20.0, 8.08, 15.6], 'D', 0.06],
      ['bloc', [-18, -12], [-4.2, 4.2], [18.2, 18.8], 'C', 'D', 'D', 0.1],                   // la trappe de toit
      ['bloc', [4, 10], [-4.2, 4.2], [18.2, 18.8], 'C', 'D', 'D', 0.1],
      ['bloc', [24.02, 24.1], [-4.4, 4.4], [16.4, 17.6], 'e', 'e', 'e', 0.1],               // la girouette
    ],
    parechocsDeChar(24, -24, 7.2), lampesDeChar(23.8, -23.8, 4.2, 7.9, 3.6, 5.2),
  ),
};
// --- La chaloupe : une coque pincee en proue, un banc, un moteur hors-bord ---------
// ⚠️ **Quelqu'un la mene** (retour de Martin : « on devrait pouvoir voir le
// personnage ou un voleur assis dans la chaloupe »). On y montait et elle partait
// VIDE : seuls le velo et la moto declaraient une selle. Comme eux, la coque
// declare ou le corps se tient — ses fesses sur le banc de poupe (`assise`), sa
// main au bout de la barre franche (`barre`) — et les juges mesurent le corps
// dessine contre les deux.
// La barre franche : du haut du moteur vers le banc de poupe, jusqu'a la main.
const BARRE_FRANCHE = ['tube', [-15.4, 0, 7.4], [-11.8, 0, 6.6], 'M', 0.4];
const MACHINE_BATEAU = {
  profondeur: BIAIS_DU_SOL, contour: true, arrondi: true,
  assise: [-8.2, 0, 3.9],
  barre: [-11.8, 0, 6.6],
  pieces: [
    ['profil', [[15, 5.2], [12.4, 2.4], [8.6, 0.6], [-14.4, 0.6], [-15, 1.2], [-15, 5.2]],
     [[-15.5, 5.0], [-2, 6.0], [6, 5.6], [11, 3.6], [15.5, 0.3]], 'c', 'DDDDD.', 0],
    ['bloc', [-14.4, 11.0], [-4.6, 4.6], [1.4, 1.6], 'r', 'r', 'r', 0],                     // le fond
    ['bloc', [9.0, 14.6], [-2.8, 2.8], [4.8, 5.3], 'C', 'c', 'c', 0.1],                     // le pont de proue
    ['bloc', [-1.2, 0.8], [-5.4, 5.4], [3.4, 3.9], 'u', 'u', 'u', 0.1],                     // les bancs
    ['bloc', [-9.2, -7.2], [-5.2, 5.2], [3.4, 3.9], 'u', 'u', 'u', 0.1],
    ['bloc', [-17.4, -15.2], [-1.2, 1.2], [4.0, 8.0], 'k', 'k', 'k', 0.2],                  // le moteur
    ['tube', [-16.2, 0, 4.0], [-16.2, 0, 0.2], 'M', 0.2],
    BARRE_FRANCHE,
    ['bloc', [12.6, 15.4], [-0.9, 0.9], [5.0, 7.0], 'l', 'l', 'l', 0.3],                     // les feux de navigation
    ['bloc', [-15.8, -14.0], [-1.0, 1.0], [5.2, 7.2], 't', 't', 't', 0.3],
  ],
};

// Les fiches. La toile de chacun couvre sa diagonale ET ce qui monte (juge : aucun
// pixel sur le bord de la toile, a aucun cap).
SPRITES.sport = enVolume(MACHINE_SPORT, 26, 44, { k: '#101018', c: '#c0392b', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', i: '#2a2028', u: '#6b4b2c', s: '#8e2b20' });
SPRITES.luxe = enVolume(MACHINE_LUXE, 32, 52, { k: '#101018', c: '#101014', v: '#5f7f99', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', m: '#b9bcc4', s: '#26262e' });
SPRITES.ambulance = enVolume(MACHINE_AMBULANCE, 32, 64, { k: '#101018', c: '#ffffff', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', x: '#e0312a', y: '#2f6fd8', s: '#f39c12', a: '#7a2320', b: '#8e9299' });
// Rouge et blanc, devant sur la cabine et derriere sur la caisse : ils tournent avec sa sirene.
SPRITES.ambulance.gyrophares = { quand: 'sirene', a: ['#ff4a3d', '#7a2320'], b: ['#ffffff', '#8e9299'] };
SPRITES.remorqueuse = enVolume(MACHINE_REMORQUEUSE, 36, 60, { k: '#101018', c: '#d98324', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', h: '#6b7078', p: '#c9cdd4', y: '#f39c12', s: '#3a3d44', a: '#6a4812', b: '#6a4812' });
// Ambre, sur la cabine : ils tournent quand elle remorque. ⚠️ Sur une BASE SOMBRE,
// et d'un ambre plus jaune que la caisse : ambre sur orange, la rampe disparaissait.
SPRITES.remorqueuse.gyrophares = { quand: 'remorque', a: ['#ffd84a', '#6a4812'], b: ['#ffd84a', '#6a4812'] };
SPRITES.camion = enVolume(MACHINE_CAMION, 40, 76, { k: '#101018', c: '#7f8c8d', b: '#8d99a6', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', s: '#565c63', n: '#aab4be' });
SPRITES.autobus = enVolume(MACHINE_AUTOBUS, 48, 80, { k: '#101018', c: '#2980b9', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', s: '#1f5f8b', e: '#ffd84a' });
SPRITES.bateau = assisDedans(MACHINE_BATEAU, 30, 48, 'barre', { k: '#101018', c: '#ecf0f1', v: '#7fb3d8', r: '#3a2f26', l: '#fff3b0', t: '#ff4b3e', x: '#ecf0f1', y: '#ecf0f1', s: '#00000030', u: '#8a6a44' });

/* --- Les variantes du parc : la meme empreinte, une autre silhouette ------------------

   ⚠️ **Retour de Martin : « aussi des variantes ».** L'auto avait ses quatre
   silhouettes ; le reste du parc etait une seule machine repeinte. Les types qui
   ne sont pas des flottes en recoivent : le CAMION (une benne, une citerne),
   l'AUTOBUS (le scolaire jaune, capot devant), la LUXE (un VUS) et la CHALOUPE
   (un bateau a console). Le taxi, la police, l'ambulance et la remorqueuse sont
   des flottes, et une flotte se reconnait d'un coup d'oeil parce qu'elle ne
   varie pas.

   ⚠️ Rien ne change a l'empreinte : c'est toujours le meme vehicule du
   catalogue, il se conduit pareil et il bloque pareil. */

// La cabine du camion, commune a ses trois silhouettes.
const CABINE_CAMION = [].concat(
  essieuDeChar(13.2, 3.4, 6.8), essieuDeChar(-12.2, 3.4, 6.8),
  [caisseDeChar({ dessus: [[20, 5.6], [19.2, 8.4], [15.8, 8.8], [10.4, 8.8], [10.2, 5.6], [-20, 5.6]], bas: 1.8, essieux: [13.2, -12.2], r: 3.4,
                  plan: planPince(40, 8.0, 6.8), aretes: 'cccDs' })],
  habitacle({ avant: 15.8, toit: [13.4, 10.4], arriere: 10.4, montant: null, bas: 8.8, haut: 15.0, demi: 7.0 }),
  parechocsDeChar(20, -20, 6.8), lampesDeChar(19.8, -19.8, 3.6, 8.3, 3.6, 5.2),
);
// Le camion-benne : des ridelles hautes, un pare-cabine, et le fond qu'on voit d'en haut.
const MACHINE_CAMION_BENNE = Object.assign({}, MACHINE_CAMION, {
  pieces: CABINE_CAMION.concat([
    ['bloc', [-20.2, 8.4], [7.2, 8.0], [5.6, 12.6], 'C', 'c', 'D', 0.02],                   // les ridelles
    ['bloc', [-20.2, 8.4], [-8.0, -7.2], [5.6, 12.6], 'C', 'c', 'D', 0.02],
    ['bloc', [8.4, 9.8], [-8.0, 8.0], [5.6, 16.0], 'C', 'D', 'D', 0.02],                    // le pare-cabine
    ['bloc', [-20.6, -19.6], [-7.2, 7.2], [5.6, 12.6], 'C', 'D', 'D', 0.02],                // le hayon
    ['bloc', [-19.6, 8.4], [-7.2, 7.2], [5.7, 6.0], 's', 's', 's', 0],                      // le fond de la benne
  ], [-15, -9, -3, 3].reduce(function (t, u) {
    return t.concat([['tube', [u, 8.05, 6.0], [u, 8.05, 12.4], 'D', 1.0], ['tube', [u, -8.05, 6.0], [u, -8.05, 12.4], 'D', 1.0]]);
  }, [])),
});
// Le camion-citerne : une citerne ronde en acier, ceinturee, et son trou d'homme.
const MACHINE_CAMION_CITERNE = Object.assign({}, MACHINE_CAMION, {
  pieces: CABINE_CAMION.concat([
    ['bloc', [-19.8, 8.8], [-6.0, 6.0], [5.6, 7.0], 'M', 'M', 'M', 0.02],
    ['bloc', [-19.8, 8.8], [-7.6, 7.6], [7.0, 14.6], 'B', 'M', 'M', 0.02],
    ['bloc', [-19.8, 8.8], [-6.4, 6.4], [14.6, 16.2], 'B', 'M', 'M', 0.02],
    ['bloc', [-19.8, 8.8], [-4.0, 4.0], [16.2, 17.0], 'B', 'B', 'M', 0.02],
    ['bloc', [-7.0, -3.6], [-1.8, 1.8], [17.0, 17.8], 'M', 's', 's', 0.1],                  // le trou d'homme
  ], [-14.6, -5.2, 4.2].reduce(function (t, u) {
    return t.concat([['bloc', [u, u + 0.9], [-7.8, 7.8], [6.8, 14.8], 's', 's', 's', 0.3],
                     ['bloc', [u, u + 0.9], [-6.6, 6.6], [14.8, 16.4], 's', 's', 's', 0.3],
                     ['bloc', [u, u + 0.9], [-4.2, 4.2], [16.4, 17.2], 's', 's', 's', 0.3]]);
  }, [])),
});

// L'autobus scolaire : un capot devant, une caisse jaune a deux bandes noires.
const FENETRES_SCOLAIRE = [];
[-20.5, -15, -9.5, -4, 1.5, 7].forEach(function (u) {
  [-1, 1].forEach(function (s) {
    const w = s * 8.02;
    FENETRES_SCOLAIRE.push(['bloc', [u, u + 4.2], [w - 0.01, w + 0.01], [11.0, 15.4], 'v', 'v', 'v', 0.04]);
    FENETRES_SCOLAIRE.push(['tube', [u - 0.4, s * 8.04, 10.7], [u + 4.6, s * 8.04, 10.7], 'D', 1.0],
                           ['tube', [u - 0.4, s * 8.04, 15.7], [u + 4.6, s * 8.04, 15.7], 'D', 1.0],
                           ['tube', [u + 4.8, s * 8.04, 10.7], [u + 4.8, s * 8.04, 15.7], 'D', 1.0]);
  });
});
const MACHINE_AUTOBUS_SCOLAIRE = Object.assign({}, MACHINE_AUTOBUS, {
  pieces: [].concat(
    essieuDeChar(17.0, 3.4, 6.8), essieuDeChar(-14.0, 3.4, 6.8),
    [caisseDeChar({ dessus: [[24, 5.6], [23.2, 8.8], [16.8, 9.6], [16.4, 16.8], [15.4, 17.8], [-23.0, 17.8], [-24, 16.8]], bas: 1.8,
                    essieux: [17.0, -14.0], r: 3.4, plan: planPince(48, 8.0, 6.4), aretes: 'ccDCCc' })],
    FENETRES_SCOLAIRE,
    [
      ['bloc', [16.2, 16.5], [-6.6, 6.6], [10.4, 16.0], 'v', 'v', 'v', 0.05],               // le pare-brise, au-dessus du capot
      ['tube', [16.6, -6.8, 10.2], [16.6, 6.8, 10.2], 'D', 1.0], ['tube', [16.6, -6.8, 16.2], [16.6, 6.8, 16.2], 'D', 1.0],
      ['tube', [16.62, -5.8, 12.4], [16.62, 5.8, 12.4], 'G', 0.3],
      ['bloc', [23.8, 24.4], [-4.0, 4.0], [3.0, 7.6], 'B', 'M', 'B', 0.2],                  // la calandre
      ['tube', [15.8, 8.06, 7.2], [-23.4, 8.06, 7.2], 'k', 1.0], ['tube', [15.8, -8.06, 7.2], [-23.4, -8.06, 7.2], 'k', 1.0],   // les bandes noires
      ['tube', [15.8, 8.06, 9.6], [-23.4, 8.06, 9.6], 'k', 1.0], ['tube', [15.8, -8.06, 9.6], [-23.4, -8.06, 9.6], 'k', 1.0],
      ['bloc', [-24.08, -24.0], [-4.0, 4.0], [10.8, 15.4], 'v', 'v', 'v', 0.05],            // la porte de secours
      ['tube', [-24.1, -4.2, 10.6], [-24.1, 4.2, 10.6], 'D', 1.0], ['tube', [-24.1, -4.2, 15.6], [-24.1, 4.2, 15.6], 'D', 1.0],
      ['bloc', [12.4, 15.6], [8.02, 8.06], [2.4, 15.8], 'E', 'E', 'E', 0.05],               // la porte
      ['bloc', [15.4, 16.6], [-7.4, -4.4], [16.6, 17.6], 'l', 'l', 'l', 0.2],                // les feux d'arret, en haut
      ['bloc', [15.4, 16.6], [4.4, 7.4], [16.6, 17.6], 'l', 'l', 'l', 0.2],
    ],
    parechocsDeChar(24, -24, 7.2), lampesDeChar(23.8, -23.8, 3.2, 7.2, 3.6, 5.2),
  ),
});

// Le VUS de luxe : haut, long toit jusqu'au hayon, barres de toit, chrome.
const MACHINE_LUXE_VUS = Object.assign({}, MACHINE_LUXE, {
  pieces: [].concat(
    essieuDeChar(10.4, 3.5, 6.6), essieuDeChar(-10.2, 3.5, 6.6),
    [caisseDeChar({ dessus: [[16, 5.6], [15.2, 7.8], [-15.0, 8.0], [-16, 7.0]], bas: 2.2, essieux: [10.4, -10.2], r: 3.5,
                    plan: planPince(32, 7.5, 6.2) })],
    habitacle({ avant: 6.0, toit: [3.0, -13.0], arriere: -15.0, montant: -2.8, custode: -8.8, bas: 7.8, haut: 13.8, demi: 6.6 }),
    [
      ['tube', [14.6, 7.52, 7.6], [-14.2, 7.52, 7.8], 'B', 1.0], ['tube', [14.6, -7.52, 7.6], [-14.2, -7.52, 7.8], 'B', 1.0],   // le jonc
      ['tube', [2.0, 5.2, 14.2], [-12.0, 5.2, 14.2], 'B', 0.2], ['tube', [2.0, -5.2, 14.2], [-12.0, -5.2, 14.2], 'B', 0.2],     // les barres de toit
      ['bloc', [15.8, 16.4], [-4.4, 4.4], [3.4, 6.8], 'B', 'M', 'B', 0.2],                  // la calandre
    ],
    parechocsDeChar(16, -16, 6.2), lampesDeChar(15.8, -15.8, 3.4, 7.1, 4.2, 5.8),
  ),
});

// Le bateau a console : la meme coque, une console et son pare-brise, un siege derriere.
// ⚠️ Ni bancs ni barre franche : on le mene assis sur son siege (`assise`), les
// mains au volant de la console (`barre`).
const MACHINE_BATEAU_CONSOLE = Object.assign({}, MACHINE_BATEAU, {
  assise: [-6.1, 0, 4.4],
  barre: [-3.8, 0, 6.4],
  pieces: MACHINE_BATEAU.pieces.filter(function (p) { return !(p[0] === 'bloc' && p[5] === 'u') && p !== BARRE_FRANCHE; }).concat([
    ['bloc', [-3.4, 0.8], [-2.4, 2.4], [1.6, 5.6], 'D', 'c', 'D', 0.1],                      // la console, son tableau de bord sombre
    ['bloc', [-3.9, -3.4], [-1.2, 1.2], [5.6, 6.8], 'k', 'k', 'k', 0.3],                     // son volant
    ['profil', [[0.8, 5.6], [-0.6, 7.6], [-1.0, 7.6], [0.4, 5.6]], [-2.4, 2.4], 'D', 'v.v.', 0.2], // son pare-brise
    ['tube', [0.6, -2.4, 5.8], [0.6, 2.4, 5.8], 'D', 1.0], ['tube', [-0.8, -2.4, 7.7], [-0.8, 2.4, 7.7], 'D', 1.0],
    ['bloc', [-7.2, -5.0], [-2.6, 2.6], [1.6, 4.4], 'u', 'u', 'u', 0.1],                     // le siege
    ['bloc', [-7.6, -7.0], [-2.6, 2.6], [4.4, 6.4], 'u', 'u', 'u', 0.1],
  ]),
});

// Les fiches des variantes, et leur poids : la silhouette d'origine reste la plus courante.
SPRITES.camion_benne = enVolume(MACHINE_CAMION_BENNE, 40, 76, SPRITES.camion.pal);
SPRITES.camion_citerne = enVolume(MACHINE_CAMION_CITERNE, 40, 76, SPRITES.camion.pal);
SPRITES.camion.variantes = { camion: 3, camion_benne: 2, camion_citerne: 1 };
// ⚠️ LA CHARRUE (M12) n'est PAS tiree au sort : c'est la tempete qui la sort
// (`Autobus.faireNaitreLaCharrue`). Le camion, une lame en biais devant et un
// gyrophare ambre sur la cabine.
const MACHINE_CAMION_CHARRUE = Object.assign({}, MACHINE_CAMION, {
  pieces: MACHINE_CAMION.pieces.concat([
    // ⚠️ Relevee de deux pixels, comme en transit : posee au sol, elle soudait la roue
    // avant a la route et la machine ne montrait plus qu'une roue de profil.
    ['profil', [[23.6, 3.6], [24.4, 5.0], [24.0, 8.4], [21.8, 8.4], [21.4, 3.6]], [-10.4, 10.4], 'y', 'kkkkk', 0.1],   // la lame
    ['tube', [20.2, -4.0, 4.6], [22.0, -6.0, 4.6], 'k', 0.3], ['tube', [20.2, 4.0, 4.6], [22.0, 6.0, 4.6], 'k', 0.3],  // ses bras
    ['bloc', [11.6, 13.2], [-1.2, 1.2], [15.0, 16.4], 'y', 'y', 'y', 0.2],                                          // le gyrophare
  ]),
});
SPRITES.camion_charrue = enVolume(MACHINE_CAMION_CHARRUE, 40, 76, Object.assign({}, SPRITES.camion.pal, { y: '#f39c12' }));
SPRITES.camion_charrue.couleur = '#e67e22';
SPRITES.camion_charrue.de = 'camion';
// ⚠️ L'autobus scolaire est JAUNE, quelle que soit la couleur tiree pour l'autobus :
// une silhouette peut porter sa couleur (`Vehicules.creer` la lui rend).
SPRITES.autobus_scolaire = enVolume(MACHINE_AUTOBUS_SCOLAIRE, 48, 80, Object.assign({}, SPRITES.autobus.pal, { c: '#f5b400' }));
SPRITES.autobus_scolaire.couleur = '#f5b400';
SPRITES.autobus.variantes = { autobus: 3, autobus_scolaire: 2 };
// ⚠️ LE TRAMWAY (M12) n'est PAS une variante tiree au sort : c'est la silhouette que
// sa ligne donne (`Autobus.faireNaitre`). La caisse de l'autobus, la jupe jusqu'aux
// bogies (aucune roue ne se voit), un pare-brise A CHAQUE BOUT — il ne fait jamais
// demi-tour —, la bande de livree, deux portes et le pantographe sur le toit.
const MACHINE_TRAMWAY = Object.assign({}, MACHINE_AUTOBUS, {
  pieces: [].concat(
    [caisseDeChar({ dessus: [[24, 15.6], [23.2, 18.2], [-23.2, 18.2], [-24, 15.6]], bas: 0.9, essieux: [], r: 3.4,
                    plan: planPince(48, 8.0, 7.4), aretes: 'cCc' })],
    FENETRES_AUTOBUS,
    [
      ['bloc', [24.0, 24.08], [-6.6, 6.6], [8.6, 15.4], 'v', 'v', 'v', 0.05],                // le pare-brise, devant
      ['tube', [24.1, -6.8, 8.4], [24.1, 6.8, 8.4], 'D', 0.5], ['tube', [24.1, -6.8, 15.6], [24.1, 6.8, 15.6], 'D', 0.5],
      ['bloc', [-24.08, -24.0], [-6.6, 6.6], [8.6, 15.4], 'v', 'v', 'v', 0.05],              // et derriere
      ['tube', [-24.1, -6.8, 8.4], [-24.1, 6.8, 8.4], 'D', 0.5], ['tube', [-24.1, -6.8, 15.6], [-24.1, 6.8, 15.6], 'D', 0.5],
      ['tube', [23.6, 8.06, 5.2], [-23.6, 8.06, 5.2], 's', 1.0], ['tube', [23.6, -8.06, 5.2], [-23.6, -8.06, 5.2], 's', 1.0],   // la livree
      ['tube', [23.6, 8.06, 6.4], [-23.6, 8.06, 6.4], 's', 1.0], ['tube', [23.6, -8.06, 6.4], [-23.6, -8.06, 6.4], 's', 1.0],
      ['bloc', [16.4, 21.6], [8.02, 8.06], [1.4, 15.4], 'E', 'E', 'E', 0.05],               // les portes
      ['bloc', [-2.6, 2.6], [8.02, 8.06], [1.4, 15.4], 'E', 'E', 'E', 0.05],
      ['bloc', [-4.0, 4.0], [-4.4, 4.4], [18.2, 19.0], 'C', 'D', 'D', 0.1],                  // le socle du pantographe
      ['tube', [-3.0, -3.0, 19.0], [1.0, 0, 23.0], 'k', 0.3], ['tube', [-3.0, 3.0, 19.0], [1.0, 0, 23.0], 'k', 0.3],
      ['tube', [1.0, 0, 23.0], [-2.0, 0, 24.8], 'k', 0.3],
      ['tube', [-2.0, -4.0, 24.8], [-2.0, 4.0, 24.8], 'k', 0.3],                             // l'archet, sous le fil
    ],
    lampesDeChar(23.8, -23.8, 4.2, 7.9, 3.0, 4.6),
  ),
});
SPRITES.tramway = enVolume(MACHINE_TRAMWAY, 48, 80, Object.assign({}, SPRITES.autobus.pal, { c: '#e9e3d0', s: '#c0392b', e: '#3a3d44' }));
SPRITES.tramway.couleur = '#e9e3d0';
SPRITES.tramway.de = 'autobus';
SPRITES.luxe_vus = enVolume(MACHINE_LUXE_VUS, 32, 56, SPRITES.luxe.pal);
SPRITES.luxe.variantes = { luxe: 3, luxe_vus: 2 };
SPRITES.bateau_console = assisDedans(MACHINE_BATEAU_CONSOLE, 30, 48, 'volant', SPRITES.bateau.pal);
SPRITES.bateau.variantes = { bateau: 3, bateau_console: 2 };

/* --- LA FOIRE QUI ROULE, EN VOLUME ------------------------------------------------

   ⚠️ **Demande de Martin : « je veux aussi que le petit train soit dans le même
   style que les véhicules et qu'on puisse y faire un tour ».** Ses wagons étaient
   des grilles plates de 12 px tournées par seizièmes de tour — un jouet posé à
   côté d'une auto qui se projette à 32 caps. Ce sont maintenant des machines
   comme les chars : les mêmes pièces, le même biais du sol, le même contour, le
   même arrondi, et `Foire` les cuit au cap par `Atlas.cuireCap`.

   ⚠️ **PAS DANS `SPRITES`.** Ce ne sont pas des chars du catalogue : on ne les
   vole pas, ils n'ont ni phare ni feu à voir à 24 caps sur 32, et les juges du
   parc (`test_poses_vehicules.py`) les prendraient pour des autos ratées. Ils
   vivent à part, et `Foire` est le seul à les lire.

   À l'échelle du passant (9,1 px/m) : une locomotive de 2,2 m fait 20 px, un
   wagon 16, et 10 de large — deux bancs, et ceux qui y sont assis dépassent du
   bord comme dans la chaloupe (posture `volant`, les mains sur la barre de
   devant). `bancs` : où ils s'assoient, d'avant en arrière. */
const MACHINE_LOCO_FOIRE = {
  profondeur: BIAIS_DU_SOL, contour: true, arrondi: true,
  bancs: [[-6.2, 0, 4.4]],                                                                  // le machiniste
  pieces: [
    ['roue', 6.0, 2.4, 'r', 'x', 'M', 1, 4.4], ['roue', 6.0, 2.4, 'r', 'x', 'M', 1, -4.4],
    ['roue', -5.2, 2.4, 'r', 'x', 'M', 1, 4.4], ['roue', -5.2, 2.4, 'r', 'x', 'M', 1, -4.4],
    ['bloc', [-10.2, 10.2], [-3.4, 3.4], [2.0, 3.2], 'k', 'k', 'k', 0],                     // le chassis
    ['bloc', [-10.4, 10.4], [-4.8, 4.8], [3.2, 4.2], 'x', 'x', 'x', 0.02],                  // le tablier rouge
    // La chaudiere : un cylindre couche, en deux etages qui s'arrondissent.
    ['bloc', [-1.6, 8.2], [-3.2, 3.2], [4.2, 8.0], 'C', 'c', 'D', 0.03],
    ['bloc', [-1.6, 8.2], [-2.2, 2.2], [8.0, 9.0], 'C', 'C', 'c', 0.03],
    ['tube', [1.8, 3.25, 4.4], [1.8, 3.25, 8.0], 'y', 0.05], ['tube', [1.8, -3.25, 4.4], [1.8, -3.25, 8.0], 'y', 0.05],   // les cerclages
    ['tube', [5.4, 3.25, 4.4], [5.4, 3.25, 8.0], 'y', 0.05], ['tube', [5.4, -3.25, 4.4], [5.4, -3.25, 8.0], 'y', 0.05],
    ['bloc', [8.2, 9.8], [-3.0, 3.0], [4.2, 8.6], 'k', 'k', 'k', 0.04],                     // la boite a fumee
    ['bloc', [5.2, 7.0], [-1.0, 1.0], [9.0, 12.6], 'k', 'k', 'k', 0.05],                    // la cheminee
    ['bloc', [4.8, 7.4], [-1.4, 1.4], [12.6, 13.6], 'y', 'y', 'y', 0.05],                   // son chapeau
    ['bloc', [1.2, 3.0], [-1.0, 1.0], [9.0, 10.4], 'y', 'y', 'y', 0.05],                    // le dome
    ['bloc', [9.8, 10.6], [-0.9, 0.9], [6.0, 7.6], 'l', 'l', 'l', 0.3],                     // le fanal
    ['bloc', [10.4, 11.8], [-3.4, 3.4], [2.4, 3.2], 'B', 'B', 'B', 0.1],                    // le chasse-pierres
    // La cabine, ouverte : trois cotes a mi-hauteur, on voit qui la mene.
    ['bloc', [-10.2, -1.6], [4.2, 4.8], [4.2, 7.6], 'C', 'c', 'D', 0.02],
    ['bloc', [-10.2, -1.6], [-4.8, -4.2], [4.2, 7.6], 'C', 'c', 'D', 0.02],
    ['bloc', [-10.4, -9.8], [-4.8, 4.8], [4.2, 7.6], 'C', 'D', 'D', 0.02],
    ['bloc', [-10.6, -10.0], [-0.8, 0.8], [5.2, 6.4], 't', 't', 't', 0.3],                  // le feu de queue
    ['bloc', [-11.8, -10.4], [-0.6, 0.6], [2.4, 3.0], 'k', 'k', 'k', 0],                    // l'attelage
  ],
};
const MACHINE_WAGON_FOIRE = {
  profondeur: BIAIS_DU_SOL, contour: true, arrondi: true,
  bancs: [[2.6, 0, 4.2], [-4.2, 0, 4.2]],
  pieces: [
    ['roue', 5.0, 2.2, 'r', 'x', 'M', 1, 4.4], ['roue', 5.0, 2.2, 'r', 'x', 'M', 1, -4.4],
    ['roue', -5.0, 2.2, 'r', 'x', 'M', 1, 4.4], ['roue', -5.0, 2.2, 'r', 'x', 'M', 1, -4.4],
    ['bloc', [-8.2, 8.2], [-3.4, 3.4], [1.8, 3.0], 'k', 'k', 'k', 0],                       // le chassis
    ['bloc', [-8.0, 8.0], [-4.8, 4.8], [3.0, 3.6], 'u', 'u', 'u', 0.01],                    // le plancher
    ['bloc', [-8.0, 8.0], [4.2, 4.8], [3.6, 6.4], 'C', 'c', 'D', 0.02],                     // les flancs
    ['bloc', [-8.0, 8.0], [-4.8, -4.2], [3.6, 6.4], 'C', 'c', 'D', 0.02],
    ['bloc', [7.4, 8.0], [-4.8, 4.8], [3.6, 6.4], 'C', 'D', 'D', 0.02],                     // les bouts
    ['bloc', [-8.0, -7.4], [-4.8, 4.8], [3.6, 6.4], 'C', 'D', 'D', 0.02],
    ['tube', [-7.8, 4.85, 5.2], [7.8, 4.85, 5.2], 'y', 0.05], ['tube', [-7.8, -4.85, 5.2], [7.8, -4.85, 5.2], 'y', 0.05],   // le filet dore
    ['bloc', [1.6, 3.8], [-4.0, 4.0], [3.6, 4.6], 'u', 'u', 'u', 0.02],                     // les bancs
    ['bloc', [-5.2, -3.0], [-4.0, 4.0], [3.6, 4.6], 'u', 'u', 'u', 0.02],
    ['bloc', [8.0, 9.6], [-0.6, 0.6], [2.4, 3.0], 'k', 'k', 'k', 0],                        // l'attelage
  ],
};
/* LE CHARIOT DE LA MONTAGNE RUSSE : une caisse basse au nez arrondi, un dossier,
   la barre de securite, et DEUX passagers cote a cote.

   ⚠️ **Ses passagers sont DANS la machine**, pas des passants poses dessus comme
   dans le petit train : un chariot PENCHE (`Atlas.projeter`, `tangage`) — il
   grimpe la chaine, il plonge, il passe le looping la tete en bas — et un passant
   dessine debout resterait debout. Buste, tete et cheveux en blocs, chacun sa
   lettre (`a` `b` `g` a gauche, `d` `e` `f` a droite) : `Foire` y met les couleurs
   de qui est assis, le joueur compris. `bras` : les bras leves, quand ca plonge. */
function chariotDeMontagne(bras) {
  const pieces = [
    // Les roues, sur le rail. ⚠️ Gris et étroites : noires et de toute la largeur, la
    // tête en bas au looping on ne voyait plus qu'elles.
    ['bloc', [-4.6, 4.6], [-1.6, 1.6], [0.0, 1.4], 'r', 'r', 'r', 0],
    ['profil', [[7.2, 1.4], [7.4, 3.0], [5.6, 5.0], [-6.2, 5.0], [-7.0, 4.2], [-7.0, 1.4]],
     [[-7.2, 4.0], [-5.6, 4.5], [5.0, 4.5], [7.6, 2.8]], 'c', 'DCCCDD', 0],
    ['tube', [6.6, 4.55, 2.8], [-6.6, 4.55, 2.8], 'y', 0.05], ['tube', [6.6, -4.55, 2.8], [-6.6, -4.55, 2.8], 'y', 0.05],
    ['bloc', [-6.4, -5.2], [-4.0, 4.0], [5.0, 8.6], 'D', 'D', 'D', 0.02],                    // le dossier
    ['tube', [1.0, -3.8, 7.4], [1.0, 3.8, 7.4], 'M', 0.3],                                   // la barre
    ['bloc', [6.2, 7.4], [-0.8, 0.8], [3.2, 4.2], 'l', 'l', 'l', 0.3],                       // le fanal du nez
  ];
  [[-2.1, 'a', 'b', 'g'], [2.1, 'd', 'e', 'f']].forEach(function (p) {
    const w = p[0];
    pieces.push(['bloc', [-3.6, -1.4], [w - 1.3, w + 1.3], [5.0, 8.0], p[1], p[1], p[1], 0.05]);   // le buste
    pieces.push(['bloc', [-3.2, -1.2], [w - 1.0, w + 1.0], [8.0, 10.0], p[3], p[3], p[3], 0.06]);  // la tete
    pieces.push(['bloc', [-3.4, -1.0], [w - 1.1, w + 1.1], [10.0, 10.8], p[2], p[2], p[2], 0.07]); // les cheveux
    if (bras) {
      pieces.push(['tube', [-2.2, w - 1.4, 7.6], [-1.6, w - 2.2, 12.6], p[3], 0.08]);
      pieces.push(['tube', [-2.2, w + 1.4, 7.6], [-1.6, w + 2.2, 12.6], p[3], 0.08]);
    }
  });
  return { profondeur: BIAIS_DU_SOL, contour: true, arrondi: true, pieces: pieces };
}
/* LA NACELLE DE LA GRANDE ROUE : un baquet pendu a son attache par deux bras, et
   deux passagers cote a cote, face a nous. ⚠️ Son point de sol est l'ATTACHE, en
   haut : tout le reste pend en dessous (`z` negatif), et elle ne tourne jamais —
   une nacelle pend toujours droite, c'est la roue qui tourne. Les passagers sont
   dans la machine, comme dans le chariot, et pour la meme raison d'echelle : la
   roue fait 72 px de diametre, un passant debout en ferait le sixieme. `vide` :
   sans personne. */
function nacelleDeRoue(vide) {
  const pieces = [
    // La tige, et la barre ou pend le baquet. ⚠️ Deux bras en V faisaient, cernes de
    // noir, une pointe de cloche sur chaque nacelle.
    ['tube', [0, 0, 0], [-2.6, 0, -4.8], 'M', 0.1],
    ['tube', [-2.6, -3.6, -4.8], [-2.6, 3.6, -4.8], 'M', 0.1],
    ['bloc', [-3.0, 3.0], [-4.0, 4.0], [-10.4, -9.6], 'D', 'D', 'D', 0],                    // le fond
    ['bloc', [-3.0, 3.0], [3.4, 4.0], [-9.6, -5.6], 'C', 'c', 'D', 0.02],                   // les flancs
    ['bloc', [-3.0, 3.0], [-4.0, -3.4], [-9.6, -5.6], 'C', 'c', 'D', 0.02],
    ['bloc', [2.4, 3.0], [-4.0, 4.0], [-9.6, -6.6], 'C', 'c', 'D', 0.02],                   // devant, plus bas
    ['bloc', [-3.0, -2.4], [-4.0, 4.0], [-9.6, -5.0], 'C', 'D', 'D', 0.02],                 // le dossier
    ['tube', [3.05, -4.0, -6.8], [3.05, 4.0, -6.8], 'y', 0.05],                             // le filet
  ];
  if (!vide) {
    [[-1.8, 'a', 'b', 'g'], [1.8, 'd', 'e', 'f']].forEach(function (p) {
      const w = p[0];
      pieces.push(['bloc', [-1.8, 0.2], [w - 1.2, w + 1.2], [-9.6, -6.8], p[1], p[1], p[1], 0.04]);  // le buste
      pieces.push(['bloc', [-1.6, 0.0], [w - 0.9, w + 0.9], [-6.8, -4.8], p[3], p[3], p[3], 0.05]);  // la tete
      pieces.push(['bloc', [-1.8, 0.2], [w - 1.0, w + 1.0], [-4.8, -4.2], p[2], p[2], p[2], 0.06]);  // les cheveux
    });
  }
  return { profondeur: BIAIS_DU_SOL, contour: true, arrondi: true, pieces: pieces };
}

const PALETTE_CHARIOT = { k: '#101018', c: '#c0392b', y: '#e2b33c', l: '#fff3b0', r: '#5e626a',
                          a: '#3f7fc4', b: '#3b2a20', g: '#e8b088', d: '#f2d34f', e: '#d8b36a', f: '#f0c9a0' };

//: Les machines de la foire, cuites comme un char (`enVolume`) — et lues par `Foire` seul.
const FOIRE_EN_VOLUME = {
  loco: enVolume(MACHINE_LOCO_FOIRE, 20, 40, { k: '#101018', c: '#2f7d4f', r: '#1a1a1e', x: '#c0392b', y: '#e2b33c', l: '#fff3b0', t: '#ff4b3e' }),
  wagon: enVolume(MACHINE_WAGON_FOIRE, 16, 32, { k: '#101018', c: '#e8a33a', r: '#1a1a1e', x: '#c0392b', y: '#e2b33c', u: '#8a6a44' }),
  // ⚠️ Une toile de 36 : le chariot pivote sur son rail dans tous les sens, bras leves compris.
  chariot: enVolume(chariotDeMontagne(false), 14, 36, PALETTE_CHARIOT),
  chariot_bras: enVolume(chariotDeMontagne(true), 14, 36, PALETTE_CHARIOT),
  // ⚠️ Une toile de 28 : l'attache au milieu, le baquet dix pixels plus bas.
  nacelle: enVolume(nacelleDeRoue(false), 6, 28, PALETTE_CHARIOT),
  nacelle_vide: enVolume(nacelleDeRoue(true), 6, 28, PALETTE_CHARIOT),
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
  /* --- Le sol d'un pate de maisons ---------------------------------------

     Trottoir, herbe, ruelle : 43 % de la ville a eux trois, et la plus grande
     surface qu'elle ait. Les trois se peignaient pareil — un aplat, quelques
     points de bruit, quatre variantes — et c'est ce qui donnait a la ville son
     air de papier peint des qu'on prenait de la hauteur.

     ⚠️ Deux regles tiennent tout ce bloc, et elles viennent du stationnement,
     qui les a apprises avant :
       1. AUCUNE USURE NE TOUCHE LE BORD DE LA TUILE. Une fissure ou une tache
          coupee net au seizieme pixel redessine la grille, et la ville entiere
          redevient un quadrillage.
       2. L'usure est un DESSIN, pas du bruit : elle ne vient que d'une variante
          sur quatre ou cinq (`Monde.USURES_DE_SOL` en compte seize). Un
          trottoir dont chaque dalle est fendue n'est pas un vieux trottoir,
          c'est un motif. */

  /** Une fissure fine dans une dalle : une ligne qui se promene, et qui
      s'arrete a trois pixels du bord. */
  function fendillement(ctx, v, T, couleur) {
    ctx.fillStyle = couleur;
    let x = 4 + Math.floor(bruit(v, 3) * 7);
    for (let y = 3; y < T - 3; y++) {
      ctx.fillRect(x, y, 1, 1);
      if (bruit(v, 20 + y) < 0.4) x += bruit(v, 40 + y) < 0.5 ? -1 : 1;
      x = Math.max(3, Math.min(T - 4, x));
    }
  }

  /** Un rapiecage : quelqu'un a ouvert le sol et l'a referme autrement. Deux
      rectangles decales, parce qu'un seul se lit comme une boite. */
  function rapiecage(ctx, v, T, couleur) {
    const x = 3 + Math.floor(bruit(v, 5) * 3), y = 3 + Math.floor(bruit(v, 6) * 3);
    ctx.fillStyle = couleur;
    ctx.fillRect(x, y, Math.min(7 + Math.floor(bruit(v, 7) * 3), T - 3 - x),
                 Math.min(4 + Math.floor(bruit(v, 8) * 3), T - 3 - y));
    ctx.fillRect(x + 1, y + 2, Math.min(5 + Math.floor(bruit(v, 9) * 4), T - 4 - x),
                 Math.min(4 + Math.floor(bruit(v, 10) * 3), T - 5 - y));
  }

  /** Une tache : deux barres croisees, comme l'huile du stationnement mais
      seche et pale — de l'eau de lavage, du cafe renverse, du sel. */
  function souillure(ctx, v, T, couleur) {
    const cx = 5 + Math.floor(bruit(v, 11) * 5), cy = 5 + Math.floor(bruit(v, 12) * 5);
    ctx.fillStyle = couleur;
    ctx.fillRect(cx - 2, cy - 1, 5, 3);
    ctx.fillRect(cx - 1, cy - 2, 3, 5);
  }

  //: Le beton du trottoir. `joint` est le creux entre deux dalles, `arete` le
  //: chant qui prend le jour juste a cote.
  const BETON = { fond: '#9a9689', joint: '#8a8578', arete: '#a7a396', grain: '#8f8b7f',
                  fissure: '#7f7b70', rapiece: '#827e74', tache: '#8c8879', mousse: '#6c7c58' };

  /** Le trottoir : la plus grande surface de la ville.

      `v` porte la place de la tuile dans sa DALLE (bit 0 = elle est a l'est de
      son joint, bit 1 = au sud) et son usure au-dessus — voir
      `Monde.varianteDeSol`. Une dalle fait DEUX tuiles de cote : c'est ce qui
      enleve a la ville le quadrillage de seize pixels qu'elle portait. */
  //: ⚠️ LE TROTTOIR DIT LE QUARTIER (des quartiers qu'on reconnait, 2e vague).
  //: Une rue commercante chic a un granit pale et lave ; une cour d'usine, un
  //: beton sombre qui a bu de l'huile. `Monde.varianteDeSol` porte l'usage et le
  //: standing au-dessus de l'usure (bits 6 a 9) : c'est une couche PEINTE, le
  //: glyphe ne change pas.
  const BETON_CHIC = { fond: '#a9a598', joint: '#968f82', arete: '#b8b4a7', grain: '#a09c90',
                       fissure: '#8a8679', rapiece: '#948f84', tache: '#9c988b', mousse: '#7a8a66' };
  const BETON_USINE = { fond: '#7d7b75', joint: '#6b6963', arete: '#8a8881', grain: '#72706a',
                        fissure: '#5f5d58', rapiece: '#6d6b65', tache: '#45434a', mousse: '#5f6752' };

  function trottoir(ctx, v, T) {
    const joinOuest = (v & 1) === 0, joinNord = (v & 2) === 0;
    const usure = (v >> 2) & 15, usage = (v >> 6) & 3, rang = (v >> 8) & 3;
    const pal = usage === 3 ? BETON_USINE : rang === 1 ? BETON_CHIC : BETON;
    // ⚠️ L'USURE SE DEPLACE, comme la salete : une rue cossue n'a ni fissure ni
    // rapiecage ; une rue pauvre en a davantage — les memes dessins, pas un motif
    // de plus. Et le beton d'usine est tache une dalle sur quatre.
    // ⚠️ Des FISSURES de plus, pas des rapiecages : le rapiecage est un carre, et
    // une rue pauvre qui en montrait une dalle sur deux se lisait comme un damier.
    let marque = usure;
    if (rang === 1 && usure >= 12) marque = 0;
    else if (usage === 3 && usure === 10) marque = 15;
    else if (rang === 2 && (usure === 10 || usure === 11)) marque = 13;
    plein(ctx, pal.fond, T);
    points(ctx, usure + 1, T, pal.grain, 6, 7);
    points(ctx, usure + 1, T, pal.arete, 4, 41);
    if (marque === 13) fendillement(ctx, usure + 1, T, pal.fissure);
    else if (marque === 14) rapiecage(ctx, usure + 1, T, pal.rapiece);
    else if (marque === 15) souillure(ctx, usure + 1, T, pal.tache);
    // Les joints, EN DERNIER : rien ne passe par-dessus le bord d'une dalle.
    if (joinOuest) {
      ctx.fillStyle = pal.joint; ctx.fillRect(0, 0, 1, T);
      ctx.fillStyle = pal.arete; ctx.fillRect(1, 0, 1, T);
      // Un peu de mousse dans le joint, une dalle sur huit : c'est elle qui dit
      // qu'il y a de la terre dessous et que personne ne passe le balai.
      if (marque === 12) { ctx.fillStyle = pal.mousse; for (let y = 3; y < T - 3; y += 4) ctx.fillRect(0, y, 1, 1); }
    }
    if (joinNord) {
      ctx.fillStyle = pal.joint; ctx.fillRect(0, 0, T, 1);
      ctx.fillStyle = pal.arete; ctx.fillRect(0, 1, T, 1);
      if (marque === 12) { ctx.fillStyle = pal.mousse; for (let x = 3; x < T - 3; x += 4) ctx.fillRect(x, 0, 1, 1); }
    }
  }

  //: Le gazon. ⚠️ Il couvre les cours, les parcs et toute la banlieue : c'est
  //: le vert qu'on voit le plus, et il etait rigoureusement uniforme.
  const GAZON = { fond: '#4f8d3e', clair: '#5a9c47', sombre: '#427a33',
                  brin: '#6aad55', terre: '#6d5c3e', terre2: '#7d6c4c', fleur: '#cfc95c' };

  function herbe(ctx, v, T) {
    plein(ctx, GAZON.fond, T);
    points(ctx, v + 1, T, GAZON.clair, 12, 3);
    points(ctx, v + 1, T, GAZON.sombre, 8, 60);
    if (v === 12 || v === 13) {
      // Des touffes : trois brins debout, et c'est tout ce qu'il faut pour que
      // le gazon cesse d'etre un aplat.
      ctx.fillStyle = GAZON.brin;
      for (let i = 0; i < 3; i++) {
        const x = 3 + Math.floor(bruit(v + 1, 13 + i) * (T - 6));
        const y = 3 + Math.floor(bruit(v + 1, 23 + i) * (T - 7));
        ctx.fillRect(x, y, 1, 3);
        ctx.fillRect(x + 1, y + 1, 1, 2);
      }
    } else if (v === 14) {
      // Le gazon a pele : de la terre, la ou l'on coupe toujours au meme
      // endroit. Jamais jusqu'au bord — sinon c'est un carre de terre.
      const x = 4 + Math.floor(bruit(v + 1, 33) * 4), y = 4 + Math.floor(bruit(v + 1, 34) * 4);
      ctx.fillStyle = GAZON.terre;
      ctx.fillRect(x, y, 6, 4); ctx.fillRect(x + 1, y - 1, 4, 6);
      ctx.fillStyle = GAZON.terre2;
      ctx.fillRect(x + 2, y + 1, 3, 2);
    } else if (v === 15) {
      // Des pissenlits : TROIS, et jamais alignes — quatre points tires dans
      // la meme suite se rangeaient en diagonale, et une pelouse entiere de
      // diagonales jaunes n'est pas une pelouse (c'est la lecon du bruit, deja
      // apprise en haut de ce fichier pour l'asphalte).
      ctx.fillStyle = GAZON.fleur;
      for (let i = 0; i < 3; i++) {
        ctx.fillRect(3 + Math.floor(bruit(v + 1, 43 + i * 7) * (T - 6)),
                     3 + Math.floor(bruit(v + 1, 91 - i * 5) * (T - 6)), 1, 1);
      }
    }
  }

  //: La friche : le sol d'un TERRAIN VAGUE, et pas du gazon plus pale. ⚠️ Un
  //: lot abandonne se peignait avec `,` — l'herbe des parcs et des cours de
  //: banlieue — et de haut il avait donc exactement la surface d'un parterre
  //: entretenu : Martin a appele ca un champ, et c'en etait un. Ce qui change
  //: n'est pas le detail, c'est le FOND : kaki et desature la ou le gazon est
  //: vert et franc. Un lot se reconnait d'un ecran de distance ou il ne se
  //: reconnait pas.
  const FRICHE = { fond: '#6d6845', clair: '#7b7551', sombre: '#5b5638',
                   terre: '#7e6b49', terre2: '#8d7a57', sec: '#a4975f',
                   gravier: '#8b8878', suie: '#43402f' };

  function friche(ctx, v, T) {
    plein(ctx, FRICHE.fond, T);
    points(ctx, v + 1, T, FRICHE.clair, 11, 5);
    points(ctx, v + 1, T, FRICHE.sombre, 9, 63);
    if (v === 12 || v === 13) {
      // La terre a perce. ⚠️ Plus large que le rond pele d'un gazon (`herbe`,
      // v === 14), et c'est voulu : la pelouse pele la ou l'on passe toujours
      // au meme endroit, une friche pele parce que plus rien ne la tient.
      const x = 3 + Math.floor(bruit(v + 1, 33) * 4), y = 3 + Math.floor(bruit(v + 1, 34) * 4);
      ctx.fillStyle = FRICHE.terre;
      ctx.fillRect(x, y, 8, 6); ctx.fillRect(x + 1, y - 1, 6, 8);
      ctx.fillStyle = FRICHE.terre2;
      ctx.fillRect(x + 2, y + 1, 4, 3); ctx.fillRect(x + 3, y + 4, 2, 2);
    } else if (v === 14) {
      // Les herbes hautes : ce qui pousse quand plus personne ne tond. Des
      // brins de CINQ pixels — le gazon en met trois, et c'est a peu pres
      // toute la difference entre une pelouse et un lot laisse a lui-meme.
      ctx.fillStyle = FRICHE.sec;
      for (let i = 0; i < 4; i++) {
        const x = 3 + Math.floor(bruit(v + 1, 13 + i) * (T - 6));
        const y = 3 + Math.floor(bruit(v + 1, 23 + i) * (T - 9));
        ctx.fillRect(x, y, 1, 5);
        ctx.fillRect(x + 1, y + 2, 1, 3);
      }
    } else if (v === 15) {
      points(ctx, v + 1, T, FRICHE.gravier, 8, 81);      // du gravat en miettes
      points(ctx, v + 1, T, FRICHE.suie, 4, 17);         // et ce qu'on y a brule
    }
  }

  //: La ruelle : deux tuiles derriere chaque bande d'ilot, sur toute sa
  //: largeur — le fond de cour de la ville entiere. ⚠️ C'etait un aplat gris
  //: avec huit points dessus, d'un bout a l'autre de Baie-des-Brumes. Un fond
  //: de cour, c'est justement l'endroit qu'on ne refait jamais : de l'asphalte
  //: rapiece, du gravier, de l'huile et des fissures.
  //: largeur — le fond de cour de la ville entiere. ⚠️ C'etait un aplat gris
  //: avec huit points dessus, d'un bout a l'autre de Baie-des-Brumes. Un fond
  //: de cour, c'est justement l'endroit qu'on ne refait jamais : de l'asphalte
  //: rapiece, du gravier, de l'huile et des fissures.
  const RUELLE = { fond: '#4e4b45', clair: '#5b5851', sombre: '#403d38',
                   goudron: '#37342f', gravier: '#6a665d', fissure: '#35322d' };

  function ruelle(ctx, v, T) {
    plein(ctx, RUELLE.fond, T);
    points(ctx, v + 1, T, RUELLE.clair, 7, 9);
    points(ctx, v + 1, T, RUELLE.sombre, 9, 70);
    if (v === 12) {
      // Un rapiecage de goudron : la tranchee qu'on a rebouchee. ⚠️ Un JOINT
      // d'un bord a l'autre de la tuile aurait ete plus juste — sauf qu'il ne
      // se raccorde pas a celui de la voisine, et une ville de bouts de joint
      // qui s'arretent tous les seize pixels, c'est la grille de la carte.
      rapiecage(ctx, v + 1, T, RUELLE.goudron);
    } else if (v === 13) {
      tacheDHuile(ctx, v + 1, T);
    } else if (v === 14) {
      fendillement(ctx, v + 1, T, RUELLE.fissure);
    } else if (v === 15) {
      points(ctx, v + 1, T, RUELLE.gravier, 9, 81);    // du gravier qui remonte
    }
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

  /** L'usure d'un toit plat : ce qui l'empeche d'etre une couleur.

      ⚠️ Un toit se voit d'aussi loin qu'une rue et il en couvre autant : les
      entrepots de La Shop font trois cents tuiles d'un seul tenant. Le champ et
      le bord suffisaient pour un toit de commerce de vingt tuiles ; a cette
      taille-la, il fallait que quelque chose ARRIVE dessus. Trois choses, et
      toutes les trois sont vraies d'un vrai toit plat : la membrane qu'on a
      rapiecee, l'eau qui ne s'est jamais rendue au drain, et la rouille qui
      coule sous un event.

      ⚠️ Comme toute usure de ce fichier : jamais au bord de la tuile. */
  function usureDeToit(ctx, v, T, style) {
    if (v === 5) {
      // Un rapiecage de membrane. ⚠️ EN CROIX, pas en rectangle : un carre
      // sombre pose au milieu d'une tuile de seize pixels, repete une tuile sur
      // huit, dessine la grille au lieu de l'effacer — c'est tout le contraire
      // de ce qu'une usure doit faire, et ca se voyait d'un bout a l'autre de
      // La Shop.
      souillure(ctx, v + 1, T, style.sombre);
      souillure(ctx, v + 9, T, style.sombre);
    } else if (v === 6) {                        // une flaque qui ne part pas
      const x = 3 + Math.floor(bruit(v + 1, 17) * 4), y = 4 + Math.floor(bruit(v + 1, 18) * 4);
      ctx.fillStyle = 'rgba(28,36,48,0.30)';
      ctx.fillRect(x, y, 9, 5); ctx.fillRect(x + 2, y - 1, 6, 7);
      ctx.fillStyle = 'rgba(160,190,220,0.14)';  // le ciel dedans
      ctx.fillRect(x + 2, y, 5, 1);
    } else if (v === 7) {                        // une coulee de rouille
      ctx.fillStyle = 'rgba(122,72,40,0.34)';
      const x = 4 + Math.floor(bruit(v + 1, 19) * 8);
      for (let y = 3; y < T - 3; y++) ctx.fillRect(x + (bruit(v + 1, 30 + y) < 0.3 ? 1 : 0), y, 2, 1);
    }
  }

  function toitPlat(ctx, v, T, style) {
    const grain = v >> 4;
    champDeToit(ctx, grain + 1, T, style);
    usureDeToit(ctx, grain, T, style);
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

  /* --- L'abord ----------------------------------------------------------------

     ⚠️ La couronne d'un bloc bati, entre ses murs et le trottoir : ni beton
     coule (le trottoir) ni gazon (la cour). Des PAVES, plus sombres et plus
     chauds que la dalle, avec leurs joints — de quoi lire d'un coup d'oeil que
     ce n'est pas le trottoir, sans que ca ait l'air d'un obstacle. C'est un
     debordement : on y marche quand la dalle est pleine, on y range les
     lampadaires et les kiosques, et le flaneur prefere la dalle. */
  //: ⚠️ L'ABORD DIT L'USAGE (2e vague) : des paves devant les commerces, une
  //: bande de gazon devant les maisons, de l'asphalte tache devant les usines.
  //: `Monde.varianteDAbord` : l'usure (bits 0 a 3), l'usage (4 et 5), le
  //: standing (6 et 7). Le port et les parcs gardent les paves.
  function abord(ctx, v, T) {
    const usure = v & 15, usage = (v >> 4) & 3, rang = (v >> 6) & 3;
    if (usage === 2) return bandeDeGazon(ctx, usure, rang, T);
    if (usage === 3) return asphalteDUsine(ctx, usure, rang, T);
    // Les paves : quatre rangees de deux, decalees une rangee sur deux. Plus
    // chauds et laves en cossu.
    plein(ctx, rang === 1 ? '#74665a' : '#6d665a', T);
    ctx.fillStyle = rang === 1 ? '#86766a' : '#7a7266';
    for (let r = 0; r < 4; r++) {
      const dec = (r % 2) * 4;
      for (let x = -4 + dec; x < T; x += 8) ctx.fillRect(Math.max(0, x + 1), r * 4 + 1, Math.min(T, x + 7) - Math.max(0, x + 1), 2);
    }
    points(ctx, usure + 1, T, '#5c5549', rang === 1 ? 2 : 5, 23);
    points(ctx, usure + 1, T, '#847c6f', 3, 61);
    // En pauvre, des paves manquent : un trou de terre, jamais jusqu'au bord.
    if (rang === 2 && usure >= 10) {
      const x = 4 + Math.floor(bruit(usure + 1, 70) * 5), y = 4 + Math.floor(bruit(usure + 1, 71) * 5);
      ctx.fillStyle = '#5a4f40'; ctx.fillRect(x, y, 6, 3); ctx.fillRect(x + 1, y + 3, 4, 2);
    }
  }

  /** La bande de gazon devant les maisons : tondue en rayures chez les riches,
      brulee par plaques chez les pauvres. */
  function bandeDeGazon(ctx, usure, rang, T) {
    plein(ctx, rang === 2 ? '#6f8a3e' : GAZON.fond, T);
    if (rang === 1) {
      // Les passes de tondeuse : des bandes de quatre pixels, qui se raccordent
      // d'une tuile a l'autre parce qu'elles tombent aux memes rangees.
      ctx.fillStyle = GAZON.clair;
      for (let y = 0; y < T; y += 8) ctx.fillRect(0, y, T, 4);
      return;
    }
    points(ctx, usure + 1, T, GAZON.clair, 10, 3);
    points(ctx, usure + 1, T, GAZON.sombre, 6, 60);
    if (rang === 2 && usure >= 6) {
      const x = 3 + Math.floor(bruit(usure + 1, 80) * 5), y = 3 + Math.floor(bruit(usure + 1, 81) * 5);
      ctx.fillStyle = '#9a8a4a'; ctx.fillRect(x, y, 7, 5); ctx.fillRect(x + 2, y - 1, 4, 7);
      ctx.fillStyle = '#7d6c3e'; ctx.fillRect(x + 2, y + 1, 3, 2);
    }
  }

  /** L'abord d'une usine : de l'asphalte qui n'a jamais ete refait, et l'huile. */
  function asphalteDUsine(ctx, usure, rang, T) {
    plein(ctx, '#45474d', T);
    points(ctx, usure + 1, T, '#51535a', 8, 5);
    points(ctx, usure + 1, T, '#3a3c41', 6, 90);
    // ⚠️ Rare, et a peine plus sombre que l'asphalte : seize usures seulement, donc
    // seize places de tache — frequente et contrastee, elle s'alignait en pointille.
    if (usure >= (rang === 2 ? 13 : 15)) souillure(ctx, usure + 1, T, '#393a3f');
  }

  return {
    ',': herbe,
    ';': friche,
    '.': trottoir,
    '_': abord,
    'x': ruelle,
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
    //
    // ⚠️ TROIS DE BANDE, CINQ DE VIDE, et les deux chiffres viennent de la
    // norme, pas du gout : une bande de passage fait 0,50 m et l'interdistance
    // 0,50 a 0,80 m — le VIDE est plus large que la bande. Ici c'etait
    // l'inverse (3 de bande, 2 de vide), et un passage se lisait comme un mur
    // blanc. A l'echelle du jeu (une tuile de 16 px pour une voie d'environ
    // 3 m, donc 1 px ≈ 0,20 m), 3 px font 0,60 m et 5 px font 1 m.
    //
    // ⚠️ Et le PAS DIVISE LA TUILE. A 5, les bandes tombaient a 1, 6, 11 : deux
    // pixels de vide dedans, TROIS a la couture entre deux tuiles. Le motif
    // boitait a chaque tuile sans qu'on sache pourquoi. A 8, elles tombent a 1
    // et 9, et le vide fait cinq partout — y compris par-dessus la couture.
    '=': function (ctx, v, T) {
      asphalte(ctx, v, T); ctx.fillStyle = '#e8e6de';
      const x0 = v === 1 ? T - 5 : 0, l = v === 0 ? T : 5;
      for (let y = 1; y < T; y += 8) ctx.fillRect(x0, y, l, 3);
    },
    ':': function (ctx, v, T) {
      asphalte(ctx, v, T); ctx.fillStyle = '#e8e6de';
      const y0 = v === 1 ? T - 5 : 0, h = v === 0 ? T : 5;
      for (let x = 1; x < T; x += 8) ctx.fillRect(x, y0, 3, h);
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
    's': function (ctx, v, T) {
      plein(ctx, '#d8c48a', T);
      points(ctx, v + 1, T, '#c9b576', 10, 4);
      points(ctx, v + 1, T, '#e3d29d', 6, 47);
      if (v === 15) points(ctx, v + 1, T, '#b2a06a', 7, 88);        // des galets
    },
    // L'allee de parc : de la poussiere de pierre, plus grise et plus grenue
    // que le sable de la greve — on doit pouvoir dire d'un coup d'oeil si l'on
    // marche au bord de l'eau ou au milieu d'une pelouse.
    'g': function (ctx, v, T) {
      plein(ctx, '#c3b492', T);
      points(ctx, v + 1, T, '#b2a381', 12, 4);
      points(ctx, v + 1, T, '#d2c5a6', 8, 55);
      if (v === 14 || v === 15) points(ctx, v + 1, T, '#9c8e70', 6, 96);   // du gravier plus gros
    },
    // ⚠️ LA VOIE DU PETIT TRAIN DE LA FOIRE. La variante vient de
    // `Monde.varianteDeRail` : les bits 1/2/4/8 disent de quel cote la voie
    // continue (nord/est/sud/ouest, la lecture de la cloture), le bit 16 que
    // c'est un PASSAGE A NIVEAU (une allee la croise : des planches entre les
    // rails), et les bits hauts le grain du gazon dessous.
    // ⚠️ Une courbe est un QUART DE CERCLE de rayon 8 autour du coin de la
    // tuile — exactement la courbe que suit le train (`Foire`). Une voie peinte
    // en equerre sous un train qui tourne rond, c'est un train qui deraille.
    'T': function (ctx, v, T) {
      herbe(ctx, (v >> 5) & 15, T);
      const m = v & 15, m2 = T / 2;
      const droite = m === 10 || m === 5;
      // Le ballast, puis les traverses, puis les rails : deux fils d'acier a
      // trois pixels de l'axe (un ecartement de train de foire).
      if (droite) {
        const h = m === 10;
        ctx.fillStyle = '#7d7466';
        if (h) ctx.fillRect(0, m2 - 5, T, 10); else ctx.fillRect(m2 - 5, 0, 10, T);
        ctx.fillStyle = '#6a6256';
        for (let k = 1; k < T; k += 5) { if (h) ctx.fillRect(k, m2 - 5, 1, 10); else ctx.fillRect(m2 - 5, k, 10, 1); }
        ctx.fillStyle = (v & 16) ? '#9a7b52' : '#5b3f28';
        for (let k = 1; k < T; k += 3) { if (h) ctx.fillRect(k, m2 - 4, 2, 8); else ctx.fillRect(m2 - 4, k, 8, 2); }
        if (v & 16) {                               // le passage a niveau : on marche sur du bois
          ctx.fillStyle = '#b08d5f';
          if (h) ctx.fillRect(0, m2 - 2, T, 4); else ctx.fillRect(m2 - 2, 0, 4, T);
        }
        for (const [d, c] of [[-3, '#c9ccd1'], [2, '#8b9097']]) {
          ctx.fillStyle = c;
          if (h) ctx.fillRect(0, m2 + d, T, 1); else ctx.fillRect(m2 + d, 0, 1, T);
        }
        return;
      }
      // Une courbe : le coin vers lequel elle tourne est celui des deux voisines.
      const ox = (m & 2) ? T : 0, oy = (m & 4) ? T : 0;
      const anneau = function (r0, r1, couleur, pas) {
        ctx.fillStyle = couleur;
        for (let y = 0; y < T; y++) {
          for (let x = 0; x < T; x++) {
            const d = Math.hypot(x + 0.5 - ox, y + 0.5 - oy);
            if (d < r0 || d >= r1) continue;
            if (pas && Math.floor(Math.atan2(Math.abs(y + 0.5 - oy), Math.abs(x + 0.5 - ox)) * 12) % pas !== 0) continue;
            ctx.fillRect(x, y, 1, 1);
          }
        }
      };
      anneau(3, 13, '#7d7466', 0);
      anneau(4, 12, '#5b3f28', 3);
      anneau(4.5, 5.5, '#8b9097', 0);
      anneau(10.5, 11.5, '#c9ccd1', 0);
    },
    // ⚠️ QUATRE TUILES FONT UN ROND, pas quatre carres. Chaque tuile porte un
    // QUART du disque, et elle sait lequel en lisant ses voisines (`bloc` dans
    // LEGENDE, bits 1/2/4/8 = nord/est/sud/ouest) : le centre du cercle est du
    // cote ou les voisines se trouvent. Peintes chacune pour soi, les quatre
    // tuiles montraient quatre margelles et quatre bassins — c'est la premiere
    // chose que Martin a vue.
    //
    // ⚠️ Et une piscine n'est pas la baie : une eau plus CLAIRE, une margelle
    // pale. Le meme bleu que la baie, et le joueur se demanderait s'il peut s'y
    // noyer — la reponse est non, et l'image doit le dire avant lui.
    'o': function (ctx, v, T) {
      plein(ctx, '#4f8d3e', T); points(ctx, v, T, '#427a33', 8, 60);     // le gazon dessous
      const cx = (v & 2) ? T : 0, cy = (v & 4) ? T : 0;                  // est / sud
      const bord = T - 0.5, eau = T - 2.5;
      for (let y = 0; y < T; y++) {
        for (let x = 0; x < T; x++) {
          const d = Math.hypot(x + 0.5 - cx, y + 0.5 - cy);
          if (d > bord) continue;
          ctx.fillStyle = d > eau ? '#e8e2cf' : (((x + y + (v >> 4)) % 7) ? '#3fa7c4' : '#5cc3dc');
          ctx.fillRect(x, y, 1, 1);
        }
      }
    },
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

    /* --- L'hopital -------------------------------------------------------

       Le lit d'hopital : UNE place, un cadre de metal, des draps blancs.
       ⚠️ `v & 15` est le masque des cotes ou le lit CONTINUE, comme pour le lit
       de chambre (`'l'`) : la tete de lit a barreaux et l'oreiller ne vont qu'a
       la tuile de tete, les roulettes et le pied qu'a la tuile du bout. Le
       MALADE n'est pas dans ce dessin : c'est une entite couchee par-dessus
       (`alite`), et la couverture qui commence a la dixieme rangee est ce qui
       le couvre jusqu'a la poitrine. */
    'r': function (ctx, v, T) {
      const nord = !(v & 1), est = !(v & 2), sud = !(v & 4), ouest = !(v & 8);   // ou le lit S'ARRETE
      const x0 = ouest ? 2 : 0, x1 = est ? T - 2 : T;
      const y0 = nord ? 1 : 0, y1 = sud ? T - 2 : T;
      if (sud) { ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.fillRect(x0 + 1, T - 1, x1 - x0 - 1, 1); }
      ctx.fillStyle = '#8e969e';                        // le cadre de metal
      ctx.fillRect(x0, y0, x1 - x0, y1 - y0);
      const mx0 = ouest ? 3 : 0, mx1 = est ? T - 3 : T;
      const my0 = nord ? 3 : 0, my1 = sud ? T - 3 : T;
      ctx.fillStyle = '#eef1f2';                        // le drap
      ctx.fillRect(mx0, my0, mx1 - mx0, my1 - my0);
      if (nord) {
        ctx.fillStyle = '#5f676f';                      // la tete de lit, a barreaux
        ctx.fillRect(x0, y0, x1 - x0, 2);
        ctx.fillStyle = '#c9ccd2';
        for (let x = x0 + 1; x < x1 - 1; x += 3) ctx.fillRect(x, y0, 1, 2);
        ctx.fillStyle = '#ffffff';                      // l'oreiller
        ctx.fillRect(mx0 + 1, 4, mx1 - mx0 - 2, 4);
        ctx.fillStyle = '#d5dadd';
        ctx.fillRect(mx0 + 1, 7, mx1 - mx0 - 2, 1);
      }
      const cy0 = nord ? 10 : 0, cy1 = sud ? T - 4 : T;
      ctx.fillStyle = '#9cc3d6';                        // la couverture d'hopital, bleu pale
      ctx.fillRect(mx0, cy0, mx1 - mx0, cy1 - cy0);
      if (nord) { ctx.fillStyle = '#eef1f2'; ctx.fillRect(mx0, 10, mx1 - mx0, 1); }   // le drap rabattu
      ctx.fillStyle = '#c9ccd2';                        // les ridelles, le long des flancs
      if (ouest) ctx.fillRect(x0, nord ? 8 : 0, 1, (sud ? T - 5 : T) - (nord ? 8 : 0));
      if (est) ctx.fillRect(x1 - 1, nord ? 8 : 0, 1, (sud ? T - 5 : T) - (nord ? 8 : 0));
      if (sud) {
        ctx.fillStyle = '#5f676f'; ctx.fillRect(x0, T - 4, x1 - x0, 2);   // le pied de lit
        ctx.fillStyle = '#2a2a2e'; ctx.fillRect(x0, T - 2, 2, 1); ctx.fillRect(x1 - 2, T - 2, 2, 1);   // les roulettes
      }
    },
    /* Le solute : la potence, le sac, la tubulure. ⚠️ Il se pose a l'OUEST du
       lit (`irq` dans les plans) et c'est pour ca que le sac pend du cote est
       et que le tube file vers le bord est de la tuile : il va au bras du
       malade, pas dans le mur. */
    'i': function (ctx, v, T) {
      ctx.fillStyle = 'rgba(0,0,0,0.18)';
      ctx.fillRect(3, 14, 9, 2);                        // l'ombre
      ctx.fillStyle = '#6f757c';
      ctx.fillRect(3, 14, 9, 1); ctx.fillRect(7, 12, 2, 3);   // le pied a roulettes
      ctx.fillStyle = '#aab1b8';
      ctx.fillRect(7, 1, 2, 12);                        // la potence
      ctx.fillRect(7, 1, 6, 1);                         // le crochet
      ctx.fillStyle = '#e4f3f6';
      ctx.fillRect(9, 2, 5, 6);                         // le sac
      ctx.fillStyle = (v >> 4) % 2 ? '#e9d77a' : '#a9dbe6';   // ce qui coule : du serum, ou du jaune
      ctx.fillRect(9, 4 + (v >> 5) % 2, 5, 4 - (v >> 5) % 2);
      ctx.fillStyle = 'rgba(255,255,255,0.7)';
      ctx.fillRect(10, 3, 1, 3);                        // le reflet du plastique
      ctx.fillStyle = '#dfe7ea';
      ctx.fillRect(11, 8, 1, 3); ctx.fillRect(11, 10, 5, 1);   // la tubulure, vers le lit
    },
    /* Le moniteur : un ecran sur son pied, et le TRACE qui dit qu'on est vivant.
       ⚠️ Le pic tombe ailleurs d'un ecran a l'autre (`v >> 4`) : six moniteurs
       qui battent au meme pixel ont l'air d'une seule image collee six fois. */
    'q': function (ctx, v, T) {
      ctx.fillStyle = 'rgba(0,0,0,0.20)';
      ctx.fillRect(3, 14, 11, 2);
      ctx.fillStyle = '#6f757c';
      ctx.fillRect(7, 10, 2, 4); ctx.fillRect(4, 14, 8, 1);   // le pied a roulettes
      ctx.fillStyle = '#c9ccd2';
      ctx.fillRect(1, 1, 14, 9);                        // le boitier
      ctx.fillStyle = '#9aa0a8';
      ctx.fillRect(1, 8, 14, 2);                        // sa face, et ses boutons
      ctx.fillStyle = '#0f1a14';
      ctx.fillRect(2, 2, 12, 6);                        // l'ecran
      const pic = 3 + (v >> 4) % 4 * 2;
      ctx.fillStyle = '#4fe38a';                        // le trace : plat, le pic, plat
      ctx.fillRect(2, 5, pic - 2, 1);
      ctx.fillRect(pic, 3, 1, 2); ctx.fillRect(pic + 1, 5, 1, 2); ctx.fillRect(pic + 2, 5, 11 - pic, 1);
      ctx.fillStyle = '#ffd23a';
      ctx.fillRect(12, 3, 1, 1);                        // le pouls, en chiffres
      ctx.fillStyle = '#ff6b5a';
      ctx.fillRect(3, 9, 1, 1);                         // le voyant
    },
    /* La distributrice d'une salle d'attente : la meme machine que dans la rue
       (`DECORS.distributrice_*`), vue de plus haut. La vitre, les rangees de
       sacs, la fente a monnaie, la trappe au pied. ⚠️ Un seul dessin pour les
       trois sortes : dedans, c'est le MENU qui dit ce qu'elle vend (la sorte est
       sur le point), et la vitre pleine de couleurs se lit « distributrice »
       avant de se lire « cafe » ou « chips ». */
    'b': function (ctx, v, T) {
      ctx.fillStyle = 'rgba(0,0,0,0.20)';
      ctx.fillRect(2, 14, 13, 2);                       // l'ombre au pied
      ctx.fillStyle = '#8a241e';
      ctx.fillRect(2, 0, 12, 15);                       // la caisse
      ctx.fillStyle = '#b8322a';
      ctx.fillRect(2, 0, 12, 10);                       // le dessus et le haut de la face
      ctx.fillStyle = '#1b2430';
      ctx.fillRect(3, 2, 7, 7);                         // la vitre
      const teintes = ['#f1c40f', '#3f7ab8', '#e8e6de', '#4f9e5a', '#c2762c'];
      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          ctx.fillStyle = teintes[(v + r * 2 + c) % teintes.length];
          ctx.fillRect(4 + c * 2, 3 + r * 2, 1, 1);
        }
      }
      ctx.fillStyle = 'rgba(255,255,255,0.30)';
      ctx.fillRect(3, 2, 1, 6);                         // le reflet de la vitre
      ctx.fillStyle = '#e8e6de';
      ctx.fillRect(11, 3, 2, 1); ctx.fillRect(11, 5, 2, 1);   // les boutons
      ctx.fillStyle = '#ffd23a';
      ctx.fillRect(12, 7, 1, 2);                        // la fente a monnaie
      ctx.fillStyle = '#5a1712';
      ctx.fillRect(2, 10, 12, 5);                       // la face
      ctx.fillStyle = '#1a0e0c';
      ctx.fillRect(4, 11, 7, 2);                        // la trappe
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

  //: Hauteurs, comptees depuis le HAUT de la tuile de facade.
  //:
  //: ⚠️ L'ENSEIGNE EST AU-DESSUS DU MUR, et c'est pour ca que son `y` est
  //: NEGATIF : le panneau monte sur la tuile de toit. Tant qu'il tenait dans
  //: les 16 px du mur, le nom, l'auvent et la vitre se partageaient UNE tuile —
  //: cinq pixels pour le nom, quatre pour l'auvent, trois pour la vitrine. Un
  //: commerce se reconnait de loin a son enseigne : c'est elle qui doit avoir
  //: la place, et vu d'en haut la hauteur va vers le NORD (c'est deja ce que
  //: dit le toit, peint au-dessus de son mur).
  //:
  //: ⚠️ Ca tient a un invariant de la carte : au-dessus d'une devanture, sur
  //: toute sa largeur, il y a du TOIT — jamais du trottoir. Un juge Python le
  //: verifie (`test_une_enseigne_a_du_toit_au-dessus_d_elle`) ; sans lui, une
  //: enseigne finirait un jour posee a plat sur une ruelle.
  const ENSEIGNE_Y = -12, ENSEIGNE_H = 12;
  //: Et le mur, degage, se partage entre l'auvent et la vitrine — qui triple.
  //: Les deux premiers pixels restent au mur : c'est le dessous du panneau.
  const AUVENT_Y = 2, AUVENT_H = 5;
  const VITRE_Y = 7, VITRE_H = 9;

  function eclaircir(couleur, dose) {
    const n = parseInt(couleur.slice(1), 16);
    const r = Math.min(255, ((n >> 16) & 255) + dose);
    const v = Math.min(255, ((n >> 8) & 255) + dose);
    const b = Math.min(255, (n & 255) + dose);
    return 'rgb(' + r + ',' + v + ',' + b + ')';
  }

  /** L'enseigne, le nom, l'auvent raye, la vitre et la pancarte.
      `d` = { x, y, l, genre, texte, pancarte, porte }, `g` = le genre. */
  function devanture(ctx, d, g, ox, oy) {
    const large = d.l * T;

    enseigne(ctx, d, g, ox, oy, large);

    // ⚠️ Sous l'enseigne, chaque tuile est ce que `motifs` dit qu'elle est.
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

  /** Le panneau du commerce, POSE SUR LE HAUT DU MUR et debordant sur le toit.

      ⚠️ Trois choses le decollent du toit, et il les faut toutes les trois :
      l'arete claire en haut (le jour vient du nord, comme pour l'ombre des
      murs), les joues sombres sur les cotes, et le DESSOUS pose sur le mur.
      Sans elles, un rectangle de couleur au ras d'un toit se lit comme une
      trappe peinte dessus. */
  function enseigne(ctx, d, g, ox, oy, large) {
    const y = oy + ENSEIGNE_Y;

    ctx.fillStyle = g.bandeau;
    ctx.fillRect(ox, y, large, ENSEIGNE_H);
    ctx.fillStyle = eclaircir(g.bandeau, 30);
    ctx.fillRect(ox, y, large, 1);
    ctx.fillStyle = 'rgba(0,0,0,0.22)';           // les joues du panneau
    ctx.fillRect(ox, y, 1, ENSEIGNE_H);
    ctx.fillRect(ox + large - 1, y, 1, ENSEIGNE_H);
    ctx.fillStyle = 'rgba(0,0,0,0.38)';
    ctx.fillRect(ox, y + ENSEIGNE_H - 1, large, 1);

    // Le nom, centre. ⚠️ Arrondi a l'entier : un texte pose sur un demi-pixel
    // est floute par le canvas, et a cinq pixels de haut il devient illisible.
    const larg = Atlas.largeurTexte(d.texte, 1);
    Atlas.texte(ctx, d.texte, Math.round(ox + (large - larg) / 2), y + 4, g.lettres, 1);

    // Le dessous du panneau, sur le mur : c'est ce qui dit qu'il est DEVANT.
    ctx.fillStyle = 'rgba(11,10,18,0.42)';
    ctx.fillRect(ox, oy, large, 1);
    ctx.fillStyle = 'rgba(11,10,18,0.20)';
    ctx.fillRect(ox, oy + 1, large, 1);
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
    // ⚠️ Le CLOCHER de la chapelle de l'ile : une tour d'ardoise vue d'en haut,
    // sa fleche en pointe de diamant et la croix. Sans lui, la chapelle est une
    // maison de plus avec un toit d'ardoise — c'est lui qu'on reconnait du quai.
    clocher: function (ctx, x, y) {
      ctx.fillStyle = 'rgba(11,10,18,0.4)'; ctx.fillRect(x + 5, y + 6, 11, 10);
      ctx.fillStyle = '#d8d2c4'; ctx.fillRect(x + 2, y + 3, 12, 11);        // la tour, blanchie a la chaux
      ctx.fillStyle = '#4a4f5c'; ctx.fillRect(x + 3, y + 4, 10, 9);          // la fleche d'ardoise
      ctx.fillStyle = '#626878'; ctx.fillRect(x + 3, y + 4, 5, 4); ctx.fillRect(x + 8, y + 9, 5, 4);
      ctx.fillStyle = '#2f333d'; ctx.fillRect(x + 7, y + 4, 2, 9); ctx.fillRect(x + 3, y + 8, 10, 1);
      ctx.fillStyle = '#e8c35a';                                            // la croix, doree
      ctx.fillRect(x + 7, y, 2, 8); ctx.fillRect(x + 5, y + 2, 6, 2);
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

  /* --- La fosse d'un arbre de rue ---------------------------------------

     ⚠️ Demande de Martin : « les arbres qui sont sur un trottoir doivent avoir
     un petit rond de terre à leur pied ». Un arbre planté dans le béton sans
     rien à son pied n'est pas planté, il est POSÉ — et c'est exactement ce
     qu'on voyait sur la place publique du Faubourg.

     ⚠️ C'est la BORDURE qui fait la fosse, pas la terre : sans le liseré de
     béton clair d'un pixel tout autour, le rond brun se lit comme une tache
     sur le trottoir. Un vrai carré d'arbre, c'est du trottoir qu'on a
     DÉCOUPÉ, et il faut voir la coupe. */

  //: Les demi-largeurs du rond, de haut en bas — un rond, pas un carré. La
  //: bordure prend une rangée de plus en haut et en bas.
  const FOSSE = [3, 5, 6, 6, 6, 5, 3];
  const BORDURE = [2, 4, 6, 7, 7, 7, 6, 4, 2];

  function fosseDArbre(ctx, x, y) {
    const haut = y - 5;
    ctx.fillStyle = '#8a8578';                       // la coupe dans le beton
    for (let i = 0; i < BORDURE.length; i++) ctx.fillRect(x - BORDURE[i], haut - 1 + i, BORDURE[i] * 2, 1);
    ctx.fillStyle = '#4f4030';                       // la terre
    for (let i = 0; i < FOSSE.length; i++) ctx.fillRect(x - FOSSE[i], haut + i, FOSSE[i] * 2, 1);
    ctx.fillStyle = '#5f4d3a';                       // remuee
    ctx.fillRect(x - 4, haut + 1, 3, 1); ctx.fillRect(x + 1, haut + 4, 3, 1);
    ctx.fillStyle = '#3d3125';
    ctx.fillRect(x - 1, haut + 3, 2, 1); ctx.fillRect(x + 2, haut + 1, 2, 1);
    ctx.fillStyle = '#4a7a3a';                       // ce qui pousse quand meme
    ctx.fillRect(x - 5, haut + 4, 1, 1); ctx.fillRect(x + 4, haut + 2, 1, 1);
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
           toiture: toiture, ombreDeMur: ombreDeMur, fosseDArbre: fosseDArbre,
           TOITURES: TOITURES, T: T };
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
     `pv: n`      ce qu'il faut lui mettre a l'ARME pour l'abattre : balles,
                  explosion, feu. Un char le couche d'un coup, une arme l'use.

   Un decor sans l'un ni l'autre reste ce qu'il etait : solide pour les gens,
   invisible pour les chars (les feux, les panneaux — on ne renverse pas la
   signalisation, sinon un croisement se demonte au premier virage rate).

   ⚠️ `casse` et `pv` vont ENSEMBLE, et `arrete` n'a jamais de `pv`. Ce qui
   tombe sous un char doit tomber sous une arme — sinon un lampadaire encaisse
   un chargeur entier sans bouger, ce qui a ete le cas jusqu'au 15 sept. 2026 :
   `Entites.briser` n'avait qu'un seul appelant, le char. Et l'inverse tient
   aussi : un arbre, une fontaine, un camion-restaurant ARRETENT — ils encaissent
   la balle, ils ne tombent jamais, sinon la rue se demonte au pistolet.
   `scripts/verifier_ce_qui_casse.py` tient les deux regles.

   ⚠️ L'echelle des `pv` se lit en balles de PISTOLET (30 points) : une poubelle
   part au premier coup, un lampadaire au deuxieme, un kiosque au troisieme. La
   fronde (10) et la mitraillette (9) usent, la carabine (60) couche. */
/** Le mat d'un feu, tout entier, « bras vers l'est » quand `vers` vaut 1 et
    par MIROIR quand il vaut -1. ⚠️ Un seul jeu de nombres pour les deux sens :
    `m()` retourne une abscisse et sa largeur d'un coup. */
function peindreFeu(ctx, w, vers) {
  const f = DECORS.feu;
  const m = function (x, l) { return vers > 0 ? x : w - x - l; };
  ctx.fillStyle = '#2c2c30';
  ctx.fillRect(m(f.boitier.x, f.boitier.l), f.boitier.y, f.boitier.l, f.boitier.h);
  const douilles = ['#3d1a16', '#3d3013', '#12331f'];        // rouge, jaune, vert eteints
  for (let i = 0; i < 3; i++) {
    ctx.fillStyle = douilles[i];
    ctx.fillRect(m(f.lentilles[i], f.lentilleCote), f.lentilleY, f.lentilleCote, f.lentilleCote);
  }
  // Le mat : il monte jusque SOUS le boitier, et son pied deborde d'un pixel
  // de chaque cote — sans ce pied, un poteau de trois pixels a l'air pose sur
  // rien.
  ctx.fillStyle = '#3a3d44';
  ctx.fillRect(m(f.mat.x, f.mat.l), f.boitier.y + 1, f.mat.l, 21);
  ctx.fillRect(m(f.mat.x - 1, f.mat.l + 2), 22, f.mat.l + 2, 2);
}

/* --- LES KIOSQUES DE LA FOIRE ---------------------------------------------
   ⚠️ **UN SEUL PEINTRE POUR TOUS, ET UN VENDEUR DERRIERE CHAQUE COMPTOIR.**
   Retour de Martin : « plein de kiosques, de vendeurs ». Le vendeur est PEINT
   dans le kiosque, pas pose comme une entite : trente vendeurs a trente entites
   mangeraient le budget d'images de toute la rue pour des gens qui ne bougent
   pas. `variantes` choisit son visage (peau, cheveux, chandail) a l'empreinte
   de la tuile — deux kiosques voisins n'ont pas le meme vendeur.

   Ce qui distingue un kiosque de l'autre tient en deux couleurs d'auvent et un
   PRODUIT sur le comptoir ; tout le reste — la boite, les poteaux, les festons,
   le vendeur — est ecrit une fois. */
const VENDEURS = {
  peau: ['#e8b088', '#c98d66', '#8d5a3b', '#f0c098'],
  cheveux: ['#3a2a1a', '#1a1a1a', '#8a5a2b', '#d9b36a'],
  chandail: ['#efe6d0', '#c0392b', '#2f6fb5', '#2f8d6a'],
};
function peindreKiosque(ctx, v, auvent, auvent2, produit) {
  const peau = VENDEURS.peau[v % 4], cheveux = VENDEURS.cheveux[(v >> 2) % 4];
  const chandail = VENDEURS.chandail[(v * 3 + 1) % 4];
  ctx.fillStyle = 'rgba(20,18,26,0.26)'; ctx.fillRect(2, 26, 25, 4);        // l'ombre
  // Le vendeur, DERRIERE le comptoir : on le peint avant la boite.
  ctx.fillStyle = chandail; ctx.fillRect(10, 13, 9, 5);
  ctx.fillStyle = peau; ctx.fillRect(11, 8, 6, 5);                           // la tete
  ctx.fillStyle = cheveux; ctx.fillRect(11, 7, 6, 2); ctx.fillRect(11, 9, 1, 2);
  ctx.fillStyle = '#1b1b1f'; ctx.fillRect(12, 10, 1, 1); ctx.fillRect(15, 10, 1, 1);
  ctx.fillStyle = peau; ctx.fillRect(8, 14, 2, 3); ctx.fillRect(19, 14, 2, 3);   // les bras sur le comptoir
  // La boite du comptoir, aux couleurs de l'auvent.
  ctx.fillStyle = auvent; ctx.fillRect(2, 17, 25, 10);
  ctx.fillStyle = 'rgba(0,0,0,0.22)'; ctx.fillRect(2, 23, 25, 4);
  ctx.fillStyle = auvent2;
  for (let x = 4; x < 26; x += 5) ctx.fillRect(x, 18, 2, 8);                 // les planches peintes
  ctx.fillStyle = '#b89060'; ctx.fillRect(1, 16, 27, 2);                     // le dessus du comptoir
  ctx.fillStyle = '#8a6a3f'; ctx.fillRect(1, 17, 27, 1);
  // Les deux poteaux et l'auvent raye, festonne.
  ctx.fillStyle = '#5a3f26'; ctx.fillRect(2, 5, 2, 12); ctx.fillRect(25, 5, 2, 12);
  for (let x = 0; x < 29; x++) {
    ctx.fillStyle = (Math.floor(x / 4) % 2) ? auvent2 : auvent;
    ctx.fillRect(x, 2, 1, 4);
    if (x % 4 !== 3) ctx.fillRect(x, 6, 1, 1);                               // le feston
  }
  ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fillRect(0, 5, 29, 1);
  if (produit) produit(ctx);
}

/* ⚠️ Un peintre MIROIR : le même dessin, retourné gauche-droite. Pas de
   `scale(-1, 1)` : on ne retourne que `fillRect`, et le banc — qui peint dans un
   faux contexte — voit exactement ce que peint le navigateur. */
function miroirX(ctx, w) {
  return {
    set fillStyle(c) { ctx.fillStyle = c; },
    get fillStyle() { return ctx.fillStyle; },
    fillRect: function (x, y, l, h) { ctx.fillRect(w - x - l, y, l, h); },
  };
}

//: ⚠️ LA BOULE FRAPPE POUR VRAI (2e vague des chantiers). Elle RECULE lentement,
//: part, cogne le mur et rebondit : seize poses, et la douzième (indice 11) est
//: le coup — `chantiers.js` y joue le son, la poussière et les éclats. Python la
//: pose à DEUX tuiles du mur (`chantiers.PORTEE_BOULE`) : au coup, le dernier
//: pixel de la boule touche le premier pixel de la tuile du mur, à 24 px du
//: centre de la machine. Un juge le mesure.
const BOULE = {
  angles: [0, -0.12, -0.26, -0.4, -0.52, -0.61, -0.66, -0.62, -0.5, -0.3, -0.06, 0.085, 0.02, -0.08, -0.04, 0.02],
  frappe: 11,
  pointe: [32, 6],     // le bout de la flèche, d'où pend le câble
  cable: 24,
};

function peindreGrueABoule(ctx, w, h, v) {
  const trait = function (x0, y0, x1, y1, e, c) {
    ctx.fillStyle = c;
    const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0), 1);
    for (let k = 0; k <= n; k++) {
      ctx.fillRect(Math.round(x0 + (x1 - x0) * k / n), Math.round(y0 + (y1 - y0) * k / n), e, e);
    }
  };
  ctx.fillStyle = 'rgba(20,18,26,0.28)'; ctx.fillRect(1, 49, 28, 5);
  ctx.fillStyle = '#2c2c30'; ctx.fillRect(1, 42, 26, 9);
  ctx.fillStyle = '#4a4d55'; for (let x = 2; x < 27; x += 3) ctx.fillRect(x, 43, 1, 7);
  ctx.fillStyle = '#b8332a'; ctx.fillRect(3, 32, 20, 11);
  ctx.fillStyle = '#d24a3a'; ctx.fillRect(3, 32, 20, 2);
  ctx.fillStyle = '#243447'; ctx.fillRect(5, 34, 6, 5);
  // La flèche en treillis : deux longerons et des diagonales, jusqu'au bout
  // d'où pend le câble.
  const piedX = 16, piedY = 34, boutX = BOULE.pointe[0], boutY = BOULE.pointe[1];
  trait(piedX, piedY, boutX, boutY, 2, '#d2a126');
  trait(piedX + 3, piedY + 1, boutX + 2, boutY + 1, 1, '#a87c16');
  for (let k = 1; k < 6; k++) {
    const x = piedX + (boutX - piedX) * k / 6, y = piedY + (boutY - piedY) * k / 6;
    trait(Math.round(x), Math.round(y), Math.round(x + 3), Math.round(y + 1), 1, '#a87c16');
  }
  const angle = BOULE.angles[v % BOULE.angles.length];
  const bx = Math.round(boutX + Math.sin(angle) * BOULE.cable), by = Math.round(boutY + Math.cos(angle) * BOULE.cable);
  trait(boutX, boutY, bx, by, 1, '#3a3d44');
  ctx.fillStyle = '#2c2c30'; ctx.fillRect(bx - 3, by - 2, 7, 6); ctx.fillRect(bx - 2, by - 3, 5, 8);
  ctx.fillStyle = '#5f6267'; ctx.fillRect(bx - 1, by - 2, 2, 2);
}

/** L'abribus, dans l'un de ses quatre sens : `sud` (ouvert vers nous), `nord`
    (vu de dos), `est` et `ouest` (de profil, le long d'une avenue).

    ⚠️ La lumiere vient du nord-ouest, comme partout : la vitre prend son reflet
    en haut a gauche, et l'ombre de l'abri tombe au sud-est. */
function peindreAbribus(ctx, sens) {
  const cadre = '#2f3238', vitre = '#8fb4c8', reflet = '#c9e2ee', toit = '#3a3d44', arete = '#5b606a';
  const reclame = '#e8b33c', poteau = '#9aa0a8', plaque = '#f4f1e6', picto = '#2471a3', bois = '#6b4b2c';
  const poteauDArret = function (x, y) {
    ctx.fillStyle = poteau; ctx.fillRect(x, y + 5, 1, 18);
    ctx.fillStyle = plaque; ctx.fillRect(x - 2, y, 5, 6);
    ctx.fillStyle = picto; ctx.fillRect(x - 1, y + 1, 3, 3);
    ctx.fillStyle = plaque; ctx.fillRect(x, y + 2, 1, 1);
  };
  if (sens === 'sud' || sens === 'nord') {
    ctx.fillStyle = 'rgba(20,18,26,0.25)'; ctx.fillRect(3, 22, 22, 4);        // l'ombre
    if (sens === 'sud') {
      ctx.fillStyle = cadre; ctx.fillRect(1, 8, 22, 12);                     // le fond, derriere
      ctx.fillStyle = vitre; ctx.fillRect(2, 9, 13, 10);
      ctx.fillStyle = reflet; ctx.fillRect(2, 9, 5, 1); ctx.fillRect(2, 9, 1, 5);
      ctx.fillStyle = reclame; ctx.fillRect(16, 9, 6, 10);                   // la reclame lumineuse
      ctx.fillStyle = '#b8862a'; ctx.fillRect(17, 11, 4, 1); ctx.fillRect(17, 14, 3, 1);
      ctx.fillStyle = bois; ctx.fillRect(3, 16, 12, 2);                      // le banc sous l'abri
      ctx.fillStyle = cadre; ctx.fillRect(1, 8, 1, 15); ctx.fillRect(22, 8, 1, 15);   // les montants
      ctx.fillStyle = vitre; ctx.fillRect(2, 20, 2, 3);                      // le bout des vitres de cote
    } else {
      ctx.fillStyle = bois; ctx.fillRect(3, 10, 12, 2);                      // le banc, derriere la vitre
      ctx.fillStyle = cadre; ctx.fillRect(1, 8, 22, 15);
      ctx.fillStyle = vitre; ctx.fillRect(2, 12, 20, 10);                    // la vitre du fond, devant nous
      ctx.fillStyle = reflet; ctx.fillRect(2, 12, 7, 1); ctx.fillRect(2, 12, 1, 4);
      ctx.fillStyle = reclame; ctx.fillRect(15, 13, 6, 8);
      ctx.fillStyle = '#b8862a'; ctx.fillRect(16, 15, 4, 1);
      ctx.fillStyle = vitre; ctx.fillRect(2, 9, 19, 2);                      // on devine l'interieur
    }
    ctx.fillStyle = toit; ctx.fillRect(0, 5, 24, 4);                         // le toit
    ctx.fillStyle = arete; ctx.fillRect(0, 5, 24, 1);
    poteauDArret(24, 0);
    return;
  }
  // De profil : l'abri court du nord au sud, la vitre du fond du cote du mur.
  const mur = sens === 'est' ? 1 : 10;
  ctx.fillStyle = 'rgba(20,18,26,0.25)'; ctx.fillRect(4, 28, 10, 4);
  ctx.fillStyle = cadre; ctx.fillRect(mur, 8, 4, 20);
  ctx.fillStyle = vitre; ctx.fillRect(mur + 1, 9, 2, 18);                    // la vitre du fond, par la tranche
  ctx.fillStyle = reflet; ctx.fillRect(mur + 1, 9, 1, 6);
  ctx.fillStyle = bois; ctx.fillRect(sens === 'est' ? 6 : 6, 13, 3, 10);     // le banc
  ctx.fillStyle = vitre; ctx.fillRect(2, 8, 12, 1); ctx.fillRect(2, 27, 12, 1);   // les vitres des bouts
  ctx.fillStyle = reclame; ctx.fillRect(sens === 'est' ? 2 : 10, 20, 4, 7);
  ctx.fillStyle = toit; ctx.fillRect(1, 5, 14, 22);                          // le toit, vu d'en haut
  ctx.fillStyle = arete; ctx.fillRect(1, 5, 14, 1); ctx.fillRect(1, 5, 1, 22);
  ctx.fillStyle = '#4a4d55'; ctx.fillRect(3, 8, 10, 16);
  poteauDArret(sens === 'est' ? 13 : 2, 7);
}

/** L'edicule du metro, ouvert vers la rue au sud (`sud`) ou vu de dos (`nord`).

    ⚠️ La lumiere vient du nord-ouest, comme partout : reflet de la vitre en haut
    a gauche, ombre au sud-est. Le « M » est a la couleur de la ligne (jaune). */
function peindreEdicule(ctx, sens) {
  const cadre = '#2b2e35', vitre = '#8fb4c8', reflet = '#cfe6f0', toit = '#3d424b', arete = '#646a75';
  const marche = '#8d8f93', ombreMarche = '#55575c', jaune = '#f1c40f', plaque = '#1b1d22';
  ctx.fillStyle = 'rgba(20,18,26,0.28)'; ctx.fillRect(4, 25, 20, 5);            // l'ombre
  if (sens === 'sud') {
    ctx.fillStyle = cadre; ctx.fillRect(2, 11, 18, 14);                        // le pavillon
    ctx.fillStyle = vitre; ctx.fillRect(3, 12, 3, 11); ctx.fillRect(16, 12, 3, 11);   // les vitres de cote
    ctx.fillStyle = reflet; ctx.fillRect(3, 12, 1, 5);
    ctx.fillStyle = '#15161a'; ctx.fillRect(6, 12, 10, 13);                    // la bouche, qui descend
    for (let k = 0; k < 5; k++) {                                              // les marches, de plus en plus sombres
      ctx.fillStyle = k % 2 ? ombreMarche : marche;
      ctx.fillRect(7, 23 - k * 2, 8, 1);
    }
    ctx.fillStyle = '#9aa0a8'; ctx.fillRect(6, 13, 1, 12); ctx.fillRect(15, 13, 1, 12);   // les rampes
  } else {
    ctx.fillStyle = cadre; ctx.fillRect(2, 11, 18, 14);
    ctx.fillStyle = vitre; ctx.fillRect(3, 13, 16, 11);                        // la vitre du fond, devant nous
    ctx.fillStyle = reflet; ctx.fillRect(3, 13, 6, 1); ctx.fillRect(3, 13, 1, 5);
    ctx.fillStyle = '#4a5560'; ctx.fillRect(7, 15, 8, 7);                      // l'escalier qu'on devine derriere
    ctx.fillStyle = cadre; ctx.fillRect(10, 13, 1, 11);
  }
  ctx.fillStyle = toit; ctx.fillRect(0, 8, 22, 4);                             // le toit en auvent
  ctx.fillStyle = arete; ctx.fillRect(0, 8, 22, 1);
  // Le poteau et sa plaque « M », au coin nord-est.
  ctx.fillStyle = '#9aa0a8'; ctx.fillRect(21, 6, 1, 19);
  ctx.fillStyle = plaque; ctx.fillRect(18, 0, 7, 7);
  ctx.fillStyle = jaune; ctx.fillRect(19, 1, 5, 5);
  ctx.fillStyle = plaque;                                                      // le « M »
  ctx.fillRect(20, 2, 1, 3); ctx.fillRect(22, 2, 1, 3); ctx.fillRect(21, 3, 1, 1);
}

/** Un ovale plein, rangee par rangee : le plancher d'un manège vu de trois
    quarts. `cx` entier : l'ovale fait `2 * rx + 1` pixels de large. */
function ovaleDeManege(ctx, cx, cy, rx, ry) {
  for (let dy = -ry; dy <= ry; dy++) {
    const demi = Math.round(rx * Math.sqrt(Math.max(0, 1 - (dy / ry) * (dy / ry))));
    ctx.fillRect(cx - demi, cy + dy, demi * 2 + 1, 1);
  }
}

const DECORS = {
  arbre: { arrete: 2.0, w: 18, h: 26, ancre: [9, 25], r: 5, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#5a3a1a'; ctx.fillRect(8, 16, 3, 9);
    ctx.fillStyle = '#2f6b2a'; ctx.fillRect(2, 4, 14, 13); ctx.fillRect(5, 1, 8, 3); ctx.fillRect(0, 7, 18, 7);
    ctx.fillStyle = '#3f8d38'; ctx.fillRect(4, 3, 6, 5); ctx.fillRect(2, 9, 5, 4);
    ctx.fillStyle = '#204d1e'; ctx.fillRect(10, 10, 6, 6); ctx.fillRect(6, 14, 8, 3);
  } },
  lampadaire: { casse: 0.7, pv: 60, w: 8, h: 30, ancre: [3, 29], r: 2, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(2, 4, 2, 26); ctx.fillRect(0, 28, 6, 2);
    ctx.fillStyle = '#4a4d55'; ctx.fillRect(2, 2, 6, 2);
    ctx.fillStyle = '#ffe9a8'; ctx.fillRect(6, 3, 2, 3);
  } },
  // ⚠️ ROUGE, et c'est la couleur qu'on attend d'une borne-fontaine — elle
  // etait jaune, et une tache jaune au coin d'une rue se lit comme une borne
  // de stationnement ou un poteau de chantier, pas comme de l'eau. Deux
  // bouchons lateraux, un chapeau, une bande claire : a douze pixels, c'est la
  // SILHOUETTE qui la nomme, la couleur ne fait que la confirmer.
  //
  // ⚠️ `casse` : elle CEDE sous un char lance, et c'est tout l'interet — une
  // borne qu'on ne peut pas defoncer n'est qu'une tache de peinture.
  // ⚠️ `pv: 40`, moins qu'un lampadaire (60), et c'est la VRAIE borne qui le
  // dit : elle est boulonnee sur des vis qui CASSENT expres, pour qu'un char
  // l'arrache au lieu de se plier autour. Elle cede plus vite que le poteau
  // d'a cote, c'est fait pour.
  borne_fontaine: { casse: 0.75, pv: 40, w: 10, h: 14, ancre: [5, 13], r: 4, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#8e1f16'; ctx.fillRect(3, 2, 4, 11);                 // le corps, dans l'ombre
    ctx.fillStyle = '#c0392b'; ctx.fillRect(3, 2, 3, 11);                 // sa face eclairee du nord-ouest
    ctx.fillStyle = '#8e1f16'; ctx.fillRect(1, 5, 2, 3); ctx.fillRect(7, 5, 2, 3);   // les deux bouchons
    ctx.fillStyle = '#c0392b'; ctx.fillRect(2, 0, 6, 2);                  // le chapeau
    ctx.fillStyle = '#e8e6de'; ctx.fillRect(3, 9, 4, 1);                  // la bande claire
    ctx.fillStyle = '#5c1410'; ctx.fillRect(3, 13, 4, 1);                 // le pied
  } },
  // ⚠️ UN GUICHET EST UNE CAISSE DE BANQUE POSEE DANS LA RUE : gris acier,
  // un ecran qui luit, le clavier, la fente des billets, le lisere de la
  // banque. `lourd: 2.5` — il ne cede qu'a un camion ou un autobus, une
  // berline s'y arrete (`Vehicules.decorDevant`) ; `pv: 240`, huit balles de
  // pistolet : blinde, pas eternel, et un char qui explose a cote l'ouvre
  // aussi. Ce qu'il fait en cedant est dans `Missions.guichetCasse`.
  guichet: { casse: 0.5, pv: 240, lourd: 2.5, w: 14, h: 20, ancre: [7, 19], r: 5, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#5e626a'; ctx.fillRect(1, 2, 12, 18);                 // la caisse, dans l'ombre
    ctx.fillStyle = '#8b8f96'; ctx.fillRect(1, 2, 11, 17);                 // sa face eclairee du nord-ouest
    ctx.fillStyle = '#a6aab0'; ctx.fillRect(1, 1, 12, 2);                  // le chapeau
    ctx.fillStyle = '#1b2a3a'; ctx.fillRect(3, 4, 8, 5);                   // l'ecran
    ctx.fillStyle = '#4fe38a'; ctx.fillRect(4, 5, 5, 1); ctx.fillRect(4, 7, 3, 1);   // ce qu'il affiche
    ctx.fillStyle = '#d9dbdf';                                             // le clavier
    for (let i = 0; i < 3; i++) for (let k = 0; k < 3; k++) ctx.fillRect(3 + i * 3, 11 + k * 2, 2, 1);
    ctx.fillStyle = '#2a2a2e'; ctx.fillRect(3, 17, 8, 1);                  // la fente des billets
    ctx.fillStyle = '#2f6fb5'; ctx.fillRect(11, 4, 1, 12);                 // le lisere de la banque
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(1, 19, 12, 1);                 // le pied
  } },
  // ⚠️ LES MACHINES DISTRIBUTRICES : la petite soeur du guichet, et elle se
  // lit pareil — une caisse haute plantee contre une devanture. Trois sortes,
  // trois couleurs qui se reconnaissent de l'autre bord de la rue : le ROUGE
  // de la liqueur (le logo, la canette peinte), la VITRE pleine de sacs des
  // grignotines, le BRUN de la machine a cafe et son gobelet dans la niche.
  // `distributrice` porte la sorte : c'est elle que lit `Missions` pour savoir
  // quoi vendre (`magasins.DISTRIBUTRICES`), et ce qu'elle crache en cedant.
  // `casse: 0.55` sans `lourd` — une berline la couche ; `pv: 80`, trois
  // balles de pistolet : de la tole et une vitre, pas un blindage.
  distributrice_liqueur: { casse: 0.55, pv: 80, w: 14, h: 22, ancre: [7, 21], r: 5, solide: true, distributrice: 'liqueur',
    peindre: function (ctx, w, h) {
      ctx.fillStyle = '#8a241e'; ctx.fillRect(1, 2, 12, 20);                 // la caisse, dans l'ombre
      ctx.fillStyle = '#b8322a'; ctx.fillRect(1, 2, 11, 19);                 // sa face eclairee du nord-ouest
      ctx.fillStyle = '#d9574a'; ctx.fillRect(1, 1, 12, 2);                  // le chapeau
      ctx.fillStyle = '#f3efe6'; ctx.fillRect(2, 4, 8, 2); ctx.fillRect(2, 7, 8, 1);   // le logo, en bandes
      ctx.fillStyle = '#f3efe6'; ctx.fillRect(4, 10, 4, 6);                  // la canette peinte
      ctx.fillStyle = '#b8322a'; ctx.fillRect(4, 12, 4, 2);
      ctx.fillStyle = '#c9ccd2'; ctx.fillRect(4, 10, 4, 1);                  // son couvercle
      ctx.fillStyle = '#e8e6de';                                             // les boutons de selection
      for (let k = 0; k < 5; k++) ctx.fillRect(10, 4 + k * 2, 1, 1);
      ctx.fillStyle = '#ffd23a'; ctx.fillRect(10, 15, 1, 2);                 // la fente a monnaie
      ctx.fillStyle = '#2a1a18'; ctx.fillRect(2, 18, 8, 2);                  // la trappe ou tombe la canette
      ctx.fillStyle = '#3a1410'; ctx.fillRect(1, 21, 12, 1);                 // le pied
    } },
  distributrice_grignotines: { casse: 0.55, pv: 80, w: 14, h: 22, ancre: [7, 21], r: 5, solide: true, distributrice: 'grignotines',
    peindre: function (ctx, w, h) {
      ctx.fillStyle = '#2c3845'; ctx.fillRect(1, 2, 12, 20);                 // la caisse, dans l'ombre
      ctx.fillStyle = '#3b4a5a'; ctx.fillRect(1, 2, 11, 19);                 // sa face eclairee
      ctx.fillStyle = '#56687a'; ctx.fillRect(1, 1, 12, 2);                  // le chapeau
      ctx.fillStyle = '#1b2430'; ctx.fillRect(2, 4, 7, 13);                  // la vitre
      const sacs = ['#f1c40f', '#c0392b', '#3f7ab8', '#4f9e5a', '#e67e22', '#8f5fb0'];
      for (let r = 0; r < 4; r++) {                                          // quatre spirales, trois sacs chacune
        for (let c = 0; c < 3; c++) {
          ctx.fillStyle = sacs[(r * 2 + c) % sacs.length];
          ctx.fillRect(3 + c * 2, 5 + r * 3, 1, 2);
        }
        ctx.fillStyle = '#56687a'; ctx.fillRect(2, 7 + r * 3, 7, 1);         // la tablette
      }
      ctx.fillStyle = 'rgba(255,255,255,0.25)'; ctx.fillRect(2, 4, 1, 12);   // le reflet de la vitre
      ctx.fillStyle = '#c9ccd2';                                             // le clavier
      for (let k = 0; k < 3; k++) ctx.fillRect(10, 5 + k * 2, 1, 1);
      ctx.fillStyle = '#ffd23a'; ctx.fillRect(10, 13, 1, 2);                 // la fente a monnaie
      ctx.fillStyle = '#0f141a'; ctx.fillRect(2, 18, 8, 2);                  // la trappe
      ctx.fillStyle = '#1f2830'; ctx.fillRect(1, 21, 12, 1);                 // le pied
    } },
  distributrice_cafe: { casse: 0.55, pv: 80, w: 14, h: 22, ancre: [7, 21], r: 5, solide: true, distributrice: 'cafe',
    peindre: function (ctx, w, h) {
      ctx.fillStyle = '#4f3620'; ctx.fillRect(1, 2, 12, 20);                 // la caisse, dans l'ombre
      ctx.fillStyle = '#6b4a2e'; ctx.fillRect(1, 2, 11, 19);                 // sa face eclairee
      ctx.fillStyle = '#8a6440'; ctx.fillRect(1, 1, 12, 2);                  // le chapeau
      ctx.fillStyle = '#e9dcc0'; ctx.fillRect(2, 4, 8, 6);                   // l'affiche eclairee
      ctx.fillStyle = '#6b4a2e'; ctx.fillRect(4, 7, 4, 3); ctx.fillRect(8, 8, 1, 1);   // la tasse, et son anse
      ctx.fillStyle = '#b39a7a'; ctx.fillRect(5, 5, 1, 1); ctx.fillRect(6, 4, 1, 2);   // la vapeur
      ctx.fillStyle = '#1a120c'; ctx.fillRect(3, 12, 6, 6);                  // la niche du gobelet
      ctx.fillStyle = '#f3efe6'; ctx.fillRect(5, 15, 2, 3);                  // le gobelet
      ctx.fillStyle = '#ffd23a'; ctx.fillRect(10, 5, 1, 1); ctx.fillRect(10, 7, 1, 1);   // les boutons
      ctx.fillStyle = '#c9ccd2'; ctx.fillRect(10, 13, 1, 2);                 // la fente a monnaie
      ctx.fillStyle = '#35240f'; ctx.fillRect(1, 21, 12, 1);                 // le pied
    } },
  // La cale du Norvegien : trois caisses empilees sous un bout de bache
  // bleue, une corde autour. Un comptoir de contrebande n'a pas d'enseigne —
  // c'est la bache qui le nomme. Il ARRETE, comme les kiosques.
  cale: { arrete: 9, w: 22, h: 18, ancre: [11, 17], r: 9, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#6e5330'; ctx.fillRect(1, 8, 20, 10);                 // les deux caisses du bas, dans l'ombre
    ctx.fillStyle = '#8a6a3f'; ctx.fillRect(1, 8, 9, 9); ctx.fillRect(12, 8, 9, 9);
    ctx.fillStyle = '#a07c4b'; ctx.fillRect(2, 9, 7, 3); ctx.fillRect(13, 9, 7, 3);
    ctx.fillStyle = '#6e5330'; ctx.fillRect(5, 8, 1, 9); ctx.fillRect(16, 8, 1, 9);   // les planches
    ctx.fillStyle = '#8a6a3f'; ctx.fillRect(6, 1, 10, 8);                  // celle du dessus
    ctx.fillStyle = '#a07c4b'; ctx.fillRect(7, 2, 8, 3);
    ctx.fillStyle = '#2f5f8a'; ctx.fillRect(4, 0, 9, 4); ctx.fillRect(2, 2, 5, 5);    // la bache
    ctx.fillStyle = '#3f78ad'; ctx.fillRect(5, 1, 6, 1);
    ctx.fillStyle = '#d9c9a0'; ctx.fillRect(1, 12, 20, 1);                 // la corde
    ctx.fillStyle = '#4a3a28'; ctx.fillRect(1, 17, 20, 1);                 // le pied
  } },
  // Le BAC ROULANT des éboueurs (M12) : vert, sa poignée et ses deux roues du côté
  // de la rue. Sorti le matin de la collecte, levé par le bras du camion — c'est le
  // navigateur qui le fait naître et rentrer (`Autobus`, la tournée).
  bac: { casse: 0.8, pv: 20, w: 10, h: 14, ancre: [5, 13], r: 4, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.25)'; ctx.fillRect(1, 11, 9, 3);
    ctx.fillStyle = '#23572e'; ctx.fillRect(1, 3, 8, 9);
    ctx.fillStyle = '#2e7d3c'; ctx.fillRect(2, 4, 6, 7);
    ctx.fillStyle = '#1b4323'; ctx.fillRect(0, 1, 10, 3);
    ctx.fillStyle = '#3a9a4b'; ctx.fillRect(1, 1, 8, 1);
    ctx.fillStyle = '#16181c'; ctx.fillRect(1, 11, 2, 3); ctx.fillRect(7, 11, 2, 3);
    ctx.fillStyle = '#9aa0a6'; ctx.fillRect(3, 6, 4, 1);
  } },
  poubelle: { casse: 0.85, pv: 25, w: 10, h: 14, ancre: [5, 13], r: 4, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#3f4a3c'; ctx.fillRect(1, 3, 8, 11);
    ctx.fillStyle = '#4c5a48'; ctx.fillRect(2, 4, 6, 9);
    ctx.fillStyle = '#2b332a'; ctx.fillRect(0, 1, 10, 3); ctx.fillRect(4, 5, 1, 8);
  } },
  // --- LA FOIRE DE LA POINTE -----------------------------------------------
  //: ⚠️ **DU DECOR ANIME, ET ON N'Y MONTE PAS.** Un manège où l'on monte et qui
  //: ne donne rien est un decor cher ; un manège qui tourne avec du monde dessus
  //: est une ville qui vit. C'est l'etage 1 des machines de chantier, mot pour
  //: mot : une articulation, pas dix — un socle cuit une fois, des nacelles
  //: peintes par-dessus a chaque image (`variantes` sert de POSE, comme pour les
  //: betes).

  // --- LES NEUF KIOSQUES DE LA FOIRE (voir `peindreKiosque`) ---------------
  barbe_a_papa: { arrete: 8, variantes: 16, w: 29, h: 30, ancre: [14, 27], r: 10, sol: [11, 5], solide: true, peindre: function (ctx, w, h, v) {
    peindreKiosque(ctx, v, '#e87aa8', '#fbe3ee', function (c) {
      for (const [x, y] of [[4, 11], [22, 10], [7, 12]]) {                     // les nuages roses sur leur baton
        c.fillStyle = '#f7a8cc'; c.fillRect(x - 2, y - 2, 5, 4); c.fillRect(x - 1, y - 3, 3, 1);
        c.fillStyle = '#fcd2e4'; c.fillRect(x - 1, y - 2, 2, 2);
        c.fillStyle = '#efe6d0'; c.fillRect(x, y + 2, 1, 3);
      }
    });
  } },
  hot_dogs: { arrete: 8, variantes: 16, w: 29, h: 30, ancre: [14, 27], r: 10, sol: [11, 5], solide: true, peindre: function (ctx, w, h, v) {
    peindreKiosque(ctx, v, '#c0392b', '#efd06a', function (c) {
      c.fillStyle = '#d9a35a'; c.fillRect(9, 0, 11, 3);                         // l'enseigne : un pain...
      c.fillStyle = '#b8452e'; c.fillRect(8, 1, 13, 1);                         // ...et sa saucisse
      c.fillStyle = '#efd06a'; c.fillRect(11, 1, 7, 1);                         // la moutarde
      c.fillStyle = '#d9a35a'; c.fillRect(3, 14, 5, 2); c.fillRect(21, 14, 5, 2);
      c.fillStyle = '#b8452e'; c.fillRect(3, 14, 5, 1); c.fillRect(21, 14, 5, 1);
    });
  } },
  pop_corn: { arrete: 8, variantes: 16, w: 29, h: 30, ancre: [14, 27], r: 10, sol: [11, 5], solide: true, peindre: function (ctx, w, h, v) {
    peindreKiosque(ctx, v, '#c0392b', '#ffffff', function (c) {
      for (const x of [3, 21]) {                                               // les boites rayees
        c.fillStyle = '#ffffff'; c.fillRect(x, 11, 5, 5);
        c.fillStyle = '#c0392b'; c.fillRect(x + 1, 11, 1, 5); c.fillRect(x + 3, 11, 1, 5);
        c.fillStyle = '#fff6c8'; c.fillRect(x - 1, 9, 7, 2); c.fillRect(x, 8, 5, 1);   // le mais qui deborde
        c.fillStyle = '#efd06a'; c.fillRect(x + 1, 9, 1, 1); c.fillRect(x + 4, 10, 1, 1);
      }
    });
  } },
  limonade: { arrete: 8, variantes: 16, w: 29, h: 30, ancre: [14, 27], r: 10, sol: [11, 5], solide: true, peindre: function (ctx, w, h, v) {
    peindreKiosque(ctx, v, '#efd06a', '#ffffff', function (c) {
      c.fillStyle = '#cfe6f5'; c.fillRect(3, 9, 5, 7);                          // le pichet
      c.fillStyle = '#f6e27a'; c.fillRect(3, 11, 5, 5);
      c.fillStyle = '#cfe6f5'; c.fillRect(8, 11, 1, 3);
      for (const x of [21, 24]) {                                              // les verres
        c.fillStyle = '#f6e27a'; c.fillRect(x, 12, 2, 4);
        c.fillStyle = '#5fb87a'; c.fillRect(x + 1, 10, 1, 2);
      }
    });
  } },
  poutine: { arrete: 8, variantes: 16, w: 29, h: 30, ancre: [14, 27], r: 10, sol: [11, 5], solide: true, peindre: function (ctx, w, h, v) {
    // ⚠️ Bleu et blanc : c'est une foire au Quebec, et la poutine est son drapeau.
    peindreKiosque(ctx, v, '#2f6fb5', '#ffffff', function (c) {
      for (const x of [3, 21]) {
        c.fillStyle = '#efe6d0'; c.fillRect(x, 13, 6, 3);                       // le casseau
        c.fillStyle = '#e8c56a'; c.fillRect(x, 11, 6, 2);                       // les frites
        c.fillStyle = '#7a4a26'; c.fillRect(x + 1, 11, 4, 1);                   // la sauce
        c.fillStyle = '#fff6e0'; c.fillRect(x + 1, 12, 1, 1); c.fillRect(x + 4, 12, 1, 1);   // le fromage en grains
      }
      c.fillStyle = '#ffffff'; c.fillRect(10, 0, 9, 2);                         // la fleur de lys, simplifiee
      c.fillStyle = '#2f6fb5'; c.fillRect(14, 0, 1, 2);
    });
  } },
  queues_de_castor: { arrete: 8, variantes: 16, w: 29, h: 30, ancre: [14, 27], r: 10, sol: [11, 5], solide: true, peindre: function (ctx, w, h, v) {
    peindreKiosque(ctx, v, '#8a5a2b', '#efe6d0', function (c) {
      for (const x of [2, 21]) {                                               // la pate aplatie, sucree
        c.fillStyle = '#b87a3a'; c.fillRect(x, 12, 7, 4); c.fillRect(x + 1, 11, 5, 1);
        c.fillStyle = '#d9a35a'; c.fillRect(x + 1, 12, 5, 2);
        c.fillStyle = '#7a4a26'; c.fillRect(x + 2, 13, 1, 1); c.fillRect(x + 4, 12, 1, 1);
      }
    });
  } },
  ballons: { arrete: 8, variantes: 16, w: 29, h: 30, ancre: [14, 27], r: 10, sol: [11, 5], solide: true, peindre: function (ctx, w, h, v) {
    peindreKiosque(ctx, v, '#9b59b6', '#efd06a', function (c) {
      // Les ballons flottent PAR-DESSUS l'auvent : c'est eux qu'on voit de loin.
      const couleurs = ['#e0574f', '#4fa3d1', '#efd06a', '#5fb87a', '#e87aa8', '#f39c12'];
      [[2, 0], [7, 1], [21, 0], [25, 2], [11, 0], [17, 1]].forEach(function (p, i) {
        c.fillStyle = couleurs[i]; c.fillRect(p[0], p[1], 3, 4);
        c.fillStyle = 'rgba(255,255,255,0.5)'; c.fillRect(p[0], p[1], 1, 1);
        c.fillStyle = '#efe6d0'; c.fillRect(p[0] + 1, p[1] + 4, 1, 3);
      });
    });
  } },
  peluches: { arrete: 8, variantes: 16, w: 29, h: 30, ancre: [14, 27], r: 10, sol: [11, 5], solide: true, peindre: function (ctx, w, h, v) {
    peindreKiosque(ctx, v, '#8e44ad', '#f1c40f', function (c) {
      // Les toutous accroches sous l'auvent : les prix qu'on ne gagne jamais.
      [[2, '#e87aa8'], [6, '#4fa3d1'], [21, '#5fb87a'], [25, '#f39c12']].forEach(function (p) {
        c.fillStyle = p[1]; c.fillRect(p[0], 8, 3, 3); c.fillRect(p[0] - 1, 7, 1, 1); c.fillRect(p[0] + 3, 7, 1, 1);
        c.fillStyle = '#1b1b1f'; c.fillRect(p[0], 9, 1, 1); c.fillRect(p[0] + 2, 9, 1, 1);
        c.fillStyle = p[1]; c.fillRect(p[0], 11, 3, 3);
      });
    });
  } },
  lance_anneaux: { arrete: 8, variantes: 16, w: 29, h: 30, ancre: [14, 27], r: 10, sol: [11, 5], solide: true, peindre: function (ctx, w, h, v) {
    peindreKiosque(ctx, v, '#2f8d6a', '#ffffff', function (c) {
      for (let i = 0; i < 6; i++) {                                            // les bouteilles
        const x = i < 3 ? 2 + i * 2 : 20 + (i - 3) * 2;
        c.fillStyle = '#2f6b2a'; c.fillRect(x, 11, 1, 5); c.fillRect(x, 10, 1, 1);
      }
      c.fillStyle = '#e8a33a'; c.fillRect(1, 9, 4, 1); c.fillRect(21, 9, 4, 1);   // les anneaux lances
    });
  } },

  // L'ARCHE DE LA FOIRE — Martin : « une entree avec une arche ». ⚠️ Elle est a
  // CHEVAL sur l'ouverture de la palissade : ses deux piliers se posent sur les
  // tuiles de cloture de part et d'autre, et l'arc passe au-dessus de l'allee
  // d'entree. Pas solide : c'est la barriere de l'arche (`carte.BARRIERES`,
  // `payer`) qui arrete — et laisse passer qui a son billet.
  portique_foire: { solide: false, r: 0, variantes: 2, anime: 18, w: 72, h: 66, ancre: [36, 62], peindre: function (ctx, w, h, v) {
    ctx.fillStyle = 'rgba(20,18,26,0.24)'; ctx.fillRect(2, 60, 20, 5); ctx.fillRect(50, 60, 20, 5);
    // Les deux piliers, rayes rouge et blanc, coiffes d'or.
    for (const px of [4, 56]) {
      ctx.fillStyle = '#8e1f16'; ctx.fillRect(px, 22, 12, 40);
      for (let y = 22; y < 62; y += 8) { ctx.fillStyle = '#c0392b'; ctx.fillRect(px, y, 11, 4); ctx.fillStyle = '#efe6d0'; ctx.fillRect(px, y + 4, 11, 4); }
      ctx.fillStyle = '#e8a33a'; ctx.fillRect(px - 2, 18, 16, 5);
      ctx.fillStyle = '#c08a20'; ctx.fillRect(px - 2, 22, 16, 1);
      ctx.fillStyle = '#5e4a2a'; ctx.fillRect(px - 1, 60, 14, 3);
    }
    // L'arc : une demi-couronne epaisse, bleue, bordee d'ampoules.
    const cx = 36, cy = 30, R = 30;
    for (let a = 0; a <= 180; a += 1) {
      const t = Math.PI + a / 180 * Math.PI;
      for (let e = 0; e < 7; e++) {
        const px = Math.round(cx + Math.cos(t) * (R - e)), py = Math.round(cy + Math.sin(t) * (R - e));
        ctx.fillStyle = e === 0 || e === 6 ? '#1f4d80' : '#2f6fb5';
        ctx.fillRect(px, py, 1, 1);
      }
    }
    for (let a = 0; a <= 180; a += 12) {
      const t = Math.PI + a / 180 * Math.PI;
      const px = Math.round(cx + Math.cos(t) * (R + 1)), py = Math.round(cy + Math.sin(t) * (R + 1));
      ctx.fillStyle = ((a / 12 + v) % 2) ? '#ffe58a' : '#b8862a';
      ctx.fillRect(px - 1, py - 1, 3, 3);
    }
    // L'enseigne dans la cle de voute : « FOIRE » en lettres doublees.
    ctx.fillStyle = '#c0392b'; ctx.fillRect(15, 6, 42, 16);
    ctx.fillStyle = '#8e1f16'; ctx.fillRect(15, 19, 42, 3);
    const LETTRES = {
      F: ['111', '100', '110', '100', '100'], O: ['111', '101', '101', '101', '111'],
      I: ['111', '010', '010', '010', '111'], R: ['110', '101', '110', '101', '101'],
      E: ['111', '100', '110', '100', '111'],
    };
    let lx = 17;
    for (const l of 'FOIRE') {
      LETTRES[l].forEach(function (rangee, ry) {
        for (let rx = 0; rx < 3; rx++) {
          if (rangee[rx] !== '1') continue;
          ctx.fillStyle = '#ffe58a'; ctx.fillRect(lx + rx * 2, 8 + ry * 2, 2, 2);
        }
      });
      lx += 8;
    }
    // Les fanions qui pendent sous l'arc.
    for (let x = 20; x < 54; x += 5) {
      ctx.fillStyle = ['#efd06a', '#5fb87a', '#e87aa8', '#4fa3d1'][(x / 5) % 4];
      ctx.fillRect(x, 24, 3, 2); ctx.fillRect(x + 1, 26, 1, 1);
    }
  } },

  // LA GRANDE ROUE. ⚠️ **Ce n'est pas un manège, c'est un BELVEDERE QUI TOURNE**,
  // et c'est le POINT DE REPERE de la foire : on la voit du bout de l'allee et
  // c'est elle qui dit ou l'on va. ⚠️ Premiere version jetee : 44 px de haut,
  // perdue au milieu d'un champ — Martin la cherchait sur sa capture. Elle
  // double : 84 x 92, douze nacelles, une jante d'ampoules.
  // ⚠️ Son empreinte au sol reste celle de son PORTIQUE, pas de sa jante : la
  // roue est EN L'AIR, on passe dessous. Le juge de `PORTEE_DECOR` le tient.
  // ⚠️ **SES NACELLES NE SONT PLUS ICI** (Martin : « pareil pour la grande roue » —
  // le style des véhicules, et un tour) : ce sont des machines en volume que
  // `Foire` peint par-dessus, à l'angle même de ces rayons (`moyeu`, `rayon`,
  // `nacelles`, et la pose qui avance d'un sixième d'intervalle) — c'est ce qui
  // permet de s'asseoir dans l'une d'elles et de faire le tour avec elle.
  grande_roue: { anime: 22, arrete: 14, w: 84, h: 92, ancre: [42, 88], r: 16, sol: [16, 8], solide: true, variantes: 6, moyeu: [42, 40], rayon: 36, nacelles: 12, peindre: function (ctx, w, h, v) {
    const f = DECORS.grande_roue, cx = f.moyeu[0], cy = f.moyeu[1], R = f.rayon, N = f.nacelles;
    ctx.fillStyle = 'rgba(20,18,26,0.26)'; ctx.fillRect(12, 84, 60, 7);      // son ombre
    // Le portique : deux jambes en A de chaque cote du moyeu.
    ctx.fillStyle = '#4a4d55';
    for (let t = 0; t <= 1; t += 0.02) {
      ctx.fillRect(Math.round(cx - 3 + (18 - 3) * -t), Math.round(cy + t * 46), 3, 2);
      ctx.fillRect(Math.round(cx + 1 + 18 * t), Math.round(cy + t * 46), 3, 2);
    }
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(18, 85, 16, 4); ctx.fillRect(50, 85, 16, 4);
    // Les rayons, qui tournent avec les nacelles.
    ctx.fillStyle = '#9aa0a8';
    for (let k = 0; k < N; k++) {
      const t = (k / N + v / (N * 6)) * Math.PI * 2;
      for (let d = 5; d < R; d += 2) ctx.fillRect(Math.round(cx + Math.cos(t) * d), Math.round(cy + Math.sin(t) * d), 1, 1);
    }
    // La jante, une couronne d'ampoules qui s'allument une sur deux.
    for (let a = 0; a < 120; a++) {
      const t = a / 120 * Math.PI * 2;
      const px = Math.round(cx + Math.cos(t) * R), py = Math.round(cy + Math.sin(t) * R);
      ctx.fillStyle = (a % 6 === (v % 2) * 3) ? '#ffe58a' : ((a % 12 < 6) ? '#c0392b' : '#efe6d0');
      ctx.fillRect(px, py, 2, 2);
    }
    ctx.fillStyle = '#5e626a'; ctx.fillRect(cx - 5, cy - 5, 10, 10);         // le moyeu
    ctx.fillStyle = '#a6aab0'; ctx.fillRect(cx - 3, cy - 4, 6, 6);
    ctx.fillStyle = '#ffe58a'; ctx.fillRect(cx - 1, cy - 2, 2, 2);
    // ⚠️ Les attaches des nacelles, au bout des rayons : les nacelles elles-memes
    // pendent de la, peintes par `Foire` (voir plus haut).
    ctx.fillStyle = '#5e626a';
    for (let k = 0; k < N; k++) {
      const t = (k / N + v / (N * 6)) * Math.PI * 2;
      ctx.fillRect(Math.round(cx + Math.cos(t) * R) - 1, Math.round(cy + Math.sin(t) * R) - 1, 3, 3);
    }
  } },

  // LE PIED DE LA MONTAGNE RUSSE. ⚠️ `invisible` : il est PEINT avec la
  // structure (`Foire`, une image pour toute la montagne) — l'entite ne sert
  // qu'a ARRETER, parce que la voie est en l'air et qu'on passe dessous, mais
  // pas au travers d'un treteau d'acier. Vingt-quatre pieds peints un par un
  // coutaient vingt-quatre images par image, pour rien.
  // Sa boite se cale sur la semelle : `Foire` pose le treteau a quatre pixels
  // au-dessus du bas de la tuile, la ou l'entite a son pied.
  pied_montagne_russe: { invisible: true, arrete: 30, w: 12, h: 6, ancre: [6, 6], r: 4, sol: [4, 3], solide: true, peindre: function (ctx) {
    ctx.fillStyle = '#6f737a'; ctx.fillRect(1, 2, 10, 3);
    ctx.fillStyle = '#e4e2da'; ctx.fillRect(3, 0, 1, 3);
    ctx.fillStyle = '#a3a6ac'; ctx.fillRect(8, 0, 1, 3);
  } },

  // ⚠️ LES TROIS MANÈGES A L'ECHELLE DE LA GRANDE ROUE. Premiere version
  // jetee : 30 a 34 px, la taille d'un kiosque a limonade — sur la capture de
  // Martin, les tasses et les chaises volantes avaient l'air de jouets poses
  // entre la roue (84 x 92) et la montagne russe. Ils doublent : le carrousel
  // et les tasses prennent presque la largeur de la roue, les chaises volantes
  // les trois quarts de sa hauteur. Le pas des manèges (7 tuiles, 112 px)
  // laisse encore une allee entre deux voisins.
  // ⚠️ `r` reste a 14 : c'est le cercle des balles et des chars, et ils ne
  // cherchent le decor qu'a 24 et `c.r + 14` pixels. C'est la BOITE `sol` qui
  // grandit — le plancher entier arrete le pieton — et `PORTEE_DECOR` avec elle.

  // LE CARROUSEL : un toit conique raye, et les chevaux dessous qui tournent.
  // ⚠️ Huit chevaux de DEUX robes, et la pose avance d'un quart de tour en six
  // images : deux chevaux, une robe entiere — la boucle ne saute pas.
  carrousel: { anime: 12, arrete: 14, w: 60, h: 58, ancre: [30, 46], r: 14, sol: [26, 8], solide: true, variantes: 6, peindre: function (ctx, w, h, v) {
    ctx.fillStyle = 'rgba(20,18,26,0.22)'; ovaleDeManege(ctx, 30, 50, 29, 6);   // son ombre
    ctx.fillStyle = '#8e2d23'; ovaleDeManege(ctx, 30, 47, 27, 8);               // la jupe du plancher
    ctx.fillStyle = '#e8a33a'; ovaleDeManege(ctx, 30, 46, 27, 8);
    ctx.fillStyle = '#cfc2a4'; ovaleDeManege(ctx, 30, 44, 27, 8);               // le plancher
    ctx.fillStyle = '#bfb193'; ovaleDeManege(ctx, 30, 44, 20, 5);
    const chevaux = [];
    for (let k = 0; k < 8; k++) {
      const t = (k / 8 + v / 24) * Math.PI * 2;
      chevaux.push({ k: k, x: Math.round(30 + Math.cos(t) * 21), y: Math.round(43 + Math.sin(t) * 6),
                     devant: Math.sin(t) >= 0, sens: Math.sin(t) >= 0 ? -1 : 1, saute: (k + v) % 2 });
    }
    function cheval(c) {
      const x = c.x, y = c.y - c.saute;
      ctx.fillStyle = '#e8a33a'; ctx.fillRect(x, y - 22, 1, 20);                // la barre doree
      ctx.fillStyle = c.k % 2 ? '#c98d66' : '#efe6d0';
      ctx.fillRect(x - 4, y - 3, 8, 3);                                         // le corps
      ctx.fillRect(x + c.sens * 3 - (c.sens < 0 ? 1 : 0), y - 6, 2, 4);         // l'encolure
      ctx.fillRect(x + c.sens * 4 - (c.sens < 0 ? 2 : 0), y - 6, 3, 2);         // la tete
      ctx.fillRect(x - 3, y, 1, 2); ctx.fillRect(x + 2, y, 1, 2);               // les pattes
      ctx.fillStyle = '#3a2a1a'; ctx.fillRect(c.sens > 0 ? x - 5 : x + 4, y - 3, 1, 3);                // la queue
      ctx.fillStyle = '#c0392b'; ctx.fillRect(x - 1, y - 4, 3, 1);              // la selle
    }
    chevaux.filter(function (c) { return !c.devant; }).forEach(cheval);
    // Le fut du milieu, rouge et or, entre les chevaux du fond et ceux de devant.
    ctx.fillStyle = '#a8322a'; ctx.fillRect(25, 22, 10, 22);
    ctx.fillStyle = '#c0392b'; ctx.fillRect(26, 22, 7, 22);
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(27, 27, 5, 6); ctx.fillRect(27, 36, 5, 5);   // les miroirs
    ctx.fillStyle = '#e8a33a'; ctx.fillRect(25, 25, 10, 1); ctx.fillRect(25, 34, 10, 1);
    chevaux.filter(function (c) { return c.devant; }).forEach(cheval);
    // Le toit conique, raye en quartiers qui montent a l'epi — c'est lui qui
    // nomme un carrousel du bout de l'allee.
    for (let r = 0; r < 19; r++) {
      const demi = 2 + Math.round(r * 27 / 18);
      for (let dx = -demi; dx <= demi; dx++) {
        const quartier = Math.floor((dx + demi) / (2 * demi + 1) * 10);
        ctx.fillStyle = quartier % 2 ? '#c0392b' : '#efe6d0';
        ctx.fillRect(30 + dx, 4 + r, 1, 1);
      }
    }
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(31, 4, 1, 19);          // l'arete a l'ombre
    // La frange festonnee, et ses ampoules qui s'allument une sur deux.
    for (let x = 1; x < 60; x++) {
      const feston = (x - 1) % 6;
      ctx.fillStyle = Math.floor((x - 1) / 6) % 2 ? '#c0392b' : '#e8a33a';
      ctx.fillRect(x, 23, 1, feston > 0 && feston < 5 ? 3 : 2);
    }
    for (let x = 4; x < 58; x += 6) {
      ctx.fillStyle = ((x / 6) | 0) % 2 === v % 2 ? '#ffe58a' : '#efe6d0';
      ctx.fillRect(x, 23, 1, 1);
    }
    ctx.fillStyle = '#e8a33a'; ctx.fillRect(29, 1, 3, 3);                       // l'epi
    ctx.fillStyle = '#c0392b'; ctx.fillRect(32, 0, 4, 2);                       // son fanion
  } },

  // LES TASSES : six tasses sur un grand plateau qui tourne, et du monde dedans.
  // ⚠️ Trois couleurs et six tasses : un demi-tour en huit poses remet
  // chaque couleur a la place de la meme couleur — la boucle ne saute pas.
  tasses: { anime: 10, arrete: 12, w: 58, h: 40, ancre: [29, 28], r: 14, sol: [25, 9], solide: true, variantes: 8, peindre: function (ctx, w, h, v) {
    ctx.fillStyle = 'rgba(20,18,26,0.22)'; ovaleDeManege(ctx, 29, 30, 28, 9);   // son ombre
    ctx.fillStyle = '#3f3748'; ovaleDeManege(ctx, 29, 27, 26, 10);              // le bord du plateau
    ctx.fillStyle = '#7a6d88'; ovaleDeManege(ctx, 29, 25, 26, 10);              // le plateau
    ctx.fillStyle = '#8c7f9a'; ovaleDeManege(ctx, 29, 25, 20, 7);
    ctx.fillStyle = '#7a6d88'; ovaleDeManege(ctx, 29, 25, 14, 5);
    const tasses = [];
    for (let k = 0; k < 6; k++) {
      const t = (k / 6 + v / 16) * Math.PI * 2;
      tasses.push({ k: k, x: Math.round(29 + Math.cos(t) * 17), y: Math.round(25 + Math.sin(t) * 7), devant: Math.sin(t) >= 0 });
    }
    function tasse(c) {
      const x = c.x, y = c.y;
      ctx.fillStyle = '#efe6d0'; ovaleDeManege(ctx, x, y + 2, 6, 2);            // la soucoupe
      ctx.fillStyle = ['#e0574f', '#4fa3d1', '#efd06a'][c.k % 3];
      ctx.fillRect(x - 5, y - 4, 11, 5);                                        // la tasse
      ctx.fillRect(x - 4, y + 1, 9, 1);
      ctx.fillRect(x + 6, y - 3, 2, 1); ctx.fillRect(x + 7, y - 3, 1, 3);       // l'anse
      ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillRect(x - 5, y - 4, 11, 1);
      ctx.fillStyle = '#2a2a2e'; ctx.fillRect(x - 4, y - 3, 9, 1);              // le creux
      // Deux tetes qui depassent — une tasse vide ne tourne pour personne.
      ctx.fillStyle = '#e8b088'; ctx.fillRect(x - 3, y - 6, 2, 2); ctx.fillRect(x + 1, y - 6, 2, 2);
      ctx.fillStyle = ['#3a2a1a', '#c98d66', '#1b1b1f'][c.k % 3];
      ctx.fillRect(x - 3, y - 7, 2, 1); ctx.fillRect(x + 1, y - 7, 2, 1);
    }
    tasses.filter(function (c) { return !c.devant; }).forEach(tasse);
    // Le sucrier du milieu : un fut creme coiffe d'un dome rouge.
    ctx.fillStyle = '#d9cfb8'; ctx.fillRect(25, 15, 9, 11);
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(25, 15, 6, 11);
    ctx.fillStyle = '#c0392b'; ovaleDeManege(ctx, 29, 14, 6, 3);
    ctx.fillStyle = '#e0574f'; ctx.fillRect(26, 12, 4, 1);
    ctx.fillStyle = '#e8a33a'; ctx.fillRect(28, 9, 3, 3);                       // le bouton
    ctx.fillStyle = v % 2 ? '#ffe58a' : '#e8a33a'; ctx.fillRect(29, 9, 1, 1);
    tasses.filter(function (c) { return c.devant; }).forEach(tasse);
  } },

  // LES CHAISES VOLANTES : le mat, le parasol, et les nacelles au bout de leurs
  // chaines — ⚠️ elles s'ECARTENT quand ca tourne, et c'est ce qui se lit.
  // ⚠️ Comme la roue, elles tournent EN L'AIR : la boite au sol est l'enclos
  // qu'elles balaient, pas leur dessin.
  chaises_volantes: { anime: 13, arrete: 14, w: 72, h: 70, ancre: [36, 64], r: 14, sol: [24, 8], solide: true, variantes: 4, peindre: function (ctx, w, h, v) {
    ctx.fillStyle = 'rgba(20,18,26,0.20)'; ovaleDeManege(ctx, 36, 65, 30, 5);   // son ombre
    ctx.fillStyle = '#3a3d44'; ovaleDeManege(ctx, 36, 63, 13, 4);               // le socle
    ctx.fillStyle = '#5e626a'; ovaleDeManege(ctx, 36, 62, 13, 4);
    const ecart = 26 + (v % 2) * 2;
    const chaises = [];
    for (let k = 0; k < 12; k++) {
      const t = (k / 12 + v / 24) * Math.PI * 2;
      chaises.push({ k: k, hx: 36 + Math.cos(t) * 18, hy: 18 + Math.sin(t) * 4,
                     x: Math.round(36 + Math.cos(t) * ecart), y: Math.round(36 + Math.sin(t) * 8),
                     devant: Math.sin(t) >= 0 });
    }
    function chaise(c) {
      ctx.fillStyle = '#9aa0a8';                                                // la chaine
      for (let i = 0; i <= 16; i++) {
        ctx.fillRect(Math.round(c.hx + (c.x - c.hx) * i / 16), Math.round(c.hy + (c.y - 2 - c.hy) * i / 16), 1, 1);
      }
      ctx.fillStyle = '#e8b088'; ctx.fillRect(c.x - 1, c.y - 3, 2, 2);          // qui est assis
      ctx.fillStyle = c.k % 2 ? '#2f6fb5' : '#d98324';
      ctx.fillRect(c.x - 2, c.y - 1, 5, 3);                                     // la nacelle
      ctx.fillStyle = 'rgba(20,18,26,0.25)'; ctx.fillRect(c.x - 2, c.y + 1, 5, 1);
      ctx.fillStyle = '#3a3d44'; ctx.fillRect(c.x - 1, c.y + 2, 1, 2); ctx.fillRect(c.x + 1, c.y + 2, 1, 2);   // les jambes
    }
    chaises.filter(function (c) { return !c.devant; }).forEach(chaise);
    ctx.fillStyle = '#4a4d55'; ctx.fillRect(33, 16, 6, 47);                     // le mat
    ctx.fillStyle = '#6f737a'; ctx.fillRect(34, 16, 2, 47);
    ctx.fillStyle = '#e8a33a'; ctx.fillRect(33, 34, 6, 2); ctx.fillRect(33, 50, 6, 2);
    chaises.filter(function (c) { return c.devant; }).forEach(chaise);
    // Le parasol, en dernier : il passe PAR-DESSUS les chaines.
    for (let r = 0; r < 12; r++) {
      const demi = 3 + Math.round(r * 19 / 11);
      for (let dx = -demi; dx <= demi; dx++) {
        const quartier = Math.floor((dx + demi) / (2 * demi + 1) * 8);
        ctx.fillStyle = quartier % 2 ? '#2f8d6a' : '#efe6d0';
        ctx.fillRect(36 + dx, 6 + r, 1, 1);
      }
    }
    for (let x = 14; x <= 58; x++) {                                            // la frange
      const feston = (x - 14) % 5;
      ctx.fillStyle = Math.floor((x - 14) / 5) % 2 ? '#2f8d6a' : '#e8a33a';
      ctx.fillRect(x, 18, 1, feston > 0 && feston < 4 ? 3 : 2);
    }
    for (let x = 16; x <= 56; x += 5) {
      ctx.fillStyle = ((x / 5) | 0) % 2 === v % 2 ? '#ffe58a' : '#efe6d0';
      ctx.fillRect(x, 18, 1, 1);
    }
    ctx.fillStyle = '#9aa0a8'; ctx.fillRect(35, 1, 2, 5);                       // la hampe
    ctx.fillStyle = '#c0392b'; ctx.fillRect(37, 1, 5, 2);                       // le fanion
  } },

  // --- Les trois kiosques de jeu. ⚠️ Un jeu d'adresse est un DEFI, pas un
  // moteur : ce qui suit n'est que le comptoir ou l'on s'arrete.
  galerie_tir: { arrete: 8, w: 28, h: 22, ancre: [14, 19], r: 11, sol: [12, 8], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.22)'; ctx.fillRect(3, 17, 22, 4);
    ctx.fillStyle = '#5a3f26'; ctx.fillRect(2, 6, 24, 12);                   // la baraque
    ctx.fillStyle = '#7a5836'; ctx.fillRect(2, 6, 23, 10);
    ctx.fillStyle = '#2a2a2e'; ctx.fillRect(4, 9, 20, 6);                    // le fond noir
    for (let k = 0; k < 3; k++) {                                            // les cibles
      const cx = 7 + k * 7;
      ctx.fillStyle = '#efe6d0'; ctx.fillRect(cx - 2, 10, 5, 5);
      ctx.fillStyle = '#c0392b'; ctx.fillRect(cx - 1, 11, 3, 3);
      ctx.fillStyle = '#efe6d0'; ctx.fillRect(cx, 12, 1, 1);
    }
    ctx.fillStyle = '#c0392b'; ctx.fillRect(1, 3, 26, 4);                    // l'auvent raye
    ctx.fillStyle = '#efe6d0';
    for (let dx = 1; dx < 27; dx += 6) ctx.fillRect(dx, 3, 3, 4);
    ctx.fillStyle = '#3a2f26'; ctx.fillRect(2, 17, 24, 1);
  } },

  marteau_force: { anime: 40, arrete: 7, w: 20, h: 40, ancre: [10, 37], r: 8, sol: [8, 7], solide: true, variantes: 3, peindre: function (ctx, w, h, v) {
    ctx.fillStyle = 'rgba(20,18,26,0.22)'; ctx.fillRect(3, 34, 14, 4);
    ctx.fillStyle = '#4a4d55'; ctx.fillRect(7, 6, 6, 30);                    // la colonne
    ctx.fillStyle = '#5e626a'; ctx.fillRect(7, 6, 4, 30);
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(4, 34, 12, 3);                   // le socle
    // L'echelle des ampoules : `v` dit jusqu'ou la derniere frappe est montee.
    for (let k = 0; k < 9; k++) {
      const allumee = k >= 8 - v * 3;
      ctx.fillStyle = allumee ? (k > 6 ? '#ff4b3e' : k > 3 ? '#e8a33a' : '#5fb87a') : '#2a2a2e';
      ctx.fillRect(5, 9 + k * 3, 2, 2); ctx.fillRect(13, 9 + k * 3, 2, 2);
    }
    ctx.fillStyle = '#e8a33a'; ctx.fillRect(6, 3, 8, 3);                     // la cloche
    ctx.fillStyle = '#c08a20'; ctx.fillRect(6, 5, 8, 1);
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(14, 28, 5, 2);                   // le maillet, appuye
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(17, 26, 3, 4);
  } },

  peche_canards: { anime: 22, arrete: 8, w: 26, h: 22, ancre: [13, 19], r: 10, sol: [11, 8], solide: true, variantes: 3, peindre: function (ctx, w, h, v) {
    ctx.fillStyle = 'rgba(20,18,26,0.22)'; ctx.fillRect(3, 17, 20, 4);
    ctx.fillStyle = '#3f6f8a'; ctx.fillRect(2, 7, 22, 11);                   // le bassin
    ctx.fillStyle = '#5a93ad'; ctx.fillRect(3, 8, 20, 9);
    ctx.fillStyle = '#7fb6d9'; ctx.fillRect(3, 8 + (v % 3), 20, 1);          // la ride qui tourne
    for (let k = 0; k < 5; k++) {                                            // les canards
      const dx = 4 + ((k * 4 + v) % 18);
      ctx.fillStyle = '#efd06a'; ctx.fillRect(dx, 10 + (k % 2) * 3, 4, 3);
      ctx.fillStyle = '#e8a33a'; ctx.fillRect(dx + 3, 10 + (k % 2) * 3, 2, 1);
    }
    ctx.fillStyle = '#5a3f26'; ctx.fillRect(1, 4, 24, 3);                    // le rebord
    ctx.fillStyle = '#7a5836'; ctx.fillRect(1, 4, 24, 2);
    ctx.fillStyle = '#c0392b'; ctx.fillRect(20, 1, 2, 6);                    // la canne
    ctx.fillStyle = '#9aa0a8'; ctx.fillRect(21, 6, 1, 4);
  } },

  // --- LA VIE QUI N'EST PAS HUMAINE ----------------------------------------
  //: ⚠️ **ILS NE COMPTENT POUR RIEN**, et c'est ce qui les rend vivants : ils ne
  //: sont la que pour etre la. Le dessin passe par la meme porte que le ballon —
  //: une fiche de decor, cuite par variante — et `v` n'y designe pas une couleur
  //: mais une POSE. C'est le seul mecanisme du depot qui sache dessiner une bete
  //: sans lui donner un corps de piéton.

  // LE GOELAND, vu d'en haut. ⚠️ Ce qui le nomme a douze pixels, c'est le BLANC
  // casse d'un corps trapu, la tache grise des ailes repliees et le point orange
  // du bec — un oiseau gris entier se lit comme un caillou.
  // Poses : 0 debout, 1 il picore (la tete descend), 2 ailes ouvertes (l'envol).
  goeland: { solide: false, r: 0, variantes: 3, w: 16, h: 16, ancre: [8, 12], peindre: function (ctx, w, h, v) {
    const envol = v === 2, picore = v === 1;
    // ⚠️ LA TETE SORT DE LA SILHOUETTE. Premiere version jetee : elle etait
    // posee DANS le corps, et a seize pixels l'oiseau n'etait qu'un bloc blanc
    // avec un point orange. Ce qui nomme un goeland, c'est le cou qui depasse
    // devant et le bec au bout — pas la couleur, qu'il partage avec un caillou.
    ctx.fillStyle = 'rgba(20,18,26,0.16)'; ctx.fillRect(6, envol ? 14 : 12, 5, 2);
    if (envol) {                                                            // les ailes ouvertes
      ctx.fillStyle = '#d8d6ce'; ctx.fillRect(0, 6, 5, 3); ctx.fillRect(11, 6, 5, 3);
      ctx.fillStyle = '#b3b8bf'; ctx.fillRect(0, 8, 5, 1); ctx.fillRect(11, 8, 5, 1);
      ctx.fillStyle = '#3a3d44'; ctx.fillRect(0, 6, 2, 2); ctx.fillRect(14, 6, 2, 2);   // le bout noir
    }
    const cou = picore ? 7 : 3;                                             // il baisse la tete pour picorer
    ctx.fillStyle = '#efeee8'; ctx.fillRect(6, cou, 4, 4);                  // la tete, DEVANT le corps
    ctx.fillStyle = '#1b1b1f'; ctx.fillRect(7, cou + 1, 1, 1);              // l'oeil
    ctx.fillStyle = '#e8a33a'; ctx.fillRect(10, cou + 1, 3, 1);             // le bec, qui depasse
    ctx.fillStyle = '#efeee8'; ctx.fillRect(5, 6, 6, 6);                    // le corps, au soleil
    ctx.fillStyle = '#d8d6ce'; ctx.fillRect(5, 10, 6, 2);                   // son dessous, dans l'ombre
    if (!envol) {
      ctx.fillStyle = '#b3b8bf'; ctx.fillRect(4, 7, 8, 3);                  // les ailes repliees, en manteau
      ctx.fillStyle = '#8f959d'; ctx.fillRect(4, 9, 8, 1);
      ctx.fillStyle = '#3a3d44'; ctx.fillRect(6, 11, 4, 1);                 // le bout de la queue
      ctx.fillStyle = '#e8a33a'; ctx.fillRect(6, 12, 1, 1); ctx.fillRect(9, 12, 1, 1);   // les pattes
    }
  } },

  // LE CHAT, vu d'en haut. ⚠️ Ce qui le nomme, c'est la QUEUE : longue, une
  // tuile a elle seule, et c'est elle qu'on voit filer au bout d'une ruelle.
  // Poses : 0 assis (queue enroulee), 1 en marche, 2 il detale (corps etire).
  chat: { solide: false, r: 0, variantes: 3, w: 16, h: 16, ancre: [8, 12], peindre: function (ctx, w, h, v) {
    const file = v === 2, marche = v === 1;
    // ⚠️ LES OREILLES SE DETACHENT SUR LE FOND, pas sur le corps. Premiere
    // version jetee : deux carres sombres poses sur une tete sombre, invisibles
    // dans une ruelle. Elles sortent maintenant du crane, en pointes, et c'est
    // avec la QUEUE ce qui nomme un chat vu d'en haut.
    ctx.fillStyle = 'rgba(20,18,26,0.22)'; ctx.fillRect(5, 12, 7, 2);        // son ombre
    const long = file ? 9 : marche ? 7 : 5;                                  // assis, il se ramasse
    const y0 = 12 - long;
    ctx.fillStyle = '#3f362e'; ctx.fillRect(5, y0, 6, long);                 // le corps, dans l'ombre
    ctx.fillStyle = '#6b5c4d'; ctx.fillRect(5, y0, 5, long - 1);             // sa face eclairee du nord-ouest
    ctx.fillStyle = '#54483c';                                               // les rayures du dos
    for (let i = 0; i < Math.max(2, long - 3); i += 2) ctx.fillRect(5, y0 + 2 + i, 6, 1);
    // La queue : enroulee quand il est assis, tendue quand il file.
    ctx.fillStyle = '#3f362e';
    if (file) { ctx.fillRect(7, 12, 2, 4); ctx.fillRect(7, 15, 3, 1); }
    else if (marche) { ctx.fillRect(11, 9, 3, 2); ctx.fillRect(13, 6, 2, 4); }
    else { ctx.fillRect(11, 10, 4, 2); ctx.fillRect(14, 7, 2, 4); }
    ctx.fillStyle = '#7d6c59'; ctx.fillRect(5, y0, 6, 3);                    // la tete, plus claire que le dos
    ctx.fillStyle = '#3f362e';                                               // les deux oreilles, en pointes
    ctx.fillRect(4, y0 - 2, 2, 3); ctx.fillRect(10, y0 - 2, 2, 3);
    ctx.fillStyle = '#6b5c4d'; ctx.fillRect(5, y0 - 1, 1, 1); ctx.fillRect(10, y0 - 1, 1, 1);
    ctx.fillStyle = '#c8d84a'; ctx.fillRect(6, y0 + 1, 1, 1); ctx.fillRect(9, y0 + 1, 1, 1);   // les yeux
    ctx.fillStyle = '#e0b7a8'; ctx.fillRect(7, y0 + 2, 2, 1);                // le museau
  } },

  // LE BALLON DE PLAGE. ⚠️ Il ne bloque rien et n'entre dans aucun index : il
  // VOLE. Un decor qui bouge se voit de trois ecrans — c'est tout ce qu'on
  // demande a deux enfants qui se le lancent.
  ballon: { solide: false, r: 3, w: 10, h: 10, ancre: [5, 7], peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(2, 8, 6, 2);         // son ombre au sol
    ctx.fillStyle = '#e8e6de'; ctx.fillRect(2, 1, 6, 7); ctx.fillRect(1, 2, 8, 5);
    ctx.fillStyle = '#c0392b'; ctx.fillRect(3, 1, 2, 7);                     // les quartiers de couleur
    ctx.fillStyle = '#2f6fb5'; ctx.fillRect(6, 2, 2, 5);
    ctx.fillStyle = '#b8b5aa'; ctx.fillRect(1, 6, 8, 1);                     // le dessous, dans l'ombre
  } },

  // --- LE BORD DE L'EAU ----------------------------------------------------
  //: ⚠️ Mesure d'abord, et c'est elle qui a decide de la vague : la ville posait
  //: **2 507 tuiles de sable** (dont 782 touchent l'eau) et **1 818 de quai**, et
  //: personne ne s'y asseyait jamais. Ce qui manquait n'etait pas le terrain :
  //: c'est que le bord de l'eau etait un decor qu'on TRAVERSE. Six fiches et un
  //: semis, aucun moteur neuf — exactement le chemin du cabanon et du BBQ.

  // LA TABLE A PIQUE-NIQUE. ⚠️ Vue d'en haut, c'est un **H couche** : deux bancs
  // paralleles et le plateau entre les deux. C'est ce dessin-la qui la nomme a
  // douze pixels — la couleur du bois ne fait que le confirmer. `casse`, comme
  // le banc dont elle est la cousine.
  table_pique_nique: { casse: 0.8, pv: 40, w: 22, h: 16, ancre: [11, 14], r: 6, sol: [9, 5], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(0, 1, 22, 4); ctx.fillRect(0, 11, 22, 4);   // les deux bancs, dans l'ombre
    ctx.fillStyle = '#8a6a3f'; ctx.fillRect(0, 1, 22, 3); ctx.fillRect(0, 11, 22, 3);   // leur face eclairee du nord
    ctx.fillStyle = '#7a5836'; ctx.fillRect(2, 5, 18, 6);                               // le plateau, dans l'ombre
    ctx.fillStyle = '#9c7846'; ctx.fillRect(2, 5, 18, 5);                               // sa face eclairee
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 7, 18, 1); ctx.fillRect(2, 9, 18, 1);    // les joints des planches
    ctx.fillStyle = '#4a3320'; ctx.fillRect(4, 4, 2, 8); ctx.fillRect(16, 4, 2, 8);     // les deux pietements
  } },

  // LE PARASOL. ⚠️ La seule chose du lot qui se lise **de loin**, et la seule
  // qu'on ne heurte pas : `solide: false`, on passe DESSOUS. Vu d'en haut c'est
  // un disque a quartiers alternes — ce sont les quartiers qui le nomment, la
  // couleur ne fait que dire lequel. Elle se tire par tuile (`variantes`).
  parasol: { solide: false, r: 0, variantes: 4, w: 24, h: 24, ancre: [12, 14], peindre: function (ctx, w, h, v) {
    const toile = ['#c0392b', '#2f6fb5', '#d98324', '#2f8d6a'][v % 4];
    const ombre = ['#8e1f16', '#1f4d80', '#9a5a12', '#1d6149'][v % 4];
    const cx = 11.5, cy = 11.5, R = 11;
    for (let y = 0; y < 24; y++) {
      const dy = y - cy;
      const demi = Math.sqrt(Math.max(0, R * R - dy * dy));
      for (let x = Math.ceil(cx - demi); x <= Math.floor(cx + demi); x++) {
        const dx = x - cx;
        // Huit quartiers : un sur deux dans le ton clair. ⚠️ C'est l'ALTERNANCE
        // qui se lit de trois ecrans, pas la teinte.
        const quartier = Math.floor((Math.atan2(dy, dx) + Math.PI) / (Math.PI / 4)) % 2;
        ctx.fillStyle = quartier ? toile : ombre;
        ctx.fillRect(x, y, 1, 1);
      }
    }
    ctx.fillStyle = 'rgba(20,18,26,0.22)';                                  // la toile retombe au sud-est
    for (let y = 14; y < 24; y++) {
      const dy = y - cy, demi = Math.sqrt(Math.max(0, R * R - dy * dy));
      ctx.fillRect(Math.ceil(cx - demi), y, Math.floor(2 * demi) + 1, 1);
    }
    ctx.fillStyle = '#e8e6de'; ctx.fillRect(11, 10, 2, 2);                   // le bouton du mat
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(11, 12, 2, 10);                  // le mat planté dans le sable
    ctx.fillStyle = '#8a6a3f'; ctx.fillRect(11, 12, 1, 10);
  } },

  // LA SERVIETTE ET SA GLACIERE. ⚠️ Le plan la voulait en DECAL ; elle est un
  // decor `solide: false`, et la raison est mesurable : `B.decals` est un anneau
  // PLAFONNE a 150 qui s'evide par la tete (`shift()`) pour le sang et les
  // impacts — une serviette posee a la construction de la ville en serait
  // chassee par la premiere fusillade. Rien ne l'arrete, rien ne la casse,
  // et `estIndexable` la garde hors du chemin de qui marche.
  serviette: { solide: false, r: 0, variantes: 3, w: 20, h: 14, ancre: [10, 10], peindre: function (ctx, w, h, v) {
    const drap = ['#e0574f', '#4fa3d1', '#efd06a'][v % 3];
    const raie = ['#f2ded9', '#eaf3f8', '#f6efd8'][v % 3];
    ctx.fillStyle = 'rgba(20,18,26,0.14)'; ctx.fillRect(2, 3, 14, 10);       // son ombre au sol
    ctx.fillStyle = drap; ctx.fillRect(1, 2, 14, 10);
    ctx.fillStyle = raie;                                                    // trois raies en travers
    for (let i = 0; i < 3; i++) ctx.fillRect(1, 3 + i * 3, 14, 1);
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(1, 11, 14, 1);       // le pli du bas
    ctx.fillStyle = '#2f6fb5'; ctx.fillRect(15, 5, 5, 6);                    // la glaciere, dans l'ombre
    ctx.fillStyle = '#4a90c4'; ctx.fillRect(15, 5, 4, 5);
    ctx.fillStyle = '#e8e6de'; ctx.fillRect(15, 5, 5, 2);                    // son couvercle
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(17, 6, 1, 1);                    // la poignee
  } },

  // LE CHATEAU DE SABLE. ⚠️ Le seul du lot qui ait une REGLE, et c'est ce qui en
  // fait autre chose qu'un ornement : `pv: 5`, le decor le plus fragile du jeu —
  // un char qui roule sur la greve le rase — et il **revient au matin** avec
  // tout le reste (`reparerLeDecor`). Un enfant qui recommence son chateau tous
  // les jours, c'est une blague que la ville raconte sans qu'on l'ecrive.
  chateau_sable: { casse: 1.0, pv: 5, w: 16, h: 16, ancre: [8, 14], r: 4, solide: false, peindre: function (ctx, w, h) {
    // ⚠️ LA SILHOUETTE AVANT LA COULEUR — premiere version jetee : tout etait du
    // meme beige, tours et courtine confondues, et ce qu'on lisait a douze
    // pixels etait une MOTTE avec un drapeau dessus. Deux tours DETACHEES, une
    // courtine basse entre elles, et l'ombre qui creuse l'ecart : c'est le
    // decoupe qui nomme un chateau, le sable ne fait que le confirmer.
    ctx.fillStyle = 'rgba(90,70,36,0.30)'; ctx.fillRect(1, 13, 14, 2);       // son ombre portee au sud
    ctx.fillStyle = '#9c7f4c'; ctx.fillRect(4, 8, 8, 6);                     // la courtine, dans l'ombre
    ctx.fillStyle = '#c9ab72'; ctx.fillRect(4, 8, 8, 4);                     // sa face eclairee du nord
    ctx.fillStyle = '#8a6e3e';                                               // les creneaux de la courtine
    ctx.fillRect(5, 8, 2, 2); ctx.fillRect(9, 8, 2, 2);
    ctx.fillStyle = '#7d6236'; ctx.fillRect(0, 4, 5, 10); ctx.fillRect(11, 4, 5, 10);   // les deux tours, dans l'ombre
    ctx.fillStyle = '#d8bd85'; ctx.fillRect(0, 4, 4, 9); ctx.fillRect(11, 4, 4, 9);     // leur face eclairee
    ctx.fillStyle = '#f0dcab'; ctx.fillRect(0, 4, 4, 2); ctx.fillRect(11, 4, 4, 2);     // leur couronne, au soleil
    ctx.fillStyle = '#6b5329';                                               // leurs creneaux, en creux
    ctx.fillRect(1, 4, 1, 2); ctx.fillRect(3, 4, 1, 2);
    ctx.fillRect(12, 4, 1, 2); ctx.fillRect(14, 4, 1, 2);
    ctx.fillStyle = '#6b5329'; ctx.fillRect(4, 4, 1, 10); ctx.fillRect(11, 4, 1, 10);   // le joint tour/courtine
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(7, 0, 1, 9);                     // la hampe, plantee dans la courtine
    ctx.fillStyle = '#c0392b'; ctx.fillRect(8, 0, 5, 3);                     // le fanion
    ctx.fillStyle = '#8e1f16'; ctx.fillRect(8, 2, 5, 1);
  } },

  // LA CHAISE LONGUE. ⚠️ Vue d'en haut, une plage se lit par ce qu'on y POSE pour
  // rester : un parasol dit « il fait soleil », une chaise longue dit « on est la
  // pour la journee ». Une toile rayee entre deux longerons, et le dossier releve
  // qui prend le jour — c'est la cassure de lumiere qui la distingue d'une
  // serviette. On passe par-dessus (`solide: false`), comme la serviette.
  chaise_longue: { solide: false, r: 0, variantes: 3, w: 12, h: 20, ancre: [6, 15], peindre: function (ctx, w, h, v) {
    const toile = ['#2f6fb5', '#e0574f', '#2f8d6a'][v % 3];
    const raie = ['#eaf3f8', '#f2ded9', '#e6f2ea'][v % 3];
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(3, 7, 8, 12);        // son ombre, au sud-est
    ctx.fillStyle = '#d8d2c0'; ctx.fillRect(1, 1, 1, 17); ctx.fillRect(9, 1, 1, 17);   // les deux longerons
    ctx.fillStyle = toile; ctx.fillRect(2, 1, 7, 16);                        // la toile tendue
    ctx.fillStyle = raie;                                                    // ses rayures en travers
    for (let y = 2; y < 17; y += 3) ctx.fillRect(2, y, 7, 1);
    ctx.fillStyle = 'rgba(255,255,255,0.30)'; ctx.fillRect(2, 1, 7, 5);      // le dossier releve prend le jour
    ctx.fillStyle = 'rgba(20,18,26,0.25)'; ctx.fillRect(1, 6, 9, 1);         // la cassure ou il se couche
    ctx.fillStyle = '#9a9385'; ctx.fillRect(1, 18, 1, 2); ctx.fillRect(9, 18, 1, 2);   // les pieds
  } },

  // LE KAYAK, tire sur le sable. ⚠️ Un FUSEAU, jamais un rectangle : un rectangle
  // de couleur couche sur la plage se lit comme une serviette de plus. Ce sont
  // les deux pointes et le trou d'homme au milieu qui le nomment, et la pagaie
  // couchee a cote le confirme.
  kayak: { solide: false, r: 0, variantes: 3, w: 30, h: 12, ancre: [15, 7], peindre: function (ctx, w, h, v) {
    const coque = ['#efc02a', '#e8742a', '#c0392b'][v % 3];
    const flanc = ['#b88a12', '#a94f16', '#8e1f16'][v % 3];
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(4, 7, 24, 2);        // son ombre sur le sable
    const demi = [8, 12, 13, 13, 12, 8];                                     // chaque rangee plus courte vers les pointes
    for (let r = 0; r < demi.length; r++) {
      ctx.fillStyle = r < 3 ? coque : flanc;
      ctx.fillRect(15 - demi[r], 1 + r, 2 * demi[r], 1);
    }
    ctx.fillStyle = '#2a2a2e'; ctx.fillRect(12, 2, 6, 3);                    // le trou d'homme
    ctx.fillStyle = '#4a4a52'; ctx.fillRect(13, 2, 4, 1);
    ctx.fillStyle = '#e8e6de'; ctx.fillRect(4, 3, 2, 1); ctx.fillRect(24, 3, 2, 1);   // les poignees de bout
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(4, 9, 22, 1);                    // la pagaie couchee a cote
    ctx.fillStyle = '#2f6fb5'; ctx.fillRect(1, 8, 3, 3); ctx.fillRect(26, 8, 3, 3);   // ses deux pales
  } },

  // LA CHAISE DU SAUVETEUR. ⚠️ UNE PAR PLAGE (`carte.GREVE["sauveteur"]`), au
  // milieu, et c'est la seule chose du lot qu'on voit de l'autre bout de l'ecran :
  // elle est HAUTE. Quatre pattes evasees, une echelle, un siege, un dossier a
  // bande rouge, le fanion et la bouee de sauvetage accrochee. Elle arrete un
  // passant comme un banc, et elle cede sous un char comme lui.
  chaise_sauveteur: { casse: 0.7, pv: 40, w: 20, h: 30, ancre: [10, 28], r: 6, sol: [8, 4], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.22)'; ctx.fillRect(3, 26, 16, 3);       // son ombre au pied
    ctx.fillStyle = '#cfc8b4';                                               // les quatre pattes, evasees
    ctx.fillRect(3, 14, 2, 14); ctx.fillRect(15, 14, 2, 14);
    ctx.fillRect(6, 16, 1, 11); ctx.fillRect(13, 16, 1, 11);
    ctx.fillStyle = '#a79f88'; ctx.fillRect(5, 20, 10, 1); ctx.fillRect(5, 24, 10, 1);   // les barreaux de l'echelle
    ctx.fillStyle = '#efe9da'; ctx.fillRect(3, 11, 14, 4);                   // le siege
    ctx.fillStyle = '#d8d2c0'; ctx.fillRect(3, 14, 14, 1);
    ctx.fillStyle = '#efe9da'; ctx.fillRect(4, 4, 12, 7);                    // le dossier
    ctx.fillStyle = '#c0392b'; ctx.fillRect(4, 6, 12, 3);                    // sa bande rouge
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(16, 0, 1, 7);                    // la hampe
    ctx.fillStyle = '#c0392b'; ctx.fillRect(17, 0, 3, 2);                    // le fanion rouge et jaune
    ctx.fillStyle = '#efc02a'; ctx.fillRect(17, 2, 3, 1);
    ctx.fillStyle = '#e8742a'; ctx.fillRect(0, 15, 3, 6);                    // la bouee de sauvetage accrochee
    ctx.fillStyle = '#f7f1e2'; ctx.fillRect(1, 17, 1, 2);
  } },

  // LA BOUEE. ⚠️ Le seul decor du jeu qui ait raison de FLOTTER, et `flotte` le
  // dit tout haut : `poser_decor` refuse le solide, et l'eau en est
  // (`solide: 2`). Un juge s'en sert pour verifier qu'aucun autre ne s'est mis
  // a nager. Elle tangue sur place — un rond immobile sur l'eau se lit comme
  // une tache de peinture.
  bouee: { solide: false, flotte: true, r: 0, w: 14, h: 14, ancre: [7, 9], peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(12,30,44,0.30)'; ctx.fillRect(2, 5, 11, 7);        // ce qu'elle assombrit sous elle
    ctx.fillStyle = '#c0392b'; ctx.fillRect(2, 2, 10, 9);                    // l'anneau, dans l'ombre
    ctx.fillStyle = '#e0574f'; ctx.fillRect(2, 2, 10, 7);
    ctx.fillStyle = '#efe6d0';                                               // quatre quartiers alternes
    ctx.fillRect(2, 2, 4, 3); ctx.fillRect(8, 8, 4, 3);
    ctx.fillStyle = '#f7f1e2'; ctx.fillRect(8, 2, 4, 2); ctx.fillRect(2, 8, 4, 2);
    ctx.fillStyle = '#1d4a63'; ctx.fillRect(5, 5, 4, 3);                     // l'eau vue par le trou
    ctx.fillStyle = '#e8e6de'; ctx.fillRect(1, 5, 1, 3); ctx.fillRect(12, 5, 1, 3);   // le cordage
  } },

  // LE POTEAU D'AMARRAGE. Un billot ceinture de fer, la boucle d'un cordage
  // autour. ⚠️ Il est SOLIDE et petit : sur un quai, c'est exactement ce qui
  // arrete une roue sans fermer le passage.
  poteau_amarrage: { casse: 0.6, pv: 90, w: 12, h: 16, ancre: [6, 14], r: 4, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#4a3320'; ctx.fillRect(3, 3, 6, 12);                    // le billot, dans l'ombre
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(3, 3, 5, 11);                    // sa face eclairee du nord-ouest
    ctx.fillStyle = '#8a6a3f'; ctx.fillRect(3, 2, 6, 2);                     // le dessus, poli par les cordages
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(3, 6, 6, 1); ctx.fillRect(3, 11, 6, 1);   // les deux ceintures de fer
    ctx.fillStyle = '#9a8f6a'; ctx.fillRect(1, 8, 2, 1); ctx.fillRect(9, 8, 2, 1);    // la boucle du cordage
    ctx.fillRect(0, 9, 1, 2); ctx.fillRect(11, 9, 1, 2);
    ctx.fillStyle = '#2a2a2e'; ctx.fillRect(3, 15, 6, 1);                    // son pied sur les planches
  } },

  // LE BELVEDERE. Un plancher de bois sur pilotis, une rambarde, deux marches —
  // pose la ou la terre DOMINE l'eau. ⚠️ Il `arrete` au lieu de bloquer, comme
  // les kiosques : on y monte, on ne le traverse pas. Et il n'a pas de `pv` —
  // ce qui porte `arrete` encaisse et ne tombe jamais, c'est ce qui fait un abri.
  belvedere: { arrete: 9, w: 30, h: 26, ancre: [15, 23], r: 12, sol: [13, 10], solide: true, peindre: function (ctx, w, h) {
    // ⚠️ PREMIERE VERSION JETEE : un plancher de planches horizontales borde
    // d'une seule lisse au nord se lisait comme une CAISSE — une palette de
    // bois posee sur le sable. Ce qui nomme un belvedere vu d'en haut, c'est la
    // RAMBARDE qui l'entoure sur trois cotes et la trouee du sud par ou l'on
    // monte : un plancher ferme est une boite, un plancher ouvert d'un cote est
    // un endroit ou l'on va.
    ctx.fillStyle = 'rgba(30,22,12,0.34)'; ctx.fillRect(2, 21, 26, 5);       // l'ombre sous les pilotis
    ctx.fillStyle = '#a8814e'; ctx.fillRect(3, 4, 24, 18);                   // le plancher, au soleil
    ctx.fillStyle = '#8e6a3c';                                               // ses planches, dans le sens de la marche
    for (let i = 0; i < 8; i++) ctx.fillRect(3 + i * 3, 4, 1, 18);
    ctx.fillStyle = 'rgba(40,28,14,0.20)'; ctx.fillRect(3, 16, 24, 6);       // le plancher s'assombrit vers le sud
    // La rambarde : trois cotes. Une lisse claire, des barreaux sombres, et le
    // vide du sud ou sont les marches.
    ctx.fillStyle = '#5a3f26';                                               // les barreaux, sous la lisse
    for (let i = 0; i < 9; i++) ctx.fillRect(2 + i * 3, 3, 2, 3);            // ceux du nord
    for (let j = 0; j < 5; j++) { ctx.fillRect(1, 5 + j * 3, 3, 2); ctx.fillRect(26, 5 + j * 3, 3, 2); }
    ctx.fillStyle = '#c29a62'; ctx.fillRect(1, 1, 28, 3);                    // la lisse du nord, au soleil
    ctx.fillStyle = '#9a7442'; ctx.fillRect(1, 3, 28, 1);
    ctx.fillStyle = '#c29a62'; ctx.fillRect(0, 3, 3, 16); ctx.fillRect(27, 3, 3, 16);   // les deux lisses laterales
    ctx.fillStyle = '#9a7442'; ctx.fillRect(2, 3, 1, 16); ctx.fillRect(27, 3, 1, 16);
    // Les marches, au sud : deux paliers de plus en plus larges, hors du garde-corps.
    ctx.fillStyle = '#b08a55'; ctx.fillRect(9, 22, 12, 2);
    ctx.fillStyle = '#9a7442'; ctx.fillRect(7, 24, 16, 2);
    ctx.fillStyle = '#4a3320'; ctx.fillRect(0, 19, 3, 5); ctx.fillRect(27, 19, 3, 5);   // les pilotis qu'on voit
  } },

  banc: { casse: 0.8, pv: 40, w: 18, h: 12, ancre: [9, 11], r: 5, sol: [8, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(1, 4, 16, 3); ctx.fillRect(1, 0, 16, 3);
    ctx.fillStyle = '#523a22'; ctx.fillRect(2, 7, 2, 5); ctx.fillRect(14, 7, 2, 5);
    ctx.fillStyle = '#7d5a36'; ctx.fillRect(1, 4, 16, 1);
  } },
  // --- Le mobilier de rue : il REGARDE la rue ------------------------------------
  // ⚠️ Demande de Martin : « des bancs sur le bord de la rue ». Un banc de parc
  // se pose n'importe comment ; un banc de trottoir tourne le dos au mur et
  // regarde passer les chars. Le `banc` d'origine est vu de FACE (il regarde le
  // sud, vers nous) ; ses trois freres le montrent de DOS (`banc_nord`, le
  // dossier devant l'assise) et de PROFIL (`banc_est`, `banc_ouest`, le dossier
  // du cote du mur). C'est le cote du trottoir qui choisit (`mobilier.py`).
  banc_nord: { casse: 0.8, pv: 40, w: 18, h: 12, ancre: [9, 11], r: 5, sol: [8, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#7d5a36'; ctx.fillRect(1, 1, 16, 3);                 // l'assise, vue par-dessus le dossier
    ctx.fillStyle = '#523a22'; ctx.fillRect(2, 8, 2, 4); ctx.fillRect(14, 8, 2, 4);   // les pieds
    ctx.fillStyle = '#5a3f25'; ctx.fillRect(1, 4, 16, 4);                 // le dos du dossier, face a nous
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(1, 4, 16, 1);                 // son arete
  } },
  banc_est: { casse: 0.8, pv: 40, w: 10, h: 18, ancre: [5, 16], r: 5, sol: [3, 6], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#523a22'; ctx.fillRect(1, 1, 3, 13);                 // le dossier, a l'ouest, dans l'ombre
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(4, 3, 4, 12);                 // l'assise, vue du dessus
    ctx.fillStyle = '#7d5a36'; ctx.fillRect(4, 3, 4, 1); ctx.fillRect(1, 1, 3, 1);
    ctx.fillStyle = '#523a22'; ctx.fillRect(4, 15, 1, 3); ctx.fillRect(7, 15, 1, 3);   // les pieds du bout sud
  } },
  // LE BAC A FLEURS, en cossu seulement (`mobilier.PART_BAC_FLEURS`) : du beton,
  // du feuillage, et trois couleurs de fleurs. ⚠️ Il ARRETE un pieton comme un
  // banc, et cede sous un char comme lui.
  bac_fleurs: { casse: 0.8, pv: 35, w: 16, h: 12, ancre: [8, 11], r: 5, sol: [7, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(1, 10, 15, 2);        // son ombre
    ctx.fillStyle = '#8b877b'; ctx.fillRect(1, 5, 14, 6);                     // le bac de beton
    ctx.fillStyle = '#a5a194'; ctx.fillRect(1, 5, 14, 1);                     // son rebord
    ctx.fillStyle = '#6f6b60'; ctx.fillRect(1, 10, 14, 1);
    ctx.fillStyle = '#2f6b2a'; ctx.fillRect(2, 2, 12, 4); ctx.fillRect(4, 1, 8, 1);  // le feuillage
    ctx.fillStyle = '#3f8d38'; ctx.fillRect(3, 3, 4, 2); ctx.fillRect(9, 2, 3, 2);
    ctx.fillStyle = '#d9486a'; ctx.fillRect(3, 2, 2, 1); ctx.fillRect(10, 1, 1, 1); ctx.fillRect(7, 3, 1, 1);
    ctx.fillStyle = '#f2c14e'; ctx.fillRect(5, 1, 1, 1); ctx.fillRect(12, 3, 1, 1);
    ctx.fillStyle = '#ffffff'; ctx.fillRect(8, 1, 1, 1);
  } },
  // --- LE MOBILIER QUI DIT L'USAGE (`mobilier.MEUBLES_PAR_USAGE`) ------------
  // ⚠️ On reconnait une rue a ce qui l'encombre avant de lire une enseigne : un
  // parcometre devant les commerces, une boite aux lettres et un bac bleu devant
  // les maisons, des palettes et une benne devant les entrepots. Les trois premiers
  // se frolent (des poteaux, un bac bas) ; les palettes et la benne arretent.

  // LE PARCOMETRE : un poteau gris, une tete ronde, son cadran.
  parcometre: { casse: 0.9, pv: 15, w: 8, h: 18, ancre: [4, 17], r: 2, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(1, 16, 6, 2);         // son ombre
    ctx.fillStyle = '#5a5f66'; ctx.fillRect(3, 7, 2, 10);                     // le poteau
    ctx.fillStyle = '#3d4248'; ctx.fillRect(1, 1, 6, 7);                      // la tete
    ctx.fillStyle = '#6f757c'; ctx.fillRect(2, 0, 4, 1); ctx.fillRect(1, 1, 1, 6);
    ctx.fillStyle = '#cfe6f5'; ctx.fillRect(2, 2, 4, 2);                      // le cadran
    ctx.fillStyle = '#c0392b'; ctx.fillRect(5, 3, 1, 1);                      // l'aiguille : c'est echu
    ctx.fillStyle = '#9aa0a6'; ctx.fillRect(3, 5, 2, 1);                      // la fente
  } },

  // LA BOITE AUX LETTRES : sur son poteau de bois, le drapeau rouge leve.
  boite_aux_lettres: { casse: 0.9, pv: 15, w: 10, h: 16, ancre: [4, 15], r: 2, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(1, 14, 7, 2);
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(3, 6, 2, 10);                     // le poteau
    ctx.fillStyle = '#2f5f8a'; ctx.fillRect(0, 2, 8, 5); ctx.fillRect(1, 1, 6, 1);   // la boite, bombee
    ctx.fillStyle = '#3f78ad'; ctx.fillRect(1, 2, 6, 1);
    ctx.fillStyle = '#1f3f5c'; ctx.fillRect(0, 6, 8, 1);
    ctx.fillStyle = '#c0392b'; ctx.fillRect(8, 0, 1, 5); ctx.fillRect(8, 0, 2, 2);   // le drapeau leve
  } },

  // LE BAC DE RECYCLAGE : bleu, le couvercle entrouvert, du papier qui depasse.
  bac_recyclage: { casse: 0.9, pv: 15, w: 10, h: 12, ancre: [5, 11], r: 3, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(1, 10, 9, 2);
    ctx.fillStyle = '#2b6cb0'; ctx.fillRect(1, 4, 8, 7);                      // la cuve
    ctx.fillStyle = '#3b82c9'; ctx.fillRect(2, 5, 3, 5);
    ctx.fillStyle = '#1f4f80'; ctx.fillRect(0, 2, 10, 2);                     // le couvercle, de travers
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(3, 1, 3, 2); ctx.fillRect(6, 2, 2, 1);   // le papier qui depasse
    ctx.fillStyle = '#ffffff'; ctx.fillRect(4, 7, 2, 2);                      // le logo
  } },

  // LES PALETTES : trois planchers empiles, les blocs qu'on voit entre deux.
  palettes: { casse: 0.85, pv: 20, w: 18, h: 12, ancre: [9, 11], r: 5, sol: [7, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(1, 10, 17, 2);
    for (let i = 0; i < 3; i++) {
      const y = 8 - i * 3;
      ctx.fillStyle = '#a07c4b'; ctx.fillRect(1, y, 16, 1);                   // le plancher
      ctx.fillStyle = '#6e5330'; ctx.fillRect(1, y + 1, 3, 2); ctx.fillRect(7, y + 1, 4, 2); ctx.fillRect(14, y + 1, 3, 2);   // les blocs
    }
    ctx.fillStyle = '#8a6a3f'; ctx.fillRect(1, 2, 16, 1);
  } },

  // LA BENNE : l'acier vert qui arrete un char, le couvercle rabattu, la rouille.
  benne: { arrete: 4, w: 18, h: 16, ancre: [9, 15], r: 6, sol: [8, 4], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.22)'; ctx.fillRect(1, 13, 17, 3);
    ctx.fillStyle = '#2f5a3a'; ctx.fillRect(1, 5, 16, 9);                     // la caisse
    ctx.fillStyle = '#3d6f48'; ctx.fillRect(2, 6, 14, 3);
    ctx.fillStyle = '#244a2e'; ctx.fillRect(0, 2, 18, 4);                     // le couvercle
    ctx.fillStyle = '#35603f'; ctx.fillRect(1, 2, 16, 1);
    ctx.fillStyle = '#1b1f22'; ctx.fillRect(2, 14, 2, 2); ctx.fillRect(14, 14, 2, 2);   // les roulettes
    ctx.fillStyle = '#8f4a22'; ctx.fillRect(12, 8, 1, 5); ctx.fillRect(4, 10, 1, 3);    // la rouille
    ctx.fillStyle = '#d9d6cc'; ctx.fillRect(6, 9, 6, 1);                      // le lettrage efface
  } },
  banc_ouest: { casse: 0.8, pv: 40, w: 10, h: 18, ancre: [5, 16], r: 5, sol: [3, 6], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#5a3f25'; ctx.fillRect(6, 1, 3, 13);                 // le dossier, a l'est
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 3, 4, 12);                 // l'assise
    ctx.fillStyle = '#7d5a36'; ctx.fillRect(2, 3, 4, 1); ctx.fillRect(2, 3, 1, 12); ctx.fillRect(6, 1, 3, 1);
    ctx.fillStyle = '#523a22'; ctx.fillRect(2, 15, 1, 3); ctx.fillRect(5, 15, 1, 3);
  } },
  // ⚠️ L'ABRIBUS : un toit, trois vitres, une reclame et le POTEAU D'ARRET. A
  // seize pixels, c'est le poteau qui le nomme — la plaque blanche et son
  // pictogramme bleu se lisent d'un bout de rue a l'autre, l'abri ne fait que
  // le confirmer. Il est vu de face (`abribus`, ouvert au sud), de dos
  // (`abribus_nord` : la vitre du fond devant, le banc derriere) et de profil.
  // ⚠️ `casse` : c'est du verre, un char lance le traverse — et c'est une
  // cible de plus pour une ville qui se brise.
  // ⚠️ L'EDICULE DU METRO : un pavillon vitre, son escalier qui s'enfonce, et le
  // poteau au « M » jaune de la ligne. C'est le poteau qui le nomme de loin ;
  // de pres, c'est l'escalier qui descend — on voit ou l'on va. Vu de face
  // (`edicule`, on y entre depuis le trottoir au sud) ou de dos (`edicule_nord`).
  // ⚠️ `arrete`, pas `casse` : une entree de metro ne tombe pas sous un char, et
  // un edicule en miettes laisserait une station sans escalier.
  edicule: { arrete: 3.0, w: 24, h: 30, ancre: [12, 23], r: 7, sol: [10, 4], solide: true, peindre: function (ctx, w, h) {
    peindreEdicule(ctx, 'sud');
  } },
  edicule_nord: { arrete: 3.0, w: 24, h: 30, ancre: [12, 23], r: 7, sol: [10, 4], solide: true, peindre: function (ctx, w, h) {
    peindreEdicule(ctx, 'nord');
  } },
  abribus: { casse: 0.6, pv: 70, w: 26, h: 28, ancre: [13, 23], r: 6, sol: [10, 3], solide: true, peindre: function (ctx, w, h) {
    peindreAbribus(ctx, 'sud');
  } },
  abribus_nord: { casse: 0.6, pv: 70, w: 26, h: 28, ancre: [13, 23], r: 6, sol: [10, 3], solide: true, peindre: function (ctx, w, h) {
    peindreAbribus(ctx, 'nord');
  } },
  abribus_est: { casse: 0.6, pv: 70, w: 16, h: 34, ancre: [8, 25], r: 6, sol: [4, 7], solide: true, peindre: function (ctx, w, h) {
    peindreAbribus(ctx, 'est');
  } },
  abribus_ouest: { casse: 0.6, pv: 70, w: 16, h: 34, ancre: [8, 25], r: 6, sol: [4, 7], solide: true, peindre: function (ctx, w, h) {
    peindreAbribus(ctx, 'ouest');
  } },
  caisse: { casse: 0.8, pv: 20, w: 16, h: 16, ancre: [8, 15], r: 6, sol: [7, 4], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#8a6a3f'; ctx.fillRect(1, 2, 14, 14);
    ctx.fillStyle = '#a07c4b'; ctx.fillRect(2, 3, 12, 5);
    ctx.fillStyle = '#6e5330'; ctx.fillRect(1, 8, 14, 1); ctx.fillRect(7, 2, 2, 14);
  } },
  buisson: { casse: 0.9, pv: 15, w: 16, h: 12, ancre: [8, 11], r: 5, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#2f6b2a'; ctx.fillRect(1, 3, 14, 8); ctx.fillRect(3, 1, 10, 3);
    ctx.fillStyle = '#3f8d38'; ctx.fillRect(3, 3, 5, 4); ctx.fillRect(9, 5, 4, 3);
    ctx.fillStyle = '#204d1e'; ctx.fillRect(2, 8, 12, 3);
  } },
  // --- Les traces de la vie de quelqu'un, dans une cour de banlieue --------
  // ⚠️ Un terrain de banlieue est le CONTRAIRE du vide. Ces trois-la le disent
  // en trois formes qu'on reconnait de haut : le TOIT EN PENTE du cabanon, la
  // LIGNE tendue de la corde a linge, le COUVERCLE ROND du BBQ.
  cabanon: { casse: 0.75, pv: 80, w: 20, h: 20, ancre: [10, 19], r: 7, sol: [9, 4], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 6, 16, 13);
    ctx.fillStyle = '#8a6a42'; ctx.fillRect(3, 7, 14, 11);
    ctx.fillStyle = '#4a3a28'; ctx.fillRect(0, 2, 20, 5); ctx.fillRect(9, 0, 2, 3);
    ctx.fillStyle = '#3a2a1a'; ctx.fillRect(8, 10, 5, 9);
    ctx.fillStyle = '#c9a227'; ctx.fillRect(11, 14, 1, 2);
  } },
  corde_a_linge: { casse: 0.9, pv: 10, w: 22, h: 18, ancre: [11, 17], r: 3, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#6f757c'; ctx.fillRect(1, 2, 2, 15); ctx.fillRect(19, 2, 2, 15);
    ctx.fillStyle = '#9aa0a6'; ctx.fillRect(2, 3, 18, 1);
    ctx.fillStyle = '#e8e2cf'; ctx.fillRect(4, 4, 3, 5); ctx.fillRect(12, 4, 4, 6);
    ctx.fillStyle = '#7fb3d8'; ctx.fillRect(8, 4, 3, 4);
  } },
  bbq: { casse: 0.85, pv: 30, w: 14, h: 14, ancre: [7, 13], r: 5, sol: [6, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(4, 9, 2, 5); ctx.fillRect(8, 9, 2, 5);
    ctx.fillStyle = '#2c2c30'; ctx.fillRect(1, 4, 12, 6);
    ctx.fillStyle = '#4a4d54'; ctx.fillRect(2, 2, 10, 3); ctx.fillRect(1, 1, 12, 2);
    ctx.fillStyle = '#c0392b'; ctx.fillRect(6, 0, 2, 1);
  } },
  debris: { w: 14, h: 10, ancre: [7, 9], r: 4, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#6b6258'; ctx.fillRect(1, 5, 12, 5);
    ctx.fillStyle = '#807768'; ctx.fillRect(3, 2, 4, 4); ctx.fillRect(8, 4, 3, 3);
    ctx.fillStyle = '#544c44'; ctx.fillRect(2, 7, 3, 2); ctx.fillRect(9, 7, 4, 2);
  } },

  /* --- CE QU'ON JETTE SUR UN TERRAIN VAGUE ---------------------------------

     ⚠️ Demande de Martin : « des terrains vague un peu salle et avec des
     deches ». Le lot abandonne n'avait qu'UNE sorte de decor — le gravat — et
     un par dix-sept tuiles : de haut, du gazon avec trois points dessus. Trois
     fiches de plus, semees avec lui (`carte.DECHETS`), et ce qui fait la
     salete n'est pas leur nombre mais leur VARIETE : trois tas de gravats se
     lisent comme un motif, un sac creve a cote d'un pneu se lit comme un
     depotoir.

     ⚠️ Chacune est la pour se reconnaitre a douze pixels, et chacune a donc UNE
     silhouette : le sac est mou et bossele, le pneu est un ANNEAU (un disque
     noir serait une flaque), le baril est un cylindre debout avec deux cercles
     de renfort. */

  // LES SACS D'ORDURES. Deux, parce qu'on ne sort jamais un sac tout seul —
  // et l'un des deux est CREVE : ce qui en sort dit qu'il est la depuis
  // longtemps et que personne ne le ramassera.
  ordures: { casse: 0.9, pv: 15, w: 16, h: 14, ancre: [8, 13], r: 5, sol: [7, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.20)'; ctx.fillRect(2, 11, 12, 3);        // son ombre
    ctx.fillStyle = '#2b2b30'; ctx.fillRect(1, 5, 8, 8); ctx.fillRect(2, 3, 6, 3);   // le gros sac
    ctx.fillStyle = '#3b3b42'; ctx.fillRect(2, 5, 5, 4);                      // le pli qui prend le jour
    ctx.fillStyle = '#1d1d21'; ctx.fillRect(3, 2, 3, 2);                      // le noeud, en haut
    ctx.fillStyle = '#35402f'; ctx.fillRect(8, 7, 7, 6); ctx.fillRect(9, 5, 5, 3);   // le vert, plus petit
    ctx.fillStyle = '#44503c'; ctx.fillRect(9, 7, 4, 3);
    ctx.fillStyle = '#c9c3ae'; ctx.fillRect(7, 10, 3, 1); ctx.fillRect(6, 12, 2, 1); // ce qui sort du creve
  } },

  // LE PNEU, couche a plat. ⚠️ Le seul dechet du lot qui ne soit PAS solide :
  // on marche dessus, et un pneu qui arrete un homme de 1,80 m est un pneu de
  // camion. Un ANNEAU, jamais un disque : rempli, il se lit comme une flaque
  // d'huile, et le trou au milieu est tout ce qui le nomme.
  pneu: { casse: 0.95, pv: 10, w: 16, h: 12, ancre: [8, 10], r: 4, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(2, 9, 12, 2);
    ctx.fillStyle = '#26262a'; ctx.fillRect(2, 2, 12, 7); ctx.fillRect(3, 1, 10, 9);
    ctx.fillStyle = '#34343a'; ctx.fillRect(3, 2, 10, 2);                     // le dessus du flanc
    ctx.fillStyle = '#4a4a52';                                                // les crampons
    for (let x = 4; x < 13; x += 3) ctx.fillRect(x, 1, 1, 2);
    ctx.fillStyle = '#5a5240'; ctx.fillRect(6, 4, 4, 3);                      // le trou, plein de terre
    ctx.fillStyle = '#6d6845'; ctx.fillRect(7, 5, 2, 1);
  } },

  // LE BARIL ROUILLE, debout. Deux cercles de renfort et une coulee de
  // rouille : sans eux, un cylindre gris est une poubelle, et la ville en a
  // deja une.
  baril: { casse: 0.75, pv: 45, w: 12, h: 18, ancre: [6, 17], r: 4, sol: [5, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.22)'; ctx.fillRect(1, 15, 10, 3);
    ctx.fillStyle = '#6a4a2c'; ctx.fillRect(1, 4, 10, 13);                    // la robe
    ctx.fillStyle = '#7f5a34'; ctx.fillRect(2, 4, 5, 12);                     // eclairee du nord-ouest
    ctx.fillStyle = '#8a6a3a'; ctx.fillRect(1, 2, 10, 3); ctx.fillRect(2, 1, 8, 2);  // le couvercle, vu d'en haut
    ctx.fillStyle = '#9a7c48'; ctx.fillRect(3, 2, 5, 1);
    ctx.fillStyle = '#4e3620'; ctx.fillRect(1, 7, 10, 1); ctx.fillRect(1, 13, 10, 1);  // les deux cercles
    ctx.fillStyle = '#8f4a22'; ctx.fillRect(8, 5, 1, 7); ctx.fillRect(3, 9, 1, 5);     // la rouille qui coule
  } },

  /* --- CE QUI TRAINE AU PIED DES PLEX ------------------------------------

     ⚠️ Des quartiers qu'on reconnait (demande de Martin : « des cartiers plus
     pauvre et sale »). La saleté des quartiers cossus DESCEND chez les pauvres
     (`salete.py`) — elle ne s'ajoute pas — et sur un trottoir, on ne jette ni
     baril ni caisse : on sort ses sacs, et un matelas le jour du déménagement.
     La poubelle, elle, reste la même : dans un quartier pauvre, elle déborde. */

  // LE MATELAS, couche a plat, jauni, une tache. ⚠️ PAS solide : on marche
  // dessus, comme sur le pneu. Ses boutons de capiton le nomment — sans eux,
  // un rectangle beige est une dalle.
  matelas: { casse: 0.95, pv: 10, w: 22, h: 14, ancre: [11, 13], r: 6, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.16)'; ctx.fillRect(1, 12, 21, 2);        // son ombre
    ctx.fillStyle = '#b9ad93'; ctx.fillRect(1, 3, 20, 9);                     // la toile, jaunie
    ctx.fillStyle = '#cfc4a8'; ctx.fillRect(2, 4, 18, 3);                     // le dessus qui prend le jour
    ctx.fillStyle = '#9c9078'; ctx.fillRect(1, 3, 20, 1); ctx.fillRect(1, 11, 20, 1);  // les bords piques
    ctx.fillStyle = '#a89c82';                                                // le capiton
    for (let x = 5; x < 20; x += 5) { ctx.fillRect(x, 5, 1, 1); ctx.fillRect(x, 9, 1, 1); }
    ctx.fillStyle = '#8a7652'; ctx.fillRect(12, 6, 5, 3); ctx.fillRect(13, 9, 3, 1);   // la tache
  } },

  // LE CADDIE RENVERSE, couche sur le flanc : les roues en l'air, la poignee
  // rouge qui depasse. Du fil de fer, jamais un bloc plein — plein, c'est une
  // caisse grise.
  caddie: { casse: 0.9, pv: 20, w: 18, h: 12, ancre: [9, 11], r: 5, sol: [8, 3], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.18)'; ctx.fillRect(1, 10, 16, 2);        // son ombre
    ctx.fillStyle = '#9aa0a6';                                                // le panier, en fil de fer
    ctx.fillRect(2, 3, 12, 1); ctx.fillRect(2, 9, 12, 1); ctx.fillRect(2, 3, 1, 7); ctx.fillRect(13, 3, 1, 7);
    ctx.fillRect(2, 6, 12, 1);
    for (let x = 5; x < 13; x += 3) ctx.fillRect(x, 3, 1, 7);                 // le grillage
    ctx.fillStyle = '#6f757c'; ctx.fillRect(14, 4, 1, 5);                     // le montant de la poignee
    ctx.fillStyle = '#c0392b'; ctx.fillRect(14, 2, 3, 2);                     // la poignee rouge
    ctx.fillStyle = '#26262a'; ctx.fillRect(3, 1, 2, 2); ctx.fillRect(10, 1, 2, 2);   // les roues, vers le ciel
  } },

  // LA POUBELLE QUI DEBORDE : la cuve de `poubelle`, le couvercle de travers, un
  // sac qui depasse et un autre au pied. ⚠️ Ce n'est pas un decor de plus : c'est
  // la MEME poubelle, dans un quartier pauvre (`salete.deplacer` la change).
  poubelle_pleine: { casse: 0.85, pv: 25, w: 14, h: 16, ancre: [6, 15], r: 4, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.20)'; ctx.fillRect(1, 14, 13, 2);        // son ombre
    ctx.fillStyle = '#3f4a3c'; ctx.fillRect(2, 5, 8, 11);                     // la cuve
    ctx.fillStyle = '#4c5a48'; ctx.fillRect(3, 6, 6, 9);
    ctx.fillStyle = '#2b2b30'; ctx.fillRect(3, 1, 6, 5); ctx.fillRect(5, 0, 2, 1);   // le sac qui depasse
    ctx.fillStyle = '#3b3b42'; ctx.fillRect(4, 2, 2, 2);
    ctx.fillStyle = '#2b332a'; ctx.fillRect(0, 3, 5, 2); ctx.fillRect(5, 7, 1, 8);   // le couvercle de travers
    ctx.fillStyle = '#35402f'; ctx.fillRect(9, 11, 5, 5); ctx.fillRect(10, 10, 3, 1); // le sac vert au pied
    ctx.fillStyle = '#c9c3ae'; ctx.fillRect(8, 15, 2, 1); ctx.fillRect(11, 9, 1, 1);  // ce qui en sort
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
  kiosque_journaux: { casse: 0.6, pv: 90, w: 24, h: 26, ancre: [12, 25], r: 9, sol: [10, 3], solide: true, peindre: function (ctx, w, h) {
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
  /* ⚠️ UN FEU QUEBECOIS SUR SA POTENCE.

     HORIZONTAL, et ses lentilles ont des FORMES — le rouge CARRE, le jaune en
     LOSANGE, le vert ROND. Ce n'est pas une licence de pixel art, c'est la
     signalisation d'ici : le Quebec la pose depuis des decennies (le
     Nouveau-Brunswick, la Nouvelle-Ecosse, l'Ile-du-Prince-Edouard et l'est de
     l'Ontario ont suivi), et la forme est la pour qui ne distingue pas le
     rouge du vert. Elle rend un service de plus a 480 x 270 : a TROIS PIXELS,
     une forme se lit quand une teinte se devine.

     ⚠️ ET LE MAT NE PORTE PAS SES TETES SUR LA TETE. Il les tient PAR UN
     BOUT, et le reste porte a faux AU-DESSUS DE LA CHAUSSEE — c'est une
     potence, et c'est ce qui fait qu'un feu se voit du milieu de la rue et pas
     seulement du trottoir. Le poteau est donc a une extremite, jamais au
     milieu, et le bras part vers le croisement (`COINS`, dans vehicules.js).

     ⚠️ UN SEUL GABARIT, ET UN MIROIR. Tout est ecrit « bras vers l'est » ; un
     mat tourne vers l'ouest se peint avec les memes nombres passes par
     `miroir()`. Deux jeux de coordonnees, c'est un jeu qui derive le jour ou
     l'on bouge une lentille.

     ⚠️ Et le miroir RETOURNE L'ORDRE DES LENTILLES — rouge a droite au lieu de
     gauche. C'est juste : le rouge est a gauche DU CONDUCTEUR, et deux tetes
     qui regardent des sens opposes se voient a l'envers l'une de l'autre vues
     d'en haut. Les douilles eteintes suivent, donc chaque tete reste lisible
     pour elle-meme.

     La fiche ne cuit que le mat, le boitier et les TROIS DOUILLES ETEINTES,
     chacune dans un ton tres sombre de sa couleur : c'est ce qui fait qu'on
     voit qu'il y a trois feux, et laquelle est allumee. La lentille vive, elle,
     se peint a la volee (`dessinerFeu`) — un seul feu a la fois. */
  feu: {
    w: 17, h: 24, ancre: [2, 23], ancreMiroir: [14, 23], r: 2, solide: false,
    //: Le gabarit, en « bras vers l'est ». `dessinerFeu` et son juge le LISENT
    //: ici : personne ne recopie ces nombres.
    mat: { x: 1, l: 3 },
    boitier: { x: 4, y: 1, l: 13, h: 5 },
    lentilles: [5, 9, 13], lentilleY: 2, lentilleCote: 3,
    tete: { x: 4, y: 8, h: 7 },          // la tete pieton, sous le bras, meme bord
    peindre: function (ctx, w, h) { peindreFeu(ctx, w, 1); },
    peindreMiroir: function (ctx, w, h) { peindreFeu(ctx, w, -1); },
  },
  // ⚠️ PLUS PETIT QUE LE FEU DES CHARS, et c'est voulu : a 480 x 270 il se lit
  // par sa COULEUR et sa FORME, jamais par son detail. Un boitier haut comme
  // celui des autos, trois cent cinquante fois dans la ville, mangerait la rue.
  feu_pieton: { w: 6, h: 18, ancre: [3, 17], r: 1, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#2c2c30'; ctx.fillRect(0, 0, 6, 7);          // la lanterne se peint a la volee
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(2, 7, 2, 10); ctx.fillRect(1, 16, 4, 2);
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
  // ⚠️ LE REMOUS REMPLACE L'OMBRE quand on nage, et il fait deux choses d'un
  // coup : il dit ou est la ligne d'eau (le corps est coupe juste au-dessus) et
  // il rend le nageur lisible sur un fond qui est de la meme couleur que lui.
  // Une tete sans remous sur la baie, on ne la voit pas.
  remous: { w: 14, h: 7, ancre: [7, 3], r: 0, solide: false, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(232,244,252,0.55)';
    ctx.fillRect(3, 1, 8, 1); ctx.fillRect(1, 3, 12, 1); ctx.fillRect(4, 5, 6, 1);
    ctx.fillStyle = 'rgba(120,170,200,0.45)';
    ctx.fillRect(2, 2, 10, 1); ctx.fillRect(3, 4, 8, 1);
  } },

  // --- Ça travaille : les machines de chantier (voir `app/chantiers.py`) -----------
  // ⚠️ Du DECOR ANIME, pas des vehicules : la refonte des chars interdit d'en
  // ajouter avant elle. Elles ne roulent pas, elles TRAVAILLENT — une
  // articulation chacune, cuite une fois par pose (`anime`), exactement comme
  // les manèges. Et elles ARRETENT un char sans jamais tomber (`arrete`) : une
  // pelle mecanique qu'on renverse au pistolet, ce serait une farce.
  tas_de_terre: { arrete: 3.0, w: 24, h: 14, ancre: [12, 12], r: 6, sol: [9, 4], solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = 'rgba(20,18,26,0.26)'; ctx.fillRect(1, 10, 22, 4);
    ctx.fillStyle = '#5e4128'; ctx.fillRect(1, 7, 22, 5); ctx.fillRect(3, 5, 18, 3);
    ctx.fillStyle = '#7a5a36'; ctx.fillRect(5, 3, 14, 4); ctx.fillRect(8, 1, 8, 3);
    ctx.fillStyle = '#8f6c44'; ctx.fillRect(9, 2, 5, 2); ctx.fillRect(6, 5, 5, 1);
    ctx.fillStyle = '#9a9689'; ctx.fillRect(4, 9, 2, 1); ctx.fillRect(15, 8, 2, 2); ctx.fillRect(18, 10, 1, 1);
  } },
  // La pelle : le bras monte, le godet racle, le bras redescend. Six poses
  // aller-retour, jamais un saut du haut au bas.
  pelleteuse: { anime: 9, arrete: 6.0, w: 40, h: 30, ancre: [16, 26], r: 8, sol: [9, 6], solide: true, variantes: 6, travaille: 'jour', racle: 0, peindre: function (ctx, w, h, v) {
    const trait = function (x0, y0, x1, y1, e, c) {
      ctx.fillStyle = c;
      const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0), 1);
      for (let k = 0; k <= n; k++) {
        ctx.fillRect(Math.round(x0 + (x1 - x0) * k / n), Math.round(y0 + (y1 - y0) * k / n), e, e);
      }
    };
    const leve = [0, 1, 2, 3, 2, 1][v % 6];
    ctx.fillStyle = 'rgba(20,18,26,0.28)'; ctx.fillRect(1, 25, 30, 5);
    // Les chenilles.
    ctx.fillStyle = '#2c2c30'; ctx.fillRect(2, 19, 26, 8);
    ctx.fillStyle = '#4a4d55'; for (let x = 3; x < 28; x += 3) ctx.fillRect(x, 20, 1, 6);
    // La caisse, le contrepoids, la cabine.
    ctx.fillStyle = '#c8961e'; ctx.fillRect(4, 11, 20, 9);
    ctx.fillStyle = '#e2b12c'; ctx.fillRect(4, 11, 20, 2);
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(0, 13, 5, 6);
    ctx.fillStyle = '#e2b12c'; ctx.fillRect(6, 3, 10, 9);
    ctx.fillStyle = '#243447'; ctx.fillRect(8, 5, 6, 4);
    ctx.fillStyle = '#7fb3d8'; ctx.fillRect(9, 5, 2, 2);
    // Le bras : la fleche monte vers le coude, le balancier descend au godet.
    const coudeX = 30, coudeY = 6 - leve * 2;
    const godetX = 34, godetY = 18 - leve * 4;
    trait(21, 13, coudeX, coudeY, 3, '#c8961e');
    trait(coudeX, coudeY, godetX, godetY, 2, '#a87c16');
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(godetX - 3, godetY, 7, 5);
    ctx.fillStyle = '#5f6267'; ctx.fillRect(godetX - 3, godetY + 4, 1, 2); ctx.fillRect(godetX, godetY + 4, 1, 2); ctx.fillRect(godetX + 3, godetY + 4, 1, 2);
    if (leve === 0) { ctx.fillStyle = '#6e5330'; ctx.fillRect(godetX - 5, godetY + 5, 10, 2); }
  } },
  // La boule : elle recule, part et FRAPPE le mur (voir `BOULE`). ⚠️ Deux
  // fiches pour une machine : Python dit de quel côté est la moitié debout
  // (`sens`), et la grue tournée vers l'ouest est le MIROIR exact de l'autre —
  // l'ancre aussi, pour que la machine reste sur sa tuile.
  // ⚠️ `travaille: 'jour'` : la nuit, elle s'arrête à sa pose de repos.
  grue_a_boule: { anime: 10, arrete: 8.0, w: 50, h: 54, ancre: [14, 50], r: 8, sol: [9, 6], solide: true, variantes: 16, travaille: 'jour', frappe: BOULE.frappe, peindre: peindreGrueABoule },
  grue_a_boule_ouest: { anime: 10, arrete: 8.0, w: 50, h: 54, ancre: [36, 50], r: 8, sol: [9, 6], solide: true, variantes: 16, travaille: 'jour', frappe: BOULE.frappe, peindre: function (ctx, w, h, v) {
    peindreGrueABoule(miroirX(ctx, w), w, h, v);
  } },
  // La grue a tour : sa fleche TOURNE, lentement, seize poses pour un tour.
  // ⚠️ Vue de trois-quarts : un cercle couche se lit en ellipse, alors la
  // fleche fait quatre fois moins de chemin en hauteur qu'en largeur.
  grue: { anime: 20, arrete: 9.0, w: 112, h: 94, ancre: [56, 90], r: 7, sol: [7, 6], solide: true, variantes: 16, travaille: 'jour', peindre: function (ctx, w, h, v) {
    const trait = function (x0, y0, x1, y1, e, c) {
      ctx.fillStyle = c;
      const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0), 1);
      for (let k = 0; k <= n; k++) {
        ctx.fillRect(Math.round(x0 + (x1 - x0) * k / n), Math.round(y0 + (y1 - y0) * k / n), e, e);
      }
    };
    const pivotX = 56, pivotY = 20;
    const t = v / 16 * Math.PI * 2;
    const devant = Math.sin(t) >= 0;         // la fleche passe devant ou derriere le mat
    const bout = { x: pivotX + Math.cos(t) * 50, y: pivotY + Math.sin(t) * 12 };
    const queue = { x: pivotX - Math.cos(t) * 18, y: pivotY - Math.sin(t) * 4 };
    const fleche = function () {
      trait(pivotX, pivotY, bout.x, bout.y, 2, '#e2b12c');
      trait(pivotX, pivotY, queue.x, queue.y, 2, '#c8961e');
      ctx.fillStyle = '#5f6267'; ctx.fillRect(Math.round(queue.x) - 3, Math.round(queue.y) - 1, 6, 5);
      // Le chariot et son crochet, aux deux tiers de la fleche.
      const cx = Math.round(pivotX + (bout.x - pivotX) * 0.66), cy = Math.round(pivotY + (bout.y - pivotY) * 0.66);
      trait(cx, cy + 1, cx, cy + 16, 1, '#3a3d44');
      ctx.fillStyle = '#3a3d44'; ctx.fillRect(cx - 1, cy + 16, 3, 2);
    };
    ctx.fillStyle = 'rgba(20,18,26,0.26)'; ctx.fillRect(46, 88, 22, 5);
    if (!devant) fleche();
    // Le mat en treillis et son lest de beton.
    ctx.fillStyle = '#9a9689'; ctx.fillRect(48, 82, 16, 9);
    ctx.fillStyle = '#b3afa2'; ctx.fillRect(48, 82, 16, 2);
    ctx.fillStyle = '#e2b12c'; ctx.fillRect(53, 24, 2, 58); ctx.fillRect(59, 24, 2, 58);
    for (let y = 26; y < 82; y += 6) trait(54, y, 59, y + 5, 1, '#c8961e');
    ctx.fillStyle = '#c8961e'; ctx.fillRect(51, 16, 12, 8);
    ctx.fillStyle = '#243447'; ctx.fillRect(53, 18, 5, 4);
    if (devant) fleche();
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
  // Le poing americain des hommes de Sal, PAR TERRE et dans la roue : quatre
  // anneaux d'acier sur la barre qui s'arrondit sous la paume. A seize pixels,
  // ce sont les TROUS qui le nomment — sans eux, c'est la barre grise du defaut.
  // ⚠️ Cerne de noir et les trous sombres : l'acier est du gris du trottoir, et
  // le premier dessin (12 x 6, sans contour) n'y etait qu'une dalle pale qu'on
  // ne voyait pas tomber. Dans la main, c'est un AUTRE dessin (`EN_MAIN`).
  poing_americain: function (ctx) {
    peindreGrilleDecor(ctx, { k: '#24262c', m: '#9aa0a8', l: '#d9dcdf', d: '#6b7079', o: '#3a3d44' }, [
      '................',
      '...kk.kk.kk.kk..',
      '..kllkllkllkllk.',
      '.kmoomoomoomoomk',
      '.kmoomoomoomoomk',
      '.kmmmmmmmmmmmmmk',
      '..kmlllllllllmk.',
      '...kdddddddddk..',
      '....kkkkkkkkk...',
      '................',
    ]);
  },
  batte: function (ctx) { ctx.fillStyle = '#8a6a3f'; ctx.fillRect(2, 5, 12, 2); ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 5, 4, 2); },
  couteau: function (ctx) { ctx.fillStyle = '#c9cdd4'; ctx.fillRect(5, 5, 8, 2); ctx.fillStyle = '#3d2a1c'; ctx.fillRect(2, 5, 3, 2); },
  pistolet: function (ctx) { ctx.fillStyle = '#3a3d44'; ctx.fillRect(3, 4, 8, 3); ctx.fillRect(4, 6, 3, 3); },
  fusil: function (ctx) { ctx.fillStyle = '#3a3d44'; ctx.fillRect(2, 4, 12, 2); ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 4, 4, 3); },
  fronde: function (ctx) { ctx.fillStyle = '#6b4b2c'; ctx.fillRect(6, 3, 2, 6); ctx.fillRect(4, 3, 6, 2); ctx.fillStyle = '#c0392b'; ctx.fillRect(4, 6, 6, 1); },
  extincteur: function (ctx) { ctx.fillStyle = '#c0392b'; ctx.fillRect(5, 2, 5, 7); ctx.fillStyle = '#3a3d44'; ctx.fillRect(6, 0, 3, 2); },
  pelle: function (ctx) { ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 5, 9, 2); ctx.fillStyle = '#9aa0a8'; ctx.fillRect(11, 3, 4, 6); },
  cone: function (ctx) { ctx.fillStyle = '#d98324'; ctx.fillRect(6, 2, 4, 7); ctx.fillRect(4, 8, 8, 2); ctx.fillStyle = '#efe6d0'; ctx.fillRect(6, 5, 4, 1); },
  bouteille: function (ctx) { ctx.fillStyle = '#2f6b2a'; ctx.fillRect(5, 3, 4, 6); ctx.fillRect(6, 1, 2, 2); },
  // Les trois du marche noir. A seize pixels, ce qui les nomme : le chargeur
  // qui pend sous la mitraillette, la crosse de bois et le long canon de la
  // carabine, le chiffon allume au goulot du Molotov.
  mitraillette: function (ctx) { ctx.fillStyle = '#3a3d44'; ctx.fillRect(2, 4, 11, 2); ctx.fillRect(6, 6, 2, 4); ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 6, 2, 2); },
  carabine: function (ctx) { ctx.fillStyle = '#6b4b2c'; ctx.fillRect(1, 5, 6, 2); ctx.fillRect(2, 7, 2, 2); ctx.fillStyle = '#3a3d44'; ctx.fillRect(6, 4, 10, 2); ctx.fillStyle = '#9aa0a8'; ctx.fillRect(8, 2, 3, 1); },
  molotov: function (ctx) { ctx.fillStyle = '#2f6b2a'; ctx.fillRect(5, 3, 4, 6); ctx.fillRect(6, 1, 2, 2); ctx.fillStyle = '#efe6d0'; ctx.fillRect(6, 0, 2, 1); ctx.fillStyle = '#ff8c1a'; ctx.fillRect(8, 0, 1, 1); ctx.fillStyle = '#ffd23a'; ctx.fillRect(9, 1, 1, 1); },
  // La liasse d'un guichet defonce : du vert, une bande de papier, une
  // deuxieme liasse qui depasse — a seize pixels, c'est la couleur qui la nomme.
  billets: function (ctx) { ctx.fillStyle = '#2f6b2a'; ctx.fillRect(5, 2, 9, 5); ctx.fillStyle = '#3f8d38'; ctx.fillRect(3, 4, 9, 5); ctx.fillStyle = '#9adf7a'; ctx.fillRect(4, 5, 7, 1); ctx.fillStyle = '#e8e6de'; ctx.fillRect(7, 4, 2, 5); },
  // Ce qu'une distributrice defoncee crache. La MONNAIE : trois pieces, de
  // l'argent et du cuivre — surtout pas le vert d'une liasse, on la
  // confondrait avec la caisse d'un guichet. La CANETTE couchee, et le SAC de
  // chips froisse.
  monnaie: function (ctx) { ctx.fillStyle = '#9aa0a8'; ctx.fillRect(4, 4, 4, 3); ctx.fillStyle = '#d9dcdf'; ctx.fillRect(4, 4, 3, 2); ctx.fillStyle = '#b87333'; ctx.fillRect(8, 6, 4, 3); ctx.fillStyle = '#e0a060'; ctx.fillRect(8, 6, 3, 2); ctx.fillStyle = '#c9ccd2'; ctx.fillRect(10, 2, 3, 3); },
  canette: function (ctx) { ctx.fillStyle = '#8a241e'; ctx.fillRect(4, 4, 8, 4); ctx.fillStyle = '#c0392b'; ctx.fillRect(4, 4, 8, 2); ctx.fillStyle = '#f3efe6'; ctx.fillRect(6, 5, 3, 1); ctx.fillStyle = '#c9ccd2'; ctx.fillRect(12, 4, 1, 4); },
  sac: function (ctx) { ctx.fillStyle = '#c79a12'; ctx.fillRect(4, 2, 8, 7); ctx.fillStyle = '#f1c40f'; ctx.fillRect(4, 2, 7, 5); ctx.fillStyle = '#c0392b'; ctx.fillRect(5, 4, 5, 2); ctx.fillStyle = '#e8e6de'; ctx.fillRect(4, 2, 8, 1); },
};

/* Ce qu'on voit DANS LA MAIN quand ce n'est pas l'objet du sol. Meme toile
   16 x 10 et meme prise que `OBJETS` : le pixel (2, 5) tombe sur la main de la
   pose (`SPRITES.joueur.mains`), et l'arme pointe vers +x. Une arme absente
   d'ici se tient telle qu'elle se ramasse. */
const EN_MAIN = {
  // Le poing americain : un bout gris sur les jointures, et rien d'autre
  // (Martin : « seulement un tip gris au bout des poings »). Tenu, le dessin du
  // sol depassait du poing comme une planche, aussi large que le torse.
  poing_americain: function (ctx) { ctx.fillStyle = '#9aa0a8'; ctx.fillRect(2, 4, 1, 3); ctx.fillStyle = '#d9dcdf'; ctx.fillRect(3, 4, 1, 3); },
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
  '★': '010111111011101', '♥': '101111111010000',
  '>': '100010001010100', '<': '001010100010001', '·': '000000010000000', '=': '000111000111000',
  '|': '010010010010010', '_': '000000000000111', '[': '110100100100110', ']': '011001001001011',
};

/* Les accents de la police pixel : deux rangs de 3 (6 bits, ligne par ligne),
   poses sur la lettre de BASE a `dy` rangs de son haut. Au-dessus, `dy` = -3 :
   un rang vide separe l'accent de la lettre — colle, un Ê se lisait comme un E
   plus grand et un Î comme un I plus haut. Dessous, la cedille (`dy` = 5).
   La cle est le caractere COMBINANT de la decomposition (NFD) : « É » = « E »
   + U+0301. Une marque absente d'ici tombe, et la lettre reste. */
const MARQUES_PIXEL = {
  '\u0301': { dy: -3, bits: '001010' },   // aigu        É
  '\u0300': { dy: -3, bits: '100010' },   // grave       À È Ù
  '\u0302': { dy: -3, bits: '010101' },   // circonflexe Â Ê Î Ô Û
  '\u0308': { dy: -2, bits: '101000' },   // trema       Ë Ï Ü Ÿ
  '\u0327': { dy: 5, bits: '010110' },    // cedille     Ç
};
