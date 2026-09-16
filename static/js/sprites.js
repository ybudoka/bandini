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

/* --- Le parc : trois dessins, et c'est LE TOIT QUI ROULE ---------------------

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

const AUTO_COTE = [
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '............kCCCCCCk............',
      '...........kGGvvkGGvk...........',
      '..........kkvvvEkvvEk...........',
      '....kCCCCCCccccccccccCCCCCCk....',
      '..kttcccccccccccccDccccccccllk..',
      '..kcccyyyyyyyyyyyyDyyyyyyyccck..',
      '..kcccxcxcxcxcxcxcDcxcxcxcccck..',
      '..kBBBkkkkkDDDDDDDDDDkkkkkBBBk..',
      '.......kkk............kkk.......',
      '......krMrk..........krMrk......',
      '......krrrk..........krrrk......',
      '.......kkk............kkk.......',
      '................................',
      '................................',
    ];
/* LA CHALOUPE — la dette nommee depuis M3, payee le 16 sept. 2026.

   ⚠️ `phase: 2` voulait dire « sans sprite et sans trafic » : `vehicules.py`
   declarait la coque depuis M3 (eau, friction 0,995, adherence 0,05, trois
   cercles) et personne ne l'avait jamais dessinee. Ce qui la nomme vu d'en
   haut : la PROUE POINTUE au nord, le tableau carre au sud, et le hors-bord
   qui depasse derriere — une coque au trait droit se lit comme une caisse.

   ⚠️ `cote` est dessinee comme pour tous les autres, et NON DESSINEE comme
   pour tous les autres : depuis la refonte, c'est `haut` qui tourne (32 caps)
   et l'elevation ne sert plus qu'a etre mesuree. Le juge du parc la lit pour
   chaque vehicule — une coque sans profil le faisait planter, et « tous sauf
   un » est exactement le genre d'exception qui se paie plus tard. */
const BATEAU_COTE = [
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '..............lll...............',
      '..........kkkkkkkkkkk...........',
      '..........vvvvvvvvvvvcccc.......',
      '..........CCCCCCCCCCCcccc.......',
      '....kkkkkkkkkkkkkkkkkkkkkkkk....',
      '..kcccccccccccccccccccccccckkkk.',
      '..kcccccccccccccccccccccccckrrr.',
      '..kcccccccccccccccccccccccck.kk.',
      '...kccccccccccccccccccccccck.k..',
      '...kccccccccccccccccccccccck.r..',
      '...kccccccccccccccccccccccck....',
      '....kcccccccccccccccccccccck....',
      '....kcccccccccccccccccccccck....',
      '.....kccccccccccccccccccccck....',
      '......kkkkkkkkkkkkkkkkkkkkkk....',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
      '................................',
];
const BATEAU_HAUT = [
      '................................',
      '..............kCCk..............',
      '..............kllk..............',
      '.............kCccCk.............',
      '.............kCccCk.............',
      '............kCccccCk............',
      '............kCccccCk............',
      '...........kCccccccCk...........',
      '...........kCccccccCk...........',
      '..........kCccccccccCk..........',
      '..........kCccccccccCk..........',
      '..........kCccccccccCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCvvvvvvvvCk..........',
      '..........kCvvvvvvvvCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDccccDDCk..........',
      '..........kCDDccccDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDrrDDrrDCk..........',
      '..........kCDrrDDrrDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCccccccccCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCttDDDDttCk..........',
      '..........kCcckkkkccCk..........',
      '..........kCcccrrcccCk..........',
      '..........kCccccccccCk..........',
      '................................',
];
const BATEAU_BAS = [
      '................................',
      '..........kCccccccccCk..........',
      '..........kCcccrrcccCk..........',
      '..........kCcckkkkccCk..........',
      '..........kCttDDDDttCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCccccccccCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDrrDDrrDCk..........',
      '..........kCDrrDDrrDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDccccDDCk..........',
      '..........kCDDccccDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCvvvvvvvvCk..........',
      '..........kCvvvvvvvvCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCDDDDDDDDCk..........',
      '..........kCccccccccCk..........',
      '..........kCccccccccCk..........',
      '..........kCccccccccCk..........',
      '...........kCccccccCk...........',
      '...........kCccccccCk...........',
      '............kCccccCk............',
      '............kCccccCk............',
      '.............kCccCk.............',
      '.............kCccCk.............',
      '..............kllk..............',
      '..............kCCk..............',
      '................................',
];

const AUTO_HAUT = [
      '................................',
      '............kBBBBBBk............',
      '...........kCccccccDk...........',
      '..........kCccccccccDk..........',
      '.........kCccccccccccDk.........',
      '........kCccccccccccccDk........',
      '........kCccccccccccccDk........',
      '........kCccccccccccccDk........',
      '.......rkCccccccccccccDkr.......',
      '.......rkCccccccccccccDkr.......',
      '........kDDDDDDDDDDDDDDk........',
      '........kCcDGvvvvvvEDcDk........',
      '........kCcDvvvvvvvvDcDk........',
      '........kCcDCCCCCCCCDcDk........',
      '........kCcDCCCCCCCCDcDk........',
      '........kCcDCCCCCCCCDcDk........',
      '........kCcDCCCCCCCCDcDk........',
      '........kCcDCCCCCCCCDcDk........',
      '........kCcDvvvvvvvvDcDk........',
      '........kCcDGvvvvvvEDcDk........',
      '........kDDDDDDDDDDDDDDk........',
      '.......rkCccccccccccccDkr.......',
      '.......rkCccccccccccccDkr.......',
      '........kCccccccccccccDk........',
      '........kCccccccccccccDk........',
      '.........kCccccccccccDk.........',
      '.........kttccccccccttk.........',
      '..........ktkkkkkkkktk..........',
      '...........kBBBBBBBBk...........',
      '................................',
      '................................',
    ];
