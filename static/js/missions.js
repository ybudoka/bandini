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

  // --- L'hopital : on ne meurt pas, on paie ------------------------------------------

  /** Le joueur tombe : fondu, reveil a l'hopital, facture, armes gardees. */
  function hopital(source) {
    const j = B.joueur;
    if (!j || j.hospitalise) return;
    j.hospitalise = true;
    if (j.dansVehicule) Vehicules.descendre(j, true);
    j.vie = 1; j.vx = 0; j.vy = 0; j.roule = 0; j.etat = 'flane';
    const facture = factureHopital(B.partie.argent);
    payer(facture, 'HOPITAL');
    B.partie.stats.hospitalisations = (B.partie.stats.hospitalisations || 0) + 1;
    Hud.fondu(150, 'REVEIL A L’HOPITAL — ' + facture + ' $');
    Police.remiseAZero();
    if (taxi.etape) taxi.abandonner();
    const lieu = Monde.carte.points.find(function (p) { return p.slug === 'hopital'; });
    setTimeoutJeu(60, function () {
      if (lieu) { j.x = lieu.x * TT + 8; j.y = lieu.y * TT + 20; }
      j.vie = j.vieMax; j.invincible = 90; j.saigne = 0; j.endurance = 100;
      Entites.dansLaCarte(j);
      Monde.centrerCamera(j.x, j.y);
      j.hospitalise = false;
    });
  }

  //: Des minuteries en images de jeu (pas setTimeout : le banc n'a pas d'horloge).
  const minuteries = [];
  function setTimeoutJeu(images, fn) { minuteries.push({ t: images, fn: fn }); }
  function majMinuteries() {
    for (let i = minuteries.length - 1; i >= 0; i--) {
      if (--minuteries[i].t <= 0) { const m = minuteries.splice(i, 1)[0]; m.fn(); }
    }
  }

  // --- Le taxi : un client, une destination, un pourboire selon la douceur ----------

  const taxi = {
    etape: null,           // null | 'attente' | 'course'
    client: null, destination: null, distance: 0, chocsDepart: 0, t: 0, courses: 0,

    /** Le klaxon dans un taxi : on prend un client, ou on n'a rien a faire. */
    klaxon: function (v) {
      if (v.slug !== 'taxi' || taxi.etape) return false;
      const place = Entites.placeDeNaissance();
      const arch = Entites.archetypeDeRue();
      const x = place ? place.x : v.x + Math.cos(v.angle) * 80, y = place ? place.y : v.y + Math.sin(v.angle) * 80;
      const client = Entites.creerPieton(x, y, arch);
      client.etat = 'fige'; client.cri = 9999; client.client = true;
      taxi.client = client; taxi.etape = 'attente'; taxi.t = 0;
      Hud.message('UN CLIENT ATTEND');
      return true;
    },

    maj: function () {
      if (!taxi.etape) return;
      const j = B.joueur, v = j.dansVehicule;
      taxi.t++;
      if (!v || v.slug !== 'taxi' || v.etat === 'epave') { taxi.abandonner('COURSE PERDUE'); return; }
      if (taxi.etape === 'attente') {
        const c = taxi.client;
        if (!c || !c.vivant) { taxi.abandonner('CLIENT PERDU'); return; }
        if (dist2(v.x, v.y, c.x, c.y) < 40 * 40 && Math.abs(v.vitesse) < 0.4) {
          Entites.retirer(c);
          taxi.client = null;
          const lieux = Monde.carte.points.filter(function (p) { return dist2(p.x * TT, p.y * TT, v.x, v.y) > 200 * 200; });
          const lieu = lieux[Math.floor(B.rng() * lieux.length)] || Monde.carte.points[0];
          taxi.destination = { x: lieu.x * TT + 8, y: lieu.y * TT + 8, nom: lieu.nom };
          taxi.distance = Math.hypot(taxi.destination.x - v.x, taxi.destination.y - v.y);
          taxi.chocsDepart = v.chocs;
          taxi.etape = 'course';
          Hud.message('DIRECTION : ' + lieu.nom.toUpperCase(), 180);
          Son.SFX.porte();
        }
        return;
      }
      const d = taxi.destination;
      if (dist2(v.x, v.y, d.x, d.y) < 44 * 44 && Math.abs(v.vitesse) < 0.4) {
        const tarifs = B.defs.economie.tarifs;
        const chocs = v.chocs - taxi.chocsDepart;
        const douceur = Math.max(0, 1 - chocs * 0.34);
        const prix = Math.round(tarifs.taxi_base + tarifs.taxi_par_tuile * (taxi.distance / TT));
        const pourboire = Math.round(tarifs.taxi_pourboire_max * douceur);
        encaisser(prix + pourboire, pourboire ? 'COURSE + ' + pourboire + ' $ DE POURBOIRE' : 'COURSE (CONDUITE BRUTALE)');
        taxi.courses++;
        B.partie.stats.courses = (B.partie.stats.courses || 0) + 1;
        taxi.etape = null; taxi.destination = null;
      }
    },

    abandonner: function (raison) {
      if (taxi.client) { taxi.client.etat = 'flane'; taxi.client.cri = 0; taxi.client.client = false; }
      taxi.client = null; taxi.destination = null; taxi.etape = null;
      if (raison) Hud.message(raison);
    },
  };

  function nouveauJour() {
    if (typeof Hud !== 'undefined') Hud.message('JOUR ' + B.partie.jour);
  }

  function sauvegarderPartie() {
    const p = B.partie, j = B.joueur;
    if (j) { p.x = Math.round(j.x); p.y = Math.round(j.y); p.vie = Math.max(1, j.vie); p.arme = j.arme; }
    p.empreinte = B.defs.empreinte;
    return Sauvegarde.ecrire(p);
  }

  function maj() {
    majMinuteries();
    taxi.maj();
    if (B.t % 600 === 0 && B.etat === 'jeu') sauvegarderPartie();
    if (B.t % 60 === 0) B.partie.stats.secondes++;
  }

  return { encaisser, payer, amende, potDeVin, factureHopital, nouveauJour, sauvegarderPartie,
           commerceDe, ouvert, acheterAmbulant, compagnie, interagir, soigner, hopital,
           setTimeoutJeu, taxi, maj };
})();
