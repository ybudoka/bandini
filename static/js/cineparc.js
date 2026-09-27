/* Bandini — le cine-parc Belvedere (docs/jalons/le-cine-parc.md).

   Un bloc de carte (`app/blocs/cineparc.py`) : on y entre par le bord nord de La Shop. L'ETE, le soir,
   un film joue sur l'ecran geant — un film muet en pixels, une poursuite de chars (un clin d'oeil au jeu
   lui-meme) ; des spectateurs sont gares dans les rangees ; on se gare, on eteint ses phares.

   ⚠️ TOUT CE QUI VIT ICI EST PEINT OU PARESSEUX : la toile, le film, les poteaux a haut-parleur sont
   peints (ni entite ni de) ; les spectateurs naissent quand on arrive pendant la seance, garés dans les
   cases, de couleurs donnees (`Vehicules.creer` ne tire pas de de), et repartent quand elle finit.

   ⚠️ LE PROJECTEUR : le casse-croute, au milieu du terrain, est aussi la cabine de projection. Pendant la
   seance, un faisceau part de sa fenetre nord (`bloc.cabine`) et s'ouvre jusqu'a la toile — peint PAR-DESSUS
   la nuit (`dessinerFaisceau`, apres `Base.fin`), sinon il s'y eteint. Le Rialto se sert du meme (`faisceau`).

   ⚠️ LES PHARES COMPTENT POUR VRAI : pendant le film, un char qui roule dans les rangees les a allumes —
   et les spectateurs klaxonnent. Gare dans une case et arrete, le tien les eteint (`pharesEteints`,
   lu par `Vehicules`). */

