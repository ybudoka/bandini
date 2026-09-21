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
  options: { muet: false, sang: true, vibration: true, daltonien: false, trace: false, neige: false,
             reculCommeEnAvant: false, manette: null, manetteProfil: null },
  trace: { anomalies: [], total: 0 },     // ce que le mode TRACE a releve (voir Vehicules.majTrace)
  cinema: null,         // un dialogue en cours : le joueur ecoute (voir Histoire.dire)
  ouverture: null,      // la scene d'ouverture en cours (voir Histoire.ouverture)
  scene: null,          // la scene qui joue, quelle qu'elle soit (voir Scenes)
  finEnAttente: null,   // la fin d'une mission reussie, qui attend qu'on soit a l'arret (Histoire.jouerLaFin)
  sonnerie: null,       // le combine sonne : { slug, t } — on decroche a l'image `t` (Histoire.majTelephone)
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
    // ⚠️ Le jour ou les chantiers de CETTE partie ont commence : leur phase se lit
    // du jour courant et de celui-ci, donc deux appareils qui ouvrent la meme
    // sauvegarde voient la meme ville (voir `Chantiers.phaseVoulue`).
    chantiers: { debut: 1 },
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
    //: Ceux qu'on a couches a un essai RATE, par mission, par objectif et
    //: par coin (`tombes.m5[0]` vaut `[2, 2, 0]`). ⚠️ Mourir ou se faire
    //: arreter fait rater la mission, pas ressusciter ses Cravates : la
    //: reprise ne repose que ceux qui tiennent encore debout.
    tombes: {},
    mission: null,        // { slug, etape } — la mission en cours
    appels: {},           // les appels recus, par mission
    appelT: null,
    defisFaits: {},
    //: LE DEFI DU JOUR (M14, 5e vague) : `{ date, slug, temps }` de la derniere prime du jour
    //: encaissee par CETTE partie. ⚠️ La date est celle du SERVEUR, jamais l'horloge locale.
    //: Null tant qu'on n'en a pas touche ; une vieille partie le recoit par `completer`.
    defiDuJour: null,
    rabais: {},
    //: Les contacts du téléphone (`donne.contacts`, m6) : des personnages
    //: dont on a le numéro. Un objet slug -> jour, comme le répertoire.
    contacts: {},
    sergentAmi: false,
    faubourgLibere: false,
    //: Les districts liberes (`libere` de M16, generalise `faubourg_libere`) :
    //: un tableau de slugs — ordonne, comme tout ce qui voyage dans la partie.
    libere: [],
    //: Les gangs CALMES (`donne.calme` de M16) : un tableau de slugs. Une fois
    //: calme, un gang oublie `hostile_toujours` et `hostile_si_arme` — la seule
    //: facon de marcher dans La Shop (`s05`).
    calmes: [],
    //: Les missions FERMEES de M16 (`ferme`, les choix) : un tableau de slugs.
    //: Une mission fermee n'apparait plus jamais, ni au telephone ni au carnet.
    fermees: [],
    //: Les choix de M16, par paire : `p.choix[q10]` vaut le slug pris
    //: (`q10` ou `q11`). C'est ce qui retient la branche qu'on a suivie.
    choix: {},
    //: Le char que DONNE une mission, gare devant la planque (`donne.vehicule`,
    //: le taxi de m97). Il vit a part de `planque.vehicule` (celui qu'on y
    //: laisse soi-meme) pour ne pas ecraser la sauvegarde.
    vehiculePlanque: null,
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
    //: Les triches du menu DEBUG qui se BASCULENT (`Hud.menuDebug`) — invincible,
    //: vehicules invincibles, energie infinie, munitions infinies, police qui
    //: n'arrete pas — et `menu`, qui n'est pas une triche mais la CLE : la suite
    //: secrete l'a tapee dans cette partie, donc la PAUSE montre la ligne
    //: TRICHES. ⚠️ Tout vit DANS LA PARTIE, pas sur `B` : ca suit son emplacement
    //: (et le compte, qui monte la partie entiere), et une nouvelle partie
    //: repart sans rien. On lit par `triche(nom)`, jamais a la main.
    triches: { menu: false, invincible: false, vehicules: false, endurance: false, munitions: false, pasArrete: false },
    stats: { crimes: 0, arrestations: 0, volees: 0, tues: 0, secondes: 0 },
    x: null, y: null,
  };
}

