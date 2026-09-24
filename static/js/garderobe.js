/* Bandini — la garde-robe : des squelettes qu'on habille, piece par piece.

   Demande de Martin (22 sept. 2026) : « des squelettes qu'on habille, ce qui donne une presque
   infinite d'habillement », « plusieurs types de squelettes pour les types de personnes ».

   Python decide (`app/garderobe.py` : les listes, les garde-robes, la tenue de chaque
   personnage), ce fichier DESSINE.

   - UN SQUELETTE est une fiche de poses en lettres de REGION : `h` cheveux, `s` peau, `o` yeux,
     `c` haut, `p` bas, `b` souliers, `k` contour. `homme` est le corps du joueur (ses 42 poses,
     `SPRITES.joueur`) ; `femme`, `costaud`, `vieux` et `grand` en sont derives par des regles
     sur les rangees (elargir le torse, retirer une rangee de jambes, voûter la tete) ; `enfant`
     est `SPRITES.enfant`. Chaque grille gagne `MARGE_HAUT` rangees au-dessus (la place d'un
     chapeau) et `MARGE_COTE` colonnes de chaque cote (un bord de feutre, une visiere).
   - UNE TENUE s'enfile sur une grille : la coiffure, le haut, le bas, les souliers et les
     accessoires changent les lettres de leur region ; le chapeau est un petit dessin pose sur
     la tete que la pose MONTRE (`tete`), de face, de dos ou de profil.
   - LA CUISSON est paresseuse et bornee : une tenue cuit une pose la premiere fois qu'on la
     dessine, et le cache garde les `CACHE_MAX` dernieres tenues. ⚠️ Un passant qui nait et
     disparait a une tenue a lui : un cache sans borne grossirait toute la partie. */

