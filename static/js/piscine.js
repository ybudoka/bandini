/* UN CHAR DANS LA PISCINE (M16, e05 et e14 — 1er oct. 2026).

   Les villas des Érables ont une piscine creusée dans leur cour (`?`, `villas.py`) : solidité 3, aucun char n'y entre
   en roulant — la haie de cèdres et la margelle l'en empêchent. Deux missions y mettent quand même un char :
   - e05 : les Chevreuils en ont poussé un dans la piscine de Diane ; on l'en sort au TREUIL de la remorqueuse
     (`remorquer`) — klaxon, à quelques mètres, la haie entre les deux : il remonte, dégoulinant, sur la fourche ;
   - e14 : la berline du maire doit finir dans sa propre piscine (`plonger`) — on l'arrête au bord, on descend, elle
     roule dedans.

   Dedans, IL RESTE PRIS (une piscine n'est pas la baie : 1,5 m d'eau, le toit dépasse) — il ne coule pas, il ne
   roule plus, on n'y monte pas. Il se peint sous l'eau claire (`dessinerChar`) : le toit pâle et ondulant, l'eau par-
   dessus, des ronds, une bulle de temps en temps. ⚠️ Rien ne touche à l'eau ni à la physique d'un char ailleurs : ce
   module ne lit que `v.piscine`, que lui seul pose.

   ⚠️ AUCUN DÉ : la piscine se trouve sans tirage (la plus proche du lieu nommé), la chute est une interpolation, les
   éclaboussures et les bulles viennent de l'empreinte (`v.id`, `B.t`). La ville d'avant reste la même. */
