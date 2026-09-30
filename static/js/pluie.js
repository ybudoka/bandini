/* Bandini — la pluie de Baie-des-Brumes (docs/jalons/les-quatre-saisons-realistes.md, lot 2).

   Au printemps et a l'automne, des averses ; l'ete, des orages le soir ; jamais l'hiver. La rue
   mouillee glisse comme derriere l'arroseuse, les flaques eclaboussent, la fonte d'avril laisse de la
   gadoue, et en octobre les chars soulevent les feuilles mortes.

   ⚠️ PYTHON REGLE, ICI ON MOUILLE (`app/pluie.py`, `B.defs.pluie`) : la recette du brouillard. Un jour
   a sa pluie a l'empreinte du jour (`journee`), son heure et sa duree aussi — rien a simuler, aucun
   de, la meme averse le meme apres-midi pour tout le monde.

   ⚠️ POUR TOUT LE MONDE, sans option. Au sec, `adherence()` rend 1, et 1 ne change rien. */

const Pluie = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.pluie; }

  //: Une part de 0 a 1 tiree de quelques bits d'une empreinte — des tranches DIFFERENTES pour
  //: la chance, l'heure et la duree (jamais deux petits tirages voisins : la lecon des bits faibles).
  function part(h, decalage) { return ((h >>> decalage) % 1000) / 1000; }

  /** La pluie de ce jour-la : { debut, fin (heures), montee, orage } — ou null. Pure. */
  function journee(jour) {
    const d = donnees();
    if (!d || typeof Calendrier === 'undefined') return null;
    const s = Calendrier.saison(jour);
    if (s === 'hiver') return null;
    const orage = s === 'ete', r = orage ? d.orages : d.averses;
    const h = hash2(jour, r.sel);
    if (part(h, 0) >= r.chance) return null;
    const debut = r.debut_h[0] + part(h, 10) * (r.debut_h[1] - r.debut_h[0]);
    const duree = r.duree_h[0] + part(h, 20) * (r.duree_h[1] - r.duree_h[0]);
    return { debut: debut, fin: debut + duree, montee: r.montee_h, orage: orage };
  }

  /** La pluie ce jour-la, a cette heure (0 a 1 de la journee) : 0 rien, 1 pleine. Pure. */
  function intensiteA(jour, heure) {
    const a = journee(jour), h = heure * 24;
    if (!a || h < a.debut || h >= a.fin) return 0;
    return Math.max(0, Math.min(1, (h - a.debut) / a.montee, (a.fin - h) / a.montee));
  }

  /** La rue est-elle mouillee (0 a 1) : 1 pendant la pluie, puis elle seche en `seche_h`
      (`duree_h` pour les flaques). ⚠️ La veille compte : une averse du soir mouille encore apres
      minuit. Pure. */
  function mouilleeA(jour, heure, duree) {
    const d = donnees();
    if (!d) return 0;
    const seche = duree === undefined ? d.effets.seche_h : duree;
    let m = 0;
    for (const [j, h] of [[jour, heure * 24], [jour - 1, heure * 24 + 24]]) {
      const a = journee(j);
      if (!a || h < a.debut) continue;
      if (h < a.fin) return 1;
      if (h < a.fin + seche) m = Math.max(m, 1 - (h - a.fin) / seche);
    }
    return m;
  }

  /** Maintenant, pour ce joueur : 0 dans une piece (on n'y voit pas la pluie) ou sans partie. */
  function intensite() { return !B.partie || B.interieur ? 0 : intensiteA(B.partie.jour, B.partie.heure); }
  function mouillee() { return !B.partie || B.interieur ? 0 : mouilleeA(B.partie.jour, B.partie.heure); }
  function orage() { const a = B.partie && journee(B.partie.jour); return !!(a && a.orage) && intensite() > 0; }

  /** La fonte d'avril (0 a 1) : de la gadoue du debut a la fin de `gadoue.jours`, qui monte et fond
      sur un quart de la periode. Pure. */
  function gadoueA(jour, heure) {
    const d = donnees();
    if (!d || typeof Calendrier === 'undefined') return 0;
    const g = d.effets.gadoue, x = Calendrier.jourDeLAnnee(jour) + heure, l = g.jours[1] - g.jours[0];
    if (x < g.jours[0] || x >= g.jours[1]) return 0;
    return Math.min(1, (x - g.jours[0]) / (l / 4), (g.jours[1] - x) / (l / 4));
  }
  function gadoue() { return !B.partie || B.interieur ? 0 : gadoueA(B.partie.jour, B.partie.heure); }

  /** Cette tuile a-t-elle sa gadoue (en avril) ? Un trottoir, ou le bord d'une rue qui touche le
      trottoir — a l'empreinte de la tuile. */
  function gadoueSur(tx, ty) {
    const d = donnees();
    if (!d) return false;
    const g = d.effets.gadoue;
    if (hash2(tx * 7 + 3, ty + g.sel) % 1000 >= g.part * 1000) return false;
    if (Monde.estTrottoir(tx, ty)) return true;
    if (!Monde.estRoute(tx, ty)) return false;
    return Monde.estTrottoir(tx + 1, ty) || Monde.estTrottoir(tx - 1, ty) || Monde.estTrottoir(tx, ty + 1) || Monde.estTrottoir(tx, ty - 1);
  }

  function melange(base, i) { return 1 - (1 - base) * i; }

  /** Y a-t-il des feuilles mortes au sol (la palette de la saison en a) ? Fin septembre, pas encore. */
  function feuillesAuSol() {
    if (typeof Saisons === 'undefined') return false;
    const g = Saisons.palette().gazon;
    return g.feuille !== g.fond;
  }

  /** Ce que la rue mouillee laisse de l'adherence d'un char : l'asphalte mouille (les feuilles
      mouillees l'automne), et la gadoue d'avril sous ses roues. Au sec : 1. */
  function adherence(v) {
    const d = donnees();
    if (!d || !B.partie || B.interieur) return 1;
    const e = d.effets, m = mouillee();
    const base = feuillesAuSol() ? e.feuilles_adherence : e.adherence;
    let a = m ? melange(base, m) : 1;
    const g = gadoue();
    if (g && v && gadoueSur(Math.floor(v.x / TT), Math.floor(v.y / TT))) a *= melange(e.gadoue.adherence, g);
    return a;
  }
  function frein(v) {
    const d = donnees(), m = mouillee();
    return d && m ? melange(d.effets.frein, m) : 1;
  }
  function vitesseTrafic() {
    const d = donnees(), i = intensite();
    return d && i ? melange(d.effets.vitesse_trafic, i) : 1;
  }

  // --- Ce qu'on voit -------------------------------------------------------------------------

  /** Cette tuile a-t-elle sa flaque (quand il a plu) ? La rue ou le trottoir, a l'empreinte. */
  function flaqueSur(tx, ty) {
    const d = donnees();
    if (!d) return false;
    const f = d.effets.flaques;
    if (hash2(tx + f.sel, ty * 13 + 5) % 1000 >= f.part * 1000) return false;
    return Monde.estRoute(tx, ty) || Monde.estTrottoir(tx, ty);
  }
  /** Les flaques durent plus longtemps que la rue mouillee (0 a 1 : leur taille). */
  function flaques() {
    const d = donnees();
    return !d || !B.partie || B.interieur ? 0 : mouilleeA(B.partie.jour, B.partie.heure, d.effets.flaques_h);
  }

  /** L'eclair de l'orage, maintenant (0 a 1 : l'eclat qui reste), ou 0. Un eclair par tranche de
      `eclair_s` secondes, a un instant tire de la tranche — a l'empreinte, jamais au de. */
  function eclairA(t) {
    const d = donnees(), e = d.effets, periode = e.eclair_s * 60, tranche = Math.floor(t / periode);
    const k = t - tranche * periode - hash2(tranche, 0xEC1A) % (periode - e.eclair_images);
    return k >= 0 && k < e.eclair_images ? 1 - k / e.eclair_images : 0;
  }
  function eclair() { return orage() ? eclairA(B.t || 0) : 0; }

  /** Le sol sous la pluie : l'asphalte mouille (le reflet de l'arroseuse), les flaques, et la gadoue
      d'avril. Par PLAGES de tuiles d'une rangee — une rue entiere, un rectangle. */
  function dessinerSol(ctx, cam) {
    const m = mouillee(), f = flaques(), g = gadoue();
    if (!m && !f && !g) return;
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    const tx0 = Math.floor(cx / TT), ty0 = Math.floor(cy / TT), tx1 = Math.floor((cx + VW) / TT), ty1 = Math.floor((cy + VH) / TT);
    for (let ty = ty0; ty <= ty1; ty++) {
      if (m) {
        let debut = -1;
        ctx.fillStyle = 'rgba(30,52,86,' + (0.22 * m).toFixed(3) + ')';
        for (let tx = tx0; tx <= tx1 + 1; tx++) {
          const r = tx <= tx1 && Monde.estRoute(tx, ty);
          if (r && debut < 0) debut = tx;
          if (!r && debut >= 0) { ctx.fillRect(debut * TT - cx, ty * TT - cy, (tx - debut) * TT, TT); B.stats.rects++; debut = -1; }
        }
      }
      for (let tx = tx0; tx <= tx1; tx++) {
        const x = tx * TT - cx, y = ty * TT - cy, h = hash2(tx, ty);
        if (m && (h & 7) === 0 && Monde.estRoute(tx, ty)) {       // un miroitement, une tuile sur huit
          ctx.fillStyle = 'rgba(205,225,255,' + (0.3 * m).toFixed(3) + ')';
          ctx.fillRect(x + (h >>> 4) % 10, y + (h >>> 8) % 14, 5, 1);
        }
        if (g && gadoueSur(tx, ty)) {
          ctx.fillStyle = 'rgba(92,70,44,' + (0.55 * g).toFixed(3) + ')';
          ctx.fillRect(x + (h >>> 12) % 5, y + (h >>> 16) % 6, 9, 5);
          ctx.fillRect(x + (h >>> 20) % 8, y + 6 + (h >>> 24) % 5, 6, 4);
        }
        if (f && flaqueSur(tx, ty)) {
          const w = 4 + Math.round(8 * f), hh = 2 + Math.round(3 * f), px = x + 8 - (w >> 1) + ((h >>> 3) % 3), py = y + 8 - (hh >> 1);
          ctx.fillStyle = 'rgba(58,82,112,0.7)';
          ctx.fillRect(px, py, w, hh); ctx.fillRect(px + 1, py - 1, w - 2, hh + 2);
          ctx.fillStyle = 'rgba(190,212,240,0.55)';
          ctx.fillRect(px + 2, py, Math.max(1, w >> 1), 1);
        }
      }
    }
  }

  /** La pluie qui tombe : le voile gris, des traits obliques (des gouttes a l'empreinte de leur
      numero, qui descendent avec le temps — aucun etat, aucun de), et l'eclair de l'orage. */
  function dessiner(ctx) {
    const i = intensite();
    if (!i) return;
    const e = donnees().effets, o = orage();
    ctx.fillStyle = 'rgba(88,98,112,' + ((o ? e.voile_orage : e.voile) * i).toFixed(3) + ')';
    ctx.fillRect(0, 0, VW, VH);
    const n = Math.round((o ? e.gouttes_orage : e.gouttes) * i), t = B.image || B.t || 0;
    ctx.fillStyle = 'rgba(206,220,240,0.62)';
    for (let k = 0; k < n; k++) {
      const h = hash2(k, 0x9A1E);
      const x = ((h % (VW + 60)) - t * 2 % (VW + 60) + (VW + 60)) % (VW + 60) - 30;
      const y = (((h >>> 9) % (VH + 30)) + t * (7 + (h >>> 24) % 3)) % (VH + 30) - 15;
      ctx.fillRect(x, y, 1, 3); ctx.fillRect(x - 1, y + 3, 1, 3);
    }
    B.stats.rects += n * 2 + 1;
  }

  /** L'eclair, PAR-DESSUS LA NUIT (`Base.ecran()`, apres `Base.fin`) : les orages tombent le soir, et
      un flash peint sous le voile de nuit n'etait qu'une lueur (la lecon des feux de la Saint-Jean). */
  function dessinerEclair(ctx) {
    const f = eclair();
    if (!f) return;
    ctx.fillStyle = 'rgba(236,241,255,' + (0.5 * f).toFixed(3) + ')';
    ctx.fillRect(0, 0, VW, VH);
  }

  // --- Ce que font les chars ------------------------------------------------------------------

  /** Chaque char, chaque image (`Vehicules.majEtatDuChar`) : il souleve les feuilles mortes quand il y
      en a au sol (octobre, novembre), et il eclabousse en passant dans une flaque. Aucun de : les
      gouttes et les feuilles sont a l'empreinte de l'instant et du char, et bornees (les particules
      du jeu, 300 au plus ; une flaque par char toutes les `repit_images`). */
  function majChar(v) {
    const d = donnees();
    // Une coque ne souleve ni feuilles ni flaques : la rue est sur la terre (les bateaux, vague 1).
    if (!d || !B.partie || B.interieur || (v.def && v.def.eau)) return;
    const e = d.effets;
    if (v.flaqueT > 0) v.flaqueT--;
    // ⚠️ CHAQUE CHAR, CHAQUE IMAGE, gares compris : on sort avant tout calcul pour ce qui est au pas.
    const vx = v.vx || 0, vy = v.vy || 0;
    if (vx * vx + vy * vy < e.flaques.vitesse_min * e.flaques.vitesse_min) return;
    const vit = Math.hypot(vx, vy);
    if (vit > e.feuilles_vitesse && (B.t + v.id) % e.feuilles_images === 0 && feuillesAuSol()
        && Entites.visibleAEcran(v.x, v.y, 30)) {
      const g = Saisons.palette().gazon, ca = Math.cos(v.angle || 0), sa = Math.sin(v.angle || 0), l = ((v.def && v.def.longueur) || 30) / 2;
      const h = hash2(B.t, v.id * 5 + 1);
      Entites.particule(v.x - ca * l, v.y - sa * l, -ca * 0.5 + ((h % 21) - 10) / 25, -sa * 0.5 + (((h >>> 5) % 21) - 10) / 25,
                        30 + (h >>> 10) % 20, (h >>> 15) & 1 ? g.feuille : g.feuille2, 2, 0.04);
    }
    if (v.flaqueT > 0 || !flaques()) return;
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    if (!flaqueSur(tx, ty)) return;
    v.flaqueT = e.flaques.repit_images;
    eclabousser(v, vit);
  }

  function eclabousser(v, vit) {
    const d = donnees(), f = d.effets.flaques;
    // Hors de l'ecran, personne ne voit les gouttes : elles evinceraient des particules visibles (300 au plus).
    if (Entites.visibleAEcran(v.x, v.y, 30)) for (let k = 0; k < 8; k++) {
      const h = hash2(B.t + k, v.id * 11 + 3), cote = k & 1 ? 1 : -1;
      const nx = -Math.sin(v.angle || 0) * cote, ny = Math.cos(v.angle || 0) * cote;
      Entites.particule(v.x + nx * 6, v.y + ny * 6, nx * (0.8 + (h % 10) / 10) + v.vx * 0.2, ny * (0.8 + ((h >>> 4) % 10) / 10) + v.vy * 0.2,
                        14 + (h >>> 8) % 10, k % 3 ? '#9fb8d6' : '#d6e4f2', 1, 0.2);
    }
    if (typeof Son !== 'undefined' && Son.SFX && Son.SFX.eclaboussure) Son.SFX.eclaboussure(v.x, v.y);
    // Le passant le plus proche, s'il est a portee de l'eclaboussure, le dit.
    const autour = Entites.pietonsAutour(v.x, v.y, f.rayon_passant_px) || [];
    let p = null, dmin = Infinity;
    for (const q of autour) {
      // Ni le passager du char (il est dedans), ni un passant assomme, ni celui qui parle deja (une
      // replique de mission ne s'ecrase pas pour une flaque).
      if (q.dansVehicule || q.etat === 'assomme' || q.bulle) continue;
      const dd = Math.hypot(q.x - v.x, q.y - v.y);
      if (dd < dmin) { dmin = dd; p = q; }
    }
    if (p) Entites.bulle(p, d.eclabousses[hash2(p.id, B.t) % d.eclabousses.length], { duree: 110 });
  }

  //: Le tonnerre attendu (l'instant `B.t` ou il gronde), apres l'eclair ; le volume APPLIQUE a la
  //: boucle (⚠️ pas celui de l'image d'avant : l'averse monte de 0,001 par image, sous tout seuil) ; et
  //: l'instant ou l'on a demande les sons (une fois toutes les 300 images, pas a chaque image — hors
  //: ligne, chaque echec relancerait quatre telechargements).
  let tonnerreA = -1, volumeBoucle = 0, volumeApplique = 0, demandeA = -Infinity;

  /** Chaque image : le groupe de sons se charge a la premiere averse, la boucle de pluie suit
      l'averse (en fondu), et le tonnerre gronde un moment apres l'eclair — pas en meme temps : l'orage
      n'est pas au-dessus de la tete. */
  function maj() {
    if (typeof Son === 'undefined') return;
    const i = intensite();
    const t0 = B.t || 0;
    if (i > 0 && Son.Lieu && t0 - demandeA >= 300) { demandeA = t0; Son.Lieu.charger('pluie'); }
    const voulu = i > 0.02 ? (orage() ? 0.9 : 0.6) * i : 0;
    if (voulu) {
      Son.boucle('pluie', true, voulu, 1.5);
      if (Math.abs(voulu - volumeApplique) > 0.01) { Son.reglerBoucle('pluie', voulu); volumeApplique = voulu; }
    } else if (volumeBoucle) { Son.boucle('pluie', false, 0, 1.5); volumeApplique = 0; }
    volumeBoucle = voulu;
    const e = donnees() && donnees().effets;
    if (!e) return;
    const t = B.t || 0;
    if (orage() && eclairA(t) === 1 && tonnerreA < t) {
      const r = e.tonnerre_apres;
      tonnerreA = t + r[0] + hash2(t, 0x70AA) % (r[1] - r[0]);
    }
    if (tonnerreA >= 0 && t >= tonnerreA) { tonnerreA = -1; if (Son.SFX && Son.SFX.tonnerre) Son.SFX.tonnerre(); }
  }

  /** Une partie recommencee, une piece : la boucle se tait. */
  function oublier() {
    if (volumeBoucle && typeof Son !== 'undefined') Son.boucle('pluie', false, 0, 1.5);
    volumeBoucle = 0; volumeApplique = 0; tonnerreA = -1; demandeA = -Infinity;
  }

  return { donnees, journee, intensiteA, mouilleeA, intensite, mouillee, orage, gadoueA, gadoue, gadoueSur,
           adherence, frein, vitesseTrafic, flaqueSur, flaques, eclairA, eclair, dessinerSol, dessiner, dessinerEclair, majChar, maj, oublier };
})();
