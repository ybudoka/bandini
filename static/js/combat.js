/* Bandini — combat : armes, melee, projectiles. M0 : le coup de poing existe
   (animation et son), il n'y a encore personne a frapper. */

const Combat = (function () {
  'use strict';

  function armeDef(slug) {
    return (B.defs.armes || []).find(function (a) { return a.slug === slug; }) || null;
  }

  function armeCourante() { return armeDef(B.joueur ? B.joueur.arme : 'poings') || armeDef('poings'); }

  function frapper(e) {
    const arme = armeDef(e.arme || 'poings');
    if (!arme || e.etat === 'attaque') return false;
    e.etat = 'attaque';
    e.t = 0;
    e.coupT = arme.anticipation + arme.actif + 6;
    e.flagrant = 120;
    Son.SFX.coup();
    return true;
  }

  function cycler(e) {
    const ordre = B.defs.ordre_armes || ['poings'];
    const possedees = ordre.filter(function (s) { return B.partie.armes[s]; });
    if (possedees.length < 2) return;
    const i = possedees.indexOf(e.arme);
    e.arme = possedees[(i + 1) % possedees.length];
    B.partie.arme = e.arme;
    Son.SFX.menu();
  }

  function maj() {
    const j = B.joueur;
    if (!j || j.dansVehicule) return;
    if (j.etat === 'attaque') {
      if (--j.coupT <= 0) j.etat = 'flane';
    } else if (Entree.neuf('attaque')) {
      frapper(j);
    }
    if (Entree.neuf('arme')) cycler(j);
  }

  return { armeDef, armeCourante, frapper, cycler, maj };
})();
