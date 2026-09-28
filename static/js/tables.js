/* Bandini — les tables du Dragon d'or (docs/jalons/le-casino-du-petit-canton.md, vague 2).

   Cinq tables dans la grande salle, un croupier a chacune : le BLACKJACK, la ROULETTE, le POKER A TROIS
   CARTES, le SIC BO et le BACCARA. Les regles sont a Python (`tables_de_jeu.py`, `B.defs.tables_de_jeu`) ;
   ici, on joue le coup. Chaque fonction qui decide d'un gain a son JUMEAU en Python, et un juge les compare
   coup pour coup (`test_tables_js.py`).

   ⚠️ LE HASARD EST AUX TABLES, comme celui du videopoker et de la machine a sous : un coup se tire d'un
   generateur seme par la graine de la partie, le numero du coup et un SEL PAR TABLE (`SELS`), jamais
   `B.rng()` — un coup joue ne decale pas un seul de du reste du jeu, et le meme coup revient au meme numero.

   ⚠️ UN MENU, PAS UN ECRAN A PART (la regle du videopoker) : MISE, PARI, DONNER, TIRER, RESTER sont des
   lignes ; la MISE et le PARI changent a ACTION (un cran) ou a GAUCHE / DROITE (`maj`). Les cartes, la roue,
   les des se DESSINENT a cote (`dessiner`), et s'animent en IMAGES DESSINEES : un menu ouvert fige `B.t`.

   LES SONS (`son.js`, « La cabane et le casino s'entendent ») : les jetons a la mise, les cartes donnees, la bille
   lancee, les des sous la cloche ; au gain, celui de la machine a sous, et son gros lot. Chacun a son repli
   synthetise, et les fichiers ne se chargent qu'en approchant du casino (`audio.LIEUX`).

   ⚠️ LE GAIN EST PAYE TOUT DE SUITE, EN SILENCE, et ANNONCE quand la bille s'arrete (`annoncer`) : payer a
   la fin de l'animation, c'etait ne jamais payer un joueur qui ferme le menu pendant que la roue tourne. */