const Garderobe = (function () {
  'use strict';

  const MARGE_HAUT = 3, MARGE_COTE = 2, CACHE_MAX = 240;

  // ------------------------------------------------------------------ outils de grille

  function copie(g) { return g.map(function (r) { return r.split(''); }); }
  function lit(g, x, y) { return (y >= 0 && y < g.length && x >= 0 && x < g[y].length) ? g[y][x] : '.'; }
  function pose(g, x, y, ch) { if (y >= 0 && y < g.length && x >= 0 && x < g[y].length) g[y][x] = ch; }
  function ligneA(r, lettres) { for (let i = 0; i < r.length; i++) if (lettres.indexOf(r[i]) >= 0) return true; return false; }
  function bornes(r) {
    let a = -1, b = -1;
    for (let i = 0; i < r.length; i++) if (r[i] !== '.') { if (a < 0) a = i; b = i; }
    return [a, b];
  }
  function vide(w) { return new Array(w).fill('.'); }

  /** La vue d'une pose : `bas` (de face), `haut` (de dos), `cote` (profil droit), ou null
      pour un corps couche — le chapeau tombe, les cheveux restent ce qu'ils sont. */
  function vueDe(nom) {
    if (nom === 'bas' || nom === 'haut' || nom === 'cote') return nom;
    const m = /_(bas|haut|cote)$/.exec(nom);
    return m ? m[1] : null;
  }

  /** La tete que montre une grille : sa boite (contour compris), le haut du crane, la rangee
      des yeux et la premiere rangee du haut du corps (`t0`). Null si on n'en trouve pas. */
  function tete(g) {
    let t0 = -1;
    for (let y = 0; y < g.length; y++) if (ligneA(g[y], 'c')) { t0 = y; break; }
    if (t0 < 2) return null;
    let x0 = 99, x1 = -1, y0 = 99, yeux = -1;
    for (let y = 0; y < t0; y++) for (let x = 0; x < g[y].length; x++) {
      const ch = g[y][x];
      if (ch === 'h' || ch === 'o') { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); }
      if (ch === 'o' && yeux < 0) yeux = y;
    }
    if (x1 < 0) return null;
    return { x0: x0 - 1, x1: x1 + 1, haut: y0 - 1, yeux: yeux, t0: t0, milieu: (x0 + x1) / 2 };
  }

  /** Les colonnes du TORSE (la rangee des epaules) : ce qui depasse, sur les rangees d'en
      dessous, ce sont les bras. */
  function torse(g, t0) {
    const r = g[t0];
    let a = -1, b = -1;
    for (let i = 0; i < r.length; i++) if (r[i] === 'c') { if (a < 0) a = i; b = i; }
    return [a, b];
  }

  function rangeesDe(g, lettre, sans) {
    const out = [];
    for (let y = 0; y < g.length; y++) if (ligneA(g[y], lettre) && !(sans && ligneA(g[y], sans))) out.push(y);
    return out;
  }

  // ------------------------------------------------------------------ les squelettes

  /** Elargit d'un pixel de chaque cote (ou du seul cote `droite`) : le contour recule d'une
      case, le contenu le suit. */
  function elargir(r, droiteSeule) {
    const [a, b] = bornes(r);
    if (a < 1 || b > r.length - 2) return r;
    const n = r.slice();
    if (!droiteSeule) { n[a - 1] = r[a]; n[a] = r[a + 1]; }
    n[b + 1] = r[b]; n[b] = r[b - 1];
    return n;
  }

  //: Les regles de chaque squelette derive, appliquees a chaque pose DEBOUT (`vueDe` non nul).
  //: Une pose couchee garde le corps d'homme, mais sa hauteur suit (rangees vides en haut).
  const DERIVES = {
    homme: function (g) { return g; },
    // Le torse et les hanches d'un pixel plus larges ; de profil, le ventre seul.
    costaud: function (g, vue) {
      const t = tete(g);
      if (!t) return g;
      const hanches = rangeesDe(g, 'p', 'c')[0];
      return g.map(function (r, y) {
        if (y >= t.t0 && (ligneA(r, 'c') || y === hanches)) return elargir(r, vue === 'cote');
        return r;
      });
    },
    // Une rangee de jambes de moins, la tete en avant (de profil) : le dos voûte.
    vieux: function (g, vue) {
      const t = tete(g);
      if (!t) return g;
      const jambes = rangeesDe(g, 'p', 'cb');
      let n = g;
      if (jambes.length >= 2) {
        n = g.filter(function (r, y) { return y !== jambes[0]; });
        n.unshift(vide(g[0].length));
      }
      if (vue === 'cote') {
        n = n.map(function (r, y) {
          if (y > t.t0) return r;
          const d = r.slice(); d.pop(); d.unshift('.'); return d;
        });
      }
      return n;
    },
    // Une rangee de jambes de plus : on la double.
    grand: function (g) {
      const t = tete(g);
      if (!t) return g;
      const jambes = rangeesDe(g, 'p', 'cb');
      if (!jambes.length) return g;
      const n = g.slice();
      n.splice(jambes[0], 0, g[jambes[0]].slice());
      return n;
    },
    // Une rangee de moins que l'homme, les hanches d'un pixel plus larges de face et de dos.
    femme: function (g, vue) {
      const t = tete(g);
      if (!t) return g;
      const jambes = rangeesDe(g, 'p', 'cb');
      let n = g;
      if (jambes.length >= 2) {
        n = g.filter(function (r, y) { return y !== jambes[1]; });
        if (vue !== 'cote') n[jambes[0]] = elargir(n[jambes[0]]);
        n.unshift(vide(g[0].length));
      }
      return n;
    },
  };

  function marger(g) {
    const w = g[0].length + MARGE_COTE * 2;
    const n = [];
    for (let i = 0; i < MARGE_HAUT; i++) n.push(vide(w));
    g.forEach(function (r) {
      const l = vide(MARGE_COTE).concat(Array.isArray(r) ? r : r.split('')).concat(vide(MARGE_COTE));
      n.push(l);
    });
    return n;
  }

  const squelettes = {};

  /** Le squelette `nom` : { w, h, ancre, poses: {nom: [grilles]}, mains }. */
  function squelette(nom) {
    if (squelettes[nom]) return squelettes[nom];
    const enfant = nom === 'enfant';
    const def = enfant ? SPRITES.enfant : SPRITES.joueur;
    const regle = enfant ? DERIVES.homme : (DERIVES[nom] || DERIVES.homme);
    const poses = {};
    let h = 0;
    for (const p in def.poses) {
      const vue = vueDe(p);
      poses[p] = def.poses[p].map(function (grille) {
        let g = copie(grille);
        if (vue) g = regle(g, vue);
        return marger(g);
      });
      h = Math.max(h, poses[p][0].length);
    }
    // Toutes les grilles a la meme hauteur : les pieds restent sur la derniere rangee.
    for (const p in poses) {
      poses[p] = poses[p].map(function (g) {
        const n = g.slice();
        while (n.length < h) n.unshift(vide(g[0].length));
        while (n.length > h) n.shift();
        return n;
      });
    }
    const w = def.w + MARGE_COTE * 2;
    const decaleY = h - def.h;
    const mains = {};
    if (def.mains) {
      for (const m in def.mains) {
        const v = def.mains[m];
        mains[m] = [v[0] + MARGE_COTE, v[1] + decaleY, v[2]];
      }
    }
    const ancre = def.ancre || [def.w >> 1, def.h - 1];
    squelettes[nom] = { w: w, h: h, ancre: [ancre[0] + MARGE_COTE, ancre[1] + decaleY], poses: poses, mains: mains };
    return squelettes[nom];
  }

  // ------------------------------------------------------------------ les chapeaux

  //: `g` le dessin ; `a` la rangee du dessin qui tombe sur le haut du crane ; `x` le decalage
  //: depuis le bord gauche de la tete (sinon centre). Lettres : `t` le chapeau, `T` son ombre,
  //: `L` son reflet, `v` la visiere, `a` la couleur d'accent (ruban, pompon, insigne).
  const H_CASQUETTE = { bas: { g: ['..kkkk..', '.kttttk.', 'kttttttk', 'kvvvvvvk'], a: 2 },
                        haut: { g: ['..kkkk..', '.kttttk.', 'kttttttk', 'kTTTTTTk'], a: 2 },
                        cote: { g: ['.kkkk.....', 'kttttk....', 'ktttttk...', 'kTTTTTvvvk'], a: 2, x: -1 } };
  const CHAPEAUX = {
    casquette: H_CASQUETTE,
    casquette_arriere: { bas: H_CASQUETTE.haut, haut: H_CASQUETTE.bas,
                         cote: { g: H_CASQUETTE.cote.g.map(function (l) { return l.split('').reverse().join(''); }), a: 2, x: -2 } },
    tuque: { bas: { g: ['...kk...', '..kaak..', '.kttttk.', 'kttttttk', 'kTtTtTtk'], a: 3 },
             haut: { g: ['...kk...', '..kaak..', '.kttttk.', 'kttttttk', 'kTtTtTtk'], a: 3 },
             cote: { g: ['..kk....', '.kaak...', '.kttttk.', 'kttttttk', 'kTtTtTtk'], a: 3, x: 0 } },
    feutre: { bas: { g: ['...kkkk...', '..kttttk..', '..kaaaak..', 'kttttttttk', 'kkkkkkkkkk'], a: 3 },
              haut: { g: ['...kkkk...', '..kttttk..', '..kaaaak..', 'kttttttttk', 'kkkkkkkkkk'], a: 3 },
              cote: { g: ['...kkkk...', '..kttttk..', '..kaaaak..', 'kttttttttk', 'kkkkkkkkkk'], a: 3, x: -2 } },
    casque_chantier: { bas: { g: ['...kkkk...', '..kttLtk..', '.kttttttk.', 'kttttttttk', 'kkkkkkkkkk'], a: 3 },
                       haut: { g: ['...kkkk...', '..kttttk..', '.kttLtttk.', 'kttttttttk', 'kkkkkkkkkk'], a: 3 },
                       cote: { g: ['..kkkk....', '.kttLtk...', 'kttttttk..', 'ktttttttkk', 'kkkkkkkkkk'], a: 3, x: -1 } },
    kepi: { bas: { g: ['.kkkkkk.', 'kttttttk', 'kttaattk', 'kvvvvvvk'], a: 2 },
            haut: { g: ['.kkkkkk.', 'kttttttk', 'kttttttk', 'kTTTTTTk'], a: 2 },
            cote: { g: ['.kkkkkk...', 'kttttttk..', 'kttttatk..', 'kTTTTTvvvk'], a: 2, x: -1 } },
    canotier: { bas: { g: ['..kkkkkk..', '..kttttk..', '..kaaaak..', 'kttttttttk', 'kkkkkkkkkk'], a: 3 },
                haut: { g: ['..kkkkkk..', '..kttttk..', '..kaaaak..', 'kttttttttk', 'kkkkkkkkkk'], a: 3 },
                cote: { g: ['..kkkkkk..', '..kttttk..', '..kaaaak..', 'kttttttttk', 'kkkkkkkkkk'], a: 3, x: -2 } },
    beret: { bas: { g: ['..kkkkk..', '.ktttttk.', 'kttttttkk'], a: 1 },
             haut: { g: ['..kkkkk..', '.ktttttk.', 'kttttttkk'], a: 1 },
             cote: { g: ['.kkkkk..', 'kttttttk', 'kttttttk'], a: 1, x: -1 } },
    bandana: { bas: { g: ['..kkkk..', '.kttttk.', 'kttatttk'], a: 0 },
               haut: { g: ['..kkkk..', '.kttttk.', 'kttttttk', '...kak..'], a: 0 },
               cote: { g: ['.kkkk..', 'kttttk.', 'katttk.'], a: 0, x: 0 } },
    cowboy: { bas: { g: ['...kkkk...', '..kttttk..', 'k.kaaaak.k', 'kttttttttk', '.kkkkkkkk.'], a: 3 },
              haut: { g: ['...kkkk...', '..kttttk..', 'k.kaaaak.k', 'kttttttttk', '.kkkkkkkk.'], a: 3 },
              cote: { g: ['...kkkk...', '..kttttk..', '..kaaaak..', 'kttttttttk', '.kkkkkkkk.'], a: 3, x: -2 } },
    marin: { bas: { g: ['.kkkkkk.', 'kttttttk', 'kTTTTTTk', 'kvvvvvvk'], a: 2 },
             haut: { g: ['.kkkkkk.', 'kttttttk', 'kTTTTTTk'], a: 2 },
             cote: { g: ['.kkkkkk..', 'kttttttk..', 'kTTTTTTvvk'], a: 2, x: -1 } },
    capuche: { bas: { g: ['..kkkkkk..', '.kttttttk.', 'kttttttttk', 'ktt....ttk', 'kt......tk', 'kt......tk', 'kt......tk', '.kt....tk.'], a: 1 },
               haut: { g: ['..kkkkkk..', '.kttttttk.', 'kttttttttk', 'kttttttttk', 'kttttttttk', 'kTTTTTTTTk', '.kTTTTTTk.'], a: 1 },
               cote: { g: ['..kkkkk..', '.kttttttk', 'ktttttttk', 'ktttk....', 'ktttk....', 'ktttk....', '.kttk....'], a: 1, x: -1 } },
  };

  function poserChapeau(g, t, vue, nom) {
    const c = CHAPEAUX[nom] && CHAPEAUX[nom][vue];
    if (!c) return;
    const w = c.g[0].length;
    const x = t.x0 + (c.x !== undefined ? c.x : Math.floor((t.x1 - t.x0 + 1 - w) / 2));
    const y = t.haut - c.a;
    c.g.forEach(function (l, dy) {
      for (let i = 0; i < l.length; i++) if (l[i] !== '.') pose(g, x + i, y + dy, l[i]);
    });
  }

  // ------------------------------------------------------------------ la coiffure

  function coiffer(g, t, vue, nom) {
    const dansTete = function (fn) {
      for (let y = Math.max(0, t.haut); y < t.t0; y++) for (let x = t.x0; x <= t.x1; x++) fn(x, y);
    };
    const bord = function (x, y) { if (lit(g, x, y) === '.') pose(g, x, y, 'k'); };
    if (nom === 'rase' || nom === 'chauve') {
      dansTete(function (x, y) { if (g[y][x] === 'h') g[y][x] = nom === 'rase' ? 'S' : 's'; });
    } else if (nom === 'degarnie') {
      for (let y = t.haut; y <= t.haut + 2; y++) for (let x = t.x0 + 2; x <= t.x1 - 2; x++) if (lit(g, x, y) === 'h') pose(g, x, y, 's');
    } else if (nom === 'longue') {
      const bas = Math.min(g.length - 1, t.t0 + 1);
      if (vue === 'bas') {
        for (let y = t.haut + 2; y <= bas; y++) {
          pose(g, t.x0, y, 'h'); pose(g, t.x1, y, 'h'); bord(t.x0 - 1, y); bord(t.x1 + 1, y);
        }
      } else if (vue === 'haut') {
        for (let y = t.haut + 1; y <= bas; y++) {
          for (let x = t.x0 + 1; x <= t.x1 - 1; x++) if (lit(g, x, y) !== '.' && lit(g, x, y) !== 'k') pose(g, x, y, 'h');
          pose(g, t.x0, y, 'h'); pose(g, t.x1, y, 'h'); bord(t.x0 - 1, y); bord(t.x1 + 1, y);
        }
      } else if (vue === 'cote') {
        for (let y = t.haut + 2; y <= bas; y++) { pose(g, t.x0, y, 'h'); if (lit(g, t.x0 + 1, y) !== 'o') pose(g, t.x0 + 1, y, 'h'); bord(t.x0 - 1, y); }
      }
    } else if (nom === 'queue') {
      if (vue === 'haut') {
        const m = Math.floor(t.milieu);
        for (let y = t.t0 - 1; y <= t.t0 + 1; y++) { pose(g, m, y, 'h'); pose(g, m + 1, y, 'h'); pose(g, m - 1, y, 'k'); pose(g, m + 2, y, 'k'); }
      } else if (vue === 'cote') {
        for (let y = t.haut + 2; y <= t.haut + 5; y++) { pose(g, t.x0, y, 'h'); pose(g, t.x0 - 1, y, 'h'); bord(t.x0 - 2, y); }
        pose(g, t.x0 - 1, t.haut + 2, 'a');
      }
    } else if (nom === 'chignon') {
      const m = Math.floor(t.milieu) + (vue === 'cote' ? -2 : 0);
      [['.kk.', 0], ['khhk', 1]].forEach(function (r) {
        for (let i = 0; i < 4; i++) if (r[0][i] !== '.') pose(g, m - 1 + i, t.haut - 2 + r[1], r[0][i]);
      });
    } else if (nom === 'bouclee') {
      for (let y = t.haut + 1; y <= t.haut + 3; y++) {
        if (vue !== 'cote') { pose(g, t.x1, y, 'h'); bord(t.x1 + 1, y); }
        pose(g, t.x0, y, 'h'); bord(t.x0 - 1, y);
      }
      dansTete(function (x, y) { if (g[y][x] === 'h' && (x + y) % 3 === 0) g[y][x] = 'H'; });
    } else if (nom === 'crete') {
      const m = Math.floor(t.milieu) + (vue === 'cote' ? -1 : 0);
      dansTete(function (x, y) { if (g[y][x] === 'h' && x !== m && x !== m + 1) g[y][x] = 'S'; });
      for (let y = t.haut - 2; y <= t.haut; y++) { pose(g, m, y, 'h'); pose(g, m + 1, y, 'h'); bord(m - 1, y); bord(m + 2, y); }
      bord(m, t.haut - 3); bord(m + 1, t.haut - 3);
    } else if (nom === 'meche') {
      const y = t.yeux > 0 ? t.yeux - 1 : t.haut + 3;
      if (vue === 'bas') for (let x = t.x0 + 1; x <= t.x0 + 3; x++) pose(g, x, y, 'h');
      else if (vue === 'cote') { pose(g, t.x1 - 1, y, 'h'); pose(g, t.x1 - 2, y, 'h'); }
    }
  }

  // ------------------------------------------------------------------ le haut, le bas, les souliers

  function habiller(g, t, vue, tn) {
    const t0 = t ? t.t0 : rangeesDe(g, 'c')[0];
    if (t0 === undefined) return;
    const [xa, xb] = torse(g, t0);
    const milieu = Math.floor((xa + xb) / 2);
    const jambes = rangeesDe(g, 'p', 'c');
    const bras = function (x) { return x < xa || x > xb; };
    const h = tn.haut;
    const face = vue === 'bas', dos = vue === 'haut';
    // Les manches : un t-shirt montre l'avant-bras, une camisole tout le bras.
    if ((h === 'tshirt' || h === 'camisole') && (face || dos)) {
      for (let y = t0 + (h === 'tshirt' ? 2 : 1); y < g.length; y++) {
        if (!ligneA(g[y], 'c')) break;
        for (let x = 0; x < g[y].length; x++) if (g[y][x] === 'c' && bras(x)) g[y][x] = 's';
      }
    }
    if (h === 'chemise' && face) { pose(g, milieu, t0, 'w'); pose(g, milieu + 1, t0, 'w'); }
    if ((h === 'veston' || h === 'sarrau') && face) {
      pose(g, milieu, t0, 'w'); pose(g, milieu + 1, t0, 'w');
      pose(g, milieu, t0 + 1, 'w'); pose(g, milieu + 1, t0 + 1, 'w');
      for (let y = t0 + 2; y < g.length && ligneA(g[y], 'c'); y++) if (g[y][milieu] === 'c') g[y][milieu] = 'C';
    }
    if (h === 'coton_ouate' && face && ligneA(g[t0 + 3] || [], 'c')) {
      for (let x = milieu - 1; x <= milieu + 2; x++) if (g[t0 + 3][x] === 'c') g[t0 + 3][x] = 'C';
    }
    if (h === 'veste_travail' && g[t0 + 2]) {
      for (let x = 0; x < g[t0 + 2].length; x++) if (g[t0 + 2][x] === 'c') g[t0 + 2][x] = 'y';
    }
    if (h === 'salopette') {
      for (let y = t0; y < g.length && ligneA(g[y], 'c'); y++) {
        for (let x = 0; x < g[y].length; x++) {
          if (g[y][x] !== 'c') continue;
          const bavette = face && y > t0 && x >= milieu - 1 && x <= milieu + 2;
          const bretelle = (face || dos) && y === t0 && (x === milieu - 1 || x === milieu + 2);
          const croise = dos && y > t0 && (x === milieu || x === milieu + 1);
          g[y][x] = (bavette || bretelle || croise) ? 'p' : 'w';
        }
      }
    }
    if (h === 'tablier' && (face || vue === 'cote')) {
      const x0 = face ? milieu - 1 : xb, x1 = face ? milieu + 2 : xb;
      for (let y = t0 + 1; y <= (jambes[1] !== undefined ? jambes[1] : t0 + 4) && y < g.length; y++) {
        for (let x = x0; x <= x1; x++) if ('cp'.indexOf(lit(g, x, y)) >= 0) pose(g, x, y, 'W');
      }
    }
    // Le motif, sur ce qui reste du haut.
    const motif = tn.motif;
    if (motif === 'raye' || motif === 'carreaute') {
      for (let y = t0; y < g.length; y++) for (let x = 0; x < g[y].length; x++) {
        if (g[y][x] !== 'c') continue;
        if (motif === 'raye' && (y - t0) % 2 === 1) g[y][x] = 'Q';
        if (motif === 'carreaute' && (x + y) % 2 === 0) g[y][x] = 'C';
      }
    }
    // Ce qui descend sur les jambes : le manteau, le sarrau, la robe.
    if (h === 'manteau' || h === 'sarrau' || h === 'robe') {
      const n = h === 'robe' ? jambes.length - 1 : 2;
      jambes.slice(0, Math.max(0, n)).forEach(function (y, i) {
        for (let x = 0; x < g[y].length; x++) if (g[y][x] === 'p') g[y][x] = (i === n - 1 && h === 'robe') ? 'C' : 'c';
        if (h === 'manteau' && face && g[y][milieu] === 'c') g[y][milieu] = 'C';
      });
    }
    // Le bas. ⚠️ Pas sur un corps couche : ses « jambes » sont une rangee couchee, et la
    // derniere rangee de `p` y est le dessus du corps — des bottes y poussaient.
    if (!vue) return;
    const derniere = jambes[jambes.length - 1];
    if ((tn.bas === 'short' || tn.bas === 'jupe') && derniere !== undefined && h !== 'robe') {
      for (let x = 0; x < g[derniere].length; x++) if (g[derniere][x] === 'p') g[derniere][x] = 's';
      if (tn.bas === 'jupe' && jambes.length >= 3) {
        const y = jambes[jambes.length - 2];
        for (let x = 0; x < g[y].length; x++) if (g[y][x] === 'p') g[y][x] = 's';
        if (face || dos) g[jambes[0]] = elargir(g[jambes[0]]);
      }
    }
    if (tn.souliers === 'bottes' && derniere !== undefined) {
      for (let x = 0; x < g[derniere].length; x++) if ('ps'.indexOf(g[derniere][x]) >= 0) g[derniere][x] = 'b';
    }
  }

  // ------------------------------------------------------------------ les accessoires

  function accessoiriser(g, t, vue, acc) {
    const a = {};
    (acc || []).forEach(function (n) { a[n] = true; });
    if (t && t.yeux > 0) {
      const y = t.yeux, r = g[y];
      const yeux = [];
      for (let x = 0; x < r.length; x++) if (r[x] === 'o') yeux.push(x);
      if ((a.lunettes || a.lunettes_soleil) && yeux.length) {
        if (a.lunettes_soleil) yeux.forEach(function (x) { r[x] = 'e'; });
        if (vue === 'bas' && yeux.length >= 2) {
          for (let x = yeux[0] + 1; x < yeux[yeux.length - 1]; x++) if (r[x] === 's') r[x] = 'e';
        } else if (vue === 'cote') {
          if (r[yeux[0] - 1] === 's') r[yeux[0] - 1] = 'e';
        }
      }
      if (a.barbe && vue !== 'haut') {
        for (let yy = y + 1; yy < t.t0; yy++) {
          const rr = g[yy];
          const peau = [];
          for (let x = 0; x < rr.length; x++) if (rr[x] === 's') peau.push(x);
          if (!peau.length) continue;
          if (yy === y + 1) { rr[peau[0]] = 'h'; rr[peau[peau.length - 1]] = 'h'; } else peau.forEach(function (x) { rr[x] = 'h'; });
        }
      }
      if (a.moustache && vue !== 'haut' && g[y + 1]) {
        const rr = g[y + 1];
        if (vue === 'bas') { const m = Math.floor(t.milieu); if (rr[m] === 's') rr[m] = 'h'; if (rr[m + 1] === 's') rr[m + 1] = 'h'; } else {
          for (let x = rr.length - 1; x >= 0; x--) if (rr[x] === 's') { rr[x] = 'h'; break; }
        }
      }
    }
    const t0 = t ? t.t0 : rangeesDe(g, 'c')[0];
    if (t0 === undefined) return;
    const [xa, xb] = torse(g, t0);
    const milieu = Math.floor((xa + xb) / 2);
    if (a.sac_a_dos) {
      if (vue === 'haut') {
        for (let y = t0; y <= t0 + 2; y++) for (let x = milieu - 1; x <= milieu + 2; x++) if (lit(g, x, y) !== '.') pose(g, x, y, y === t0 + 2 ? 'A' : 'a');
      } else if (vue === 'bas') {
        pose(g, xa, t0, 'a'); pose(g, xb, t0, 'a');
      } else if (vue === 'cote') {
        for (let y = t0; y <= t0 + 2; y++) { pose(g, xa - 1, y, 'a'); if (lit(g, xa - 2, y) === '.') pose(g, xa - 2, y, 'k'); }
      }
    }
    if (a.cravate && vue === 'bas') {
      pose(g, milieu, t0, 'a'); pose(g, milieu + 1, t0, 'a');
      for (let y = t0 + 1; y <= t0 + 2; y++) if ('cCwQ'.indexOf(lit(g, milieu, y)) >= 0) pose(g, milieu, y, 'a');
    }
    if (a.foulard) {
      for (let x = 0; x < g[t0].length; x++) if ('cCQw'.indexOf(g[t0][x]) >= 0) g[t0][x] = 'a';
      if (vue === 'bas') pose(g, xa + 1, t0 + 1, 'a');
    }
  }

  // ------------------------------------------------------------------ la tenue enfilee

  /** La grille d'une pose habillee, en lettres — ce que `cuire` peint et ce que les juges lisent. */
  function grille(tn, nomPose, image) {
    const sq = squelette(tn.squelette || 'homme');
    const src = sq.poses[nomPose] && sq.poses[nomPose][image || 0];
    if (!src) return null;
    const g = src.map(function (r) { return r.slice(); });
    const vue = vueDe(nomPose);
    const t = vue ? tete(g) : null;
    if (t) coiffer(g, t, vue, tn.coiffure);
    habiller(g, t, vue, tn);
    accessoiriser(g, t, vue, tn.accessoires);
    if (t && tn.chapeau && tn.chapeau !== 'aucun') poserChapeau(g, t, vue, tn.chapeau);
    return g.map(function (r) { return r.join(''); });
  }

  // ------------------------------------------------------------------ couleurs

  function rgb(hex) { const n = parseInt(hex.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
  function hex(c) { return '#' + c.map(function (v) { return Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0'); }).join(''); }
  function melange(a, b, t) { const x = rgb(a), y = rgb(b); return hex([0, 1, 2].map(function (i) { return x[i] + (y[i] - x[i]) * t; })); }

  function palette(tn) {
    const s = tn.peau || '#e8b088', h = tn.cheveux || '#3a2a1a', c = tn.couleur_haut || '#7f8c8d';
    const p = tn.couleur_bas || '#2a2a3a', t = tn.couleur_chapeau || '#1a1a22', a = tn.accent || '#c0392b';
    return {
      k: '#101018', o: '#ffffff', e: '#1a1a22', w: '#efe6d0', W: '#f7f2e6', y: '#e8e23c', v: '#1a1a1a',
      s: s, S: melange(s, h, 0.45),
      h: h, H: melange(h, '#000000', 0.3),
      c: c, C: melange(c, '#000000', 0.28), Q: melange(c, '#ffffff', 0.3),
      p: p, b: tn.couleur_souliers || '#1a1a1a',
      t: t, T: melange(t, '#000000', 0.3), L: melange(t, '#ffffff', 0.4),
      a: a, A: melange(a, '#000000', 0.3),
    };
  }

  // ------------------------------------------------------------------ la cuisson

  const cache = new Map();

  function cle(tn) {
    return [tn.squelette, tn.peau, tn.cheveux, tn.coiffure, tn.chapeau, tn.couleur_chapeau, tn.haut,
            tn.couleur_haut, tn.motif, tn.bas, tn.couleur_bas, tn.souliers, tn.couleur_souliers,
            (tn.accessoires || []).join('+'), tn.accent].join('|');
  }

  function peindre(lignes, pal, w, h, miroir) {
    const c = Base.nouveauCanvas(w, h);
    const ctx = c.getContext('2d');
    for (let y = 0; y < h; y++) {
      const l = lignes[y];
      for (let x = 0; x < w; x++) {
        const ch = l[x];
        if (ch === '.' || ch === undefined) continue;
        ctx.fillStyle = pal[ch] || '#ff00ff';
        ctx.fillRect(miroir ? w - 1 - x : x, y, 1, 1);
      }
    }
    return c;
  }

  /** La tenue cuite, comme `Atlas.cuire` la rendrait : { w, h, ancre, poses, mains }. Les
      poses sont des GETTERS : chacune se peint la premiere fois qu'on la demande (un passant
      ne s'assoit pas toujours, ne fait pas toujours de geste). « gauche » est le miroir de
      « cote », comme dans `Atlas`. */
  function cuire(tn) {
    if (!tn) return null;
    const k = cle(tn);
    if (cache.has(k)) { const v = cache.get(k); cache.delete(k); cache.set(k, v); return v; }
    const sq = squelette(tn.squelette || 'homme');
    const pal = palette(tn);
    const poses = {};
    const peintes = {};
    const definir = function (nom, source, miroir) {
      Object.defineProperty(poses, nom, {
        enumerable: true, configurable: true,
        get: function () {
          if (!peintes[nom]) {
            peintes[nom] = sq.poses[source].map(function (g, i) {
              return peindre(grille(tn, source, i), pal, sq.w, sq.h, miroir);
            });
          }
          return peintes[nom];
        },
      });
    };
    for (const p in sq.poses) definir(p, p, false);
    for (const p in sq.poses) {
      const base = p === 'cote' ? '' : (p.endsWith('_cote') ? p.slice(0, -5) + '_' : null);
      if (base === null) continue;
      if (!sq.poses[base + 'gauche']) definir(base + 'gauche', p, true);
      if (!sq.poses[base + 'droite']) definir(base + 'droite', p, false);
    }
    const cuit = { w: sq.w, h: sq.h, ancre: sq.ancre, poses: poses, mains: sq.mains, tenue: tn };
    cache.set(k, cuit);
    while (cache.size > CACHE_MAX) cache.delete(cache.keys().next().value);
    return cuit;
  }

  // ------------------------------------------------------------------ le tirage

  function defs() { return (typeof B !== 'undefined' && B.defs && B.defs.garderobe) || null; }

  /** Un entier melange de `n` et d'un sel : le tirage est une EMPREINTE, jamais un de. */
  function melanger(n, sel) {
    let h = (n ^ Math.imul(sel + 0x9e3779b9, 0x85ebca6b)) >>> 0;
    h = Math.imul(h ^ (h >>> 16), 0x7feb352d) >>> 0;
    h = Math.imul(h ^ (h >>> 15), 0x846ca68b) >>> 0;
    return (h ^ (h >>> 16)) >>> 0;
  }

  /** Tire une tenue dans la garde-robe de l'archetype `slug`, a l'empreinte `graine`. Null si
      l'archetype n'a pas de garde-robe (il garde son corps dessine a la main). */
  function tirer(slug, graine) {
    const d = defs();
    const g = d && d.garde_robes && d.garde_robes[slug];
    if (!g) return null;
    let sel = 1;
    const un = function (liste) { return liste && liste.length ? liste[melanger(graine, sel++) % liste.length] : undefined; };
    const chance = function (p) { return (melanger(graine, sel++) % 1000) / 1000 < p; };
    const couleurDe = function (familles) { return un(d.couleurs[un(familles)] || d.couleurs.sobres); };
    const squel = un(g.squelettes);
    const vieux = squel === 'vieux';
    const tn = {
      squelette: squel,
      peau: un(g.peaux),
      cheveux: vieux ? un(['#8a8a8a', '#c8c8c8', '#e8e8e8']) : un(g.cheveux),
      coiffure: un(g.coiffures),
      haut: un(g.hauts),
      couleur_haut: g.haut_fixe || couleurDe(g.couleurs_haut),
      motif: un(g.motifs),
      bas: un(g.bas),
      couleur_bas: couleurDe(g.couleurs_bas),
      souliers: un(g.souliers),
      couleur_souliers: un(d.couleurs.souliers),
      chapeau: 'aucun',
      couleur_chapeau: couleurDe(g.couleurs_chapeau),
      accent: un(d.couleurs.vives),
      accessoires: [],
    };
    if (g.chapeaux.length && chance(g.chapeau_chance)) tn.chapeau = un(g.chapeaux);
    // Une jupe ou une robe, c'est la femme qui la porte ; un homme en jupe pioche un pantalon.
    if (squel !== 'femme' && tn.bas === 'jupe') tn.bas = 'pantalon';
    if (squel !== 'femme' && tn.haut === 'robe') tn.haut = 'chandail';
    const imberbe = squel === 'femme' || squel === 'enfant';
    d.accessoires.forEach(function (n) {
      const p = g.accessoires[n];
      if (!p || !chance(p)) return;
      if (imberbe && (n === 'barbe' || n === 'moustache')) return;
      if (n === 'moustache' && tn.accessoires.indexOf('barbe') >= 0) return;
      if (n === 'lunettes_soleil' && tn.accessoires.indexOf('lunettes') >= 0) return;
      tn.accessoires.push(n);
    });
    return tn;
  }

  /** La tenue de rue d'un personnage (`garderobe.tenue_du_personnage`), ou null. */
  function duPersonnage(slug) {
    const d = defs();
    return (d && d.personnages && d.personnages[slug]) || null;
  }

  /** La tenue du JOUEUR : le squelette d'homme, ses couleurs de toujours (`SPRITES.joueur`),
      la coupe du barbier (`partie.cheveux`), le linge porte (`partie.tenue`, une piece `corps`
      de `magasins.TENUES`) et le chapeau (`partie.chapeau`, une piece `tete`).
      ⚠️ Une vieille sauvegarde peut PORTER la casquette de la foire comme linge (elle etait une
      couleur de chandail avant la garde-robe) : elle passe sur la tete, et le chandail revient. */
  function duJoueur(partie, defsJeu) {
    const tenues = (defsJeu && defsJeu.tenues) || [];
    const trouve = function (s) { return s ? tenues.find(function (t) { return t.slug === s; }) || null : null; };
    const pal = SPRITES.joueur.pal;
    let corps = trouve(partie.tenue), tete = trouve(partie.chapeau);
    if (corps && corps.emplacement === 'tete') { if (!tete) tete = corps; corps = trouve('chandail'); }
    if (tete && tete.emplacement !== 'tete') tete = null;
    const piece = (corps && corps.piece) || {};
    return {
      squelette: 'homme', peau: pal.s, cheveux: partie.cheveux || pal.h, coiffure: 'courte',
      haut: piece.haut || 'chandail', couleur_haut: corps ? corps.couleur : pal.c, motif: piece.motif || 'uni',
      bas: 'pantalon', couleur_bas: pal.p, souliers: 'souliers', couleur_souliers: pal.b,
      chapeau: tete && tete.piece ? tete.piece.chapeau : 'aucun', couleur_chapeau: tete ? tete.couleur : '#1a1a22',
      accessoires: (piece.accessoires || []).slice(), accent: '#c0392b',
    };
  }

  /** Les couleurs de rue d'une tenue, au format des echanges de palette (`e.swaps`) : ce que
      le reste du jeu lit encore (le cavalier d'une moto, l'autobus qui recree un passant). */
  function couleurs(tn) {
    return { c: tn.couleur_haut, h: tn.cheveux, s: tn.peau, p: tn.couleur_bas };
  }

  function vider() { cache.clear(); }

  return { MARGE_HAUT, MARGE_COTE, CACHE_MAX, CHAPEAUX, squelette, tete, vueDe, grille, palette,
           cuire, tirer, duPersonnage, duJoueur, couleurs, vider, get taille() { return cache.size; } };
})();