/** Une triche du menu DEBUG est-elle allumee dans la partie en cours ? Faux sans
    partie (le titre) et pour un nom inconnu. */
function triche(nom) {
  const p = B.partie;
  return !!(p && p.triches && p.triches[nom]);
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

//: Les quatre regards que le sprite MONTRE, en radians (`e.face`).
const REGARDS = { droite: 0, bas: Math.PI / 2, gauche: Math.PI, haut: -Math.PI / 2 };

/** `e` FAIT-IL FACE au point (x, y) ? La regle de toute interaction : pour agir sur
    une porte, un char, un comptoir ou quelqu'un, on le regarde.

    ⚠️ Le regard est ce que le sprite MONTRE (`face`), pas l'angle fin du stick :
    ce que le joueur voit est ce que le jeu juge. `angle` ne sert que quand la pose
    n'est pas un regard (couche, assis). ⚠️ Et on n'a pas a regarder ce qu'on a sous
    les pieds (`regard.dessus_px`) : la, la direction n'est plus definie.

    Toutes les fonctions « sous la main » passent par ici, et l'invite du HUD lit
    les memes : le bouton ne promet jamais ce qu'il refuserait (`recherche.regard`). */
function faceA(e, x, y) {
  const r = B.defs.recherche.regard;
  if (dist2(e.x, e.y, x, y) <= r.dessus_px * r.dessus_px) return true;
  const regard = REGARDS[e.face];
  return Math.abs(ecartAngle(regard === undefined ? e.angle : regard, angleVers(e.x, e.y, x, y)))
    <= r.demi_cone_degres * Math.PI / 180;
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
  //: L'echelle que le CASQUE impose (`Casque.ECHELLE`) : la fenetre n'y a plus
  //: rien a dire, c'est la texture de l'ecran virtuel qu'on dessine.
  let echelleImposee = null;
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
    SCALE = echelleImposee || Math.max(1, Math.min(8, Math.floor(z)));
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
  //: eux : 25 lampadaires + 24 feux + le projecteur de l'helico. Et depuis la
  //: nuit a ses habitudes, les PHARES : douze lampes de plus (six chars menes).
  const LAMPES_MAX = 62;

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
          // Un faisceau (un phare) : le meme halo, ETIRE dans son axe (`e`, `a`).
          if (l.e) {
            c.save();
            c.translate(l.x, l.y);
            c.rotate(l.a || 0);
            c.scale(l.e, 1);
            const f = c.createRadialGradient(0, 0, 2, 0, 0, l.r);
            f.addColorStop(0, l.c);
            f.addColorStop(1, 'rgba(0,0,0,0)');
            c.fillStyle = f;
            c.fillRect(-l.r, -l.r, l.r * 2, l.r * 2);
            c.restore();
            continue;
          }
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

  /** `n` : l'echelle a tenir quelle que soit la fenetre ; null la rend a la fenetre. */
  function imposerEchelle(n) { echelleImposee = n || null; }

  return {
    initCanvas, redimensionner, imposerEchelle, debut, fin, ecran, nouveauCanvas,
    get SCALE() { return SCALE; },
  };
})();

// --- Chargements ----------------------------------------------------------------------

