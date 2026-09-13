/* Bandini — missions, boulots, economie du joueur, sauvegarde de la partie.
   M0 : l'argent (gagner, payer, amende, pot-de-vin, hopital) et la sauvegarde. */

const Missions = (function () {
  'use strict';

  function encaisser(montant, raison) {
    montant = Math.max(0, Math.round(montant));
    B.partie.argent = Math.min(B.defs.economie.fortune_max, B.partie.argent + montant);
    if (montant > 0) { Son.SFX.argent(); if (typeof Hud !== 'undefined') Hud.message('+' + montant + ' $' + (raison ? ' ' + raison : '')); }
    return montant;
  }

  function payer(montant, raison) {
    montant = Math.max(0, Math.round(montant));
    if (B.partie.argent < montant) return false;
    B.partie.argent -= montant;
    if (typeof Hud !== 'undefined') Hud.message('-' + montant + ' $' + (raison ? ' ' + raison : ''));
    return true;
  }

  /** Indexe la table servie par le serveur : amendes[etoiles-1][casier]. */
  function amende(argent, etoiles, casier) {
    const eco = B.defs.economie;
    const e = borner(etoiles, 1, eco.amendes.length);
    const c = borner(casier, 0, eco.casier_max);
    return Math.max(0, Math.min(argent, eco.amendes[e - 1][c]));
  }

  function potDeVin(etoiles, casier) {
    const eco = B.defs.economie;
    return eco.pots_de_vin[borner(etoiles, 1, 5) - 1][borner(casier, 0, eco.casier_max)];
  }

  function factureHopital(argent) {
    const h = B.defs.economie.hopital;
    const m = Math.round(argent * h.fraction);
    return Math.max(0, Math.min(argent, Math.max(h.minimum, Math.min(h.maximum, m))));
  }

  // --- Les commerces de trottoir ---------------------------------------------------

  function commerceDe(slug) {
    return (B.defs.ambulants || []).find(function (c) { return c.slug === slug; }) || null;
  }

  /** Un kiosque a ses heures : un marchand de journaux ferme la nuit. */
  function ouvert(commerce) {
    if (!commerce || !commerce.heures) return true;
    const h = B.partie.heure;
    const debut = commerce.heures[0], fin = commerce.heures[1];
    return debut < fin ? (h >= debut && h < fin) : (h >= debut || h < fin);
  }

  function soigner(j, pv) {
    if (!pv) return;
    j.vie = Math.min(j.vieMax, j.vie + pv);
    B.partie.vie = j.vie;
  }

  /** Acheter au kiosque ou au camion : de la vie contre de l'argent. */
  function acheterAmbulant(j, etal) {
    const commerce = commerceDe(etal.slug);
    if (!commerce) return false;
    if (!ouvert(commerce)) { Hud.message('FERME'); Son.SFX.erreur(); return true; }
    const prix = B.defs.economie.tarifs[commerce.tarif];
    if (B.partie.argent < prix) { Hud.message(prix + ' $ — PAS ASSEZ'); Son.SFX.erreur(); return true; }
    payer(prix, commerce.nom.toUpperCase());
    soigner(j, commerce.gain_pv ? B.defs.economie.tarifs[commerce.gain_pv] : 0);
    Son.SFX.argent();
    if (commerce.service === 'journal') Hud.message('LE CLAIRON DE LA BAIE');
    return true;
  }

  /** La compagnie d'une fille de la Brume : ca se paie, et ca ne se montre pas. */
  function compagnie(j, fille) {
    const prix = B.defs.economie.tarifs.compagnie;
    if (B.recherche.etoiles > 0) { Hud.message('PAS AVEC LA POLICE AUX FESSES'); return true; }
    if (B.partie.argent < prix) { Hud.message(prix + ' $ — PAS ASSEZ'); Son.SFX.erreur(); return true; }
    payer(prix, 'LA BRUME');
    soigner(j, B.defs.economie.tarifs.compagnie_pv);
    fille.minuterie = 900;
    Hud.fondu(90, 'ON REPREND SON SOUFFLE');
    return true;
  }

  /** Ce qu'on peut faire la ou l'on est (bouton ACTION). */
  function interagir(j) {
    const etal = Entites.autour(j.x, j.y, 30, function (e) { return e.type === 'ambulant'; })[0];
    if (etal) return acheterAmbulant(j, etal);
    const fille = Entites.pietonsAutour(j.x, j.y, 26).find(function (e) {
      return e.metier === 'compagnie' && e.vivant && e.etat !== 'fuit';
    });
    if (fille) return compagnie(j, fille);
    return false;
  }

  function nouveauJour() {
    if (typeof Hud !== 'undefined') Hud.message('JOUR ' + B.partie.jour);
  }

  function sauvegarderPartie() {
    const p = B.partie, j = B.joueur;
    if (j) { p.x = Math.round(j.x); p.y = Math.round(j.y); p.vie = j.vie; p.arme = j.arme; }
    p.empreinte = B.defs.empreinte;
    return Sauvegarde.ecrire(p);
  }

  function maj() {
    if (B.t % 600 === 0 && B.etat === 'jeu') sauvegarderPartie();
    if (B.t % 60 === 0) B.partie.stats.secondes++;
  }

  return { encaisser, payer, amende, potDeVin, factureHopital, nouveauJour, sauvegarderPartie,
           commerceDe, ouvert, acheterAmbulant, compagnie, interagir, soigner, maj };
})();
