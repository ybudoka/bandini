/* Bandini — la file pour entrer à la foire.

   Martin (30 sept. 2026) : « je veux une file de personnes qui attendent pour entrer à la foire quand c'est
   ouvert », puis « mets aussi des câbles de gestion de file » (docs/jalons/une-file-pour-entrer-a-la-foire.md).

   ⚠️ Python décide (`carte.FOIRE["file"]`, `_Chantier.file_de_foire`) : le rectangle du serpentin, sous la
   colonne EST de l'arche, et tous les nombres — combien attendent à chaque heure, l'écart, les cadences. Ce
   script trace le chemin, tend les câbles, fait avancer les gens et les fait chialer.

   ⚠️ **UN SEUL CHEMIN, DE LA RUE JUSQU'À DEDANS.** Il part du trottoir à l'est (d'où l'on arrive), entre par le
   bas du dernier couloir, serpente d'un couloir à l'autre, attend à la bouche de l'arche, et finit dans la foire.
   Ceux de la file ne marchent pas, ils GLISSENT le long de ce chemin (`s`, en pixels) : c'est la file qui les
   pose à chaque image, comme `Foire` pose le joueur assis dans un manège. Aucune collision ne les concerne, et
   `demeler` pousse les autres hors de leur chemin — pas l'inverse.

   ⚠️ **LE SERPENTIN EST SOLIDE POUR TOUS LES AUTRES** (`Monde.charger` : solidité 5 sur ses tuiles, sans en
   faire une clôture à peindre). On le contourne par la rue — ce que Martin a choisi en prenant le trottoir.

   ⚠️ **RIEN AU DÉ** (sauf ce que `creerPieton` tire lui-même, comme toute la foule de la foire) : les cadences,
   l'archétype et la réplique viennent de l'empreinte (`hash2`) ou d'un compteur. */

