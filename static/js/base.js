/* Bandini — base : constantes, sac d'etat, maths, canvas, rendu, sauvegarde.

   ⚠️ Aucun acces au DOM a l'analyse : tout ce qui touche `document` est dans
   une fonction appelee par jeu.js. C'est ce qui permet au banc d'essai
   (tests/banc.js) de charger ce fichier sous Node. */

const VW = 480;
const VH = 270;
const TT = 16;

/** Le sac d'etat : une seule source, lue et ecrite par tous les modules. */
const B = {
  etat: 'chargement',   // chargement | titre | jeu | pause | prison | hopital | fin
  menu: null,           // objet de menu canvas ; non nul = simulation figee
  interieur: null,      // la piece ou l'on est, ou null dehors
  exterieur: null,      // la ville mise de cote pendant qu'on est dedans
  dialogue: null,       // boite de texte en cours
  fondu: null,
  t: 0,                 // images simulees depuis le demarrage
  rng: null,
  graine: 1,
  defs: null,           // le paquet /api/definitions
  carte: null,
  cam: { x: 0, y: 0, secousse: 0 },
  joueur: null,
  entites: [],
  particules: [],
  decals: [],
  crimes: [],
  recherche: { etoiles: 0, chaleur: 0, vu: 0, dernierVu: null, flash: 0 },
  budget: { chemins: 2, los: 20 },
  msg: null, msgT: 0,
  partie: null,         // ce qui se sauvegarde (voir etatInitial)
  options: { muet: false, sang: true, vibration: true, daltonien: false, trace: false },
  trace: { anomalies: [], total: 0 },     // ce que le mode TRACE a releve (voir Vehicules.majTrace)
  cinema: null,         // un dialogue en cours : le joueur ecoute (voir Histoire.dire)
  mission: null,        // les figurants de la mission en cours (pas sauvegardes : voir Histoire)
  defi: null,           // le defi en cours
  stats: { images: 0, rects: 0, entites: 0, actifs: 0, morceaux: 0, ms: 0 },
};

/** Ce qui survit a un rechargement — et ses valeurs par defaut. */
function etatInitial(defs) {
  const eco = (defs && defs.economie) || {};
  return {
    version: 1,
    empreinte: defs ? defs.empreinte : '',
    argent: eco.argent_depart || 50,
    casier: 0,
    jour: 1,
    heure: 0.35,
    vie: 100,
    tenue: 'chandail',
    tenues: ['chandail'],
    armes: { poings: { mun: null } },
    arme: 'poings',
    planque: { armes: {}, vehicule: null, coffre: 0 },
    proprietes: {},
    missionsFaites: {},
    mission: null,        // { slug, etape } — la mission en cours
    appels: {},           // les appels recus, par mission
    appelT: null,
    defisFaits: {},
    rabais: {},
    sergentAmi: false,
    faubourgLibere: false,
    manchetteForcee: null,
    paquets: {},
    journal: null,
    stats: { crimes: 0, arrestations: 0, volees: 0, tues: 0, secondes: 0 },
    x: null, y: null,
  };
}

// --- Maths ------------------------------------------------------------------

