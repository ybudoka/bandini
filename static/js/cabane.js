/* Bandini — la cabane a sucre, pour vrai (docs/jalons/la-cabane-a-sucre-pour-vrai.md).

   Martin (28 sept. 2026) : « la cabane a sucre a besoin de tout ce qui fait une vraie cabane : promenade en
   caleche avec chevaux, seaux et tubulure sur les arbres, banc de neige avec la tire, etc. »

   Au rang (`app/blocs/rang.py`, `BLOC.cabane`) :
   - LA TUBULURE : la ligne bleue d'erable en erable (les `erable_tube` du plan), rang par rang, jusqu'au tuyau
     maitre qui descend au toit de la cabane. Les erables et leurs chaudieres sont du decor (`DECORS`).
   - LA CALECHE : deux chevaux, un cocher, trois bancs. Elle attend a son arret, fait le tour de l'erabliere par
     son sentier et revient ; on y monte (ACTION) et on fait le tour avec elle (`j.manege`, comme le petit
     train de la foire).
   - LA TABLE DE TIRE : le banc de neige dans son auge (`DECORS.table_tire`, ses rubans de sirop qui s'allongent),
     ACTION devant propose le defi de la tire — au temps des sucres.
   - LES GENS : au temps des sucres, pendant les heures du comptoir, le tireur derriere la table, ceux qui roulent
     leur tire, le musicien a la porte (le reel du trottoir), ceux qui attendent la caleche.

   ⚠️ SANS UN DE. La caleche avance par images (ni `B.rng` ni `Math.random`) ; les gens naissent avec un de
   PRETE, tire a l'empreinte (`sansDe`) : entrer au rang ne decale pas le hasard du jeu.
   ⚠️ `Monde.carte` EST LE BLOC ici (la memoire « Monde.carte est le bloc ») : tout se garde par `ici()`. */

