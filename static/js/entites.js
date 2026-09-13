/* Bandini — entites : une structure, un tableau, un tri par y.

   (x, y) est le point de contact au sol (les pieds). `r` est le rayon du
   cercle au sol pour les collisions. `z` est la hauteur (sauts, rampes) : y
   de tri = y, y de dessin = y - z.

   ⚠️ Tout ce qui bouge passe par le HACHAGE SPATIAL : chercher qui est a
   portee en parcourant les 300 entites de la carte coutait 300 tests par
   entite et par image. La grille de 64 px ramene ca a une poignee. Elle est
   REBATIE a chaque image plutot que tenue a jour : une entite qui bouge sans
   prevenir la grille est un bogue invisible, et 300 insertions ne coutent
   rien. */

const Entites = (function () {
  'use strict';

  const CELLULE = 64;
  //: Le monde vit dans une bulle autour du joueur : on peuple au-dela de
  //: l'ecran, on oublie plus loin encore. Entre les deux, personne n'apparait
  //: ni ne disparait sous les yeux du joueur.
  const BULLE_NAISSANCE = 300, BULLE_OUBLI = 520;
  const MAX_PIETONS = 22, MAX_PARTICULES = 300, MAX_DECALS = 150;

  let suivantId = 1;
  //: Deux index : le decor ne bouge JAMAIS (bati une fois, a la creation) et
  //: tout le reste est rebati a chaque image.
  //: ⚠️ Melanger les deux coutait 270 insertions par image — et surtout, un
  //: index vide hors de la boucle laissait traverser les arbres en silence.
  const grille = new Map();
  const grilleFixe = new Map();

  function cle(x, y) { return Math.floor(x / CELLULE) + ',' + Math.floor(y / CELLULE); }

  function ajouterA(index, e) {
    const k = cle(e.x, e.y);
    const liste = index.get(k);
    if (liste) liste.push(e); else index.set(k, [e]);
  }

  function creer(type, x, y, extra) {
    const e = {
      id: suivantId++, type: type, x: x, y: y, vx: 0, vy: 0, r: 5, z: 0, vz: 0,
      angle: 0, face: 'bas', etat: 'flane', t: 0,
      vie: 100, vieMax: 100, vivant: true,
      sprite: null, swaps: null, anim: { i: 0, dist: 0 },
      actif: true, dessine: true, solide: false,
      invincible: 0, recul: 0, saigne: 0, minuterie: 0, menace: null,
    };
    if (extra) Object.assign(e, extra);
    B.entites.push(e);
    return e;
  }

  function retirer(e) {
    const i = B.entites.indexOf(e);
    if (i >= 0) B.entites.splice(i, 1);
  }

  function vider() {
    B.entites.length = 0;
    B.particules.length = 0;
    B.decals.length = 0;
    B.joueur = null;
    grille.clear();
    grilleFixe.clear();
  }

  // --- Hachage spatial ------------------------------------------------------------

  function indexer() {
    grille.clear();
    for (const e of B.entites) {
      if (!e.actif || e.type === 'decor') continue;
      ajouterA(grille, e);
    }
  }

  /** Parcourt un index autour d'un point et rend ce qui passe le filtre. */
  function chercher(index, x, y, rayon, filtre) {
    const out = [];
    const c0x = Math.floor((x - rayon) / CELLULE), c1x = Math.floor((x + rayon) / CELLULE);
    const c0y = Math.floor((y - rayon) / CELLULE), c1y = Math.floor((y + rayon) / CELLULE);
    const r2 = rayon * rayon;
    for (let cy = c0y; cy <= c1y; cy++) {
      for (let cx = c0x; cx <= c1x; cx++) {
        const liste = index.get(cx + ',' + cy);
        if (!liste) continue;
        for (const e of liste) {
          if (dist2(e.x, e.y, x, y) > r2) continue;
          if (filtre && !filtre(e)) continue;
          out.push(e);
        }
      }
    }
    return out;
  }

  /** Ce qui BOUGE dans un rayon (px) : joueur, pietons, objets, projectiles. */
  function autour(x, y, rayon, filtre) { return chercher(grille, x, y, rayon, filtre); }

  /** Le decor solide dans un rayon — index fixe, donc jamais perime. */
  function decorAutour(x, y, rayon) { return chercher(grilleFixe, x, y, rayon, null); }

  function pietonsAutour(x, y, rayon) {
    return autour(x, y, rayon, function (e) { return e.type === 'pieton' && e.vivant; });
  }

  // --- Naissance ------------------------------------------------------------------

  function creerJoueur(x, y) {
    const p = B.partie;
    const tenue = (B.defs.tenues || []).find(function (t) { return t.slug === p.tenue; });
    const j = creer('joueur', x, y, {
      r: 5, sprite: 'joueur', swaps: tenue ? { c: tenue.couleur } : null,
      vie: p.vie, vieMax: 100, endurance: 100, arme: p.arme || 'poings',
      dansVehicule: null, flagrant: 0, pasDist: 0, coupT: 0, charge: 0, roule: 0,
    });
    B.joueur = j;
    return j;
  }

  function creerDecor(def) {
    grilleFixe.clear();
    (def.decor || []).forEach(function (d) {
      const fiche = DECORS[d.type] || {};
      const e = creer('decor', d.x * TT + 8, d.y * TT + 15, {
        decor: d.type, r: fiche.r === undefined ? 3 : fiche.r, solide: !!fiche.solide,
        dessine: true,
      });
      if (e.solide) ajouterA(grilleFixe, e);
    });
  }

  function archetype(slug) {
    const cat = B.defs.pietons.catalogue;
    for (const p of cat) if (p.slug === slug) return p;
    return cat[0];
  }

  /** Un passant au hasard, tire selon les poids du catalogue. */
  function archetypeDeRue() {
    const ordinaires = B.defs.pietons.catalogue.filter(function (p) { return p.frequence > 0 && !p.gang; });
    let tirage = B.rng() * ordinaires.reduce(function (s, p) { return s + p.frequence; }, 0);
    for (const p of ordinaires) {
      tirage -= p.frequence;
      if (tirage <= 0) return p;
    }
    return ordinaires[0];
  }

  function creerPieton(x, y, arch) {
    const p = arch || archetypeDeRue();
    const bourse = Math.round(p.argent[0] + B.rng() * (p.argent[1] - p.argent[0]));
    const e = creer('pieton', x, y, {
      r: p.sprite === 'enfant' ? 4 : 5, sprite: p.sprite || 'joueur', swaps: p.couleurs,
      arch: p.slug, gang: p.gang, metier: p.metier || null,
      vie: p.vie, vieMax: p.vie, allure: p.vitesse, courage: p.courage,
      probaTemoin: p.temoin, argent: bourse, arme: p.arme || null,
      intouchable: !!p.intouchable,
      etat: 'flane', dir: Math.floor(B.rng() * 4), butT: 0, cri: 0,
    });
    // Une mere ne sort pas sans son petit : il la suit, et il detale avec elle.
    if (p.accompagne) {
      const petit = creerPieton(x + 10, y + 4, archetype(p.accompagne));
      petit.suit = e;
      e.petit = petit;
    }
    return e;
  }

  /** Une tuile ou un pieton peut naitre : marchable, hors chaussee, hors ecran.
      Une fois sur trois, il SORT D'UNE PORTE — la ville a des dedans. */
  function placeDeNaissance() {
    const carte = Monde.carte;
    if (B.rng() < 0.34 && carte.portesFermees.length) {
      for (let essai = 0; essai < 8; essai++) {
        const porte = carte.portesFermees[Math.floor(B.rng() * carte.portesFermees.length)];
        const x = porte.x * TT + 8, y = (porte.y + 1) * TT + 8;
        if (dist2(x, y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI) continue;
        if (visibleAEcran(x, y, 24) || !Monde.marchablePieton(porte.x, porte.y + 1)) continue;
        return { x: x, y: y };
      }
    }
    for (let essai = 0; essai < 24; essai++) {
      const angle = B.rng() * Math.PI * 2;
      const rayon = BULLE_NAISSANCE + B.rng() * (BULLE_OUBLI - BULLE_NAISSANCE - 60);
      const x = B.joueur.x + Math.cos(angle) * rayon;
      const y = B.joueur.y + Math.sin(angle) * rayon;
      const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
      if (tx < 1 || ty < 1 || tx >= carte.w - 1 || ty >= carte.h - 1) continue;
      if (Monde.solidite(tx, ty) !== 0 || Monde.estRoute(tx, ty)) continue;
      if (visibleAEcran(x, y, 24)) continue;
      return { x: tx * TT + 8, y: ty * TT + 8 };
    }
    return null;
  }

  function visibleAEcran(x, y, marge) {
    const m = marge || 0;
    return x > B.cam.x - m && x < B.cam.x + VW + m && y > B.cam.y - m && y < B.cam.y + VH + m;
  }

  /** Au premier instant d'une partie, la rue est deja vivante : on peuple
      AUSSI l'ecran, une seule fois — personne ne voit apparaitre qui que ce
      soit, le voile du titre n'est pas encore tombe. */
  function peuplerDabord() {
    const zone = Monde.zoneA(B.joueur.x, B.joueur.y);
    const voulu = Math.min(MAX_PIETONS, zone ? zone.pietons : 12) * 0.6;
    for (let essai = 0; essai < 80 && B.entites.filter(function (e) { return e.type === 'pieton' && !e.metier; }).length < voulu; essai++) {
      const a = B.rng() * Math.PI * 2, d = 40 + B.rng() * 260;
      const tx = Math.floor((B.joueur.x + Math.cos(a) * d) / TT), ty = Math.floor((B.joueur.y + Math.sin(a) * d) / TT);
      if (!Monde.marchablePieton(tx, ty) || Monde.estPassage(tx, ty)) continue;
      creerPieton(tx * TT + 8, ty * TT + 8, null);
    }
    indexer();
  }

  /** Garde la rue peuplee : on nait hors champ, on s'oublie hors de la bulle. */
  function peupler() {
    let vivants = 0;
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const e = B.entites[i];
      if (e.type !== 'pieton') continue;
      const loin = dist2(e.x, e.y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI;
      if (loin && !visibleAEcran(e.x, e.y, 40)) { retirer(e); continue; }
      if (e.vivant && !e.metier) vivants++;
    }
    const zone = Monde.zoneA(B.joueur.x, B.joueur.y);
    const voulu = Math.min(MAX_PIETONS, zone ? zone.pietons : 12);
    if (vivants >= voulu || B.t % 12 !== 0) return;
    const place = placeDeNaissance();
    if (!place) return;
    // La nuit, pres du bar et du port, la Brume a ses habituees.
    const nuit = Monde.estNuit();
    if (nuit && zone && (zone.slug === 'port' || zone.slug === 'faubourg') && B.rng() < 0.18) {
      const fille = archetype('racoleuse');
      if (fille) {
        const e = creerPieton(place.x, place.y, fille);
        e.etat = 'arret';
        e.minuterie = 600;
        return;
      }
    }
    // Sur le territoire d'une gang, ce sont ses membres qui trainent dehors.
    const gang = zone && zone.gang && B.rng() < 0.5
      ? (B.defs.pietons.gangs.find(function (g) { return g.slug === zone.gang; }) || null)
      : null;
    creerPieton(place.x, place.y, gang ? archetype(gang.pieton) : null);
  }

  /** Les kiosques et les camions de la carte, avec quelqu'un derriere. */
  function creerAmbulants(def) {
    (def.ambulants || []).forEach(function (a) {
      const commerce = (B.defs.ambulants || []).find(function (c) { return c.slug === a.slug; });
      if (!commerce) return;
      const fiche = DECORS[commerce.sprite] || {};
      creer('ambulant', a.x * TT + 8, a.y * TT + 15, {
        decor: commerce.sprite, slug: a.slug, r: fiche.r === undefined ? 10 : fiche.r,
        solide: true, dessine: true,
      });
      ajouterA(grilleFixe, B.entites[B.entites.length - 1]);
      const vendeur = creerPieton(a.x * TT + 8, a.y * TT + 4, archetype('vendeur'));
      vendeur.etat = 'fige';
      vendeur.face = 'bas';
      vendeur.commerce = a.slug;
    });
  }

  /** Des armes de fortune trainent partout : un cone de chantier, une
      bouteille, une pelle. C'est ce qui permet de se battre sans rien acheter
      — et elles cassent au bout de quelques coups. */
  function semerDesArmesDeFortune() {
    if (B.t % 90 !== 0) return;
    let trainent = 0;
    for (const e of B.entites) if (e.type === 'ramassage' && e.fortune) trainent++;
    if (trainent >= 3) return;
    const fortunes = B.defs.armes.filter(function (a) { return a.usures > 0 && a.prix === 0; });
    if (!fortunes.length) return;
    const place = placeDeNaissance();
    if (!place) return;
    const arme = fortunes[Math.floor(B.rng() * fortunes.length)];
    creer('ramassage', place.x, place.y, {
      r: 4, objet: 'arme', arme: arme.slug, munitions: arme.chargeur, fortune: true, t: 0,
    });
  }

  // --- Deplacement avec collisions --------------------------------------------------

  /** Deplace un cercle (approche par boite) contre les tuiles, axe par axe. */
  function deplacerCercle(e, dx, dy, masque) {
    const r = e.r;
    if (dx !== 0) {
      e.x += dx;
      const ty0 = Math.floor((e.y - r) / TT), ty1 = Math.floor((e.y + r - 0.01) / TT);
      if (dx > 0) {
        const tx = Math.floor((e.x + r) / TT);
        for (let ty = ty0; ty <= ty1; ty++) if (Monde.bloque(tx, ty, masque)) { e.x = tx * TT - r - 0.01; break; }
      } else {
        const tx = Math.floor((e.x - r) / TT);
        for (let ty = ty0; ty <= ty1; ty++) if (Monde.bloque(tx, ty, masque)) { e.x = (tx + 1) * TT + r + 0.01; break; }
      }
    }
    if (dy !== 0) {
      e.y += dy;
      const tx0 = Math.floor((e.x - e.r) / TT), tx1 = Math.floor((e.x + e.r - 0.01) / TT);
      if (dy > 0) {
        const ty = Math.floor((e.y + r) / TT);
        for (let tx = tx0; tx <= tx1; tx++) if (Monde.bloque(tx, ty, masque)) { e.y = ty * TT - r - 0.01; break; }
      } else {
        const ty = Math.floor((e.y - r) / TT);
        for (let tx = tx0; tx <= tx1; tx++) if (Monde.bloque(tx, ty, masque)) { e.y = (ty + 1) * TT + r + 0.01; break; }
      }
    }
    bloquerParDecor(e);
  }

  function bloquerParDecor(e) {
    for (const d of decorAutour(e.x, e.y, e.r + 16)) {
      if (d === e) continue;
      const dx = e.x - d.x, dy = e.y - d.y;
      const min = e.r + d.r;
      const d2 = dx * dx + dy * dy;
      if (d2 >= min * min || d2 === 0) continue;
      const dist = Math.sqrt(d2);
      e.x = d.x + dx / dist * min;
      e.y = d.y + dy / dist * min;
    }
  }

  function dansLaCarte(e) {
    const c = Monde.carte;
    e.x = borner(e.x, e.r, c.pxW - e.r);
    e.y = borner(e.y, e.r, c.pxH - e.r);
  }

  function regarder(e, dx, dy) {
    if (dx === 0 && dy === 0) return;
    e.angle = Math.atan2(dy, dx);
    e.face = Math.abs(dx) >= Math.abs(dy) ? (dx > 0 ? 'droite' : 'gauche') : (dy > 0 ? 'bas' : 'haut');
  }

  // --- Joueur ---------------------------------------------------------------------------

  function majJoueur(j) {
    if (j.dansVehicule) return;
    const v = B.defs.recherche.vitesses;
    const axe = Entree.axe;
    if (j.roule > 0) {                       // roulade : on ne se dirige plus
      j.roule--;
      deplacerCercle(j, j.vx, j.vy, Monde.MASQUE_PIETON);
      dansLaCarte(j);
      if (j.roule === 0) j.invincible = 6;
      return;
    }
    const veutCourir = Entree.bas('esquive') || (axe.source !== 'clavier' && axe.mag > 0.85);
    let vitesse = v.joueur_marche;
    if (veutCourir && axe.mag > 0 && j.endurance > 0) {
      vitesse = v.joueur_sprint;
      j.endurance = Math.max(0, j.endurance - v.endurance_par_image);
    } else {
      j.endurance = Math.min(v.endurance, j.endurance + v.endurance_par_image * 0.6);
    }
    if (j.etat === 'attaque') vitesse *= 0.45;    // on frappe en marchant, pas en courant
    const mag = axe.source === 'clavier' ? axe.mag : Math.min(1, axe.mag * 1.15);
    j.vx = axe.x * vitesse * mag;
    j.vy = axe.y * vitesse * mag;
    if (axe.mag > 0) regarder(j, axe.x, axe.y);
    const avant = { x: j.x, y: j.y };
    deplacerCercle(j, j.vx, j.vy, Monde.MASQUE_PIETON);
    dansLaCarte(j);
    const d = Math.hypot(j.x - avant.x, j.y - avant.y);
    j.anim.dist += d;
    j.pasDist += d;
    if (j.pasDist > 14) { j.pasDist = 0; Son.SFX.pas(); }
    if (j.invincible > 0) j.invincible--;
    if (j.flagrant > 0) j.flagrant--;
    if (j.saigne > 0) saigner(j);
  }

  // --- Pietons --------------------------------------------------------------------------

  const DIRECTIONS = [[1, 0], [0, 1], [-1, 0], [0, -1]];

  function majPieton(e) {
    const v = B.defs.recherche.vitesses;
    const reactions = B.defs.pietons.reactions;
    if (!e.vivant) { if (e.saigne > 0) e.saigne--; return; }
    if (e.saigne > 0) saigner(e);

    if (e.etat === 'fige') { e.vx = 0; e.vy = 0; return; }
    // Le petit colle a sa mere : il ne flane jamais tout seul.
    if (e.suit && e.suit.vivant && e.etat !== 'fuit') {
      const ecart = B.defs.pietons.reactions.suite_distance_px;
      const dx = e.suit.x - e.x, dy = e.suit.y - e.y;
      const norme = Math.hypot(dx, dy);
      if (norme > ecart) {
        const vitesse = Math.min(v.pieton_course, v.pieton * e.allure * 1.6);
        e.vx = dx / norme * vitesse;
        e.vy = dy / norme * vitesse;
      } else { e.vx = 0; e.vy = 0; }
      deplacerCercle(e, e.vx, e.vy, Monde.MASQUE_PIETON);
      dansLaCarte(e);
      e.anim.dist += Math.abs(e.vx) + Math.abs(e.vy);
      regarder(e, e.vx, e.vy);
      return;
    }
    if (e.etat === 'assomme') {
      if (--e.minuterie <= 0) { e.etat = 'fuit'; e.minuterie = reactions.fuite_secondes * 60; e.face = 'bas'; }
      return;
    }
    if (e.recul > 0) {
      e.recul--;
      deplacerCercle(e, e.vx, e.vy, Monde.MASQUE_PIETON);
      e.vx *= 0.82; e.vy *= 0.82;
      dansLaCarte(e);
      return;
    }

    let vitesse = v.pieton * e.allure;
    if (e.etat === 'fuit' || e.etat === 'temoin') {
      vitesse = v.pieton_course * e.allure;
      if (--e.minuterie <= 0) { e.etat = 'flane'; e.cri = 0; }
      const menace = e.menace || B.joueur;
      const dx = e.x - menace.x, dy = e.y - menace.y;
      const norme = Math.hypot(dx, dy) || 1;
      e.vx = dx / norme * vitesse;
      e.vy = dy / norme * vitesse;
    } else if (e.etat === 'attaque_joueur') {
      vitesse = v.pieton_course * e.allure;
      const dx = B.joueur.x - e.x, dy = B.joueur.y - e.y;
      const norme = Math.hypot(dx, dy) || 1;
      if (norme > 260) { e.etat = 'flane'; }
      e.vx = dx / norme * vitesse;
      e.vy = dy / norme * vitesse;
      if (norme < 18 && e.t % 40 === 0) Combat.frapper(e);
    } else if (e.etat === 'arret') {
      // On s'arrete : on regarde une vitrine, on attend quelqu'un, on respire.
      e.vx = 0; e.vy = 0;
      if (--e.minuterie <= 0) e.etat = 'flane';
      return;
    } else if (e.etat === 'entre') {
      // Il rentre chez lui : un pas vers la porte, et il n'est plus la.
      e.vx = 0; e.vy = -vitesse;
      if (--e.minuterie <= 0) { retirer(e); return; }
    } else {
      // Flaner : on suit une direction jusqu'a ce qu'elle ne mene plus nulle part.
      const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
      if (Monde.estChaussee(tx, ty)) {
        // Pousse sur la chaussee (par un char) : on regagne le trottoir le plus proche.
        const refuge = trottoirLePlusProche(tx, ty);
        if (refuge) {
          const dx = refuge.x - e.x, dy = refuge.y - e.y, n = Math.hypot(dx, dy) || 1;
          e.vx = dx / n * v.pieton_course; e.vy = dy / n * v.pieton_course;
        }
      } else {
        if (e.butT-- <= 0) {
          if (B.rng() < 0.3) {
            e.etat = 'arret';
            e.minuterie = 50 + Math.floor(B.rng() * 160);
            e.butT = 90;
            e.vx = 0; e.vy = 0;
            return;
          }
          // Une porte juste au nord ? Une fois sur douze, on rentre.
          const g = Monde.glyphe(tx, ty - 1);
          if ((g === 'd' || g === 'D') && !e.metier && !e.suit && !e.petit && B.rng() < 0.08) {
            e.etat = 'entre'; e.minuterie = 40; e.face = 'haut';
            return;
          }
          e.dir = Math.floor(B.rng() * 4);
          e.butT = 90 + Math.floor(B.rng() * 240);
        }
        const dir = DIRECTIONS[e.dir];
        // ⚠️ La regle de la ville : on ne pose pas le pied sur la chaussee.
        // On traverse au passage, et seulement quand c'est sur.
        const ax = Math.floor((e.x + dir[0] * (e.r + 4)) / TT), ay = Math.floor((e.y + dir[1] * (e.r + 4)) / TT);
        if (Monde.estChaussee(ax, ay) || Monde.bloque(ax, ay, Monde.MASQUE_PIETON)) {
          e.dir = (e.dir + (B.rng() < 0.5 ? 1 : 3)) % 4;      // on tourne, on ne fonce pas
          e.butT = 60 + Math.floor(B.rng() * 120);
          e.vx = 0; e.vy = 0;
          return;
        }
        if (Monde.estPassage(ax, ay) && !Monde.estPassage(tx, ty) && !traverseeSure(ax, ay, dir)) {
          e.vx = 0; e.vy = 0;                                   // on attend au bord
          e.anim.dist = 0;
          return;
        }
        e.vx = dir[0] * vitesse;
        e.vy = dir[1] * vitesse;
      }
    }
    const avant = { x: e.x, y: e.y };
    deplacerCercle(e, e.vx, e.vy, Monde.MASQUE_PIETON);
    dansLaCarte(e);
    const bouge = Math.hypot(e.x - avant.x, e.y - avant.y);
    e.anim.dist += bouge;
    if (bouge < 0.2 && e.etat === 'flane') e.butT = 0;      // bloque : on change d'idee
    else if (bouge < 0.2) { e.dir = Math.floor(B.rng() * 4); e.vx = 0; e.vy = 0; }
    regarder(e, e.vx, e.vy);
    if (e.cri > 0) e.cri--;
  }

  /** La tuile de trottoir (ou d'herbe) la plus proche, en pixels. */
  function trottoirLePlusProche(tx, ty) {
    for (let r = 1; r <= 4; r++) {
      for (let dy = -r; dy <= r; dy++) {
        for (let dx = -r; dx <= r; dx++) {
          if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
          if (Monde.marchablePieton(tx + dx, ty + dy)) return { x: (tx + dx) * TT + 8, y: (ty + dy) * TT + 8 };
        }
      }
    }
    return null;
  }

  /** Peut-on s'engager sur ce passage ? Au feu : quand les chars de cette rue
      sont au rouge. Sans feu : quand aucun char n'approche. */
  function traverseeSure(tx, ty, dir) {
    const inter = Monde.intersectionA(tx, ty);
    // Le passage « = » barre une rue est-ouest : les chars y roulent en > <.
    const sensChars = Monde.glyphe(tx, ty) === '=' ? '>' : '^';
    if (inter && inter.feux) return !Monde.feuVert(inter, sensChars);
    const portee = B.defs.conduite.trafic.priorite_pieton_px;
    return autour(tx * TT + 8, ty * TT + 8, portee, function (q) {
      return q.type === 'vehicule' && q.etat !== 'epave' && Math.abs(q.vitesse) > 0.2;
    }).length === 0;
  }

  /** Un coup, une chute, un cri : qui voit ca prend peur (ou s'approche). */
  function alerter(x, y, menace, gravite) {
    const reactions = B.defs.pietons.reactions;
    // Un enfant prend peur de bien plus loin que les grandes personnes.
    const rayonMax = Math.max(reactions.peur_rayon_tuiles, reactions.enfant_peur_tuiles) * TT;
    for (const e of pietonsAutour(x, y, rayonMax)) {
      const rayon = (e.intouchable ? reactions.enfant_peur_tuiles : reactions.peur_rayon_tuiles) * TT;
      if (dist2(e.x, e.y, x, y) > rayon * rayon) continue;
      if (e === menace || e.etat === 'assomme') continue;
      if (!Monde.ligneLibre(e.x, e.y, x, y)) continue;
      if (e.intouchable) {                       // l'enfant ne fait que detaler
        e.etat = 'fuit'; e.menace = menace; e.minuterie = reactions.fuite_secondes * 90; e.cri = 120;
        continue;
      }
      if (e.gang && gravite >= 1) { e.etat = 'attaque_joueur'; e.cri = 90; continue; }
      if (e.courage > 0 && B.rng() < e.courage * 0.5 && gravite >= 2) {
        e.etat = 'attaque_joueur'; e.cri = 90; continue;
      }
      if (e.etat !== 'fuit' && e.etat !== 'temoin') {
        e.etat = B.rng() < e.probaTemoin ? 'temoin' : 'fuit';
        e.menace = menace;
        e.minuterie = reactions.fuite_secondes * 60;
        e.cri = 120;
      }
    }
  }

  function saigner(e) {
    const reactions = B.defs.pietons.reactions;
    e.saigne--;
    if (e.saigne % 60 === 0) {
      e.vie -= reactions.degats_saignement;
      goutte(e.x, e.y);
      if (e.vie <= 0 && e.vivant) { if (e.type === 'joueur') Missions.hopital(e.menace); else tuer(e, e.menace); }
    }
  }

  /** Blesse une entite. Rend true si le coup a porte. */
  function blesser(e, degats, source, options) {
    const opts = options || {};
    if (!e.vivant || e.invincible > 0) return false;
    // ⚠️ RIEN n'atteint un enfant : ni un poing, ni une balle, ni un char. Le
    // jeu est adulte, pas ca. Il prend peur et il court, point.
    if (e.intouchable) {
      e.etat = 'fuit';
      e.menace = source;
      e.minuterie = B.defs.pietons.reactions.fuite_secondes * 90;
      e.cri = 120;
      alerter(e.x, e.y, source, 1);
      return false;
    }
    e.vie -= degats;
    e.menace = source || e.menace;
    e.recul = Math.max(e.recul, opts.renverse ? 22 : 8);
    const angle = opts.angle === undefined ? angleVers(source ? source.x : e.x, source ? source.y : e.y, e.x, e.y) : opts.angle;
    const poussee = opts.renverse ? 3.2 : 1.4;
    e.vx = Math.cos(angle) * poussee;
    e.vy = Math.sin(angle) * poussee;
    if (opts.saigne) e.saigne = Math.min(B.defs.pietons.reactions.saignement_images, opts.saigne);
    if (e !== B.joueur) sang(e.x, e.y, opts.saigne ? 6 : 3);
    Son.SFX.touche();
    if (e.vie <= 0 && e.type === 'joueur') {
      Missions.hopital(source);
    } else if (e.vie <= 0) {
      if (opts.assomme) assommer(e);
      else tuer(e, source);
    } else if (e.type === 'pieton') {
      alerter(e.x, e.y, source, 2);
      if (e.etat !== 'attaque_joueur') {
        e.etat = (e.courage > 0 && B.rng() < e.courage) ? 'attaque_joueur' : 'fuit';
        e.minuterie = B.defs.pietons.reactions.fuite_secondes * 60;
      }
    }
    return true;
  }

  function assommer(e) {
    e.vie = 1;
    e.etat = 'assomme';
    e.face = 'couche';
    e.minuterie = B.defs.pietons.reactions.ko_images;
    e.vx = 0; e.vy = 0;
    if (e.arme) lacherArme(e);
  }

  function tuer(e, source) {
    if (!e.vivant) return;
    e.vivant = false;
    e.vie = 0;
    e.etat = 'mort';
    e.face = 'couche';
    e.solide = false;
    e.vx = 0; e.vy = 0;
    sang(e.x, e.y, 14);
    if (e.arme) lacherArme(e);
    if (e.type === 'pieton') {
      B.partie.stats.tues++;
      alerter(e.x, e.y, source, 3);
      if (source === B.joueur) {
        Police.signalerCrime('mort_pieton', e.x, e.y, Police.quelqu_un_voit(e.x, e.y, e));
      }
    }
  }

  function lacherArme(e) {
    const def = Combat.armeDef(e.arme);
    if (!def || def.prix === 0 && def.slug === 'poings') { e.arme = null; return; }
    creer('ramassage', e.x + (B.rng() - 0.5) * 8, e.y + 4, {
      r: 4, objet: 'arme', arme: e.arme, munitions: def.chargeur, t: 0, solide: false,
    });
    e.arme = null;
  }

  // --- Particules, sang, decalques ----------------------------------------------------

  function particule(x, y, vx, vy, vie, couleur, taille, gravite) {
    if (B.particules.length >= MAX_PARTICULES) B.particules.shift();
    B.particules.push({ x: x, y: y, z: 4, vx: vx, vy: vy, vz: 1.2, vie: vie, vieMax: vie,
                        c: couleur, s: taille || 1, g: gravite === undefined ? 0.22 : gravite });
  }

  function sang(x, y, nombre) {
    if (!B.options.sang) { poussiere(x, y, 3); return; }
    for (let i = 0; i < nombre; i++) {
      const a = B.rng() * Math.PI * 2, v = 0.4 + B.rng() * 1.6;
      particule(x, y, Math.cos(a) * v, Math.sin(a) * v * 0.6, 18 + B.rng() * 14, '#8e1b1b', 1);
    }
    if (nombre >= 6) decal(x, y, 'sang');
  }

  function goutte(x, y) {
    if (!B.options.sang) return;
    particule(x, y, 0, 0.2, 20, '#8e1b1b', 1);
    if (B.rng() < 0.4) decal(x, y, 'goutte');
  }

  function poussiere(x, y, nombre) {
    for (let i = 0; i < nombre; i++) {
      const a = B.rng() * Math.PI * 2;
      particule(x, y, Math.cos(a) * 0.6, Math.sin(a) * 0.4, 14, '#b9b2a4', 1);
    }
  }

  function decal(x, y, type) {
    if (!B.options.sang && type !== 'impact') return;
    if (B.decals.length >= MAX_DECALS) B.decals.shift();
    B.decals.push({ x: x, y: y, type: type, v: Math.floor(B.rng() * 4) });
  }

  function majParticules() {
    for (let i = B.particules.length - 1; i >= 0; i--) {
      const p = B.particules[i];
      p.x += p.vx; p.y += p.vy;
      p.z += p.vz; p.vz -= p.g;
      if (p.z <= 0) { p.z = 0; p.vz = 0; p.vx *= 0.6; p.vy *= 0.6; }
      if (--p.vie <= 0) B.particules.splice(i, 1);
    }
  }

  // --- Boucle ---------------------------------------------------------------------------

  function maj() {
    indexer();
    let actifs = 0;
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const e = B.entites[i];
      if (!e.actif) continue;
      e.t++;
      if (e.type === 'joueur') majJoueur(e);
      else if (e.type === 'pieton') { majPieton(e); actifs++; }
      else if (e.type === 'ramassage'
               && (e.t > 3600 || dist2(e.x, e.y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI)) {
        retirer(e);
      }
    }
    majParticules();
    if (B.joueur) { peupler(); semerDesArmesDeFortune(); }
    B.stats.actifs = actifs;
  }

  // --- Dessin ------------------------------------------------------------------------------

  function imageDe(e) {
    const def = SPRITES[e.sprite];
    if (!def) return null;
    const cuit = Atlas.cuire(e.sprite, def, e.swaps);
    const poses = cuit.poses[e.face] || cuit.poses.bas;
    const bouge = Math.abs(e.vx) + Math.abs(e.vy) > 0.05;
    // ⚠️ Une foulee de 9 px, pas 7 : a 7, les jambes tournaient plus vite que
    // le corps n'avancait et tout le monde avait l'air de courir.
    const i = bouge ? [0, 1, 0, 2][Math.floor(e.anim.dist / 9) % 4] : 0;
    return { canvas: poses[Math.min(i, poses.length - 1)], ancre: cuit.ancre };
  }

  function dessinerDecals(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const d of B.decals) {
      if (d.x < cx - 16 || d.x > cx + VW + 16 || d.y < cy - 16 || d.y > cy + VH + 16) continue;
      const image = Atlas.cuirePeintre('decal|' + d.type + '|' + d.v, 16, 12, function (c, w, h) {
        DECALS[d.type](c, d.v, w, h);
      });
      ctx.drawImage(image, Math.round(d.x - 8 - cx), Math.round(d.y - 6 - cy));
      B.stats.images++;
    }
  }

  function dessinerParticules(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const p of B.particules) {
      const x = Math.round(p.x - cx), y = Math.round(p.y - p.z - cy);
      if (x < -4 || y < -4 || x > VW + 4 || y > VH + 4) continue;
      ctx.globalAlpha = Math.min(1, p.vie / (p.vieMax * 0.4));
      ctx.fillStyle = p.c;
      ctx.fillRect(x, y, p.s, p.s);
      B.stats.rects++;
    }
    ctx.globalAlpha = 1;
  }

  function dessiner(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    const visibles = [];
    for (const e of B.entites) {
      if (!e.dessine) continue;
      if (e.x < cx - 40 || e.x > cx + VW + 40 || e.y < cy - 48 || e.y > cy + VH + 48) continue;
      visibles.push(e);
    }
    // ⚠️ Les morts d'abord : un cadavre se fait marcher dessus, il ne cache
    // jamais un vivant.
    visibles.sort(function (a, b) {
      return (a.vivant ? 1 : 0) - (b.vivant ? 1 : 0) || a.y - b.y || a.id - b.id;
    });
    B.stats.entites = visibles.length;
    const ombre = Atlas.cuirePeintre('ombre', DECORS.ombre.w, DECORS.ombre.h, DECORS.ombre.peindre);
    for (const e of visibles) {
      if (e.decor) {                 // decor ET commerces ambulants
        const d = DECORS[e.decor];
        if (!d) continue;
        const c = Atlas.cuirePeintre('decor|' + e.decor, d.w, d.h, d.peindre);
        ctx.drawImage(c, Math.round(e.x - d.ancre[0] - cx), Math.round(e.y - d.ancre[1] - cy));
        B.stats.images++;
        continue;
      }
      if (e.type === 'vehicule') { Vehicules.dessinerUn(ctx, e, cx, cy); continue; }
      if (e.type === 'feu') { Vehicules.dessinerFeu(ctx, e, cx, cy); continue; }
      if (e.type === 'ramassage') {
        const def = Combat.armeDef(e.arme);
        const c = Atlas.cuirePeintre('objet|' + (def ? def.sprite : 'poings'), 16, 10, function (g, w, h) {
          OBJETS[def && OBJETS[def.sprite] ? def.sprite : 'defaut'](g, w, h);
        });
        const flotte = Math.sin(e.t / 14) * 1.5;
        ctx.drawImage(c, Math.round(e.x - 8 - cx), Math.round(e.y - 8 + flotte - cy));
        B.stats.images++;
        continue;
      }
      const img = imageDe(e);
      if (!img) continue;
      if (e.vivant) ctx.drawImage(ombre, Math.round(e.x - 6 - cx), Math.round(e.y - 3 - cy));
      if (e.invincible > 0 && (e.invincible >> 2) % 2 === 0) continue;
      ctx.drawImage(img.canvas, Math.round(e.x - img.ancre[0] - cx), Math.round(e.y - e.z - img.ancre[1] - cy));
      B.stats.images += 2;
      // La bulle du temoin : on doit VOIR qu'on a ete vu.
      if (e.cri > 0 && e.vivant) {
        const bulle = Atlas.cuirePeintre('bulle|' + (e.etat === 'temoin' ? 't' : 'p'), 8, 10, function (g, w, h) {
          BULLES[e.etat === 'temoin' ? 'temoin' : 'peur'](g, w, h);
        });
        ctx.drawImage(bulle, Math.round(e.x - 4 - cx), Math.round(e.y - 26 - cy));
        B.stats.images++;
      }
    }
  }

  return {
    CELLULE, BULLE_NAISSANCE, BULLE_OUBLI, MAX_PIETONS, MAX_DECALS, MAX_PARTICULES,
    creer, retirer, vider, creerJoueur, creerDecor, creerAmbulants, creerPieton,
    archetype, archetypeDeRue,
    indexer, autour, decorAutour, pietonsAutour, placeDeNaissance, peupler, peuplerDabord,
    semerDesArmesDeFortune, visibleAEcran,
    deplacerCercle, dansLaCarte, regarder, majJoueur, majPieton, maj,
    blesser, assommer, tuer, alerter, lacherArme, traverseeSure, trottoirLePlusProche,
    particule, sang, poussiere, decal, majParticules,
    dessiner, dessinerDecals, dessinerParticules, imageDe,
  };
})();
