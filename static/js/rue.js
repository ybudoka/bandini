/* Bandini — les épreuves dans la rue (les dix-huit défis, 3e vague, 23 sept. 2026).

   La filature et l'esquive. Comme les autres épreuves (`Adresse`, `Conduite`),
   ce sont des défis du catalogue (`rue` et `regles` dans `missions.DEFIS`) :
   `Histoire` les commence, les chronomètre, les finit et les paie. Ce module pose
   celui qu'on file ou celui qui cogne, le fait bouger, et juge.

   ⚠️ **LE SUSPECT MARCHE PAR SON POSTE** : c'est un passant `fige`, et un passant
   figé rejoint son point (`plante`) à pas de piéton (`Entites.majPieton`). On
   déplace le point le long d'un trottoir droit (`Conduite.pisteDroite`, la voie
   du bord, et le trottoir à sa droite) : il marche, s'arrête, se retourne — sans
   une ligne de plus dans le moteur des passants.

   ⚠️ **ON LE PERD, OU IL NOUS VOIT** : trop près trop longtemps, la méfiance
   monte ; quand il se retourne, tout ce qui est devant lui, pas trop loin et à
   découvert, est vu. Trop loin, on a quelques secondes pour le rattraper.

   ⚠️ **L'ESQUIVE SE JOUE SANS FRAPPER** : un seul coup parti (`j.phase`, ou une
   frappe qu'on charge, `j.charge`), et c'est raté. Il ne reste que la roulade
   (ESQUIVE) — ses images d'invincibilité et son souffle (`Combat.roulade`) — et
   le pas du boxeur, DANS le ring : on court plus vite que lui, et sans ring il
   suffirait de tourner en rond au loin. */

