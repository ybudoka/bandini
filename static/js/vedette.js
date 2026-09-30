/* Bandini — la vedette de police (les bateaux ne sont pas des chars, vague 4).

   ⚠️ Sur l'eau, la police de terre ne peut rien : ses agents nagent mais ne sortent personne d'une coque, ses
   autos s'arretent au quai, ses barrages sont dans la rue. Recherche dans une coque, on voit sortir la VEDETTE :
   une coque de police (`vedette` au parc), plus vive qu'une chaloupe, qui te rejoint PAR L'EAU et t'arraisonne
   bord a bord quand tu t'arretes.

   - Combien : aucune hors d'une coque ou sans etoile ; une des la premiere, deux des la troisieme (`voulues`).
   - Ou elle nait : hors champ, sur l'eau qui mene au joueur — le CHAMP des distances (`champ`), un parcours en
     largeur sur les tuiles d'eau depuis la tuile du joueur, borne a `PORTEE` tuiles, refait chaque demi-seconde.
   - Comment elle mene : elle suit la pente du champ, quelques tuiles devant ; a vue et sur l'eau jusqu'a toi,
     elle vise ta coque ; de pres, la machine arriere pour se mettre bord a bord. Coincee contre une rive, elle
     recule un instant.
   - Elle arraisonne : bord a bord (`ABORDAGE_PX` entre les coques), ta coque presque arretee, et c'est
     l'arrestation — comme un agent qui te met la main dessus.
   - Elle s'en va : quand on n'en veut plus, elle s'efface HORS CHAMP, jamais sous tes yeux.

   ⚠️ Conduite par `conducteur: 'vedette'` — pas `'police'` : `Police.autos` compte ceux-la comme des
   autos-patrouilles, et `Police.commandes` les mene sur les rails de la rue. */
'use strict';

