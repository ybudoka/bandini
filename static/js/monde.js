/* Bandini — monde : la carte active, les collisions, la camera, l'heure.

   La carte vient du serveur (paquet `carte`) : lignes de glyphes + legende.
   Ici on en derive des tableaux types (solidite, route) et un cache de rendu
   par morceaux de 16x16 tuiles, peints une fois. */

const Monde = (function () {
  'use strict';

  const MORCEAU = 16;                 // tuiles par cote d'un morceau
  const MORCEAU_PX = MORCEAU * TT;
  // ⚠️ Le Faubourg fait 77 morceaux ; a 256x256 en RGBA, tout gardez-vous
  // coute 20 Mo de canevas — un telephone rend l'ame bien avant. On n'en garde
  // que le tour de l'ecran (9 visibles au pire), avec de la marge pour ne pas
  // repeindre a chaque pas de cote.
  const MORCEAUX_MAX = 24;
  const MUR = 1, EAU = 2, BASSE = 4;  // masques de collision
  const MASQUE_PIETON = MUR | EAU;
  const MASQUE_VEHICULE = MUR | EAU | BASSE;

  let carte = null;

  function charger(def) {
    const w = def.largeur, h = def.hauteur;
    const solide = new Uint8Array(w * h);
    const route = new Uint8Array(w * h);
    const passage = new Uint8Array(w * h);     // passage pieton : route ET trottoir
    const portesFermees = [];                   // les « d » : par ou les gens rentrent chez eux
    for (let y = 0; y < h; y++) {
      const ligne = def.sol[y];
      for (let x = 0; x < w; x++) {
        const p = def.legende[ligne[x]] || {};
        solide[y * w + x] = p.solide || 0;
        route[y * w + x] = p.route ? 1 : 0;
        passage[y * w + x] = (p.route && p.trottoir) ? 1 : 0;
        if (ligne[x] === 'd' || ligne[x] === 'D') portesFermees.push({ x: x, y: y });
      }
    }
    const portes = new Map();
    (def.portes || []).forEach(function (p) { portes.set(p.x + ',' + p.y, p); });
    // Chaque tuile de croisement connait son croisement : un char a la ligne
    // d'arret demande a QUEL feu il obeit.
    // ⚠️ La boite inclut les PASSAGES PIETONS (deux tuiles de chaque cote) :
    // un pieton au bord du passage demande, lui aussi, a quel feu il obeit.
    const croisements = new Map();
    (def.intersections || []).forEach(function (inter, i) {
      inter.i = i;
      inter.decalage = hash2(inter.x, inter.y) % 600;
      inter.feux = inter.bras.length >= 4;
      // Un T : la rue qui s'arrete (la tige) a un STOP. Son approche est le
      // sens qui va de la tige vers le croisement.
      inter.stop = null;
      if (inter.bras.length === 3) {
        const manquant = 'NSOE'.split('').find(function (b) { return inter.bras.indexOf(b) < 0; });
        inter.stop = { N: '^', S: 'v', O: '<', E: '>' }[manquant];   // bras manquant N → la tige est S → on arrive en montant
      }
      for (let y = inter.y - 2; y < inter.y + inter.h + 2; y++) {
        for (let x = inter.x - 2; x < inter.x + inter.l + 2; x++) croisements.set(x + ',' + y, inter);
      }
    });
    carte = {
      def: def, w: w, h: h, sol: def.sol, voie: def.voie, legende: def.legende,
      solide: solide, route: route, passage: passage, portesFermees: portesFermees,
      morceaux: new Map(), visibles: new Set(),
      portesParTuile: portes, mini: null, croisements: croisements, arrets: def.arrets || {},
      intersections: def.intersections || [],
      lampes: (def.lampes || []).map(function (l) { return { x: l.x * TT + 8, y: l.y * TT + 2, r: 44, c: 'rgba(255,214,130,0.55)' }; }),
      portes: def.portes || [],
      points: def.points_interet || [],
      zones: def.zones || [],
      apparition: def.apparition,
      pxW: w * TT, pxH: h * TT,
    };
    B.carte = carte;
    return carte;
  }

  function glyphe(tx, ty) {
    if (!carte || tx < 0 || ty < 0 || tx >= carte.w || ty >= carte.h) return 'B';
    return carte.sol[ty][tx];
  }
  function solidite(tx, ty) {
    if (!carte || tx < 0 || ty < 0 || tx >= carte.w || ty >= carte.h) return 1;
    return carte.solide[ty * carte.w + tx];
  }
  function bloque(tx, ty, masque) {
    const s = solidite(tx, ty);
    if (s === 1) return (masque & MUR) !== 0;
    if (s === 2) return (masque & EAU) !== 0;
    if (s === 3) return (masque & BASSE) !== 0;
    return false;
  }
  function estRoute(tx, ty) {
    if (!carte || tx < 0 || ty < 0 || tx >= carte.w || ty >= carte.h) return false;
    return carte.route[ty * carte.w + tx] === 1;
  }
  function estPassage(tx, ty) {
    if (!carte || tx < 0 || ty < 0 || tx >= carte.w || ty >= carte.h) return false;
    return carte.passage[ty * carte.w + tx] === 1;
  }
  /** La chaussee nue : la ou un pieton n'a rien a faire. */
  function estChaussee(tx, ty) { return estRoute(tx, ty) && !estPassage(tx, ty); }
  /** Une tuile qu'un pieton peut fouler en flanant : ni mur, ni eau, ni chaussee. */
  function marchablePieton(tx, ty) { return !bloque(tx, ty, MASQUE_PIETON) && !estChaussee(tx, ty); }

  /** Ligne de vue entre deux points (pixels) : rien de MUR entre les deux. */
  function ligneLibre(x0, y0, x1, y1) {
    let tx = Math.floor(x0 / TT), ty = Math.floor(y0 / TT);
    const fx = Math.floor(x1 / TT), fy = Math.floor(y1 / TT);
    const dx = Math.abs(fx - tx), dy = Math.abs(fy - ty);
    const sx = tx < fx ? 1 : -1, sy = ty < fy ? 1 : -1;
    let err = dx - dy, n = dx + dy + 1;
    while (n-- > 0) {
      if (solidite(tx, ty) === 1) return false;
      if (tx === fx && ty === fy) return true;
      const e2 = err * 2;
      if (e2 > -dy) { err -= dy; tx += sx; }
      if (e2 < dx) { err += dx; ty += sy; }
    }
    return true;
  }

  /** Une porte a cette tuile ? (index : on interroge a chaque image) */
  function porteA(tx, ty) {
    return carte.portesParTuile.get(tx + ',' + ty) || null;
  }

  function fleche(tx, ty) {
    if (!carte || tx < 0 || ty < 0 || tx >= carte.w || ty >= carte.h) return '.';
    return carte.voie[ty][tx];
  }

  /** Le sens d'une ligne d'arret ('>' '<' '^' 'v'), ou null. */
  function sensArret(tx, ty) { return carte.arrets[tx + ',' + ty] || null; }

  function intersectionA(tx, ty) { return carte.croisements.get(tx + ',' + ty) || null; }

  /** Le feu est-il vert pour qui roule dans ce sens vers ce croisement ?
      ⚠️ Un croisement en T ou en L n'a pas de feu : on y passe a vue. */
  function feuVert(inter, sens) {
    if (!inter || !inter.feux) return true;
    const t = B.defs.conduite.trafic;
    const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
    const phase = (B.t + inter.decalage) % cycle;
    const nordSud = sens === '^' || sens === 'v';
    const moitie = phase < cycle / 2;
    // Premiere moitie : nord-sud roule. L'orange ferme la fin de chaque moitie.
    const dansMoitie = moitie ? phase : phase - cycle / 2;
    if (dansMoitie >= t.feu_vert_images) return false;
    return nordSud === moitie;
  }

  function estRampe(tx, ty) {
    const p = carte && carte.legende[glyphe(tx, ty)];
    return !!(p && p.rampe);
  }

  /** La zone nommee qui contient ce point (la derniere gagne : la plus precise). */
  function zoneA(x, y) {
    let trouvee = null;
    for (const z of carte.zones) {
      if (x >= z.x * TT && x < (z.x + z.l) * TT && y >= z.y * TT && y < (z.y + z.h) * TT) trouvee = z;
    }
    return trouvee;
  }

  // --- Rendu du sol ---------------------------------------------------------------

  function peindreMorceau(mx, my) {
    const c = Base.nouveauCanvas(MORCEAU_PX, MORCEAU_PX);
    const ctx = c.getContext('2d');
    for (let j = 0; j < MORCEAU; j++) {
      for (let i = 0; i < MORCEAU; i++) {
        const tx = mx * MORCEAU + i, ty = my * MORCEAU + j;
        if (tx >= carte.w || ty >= carte.h) continue;
        const g = carte.sol[ty][tx];
        const peintre = TUILES[g] || TUILES[','];
        const tuile = Atlas.cuireTuile(g, hash2(tx, ty) % 4, peintre);
        ctx.drawImage(tuile, i * TT, j * TT);
      }
    }
    return c;
  }

  function dessinerSol(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    const m0x = Math.floor(cx / MORCEAU_PX), m0y = Math.floor(cy / MORCEAU_PX);
    const m1x = Math.floor((cx + VW - 1) / MORCEAU_PX), m1y = Math.floor((cy + VH - 1) / MORCEAU_PX);
    carte.visibles.clear();
    for (let my = m0y; my <= m1y; my++) {
      for (let mx = m0x; mx <= m1x; mx++) {
        if (mx < 0 || my < 0 || mx * MORCEAU >= carte.w || my * MORCEAU >= carte.h) continue;
        const cle = mx + ',' + my;
        let m = carte.morceaux.get(cle);
        if (m) carte.morceaux.delete(cle);          // re-insere = le plus frais
        else m = peindreMorceau(mx, my);
        carte.morceaux.set(cle, m);
        carte.visibles.add(cle);
        ctx.drawImage(m, mx * MORCEAU_PX - cx, my * MORCEAU_PX - cy);
        B.stats.images++;
      }
    }
    oublierLesVieuxMorceaux();
    B.stats.morceaux = carte.morceaux.size;
  }

  /** Jette les morceaux les plus anciens, jamais un morceau a l'ecran. */
  function oublierLesVieuxMorceaux() {
    if (carte.morceaux.size <= MORCEAUX_MAX) return;
    for (const cle of carte.morceaux.keys()) {
      if (carte.morceaux.size <= MORCEAUX_MAX) break;
      if (!carte.visibles.has(cle)) carte.morceaux.delete(cle);
    }
  }

  // --- Mini-carte -----------------------------------------------------------------

  /** Une couleur par FAMILLE de tuile, lue dans la legende : un glyphe ajoute
      demain apparait tout seul sur la mini-carte. */
  function couleurMini(glyphe) {
    const p = carte.legende[glyphe] || {};
    if (p.solide === 2) return '#24506f';
    if (p.solide === 1) return '#4a3f3f';
    if (p.route) return '#34373d';
    if (p.trottoir) return '#8a877c';
    if (p.herbe) return '#3f6b33';
    if (p.ruelle) return '#4a4741';
    return '#6b5a3a';
  }

  /** La ville entiere, une tuile = un pixel. Cuite une fois : 18 000 rectangles
      au chargement valent mieux que 64x48 relus a chaque image. */
  function miniCarte() {
    if (carte.mini) return carte.mini;
    const c = Base.nouveauCanvas(carte.w, carte.h);
    const ctx = c.getContext('2d');
    for (let y = 0; y < carte.h; y++) {
      const ligne = carte.sol[y];
      let debut = 0, couleur = couleurMini(ligne[0]);
      for (let x = 1; x <= carte.w; x++) {
        const suivante = x < carte.w ? couleurMini(ligne[x]) : null;
        if (suivante !== couleur) {
          ctx.fillStyle = couleur;
          ctx.fillRect(debut, y, x - debut, 1);
          debut = x; couleur = suivante;
        }
      }
    }
    carte.mini = c;
    return c;
  }

  // --- Camera ---------------------------------------------------------------------

  function centrerCamera(x, y) {
    B.cam.x = borner(x - VW / 2, 0, Math.max(0, carte.pxW - VW));
    B.cam.y = borner(y - VH / 2, 0, Math.max(0, carte.pxH - VH));
  }

  function majCamera() {
    const j = B.joueur;
    if (!j) return;
    let avanceX = 0, avanceY = 0;
    if (j.dansVehicule) {
      const v = j.dansVehicule, f = Math.min(1, Math.abs(v.vitesse || 0) / 4);
      avanceX = Math.cos(v.angle) * 48 * f; avanceY = Math.sin(v.angle) * 48 * f;
    } else { avanceX = j.vx * 14; avanceY = j.vy * 14; }
    const cibleX = borner(j.x + avanceX - VW / 2, 0, Math.max(0, carte.pxW - VW));
    const cibleY = borner(j.y + avanceY - VH / 2, 0, Math.max(0, carte.pxH - VH));
    B.cam.x += (cibleX - B.cam.x) * 0.12;
    B.cam.y += (cibleY - B.cam.y) * 0.12;
    if (B.cam.secousse > 0) B.cam.secousse *= 0.9;
  }

  // --- Heure et ambiance ---------------------------------------------------------------

  //: [heure 0..1, teinte, alpha]. 0 = minuit, 0.5 = midi.
  const TEINTES = [
    [0.00, [26, 32, 80], 0.72], [0.22, [26, 32, 80], 0.66], [0.30, [255, 150, 90], 0.22],
    [0.38, [255, 255, 255], 0.0], [0.72, [255, 255, 255], 0.0], [0.80, [255, 130, 70], 0.28],
    [0.88, [40, 40, 100], 0.62], [1.00, [26, 32, 80], 0.72],
  ];

  function majHeure() {
    const p = B.partie;
    if (!p || !B.defs) return;
    const parImage = 1 / (B.defs.economie.jour_secondes * 60);
    p.heure += parImage;
    if (p.heure >= 1) { p.heure -= 1; p.jour += 1; if (typeof Missions !== 'undefined' && Missions.nouveauJour) Missions.nouveauJour(); }
  }

  function ambiance(heure) {
    const h = heure === undefined ? (B.partie ? B.partie.heure : 0.5) : heure;
    let a = TEINTES[0], b = TEINTES[TEINTES.length - 1];
    for (let i = 0; i < TEINTES.length - 1; i++) {
      if (h >= TEINTES[i][0] && h <= TEINTES[i + 1][0]) { a = TEINTES[i]; b = TEINTES[i + 1]; break; }
    }
    const t = b[0] === a[0] ? 0 : (h - a[0]) / (b[0] - a[0]);
    const r = Math.round(lerp(a[1][0], b[1][0], t)), g = Math.round(lerp(a[1][1], b[1][1], t)), bl = Math.round(lerp(a[1][2], b[1][2], t));
    return { teinte: 'rgb(' + r + ',' + g + ',' + bl + ')', alpha: lerp(a[2], b[2], t) };
  }

  function estNuit() { return ambiance().alpha > 0.4; }

  function heureTexte() {
    const h = B.partie ? B.partie.heure : 0.5;
    const minutes = Math.floor(h * 24 * 60);
    const hh = Math.floor(minutes / 60), mm = minutes % 60;
    return (hh < 10 ? '0' : '') + hh + ':' + (mm < 10 ? '0' : '') + mm;
  }

  function lampesVisibles(cam) {
    // Les lampadaires n'eclairent qu'a la brune : en plein jour, rien.
    if (!carte || ambiance().alpha < 0.2) return [];
    const out = [];
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const l of carte.lampes) {
      if (l.x < cx - l.r || l.x > cx + VW + l.r || l.y < cy - l.r || l.y > cy + VH + l.r) continue;
      out.push({ x: l.x - cx, y: l.y - cy, r: l.r, c: l.c });
      if (out.length >= 25) break;
    }
    return out;
  }

  return {
    MUR, EAU, BASSE, MASQUE_PIETON, MASQUE_VEHICULE, MORCEAUX_MAX,
    charger, glyphe, solidite, bloque, estRoute, estPassage, estChaussee, marchablePieton,
    ligneLibre, porteA, zoneA, fleche, sensArret, intersectionA, feuVert, estRampe,
    dessinerSol, centrerCamera, majCamera, majHeure, ambiance, estNuit, heureTexte, lampesVisibles,
    miniCarte, couleurMini,
    get carte() { return carte; },
  };
})();
