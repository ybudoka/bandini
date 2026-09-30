/* Bandini — la patinoire du parc (docs/jalons/la-patinoire-du-parc.md).

   L'hiver, tant que la neige tient (`Saisons.enHiver`), le parc du Faubourg a sa patinoire a bandes : la
   glace, des bandes blanches a liseret rouge, deux filets, et quatre lampadaires qui s'allument le soir.
   L'ete, sa clairiere n'est que du gazon. Sa PLACE vient de Python (`app/patinoire.py`, dans la carte :
   `B.defs.carte.patinoire`, en tuiles) ; ses couleurs, sa glisse et sa chute de sa fiche (`B.defs.patinoire`).

   ⚠️ TOUT EST PEINT, RIEN N'EST POSE : aucune tuile, aucun decor, aucun identifiant, aucun de. Mais les
   bandes sont SOLIDES l'hiver, comme les Tempo (`RueDesSaisons`) : un char n'entre pas (`bloqueChar`, lu
   par `Monde.barriereBloque`), un pieton passe par les portes (`bloquer`, lu par `Entites.bloquerParDecor`).

   ⚠️ LA GLISSE : sur la glace, la vitesse que veulent les commandes (ou la tete d'un passant) ne se prend
   pas d'un coup — elle se rejoint peu a peu (`glisser`, appele par `Entites` une fois la vitesse voulue
   calculee). D'ou l'elan, le virage large, l'arret qui prend du temps. Et le joueur qui court sans patins,
   ou qui vire sec lance, TOMBE (`auSol`) — sans un de. */