const Tables = (function () {
  'use strict';

  function regles() { return B.defs.tables_de_jeu; }

  //: Un sel par table : la main numero 3 du blackjack et le tour numero 3 de la roulette ne tirent pas le meme
  //: hasard (ni celui du videopoker, ni celui de la machine a sous).
  const SELS = { blackjack: 0x7FEB352D, roulette: 0x846CA68B, poker: 0x5BD1E995, sic_bo: 0x27D4EB2F, baccara: 0x165667B1 };

  //: Combien d'images dure chaque animation, et le pas des cartes qu'on retourne une a une.
  const ANIME = { roulette: 110, sic_bo: 50, carte: 9 };

  // --- Les compteurs et le hasard ----------------------------------------------------------------------------

  /** Ce que la partie garde des tables : la mise choisie, les paris, et un compteur par table (`jour`, `coups`
      ce jour-la, `total` : le numero du prochain coup, qui seme son hasard). */
  function etat() {
    const p = B.partie;
    p.tables = p.tables || { mise: regles().mises[0], roulette: 'rouge', numero: 17, sic_bo: 'petit', chiffre: 4, baccara: 'banque' };
    return p.tables;
  }

  function compteur(jeu) {
    const p = B.partie, e = etat();
    e.coups = e.coups || {};
    const c = e.coups[jeu] = e.coups[jeu] || { jour: p.jour, coups: 0, total: 0 };
    if (c.jour !== p.jour) { c.jour = p.jour; c.coups = 0; }
    return c;
  }

  function hasard(jeu, n) { return mulberry(((B.graine | 0) ^ Math.imul(n + 1, SELS[jeu])) >>> 0); }

  /** Le paquet du coup numero `n` a cette table : cinquante-deux cartes battues (0 a 51, celles du videopoker). */
  function paquet(jeu, n) {
    const rng = hasard(jeu, n), cartes = [];
    for (let c = 0; c < 52; c++) cartes.push(c);
    for (let i = 51; i > 0; i--) {
      const k = Math.floor(rng() * (i + 1));
      const t = cartes[i]; cartes[i] = cartes[k]; cartes[k] = t;
    }
    return cartes;
  }

  /** La case ou tombe la bille au tour numero `n` (0 a 36). */
  function numeroDuTour(n) { return Math.floor(hasard('roulette', n)() * 37); }

  /** Les trois des du jet numero `n`. */
  function desDuJet(n) {
    const rng = hasard('sic_bo', n);
    return [0, 1, 2].map(function () { return 1 + Math.floor(rng() * 6); });
  }

  // --- Les regles : les jumeaux de `tables_de_jeu.py` ---------------------------------------------------------

  function bjValeur(cartes) {
    let total = 0, as = 0;
    cartes.forEach(function (c) { const r = c % 13; total += r === 12 ? 1 : Math.min(10, r + 2); if (r === 12) as++; });
    return as && total + 10 <= 21 ? { total: total + 10, souple: true } : { total: total, souple: false };
  }
  function bjNaturel(cartes) { return cartes.length === 2 && bjValeur(cartes).total === 21; }
  function bjCroupier(main, pioche) {
    main = main.slice();
    let k = 0;
    while (bjValeur(main).total < regles().croupier) main.push(pioche[k++]);
    return main;
  }
  function bjRegler(joueur, croupier) {
    const j = bjValeur(joueur).total, c = bjValeur(croupier).total;
    if (j > 21) return 0;
    if (bjNaturel(joueur)) return bjNaturel(croupier) ? 1 : regles().naturel;
    if (bjNaturel(croupier) || (c <= 21 && c > j)) return 0;
    return c === j ? 1 : 2;
  }
  /** Une main entiere, `tirer(main, visible)` decidant pour le joueur — le jumeau de `bj_jouer`. */
  function bjJouer(cartes, tirer) {
    const joueur = [cartes[0], cartes[2]];
    let croupier = [cartes[1], cartes[3]], k = 4;
    if (!bjNaturel(joueur)) {
      while (bjValeur(joueur).total < 21 && tirer(joueur, croupier[0])) joueur.push(cartes[k++]);
    }
    if (bjValeur(joueur).total <= 21 && !bjNaturel(joueur)) croupier = bjCroupier(croupier, cartes.slice(k));
    return { paie: bjRegler(joueur, croupier), joueur: joueur, croupier: croupier };
  }

  /** La couleur d'une case : le zero est vert, et autour de la roue, rouge et noir alternent. */
  function couleurDe(n) {
    if (n === 0) return 'vert';
    return regles().roue.indexOf(n) % 2 === 1 ? 'rouge' : 'noir';
  }
  function roulettePaie(pari, n) {
    if (typeof pari === 'number') return pari === n ? regles().plein : 0;
    if (n === 0) return 0;
    const gagne = pari === 'rouge' ? couleurDe(n) === 'rouge' : pari === 'noir' ? couleurDe(n) === 'noir'
      : pari === 'pair' ? n % 2 === 0 : n % 2 === 1;
    return gagne ? 2 : 0;
  }

  function sicBoPaie(pari, des) {
    if (typeof pari === 'number') {
      const k = des.filter(function (d) { return d === pari; }).length;
      return k ? 1 + k : 0;
    }
    if (des[0] === des[1] && des[1] === des[2]) return 0;
    const total = des[0] + des[1] + des[2];
    return ((total >= 4 && total <= 10) === (pari === 'petit')) ? 2 : 0;
  }

  const MAINS_POKER = ['carte_haute', 'paire', 'couleur', 'quinte', 'brelan', 'quinte_flush'];
  const NOMS_POKER = ['CARTE HAUTE', 'PAIRE', 'COULEUR', 'QUINTE', 'BRELAN', 'QUINTE FLUSH'];
  /** La force d'une main de trois cartes, en liste : le rang de la main, puis ce qui departage. */
  function pokerForce(cartes) {
    const rangs = cartes.map(function (c) { return c % 13; }).sort(function (a, b) { return b - a; });
    const couleur = cartes.every(function (c) { return Math.floor(c / 13) === Math.floor(cartes[0] / 13); });
    const roue = rangs[0] === 12 && rangs[1] === 1 && rangs[2] === 0;
    const quinte = roue || (rangs[0] - rangs[2] === 2 && rangs[0] !== rangs[1] && rangs[1] !== rangs[2]);
    const haut = roue ? [1, 0, -1] : rangs;
    if (quinte && couleur) return [5].concat(haut);
    if (rangs[0] === rangs[2]) return [4].concat(haut);
    if (quinte) return [3].concat(haut);
    if (couleur) return [2].concat(haut);
    if (rangs[0] === rangs[1] || rangs[1] === rangs[2]) return [1, rangs[1], rangs[0] === rangs[1] ? rangs[2] : rangs[0]];
    return [0].concat(haut);
  }
  function comparer(a, b) {
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      const x = a[i] === undefined ? -9 : a[i], y = b[i] === undefined ? -9 : b[i];
      if (x !== y) return x > y ? 1 : -1;
    }
    return 0;
  }
  function pokerMain(cartes) { return MAINS_POKER[pokerForce(cartes)[0]]; }
  function pokerOuvre(cartes) { const f = pokerForce(cartes); return f[0] >= 1 || f[1] >= regles().dame; }
  function pokerRegler(joueur, croupier, joue) {
    if (!joue) return 0;
    const bonus = regles().bonus[pokerMain(joueur)] || 0;
    if (!pokerOuvre(croupier)) return 3 + bonus;
    const s = comparer(pokerForce(joueur), pokerForce(croupier));
    return (s > 0 ? 4 : s === 0 ? 2 : 0) + bonus;
  }

  function bacValeur(c) { const r = c % 13; return r === 12 ? 1 : (r >= 8 ? 0 : r + 2); }
  function bacPoint(cartes) { return cartes.reduce(function (s, c) { return s + bacValeur(c); }, 0) % 10; }
  function bacTireBanque(b, t) {
    if (t === null) return b <= 5;
    return b <= 2 || (b === 3 && t !== 8) || (b === 4 && t >= 2 && t <= 7) || (b === 5 && t >= 4 && t <= 7)
      || (b === 6 && (t === 6 || t === 7));
  }
  /** Le coup, selon le tableau — le jumeau de `bac_coup`. */
  function bacCoup(cartes) {
    const joueur = [cartes[0], cartes[2]], banque = [cartes[1], cartes[3]];
    let k = 4;
    if (bacPoint(joueur) >= 8 || bacPoint(banque) >= 8) return { joueur: joueur, banque: banque };
    let t = null;
    if (bacPoint(joueur) <= 5) { joueur.push(cartes[k++]); t = bacValeur(joueur[2]); }
    if (bacTireBanque(bacPoint(banque), t)) banque.push(cartes[k]);
    return { joueur: joueur, banque: banque };
  }
  function bacRegler(pari, joueur, banque) {
    const pj = bacPoint(joueur), pb = bacPoint(banque);
    if (pari === 'egalite') return pj === pb ? regles().egalite : 0;
    if (pj === pb) return 1;
    if (pari === 'joueur') return pj > pb ? 2 : 0;
    return pb > pj ? (pb === 6 ? regles().six : 2) : 0;
  }

  // --- Jouer un coup ---------------------------------------------------------------------------------------

  //: Le coup en cours a chaque table (`B.tables`) : `phase` (mise, joue, fin), les cartes ou la case, le
  //: resultat, et `images`, l'horloge de son animation.
  function enCours(jeu) { B.tables = B.tables || {}; return B.tables[jeu] || null; }

  /** La mise part (et le coup est compte) : rend le compteur, ou null si la table refuse. `fois` : ce qu'il
      faut avoir en poche (le poker demande de quoi JOUER apres le depart). */
  function miser(jeu, fois) {
    const r = regles(), c = compteur(jeu), mise = etat().mise;
    if (c.coups >= r.par_jour && !triche('machines')) { Hud.message('LA TABLE EST FERMÉE POUR TOI AUJOURD’HUI'); Son.SFX.erreur(); return null; }
    if (B.partie.argent < mise * (fois || 1)) { Hud.message('PAS ASSEZ D’ARGENT'); Son.SFX.erreur(); return null; }
    if (!Missions.payer(mise, r.noms[jeu])) return null;
    B.tables = B.tables || {};
    Son.SFX.jetons();
    c.coups++;
    return c;
  }

  /** Le coup est regle : ce qu'il rend est paye TOUT DE SUITE, en silence — l'annonce vient quand l'animation
      finit (`annoncer`). `mise` : ce qui a ete mise en tout. */
  function regler(t, paie, nom, mise) {
    const gain = Math.round(paie * etat().mise);
    t.phase = 'fin';
    t.resultat = { nom: nom, gain: gain, mise: mise };
    t.annonce = false;
    if (gain > 0) Missions.encaisser(gain, null, true);
    return gain;
  }

  /** Quand l'animation d'un coup finit : le gain qui sonne, ou ce que la table garde. */
  function annoncer(t) {
    if (t.annonce || !t.resultat) return;
    t.annonce = true;
    const r = t.resultat;
    // Le gros lot (dix mises de profit et plus : un numero plein, un triple au sic bo) sonne comme a la machine.
    if (r.gain > r.mise) { if (r.gain - r.mise >= 10 * etat().mise) Son.SFX.jackpot(); else Son.SFX.gain_machine(); Hud.message('+' + (r.gain - r.mise) + ' $ · ' + r.nom); }
    else if (r.gain === r.mise && r.gain > 0) Hud.message(r.nom + ' · LA MISE EST RENDUE');
    else if (r.gain > 0) Hud.message(r.nom + ' · ' + r.gain + ' $ RENDUS');
    else Hud.message(r.nom + ' · LA TABLE GARDE TES ' + r.mise + ' $');
  }

  //: Le BLACKJACK : DONNER, puis TIRER ou RESTER ; le croupier tire jusqu'a dix-sept.
  function bjDonner() {
    const c = miser('blackjack');
    if (!c) return false;
    const cartes = paquet('blackjack', c.total++);
    Son.SFX.cartes_donnees();
    const t = B.tables.blackjack = { phase: 'joue', cartes: cartes, joueur: [cartes[0], cartes[2]],
                                     croupier: [cartes[1], cartes[3]], k: 4, images: 0, fin: 0 };
    if (bjNaturel(t.joueur)) bjFinir(t);
    return true;
  }
  function bjTirer() {
    const t = enCours('blackjack');
    if (!t || t.phase !== 'joue') return false;
    t.joueur.push(t.cartes[t.k++]);
    Son.SFX.cartes_donnees();
    if (bjValeur(t.joueur).total >= 21) bjFinir(t);
    return true;
  }
  function bjRester() {
    const t = enCours('blackjack');
    if (!t || t.phase !== 'joue') return false;
    bjFinir(t);
    return true;
  }
  function bjFinir(t) {
    const j = bjValeur(t.joueur).total;
    if (j <= 21 && !bjNaturel(t.joueur)) t.croupier = bjCroupier(t.croupier, t.cartes.slice(t.k));
    const paie = bjRegler(t.joueur, t.croupier), c = bjValeur(t.croupier).total;
    const nom = j > 21 ? 'CRÈVE À ' + j : bjNaturel(t.joueur) && paie > 1 ? 'BLACKJACK'
      : paie === 2 ? j + ' CONTRE ' + (c > 21 ? 'LE CROUPIER QUI CRÈVE' : c) : paie === 1 ? 'ÉGALITÉ À ' + j
      : bjNaturel(t.croupier) ? 'BLACKJACK DU CROUPIER' : j + ' CONTRE ' + c;
    t.fin = t.images;
    regler(t, paie, nom, etat().mise);
  }

  //: La ROULETTE : un pari (une chance simple, ou un numero plein), et la bille.
  function pariDeRoulette() { const e = etat(); return e.roulette === 'numero' ? e.numero : e.roulette; }
  function lancer() {
    const c = miser('roulette');
    if (!c) return false;
    const pari = pariDeRoulette(), n = numeroDuTour(c.total++);
    Son.SFX.roulette_bille();
    const t = B.tables.roulette = { phase: 'fin', n: n, pari: pari, images: 0, depart: hash2(c.total, 7) % 37 };
    const coul = couleurDe(n);
    regler(t, roulettePaie(pari, n), n + (coul === 'vert' ? ' · LE ZÉRO' : ' ' + coul.toUpperCase()), etat().mise);
    return true;
  }

  //: Le SIC BO : petit, grand, ou un chiffre, et trois des sous la cloche.
  function pariDeSicBo() { const e = etat(); return e.sic_bo === 'chiffre' ? e.chiffre : e.sic_bo; }
  function secouer() {
    const c = miser('sic_bo');
    if (!c) return false;
    const pari = pariDeSicBo(), des = desDuJet(c.total++);
    Son.SFX.des_sic_bo();
    const t = B.tables.sic_bo = { phase: 'fin', des: des, pari: pari, images: 0 };
    const total = des[0] + des[1] + des[2], triple = des[0] === des[1] && des[1] === des[2];
    regler(t, sicBoPaie(pari, des), des.join('-') + ' · ' + (triple ? 'TRIPLE' : total + (total <= 10 ? ' PETIT' : ' GRAND')), etat().mise);
    return true;
  }

  //: Le POKER A TROIS CARTES : le depart, trois cartes, puis JOUER (une mise de plus) ou PASSER.
  function pkDonner() {
    const c = miser('poker', 2);
    if (!c) return false;
    const cartes = paquet('poker', c.total++);
    Son.SFX.cartes_donnees();
    B.tables.poker = { phase: 'joue', joueur: cartes.slice(0, 3), croupier: cartes.slice(3, 6), images: 0, fin: 0 };
    return true;
  }
  function pkDecider(joue) {
    const t = enCours('poker'), mise = etat().mise;
    if (!t || t.phase !== 'joue') return false;
    if (joue && !Missions.payer(mise, 'POKER')) { Hud.message('PAS ASSEZ D’ARGENT'); Son.SFX.erreur(); return false; }
    const paie = pokerRegler(t.joueur, t.croupier, joue);
    const nomJ = NOMS_POKER[pokerForce(t.joueur)[0]], nomC = NOMS_POKER[pokerForce(t.croupier)[0]];
    const nom = !joue ? 'TU PASSES' : !pokerOuvre(t.croupier) ? 'LE CROUPIER N’OUVRE PAS'
      : nomJ + ' CONTRE ' + nomC;
    t.fin = t.images;
    t.joue = joue;
    regler(t, paie, nom, joue ? 2 * mise : mise);
    return true;
  }

  //: Le BACCARA : on parie sur le JOUEUR, la BANQUE ou l'EGALITE, et le tableau fait le reste.
  function bacDonner() {
    const c = miser('baccara');
    if (!c) return false;
    const cartes = paquet('baccara', c.total++), pari = etat().baccara;
    Son.SFX.cartes_donnees();
    const coup = bacCoup(cartes), pj = bacPoint(coup.joueur), pb = bacPoint(coup.banque);
    const t = B.tables.baccara = { phase: 'fin', joueur: coup.joueur, banque: coup.banque, pari: pari, images: 0 };
    const nom = pj === pb ? 'ÉGALITÉ À ' + pj : (pj > pb ? 'LE JOUEUR ' : 'LA BANQUE ') + Math.max(pj, pb) + ' CONTRE ' + Math.min(pj, pb);
    regler(t, bacRegler(pari, coup.joueur, coup.banque), nom, etat().mise);
    return true;
  }

  // --- Le menu ---------------------------------------------------------------------------------------------

  //: Les paris qu'on fait defiler, table par table, et leur nom.
  const PARIS = {
    roulette: [['rouge', 'ROUGE'], ['noir', 'NOIR'], ['pair', 'PAIR'], ['impair', 'IMPAIR'], ['numero', 'UN NUMÉRO']],
    sic_bo: [['petit', 'PETIT (4 À 10)'], ['grand', 'GRAND (11 À 17)'], ['chiffre', 'UN CHIFFRE']],
    baccara: [['joueur', 'LE JOUEUR'], ['banque', 'LA BANQUE'], ['egalite', 'L’ÉGALITÉ']],
  };

  /** Une ligne qui CHANGE de valeur : ACTION avance d'un cran, GAUCHE et DROITE dans les deux sens (`maj`). */
  function ligneAChoix(libelle, valeurs, cle, noms) {
    const e = etat();
    const i = Math.max(0, valeurs.indexOf(e[cle]));
    const ajuster = function (s) { e[cle] = valeurs[(valeurs.indexOf(e[cle]) + s + valeurs.length) % valeurs.length]; Son.SFX.menu(); };
    return { libelle: libelle, detail: noms ? noms[i] : String(valeurs[i]), ajuster: ajuster,
             faire: function () { ajuster(1); return false; } };
  }

  function ligneDeMise() {
    return ligneAChoix('MISE', regles().mises, 'mise', regles().mises.map(function (m) { return m + ' $'; }));
  }

  function ligneDePari(jeu) {
    const liste = PARIS[jeu];
    return ligneAChoix('PARI', liste.map(function (p) { return p[0]; }), jeu, liste.map(function (p) { return p[1]; }));
  }

  /** Le retour du pari choisi, pour l'aide du menu. */
  function retourAffiche(jeu) {
    const r = regles().retours[jeu], e = etat();
    if (jeu === 'roulette') return e.roulette === 'numero' ? r.numero : r.chance;
    if (jeu === 'sic_bo') return r[e.sic_bo];
    if (jeu === 'baccara') return r[e.baccara];
    return r.main;
  }

  /** Les lignes du menu, dans la phase ou la table est. */
  function lignes(jeu) {
    const t = enCours(jeu), e = etat(), p = B.partie, r = regles();
    const reste = r.par_jour - compteur(jeu).coups;
    const peut = function (fois) { return (reste > 0 || triche('machines')) && p.argent >= e.mise * (fois || 1); };
    if (jeu === 'blackjack') {
      if (t && t.phase === 'joue') {
        return [{ libelle: 'TIRER', detail: String(bjValeur(t.joueur).total), faire: function () { bjTirer(); return curseurApres('blackjack', 0); } },
                { libelle: 'RESTER', faire: function () { bjRester(); return curseurApres('blackjack', 1); } }];
      }
      return [ligneDeMise(), { libelle: 'DONNER', detail: e.mise + ' $', actif: peut(), faire: function () { bjDonner(); return curseurApres('blackjack', 0); } }];
    }
    if (jeu === 'poker') {
      if (t && t.phase === 'joue') {
        return [{ libelle: 'JOUER', detail: '+' + e.mise + ' $', faire: function () { pkDecider(true); return curseurApres('poker', 0); } },
                { libelle: 'PASSER', faire: function () { pkDecider(false); return curseurApres('poker', 1); } }];
      }
      return [ligneDeMise(), { libelle: 'DONNER', detail: e.mise + ' $', actif: peut(2), faire: function () { pkDonner(); return curseurApres('poker', 0); } }];
    }
    const items = [ligneDePari(jeu)];
    if (jeu === 'roulette' && e.roulette === 'numero') {
      const numeros = []; for (let n = 0; n <= 36; n++) numeros.push(n);
      items.push(ligneAChoix('NUMÉRO', numeros, 'numero'));
    }
    if (jeu === 'sic_bo' && e.sic_bo === 'chiffre') items.push(ligneAChoix('CHIFFRE', [1, 2, 3, 4, 5, 6], 'chiffre'));
    items.push(ligneDeMise());
    const geste = { roulette: ['LANCER LA BILLE', lancer], sic_bo: ['SECOUER LES DÉS', secouer], baccara: ['DONNER', bacDonner] }[jeu];
    items.push({ libelle: geste[0], detail: e.mise + ' $', actif: peut(), faire: function () { geste[1](); return false; } });
    return items;
  }

  /** Apres un geste, le curseur va ou le pouce voudra aller : sur TIRER (ou JOUER) si la main continue, sur
      DONNER si elle est finie — un blackjack servi d'emblee laissait le curseur sur MISE, et ACTION changeait
      la mise au lieu de redonner. Rend false : le menu reste ouvert. */
  function curseurApres(jeu, siJoue) {
    const t = enCours(jeu);
    if (B.menu) B.menu.curseur = t && t.phase === 'joue' ? siJoue : 1;
    return false;
  }

  /** Ce qui n'est pas encore annonce (la bille roule) ne se voit pas encore en poche. */
  function enAttente(jeu) {
    const t = enCours(jeu);
    return t && t.phase === 'fin' && t.resultat && !t.annonce ? t.resultat.gain : 0;
  }

  function menu(jeu) {
    const r = regles(), p = B.partie;
    const reste = Math.max(0, r.par_jour - compteur(jeu).coups), libre = triche('machines');   // la triche MACHINES SANS LIMITE
    const m = { titre: r.noms[jeu], sur: (p.argent - enAttente(jeu)) + ' $', items: lignes(jeu), largeur: 440, hauteur: 214, colonne: 176,
                aide: 'RETOUR ' + retourAffiche(jeu) + ' % · ' + (libre ? 'SANS LIMITE' : reste + ' COUP' + (reste > 1 ? 'S' : '') + ' AUJOURD’HUI'),
                dessiner: function (ctx, x, y) { dessiner(jeu, ctx, x, y); },
                maj: function (menu) { majMenu(menu); } };
    // Un coup en cours se reprend ou on l'avait laisse (TIRER, JOUER) ; sinon, le curseur sur le geste.
    const t = enCours(jeu);
    m.curseur = t && t.phase === 'joue' ? 0 : m.items.length - 1;
    return m;
  }

  /** GAUCHE et DROITE changent la ligne a choix sous le curseur. ⚠️ Un appui neuf, un cran : tenu, le pouce
      ferait defiler les trente-sept numeros en une seconde. */
  function majMenu(m) {
    const item = m.items[m.curseur];
    if (!item || !item.ajuster) return;
    const s = Entree.neuf('gauche') ? -1 : Entree.neuf('droite') ? 1 : 0;
    if (!s) return;
    item.ajuster(s);
    Hud.rafraichirMenu();
  }

  // --- Le dessin, a droite de la liste --------------------------------------------------------------------

  const ENCRE = { rouge: '#c0392b', noir: '#1b1b24', vert: '#2e8a4a', or: '#e8b33c', gris: '#8a8698', papier: '#efe6d0', feutre: '#1f5e3a' };
  //: Les couleurs des cartes en pixels, 5 × 5 : pique, coeur, carreau, trefle (celles du videopoker).
  const ENSEIGNES = [
    ['..#..', '.###.', '#####', '..#..', '.###.'],
    ['.#.#.', '#####', '#####', '.###.', '..#..'],
    ['..#..', '.###.', '#####', '.###.', '..#..'],
    ['..#..', '.###.', '#.#.#', '#####', '..#..'],
  ];

  function motif(ctx, lignes, x, y, pas, couleur) {
    ctx.fillStyle = couleur;
    for (let yy = 0; yy < lignes.length; yy++) {
      for (let xx = 0; xx < lignes[yy].length; xx++) if (lignes[yy][xx] === '#') ctx.fillRect(x + xx * pas, y + yy * pas, pas, pas);
    }
  }

  /** Une carte de 26 × 36, face visible ou de dos. */
  function carte(ctx, x, y, c, cachee) {
    ctx.fillStyle = '#3a3450'; ctx.fillRect(x - 1, y - 1, 28, 38);
    if (cachee) {
      ctx.fillStyle = '#6b2a2a'; ctx.fillRect(x, y, 26, 36);
      ctx.fillStyle = '#8a3a36'; for (let k = 2; k < 34; k += 4) ctx.fillRect(x + 2, y + k, 22, 2);
      return;
    }
    const rouge = Math.floor(c / 13) === 1 || Math.floor(c / 13) === 2, encre = rouge ? ENCRE.rouge : ENCRE.noir;
    ctx.fillStyle = ENCRE.papier; ctx.fillRect(x, y, 26, 36);
    Atlas.texte(ctx, B.defs.videopoker.rangs[c % 13], x + 2, y + 2, encre, 1);
    motif(ctx, ENSEIGNES[Math.floor(c / 13)], x + 6, y + 14, 3, encre);
  }

  /** Une rangee de cartes ; `vues` : combien sont deja retournees (les autres restent de dos). */
  function rangee(ctx, cartes, x, y, vues, cacherLaDeuxieme) {
    cartes.forEach(function (c, i) {
      if (i >= vues) return;
      carte(ctx, x + i * 30, y, c, cacherLaDeuxieme && i === 1);
    });
  }

  function titre(ctx, s, x, y, couleur) { Atlas.texte(ctx, s, x, y, couleur || ENCRE.gris, 1); }

  /** Le montant d'argent en haut a droite, SANS le gain qui n'est pas encore annonce : l'argent ne saute pas
      avant que la bille s'arrete. */
  function sur(t, fini) {
    if (!B.menu) return;
    B.menu.sur = (B.partie.argent - (t && t.resultat && !fini ? t.resultat.gain : 0)) + ' $';
  }

  function dessiner(jeu, ctx, x, y) {
    const t = enCours(jeu), x0 = x + 190, y0 = y + 30;
    const depuis = t ? t.images++ : 0;
    ctx.fillStyle = ENCRE.feutre; ctx.fillRect(x0 - 6, y0 - 6, 244, 150);
    ctx.fillStyle = '#6b4a2a'; ctx.fillRect(x0 - 6, y0 - 6, 244, 2); ctx.fillRect(x0 - 6, y0 + 142, 244, 2);
    let fini = true;
    if (jeu === 'blackjack') fini = dessinerBlackjack(ctx, x0, y0, t, depuis);
    else if (jeu === 'roulette') fini = dessinerRoulette(ctx, x0, y0, t, depuis);
    else if (jeu === 'poker') fini = dessinerPoker(ctx, x0, y0, t, depuis);
    else if (jeu === 'sic_bo') fini = dessinerSicBo(ctx, x0, y0, t, depuis);
    else fini = dessinerBaccara(ctx, x0, y0, t, depuis);
    if (t && t.phase === 'fin') {
      sur(t, fini);
      if (fini) {
        annoncer(t);
        const g = t.resultat.gain, m = t.resultat.mise;
        Atlas.texte(ctx, t.resultat.nom, x0, y0 + 150, g > m ? ENCRE.or : ENCRE.gris, 1);
        Atlas.texte(ctx, g > m ? '+' + (g - m) + ' $' : g === m ? 'MISE RENDUE' : g > 0 ? g + ' $ RENDUS' : 'PERDU', x + 12, y + 150, g > m ? ENCRE.or : ENCRE.gris, 1);
      }
    }
    B.stats.rects += 40;
  }

  function dessinerBlackjack(ctx, x0, y0, t, depuis) {
    const r = regles();
    titre(ctx, 'LE CROUPIER TIRE JUSQU’À ' + r.croupier, x0, y0 + 124);
    titre(ctx, 'BLACKJACK 3 POUR 2 · LE RESTE 1 POUR 1', x0, y0 + 134);
    if (!t) { titre(ctx, 'LE CROUPIER', x0, y0); titre(ctx, 'TOI', x0, y0 + 70); return true; }
    // Le croupier retourne sa carte cachee, puis tire les siennes, une a une.
    const fin = t.phase === 'fin';
    const vues = fin ? Math.min(t.croupier.length, 2 + Math.floor((depuis - t.fin) / ANIME.carte)) : 2;
    const cVu = t.croupier.slice(0, vues);
    titre(ctx, 'LE CROUPIER' + (fin ? ' · ' + bjValeur(cVu).total : ''), x0, y0);
    rangee(ctx, t.croupier, x0, y0 + 10, vues, !fin);
    titre(ctx, 'TOI · ' + bjValeur(t.joueur).total, x0, y0 + 70);
    rangee(ctx, t.joueur, x0, y0 + 80, t.joueur.length, false);
    return !fin || vues >= t.croupier.length;
  }

  function dessinerPoker(ctx, x0, y0, t, depuis) {
    const r = regles();
    titre(ctx, 'LE CROUPIER OUVRE À LA DAME', x0, y0 + 124);
    titre(ctx, 'BONUS : QUINTE ' + r.bonus.quinte + ' · BRELAN ' + r.bonus.brelan + ' · QUINTE FLUSH ' + r.bonus.quinte_flush, x0, y0 + 134);
    if (!t) { titre(ctx, 'LE CROUPIER', x0, y0); titre(ctx, 'TOI', x0, y0 + 70); return true; }
    const fin = t.phase === 'fin';
    const vues = fin ? Math.min(3, Math.floor((depuis - t.fin) / ANIME.carte) + 1) : 0;
    titre(ctx, 'LE CROUPIER' + (fin && vues >= 3 ? ' · ' + NOMS_POKER[pokerForce(t.croupier)[0]] : ''), x0, y0);
    t.croupier.forEach(function (c, i) { carte(ctx, x0 + i * 30, y0 + 10, c, i >= vues); });
    titre(ctx, 'TOI · ' + NOMS_POKER[pokerForce(t.joueur)[0]], x0, y0 + 70);
    rangee(ctx, t.joueur, x0, y0 + 80, 3, false);
    return !fin || vues >= 3;
  }

  function dessinerBaccara(ctx, x0, y0, t, depuis) {
    const r = regles();
    titre(ctx, 'LA BANQUE QUI GAGNE À 6 PAIE LA MOITIÉ', x0, y0 + 124);
    titre(ctx, 'ÉGALITÉ ' + (r.egalite - 1) + ' POUR 1 · LES AUTRES SONT RENDUS', x0, y0 + 134);
    if (!t) { titre(ctx, 'LE JOUEUR', x0, y0); titre(ctx, 'LA BANQUE', x0, y0 + 70); return true; }
    // Les cartes arrivent dans l'ordre du sabot : joueur, banque, joueur, banque, puis les troisiemes.
    const ordre = [['joueur', 0], ['banque', 0], ['joueur', 1], ['banque', 1], ['joueur', 2], ['banque', 2]]
      .filter(function (o) { return t[o[0]].length > o[1]; });
    const n = Math.min(ordre.length, 1 + Math.floor(depuis / ANIME.carte));
    const vues = { joueur: 0, banque: 0 };
    ordre.slice(0, n).forEach(function (o) { vues[o[0]]++; });
    const fini = n >= ordre.length;
    titre(ctx, 'LE JOUEUR · ' + bacPoint(t.joueur.slice(0, vues.joueur)), x0, y0, t.pari === 'joueur' ? ENCRE.or : ENCRE.gris);
    rangee(ctx, t.joueur, x0, y0 + 10, vues.joueur, false);
    titre(ctx, 'LA BANQUE · ' + bacPoint(t.banque.slice(0, vues.banque)), x0, y0 + 70, t.pari === 'banque' ? ENCRE.or : ENCRE.gris);
    rangee(ctx, t.banque, x0, y0 + 80, vues.banque, false);
    return fini;
  }

  /** La roue, vue de haut : trente-sept cases en couronne, le zero en vert, et la bille qui tourne a l'envers
      de la roue, ralentit et tombe dans sa case. */
  function dessinerRoulette(ctx, x0, y0, t, depuis) {
    const r = regles(), roue = r.roue, cx = x0 + 60, cy = y0 + 62, R = 50;
    const duree = ANIME.roulette, avance = t ? Math.min(1, depuis / duree) : 1;
    const rotation = (B.image || 0) * 0.004;
    for (let i = 0; i < 37; i++) {
      const a = rotation + i * 2 * Math.PI / 37;
      const coul = couleurDe(roue[i]);
      ctx.fillStyle = coul === 'vert' ? ENCRE.vert : coul === 'rouge' ? ENCRE.rouge : ENCRE.noir;
      ctx.fillRect(Math.round(cx + Math.cos(a) * R) - 4, Math.round(cy + Math.sin(a) * R) - 4, 8, 8);
      ctx.fillStyle = '#b89a4a';
      ctx.fillRect(Math.round(cx + Math.cos(a) * (R - 9)) - 1, Math.round(cy + Math.sin(a) * (R - 9)) - 1, 2, 2);
    }
    ctx.fillStyle = '#6b4a2a'; ctx.fillRect(cx - 26, cy - 26, 52, 52);
    ctx.fillStyle = '#b89a4a'; ctx.fillRect(cx - 3, cy - 18, 6, 36); ctx.fillRect(cx - 18, cy - 3, 36, 6);
    if (t) {
      // La bille : sa place SUR LA ROUE (la case du resultat), plus des tours qui fondent a mesure qu'elle ralentit.
      const i = roue.indexOf(t.n), frein = 1 - Math.pow(1 - avance, 3);
      const rel = i * 2 * Math.PI / 37 - (1 - frein) * 5 * 2 * Math.PI - (t.depart || 0) * 0.17;
      const rayon = R - (avance >= 1 ? 0 : 6 + 4 * Math.sin(depuis * 0.3) * (1 - avance));
      const a = rotation + rel;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(Math.round(cx + Math.cos(a) * rayon) - 2, Math.round(cy + Math.sin(a) * rayon) - 2, 4, 4);
    }
    // Le tapis : ce qu'on a mise, et ce que ça paie.
    const tx = x0 + 128;
    const pari = t ? t.pari : pariDeRoulette();
    const nomPari = typeof pari === 'number' ? 'NUMÉRO ' + pari : pari.toUpperCase();
    titre(ctx, 'TON PARI', tx, y0, ENCRE.gris);
    Atlas.texte(ctx, nomPari, tx, y0 + 10, ENCRE.or, 2);
    titre(ctx, 'CHANCES SIMPLES', tx, y0 + 40); titre(ctx, '1 POUR 1', tx + 4, y0 + 50, ENCRE.papier);
    titre(ctx, 'NUMÉRO PLEIN', tx, y0 + 64); titre(ctx, (r.plein - 1) + ' POUR 1', tx + 4, y0 + 74, ENCRE.papier);
    titre(ctx, 'LE ZÉRO PREND', tx, y0 + 88); titre(ctx, 'LES CHANCES', tx, y0 + 98);
    if (t && avance >= 1) {
      const coul = couleurDe(t.n);
      ctx.fillStyle = '#1b1b24'; ctx.fillRect(cx - 12, cy - 9, 24, 18);          // le numero sur un fond, pas sur la croix
      Atlas.texte(ctx, String(t.n), cx - Atlas.largeurTexte(String(t.n), 2) / 2, cy - 5, coul === 'rouge' ? '#ff7a6a' : coul === 'vert' ? '#7ae08a' : ENCRE.papier, 2);
    }
    return !t || avance >= 1;
  }

  //: Les faces d'un de, 3 × 3.
  const FACES = [null, ['...', '.#.', '...'], ['#..', '...', '..#'], ['#..', '.#.', '..#'], ['#.#', '...', '#.#'],
                 ['#.#', '.#.', '#.#'], ['#.#', '#.#', '#.#']];

  /** Un de de 20 × 20, ses points de 4 × 4 SEPARES (colles, le six se lisait comme deux barres). Le un et le
      quatre en rouge, comme les des qu'on joue au sic bo. */
  function de(ctx, x, y, face) {
    ctx.fillStyle = '#3a3450'; ctx.fillRect(x - 1, y - 1, 22, 22);
    ctx.fillStyle = ENCRE.papier; ctx.fillRect(x, y, 20, 20);
    ctx.fillStyle = face === 1 || face === 4 ? ENCRE.rouge : ENCRE.noir;
    FACES[face].forEach(function (ligne, yy) {
      for (let xx = 0; xx < 3; xx++) if (ligne[xx] === '#') ctx.fillRect(x + 2 + xx * 6, y + 2 + yy * 6, 4, 4);
    });
  }

  function dessinerSicBo(ctx, x0, y0, t, depuis) {
    const fini = !t || depuis >= ANIME.sic_bo;
    // La cloche : on la secoue (elle tremble), puis on la leve, et les des sont la.
    if (t && !fini) {
      // Une cloche en dome : des rangees de plus en plus larges vers le bas, un reflet, et la poignee.
      const dx = Math.round(Math.sin(depuis * 1.3) * 3);
      for (let k = 0; k < 11; k++) {
        const demi = Math.round(14 + 16 * Math.sqrt(k / 10));
        ctx.fillStyle = k === 10 ? '#8a6a2a' : '#b89a4a';
        ctx.fillRect(x0 + 50 + dx - demi, y0 + 18 + k * 4, 2 * demi, 4);
      }
      ctx.fillStyle = '#e0c060'; ctx.fillRect(x0 + 36 + dx, y0 + 24, 6, 16);
      ctx.fillStyle = '#6b4a2a'; ctx.fillRect(x0 + 44 + dx, y0 + 10, 12, 8);
    } else if (t) {
      t.des.forEach(function (d, i) { de(ctx, x0 + 10 + i * 30, y0 + 26, d); });
    } else {
      [1, 2, 3].forEach(function (d, i) { de(ctx, x0 + 10 + i * 30, y0 + 26, d); });
    }
    const tx = x0 + 128, pari = t ? t.pari : pariDeSicBo();
    titre(ctx, 'TON PARI', tx, y0);
    Atlas.texte(ctx, typeof pari === 'number' ? 'LE ' + pari : pari.toUpperCase(), tx, y0 + 10, ENCRE.or, 2);
    titre(ctx, 'PETIT, GRAND', tx, y0 + 40); titre(ctx, '1 POUR 1', tx + 4, y0 + 50, ENCRE.papier);
    titre(ctx, 'UN TRIPLE LES PERD', tx, y0 + 60);
    titre(ctx, 'UN CHIFFRE', tx, y0 + 76); titre(ctx, '1, 2 OU 3 POUR 1', tx + 4, y0 + 86, ENCRE.papier);
    titre(ctx, 'SELON LES DÉS', tx + 4, y0 + 96, ENCRE.papier);
    return fini;
  }

  // --- La salle : ce qu'il y a sur chaque table --------------------------------------------------------------

  //: Les points des tables dans la salle, et leur type.
  const JEUX = { blackjack: true, roulette: true, poker: true, sic_bo: true, baccara: true };

  /** Sur le feutre de chaque table (le glyphe `!`, un bloc), ce qui dit a quoi on y joue : le sabot et les
      cercles du blackjack, la roue de la roulette (qui tourne quand on y joue), les trois cartes du poker, la
      cloche du sic bo, les cases JOUEUR et BANQUE du baccara. ⚠️ Par-dessus le sol de la piece, jamais cuit
      dedans : la roue bouge. */
  function dessinerSalle(ctx, vue) {
    const piece = B.interieur;
    if (!piece || !piece.points) return;
    for (const p of piece.points) {
      if (!JEUX[p.type]) continue;
      const x = p.x * TT - Math.round(vue.x), y = (p.y - 1) * TT - Math.round(vue.y);   // la tuile du haut de la table
      if (x < -64 || x > VW + 64 || y < -64 || y > VH + 64) continue;
      if (p.type === 'blackjack') {
        ctx.fillStyle = '#e8e0c8'; for (let k = -2; k <= 2; k++) ctx.fillRect(x + 6 + k * 14, y + 22, 5, 3);   // les cercles des mises
        ctx.fillStyle = '#3a3450'; ctx.fillRect(x + 30, y + 3, 7, 5);                                         // le sabot
        ctx.fillStyle = '#c0392b'; ctx.fillRect(x - 10, y + 3, 3, 3); ctx.fillStyle = '#2a5ab8'; ctx.fillRect(x - 6, y + 3, 3, 3);   // les jetons
      } else if (p.type === 'roulette') {
        const cx = x - 20, cy = y + 16, tourne = enCours('roulette') && B.menu ? 0.2 : 0.01;
        ctx.fillStyle = '#6b4a2a'; ctx.fillRect(cx - 7, cy - 7, 14, 14);
        ctx.fillStyle = '#1b1b24'; ctx.fillRect(cx - 5, cy - 5, 10, 10);
        const a = (B.image || 0) * tourne;
        ctx.fillStyle = '#c0392b'; ctx.fillRect(Math.round(cx + Math.cos(a) * 4) - 1, Math.round(cy + Math.sin(a) * 4) - 1, 2, 2);
        ctx.fillStyle = '#b89a4a'; ctx.fillRect(cx - 1, cy - 1, 2, 2);
        ctx.fillStyle = '#e8e0c8'; for (let k = 0; k < 4; k++) ctx.fillRect(x + 2 + k * 8, y + 6, 1, 18);   // la grille des numeros
        ctx.fillStyle = '#c0392b'; ctx.fillRect(x + 4, y + 9, 3, 3); ctx.fillRect(x + 20, y + 17, 3, 3);
        ctx.fillStyle = '#1b1b24'; ctx.fillRect(x + 12, y + 9, 3, 3); ctx.fillRect(x + 28, y + 17, 3, 3);
      } else if (p.type === 'poker') {
        ctx.fillStyle = '#efe6d0'; for (let k = -1; k <= 1; k++) ctx.fillRect(x + 5 + k * 6, y + 18, 5, 7);
        ctx.fillStyle = '#c0392b'; ctx.fillRect(x + 1, y + 20, 1, 2);
      } else if (p.type === 'sic_bo') {
        ctx.fillStyle = '#b89a4a'; ctx.fillRect(x + 3, y + 5, 10, 8);                          // la cloche
        ctx.fillStyle = '#e0c060'; ctx.fillRect(x + 6, y + 3, 4, 2);
        ctx.fillStyle = '#e8e0c8'; ctx.fillRect(x - 12, y + 20, 10, 5); ctx.fillRect(x + 18, y + 20, 10, 5);   // PETIT, GRAND
      } else {
        ctx.fillStyle = '#e8e0c8'; ctx.fillRect(x - 14, y + 18, 12, 6); ctx.fillRect(x + 18, y + 18, 12, 6);  // JOUEUR, BANQUE
        ctx.fillStyle = '#e8b33c'; ctx.fillRect(x + 4, y + 18, 8, 6);                                           // l'egalite
      }
    }
    B.stats.rects += 30;
  }

  return { regles, etat, compteur, paquet, numeroDuTour, desDuJet, bjValeur, bjNaturel, bjCroupier, bjRegler, bjJouer,
           couleurDe, roulettePaie, sicBoPaie, pokerForce, pokerOuvre, pokerRegler, bacPoint, bacCoup, bacRegler,
           bjDonner, bjTirer, bjRester, lancer, secouer, pkDonner, pkDecider, bacDonner, enCours, menu, dessinerSalle };
})();
