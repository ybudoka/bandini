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
  const MAP_MANETTE = { 0: 'action', 1: 'esquive', 2: 'attaque', 3: 'arme', 4: 'arme', 5: 'attaque',
                        8: 'carte', 9: 'pause', 12: 'haut', 13: 'bas', 14: 'gauche', 15: 'droite' };
  const ZONE_MORTE = 0.2, ZONE_PLEINE = 0.95;
  const TOUCHES_JEU = new Set([].concat.apply([], Object.values(MAP_TOUCHES)));

  const enfonce = {}, presse = {};       // clavier, par e.code
  const vPad = {}, vTact = {}, vNeuf = {}; // manette / tactile, par action
  const axe = { x: 0, y: 0, mag: 0, source: 'clavier' };
  const stick = { x: 0, y: 0, mag: 0 };
  const pouce = { x: 0, y: 0, mag: 0, actif: false };
  let gaz = 0, frein = 0;
  let manetteVue = false, tactile = false, contexteCourant = 'pied';
  let nav = null, doc = null, fenetre = null;

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

  function lireManette() {
    if (!nav || !nav.getGamepads) return;
    const etat = {};
    let branchee = false, sx = 0, sy = 0, g = 0, f = 0;
    const pads = nav.getGamepads() || [];
    for (let i = 0; i < pads.length; i++) {
      const p = pads[i];
      if (!p || p.connected === false) continue;
      branchee = true;
      for (let b = 0; b < p.buttons.length; b++) {
        const bt = p.buttons[b], a = MAP_MANETTE[b];
        if (a && bt && (bt.pressed || bt.value > 0.5)) etat[a] = true;
      }
      const ax = p.axes[0] || 0, ay = p.axes[1] || 0;
      const h = Math.hypot(ax, ay);
      if (h > ZONE_MORTE) {
        const m = borner((h - ZONE_MORTE) / (ZONE_PLEINE - ZONE_MORTE), 0, 1);
        sx = ax / h * m; sy = ay / h * m;
      }
      if (p.buttons[7]) g = Math.max(g, p.buttons[7].value || 0);
      if (p.buttons[6]) f = Math.max(f, p.buttons[6].value || 0);
    }
    if (!branchee && !manetteVue) return;
    manetteVue = branchee;
    for (const a in MAP_TOUCHES) poser(vPad, a, etat[a]);
    stick.x = sx; stick.y = sy; stick.mag = Math.hypot(sx, sy);
    gaz = g; frein = f;
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
    MAP_TOUCHES, MAP_MANETTE, ZONE_MORTE,
    init, debutImage, bas, neuf, videPresse, toutRelacher, contexte, passerEnTactile,
    lireManette, vibrer, pleinEcran,
    get axe() { return axe; }, get gaz() { return gaz; }, get frein() { return frein; },
    get estTactile() { return tactile; },
    _sacs: function () { return { enfonce: enfonce, presse: presse, vPad: vPad, vTact: vTact, vNeuf: vNeuf, pouce: pouce, stick: stick }; },
  };
})();
