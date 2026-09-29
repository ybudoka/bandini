/* Bandini — les 4 roues garés (docs/jalons/les-4-roues.md, vague 1) : trois dans les Friches, a cote des
   cabanons (`carte.quatre_roues`, `app/quatre_roues.py`), et le tien au chalet du rang (`bloc.quatre_roues`).

   ⚠️ ILS NAISSENT A L'APPROCHE, comme les motoneiges : rien au demarrage (la bande est dans la bulle de
   naissance du terminus, et un vehicule de plus y deplacerait le hasard du depart). Quand on passe a moins de
   `PORTEE` d'une place vide et qu'elle est hors de l'ecran, un 4 roues y nait — hors de la suite des numeros,
   de couleur DONNEE (aucun de). Oublie loin du joueur (`Vehicules.peupler`), il renait a sa place. */

const QuatreRoues = (function () {
  'use strict';

  //: Tous les combien d'images on regarde, et a quelle distance d'une place un 4 roues y nait.
  const PAS = 60, PORTEE = 500;

  /** Les places ou un 4 roues attend, ici : celles du bloc (le chalet) ou celles de la ville (les Friches).
      ⚠️ Dans un bloc, `Monde.carte` EST le bloc. */
  function places() {
    const def = Monde.carte && Monde.carte.def;
    if (!def) return [];
    if (B.bloc) {
      const q = def.bloc && def.bloc.quatre_roues;
      return q ? [{ x: q.x, y: q.y, cle: 'bloc:' + B.bloc.slug, aToi: true }] : [];
    }
    return (def.quatre_roues || []).map(function (q, k) { return { x: q.x, y: q.y, cle: 'friches:' + k, aToi: false }; });
  }

  function la(cle) {
    return B.entites.find(function (e) { return e.type === 'vehicule' && e.placeQuad === cle && e.vivant !== false; }) || null;
  }

  function maj() {
    if (B.interieur || (B.t || 0) % PAS !== 23) return;
    const j = B.joueur, def = Vehicules.vehiculeDef('quatre_roues');
    if (!j || !def) return;
    places().forEach(function (q, k) {
      const x = q.x * TT + 8, y = q.y * TT + 8;
      if (Math.hypot(j.x - x, j.y - y) > PORTEE || la(q.cle) || Entites.visibleAEcran(x, y, 24)) return;
      const couleur = def.couleurs[(q.x + q.y + k) % def.couleurs.length];
      Entites.enDehorsDeLaSuite(function () {
        Vehicules.creer('quatre_roues', x, y, -Math.PI / 2,
                        { etat: 'stationne', couleur: couleur, resteGare: true, placeQuad: q.cle, aToi: q.aToi });
      });
    });
  }

  return { places, maj, la };
})();