const Vedette = (function () {
  //: Jusqu'ou le champ va chercher (tuiles), et ou elle nait (en pas de champ depuis le joueur).
  const PORTEE = 60, NAISSANCE = [20, 34];
  //: Le champ se refait toutes les N images ; la naissance et le menage, toutes les M.
  const CHAMP_TOUTES_LES = 30, NAISSANCE_TOUTES_LES = 30;
  //: Combien de tuiles devant elle vise, sur la pente ; sous quelle distance elle te vise tout droit (px).
  const VISEE_TUILES = 3, DIRECT_PX = 110;
  //: Bord a bord : l'ecart entre les deux coques (px) ; ta coque « arretee » sous cette vitesse.
  const ABORDAGE_PX = 18, ARRETE_SOUS = 0.5;
  //: Coincee : sans avancer ce nombre d'images, elle recule autant.
  const COINCEE_IMAGES = 50, RECUL_IMAGES = 40;

  let champ = null;          // { tx, ty, t, w, h, dist: Int16Array } — les distances depuis le joueur

  function vedettes() {
    return B.entites.filter(function (e) { return e.type === 'vehicule' && e.conducteur === 'vedette' && e.etat !== 'epave'; });
  }

  /** La coque que mene le joueur, ou null. */
  function coqueDuJoueur() {
    const v = B.joueur && B.joueur.dansVehicule;
    return v && v.def && v.def.eau ? v : null;
  }

  function voulues() {
    const e = B.recherche ? B.recherche.etoiles : 0;
    // ⚠️ L'ILE EST UN REFUGE pour toute la police (`Police.auRefuge`) : la vedette n'y vient pas.
    if (!coqueDuJoueur() || e <= 0 || Police.auRefuge()) return 0;
    return e >= 3 ? 2 : 1;
  }

  // --- Le champ des distances, sur l'eau --------------------------------------------------------------

  function calculerChamp() {
    const c = Monde.carte, j = B.joueur;
    const tx0 = Math.floor(j.x / TT), ty0 = Math.floor(j.y / TT);
    const w = c.w, h = c.h;
    const dist = (champ && champ.dist.length === w * h) ? champ.dist : new Int16Array(w * h);
    dist.fill(-1);
    champ = { tx: tx0, ty: ty0, t: B.t, w: w, h: h, dist: dist };
    if (tx0 < 0 || ty0 < 0 || tx0 >= w || ty0 >= h) return;
    const file = [tx0 + ty0 * w];
    dist[file[0]] = 0;
    for (let i = 0; i < file.length; i++) {
      const k = file[i], x = k % w, y = (k - x) / w, d = dist[k];
      if (d >= PORTEE * 2) continue;
      for (const p of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = x + p[0], ny = y + p[1];
        if (nx < 0 || ny < 0 || nx >= w || ny >= h || Math.abs(nx - tx0) > PORTEE || Math.abs(ny - ty0) > PORTEE) continue;
        const n = nx + ny * w;
        if (dist[n] >= 0 || !Monde.estEau(nx, ny)) continue;
        dist[n] = d + 1;
        file.push(n);
      }
    }
  }

  /** La distance par l'eau de (tx, ty) jusqu'au joueur, en tuiles ; -1 si l'eau n'y mene pas. */
  function distance(tx, ty) {
    if (!champ || champ.t + CHAMP_TOUTES_LES <= B.t || champ.w !== Monde.carte.w) calculerChamp();
    if (tx < 0 || ty < 0 || tx >= champ.w || ty >= champ.h) return -1;
    return champ.dist[tx + ty * champ.w];
  }

  /** De l'eau franche : la tuile et ses huit voisines (une coque y tient sans racler). */
  function franche(tx, ty) {
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) if (!Monde.estEau(tx + dx, ty + dy)) return false;
    return true;
  }

  // --- Naitre et s'en aller -----------------------------------------------------------------------------

  function naitre() {
    distance(0, 0);
    const c = champ, places = [];
    for (let y = Math.max(0, c.ty - PORTEE); y <= Math.min(c.h - 1, c.ty + PORTEE); y++) {
      for (let x = Math.max(0, c.tx - PORTEE); x <= Math.min(c.w - 1, c.tx + PORTEE); x++) {
        const d = c.dist[x + y * c.w];
        if (d < NAISSANCE[0] || d > NAISSANCE[1] || !franche(x, y)) continue;
        if (Entites.visibleAEcran(x * TT + 8, y * TT + 8, 40)) continue;
        places.push([x, y]);
      }
    }
    if (!places.length) return null;
    const p = places[Math.floor(B.rng() * places.length)];
    const cap = capVersLeJoueur(p[0], p[1]);
    const v = Vehicules.creer('vedette', p[0] * TT + 8, p[1] * TT + 8, cap, { conducteur: 'vedette', etat: 'roule', sirene: true });
    if (!v) return null;
    v.pilote = { swaps: Police.paletteAgent() };
    return v;
  }

  function maj() {
    if (!B.partie || B.interieur || B.bloc || !Monde.carte || !B.joueur) return;
    const voulu = voulues(), presentes = vedettes();
    if (B.t % NAISSANCE_TOUTES_LES === 0) {
      // Le menage : celles de trop s'effacent hors champ, jamais sous les yeux.
      let n = presentes.length;
      for (const v of presentes) {
        if (n <= voulu) break;
        if (!Entites.visibleAEcran(v.x, v.y, 60)) { Entites.retirer(v); n--; }
      }
      if (n < voulu) naitre();
    }
    arraisonner();
  }

  // --- Le pilote ----------------------------------------------------------------------------------------

  /** Le cap qui descend la pente du champ depuis (tx, ty), `VISEE_TUILES` pas plus loin. */
  function capVersLeJoueur(tx, ty) {
    let x = tx, y = ty;
    for (let pas = 0; pas < VISEE_TUILES; pas++) {
      let meilleur = null, dMin = distance(x, y);
      if (dMin <= 0) break;
      for (const p of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) {
        const nx = x + p[0], ny = y + p[1], d = distance(nx, ny);
        // En diagonale, seulement si les deux tuiles d'angle sont de l'eau : on ne coupe pas un coin de quai.
        if (d < 0 || (p[0] && p[1] && (!Monde.estEau(x + p[0], y) || !Monde.estEau(x, y + p[1])))) continue;
        if (d < dMin || (d === dMin && meilleur && franche(nx, ny) && !franche(meilleur[0], meilleur[1]))) { dMin = d; meilleur = [nx, ny]; }
      }
      if (!meilleur) break;
      x = meilleur[0]; y = meilleur[1];
    }
    return angleVers(tx * TT + 8, ty * TT + 8, x * TT + 8, y * TT + 8);
  }

  /** De l'eau tout du long, de (x0, y0) a (x1, y1) ? Un pas de 8 px. */
  function eauTouteLaLigne(x0, y0, x1, y1) {
    const n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / 8));
    for (let i = 0; i <= n; i++) {
      const x = x0 + (x1 - x0) * i / n, y = y0 + (y1 - y0) * i / n;
      if (!Monde.estEau(Math.floor(x / TT), Math.floor(y / TT))) return false;
    }
    return true;
  }

  const AU_REPOS = { gaz: 0, frein: 0, direction: 0, freinMain: false };

  function commandes(v) {
    const cible = coqueDuJoueur();
    if (!cible) return AU_REPOS;
    // Coincee contre une rive : elle recule un instant, la barre a l'oppose.
    if (v.reculT > 0) { v.reculT--; return { gaz: 0, frein: 1, direction: -(v.barreRecul || 1), freinMain: false }; }
    const d = Math.hypot(cible.x - v.x, cible.y - v.y);
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    const direct = d < DIRECT_PX && eauTouteLaLigne(v.x, v.y, cible.x, cible.y);
    const cap = direct ? angleVers(v.x, v.y, cible.x, cible.y) : capVersLeJoueur(tx, ty);
    const ecart = ecartAngle(v.angle, cap);
    const direction = borner(ecart * 2.2, -1, 1);
    // De pres : on se met a la vitesse de la coque, pour venir bord a bord sans l'eperonner.
    const bord = (v.def.largeur + cible.def.largeur) / 2 + ABORDAGE_PX;
    let gaz = Math.abs(ecart) < 1.4 ? 1 : 0.35, frein = 0;
    if (direct && d < bord + 40) {
      const voulue = Math.max(0.4, Math.abs(cible.vitesse) + (d > bord ? 0.5 : 0));
      if (v.vitesse > voulue + 0.3) { gaz = 0; frein = 1; } else if (v.vitesse > voulue) gaz = 0;
    }
    // Coincee : du gaz et pas d'erre depuis `COINCEE_IMAGES`.
    if (gaz > 0 && Math.abs(v.vitesse) < 0.2) v.coinceT = (v.coinceT || 0) + 1; else v.coinceT = 0;
    if (v.coinceT > COINCEE_IMAGES) { v.coinceT = 0; v.reculT = RECUL_IMAGES; v.barreRecul = direction >= 0 ? 1 : -1; }
    return { gaz: gaz, frein: frein, direction: direction, freinMain: false };
  }

  // --- Arraisonner --------------------------------------------------------------------------------------

  function arraisonner() {
    const j = B.joueur, c = coqueDuJoueur(), r = B.recherche;
    if (!c || r.etoiles <= 0 || j.arrete || j.intouchable || B.menu || triche('pasArrete') || Police.auRefuge()) return;
    if (Math.abs(c.vitesse) >= ARRETE_SOUS) return;
    for (const v of vedettes()) {
      const ecart = Math.hypot(v.x - c.x, v.y - c.y) - (v.def.largeur + c.def.largeur) / 2;
      if (ecart > ABORDAGE_PX) continue;
      Hud.message('ARRAISONNÉ !', 180);
      Vehicules.descendre(j, true);
      Missions.arrestation(null);
      return;
    }
  }

  /** Nouvelle partie, partie chargee : le champ d'avant ne vaut plus rien. */
  function oublier() { champ = null; }

  return { voulues, vedettes, distance, maj, commandes, oublier };
})();
