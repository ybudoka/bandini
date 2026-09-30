/* Bandini — la suite du paquet (docs/jalons/le-paquet-des-definitions-maigrit.md, la deuxième cure).

   Ce que le navigateur ne lit jamais avant d'avoir quitté l'écran titre voyage À PART, sur `/api/suite`
   (`definitions.DANS_LA_SUITE` : le Clairon, les Galeries hantées). Demandé juste APRÈS les définitions,
   en arrière-plan (`Jeu.demarrer`), comme les notes de la musique ; gardé par la coquille du travailleur :
   hors ligne, il est là. À son arrivée, chaque clé revient dans `B.defs` sous son nom — aucun lecteur ne
   sait d'où elle vient.

   ⚠️ UN TEXTE N'A PAS DE REPLI. Ce qui s'en sert l'ATTEND (`quand`) : la manchette d'un jour qui se lève
   avant la suite paraît à son arrivée, au lieu de se perdre. Ou se tait sans lui (`B.defs.x || …`) —
   jamais une exception dans `maj()` (elle figerait l'écran sans un mot).

   ⚠️ Une demande ratée se refait, au plus une fois par `REESSAI_IMAGES` (`maj`, chaque image) : un réseau
   coupé ne se martèle pas. Une suite d'une AUTRE construction (un déploiement tombé entre les deux
   requêtes) ne se pose pas, et ne se redemande pas — la même adresse rendrait la même chose. */

const Suite = (function () {
  'use strict';

  //: Une demande ratée se refait, au plus une fois par tant d'images (dix secondes).
  const REESSAI_IMAGES = 600;
  //: La demande : null | 'en cours' | 'arrivee' | 'ratee' | 'etrangere'.
  const demande = { etat: null, url: null, empreinte: null, essaiT: 0 };
  //: Ce qui attend la suite (`quand`), dans l'ordre.
  let enAttente = [];
  //: La fenêtre du navigateur (le banc en pose une fausse) : c'est elle qui a `fetch`.
  let fenetre = null;

  /** Va chercher la suite. `empreinte` : celle que les définitions nomment (`suite_empreinte`). */
  function charger(w, url, empreinte) {
    fenetre = w || null;
    demande.url = url || null; demande.empreinte = empreinte || null;
    tenter();
  }

  function tenter() {
    if (!demande.url || demande.etat === 'en cours' || demande.etat === 'arrivee' || demande.etat === 'etrangere') return;
    if (!fenetre || !fenetre.fetch) return;
    demande.etat = 'en cours';
    demande.essaiT = B.t || 0;
    fenetre.fetch(demande.url)
      .then(function (r) { if (!r.ok) throw new Error('suite ' + r.status); return r.json(); })
      .then(function (p) {
        if (!p || (demande.empreinte && p.empreinte !== demande.empreinte)) { demande.etat = 'etrangere'; return; }
        poser(p);
      })
      .catch(function () { if (demande.etat === 'en cours') demande.etat = 'ratee'; });
  }

  /** Remet chaque clé dans `B.defs`, puis réveille ce qui l'attendait. */
  function poser(p) {
    if (!B.defs) return;
    for (const cle in p) if (cle !== 'empreinte') B.defs[cle] = p[cle];
    demande.etat = 'arrivee';
    const attente = enAttente;
    enAttente = [];
    // ⚠️ Chacun dans son `try` : une attente qui lève ne doit pas priver les suivantes (ni figer la promesse).
    attente.forEach(function (fn) {
      try { fn(); } catch (e) { if (typeof console !== 'undefined' && console.error) console.error(e); }
    });
  }

  function arrivee() { return demande.etat === 'arrivee'; }

  /** `fn` tout de suite si la suite est là ; sinon à son arrivée. */
  function quand(fn) {
    if (arrivee()) { fn(); return true; }
    enAttente.push(fn);
    reclamer();
    return false;
  }

  /** Une demande ratée se refait, sans marteler un réseau coupé. */
  function reclamer() {
    if (demande.etat === 'ratee' && (B.t || 0) - demande.essaiT >= REESSAI_IMAGES) { demande.etat = null; tenter(); }
  }

  /** Une image : la seule chose à faire, c'est redemander ce qui a raté. */
  function maj() { reclamer(); }

  function etat() { return demande.etat; }
  function attentes() { return enAttente.length; }

  return { charger, poser, arrivee, quand, reclamer, maj, etat, attentes, REESSAI_IMAGES };
})();
