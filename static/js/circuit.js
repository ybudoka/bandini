/* Bandini — le labyrinthe électrifié du piratage (Martin, 27 sept. 2026 : « je veux un jeu de
   labyrinthe électrifié »). Il remplace la séquence de directions de chaque objectif `pirater` :
   on guide une étincelle au stick, de la PRISE (à gauche) au PORT du terminal (à droite), dans des
   couloirs bordés de fils électrifiés. Toucher un fil, c'est un zap : retour au dernier relais.

   Ce module ne fait que le labyrinthe — le tracer, faire avancer l'étincelle, le peindre. C'est
   `Histoire` qui l'ouvre (`commencerPiratage`), qui compte les zaps contre `essais` et qui tranche
   (`avancer`, échec `alarme`) ; `Hud.dessinerPiratage` le pose à l'écran.

   ⚠️ **AUCUN `B.rng`** : le tracé se tire à l'EMPREINTE (le slug de la mission et l'étape). Le
   même labyrinthe à chaque essai — on l'apprend, c'est le jeu —, et ouvrir un terminal ne fait
   pas glisser la ville.

   ⚠️ **LE MÊME AXE QUE LA MARCHE** (`Entree.axe` : clavier, manette, stick tactile) : la vitesse
   suit l'inclinaison, rien de neuf à apprendre au pouce.

   Les coordonnées de l'étincelle sont LOCALES à la boîte : (0, 0) au coin haut-gauche du
   labyrinthe, une case fait `CASE` px. */