const Patinoire = (function () {
  'use strict';

  const T = 16;
  //: L'epaisseur d'une bande, en px, et son retrait dans la tuile du bord.
  const BANDE = 3, RETRAIT = 2;

  function fiche() { return B.defs && B.defs.patinoire; }
  function lieu() { return B.defs && B.defs.carte && B.defs.carte.patinoire; }

  /** La patinoire en px, et ses bandes (des boites { x, y, l, h } en demi-tailles), calculees une fois par
      lieu : la carte ne bouge pas. */
  let calcul = null, deQui = null;
  function geo() {
    const p = lieu();
    if (!p) return null;
    if (calcul && deQui === p) return calcul;
    const x0 = p.x * T + RETRAIT, y0 = p.y * T + RETRAIT;
    const x1 = (p.x + p.l) * T - RETRAIT, y1 = (p.y + p.h) * T - RETRAIT;
    const portes = p.portes || [];
    const bandes = [];
    // Une bande par cote, coupee a chaque porte : l'ouverture fait la tuile de la porte.
    const cote = function (nom, horizontale, fixe, a, b) {
      const trous = portes.filter(function (q) { return q.cote === nom; })
        .map(function (q) { return horizontale ? [q.x * T, (q.x + 1) * T] : [q.y * T, (q.y + 1) * T]; })
        .sort(function (u, w) { return u[0] - w[0]; });
      let debut = a;
      trous.concat([[b, b]]).forEach(function (t) {
        const fin = Math.min(b, t[0]);
        if (fin - debut > 0.5) {
          const m = (debut + fin) / 2, demi = (fin - debut) / 2;
          bandes.push(horizontale ? { x: m, y: fixe, l: demi, h: BANDE / 2, cote: nom }
                                  : { x: fixe, y: m, l: BANDE / 2, h: demi, cote: nom });
        }
        debut = Math.max(debut, t[1]);
      });
    };
    cote('nord', true, y0 + BANDE / 2, x0, x1);
    cote('sud', true, y1 - BANDE / 2, x0, x1);
    cote('ouest', false, x0 + BANDE / 2, y0, y1);
    cote('est', false, x1 - BANDE / 2, y0, y1);
    calcul = { p: p, x0: x0, y0: y0, x1: x1, y1: y1, bandes: bandes, portes: portes };
    deQui = p;
    return calcul;
  }

  /** Dehors, dans la ville, et la neige tient : la glace est la. */
  function ouverte() {
    const c = Monde.carte;
    // ⚠️ `fiche()` : elle voyage dans la SUITE du paquet (`/api/suite`), qui arrive juste apres la ville.
    return !!(c && c.laVille && !B.interieur && !B.bloc && fiche() && typeof Saisons !== 'undefined' && Saisons.enHiver() && geo());
  }

  /** Ce point (px) est-il SUR la glace (en dedans des bandes) ? */
  function surLaGlace(x, y) {
    if (!ouverte()) return false;
    const g = geo();
    return x > g.x0 + BANDE && x < g.x1 - BANDE && y > g.y0 + BANDE && y < g.y1 - BANDE;
  }

  // ------------------------------------------------------------------ les bandes, solides

  /** Un pieton ou le joueur a pied qui entre dans une bande en ressort par le cote le moins enfonce ; son
      elan contre la bande s'arrete (on ne glisse pas a travers). Appele par `Entites.bloquerParDecor`. */
  function bloquer(e) {
    if (!e || (e.type !== 'pieton' && e.type !== 'joueur') || e.dansVehicule || !ouverte()) return;
    const g = geo();
    if (e.x < g.x0 - e.r - 2 || e.x > g.x1 + e.r + 2 || e.y < g.y0 - e.r - 2 || e.y > g.y1 + e.r + 2) return;
    for (const b of g.bandes) {
      const dx = e.x - b.x, dy = e.y - b.y;
      const px = b.l + e.r - Math.abs(dx), py = b.h + e.r - Math.abs(dy);
      if (px <= 0 || py <= 0) continue;
      if (px < py) { e.x = b.x + (dx < 0 ? -1 : 1) * (b.l + e.r + 0.01); e.gx = 0; }
      else { e.y = b.y + (dy < 0 ? -1 : 1) * (b.h + e.r + 0.01); e.gy = 0; }
    }
  }

  /** Un char `v` peut-il entrer sur la tuile (tx, ty) ? Non, l'hiver, si elle est dans la patinoire — sauf
      pour le char qui s'y trouve deja (il en sort librement). Appele par `Monde.barriereBloque`. */
  function bloqueChar(v, tx, ty) {
    if (!v || v.type !== 'vehicule') return false;
    const p = lieu();
    if (!p || tx < p.x || tx >= p.x + p.l || ty < p.y || ty >= p.y + p.h || !ouverte()) return false;
    const vx = Math.floor(v.x / T), vy = Math.floor(v.y / T);
    return !(vx >= p.x && vx < p.x + p.l && vy >= p.y && vy < p.y + p.h);
  }

  // ------------------------------------------------------------------ la glisse, et la chute

  function tomber(j, f) {
    j.auSol = f.images_au_sol; j.face = 'couche';
    j.vx = 0; j.vy = 0; j.gx = 0; j.gy = 0; j.courseSurGlace = 0;
    if (typeof Son !== 'undefined' && Son.SFX && Son.SFX.chute) Son.SFX.chute();
  }

  /** Sur la glace, la vitesse voulue (`e.vx`, `e.vy`, deja calculee) se rejoint peu a peu depuis celle de
      l'image d'avant (`e.gx`, `e.gy`). `court` : le joueur tient ESQUIVE en poussant. Rend vrai si le joueur
      vient de tomber (il ne bouge plus cette image-ci). Hors de la glace, on retient seulement la vitesse :
      on y entre avec son elan. */
  function glisser(e, court) {
    const f = fiche();
    const suite = e.gt === B.t - 1;
    e.gt = B.t;
    if (!f || !surLaGlace(e.x, e.y)) { e.gx = e.vx; e.gy = e.vy; e.courseSurGlace = 0; return false; }
    const g = f.glisse[e.type === 'joueur' ? 'joueur' : 'pieton'];
    // ⚠️ Une suite rompue (la premiere image, un retour anticipe d'`Entites` qui a remis la vitesse a zero) repart
    // de l'ARRET, jamais de la vitesse voulue : sinon on demarre sur la glace aussi vite qu'au sec.
    const avx = suite ? (e.gx || 0) : 0, avy = suite ? (e.gy || 0) : 0;
    const pousse = Math.abs(e.vx) + Math.abs(e.vy) > 0.01;
    if (e.type === 'joueur') {
      const c = f.chute, va = Math.hypot(avx, avy), vv = Math.hypot(e.vx, e.vy);
      e.courseSurGlace = court ? (e.courseSurGlace || 0) + 1 : 0;
      let virage = 0;
      if (pousse && va > 0.01 && vv > 0.01) {
        const cos = (avx * e.vx + avy * e.vy) / (va * vv);
        virage = Math.acos(Math.max(-1, Math.min(1, cos))) * 180 / Math.PI;
      }
      if (e.courseSurGlace > c.images_de_course || (virage > c.virage_deg && va > c.vitesse_de_virage)) {
        tomber(e, c);
        return true;
      }
    }
    const k = pousse ? g.elan : g.freinage;
    e.vx = avx + (e.vx - avx) * k;
    e.vy = avy + (e.vy - avy) * k;
    e.gx = e.vx; e.gy = e.vy;
    return false;
  }

  // ------------------------------------------------------------------ la peinture

  /** La glace, les bandes, les filets et les lampadaires, sous les gens. Rien l'ete. */
  function dessinerSol(ctx, vue) {
    if (!ouverte()) return;
    const g = geo(), c = fiche().couleurs;
    const X = function (x) { return Math.round(x - vue.x); }, Y = function (y) { return Math.round(y - vue.y); };
    if (X(g.x1) < -24 || X(g.x0) > VW + 24 || Y(g.y1) < -24 || Y(g.y0) > VH + 24) return;
    const l = g.x1 - g.x0, h = g.y1 - g.y0;
    let n = 0;
    // La glace, et ses rayures de lames : a l'empreinte de la patinoire, jamais un de.
    ctx.fillStyle = c.glace; ctx.fillRect(X(g.x0), Y(g.y0), l, h); n++;
    ctx.fillStyle = c.rayure;
    for (let k = 0; k < 18; k++) {
      const hh = hash2(g.p.x * 31 + k, g.p.y * 17 + k) >>> 0;
      const rx = g.x0 + 6 + (hh % Math.max(1, l - 30)), ry = g.y0 + 6 + ((hh >>> 8) % Math.max(1, h - 12));
      ctx.fillRect(X(rx), Y(ry), 8 + ((hh >>> 16) % 14), 1); n++;
    }
    ctx.fillStyle = c.reflet;
    ctx.fillRect(X(g.x0 + 10), Y(g.y0 + 6), Math.round(l * 0.3), 1); ctx.fillRect(X(g.x0 + l * 0.55), Y(g.y1 - 9), Math.round(l * 0.25), 1); n += 2;
    // La ligne rouge du centre.
    ctx.fillStyle = c.liseret; ctx.globalAlpha = 0.45;
    ctx.fillRect(X(g.x0 + l / 2) - 1, Y(g.y0 + BANDE), 2, h - 2 * BANDE); n++;
    ctx.globalAlpha = 1;
    // Les filets, au milieu des petits cotes.
    const my = (g.y0 + g.y1) / 2, FILET = 7;
    [[g.x0 + BANDE + 6, -1], [g.x1 - BANDE - 6, 1]].forEach(function (f) {
      ctx.fillStyle = c.filet; ctx.fillRect(X(f[0]) + (f[1] > 0 ? 0 : -3), Y(my - FILET), 3, FILET * 2);
      ctx.fillStyle = c.poteau; ctx.fillRect(X(f[0]) - 1, Y(my - FILET) - 1, 2, 2); ctx.fillRect(X(f[0]) - 1, Y(my + FILET) - 1, 2, 2);
      n += 3;
    });
    // Les bandes : une ombre sous chacune, le blanc, le liseret rouge en haut.
    for (const b of g.bandes) {
      const bx = X(b.x - b.l), by = Y(b.y - b.h), bl = Math.round(b.l * 2), bh = Math.round(b.h * 2);
      ctx.fillStyle = c.ombre; ctx.fillRect(bx, by + 1, bl, bh);
      ctx.fillStyle = c.bande; ctx.fillRect(bx, by, bl, bh);
      ctx.fillStyle = c.liseret;
      if (b.cote === 'nord' || b.cote === 'sud') ctx.fillRect(bx, by, bl, 1); else ctx.fillRect(bx + (b.cote === 'ouest' ? 0 : bl - 1), by, 1, bh);
      n += 3;
    }
    // Les lampadaires des quatre coins.
    for (const q of coins(g)) {
      ctx.fillStyle = c.lampe; ctx.fillRect(X(q[0]) - 1, Y(q[1]) - 9, 2, 10); ctx.fillRect(X(q[0]) - 2, Y(q[1]) - 10, 4, 2);
      n += 2;
    }
    B.stats.rects += n;
  }

  function coins(g) { return [[g.x0 - 3, g.y0 - 2], [g.x1 + 3, g.y0 - 2], [g.x0 - 3, g.y1 + 2], [g.x1 + 3, g.y1 + 2]]; }

  /** La lueur des lampadaires, le soir. */
  function lampes(vue) {
    if (!ouverte() || Monde.ambianceVue().alpha <= 0.2) return [];
    const g = geo(), f = fiche().lampes, coul = 'rgba(' + f.lueur.join(',') + ',' + f.force + ')', out = [];
    for (const q of coins(g)) {
      const x = q[0] - vue.x, y = q[1] - 9 - vue.y;
      if (x < -f.rayon || y < -f.rayon || x > VW + f.rayon || y > VH + f.rayon) continue;
      out.push({ x: x, y: y, r: f.rayon, c: coul });
    }
    return out;
  }

  return { geo, ouverte, surLaGlace, bloquer, bloqueChar, glisser, dessinerSol, lampes };
})();
