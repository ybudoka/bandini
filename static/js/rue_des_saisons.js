/* Bandini — la rue des saisons (docs/jalons/les-quatre-saisons-realistes.md, lot 4, vague 4b).

   Ce que la saison met dans la rue : les BANCS DE NEIGE au bord des trottoirs tant que la neige tient,
   les ABRIS TEMPO dans les entrees des maisons de novembre a la fonte, la FUMEE des cheminees quand il
   fait froid, et les TERRASSES devant les restos et les bars l'ete.

   ⚠️ TOUT EST PEINT, RIEN N'EST POSE : aucune tuile, aucun decor, aucun identifiant d'entite, aucun de —
   la ville (`carte.generer`) ne bouge pas d'un octet, et un char passe sous un Tempo comme avant.
   ⚠️ LES MORCEAUX : bancs, Tempo et terrasses se peignent dans les morceaux cuits (`Monde.peindreDevantures`)
   et ne lisent QUE la palette du moment (`neige`, `froid`, la cle du palier) — ils se repeignent donc au
   changement de palier, avec le gazon, jamais a chaque image. Seule la fumee se dessine a chaque image,
   d'apres `B.t`, pour les cheminees des morceaux a l'ecran. */

const RueDesSaisons = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.saisons && B.defs.saisons.rue; }
  function hash(x, y, sel) { return hash2(x * 131 + sel, y * 7919 + sel * 31) >>> 0; }
  function part(h, dec) { return ((h >>> dec) % 1000) / 1000; }

  function rgb(c) { return [parseInt(c.substr(1, 2), 16), parseInt(c.substr(3, 2), 16), parseInt(c.substr(5, 2), 16)]; }
  function meler(a, b, t) {
    const x = rgb(a), y = rgb(b);
    return '#' + x.map(function (v, i) { return ('0' + Math.round(v + (y[i] - v) * t).toString(16)).slice(-2); }).join('');
  }

  //: La neige pleine de la palette d'hiver : un banc est a sa pleine largeur a cette neige-la.
  const NEIGE_PLEINE = 0.7;

  /** Le moment de la rue : ce que la palette dit, lu une fois par morceau peint. */
  function moment() {
    const p = Saisons.palette(), k = Saisons.cle();
    return { neige: p.neige || 0, froid: p.froid || 0, degel: k.indexOf('hiver>') === 0 };
  }

  // ------------------------------------------------------------------ les bancs de neige

  //: Les quatre cotes d'une tuile : [dx, dy] vers le voisin.
  const COTES = [[0, -1], [0, 1], [-1, 0], [1, 0]];

  /** Une tuile de CHAUSSEE qui porte un banc : la rue, pas une traverse pietonne, pas une entree ni une
      ruelle. Rend les cotes (index de `COTES`) qui touchent un trottoir. Pure. */
  function bancsDe(tx, ty) {
    if (!Monde.estRoute(tx, ty) || Monde.estPassage(tx, ty)) return [];
    const l = Monde.carte && Monde.carte.legende[Monde.glyphe(tx, ty)];
    if (!l || l.stationnement || l.ruelle || l.rail) return [];
    const cotes = [];
    COTES.forEach(function (c, i) { if (Monde.estTrottoir(tx + c[0], ty + c[1])) cotes.push(i); });
    return cotes;
  }

  /** Les tuiles a banc d'un morceau, [tx, ty, cotes], trouvees une fois par carte et par morceau : la rue
      ne bouge pas, et la repeinte d'un palier ne refait pas la recherche (le rythme). */
  function bordsDuMorceau(mx, my, n) {
    const carte = Monde.carte;
    if (!carte.bordsDeRue) carte.bordsDeRue = new Map();
    const cle = mx + ',' + my;
    let l = carte.bordsDeRue.get(cle);
    if (l) return l;
    l = [];
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
      const tx = mx * n + i, ty = my * n + j, cotes = bancsDe(tx, ty);
      if (cotes.length) l.push([tx, ty, cotes]);
    }
    carte.bordsDeRue.set(cle, l);
    return l;
  }

  function peindreBancs(ctx, m, mx, my, T, n) {
    const d = donnees().bancs;
    const k = Math.min(1, m.neige / NEIGE_PLEINE);
    const sale = m.degel ? 0.35 + 0.5 * (1 - k) : 0;
    const blanc = sale ? meler(d.neige, d.sale, sale) : d.neige;
    const ombre = sale ? meler(d.ombre, d.sale, sale) : d.ombre;
    for (const b of bordsDuMorceau(mx, my, n)) {
      const tx = b[0], ty = b[1], cotes = b[2];
      const ox = (tx - mx * n) * T, oy = (ty - my * n) * T;
      cotes.forEach(function (c) {
        const vertical = c >= 2;          // un banc le long d'un trottoir a gauche ou a droite
        for (let p = 0; p < T; p += 2) {
          const h = hash(tx * 16 + (vertical ? 0 : p), ty * 16 + (vertical ? p : 0), 5 + c);
          // Le profil du banc : une houle douce le long du trottoir, continue d'une tuile a l'autre (la
          // coordonnee du monde, pas celle de la tuile) — au hasard pur, il faisait un peigne.
          const s = (vertical ? ty : tx) * T + p + (c * 37);
          const houle = 0.5 + 0.32 * Math.sin(s * 0.21) + 0.18 * Math.sin(s * 0.057 + (vertical ? tx : ty));
          const l = Math.max(1, Math.round((d.largeur[0] + houle * (d.largeur[1] - d.largeur[0])) * k));
          const a = c === 0 ? [ox + p, oy, 2, l] : c === 1 ? [ox + p, oy + T - l, 2, l]
            : c === 2 ? [ox, oy + p, l, 2] : [ox + T - l, oy + p, l, 2];
          ctx.fillStyle = blanc; ctx.fillRect(a[0], a[1], a[2], a[3]);
          // L'ombre du banc, du cote de la rue : c'est elle qui lui donne du relief.
          ctx.fillStyle = ombre;
          if (c === 0) ctx.fillRect(a[0], oy + l, 2, 1);
          else if (c === 1) ctx.fillRect(a[0], oy + T - l - 1, 2, 1);
          else if (c === 2) ctx.fillRect(ox + l, a[1], 1, 2);
          else ctx.fillRect(ox + T - l - 1, a[1], 1, 2);
          // Au degel, la neige sale : des grains de gravier.
          if (sale && part(h, 13) < 0.35) { ctx.fillStyle = d.sale; ctx.fillRect(a[0] + (h & 1), a[1] + ((h >> 1) & 1), 1, 1); }
        }
      });
    }
  }

  // ------------------------------------------------------------------ ce qu'on trouve une fois par carte

  /** Les Tempo et les terrasses possibles de la ville, calcules une fois par carte (ils ne bougent
      pas) : `{ tempos: [{x, y, w, h, sens}], terrasses: [{x, y, genre, parasol}] }`, en tuiles. */
  function lieux(carte) {
    if (carte.rueDesSaisons) return carte.rueDesSaisons;
    const def = B.defs.carte, d = donnees();
    const sol = function (x, y) { return (carte.sol[y] && carte.sol[y][x]) || ''; };
    const out = { tempos: [], terrasses: [] };
    if (!def || !carte.laVille) return (carte.rueDesSaisons = out);
    (def.residences || []).forEach(function (r) {
      // L'entree de cote : une colonne de stationnement qui longe la maison, de la rangee d'avant a celle d'apres.
      [r.x - 1, r.x + r.l].forEach(function (cx) {
        if ([r.y - 1, r.y, r.y + 1].every(function (y) { return sol(cx, y) === 'p'; }) &&
            part(hash(cx, r.y, 71), 0) < d.tempo.part) {
          out.tempos.push({ x: cx, y: r.y - 1, w: 1, h: 3, sens: 'bas' });
        }
      });
      // Devant le rideau de garage : deux tuiles d'entree sous le rideau.
      for (let x = r.x; x < r.x + r.l; x++) {
        if (sol(x, r.y) !== 'G' || sol(x - 1, r.y) === 'G') continue;
        let w = 0;
        while (sol(x + w, r.y) === 'G') w++;
        let ok = true;
        for (let dx = 0; dx < w; dx++) if (sol(x + dx, r.y + 1) !== 'p' || sol(x + dx, r.y + 2) !== 'p') ok = false;
        if (ok) out.tempos.push({ x: x, y: r.y + 1, w: w, h: 2, sens: 'bas' });
      }
    });
    const genres = (B.defs.devantures && B.defs.devantures.genres) || [];
    // Ce qui tient deja le trottoir (un banc, une poubelle, un abribus, un lampadaire) : pas de table dessus.
    const pris = new Set();
    (def.decor || []).forEach(function (o) { pris.add(o.x + ',' + o.y); });
    (def.lampes || []).forEach(function (o) { pris.add(o.x + ',' + o.y); });
    const pave = function (x, y) { const g = sol(x, y); return g === '.' || g === '_'; };
    const porte = function (g) { return g === 'D' || g === 'd' || g === 'G'; };
    (def.devantures || []).forEach(function (f) {
      const g = genres[f.genre];
      if (!g || d.terrasses.genres.indexOf(g.slug) < 0) return;
      for (let x = f.x; x < f.x + f.l; x++) {
        // Jamais devant une porte, ni hors du trottoir.
        if (porte(sol(x, f.y)) || porte(sol(x - 1, f.y)) || porte(sol(x + 1, f.y))) continue;
        if (!pave(x, f.y + 1) || pris.has(x + ',' + (f.y + 1))) continue;
        out.terrasses.push({ x: x, y: f.y + 1, genre: g.slug, parasol: (x - f.x) % 2 === 0, couleur: hash(f.x, f.y, 3) % d.terrasses.parasols.length });
      }
    });
    return (carte.rueDesSaisons = out);
  }

  function dansLeMorceau(r, mx, my, n) {
    const w = r.w || 1, h = r.h || 1;
    return r.x + w > mx * n && r.x < (mx + 1) * n && r.y + h > my * n && r.y < (my + 1) * n;
  }

  // ------------------------------------------------------------------ les abris Tempo

  //: Monte-t-on les Tempo a ce froid-la ? De novembre (le froid) jusqu'au milieu de la fonte (au degel,
  //: quand la neige a fondu de moitie, on les demonte) — la palette seule le dit.
  function tempoMonte(m) {
    const d = donnees().tempo;
    return m.froid >= d.froid_min && !(m.degel && m.neige < d.demonte_neige);
  }

  /** Un Tempo vu d'en haut : la toile tendue sur ses arceaux, son bord, et l'ouverture cote rue. */
  function peindreTempo(ctx, t, ox, oy, T) {
    const d = donnees().tempo;
    const x = ox + 1, y = oy + 1, w = t.w * T - 2, h = t.h * T - 2;
    ctx.fillStyle = 'rgba(11,10,18,0.28)'; ctx.fillRect(x + 2, y + 2, w, h);            // son ombre
    ctx.fillStyle = d.bord; ctx.fillRect(x, y, w, h);
    ctx.fillStyle = d.toile; ctx.fillRect(x + 1, y + 1, w - 2, h - 3);
    ctx.fillStyle = d.arceau;
    for (let yy = y + 4; yy < y + h - 4; yy += 5) ctx.fillRect(x + 1, yy, w - 2, 1);    // les arceaux
    ctx.fillRect(x + Math.floor(w / 2), y + 1, 1, h - 3);                                   // le faite
    ctx.fillStyle = d.ouverture; ctx.fillRect(x + 2, y + h - 3, w - 4, 2);                  // l'ouverture, cote rue
  }

  // ------------------------------------------------------------------ les terrasses

  function terrassesOuvertes(m) { return m.froid <= donnees().terrasses.froid_max; }

  function peindreTerrasse(ctx, t, ox, oy) {
    const d = donnees().terrasses;
    // La table ronde et ses deux chaises.
    ctx.fillStyle = 'rgba(11,10,18,0.3)'; ctx.fillRect(ox + 5, oy + 8, 7, 5);
    ctx.fillStyle = '#5a4634'; ctx.fillRect(ox + 1, oy + 6, 3, 3); ctx.fillRect(ox + 12, oy + 6, 3, 3);
    ctx.fillStyle = '#d9d4ca'; ctx.fillRect(ox + 5, oy + 5, 6, 5); ctx.fillRect(ox + 6, oy + 4, 4, 7);
    if (!t.parasol) return;
    // Le parasol vu d'en haut : un disque de huit pointes de deux couleurs, son ombre, et sa tige au centre.
    const c = d.parasols[t.couleur];
    const cx = ox + 8, cy = oy + 5;
    ctx.fillStyle = 'rgba(11,10,18,0.25)'; ctx.fillRect(cx - 4, cy + 4, 11, 4);
    for (let dy = -5; dy <= 5; dy++) for (let dx = -6; dx <= 6; dx++) {
      const e = dx * dx / 36 + dy * dy / 25;
      if (e > 1) continue;
      const secteur = Math.floor((Math.atan2(dy, dx) + Math.PI) / (Math.PI * 2) * 8) % 2;
      ctx.fillStyle = e > 0.72 ? meler(c[secteur], '#000000', 0.25) : c[secteur];
      ctx.fillRect(cx + dx, cy + dy, 1, 1);
    }
    ctx.fillStyle = '#2a2a2a'; ctx.fillRect(cx, cy, 1, 1);
  }

  // ------------------------------------------------------------------ dans le morceau

  /** Ce que la saison peint dans le morceau (mx, my) de la carte : appele par `Monde.peindreDevantures`.
      Rien dans une piece ni dans un bloc — seulement la ville. */
  function peindre(ctx, carte, mx, my, T, n) {
    if (!carte || !carte.laVille || !donnees() || typeof Saisons === 'undefined') return;
    const m = moment();
    if (m.neige > 0.02) peindreBancs(ctx, m, mx, my, T, n);
    const l = lieux(carte);
    if (tempoMonte(m)) {
      l.tempos.forEach(function (t) { if (dansLeMorceau(t, mx, my, n)) peindreTempo(ctx, t, (t.x - mx * n) * T, (t.y - my * n) * T, T); });
    }
    if (terrassesOuvertes(m)) {
      l.terrasses.forEach(function (t) { if (dansLeMorceau(t, mx, my, n)) peindreTerrasse(ctx, t, (t.x - mx * n) * T, (t.y - my * n) * T); });
    }
  }

  // ------------------------------------------------------------------ la fumee des cheminees

  /** La part de cheminees qui fume a ce froid : aucune sous `froid_min`, toutes au grand froid. */
  function fumeA(t, froid) {
    const f = donnees().fumee;
    if (froid < f.froid_min) return false;
    return part(hash(t.x, t.y, 17), 2) < froid;
  }

  /** Les cheminees qui fument, dans les morceaux a l'ecran (`carte.visibles`). */
  function cheminees() {
    const carte = Monde.carte, out = [];
    if (!carte || !carte.laVille || !carte.toits || !carte.visibles || !donnees() || typeof Saisons === 'undefined') return out;
    const froid = Saisons.palette().froid || 0;
    if (froid < donnees().fumee.froid_min) return out;
    carte.visibles.forEach(function (cle) {
      const toits = carte.toits.get(cle);
      if (!toits) return;
      toits.forEach(function (t) { if (t.type === 'cheminee' && fumeA(t, froid)) out.push(t); });
    });
    return out;
  }

  /** La fumee : des bouffees grises qui montent, grossissent, derivent vers l'est et s'effacent. ⚠️ D'apres
      `B.t` seulement — jamais un de ; au-dessus des toits et des gens (`Jeu.rendre`). */
  function dessinerFumees(ctx, cam) {
    const liste = cheminees();
    if (!liste.length) return;
    const F = donnees().fumee, TT = 16;
    for (const c of liste) {
      const bx = c.x * TT + 8 - cam.x, by = c.y * TT + 2 - cam.y;
      if (bx < -80 || bx > VW + 80 || by < -120 || by > VH + 40) continue;
      const decale = hash(c.x, c.y, 29) % F.vie;
      for (let i = 0; i < F.bouffees; i++) {
        const p = (((B.t || 0) + decale + i * F.vie / F.bouffees) % F.vie) / F.vie;
        const x = bx + F.derive * p * p + Math.sin(p * 6 + i) * 2;
        const y = by - F.monte * p;
        const r = 2 + (F.rayon - 2) * p;
        const a = 0.5 * (1 - p) * Math.min(1, p * 6);
        ctx.fillStyle = 'rgba(214,216,220,' + a.toFixed(3) + ')';
        ctx.fillRect(Math.round(x - r), Math.round(y - r * 0.8), Math.round(2 * r), Math.round(1.6 * r));
        ctx.fillRect(Math.round(x - r * 0.7), Math.round(y - r), Math.round(1.4 * r), Math.round(2 * r));
        B.stats.rects += 2;
      }
    }
  }

  return { bancsDe, lieux, peindre, cheminees, fumeA, dessinerFumees, tempoMonte, terrassesOuvertes, moment };
})();
