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
  /*: La roue d'armes OUVERTE : { armes, choix, t } — voir `Combat.majRoue`.
    ⚠️ Elle ne fige pas le monde comme `menu`, elle le RALENTIT (une image
    de monde sur quatre) : une roue qui fige serait une pause gratuite au
    milieu d'une fusillade. Le joueur, lui, ne bouge plus tant qu'elle est
    ouverte — il choisit, il ne marche pas. */
  roue: null,
  interieur: null,      // la piece ou l'on est, ou null dehors
  exterieur: null,      // la ville mise de cote pendant qu'on est dedans
  dialogue: null,       // boite de texte en cours
  transition: null,     // un changement de scene EN COURS ; non nul = simulation figee (voir Jeu.transiter)
  t: 0,                 // images simulees depuis le demarrage
  /*: Les images DESSINEES depuis le demarrage. ⚠️ Ce n'est pas `t` : `t` est le
    temps du MONDE, et il s'arrete des qu'on ouvre la carte, un menu ou la
    pause. Ce qui bat a l'ecran — l'anneau du joueur, le losange de l'objectif —
    bat sur celle-ci, sinon le repere qu'on ouvre la carte pour trouver reste
    fige sur l'image ou on l'a ouverte, et une fois sur deux fige sur du vide. */
  image: 0,
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
  //: Depuis quand la barre de souffle a quelque chose a dire (images).
  souffleT: 0,
  msg: null, msgT: 0,
  partie: null,         // ce qui se sauvegarde (voir etatInitial)
  options: { muet: false, sang: true, vibration: true, daltonien: false, trace: false,
             manette: null, manetteProfil: null },
  trace: { anomalies: [], total: 0 },     // ce que le mode TRACE a releve (voir Vehicules.majTrace)
  cinema: null,         // un dialogue en cours : le joueur ecoute (voir Histoire.dire)
  ouverture: null,      // la scene d'ouverture en cours (voir Histoire.ouverture)
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
    cheveux: null,        // la couleur donnee par le barbier (`magasins.COIFFURES`)
    fouilles: {},         // les logements deja fouilles, par porte et par etage
    armes: { poings: { mun: null } },
    arme: 'poings',
    //: L'arme d'AVANT — ce sur quoi retombe le RETOUR RAPIDE (une tape sur
    //: ARME, sans tenir). Les poings pour les poches, la carabine pour le
    //: toit : c'est le geste qu'on fait le plus souvent, et il se garde
    //: dans la partie parce qu'il survit a une nuit de sommeil.
    armePrecedente: 'poings',
    planque: { armes: {}, vehicule: null, coffre: 0 },
    //: Les chars saisis, du plus vieux au plus recent. ⚠️ Un TABLEAU, pas un
    //: objet : le lot a un nombre de places, et c'est le plus vieux qui part
    //: quand il deborde — un ordre, donc, pas un sac.
    fourriere: [],
    //: M11 — ce qu'on a entrepris pour faire maigrir son casier. `avocatJour`
    //: est le jour ou Me Desjardins a travaille (il ne travaille pas deux fois
    //: le meme) ; `commande` est la job payee d'avance au comptoir du fond de
    //: La Shop, qui ne donne de nouvelles que le lendemain.
    //: ⚠️ La commande est DANS LA SAUVEGARDE : on a paye hier, on apprend
    //: aujourd'hui, et il n'y a pas de retour en arriere.
    nettoyage: { avocatJour: 0, commande: null, provision: false },
    //: M10, 2e vague — ce qu'on a en poche qui n'est pas une arme (le
    //: skimmer, par nombre), les skimmers POSES sur les guichets de la ville
    //: (cle = la tuile ; `pret` quand la nuit a lu), et le dossier
    //: d'assurance : ce qu'elle nous doit, combien de fois on a reclame, et
    //: jusqu'a quel jour l'assureur enquete (0 = il ne fait rien).
    objets: {},
    skimmers: [],
    assurance: { du: 0, reclamations: 0, enquete: 0 },
    //: La run : ce qu'on a achete a la cale AUJOURD'HUI (le prix monte avec).
    //: Les caisses, elles, sont dans le coffre du char — pas dans la partie.
    contrebande: { jour: 0, achetees: 0 },
    //: M10 — la dette de Rocco, celle dont on herite avec le garage. Elle
    //: MONTE chaque nuit et elle est BORNEE : une dette qui double pendant
    //: qu'on dort n'est plus une pression, c'est une partie perdue au reveil.
    //: `collecteJour` est le dernier jour ou les hommes de Sal se sont
    //: presentes — ils ne viennent qu'une fois par jour.
    dette: (eco.dette && eco.dette.montant) || 0,
    collecteJour: 0,
    rappelJour: 0,
    //: Combien de fois chaque boulot a ete fait, et quels paliers sont
    //: debloques. ⚠️ CA VIT DANS LA PARTIE, pas dans le module : le compte
    //: etait garde sur l'objet `boulot` de `missions.js`, donc remis a zero a
    //: chaque rechargement. « Cinquante courses » n'aurait jamais voulu dire
    //: quoi que ce soit.
    boulots: { taxi: 0, pizza: 0, ambulance: 0, remorquage: 0 },
    paliers: {},
    //: Les gens qu'on a RENCONTRES (slug -> jour). ⚠️ Sans ca, le repertoire
    //: du carnet montrerait des personnages qu'on n'a jamais vus — et il
    //: divulgacherait l'histoire : Josee, le Dr Lachance de M13, Marco qui te
    //: vend. Un repertoire qui montre la fin est pire que pas de repertoire.
    connus: {},
    //: Le JOURNAL du carnet : ce qui s'est passe, en ordre, date au jour de
    //: jeu. ⚠️ Ce n'est ni `journal.py` (Le Clairon, la manchette du matin) ni
    //: le carnet du poste de M11 (le dossier de la police sur toi). Trois
    //: choses, trois noms.
    carnet: [],
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
    // ⚠️ Les lecons du Clairon deja lues. Elles vivent dans la PARTIE, pas
    // dans le moteur : une lecon relue dix parties de suite n'apprend rien la
    // dixieme fois, mais une nouvelle partie recommence a zero — et c'est la
    // qu'on en a besoin.
    leconsLues: [],
    //: L'ouverture a ete vue. ⚠️ Elle ne joue qu'a la PREMIERE partie d'une
    //: sauvegarde : une introduction qu'on revoit a chaque chargement devient
    //: un peage. Elle se revoit quand on la demande (LE CARNET > REVOIR
    //: L'OUVERTURE), et une partie deja commencee (`x` non nul) ne la voit
    //: jamais — celui qui joue depuis trois jours n'a pas besoin qu'on lui
    //: presente son oncle.
    ouvertureVue: false,
    stats: { crimes: 0, arrestations: 0, volees: 0, tues: 0, secondes: 0 },
    x: null, y: null,
  };
}

