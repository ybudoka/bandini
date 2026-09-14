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
   dans son sens, et qu'elle est de l'autre cote.

   Sur un boulevard (deux voies dans le meme sens), un char bloque par un
   pieton, une epave ou un char arrete ne reste pas derriere : il vise la
   tuile d'a cote et se DEPORTE, par la gauche si elle est libre. */

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
      patience: 0, force: 0, deportT: 0, deportFroid: 0, alarme: 0, klaxonT: 0, chocs: 0, agresseur: null,
      vole: false, aToi: false, laisse: false, malGareT: 0, epaveT: 0, solide: false, vivant: true, sprite: def.sprite, sirene: false, remorque: null, remorqueePar: null,
    }, options || {}));
    return v;
  }

  /** Un type de char selon les poids du catalogue (phase 1 seulement).

      ⚠️ Un char `rare` ne nait QUE dans un district qui le declare (`rares` de
      la zone, pose par `carte.py`). C'est la, et pas dans sa `frequence`, que
      se joue sa rarete : un coupe sport qu'on croise dans une cour a ferraille
      n'est plus un coupe sport, c'est une auto de plus. Et c'est PYTHON qui
      decide ou — le navigateur n'a pas a savoir qu'une decapotable n'a rien a
      faire a La Shop. */
  function typeDeRue(zone) {
    const rares = (zone && zone.rares) || [];
    const types = B.defs.vehicules.filter(function (v) {
      if (v.phase !== 1 || v.frequence <= 0) return false;
      return !v.rare || rares.indexOf(v.slug) >= 0;
    });
    if (!types.length) return null;
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

  //: Le glyphe d'une case dit ou pointe le NEZ de l'auto garee.
  const NEZ = { '^': [0, -1], 'v': [0, 1], '<': [-1, 0], '>': [1, 0] };

  /** Une case de stationnement libre, DANS SES LIGNES : on cherche la tuile du
      fond (celle contre la ligne de nez) qui a le reste de sa case derriere
      elle, et l'auto se pose a cheval sur les deux — elle fait deux tuiles de
      long, la case aussi. */
  function placeStationnee() {
    const t = trafic(), c = Monde.carte, j = B.joueur;
    for (let essai = 0; essai < 20; essai++) {
      const a = B.rng() * Math.PI * 2;
      const d = t.naissance_px * 0.6 + B.rng() * (t.oubli_px - t.naissance_px);
      const tx = Math.floor((j.x + Math.cos(a) * d) / TT), ty = Math.floor((j.y + Math.sin(a) * d) / TT);
      if (tx < 1 || ty < 2 || tx >= c.w - 1 || ty >= c.h - 1) continue;
      const g = Monde.glyphe(tx, ty), nez = NEZ[g];
      if (!nez) continue;
      if (Monde.glyphe(tx + nez[0], ty + nez[1]) === g) continue;     // pas le fond
      if (Monde.glyphe(tx - nez[0], ty - nez[1]) !== g) continue;     // case tronquee
      const x = (tx + 0.5 - nez[0] / 2) * TT, y = (ty + 0.5 - nez[1] / 2) * TT;
      if (Entites.visibleAEcran(x, y, 40) || !libreAutour(x, y, 40)) continue;
      return { x: x, y: y, angle: Math.atan2(nez[1], nez[0]) };
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
      if (loin && v.conducteur !== j && !v.mission && !v.remorqueePar && !v.remorque && !Entites.visibleAEcran(v.x, v.y, 60)) { Entites.retirer(v); continue; }
      if (v.etat === 'epave') continue;
      if (v.conducteur === 'trafic') roulent++; else if (v.conducteur !== j) stationnes++;
    }
    if (B.t % 20 !== 0) return;
    const zone = Monde.zoneA(j.x, j.y);
    const voulu = Math.min(t.vehicules_max, zone ? zone.vehicules : 6) * Monde.rythme(zone);
    if (roulent < voulu) {
      const place = placeDansLeTrafic();
      if (place) {
        const type = typeDeRue(zone);
        const v = type && creer(type.slug, place.x, place.y, place.angle, { conducteur: 'trafic', etat: 'roule', sens: place.sens });
        if (v) {
          v.vitesse = v.def.vitesse_max * t.vitesse_ville * 0.5;
          // ⚠️ Une ambulance sur trois est EN COURSE, et on l'entend passer.
          // Les deux autres rentrent au garage : une ville ou toutes les
          // ambulances hurlent n'est pas une ville, c'est une alarme.
          if (v.def.sirene) v.sirene = B.rng() < AMBULANCE_EN_COURSE;
        }
      }
    } else if (stationnes < t.stationnes_max && B.t % 40 === 0) {
      const place = placeStationnee();
      if (place) { const type = typeDeRue(zone); if (type) creer(type.slug, place.x, place.y, place.angle, { etat: 'stationne' }); }
    }
  }

  // --- Geometrie : la chaine de cercles ------------------------------------------

  /** ⚠️ Le nombre de cercles vient de la FICHE, pas d'une constante unique.
      Il en faut au moins `longueur / largeur`, sinon deux cercles voisins
      laissent un trou et une moto entre dans l'autobus par le milieu sans que
      rien ne se touche (juge Python `test_la_chaine_de_cercles_ne_laisse_aucun_trou`).
      Les cinq de l'autobus et les quatre du camion ne sont pas un reglage de
      confort : c'est ce qui fait qu'ils ont une carrosserie. */
  function cercles(v, x, y, angle) {
    const n = v.def.cercles || physique().cercles;
    const demi = v.def.longueur / 2 - v.r;
    const out = [];
    const cx = Math.cos(angle === undefined ? v.angle : angle), cy = Math.sin(angle === undefined ? v.angle : angle);
    for (let i = 0; i < n; i++) {
      const t = n === 1 ? 0 : -demi + (2 * demi) * i / (n - 1);
      out.push({ x: (x === undefined ? v.x : x) + cx * t, y: (y === undefined ? v.y : y) + cy * t, r: v.r });
    }
    return out;
  }

  /** Les tuiles qui bloquent le char a cette place — la liste, pas un oui/non.
      C'est ce qu'il faut pour decider si un LOURD passe au travers : il faut
      les voir TOUTES avant de trancher. */
  function tuilesQuiBloquent(v, x, y) {
    const out = [];
    for (const c of cercles(v, x, y)) {
      const tx0 = Math.floor((c.x - c.r) / TT), tx1 = Math.floor((c.x + c.r) / TT);
      const ty0 = Math.floor((c.y - c.r) / TT), ty1 = Math.floor((c.y + c.r) / TT);
      for (let ty = ty0; ty <= ty1; ty++) {
        for (let tx = tx0; tx <= tx1; tx++) {
          if (Monde.bloque(tx, ty, Monde.MASQUE_VEHICULE)) out.push([tx, ty]);
        }
      }
    }
    return out;
  }

  /** Un lourd lance passe AU TRAVERS de ce qui est bas. Rend vrai si la voie
      s'est ouverte.

      ⚠️ **Tout ou rien.** On regarde d'abord TOUTES les tuiles qui bloquent :
      s'il y en a une seule qu'on ne casse pas (une façade, l'eau, du barbelé),
      le camion s'arrête comme n'importe qui. Casser « celles qu'on peut » et
      s'arrêter sur le reste laisserait un trou dans une clôture sans être
      passé — le pire des deux mondes.

      Le `defonce` de la fiche dit ce qu'il RESTE de vitesse une fois passé au
      travers : 0,75 pour le camion, 0,6 pour la remorqueuse. Un mur de clôture
      coûte donc quelque chose, sinon on le franchit sans le sentir. */
  function defoncerDevant(v, x, y) {
    const ph = physique();
    if (!v.def.defonce || B.interieur) return false;
    if (Math.hypot(v.vx, v.vy) < ph.defonce_vitesse_min) return false;
    const tuiles = tuilesQuiBloquent(v, x, y);
    if (!tuiles.length) return false;
    for (const t of tuiles) {
      const s = Monde.solidite(t[0], t[1]);
      if (s !== 3 && s !== 4) return false;      // une façade : on s'arrête
      if (Monde.estMeuble(t[0], t[1])) return false;
    }
    let casse = false;
    for (const t of tuiles) if (Monde.defoncer(t[0], t[1])) casse = true;
    if (!casse) return false;
    v.vitesse *= v.def.defonce;
    v.vx *= v.def.defonce; v.vy *= v.def.defonce;
    endommager(v, ph.defonce_degats, v.agresseur);
    Entites.poussiere(x, y, 10);
    Son.SFX.choc();
    if (v.conducteur === B.joueur) { B.cam.secousse = Math.max(B.cam.secousse, 0.5); Entree.vibrer(120); }
    return true;
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
        if (bloqueParLesTuiles(v, v.x + px, v.y)) {
          if (defoncerDevant(v, v.x + px, v.y)) v.x += px;
          else { choc = Math.max(choc, Math.abs(v.vx)); v.vx = -v.vx * ph.choc_rebond; }
        } else v.x += px;
      }
      if (py !== 0) {
        if (bloqueParLesTuiles(v, v.x, v.y + py)) {
          if (defoncerDevant(v, v.x, v.y + py)) v.y += py;
          else { choc = Math.max(choc, Math.abs(v.vy)); v.vy = -v.vy * ph.choc_rebond; }
        } else v.y += py;
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
    // ⚠️ Le seuil de decollage vient de Python (`saut_vitesse_min`), qui le
    // deduit de la hauteur minimale visible. L'ancien 1,5 etait ecrit ici a la
    // main : un velo a 2 px/image le passait et « sautait » de deux pixels —
    // moins que l'epaisseur de son ombre.
    if (v.z === 0 && Math.abs(v.vitesse) >= B.defs.conduite.saut_vitesse_min && Monde.estRampe(tx, ty)) {
      v.vz = Math.abs(v.vitesse) * ph.rampe_impulsion;
    }
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
      // Le char au bout du cable n'est pas un obstacle : il est accroche.
      if (autre === v.remorque || autre === v.remorqueePar) continue;
      const siens = cercles(autre);
      for (const a of miens) {
        for (const b of siens) {
          const dx = b.x - a.x, dy = b.y - a.y;
          const d2 = dx * dx + dy * dy, min = a.r + b.r;
          if (d2 >= min * min || d2 === 0) continue;
          const d = Math.sqrt(d2), nx = dx / d, ny = dy / d, chevauche = min - d;
          const m1 = v.def.masse, m2 = autre.def.masse, total = m1 + m2;
          const deuxDuTrafic = v.conducteur === 'trafic' && autre.conducteur === 'trafic';
          if (deuxDuTrafic) return;                     // sur des rails : on ne se pousse pas
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
    if (v.vie > 0) return;
    // ⚠️ Ce qui n'a pas de reservoir ne brule pas et n'explose pas : ca se
    // PLIE. C'est la fiche qui le dit (`reservoir`), pas un `slug === 'velo'`
    // cache ici — le jour ou une trottinette arrive, elle se plie toute seule.
    if (v.def.reservoir === false) plier(v); else exploser(v);
  }

  /** Un char sans reservoir a zero PV : il tombe sur le cote, tordu, et c'est
      tout. Pas de feu, pas de fumee, pas de secousse, pas de deflagration —
      et surtout AUCUN DELIT : on renversait un velo, et la police arrivait
      pour une explosion a deux etoiles. */
  function plier(v) {
    v.etat = 'epave';
    // ⚠️ Le cable lache : sans ca, un char reste accroche a une carcasse
    // que plus personne ne met a jour, et le trafic ne l'oublie jamais.
    if (v.remorque) decrocher(v);
    if (v.remorqueePar) decrocher(v.remorqueePar);
    v.vie = 0;
    v.vitesse = 0; v.vx = 0; v.vy = 0;
    v.plie = true;
    v.swaps = { c: '#4a4a52' };
    v.angle += (B.rng() - 0.5) * 1.6;      // il gît de travers : on voit qu'il est tombe
    v.epaveT = physique().epave_secondes * 60;
    v.alarme = 0;
    for (let i = 0; i < 8; i++) {
      const a = B.rng() * Math.PI * 2, s = 0.4 + B.rng();
      Entites.particule(v.x, v.y, Math.cos(a) * s, Math.sin(a) * s * 0.6, 16 + B.rng() * 10, '#8a8a8a', 1, 0.06);
    }
    Son.SFX.choc();
    if (v.conducteur && v.conducteur !== 'trafic') descendre(v.conducteur, true);
    if (v.conducteur === 'trafic') v.conducteur = null;
  }

  /** Un char du trafic qui nous passe pres : on l'entend passer, une fois. */
  function bruitDePassage(v) {
    const j = B.joueur;
    if (!j || v.conducteur !== 'trafic' || Math.abs(v.vitesse) < 0.8) return;
    const d2 = dist2(v.x, v.y, j.x, j.y);
    if (d2 > 90 * 90) { v.passeT = 0; return; }
    if (v.passeT > 0) { v.passeT--; return; }
    v.passeT = 240;
    const slug = v.def.classe === 'velo' ? 'sonnette' : (v.def.classe === 'moto' ? 'passage_moto' : 'passage_auto');
    Son.jouerA(slug, v.x, v.y, 160);
  }

  function majEtatDuChar(v) {
    const ph = physique();
    bruitDePassage(v);
    if (v.etat === 'epave') {
      if (v.epaveT > 0) v.epaveT--;
      // ⚠️ Une carcasse fume — sauf celle qui n'avait rien a bruler. Un velo
      // plie sur le trottoir ne degage pas une colonne de fumee noire.
      if (v.def.reservoir !== false && B.t % 6 === 0) Entites.particule(v.x + (B.rng() - 0.5) * 14, v.y - 4, (B.rng() - 0.5) * 0.3, -0.2, 40, '#3a3a3a', 2, -0.01);
      return;
    }
    const part = v.vie / v.vieMax;
    // ⚠️ Sans reservoir, pas de feu ni de fumee : un velo cabosse au bord du
    // trottoir ne s'enflamme pas tout seul, et rien ne le ronge jusqu'a zero.
    const brule = v.def.reservoir !== false;
    if (brule && part < ph.feu_sous) {
      if (B.t % 3 === 0) Entites.particule(v.x + (B.rng() - 0.5) * 10, v.y - 6, (B.rng() - 0.5) * 0.4, -0.5, 18, B.rng() < 0.5 ? '#ff8c1a' : '#ffd23a', 2, -0.02);
      if (B.t % 60 === 0) endommager(v, ph.feu_degats_par_seconde, v.agresseur);
    } else if (brule && part < ph.fumee_sous && B.t % 8 === 0) {
      Entites.particule(v.x + (B.rng() - 0.5) * 8, v.y - 6, (B.rng() - 0.5) * 0.3, -0.3, 30, '#8a8a8a', 2, -0.01);
    }
    if (v.alarme > 0) {
      v.alarme--;
      if (v.alarme % 40 === 0) Son.SFX.klaxon();
    }
    if (v.klaxonT > 0) { v.klaxonT--; if (v.klaxonT === 29) avertir(v); }
    soignerAuVolant(v);
    majCrochet(v);
  }

  // --- Le crochet de la remorqueuse ------------------------------------------------

  /** Le char qu'on peut accrocher : le plus proche DERRIERE soi, sans
      conducteur, dans `crochet_portee_px`. ⚠️ Derriere : un crochet est a
      l'arriere, et il faut donc reculer dessus — c'est le geste qui rend la
      remorqueuse autre chose qu'un camion. */
  function aCrocher(v) {
    const ph = physique();
    const ax = v.x - Math.cos(v.angle) * v.def.longueur / 2;
    const ay = v.y - Math.sin(v.angle) * v.def.longueur / 2;
    let meilleur = null, dMin = ph.crochet_portee_px * ph.crochet_portee_px;
    for (const e of Entites.autour(ax, ay, ph.crochet_portee_px + 30, function (q) { return q.type === 'vehicule'; })) {
      if (e === v || e.remorqueePar || e.remorque || e.conducteur) continue;
      const d = dist2(e.x, e.y, ax, ay);
      if (d < dMin) { dMin = d; meilleur = e; }
    }
    return meilleur;
  }

  /** Accrocher, ou decrocher si on traine deja quelque chose. ⚠️ UN SEUL a la
      fois : c'est la fiche qui le dit, et c'est ce qui empeche le train de
      douze chars qu'on ne saurait plus arreter. */
  function basculerCrochet(v) {
    if (v.remorque) { decrocher(v); return false; }
    const cible = aCrocher(v);
    if (!cible) { Hud.message('RIEN A ACCROCHER DERRIERE'); return false; }
    v.remorque = cible;
    cible.remorqueePar = v;
    cible.alarme = 0;
    Son.SFX.choc();
    Hud.message(cible.def.nom.toUpperCase() + ' ACCROCHE');
    return true;
  }

  function decrocher(v) {
    const t = v.remorque;
    v.remorque = null;
    if (!t) return;
    t.remorqueePar = null;
    Son.SFX.porte('vehicule');    // le crochet qui lache : de la tole, comme une portiere
  }

  /** Le cable, une fois par image : le char remorque est tire vers un point
      fixe derriere la remorqueuse, et il pointe vers elle.

      ⚠️ Il reste BLOQUE PAR LES TUILES : on ne traine pas une epave a travers
      un mur. Le cable s'etire alors — et s'il s'etire trop, il casse. C'est ce
      qui rend le virage serre couteux sans une seule ligne de plus. */
  function majCrochet(v) {
    const t = v.remorque;
    if (!t) return;
    if (!t.actif || t.remorqueePar !== v) { v.remorque = null; return; }
    const ph = physique();
    const d = ph.crochet_cable_px + (v.def.longueur + t.def.longueur) / 2;
    const ax = v.x - Math.cos(v.angle) * d;
    const ay = v.y - Math.sin(v.angle) * d;
    const dx = ax - t.x, dy = ay - t.y;
    if (Math.hypot(dx, dy) > ph.crochet_cable_px * 2.5) {
      Hud.message('LE CABLE A LACHE');
      decrocher(v);
      return;
    }
    t.angle = Math.atan2(v.y - t.y, v.x - t.x);
    t.vx = dx * ph.crochet_raideur;
    t.vy = dy * ph.crochet_raideur;
    t.vitesse = Math.hypot(t.vx, t.vy);
    if (!bloqueParLesTuiles(t, t.x + t.vx, t.y)) t.x += t.vx;
    if (!bloqueParLesTuiles(t, t.x, t.y + t.vy)) t.y += t.vy;
    Entites.dansLaCarte(t);
  }

  /** L'ambulance rend des PV a qui la conduit — `soigne` de la fiche, en PV
      par seconde.

      ⚠️ Elle ne RESSUSCITE personne : un mort reste mort, et le boulot est
      perdu. C'est la seule chose que la fiche disait et qu'il fallait tenir —
      sinon l'ambulance devient la sortie de secours de toutes les fusillades,
      et l'hopital ne veut plus rien dire. */
  function soignerAuVolant(v) {
    if (!v.def.soigne || B.t % 60 !== 0) return;
    const c = v.conducteur;
    if (!c || c === 'trafic' || c === 'police' || !c.vivant) return;
    if (c.vie <= 0 || c.vie >= c.vieMax) return;
    c.vie = Math.min(c.vieMax, c.vie + v.def.soigne);
    if (c === B.joueur) B.partie.vie = c.vie;
  }

  function exploser(v) {
    const ph = physique();
    v.etat = 'epave';
    // ⚠️ Le cable lache : sans ca, un char reste accroche a une carcasse
    // que plus personne ne met a jour, et le trafic ne l'oublie jamais.
    if (v.remorque) decrocher(v);
    if (v.remorqueePar) decrocher(v.remorqueePar);
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
    // ⚠️ `alarme_s` de la fiche : la berline de luxe hurle deux fois et demie
    // plus longtemps que les autres. C'est le prix de la meilleure revente.
    v.alarme = (v.def.alarme_s || physique().alarme_secondes) * 60;
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
    } else if (v.conducteur === null && !v.vole && !v.aToi) {
      // ⚠️ `aToi` : un char PAYE devant un guichet. Sans lui, racheter le sien
      // a la fourriere puis monter dedans etait un `vol_vehicule` — et le
      // comptoir ne servait plus a rien : autant sauter la cloture.
      crime = 'vol_vehicule';
      vu = Police.quelqu_un_voit(v.x, v.y, null);
      if (v.def.alarme && declencherAlarme(v)) vu = true;
    }
    // Changer de char hors de vue : la police perd ta trace d'une etoile.
    const r = B.recherche, deg = B.defs.recherche.deguisement;
    if (r.etoiles > 0 && r.vu > deg.vehicule_s * 60) { r.etoiles = Math.max(0, r.etoiles - deg.vehicule_etoiles); r.vu = 0; Hud.message('ILS T’ONT PERDU DE VUE'); }
    v.conducteur = j; v.etat = 'roule'; v.vole = v.vole || !!crime; v.cible = null;
    v.laisse = false; v.malGareT = 0;              // on le reprend : le chrono repart de zero
    j.dansVehicule = v;
    // ⚠️ Le dernier char conduit, pour la fourriere : la police te SORT
    // du char avant de t'arreter, donc a l'arrestation `dansVehicule` est
    // deja nul — sans ce souvenir, on ne saisirait jamais rien.
    j.dernierVehicule = v; j.dessine = false; j.vx = 0; j.vy = 0;
    j.x = v.x; j.y = v.y;
    if (crime) { Police.signalerCrime(crime, v.x, v.y, vu); B.partie.stats.volees++; }
    // ⚠️ L'etiquette du bouton tactile suit l'avertisseur : SIRENE, SONNETTE, KLAXON.
    Entree.contexte(v.def.sirene ? 'vehicule_sirene' : v.def.klaxon === 'sonnette' ? 'vehicule_sonnette' : 'vehicule');
    bruitDeMontee(v);
    if (v.def.classe !== 'velo') Son.boucle('moteur', true, 0.6);
    if (v.def.radio) { Son.Ambiance.arreter(); Son.Radio.jouer(v.def.radio); }
    Hud.message(v.def.nom.toUpperCase());
    return true;
  }

  /** Le bruit de la montee, et de la descente : la portiere d'un char — ou
      la bequille et le cadre d'une moto et d'un velo, qu'on enfourche.
      ⚠️ La FICHE decide (`portieres`, `vehicules.py`), pas un
      `slug === 'velo'` ici. */
  function bruitDeMontee(v) {
    if (v.def.portieres) Son.SFX.porte('vehicule'); else Son.SFX.enfourcher();
  }

  /** L'avertisseur du char, au bouton du klaxon : le klaxon, ou la sonnette
      d'un velo. ⚠️ C'est la fiche qui le nomme (`klaxon`, `vehicules.py`),
      et c'est un effet de `Son.SFX` — le trafic impatient passe par ici aussi. */
  function avertir(v) {
    (Son.SFX[v.def.klaxon] || Son.SFX.klaxon)();
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
    // ⚠️ « Laisse » : un char que LE JOUEUR a garé. La fourriere ne remorque
    // que ceux-la — remorquer le trafic viderait les rues sans que personne
    // comprenne pourquoi, et le juge du trafic le verrait avant le joueur.
    v.laisse = true;
    j.dansVehicule = null; j.dessine = true;
    // ⚠️ Le meme appui ne doit pas nous faire REMONTER dans la meme image :
    // la fin de maj() regarde aussi le bouton ACTION.
    j.descenduT = B.t;
    Entites.dansLaCarte(j);
    Entree.contexte('pied');
    Son.boucle('moteur', false);
    Son.Radio.arreter();
    Son.Ambiance.jouer();
    if (!force) bruitDeMontee(v);
    if (typeof Missions !== 'undefined' && Missions.boulot) Missions.boulot.abandonner('BOULOT ABANDONNE');
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
      v.enBoite = null;                              // on rend le croisement
      const p = PAS_FLECHE[f];
      return centre(tx + p[0], ty + p[1]);
    }
    if (f === 'S') {
      const sens = Monde.sensArret(tx, ty) || v.sens;
      v.sens = sens;
      const p = PAS_FLECHE[sens];
      const inter = Monde.intersectionA(tx + p[0], ty + p[1]);
      if (v.poursuite) {                             // sirene : feux, stops et boite, on brule tout
        v.attenteBoite = 0; v.stopT = undefined; v.enBoite = inter || null;
        return centre(tx + p[0], ty + p[1]);
      }
      if (inter && !Monde.feuVert(inter, sens)) { v.attendFeu = true; v.attenteBoite = 0; return centre(tx, ty); }
      // Un STOP : on s'immobilise d'abord.
      if (inter && inter.stop === sens) {
        if (v.stopT === undefined) v.stopT = trafic().arret_images;
        // ⚠️ Le compte ne tourne qu'a l'ARRET complet : sinon on comptait le
        // freinage et le char repartait sans s'etre vraiment immobilise.
        if (Math.abs(v.vitesse) < 0.05) v.stopT = Math.max(0, v.stopT - 1);
        if (v.stopT > 0) { v.attendFeu = true; return centre(tx, ty); }
      }
      // ⚠️ Feu vert ou stop, on ne S'ENGAGE que si la boite est libre : deux
      // chars qui tournent a gauche de bouts opposes se retrouvaient nez a nez
      // au milieu, chacun attendant l'autre. Un croisement, un char a la fois.
      // Passe un long moment (un char stationne dans la boite), on y va quand meme.
      if (inter && !croisementLibre(inter, v)) {
        v.attenteBoite = (v.attenteBoite || 0) + 1;
        if (v.attenteBoite < trafic().patience_images * 2) { v.attendFeu = true; return centre(tx, ty); }
      }
      v.attenteBoite = 0;
      v.stopT = undefined;
      v.enBoite = inter || null;                     // on prend le croisement
      if (inter) noterLaBoite(v, inter);
      return centre(tx + p[0], ty + p[1]);
    }
    if (f === '+') {
      if (!v.sens) v.sens = FLECHE_DE[Math.round(Math.cos(v.angle)) + ',' + Math.round(Math.sin(v.angle))] || '>';
      const droit = v.sens;
      const p = PAS_FLECHE[droit];
      const droite = FLECHE_DE[(-p[1]) + ',' + p[0]], gauche = FLECHE_DE[p[1] + ',' + (-p[0])];
      const vers = { droit: droit, droite: droite, gauche: gauche };
      // Au premier '+', on decide ou l'on va : tout droit, a droite, a gauche —
      // et on le garde EN SENS ABSOLUS pour toute la boite.
      // ⚠️ Une preference relative (« a gauche ») relue a chaque tuile par
      // rapport au cap du moment fait tourner a gauche, puis a gauche du
      // nouveau cap, puis encore : le char faisait le tour de la boite sans
      // fin. Martin l'a vu, et le juge des boites en trouvait 1858 cas.
      if (!v.sortie) {
        let ordre;
        if (v.poursuite && B.joueur) {
          // En poursuite : la sortie qui rapproche le plus du joueur, d'abord.
          // En fuite (le fuyard de M2) : celle qui en eloigne le plus.
          const j = B.joueur, signe = v.fuite ? -1 : 1;
          ordre = ['droit', 'droite', 'gauche'].sort(function (a, b) {
            const qa = PAS_FLECHE[vers[a]], qb = PAS_FLECHE[vers[b]];
            return signe * (dist2((tx + qa[0] * 4) * TT, (ty + qa[1] * 4) * TT, j.x, j.y) - dist2((tx + qb[0] * 4) * TT, (ty + qb[1] * 4) * TT, j.x, j.y));
          });
        } else {
          const tirage = B.rng();
          ordre = tirage < 0.55 ? ['droit', 'droite', 'gauche'] : tirage < 0.78 ? ['droite', 'droit', 'gauche'] : ['gauche', 'droit', 'droite'];
        }
        v.sortie = ordre.map(function (choix) { return vers[choix]; });
      }
      // 1. La sortie voulue, si elle part d'ici. Sinon on traverse la boite
      //    tout droit jusqu'a la voie d'ou elle part : un virage a droite se
      //    prend a l'entree de la boite, un virage a gauche au fond.
      const voulu = v.sortie[0];
      if (peutSortir(tx, ty, voulu)) {
        const q = PAS_FLECHE[voulu];
        v.sens = voulu;
        return centre(tx + q[0], ty + q[1]);
      }
      if (Monde.fleche(tx + p[0], ty + p[1]) === '+') return centre(tx + p[0], ty + p[1]);
      // 2. Au fond de la boite sans la sortie voulue : les autres, dans l'ordre.
      for (const sens of v.sortie.slice(1)) {
        if (peutSortir(tx, ty, sens)) {
          const q = PAS_FLECHE[sens];
          v.sens = sens;
          return centre(tx + q[0], ty + q[1]);
        }
      }
      // 3. N'importe quelle sortie d'ici fera (a droite, a gauche du cap).
      for (const sens of [droite, gauche]) {
        if (peutSortir(tx, ty, sens)) {
          const q = PAS_FLECHE[sens];
          v.sens = sens; v.sortie = null;
          return centre(tx + q[0], ty + q[1]);
        }
      }
      // 4. Aucune sortie depuis cette rangee : on se decale DANS la boite
      //    (vers la droite d'abord) jusqu'a en trouver une. ⚠️ Jamais « la
      //    voie la plus proche » ici : elle ramenait dans la boite.
      for (const sens of [droite, gauche]) {
        const q = PAS_FLECHE[sens];
        if (Monde.fleche(tx + q[0], ty + q[1]) === '+') { v.sens = sens; return centre(tx + q[0], ty + q[1]); }
      }
      // 5. Boite d'une tuile sans issue : demi-tour sur place.
      const arriere = FLECHE_DE[(-p[0]) + ',' + (-p[1])];
      v.sens = arriere; v.sortie = null;
      return centre(tx - p[0], ty - p[1]);
    }
    // Hors route : on cherche la voie la plus proche.
    return voieLaPlusProche(v, tx, ty);
  }

  /** La voie la plus proche qui MENE QUELQUE PART : sa fleche continue sur
      une voie (pas dans une boite), elle ne pointe pas vers nous, et une voie
      dans notre rangee ou notre colonne passe avant une voie en diagonale. */
  function voieLaPlusProche(v, tx, ty) {
    let meilleur = null, coutMin = Infinity, sens = null;
    for (let dy = -3; dy <= 3; dy++) {
      for (let dx = -3; dx <= 3; dx++) {
        const g = Monde.fleche(tx + dx, ty + dy);
        if (!PAS_FLECHE[g]) continue;
        const q = PAS_FLECHE[g];
        if (tx + dx + q[0] === tx && ty + dy + q[1] === ty) continue;           // elle pointe vers nous
        if (!PAS_FLECHE[Monde.fleche(tx + dx + q[0], ty + dy + q[1])]) continue;   // elle ne continue pas
        const cout = dx * dx + dy * dy + (dx !== 0 && dy !== 0 ? 6 : 0);
        if (cout < coutMin) { coutMin = cout; meilleur = centre(tx + dx, ty + dy); sens = g; }
      }
    }
    if (meilleur) v.sens = sens;
    return meilleur;
  }

  /** Personne dans le croisement (a part nous) ? Un char qui s'y est engage
      le RESERVE (`enBoite`) jusqu'a ce qu'il en ressorte : le suivant ne se
      contente pas de regarder la boite, il attend que la place soit rendue. */
  function croisementLibre(inter, v) {
    const cx = (inter.x + inter.l / 2) * TT, cy = (inter.y + inter.h / 2) * TT;
    const rayon = Math.max(inter.l, inter.h) * TT / 2 + 2 * TT + 12;      // la boite ET ses passages
    for (const e of Entites.autour(cx, cy, rayon + 40, function (q) { return q.type === 'vehicule' && q !== v && q.etat !== 'epave'; })) {
      if (e.enBoite === inter) return false;
      if (e.conducteur !== 'trafic' && dist2(e.x, e.y, cx, cy) < rayon * rayon) return false;   // le joueur, un char stationne
    }
    return true;
  }

  // --- Le deport : se tasser dans la voie d'a cote -----------------------------------
  //
  // Une rue a deux voies (un boulevard : `RUES_V`/`RUES_H` a 8) a DEUX tuiles
  // cote a cote portant la meme fleche. Un char coince derriere un pieton
  // arrete au milieu de la chaussee, une epave ou le char du joueur n'a alors
  // aucune raison d'attendre : il se deporte, comme dans la vraie rue. Sur une
  // rue a deux voies (largeur 6), il n'y a pas de voisine dans notre sens, et
  // tout ce code se tait.

  /** La voie d'a cote est-elle degagee ? On regarde un couloir qui va de DEUX
      tuiles derriere a `depassement_tuiles` devant : un char qui arrive vite
      par derriere dans cette voie compte autant qu'un char arrete dedans. Les
      echantillons se chevauchent (un par tuile, rayon 13 px), le couloir est
      donc continu : le centre d'un char ne peut pas s'y glisser entre deux. */
  function voieLibre(v, tx, ty, p) {
    const avant = trafic().depassement_tuiles;
    for (let k = -2; k <= avant; k++) {
      const x = (tx + p[0] * k) * TT + 8, y = (ty + p[1] * k) * TT + 8;
      const gene = Entites.autour(x, y, TT * 0.8, function (e) {
        return e !== v && (e.type === 'vehicule'
          || ((e.type === 'pieton' || e.type === 'joueur') && e.vivant && !e.dansVehicule));
      });
      if (gene.length) return false;
    }
    return true;
  }

  /** Le pas lateral vers une voie parallele libre — a GAUCHE d'abord (on
      depasse par la gauche), a droite sinon. null s'il n'y en a pas.

      ⚠️ On exige que la voisine ET la tuile suivante portent notre fleche :
      c'est ce qui interdit de se deporter juste avant une ligne d'arret ou
      dans une boite de croisement, ou le deport couperait la trajectoire de
      quelqu'un qui a la priorite. */
  function voieDeDepassement(v, tx, ty) {
    const p = PAS_FLECHE[v.sens];
    if (!p) return null;
    for (const q of [[p[1], -p[0]], [-p[1], p[0]]]) {
      if (Monde.fleche(tx + q[0], ty + q[1]) !== v.sens) continue;
      if (Monde.fleche(tx + q[0] + p[0], ty + q[1] + p[1]) !== v.sens) continue;
      if (!voieLibre(v, tx + q[0], ty + q[1], p)) continue;
      return q;
    }
    return null;
  }

  /** Viser la voie d'a cote, une tuile plus loin : les rails font le reste —
      le char y glisse en diagonale et, arrive au centre, `prochaineCible`
      relit la fleche sous lui et continue tout droit dans sa nouvelle voie. */
  function changerDeVoie(v) {
    if (v.deportT > 0) return true;                      // deja en train de se tasser
    if (v.deportFroid > 0) return false;                 // on vient de le faire : pas de zigzag
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    if (Monde.fleche(tx, ty) !== v.sens) return false;   // en boite ou a l'arret : pas ici
    const q = voieDeDepassement(v, tx, ty);
    if (!q) return false;
    const p = PAS_FLECHE[v.sens];
    v.cible = centre(tx + q[0] + p[0], ty + q[1] + p[1]);
    v.deportT = trafic().depassement_images;
    v.deports = (v.deports || 0) + 1;
    return true;
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
      // ⚠️ La tolerance laterale doit rester SOUS l'ecart entre deux voies
      // (16 px) : avec +2 px de marge, le char d'en face, sur la voie d'a
      // cote, comptait comme un obstacle — et tout le monde s'arretait nez a
      // nez. C'etait l'embouteillage de Martin.
      if (devant < v.def.longueur / 2 - 4 || cote > v.def.largeur / 2 + (e.r || 5) * 0.8) continue;
      if (e.type === 'vehicule' && Math.abs(e.vitesse) > 0.3) {
        const face = Math.cos(e.angle) * cx + Math.sin(e.angle) * cy;
        if (face < -0.5 && cote > 6) continue;         // il vient en face, dans sa voie : rien a craindre
      }
      if (devant < dMin) dMin = devant - v.def.longueur / 2;
    }
    return dMin;
  }

  /** Le chien de garde du trafic : dix secondes sans bouger, sans feu rouge
      devant, c'est un char coince — quelle qu'en soit la cause. On le recale
      au centre de la voie la plus proche dans son sens, cap redressé,
      croisement rendu. Martin en a vu trois de travers dans une boîte ;
      plutôt que courir après chaque cause, on garantit la sortie. */
  /** Une attente LEGITIME : un vrai feu rouge, un stop qui s'egrene, ou une
      boite qu'un autre char n'a pas encore rendue.

      ⚠️ Elle est BORNEE, sinon elle serait une excuse a tout : un feu rouge
      dure au plus 480 images, l'attente de boite au plus `patience x 2`. Un
      char pris pour de vrai n'est jamais dans un de ces trois cas bien
      longtemps — et on ne compte pas contre lui le temps ou il a raison
      d'attendre. (C'est ce qui mordait a tort : 480 images de feu rouge PUIS
      110 d'attente de boite faisaient 600, et le chien sautait sur un char
      parfaitement sage.) */
  function attenteLegitime(v) {
    if (!v.attendFeu) return false;
    if (v.stopT !== undefined && v.stopT > 0) return true;
    if (v.attenteBoite > 0) return v.attenteBoite < trafic().patience_images * 2;
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    const p = PAS_FLECHE[v.sens] || [0, 0];
    const inter = Monde.intersectionA(tx + p[0], ty + p[1]);
    return !!inter && !Monde.feuVert(inter, v.sens);
  }

  function debloquer(v) {
    const immobile = Math.abs(v.vx) + Math.abs(v.vy) < 0.05 && !attenteLegitime(v);
    v.immobileT = immobile ? (v.immobileT || 0) + 1 : 0;
    // ⚠️ « Sur place » : il bouge, mais n'avance pas (un va-et-vient entre
    // deux cibles). Il n'est jamais immobile, le compteur ci-dessus ne le
    // voit pas ; la capture de Martin, elle, le montrait bien. On compare a
    // l'endroit ou il etait il y a dix secondes. Seul un vrai feu rouge excuse.
    if (!v.ancrage || B.t - v.ancrage.t >= 600) {
      if (v.ancrage && !attenteLegitime(v) && dist2(v.x, v.y, v.ancrage.x, v.ancrage.y) < 24 * 24) v.surPlace = (v.surPlace || 0) + 1;
      else v.surPlace = 0;
      v.ancrage = { x: v.x, y: v.y, t: B.t };
    }
    if (v.immobileT < 600 && !v.surPlace) return false;
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    v.etatBloque = etatCourt(v);                   // ce qu'il attendait, avant qu'on efface tout
    const voie = voieLaPlusProche(v, tx, ty);
    v.cible = null; v.sortie = null; v.enBoite = null; v.stopT = undefined; v.attenteBoite = 0; v.attendFeu = false;
    v.patience = 0; v.force = 90; v.immobileT = 0; v.surPlace = 0; v.ancrage = null; v.debloques = (v.debloques || 0) + 1;
    if (voie) {
      v.x = voie.x; v.y = voie.y;
      const q = PAS_FLECHE[v.sens] || [1, 0];
      v.angle = Math.atan2(q[1], q[0]);
    }
    return true;
  }

  function majConducteur(v) {
    const t = trafic();
    if (debloquer(v)) return;
    if (v.deportT > 0 && --v.deportT === 0) v.deportFroid = t.depassement_images;
    if (v.deportFroid > 0) v.deportFroid--;
    // L'escorte (Ti-Guy, M4) : elle te suit, et t'attend quand elle t'a rejoint.
    if (v.escorte && B.joueur && dist2(v.x, v.y, B.joueur.x, B.joueur.y) < 70 * 70) { rouler(v, 0); return; }
    if (!v.cible || (v.attendFeu && !v.cible.tx)) v.cible = prochaineCible(v);
    if (!v.cible) { majPhysique(v, { gaz: 0, frein: 1, direction: 0 }); return; }
    if (v.attendFeu) {
      // On attend (feu rouge, stop) : on redemande chaque image, sans bouger.
      v.cible = prochaineCible(v);
      if (v.attendFeu) { rouler(v, 0); return; }
      if (!v.cible) return;
    }
    const dx = v.cible.x - v.x, dy = v.cible.y - v.y;
    if (dx * dx + dy * dy < 36) {
      // Arrive : si c'etait la voie d'a cote, le deport est fini et on s'interdit
      // le suivant un moment — sinon un char zigzague entre deux voies.
      if (v.deportT > 0) { v.deportT = 0; v.deportFroid = t.depassement_images; }
      v.cible = prochaineCible(v);
      if (!v.cible) return;
    }
    const voulu = angleVers(v.x, v.y, v.cible.x, v.cible.y);
    const ecart = ecartAngle(v.angle, voulu);
    let vitesseVoulue = v.def.vitesse_max * (v.poursuite ? 0.85 : t.vitesse_ville);   // sirene : bien plus vite
    // ⚠️ On ralentit AVANT le coin, pas dedans : a 2,2 px/image le rayon de
    // braquage fait 3,6 tuiles, et un coin de rue en demande 1,5 — le char
    // ratait son virage et finissait sur le trottoir d'en face.
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    const ici = Monde.fleche(tx, ty);
    const p = PAS_FLECHE[v.sens] || [0, 0];
    const devant = Monde.fleche(tx + p[0] * 2, ty + p[1] * 2);
    if (ici === '+' || ici === 'S' || devant === '+' || devant === 'S') vitesseVoulue = Math.min(vitesseVoulue, v.poursuite ? 1.5 : 1.1);
    if (Math.abs(ecart) > 0.5) vitesseVoulue = Math.min(vitesseVoulue, 0.8);
    const obstacle = obstacleDevant(v);
    const proche = obstacle < t.distance_securite_px;
    // ⚠️ On decide de se tasser DE LOIN (deux fois la distance de securite),
    // pas au dernier moment : a une tuile du pieton, le deport serait un coup
    // de volant a 45 degres. De loin, la diagonale se voit venir.
    const deport = obstacle < t.distance_securite_px * 2 && changerDeVoie(v);
    if (proche && !deport) {
      vitesseVoulue = 0;
      v.patience++;
      if (v.patience > t.patience_images) { v.force = 90; v.patience = 0; v.klaxonT = 30; }
    } else {
      if (obstacle < t.distance_securite_px * 2) vitesseVoulue *= 0.5;
      // ⚠️ Tant qu'on longe l'obstacle, on reste SOUS la vitesse qui renverse :
      // on contourne un pieton plante sur la chaussee, on ne le fauche pas.
      if (deport && proche) vitesseVoulue = Math.min(vitesseVoulue, physique().renverse_vitesse_min * 0.9);
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
    if (Entree.neuf('attaque')) {
      // ⚠️ Un char a sirene n'a pas de klaxon sous le pouce : il a sa sirene.
      // Le boulot, lui, se prend au meme bouton — dans une ambulance, on
      // repond a l'appel et on part la sirene allumee, d'un seul geste.
      //
      // ⚠️ MAIS SEULEMENT QUAND ON L'ALLUME (retour de Martin). Le geste
      // inverse veut dire « j'ai fini », pas « donne-m'en un autre » : eteindre
      // sa sirene en sortant de l'hopital rappelait aussitot une ambulance,
      // et on repartait sans l'avoir demande.
      const allume = v.def.sirene && !v.sirene;
      if (v.def.sirene) { v.sirene = !v.sirene; Son.SFX.touche(); } else v.klaxonT = 30;
      // ⚠️ Sur la remorqueuse, le meme bouton accroche et decroche : le boulot
      // de remorquage EST le crochet, il n'y a pas deux gestes a apprendre.
      if (v.def.crochet) basculerCrochet(v);
      if ((!v.def.sirene || allume) && typeof Missions !== 'undefined' && Missions.boulot) Missions.boulot.klaxon(v);
    }
    if (Entree.neuf('action') && !B.cinema) descendre(j, false);   // (pendant un dialogue, ACTION passe la replique)
    if (Entree.neuf('arme')) {
      const station = Son.Radio.suivante();
      const def = station ? Son.Radio.station(station) : null;
      Hud.message(def ? 'RADIO : ' + def.nom.toUpperCase() : 'RADIO ETEINTE');
    }
    // Le moteur monte dans les tours.
    if (v.def.classe !== 'velo') Son.reglerBoucle('moteur', 0.35 + Math.abs(v.vitesse) / v.def.vitesse_max * 0.5, 0.7 + Math.abs(v.vitesse) / v.def.vitesse_max * 0.9);
  }

  // --- Boucle -------------------------------------------------------------------------

  //: A quelle distance on entend encore une sirene. Au-dela, elle se tait —
  //: sinon la moindre poursuite a l'autre bout du district hurle dans le
  //: casque, et une sirene qu'on entend toujours ne veut plus rien dire.
  const SIRENE_PORTEE_PX = 460;
  //: Une ambulance sur trois qui naît dans le trafic est EN COURSE. Les deux
  //: autres rentrent au garage : une ville ou toutes les ambulances hurlent
  //: n'est pas une ville, c'est une alarme.
  const AMBULANCE_EN_COURSE = 1 / 3;

  /** La boucle qui va avec ce char. ⚠️ DEUX sirenes, pas une : celle de la
      police monte et descend sans s'arreter, celle d'une ambulance fait deux
      notes, plus haut et plus lent. Les confondre, c'est ne pas savoir qui
      arrive derriere soi — et c'est toute la difference entre se ranger et
      se sauver. */
  function boucleDeSirene(v) { return v.def.police ? 'sirene' : 'sirene_ambulance'; }

  //: Ce que le melangeur a demande a `Son`, par boucle : 0 = eteinte.
  const sirenes = { sirene: 0, sirene_ambulance: 0 };

  /** Les sirenes : une boucle par sorte, au volume du char le plus proche qui
      la fait hurler.

      ⚠️ Avant, il n'y en avait qu'une, allumee a volume fixe des qu'une
      auto-patrouille chassait, et **jamais** pour une ambulance — dont la
      fiche declare pourtant `sirene: true` depuis M9. Au volant, on n'en avait
      aucune : on conduisait une ambulance en silence. */
  function majSirenes() {
    const j = B.joueur;
    const voulu = { sirene: 0, sirene_ambulance: 0 };
    if (j && !B.interieur) {
      for (const v of B.entites) {
        if (v.type !== 'vehicule' || v.etat === 'epave' || !v.sirene) continue;
        // Au volant, on l'a sur le toit : plein volume, sans distance.
        const d = v.conducteur === j ? 0 : Math.hypot(v.x - j.x, v.y - j.y);
        const part = Math.max(0, 1 - d / SIRENE_PORTEE_PX);
        const slug = boucleDeSirene(v);
        if (part > voulu[slug]) voulu[slug] = part;
      }
    }
    for (const slug in voulu) {
      const part = voulu[slug] > 0.02 ? voulu[slug] : 0;
      const avant = sirenes[slug] || 0;
      // ⚠️ Le melangeur retient CE QU'IL A DEMANDE, il ne lit pas l'etat de
      // `Son`. Un mp3 absent (ou un navigateur sans geste) laisse
      // `boucleActive` a faux pour toujours : s'y fier, c'est redemander la
      // meme boucle soixante fois par seconde sans jamais s'en rendre compte.
      if (part && !avant) Son.boucle(slug, true, part);
      else if (part) Son.reglerBoucle(slug, part);
      else if (avant) Son.boucle(slug, false);
      sirenes[slug] = part;
    }
  }

  function maj() {
    const j = B.joueur;
    if (!j || B.interieur) { majSirenes(); return; }
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const v = B.entites[i];
      if (v.type !== 'vehicule') continue;
      majEtatDuChar(v);
      if (v.etat === 'epave') { if (v.epaveT <= 0 && !Entites.visibleAEcran(v.x, v.y, 40)) Entites.retirer(v); continue; }
      if (v.conducteur === j) majJoueur(j);
      else if (v.conducteur === 'trafic') majConducteur(v);
      else if (v.conducteur === 'police') { const c = Police.commandes(v); if (c === 'rails') majConducteur(v); else majPhysique(v, c); }
      else majPhysique(v, { gaz: 0, frein: 0, direction: 0 });
      // La chasse finie, la sirene de l'auto-patrouille se tait.
      if (v.conducteur === 'police') v.sirene = B.recherche.etoiles > 0;
      if (v.conducteur === 'trafic' || (v.conducteur === 'police' && v.surRails)) {
        v.x += v.vx; v.y += v.vy;
        heurterVehicules(v);
        heurterPietons(v);
        if (B.options.trace) majTrace(v);
      } else if (Math.abs(v.vx) + Math.abs(v.vy) > 0.01 || v.z > 0) avancer(v);
      else { heurterPietons(v); }
      if (v.conducteur === j) { j.x = v.x; j.y = v.y; j.angle = v.angle; }
    }
    peupler();
    majSirenes();
    // ⚠️ LA PORTE GAGNE SUR LA PORTIERE (bug de Martin : devant le garage,
    // avec un char gare devant, « ENTRER » faisait monter dans le char). La
    // meme pression d'ACTION est lue ici APRES `Combat.maj`, dans la meme
    // image : si elle a deja ouvert un menu (ACHETER / ENTRER d'une
    // propriete) ou lance le fondu d'une porte, elle est depensee. Un menu
    // et un fondu figent tout le jeu (`Jeu.maj`) ; la portiere d'a cote ne
    // fait pas exception — sinon, au moment de choisir ENTRER, `Jeu.entrer`
    // refusait parce qu'on etait deja au volant.
    if (!j.dansVehicule && Entree.neuf('action') && !j.roule && j.descenduT !== B.t && !B.cinema && !B.menu && !B.transition) {
      const v = vehiculeSousLaMain(j);
      if (v && !Missions.interagir(j)) monter(j, v);
    }
  }

  // --- La trace : le trajet de chaque char, valide par le jeu lui-meme ----------------------
  //
  // Idee de Martin : plutot que de deviner au banc pourquoi un char reste pris,
  // le jeu DESSINE ses trajets (option TRACE, ou ?trace=1) et se surveille :
  // chien de garde declenche, char qui repasse dans la meme boite, char hors
  // de la chaussee. Chaque anomalie garde le trajet des huit dernieres secondes
  // et s'affiche en rouge sur place — une capture d'ecran suffit a la raconter.

  const TRACE_POINTS = 120, TRACE_TOUTES_LES = 4, TRACE_ANOMALIES_MAX = 30, TRACE_MONTRE = 600;
  let boitesId = 0;

  function noterLaBoite(v, inter) {
    inter.id = inter.id || ++boitesId;
    v.boites = v.boites || [];
    v.boites.push({ id: inter.id, t: B.t });
    if (v.boites.length > 8) v.boites.shift();
  }

  function anomalie(v, quoi, etat) {
    const a = { t: B.t, quoi: quoi, slug: v.slug, id: v.id, x: v.x, y: v.y, tx: Math.floor(v.x / TT), ty: Math.floor(v.y / TT),
                etat: etat || etatCourt(v), points: (v.trace || []).slice() };
    B.trace.anomalies.push(a);
    B.trace.total++;
    if (B.trace.anomalies.length > TRACE_ANOMALIES_MAX) B.trace.anomalies.shift();
    if (typeof console !== 'undefined' && console.warn) console.warn('[trace] ' + quoi + ' — ' + v.slug + '#' + v.id + ' en (' + a.tx + ',' + a.ty + ') ' + a.etat);
    return a;
  }

  /** L'etat d'un char de trafic en trois lettres : ce qu'il attend, depuis combien de temps. */
  function etatCourt(v) {
    let e = v.attendFeu ? 'FEU' : v.stopT !== undefined ? 'STOP' : v.attenteBoite > 0 ? 'BOITE' : v.deportT > 0 ? 'DEPORT' : v.enBoite ? 'DANS' : 'ROULE';
    if (v.immobileT > 60) e += ' ' + Math.round(v.immobileT / 60) + 'S';
    return e;
  }

  /** A chaque image, pour un char du trafic : le trajet, et les trois verifications. */
  function majTrace(v) {
    if (B.t % TRACE_TOUTES_LES === 0) {
      v.trace = v.trace || [];
      v.trace.push({ x: v.x, y: v.y });
      if (v.trace.length > TRACE_POINTS) v.trace.shift();
    }
    // 1. Le chien de garde a du le deplacer : les rails ont failli.
    if ((v.debloques || 0) > (v.traceDebloques || 0)) { v.traceDebloques = v.debloques; anomalie(v, 'CHIEN DE GARDE', v.etatBloque); }
    // 2. Il repasse dans la meme boite : il tourne en rond.
    if (v.boites && v.boites.length >= 3) {
      const dernier = v.boites[v.boites.length - 1];
      const memes = v.boites.filter(function (b) { return b.id === dernier.id && dernier.t - b.t < 1200; }).length;
      if (memes >= 3 && v.traceRond !== dernier.t) { v.traceRond = dernier.t; anomalie(v, 'TOURNE EN ROND'); }
    }
    // 3. Il roule hors de la chaussee.
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    const surRoute = Monde.estChaussee(tx, ty) || Monde.estRampe(tx, ty) || Monde.estPassage(tx, ty);
    v.horsVoieT = surRoute ? 0 : (v.horsVoieT || 0) + 1;
    if (v.horsVoieT === 90) anomalie(v, 'HORS VOIE');
  }

  /** Les anomalies encore fraiches (dix secondes) — ce que l'ecran montre. */
  function anomaliesFraiches() {
    return B.trace.anomalies.filter(function (a) { return B.t - a.t < TRACE_MONTRE; });
  }

  function dessinerTrace(ctx, vue) {
    const cx = vue.x, cy = vue.y;
    ctx.lineWidth = 1;
    for (const v of B.entites) {
      if (v.type !== 'vehicule' || (v.conducteur !== 'trafic' && v.conducteur !== 'police') || !v.trace) continue;
      if (!Entites.visibleAEcran(v.x, v.y, 80)) continue;
      const bloque = v.immobileT > 120;
      ctx.strokeStyle = bloque ? '#ff5a4e' : v.attendFeu || v.stopT !== undefined || v.attenteBoite > 0 ? '#ffd23a' : '#5fe08a';
      ctx.beginPath();
      v.trace.forEach(function (q, i) { if (i === 0) ctx.moveTo(q.x - cx, q.y - cy); else ctx.lineTo(q.x - cx, q.y - cy); });
      ctx.stroke();
      if (v.cible && v.cible.tx !== undefined) {           // ou il veut aller
        ctx.strokeStyle = '#7fc4ff';
        ctx.beginPath(); ctx.moveTo(v.x - cx, v.y - cy); ctx.lineTo(v.cible.tx * TT + 8 - cx, v.cible.ty * TT + 8 - cy); ctx.stroke();
      }
      if (v.sortie && v.sortie.tx !== undefined) {         // la sortie qu'il a choisie
        ctx.fillStyle = '#7fc4ff'; ctx.fillRect(v.sortie.tx * TT + 6 - cx, v.sortie.ty * TT + 6 - cy, 4, 4); B.stats.rects++;
      }
      Atlas.texte(ctx, etatCourt(v), Math.round(v.x - cx - 10), Math.round(v.y - cy - 16), bloque ? '#ff5a4e' : '#ffffff', 1);
    }
    for (const a of anomaliesFraiches()) {
      if (!Entites.visibleAEcran(a.x, a.y, 80)) continue;
      ctx.strokeStyle = '#ff5a4e';
      ctx.beginPath();
      a.points.forEach(function (q, i) { if (i === 0) ctx.moveTo(q.x - cx, q.y - cy); else ctx.lineTo(q.x - cx, q.y - cy); });
      ctx.stroke();
      if ((B.t >> 3) % 2 === 0) { ctx.beginPath(); ctx.arc(a.x - cx, a.y - cy, 12, 0, Math.PI * 2); ctx.stroke(); }
      Atlas.texte(ctx, a.quoi, Math.round(a.x - cx - 20), Math.round(a.y - cy + 14), '#ff5a4e', 1);
    }
  }

  /** Le bilan de la trace : ce que le HUD ecrit, ce qu'un test verifie. */
  function bilanTrace() {
    const chars = B.entites.filter(function (v) { return v.type === 'vehicule' && v.conducteur === 'trafic'; });
    return { chars: chars.length, immobiles: chars.filter(function (v) { return v.immobileT > 120; }).length,
             anomalies: B.trace.anomalies.length, total: B.trace.total, fraiches: anomaliesFraiches().length };
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
    // ⚠️ L'ombre est ce qui RACONTE la hauteur. Avant, c'etait un rectangle de
    // 20 x 10 fixe, pose des que `z > 2` : la meme tache pour une moto et pour
    // un autobus de 48 px, qui ne retrecissait pas, ne s'ecartait pas et ne
    // palissait pas. Une ombre collee sous le char ne dit aucune altitude —
    // c'est pour ca qu'un saut avait l'air de ne pas exister.
    //
    // Elle fait donc la taille du char, elle RETRECIT en montant, elle
    // S'ECARTE vers le sud-est (la lumiere vient du nord-ouest, comme pour les
    // facades) et elle palit. Et elle existe des le premier pixel de vol,
    // jamais a partir d'un seuil.
    if (v.z > 0) {
      const haut = Math.min(1, v.z / 30);                 // 0 au sol, 1 tres haut
      const l = Math.max(4, Math.round(v.def.longueur * (1 - haut * 0.35)));
      const h = Math.max(3, Math.round(v.def.largeur * (1 - haut * 0.35)));
      const ecart = Math.round(v.z * 0.35);
      ctx.fillStyle = 'rgba(0,0,0,' + (0.30 - haut * 0.14).toFixed(2) + ')';
      ctx.fillRect(Math.round(v.x - l / 2 + ecart - cx), Math.round(v.y - h / 2 + ecart - cy), l, h);
      B.stats.rects++;
    }
    ctx.drawImage(rot.images[i], Math.round(v.x - rot.cote / 2 - cx), Math.round(v.y - v.z - rot.cote / 2 - cy));
    B.stats.images++;
  }

  return {
    ROTATIONS, courbeBraquage, vehiculeDef, creer, peupler, cercles, bloqueParLesTuiles, defoncerDevant, sirenes, aCrocher, basculerCrochet, decrocher,
    majPhysique, avancer, endommager, exploser, declencherAlarme,
    vehiculeSousLaMain, monter, descendre, ejecter,
    prochaineCible, peutSortir, obstacleDevant, majConducteur, commandesJoueur, rouler,
    voieDeDepassement, voieLibre, changerDeVoie,
    croisementLibre, creerSignalisation, dessinerFeu, maj, dessinerUn,
    majTrace, dessinerTrace, bilanTrace, etatCourt,
  };
})();
