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
  // ⚠️ `traces` : pose un tableau ici et chaque `fillRect` s'y ecrit. C'est la
  // seule facon de JUGER UN DESSIN sous Node — le canevas du banc ne garde
  // aucun pixel. Sert a comparer deux cuissons d'une meme tuile (une cloture
  // nord-sud ne se peint pas comme une est-ouest).
  c.traces = null;
  c.fillRect = function (x, y, w, h) {
    c.rects++;
    if (c.traces) c.traces.push([Math.round(x), Math.round(y), Math.round(w), Math.round(h), String(c.fillStyle)]);
  };
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
    tagName: tag.toUpperCase(), id: id || '', hidden: false, textContent: '', value: '',
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
  // ⚠️ `innerHTML = ''` VIDE la liste des enfants : sans ca, l'ecran du compte
  // empilerait ses trois cases a chaque mise a jour et le banc ne le verrait pas.
  let html = '';
  Object.defineProperty(el, 'innerHTML', {
    get: function () { return html; },
    set: function (v) { html = String(v); if (!html) el.enfants.length = 0; },
  });
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
  bandini.dataset = { etat: 'chargement', urlDefinitions: '/api/definitions', urlCarte: '/api/carte',
                      urlCompte: '/api/compte/' };
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
  ['voile-titre', 'bouton-jouer', 'etat-chargement',
   'avis-son', 'bouton-casque',
   // L'ecran du compte (M14, 2e vague).
   'voile-compte', 'bouton-compte', 'bouton-fermer-compte', 'compte-form', 'compte-pseudo', 'compte-passe',
   'compte-courriel', 'compte-etat', 'compte-mot', 'compte-parties', 'bouton-compte-inscription',
   'bouton-compte-connexion', 'bouton-compte-deconnexion'].forEach(function (id) {
    const entree = id.indexOf('compte-pseudo') === 0 || id === 'compte-passe' || id === 'compte-courriel';
    elements[id] = faireElement(id.indexOf('bouton') === 0 ? 'button' : entree ? 'input' : 'div', id);
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
  // ⚠️ `ENTREE.stockage` : ce que le navigateur avait DEJA avant que la page
  // charge (une partie d'avant, trois emplacements). Le jeu lit sa partie au
  // demarrage : l'ecrire apres coup, dans le corps d'un test, arrive trop tard.
  const store = Object.assign({}, ENTREE.stockage || {});
  const session = Object.assign({}, ENTREE.session || {});
  let rechargements = 0;
  const fetchs = [];
  const pads = [];
  /*: LE FAUX SERVEUR DE COMPTES (M14). `ENTREE.reseau` pose les reponses AVANT le
    chargement — l'ouverture part des la ville batie, un test qui les poserait
    apres arriverait trop tard. Une entree vaut { statut, corps } ou { panne: true }
    (le serveur ne repond pas du tout), et la cle est le chemin sous /api/compte/
    ('ouvrir', 'parties/1'...) ou '*' pour toutes. */
  const reseau = Object.assign({}, ENTREE.reseau || {});
  const appelsCompte = [];
  const beacons = [];
  //: `tenu: true` dans `ENTREE.reseau` : la reponse attend `o.compte.rendre(…)`.
  //: ⚠️ Il faut l'armer AVANT le chargement — l'ouverture part des la ville batie,
  //: et c'est justement ce qu'on veut voir attendre.
  const tenues = {};
  for (const chemin in reseau) if (reseau[chemin] && reseau[chemin].tenu) tenues[chemin] = [];
  //: ⚠️ La cle peut porter sa methode (`'GET parties/1'`) : la meme adresse rend
  //: la partie du serveur en GET et accepte ou refuse un instantane en POST, et
  //: un test qui ne peut pas les distinguer ferait passer une montee pour une
  //: descente reussie. A defaut, la cle nue sert les deux, puis '*'.
  function reponseDe(chemin, methode) {
    const cles = [methode + ' ' + chemin, chemin, '*'];
    for (const c of cles) if (reseau[c] !== undefined) return reseau[c];
    return { statut: 200, corps: chemin === 'ouvrir' ? { compte: null } : {} };
  }
  function servirCompte(chemin, methode) {
    const r = reponseDe(chemin, methode);
    if (r && r.panne) return Promise.reject(new Error('reseau coupe'));
    const statut = r && typeof r.statut === 'number' ? r.statut : 200;
    const corps = r && r.corps !== undefined ? r.corps : {};
    return Promise.resolve({ ok: statut < 400, status: statut,
                             json: function () { return Promise.resolve(corps); } });
  }
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
    sessionStorage: { getItem: function (k) { return k in session ? session[k] : null; }, setItem: function (k, v) { session[k] = String(v); },
                      removeItem: function (k) { delete session[k]; } },
    // Recharger la page ne recharge rien ici : on COMPTE. Le test rejoue la
    // suite dans un second banc, avec le stockage que le premier a laisse.
    location: { search: '', reload: function () { rechargements++; } },
    navigator: { getGamepads: function () { return pads; }, vibrate: function () {},
                 userAgent: 'Banc/1.0',
                 // ⚠️ Le seul appel qui survit a la fermeture d'un onglet : le banc
                 // garde ce qui part, personne n'en lit la reponse.
                 sendBeacon: function (url, paquet) {
                   beacons.push({ url: String(url), type: (paquet && paquet.type) || '',
                                  corps: paquet && paquet.texte !== undefined ? JSON.parse(paquet.texte) : paquet });
                   return true;
                 } },
    // Un Blob juste assez vrai : `sendBeacon` a besoin de son type pour que Flask
    // lise le corps en JSON.
    Blob: function (parties, options) {
      this.texte = (parties || []).join('');
      this.type = (options && options.type) || '';
    },
    matchMedia: function () { return { matches: false }; },
    fetch: function (url, opts) {
      fetchs.push({ url: url, opts: opts });
      const adresse = String(url);
      if (adresse.indexOf('/api/compte/') === 0) {
        const chemin = adresse.slice('/api/compte/'.length);
        let corps = null;
        try { corps = opts && opts.body ? JSON.parse(opts.body) : null; } catch (e) { corps = String(opts.body); }
        appelsCompte.push({ chemin: chemin, methode: (opts && opts.method) || 'GET', corps: corps,
                            entete: (opts && opts.headers) || null });
        // ⚠️ Une reponse TENUE ne se resout pas toute seule : c'est ce qui
        // permet de juger que rien ne double l'ouverture pendant qu'elle vole.
        const methode = (opts && opts.method) || 'GET';
        const tenu = tenues[methode + ' ' + chemin] || tenues[chemin];
        if (tenu) return new Promise(function (r) { tenu.push(r); }).then(function () { return servirCompte(chemin, methode); });
        return servirCompte(chemin, methode);
      }
      if (String(url).indexOf('definitions') >= 0) return Promise.resolve({ ok: true, json: function () { return Promise.resolve(defs); } });
      // ⚠️ La carte a sa requete depuis qu'elle est sortie du paquet : le banc
      // la sert comme le serveur, a part, et le jeu la remet dans `defs.carte`.
      if (String(url).indexOf('/api/carte') >= 0) return Promise.resolve({ ok: true, json: function () { return Promise.resolve(defs.carte); } });
      // Les sons : de quoi suivre TOUT le chemin d'un echantillon, du
      // telechargement au branchement sur la sortie.
      if (/\.mp3($|\?)/.test(String(url))) {
        return Promise.resolve({ ok: true, arrayBuffer: function () { return Promise.resolve(new ArrayBuffer(64)); } });
      }
      return Promise.resolve({ ok: true, json: function () { return Promise.resolve({}); } });
    },
    addEventListener: function (t, f) { (ecouteurs[t] = ecouteurs[t] || []).push(f); },
    removeEventListener: function () {}, dispatchEvent: function () {},
    screen: {},
  };
  // --- Faux audio ---------------------------------------------------------------------
  // ⚠️ Par defaut le banc n'a PAS d'AudioContext : le jeu doit tourner muet sans
  // broncher. `brancherAudio(demarre)` en pose un pour tester l'autre panne —
  // celle ou le navigateur retient le son tant qu'aucun geste n'a touche la page.
  let fauxContexte = null;
  function brancherAudio(demarre) {
    function param(v) {
      // ⚠️ `setValueAtTime` pose vraiment la valeur : sinon le banc lit 440 Hz
      // pour toutes les notes et un sequenceur faux passerait les tests.
      return { value: v, setValueAtTime: function (x) { this.value = x; return this; },
               exponentialRampToValueAtTime: function () { return this; } };
    }
    // ⚠️ Chaque noeud garde la liste de ce sur quoi il est branche. C'est ce qui
    // permet de juger qu'un son ATTEINT vraiment la sortie : une source que
    // personne ne relie au maitre demarre sans erreur et ne s'entend jamais.
    let idNoeud = 0;
    function noeud(extra) {
      const n = Object.assign({
        __id: ++idNoeud, __vers: [],
        connect: function (c) { this.__vers.push(c); return c; },
        disconnect: function () { this.__vers.length = 0; },
        start: function () {}, stop: function () {},
      }, extra || {});
      return n;
    }
    const joues = [];
    const sources = [];
    function FauxContexte() {
      fauxContexte = this;
      this.state = demarre ? 'running' : 'suspended';
      this.currentTime = 0;
      this.sampleRate = 48000;
      this.destination = noeud({ __sortie: true });
      this.joues = joues;
      this.sources = sources;
      /** Les sources qui ont demarre sans jamais atteindre la sortie : elles
          « jouent » et on n'entend rien. C'est le juge qui aurait attrape les
          deux soudures oubliees du 13 sept. 2026 (echantillon et voix). */
      this.sourcesMuettes = function () {
        const ctx = this;
        return sources.filter(function (s) { return s.__demarree && !ctx.atteintLaSortie(s); }).length;
      };
      /** Vrai si `n` atteint la sortie en suivant les branchements. */
      this.atteintLaSortie = function (n) {
        const vus = new Set();
        const pile = [n];
        while (pile.length) {
          const c = pile.pop();
          if (!c || vus.has(c)) continue;
          vus.add(c);
          if (c.__sortie) return true;
          (c.__vers || []).forEach(function (x) { pile.push(x); });
        }
        return false;
      };
      const ctx = this;
      this.resume = function () {
        // Sans geste, le navigateur REFUSE : la promesse part en erreur.
        if (!demarre) return Promise.reject(new Error('pas de geste'));
        ctx.state = 'running';
        return Promise.resolve();
      };
      this.suspend = function () { ctx.state = 'suspended'; return Promise.resolve(); };
      this.createGain = function () { return noeud({ gain: param(1) }); };
      this.createOscillator = function () {
        const n = noeud({ type: 'square', frequency: param(440), stop: function () {} });
        sources.push(n);
        n.start = function (t) { n.__demarree = true; joues.push({ quoi: 'ton', t: t, hz: n.frequency.value, forme: n.type }); };
        return n;
      };
      this.createBufferSource = function () {
        const n = noeud({ buffer: null, loop: false, playbackRate: param(1), onended: null, stop: function () {} });
        sources.push(n);
        n.start = function (t) { n.__demarree = true; joues.push({ quoi: 'echantillon', t: t }); };
        return n;
      };
      this.createBiquadFilter = function () { return noeud({ type: 'lowpass', frequency: param(800), Q: param(1) }); };
      this.createStereoPanner = function () { return noeud({ pan: param(0) }); };
      this.createBuffer = function (canaux, longueur) {
        return { length: longueur, numberOfChannels: canaux,
                 getChannelData: function () { return new Float32Array(longueur); } };
      };
      this.decodeAudioData = function (octets, ok) { if (ok) ok(this.createBuffer(1, 128)); };
    }
    fenetre.AudioContext = FauxContexte;
    return joues;
  }

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
      // L'horloge AUDIO avance avec les images : sans ca un sequenceur
      // programmerait sa boucle entiere au meme instant et ne bouclerait jamais.
      if (fauxContexte) fauxContexte.currentTime += 1 / 60;
      const cb = rafCb;
      cb(horloge);
    }
  }
  /** Un evenement de la FENETRE, joue comme le navigateur le joue (`pagehide`,
      `resize`...). ⚠️ Juger `Compte.partir()` en l'appelant soi-meme ne dit rien
      du jour ou plus personne ne l'appelle : c'est le geste qu'on veut voir. */
  function fenetreEvenement(type, extra) { (ecouteurs[type] || []).forEach(function (f) { f(evenement(type, extra)); }); }
  function touche(code) { (ecouteurs.keydown || []).forEach(function (f) { f(evenement('keydown', { code: code })); }); }
  function relacher(code) { (ecouteurs.keyup || []).forEach(function (f) { f(evenement('keyup', { code: code })); }); }
  function tape(code, images) { touche(code); frame(1); relacher(code); frame(images || 1); }
  /** Branche une manette. `fiche` : { id, mapping } — `mapping: ''` imite une
      manette Bluetooth que le navigateur ne reconnait pas. */
  function pad(axes, boutons, fiche) {
    pads.length = 0;
    if (axes) {
      pads.push({ connected: true, axes: axes,
                  id: (fiche && fiche.id) || 'Banc Pad',
                  mapping: fiche && fiche.mapping !== undefined ? fiche.mapping : 'standard',
                  buttons: (boutons || []).map(function (v) { return { pressed: v > 0.5, value: v }; }) });
    }
  }
  function pointeur(type, x, y, id) { croix.dispatch(type, evenement(type, { clientX: x, clientY: y, pointerId: id || 1 })); }
  function bouton(a, type) { const b = boutonsTactiles.find(function (q) { return q.dataset.a === a; }); b.dispatch(type, evenement(type, { pointerId: 2 })); }
  /** Pose un pieton a (dx, dy) du joueur, FIGE, et reindexe. Sans cela chaque
      test de combat commencerait par attendre qu'un passant veuille bien
      passer a portee. */
  function poser(arch, dx, dy) {
    const j = L.B.joueur;
    const p = L.Entites.creerPieton(j.x + dx, j.y + dy, arch ? L.Entites.archetype(arch) : null);
    p.etat = 'fige';
    L.Entites.indexer();
    return p;
  }
  /** Laisse jouer jusqu'au bout le fondu de porte en cours, s'il y en a un.

      ⚠️ Un fondu de porte change la scene AU NOIR, pas a l'appel de
      `Jeu.entrer()` : un test qui lirait `B.interieur` tout de suite lirait
      encore la rue. Et le jeu est FIGE pendant — ces images-la ne coutent rien a
      la simulation. Rend le nombre d'images qu'il a fallu. */
  function fondu() {
    let n = 0;
    while (L.B.transition && n < 240) { frame(1); n++; }
    return n;
  }
  /** Passer une porte comme le joueur : le fondu joue, la piece est chargee. */
  function entrer(porte) { const ok = L.Jeu.entrer(porte); fondu(); return ok; }
  /** Ressortir, fondu joue. */
  function sortir() { const ok = L.Jeu.sortir(); fondu(); return ok; }
  /** Pose un char stationne a (dx, dy) du joueur, cap `angle`, et reindexe. */
  function char(slug, dx, dy, angle) {
    const j = L.B.joueur;
    const v = L.Vehicules.creer(slug, j.x + dx, j.y + dy, angle || 0, { etat: 'stationne' });
    L.Entites.indexer();
    return v;
  }
  /** La premiere rangee de voie « > » a la colonne 14 (milieu d'un bloc, loin d'une ligne d'arret). */
  function ligneDroite() {
    const c = L.Monde.carte;
    for (let y = 0; y < c.h; y++) if (c.voie[y][14] === '>') return { x: 14 * L.TT + 8, y: y * L.TT + 8 };
    return null;
  }
  /** Une tuile de voie « > » avec dix tuiles droites devant — assez loin d'une
      ligne d'arret pour qu'aucun feu ne vienne brouiller une mesure de trafic.
      `double` : sa voisine du NORD va dans le meme sens (un boulevard, la voie
      de GAUCHE existe, c'est par la qu'on depasse) ; sinon : aucune des deux
      voisines n'y va (une rue a deux voies, une par sens). Rend null si la
      carte n'en a pas. */
  function boulevard(double) {
    const c = L.Monde.carte;
    for (let y = 3; y < c.h - 3; y++) {
      for (let x = 3; x < c.w - 14; x++) {
        if (c.voie[y][x] !== '>') continue;
        const gauche = c.voie[y - 1][x] === '>';
        if (double ? !gauche : (gauche || c.voie[y + 1][x] === '>')) continue;
        let droit = true;
        for (let k = 0; k <= 10; k++) {
          if (c.voie[y][x + k] !== '>') droit = false;
          if (double && c.voie[y - 1][x + k] !== '>') droit = false;
        }
        if (droit) return { tx: x, ty: y, x: x * L.TT + 8, y: y * L.TT + 8 };
      }
    }
    return null;
  }
  /** Tourne le joueur vers une cible (le sens compte : l'arc est devant). */
  function viser(cible) {
    const j = L.B.joueur;
    L.Entites.regarder(j, cible.x - j.x, cible.y - j.y);
  }
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
                   fenetreEvenement: fenetreEvenement,
                   poser: poser, viser: viser, char: char, ligneDroite: ligneDroite, boulevard: boulevard,
                   fondu: fondu, entrer: entrer, sortir: sortir,
                   doc: doc, fenetre: fenetre, fetchs: fetchs, elements: elements, store: store, session: session, ctx: toile.getContext('2d'),
                   // Le compte (M14) : ce qui est parti, ce qui reste a rendre, et ce qu'on repond.
                   compte: { appels: appelsCompte, beacons: beacons,
                             repondre: function (chemin, valeur) { reseau[chemin] = valeur; },
                             tenir: function (chemin) { tenues[chemin] = tenues[chemin] || []; },
                             rendre: function (chemin) {
                               const attente = tenues[chemin] || [];
                               delete tenues[chemin];
                               attente.forEach(function (r) { r(); });
                             } },
                   rechargements: function () { return rechargements; },
                   brancherAudio: brancherAudio,
                   // Laisse tourner les promesses en attente (chargement d'un son).
                   attendre: function () { return new Promise(function (r) { setImmediate(r); }); } };

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
