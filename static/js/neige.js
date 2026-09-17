/* Bandini — la neige (M12) : la tempete, ce qu'elle fait aux chars, et la charrue.

   Demande du plan : « Tempete de neige (risque) : visibilite reduite, adherence divisee,
   charrue qui pousse la neige et les chars mal gares ; la police glisse aussi. »

   ⚠️ PYTHON REGLE, ICI ON NEIGE. Quand il neige, ce que la neige fait et la tournee de
   la charrue viennent du paquet (`carte.neige`, `app/neige.py`). L'intensite est une
   fonction du jour et de l'heure (`intensiteA`) : rien a simuler, et deux joueurs voient
   la meme tempete le meme soir.

   ⚠️ DERRIERE UNE OPTION (`B.options.neige`, NON par defaut). Sans elle, `intensite()`
   rend 0, et 0 ne change rien : l'adherence est multipliee par 1, le trafic roule a sa
   vitesse, rien ne se peint et la charrue ne sort pas. La sonde de performance du
   navigateur la mesure allumee avant qu'on l'allume pour tout le monde.

   ⚠️ LA NEIGE DEBLAYEE EST LA SEULE MEMOIRE. La charrue note les tuiles qu'elle passe
   (`deneiger`) ; une tuile deblayee se recouvre au bout de `deneige_images`. Rien d'autre
   n'est retenu, et rien ne se sauvegarde : une partie rechargee trouve la rue blanche. */

