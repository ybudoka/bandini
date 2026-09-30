/* Bandini — un char qui coule pour vrai (docs/jalons/un-char-qui-coule-pour-vrai.md).

   Un char dans l'eau restait entier, en pleines couleurs, pendant ses trois secondes, puis
   `Entites.retirer` le faisait disparaitre d'un coup. Ici, le DESSIN du naufrage (la logique
   reste a `Vehicules.majNoyade` : meme duree, meme perte, meme ejection) :
   - `etat` : ou il en est — la ligne de flottaison court du NEZ vers l'arriere (le moteur pese),
     ce qui est devant est sous l'eau et presque transparent ; il palit, rapetisse, perd son ombre ;
   - `dessinerChar` : le toit en deux moities (sous l'eau, hors de l'eau), l'ecume sur la ligne,
     des ronds autour de la coque ;
   - `poser` / `dessinerSol` : au fond, la trace du naufrage — une grosse bulle qui creve, des
     cercles qui s'elargissent, puis une tache d'huile irisee qui flotte et s'efface.

   ⚠️ AUCUN DE : tout se tire a l'empreinte (`v.id`, l'age de la trace). Le hasard de la ville et
   du trafic ne bouge pas d'un tirage (`test_naufrage_js`). ⚠️ Les ages se comptent en `B.t` : le
   monde fige (menu, pause), la tache attend avec lui. */

