/* Bandini — le tour de l'île : les bouées de course sur la baie, et le rival qui les court (M16, vague 17, i07).
   Python pose le parcours (`app/regate.py`, `carte.regate.bouees` : six bouées autour de l'Île-aux-Corneilles) ; ici,
   on les PEINT (elles ne sont ni des tuiles ni du décor : rien ne naît, aucun identifiant ne bouge), on les nomme pour
   `course` (`bouee:<n>`, `Histoire.resoudre`), et on mène le RIVAL d'une course `contre` quelqu'un.

   ⚠️ Le rival n'a pas de dé : il vise la bouée suivante en ligne droite (le parcours est de l'eau libre d'une bouée à
   l'autre, `regate.py` le garantit), à l'`allure` que la fiche lui donne — un pilote honnête, qu'un joueur appliqué
   bat. Il part après le décompte (`DECOMPTE`), comme toi. Calé contre une rive, il recule une seconde (comme la vedette
   de police). */

const Regate = (function () {
  'use strict';

  //: Le départ : « À VOS MARQUES » — trois secondes avant que le rival ne mette les gaz.
  const DECOMPTE = 180;
  //: Calé : du gaz sans erre depuis tant d'images ; il recule alors tant d'images, la barre à l'opposé.
  const CALE_IMAGES = 50, RECUL_IMAGES = 40;
  const AU_REPOS = Object.freeze({ gaz: 0, frein: 0, direction: 0, freinMain: false });

  function parcours() {
    const c = B.defs && B.defs.carte;
    return c && c.regate && c.regate.bouees ? c.regate.bouees : null;
  }

  /** La bouée `n` du tour, en pixels — `bouee:<n>` pour `Histoire.resoudre`. Null sans parcours. */
  function point(n) {
    const b = parcours(), q = b && b[Number(n)];
    return q ? { x: q[0] * TT + 8, y: q[1] * TT + 8, nom: 'la bouée ' + (Number(n) + 1) } : null;
  }

  // --- Le rival --------------------------------------------------------------------------------------------

  /** Le rival d'une course (`contre: { qui, vehicule, allure }`) : sa coque à côté de la tienne, du côté où il y a de
      l'eau, le même cap ; il court les MÊMES points que toi. */
  function creerRival(m, o, points) {
    const j = B.joueur, moi = j.dansVehicule || j, c = o.contre || {};
    const cap = moi.angle || 0, nx = -Math.sin(cap), ny = Math.cos(cap);
    let place = null;
    for (const cote of [1, -1]) for (const d of [30, 44]) {
      const x = moi.x + nx * d * cote, y = moi.y + ny * d * cote;
      if (!place && Monde.estEau(Math.floor(x / TT), Math.floor(y / TT))) place = { x: x, y: y };
    }
    if (!place) place = { x: moi.x + nx * 30, y: moi.y + ny * 30 };
    const v = Vehicules.creer(c.vehicule || 'bateau', place.x, place.y, cap, { conducteur: 'regate', etat: 'roule', mission: m.slug });
    if (!v) return null;
    const qui = c.qui ? Histoire.personnage(c.qui) : null;
    if (qui) v.pilote = { swaps: qui.couleurs };
    v.regate = { i: 0, points: points.slice(), depart: B.t + DECOMPTE, allure: c.allure || 0.85, rayon: (o.rayon || 3) * TT, qui: c.qui || null };
    return v;
  }

  /** Les commandes du rival : la bouée suivante, droit dessus. Arrivé au bout, il se laisse dériver. */
  function commandes(v) {
    const r = v.regate;
    // Battu (`battu` : tu as fini avant lui), il lève les gaz et dérive.
    if (!r || r.battu || B.t < r.depart || r.i >= r.points.length) return AU_REPOS;
    const cible = r.points[r.i];
    if (Math.hypot(cible.x - v.x, cible.y - v.y) < r.rayon) { r.i++; return AU_REPOS; }
    if (v.reculT > 0) { v.reculT--; return { gaz: 0, frein: 1, direction: -(v.barreRecul || 1), freinMain: false }; }
    const ecart = ecartAngle(v.angle, angleVers(v.x, v.y, cible.x, cible.y));
    const direction = borner(ecart * 2.2, -1, 1);
    // ⚠️ L'ALLURE EST UNE VITESSE, PAS UN GAZ : à 0,82 de gaz, la coque finit quand même à sa vitesse de pointe (3,2 px
    // par image, mesuré) — le rival faisait le tour en trente secondes, plus vite qu'aucun joueur. Au-dessus de
    // `allure` × sa pointe, il lâche les gaz.
    const pointe = (v.def && v.def.vitesse_max) || 3;
    const gaz = Math.abs(v.vitesse) > r.allure * pointe ? 0 : Math.abs(ecart) < 1.2 ? 1 : 0.35;
    if (Math.abs(v.vitesse) < 0.2) v.coinceT = (v.coinceT || 0) + 1; else v.coinceT = 0;
    if (v.coinceT > CALE_IMAGES) { v.coinceT = 0; v.reculT = RECUL_IMAGES; v.barreRecul = direction >= 0 ? 1 : -1; }
    return { gaz: gaz, frein: 0, direction: direction, freinMain: false };
  }

  /** Le rival a-t-il passé sa dernière bouée ? */
  function arrive(v) { return !!(v && v.regate && v.regate.i >= v.regate.points.length); }

  // --- Le dessin --------------------------------------------------------------------------------------------

  /** Les bouées sur l'eau : une bouée de course orange à bande blanche, son fanion, qui danse avec la houle. La
      prochaine d'une course en cours a son halo et son numéro ; celles déjà passées pâlissent. */
  function dessiner(ctx, vue) {
    const b = parcours();
    if (!b || B.interieur || B.bloc) return;
    const course = B.mission && B.mission.course, vise = course && course.points[course.i];
    for (let n = 0; n < b.length; n++) {
      const x = Math.round(b[n][0] * TT + 8 - vue.x), y = Math.round(b[n][1] * TT + 8 - vue.y);
      const houle = Math.round(Math.sin((B.t + n * 37) / 24) * 1.5);
      const prochaine = vise && Math.abs(vise.x - (b[n][0] * TT + 8)) < 1 && Math.abs(vise.y - (b[n][1] * TT + 8)) < 1;
      if (prochaine) {
        ctx.fillStyle = (B.t >> 4) % 2 ? 'rgba(255,220,80,0.35)' : 'rgba(255,220,80,0.2)';
        ctx.beginPath(); ctx.arc(x, y + houle, 15, 0, Math.PI * 2); ctx.fill();
      }
      ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillRect(x - 6, y + 4 + houle, 12, 1);      // le remous
      ctx.fillStyle = '#e8641e'; ctx.fillRect(x - 4, y - 3 + houle, 8, 7);                      // la coque de la bouée
      ctx.fillStyle = '#f4f0e6'; ctx.fillRect(x - 4, y + houle, 8, 2);                          // sa bande blanche
      ctx.fillStyle = '#3a3a3a'; ctx.fillRect(x, y - 11 + houle, 1, 8);                         // le mât
      ctx.fillStyle = prochaine ? '#ffd84a' : '#d8342c'; ctx.fillRect(x + 1, y - 11 + houle, 5, 3);   // le fanion
      if (prochaine) {
        ctx.fillStyle = '#1a1a22'; ctx.font = '8px monospace'; ctx.textAlign = 'center';
        ctx.fillText(String(n + 1), x, y - 14 + houle);
      }
    }
  }

  return { DECOMPTE, parcours, point, creerRival, commandes, arrive, dessiner };
})();
