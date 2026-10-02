/* Bandini — le caddie qu'on pousse (le décor, les bêtes et les gens répondent, deuxième vague, 2 oct. 2026).

   Tranché par Martin : le caddie couché de la ville se FOUILLE d'abord (`Interactions`, ACTION), puis
   se REDRESSE et se POUSSE à pied — il roule, il heurte, il sert de bélier, et il reste là où on le
   laisse. Les nombres et les mots sont dans `app/interactions.py` (`CADDIE`) : ici, on ne fait que
   le faire rouler.

   ⚠️ **LE CADDIE RESTE LE DÉCOR QU'IL ÉTAIT.** Redressé, c'est la MÊME entité (`decor: 'caddie'`
   devient `'caddie_debout'`) : aucun numéro neuf (`Entites.creer`), aucune naissance — la suite des
   identifiants de la ville ne bouge pas d'un cran. Il bouge par `Entites.replacerDecor`, qui tient
   l'index fixe à jour : la foule bute sur lui là où il est, pas là où il était.

   ⚠️ **POUSSER, C'EST MARCHER DEDANS.** Aucun bouton : `Entites.majJoueur` arrête le joueur contre
   sa boîte (il est solide, comme avant), et ici, un peu plus tard dans la même image, le caddie prend
   la vitesse de qui marche vers lui (`pousse_x` de plus : il part devant). Lâché, il roule sur sa
   lancée et ralentit (`frottement`).

   ⚠️ **LE BÉLIER NE BLESSE PERSONNE.** Lancé au SPRINT (`j.sprinte`, ESQUIVE tenue — l'hiver sans bottes
   compris, où la neige le ralentit), et tant qu'il garde `belier` de vitesse, il BOUSCULE le passant
   qu'il touche — le recul d'un coup sans le coup : ni PV, ni délit, ni alerte, juste un pas de côté et
   un mot — et il COGNE le char (quelques PV de tôle, l'alarme d'un char garé qui en a une). Plus lent,
   il s'arrête contre lui. Un char plus rapide que lui le pousse ; un char lancé l'écrase (son décor
   `casse`, `Vehicules.heurterDecor`), et la ville le répare au matin, là où il était.

   ⚠️ **IL RESTE LÀ OÙ ON LE LAISSE** : `partie.caddies`, la tuile de naissance → `[x, y, pose]`, et
   `poser()` le remet debout à sa place quand la partie se rouvre. Sans dé, nulle part : la fouille
   tire UN `B.rng()` à la pression, comme un bac ; le reste se lit à l'empreinte. */