const Cabane = (function () {
  'use strict';

  function def() {
    const c = Monde.carte && Monde.carte.def;
    return c && c.bloc && c.bloc.cabane ? c.bloc.cabane : null;
  }
  function ici() { return !!(B.bloc && !B.interieur && def()); }

  /** Le temps des sucres : le printemps, pendant les heures du comptoir `sucre` (on fait bouillir). */
  function temps() { return !!(B.partie && typeof Calendrier !== 'undefined' && Calendrier.saisonDuJour() === 'printemps'); }
  function heures() {
    const c = B.defs && B.defs.comptoirs && B.defs.comptoirs.sucre;
    const h = (c && c.heures) || [7 / 24, 22 / 24], t = B.partie ? B.partie.heure : 0.5;
    return h[0] <= h[1] ? t >= h[0] && t < h[1] : t >= h[0] || t < h[1];
  }
  function onFaitBouillir() { return temps() && heures(); }

  // --- La caleche -----------------------------------------------------------------------------

  //: La caleche : la moitie de sa longueur, la moitie de sa largeur, et ou sont les chevaux (devant elle,
  //: le long du sentier). En pixels.
  const CAISSE = { l: 20, w: 11 };
  const CHEVAUX = { avance: 38, l: 12, w: 10 };
  //: A quelle distance de l'arriere de la caleche on peut y monter.
  const PORTEE_MONTER = 30;
  const INVITE = 'UN TOUR DE CALÈCHE';

  let cal = null;          // { s, attente, tours, visite }
  let chemin = null;       // la boucle, en pixels : [{ x, y, s }], et sa longueur

  function construireChemin(d) {
    const pts = d.caleche.chemin.map(function (p) { return { x: p[0] * TT, y: p[1] * TT }; });
    let s = 0;
    pts[0].s = 0;
    for (let i = 1; i < pts.length; i++) { s += Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y); pts[i].s = s; }
    return { pts: pts, longueur: s, def: d.caleche };
  }

  /** Le point du sentier a l'abscisse `s` (bouclee), et le cap du troncon. */
  function point(s) {
    const c = chemin, L = c.longueur;
    s = ((s % L) + L) % L;
    for (let i = 1; i < c.pts.length; i++) {
      const a = c.pts[i - 1], b = c.pts[i];
      if (s <= b.s) {
        const k = (s - a.s) / ((b.s - a.s) || 1);
        return { x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k, a: Math.atan2(b.y - a.y, b.x - a.x) };
      }
    }
    const z = c.pts[c.pts.length - 1];
    return { x: z.x, y: z.y, a: 0 };
  }

  /** Le cap dessine : est, ouest, nord ou sud. */
  function sens(a) {
    const c = Math.cos(a), s = Math.sin(a);
    if (Math.abs(c) >= Math.abs(s)) return c >= 0 ? 'est' : 'ouest';
    return s >= 0 ? 'sud' : 'nord';
  }

  /** La caleche et ses chevaux, maintenant : ou, dans quel sens, et si elle roule. */
  function caleche() {
    if (!cal || !chemin) return null;
    const p = point(cal.s), c = point(cal.s + CHEVAUX.avance);
    return { x: p.x, y: p.y, a: p.a, sens: sens(p.a), chevaux: { x: c.x, y: c.y, a: c.a, sens: sens(c.a) },
             roule: cal.attente <= 0, s: cal.s, tours: cal.tours };
  }

  /** Une visite neuve (on vient d'arriver au rang) : la caleche est a son arret, et les gens a leur place. */
  function nouvelleVisite(d) {
    chemin = construireChemin(d);
    cal = { s: 0, attente: d.caleche.attente, tours: 0, visite: B.bloc, gens: false };
  }

  function majCaleche() {
    const d = chemin.def;
    const j = B.joueur, aBord = !!(j && j.manege && j.manege.quoi === 'caleche');
    if (cal.attente > 0) {
      // ⚠️ Hors des heures, le cocher est couche : elle attend a l'arret — sauf s'il y a quelqu'un a bord.
      if (heures() || aBord) cal.attente--;
      return;
    }
    cal.s += d.vitesse;
    if (cal.s >= chemin.longueur) {
      cal.s = 0; cal.attente = d.attente; cal.tours++;
    }
  }

  /** Debout, libre, pres de l'arriere de la caleche arretee : on peut monter. */
  function calecheSousLaMain(j) {
    if (!ici() || !cal || cal.attente <= 0 || !heures()) return false;
    if (!j || !j.vivant || j.manege || j.dansVehicule || j.aBord || j.enjambe) return false;
    const c = caleche(), arriere = { x: c.x - Math.cos(c.a) * CAISSE.l, y: c.y - Math.sin(c.a) * CAISSE.l };
    return Math.hypot(j.x - arriere.x, j.y - arriere.y) <= PORTEE_MONTER || Math.hypot(j.x - c.x, j.y - c.y) <= PORTEE_MONTER;
  }

  //: Ou l'on s'assoit : le banc du fond, a gauche (en pixels, le long de la caleche et en travers).
  const SIEGE = { u: -12, v: 0 };

  function siege() {
    const c = caleche();
    const ca = Math.cos(c.a), sa = Math.sin(c.a);
    return { x: c.x + ca * SIEGE.u - sa * SIEGE.v, y: c.y + sa * SIEGE.u + ca * SIEGE.v };
  }

  function monter(j) {
    if (B.recherche && B.recherche.etoiles > 0) {
      Hud.message('LE COCHER NE T’ATTEND PAS', 120);
      if (Son.SFX && Son.SFX.erreur) Son.SFX.erreur();
      return true;
    }
    j.manege = { quoi: 'caleche', tours: cal.tours, monteT: B.t, z: 0 };
    j.dessine = false; j.vx = 0; j.vy = 0;
    const s = siege();
    j.x = s.x; j.y = s.y;
    // ⚠️ On part tout de suite, ou presque : le cocher n'attend pas un deuxieme client.
    cal.attente = Math.min(cal.attente, 60);
    Hud.message('LA CALÈCHE — UN TOUR DE L’ÉRABLIÈRE', 150);
    return true;
  }

  /** Descendre, de retour a l'arret : a cote de la caleche, du cote de la cabane. `force` : ailleurs. */
  function descendre(j, force) {
    if (!j || !j.manege || j.manege.quoi !== 'caleche') return false;
    if (!force) {
      const c = caleche();
      j.x = c.x; j.y = c.y - CAISSE.w - 8;
      Hud.message('LA CALÈCHE — MERCI, BONNE CABANE!', 120);
    }
    j.manege = null;
    j.dessine = true; j.vx = 0; j.vy = 0;
    j.descenduT = B.t;
    Entites.dansLaCarte(j);
    return true;
  }

  function majPassager() {
    const j = B.joueur, m = j && j.manege;
    if (!m || m.quoi !== 'caleche') return;
    if (!j.vivant || !ici()) { descendre(j, true); return; }
    const s = siege();
    j.x = s.x; j.y = s.y; j.vx = 0; j.vy = 0;
    if (cal.tours > m.tours && cal.attente > 0) descendre(j, false);
  }

  /** On ne passe pas au travers de la caleche ni des chevaux (comme le petit train de la foire). */
  function bloquer(e) {
    if (!cal || !chemin || !ici() || e.manege || (e.type !== 'joueur' && e.type !== 'pieton')) return;
    const c = caleche();
    const boites = [{ x: c.x, y: c.y, a: c.a, l: CAISSE.l, w: CAISSE.w },
                    { x: c.chevaux.x, y: c.chevaux.y, a: c.chevaux.a, l: CHEVAUX.l, w: CHEVAUX.w }];
    for (const b of boites) {
      const ca = Math.cos(b.a), sa = Math.sin(b.a), dx = e.x - b.x, dy = e.y - b.y;
      if (Math.abs(dx) > 40 || Math.abs(dy) > 40) continue;
      let lx = dx * ca + dy * sa, ly = -dx * sa + dy * ca;
      const px = b.l + e.r - Math.abs(lx), py = b.w + e.r - Math.abs(ly);
      if (px <= 0 || py <= 0) continue;
      if (px < py) lx = (lx < 0 ? -1 : 1) * (b.l + e.r);
      else ly = (ly < 0 ? -1 : 1) * (b.w + e.r);
      e.x = b.x + lx * ca - ly * sa;
      e.y = b.y + lx * sa + ly * ca;
    }
  }

  // --- La table de tire -------------------------------------------------------------------------

  function tableSousLaMain(j) {
    const d = def();
    if (!ici() || !d || !d.table || !j || j.manege || j.dansVehicule) return false;
    const tx = d.table.x * TT + 8, ty = d.table.y * TT + 12;
    return Math.abs(j.x - tx) < 30 && Math.abs(j.y - ty) < 22;
  }

  function defiDeLaTire() { return ((B.defs && B.defs.defis) || []).find(function (q) { return q.slug === 'tire'; }) || null; }

  function inviteTable(j) {
    if (!tableSousLaMain(j)) return null;
    return onFaitBouillir() ? 'LA TIRE SUR LA NEIGE' : 'LA TABLE DE TIRE';
  }

  /** ACTION devant la table : au temps des sucres, le defi de la tire ; sinon, on le dit. */
  function toucherLaTable(j) {
    const d = defiDeLaTire();
    if (!onFaitBouillir()) {
      const c = B.defs.comptoirs && B.defs.comptoirs.sucre;
      Hud.message(temps() ? 'LE TIREUR EST COUCHÉ — REVIENS À ' + Math.round(((c && c.heures) || [7 / 24])[0] * 24) + ' H'
        : ((c && c.hors_saison) || 'FERMÉ'), 150);
      return true;
    }
    if (d && !B.defi && Histoire.defiOuvert(d)) return Histoire.proposerDefi(d.slug) || true;
    Hud.message('LA TIRE — ELLE SE GAGNE PLUS TARD (TROIS DÉFIS D’ABORD)', 150);
    return true;
  }

  function sousLaMain(j) { return tableSousLaMain(j) ? 'table' : calecheSousLaMain(j) ? 'caleche' : null; }
  function invite(j) {
    const t = inviteTable(j);
    if (t) return t;
    return calecheSousLaMain(j) ? INVITE : null;
  }
  function agir(j) {
    if (tableSousLaMain(j)) return toucherLaTable(j);
    if (calecheSousLaMain(j)) return monter(j);
    return false;
  }

  // --- Les gens -------------------------------------------------------------------------------

  /** `fn` sans toucher au de du jeu : `B.rng` est prete, tire a l'empreinte de `graine`. */
  function sansDe(graine, fn) {
    const rng = B.rng;
    let k = 0;
    B.rng = function () { return (hash2(graine, k++) % 10007) / 10007; };
    try { return fn(); } finally { B.rng = rng; }
  }

  function gens() { return B.entites.filter(function (e) { return e.type === 'pieton' && e.cabane; }); }

  function majGens(d) {
    const les = gens();
    if (!onFaitBouillir()) {
      // Ils rentrent a la fermeture — hors de la vue : personne ne s'evapore sous nos yeux.
      for (const e of les) if (!Entites.visibleAEcran(e.x, e.y, 24)) Entites.retirer(e);
      return;
    }
    if (cal.gens) return;
    cal.gens = true;
    if (les.length) return;
    d.gens.forEach(function (g, k) {
      sansDe(0xCAB0 + k, function () {
        const arch = Entites.archetype(g.arch);
        const e = Entites.creerPieton(g.x * TT + 8, g.y * TT + 10, arch);
        e.cabane = g.qui;
        e.etat = 'fige'; e.plante = { x: e.x, y: e.y }; e.face = g.face || 'bas';
        e.vx = 0; e.vy = 0;
        // Le musicien de la cabane joue le reel (`musique.RUE`) : un air de danse, pour la cabane.
        if (g.qui === 'musicien') e.toune = 'rue_reel';
        if (g.qui === 'tireur') e.poste = { x: e.x, y: e.y };
      });
    });
    Entites.indexer();
  }

  function maj() {
    if (!ici()) { if (cal) cal = null; return; }
    const d = def();
    if (!cal || cal.visite !== B.bloc) nouvelleVisite(d);
    majCaleche();
    majPassager();
    majGens(d);
    // La table de tire : ses rubans s'allongent quand on fait bouillir ; sinon, la neige toute propre.
    const t = d.table;
    if (t) {
      for (const e of Entites.decorAutour(t.x * TT + 8, t.y * TT + 15, 6)) {
        if (e.decor !== 'table_tire') continue;
        if (onFaitBouillir()) delete e.poseManuelle; else e.poseManuelle = 0;
      }
    }
  }

  // --- Le dessin ------------------------------------------------------------------------------

  //: Le bleu de la tubulure, et le noir du tuyau maitre.
  const BLEU = '#2f86d6', BLEU_OMBRE = '#1d5a94', MAITRE = '#1c2e44';

  /** Le chalumeau d'un erable en tubulure, dans le monde (voir `DECORS.erable_tube`). */
  function chalumeau(e) { return { x: e.x + 3, y: e.y - 8 }; }

  let tubes = null;        // les segments, calcules une fois par visite : [[x0, y0, x1, y1, maitre]]

  function calculerTubes(d) {
    const arbres = B.entites.filter(function (e) { return e.type === 'decor' && e.decor === 'erable_tube'; });
    const xm = d.tubulure.x * TT + 8, segs = [];
    const rangs = {};
    for (const e of arbres) (rangs[e.y] = rangs[e.y] || []).push(e);
    Object.keys(rangs).forEach(function (y) {
      const r = rangs[y].slice().sort(function (a, b) { return a.x - b.x; });
      // Chaque cote du maitre court vers lui, d'arbre en arbre, en descendant un peu (la pente de la tubulure).
      const ouest = r.filter(function (e) { return e.x < xm; }), est = r.filter(function (e) { return e.x > xm; }).reverse();
      for (const cote of [ouest, est]) {
        for (let i = 0; i < cote.length; i++) {
          const a = chalumeau(cote[i]), b = i + 1 < cote.length ? chalumeau(cote[i + 1]) : { x: xm, y: a.y + 3 };
          segs.push([a.x, a.y, b.x, b.y, false]);
        }
      }
    });
    // Le tuyau maitre : du premier rang jusqu'au toit de la cabane.
    segs.push([xm, d.tubulure.de * TT + 4, xm, d.tubulure.a * TT + 2, true]);
    return segs;
  }

  /** La tubulure, sous les gens et les arbres (les troncs la cachent ou elle y entre). */
  function dessinerSol(ctx, cam) {
    const d = def();
    if (!ici() || !d) return;
    if (!tubes || tubes.visite !== B.bloc) { tubes = calculerTubes(d); tubes.visite = B.bloc; }
    for (const s of tubes) {
      if (Math.max(s[0], s[2]) < cam.x - 8 || Math.min(s[0], s[2]) > cam.x + VW + 8) continue;
      if (Math.max(s[1], s[3]) < cam.y - 8 || Math.min(s[1], s[3]) > cam.y + VH + 8) continue;
      const n = Math.max(1, Math.round(Math.max(Math.abs(s[2] - s[0]), Math.abs(s[3] - s[1]))));
      ctx.fillStyle = 'rgba(20,18,26,0.16)';                         // son ombre, au sol, plus bas
      for (let k = 0; k <= n; k += 2) ctx.fillRect(Math.round(s[0] + (s[2] - s[0]) * k / n - cam.x), Math.round(s[1] + (s[3] - s[1]) * k / n - cam.y) + 7, 1, 1);
      for (let k = 0; k <= n; k++) {
        const x = Math.round(s[0] + (s[2] - s[0]) * k / n - cam.x), y = Math.round(s[1] + (s[3] - s[1]) * k / n - cam.y);
        if (s[4]) { ctx.fillStyle = MAITRE; ctx.fillRect(x - 1, y, 3, 1); }
        else { ctx.fillStyle = BLEU; ctx.fillRect(x, y, 1, 1); ctx.fillStyle = BLEU_OMBRE; ctx.fillRect(x, y + 1, 1, 1); }
      }
      B.stats.rects += n;
    }
  }

  //: Les couleurs de ceux qui font deja le tour (des gens de la cabane), et le cocher a son chapeau.
  const PROMENEURS = [
    { c: '#c0392b', h: '#3b2a20', s: '#e8b088', p: '#2a2a3a' },
    { c: '#2e86c1', h: '#d8b36a', s: '#f0c9a0', p: '#3a4a6a' },
    { c: '#f1c40f', h: '#1b1b1f', s: '#8d5a3b', p: '#2a2a3a' },
    { c: '#8e44ad', h: '#7a4a2a', s: '#f0c9a0', p: '#3a4a6a' },
  ];
  const COCHER = { c: '#5a2d1a', h: '#1b1b1f', s: '#e8b088', p: '#2a2a3a' };

  function assis(tenue, face) {
    const cuit = Atlas.cuire('joueur', SPRITES.joueur, tenue);
    const p = cuit.poses['assis_' + face] || cuit.poses.assis_bas;
    return p ? { img: p[0], ancre: cuit.ancre } : null;
  }

  function peindreAssis(ctx, tenue, face, x, y) {
    const a = assis(tenue, face);
    if (!a) return;
    ctx.drawImage(a.img, Math.round(x - a.ancre[0]), Math.round(y - a.ancre[1]));
    B.stats.images++;
  }

  /** Une roue de bois, de profil : la jante, deux rayons qui tournent avec le chemin fait. */
  function roue(ctx, cx, cy, r, tour) {
    ctx.fillStyle = '#2a1d12';
    for (let k = 0; k < 16; k++) {
      const t = k / 16 * Math.PI * 2;
      ctx.fillRect(Math.round(cx + Math.cos(t) * r), Math.round(cy + Math.sin(t) * r), 1, 1);
    }
    ctx.fillStyle = '#8a6a3a';
    for (let k = 0; k < 2; k++) {
      const t = tour + k * Math.PI / 2;
      for (let q = -r + 1; q <= r - 1; q++) ctx.fillRect(Math.round(cx + Math.cos(t) * q), Math.round(cy + Math.sin(t) * q), 1, 1);
    }
    ctx.fillStyle = '#1b1410'; ctx.fillRect(Math.round(cx) - 1, Math.round(cy) - 1, 2, 2);
    B.stats.rects += 20;
  }

  /** La caleche, de profil, tournee vers l'est (`ox, oy` : son milieu au sol, a l'ecran ; la ville la peint
      en miroir vers l'ouest). Les gens assis dedans : trois promeneurs (le joueur au banc du fond s'il y est),
      et le cocher sur son siege haut, devant. */
  function peindreCaisseProfil(ctx, ox, oy, c, lui) {
    const tour = c.s / 5.5;
    ctx.fillStyle = 'rgba(20,18,26,0.28)'; ctx.fillRect(ox - 21, oy - 2, 44, 4);        // l'ombre
    // Les gens d'abord : on les voit par-dessus les ridelles.
    [-14, -7, 0].forEach(function (u, i) {
      const tenue = lui && i === 0 ? (B.joueur.swaps || {}) : PROMENEURS[(i + (c.tours || 0)) % PROMENEURS.length];
      peindreAssis(ctx, tenue, 'droite', ox + u, oy - 9);
    });
    if (c.cocher) peindreAssis(ctx, COCHER, 'droite', ox + 13, oy - 14);
    // La caisse : rouge, bordee de brun, son filet dore ; devant, le siege du cocher et son garde-boue.
    ctx.fillStyle = '#5a1a14'; ctx.fillRect(ox - 20, oy - 16, 30, 10);
    ctx.fillStyle = '#a8322a'; ctx.fillRect(ox - 19, oy - 15, 28, 8);
    ctx.fillStyle = '#c9483c'; ctx.fillRect(ox - 19, oy - 15, 28, 1);
    ctx.fillStyle = '#e8c070'; ctx.fillRect(ox - 17, oy - 12, 24, 1); ctx.fillRect(ox - 17, oy - 9, 24, 1);
    ctx.fillStyle = '#5a1a14'; ctx.fillRect(ox + 10, oy - 19, 7, 12);                     // le siege du cocher
    ctx.fillStyle = '#7a2a20'; ctx.fillRect(ox + 11, oy - 18, 5, 10);
    ctx.fillStyle = '#1b1b1f'; ctx.fillRect(ox + 17, oy - 12, 4, 1); ctx.fillRect(ox + 20, oy - 12, 1, 4);   // le garde-boue
    ctx.fillStyle = '#3a2413'; ctx.fillRect(ox - 20, oy - 7, 38, 2);                     // le chassis
    ctx.fillStyle = '#4a3218'; ctx.fillRect(ox + 17, oy - 9, 11, 1);                     // le brancard, vers les chevaux
    roue(ctx, ox - 12, oy - 5.5, 5.5, tour);
    roue(ctx, ox + 12, oy - 4.5, 4.5, tour * 1.2);
    B.stats.rects += 14;
  }

  /** La caleche de dos (vers le nord) ou de face (vers le sud) : le plancher et ses bancs vus d'en haut, les
      roues de chaque cote, et le panneau du bout qui est vers nous. */
  function peindreCaisseDebout(ctx, ox, oy, c, lui, versLeNord) {
    ctx.fillStyle = 'rgba(20,18,26,0.28)'; ctx.fillRect(ox - 12, oy - 20, 26, 42);
    const ray = Math.floor(c.s / 3) % 4;
    const roues = [[-14, -18], [12, -18], [-14, 6], [12, 6]];
    for (const [dx, dy] of roues) {
      ctx.fillStyle = '#2a1d12'; ctx.fillRect(ox + dx, oy + dy, 2, 11);
      ctx.fillStyle = '#8a6a3a'; ctx.fillRect(ox + dx, oy + dy + 1 + ray * 2, 2, 1); ctx.fillRect(ox + dx, oy + dy + 9 - ray * 2, 2, 1);
    }
    ctx.fillStyle = '#5a1a14'; ctx.fillRect(ox - 11, oy - 22, 23, 40);                   // les ridelles
    ctx.fillStyle = '#8a5a2b'; ctx.fillRect(ox - 10, oy - 21, 21, 38);                    // le plancher
    ctx.fillStyle = '#7a4c24'; for (let k = 0; k < 9; k++) ctx.fillRect(ox - 10, oy - 19 + k * 4, 21, 1);
    ctx.fillStyle = '#a8322a'; ctx.fillRect(ox - 11, oy - 22, 2, 40); ctx.fillRect(ox + 10, oy - 22, 2, 40);
    B.stats.rects += 14;
    const face = versLeNord ? 'haut' : 'bas';
    // Du haut de l'ecran vers le bas : ce qui est plus au sud cache ce qui est derriere.
    const bancs = versLeNord ? ['cocher', 1, 2] : [2, 1, 'cocher'];
    const ys = versLeNord ? [-14, -2, 10] : [-12, 0, 12];
    bancs.forEach(function (qui, k) {
      const y = oy + ys[k];
      ctx.fillStyle = '#3a2413'; ctx.fillRect(ox - 9, y - 2, 19, 2);
      if (qui === 'cocher') { if (c.cocher) peindreAssis(ctx, COCHER, face, ox, y); return; }
      const a = PROMENEURS[(qui + (c.tours || 0)) % 4], b = PROMENEURS[(qui + 2 + (c.tours || 0)) % 4];
      if (qui === 2) { peindreAssis(ctx, lui ? (B.joueur.swaps || {}) : a, face, ox - 4, y); return; }
      peindreAssis(ctx, a, face, ox - 4, y); peindreAssis(ctx, b, face, ox + 5, y);
    });
    // Le panneau du bout qu'on voit, en bas : rouge, filet dore.
    ctx.fillStyle = '#5a1a14'; ctx.fillRect(ox - 11, oy + 15, 23, 6);
    ctx.fillStyle = '#a8322a'; ctx.fillRect(ox - 10, oy + 16, 21, 4);
    ctx.fillStyle = '#e8c070'; ctx.fillRect(ox - 8, oy + 17, 17, 1);
    if (!versLeNord) { ctx.fillStyle = '#4a3218'; ctx.fillRect(ox - 1, oy + 21, 2, 8); }  // le timon, vers les chevaux
    B.stats.rects += 6;
  }

  //: Les robes des deux chevaux : un bai et un alezan, criniere et queue noires.
  const ROBES = [{ corps: '#7a4a26', ombre: '#5a3418', crin: '#241610', bas: '#1e140e' },
                 { corps: '#9a5a2a', ombre: '#6e3e1c', crin: '#3a2012', bas: '#2a1a10' }];

  /** Un cheval de profil, tourne vers l'est (`x, y` : sous son ventre, au sol). Le trot : les pattes par
      paires diagonales, levees une image sur deux ; la tete qui hoche ; la queue qui balance. */
  function cheval(ctx, x, y, robe, pas, roule) {
    const leve = roule ? pas % 2 : -1, hoche = roule ? (pas % 2) : 0;
    ctx.fillStyle = 'rgba(20,18,26,0.25)'; ctx.fillRect(x - 9, y - 1, 20, 2);
    // Les pattes : arriere (-6, -3), avant (4, 7). Paires diagonales : (-6, 7) et (-3, 4).
    const pattes = [[-6, 0], [-3, 1], [4, 1], [7, 0]];
    for (const [px, paire] of pattes) {
      const haut = paire === leve ? 2 : 0;
      ctx.fillStyle = robe.ombre; ctx.fillRect(x + px, y - 9, 2, 8 - haut);
      ctx.fillStyle = robe.bas; ctx.fillRect(x + px + (haut ? 1 : 0), y - 2 - haut, 2, 2);          // le sabot
    }
    ctx.fillStyle = robe.corps; ctx.fillRect(x - 8, y - 15, 17, 7);                                     // le corps
    ctx.fillStyle = robe.ombre; ctx.fillRect(x - 8, y - 10, 17, 2);                                     // le ventre
    ctx.fillStyle = robe.corps; ctx.fillRect(x + 6, y - 19 + hoche, 4, 7);                               // l'encolure
    ctx.fillRect(x + 8, y - 21 + hoche, 5, 4);                                                           // la tete
    ctx.fillStyle = robe.ombre; ctx.fillRect(x + 12, y - 19 + hoche, 2, 3);                              // le bout du nez
    ctx.fillStyle = robe.crin; ctx.fillRect(x + 6, y - 21 + hoche, 2, 6); ctx.fillRect(x + 8, y - 22 + hoche, 1, 1);   // criniere, oreille
    ctx.fillStyle = '#0d0906'; ctx.fillRect(x + 10, y - 20 + hoche, 1, 1);                               // l'oeil
    const q = roule ? (pas % 4 < 2 ? 0 : 1) : 0;
    ctx.fillStyle = robe.crin; ctx.fillRect(x - 10, y - 15, 2, 2); ctx.fillRect(x - 11 + q, y - 13, 2, 6);   // la queue
    // Le harnais : le collier, la sellette et les traits qui filent vers la caleche.
    ctx.fillStyle = '#1b1b1f'; ctx.fillRect(x + 5, y - 16 + hoche, 2, 6); ctx.fillRect(x - 2, y - 15, 3, 7);
    ctx.fillStyle = '#c9a24a'; ctx.fillRect(x + 5, y - 13 + hoche, 1, 1);
    ctx.fillStyle = '#1b1b1f'; ctx.fillRect(x - 12, y - 11, 17, 1);
    B.stats.rects += 22;
  }

  /** Un cheval de dos (vers le nord) ou de face (vers le sud), debout (`x, y` : au sol, sous lui). */
  function chevalDebout(ctx, x, y, robe, pas, roule, versLeNord) {
    const leve = roule ? pas % 2 : -1;
    ctx.fillStyle = 'rgba(20,18,26,0.25)'; ctx.fillRect(x - 4, y - 1, 9, 2);
    // Deux pattes qu'on voit, qui se levent tour a tour.
    for (const [px, k] of [[-3, 0], [2, 1]]) {
      const haut = k === leve ? 2 : 0;
      ctx.fillStyle = robe.ombre; ctx.fillRect(x + px, y - 7, 2, 6 - haut);
      ctx.fillStyle = robe.bas; ctx.fillRect(x + px, y - 2 - haut, 2, 2);
    }
    if (versLeNord) {
      // La croupe ronde, la queue au milieu, le dos qui file vers le haut de l'ecran, la tete tout au bout.
      ctx.fillStyle = robe.corps; ctx.fillRect(x - 4, y - 22, 9, 16); ctx.fillRect(x - 3, y - 25, 7, 3);
      ctx.fillStyle = robe.ombre; ctx.fillRect(x + 3, y - 20, 2, 13);
      ctx.fillStyle = robe.crin; ctx.fillRect(x - 1, y - 30, 3, 8);                                    // la criniere
      ctx.fillRect(x - 2, y - 32, 1, 2); ctx.fillRect(x + 2, y - 32, 1, 2);                            // les oreilles
      const q = roule ? (pas % 4 < 2 ? -1 : 1) : 0;
      ctx.fillRect(x + q, y - 13, 2, 8);                                                               // la queue
      ctx.fillStyle = '#1b1b1f'; ctx.fillRect(x - 4, y - 17, 9, 1);                                    // l'avaloire
    } else {
      // De face : le poitrail, l'encolure, la tete longue et son liste blanc.
      ctx.fillStyle = robe.corps; ctx.fillRect(x - 4, y - 16, 9, 10);
      ctx.fillStyle = robe.ombre; ctx.fillRect(x + 3, y - 16, 2, 10);
      ctx.fillStyle = robe.corps; ctx.fillRect(x - 2, y - 26, 5, 11);
      ctx.fillStyle = '#efe6d0'; ctx.fillRect(x, y - 25, 1, 7);                                         // le liste
      ctx.fillStyle = robe.ombre; ctx.fillRect(x - 2, y - 17, 5, 2);                                    // le bout du nez
      ctx.fillStyle = '#0d0906'; ctx.fillRect(x - 2, y - 23, 1, 1); ctx.fillRect(x + 2, y - 23, 1, 1);   // les yeux
      ctx.fillStyle = robe.crin; ctx.fillRect(x - 2, y - 28, 1, 2); ctx.fillRect(x + 2, y - 28, 1, 2); ctx.fillRect(x, y - 27, 1, 2);
      ctx.fillStyle = '#1b1b1f'; ctx.fillRect(x - 4, y - 14, 9, 2);                                    // le collier
      ctx.fillStyle = '#c9a24a'; ctx.fillRect(x, y - 14, 1, 1);
    }
    B.stats.rects += 16;
  }

  /** Les deux chevaux, cote a cote, selon le sens ; `c` : la caleche (le trot suit le chemin fait). */
  function peindreChevaux(ctx, ox, oy, c) {
    const s = c.chevaux.sens, pas = Math.floor(c.s / 6), roule = c.roule;
    if (s === 'est' || s === 'ouest') {
      ctx.save();
      if (s === 'ouest') { ctx.translate(ox * 2, 0); ctx.scale(-1, 1); }
      cheval(ctx, ox - 1, oy - 3, ROBES[1], pas + 1, roule);           // celui d'en face, un peu plus haut
      cheval(ctx, ox, oy + 2, ROBES[0], pas, roule);
      ctx.restore();
      return;
    }
    const nord = s === 'nord';
    chevalDebout(ctx, ox - 5, oy + 3, ROBES[0], pas, roule, nord);
    chevalDebout(ctx, ox + 5, oy + 3, ROBES[1], pas + 1, roule, nord);
  }

  function peindreCaleche(ctx, ox, oy, c) {
    const j = B.joueur, lui = !!(j && j.manege && j.manege.quoi === 'caleche');
    if (c.sens === 'est' || c.sens === 'ouest') {
      ctx.save();
      if (c.sens === 'ouest') { ctx.translate(ox * 2, 0); ctx.scale(-1, 1); }
      peindreCaisseProfil(ctx, ox, oy, c, lui);
      ctx.restore();
    } else peindreCaisseDebout(ctx, ox, oy, c, lui, c.sens === 'nord');
  }

  /** La pancarte de l'arret : CALÈCHE, sur deux poteaux. */
  function peindrePancarte(ctx, x, y) {
    const TEXTE = 'CALÈCHE', large = Atlas.largeurTexte(TEXTE) + 6, x0 = Math.round(x - large / 2);
    ctx.fillStyle = '#4a3218'; ctx.fillRect(x0 + 2, y - 16, 1, 17); ctx.fillRect(x0 + large - 3, y - 16, 1, 17);
    ctx.fillStyle = '#4a3218'; ctx.fillRect(x0, y - 22, large, 9);
    ctx.fillStyle = '#8a5a2b'; ctx.fillRect(x0 + 1, y - 21, large - 2, 7);
    Atlas.texte(ctx, TEXTE, x0 + 3, y - 20, '#f4e4c1');
    B.stats.rects += 5;
  }

  //: Un numero de tri hors de portee de ceux des entites (voir `Foire.ajouterVisibles`), et de ceux de la foire.
  const ID_TRI = 910000000;

  /** Ce qui se trie avec les entites : la caleche, ses chevaux, la pancarte. */
  function ajouterVisibles(visibles, cx, cy) {
    if (!ici() || !cal || !chemin) return;
    const c = caleche();
    c.cocher = heures() || c.roule;
    const d = chemin.def;
    const dans = function (x, y) { return x > cx - 48 && x < cx + VW + 48 && y > cy - 48 && y < cy + VH + 48; };
    if (dans(c.x, c.y)) {
      visibles.push({ id: ID_TRI, vivant: true, x: c.x, y: c.y + CAISSE.w,
                      peindreFoire: function (ctx) { peindreCaleche(ctx, Math.round(c.x - cx), Math.round(c.y - cy), c); } });
    }
    if (dans(c.chevaux.x, c.chevaux.y)) {
      visibles.push({ id: ID_TRI + 1, vivant: true, x: c.chevaux.x, y: c.chevaux.y + 3,
                      peindreFoire: function (ctx) { peindreChevaux(ctx, Math.round(c.chevaux.x - cx), Math.round(c.chevaux.y - cy), c); } });
    }
    if (d.pancarte) {
      const px = d.pancarte[0] * TT + 8, py = d.pancarte[1] * TT + 14;
      if (dans(px, py)) visibles.push({ id: ID_TRI + 2, vivant: true, x: px, y: py,
                                        peindreFoire: function (ctx) { peindrePancarte(ctx, Math.round(px - cx), Math.round(py - cy)); } });
    }
  }

  return { ici, temps, heures, onFaitBouillir, maj, caleche, sousLaMain, invite, agir, monter, descendre, bloquer,
           dessinerSol, ajouterVisibles, gens, tableSousLaMain, calecheSousLaMain, chalumeau, sansDe,
           get chemin() { return chemin; }, get etat() { return cal; }, CAISSE, CHEVAUX, SIEGE, INVITE };
})();
