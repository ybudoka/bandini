/* Banc d'essai de Bandini sous Node — un faux navigateur, juste assez vrai.

   Charge les scripts DANS L'ORDRE DE templates/index.html (la source unique),
   avec un faux canvas, un faux DOM, un faux fetch qui sert le paquet de
   definitions recu de Python (ENTREE.defs), une fausse manette pilotable et un
   requestAnimationFrame CAPTURE : la boucle ne tourne jamais toute seule, c'est
   `frame(n)` qui l'avance. Math.random est ensemence : le banc est un juge.

   Utilisation (depuis tests/harnais_js.py) :
     banc(function (L, o) { ... return resultat; })
   ou L = window.BANDINI et o = { frame, touche, relacher, tape, pad, pointeur, doc, fenetre, fetchs } */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

function faireC2d() {
  const c = { fillStyle: '#000', strokeStyle: '#000', lineWidth: 1, globalAlpha: 1, font: '', textAlign: 'left',
              globalCompositeOperation: 'source-over', imageSmoothingEnabled: false };
  ['save', 'restore', 'translate', 'rotate', 'scale', 'transform', 'setTransform', 'beginPath', 'closePath', 'moveTo',
   'lineTo', 'arc', 'ellipse', 'rect', 'fill', 'stroke', 'clip', 'clearRect', 'strokeRect', 'fillText', 'strokeText',
   'drawImage', 'quadraticCurveTo', 'bezierCurveTo', 'putImageData', 'resetTransform'].forEach(function (m) { c[m] = function () {}; });
  c.rects = 0;
  c.fillRect = function () { c.rects++; };
  c.measureText = function (s) { return { width: String(s).length * 4 }; };
  c.createLinearGradient = function () { return { addColorStop: function () {} }; };
  c.createRadialGradient = function () { return { addColorStop: function () {} }; };
  c.createPattern = function () { return { setTransform: function () {} }; };
  const image = function (w, h) { return { width: w | 0, height: h | 0, data: new Uint8ClampedArray(Math.max(0, (w | 0) * (h | 0) * 4)) }; };
  c.createImageData = image;
  c.getImageData = function (x, y, w, h) { return image(w, h); };
  return c;
}

function faireCanvas(w, h) {
  const ctx = faireC2d();
  return { tagName: 'CANVAS', width: w | 0, height: h | 0, style: {}, dataset: {}, getContext: function () { return ctx; },
           addEventListener: function () {}, setPointerCapture: function () {},
           getBoundingClientRect: function () { return { left: 0, top: 0, width: this.width, height: this.height }; } };
}

function faireElement(tag, id) {
  const ecouteurs = {};
  const el = {
    tagName: tag.toUpperCase(), id: id || '', hidden: false, textContent: '', innerHTML: '', value: '',
    dataset: {}, style: {}, enfants: [], classes: new Set(),
    classList: { add: function (c) { el.classes.add(c); }, remove: function (c) { el.classes.delete(c); },
                 contains: function (c) { return el.classes.has(c); } },
    addEventListener: function (t, f) { (ecouteurs[t] = ecouteurs[t] || []).push(f); },
    removeEventListener: function () {},
    dispatch: function (t, ev) { (ecouteurs[t] || []).forEach(function (f) { f(ev); }); },
    appendChild: function (e) { el.enfants.push(e); return e; },
    querySelector: function () { return null; },
    querySelectorAll: function () { return []; },
    setPointerCapture: function () {}, releasePointerCapture: function () {},
    getBoundingClientRect: function () { return { left: 20, top: 500, width: 140, height: 140, right: 160, bottom: 640 }; },
    focus: function () {}, blur: function () {},
  };
  return el;
}

