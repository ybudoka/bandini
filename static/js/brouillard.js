/* Bandini — le brouillard de Baie-des-Brumes (docs/jalons/le-brouillard-de-baie-des-brumes.md).

   Certains matins, un brouillard roule de la baie : de l'aube a midi, on n'y voit plus a trois coins
   de rue, et la police non plus.

   ⚠️ PYTHON REGLE, ICI ON EMBRUME (`app/brouillard.py`, `B.defs.brouillard`). L'intensite est une
   fonction du jour et de l'heure (`intensiteA`) — la meme regle que la neige : rien a simuler, aucun
   de, et le meme brouillard le meme matin pour tout le monde.

   ⚠️ DERRIERE UNE OPTION (`B.options.brouillard`, NON par defaut). Sans elle, `intensite()` rend 0,
   et 0 ne change rien : la police voit comme avant, rien ne se peint, la corne se tait. La sonde du
   navigateur le mesure allume avant qu'on l'allume pour tout le monde. */

const Brouillard = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.brouillard; }

  /** Ce matin-la a-t-il son brouillard ? A l'empreinte du jour, jamais au de. */
  function matinDeBrouillard(jour) {
    const d = donnees();
    return !!d && hash2(jour, d.matins.sel) / 4294967296 < d.matins.chance;
  }

  /** Le brouillard ce jour-la, a cette heure (0 a 1 de la journee) : 0 rien, 1 plein. Pure. */
  function intensiteA(jour, heure) {
    const d = donnees();
    if (!d || !matinDeBrouillard(jour)) return 0;
    const m = d.matins, h = heure * 24;
    if (h < m.debut_h || h >= m.fin_h) return 0;
    if (h < m.plein_h) return (h - m.debut_h) / (m.plein_h - m.debut_h);
    if (h < m.leve_h) return 1;
    return (m.fin_h - h) / (m.fin_h - m.leve_h);
  }

  /** Plus epais pres de l'eau : 1 aux Quais et a La Pointe, `ailleurs` sinon. */
  function partDuQuartier(x, y) {
    const e = donnees().effets, z = Monde.carte && Monde.zoneA(x, y);
    return z && e.pres_de_l_eau.indexOf(z.district) >= 0 ? 1 : e.ailleurs;
  }

  /** Le brouillard, maintenant, la ou l'on est : 0 sans l'option, dedans, ou par temps clair. */
  function intensite() {
    const j = B.joueur;
    if (!B.options || !B.options.brouillard || !B.partie || B.interieur || !j) return 0;
    const i = intensiteA(B.partie.jour, B.partie.heure);
    return i ? i * partDuQuartier(j.x, j.y) : 0;
  }

  /** Ce qui reste de la vue de la police et des temoins, en part de leur portee (1 : tout). */
  function vision() {
    const i = intensite();
    return i ? 1 - (1 - donnees().effets.vision) * i : 1;
  }

  /** La veille d'un matin de brouillard, le Clairon l'annonce ; null sinon (ou sans l'option). */
  function annonceDeDemain() {
    const d = donnees(), p = B.partie;
    if (!d || !B.options || !B.options.brouillard || !p) return null;
    return matinDeBrouillard(p.jour + 1) ? d.annonce : null;
  }

  //: La derniere image ou la corne a sonne.
  let corneT = -Infinity;

  /** La corne du phare, a intervalles, tant que le brouillard est la. */
  function maj() {
    const i = intensite();
    if (!i) return;
    const e = donnees().effets;
    if (B.t - corneT < e.corne_s * 60) return;
    corneT = B.t;
    const phare = typeof Histoire !== 'undefined' && Histoire.lieu ? Histoire.lieu('phare') : null;
    if (phare) Son.SFX.corne(phare.x, phare.y, e.corne_portee_px);
  }

  /** Le voile : clair au milieu, epais aux bords. ⚠️ Un seul rectangle, et un degrade : c'est ce que
      la sonde du navigateur mesure. */
  function dessiner(ctx) {
    const i = intensite();
    if (!i) return;
    const e = donnees().effets, rayon = Math.hypot(VW, VH) / 2;
    const g = ctx.createRadialGradient(VW / 2, VH / 2, rayon * e.clair, VW / 2, VH / 2, rayon);
    g.addColorStop(0, 'rgba(214,220,226,' + (e.voile_centre * i).toFixed(3) + ')');
    g.addColorStop(1, 'rgba(214,220,226,' + (e.voile_bord * i).toFixed(3) + ')');
    ctx.fillStyle = 'rgba(214,220,226,' + (e.voile_centre * i).toFixed(3) + ')';
    ctx.fillRect(0, 0, VW, VH);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, VW, VH);
    B.stats.rects += 2;
  }

  function oublier() { corneT = -Infinity; }

  return { donnees, matinDeBrouillard, intensiteA, intensite, vision, annonceDeDemain, maj, dessiner, oublier };
})();
