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

  return { valider, cuire, toitDe, cuireCap, cuireTuile, cuirePeintre, texte, largeurTexte, normaliser, vider, get taille() { return cache.size; } };
})();
