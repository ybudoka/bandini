/* Bandini — installable, et jouable hors ligne : le cote page.

   Demande de Martin : « est-ce compliqué de faire du jeu une webapp
   installable ? », puis « jouable hors ligne ».

   Il inscrit le travailleur (`static/js/travailleur.js`, servi a la racine) et
   tient ce qu'il en sait pour la ligne LES SONS HORS LIGNE des OPTIONS. Le jeu,
   lui, ne sait pas qu'il existe : la ville qu'il charge vient du reseau ou du
   cache, et c'est la meme.

   ⚠️ Ce n'est pas lui qui rend le jeu INSTALLABLE : mesure le 17 sept. 2026,
   Chromium le dit installable avec ou sans travailleur (le critere du
   gestionnaire `fetch` est tombe) — le manifeste et les icones suffisent. Le
   travailleur, c'est le HORS LIGNE.
   ⚠️ Rien sans contexte securise : en http sur le reseau local (le telephone
   de Martin sur `192.168.x.x:5400`), `navigator.serviceWorker` n'existe pas, et
   le jeu se joue comme avant.
   ⚠️ Aucun acces qui ne soit pas garde : le banc d'essai (tests/banc.js) charge
   ce fichier sous Node, sans travailleur. */

const HorsLigne = (function () {
  'use strict';

  let fenetre = null, conteneur = null;
  //: Le dernier etat annonce par le travailleur : { sons, total, octets, octets_total, en_cours }.
  let etat = null;

  function init(w, d) {
    fenetre = w;
    const nav = w && w.navigator;
    const racine = d && d.getElementById && d.getElementById('bandini');
    if (!nav || !nav.serviceWorker || !racine || !racine.dataset.urlTravailleur) return;
    conteneur = nav.serviceWorker;
    conteneur.addEventListener('message', function (ev) {
      if (ev.data && ev.data.type === 'hors-ligne') etat = ev.data;
    });
    // ⚠️ Apres `load` : le travailleur remplit son cache en s'installant, et il
    // n'a pas a disputer la bande passante aux scripts et a la ville.
    function inscrire() {
      conteneur.register(racine.dataset.urlTravailleur)
        .then(function () { demander({ type: 'etat' }); })
        .catch(function () { conteneur = null; });
    }
    if (d.readyState === 'complete') inscrire();
    else w.addEventListener('load', inscrire);
  }

  function demander(message) {
    if (!conteneur) return;
    conteneur.ready.then(function (inscription) {
      if (inscription.active) inscription.active.postMessage(message);
    });
  }

  /** Tous les sons dans le cache, d'un coup — le bouton des OPTIONS.

      ⚠️ On demande aussi au navigateur de NE PAS les effacer quand il manque de
      place : 14 Mo telecharges expres ne doivent pas disparaitre en silence. */
  function toutTelecharger() {
    if (!conteneur) return false;
    const stockage = fenetre.navigator.storage;
    if (stockage && stockage.persist) stockage.persist().catch(function () {});
    if (etat) etat = Object.assign({}, etat, { en_cours: true });
    demander({ type: 'tout-telecharger' });
    return true;
  }

  /** Ce que dit la ligne des OPTIONS : ce qu'il reste a telecharger, ou ou on en est. */
  function detail() {
    if (!conteneur) return 'INDISPONIBLE';
    if (!etat) return '…';
    if (etat.total && etat.sons >= etat.total) return 'OUI';
    if (etat.en_cours) return Math.floor(100 * etat.octets / Math.max(1, etat.octets_total)) + ' %';
    return Math.max(1, Math.round((etat.octets_total - etat.octets) / 1e6)) + ' MO';
  }

  if (typeof window !== 'undefined' && typeof document !== 'undefined') init(window, document);

  return { init, toutTelecharger, detail,
    get disponible() { return !!conteneur; },
    get etat() { return etat; },
    demanderEtat: function () { demander({ type: 'etat' }); } };
})();
