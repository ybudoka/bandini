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
    const prix = prixAmbulant(j, commerce);
    if (B.partie.argent < prix) { Hud.message(prix + ' $ — PAS ASSEZ'); Son.SFX.erreur(); return true; }
    payer(prix, commerce.nom.toUpperCase());
    if (j.coupons && j.coupons[commerce.slug]) delete j.coupons[commerce.slug];   // le coupon ne sert qu'une fois
    soigner(j, commerce.gain_pv ? B.defs.economie.tarifs[commerce.gain_pv] : 0);
    nourrir(j, commerce.gain_souffle ? B.defs.economie.tarifs[commerce.gain_souffle] : 0);
    if (commerce.effet === 'cafe') cafeine(j);
    Son.SFX.argent();
    if (commerce.service === 'journal') Hud.message('LE CLAIRON DE LA BAIE');
    return true;
  }

  /** Un rabais gagne dans l'histoire (1 = plein prix). */
  function rabais(cle) { return (B.partie && B.partie.rabais && B.partie.rabais[cle]) || 1; }

  // --- L'homme-sandwich et son coupon --------------------------------------------

  /** Ce que vaut le coupon d'un homme-sandwich sur ce kiosque (1 = pas de
      coupon). Il vit sur le JOUEUR, comme la cafeine : trois minutes ne
      meritent pas une sauvegarde, et il ne survit pas plus qu'elle. */
  function coupon(j, slug) {
    return (j && j.coupons && j.coupons[slug] > 0 && B.defs.reclame) ? B.defs.reclame.rabais : 1;
  }

  /** Le prix d'une bouchee au kiosque : le tarif, le rabais de l'histoire,
      et le coupon s'il y en a un — le meme calcul pour l'invite et l'achat,
      pour que le HUD ne promette jamais un prix que la caisse ne fait pas. */
  function prixAmbulant(j, commerce) {
    return Math.round(B.defs.economie.tarifs[commerce.tarif] * rabais('kiosque') * coupon(j, commerce.slug));
  }

  /** L'homme-sandwich a portee de main : celui qui te parle, ou qui passe. */
  function crieurSousLaMain(j) {
    return Entites.pietonsAutour(j.x, j.y, 26).find(function (e) {
      return e.metier === 'reclame' && e.vivant && e.etat !== 'fuit' && e.etat !== 'assomme' && e.etat !== 'temoin';
    }) || null;
  }

  /** Prendre le coupon : la prochaine bouchee a SON kiosque a `reclame.rabais`
      fois le prix, une fois, et il expire (`reclame.coupon_s`). Lui, une fois
      son papier donne, te laisse la paix un moment. */
  function prendreCoupon(j, crieur) {
    const r = B.defs.reclame, c = commerceDe(crieur.kiosque);
    if (!r || !c) return false;
    j.coupons = j.coupons || {};
    if (j.coupons[c.slug] > 0) { Hud.message('T’AS DÉJÀ LE COUPON'); return true; }
    j.coupons[c.slug] = Math.round(r.coupon_s * 60);
    Hud.message('COUPON — ' + c.nom.toUpperCase());
    Son.SFX.ramasse();
    crieur.etat = 'flane'; crieur.repos = r.repos_images; crieur.minuterie = 0;
    Entites.taire(crieur);
    return true;
  }

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
    const crieur = crieurSousLaMain(j);
    if (crieur) return prendreCoupon(j, crieur);
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
    if (boulot.etape) boulot.abandonner();
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
    // ⚠️ La provision de Me Desjardins efface l'AMENDE, et rien d'autre : la
    // page s'ajoute quand meme, les armes partent quand meme, le char va
    // quand meme au lot et la nuit passe quand meme. Un avocat sort son
    // client de prison ; il ne le rend pas innocent.
    const retenu = !!p.nettoyage.provision;
    const fine = retenu ? 0 : amende(p.argent, Math.max(1, r.etoiles), p.casier);
    if (retenu) p.nettoyage.provision = false;
    payer(fine, 'AMENDE');
    p.casier = Math.min(B.defs.economie.casier_max, p.casier + 1);
    p.stats.arrestations++;
    p.armes = { poings: { mun: null } }; p.arme = 'poings'; j.arme = 'poings';
    // ⚠️ Le char part au lot AVANT la remise a zero : apres, la police lache
    // le morceau et on n'a plus de raison de savoir ce qu'on conduisait.
    const saisi = charSaisissable(j);
    if (saisi) { const nom = saisi.def.nom.toUpperCase(); saisir(saisi); Hud.message(nom + ' A LA FOURRIERE', 240); }
    Police.remiseAZero();
    if (boulot.etape) boulot.abandonner();
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
    }, retenu ? 'PRISON — TON AVOCAT T’A SORTI, ARMES CONFISQUEES'
              : 'PRISON — ' + fine + ' $, ARMES CONFISQUEES');
  }



  // --- Les boulots au klaxon --------------------------------------------------------

  /*: ⚠️ UNE machine pour les quatre boulots, pas quatre machines. Le taxi de la
    v1 avait la sienne ; a quatre, on aurait recopie quatre fois « va la, reviens
    ici, encaisse » avec quatre facons de se tromper. Ce qui DIFFERE d'un boulot a
    l'autre tient dans `SORTES` ci-dessous ; tout le reste est commun.

    Les nombres, eux, ne sont pas ici : ils viennent de `economie.BOULOTS`, ou un
    juge Python les compare entre eux. */
  const SORTES = {
    //: `ramasser` : ce qu'on va chercher avant de rouler (null = rien).
    //: `destination` : ou l'on va, une fois charge.
    //: `perte` : ce qui ronge la prime en route (chocs, chrono, ou les deux).
    taxi: {
      ramasser: 'client',
      destination: 'ailleurs',
      pris: 'DIRECTION : ',
      fini: 'COURSE',
    },
    pizza: {
      // ⚠️ Pas de ramassage : on part avec les boites. La seule pression du
      // boulot, c'est que la pizza REFROIDIT — et trois livraisons de suite.
      ramasser: null,
      destination: 'ailleurs',
      pris: 'LIVRAISON : ',
      fini: 'LIVRAISON',
    },
    ambulance: {
      // Le blesse se ramasse comme un client, mais lui se PERD : passe le
      // chrono, il ne se releve pas, et il ne reste que la base.
      ramasser: 'blesse',
      destination: 'hopital',
      pris: 'A L’HOPITAL, VITE',
      fini: 'TRANSPORT',
    },
    remorquage: {
      // ⚠️ Ce qu'on ramasse est deja AU CROCHET : le bouton du klaxon accroche
      // (`Vehicules.basculerCrochet`) avant d'appeler le boulot, donc dans la
      // meme pression on accroche l'epave et on prend le contrat. Et la
      // fourriere ne paie que les EPAVES — trainer une berline saine au lot,
      // c'est du vol, pas du remorquage.
      ramasser: 'crochet',
      destination: 'fourriere',
      pris: 'A LA FOURRIERE',
      fini: 'REMORQUAGE',
    },
  };

  const boulot = {
    slug: null,            // le boulot en cours, ou null
    etape: null,           // null | 'ramasse' | 'route'
    client: null,          // le pieton a prendre (taxi, ambulance)
    destination: null,     // { x, y, nom }
    distance: 0, chocsDepart: 0, t: 0, etapesFaites: 0, gagne: 0,
    //: Combien de fois chaque boulot a ete FINI. ⚠️ Un compteur par sorte :
    //: le defi « trois courses » de M6 compte des courses de taxi, et une
    //: pizza livree n'en est pas une.
    faits: { taxi: 0, pizza: 0, ambulance: 0, remorquage: 0 },

    fiche: function () { return boulot.slug ? B.defs.economie.boulots[boulot.slug] : null; },

    /** Ce que le HUD doit montrer : le point vers lequel on roule. */
    get cible() {
      if (boulot.etape === 'ramasse') return boulot.client;
      return boulot.etape === 'route' ? boulot.destination : null;
    },

    /** Le klaxon dans un char qui a un boulot : on le prend, ou rien. */
    klaxon: function (v) {
      if (!v || !v.def.boulot) return false;
      // ⚠️ UN contrat a la fois — et sur un char a sirene, ca se DIT : le
      // bouton vient d'allumer la sirene, il a donc l'air d'avoir fait
      // quelque chose, et un refus muet passerait pour une panne. Dans un
      // taxi, on se tait : le klaxon y sert a la circulation, et le repeter a
      // chaque coup de klaxon serait du harcelement.
      if (boulot.etape) { if (v.def.sirene) Hud.message('UN CONTRAT EST DEJA EN COURS'); return false; }
      const sorte = SORTES[v.def.boulot];
      if (!sorte) return false;          // le remorquage attend sa fourriere
      if (sorte.ramasser === 'crochet') {
        if (!v.remorque) return false;                    // `basculerCrochet` l'a deja dit
        if (v.remorque.etat !== 'epave') { Hud.message('LA FOURRIERE NE PAIE QUE LES EPAVES'); return false; }
      }
      boulot.slug = v.def.boulot;
      boulot.etape = 'ramasse';
      boulot.t = 0; boulot.etapesFaites = 0; boulot.gagne = 0;
      if (!sorte.ramasser || sorte.ramasser === 'crochet') { boulot.enRoute(v); return true; }
      boulot.client = boulot.poser(v, sorte.ramasser);
      if (!boulot.client) { boulot.abandonner(); return false; }
      Hud.message(sorte.ramasser === 'blesse' ? 'QUELQU’UN EST A TERRE' : 'UN CLIENT ATTEND');
      return true;
    },

    /** Le quidam qu'on va chercher : un passant qui hele, ou un blesse. */
    poser: function (v, quoi) {
      const place = Entites.placeDeNaissance();
      const x = place ? place.x : v.x + Math.cos(v.angle) * 80;
      const y = place ? place.y : v.y + Math.sin(v.angle) * 80;
      const e = Entites.creerPieton(x, y, Entites.archetypeDeRue());
      if (!e) return null;
      e.etat = 'fige'; e.cri = 9999; e.client = true;
      if (quoi === 'blesse') {
        // ⚠️ Il est A TERRE, pas debout : c'est ce qui le distingue d'un
        // client de taxi a douze pixels de distance. Et il NE SE RELEVE PAS —
        // un assomme se remet debout au bout de `ko_images` et s'enfuit ; un
        // blesse attend l'ambulance. Le seul chrono qui compte est celui du
        // boulot.
        Entites.assommer(e);
        e.minuterie = 99999;
        e.vie = Math.max(1, Math.round(e.vieMax * 0.15));
        Entites.bulle(e, '…');
      } else {
        const civil = Histoire.personnage('civil');
        Entites.bulle(e, civil ? civil.heler : '');
      }
      return e;
    },

    /** On est charge : on choisit ou aller, et le chrono part. */
    enRoute: function (v) {
      const sorte = SORTES[boulot.slug];
      let lieu = null;
      if (sorte.destination === 'hopital') {
        lieu = Monde.carte.points.find(function (p) { return p.slug === 'hopital'; });
      } else if (sorte.destination === 'fourriere' && Monde.carte.fourriere) {
        // La grille du lot : la seule ouverture, et c'est par la qu'on entre.
        const g = Monde.carte.fourriere.grille;
        lieu = { x: g.x + Math.floor(g.largeur / 2), y: g.y, nom: 'Fourrière municipale' };
      }
      if (!lieu) {
        const loin = Monde.carte.points.filter(function (p) { return dist2(p.x * TT, p.y * TT, v.x, v.y) > 200 * 200; });
        lieu = loin[Math.floor(B.rng() * loin.length)] || Monde.carte.points[0];
      }
      boulot.destination = { x: lieu.x * TT + 8, y: lieu.y * TT + 8, nom: lieu.nom };
      boulot.distance = Math.hypot(boulot.destination.x - v.x, boulot.destination.y - v.y);
      boulot.chocsDepart = v.chocs;
      boulot.t = 0;
      boulot.etape = 'route';
      Hud.message(sorte.pris + (sorte.destination === 'ailleurs' ? lieu.nom.toUpperCase() : ''), 180);
    },

    /** Ce qui reste de la prime : les chocs la mangent, le chrono la fait
        fondre. ⚠️ Les deux nombres viennent de la fiche du boulot — un chrono
        a zero veut dire « rien ne fond », pas « tout est perdu ». */
    prime: function (v) {
      const f = boulot.fiche();
      if (!f || !f.prime) return 0;
      const chocs = Math.max(0, v.chocs - boulot.chocsDepart);
      let part = Math.max(0, 1 - chocs * f.malus_choc);
      if (f.chrono_s > 0) part *= Math.max(0, 1 - boulot.t / (f.chrono_s * 60));
      return Math.round(f.prime * part);
    },

    maj: function () {
      if (!boulot.etape) return;
      const j = B.joueur, v = j.dansVehicule;
      const sorte = SORTES[boulot.slug];
      boulot.t++;
      if (!v || v.def.boulot !== boulot.slug || v.etat === 'epave') { boulot.abandonner('BOULOT PERDU'); return; }
      if (boulot.etape === 'ramasse') {
        const c = boulot.client;
        if (!c || !c.vivant) { boulot.abandonner('IL N’EST PLUS LA'); return; }
        if (dist2(v.x, v.y, c.x, c.y) < 40 * 40 && Math.abs(v.vitesse) < 0.4) {
          Entites.retirer(c);
          boulot.client = null;
          boulot.enRoute(v);
          Son.SFX.porte('vehicule');    // il monte et la portiere claque
        }
        return;
      }
      if (sorte.ramasser === 'crochet' && !v.remorque) { boulot.abandonner('EPAVE PERDUE'); return; }
      const d = boulot.destination;
      // ⚠️ Au lot, on livre DANS LA COUR, pas a 44 px d'un point : la grille
      // est une ouverture de quatre tuiles, et une remorqueuse de 36 px avec
      // son epave au bout ne s'arrete pas au pixel pres dessus.
      const arrive = sorte.destination === 'fourriere' ? dansLaCour(v) : dist2(v.x, v.y, d.x, d.y) < 44 * 44;
      if (!arrive || Math.abs(v.vitesse) >= 0.4) return;
      if (sorte.ramasser === 'crochet') {
        // L'epave part a la ferraille : le lot la prend, il ne la range pas.
        const epave = v.remorque;
        Vehicules.decrocher(v);
        Entites.retirer(epave);
      }
      const f = boulot.fiche();
      // ⚠️ La distance se paie A CHAQUE ETAPE : trois livraisons, trois
      // trajets. Sinon la pizza rapporterait trois fois la premiere course.
      const prix = Math.round(f.base + f.par_tuile * (boulot.distance / TT));
      const prime = boulot.prime(v);
      boulot.gagne += prix + prime;
      boulot.etapesFaites++;
      // Le blesse qu'on n'a pas sorti a temps : il ne reste que la base.
      const perdu = f.chrono_s > 0 && sorte.destination === 'hopital' && prime === 0;
      if (boulot.etapesFaites < f.etapes) {
        encaisser(prix + prime, sorte.fini + ' ' + boulot.etapesFaites + '/' + f.etapes);
        boulot.enRoute(v);
        return;
      }
      encaisser(prix + prime, perdu ? sorte.fini + ' — TROP TARD' : (prime ? sorte.fini + ' + ' + prime + ' $' : sorte.fini));
      boulot.faits[boulot.slug]++;
      B.partie.stats.courses = (B.partie.stats.courses || 0) + 1;
      boulot.fin();
    },

    /** Range la machine sans rien dire : le boulot est fini, ou il n'y en a pas. */
    fin: function () {
      boulot.slug = null; boulot.etape = null; boulot.destination = null; boulot.client = null;
    },

    abandonner: function (raison) {
      // Sans boulot en cours, il n'y a rien a abandonner : on se tait.
      const encours = !!boulot.etape;
      if (boulot.client) {
        boulot.client.etat = 'flane'; boulot.client.cri = 0; boulot.client.client = false;
        Entites.taire(boulot.client);
      }
      boulot.fin();
      if (raison && encours) Hud.message(raison);
    },
  };

  // --- La fourriere -----------------------------------------------------------------

  /** Le char qu'on te prend quand on t'embarque : celui que tu conduisais.

      ⚠️ `j.dansVehicule` est deja nul a l'arrestation — la police te SORT du
      char avant de te passer les menottes. C'est donc le DERNIER char conduit
      qui compte, et seulement s'il est encore la, a portee de vue. */
  function charSaisissable(j) {
    const v = j.dansVehicule || j.dernierVehicule;
    if (!v || !v.def || !v.actif || v.etat === 'epave') return null;
    if (dist2(v.x, v.y, j.x, j.y) > 220 * 220) return null;
    if (estDeLaPlanque(v)) return null;      // la sauvegarde de Martin, jamais
    return v;
  }

  /** Le lot prend le char. Il garde `places` chars ; au-dela, le plus vieux part. */
  function saisir(v) {
    if (!v || !v.def) return false;
    const f = B.defs.economie.fourriere, p = B.partie;
    p.fourriere.push({ slug: v.slug, couleur: v.couleur, vie: Math.max(1, Math.round(v.vie)), vole: !!v.vole });
    while (p.fourriere.length > f.places) p.fourriere.shift();
    if (B.joueur && B.joueur.dansVehicule === v) Vehicules.descendre(B.joueur, true);
    Entites.retirer(v);
    return true;
  }

  /** Ce qu'il en coute pour le ravoir. ⚠️ Le calcul est celui de Python
      (`economie.prix_rachat`) : il DOIT rester plus cher que la revente du
      meme char au garage, sinon la fourriere devient une machine a argent. */
  function prixRachat(slug) {
    const f = B.defs.economie.fourriere, def = Vehicules.vehiculeDef(slug);
    if (!def) return f.rachat_minimum;
    return Math.max(f.rachat_minimum, Math.round(def.prix * f.rachat_fraction));
  }

  /*: Les cases de stationnement, par glyphe : le nez du char y pointe. Un
    char DANS sa case n'est jamais mal gare, quoi qu'il bloque — c'est la place
    qu'on lui a dessinee. */
  const CASES_DE_STATIONNEMENT = { '^': 1, 'v': 1, '<': 1, '>': 1 };

  /** Est-il MAL GARE ? ⚠️ La fourriere promettait cette regle depuis M9 et
      elle n'existait nulle part.

      Depuis que les stationnements ont de vraies **cases**, la definition
      tombe toute seule et se teste : est mal gare un char **laisse hors d'une
      case ET qui gene**. Ce qui gene, c'est la chaussee (la ou personne ne
      s'arrete), un passage pieton (la ou les gens traversent) et le devant
      d'une porte (la ou les gens sortent). Un char range sur une ruelle, sur
      du stationnement, ou dans sa case, ne se fait JAMAIS remorquer — meme
      mal aligne, meme depuis trois jours.

      ⚠️ On regarde TOUTES les tuiles que le char couvre, pas son centre : un
      char de 48 px en travers d'un passage pieton a son centre sur le
      trottoir, et il bloque quand meme le passage. */
  function malGare(v) {
    if (!v || !v.def || v.conducteur || v.etat === 'epave') return false;
    if (v.saisi !== null && v.saisi !== undefined) return false;   // deja au lot
    if (estDeLaPlanque(v)) return false;
    const demi = Math.max(v.def.longueur, v.def.largeur) / 2;
    let gene = false;
    for (let ty = Math.floor((v.y - demi) / TT); ty <= Math.floor((v.y + demi) / TT); ty++) {
      for (let tx = Math.floor((v.x - demi) / TT); tx <= Math.floor((v.x + demi) / TT); tx++) {
        if (CASES_DE_STATIONNEMENT[Monde.glyphe(tx, ty)]) return false;
        if (Monde.estChaussee(tx, ty) || Monde.estPassage(tx, ty) || Monde.porteA(tx, ty + 1)) gene = true;
      }
    }
    return gene;
  }

  /** Le char gare devant la planque. ⚠️ Il ne se fait JAMAIS remorquer ni
      saisir, quoi qu'il arrive : c'est la sauvegarde de Martin, et un char qui
      disparait de devant chez soi n'est pas une regle de jeu, c'est une perte. */
  function estDeLaPlanque(v) {
    const garde = B.partie.planque.vehicule;
    return !!(garde && garde.slug === v.slug && dist2(v.x, v.y, garde.x, garde.y) < 40 * 40);
  }

  /** La remorqueuse municipale, une fois par seconde. */
  function majMalGares() {
    if (B.interieur || B.t % 60 !== 0) return;
    const delai = B.defs.economie.fourriere.remorquage_s;
    for (const v of B.entites) {
      if (v.type !== 'vehicule' || !v.laisse) continue;
      if (!malGare(v)) { v.malGareT = 0; continue; }
      v.malGareT = (v.malGareT || 0) + 1;
      // ⚠️ On PREVIENT : sans avertissement, un char qui disparait pendant
      // qu'on fait une course passe pour un bogue, pas pour une regle.
      if (v.malGareT === 1 && Entites.visibleAEcran(v.x, v.y, 120)) {
        Hud.message('MAL GARÉ — LA FOURRIÈRE VA PASSER', 240);
      }
      if (v.malGareT < delai) continue;
      const nom = v.def.nom.toUpperCase();
      saisir(v);
      Hud.message(nom + ' REMORQUÉ — À LA FOURRIÈRE', 240);
    }
  }

  /** Dans la cour du lot, au pixel : c'est ce qui decide si on livre une
      epave, et si on est en train d'en sortir un char sans payer. */
  function dansLaCour(e) {
    const lot = Monde.carte.fourriere;
    if (!lot) return false;
    const tx = e.x / TT, ty = e.y / TT;
    return tx >= lot.x && tx < lot.x + lot.largeur && ty >= lot.y && ty < lot.y + lot.hauteur;
  }

  /** Un char saisi qui franchit la cloture avec le joueur au volant : le lot
      appelle, et les gars du lot ripostent.

      ⚠️ C'est la MOITIE de ce qui rend la fourriere interessante — l'autre
      etant le comptoir. Le grillage s'enjambe a pied et arrete les chars ;
      il n'y a qu'une grille ; donc sortir sans payer, c'est passer devant les
      gardiens. Rien ici ne teste la cloture : la geometrie du lot suffit. */
  function majFourriere() {
    const j = B.joueur, v = j && j.dansVehicule;
    if (!v || v.saisi === null || v.saisi === undefined || B.interieur) return;
    if (dansLaCour(v)) return;
    const rang = v.saisi;
    v.saisi = null;
    v.vole = true;
    if (rang < B.partie.fourriere.length) B.partie.fourriere.splice(rang, 1);
    // Les rangs des autres chars de la cour glissent d'un cran : sans ca, le
    // comptoir libererait le mauvais char au prochain rachat.
    for (const e of B.entites) {
      if (e.type === 'vehicule' && e.saisi !== null && e.saisi !== undefined && e.saisi > rang) e.saisi--;
    }
    Police.signalerCrime('fourriere', v.x, v.y, true);
    // ⚠️ Et un PLANCHER d'etoiles, pas de la chaleur : le lot APPELLE. Sans
    // ca, sortir un char sans payer posait 35 points sur les 100 d'une etoile
    // — il fallait le faire trois fois pour que quiconque se deplace, et la
    // moitie de l'interet de la fourriere tombait.
    Police.etoilesAuMoins(B.defs.economie.fourriere.etoiles_vol);
    // ⚠️ Les gardiens se lancent APRES `alerter` : celui-ci repasse sur tout
    // le monde autour et remplace l'etat de qui n'est ni en fuite ni temoin —
    // il effacait donc leur riposte a l'image meme ou on la posait.
    Entites.alerter(v.x, v.y, j, 1);
    for (const e of B.entites) {
      if (e.type === 'pieton' && e.gardien && e.vivant) { e.etat = 'attaque_joueur'; e.menace = j; e.cri = 90; }
    }
    Hud.message('LE LOT APPELLE LA POLICE', 240);
  }

  /** Pose les chars saisis dans la cour, sur les cases du lot — et les gars
      du lot a la grille. */
  function garnirLaFourriere() {
    const lot = Monde.carte.fourriere;
    if (!lot || !lot.places || !lot.places.length) return 0;
    const arch = Entites.archetype('gardien');
    // ⚠️ Idempotent : `commencer()` garnit la cour, et un rechargement ou un
    // test peuvent la garnir encore. Deux fois les gardiens, c'est quatre gars
    // a la grille — et deux fois les chars, c'est un char par-dessus l'autre.
    const deja = B.entites.filter(function (e) { return e.type === 'pieton' && e.gardien; }).length;
    const n = Math.max(0, B.defs.economie.fourriere.gardiens - deja);
    for (let i = 0; arch && i < n; i++) {
      // Un a chaque bout de la grille, une tuile en dedans, face a la rue.
      const gx = i === 0 ? lot.grille.x : lot.grille.x + lot.grille.largeur - 1;
      const g = Entites.creerPieton(gx * TT + 8, (lot.grille.y - 1) * TT + 8, arch);
      if (!g) continue;
      g.etat = 'fige'; g.face = 'bas'; g.gardien = true; g.poste = { x: g.x, y: g.y };
    }
    let poses = 0;
    const dejaPoses = B.entites.filter(function (e) { return e.type === 'vehicule' && e.saisi !== null && e.saisi !== undefined; }).length;
    B.partie.fourriere.forEach(function (c, i) {
      if (i < dejaPoses) return;                 // deja dans la cour
      const place = lot.places[i % lot.places.length];
      const def = Vehicules.vehiculeDef(c.slug);
      if (!def) return;
      const angle = place.sens === 'N' ? -Math.PI / 2 : place.sens === 'S' ? Math.PI / 2 : place.sens === 'O' ? Math.PI : 0;
      const v = Vehicules.creer(c.slug, place.x * TT + 8, place.y * TT + 8, angle, { etat: 'stationne' });
      if (!v) return;
      v.couleur = c.couleur; v.swaps = { c: c.couleur };
      v.vie = Math.max(1, c.vie); v.vole = !!c.vole;
      v.saisi = i;                    // son rang dans le lot : le comptoir s'y retrouve
      poses++;
    });
    return poses;
  }

  /** Le comptoir du lot : on rachete, et le char est dehors dans la cour. */
  function menuFourriere(items) {
    const p = B.partie;
    if (!p.fourriere.length) {
      items.push({ libelle: 'LE LOT EST VIDE', actif: false });
      return { titre: 'FOURRIERE MUNICIPALE', items: items, aide: 'ON T’Y AMENE CE QU’ON TE SAISIT' };
    }
    p.fourriere.slice().reverse().forEach(function (c) {
      const def = Vehicules.vehiculeDef(c.slug);
      const prix = prixRachat(c.slug);
      items.push({ libelle: (def ? def.nom : c.slug).toUpperCase(), detail: prix + ' $', actif: p.argent >= prix,
                   faire: function () { return racheter(c, prix); } });
    });
    return { titre: 'FOURRIERE MUNICIPALE', items: items,
             sur: p.argent + ' $ · ' + p.fourriere.length + '/' + B.defs.economie.fourriere.places,
             aide: 'UN CHAR RACHETE T’ATTEND DANS LA COUR' };
  }

  function racheter(c, prix) {
    const p = B.partie;
    if (p.argent < prix) { Son.SFX.erreur(); return false; }
    const i = p.fourriere.indexOf(c);
    if (i < 0) return false;
    payer(prix, 'FOURRIERE');
    p.fourriere.splice(i, 1);
    // ⚠️ Un char rachete n'est plus vole : on vient d'en payer la sortie
    // devant un guichet municipal, avec son numero au registre.
    c.vole = false;
    (B.exterieur ? B.exterieur.entites : B.entites).forEach(function (e) {
      if (e.type === 'vehicule' && e.saisi === i) { e.saisi = null; e.vole = false; e.aToi = true; }
    });
    Hud.message('CHAR RACHETE — IL EST DANS LA COUR');
    Son.SFX.argent();
    return true;
  }

  // --- Les points d'action des interieurs --------------------------------------------

  //: ⚠️ Un type de point sans libelle ici, ou sans cas dans `menuDuPoint`, est
  //: un comptoir qu'on touche pour rien. Le juge du banc les compare a ceux que
  //: `carte.INTERIEURS` declare : on ne peut plus dessiner un comptoir mort.
  const LIBELLES = {
    lit: 'DORMIR', coffre: 'COFFRE', garde_robe: 'GARDE-ROBE', vendre: 'VENDRE LE CHAR', reparer: 'REPARER',
    repeindre: 'REPEINDRE', acheter: 'ACHETER', hotdog: 'MANGER', soigner: 'SE FAIRE SOIGNER', caisse: 'LA CAISSE',
    journal: 'LE CLAIRON', contact: 'PARLER', sergent: 'PARLER', casier: 'LE CARNET',
    emplettes: 'ACHETER', salon: 'SE FAIRE COIFFER', escalier: 'MONTER', fouiller: 'FOUILLER',
    fourriere: 'LE LOT', avocat: 'PARLER A L’AVOCAT', hacker: 'LE COMPTOIR DU FOND',
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
        // Le casse-croute : le hot-dog, la poutine, la soupe, la liqueur — et
        // le cafe, sinon la roulotte du trottoir est le seul endroit du jeu ou
        // courir plus longtemps s'achete, et elle ferme.
        [['HOT-DOG', 'hotdog'], ['POUTINE', 'poutine'], ['SOUPE AUX POIS', 'soupe'], ['LIQUEUR', 'liqueur']].forEach(function (d) {
          items.push({ libelle: d[0], detail: tarifs[d[1]] + ' $ / +' + tarifs[d[1] + '_pv'] + ' PV +' + tarifs[d[1] + '_souffle'] + ' SOUFFLE',
                       actif: p.argent >= tarifs[d[1]],
                       faire: function () { payer(tarifs[d[1]], d[0]); soigner(B.joueur, tarifs[d[1] + '_pv']); nourrir(B.joueur, tarifs[d[1] + '_souffle']); Son.SFX.argent(); return false; } });
        });
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
      case 'fourriere':
        return menuFourriere(items);
      case 'avocat':
        return menuAvocat();
      case 'hacker':
        return menuHacker();
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
    // ⚠️ LE CARNET DOIT DIRE CE QUE LE CASIER COUTE. Il pesait deja sur
    // l'amende et le pot-de-vin ; depuis M11 il allonge aussi la portee du
    // cone des agents — et une regle qu'on subit sans jamais la lire n'est pas
    // une regle, c'est une malchance. Le pourcentage est donc ici, a cote du
    // dossier qui le produit.
    const vu = Math.round((Police.porteeDuCasier() - 1) * 100);
    return { titre: 'LE CARNET', items: [
      { libelle: 'DOSSIER', detail: p.casier + ' / ' + eco.casier_max, actif: false },
      { libelle: 'ON TE RECONNAIT', detail: vu > 0 ? '+' + vu + ' % DE LOIN' : 'PAS ENCORE', actif: false },
      { libelle: 'ARRESTATIONS', detail: '' + p.stats.arrestations, actif: false },
      { libelle: 'CRIMES VUS', detail: '' + p.stats.crimes, actif: false },
      { libelle: 'CHARS VOLES', detail: '' + p.stats.volees, actif: false },
      { libelle: 'LA PROCHAINE AMENDE', detail: amende(p.argent, 1, p.casier) + ' $', actif: false },
    ], aide: 'UN DOSSIER EPAIS COUTE PLUS CHER, ET SE VOIT DE PLUS LOIN' };
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

  /** A qui est ce char, si ce n'est pas a toi — le nom a dire, ou null.

      ⚠️ Ti-Guy achete n'importe quel char gare devant sa porte, et c'est
      exactement la que dort le taxi de Marco (M3 le pose a `porte:garage`).
      Vendu, il sort du monde : l'objectif attend un char qui n'existe plus,
      la mission ne RATE meme pas — elle reste prise, le telephone ne sonne
      plus, et il faut se faire arreter pour s'en sortir. Deux raisons de
      refuser, donc, et elles ne se recouvrent pas : un char de mission
      EN COURS (`mission`), et un char PRETE (`aQui`, pose par la fiche et
      jamais efface — le taxi reste a Marco une fois M3 finie). */
  function aQui(v) {
    if (v.aQui) { const p = Histoire.personnage(v.aQui); return (p ? p.nom : v.aQui).toUpperCase(); }
    return v.mission ? 'QUELQU’UN D’AUTRE' : null;
  }

  function menuGarage(items) {
    const eco = B.defs.economie, p = B.partie, v = charDevant();
    if (!v) {
      items.push({ libelle: 'GARE UN CHAR DEVANT LA PORTE', actif: false });
      return { titre: 'GARAGE ROCCO BANDINI', items: items };
    }
    const vente = prixDeVente(v);
    const reparation = Math.round((v.vieMax - v.vie) * eco.reparation_par_pv);
    const proprio = aQui(v);
    items.push({ libelle: 'VENDRE ' + v.def.nom.toUpperCase(),
                 detail: proprio ? 'IL EST À ' + proprio : vente + ' $', actif: !proprio && vente > 0, faire: function () {
      if (aQui(v)) { Son.SFX.erreur(); return false; }
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
    // ⚠️ LE REPLI « RIEN A SIGNALER » DEVIENT UNE LECON. Le jeu a des boulots
    // au klaxon, une fourriere, un marche noir, des proprietes — et rien
    // n'explique rien : M1 apprend a marcher et a voler un char, apres quoi le
    // joueur est tout seul. Un matin ou il ne s'est rien passe est exactement
    // la place libre, et elle ne coute pas une fenetre de plus.
    //
    // ⚠️ On n'enseigne QUE ce qu'il n'a pas encore fait (`cle`), et jamais deux
    // fois la meme (`leconsLues`, gardee dans la partie). Quand il n'y a plus
    // rien a apprendre, le repli redevient « rien a signaler » — et c'est une
    // bonne nouvelle.
    if (choisie === regles[regles.length - 1]) {
      if (!p.leconsLues) p.leconsLues = [];
      const lecon = (B.defs.journal_lecons || []).find(function (l) {
        return p.leconsLues.indexOf(l.slug) < 0 && !(s[l.cle] > 0);
      });
      if (lecon) { p.leconsLues.push(lecon.slug); choisie = lecon; }
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
    // ⚠️ La ville se repare AU LEVER DU JOUR, pas dans la minute : ce qu'on a
    // casse reste casse, et le quartier porte ses blessures jusqu'au matin.
    // C'est ce qui fait qu'une nuit de folie SE VOIT.
    Entites.reparerLeDecor();
    revenusDuJour();
    const m = manchetteDuJour();
    if (m) { B.partie.derniereManchette = m; direLaManchette(m); }
    else Hud.message('JOUR ' + B.partie.jour);
  }

  // --- Effacer le casier : la certitude, ou le pari ---------------------------------------

  /** Ce que le comptoir demande, dossier en main. ⚠️ Rien ne se calcule ici :
      le serveur descend la table `prix_effacer[quoi][casier]`, et le prix monte
      avec l'epaisseur du dossier comme l'amende. */
  function prixEffacer(quoi) {
    const eco = B.defs.economie;
    const table = (eco.prix_effacer || {})[quoi] || [];
    return table[borner(B.partie.casier, 0, eco.casier_max)] || 0;
  }

  function pages(n) { return n + ' PAGE' + (n > 1 ? 'S' : ''); }

  /** Me Desjardins, au fond du Brouillard : cher, sur, une page, une fois par
      jour. ⚠️ C'est la MOITIE d'un choix — l'autre est au comptoir du fond de
      La Shop, et aucun des deux n'a de sens sans l'autre. Seul, l'un ou
      l'autre serait un bouton « annuler la partie ». */
  function menuAvocat() {
    const p = B.partie, fiche = B.defs.economie.effacer.avocat;
    const prix = prixEffacer('avocat'), items = [];
    const occupe = p.nettoyage.avocatJour === p.jour;
    items.push({ libelle: 'TON DOSSIER', detail: pages(p.casier), actif: false });
    items.push({
      libelle: 'EFFACER ' + pages(fiche.pages),
      detail: occupe ? 'PAS AVANT DEMAIN' : (p.casier ? prix + ' $' : 'RIEN A EFFACER'),
      actif: !occupe && p.casier > 0 && p.argent >= prix,
      faire: function () {
        payer(prix, 'ME DESJARDINS');
        p.casier = Math.max(0, p.casier - fiche.pages);
        p.nettoyage.avocatJour = p.jour;
        Son.SFX.argent();
        Hud.message('UNE PAGE DE MOINS — DOSSIER ' + pages(p.casier));
        return true;
      }
    });
    // ⚠️ L'AUTRE MOITIE DE CE QU'IL VEND. Une provision retenue d'avance :
    // la prochaine arrestation ne coute pas d'amende. Elle ne touche a rien
    // d'autre — la page s'ajoute, les armes partent, le char va au lot — et
    // elle prend SA JOURNEE, comme l'effacement : on choisit lequel des deux
    // on lui achete aujourd'hui, et c'est ce choix-la qui fait le comptoir.
    const provision = B.defs.economie.prix_provision[borner(p.casier, 0, B.defs.economie.casier_max)];
    items.push({
      libelle: 'RETENIR SES SERVICES',
      detail: p.nettoyage.provision ? 'DEJA RETENU' : (occupe ? 'PAS AVANT DEMAIN' : provision + ' $'),
      actif: !occupe && !p.nettoyage.provision && p.argent >= provision,
      faire: function () {
        payer(provision, 'ME DESJARDINS');
        p.nettoyage.provision = true;
        p.nettoyage.avocatJour = p.jour;
        Son.SFX.argent();
        Hud.message('IL SERA LA — LA PROCHAINE SANS AMENDE');
        return true;
      }
    });
    return { titre: 'ME DESJARDINS', items: items, sur: p.argent + ' $',
             aide: 'CHER, SUR, ET JAMAIS DEUX FOIS LE MEME JOUR' };
  }

  /** Le comptoir du fond, chez Turcotte. ⚠️ On paie D'AVANCE et on revient
      LE LENDEMAIN : le tirage n'a lieu qu'a la deuxieme visite, et le trajet
      de nuit jusqu'a La Shop fait partie du prix. */
  function menuHacker() {
    const p = B.partie, fiche = B.defs.economie.effacer.hacker;
    const prix = prixEffacer('hacker'), items = [], cmd = p.nettoyage.commande;
    items.push({ libelle: 'TON DOSSIER', detail: pages(p.casier), actif: false });
    if (cmd && p.jour < cmd.jour) {
      items.push({ libelle: 'IL Y TRAVAILLE', detail: 'REVIENS DEMAIN', actif: false });
      return { titre: 'LE COMPTOIR DU FOND', items: items, sur: p.argent + ' $',
               aide: 'TU AS PAYE ' + cmd.paye + ' $ — TU SAURAS DEMAIN' };
    }
    if (cmd) {
      items.push({ libelle: 'PRENDRE LES NOUVELLES', faire: nouvellesDuHacker });
      return { titre: 'LE COMPTOIR DU FOND', items: items, sur: p.argent + ' $',
               aide: 'IL A FINI — RESTE A SAVOIR CE QU’IL A FAIT' };
    }
    items.push({
      libelle: 'ENTRER DANS LE FICHIER',
      detail: p.casier ? prix + ' $ D’AVANCE' : 'RIEN A EFFACER',
      actif: p.casier > 0 && p.argent >= prix,
      faire: function () {
        payer(prix, 'LE COMPTOIR DU FOND');
        p.nettoyage.commande = { jour: p.jour + fiche.delai_jours, paye: prix };
        Son.SFX.argent();
        Hud.message('IL Y TRAVAILLE — REVIENS DEMAIN');
        return true;
      }
    });
    return { titre: 'LE COMPTOIR DU FOND', items: items, sur: p.argent + ' $',
             aide: 'MOINS CHER QUE L’AVOCAT, ET TU NE SAIS PAS CE QUE TU ACHETES' };
  }

  /** Le tirage : autant de pages, autant de chances. ⚠️ Un nombre NEGATIF est
      une page DE PLUS — il s'est fait prendre les doigts dans le fichier, et
      c'est ce qui empeche le comptoir du fond de devenir un bouton « annuler
      la partie ». La table vient du serveur ; le navigateur n'invente rien. */
  function tirerLeHacker() {
    const tirage = B.defs.economie.effacer.hacker.tirage;
    let r = B.rng(), somme = 0;
    for (let i = 0; i < tirage.length; i++) {
      somme += tirage[i][1];
      if (r < somme) return tirage[i][0];
    }
    return tirage[tirage.length - 1][0];
  }

  function nouvellesDuHacker() {
    const p = B.partie, eco = B.defs.economie;
    p.nettoyage.commande = null;
    const n = tirerLeHacker();
    if (n > 0) {
      const avant = p.casier;
      p.casier = Math.max(0, p.casier - n);
      Hud.message(pages(avant - p.casier) + ' DE MOINS — DOSSIER ' + pages(p.casier));
      Son.SFX.argent();
    } else if (n < 0) {
      p.casier = Math.min(eco.casier_max, p.casier + 1);
      Hud.message('IL S’EST FAIT PRENDRE — UNE PAGE DE PLUS');
      Son.SFX.erreur();
    } else {
      Hud.message('IL N’A RIEN PU FAIRE');
      Son.SFX.erreur();
    }
    return true;
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
    if (etal) {
      const c = commerceDe(etal.slug);
      B.invite = c ? c.nom.toUpperCase() + ' — ' + prixAmbulant(j, c) + ' $' + (coupon(j, c.slug) < 1 ? ' (COUPON)' : '') : 'ACHETER';
      return;
    }
    const temoin = Entites.pietonsAutour(j.x, j.y, B.defs.recherche.police.silence_rayon_px).find(function (e) {
      return e.etat === 'temoin' && e.crime && !e.crime.rapporte;
    });
    if (temoin) { B.invite = 'ACHETER SON SILENCE — ' + B.defs.economie.tarifs.silence_temoin + ' $'; return; }
    // L'homme-sandwich : l'invite nomme le kiosque pour lequel il crie.
    const crieur = crieurSousLaMain(j);
    if (crieur) { const c = commerceDe(crieur.kiosque); B.invite = 'PRENDRE LE COUPON' + (c ? ' — ' + c.nom.toUpperCase() : ''); return; }
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
    // Les coupons des hommes-sandwichs expirent pareil : au volant aussi.
    if (B.joueur && B.joueur.coupons) {
      for (const slug in B.joueur.coupons) if (--B.joueur.coupons[slug] <= 0) delete B.joueur.coupons[slug];
    }
    boulot.maj();
    majFourriere();
    majMalGares();
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
           coupon, prixAmbulant, crieurSousLaMain, prendreCoupon,
           boulot, arrestation, saisir, charSaisissable, prixRachat, garnirLaFourriere, menuFourriere, dansLaCour, majFourriere, malGare, majMalGares, estDeLaPlanque, prison, utiliserPoint, pointSousLaMain, libelleDuPoint, menuDuPoint, acheterPropriete, proprieteDe, possede,
           dormir, porterTenue, fouiller, menuComptoir, menuSalon, menuCasier, charDevant, prixDeVente, menuGarage, menuArmurerie, menuVetements,
           revenusDuJour, manchetteDuJour, lireLeJournal, menuMarcheNoir, ramasserPaquet, majInvite, rabais, maj };
})();
