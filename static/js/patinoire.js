/* Bandini — la patinoire du parc (docs/jalons/la-patinoire-du-parc.md).

   L'hiver, tant que la neige tient (`Saisons.enHiver`), le parc du Faubourg a sa patinoire a bandes : la
   glace, des bandes blanches a liseret rouge, deux filets, et quatre lampadaires qui s'allument le soir.
   L'ete, sa clairiere n'est que du gazon. Sa PLACE vient de Python (`app/patinoire.py`, dans la carte :
   `B.defs.carte.patinoire`, en tuiles) ; ses couleurs, sa glisse et sa chute de sa fiche (`B.defs.patinoire`).

   ⚠️ TOUT EST PEINT, RIEN N'EST POSE : aucune tuile, aucun decor, aucun identifiant, aucun de. Mais les
   bandes sont SOLIDES l'hiver, comme les Tempo (`RueDesSaisons`) : un char n'entre pas (`bloqueChar`, lu
   par `Monde.barriereBloque`), un pieton passe par les portes (`bloquer`, lu par `Entites.bloquerParDecor`).

   ⚠️ LA GLISSE : sur la glace, la vitesse que veulent les commandes (ou la tete d'un passant) ne se prend
   pas d'un coup — elle se rejoint peu a peu (`glisser`, appele par `Entites` une fois la vitesse voulue
   calculee). D'ou l'elan, le virage large, l'arret qui prend du temps. Et le joueur qui court sans patins,
   ou qui vire sec lance, TOMBE (`auSol`) — sans un de.

   LES PATINS A LOUER (vague 3) : au guichet du kiosque de Madame Thibodeau, qui ouvre sur la glace
   (`p.guichet`). ACTION, deux piastres, on les chausse (`j.patins`) ; on va plus vite, MAIS on glisse toujours
   — un elan plus franc, un arret plus long (Martin : « patin, mais on doit glisser aussi »). On les rend en
   quittant la glace. */

