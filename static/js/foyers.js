/* Bandini — les foyers de l'hiver (docs/jalons/la-foire-fermee-l-hiver.md, vague 3 ; `app/foyers.py`).

   Martin (30 sept. 2026) : l'hiver ferme la foire, les amuseurs et la fontaine — « à la place : jongleur
   de feu, des foyers centraux et des vendeurs de chocolat chaud ». Tant que la neige tient
   (`Saisons.enHiver`), chaque place publique allume un brasero de part et d'autre de sa fontaine à sec,
   et une roulotte de chocolat chaud se tient juste au sud. Des passants s'arrêtent s'y chauffer les
   mains (`Entites.majLesFoyers`) ; le joueur debout près du feu reprend son souffle plus vite ; ACTION
   devant la roulotte, une tasse (`Missions.acheterAmbulant`, le commerce `chocolat`).

   ⚠️ RIEN NE NAÎT : braseros et roulottes se PEIGNENT (`ajouterVisibles`, triés avec les gens comme les
   jets des bornes-fontaines) et ARRÊTENT le pas (`bloquer`) — aucune entité, aucun dé, aucun numéro
   décalé. Leurs places se lisent sur la carte finie : la fontaine de chaque place publique, et la
   première tuile libre d'une liste écrite à la main (`foyers.BRASERO_ESSAIS`). */