const Rue = (function () {
  'use strict';

  function s(sec) { return Math.round(sec * 60); }

  function present(e) { return B.entites.indexOf(e) >= 0; }

  const EPREUVES = {

    // LA FILATURE : un suspect sur le trottoir ; ni trop près, ni trop loin.
    filature: {
      preparer: function (d, r, depart) {
        const p = Conduite.pisteDroite(depart.x, depart.y, r.longueur, true);
        if (!p) return null;
        // Le trottoir : la tuile à DROITE de la voie du bord.
        const e = { piste: p, lat: TT, s: r.depart * TT, phase: 'attend', t: 0, mefiance: 0, perdu: 0,
                    prochainRegard: s(r.regard_tous_s[0]), regarde: 0 };
        const x0 = Conduite.point(p, e.s, e.lat);
        const q = Entites.creerPieton(x0.x, x0.y, Entites.archetype('passant'));
        if (!q) return null;
        q.etat = 'fige'; q.mission = true; q.plante = { x: x0.x, y: x0.y }; q.suspect = true;
        B.rue.poses.push(q);
        e.suspect = q;
        return e;
      },
      maj: function (e, r) {
        const q = e.suspect, j = B.joueur;
        if (!present(q) || !q.vivant || q.etat !== 'fige') return { gagne: false, raison: 'TU L\'AS BRUSQUÉ' };
        e.t++;
        const moi = j.dansVehicule || j;
        const d = Math.hypot(moi.x - q.x, moi.y - q.y);
        if (e.phase === 'attend') {
          if (e.t > s(1)) { e.phase = 'marche'; Hud.message('IL PART — SUIS-LE', 120); }
          return null;
        }
        const avant = Conduite.projeter(e.piste, moi.x, moi.y).s < e.s;
        // Il se retourne de temps en temps, et regarde un moment.
        if (e.regarde > 0) {
          e.regarde--;
          Entites.regarder(q, -e.piste.dx, -e.piste.dy);
          if (avant && d < r.vu * TT && Monde.ligneLibre(q.x, q.y, moi.x, moi.y)) return { gagne: false, raison: 'IL T\'A VU' };
        } else {
          if (--e.prochainRegard <= 0) {
            e.regarde = s(r.regard_s);
            e.prochainRegard = s(r.regard_tous_s[0] + B.rng() * (r.regard_tous_s[1] - r.regard_tous_s[0]));
            Entites.bulle(q, '?');
          } else {
            e.s += r.pas_px;
            const p = Conduite.point(e.piste, e.s, e.lat);
            q.plante = { x: p.x, y: p.y };
            Entites.regarder(q, e.piste.dx, e.piste.dy);
          }
        }
        if (d < r.proche * TT) {
          if (++e.mefiance > s(r.mefiance_s)) return { gagne: false, raison: 'IL T\'A REPÉRÉ' };
        } else e.mefiance = Math.max(0, e.mefiance - 0.5);
        if (d > r.loin * TT) {
          if (++e.perdu > s(r.perdu_s)) return { gagne: false, raison: 'TU L\'AS PERDU' };
        } else e.perdu = 0;
        if (e.s >= (r.longueur - 1) * TT) return { gagne: true };
        return null;
      },
      compte: function (e, r) {
        if (e.phase === 'attend') return '— IL VA PARTIR';
        if (e.perdu > 0) return '— TU LE PERDS ! ' + Math.max(1, Math.ceil((s(r.perdu_s) - e.perdu) / 60)) + ' S';
        if (e.regarde > 0) return '— IL SE RETOURNE !';
        if (e.mefiance > 0) return '— TROP PRÈS !';
        return '— SUIS-LE';
      },
      cible: function (e) { return e.suspect; },
    },

    // LE HOCKEY DE RUELLE (docs/jalons/le-hockey-de-ruelle.md) : trois contre trois dans une ruelle des
    // Erables, une balle orange, deux filets de fortune. On gagne par trois buts d'ecart avant la fin.
    // ⚠️ LES JEUNES SONT PEINTS (ni entites ni `B.rng()`) : ils decident sur LEUR generateur
    // (`mulberry`, seme par le jour et la partie), et la patinoire les retient. On court avec les
    // commandes du jeu : ATTAQUE lance, ESQUIVE passe. L'hiver, la ruelle est une patinoire : la balle glisse.
    hockey: {
      preparer: function (d, r, depart) {
        const piste = ruelleDeHockey(depart.x, depart.y, r.longueur);
        if (!piste) return null;
        const p = piste, milieu = { x: (p.x0 + p.x1) / 2, y: p.y };
        const place = function (equipe, rang) {
          const sens = equipe === 'nous' ? -1 : 1;           // nous defendons l'ouest
          return { x: milieu.x + sens * (30 + rang * 50), y: p.y + (rang % 2 ? -6 : 6) };
        };
        const jeunes = [];
        for (const equipe of ['nous', 'eux']) {
          for (let k = 0; k < (equipe === 'nous' ? 2 : 3); k++) {
            const q = place(equipe, k + (equipe === 'nous' ? 1 : 0));
            jeunes.push({ equipe: equipe, x: q.x, y: q.y, depart: q, k: k, angle: equipe === 'nous' ? 0 : Math.PI, repit: 0 });
          }
        }
        const graine = ((B.partie ? B.partie.jour : 0) * 7919 + (B.graine || 0)) >>> 0;
        return { piste: p, jeunes: jeunes, balle: { x: milieu.x, y: p.y, vx: 0, vy: 0 }, porteur: null,
                 nous: 0, eux: 0, phase: 'approche', t: 0, pause: 0, dehors: 0, de: mulberry(graine) };
      },
      maj: function (e, r) {
        const j = B.joueur, p = e.piste;
        if (e.phase === 'approche') {
          if (dansLaPatinoire(p, j.x, j.y, 0)) { e.phase = 'jeu'; Hud.message('MISE AU JEU! ATTAQUE LANCE, ESQUIVE PASSE', 150); }
          return null;
        }
        e.t++;
        // Sortir de la patinoire, c'est abandonner (trois secondes pour revenir).
        if (!dansLaPatinoire(p, j.x, j.y, 8)) { if (++e.dehors > s(3)) return { gagne: false, raison: 'TU AS QUITTÉ LA PATINOIRE' }; }
        else e.dehors = 0;
        if (e.pause > 0) { e.pause--; return null; }
        majHockey(e, r);
        if (e.nous - e.eux >= r.ecart) return { gagne: true };
        // ⚠️ Pas d'horloge a elle : le chrono du defi est le seul a l'ecran (deux chronos qui ne disent
        // pas la meme chose, c'etait la capture). Il tombe, c'est « TEMPS ÉCOULÉ ».
        return null;
      },
      compte: function (e, r) {
        if (e.phase === 'approche') return '— REJOINS LA RUELLE';
        return 'NOUS ' + e.nous + ' – ' + e.eux + ' CHEVREUILS';
      },
      cible: function (e) { return e.phase === 'approche' ? { x: (e.piste.x0 + e.piste.x1) / 2, y: e.piste.y } : { x: e.balle.x, y: e.balle.y }; },
      sol: function (ctx, e, r, vue) { dessinerHockey(ctx, e, vue); },
    },

    // L'ESQUIVE : trente secondes contre le cousin du Grand Mo, sans frapper,
    // dans un ring dégagé ; il attend au milieu qu'on y entre.
    esquive: {
      preparer: function (d, r, depart) {
        const c = ringDegage(depart, r.ring);
        if (!c) return null;
        const q = Entites.creerPieton(c.x, c.y, Entites.archetype('docker'));
        if (!q) return null;
        q.arme = null; q.etat = 'fige'; q.mission = true; q.plante = { x: c.x, y: c.y }; q.cousin = true;
        // ⚠️ C'EST LUI QUI DÉCIDE QUAND IL FRAPPE, pas le tic des passants (`coupsDictes`) : il
        // ANNONCE chaque coup, et il court aussi vite que toi — tourner en rond ne le sème plus.
        q.coupsDictes = true; q.allure = r.allure;
        B.rue.poses.push(q);
        return { adversaire: q, phase: 'attend', t: 0, dehors: 0, depart: c, annonce: 0, souffle: 0, coups: 0 };
      },
      /** Le combat part quand on entre dans le ring. */
      engager: function (e) {
        e.adversaire.etat = 'attaque_joueur';
        e.adversaire.plante = null;
        e.phase = 'combat';
        Entites.bulle(e.adversaire, 'ENVOYE !');
        Hud.message('TRENTE SECONDES — SANS FRAPPER', 120);
      },
      maj: function (e, r) {
        const q = e.adversaire, j = B.joueur;
        if (e.phase !== 'combat') {
          if (Math.hypot(j.x - e.depart.x, j.y - e.depart.y) < (r.ring - 1) * TT) EPREUVES.esquive.engager(e);
          return null;
        }
        e.t++;
        if (j.phase || j.charge > 0) return { gagne: false, raison: 'TU AS FRAPPÉ' };
        if (j.vie < r.vie_min * j.vieMax) return { gagne: false, raison: 'IL T\'A SONNÉ' };
        if (!present(q) || !q.vivant) return { gagne: false, raison: 'PLUS D\'ADVERSAIRE' };
        if (Math.hypot(j.x - e.depart.x, j.y - e.depart.y) > r.ring * TT) {
          if (++e.dehors > s(r.dehors_s)) return { gagne: false, raison: 'ESQUIVER, PAS FUIR' };
        } else e.dehors = 0;
        // ⚠️ Il reste sur toi : un passant qui cogne finit par se lasser.
        if (q.etat !== 'attaque_joueur' && q.etat !== 'attaque') q.etat = 'attaque_joueur';
        EPREUVES.esquive.boxer(e, r, q, j);
        return e.t >= s(r.duree_s) ? { gagne: true } : null;
      },
      /** LE COUSIN BOXE : il te colle, il ANNONCE son coup (`annonce_s` — il continue de te
          suivre, et le cercle de son poing se referme au sol), il cogne, il souffle (`souffle_s`).
          ⚠️ LA ROULADE DOIT SERVIR (29 sept. 2026) : il court aussi vite que toi (`allure`), son
          coup porte plus loin et plus large qu'une tape (`coup_portee`, `coup_arc`) — tourner
          en rond ne le sème plus, s'écarter d'un pas non plus. Une roulade dans l'annonce passe
          sous le coup (ses images d'invincibilité, `Combat.roulade`), ou hors de sa portée. */
      boxer: function (e, r, q, j) {
        if (q.etat !== 'attaque_joueur') return;
        if (e.annonce > 0) {
          if (--e.annonce > 0) return;
          if (Combat.frapper(q)) {
            q.arc = Object.assign({}, q.arc, { portee: r.coup_portee, arc: r.coup_arc, degats: r.coup_degats });
            e.coups++;
          }
          e.souffle = s(r.souffle_s);
        } else if (e.souffle > 0) e.souffle--;
        else if (Math.hypot(q.x - j.x, q.y - j.y) < r.arme_px) e.annonce = s(r.annonce_s);
      },
      compte: function (e, r) {
        if (e.phase !== 'combat') return '— ENTRE DANS LE RING';
        if (e.dehors > 0) return '— REVIENS DANS LE RING !';
        return '— ' + Math.max(0, Math.ceil((s(r.duree_s) - e.t) / 60)) + ' S, SANS FRAPPER';
      },
      cible: function (e) { return e.phase === 'combat' ? e.adversaire : e.depart; },
      // Le ring, peint au sol : un cercle de pointillés autour de là où il a chargé.
      sol: function (ctx, e, r, vue) {
        ctx.fillStyle = e.dehors > 0 ? '#ff5a4e' : '#e8b33c';
        const R = r.ring * TT;
        for (let k = 0; k < 64; k++) {
          const a = k * Math.PI / 32;
          ctx.fillRect(Math.round(e.depart.x + Math.cos(a) * R - vue.x), Math.round(e.depart.y + Math.sin(a) * R - vue.y), 2, 2);
        }
        B.stats.rects += 64;
        // LE COUP S'ANNONCE : un cercle rouge autour du cousin, de deux fois sa portée à sa portée,
        // qui se referme pendant l'annonce ; plein quand le poing part. ⚠️ C'est le signal qu'on
        // lit pour rouler — sans lui, cinq images d'élan (83 ms) ne se voient pas venir.
        const q = e.adversaire, T = s(r.annonce_s);
        const part = q.etat === 'attaque' && (q.phase === 'anticipation' || q.phase === 'actif');
        if (e.phase !== 'combat' || (!e.annonce && !part)) return;
        const P = r.coup_portee + 6, rayon = part ? P : P * (1 + e.annonce / T);
        ctx.fillStyle = part ? '#ff3a2e' : '#ff8a4e';
        for (let k = 0; k < 32; k++) {
          const a = k * Math.PI / 16;
          ctx.fillRect(Math.round(q.x + Math.cos(a) * rayon - vue.x), Math.round(q.y + Math.sin(a) * rayon - vue.y), 2, 2);
        }
        B.stats.rects += 32;
      },
    },
  };

  /** Le ring de l'esquive : le centre de tuile le plus proche de `depart` d'où, à
      `rayon` tuiles, il n'y a AUCUNE chaussée (ni voie, ni route) et presque que
      du sol où l'on marche. ⚠️ Au banc, une moto a fauché le joueur qui tournait
      dans un ring au bord d'une rue : ce qui passe sur la chaussée ne regarde
      pas où l'on boxe. Pas de dé : on balaie en anneaux, dans un ordre fixe. */
  function ringDegage(depart, rayon) {
    const tx0 = Math.floor(depart.x / TT), ty0 = Math.floor(depart.y / TT);
    const libre = function (cx, cy) {
      let tout = 0, pied = 0;
      for (let y = cy - rayon; y <= cy + rayon; y++) {
        for (let x = cx - rayon; x <= cx + rayon; x++) {
          if ((x - cx) * (x - cx) + (y - cy) * (y - cy) > rayon * rayon) continue;
          if (Monde.fleche(x, y) !== '.' || Monde.estChaussee(x, y)) return false;
          tout++;
          if (Monde.marchablePieton(x, y)) pied++;
        }
      }
      return pied >= tout * 0.85;
    };
    for (let k = 0; k <= 14; k++) {
      for (let dy = -k; dy <= k; dy++) {
        for (let dx = -k; dx <= k; dx++) {
          if (Math.max(Math.abs(dx), Math.abs(dy)) !== k) continue;
          if (libre(tx0 + dx, ty0 + dy)) return { x: (tx0 + dx) * TT + 8, y: (ty0 + dy) * TT + 8, nom: 'le ring' };
        }
      }
    }
    return null;
  }

  // --- Le hockey de ruelle ------------------------------------------------------------------

  /** La patinoire : la ruelle horizontale (deux rangees de `x` a la file, sur `longueur` tuiles) la plus
      proche de (x, y), a 80 tuiles au plus. Rend { x0, x1, y, haut, bas } en pixels, ou null. Sans de. */
  function ruelleDeHockey(x, y, longueur) {
    const tx0 = Math.floor(x / TT), ty0 = Math.floor(y / TT);
    const ruelle = function (tx, ty) { return Monde.glyphe(tx, ty) === 'x'; };
    let mieux = null, dMin = Infinity;
    for (let ty = ty0 - 80; ty <= ty0 + 80; ty++) {
      for (let tx = tx0 - 80; tx <= tx0 + 80; tx++) {
        if (!ruelle(tx, ty) || !ruelle(tx, ty + 1) || ruelle(tx - 1, ty)) continue;   // le debut d'un troncon
        let n = 0;
        while (n < longueur && ruelle(tx + n, ty) && ruelle(tx + n, ty + 1)) n++;
        if (n < longueur) continue;
        const d = Math.abs(tx + longueur / 2 - tx0) + Math.abs(ty - ty0);
        if (d < dMin) { dMin = d; mieux = { x0: tx * TT, x1: (tx + longueur) * TT, y: (ty + 1) * TT, haut: ty * TT, bas: (ty + 2) * TT }; }
      }
    }
    return mieux;
  }

  function dansLaPatinoire(p, x, y, marge) {
    return x >= p.x0 - marge && x <= p.x1 + marge && y >= p.haut - marge && y <= p.bas + marge;
  }

  //: Le filet : la moitie de son ouverture (la ruelle fait 32 px de large ; le filet, 16). A 20, un bon
  //: tireur gagnait par trois buts en quinze secondes : le gardien n'avait rien a couvrir.
  const FILET = 8;

  /** Retenir un corps dans la patinoire (les jeunes n'en sortent jamais). */
  function retenirDans(p, q) {
    q.x = Math.max(p.x0 + 4, Math.min(p.x1 - 4, q.x));
    q.y = Math.max(p.haut + 4, Math.min(p.bas - 4, q.y));
  }

  /** Une image de jeu : qui a la balle, ce que chacun fait, ou va la balle, et les buts. */
  function majHockey(e, r) {
    const p = e.piste, b = e.balle, j = B.joueur, de = e.de;
    const hiver = typeof Missions !== 'undefined' && Missions.hiverDeMotoneige && Missions.hiverDeMotoneige();
    // ⚠️ LE REPIT DU JOUEUR vit dans l'epreuve (`e.repitJoueur`), pas sur son entite : pose sur `j`, il
    // n'etait jamais decompte — apres son premier tir, le joueur ne touchait plus jamais la balle.
    if (e.repitJoueur > 0) e.repitJoueur--;
    const corps = [{ q: j, equipe: 'nous', joueur: true }].concat(e.jeunes.map(function (y) { return { q: y, equipe: y.equipe }; }));
    const enRepit = function (c) { return c.joueur ? e.repitJoueur > 0 : c.q.repit > 0; };
    const but = function (equipe) { return equipe === 'nous' ? p.x1 : p.x0; };       // le filet qu'on attaque
    // 1. LA POSSESSION : le plus proche de la balle, s'il est dessus et qu'elle ne file pas.
    // ⚠️ Le JOUEUR ramasse de plus loin (`prise_joueur`) et intercepte plus vite : c'est lui qu'on joue.
    const vite = Math.hypot(b.vx, b.vy);
    if (!e.porteur) {
      let mieux = null, dMin = Infinity;
      for (const c of corps) {
        if (enRepit(c)) continue;
        const d = Math.hypot(c.q.x - b.x, c.q.y - b.y);
        const portee = c.joueur ? r.prise_joueur : 7, seuil = c.joueur ? 5.2 : 3.5;
        if (d < portee && vite < seuil && d < dMin) { dMin = d; mieux = c; }
      }
      if (mieux) e.porteur = mieux;
    }
    // 1b. L'ARRET : une balle LANCEE qui frole le gardien (le jeune du rang 0, devant son filet) s'arrete
    // souvent sur lui — sans gardien, trois minutes faisaient vingt-sept buts.
    if (!e.porteur && vite >= 3.5) {
      for (const y of e.jeunes) {
        if (y.k !== 0 || y.repit > 0 || Math.hypot(y.x - b.x, y.y - b.y) > r.gardien_px) continue;
        if (de() < r.arret) { e.porteur = { q: y, equipe: y.equipe }; b.vx = 0; b.vy = 0; }
        else y.repit = 15;          // elle lui passe entre les jambes : il ne la reprend pas tout de suite
        break;
      }
    }
    // 2. LE VOL : un adversaire colle au porteur lui prend la balle, parfois (son de a lui).
    if (e.porteur) {
      for (const c of corps) {
        if (c.equipe === e.porteur.equipe || enRepit(c)) continue;
        if (Math.hypot(c.q.x - e.porteur.q.x, c.q.y - e.porteur.q.y) < 8 && de() < r.vol) {
          if (e.porteur.joueur) e.repitJoueur = 30; else e.porteur.q.repit = 30;
          e.porteur = c; break;
        }
      }
    }
    // 3. LES JEUNES : le plus proche de chaque equipe court a la balle ; les autres tiennent leur poste.
    for (const y of e.jeunes) {
      if (y.repit > 0) y.repit--;
      const monPorteur = e.porteur && e.porteur.q === y;
      let cx, cy;
      if (monPorteur && y.k === 0) {
        // LE GARDIEN a la balle : il la passe au plus avance des siens (il ne quitte pas son filet).
        const avant = corps.filter(function (c) { return c.equipe === y.equipe && c.q !== y; })
          .sort(function (a, c) { return y.equipe === 'nous' ? c.q.x - a.q.x : a.q.x - c.q.x; })[0];
        if (avant) { lancer(e, y, avant.q.x, avant.q.y, r.passe); continue; }
      }
      if (monPorteur) {
        // Il file vers le filet ; pres du but, ou quand on le colle, il lance.
        const cible = but(y.equipe);
        cx = cible; cy = p.y + (y.k % 2 ? -3 : 3);
        const colle = corps.some(function (c) { return c.equipe !== y.equipe && Math.hypot(c.q.x - y.x, c.q.y - y.y) < 12; });
        if (Math.abs(cible - y.x) < r.tir_px || (colle && de() < 0.05)) {
          const vise = p.y + (de() - 0.5) * FILET * r.dispersion;
          lancer(e, y, cible, vise, r.lancer);
          continue;
        }
      } else {
        const leMien = corps.filter(function (c) { return c.equipe === y.equipe && !c.joueur && c.q.k !== 0; })
          .sort(function (a, c) { return Math.hypot(a.q.x - b.x, a.q.y - b.y) - Math.hypot(c.q.x - b.x, c.q.y - b.y); })[0];
        if (leMien && leMien.q === y && (!e.porteur || e.porteur.equipe !== y.equipe)) { cx = b.x; cy = b.y; }
        else {
          // Le poste : le GARDIEN (rang 0) devant son filet, a la hauteur de la balle ; les autres
          // devant la balle, vers le filet d'en face.
          const monFilet = y.equipe === 'nous' ? p.x0 : p.x1, sens = y.equipe === 'nous' ? 1 : -1;
          if (y.k === 0) { cx = monFilet + sens * 10; cy = Math.max(p.y - FILET, Math.min(p.y + FILET, b.y)); }
          else { cx = b.x + sens * 50; cy = y.depart.y; }
        }
      }
      const dx = cx - y.x, dy = cy - y.y, d = Math.hypot(dx, dy);
      if (d > 1) { y.x += dx / d * r.vitesse_jeunes; y.y += dy / d * r.vitesse_jeunes; y.angle = Math.atan2(dy, dx); }
      retenirDans(p, y);
    }
    // 4. LE JOUEUR : ATTAQUE lance dans son cap, ESQUIVE passe au plus proche des siens.
    if (e.porteur && e.porteur.joueur) {
      if (Entree.neuf('attaque')) lancer(e, j, j.x + Math.cos(j.angle) * 100, j.y + Math.sin(j.angle) * 100, r.lancer);
      else if (Entree.neuf('esquive')) {
        const ami = e.jeunes.filter(function (y) { return y.equipe === 'nous'; })
          .sort(function (a, c) { return Math.hypot(a.x - j.x, a.y - j.y) - Math.hypot(c.x - j.x, c.y - j.y); })[0];
        if (ami) lancer(e, j, ami.x, ami.y, r.passe);
      }
    }
    // 5. LA BALLE : au bâton du porteur, ou libre — elle glisse, rebondit sur les bords.
    if (e.porteur) {
      const q = e.porteur.q, a = q.angle || 0;
      b.x = q.x + Math.cos(a) * 6; b.y = q.y + Math.sin(a) * 4; b.vx = 0; b.vy = 0;
    } else {
      b.x += b.vx; b.y += b.vy;
      const f = hiver ? r.frottement_glace : r.frottement;
      b.vx *= f; b.vy *= f;
      if (b.y < p.haut + 3 || b.y > p.bas - 3) { b.vy = -b.vy * 0.7; b.y = Math.max(p.haut + 3, Math.min(p.bas - 3, b.y)); }
    }
    // 6. LES BUTS : la balle passe une ligne de but DANS le filet.
    const dansLeFilet = Math.abs(b.y - p.y) < FILET;
    if (b.x >= p.x1 - 2 && dansLeFilet) marquer(e, 'nous');
    else if (b.x <= p.x0 + 2 && dansLeFilet) marquer(e, 'eux');
    else if (b.x < p.x0 + 2 || b.x > p.x1 - 2) { b.vx = -b.vx * 0.6; b.x = Math.max(p.x0 + 2, Math.min(p.x1 - 2, b.x)); }
  }

  function lancer(e, q, x, y, vitesse) {
    const b = e.balle, d = Math.hypot(x - b.x, y - b.y) || 1;
    b.vx = (x - b.x) / d * vitesse; b.vy = (y - b.y) / d * vitesse;
    if (q === B.joueur) e.repitJoueur = 20; else q.repit = 20;
    e.porteur = null;
    if (Son.SFX.cone) Son.SFX.cone();
  }

  function marquer(e, equipe) {
    e[equipe]++;
    const p = e.piste, b = e.balle;
    b.x = (p.x0 + p.x1) / 2; b.y = p.y; b.vx = 0; b.vy = 0; e.porteur = null;
    for (const y of e.jeunes) { y.x = y.depart.x; y.y = y.depart.y; y.repit = 0; }
    e.pause = 60;
    Hud.message(equipe === 'nous' ? 'BUT! ' + e.nous + ' – ' + e.eux : 'BUT DES CHEVREUILS… ' + e.nous + ' – ' + e.eux, 90);
    Son.SFX.klaxon();
  }

  /** La patinoire a l'ecran : les filets, la glace l'hiver, les jeunes et la balle (peints). */
  function dessinerHockey(ctx, e, vue) {
    const p = e.piste, hiver = typeof Missions !== 'undefined' && Missions.hiverDeMotoneige && Missions.hiverDeMotoneige();
    const X = function (x) { return Math.round(x - vue.x); }, Y = function (y) { return Math.round(y - vue.y); };
    if (X(p.x1) < -20 || X(p.x0) > VW + 20 || Y(p.bas) < -20 || Y(p.haut) > VH + 20) return;
    let n = 0;
    if (hiver) { ctx.fillStyle = 'rgba(200,228,250,0.55)'; ctx.fillRect(X(p.x0), Y(p.haut), p.x1 - p.x0, p.bas - p.haut); n++; }
    // Les filets : deux poteaux et le filet rouge.
    for (const fx of [p.x0, p.x1]) {
      const dir = fx === p.x0 ? -1 : 1;
      ctx.fillStyle = '#d23b2e'; ctx.fillRect(X(fx) + (dir > 0 ? 0 : -4), Y(p.y - FILET), 4, FILET * 2);
      ctx.fillStyle = '#f2f2f2'; ctx.fillRect(X(fx) - 1, Y(p.y - FILET) - 1, 2, 2); ctx.fillRect(X(fx) - 1, Y(p.y + FILET) - 1, 2, 2);
      n += 3;
    }
    // Les jeunes : tuque, chandail de l'equipe, baton dans leur cap.
    for (const y of e.jeunes) {
      const x = X(y.x), yy = Y(y.y), nous = y.equipe === 'nous';
      ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fillRect(x - 3, yy + 2, 6, 2);
      ctx.fillStyle = nous ? '#1f5fbf' : '#2e7d32'; ctx.fillRect(x - 2, yy - 5, 5, 5);
      ctx.fillStyle = '#e8b088'; ctx.fillRect(x - 1, yy - 8, 3, 3);
      ctx.fillStyle = nous ? '#e0453a' : '#f2c230'; ctx.fillRect(x - 1, yy - 9, 3, 1);
      ctx.fillStyle = '#2a2a30'; ctx.fillRect(x - 2, yy, 2, 2); ctx.fillRect(x + 1, yy, 2, 2);
      ctx.fillStyle = '#8a5a2a';
      ctx.fillRect(Math.round(x + Math.cos(y.angle) * 5), Math.round(yy + 1 + Math.sin(y.angle) * 3), 2, 1);
      n += 8;
    }
    // La balle orange.
    ctx.fillStyle = '#ff8c1a'; ctx.fillRect(X(e.balle.x) - 1, Y(e.balle.y) - 1, 3, 3);
    B.stats.rects += n + 1;
  }

  function defDe(slug) { return (B.defs.defis || []).find(function (q) { return q.slug === slug; }) || null; }

  /** Au panneau : pose le suspect, ou l'adversaire. Faux s'il n'y a pas de place. */
  function commencer(d) {
    const sorte = EPREUVES[d.rue];
    if (!sorte) return false;
    B.rue = { slug: d.slug, sorte: d.rue, poses: [] };
    const j = B.joueur;
    const e = sorte.preparer(d, d.regles, { x: j.x, y: j.y });
    if (!e) { fermer(); return false; }
    Object.assign(B.rue, e);
    Entites.indexer();
    return true;
  }

  function maj(d) {
    const e = B.rue;
    if (!e || e.slug !== d.slug) return null;
    return EPREUVES[e.sorte].maj(e, d.regles);
  }

  /** Ceux que l'épreuve a posés repartent. */
  function fermer() {
    const e = B.rue;
    if (!e) return;
    for (const q of e.poses) if (present(q)) Entites.retirer(q);
    B.rue = null;
  }

  /** Les marques d'une épreuve dans la rue, sur le sol (le ring de l'esquive). */
  function dessinerSol(ctx, vue) {
    const e = B.rue;
    if (!e || B.interieur) return;
    const d = defDe(e.slug), sorte = EPREUVES[e.sorte];
    if (d && sorte.sol) sorte.sol(ctx, e, d.regles, vue);
  }

  function compte(d) {
    const e = B.rue;
    return e && e.slug === d.slug ? EPREUVES[e.sorte].compte(e, d.regles) : '';
  }

  function cible(d) {
    const e = B.rue;
    return e && e.slug === d.slug ? EPREUVES[e.sorte].cible(e, d.regles) : null;
  }

  return { commencer, maj, fermer, compte, cible, dessinerSol, EPREUVES, defDe };
})();