/** Les couleurs du joueur : son linge, et sa coupe s'il est passe chez le barbier.

    ⚠️ UNE seule fonction pour les deux. `porterTenue` remplacait les swaps par
    `{ c: couleur }` : la teinture du barbier disparaissait des qu'on changeait
    de chandail, et on se demandait pourquoi la police nous reconnaissait. */
function apparenceDuJoueur(partie, defs) {
  const tenue = ((defs && defs.tenues) || []).find(function (t) { return t.slug === partie.tenue; });
  const swaps = {};
  if (tenue) swaps.c = tenue.couleur;
  if (partie.cheveux) swaps.h = partie.cheveux;
  return Object.keys(swaps).length ? swaps : null;
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
/** Les trois tons d'une carrosserie a partir d'UNE couleur : la couleur,
    son rehaut (`C`, la ou la lumiere tombe — le toit, le capot) et son ombre
    (`D`, le bas de caisse, dessous le pare-chocs).

    ⚠️ ICI, et une seule fois. Les palettes de `sprites.js` en ont besoin pour
    leurs tons par defaut, et `vehicules.js` pour chaque couleur du catalogue
    tiree a la naissance d'un char (les 32 variantes). Deux formules pour un
    meme rehaut auraient fini par diverger : un taxi jaune neuf aurait eu un
    toit d'une autre teinte qu'un taxi jaune gare depuis le debut. */
function nuances(hex) {
  const n = parseInt(String(hex).replace('#', '').slice(0, 6), 16);
  const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
  const mix = function (a, cible, part) { return Math.round(a + (cible - a) * part); };
  const h = function (r2, g2, b2) { return '#' + ((1 << 24) | (r2 << 16) | (g2 << 8) | b2).toString(16).slice(1); };
  return { c: '#' + ('000000' + n.toString(16)).slice(-6),
           C: h(mix(r, 255, 0.34), mix(g, 255, 0.34), mix(b, 255, 0.34)),
           D: h(mix(r, 0, 0.32), mix(g, 0, 0.32), mix(b, 0, 0.32)) };
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

  //: Le plafond de lampes d'une image. ⚠️ Il etait a 25, taille pour les
  //: LAMPADAIRES SEULS — c'est aussi ce que `Monde.lampesVisibles` en rend au
  //: plus. Les feux s'y ajoutent maintenant, une lampe par ampoule allumee :
  //: un croisement, c'est 2 poteaux de chars a 2 ampoules et jusqu'a 4
  //: poteaux de pietons — 8 lampes, et l'ecran en tient plusieurs. Au plafond
  //: d'avant, les feux AURAIENT ETEINT les lampadaires au lieu de s'ajouter a
  //: eux : 25 lampadaires + 24 feux + le projecteur de l'helico.
  const LAMPES_MAX = 50;

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
        for (let i = 0; i < lampes.length && i < LAMPES_MAX; i++) {
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
    for (const k of ['armes', 'planque', 'proprietes', 'missionsFaites', 'paquets', 'stats', 'connus', 'nettoyage', 'boulots', 'paliers', 'objets', 'assurance', 'contrebande']) {
      out[k] = Object.assign({}, base[k], (partie[k] && typeof partie[k] === 'object') ? partie[k] : {});
    }
    if (!Array.isArray(out.tenues) || out.tenues.indexOf('chandail') < 0) out.tenues = ['chandail'].concat(Array.isArray(out.tenues) ? out.tenues : []);
    // ⚠️ Un tableau ne passe pas par la fusion des objets ci-dessus : une
    // partie d'avant la fourriere arriverait avec `undefined`, et le comptoir
    // planterait au premier clic.
    if (!Array.isArray(out.fourriere)) out.fourriere = [];
    if (!Array.isArray(out.carnet)) out.carnet = [];
    if (!Array.isArray(out.skimmers)) out.skimmers = [];
    if (!out.armes.poings) out.armes.poings = { mun: null };
    if (!out.armes[out.arme]) out.arme = 'poings';
    if (!out.armes[out.armePrecedente]) out.armePrecedente = 'poings';
    return out;
  }

  return { CLE, CLE_OPTIONS, init, lire, ecrire, effacer, completer, ecrireOptions, lireOptions };
})();
