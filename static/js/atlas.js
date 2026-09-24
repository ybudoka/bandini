/* Bandini — atlas : cuisson des sprites pixel definis en code.

   Un sprite = { w, h, ancre: [ax, ay], pal: { lettre: '#rrggbb' }, poses: { nom: [grilles] } }
   ou une grille est un tableau de h chaines de w caracteres ; '.' = transparent.
   La cuisson produit un canvas par image, une fois, a 1x : l'atlas ne depend
   pas de l'echelle d'affichage et n'est jamais invalide par un redimensionnement.

   `swaps` remplace des couleurs de la palette (tenues, carrosseries). */

const Atlas = (function () {
  'use strict';

  const cache = new Map();

  /** Liste les problemes d'une definition ; vide si tout est bon. */
  function valider(nom, def) {
    const problemes = [];
    if (!def || !def.poses) { problemes.push(nom + ' : pas de poses'); return problemes; }
    for (const pose in def.poses) {
      const images = def.poses[pose];
      if (!Array.isArray(images) || !images.length) { problemes.push(nom + '.' + pose + ' : aucune image'); continue; }
      images.forEach(function (grille, i) {
        if (grille.length !== def.h) problemes.push(nom + '.' + pose + '[' + i + '] : ' + grille.length + ' lignes au lieu de ' + def.h);
        grille.forEach(function (ligne, y) {
          if (ligne.length !== def.w) problemes.push(nom + '.' + pose + '[' + i + '] ligne ' + y + ' : ' + ligne.length + ' colonnes au lieu de ' + def.w);
          for (const ch of ligne) {
            if (ch !== '.' && !(ch in def.pal)) problemes.push(nom + '.' + pose + '[' + i + '] : « ' + ch + ' » absent de la palette');
          }
        });
      });
    }
    return problemes;
  }

  function peindreGrille(ctx, grille, pal, w, h, miroir) {
    for (let y = 0; y < h; y++) {
      const ligne = grille[y];
      for (let x = 0; x < w; x++) {
        const ch = ligne[x];
        if (ch === '.') continue;
        ctx.fillStyle = pal[ch];
        ctx.fillRect(miroir ? w - 1 - x : x, y, 1, 1);
      }
    }
  }

  /** Cuit un sprite ; `swaps` = { lettre: couleur }. Rend { w, h, ancre, poses }. */
  function cuire(nom, def, swaps) {
    const cle = nom + '|' + (swaps ? JSON.stringify(swaps) : '');
    if (cache.has(cle)) return cache.get(cle);
    const pal = Object.assign({}, def.pal, swaps || {});
    const poses = {};
    for (const pose in def.poses) {
      poses[pose] = def.poses[pose].map(function (grille) {
        const c = Base.nouveauCanvas(def.w, def.h);
        peindreGrille(c.getContext('2d'), grille, pal, def.w, def.h, false);
        return c;
      });
    }
    // « gauche » = miroir de « cote » si le sprite n'en definit pas — et de
    // meme pour toute pose « X_cote » (frappe_cote → frappe_gauche/droite).
    for (const pose in def.poses) {
      const base = pose === 'cote' ? '' : (pose.endsWith('_cote') ? pose.slice(0, -5) + '_' : null);
      if (base === null || def.poses[base + 'gauche']) continue;
      poses[base + 'gauche'] = def.poses[pose].map(function (grille) {
        const c = Base.nouveauCanvas(def.w, def.h);
        peindreGrille(c.getContext('2d'), grille, pal, def.w, def.h, true);
        return c;
      });
      poses[base + 'droite'] = poses[pose];
    }
    const cuit = { w: def.w, h: def.h, ancre: def.ancre || [def.w >> 1, def.h - 1], poses: poses };
    cache.set(cle, cuit);
    return cuit;
  }

  /** Les rangees pleines d'une grille : [premiere, derniere]. */
  function caisseDe(grille) {
    let y0 = -1, y1 = -1;
    grille.forEach(function (ligne, y) {
      if (/[^.]/.test(ligne)) { if (y0 < 0) y0 = y; y1 = y; }
    });
    return [y0, y1];
  }

  /** LE DESSIN QUI TOURNE : le char vu d'en haut, nez au NORD.

      C'est la pose `haut` — le toit — avec les PHARES de la pose `bas` poses
      sur son nez. Les deux poses sont le meme toit lu dans l'autre sens :
      `haut` ne montre que les feux arriere (le char s'eloigne), `bas` que les
      phares (il vient). Un seul dessin qui tourne doit porter LES DEUX, sinon
      un char qui vient vers nous roule tous phares eteints.

      ⚠️ Le retournement se fait sur la CAISSE, pas sur la grille : le dessin
      n'y est pas centre (l'ancre est la ligne de sol, et il reste deux rangees
      vides sous les roues). Un miroir sur la grille decalerait les phares
      d'une rangee — assez pour les poser dans le pare-chocs.

      ⚠️ Et un phare ne DEBORDE pas : il ne se pose que la ou il y a deja de la
      tole. Le nez du toit est plus etroit que sa queue, et deux pixels de
      jaune dans le vide auraient fait des moustaches. */
  function toitDe(nom, def) {
    const cle = 'toit|' + nom;
    if (cache.has(cle)) return cache.get(cle);
    const haut = (def.poses.haut || def.poses.base)[0];
    const grille = haut.map(function (ligne) { return ligne.split(''); });
    const bas = def.poses.bas && def.poses.bas[0];
    if (bas) {
      const caisse = caisseDe(haut);
      for (let y = 0; y < bas.length; y++) {
        const cible = caisse[0] + caisse[1] - y;
        if (cible < 0 || cible >= grille.length) continue;
        for (let x = 0; x < bas[y].length; x++) {
          if (bas[y][x] === 'l' && grille[cible][x] !== '.') grille[cible][x] = 'l';
        }
      }
    }
    const fini = grille.map(function (ligne) { return ligne.join(''); });
    cache.set(cle, fini);
    return fini;
  }

  /** UNE MACHINE A DEUX ROUES, vue a un cap : la grille de lettres, `cote` x
      `cote`, le point de sol au milieu de l'empreinte pose au CENTRE.

      ⚠️ **Pourquoi pas un toit qui tourne, comme les chars.** Retour de Martin,
      capture a l'appui : « il faut ameliorer ca ». Vu d'en haut, un velo est un
      BATON avec une barre en travers — c'est ce qui roulait, et le cycliste de
      profil pose dessus lisait comme un passant sur une echasse. Un toit d'auto
      dit ce qu'il est ; celui d'un velo, non. Et une elevation ne se laisse pas
      tourner (un flanc pivote de 40 degres, c'est une machine qui cabre).

      ⚠️ **Alors la machine est decrite EN VOLUME, et elle se projette.** Un
      deux-roues est presque plat — deux roues dans un meme plan vertical, un
      cadre, un guidon en travers — et c'est exactement ce qu'une projection
      rend bien : de profil, deux roues RONDES ; de dos, un trait et le guidon
      ; entre les deux, des roues en ellipse. Les 32 caps suivent l'ombre au
      cran pres, comme le toit des chars, et chacun est un vrai dessin.

      La vue est celle de toute la ville : ce qui est debout se dessine debout
      (`z` monte a l'ecran, un pixel pour un pixel), et le sol se voit DE BIAIS
      — la profondeur est ecrasee par `machine.profondeur`, le meme biais que
      l'ombre (`vehicules.OMBRE`), sinon le guidon d'un velo de profil montait
      en antenne de cinq pixels.

      ⚠️ `u` va vers l'avant, `w` vers la droite de la machine, `z` en haut. Le
      cap `angle` est celui du moteur : 0 a l'EST. Ce qui cache quoi se decide
      point par point — le plus pres de l'oeil gagne (le plus au sud, le plus
      haut), et `avance` depasse d'une fraction pour qu'un phare ou un guidon
      ne se noie pas dans ce qu'il touche.

      ⚠️ `tangage` (facultatif, en radians) : la machine PENCHE avant de tourner,
      le nez vers le haut quand il est positif — un chariot de montagne russe qui
      grimpe la chaine, qui plonge, et qui passe le looping LA TETE EN BAS (a pi,
      son dessus est dessous). Elle pivote autour de son point de sol, la ou elle
      tient au rail. Absent, rien ne change pour le parc. */
  function projeter(machine, angle, cote, tangage) {
    const K = machine.profondeur;
    const ca = Math.cos(angle), sa = Math.sin(angle);
    const penche = !!tangage, ct = Math.cos(tangage || 0), st = Math.sin(tangage || 0);
    const milieu = cote / 2;
    const prof = new Float64Array(cote * cote).fill(-Infinity);
    const lettres = new Array(cote * cote).fill('.');
    // ⚠️ L'epsilon : a -PI/2, cos vaut 6e-17 et non 0. Un point pile sur une
    // arete de pixel tombait d'un cote ou de l'autre selon le cap, et le dessin
    // du nord n'etait plus le miroir exact de celui du sud.
    function point(u, w, z, ch, avance) {
      if (penche) { const u2 = u * ct - z * st; z = u * st + z * ct; u = u2; }
      const sol = u * sa + w * ca;
      const x = Math.floor(milieu + u * ca - w * sa + 1e-6), y = Math.floor(milieu + sol * K - z + 1e-6);
      if (x < 0 || y < 0 || x >= cote || y >= cote) return;
      const d = sol + K * z + (avance || 0), i = y * cote + x;
      if (d > prof[i]) { prof[i] = d; lettres[i] = ch; }
    }
    function tube(a, b, ch, avance) {
      const n = Math.max(2, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]) * 5));
      for (let k = 0; k <= n; k++) {
        const t = k / n;
        point(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t, ch, avance);
      }
    }
    function anneau(u, w, z, r, ch, avance) {
      const n = Math.ceil(r * 40);
      for (let k = 0; k < n; k++) {
        const f = k / n * Math.PI * 2;
        point(u + r * Math.cos(f), w, z + r * Math.sin(f), ch, avance);
      }
    }
    for (const p of machine.pieces) {
      if (p[0] === 'roue') {
        // [u, rayon, pneu, jante, moyeu, largeur, w] — le pneu en deux passes
        // pour qu'il reste plein dans ses ellipses, `largeur` > 1 pour une moto
        // ou un char, `w` pour une roue qui n'est pas dans l'axe.
        const u = p[1], r = p[2], larges = p[6] || 1, w0 = p[7] || 0;
        for (let e = 0; e < larges; e++) {
          const w = w0 + (larges > 1 ? (e - (larges - 1) / 2) * 0.8 : 0);
          anneau(u, w, r, r - 0.1, p[3]);
          anneau(u, w, r, r - 0.7, p[3]);
        }
        // ⚠️ La jante et le moyeu sur la face du DEHORS : un char a une roue de
        // chaque cote, et de chacune on ne voit que l'exterieur.
        const dehors = w0 + Math.sign(w0) * (larges - 1) * 0.4;
        if (p[4]) anneau(u, dehors, r, r - 1.4, p[4], 0.01);
        if (p[5]) point(u, dehors, r, p[5], 0.3);
      } else if (p[0] === 'profil') {
        // [[[u, z], ...], largeur, flanc, aretes, avance] : une SILHOUETTE DE
        // PROFIL extrudee sur la largeur — un capot et un pare-brise en pente,
        // des passages de roue, ce qu'une boite ne sait pas faire. Les deux
        // flancs se remplissent de `flanc` ; l'arete k -> k+1 balaie la largeur
        // avec la lettre `aretes[k]` ('.' : rien, elle ne se voit pas).
        // ⚠️ `largeur` est [w0, w1], ou un PLAN [[u, demi-largeur], ...] : une
        // caisse qui se pince au nez et a la queue, vue d'en haut, au lieu
        // d'un pave aux coins vifs.
        const P = p[1], av = p[5], pas = 0.25;
        const plan = Array.isArray(p[2][0]) ? p[2] : null;
        const bords = function (u) {
          if (!plan) return p[2];
          let d = plan[0][1];
          for (let k = 1; k < plan.length; k++) {
            const a = plan[k - 1], b = plan[k];
            if (u >= a[0] && u <= b[0]) { d = a[1] + (b[1] - a[1]) * (u - a[0]) / (b[0] - a[0]); break; }
            if (u > b[0]) d = b[1];
          }
          return [-d, d];
        };
        let u0 = Infinity, u1 = -Infinity, z0 = Infinity, z1 = -Infinity;
        P.forEach(function (q) { u0 = Math.min(u0, q[0]); u1 = Math.max(u1, q[0]); z0 = Math.min(z0, q[1]); z1 = Math.max(z1, q[1]); });
        const dedans = function (u, z) {
          let c = false;
          for (let k = 0, m = P.length - 1; k < P.length; m = k++) {
            const a = P[k], b = P[m];
            if ((a[1] > z) !== (b[1] > z) && u < (b[0] - a[0]) * (z - a[1]) / (b[1] - a[1]) + a[0]) c = !c;
          }
          return c;
        };
        for (let u = u0; u <= u1 + 1e-6; u += pas) {
          for (let z = z0; z <= z1 + 1e-6; z += pas) {
            if (dedans(u, z)) { const W = bords(u); point(u, W[0], z, p[3], av); point(u, W[1], z, p[3], av); }
          }
        }
        for (let k = 0; k < P.length; k++) {
          const ch = p[4][k];
          if (!ch || ch === '.') continue;
          const a = P[k], b = P[(k + 1) % P.length];
          const n = Math.max(2, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / pas));
          for (let t = 0; t <= n; t++) {
            const u = a[0] + (b[0] - a[0]) * t / n, z = a[1] + (b[1] - a[1]) * t / n, W = bords(u);
            for (let w = W[0]; w <= W[1] + 1e-6; w += pas) point(u, w, z, ch, av);
          }
        }
      } else if (p[0] === 'damier') {
        // [[u0, u1], z, w, lettre] : un pixel sur deux, sur deux rangees
        // decalees — le damier d'un taxi, a l'echelle d'une portiere.
        for (let u = p[1][0]; u >= p[1][1] - 1e-6; u -= 1) {
          point(u, p[3], Math.round(p[1][0] - u) % 2 === 0 ? p[2] : p[2] - 1, p[4], 1.0);
        }
      } else if (p[0] === 'tube') {
        tube(p[1], p[2], p[3], p[4]);
      } else if (p[0] === 'point') {
        point(p[1][0], p[1][1], p[1][2], p[2], p[3]);
      } else if (p[0] === 'bloc') {
        // [[u0, u1], [w0, w1], [z0, z1], dessus, flanc, bout, avance] : une
        // boite pleine, ses six faces echantillonnees au quart de pixel.
        const U = p[1], W = p[2], Z = p[3], pas = 0.25, av = p[7];
        for (let u = U[0]; u <= U[1] + 1e-6; u += pas) {
          for (let w = W[0]; w <= W[1] + 1e-6; w += pas) { point(u, w, Z[1], p[4], av); point(u, w, Z[0], p[5], av); }
          for (let z = Z[0]; z <= Z[1] + 1e-6; z += pas) { point(u, W[0], z, p[5], av); point(u, W[1], z, p[5], av); }
        }
        for (let w = W[0]; w <= W[1] + 1e-6; w += pas) {
          for (let z = Z[0]; z <= Z[1] + 1e-6; z += pas) { point(U[0], w, z, p[6], av); point(U[1], w, z, p[6], av); }
        }
      }
    }
    // LE CONTOUR : la silhouette cernee de `k`, comme tout ce qui est dessine
    // a la main dans la ville. Seulement le DEHORS — un trait sur les aretes
    // du dedans ferait des vitres en vitrail. Un velo n'en veut pas : ses
    // tubes d'un pixel deviendraient des barres de trois.
    // L'ARRONDI : un pixel de moins a chaque coin VIF de la silhouette — la
    // ou un bord droit en rencontre un autre a angle droit. ⚠️ Pas a chaque
    // marche d'escalier : un bord en diagonale est fait de coins, et les ronger
    // amincirait tout char de trois quarts. On ne retire un coin que si ses
    // deux bords continuent tout droit au-dela de lui. Juge sur la silhouette
    // d'avant (`avant`), pour qu'un coin rogne n'en fasse pas naitre un autre.
    if (machine.arrondi) {
      const avant = lettres.slice();
      const vide = function (x, y) { return x < 0 || y < 0 || x >= cote || y >= cote || avant[y * cote + x] === '.'; };
      for (let y = 0; y < cote; y++) {
        for (let x = 0; x < cote; x++) {
          if (vide(x, y)) continue;
          for (const [dx, dy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
            if (vide(x + dx, y) && vide(x, y + dy) && vide(x + dx, y + dy) &&
                !vide(x - dx, y) && vide(x - dx, y + dy) && !vide(x, y - dy) && vide(x + dx, y - dy)) {
              lettres[y * cote + x] = '.';
              break;
            }
          }
        }
      }
    }
    if (machine.contour) {
      const peint = lettres.slice();
      for (let y = 0; y < cote; y++) {
        for (let x = 0; x < cote; x++) {
          const i = y * cote + x;
          if (peint[i] !== '.') continue;
          if ((x > 0 && peint[i - 1] !== '.') || (x < cote - 1 && peint[i + 1] !== '.') ||
              (y > 0 && peint[i - cote] !== '.') || (y < cote - 1 && peint[i + cote] !== '.')) lettres[i] = 'k';
        }
      }
    }
    const grille = [];
    for (let y = 0; y < cote; y++) grille.push(lettres.slice(y * cote, (y + 1) * cote).join(''));
    return grille;
  }

  /** UN cap d'un char, cuit A LA DEMANDE : le toit tourne de `i / n` de tour.

      ⚠️ **Un cap a la fois, et seulement ceux qu'on a vraiment montres.** Les
      32 caps de toute la flotte, cuits d'avance, pesaient un millier de
      canevas pour rien : un char du trafic roule sur des rails et n'en montre
      que quatre. Le joueur, lui, les prend tous — et c'est lui qui conduit.

      ⚠️ Le canevas est CARRE, de cote la diagonale du dessin (arrondie au
      pair), pour qu'aucun cap ne soit rogne ; son milieu tombe sur `centre`,
      le centre de l'EMPREINTE du catalogue — pas celui de la grille. Le
      dessin ne tourne donc pas autour d'un point a lui : il tourne autour de
      ce qui bloque, comme l'ombre.

      ⚠️ Le lissage doit rester eteint sur le canevas TOURNE : un char tourne
      avec `imageSmoothingEnabled` a true devient une tache floue. */
  function cuireCap(nom, def, swaps, n, i, centre, tangage) {
    // ⚠️ `tangage` : un cran sur `n`, comme le cap (voir `projeter`) — seulement
    // pour une machine. Les cles d'avant restent les memes quand il est absent.
    const t = tangage ? ((tangage % n) + n) % n : 0;
    const sel = swaps ? JSON.stringify(swaps) : '';
    const cle = 'cap|' + nom + '|' + n + '|' + i + (t ? '|t' + t : '') + '|' + sel;
    if (cache.has(cle)) return cache.get(cle);
    // ⚠️ UN DEUX-ROUES NE TOURNE PAS SON TOIT : il se PROJETTE au cap (voir
    // `projeter`). La grille de lettres ne depend pas de la couleur, elle se
    // cuit une fois par cap ; le canevas, lui, une fois par couleur.
    if (def.machine) {
      const cleGrille = 'machine|' + nom + '|' + n + '|' + i + (t ? '|t' + t : '');
      let grille = cache.get(cleGrille);
      if (!grille) {
        grille = projeter(def.machine, i * Math.PI * 2 / n - Math.PI / 2, def.w, t * Math.PI * 2 / n);
        cache.set(cleGrille, grille);
      }
      const c = Base.nouveauCanvas(def.w, def.w);
      peindreGrille(c.getContext('2d'), grille, Object.assign({}, def.pal, swaps || {}), def.w, def.w, false);
      c.cote = def.w;
      cache.set(cle, c);
      return c;
    }
    const cleBase = 'toit1|' + nom + '|' + sel;
    let base = cache.get(cleBase);
    if (!base) {
      base = Base.nouveauCanvas(def.w, def.h);
      peindreGrille(base.getContext('2d'), toitDe(nom, def), Object.assign({}, def.pal, swaps || {}),
                    def.w, def.h, false);
      cache.set(cleBase, base);
    }
    let cote = Math.ceil(Math.hypot(def.w, def.h)) + 2;
    cote += cote % 2;
    const c = Base.nouveauCanvas(cote, cote);
    const ctx = c.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    ctx.translate(cote / 2, cote / 2);
    ctx.rotate(i * Math.PI * 2 / n);
    ctx.drawImage(base, -centre[0], -centre[1]);
    c.cote = cote;
    cache.set(cle, c);
    return c;
  }

  /** La grille de lettres d'une machine a ce cap (`n` crans, le `i`-ieme) — celle-la
      meme que `cuireCap` peint, et que la projection a decidee point par point (le plus
      pres de l'oeil gagne). ⚠️ C'est elle qui SAIT ce qui se voit : une lampe dont les
      pixels n'y sont pas est cachee par la caisse (`Vehicules.allumerLesPhares`). */
  function grilleDuCap(nom, def, n, i) {
    if (!def || !def.machine) return null;
    const cle = 'machine|' + nom + '|' + n + '|' + i;
    let grille = cache.get(cle);
    if (!grille) {
      grille = projeter(def.machine, i * Math.PI * 2 / n - Math.PI / 2, def.w, 0);
      cache.set(cle, grille);
    }
    return grille;
  }

  /** Ou tombe, dans cette grille, le point (`u` avant, `w` droite, `z` haut) de la
      machine — le calcul de `projeter`, au pixel pres. */
  function ouTombe(def, n, i, u, w, z) {
    const angle = i * Math.PI * 2 / n - Math.PI / 2, ca = Math.cos(angle), sa = Math.sin(angle);
    const milieu = def.w / 2, sol = u * sa + w * ca;
    return { x: Math.floor(milieu + u * ca - w * sa + 1e-6), y: Math.floor(milieu + sol * def.machine.profondeur - z + 1e-6) };
  }

  /** Cuit une tuile 16x16 par un peintre procedural (variante = entier stable). */
  function cuireTuile(glyphe, variante, peintre) {
    const cle = 'tuile|' + glyphe + '|' + variante;
    if (cache.has(cle)) return cache.get(cle);
    const c = Base.nouveauCanvas(TT, TT);
    peintre(c.getContext('2d'), variante, TT);
    cache.set(cle, c);
    return c;
  }

  /** Un dessin procedural quelconque, cuit une fois par cle. */
  function cuirePeintre(cle, w, h, peintre) {
    if (cache.has(cle)) return cache.get(cle);
    const c = Base.nouveauCanvas(w, h);
    peintre(c.getContext('2d'), w, h);
    cache.set(cle, c);
    return c;
  }

  //: ⚠️ Un glyphe absent tombe sur « ? » (l'apostrophe courbe, le tiret
  //: cadratin, les guillemets…). Ceux-ci se ramenent a ce que la police sait
  //: ecrire AVANT le dessin. Les LETTRES ACCENTUEES n'y sont plus : longtemps
  //: HÔPITAL s'est ecrit HOPITAL (« a cinq pixels de haut, un accent ne se lit
  //: pas »), jusqu'a la demande de Martin du 17 sept. 2026 — « le jeu doit
  //: supporter les accents ». Elles gardent leur accent et `lettre` le dessine.
  const SANS_ACCENT = {
    'Œ': 'OE', 'Æ': 'AE',
    '’': "'", '‘': "'", '«': '"', '»': '"', '“': '"', '”': '"', '—': '-', '–': '-', '…': '...',
  };

  //: ⚠️ Meme piege avec les espaces invisibles : toLocaleString('fr-CA') separe
  //: les milliers par une espace fine insecable (U+202F), que la police ne
  //: connait pas — la fortune s'affichait « 1?078 $ ». Toute espace Unicode
  //: (fine, insecable, tabulation, saut de ligne) redevient donc une espace.
  const ESPACES = /\s/;

  //: Un accent qui ne s'est pas compose a sa lettre (« E » suivi de U+0301,
  //: tel quel apres NFC parce que la paire n'existe pas en un caractere) ne
  //: prend pas une case a lui : il tomberait sur « ? » et decalerait la ligne.
  const COMBINANT = /\p{M}/u;

  /** Majuscules, accents compris, sans ponctuation courbe : ce que la police sait ecrire.
      ⚠️ Une lettre accentuee reste UN caractere (NFC) : `largeurTexte` compte
      les caracteres, et un accent n'elargit pas sa lettre. */
  function normaliser(s) {
    let out = '';
    for (const ch of String(s).normalize('NFC').toUpperCase()) {
      if (ch in SANS_ACCENT) out += SANS_ACCENT[ch];
      else if (COMBINANT.test(ch)) continue;
      else out += ESPACES.test(ch) ? ' ' : ch;
    }
    return out;
  }

  //: Chaque caractere se decompose une fois : le glyphe de sa lettre de base
  //: et ses accents (`MARQUES_PIXEL`). « É » donne le « E » de la police et
  //: l'aigu ; « Ñ », sans tilde dessine, garde au moins son « N » au lieu d'un
  //: « ? ». Le cache tient : il n'y a pas cent caracteres dans tout le jeu.
  const LETTRES = new Map();
  function lettre(ch) {
    let l = LETTRES.get(ch);
    if (l) return l;
    const police = POLICE_PIXEL;
    const marques = (typeof MARQUES_PIXEL !== 'undefined') ? MARQUES_PIXEL : {};
    let glyphe = police[ch] || null;
    const accents = [];
    if (!glyphe) {
      const nfd = ch.normalize('NFD');
      glyphe = police[nfd[0]] || null;
      if (glyphe) for (const m of nfd.slice(1)) if (marques[m]) accents.push(marques[m]);
    }
    l = { glyphe: glyphe, accents: accents };
    LETTRES.set(ch, l);
    return l;
  }

  /** La police sait-elle ecrire ce caractere (deja normalise) ? Sa lettre de base suffit. */
  function connait(ch) {
    return typeof POLICE_PIXEL !== 'undefined' && lettre(ch).glyphe !== null;
  }

  /** Texte en police pixel 3x5 (majuscules, chiffres, ponctuation). */
  function texte(ctx, s, x, y, couleur, echelle) {
    const e = echelle || 1;
    const police = (typeof POLICE_PIXEL !== 'undefined') ? POLICE_PIXEL : null;
    if (!police) return;
    ctx.fillStyle = couleur || '#fff';
    let cx = x;
    s = normaliser(s);
    for (const ch of s) {
      const l = lettre(ch);
      const g = l.glyphe || police['?'];
      if (ch !== ' ' && g) {
        for (let i = 0; i < 15; i++) {
          if (g[i] === '1') ctx.fillRect(cx + (i % 3) * e, y + Math.floor(i / 3) * e, e, e);
        }
        // L'accent prend l'interligne : trois rangs au-dessus de la lettre
        // (la cedille, deux dessous). Ni la largeur ni la ligne ne bougent.
        for (const a of l.accents) {
          for (let i = 0; i < 6; i++) {
            if (a.bits[i] === '1') ctx.fillRect(cx + (i % 3) * e, y + (a.dy + Math.floor(i / 3)) * e, e, e);
          }
        }
      }
      cx += 4 * e;
      B.stats.rects++;
    }
    return cx - x;
  }

  function largeurTexte(s, echelle) { return normaliser(s).length * 4 * (echelle || 1) - (echelle || 1); }

  function vider() { cache.clear(); }

  return { valider, cuire, toitDe, projeter, cuireCap, grilleDuCap, ouTombe, cuireTuile, cuirePeintre, texte, largeurTexte, normaliser, connait, vider, get taille() { return cache.size; } };
})();
