/* Bandini — les saisons de la ville (docs/jalons/les-quatre-saisons-realistes.md, lot 1).

   La palette du moment : le gazon, la friche, les arbres, la neige qui tient sur les trottoirs et
   les toits. ⚠️ UNE PURE FONCTION DU JOUR ET DE L'HEURE (`app/saisons.py` donne les palettes et les
   images-cles) : aucun de, rien a sauvegarder, la meme ville pour tout le monde.

   ⚠️ HUIT PALIERS PAR TRANSITION : la couleur ne glisse pas a chaque image, elle saute d'un palier
   a l'autre. C'est le palier (`cle`) qui fait repeindre les tuiles cuites et les morceaux
   (`Monde.dessinerSol`) : une repeinte toutes les deux minutes pendant une transition, jamais le
   reste du temps — le rythme sur le telephone.

   ⚠️ LA LUMIERE EST POUR LES YEUX (`heureDeLumiere`) : les regles gardent l'horloge fixe de
   `Monde.ambiance`. */

const Saisons = (function () {
  'use strict';

  //: La neige qui tient, sur un trottoir ou un toit.
  const BLANC = [238, 242, 246];

  function donnees() { return B.defs && B.defs.saisons; }

  function rgb(c) { return [parseInt(c.substr(1, 2), 16), parseInt(c.substr(3, 2), 16), parseInt(c.substr(5, 2), 16)]; }
  function hex(v) { return '#' + v.map(function (x) { return ('0' + Math.round(x).toString(16)).slice(-2); }).join(''); }
  function meler(a, b, t) { const x = rgb(a), y = rgb(b); return hex(x.map(function (v, i) { return v + (y[i] - v) * t; })); }

  /** Mele deux valeurs de palette de meme forme : couleurs, nombres, tableaux, objets. */
  function melerTout(a, b, t) {
    if (typeof a === 'string') return t === 0 ? a : meler(a, b, t);
    if (typeof a === 'number') return a + (b - a) * t;
    if (Array.isArray(a)) return a.map(function (v, i) { return melerTout(v, b[i], t); });
    const o = {};
    for (const k in a) o[k] = melerTout(a[k], b[k], t);
    return o;
  }

  /** Ou en est l'annee : { de, vers, palier } — `palier` de 0 a paliers-1 dans une transition. */
  function position(jour, heure) {
    const d = donnees(), x = Calendrier.jourDeLAnnee(jour) + (heure || 0);
    const cles = d.cles;
    for (let i = 0; i < cles.length - 1; i++) {
      const a = cles[i], b = cles[i + 1];
      if (x >= a[0] && x < b[0]) {
        if (a[1] === b[1]) return { de: a[1], vers: a[1], palier: 0 };
        return { de: a[1], vers: b[1], palier: Math.floor((x - a[0]) / (b[0] - a[0]) * d.paliers) };
      }
    }
    return { de: cles[0][1], vers: cles[0][1], palier: 0 };
  }

  function cleA(jour, heure) {
    const p = position(jour, heure);
    return p.de === p.vers ? p.de : p.de + '>' + p.vers + ':' + p.palier;
  }

  const memo = new Map();
  function paletteA(jour, heure) {
    const d = donnees(), cle = cleA(jour, heure);
    if (memo.has(cle)) return memo.get(cle);
    const p = position(jour, heure);
    const pal = melerTout(d.palettes[p.de], d.palettes[p.vers], p.palier / d.paliers);
    memo.set(cle, pal);
    return pal;
  }

  function maintenant() { return B.partie ? [B.partie.jour, B.partie.heure] : [21, 0.5]; }
  function palette() { const m = maintenant(); return paletteA(m[0], m[1]); }
  function cle() { const m = maintenant(); return cleA(m[0], m[1]); }

  /** Le style d'un trottoir ou d'un toit sous la neige qui tient : chaque couleur melee au blanc
      de `palette().neige`. Le meme objet tant que la cle ne change pas (les peintres le lisent a
      chaque tuile cuite). */
  const neiges = new Map();
  function enneiger(style) {
    const n = palette().neige;
    if (!n) return style;
    const k = cle();
    let parStyle = neiges.get(k);
    if (!parStyle) { parStyle = new Map(); neiges.set(k, parStyle); }
    if (parStyle.has(style)) return parStyle.get(style);
    const o = {};
    for (const c in style) o[c] = typeof style[c] === 'string' && style[c][0] === '#' ? meler(style[c], hex(BLANC), n) : style[c];
    parStyle.set(style, o);
    return o;
  }

  /** L'hiver, pour ce qui s'habille : tant que la neige tient (`palette().neige`, de decembre au
      degel de la fin mars). ⚠️ Pas le mois du calendrier : ce qu'on voit au sol et sur les chars
      doit dire la meme chose — une capote relevee sur une rue sans neige ne se comprend pas. */
  function enHiver() {
    return !!(donnees() && palette().neige > 0);
  }

  /** LA FICHE DU MOMENT (docs/jalons/les-decapotables-l-hiver.md) : une fiche peut porter sa
      version d'hiver (`fiche.hiver` : la capote relevee de la decapotable, la tuque de la
      conductrice). Rend [nom, fiche] — le NOM change avec elle, sinon le cache de l'atlas
      rendrait l'image d'ete sous la cle d'ete. */
  function ficheDuMoment(nom, fiche) {
    if (fiche && fiche.hiver && enHiver()) return [nom + '~hiver', fiche.hiver];
    return [nom, fiche];
  }

  /** L'heure DE LUMIERE : l'heure de l'horloge fixe (`Monde.TEINTES`) qui a la meme lumiere que
      `heure` ce jour-la. Le jour reel (lever -> coucher, qui suivent l'annee) est etire sur le jour
      de reference (7 h 12 -> 19 h 12), la nuit reelle sur la nuit de reference. Pure et continue :
      l'annee glisse avec `jour + heure`, sans saut a minuit. */
  function heureDeLumiere(jour, heure) {
    const d = donnees();
    if (!d) return heure;
    const l = d.lumiere, x = Calendrier.jourDeLAnnee(jour) + heure;
    const c = Math.cos(2 * Math.PI * (x - l.solstice_ete) / d.annee);
    const lever = l.lever[0] + l.lever[1] * c, coucher = l.coucher[0] + l.coucher[1] * c;
    const rl = l.reference[0], rc = l.reference[1], h = heure * 24;
    let r;
    if (h >= lever && h <= coucher) r = rl + (h - lever) / (coucher - lever) * (rc - rl);
    else {
      const depuis = h > coucher ? h - coucher : h + 24 - coucher, nuit = 24 - (coucher - lever);
      r = rc + depuis / nuit * (24 - (rc - rl));
    }
    return (r % 24) / 24;
  }

  return { paletteA, cleA, palette, cle, enneiger, enHiver, ficheDuMoment, heureDeLumiere };
})();