const FileDeFoire = (function () {
  'use strict';

  //: Un numéro de tri hors de portée des entités, de la foire (`Foire`, 900 000 000) et de la cabane.
  const ID_TRI = 930000000;
  //: La hauteur de la sangle au-dessus du sol, et ses couleurs : la sangle rouge des vraies, sur des poteaux
  //: chromés au pied noir.
  const HAUT = 7;
  const SANGLE = '#c0392b', SANGLE_OMBRE = '#7b241c', POTEAU = '#c8ccd4', POTEAU_OMBRE = '#6c717c', PIED = '#23232b';

  let fiche = null;        // le rectangle et sa fiche (`def.file_de_foire`), ou null : pas de file
  let chemin = null;       // [{x, y, s}] : les points du chemin, et leur abscisse curviligne
  let bouche = 0;          // l'abscisse où la tête attend, au pied de l'arche
  let entree = 0;          // l'abscisse du bas du dernier couloir : où la file commence pour vrai
  let fin = 0;             // l'abscisse dedans, où l'on devient un forain
  let cables = [];         // [{x1, y1, x2, y2}] : les sangles, poteau à poteau
  let gens = [];           // ceux de la file, de la tête à la queue
  let prochaineEntree = 0; // l'image où la tête passe l'arche
  let prochaineArrivee = 0;
  let chialeT = -1e9;      // la dernière fois que la file a chialé
  let chiales = 0;         // un compteur : la réplique tourne, elle ne se tire pas
  let rangeeAvant = null;  // la rangée du joueur à l'image d'avant (passe-t-il l'arche ?)

  // --- La géométrie ---------------------------------------------------------------------

  function cx(k) { return (fiche.x + k) * TT + 8; }
  function haut() { return fiche.y * TT + 5; }
  function bas() { return (fiche.y + fiche.h) * TT - 5; }

  /** Le trottoir à l'est de l'entrée : jusqu'où on peut arriver en ligne droite (une rue qui croise, un
      obstacle, et l'approche s'arrête là). */
  function approche() {
    const ty = fiche.y + fiche.h - 1;
    let n = 0;
    while (n < 24) {
      const tx = fiche.x + fiche.l + n;
      if (!Monde.marchablePieton(tx, ty) || Monde.estRoute(tx, ty)) break;
      n++;
    }
    return n;
  }

  function construire(def) {
    fiche = def || null;
    chemin = null; cables = []; gens = [];
    if (!fiche) return;
    const l = fiche.l, points = [];
    // D'où l'on arrive : le trottoir à l'est, puis l'entrée au bas du dernier couloir.
    points.push({ x: cx(l - 1) + approche() * TT, y: bas() });
    // Le serpentin : le dernier couloir monte, le suivant descend… le premier monte vers l'arche (`couloirs`
    // est impair : c'est ce qui met l'entrée en bas et la sortie en haut).
    for (let k = l - 1; k >= 0; k--) {
      const monte = (l - 1 - k) % 2 === 0;
      points.push({ x: cx(k), y: monte ? bas() : haut() });
      points.push({ x: cx(k), y: monte ? haut() : bas() });
    }
    const avantBouche = points.length - 1;
    // La bouche, puis l'arche, puis dedans.
    points.push({ x: cx(0), y: (fiche.y - 1) * TT + 8 });
    points.push({ x: cx(0), y: (fiche.y - 2) * TT + 8 });
    let s = 0;
    points.forEach(function (p, i) {
      if (i > 0) s += Math.hypot(p.x - points[i - 1].x, p.y - points[i - 1].y);
      p.s = s;
    });
    chemin = points;
    entree = points[1].s;
    bouche = points[avantBouche].s;
    fin = s;
    // Les câbles. Entre deux couloirs, la sangle s'ouvre là où l'on passe de l'un à l'autre : en bas si le
    // couloir de gauche monte (on y entre par le bas), en haut s'il descend.
    const x0 = fiche.x * TT, y0 = fiche.y * TT, y1 = (fiche.y + fiche.h) * TT, trou = 13;
    cables.push({ x1: x0, y1: y0 + 1, x2: x0, y2: y1 - 1 });                    // l'ouest : les colonnes libres
    for (let k = 0; k < l - 1; k++) {
      const x = (fiche.x + k + 1) * TT, monte = (l - 1 - k) % 2 === 0;
      cables.push(monte ? { x1: x, y1: y0 + 1, x2: x, y2: y1 - trou } : { x1: x, y1: y0 + trou, x2: x, y2: y1 - 1 });
    }
    cables.push({ x1: (fiche.x + l) * TT, y1: y0 + 1, x2: (fiche.x + l) * TT, y2: y1 - trou });   // l'est : l'entrée en bas
    cables.push({ x1: x0, y1: y1 - 1, x2: (fiche.x + l) * TT, y2: y1 - 1 });   // le sud : le bord de la rue
  }

  /** Le point du chemin à l'abscisse `s`, et le sens où l'on y va. */
  function point(s) {
    const c = chemin;
    if (s <= 0) return { x: c[0].x, y: c[0].y, dx: c[1].x - c[0].x, dy: c[1].y - c[0].y };
    for (let i = 1; i < c.length; i++) {
      if (s <= c[i].s || i === c.length - 1) {
        const a = c[i - 1], b = c[i], u = b.s > a.s ? Math.min(1, (s - a.s) / (b.s - a.s)) : 1;
        return { x: a.x + (b.x - a.x) * u, y: a.y + (b.y - a.y) * u, dx: b.x - a.x, dy: b.y - a.y };
      }
    }
    return null;
  }

  /** Combien le serpentin tient, de la bouche jusqu'à l'entrée. */
  function capacite() { return fiche ? Math.floor((bouche - entree) / fiche.ecart_px) + 1 : 0; }

  /** Combien attendent à cette heure-ci (`par_heure`), plafonné par ce que le serpentin tient. */
  function voulus() {
    if (!fiche || !B.partie) return 0;
    const h = Math.floor(((B.partie.heure || 0) % 1) * 24) % 24;
    return Math.min(capacite(), fiche.par_heure[h] || 0);
  }

  // --- La vie de la file ----------------------------------------------------------------

  /** La foire est-elle ouverte ? Fermée l'hiver (`Foire.fermee`, s'il existe), jamais autrement. */
  function ouverte() { return !(typeof Foire !== 'undefined' && Foire.fermee && Foire.fermee()); }

  /** La file existe-t-elle ici et maintenant ? Dehors, la foire ouverte, le joueur pas trop loin. */
  function active() {
    const def = Monde.carte && Monde.carte.def, r = def && def.foire, j = B.joueur;
    if (!fiche || !r || !j || B.interieur || !ouverte()) return false;
    const bx = Math.max(r.x * TT, Math.min(j.x, (r.x + r.l) * TT));
    const by = Math.max(r.y * TT, Math.min(j.y, (r.y + r.h) * TT));
    return Math.hypot(bx - j.x, by - j.y) <= fiche.rayon_px;
  }

  function zoneVisible() {
    return Entites.visibleAEcran((fiche.x + fiche.l / 2) * TT, (fiche.y + fiche.h / 2) * TT, 5 * TT);
  }

  function poser(e, s) {
    const p = point(s);
    const avant = e.fileS === undefined ? null : { x: e.x, y: e.y };
    e.fileS = s; e.x = p.x; e.y = p.y; e.vx = 0; e.vy = 0;
    if (avant && e.anim) e.anim.dist += Math.abs(e.x - avant.x) + Math.abs(e.y - avant.y);
    // On regarde où l'on va : la tête de la file, par le chemin.
    Entites.regarder(e, p.dx, p.dy);
  }

  /** Un de plus dans la file, à l'abscisse `s`. ⚠️ Un passant ORDINAIRE : pas une mascotte, pas un gang. */
  function naitre(s) {
    const p = point(s);
    const arch = Entites.archetypeDeRue(p.x, p.y, hash2(Math.round(s * 7) + B.t, 0xF11E) / 4294967296);
    const e = Entites.creerPieton(p.x, p.y, arch);
    if (!e) return null;
    e.enFile = true; e.etat = 'file'; e.metier = null;
    poser(e, s);
    gens.push(e);
    return e;
  }

  /** On lâche quelqu'un : un passant de la rue (hors de la file), ou — s'il n'est plus à l'écran — personne. */
  function lacher(e) {
    e.enFile = false; e.fileS = undefined;
    if (e.etat === 'file') { e.etat = 'flane'; e.minuterie = 0; }
    if (!Entites.visibleAEcran(e.x, e.y, 40)) Entites.retirer(e);
  }

  function vider() { gens.forEach(lacher); gens = []; }

  /** La tête a passé l'arche : elle devient quelqu'un de la foire (`majForain`, la foule qui flâne). */
  function entrerDansLaFoire(e) {
    e.enFile = false; e.fileS = undefined;
    e.metier = 'forain'; e.foire = true;
    e.etat = 'flane'; e.minuterie = 0;
  }

  function maj() {
    if (!fiche || !chemin) return;
    if (!active()) { if (gens.length) vider(); rangeeAvant = null; return; }
    if (typeof Son !== 'undefined' && Son.Voix && Son.Voix.chargerLieu) Son.Voix.chargerLieu('foire');
    // Qui a quitté la file (frappé, effrayé, retiré de la ville) n'y est plus.
    gens = gens.filter(function (e) {
      if (e.vivant && e.enFile && e.etat === 'file' && B.entites.indexOf(e) >= 0) return true;
      if (e.enFile) { e.enFile = false; e.fileS = undefined; }
      return false;
    });
    const voulu = voulus();
    // ⚠️ ON ARRIVE ET ELLE EST DÉJÀ LÀ : tant qu'on ne la voit pas, la file se remplit d'un coup — comme
    // la foule de la foire, qu'on trouve pleine en y arrivant.
    if (!zoneVisible()) {
      while (gens.length < voulu && naitre(Math.max(0, bouche - gens.length * fiche.ecart_px))) { /* rien */ }
    } else if (gens.length < voulu && B.t >= prochaineArrivee) {
      // Sous nos yeux : on arrive à pied, par le trottoir de l'est, d'aussi loin qu'on ne se voit pas.
      prochaineArrivee = B.t + fiche.arrivee_images;
      const queue = gens.length ? gens[gens.length - 1].fileS : fin;
      if (queue - fiche.ecart_px > 0) {
        let s = 0;
        for (let d = entree; d >= 0; d -= TT) {
          const p = point(d);
          if (!Entites.visibleAEcran(p.x, p.y, 12)) { s = d; break; }
        }
        naitre(Math.min(s, queue - fiche.ecart_px));
      }
    }
    // La tête paie et entre, à sa cadence.
    const tete = gens[0];
    if (tete && !tete.entre && tete.fileS >= bouche - 0.5 && B.t >= prochaineEntree) {
      const [a, b] = fiche.entree_images;
      prochaineEntree = B.t + a + hash2(B.t, 0xF11E0) % (b - a + 1);
      tete.entre = true;
    }
    // Chacun avance jusqu'à sa place : la bouche pour la tête (dedans si elle entre), un écart derrière celui
    // de devant pour les autres. ⚠️ Jamais à reculons, et jamais dans le dos de celui de devant.
    let devant = null;
    for (const e of gens.slice()) {
      const but = devant ? devant.fileS - fiche.ecart_px : (e.entre ? fin : bouche);
      if (but > e.fileS) poser(e, Math.min(but, e.fileS + fiche.pas_px));
      else poser(e, e.fileS);
      if (e.entre && e.fileS >= fin - 0.01) { gens.splice(gens.indexOf(e), 1); entrerDansLaFoire(e); continue; }
      devant = e;
    }
    majChiale();
  }

  // --- Le joueur coupe la file ------------------------------------------------------------

  function arche() { return Monde.barrieres().find(function (q) { return q.slug === 'foire'; }); }

  /** Les répliques d'un genre (`file_h`, `file_f`), dans l'ordre : elles voyagent dans la suite du paquet
      (`repliques_de_la_file`, `audio.VOIX_DE_LA_FILE`). */
  function repliques(genre) {
    return ((B.defs && B.defs.repliques_de_la_file) || []).filter(function (v) { return v.genre === genre; });
  }

  /** Le joueur passe l'arche vers dedans alors qu'on attend : la file chiale. Une fois, pas à chaque pas. */
  function majChiale() {
    const j = B.joueur, b = arche();
    if (!j || !b) return;
    const rangee = Math.floor(j.y / TT), colonne = Math.floor(j.x / TT);
    const passe = rangeeAvant !== null && rangeeAvant > b.y && rangee <= b.y && colonne >= b.x && colonne < b.x + b.l;
    rangeeAvant = rangee;
    if (!passe || !gens.length || j.dansVehicule || B.t - chialeT < fiche.chiale_images) return;
    // Qui chiale : le plus proche du joueur (celui qui l'a vu passer devant lui).
    let qui = gens[0], d = Infinity;
    for (const e of gens) {
      const ici = Math.hypot(e.x - j.x, e.y - j.y);
      if (ici < d) { d = ici; qui = e; }
    }
    chiale(qui);
  }

  /** `qui` le dit, en bulle et à voix haute (genres `file_h` et `file_f`). Rend la réplique. */
  function chiale(qui) {
    const genre = Entites.estFemme(qui) ? 'file_f' : 'file_h';
    const liste = repliques(genre);
    if (!liste.length) return null;
    const v = liste[chiales % liste.length];
    chiales++;
    chialeT = B.t;
    Entites.bulle(qui, v.texte, { duree: fiche.bulle_images });
    if (typeof Son !== 'undefined' && Son.Voix) Son.Voix.dire(genre, qui.x, qui.y, v.slug);
    return v;
  }

  // --- Le dessin : les poteaux et leurs sangles, triés avec les gens ---------------------------

  function peindreCable(ctx, c, cx0, cy0) {
    const x1 = Math.round(c.x1 - cx0), y1 = Math.round(c.y1 - cy0), x2 = Math.round(c.x2 - cx0), y2 = Math.round(c.y2 - cy0);
    // La sangle : une bande de deux pixels, tendue d'un poteau à l'autre, avec son ombre dessous.
    if (y1 === y2) {
      ctx.fillStyle = SANGLE; ctx.fillRect(Math.min(x1, x2), y1 - HAUT, Math.abs(x2 - x1) + 1, 1);
      ctx.fillStyle = SANGLE_OMBRE; ctx.fillRect(Math.min(x1, x2), y1 - HAUT + 1, Math.abs(x2 - x1) + 1, 1);
    } else {
      ctx.fillStyle = SANGLE; ctx.fillRect(x1 - 1, Math.min(y1, y2) - HAUT, 1, Math.abs(y2 - y1) + 1);
      ctx.fillStyle = SANGLE_OMBRE; ctx.fillRect(x1, Math.min(y1, y2) - HAUT, 1, Math.abs(y2 - y1) + 1);
    }
    // Les poteaux : aux deux bouts, et un tous les seize pixels entre les deux.
    const long = Math.max(Math.abs(x2 - x1), Math.abs(y2 - y1)), n = Math.max(1, Math.round(long / TT));
    for (let i = 0; i <= n; i++) {
      const px = Math.round(x1 + (x2 - x1) * i / n), py = Math.round(y1 + (y2 - y1) * i / n);
      ctx.fillStyle = PIED; ctx.fillRect(px - 2, py, 4, 1);
      ctx.fillStyle = POTEAU_OMBRE; ctx.fillRect(px, py - HAUT, 1, HAUT);
      ctx.fillStyle = POTEAU; ctx.fillRect(px - 1, py - HAUT, 1, HAUT);
      ctx.fillStyle = POTEAU; ctx.fillRect(px - 1, py - HAUT - 1, 2, 1);
    }
  }

  function ajouterVisibles(visibles, cx0, cy0) {
    if (!fiche || !chemin || B.interieur) return;
    if (!Entites.visibleAEcran((fiche.x + fiche.l / 2) * TT, (fiche.y + fiche.h / 2) * TT, 6 * TT)) return;
    cables.forEach(function (c, k) {
      // ⚠️ Trié par le bout SUD : un câble nord-sud passe derrière qui se tient plus bas que lui.
      visibles.push({ id: ID_TRI + k, vivant: true, x: Math.max(c.x1, c.x2), y: Math.max(c.y1, c.y2),
                      peindreFoire: function (ctx) { peindreCable(ctx, c, cx0, cy0); } });
    });
  }

  // --- Le départ ------------------------------------------------------------------------------

  function demarrer() {
    const def = Monde.carte && Monde.carte.def;
    construire(def && def.file_de_foire);
    prochaineEntree = 0; prochaineArrivee = 0; chialeT = -1e9; chiales = 0; rangeeAvant = null;
  }

  return {
    demarrer, maj, ajouterVisibles, chiale, active, voulus, capacite, point,
    gens: function () { return gens; },
    chemin: function () { return chemin; },
    cables: function () { return cables; },
    abscisses: function () { return { entree: entree, bouche: bouche, fin: fin }; },
  };
})();
