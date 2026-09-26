/* Bandini — la nuit aux Galeries de la Baie, le centre d'achat hante (docs/jalons/le-centre-d-achat-hante.md).

   Un bloc de carte (`app/blocs/galeries.py`) et sa grande piece. Le jour, un centre d'achat ordinaire.
   LA NUIT, il est vide (`vide_la_nuit`) et il ne dort pas : les lumieres s'eteignent une a une, la voix
   au haut-parleur sait ou tu es (la fontaine, l'escalier roulant, le rayon 4), un gardien qui n'est
   peut-etre pas un gardien se montre au loin et s'evanouit quand on approche, et quelqu'un a oublie
   quelque chose sur l'etagere du fond. Drole d'abord, inquietant ensuite, jamais gore.

   ⚠️ RIEN AU DE : le gardien se montre a des places ecrites, l'une apres l'autre ; tout le reste est
   une affaire d'heure et de distance. La voix a sa banque (`galeries`, une serie du paquet). */

const Galeries = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.galeries; }
  function ici() { return !!(B.interieur && B.interieur.slug === 'galeries'); }
  function nuit() { return !!B.partie && Monde.estNuit(B.partie.heure); }

  //: Les places ou le gardien se montre, en tuiles de la piece (loin les unes des autres).
  const POSTES = [[21, 8], [12, 2], [2, 5], [21, 2], [12, 8], [6, 6]];
  //: Les coins que la voix « voit » : (x0, y0, x1, y1) en tuiles, et ce qu'elle en dit.
  const COINS = [{ cle: 'fontaine', r: [14, 2, 17, 5] }, { cle: 'escalier', r: [8, 2, 11, 5] }, { cle: 'rayon', r: [1, 7, 4, 9] }];

  //: L'etat d'une visite de nuit (null dehors, ou le jour).
  let visite = null;

  function dire(cle) {
    if (!visite || visite.dits[cle]) return;
    visite.dits[cle] = true;
    Son.Voix.chargerHistoire('galeries');
    Son.Voix.parler('galeries-' + cle, {});
    const texte = donnees().annonces[cle];
    if (texte) Hud.message('« ' + texte.toUpperCase() + ' »', 240);
  }

  function tuile(q) { return { x: Math.floor(q.x / TT), y: Math.floor(q.y / TT) }; }

  function maj() {
    if (!ici() || !nuit() || !donnees()) { visite = null; return; }
    const h = donnees().hantise, j = B.joueur;
    if (!visite) {
      visite = { t: 0, eteintes: 0, dits: {}, gardien: null, poste: 0, revient: 0, pres: false };
      dire('entree');
    }
    visite.t++;
    // Les lumieres, une a une.
    if (visite.eteintes < h.lumieres && visite.t >= (visite.eteintes + 1) * h.lumiere_s * 60) {
      visite.eteintes++;
      Son.SFX.interrupteur();
      if (visite.eteintes === 1) dire('lumiere');
      else if (visite.eteintes === 3) { visite.dits.lumiere_2 = false; dire('lumiere_2'); }
    }
    // Les coins qu'elle voit.
    const t = tuile(j);
    for (const c of COINS) if (t.x >= c.r[0] && t.x <= c.r[2] && t.y >= c.r[1] && t.y <= c.r[3]) dire(c.cle);
    // Le gardien : des la deuxieme lumiere eteinte, a sa place ; il s'evanouit quand on s'approche, et
    // revient plus tard a la suivante.
    if (visite.eteintes >= 2) {
      if (visite.gardien) {
        if (Math.hypot(visite.gardien.x - j.x, visite.gardien.y - j.y) < h.gardien_px) {
          visite.gardien = null; visite.revient = h.gardien_revient_s * 60;
          dire('gardien');
        }
      } else if (--visite.revient <= 0) {
        for (let k = 0; k < POSTES.length; k++) {
          const p = POSTES[(visite.poste + k) % POSTES.length], x = p[0] * TT + 8, y = p[1] * TT + 8;
          if (Math.hypot(x - j.x, y - j.y) > h.gardien_px * 2.5) { visite.gardien = { x: x, y: y }; visite.poste += k + 1; break; }
        }
      }
    }
    // L'objet perdu du rayon 4, une fois par nuit.
    const o = B.interieur.trouvaille;
    if (o && B.partie.galeriesNuit !== B.partie.jour) {
      const pres = Math.hypot(o.x * TT + 8 - j.x, o.y * TT + 8 - j.y) < 20;
      if (pres && !visite.pres) Hud.message('QUELQUE CHOSE TRAÎNE SUR L\'ÉTAGÈRE… (ACTION)', 150);
      visite.pres = pres;
      if (pres && Entree.neuf('action')) {
        B.partie.galeriesNuit = B.partie.jour;
        Missions.encaisser(h.recompense, 'L\'ARTICLE PERDU');
        Hud.message(h.objet, 200);
        visite.dits.trouvaille = false; dire('trouvaille');
      }
    }
  }

  /** Le noir qui gagne, une lumiere a la fois — sauf un halo autour du joueur — et le gardien dedans.
      ⚠️ Par-dessus la scene (`Base.ecran()`, apres `Base.fin`) : dans une piece, il n'y a pas de nuit. */
  function dessiner(ctx, vue) {
    if (!visite || !ici()) return;
    const h = donnees().hantise, a = Math.min(0.85, visite.eteintes / h.lumieres * 0.85);
    const j = B.joueur, px = j.x - vue.x, py = j.y - vue.y;
    if (a > 0) {
      const g = ctx.createRadialGradient(px, py, 18, px, py, 90);
      g.addColorStop(0, 'rgba(4,4,10,0)');
      g.addColorStop(1, 'rgba(4,4,10,' + a.toFixed(2) + ')');
      ctx.fillStyle = g; ctx.fillRect(0, 0, VW, VH);
    }
    const q = visite.gardien;
    if (q) {
      // Le gardien : une silhouette grise, la casquette, et le rond de sa lampe de poche devant lui.
      const x = Math.round(q.x - vue.x), y = Math.round(q.y - vue.y);
      ctx.fillStyle = 'rgba(255,245,200,0.18)'; ctx.fillRect(x - 10, y + 6, 20, 8);
      ctx.fillStyle = '#6b6f78'; ctx.fillRect(x - 3, y - 9, 6, 11);
      ctx.fillStyle = '#2a2d34'; ctx.fillRect(x - 3, y + 2, 2, 5); ctx.fillRect(x + 1, y + 2, 2, 5);
      ctx.fillStyle = '#c9c3b6'; ctx.fillRect(x - 2, y - 13, 4, 4);
      ctx.fillStyle = '#1e2230'; ctx.fillRect(x - 3, y - 14, 6, 2);
      ctx.fillStyle = '#f5e7a0'; ctx.fillRect(x + 3, y - 3, 2, 2);
      B.stats.rects += 8;
    }
  }

  return { donnees, ici, nuit, maj, dessiner, POSTES, get visite() { return visite; } };
})();