const Patinoire = (function () {
  'use strict';

  const T = 16;
  //: L'epaisseur d'une bande, en px, et son retrait dans la tuile du bord.
  const BANDE = 3, RETRAIT = 2;

  function fiche() { return B.defs && B.defs.patinoire; }
  function lieu() { return B.defs && B.defs.carte && B.defs.carte.patinoire; }

  /** La patinoire en px, et ses bandes (des boites { x, y, l, h } en demi-tailles), calculees une fois par
      lieu : la carte ne bouge pas. */
  let calcul = null, deQui = null;
  function geo() {
    const p = lieu();
    if (!p) return null;
    if (calcul && deQui === p) return calcul;
    const x0 = p.x * T + RETRAIT, y0 = p.y * T + RETRAIT;
    const x1 = (p.x + p.l) * T - RETRAIT, y1 = (p.y + p.h) * T - RETRAIT;
    const portes = p.portes || [];
    const bandes = [];
    // Une bande par cote, coupee a chaque porte : l'ouverture fait la tuile de la porte.
    const cote = function (nom, horizontale, fixe, a, b) {
      const trous = portes.filter(function (q) { return q.cote === nom; })
        .map(function (q) { return horizontale ? [q.x * T, (q.x + 1) * T] : [q.y * T, (q.y + 1) * T]; })
        .sort(function (u, w) { return u[0] - w[0]; });
      let debut = a;
      trous.concat([[b, b]]).forEach(function (t) {
        const fin = Math.min(b, t[0]);
        if (fin - debut > 0.5) {
          const m = (debut + fin) / 2, demi = (fin - debut) / 2;
          bandes.push(horizontale ? { x: m, y: fixe, l: demi, h: BANDE / 2, cote: nom }
                                  : { x: fixe, y: m, l: BANDE / 2, h: demi, cote: nom });
        }
        debut = Math.max(debut, t[1]);
      });
    };
    cote('nord', true, y0 + BANDE / 2, x0, x1);
    cote('sud', true, y1 - BANDE / 2, x0, x1);
    cote('ouest', false, x0 + BANDE / 2, y0, y1);
    cote('est', false, x1 - BANDE / 2, y0, y1);
    calcul = { p: p, x0: x0, y0: y0, x1: x1, y1: y1, bandes: bandes, portes: portes };
    deQui = p;
    return calcul;
  }

  /** Dehors, dans la ville, et la neige tient : la glace est la. */
  function ouverte() {
    const c = Monde.carte;
    // ⚠️ `fiche()` : elle voyage dans la SUITE du paquet (`/api/suite`), qui arrive juste apres la ville.
    return !!(c && c.laVille && !B.interieur && !B.bloc && fiche() && typeof Saisons !== 'undefined' && Saisons.enHiver() && geo());
  }

  /** Ce point (px) est-il SUR la glace (en dedans des bandes) ? */
  function surLaGlace(x, y) {
    if (!ouverte()) return false;
    const g = geo();
    return x > g.x0 + BANDE && x < g.x1 - BANDE && y > g.y0 + BANDE && y < g.y1 - BANDE;
  }

  // ------------------------------------------------------------------ les bandes, solides

  /** Un pieton ou le joueur a pied qui entre dans une bande en ressort par le cote le moins enfonce ; son
      elan contre la bande s'arrete (on ne glisse pas a travers). Appele par `Entites.bloquerParDecor`. */
  function bloquer(e) {
    if (!e || (e.type !== 'pieton' && e.type !== 'joueur') || e.dansVehicule || !ouverte()) return;
    const g = geo();
    if (e.x < g.x0 - e.r - 2 || e.x > g.x1 + e.r + 2 || e.y < g.y0 - e.r - 2 || e.y > g.y1 + e.r + 2) return;
    for (const b of g.bandes) {
      const dx = e.x - b.x, dy = e.y - b.y;
      const px = b.l + e.r - Math.abs(dx), py = b.h + e.r - Math.abs(dy);
      if (px <= 0 || py <= 0) continue;
      if (px < py) { e.x = b.x + (dx < 0 ? -1 : 1) * (b.l + e.r + 0.01); e.gx = 0; }
      else { e.y = b.y + (dy < 0 ? -1 : 1) * (b.h + e.r + 0.01); e.gy = 0; }
    }
  }

  /** Les tuiles de la porte de service (`service`), et celles juste dehors : la seule entree des chars. */
  let services = null, servicesDe = null;
  function serviceDe(p) {
    if (services && servicesDe === p) return services;
    const pas = { nord: [0, -1], sud: [0, 1], ouest: [-1, 0], est: [1, 0] };
    const dedans = new Set(), dehors = new Set();
    (p.portes || []).forEach(function (q) {
      if (!q.service) return;
      const o = pas[q.cote];
      dedans.add(q.x + ',' + q.y); dehors.add((q.x + o[0]) + ',' + (q.y + o[1]));
    });
    servicesDe = p;
    return (services = { dedans: dedans, dehors: dehors });
  }

  /** Un char `v` peut-il entrer sur la tuile (tx, ty) ? L'hiver, les bandes l'arretent : il n'entre sur la glace
      que par la porte de service (la surfaceuse, deuxieme vague), et n'en ressort que par elle. Appele par
      `Monde.barriereBloque`. */
  function bloqueChar(v, tx, ty) {
    if (!v || v.type !== 'vehicule') return false;
    const p = lieu();
    if (!p || !ouverte()) return false;
    const dans = function (x, y) { return x >= p.x && x < p.x + p.l && y >= p.y && y < p.y + p.h; };
    const vx = Math.floor(v.x / T), vy = Math.floor(v.y / T), cible = dans(tx, ty), lui = dans(vx, vy);
    if (cible === lui) return false;
    const s = serviceDe(p);
    // Il entre : seulement sur la porte de service. Il sort : seulement par elle (sa tuile, ou celle d'en face).
    if (cible) return !s.dedans.has(tx + ',' + ty);
    return !(s.dehors.has(tx + ',' + ty) || s.dedans.has(vx + ',' + vy));
  }

  /** Ce que la glace laisse d'adherence a un char (et de frein) : lu par `Vehicules`, comme la neige et le verglas. */
  function adherence(v) {
    const f = fiche();
    return f && f.chars && v && surLaGlace(v.x, v.y) ? f.chars.adherence : 1;
  }
  function frein(v) {
    const f = fiche();
    return f && f.chars && v && surLaGlace(v.x, v.y) ? f.chars.frein : 1;
  }

  // ------------------------------------------------------------------ la glisse, et la chute

  function tomber(j, f) {
    j.auSol = f.images_au_sol; j.face = 'couche';
    j.vx = 0; j.vy = 0; j.gx = 0; j.gy = 0; j.courseSurGlace = 0;
    if (typeof Son !== 'undefined' && Son.SFX && Son.SFX.chute) Son.SFX.chute();
  }

  /** Sur la glace, la vitesse voulue (`e.vx`, `e.vy`, deja calculee) se rejoint peu a peu depuis celle de
      l'image d'avant (`e.gx`, `e.gy`). `court` : le joueur tient ESQUIVE en poussant. Rend vrai si le joueur
      vient de tomber (il ne bouge plus cette image-ci). Hors de la glace, on retient seulement la vitesse :
      on y entre avec son elan. */
  function glisser(e, court) {
    const f = fiche();
    const suite = e.gt === B.t - 1;
    e.gt = B.t;
    if (!f || !surLaGlace(e.x, e.y)) {
      e.gx = e.vx; e.gy = e.vy; e.courseSurGlace = 0;
      if (e.patins) rendre(e);
      return false;
    }
    // En patins, la vitesse voulue grandit, et la glisse est la leur.
    const patins = e.type === 'joueur' && e.patins && f.patins;
    const g = patins ? f.patins.glisse : f.glisse[e.type === 'joueur' ? 'joueur' : 'pieton'];
    if (patins) { e.vx *= f.patins.vitesse; e.vy *= f.patins.vitesse; }
    // ⚠️ Une suite rompue (la premiere image, un retour anticipe d'`Entites` qui a remis la vitesse a zero) repart
    // de l'ARRET, jamais de la vitesse voulue : sinon on demarre sur la glace aussi vite qu'au sec.
    const avx = suite ? (e.gx || 0) : 0, avy = suite ? (e.gy || 0) : 0;
    const pousse = Math.abs(e.vx) + Math.abs(e.vy) > 0.01;
    if (e.type === 'joueur') {
      const c = f.chute, va = Math.hypot(avx, avy), vv = Math.hypot(e.vx, e.vy);
      e.courseSurGlace = court && !patins ? (e.courseSurGlace || 0) + 1 : 0;
      let virage = 0;
      if (pousse && va > 0.01 && vv > 0.01) {
        const cos = (avx * e.vx + avy * e.vy) / (va * vv);
        virage = Math.acos(Math.max(-1, Math.min(1, cos))) * 180 / Math.PI;
      }
      if (e.courseSurGlace > c.images_de_course || (virage > c.virage_deg && va > c.vitesse_de_virage)) {
        tomber(e, c);
        return true;
      }
    }
    const k = pousse ? g.elan : g.freinage;
    e.vx = avx + (e.vx - avx) * k;
    e.vy = avy + (e.vy - avy) * k;
    e.gx = e.vx; e.gy = e.vy;
    return false;
  }

  // ------------------------------------------------------------------ la peinture

  /** La glace, les bandes, les filets et les lampadaires, sous les gens. Rien l'ete. */
  function dessinerSol(ctx, vue) {
    if (!ouverte()) return;
    const g = geo(), c = fiche().couleurs;
    const X = function (x) { return Math.round(x - vue.x); }, Y = function (y) { return Math.round(y - vue.y); };
    if (X(g.x1) < -24 || X(g.x0) > VW + 24 || Y(g.y1) < -24 || Y(g.y0) > VH + 24) return;
    const l = g.x1 - g.x0, h = g.y1 - g.y0;
    let n = 0;
    // La glace, et ses rayures de lames : a l'empreinte de la patinoire, jamais un de.
    ctx.fillStyle = c.glace; ctx.fillRect(X(g.x0), Y(g.y0), l, h); n++;
    ctx.fillStyle = c.rayure;
    for (let k = 0; k < 18; k++) {
      const hh = hash2(g.p.x * 31 + k, g.p.y * 17 + k) >>> 0;
      const rx = g.x0 + 6 + (hh % Math.max(1, l - 30)), ry = g.y0 + 6 + ((hh >>> 8) % Math.max(1, h - 12));
      ctx.fillRect(X(rx), Y(ry), 8 + ((hh >>> 16) % 14), 1); n++;
    }
    ctx.fillStyle = c.reflet;
    ctx.fillRect(X(g.x0 + 10), Y(g.y0 + 6), Math.round(l * 0.3), 1); ctx.fillRect(X(g.x0 + l * 0.55), Y(g.y1 - 9), Math.round(l * 0.25), 1); n += 2;
    // La ligne rouge du centre.
    ctx.fillStyle = c.liseret; ctx.globalAlpha = 0.45;
    ctx.fillRect(X(g.x0 + l / 2) - 1, Y(g.y0 + BANDE), 2, h - 2 * BANDE); n++;
    ctx.globalAlpha = 1;
    // Les filets, au milieu des petits cotes.
    const my = (g.y0 + g.y1) / 2, FILET = 7;
    [[g.x0 + BANDE + 6, -1], [g.x1 - BANDE - 6, 1]].forEach(function (f) {
      ctx.fillStyle = c.filet; ctx.fillRect(X(f[0]) + (f[1] > 0 ? 0 : -3), Y(my - FILET), 3, FILET * 2);
      ctx.fillStyle = c.poteau; ctx.fillRect(X(f[0]) - 1, Y(my - FILET) - 1, 2, 2); ctx.fillRect(X(f[0]) - 1, Y(my + FILET) - 1, 2, 2);
      n += 3;
    });
    // Les bandes : une ombre sous chacune, le blanc, le liseret rouge en haut.
    for (const b of g.bandes) {
      const bx = X(b.x - b.l), by = Y(b.y - b.h), bl = Math.round(b.l * 2), bh = Math.round(b.h * 2);
      ctx.fillStyle = c.ombre; ctx.fillRect(bx, by + 1, bl, bh);
      ctx.fillStyle = c.bande; ctx.fillRect(bx, by, bl, bh);
      ctx.fillStyle = c.liseret;
      if (b.cote === 'nord' || b.cote === 'sud') ctx.fillRect(bx, by, bl, 1); else ctx.fillRect(bx + (b.cote === 'ouest' ? 0 : bl - 1), by, 1, bh);
      n += 3;
    }
    // Le guichet des patins : un volet de bois sur la bande, et l'enseigne au-dessus.
    const q = guichet(), pc = fiche().patins && fiche().patins.couleurs;
    if (q && pc) {
      const horiz = q.cote === 'nord' || q.cote === 'sud';
      const gx = X(q.x) - (horiz ? 6 : 2), gy = Y(q.y) - (horiz ? 2 : 6);
      ctx.fillStyle = pc.guichet; ctx.fillRect(gx, gy, horiz ? 12 : 4, horiz ? 4 : 12);
      ctx.fillStyle = pc.enseigne; ctx.fillRect(X(q.x) - 5, Y(q.y) - 12, 10, 5);
      ctx.fillStyle = pc.texte; ctx.fillRect(X(q.x) - 4, Y(q.y) - 10, 3, 1); ctx.fillRect(X(q.x) + 1, Y(q.y) - 10, 3, 1);
      n += 4;
    }
    // Les lampadaires des quatre coins.
    for (const q of coins(g)) {
      ctx.fillStyle = c.lampe; ctx.fillRect(X(q[0]) - 1, Y(q[1]) - 9, 2, 10); ctx.fillRect(X(q[0]) - 2, Y(q[1]) - 10, 4, 2);
      n += 2;
    }
    B.stats.rects += n;
  }

  function coins(g) { return [[g.x0 - 3, g.y0 - 2], [g.x1 + 3, g.y0 - 2], [g.x0 - 3, g.y1 + 2], [g.x1 + 3, g.y1 + 2]]; }

  /** La lueur des lampadaires, le soir. */
  function lampes(vue) {
    if (!ouverte() || Monde.ambianceVue().alpha <= 0.2) return [];
    const g = geo(), f = fiche().lampes, coul = 'rgba(' + f.lueur.join(',') + ',' + f.force + ')', out = [];
    for (const q of coins(g)) {
      const x = q[0] - vue.x, y = q[1] - 9 - vue.y;
      if (x < -f.rayon || y < -f.rayon || x > VW + f.rayon || y > VH + f.rayon) continue;
      out.push({ x: x, y: y, r: f.rayon, c: coul });
    }
    return out;
  }

  // ------------------------------------------------------------------ les patineurs (vague 2)

  //: Les patineurs en cours : de vrais passants (`Entites.creerPieton`), marques `patineur`.
  let patineurs = [];

  /** Combien de patineurs a cette heure (0 a 1 de la journee) : 0 hors des heures d'ouverture. */
  function voulus(heure) {
    const f = fiche(), h = heure * 24;
    if (!f || !f.patineurs) return 0;
    for (const n of f.patineurs.nombre) if (h >= n[0] && h < n[1]) return n[2];
    return 0;
  }

  /** La patinoire (et ses lampadaires) touche-t-elle l'ecran, a `marge` pres ? */
  function aLEcran(g, marge) {
    const m = marge || 0;
    return g.x1 > B.cam.x - m && g.x0 < B.cam.x + VW + m && g.y1 > B.cam.y - m && g.y0 < B.cam.y + VH + m;
  }

  /** L'anneau d'un patineur : le centre de la glace, et ses deux rayons, rentres de son couloir. */
  function anneau(g, e) {
    const d = fiche().patineurs, couloir = (hash2(e.id, 0x9a71) >>> 0) % d.couloirs;
    const rentre = d.marge_px + BANDE + couloir * d.couloirs_px;
    return { cx: (g.x0 + g.x1) / 2, cy: (g.y0 + g.y1) / 2,
             rx: Math.max(8, (g.x1 - g.x0) / 2 - rentre), ry: Math.max(6, (g.y1 - g.y0) / 2 - rentre) };
  }

  /** Le cap d'un patineur : un peu plus loin sur son anneau, a contre-sens des aiguilles d'une montre (l'angle
      DECROIT : y descend a l'ecran). */
  function viser(g, e) {
    const a = anneau(g, e), d = fiche().patineurs;
    const t = Math.atan2((e.y - a.cy) / a.ry, (e.x - a.cx) / a.rx) - d.avance_rad;
    e.etat = 'cap'; e.cap = { x: a.cx + Math.cos(t) * a.rx, y: a.cy + Math.sin(t) * a.ry }; e.capT = 0; e.capVite = false;
  }

  /** Qu'ils naissent sur la glace, repartis sur leurs anneaux ; un enfant sur `un_enfant_sur`, par le rang. ⚠️ Pas
      un seuil sur `hash2` : ses petites entrees consecutives se repartissent mal (aucune sous 0,35 de 0 a 9). */
  function faireNaitre(g, n) {
    const d = fiche().patineurs, enfant = Entites.archetype('enfant');
    for (let k = 0; k < n; k++) {
      const rang = patineurs.length, t = rang * 2.39996;               // l'angle d'or : un anneau bien reparti
      const petit = rang % d.un_enfant_sur === 1;
      const cx = (g.x0 + g.x1) / 2, cy = (g.y0 + g.y1) / 2;
      const rx = (g.x1 - g.x0) / 2 - d.marge_px - BANDE, ry = (g.y1 - g.y0) / 2 - d.marge_px - BANDE;
      const e = Entites.creerPieton(cx + Math.cos(t) * rx * 0.8, cy + Math.sin(t) * ry * 0.8, petit ? enfant : undefined);
      e.patineur = true;
      patineurs.push(e);
      viser(g, e);
    }
    Entites.indexer();
  }

  /** Toutes les 15 images : ils tournent ; ils naissent quand la glace est hors de l'ecran et que le joueur
      approche ; ils repartent, HORS DE L'ECRAN, a la fermeture ou quand le joueur s'eloigne. Un patineur
      qu'on a bouscule (il fuit, il est assomme) n'est plus mene : c'est un passant comme un autre. */
  function maj() {
    const f = fiche();
    if (!f || !f.patineurs || !B.partie || !B.joueur) return;
    patineurs = patineurs.filter(function (e) { return e.vivant && B.entites.indexOf(e) >= 0 && e.patineur; });
    if (B.t % 15 !== 0 || B.interieur || B.bloc || !Monde.carte || !Monde.carte.laVille) return;
    const g = geo();
    if (!g) return;
    const d = f.patineurs, j = B.joueur, ouvert = ouverte();
    const proche = Math.hypot(j.x - (g.x0 + g.x1) / 2, j.y - (g.y0 + g.y1) / 2) <= d.portee_px;
    const voulu = ouvert && proche ? voulus(B.partie.heure) : 0;
    const chute = B.t % 60 === 0;
    for (const e of patineurs) {
      if (e.etat !== 'cap' && e.etat !== 'flane' && e.etat !== 'arret') { e.patineur = false; continue; }
      if (!surLaGlace(e.x, e.y)) { if (e.etat !== 'arret') viser(g, e); continue; }
      if (e.etat === 'arret') continue;                // il se releve (`Entites` le remet a flaner)
      // Un enfant tombe parfois, lance : a l'empreinte de la seconde, jamais un de.
      if (chute && e.arch === 'enfant' && Math.hypot(e.vx, e.vy) > 0.3
          && (hash2(e.id, Math.floor(B.t / 60)) >>> 0) % d.chute_une_sur === 0) {
        e.etat = 'arret'; e.minuterie = d.images_de_chute; e.face = 'couche'; e.vx = 0; e.vy = 0; e.gx = 0; e.gy = 0;
        continue;
      }
      viser(g, e);
    }
    patineurs = patineurs.filter(function (e) { return e.patineur; });
    const vue = aLEcran(g, 40);
    if (patineurs.length > voulu && !vue) {
      for (const e of patineurs.splice(voulu)) Entites.retirer(e);
    }
    if (patineurs.length < voulu && !vue) faireNaitre(g, voulu - patineurs.length);
  }

  /** Les lames sous les pieds des patineurs : un trait clair, sous le corps. */
  function dessinerLames(ctx, vue) {
    const j = B.joueur, lui = j && j.patins && !j.dansVehicule ? [j] : [];
    if ((!patineurs.length && !lui.length) || !ouverte()) return;
    ctx.fillStyle = fiche().patineurs.lame;
    for (const e of patineurs.concat(lui)) {
      if (e.face === 'couche' || !e.vivant) continue;
      const x = Math.round(e.x - vue.x), y = Math.round(e.y - vue.y);
      if (x < -8 || y < -8 || x > VW + 8 || y > VH + 8) continue;
      ctx.fillRect(x - 3, y + 1, 3, 1); ctx.fillRect(x + 1, y + 1, 3, 1);
      B.stats.rects += 2;
    }
  }

  // ------------------------------------------------------------------ les patins a louer (vague 3)

  /** Le guichet, en px : au milieu du cote de sa tuile qui touche la bande (le mur du kiosque). */
  function guichet() {
    const g = geo(), q = g && g.p.guichet;
    if (!q) return null;
    const o = { est: [T / 2 - RETRAIT, 0], ouest: [-T / 2 + RETRAIT, 0], nord: [0, -T / 2 + RETRAIT], sud: [0, T / 2 - RETRAIT] }[q.cote] || [0, 0];
    return { x: q.x * T + T / 2 + o[0], y: q.y * T + T / 2 + o[1], cote: q.cote };
  }

  /** Le joueur, a pied sur la glace, au guichet, sans patins aux pieds. */
  function sousLaMain(j) {
    const f = fiche(), q = guichet();
    if (!f || !f.patins || !q || !j || j.dansVehicule || j.patins || !surLaGlace(j.x, j.y)) return false;
    return dist2(j.x, j.y, q.x, q.y) <= f.patins.portee_px * f.patins.portee_px;
  }

  function invite(j) {
    if (!sousLaMain(j)) return null;
    const p = fiche().patins;
    return p.invite + ' — ' + p.prix + ' $';
  }

  //: Les voix du guichet (`fiche().voix`, une serie) : declarees et chargees une fois, en approchant de la glace.
  let voixPretes = false;
  function preparerVoix() {
    const f = fiche();
    if (voixPretes || !f || !f.voix || typeof Son === 'undefined' || !Son.Voix) return;
    voixPretes = true;
    Son.Voix.declarer([f.voix]);
    Son.Voix.chargerHistoire('patinoire');
  }
  /** Madame Thibodeau dit sa replique `cle` : sa voix (si elle est la), et le texte au HUD. */
  function dire(cle, texte) {
    preparerVoix();
    if (Son.Voix) Son.Voix.parler('thibodeau-patins-' + cle, {});
    Hud.message(texte);
  }

  /** ACTION au guichet : deux piastres, et on chausse. Le mot de Madame Thibodeau suit le jour, pas un de. */
  function agir(j) {
    const p = fiche().patins;
    if (!Missions.payer(p.prix, 'PATINS')) { dire('fauche', p.fauche); Son.SFX.erreur(); return true; }
    j.patins = true;
    const n = (B.partie.jour || 0) % p.mots.length;
    dire('mot-' + (n + 1), p.mots[n]);
    Son.SFX.ramasse();
    return true;
  }

  /** On rend ses patins (on quitte la glace, ou elle fond). */
  function rendre(j) {
    j.patins = false;
    if (j.type === 'joueur' && fiche() && fiche().patins) Hud.message(fiche().patins.rendus);
  }

  // ------------------------------------------------------------------ le son (vague 3)

  //: La rumeur qu'on entend, glissee image par image ; quand on a demande son lieu.
  let rumeur = 0, rumeurDemandee = -Infinity;

  /** A chaque image : les lames et les enfants tant qu'on patine (en fondu, jamais coupe net), et la valse du
      haut-parleur le soir — plus fort en approchant, muets dedans. */
  function majSon() {
    const f = fiche(), j = B.joueur;
    if (typeof Son === 'undefined' || !f || !f.son || !B.partie) return;
    const s = f.son, g = geo();
    let pres = 0;
    if (j && g && ouverte() && voulus(B.partie.heure) > 0) {
      const d = Math.hypot(j.x - (g.x0 + g.x1) / 2, j.y - (g.y0 + g.y1) / 2);
      if (d < s.portee_px) pres = d <= s.plein_px ? 1 : 1 - (d - s.plein_px) / (s.portee_px - s.plein_px);
    }
    const voulu = s.rumeur * Math.pow(pres, 1.5);
    rumeur += (voulu - rumeur) * 0.05;
    if (Math.abs(voulu - rumeur) < 0.004) rumeur = voulu;
    const t = B.t || 0;
    if (voulu > 0 && Son.Lieu && t - rumeurDemandee >= 300) { rumeurDemandee = t; Son.Lieu.charger('patinoire'); }
    if (rumeur > 0.004) {
      if (!Son.boucleActive('patinoire')) Son.boucle('patinoire', true, rumeur, 0.5);
      else Son.reglerBoucle('patinoire', rumeur);
    } else if (Son.boucleActive('patinoire')) Son.boucle('patinoire', false, 0, 0.5);
    if (pres > 0) preparerVoix();                    // les mots du guichet : prets avant le premier patin
    const h = B.partie.heure * 24;
    if (pres > 0 && h >= s.valse_des_h && h < s.valse_jusqu_h && Son.Rue) Son.Rue.demander('patinoire_valse', pres * s.valse);
  }

  function enCours() { return patineurs; }
  function oublier() { patineurs = []; }

  return { geo, ouverte, surLaGlace, bloquer, bloqueChar, glisser, dessinerSol, dessinerLames, lampes,
           maj, voulus, enCours, oublier, guichet, sousLaMain, invite, agir, majSon, adherence, frein };
})();