const AUTO_BAS = [
      '................................',
      '............kBBBBBBk............',
      '...........kCccccccDk...........',
      '..........kCccccccccDk..........',
      '.........kCccccccccccDk.........',
      '........kCccccccccccccDk........',
      '........kCccccccccccccDk........',
      '........kCccccccccccccDk........',
      '.......rkCccccccccccccDkr.......',
      '.......rkCccccccccccccDkr.......',
      '........kDDDDDDDDDDDDDDk........',
      '........kCcDGvvvvvvEDcDk........',
      '........kCcDvvvvvvvvDcDk........',
      '........kCcDCCCCCCCCDcDk........',
      '........kCcDCCCCCCCCDcDk........',
      '........kCcDCCCCCCCCDcDk........',
      '........kCcDCCCCCCCCDcDk........',
      '........kCcDCCCCCCCCDcDk........',
      '........kCcDvvvvvvvvDcDk........',
      '........kCcDGvvvvvvEDcDk........',
      '........kDDDDDDDDDDDDDDk........',
      '.......rkCccccccccccccDkr.......',
      '.......rkCccccccccccccDkr.......',
      '........kCccccccccccccDk........',
      '........kCccccccccccccDk........',
      '.........kCccccccccccDk.........',
      '.........kllccccccccllk.........',
      '..........klkkkkkkkklk..........',
      '...........kBBBBBBBBk...........',
      '................................',
      '................................',
    ];
const VELO_COTE = [
      '....................',
      '....................',
      '....................',
      '....................',
      '....................',
      '....................',
      '....................',
      '....................',
      '.............kkk....',
      '.......kkk.....k....',
      '.....k...cc....kl...',
      '...krrrcccccccrrrk..',
      '..krrrcccc.ccccrrrk.',
      '..krrMrrk...krrMrrk.',
      '..krrrrrk...krrrrrk.',
      '...krrrk.....krrrk..',
      '.....k.........k....',
      '....................',
      '....................',
    ];
const VELO_HAUT = [
      '....................',
      '........krk.........',
      '........krk.........',
      '........kMk.........',
      '........krk.........',
      '.....kkkkkkkkk......',
      '........kck.........',
      '........kck.........',
      '........kcck........',
      '.......kccck........',
      '.......kcccck.......',
      '.......kcccck.......',
      '........kcck........',
      '........krk.........',
      '........kMk.........',
      '........krk.........',
      '........ktk.........',
      '....................',
      '....................',
    ];
const VELO_BAS = [
      '....................',
      '........ktk.........',
      '........krk.........',
      '........kMk.........',
      '........krk.........',
      '........kcck........',
      '.......kcccck.......',
      '.......kcccck.......',
      '.......kccck........',
      '........kcck........',
      '........kck.........',
      '........kck.........',
      '.....kkkkkkkkk......',
      '........krk.........',
      '........kMk.........',
      '........krk.........',
      '........klk.........',
      '....................',
      '....................',
    ];
const MOTO_COTE = [
      '........................',
      '........................',
      '........................',
      '........................',
      '........................',
      '........................',
      '........................',
      '........................',
      '........................',
      '........................',
      '........................',
      '........................',
      '...............kkkkk....',
      '..................kll...',
      '.....k.kkkkk....kk.k....',
      '...krrrtkCCCCCCk.kkrrk..',
      '..krrrrrkcccccckkrkrrrk.',
      '..krrMrrkDDDDDDkkrrMrrk.',
      '..krrrrrMMMMMMM.krrrrrk.',
      '...krrrk.........krrrk..',
      '.....k.............k....',
      '........................',
      '........................',
    ];
const MOTO_HAUT = [
      '........................',
      '..........kck...........',
      '..........krk...........',
      '..........krk...........',
      '..........kMk...........',
      '..........krk...........',
      '.......kkcccccckk.......',
      '......kkkkkkkkkkkk......',
      '..........kcck..........',
      '.........kccck..........',
      '........kccccck.........',
      '........kCCCCCk.........',
      '........kccccck.........',
      '.........kcccck.........',
      '.........kcccck.........',
      '..........kcck..........',
      '..........kck...........',
      '..........krk...........',
      '..........kMk...........',
      '..........krk...........',
      '..........ktk...........',
      '........................',
      '........................',
    ];
const MOTO_BAS = [
      '........................',
      '..........ktk...........',
      '..........krk...........',
      '..........kMk...........',
      '..........krk...........',
      '..........kck...........',
      '..........kcck..........',
      '.........kcccck.........',
      '.........kcccck.........',
      '........kccccck.........',
      '........kCCCCCk.........',
      '........kccccck.........',
      '.........kccck..........',
      '..........kcck..........',
      '......kkkkkkkkkkkk......',
      '.......kkcccccckk.......',
      '..........krk...........',
      '..........kMk...........',
      '..........krk...........',
      '..........krk...........',
      '..........klk...........',
      '........................',
      '........................',
    ];
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
   miroite en `assis_gauche` / `assis_droite` par le suffixe, comme la marche. */
