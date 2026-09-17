/* Bandini — la barre de chargement, AVANT le jeu.

   Demande de Martin (17 sept. 2026) : « je prendrais bien une barre de
   chargement au lancement du jeu ».

   ⚠️ Les scripts du jeu sont la plus grosse part de l'attente sur un téléphone
   — mesuré le 17 sept. 2026, Fast 3G et processeur ×4 : sept secondes sur
   presque onze avant l'écran titre — et le jeu ne peut pas les compter : il
   n'existe pas encore. Ce fichier-ci est chargé EN PREMIER, il compte les
   scripts à mesure qu'ils arrivent, et `jeu.js` reprend la barre là où il
   l'a laissée (les définitions et la carte, à l'octet près, puis la ville).

   ⚠️ Un fichier et pas un script dans la page : la configuration de sécurité
   du serveur peut refuser les scripts en ligne, et une barre bloquée à zéro
   ment plus qu'une absence de barre.

   ⚠️ Aucun accès au DOM qui ne soit pas gardé : le banc d'essai (tests/banc.js)
   charge ce fichier sous Node, avec un faux document. */

(function () {
  'use strict';
  if (typeof document === 'undefined' || !document.addEventListener) return;
  let recus = 0;
  document.addEventListener('load', function (ev) {
    const cible = ev && ev.target;
    if (!cible || cible.tagName !== 'SCRIPT' || String(cible.src || '').indexOf('/js/') < 0) return;
    const barre = document.getElementById('chargement');
    const plein = document.getElementById('chargement-plein');
    const racine = document.getElementById('bandini');
    if (!barre || !plein || !racine) return;
    recus++;
    // Le nombre de scripts vient de la page (`data-scripts`) ; la part de la
    // barre qui leur revient, de la barre (`data-part-scripts`) — jeu.js lit
    // la même, et continue au-dessus.
    const total = Math.max(1, Number(racine.dataset.scripts) || 1);
    const part = Number(barre.dataset.partScripts) || 60;
    const valeur = Math.round(Math.min(1, recus / total) * part);
    if (valeur <= (Number(barre.getAttribute('aria-valuenow')) || 0)) return;
    barre.setAttribute('aria-valuenow', String(valeur));
    plein.style.width = valeur + '%';
  }, true);
})();
