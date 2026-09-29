/* Bandini — la rue des saisons (docs/jalons/les-quatre-saisons-realistes.md, lot 4, vague 4b).

   Ce que la saison met dans la rue : les BANCS DE NEIGE au bord des trottoirs tant que la neige tient,
   les ABRIS TEMPO dans les entrees des maisons de novembre a la fonte, la FUMEE des cheminees quand il
   fait froid, et les TERRASSES devant les restos et les bars l'ete.

   ⚠️ TOUT EST PEINT, RIEN N'EST POSE : aucune tuile, aucun decor, aucun identifiant d'entite, aucun de —
   la ville (`carte.generer`) ne bouge pas d'un octet. ⚠️ Mais Tempo et terrasses sont SOLIDES en leur
   saison (vague 4c) : la collision se lit ici, a cote du dessin (`tempoBloque`, `bloquer`).
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
      // Devant le rideau de garage : deux tuiles d'entree sous le rideau. ⚠️ Jamais devant un garage ou
      // l'on ENTRE (`portes_garage` : les cachettes des bungalows) — solide l'hiver (vague 4c), le Tempo
      // fermerait la cachette.
      for (let x = r.x; x < r.x + r.l; x++) {
        if (sol(x, r.y) !== 'G' || sol(x - 1, r.y) === 'G') continue;
        if ((def.portes_garage || []).some(function (pg) { return pg.y === r.y && pg.x <= x + 1 && pg.x + (pg.l || 1) > x; })) continue;
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

  // ------------------------------------------------------------------ solides selon la saison (vague 4c)

  //: ⚠️ TERRASSES ET TEMPO SONT SOLIDES (Martin, 29 sept. 2026) : on ne marche plus sur les tables, et les
  //: chars ne passent plus sous les abris (les pietons, oui : c'est un abri). Ils n'existent qu'en leur
  //: saison : leur collision apparait et disparait avec eux. ⚠️ RIEN N'EST POSE : ni tuile, ni decor, ni
  //: identifiant, ni de — la collision se LIT dans `lieux(carte)` et la palette du moment, comme le dessin.
  //: ⚠️ PERSONNE N'Y RESTE PRIS : un char deja sous un Tempo quand on le monte en sort librement (le Tempo
  //: ne l'arrete que s'il n'y est pas deja), et un passant sur une table au premier jour d'ete est pousse
  //: hors de la terrasse, jamais vers la facade.

  //: Ce qui tient debout a ce moment : lu une fois par heure de jeu, pas a chaque tuile testee.
  let etatJ = null, etatH = null, etatK = null, etat = { tempo: false, terrasses: false };
  function ouverts() {
    const p = B.partie;
    if (!p) return etat;
    if (p.jour !== etatJ || p.heure !== etatH) {
      etatJ = p.jour; etatH = p.heure;
      const k = Saisons.cle();
      if (k !== etatK) {
        etatK = k;
        const m = moment(), avant = etat;
        etat = { tempo: tempoMonte(m), terrasses: terrassesOuvertes(m) };
        // ⚠️ LES TABLES SORTENT : qui s'y tenait debout (un passant qui attend, le joueur immobile) en est
        // pousse tout de suite — sinon il resterait plante sur la table jusqu'a son prochain pas.
        if (etat.terrasses && !avant.terrasses) degagerLesTables();
      }
    }
    return etat;
  }

  function degagerLesTables() {
    if (!enVille() || !B.entites) return;
    for (const e of B.entites) if (e.type === 'pieton' || e.type === 'joueur') bloquer(e);
  }

  /** Les tuiles des Tempo et des terrasses de la carte, indexees une fois par carte : `tempos` (tuile ->
      Tempo) et `tables` (tuile -> boite de la table et de ses chaises, en pixels). */
  function index(carte) {
    if (carte.rueSolide) return carte.rueSolide;
    const l = lieux(carte), T = 16, out = { tempos: new Map(), tables: new Map() };
    l.tempos.forEach(function (t) {
      for (let y = t.y; y < t.y + t.h; y++) for (let x = t.x; x < t.x + t.w; x++) out.tempos.set(y * carte.w + x, t);
    });
    // La table et ses deux chaises (`peindreTerrasse`) : de x+1 a x+15, de y+4 a y+11 dans la tuile.
    l.terrasses.forEach(function (t) {
      out.tables.set(t.y * carte.w + t.x, { x: t.x * T + 8, y: t.y * T + 7.5, l: 7, h: 3.5, tx: t.x, ty: t.y });
    });
    return (carte.rueSolide = out);
  }

  function enVille() {
    const c = Monde.carte;
    return c && c.laVille && donnees() && typeof Saisons !== 'undefined' ? c : null;
  }

  /** Le char deja SOUS ce Tempo (un de ses cercles chevauche l'abri, a sa place d'avant le pas) : il en
      sort librement — le meme test de boite que `Vehicules.bloqueParLesTuiles`. */
  function dessous(v, t) {
    const T = 16;
    for (const c of Vehicules.cercles(v)) {
      const tx0 = Math.floor((c.x - c.r) / T), tx1 = Math.floor((c.x + c.r) / T);
      const ty0 = Math.floor((c.y - c.r) / T), ty1 = Math.floor((c.y + c.r) / T);
      if (tx1 >= t.x && tx0 < t.x + t.w && ty1 >= t.y && ty0 < t.y + t.h) return true;
    }
    return false;
  }

  /** Un char `v` peut-il entrer sur la tuile (tx, ty) ? Non si un Tempo monte la couvre (et que le char
      n'est pas deja dessous). Appele par `Monde.barriereBloque` : toutes les regles des chars la lisent. */
  function tempoBloque(v, tx, ty) {
    const c = enVille();
    if (!c || !v || v.type !== 'vehicule') return false;
    const t = index(c).tempos.get(ty * c.w + tx);
    if (!t || !ouverts().tempo) return false;
    return !dessous(v, t);
  }

  /** On ne marche pas sur une table de terrasse : un pieton (ou le joueur a pied) qui y entre en ressort par
      le cote le moins enfonce — jamais vers la facade (le nord : la devanture) ni dans un mur. Appele par
      `Entites.bloquerParDecor`, comme la caleche et le petit train. */
  function bloquer(e) {
    const c = enVille();
    if (!c || !e || (e.type !== 'pieton' && e.type !== 'joueur') || e.dansVehicule) return;
    const tables = index(c).tables;
    if (!tables.size || !ouverts().terrasses) return;
    const T = 16, tx0 = Math.floor((e.x - e.r - 8) / T), tx1 = Math.floor((e.x + e.r + 8) / T);
    const ty0 = Math.floor((e.y - e.r - 8) / T), ty1 = Math.floor((e.y + e.r + 8) / T);
    for (let ty = ty0; ty <= ty1; ty++) for (let tx = tx0; tx <= tx1; tx++) {
      const b = tables.get(ty * c.w + tx);
      if (!b) continue;
      const dx = e.x - b.x, dy = e.y - b.y;
      const px = b.l + e.r - Math.abs(dx), py = b.h + e.r - Math.abs(dy);
      if (px <= 0 || py <= 0) continue;
      // Les sorties possibles : a l'ouest, a l'est, au sud (le trottoir d'en bas) ; le nord seulement s'il
      // ne mene pas dans la facade.
      const sorties = [[px + 0.01, dx < 0 ? -1 : 1, 0]];
      if (dy >= 0 || !Monde.marchablePieton(b.tx, b.ty - 1)) sorties.push([b.h + e.r - dy + 0.01, 0, 1]);
      else sorties.push([py + 0.01, 0, -1]);
      sorties.sort(function (u, w) { return u[0] - w[0]; });
      const s = sorties[0];
      if (s[1]) e.x = b.x + s[1] * (b.l + e.r + 0.01);
      else e.y = b.y + s[2] * (b.h + e.r + 0.01);
    }
  }

  // ------------------------------------------------------------------ les bornes-fontaines ouvertes (vague 4c)

  //: LES BORNES-FONTAINES OUVERTES DE LA CANICULE : les jours de chaleur, quelques bornes crachent vers la rue
  //: et des enfants courent dans l'eau. ⚠️ TOUT EST PEINT d'apres `B.t` : ni entite (un enfant de plus
  //: prendrait un numero et decalerait la ville), ni de, ni tuile. Les enfants se trient avec les gens
  //: (`ajouterVisibles`, comme les citrouilles) et on ne les bouscule pas : ils jouent, on passe a cote.

  function bornesDonnees() { const d = donnees(); return d && d.bornes; }

  /** Les bornes de la carte, trouvees une fois : leur entite (pour savoir si elle est cassee), leur tuile,
      et le cote de la rue — le jet crache vers la chaussee, les enfants courent le long du trottoir. */
  function bornesDe(carte) {
    if (carte.bornesFontaines) return carte.bornesFontaines;
    const out = [], T = 16;
    for (const e of (B.entites || [])) {
      if (e.decor !== 'borne_fontaine') continue;
      const tx = Math.floor(e.x / T), ty = Math.floor((e.y - 1) / T);
      let dir = [1, 0];
      for (const q of [[0, 1], [0, -1], [1, 0], [-1, 0]]) {
        if (Monde.estRoute(tx + q[0], ty + q[1]) && !Monde.estTrottoir(tx + q[0], ty + q[1])) { dir = q; break; }
      }
      out.push({ e: e, tx: tx, ty: ty, x: e.x, y: e.y, dir: dir });
    }
    // ⚠️ Pas de souvenir d'une ville encore vide : le premier rendu (sous l'ecran titre) passe avant que le
    // decor ne naisse, et la liste vide y serait restee pour toute la partie (vu a la capture).
    if (out.length) carte.bornesFontaines = out;
    return out;
  }

  /** Un jour de CHALEUR ? L'ete (la palette), un jour sur `part_jours` a l'empreinte du jour. Pure. */
  function jourDeChaleur(jour) {
    const d = bornesDonnees();
    if (!d || typeof Saisons === 'undefined') return false;
    const p = Saisons.paletteA(jour, 0.5);
    return (p.froid || 0) <= d.froid_max && part(hash(jour, 3, 91), 3) < d.part_jours;
  }

  /** Cette borne crache-t-elle a ce moment ? Pure : le jour, l'heure, la pluie, sa tuile. */
  function borneOuverteA(b, jour, heure, pluie) {
    const d = bornesDonnees(), h = heure * 24;
    if (!d || pluie || h < d.heures[0] || h >= d.heures[1] || !jourDeChaleur(jour)) return false;
    return part(hash(b.tx, b.ty + jour * 13, 97), 5) < d.part;
  }

  //: Les bornes ouvertes du moment : recalculees quand le quart d'heure, le jour ou la pluie changent.
  let ouvertesCle = null, ouvertes = [];
  function bornesOuvertes() {
    const c = enVille(), p = B.partie;
    if (!c || !p || !bornesDonnees()) return [];
    const pluie = typeof Pluie !== 'undefined' && Pluie.intensite() > 0.05;
    const k = p.jour + '|' + Math.floor(p.heure * 96) + '|' + (pluie ? 1 : 0) + '|' + c.w;
    if (k !== ouvertesCle) {
      ouvertesCle = k;
      ouvertes = bornesDe(c).filter(function (b) { return borneOuverteA(b, p.jour, p.heure, pluie); });
    }
    return ouvertes.filter(function (b) { return !b.e.brise; });
  }

  /** Ce decor est-il une borne que la canicule a ouverte ? (le geste FERMER LA BORNE la laisse couler) */
  function borneOuverte(e) {
    return bornesOuvertes().some(function (b) { return b.e === e; });
  }

  /** Le pied du jet : a une douzaine de pixels de la borne, du cote de la rue. */
  function piedDuJet(b) {
    const L = bornesDonnees().jet_px;
    return { x: b.x + b.dir[0] * L * 0.6, y: b.y - 2 + b.dir[1] * L * 0.6 };
  }

  /** Est-on dans l'eau d'une borne ouverte (se rafraichir, `Interactions.maj`) ? */
  function dansUnJet(x, y, r) {
    return bornesOuvertes().some(function (b) {
      const q = piedDuJet(b);
      return (q.x - x) * (q.x - x) + (q.y - y) * (q.y - y) < r * r || (b.x - x) * (b.x - x) + (b.y - y) * (b.y - y) < r * r;
    });
  }

  /** La flaque et le jet d'une borne, au sol puis en l'air ; (x, y) = son pied a l'ecran. */
  function peindreJet(ctx, b, x, y) {
    const d = bornesDonnees(), L = d.jet_px, t = B.t || 0, dx = b.dir[0], dy = b.dir[1];
    // Le jet : une gerbe de gouttes qui part de la bouche (a 8 px du sol), monte et retombe vers la rue.
    for (let i = 0; i < 16; i++) {
      const p = ((t * 1.3 + i * 5.3 + hash(b.tx, b.ty, i) % 7) % 40) / 40;
      const ecart = Math.sin(i * 2.3 + t * 0.21) * 2.2 * p;
      const haut = 11 * 4 * p * (1 - p) + 8 * (1 - p);
      const gx = x + dx * (3 + p * L) + (dy ? ecart : 0), gy = y + dy * (p * L) - haut + (dx ? ecart * 0.5 : 0);
      ctx.fillStyle = i % 3 === 0 ? 'rgba(236,246,255,0.95)' : 'rgba(170,214,240,0.85)';
      ctx.fillRect(Math.round(gx), Math.round(gy), i % 4 === 0 ? 2 : 1, 2);
    }
    // La colonne pleine au sortir de la bouche.
    ctx.fillStyle = 'rgba(214,236,250,0.9)';
    if (dx) ctx.fillRect(Math.round(x + (dx > 0 ? 3 : -9)), Math.round(y - 9), 6, 2);
    else ctx.fillRect(Math.round(x - 1), Math.round(y - 9 + (dy > 0 ? 2 : -6)), 2, 5);
    // Les eclaboussures au pied du jet.
    const q = piedDuJet(b), sx = q.x - b.x + x, sy = q.y - b.y + y;
    for (let i = 0; i < 5; i++) {
      const a = (t * 0.17 + i * 1.3) % 6.283, r = 2 + ((t + i * 11) % 18) / 3;
      ctx.fillStyle = 'rgba(226,242,252,0.8)';
      ctx.fillRect(Math.round(sx + Math.cos(a) * r), Math.round(sy + 2 + Math.sin(a) * r * 0.5 - (r > 6 ? 0 : 2)), 1, 1);
    }
    B.stats.rects += 23;
  }

  /** La flaque sous la borne ouverte et au pied du jet : peinte sur le sol, SOUS les gens. */
  function dessinerFlaques(ctx, cam) {
    const liste = bornesOuvertes();
    if (!liste.length) return;
    for (const b of liste) {
      const q = piedDuJet(b), x = Math.round(q.x - cam.x), y = Math.round(q.y - cam.y);
      if (x < -60 || y < -60 || x > VW + 60 || y > VH + 60) continue;
      const rx = 16 + Math.abs(b.dir[0]) * 8, ry = 8 + Math.abs(b.dir[1]) * 8;
      for (let yy = -ry; yy <= ry; yy += 2) {
        const w = Math.round(rx * Math.sqrt(Math.max(0, 1 - (yy * yy) / (ry * ry))));
        ctx.fillStyle = 'rgba(60,96,128,0.32)'; ctx.fillRect(x - w, y + yy, 2 * w, 2);
      }
      // Le reflet qui bouge dans la flaque.
      const k = Math.floor((B.t || 0) / 10) % 4;
      ctx.fillStyle = 'rgba(210,232,250,0.35)'; ctx.fillRect(x - 6 + k * 2, y - 2, 5, 1); ctx.fillRect(x + 2 - k, y + 3, 4, 1);
      B.stats.rects += ry + 2;
    }
  }

  //: Un char qui roule a moins de ce rayon du jet : les enfants remontent sur le trottoir et attendent.
  const PRUDENCE_PX = 90;
  let prudenceT = -1, roulent = [];
  /** Les chars qui roulent, cherches une fois par image (pour tous les jets a l'ecran). */
  function charsQuiRoulent() {
    if (prudenceT === B.t) return roulent;
    prudenceT = B.t; roulent = [];
    for (const e of (B.entites || [])) if (e.type === 'vehicule' && Math.abs(e.vitesse || 0) > 0.3) roulent.push(e);
    return roulent;
  }
  function unCharApproche(b) {
    const q = piedDuJet(b);
    return charsQuiRoulent().some(function (v) { return Math.abs(v.x - q.x) < PRUDENCE_PX && Math.abs(v.y - q.y) < PRUDENCE_PX; });
  }

  //: Les enfants qui jouent dans l'eau : leurs couleurs a l'empreinte de la borne (un chandail, un maillot).
  //: ⚠️ Ils courent dans le jet, donc au bord de la rue : quand un char approche, ils remontent sur le
  //: trottoir, en rang derriere la borne, et regardent passer — personne n'est peint sous un char.
  function enfantsDe(b) {
    const d = bornesDonnees(), n = d.enfants, out = [], t = B.t || 0;
    const long = b.dir[1] !== 0;                          // la rue au nord ou au sud : on court d'est en ouest
    const q = piedDuJet(b), cx = (b.x + q.x) / 2, cy = (b.y + q.y) / 2 + 2;
    const prudents = unCharApproche(b);
    for (let i = 0; i < n; i++) {
      const h = hash(b.tx + i * 17, b.ty, 131);
      if (prudents) {
        const o = (i - (n - 1) / 2) * 9;
        const x = long ? b.x + o : b.x - b.dir[0] * 10, y = long ? b.y - b.dir[1] * 9 : b.y + o;
        const face = long ? (b.dir[1] > 0 ? 'bas' : 'haut') : (b.dir[0] > 0 ? 'droite' : 'gauche');
        out.push({ x: x, y: y, face: face, image: 0, saut: 0, prudent: true, swaps: couleursEnfant(d, h) });
        continue;
      }
      const v = 0.028 + (h % 13) / 1000, a = t * v + i * 2.094 + (h % 100) / 30;
      const rx = long ? 22 : 9, ry = long ? 7 : 20;
      const x = cx + Math.cos(a) * rx, y = cy + Math.sin(a) * ry;
      const vx = -Math.sin(a) * rx, vy = Math.cos(a) * ry;
      const face = Math.abs(vx) > Math.abs(vy) ? (vx > 0 ? 'droite' : 'gauche') : (vy > 0 ? 'bas' : 'haut');
      // Un saut en passant dans l'eau : on bondit en criant.
      const saut = Math.max(0, Math.sin(a * 2 + i)) > 0.92 ? 3 : 0;
      out.push({ x: x, y: y, face: face, image: Math.floor(t / 7 + i) % 2, saut: saut, swaps: couleursEnfant(d, h) });
    }
    return out;
  }

  function couleursEnfant(d, h) {
    return { c: d.chandails[h % d.chandails.length], p: d.maillots[(h >>> 5) % d.maillots.length],
             h: ['#2a1a10', '#6b4b2c', '#b8862a', '#101018', '#d8c07a'][(h >>> 9) % 5],
             s: ['#f0c098', '#d9a070', '#a86e4a', '#7a4a2e', '#e8b088'][(h >>> 13) % 5] };
  }

  function peindreEnfant(ctx, k, x, y) {
    const def = SPRITES.enfant, cuit = Atlas.cuire('enfant', def, k.swaps), poses = cuit.poses[k.face] || cuit.poses.bas;
    const img = poses[Math.min(k.image, poses.length - 1)];
    ctx.fillStyle = 'rgba(11,10,18,0.25)'; ctx.fillRect(Math.round(x - 3), Math.round(y - 1), 6, 2);
    ctx.drawImage(img, Math.round(x - cuit.ancre[0]), Math.round(y - cuit.ancre[1] - k.saut));
  }

  //: Au tri des gens, apres tout le reste (voir `Halloween.ajouterVisibles`).
  const ID_TRI = 1e9 + 77;

  /** Les enfants et le jet des bornes a l'ecran, tries avec les gens : un passant plus bas les cache. */
  function ajouterVisibles(visibles, cx, cy) {
    const liste = bornesOuvertes();
    if (!liste.length) return;
    for (const b of liste) {
      if (b.x < cx - 60 || b.y < cy - 60 || b.x > cx + VW + 60 || b.y > cy + VH + 60) continue;
      visibles.push({ id: ID_TRI, vivant: true, x: b.x, y: b.y + 0.5,
                      peindreFoire: function (ctx) { peindreJet(ctx, b, b.x - Math.round(cx), b.y - Math.round(cy)); } });
      for (const k of enfantsDe(b)) {
        visibles.push({ id: ID_TRI, vivant: true, x: k.x, y: k.y,
                        peindreFoire: function (ctx) { peindreEnfant(ctx, k, k.x - Math.round(cx), k.y - Math.round(cy)); } });
      }
    }
  }

  //: Le son de la borne : ce qu'on entend, glisse image par image ; quand on a demande le lieu.
  let sonBorne = 0, sonBorneDemande = -Infinity;

  /** Chaque pas de jeu : l'eau qui crache et les enfants qui crient, d'apres la borne ouverte la plus
      proche — plus fort en approchant, en fondu, muet dedans. */
  function majSon() {
    const d = bornesDonnees(), j = B.joueur;
    if (typeof Son === 'undefined' || !d) return;
    let voulu = 0;
    if (j && !B.interieur) {
      let d2 = Infinity;
      for (const b of bornesOuvertes()) d2 = Math.min(d2, (b.x - j.x) * (b.x - j.x) + (b.y - j.y) * (b.y - j.y));
      const dist = Math.sqrt(d2);
      if (dist < d.portee_px) voulu = d.volume * Math.pow(1 - dist / d.portee_px, 1.5);
    }
    sonBorne += (voulu - sonBorne) * 0.05;
    if (Math.abs(voulu - sonBorne) < 0.004) sonBorne = voulu;
    const t = B.t || 0;
    if (voulu > 0 && Son.Lieu && t - sonBorneDemande >= 300) { sonBorneDemande = t; Son.Lieu.charger('borne_ete'); }
    if (sonBorne > 0.004) {
      if (!Son.boucleActive('borne_ete')) Son.boucle('borne_ete', true, sonBorne, 0.5);
      else Son.reglerBoucle('borne_ete', sonBorne);
    } else if (Son.boucleActive('borne_ete')) Son.boucle('borne_ete', false, 0, 0.5);
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

  return { bancsDe, lieux, peindre, cheminees, fumeA, dessinerFumees, tempoMonte, terrassesOuvertes, moment,
           tempoBloque, bloquer, ouverts, index,
           bornesDe, jourDeChaleur, borneOuverteA, bornesOuvertes, borneOuverte, dansUnJet, enfantsDe, ajouterVisibles,
           dessinerFlaques, majSon, get sonBorne() { return sonBorne; } };
})();