SPRITES.joueur.poses.assis_cote = [ASSIS_COTE];
SPRITES.joueur.poses.assis_haut = [ASSIS_HAUT];
SPRITES.joueur.poses.assis_bas = [ASSIS_BAS];
const SPORT_COTE = [
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '..............................',
      '............kCCCCCCCk.........',
      '..........kkGGvvvvvvEk........',
      '...kCCCCCCCcccccccccccCCCCk...',
      '..kttccccccccccccccccccccllk..',
      '..kBBkrrrkDDDDDDDDDDkrrrkBBk..',
      '.....krMrk..........krMrk.....',
      '.....krrrk..........krrrk.....',
      '......kkk............kkk......',
      '..............................',
      '..............................',
    ];
const SPORT_HAUT = [
      '..............................',
      '...........kBBBBBk............',
      '..........kCcccccDk...........',
      '.........kCcccccccDk..........',
      '........kCcccccccccDk.........',
      '.......kCcccccccccccDk........',
      '.......kCcccccccccccDk........',
      '.......kCcccccccccccDk........',
      '.......kCcccccccccccDk........',
      '......rkCcccccccccccDkr.......',
      '......rkCcccccccccccDkr.......',
      '.......kDDDDDDDDDDDDDk........',
      '.......kCcDGvvvvvEDcDk........',
      '.......kCcDvvvvvvvDcDk........',
      '.......kCcDCCCCCCCDcDk........',
      '.......kCcDCCCCCCCDcDk........',
      '.......kCcDCCCCCCCDcDk........',
      '.......kCcDvvvvvvvDcDk........',
      '.......kCcDGvvvvvEDcDk........',
      '.......kDDDDDDDDDDDDDk........',
      '......rkCcccccccccccDkr.......',
      '......rkCcccccccccccDkr.......',
      '.......kCcccccccccccDk........',
      '........kCcccccccccDk.........',
      '........kttcccccccttk.........',
      '.........ktkkkkkkktk..........',
      '..........kBBBBBBBk...........',
      '..............................',
      '..............................',
    ];
const SPORT_BAS = [
      '..............................',
      '...........kBBBBBk............',
      '..........kCcccccDk...........',
      '.........kCcccccccDk..........',
      '........kCcccccccccDk.........',
      '.......kCcccccccccccDk........',
      '.......kCcccccccccccDk........',
      '.......kCcccccccccccDk........',
      '.......kCcccccccccccDk........',
      '......rkCcccccccccccDkr.......',
      '......rkCcccccccccccDkr.......',
      '.......kDDDDDDDDDDDDDk........',
      '.......kCcDGvvvvvEDcDk........',
      '.......kCcDvvvvvvvDcDk........',
      '.......kCcDCCCCCCCDcDk........',
      '.......kCcDCCCCCCCDcDk........',
      '.......kCcDCCCCCCCDcDk........',
      '.......kCcDvvvvvvvDcDk........',
      '.......kCcDGvvvvvEDcDk........',
      '.......kDDDDDDDDDDDDDk........',
      '......rkCcccccccccccDkr.......',
      '......rkCcccccccccccDkr.......',
      '.......kCcccccccccccDk........',
      '........kCcccccccccDk.........',
      '........kllcccccccllk.........',
      '.........klkkkkkkklk..........',
      '..........kBBBBBBBk...........',
      '..............................',
      '..............................',
    ];
const LUXE_COTE = [
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '....................................',
      '............kCCCCCCCk...............',
      '...........kGGvvvkGGvk..............',
      '..........kkvvvvEkvvEk..............',
      '....kCCCCCCcccccccccccCCCCCCCCCk....',
      '..kttccccccccccccccDcccccccccccllk..',
      '..kccccccccccccccccDccccccccccccck..',
      '..kccccccccccccccccDccccccccccccck..',
      '..kBBBkkkkkDDDDDDDDDDDDDDkkkkkBBBk..',
      '.......kkk................kkk.......',
      '......krMrk..............krMrk......',
      '......krrrk..............krrrk......',
      '.......kkk................kkk.......',
      '....................................',
      '....................................',
    ];
const LUXE_HAUT = [
      '....................................',
      '.............kBBBBBBBBk.............',
      '............kCccccccccDk............',
      '...........kCccccccccccDk...........',
      '..........kCccccccccccccDk..........',
      '.........kCccccccccccccccDk.........',
      '.........kCccccccccccccccDk.........',
      '.........kCccccccccccccccDk.........',
      '.........kCccccccccccccccDk.........',
      '........rkCccccccccccccccDkr........',
      '........rkCccccccccccccccDkr........',
      '.........kDDDDDDDDDDDDDDDDk.........',
      '.........kCcDGvvvvvvvvEDcDk.........',
      '.........kCcDvvvvvvvvvvDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDvvvvvvvvvvDcDk.........',
      '.........kCcDGvvvvvvvvEDcDk.........',
      '.........kDDDDDDDDDDDDDDDDk.........',
      '........rkCccccccccccccccDkr........',
      '........rkCccccccccccccccDkr........',
      '.........kCccccccccccccccDk.........',
      '.........kCccccccccccccccDk.........',
      '.........kCccccccccccccccDk.........',
      '..........kCccccccccccccDk..........',
      '..........kttccccccccccttk..........',
      '...........ktkkkkkkkkkktk...........',
      '............kBBBBBBBBBBk............',
      '....................................',
      '....................................',
    ];
