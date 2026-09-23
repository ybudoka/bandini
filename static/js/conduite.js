/* Bandini — les épreuves au volant (les dix-huit défis, 2e vague, 23 sept. 2026).

   Le frein pile, le démarrage au feu, le créneau, le slalom, le verre de lait
   et le remorquage. Comme les épreuves debout (`Adresse`), ce sont des défis du
   catalogue (`conduite` et `regles` dans `missions.DEFIS`) : `Histoire` les
   commence, les chronomètre, les finit et les paie. Ce module les JOUE : il
   trouve un bout de rue, y peint ses marques, pose ce qu'il faut (deux chars
   garés, une épave, une remorqueuse), lit la conduite, et retire tout à la fin.

   ⚠️ **UN BOUT DE RUE DROIT, SANS CROISEMENT** (`pisteDroite`) : les tuiles d'une
   même voie (`Monde.fleche`, `>` `<` `^` `v`) à la file. Un croisement change le
   glyphe, donc une piste n'en traverse jamais. On la cherche autour du panneau,
   la plus proche, sans dé : deux joueurs ont la même.

   ⚠️ **LES CÔNES NE SONT PAS DES ENTITÉS** : peints au sol, heurtés par la
   géométrie. Un décor posé en cours de partie prendrait un numéro, et tout ce
   qui se tire à l'empreinte d'un numéro changerait de tirage.

   ⚠️ **LES CHARS POSÉS PAR UNE ÉPREUVE SONT `mission`** : la ville ne les oublie
   pas quand on s'éloigne, la fourrière ne les prend pas — et `fermer` les
   retire, sauf celui qu'on conduit. Leur couleur est donnée : `Vehicules.creer`
   ne tire alors aucun dé.

   ⚠️ **LES À-COUPS SE LISENT SUR LA COMMANDE, PAS SUR LA VITESSE**
   (`Vehicules.commandesJoueur`) : lancée, une auto perd par la friction autant
   qu'elle gagne au gaz, et une mesure de la vitesse prendrait la route pour un
   coup de frein. C'est ce qui exclut le clavier du verre de lait et du
   remorquage, et le catalogue l'écrit : ses touches donnent tout le gaz ou
   rien, tout le frein ou rien. */