function banc(corps) {
  const racine = ENTREE.racine;
  const defs = ENTREE.defs;
  const html = fs.readFileSync(path.join(racine, 'templates', 'index.html'), 'utf8');
  const SCRIPTS = Array.from(html.matchAll(/filename='js\/([^']+)'/g)).map(function (m) { return m[1]; });
  if (!SCRIPTS.length) throw new Error('aucun script trouve dans templates/index.html');

  // --- Faux DOM ---------------------------------------------------------------------
  const elements = {};
  const toile = faireCanvas(480, 270);
  toile.id = 'toile';
  elements.toile = toile;
  const bandini = faireElement('main', 'bandini');
  bandini.dataset = { etat: 'chargement', urlDefinitions: '/api/definitions', urlScores: '/api/scores' };
  elements.bandini = bandini;
  const tactile = faireElement('div', 'tactile');
  const boutonsTactiles = ['attaque', 'action', 'esquive', 'arme', 'pause', 'plein'].map(function (a) {
    const b = faireElement('b'); b.dataset.a = a; return b;
  });
  tactile.querySelectorAll = function (sel) { return sel.indexOf('data-a') >= 0 ? boutonsTactiles : []; };
  elements.tactile = tactile;
  const croix = faireElement('div', 'croix');
  const pouce = faireElement('u');
  croix.querySelector = function () { return pouce; };
  elements.croix = croix;
  ['voile-titre', 'voile-scores', 'voile-score-envoi', 'bouton-jouer', 'bouton-scores', 'bouton-fermer-scores',
   'bouton-annuler-score', 'score-form', 'pseudo', 'score-etat', 'liste-scores', 'etat-chargement'].forEach(function (id) {
    elements[id] = faireElement(id.indexOf('bouton') === 0 ? 'button' : id === 'pseudo' ? 'input' : 'div', id);
  });
  const body = faireElement('body');
  const documentElement = faireElement('html');
  const ecouteursDoc = {};
  const doc = {
    body: body, documentElement: documentElement, hidden: false, readyState: 'complete',
    getElementById: function (id) { return elements[id] || null; },
    createElement: function (tag) { return tag === 'canvas' ? faireCanvas(0, 0) : faireElement(tag); },
    querySelector: function (sel) {
      const m = /data-a="([a-z]+)"/.exec(sel);
      return m ? boutonsTactiles.find(function (b) { return b.dataset.a === m[1]; }) || null : null;
    },
    addEventListener: function (t, f) { (ecouteursDoc[t] = ecouteursDoc[t] || []).push(f); },
    removeEventListener: function () {},
  };

  // --- Fausse fenetre -----------------------------------------------------------------
  const ecouteurs = {};
  let rafCb = null, horloge = 0;
  const store = {};
  const fetchs = [];
  const pads = [];
  const FauxMath = Object.create(Math);
  (function () { let a = (ENTREE.graine || 0x1a2b3c4d) >>> 0; FauxMath.random = function () {
    a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; })();

  const fenetre = {
    innerWidth: 1280, innerHeight: 720, devicePixelRatio: 1,
    document: doc, console: console, Math: FauxMath, Date: Date, JSON: JSON, Object: Object, Array: Array,
    Uint8Array: Uint8Array, Uint8ClampedArray: Uint8ClampedArray, Int32Array: Int32Array, Float32Array: Float32Array,
    Map: Map, Set: Set, Promise: Promise, Error: Error, String: String, Number: Number, Boolean: Boolean,
    Event: function (t) { this.type = t; }, performance: { now: function () { return horloge; } },
    setTimeout: function () { return 0; }, clearTimeout: function () {}, setInterval: function () { return 0; }, clearInterval: function () {},
    requestAnimationFrame: function (cb) { rafCb = cb; return 1; }, cancelAnimationFrame: function () {},
    localStorage: { getItem: function (k) { return k in store ? store[k] : null; }, setItem: function (k, v) { store[k] = String(v); },
                    removeItem: function (k) { delete store[k]; } },
    navigator: { getGamepads: function () { return pads; }, vibrate: function () {} },
    matchMedia: function () { return { matches: false }; },
    fetch: function (url, opts) {
      fetchs.push({ url: url, opts: opts });
      if (String(url).indexOf('definitions') >= 0) return Promise.resolve({ ok: true, json: function () { return Promise.resolve(defs); } });
      return Promise.resolve({ ok: true, json: function () { return Promise.resolve({ scores: [], rang: 1 }); } });
    },
    addEventListener: function (t, f) { (ecouteurs[t] = ecouteurs[t] || []).push(f); },
    removeEventListener: function () {}, dispatchEvent: function () {},
    screen: {},
  };
  fenetre.window = fenetre;
  fenetre.globalThis = fenetre;
  vm.createContext(fenetre);

  for (const s of SCRIPTS) {
    vm.runInContext(fs.readFileSync(path.join(racine, 'static', 'js', s), 'utf8'), fenetre, { filename: s });
  }
  const L = fenetre.BANDINI;
  if (!L) throw new Error('window.BANDINI absent apres chargement');

  // --- Outils -----------------------------------------------------------------------------
  function evenement(type, extra) { return Object.assign({ type: type, preventDefault: function () {}, target: null, repeat: false }, extra || {}); }
  function frame(n) {
    for (let i = 0; i < (n || 1); i++) {
      if (!rafCb) throw new Error('boucle non armee');
      horloge += 1000 / 60;
      const cb = rafCb;
      cb(horloge);
    }
  }
  function touche(code) { (ecouteurs.keydown || []).forEach(function (f) { f(evenement('keydown', { code: code })); }); }
  function relacher(code) { (ecouteurs.keyup || []).forEach(function (f) { f(evenement('keyup', { code: code })); }); }
  function tape(code, images) { touche(code); frame(1); relacher(code); frame(images || 1); }
  function pad(axes, boutons) {
    pads.length = 0;
    if (axes) pads.push({ connected: true, axes: axes, buttons: (boutons || []).map(function (v) { return { pressed: v > 0.5, value: v }; }) });
  }
  function pointeur(type, x, y, id) { croix.dispatch(type, evenement(type, { clientX: x, clientY: y, pointerId: id || 1 })); }
  function bouton(a, type) { const b = boutonsTactiles.find(function (q) { return q.dataset.a === a; }); b.dispatch(type, evenement(type, { pointerId: 2 })); }
  function singe(images, graine, codes) {
    let a = (graine || 7) >>> 0;
    const rnd = function () { a = (a * 1664525 + 1013904223) >>> 0; return a / 4294967296; };
    const touches = codes || ['KeyW', 'KeyA', 'KeyS', 'KeyD', 'ShiftLeft', 'Space', 'KeyE', 'Tab'];
    const tenues = {};
    for (let i = 0; i < images; i++) {
      if (rnd() < 0.09) { const k = touches[Math.floor(rnd() * touches.length)]; if (tenues[k]) { relacher(k); tenues[k] = false; } else { touche(k); tenues[k] = true; } }
      frame(1);
    }
    for (const k in tenues) if (tenues[k]) relacher(k);
    frame(1);
  }

  const outils = { frame: frame, touche: touche, relacher: relacher, tape: tape, pad: pad, pointeur: pointeur, bouton: bouton, singe: singe,
                   doc: doc, fenetre: fenetre, fetchs: fetchs, elements: elements, store: store, ctx: toile.getContext('2d') };

  // Le demarrage est asynchrone (fetch) : on attend la promesse du jeu.
  return Promise.resolve().then(function () { return new Promise(function (r) { setImmediate(r); }); })
    .then(function () { return new Promise(function (r) { setImmediate(r); }); })
    .then(function () {
      if (L.B.etat === 'chargement') throw new Error('le jeu n\'a pas fini de charger : ' + JSON.stringify(fetchs));
      return corps(L, outils);
    });
}

function rapporter(promesse) {
  promesse.then(function (r) { console.log(JSON.stringify(r === undefined ? null : r)); })
    .catch(function (e) { console.error(e && e.stack || e); process.exit(1); });
}