const LUXE_BAS = [
      '....................................',
      '.............kBBBBBBBBk.............',
      '............kCccccccccDk............',
      '...........kCccccccccccDk...........',
      '..........kCccccccccccccDk..........',
      '.........kCccccccccccccccDk.........',
      '.........kCccccccccccccccDk.........',
      '.........kCccccccccccccccDk.........',
      '.........kCccccccccccccccDk.........',
      '........rkCccccccccccccccDkr........',
      '........rkCccccccccccccccDkr........',
      '.........kDDDDDDDDDDDDDDDDk.........',
      '.........kCcDGvvvvvvvvEDcDk.........',
      '.........kCcDvvvvvvvvvvDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDCCCCCCCCCCDcDk.........',
      '.........kCcDvvvvvvvvvvDcDk.........',
      '.........kCcDGvvvvvvvvEDcDk.........',
      '.........kDDDDDDDDDDDDDDDDk.........',
      '........rkCccccccccccccccDkr........',
      '........rkCccccccccccccccDkr........',
      '.........kCccccccccccccccDk.........',
      '.........kCccccccccccccccDk.........',
      '.........kCccccccccccccccDk.........',
      '..........kCccccccccccccDk..........',
      '..........kllccccccccccllk..........',
      '...........klkkkkkkkkkklk...........',
      '............kBBBBBBBBBBk............',
      '....................................',
      '....................................',
    ];
const AMBULANCE_COTE = [
      '......................................',
      '......................................',
      '......................................',
      '......................................',
      '......................................',
      '......................................',
      '......................................',
      '......................................',
      '......................................',
      '......................................',
      '................kkkkkkk...............',
      '................llttttt...............',
      '....kkkkkkkkkkkkkkkkkkkk..............',
      '...kCCCCCCCCCCCCCCCCCCCCk.............',
      '...kccDccccccccccccccccck.............',
      '...kttDcccctcccccccccccck.............',
      '...kccDcccctcccccccccccckkkkkkkkkk....',
      '...kccDcctttttcccccccccckCCCCCCCCCk...',
      '...kccDcccctcccccccccccckcGGGvvvvck...',
      '...kccDcccctcccccccccccckcvvvvvEEck...',
      '...kccDccccccccccccccccckccccccccck...',
      '...kDDDDDDDDDDDDDDDDDDDDkDDDDDDDDDk...',
      '...kDDDDDDDDDDDDDDDDDDDDkDDDDDDDllk...',
      '...kBBBkkkkkDDDDDDDDDDDDDDkkkkkBBBk...',
      '........kkk................kkk........',
      '.......krMrk..............krMrk.......',
      '.......krrrk..............krrrk.......',
      '........kkk................kkk........',
      '......................................',
      '......................................',
    ];
const AMBULANCE_HAUT = [
      '......................................',
      '.............kBBBBBBBBBBk.............',
      '............kCccccccccccDk............',
      '...........kCccccccccccccDk...........',
      '..........kCccccccccccccccDk..........',
      '.........rkCccccccccccccccDkr.........',
      '..........kDDDDDDDDDDDDDDDDk..........',
      '..........kCcDGvvvvvvvvEDcDk..........',
      '..........kCcDCCCCCCCCCCDcDk..........',
      '..........kCcDCCCCCCCCCCDcDk..........',
      '..........kDDDDDDDDDDDDDDDDk..........',
      '..........kCccccccccccccccDk..........',
      '.........rkCccccccccccccccDkr.........',
      '.........rkCccccccccccccccDkr.........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '.........rkCccccccccccccccDkr.........',
      '.........rkCccccccccccccccDkr.........',
      '..........kCccccccccccccccDk..........',
      '..........kDDDDDDDDDDDDDDDDk..........',
      '...........kttccccccccccttk...........',
      '............ktkkkkkkkkkktk............',
      '.............kBBBBBBBBBBk.............',
      '......................................',
      '......................................',
    ];
const AMBULANCE_BAS = [
      '......................................',
      '.............kBBBBBBBBBBk.............',
      '............kCccccccccccDk............',
      '...........kCccccccccccccDk...........',
      '..........kCccccccccccccccDk..........',
      '.........rkCccccccccccccccDkr.........',
      '..........kDDDDDDDDDDDDDDDDk..........',
      '..........kCcDGvvvvvvvvEDcDk..........',
      '..........kCcDCCCCCCCCCCDcDk..........',
      '..........kCcDCCCCCCCCCCDcDk..........',
      '..........kDDDDDDDDDDDDDDDDk..........',
      '..........kCccccccccccccccDk..........',
      '.........rkCccccccccccccccDkr.........',
      '.........rkCccccccccccccccDkr.........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '..........kCccccccccccccccDk..........',
      '.........rkCccccccccccccccDkr.........',
      '.........rkCccccccccccccccDkr.........',
      '..........kCccccccccccccccDk..........',
      '..........kDDDDDDDDDDDDDDDDk..........',
      '...........kllccccccccccllk...........',
      '............klkkkkkkkkkklk............',
      '.............kBBBBBBBBBBk.............',
      '......................................',
      '......................................',
    ];
