/* Bandini — le Petit-Canton, ce qui passe AU-DESSUS des gens (docs/jalons/le-quartier-chinois.md, etape 2,
   vague B) : le toit de l'arche et les cordes de lanternes, tendues en travers de la rue principale.

   ⚠️ PAS DU DECOR : un decor est un sprite trie a son pied, et on passerait DEVANT un toit tendu au-dessus de
   la rue. Ceci se peint apres les entites (`Jeu.rendre`), comme la fumee des cheminees. Les deux piliers de
   l'arche, eux, sont du decor (`pilier_arche`, solide) : c'est sur eux que le toit se pose.

   ⚠️ AUCUN DE, et rien qui bouge a part le balancement des lanternes (d'apres `B.t`). ⚠️ Et seulement EN
   VILLE : dans un bloc, `Monde.carte` est le bloc, et il n'a ni arche ni lanternes. */

const Canton = (function () {
  'use strict';

  function donnees() {
    if (B.interieur || B.bloc || !Monde.carte || !Monde.carte.def) return null;
    return Monde.carte.def.canton || null;
  }

  //: Le rouge laque des piliers et du linteau, l'or du panneau, le vert des tuiles vernissees du toit.
  const ARCHE = { tuile: '#2f7a4a', tuileClaire: '#4fa56a', tuileSombre: '#1f5534', linteau: '#a3201c',
                  or: '#e0b040', lettres: '#f2cc5a', ombre: 'rgba(0,0,0,0.30)' };
  //: La hauteur du toit au-dessus du trottoir (le haut des piliers, `pilier_arche` fait 30 px).
  const HAUT = 30;

  /** Le toit de l'arche, pose sur ses deux piliers : un linteau rouge, un panneau d'or a deux ideogrammes
      (`devantures.IDEOGRAMMES`), et un toit de tuiles vertes aux coins releves. */
  function arche(ctx, a, cam) {
    const x = a.x * TT - cam.x - 10, y = (a.y + 1) * TT - HAUT - cam.y;
    const large = a.l * TT + 20;
    if (x > VW + 20 || x + large < -20 || y > VH + 20 || y + 40 < -20) return;
    ctx.fillStyle = ARCHE.ombre;                                      // son ombre sur la chaussee
    ctx.fillRect(x + 6, y + HAUT + 4, large - 8, 4);
    ctx.fillStyle = ARCHE.linteau;                                   // le linteau
    ctx.fillRect(x + 6, y + 8, large - 12, 5);
    ctx.fillStyle = ARCHE.tuileSombre;                               // le toit : son egout,
    ctx.fillRect(x, y + 4, large, 4);
    ctx.fillStyle = ARCHE.tuile;                                     // ses tuiles,
    ctx.fillRect(x + 3, y, large - 6, 5);
    ctx.fillStyle = ARCHE.tuileClaire;                               // son faitage,
    ctx.fillRect(x + 6, y, large - 12, 1);
    ctx.fillRect(x, y + 3, 3, 2); ctx.fillRect(x + large - 3, y + 3, 3, 2);   // et ses coins releves
    ctx.fillRect(x - 1, y + 2, 2, 2); ctx.fillRect(x + large - 1, y + 2, 2, 2);
    const table = d0().ideogrammes;
    if (!table) return;
    const paire = table.paires[(a.paire || 0) % table.paires.length];
    const px = Math.round(x + large / 2 - 8), py = y + 7;              // le panneau, au milieu du linteau
    ctx.fillStyle = ARCHE.or;
    ctx.fillRect(px, py, 16, 9);
    ctx.fillStyle = ARCHE.linteau;
    ctx.fillRect(px + 1, py + 1, 14, 7);
    ctx.fillStyle = ARCHE.lettres;
    Array.from(paire).forEach(function (car, k) {
      const rangs = table.glyphes[car] || [];
      for (let j = 0; j < rangs.length; j++) {
        for (let i = 0; i < rangs[j].length; i++) {
          if (rangs[j][i] === '#') ctx.fillRect(px + 2 + k * 7 + i, py + 2 + j, 1, 1);
        }
      }
    });
    B.stats.rects += 12;
  }

  //: Les lanternes : rouges, un capuchon d'or, une corde sombre qui ploie un peu au milieu.
  const LANTERNE = { corde: '#2a2020', rouge: '#c8281e', clair: '#ff6a4a', or: '#e0b040' };
  const AU_DESSUS = 22;                                                // la corde, au-dessus du trottoir

  function cordee(ctx, c, cam) {
    const x0 = c.x * TT + 8 - cam.x, x1 = (c.x + c.l - 1) * TT + 8 - cam.x;
    const y = c.y * TT + 8 - AU_DESSUS - cam.y;
    if (x0 > VW + 20 || x1 < -20 || y > VH + 30 || y < -30) return;
    const n = c.l + 1;
    ctx.fillStyle = LANTERNE.corde;
    for (let i = 0; i <= x1 - x0; i++) {
      const t = i / Math.max(1, x1 - x0);
      ctx.fillRect(x0 + i, Math.round(y + 4 * t * (1 - t) * 4), 1, 1);   // elle ploie de quatre pixels
    }
    for (let k = 1; k < n; k++) {
      const t = k / n, lx = Math.round(x0 + (x1 - x0) * t);
      const ly = Math.round(y + 16 * t * (1 - t)) + 1;
      const balance = Math.round(Math.sin(((B.t || 0) + k * 23 + c.y * 7) / 40));   // le vent, sans de
      ctx.fillStyle = LANTERNE.or;
      ctx.fillRect(lx - 1 + balance, ly, 3, 1);
      ctx.fillStyle = LANTERNE.rouge;
      ctx.fillRect(lx - 2 + balance, ly + 1, 5, 4);
      ctx.fillStyle = LANTERNE.clair;
      ctx.fillRect(lx - 1 + balance, ly + 2, 1, 2);
      ctx.fillStyle = LANTERNE.or;
      ctx.fillRect(lx - 1 + balance, ly + 5, 3, 1);
    }
    B.stats.rects += 4 * n;
  }

  /** Au-dessus des entites (`Jeu.rendre`). */
  function d0() { return donnees() || {}; }

  function dessiner(ctx, cam) {
    const d = donnees();
    if (!d) return;
    (d.lanternes || []).forEach(function (c) { cordee(ctx, c, cam); });
    (d.arches || []).forEach(function (a) { arche(ctx, a, cam); });
  }

  return { dessiner: dessiner, donnees: donnees };
})();

