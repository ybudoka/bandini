/* Bandini — la réputation par quartier (docs/jalons/la-reputation-et-la-lecture-des-passants.md, vague 2).

   Tranché par Martin le 1er oct. 2026 : ce que chaque quartier pense de toi, de −100 à +100
   (`recherche.REPUTATION`), dans `partie.reputation` — sauvegardé avec la partie. Une mission réussie dans le
   quartier la monte, une petite job aussi ; un crime VU dans le quartier la descend selon sa gravité ; chaque
   matin elle revient un peu vers 0. On la lit au CARNET et sur la CARTE, en jauge.

   ⚠️ ELLE NE CHANGE QU'UNE CHOSE : LA DÉLATION (`denonce`). Bien vu, aucun passant du quartier ne devient
   témoin ; mal vu, tous ceux qui ont vu le deviennent ; entre les deux, le cœur de chacun, comme avant. Rien
   d'autre ne la lit (juge `test_reputation`) : ni un prix, ni une mission, ni le stool.

   ⚠️ RIEN AU DÉ. `denonce` reçoit le dé que l'appelant tirait déjà (`B.rng() < e.probaTemoin`) et le tire
   toujours, quelle que soit la réputation : la ville d'un joueur bien vu ne bascule pas dans un autre hasard. */

const Reputation = (function () {
  'use strict';

  //: Le dernier crime de chaque type qui a pesé, pour le répit du délit (`repit_s`).
  let derniers = {};

  function regle() { return (B.defs && B.defs.recherche && B.defs.recherche.reputation) || null; }

  /** Le quartier d'un point où se tient le joueur (ou ce qu'il voit) : dans une pièce, celui de la porte qu'on a
      passée ; dans un bloc, aucun. */
  function quartierA(x, y) {
    if (B.bloc) return null;
    if (B.interieur) {
      const porte = Monde.carte && Monde.carte.porte;
      if (!porte) return null;
      x = porte.x * TT + 8; y = porte.y * TT + 8;
    }
    return quartierDeLaVille(x, y);
  }

  /** Le quartier d'un point en coordonnées de la VILLE, où que soit le joueur. ⚠️ `B.defs.carte`, jamais
      `Monde.carte` : dans un bloc ou une pièce, `Monde.carte` n'est pas la ville. */
  function quartierDeLaVille(x, y) {
    const ville = B.defs && B.defs.carte;
    if (!ville) return null;
    let trouvee = null;
    for (const z of ville.zones || []) {
      if (x >= z.x * TT && x < (z.x + z.l) * TT && y >= z.y * TT && y < (z.y + z.h) * TT) trouvee = z;
    }
    return trouvee ? trouvee.district || trouvee.slug : null;
  }

  /** Les quartiers qui en ont une, dans l'ordre de la règle. */
  function quartiers() { const r = regle(); return r ? r.quartiers : []; }
  function compte(q) { return quartiers().indexOf(q) >= 0; }

  function de(q) { return (B.partie && B.partie.reputation && B.partie.reputation[q]) || 0; }

  /** 'bien', 'mal' ou 'neutre' : ce que le quartier fait de ce qu'il voit. */
  function etat(q) {
    const r = regle(), v = de(q);
    if (!r) return 'neutre';
    return v >= r.bien_vu ? 'bien' : v <= r.mal_vu ? 'mal' : 'neutre';
  }

  function changer(q, d) {
    const r = regle();
    if (!r || !compte(q) || !d || !B.partie) return;
    const p = B.partie.reputation || (B.partie.reputation = {});
    p[q] = Math.max(r.min, Math.min(r.max, (p[q] || 0) + d));
  }

  /** Un crime VU (par un agent ou un passant) au point (x, y) : le quartier s'en souvient, selon sa gravité.
      Le répit du délit vaut ici aussi — un carambolage est un délit, pas trois. */
  function crime(type, x, y) {
    const r = regle(), delit = B.defs.recherche.delits[type];
    if (!r || !delit) return;
    const dernier = derniers[type];
    if (delit.repit_s && dernier !== undefined && B.t - dernier >= 0 && B.t - dernier < delit.repit_s * 60) return;
    if (delit.repit_s) derniers[type] = B.t;
    changer(quartierA(x, y), -r.par_etoile * delit.etoiles);
  }

  /** Une mission réussie, une petite job : son quartier. */
  function mission(q) { const r = regle(); if (r) changer(q, r.mission); }
  function job(q) { const r = regle(); if (r) changer(q, r.job); }

  /** Le quartier d'une mission : celui de son donneur (là où il se tient en ville) ; pour une petite job, le
      district de la fiche, sinon celui du passant qui l'a demandée. À défaut (une voix au téléphone), celui où
      l'on se tient. */
  function quartierDeLaMission(m) {
    if (m.passant) {
      const f = Jobs.fiche(m), e = B.job && B.job.e;
      if (f && f.district) return f.district;
      if (e) return quartierDeLaVille(e.x, e.y);
    } else {
      const l = Histoire.lieuDuPersonnage(Chapitres.donneurDe(m));
      if (l) return quartierDeLaVille(l.x, l.y);
    }
    return B.joueur ? quartierA(B.joueur.x, B.joueur.y) : null;
  }

  /** `Histoire.reussir` : la mission (ou la petite job) vient de réussir. */
  function reussite(m) {
    const q = quartierDeLaMission(m);
    if (m.passant) job(q); else mission(q);
  }

  /** Chaque matin : un peu plus près de 0, dans un sens comme dans l'autre. */
  function nouveauJour() {
    const r = regle(), p = B.partie && B.partie.reputation;
    if (!r || !p) return;
    for (const q in p) p[q] = p[q] > 0 ? Math.max(0, p[q] - r.retour_par_jour) : Math.min(0, p[q] + r.retour_par_jour);
  }

  /** Ce passant, qui a vu un crime en (x, y), va-t-il te dénoncer ? `tirage` : le dé que l'appelant a DÉJÀ tiré
      (`B.rng()`), qu'on lit seulement entre les deux seuils. */
  function denonce(e, tirage, x, y) {
    // ⚠️ UN HOMME DE GANG NE PARLE PAS À LA POLICE, bien vu ou mal vu (son `temoin` est 0 au catalogue) : « mal vu,
    // tout le monde » envoyait le Cravate qu'on bat témoigner contre toi au lieu de se battre (1er oct. 2026, la
    // rixe : il n'esquivait plus un seul coup, 38 graines sur 40).
    if (e.gang) return false;
    const q = quartierA(x, y), et = q ? etat(q) : 'neutre';
    if (et === 'bien') return false;
    if (et === 'mal') return true;
    return tirage < e.probaTemoin;
  }

  /** La jauge : un trait de −100 à +100, le zéro au milieu, rempli de son côté. */
  function dessinerJauge(ctx, x, y, l, q) {
    const r = regle();
    if (!r) return;
    const v = de(q), milieu = x + Math.floor(l / 2);
    ctx.fillStyle = '#2a2a33';
    ctx.fillRect(x, y, l, 4);
    const w = Math.round(Math.abs(v) / r.max * (l / 2));
    ctx.fillStyle = v >= r.bien_vu ? '#5fd35f' : v <= r.mal_vu ? '#e0503c' : v > 0 ? '#9fcf6a' : '#d99a4a';
    if (v > 0) ctx.fillRect(milieu, y, w, 4);
    else if (v < 0) ctx.fillRect(milieu - w, y, w, 4);
    ctx.fillStyle = '#efe6d0';
    ctx.fillRect(milieu, y - 1, 1, 6);
  }

  /** Sur la CARTE de la ville : le nom de chaque quartier en haut de son rectangle, et sa jauge dessous. */
  function dessinerSurLaCarte(ctx, pos) {
    const ville = B.defs && B.defs.carte;
    if (!regle() || !ville) return;
    for (const z of ville.zones || []) {
      if (z.gang || z.district !== z.slug || !compte(z.slug)) continue;
      const a = pos(z.x * TT, z.y * TT), c = pos((z.x + z.l) * TT, (z.y + z.h) * TT);
      const nom = z.nom.toUpperCase(), l = 40, mx = Math.round((a.x + c.x) / 2);
      const w = Math.max(Atlas.largeurTexte(nom, 1), l) + 6;
      ctx.fillStyle = 'rgba(11,10,18,0.7)';
      ctx.fillRect(mx - Math.ceil(w / 2), a.y + 3, w, 15);
      Atlas.texte(ctx, nom, mx - Math.floor(Atlas.largeurTexte(nom, 1) / 2), a.y + 5, '#cdc6e6', 1);
      dessinerJauge(ctx, mx - l / 2, a.y + 12, l, z.slug);
    }
  }

  /** Une partie neuve : aucun répit en cours. */
  function oublier() { derniers = {}; }

  return { quartierA, quartierDeLaVille, quartiers, de, etat, changer, crime, mission, job, reussite, nouveauJour, denonce,
           dessinerJauge, dessinerSurLaCarte, oublier };
})();