/** Ce qui se charge en ce moment : un son, une voix, une musique.

    Demande de Martin (17 sept. 2026) : « s'il y a des chargements dans le jeu, un
    petit icone s'animant dans un coin de l'ecran ». L'audio se charge A L'USAGE
    (12 Mo en 166 fichiers) : c'est lui qu'on attend en jouant, et rien ne le
    disait. Le HUD lit ce compte (`Hud.dessiner`).

    ⚠️ Chaque debut rend SA fin, qui ne decompte qu'une fois : une fin appelee deux
    fois ferait tomber le compte sous zero, et une fin jamais appelee laisserait
    l'icone tourner pour toujours — d'ou `suivre`, qui la pose sur la reussite
    comme sur l'echec. */
const Chargements = (function () {
  'use strict';
  let enCours = 0;
  function debut() {
    enCours++;
    let fini = false;
    return function fin() { if (!fini) { fini = true; enCours--; } };
  }
  function suivre(promesse) {
    const fin = debut();
    return promesse.then(function (v) { fin(); return v; }, function (e) { fin(); throw e; });
  }
  return { debut: debut, suivre: suivre, nombre: function () { return enCours; } };
})();

// --- Sauvegarde ----------------------------------------------------------------------

const Sauvegarde = (function () {
  'use strict';
  /*: TROIS EMPLACEMENTS, et le premier porte la cle d'AVANT les emplacements.
    ⚠️ Rien ne se deplace : la partie de Martin etait sous `bandini-partie-v1`,
    elle y reste, et elle devient l'emplacement 1 sans qu'une seule ecriture ait
    lieu. Une migration qui recopie puis efface est une migration qui peut
    s'arreter au milieu — et un retour a une version d'avant retrouverait sa
    partie la ou il l'a laissee. */
  const CLE = 'bandini-partie-v1';
  const EMPLACEMENTS = 3;
  //: Le dernier emplacement joue : c'est lui que le titre charge et propose.
  const CLE_EMPLACEMENT = 'bandini-emplacement-v1';
  //: ⚠️ Dans `sessionStorage`, pas dans `localStorage` : ce drapeau ne doit
  //: survivre qu'au rechargement qu'on a demande, jamais a la visite suivante.
  const CLE_ROUVRIR = 'bandini-rouvrir-parties';
  /*: LE COMPTEUR DES SAUVEGARDES, par emplacement (M14) : il avance d'un cran a
    chaque ecriture locale, et c'est le SEUL ordre que le serveur comprend — deux
    appareils n'ont pas la meme heure, et une horloge qui recule ferait perdre une
    partie. ⚠️ Il ne vit pas DANS la partie : une copie d'un emplacement vers un
    autre emporterait son compteur, et la case copiee se croirait a jour. */
  const CLE_COMPTEUR = 'bandini-compteur-v1';
  let stockage = null, session = null, actif = 1, compteurs = {}, apresEcriture = null;

  function init(s, sess) {
    stockage = s; session = sess || null;
    let n = 1;
    try { n = parseInt(stockage && stockage.getItem(CLE_EMPLACEMENT), 10); } catch (e) { n = 1; }
    actif = n >= 1 && n <= EMPLACEMENTS ? n : 1;
    compteurs = {};
    try {
      const gardes = stockage && stockage.getItem(CLE_COMPTEUR);
      const lus = gardes ? JSON.parse(gardes) : null;
      if (lus && typeof lus === 'object') compteurs = lus;
    } catch (e) { compteurs = {}; }
    // ⚠️ Une partie d'AVANT le compteur (celle de Martin) n'en a pas, et une case
    // pleine a zero passerait pour une case vide au premier compte : elle demarre
    // a 1. Ce qui est vide reste a zero — c'est ce qui dit « il n'y a rien ici ».
    for (let i = 1; i <= EMPLACEMENTS; i++) {
      if (!compteurs[i] && brut(i)) compteurs[i] = 1;
    }
  }

  function compteur(n) {
    const v = compteurs[n || actif];
    return typeof v === 'number' && v > 0 ? v : 0;
  }

  function ecrireCompteurs() {
    try { stockage && stockage.setItem(CLE_COMPTEUR, JSON.stringify(compteurs)); } catch (e) { /* rien */ }
  }

  /** Le compteur de `n` prend la valeur `v` — celle du serveur, quand sa partie
      descend : la prochaine sauvegarde repart de la, et rien ne se refuse. */
  function poserCompteur(n, v) {
    compteurs[n || actif] = typeof v === 'number' && v > 0 ? Math.floor(v) : 0;
    ecrireCompteurs();
  }

  function avancer(n) {
    compteurs[n] = compteur(n) + 1;
    ecrireCompteurs();
    return compteurs[n];
  }

  /** Le crochet du compte (M14) : appele apres CHAQUE ecriture locale, avec
      l'emplacement ecrit. ⚠️ `Sauvegarde` ne sait rien du reseau et ne doit rien
      en savoir : elle previent, c'est tout. */
  function surEcriture(f) { apresEcriture = f; }

  function prevenirEcriture(n) { if (apresEcriture) apresEcriture(n); }

  function cle(n) { return n === 1 ? CLE : CLE + '-' + n; }
  function emplacement() { return actif; }
  function choisir(n) {
    actif = n;
    try { stockage && stockage.setItem(CLE_EMPLACEMENT, String(n)); } catch (e) { /* rien */ }
  }

  function brut(n) {
    try { return (stockage && stockage.getItem(cle(n || actif))) || null; } catch (e) { return null; }
  }

  function lire(n) {
    try {
      const b = brut(n);
      return b ? JSON.parse(b) : null;
    } catch (e) { return null; }
  }

  /** ⚠️ La date part avec la partie ECRITE, pas dans `B.partie` : une horloge
      murale dans l'etat du jeu ferait differer deux parties jouees pareil. */
  function ecrire(partie, n) {
    const ou = n || actif;
    try {
      stockage && stockage.setItem(cle(ou), JSON.stringify(Object.assign({}, partie, { sauveeLe: Date.now() })));
    } catch (e) { return false; }
    // ⚠️ Le compteur n'avance QUE si l'ecriture a tenu : un quota plein qui
    // ferait avancer le compteur ferait monter au serveur une partie qui n'est
    // pas celle d'ici.
    avancer(ou);
    prevenirEcriture(ou);
    return true;
  }

  /** La partie du serveur, posee TELLE QUELLE (M14) : elle garde sa date de
      sauvegarde, et le compteur ne bouge pas — c'est `Compte` qui le pose sur
      celui du serveur. ⚠️ Passer par `ecrire` la redaterait a maintenant et
      avancerait le compteur : la case descendue se croirait plus neuve que la
      version dont elle vient, et elle remonterait aussitot. */
  function poser(n, partie) {
    try { stockage && stockage.setItem(cle(n || actif), JSON.stringify(partie)); return true; } catch (e) { return false; }
  }

  /** ⚠️ Effacer AVANCE le compteur (M14) : une case videe ici doit se vider
      la-bas aussi, et une case vide sans compteur neuf se ferait remplir par la
      vieille copie que le serveur garde encore. */
  function effacer(n) {
    const ou = n || actif;
    try { stockage && stockage.removeItem(cle(ou)); } catch (e) { /* rien */ }
    avancer(ou);
    prevenirEcriture(ou);
  }

  /** Copie TELLE QUELLE, a l'octet : une copie qu'on relit et reecrit passerait
      par `completer()` et ne serait plus la partie qu'on a voulu garder. */
  function copier(de, vers) {
    const b = brut(de);
    if (!b || de === vers) return false;
    try { stockage.setItem(cle(vers), b); } catch (e) { return false; }
    // La case d'arrivee vient de changer : c'est une version de plus, comme une
    // sauvegarde. Celle de depart, elle, n'a pas bouge.
    avancer(vers);
    prevenirEcriture(vers);
    return true;
  }

  /** Ce que le choix des parties montre d'un emplacement, ou null s'il est vide
      (ou illisible : il n'y a rien a en reprendre). */
  function apercu(n) {
    const p = lire(n);
    if (!p || typeof p !== 'object') return null;
    return { jour: p.jour || 1, argent: p.argent || 0,
             secondes: (p.stats && p.stats.secondes) || 0,
             missions: p.missionsFaites ? Object.keys(p.missionsFaites).length : 0,
             sauveeLe: typeof p.sauveeLe === 'number' ? p.sauveeLe : null };
  }

  function occupes() {
    const out = [];
    for (let n = 1; n <= EMPLACEMENTS; n++) if (apercu(n)) out.push(n);
    return out;
  }

  function marquerRouverture(n) { try { session && session.setItem(CLE_ROUVRIR, String(n)); } catch (e) { /* rien */ } }
  /** L'emplacement a rouvrir, UNE fois apres `marquerRouverture(n)` — le
      drapeau se lit et s'efface —, sinon 0. ⚠️ Le numero voyage avec le
      drapeau : on a pu prendre une case VIDE, et le choix doit se rouvrir sur
      elle, pas sur la premiere partie qui existe. */
  function rouverture() {
    try {
      const n = session ? parseInt(session.getItem(CLE_ROUVRIR), 10) : 0;
      if (session) session.removeItem(CLE_ROUVRIR);
      return n >= 1 && n <= EMPLACEMENTS ? n : 0;
    } catch (e) { return 0; }
  }

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
    for (const k of ['armes', 'planque', 'proprietes', 'missionsFaites', 'paquets', 'stats', 'connus', 'nettoyage', 'boulots', 'paliers', 'objets', 'assurance', 'contrebande', 'contacts', 'triches']) {
      out[k] = Object.assign({}, base[k], (partie[k] && typeof partie[k] === 'object') ? partie[k] : {});
    }
    if (!Array.isArray(out.tenues) || out.tenues.indexOf('chandail') < 0) out.tenues = ['chandail'].concat(Array.isArray(out.tenues) ? out.tenues : []);
    // ⚠️ Un tableau ne passe pas par la fusion des objets ci-dessus : une
    // partie d'avant la fourriere arriverait avec `undefined`, et le comptoir
    // planterait au premier clic.
    if (!Array.isArray(out.fourriere)) out.fourriere = [];
    if (!Array.isArray(out.carnet)) out.carnet = [];
    if (!Array.isArray(out.skimmers)) out.skimmers = [];
    // ⚠️ M16 : les trois champs des choix et des gangs, en tableau ordonne (un
    // tableau ne passe pas par la fusion d'objets ci-dessus). Une vieille
    // partie repart avec tout a vide.
    if (!Array.isArray(out.libere)) out.libere = [];
    if (!Array.isArray(out.calmes)) out.calmes = [];
    if (!Array.isArray(out.fermees)) out.fermees = [];
    if (!out.choix || typeof out.choix !== 'object') out.choix = {};
    // ⚠️ Une partie d'avant les chantiers REPART de son jour : sinon elle
    // s'ouvrirait au trentieme jour sur trois batiments neufs qu'on n'a jamais
    // vus tomber.
    if (!partie.chantiers || typeof partie.chantiers.debut !== 'number') {
      out.chantiers = { debut: typeof out.jour === 'number' ? out.jour : 1 };
    }
    if (!out.armes.poings) out.armes.poings = { mun: null };
    if (!out.armes[out.arme]) out.arme = 'poings';
    if (!out.armes[out.armePrecedente]) out.armePrecedente = 'poings';
    return out;
  }

  return { CLE, CLE_OPTIONS, CLE_EMPLACEMENT, CLE_COMPTEUR, EMPLACEMENTS, init, cle, emplacement, choisir, lire, ecrire, effacer, copier,
           poser, compteur, poserCompteur, surEcriture,
           apercu, occupes, marquerRouverture, rouverture, completer, ecrireOptions, lireOptions };
})();
