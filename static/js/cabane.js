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
  const CHEVAUX = { avance: 38, l: 12, w: 9 };
  //: A quelle distance de la caisse (ou des chevaux) on peut y monter, de n'importe quel cote. En pixels.
  //: ⚠️ Martin (28 sept. 2026) : « je ne peux plus embarquer » — debout pres des chevaux, il etait trop loin de
  //: l'ARRIERE, la seule place ou l'on montait, et rien ne le disait.
  const PORTEE_MONTER = 16;
  //: Ou, pres de l'arret, on apprend que la calèche n'est pas la (autour de la pancarte et de son arret).
  const PORTEE_ARRET = 44;
  const INVITE = 'UN TOUR DE CALÈCHE';
  //: LES VIRAGES (Martin, 28 sept. 2026 : « comme un vrai vehicule ») : le rayon des coins du sentier, et ou
  //: sont les essieux de part et d'autre du milieu de la caisse. En pixels.
  //: ⚠️ La caisse ne suit pas le sentier, elle est TIREE : ses deux essieux roulent dessus, et elle va de l'un a
  //: l'autre — dans un coin, les chevaux tournent d'abord, la caisse pivote apres eux et coupe un peu le virage,
  //: comme une vraie voiture attelee. Les chevaux, de meme, d'un bout a l'autre de leur longueur.
  const RAYON = 40;
  const ESSIEUX = 12;

  let cal = null;          // { s, attente, tours, visite }
  let chemin = null;       // la boucle, en pixels : [{ x, y, s }], et sa longueur

  /** La boucle du sentier, en pixels, ses coins arrondis en arcs de `RAYON` (un point tous les deux pixels). */
  function construireChemin(d) {
    const coins = d.caleche.chemin.map(function (p) { return { x: p[0] * TT, y: p[1] * TT }; });
    const pts = [coins[0]];
    for (let i = 1; i < coins.length - 1; i++) {
      const a = coins[i - 1], b = coins[i], c = coins[i + 1];
      const l1 = Math.hypot(b.x - a.x, b.y - a.y), l2 = Math.hypot(c.x - b.x, c.y - b.y);
      const u1 = { x: (b.x - a.x) / l1, y: (b.y - a.y) / l1 }, u2 = { x: (c.x - b.x) / l2, y: (c.y - b.y) / l2 };
      const phi = Math.atan2(u1.x * u2.y - u1.y * u2.x, u1.x * u2.x + u1.y * u2.y);
      if (Math.abs(phi) < 1e-3) { pts.push(b); continue; }
      // Le coin se coupe a `t` de part et d'autre, jamais plus loin que la moitie d'un troncon.
      const t = Math.min(RAYON * Math.tan(Math.abs(phi) / 2), l1 / 2, l2 / 2), r = t / Math.tan(Math.abs(phi) / 2);
      const p1 = { x: b.x - u1.x * t, y: b.y - u1.y * t };
      let nx = -u1.y, ny = u1.x;
      if (nx * u2.x + ny * u2.y < 0) { nx = -nx; ny = -ny; }
      const cx = p1.x + nx * r, cy = p1.y + ny * r, a0 = Math.atan2(p1.y - cy, p1.x - cx);
      const n = Math.max(2, Math.ceil(r * Math.abs(phi) / 2));
      for (let k = 0; k <= n; k++) pts.push({ x: cx + Math.cos(a0 + phi * k / n) * r, y: cy + Math.sin(a0 + phi * k / n) * r });
    }
    pts.push(coins[coins.length - 1]);
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

  /** Ce qui roule d'un point du sentier a un autre (`s - demi` derriere, `s + demi` devant) : son milieu, et
      son cap de l'un a l'autre. */
  function tire(s, demi) {
    const ar = point(s - demi), av = point(s + demi);
    return { x: (ar.x + av.x) / 2, y: (ar.y + av.y) / 2, a: Math.atan2(av.y - ar.y, av.x - ar.x) };
  }

  /** La caleche et ses chevaux, maintenant : ou, dans quel cap, et si elle roule. `null` : elle n'est pas la
      (la cabane est fermee, voir `majCaleche`). */
  function caleche() {
    if (!cal || !chemin || cal.absente) return null;
    const p = tire(cal.s, ESSIEUX), c = tire(cal.s + CHEVAUX.avance, CHEVAUX.l * 0.6);
    return { x: p.x, y: p.y, a: p.a, chevaux: { x: c.x, y: c.y, a: c.a },
             roule: cal.attente <= 0, s: cal.s, tours: cal.tours };
  }

  /** Une visite neuve (on vient d'arriver au rang) : la caleche est a son arret, et les gens a leur place. */
  function nouvelleVisite(d) {
    chemin = construireChemin(d);
    cal = { s: 0, attente: d.caleche.attente, tours: 0, visite: B.bloc, gens: false, absente: !onFaitBouillir() };
  }

  /** La caleche ou ses chevaux sont-ils a l'ecran ? */
  function enVue() {
    const p = tire(cal.s, ESSIEUX), c = tire(cal.s + CHEVAUX.avance, CHEVAUX.l * 0.6);
    return Entites.visibleAEcran(p.x, p.y, 48) || Entites.visibleAEcran(c.x, c.y, 48);
  }

  function majCaleche() {
    const d = chemin.def;
    const j = B.joueur, aBord = !!(j && j.manege && j.manege.quoi === 'caleche');
    // LA CABANE FERMEE, PAS DE CALECHE (Martin, 28 sept. 2026 : « la caleche devrait etre absente si fermee ») :
    // hors des heures du comptoir et hors du temps des sucres, comme les gens de la cabane. Elle s'en va et revient
    // a son arret, HORS DE LA VUE — personne ne s'evapore sous nos yeux —, et un tour commence se finit.
    if (cal.attente > 0 && !aBord && cal.absente === onFaitBouillir() && !enVue()) cal.absente = !cal.absente;
    if (cal.absente) return;
    if (cal.attente > 0) {
      if (onFaitBouillir() || aBord) cal.attente--;
      return;
    }
    cal.s += d.vitesse;
    if (cal.s >= chemin.longueur) {
      cal.s = 0; cal.attente = d.attente; cal.tours++;
    }
  }

  /** A combien de pixels du bord d'une boite orientee (`x, y, a, l, w`) est ce point (0 : dedans). */
  function horsDe(b, x, y) {
    const ca = Math.cos(b.a), sa = Math.sin(b.a), dx = x - b.x, dy = y - b.y;
    return Math.hypot(Math.max(0, Math.abs(dx * ca + dy * sa) - b.l), Math.max(0, Math.abs(-dx * sa + dy * ca) - b.w));
  }

  /** Debout, libre, a cote de la caleche arretee — n'importe quel cote, les chevaux compris : on peut monter. */
  function calecheSousLaMain(j) {
    if (!ici() || !cal || cal.attente <= 0 || !onFaitBouillir()) return false;
    if (!j || !j.vivant || j.manege || j.dansVehicule || j.aBord || j.enjambe) return false;
    const c = caleche();
    if (!c) return false;
    return horsDe({ x: c.x, y: c.y, a: c.a, l: CAISSE.l, w: CAISSE.w }, j.x, j.y) <= PORTEE_MONTER ||
           horsDe({ x: c.chevaux.x, y: c.chevaux.y, a: c.chevaux.a, l: CHEVAUX.l, w: CHEVAUX.w }, j.x, j.y) <= PORTEE_MONTER;
  }

  /** La cabane fermee, a l'arret (pres de la pancarte, ou de la caleche qui n'est pas encore partie) : ce qu'on en
      dit — quand le cocher attelle. `null` : ouverte, ou pas pres de l'arret. */
  function calecheFermee(j) {
    if (!ici() || !cal || !chemin || onFaitBouillir() || !j || j.manege || j.dansVehicule) return null;
    const p = pancarte(), arret = point(0);
    const pres = Math.hypot(j.x - arret.x, j.y - arret.y) <= PORTEE_ARRET ||
                 (p && Math.hypot(j.x - (p.x0 + p.large / 2), j.y - p.y) <= PORTEE_ARRET);
    if (!pres) return null;
    if (!temps()) return 'PAS DE CALÈCHE — ON ATTELLE AU TEMPS DES SUCRES';
    const c = B.defs && B.defs.comptoirs && B.defs.comptoirs.sucre;
    return 'PAS DE CALÈCHE — LE COCHER ATTELLE À ' + Math.round(((c && c.heures) || [7 / 24])[0] * 24) + ' H';
  }

  //: Ou l'on s'assoit : le banc du fond, a gauche (en pixels, le long de la caleche et en travers) — la premiere
  //: place des bancs de `CABANE_EN_VOLUME`, ou le joueur se peint.
  const SIEGE = { u: -14, v: -4.2 };

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
    const ch = caleche().chevaux;
    Son.SFX.hennissement(ch.x, ch.y);            // les chevaux savent qu'on part
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
    if (!c) return;
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

  function sousLaMain(j) {
    return tableSousLaMain(j) ? 'table' : calecheSousLaMain(j) ? 'caleche' : calecheFermee(j) ? 'arret' : null;
  }
  function invite(j) {
    const t = inviteTable(j);
    if (t) return t;
    return calecheSousLaMain(j) ? INVITE : calecheFermee(j);
  }
  function agir(j) {
    if (tableSousLaMain(j)) return toucherLaTable(j);
    if (calecheSousLaMain(j)) return monter(j);
    const fermee = calecheFermee(j);
    if (fermee) { Hud.message(fermee, 150); return true; }
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
        // Le musicien de la cabane est un violoneux (`musique.VIOLON`, 28 sept. 2026) : son reel à lui.
        if (g.qui === 'musicien') e.toune = 'cabane_violon';
        if (g.qui === 'tireur') e.poste = { x: e.x, y: e.y };
      });
    });
    Entites.indexer();
  }

  //: Jusqu'où s'entendent la calèche qui roule et l'évaporateur, en pixels.
  const PORTEE_SONS = { caleche: 360, evaporateur: 260 };

  /** LES SONS DU RANG : la calèche qui roule (ses sabots, ses grelots), dosée à la distance, et
      l'évaporateur qui bout — au plus fort DANS la cabane, au temps des sucres. Hors du rang, tout se tait. */
  function majSons() {
    const j = B.joueur;
    const dansLaCabane = !!(B.bloc && B.interieur && B.interieur.slug === 'cabane');
    if (!j || !ici()) {
      Son.SFX.caleche(0);
      Son.SFX.evaporateur(dansLaCabane && onFaitBouillir() ? 1 : 0);
      return;
    }
    Son.Lieu.charger('cabane');               // ses sons, une fois, en arrivant au rang
    const c = caleche();
    const aBord = !!(j.manege && j.manege.quoi === 'caleche');
    const dc = c ? Math.hypot(j.x - c.chevaux.x, j.y - c.chevaux.y) : Infinity;
    Son.SFX.caleche(c && c.roule ? (aBord ? 0.8 : Math.max(0, 1 - dc / PORTEE_SONS.caleche)) : 0);
    const porte = (Monde.carte.def.portes || []).find(function (p) { return p.lieu === 'cabane'; });
    const de = porte ? Math.hypot(j.x - (porte.x * TT + 8), j.y - (porte.y * TT + 8)) : Infinity;
    Son.SFX.evaporateur(onFaitBouillir() ? Math.max(0, 1 - de / PORTEE_SONS.evaporateur) * 0.6 : 0);
  }

  function maj() {
    if (!ici()) { if (cal) cal = null; majSons(); return; }
    const d = def();
    if (!cal || cal.visite !== B.bloc) nouvelleVisite(d);
    majCaleche();
    majPassager();
    majGens(d);
    majSons();
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

  //: Qui est assis ou, sur les six places des bancs (`CABANE_EN_VOLUME`, du fond a gauche jusqu'au banc de devant
  //: a droite) : un promeneur, ou personne (`null`). La premiere est la place du joueur quand il fait le tour.
  const PLACES = [0, null, 1, 2, null, 3];

  //: Les bancs, prets pour `Vehicules.imageDuCavalier` (la selle se tire du banc comme dans le petit train), et
  //: de combien chacun est plus haut que le siege d'un char : ceux de la caleche sont hauts sur leurs roues.
  const SIEGE_D_UN_CHAR = 4.6;
  let ASSISES = null;
  function assises() {
    const m = CABANE_EN_VOLUME.caisse[0].machine;
    return m.bancs.map(function (b) {
      return { u: b[0], w: b[1], z: b[2] - SIEGE_D_UN_CHAR, def: { selle: [b[1], -b[0] - 20], posture: 'volant', machine: m } };
    });
  }

  /** L'ombre d'une machine, orientee comme elle et ecrasee comme le sol (`Foire`, `Vehicules.dessinerUn`). */
  function ombre(ctx, x, y, a, l, w) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(1, BIAIS_DU_SOL);
    ctx.rotate(a);
    ctx.fillStyle = 'rgba(20,18,26,0.26)';
    ctx.fillRect(-l - 1, -w - 1, 2 * l + 2, 2 * w + 2);
    ctx.restore();
  }

  /** Une machine de la caleche cuite au cap `a`, son point de sol en `x, y` (a l'ecran). */
  function peindreMachine(ctx, nom, fiche, x, y, a) {
    const image = Atlas.cuireCap(nom, fiche, null, Vehicules.ROTATIONS, Vehicules.capDe(a), [0, 0]);
    ctx.drawImage(image, Math.round(x - image.width / 2), Math.round(y - image.height / 2));
    B.stats.images++;
  }

  /** Les deux chevaux et leur harnais, au trot (le pas suit le chemin fait) ou a l'arret. */
  function peindreChevaux(ctx, ox, oy, c) {
    const ch = c.chevaux, pas = Math.floor(c.s / 6) % 4;
    ombre(ctx, ox, oy, ch.a, CHEVAUX.l - 2, CHEVAUX.w - 1);
    if (c.roule) peindreMachine(ctx, 'caleche_chevaux_' + pas, CABANE_EN_VOLUME.chevaux[pas], ox, oy, ch.a);
    else peindreMachine(ctx, 'caleche_chevaux_arret', CABANE_EN_VOLUME.arret, ox, oy, ch.a);
  }

  /** La caisse au cap, ses rayons qui tournent, et ceux qui y sont assis — du plus au nord au plus au sud, pour
      que le banc de devant cache celui de derriere quand elle descend. Le cocher a son siege quand il travaille,
      le joueur a la premiere place quand il fait le tour. */
  function peindreCaleche(ctx, ox, oy, c) {
    const j = B.joueur, lui = !!(j && j.manege && j.manege.quoi === 'caleche');
    const phase = Math.floor(c.s / 5) % 2;
    ombre(ctx, ox, oy, c.a, CAISSE.l, CAISSE.w - 1);
    peindreMachine(ctx, 'caleche_caisse_' + phase, CABANE_EN_VOLUME.caisse[phase], ox, oy, c.a);
    if (!ASSISES) ASSISES = assises();
    const ca = Math.cos(c.a), sa = Math.sin(c.a);
    const faux = { x: ox, y: oy, angle: c.a, def: { longueur: 40 } };
    const ordre = ASSISES.map(function (b, i) { return i; }).sort(function (p, q) {
      const b1 = ASSISES[p], b2 = ASSISES[q];
      return (b1.u * sa + b1.w * ca) - (b2.u * sa + b2.w * ca);
    });
    for (const i of ordre) {
      let tenue;
      if (i === ASSISES.length - 1) { if (!c.cocher) continue; tenue = COCHER; }
      else if (i === 0 && lui) tenue = j.swaps || {};
      else if (PLACES[i] === null) continue;
      else tenue = PROMENEURS[(PLACES[i] + (c.tours || 0)) % PROMENEURS.length];
      const assis = Vehicules.imageDuCavalier(ASSISES[i].def, faux, tenue);
      if (!assis) continue;
      ctx.drawImage(assis.canvas, Math.round(assis.x), Math.round(assis.y - ASSISES[i].z));
      B.stats.images++;
    }
  }

  //: L'ecriteau de l'arret, et sa largeur (le texte et trois pixels de chaque cote).
  const PANCARTE = 'CALÈCHE';
  function largePancarte() { return Atlas.largeurTexte(PANCARTE) + 6; }

  /** Ou est la pancarte, dans le monde : `x0` son bord gauche, `y` le pied de ses poteaux.
      ⚠️ Son poteau de GAUCHE est planté dans la tuile `pancarte` (Martin, 28 sept. 2026 : « la pancarte est pas
      alignée au chemin ») : centrée sur sa tuile, elle débordait d'une demi-largeur vers l'ouest, et son poteau
      tombait dans le passage qui descend de la cabane. Les poteaux dans l'herbe, les pieds au bord du sentier. */
  function pancarte() {
    const d = chemin && chemin.def;
    if (!d || !d.pancarte) return null;
    const large = largePancarte(), x0 = d.pancarte[0] * TT + 1;
    return { x0: x0, y: d.pancarte[1] * TT + 15, large: large, poteaux: [x0 + 2, x0 + large - 3] };
  }

  /** La pancarte de l'arret : CALÈCHE, sur deux poteaux (`x0`, `y` a l'ecran). */
  function peindrePancarte(ctx, x0, y) {
    const large = largePancarte();
    ctx.fillStyle = '#4a3218'; ctx.fillRect(x0 + 2, y - 16, 1, 17); ctx.fillRect(x0 + large - 3, y - 16, 1, 17);
    ctx.fillStyle = '#4a3218'; ctx.fillRect(x0, y - 22, large, 9);
    ctx.fillStyle = '#8a5a2b'; ctx.fillRect(x0 + 1, y - 21, large - 2, 7);
    Atlas.texte(ctx, PANCARTE, x0 + 3, y - 20, '#f4e4c1');
    B.stats.rects += 5;
  }

  //: Un numero de tri hors de portee de ceux des entites (voir `Foire.ajouterVisibles`), et de ceux de la foire.
  const ID_TRI = 910000000;

  /** Ce qui se trie avec les entites : la caleche, ses chevaux, la pancarte. */
  function ajouterVisibles(visibles, cx, cy) {
    if (!ici() || !cal || !chemin) return;
    const c = caleche();
    const dans = function (x, y) { return x > cx - 48 && x < cx + VW + 48 && y > cy - 48 && y < cy + VH + 48; };
    if (c) c.cocher = true;
    if (c && dans(c.x, c.y)) {
      visibles.push({ id: ID_TRI, vivant: true, x: c.x, y: c.y + CAISSE.w,
                      peindreFoire: function (ctx) { peindreCaleche(ctx, Math.round(c.x - cx), Math.round(c.y - cy), c); } });
    }
    if (c && dans(c.chevaux.x, c.chevaux.y)) {
      visibles.push({ id: ID_TRI + 1, vivant: true, x: c.chevaux.x, y: c.chevaux.y + 3,
                      peindreFoire: function (ctx) { peindreChevaux(ctx, Math.round(c.chevaux.x - cx), Math.round(c.chevaux.y - cy), c); } });
    }
    const p = pancarte();
    if (p && dans(p.x0 + p.large / 2, p.y)) {
      visibles.push({ id: ID_TRI + 2, vivant: true, x: p.x0 + p.large / 2, y: p.y,
                      peindreFoire: function (ctx) { peindrePancarte(ctx, Math.round(p.x0 - cx), Math.round(p.y - cy)); } });
    }
  }

  return { ici, temps, heures, onFaitBouillir, maj, majSons, caleche, sousLaMain, invite, agir, monter, descendre, bloquer,
           dessinerSol, ajouterVisibles, gens, tableSousLaMain, calecheSousLaMain, calecheFermee, chalumeau, sansDe, pancarte,
           get chemin() { return chemin; }, get etat() { return cal; }, CAISSE, CHEVAUX, SIEGE, INVITE, RAYON };
})();
