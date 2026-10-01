/* Bandini — les bancs de neige qui enlisent (docs/jalons/les-quatre-saisons-realistes.md, lot 6, vague 6c).

   L'hiver, la charrue laisse un BANC le long de chaque trottoir (la rue des saisons, vague 4b, le peint). Ici, il
   TIENT : un char qui l'effleure de cote freine un peu et la neige gicle ; qui l'aborde lentement le monte au pas ;
   qui y fonce s'y PLANTE — les roues patinent, la neige gicle, et on s'en sort en marche arriere, en bercant
   (avancer, reculer, avancer), ou on ne s'y prend pas du tout en 4 roues. La motoneige et les coques n'en savent rien.

   ⚠️ LE DESSIN ET LA CONDUITE LISENT LE MEME PROFIL (`largeurs`) : le banc chevauche la bordure — une levre dans la
   rue (au plus `rue.max` px : les roues d'un char au milieu de sa voie passent a 3 px de la bordure et ne la touchent
   jamais), le gros sur le bord du trottoir. La ou il est peint, il tient ; ailleurs, rien.

   ⚠️ UNE PURE FONCTION DU JOUR ET DE L'HEURE (`grosseurA`) : la neige qui tient (la palette, 4b), plus chaque tempete
   de l'hiver que la charrue a repoussee au bord, jusqu'a un plafond ; au degel, elle fond avec la palette. Aucun de,
   rien de pose, aucune entite : la ville ne glisse pas. Seul l'etat d'un char PRIS vit sur le char (`v.banc`).

   ⚠️ LA VILLE NE S'Y JETTE PAS : le trafic roule sur ses rails, au milieu de sa voie (il ne passe jamais ici) ; l'IA
   hors des rails (la police, les poursuivants) y perd de l'elan mais n'y reste jamais prise. */

