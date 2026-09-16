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
      ne se noie pas dans ce qu'il touche. */
  function projeter(machine, angle, cote) {
    const K = machine.profondeur;
    const ca = Math.cos(angle), sa = Math.sin(angle);
    const milieu = cote / 2;
    const prof = new Float64Array(cote * cote).fill(-Infinity);
    const lettres = new Array(cote * cote).fill('.');
    // ⚠️ L'epsilon : a -PI/2, cos vaut 6e-17 et non 0. Un point pile sur une
    // arete de pixel tombait d'un cote ou de l'autre selon le cap, et le dessin
    // du nord n'etait plus le miroir exact de celui du sud.
    function point(u, w, z, ch, avance) {
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
        // [u, rayon, pneu, jante, moyeu, largeur] — le pneu en deux passes pour
        // qu'il reste plein dans ses ellipses, `largeur` > 1 pour une moto.
        const u = p[1], r = p[2], larges = p[6] || 1;
        for (let e = 0; e < larges; e++) {
          const w = larges > 1 ? (e - (larges - 1) / 2) * 0.8 : 0;
          anneau(u, w, r, r - 0.1, p[3]);
          anneau(u, w, r, r - 0.7, p[3]);
        }
        if (p[4]) anneau(u, 0, r, r - 1.4, p[4], 0.01);
        if (p[5]) point(u, 0, r, p[5], 0.3);
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
  function cuireCap(nom, def, swaps, n, i, centre) {
    const sel = swaps ? JSON.stringify(swaps) : '';
    const cle = 'cap|' + nom + '|' + n + '|' + i + '|' + sel;
    if (cache.has(cle)) return cache.get(cle);
    // ⚠️ UN DEUX-ROUES NE TOURNE PAS SON TOIT : il se PROJETTE au cap (voir
    // `projeter`). La grille de lettres ne depend pas de la couleur, elle se
    // cuit une fois par cap ; le canevas, lui, une fois par couleur.
    if (def.machine) {
      const cleGrille = 'machine|' + nom + '|' + n + '|' + i;
      let grille = cache.get(cleGrille);
      if (!grille) {
        grille = projeter(def.machine, i * Math.PI * 2 / n - Math.PI / 2, def.w);
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

  //: ⚠️ A cinq pixels de haut, un accent ne se lit pas ; et un glyphe absent
  //: tombait sur « ? » (HÔPITAL, CASSE-CROÛTE, BÂTON, l'apostrophe courbe…).
  //: On ramene donc chaque lettre a sa base AVANT de la dessiner.
  const SANS_ACCENT = {
    'À': 'A', 'Â': 'A', 'Ä': 'A', 'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E', 'Î': 'I', 'Ï': 'I',
    'Ô': 'O', 'Ö': 'O', 'Ù': 'U', 'Û': 'U', 'Ü': 'U', 'Ç': 'C', 'Œ': 'OE', 'Æ': 'AE', 'Ÿ': 'Y',
    '’': "'", '‘': "'", '«': '"', '»': '"', '“': '"', '”': '"', '—': '-', '–': '-', '…': '...',
  };

  //: ⚠️ Meme piege avec les espaces invisibles : toLocaleString('fr-CA') separe
  //: les milliers par une espace fine insecable (U+202F), que la police ne
  //: connait pas — la fortune s'affichait « 1?078 $ ». Toute espace Unicode
  //: (fine, insecable, tabulation, saut de ligne) redevient donc une espace.
  const ESPACES = /\s/;

  /** Majuscules sans accent ni ponctuation courbe : ce que la police sait ecrire. */
  function normaliser(s) {
    let out = '';
    for (const ch of String(s).toUpperCase()) {
      if (ch in SANS_ACCENT) out += SANS_ACCENT[ch];
      else out += ESPACES.test(ch) ? ' ' : ch;
    }
    return out;
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
      const g = police[ch] || police['?'];
      if (ch !== ' ' && g) {
        for (let i = 0; i < 15; i++) {
          if (g[i] === '1') ctx.fillRect(cx + (i % 3) * e, y + Math.floor(i / 3) * e, e, e);
        }
      }
      cx += 4 * e;
      B.stats.rects++;
    }
    return cx - x;
  }

  function largeurTexte(s, echelle) { return normaliser(s).length * 4 * (echelle || 1) - (echelle || 1); }

  function vider() { cache.clear(); }

  return { valider, cuire, toitDe, projeter, cuireCap, cuireTuile, cuirePeintre, texte, largeurTexte, normaliser, vider, get taille() { return cache.size; } };
})();
