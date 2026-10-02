/* Bandini — ce qu'on lit dans la rue : la plaque d'un coin, et les panneaux drôles (le décor, les bêtes
   et les gens répondent, deuxième vague, 2 oct. 2026).

   Tranché par Martin : « ACTION sous une plaque de rue dit l'adresse », et « des panneaux drôles écrits
   à lire en ville, un ou deux par district, posés sans dé, et lisibles au bouton ».

   ⚠️ **RIEN NE NAÎT ICI.** La plaque est peinte sur un poteau qui existait déjà — celui du panneau
   d'arrêt, ou le mât d'un feu, un par croisement (`Vehicules.creerSignalisation` le marque `plaque`) ;
   le panneau drôle est peint d'après la SUITE du paquet (`B.defs.panneaux`, `app/panneaux.py`, à sa
   place sur la ville finie) et ajouté au tri du dessin comme les braseros d'une place
   (`ajouterVisibles`). Aucune entité, aucun numéro : la suite des identifiants de la ville ne bouge
   pas. Un poteau mince n'arrête personne : la foule marche comme avant.

   ⚠️ **LE NOM D'UN COIN SE LIT SUR LA TRAME** (`carte.grille`, et `grille_nord` pour la bande du nord),
   avec la règle des arrêts d'autobus (`autobus.nom_de_coin`) : les avenues vont du nord au sud et se
   comptent d'ouest en est, les rues vont d'est en ouest et se comptent du nord au sud. Un juge compare
   les deux, arrêt par arrêt. Rien de neuf dans la carte.

   ⚠️ **ACTION LES LIT EN DERNIER**, avec le décor (`Interactions.decorSousLaMain`, le plus proche gagne) :
   le panneau d'un défi, plus haut dans la chaîne (`Missions.interagir`), garde son bouton. */

