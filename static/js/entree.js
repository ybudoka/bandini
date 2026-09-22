/* Bandini — entrees : clavier, manette, tactile, fusionnes par ACTION.

   Trois sacs separes (Loren) : un pad au repos n'efface pas ce que le doigt
   tient, et le clavier reste vivant pendant qu'on touche.
   Par-dessus, un axe ANALOGIQUE `axe = { x, y, mag }` calcule une fois par
   image : clavier (vecteur unitaire), stick (zone morte radiale, module
   conserve) ou joystick tactile (decalage du pouce / rayon). */

const Entree = (function () {
  'use strict';

  const MAP_TOUCHES = {
    gauche: ['ArrowLeft', 'KeyA', 'KeyQ'],
    droite: ['ArrowRight', 'KeyD'],
    haut: ['ArrowUp', 'KeyW', 'KeyZ'],
    bas: ['ArrowDown', 'KeyS'],
    action: ['KeyE', 'Enter', 'KeyC'],
    attaque: ['Space', 'KeyX', 'KeyJ'],
    esquive: ['ShiftLeft', 'ShiftRight', 'KeyV', 'KeyK'],
    arme: ['Tab', 'KeyF'],
    pause: ['Escape', 'KeyP'],
    annuler: ['Backspace', 'KeyB'],
    muet: ['KeyM'],
    carte: ['KeyN'],
    // ⚠️ PAS KeyT NI AUCUNE LETTRE D'UNE SUITE SECRETE (`Jeu.SEQUENCE_DEBUG`,
    // ecoutee par `surSecret`) : elles doivent rester hors de `MAP_TOUCHES`
    // (voir le commentaire au-dessus de `secrets`, plus bas dans ce fichier),
    // sans quoi les taper declenche AUSSI cette action-ci.
    verrouiller: ['KeyH'],
  };
  //: La disposition d'une manette RECONNUE par le navigateur (`mapping:
  //: "standard"`, W3C) : 0 le bouton du bas, 1 celui de droite, 2 celui de
  //: gauche, 3 celui du haut, 4/5 les boutons d'epaule, 6/7 les gachettes,
  //: 8 SELECT, 9 START, 12-15 la croix.
  //:
  //: ⚠️ Une manette Bluetooth que le navigateur NE reconnait pas rend
  //: `mapping: ""` et numerote ses boutons comme elle veut — la meme manette
  //: n'a pas les memes numeros sur le telephone et sur le Mac. Ca ne se devine
  //: pas : l'ecran MANETTE des options fait REAPPRENDRE chaque bouton en
  //: l'appuyant, et garde le resultat dans les options (`options.manette`).
  const MANETTE_DEFAUT = {
    action: [0], esquive: [1], annuler: [1], attaque: [2, 5], arme: [3, 4],
    carte: [8], pause: [9], muet: [], verrouiller: [10],
    haut: [12], bas: [13], gauche: [14], droite: [15],
  };
  //: Le stick de marche, puis le gaz et le frein. Sur une manette reconnue ce
  //: sont les gachettes 7 et 6 ; ailleurs, souvent des AXES — d'ou les deux
  //: types, et le repos mesure au moment ou on les apprend (une gachette-axe
  //: repose a -1 sur une manette et a 0 sur la suivante).
  const AXES_DEFAUT = [0, 1];
  const PEDALES_DEFAUT = { gaz: { type: 'bouton', i: 7 }, frein: { type: 'bouton', i: 6 } };
  const ZONE_MORTE = 0.2, ZONE_PLEINE = 0.95;
  //: De combien un bouton ou un axe doit bouger pour qu'on dise « c'est
  //: celui-la » pendant un apprentissage.
  const GESTE = 0.5;
  const TOUCHES_JEU = new Set([].concat.apply([], Object.values(MAP_TOUCHES)));

  const enfonce = {}, presse = {};       // clavier, par e.code
  const vPad = {}, vTact = {}, vNeuf = {}; // manette / tactile, par action
  //: ⚠️ Les nouveautes du TACTILE a part : l'ecran MANETTE doit pouvoir
  //: ignorer la manette (on y appuie sur ses boutons pour les VOIR, pas pour
  //: commander) sans devenir injouable au doigt.
  const vNeufTact = {};
  //: Le quatrieme sac : les manettes Touch d'un casque Meta Quest (voir
  //: `lireCasque`), et ses nouveautes a part pour la meme raison que le tactile.
  const vCasque = {}, vNeufCasque = {};
  const axe = { x: 0, y: 0, mag: 0, source: 'clavier' };
  const stick = { x: 0, y: 0, mag: 0 };
  const pouce = { x: 0, y: 0, mag: 0, actif: false };
  let gaz = 0, frein = 0;
  let manetteVue = false, tactile = false, contexteCourant = 'pied';
  let nav = null, doc = null, fenetre = null;
  let profil = null;                 // { boutons, axes, gaz, frein } — voir profilParDefaut
  let parIndice = {};                // indice de bouton -> actions, refait avec le profil
  let apprentissage = null;          // { quoi, fait, reference }
  //: Le REPOS de la manette : ce que valent ses axes quand on ne touche a
  //: rien. ⚠️ Ca ne se suppose pas — une gachette repose a -1 sur une manette
  //: et a 0 sur la suivante, et une croix-chapeau repose HORS de son anneau. On
  //: le MESURE : une demi-seconde sans qu'un axe bouge et sans bouton enfonce.
  let reposManette = null, reposCandidat = null, reposStable = 0;
  const REPOS_IMAGES = 30;
  const ignores = {};                // le bouton qu'on vient d'apprendre, jusqu'au relachement
  const info = { branchee: false, id: '', mapping: '', boutons: [], axes: [] };
  //: L'APPAREIL QU'ON TIENT : le dernier qui a servi — 'clavier', 'manette' ou
  //: 'tactile'. L'ecran COMMANDES et l'invite du HUD montrent SES boutons, et
  //: changent sous les yeux quand on pose le clavier pour prendre la manette.
  //: ⚠️ Pas « une manette est branchee » : celui qui joue au clavier avec une
  //: manette qui dort sur le bureau ne veut pas lire des A et des B.
  let appareil = null;
  //: Ce que la manette tenait a l'image d'avant (boutons, croix, stick pousse,
  //: gachettes) : elle ne reprend l'appareil que sur un geste NEUF.
  let actifAvant = [];

  function poser(sac, a, v) {
    v = !!v;
    if (v && !sac[a]) {
      vNeuf[a] = true;
      if (sac === vTact) vNeufTact[a] = true;
      if (sac === vCasque) vNeufCasque[a] = true;
    }
    sac[a] = v;
  }

  function bas(a) {
    return !!vPad[a] || !!vTact[a] || !!vCasque[a] || MAP_TOUCHES[a].some(function (k) { return enfonce[k]; });
  }
  function neuf(a) {
    return !!vNeuf[a] || MAP_TOUCHES[a].some(function (k) { return presse[k]; });
  }
  /** Comme `neuf`, mais la manette ne compte pas — le clavier, le doigt et les
      mains du casque, oui : l'ecran MANETTE montre la manette Bluetooth, pas elles. */
  /** Le DOIGT seul : dans un menu, les boutons ARME et COURS deviennent HAUT et
      BAS (voir `contexte`). A la manette et au clavier, ces boutons-la gardent
      leur sens — le bouton de droite d'une manette est aussi RETOUR. */
  function basTactile(a) { return !!vTact[a]; }
  function neufTactile(a) { return !!vNeufTact[a]; }
  function neufSansManette(a) {
    return !!vNeufTact[a] || !!vNeufCasque[a] || MAP_TOUCHES[a].some(function (k) { return presse[k]; });
  }
  function videPresse() {
    for (const k in presse) presse[k] = false;
    for (const a in vNeuf) vNeuf[a] = false;
    for (const a in vNeufTact) vNeufTact[a] = false;
    for (const a in vNeufCasque) vNeufCasque[a] = false;
  }
  function toutRelacher() {
    for (const k in enfonce) enfonce[k] = false;
    for (const a in vPad) vPad[a] = false;
    for (const a in vTact) vTact[a] = false;
    for (const a in vCasque) vCasque[a] = false;
    videPresse();
  }

  // --- Clavier ---------------------------------------------------------------------

  function surTouche(e, valeur) {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
    if (!TOUCHES_JEU.has(e.code)) return;
    e.preventDefault();
    if (valeur) appareil = 'clavier';
    if (valeur && !enfonce[e.code] && !e.repeat) presse[e.code] = true;
    enfonce[e.code] = valeur;
  }

  // --- Secret -------------------------------------------------------------------------

  //: Une SUITE de touches a taper dans l'ordre, pour reveiller quelque chose de
  //: cache (le menu DEBUG) — jamais dans MAP_TOUCHES, qui associe une touche a
  //: une ACTION, pas une suite ordonnee. Les fleches qu'elle utilise bougent le
  //: joueur au passage : les deux sacs sont independants, ca ne genre rien.
  const SECRET_DELAI = 1500;      // trop lent entre deux touches et on repart a zero
  let secretTampon = [], secretDernier = 0;
  const secrets = [];

  /** Enregistre une suite (tableau de `e.code`) et la fonction appelee des
      qu'elle est tapee au complet. */
  function surSecret(suite, fait) { secrets.push({ suite: suite.slice(), fait: fait }); }

  function surToucheSecrete(e) {
    if (!secrets.length || e.repeat) return;
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
    const t = Date.now();
    if (t - secretDernier > SECRET_DELAI) secretTampon.length = 0;
    secretDernier = t;
    secretTampon.push(e.code);
    for (const s of secrets) {
      const n = s.suite.length, q = secretTampon.length;
      if (q < n) continue;
      let pareil = true;
      for (let i = 0; i < n; i++) if (secretTampon[q - n + i] !== s.suite[i]) { pareil = false; break; }
      if (pareil) { secretTampon.length = 0; s.fait(); }
    }
  }

  // --- Secret par ACTIONS (manette + tactile) -------------------------------------

  //: La meme suite secrete, mais en ACTIONS plutot qu'en touches : ce que la
  //: manette, le stick du casque ou le joystick tactile donnent. On la lit UNE
  //: FOIS PAR IMAGE (`debutImage`), quand `neuf` est encore frais, sur les
  //: actions qui viennent de s'enclencher — un Konami directionnel marche ainsi
  //: au pouce comme au doigt, et au clavier aussi (les fleches sont des actions).
  const SECRET_ACTIONS_DELAI = 1500;
  let tamponActions = [], dernierActions = 0;
  const suitesActions = [];

  /** Enregistre une suite d'ACTIONS (`haut`, `bas`, `gauche`, `droite`…) a
      enchainer dans l'ordre pour reveiller quelque chose de cache. */
  function surSuiteActions(suite, fait) { suitesActions.push({ suite: suite.slice(), fait: fait }); }

  //: Le STICK pour la suite d'actions. ⚠️ La suite se lisait sur `neuf`, qui ne
  //: VIENT QUE DES BOUTONS (la croix, le clavier, le doigt) : un stick
  //: analogique ne « presse » jamais haut/bas/gauche/droite, il ne fait que
  //: pousser `axe`. On traduit donc le stick en direction cardinale, avec une
  //: MORTE confortable (il faut pousser franchement) et une HYSTERESIS (une
  //: direction ne compte qu'une fois par poussee, jusqu'au relachement). Le
  //: cardinal dominant absorbe les diagonales : un Konami mal ajuste de
  //: quelques degres reste lu « haut » ou « droite », jamais « diagonal ».
  let directionStick = null, directionStickEmise = null;
  const STICK_MORTE = 0.55;     // il faut vraiment pousser pour choisir
  const STICK_RELACHE = 0.3;    // ... et vraiment lacher pour pouvoir recompter

  function directionDuStick() {
    const st = stickCasque.mag > stick.mag ? stickCasque : stick;
    const m = Math.hypot(st.x, st.y);
    // Zone morte : sous le relachement, on rend la main et on oublie.
    if (m < STICK_RELACHE) { directionStick = null; return null; }
    // Entre les deux : on GARDE la direction deja verrouillee (hysteresis).
    if (m < STICK_MORTE) return directionStick;
    let d;
    if (Math.abs(st.x) > Math.abs(st.y)) d = st.x > 0 ? 'droite' : 'gauche';
    else d = st.y > 0 ? 'bas' : 'haut';
    directionStick = d;
    return d;
  }

  function lireSuitesActions() {
    if (!suitesActions.length) return;
    const fraiches = [];
    for (const a in MAP_TOUCHES) if (neuf(a)) fraiches.push(a);
    // Le stick : sa direction ne va au tampon que quand elle VIENT de changer
    // (une fois par poussee) — pas a chaque image.
    const d = directionDuStick();
    if (d !== directionStickEmise) {
      directionStickEmise = d;
      if (d) fraiches.push(d);
    }
    if (!fraiches.length) return;
    const t = Date.now();
    if (t - dernierActions > SECRET_ACTIONS_DELAI) tamponActions.length = 0;
    dernierActions = t;
    for (const a of fraiches) {
      tamponActions.push(a);
      for (const s of suitesActions) {
        const n = s.suite.length, q = tamponActions.length;
        if (q < n) continue;
        let pareil = true;
        for (let i = 0; i < n; i++) if (tamponActions[q - n + i] !== s.suite[i]) { pareil = false; break; }
        if (pareil) { tamponActions.length = 0; s.fait(); break; }
      }
    }
  }

  // --- Manette ----------------------------------------------------------------------

  function profilParDefaut() {
    const boutons = {};
    for (const a in MANETTE_DEFAUT) boutons[a] = MANETTE_DEFAUT[a].slice();
    return { boutons: boutons, axes: AXES_DEFAUT.slice(),
             gaz: Object.assign({}, PEDALES_DEFAUT.gaz),
             frein: Object.assign({}, PEDALES_DEFAUT.frein),
             croix: null };
  }

  /** Charge un profil de manette (celui des options, ou rien pour les defauts)
      et refait la table `indice -> actions` que `lireManette` consulte. */
  function reglerManette(p) {
    profil = profilParDefaut();
    if (p && p.boutons) {
      for (const a in profil.boutons) {
        if (Array.isArray(p.boutons[a])) profil.boutons[a] = p.boutons[a].slice();
      }
    }
    if (p && Array.isArray(p.axes) && p.axes.length === 2) profil.axes = p.axes.slice();
    for (const cle of ['gaz', 'frein']) {
      const s = p && p[cle];
      if (s && (s.type === 'bouton' || s.type === 'axe')) profil[cle] = Object.assign({}, s);
    }
    if (p && p.croix && typeof p.croix.i === 'number' && p.croix.valeurs) {
      profil.croix = { i: p.croix.i, valeurs: Object.assign({}, p.croix.valeurs) };
    }
    parIndice = {};
    for (const a in profil.boutons) {
      for (const i of profil.boutons[a]) (parIndice[i] = parIndice[i] || []).push(a);
    }
    return profil;
  }

  function profilManette() {
    if (!profil) reglerManette(null);
    return JSON.parse(JSON.stringify(profil));
  }

  function valeurBouton(p, i) {
    const bt = p.buttons && p.buttons[i];
    if (!bt) return 0;
    return bt.value !== undefined && bt.value !== null ? bt.value : (bt.pressed ? 1 : 0);
  }

  /** Une pedale : un bouton analogique, ou un axe dont on a mesure le repos. */
  function lirePedale(p, source) {
    if (!source) return 0;
    if (source.type !== 'axe') return valeurBouton(p, source.i);
    const v = p.axes[source.i];
    if (v === undefined || v === null) return 0;
    const plage = (source.plein === undefined ? 1 : source.plein) - (source.repos || 0);
    if (!plage) return 0;
    return borner((v - (source.repos || 0)) / plage, 0, 1);
  }

  const CROIX_ACTIONS = ['haut', 'bas', 'gauche', 'droite'];
  //: L'ordre des huit positions d'une croix-chapeau, dans le sens des
  //: aiguilles d'une montre a partir du haut.
  const TOUR_CROIX = [['haut'], ['haut', 'droite'], ['droite'], ['droite', 'bas'],
                      ['bas'], ['bas', 'gauche'], ['gauche'], ['gauche', 'haut']];
  const TOL_CROIX = 0.12;

  /** Une croix-CHAPEAU : UN seul axe pour huit directions.

      ⚠️ Beaucoup de manettes en Bluetooth — les 8BitDo entre autres — rendent
      la croix comme ca : on appuie dessus et AUCUN numero de bouton ne bouge,
      ce qui donne exactement l'impression qu'elle est morte. Ici on apprend une
      direction a la fois ; des qu'on connait HAUT et DROITE, on deduit le tour
      complet (huit positions regulierement espacees sur l'axe), diagonales
      comprises. Si le tour ne se verifie pas sur les directions qu'on connait
      aussi, on retombe sur la correspondance exacte : les quatre cotes
      marchent, pas les diagonales — mieux vaut ca qu'une croix qui ment. */
  function lireCroix(p, etat) {
    const c = profil.croix;
    if (!c) return;
    const v = p.axes[c.i];
    if (v === undefined || v === null) return;
    const vals = c.valeurs;
    const pas = (vals.haut !== undefined && vals.droite !== undefined)
      ? (vals.droite - vals.haut) / 2 : 0;
    if (pas && tourCoherent(vals, pas)) {
      const k = Math.round((v - vals.haut) / pas);
      if (k >= 0 && k <= 7 && Math.abs(vals.haut + k * pas - v) <= TOL_CROIX) {
        for (const a of TOUR_CROIX[k]) etat[a] = true;
      }
      return;
    }
    for (const a in vals) if (Math.abs(v - vals[a]) <= TOL_CROIX) etat[a] = true;
  }

  /** Le tour deduit de HAUT et DROITE place-t-il BAS et GAUCHE la ou ils sont ? */
  function tourCoherent(vals, pas) {
    const attendus = { bas: 4, gauche: 6 };
    for (const a in attendus) {
      if (vals[a] === undefined) continue;
      if (Math.abs(vals[a] - (vals.haut + attendus[a] * pas)) > TOL_CROIX) return false;
    }
    return true;
  }

  /** Le prochain bouton (ou, pour le gaz, le frein et le stick, le prochain
      axe pousse) devient `quoi`. Rend une fonction qui annule l'attente.

      ⚠️ Tant qu'on apprend, la manette ne COMMANDE plus rien : sans cela, le
      bouton qu'on apprend valide aussi la ligne du menu ou on l'apprend. */
  function apprendre(quoi, fait) {
    apprentissage = { quoi: quoi, fait: fait || null, reference: null };
    for (const a in vPad) vPad[a] = false;
    return function () { apprentissage = null; };
  }

  function apprendEnCours() { return apprentissage ? apprentissage.quoi : null; }

  function annulerApprentissage() { apprentissage = null; }

  /** Oublie le repos mesure — a faire quand on change de manette. */
  function oublierRepos() { reposManette = null; reposCandidat = null; reposStable = 0; }

  function poserAppris(quoi, source) {
    if (!profil) reglerManette(null);
    if (quoi === 'gaz' || quoi === 'frein') {
      profil[quoi] = source;
    } else if (quoi === 'stick') {
      const i = source.i;
      profil.axes = i % 2 === 0 ? [i, i + 1] : [i - 1, i];
    } else if (source.type === 'axe' && CROIX_ACTIONS.indexOf(quoi) >= 0) {
      // Une direction apprise sur un AXE : c'est une croix-chapeau.
      if (!profil.croix || profil.croix.i !== source.i) profil.croix = { i: source.i, valeurs: {} };
      profil.croix.valeurs[quoi] = source.plein;
      profil.boutons[quoi] = [];
    } else if (source.type === 'bouton') {
      // Un bouton ne fait qu'une chose : on le retire de partout ailleurs.
      for (const a in profil.boutons) {
        profil.boutons[a] = profil.boutons[a].filter(function (k) { return k !== source.i; });
      }
      profil.boutons[quoi] = [source.i];
      ignores[source.i] = true;
    } else {
      return false;
    }
    reglerManette(profil);
    return true;
  }

  /** Suit le repos tant qu'on n'apprend rien : c'est la reference de tout. */
  function suivreRepos(p) {
    for (let b = 0; b < (p.buttons || []).length; b++) {
      if (valeurBouton(p, b) > GESTE) { reposCandidat = null; reposStable = 0; return; }
    }
    const axes = (p.axes || []);
    const pareil = reposCandidat && reposCandidat.length === axes.length
      && axes.every(function (v, i) { return Math.abs(v - reposCandidat[i]) < 0.05; });
    if (pareil) {
      if (++reposStable >= REPOS_IMAGES) reposManette = { axes: reposCandidat.slice() };
    } else {
      reposCandidat = axes.slice();
      reposStable = 0;
    }
  }

  /** La manette est-elle revenue au repos qu'on lui connait ? */
  function auRepos(p) {
    if (!reposManette) return true;
    for (let b = 0; b < (p.buttons || []).length; b++) if (valeurBouton(p, b) > GESTE) return false;
    const axes = p.axes || [];
    for (let k = 0; k < axes.length; k++) {
      const r = reposManette.axes[k];
      if (r !== undefined && Math.abs(axes[k] - r) > GESTE) return false;
    }
    return true;
  }

  /** Regarde ce qui a bouge depuis le debut de l'apprentissage.

      ⚠️ On n'arme pas tant que la manette n'est pas REVENUE AU REPOS. Sans ca,
      « tout reapprendre » prenait le RELACHEMENT de la direction precedente
      pour le geste suivant : sur une croix-chapeau, lacher le haut fait bouger
      l'axe autant qu'appuyer sur le bas, et BAS se retrouvait appris sur la
      valeur du repos — une croix qui tient tout enfoncee, tout le temps. */
  function ecouterApprentissage(p) {
    const a = apprentissage;
    const axes = (p.axes || []);
    if (!a.reference) {
      if (!auRepos(p)) { a.attend = true; return; }
      a.attend = false;
      a.reference = { boutons: (p.buttons || []).map(function (_, i) { return valeurBouton(p, i); }),
                      axes: axes.slice() };
      if (!reposManette) reposManette = { axes: axes.slice() };
      return;
    }
    for (let b = 0; b < (p.buttons || []).length; b++) {
      const avant = a.reference.boutons[b] || 0;
      if (valeurBouton(p, b) > GESTE && avant <= GESTE) {
        const source = { type: 'bouton', i: b };
        const pose = poserAppris(a.quoi, source);
        // ⚠️ On vide AVANT le rappel : un rappel qui enchaine (« tout
        // reapprendre ») verrait sinon son propre apprentissage efface juste
        // apres, et la suite s'arreterait au premier bouton.
        apprentissage = null;
        if (pose && a.fait) a.fait(source);
        return;
      }
    }
    // Le gaz, le frein, le stick — et les directions, qui sont souvent un
    // seul axe (croix-chapeau) plutot que quatre boutons.
    if (a.quoi !== 'gaz' && a.quoi !== 'frein' && a.quoi !== 'stick'
        && CROIX_ACTIONS.indexOf(a.quoi) < 0) return;
    for (let k = 0; k < axes.length; k++) {
      const repos = a.reference.axes[k] === undefined ? 0 : a.reference.axes[k];
      if (Math.abs(axes[k] - repos) > GESTE) {
        // Un axe qui revient a SON repos connu n'est pas un geste, c'est un
        // relachement : on ne l'apprend pas.
        const connu = reposManette && reposManette.axes[k];
        if (connu !== undefined && Math.abs(axes[k] - connu) <= GESTE) continue;
        const source = { type: 'axe', i: k, repos: repos, plein: axes[k] };
        const pose = poserAppris(a.quoi, source);
        apprentissage = null;
        if (pose && a.fait) a.fait(source);
        return;
      }
    }
  }

  function lireManette() {
    if (!nav || !nav.getGamepads) return;
    if (!profil) reglerManette(null);
    const etat = {};
    let branchee = false, sx = 0, sy = 0, g = 0, f = 0;
    const pads = nav.getGamepads() || [];
    info.branchee = false; info.id = ''; info.mapping = ''; info.boutons = []; info.axes = [];
    for (let i = 0; i < pads.length; i++) {
      const p = pads[i];
      if (!p || p.connected === false) continue;
      branchee = true;
      if (!info.branchee) {
        info.branchee = true;
        info.id = p.id || '';
        info.mapping = p.mapping || '';
        info.axes = (p.axes || []).map(function (v) { return Math.round((v || 0) * 100) / 100; });
      }
      for (let b = 0; b < (p.buttons || []).length; b++) {
        const v = valeurBouton(p, b);
        if (v > GESTE && info.boutons.indexOf(b) < 0) info.boutons.push(b);
        if (ignores[b]) { if (v <= GESTE) delete ignores[b]; continue; }
        const actions = parIndice[b];
        if (actions && v > GESTE) for (const a of actions) etat[a] = true;
      }
      const s = zoneMorte(p.axes[profil.axes[0]] || 0, p.axes[profil.axes[1]] || 0);
      if (s.mag > 0) { sx = s.x; sy = s.y; }
      lireCroix(p, etat);
      if (!apprentissage) suivreRepos(p);
      g = Math.max(g, lirePedale(p, profil.gaz));
      f = Math.max(f, lirePedale(p, profil.frein));
      if (apprentissage) ecouterApprentissage(p);
    }
    if (!branchee && !manetteVue) return;
    manetteVue = branchee;
    // ⚠️ SUR UN GESTE NEUF, pas sur un etat : un stick qui derive au repos, ou
    // un bouton que la manette rend enfonce en permanence, reprenaient
    // l'appareil a CHAQUE image — et l'aide montrait des A et des B a qui tape
    // au clavier (vu dans Chromium, une vraie manette branchee au Mac).
    const actif = info.boutons.slice();
    for (const a of CROIX_ACTIONS) if (etat[a]) actif.push(a);
    if (Math.hypot(sx, sy) > 0.5) actif.push('stick');
    if (g > 0.5) actif.push('gaz');
    if (f > 0.5) actif.push('frein');
    if (branchee && actif.some(function (a) { return actifAvant.indexOf(a) < 0; })) appareil = 'manette';
    actifAvant = actif;
    // Pendant un apprentissage la manette ne commande rien (voir `apprendre`).
    for (const a in MAP_TOUCHES) poser(vPad, a, apprentissage ? false : etat[a]);
    if (apprentissage) { stick.x = 0; stick.y = 0; stick.mag = 0; gaz = 0; frein = 0; return; }
    stick.x = sx; stick.y = sy; stick.mag = Math.hypot(sx, sy);
    gaz = g; frein = f;
  }

  /** Zone morte RADIALE : sous `ZONE_MORTE` rien, au-dela le module repart de
      zero jusqu'a `ZONE_PLEINE` — la direction, elle, est gardee telle quelle. */
  function zoneMorte(ax, ay) {
    const h = Math.hypot(ax, ay);
    if (h <= ZONE_MORTE) return { x: 0, y: 0, mag: 0 };
    const m = borner((h - ZONE_MORTE) / (ZONE_PLEINE - ZONE_MORTE), 0, 1);
    return { x: ax / h * m, y: ay / h * m, mag: m };
  }

  // --- Casque (les manettes Touch d'un Meta Quest) ----------------------------------

  //: ⚠️ Un sac a part, et pas une manette de plus dans `lireManette` : les Touch
  //: n'ont qu'UNE disposition, connue d'avance. `casque.js` les rend comme une
  //: manette Xbox et on la lit TOUJOURS avec la disposition par defaut — le
  //: profil reappris est celui d'une manette Bluetooth, il n'a rien a dire des
  //: Touch. Et elles restent vivantes pendant un apprentissage : dans le casque,
  //: ce sont les seules mains qui peuvent encore l'annuler.
  const stickCasque = { x: 0, y: 0, mag: 0 };
  let gazCasque = 0, freinCasque = 0, padCasque = null, lireSourceCasque = null, vibreurCasque = null;

  /** `lire()` rend la manette du casque (`{ id, mapping, buttons, axes }`), ou
      null hors du casque ; `vibrer(ms)` fait trembler les mains. */
  function brancherCasque(lire, vibrer) {
    lireSourceCasque = lire || null;
    vibreurCasque = vibrer || null;
  }

  function lireCasque() {
    const p = lireSourceCasque ? lireSourceCasque() : null;
    if (!p && !padCasque) return;
    padCasque = p;
    const etat = {};
    let s = { x: 0, y: 0, mag: 0 };
    if (p) {
      for (const a in MANETTE_DEFAUT) {
        if (MANETTE_DEFAUT[a].some(function (i) { return valeurBouton(p, i) > GESTE; })) etat[a] = true;
      }
      s = zoneMorte(p.axes[AXES_DEFAUT[0]] || 0, p.axes[AXES_DEFAUT[1]] || 0);
    }
    for (const a in MAP_TOUCHES) poser(vCasque, a, etat[a]);
    if (s.mag > 0 || Object.keys(etat).length) appareil = 'manette';
    stickCasque.x = s.x; stickCasque.y = s.y; stickCasque.mag = s.mag;
    gazCasque = p ? lirePedale(p, PEDALES_DEFAUT.gaz) : 0;
    freinCasque = p ? lirePedale(p, PEDALES_DEFAUT.frein) : 0;
  }

  /** Ce que la manette dit d'elle-meme — l'ecran MANETTE le montre tel quel.
      `mapping` vide = le navigateur ne la reconnait pas, ses numeros de
      boutons ne veulent rien dire, il faut les reapprendre. */
  function manetteInfo() {
    // ⚠️ Dans le casque, les Touch ne sont pas dans `getGamepads()` : sans ce
    // repli, l'ecran MANETTE dirait AUCUNE MANETTE a qui en tient deux.
    if (!info.branchee && padCasque) {
      const p = padCasque;
      return { branchee: true, id: p.id, mapping: p.mapping,
               boutons: p.buttons.map(function (_, i) { return i; })
                 .filter(function (i) { return valeurBouton(p, i) > GESTE; }),
               axes: p.axes.map(function (v) { return Math.round((v || 0) * 100) / 100; }),
               apprend: apprentissage ? apprentissage.quoi : null,
               attend: !!(apprentissage && apprentissage.attend) };
    }
    return { branchee: info.branchee, id: info.id, mapping: info.mapping,
             boutons: info.boutons.slice(), axes: info.axes.slice(),
             apprend: apprentissage ? apprentissage.quoi : null,
             attend: !!(apprentissage && apprentissage.attend) };
  }

  /** L'appareil qu'on tient (voir `appareil`). Avant le premier geste : la
      manette si le navigateur en voit une, le doigt sur un ecran tactile,
      sinon le clavier. */
  function appareilCourant() {
    if (appareil) return appareil;
    if (manetteVue || padCasque) return 'manette';
    return tactile ? 'tactile' : 'clavier';
  }

  /** Les lettres de la manette : 'xbox', 'playstation' ou 'nintendo'
      (`manettes.FAMILLES`). Celle qu'on a choisie dans OPTIONS > MANETTE, sinon
      celle que son nom trahit (`manettes.DETECTION`), sinon Xbox.

      ⚠️ Rien ne devine une Nintendo : la 8BitDo de Martin se presente parfois
      en « Pro Controller » et porte pourtant les lettres Xbox. */
  function familleManette() {
    const bloc = (B.defs && B.defs.manettes) || {};
    const familles = bloc.familles || {};
    const choisie = B.options && B.options.lettresManette;
    if (choisie && familles[choisie]) return choisie;
    const id = info.id || (padCasque && padCasque.id) || '';
    for (const d of bloc.detection || []) {
      if (new RegExp(d.motif, 'i').test(id)) return d.famille;
    }
    return bloc.famille_defaut || 'xbox';
  }

  // --- Tactile ----------------------------------------------------------------------

  function passerEnTactile() {
    appareil = 'tactile';
    if (tactile) return;
    tactile = true;
    if (doc && doc.body) doc.body.classList.add('tactile');
    if (fenetre && fenetre.dispatchEvent) {
      try { fenetre.dispatchEvent(new Event('resize')); } catch (e) { /* banc */ }
    }
  }

  function initTactile(d) {
    const zone = d.getElementById('tactile');
    if (!zone) return;
    if (fenetre && fenetre.matchMedia && fenetre.matchMedia('(pointer: coarse)').matches) passerEnTactile();
    fenetre.addEventListener('touchstart', passerEnTactile, { once: true, passive: true });
    // ⚠️ Une fois, c'est pour la classe `tactile` ; le doigt qui REVIENT apres
    // le clavier ou la manette, lui, doit se lire a chaque fois.
    fenetre.addEventListener('touchstart', function () { appareil = 'tactile'; }, { passive: true });

    const croix = d.getElementById('croix');
    const bouton = croix.querySelector('u');
    let doigt = null;
    function capter(el, id) { try { el.setPointerCapture(id); } catch (e) { /* rien */ } }
    function suivre(ev) {
      const r = croix.getBoundingClientRect();
      let dx = ev.clientX - (r.left + r.width / 2), dy = ev.clientY - (r.top + r.height / 2);
      const max = r.width / 2 - 14;
      const dist = Math.hypot(dx, dy);
      if (dist > max) { dx *= max / dist; dy *= max / dist; }
      if (bouton) bouton.style.transform = 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px)';
      const m = borner((Math.hypot(dx, dy) - 8) / (max - 8), 0, 1);
      const h = Math.hypot(dx, dy) || 1;
      pouce.x = dx / h * m; pouce.y = dy / h * m; pouce.mag = m; pouce.actif = true;
      direction('gauche', -pouce.x); direction('droite', pouce.x);
      direction('haut', -pouce.y); direction('bas', pouce.y);
    }
    //: ⚠️ Un seuil qui ENTRE a 0.5 et qui ne SORT que sous 0.35 : un pouce pose
    //: sur la vitre tremble, et autour d'un seuil unique chaque tremblement
    //: etait un nouvel appui — une ligne de menu de plus, sans rien demander.
    function direction(a, v) { poser(vTact, a, v > (vTact[a] ? 0.35 : 0.5)); }
    function lacher(ev) {
      if (doigt !== null && ev.pointerId !== doigt) return;
      doigt = null;
      if (bouton) bouton.style.transform = '';
      pouce.x = 0; pouce.y = 0; pouce.mag = 0; pouce.actif = false;
      ['gauche', 'droite', 'haut', 'bas'].forEach(function (a) { poser(vTact, a, false); });
    }
    croix.addEventListener('pointerdown', function (ev) {
      ev.preventDefault(); doigt = ev.pointerId; capter(croix, doigt); passerEnTactile();
      Son.reveiller(); vibrer(8); suivre(ev);
    });
    croix.addEventListener('pointermove', function (ev) { if (ev.pointerId === doigt) { ev.preventDefault(); suivre(ev); } });
    croix.addEventListener('pointerup', lacher);
    croix.addEventListener('pointercancel', lacher);

    zone.querySelectorAll('b[data-a]').forEach(function (b) {
      const a = b.dataset.a;
      b.addEventListener('pointerdown', function (ev) {
        ev.preventDefault(); capter(b, ev.pointerId); b.classList.add('on'); passerEnTactile();
        Son.reveiller(); vibrer(12);
        if (a === 'plein') pleinEcran(); else poser(vTact, a, true);
      });
      const fin = function (ev) { ev.preventDefault(); b.classList.remove('on'); if (a !== 'plein') poser(vTact, a, false); };
      b.addEventListener('pointerup', fin);
      b.addEventListener('pointercancel', fin);
    });

    d.addEventListener('touchmove', function (e) {
      if (d.body.classList.contains('tactile')) e.preventDefault();
    }, { passive: false });
  }

  function pleinEcran() {
    const el = doc && doc.documentElement;
    if (!el) return;
    const demande = el.requestFullscreen || el.webkitRequestFullscreen;
    if (demande) { try { demande.call(el); } catch (e) { /* rien */ } }
    if (fenetre.screen && fenetre.screen.orientation && fenetre.screen.orientation.lock) {
      fenetre.screen.orientation.lock('landscape').catch(function () {});
    }
  }

  function vibrer(ms) {
    if (!B.options.vibration) return;
    // Dans le casque, ce sont les mains qui tremblent.
    if (padCasque && vibreurCasque) { vibreurCasque(ms); return; }
    if (!nav || !nav.vibrate) return;
    try { nav.vibrate(ms); } catch (e) { /* rien */ }
  }

  /** Zoom refuse partout : pincement, double-tap, Ctrl+molette, Ctrl +/-. */
  function empecherZoom(d, w) {
    ['gesturestart', 'gesturechange', 'gestureend'].forEach(function (n) {
      d.addEventListener(n, function (e) { e.preventDefault(); }, { passive: false });
    });
    d.addEventListener('touchmove', function (e) { if (e.touches && e.touches.length > 1) e.preventDefault(); }, { passive: false });
    let dernierTap = 0;
    d.addEventListener('touchend', function (e) {
      const t = Date.now();
      if (t - dernierTap < 320) e.preventDefault();
      dernierTap = t;
    }, { passive: false });
    d.addEventListener('dblclick', function (e) { e.preventDefault(); });
    w.addEventListener('wheel', function (e) { if (e.ctrlKey || e.metaKey) e.preventDefault(); }, { passive: false });
    w.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && ['Equal', 'Minus', 'Digit0', 'NumpadAdd', 'NumpadSubtract'].includes(e.code)) e.preventDefault();
    });
  }

  // --- Par image -------------------------------------------------------------------------

  /** Calcule l'axe analogique. Priorite : doigt, puis stick, puis clavier. */
  function debutImage() {
    lireManette();
    lireCasque();
    // Le stick d'une manette Bluetooth et celui du casque : le plus pousse
    // gagne, et c'est un stick de MANETTE dans les deux cas (marcher a mi-course,
    // promener un menu).
    const st = stickCasque.mag > stick.mag ? stickCasque : stick;
    if (pouce.actif && pouce.mag > 0) {
      axe.x = pouce.x; axe.y = pouce.y; axe.mag = pouce.mag; axe.source = 'tactile';
    } else if (st.mag > 0 && !B.coop) {
      axe.x = st.x; axe.y = st.y; axe.mag = st.mag; axe.source = 'manette';
    } else {
      // ⚠️ La coop locale (essai, un clavier + une manette) : le joueur 1 ne
      // repond QU'AU CLAVIER — la manette est celle du deuxieme joueur
      // (`Entites.majJoueur2`, qui lit `Entree.stick` directement). `bas()`
      // compte aussi la manette (son stick ET sa croix) : en coop on lit
      // `enfonce` tout cru pour ne rien lui laisser passer.
      const touche = B.coop
        ? function (a) { return MAP_TOUCHES[a].some(function (k) { return enfonce[k]; }); }
        : bas;
      let x = 0, y = 0;
      if (touche('gauche')) x -= 1; if (touche('droite')) x += 1;
      if (touche('haut')) y -= 1; if (touche('bas')) y += 1;
      const h = Math.hypot(x, y);
      axe.x = h ? x / h : 0; axe.y = h ? y / h : 0; axe.mag = h ? 1 : 0; axe.source = 'clavier';
    }
    lireSuitesActions();
  }

  /** Ce qu'on lit sur les quatre boutons tactiles dans ce contexte-la. L'ecran
      COMMANDES les montre tels quels : au doigt, le nom du bouton EST son geste. */
  function etiquettes(nom) {
    return nom === 'vehicule'
      ? { attaque: 'KLAXON', action: 'SORTIR', esquive: 'FREIN', arme: 'RADIO' }
      // ⚠️ Sur un char a sirene, le bouton du klaxon EST celui de la sirene :
      // c'est ce qu'on cherche en premier au volant d'une ambulance, et le
      // klaxon d'une auto-patrouille n'a jamais servi a rien.
      : nom === 'vehicule_sirene'
      ? { attaque: 'SIRÈNE', action: 'SORTIR', esquive: 'FREIN', arme: 'RADIO' }
      : nom === 'vehicule_sonnette'                       // un velo : sa sonnette
      ? { attaque: 'SONNETTE', action: 'SORTIR', esquive: 'FREIN', arme: 'RADIO' }
      : nom === 'menu'
        ? { attaque: 'RETOUR', action: 'CHOISIR', esquive: 'BAS', arme: 'HAUT' }
        : nom === 'dialogue'
          ? { attaque: 'PASSER', action: 'SUIVANT', esquive: '·', arme: '·' }
          // ⚠️ Le piratage se joue au STICK (une direction a la fois, comme la
          // roue d'armes) : FRAPPE est le seul bouton qui compte encore, et il
          // change de sens — abandonner, pas frapper.
          : nom === 'piratage'
            ? { attaque: 'ABANDONNER', action: '·', esquive: '·', arme: '·' }
            // Le mode photo (M14) : pas de FRAPPE ni d'ESQUIVE, on ne fait
            // que regarder.
            : nom === 'photo'
              ? { attaque: '·', action: 'CAPTURER', esquive: '·', arme: 'FILTRE' }
              // ⚠️ « SPRINT », plus « COURS » : courir est devenu la vitesse par
              // defaut (la ville fait 421 tuiles), et le bouton ne sert plus qu'a
              // la bouffee qui coute du souffle.
              : { attaque: 'FRAPPE', action: 'ACTION', esquive: 'SPRINT', arme: 'ARME' };
  }

  function contexte(nom) {
    if (nom === contexteCourant || !doc) { contexteCourant = nom; return; }
    contexteCourant = nom;
    const e = etiquettes(nom);
    Object.keys(e).forEach(function (a) {
      const b = doc.querySelector('#boutons b[data-a="' + a + '"]');
      if (b) b.textContent = e[a];
    });
  }

  function init(d, w, n) {
    doc = d; fenetre = w; nav = n;
    w.addEventListener('keydown', function (e) { surToucheSecrete(e); surTouche(e, true); });
    w.addEventListener('keyup', function (e) { surTouche(e, false); });
    w.addEventListener('blur', toutRelacher);
    w.addEventListener('gamepadconnected', function () { manetteVue = true; appareil = 'manette'; Son.reveiller(); });
    initTactile(d);
    empecherZoom(d, w);
  }

  return {
    MAP_TOUCHES, MANETTE_DEFAUT, ZONE_MORTE,
    init, debutImage, bas, neuf, basTactile, neufTactile, neufSansManette, videPresse, toutRelacher, contexte, passerEnTactile,
    etiquettesTactiles: etiquettes,
    toucheEnfoncee: function (code) { return !!enfonce[code]; },
    surSecret, surSuiteActions,
    lireManette, vibrer, pleinEcran,
    reglerManette, profilManette, profilParDefaut, apprendre, apprendEnCours,
    annulerApprentissage, oublierRepos, manetteInfo, brancherCasque, familleManette,
    get appareil() { return appareilCourant(); },
    get axe() { return axe; },
    //: La coop locale (essai, un clavier + une manette) : le stick de LA
    //: manette, brut — celui que `axe` (au-dessus) fusionne aussi au clavier
    //: pour le joueur 1, hors coop. `Entites.majJoueur2` le lit directement.
    get stick() { return stick; },
    get gaz() { return Math.max(gaz, gazCasque); }, get frein() { return Math.max(frein, freinCasque); },
    get estTactile() { return tactile; },
    _sacs: function () { return { enfonce: enfonce, presse: presse, vPad: vPad, vTact: vTact, vNeuf: vNeuf, vCasque: vCasque, pouce: pouce, stick: stick, stickCasque: stickCasque }; },
  };
})();
