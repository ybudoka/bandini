/* Bandini — les territoires des gangs bougent (docs/jalons/les-territoires-des-gangs-bougent.md, vague 1).

   Martin (29 sept. 2026) : UN COIN PAR NUIT — chaque nuit, un gang plus fort que son voisin lui prend UN ilot a
   la frontiere ; COUCHER SES MEMBRES l'affaiblit, sa force remonte doucement ; IL GARDE SON COEUR — les ilots de
   sa cour ne se prennent jamais par la frontiere.

   ⚠️ LA CARTE vient de Python (`B.defs.pietons.territoires` : les ilots de chaque district, le gang du depart, le
   coeur de chaque gang) ; LA PARTIE garde le reste — `forcesDesGangs` (un nombre par gang) et `territoires`
   (« bx,by » -> le gang qui a PRIS l'ilot ; un ilot absent est au gang de son district). Une nouvelle partie n'a
   rien de pris : rien ne change au depart (la naissance des membres, le hasard du terminus).

   ⚠️ AUCUN DE : la nuit choisit l'ilot a prendre a l'empreinte du jour (`hash2`), jamais `B.rng()`.

   ⚠️ UN ILOT PRIS SE VIT : les membres du gang qui le tient y naissent et le defendent, comme dans une cour
   (`gangA`, lu par `Entites.peupler` et par l'hostilite a l'arme au poing). Les ilots d'origine d'un district,
   eux, restent ce qu'ils etaient : sans gang dans la rue, hors de sa cour. */

