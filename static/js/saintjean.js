/* Bandini — la Saint-Jean sur la baie (docs/jalons/la-saint-jean-sur-la-baie.md).

   Le soir du 24 juin (`Calendrier.estLe('saint_jean')`) : un defile de chars allegoriques remonte une rue
   du Faubourg, fermee le temps qu'il passe, puis des feux d'artifice partent du phare de La Pointe.

   ⚠️ PYTHON DIT OU ET QUAND (`app/saint_jean.py`, `B.defs.saint_jean`) : la rue est une des `fermetures`
   que la carte sait deja barrer sans couper la ville. Le soir de la fete, elle PREND LA PLACE de l'entrave
   du jour (`Monde.entraveDuJour` la demande ici) — une seule rue fermee a la fois, toujours.

   ⚠️ RIEN AU DE : le defile est une fonction de l'heure ; une fusee, de l'image et de son numero (ses
   couleurs a l'empreinte). Ni entite ni `B.rng()` : les chars du defile sont PEINTS. */

const SaintJean = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.saint_jean; }

  function heure() { return B.partie ? B.partie.heure * 24 : 0; }

  /** Le soir de la fete ? (le jour, pas encore l'heure) */
  function aujourdhui() {
    return !!(B.partie && donnees() && typeof Calendrier !== 'undefined' && Calendrier.estLe('saint_jean', B.partie.jour));
  }

  function dans(fenetre) { const h = heure(); return h >= fenetre[0] && h < fenetre[1]; }

  /** Le defile passe maintenant ? `defileA(jour, heure)` en est la version pure. */
  function defile() { return aujourdhui() && !!donnees().rue && dans(donnees().horaire.defile); }
  function feux() { return aujourdhui() && dans(donnees().horaire.feux); }

  /** La rue fermee du defile, comme une entrave du jour (`Monde.entraveDuJour`) — ou null. */
  let barriere = null;
  function fermeture() {
    if (!defile()) return null;
    const d = donnees(), r = d.rue;
    if (!barriere) {
      barriere = { slug: 'defile', nom: 'Le défilé de la Saint-Jean', x: r.x, y: r.y, l: r.l, h: r.h, sens: null,
                   arrete: ['vehicule'], condition: { toujours: true }, forcer: { degats: 14 },
                   raison: d.raison, decor: 'barricade', plein: true, existant: false };
    }
    return barriere;
  }

  /** Ou en est le defile (0 a 1 de sa fenetre). */
  function avance() {
    const f = donnees().horaire.defile;
    return Math.max(0, Math.min(1, (heure() - f[0]) / (f[1] - f[0])));
  }

  /** Les chars du defile, en pixels : ils remontent la rue d'un bout a l'autre, a la file. Ceux qui ne
      sont pas encore entres, ou deja sortis, n'y sont pas. Pure (avec l'heure). */
  function chars() {
    if (!defile()) return [];
    const d = donnees(), r = d.rue, vertical = r.h >= r.l;
    const long = (vertical ? r.h : r.l) * TT, ecart = d.defile.ecart_tuiles * TT, n = d.defile.chars;
    const tete = avance() * (long + ecart * (n - 1));
    const out = [];
    for (let k = 0; k < n; k++) {
      const s = tete - k * ecart;
      if (s < 0 || s > long) continue;
      const milieu = vertical ? (r.x + r.l / 2) * TT : (r.y + r.h / 2) * TT;
      out.push(vertical ? { x: milieu, y: r.y * TT + s, k: k, vertical: true } : { x: r.x * TT + s, y: milieu, k: k, vertical: false });
    }
    return out;
  }

  //: Les quatre chars : leur plateau, et ce qu'ils portent (une fleur de lys, un drapeau, une
  //: violoneux, un feu de joie).
  const TONS = ['#1f4fa3', '#ffffff', '#f2c230', '#e0453a'];

  function peindreChar(ctx, c, cam) {
    const x = Math.round(c.x - cam.x), y = Math.round(c.y - cam.y);
    const lx = c.vertical ? 12 : 20, ly = c.vertical ? 20 : 12;
    ctx.fillStyle = '#101018'; ctx.fillRect(x - lx / 2 - 1, y - ly / 2 - 1, lx + 2, ly + 2);
    ctx.fillStyle = '#1f4fa3'; ctx.fillRect(x - lx / 2, y - ly / 2, lx, ly);
    ctx.fillStyle = '#ffffff'; ctx.fillRect(x - lx / 2, y - ly / 2, lx, 2); ctx.fillRect(x - lx / 2, y + ly / 2 - 2, lx, 2);
    ctx.fillStyle = TONS[c.k % TONS.length];
    if (c.k % 4 === 0) {                      // la fleur de lys
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(x - 1, y - 7, 2, 11); ctx.fillRect(x - 4, y - 3, 8, 2);
      ctx.fillRect(x - 5, y - 6, 2, 4); ctx.fillRect(x + 3, y - 6, 2, 4); ctx.fillRect(x - 3, y + 3, 6, 1);
    } else if (c.k % 4 === 1) {               // le drapeau au mat
      ctx.fillStyle = '#3a3d44'; ctx.fillRect(x - 4, y - 9, 1, 13);
      ctx.fillStyle = '#1f4fa3'; ctx.fillRect(x - 3, y - 9, 8, 6);
      ctx.fillStyle = '#ffffff'; ctx.fillRect(x, y - 9, 1, 6); ctx.fillRect(x - 3, y - 7, 8, 1);
    } else if (c.k % 4 === 2) {               // le violoneux, sur une balle de foin
      ctx.fillStyle = '#d9b44a'; ctx.fillRect(x - 5, y - 1, 10, 5);
      ctx.fillStyle = '#e8b088'; ctx.fillRect(x - 1, y - 8, 3, 3);
      ctx.fillStyle = '#c0392b'; ctx.fillRect(x - 2, y - 5, 5, 5);
      ctx.fillStyle = '#7a4a16'; ctx.fillRect(x + 3, y - 5, 4, 1);
    } else {                                  // le feu de joie
      ctx.fillStyle = '#5a3a22'; ctx.fillRect(x - 5, y + 1, 10, 2);
      const f = Math.floor(B.t / 6) % 2;
      ctx.fillStyle = '#e0453a'; ctx.fillRect(x - 3, y - 4 - f, 6, 5 + f);
      ctx.fillStyle = '#ffd23f'; ctx.fillRect(x - 1, y - 6 - f, 3, 6);
    }
  }

  /** Le defile a l'ecran (sous les passants). */
  function dessinerDefile(ctx, cam) {
    const cs = chars();
    for (const c of cs) {
      if (c.x < cam.x - 30 || c.y < cam.y - 30 || c.x > cam.x + VW + 30 || c.y > cam.y + VH + 30) continue;
      peindreChar(ctx, c, cam);
      B.stats.rects += 8;
    }
  }

  // --- Les feux ---------------------------------------------------------------------------

  //: Une fusee vit tant d'images (elle monte, eclate, retombe en s'eteignant).
  const VIE = 84;

  /** Les fusees en l'air a cette image : leur numero (a l'empreinte duquel tout se tire) et leur age. */
  function fusees() {
    if (!feux()) return [];
    const pas = donnees().feux.images_entre, out = [];
    const derniere = Math.floor(B.t / pas);
    for (let n = derniere; n >= 0 && (B.t - n * pas) < VIE; n--) out.push({ n: n, age: B.t - n * pas });
    return out;
  }

  /** Ou eclatent les fusees, a l'ecran : au-dessus du phare s'il est a l'ecran ; sinon au bord du ciel,
      du cote du phare (on les voit de partout). */
  function ciel(cam) {
    const phare = typeof Histoire !== 'undefined' && Histoire.lieu ? Histoire.lieu('phare') : null;
    if (!phare) return { x: VW / 2, y: 40 };
    const x = phare.x - cam.x, y = phare.y - cam.y - 90;
    return { x: Math.max(40, Math.min(VW - 40, x)), y: Math.max(28, Math.min(VH * 0.45, y)) };
  }

  function eclat(f, c) {
    const d = donnees(), h = hash2(f.n, 0x5A1E);
    const couleur = d.feux.couleurs[h % d.feux.couleurs.length];
    const x = c.x + ((h >>> 4) % 140) - 70, y = c.y + ((h >>> 12) % 40) - 20;
    // Une fusee sur trois a une deuxieme couleur, au coeur de sa couronne.
    const coeur = (h >>> 8) % 3 === 0 ? d.feux.couleurs[(h >>> 16) % d.feux.couleurs.length] : null;
    return { x: x, y: y, couleur: couleur, coeur: coeur, rayon: 24 + ((h >>> 20) % 20) };
  }

  /** Les feux par-dessus la ville (sous la nuit : ce sont leurs lampes qui brillent). ⚠️ Ni entite ni de. */
  function dessinerFeux(ctx, cam) {
    const fs = fusees();
    if (!fs.length) return;
    const c = ciel(cam);
    let n = 0;
    for (const f of fs) {
      const e = eclat(f, c);
      if (f.age < 16) {                                   // elle monte
        ctx.fillStyle = '#ffe9a8';
        ctx.fillRect(Math.round(e.x), Math.round(e.y + (16 - f.age) * 5), 1, 3);
        n++;
        continue;
      }
      const t = (f.age - 16) / (VIE - 16), r = e.rayon * Math.min(1, t * 2.2), chute = t * t * 14;
      if (f.age < 20) { ctx.fillStyle = '#ffffff'; ctx.fillRect(Math.round(e.x) - 2, Math.round(e.y) - 2, 5, 5); n++; }   // le flash
      ctx.globalAlpha = Math.max(0, 1 - t);
      for (let k = 0; k < 24; k++) {
        const a = k / 24 * Math.PI * 2, c = Math.cos(a), s = Math.sin(a);
        ctx.fillStyle = e.couleur;
        ctx.fillRect(Math.round(e.x + c * r), Math.round(e.y + s * r + chute), 2, 2);
        ctx.fillRect(Math.round(e.x + c * r * 0.8), Math.round(e.y + s * r * 0.8 + chute * 0.8), 1, 1);   // la trainee
        if (e.coeur && k % 2 === 0) { ctx.fillStyle = e.coeur; ctx.fillRect(Math.round(e.x + c * r * 0.5), Math.round(e.y + s * r * 0.5 + chute * 0.6), 1, 1); }
        n += 2;
      }
      ctx.globalAlpha = 1;
    }
    B.stats.rects += n;
  }

  /** La lueur des eclats, pour la nuit (`Base.fin`) : une lampe par fusee eclatee. */
  function lampes(cam) {
    const fs = fusees();
    if (!fs.length) return [];
    const c = ciel(cam), out = [];
    for (const f of fs) {
      if (f.age < 16) continue;
      const e = eclat(f, c), t = (f.age - 16) / (VIE - 16);
      if (t > 0.8) continue;
      out.push({ x: e.x, y: e.y, r: Math.round(60 * (1 - t) + 20), c: e.couleur });
    }
    return out;
  }

  /** Une fusee part : le bruit de son eclat (synthetise). Une fois par fusee. */
  let derniereEntendue = -1;
  function maj() {
    if (!feux()) return;
    const pas = donnees().feux.images_entre, n = Math.floor(B.t / pas);
    if (B.t - n * pas === 16 && n !== derniereEntendue) { derniereEntendue = n; Son.SFX.artifice(); }
  }

  /** Ce que le Clairon ecrit : la veille, et le matin de la fete. */
  function ligneDuClairon() {
    const d = donnees(), p = B.partie;
    if (!d || !p || typeof Calendrier === 'undefined') return null;
    if (Calendrier.estLe('saint_jean', p.jour + 1)) return d.clairon.veille;
    if (Calendrier.estLe('saint_jean', p.jour)) return d.clairon.jour;
    return null;
  }

  return { donnees, aujourdhui, defile, feux, fermeture, chars, fusees, dessinerDefile, dessinerFeux, lampes, maj,
           ligneDuClairon };
})();
