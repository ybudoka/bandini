/* Bandini — le cine-parc Belvedere (docs/jalons/le-cine-parc.md).

   Un bloc de carte (`app/blocs/cineparc.py`) : on y entre par le bord nord de La Shop. L'ETE, le soir,
   un film joue sur l'ecran geant — un film muet en pixels, une poursuite de chars (un clin d'oeil au jeu
   lui-meme) ; des spectateurs sont gares dans les rangees ; on se gare, on eteint ses phares.

   ⚠️ TOUT CE QUI VIT ICI EST PEINT OU PARESSEUX : la toile, le film, les poteaux a haut-parleur sont
   peints (ni entite ni de) ; les spectateurs naissent quand on arrive pendant la seance, garés dans les
   cases, de couleurs donnees (`Vehicules.creer` ne tire pas de de), et repartent quand elle finit.

   ⚠️ LES PHARES COMPTENT POUR VRAI : pendant le film, un char qui roule dans les rangees les a allumes —
   et les spectateurs klaxonnent. Gare dans une case et arrete, le tien les eteint (`pharesEteints`,
   lu par `Vehicules`). */

const Cineparc = (function () {
  'use strict';

  function ici() { return !!(B.bloc && B.bloc.slug === 'cineparc' && Monde.carte && Monde.carte.def && Monde.carte.def.bloc); }
  function ecran() { return ici() ? Monde.carte.def.bloc.ecran : null; }

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
    ctx.fillStyle = '#2a2a30'; ctx.fillRect(x - 2, y - 2, l + 4, h + 4);          // le cadre
    if (!seance()) {
      ctx.fillStyle = '#d8d8dc'; ctx.fillRect(x, y, l, h);
      ctx.fillStyle = '#c4c4ca'; for (let k = 0; k < l; k += 12) ctx.fillRect(x + k, y, 1, h);
      B.stats.rects += 3;
      return;
    }
    film(ctx, x, y, l, h);
  }

  /** LE FILM : une poursuite de chars, en noir et blanc qui tremble — la route defile, le fuyard
      zigzague, l'auto-patrouille le colle, gyrophare au vent. Fonction de l'image, rien d'autre. */
  function film(ctx, x, y, l, h) {
    const t = B.t, grain = (t >> 2) % 3;
    ctx.fillStyle = grain === 0 ? '#e9e9e4' : grain === 1 ? '#dededa' : '#f2f2ee'; ctx.fillRect(x, y, l, h);
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
    // Les rayures de la pellicule, et une tache qui passe.
    ctx.fillStyle = 'rgba(40,40,40,0.35)';
    ctx.fillRect(x + ((t * 7) % l), y, 1, h);
    if ((t >> 5) % 4 === 0) ctx.fillRect(x + ((t * 13) % (l - 6)), y + ((t * 5) % (h - 6)), 4, 3);
    B.stats.rects += 20;
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

  // ⚠️ `film` sert aussi a la toile du Rialto (`Enseignes`) : le meme film muet, en ville.
  return { ici, seance, dansUneCase, cases, spectateurs, maj, dessiner, lampes, film };
})();