const Piscine = (function () {
  'use strict';

  //: La piscine d'un lieu (`piscine:<lieu>`) est la plus proche, à tant de tuiles au plus.
  const PRES_TUILES = 70;
  //: Le TREUIL de la remorqueuse : le crochet seul prend un char à 46 px derrière elle (`crochet_portee_px`) ; dans
  //: une piscine, le câble va le chercher jusqu'à tant de pixels, par-dessus la haie.
  const TREUIL_PX = 7 * TT;
  //: `plonger` : arrêté à tant de tuiles au plus du bord, on descend, et il roule dedans.
  const BORD_TUILES = 5;
  //: La chute : tant d'images du bord au fond.
  const CHUTE = 40;
  //: Le glyphe de la piscine creusée (`villas.PISCINE`).
  const GLYPHE = '?';

  let groupes = null, carteDesGroupes = null;

  /** Les piscines de la ville : chaque bloc de tuiles `?` (une piscine de villa fait 2 × 2 ou 3 × 2), avec son
      centre en pixels. Calculé une fois par carte. */
  function piscines() {
    const c = Monde.carte;
    if (!c || c.interieur || B.bloc) return [];
    if (groupes && carteDesGroupes === c) return groupes;
    const vus = {}, out = [];
    for (let ty = 0; ty < c.h; ty++) {
      for (let tx = 0; tx < c.w; tx++) {
        if (c.sol[ty][tx] !== GLYPHE || vus[tx + ',' + ty]) continue;
        const tuiles = [[tx, ty]];
        vus[tx + ',' + ty] = true;
        for (let i = 0; i < tuiles.length; i++) {
          const [x, y] = tuiles[i];
          for (const [nx, ny] of [[x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]]) {
            if (nx < 0 || ny < 0 || nx >= c.w || ny >= c.h || vus[nx + ',' + ny] || c.sol[ny][nx] !== GLYPHE) continue;
            vus[nx + ',' + ny] = true; tuiles.push([nx, ny]);
          }
        }
        let sx = 0, sy = 0;
        tuiles.forEach(function (t) { sx += t[0]; sy += t[1]; });
        out.push({ x: (sx / tuiles.length) * TT + 8, y: (sy / tuiles.length) * TT + 8, tuiles: tuiles });
      }
    }
    groupes = out; carteDesGroupes = c;
    return out;
  }

  /** La piscine la plus proche d'un point, ou null. */
  function presDe(l) {
    if (!l) return null;
    let meilleure = null, dMin = PRES_TUILES * TT * PRES_TUILES * TT;
    for (const p of piscines()) {
      const d = (p.x - l.x) * (p.x - l.x) + (p.y - l.y) * (p.y - l.y);
      if (d < dMin) { dMin = d; meilleure = p; }
    }
    return meilleure ? { x: meilleure.x, y: meilleure.y, piscine: meilleure, nom: 'la piscine' } : null;
  }

  /** Il y est, et sa chute est finie. */
  function dedans(v) { return !!(v && v.piscine && v.piscine.t >= CHUTE); }

  /** Il y TOMBE : du bord (là où il est) jusqu'au milieu de la piscine, en `CHUTE` images. `tout` : il y est déjà
      (posé là par une mission — les Chevreuils l'ont poussé cette nuit). */
  function plonger(v, p, tout) {
    if (!v || !p) return;
    if (v.conducteur === B.joueur) Vehicules.descendre(B.joueur, true);
    if (v.remorqueePar) Vehicules.decrocher(v.remorqueePar);
    v.conducteur = null; v.etat = 'stationne'; v.vitesse = 0; v.vx = 0; v.vy = 0; v.alarme = 0;
    // Le bassin, en pixels : ce qui dépasse n'est pas dans l'eau (le dessin s'y découpe).
    const t = (p.piscine && p.piscine.tuiles) || [[Math.floor(p.x / TT), Math.floor(p.y / TT)]];
    const xs = t.map(function (q) { return q[0]; }), ys = t.map(function (q) { return q[1]; });
    const bassin = { x: Math.min.apply(null, xs) * TT, y: Math.min.apply(null, ys) * TT,
                     l: (Math.max.apply(null, xs) - Math.min.apply(null, xs) + 1) * TT,
                     h: (Math.max.apply(null, ys) - Math.min.apply(null, ys) + 1) * TT };
    v.piscine = { x: p.x, y: p.y, de: { x: v.x, y: v.y }, t: tout ? CHUTE : 0, bassin: bassin };
    v.angle = Math.abs(Math.cos(v.angle)) >= Math.abs(Math.sin(v.angle)) ? (Math.cos(v.angle) >= 0 ? 0 : Math.PI) : v.angle;
    if (tout) { v.x = p.x; v.y = p.y; }
    else Son.depuis(v, function () { Son.SFX.choc('vehicule'); });
  }

  /** Le treuil le sort : il quitte la piscine, mouillé, accroché derrière la remorqueuse (`Vehicules.basculerCrochet`). */
  function sortir(v) {
    if (!v || !v.piscine) return;
    v.piscine = null;
    v.degoutte = 360;
    Son.depuis(v, function () { Son.SFX.choc('crochet'); });
  }

  /** Une image d'un char dans la piscine : sa chute, puis il ne bouge plus ; l'eau éclabousse à l'arrivée. */
  function majChar(v) {
    const p = v.piscine;
    v.vitesse = 0; v.vx = 0; v.vy = 0;
    if (p.t < CHUTE) {
      p.t++;
      const k = p.t / CHUTE, e = k * k;                 // il accélère en tombant
      v.x = p.de.x + (p.x - p.de.x) * e; v.y = p.de.y + (p.y - p.de.y) * e;
      if (p.t === CHUTE) eclabousser(v, 14);
      return;
    }
    v.x = p.x; v.y = p.y;
  }

  /** Les gouttes qui retombent autour, à l'empreinte. */
  function eclabousser(v, n) {
    for (let k = 0; k < n; k++) {
      const h = hash2(v.id * 31 + k, 0x9155);
      const a = (h % 360) * Math.PI / 180, f = 0.6 + ((h >>> 9) % 10) / 10;
      Entites.particule(v.x + Math.cos(a) * 6, v.y + Math.sin(a) * 4, Math.cos(a) * f, -0.8 - ((h >>> 5) % 8) / 10,
                        20 + (h >>> 13) % 12, k % 3 ? '#bfe8f4' : '#ffffff', 2, 0.06);
    }
  }

  /** Mouillé, il dégoutte quelque temps derrière la remorqueuse. */
  function majDegoutte(v) {
    if (!(v.degoutte > 0)) return;
    v.degoutte--;
    if (v.degoutte % 6 === 0) {
      const h = hash2(v.id, v.degoutte);
      Entites.particule(v.x + (h % 11) - 5, v.y + 3, 0, 0.3, 14, '#9ad4e8', 1, 0.02);
    }
  }

  /** ⚠️ LE DESSIN SOUS L'EAU : le toit pâli et légèrement plus petit (il est en dessous), ondulé d'un pixel, puis
      l'eau claire par-dessus, et des ronds qui s'élargissent ; une bulle remonte de temps en temps. Pendant la chute,
      on passe du char sec au char noyé. */
  function dessinerChar(ctx, v, toit, x, y) {
    const p = v.piscine, k = Math.min(1, p.t / CHUTE), demi = toit.width / 2;
    // Il tombe : le char entier, qui s'enfonce de quelques pixels au bord du bassin.
    if (k < 1) {
      ctx.drawImage(toit, Math.round(x - demi), Math.round(y - demi + 4 * k * k));
      B.stats.images++;
      return;
    }
    // Il y est : DÉCOUPÉ AU BASSIN (ce qui dépasserait est sous la margelle), enfoncé de quatre pixels, pâli, et
    // l'eau par-dessus — plus claire au bord, une ligne d'écume en haut.
    const b = p.bassin, ox = x - v.x, oy = y - v.y;
    const bx = Math.round(b.x + ox) + 1, by = Math.round(b.y + oy) + 1, bl = b.l - 2, bh = b.h - 2;
    const ondule = Math.round(Math.sin((B.t + v.id * 7) / 18));
    // L'eau du bassin, d'abord : le fond bleu, plus sombre (on ne voit pas le fond, il y a un char).
    ctx.save();
    ctx.beginPath(); ctx.rect(bx, by, bl, bh); ctx.clip();
    ctx.fillStyle = 'rgba(40,120,160,0.55)';
    ctx.fillRect(bx, by, bl, bh);
    // Le TOIT seul dépasse : on ne peint que le haut du char (sa moitié du dessus), enfoncé de trois pixels — les
    // portières et les roues sont sous l'eau.
    const haut = Math.round(y - demi + 3), coupe = Math.round(toit.height * 0.5);
    ctx.save();
    ctx.beginPath(); ctx.rect(bx, haut, bl, coupe); ctx.clip();
    ctx.drawImage(toit, Math.round(x - demi + ondule), haut);
    ctx.restore();
    // Un voile d'eau léger sur le toit, l'écume tout autour de lui, et la ligne claire au bord du bassin.
    ctx.fillStyle = 'rgba(120,205,232,0.22)';
    ctx.fillRect(bx, haut, bl, coupe);
    ctx.fillStyle = 'rgba(232,248,252,0.75)';
    ctx.fillRect(Math.round(x - v.def.longueur / 2 + ondule), haut + coupe - 1, v.def.longueur, 1);
    ctx.fillStyle = 'rgba(232,248,252,0.5)';
    ctx.fillRect(bx, by, bl, 1);
    ctx.restore();
    B.stats.images++; B.stats.rects += 4;
    // Les ronds qui s'élargissent, l'un après l'autre, et une bulle qui remonte.
    const age = (B.t + v.id * 13) % 90;
    ctx.strokeStyle = 'rgba(232,248,252,' + (0.5 * (1 - age / 90)).toFixed(2) + ')';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.ellipse(Math.round(x), Math.round(y + 4), 4 + age / 9, 2 + age / 18, 0, 0, Math.PI * 2);
    ctx.stroke();
    if (((B.t + v.id) >> 5) % 3 === 0) {
      const h = hash2(v.id, (B.t >> 5));
      ctx.fillStyle = '#e8f8fc';
      ctx.fillRect(Math.round(x + (h % 13) - 6), Math.round(y + ((h >>> 4) % 7) - 3), 2, 2);
    }
    B.stats.images++;
  }

  return { piscines, presDe, dedans, plonger, sortir, majChar, majDegoutte, dessinerChar, eclabousser,
           TREUIL_PX, BORD_TUILES, CHUTE };
})();