const Circuit = (function () {
  'use strict';

  //: La largeur d'une case (le couloir), l'épaisseur d'un fil, le rayon de l'étincelle. Le jeu
  //: qui reste au pouce : CASE − FIL − 2 × RAYON = 10 px (jugé : au moins 6). ⚠️ Réglé à la
  //: capture : à 14 px, la boîte de m53 faisait 100 × 60 sur 480 — illisible au téléphone.
  const CASE = 18, FIL = 2, RAYON = 3;
  //: Un contact, c'est l'étincelle à moins de ça du milieu d'un fil.
  const MARGE = RAYON + FIL / 2;
  //: Plein régime, en px par image ; en deçà de la zone morte, le stick ne pousse rien (celle de
  //: la roue d'armes et de l'ancien piratage : 0,22 — le même pouce).
  const VITESSE = 1.3, ZONE_MORTE = 0.22;
  //: Après un zap : autant d'images sans bouger ni recompter (on voit où l'on est revenu), et
  //: l'éclair qui s'éteint.
  const IMMUNITE = 20, ECLAIR = 12;
  //: La traînée de l'étincelle, en positions retenues.
  const TRAINEE = 6;

  /** Une graine de 32 bits pour une empreinte (FNV-1a). */
  function graine(texte) {
    let h = 2166136261;
    for (let i = 0; i < texte.length; i++) { h ^= texte.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }

  /** Un générateur à graine (mulberry32) : rend une fonction qui donne [0, 1). */
  function generateur(g) {
    let a = g >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /** Le labyrinthe d'une empreinte : parfait (un seul chemin entre deux cases), creusé par
      retour arrière depuis la prise. `est[r * cols + c]` : passage entre (c, r) et (c + 1, r) ;
      `sud[r * cols + c]` : entre (c, r) et (c, r + 1). `entree` / `sortie` : le rang de la prise
      (colonne 0) et du port (dernière colonne). `solution` : les cases de l'une à l'autre ;
      `relais` : sa case du milieu. */
  function generer(empreinte, cols, rangs) {
    const alea = generateur(graine(String(empreinte)));
    const n = cols * rangs;
    const est = new Array(n).fill(false), sud = new Array(n).fill(false), vu = new Array(n).fill(false);
    const entree = Math.floor(alea() * rangs), sortie = Math.floor(alea() * rangs);
    const pile = [entree * cols];
    vu[entree * cols] = true;
    while (pile.length) {
      const i = pile[pile.length - 1], c = i % cols, r = (i - c) / cols;
      const voisins = [];
      if (c > 0 && !vu[i - 1]) voisins.push(i - 1);
      if (c < cols - 1 && !vu[i + 1]) voisins.push(i + 1);
      if (r > 0 && !vu[i - cols]) voisins.push(i - cols);
      if (r < rangs - 1 && !vu[i + cols]) voisins.push(i + cols);
      if (!voisins.length) { pile.pop(); continue; }
      const j = voisins[Math.floor(alea() * voisins.length)];
      if (j === i + 1) est[i] = true;
      else if (j === i - 1) est[j] = true;
      else if (j === i + cols) sud[i] = true;
      else sud[j] = true;
      vu[j] = true;
      pile.push(j);
    }
    // La solution : un parcours en largeur de la prise au port, par les passages ouverts.
    const depart = entree * cols, but = sortie * cols + cols - 1, venu = new Array(n).fill(-1);
    const file = [depart];
    venu[depart] = depart;
    while (file.length) {
      const i = file.shift();
      if (i === but) break;
      const c = i % cols, suivants = [];
      if (c < cols - 1 && est[i]) suivants.push(i + 1);
      if (c > 0 && est[i - 1]) suivants.push(i - 1);
      if (sud[i]) suivants.push(i + cols);
      if (i >= cols && sud[i - cols]) suivants.push(i - cols);
      suivants.forEach(function (j) { if (venu[j] < 0) { venu[j] = i; file.push(j); } });
    }
    const solution = [];
    for (let i = but; ; i = venu[i]) {
      solution.unshift({ c: i % cols, r: Math.floor(i / cols) });
      if (i === depart) break;
    }
    const relais = solution[Math.floor(solution.length / 2)];
    return { cols: cols, rangs: rangs, est: est, sud: sud, entree: entree, sortie: sortie,
             solution: solution, relais: { c: relais.c, r: relais.r } };
  }

  function centre(c, r) { return { x: (c + 0.5) * CASE, y: (r + 0.5) * CASE }; }

  /** La taille du labyrinthe peint, en px (sans le cadre). */
  function taille(p) { return { l: p.cols * CASE, h: p.rangs * CASE }; }

  /** L'étincelle touche-t-elle un fil en (x, y) ? Les quatre côtés de sa case (la prise et le port
      sont les deux seules ouvertures de la bordure), et les quatre POTEAUX de ses coins — ⚠️ un
      poteau touche toujours, même entre deux côtés ouverts : dans un labyrinthe parfait, aucun
      croisement n'est libre de tous ses fils, et c'est là qu'une diagonale au clavier frotte. */
  function touche(p, x, y) {
    const c = Math.max(0, Math.min(p.cols - 1, Math.floor(x / CASE)));
    const r = Math.max(0, Math.min(p.rangs - 1, Math.floor(y / CASE)));
    const lx = x - c * CASE, ly = y - r * CASE, i = r * p.cols + c;
    const ouest = c === 0 ? r !== p.entree : !p.est[i - 1];
    const est = c === p.cols - 1 ? r !== p.sortie : !p.est[i];
    const nord = r === 0 || !p.sud[i - p.cols];
    const sud = r === p.rangs - 1 || !p.sud[i];
    if ((ouest && lx < MARGE) || (est && lx > CASE - MARGE) || (nord && ly < MARGE) || (sud && ly > CASE - MARGE)) return true;
    const px = lx < CASE / 2 ? lx : CASE - lx, py = ly < CASE / 2 ? ly : CASE - ly;
    return px * px + py * py < MARGE * MARGE;
  }

  /** L'étincelle posée à la prise ; `zaps` : ceux qu'on avait déjà pris sur ce terminal (on ne
      les efface pas en abandonnant). */
  function ouvrir(p, zaps) {
    const m = centre(0, p.entree);
    return { plan: p, x: m.x, y: m.y, relais: null, zaps: zaps || 0, immunite: 0, eclair: 0, trace: [] };
  }

  /** Une image : l'étincelle suit `axe` ({x, y, mag}). Rend `'zap'` (un fil touché : elle est
      ramenée au relais, ou à la prise), `'fini'` (le port est atteint), ou `null`. */
  function maj(e, axe) {
    const p = e.plan;
    if (e.eclair > 0) e.eclair--;
    if (e.immunite > 0) { e.immunite--; return null; }
    if (axe && axe.mag > ZONE_MORTE) {
      const k = Math.min(1, (axe.mag - ZONE_MORTE) / (1 - ZONE_MORTE)), n = Math.hypot(axe.x, axe.y) || 1;
      e.x += axe.x / n * VITESSE * k;
      e.y += axe.y / n * VITESSE * k;
      e.trace.push({ x: e.x, y: e.y });
      if (e.trace.length > TRAINEE) e.trace.shift();
    }
    const c = Math.floor(e.x / CASE), r = Math.floor(e.y / CASE);
    // La prise : on n'en ressort pas par la gauche (ce n'est pas un fil, c'est d'où l'on vient).
    if (r === p.entree && e.x < MARGE) e.x = MARGE;
    if (r === p.sortie && e.x >= p.cols * CASE - MARGE) return 'fini';
    if (touche(p, e.x, e.y)) {
      e.zaps++;
      e.eclair = ECLAIR; e.immunite = IMMUNITE; e.trace = [];
      const q = e.relais || { c: 0, r: p.entree }, m = centre(q.c, q.r);
      e.x = m.x; e.y = m.y;
      return 'zap';
    }
    if (c === p.relais.c && r === p.relais.r) e.relais = { c: c, r: r };
    return null;
  }

  //: Les fils grésillent : la plupart bleus, un sur huit qui claque blanc, et ça change quatre
  //: fois par seconde.
  const BLEU = '#3a9ee0', BLANC = '#e8f6ff';

  /** Le labyrinthe à l'écran, son coin haut-gauche en (x0, y0). */
  function dessiner(ctx, e, x0, y0) {
    const p = e.plan, t = Math.floor((B.t || 0) / 15);
    const fil = function (k) { return (hash2(k, t) & 7) === 0 ? BLANC : BLEU; };
    const trait = function (x, y, l, h, k) { ctx.fillStyle = fil(k); ctx.fillRect(x0 + x, y0 + y, l, h); B.stats.rects++; };
    const d = FIL / 2;
    // Les fils : le nord et l'ouest de chaque case, puis l'est et le sud de la bordure.
    for (let r = 0; r < p.rangs; r++) {
      for (let c = 0; c < p.cols; c++) {
        const i = r * p.cols + c;
        if (r === 0 || !p.sud[i - p.cols]) trait(c * CASE - d, r * CASE - d, CASE + FIL, FIL, i * 4);
        if (c === 0 ? r !== p.entree : !p.est[i - 1]) trait(c * CASE - d, r * CASE - d, FIL, CASE + FIL, i * 4 + 1);
        if (c === p.cols - 1 && r !== p.sortie) trait((c + 1) * CASE - d, r * CASE - d, FIL, CASE + FIL, i * 4 + 2);
        if (r === p.rangs - 1) trait(c * CASE - d, (r + 1) * CASE - d, CASE + FIL, FIL, i * 4 + 3);
      }
    }
    // La prise et le port : d'où part le courant, où il doit arriver.
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(x0 - 6, y0 + p.entree * CASE + 4, 5, CASE - 8);
    ctx.fillStyle = '#8fd46a'; ctx.fillRect(x0 + p.cols * CASE + 1, y0 + p.sortie * CASE + 4, 5, CASE - 8);
    // Le relais : gris tant qu'on ne l'a pas passé, doré ensuite.
    const m = centre(p.relais.c, p.relais.r);
    ctx.fillStyle = e.relais ? '#e8b33c' : '#4a4a58'; ctx.fillRect(x0 + m.x - 1, y0 + m.y - 1, 3, 3);
    B.stats.rects += 3;
    // La traînée, puis l'étincelle — qui clignote pendant l'immunité.
    ctx.fillStyle = '#b89a30';
    e.trace.forEach(function (q) { ctx.fillRect(x0 + Math.round(q.x) - 1, y0 + Math.round(q.y) - 1, 2, 2); B.stats.rects++; });
    if (!e.immunite || (e.immunite >> 2) % 2 === 0) {
      ctx.fillStyle = '#fff3a0'; ctx.fillRect(x0 + Math.round(e.x) - RAYON, y0 + Math.round(e.y) - RAYON, RAYON * 2, RAYON * 2);
      ctx.fillStyle = '#ffffff'; ctx.fillRect(x0 + Math.round(e.x) - 1, y0 + Math.round(e.y) - 1, 2, 2);
      B.stats.rects += 2;
    }
    // L'éclair d'un zap : toute la boîte blanchit, puis s'éteint.
    if (e.eclair > 0) {
      ctx.fillStyle = 'rgba(220,240,255,' + (0.55 * e.eclair / ECLAIR).toFixed(2) + ')';
      ctx.fillRect(x0 - 4, y0 - 4, p.cols * CASE + 8, p.rangs * CASE + 8);
      B.stats.rects++;
    }
  }

  return { CASE: CASE, FIL: FIL, RAYON: RAYON, VITESSE: VITESSE, IMMUNITE: IMMUNITE,
           generer: generer, ouvrir: ouvrir, maj: maj, touche: touche, taille: taille, dessiner: dessiner };
})();
