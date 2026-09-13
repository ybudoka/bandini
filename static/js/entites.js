/* Bandini — entites : une structure, un tableau, un tri par y.

   (x, y) est le point de contact au sol (les pieds). `r` est le rayon du
   cercle au sol pour les collisions. `z` est la hauteur (sauts, rampes) : y
   de tri = y, y de dessin = y - z. */

const Entites = (function () {
  'use strict';

  let suivantId = 1;

  function creer(type, x, y, extra) {
    const e = {
      id: suivantId++, type: type, x: x, y: y, vx: 0, vy: 0, r: 5, z: 0, vz: 0,
      angle: 0, face: 'bas', etat: 'flane', t: 0,
      vie: 100, vieMax: 100, vivant: true,
      sprite: null, swaps: null, anim: { i: 0, dist: 0 },
      actif: true, dessine: true, solide: false,
    };
    if (extra) Object.assign(e, extra);
    B.entites.push(e);
    return e;
  }

  function retirer(e) {
    const i = B.entites.indexOf(e);
    if (i >= 0) B.entites.splice(i, 1);
  }

  function vider() { B.entites.length = 0; B.joueur = null; }

  function creerJoueur(x, y) {
    const p = B.partie;
    const tenue = (B.defs.tenues || []).find(function (t) { return t.slug === p.tenue; });
    const j = creer('joueur', x, y, {
      r: 5, sprite: 'joueur', swaps: tenue ? { c: tenue.couleur } : null,
      vie: p.vie, vieMax: 100, endurance: 100, arme: p.arme || 'poings',
      dansVehicule: null, invincible: 0, flagrant: 0, pasDist: 0,
    });
    B.joueur = j;
    return j;
  }

  function creerDecor(def) {
    (def.decor || []).forEach(function (d) {
      const fiche = DECORS[d.type] || {};
      creer('decor', d.x * TT + 8, d.y * TT + 15, {
        decor: d.type, r: fiche.r === undefined ? 3 : fiche.r, solide: !!fiche.solide,
      });
    });
  }

  // --- Deplacement avec collisions --------------------------------------------------

  /** Deplace un cercle (approche par boite) contre les tuiles, axe par axe. */
  function deplacerCercle(e, dx, dy, masque) {
    const r = e.r;
    if (dx !== 0) {
      e.x += dx;
      const ty0 = Math.floor((e.y - r) / TT), ty1 = Math.floor((e.y + r - 0.01) / TT);
      if (dx > 0) {
        const tx = Math.floor((e.x + r) / TT);
        for (let ty = ty0; ty <= ty1; ty++) if (Monde.bloque(tx, ty, masque)) { e.x = tx * TT - r - 0.01; break; }
      } else {
        const tx = Math.floor((e.x - r) / TT);
        for (let ty = ty0; ty <= ty1; ty++) if (Monde.bloque(tx, ty, masque)) { e.x = (tx + 1) * TT + r + 0.01; break; }
      }
    }
    if (dy !== 0) {
      e.y += dy;
      const tx0 = Math.floor((e.x - e.r) / TT), tx1 = Math.floor((e.x + e.r - 0.01) / TT);
      if (dy > 0) {
        const ty = Math.floor((e.y + r) / TT);
        for (let tx = tx0; tx <= tx1; tx++) if (Monde.bloque(tx, ty, masque)) { e.y = ty * TT - r - 0.01; break; }
      } else {
        const ty = Math.floor((e.y - r) / TT);
        for (let tx = tx0; tx <= tx1; tx++) if (Monde.bloque(tx, ty, masque)) { e.y = (ty + 1) * TT + r + 0.01; break; }
      }
    }
    bloquerParDecor(e);
  }

  function bloquerParDecor(e) {
    for (const d of B.entites) {
      if (!d.solide || d === e) continue;
      const dx = e.x - d.x, dy = e.y - d.y;
      const min = e.r + d.r;
      const d2 = dx * dx + dy * dy;
      if (d2 >= min * min || d2 === 0) continue;
      const dist = Math.sqrt(d2);
      e.x = d.x + dx / dist * min; e.y = d.y + dy / dist * min;
    }
  }

  function dansLaCarte(e) {
    const c = Monde.carte;
    e.x = borner(e.x, e.r, c.pxW - e.r); e.y = borner(e.y, e.r, c.pxH - e.r);
  }

  // --- Joueur ---------------------------------------------------------------------------

  function majJoueur(j) {
    if (j.dansVehicule) return;
    const v = B.defs.recherche.vitesses;
    const axe = Entree.axe;
    const veutCourir = Entree.bas('esquive') || (axe.source !== 'clavier' && axe.mag > 0.85);
    let vitesse = v.joueur_marche;
    if (veutCourir && axe.mag > 0 && j.endurance > 0) {
      vitesse = v.joueur_sprint;
      j.endurance = Math.max(0, j.endurance - v.endurance_par_image);
    } else {
      j.endurance = Math.min(v.endurance, j.endurance + v.endurance_par_image * 0.6);
    }
    const mag = axe.source === 'clavier' ? axe.mag : Math.min(1, axe.mag * 1.15);
    j.vx = axe.x * vitesse * mag; j.vy = axe.y * vitesse * mag;
    if (axe.mag > 0) {
      j.angle = Math.atan2(axe.y, axe.x);
      j.face = Math.abs(axe.x) >= Math.abs(axe.y) ? (axe.x > 0 ? 'droite' : 'gauche') : (axe.y > 0 ? 'bas' : 'haut');
    }
    const avant = { x: j.x, y: j.y };
    deplacerCercle(j, j.vx, j.vy, Monde.MASQUE_PIETON);
    dansLaCarte(j);
    const d = Math.hypot(j.x - avant.x, j.y - avant.y);
    j.anim.dist += d;
    j.pasDist += d;
    if (j.pasDist > 14) { j.pasDist = 0; Son.SFX.pas(); }
    if (j.invincible > 0) j.invincible--;
    if (j.flagrant > 0) j.flagrant--;
  }

  function maj() {
    for (let i = 0; i < B.entites.length; i++) {
      const e = B.entites[i];
      if (!e.actif) continue;
      e.t++;
      if (e.type === 'joueur') majJoueur(e);
    }
  }

  // --- Dessin ------------------------------------------------------------------------------

  function imageDe(e) {
    const def = SPRITES[e.sprite];
    if (!def) return null;
    const cuit = Atlas.cuire(e.sprite, def, e.swaps);
    const poses = cuit.poses[e.face] || cuit.poses.bas;
    const bouge = Math.abs(e.vx) + Math.abs(e.vy) > 0.05;
    const i = bouge ? [0, 1, 0, 2][Math.floor(e.anim.dist / 7) % 4] : 0;
    return { canvas: poses[Math.min(i, poses.length - 1)], ancre: cuit.ancre };
  }

  function dessiner(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    const visibles = [];
    for (const e of B.entites) {
      if (!e.dessine) continue;
      if (e.x < cx - 40 || e.x > cx + VW + 40 || e.y < cy - 48 || e.y > cy + VH + 48) continue;
      visibles.push(e);
    }
    visibles.sort(function (a, b) { return a.y - b.y || a.id - b.id; });
    B.stats.entites = visibles.length;
    const ombre = Atlas.cuirePeintre('ombre', DECORS.ombre.w, DECORS.ombre.h, DECORS.ombre.peindre);
    for (const e of visibles) {
      if (e.type === 'decor') {
        const d = DECORS[e.decor];
        if (!d) continue;
        const c = Atlas.cuirePeintre('decor|' + e.decor, d.w, d.h, d.peindre);
        ctx.drawImage(c, Math.round(e.x - d.ancre[0] - cx), Math.round(e.y - d.ancre[1] - cy));
        B.stats.images++;
        continue;
      }
      const img = imageDe(e);
      if (!img) continue;
      ctx.drawImage(ombre, Math.round(e.x - 6 - cx), Math.round(e.y - 3 - cy));
      if (e.invincible > 0 && (e.invincible >> 2) % 2 === 0) continue;
      ctx.drawImage(img.canvas, Math.round(e.x - img.ancre[0] - cx), Math.round(e.y - e.z - img.ancre[1] - cy));
      B.stats.images += 2;
    }
  }

  return { creer, retirer, vider, creerJoueur, creerDecor, deplacerCercle, majJoueur, maj, dessiner, imageDe };
})();
