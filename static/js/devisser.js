/* Bandini — les enseignes qu'on dévisse la nuit (P4, docs/jalons/des-choses-a-collectionner-et-la-planque-qu-on-decore.md),
   la cinquième famille des collections.

   Douze ENSEIGNES-DRAPEAUX : celle qui pend au bout d'une devanture, au-dessus du trottoir — là où les autres commerces
   ont une pancarte muette, ces douze ont un NÉON à leur emblème (`app/devisser.py` : une grille de 5 × 7 et sa palette),
   qui luit la nuit. La nuit seulement, à pied, debout sous elle : ACTION ouvre LE TOURNEVIS, une épreuve d'adresse
   (`Adresse.EPREUVES.tournevis`) — quatre vis, chacune d'un tour dans le sens contraire des aiguilles (HAUT, GAUCHE,
   BAS, DROITE), au stick, à la croix ou aux flèches.

   ⚠️ AUCUNE FENÊTRE DE RYTHME ET AUCUN ÉCHEC (la leçon du dojo) : on tourne à son rythme ; un cran dans le mauvais
   sens ne défait rien, il est seulement commenté ; ESQUIVE abandonne et l'enseigne reste.

   ⚠️ LE RISQUE : l'enseigne qui tombe est une EFFRACTION (`recherche.DELITS`, une étoile, il faut un témoin) — un
   policier qui voit chauffe tout de suite, un passant qui a vu court le raconter (`Police.signalerCrime`).

   ⚠️ RIEN AU DÉMARRAGE ET RIEN DANS LA VILLE : le néon se PEINT dans le morceau de la façade (`Monde`, par
   `peindreDrapeau`), recuit quand le compte change (`cle`) ; une enseigne dévissée laisse la potence vide, un fil qui
   pend. Elle monte au mur de la planque (`Decoration`, `mur_enseignes` : un bit chacune, `masque`).

   ⚠️ LE SLUG EST LE NOM : `partie.collections.enseignes[slug] = { jour, source }`. Le catalogue arrive avec les
   collections (`Collections.catalogue().enseignes`). */

