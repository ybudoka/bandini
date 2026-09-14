/* Bandini — missions, boulots, economie du joueur, sauvegarde de la partie.
   M0 : l'argent (gagner, payer, amende, pot-de-vin, hopital) et la sauvegarde. */

const Missions = (function () {
  'use strict';

  /*: Les ellipses : `[noircir, TENIR, eclaircir]`, en images (voir
    `Jeu.transiter`). ⚠️ Ce n'est pas un fondu de porte — une porte, on la
    passe ; ici il PASSE DU TEMPS, et ce temps se sent dans le noir tenu, ou
    s'ecrit ce qui vient d'arriver. Le noir est la moitie de la duree : plus
    court, on n'a pas fini de lire ; plus long, on attend. */
  const FONDU_ELLIPSE = [40, 70, 40];   // l'hopital, la prison : la plus longue absence
  const FONDU_NUIT = [32, 56, 32];      // une nuit de sommeil
  const FONDU_SOUFFLE = [24, 42, 24];   // la compagnie d'une fille de la Brume

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

  /** Manger reprend aussi le souffle. L'endurance ne va pas dans la
      sauvegarde (elle se refait toute seule) : elle vit sur le joueur. */
  /** Manger : le souffle d'abord, et ce qui deborde devient du SURPLUS.

      ⚠️ Sans le surplus, manger ne servait a rien : le souffle remonte tout
      seul de 0,24 par image des qu'on arrete de courir — une barre vide se
      remplit en sept secondes. Une poutine a 18 $ rendait 70 points qu'on
      aurait eus gratuitement en s'arretant quatre secondes. Le surplus est la
      part que la regeneration ne peut PAS donner. */
  function nourrir(j, souffle) {
    if (!souffle || !j) return;
    const plein = B.defs.recherche.vitesses.endurance;
    const manque = Math.max(0, plein - j.endurance);
    j.endurance = Math.min(plein, j.endurance + souffle);
    const reste = souffle - manque;
    if (reste > 0) j.surplus = Math.min(B.defs.economie.souffle.surplus_max, (j.surplus || 0) + reste);
  }

  /** Le cafe : pendant un temps, le sprint coute moitie moins (`economie.cafe`
      le dit, `Entites` le depense). Un deuxieme cafe ne s'empile pas, il
      repart la minuterie — sinon on s'acheterait l'endurance infinie a 4 $. */
  function cafeine(j) {
    if (!j) return;
    j.cafeine = Math.round(B.defs.economie.cafe.duree_s * 60);
    Hud.message('BIEN RÉVEILLÉ');
  }

  /** Acheter au kiosque ou au camion : de la vie, du souffle et, au café, de
      quoi courir plus longtemps — contre de l'argent. */
  function acheterAmbulant(j, etal) {
    const commerce = commerceDe(etal.slug);
    if (!commerce) return false;
    if (!ouvert(commerce)) { Hud.message('FERME'); Son.SFX.erreur(); return true; }
    const prix = Math.round(B.defs.economie.tarifs[commerce.tarif] * rabais('kiosque'));
    if (B.partie.argent < prix) { Hud.message(prix + ' $ — PAS ASSEZ'); Son.SFX.erreur(); return true; }
    payer(prix, commerce.nom.toUpperCase());
    soigner(j, commerce.gain_pv ? B.defs.economie.tarifs[commerce.gain_pv] : 0);
    nourrir(j, commerce.gain_souffle ? B.defs.economie.tarifs[commerce.gain_souffle] : 0);
    if (commerce.effet === 'cafe') cafeine(j);
    Son.SFX.argent();
    if (commerce.service === 'journal') Hud.message('LE CLAIRON DE LA BAIE');
    return true;
  }

  /** Un rabais gagne dans l'histoire (1 = plein prix). */
  function rabais(cle) { return (B.partie && B.partie.rabais && B.partie.rabais[cle]) || 1; }

  /** La compagnie d'une fille de la Brume : ca se paie, et ca ne se montre pas. */
  function compagnie(j, fille) {
    const prix = B.defs.economie.tarifs.compagnie;
    if (B.recherche.etoiles > 0) { Hud.message('PAS AVEC LA POLICE AUX FESSES'); return true; }
    if (B.partie.argent < prix) { Hud.message(prix + ' $ — PAS ASSEZ'); Son.SFX.erreur(); return true; }
    payer(prix, 'LA BRUME');
    fille.minuterie = 900;
    Jeu.transiter(FONDU_SOUFFLE, function () {
      soigner(j, B.defs.economie.tarifs.compagnie_pv);
    }, 'ON REPREND SON SOUFFLE');
    return true;
  }

  /** La fille de la Brume a portee de main — la meme pour l'invite et pour
      l'action, pour que le HUD ne promette jamais autre chose que ce qui va
      se passer. */
  function filleSousLaMain(j) {
    return Entites.pietonsAutour(j.x, j.y, 26).find(function (e) {
      return e.metier === 'compagnie' && e.vivant && e.etat !== 'fuit';
    }) || null;
  }

  /** Ce qu'on peut faire la ou l'on est (bouton ACTION). */
  function interagir(j) {
    // Un personnage de l'histoire, un panneau de defi : avant tout le reste.
    const perso = Histoire.personnageSousLaMain(j);
    if (perso) return Histoire.parler(perso.personnage);
    const panneau = Histoire.panneauSousLaMain(j);
    if (panneau) return Histoire.proposerDefi(panneau.defi);
    const etal = Entites.autour(j.x, j.y, 30, function (e) { return e.type === 'ambulant'; })[0];
    if (etal) return acheterAmbulant(j, etal);
    // Un temoin qui court raconter : on lui achete le silence.
    const temoin = Entites.pietonsAutour(j.x, j.y, B.defs.recherche.police.silence_rayon_px).find(function (e) {
      return e.etat === 'temoin' && e.crime && !e.crime.rapporte;
    });
    if (temoin) return Police.acheterLeSilence(j, temoin);
    const fille = filleSousLaMain(j);
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
    Police.remiseAZero();
    if (taxi.etape) taxi.abandonner();
    if (B.defi) Histoire.finirDefi(false, 'A L’HOPITAL');
    Histoire.evenement('mort');
    const lieu = Monde.carte.points.find(function (p) { return p.slug === 'hopital'; });
    Jeu.transiter(FONDU_ELLIPSE, function () {
      if (lieu) { j.x = lieu.x * TT + 8; j.y = lieu.y * TT + 20; }
      j.vie = j.vieMax; j.invincible = 90; j.saigne = 0; j.endurance = 100; j.cafeine = 0;
      j.surplus = 0;                  // le surplus est passager : il ne survit pas a l'hopital
      Entites.dansLaCarte(j);
      Monde.centrerCamera(j.x, j.y);
      j.hospitalise = false;
    }, 'REVEIL A L’HOPITAL — ' + facture + ' $');
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
    if (B.defi) Histoire.finirDefi(false, 'EN PRISON');
    Histoire.evenement('arrete');
    if (agent) { agent.etat = 'flane'; agent.but = null; }
    const heures = B.defs.recherche.police.prison_heures / 24;
    p.heure += heures; while (p.heure >= 1) { p.heure -= 1; p.jour += 1; nouveauJour(); }
    Jeu.transiter(FONDU_ELLIPSE, function () {
      const poste = Monde.carte.points.find(function (q) { return q.slug === 'poste'; });
      if (poste) { j.x = poste.x * TT + 8; j.y = poste.y * TT + 20; }
      j.vie = j.vieMax; j.invincible = 90; j.saigne = 0; j.arrete = false; j.surplus = 0;
      Entites.dansLaCarte(j);
      Monde.centrerCamera(j.x, j.y);
      sauvegarderPartie();
    }, 'PRISON — ' + fine + ' $, ARMES CONFISQUEES');
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
      // Le meme outil que les donneurs : un client qui leve le bras au bord du
      // trottoir sans rien dire, on le prend pour un passant de plus.
      const civil = Histoire.personnage('civil');
      Entites.bulle(client, civil ? civil.heler : '');
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
          Son.SFX.porte('vehicule');    // le client monte et claque la portiere
        }
        return;
      }
      const d = taxi.destination;
      if (dist2(v.x, v.y, d.x, d.y) < 44 * 44 && Math.abs(v.vitesse) < 0.4) {
        // ⚠️ Les trois nombres de la course viennent de la FICHE du boulot
        // (`economie.BOULOTS`), y compris ce qu'un choc mange du pourboire :
        // ils etaient perdus dans `tarifs`, ou rien ne les rattachait au taxi.
        const boulot = B.defs.economie.boulots.taxi;
        const chocs = v.chocs - taxi.chocsDepart;
        const douceur = Math.max(0, 1 - chocs * boulot.malus_choc);
        const prix = Math.round(boulot.base + boulot.par_tuile * (taxi.distance / TT));
        const pourboire = Math.round(boulot.prime * douceur);
        encaisser(prix + pourboire, pourboire ? 'COURSE + ' + pourboire + ' $ DE POURBOIRE' : 'COURSE (CONDUITE BRUTALE)');
        taxi.courses++;
        B.partie.stats.courses = (B.partie.stats.courses || 0) + 1;
        taxi.etape = null; taxi.destination = null;
      }
    },

    abandonner: function (raison) {
      // Sans course en cours, il n'y a rien a abandonner : on se tait.
      const encours = !!taxi.etape;
      if (taxi.client) { taxi.client.etat = 'flane'; taxi.client.cri = 0; taxi.client.client = false; Entites.taire(taxi.client); }
      taxi.client = null; taxi.destination = null; taxi.etape = null;
      if (raison && encours) Hud.message(raison);
    },
  };

  // --- Les points d'action des interieurs --------------------------------------------

  //: ⚠️ Un type de point sans libelle ici, ou sans cas dans `menuDuPoint`, est
  //: un comptoir qu'on touche pour rien. Le juge du banc les compare a ceux que
  //: `carte.INTERIEURS` declare : on ne peut plus dessiner un comptoir mort.
  const LIBELLES = {
    lit: 'DORMIR', coffre: 'COFFRE', garde_robe: 'GARDE-ROBE', vendre: 'VENDRE LE CHAR', reparer: 'REPARER',
    repeindre: 'REPEINDRE', acheter: 'ACHETER', hotdog: 'MANGER', soigner: 'SE FAIRE SOIGNER', caisse: 'LA CAISSE',
    journal: 'LE CLAIRON', contact: 'PARLER', sergent: 'PARLER', casier: 'LE CARNET',
    emplettes: 'ACHETER', salon: 'SE FAIRE COIFFER', escalier: 'MONTER', fouiller: 'FOUILLER',
    fourriere: 'LE LOT',
  };

  /** Le libelle d'invite d'un type de point — et la preuve qu'il est servi. */
  function libelleDuPoint(type) { return LIBELLES[type] || null; }

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
    // ⚠️ Un personnage DEBOUT devant nous passe avant le comptoir : depuis
    // qu'on les voit, Bouchard et Josee ne se tiennent plus forcement sur leur
    // point (Josee pointe une TABLE — personne ne se tient debout dessus), et
    // c'est la personne qu'on vise, pas la tuile.
    const perso = Histoire.personnageSousLaMain(j);
    if (perso) { j.animT = 10; j.animType = 'ramasse'; return Histoire.parler(perso.personnage); }
    const point = pointSousLaMain(j);
    if (!point) return false;
    j.animT = 10; j.animType = 'ramasse';           // un geste vers le comptoir
    // Le sergent au casse-croute, Josee au bar : des personnages, pas des
    // comptoirs. Leur point reste le filet, si on l'aborde par l'autre bord.
    const assis = Histoire.personnageDuPoint(point.type);
    if (assis) return Histoire.parler(assis.slug);
    // L'escalier et les tiroirs : un geste, pas un menu.
    if (point.type === 'escalier') return Jeu.changerEtage(point.vers);
    if (point.type === 'fouiller') return fouiller(point);
    const menu = menuDuPoint(point);
    if (!menu) { Hud.message('PLUS TARD'); return true; }
    // Un comptoir qui reste ouvert se refait apres chaque achat : l'arme passe
    // a « DEJA A TOI », le magot en haut a droite fond, les munitions de ce
    // qu'on vient d'acheter apparaissent. Sans ca, on paie deux fois.
    menu.refaire = function () { return menuDuPoint(point); };
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
        return { titre: piece.nom.toUpperCase(), items: items };
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
        items.push({ libelle: 'HOT-DOG', detail: tarifs.hotdog + ' $ / +' + tarifs.hotdog_pv + ' PV +' + tarifs.hotdog_souffle + ' SOUFFLE',
                     actif: p.argent >= tarifs.hotdog,
                     faire: function () { payer(tarifs.hotdog, 'HOT-DOG'); soigner(B.joueur, tarifs.hotdog_pv); nourrir(B.joueur, tarifs.hotdog_souffle); Son.SFX.argent(); return false; } });
        // Un casse-croute sert le cafe : sinon la roulotte du trottoir est le
        // seul endroit du jeu ou courir plus longtemps s'achete, et elle ferme.
        items.push({ libelle: 'CAFÉ', detail: tarifs.cafe + ' $ / +' + tarifs.cafe_souffle + ' SOUFFLE · COURSE LONGUE ' + B.defs.economie.cafe.duree_s + ' S',
                     actif: p.argent >= tarifs.cafe,
                     faire: function () { payer(tarifs.cafe, 'CAFÉ'); soigner(B.joueur, tarifs.cafe_pv); nourrir(B.joueur, tarifs.cafe_souffle); cafeine(B.joueur); Son.SFX.argent(); return false; } });
        return { titre: piece.nom.toUpperCase(), items: items, sur: p.argent + ' $' };
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
        return { titre: piece.nom.toUpperCase(), items: items, sur: p.argent + ' $' };
      case 'emplettes':
        return menuComptoir(point, items);
      case 'salon':
        return menuSalon(items);
      case 'casier':
        return menuCasier();
      default:
        return null;
    }
  }

  // --- Les comptoirs des commerces ordinaires ------------------------------------------

  /** Ce qu'on achete au comptoir d'un commerce ordinaire.

      ⚠️ Rien n'est ecrit ici : le comptoir vient du serveur
      (`magasins.COMPTOIRS`, par famille de devanture), les prix de
      `economie.TARIFS`, les armes du catalogue des armes et les tenues de
      celui des tenues. Ajouter un article a une quincaillerie ne demande donc
      pas une ligne de JS — et un article qui pointerait a cote se voit au
      test, pas dans la partie. */
  function menuComptoir(point, items) {
    const p = B.partie, tarifs = B.defs.economie.tarifs, piece = B.interieur;
    const comptoir = (B.defs.comptoirs || {})[point.genre];
    if (!comptoir) return null;
    comptoir.articles.forEach(function (a) {
      if (a.arme) return items.push(itemArme(a, comptoir.marge));
      if (a.tenue) return items.push(itemTenue(a, comptoir.rabais));
      const prix = Math.round(tarifs[a.tarif] || 0);
      const gains = [];
      if (a.gain_pv) gains.push('+' + tarifs[a.gain_pv] + ' PV');
      if (a.gain_souffle) gains.push('+' + tarifs[a.gain_souffle] + ' SOUFFLE');
      items.push({ libelle: a.nom.toUpperCase(), detail: prix + ' $' + (gains.length ? ' / ' + gains.join(' ') : ''),
                   actif: p.argent >= prix,
                   faire: function () {
                     payer(prix, a.nom.toUpperCase());
                     if (a.gain_pv) soigner(B.joueur, tarifs[a.gain_pv]);
                     if (a.gain_souffle) nourrir(B.joueur, tarifs[a.gain_souffle]);
                     if (a.effet === 'cafe') cafeine(B.joueur);
                     if (a.journal) { lireLeJournal(); return true; }
                     Son.SFX.argent();
                     return false;
                   } });
    });
    return { titre: piece.nom.toUpperCase(), items: items, sur: p.argent + ' $' };
  }

  /** Une arme au comptoir du quincaillier : la meme que Chez Gus, avec sa marge. */
  function itemArme(article, marge) {
    const p = B.partie, arme = Combat.armeDef(article.arme);
    if (!arme) return { libelle: article.nom.toUpperCase(), actif: false };
    const prix = Math.round(arme.prix * (marge || 1));
    const deja = !!p.armes[article.arme];
    return { libelle: article.nom.toUpperCase(), detail: deja ? 'DEJA A TOI' : prix + ' $',
             actif: !deja && p.argent >= prix,
             faire: function () {
               payer(prix, article.nom.toUpperCase());
               Combat.ramasserArme(article.arme, arme.chargeur);
               return false;
             } };
  }

  /** Une tenue a la friperie : le prix de la boutique, moins le rabais de l'usage. */
  function itemTenue(article, rabaisTenue) {
    const p = B.partie;
    const tenue = (B.defs.tenues || []).find(function (t) { return t.slug === article.tenue; });
    if (!tenue) return { libelle: article.nom.toUpperCase(), actif: false };
    const prix = Math.round(tenue.prix * (rabaisTenue || 1));
    const deja = p.tenues.indexOf(article.tenue) >= 0;
    return { libelle: tenue.nom.toUpperCase(),
             detail: deja ? (p.tenue === article.tenue ? 'PORTEE' : 'A TOI') : prix + ' $',
             actif: deja || p.argent >= prix,
             faire: function () {
               if (!deja) { payer(prix, tenue.nom.toUpperCase()); p.tenues.push(article.tenue); }
               porterTenue(article.tenue);
               return true;
             } };
  }

  /** Le barbier : une couleur de cheveux, et la police cherche encore le gars
      d'avant. ⚠️ Meme effet qu'un changement de linge (`Police.remiseAZero`) :
      c'est LA raison d'entrer chez un coiffeur quand on a les etoiles au cul. */
  function menuSalon(items) {
    const p = B.partie, prix = B.defs.economie.tarifs.coupe;
    (B.defs.coiffures || []).forEach(function (c) {
      items.push({ libelle: c.nom.toUpperCase(), detail: p.cheveux === c.couleur ? 'C\u2019EST LA TIENNE' : prix + ' $',
                   actif: p.cheveux !== c.couleur && p.argent >= prix,
                   faire: function () {
                     payer(prix, 'COUPE DE CHEVEUX');
                     p.cheveux = c.couleur;
                     B.joueur.swaps = apparenceDuJoueur(p, B.defs);
                     Police.remiseAZero();
                     return true;
                   } });
    });
    return { titre: B.interieur.nom.toUpperCase(), items: items, sur: p.argent + ' $',
             aide: 'CHANGER DE TETE FAIT OUBLIER LA TIENNE' };
  }

  /** Le carnet du poste : ce que la police sait de toi. M11 l'etoffera. */
  function menuCasier() {
    const p = B.partie, eco = B.defs.economie;
    return { titre: 'LE CARNET', items: [
      { libelle: 'DOSSIER', detail: p.casier + ' / ' + eco.casier_max, actif: false },
      { libelle: 'ARRESTATIONS', detail: '' + p.stats.arrestations, actif: false },
      { libelle: 'CRIMES VUS', detail: '' + p.stats.crimes, actif: false },
      { libelle: 'CHARS VOLES', detail: '' + p.stats.volees, actif: false },
      { libelle: 'LA PROCHAINE AMENDE', detail: amende(p.argent, 1, p.casier) + ' $', actif: false },
    ], aide: 'PLUS LE DOSSIER EST EPAIS, PLUS L\u2019AMENDE MONTE' };
  }

  /** Fouiller les tiroirs d'un logement : une fois par adresse et par etage.

      ⚠️ La cle est celle de la PORTE, pas de la piece : les vingt logements de
      la ville partagent le meme plan, et sans ca le premier fouille les aurait
      tous vides. L'etage compte a part — deux planchers, deux commodes. */
  function fouiller(point) {
    const p = B.partie, tarifs = B.defs.economie.tarifs;
    const porte = Monde.carte.porte;
    const cle = (porte ? porte.lieu : 'ici') + ':' + B.interieur.slug + ':' + point.x + ',' + point.y;
    p.fouilles = p.fouilles || {};
    if (p.fouilles[cle]) { Hud.message('LES TIROIRS SONT VIDES'); return true; }
    p.fouilles[cle] = 1;
    const gain = Math.round(tarifs.fouille_min + B.rng() * (tarifs.fouille_max - tarifs.fouille_min));
    encaisser(gain, 'DANS LES TIROIRS');
    Son.SFX.argent();
    return true;
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
    // ⚠️ `apparenceDuJoueur` et pas `{ c: ... }` : ecraser les swaps effacait la
    // teinture du barbier des qu'on changeait de linge.
    B.joueur.swaps = apparenceDuJoueur(B.partie, B.defs);
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

  /** Dormir : la nuit passe, on se reveille au matin, la partie est sauvee.

      ⚠️ La nuit passe AU NOIR, comme l'hopital et la prison : le jour ne
      change pas sous les yeux du joueur, il a change quand la lumiere revient. */
  function dormir() {
    Jeu.transiter(FONDU_NUIT, function () {
      const p = B.partie;
      p.jour += 1;
      p.heure = 0.30;
      B.joueur.vie = B.joueur.vieMax;
      B.joueur.endurance = 100;
      B.joueur.cafeine = 0;
      B.joueur.surplus = 0;           // une nuit reprend le souffle, pas l'avance

      p.vie = B.joueur.vie;
      Police.remiseAZero();
      nouveauJour();
      sauvegarderPartie();
    }, 'LE LENDEMAIN MATIN');
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
    // L'histoire a fait la une : la manchette est imposee, une fois.
    if (p.manchetteForcee) { choisie = (B.defs.journal_speciales || []).find(function (m) { return m.slug === p.manchetteForcee; }) || null; p.manchetteForcee = null; }
    for (const r of regles) {
      if (choisie) break;
      if (delta(r.cle) >= r.min) { choisie = r; break; }
    }
    p.journal = { crimes: s.crimes, tues: s.tues, volees: s.volees, courses: s.courses || 0, hospitalisations: s.hospitalisations || 0 };
    return choisie || regles[regles.length - 1] || null;
  }

  /** La manchette s'affiche ET se lit : le narrateur du Clairon la dit a voix haute. */
  function direLaManchette(m) {
    Hud.dialogue('LE CLAIRON DE LA BAIE', [m.titre, m.texte], 420);
    if (m.slug) { Son.Voix.chargerHistoire('journal'); Son.Voix.parler('narrateur-journal-' + m.slug, {}); }
  }

  function lireLeJournal() {
    const m = B.partie.derniereManchette;
    if (m) direLaManchette(m);
    else Hud.dialogue('LE CLAIRON DE LA BAIE', ['RIEN A SIGNALER A BAIE-DES-BRUMES.'], 300);
  }

  function nouveauJour() {
    revenusDuJour();
    const m = manchetteDuJour();
    if (m) { B.partie.derniereManchette = m; direLaManchette(m); }
    else Hud.message('JOUR ' + B.partie.jour);
  }

  // --- Le marche noir : Josee, une fois le Faubourg libere --------------------------------

  function menuMarcheNoir() {
    const p = B.partie, mn = B.defs.marche_noir || { rabais: 1, articles: [], munitions: [] };
    const items = [];
    mn.articles.forEach(function (slug) {
      const arme = Combat.armeDef(slug);
      if (!arme) return;
      const prix = Math.round(arme.prix * mn.rabais), deja = !!p.armes[slug];
      items.push({ libelle: arme.nom.toUpperCase(), detail: deja ? 'DEJA A TOI' : prix + ' $', actif: !deja && p.argent >= prix,
                   faire: function () { payer(prix, arme.nom.toUpperCase()); Combat.ramasserArme(slug, arme.chargeur); return false; } });
    });
    mn.munitions.forEach(function (slug) {
      const arme = Combat.armeDef(slug);
      if (!arme || !p.armes[slug] || arme.prix_munitions === null) return;
      const prix = Math.round(arme.prix_munitions * mn.rabais), pleine = p.armes[slug].mun >= arme.munitions_max;
      items.push({ libelle: 'MUNITIONS ' + arme.nom.toUpperCase(), detail: pleine ? 'PLEIN' : prix + ' $', actif: !pleine && p.argent >= prix,
                   faire: function () { payer(prix, 'MUNITIONS'); Combat.ramasserArme(slug, arme.chargeur); return false; } });
    });
    return { titre: 'MARCHÉ NOIR', sur: p.argent + ' $', refaire: menuMarcheNoir,
             aide: 'SANS FACTURE. ' + Math.round((1 - mn.rabais) * 100) + ' % DE MOINS QUE CHEZ GUS.', items: items };
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
    if (!j || j.dansVehicule || B.menu || B.cinema) return;
    if (B.interieur) {
      // ⚠️ Meme ordre que `utiliserPoint`, sinon le HUD promet « MANGER » et
      // ACTION parle au sergent.
      const dedans = Histoire.personnageSousLaMain(j);
      if (dedans) { const d = Histoire.personnage(dedans.personnage); B.invite = 'PARLER À ' + (d ? d.nom.toUpperCase() : '?'); return; }
      const point = pointSousLaMain(j);
      if (point) {
        const assis = Histoire.personnageDuPoint(point.type);
        B.invite = assis ? 'PARLER À ' + assis.nom.toUpperCase() : (LIBELLES[point.type] || point.type.toUpperCase());
        return;
      }
      if (Monde.porteDevant(j)) B.invite = 'SORTIR';
      return;
    }
    const perso = Histoire.personnageSousLaMain(j);
    if (perso) { const d = Histoire.personnage(perso.personnage); B.invite = 'PARLER À ' + (d ? d.nom.toUpperCase() : '?'); return; }
    const panneau = Histoire.panneauSousLaMain(j);
    if (panneau) { B.invite = 'DÉFI'; return; }
    const etal = Entites.autour(j.x, j.y, 30, function (e) { return e.type === 'ambulant'; })[0];
    if (etal) { const c = commerceDe(etal.slug); B.invite = c ? c.nom.toUpperCase() + ' — ' + Math.round(B.defs.economie.tarifs[c.tarif] * rabais('kiosque')) + ' $' : 'ACHETER'; return; }
    const temoin = Entites.pietonsAutour(j.x, j.y, B.defs.recherche.police.silence_rayon_px).find(function (e) {
      return e.etat === 'temoin' && e.crime && !e.crime.rapporte;
    });
    if (temoin) { B.invite = 'ACHETER SON SILENCE — ' + B.defs.economie.tarifs.silence_temoin + ' $'; return; }
    // ⚠️ Meme ordre que `interagir` : elle passe avant l'objet par terre,
    // sinon l'invite annoncerait un ramassage et ACTION ferait autre chose.
    // C'est aussi la derniere preuve qu'on a devant soi une fille de la
    // Brume et pas une passante — le HUD la nomme.
    const fille = filleSousLaMain(j);
    if (fille) { B.invite = 'LA BRUME — ' + B.defs.economie.tarifs.compagnie + ' $'; return; }
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
    // Le cafe est une minuterie, pas une depense : il s'ecoule aussi au volant
    // et dans une piece, la ou `majJoueur` ne passe pas.
    if (B.joueur && B.joueur.cafeine > 0) B.joueur.cafeine--;
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
           commerceDe, ouvert, acheterAmbulant, compagnie, interagir, soigner, nourrir, cafeine, hopital,
           taxi, arrestation, prison, utiliserPoint, pointSousLaMain, libelleDuPoint, menuDuPoint, acheterPropriete, proprieteDe, possede,
           dormir, porterTenue, fouiller, menuComptoir, menuSalon, menuCasier, charDevant, prixDeVente, menuGarage, menuArmurerie, menuVetements,
           revenusDuJour, manchetteDuJour, lireLeJournal, menuMarcheNoir, ramasserPaquet, majInvite, rabais, maj };
})();
