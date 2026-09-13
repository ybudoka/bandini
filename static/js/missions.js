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
    // Un temoin qui court raconter : on lui achete le silence.
    const temoin = Entites.pietonsAutour(j.x, j.y, B.defs.recherche.police.silence_rayon_px).find(function (e) {
      return e.etat === 'temoin' && e.crime && !e.crime.rapporte;
    });
    if (temoin) return Police.acheterLeSilence(j, temoin);
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

  // --- L'arrestation : pot-de-vin ou prison ---------------------------------------------

  /** La main au collet. Un menu : graisser la patte, ou suivre. */
  function arrestation(agent) {
    const j = B.joueur, r = B.recherche, eco = B.defs.economie, p = B.partie;
    if (j.arrete) return;
    j.arrete = true; j.vx = 0; j.vy = 0; j.etat = 'flane';
    const etoiles = Math.max(1, r.etoiles);
    const pot = potDeVin(etoiles, p.casier);
    const fine = amende(p.argent, etoiles, p.casier);
    const items = [];
    items.push({ libelle: 'POT-DE-VIN', detail: pot + ' $', actif: p.argent >= pot, faire: function () {
      const ami = p.sergentAmi && etoiles <= eco.pot_de_vin_ami_max;
      const chance = eco.pot_de_vin_accepte[Math.min(5, etoiles)];
      payer(pot, 'POT-DE-VIN');
      if (ami || B.rng() < chance) {
        Police.remiseAZero();
        j.arrete = false;
        if (agent) { agent.etat = 'flane'; agent.but = null; }
        Hud.dialogue(ami ? 'SGT BOUCHARD' : 'L’AGENT', ['« ON N’A RIEN VU. CIRCULE. »'], 180);
        return true;
      }
      Police.signalerCrime('pot_de_vin_refuse', j.x, j.y, true);
      Hud.dialogue('L’AGENT', ['« TU TE PENSES OU, TOI? »'], 120);
      prison(agent);
      return true;
    } });
    items.push({ libelle: 'SUIVRE L’AGENT', detail: 'AMENDE ' + fine + ' $', faire: function () { prison(agent); return true; } });
    Hud.ouvrirMenu({ titre: 'ARRETE !', sur: etoiles + ' ETOILE' + (etoiles > 1 ? 'S' : ''), items: items,
                     aide: 'CASIER : ' + p.casier, obligatoire: true });
  }

  /** La prison prend l'amende, les armes, quelques heures, et note le casier. */
  function prison(agent) {
    const j = B.joueur, r = B.recherche, p = B.partie;
    const fine = amende(p.argent, Math.max(1, r.etoiles), p.casier);
    payer(fine, 'AMENDE');
    p.casier = Math.min(B.defs.economie.casier_max, p.casier + 1);
    p.stats.arrestations++;
    p.armes = { poings: { mun: null } }; p.arme = 'poings'; j.arme = 'poings';
    Police.remiseAZero();
    if (taxi.etape) taxi.abandonner();
    if (agent) { agent.etat = 'flane'; agent.but = null; }
    const heures = B.defs.recherche.police.prison_heures / 24;
    p.heure += heures; while (p.heure >= 1) { p.heure -= 1; p.jour += 1; nouveauJour(); }
    Hud.fondu(150, 'PRISON — ' + fine + ' $, ARMES CONFISQUEES');
    setTimeoutJeu(60, function () {
      const poste = Monde.carte.points.find(function (q) { return q.slug === 'poste'; });
      if (poste) { j.x = poste.x * TT + 8; j.y = poste.y * TT + 20; }
      j.vie = j.vieMax; j.invincible = 90; j.saigne = 0; j.arrete = false;
      Entites.dansLaCarte(j);
      Monde.centrerCamera(j.x, j.y);
      sauvegarderPartie();
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

  // --- Les points d'action des interieurs --------------------------------------------

  const LIBELLES = {
    lit: 'DORMIR', coffre: 'COFFRE', garde_robe: 'GARDE-ROBE', vendre: 'VENDRE LE CHAR', reparer: 'REPARER',
    repeindre: 'REPEINDRE', acheter: 'ACHETER', hotdog: 'MANGER', soigner: 'SE FAIRE SOIGNER', caisse: 'LA CAISSE',
    journal: 'LE CLAIRON', contact: 'PARLER', sergent: 'PARLER', sortie_prison: 'SORTIR', casier: 'CASIER', guichet: 'GUICHET',
  };

  function pointSousLaMain(j) {
    const piece = B.interieur;
    if (!piece) return null;
    const tx = j.x / TT - 0.5, ty = j.y / TT - 0.5;
    let meilleur = null, dMin = 1.6;
    for (const p of piece.points) {
      const d = Math.hypot(p.x - tx, p.y - ty);
      if (d < dMin) { dMin = d; meilleur = p; }
    }
    return meilleur;
  }

  function utiliserPoint(j) {
    const point = pointSousLaMain(j);
    if (!point) return false;
    j.animT = 10; j.animType = 'ramasse';           // un geste vers le comptoir
    const menu = menuDuPoint(point);
    if (!menu) { Hud.message('PLUS TARD'); return true; }
    Hud.ouvrirMenu(menu);
    return true;
  }

  function proprieteDe(lieu) {
    return (B.defs.economie.proprietes || []).find(function (p) { return p.lieu === lieu; }) || null;
  }

  function possede(propriete) { return !!(propriete && B.partie.proprietes[propriete.slug]); }

  /** L'entree de menu « prendre la caisse » d'une propriete a soi. */
  function itemCaisse(lieu) {
    const prop = proprieteDe(lieu);
    if (!possede(prop)) return null;
    const caisse = B.partie.proprietes[prop.slug].caisse || 0;
    return { libelle: 'PRENDRE LA CAISSE', detail: caisse + ' $', actif: caisse > 0, faire: function () {
      encaisser(caisse, prop.nom.toUpperCase());
      B.partie.proprietes[prop.slug].caisse = 0;
      return true;
    } };
  }

  function menuDuPoint(point) {
    const piece = B.interieur, p = B.partie, tarifs = B.defs.economie.tarifs;
    const items = [];
    const caisse = itemCaisse(piece.slug);
    if (caisse) items.push(caisse);
    switch (point.type) {
      case 'lit':
        items.push({ libelle: 'DORMIR JUSQU’AU MATIN', detail: 'SAUVEGARDE', faire: function () { dormir(); return true; } });
        items.push({ libelle: 'SAUVEGARDER SEULEMENT', faire: function () { sauvegarderPartie(); Hud.message('PARTIE SAUVEGARDEE'); return true; } });
        return { titre: 'LA PLANQUE', items: items };
      case 'coffre':
        return menuCoffre();
      case 'garde_robe':
        return menuGardeRobe();
      case 'vendre':
      case 'reparer':
      case 'repeindre':
        return menuGarage(items);
      case 'acheter':
        return piece.slug === 'armurerie' ? menuArmurerie() : menuVetements();
      case 'hotdog':
        items.push({ libelle: 'HOT-DOG', detail: tarifs.hotdog + ' $ / +' + tarifs.hotdog_pv + ' PV', actif: p.argent >= tarifs.hotdog,
                     faire: function () { payer(tarifs.hotdog, 'HOT-DOG'); soigner(B.joueur, tarifs.hotdog_pv); Son.SFX.argent(); return false; } });
        return { titre: 'CASSE-CROUTE DU FAUBOURG', items: items, sur: p.argent + ' $' };
      case 'soigner': {
        const prix = B.defs.economie.hopital.minimum;
        items.push({ libelle: 'SOINS COMPLETS', detail: prix + ' $', actif: p.argent >= prix && B.joueur.vie < B.joueur.vieMax,
                     faire: function () { payer(prix, 'SOINS'); soigner(B.joueur, 999); return true; } });
        return { titre: 'HOPITAL DE BAIE-DES-BRUMES', items: items, sur: p.argent + ' $' };
      }
      case 'caisse':
        if (!caisse) items.push({ libelle: 'CE N’EST PAS A TOI', actif: false });
        return { titre: piece.nom.toUpperCase(), items: items };
      case 'journal':
        items.push({ libelle: 'LE CLAIRON DE LA BAIE', detail: tarifs.journal + ' $', actif: p.argent >= tarifs.journal,
                     faire: function () { payer(tarifs.journal, 'JOURNAL'); lireLeJournal(); return true; } });
        return { titre: 'KIOSQUE A JOURNAUX', items: items, sur: p.argent + ' $' };
      default:
        return null;
    }
  }

  // --- La planque ----------------------------------------------------------------------

  function menuCoffre() {
    const p = B.partie;
    function depot(n) { return function () { const m = Math.min(n, p.argent); p.argent -= m; p.planque.coffre += m; Son.SFX.argent(); return false; }; }
    function retrait(n) { return function () { const m = Math.min(n, p.planque.coffre); p.planque.coffre -= m; p.argent += m; Son.SFX.argent(); return false; }; }
    return { titre: 'LE COFFRE', sur: 'COFFRE ' + p.planque.coffre + ' $ · POCHES ' + p.argent + ' $',
             aide: 'CE QUI EST DANS LE COFFRE NE PART PAS EN PRISON',
             items: [
               { libelle: 'DEPOSER 100 $', actif: p.argent >= 1, faire: depot(100) },
               { libelle: 'DEPOSER TOUT', actif: p.argent >= 1, faire: depot(Infinity) },
               { libelle: 'RETIRER 100 $', actif: p.planque.coffre >= 1, faire: retrait(100) },
               { libelle: 'RETIRER TOUT', actif: p.planque.coffre >= 1, faire: retrait(Infinity) },
             ] };
  }

  function porterTenue(slug) {
    const tenue = (B.defs.tenues || []).find(function (t) { return t.slug === slug; });
    if (!tenue) return false;
    B.partie.tenue = slug;
    B.joueur.swaps = { c: tenue.couleur };
    // Changer de linge, c'est devenir quelqu'un d'autre pour la police (M4 affinera).
    Police.remiseAZero();
    return true;
  }

  function menuGardeRobe() {
    const p = B.partie;
    const items = (B.defs.tenues || []).filter(function (t) { return p.tenues.indexOf(t.slug) >= 0; }).map(function (t) {
      return { libelle: t.nom.toUpperCase(), detail: p.tenue === t.slug ? 'PORTEE' : '', faire: function () { porterTenue(t.slug); return true; } };
    });
    return { titre: 'GARDE-ROBE', items: items, aide: 'CHANGER DE LINGE FAIT OUBLIER TA TETE' };
  }

  /** Dormir : la nuit passe, on se reveille au matin, la partie est sauvee. */
  function dormir() {
    const p = B.partie;
    p.jour += 1;
    p.heure = 0.30;
    B.joueur.vie = B.joueur.vieMax;
    B.joueur.endurance = 100;
    p.vie = B.joueur.vie;
    Police.remiseAZero();
    nouveauJour();
    sauvegarderPartie();
    Hud.fondu(120, 'LE LENDEMAIN MATIN');
  }

  // --- Le garage de Ti-Guy --------------------------------------------------------------

  /** Le char gare devant : le plus proche de la porte, dans les 90 px. */
  function charDevant() {
    const ext = B.exterieur;
    if (!ext) return null;
    let meilleur = null, dMin = 90 * 90;
    for (const e of ext.entites) {
      if (e.type !== 'vehicule' || e.etat === 'epave') continue;
      const d = dist2(e.x, e.y, ext.x, ext.y);
      if (d < dMin) { dMin = d; meilleur = e; }
    }
    return meilleur;
  }

  function prixDeVente(v) {
    const eco = B.defs.economie, p = B.partie;
    const ventes = (p.ventes && p.ventes[v.slug] && p.ventes[v.slug].jour === p.jour) ? p.ventes[v.slug].n : 0;
    const part = Math.max(0, Math.min(1, v.vie / v.vieMax));
    return Math.max(0, Math.round(v.def.prix * eco.vente_fraction * part * Math.max(0, 1 - eco.vente_malus_doublon * ventes)));
  }

  function menuGarage(items) {
    const eco = B.defs.economie, p = B.partie, v = charDevant();
    if (!v) {
      items.push({ libelle: 'GARE UN CHAR DEVANT LA PORTE', actif: false });
      return { titre: 'GARAGE ROCCO BANDINI', items: items };
    }
    const vente = prixDeVente(v);
    const reparation = Math.round((v.vieMax - v.vie) * eco.reparation_par_pv);
    items.push({ libelle: 'VENDRE ' + v.def.nom.toUpperCase(), detail: vente + ' $', actif: vente > 0, faire: function () {
      encaisser(vente, 'VENDU');
      p.ventes = p.ventes || {};
      const jour = p.ventes[v.slug] && p.ventes[v.slug].jour === p.jour ? p.ventes[v.slug].n : 0;
      p.ventes[v.slug] = { jour: p.jour, n: jour + 1 };
      const i = B.exterieur.entites.indexOf(v);
      if (i >= 0) B.exterieur.entites.splice(i, 1);
      return true;
    } });
    items.push({ libelle: 'REPARER', detail: reparation + ' $', actif: reparation > 0 && p.argent >= reparation, faire: function () {
      payer(reparation, 'REPARATION'); v.vie = v.vieMax; return true;
    } });
    items.push({ libelle: 'REPEINDRE (EFFACE LE VOL)', detail: eco.repeinte + ' $', actif: p.argent >= eco.repeinte, faire: function () {
      payer(eco.repeinte, 'PEINTURE');
      const autres = v.def.couleurs.filter(function (c) { return c !== v.couleur; });
      v.couleur = autres.length ? autres[Math.floor(B.rng() * autres.length)] : v.couleur;
      v.swaps = { c: v.couleur }; v.vole = false; v.alarme = 0;
      Police.remiseAZero();
      return true;
    } });
    return { titre: 'GARAGE ROCCO BANDINI', items: items, sur: p.argent + ' $' };
  }

  // --- Les magasins ------------------------------------------------------------------

  function magasin(slug) { return (B.defs.magasins || []).find(function (m) { return m.slug === slug; }) || null; }

  function menuArmurerie() {
    const p = B.partie, m = magasin('armurerie');
    const items = [];
    (m ? m.articles : []).forEach(function (slug) {
      const arme = Combat.armeDef(slug);
      if (!arme) return;
      const deja = !!p.armes[slug];
      items.push({ libelle: arme.nom.toUpperCase(), detail: deja ? 'DEJA A TOI' : arme.prix + ' $', actif: !deja && p.argent >= arme.prix,
                   faire: function () { payer(arme.prix, arme.nom.toUpperCase()); Combat.ramasserArme(slug, arme.chargeur); return false; } });
    });
    (m ? m.munitions : []).forEach(function (slug) {
      const arme = Combat.armeDef(slug);
      if (!arme || !p.armes[slug] || arme.prix_munitions === null) return;
      const pleine = p.armes[slug].mun >= arme.munitions_max;
      items.push({ libelle: 'MUNITIONS ' + arme.nom.toUpperCase(), detail: pleine ? 'PLEIN' : arme.prix_munitions + ' $',
                   actif: !pleine && p.argent >= arme.prix_munitions,
                   faire: function () { payer(arme.prix_munitions, 'MUNITIONS'); Combat.ramasserArme(slug, arme.chargeur); return false; } });
    });
    return { titre: 'CHEZ GUS', items: items, sur: p.argent + ' $' };
  }

  function menuVetements() {
    const p = B.partie;
    const items = (B.defs.tenues || []).map(function (t) {
      const deja = p.tenues.indexOf(t.slug) >= 0;
      return { libelle: t.nom.toUpperCase(), detail: deja ? (p.tenue === t.slug ? 'PORTEE' : 'A TOI') : t.prix + ' $',
               actif: deja || p.argent >= t.prix, faire: function () {
                 if (!deja) { payer(t.prix, t.nom.toUpperCase()); p.tenues.push(t.slug); }
                 porterTenue(t.slug);
                 return true;
               } };
    });
    return { titre: 'BOUTIQUE ROSA', items: items, sur: p.argent + ' $' };
  }

  // --- Les proprietes -------------------------------------------------------------------

  /** A la porte d'une propriete a vendre : acheter ou entrer. Rend true si un menu s'ouvre. */
  function acheterPropriete(porte) {
    const prop = proprieteDe(porte.lieu);
    if (!prop || prop.phase !== 1 || possede(prop)) return false;
    const p = B.partie;
    Hud.ouvrirMenu({ titre: prop.nom.toUpperCase(), sur: p.argent + ' $',
      aide: prop.revenu_par_jour + ' $ PAR JOUR, A RAMASSER SUR PLACE',
      items: [
        { libelle: 'ACHETER', detail: prop.prix + ' $', actif: p.argent >= prop.prix, faire: function () {
          payer(prop.prix, prop.nom.toUpperCase());
          p.proprietes[prop.slug] = { jour: p.jour, caisse: 0 };
          Hud.message(prop.nom.toUpperCase() + ' EST A TOI', 180);
          return true;
        } },
        { libelle: 'ENTRER', faire: function () { Jeu.entrer(porte); return true; } },
      ] });
    return true;
  }

  function revenusDuJour() {
    const eco = B.defs.economie, p = B.partie;
    for (const slug in p.proprietes) {
      const prop = eco.proprietes.find(function (q) { return q.slug === slug; });
      if (!prop) continue;
      const plafond = prop.revenu_par_jour * eco.caisse_jours_max;
      p.proprietes[slug].caisse = Math.min(plafond, (p.proprietes[slug].caisse || 0) + prop.revenu_par_jour);
    }
  }

  // --- Le journal du matin --------------------------------------------------------------

  function manchetteDuJour() {
    const p = B.partie, hier = p.journal || {}, s = p.stats;
    const delta = function (k) { return (s[k] || 0) - (hier[k] || 0); };
    const regles = B.defs.journal || [];
    let choisie = null;
    for (const r of regles) {
      if (delta(r.cle) >= r.min) { choisie = r; break; }
    }
    p.journal = { crimes: s.crimes, tues: s.tues, volees: s.volees, courses: s.courses || 0, hospitalisations: s.hospitalisations || 0 };
    return choisie || regles[regles.length - 1] || null;
  }

  function lireLeJournal() {
    const m = B.partie.derniereManchette;
    if (m) Hud.dialogue('LE CLAIRON DE LA BAIE', [m.titre, m.texte], 420);
    else Hud.dialogue('LE CLAIRON DE LA BAIE', ['RIEN A SIGNALER A BAIE-DES-BRUMES.'], 300);
  }

  function nouveauJour() {
    revenusDuJour();
    const m = manchetteDuJour();
    if (m) { B.partie.derniereManchette = m; Hud.dialogue('LE CLAIRON DE LA BAIE', [m.titre, m.texte], 420); }
    else Hud.message('JOUR ' + B.partie.jour);
  }

  // --- Les paquets caches ------------------------------------------------------------------

  function ramasserPaquet(paquet) {
    const p = B.partie, tarifs = B.defs.economie.tarifs;
    B.joueur.animT = 12; B.joueur.animType = 'ramasse';
    p.paquets[paquet.numero] = true;
    const n = Object.keys(p.paquets).length;
    encaisser(tarifs.paquet, 'PAQUET ' + n + '/' + Monde.carte.def.paquets.length);
    if (n === 10) encaisser(tarifs.paquets_prime_10, 'PRIME : DIX PAQUETS');
    if (n === 20) encaisser(tarifs.paquets_prime_20, 'PRIME : VINGT PAQUETS');
    Entites.retirer(paquet);
  }

  /** L'invite ACTION du HUD : ce qu'on ferait ici, maintenant. */
  function majInvite(j) {
    B.invite = null;
    if (!j || j.dansVehicule || B.menu) return;
    if (B.interieur) {
      const point = pointSousLaMain(j);
      if (point) { B.invite = LIBELLES[point.type] || point.type.toUpperCase(); return; }
      if (Monde.porteDevant(j)) B.invite = 'SORTIR';
      return;
    }
    const etal = Entites.autour(j.x, j.y, 30, function (e) { return e.type === 'ambulant'; })[0];
    if (etal) { const c = commerceDe(etal.slug); B.invite = c ? c.nom.toUpperCase() + ' — ' + B.defs.economie.tarifs[c.tarif] + ' $' : 'ACHETER'; return; }
    const temoin = Entites.pietonsAutour(j.x, j.y, B.defs.recherche.police.silence_rayon_px).find(function (e) {
      return e.etat === 'temoin' && e.crime && !e.crime.rapporte;
    });
    if (temoin) { B.invite = 'ACHETER SON SILENCE — ' + B.defs.economie.tarifs.silence_temoin + ' $'; return; }
    const objet = Combat.objetSousLaMain(j);
    if (objet) { const a = Combat.armeDef(objet.arme); B.invite = 'RAMASSER ' + (a ? a.nom.toUpperCase() : ''); return; }
    const porte = Monde.porteDevant(j);
    if (porte) {
      const prop = proprieteDe(porte.lieu);
      B.invite = (prop && prop.phase === 1 && !possede(prop)) ? 'ACHETER ' + prop.nom.toUpperCase() : 'ENTRER';
      return;
    }
    const v = Vehicules.vehiculeSousLaMain(j);
    if (v) B.invite = (v.conducteur === 'trafic' ? 'VOLER ' : 'MONTER : ') + v.def.nom.toUpperCase();
  }

  function sauvegarderPartie() {
    const p = B.partie, j = B.joueur;
    if (j) {
      const dehors = B.exterieur ? { x: B.exterieur.x, y: B.exterieur.y } : { x: j.x, y: j.y };
      p.x = Math.round(dehors.x); p.y = Math.round(dehors.y); p.vie = Math.max(1, j.vie); p.arme = j.arme;
      // Le char gare devant la planque revient avec la partie.
      const planque = Monde.carte.ville ? Monde.carte.ville : Monde.carte;
      const porte = planque.portes.find(function (q) { return q.lieu === 'planque'; });
      p.planque.vehicule = null;
      if (porte) {
        const entites = B.exterieur ? B.exterieur.entites : B.entites;
        for (const e of entites) {
          if (e.type === 'vehicule' && e.etat !== 'epave' && dist2(e.x, e.y, porte.x * TT + 8, (porte.y + 1) * TT) < 100 * 100) {
            p.planque.vehicule = { slug: e.slug, couleur: e.couleur, vie: e.vie, x: Math.round(e.x), y: Math.round(e.y), angle: e.angle, vole: e.vole };
            break;
          }
        }
      }
    }
    p.empreinte = B.defs.empreinte;
    return Sauvegarde.ecrire(p);
  }

  function maj() {
    majMinuteries();
    taxi.maj();
    majInvite(B.joueur);
    // Les paquets se ramassent en passant dessus.
    if (B.joueur && !B.interieur) {
      for (const e of Entites.autour(B.joueur.x, B.joueur.y, 12, function (q) { return q.type === 'paquet'; })) ramasserPaquet(e);
    }
    if (B.t % 600 === 0 && B.etat === 'jeu') sauvegarderPartie();
    if (B.t % 60 === 0) B.partie.stats.secondes++;
  }

  return { encaisser, payer, amende, potDeVin, factureHopital, nouveauJour, sauvegarderPartie,
           commerceDe, ouvert, acheterAmbulant, compagnie, interagir, soigner, hopital,
           setTimeoutJeu, taxi, arrestation, prison, utiliserPoint, pointSousLaMain, acheterPropriete, proprieteDe, possede,
           dormir, porterTenue, charDevant, prixDeVente, menuGarage, menuArmurerie, menuVetements,
           revenusDuJour, manchetteDuJour, ramasserPaquet, majInvite, maj };
})();
