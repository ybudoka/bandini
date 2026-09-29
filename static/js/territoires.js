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
    reprendre(e, p, d);
  }

  /** REPRENDRE UN COIN (vague 2) : dans un ilot qu'un gang a PRIS, coucher `regles.reprise` de ses membres le meme
      jour le rend au gang de son district. Le compte est par ilot et par jour (`partie.reprises`) : il ne
      s'accumule pas d'une semaine a l'autre. */
  function reprendre(e, p, d) {
    const i = ilotA(Math.floor(e.x / TT), Math.floor(e.y / TT));
    if (!i || p.territoires[i.k] !== e.gang) return;
    p.reprises = p.reprises || {};
    const avant = p.reprises[i.k];
    const r = avant && avant.jour === p.jour ? avant : { jour: p.jour, n: 0 };
    r.n++;
    if (r.n < d.regles.reprise) {
      p.reprises[i.k] = r;
      Hud.message('COIN DISPUTÉ · ' + r.n + ' / ' + d.regles.reprise, 90);
      return;
    }
    delete p.territoires[i.k];
    delete p.reprises[i.k];
    Hud.message('LE COIN EST REPRIS · ' + nomDe(i.gang).toUpperCase() + ' SONT CHEZ EUX', 180);
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

  /** La legende des territoires, sur la grande carte : qui tient les ilots pris (une puce de sa couleur, son nom),
      dans la marge de gauche. Rien tant que rien n'est pris. */
  function dessinerLaLegende(ctx, x, y) {
    const p = B.partie;
    if (!p || !p.territoires) return;
    const gangs = [];
    Object.keys(p.territoires).sort().forEach(function (k) {
      if (gangs.indexOf(p.territoires[k]) < 0) gangs.push(p.territoires[k]);
    });
    if (!gangs.length) return;
    Atlas.texte(ctx, 'COINS PRIS', x, y, '#e88a98', 1);
    gangs.forEach(function (g, n) {
      const yy = y + 10 + n * 9;
      ctx.fillStyle = '#101018'; ctx.fillRect(x, yy - 1, 7, 7);
      ctx.fillStyle = couleurDe(g); ctx.fillRect(x + 1, yy, 5, 5);
      Atlas.texte(ctx, nomDe(g).toUpperCase(), x + 10, yy, '#e8e2f4', 1);
    });
    B.stats.rects += 2 * gangs.length;
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

  /* --- LES GRAFFITIS SUIVENT LA FRONTIERE (vague 3) ----------------------------------------------------------

     Martin (29 sept. 2026) : un ilot pris porte les tags de qui le tient, et ceux du perdant y sont BARRES.

     ⚠️ UNE COUCHE, PAS LA VILLE : les tags de la ville sont cuits une fois dans les morceaux de carte
     (`carte.graffitis`) ; les refaire, c'etait regenerer la ville. Ceux d'un ilot pris se calculent ici, sans
     un de, depuis la carte finie : les murs nus (`F`, `d`) qu'on voit du trottoir, pas deja pris par une
     vitrine, une residence ou un tag — la regle de `Chantier.mur_taggable`. `Monde` les peint par-dessus, et
     recuit ses morceaux quand la frontiere bouge (`cle`).
     ⚠️ Choisis a l'EMPREINTE (`hash2` de la tuile et du gang) : le meme ilot pris par le meme gang porte les
     memes tags d'une partie a l'autre, et rendu puis repris, les memes encore. */

  /** Au plus tant de tags neufs par ilot pris, et pas plus pres que ca l'un de l'autre (en tuiles). */
  const TAGS_PAR_ILOT = 3, ECART_TAG = 4;

  /** La signature de la frontiere : change quand un ilot change de mains (et seulement la). */
  function cle() {
    const p = B.partie;
    if (!p || !p.territoires) return '';
    return Object.keys(p.territoires).sort().map(function (k) { return k + '=' + p.territoires[k]; }).join(';');
  }

  let reserves = null, reservesDe = null, gangDuTexte = null;

  /** Les murs deja pris, dans la ville cuite : les vitrines, les residences et les tags (`murs_tagges`). */
  function mursReserves() {
    const def = B.defs && B.defs.carte;
    if (!def) return new Set();
    if (reservesDe === def) return reserves;
    reservesDe = def;
    reserves = new Set();
    (def.devantures || []).concat(def.residences || []).forEach(function (d) {
      for (let i = 0; i < (d.l || 1); i++) reserves.add((d.x + i) + ',' + d.y);
    });
    (def.graffitis || []).forEach(function (g) { reserves.add(g.x + ',' + g.y); });
    return reserves;
  }

  /** Le gang qui signe ce texte (« CRV » -> cravates), ou null (un tag libre). */
  function gangDuTag(texte) {
    const d = donnees();
    if (!d) return null;
    if (!gangDuTexte) {
      gangDuTexte = {};
      const t = B.defs.pietons.territoires.tags || {};
      Object.keys(t).forEach(function (g) { t[g].forEach(function (m) { gangDuTexte[m[0]] = { gang: g, tuiles: m[1] }; }); });
    }
    const q = gangDuTexte[texte];
    return q ? q.gang : null;
  }

  /** Le rectangle de tuiles d'un ilot (coupe au milieu des rues, comme `ilotA`). */
  function rectangle(d, i) {
    return { x0: d.x[i.bx], x1: i.bx + 1 < d.x.length ? d.x[i.bx + 1] : d.w,
             y0: d.y[i.by] + d.y0, y1: (i.by + 1 < d.y.length ? d.y[i.by + 1] : d.h) + d.y0 };
  }

  /** Les tags que `gang` pose dans l'ilot `i` de `carte` : [{ x, y, texte, motif, penche, gang }]. */
  function tagsDuCoin(carte, d, i, gang) {
    const mots = (B.defs.pietons.territoires.tags || {})[gang] || [];
    if (!mots.length) return [];
    const pris = mursReserves(), r = rectangle(d, i);
    const mur = function (x, y) {
      if (x < 0 || y < 0 || x >= carte.w || y + 1 >= carte.h || pris.has(x + ',' + y)) return false;
      const g = carte.sol[y][x];
      return (g === 'F' || g === 'd') && !carte.solide[(y + 1) * carte.w + x];
    };
    const sel = gang.length * 7919 + gang.charCodeAt(0);
    const candidats = [];
    for (let y = r.y0; y < r.y1; y++) {
      for (let x = r.x0; x < r.x1; x++) if (mur(x, y)) candidats.push({ x: x, y: y, h: hash2(x * 31 + sel, y) >>> 0 });
    }
    candidats.sort(function (a, b) { return a.h - b.h || a.y - b.y || a.x - b.x; });
    // ⚠️ L'ECART vaut aussi pour les tags CUITS de l'ilot : un tag neuf colle a un vieux s'ecrivait par-dessus.
    const cuits = (B.defs.carte.graffitis || []).filter(function (g) {
      return g.x >= r.x0 - ECART_TAG && g.x < r.x1 + ECART_TAG && g.y >= r.y0 - ECART_TAG && g.y < r.y1 + ECART_TAG;
    });
    const poses = [];
    const loin = function (c) {
      return !poses.concat(cuits).some(function (q) { return Math.abs(q.x - c.x) + Math.abs(q.y - c.y) < ECART_TAG; });
    };
    for (const c of candidats) {
      if (poses.length >= TAGS_PAR_ILOT) break;
      if (!loin(c)) continue;
      // La place REELLE, jusqu'a trois tuiles de mur d'un seul tenant — puis un mot qui y tient.
      let place = 1;
      while (place < 3 && mur(c.x + place, c.y)) place++;
      const possibles = mots.filter(function (m) { return m[1] <= place; });
      if (!possibles.length) continue;
      poses.push({ x: c.x, y: c.y, texte: possibles[c.h % possibles.length][0], motif: (c.h >> 4) % 2 ? 2 : 0,
                   penche: (c.h >> 6) % 2, gang: gang });
    }
    return poses;
  }

  let tagsCle = null, tagsCarte = null, tagsListe = [];

  /** Tous les tags neufs de la frontiere (les ilots pris), pour la carte de la ville `carte`. */
  function tagsDeLaFrontiere(carte) {
    const k = cle(), d = donnees();
    if (!d || !k) return [];
    if (tagsCle === k && tagsCarte === carte) return tagsListe;
    tagsCle = k; tagsCarte = carte;
    const p = B.partie;
    tagsListe = [];
    Object.keys(p.territoires).sort().forEach(function (ik) {
      const i = d.ilots[ik];
      if (i) tagsListe = tagsListe.concat(tagsDuCoin(carte, d, i, p.territoires[ik]));
    });
    return tagsListe;
  }

  /** La couleur de bombe d'un gang : la sienne, eclaircie d'un tiers. ⚠️ Le brun des Chevreuils, tel quel, ne se
      lisait pas sur la brique (vu a la capture). */
  function bombeDe(gang) {
    const c = couleurDe(gang);
    const m = /^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(c);
    if (!m) return c;
    return '#' + [m[1], m[2], m[3]].map(function (h) {
      const v = Math.round(parseInt(h, 16) + (255 - parseInt(h, 16)) / 3);
      return (v < 16 ? '0' : '') + v.toString(16);
    }).join('');
  }

  /** Un tag CUIT de la ville est-il barre ? Oui s'il signe un gang, dans un ilot pris par un autre : rend
      { couleur (celle de qui tient l'ilot), tuiles (la longueur du trait) }, sinon null. */
  function barre(gr) {
    const p = B.partie;
    if (!p || !p.territoires || gr.motif === 1) return null;
    const signe = gangDuTag(gr.texte);
    if (!signe) return null;
    const i = ilotA(gr.x, gr.y);
    const tient = i && p.territoires[i.k];
    return tient && tient !== signe ? { couleur: bombeDe(tient), tuiles: gangDuTexte[gr.texte].tuiles } : null;
  }

  return { donnees, ilotA, tenuPar, force, horsJeu, gangA, couche, nuit, ligneDuClairon, couleurDe, nomDe,
           dessinerSurLaCarte, dessinerLaLegende, cle, tagsDeLaFrontiere, barre, gangDuTag, bombeDe };
})();