const Naufrage = (function () {
  'use strict';

  //: ⚠️ LES REGLAGES VIVENT ICI, PAS DANS LE PAQUET : du dessin que Python ne lit jamais (le
  //: paquet a un plafond gzip, `test_definitions`). La duree du naufrage, elle, reste au paquet
  //: (`recherche.nage.coule_s`) : c'est une regle du jeu, le temps qu'on a pour sortir.
  //: (`nez` : la part du naufrage ou la ligne atteint l'arriere ; `dessus`, `dessous` : l'opacite
  //: de ce qui est hors de l'eau a la fin, et de ce qui est dessous au debut ; `echelle` : ce qu'il
  //: perd en descendant ; `glisse` : les pixels qu'il avance, le nez vers le fond ; `ombre` : la part
  //: du naufrage ou son ombre s'efface.)
  const CHAR = { nez: 0.8, dessus: 0.55, dessous: 0.4, echelle: 0.12, glisse: 2, ombre: 0.25 };
  //: La trace au fond, en images : la bulle gonfle (`bulle`) et creve en gouttes (`gouttes`) ;
  //: `anneaux` cercles, un toutes les `ecart` images, chacun vit `anneau` images ; la tache d'huile
  //: s'etale en `etale`, vit `DUREE` et palit sur ses `palit` dernieres ; une bulle remonte toutes
  //: les `remonte` images tant qu'il reste `remonte_fin` de la tache.
  const FOND = { bulle: 24, gouttes: 16, anneaux: 3, ecart: 16, anneau: 70, etale: 240, palit: 180,
                 remonte: 64, remonte_fin: 0.4 };
  const DUREE = 8 * 60;
  //: L'huile : ses reflets, du violet au vert et a l'ambre — l'arc-en-ciel sale d'une flaque.
  const IRISE = ['106,76,147', '46,139,122', '201,161,59', '59,95,160'];
  const ECUME = '220,236,244';
  //: De combien l'image d'un char deborde sa caisse, devant et derriere, en pixels.
  const BORD = 4;

  const traces = [];
  let coupe = false;
  /** Pour les juges : couper le module (l'ancien naufrage, qui s'evapore), puis le remettre. */
  function couper(oui) { coupe = !!oui; }
  function oublier() { traces.length = 0; }

  /** Un entier de 0 a 1 tire de `a` et `b`, sans de. */
  function empreinte(a, b) {
    let h = (Math.imul((a | 0) + 0x9E37, 0x85EBCA6B) ^ Math.imul((b | 0) + 0x7F4A, 0xC2B2AE35)) >>> 0;
    h = Math.imul(h ^ (h >>> 15), 0x2C1B3C6D) >>> 0;
    return ((h ^ (h >>> 12)) >>> 0) / 4294967296;
  }

  function profondeur() {
    const f = B.defs.conduite && B.defs.conduite.ombre;
    return (f && f.profondeur) || 1;
  }

  /** Ou en est le naufrage de `v`, ou null s'il ne coule pas. `ligne` : la ligne de flottaison,
      en pixels le long du char depuis son centre (+ devant) ; `dessus`, `dessous` : l'opacite de
      ce qui est hors de l'eau et dessous ; `echelle`, `glisse` (px vers l'avant), `ombre` (0 a 1). */
  function etat(v) {
    if (coupe || !v || !v.coule || !v.def) return null;
    const u = Math.min(1, v.coule / (B.defs.recherche.nage.coule_s * 60)), demi = v.def.longueur / 2;
    // ⚠️ Doux au depart : il flotte un instant, puis le nez pique — et la ligne va jusqu'a
    // l'arriere avant la fin, pour que la derniere seconde soit tout entiere sous l'eau.
    const p = Math.min(1, u / CHAR.nez);
    return {
      u: u,
      ligne: demi - p * p * (3 - 2 * p) * (2 * demi + 1),
      dessus: 1 - (1 - CHAR.dessus) * u,
      dessous: CHAR.dessous * (1 - u) * (1 - u),
      echelle: 1 - CHAR.echelle * u,
      glisse: CHAR.glisse * u,
      ombre: Math.max(0, 1 - u / CHAR.ombre),
    };
  }

  /** Le toit du char qui coule, a la place de son dessin de tous les jours. `toit` : son image
      cuite, centree sur (`x`, `y`) a l'ecran. Le cavalier (`cavalier` : { canvas, x, y } a l'ecran,
      ou null) palit avec sa machine. */
  function dessinerChar(ctx, v, e, toit, x, y, cavalier) {
    const ca = Math.cos(v.angle), sa = Math.sin(v.angle), k = profondeur();
    // Les axes du char A L'ECRAN : le long (`ax`, `ay`) et le travers (`nx`, `ny`), le sol vu de biais.
    const ax = ca, ay = sa * k, nx = -sa, ny = ca * k;
    const ox = x + ax * e.glisse, oy = y + ay * e.glisse, R = toit.width, demi = v.def.longueur / 2;
    // ⚠️ La ligne court sur toute l'IMAGE, pas sur la longueur du char : le dessin deborde la
    // caisse (le pare-chocs, la hauteur vue de biais), et un coin de l'arriere restait hors de
    // l'eau, net et sombre, quand le reste avait coule (vu a la capture).
    const s = e.echelle, l = e.ligne * (demi + BORD) / demi * s, dessousTout = e.ligne <= -demi;
    const moitie = function (de, a, alpha) {
      if (alpha <= 0.01 || a <= de) return;
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(ox + ax * de - nx * R, oy + ay * de - ny * R);
      ctx.lineTo(ox + ax * a - nx * R, oy + ay * a - ny * R);
      ctx.lineTo(ox + ax * a + nx * R, oy + ay * a + ny * R);
      ctx.lineTo(ox + ax * de + nx * R, oy + ay * de + ny * R);
      ctx.closePath();
      ctx.clip();
      ctx.globalAlpha = alpha;
      ctx.drawImage(toit, Math.round(ox - toit.width * s / 2), Math.round(oy - toit.height * s / 2),
                    Math.round(toit.width * s), Math.round(toit.height * s));
      ctx.restore();
      B.stats.images++;
    };
    if (dessousTout) moitie(-R, R, e.dessous);   // tout entier sous l'eau
    else {
      moitie(l, R, e.dessous);          // devant la ligne : sous l'eau
      moitie(-R, l, e.dessus);          // derriere : hors de l'eau, pour l'instant
    }
    if (cavalier) {
      ctx.save();
      ctx.globalAlpha = dessousTout ? e.dessous : e.dessus;
      ctx.drawImage(cavalier.canvas, Math.round(cavalier.x + ax * e.glisse), Math.round(cavalier.y + ay * e.glisse));
      ctx.restore();
      B.stats.images++;
    }
    // L'ecume sur la ligne de flottaison, en travers de la caisse : des points qui frissonnent.
    // ⚠️ Pas un trait : un trait blanc continu se lisait comme une rayure sur la tole.
    if (!dessousTout) {
      const demiL = Math.ceil(v.def.largeur / 2 * s) + 2, tic = Math.floor((B.t || 0) / 5);
      ctx.fillStyle = 'rgba(' + ECUME + ',0.85)';
      for (let i = -demiL; i <= demiL; i++) {
        if (empreinte(v.id * 64 + i, tic) < 0.4) continue;
        const d = empreinte(i, tic + 7) < 0.3 ? 1 : 0;       // une goutte deborde, un pixel devant
        ctx.fillRect(Math.round(ox + ax * (l + d) + nx * i), Math.round(oy + ay * (l + d) + ny * i), 1, 1);
      }
      B.stats.rects += 2 * demiL + 1;
    }
    // Les ronds autour de la coque : un toutes les 20 images, qui s'elargit et palit.
    const rayon = v.def.longueur / 2 * s;
    for (let i = 0; i < 2; i++) {
      const f = (((B.t || 0) + i * 10 + v.id * 7) % 20) / 20;
      anneau(ctx, x, y, rayon + 1 + f * 7, k, 0.45 * (1 - f) * (1 - e.u * 0.5));
    }
  }

  function anneau(ctx, x, y, r, k, alpha) {
    if (alpha <= 0.01) return;
    ctx.strokeStyle = 'rgba(' + ECUME + ',' + alpha.toFixed(3) + ')';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.ellipse(x, y, r, Math.max(1, r * k), 0, 0, Math.PI * 2);
    ctx.stroke();
  }

  function tache(ctx, x, y, rx, ry, rgb, alpha) {
    ctx.fillStyle = 'rgba(' + rgb + ',' + alpha.toFixed(3) + ')';
    ctx.beginPath();
    ctx.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  /** Au fond : la trace du naufrage, la ou il a coule. */
  function poser(v) {
    if (coupe || !v || !v.def) return;
    traces.push({ x: v.x, y: v.y, t: B.t || 0, id: v.id | 0, longueur: v.def.longueur, largeur: v.def.largeur });
    if (traces.length > 12) traces.shift();
  }

  /** Les traces de naufrage a l'ecran, sur l'eau et sous les gens. Rend combien on en a dessine. */
  function dessinerSol(ctx, cam) {
    const t = B.t || 0;
    while (traces.length && t - traces[0].t > DUREE) traces.shift();
    if (coupe || B.interieur || !traces.length) return 0;
    const cx = Math.round(cam.x), cy = Math.round(cam.y), k = profondeur();
    let n = 0;
    for (const tr of traces) {
      const x = tr.x - cx, y = tr.y - cy, age = t - tr.t, L = tr.longueur;
      if (x < -L * 2 || y < -L * 2 || x > VW + L * 2 || y > VH + L * 2) continue;
      n++;
      // La tache d'huile : quatre reflets qui s'etalent, puis palissent.
      const vie = Math.min(1, age / 30) * Math.min(1, (DUREE - age) / FOND.palit);
      const etale = 0.55 + 0.45 * Math.min(1, age / FOND.etale);
      for (let i = 0; i < IRISE.length; i++) {
        const a = empreinte(tr.id, i) * Math.PI * 2, d = L * 0.18 * empreinte(tr.id, i + 8);
        const r = L * 0.42 * etale * (0.7 + 0.5 * empreinte(tr.id, i + 16));
        tache(ctx, x + Math.cos(a) * d, y + Math.sin(a) * d * k, r, r * k * 0.8, IRISE[i], 0.24 * vie);
      }
      // Le reflet de l'huile : un liseré clair sur le bord de la nappe.
      ctx.strokeStyle = 'rgba(255,255,255,' + (0.14 * vie).toFixed(3) + ')';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(x, y, L * 0.4 * etale, L * 0.4 * etale * k * 0.8, 0, Math.PI * 1.1, Math.PI * 1.7);
      ctx.stroke();
      // Les cercles qui s'elargissent.
      for (let i = 0; i < FOND.anneaux; i++) {
        const f = (age - i * FOND.ecart) / FOND.anneau;
        if (f >= 0 && f < 1) anneau(ctx, x, y, 4 + f * L * 0.9, k, 0.6 * (1 - f));
      }
      // La grosse bulle : elle gonfle, puis creve en gouttes.
      if (age < FOND.bulle) {
        const r = 2 + 5 * (age / FOND.bulle) * (L / 30);
        tache(ctx, x, y - r * 0.4, r, r * 0.9, ECUME, 0.35);
        anneau(ctx, x, y - r * 0.4, r, 0.9, 0.9);
      } else if (age < FOND.bulle + FOND.gouttes) {
        const f = (age - FOND.bulle) / FOND.gouttes;
        ctx.fillStyle = 'rgba(' + ECUME + ',' + (0.9 * (1 - f)).toFixed(2) + ')';
        for (let i = 0; i < 7; i++) {
          const a = (i / 7 + empreinte(tr.id, 30)) * Math.PI * 2, d = 3 + f * 9;
          ctx.fillRect(Math.round(x + Math.cos(a) * d), Math.round(y + Math.sin(a) * d * k - 2 - f * 3), 1, 1);
        }
        B.stats.rects += 7;
      }
      // Une bulle remonte de temps en temps dans la tache, tant qu'elle est fraiche.
      const cycle = Math.floor(age / FOND.remonte), dans = age % FOND.remonte;
      if (age > FOND.bulle + FOND.gouttes && age < DUREE * FOND.remonte_fin && dans < 12) {
        const a = empreinte(tr.id, 40 + cycle) * Math.PI * 2, d = L * 0.3 * empreinte(tr.id, 60 + cycle);
        const bx = x + Math.cos(a) * d, by = y + Math.sin(a) * d * k;
        anneau(ctx, bx, by, 1 + dans / 6, 0.9, 0.8 * (1 - dans / 12));
      }
    }
    return n;
  }

  return { etat, dessinerChar, poser, dessinerSol, traces: function () { return traces; }, oublier, couper, DUREE };
})();