const Devisser = (function () {
  'use strict';

  const T = 16;

  // --- Le catalogue ---------------------------------------------------------------------------------

  function donnees() { const c = typeof Collections !== 'undefined' && Collections.catalogue(); return (c && c.enseignes) || null; }
  function liste() { const d = donnees(); return (d && d.liste) || []; }
  function regle() { const d = donnees(); return (d && d.regle) || {}; }
  function enseigne(slug) { return liste().find(function (f) { return f.slug === slug; }) || null; }
  function prises() { return Collections.famille('enseignes'); }
  function devissee(slug) { return !!prises()[slug]; }
  function nombre() { return liste().filter(function (f) { return devissee(f.slug); }).length; }
  function total() { return liste().length; }
  /** Le mur de la planque : un bit par enseigne dévissée, dans l'ordre du catalogue (la pose du dessin). */
  function masque() {
    let m = 0;
    liste().forEach(function (f, i) { if (devissee(f.slug)) m |= 1 << i; });
    return m;
  }
  /** La clé des façades peintes : elle change quand le catalogue arrive et à chaque enseigne dévissée — les morceaux
      de la ville se recuisent alors (`Monde.dessinerSol`), une fois, jamais à chaque image. */
  function cle() { return donnees() ? 'e' + masque() : ''; }

  //: Les enseignes par devanture (« x,y » de la devanture) : refait quand le catalogue change.
  let index = null, indexDe = null;
  /** L'enseigne qui pend à cette devanture (`ville.devantures`), ou null. */
  function deLaDevanture(d) {
    const l = liste();
    if (indexDe !== l) {
      index = new Map(); indexDe = l;
      for (const f of l) if (typeof f.x === 'number') index.set(f.x + ',' + f.y, f);
    }
    return index.get(d.x + ',' + d.y) || null;
  }

  /** Le coin haut-gauche du néon, en pixels du monde : là où pendait la pancarte (`FACADES.pancarte`). */
  function coin(f) { return { x: f.x * T + (f.pancarte < 0 ? 2 : f.l * T - 9), y: (f.y + 1) * T + 1 }; }
  /** Son centre, en pixels du monde. */
  function point(f) { const c = coin(f); return { x: c.x + 3.5, y: c.y + 4.5 }; }

  /** Celles qui pendent encore, en ville (ni dans une pièce, ni dans un bloc). */
  function aDevisser() {
    if (B.interieur || B.bloc) return [];
    return liste().filter(function (f) { return typeof f.x === 'number' && !devissee(f.slug); });
  }

  // --- Les dessins -----------------------------------------------------------------------------------

  /** L'emblème : sa grille (5 × 7), `ech` pixels par case. */
  function peindreEmbleme(ctx, f, x, y, ech) {
    const g = f.grille || [];
    for (let iy = 0; iy < g.length; iy++) {
      for (let ix = 0; ix < g[iy].length; ix++) {
        const c = g[iy][ix];
        if (c === '.') continue;
        ctx.fillStyle = f.palette[c] || '#ff00ff';
        ctx.fillRect(x + ix * ech, y + iy * ech, ech, ech);
      }
    }
  }

  //: Le néon, 7 × 9 : un cadre de métal, le fond noir du tube, l'emblème au milieu.
  const NEON = { l: 7, h: 9, cadre: '#8a8c94', arete: '#c8cad0', fond: '#14121c' };

  /** Le néon d'une enseigne, `ech` pixels par pixel (1 sur la rue et au mur, 4 au tournevis, 5 au carnet). */
  function peindreNeon(ctx, f, x, y, ech) {
    const e = ech || 1;
    ctx.fillStyle = NEON.cadre; ctx.fillRect(x, y, NEON.l * e, NEON.h * e);
    ctx.fillStyle = NEON.arete; ctx.fillRect(x, y, NEON.l * e, e);
    ctx.fillStyle = NEON.fond; ctx.fillRect(x + e, y + e, (NEON.l - 2) * e, (NEON.h - 2) * e);
    peindreEmbleme(ctx, f, x + e, y + e, e);
  }

  /** Sur la façade, à la place de la pancarte (`Monde.peindreDevantures`, dans le repère du MORCEAU : `ox`, `oy` est le
      coin de la devanture). Pendue : son ombre, sa potence, le néon. Dévissée : la potence vide, les deux crochets et
      le fil qui pend — la façade garde tout le reste. */
  function peindreDrapeau(ctx, f, d, ox, oy) {
    const x = d.pancarte < 0 ? ox + 2 : ox + d.l * T - 9, y = oy + T + 1;
    const fer = '#5c5e66';
    ctx.fillStyle = fer; ctx.fillRect(x + 3, y - 2, 1, 2);          // la potence, scellée au mur
    if (!devissee(f.slug)) {
      ctx.fillStyle = 'rgba(0,0,0,0.30)'; ctx.fillRect(x + 1, y + 1, 7, 10);   // l'ombre portée au sol
      peindreNeon(ctx, f, x, y, 1);
      return;
    }
    ctx.fillStyle = fer; ctx.fillRect(x, y, 7, 1);                  // la barre d'où elle pendait
    ctx.fillRect(x, y + 1, 1, 1); ctx.fillRect(x + 6, y + 1, 1, 1); // ses deux crochets, vides
    ctx.fillStyle = '#1c1a22';                                       // le fil du néon, coupé, qui pend
    ctx.fillRect(x + 3, y + 1, 1, 2); ctx.fillRect(x + 4, y + 3, 1, 2); ctx.fillRect(x + 3, y + 5, 1, 1);
    ctx.fillStyle = '#c87a3a'; ctx.fillRect(x + 3, y + 6, 1, 1);   // le cuivre, au bout
  }

  //: La lueur du néon la nuit (`lampes`) : la couleur de son emblème, un grésillement de temps en temps.
  const LUEUR = { rayon: 15, alpha: 0.55, nuit: 0.2 };

  function couleurDuNeon(f) {
    const p = f.palette || {}, c = (f.grille || []).join('').replace(/\./g, '')[0];
    return p[c] || '#ffffff';
  }

  function rgba(hex, a) {
    const n = parseInt(hex.slice(1), 16);
    return 'rgba(' + ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a.toFixed(2) + ')';
  }

  /** Les néons qui pendent encore, la nuit : une petite lampe chacun, en coordonnées d'écran (comme les cartes). Un
      néon grésille : quelques images éteintes de temps en temps, à l'empreinte de son rang — jamais un dé. */
  function lampes(cam) {
    if (typeof Monde === 'undefined' || !Monde.ambianceVue || Monde.ambianceVue().alpha <= LUEUR.nuit) return [];
    const out = [];
    liste().forEach(function (f, i) {
      if (typeof f.x !== 'number' || devissee(f.slug) || B.interieur || B.bloc) return;
      const q = point(f), x = q.x - cam.x, y = q.y - cam.y;
      if (x < -30 || y < -30 || x > VW + 30 || y > VH + 30) return;
      if (((B.t || 0) + i * 97) % 420 < 5) return;                  // le grésillement
      out.push({ x: x, y: y, r: LUEUR.rayon, c: rgba(couleurDuNeon(f), LUEUR.alpha) });
    });
    return out;
  }

  // --- Sous la main : la nuit, à pied, debout sous elle ----------------------------------------------

  /** L'enseigne qu'on atteint d'ici, ou null. ⚠️ Le jour, rien : le bouton reste à la porte et aux poches. Et la
      PORTE d'abord : une enseigne ne vole jamais ACTION à une porte où l'on entre. */
  function sousLaMain(j) {
    if (!j || !B.partie || j !== B.joueur || j.dansVehicule || j.nage || B.interieur || B.bloc || B.epreuve || B.defi) return null;
    if (!Monde.estNuit() || Monde.porteDevant(j)) return null;
    const r = regle().portee_px || 16;
    let meilleure = null, dMin = r * r;
    for (const f of aDevisser()) {
      const q = point(f);
      if (Math.abs(q.x - j.x) > r || Math.abs(q.y - j.y) > r) continue;
      const d = dist2(j.x, j.y, q.x, q.y);
      if (d <= dMin) { dMin = d; meilleure = f; }
    }
    return meilleure;
  }

  function invite(j) { const f = sousLaMain(j); return f ? 'DÉVISSER : ' + f.nom : null; }

  //: Le tournevis en cours : `{ slug, epreuve, consigne, regles, f }` — la fiche que joue `Adresse` (null sinon).
  let chantier = null;

  /** ACTION sous une enseigne, la nuit : le tournevis sort. */
  function agir(j) {
    const f = sousLaMain(j);
    if (!f) return false;
    const r = regle();
    chantier = { slug: 'tournevis', epreuve: 'tournevis', consigne: 'À GAUCHE, ÇA SE DÉVISSE : HAUT, GAUCHE, BAS, DROITE',
                 regles: { vis: r.vis || 4, crans: r.crans || 4, f: f }, f: f };
    j.vx = 0; j.vy = 0;
    Son.Lieu.charger('collections');
    return Adresse.commencer(chantier);
  }

  /** Chaque image : le tournevis en cours, et les sons du lieu à un écran d'une enseigne, la nuit. */
  function maj() {
    const j = B.joueur;
    if (j && (B.t || 0) % 30 === 0 && Monde.estNuit && Monde.estNuit()) {
      if (aDevisser().some(function (f) { const q = point(f); return Math.abs(q.x - j.x) < 480 && Math.abs(q.y - j.y) < 480; })) {
        Son.Lieu.charger('collections');
      }
    }
    if (!chantier) return;
    if (!B.epreuve || B.epreuve.slug !== 'tournevis' || !j || !j.vivant || j.dansVehicule) {
      if (B.epreuve && B.epreuve.slug === 'tournevis') Adresse.fermer();
      chantier = null;
      return;
    }
    const issue = Adresse.maj(chantier);
    if (!issue) return;
    Adresse.fermer();
    const f = chantier.f;
    chantier = null;
    if (issue.gagne) arracher(j, f);
    else Hud.message('L’ENSEIGNE RESTE — ' + (issue.raison || ''), 150);
  }

  /** L'enseigne tombe dans les mains : une effraction (un témoin peut la raconter), et elle entre dans la collection. */
  function arracher(j, f) {
    const q = point(f), r = regle();
    j.animT = 14; j.animType = 'ramasse';
    Police.signalerCrime(r.delit || 'effraction', q.x, q.y, Police.quelqu_un_voit(q.x, q.y, null));
    return donner(f.slug, 'rue');
  }

  /** `slug` monte au mur de la planque. `source` : `rue`, `debug`. La prime, le carnet, les paliers. */
  function donner(slug, source, silence) {
    const f = enseigne(slug), p = B.partie;
    if (!f || !p || devissee(f.slug)) return false;
    prises()[f.slug] = { jour: p.jour, source: source || 'rue' };
    if (silence) return true;
    const r = regle(), n = nombre(), N = total();
    if (r.prime) Missions.encaisser(r.prime, 'ENSEIGNE', true);
    Hud.message('ENSEIGNE ' + n + '/' + N + ' — ' + f.nom + (r.prime ? ' (+' + r.prime + ' $)' : ''), 240);
    Histoire.noter('ENSEIGNE : ' + f.nom + ' — AU MUR DE LA PLANQUE', false);
    const palier = (r.paliers || {})[String(n)];
    if (palier) {
      Missions.encaisser(palier, 'COLLECTION', true);
      const complet = n === N;
      Son.SFX.reel_bebelles();
      Hud.prime({ montant: palier, titre: complet ? 'LE MUR DES ENSEIGNES EST PLEIN' : n + ' ENSEIGNES', quoi: 'COLLECTION',
                  bonus: 0, palier: Missions.palierDePrime(palier) });
      Histoire.noter((complet ? 'LES DOUZE ENSEIGNES SONT AU MUR' : n + ' ENSEIGNES') + ' — ' + palier + ' $', true);
    }
    return true;
  }

  // --- Le tournevis : une épreuve d'adresse ------------------------------------------------------------

  //: Les crans du stick, comme `Adresse` : 0 en HAUT, puis dans le sens des aiguilles. Un pas dans le sens CONTRAIRE
  //: (HAUT → GAUCHE → BAS → DROITE) dévisse d'un quart de tour.
  const DIRS = ['HAUT', 'DROITE', 'BAS', 'GAUCHE'];
  const SEUIL = 0.45;
  //: Le temps de voir l'enseigne lâcher avant qu'elle tombe dans les mains.
  const LACHE = 24;

  const TOURNEVIS = {
    init: function () { return { vis: 0, quarts: 0, cran: -1, dit: 'POUSSE OÙ TU VEUX', fini: 0 }; },
    /** Une image : rend `{ gagne }` quand la dernière vis a lâché. Jamais d'échec ni de fenêtre : le mauvais sens est
        dit, rien ne se défait. */
    maj: function (e, r) {
      if (e.fini > 0) return --e.fini === 0 ? { gagne: true } : null;
      const a = Entree.axe;
      if (!a || a.mag < SEUIL) return null;
      const c = Combat.creneauVise(a, 4);
      if (c < 0 || c === e.cran) return null;
      if (e.cran < 0) { e.cran = c; e.dit = 'LA LAME EST DANS LA VIS'; return null; }
      const pas = (e.cran - c + 4) % 4;
      e.cran = c;
      if (pas === 3) { e.dit = 'DANS L’AUTRE SENS, TU LA REVISSES'; return null; }
      if (pas === 2) { e.dit = 'UN QUART À LA FOIS'; return null; }
      e.quarts++;
      e.dit = '';
      if (e.quarts < r.crans) return null;
      e.quarts = 0;
      e.vis++;
      Son.SFX.devisser();
      if (e.vis >= r.vis) { e.fini = LACHE; e.dit = 'ELLE LÂCHE !'; } else e.dit = 'UNE DE MOINS';
      return null;
    },
    compte: function (e, r) { return 'VIS ' + e.vis + ' / ' + r.vis; },
    /** Le néon en grand et ses quatre vis ; à droite, la tête de la vis qu'on tourne, sa fente, ses quarts faits, et la
        direction qui vient, allumée. */
    dessiner: function (ctx, e, r, x, y) {
      const f = r.f, ech = 4, nx = x + 30, ny = y + 4 + (e.fini > 0 ? Math.round((LACHE - e.fini) / 3) : 0);
      peindreNeon(ctx, f, nx, ny, ech);
      // Les quatre vis, aux coins du cadre : celles qu'on a défaites sont des trous.
      const coins = [[0, 0], [NEON.l * ech - 4, 0], [0, NEON.h * ech - 4], [NEON.l * ech - 4, NEON.h * ech - 4]];
      coins.forEach(function (k, i) {
        ctx.fillStyle = i < e.vis ? '#14121c' : i === e.vis ? '#ffe28a' : '#c8cad0';
        ctx.fillRect(nx + k[0], ny + k[1], 4, 4);
        if (i >= e.vis) { ctx.fillStyle = '#5c5e66'; ctx.fillRect(nx + k[0] + 1, ny + k[1] + 1, 2, 2); }
      });
      // La tête de vis, en grand : sa fente suit le dernier cran ; les quarts faits s'allument autour.
      const cx = x + 140, cy = y + 24;
      ctx.fillStyle = '#9a9ca4'; ctx.fillRect(cx - 9, cy - 9, 18, 18);
      ctx.fillStyle = '#c8cad0'; ctx.fillRect(cx - 9, cy - 9, 18, 2);
      ctx.fillStyle = '#2a2a30';
      if (e.cran < 0 || e.cran % 2 === 0) ctx.fillRect(cx - 1, cy - 7, 3, 14); else ctx.fillRect(cx - 7, cy - 1, 14, 3);
      for (let q = 0; q < r.crans; q++) {
        ctx.fillStyle = q < e.quarts ? '#8fd46a' : '#3a3a48';
        ctx.fillRect(cx - 14 + q * 8, cy + 13, 6, 2);
      }
      // HAUT, GAUCHE, BAS, DROITE autour de la tête : la suivante allumée (au début, toutes).
      const suivante = e.cran < 0 ? -1 : (e.cran + 3) % 4;
      const ou = [[0, -20], [21, 0], [0, 20], [-21, 0]];
      DIRS.forEach(function (d, i) {
        const t = d.charAt(0), lx = cx + ou[i][0] - 1, ly = cy + ou[i][1] - 2;
        Atlas.texte(ctx, t, lx, ly, suivante < 0 || suivante === i ? '#ffe28a' : '#5a5a6a', 1);
      });
      const vis = 'VIS ' + Math.min(r.vis, e.vis + 1) + ' / ' + r.vis;
      Atlas.texte(ctx, vis, cx - Math.round(Atlas.largeurTexte(vis, 1) / 2), y + 54, '#cdc6e6', 1);
      if (e.dit) Atlas.texte(ctx, e.dit, x + 100 - Math.round(Atlas.largeurTexte(e.dit, 1) / 2), y + 64,
                             e.dit.indexOf('AUTRE SENS') >= 0 || e.dit.indexOf('QUART') >= 0 ? '#ff8a7a' : '#8fd46a', 1);
      B.stats.rects += 30;
    },
  };
  if (typeof Adresse !== 'undefined') Adresse.EPREUVES.tournevis = TOURNEVIS;

  // --- Le debug ----------------------------------------------------------------------------------------

  /** TRICHES > ALLER > COLLECTIONS : debout sous l'enseigne, sur le trottoir — et la nuit tombée, si c'était le jour. */
  function allerA(f) {
    const j = B.joueur;
    if (!j || !f || typeof f.x !== 'number' || j.dansVehicule || B.interieur || B.bloc) return false;
    const q = point(f);
    j.x = q.x; j.y = (f.y + 1) * T + 9; j.vx = 0; j.vy = 0;
    if (!Monde.estNuit()) B.partie.heure = 22 / 24;
    Entites.indexer();
    Monde.centrerCamera(j.x, j.y);
    return true;
  }

  /** Toutes, d'un coup, en silence (TRICHES) : le mur plein, sans prime. */
  function toutes() {
    let n = 0;
    for (const f of liste()) if (donner(f.slug, 'debug', true)) n++;
    return n;
  }

  function oublier() { if (chantier && B.epreuve && B.epreuve.slug === 'tournevis') Adresse.fermer(); chantier = null; }

  return { donnees, liste, regle, enseigne, devissee, nombre, total, masque, cle, deLaDevanture, coin, point, aDevisser,
           peindreEmbleme, peindreNeon, peindreDrapeau, lampes, sousLaMain, invite, agir, maj, donner, allerA, toutes, oublier,
           TOURNEVIS, get chantier() { return chantier; } };
})();