const Foyers = (function () {
  'use strict';

  //: Un numéro de tri hors de portée des entités, de la foire (900000000) et de la cabane.
  const ID_TRI = 910000000;
  //: La lueur d'un brasero, la couleur du baril du bidonville (`Monde`, `SORTES_DE_LAMPE.feu`).
  const LUEUR = 'rgba(255,140,50,0.58)';
  //: La lueur d'un jongleur de feu, plus petite : trois torches, pas un feu.
  const LUEUR_JONGLEUR = 'rgba(255,170,70,0.45)';

  function regles() { return (B.defs && B.defs.foyers) || null; }
  function allumes() { return !!regles() && typeof Saisons !== 'undefined' && Saisons.enHiver() && !B.interieur && !B.bloc; }

  // --- Les places ------------------------------------------------------------------------------

  let memo = null, memoDef = null;

  /** Les places publiques, lues une fois par carte : { fontaine, braseros: [{ x, y }], roulotte: { x, y } }.
      ⚠️ SANS DÉ : la fontaine est au centre de la place (`carte._place`), et chaque brasero prend la
      première tuile libre de sa liste — du pavé où l'on marche, hors de la rue et du pas d'une porte, à
      distance de tout décor posé (un banc, un arbre, le lampadaire). */
  function places() {
    const c = Monde.carte, def = c && c.def, r = regles();
    if (!def || !r) return [];
    if (memoDef === def) return memo;
    const decor = (def.decor || []).map(function (d) { return { x: d.x * TT + 8, y: d.y * TT + 15 }; });
    const pris = [];
    //: ⚠️ LA HAUTEUR DU DESSIN COMPTE, pas seulement la tuile du pied : la roulotte monte de deux tuiles, et
    //: posee sous un banc elle le couvrait (la capture du 30 sept. 2026). `haut` : jusqu'ou il monte, en px.
    function libre(tx, ty, haut) {
      if (!Monde.marchablePieton(tx, ty) || Monde.solidite(tx, ty) !== 0 || Monde.estRoute(tx, ty)) return false;
      if (Monde.devantDUnePorte(tx, ty)) return false;
      const x = tx * TT + 8, y = ty * TT + 12, m = r.degagement_px || 14;
      if (decor.some(function (d) { return Math.abs(d.x - x) < m + 8 && d.y > y - haut - 6 && d.y < y + m; })) return false;
      return !pris.some(function (p) { return Math.abs(p.x - x) < 20 && Math.abs(p.y - y) < 16; });
    }
    function premiere(fx, fy, essais, cote, haut) {
      for (const e of essais) {
        const tx = fx + e[0] * cote, ty = fy + e[1];
        if (!libre(tx, ty, haut)) continue;
        const p = { x: tx * TT + 8, y: ty * TT + 12, tx: tx, ty: ty };
        pris.push(p);
        return p;
      }
      return null;
    }
    memo = (def.decor || []).filter(function (d) { return d.type === 'fontaine'; }).map(function (f) {
      const braseros = [premiere(f.x, f.y, r.brasero_essais, -1, 22), premiere(f.x, f.y, r.brasero_essais, 1, 22)].filter(Boolean);
      return { fontaine: f, braseros: braseros, roulotte: premiere(f.x, f.y, r.roulotte_essais, 1, 28) };
    });
    memoDef = def;
    return memo;
  }

  function braseros() { return allumes() ? [].concat.apply([], places().map(function (p) { return p.braseros; })) : []; }
  function roulottes() { return allumes() ? places().map(function (p) { return p.roulotte; }).filter(Boolean) : []; }

  /** Les braseros allumés dans ce rayon d'un point. */
  function braserosPres(x, y, rayon) {
    return braseros().filter(function (b) { return Math.hypot(b.x - x, b.y - y) <= rayon; });
  }

  // --- La chaleur, le chocolat ----------------------------------------------------------------

  /** Chaque pas de jeu : le joueur à pied, debout près d'un feu, reprend son souffle plus vite. */
  //: Jusqu'où l'on entend un brasero crépiter, et d'où il joue plein.
  const SON_PORTEE_PX = 200, SON_PLEIN_PX = 40;

  /** Le crépitement du brasero le plus proche, dosé à la distance, une fois par image (comme l'orgue de la
      foire) — muet dedans, l'été, ou loin de tout. */
  function sonDuFeu(j) {
    if (typeof Son === 'undefined' || !Son.SFX.foyer_feu) return;
    let d = Infinity;
    if (allumes()) for (const b of braseros()) d = Math.min(d, Math.hypot(b.x - j.x, b.y - j.y));
    Son.SFX.foyer_feu(d >= SON_PORTEE_PX ? 0 : d <= SON_PLEIN_PX ? 1 : 1 - (d - SON_PLEIN_PX) / (SON_PORTEE_PX - SON_PLEIN_PX));
  }

  function maj() {
    const j = B.joueur, r = regles();
    if (!j || !r) return;
    sonDuFeu(j);
    const pres = !j.dansVehicule && allumes() && braserosPres(j.x, j.y, r.chaleur_px).length > 0;
    if (!pres) { j.auChaud = false; return; }
    if (Math.hypot(j.vx || 0, j.vy || 0) > 0.3) return;
    const plein = B.defs.recherche.vitesses.endurance;
    j.endurance = Math.min(plein, j.endurance + r.chaleur_souffle);
    if (!j.auChaud) { j.auChaud = true; Hud.message('ÇA RÉCHAUFFE', 90); }
  }

  /** La roulotte devant soi, à pied — ou null. */
  function sousLaMain(j) {
    const r = regles();
    if (!j || !r || j.dansVehicule || j.manege) return null;
    for (const q of roulottes()) {
      if (Math.hypot(j.x - q.x, j.y - (q.y + 6)) <= r.portee_roulotte_px && faceA(j, q.x, q.y)) return q;
    }
    return null;
  }

  /** ⚠️ ON NE PASSE PAS À TRAVERS UN BRASERO NI UNE ROULOTTE — appelé à la fin de chaque pas d'un piéton
      (`Entites.bloquerParDecor`), comme le train de la foire : on ressort par le rayon. */
  function bloquer(e) {
    if (!e || (e.type !== 'pieton' && e.type !== 'joueur' && e.type !== 'agent') || e.dansVehicule || !allumes()) return;
    const obstacles = braseros().map(function (b) { return [b, 6]; }).concat(roulottes().map(function (q) { return [q, 11]; }));
    for (const [o, r] of obstacles) {
      const dx = e.x - o.x, dy = e.y - o.y, min = r + (e.r || 5), d2 = dx * dx + dy * dy;
      if (d2 >= min * min || d2 === 0) continue;
      const d = Math.sqrt(d2);
      e.x = o.x + dx / d * min; e.y = o.y + dy / d * min;
    }
  }

  // --- Le dessin ------------------------------------------------------------------------------

  function px(ctx, c, x, y, l, h) { ctx.fillStyle = c; ctx.fillRect(x, y, l || 1, h || 1); }

  /** LE BRASERO : une vasque d'acier sur trois pattes, des bûches, et trois flammes qui dansent (`pose`,
      trois images). 16 × 24, le pied en bas. */
  function peindreBrasero(ctx, pose) {
    px(ctx, 'rgba(20,18,26,0.28)', 2, 21, 12, 3);                        // l'ombre
    px(ctx, '#2f3136', 3, 15, 1, 7); px(ctx, '#2f3136', 12, 15, 1, 7); px(ctx, '#2f3136', 7, 16, 2, 6);   // les pattes
    px(ctx, '#3d4046', 1, 11, 14, 5); px(ctx, '#55595f', 2, 11, 12, 1);  // la vasque, son rebord
    px(ctx, '#2a2c30', 2, 15, 12, 1);
    px(ctx, '#6b4a2e', 3, 9, 10, 2); px(ctx, '#4a3320', 5, 8, 6, 1);     // les bûches
    px(ctx, '#ffb347', 3, 10, 10, 1);                                     // la braise
    const flammes = [[3, 7, 4], [7, 4, 7], [11, 6, 5]];
    flammes.forEach(function (f, k) {
      const monte = (pose + k) % 3, x = f[0], h = f[2] - (monte === 1 ? 1 : 0) + (monte === 2 ? 1 : 0);
      px(ctx, '#e8452c', x - 1, 10 - h, 3, h);
      px(ctx, '#ff8a1f', x - 1 + (monte & 1), 10 - h + 1, 2, h - 1);
      px(ctx, '#ffe36a', x, 10 - Math.max(1, h - 2), 1, Math.max(1, h - 3));
    });
    if (pose === 1) px(ctx, '#ffd23a', 9, 1, 1, 1);                      // une étincelle
    if (pose === 2) px(ctx, '#ffd23a', 5, 2, 1, 1);
  }

  /** LA ROULOTTE DE CHOCOLAT CHAUD : une charrette de bois sous un auvent brun et crème, la marchande en
      tuque derrière son comptoir, la grosse tasse peinte sur l'enseigne, et la vapeur qui monte
      (`pose`, deux images). 28 × 30, le pied en bas. */
  function peindreRoulotte(ctx, pose) {
    px(ctx, 'rgba(20,18,26,0.28)', 2, 26, 24, 4);
    // La marchande, derrière : la tuque rouge et son pompon, le manteau.
    px(ctx, '#2c4a78', 9, 13, 10, 5);
    px(ctx, '#e8b088', 11, 9, 6, 4); px(ctx, '#1b1b1f', 12, 11, 1, 1); px(ctx, '#1b1b1f', 15, 11, 1, 1);
    px(ctx, '#c0392b', 11, 7, 6, 3); px(ctx, '#efe6d0', 11, 9, 6, 1); px(ctx, '#efe6d0', 13, 6, 2, 1);
    // La caisse de la roulotte.
    px(ctx, '#7a5230', 2, 17, 24, 8); px(ctx, '#8e6440', 2, 17, 24, 2);
    for (let x = 5; x < 25; x += 5) px(ctx, '#6a4526', x, 19, 1, 6);
    px(ctx, '#b89060', 1, 16, 26, 2);                                      // le comptoir
    px(ctx, '#2f3136', 4, 24, 4, 4); px(ctx, '#2f3136', 20, 24, 4, 4);    // les roues
    px(ctx, '#55595f', 5, 25, 2, 2); px(ctx, '#55595f', 21, 25, 2, 2);
    // Sur le comptoir : le thermos et deux tasses.
    px(ctx, '#c0392b', 4, 12, 3, 4); px(ctx, '#efe6d0', 4, 13, 3, 1);
    px(ctx, '#efe6d0', 20, 14, 3, 2); px(ctx, '#efe6d0', 23, 14, 2, 2); px(ctx, '#5a3a1e', 20, 14, 3, 1);
    // L'auvent raye et ses deux poteaux.
    px(ctx, '#5a3f26', 2, 5, 1, 12); px(ctx, '#5a3f26', 25, 5, 1, 12);
    for (let x = 0; x < 28; x++) {
      px(ctx, (Math.floor(x / 4) % 2) ? '#efe6d0' : '#6b3f22', x, 2, 1, 4);
      if (x % 4 !== 3) px(ctx, (Math.floor(x / 4) % 2) ? '#efe6d0' : '#6b3f22', x, 6, 1, 1);
    }
    // L'enseigne, peinte sur le devant de la caisse : une grosse tasse crème et son anse, pleine de chocolat.
    px(ctx, '#efe6d0', 11, 19, 6, 5); px(ctx, '#efe6d0', 17, 20, 2, 1); px(ctx, '#efe6d0', 18, 20, 1, 3);
    px(ctx, '#5a3a1e', 12, 19, 4, 1);
    // La vapeur de la tasse de droite, qui monte en deux temps.
    const v = pose ? 0 : 1;
    px(ctx, 'rgba(240,240,245,0.75)', 21 + v, 11, 1, 2); px(ctx, 'rgba(240,240,245,0.55)', 22 - v, 8, 1, 2);
  }

  function imageBrasero(pose) {
    return Atlas.cuirePeintre('foyers|brasero|' + pose, 16, 24, function (g) { peindreBrasero(g, pose); });
  }
  function imageRoulotte(pose) {
    return Atlas.cuirePeintre('foyers|roulotte|' + pose, 28, 30, function (g) { peindreRoulotte(g, pose); });
  }

  /** Ce qui se trie avec les gens, s'il est à l'écran : chaque brasero et chaque roulotte, à leur pied. */
  function ajouterVisibles(visibles, cx, cy) {
    if (!allumes()) return;
    const pb = Math.floor(B.t / 7) % 3, pr = Math.floor(B.t / 30) % 2;
    for (const b of braseros()) {
      if (b.x < cx - 20 || b.x > cx + VW + 20 || b.y < cy - 30 || b.y > cy + VH + 20) continue;
      visibles.push({ id: ID_TRI, vivant: true, x: b.x, y: b.y, peindreFoire: function (ctx) {
        ctx.drawImage(imageBrasero(pb), Math.round(b.x - 8 - cx), Math.round(b.y - 22 - cy)); B.stats.images++;
      } });
    }
    for (const q of roulottes()) {
      if (q.x < cx - 30 || q.x > cx + VW + 30 || q.y < cy - 34 || q.y > cy + VH + 20) continue;
      visibles.push({ id: ID_TRI + 1, vivant: true, x: q.x, y: q.y, peindreFoire: function (ctx) {
        ctx.drawImage(imageRoulotte(pr), Math.round(q.x - 14 - cx), Math.round(q.y - 26 - cy)); B.stats.images++;
      } });
    }
  }

  /** Les lueurs du soir (`Monde.lampesVisibles`, qui ne demande qu'à la brune) : chaque brasero, et chaque
      jongleur de feu qui joue. En pixels d'écran, comme les autres lampes. */
  function lampes(cx, cy) {
    if (!allumes()) return [];
    const r = regles(), out = [];
    for (const b of braseros()) {
      if (b.x < cx - r.lueur_px || b.x > cx + VW + r.lueur_px || b.y < cy - r.lueur_px || b.y > cy + VH + r.lueur_px) continue;
      out.push({ x: b.x - cx, y: b.y - 10 - cy, r: r.lueur_px, c: LUEUR });
    }
    for (const e of B.entites) {
      if (e.type !== 'pieton' || !e.vivant || e.metier !== 'jongleur' || e.etat === 'assomme') continue;
      if (e.x < cx - 40 || e.x > cx + VW + 40 || e.y < cy - 40 || e.y > cy + VH + 40) continue;
      out.push({ x: e.x - cx, y: e.y - 16 - cy, r: 40, c: LUEUR_JONGLEUR });
    }
    return out;
  }

  return { regles, allumes, places, braseros, roulottes, braserosPres, maj, sousLaMain, bloquer, ajouterVisibles, lampes,
           peindreBrasero, peindreRoulotte };
})();
