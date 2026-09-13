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
    carte: [8], pause: [9], muet: [],
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
  const axe = { x: 0, y: 0, mag: 0, source: 'clavier' };
  const stick = { x: 0, y: 0, mag: 0 };
  const pouce = { x: 0, y: 0, mag: 0, actif: false };
  let gaz = 0, frein = 0;
  let manetteVue = false, tactile = false, contexteCourant = 'pied';
  let nav = null, doc = null, fenetre = null;
  let profil = null;                 // { boutons, axes, gaz, frein } — voir profilParDefaut
  let parIndice = {};                // indice de bouton -> actions, refait avec le profil
  let apprentissage = null;          // { quoi, fait, reference }
  const ignores = {};                // le bouton qu'on vient d'apprendre, jusqu'au relachement
  const info = { branchee: false, id: '', mapping: '', boutons: [], axes: [] };

  function poser(sac, a, v) {
    v = !!v;
    if (v && !sac[a]) vNeuf[a] = true;
    sac[a] = v;
  }

  function bas(a) {
    return !!vPad[a] || !!vTact[a] || MAP_TOUCHES[a].some(function (k) { return enfonce[k]; });
  }
  function neuf(a) {
    return !!vNeuf[a] || MAP_TOUCHES[a].some(function (k) { return presse[k]; });
  }
  function videPresse() {
    for (const k in presse) presse[k] = false;
    for (const a in vNeuf) vNeuf[a] = false;
  }
  function toutRelacher() {
    for (const k in enfonce) enfonce[k] = false;
    for (const a in vPad) vPad[a] = false;
    for (const a in vTact) vTact[a] = false;
    videPresse();
  }

  // --- Clavier ---------------------------------------------------------------------

  function surTouche(e, valeur) {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
    if (!TOUCHES_JEU.has(e.code)) return;
    e.preventDefault();
    if (valeur && !enfonce[e.code] && !e.repeat) presse[e.code] = true;
    enfonce[e.code] = valeur;
  }

  // --- Manette ----------------------------------------------------------------------

  function profilParDefaut() {
    const boutons = {};
    for (const a in MANETTE_DEFAUT) boutons[a] = MANETTE_DEFAUT[a].slice();
    return { boutons: boutons, axes: AXES_DEFAUT.slice(),
             gaz: Object.assign({}, PEDALES_DEFAUT.gaz),
             frein: Object.assign({}, PEDALES_DEFAUT.frein) };
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

  function poserAppris(quoi, source) {
    if (!profil) reglerManette(null);
    if (quoi === 'gaz' || quoi === 'frein') {
      profil[quoi] = source;
    } else if (quoi === 'stick') {
      const i = source.i;
      profil.axes = i % 2 === 0 ? [i, i + 1] : [i - 1, i];
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

  /** Regarde ce qui a bouge depuis le debut de l'apprentissage. */
  function ecouterApprentissage(p) {
    const a = apprentissage;
    const axes = (p.axes || []);
    if (!a.reference) {
      a.reference = { boutons: (p.buttons || []).map(function (_, i) { return valeurBouton(p, i); }),
                      axes: axes.slice() };
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
    if (a.quoi !== 'gaz' && a.quoi !== 'frein' && a.quoi !== 'stick') return;
    for (let k = 0; k < axes.length; k++) {
      const repos = a.reference.axes[k] === undefined ? 0 : a.reference.axes[k];
      if (Math.abs(axes[k] - repos) > GESTE) {
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
      const ax = p.axes[profil.axes[0]] || 0, ay = p.axes[profil.axes[1]] || 0;
      const h = Math.hypot(ax, ay);
      if (h > ZONE_MORTE) {
        const m = borner((h - ZONE_MORTE) / (ZONE_PLEINE - ZONE_MORTE), 0, 1);
        sx = ax / h * m; sy = ay / h * m;
      }
      g = Math.max(g, lirePedale(p, profil.gaz));
      f = Math.max(f, lirePedale(p, profil.frein));
      if (apprentissage) ecouterApprentissage(p);
    }
    if (!branchee && !manetteVue) return;
    manetteVue = branchee;
    // Pendant un apprentissage la manette ne commande rien (voir `apprendre`).
    for (const a in MAP_TOUCHES) poser(vPad, a, apprentissage ? false : etat[a]);
    if (apprentissage) { stick.x = 0; stick.y = 0; stick.mag = 0; gaz = 0; frein = 0; return; }
    stick.x = sx; stick.y = sy; stick.mag = Math.hypot(sx, sy);
    gaz = g; frein = f;
  }

  /** Ce que la manette dit d'elle-meme — l'ecran MANETTE le montre tel quel.
      `mapping` vide = le navigateur ne la reconnait pas, ses numeros de
      boutons ne veulent rien dire, il faut les reapprendre. */
  function manetteInfo() {
    return { branchee: info.branchee, id: info.id, mapping: info.mapping,
             boutons: info.boutons.slice(), axes: info.axes.slice(),
             apprend: apprentissage ? apprentissage.quoi : null };
  }

  // --- Tactile ----------------------------------------------------------------------

  function passerEnTactile() {
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
      poser(vTact, 'gauche', pouce.x < -0.5); poser(vTact, 'droite', pouce.x > 0.5);
      poser(vTact, 'haut', pouce.y < -0.5); poser(vTact, 'bas', pouce.y > 0.5);
    }
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
    if (!B.options.vibration || !nav || !nav.vibrate) return;
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
    if (pouce.actif && pouce.mag > 0) {
      axe.x = pouce.x; axe.y = pouce.y; axe.mag = pouce.mag; axe.source = 'tactile';
    } else if (stick.mag > 0) {
      axe.x = stick.x; axe.y = stick.y; axe.mag = stick.mag; axe.source = 'manette';
    } else {
      let x = 0, y = 0;
      if (bas('gauche')) x -= 1; if (bas('droite')) x += 1;
      if (bas('haut')) y -= 1; if (bas('bas')) y += 1;
      const h = Math.hypot(x, y);
      axe.x = h ? x / h : 0; axe.y = h ? y / h : 0; axe.mag = h ? 1 : 0; axe.source = 'clavier';
    }
  }

  function contexte(nom) {
    if (nom === contexteCourant || !doc) { contexteCourant = nom; return; }
    contexteCourant = nom;
    const etiquettes = nom === 'vehicule'
      ? { attaque: 'KLAXON', action: 'SORTIR', esquive: 'FREIN', arme: 'RADIO' }
      : nom === 'menu'
        ? { attaque: 'RETOUR', action: 'CHOISIR', esquive: 'BAS', arme: 'HAUT' }
        : nom === 'dialogue'
          ? { attaque: 'PASSER', action: 'SUIVANT', esquive: '·', arme: '·' }
          : { attaque: 'FRAPPE', action: 'ACTION', esquive: 'COURS', arme: 'ARME' };
    Object.keys(etiquettes).forEach(function (a) {
      const b = doc.querySelector('#boutons b[data-a="' + a + '"]');
      if (b) b.textContent = etiquettes[a];
    });
  }

  function init(d, w, n) {
    doc = d; fenetre = w; nav = n;
    w.addEventListener('keydown', function (e) { surTouche(e, true); });
    w.addEventListener('keyup', function (e) { surTouche(e, false); });
    w.addEventListener('blur', toutRelacher);
    w.addEventListener('gamepadconnected', function () { manetteVue = true; Son.reveiller(); });
    initTactile(d);
    empecherZoom(d, w);
  }

  return {
    MAP_TOUCHES, MANETTE_DEFAUT, ZONE_MORTE,
    init, debutImage, bas, neuf, videPresse, toutRelacher, contexte, passerEnTactile,
    lireManette, vibrer, pleinEcran,
    reglerManette, profilManette, profilParDefaut, apprendre, apprendEnCours,
    annulerApprentissage, manetteInfo,
    get axe() { return axe; }, get gaz() { return gaz; }, get frein() { return frein; },
    get estTactile() { return tactile; },
    _sacs: function () { return { enfonce: enfonce, presse: presse, vPad: vPad, vTact: vTact, vNeuf: vNeuf, pouce: pouce, stick: stick }; },
  };
})();
