/* Bandini — le sillage et l'ecume (docs/jalons/les-bateaux-ne-sont-pas-des-chars.md, vague 5).

   Une coque qui file laisse derriere elle deux bras d'ecume qui s'ouvrent (le V d'un sillage), le bouillon blanc de
   son helice, et a l'etrave une moustache qui grandit avec la vitesse. Le traversier et la navette aussi.

   ⚠️ RIEN DE TIRE, RIEN DE NE : aucun de, aucune entite, aucune particule (`Entites.remous` tire des des). Les points
   du sillage vivent ICI (`traces`, une table cle -> points), pas sur le vehicule — ils ne vont ni dans la sauvegarde
   ni dans le hasard de la ville. Un point est pose toutes les `pas` images (`maj`, le temps du monde : `B.t`), et
   s'efface au bout de `vie` images ; le dessin le lit.

   ⚠️ PEINT SOUS LES COQUES (`Jeu.rendre`, avec le sol) : la coque cache le debut de son sillage, et l'ecume ne se pose
   jamais sur la terre (chaque goutte lit `Monde.estEau`). */

const Sillage = (function () {
  'use strict';

  //: ⚠️ Du ressenti que Python ne lit pas : ici, pas dans le paquet (comme `Glace`, `Derapage`).
  const REGLAGES = {
    //: Sous cette erre (px/image), pas de sillage : une coque qui derive ne fend rien.
    "vitesse_min": 0.25,
    //: Un point du sillage toutes les `pas` images ; il vit `vie` images.
    "pas": 2, "vie": 110,
    //: Les bras s'ecartent de `ouverture` px par image d'age, a pleine erre (`pleine` px/image).
    "ouverture": 0.2, "pleine": 1.6,
    //: Le bouillon de l'helice : blanc, au milieu, `bouillon_vie` images.
    "bouillon_vie": 46,
    //: La moustache d'etrave : `moustache[0]` px, plus `moustache[1]` par px/image d'erre, au-dessus de `moustache_min`.
    "moustache": [3, 4], "moustache_min": 0.8,
    //: Jusqu'ou de l'ecran on garde la trace d'une coque (px, depuis le centre de la vue).
    "portee": 420,
  };

  //: cle (le vehicule, ou le nom d'un bateau a l'heure) -> { pts: [{x, y, a, s, l, n}], vu: B.t }
  const traces = new Map();
  //: Le dernier centre des bateaux a l'heure, pour leur cap et leur erre.
  const derniers = {};

  function reglages() { return REGLAGES; }

  function noter(cle, x, y, a, s, l) {
    let t = traces.get(cle);
    if (!t) { t = { pts: [] }; traces.set(cle, t); }
    t.vu = B.t;
    t.pts.push({ x: x, y: y, a: a, s: s, l: l, n: B.t });
  }

  /** Les bateaux a l'heure (le traversier, la navette) : leur centre, leur cap et leur erre, d'une image a l'autre. */
  function bateauxALHeure() {
    const out = [];
    if (!B.partie) return out;
    [['traversier', typeof Traversier !== 'undefined' ? Traversier : null],
     ['navette', typeof Navette !== 'undefined' ? Navette : null]].forEach(function (p) {
      const T = p[1], d = T && T.donnees();
      if (!d) return;
      const ici = T.placeA(B.partie.heure);
      if (!ici) return;
      const cx = ici.x + d.largeurPx / 2, cy = ici.y + d.hauteurPx / 2, avant = derniers[p[0]];
      derniers[p[0]] = { x: cx, y: cy, t: B.t };
      if (!avant || avant.t !== B.t - 1 || ici.etat.phase !== 'traverse') return;
      const dx = cx - avant.x, dy = cy - avant.y, s = Math.hypot(dx, dy);
      out.push({ cle: p[0], x: cx, y: cy, a: Math.atan2(dy, dx), s: s, demiL: d.largeurPx / 2, l: d.hauteurPx / 2 });
    });
    return out;
  }

  /** Une image du monde : on note la poupe de chaque coque qui file, et on oublie ce qui a fini de s'effacer. */
  function maj() {
    if (!B.partie || B.interieur || B.bloc || !Monde.carte) return;
    const R = REGLAGES, pose = B.t % R.pas === 0, cx = B.cam.x + VW / 2, cy = B.cam.y + VH / 2;
    if (pose) {
      for (const v of B.entites) {
        if (v.type !== 'vehicule' || !v.def || !v.def.eau || v.etat === 'epave') continue;
        const s = Math.hypot(v.vx || 0, v.vy || 0);
        if (s < R.vitesse_min) continue;
        if (Math.abs(v.x - cx) > R.portee || Math.abs(v.y - cy) > R.portee) continue;
        // La poupe : derriere le centre, sur l'axe de la coque ; le sillage suit la ROUTE (vx, vy), pas le cap.
        const demi = v.def.longueur / 2, a = Math.atan2(v.vy, v.vx);
        const sens = Math.cos(a - v.angle) >= 0 ? 1 : -1;      // en machine arriere, le bouillon est devant la poupe
        noter(v, v.x - Math.cos(v.angle) * demi * sens, v.y - Math.sin(v.angle) * demi * sens, a, s, v.def.largeur / 2);
      }
      for (const b of bateauxALHeure()) {
        if (b.s < R.vitesse_min * 0.4) continue;
        noter(b.cle, b.x - Math.cos(b.a) * b.demiL, b.y - Math.sin(b.a) * b.demiL, b.a, Math.max(b.s * 2.5, R.vitesse_min), b.l);
      }
    } else bateauxALHeure();
    for (const [cle, t] of traces) {
      while (t.pts.length && B.t - t.pts[0].n > R.vie) t.pts.shift();
      if (!t.pts.length) traces.delete(cle);
    }
  }

  //: ⚠️ LES GOUTTES D'UNE IMAGE SE PEIGNENT PAR LOTS : groupees par teinte et par palier d'alpha (un dixieme), UN chemin et
  //: UN remplissage par lot. La premiere version faisait un `fillRect` et un `globalAlpha` par goutte : 2,7 ms de plus
  //: par image au processeur x4 (mesure A/B, 2 oct. 2026).
  const lots = new Map();

  /** Une goutte d'ecume de `w` x `h` px : ⚠️ ses DEUX coins sur l'eau, la ou elle tombe au pixel pres (arrondie). */
  function goutte(ctx, vue, x, y, alpha, w, h, coul) {
    if (alpha <= 0.05) return 0;
    const sx = Math.round(x - vue.x), sy = Math.round(y - vue.y);
    if (sx < -4 || sy < -4 || sx > VW + 4 || sy > VH + 4) return 0;
    const ax = sx + vue.x, ay = sy + vue.y;
    if (!Monde.estEau(Math.floor(ax / TT), Math.floor(ay / TT)) || !Monde.estEau(Math.floor((ax + w - 0.5) / TT), Math.floor((ay + h - 0.5) / TT))) return 0;
    const cle = coul + '|' + Math.min(10, Math.round(alpha * 10));
    let l = lots.get(cle);
    if (!l) { l = []; lots.set(cle, l); }
    l.push(sx, sy, w, h);
    return 1;
  }

  /** Les lots de l'image, a l'ecran : un remplissage par teinte et par palier. */
  function vider(ctx) {
    for (const [cle, l] of lots) {
      if (!l.length) continue;
      const i = cle.indexOf('|');
      ctx.globalAlpha = Number(cle.slice(i + 1)) / 10;
      ctx.fillStyle = cle.slice(0, i);
      ctx.beginPath();
      for (let k = 0; k < l.length; k += 4) ctx.rect(l[k], l[k + 1], l[k + 2], l[k + 3]);
      ctx.fill();
      l.length = 0;
    }
  }

  /** Le bras d'un cote (`cote` = 1 ou -1) au point `p` d'age `k`. */
  function bras(p, k, cote) {
    const R = REGLAGES, force = Math.min(1, p.s / R.pleine);
    const off = p.l * 0.55 + k * R.ouverture * force;
    return { x: p.x - Math.sin(p.a) * off * cote, y: p.y + Math.cos(p.a) * off * cote };
  }

  /** Le sillage de chaque coque, et la moustache des coques qui filent : sur l'eau, sous les coques. */
  function dessiner(ctx, vue) {
    if (B.interieur || B.bloc || !Monde.carte) return;
    const R = REGLAGES;
    let n = 0;
    ctx.save();
    for (const t of traces.values()) {
      const pts = t.pts;
      for (let i = 0; i < pts.length; i++) {
        const p = pts[i], k = B.t - p.n, f = k / R.vie;
        if (f >= 1) continue;
        const force = Math.min(1, p.s / R.pleine);
        // Les deux bras : des gouttes d'un point au suivant, pour un trait sans trou.
        const q = pts[i + 1];
        for (const cote of [1, -1]) {
          const a = bras(p, k, cote), b = q ? bras(q, B.t - q.n, cote) : a;
          const pas = Math.max(1, Math.ceil(Math.hypot(b.x - a.x, b.y - a.y) / 2));
          const alpha = 0.62 * (1 - f) * (0.35 + 0.65 * force);
          for (let s = 0; s < pas; s++) {
            const u = s / pas;
            n += goutte(ctx, vue, a.x + (b.x - a.x) * u, a.y + (b.y - a.y) * u, alpha, 1, 1, '#eef7fb');
          }
        }
        // Le bouillon de l'helice : large et blanc pres de la poupe, qui s'etale et palit.
        if (k < R.bouillon_vie) {
          const g = k / R.bouillon_vie, w = Math.max(2, Math.round(p.l * (0.7 + g * 0.6)));
          n += goutte(ctx, vue, p.x - w / 2, p.y - w / 3, 0.38 * (1 - g) * force, w, Math.max(1, Math.round(w * 0.6)), '#cfe9f1');
          // Et l'ecume qui y petille, a l'empreinte du point (jamais un de).
          const h = hash2(p.n * 31 + i, 0x5111A6E);
          n += goutte(ctx, vue, p.x + ((h & 7) - 3.5) * (1 + g), p.y + (((h >>> 3) & 7) - 3.5) * (1 + g), 0.7 * (1 - g) * force, 1, 1, '#ffffff');
        }
      }
    }
    // La moustache d'etrave : deux traits qui partent du nez vers l'arriere, en s'ouvrant.
    const cx = vue.x + VW / 2, cy = vue.y + VH / 2;
    for (const v of B.entites) {
      if (v.type !== 'vehicule' || !v.def || !v.def.eau || v.etat === 'epave') continue;
      if (Math.abs(v.x - cx) > VW / 2 + 80 || Math.abs(v.y - cy) > VH / 2 + 80) continue;
      const s = v.vitesse;
      if (s < R.moustache_min) continue;
      const demi = v.def.longueur / 2, bx = v.x + Math.cos(v.angle) * demi, by = v.y + Math.sin(v.angle) * demi;
      const long = R.moustache[0] + R.moustache[1] * s, alpha = Math.min(0.8, 0.3 + s * 0.18);
      for (const cote of [1, -1]) {
        const a = v.angle + Math.PI - cote * 0.42;
        for (let d = 0; d < long; d += 1.5) {
          n += goutte(ctx, vue, bx + Math.cos(a) * d, by + Math.sin(a) * d, alpha * (1 - d / long * 0.6), 1, 1, '#ffffff');
        }
      }
    }
    vider(ctx);
    ctx.restore();
    B.stats.rects += lots.size;
  }

  /** Les points d'une trace (pour les juges) : la coque, ou 'traversier' / 'navette'. */
  function points(cle) { const t = traces.get(cle); return t ? t.pts.slice() : []; }
  /** Une partie qui recommence : plus de sillage. */
  function oublier() { traces.clear(); for (const k in derniers) delete derniers[k]; }

  return { REGLAGES, reglages, maj, dessiner, points, oublier, bras };
})();