function borner(v, min, max) { return v < min ? min : v > max ? max : v; }
function lerp(a, b, t) { return a + (b - a) * t; }
function dist2(ax, ay, bx, by) { const dx = ax - bx, dy = ay - by; return dx * dx + dy * dy; }
function angleVers(ax, ay, bx, by) { return Math.atan2(by - ay, bx - ax); }
/** Ecart signe entre deux angles, dans ]-PI, PI]. */
function ecartAngle(a, b) {
  let d = (b - a) % (Math.PI * 2);
  if (d > Math.PI) d -= Math.PI * 2;
  if (d <= -Math.PI) d += Math.PI * 2;
  return d;
}
/** Un entier stable pour une paire (x, y) — variantes de tuiles. */
function hash2(x, y) {
  let h = (x * 374761393 + y * 668265263) | 0;
  h = (h ^ (h >>> 13)) * 1274126177;
  return (h ^ (h >>> 16)) >>> 0;
}
/** Generateur deterministe (mulberry32). */
function mulberry(graine) {
  let a = graine >>> 0;
  return function () {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// --- Canvas, echelle entiere, rendu ---------------------------------------------

const Base = (function () {
  'use strict';

  let cv = null, ctx = null, SCALE = 1;
  const cible = { cv: null, ctx: null };   // rendu 1x, puis un seul drawImage a l'ecran
  let fabrique = null;                      // (w, h) => canvas, injecte par jeu.js ou le banc

  function initCanvas(canvas, fabriqueCanvas) {
    cv = canvas;
    ctx = cv.getContext('2d');
    fabrique = fabriqueCanvas;
    cible.cv = fabrique(VW, VH);
    cible.ctx = cible.cv.getContext('2d');
    cible.ctx.imageSmoothingEnabled = false;
  }

  /** Echelle entiere selon les pixels PHYSIQUES ; sous 1x on laisse reduire. */
  function redimensionner(fenetre, tactile) {
    if (!cv) return;
    const dpr = Math.max(1, Math.min(3, fenetre.devicePixelRatio || 1));
    const margeH = tactile ? 0 : 24, margeV = tactile ? 0 : 80;
    const dispoW = (fenetre.innerWidth - margeH) * dpr;
    const dispoH = (fenetre.innerHeight - margeV) * dpr;
    const z = Math.min(dispoW / VW, dispoH / VH);
    SCALE = Math.max(1, Math.min(8, Math.floor(z)));
    cv.width = VW * SCALE;
    cv.height = VH * SCALE;
    // ⚠️ Sur un telephone, l'echelle entiere peut laisser un tiers de l'ecran
    // vide (844x390 CSS a 2x : 2,88 → 2). On etire alors en CSS a l'echelle
    // fractionnaire : des pixels un peu inegaux valent mieux qu'un timbre-poste.
    const zAff = z >= 1 ? (z - SCALE > 0.35 ? z : SCALE) : z;
    cv.style.width = (VW * zAff / dpr) + 'px';
    cv.style.height = (VH * zAff / dpr) + 'px';
    cv.style.imageRendering = z >= 1 ? 'pixelated' : 'auto';
    ctx.imageSmoothingEnabled = false;
  }

  /** Le contexte 1x dans lequel tout le jeu se dessine. */
  function debut() {
    const c = cible.ctx;
    c.setTransform(1, 0, 0, 1, 0, 0);
    c.imageSmoothingEnabled = false;
    B.stats.images = 0; B.stats.rects = 0;
    return c;
  }

  /** Compose la nuit et les lampes, puis envoie a l'ecran. */
  function fin(ambiance, lampes) {
    const c = cible.ctx;
    if (ambiance && ambiance.alpha > 0) {
      c.save();
      c.globalCompositeOperation = 'multiply';
      c.fillStyle = ambiance.teinte;
      c.globalAlpha = ambiance.alpha;
      c.fillRect(0, 0, VW, VH);
      c.restore();
      if (lampes && lampes.length) {
        c.save();
        c.globalCompositeOperation = 'lighter';
        for (let i = 0; i < lampes.length && i < 25; i++) {
          const l = lampes[i];
          const g = c.createRadialGradient(l.x, l.y, 2, l.x, l.y, l.r);
          g.addColorStop(0, l.c || 'rgba(255,220,140,0.55)');
          g.addColorStop(1, 'rgba(0,0,0,0)');
          c.fillStyle = g;
          c.fillRect(l.x - l.r, l.y - l.r, l.r * 2, l.r * 2);
        }
        c.restore();
      }
    }
    ctx.setTransform(SCALE, 0, 0, SCALE, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(cible.cv, 0, 0);
  }

  /** Le contexte ECRAN (pour le HUD, hors nuit). Echelle deja posee. */
  function ecran() { return ctx; }

  function nouveauCanvas(w, h) { return fabrique(w, h); }

  return {
    initCanvas, redimensionner, debut, fin, ecran, nouveauCanvas,
    get SCALE() { return SCALE; },
  };
})();

// --- Sauvegarde ----------------------------------------------------------------------

const Sauvegarde = (function () {
  'use strict';
  const CLE = 'bandini-partie-v1';
  let stockage = null;

  function init(s) { stockage = s; }

  function lire() {
    try {
      const brut = stockage && stockage.getItem(CLE);
      return brut ? JSON.parse(brut) : null;
    } catch (e) { return null; }
  }

  function ecrire(partie) {
    try { stockage && stockage.setItem(CLE, JSON.stringify(partie)); return true; } catch (e) { return false; }
  }

  function effacer() { try { stockage && stockage.removeItem(CLE); } catch (e) { /* rien */ } }

  const CLE_OPTIONS = 'bandini-options-v1';
  function ecrireOptions(options) {
    try { stockage && stockage.setItem(CLE_OPTIONS, JSON.stringify(options)); return true; } catch (e) { return false; }
  }
  function lireOptions() {
    try { const brut = stockage && stockage.getItem(CLE_OPTIONS); return brut ? JSON.parse(brut) : null; } catch (e) { return null; }
  }

  /** Une partie chargee recoit tout champ ajoute depuis (repli sur les defauts). */
  function completer(partie, defs) {
    const base = etatInitial(defs);
    if (!partie || typeof partie !== 'object') return base;
    const out = Object.assign({}, base, partie);
    for (const k of ['armes', 'planque', 'proprietes', 'missionsFaites', 'paquets', 'stats']) {
      out[k] = Object.assign({}, base[k], (partie[k] && typeof partie[k] === 'object') ? partie[k] : {});
    }
    if (!Array.isArray(out.tenues) || out.tenues.indexOf('chandail') < 0) out.tenues = ['chandail'].concat(Array.isArray(out.tenues) ? out.tenues : []);
    if (!out.armes.poings) out.armes.poings = { mun: null };
    if (!out.armes[out.arme]) out.arme = 'poings';
    return out;
  }

  return { CLE, CLE_OPTIONS, init, lire, ecrire, effacer, completer, ecrireOptions, lireOptions };
})();
