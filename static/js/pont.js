/* Bandini — le pont de glace (docs/jalons/le-pont-de-glace.md).

   Au grand froid (les jours `froid.jours` de l'annee, `Calendrier`), la baie prend entre La Pointe et
   l'Ile-aux-Corneilles : un chemin balise de sapins qu'on fait en char. Le dernier jour, a partir de
   `degel_h`, la glace craque — un char arrete dessus plus de `craque_s` secondes passe au travers.

   ⚠️ PYTHON DIT OU, ICI ON GELE (`app/pont_de_glace.py`, `B.defs.pont`). La ville garde son eau : le
   temps du grand froid, les tuiles du chemin deviennent du sol (`poser`, comme la passerelle du
   traversier — `solide`, `route`, `passage` sauves), et `lever` les rend a l'eau, exactement comme
   avant. Ce qui est dessus a ce moment-la tombe a l'eau : un char coule, un passant nage.

   ⚠️ DERRIERE L'OPTION DE LA NEIGE (`B.options.neige`) : l'hiver du jeu. Sans elle, jamais de glace.

   ⚠️ UN BATEAU NE SE FAIT PAS PRENDRE : tant qu'une coque est sur le chemin, la baie attend pour prendre
   (on reessaie a la seconde suivante). Et une fois la glace posee, une coque s'y bute (`tuileInterdite`
   ne veut que de l'eau). */

