/* Bandini — vehicules : physique arcade, collisions par cercles, trafic.

   Un char est une CHAINE DE CERCLES (trois, le long de son axe) : c'est ce
   qui permet de tester un mur, un autre char ou un pieton avec la meme
   fonction, et de tourner sans boite orientee. Au-dessus de `sous_pas_px`
   par image, le deplacement est decoupe : deux cercles ne se croisent jamais
   sans se voir.

   Le trafic ne connait pas de graphe : il LIT le champ `voie` de la carte,
   tuile par tuile. Sur un croisement, il choisit une sortie ; a une ligne
   d'arret, il regarde le feu. Quand il veut tourner a gauche, il traverse le
   croisement avant de virer — parce qu'il cherche la voie dont la fleche va
   dans son sens, et qu'elle est de l'autre cote. */

const Vehicules = (function () {
  'use strict';

  const ROTATIONS = 32;
  const PAS_FLECHE = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] };
  const FLECHE_DE = { '1,0': '>', '-1,0': '<', '0,-1': '^', '0,1': 'v' };

  /** Facteur de braquage selon la vitesse relative (0 a l'arret, plein vers 0,3). */
  function courbeBraquage(t) {
    t = borner(Math.abs(t), 0, 1);
    if (t < 0.3) return t / 0.3;
    return 1 - (t - 0.3) * 0.65;
  }

  function vehiculeDef(slug) {
    return (B.defs.vehicules || []).find(function (v) { return v.slug === slug; }) || null;
  }

  function trafic() { return B.defs.conduite.trafic; }
  function physique() { return B.defs.conduite.physique; }

  // --- Naissance ------------------------------------------------------------------

  function creer(slug, x, y, angle, options) {
    const def = vehiculeDef(slug);
    if (!def) return null;
    const couleur = def.couleurs[Math.floor(B.rng() * def.couleurs.length)];
    const v = Entites.creer('vehicule', x, y, Object.assign({
      slug: slug, def: def, angle: angle || 0, vitesse: 0, vx: 0, vy: 0, z: 0, vz: 0,
      r: def.largeur / 2, vie: def.vie, vieMax: def.vie, couleur: couleur, swaps: { c: couleur },
      conducteur: null, etat: 'stationne', cible: null, sens: null, sortie: null,
      patience: 0, force: 0, alarme: 0, klaxonT: 0, chocs: 0, agresseur: null,
      vole: false, epaveT: 0, solide: false, vivant: true, sprite: def.sprite,
    }, options || {}));
    return v;
  }

  /** Un type de char selon les poids du catalogue (phase 1 seulement). */
  function typeDeRue() {
    const types = B.defs.vehicules.filter(function (v) { return v.phase === 1 && v.frequence > 0; });
    let tirage = B.rng() * types.reduce(function (s, v) { return s + v.frequence; }, 0);
    for (const v of types) { tirage -= v.frequence; if (tirage <= 0) return v; }
    return types[0];
  }

  function libreAutour(x, y, rayon) {
    return Entites.autour(x, y, rayon, function (e) { return e.type === 'vehicule' || e.type === 'joueur'; }).length === 0;
  }

  /** Une tuile de voie (fleche) dans la bulle, hors ecran, sans char dessus. */
  function placeDansLeTrafic() {
    const t = trafic(), c = Monde.carte, j = B.joueur;
    for (let essai = 0; essai < 20; essai++) {
      const a = B.rng() * Math.PI * 2;
      const d = t.naissance_px + B.rng() * (t.oubli_px - t.naissance_px - 80);
      const tx = Math.floor((j.x + Math.cos(a) * d) / TT), ty = Math.floor((j.y + Math.sin(a) * d) / TT);
      if (tx < 1 || ty < 1 || tx >= c.w - 1 || ty >= c.h - 1) continue;
      const f = Monde.fleche(tx, ty);
      if (!PAS_FLECHE[f]) continue;
      const x = tx * TT + 8, y = ty * TT + 8;
      if (Entites.visibleAEcran(x, y, 40) || !libreAutour(x, y, 48)) continue;
      const pas = PAS_FLECHE[f];
      return { x: x, y: y, angle: Math.atan2(pas[1], pas[0]), sens: f };
    }
    return null;
  }

  function placeStationnee() {
    const t = trafic(), c = Monde.carte, j = B.joueur;
    for (let essai = 0; essai < 20; essai++) {
      const a = B.rng() * Math.PI * 2;
      const d = t.naissance_px * 0.6 + B.rng() * (t.oubli_px - t.naissance_px);
      const tx = Math.floor((j.x + Math.cos(a) * d) / TT), ty = Math.floor((j.y + Math.sin(a) * d) / TT);
      if (tx < 1 || ty < 2 || tx >= c.w - 1 || ty >= c.h - 1) continue;
      if (Monde.glyphe(tx, ty) !== 'p' || Monde.glyphe(tx, ty - 1) !== 'p') continue;
      const x = tx * TT + 8, y = ty * TT;
      if (Entites.visibleAEcran(x, y, 40) || !libreAutour(x, y, 40)) continue;
      return { x: x, y: y, angle: -Math.PI / 2 };
    }
    return null;
  }

  /** Comme les pietons : naitre hors champ, s'oublier hors de la bulle. */
  function peupler() {
    const t = trafic(), j = B.joueur;
    let roulent = 0, stationnes = 0;
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const v = B.entites[i];
      if (v.type !== 'vehicule') continue;
      const loin = dist2(v.x, v.y, j.x, j.y) > t.oubli_px * t.oubli_px;
      if (loin && v.conducteur !== j && !Entites.visibleAEcran(v.x, v.y, 60)) { Entites.retirer(v); continue; }
      if (v.etat === 'epave') continue;
      if (v.conducteur === 'trafic') roulent++; else if (v.conducteur !== j) stationnes++;
    }
    if (B.t % 20 !== 0) return;
    const zone = Monde.zoneA(j.x, j.y);
    const voulu = Math.min(t.vehicules_max, zone ? zone.vehicules : 6);
    if (roulent < voulu) {
      const place = placeDansLeTrafic();
      if (place) {
        const v = creer(typeDeRue().slug, place.x, place.y, place.angle, { conducteur: 'trafic', etat: 'roule', sens: place.sens });
        if (v) v.vitesse = v.def.vitesse_max * t.vitesse_ville * 0.5;
      }
    } else if (stationnes < t.stationnes_max && B.t % 40 === 0) {
      const place = placeStationnee();
      if (place) creer(typeDeRue().slug, place.x, place.y, place.angle, { etat: 'stationne' });
    }
  }

  // --- Geometrie : la chaine de cercles ------------------------------------------

  function cercles(v, x, y, angle) {
    const n = physique().cercles;
    const demi = v.def.longueur / 2 - v.r;
    const out = [];
    const cx = Math.cos(angle === undefined ? v.angle : angle), cy = Math.sin(angle === undefined ? v.angle : angle);
    for (let i = 0; i < n; i++) {
      const t = n === 1 ? 0 : -demi + (2 * demi) * i / (n - 1);
      out.push({ x: (x === undefined ? v.x : x) + cx * t, y: (y === undefined ? v.y : y) + cy * t, r: v.r });
    }
    return out;
  }

  /** Un des cercles touche-t-il une tuile qui bloque un char ? (en l'air : non) */
  function bloqueParLesTuiles(v, x, y) {
    if (v.z > 6) return false;
    for (const c of cercles(v, x, y)) {
      const tx0 = Math.floor((c.x - c.r) / TT), tx1 = Math.floor((c.x + c.r) / TT);
      const ty0 = Math.floor((c.y - c.r) / TT), ty1 = Math.floor((c.y + c.r) / TT);
      for (let ty = ty0; ty <= ty1; ty++) {
        for (let tx = tx0; tx <= tx1; tx++) {
          if (Monde.bloque(tx, ty, Monde.MASQUE_VEHICULE)) return true;
        }
      }
    }
    return false;
  }

  // --- Physique -------------------------------------------------------------------

  /** Une image de conduite : gaz, frein, direction (-1..1), frein a main. */
  function majPhysique(v, cmd) {
    const d = v.def;
    if (cmd.gaz > 0) v.vitesse += d.acceleration * cmd.gaz;
    if (cmd.frein > 0) {
      if (v.vitesse > 0.15) v.vitesse -= d.frein * cmd.frein;
      else v.vitesse -= d.acceleration * 0.7 * cmd.frein;      // marche arriere
    }
    if (cmd.freinMain) v.vitesse *= 0.965;
    v.vitesse *= d.friction;
    v.vitesse = borner(v.vitesse, -d.vitesse_recul, d.vitesse_max);
    if (Math.abs(v.vitesse) < 0.02 && !cmd.gaz && !cmd.frein) v.vitesse = 0;
    const t = v.vitesse / d.vitesse_max;
    if (cmd.direction) {
      v.angle += cmd.direction * d.braquage * courbeBraquage(t) * (v.vitesse < 0 ? -1 : 1) * (cmd.freinMain ? 1.35 : 1);
    }
    // Adherence : la vitesse reelle glisse vers le cap. Frein a main : elle traine.
    const adh = cmd.freinMain ? d.adherence_frein : d.adherence;
    v.vx += (Math.cos(v.angle) * v.vitesse - v.vx) * adh;
    v.vy += (Math.sin(v.angle) * v.vitesse - v.vy) * adh;
    // En l'air (rampe) : on retombe.
    if (v.z > 0 || v.vz !== 0) {
      v.z += v.vz; v.vz -= physique().gravite;
      if (v.z <= 0) { v.z = 0; v.vz = 0; }
    }
  }

  /** Le deplacement, decoupe en sous-pas, avec les tuiles, les chars, les gens. */
  function avancer(v) {
    const ph = physique();
    const vitesse = Math.hypot(v.vx, v.vy);
    const n = Math.max(1, Math.ceil(vitesse / ph.sous_pas_px));
    const px = v.vx / n, py = v.vy / n;
    for (let i = 0; i < n; i++) {
      // Axe par axe : un mur de face arrete, un mur de cote fait glisser.
      let choc = 0;
      if (px !== 0) {
        if (bloqueParLesTuiles(v, v.x + px, v.y)) { choc = Math.max(choc, Math.abs(v.vx)); v.vx = -v.vx * ph.choc_rebond; }
        else v.x += px;
      }
      if (py !== 0) {
        if (bloqueParLesTuiles(v, v.x, v.y + py)) { choc = Math.max(choc, Math.abs(v.vy)); v.vy = -v.vy * ph.choc_rebond; }
        else v.y += py;
      }
      if (choc >= ph.choc_vitesse_min) {
        heurterMur(v, choc);
        break;
      }
      if (choc > 0) v.vitesse *= 0.5;
    }
    Entites.dansLaCarte(v);
    heurterVehicules(v);
    heurterPietons(v);
    // La rampe : on decolle a la sortie.
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    if (v.z === 0 && Math.abs(v.vitesse) > 1.5 && Monde.estRampe(tx, ty)) v.vz = Math.abs(v.vitesse) * ph.rampe_impulsion;
  }

  function heurterMur(v, force) {
    const ph = physique();
    v.vitesse *= -ph.choc_rebond;
    v.chocs++;
    endommager(v, Math.round(force * ph.choc_degats_par_px), null);
    Entites.poussiere(v.x + Math.cos(v.angle) * v.def.longueur / 2, v.y + Math.sin(v.angle) * v.def.longueur / 2, 6);
    if (v.conducteur === B.joueur) {
      B.cam.secousse = Math.min(1.2, force * 0.3);
      Entree.vibrer(Math.round(force * 12));
      if (force >= ph.ejection_vitesse_min && v.def.ejecte) ejecter(B.joueur, v);
    }
    Son.SFX.choc();
  }

  function heurterVehicules(v) {
    const ph = physique();
    const miens = cercles(v);
    const portee = v.def.longueur + 20;
    for (const autre of Entites.autour(v.x, v.y, portee, function (e) { return e.type === 'vehicule' && e !== v; })) {
      const siens = cercles(autre);
      for (const a of miens) {
        for (const b of siens) {
          const dx = b.x - a.x, dy = b.y - a.y;
          const d2 = dx * dx + dy * dy, min = a.r + b.r;
          if (d2 >= min * min || d2 === 0) continue;
          const d = Math.sqrt(d2), nx = dx / d, ny = dy / d, chevauche = min - d;
          const m1 = v.def.masse, m2 = autre.def.masse, total = m1 + m2;
          v.x -= nx * chevauche * (m2 / total); v.y -= ny * chevauche * (m2 / total);
          autre.x += nx * chevauche * (m1 / total); autre.y += ny * chevauche * (m1 / total);
          const relatif = (v.vx - autre.vx) * nx + (v.vy - autre.vy) * ny;
          // ⚠️ Le trafic ne s'entretue pas : deux chars sur leurs rails qui se
          // frolent a un coin se poussent, sans degats. Les chocs qui comptent
          // sont ceux ou le joueur est au volant d'un des deux.
          const joueurImplique = v.conducteur === B.joueur || autre.conducteur === B.joueur;
          if (relatif > ph.choc_vitesse_min && joueurImplique) {
            const degats = Math.round(relatif * ph.choc_degats_par_px);
            endommager(autre, degats, v.conducteur === B.joueur ? B.joueur : null);
            endommager(v, Math.round(degats * 0.6), autre.conducteur === B.joueur ? B.joueur : null);
            v.chocs++; autre.chocs++;
            v.vx -= nx * relatif * 0.6; v.vy -= ny * relatif * 0.6;
            autre.vx += nx * relatif * 0.6 * (m1 / m2); autre.vy += ny * relatif * 0.6 * (m1 / m2);
            v.vitesse *= 0.5; autre.vitesse *= 0.7;
            Son.SFX.choc();
            if (v.conducteur === B.joueur) {
              B.cam.secousse = 0.7;
              if (autre.alarme === 0 && autre.def.alarme && !autre.conducteur) declencherAlarme(autre);
              if (relatif > 2) Police.signalerCrime('conduite_dangereuse', v.x, v.y, Police.quelqu_un_voit(v.x, v.y, null));
            }
            if (autre.conducteur === 'trafic') autre.klaxonT = 30;
          }
          return;   // un contact par image suffit
        }
      }
    }
  }

  /** Les gens : bouscules a basse vitesse, renverses au-dela. Les enfants,
      eux, ne sont que bouscules — c'est la regle. */
  function heurterPietons(v) {
    const ph = physique();
    const vitesse = Math.hypot(v.vx, v.vy);
    for (const c of cercles(v)) {
      for (const p of Entites.autour(c.x, c.y, c.r + 8, function (e) {
        return (e.type === 'pieton' || (e.type === 'joueur' && !e.dansVehicule)) && e.vivant;
      })) {
        const dx = p.x - c.x, dy = p.y - c.y;
        const d = Math.hypot(dx, dy) || 1, min = c.r + p.r;
        if (d >= min) continue;
        const nx = dx / d, ny = dy / d;
        p.x = c.x + nx * min; p.y = c.y + ny * min;
        if (vitesse >= ph.renverse_vitesse_min && !p.intouchable && p.etat !== 'assomme') {
          const degats = Math.round(vitesse * ph.renverse_degats_par_px);
          const avant = p.vivant;
          Entites.blesser(p, degats, v.conducteur === B.joueur ? B.joueur : v, {
            renverse: true, angle: Math.atan2(v.vy, v.vx), saigne: 60,
          });
          p.vx = v.vx * 1.2; p.vy = v.vy * 1.2;
          v.vitesse *= 0.85;
          if (v.conducteur === B.joueur && p.type === 'pieton') {
            const type = (avant && !p.vivant) ? 'renversement_mortel' : 'renversement';
            Police.signalerCrime(type, p.x, p.y, Police.quelqu_un_voit(p.x, p.y, p));
            B.cam.secousse = 0.5;
          }
        } else if (p.type === 'pieton' && vitesse > 0.3 && p.etat === 'flane') {
          p.etat = 'fuit'; p.menace = v; p.minuterie = 90; p.cri = 60;
        }
      }
    }
  }

  // --- Degats, feu, explosion ------------------------------------------------------

  function endommager(v, degats, source) {
    if (v.etat === 'epave' || degats <= 0) return;
    v.vie -= degats;
    if (source) v.agresseur = source;
    if (v.vie <= 0) exploser(v);
  }

  function majEtatDuChar(v) {
    const ph = physique();
    if (v.etat === 'epave') {
      if (v.epaveT > 0) v.epaveT--;
      if (B.t % 6 === 0) Entites.particule(v.x + (B.rng() - 0.5) * 14, v.y - 4, (B.rng() - 0.5) * 0.3, -0.2, 40, '#3a3a3a', 2, -0.01);
      return;
    }
    const part = v.vie / v.vieMax;
    if (part < ph.feu_sous) {
      if (B.t % 3 === 0) Entites.particule(v.x + (B.rng() - 0.5) * 10, v.y - 6, (B.rng() - 0.5) * 0.4, -0.5, 18, B.rng() < 0.5 ? '#ff8c1a' : '#ffd23a', 2, -0.02);
      if (B.t % 60 === 0) endommager(v, ph.feu_degats_par_seconde, v.agresseur);
    } else if (part < ph.fumee_sous && B.t % 8 === 0) {
      Entites.particule(v.x + (B.rng() - 0.5) * 8, v.y - 6, (B.rng() - 0.5) * 0.3, -0.3, 30, '#8a8a8a', 2, -0.01);
    }
    if (v.alarme > 0) {
      v.alarme--;
      if (v.alarme % 40 === 0) Son.SFX.klaxon();
    }
    if (v.klaxonT > 0) { v.klaxonT--; if (v.klaxonT === 29) Son.SFX.klaxon(); }
  }

  function exploser(v) {
    const ph = physique();
    v.etat = 'epave';
    v.vie = 0;
    v.vitesse = 0; v.vx = 0; v.vy = 0;
    v.swaps = { c: '#2a2a2a', v: '#1a1a1e', l: '#2a2a2a', t: '#2a2a2a', x: '#2a2a2a', y: '#2a2a2a' };
    v.epaveT = ph.epave_secondes * 60;
    v.alarme = 0;
    for (let i = 0; i < 40; i++) {
      const a = B.rng() * Math.PI * 2, s = 1 + B.rng() * 3;
      Entites.particule(v.x, v.y, Math.cos(a) * s, Math.sin(a) * s * 0.6, 30 + B.rng() * 20, i % 3 ? '#ff8c1a' : '#3a3a3a', 2 + (i % 2), 0.1);
    }
    Entites.decal(v.x, v.y, 'impact');
    Son.SFX.explosion();
    B.cam.secousse = Math.max(B.cam.secousse, 1.2);
    const coupable = v.agresseur === B.joueur ? B.joueur : null;
    for (const e of Entites.autour(v.x, v.y, ph.explosion_rayon_px, function (q) { return q !== v && q.vivant; })) {
      const d = Math.hypot(e.x - v.x, e.y - v.y);
      const part = 1 - d / ph.explosion_rayon_px;
      if (e.type === 'vehicule') endommager(e, Math.round(ph.explosion_degats * part), coupable);
      else if (e.type === 'pieton' || e.type === 'joueur') {
        if (e.dansVehicule === v) descendre(e, true);
        Entites.blesser(e, Math.round(ph.explosion_degats * part), coupable || v, { renverse: true, angle: angleVers(v.x, v.y, e.x, e.y), saigne: 120 });
      }
    }
    if (v.conducteur && v.conducteur !== 'trafic') descendre(v.conducteur, true);
    if (v.conducteur === 'trafic') { v.conducteur = null; }
    if (coupable) {
      Police.signalerCrime('explosion', v.x, v.y, true);
      Entites.alerter(v.x, v.y, coupable, 3);
    }
  }

  function declencherAlarme(v) {
    v.alarme = physique().alarme_secondes * 60;
    Son.SFX.klaxon();
    // L'alarme est un canal de detection : qui l'entend le sait.
    const rayon = B.defs.recherche.vision.alarme_rayon * TT;
    const entendue = Entites.pietonsAutour(v.x, v.y, rayon).some(function (e) { return e.etat !== 'assomme'; });
    return entendue;
  }

  // --- Monter, descendre, ejecter ---------------------------------------------------

  function vehiculeSousLaMain(j) {
    const portee = physique().portee_monter_px;
    let meilleur = null, dMin = Infinity;
    for (const v of Entites.autour(j.x, j.y, portee + 20, function (e) { return e.type === 'vehicule' && e.etat !== 'epave'; })) {
      for (const c of cercles(v)) {
        const d = Math.hypot(c.x - j.x, c.y - j.y) - c.r;
        if (d < dMin && d <= portee) { dMin = d; meilleur = v; }
      }
    }
    return meilleur;
  }

  function monter(j, v) {
    if (!v || v.etat === 'epave' || j.dansVehicule) return false;
    let crime = null, vu = false;
    if (v.conducteur === 'trafic' && v.def.classe === 'velo') {
      // On prend le velo au cycliste : il tombe, il a tout vu, il le dit.
      const cycliste = Entites.creerPieton(v.x, v.y + 10, Entites.archetypeDeRue());
      cycliste.etat = 'temoin'; cycliste.menace = j; cycliste.minuterie = 600; cycliste.cri = 120;
      cycliste.recul = 14; cycliste.vx = 0; cycliste.vy = 1.5;
      crime = 'vol_vehicule'; vu = true;
    } else if (v.conducteur === 'trafic') {
      // Carjacking : le conducteur sort, temoigne, et fuit. Pas besoin de temoin :
      // la victime en est un.
      const arch = Entites.archetypeDeRue();
      const victime = Entites.creerPieton(v.x + Math.cos(v.angle + Math.PI / 2) * 14, v.y + Math.sin(v.angle + Math.PI / 2) * 14, arch);
      victime.etat = 'temoin'; victime.menace = j; victime.minuterie = 600; victime.cri = 120;
      crime = 'carjacking'; vu = true;
    } else if (v.conducteur === null && !v.vole) {
      crime = 'vol_vehicule';
      vu = Police.quelqu_un_voit(v.x, v.y, null);
      if (v.def.alarme && declencherAlarme(v)) vu = true;
    }
    v.conducteur = j; v.etat = 'roule'; v.vole = v.vole || !!crime; v.cible = null;
    j.dansVehicule = v; j.dessine = false; j.vx = 0; j.vy = 0;
    j.x = v.x; j.y = v.y;
    if (crime) { Police.signalerCrime(crime, v.x, v.y, vu); B.partie.stats.volees++; }
    Entree.contexte('vehicule');
    if (v.def.classe === 'velo') Son.SFX.ramasse(); else { Son.SFX.porte(); Son.boucle('moteur', true, 0.6); }
    if (v.def.radio) Son.Radio.jouer(v.def.radio);
    Hud.message(v.def.nom.toUpperCase());
    return true;
  }

  /** Descendre : a gauche si c'est libre, sinon a droite, sinon derriere. */
  function descendre(j, force) {
    const v = j.dansVehicule;
    if (!v) return false;
    if (!force && Math.abs(v.vitesse) > 1.2) { v.vitesse *= 0.8; return false; }
    const cotes = [v.angle + Math.PI / 2, v.angle - Math.PI / 2, v.angle + Math.PI];
    let pose = false;
    for (const a of cotes) {
      const x = v.x + Math.cos(a) * (v.def.largeur / 2 + 8), y = v.y + Math.sin(a) * (v.def.largeur / 2 + 8);
      if (!Monde.bloque(Math.floor(x / TT), Math.floor(y / TT), Monde.MASQUE_PIETON)) { j.x = x; j.y = y; pose = true; break; }
    }
    if (!pose) { j.x = v.x; j.y = v.y + v.def.largeur; }
    v.conducteur = null;
    v.etat = 'stationne';
    j.dansVehicule = null; j.dessine = true;
    // ⚠️ Le meme appui ne doit pas nous faire REMONTER dans la meme image :
    // la fin de maj() regarde aussi le bouton ACTION.
    j.descenduT = B.t;
    Entites.dansLaCarte(j);
    Entree.contexte('pied');
    Son.boucle('moteur', false);
    Son.Radio.arreter();
    if (!force) Son.SFX.porte();
    if (typeof Missions !== 'undefined' && Missions.taxi) Missions.taxi.abandonner('SORTI DU TAXI');
    return true;
  }

  function ejecter(j, v) {
    const ph = physique();
    const vitesse = Math.hypot(v.vx, v.vy);
    descendre(j, true);
    j.x = v.x + Math.cos(v.angle) * (v.def.longueur / 2 + 6);
    j.y = v.y + Math.sin(v.angle) * (v.def.longueur / 2 + 6);
    j.vx = Math.cos(v.angle) * vitesse * 0.8; j.vy = Math.sin(v.angle) * vitesse * 0.8;
    j.roule = 18; j.invincible = 0;
    Entites.dansLaCarte(j);
    Entites.blesser(j, Math.round(vitesse * ph.renverse_degats_par_px * 0.5), null, { renverse: true, angle: v.angle });
    Hud.message('EJECTE !');
  }

  // --- Trafic : lire la carte, choisir, freiner ---------------------------------------

  function centre(tx, ty) { return { x: tx * TT + 8, y: ty * TT + 8, tx: tx, ty: ty }; }

  /** Peut-on sortir du croisement dans ce sens depuis cette tuile ? On avance
      tant qu'on est sur du '+' (le carrefour, ses passages pietons) et on veut
      trouver une voie dont la fleche va dans NOTRE sens — pas a contresens. */
  function peutSortir(tx, ty, sens) {
    const pas = PAS_FLECHE[sens];
    let x = tx, y = ty;
    for (let i = 0; i < 9; i++) {
      x += pas[0]; y += pas[1];
      const f = Monde.fleche(x, y);
      if (f === sens) return true;
      if (f !== '+') return false;
    }
    return false;
  }

  function prochaineCible(v) {
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    const f = Monde.fleche(tx, ty);
    v.attendFeu = false;
    if (PAS_FLECHE[f]) {
      v.sens = f; v.sortie = null;
      const p = PAS_FLECHE[f];
      return centre(tx + p[0], ty + p[1]);
    }
    if (f === 'S') {
      const sens = Monde.sensArret(tx, ty) || v.sens;
      v.sens = sens;
      const p = PAS_FLECHE[sens];
      const inter = Monde.intersectionA(tx + p[0], ty + p[1]);
      if (inter && !Monde.feuVert(inter, sens)) { v.attendFeu = true; return centre(tx, ty); }
      // Un STOP : on s'immobilise, puis on passe si le croisement est libre.
      if (inter && inter.stop === sens) {
        if (v.stopT === undefined) v.stopT = trafic().arret_images;
        // ⚠️ Le compte ne tourne qu'a l'ARRET complet : sinon on comptait le
        // freinage et le char repartait sans s'etre vraiment immobilise.
        if (Math.abs(v.vitesse) < 0.05) v.stopT = Math.max(0, v.stopT - 1);
        if (v.stopT > 0 || !croisementLibre(inter, v)) { v.attendFeu = true; return centre(tx, ty); }
      }
      v.stopT = undefined;
      return centre(tx + p[0], ty + p[1]);
    }
    if (f === '+') {
      if (!v.sens) v.sens = FLECHE_DE[Math.round(Math.cos(v.angle)) + ',' + Math.round(Math.sin(v.angle))] || '>';
      // Au premier '+', on decide ou l'on va : tout droit, a gauche, a droite.
      if (!v.sortie) {
        const tirage = B.rng();
        const ordre = tirage < 0.55 ? ['droit', 'droite', 'gauche'] : tirage < 0.78 ? ['droite', 'droit', 'gauche'] : ['gauche', 'droit', 'droite'];
        v.sortie = ordre;
      }
      const droit = v.sens;
      const p = PAS_FLECHE[droit];
      const droite = FLECHE_DE[(-p[1]) + ',' + p[0]], gauche = FLECHE_DE[p[1] + ',' + (-p[0])];
      const vers = { droit: droit, droite: droite, gauche: gauche };
      for (const choix of v.sortie) {
        const sens = vers[choix];
        if (peutSortir(tx, ty, sens)) {
          const q = PAS_FLECHE[sens];
          v.sens = sens;
          return centre(tx + q[0], ty + q[1]);
        }
      }
      // Rien ne sort d'ici dans ces sens : on continue tout droit sur le '+'.
      return centre(tx + p[0], ty + p[1]);
    }
    // Hors route : on cherche la voie la plus proche.
    let meilleur = null, dMin = Infinity;
    for (let dy = -3; dy <= 3; dy++) {
      for (let dx = -3; dx <= 3; dx++) {
        const g = Monde.fleche(tx + dx, ty + dy);
        if (!PAS_FLECHE[g]) continue;
        const d = dx * dx + dy * dy;
        if (d < dMin) { dMin = d; meilleur = centre(tx + dx, ty + dy); v.sens = g; }
      }
    }
    return meilleur;
  }

  /** Personne dans la boite du croisement (a part nous) ? */
  function croisementLibre(inter, v) {
    const cx = (inter.x + inter.l / 2) * TT, cy = (inter.y + inter.h / 2) * TT;
    const rayon = Math.max(inter.l, inter.h) * TT / 2 + 12;
    return Entites.autour(cx, cy, rayon, function (e) { return e.type === 'vehicule' && e !== v && e.etat !== 'epave'; }).length === 0;
  }

  /** Quelque chose devant ? Rend la distance, ou Infinity. */
  function obstacleDevant(v) {
    const t = trafic();
    const portee = t.regard_tuiles * TT;
    const cx = Math.cos(v.angle), cy = Math.sin(v.angle);
    const ax = v.x + cx * (v.def.longueur / 2 + portee / 2), ay = v.y + cy * (v.def.longueur / 2 + portee / 2);
    let dMin = Infinity;
    for (const e of Entites.autour(ax, ay, portee / 2 + 16, function (q) {
      return q !== v && ((q.type === 'vehicule') || ((q.type === 'pieton' || q.type === 'joueur') && q.vivant && !q.dansVehicule));
    })) {
      const dx = e.x - v.x, dy = e.y - v.y;
      const devant = dx * cx + dy * cy;                 // projection sur l'axe
      const cote = Math.abs(-dx * cy + dy * cx);         // ecart lateral
      if (devant < v.def.longueur / 2 - 4 || cote > v.def.largeur / 2 + (e.r || 5) + 2) continue;
      if (devant < dMin) dMin = devant - v.def.longueur / 2;
    }
    return dMin;
  }

  function majConducteur(v) {
    const t = trafic();
    if (!v.cible || (v.attendFeu && !v.cible.tx)) v.cible = prochaineCible(v);
    if (!v.cible) { majPhysique(v, { gaz: 0, frein: 1, direction: 0 }); return; }
    if (v.attendFeu) {
      // On attend (feu rouge, stop) : on redemande chaque image, sans bouger.
      v.cible = prochaineCible(v);
      if (v.attendFeu) { rouler(v, 0); return; }
      if (!v.cible) return;
    }
    const dx = v.cible.x - v.x, dy = v.cible.y - v.y;
    if (dx * dx + dy * dy < 36) { v.cible = prochaineCible(v); if (!v.cible) return; }
    const voulu = angleVers(v.x, v.y, v.cible.x, v.cible.y);
    const ecart = ecartAngle(v.angle, voulu);
    let vitesseVoulue = v.def.vitesse_max * t.vitesse_ville;
    // ⚠️ On ralentit AVANT le coin, pas dedans : a 2,2 px/image le rayon de
    // braquage fait 3,6 tuiles, et un coin de rue en demande 1,5 — le char
    // ratait son virage et finissait sur le trottoir d'en face.
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    const ici = Monde.fleche(tx, ty);
    const p = PAS_FLECHE[v.sens] || [0, 0];
    const devant = Monde.fleche(tx + p[0] * 2, ty + p[1] * 2);
    if (ici === '+' || ici === 'S' || devant === '+' || devant === 'S') vitesseVoulue = Math.min(vitesseVoulue, 1.1);
    if (Math.abs(ecart) > 0.5) vitesseVoulue = Math.min(vitesseVoulue, 0.8);
    const obstacle = obstacleDevant(v);
    if (obstacle < t.distance_securite_px) {
      vitesseVoulue = 0;
      v.patience++;
      if (v.patience > t.patience_images) { v.force = 90; v.patience = 0; v.klaxonT = 30; }
    } else {
      if (obstacle < t.distance_securite_px * 2) vitesseVoulue *= 0.5;
      v.patience = 0;
    }
    if (v.force > 0) { v.force--; vitesseVoulue = Math.max(vitesseVoulue, v.def.vitesse_max * 0.25); }
    void ecart;
    rouler(v, vitesseVoulue);
  }

  /** Le trafic est SUR DES RAILS : il avance vers le centre de sa tuile cible,
      accelere et freine comme un char, mais ne connait pas le braquage.

      ⚠️ C'est ce qui l'empeche de couper les coins. Avec la physique du
      joueur, un char a 1,1 px/image a un rayon de braquage d'une tuile et
      demie : il ratait un virage sur deux et finissait sur le trottoir d'en
      face. Ici il tourne AU centre de la tuile, comme un tramway. */
  function rouler(v, vitesseVoulue) {
    const d = v.def;
    if (v.vitesse < vitesseVoulue) v.vitesse = Math.min(vitesseVoulue, v.vitesse + d.acceleration * 1.5);
    else v.vitesse = Math.max(vitesseVoulue, v.vitesse - d.frein * 1.5);
    if (!v.cible) { v.vx = 0; v.vy = 0; return; }
    const dx = v.cible.x - v.x, dy = v.cible.y - v.y;
    const dist = Math.hypot(dx, dy);
    if (dist < 0.01 || v.vitesse <= 0) { v.vx = 0; v.vy = 0; return; }
    const pas = Math.min(dist, v.vitesse);
    v.vx = dx / dist * pas; v.vy = dy / dist * pas;
    // Le cap suit la route, en douceur : on VOIT le char tourner.
    const voulu = Math.atan2(dy, dx);
    v.angle += ecartAngle(v.angle, voulu) * 0.3;
  }

  // --- Le joueur au volant ----------------------------------------------------------

  function commandesJoueur(v) {
    const axe = Entree.axe;
    const clavierHaut = Entree.bas('haut'), clavierBas = Entree.bas('bas');
    let gaz = clavierHaut ? 1 : 0, frein = clavierBas ? 1 : 0;
    if (axe.source !== 'clavier') { if (axe.y < -0.2) gaz = Math.max(gaz, -axe.y); if (axe.y > 0.2) frein = Math.max(frein, axe.y); }
    gaz = Math.max(gaz, Entree.gaz); frein = Math.max(frein, Entree.frein);
    const direction = axe.source === 'clavier' ? (Entree.bas('droite') ? 1 : 0) - (Entree.bas('gauche') ? 1 : 0) : borner(axe.x * 1.3, -1, 1);
    return { gaz: gaz, frein: frein, direction: direction, freinMain: Entree.bas('esquive') };
  }

  function majJoueur(j) {
    const v = j.dansVehicule;
    if (v.etat === 'epave') { descendre(j, true); return; }
    majPhysique(v, commandesJoueur(v));
    if (Entree.neuf('attaque')) { v.klaxonT = 30; if (typeof Missions !== 'undefined' && Missions.taxi) Missions.taxi.klaxon(v); }
    if (Entree.neuf('action')) descendre(j, false);
    if (Entree.neuf('arme')) {
      const station = Son.Radio.suivante();
      const def = station ? Son.Radio.station(station) : null;
      Hud.message(def ? 'RADIO : ' + def.nom.toUpperCase() : 'RADIO ETEINTE');
    }
    // Le moteur monte dans les tours.
    if (v.def.classe !== 'velo') Son.reglerBoucle('moteur', 0.35 + Math.abs(v.vitesse) / v.def.vitesse_max * 0.5, 0.7 + Math.abs(v.vitesse) / v.def.vitesse_max * 0.9);
  }

  // --- Boucle -------------------------------------------------------------------------

  function maj() {
    const j = B.joueur;
    if (!j) return;
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const v = B.entites[i];
      if (v.type !== 'vehicule') continue;
      majEtatDuChar(v);
      if (v.etat === 'epave') { if (v.epaveT <= 0 && !Entites.visibleAEcran(v.x, v.y, 40)) Entites.retirer(v); continue; }
      if (v.conducteur === j) majJoueur(j);
      else if (v.conducteur === 'trafic') majConducteur(v);
      else majPhysique(v, { gaz: 0, frein: 0, direction: 0 });
      if (v.conducteur === 'trafic') {
        v.x += v.vx; v.y += v.vy;
        heurterVehicules(v);
        heurterPietons(v);
      } else if (Math.abs(v.vx) + Math.abs(v.vy) > 0.01 || v.z > 0) avancer(v);
      else { heurterPietons(v); }
      if (v.conducteur === j) { j.x = v.x; j.y = v.y; j.angle = v.angle; }
    }
    peupler();
    if (!j.dansVehicule && Entree.neuf('action') && !j.roule && j.descenduT !== B.t) {
      const v = vehiculeSousLaMain(j);
      if (v && !Missions.interagir(j)) monter(j, v);
    }
  }

  // --- Les feux et les stops, comme du mobilier ---------------------------------------

  /** Le coin de trottoir libre le plus proche : pas la borne-fontaine, pas le
      pied du lampadaire. On s'ecarte d'une tuile s'il le faut. */
  function coinLibre(tx, ty) {
    const essais = [[tx, ty], [tx + 1, ty], [tx, ty - 1], [tx - 1, ty], [tx, ty + 1], [tx + 1, ty - 1]];
    for (const c of essais) {
      if (Monde.glyphe(c[0], c[1]) !== '.') continue;
      if (Entites.decorAutour(c[0] * TT + 8, c[1] * TT + 8, 10).length) continue;
      return c;
    }
    return [tx, ty];
  }

  function creerSignalisation() {
    const carte = Monde.carte;
    carte.intersections.forEach(function (inter) {
      if (inter.feux) {
        // Deux feux, aux coins nord-est et sud-ouest (les lampadaires ont les autres).
        for (const coin of [[inter.x + inter.l, inter.y - 1], [inter.x - 1, inter.y + inter.h]]) {
          const c = coinLibre(coin[0], coin[1]);
          Entites.creer('feu', c[0] * TT + 8, c[1] * TT + 15, { inter: inter, decor: 'feu', r: 2, solide: false });
        }
      } else if (inter.stop) {
        const coins = { '<': [inter.x + inter.l, inter.y - 1], '>': [inter.x - 1, inter.y + inter.h],
                        'v': [inter.x - 1, inter.y - 1], '^': [inter.x + inter.l, inter.y + inter.h] };
        const c = coinLibre(coins[inter.stop][0], coins[inter.stop][1]);
        Entites.creer('stop', c[0] * TT + 8, c[1] * TT + 15, { inter: inter, decor: 'stop', r: 2, solide: false });
      }
    });
  }

  /** Un feu : un poteau cuit, deux lanternes peintes a la volee selon la phase. */
  function dessinerFeu(ctx, e, cx, cy) {
    const d = DECORS.feu;
    const poteau = Atlas.cuirePeintre('decor|feu', d.w, d.h, d.peindre);
    const x = Math.round(e.x - d.ancre[0] - cx), y = Math.round(e.y - d.ancre[1] - cy);
    ctx.drawImage(poteau, x, y);
    const ns = Monde.feuVert(e.inter, '^'), eo = Monde.feuVert(e.inter, '>');
    const orange = !ns && !eo;
    ctx.fillStyle = orange ? '#f39c12' : (ns ? '#2ecc71' : '#e74c3c'); ctx.fillRect(x + 1, y + 2, 3, 3);    // lanterne nord-sud
    ctx.fillStyle = orange ? '#f39c12' : (eo ? '#2ecc71' : '#e74c3c'); ctx.fillRect(x + 6, y + 2, 3, 3);    // lanterne est-ouest
    B.stats.images++; B.stats.rects += 2;
  }

  // --- Dessin --------------------------------------------------------------------------

  function dessinerUn(ctx, v, cx, cy) {
    const def = SPRITES[v.sprite];
    if (!def) return;
    const rot = Atlas.cuireRotations(v.sprite, def, v.swaps, ROTATIONS);
    let i = Math.round(v.angle / (Math.PI * 2) * ROTATIONS) % ROTATIONS;
    if (i < 0) i += ROTATIONS;
    if (v.z > 2) {                       // en l'air : l'ombre reste au sol
      ctx.fillStyle = 'rgba(0,0,0,0.25)';
      ctx.fillRect(Math.round(v.x - 10 - cx), Math.round(v.y - 5 - cy), 20, 10);
      B.stats.rects++;
    }
    ctx.drawImage(rot.images[i], Math.round(v.x - rot.cote / 2 - cx), Math.round(v.y - v.z - rot.cote / 2 - cy));
    B.stats.images++;
  }

  return {
    ROTATIONS, courbeBraquage, vehiculeDef, creer, peupler, cercles, bloqueParLesTuiles,
    majPhysique, avancer, endommager, exploser, declencherAlarme,
    vehiculeSousLaMain, monter, descendre, ejecter,
    prochaineCible, peutSortir, obstacleDevant, majConducteur, commandesJoueur, rouler,
    croisementLibre, creerSignalisation, dessinerFeu, maj, dessinerUn,
  };
})();
