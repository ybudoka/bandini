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

    // L'ESQUIVE : trente secondes contre le cousin du Grand Mo, sans frapper,
    // dans un ring dégagé ; il attend au milieu qu'on y entre.
    esquive: {
      preparer: function (d, r, depart) {
        const c = ringDegage(depart, r.ring);
        if (!c) return null;
        const q = Entites.creerPieton(c.x, c.y, Entites.archetype('docker'));
        if (!q) return null;
        q.arme = null; q.etat = 'fige'; q.mission = true; q.plante = { x: c.x, y: c.y }; q.cousin = true;
        B.rue.poses.push(q);
        return { adversaire: q, phase: 'attend', t: 0, dehors: 0, depart: c };
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
        return e.t >= s(r.duree_s) ? { gagne: true } : null;
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