const Pont = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.pont; }

  //: La glace posee : { carte, sauve: [[i, solide, route, passage]], fondues: Set d'indices }.
  let pose = null;

  /** Le grand froid ce jour-la ? Pure (avec l'option). */
  function froidA(jour) {
    const d = donnees();
    return !!(d && d.chemin && B.options && B.options.neige && typeof Calendrier !== 'undefined'
              && d.froid.jours.indexOf(Calendrier.jourDeLAnnee(jour)) >= 0);
  }

  function froid() { return !!B.partie && froidA(B.partie.jour); }

  /** Le dernier jour du froid, passe `degel_h` : la glace craque. */
  function degel() {
    const d = donnees(), p = B.partie;
    if (!froid() || froidA(p.jour + 1)) return false;
    return p.heure * 24 >= d.froid.degel_h;
  }

  function indice(c, t) { return t[1] * c.w + t[0]; }

  //: Les tuiles du chemin, depliees de ses rangees (`[y, x0, x1]`, le paquet), une fois.
  let deplie = null;
  function tuiles() {
    const d = donnees();
    if (!deplie && d && d.chemin) {
      deplie = [];
      for (const r of d.chemin.rangs) for (let x = r[1]; x <= r[2]; x++) deplie.push([x, r[0]]);
    }
    return deplie || [];
  }

  /** Cette tuile est-elle de la glace posee (et pas fondue) ? */
  function glace(tx, ty) {
    if (!pose || pose.carte !== Monde.carte) return false;
    const i = ty * pose.carte.w + tx;
    return pose.indices.has(i) && !pose.fondues.has(i);
  }

  /** La baie prend : les tuiles du chemin deviennent du sol. Pas tant qu'une coque est dessus. */
  function poser() {
    const d = donnees(), c = Monde.carte, indices = new Set();
    for (const t of tuiles()) indices.add(indice(c, t));
    const coque = B.entites.some(function (e) {
      return e.type === 'vehicule' && e.def && e.def.eau && indices.has(Math.floor(e.y / TT) * c.w + Math.floor(e.x / TT));
    });
    if (coque) return false;
    const sauve = [];
    for (const i of indices) {
      sauve.push([i, c.solide[i], c.route[i], c.passage[i]]);
      c.solide[i] = 0; c.route[i] = 1; c.passage[i] = 0;
    }
    pose = { carte: c, sauve: sauve, indices: indices, fondues: new Set() };
    return true;
  }

  /** Le degel fini : la carte redevient exactement ce qu'elle etait. */
  function lever() {
    if (!pose) return;
    const c = pose.carte;
    for (const s of pose.sauve) { c.solide[s[0]] = s[1]; c.route[s[0]] = s[2]; c.passage[s[0]] = s[3]; }
    pose = null;
  }

  /** Un trou dans la glace, sous ce char : sa tuile et ses voisines redeviennent de l'eau. */
  function craquer(v) {
    const c = pose.carte, tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    for (let dy = -1; dy <= 1; dy++) {
      for (let dx = -1; dx <= 1; dx++) {
        const i = (ty + dy) * c.w + tx + dx;
        if (!pose.indices.has(i) || pose.fondues.has(i)) continue;
        const s = pose.sauve.find(function (q) { return q[0] === i; });
        c.solide[i] = s[1]; c.route[i] = s[2]; c.passage[i] = s[3];
        pose.fondues.add(i);
      }
    }
    Son.SFX.choc();
    if (v.conducteur === B.joueur) { Hud.message('LA GLACE CÈDE!', 120); B.cam.secousse = Math.max(B.cam.secousse, 0.8); }
  }

  /** Une image : la glace se pose, craque au degel, se leve apres. ⚠️ En ville seulement : dedans,
      la carte est celle de la piece — la glace attend dehors, sur SA carte (`pose.carte`). */
  function maj() {
    if (B.interieur || B.bloc || !Monde.carte) return;
    // Une carte rechargee (une partie neuve) a toute son eau : l'ancienne pose ne tient plus.
    if (pose && pose.carte !== Monde.carte) pose = null;
    const f = froid();
    if (!f) { if (pose) lever(); return; }
    if (!pose) { if (B.t % 60 === 0) poser(); return; }
    if (!degel()) return;
    const d = donnees();
    for (const v of B.entites) {
      if (v.type !== 'vehicule' || v.etat === 'epave' || !glace(Math.floor(v.x / TT), Math.floor(v.y / TT))) { if (v.glaceT) v.glaceT = 0; continue; }
      if (Math.abs(v.vitesse) > 0.3) { v.glaceT = 0; continue; }
      v.glaceT = (v.glaceT || 0) + 1;
      if (v.glaceT > d.froid.craque_s * 60) { v.glaceT = 0; craquer(v); }
    }
  }

  //: La glace mince peinte de chaque cote du chemin, en tuiles.
  const MINCE = 4;

  //: Un sapin de balise, 10 x 14 (a l'empreinte de rien : ils se ressemblent tous).
  function peindreSapin(ctx) {
    const lignes = ['....a....', '...aaa...', '..aaaaa..', '....a....', '..aaaaa..', '.aaaaaaa.', '...aaa...', '.aaaaaaa.', 'aaaaaaaaa', '....t....', '....t....'];
    for (let y = 0; y < lignes.length; y++) {
      for (let x = 0; x < lignes[y].length; x++) {
        const g = lignes[y][x];
        if (g === '.') continue;
        ctx.fillStyle = g === 't' ? '#5a3a22' : ((x + y) % 3 === 0 ? '#e8f2fa' : '#1f5a36');
        ctx.fillRect(x, y + 2, 1, 1);
      }
    }
  }

  /** La glace a l'ecran : claire, rayee, et fendue au degel ; les sapins le long. Sans cache : quelques
      dizaines de tuiles, et seulement quand le froid tient. */
  function dessiner(ctx, cam) {
    if (!pose || pose.carte !== Monde.carte || B.interieur) return;
    const d = donnees(), fend = degel();
    let n = 0;
    // LA GLACE MINCE, de part et d'autre : peinte, pas posee — c'est de l'eau, on y coule. Plus pale a
    // mesure qu'on s'eloigne du chemin (un chemin de glace au milieu d'une eau d'ete ne ferait pas froid).
    const ys = tuiles().map(function (t) { return t[1]; }), xs = tuiles().map(function (t) { return t[0]; });
    const y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys), x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
    for (let ty = y0 - MINCE; ty <= y1 + MINCE; ty++) {
      if (ty >= y0 && ty <= y1) continue;
      const loin = ty < y0 ? y0 - ty : ty - y1;
      const y = Math.round(ty * TT - cam.y);
      if (y < -TT || y > VH) continue;
      ctx.fillStyle = 'rgba(214,232,245,' + (0.75 - loin * 0.16).toFixed(2) + ')';
      for (let tx = x0; tx <= x1; tx++) {
        if (!Monde.estEau(tx, ty)) continue;
        const x = Math.round(tx * TT - cam.x);
        if (x < -TT || x > VW) continue;
        const h = hash2(tx, ty + 7);
        if (loin === MINCE && h % 3) continue;          // le bord s'effiloche
        ctx.fillRect(x, y, TT, TT);
        n++;
      }
    }
    for (const t of tuiles()) {
      const i = indice(pose.carte, t);
      if (pose.fondues.has(i)) continue;
      const x = Math.round(t[0] * TT - cam.x), y = Math.round(t[1] * TT - cam.y);
      if (x < -TT || y < -TT || x > VW || y > VH) continue;
      const h = hash2(t[0], t[1]);
      ctx.fillStyle = '#cfe3f2'; ctx.fillRect(x, y, TT, TT);
      ctx.fillStyle = '#e9f4fb'; ctx.fillRect(x + (h % 9), y + ((h >>> 4) % 12), 6, 1);
      ctx.fillStyle = '#a9c8de'; ctx.fillRect(x + ((h >>> 8) % 11), y + ((h >>> 12) % 13), 4, 1);
      if (fend && h % 3 === 0) {
        ctx.fillStyle = '#4b6a82';
        for (let k = 0; k < 6; k++) ctx.fillRect(x + 3 + k * 2, y + 4 + ((h >>> k) % 3) + k, 2, 1);
      }
      n += 3;
    }
    for (const s of d.chemin.sapins) {
      const x = Math.round(s[0] * TT - cam.x), y = Math.round(s[1] * TT - cam.y);
      if (x < -TT || y < -TT || x > VW || y > VH) continue;
      ctx.drawImage(Atlas.cuirePeintre('sapin-de-balise', 10, 14, peindreSapin), x + 3, y);
    }
    B.stats.rects += n;
  }

  /** Ce que le Clairon ecrit : la veille du grand froid, et son premier matin. */
  function ligneDuClairon() {
    const d = donnees(), p = B.partie;
    if (!d || !d.chemin || !p) return null;
    if (!froidA(p.jour) && froidA(p.jour + 1)) return d.clairon.veille;
    if (froidA(p.jour) && !froidA(p.jour - 1)) return d.clairon.pendant;
    return null;
  }

  /** Une partie qui recommence : la glace rend son eau (la carte peut etre la meme). */
  function oublier() { lever(); }

  return { donnees, tuiles, froidA, froid, degel, glace, poser, lever, maj, dessiner, ligneDuClairon, oublier,
           get pose() { return pose; } };
})();
