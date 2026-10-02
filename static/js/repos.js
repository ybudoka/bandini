/* Bandini — s'asseoir, attendre, se coucher (P4, docs/jalons/s-asseoir-attendre-se-coucher.md).

   Demande de Martin (2 oct. 2026) : « il faut pouvoir s'asseoir sur les sofas et se coucher dans les lits avant de
   dormir ». Vague 1 : DEDANS, on s'assoit sur une chaise (`h`), une berçante (`V`) ou le sofa à carreaux de la
   planque ; et le lit À SOI (le point `lit` : la planque, la chambre de l'hôtel, le phare, le chalet acheté) nous
   couche avant d'ouvrir son menu.

   ⚠️ RIEN DE NEUF DANS LE CORPS : l'assis est celui du banc (`Interactions.asseoirA`, `majAssis` — le stick ou
   ACTION lève, un coup aussi), le couché celui du lit d'hôpital (`Entites.coucher`, `seLever`). Ce module ne dit
   que OÙ s'asseoir et se coucher dans une pièce.

   ⚠️ LE SIÈGE PASSE APRÈS LES GENS, ET LE POINT LE PLUS PROCHE GAGNE (`siegeAvantLePoint`) : une chaise se prend
   droit devant soi, collée ; un comptoir attrape ACTION dans 1,6 tuile autour (`Missions.pointSousLaMain`). À
   égalité — un point posé SUR la chaise —, c'est le point. L'invite et le geste lisent la même fonction. */