const CAMION_COTE = [
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '..............................................',
      '....kkkkkkkkkkkkkkkkkkkkkkkkkk................',
      '...kCCCCCCCCCCCCCCCCCCCCCCCCCCk...............',
      '...kccDccccccccccccccccccccccck...............',
      '...kttDccccccccccccccccccccccck...............',
      '...kccDccccccccccccccccccccccckkkkkkkkkkkk....',
      '...kccDccccccccccccccccccccccckCCCCCCCCCCCk...',
      '...kccDccccccccccccccccccccccckcGGGvvvvvvck...',
      '...kccDccccccccccccccccccccccckcvvvvvvvEEck...',
      '...kccDccccccccccccccccccccccckccccccccccck...',
      '...kccDccccccccccccccccccccccckccccccccccck...',
      '...kccDccccccccccccccccccccccckccccccccccck...',
      '...kDDDDDDDDDDDDDDDDDDDDDDDDDDkDDDDDDDDDDDk...',
      '...kDDDDDDDDDDDDDDDDDDDDDDDDDDkDDDDDDDDDllk...',
      '...kBBBkkkkkDDDDDDDDDDDDDDDDDDDDDDkkkkkBBBk...',
      '........kkk........................kkk........',
      '.......krMrk......................krMrk.......',
      '.......krrrk......................krrrk.......',
      '........kkk........................kkk........',
      '..............................................',
      '..............................................',
    ];
const CAMION_HAUT = [
      '..............................................',
      '.................kBBBBBBBBBBk.................',
      '................kCccccccccccDk................',
      '...............kCccccccccccccDk...............',
      '..............kCccccccccccccccDk..............',
      '.............rkCccccccccccccccDkr.............',
      '..............kDDDDDDDDDDDDDDDDk..............',
      '..............kCcDGvvvvvvvvEDcDk..............',
      '..............kCcDCCCCCCCCCCDcDk..............',
      '..............kCcDCCCCCCCCCCDcDk..............',
      '..............kCcDCCCCCCCCCCDcDk..............',
      '..............kDDDDDDDDDDDDDDDDk..............',
      '..............kCccccccccccccccDk..............',
      '.............rkCccccccccccccccDkr.............',
      '.............rkCccccccccccccccDkr.............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCCCCCCCCCCCCCCCDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCCCCCCCCCCCCCCCDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCCCCCCCCCCCCCCCDk..............',
      '.............rkCccccccccccccccDkr.............',
      '.............rkCccccccccccccccDkr.............',
      '..............kCccccccccccccccDk..............',
      '..............kDDDDDDDDDDDDDDDDk..............',
      '...............kttccccccccccttk...............',
      '................ktkkkkkkkkkktk................',
      '.................kBBBBBBBBBBk.................',
      '..............................................',
      '..............................................',
    ];
const CAMION_BAS = [
      '..............................................',
      '.................kBBBBBBBBBBk.................',
      '................kCccccccccccDk................',
      '...............kCccccccccccccDk...............',
      '..............kCccccccccccccccDk..............',
      '.............rkCccccccccccccccDkr.............',
      '..............kDDDDDDDDDDDDDDDDk..............',
      '..............kCcDGvvvvvvvvEDcDk..............',
      '..............kCcDCCCCCCCCCCDcDk..............',
      '..............kCcDCCCCCCCCCCDcDk..............',
      '..............kCcDCCCCCCCCCCDcDk..............',
      '..............kDDDDDDDDDDDDDDDDk..............',
      '..............kCccccccccccccccDk..............',
      '.............rkCccccccccccccccDkr.............',
      '.............rkCccccccccccccccDkr.............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCCCCCCCCCCCCCCCDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCCCCCCCCCCCCCCCDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCccccccccccccccDk..............',
      '..............kCCCCCCCCCCCCCCCDk..............',
      '.............rkCccccccccccccccDkr.............',
      '.............rkCccccccccccccccDkr.............',
      '..............kCccccccccccccccDk..............',
      '..............kDDDDDDDDDDDDDDDDk..............',
      '...............kllccccccccccllk...............',
      '................klkkkkkkkkkklk................',
      '.................kBBBBBBBBBBk.................',
      '..............................................',
      '..............................................',
    ];
const REMORQUEUSE_COTE = [
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '................................................',
      '.....................kkkkkkk....................',
      '.....................llttttt....................',
      '.......kkkkkkkkkkkkkkkkkkkkkkk..................',
      '......kCCCCCCCCCCCCCCCCCCCCCCCk.................',
      '.kkkkkkccDcccccccccccccccccccck.................',
      '.kkkkkkttDcccccccccccccccccccck.................',
      '.kk...kccDcccccccccccccccccccckkkkkkkkkkk.......',
      '.MM...kccDcccccccccccccccccccckCCCCCCCCCCk......',
      '......kccDcccccccccccccccccccckcGGGvvvvvck......',
      '......kDDDDDDDDDDDDDDDDDDDDDDDkDDDDDDDDDDk......',
      '......kDDDDDDDDDDDDDDDDDDDDDDDkDDDDDDDDllk......',
      '......kBBBkkkkkDDDDDDDDDDDDDDDDDDkkkkkBBBk......',
      '...........kkk....................kkk...........',
      '..........krMrk..................krMrk..........',
      '..........krrrk..................krrrk..........',
      '...........kkk....................kkk...........',
      '................................................',
      '................................................',
    ];
const REMORQUEUSE_HAUT = [
      '................................................',
      '..................kBBBBBBBBBBk..................',
      '.................kCccccccccccDk.................',
      '................kCccccccccccccDk................',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '..............rkCccccccccccccccDkr..............',
      '...............kDDDDDDDDDDDDDDDDk...............',
      '...............kCcDGvvvvvvvvEDcDk...............',
      '...............kCcDCCCCCCCCCCDcDk...............',
      '...............kCcDCCCCCCCCCCDcDk...............',
      '...............kDDDDDDDDDDDDDDDDk...............',
      '...............kCccccccccccccccDk...............',
      '..............rkCccccccccccccccDkr..............',
      '..............rkCccccccccccccccDkr..............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCCCCCCCCCCCCCCCDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '..............rkCccccccccccccccDkr..............',
      '..............rkCccccccccccccccDkr..............',
      '...............kCccccccccccccccDk...............',
      '...............kDDDDDDDDDDDDDDDDk...............',
      '................kttccccccccccttk................',
      '.................ktkkkkkkkkkktk.................',
      '..................kBBBBBBBBBBk..................',
      '................................................',
      '................................................',
    ];