const BancsDeNeige = (function () {
  'use strict';

  //: ⚠️ LES REGLAGES VIVENT ICI, PAS DANS LE PAQUET (comme `Derapage` et `Glace`) : du ressenti de conduite que Python
  //: ne lit jamais, et le paquet des definitions a un plafond gzip. La largeur du banc (3 a 6 px a la neige pleine)
  //: et ses couleurs restent dans le paquet (`saisons.rue.bancs`) : le dessin de la vague 4b.
  const REGLAGES = {
    //: La part de la largeur qui deborde dans la RUE, et son plafond en px : le reste est sur le trottoir.
    "rue": {"part": 0.5, "max": 3},
    //: La grosseur : la neige qui tient (1 a la neige pleine de l'hiver), plus `croissance` par tempete de l'hiver,
    //: au plus `max` tempetes ; arrondie au 1/`paliers` (une repeinte des morceaux par palier, jamais par image).
    "tempetes": {"croissance": 0.15, "max": 3},
    "paliers": 20,
    //: Les roues : a (longueur/2 - `avant`) du centre, (largeur/2 - `cote`) de cote mais jamais plus de `voie` (un
    //: camion de 16 px n'a pas les roues plus ecartees qu'une auto : au milieu de sa voie, elles passent a 3 px de la
    //: bordure, comme les autres) ; une roue compte des qu'elle est `contact` px dans la neige. La carrosserie surplombe
    //: le banc : ce sont les roues qui le touchent.
    "roues": {"avant": 4, "cote": 2, "voie": 5, "contact": 0.5},
    //: PLANTE : abordé a `vitesse` px/image ou plus VERS le banc (pas le long) ; `pleine` : la prise la plus profonde.
    "prise": {"vitesse": 0.9, "pleine": 2.6},
    //: Et il s'y enfonce : de `enfonce` px (le plus doux, le plus profond) au-dela de la ou il l'a touche — le nez
    //: dans la neige, pas sur le bord.
    "enfonce": [1, 3],
    //: RETENU (abordé plus lentement) : on le monte au pas, au plus `ramper` px/image vers le banc (divise par la
    //: grosseur). Et il freine : `frottement` x la neige sous les roues (0 a 1), par image, selon qui conduit.
    "ramper": 0.25,
    "frottement": {"joueur": 0.06, "pousse": 0.05, "ia": 0.04},
    //: SORTIR : l'effort a fournir = `base` + `profond` x la prise x la grosseur. Par image a fond : `recul` en
    //: marche arriere, `pousser` en avancant plus loin dedans.
    "sortir": {"base": 0.7, "profond": 0.8, "recul": 0.007, "pousser": 0.003, "vitesse": 0.7},
    //: BERCER : changer de sens moins de `fenetre` images apres le dernier effort ajoute `coup` a l'effort, et chaque
    //: aller-retour (au plus `max`) multiplie l'effort par (1 + `gain` x allers-retours). Le char va et vient de
    //: `pas` px par image, au plus `ampleur` px autour de sa place.
    "berce": {"fenetre": 40, "coup": 0.2, "gain": 0.5, "max": 4, "ampleur": 1.5, "pas": 0.15},
    //: Ce qui pousse la neige au lieu de s'y planter : le 4 roues, et les camions lourds (`masse` ou plus, la masse de
    //: la fiche, l'auto valant 1 : le camion, l'autobus, l'asphalteuse, la pelleteuse).
    "pousse": {"slugs": ["quatre_roues"], "masse": 2.5},
    //: La neige qui gicle : `impact` grains quand on se plante, `patine` par image quand les roues patinent, un grain
    //: toutes les `frotte` images quand on frotte ; le son des roues qui patinent toutes les `son` images ; le rappel
    //: (comment s'en sortir) au plus toutes les `rappel` images, quand le HUD n'a rien d'autre a dire.
    "gicle": {"impact": 18, "patine": 3, "frotte": 3, "son": 20, "rappel": 600, "couleurs": ["#f4f7fb", "#dfe5ee", "#c9d2de"]},
  };

  let coupe = false;
  /** Pour les juges : couper les bancs (l'hiver d'avant la vague 6c : peints dans la rue, sans physique), puis les remettre. */
  function couper(oui) { coupe = !!oui; }
  function reglages() { return REGLAGES; }
  function donnees() { return B.defs && B.defs.saisons && B.defs.saisons.rue && B.defs.saisons.rue.bancs; }

  // --- Quand : la grosseur, une pure fonction du jour et de l'heure ---------------------------------------------

  //: La neige pleine de la palette d'hiver : un banc est a sa pleine largeur a cette neige-la (4b).
  const NEIGE_PLEINE = 0.7;

  /** Combien de tempetes l'hiver a deja repoussees au bord, a ce moment (des fractions pendant qu'elle tombe : la
      charrue passe et repasse). L'hiver d'ou l'on vient compte encore au degel. Pure. */
  function tempetesA(jour, heure) {
    if (typeof Neige === 'undefined' || !Neige.donnees() || typeof Calendrier === 'undefined') return 0;
    const t = Neige.donnees().tempete, x = jour + (heure || 0);
    // Le dernier jour d'hiver, au plus tard aujourd'hui (le degel d'avril fond l'hiver de mars) ; puis son debut.
    let fin = jour;
    while (fin >= 1 && jour - fin < 20 && Calendrier.saison(fin) !== 'hiver') fin--;
    if (fin < 1 || Calendrier.saison(fin) !== 'hiver') return 0;
    let debut = fin;
    while (debut > 1 && Calendrier.saison(debut - 1) === 'hiver') debut--;
    let n = 0;
    for (let d = debut; d <= fin; d++) {
      if (Neige.rangDeTempete(d) < 0) continue;
      const a = d + t.debut_h / 24, b = d + t.fin_h / 24;
      n += Math.max(0, Math.min(1, (x - a) / (b - a)));
    }
    return n;
  }

  /** La grosseur des bancs ce jour-la, a cette heure : 0 (pas de banc) a 1,45 (apres trois tempetes). Arrondie au
      palier : c'est elle que le dessin ET la conduite lisent. Pure. */
  function grosseurA(jour, heure) {
    if (typeof Saisons === 'undefined' || !B.defs.saisons || !donnees()) return 0;
    const neige = Saisons.paletteA(jour, heure).neige || 0;
    if (neige <= 0.02) return 0;
    const k = Math.min(1, neige / NEIGE_PLEINE), T = REGLAGES.tempetes;
    const g = k * (1 + T.croissance * Math.min(T.max, tempetesA(jour, heure)));
    return Math.round(g * REGLAGES.paliers) / REGLAGES.paliers;
  }

  function maintenant() { return B.partie ? [B.partie.jour, B.partie.heure] : null; }
  /** Pour le DESSIN (la rue des saisons) : la grosseur du moment, qu'on soit dehors ou non. */
  function grosseurVue() { const m = maintenant(); return m ? grosseurA(m[0], m[1]) : 0; }
  /** La cle de repeinte des morceaux : elle ne change qu'au palier de grosseur. */
  function cle() { return String(grosseurVue()); }

  /** Pour la CONDUITE : la grosseur la ou l'on roule — 0 dans une piece, au chalet du rang (`Monde.carte` y est le
      bloc), ou bancs coupes. */
  function grosseur() {
    const c = Monde.carte;
    if (coupe || !c || !c.laVille || B.interieur || B.bloc) return 0;
    return grosseurVue();
  }

  // --- Ou : le profil, le meme pour le dessin et pour les roues -------------------------------------------------

  /** La houle du banc le long de la bordure (4b) : continue d'une tuile a l'autre (la coordonnee du monde). `p` : la
      position dans la tuile, par pas de 2 px. Pure. */
  function houle(tx, ty, c, p) {
    const vertical = c >= 2, s = (vertical ? ty : tx) * 16 + p + (c * 37);
    return 0.5 + 0.32 * Math.sin(s * 0.21) + 0.18 * Math.sin(s * 0.057 + (vertical ? tx : ty));
  }

  /** Le banc du cote `c` de la tuile de rue (tx, ty), a la position `p` (0 a 15) : { rue, trottoir } en px — la
      levre dans la rue, le gros sur le trottoir —, ou null (pas de banc a cette grosseur). Pure. */
  function largeurs(tx, ty, c, p, g) {
    const d = donnees();
    if (!d || !(g > 0)) return null;
    const q = p - (p & 1);
    const w = (d.largeur[0] + houle(tx, ty, c, q) * (d.largeur[1] - d.largeur[0])) * g;
    if (w < 0.5) return null;
    const R = REGLAGES.rue, rue = Math.min(R.max, Math.max(1, Math.round(w * R.part)));
    return { rue: rue, trottoir: Math.max(1, Math.round(w) - rue) };
  }

  //: Les cotes d'une tuile : [dx, dy] vers le voisin (0 nord, 1 sud, 2 ouest, 3 est) — ceux de `RueDesSaisons.bancsDe`.
  const COTES = [[0, -1], [0, 1], [-1, 0], [1, 0]];

  /** Les cotes a banc d'une tuile de rue, gardes par tuile pour la carte (la rue ne bouge pas). */
  function cotesDe(tx, ty) {
    const c = Monde.carte;
    if (!c.cotesDeBanc) c.cotesDeBanc = new Map();
    const k = ty * c.w + tx;
    let l = c.cotesDeBanc.get(k);
    if (l === undefined) { l = RueDesSaisons.bancsDe(tx, ty); c.cotesDeBanc.set(k, l); }
    return l;
  }

  /** Le banc sous le point (x, y), s'il y en a un : { profond (px dans la neige, depuis le bord le plus proche),
      nx, ny (la normale de la rue vers le trottoir), cx, cy (un point de la bordure), haut (sa largeur, px) }. */
  function sous(x, y, g) {
    const tx = Math.floor(x / 16), ty = Math.floor(y / 16), lx = x - tx * 16, ly = y - ty * 16;
    let mieux = null;
    const garder = function (profond, c, rx, ry, w) {
      if (profond < REGLAGES.roues.contact || (mieux && mieux.profond >= profond)) return;
      const n = COTES[c];
      const cx = c === 3 ? (rx + 1) * 16 : rx * 16, cy = c === 1 ? (ry + 1) * 16 : ry * 16;
      mieux = { profond: profond, nx: n[0], ny: n[1], cx: c < 2 ? x : cx, cy: c < 2 ? cy : y, haut: w.rue + w.trottoir };
    };
    // Dans la rue : la levre, du cote du trottoir.
    if (Monde.estRoute(tx, ty)) {
      for (const c of cotesDe(tx, ty)) {
        const delta = c === 0 ? ly : c === 1 ? 16 - ly : c === 2 ? lx : 16 - lx;
        const w = largeurs(tx, ty, c, Math.floor(c < 2 ? lx : ly), g);
        if (w && delta < w.rue) garder(Math.min(w.rue - delta, delta + w.trottoir), c, tx, ty, w);
      }
      return mieux;
    }
    // Sur le trottoir : le gros du banc, au bord de la rue voisine.
    if (!Monde.estTrottoir(tx, ty)) return null;
    for (let c = 0; c < 4; c++) {
      // La rue voisine, et SON cote qui regarde ce trottoir.
      const o = COTES[c], rx = tx - o[0], ry = ty - o[1];
      if (!Monde.estRoute(rx, ry) || cotesDe(rx, ry).indexOf(c) < 0) continue;
      const delta = c === 0 ? 16 - ly : c === 1 ? ly : c === 2 ? 16 - lx : lx;
      const w = largeurs(rx, ry, c, Math.floor(c < 2 ? lx : ly), g);
      if (w && delta < w.trottoir) garder(Math.min(w.rue + delta, w.trottoir - delta), c, rx, ry, w);
    }
    return mieux;
  }

  /** Les quatre roues d'un char, ou il est (ou en `x, y`). */
  function roues(v, x, y) {
    const R = REGLAGES.roues, a = v.angle, ca = Math.cos(a), sa = Math.sin(a);
    if (x === undefined) { x = v.x; y = v.y; }
    const l = (v.def.longueur || 28) / 2 - R.avant, w = Math.max(1, Math.min(R.voie, (v.def.largeur || 14) / 2 - R.cote));
    return [[l, -w], [l, w], [-l, -w], [-l, w]].map(function (r) {
      return { x: x + ca * r[0] - sa * r[1], y: y + sa * r[0] + ca * r[1], avant: r[0] > 0 };
    });
  }

  /** Les roues dans la neige : [{ roue, banc }] (ou en `x, y`). */
  function contacts(v, g, x, y) {
    const out = [];
    for (const r of roues(v, x, y)) { const b = sous(r.x, r.y, g); if (b) out.push({ roue: r, banc: b }); }
    return out;
  }

  /** Le banc est-il SOUS le char (entre ses pare-chocs, sur ses deux traces) ? Un char pris a le nez dedans : ses
      roues avant peuvent etre passees, la neige est sous son ventre. */
  function sousLeChar(v, g, x, y) {
    const R = REGLAGES.roues, a = v.angle, ca = Math.cos(a), sa = Math.sin(a);
    const l = (v.def.longueur || 28) / 2 - 1, w = Math.max(1, Math.min(R.voie, (v.def.largeur || 14) / 2 - R.cote));
    for (let u = -l; u <= l; u += 2) for (const c of [-w, 0, w]) {
      if (sous(x + ca * u - sa * c, y + sa * u + ca * c, g)) return true;
    }
    return false;
  }

  // --- Qui : ce que le banc fait selon le char et qui le conduit -------------------------------------------------

  /** null : il n'en sait rien (la motoneige sur ses skis, une coque). 'pousse' : il pousse la neige (le 4 roues, un
      camion lourd). 'ia' : un conducteur de la ville hors des rails (la police, un poursuivant) — il y perd de l'elan,
      n'y reste jamais pris. 'joueur' : le joueur (et le deuxieme), ou un char sans conducteur qui roule encore. */
  function genre(v) {
    const d = v.def;
    if (!d || d.eau || d.hors_neige < 1) return null;
    if (typeof v.conducteur === 'string') return 'ia';
    const P = REGLAGES.pousse;
    if (P.slugs.indexOf(v.slug) >= 0 || (d.masse || 0) >= P.masse) return 'pousse';
    return 'joueur';
  }

  // --- La neige qui gicle, sans un de ---------------------------------------------------------------------------

  function grain(v, k) { return hash2((B.t || 0) * 13 + k, (v.id || 0) * 7 + 3) >>> 0; }

  /** `n` grains de neige au point (x, y), lances vers (dx, dy) (unitaire), en eventail. Aucun de : l'empreinte de
      l'image et du char. */
  function gicler(v, x, y, dx, dy, n, force) {
    if (typeof Entites === 'undefined' || !Entites.particule) return;
    const C = REGLAGES.gicle.couleurs;
    for (let k = 0; k < n; k++) {
      const h = grain(v, k), ecart = ((h % 1000) / 1000 - 0.5) * 1.4, vit = (0.5 + ((h >>> 10) % 1000) / 1000) * (force || 1);
      const ca = Math.cos(ecart), sa = Math.sin(ecart);
      Entites.particule(x, y, (dx * ca - dy * sa) * vit, (dx * sa + dy * ca) * vit * 0.8,
        12 + ((h >>> 20) % 12), C[(h >>> 4) % C.length], (h >>> 7) % 3 === 0 ? 2 : 1);
    }
  }

  function son(nom, v) {
    if (v.conducteur !== B.joueur || typeof Son === 'undefined' || !Son.SFX || !Son.SFX[nom]) return;
    Son.SFX[nom](v.x, v.y);
  }

  // --- A chaque image : appele par `Vehicules.majPhysique`, une fois la vitesse et le cap faits ------------------

  /** Le banc sous le char : il frotte, il retient, il plante — ou le char pris patine et se bat pour sortir. */
  function maj(v, cmd) {
    const g = grosseur();
    const qui = g && v.z <= 0 ? genre(v) : null;
    if (!qui) { if (v.banc) v.banc = null; return; }
    let b = v.banc;
    // ⚠️ DEPLACE PAR AUTRE CHOSE (une remorqueuse, un char qui le pousse, le garde-fou) : il n'est plus pris.
    if (b && b.pris && Math.hypot(v.x - b.ax - Math.cos(b.angle) * b.decal, v.y - b.ay - Math.sin(b.angle) * b.decal) > 3) b = v.banc = null;
    // ⚠️ PRIS, on juge a SA PLACE (l'ancre), pas ou le bercement l'a pousse d'un cheveu, et la neige SOUS LE CHAR, pas
    // sous ses roues : le nez enfonce, les roues avant ont pu passer le banc. Le banc fond (un palier de degel) : libre.
    if (b && b.pris) {
      if (sousLeChar(v, g, b.ax, b.ay)) majPris(v, cmd, b);
      else v.banc = null;
      return;
    }
    const cs = contacts(v, g);
    if (!cs.length) { if (b) v.banc = null; return; }
    // Vers le banc : de la rue vers le trottoir si le char est cote rue, l'inverse s'il arrive du trottoir.
    let ix = 0, iy = 0, neige = 0;
    for (const c of cs) {
      const s = (v.x - c.banc.cx) * c.banc.nx + (v.y - c.banc.cy) * c.banc.ny < 0 ? 1 : -1;
      ix += c.banc.nx * s * c.banc.profond; iy += c.banc.ny * s * c.banc.profond;
      neige += Math.min(1, c.banc.haut / 6);
    }
    neige = Math.min(1, neige / 4);
    const n = Math.hypot(ix, iy) || 1;
    ix /= n; iy /= n;
    const un = v.vx * ix + v.vy * iy;
    // PLANTE : a l'entree seulement (aucune roue dans la neige l'image d'avant), abordé assez vite VERS le banc.
    if (qui === 'joueur' && !b && un >= REGLAGES.prise.vitesse) { planter(v, un, ix, iy, g, cs); return; }
    v.banc = b || { pris: false };
    v.vitesse *= 1 - REGLAGES.frottement[qui] * neige;
    if (qui === 'joueur') {
      // RETENU : on le monte au pas, jamais plus vite — la vitesse vers le banc est bornee ; et l'elan avec quand on
      // lui fait face (plus de 30°) : de biais, on glisse le long, comme contre une bordure.
      // ⚠️ DANS LES DEUX SENS : passe la bordure, ses roues arriere grimpent encore le banc ; et on en ressort au pas.
      const lim = REGLAGES.ramper / Math.max(1, g), an = Math.abs(un);
      if (an > lim) {
        const s = un > 0 ? 1 : -1;
        v.vx -= ix * s * (an - lim); v.vy -= iy * s * (an - lim);
        const cap = Math.abs(Math.cos(v.angle) * ix + Math.sin(v.angle) * iy);
        if (cap > 0.5 && Math.abs(v.vitesse) * cap > lim) v.vitesse = Math.sign(v.vitesse) * lim / cap;
      }
    }
    // Ca frotte : la neige gicle de la roue qui la laboure.
    const vit = Math.hypot(v.vx, v.vy);
    if (vit > 0.4 && (B.t || 0) % REGLAGES.gicle.frotte === 0) {
      const r = cs[0].roue;
      gicler(v, r.x, r.y, -v.vx / vit, -v.vy / vit, 1, 0.6 + vit * 0.2);
    }
  }

  /** Il y fonce : la neige l'avale. La prise (0 a 1) dit combien il faudra se battre pour en sortir. */
  function planter(v, un, ix, iy, g, cs) {
    const P = REGLAGES.prise, S = REGLAGES.sortir;
    const prise = Math.max(0, Math.min(1, (un - P.vitesse) / (P.pleine - P.vitesse)));
    const sens = v.vitesse >= 0 ? 1 : -1;
    // Le nez dans la neige : il avance encore de quelques pixels dans le banc, puis s'arrete net.
    const vit = Math.hypot(v.vx, v.vy) || 1, e = REGLAGES.enfonce, d = e[0] + (e[1] - e[0]) * prise;
    for (let k = d; k > 0; k -= 0.5) {
      const x = v.x + v.vx / vit * k, y = v.y + v.vy / vit * k;
      if (!Vehicules.bloqueParLesTuiles(v, x, y)) { v.x = x; v.y = y; break; }
    }
    v.banc = { pris: true, sens: sens, prise: prise, besoin: S.base + S.profond * prise * Math.max(1, g), effort: 0,
               berce: 0, dernier: 0, vuT: -1e9, ax: v.x, ay: v.y, angle: v.angle, decal: 0, patine: false, t: B.t || 0 };
    v.vitesse = 0; v.vx = 0; v.vy = 0; v.lacet = 0;
    // L'impact : une gerbe de neige au-dessus de ce qui s'est enfonce, vers le haut et vers l'arriere.
    const r = cs[0].roue;
    gicler(v, r.x + ix * 4, r.y + iy * 4, -ix, -iy, REGLAGES.gicle.impact, 1.4);
    gicler(v, r.x + ix * 4, r.y + iy * 4, ix, iy, Math.round(REGLAGES.gicle.impact / 2), 0.8);
    son('banc_de_neige', v);
    if (v.conducteur === B.joueur) {
      B.cam.secousse = Math.min(1, 0.25 + un * 0.15);
      if (typeof Entree !== 'undefined' && Entree.vibrer) Entree.vibrer(Math.round(80 + un * 40));
      rappeler(v, true);
    }
  }

  //: Le dernier rappel (l'image) : on ne le repete pas a chaque coup de gaz.
  let rappelT = -1e9;
  /** Le HUD dit comment s'en sortir : a l'impact, puis quand on patine sans que le HUD ait autre chose a dire. */
  function rappeler(v, force) {
    if (v.conducteur !== B.joueur || typeof Hud === 'undefined' || !Hud.message) return;
    const t = B.t || 0;
    if (!force && (B.msgT > 0 || t - rappelT < REGLAGES.gicle.rappel)) return;
    rappelT = t;
    Hud.message('PRIS DANS LE BANC — RECULE, OU BERCE : AVANCE, RECULE, AVANCE', 240);
  }

  /** Pris : il ne roule plus. Le gaz ou la marche arriere font patiner les roues ; reculer le sort peu a peu,
      bercer (changer de sens en rythme) bien plus vite. */
  function majPris(v, cmd, b) {
    const S = REGLAGES.sortir, Bc = REGLAGES.berce, t = B.t || 0;
    const i = (cmd && cmd.gaz > 0.1) ? 1 : (cmd && cmd.frein > 0.1) ? -1 : 0;
    const force = i > 0 ? cmd.gaz : i < 0 ? cmd.frein : 0;
    v.vitesse = 0; v.vx = 0; v.vy = 0; v.lacet = 0; v.angle = b.angle;
    b.patine = !!i;
    if (i) {
      if (b.dernier && i !== b.dernier && t - b.vuT <= Bc.fenetre) { b.berce = Math.min(Bc.max, b.berce + 1); b.effort += Bc.coup; }
      b.dernier = i; b.vuT = t;
      b.effort += (i === -b.sens ? S.recul : S.pousser) * force * (1 + Bc.gain * b.berce);
      b.decal = Math.max(-Bc.ampleur, Math.min(Bc.ampleur, b.decal + i * Bc.pas * (1 + 0.3 * b.berce)));
      // Les roues patinent : la neige gicle derriere celles qui poussent (vers l'arriere en avancant, vers l'avant en reculant).
      const dx = -Math.cos(v.angle) * i, dy = -Math.sin(v.angle) * i;
      for (const r of roues(v)) if (r.avant === (b.sens > 0)) gicler(v, r.x, r.y, dx, dy, REGLAGES.gicle.patine, 1.6 + 0.25 * b.berce);
      if (t % REGLAGES.gicle.son === 0) { son('roues_patinent', v); rappeler(v, false); }
    } else b.decal *= 0.85;
    // Le char va et vient d'un cheveu autour de sa place : on le voit bercer.
    const x = b.ax + Math.cos(b.angle) * b.decal, y = b.ay + Math.sin(b.angle) * b.decal;
    if (!Vehicules.bloqueParLesTuiles(v, x, y)) { v.x = x; v.y = y; }
    if (b.effort >= b.besoin) {
      // Il sort, du cote ou il poussait : en marche arriere, il recule hors du banc ; en avant, il le franchit au pas.
      const sens = i || -b.sens;
      v.banc = { pris: false, libre: true };
      v.vitesse = sens * S.vitesse;
      v.vx = Math.cos(v.angle) * v.vitesse; v.vy = Math.sin(v.angle) * v.vitesse;
      gicler(v, v.x, v.y, -Math.cos(v.angle) * sens, -Math.sin(v.angle) * sens, 6, 1.2);
    }
  }

  function estPris(v) { return !!(v && v.banc && v.banc.pris); }

  // --- Le dessin : le banc peint (la rue des saisons), et la neige sur le nez d'un char pris ---------------------

  /** La neige ramassee sur le pare-chocs d'un char PRIS, du cote enfonce : par-dessus le char. */
  function dessiner(ctx, cam) {
    if (!B.entites || !grosseur()) return;
    const d = donnees(), cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const v of B.entites) {
      if (v.type !== 'vehicule' || !estPris(v)) continue;
      const b = v.banc, a = v.angle, ca = Math.cos(a), sa = Math.sin(a);
      const bout = (v.def.longueur / 2 - 1) * b.sens, x = v.x + ca * bout - cx, y = v.y + sa * bout - cy;
      if (x < -20 || y < -20 || x > VW + 20 || y > VH + 20) continue;
      const larg = v.def.largeur / 2 + 1, prof = 2 + 3 * b.prise;
      for (let k = -larg; k <= larg; k += 1) {
        const bosse = prof * (1 - (k * k) / (larg * larg + 1)) + 0.5 * Math.sin(k * 1.7 + v.id);
        for (let e = 0; e < bosse; e += 1) {
          const px = Math.round(x - sa * k - ca * e * b.sens), py = Math.round(y + ca * k - sa * e * b.sens);
          ctx.fillStyle = e > bosse - 1.2 ? d.ombre : d.neige;
          ctx.fillRect(px, py, 1, 1);
        }
      }
      B.stats.rects += Math.round(larg * 2 * prof);
    }
  }

  return { reglages, couper, grosseurA, grosseur, grosseurVue, cle, tempetesA, largeurs, houle, sous, roues, contacts, sousLeChar,
           genre, maj, estPris, dessiner };
})();
