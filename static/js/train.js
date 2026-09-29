/* Le train : une ligne de passage au rang 6 de la bande nord — au sol, sur le viaduc, dans le tunnel.
   Martin (28 sept. 2026) : « je veux un vrai train aérien, terrestre et tunnel » (docs/jalons/le-train.md).

   ⚠️ LE TRAIN EST UNE HEURE, comme la rame du métro : sa place ne dépend que de
   `Autobus.tempsDeLaPartie()` — rien à simuler, pas un dé, la même place au rechargement. Une seule voie,
   un seul train : il fait l'aller vers l'est (Friches → viaduc → gare centrale → tunnel), attend `bout`
   images sous la montagne, fait le retour, attend `bout` images hors carte à l'ouest. */
const Train = (function () {
  'use strict';
  const TT = 16;
  let cache = null, source = null;

  /** Distance couverte et vitesse, `t` images après le départ d'un arrêt, sur un tronçon de `d` px qui finit à
      l'arrêt : accélération `a` jusqu'à `v`, croisière, freinage — ou un triangle si le tronçon est court. */
  function profil(d, v, a, t) {
    const ta = v / a, da = v * ta / 2;
    if (2 * da >= d) {
      const tm = Math.sqrt(d / a);
      if (t <= tm) return { s: a * t * t / 2, v: a * t };
      const r = Math.max(0, 2 * tm - t);
      return { s: d - a * r * r / 2, v: a * r };
    }
    const tc = (d - 2 * da) / v, total = 2 * ta + tc;
    if (t <= ta) return { s: a * t * t / 2, v: a * t };
    if (t <= ta + tc) return { s: da + v * (t - ta), v: v };
    const r = Math.max(0, total - t);
    return { s: d - a * r * r / 2, v: a * r };
  }
  function dureeProfil(d, v, a) {
    const ta = v / a, da = v * ta / 2;
    return 2 * da >= d ? 2 * Math.sqrt(d / a) : 2 * ta + (d - 2 * da) / v;
  }

  /** Un trajet : les arrêts de la TÊTE, en px, dans l'ordre du sens. À l'est, la tête est le bout est du train :
      arrêté en gare, son milieu est sur la gare. Le départ et la fin sont hors carte (ou sous la montagne). */
  function trajet(t, sens) {
    const L = t.horaire.longueur, gares = t.gares.map(function (g) { return { nom: g[0], x: g[1] }; });
    const depart = { nom: null, px: -(L + 40) * TT }, fin = { nom: null, px: (t.tunnel + L + 45) * TT };
    let arrets = gares.map(function (g) { return { nom: g.nom, px: (g.x + 0.5 + L / 2) * TT }; });
    if (sens < 0) {
      arrets = gares.slice().reverse().map(function (g) { return { nom: g.nom, px: (g.x + 0.5 - L / 2) * TT }; });
      return [{ nom: null, px: fin.px - L * TT }].concat(arrets, [{ nom: null, px: depart.px }]);
    }
    return [depart].concat(arrets, [fin]);
  }

  function donnees() {
    const t = B.defs && B.defs.carte && B.defs.carte.train;
    if (!t) { cache = null; source = null; return null; }
    if (t === source) return cache;
    const h = t.horaire, trajets = [];
    let debut = 0;
    [1, -1].forEach(function (sens) {
      const pts = trajet(t, sens), troncons = [];
      for (let i = 0; i + 1 < pts.length; i++) {
        const d = Math.abs(pts[i + 1].px - pts[i].px), duree = dureeProfil(d, h.vitesse, h.acceleration);
        const arret = pts[i].nom ? h.arret : 0;     // on attend en gare AVANT de repartir
        troncons.push({ de: pts[i], vers: pts[i + 1], d: d, debut: debut, arret: arret, duree: duree });
        debut += arret + duree;
      }
      trajets.push({ sens: sens, troncons: troncons });
      debut += h.bout;
    });
    source = t;
    cache = Object.assign({}, t, { yPx: (t.rang + 0.5) * TT, trajets: trajets, periode: debut });
    return cache;
  }

  function etat(temps) {
    const d = donnees();
    if (!d) return null;
    const phase = ((temps % d.periode) + d.periode) % d.periode;
    for (const tr of d.trajets) {
      for (const c of tr.troncons) {
        if (phase < c.debut || phase >= c.debut + c.arret + c.duree) continue;
        if (phase < c.debut + c.arret) return { sens: tr.sens, tete: c.de.px, vitesse: 0, gare: c.de.nom };
        const p = profil(c.d, d.horaire.vitesse, d.horaire.acceleration, phase - c.debut - c.arret);
        return { sens: tr.sens, tete: c.de.px + tr.sens * p.s, vitesse: p.v, gare: null };
      }
    }
    return null;                                     // au bout, sous la montagne ou hors carte
  }

  /** Ce que le train couvre, en px, de gauche à droite. */
  function etendue(e) {
    const L = donnees().horaire.longueur * TT;
    return e.sens > 0 ? [e.tete - L, e.tete] : [e.tete, e.tete + L];
  }

  function enVille() { return !B.interieur && !B.bloc; }

  // ---------------------------------------------------------------- la géométrie
  /** Le viaduc, rampes comprises : du pied de la rampe ouest au pied de la rampe est. */
  function surLeViaduc(x) {
    const d = donnees();
    return !!d && x >= d.viaduc[0] * TT && x < (d.viaduc[1] + 1) * TT;
  }
  /** Au sol : ni sur le viaduc ni ses rampes, ni passé le portail du tunnel. */
  function auSol(x) {
    const d = donnees();
    return !!d && !surLeViaduc(x) && x < d.tunnel * TT;
  }
  const HAUT = 12;                                   // la hauteur du tablier, en px d'écran
  /** La hauteur de la voie à x : 0 au sol, `HAUT` sur le tablier, en pente sur les rampes. */
  function hauteur(x) {
    const d = donnees();
    if (!d || !surLeViaduc(x)) return 0;
    const a = d.viaduc[0] * TT, b = (d.viaduc[1] + 1) * TT, r = d.rampe * TT;
    return Math.round(HAUT * Math.min(1, (x - a) / r, (b - x) / r));
  }

  // ---------------------------------------------------------------- les passages à niveau
  /** Un passage est fermé quand le train le couvre, quand sa tête en est à moins de `annonce` px devant lui, ou
      tant que sa queue ne l'a pas dépassé d'une tuile. ⚠️ FONCTION DE L'HEURE SEULE : un saut dans le temps
      (dormir, recharger) ne laisse jamais une barrière coincée. */
  function passageFerme(i, temps) {
    const d = donnees(), e = d && etat(temps);
    if (!e) return false;
    const p = d.passages[i], a = p[0] * TT, b = (p[1] + 1) * TT, ext = etendue(e);
    const g = e.sens > 0 ? ext[0] - TT : ext[0] - d.horaire.annonce;
    const dr = e.sens > 0 ? ext[1] + d.horaire.annonce : ext[1] + TT;
    return dr > a && g < b;
  }

  /** ⚠️ ON N'ATTEND JAMAIS SUR LA VOIE. Deux passages sont à la bouche d'un carrefour du boulevard : sa ligne
      d'arrêt (la tuile « S ») tombe sur les rails, et un char qui y attendait son tour attendait sur la voie.
      Rend la tuile où s'arrêter : une tuile avant la voie si la ligne est sur un passage, sinon la ligne. */
  function ligneHorsDeLaVoie(sx, sy, p) {
    const d = donnees();
    if (!d || sy !== d.rang || !enVille()) return [sx, sy];
    for (const q of d.passages) if (sx >= q[0] && sx <= q[1]) return [sx - p[0], sy - p[1]];
    return [sx, sy];
  }

  /** ENGAGÉ : le nez a passé la ligne reculée d'un passage. Un char engagé ne s'arrête plus avant le carrefour
      (ni feu, ni STOP, ni boîte) — sinon « jamais derrière soi » (`pointDArret`) l'arrêtait là où il était, sur
      les rails. Faux partout ailleurs. */
  function engage(v, sx, sy, p) {
    const l = ligneHorsDeLaVoie(sx, sy, p);
    if (l[0] === sx && l[1] === sy) return false;
    const demi = v.def.longueur / 2;
    const nx = v.x + p[0] * demi, ny = v.y + p[1] * demi;
    const bx = l[0] * TT + 8 + p[0] * 8, by = l[1] * TT + 8 + p[1] * 8;
    return (nx - bx) * p[0] + (ny - by) * p[1] > 0;
  }

  const PAS_RUE = { '^': -1, 'v': 1 };
  /** La distance d'un char jusqu'à sa ligne d'arrêt devant un passage FERMÉ, dans sa file. Jamais pour une rame
      ni pour une poursuite (comme le signaleur de chantier, `Chantiers.signalDevant`) : la police passe, et le
      train la heurte comme les autres. */
  function signalDevant(v) {
    const d = donnees();
    if (!d || v.rails || v.poursuite || !enVille()) return Infinity;
    const pas = PAS_RUE[v.sens];
    if (!pas) return Infinity;
    const tx = Math.floor(v.x / TT), temps = Autobus.tempsDeLaPartie();
    for (let i = 0; i < d.passages.length; i++) {
      const p = d.passages[i];
      if (tx < p[0] || tx > p[1] || !passageFerme(i, temps)) continue;
      // Le bord de la voie : la même ligne que celle d'un carrefour reculée hors des rails (`ligneHorsDeLaVoie`).
      const ligne = pas < 0 ? (d.rang + 1) * TT : d.rang * TT;
      const devant = (ligne - v.y) * pas - v.def.longueur / 2;
      if (devant >= -2 && devant < 6 * TT) return Math.max(0, devant);
    }
    return Infinity;
  }

  // Les barrières défoncées : le passage du train où on les a cassées. Dessinées cassées jusqu'au train suivant
  // (un état d'image, pas d'horaire : c'est un dégât, pas une heure).
  const brises = {};
  function cycle(temps) { return Math.floor(temps / donnees().periode); }
  function brisee(i) {
    const d = donnees();
    return !!d && brises[i] === cycle(Autobus.tempsDeLaPartie());
  }
  /** Le joueur au volant qui passe une barrière baissée la casse — sans étoile : la barrière n'est pas la police. */
  function defoncer() {
    const d = donnees(), j = B.joueur, v = j && j.dansVehicule;
    if (!v) return;
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT), temps = Autobus.tempsDeLaPartie();
    if (ty < d.rang - 1 || ty > d.rang + 1 || Math.hypot(v.vx || 0, v.vy || 0) < 0.5) return;
    for (let i = 0; i < d.passages.length; i++) {
      const p = d.passages[i];
      if (tx < p[0] || tx > p[1] || brisee(i) || !passageFerme(i, temps)) continue;
      brises[i] = cycle(temps);
      Son.SFX.casse();
      if (B.cam) B.cam.secousse = Math.max(B.cam.secousse || 0, 4);
    }
  }

  /** Depuis combien d'images (jusqu'à `n`) le passage est fermé : le bras s'abaisse en `n` images. */
  function fermeDepuis(i, temps, n) {
    let k = 0;
    while (k < n && passageFerme(i, temps - k - 1)) k++;
    return k;
  }

  /** Les barrières d'un passage : un poteau de chaque côté de la rue, ses deux feux rouges qui alternent, et le
      bras rayé qui s'abaisse sur la file qui arrive (au sud pour ceux qui montent, au nord pour ceux qui descendent). */
  function dessinerPassages(ctx, cx, cy, y0) {
    const d = donnees(), temps = Autobus.tempsDeLaPartie();
    for (let i = 0; i < d.passages.length; i++) {
      const p = d.passages[i], xa = p[0] * TT - cx, xb = (p[1] + 1) * TT - cx;
      if (xb < -40 || xa > VW + 40) continue;
      const ferme = passageFerme(i, temps), casse = brisee(i);
      const bas = ferme ? fermeDepuis(i, temps, 45) / 45 : 0;
      const long = xb - xa;
      // [x du poteau, y du bras, sens du bras]
      for (const [px, yb, dir] of [[xb + 2, y0 + TT + 3, -1], [xa - 4, y0 - 5, 1]]) {
        ctx.fillStyle = '#2d2d30'; ctx.fillRect(px, yb - 3, 3, 6);                     // le poteau
        const allume = ferme && (Math.floor(temps / 30) % 2 === 0);
        ctx.fillStyle = allume ? '#ff3b2f' : '#5a1d1a'; ctx.fillRect(px - 1, yb - 5, 2, 2);
        ctx.fillStyle = ferme && !allume ? '#ff3b2f' : '#5a1d1a'; ctx.fillRect(px + 2, yb - 5, 2, 2);
        const bras = Math.round((casse ? 0.3 : bas) * (long * 0.6));
        for (let k = 0; k < bras; k++) {
          ctx.fillStyle = Math.floor(k / 3) % 2 ? '#e6e6e6' : '#c8261e';
          ctx.fillRect(dir < 0 ? px - 1 - k : px + 3 + k, yb, 1, 2);
        }
        if (!bras) { ctx.fillStyle = '#c8261e'; ctx.fillRect(px, yb - 1, 3, 1); }     // levé : le bras en l'air
      }
      B.stats.rects += 14;
    }
  }

  // ---------------------------------------------------------------- les piliers et les rampes, solides
  // ⚠️ Comme le tronc du sapin (`Fetes.maj`) : la carte de la ville se rebâtit (nouvelle partie, bloc,
  // chargement) et oublie ce qu'on y a posé — on remarque chaque carte neuve. Les rampes sont un REMBLAI :
  // on ne traverse la voie ni à pied ni en char là où elle monte ; sous le tablier, seuls les piliers.
  let marquee = null;
  function marquer() {
    const d = donnees(), c = Monde.carte;
    if (!d || !c || c === marquee) return;
    const poser = function (x) { c.solide[d.rang * c.w + x] = 1; };
    d.piliers.forEach(poser);
    for (let k = 0; k < d.rampe; k++) { poser(d.viaduc[0] + k); poser(d.viaduc[1] - k); }
    marquee = c;
  }

  // ---------------------------------------------------------------- ce qu'on entend
  const PORTEE_CLOCHE = 500, PORTEE_ROULEMENT = 900;
  /** La cloche du passage fermé le plus proche, et le roulement du train à sa distance — étouffé de moitié
      quand il passe sur le viaduc au-dessus de soi, coupé passé le portail. Rien, hors de la ville. */
  function entendre() {
    const d = donnees(), j = B.joueur;
    if (!d || !j || !enVille()) { Son.SFX.cloche_passage(0); Son.SFX.roulement_train(0); return; }
    if (Math.abs(j.y - d.yPx) < 60 * TT) Son.Lieu.charger('train');   // ses sons, une fois, en approchant de la ligne
    const temps = Autobus.tempsDeLaPartie();
    let cloche = 0;
    for (let i = 0; i < d.passages.length; i++) {
      if (!passageFerme(i, temps)) continue;
      const p = d.passages[i], px = (p[0] + p[1] + 1) / 2 * TT;
      cloche = Math.max(cloche, 1 - Math.hypot(px - j.x, d.yPx - j.y) / PORTEE_CLOCHE);
    }
    Son.SFX.cloche_passage(cloche * 0.9);
    const e = etat(temps);
    let roule = 0;
    if (e) {
      const ext = etendue(e), fin = d.tunnel * TT;
      if (ext[0] < fin) {
        const x = Math.max(ext[0], Math.min(Math.min(ext[1], fin), j.x));
        roule = 1 - Math.hypot(x - j.x, d.yPx - j.y) / PORTEE_ROULEMENT;
        roule *= e.vitesse > 0 ? Math.min(1, 0.35 + e.vitesse / d.horaire.vitesse) : 0.2;
        if (surLeViaduc(x) && surLeViaduc(j.x)) roule *= 0.5;      // sous le tablier : le béton étouffe
      }
    }
    Son.SFX.roulement_train(Math.max(0, roule));
  }

  function maj() {
    entendre();
    if (!enVille() || !donnees()) return;
    marquer();
    defoncer();
    heurter();
    klaxonner();
  }

  // ---------------------------------------------------------------- ce qu'il heurte
  // ⚠️ LE TRAIN NE FREINE JAMAIS : il klaxonne, et il passe. La source des dégâts est le train, jamais le
  // joueur : ni meurtre ni crime à son compte (`Entites.tuer` ne crédite que `source === B.joueur`).
  const TRAIN = { type: 'train', nom: 'le train', x: 0, y: 0 };
  // ⚠️ CE QUI FRAPPE TIENT DANS LA RANGÉE DES RAILS (7 px de part et d'autre de l'axe), pas dans les 20 px peints :
  // un char arrêté le nez au bord de la voie (la ligne d'arrêt, le signal du passage) doit être hors d'atteinte.
  // À 10 px, le juge des T du trafic a vu le train écraser un char sage, arrêté à sa ligne.
  const DEMI_TRAIN = 7;
  /** La demi-étendue [en x, en y] d'une chose : un char selon son cap, un passant par son rayon. */
  function demiEtendue(q) {
    if (q.type !== 'vehicule' || !q.def) return [q.r || 5, q.r || 5];
    const c = Math.abs(Math.cos(q.angle || 0)), si = Math.abs(Math.sin(q.angle || 0));
    const L = q.def.longueur / 2, W = q.def.largeur / 2;
    return [c * L + si * W, si * L + c * W];
  }
  function heurter() {
    const d = donnees(), e = etat(Autobus.tempsDeLaPartie());
    if (!e || e.vitesse <= 0) return;
    const ext = etendue(e), feu = B.defs.conduite.physique.feu_sous;
    TRAIN.x = e.tete; TRAIN.y = d.yPx;
    const cx = (ext[0] + ext[1]) / 2, demi = (ext[1] - ext[0]) / 2 + TT;
    for (const q of Entites.autour(cx, d.yPx, demi, function (q) {
      return q.vivant && (q.type === 'vehicule' || q.type === 'pieton' || (q.type === 'joueur' && !q.dansVehicule));
    })) {
      // ⚠️ SON ÉTENDUE, PAS SON CENTRE : un autobus debout dans la rue, le nez sur les rails et le centre à
      // 18 px, passait sous le train sans une égratignure (la relecture finale l'a mesuré).
      const dm = demiEtendue(q);
      if (!auSol(q.x) || q.x + dm[0] < ext[0] || q.x - dm[0] > ext[1] || Math.abs(q.y - d.yPx) >= DEMI_TRAIN + dm[1]) continue;
      const cote = q.y >= d.yPx ? 1 : -1;             // on le jette du côté où il est déjà
      if (q.type === 'vehicule') {
        if (q.conducteur !== B.joueur) q.conducteur = null;   // un char du trafic ne se remet pas en voie
        q.etat = q.etat === 'epave' ? q.etat : 'roule';
        q.y = d.yPx + cote * (DEMI_TRAIN + dm[1] + 2);
        q.vx = e.sens * e.vitesse * 0.6; q.vy = cote * e.vitesse * 0.8;
        const vite = e.vitesse > d.horaire.vitesse * 0.66;
        Vehicules.endommager(q, vite ? q.vie - q.vieMax * feu * 0.5 : q.vieMax * 0.3, TRAIN);
        if (B.cam) B.cam.secousse = Math.max(B.cam.secousse || 0, 8);
        Son.SFX.choc();
      } else {
        if (q.type === 'joueur') Hud.message('FRAPPÉ PAR LE TRAIN', 180);
        Entites.blesser(q, 9999, TRAIN, { renverse: true, angle: e.sens > 0 ? 0 : Math.PI, saigne: 90 });
      }
    }
  }

  const COOLDOWN_KLAXON = 180;
  let klaxonT = 0;
  /** Quelque chose sur la voie, à moins de douze tuiles devant le nez : un long coup de klaxon. */
  function klaxonner() {
    if (klaxonT > 0) { klaxonT--; return; }
    const d = donnees(), e = etat(Autobus.tempsDeLaPartie());
    if (!e || e.vitesse <= 0 || !auSol(e.tete)) return;
    const nez = e.tete, loin = nez + e.sens * 12 * TT;
    const devant = Entites.autour((nez + loin) / 2, d.yPx, 7 * TT, function (q) {
      return q.vivant && (q.type === 'vehicule' || q.type === 'pieton' || q.type === 'joueur')
        && Math.abs(q.y - d.yPx) < DEMI_TRAIN + demiEtendue(q)[1] && (q.x - nez) * e.sens > 0 && auSol(q.x);
    });
    if (devant.length) { Son.SFX.klaxon_train(nez, d.yPx); klaxonT = COOLDOWN_KLAXON; }
  }

  // ---------------------------------------------------------------- le dessin
  /** Les voitures du train, de la tête à la queue : `[gauche, droite]` en px, et la locomotive. */
  function voitures(e) {
    const ext = etendue(e), L = ext[1] - ext[0], loco = 4 * TT, n = 3, v = (L - loco) / n;
    const out = [];
    for (let k = 0; k <= n; k++) {
      const long = k === 0 ? loco : v;
      const debut = k === 0 ? 0 : loco + (k - 1) * v;
      // la tête est à droite vers l'est, à gauche vers l'ouest
      const a = e.sens > 0 ? ext[1] - debut - long : ext[0] + debut;
      out.push({ a: a + 1, b: a + long - 1, loco: k === 0 });
    }
    return out;
  }

  /** ⚠️ COMME LES AUTRES VÉHICULES (Martin, 29 sept. 2026) : chaque voiture est une machine en volume
      (`SPRITES.locomotive`, `SPRITES.voiture_train`) peinte par le peintre des chars, `Vehicules.dessinerUn` —
      même projection, même ombre, mêmes phares la nuit. On lui passe un objet qui a la forme d'un char (un par
      voiture, réutilisé d'une image à l'autre) ; `z` le lève sur le viaduc comme un char qui saute. */
  const PEINTES = [];
  function voitureAPeindre(k, w, e, z) {
    const o = PEINTES[k] || (PEINTES[k] = { type: 'train', etat: 'roule', panneT: 0, swaps: null,
                                            def: { classe: 'train', largeur: 16, longueur: 0 } });
    o.sprite = w.loco ? 'locomotive' : 'voiture_train';
    o.conducteur = w.loco ? 'train' : null;          // la locomotive allume ses phares, les voitures non
    o.def.longueur = w.loco ? 64 : 80;
    o.x = (w.a + w.b) / 2; o.y = donnees().yPx; o.z = z;
    o.angle = e.sens > 0 ? 0 : Math.PI;
    return o;
  }
  /** Peinte, et coupée au portail : ce qui est passé à l'est de `fin` est sous la montagne. */
  function peindreVoiture(ctx, o, cx, cy, fin) {
    ctx.save();
    ctx.beginPath(); ctx.rect(-100000, -100000, fin - cx + 100000, 200000); ctx.clip();
    Vehicules.dessinerUn(ctx, o, cx, cy);
    ctx.restore();
  }

  /** Au sol : la voie (ballast, traverses, rails d'écartement de vrai train), et l'ombre du tablier. */
  function dessinerVoie(ctx, vue) {
    const d = donnees();
    if (!d || !enVille()) return;
    const cx = Math.round(vue.x), cy = Math.round(vue.y), y0 = d.rang * TT - cy;
    if (y0 > VH + 40 || y0 < -60) return;
    const t0 = Math.max(0, Math.floor(cx / TT)), t1 = Math.min(d.tunnel - 1, Math.floor((cx + VW) / TT));
    for (let tx = t0; tx <= t1; tx++) {
      const x = tx * TT - cx;
      if (tx >= d.viaduc[0] && tx <= d.viaduc[1]) {
        const rampe = tx < d.viaduc[0] + d.rampe || tx > d.viaduc[1] - d.rampe;
        if (!rampe) { ctx.fillStyle = 'rgba(0,0,0,0.26)'; ctx.fillRect(x, y0 + 6, TT, TT + 6); }   // l'ombre du tablier
        continue;
      }
      if (d.passages.some(function (q) { return tx >= q[0] && tx <= q[1]; })) {
        ctx.fillStyle = '#4b4a48'; ctx.fillRect(x, y0 + 1, TT, 14);             // le passage : un tablier de caoutchouc
        ctx.fillStyle = '#3c3b39'; ctx.fillRect(x, y0 + 1, TT, 1); ctx.fillRect(x, y0 + 14, TT, 1);
      } else {
        ctx.fillStyle = '#7d7466'; ctx.fillRect(x, y0 + 1, TT, 14);
        ctx.fillStyle = '#5b3f28';
        for (let k = 1; k < TT; k += 4) ctx.fillRect(x + k, y0 + 2, 2, 12);
      }
      ctx.fillStyle = '#c9ccd1'; ctx.fillRect(x, y0 + 3, TT, 1); ctx.fillRect(x, y0 + 11, TT, 1);
      ctx.fillStyle = '#8b9097'; ctx.fillRect(x, y0 + 4, TT, 1); ctx.fillRect(x, y0 + 12, TT, 1);
    }
    B.stats.rects += (t1 - t0 + 1) * 6;
    dessinerPassages(ctx, cx, cy, y0);
  }

  const ID_TRI = 1e9 + 900;
  /** Les voitures AU SOL se trient avec les gens et les chars, par le bas de leur caisse. */
  function ajouterVisibles(visibles, cx, cy) {
    const d = donnees();
    if (!d || !enVille()) return;
    const e = etat(Autobus.tempsDeLaPartie());
    if (!e) return;
    const fin = d.tunnel * TT;
    voitures(e).forEach(function (w, k) {
      const m = (w.a + w.b) / 2;
      if (surLeViaduc(m) || w.a >= fin || w.b < cx - 40 || w.a > cx + VW + 40) return;
      if (d.yPx < cy - 40 || d.yPx > cy + VH + 40) return;
      const o = voitureAPeindre(k, w, e, 0);
      visibles.push({ id: ID_TRI, vivant: true, x: m, y: d.yPx + 8,
                      peindreFoire: function (ctx) { peindreVoiture(ctx, o, cx, cy, fin); } });
    });
  }

  /** En haut, par-dessus les gens et les chars : le viaduc (ses rampes, son tablier, ses piliers), les voitures
      qui y roulent, puis le portail du tunnel — qui avale tout ce qui est passé à l'est. */
  function dessinerHaut(ctx, vue) {
    const d = donnees();
    if (!d || !enVille()) return;
    const cx = Math.round(vue.x), cy = Math.round(vue.y), y0 = d.rang * TT - cy;
    if (y0 > VH + 60 || y0 < -60) return;
    const t0 = Math.max(d.viaduc[0], Math.floor(cx / TT)), t1 = Math.min(d.viaduc[1], Math.floor((cx + VW) / TT));
    for (let tx = t0; tx <= t1; tx++) {
      const x = tx * TT - cx, z = hauteur(tx * TT + TT / 2);
      const haut = y0 - 4 - z;
      ctx.fillStyle = '#6f6b64'; ctx.fillRect(x, haut + 24, TT, z);            // la face du tablier, ou le remblai
      ctx.fillStyle = '#9a968f'; ctx.fillRect(x, haut, TT, 24);                // la dalle
      ctx.fillStyle = '#4a4744'; ctx.fillRect(x, haut, TT, 2); ctx.fillRect(x, haut + 22, TT, 2);   // les garde-corps
      ctx.fillStyle = '#5b3f28';
      for (let k = 1; k < TT; k += 4) ctx.fillRect(x + k, y0 + 2 - z, 2, 12);
      ctx.fillStyle = '#c9ccd1'; ctx.fillRect(x, y0 + 3 - z, TT, 1); ctx.fillRect(x, y0 + 11 - z, TT, 1);
    }
    for (const p of d.piliers) {                                                  // le pied des piliers, sous la face
      if (p < t0 || p > t1) continue;
      ctx.fillStyle = '#5d5953'; ctx.fillRect(p * TT - cx + 3, y0 + 20, 10, 4);
    }
    B.stats.rects += (Math.max(0, t1 - t0 + 1)) * 9;
    const e = etat(Autobus.tempsDeLaPartie()), fin = d.tunnel * TT;
    if (e) {
      voitures(e).forEach(function (w, k) {
        const m = (w.a + w.b) / 2;
        if (surLeViaduc(m) && w.b >= cx - 40 && w.a <= cx + VW + 40) peindreVoiture(ctx, voitureAPeindre(k, w, e, hauteur(m)), cx, cy, fin);
      });
    }
    // Le portail : un arc de béton dans la falaise, et le noir du tunnel.
    const px = fin - cx;
    if (px > -40 && px < VW + 40) {
      ctx.fillStyle = '#8c8880'; ctx.fillRect(px - 6, y0 - 12, 14, TT + 24);
      ctx.fillStyle = '#6f6b64'; ctx.fillRect(px - 6, y0 - 12, 14, 3); ctx.fillRect(px - 6, y0 + TT + 9, 14, 3);
      ctx.fillStyle = '#121214'; ctx.fillRect(px - 2, y0 - 2, 10, TT + 4);
      B.stats.rects += 5;
    }
  }

  /** La grande carte : la voie pleine au sol, doublée sur le viaduc, en pointillé sous la montagne ; les gares
      en carrés sombres à cœur bordeaux, comme les stations du métro. */
  function dessinerSurLaCarte(ctx, pos) {
    const d = donnees();
    if (!d) return;
    const w = B.defs.carte.largeur;
    ctx.fillStyle = '#6e1a26';
    for (let tx = 0; tx < w; tx++) {
      const p = pos(tx * TT + TT / 2, d.yPx);
      if (tx >= d.tunnel) { if ((tx - d.tunnel) % 3 === 0) ctx.fillRect(p.x, p.y, 1, 1); }
      else if (tx >= d.viaduc[0] && tx <= d.viaduc[1]) { ctx.fillRect(p.x, p.y - 1, 1, 1); ctx.fillRect(p.x, p.y + 1, 1, 1); }
      else ctx.fillRect(p.x, p.y, 1, 1);
    }
    B.stats.rects += w;
    for (const g of d.gares) {
      const p = pos(g[1] * TT + TT / 2, d.yPx);
      ctx.fillStyle = '#101018'; ctx.fillRect(p.x - 2, p.y - 2, 5, 5);
      ctx.fillStyle = '#b8323f'; ctx.fillRect(p.x - 1, p.y - 1, 3, 3);
      B.stats.rects += 2;
    }
  }

  return { donnees: donnees, etat: etat, etendue: etendue, maj: maj, profil: profil,
           passageFerme: passageFerme, signalDevant: signalDevant, brisee: brisee, ligneHorsDeLaVoie: ligneHorsDeLaVoie, engage: engage,
           surLeViaduc: surLeViaduc, auSol: auSol, hauteur: hauteur,
           dessinerVoie: dessinerVoie, ajouterVisibles: ajouterVisibles, dessinerHaut: dessinerHaut,
           dessinerSurLaCarte: dessinerSurLaCarte };
})();