const Territoires = (function () {
  'use strict';

  let prepare = null, source = null;

  function coupes(blocs, rues) {
    const sortie = [0];
    let x = 0;
    for (let i = 0; i < blocs.length; i++) {
      if (i > 0) sortie.push(x + Math.floor(rues[i] / 2));
      x += rues[i] + blocs[i];
    }
    return sortie;
  }
  function rang(bornes, v) {
    let i = 0;
    while (i + 1 < bornes.length && bornes[i + 1] <= v) i++;
    return i;
  }

  /** La carte des ilots : `ilots` (« bx,by » -> { bx, by, gang (celui du depart), coeur }), les gangs, la grille. */
  function donnees() {
    const t = B.defs && B.defs.pietons && B.defs.pietons.territoires;
    const g = B.defs && B.defs.carte && B.defs.carte.grille;
    if (!t || !g) return null;
    if (source === t) return prepare;
    source = t;
    const ilots = {}, coeur = {};
    Object.keys(t.coeurs || {}).forEach(function (gang) {
      t.coeurs[gang].forEach(function (b) { coeur[b[0] + ',' + b[1]] = gang; });
    });
    for (const d of t.districts) {
      d.plan.forEach(function (ligne, j) {
        Array.from(ligne).forEach(function (lettre, i) {
          if (t.eau.indexOf(lettre) >= 0) return;
          const bx = d.bx + i, by = d.by + j, k = bx + ',' + by;
          ilots[k] = { bx: bx, by: by, k: k, gang: d.gang, district: d.slug, coeur: coeur[k] === d.gang };
        });
      });
    }
    prepare = { ilots: ilots, regles: t.regles, gangs: t.districts.map(function (d) { return d.gang; }),
                x: coupes(g.colonnes, g.rues_v), y: coupes(g.rangees, g.rues_h), y0: g.y0 || 0,
                w: g.colonnes.reduce(function (s, n) { return s + n; }, 0) + g.rues_v.reduce(function (s, n) { return s + n; }, 0),
                h: g.rangees.reduce(function (s, n) { return s + n; }, 0) + g.rues_h.reduce(function (s, n) { return s + n; }, 0) };
    return prepare;
  }

  /** L'ilot de cette tuile (de la ville d'avant), ou null. */
  function ilotA(tx, ty) {
    const d = donnees();
    if (!d) return null;
    const y = ty - d.y0;
    if (tx < 0 || y < 0 || tx >= d.w || y >= d.h) return null;
    return d.ilots[rang(d.x, tx) + ',' + rang(d.y, y)] || null;
  }

  function partie() {
    const p = B.partie;
    if (!p) return null;
    p.forcesDesGangs = p.forcesDesGangs || {};
    p.territoires = p.territoires || {};
    return p;
  }

  /** Le gang qui tient cet ilot, maintenant. */
  function tenuPar(ilot) {
    const p = partie();
    return (p && p.territoires[ilot.k]) || ilot.gang;
  }

  function force(gang) {
    const p = partie(), d = donnees();
    if (!p || !d) return 0;
    const f = p.forcesDesGangs[gang];
    return f === undefined ? d.regles.force : f;
  }

  /** Le district de ce gang est-il libere (M16, `libere`) ? Alors il sort du jeu : ni il ne prend, ni on ne lui
      prend. */
  function horsJeu(gang) {
    const p = B.partie, d = donnees();
    if (!p || !d) return false;
    const district = Object.keys(d.ilots).map(function (k) { return d.ilots[k]; })
      .find(function (i) { return i.gang === gang; });
    if (!district) return true;
    if (district.district === 'faubourg' && p.faubourgLibere) return true;
    return (p.libere || []).indexOf(district.district) >= 0;
  }

  /** Le gang CHEZ LUI a ce pixel : celui de la cour ou l'on est (`zone.gang`), sinon celui qui a PRIS l'ilot —
      null sur un ilot qui n'a jamais change de mains (comme avant). */
  function gangA(x, y) {
    const zone = Monde.zoneA(x, y);
    if (zone && zone.gang) return zone.gang;
    const i = ilotA(Math.floor(x / TT), Math.floor(y / TT));
    if (!i) return null;
    const p = partie();
    return (p && p.territoires[i.k]) || null;
  }

  /** Un membre couche (assomme ou tue) par un joueur : son gang s'affaiblit. ⚠️ Une fois par membre (`compteGang`) :
      un deuxieme coup sur un assomme le rassomme, il ne compte pas deux fois. */
  function couche(e, source) {
    if (!e || !e.gang || e.compteGang || !source || source.type !== 'joueur') return;
    const p = partie(), d = donnees();
    if (!p || !d) return;
    e.compteGang = true;
    p.forcesDesGangs[e.gang] = Math.max(0, force(e.gang) - d.regles.coup);
  }

  /** Les ilots voisins (les quatre cotes) d'un ilot. */
  function voisins(d, i) {
    return [[1, 0], [-1, 0], [0, 1], [0, -1]].map(function (v) { return d.ilots[(i.bx + v[0]) + ',' + (i.by + v[1])]; })
      .filter(Boolean);
  }

  /** LA NUIT : chaque gang reprend des forces ; puis, pour chaque paire de gangs voisins, le plus fort (de la marge
      au moins) prend UN ilot au plus faible — a la frontiere, jamais son coeur. Rend les prises
      ([{ gang, a, k }]), pour le Clairon. */
  function nuit() {
    const p = partie(), d = donnees();
    if (!p || !d) return [];
    const r = d.regles;
    d.gangs.forEach(function (g) { p.forcesDesGangs[g] = Math.min(r.force, force(g) + r.regain); });
    const prises = [];
    const ilots = Object.keys(d.ilots).sort().map(function (k) { return d.ilots[k]; });
    for (const fort of d.gangs) {
      if (horsJeu(fort)) continue;
      for (const faible of d.gangs) {
        if (faible === fort || horsJeu(faible) || force(fort) < force(faible) + r.marge) continue;
        // Les ilots du faible, a la frontiere du fort, hors de son coeur — un seul, a l'empreinte du jour.
        const possibles = ilots.filter(function (i) {
          return tenuPar(i) === faible && !(i.coeur && i.gang === faible)
            && voisins(d, i).some(function (v) { return tenuPar(v) === fort; });
        });
        if (!possibles.length) continue;
        let choisi = possibles[0], mieux = Infinity;
        for (const i of possibles) {
          const h = hash2((p.jour || 0) * 131 + i.bx, i.by * 977 + fort.length);
          if (h < mieux) { mieux = h; choisi = i; }
        }
        if (choisi.gang === fort) delete p.territoires[choisi.k];   // il reprend un ilot a lui
        else p.territoires[choisi.k] = fort;
        prises.push({ gang: fort, a: faible, k: choisi.k });
      }
    }
    return prises;
  }

  /** Le nom d'un gang, tel qu'on le dit (« Les Cravates »). */
  function nomDe(gang) {
    const g = ((B.defs.pietons && B.defs.pietons.gangs) || []).find(function (q) { return q.slug === gang; });
    return (g && g.nom) || gang;
  }

  /** La ligne du Clairon, le matin d'une prise. */
  function ligneDuClairon(prises) {
    if (!prises || !prises.length) return null;
    const q = prises[0];
    return nomDe(q.gang).toUpperCase() + ' ONT PRIS UN COIN AUX ' + nomDe(q.a).toUpperCase().replace(/^LES /, '');
  }

  /** La couleur d'un gang : celle du haut de ses membres (leur tenue ne change pas, `garderobe`). */
  function couleurDe(gang) {
    const g = ((B.defs.pietons && B.defs.pietons.gangs) || []).find(function (q) { return q.slug === gang; });
    const a = g && ((B.defs.pietons && B.defs.pietons.catalogue) || []).find(function (q) { return q.slug === g.pieton; });
    return (a && a.couleurs && a.couleurs.c) || '#c0392b';
  }

  /** Sur la grande carte : les ilots PRIS, aux couleurs de qui les tient. `pos(x, y)` : pixel de ville -> carte. */
  function dessinerSurLaCarte(ctx, pos) {
    const p = B.partie, d = donnees();
    if (!p || !d || !p.territoires) return;
    Object.keys(p.territoires).forEach(function (k) {
      const i = d.ilots[k];
      if (!i) return;
      const x0 = d.x[i.bx], x1 = i.bx + 1 < d.x.length ? d.x[i.bx + 1] : d.w;
      const y0 = d.y[i.by] + d.y0, y1 = (i.by + 1 < d.y.length ? d.y[i.by + 1] : d.h) + d.y0;
      const a = pos(x0 * TT, y0 * TT), b = pos(x1 * TT, y1 * TT);
      ctx.globalAlpha = 0.45;
      ctx.fillStyle = couleurDe(p.territoires[k]);
      ctx.fillRect(Math.round(a.x), Math.round(a.y), Math.max(1, Math.round(b.x - a.x)), Math.max(1, Math.round(b.y - a.y)));
      ctx.globalAlpha = 1;
      B.stats.rects++;
    });
  }

  return { donnees, ilotA, tenuPar, force, horsJeu, gangA, couche, nuit, ligneDuClairon, couleurDe, dessinerSurLaCarte };
})();
