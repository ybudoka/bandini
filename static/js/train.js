/* Le train : une ligne de passage au rang 6 de la bande nord — au sol, sur le viaduc, dans le tunnel.
   Martin (28 sept. 2026) : « je veux un vrai train aérien, terrestre et tunnel » (docs/jalons/le-train.md).

   ⚠️ LE TRAIN EST UNE HEURE, comme la rame du métro : sa place ne dépend que de
   `Autobus.tempsDeLaPartie()` — rien à simuler, pas un dé, la même place au rechargement. Une seule voie,
   un seul train : il fait l'aller vers l'est (Friches → viaduc → gare centrale → tunnel), attend `bout`
   images sous la montagne, fait le retour, attend `bout` images hors carte à l'ouest. */
const Train = (function () {
  'use strict';
  const TT = 16;
  let cache = null, source = null;

  /** Distance couverte et vitesse, `t` images après le départ d'un arrêt, sur un tronçon de `d` px qui finit à
      l'arrêt : accélération `a` jusqu'à `v`, croisière, freinage — ou un triangle si le tronçon est court. */
  function profil(d, v, a, t) {
    const ta = v / a, da = v * ta / 2;
    if (2 * da >= d) {
      const tm = Math.sqrt(d / a);
      if (t <= tm) return { s: a * t * t / 2, v: a * t };
      const r = Math.max(0, 2 * tm - t);
      return { s: d - a * r * r / 2, v: a * r };
    }
    const tc = (d - 2 * da) / v, total = 2 * ta + tc;
    if (t <= ta) return { s: a * t * t / 2, v: a * t };
    if (t <= ta + tc) return { s: da + v * (t - ta), v: v };
    const r = Math.max(0, total - t);
    return { s: d - a * r * r / 2, v: a * r };
  }
  function dureeProfil(d, v, a) {
    const ta = v / a, da = v * ta / 2;
    return 2 * da >= d ? 2 * Math.sqrt(d / a) : 2 * ta + (d - 2 * da) / v;
  }

  /** Un trajet : les arrêts de la TÊTE, en px, dans l'ordre du sens. À l'est, la tête est le bout est du train :
      arrêté en gare, son milieu est sur la gare. Le départ et la fin sont hors carte (ou sous la montagne). */
  function trajet(t, sens) {
    const L = t.horaire.longueur, gares = t.gares.map(function (g) { return { nom: g[0], x: g[1] }; });
    const depart = { nom: null, px: -(L + 40) * TT }, fin = { nom: null, px: (t.tunnel + L + 45) * TT };
    let arrets = gares.map(function (g) { return { nom: g.nom, px: (g.x + 0.5 + L / 2) * TT }; });
    if (sens < 0) {
      arrets = gares.slice().reverse().map(function (g) { return { nom: g.nom, px: (g.x + 0.5 - L / 2) * TT }; });
      return [{ nom: null, px: fin.px - L * TT }].concat(arrets, [{ nom: null, px: depart.px }]);
    }
    return [depart].concat(arrets, [fin]);
  }

  function donnees() {
    const t = B.defs && B.defs.carte && B.defs.carte.train;
    if (!t) { cache = null; source = null; return null; }
    if (t === source) return cache;
    const h = t.horaire, trajets = [];
    let debut = 0;
    [1, -1].forEach(function (sens) {
      const pts = trajet(t, sens), troncons = [];
      for (let i = 0; i + 1 < pts.length; i++) {
        const d = Math.abs(pts[i + 1].px - pts[i].px), duree = dureeProfil(d, h.vitesse, h.acceleration);
        const arret = pts[i].nom ? h.arret : 0;     // on attend en gare AVANT de repartir
        troncons.push({ de: pts[i], vers: pts[i + 1], d: d, debut: debut, arret: arret, duree: duree });
        debut += arret + duree;
      }
      trajets.push({ sens: sens, troncons: troncons });
      debut += h.bout;
    });
    source = t;
    cache = Object.assign({}, t, { yPx: (t.rang + 0.5) * TT, trajets: trajets, periode: debut });
    return cache;
  }

  function etat(temps) {
    const d = donnees();
    if (!d) return null;
    const phase = ((temps % d.periode) + d.periode) % d.periode;
    for (const tr of d.trajets) {
      for (const c of tr.troncons) {
        if (phase < c.debut || phase >= c.debut + c.arret + c.duree) continue;
        if (phase < c.debut + c.arret) return { sens: tr.sens, tete: c.de.px, vitesse: 0, gare: c.de.nom };
        const p = profil(c.d, d.horaire.vitesse, d.horaire.acceleration, phase - c.debut - c.arret);
        return { sens: tr.sens, tete: c.de.px + tr.sens * p.s, vitesse: p.v, gare: null };
      }
    }
    return null;                                     // au bout, sous la montagne ou hors carte
  }

  /** Ce que le train couvre, en px, de gauche à droite. */
  function etendue(e) {
    const L = donnees().horaire.longueur * TT;
    return e.sens > 0 ? [e.tete - L, e.tete] : [e.tete, e.tete + L];
  }

  function enVille() { return !B.interieur && !B.bloc; }

  // ---------------------------------------------------------------- la géométrie
  /** Le viaduc, rampes comprises : du pied de la rampe ouest au pied de la rampe est. */
  function surLeViaduc(x) {
    const d = donnees();
    return !!d && x >= d.viaduc[0] * TT && x < (d.viaduc[1] + 1) * TT;
  }
  /** Au sol : ni sur le viaduc ni ses rampes, ni passé le portail du tunnel. */
  function auSol(x) {
    const d = donnees();
    return !!d && !surLeViaduc(x) && x < d.tunnel * TT;
  }
  const HAUT = 12;                                   // la hauteur du tablier, en px d'écran
  /** La hauteur de la voie à x : 0 au sol, `HAUT` sur le tablier, en pente sur les rampes. */
  function hauteur(x) {
    const d = donnees();
    if (!d || !surLeViaduc(x)) return 0;
    const a = d.viaduc[0] * TT, b = (d.viaduc[1] + 1) * TT, r = d.rampe * TT;
    return Math.round(HAUT * Math.min(1, (x - a) / r, (b - x) / r));
  }

  // ---------------------------------------------------------------- les passages à niveau
  /** Un passage est fermé quand le train le couvre, quand sa tête en est à moins de `annonce` px devant lui, ou
      tant que sa queue ne l'a pas dépassé d'une tuile. ⚠️ FONCTION DE L'HEURE SEULE : un saut dans le temps
      (dormir, recharger) ne laisse jamais une barrière coincée. */
  function passageFerme(i, temps) {
    const d = donnees(), e = d && etat(temps);
    if (!e) return false;
    const p = d.passages[i], a = p[0] * TT, b = (p[1] + 1) * TT, ext = etendue(e);
    const g = e.sens > 0 ? ext[0] - TT : ext[0] - d.horaire.annonce;
    const dr = e.sens > 0 ? ext[1] + d.horaire.annonce : ext[1] + TT;
    return dr > a && g < b;
  }

  /** ⚠️ ON N'ATTEND JAMAIS SUR LA VOIE. Deux passages sont à la bouche d'un carrefour du boulevard : sa ligne
      d'arrêt (la tuile « S ») tombe sur les rails, et un char qui y attendait son tour attendait sur la voie.
      Rend la tuile où s'arrêter : une tuile avant la voie si la ligne est sur un passage, sinon la ligne. */
  function ligneHorsDeLaVoie(sx, sy, p) {
    const d = donnees();
    if (!d || sy !== d.rang || !enVille()) return [sx, sy];
    for (const q of d.passages) if (sx >= q[0] && sx <= q[1]) return [sx - p[0], sy - p[1]];
    return [sx, sy];
  }

  /** ENGAGÉ : le nez a passé la ligne reculée d'un passage. Un char engagé ne s'arrête plus avant le carrefour
      (ni feu, ni STOP, ni boîte) — sinon « jamais derrière soi » (`pointDArret`) l'arrêtait là où il était, sur
      les rails. Faux partout ailleurs. */
  function engage(v, sx, sy, p) {
    const l = ligneHorsDeLaVoie(sx, sy, p);
    if (l[0] === sx && l[1] === sy) return false;
    const demi = v.def.longueur / 2;
    const nx = v.x + p[0] * demi, ny = v.y + p[1] * demi;
    const bx = l[0] * TT + 8 + p[0] * 8, by = l[1] * TT + 8 + p[1] * 8;
    return (nx - bx) * p[0] + (ny - by) * p[1] > 0;
  }

  const PAS_RUE = { '^': -1, 'v': 1 };
  /** La distance d'un char jusqu'à sa ligne d'arrêt devant un passage FERMÉ, dans sa file. Jamais pour une rame
      ni pour une poursuite (comme le signaleur de chantier, `Chantiers.signalDevant`) : la police passe, et le
      train la heurte comme les autres. */
  function signalDevant(v) {
    const d = donnees();
    if (!d || v.rails || v.poursuite || !enVille()) return Infinity;
    const pas = PAS_RUE[v.sens];
    if (!pas) return Infinity;
    const tx = Math.floor(v.x / TT), temps = Autobus.tempsDeLaPartie();
    for (let i = 0; i < d.passages.length; i++) {
      const p = d.passages[i];
      if (tx < p[0] || tx > p[1] || !passageFerme(i, temps)) continue;
      // Le bord de la voie : la même ligne que celle d'un carrefour reculée hors des rails (`ligneHorsDeLaVoie`).
      const ligne = pas < 0 ? (d.rang + 1) * TT : d.rang * TT;
      const devant = (ligne - v.y) * pas - v.def.longueur / 2;
      if (devant >= -2 && devant < 6 * TT) return Math.max(0, devant);
    }
    return Infinity;
  }

  // Les barrières défoncées : le passage du train où on les a cassées. Dessinées cassées jusqu'au train suivant
  // (un état d'image, pas d'horaire : c'est un dégât, pas une heure).
  const brises = {};
  function cycle(temps) { return Math.floor(temps / donnees().periode); }
  function brisee(i) {
    const d = donnees();
    return !!d && brises[i] === cycle(Autobus.tempsDeLaPartie());
  }
  /** Le joueur au volant qui passe une barrière baissée la casse — sans étoile : la barrière n'est pas la police. */
  function defoncer() {
    const d = donnees(), j = B.joueur, v = j && j.dansVehicule;
    if (!v) return;
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT), temps = Autobus.tempsDeLaPartie();
    if (ty < d.rang - 1 || ty > d.rang + 1 || Math.hypot(v.vx || 0, v.vy || 0) < 0.5) return;
    for (let i = 0; i < d.passages.length; i++) {
      const p = d.passages[i];
      if (tx < p[0] || tx > p[1] || brisee(i) || !passageFerme(i, temps)) continue;
      brises[i] = cycle(temps);
      Son.SFX.casse();
      if (B.cam) B.cam.secousse = Math.max(B.cam.secousse || 0, 4);
    }
  }

  /** Depuis combien d'images (jusqu'à `n`) le passage est fermé : le bras s'abaisse en `n` images. */
  function fermeDepuis(i, temps, n) {
    let k = 0;
    while (k < n && passageFerme(i, temps - k - 1)) k++;
    return k;
  }

  /** Les barrières d'un passage, EN VOLUME (Martin, 29 sept. 2026 : « il faut que ce soit 2.5D ») : un poteau
      de chaque côté de la rue, debout — son mât, sa croix de Saint-André, ses deux feux rouges qui alternent —, et
      le bras rayé qui PIVOTE sur la file qui arrive (au sud pour ceux qui montent, au nord pour ceux qui
      descendent) : dressé quand le passage est ouvert, en arc pendant qu'il s'abaisse, à hauteur de capot une fois
      baissé, un moignon penché quand on l'a défoncé. La hauteur `z` se peint à `y - z`, comme le viaduc ; l'ombre
      tombe au sud-est, comme celle des chars. Rend, pour chaque poteau : son pied au sol en px d'écran, le sens du
      bras, son angle (0 couché, π/2 dressé), sa longueur, et l'état des feux. */
  const HAUT_MAT = 24, HAUT_BRAS = 7, HAUT_FEUX = 15, OMBRE = 0.35, PIVOT = 7;   // la charnière du bras, à côté du mât
  function barrieres(cx, cy, y0) {
    const d = donnees(), temps = Autobus.tempsDeLaPartie(), out = [];
    for (let i = 0; i < d.passages.length; i++) {
      const p = d.passages[i], xa = p[0] * TT - cx, xb = (p[1] + 1) * TT - cx;
      if (xb < -60 || xa > VW + 60) continue;
      const ferme = passageFerme(i, temps), casse = brisee(i);
      const bas = ferme ? fermeDepuis(i, temps, 45) / 45 : 0;
      const allume = ferme && (Math.floor(temps / 30) % 2 === 0);
      const long = (xb - xa) * 0.6;
      // [x du pied, y du pied, sens du bras] — le pied au sud-est, sur le trottoir est ; l'autre au nord-ouest.
      for (const [fx, fy, dir] of [[xb + 3, y0 + TT + 7, -1], [xa - 4, y0 - 5, 1]]) {
        const angle = casse ? -0.45 : (1 - bas) * Math.PI / 2;
        out.push({ fx: fx, fy: fy, dir: dir, angle: angle, long: casse ? long * 0.3 : long,
                   feux: [ferme && allume, ferme && !allume], ferme: ferme, casse: casse });
      }
    }
    return out;
  }
  /** Les points du bras, de la charnière au bout : `[x, y d'écran, z]`, un par pixel de longueur. */
  function pointsDuBras(b) {
    const pts = [], c = Math.cos(b.angle), s = Math.sin(b.angle);
    for (let k = 0; k < b.long; k++) {
      const x = b.fx + b.dir * (PIVOT + k * c), z = HAUT_BRAS + k * s;
      pts.push([Math.round(x), Math.round(b.fy - z), z, k]);
    }
    return pts;
  }
  /** Au sol, sous les gens : l'ombre du mât et celle du bras, projetées au sud-est. */
  function dessinerOmbresDesBarrieres(ctx, bs) {
    ctx.fillStyle = 'rgba(8,8,14,0.30)';
    for (const b of bs) {
      for (let z = 0; z < HAUT_MAT; z += 1) ctx.fillRect(Math.round(b.fx + z * OMBRE), Math.round(b.fy + z * OMBRE * 0.5), 2, 1);
      for (const p of pointsDuBras(b)) {
        if (p[2] < 0) continue;
        ctx.fillRect(Math.round(p[0] + p[2] * OMBRE), Math.round(b.fy + p[2] * OMBRE * 0.5) + 1, 1, 2);
      }
      B.stats.rects += 2;
    }
  }
  /** Un poteau et son bras, triés avec les gens et les chars par leur pied. */
  function peindreBarriere(ctx, b) {
    const fx = b.fx, fy = b.fy;
    ctx.fillStyle = '#5f5b55'; ctx.fillRect(fx - 2, fy - 1, 6, 3);                        // le socle de béton
    ctx.fillStyle = '#8a857d'; ctx.fillRect(fx - 2, fy - 1, 6, 1);
    ctx.fillStyle = '#b9bec4'; ctx.fillRect(fx, fy - HAUT_MAT, 1, HAUT_MAT);               // le mât : le flanc au soleil
    ctx.fillStyle = '#6b7077'; ctx.fillRect(fx + 1, fy - HAUT_MAT, 1, HAUT_MAT);           // et l'autre
    // La croix de Saint-André : deux planches blanches bordées de rouge, en X.
    const cy = fy - HAUT_MAT + 1;
    for (let k = -3; k <= 3; k++) {
      const y1 = cy + Math.round((k + 3) * 4 / 6);
      ctx.fillStyle = Math.abs(k) === 3 ? '#c8261e' : '#f1efe9';
      ctx.fillRect(fx + k, y1, 2, 1); ctx.fillRect(fx + k, cy + 4 - (y1 - cy), 2, 1);
    }
    ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(fx - 3, cy + 5, 8, 1);
    // Les deux feux sur leur traverse, chacun sa visière ; allumé, il éclaire autour de lui.
    const ly = fy - HAUT_FEUX;
    ctx.fillStyle = '#1b1b1e'; ctx.fillRect(fx - 4, ly, 10, 3);
    for (let n = 0; n < 2; n++) {
      const lx = n ? fx + 3 : fx - 3, on = b.feux[n];
      if (on) { ctx.fillStyle = 'rgba(255,70,40,0.28)'; ctx.fillRect(lx - 2, ly - 1, 6, 5); }
      ctx.fillStyle = on ? '#ff3b2f' : '#5a1d1a'; ctx.fillRect(lx, ly + 1, 2, 2);
      if (on) { ctx.fillStyle = '#ffd0c0'; ctx.fillRect(lx, ly + 1, 1, 1); }
      ctx.fillStyle = '#0c0c0e'; ctx.fillRect(lx - 1, ly - 1, 4, 1);                      // la visière
    }
    // Le boîtier de la barrière, sur son socle à côté du mât, son contrepoids de l'autre côté de la charnière ;
    // puis le bras, rayé rouge et blanc, sa tranche dans l'ombre.
    const px = fx + b.dir * PIVOT;
    ctx.fillStyle = '#5f5b55'; ctx.fillRect(px - 2, fy - 1, 5, 3);
    ctx.fillStyle = '#d8d4cc'; ctx.fillRect(px - 1, fy - HAUT_BRAS - 1, 1, HAUT_BRAS + 1);
    ctx.fillStyle = '#a19c93'; ctx.fillRect(px, fy - HAUT_BRAS - 1, 2, HAUT_BRAS + 1);
    ctx.fillStyle = '#2d2d30'; ctx.fillRect(px - b.dir * 3 - (b.dir > 0 ? 1 : 0), fy - HAUT_BRAS - 2, 2, 3);
    const couche = Math.abs(Math.cos(b.angle)) > 0.7;
    for (const p of pointsDuBras(b)) {
      const blanc = Math.floor(p[3] / 4) % 2 === 1;
      ctx.fillStyle = blanc ? '#ececec' : '#c8261e'; ctx.fillRect(p[0], p[1], 1, 1);
      ctx.fillStyle = blanc ? '#9c9c9c' : '#7e1812';
      if (couche) ctx.fillRect(p[0], p[1] + 1, 1, 1); else ctx.fillRect(p[0] + 1, p[1], 1, 1);
    }
    if (b.casse) { ctx.fillStyle = '#ececec'; const q = pointsDuBras(b).pop(); if (q) ctx.fillRect(q[0], q[1] - 1, 1, 1); }
    B.stats.rects += 16;
  }

  // ---------------------------------------------------------------- les piliers et les rampes, solides
  // ⚠️ Comme le tronc du sapin (`Fetes.maj`) : la carte de la ville se rebâtit (nouvelle partie, bloc,
  // chargement) et oublie ce qu'on y a posé — on remarque chaque carte neuve. Les rampes sont un REMBLAI :
  // on ne traverse la voie ni à pied ni en char là où elle monte ; sous le tablier, seuls les piliers.
  let marquee = null;
  function marquer() {
    const d = donnees(), c = Monde.carte;
    if (!d || !c || c === marquee) return;
    const poser = function (x) { c.solide[d.rang * c.w + x] = 1; };
    d.piliers.forEach(poser);
    for (let k = 0; k < d.rampe; k++) { poser(d.viaduc[0] + k); poser(d.viaduc[1] - k); }
    marquee = c;
  }

  // ---------------------------------------------------------------- ce qu'on entend
  const PORTEE_CLOCHE = 500, PORTEE_ROULEMENT = 900;
  /** La cloche du passage fermé le plus proche, et le roulement du train à sa distance — étouffé de moitié
      quand il passe sur le viaduc au-dessus de soi, coupé passé le portail. Rien, hors de la ville. */
  function entendre() {
    const d = donnees(), j = B.joueur;
    if (!d || !j || !enVille()) { Son.SFX.cloche_passage(0); Son.SFX.roulement_train(0); return; }
    if (Math.abs(j.y - d.yPx) < 60 * TT) Son.Lieu.charger('train');   // ses sons, une fois, en approchant de la ligne
    const temps = Autobus.tempsDeLaPartie();
    let cloche = 0;
    for (let i = 0; i < d.passages.length; i++) {
      if (!passageFerme(i, temps)) continue;
      const p = d.passages[i], px = (p[0] + p[1] + 1) / 2 * TT;
      cloche = Math.max(cloche, 1 - Math.hypot(px - j.x, d.yPx - j.y) / PORTEE_CLOCHE);
    }
    Son.SFX.cloche_passage(cloche * 0.9);
    const e = etat(temps);
    let roule = 0;
    if (e) {
      const ext = etendue(e), fin = d.tunnel * TT;
      if (ext[0] < fin) {
        const x = Math.max(ext[0], Math.min(Math.min(ext[1], fin), j.x));
        roule = 1 - Math.hypot(x - j.x, d.yPx - j.y) / PORTEE_ROULEMENT;
        roule *= e.vitesse > 0 ? Math.min(1, 0.35 + e.vitesse / d.horaire.vitesse) : 0.2;
        if (surLeViaduc(x) && surLeViaduc(j.x)) roule *= 0.5;      // sous le tablier : le béton étouffe
      }
    }
    Son.SFX.roulement_train(Math.max(0, roule));
  }

  function maj() {
    entendre();
    if (!enVille() || !donnees()) return;
    marquer();
    defoncer();
    heurter();
    klaxonner();
  }

  // ---------------------------------------------------------------- ce qu'il heurte
  // ⚠️ LE TRAIN NE FREINE JAMAIS : il klaxonne, et il passe. La source des dégâts est le train, jamais le
  // joueur : ni meurtre ni crime à son compte (`Entites.tuer` ne crédite que `source === B.joueur`).
  const TRAIN = { type: 'train', nom: 'le train', x: 0, y: 0 };
  // ⚠️ CE QUI FRAPPE TIENT DANS LA RANGÉE DES RAILS (7 px de part et d'autre de l'axe), pas dans les 20 px peints :
  // un char arrêté le nez au bord de la voie (la ligne d'arrêt, le signal du passage) doit être hors d'atteinte.
  // À 10 px, le juge des T du trafic a vu le train écraser un char sage, arrêté à sa ligne.
  const DEMI_TRAIN = 7;
  /** La demi-étendue [en x, en y] d'une chose : un char selon son cap, un passant par son rayon. */
  function demiEtendue(q) {
    if (q.type !== 'vehicule' || !q.def) return [q.r || 5, q.r || 5];
    const c = Math.abs(Math.cos(q.angle || 0)), si = Math.abs(Math.sin(q.angle || 0));
    const L = q.def.longueur / 2, W = q.def.largeur / 2;
    return [c * L + si * W, si * L + c * W];
  }
  function heurter() {
    const d = donnees(), e = etat(Autobus.tempsDeLaPartie());
    if (!e || e.vitesse <= 0) return;
    const ext = etendue(e), feu = B.defs.conduite.physique.feu_sous;
    TRAIN.x = e.tete; TRAIN.y = d.yPx;
    const cx = (ext[0] + ext[1]) / 2, demi = (ext[1] - ext[0]) / 2 + TT;
    for (const q of Entites.autour(cx, d.yPx, demi, function (q) {
      return q.vivant && (q.type === 'vehicule' || q.type === 'pieton' || (q.type === 'joueur' && !q.dansVehicule));
    })) {
      // ⚠️ SON ÉTENDUE, PAS SON CENTRE : un autobus debout dans la rue, le nez sur les rails et le centre à
      // 18 px, passait sous le train sans une égratignure (la relecture finale l'a mesuré).
      const dm = demiEtendue(q);
      if (!auSol(q.x) || q.x + dm[0] < ext[0] || q.x - dm[0] > ext[1] || Math.abs(q.y - d.yPx) >= DEMI_TRAIN + dm[1]) continue;
      const cote = q.y >= d.yPx ? 1 : -1;             // on le jette du côté où il est déjà
      if (q.type === 'vehicule') {
        if (q.conducteur !== B.joueur) q.conducteur = null;   // un char du trafic ne se remet pas en voie
        q.etat = q.etat === 'epave' ? q.etat : 'roule';
        q.y = d.yPx + cote * (DEMI_TRAIN + dm[1] + 2);
        q.vx = e.sens * e.vitesse * 0.6; q.vy = cote * e.vitesse * 0.8;
        const vite = e.vitesse > d.horaire.vitesse * 0.66;
        Vehicules.endommager(q, vite ? q.vie - q.vieMax * feu * 0.5 : q.vieMax * 0.3, TRAIN);
        if (B.cam) B.cam.secousse = Math.max(B.cam.secousse || 0, 8);
        Son.SFX.choc();
      } else {
        if (q.type === 'joueur') Hud.message('FRAPPÉ PAR LE TRAIN', 180);
        Entites.blesser(q, 9999, TRAIN, { renverse: true, angle: e.sens > 0 ? 0 : Math.PI, saigne: 90 });
      }
    }
  }

  const COOLDOWN_KLAXON = 180;
  let klaxonT = 0;
  /** Quelque chose sur la voie, à moins de douze tuiles devant le nez : un long coup de klaxon. */
  function klaxonner() {
    if (klaxonT > 0) { klaxonT--; return; }
    const d = donnees(), e = etat(Autobus.tempsDeLaPartie());
    if (!e || e.vitesse <= 0 || !auSol(e.tete)) return;
    const nez = e.tete, loin = nez + e.sens * 12 * TT;
    const devant = Entites.autour((nez + loin) / 2, d.yPx, 7 * TT, function (q) {
      return q.vivant && (q.type === 'vehicule' || q.type === 'pieton' || q.type === 'joueur')
        && Math.abs(q.y - d.yPx) < DEMI_TRAIN + demiEtendue(q)[1] && (q.x - nez) * e.sens > 0 && auSol(q.x);
    });
    if (devant.length) { Son.SFX.klaxon_train(nez, d.yPx); klaxonT = COOLDOWN_KLAXON; }
  }

  // ---------------------------------------------------------------- le dessin
  /** Les voitures du train, de la tête à la queue : `[gauche, droite]` en px, et la locomotive. */
  function voitures(e) {
    const ext = etendue(e), L = ext[1] - ext[0], loco = 4 * TT, n = 3, v = (L - loco) / n;
    const out = [];
    for (let k = 0; k <= n; k++) {
      const long = k === 0 ? loco : v;
      const debut = k === 0 ? 0 : loco + (k - 1) * v;
      // la tête est à droite vers l'est, à gauche vers l'ouest
      const a = e.sens > 0 ? ext[1] - debut - long : ext[0] + debut;
      out.push({ a: a + 1, b: a + long - 1, loco: k === 0 });
    }
    return out;
  }

  /** ⚠️ COMME LES AUTRES VÉHICULES (Martin, 29 sept. 2026) : chaque voiture est une machine en volume
      (`SPRITES.locomotive`, `SPRITES.voiture_train`) peinte par le peintre des chars, `Vehicules.dessinerUn` —
      même projection, même ombre, mêmes phares la nuit. On lui passe un objet qui a la forme d'un char (un par
      voiture, réutilisé d'une image à l'autre) ; `z` le lève sur le viaduc comme un char qui saute. */
  const PEINTES = [];
  function voitureAPeindre(k, w, e, z) {
    const o = PEINTES[k] || (PEINTES[k] = { type: 'train', etat: 'roule', panneT: 0, swaps: null,
                                            def: { classe: 'train', largeur: 16, longueur: 0 } });
    o.sprite = w.loco ? 'locomotive' : 'voiture_train';
    o.conducteur = w.loco ? 'train' : null;          // la locomotive allume ses phares, les voitures non
    o.def.longueur = w.loco ? 64 : 80;
    o.x = (w.a + w.b) / 2; o.y = donnees().yPx; o.z = z;
    o.angle = e.sens > 0 ? 0 : Math.PI;
    return o;
  }
  /** Peinte, et coupée au portail : ce qui est passé à l'est de `fin` est sous la montagne. */
  function peindreVoiture(ctx, o, cx, cy, fin) {
    ctx.save();
    ctx.beginPath(); ctx.rect(-100000, -100000, fin - cx + 100000, 200000); ctx.clip();
    Vehicules.dessinerUn(ctx, o, cx, cy);
    ctx.restore();
  }

  /** Au sol : la voie (ballast, traverses, rails d'écartement de vrai train), et l'ombre du tablier. */
  function dessinerVoie(ctx, vue) {
    const d = donnees();
    if (!d || !enVille()) return;
    const cx = Math.round(vue.x), cy = Math.round(vue.y), y0 = d.rang * TT - cy;
    if (y0 > VH + 40 || y0 < -60) return;
    const t0 = Math.max(0, Math.floor(cx / TT)), t1 = Math.min(d.tunnel - 1, Math.floor((cx + VW) / TT));
    for (let tx = t0; tx <= t1; tx++) {
      const x = tx * TT - cx;
      if (tx >= d.viaduc[0] && tx <= d.viaduc[1]) {
        const rampe = tx < d.viaduc[0] + d.rampe || tx > d.viaduc[1] - d.rampe;
        if (!rampe) { ctx.fillStyle = 'rgba(0,0,0,0.26)'; ctx.fillRect(x, y0 + 6, TT, TT + 6); }   // l'ombre du tablier
        continue;
      }
      if (d.passages.some(function (q) { return tx >= q[0] && tx <= q[1]; })) {
        // Le passage : un tablier de caoutchouc AU RAS de la rue, les rails noyés dedans, leur ornière sombre.
        ctx.fillStyle = '#4b4a48'; ctx.fillRect(x, y0 + 1, TT, 14);
        ctx.fillStyle = '#3c3b39'; ctx.fillRect(x, y0 + 1, TT, 1); ctx.fillRect(x, y0 + 14, TT, 1);
        ctx.fillStyle = '#2a2927'; ctx.fillRect(x, y0 + 4, TT, 1); ctx.fillRect(x, y0 + 11, TT, 1);
        ctx.fillStyle = '#b9bcc1'; ctx.fillRect(x, y0 + 3, TT, 1); ctx.fillRect(x, y0 + 10, TT, 1);
        continue;
      }
      // Au sol, EN VOLUME : un talus de ballast (son dessus, son flanc sud dans l'ombre, l'ombre au pied), les
      // traverses posées dessus, et les rails debout sur elles, chacun son ombre au sud.
      ctx.fillStyle = '#8a8172'; ctx.fillRect(x, y0, TT, 1);                     // l'arête nord du talus, au soleil
      ctx.fillStyle = '#7d7466'; ctx.fillRect(x, y0 + 1, TT, 12);
      ctx.fillStyle = '#665e52'; ctx.fillRect(x, y0 + 13, TT, 2);                // le flanc sud
      ctx.fillStyle = 'rgba(8,8,14,0.22)'; ctx.fillRect(x, y0 + 15, TT, 2);     // l'ombre du talus
      ctx.fillStyle = '#948a7b'; ctx.fillRect(x + (tx * 7) % 13, y0 + 6, 1, 1); ctx.fillRect(x + (tx * 5) % 11 + 2, y0 + 12, 1, 1);
      for (let k = 1; k < TT; k += 4) {
        ctx.fillStyle = '#6e4d31'; ctx.fillRect(x + k, y0 + 2, 1, 11);         // la traverse : le chant au soleil
        ctx.fillStyle = '#4e3520'; ctx.fillRect(x + k + 1, y0 + 2, 1, 11);
        ctx.fillStyle = 'rgba(8,8,14,0.30)'; ctx.fillRect(x + k, y0 + 13, 2, 1);
      }
      ctx.fillStyle = '#dfe2e6'; ctx.fillRect(x, y0 + 3, TT, 1); ctx.fillRect(x, y0 + 10, TT, 1);   // le champignon
      ctx.fillStyle = '#7b8088'; ctx.fillRect(x, y0 + 4, TT, 1); ctx.fillRect(x, y0 + 11, TT, 1);   // l'âme
      ctx.fillStyle = 'rgba(8,8,14,0.35)'; ctx.fillRect(x, y0 + 5, TT, 1); ctx.fillRect(x, y0 + 12, TT, 1);
    }
    B.stats.rects += (t1 - t0 + 1) * 17;
    dessinerBouche(ctx, d.tunnel * TT - cx, y0);
    dessinerOmbresDesBarrieres(ctx, barrieres(cx, cy, y0));
  }

  /** La bouche du tunnel, AU SOL : le noir qui s'enfonce sous la montagne, et les rails qui s'y perdent. Le
      cadre de béton se peint par-dessus, en haut (`dessinerPortail`).
      ⚠️ LA HAUTEUR SE PEINT AU NORD (`y - z`, comme le viaduc) : la voûte d'un tunnel où passe une locomotive
      de 20 px de haut monte donc bien au-dessus de la voie à l'écran — une ouverture centrée sur les rails
      laissait le toit du train dépasser sur la roche. L'ouverture va du bord sud du ballast (le sol) jusqu'à
      la voûte, arrondie au nord. */
  const BOUCHE = 10, HAUT_BOUCHE = 24;
  function bordsDeLaBouche(y0) { return [y0 - HAUT_BOUCHE, y0 + 16]; }
  /** Les colonnes de l'ouverture : pour chaque rangée d'écran, sa largeur (la voûte arrondie au nord). */
  function largeurDeBouche(y, y0) {
    const b = bordsDeLaBouche(y0), r = BOUCHE / 2;
    if (y < b[0] || y > b[1]) return 0;
    const dy = b[0] + r - y;
    if (dy <= 0) return BOUCHE;
    return Math.max(0, Math.round(2 * Math.sqrt(Math.max(0, r * r - dy * dy))));
  }
  function dessinerBouche(ctx, mx, y0) {
    if (mx < -40 || mx > VW + 40) return;
    const b = bordsDeLaBouche(y0);
    for (let y = b[0]; y <= b[1]; y++) {
      const l = largeurDeBouche(y, y0);
      if (!l) continue;
      const x0 = mx + Math.round((BOUCHE - l) / 2);
      for (let c = 0; c < l; c++) {
        const f = (x0 + c - mx) / (BOUCHE - 1), sol = y > y0 ? 6 : 0;   // le sol, un peu moins noir que la voûte
        ctx.fillStyle = 'rgb(' + Math.round(30 + sol - 24 * f) + ',' + Math.round(29 + sol - 23 * f) + ',' + Math.round(34 + sol - 26 * f) + ')';
        ctx.fillRect(x0 + c, y, 1, 1);
      }
    }
    for (let c = 0; c < 7; c++) {
      ctx.fillStyle = 'rgba(223,226,230,' + (0.65 * (1 - c / 7)).toFixed(2) + ')';
      ctx.fillRect(mx + c, y0 + 3, 1, 1); ctx.fillRect(mx + c, y0 + 10, 1, 1);
    }
    B.stats.rects += 60;
  }

  const ID_TRI = 1e9 + 900;
  /** Les voitures AU SOL se trient avec les gens et les chars, par le bas de leur caisse. */
  function ajouterVisibles(visibles, cx, cy) {
    const d = donnees();
    if (!d || !enVille()) return;
    // Les poteaux des passages, debout : triés par leur pied, comme un lampadaire.
    const y0 = d.rang * TT - Math.round(cy);
    if (y0 < VH + 60 && y0 > -80) {
      barrieres(Math.round(cx), Math.round(cy), y0).forEach(function (b, k) {
        visibles.push({ id: ID_TRI + 10 + k, vivant: true, x: b.fx + Math.round(cx), y: b.fy + Math.round(cy),
                        peindreFoire: function (ctx) { peindreBarriere(ctx, b); } });
      });
    }
    const e = etat(Autobus.tempsDeLaPartie());
    if (!e) return;
    const fin = d.tunnel * TT;
    voitures(e).forEach(function (w, k) {
      const m = (w.a + w.b) / 2;
      if (surLeViaduc(m) || w.a >= fin || w.b < cx - 40 || w.a > cx + VW + 40) return;
      if (d.yPx < cy - 40 || d.yPx > cy + VH + 40) return;
      const o = voitureAPeindre(k, w, e, 0);
      visibles.push({ id: ID_TRI, vivant: true, x: m, y: d.yPx + 8,
                      peindreFoire: function (ctx) { peindreVoiture(ctx, o, cx, cy, fin); } });
    });
  }

  /** En haut, par-dessus les gens et les chars : le viaduc (ses rampes, son tablier, ses piliers), les voitures
      qui y roulent, puis le portail du tunnel — qui avale tout ce qui est passé à l'est. */
  function dessinerHaut(ctx, vue) {
    const d = donnees();
    if (!d || !enVille()) return;
    const cx = Math.round(vue.x), cy = Math.round(vue.y), y0 = d.rang * TT - cy;
    if (y0 > VH + 60 || y0 < -60) return;
    const t0 = Math.max(d.viaduc[0], Math.floor(cx / TT)), t1 = Math.min(d.viaduc[1], Math.floor((cx + VW) / TT));
    for (let tx = t0; tx <= t1; tx++) {
      const x = tx * TT - cx, z = hauteur(tx * TT + TT / 2);
      const haut = y0 - 4 - z;
      ctx.fillStyle = '#6f6b64'; ctx.fillRect(x, haut + 24, TT, z);            // la face du tablier, ou le remblai
      ctx.fillStyle = '#9a968f'; ctx.fillRect(x, haut, TT, 24);                // la dalle
      ctx.fillStyle = '#4a4744'; ctx.fillRect(x, haut, TT, 2); ctx.fillRect(x, haut + 22, TT, 2);   // les garde-corps
      ctx.fillStyle = '#5b3f28';
      for (let k = 1; k < TT; k += 4) ctx.fillRect(x + k, y0 + 2 - z, 2, 12);
      ctx.fillStyle = '#c9ccd1'; ctx.fillRect(x, y0 + 3 - z, TT, 1); ctx.fillRect(x, y0 + 11 - z, TT, 1);
    }
    for (const p of d.piliers) {                                                  // le pied des piliers, sous la face
      if (p < t0 || p > t1) continue;
      ctx.fillStyle = '#5d5953'; ctx.fillRect(p * TT - cx + 3, y0 + 20, 10, 4);
    }
    B.stats.rects += (Math.max(0, t1 - t0 + 1)) * 9;
    const e = etat(Autobus.tempsDeLaPartie()), fin = d.tunnel * TT;
    if (e) {
      voitures(e).forEach(function (w, k) {
        const m = (w.a + w.b) / 2;
        if (surLeViaduc(m) && w.b >= cx - 40 && w.a <= cx + VW + 40) peindreVoiture(ctx, voitureAPeindre(k, w, e, hauteur(m)), cx, cy, fin);
      });
    }
    dessinerPortail(ctx, fin - cx, y0);
  }

  /** Le portail, EN VOLUME : un cadre de béton encastré dans la falaise autour de la bouche — son intrados dans
      l'ombre, son arête au soleil —, le chaperon du mur de tête posé sur la pente, deux murs en aile pleins qui
      retiennent la roche (celui du nord au soleil, celui du sud montre sa face), et l'ombre du tout au sud-est.
      Tout ce qui passe à l'est de sa face est sous la montagne (les voitures sont coupées là, `peindreVoiture`). */
  function dessinerPortail(ctx, mx, y0) {
    if (mx < -60 || mx > VW + 60) return;
    const b = bordsDeLaBouche(y0), n = b[0], s = b[1], E = BOUCHE;
    // L'ombre du portail sur la pente, au sud-est.
    ctx.fillStyle = 'rgba(8,8,14,0.32)';
    ctx.fillRect(mx + E + 9, n - 8, 3, s - n + 18); ctx.fillRect(mx, s + 9, E + 12, 2);
    // Les murs en aile : au nord, un pan qui monte vers la crête (son dessus au soleil) ; au sud, la même pente,
    // dont on voit la face.
    for (let c = -3; c < E + 9; c++) {
      const h = Math.max(0, Math.round((c + 3) * 0.55));
      ctx.fillStyle = '#b3ada2'; ctx.fillRect(mx + c, n - 4 - h, 1, h + 1);
      ctx.fillStyle = '#d0cabe'; ctx.fillRect(mx + c, n - 5 - h, 1, 1);
      const hs = Math.max(0, Math.round((c + 3) * 0.4));
      ctx.fillStyle = '#9a958c'; ctx.fillRect(mx + c, s + 1, 1, 2);
      ctx.fillStyle = '#6f6b64'; ctx.fillRect(mx + c, s + 3, 1, hs + 2);
      ctx.fillStyle = '#4f4c47'; ctx.fillRect(mx + c, s + 5 + hs, 1, 1);
    }
    // Le cadre : les deux piédroits et la voûte, trois pixels de béton autour de l'ouverture — l'intrados sombre
    // contre le noir, l'arête claire dehors.
    for (let y = n - 3; y <= s; y++) {
      const l = largeurDeBouche(y, y0);
      const x0 = l ? mx + Math.round((E - l) / 2) : mx + E / 2, x1 = l ? x0 + l - 1 : x0 - 1;
      const cadre = function (x, r) { ctx.fillRect(x, y, 1, 1); };
      for (let r = 1; r <= 3; r++) {
        if (x0 - r < mx - 3) continue;
        ctx.fillStyle = ['#6a665f', '#a8a397', '#c6c0b4'][r - 1]; cadre(x0 - r, r);
        ctx.fillStyle = ['#46433e', '#78736b', '#8c8880'][r - 1]; cadre(x1 + r, r);
      }
      if (!l) { ctx.fillStyle = y === n - 3 ? '#c6c0b4' : '#a8a397'; ctx.fillRect(mx - 3, y, E + 6, 1); }
    }
    ctx.fillStyle = '#a8a397'; ctx.fillRect(mx - 3, n - 3, 3, n + BOUCHE / 2 - (n - 3));   // les écoinçons de la voûte
    ctx.fillRect(mx + E, n - 3, 3, n + BOUCHE / 2 - (n - 3));
    ctx.fillStyle = '#d9d3c6'; ctx.fillRect(mx + E / 2 - 1, n - 3, 2, 3);                  // la clé de voûte
    // Le chaperon du mur de tête : une dalle posée sur la pente, derrière le cadre.
    ctx.fillStyle = '#9d988f'; ctx.fillRect(mx + E + 3, n - 10, 6, s - n + 16);
    ctx.fillStyle = '#c4beb2'; ctx.fillRect(mx + E + 3, n - 10, 6, 1); ctx.fillRect(mx + E + 3, n - 10, 1, s - n + 16);
    ctx.fillStyle = '#5f5b55'; ctx.fillRect(mx + E + 8, n - 9, 1, s - n + 15); ctx.fillRect(mx + E + 3, s + 5, 6, 1);
    B.stats.rects += 60;
  }

  /** La grande carte : la voie pleine au sol, doublée sur le viaduc, en pointillé sous la montagne ; les gares
      en carrés sombres à cœur bordeaux, comme les stations du métro. */
  function dessinerSurLaCarte(ctx, pos) {
    const d = donnees();
    if (!d) return;
    const w = B.defs.carte.largeur;
    ctx.fillStyle = '#6e1a26';
    for (let tx = 0; tx < w; tx++) {
      const p = pos(tx * TT + TT / 2, d.yPx);
      if (tx >= d.tunnel) { if ((tx - d.tunnel) % 3 === 0) ctx.fillRect(p.x, p.y, 1, 1); }
      else if (tx >= d.viaduc[0] && tx <= d.viaduc[1]) { ctx.fillRect(p.x, p.y - 1, 1, 1); ctx.fillRect(p.x, p.y + 1, 1, 1); }
      else ctx.fillRect(p.x, p.y, 1, 1);
    }
    B.stats.rects += w;
    for (const g of d.gares) {
      const p = pos(g[1] * TT + TT / 2, d.yPx);
      ctx.fillStyle = '#101018'; ctx.fillRect(p.x - 2, p.y - 2, 5, 5);
      ctx.fillStyle = '#b8323f'; ctx.fillRect(p.x - 1, p.y - 1, 3, 3);
      B.stats.rects += 2;
    }
  }

  return { donnees: donnees, etat: etat, etendue: etendue, maj: maj, profil: profil,
           passageFerme: passageFerme, signalDevant: signalDevant, brisee: brisee, ligneHorsDeLaVoie: ligneHorsDeLaVoie, engage: engage,
           surLeViaduc: surLeViaduc, auSol: auSol, hauteur: hauteur, barrieres: barrieres,
           dessinerVoie: dessinerVoie, ajouterVisibles: ajouterVisibles, dessinerHaut: dessinerHaut,
           dessinerSurLaCarte: dessinerSurLaCarte };
})();