const Caddies = (function () {
  'use strict';

  function cfg() { return B.defs && B.defs.interactions && B.defs.interactions.caddie; }

  //: Les caddies de la ville, couchés ou debout : posés par `poser()` à chaque partie.
  let liste = [];

  //: Au-delà de cette distance du joueur, un caddie immobile dort : il n'y a personne pour le pousser.
  const EVEIL_PX = 64;
  //: Un char ne le cogne qu'une fois par choc (sinon chaque image du contact repeserait sur la tôle).
  const REPIT_CHOC = 20;

  function cle(d) { return Math.floor(d.chezCaddie.x / TT) + ',' + Math.floor(d.chezCaddie.y / TT); }

  function estDebout(d) { const c = cfg(); return !!c && d.decor === c.debout; }

  /** Les caddies de la partie, et ceux qu'on a redressés remis à leur place (`partie.caddies`).
      Appelé par `Jeu.commencer`, juste après `Entites.creerDecor` : avant la foule. */
  function poser() {
    const c = cfg();
    liste = [];
    if (!c) return;
    const gardes = (B.partie && B.partie.caddies) || {};
    for (const d of B.entites) {
      if (d.type !== 'decor' || (c.decors.indexOf(d.decor) < 0 && d.decor !== c.debout)) continue;
      d.chezCaddie = d.chezCaddie || { x: d.x, y: d.y };
      d.vx = 0; d.vy = 0;
      liste.push(d);
      const g = gardes[cle(d)];
      if (!Array.isArray(g) || !isFinite(g[0]) || !isFinite(g[1])) continue;
      d.decor = c.debout; d.v = (g[2] | 0) % 4;
      Entites.replacerDecor(d, g[0], g[1]);
    }
  }

  function retenir(d) {
    const p = B.partie;
    if (!p) return;
    p.caddies = p.caddies || {};
    p.caddies[cle(d)] = [Math.round(d.x), Math.round(d.y), d.v | 0];
  }

  /** REDRESSER : il se remet sur ses roues, poignée vers nous. */
  function redresser(j, d) {
    const c = cfg();
    j.animT = 16; j.animType = 'ramasse';
    d.decor = c.debout;
    d.v = poignee(d.x - j.x, d.y - j.y);
    d.vx = 0; d.vy = 0;
    retenir(d);
    Hud.message(c.redresse);
    Son.SFX.choc('choc_leger');
    return true;
  }

  /** Le côté de la poignée quand on pousse dans la direction (dx, dy) : celui d'où l'on vient. */
  function poignee(dx, dy) {
    if (Math.abs(dx) > Math.abs(dy)) return dx > 0 ? 2 : 3;
    return dy < 0 ? 0 : 1;
  }

  // --- Ce qui le met en branle ---------------------------------------------------------

  /** Un joueur à pied qui marche DANS le caddie le pousse : il prend sa vitesse, un peu plus. */
  function pousseeDesJoueurs(d, c) {
    for (const j of Entites.joueurs()) {
      if (!j.vivant || j.dansVehicule || j.assis || j.nage) continue;
      const vx = j.vx || 0, vy = j.vy || 0;
      if (!vx && !vy) continue;
      if (!Entites.boiteTouche(d, j.x, j.y, j.r + 1.5)) continue;
      if (vx * (d.x - j.x) + vy * (d.y - j.y) <= 0) continue;
      d.vx = vx * c.pousse_x; d.vy = vy * c.pousse_x;
      d.v = poignee(vx, vy);
      // ⚠️ LANCÉ AU SPRINT, il part en bélier — pas à la course de tous les jours. Une vitesse seule ne le
      // dirait pas : l'hiver, sans bottes, un sprint dans la neige va moins vite que la course de l'été.
      d.lance = !!j.sprinte;
      return;
    }
  }

  /** Le char qui le touche : plus vite que lui, il le pousse ; moins vite, c'est le caddie qui cogne
      (lancé en bélier) ou qui s'arrête contre la tôle. */
  function heurterLesChars(d, c, v) {
    for (const q of Entites.autour(d.x, d.y, 40, function (e) { return e.type === 'vehicule' && e.etat !== 'epave'; })) {
      if (!Vehicules.cercles(q).some(function (k) { return Entites.boiteTouche(d, k.x, k.y, k.r); })) continue;
      const vq = Math.hypot(q.vx || 0, q.vy || 0);
      // Le char qui ROULE VERS lui le pousse devant (un char qui s'en éloigne le laisse).
      if (vq > v && vq > 0.2) {
        if (q.vx * (d.x - q.x) + q.vy * (d.y - q.y) > 0) { d.vx = q.vx * c.pousse_x; d.vy = q.vy * c.pousse_x; }
        return;
      }
      if (d.lance && v >= c.belier && (!d.chocT || B.t - d.chocT > REPIT_CHOC)) {
        d.chocT = B.t;
        Vehicules.endommager(q, c.degats_char, null);
        // ⚠️ La règle de deux chars qui se touchent (`Vehicules.heurterVehicules`) : un char garé qui a une
        // alarme la fait entendre — personne ne vole rien, c'est du bruit.
        if (q.etat === 'stationne' && !q.conducteur && q.def.alarme && !(q.alarme > 0)) Vehicules.declencherAlarme(q);
        Son.depuis(d, function () { Son.SFX.choc('choc_leger'); });
        Entites.poussiere(d.x, d.y, 3);
      }
      d.vx = -d.vx * c.rebond; d.vy = -d.vy * c.rebond;
      return;
    }
  }

  /** Le passant DEVANT lui : lancé en bélier, il le bouscule — un pas de côté, un mot, jamais un coup ;
      sinon, il s'arrête contre lui (on ne roule pas à travers les gens). */
  function heurterLesGens(d, c, v) {
    for (const e of Entites.pietonsAutour(d.x, d.y, 16)) {
      if (e.etat === 'assomme' || e.dansVehicule || !e.vivant) continue;
      if (!Entites.boiteTouche(d, e.x, e.y, e.r + 1) || d.vx * (e.x - d.x) + d.vy * (e.y - d.y) <= 0) continue;
      if (!d.lance || v < c.belier || e.personnage || e.mission || e.recul > 0) { d.vx = 0; d.vy = 0; return; }
      e.recul = 12;
      e.vx = d.vx / v * 1.8; e.vy = d.vy / v * 1.8;
      Entites.bulle(e, c.bouscule[e.id % c.bouscule.length], { duree: 90 });
      Son.depuis(d, function () { Son.SFX.choc('choc_corps'); });
      d.vx *= 0.5; d.vy *= 0.5;
      return;
    }
  }

  /** Une image de roulement : axe par axe, comme un corps (`Entites.deplacerCercle`) — un mur
      renvoie l'axe qui l'a touché, l'autre continue. */
  function rouler(d, c) {
    let v = Math.hypot(d.vx, d.vy);
    if (v > c.vitesse_max) { d.vx *= c.vitesse_max / v; d.vy *= c.vitesse_max / v; v = c.vitesse_max; }
    let cogne = 0;
    if (d.vx) {
      if (Entites.decorPeutAller(d, d.x + d.vx, d.y) && !porteSous(d, d.x + d.vx, d.y)) Entites.replacerDecor(d, d.x + d.vx, d.y);
      else { cogne = Math.max(cogne, Math.abs(d.vx)); d.vx = -d.vx * c.rebond; }
    }
    if (d.vy) {
      if (Entites.decorPeutAller(d, d.x, d.y + d.vy) && !porteSous(d, d.x, d.y + d.vy)) Entites.replacerDecor(d, d.x, d.y + d.vy);
      else { cogne = Math.max(cogne, Math.abs(d.vy)); d.vy = -d.vy * c.rebond; }
    }
    if (cogne > 1.2 && (!d.chocT || B.t - d.chocT > REPIT_CHOC)) {
      d.chocT = B.t;
      Son.depuis(d, function () { Son.SFX.choc('choc_leger'); });
    }
    d.vx *= c.frottement; d.vy *= c.frottement;
    // Le bélier s'essouffle avec sa vitesse : sous `belier`, ce n'est plus qu'un caddie qui roule.
    if (Math.hypot(d.vx, d.vy) < c.belier) d.lance = false;
    if (Math.hypot(d.vx, d.vy) < 0.05) { d.vx = 0; d.vy = 0; }
    retenir(d);
  }

  /** ⚠️ Pas sur un pas de porte : un caddie laissé devant une porte la boucherait à la foule (et au
      joueur qui sort). La boîte entière, ses quatre coins. */
  function porteSous(d, nx, ny) {
    const sol = DECORS[d.decor].sol;
    for (const sx of [-1, 1]) {
      for (const sy of [-1, 1]) {
        if (Monde.porteA(Math.floor((nx + sx * sol[0]) / TT), Math.floor((ny + sy * sol[1]) / TT))) return true;
      }
    }
    return false;
  }

  // --- À chaque image -------------------------------------------------------------------

  function maj() {
    const c = cfg(), j = B.joueur;
    if (!c || !j || B.interieur || B.bloc || !liste.length) return;
    for (const d of liste) {
      if (d.brise || !estDebout(d)) continue;
      const bouge = d.vx || d.vy;
      if (!bouge && dist2(d.x, d.y, j.x, j.y) > EVEIL_PX * EVEIL_PX && !Entites.autour(d.x, d.y, 40, function (e) { return e.type === 'vehicule'; }).length) continue;
      pousseeDesJoueurs(d, c);
      const v = Math.hypot(d.vx, d.vy);
      heurterLesChars(d, c, v);
      if (!d.vx && !d.vy) continue;
      heurterLesGens(d, c, v);
      if (d.vx || d.vy) rouler(d, c);
    }
  }

  return { poser, redresser, maj, estDebout, cle: function (d) { return d.chezCaddie ? cle(d) : null; },
           liste: function () { return liste; } };
})();