const Repos = (function () {
  'use strict';

  function cfg() { return B.defs && B.defs.interactions && B.defs.interactions.asseoir; }

  //: Jusqu'où devant soi on cherche la chaise : de quoi tomber dans la tuile d'à côté, pas deux plus loin.
  const DEVANT_PX = 12;

  /** Le siège, s'il est libre : personne d'autre n'y est assis (le patient, l'avocat, l'autre joueur). */
  function libre(j, x, y) {
    return !B.entites.some(function (e) {
      return e !== j && e.vivant && (e.type === 'pieton' || e.type === 'joueur') && dist2(e.x, e.y, x, y) < 8 * 8;
    });
  }

  /** Le siège droit devant, dans la pièce : `{ x, y, pose, dist, refus }`, ou null.

      La chaise et la berçante sont des TUILES (la tuile collée dans le sens du regard) ; le sofa est un décor de la
      planque (`Decoration.meubler`), qu'on regarde à portée du banc. */
  function siegeDevant(j) {
    const c = cfg();
    if (!c || !c.dedans || !B.interieur || !j || !j.vivant || j.assis || j.alite || j.dansVehicule || j.otage) return null;
    let meilleur = null;
    const regard = REGARDS[j.face];
    if (regard !== undefined) {
      const tx = Math.floor((j.x + Math.cos(regard) * DEVANT_PX) / TT), ty = Math.floor((j.y + Math.sin(regard) * DEVANT_PX) / TT);
      const s = Monde.estMeuble(tx, ty) && c.dedans[Monde.glyphe(tx, ty)];
      if (s) {
        const x = tx * TT + 8 + s.dx, y = ty * TT + 8 + s.dy;
        meilleur = { x: x, y: y, pose: s.pose, dist: Math.hypot(tx * TT + 8 - j.x, ty * TT + 8 - j.y) };
      }
    }
    const portee = B.defs.interactions.asseoir.portee_px;
    for (const d of B.entites) {
      const s = d.type === 'decor' && c.dedans[d.decor];
      if (!s || dist2(j.x, j.y, d.x, d.y) > portee * portee || !faceA(j, d.x, d.y)) continue;
      const dist = Math.hypot(d.x - j.x, d.y - j.y);
      if (!meilleur || dist < meilleur.dist) meilleur = { x: d.x + s.dx, y: d.y + s.dy, pose: s.pose, dist: dist };
    }
    if (!meilleur || !libre(j, meilleur.x, meilleur.y)) return null;
    meilleur.refus = Interactions.refusAsseoir(j);
    return meilleur;
  }

  /** Le siège devant, s'il passe avant `point` (le point de la pièce sous la main, ou null) : plus près que lui. */
  function siegeAvantLePoint(j, point) {
    const s = siegeDevant(j);
    if (!s || !point) return s;
    return s.dist < Math.hypot((point.x + 0.5) * TT - j.x, (point.y + 0.5) * TT - j.y) ? s : null;
  }

  /** ACTION devant un siège : on s'assoit, ou l'on dit pourquoi pas. */
  function sAsseoir(j, s) {
    j.gesteT = B.t;
    if (s.refus) { Hud.message(s.refus); Son.SFX.erreur(); return true; }
    return Interactions.asseoirA(j, s.x, s.y, s.pose);
  }

  // --- Le lit ------------------------------------------------------------------------------------------------

  /** Le lit du point `lit` : les tuiles du meuble collées au point (le point est posé sur le lit ou à côté), de la
      tuile de tête (en haut à gauche) à sa largeur. `{ x, y, largeur }` en tuiles, ou null. */
  function litDuPoint(point) {
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      const tx = point.x + dx, ty = point.y + dy;
      if (!Monde.estMeuble(tx, ty) || Monde.glyphe(tx, ty) !== 'l') continue;
      let x = tx, y = ty, droite = tx;
      while (Monde.glyphe(x - 1, y) === 'l') x--;
      while (Monde.glyphe(x, y - 1) === 'l') y--;
      while (Monde.glyphe(droite + 1, y) === 'l') droite++;
      return { x: x, y: y, largeur: droite - x + 1 };
    }
    return null;
  }

  /** Le menu du lit, couché : celui d'avant (DORMIR, LA SIESTE, SAUVEGARDER), et SE LEVER au bout. */
  function menuDuLit(point) {
    const menu = Missions.menuDuPoint(point);
    if (!menu) return null;
    menu.items.push({ libelle: 'SE LEVER', faire: function () { Entites.seLever(B.joueur, 0, 0); return true; } });
    return menu;
  }

  function ouvrirLeMenu(point) {
    const menu = menuDuLit(point);
    if (!menu) return false;
    menu.refaire = function () { return menuDuLit(point); };
    Hud.ouvrirMenu(menu);
    return true;
  }

  /** ACTION au lit à soi : on se couche dedans, la tête sur l'oreiller, au milieu du lit — puis le menu. Fermé, on
      reste couché : le stick lève (`Entites.majJoueur`), ACTION rouvre le menu (`majCouche`). */
  function seCoucher(j, point) {
    const lit = litDuPoint(point);
    if (!lit) return false;
    Entites.coucher(j, lit.x, lit.y);
    // ⚠️ Au milieu d'un lit de deux places, mais un demi-pixel à GAUCHE de la jointure : `seLever` reconnaît son lit
    // à la tuile sous le corps, celle de tête.
    j.x = lit.x * TT + lit.largeur * TT / 2 - 0.5;
    j.alite.aSoi = point;
    j.gesteT = B.t;
    return ouvrirLeMenu(point);
  }

  /** Couché dans son lit : son menu revient. */
  function rouvrir(j) { return !!(j.alite && j.alite.aSoi) && ouvrirLeMenu(j.alite.aSoi); }

  /** Couché dans son lit, une image : ACTION rouvre le menu. Vrai si la pression est prise. */
  function majCouche(j, ent) {
    if (!j.alite || !j.alite.aSoi || !ent.neuf('action') || B.menu) return false;
    Entree.videPresse();
    return rouvrir(j);
  }

  // --- Attendre, assis (vague 2) -----------------------------------------------------------------------------

  function cfgAttente() { return B.defs && B.defs.interactions && B.defs.interactions.attendre; }

  /** Pourquoi on ne peut pas attendre ici et maintenant, ou null. ⚠️ Tout ce qui COMPTE en images compterait au
      quadruple : le défi, la frénésie, le boulot, l'objectif à chrono. Et la villa, dont la nuit tient
      (`Monde.majHeure` y arrête l'horloge : l'attente n'y finirait jamais). */
  function refusAttendre() {
    const r = cfgAttente().refus;
    if (B.recherche.etoiles > 0) return B.defs.interactions.asseoir.refus.police;
    if (B.defi || B.epreuve || (typeof Frenesies !== 'undefined' && Frenesies.enCours())) return r.defi;
    if (Missions.boulot.etape) return r.boulot;
    const o = B.partie.mission && Histoire.objectif();
    const bloc = B.bloc && B.bloc.def && B.bloc.def.bloc;
    if ((o && o.chrono_s) || (bloc && bloc.nuit_tient)) return r.chrono;
    return null;
  }

  /** L'heure qu'il sera dans `heures` heures, comme l'horloge l'écrit (« 14:20 »). */
  function heureDans(heures) {
    const minutes = Math.floor(((B.partie.heure + heures / 24) % 1) * 24 * 60);
    const hh = Math.floor(minutes / 60), mm = minutes % 60;
    return (hh < 10 ? '0' : '') + hh + ':' + (mm < 10 ? '0' : '') + mm;
  }

  /** Le menu de l'assis (ACTION, `Interactions.majAssis`) : ATTENDRE 1 H · 2 H · 3 H, et SE LEVER. Refusée, l'attente
      se montre grisée, avec sa raison. */
  function menuAssis(j) {
    const c = cfgAttente(), refus = refusAttendre();
    const items = c.heures.map(function (h) {
      return { libelle: c.invite + ' ' + h + ' H', detail: refus || heureDans(h), actif: !refus,
               faire: function () { attendre(j, h); return true; } };
    });
    items.push({ libelle: 'SE LEVER', faire: function () { Interactions.seLever(j, 0, 0); return true; } });
    return { titre: 'ASSIS', items: items, aide: refus || 'LE STICK TE LÈVE, ET UN COUP AUSSI' };
  }

  /** L'attente commence : `reste`, en fraction de jour, ce que l'horloge doit encore avancer. */
  function attendre(j, heures) {
    B.attente = { joueur: j, reste: heures / 24 };
    Hud.message(cfgAttente().bandeau + ' — ' + Monde.heureTexte(), 30);
  }

  function finir(message) {
    B.attente = null;
    if (message) Hud.message(message, 120);
  }

  /** Une image d'horloge (`Monde.majHeure`, `parImage` : ce qu'elle avance d'ordinaire) : ce qu'elle avance DE PLUS
      pendant l'attente, et la fin de l'attente — à l'heure voulue, debout, sous un refus.

      Par pas de simulation, l'horloge avance d'une heure divisée en `secondes_par_heure × 60` images × `vitesse`
      pas : une heure en deux secondes, quand la ville fait ses quatre pas. ⚠️ Jamais plus que ce qui reste : on
      arrive à l'heure dite, pas une minute plus loin. */
  function majAttente(parImage) {
    const at = B.attente;
    if (!at) return 0;
    if (!at.joueur.assis || !at.joueur.vivant) { finir(null); return 0; }
    const refus = refusAttendre();
    if (refus) { finir(refus); return 0; }
    const c = cfgAttente();
    const total = Math.min(at.reste, 1 / (24 * c.secondes_par_heure * 60 * c.vitesse));
    const plus = Math.max(0, total - parImage);
    at.reste -= parImage + plus;
    // L'heure qu'il sera au sortir de cette image (l'horloge avance APRÈS nous, `Monde.majHeure`).
    const ici = heureDans((parImage + plus) * 24);
    if (at.reste <= 1e-9) finir('IL EST ' + ici);
    else if (B.t % 6 === 0) Hud.message(c.bandeau + ' — ' + ici, 12);
    return plus;
  }

  /** Après les pas ordinaires d'une image (`Jeu`, `n` pas) : la ville en fait d'autres pendant l'attente, jusqu'à
      `vitesse` par pas ordinaire, tant que l'image a du budget. Rend le nombre de pas de plus. */
  function accelerer(maj, n) {
    const c = cfgAttente();
    if (!B.attente || !c || !n) return 0;
    const montre = typeof performance !== 'undefined' && performance.now ? function () { return performance.now(); } : function () { return 0; };
    const t0 = montre(), max = n * (c.vitesse - 1);
    let k = 0;
    while (B.attente && k < max && montre() - t0 < c.budget_ms) { maj(); k++; }
    return k;
  }

  /** Une partie neuve n'attend rien. */
  function oublier() { B.attente = null; }

  return { siegeDevant, siegeAvantLePoint, sAsseoir, litDuPoint, seCoucher, rouvrir, majCouche, menuDuLit,
           refusAttendre, menuAssis, attendre, majAttente, accelerer, oublier };
})();
