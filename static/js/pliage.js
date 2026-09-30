/* Bandini — la carte pliée : la déplier en arrivant (docs/jalons/charger-les-districts-autour-du-joueur.md).

   La carte voyage EN COLONNES depuis le 30 sept. 2026 (`app/pliage.py`, qui dit le format) : son paquet
   touchait son plafond, et presque tout son poids venait de longues listes d'objets qui répètent leurs clés.
   `Jeu.chargerDefinitions` la déplie ICI, avant de la poser dans `defs.carte` — aucun lecteur de la carte
   ne sait qu'elle a été pliée, et la ville dépliée est celle de Python à l'octet près (les juges comparent
   le JSON).

   ⚠️ Une valeur qui n'est pas pliée revient telle quelle (copiée) : une carte déjà dépliée passe sans dommage. */

const Pliage = (function () {
  'use strict';

  //: Les lettres des palettes, comme `pliage.ALPHA` : l'ASCII de `#` à `~`, sans `"` ni `\`.
  const ALPHA = (function () {
    let s = '';
    for (let i = 35; i < 127; i++) { const c = String.fromCharCode(i); if (c !== '"' && c !== '\\') s += c; }
    return s;
  })();
  const RANG = {};
  for (let i = 0; i < ALPHA.length; i++) RANG[ALPHA[i]] = i;

  function cumuls(ecarts) {
    const valeurs = new Array(ecarts.length);
    let v = 0;
    for (let i = 0; i < ecarts.length; i++) { v += ecarts[i]; valeurs[i] = v; }
    return valeurs;
  }

  function colonne(c) {
    if (c.d) return cumuls(c.d);
    if (c.p) {
      const valeurs = new Array(c.s.length);
      for (let i = 0; i < c.s.length; i++) valeurs[i] = c.p[RANG[c.s[i]]];
      return valeurs;
    }
    return c.v.map(deplier);
  }

  function table(t) {
    const colonnes = {}, curseurs = {};
    Object.keys(t.c).forEach(function (cle) { colonnes[cle] = colonne(t.c[cle]); curseurs[cle] = 0; });
    const formes = t['~t'], objets = new Array(t.n);
    for (let i = 0; i < t.n; i++) {
      const forme = formes[t.f ? RANG[t.f[i]] : 0], o = {};
      for (let k = 0; k < forme.length; k++) { const cle = forme[k]; o[cle] = colonnes[cle][curseurs[cle]++]; }
      objets[i] = o;
    }
    return objets;
  }

  /** La valeur dépliée — le même travail que `pliage.deplier` côté Python. */
  function deplier(v) {
    if (Array.isArray(v)) return v.map(deplier);
    if (v === null || typeof v !== 'object') return v;
    if (v['~t']) return table(v);
    if (v['~p']) {
      const xs = cumuls(v['~p'][0]), ys = cumuls(v['~p'][1]);
      return xs.map(function (x, i) { return [x, ys[i]]; });
    }
    if (v['~xy']) {
      const xs = cumuls(v['~xy'][0]), ys = cumuls(v['~xy'][1]), valeurs = colonne(v.v), o = {};
      for (let i = 0; i < xs.length; i++) o[xs[i] + ',' + ys[i]] = valeurs[i];
      return o;
    }
    const o = {};
    Object.keys(v).forEach(function (cle) { o[cle] = deplier(v[cle]); });
    return o;
  }

  return { deplier: deplier, ALPHA: ALPHA };
})();