const Cineparc = (function () {
  'use strict';

  function ici() { return !!(B.bloc && B.bloc.slug === 'cineparc' && Monde.carte && Monde.carte.def && Monde.carte.def.bloc); }
  function ecran() { return ici() ? Monde.carte.def.bloc.ecran : null; }
  function cabine() { return ici() ? Monde.carte.def.bloc.cabine : null; }

  /** La seance joue : l'ete, au crepuscule ou la nuit. Pure (avec l'heure et le jour). */
  function seance() {
    if (!B.partie || typeof Calendrier === 'undefined') return false;
    return Calendrier.saisonDuJour() === 'ete' && ['crepuscule', 'nuit'].indexOf(Monde.periode()) >= 0;
  }

  /** Une case de stationnement sous ce pixel ? */
  function dansUneCase(x, y) {
    return Monde.glyphe(Math.floor(x / TT), Math.floor(y / TT)) === '^';
  }

  /** Les cases (en pixels, le centre), dans l'ordre du plan : les places des spectateurs. */
  function cases() {
    const c = Monde.carte, out = [];
    for (let ty = 0; ty < c.h; ty++) {
      for (let tx = 0; tx < c.w; tx++) if (Monde.glyphe(tx, ty) === '^') out.push({ x: tx * TT + 8, y: ty * TT + 8, tx: tx, ty: ty });
    }
    return out;
  }

  //: Les couleurs des chars des spectateurs (donnees : aucun de).
  const COULEURS = ['#c0392b', '#2c3e50', '#ecf0f1', '#27ae60', '#8e44ad', '#d35400', '#16a085', '#7f8c8d'];
  //: Combien de spectateurs, et une case sur combien (on laisse de la place au joueur).
  const SPECTATEURS = 7;

  function spectateurs() { return B.entites.filter(function (e) { return e.type === 'vehicule' && e.spectateur; }); }

  /** Les spectateurs arrivent avec la seance (une fois), et repartent apres. */
  function majSpectateurs() {
    const seanceIci = ici() && seance(), les = spectateurs();
    if (!seanceIci) {
      for (const v of les) if (v.conducteur !== B.joueur) Entites.retirer(v);
      return;
    }
    if (les.length) return;
    const cs = cases();
    for (let k = 0; k < SPECTATEURS; k++) {
      // Les places a l'EMPREINTE du numero du spectateur : une case sur quatre, jamais deux voisines.
      const c = cs[(hash2(k, 0xC1E) % Math.floor(cs.length / 4)) * 4 + (k % 2) * 2];
      if (!c || les.some(function (v) { return Math.hypot(v.x - c.x, v.y - c.y) < 20; })) continue;
      const v = Vehicules.creer('auto', c.x, c.y + 4, -Math.PI / 2, { etat: 'stationne', couleur: COULEURS[k % COULEURS.length] });
      if (!v) continue;
      v.spectateur = true; v.resteGare = true; v.pharesEteints = true;
      les.push(v);
    }
    Entites.indexer();
    // On arrive pendant la seance (ou elle commence) : l'affiche du soir.
    if (typeof Hud !== 'undefined') Hud.message('CE SOIR : ' + programme().titre, 180);
  }

  //: Le dernier klaxon des spectateurs (images), et le repit entre deux.
  let klaxonT = -1e9;
  const REPIT_KLAXON = 90;

  /** Le char du joueur, pendant la seance : roulant dans le stationnement, phares allumes — les
      spectateurs klaxonnent ; gare dans une case et arrete, ses phares s'eteignent. */
  function majPhares() {
    const j = B.joueur, v = j && j.dansVehicule;
    if (!v) return;
    if (!ici() || !seance()) { if (v.pharesEteints) v.pharesEteints = false; return; }
    const arrete = Math.abs(v.vitesse) < 0.1;
    v.gareT = arrete && dansUneCase(v.x, v.y) ? (v.gareT || 0) + 1 : 0;
    v.pharesEteints = v.gareT > 30;
    const dansLeParc = Monde.glyphe(Math.floor(v.x / TT), Math.floor(v.y / TT)) !== ',';
    if (!v.pharesEteints && dansLeParc && Math.abs(v.vitesse) > 0.3 && B.t - klaxonT > REPIT_KLAXON && spectateurs().length) {
      klaxonT = B.t;
      Son.SFX.klaxon();
      Hud.message('ÉTEINS TES PHARES!', 90);
    }
  }

  function maj() { majSpectateurs(); majPhares(); }

  // --- La toile et le film -------------------------------------------------------------------

  /** La toile, au-dessus de son cadre : blanche et grise hors seance, le film pendant. */
  function dessiner(ctx, cam) {
    const e = ecran();
    if (!e) return;
    const x = Math.round(e.x * TT - cam.x), l = e.l * TT;
    // ⚠️ Quatre tuiles de haut, de la premiere rangee du bloc a son cadre : plus haute, elle sortait de
    // la carte (la camera ne monte pas au-dessus de la rangee 0).
    const h = (e.y + e.h) * TT, y = Math.round(-cam.y);
    dessinerPoteaux(ctx, cam);
    dessinerCabine(ctx, cam);
    ctx.fillStyle = '#2a2a30'; ctx.fillRect(x - 2, y - 2, l + 4, h + 4);          // le cadre
    if (!seance()) {
      ctx.fillStyle = '#d8d8dc'; ctx.fillRect(x, y, l, h);
      ctx.fillStyle = '#c4c4ca'; for (let k = 0; k < l; k += 12) ctx.fillRect(x + k, y, 1, h);
      B.stats.rects += 3;
      return;
    }
    film(ctx, x, y, l, h);
  }

  // --- La programmation : trois films, un par soir -------------------------------------------
  //
  // ⚠️ Martin (27 sept. 2026) : « des films de combat ». Le Rialto et le cine-parc passent le MEME film le meme
  // soir, choisi par le jour de la seance — apres minuit, c'est encore la seance de la veille : le film ne change
  // pas en pleine projection. Ni de ni etat : chaque film est une fonction de l'image.

  //: Les trois films, dans l'ordre des soirs.
  const FILMS = [
    { slug: 'poursuite', titre: 'PAS DE FREINS', peindre: poursuite },
    { slug: 'karate', titre: 'LE POING DE LA BAIE', peindre: karate },
    { slug: 'boxe', titre: 'LE KID DES BRUMES', peindre: boxe },
  ];

  /** Le film de ce soir : `{ slug, titre }`. */
  function programme() {
    const p = B.partie;
    if (!p) return FILMS[0];
    const jour = Math.floor(p.jour || 0) - (p.heure < 0.5 ? 1 : 0), n = FILMS.length;
    return FILMS[((jour % n) + n) % n];
  }

  /** LE FILM de ce soir, en noir et blanc qui tremble, sur la toile (x, y, l, h) : le grain, le film, les rayures
      de la pellicule. ⚠️ `film` sert aussi a la toile du Rialto (`Enseignes`). */
  function film(ctx, x, y, l, h) {
    const t = B.t, grain = (t >> 2) % 3;
    ctx.fillStyle = grain === 0 ? '#e9e9e4' : grain === 1 ? '#dededa' : '#f2f2ee'; ctx.fillRect(x, y, l, h);
    ctx.save();
    ctx.beginPath(); ctx.rect(x, y, l, h); ctx.clip();
    programme().peindre(ctx, x, y, l, h, t);
    ctx.restore();
    ctx.fillStyle = 'rgba(40,40,40,0.35)';
    ctx.fillRect(x + ((t * 7) % l), y, 1, h);
    if ((t >> 5) % 4 === 0) ctx.fillRect(x + ((t * 13) % (l - 6)), y + ((t * 5) % (h - 6)), 4, 3);
    B.stats.rects += 4;
  }

  /** PAS DE FREINS : une poursuite de chars — la route qui defile, le fuyard qui zigzague, l'auto-patrouille qui
      le colle, gyrophare au vent. */
  function poursuite(ctx, x, y, l, h, t) {
    // La route, de face : ses bords et ses tirets qui defilent vers nous.
    const rx = x + l * 0.25, rl = l * 0.5;
    ctx.fillStyle = '#6a6a6a'; ctx.fillRect(Math.round(rx), y, Math.round(rl), h);
    ctx.fillStyle = '#f2f2ee';
    for (let k = 0; k < 6; k++) {
      const ty = y + ((k * 14 + t) % (h + 10)) - 10;
      ctx.fillRect(Math.round(x + l / 2 - 1), Math.round(ty), 2, 6);
    }
    // Le fuyard, puis la police.
    const zig = Math.sin(t / 18) * rl * 0.25;
    const fx = Math.round(x + l / 2 + zig - 4), fy = Math.round(y + h * 0.35);
    ctx.fillStyle = '#1a1a1a'; ctx.fillRect(fx, fy, 8, 12); ctx.fillStyle = '#9a9a9a'; ctx.fillRect(fx + 1, fy + 2, 6, 3);
    const px = Math.round(x + l / 2 + Math.sin((t - 20) / 18) * rl * 0.25 - 4), py = Math.round(y + h * 0.62);
    ctx.fillStyle = '#f2f2ee'; ctx.fillRect(px, py, 8, 12); ctx.fillStyle = '#1a1a1a'; ctx.fillRect(px, py + 5, 8, 2);
    ctx.fillStyle = (t >> 3) % 2 ? '#1a1a1a' : '#8a8a8a'; ctx.fillRect(px + 2, py - 1, 4, 2);
    B.stats.rects += 18;
  }

  //: La longueur d'un film de combat (images) : il boucle, comme une bobine qu'on rembobine.
  const BOBINE = 600;

  /** Un combattant, de profil, en blocs de `s` pixels : `(cx, sol)` sous ses pieds, `dir` 1 s'il regarde a
      droite, -1 a gauche. `p` : ses couleurs (`corps`, `bas`, `peau`, `ceinture`, `gants`). Les poses : garde,
      poing, crochet, coupdepied, vole, couche, salut, victoire. */
  function combattant(ctx, cx, sol, s, dir, pose, p) {
    const r = function (dx, dy, w, hh, c) {
      ctx.fillStyle = c;
      ctx.fillRect(Math.round(cx + (dir > 0 ? dx : -dx - w) * s), Math.round(sol + dy * s), w * s, hh * s);
    };
    const main = p.gants || p.peau, g = p.gants ? 2 : 1;
    if (pose === 'couche') {                                     // a plat sur le dos, les bras en croix
      r(-6, -2, 9, 2, p.corps); r(-6, -2, 3, 2, p.bas); r(3, -3, 3, 3, p.peau); r(0, -3, g, g, main);
      return;
    }
    if (pose === 'vole') {                                       // a l'horizontale, les pieds devant
      r(-7, -8, 5, 2, p.bas); r(-2, -8, 5, 3, p.corps); r(3, -9, 3, 3, p.peau);
      r(0, -11, 1, 3, p.corps); r(0, -12, g, g, main);
      if (p.ceinture) r(-2, -8, 1, 3, p.ceinture);
      return;
    }
    const baisse = pose === 'salut' ? 1 : 0;
    // Les jambes, le tronc, la ceinture, la tete.
    if (pose === 'coupdepied') { r(1, -6, 6, 1, p.bas); r(-1, -5, 1, 3, p.bas); r(0, -3, 2, 1, p.bas); }
    else if (pose === 'salut' || pose === 'victoire') { r(-1, -5, 1, 5, p.bas); r(1, -5, 1, 5, p.bas); }
    else { r(-2, -5, 1, 5, p.bas); r(1, -5, 1, 5, p.bas); }
    r(-1, -10 + baisse, 3, 5 - baisse, p.corps);
    if (p.ceinture) r(-1, -6, 3, 1, p.ceinture);
    r(-1 + baisse * 2, -13 + baisse * 3, 3, 3, p.peau);
    // Les bras.
    if (pose === 'poing') { r(2, -9, 4, 1, p.corps === p.peau ? p.peau : p.corps); r(6, -9 - (g - 1), g, g, main); r(1, -8, 1, 2, p.corps); }
    else if (pose === 'crochet') { r(2, -11, 2, 1, p.corps); r(4, -13, g, g, main); r(1, -8, 1, 2, p.corps); }
    else if (pose === 'victoire') { r(1, -15, 1, 5, p.corps); r(1, -16 - (g - 1), g, g, main); r(-2, -9, 1, 3, p.corps); }
    else if (pose === 'salut') { r(-2, -9, 1, 4, p.corps); r(2, -9, 1, 4, p.corps); }
    else { r(2, -9, 2, 1, p.corps); r(3, -10 - (g - 1), g, g, main); r(1, -8, 2, 1, p.corps); r(2, -8, g, g, main); }
  }

  /** Le « POW! » d'un coup qui porte : une etoile blanche cernee de noir, et le mot dedans. */
  function pow(ctx, px, py, s) {
    const pointes = 8, grand = 7 * s, petit = 3.5 * s;
    const etoile = function (k) {
      ctx.beginPath();
      for (let i = 0; i < pointes * 2; i++) {
        const a = i * Math.PI / pointes, rr = (i % 2 ? petit : grand) + k;
        if (i) ctx.lineTo(px + Math.cos(a) * rr, py + Math.sin(a) * rr); else ctx.moveTo(px + rr, py);
      }
      ctx.closePath(); ctx.fill();
    };
    ctx.fillStyle = '#1a1a1a'; etoile(s);
    ctx.fillStyle = '#f7f7f2'; etoile(0);
    ctx.fillStyle = '#1a1a1a'; ctx.font = 'bold ' + (3 * s) + 'px monospace';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('POW!', px, py + 0.5);
  }

  /** Le carton de la fin, sur la toile noire. */
  function carton(ctx, x, y, l, h, s, mot) {
    ctx.fillStyle = '#1a1a1a'; ctx.fillRect(x, y, l, h);
    ctx.fillStyle = '#e9e9e4'; ctx.font = 'bold ' + (6 * s) + 'px monospace';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(mot, x + l / 2, y + h / 2);
  }

  //: Les deux karatekas : le blanc (le heros) et le noir.
  const GI_BLANC = { corps: '#f4f4f0', bas: '#f4f4f0', peau: '#b4b4ae', ceinture: '#1a1a1a' };
  const GI_NOIR = { corps: '#2a2a2a', bas: '#2a2a2a', peau: '#8e8e8a', ceinture: '#e9e9e4' };

  /** LE POING DE LA BAIE : deux karatekas dans un dojo. La garde, les echanges, le coup de pied saute, POW —
      le noir vole hors de l'image, le blanc salue. FIN. */
  function karate(ctx, x, y, l, h, t) {
    const T = t % BOBINE, s = Math.max(1, Math.floor(h / 20)), sol = y + h - 3 * s;
    // Le dojo : le mur, la bannière et son idéogramme, le plancher et ses lattes.
    ctx.fillStyle = '#8a8a86'; ctx.fillRect(x, y, l, h);
    // ⚠️ La banniere au premier TIERS, pas au milieu : au milieu, le coup de pied s'y confondait (vu a la capture).
    const bx0 = Math.round(x + l * 0.12);
    ctx.fillStyle = '#2a2a2a'; ctx.fillRect(bx0, y + s, 8 * s, 11 * s);
    ctx.fillStyle = '#e9e9e4'; ctx.fillRect(bx0 + 2 * s, y + 3 * s, 4 * s, s);
    ctx.fillRect(bx0 + 4 * s - Math.round(s / 2), y + 3 * s, s, 6 * s); ctx.fillRect(bx0 + 2 * s, y + 7 * s, 4 * s, s);
    ctx.fillStyle = '#c4c4be'; ctx.fillRect(x, sol, l, y + h - sol);
    ctx.fillStyle = '#a8a8a2'; for (let k = 0; k < l; k += 10 * s) ctx.fillRect(x + k, sol, s, y + h - sol);
    B.stats.rects += 8 + l / (10 * s);
    if (T >= 560) return carton(ctx, x, y, l, h, s, 'FIN');
    const saut = (T >> 3) % 2 ? s : 0;
    let ax = x + l * 0.32 + Math.sin(T / 20) * 2 * s, bx = x + l * 0.68 - Math.sin(T / 23) * 2 * s;
    let pa = 'garde', pb = 'garde', la = saut, lb = (saut ? 0 : s);
    if (T >= 180 && T < 300) {                                   // les echanges : un poing chacun son tour
      const k = Math.floor((T - 180) / 30), coup = (T - 180) % 30 < 12;
      if (coup) { if (k % 2) pb = 'poing'; else pa = 'poing'; }
    } else if (T >= 300 && T < 350) {                            // le coup de pied saute
      const f = (T - 300) / 50;
      pa = 'coupdepied'; la = Math.sin(f * Math.PI) * 6 * s; ax += f * (bx - ax - 9 * s);
    } else if (T >= 350) {
      ax = x + l * 0.32 + (x + l * 0.68 - x - l * 0.32 - 9 * s);
      if (T < 430) { pb = 'vole'; const f = (T - 350) / 20; bx += f * l * 0.25; lb = Math.sin(Math.min(1, f / 3) * Math.PI) * 5 * s; }
      else { pb = null; pa = 'salut'; }
    }
    combattant(ctx, ax, sol - la, s, 1, pa, GI_BLANC);
    if (pb) combattant(ctx, bx, sol - lb, s, -1, pb, GI_NOIR);
    if (T >= 335 && T < 365) pow(ctx, bx - 2 * s, sol - 9 * s, s);
    B.stats.rects += 30;
  }

  //: Les deux boxeurs (le Kid en culottes blanches) et l'arbitre.
  const KID = { corps: '#a8a8a4', bas: '#f4f4f0', peau: '#a8a8a4', gants: '#1a1a1a' };
  const COGNEUR = { corps: '#7a7a76', bas: '#1a1a1a', peau: '#7a7a76', gants: '#f4f4f0' };

  /** LE KID DES BRUMES : un ring. Les jabs, le crochet, POW — l'autre tombe, l'arbitre compte sur ses doigts
      jusqu'a dix, et le Kid leve le gant. FIN. */
  function boxe(ctx, x, y, l, h, t) {
    const T = t % BOBINE, s = Math.max(1, Math.floor(h / 20)), sol = y + h - 4 * s;
    // La foule dans le noir (des tetes), le tapis, les poteaux et les trois cables.
    ctx.fillStyle = '#3a3a3a'; ctx.fillRect(x, y, l, h);
    ctx.fillStyle = '#555553';
    for (let k = 0; k < l; k += 5 * s) ctx.fillRect(x + k + ((k * 7) % 3) * s, y + s + ((k * 3) % 4) * s, 3 * s, 3 * s);
    ctx.fillStyle = '#cfcfca'; ctx.fillRect(x, sol, l, y + h - sol);
    ctx.fillStyle = '#e9e9e4'; ctx.fillRect(x + 2 * s, sol - 16 * s, 2 * s, 16 * s); ctx.fillRect(x + l - 4 * s, sol - 16 * s, 2 * s, 16 * s);
    for (const c of [6, 10, 14]) ctx.fillRect(x, sol - c * s, l, Math.max(1, Math.round(s / 2)));
    B.stats.rects += 8 + l / (5 * s);
    if (T >= 560) return carton(ctx, x, y, l, h, s, 'FIN');
    const saut = (T >> 3) % 2 ? s : 0;
    const ax = x + l * 0.36 + Math.sin(T / 17) * 2 * s, bx0 = x + l * 0.6 - Math.sin(T / 21) * 2 * s;
    let pa = 'garde', pb = 'garde', la = saut, lb = saut ? 0 : s, bx = bx0;
    if (T < 200) {                                               // les jabs
      const k = Math.floor(T / 24), coup = T % 24 < 9;
      if (coup) { if (k % 3 === 2) pb = 'poing'; else pa = 'poing'; }
    } else if (T < 230) { pa = 'crochet'; }
    else { pb = T < 260 ? 'vole' : 'couche'; lb = T < 260 ? (1 - (T - 230) / 30) * 4 * s : 0; bx = bx0 + 3 * s; }
    if (T >= 480) pa = 'victoire';
    combattant(ctx, ax, sol - la, s, 1, pa, KID);
    combattant(ctx, bx, sol - lb, s, -1, pb, COGNEUR);
    if (T >= 212 && T < 240) pow(ctx, bx0 - s, sol - 10 * s, s);
    // L'arbitre, au-dessus du tombe : il compte, un doigt de plus a chaque seconde, jusqu'a dix.
    if (T >= 260) {
      const rx = Math.round(x + l * 0.8), n = Math.min(10, Math.floor((T - 260) / 22) + 1);
      for (let k = 0; k < 3; k++) { ctx.fillStyle = k % 2 ? '#1a1a1a' : '#f4f4f0'; ctx.fillRect(rx - s + k * s, sol - 10 * s, s, 5 * s); }
      ctx.fillStyle = '#2a2a2a'; ctx.fillRect(rx - 2 * s, sol - 5 * s, s, 5 * s); ctx.fillRect(rx + s, sol - 5 * s, s, 5 * s);
      ctx.fillStyle = '#9a9a96'; ctx.fillRect(rx - s, sol - 13 * s, 3 * s, 3 * s);
      ctx.fillStyle = '#9a9a96'; ctx.fillRect(rx - 3 * s, sol - 15 * s, s, 6 * s);           // le bras leve
      if (T < 480) {
        ctx.fillStyle = '#f4f4f0';
        for (let k = 0; k < n; k++) ctx.fillRect(rx - 7 * s + (k % 5) * s * 1.2, sol - (18 + 4 * Math.floor(k / 5)) * s, Math.max(1, Math.round(s * 0.7)), 3 * s);
      }
      B.stats.rects += 8 + n;
    }
    B.stats.rects += 30;
  }

  /** La fenetre de la cabine, au bord nord du toit du casse-croute : allumee pendant la seance. */
  function dessinerCabine(ctx, cam) {
    const c = cabine();
    if (!c) return;
    const x = Math.round(c.x * TT - cam.x), y = Math.round(c.y * TT - cam.y);
    if (x < -8 || y < -8 || x > VW + 8 || y > VH + 8) return;
    ctx.fillStyle = '#2a2a30'; ctx.fillRect(x - 4, y, 8, 4);                      // le cadre
    ctx.fillStyle = seance() ? '#fff4c8' : '#3c4a5a'; ctx.fillRect(x - 3, y + 1, 6, 2);   // la vitre
    B.stats.rects += 2;
  }

  /** LE FAISCEAU D'UN PROJECTEUR, en pixels d'ecran : de la lentille (sx, sy) jusqu'au bord de la toile
      (de x0 a x1, a la hauteur ty). Trois cones l'un dans l'autre, en lumiere qui s'ADDITIONNE (le coeur
      plus vif que les bords), qui tremblote comme une lampe a arc, et la poussiere qui y passe. `force` (0 a 1)
      l'allume ou l'eteint en fondu ; `t` (images) le fait vivre. Fonction de l'image : ni de ni etat.
      ⚠️ Le Rialto s'en sert aussi (`Enseignes.dessinerPardessus`). */
  function faisceau(ctx, sx, sy, x0, x1, ty, force, t) {
    if (!(force > 0)) return;
    const l = x1 - x0, mx = (x0 + x1) / 2;
    const vacille = 0.86 + 0.14 * Math.sin(t * 0.9) * Math.sin(t * 0.23);
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    const cone = function (demi, bord, a) {
      ctx.fillStyle = 'rgba(220,228,255,' + (a * force * vacille).toFixed(3) + ')';
      ctx.beginPath();
      ctx.moveTo(sx - demi, sy); ctx.lineTo(sx + demi, sy);
      ctx.lineTo(x1 - l * bord, ty); ctx.lineTo(x0 + l * bord, ty);
      ctx.closePath(); ctx.fill();
    };
    cone(2, 0, 0.07);
    cone(1.5, 0.16, 0.07);
    cone(1, 0.34, 0.09);
    // La poussiere qui monte dans la lumiere : des grains qui filent de la lentille vers la toile.
    for (let k = 0; k < 16; k++) {
      const f = (t * 0.005 + k * 0.1373) % 1, demi = 2 + (l / 2 - 2) * f;
      const px = sx + (mx - sx) * f + (((k * 0.618) % 1) * 2 - 1) * demi * 0.85, py = sy + (ty - sy) * f;
      const a = 0.22 + 0.18 * Math.sin(t * 0.11 + k * 1.7);
      ctx.fillStyle = 'rgba(255,250,230,' + (a * force).toFixed(3) + ')';
      ctx.fillRect(Math.round(px), Math.round(py), 1, 1);
    }
    // La lentille : un point blanc.
    ctx.fillStyle = 'rgba(255,250,225,' + (0.85 * force).toFixed(3) + ')';
    ctx.fillRect(Math.round(sx) - 2, Math.round(sy) - 1, 4, 2);
    ctx.restore();
    B.stats.rects += 20;
  }

  /** Par-dessus la nuit (apres `Base.fin`) : le faisceau de la cabine jusqu'a la toile, pendant la seance. */
  function dessinerFaisceau(ctx, cam) {
    const e = ecran(), c = cabine();
    if (!e || !c || !seance()) return;
    const x0 = e.x * TT - cam.x;
    faisceau(ctx, c.x * TT - cam.x, c.y * TT - cam.y, x0, x0 + e.l * TT, (e.y + e.h) * TT - cam.y, 1, B.t);
  }

  /** Un poteau a haut-parleur a la tete de chaque paire de cases (peint : ni entite ni obstacle). */
  function dessinerPoteaux(ctx, cam) {
    const cs = cases();
    let n = 0;
    for (let k = 0; k < cs.length; k += 2) {
      const c = cs[k], x = Math.round(c.tx * TT + TT - cam.x), y = Math.round(c.ty * TT - cam.y);
      if (x < -8 || y < -16 || x > VW + 8 || y > VH + 8) continue;
      ctx.fillStyle = '#3a3d44'; ctx.fillRect(x, y - 6, 1, 12);
      ctx.fillStyle = '#b8b8bf'; ctx.fillRect(x - 2, y - 8, 5, 3);
      n += 2;
    }
    B.stats.rects += n;
  }

  /** La lueur de l'ecran pendant le film, pour la nuit (`Base.fin`). */
  function lampes(cam) {
    const e = ecran();
    if (!e || !seance()) return [];
    const cx = (e.x + e.l / 2) * TT - cam.x, cy = e.y * TT - cam.y;
    return [{ x: cx, y: cy - 20, r: 150, c: 'rgba(210,220,255,0.5)' }, { x: cx, y: cy + 60, r: 110, c: 'rgba(210,220,255,0.35)' }];
  }

  // ⚠️ `film` et `faisceau` servent aussi au Rialto (`Enseignes`) : le meme film, le meme soir, en ville.
  return { ici, seance, dansUneCase, cases, spectateurs, maj, dessiner, dessinerFaisceau, lampes, film, faisceau, programme,
           FILMS: FILMS.map(function (f) { return { slug: f.slug, titre: f.titre }; }) };
})();
