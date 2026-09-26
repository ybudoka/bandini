/* Bandini — la tempete de verglas (docs/jalons/la-tempete-de-verglas.md).

   Trois jours de glace : les chars glissent, des quartiers passent au noir, la police est debordee,
   et on livre des generatrices. Puis ca fond, et tout se rallume.

   ⚠️ PYTHON REGLE, ICI ON GIVRE (`app/verglas.py`, `B.defs.verglas`). L'intensite et les quartiers
   au noir sont des fonctions du jour et de l'heure (`intensiteA`, `quartiersNoirsA`) : rien a
   simuler, aucun de, rien a sauvegarder — et « tout se rallume apres » n'a rien a defaire.

   ⚠️ DERRIERE UNE OPTION (`B.options.verglas`, NON par defaut). Sans elle, `intensite()` rend 0, et
   0 ne change rien : chaque coefficient vaut 1, aucune lampe ne s'eteint, rien ne se peint. */

const Verglas = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.verglas; }

  /** Le jour de tempete : { tempete, k } (laquelle, et son k-ieme jour) — ou null. Pure. */
  function rangA(jour) {
    const d = donnees();
    if (!d) return null;
    const t = d.tempete;
    if (jour < t.premier) return null;
    const k = (jour - t.premier) % t.tous_les;
    return k < t.jours ? { tempete: Math.floor((jour - t.premier) / t.tous_les), k: k } : null;
  }

  /** La glace ce jour-la, a cette heure (0 a 1 de la journee) : 0 rien, 1 pleine. Pure. */
  function intensiteA(jour, heure) {
    const r = rangA(jour);
    if (!r) return 0;
    const t = donnees().tempete, h = heure * 24;
    if (r.k === 0 && h < t.arrive_h) return h / t.arrive_h;
    if (r.k === t.jours - 1 && h >= t.fond_h) return Math.max(0, (24 - h) / (24 - t.fond_h));
    return 1;
  }

  /** La glace, maintenant : 0 sans l'option, ou par beau temps. ⚠️ Pas de garde « dedans » : c'est
      la ville qui glisse, et une piece n'a ni chars ni lampes de rue. */
  function intensite() {
    if (!B.options || !B.options.verglas || !B.partie) return 0;
    return intensiteA(B.partie.jour, B.partie.heure);
  }

  /** Les quartiers sans courant ce jour-la (des slugs de district), a l'EMPREINTE de la tempete et
      du jour : les memes pour tout le monde. Pure. */
  function quartiersNoirsA(jour) {
    const r = rangA(jour);
    if (!r) return [];
    const d = donnees(), q = d.pannes.quartiers, n = d.pannes.par_jour[r.k] || 0;
    const cle = r.tempete * 7 + r.k;
    return q.map(function (s, i) { return { s: s, h: hash2(cle, i + d.tempete.sel) }; })
      .sort(function (a, b) { return a.h - b.h; }).slice(0, n).map(function (o) { return o.s; });
  }

  let noirsJour = null, noirs = null;
  /** Les quartiers au noir, maintenant (un Set, garde pour la journee). Vide sans la glace. */
  function quartiersNoirs() {
    if (!intensite()) return new Set();
    if (noirsJour !== B.partie.jour) { noirsJour = B.partie.jour; noirs = new Set(quartiersNoirsA(noirsJour)); }
    return noirs;
  }

  /** Le district d'un pixel de la ville (null hors de toute zone). */
  function districtA(x, y) {
    const z = Monde.carte && Monde.zoneA(x, y);
    return z ? z.district : null;
  }

  /** Cette lampe (`carte.lampes`, en pixels) est-elle dans un quartier au noir ? ⚠️ Son district se
      calcule UNE fois et se garde sur la lampe : 420 poteaux, et on les passe a chaque image. */
  function lampeAuNoir(l) {
    const n = quartiersNoirs();
    if (!n.size) return false;
    if (l.district === undefined) l.district = districtA(l.x, l.y);
    return n.has(l.district);
  }

  function auNoir(x, y) {
    const n = quartiersNoirs();
    return n.size > 0 && n.has(districtA(x, y));
  }

  function melange(base, i) { return 1 - (1 - base) * i; }
  function coefficient(cle) {
    const i = intensite();
    return i ? melange(donnees().effets[cle], i) : 1;
  }

  /** Ce que la glace laisse de l'adherence d'un char, de son freinage ; la vitesse du trafic. */
  function adherence() { return coefficient('adherence'); }
  function frein() { return coefficient('frein'); }
  function vitesseTrafic() { return coefficient('vitesse_trafic'); }

  /** La police debordee : sa vue (en part), et ses delais (en multiple). */
  function vision() { return coefficient('vision_police'); }
  function retardPolice() {
    const i = intensite();
    return i ? 1 + (donnees().effets.retard_police - 1) * i : 1;
  }

  /** La nuit, dans un quartier au noir, est plus noire : l'ambiance de la camera. */
  function ambiance(a) {
    if (!a || a.alpha < 0.2 || B.interieur || !B.cam) return a;
    if (!auNoir(B.cam.x + VW / 2, B.cam.y + VH / 2)) return a;
    return { teinte: a.teinte, alpha: Math.min(0.95, a.alpha + donnees().effets.nuit_noire * intensite()) };
  }

  //: Une branche cassee, trois dessins (a l'empreinte de la tuile).
  const BRANCHES = [
    ['............', '..b.........', '...bb....b..', '.....bbbbb..', '...bb..b....', '..b.....b...'],
    ['............', '.........b..', '..b....bb...', '...bbbbb....', '....b...bb..', '...b........'],
    ['............', '....b.......', '.....b..b...', '..bbbbbbbb..', '.b....b.....', '......b.....'],
  ];
  function peindreBranche(v) {
    return function (ctx) {
      const m = BRANCHES[v];
      for (let y = 0; y < m.length; y++) {
        for (let x = 0; x < m[y].length; x++) {
          if (m[y][x] !== 'b') continue;
          ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fillRect(x + 2, y + 7, 1, 1);          // son ombre
          ctx.fillStyle = '#3d2a1b'; ctx.fillRect(x + 2, y + 5, 1, 2);
          ctx.fillStyle = 'rgba(225,240,255,0.9)'; ctx.fillRect(x + 2, y + 4, 1, 1);   // la gaine de glace
        }
      }
    };
  }

  /** La glace au sol : un reflet bleute, la chaussee vernie, des eclats qui scintillent sur la chaussee, des branches
      cassees sur les trottoirs. ⚠️ Tout a l'empreinte de la tuile et de l'image : aucun etat, aucun
      de, aucune entite (une branche ne bloque rien et ne prend pas d'identifiant). */
  function dessinerSol(ctx, cam) {
    const i = intensite();
    if (!i || B.interieur) return;
    const c = Monde.carte, e = donnees().effets;
    ctx.fillStyle = 'rgba(190,220,255,' + (e.reflet * i).toFixed(3) + ')';
    ctx.fillRect(0, 0, VW, VH);
    const x0 = Math.max(0, Math.floor(cam.x / TT)), y0 = Math.max(0, Math.floor(cam.y / TT));
    const x1 = Math.min(c.w - 1, Math.ceil((cam.x + VW) / TT)), y1 = Math.min(c.h - 1, Math.ceil((cam.y + VH) / TT));
    const battement = Math.floor(B.t / 8);
    let n = 1;
    // Le vernis : la chaussee glacee, par bandes (une par rangee de tuiles glacees qui se suivent).
    ctx.fillStyle = 'rgba(175,210,245,' + (e.vernis * i).toFixed(3) + ')';
    for (let ty = y0; ty <= y1; ty++) {
      let debut = -1;
      for (let tx = x0; tx <= x1 + 1; tx++) {
        const glace = tx <= x1 && Monde.estChaussee(tx, ty);
        if (glace && debut < 0) debut = tx;
        if (!glace && debut >= 0) {
          ctx.fillRect(Math.round(debut * TT - cam.x), Math.round(ty * TT - cam.y), (tx - debut) * TT, TT);
          n++;
          debut = -1;
        }
      }
    }
    for (let ty = y0; ty <= y1; ty++) {
      for (let tx = x0; tx <= x1; tx++) {
        const h = hash2(tx, ty + 0x61ACE);
        if (h % e.eclats_une_sur === 0 && Monde.estChaussee(tx, ty)) {
          if ((battement + (h >>> 8)) % 3 === 0) {
            ctx.fillStyle = 'rgba(255,255,255,0.9)';
            const px = Math.round(tx * TT - cam.x) + ((h >>> 4) % 12) + 2, py = Math.round(ty * TT - cam.y) + ((h >>> 12) % 12) + 2;
            ctx.fillRect(px, py, 1, 1); ctx.fillRect(px - 1, py, 3, 1); ctx.fillRect(px, py - 1, 1, 3);
            n++;
          }
        } else if (h % e.branches_une_sur === 1 && Monde.estTrottoir(tx, ty)) {
          const v = (h >>> 16) % BRANCHES.length;
          ctx.drawImage(Atlas.cuirePeintre('branche|' + v, TT, TT, peindreBranche(v)), Math.round(tx * TT - cam.x), Math.round(ty * TT - cam.y));
          B.stats.images = (B.stats.images || 0) + 1;
        }
      }
    }
    B.stats.rects += n;
  }

  /** Ce que le Clairon ecrit ce matin : l'annonce la veille, les quartiers au noir pendant. */
  function ligneDuClairon() {
    const d = donnees(), p = B.partie;
    if (!d || !B.options || !B.options.verglas || !p) return null;
    const r = rangA(p.jour);
    if (!r) return rangA(p.jour + 1) && rangA(p.jour + 1).k === 0 ? d.clairon.veille : null;
    const noms = quartiersNoirsA(p.jour).map(function (s) {
      const z = Monde.carte && Monde.carte.zones.find(function (q) { return q.district === s && q.slug === s; });
      return (z ? z.nom : s).toUpperCase();
    });
    if (!noms.length) return null;
    const liste = noms.length > 1 ? noms.slice(0, -1).join(', ') + ' ET ' + noms[noms.length - 1] : noms[0];
    return d.clairon.pendant.replace('{quartiers}', liste);
  }

  function oublier() { noirsJour = null; noirs = null; }

  return { donnees, rangA, intensiteA, intensite, quartiersNoirsA, quartiersNoirs, lampeAuNoir, auNoir,
           adherence, frein, vitesseTrafic, vision, retardPolice, ambiance, dessinerSol, ligneDuClairon, oublier };
})();
