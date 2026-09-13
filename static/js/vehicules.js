/* Bandini — vehicules : physique arcade, collisions par cercles, trafic.
   M0 : souche. Les fonctions pures ci-dessous servent deja aux tests. */

const Vehicules = (function () {
  'use strict';

  /** Facteur de braquage selon la vitesse relative (0 a l'arret, plein vers 0,3). */
  function courbeBraquage(t) {
    t = borner(Math.abs(t), 0, 1);
    if (t < 0.3) return t / 0.3;
    return 1 - (t - 0.3) * 0.65;
  }

  function vehiculeDef(slug) {
    return (B.defs.vehicules || []).find(function (v) { return v.slug === slug; }) || null;
  }

  function maj() { /* M3 */ }

  return { courbeBraquage, vehiculeDef, maj };
})();