const REMORQUEUSE_BAS = [
      '................................................',
      '..................kBBBBBBBBBBk..................',
      '.................kCccccccccccDk.................',
      '................kCccccccccccccDk................',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '..............rkCccccccccccccccDkr..............',
      '...............kDDDDDDDDDDDDDDDDk...............',
      '...............kCcDGvvvvvvvvEDcDk...............',
      '...............kCcDCCCCCCCCCCDcDk...............',
      '...............kCcDCCCCCCCCCCDcDk...............',
      '...............kDDDDDDDDDDDDDDDDk...............',
      '...............kCccccccccccccccDk...............',
      '..............rkCccccccccccccccDkr..............',
      '..............rkCccccccccccccccDkr..............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCCCCCCCCCCCCCCCDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '...............kCccccccccccccccDk...............',
      '..............rkCccccccccccccccDkr..............',
      '..............rkCccccccccccccccDkr..............',
      '...............kCccccccccccccccDk...............',
      '...............kDDDDDDDDDDDDDDDDk...............',
      '................kllccccccccccllk................',
      '.................klkkkkkkkkkklk.................',
      '..................kBBBBBBBBBBk..................',
      '................................................',
      '................................................',
    ];
const AUTOBUS_COTE = [
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '......................................................',
      '....kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk....',
      '...kCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCk...',
      '...kttcccccccccccccccccccccccccccccccccccccccccccck...',
      '...kcGGGvvvkGGGvvvkGGGvvvkGGGvvvkGGGvvvkGGckkkkkcck...',
      '...kcvvvvvvkvvvvvvkvvvvvvkvvvvvvkvvvvvvkvvckGGvkcck...',
      '...kcvvvvvvkvvvvvvkvvvvvvkvvvvvvkvvvvvvkvvckvvvkcck...',
      '...kcvvvvvvkvvvvvvkvvvvvvkvvvvvvkvvvvvvkvvckvvvkcck...',
      '...kcvvvvEEkvvvvEEkvvvvEEkvvvvEEkvvvvEEkvEckvvEkcck...',
      '...kccccccccccccccccccccccccccccccccccccccckkkkkcck...',
      '...kccccccccccccccccccccccccccccccccccccccckkkkkcck...',
      '...kDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDk...',
      '...kDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDllk...',
      '...kBBBDkkkkkDDDDDDDDDDDDDDDDDDDDDDDDDDDDkkkkkDBBBk...',
      '.........kkk..............................kkk.........',
      '........krMrk............................krMrk........',
      '........krrrk............................krrrk........',
      '.........kkk..............................kkk.........',
      '......................................................',
      '......................................................',
    ];
const AUTOBUS_HAUT = [
      '......................................................',
      '....................kCccccccccccDk....................',
      '...................kCccccccccccccDk...................',
      '..................kDDDDDDDDDDDDDDDDk..................',
      '..................kCcDGvvvvvvvvEDcDk..................',
      '..................kCcDCCCCCCCCCCDcDk..................',
      '..................kCcDCCCCCCCCCCDcDk..................',
      '..................kCcDCCCCCCCCCCDcDk..................',
      '..................kCcDCCCCCCCCCCDcDk..................',
      '..................kDDDDDDDDDDDDDDDDk..................',
      '..................kCccccccccccccccDk..................',
      '.................rkCccccccccccccccDkr.................',
      '.................rkCccccccccccccccDkr.................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCCCCCCCCCCCCCCCDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCCCCCCCCCCCCCCCDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCCCCCCCCCCCCCCCDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCCCCCCCCCCCCCCCDk..................',
      '..................kCccccccccccccccDk..................',
      '.................rkCccccccccccccccDkr.................',
      '.................rkCccccccccccccccDkr.................',
      '..................kCccccccccccccccDk..................',
      '..................kDDDDDDDDDDDDDDDDk..................',
      '...................kttccccccccccttk...................',
      '....................ktkkkkkkkkkktk....................',
      '......................................................',
      '......................................................',
    ];
