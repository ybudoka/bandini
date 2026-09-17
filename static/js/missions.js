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
    const facture = Math.max(0, Math.min(argent, Math.max(h.minimum, Math.min(h.maximum, m))));
    return Math.round(facture * avantage('hopital', 1));
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
    if (!ouvert(commerce)) { Hud.message('FERMÉ'); Son.SFX.erreur(); return true; }
    // La cale n'est pas une bouchee : c'est un comptoir, et les caisses vont
    // dans le char d'a cote.
    if (commerce.service === 'contrebande') { Hud.ouvrirMenu(menuContrebande(j, etal)); return true; }
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
  function rabais(cle) {
    const histoire = (B.partie && B.partie.rabais && B.partie.rabais[cle]) || 1;
    // ⚠️ Le rabais de l'histoire et celui d'un palier se MULTIPLIENT : ce sont
    // deux choses qu'on a gagnees separement, et les additionner aurait pu
    // donner un prix negatif.
    return histoire * avantage('rabais', 1);
  }

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
  /** Le stool a portee de main. Meme rayon que le temoin : on n'achete pas un
      silence a travers la rue. */
  function stoolSousLaMain(j) {
    return Entites.pietonsAutour(j.x, j.y, B.defs.recherche.police.silence_rayon_px)
      .find(Police.estStool) || null;
  }

  function interagir(j) {
    // ⚠️ On ne magasine pas avec quelqu'un dans les bras : tant qu'on tient un
    // otage, ACTION ne fait qu'une chose — le lacher.
    if (j.otage) return Combat.lacherOtage(false);
    // Un personnage de l'histoire, un panneau de defi : avant tout le reste.
    const perso = Histoire.personnageSousLaMain(j);
    if (perso) return Histoire.parler(perso.personnage);
    const panneau = Histoire.panneauSousLaMain(j);
    if (panneau) return Histoire.proposerDefi(panneau.defi);
    const etal = Entites.autour(j.x, j.y, 30, function (e) { return e.type === 'ambulant'; })[0];
    if (etal) return acheterAmbulant(j, etal);
    // ⚠️ LES HOMMES DE SAL AVANT TOUT LE MONDE : quand ils sont sur toi, il
    // n'y a rien d'autre a faire de ce bouton-la.
    const homme = collecteurSousLaMain(j);
    // ⚠️ PAR `Hud.ouvrirMenu`, jamais en posant `B.menu` a la main : c'est lui
    // qui donne au menu son curseur. Pose directement, ce comptoir-la s'ouvrait
    // SANS curseur — aucune ligne surlignee, HAUT et BAS le mettaient a NaN,
    // ACTION ne choisissait rien. Le menu le plus tendu du jeu ne se jouait pas.
    if (homme) { Hud.ouvrirMenu(menuDette(homme)); return true; }
    // ⚠️ LE STOOL AVANT LE TEMOIN : lui est en route vers un telephone, l'autre
    // cherche encore un agent. Quand les deux sont a portee, c'est le plus
    // presse qu'on paie.
    const stool = stoolSousLaMain(j);
    if (stool) return Police.acheterLeStool(j, stool);
    // Un temoin qui court raconter : on lui achete le silence.
    const temoin = Entites.pietonsAutour(j.x, j.y, B.defs.recherche.police.silence_rayon_px).find(function (e) {
      return e.etat === 'temoin' && e.crime && !e.crime.rapporte;
    });
    if (temoin) return Police.acheterLeSilence(j, temoin);
    const crieur = crieurSousLaMain(j);
    if (crieur) return prendreCoupon(j, crieur);
    const fille = filleSousLaMain(j);
    if (fille) return compagnie(j, fille);
    // Le guichet : poser un skimmer, ou le vider. ⚠️ Seulement s'il y a
    // quelque chose a y faire — sinon le bouton reste a ce qui suit.
    if (inviteGuichet(j)) return utiliserGuichet(j);
    // La distributrice : son menu, ou la brasser si quelque chose y est reste pris.
    const machine = distributriceSousLaMain(j);
    if (machine) return utiliserDistributrice(j, machine);
    // L'autobus arrete a l'abribus : on monte, on paie. ⚠️ AVANT le bouclier
    // humain et avant la portiere (`Vehicules.maj`) : devant un autobus en
    // service, ACTION veut dire « monter », pas « voler l'autobus ».
    // L'edicule du metro : le tourniquet, puis l'escalier qui descend au quai.
    const edicule = Metro.ediculeSousLaMain(j);
    if (edicule) return Metro.descendre(j, edicule);
    // Le petit train arrêté en gare : on monte faire un tour.
    const manege = Foire.sousLaMain(j);
    if (manege) return Foire.monter(j, manege);
    const autobus = Autobus.autobusSousLaMain(j);
    if (autobus) return Autobus.monter(j, autobus);
    // ⚠️ LE BOUCLIER HUMAIN EN DERNIER, et c'est voulu : on attrape quelqu'un
    // quand ACTION n'avait rien d'autre a faire. Sinon le geste aurait pris
    // Josee en otage au lieu de lui parler. `otageSousLaMain` ecarte aussi la
    // porte, le char et l'arme par terre — eux sont servis par l'appelant,
    // APRES nous, et on leur volerait le bouton.
    //
    // ⚠️ Et c'est PRECISEMENT parce qu'il est le dernier qu'il se TIENT : la
    // pression arme la prise, le maintien la prend (`Combat.majSaisie`). Etre
    // au bout de la chaine, c'est etre ce que le bouton fait quand on ne lui
    // demandait rien — donc par accident, deux etoiles comprises. On rend
    // `true` quand meme : la pression est DEPENSEE, et c'est au RELACHER que
    // `Combat.majSaisie` tranche — tenue, elle prend l'otage ; relachee avant
    // l'heure, c'etait une tape, et elle fait les poches. ⚠️ Rendre `true` sans
    // ce relais, c'etait le bug « je n'arrive plus a voler les gens » : l'arme a
    // la main, toute victime des poches est aussi a portee de bouclier.
    const otage = Combat.otageSousLaMain(j);
    if (otage) return Combat.viserOtage(j);
    return false;
  }

  // --- L'hopital : on ne meurt pas, on paie ------------------------------------------

  /** Le joueur tombe : fondu, reveil DANS un lit de l'hopital, facture, armes
      gardees. */
  function hopital(source) {
    const j = B.joueur;
    if (!j || j.hospitalise) return;
    j.hospitalise = true;
    if (j.dansVehicule) Vehicules.descendre(j, true);
    j.vie = 1; j.vx = 0; j.vy = 0; j.roule = 0; j.etat = 'flane';
    const facture = factureHopital(B.partie.argent);
    payer(facture, 'HÔPITAL');
    B.partie.stats.hospitalisations = (B.partie.stats.hospitalisations || 0) + 1;
    Police.remiseAZero();
    if (boulot.etape) boulot.abandonner();
    if (B.defi) Histoire.finirDefi(false, 'À L’HÔPITAL');
    Histoire.evenement('mort');
    Jeu.transiter(FONDU_ELLIPSE, function () {
      j.vie = j.vieMax; j.saigne = 0; j.endurance = 100; j.cafeine = 0;
      j.surplus = 0;                  // le surplus est passager : il ne survit pas a l'hopital
      // Dans un lit de l'urgence (`Jeu.coucherALHopital`). ⚠️ Une ville sans
      // hopital ou sans lit : devant la porte, comme avant, et un moment
      // d'invincibilite parce qu'on se releve en pleine rue.
      if (!Jeu.coucherALHopital()) {
        const lieu = Monde.carte.points.find(function (p) { return p.slug === 'hopital'; });
        if (lieu) { j.x = lieu.x * TT + 8; j.y = lieu.y * TT + 20; }
        j.invincible = 90;
        Entites.dansLaCarte(j);
        Monde.centrerCamera(j.x, j.y);
      }
      j.hospitalise = false;
    }, 'RÉVEIL À L’HÔPITAL — ' + facture + ' $');
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
      Hud.dialogue('L’AGENT', ['« TU TE PENSES OÙ, TOI? »'], 120);
      prison(agent);
      return true;
    } });
    items.push({ libelle: 'SUIVRE L’AGENT', detail: 'AMENDE ' + fine + ' $', faire: function () { prison(agent); return true; } });
    Hud.ouvrirMenu({ titre: 'ARRÊTÉ !', sur: etoiles + ' ÉTOILE' + (etoiles > 1 ? 'S' : ''), items: items,
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
    // ⚠️ La police FOUILLE : arrete avec des caisses, on les perd en entier.
    if (saisi) confisquerLaCargaison(saisi);
    if (saisi) { const nom = saisi.def.nom.toUpperCase(); saisir(saisi); Hud.message(nom + ' À LA FOURRIÈRE', 240); }
    Police.remiseAZero();
    if (boulot.etape) boulot.abandonner();
    if (B.defi) Histoire.finirDefi(false, 'EN PRISON');
    Histoire.evenement('arrete');
    if (agent) { agent.etat = 'flane'; agent.but = null; }
    const heures = B.defs.recherche.police.prison_heures / 24;
    p.heure += heures; while (p.heure >= 1) { p.heure -= 1; p.jour += 1; nouveauJour(); }
    Jeu.transiter(FONDU_ELLIPSE, function () {
      // ⚠️ Arrete pendant le fondu de l'hopital, on est deja couche dans son
      // lit (`finirTransition` a fini le reveil) : on se leve, on sort de la
      // piece, et c'est au poste qu'on se reveille — pas dans la piece d'avant.
      if (j.alite) Entites.seLever(j, 0, 0);
      Jeu.quitterLaPiece();
      const poste = Monde.carte.points.find(function (q) { return q.slug === 'poste'; });
      if (poste) { j.x = poste.x * TT + 8; j.y = poste.y * TT + 20; }
      j.vie = j.vieMax; j.invincible = 90; j.saigne = 0; j.arrete = false; j.surplus = 0;
      Entites.dansLaCarte(j);
      Monde.centrerCamera(j.x, j.y);
      sauvegarderPartie();
    }, retenu ? 'PRISON — TON AVOCAT T’A SORTI, ARMES CONFISQUÉES'
              : 'PRISON — ' + fine + ' $, ARMES CONFISQUÉES');
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
      pris: 'À L’HÔPITAL, VITE',
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
      pris: 'À LA FOURRIÈRE',
      fini: 'REMORQUAGE',
    },
  };

  //: A cette distance de sa destination, un boulot est arrive.
  const ARRIVEE_PX = 44;

  /** Ce qu'un char atteint en roulant depuis `v` : rend `(x, y, r)`, vrai si une
      tuile ou il roule est a moins de `r` px de ce pixel. ⚠️ L'eau n'y est pas :
      un char y entre, et il coule. */
  function atteignableEnChar(v) {
    const c = Monde.carte, W = c.w, H = c.h, vu = new Uint8Array(W * H), file = [];
    const roule = function (tx, ty) { return !Monde.bloque(tx, ty, Monde.MASQUE_VEHICULE) && !Monde.estEau(tx, ty); };
    const sx = Math.floor(v.x / TT), sy = Math.floor(v.y / TT);
    if (sx >= 0 && sy >= 0 && sx < W && sy < H) { vu[sy * W + sx] = 1; file.push(sy * W + sx); }
    for (let i = 0; i < file.length; i++) {
      const k = file[i], x = k % W, y = (k - x) / W;
      if (x > 0 && !vu[k - 1] && roule(x - 1, y)) { vu[k - 1] = 1; file.push(k - 1); }
      if (x < W - 1 && !vu[k + 1] && roule(x + 1, y)) { vu[k + 1] = 1; file.push(k + 1); }
      if (y > 0 && !vu[k - W] && roule(x, y - 1)) { vu[k - W] = 1; file.push(k - W); }
      if (y < H - 1 && !vu[k + W] && roule(x, y + 1)) { vu[k + W] = 1; file.push(k + W); }
    }
    return function (px, py, r) {
      const rt = Math.ceil(r / TT);
      const cx = Math.floor(px / TT), cy = Math.floor(py / TT);
      for (let y = Math.max(0, cy - rt); y <= Math.min(H - 1, cy + rt); y++) {
        for (let x = Math.max(0, cx - rt); x <= Math.min(W - 1, cx + rt); x++) {
          if (vu[y * W + x] && dist2(x * TT + 8, y * TT + 8, px, py) < r * r) return true;
        }
      }
      return false;
    };
  }

  const boulot = {
    slug: null,            // le boulot en cours, ou null
    etape: null,           // null | 'ramasse' | 'route'
    client: null,          // le pieton a prendre (taxi, ambulance)
    destination: null,     // { x, y, nom }
    distance: 0, chocsDepart: 0, t: 0, etapesFaites: 0, gagne: 0,
    //: Combien de fois chaque boulot a ete FINI. ⚠️ Un compteur par sorte :
    //: le defi « trois courses » de M6 compte des courses de taxi, et une
    //: pizza livree n'en est pas une.
    //: ⚠️ Lecture seule, et elle vient de la PARTIE : le compte vivait ici et
    //: repartait de zero a chaque rechargement. `histoire.js` la lit pour la
    //: mission des courses, et elle comptait les courses de la session, pas
    //: celles du joueur.
    get faits() { return B.partie.boulots; },

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
      if (boulot.etape) { if (v.def.sirene) Hud.message('UN CONTRAT EST DÉJÀ EN COURS'); return false; }
      const sorte = SORTES[v.def.boulot];
      if (!sorte) return false;          // le remorquage attend sa fourriere
      if (sorte.ramasser === 'crochet') {
        if (!v.remorque) return false;                    // `basculerCrochet` l'a deja dit
        if (v.remorque.etat !== 'epave') { Hud.message('LA FOURRIÈRE NE PAIE QUE LES ÉPAVES'); return false; }
      }
      boulot.slug = v.def.boulot;
      boulot.etape = 'ramasse';
      boulot.t = 0; boulot.etapesFaites = 0; boulot.gagne = 0;
      if (!sorte.ramasser || sorte.ramasser === 'crochet') { boulot.enRoute(v); return true; }
      boulot.client = boulot.poser(v, sorte.ramasser);
      if (!boulot.client) { boulot.abandonner('PERSONNE N’ATTEND DANS LE COIN'); return false; }
      Hud.message(sorte.ramasser === 'blesse' ? 'QUELQU’UN EST À TERRE' : 'UN CLIENT ATTEND');
      return true;
    },

    /** Le quidam qu'on va chercher : un passant qui hele, ou un blesse.

        ⚠️ AU BORD DE LA ROUTE, sur le trottoir d'une voie que ce char rejoint
        (`Entites.placeAuBordDeLaRoute`) — pas n'importe ou dans la bulle : on
        le ramasse au volant, a 40 px, et un client dans un parc ne se ramasse
        pas. Le blesse aussi : l'ambulance vient par la rue. Et plus de repli
        « a 80 px devant le capot » : c'etait sur la chaussee, sous les roues. */
    poser: function (v, quoi) {
      const atteint = atteignableEnChar(v);
      const place = Entites.placeAuBordDeLaRoute(function (tx, ty) { return atteint(tx * TT + 8, ty * TT + 8, 1); });
      if (!place) return null;
      const e = Entites.creerPieton(place.x, place.y, Entites.archetypeDeRue());
      if (!e) return null;
      e.etat = 'fige'; e.cri = 9999; e.client = true;
      e.plante = { x: e.x, y: e.y };
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
        Entites.regarder(e, place.rue.x - e.x, place.rue.y - e.y);     // il guette la rue
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
        // ⚠️ SEULEMENT LA OU UN CHAR SE REND. Depuis l'ile, la chapelle
        // Sainte-Anne est un point de la carte comme un autre, et on ne
        // l'atteint qu'a la nage : une course sur dix-sept ne se finissait
        // jamais. La regle est ce dont le boulot a besoin — une route depuis la
        // ou l'on est — et pas « hors de l'ile » : le prochain lieu coupe de la
        // ville s'ecartera tout seul.
        const atteint = atteignableEnChar(v);
        const loin = Monde.carte.points.filter(function (p) {
          return dist2(p.x * TT, p.y * TT, v.x, v.y) > 200 * 200 && atteint(p.x * TT + 8, p.y * TT + 8, ARRIVEE_PX);
        });
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
      // Le palier de pourboire : le meilleur debloque, jamais la somme.
      return Math.round(f.prime * part * avantage('prime', 1));
    },

    maj: function () {
      if (!boulot.etape) return;
      const j = B.joueur, v = j.dansVehicule;
      const sorte = SORTES[boulot.slug];
      boulot.t++;
      if (!v || v.def.boulot !== boulot.slug || v.etat === 'epave') { boulot.abandonner('BOULOT PERDU'); return; }
      if (boulot.etape === 'ramasse') {
        const c = boulot.client;
        if (!c || !c.vivant) { boulot.abandonner('IL N’EST PLUS LÀ'); return; }
        if (dist2(v.x, v.y, c.x, c.y) < 40 * 40 && Math.abs(v.vitesse) < 0.4) {
          Entites.retirer(c);
          boulot.client = null;
          boulot.enRoute(v);
          Son.SFX.porte('vehicule');    // il monte et la portiere claque
        }
        return;
      }
      if (sorte.ramasser === 'crochet' && !v.remorque) { boulot.abandonner('ÉPAVE PERDUE'); return; }
      const d = boulot.destination;
      // ⚠️ Au lot, on livre DANS LA COUR, pas a 44 px d'un point : la grille
      // est une ouverture de quatre tuiles, et une remorqueuse de 36 px avec
      // son epave au bout ne s'arrete pas au pixel pres dessus.
      const arrive = sorte.destination === 'fourriere' ? dansLaCour(v) : dist2(v.x, v.y, d.x, d.y) < ARRIVEE_PX * ARRIVEE_PX;
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
      compterLeBoulot(boulot.slug);
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
    p.fourriere.push({ slug: v.slug, sprite: v.sprite, couleur: v.couleur, vie: Math.max(1, Math.round(v.vie)), vole: !!v.vole });
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
    const part = avantage('fourriere', 1);     // les gars du lot te connaissent
    if (!def) return Math.round(f.rachat_minimum * part);
    return Math.round(Math.max(f.rachat_minimum, Math.round(def.prix * f.rachat_fraction)) * part);
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
      const v = Vehicules.creer(c.slug, place.x * TT + 8, place.y * TT + 8, angle, { etat: 'stationne', sprite: c.sprite });
      if (!v) return;
      // ⚠️ `nuances`, pas `{ c: couleur }` : le rehaut et l'ombre suivent la
      // couleur. Sans eux, une auto bleue revenait du lot avec le toit et le
      // cadre des vitres de la palette — rouges.
      v.couleur = c.couleur; v.swaps = nuances(c.couleur);
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
      return { titre: 'FOURRIÈRE MUNICIPALE', items: items, aide: 'ON T’Y AMÈNE CE QU’ON TE SAISIT' };
    }
    p.fourriere.slice().reverse().forEach(function (c) {
      const def = Vehicules.vehiculeDef(c.slug);
      const prix = prixRachat(c.slug);
      items.push({ libelle: (def ? def.nom : c.slug).toUpperCase(), detail: prix + ' $', actif: p.argent >= prix,
                   faire: function () { return racheter(c, prix); } });
    });
    return { titre: 'FOURRIÈRE MUNICIPALE', items: items,
             sur: p.argent + ' $ · ' + p.fourriere.length + '/' + B.defs.economie.fourriere.places,
             aide: 'UN CHAR RACHETÉ T’ATTEND DANS LA COUR' };
  }

  function racheter(c, prix) {
    const p = B.partie;
    if (p.argent < prix) { Son.SFX.erreur(); return false; }
    const i = p.fourriere.indexOf(c);
    if (i < 0) return false;
    payer(prix, 'FOURRIÈRE');
    p.fourriere.splice(i, 1);
    // ⚠️ Un char rachete n'est plus vole : on vient d'en payer la sortie
    // devant un guichet municipal, avec son numero au registre.
    c.vole = false;
    (B.exterieur ? B.exterieur.entites : B.entites).forEach(function (e) {
      if (e.type === 'vehicule' && e.saisi === i) { e.saisi = null; e.vole = false; e.aToi = true; }
    });
    Hud.message('CHAR RACHETÉ — IL EST DANS LA COUR');
    Son.SFX.argent();
    return true;
  }

  // --- Les points d'action des interieurs --------------------------------------------

  //: ⚠️ Un type de point sans libelle ici, ou sans cas dans `menuDuPoint`, est
  //: un comptoir qu'on touche pour rien. Le juge du banc les compare a ceux que
  //: `carte.INTERIEURS` declare : on ne peut plus dessiner un comptoir mort.
  const LIBELLES = {
    lit: 'DORMIR', coffre: 'COFFRE', garde_robe: 'GARDE-ROBE', vendre: 'VENDRE LE CHAR', reparer: 'RÉPARER',
    repeindre: 'REPEINDRE', acheter: 'ACHETER', hotdog: 'MANGER', soigner: 'SE FAIRE SOIGNER', caisse: 'LA CAISSE',
    journal: 'LE CLAIRON', contact: 'PARLER', sergent: 'PARLER', casier: 'LE CARNET',
    emplettes: 'ACHETER', salon: 'SE FAIRE COIFFER', escalier: 'MONTER', fouiller: 'FOUILLER',
    fourriere: 'LE LOT', avocat: 'PARLER À L’AVOCAT', hacker: 'LE COMPTOIR DU FOND',
    distributrice: 'LA MACHINE',
    // Le metro : monter dans la rame au quai, en descendre dans la rame.
    rame: 'LA RAME',
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
    if (point.type === 'rame') return Metro.utiliser(j, point);
    if (point.type === 'fouiller') return fouiller(point);
    // ⚠️ La machine AVANT le menu : si quelque chose y est reste pris, ACTION la
    // brasse — l'invite l'a promis.
    if (point.type === 'distributrice') return utiliserDistributrice(j, machineDuPoint(point));
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

  /** La propriete de ce lieu si elle se vend aujourd'hui, sinon null. */
  function aVendre(lieu) {
    const prop = proprieteDe(lieu);
    return prop && prop.phase === 1 && !possede(prop) ? prop : null;
  }

  /** L'entree de menu « acheter » d'une propriete a vendre.

      ⚠️ DEDANS, au comptoir (retour de Martin : « pour acheter un commerce
      c'est a l'interieur »). La porte ouvrait un menu ACHETER / ENTRER sur le
      trottoir ; elle n'est plus qu'une porte. */
  function itemAchat(prop) {
    const p = B.partie;
    return { libelle: 'ACHETER LE COMMERCE', detail: prop.prix + ' $', actif: p.argent >= prop.prix, faire: function () {
      payer(prop.prix, prop.nom.toUpperCase());
      p.proprietes[prop.slug] = { jour: p.jour, caisse: 0 };
      Hud.message(prop.nom.toUpperCase() + ' EST À TOI', 180);
      return true;
    } };
  }

  function menuDuPoint(point) {
    const items = [];
    const menu = menuDuComptoir(point, items);
    const prop = aVendre(B.interieur.slug);
    // L'achat se fait la ou la caisse se prendra une fois le commerce a soi :
    // dans les menus batis sur `items` (l'avocat a sa table n'en est pas un).
    // ⚠️ EN DERNIER : le curseur s'ouvre sur la premiere ligne qui se choisit,
    // et au garage, deux pressions d'ACTION pour vendre un char auraient paye
    // le garage 4500 $.
    if (menu && prop && menu.items === items) {
      items.push(itemAchat(prop));
      menu.aide = menu.aide || prop.revenu_par_jour + ' $ PAR JOUR, À RAMASSER SUR PLACE';
      menu.sur = menu.sur || B.partie.argent + ' $';
    }
    return menu;
  }

  function menuDuComptoir(point, items) {
    const piece = B.interieur, p = B.partie, tarifs = B.defs.economie.tarifs;
    const caisse = itemCaisse(piece.slug);
    if (caisse) items.push(caisse);
    // La run : le prix du jour, et « vendre » ce qu'il y a dans le char devant.
    itemsRevente(piece).forEach(function (i) { items.push(i); });
    switch (point.type) {
      case 'lit':
        items.push({ libelle: 'DORMIR JUSQU’AU MATIN', detail: 'SAUVEGARDE', faire: function () { dormir(); return true; } });
        // ⚠️ La sieste n'est offerte que LE JOUR, et la question se pose
        // DEHORS : dans la piece, `estNuit()` dit toujours non. Offerte le
        // jour, elle ne passe jamais minuit — ni dette, ni revenus, ni
        // skimmers de plus. Et elle vient APRES le matin : la main qui
        // appuie deux fois pour dormir retrouve la ligne qu'elle connait.
        if (!Monde.estNuit(p.heure) && p.heure < B.defs.economie.sieste.reveil) {
          items.push({ libelle: 'DORMIR JUSQU’AU SOIR', detail: 'SAUVEGARDE', faire: function () { dormirJusquAuSoir(); return true; } });
        }
        items.push({ libelle: 'SAUVEGARDER SEULEMENT', faire: function () { sauvegarderPartie(); Hud.message('PARTIE SAUVEGARDÉE'); return true; } });
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
        return { titre: 'HÔPITAL DE BAIE-DES-BRUMES', items: items, sur: p.argent + ' $' };
      }
      case 'caisse':
        if (!caisse && !aVendre(piece.slug)) items.push({ libelle: 'CE N’EST PAS À TOI', actif: false });
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
      case 'distributrice':
        return menuDistributrice(machineDuPoint(point));
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
      items.push(itemBouchee(a));
    });
    return { titre: piece.nom.toUpperCase(), items: items, sur: p.argent + ' $' };
  }

  /** Une bouchee, au comptoir comme a la machine : le prix, ce qu'elle rend, le geste.

      ⚠️ `servir` (facultatif) passe ENTRE la caisse et la bouche. La machine
      distributrice s'en sert pour decider, une fois l'argent pris, si la
      canette tombe — il rend faux quand rien n'est servi, et on a paye pour
      rien. C'est une seule fonction pour les deux, parce que le jour ou une
      liqueur change de prix, le comptoir et la machine doivent le dire
      ensemble. */
  function itemBouchee(a, servir) {
    const p = B.partie, tarifs = B.defs.economie.tarifs;
    const prix = Math.round(tarifs[a.tarif] || 0);
    const gains = [];
    if (a.gain_pv) gains.push('+' + tarifs[a.gain_pv] + ' PV');
    if (a.gain_souffle) gains.push('+' + tarifs[a.gain_souffle] + ' SOUFFLE');
    return { libelle: a.nom.toUpperCase(), detail: prix + ' $' + (gains.length ? ' / ' + gains.join(' ') : ''),
             actif: p.argent >= prix,
             faire: function () {
               payer(prix, a.nom.toUpperCase());
               if (servir) {
                 if (!servir(a)) return true;
                 manger(a);
                 return false;
               }
               manger(a);
               if (a.journal) { lireLeJournal(); return true; }
               Son.SFX.argent();
               return false;
             } };
  }

  /** Ce qu'un article rend a qui le mange : la vie, le souffle, et le cafe. */
  function manger(a) {
    const tarifs = B.defs.economie.tarifs;
    if (a.gain_pv) soigner(B.joueur, tarifs[a.gain_pv]);
    if (a.gain_souffle) nourrir(B.joueur, tarifs[a.gain_souffle]);
    if (a.effet === 'cafe') cafeine(B.joueur);
  }

  /** Une arme au comptoir du quincaillier : la meme que Chez Gus, avec sa marge. */
  function itemArme(article, marge) {
    const p = B.partie, arme = Combat.armeDef(article.arme);
    if (!arme) return { libelle: article.nom.toUpperCase(), actif: false };
    const prix = Math.round(arme.prix * (marge || 1));
    const deja = !!p.armes[article.arme];
    return { libelle: article.nom.toUpperCase(), detail: deja ? 'DÉJÀ À TOI' : prix + ' $',
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
             detail: deja ? (p.tenue === article.tenue ? 'PORTÉE' : 'À TOI') : prix + ' $',
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
                     // ⚠️ Le stool reconnait une FACE : une coupe neuve la defait.
                     Police.onNeTeReconnaitPlus();
                     return true;
                   } });
    });
    return { titre: B.interieur.nom.toUpperCase(), items: items, sur: p.argent + ' $',
             aide: 'CHANGER DE TÊTE FAIT OUBLIER LA TIENNE' };
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
      { libelle: 'ON TE RECONNAÎT', detail: vu > 0 ? '+' + vu + ' % DE LOIN' : 'PAS ENCORE', actif: false },
      { libelle: 'ARRESTATIONS', detail: '' + p.stats.arrestations, actif: false },
      { libelle: 'CRIMES VUS', detail: '' + p.stats.crimes, actif: false },
      { libelle: 'CHARS VOLÉS', detail: '' + p.stats.volees, actif: false },
      { libelle: 'LA PROCHAINE AMENDE', detail: amende(p.argent, 1, p.casier) + ' $', actif: false },
    ].concat(
      // Ce qui est ferme en ville, et pourquoi : la ville est ouverte, mais
      // elle a ses raisons — le carnet les liste.
      Monde.barrieresFermees().map(function (b) { return { libelle: 'FERMÉ — ' + b.nom.toUpperCase(), detail: b.raison, actif: false }; })
    ), aide: 'UN DOSSIER ÉPAIS COÛTE PLUS CHER, ET SE VOIT DE PLUS LOIN' };
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
               { libelle: 'DÉPOSER 100 $', actif: p.argent >= 1, faire: depot(100) },
               { libelle: 'DÉPOSER TOUT', actif: p.argent >= 1, faire: depot(Infinity) },
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
    Police.onNeTeReconnaitPlus();
    return true;
  }

  function menuGardeRobe() {
    const p = B.partie;
    const items = (B.defs.tenues || []).filter(function (t) { return p.tenues.indexOf(t.slug) >= 0; }).map(function (t) {
      return { libelle: t.nom.toUpperCase(), detail: p.tenue === t.slug ? 'PORTÉE' : '', faire: function () { porterTenue(t.slug); return true; } };
    });
    return { titre: 'GARDE-ROBE', items: items, aide: 'CHANGER DE LINGE FAIT OUBLIER TA TÊTE' };
  }

  /** Dormir : la nuit passe, on se reveille au matin, la partie est sauvee.

      ⚠️ La nuit passe AU NOIR, comme l'hopital et la prison : le jour ne
      change pas sous les yeux du joueur, il a change quand la lumiere revient. */
  function dormir() {
    Jeu.transiter(FONDU_NUIT, function () {
      const p = B.partie;
      p.jour += 1;
      p.heure = 0.30;
      seReveiller(B.joueur.vieMax);
      nouveauJour();
      sauvegarderPartie();
    }, 'LE LENDEMAIN MATIN');
  }

  /** Dormir jusqu'au soir : on se reveille a la noirceur, le MEME jour.

      C'est ce qui manquait aux missions de nuit : le lit ne menait qu'au
      matin, et une mission `nuit` prise au reveil faisait attendre quatre
      minutes reelles sous « ATTENDS LA NUIT ». ⚠️ Une sieste n'est pas une
      nuit : elle rend `soin` de la vie maximum, pas tout. Et `Math.max` :
      appelee passe l'heure du reveil, elle ne fait pas reculer le temps. */
  function dormirJusquAuSoir() {
    Jeu.transiter(FONDU_NUIT, function () {
      const p = B.partie, j = B.joueur, sieste = B.defs.economie.sieste;
      p.heure = Math.max(p.heure, sieste.reveil);
      seReveiller(Math.min(j.vieMax, j.vie + Math.round(j.vieMax * sieste.soin)));
      sauvegarderPartie();
    }, 'LE SOIR VENU');
  }

  /** Ce que tout somme rend, la nuit comme la sieste : le souffle, et une
      police qui a lache le morceau. `vie` est ce qu'on a au reveil. */
  function seReveiller(vie) {
    const j = B.joueur;
    j.vie = vie;
    j.endurance = 100;
    j.cafeine = 0;
    j.surplus = 0;           // un somme reprend le souffle, pas l'avance
    B.partie.vie = j.vie;
    Police.remiseAZero();
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

  /** `v` : le char a traiter. Sans lui, celui qui est gare devant la porte des
      pietons (le comptoir, dedans) ; avec lui, celui qui attend devant le rideau
      (`majGarage`), conducteur a bord. */
  function menuGarage(items, vDonne) {
    const eco = B.defs.economie, p = B.partie, v = vDonne || charDevant();
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
      // ⚠️ Vendu DEVANT LE RIDEAU, on est encore au volant : on descend avant
      // que Ti-Guy le rentre, sinon on part avec le char dans la poche.
      if (B.joueur && B.joueur.dansVehicule === v) Vehicules.descendre(B.joueur, true);
      if (B.exterieur) {
        const i = B.exterieur.entites.indexOf(v);
        if (i >= 0) B.exterieur.entites.splice(i, 1);
      } else Entites.retirer(v);
      return true;
    } });
    items.push({ libelle: 'RÉPARER', detail: reparation + ' $', actif: reparation > 0 && p.argent >= reparation, faire: function () {
      payer(reparation, 'RÉPARATION'); v.vie = v.vieMax; return true;
    } });
    items.push({ libelle: 'REPEINDRE (EFFACE LE VOL)', detail: eco.repeinte + ' $', actif: p.argent >= eco.repeinte, faire: function () {
      payer(eco.repeinte, 'PEINTURE');
      const autres = v.def.couleurs.filter(function (c) { return c !== v.couleur; });
      v.couleur = autres.length ? autres[Math.floor(B.rng() * autres.length)] : v.couleur;
      v.swaps = nuances(v.couleur); v.vole = false; v.alarme = 0;
      Police.remiseAZero();
      return true;
    } });
    // L'assurance : Ti-Guy couvre ce qui est gare devant, sans demander a qui
    // c'est. La prime, la valeur couverte, et « deja assure » — une fois.
    const prime = primeAssurance(v), couvre = valeurAssuree(v);
    items.push({ libelle: 'ASSURER ' + v.def.nom.toUpperCase(),
                 detail: v.assure ? 'DÉJÀ ASSURÉ' : (enqueteEnCours() ? 'L’ASSUREUR ENQUÊTE' : prime + ' $ / COUVRE ' + couvre + ' $'),
                 actif: !v.assure && !proprio && !enqueteEnCours() && p.argent >= prime,
                 faire: function () { return assurer(v); } });
    if (p.assurance.du > 0) {
      items.push({ libelle: 'ENCAISSER L’ASSURANCE', detail: p.assurance.du + ' $', actif: true,
                   faire: function () { encaisserAssurance(); return true; } });
    }
    return { titre: 'GARAGE ROCCO BANDINI', items: items, sur: p.argent + ' $' };
  }

  // --- La porte de garage : on se gare devant, le rideau monte, Ti-Guy sort ---------------

  //: A combien de tuiles de la facade le rideau se leve pour un char qui arrive, et
  //: combien de tuiles de cote on tolere : « des qu'on est devant en voiture ».
  const RIDEAU_PORTEE = 4, RIDEAU_MARGE = 1;
  //: La place devant le rideau, en tuiles de profondeur : un char nez au rideau.
  const BAIE_PROFONDEUR = 2;
  //: Sous cette vitesse, le char est GARE — le menu s'ouvre.
  const BAIE_ARRET = 0.3;

  /** Demande de Martin (17 sept. 2026) : « il faut une vraie porte de garage ou
      on stationne pour vendre ou faire des missions. la porte ouvre seule des
      qu'on est devant en voiture. »

      Au volant, devant le rideau : il monte. Arrete dans la baie, rideau leve :
      le menu du garage s'ouvre avec CE char — vendre, reparer, repeindre,
      assurer —, sans descendre ni passer par le comptoir. Une fois par arrivee
      (`servi` : le CHAR servi) : on le ferme, il ne revient pas tant que ce
      char-la n'est pas ressorti de la baie. ⚠️ Le char, pas le conducteur : on
      descend devant le rideau pour entrer au garage a pied, on remonte pour
      repartir — et le menu ne doit pas nous rattraper a la portiere.

      ⚠️ JAMAIS pour le char d'une mission en cours ni pendant une scene : la
      livraison au garage est l'affaire de `Histoire` (elle se fait DEVANT CE
      RIDEAU, `lieuDeLivraison`), et un menu ouvert par-dessus figerait
      l'objectif qu'on vient d'atteindre. */
  function majGarage() {
    const portes = Monde.portesDeGarage();
    if (!portes.length || B.interieur) return;
    const j = B.joueur, v = j && j.dansVehicule;
    for (const pg of portes) {
      if (v && Monde.devantLaPorteDeGarage(pg, v.x, v.y, RIDEAU_PORTEE, RIDEAU_MARGE)) Monde.leverLaPorteDeGarage(pg);
    }
    if (Monde.majPortesDeGarage()) Son.SFX.rideau_garage();
    for (const pg of portes) {
      if (pg.servi && !Monde.devantLaPorteDeGarage(pg, pg.servi.x, pg.servi.y, BAIE_PROFONDEUR, 0)) pg.servi = null;
      if (!v || !Monde.devantLaPorteDeGarage(pg, v.x, v.y, BAIE_PROFONDEUR, 0)) continue;
      if (pg.servi === v || pg.ouverture < 1 || Math.abs(v.vitesse) >= BAIE_ARRET) continue;
      if (B.cinema || B.menu || B.transition || v.mission || v.etat === 'epave') continue;
      pg.servi = v;
      v.vitesse = 0; v.vx = 0; v.vy = 0;
      Hud.ouvrirMenu(menuDuRideau(v));
    }
  }

  /** Le menu du garage, ouvert du volant. ⚠️ REPARTIR EN TETE, et c'est le
      curseur : le menu s'ouvre tout seul au moment ou l'on freine, donc au
      moment ou la main appuie sur ACTION pour descendre — deux pressions
      auraient VENDU le char qu'on voulait seulement garer. */
  function menuDuRideau(v) {
    const items = [{ libelle: 'REPARTIR', faire: function () { return true; } }];
    return menuGarage(items, v);
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
      items.push({ libelle: arme.nom.toUpperCase(), detail: deja ? 'DÉJÀ À TOI' : arme.prix + ' $', actif: !deja && p.argent >= arme.prix,
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
      return { libelle: t.nom.toUpperCase(), detail: deja ? (p.tenue === t.slug ? 'PORTÉE' : 'À TOI') : t.prix + ' $',
               actif: deja || p.argent >= t.prix, faire: function () {
                 if (!deja) { payer(t.prix, t.nom.toUpperCase()); p.tenues.push(t.slug); }
                 porterTenue(t.slug);
                 return true;
               } };
    });
    return { titre: 'BOUTIQUE ROSA', items: items, sur: p.argent + ' $' };
  }

  // --- Les proprietes -------------------------------------------------------------------

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
    else Hud.dialogue('LE CLAIRON DE LA BAIE', ['RIEN À SIGNALER À BAIE-DES-BRUMES.'], 300);
  }

  function nouveauJour() {
    nuitDeLaDette();
    nuitDesSkimmers();
    nuitDeLAssurance();
    // ⚠️ La ville se repare AU LEVER DU JOUR, pas dans la minute : ce qu'on a
    // casse reste casse, et le quartier porte ses blessures jusqu'au matin.
    // C'est ce qui fait qu'une nuit de folie SE VOIT.
    Entites.reparerLeDecor();
    // ⚠️ Et le livreur passe vider les machines : ce qui etait reste pris la
    // veille est parti avec lui.
    B.coincees = {};
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
      detail: occupe ? 'PAS AVANT DEMAIN' : (p.casier ? prix + ' $' : 'RIEN À EFFACER'),
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
      detail: p.nettoyage.provision ? 'DÉJÀ RETENU' : (occupe ? 'PAS AVANT DEMAIN' : provision + ' $'),
      actif: !occupe && !p.nettoyage.provision && p.argent >= provision,
      faire: function () {
        payer(provision, 'ME DESJARDINS');
        p.nettoyage.provision = true;
        p.nettoyage.avocatJour = p.jour;
        Son.SFX.argent();
        Hud.message('IL SERA LÀ — LA PROCHAINE SANS AMENDE');
        return true;
      }
    });
    return { titre: 'ME DESJARDINS', items: items, sur: p.argent + ' $',
             aide: 'CHER, SÛR, ET JAMAIS DEUX FOIS LE MÊME JOUR' };
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
               aide: 'TU AS PAYÉ ' + cmd.paye + ' $ — TU SAURAS DEMAIN' };
    }
    if (cmd) {
      items.push({ libelle: 'PRENDRE LES NOUVELLES', faire: nouvellesDuHacker });
      return { titre: 'LE COMPTOIR DU FOND', items: items, sur: p.argent + ' $',
               aide: 'IL A FINI — RESTE À SAVOIR CE QU’IL A FAIT' };
    }
    items.push({
      libelle: 'ENTRER DANS LE FICHIER',
      detail: p.casier ? prix + ' $ D’AVANCE' : 'RIEN À EFFACER',
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
             aide: 'MOINS CHER QUE L’AVOCAT, ET TU NE SAIS PAS CE QUE TU ACHÈTES' };
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

  // --- Les boulots montent en grade ------------------------------------------------------

  /** ⚠️ **Un boulot qui paie et rien d'autre n'est pas une activite, c'est un
      distributeur.** Les paliers transforment « je fais trois courses pour
      manger » en « j'en fais cinquante parce qu'au bout il y a quelque
      chose » — et ce qu'on gagne n'est presque jamais de l'argent : des points
      de vie, un char gare a la planque, un lot qui ne fait plus payer. */
  function paliersDe(slug) { return (B.defs.economie.paliers || {})[slug] || []; }

  function palierDebloque(slug, palier) {
    return !!(B.partie.paliers && B.partie.paliers[slug + ':' + palier.compte]);
  }

  /** La force d'un avantage, tous boulots confondus. ⚠️ **Le PLUS FORT gagne,
      les paliers ne s'additionnent pas** : sans cette regle, « +10 % puis
      +25 % de vie » ferait +35 %, et la fiche dirait une chose pendant que le
      jeu en ferait une autre. */
  function avantage(type, defaut) {
    const paliers = B.defs.economie.paliers || {};
    let valeur = null;
    for (const slug in paliers) {
      for (const palier of paliers[slug]) {
        if (palier.type !== type || !palierDebloque(slug, palier)) continue;
        // `fourriere` et `hopital` sont des RABAIS : le meilleur est le plus
        // petit. Tout le reste monte.
        if (valeur === null) valeur = palier.valeur;
        else if (type === 'fourriere' || type === 'hopital' || type === 'rabais') valeur = Math.min(valeur, palier.valeur);
        else valeur = Math.max(valeur, palier.valeur);
      }
    }
    return valeur === null ? defaut : valeur;
  }

  /** Un boulot de plus au compteur : on regarde si un palier tombe.

      ⚠️ Un palier ne se donne QU'UNE FOIS, et il est marque dans la partie
      avant que sa recompense soit posee : sinon un char a la planque se
      regarait a chaque sauvegarde. */
  function compterLeBoulot(slug) {
    const p = B.partie;
    p.boulots[slug] = (p.boulots[slug] || 0) + 1;
    for (const palier of paliersDe(slug)) {
      if (p.boulots[slug] !== palier.compte || palierDebloque(slug, palier)) continue;
      p.paliers[slug + ':' + palier.compte] = 1;
      donnerLePalier(palier);
      Hud.message(palier.nom + ' — ' + palier.detail, 300);
      Son.SFX.etoile();
      Histoire.evenement && Histoire.evenement('palier');
    }
  }

  /** Ce qu'un palier POSE tout de suite. Les autres types (prime, rabais,
      fourriere, hopital, vie) ne posent rien : ils se lisent au moment ou
      l'on s'en sert, ce qui evite qu'un avantage vive en deux endroits. */
  function donnerLePalier(palier) {
    if (palier.type !== 'char') return;
    const def = Vehicules.vehiculeDef(palier.valeur);
    if (!def) return;
    const planque = Monde.carte.ville ? Monde.carte.ville : Monde.carte;
    const point = (planque.points || []).find(function (q) { return q.slug === 'planque'; });
    // ⚠️ Il se GARE VRAIMENT : un palier qui promet un char et n'en pose
    // aucun est pire que pas de palier du tout. On le range dans la partie,
    // la ou `Jeu` va le chercher au chargement — comme le char qu'on y laisse.
    B.partie.planque.vehicule = {
      slug: palier.valeur, couleur: def.couleurs ? def.couleurs[0] : null,
      vie: 100, x: point ? point.x * TT + 8 : 0, y: point ? (point.y + 2) * TT : 0,
      angle: 0, vole: false,
    };
  }

  // --- La dette de Rocco : une raison de se lever le matin -------------------------------

  /** ⚠️ **Elle ne se rembourse pas a un comptoir**, et ce n'est pas une
      economie de geographie : un shylock n'attend pas derriere une caisse, il
      ENVOIE DU MONDE. Les rappels arrivent au telephone, puis les hommes de
      Sal te trouvent ou que tu sois — et c'est a eux qu'on paie. La collecte
      est une scene, pas un menu de plus dans une piece. */
  function ficheDette() { return B.defs.economie.dette || null; }

  /** La nuit passe : la dette monte, et elle s'arrete au plafond.

      ⚠️ Le navigateur n'a rien a calculer — le serveur descend `dettes[n]`,
      la borne comprise. On cherche donc la case suivante plutot que de refaire
      l'interet ici : deux formules pour un seul nombre finissent toujours par
      diverger. */
  function detteDuLendemain(dette) {
    const table = B.defs.economie.dettes || [];
    if (!table.length || dette <= 0) return Math.max(0, dette);
    for (let i = 0; i < table.length - 1; i++) {
      if (dette <= table[i]) return Math.min(table[i + 1], table[table.length - 1]);
    }
    return table[table.length - 1];
  }

  function nuitDeLaDette() {
    const p = B.partie, f = ficheDette();
    if (!f || p.dette <= 0) return;
    const avant = p.dette;
    p.dette = detteDuLendemain(p.dette);
    // Le telephone commence a sonner avant que les hommes ne viennent : on a
    // le temps de faire quelque chose, et c'est ce qui en fait une pression
    // plutot qu'une embuscade.
    if (p.jour >= f.rappel_jour && p.rappelJour !== p.jour && p.jour < f.collecte_jour) {
      p.rappelJour = p.jour;
      Son.SFX.telephone();
      Hud.message('SAL : « TU ME DOIS ' + p.dette + ' $ »', 240);
    } else if (p.dette > avant) {
      Hud.message('LA DETTE MONTE — ' + p.dette + ' $', 180);
    }
  }

  function collecteurs() {
    return B.entites.filter(function (e) { return e.collecteur && e.vivant; });
  }

  /** Les hommes de Sal. ⚠️ Ils NAISSENT HORS CHAMP et viennent vers toi : on
      ne les voit pas apparaitre, on les voit arriver. Et une seule visite par
      jour — sans ca, la dette n'est plus une pression, c'est un harcelement
      dont on ne peut rien faire. */
  function envoyerLesCollecteurs() {
    const p = B.partie, f = ficheDette();
    if (!f || p.dette <= 0 || B.interieur) return;
    if (p.jour < f.collecte_jour || p.collecteJour === p.jour) return;
    if (collecteurs().length) return;
    if (B.t < (p.collecteT || 0)) return;
    const arch = Entites.archetype('cravate');
    if (!arch) return;
    let nes = 0;
    for (let i = 0; i < f.hommes; i++) {
      const place = Entites.placeDeNaissance();
      if (!place) continue;
      const e = Entites.creerPieton(place.x, place.y, arch);
      e.collecteur = true;
      // ⚠️ A MAINS NUES OU AU POING AMERICAIN, tour a tour — demande de
      // Martin. Ils ont le corps d'un Cravate, et la fiche du Cravate porte
      // un BATON : sans cette ligne, le recouvrement arrivait la batte a la
      // main, et la laissait par terre quand on le couchait.
      const armes = f.armes && f.armes.length ? f.armes : [''];
      e.arme = armes[nes % armes.length] || null;
      // ⚠️ `mission` : ils ne s'oublient pas hors de la bulle. « Ils te
      // trouvent ou que tu sois » n'est pas une figure de style.
      e.mission = true;
      e.etat = 'attaque_joueur';
      e.cri = 90;
      nes++;
    }
    if (!nes) return;
    p.collecteJour = p.jour;
    Hud.message('LES HOMMES DE SAL SONT LÀ', 240);
  }

  /** Ils te suivent tant que la dette court. ⚠️ `attaque_joueur` abandonne a
      260 px ; eux, non — c'est toute la difference entre une gang de rue et
      un recouvrement. */
  function majCollecteurs() {
    const p = B.partie, f = ficheDette();
    if (!f) return;
    const gens = collecteurs();
    if (p.dette <= 0) {
      gens.forEach(function (e) { e.collecteur = false; e.mission = false; e.etat = 'flane'; });
      return;
    }
    if (!gens.length) { envoyerLesCollecteurs(); return; }
    const j = B.joueur;
    for (const e of gens) {
      if (e.etat === 'flane' || e.etat === 'arret') e.etat = 'attaque_joueur';
      // Au contact, ils se servent. ⚠️ ET CA COMPTE SUR LA DETTE : des hommes
      // de main qui volent sans rien effacer seraient un impot, pas un
      // recouvrement — et le joueur n'aurait aucune raison de les laisser
      // approcher plutot que de fuir chaque fois.
      if (e.preleveT > 0) { e.preleveT--; continue; }
      if (!j || j.dansVehicule || B.interieur) continue;
      if (Math.hypot(e.x - j.x, e.y - j.y) > 22) continue;
      const pris = Math.min(p.argent, Math.round(p.argent * f.prend));
      e.preleveT = 180;
      if (pris <= 0) continue;
      p.argent -= pris;
      rembourser(pris, 'ILS SE SERVENT');
    }
  }

  /** Payer. ⚠️ La dette ne descend jamais sous zero, et le jour ou elle y
      arrive les hommes rentrent chez eux — c'est la seule chose qui les fait
      partir pour de bon. */
  function rembourser(montant, raison) {
    const p = B.partie;
    montant = Math.max(0, Math.min(p.dette, Math.round(montant)));
    if (!montant) return 0;
    p.dette -= montant;
    Hud.message((raison || 'SUR LA DETTE') + ' — ' + montant + ' $, RESTE ' + p.dette + ' $', 200);
    if (p.dette <= 0) {
      p.dette = 0;
      collecteurs().forEach(function (e) { e.collecteur = false; e.mission = false; e.etat = 'flane'; });
      B.partie.collecteT = B.t + (ficheDette().repit_s || 120) * 60;
      Hud.message('LA DETTE DE ROCCO EST RÉGLÉE', 300);
      Son.SFX.argent();
      Histoire.evenement && Histoire.evenement('dette_reglee');
    }
    return montant;
  }

  function collecteurSousLaMain(j) {
    if (!j || B.interieur) return null;
    return Entites.pietonsAutour(j.x, j.y, 26).find(function (e) {
      return e.collecteur && e.vivant;
    }) || null;
  }

  /** Ce qu'on peut leur donner, en main propre. */
  function menuDette(e) {
    const p = B.partie, f = ficheDette();
    const items = [];
    items.push({ libelle: 'LA DETTE', detail: p.dette + ' $', actif: false });
    [f.acompte_min, f.acompte_min * 4, p.dette].forEach(function (montant, i) {
      const m = Math.min(p.dette, Math.round(montant));
      if (!m || (i === 2 && m <= f.acompte_min * 4)) return;
      if (items.some(function (q) { return q.montant === m; })) return;
      items.push({ libelle: i === 2 ? 'TOUT RÉGLER' : 'DONNER ' + m + ' $', montant: m,
                   detail: m + ' $', actif: p.argent >= m,
                   faire: function () {
                     payer(m, 'SUR LA DETTE');
                     rembourser(m, 'À SES HOMMES');
                     B.partie.collecteT = B.t + (f.repit_s || 120) * 60;
                     collecteurs().forEach(function (q) { q.collecteur = false; q.mission = false; q.etat = 'flane'; });
                     Son.SFX.argent();
                     return true;
                   } });
    });
    return { titre: 'LES HOMMES DE SAL', items: items, sur: p.argent + ' $',
             aide: 'UN ACOMPTE LES RENVOIE POUR AUJOURD’HUI' };
  }

  // --- Les guichets : au camion, ou au skimmer ---------------------------------------------

  /** Le guichet a portee de main — debout, dehors, et pas deja defonce. */
  function guichetSousLaMain(j) {
    if (B.interieur || j.dansVehicule) return null;
    return Entites.decorAutour(j.x, j.y, 22).find(function (d) { return d.decor === 'guichet' && !d.brise; }) || null;
  }

  function tuileDe(e) { return Math.floor(e.x / TT) + ',' + Math.floor(e.y / TT); }

  function skimmerA(g) {
    const cle = tuileDe(g);
    return B.partie.skimmers.find(function (s) { return s.cle === cle; }) || null;
  }

  /** Ce qu'ACTION ferait a ce guichet — le libelle de l'invite, ou null s'il
      n'y a rien a y faire. ⚠️ UNE SEULE fonction pour l'invite et le geste :
      une invite qui annonce autre chose que ce qu'ACTION va faire est pire
      que pas d'invite du tout. */
  function inviteGuichet(j) {
    const g = guichetSousLaMain(j);
    if (!g) return null;
    const p = B.partie, fiche = B.defs.economie.guichet.skimmer, s = skimmerA(g);
    if (s && s.pret) return 'VIDER LE SKIMMER — ' + s.monte + ' $';
    if (s) return 'SKIMMER POSÉ — REVIENS DEMAIN';
    if ((p.objets.skimmer || 0) > 0 && p.skimmers.length < fiche.max_poses) return 'POSER UN SKIMMER';
    return null;
  }

  function utiliserGuichet(j) {
    const g = guichetSousLaMain(j);
    if (!g) return false;
    const p = B.partie, fiche = B.defs.economie.guichet.skimmer, s = skimmerA(g);
    j.animT = 10; j.animType = 'ramasse';
    if (s && s.pret) {
      encaisser(s.monte, 'SKIMMER');
      p.skimmers.splice(p.skimmers.indexOf(s), 1);
      return true;
    }
    if (s) { Hud.message('REVIENS DEMAIN'); return true; }
    if ((p.objets.skimmer || 0) <= 0 || p.skimmers.length >= fiche.max_poses) return false;
    p.objets.skimmer -= 1;
    p.skimmers.push({ cle: tuileDe(g), x: g.x, y: g.y, jour: p.jour, monte: 0, pret: false });
    Hud.message('SKIMMER POSÉ — REVIENS DEMAIN', 180);
    return true;
  }

  /** La nuit des skimmers : chacun lit, ou se fait trouver. Rend combien
      ont ete trouves. ⚠️ Les des viennent de la fiche, pas d'ici. */
  function nuitDesSkimmers() {
    const p = B.partie, fiche = B.defs.economie.guichet.skimmer;
    let trouves = 0;
    for (let i = p.skimmers.length - 1; i >= 0; i--) {
      const s = p.skimmers[i];
      if (s.pret) continue;
      if (B.rng() < fiche.trouve) { p.skimmers.splice(i, 1); trouves++; continue; }
      s.monte = fiche.rendement[0] + Math.floor(B.rng() * (fiche.rendement[1] - fiche.rendement[0] + 1));
      s.pret = true;
    }
    if (trouves) Hud.message(trouves > 1 ? trouves + ' SKIMMERS ONT ÉTÉ TROUVÉS' : 'UN SKIMMER A ÉTÉ TROUVÉ', 180);
    return trouves;
  }

  /** Un guichet qui cede : la caisse par terre, en liasses, un delit a deux
      etoiles — et le skimmer qui y etait est parti avec la caisse. Appele par
      `Entites.briser`, quoi que ce soit qui l'ait ouvert. */
  function guichetCasse(g) {
    const fiche = B.defs.economie.guichet, p = B.partie;
    const total = fiche.caisse[0] + Math.floor(B.rng() * (fiche.caisse[1] - fiche.caisse[0] + 1));
    let reste = total;
    for (let i = 0; i < fiche.liasses; i++) {
      const part = i === fiche.liasses - 1 ? reste : Math.round(total / fiche.liasses);
      reste -= part;
      const a = B.rng() * Math.PI * 2, d = 6 + B.rng() * 14;
      Entites.creer('ramassage', g.x + Math.cos(a) * d, g.y + 4 + Math.sin(a) * d * 0.6,
                    { r: 4, objet: 'billets', montant: part, t: 0, solide: false });
    }
    const cle = tuileDe(g);
    p.skimmers = p.skimmers.filter(function (s) { return s.cle !== cle; });
    Police.signalerCrime('guichet', g.x, g.y, Police.quelqu_un_voit(g.x, g.y, null));
    Son.SFX.argent();
    return total;
  }

  /** Les liasses se ramassent en passant dessus, comme les paquets — et la
      monnaie d'une distributrice aussi. Ses canettes et ses sacs, eux, se
      mangent sur place : ce qu'ils rendent est celui de l'article. */
  function ramasserLesBillets(j) {
    for (const e of Entites.autour(j.x, j.y, 14, function (q) {
      return q.type === 'ramassage' && (q.objet === 'billets' || q.objet === 'monnaie');
    })) {
      encaisser(e.montant, e.objet === 'monnaie' ? 'MONNAIE' : 'LIASSE');
      Entites.retirer(e);
    }
    for (const e of Entites.autour(j.x, j.y, 14, function (q) {
      return q.type === 'ramassage' && (q.objet === 'canette' || q.objet === 'sac');
    })) {
      const a = articleDe(e.sorte, e.article);
      if (a) { manger(a); Hud.message(a.nom.toUpperCase()); }
      Son.SFX.ramasse();
      Entites.retirer(e);
    }
  }

  // --- Les machines distributrices ----------------------------------------------------------

  /** Une machine : sa sorte, sa fiche (`magasins.DISTRIBUTRICES`), et une CLE.

      ⚠️ La cle, pas l'entite : dedans, la machine est un point du plan que la
      piece refait a chaque entree ; dehors, c'est un decor que la nuit remet
      debout. Ce qui est reste pris dans la spirale tient donc sur la cle
      (`B.coincees`), et pas sur un objet qui ne vivra pas jusqu'a demain. */
  function machine(sorte, cle, x, y) {
    const fiche = (B.defs.distributrices || {})[sorte];
    return fiche ? { sorte: sorte, fiche: fiche, cle: cle, x: x, y: y } : null;
  }

  function machineDuPoint(point) {
    return machine(point.sorte, (B.interieur ? B.interieur.slug : 'piece') + ':' + point.x + ',' + point.y,
                   point.x * TT + 8, point.y * TT + 8);
  }

  function articleDe(sorte, slug) {
    const fiche = (B.defs.distributrices || {})[sorte];
    return (fiche && fiche.articles.find(function (a) { return a.slug === slug; })) || null;
  }

  /** La distributrice a portee de main : celle de la salle d'attente (un point
      du plan), ou celle de la rue (un decor debout et pas defonce). ⚠️ Meme
      rayon que le guichet, et c'est pour ca que la ville ne les colle pas. */
  function distributriceSousLaMain(j) {
    if (!j || j.dansVehicule) return null;
    if (B.interieur) {
      const point = pointSousLaMain(j);
      return point && point.type === 'distributrice' ? machineDuPoint(point) : null;
    }
    // ⚠️ LA PORTE D'ABORD. Une machine a moins de 22 px de la tuile ou l'on
    // pousse une porte lui volait ACTION : l'invite disait MACHINE A CAFE devant
    // l'entree d'un commerce. La ville ne les colle plus (`carte.distributrices`),
    // et ceci est le filet pour tout ce qu'on posera demain a cote d'une porte.
    if (Monde.porteDevant(j)) return null;
    const d = Entites.decorAutour(j.x, j.y, 22).find(function (q) {
      return !q.brise && (DECORS[q.decor] || {}).distributrice;
    });
    return d ? machine(DECORS[d.decor].distributrice, 'rue:' + tuileDe(d), d.x, d.y) : null;
  }

  /** Ce qui est reste pris dans cette machine-la (le slug de l'article), ou null. */
  function coincee(m) { return (m && B.coincees && B.coincees[m.cle]) || null; }

  /** ⚠️ UNE SEULE fonction pour l'invite et le geste, comme au guichet. */
  function inviteDistributrice(m) {
    if (!m) return null;
    return coincee(m) ? 'BRASSER LA MACHINE' : m.fiche.nom.toUpperCase();
  }

  function utiliserDistributrice(j, m) {
    if (!m) return false;
    j.animT = 10; j.animType = 'ramasse';
    if (coincee(m)) return brasser(m);
    const menu = menuDistributrice(m);
    menu.refaire = function () { return menuDistributrice(m); };
    Hud.ouvrirMenu(menu);
    return true;
  }

  /** Le menu de la machine : ses articles, au prix du comptoir. ⚠️ La spirale
      decide APRES qu'on a paye — c'est tout le drame de la machine
      distributrice — et une canette restee prise ferme le menu : il y a
      maintenant une machine a brasser. */
  function menuDistributrice(m) {
    const items = m.fiche.articles.map(function (a) {
      return itemBouchee(a, function () {
        if (B.rng() < B.defs.economie.distributrice.coincee) {
          B.coincees = B.coincees || {};
          B.coincees[m.cle] = a.slug;
          Hud.message(m.fiche.coincee, 180);
          Son.SFX.erreur();
          return false;
        }
        Son.SFX.distributrice();
        return true;
      });
    });
    return { titre: m.fiche.nom.toUpperCase(), items: items, sur: B.partie.argent + ' $' };
  }

  /** Brasser la machine : une fois sur `brasser`, ce qui etait pris tombe. */
  function brasser(m) {
    const a = articleDe(m.sorte, coincee(m));
    Son.SFX.machine_brassee();
    if (B.rng() >= B.defs.economie.distributrice.brasser && a) {
      Hud.message('ÇA TIENT ENCORE');
      return true;
    }
    delete B.coincees[m.cle];
    if (a) { manger(a); Hud.message(m.fiche.tombe); Son.SFX.distributrice(); }
    return true;
  }

  /** Une distributrice qui cede : sa monnaie par terre en tas, ses canettes
      avec, et ce qui etait reste pris dedans part avec le reste. Un delit a une
      etoile — et seulement si un temoin va le raconter. Appele par
      `Entites.briser`, quoi que ce soit qui l'ait ouverte. */
  function distributriceCassee(d) {
    const fiche = B.defs.economie.distributrice, sorte = (DECORS[d.decor] || {}).distributrice;
    const m = machine(sorte, 'rue:' + tuileDe(d), d.x, d.y);
    const total = fiche.monnaie[0] + Math.floor(B.rng() * (fiche.monnaie[1] - fiche.monnaie[0] + 1));
    // ⚠️ Vers le SUD, jamais dans le mur : la machine est adossee a une devanture.
    function parTerre(objet, champs) {
      const a = B.rng() * Math.PI, r = 6 + B.rng() * 12;
      Entites.creer('ramassage', d.x + Math.cos(a) * r, d.y + 4 + Math.sin(a) * r * 0.6,
                    Object.assign({ r: 4, objet: objet, t: 0, solide: false }, champs));
    }
    let reste = total;
    for (let i = 0; i < fiche.tas; i++) {
      const part = i === fiche.tas - 1 ? reste : Math.round(total / fiche.tas);
      reste -= part;
      parTerre('monnaie', { montant: part });
    }
    if (m && m.fiche.recrache && m.fiche.objet) {
      for (let i = 0; i < fiche.canettes; i++) {
        parTerre(m.fiche.objet, { sorte: sorte, article: m.fiche.articles[i % m.fiche.articles.length].slug });
      }
    }
    if (m && B.coincees) delete B.coincees[m.cle];
    Police.signalerCrime('distributrice', d.x, d.y, Police.quelqu_un_voit(d.x, d.y, null));
    Son.SFX.monnaie();
    return total;
  }

  // --- L'assurance : la fraude, et l'assureur qui enquete ----------------------------------

  function valeurAssuree(v) {
    const a = B.defs.economie.assurance;
    return Math.min(a.valeur_max, Math.round(v.def.prix * a.valeur_fraction));
  }

  function primeAssurance(v) { return Math.round(valeurAssuree(v) * B.defs.economie.assurance.prime_fraction); }

  function enqueteEnCours() {
    const p = B.partie;
    return p.assurance.enquete > 0 && p.jour < p.assurance.enquete;
  }

  /** Ti-Guy couvre ce char : la prime part, la valeur couverte reste sur le
      char. ⚠️ Pas deux fois, pas un char prete ou de mission, pas pendant
      une enquete. */
  function assurer(v) {
    if (!v || v.assure || aQui(v) || enqueteEnCours()) return false;
    const prime = primeAssurance(v);
    if (!payer(prime, 'PRIME')) return false;
    v.assure = { valeur: valeurAssuree(v), jour: B.partie.jour };
    return true;
  }

  /** Un char assure qui disparait : la reclamation s'ouvre, a encaisser au
      garage. ⚠️ A la `reclamations_max`-ieme, l'assureur enquete : plus de
      police jusqu'au jour dit, et une page au casier. */
  function charPerdu(v) {
    const p = B.partie, a = B.defs.economie.assurance;
    if (!v.assure) return false;
    p.assurance.du += v.assure.valeur;
    p.assurance.reclamations += 1;
    v.assure = null;
    if (p.assurance.reclamations >= a.reclamations_max) {
      p.assurance.enquete = p.jour + a.enquete_jours;
      p.casier = Math.min(B.defs.economie.casier_max, p.casier + a.enquete_pages);
      Hud.message('L’ASSUREUR ENQUÊTE', 240);
    } else {
      Hud.message('CHAR ASSURÉ — PASSE AU GARAGE', 180);
    }
    return true;
  }

  function encaisserAssurance() {
    const p = B.partie;
    if (p.assurance.du <= 0) return false;
    encaisser(p.assurance.du, 'ASSURANCE');
    p.assurance.du = 0;
    return true;
  }

  /** Le dossier se classe le jour dit : on repart a zero. */
  function nuitDeLAssurance() {
    const p = B.partie;
    if (p.assurance.enquete > 0 && p.jour >= p.assurance.enquete) {
      p.assurance.enquete = 0;
      p.assurance.reclamations = 0;
      Hud.message('L’ASSUREUR A CLASSÉ LE DOSSIER', 180);
    }
  }

  // --- La run : la contrebande de Sven, d'un district a l'autre ----------------------------

  /** Le char a portee de la cale : le plus proche dans `rayon` px, pas une
      epave, pas conduit par le trafic. ⚠️ C'est LUI qui porte les caisses :
      la cale ne se porte pas, et un char qui brule brule la run avec. */
  function charPres(x, y, rayon) {
    let meilleur = null, dMin = rayon * rayon;
    for (const e of B.entites) {
      if (e.type !== 'vehicule' || !e.actif || e.etat === 'epave' || e.conducteur === 'trafic') continue;
      const d = dist2(e.x, e.y, x, y);
      if (d < dMin) { dMin = d; meilleur = e; }
    }
    return meilleur;
  }

  function caissesDe(v) {
    let n = 0;
    if (v && v.cargaison) for (const m in v.cargaison) n += v.cargaison[m];
    return n;
  }

  /** Ce qu'on a deja achete AUJOURD'HUI : le prix monte avec, et le compteur
      repart chaque matin. */
  function acheteesAujourdhui() {
    const p = B.partie;
    if (p.contrebande.jour !== p.jour) { p.contrebande.jour = p.jour; p.contrebande.achetees = 0; }
    return p.contrebande.achetees;
  }

  function prixAchat(slug) {
    const c = B.defs.economie.contrebande, m = c.marchandises[slug];
    return Math.round(m.achat * (1 + c.hausse * acheteesAujourdhui()));
  }

  /** Le prix du jour d'une marchandise dans un district : entre `facteur[0]`
      et `facteur[1]` fois le prix de vente, tire du JOUR et du district — le
      meme pour tous les comptoirs du district, et il bouge chaque nuit.
      ⚠️ `hash2`, pas `B.rng()` : un prix affiche ne consomme pas un de. */
  function facteurDuJour(district, slug) {
    const c = B.defs.economie.contrebande;
    const districts = (Monde.carte && Monde.carte.def.districts) || [];
    const di = Math.max(0, districts.findIndex(function (d) { return d.slug === district; }));
    const mi = Object.keys(c.marchandises).sort().indexOf(slug);   // stable, quel que soit l'ordre du paquet
    const h = hash2(B.partie.jour * 131 + di, 977 + mi) % 1000;
    return c.facteur[0] + (c.facteur[1] - c.facteur[0]) * h / 1000;
  }

  function prixDuJour(district, slug) {
    return Math.round(B.defs.economie.contrebande.marchandises[slug].vente * facteurDuJour(district, slug));
  }

  function districtDe(x, y) {
    const z = Monde.zoneA(x, y);
    return z ? z.district : null;
  }

  /** Le comptoir de la cale : une caisse dans le coffre du char d'a cote. */
  function menuContrebande(j, etal) {
    const p = B.partie, c = B.defs.economie.contrebande, items = [];
    const v = charPres(etal.x, etal.y, c.rayon_px);
    if (!v) items.push({ libelle: 'VIENS EN CHAR — LA CALE NE SE PORTE PAS', actif: false });
    const dedans = caissesDe(v);
    Object.keys(c.marchandises).sort().forEach(function (slug) {
      const m = c.marchandises[slug], prix = prixAchat(slug);
      items.push({ libelle: 'CAISSE DE ' + m.nom.toUpperCase(), detail: prix + ' $',
                   actif: !!v && dedans < c.caisses_max && p.argent >= prix,
                   faire: function () {
                     if (!v || caissesDe(v) >= c.caisses_max || !payer(prix, m.nom.toUpperCase())) return false;
                     v.cargaison = v.cargaison || {};
                     v.cargaison[slug] = (v.cargaison[slug] || 0) + 1;
                     acheteesAujourdhui();
                     p.contrebande.achetees += 1;
                     Son.SFX.argent();
                     return false;
                   } });
    });
    return { titre: c.nom.toUpperCase(), items: items, sur: p.argent + ' $',
             refaire: function () { return menuContrebande(j, etal); },
             aide: (v ? dedans + '/' + c.caisses_max + ' CAISSES DANS LE COFFRE · ' : '') + 'LE PRIX MONTE AVEC CE QU’ON A DÉJÀ PRIS AUJOURD’HUI' };
  }

  /** Au comptoir d'un commerce qui en prend : le prix du jour du district, et
      « vendre » chaque marchandise qu'on a dans le char gare devant. */
  function itemsRevente(piece) {
    const c = B.defs.economie.contrebande, items = [];
    if (!piece || c.comptoirs.indexOf(piece.slug) < 0 || !B.exterieur) return items;
    const district = districtDe(B.exterieur.x, B.exterieur.y);
    if (!district) return items;
    const prix = {}, affiche = [];
    Object.keys(c.marchandises).sort().forEach(function (slug) {
      prix[slug] = prixDuJour(district, slug);
      affiche.push(c.marchandises[slug].nom.toUpperCase() + ' ' + prix[slug] + ' $');
    });
    items.push({ libelle: 'PRIX DU JOUR — ' + affiche.join(' · '), actif: false });
    const v = charDevant();
    if (!v || !v.cargaison) return items;
    Object.keys(c.marchandises).sort().forEach(function (slug) {
      const n = v.cargaison[slug] || 0;
      if (!n) return;
      const total = n * prix[slug];
      items.push({ libelle: 'VENDRE ' + n + ' CAISSE' + (n > 1 ? 'S' : '') + ' DE ' + c.marchandises[slug].nom.toUpperCase(),
                   detail: total + ' $', actif: true,
                   faire: function () { encaisser(total, 'LA RUN'); v.cargaison[slug] = 0; return false; } });
    });
    return items;
  }

  /** La police FOUILLE : arrete avec des caisses, on les perd en entier. */
  function confisquerLaCargaison(v) {
    const n = caissesDe(v);
    if (!n) return 0;
    v.cargaison = null;
    Hud.message('LA POLICE A TROUVÉ LES ' + n + ' CAISSES', 240);
    return n;
  }

  // --- Le marche noir : Josee, une fois le Faubourg libere --------------------------------

  function menuMarcheNoir() {
    const p = B.partie, mn = B.defs.marche_noir || { rabais: 1, articles: [], munitions: [] };
    const items = [];
    mn.articles.forEach(function (slug) {
      const arme = Combat.armeDef(slug);
      if (!arme) return;
      const prix = Math.round(arme.prix * mn.rabais), deja = !!p.armes[slug];
      items.push({ libelle: arme.nom.toUpperCase(), detail: deja ? 'DÉJÀ À TOI' : prix + ' $', actif: !deja && p.argent >= prix,
                   faire: function () { payer(prix, arme.nom.toUpperCase()); Combat.ramasserArme(slug, arme.chargeur); return false; } });
    });
    mn.munitions.forEach(function (slug) {
      const arme = Combat.armeDef(slug);
      if (!arme || !p.armes[slug] || arme.prix_munitions === null) return;
      const prix = Math.round(arme.prix_munitions * mn.rabais), pleine = p.armes[slug].mun >= arme.munitions_max;
      items.push({ libelle: 'MUNITIONS ' + arme.nom.toUpperCase(), detail: pleine ? 'PLEIN' : prix + ' $', actif: !pleine && p.argent >= prix,
                   faire: function () { payer(prix, 'MUNITIONS'); Combat.ramasserArme(slug, arme.chargeur); return false; } });
    });
    // Ce qui n'est pas une arme : le skimmer, par nombre en poche.
    (mn.objets || []).forEach(function (slug) {
      if (slug !== 'skimmer') return;
      const prix = B.defs.economie.guichet.skimmer.prix, n = p.objets.skimmer || 0;
      items.push({ libelle: 'SKIMMER', detail: prix + ' $' + (n ? ' (' + n + ' EN POCHE)' : ''), actif: p.argent >= prix,
                   faire: function () { payer(prix, 'SKIMMER'); p.objets.skimmer = (p.objets.skimmer || 0) + 1; return false; } });
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
    // A bord d'un autobus : ACTION demande l'arret, ou descend.
    if (j && j.passager) { if (!B.menu && !B.cinema) B.invite = Autobus.invite(j); return; }
    // ⚠️ Assis dans un manège, ACTION ne fait rien : pas d'invite, une invite qui
    // promet un geste qui n'aura pas lieu se lit comme un bogue.
    if (j && j.manege) return;
    if (!j || j.dansVehicule || B.menu || B.cinema) return;
    if (B.interieur) {
      // Le metro dit ce qu'ACTION fait sous terre (monter, descendre, remonter) —
      // et se tait quand la rame n'est pas la : une invite qui promet un geste
      // qui n'aura pas lieu se lit comme un bogue.
      const metro = Metro.invite(j);
      if (metro !== null) { B.invite = metro || null; return; }
      // ⚠️ Meme ordre que `utiliserPoint`, sinon le HUD promet « MANGER » et
      // ACTION parle au sergent.
      const dedans = Histoire.personnageSousLaMain(j);
      if (dedans) { const d = Histoire.personnage(dedans.personnage); B.invite = 'PARLER À ' + (d ? d.nom.toUpperCase() : '?'); return; }
      const point = pointSousLaMain(j);
      if (point) {
        const assis = Histoire.personnageDuPoint(point.type);
        const vente = point.type === 'caisse' && aVendre(B.interieur.slug);
        B.invite = assis ? 'PARLER À ' + assis.nom.toUpperCase()
          : vente ? 'ACHETER ' + vente.nom.toUpperCase()
          : (point.type === 'distributrice' ? inviteDistributrice(machineDuPoint(point))
            : (LIBELLES[point.type] || point.type.toUpperCase()));
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
      if (c && c.service === 'contrebande') {
        const cf = B.defs.economie.contrebande, v = charPres(etal.x, etal.y, cf.rayon_px);
        B.invite = c.nom.toUpperCase() + (v ? ' — ' + caissesDe(v) + '/' + cf.caisses_max + ' CAISSES' : ' — VIENS EN CHAR');
        return;
      }
      // ⚠️ Fermé, on ne promet pas de prix : ACTION ne vendra rien.
      if (c && !ouvert(c)) { B.invite = c.nom.toUpperCase() + ' — FERMÉ'; return; }
      B.invite = c ? c.nom.toUpperCase() + ' — ' + prixAmbulant(j, c) + ' $' + (coupon(j, c.slug) < 1 ? ' (COUPON)' : '') : 'ACHETER';
      return;
    }
    // ⚠️ Meme ordre que `interagir`, toujours : une invite qui annonce autre
    // chose que ce qu'ACTION va faire est pire que pas d'invite du tout.
    if (j.otage) { B.invite = 'LE LÂCHER'; return; }
    if (collecteurSousLaMain(j)) { B.invite = 'PAYER SAL — ' + B.partie.dette + ' $'; return; }
    const stool = stoolSousLaMain(j);
    if (stool) { B.invite = 'ACHETER SON SILENCE — ' + Police.prixDuStool() + ' $'; return; }
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
    const guichet = inviteGuichet(j);
    if (guichet) { B.invite = guichet; return; }
    const machine = distributriceSousLaMain(j);
    if (machine) { B.invite = inviteDistributrice(machine); return; }
    const edicule = Metro.inviteDescendre(j);
    if (edicule) { B.invite = edicule; return; }
    const manege = Foire.inviteMonter(j);
    if (manege) { B.invite = manege; return; }
    const autobus = Autobus.inviteMonter(j);
    if (autobus) { B.invite = autobus; return; }
    const objet = Combat.objetSousLaMain(j);
    if (objet) { const a = Combat.armeDef(objet.arme); B.invite = 'RAMASSER ' + (a ? a.nom.toUpperCase() : ''); return; }
    const porte = Monde.porteDevant(j);
    if (porte) { B.invite = 'ENTRER'; return; }
    const v = Vehicules.vehiculeSousLaMain(j);
    if (v) { B.invite = (v.conducteur === 'trafic' ? 'VOLER ' : 'MONTER : ') + v.def.nom.toUpperCase(); return; }
    // ⚠️ Au bout de la chaine, comme dans `interagir` : le bouclier humain est
    // ce qu'ACTION fait quand il n'avait rien d'autre a faire.
    // ⚠️ « TENIR » est dans l'invite parce que la prise se tient : un bouton
    // qui demande qu'on insiste sans le dire n'est pas un bouton qui resiste,
    // c'est un bouton brise. Le HUD la remplit pendant qu'on insiste.
    if (Combat.otageSousLaMain(j)) B.invite = 'BOUCLIER HUMAIN — TENIR';
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
            p.planque.vehicule = { slug: e.slug, sprite: e.sprite, couleur: e.couleur, vie: e.vie, x: Math.round(e.x), y: Math.round(e.y), angle: e.angle, vole: e.vole };
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
    if (B.t % 30 === 0) majCollecteurs();
    majFourriere();
    majMalGares();
    majGarage();
    majInvite(B.joueur);
    // Les paquets se ramassent en passant dessus.
    if (B.joueur && !B.interieur) {
      for (const e of Entites.autour(B.joueur.x, B.joueur.y, 12, function (q) { return q.type === 'paquet'; })) ramasserPaquet(e);
    }
    // Les liasses d'un guichet aussi — a pied : on ne ramasse pas au volant.
    if (B.joueur && !B.interieur && !B.joueur.dansVehicule) ramasserLesBillets(B.joueur);
    if (B.t % 600 === 0 && B.etat === 'jeu') sauvegarderPartie();
    if (B.t % 60 === 0) B.partie.stats.secondes++;
  }

  return { encaisser, payer, amende, potDeVin, factureHopital, nouveauJour, sauvegarderPartie,
           commerceDe, ouvert, acheterAmbulant, compagnie, interagir, soigner, nourrir, cafeine, hopital,
           coupon, prixAmbulant, crieurSousLaMain, stoolSousLaMain, prendreCoupon,
           paliersDe, palierDebloque, avantage, compterLeBoulot,
           boulot, arrestation, saisir, charSaisissable, prixRachat, garnirLaFourriere, menuFourriere, dansLaCour, majFourriere, malGare, majMalGares, estDeLaPlanque, prison, utiliserPoint, pointSousLaMain, libelleDuPoint, menuDuPoint, proprieteDe, possede,
           dormir, dormirJusquAuSoir, porterTenue, fouiller, menuComptoir, menuSalon, menuCasier, charDevant, prixDeVente, menuGarage, majGarage, menuDuRideau, menuArmurerie, menuVetements,
           revenusDuJour, manchetteDuJour, lireLeJournal, menuMarcheNoir, ramasserPaquet, majInvite, rabais,
           nuitDeLaDette, detteDuLendemain, collecteurs, envoyerLesCollecteurs, majCollecteurs, rembourser, collecteurSousLaMain, menuDette,
           guichetSousLaMain, inviteGuichet, utiliserGuichet, nuitDesSkimmers, guichetCasse, ramasserLesBillets,
           itemBouchee, manger, distributriceSousLaMain, inviteDistributrice, utiliserDistributrice, menuDistributrice,
           brasser, distributriceCassee, machineDuPoint,
           valeurAssuree, primeAssurance, assurer, charPerdu, encaisserAssurance, nuitDeLAssurance,
           charPres, caissesDe, prixAchat, facteurDuJour, prixDuJour, menuContrebande, itemsRevente, confisquerLaCargaison, maj };
})();
