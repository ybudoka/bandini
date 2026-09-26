/* Bandini — le temps des Fetes (docs/jalons/le-temps-des-fetes.md).

   En decembre (`Calendrier`), la ville s'allume : les fenetres et les vitrines prennent les couleurs des
   guirlandes la nuit, un grand sapin brille sur la place du Faubourg, et on livre des dindes en camion.

   ⚠️ RIEN DE POSE : les guirlandes sont la COULEUR des lampes qui existent (`Monde.lampesVisibles` la
   demande ici), a l'empreinte de chaque lampe ; le sapin est PEINT. Rien ne bouche une porte, rien ne
   reste en janvier — une pure fonction du jour. */

const Fetes = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.fetes; }

  function actifA(jour) {
    const d = donnees();
    return !!(d && typeof Calendrier !== 'undefined' && d.jours.indexOf(Calendrier.jourDeLAnnee(jour)) >= 0);
  }
  function actif() { return !!B.partie && actifA(B.partie.jour); }

  /** La couleur de guirlande d'une lampe (une fenetre, une vitrine), ou null : a l'empreinte de sa tuile,
      et qui clignote doucement (une ampoule sur quatre, a son tour). */
  function couleur(l) {
    const d = donnees();
    if (!actif() || !l || !l.sorte || d.guirlandes.sortes.indexOf(l.sorte) < 0) return null;
    const h = hash2(l.tx || 0, (l.ty || 0) + 0xF37E), cs = d.guirlandes.couleurs;
    const c = cs[(h + (Math.floor(B.t / 40) % 4 === (h % 4) ? 1 : 0)) % cs.length];
    return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + d.guirlandes.force + ')';
  }

  /** Le sapin de la place : deux tuiles de haut, ses boules qui clignotent, l'etoile au bout. */
  function dessinerSapin(ctx, cam) {
    const d = donnees();
    if (!actif() || !d.sapin || B.interieur) return;
    const x = Math.round(d.sapin.x * TT + 8 - cam.x), y = Math.round(d.sapin.y * TT + 14 - cam.y);
    if (x < -30 || y < -50 || x > VW + 30 || y > VH + 30) return;
    ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fillRect(x - 12, y - 1, 24, 4);
    ctx.fillStyle = '#5a3a22'; ctx.fillRect(x - 2, y - 6, 4, 6);
    const etages = [[14, 0], [11, 8], [8, 16], [5, 23]];
    for (const e of etages) { ctx.fillStyle = '#1f6b3a'; ctx.fillRect(x - e[0], y - 12 - e[1], e[0] * 2, 9); }
    ctx.fillStyle = '#185a30'; for (const e of etages) ctx.fillRect(x - e[0], y - 5 - e[1], e[0] * 2, 2);
    const cs = d.guirlandes.couleurs;
    for (let k = 0; k < 14; k++) {
      const h = hash2(k, 0xF37E), e = etages[k % etages.length];
      const bx = x - e[0] + 2 + (h % (e[0] * 2 - 3)), by = y - 11 - e[1] + ((h >>> 5) % 7);
      const allume = (Math.floor(B.t / 20) + k) % 3 !== 0, c = cs[k % cs.length];
      ctx.fillStyle = allume ? 'rgb(' + c[0] + ',' + c[1] + ',' + c[2] + ')' : '#2a2a30';
      ctx.fillRect(bx, by, 2, 2);
    }
    ctx.fillStyle = '#ffd23f'; ctx.fillRect(x - 1, y - 40, 3, 3); ctx.fillRect(x - 3, y - 39, 7, 1); ctx.fillRect(x, y - 42, 1, 7);
    B.stats.rects += 30;
  }

  /** La lueur du sapin, la nuit. */
  function lampes(cam) {
    const d = donnees();
    if (!actif() || !d.sapin || B.interieur) return [];
    return [{ x: d.sapin.x * TT + 8 - cam.x, y: d.sapin.y * TT - 6 - cam.y, r: 70, c: 'rgba(255,214,130,0.5)' }];
  }

  /** Le Clairon du premier matin de decembre. */
  function ligneDuClairon() {
    const d = donnees(), p = B.partie;
    if (!d || !p || !actifA(p.jour) || actifA(p.jour - 1)) return null;
    return d.clairon;
  }

  return { donnees, actifA, actif, couleur, dessinerSapin, lampes, ligneDuClairon };
})();
