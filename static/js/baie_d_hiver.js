/* Bandini — la baie l'hiver (docs/jalons/les-bateaux-ne-sont-pas-des-chars.md, vague 5).

   Tant que la neige tient (`Saisons.enHiver`, de decembre au degel de la fin mars) :
   - LA GLACE DE RIVE colle aux berges et aux quais, plus large en fevrier qu'en decembre ;
   - LES GLACES FLOTTANTES derivent sur la baie avec le courant (vers l'est, lentement) — peu en decembre, beaucoup en
     fevrier, la debacle en mars ;
   - LE CHENAL du traversier et de la navette reste ouvert : ils cassent la glace a chaque traversee ;
   - LES CHALOUPES DE PLAISANCE sont sorties de l'eau, sur leurs BERS a quai, sous une bache blanche (ou bleue) et la
     neige. La chaloupe d'une mission (Sven, m52 ; un `amarrage:<lieu>`), le chalutier, le cargo et la vedette restent
     a l'eau.

   ⚠️ RIEN NE SE POSE, RIEN NE SE TIRE (comme `Glace`, `Pont`) : une glace flottante est une fonction de sa CELLULE et
   de l'heure de la partie (`glacesAutour`) ; la glace de rive, de sa tuile ; un ber, de son amarrage. Aucun de, aucune
   tuile changee, aucune entite (le ber est PEINT). La remise d'hiver MARQUE l'amarrage (`Vehicules.majAmarrages` n'y
   fait plus naitre de chaloupe) ; elle n'en retire aucun de la liste — c'est un tirage.

   ⚠️ CE QUE LA BARRE SENT (`traine`, lu par `Vehicules.majPhysique`) : une coque dont l'etrave entre dans la glace la
   croque (`Son.SFX.glaceCoque`), la barre tremble, et la glace lui prend de l'erre a chaque image. Hors de l'hiver,
   `couverture()` vaut 0 et rien ne change, au pixel. */

