/* Bandini — police : crimes, cones de vision, niveau de recherche.
   M0 : la machine de recherche (chaleur, etoiles, decroissance) et le test de
   cone, sans policiers dans la rue. */

const Police = (function () {
  'use strict';

  /** L'agent en (ax, ay) regardant vers `angle` voit-il (x, y) ? Cone + portee ; la ligne de vue est a part. */
  function dansLeCone(ax, ay, angle, demiAngleRad, portee, x, y) {
    const d2 = dist2(ax, ay, x, y);
    if (d2 > portee * portee) return false;
    if (d2 < 1) return true;
    return Math.abs(ecartAngle(angle, angleVers(ax, ay, x, y))) <= demiAngleRad;
  }

  function voit(agent, x, y, genre) {
    const vision = B.defs.recherche.vision[genre || 'policier'];
    const nuit = Monde.estNuit();
    const portee = (nuit ? vision.nuit : vision.jour) * TT;
    if (!dansLeCone(agent.x, agent.y, agent.angle, vision.angle * Math.PI / 180, portee, x, y)) return false;
    return Monde.ligneLibre(agent.x, agent.y, x, y);
  }

  function ajouterChaleur(gravite) {
    const r = B.recherche, defs = B.defs.recherche;
    r.chaleur += gravite * defs.chaleur_par_gravite;
    while (r.chaleur >= defs.chaleur_etoile && r.etoiles < defs.etoiles_max) {
      r.chaleur -= defs.chaleur_etoile;
      r.etoiles++;
      r.vu = 0;
      Son.SFX.etoile();
    }
    if (r.etoiles >= defs.etoiles_max) r.chaleur = 0;
  }

  /** Un crime commis. `vu` force la detection (M0 : aucun policier, on l'utilise pour les tests). */
  function signalerCrime(type, x, y, vu) {
    const delit = B.defs.recherche.delits[type];
    if (!delit) return null;
    const crime = { type: type, gravite: delit.etoiles, temoin: delit.temoin, x: x, y: y, t: B.t, vu: !!vu };
    B.crimes.push(crime);
    if (B.crimes.length > 40) B.crimes.shift();
    B.partie.stats.crimes++;
    if (vu) ajouterChaleur(delit.etoiles);
    return crime;
  }

  function remiseAZero() { const r = B.recherche; r.etoiles = 0; r.chaleur = 0; r.vu = 0; }

  function maj() {
    const r = B.recherche;
    if (r.etoiles <= 0) return;
    r.vu++;
    const palier = B.defs.recherche.paliers[r.etoiles];
    if (r.vu > palier.decroissance_s * 60) { r.etoiles--; r.vu = 0; }
  }

  return { dansLeCone, voit, ajouterChaleur, signalerCrime, remiseAZero, maj };
})();