const Neige = (function () {
  'use strict';

  //: Le voile et les flocons tombent de la meme graine d'une image a l'autre.
  const GRAINE_FLOCONS = 7;
  //: Toutes les combien d'images on oublie les tuiles recouvertes.
  const MENAGE_IMAGES = 600;

  const deneigees = new Map();
  let boucleVent = 0;

  function donnees() { return B.defs && B.defs.carte && B.defs.carte.neige; }

  /** La tempete ce jour-la, a cette heure (0 a 1 de la journee) : 0 rien, 1 pleine. Pure. */
  function intensiteA(jour, heure) {
    const d = donnees();
    if (!d) return 0;
    const t = d.tempete, h = heure * 24;
    if (jour < t.premier || (jour - t.premier) % t.tous_les !== 0) return 0;
    if (h < t.debut_h || h >= t.fin_h) return 0;
    return Math.max(0, Math.min(1, (h - t.debut_h) / t.montee_h, (t.fin_h - h) / t.montee_h));
  }

  /** La tempete, maintenant, pour ce joueur : 0 sans l'option, dedans, ou par beau temps. */
  function intensite() {
    if (!B.options || !B.options.neige || !B.partie || B.interieur) return 0;
    return intensiteA(B.partie.jour, B.partie.heure);
  }

  function cle(tx, ty) { return tx + ',' + ty; }

  function deneigee(tx, ty) {
    const t = deneigees.get(cle(tx, ty));
    return t !== undefined && B.t - t < donnees().effets.deneige_images;
  }

  /** La charrue passe : sa tuile et ses voisines sont deblayees. */
  function deneiger(tx, ty, largeur) {
    const l = largeur || 0;
    for (let dy = -l; dy <= l; dy++) for (let dx = -l; dx <= l; dx++) deneigees.set(cle(tx + dx, ty + dy), B.t);
  }

  function melange(base, i) { return 1 - (1 - base) * i; }

  /** Ce que la neige laisse de l'adherence d'un char, ici. */
  function adherence(v) {
    const i = intensite();
    if (!i) return 1;
    const e = donnees().effets;
    return melange(deneigee(Math.floor(v.x / TT), Math.floor(v.y / TT)) ? e.adherence_deneigee : e.adherence, i);
  }

  /** Et de son freinage. */
  function frein(v) {
    const i = intensite();
    if (!i) return 1;
    const e = donnees().effets;
    return deneigee(Math.floor(v.x / TT), Math.floor(v.y / TT)) ? 1 : melange(e.frein, i);
  }

  /** Le trafic leve le pied. */
  function vitesseTrafic() {
    const i = intensite();
    return i ? melange(donnees().effets.vitesse_trafic, i) : 1;
  }

  // --- A chaque image ------------------------------------------------------------------

  function maj() {
    const i = intensite();
    // Le vent : une boucle dont le volume suit la tempete.
    const voulu = i > 0.02 ? i * 0.5 : 0;
    if (voulu && !boucleVent) Son.boucle('tempete', true, voulu);
    else if (voulu) Son.reglerBoucle('tempete', voulu);
    else if (boucleVent) Son.boucle('tempete', false);
    boucleVent = voulu;
    if (B.t % MENAGE_IMAGES === 0 && deneigees.size) {
      const vieux = donnees().effets.deneige_images;
      deneigees.forEach(function (t, k) { if (B.t - t >= vieux) deneigees.delete(k); });
    }
  }

  function oublier() {
    deneigees.clear();
    if (boucleVent) Son.boucle('tempete', false);
    boucleVent = 0;
  }

  // --- Le dessin -----------------------------------------------------------------------

  /** La neige au sol : un blanc translucide sur tout ce qui n'est ni de l'eau ni
      deblaye. ⚠️ Par PLAGES de tuiles d'une rangee, pas tuile par tuile : cinq cents
      rectangles par image deviennent une cinquantaine. */
  function dessinerSol(ctx, cam) {
    const i = intensite();
    if (!i) return;
    const c = Monde.carte, e = donnees().effets;
    const x0 = Math.max(0, Math.floor(cam.x / TT)), y0 = Math.max(0, Math.floor(cam.y / TT));
    const x1 = Math.min(c.w - 1, Math.ceil((cam.x + VW) / TT)), y1 = Math.min(c.h - 1, Math.ceil((cam.y + VH) / TT));
    ctx.fillStyle = 'rgba(238,243,250,' + (e.sol * i).toFixed(3) + ')';
    let n = 0;
    for (let ty = y0; ty <= y1; ty++) {
      let debut = -1;
      for (let tx = x0; tx <= x1 + 1; tx++) {
        const blanc = tx <= x1 && !Monde.estEau(tx, ty) && !deneigee(tx, ty);
        if (blanc && debut < 0) debut = tx;
        if (!blanc && debut >= 0) {
          ctx.fillRect(Math.round(debut * TT - cam.x), Math.round(ty * TT - cam.y), (tx - debut) * TT, TT);
          n++;
          debut = -1;
        }
      }
    }
    B.stats.rects += n;
  }

  /** La tempete a l'ecran : le voile (la visibilite) et les flocons qui tombent en
      biais. ⚠️ Chaque flocon est une fonction de l'image : aucun etat, aucun de. */
  function dessinerTempete(ctx) {
    const i = intensite();
    if (!i) return;
    const e = donnees().effets;
    ctx.fillStyle = 'rgba(226,232,240,' + (e.voile * i).toFixed(3) + ')';
    ctx.fillRect(0, 0, VW, VH);
    const n = Math.round(e.flocons * i), t = B.image || B.t;
    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    for (let k = 0; k < n; k++) {
      const h = hash2(k, GRAINE_FLOCONS);
      const vitesse = 0.6 + (h % 7) / 6, derive = 0.35 + ((h >>> 3) % 5) / 10;
      const x = ((h % (VW + 40)) + t * derive) % (VW + 40) - 20;
      const y = (((h >>> 9) % (VH + 20)) + t * vitesse) % (VH + 20) - 10;
      const taille = (h >>> 17) % 3 === 0 ? 2 : 1;
      ctx.fillRect(Math.round(x), Math.round(y), taille, taille);
    }
    B.stats.rects += n + 1;
  }

  return {
    donnees, intensiteA, intensite, deneigee, deneiger, adherence, frein, vitesseTrafic,
    maj, oublier, dessinerSol, dessinerTempete,
    get deneigees() { return deneigees.size; },
  };
})();