const Panneaux = (function () {
  'use strict';

  //: Le rang du tri au dessin (`Entites.dessiner`), à part de celui des entités et des braseros.
  const ID_TRI = 920000000;
  //: Le panneau drôle qu'on lit : son rang dans la suite -> la ligne qu'on lira à la prochaine pression.
  const lus = {};

  function cfg() { return B.defs && B.defs.interactions; }
  /** Les panneaux drôles : `[x, y, genre, lignes]` en tuiles — vide tant que la suite n'est pas là. */
  function liste() { return (B.defs && B.defs.panneaux) || []; }

  // --- Le nom d'un coin -------------------------------------------------------------------

  /** Le début et la fin de chaque rue d'une trame (rue, bloc, rue, bloc…) — `autobus._rues`. */
  function bandes(largeurs, blocs) {
    const out = [];
    let x = 0;
    for (let i = 0; i < largeurs.length; i++) {
      out.push([x, x + largeurs[i]]);
      x += largeurs[i] + (blocs[i] || 0);
    }
    return out;
  }

  /** La bande dont le milieu est le plus proche de `v` (la première, à égalité) — `la_plus_proche`. */
  function laPlusProche(b, v) {
    let meilleure = 0, ecart = Infinity;
    for (let i = 0; i < b.length; i++) {
      const e = Math.abs((b[i][0] + b[i][1] - 1) / 2 - v);
      if (e < ecart) { ecart = e; meilleure = i; }
    }
    return meilleure;
  }

  function ordinal(n) { return n === 1 ? '1re' : n + 'e'; }

  /** « 4e RUE », « 7e AVENUE » : le numéro de la rue et de l'avenue qui se croisent en (tx, ty). La bande
      du nord compte ses rues depuis la couture, vers le haut ; la couture elle-même est la 1re Rue. */
  function coin(tx, ty) {
    const ville = B.defs && B.defs.carte, c = cfg().plaque;
    if (!ville || !ville.grille) return null;
    const g = ville.grille, y0 = g.y0 || 0, gn = ville.grille_nord;
    const avenue = laPlusProche(bandes(g.rues_v, g.colonnes), tx) + 1;
    let rue = c.rue.replace('{n}', ordinal(laPlusProche(bandes(g.rues_h, g.rangees), ty - y0) + 1));
    if (ty < y0 && gn) {
      const b = bandes(gn.rues_h, gn.rangees), n = b.length - 1 - laPlusProche(b, ty - (gn.y0 || 0));
      rue = n > 0 ? c.rue_nord.replace('{n}', ordinal(n)) : c.rue.replace('{n}', ordinal(1));
    }
    return { rue: rue, avenue: c.avenue.replace('{n}', ordinal(avenue)) };
  }

  /** Ce qu'on lit sous la plaque d'un croisement : son coin, et son quartier. */
  function nomDuCroisement(inter) {
    const c = cfg().plaque;
    const tx = inter.x + (inter.l - 1) / 2, ty = inter.y + (inter.h - 1) / 2;
    const k = coin(tx, ty);
    if (!k) return null;
    const q = Reputation.quartierA(tx * TT + 8, ty * TT + 8);
    const d = q && ((B.defs.carte.districts || []).find(function (z) { return z.slug === q; }));
    const texte = c.coin.replace('{rue}', k.rue).replace('{avenue}', k.avenue);
    return d ? texte.replace('{quartier}', d.nom.toUpperCase()) : texte.replace(/ — \{quartier\}$/, '');
  }

  // --- Ce qui est sous la main ---------------------------------------------------------

  /** La plaque ou le panneau drôle qu'on regarde, le plus proche : `{ cible, d2, invite, plaque | panneau }`,
      ou null. */
  function sousLaMain(j) {
    const c = cfg();
    if (!c || !c.plaque || !Interactions.peutAgir(j)) return null;
    let mieux = null;
    const rp = c.plaque.portee_px;
    for (const e of Entites.autour(j.x, j.y, rp, function (q) { return q.plaque && q.inter; })) {
      const d2 = dist2(j.x, j.y, e.x, e.y);
      if ((!mieux || d2 < mieux.d2) && faceA(j, e.x, e.y)) mieux = { cible: e, d2: d2, invite: c.plaque.invite, plaque: true };
    }
    const r = c.panneau.portee_px;
    liste().forEach(function (p, i) {
      const x = p[0] * TT + 8, y = p[1] * TT + 15, d2 = dist2(j.x, j.y, x, y);
      if (d2 > r * r || (mieux && d2 >= mieux.d2) || !faceA(j, x, y)) return;
      mieux = { cible: { x: x, y: y }, d2: d2, invite: c.panneau.invite, panneau: i };
    });
    return mieux;
  }

  /** LIRE : le coin, d'un coup ; le panneau drôle, UNE ligne par pression — la suivante à la prochaine,
      et on recommence au bout (la plaque d'une statue, `Interactions.lire`). */
  function lire(j, lu) {
    const c = cfg();
    if (lu.plaque) {
      const nom = nomDuCroisement(lu.cible.inter);
      if (!nom) return false;
      Hud.message(nom, c.plaque.duree_images);
      Son.SFX.menu();
      return true;
    }
    const p = liste()[lu.panneau];
    if (!p || !p[3].length) return false;
    const i = (lus[lu.panneau] || 0) % p[3].length;
    lus[lu.panneau] = i + 1;
    Hud.message(p[3][i], c.panneau.duree_images);
    Son.SFX.menu();
    return true;
  }

  // --- Le dessin --------------------------------------------------------------------------

  /** La plaque bleue d'un coin : une lame, deux traits de lettres blanches. */
  function imagePlaque() {
    return Atlas.cuirePeintre('plaque_rue', 11, 4, function (ctx) {
      ctx.fillStyle = '#e8eef5'; ctx.fillRect(0, 0, 11, 4);
      ctx.fillStyle = '#1d4f91'; ctx.fillRect(1, 0, 9, 4); ctx.fillRect(0, 1, 11, 2);
      ctx.fillStyle = '#e8eef5'; ctx.fillRect(2, 1, 3, 1); ctx.fillRect(6, 1, 3, 1); ctx.fillRect(2, 2, 5, 1);
    });
  }

  /** Sur le poteau du panneau d'arrêt, PAR-DESSUS l'octogone ; sur le mât d'un feu, à mi-hauteur, du côté
      opposé au bras (la lame dépasse comme un drapeau). */
  function dessinerPlaque(ctx, e, cx, cy) {
    const img = imagePlaque();
    if (e.type === 'stop') {
      ctx.fillStyle = '#6f757c'; ctx.fillRect(Math.round(e.x - 1 - cx), Math.round(e.y - 23 - cy), 2, 2);
      ctx.drawImage(img, Math.round(e.x - 6 - cx), Math.round(e.y - 26 - cy));
    } else {
      ctx.drawImage(img, Math.round((e.bras > 0 ? e.x - 12 : e.x + 1) - cx), Math.round(e.y - 14 - cy));
    }
    B.stats.images++;
  }

  /** Le panneau drôle : la tôle blanche à bord rouge de la Ville (`ville`, 0), ou le contreplaqué peint à
      la main (`carton`, 1), sur son poteau. 16 × 22, le pied au milieu du bas. */
  function imagePanneau(genre) {
    return Atlas.cuirePeintre('panneau_drole|' + genre, 16, 22, function (ctx) {
      if (genre === 1) {
        ctx.fillStyle = '#5a3f25'; ctx.fillRect(7, 9, 2, 13);                       // le piquet de bois
        ctx.fillStyle = '#8a6438'; ctx.fillRect(0, 1, 16, 10);                      // le contreplaqué
        ctx.fillStyle = '#b08a55'; ctx.fillRect(1, 2, 14, 8);
        ctx.fillStyle = '#f2ede0';                                                  // les lettres au pinceau
        ctx.fillRect(2, 3, 5, 1); ctx.fillRect(8, 4, 5, 1); ctx.fillRect(3, 6, 9, 1); ctx.fillRect(2, 8, 4, 1); ctx.fillRect(7, 8, 6, 1);
        ctx.fillStyle = '#c0392b'; ctx.fillRect(13, 6, 1, 1);                       // le point d'exclamation
        ctx.fillRect(13, 3, 1, 2);
      } else {
        ctx.fillStyle = '#6f757c'; ctx.fillRect(7, 10, 2, 12);                      // le poteau de la Ville
        ctx.fillStyle = '#c0392b'; ctx.fillRect(1, 0, 14, 11);                      // le bord rouge
        ctx.fillStyle = '#f4f1e6'; ctx.fillRect(2, 1, 12, 9);                       // la tôle blanche
        ctx.fillStyle = '#26262a';                                                  // trois lignes de texte
        ctx.fillRect(3, 2, 10, 1); ctx.fillRect(4, 4, 8, 1); ctx.fillRect(3, 6, 10, 1); ctx.fillRect(5, 8, 6, 1);
      }
    });
  }

  /** Les panneaux drôles à l'écran, dans le tri du dessin (ils passent devant ou derrière un passant
      selon leur rangée, comme un poteau). */
  function ajouterVisibles(visibles, cx, cy) {
    liste().forEach(function (p, i) {
      const x = p[0] * TT + 8, y = p[1] * TT + 15;
      if (x < cx - 20 || x > cx + VW + 20 || y < cy - 10 || y > cy + VH + 30) return;
      visibles.push({ id: ID_TRI + i, vivant: true, x: x, y: y, peindreFoire: function (ctx) {
        ctx.drawImage(imagePanneau(p[2]), Math.round(x - 8 - cx), Math.round(y - 21 - cy));
        B.stats.images++;
      } });
    });
  }

  /** Une nouvelle partie relit ses panneaux depuis le début. */
  function oublier() { for (const k in lus) delete lus[k]; }

  return { coin, nomDuCroisement, sousLaMain, lire, dessinerPlaque, ajouterVisibles, oublier };
})();