const Conduite = (function () {
  'use strict';

  const DIRS = { '>': [1, 0], '<': [-1, 0], 'v': [0, 1], '^': [0, -1] };
  //: On cherche la piste à cette distance du panneau, en tuiles.
  const RAYON_PISTE = 16;
  //: Arrêté, c'est sous cette vitesse (px/image).
  const ARRET = 0.05;
  //: Le rayon d'un cône, pour qui le heurte. ⚠️ Posé sur la ligne entre deux voies,
  //: il laisse passer une auto (14 px) roulant au milieu de la sienne (16 px) — pas plus.
  const CONE_R = 1;

  function s(sec) { return Math.round(sec * 60); }

  function estVoie(g) { return !!DIRS[g]; }

  /** Pas de chaussée à DROITE de cette tuile (pour qui roule dans son sens) :
      c'est la voie du bord, celle où l'on se gare. */
  function bordADroite(tx, ty, g) {
    const d = DIRS[g], v = Monde.fleche(tx - d[1], ty + d[0]);
    return !estVoie(v) && v !== '+';
  }

  /** Le bout de rue droit le plus proche de (x, y) : `longueur` tuiles d'une même
      voie à la file (`bord` : la voie du bord, tout du long). Rend `{ x, y, dx, dy }`
      — le centre de la première tuile, en pixels, et le sens — ou null. */
  function pisteDroite(x, y, longueur, bord) {
    const tx0 = Math.floor(x / TT), ty0 = Math.floor(y / TT);
    let meilleur = null, dMin = Infinity;
    for (let dy = -RAYON_PISTE; dy <= RAYON_PISTE; dy++) {
      for (let dx = -RAYON_PISTE; dx <= RAYON_PISTE; dx++) {
        const d = Math.abs(dx) + Math.abs(dy);
        if (d >= dMin) continue;
        const tx = tx0 + dx, ty = ty0 + dy, g = Monde.fleche(tx, ty);
        if (!estVoie(g)) continue;
        const sens = DIRS[g];
        let n = 0;
        while (n < longueur && Monde.fleche(tx + sens[0] * n, ty + sens[1] * n) === g
               && (!bord || bordADroite(tx + sens[0] * n, ty + sens[1] * n, g))) n++;
        if (n < longueur) continue;
        meilleur = { x: tx * TT + 8, y: ty * TT + 8, dx: sens[0], dy: sens[1] };
        dMin = d;
      }
    }
    return meilleur;
  }

  /** Le pixel à `sl` pixels devant le début de la piste et `lat` à sa droite. */
  function point(p, sl, lat) {
    return { x: p.x + p.dx * sl - p.dy * lat, y: p.y + p.dy * sl + p.dx * lat };
  }

  /** Où est (x, y) sur la piste : `s` devant, `lat` à droite, en pixels. */
  function projeter(p, x, y) {
    const ex = x - p.x, ey = y - p.y;
    return { s: ex * p.dx + ey * p.dy, lat: -ex * p.dy + ey * p.dx };
  }

  /** L'écart d'angle entre le char et la piste, sans tenir compte du sens (0 à π/2). */
  function travers(p, angle) {
    const a = Math.abs(((angle - Math.atan2(p.dy, p.dx)) % Math.PI + Math.PI) % Math.PI);
    return Math.min(a, Math.PI - a);
  }

  /** Un char posé par l'épreuve : garé, `mission`, de la PREMIÈRE couleur de sa fiche. */
  function poser(slug, x, y, angle) {
    const def = Vehicules.vehiculeDef(slug);
    const v = Vehicules.creer(slug, x, y, angle, { etat: 'stationne', couleur: def.couleurs[0], mission: true });
    if (v) B.conduite.poses.push(v);
    return v;
  }

  /** Les à-coups d'une image : ce qu'on demande AU-DELÀ de la douceur permise
      (le gaz, le frein, le volant à vitesse), de 0 à 1 par commande. */
  function aCoups(v, r) {
    const c = Vehicules.commandesJoueur(v);
    const vite = Math.abs(v.vitesse) / v.def.vitesse_max;
    return Math.max(0, c.gaz - r.gaz) + Math.max(0, (v.vitesse > 0.15 ? c.frein : 0) - r.frein)
      + Math.max(0, Math.abs(v.volant || 0) * vite - r.virage) + (c.freinMain ? 1 : 0);
  }

  /** Le cap de la voie sous ce pixel (un char garé dans le sens de la rue). */
  function capDeLaVoie(p) {
    const d = DIRS[Monde.fleche(Math.floor(p.x / TT), Math.floor(p.y / TT))] || [1, 0];
    return Math.atan2(d[1], d[0]);
  }

  /** Le temps (en images) que met CE char, pied au plancher depuis l'arrêt, pour
      faire `distance` pixels — sa physique à lui (`Vehicules.majPhysique`). */
  function tempsIdeal(v, distance) {
    let u = 0, d = 0, n = 0;
    while (d < distance && n < 3600) {
      u = Math.min(v.def.vitesse_max, (u + v.def.acceleration) * v.def.friction);
      d += u; n++;
    }
    return n;
  }

  /** Le milieu de la cour de la fourrière (`carte.fourriere`), ou null. */
  function centreDeLaCour() {
    const lot = Monde.carte && Monde.carte.fourriere;
    return lot ? { x: (lot.x + lot.largeur / 2) * TT, y: (lot.y + lot.hauteur / 2) * TT, nom: 'la fourrière' } : null;
  }

  /** Encore dans la ville ? ⚠️ `Entites.retirer` ne touche pas `actif` : c'est la liste qui le dit. */
  function present(v) { return B.entites.indexOf(v) >= 0; }

  function arrete(v) { return Math.abs(v.vitesse) < ARRET && Math.hypot(v.vx, v.vy) < ARRET * 2; }

  // --- Les épreuves ---------------------------------------------------------------------
  //
  // Chacune : `preparer(d, r, depart)` (au panneau, à pied) rend son état ou
  // null ; `partir(e, r, v)` (au volant) ; `maj(e, r, v)` rend `{ gagne, raison }`
  // quand c'est fini ; `compte`, `cible` (le GPS), `sol` (les marques peintes).

  const EPREUVES = {

    // LE FREIN PILE : on passe la ligne lancé, on s'arrête DANS la case.
    frein: {
      preparer: function (d, r, depart) {
        const p = pisteDroite(depart.x, depart.y, r.longueur, false);
        return p ? { piste: p, phase: 'approche', arret: 0 } : null;
      },
      maj: function (e, r, v) {
        const q = projeter(e.piste, v.x, v.y), vite = v.vitesse / v.def.vitesse_max;
        const case0 = r.case * TT - TT / 2, case1 = r.case * TT + TT / 2;
        if (e.phase === 'approche') {
          if (q.s < -TT) e.pret = true;
          if (e.pret && q.s >= 0 && q.s < TT && Math.abs(q.lat) < TT) {
            if (vite >= r.elan) { e.phase = 'lance'; Hud.message('FREINE !', 60); }
            else { e.pret = false; Hud.message('PAS ASSEZ LANCÉ — RECULE ET REPRENDS', 120); Son.SFX.erreur(); }
          }
          return null;
        }
        if (q.s > case1 + 4) return { gagne: false, raison: 'TROP LOIN' };
        if (!arrete(v)) { e.arret = 0; return null; }
        if (++e.arret < s(r.arret_s)) return null;
        if (q.s < case0) return { gagne: false, raison: 'TROP COURT' };
        if (Math.abs(q.lat) > TT * 0.75) return { gagne: false, raison: 'HORS DE LA CASE' };
        return { gagne: true };
      },
      compte: function (e) { return e.phase === 'approche' ? '— PASSE LA LIGNE LANCÉ' : '— ARRÊTE-TOI DANS LA CASE'; },
      cible: function (e, r) { return e.phase === 'approche' ? point(e.piste, -2 * TT, 0) : point(e.piste, r.case * TT, 0); },
      sol: function (ctx, e, r, vue) {
        ligne(ctx, e.piste, 0, vue, '#efe6d0');
        caseAuSol(ctx, e.piste, r.case * TT, 0, TT, TT * 1.5, vue, '#e8b33c');
      },
    },

    // LE DÉMARRAGE AU FEU : arrêté à la ligne, trois rouges, un vert au hasard.
    feu: {
      preparer: function (d, r, depart) {
        const p = pisteDroite(depart.x, depart.y, r.longueur, false);
        return p ? { piste: p, phase: 'approche', arret: 0, t: 0, vert: 0 } : null;
      },
      maj: function (e, r, v) {
        const q = projeter(e.piste, v.x, v.y);
        if (e.phase === 'approche') {
          const surLaLigne = q.s > -1.5 * TT && q.s < TT / 2 && Math.abs(q.lat) < TT;
          e.arret = surLaLigne && arrete(v) ? e.arret + 1 : 0;
          if (e.arret >= s(0.5)) {
            e.phase = 'rouge'; e.t = 0; e.depart = q.s;
            e.vert = s(r.rouges_s) * 3 + s(r.attente_s[0] + B.rng() * (r.attente_s[1] - r.attente_s[0]));
          }
          return null;
        }
        e.t++;
        if (e.phase === 'rouge') {
          if (e.t % s(r.rouges_s) === 1 && e.t < s(r.rouges_s) * 3) Son.SFX.menu();
          if (q.s - e.depart > 3 || v.vitesse > 0.15) return { gagne: false, raison: 'FAUX DÉPART' };
          if (e.t >= e.vert) { e.phase = 'vert'; e.t = 0; Son.SFX.etoile(); }
          return null;
        }
        if (!e.permis) e.permis = Math.round(tempsIdeal(v, r.arrivee * TT - e.depart) * (1 + r.marge)) + s(r.reflexe_s);
        if (q.s >= r.arrivee * TT) return e.t <= e.permis ? { gagne: true } : { gagne: false, raison: 'TROP LENT AU VERT' };
        if (e.t > e.permis) return { gagne: false, raison: 'TROP LENT AU VERT' };
        return null;
      },
      compte: function (e) {
        return e.phase === 'approche' ? '— ARRÊTE-TOI SUR LA LIGNE' : e.phase === 'rouge' ? '— ATTENDS LE VERT' : '— GO !';
      },
      cible: function (e, r) { return e.phase === 'approche' ? point(e.piste, 0, 0) : point(e.piste, r.arrivee * TT, 0); },
      sol: function (ctx, e, r, vue) { ligne(ctx, e.piste, 0, vue, '#efe6d0'); ligne(ctx, e.piste, r.arrivee * TT, vue, '#8fd46a'); },
      hud: function (ctx, e, r) {
        if (e.phase === 'approche') return;
        const x = VW / 2 - 24, y = 44, rouges = e.phase === 'rouge' ? Math.min(3, Math.floor(e.t / s(r.rouges_s)) + 1) : 0;
        ctx.fillStyle = 'rgba(11,10,18,0.84)'; ctx.fillRect(x - 4, y - 4, 56, 18);
        for (let k = 0; k < 3; k++) {
          ctx.fillStyle = e.phase === 'vert' ? '#8fd46a' : (k < rouges ? '#ff3b2f' : '#3a1a18');
          ctx.fillRect(x + k * 17, y, 12, 10);
        }
        B.stats.rects += 4;
      },
    },

    // LE CRÉNEAU : deux chars garés à la file dans la voie du bord, et la place
    // entre eux. On s'y gare, droit, sans toucher personne.
    creneau: {
      preparer: function (d, r, depart) {
        const p = pisteDroite(depart.x, depart.y, r.longueur, true);
        return p ? { piste: p, phase: 'approche', arret: 0, garees: [] } : null;
      },
      partir: function (e, r, v) {
        // ⚠️ LA PLACE SE MESURE AU CHAR QU'ON CONDUIT : on ne sait qu'au volant
        // si c'est une moto ou l'autobus.
        const lon = v.def.longueur, milieu = r.longueur * TT / 2, garee = Vehicules.vehiculeDef('auto').longueur;
        e.place = lon * r.place;
        e.milieu = milieu;
        const cap = Math.atan2(e.piste.dy, e.piste.dx);
        for (const cote of [-1, 1]) {
          const c = point(e.piste, milieu + cote * (e.place / 2 + garee / 2 + 2), 0);
          const g = poser('auto', c.x, c.y, cap);
          if (g) { e.garees.push(g); g.vieDepart = g.vie; }
        }
        e.chocs = v.chocs; e.lon = lon;
      },
      maj: function (e, r, v) {
        if (v.chocs !== e.chocs || e.garees.some(function (g) { return g.vie < g.vieDepart || !present(g); })) {
          return { gagne: false, raison: 'TU AS ACCROCHÉ' };
        }
        const q = projeter(e.piste, v.x, v.y);
        const dedans = Math.abs(q.s - e.milieu) <= (e.place - e.lon) / 2 + 3 && Math.abs(q.lat) <= 5
          && travers(e.piste, v.angle) <= r.angle_deg * Math.PI / 180;
        e.arret = dedans && arrete(v) ? e.arret + 1 : 0;
        return e.arret >= s(r.arret_s) ? { gagne: true } : null;
      },
      compte: function () { return '— GARE-TOI ENTRE LES DEUX'; },
      cible: function (e, r) { return point(e.piste, e.milieu || r.longueur * TT / 2, 0); },
      sol: function (ctx, e, r, vue) {
        if (e.place) caseAuSol(ctx, e.piste, e.milieu, 0, e.place, TT, vue, '#6fe3ff');
      },
    },

    // LE SLALOM : des cônes sur la ligne du milieu ; on passe à droite du
    // premier, à gauche du suivant… Un cône renversé coûte du temps.
    slalom: {
      preparer: function (d, r, depart) {
        const p = pisteDroite(depart.x, depart.y, r.depart + r.cones * r.pas + 3, false);
        if (!p) return null;
        const cones = [];
        for (let k = 0; k < r.cones; k++) cones.push({ s: (r.depart + k * r.pas) * TT, lat: -TT / 2, tombe: false, passe: false });
        return { piste: p, phase: 'approche', cones: cones, t: 0, penalites: 0 };
      },
      maj: function (e, r, v) {
        const q = projeter(e.piste, v.x, v.y), fin = (r.depart + r.cones * r.pas + 1) * TT;
        if (e.phase === 'approche') {
          if (q.s < -TT) e.pret = true;
          if (e.pret && q.s >= 0 && q.s < TT) { e.phase = 'slalom'; e.t = 0; Hud.message('GO !', 60); }
          return null;
        }
        e.t++;
        for (let k = 0; k < e.cones.length; k++) {
          const c = e.cones[k], pc = point(e.piste, c.s, c.lat);
          if (!c.tombe && Math.hypot(v.x - pc.x, v.y - pc.y) < v.r + CONE_R) {
            c.tombe = true; e.penalites++; Son.SFX.cone(); Hud.message('+' + r.penalite_s + ' S', 45);
          }
          if (!c.passe && q.s >= c.s) {
            c.passe = true;
            // ⚠️ Pair : à DROITE du cône (dans sa voie) ; impair : à GAUCHE.
            const bonCote = k % 2 === 0 ? q.lat > c.lat : q.lat < c.lat;
            if (!bonCote && !c.tombe) return { gagne: false, raison: 'CÔNE DU MAUVAIS CÔTÉ' };
          }
        }
        const total = e.t + e.penalites * s(r.penalite_s);
        if (q.s >= fin) return total <= s(r.temps_s) ? { gagne: true } : { gagne: false, raison: 'TROP LENT' };
        if (total > s(r.temps_s)) return { gagne: false, raison: 'TROP LENT' };
        return null;
      },
      compte: function (e, r) {
        if (e.phase === 'approche') return '— PASSE LA LIGNE';
        const total = e.t + e.penalites * s(r.penalite_s);
        return (total / 60).toFixed(1) + ' S / ' + r.temps_s + ' S · CÔNES ' + e.penalites;
      },
      cible: function (e, r) {
        if (e.phase === 'approche') return point(e.piste, -2 * TT, 0);
        return point(e.piste, (r.depart + r.cones * r.pas + 1) * TT, 0);
      },
      sol: function (ctx, e, r, vue) {
        ligne(ctx, e.piste, 0, vue, '#efe6d0');
        ligne(ctx, e.piste, (r.depart + r.cones * r.pas + 1) * TT, vue, '#8fd46a');
        for (let k = 0; k < e.cones.length; k++) {
          const c = e.cones[k], p = point(e.piste, c.s, c.lat), x = Math.round(p.x - vue.x), y = Math.round(p.y - vue.y);
          ctx.fillStyle = '#101018'; ctx.fillRect(x - 4, y + 1, 9, 3);
          ctx.fillStyle = '#e8741c';
          if (c.tombe) ctx.fillRect(x - 5, y - 1, 9, 3);
          else { ctx.fillRect(x - 3, y, 7, 3); ctx.fillRect(x - 2, y - 5, 5, 5); ctx.fillStyle = '#efe6d0'; ctx.fillRect(x - 2, y - 3, 5, 1); }
          // Le côté par où passer : une flèche peinte à côté du cône.
          if (!c.passe) chevronAuSol(ctx, e.piste, c.s, c.lat + (k % 2 === 0 ? TT / 2 : -TT / 2), vue);
        }
        B.stats.rects += e.cones.length * 3;
      },
    },

    // LE VERRE DE LAIT : une livraison, et un verre plein sur la banquette.
    lait: {
      preparer: function () { return { lait: 0 }; },
      partir: function (e, r, v) { e.chocs = v.chocs; },
      maj: function (e, r, v, d) {
        if (v.chocs !== e.chocs) return { gagne: false, raison: 'LE LAIT A REVOLÉ' };
        e.lait += aCoups(v, r) * r.debord;
        if (e.lait >= 1) return { gagne: false, raison: 'LE LAIT A DÉBORDÉ' };
        const l = Histoire.lieu(d.lieu);
        if (l && dist2(v.x, v.y, l.x, l.y) < (4 * TT) * (4 * TT) && arrete(v)) return { gagne: true };
        return null;
      },
      compte: function (e) { return '— LE VERRE ' + Math.round(e.lait * 100) + ' %'; },
      cible: function (e, r, d) { return Histoire.lieu(d.lieu); },
      hud: function (ctx, e) { jauge(ctx, e.lait, 'LE VERRE', '#efe6d0'); },
    },

    // LE REMORQUAGE : une remorqueuse devant la fourrière, une épave plus loin ;
    // on l'accroche et on la ramène, en douceur.
    remorquage: {
      aPied: true,
      preparer: function (d, r, depart) {
        // ⚠️ La fourrière est au fond d'une COUR qui ne touche aucune rue (le juge des
        // courses l'a appris) : la remorqueuse attend sur la rue la plus proche, plus loin.
        const route = Monde.routeLaPlusProche(depart.x, depart.y, 16);
        // L'épave : sur une rue à `epave_loin` tuiles de la COUR, pas du joueur —
        // c'est la route du retour qu'on mesure.
        const cour = centreDeLaCour() || depart;
        let loin = null;
        for (let k = 0; k < 16 && !loin; k++) {
          const a = k * Math.PI / 8;
          loin = Monde.routeLaPlusProche(cour.x + Math.cos(a) * r.epave_loin * TT, cour.y + Math.sin(a) * r.epave_loin * TT, 8);
        }
        if (!route || !loin) return null;
        const e = { secousses: 0 };
        e.remorqueuse = poser('remorqueuse', route.x, route.y, capDeLaVoie(route));
        e.epave = poser('auto', loin.x, loin.y, capDeLaVoie(loin));
        return e.remorqueuse && e.epave ? e : null;
      },
      partir: function (e, r, v) { e.chocs = v.chocs; },
      maj: function (e, r, v, d) {
        if (v.slug !== 'remorqueuse') return null;
        if (!present(e.epave)) return { gagne: false, raison: 'L\'ÉPAVE A DISPARU' };
        if (v.remorque !== e.epave) return null;
        e.secousses += aCoups(v, r) * r.debord;
        if (e.secousses >= 1) { Vehicules.decrocher(v); return { gagne: false, raison: 'L\'ÉPAVE A LÂCHÉ' }; }
        // ⚠️ AU LOT, ON LIVRE DANS LA COUR (`Missions.dansLaCour`), comme le boulot
        // de remorquage : la porte de la fourrière est au fond, loin de la grille.
        if (Missions.dansLaCour(v) && Math.abs(v.vitesse) < 0.4) return { gagne: true };
        return null;
      },
      compte: function (e, r, v) {
        if (!v || v.slug !== 'remorqueuse') return '— PRENDS LA REMORQUEUSE';
        if (v.remorque !== e.epave) return '— ACCROCHE L\'ÉPAVE (RECULE, KLAXON)';
        return '— À LA FOURRIÈRE · SECOUSSES ' + Math.round(e.secousses * 100) + ' %';
      },
      cible: function (e, r, d) {
        const v = B.joueur.dansVehicule;
        if (!v || v.slug !== 'remorqueuse') return e.remorqueuse;
        return v.remorque === e.epave ? (centreDeLaCour() || Histoire.lieu(d.lieu)) : e.epave;
      },
      hud: function (ctx, e) {
        const v = B.joueur.dansVehicule;
        if (v && v.remorque === e.epave) jauge(ctx, e.secousses, 'LA FOURCHE', '#e8b33c');
      },
    },
  };

  // --- Les marques au sol ---------------------------------------------------------------

  /** Une ligne peinte en travers de la voie, à `sl` pixels : un damier de deux
      rangées sur toute sa largeur. ⚠️ Plus fine, elle disparaissait sous le char
      arrêté dessus (capture) — et c'est là qu'on la cherche. */
  function ligne(ctx, p, sl, vue, couleur) {
    for (let u = 0; u < 2; u++) {
      for (let k = -4; k < 4; k++) {
        const a = point(p, sl - 3 + u * 3 + 1.5, k * 2 + 1);
        ctx.fillStyle = (k + u) % 2 ? couleur : '#101018';
        ctx.fillRect(Math.round(a.x - vue.x) - 1, Math.round(a.y - vue.y) - 1, 3, 3);
      }
    }
    B.stats.rects += 16;
  }

  /** Un cadre peint au sol : `long` dans le sens de la piste, `large` en travers. */
  function caseAuSol(ctx, p, sl, lat, long, large, vue, couleur) {
    ctx.fillStyle = couleur;
    for (let u = -long / 2; u <= long / 2; u += 2) {
      for (const w of [-large / 2, large / 2]) {
        const a = point(p, sl + u, lat + w);
        ctx.fillRect(Math.round(a.x - vue.x), Math.round(a.y - vue.y), 1, 1);
      }
    }
    for (let w = -large / 2; w <= large / 2; w += 2) {
      for (const u of [-long / 2, long / 2]) {
        const a = point(p, sl + u, lat + w);
        ctx.fillRect(Math.round(a.x - vue.x), Math.round(a.y - vue.y), 1, 1);
      }
    }
    B.stats.rects += 8;
  }

  /** Un petit chevron peint dans le sens de la piste. */
  function chevronAuSol(ctx, p, sl, lat, vue) {
    ctx.fillStyle = '#b8f1ff';
    for (let k = 0; k < 3; k++) {
      const a = point(p, sl - 2 + k, lat - 2 + k), b = point(p, sl - 2 + k, lat + 2 - k);
      ctx.fillRect(Math.round(a.x - vue.x), Math.round(a.y - vue.y), 1, 1);
      ctx.fillRect(Math.round(b.x - vue.x), Math.round(b.y - vue.y), 1, 1);
    }
  }

  /** Une jauge qui monte, en haut de l'écran, sous la ligne d'objectif. */
  function jauge(ctx, frac, nom, couleur) {
    const x = VW / 2 - 50, y = 44;
    ctx.fillStyle = 'rgba(11,10,18,0.84)'; ctx.fillRect(x - 4, y - 4, 108, 20);
    ctx.fillStyle = '#3a3a48'; ctx.fillRect(x, y + 6, 100, 5);
    ctx.fillStyle = frac > 0.7 ? '#ff5a4e' : couleur; ctx.fillRect(x, y + 6, Math.round(100 * Math.min(1, frac)), 5);
    Atlas.texte(ctx, nom, x, y - 2, '#cdc6e6', 1);
    B.stats.rects += 4;
  }

  // --- Le cycle -------------------------------------------------------------------------

  function defDe(slug) { return (B.defs.defis || []).find(function (q) { return q.slug === slug; }) || null; }

  /** Au panneau, à pied : trouve la piste et pose ce qui attend (la remorqueuse,
      l'épave). Rend faux s'il n'y a pas de place ici — le défi ne ment pas. */
  function commencer(d) {
    const sorte = EPREUVES[d.conduite];
    if (!sorte) return false;
    B.conduite = { slug: d.slug, sorte: d.conduite, poses: [], parti: false };
    const j = B.joueur;
    const e = sorte.preparer(d, d.regles, { x: j.x, y: j.y });
    if (!e) { fermer(); return false; }
    Object.assign(B.conduite, e);
    return true;
  }

  /** Au volant : le chrono part (`Histoire.partir`). */
  function partir(d, v) {
    const e = B.conduite;
    if (!e || e.slug !== d.slug || !v) return;
    e.parti = true;
    const sorte = EPREUVES[e.sorte];
    if (sorte.partir) sorte.partir(e, d.regles, v);
  }

  /** Une image au volant : `{ gagne, raison }` quand c'est fini. */
  function maj(d, v) {
    const e = B.conduite;
    if (!e || e.slug !== d.slug) return null;
    const sorte = EPREUVES[e.sorte];
    // ⚠️ Le remorquage se joue en DEUX chars : on descend du sien pour prendre la
    // remorqueuse. Les autres épreuves se ratent à pied.
    if (!v) return sorte.aPied ? null : { gagne: false, raison: 'PAS SANS CHAR' };
    return sorte.maj(e, d.regles, v, d);
  }

  /** Tout ce que l'épreuve a posé repart — sauf le char qu'on conduit. */
  function fermer() {
    const e = B.conduite;
    if (!e) return;
    const conduit = B.joueur && B.joueur.dansVehicule;
    for (const v of e.poses) {
      if (v.remorque) Vehicules.decrocher(v);
      if (v.remorqueePar) Vehicules.decrocher(v.remorqueePar);
      if (v === conduit || !present(v)) continue;
      Entites.retirer(v);
    }
    // Le char qu'on garde n'est plus « de mission » : la ville le traite comme les autres.
    if (conduit && e.poses.indexOf(conduit) >= 0) conduit.mission = false;
    B.conduite = null;
  }

  function compte(d) {
    const e = B.conduite;
    return e && e.slug === d.slug ? EPREUVES[e.sorte].compte(e, d.regles, B.joueur && B.joueur.dansVehicule) : '';
  }

  function cible(d) {
    const e = B.conduite;
    return e && e.slug === d.slug ? EPREUVES[e.sorte].cible(e, d.regles, d) : null;
  }

  /** Les marques de l'épreuve, sur la chaussée (sous les chars et les gens). */
  function dessinerSol(ctx, vue) {
    const e = B.conduite;
    if (!e || B.interieur) return;
    const d = defDe(e.slug), sorte = EPREUVES[e.sorte];
    if (d && sorte.sol) sorte.sol(ctx, e, d.regles, vue);
  }

  /** Ce que l'épreuve montre par-dessus la ville (le feu, la jauge). */
  function dessiner(ctx) {
    const e = B.conduite;
    if (!e || !e.parti) return;
    const d = defDe(e.slug), sorte = EPREUVES[e.sorte];
    if (d && sorte.hud) sorte.hud(ctx, e, d.regles);
  }

  return { commencer, partir, maj, fermer, compte, cible, dessinerSol, dessiner, pisteDroite, projeter, point, aCoups, tempsIdeal, EPREUVES };
})();