const BaieDHiver = (function () {
  'use strict';

  const REGLAGES = {
    //: L'empreinte des glaces : change-la, et toutes les glaces changent de place.
    "sel": 0x1CEB0A7,
    //: La part des cellules de `cellule` px qui portent une glace flottante, selon le mois.
    "couverture": {"decembre": 0.2, "janvier": 0.48, "fevrier": 0.58, "mars": 0.34},
    "cellule": 44,
    //: Les demi-axes d'une glace flottante (px) ; le frasil, des eclats de `frasil_cellule` px, `frasil` fois la couverture.
    "rx": [8, 19], "ry": [5, 12], "frasil_cellule": 13, "frasil": 0.6,
    //: La glace de rive : sa largeur depuis la terre (px), selon le mois, a `rive_jeu` px pres.
    "rive": {"decembre": 3, "janvier": 6, "fevrier": 8, "mars": 4}, "rive_jeu": 3,
    //: La derive, en px par seconde de jeu : le courant descend vers l'est.
    "derive": [3.2, 0.6],
    //: Ce que la glace prend a l'erre d'une coque, par image ; au-dessus de `choc_vitesse` px/image, on l'entend et la
    //: barre tremble de `secousse`.
    "traine": 0.05, "choc_vitesse": 0.9, "secousse": 0.35,
    //: Le chenal du traversier et de la navette : leur coque, et `chenal_marge` px de chaque bord.
    "chenal_marge": 10,
    "couleurs": {"dessous": "#7d9fb8", "glace": "#d9e6ee", "neige": "#f3f7fa", "rive": "#dbe7ef", "levre": "#a9c3d6",
                 "frasil": "#c8dbe7"},
  };

  function reglages() { return REGLAGES; }

  /** L'hiver des bateaux : la neige tient. */
  function remisees() { return !!B.partie && typeof Saisons !== 'undefined' && Saisons.enHiver(); }

  /** La part de la baie prise par les glaces en ce moment (0 hors de l'hiver). */
  function couverture() {
    if (!remisees() || typeof Calendrier === 'undefined') return 0;
    return REGLAGES.couverture[Calendrier.mois(B.partie.jour)] || 0;
  }
  function largeurDeRive() {
    if (!remisees() || typeof Calendrier === 'undefined') return 0;
    return REGLAGES.rive[Calendrier.mois(B.partie.jour)] || 0;
  }

  /** Un melange 32 bits (`Math.imul`) : `hash2` repartit mal de petites cellules voisines. */
  function melange(a, b) {
    let h = Math.imul(a ^ REGLAGES.sel, 0x9E3779B1) ^ Math.imul((b | 0) + 0x7F4A7C15, 0x85EBCA6B);
    h ^= h >>> 16; h = Math.imul(h, 0x7FEB352D); h ^= h >>> 15; h = Math.imul(h, 0x846CA68B); h ^= h >>> 16;
    return h >>> 0;
  }

  /** Ou en est la derive, en px : une pure fonction de l'heure de la partie. */
  function derive() {
    const p = B.partie, s = ((p.jour - 1) + p.heure) * B.defs.economie.jour_secondes;
    return [s * REGLAGES.derive[0], s * REGLAGES.derive[1]];
  }

  // --- Le chenal et les quais du traversier ------------------------------------------------------------------

  let chenal = null, chenalSource = null;
  /** Les segments que le traversier et la navette gardent ouverts, et les tuiles de leurs quais. */
  function leChenal() {
    const src = B.defs && B.defs.carte;
    if (chenal && chenalSource === src) return chenal;
    chenalSource = src;
    chenal = { segments: [], quais: new Set() };
    const c = Monde.carte;
    [typeof Traversier !== 'undefined' ? Traversier : null, typeof Navette !== 'undefined' ? Navette : null].forEach(function (T) {
      const d = T && T.donnees();
      if (!d || d.escales.length < 2) return;
      const centre = function (q) { return [q.px + d.largeurPx / 2, q.py + d.hauteurPx / 2]; };
      for (let k = 0; k + 1 < d.escales.length; k++) {
        chenal.segments.push({ a: centre(d.escales[k]), b: centre(d.escales[k + 1]), demi: d.hauteurPx / 2 + REGLAGES.chenal_marge });
      }
      if (c) d.escales.forEach(function (q) {
        for (let y = q.y - 1; y <= q.y + d.coque.largeur; y++) for (let x = q.x - 1; x <= q.x + d.coque.longueur; x++) chenal.quais.add(y * c.w + x);
      });
    });
    return chenal;
  }

  function distSegment(x, y, s) {
    const ax = s.a[0], ay = s.a[1], dx = s.b[0] - ax, dy = s.b[1] - ay, l2 = dx * dx + dy * dy;
    const u = l2 ? Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / l2)) : 0;
    return Math.hypot(x - ax - dx * u, y - ay - dy * u);
  }

  /** Ce point est-il dans le chenal (a `marge` px pres) ? */
  function dansLeChenal(x, y, marge) {
    for (const s of leChenal().segments) if (distSegment(x, y, s) < s.demi + (marge || 0)) return true;
    return false;
  }

  // --- Les glaces flottantes ---------------------------------------------------------------------------------

  /** La glace de la cellule (cu, cw) du repere qui derive, ou null : { u, w, rx, ry, rot, h }. */
  function glaceDe(cu, cw, cov) {
    const h = melange(cu * 92821 + 7, cw);
    if ((h % 10000) / 10000 >= cov) return null;
    const C = REGLAGES.cellule, h2 = melange(h, 0xF10E);
    const rx = REGLAGES.rx[0] + (h2 % 1000) / 1000 * (REGLAGES.rx[1] - REGLAGES.rx[0]);
    const ry = Math.min(rx, REGLAGES.ry[0] + ((h2 >>> 10) % 1000) / 1000 * (REGLAGES.ry[1] - REGLAGES.ry[0]));
    return { u: cu * C + C * 0.2 + ((h >>> 8) % 1000) / 1000 * C * 0.6, w: cw * C + C * 0.2 + ((h >>> 18) % 1000) / 1000 * C * 0.6,
             rx: rx, ry: ry, rot: ((h2 >>> 20) % 16) / 16 * Math.PI, h: h2 };
  }

  /** Les glaces flottantes dont le centre tombe dans ce rectangle du monde (px), en coordonnees du monde. Seulement
      celles qui flottent : centre sur l'eau, hors du chenal. */
  function glacesDans(x0, y0, x1, y1) {
    const cov = couverture(), out = [];
    if (!cov) return out;
    const C = REGLAGES.cellule, dr = derive();
    const u0 = Math.floor((x0 - dr[0]) / C), u1 = Math.floor((x1 - dr[0]) / C);
    const w0 = Math.floor((y0 - dr[1]) / C), w1 = Math.floor((y1 - dr[1]) / C);
    for (let cw = w0; cw <= w1; cw++) for (let cu = u0; cu <= u1; cu++) {
      const g = glaceDe(cu, cw, cov);
      if (!g) continue;
      const x = g.u + dr[0], y = g.w + dr[1];
      if (!Monde.estEau(Math.floor(x / TT), Math.floor(y / TT)) || dansLeChenal(x, y, g.rx)) continue;
      out.push({ x: x, y: y, rx: g.rx, ry: g.ry, rot: g.rot, h: g.h });
    }
    return out;
  }

  /** Ce point est-il sur une glace flottante ? */
  function surUneGlace(x, y) {
    const m = REGLAGES.rx[1] + 2;
    for (const g of glacesDans(x - m, y - m, x + m, y + m)) {
      const c = Math.cos(g.rot), s = Math.sin(g.rot), dx = x - g.x, dy = y - g.y;
      const a = (dx * c + dy * s) / g.rx, b = (-dx * s + dy * c) / g.ry;
      if (a * a + b * b <= 0.9) return true;
    }
    return false;
  }

  // --- La glace de rive --------------------------------------------------------------------------------------

  function terre(c, tx, ty) {
    if (tx < 0 || ty < 0 || tx >= c.w || ty >= c.h) return false;           // le bord du monde n'est pas une rive
    return c.solide[ty * c.w + tx] !== 2;
  }
  const COTES = [[0, -1], [0, 1], [-1, 0], [1, 0]];

  /** La largeur de la glace de rive sur ce cote, a ce quart de tuile (px). */
  function profondeur(tx, ty, k, seg, base) {
    const j = REGLAGES.rive_jeu, h = melange(tx * 4 + k, ty * 4 + seg);
    return Math.max(1, base + (h % (2 * j + 1)) - j);
  }

  /** Ce point est-il sur la glace de rive ? */
  function surLaRive(x, y) {
    const base = largeurDeRive(), c = Monde.carte;
    if (!base || !c) return false;
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    if (terre(c, tx, ty) || tx < 0 || ty < 0 || tx >= c.w || ty >= c.h || leChenal().quais.has(ty * c.w + tx)) return false;
    const lx = x - tx * TT, ly = y - ty * TT;
    for (let k = 0; k < 4; k++) {
      const d = COTES[k];
      if (!terre(c, tx + d[0], ty + d[1])) continue;
      const loin = d[1] < 0 ? ly : d[1] > 0 ? TT - ly : d[0] < 0 ? lx : TT - lx;
      const le = d[1] !== 0 ? lx : ly;
      if (loin < profondeur(tx, ty, k, Math.min(3, Math.floor(le / 4)), base)) return true;
    }
    return false;
  }

  /** La glace, la ou est ce point : la rive ou une glace flottante. */
  function dansLaGlace(x, y) {
    if (!couverture()) return false;
    return surLaRive(x, y) || surUneGlace(x, y);
  }

  // --- Ce que la barre sent ----------------------------------------------------------------------------------

  //: Qui etait deja dans la glace a l'image d'avant (on ne croque qu'en y ENTRANT).
  const dedans = new WeakMap();

  /** Une image de coque : son etrave dans la glace lui prend de l'erre ; en y entrant vite, le choc et le craquement. */
  function traine(v) {
    if (!v.def || !v.def.eau || !couverture() || B.interieur || B.bloc) return false;
    const demi = v.def.longueur / 2, sens = v.vitesse >= 0 ? 1 : -1;
    const ex = v.x + Math.cos(v.angle) * demi * sens, ey = v.y + Math.sin(v.angle) * demi * sens;
    const pris = dansLaGlace(ex, ey) || dansLaGlace(v.x, v.y);
    const avant = dedans.get(v);
    dedans.set(v, pris);
    if (!pris) return false;
    if (!avant && Math.abs(v.vitesse) >= REGLAGES.choc_vitesse) {
      // La coque du joueur, c'est la sienne : il l'entend comme son moteur ; celle d'un autre, de la ou elle est.
      if (v.conducteur === B.joueur) Son.SFX.glaceCoque(); else Son.depuis(v, function () { Son.SFX.glaceCoque(); });
      if (v.conducteur === B.joueur) B.cam.secousse = Math.max(B.cam.secousse || 0, REGLAGES.secousse);
    }
    v.vitesse *= 1 - REGLAGES.traine;
    return true;
  }

  // --- Les bers ----------------------------------------------------------------------------------------------

  let bers = null, bersCarte = null;
  //: Ou l'on remise une chaloupe : les planches d'un quai (`Q`) d'abord, puis la greve, le gazon — jamais un trottoir
  //: (`.`) ni la chaussee : une coque sur son ber au milieu des passants ne se croyait pas.
  const SOLS_DE_BER = { Q: 4, s: 3, g: 2, ",": 1 };
  /** Ou chaque amarrage remise sa chaloupe : une tuile de terre a deux pas au plus (le quai, la greve), la plus pres, sur
      le meilleur sol, libre d'un autre ber. Une fois par carte. { place, x, y, debout } — `debout` : la coque tourne vers
      le nord (la terre est a l'est ou a l'ouest de l'eau). Sans sol qui convienne, la chaloupe est remisee ailleurs. */
  function lesBers() {
    const c = Monde.carte, def = c && c.def;
    if (bers && bersCarte === c) return bers;
    bersCarte = c; bers = [];
    const prises = new Set();
    for (const place of (def && def.amarrages) || []) {
      let choix = null, note = -1;
      for (let dy = -2; dy <= 2; dy++) for (let dx = -2; dx <= 2; dx++) {
        const tx = place.x + dx, ty = place.y + dy, i = ty * c.w + tx;
        if ((!dx && !dy) || tx < 0 || ty < 0 || tx >= c.w || ty >= c.h || c.solide[i] !== 0 || c.route[i] || prises.has(i)) continue;
        const sol = SOLS_DE_BER[Monde.glyphe(tx, ty)];
        if (!sol) continue;
        const n = sol * 10 - Math.abs(dx) - Math.abs(dy);
        if (n > note) { note = n; choix = { tx: tx, ty: ty, dx: dx, dy: dy }; }
      }
      if (!choix) continue;
      prises.add(choix.ty * c.w + choix.tx);
      const debout = Math.abs(choix.dx) > Math.abs(choix.dy);
      bers.push({ place: place, x: choix.tx * TT + 8, y: choix.ty * TT + 8, debout: debout, bleue: melange(place.x, place.y) % 3 === 0 });
    }
    return bers;
  }

  /** Une chaloupe remisee : ses bers de bois, sa coque sous la bache tendue (le faite, les sangles), la neige sur le
      dessus. Couchee (la coque est-ouest, l'etrave a l'est) ou debout (nord-sud, l'etrave au nord). */
  function peindreBer(debout, bleue) {
    const b = bleue ? { dessus: '#3d7fc4', flanc: '#2a5f99', faite: '#6aa3dc', sangle: '#1d4675' }
                    : { dessus: '#eef3f6', flanc: '#c3d1dc', faite: '#ffffff', sangle: '#9fb1bf' };
    const coque = '#24323f', bois = '#7a5532', boisFonce = '#4e3520', neige = '#ffffff', neigeOmbre = '#dfe9f2';
    return function (ctx, w, h) {
      const px = function (c, x, y, ww, hh) { ctx.fillStyle = c; ctx.fillRect(x, y, ww, hh); };
      px('rgba(0,0,0,0.28)', 3, h - 3, w - 6, 2);                                          // l'ombre au sol
      if (!debout) {
        // Les deux bers : un poteau de chaque bord, la semelle au sol.
        for (const x of [7, w - 12]) { px(bois, x, 12, 2, h - 15); px(bois, x + 4, 12, 2, h - 15); px(boisFonce, x - 1, h - 4, 8, 1); }
        // La coque sous la bache : le flanc (ombre), le dessus (clair), l'etrave en pointe a l'est.
        for (let y = 3; y <= 13; y++) {
          const pointe = Math.abs(y - 8) > 3 ? 3 : Math.abs(y - 8) > 1 ? 1 : 0;
          px(y <= 7 ? b.dessus : b.flanc, 2, y, w - 6 - pointe * 2, 1);
        }
        px(b.dessus, w - 4, 7, 2, 2);                                                        // le bout de l'etrave
        px(b.faite, 3, 5, w - 10, 1);                                                        // le faite de la bache
        for (let x = 7; x < w - 7; x += 6) px(b.sangle, x, 8, 1, 6);                         // les sangles
        px(coque, 3, 14, w - 10, 1); px(coque, w - 7, 13, 2, 1);                              // la quille qui depasse
        // La neige sur le dessus, en bourrelets.
        px(neige, 4, 2, w - 13, 2); px(neige, 8, 1, w - 20, 1); px(neigeOmbre, 4, 4, w - 13, 1);
      } else {
        for (const y of [10, h - 13]) { px(bois, 2, y, 2, 6); px(bois, w - 4, y, 2, 6); px(boisFonce, 1, y + 6, w - 2, 1); }
        for (let x = 4; x <= w - 5; x++) {
          const pointe = Math.abs(x - (w - 1) / 2) > 4 ? 3 : Math.abs(x - (w - 1) / 2) > 2 ? 1 : 0;
          px(x <= (w - 1) / 2 + 1 ? b.dessus : b.flanc, x, 3 + pointe * 2, 1, h - 10 - pointe * 2);
        }
        px(b.faite, Math.floor(w / 2) - 1, 4, 1, h - 12);
        for (let y = 9; y < h - 8; y += 6) px(b.sangle, 5, y, w - 10, 1);
        px(coque, 5, h - 7, w - 10, 1);
        px(neige, 5, 5, Math.floor(w / 2) - 4, h - 16); px(neige, 6, 3, w - 12, 2); px(neigeOmbre, Math.floor(w / 2), 6, 2, h - 18);
      }
    };
  }

  /** Les chaloupes remisees sur leurs bers, a l'ecran — peintes avec le sol, mais APRES la neige au sol. */
  function dessinerBers(ctx, vue) {
    if (B.interieur || B.bloc || !Monde.carte || !remisees()) return 0;
    let n = 0;
    for (const b of lesBers()) {
      const w = b.debout ? 18 : 34, h = b.debout ? 36 : 20;
      const x = Math.round(b.x - w / 2 - vue.x), y = Math.round(b.y - h + 6 - vue.y);
      if (x < -w || y < -h || x > VW || y > VH) continue;
      // ⚠️ Une coque A L'EAU sur cet amarrage (la chaloupe de Sven, celle d'une mission) : pas de ber vide a cote.
      if (B.entites.some(function (q) { return q.type === 'vehicule' && q.amarrage === b.place; })) continue;
      const cle = 'ber-' + (b.debout ? 'debout' : 'couche') + (b.bleue ? '-bleu' : '-blanc');
      ctx.drawImage(Atlas.cuirePeintre(cle, w, h, peindreBer(b.debout, b.bleue)), x, y);
      n += 12;
    }
    B.stats.rects += n;
    return n;
  }

  // --- Le dessin de la glace ---------------------------------------------------------------------------------

  /** Le contour d'une glace flottante, AJOUTE au chemin en cours (le remplissage se fait par lot). */
  function polygone(ctx, g, vue, k, dx, dy) {
    const c = Math.cos(g.rot), s = Math.sin(g.rot);
    for (let i = 0; i < 9; i++) {
      const t = i / 9 * Math.PI * 2, r = 0.82 + ((g.h >>> (i * 3)) & 7) / 7 * 0.22;
      const px = Math.cos(t) * g.rx * r * k, py = Math.sin(t) * g.ry * r * k;
      const x = Math.round(g.x + px * c - py * s - vue.x + dx), y = Math.round(g.y + px * s + py * c - vue.y + dy);
      if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y);
    }
    ctx.closePath();
  }

  /** Un lot de rectangles (x, y, w, h a plat), d'une seule teinte : un chemin, un remplissage. */
  function remplir(ctx, teinte, l) {
    if (!l.length) return 0;
    ctx.fillStyle = teinte;
    ctx.beginPath();
    for (let k = 0; k < l.length; k += 4) ctx.rect(l[k], l[k + 1], l[k + 2], l[k + 3]);
    ctx.fill();
    return 1;
  }

  /** La glace de la baie a l'ecran : la rive, le frasil, les bords du chenal, les glaces flottantes — taillees a l'eau
      (le chemin du clip suit les tuiles d'eau). Les bers se peignent a part (`dessinerBers`).
      ⚠️ PAR LOTS : un chemin et un remplissage par teinte (la premiere version, un `fillRect` par quart de tuile et trois
      remplissages par glace, coutait 3,7 ms de plus par image au processeur x4). */
  function dessiner(ctx, vue) {
    if (B.interieur || B.bloc || !Monde.carte || !B.partie) return;
    const cov = couverture(), c = Monde.carte;
    if (!cov) return;
    const R = REGLAGES, coul = R.couleurs;
    const tx0 = Math.max(0, Math.floor(vue.x / TT)), ty0 = Math.max(0, Math.floor(vue.y / TT));
    const tx1 = Math.min(c.w - 1, Math.floor((vue.x + VW) / TT)), ty1 = Math.min(c.h - 1, Math.floor((vue.y + VH) / TT));
    let eau = 0;
    ctx.save();
    ctx.beginPath();
    for (let ty = ty0; ty <= ty1; ty++) {
      let debut = -1;
      for (let tx = tx0; tx <= tx1 + 1; tx++) {
        const e = tx <= tx1 && c.solide[ty * c.w + tx] === 2;
        if (e && debut < 0) debut = tx;
        if (!e && debut >= 0) { ctx.rect(Math.round(debut * TT - vue.x), Math.round(ty * TT - vue.y), (tx - debut) * TT, TT); debut = -1; eau++; }
      }
    }
    if (!eau) { ctx.restore(); return; }
    ctx.clip();
    const rive = [], levre = [], frasil = [], eclats = [], eclatsSombres = [];
    // La glace de rive : par quart de tuile, contre chaque cote qui touche la terre.
    const base = largeurDeRive(), quais = leChenal().quais;
    for (let ty = ty0; ty <= ty1; ty++) for (let tx = tx0; tx <= tx1; tx++) {
      if (c.solide[ty * c.w + tx] !== 2 || quais.has(ty * c.w + tx)) continue;
      const x = Math.round(tx * TT - vue.x), y = Math.round(ty * TT - vue.y);
      for (let k = 0; k < 4; k++) {
        const d = COTES[k];
        if (!terre(c, tx + d[0], ty + d[1])) continue;
        for (let seg = 0; seg < 4; seg++) {
          const p = Math.min(TT, profondeur(tx, ty, k, seg, base));
          let rx, ry, rw, rh;
          if (d[1] !== 0) { rx = x + seg * 4; rw = 4; rh = p; ry = d[1] < 0 ? y : y + TT - p; }
          else { ry = y + seg * 4; rh = 4; rw = p; rx = d[0] < 0 ? x : x + TT - p; }
          rive.push(rx, ry, rw, rh);
          // La levre de la glace, du cote de l'eau.
          if (d[1] < 0) levre.push(rx, ry + rh - 1, rw, 1); else if (d[1] > 0) levre.push(rx, ry, rw, 1);
          else if (d[0] < 0) levre.push(rx + rw - 1, ry, 1, rh); else levre.push(rx, ry, 1, rh);
        }
      }
    }
    // Le frasil : des eclats qui derivent avec le reste.
    const dr = derive(), F = R.frasil_cellule, covF = cov * R.frasil;
    for (let cw = Math.floor((vue.y - dr[1]) / F); cw <= Math.floor((vue.y + VH - dr[1]) / F); cw++) {
      for (let cu = Math.floor((vue.x - dr[0]) / F); cu <= Math.floor((vue.x + VW - dr[0]) / F); cu++) {
        const h = melange(cu * 7 + 3, cw * 13 + 0xF5A);
        if ((h % 1000) / 1000 >= covF) continue;
        const x = cu * F + (h >>> 12) % F + dr[0], y = cw * F + (h >>> 20) % F + dr[1];
        if (dansLeChenal(x, y, 0)) continue;
        frasil.push(Math.round(x - vue.x), Math.round(y - vue.y), 2 + (h >>> 28) % 3, 1);
      }
    }
    // Les bords du chenal : la glace cassee que le traversier repousse, serree contre le bord de la glace, de plus en
    // plus rare vers le milieu du chenal.
    for (const sg of leChenal().segments) {
      const dx = sg.b[0] - sg.a[0], dy = sg.b[1] - sg.a[1], l = Math.hypot(dx, dy), ux = dx / l, uy = dy / l;
      for (let t = 0; t <= l; t += 2) {
        const mx = sg.a[0] + ux * t, my = sg.a[1] + uy * t;
        if (mx < vue.x - 20 || mx > vue.x + VW + 20 || my < vue.y - 60 || my > vue.y + VH + 60) continue;
        for (const cote of [1, -1]) {
          const h = melange(Math.round(t), cote * 977 + Math.round(sg.a[1]));
          if (h % 10 < 4) continue;
          const r = ((h >>> 8) % 1000) / 1000, loin = sg.demi + 4 - r * r * 22;
          const x = mx - uy * loin * cote, y = my + ux * loin * cote;
          ((h >>> 4) % 3 ? eclats : eclatsSombres).push(Math.round(x - vue.x), Math.round(y - vue.y), 2 + (h >>> 12) % 4, 1 + (h >>> 16) % 3);
        }
      }
    }
    let n = remplir(ctx, coul.rive, rive) + remplir(ctx, coul.levre, levre) + remplir(ctx, coul.frasil, frasil)
          + remplir(ctx, coul.glace, eclats) + remplir(ctx, coul.dessous, eclatsSombres);
    // Les glaces flottantes : le dessous bleute qui deborde dans l'eau, la glace, la neige dessus — un lot par couche.
    const m = R.rx[1] + 4, glaces = glacesDans(vue.x - m, vue.y - m, vue.x + VW + m, vue.y + VH + m);
    if (glaces.length) {
      for (const couche of [[coul.dessous, 1.08, 0, 1], [coul.glace, 1, 0, 0], [coul.neige, 0.62, -1, -1]]) {
        ctx.fillStyle = couche[0];
        ctx.beginPath();
        for (const g of glaces) polygone(ctx, g, vue, couche[1], couche[2], couche[3]);
        ctx.fill();
        n++;
      }
    }
    ctx.restore();
    B.stats.rects += n;
  }

  /** Une partie qui recommence (la carte peut changer). */
  function oublier() { chenal = null; chenalSource = null; bers = null; bersCarte = null; }

  return { REGLAGES, reglages, remisees, couverture, largeurDeRive, derive, glacesDans, surUneGlace, surLaRive,
           dansLaGlace, dansLeChenal, leChenal, traine, lesBers, dessiner, dessinerBers, oublier };
})();
