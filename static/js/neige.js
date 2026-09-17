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

  /** Le jour d'une tempete ? Et laquelle (0, 1, 2...) : c'est elle qui choisit le secteur. */
  function rangDeTempete(jour) {
    const t = donnees().tempete;
    if (jour < t.premier || (jour - t.premier) % t.tous_les !== 0) return -1;
    return (jour - t.premier) / t.tous_les;
  }

  /** La nuit de deneigement a cette heure : { secteur, enCours } — ou null. Pure.
      ⚠️ Le LENDEMAIN d'une tempete, des `annonce_h` : les panneaux du secteur clignotent.
      De `debut_h` a `fin_h` le matin d'apres, ce qui reste dans ses rues part au lot. */
  function operationA(jour, heure) {
    const d = donnees();
    if (!d || !d.deneigement) return null;
    const o = d.deneigement, h = heure * 24;
    const annonce = rangDeTempete(jour - o.apres_tempete_jours);
    if (annonce >= 0 && h >= o.annonce_h) return { secteur: o.secteurs[annonce % o.secteurs.length], enCours: h >= o.debut_h };
    const veille = rangDeTempete(jour - 1 - o.apres_tempete_jours);
    if (veille >= 0 && h < o.fin_h) return { secteur: o.secteurs[veille % o.secteurs.length], enCours: true };
    return null;
  }

  function operation() {
    if (!B.options || !B.options.neige || !B.partie) return null;
    return operationA(B.partie.jour, B.partie.heure);
  }

  /** La neige AU SOL : la tempete, puis ce qu'il en reste jusqu'a la fin de l'operation
      qui la deblaie. Pure (avec l'intensite). */
  function couvertureA(jour, heure) {
    const i = intensiteA(jour, heure), d = donnees();
    if (!d || !d.deneigement) return i;
    const o = d.deneigement, t = d.tempete, h = heure * 24;
    const reste = (rangDeTempete(jour) >= 0 && h >= t.fin_h)
      || rangDeTempete(jour - o.apres_tempete_jours) >= 0
      || (rangDeTempete(jour - 1 - o.apres_tempete_jours) >= 0 && h < o.fin_h);
    return Math.max(i, reste ? o.reste : 0);
  }

  function couverture() {
    if (!B.options || !B.options.neige || !B.partie || B.interieur) return 0;
    return couvertureA(B.partie.jour, B.partie.heure);
  }

  /** La charrue sort avec la tempete, et la nuit de deneigement. */
  function charrueDehors() {
    const o = operation();
    return intensite() > 0 || !!(o && o.enCours);
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
    const i = couverture();
    if (!i) return 1;
    const e = donnees().effets;
    return melange(deneigee(Math.floor(v.x / TT), Math.floor(v.y / TT)) ? e.adherence_deneigee : e.adherence, i);
  }

  /** Et de son freinage. */
  function frein(v) {
    const i = couverture();
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

  // --- La nuit de deneigement ----------------------------------------------------------

  //: Les cases de stationnement : un char DANS sa case ne part jamais au lot.
  const CASES = { '^': 1, 'v': 1, '<': 1, '>': 1 };

  function dansLeSecteur(secteur, tx, ty) {
    return Monde.carte.def.zones.some(function (z) {
      return z.district === secteur && tx >= z.x && tx < z.x + z.l && ty >= z.y && ty < z.y + z.h;
    });
  }

  function dansUneCase(v) {
    const demi = Math.max(v.def.longueur, v.def.largeur) / 2;
    for (let ty = Math.floor((v.y - demi) / TT); ty <= Math.floor((v.y + demi) / TT); ty++) {
      for (let tx = Math.floor((v.x - demi) / TT); tx <= Math.floor((v.x + demi) / TT); tx++) {
        if (CASES[Monde.glyphe(tx, ty)]) return true;
      }
    }
    return false;
  }

  /** Pendant l'operation, une fois par seconde : un char LAISSE dans les rues du secteur
      (hors d'une case, hors de la planque) part au lot — quand on ne le regarde pas. On
      ne voit pas la remorqueuse l'emmener : on le retrouve au lot le lendemain. */
  function majDeneigement() {
    const o = operation();
    if (!o || !o.enCours || B.interieur || B.t % 60 !== 0) return;
    for (const v of B.entites.slice()) {
      if (v.type !== 'vehicule' || !v.laisse || v.conducteur || v.etat === 'epave') continue;
      if (v.saisi !== null && v.saisi !== undefined) continue;
      if (Missions.estDeLaPlanque(v) || dansUneCase(v)) continue;
      if (!dansLeSecteur(o.secteur, Math.floor(v.x / TT), Math.floor(v.y / TT))) continue;
      if (Entites.visibleAEcran(v.x, v.y, 60)) continue;
      const nom = v.def.nom.toUpperCase();
      Missions.saisir(v);
      Hud.message('DÉNEIGEMENT — ' + nom + ' REMORQUÉ AU LOT', 300);
    }
  }

  function panneauxDuSecteur(o) {
    const d = donnees();
    return (o && d.deneigement && d.deneigement.panneaux[o.secteur]) || [];
  }

  /** Les panneaux du secteur annonce, le feu orange qui clignote. */
  function dessinerPanneaux(ctx, cam) {
    const o = operation();
    if (!o || B.interieur) return;
    const allume = ((B.image || B.t) % 40) < 20;
    let n = 0;
    for (const p of panneauxDuSecteur(o)) {
      const px = Math.round(p[0] * TT + 8 - cam.x), py = Math.round(p[1] * TT + 13 - cam.y);
      if (px < -10 || px > VW + 10 || py < -4 || py > VH + 26) continue;
      ctx.fillStyle = '#4a4d55'; ctx.fillRect(px, py - 15, 1, 15);
      ctx.fillStyle = '#eeeae0'; ctx.fillRect(px - 4, py - 22, 9, 7);
      ctx.fillStyle = '#c0392b'; ctx.fillRect(px - 3, py - 21, 7, 1); ctx.fillRect(px - 3, py - 17, 7, 1); ctx.fillRect(px, py - 20, 1, 3);
      ctx.fillStyle = allume ? '#ff9f1c' : '#6a4812'; ctx.fillRect(px - 1, py - 26, 3, 3);
      n += 6;
    }
    B.stats.rects += n;
  }

  /** Pres d'un panneau allume, la ligne du bas dit ce qu'il annonce. */
  function texteDInfo(j) {
    const o = operation();
    if (!o || !j || B.interieur) return null;
    const pres = panneauxDuSecteur(o).some(function (p) { return Math.abs(p[0] * TT + 8 - j.x) + Math.abs(p[1] * TT + 8 - j.y) <= 3 * TT; });
    if (!pres) return null;
    const debut = donnees().deneigement.debut_h;
    return o.enCours ? 'DÉNEIGEMENT EN COURS · STATIONNEMENT INTERDIT' : 'DÉNEIGEMENT CETTE NUIT · STATIONNEMENT INTERDIT DÈS ' + debut + ':00';
  }

  function maj() {
    majDeneigement();
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
    const i = couverture();
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
    donnees, intensiteA, intensite, couvertureA, couverture, operationA, operation, charrueDehors,
    deneigee, deneiger, adherence, frein, vitesseTrafic, dansUneCase, majDeneigement, texteDInfo,
    maj, oublier, dessinerSol, dessinerTempete, dessinerPanneaux,
    get deneigees() { return deneigees.size; },
  };
})();