const AUTOBUS_BAS = [
      '......................................................',
      '....................kCccccccccccDk....................',
      '...................kCccccccccccccDk...................',
      '..................kDDDDDDDDDDDDDDDDk..................',
      '..................kCcDGvvvvvvvvEDcDk..................',
      '..................kCcDCCCCCCCCCCDcDk..................',
      '..................kCcDCCCCCCCCCCDcDk..................',
      '..................kCcDCCCCCCCCCCDcDk..................',
      '..................kCcDCCCCCCCCCCDcDk..................',
      '..................kDDDDDDDDDDDDDDDDk..................',
      '..................kCccccccccccccccDk..................',
      '.................rkCccccccccccccccDkr.................',
      '.................rkCccccccccccccccDkr.................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCCCCCCCCCCCCCCCDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCCCCCCCCCCCCCCCDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCCCCCCCCCCCCCCCDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCccccccccccccccDk..................',
      '..................kCCCCCCCCCCCCCCCDk..................',
      '..................kCccccccccccccccDk..................',
      '.................rkCccccccccccccccDkr.................',
      '.................rkCccccccccccccccDkr.................',
      '..................kCccccccccccccccDk..................',
      '..................kDDDDDDDDDDDDDDDDk..................',
      '...................kllccccccccccllk...................',
      '....................klkkkkkkkkkklk....................',
      '......................................................',
      '......................................................',
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

SPRITES.auto = {
  w: 32, h: 31, ancre: [16, 28],
  pal: nuancer({ k: '#101018', c: '#c0392b', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', x: '#c0392b', y: '#c0392b', s: '#00000030' }),
  swaps: ['c'], poses: { cote: [AUTO_COTE], haut: [AUTO_HAUT], bas: [AUTO_BAS] },
};
SPRITES.bateau = {
  w: 32, h: 34, ancre: [16, 31],
  pal: nuancer({ k: '#101018', c: '#ecf0f1', v: '#7fb3d8', r: '#3a2f26', l: '#fff3b0', t: '#ff4b3e', x: '#ecf0f1', y: '#ecf0f1', s: '#00000030' }),
  swaps: ['c'], poses: { cote: [BATEAU_COTE], haut: [BATEAU_HAUT], bas: [BATEAU_BAS] },
};
SPRITES.taxi = {
  w: 32, h: 31, ancre: [16, 28],
  pal: nuancer({ k: '#101018', c: '#f1c40f', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', x: '#101018', y: '#101018', s: '#00000030' }),
  swaps: ['c'], poses: { cote: [AUTO_COTE], haut: [AUTO_HAUT], bas: [AUTO_BAS] },
};
SPRITES.police = {
  w: 32, h: 31, ancre: [16, 28],
  pal: nuancer({ k: '#101018', c: '#ffffff', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', x: '#e0312a', y: '#2f6fd8', s: '#00000030' }),
  swaps: ['c'], poses: { cote: [AUTO_COTE], haut: [AUTO_HAUT], bas: [AUTO_BAS] },
};
SPRITES.velo = {
  w: 20, h: 19, ancre: [10, 16],
  // LA SELLE, en [dx, dy] depuis la ligne de sol du dessin vu d'en haut : la ou
  // l'ANCRE du passant assis se pose. ⚠️ Une seule, depuis que la machine
  // tourne : elle est un point DE LA MACHINE et elle tourne avec elle
  // (`Vehicules.imageDuCavalier`). Trois selles, une par pose, c'etaient trois
  // chiffres a tenir d'accord pour un seul siege.
  selle: [0, -7],
  pal: nuancer({ k: '#101018', c: '#2980b9', r: '#2a2a2e', l: '#fff3b0', t: '#ff4b3e' }),
  swaps: ['c'],
  poses: { cote: [VELO_COTE], haut: [VELO_HAUT], bas: [VELO_BAS] },
};
SPRITES.moto = {
  w: 24, h: 23, ancre: [12, 20],
  selle: [0, -8],
  pal: nuancer({ k: '#101018', c: '#1a1a1a', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e' }),
  swaps: ['c'],
  poses: { cote: [MOTO_COTE], haut: [MOTO_HAUT], bas: [MOTO_BAS] },
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
  w: 46, h: 40, ancre: [23, 37],
  pal: nuancer({ k: '#101018', c: '#7f8c8d', b: '#8d99a6', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', s: '#565c63' }),
  swaps: ['c'],
  poses: { cote: [CAMION_COTE], haut: [CAMION_HAUT], bas: [CAMION_BAS] },
};
// Le plus long du parc — cinq cercles de collision, et un toit a trappes.
SPRITES.autobus = {
  w: 54, h: 48, ancre: [27, 45],
  pal: nuancer({ k: '#101018', c: '#2980b9', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', s: '#1f5f8b' }),
  swaps: ['c'],
  poses: { cote: [AUTOBUS_COTE], haut: [AUTOBUS_HAUT], bas: [AUTOBUS_BAS] },
};
// ⚠️ La croix se lit d'EN HAUT : vue de dessus, c'est elle qui la nomme.
SPRITES.ambulance = {
  w: 38, h: 30, ancre: [19, 27],
  pal: nuancer({ k: '#101018', c: '#ffffff', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', x: '#e0312a', y: '#2f6fd8', s: '#f39c12' }),
  swaps: ['c'],
  poses: { cote: [AMBULANCE_COTE], haut: [AMBULANCE_HAUT], bas: [AMBULANCE_BAS] },
};
// Le bras couche sur le plateau, et le crochet qui depasse a l'arriere.
SPRITES.remorqueuse = {
  w: 48, h: 34, ancre: [24, 31],
  pal: nuancer({ k: '#101018', c: '#d98324', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', h: '#6b7078', p: '#c9cdd4', y: '#f39c12', s: '#3a3d44' }),
  swaps: ['c'],
  poses: { cote: [REMORQUEUSE_COTE], haut: [REMORQUEUSE_HAUT], bas: [REMORQUEUSE_BAS] },
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
  w: 30, h: 29, ancre: [15, 26],
  pal: nuancer({ k: '#101018', c: '#c0392b', v: '#7fb3d8', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', i: '#2a2028', u: '#6b4b2c', s: '#8e2b20' }),
  swaps: ['c'],
  poses: { cote: [SPORT_COTE], haut: [SPORT_HAUT], bas: [SPORT_BAS] },
};
// L'inverse exact du sport : rien ne depasse, rien ne s'ouvre. Un long
// rectangle sombre, deux vitres fines et du chrome tout autour.
SPRITES.luxe = {
  w: 36, h: 34, ancre: [18, 31],
  pal: nuancer({ k: '#101018', c: '#101014', v: '#5f7f99', r: '#1a1a1e', l: '#fff3b0', t: '#ff4b3e', m: '#b9bcc4', s: '#26262e' }),
  swaps: ['c'],
  poses: { cote: [LUXE_COTE], haut: [LUXE_HAUT], bas: [LUXE_BAS] },
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
  function trottoir(ctx, v, T) {
    const joinOuest = (v & 1) === 0, joinNord = (v & 2) === 0;
    const usure = v >> 2;
    plein(ctx, BETON.fond, T);
    points(ctx, usure + 1, T, BETON.grain, 6, 7);
    points(ctx, usure + 1, T, BETON.arete, 4, 41);
    if (usure === 13) fendillement(ctx, usure + 1, T, BETON.fissure);
    else if (usure === 14) rapiecage(ctx, usure + 1, T, BETON.rapiece);
    else if (usure === 15) souillure(ctx, usure + 1, T, BETON.tache);
    // Les joints, EN DERNIER : rien ne passe par-dessus le bord d'une dalle.
    if (joinOuest) {
      ctx.fillStyle = BETON.joint; ctx.fillRect(0, 0, 1, T);
      ctx.fillStyle = BETON.arete; ctx.fillRect(1, 0, 1, T);
      // Un peu de mousse dans le joint, une dalle sur huit : c'est elle qui dit
      // qu'il y a de la terre dessous et que personne ne passe le balai.
      if (usure === 12) { ctx.fillStyle = BETON.mousse; for (let y = 3; y < T - 3; y += 4) ctx.fillRect(0, y, 1, 1); }
    }
    if (joinNord) {
      ctx.fillStyle = BETON.joint; ctx.fillRect(0, 0, T, 1);
      ctx.fillStyle = BETON.arete; ctx.fillRect(0, 1, T, 1);
      if (usure === 12) { ctx.fillStyle = BETON.mousse; for (let x = 3; x < T - 3; x += 4) ctx.fillRect(x, 0, 1, 1); }
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

  //: La ruelle : deux tuiles derriere chaque bande d'ilot, sur toute sa
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
  function abord(ctx, v, T) {
    plein(ctx, '#6d665a', T);
    // Les paves : quatre rangees de deux, decalees une rangee sur deux.
    ctx.fillStyle = '#7a7266';
    for (let r = 0; r < 4; r++) {
      const dec = (r % 2) * 4;
      for (let x = -4 + dec; x < T; x += 8) ctx.fillRect(Math.max(0, x + 1), r * 4 + 1, Math.min(T, x + 7) - Math.max(0, x + 1), 2);
    }
    points(ctx, (v >> 2) + 1, T, '#5c5549', 5, 23);
    points(ctx, (v >> 2) + 1, T, '#847c6f', 3, 61);
  }

  return {
    ',': herbe,
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
  poubelle: { casse: 0.85, pv: 25, w: 10, h: 14, ancre: [5, 13], r: 4, solide: true, peindre: function (ctx, w, h) {
    ctx.fillStyle = '#3f4a3c'; ctx.fillRect(1, 3, 8, 11);
    ctx.fillStyle = '#4c5a48'; ctx.fillRect(2, 4, 6, 9);
    ctx.fillStyle = '#2b332a'; ctx.fillRect(0, 1, 10, 3); ctx.fillRect(4, 5, 1, 8);
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
  // Les trois du marche noir. A seize pixels, ce qui les nomme : le chargeur
  // qui pend sous la mitraillette, la crosse de bois et le long canon de la
  // carabine, le chiffon allume au goulot du Molotov.
  mitraillette: function (ctx) { ctx.fillStyle = '#3a3d44'; ctx.fillRect(2, 4, 11, 2); ctx.fillRect(6, 6, 2, 4); ctx.fillStyle = '#6b4b2c'; ctx.fillRect(2, 6, 2, 2); },
  carabine: function (ctx) { ctx.fillStyle = '#6b4b2c'; ctx.fillRect(1, 5, 6, 2); ctx.fillRect(2, 7, 2, 2); ctx.fillStyle = '#3a3d44'; ctx.fillRect(6, 4, 10, 2); ctx.fillStyle = '#9aa0a8'; ctx.fillRect(8, 2, 3, 1); },
  molotov: function (ctx) { ctx.fillStyle = '#2f6b2a'; ctx.fillRect(5, 3, 4, 6); ctx.fillRect(6, 1, 2, 2); ctx.fillStyle = '#efe6d0'; ctx.fillRect(6, 0, 2, 1); ctx.fillStyle = '#ff8c1a'; ctx.fillRect(8, 0, 1, 1); ctx.fillStyle = '#ffd23a'; ctx.fillRect(9, 1, 1, 1); },
  // La liasse d'un guichet defonce : du vert, une bande de papier, une
  // deuxieme liasse qui depasse — a seize pixels, c'est la couleur qui la nomme.
  billets: function (ctx) { ctx.fillStyle = '#2f6b2a'; ctx.fillRect(5, 2, 9, 5); ctx.fillStyle = '#3f8d38'; ctx.fillRect(3, 4, 9, 5); ctx.fillStyle = '#9adf7a'; ctx.fillRect(4, 5, 7, 1); ctx.fillStyle = '#e8e6de'; ctx.fillRect(7, 4, 2, 5); },
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
