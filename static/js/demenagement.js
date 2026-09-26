/* Bandini — le 1er juillet, jour du demenagement (docs/jalons/le-1er-juillet-jour-du-demenagement.md).

   Le jour venu (`Calendrier.estLe('demenagement')`), des camions de demenagement a cheval sur le
   trottoir devant les maisons, des meubles sur le trottoir d'a cote, et le camion qui prend un boulot de
   plus (`Missions.boulotDuChar` : les boites de trois familles, sans une bosse).

   ⚠️ PYTHON DIT OU (`app/demenagement.py`, lu sur la ville finie, sans de). Ici, QUAND et comment :
   - les camions naissent A L'APPROCHE (la ville oublie ce qui est gare loin du joueur), d'une couleur
     donnee — `Vehicules.creer` ne tire alors aucun de —, et `resteGare` : un passant ne part pas avec ;
   - le lendemain, ils sont partis (sauf celui qu'on conduit : il est a nous) ;
   - les meubles sont PEINTS, ni entite ni obstacle. */

const Demenagement = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.demenagement; }

  /** Le jour du demenagement ? */
  function aujourdhui() {
    return !!(B.partie && donnees() && typeof Calendrier !== 'undefined' && Calendrier.estLe('demenagement', B.partie.jour));
  }

  //: Les camions des demenageurs : blancs, comme ceux qu'on loue (une couleur donnee : aucun de).
  const COULEUR = '#ecf0f1';
  //: A cette distance du joueur, un camion nait ; plus loin que `OUBLI_PX`, il s'en va.
  const NAISSANCE_PX = 520, OUBLI_PX = 900;

  function camions() { return B.entites.filter(function (e) { return e.type === 'vehicule' && e.demenageur !== undefined; }); }

  function maj() {
    if (B.t % 20 !== 0 || B.interieur) return;
    const d = donnees(), j = B.joueur;
    if (!d || !j) return;
    const ici = aujourdhui(), les = camions();
    for (const v of les) {
      if (v.conducteur === j) { delete v.demenageur; continue; }        // on l'a pris : il est a nous
      if (!ici || Math.hypot(v.x - j.x, v.y - j.y) > OUBLI_PX) Entites.retirer(v);
    }
    if (!ici) return;
    let neufs = 0;
    d.camions.forEach(function (c, k) {
      const x = c[0] * TT + 8, y = c[1] * TT + 8;
      if (Math.hypot(x - j.x, y - j.y) > NAISSANCE_PX) return;
      if (les.some(function (v) { return v.demenageur === k && B.entites.indexOf(v) >= 0; })) return;
      const v = Vehicules.creer('camion', x, y, 0, { etat: 'stationne', couleur: COULEUR });
      if (!v) return;
      v.demenageur = k; v.resteGare = true;
      neufs++;
    });
    if (neufs) Entites.indexer();
  }

  // --- Les meubles du trottoir (peints) ----------------------------------------------

  const PEINTRES = {
    sofa: function (ctx, x, y) {
      ctx.fillStyle = '#5a6b3a'; ctx.fillRect(x + 1, y + 5, 14, 8);
      ctx.fillStyle = '#6f8448'; ctx.fillRect(x + 1, y + 3, 14, 3); ctx.fillRect(x, y + 5, 2, 7); ctx.fillRect(x + 14, y + 5, 2, 7);
      ctx.fillStyle = '#4a5a30'; ctx.fillRect(x + 8, y + 6, 1, 6);
    },
    matelas: function (ctx, x, y) {
      ctx.fillStyle = '#e8e4d8'; ctx.fillRect(x + 1, y + 2, 14, 12);
      ctx.fillStyle = '#7fa6c9'; for (let k = 3; k < 14; k += 3) ctx.fillRect(x + 1, y + k, 14, 1);
      ctx.fillStyle = '#c8b88a'; ctx.fillRect(x + 4, y + 6, 3, 2);                       // la tache
    },
    boites: function (ctx, x, y) {
      ctx.fillStyle = '#b08a52'; ctx.fillRect(x + 1, y + 7, 7, 7); ctx.fillRect(x + 8, y + 8, 7, 6); ctx.fillRect(x + 3, y + 1, 7, 6);
      ctx.fillStyle = '#8a6a3a'; ctx.fillRect(x + 1, y + 10, 7, 1); ctx.fillRect(x + 8, y + 11, 7, 1); ctx.fillRect(x + 3, y + 4, 7, 1);
    },
    lampe: function (ctx, x, y) {
      ctx.fillStyle = '#3a3d44'; ctx.fillRect(x + 7, y + 4, 2, 10); ctx.fillRect(x + 5, y + 13, 6, 2);
      ctx.fillStyle = '#e8d8a0'; ctx.fillRect(x + 4, y, 8, 5);
    },
    frigo: function (ctx, x, y) {
      ctx.fillStyle = '#f2efe6'; ctx.fillRect(x + 3, y, 10, 15);
      ctx.fillStyle = '#b8b4aa'; ctx.fillRect(x + 3, y + 5, 10, 1); ctx.fillRect(x + 11, y + 2, 1, 2); ctx.fillRect(x + 11, y + 7, 1, 3);
    },
    chaise: function (ctx, x, y) {
      ctx.fillStyle = '#8a5a2a'; ctx.fillRect(x + 4, y + 2, 8, 2); ctx.fillRect(x + 4, y + 2, 2, 12); ctx.fillRect(x + 10, y + 7, 2, 7);
      ctx.fillRect(x + 4, y + 7, 8, 2);
    },
  };

  /** Les meubles, sous les gens. */
  function dessiner(ctx, vue) {
    if (B.interieur || !aujourdhui()) return;
    let n = 0;
    for (const m of donnees().meubles) {
      const x = Math.round(m[0] * TT - vue.x), y = Math.round(m[1] * TT - vue.y);
      if (x < -TT || y < -TT || x > VW || y > VH) continue;
      ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.fillRect(x + 1, y + 13, 14, 3);        // l'ombre
      (PEINTRES[m[2]] || PEINTRES.boites)(ctx, x, y);
      n += 6;
    }
    B.stats.rects += n;
  }

  /** Ce que le Clairon ecrit : la veille, et le matin du 1er juillet. */
  function ligneDuClairon() {
    const d = donnees(), p = B.partie;
    if (!d || !p || typeof Calendrier === 'undefined') return null;
    if (Calendrier.estLe('demenagement', p.jour + 1)) return d.clairon.veille;
    if (Calendrier.estLe('demenagement', p.jour)) return d.clairon.jour;
    return null;
  }

  return { donnees, aujourdhui, camions, maj, dessiner, ligneDuClairon, PEINTRES };
})();
