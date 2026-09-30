/* Bandini — le cerveau d'un homme de gang qui se bat (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md).

   UN SEUL CERVEAU pour la rixe a la frontiere (sa cible : un rival) et pour le gang qui te tombe dessus (sa
   cible : toi). `entites.js` lui passe la main depuis `bagarre` et `attaque_joueur` ; il ne fait que DECIDER
   (`e.vx`, `e.vy`, `Combat.frapper`) — le pas se fait apres, comme pour tout le monde (`majPieton`).

   Vague 1, AU CONTACT : chacun prend SA place sur un cercle autour de la cible (son rang parmi ceux qui la
   visent), fait un pas de cote de temps en temps, recule apres son coup en lui faisant face, esquive parfois le
   coup qu'on arme contre lui, et frappe a SON rythme.

   ⚠️ AUCUN DE DU JEU : la place, le rythme et l'esquive se lisent a l'EMPREINTE (`hash2` de l'identifiant et de
   son horloge `e.t`), jamais par le generateur du jeu — un de tire ici decalerait tout le hasard de la ville (la
   lecon du char en panne ; un juge lit ce fichier et le refuse). */

const Rixe = (function () {
  'use strict';

  //: Ceux qui se battent, a cette image : les deux etats du cerveau, et le coup lui-meme (`Combat` ecrase l'etat
  //: par 'attaque' le temps des trois temps). ⚠️ Un homme qui est passe a `flane` garde son vieux `e.rixe` :
  //: sans ce filtre, il tiendrait encore une place dans le cercle d'une cible qu'il a quittee.
  const EN_COMBAT = { bagarre: true, attaque_joueur: true, attaque: true };

  function fiche() { return B.defs.rixes.contact; }

  /** Sa cadence a lui : la base de la fiche, plus ou moins `cadence_ecart`, a l'empreinte du coup `n`. */
  function cadenceDe(e, f, n) {
    return f.cadence_images + hash2(e.id, 0xCADE + n) % (2 * f.cadence_ecart + 1) - f.cadence_ecart;
  }

  /** L'attente avant son prochain pas de cote. */
  function tourneDe(e, f, n) {
    return f.tourne_min + hash2(e.id, 0x7042 + n) % (f.tourne_max - f.tourne_min + 1);
  }

  /** L'etat du combattant, cree au premier appel. ⚠️ `pret` part DECALE a l'empreinte : six hommes nes a la
      meme image ont la meme horloge, et sans ce decalage ils frappent a la meme image. */
  function etat(e, f) {
    if (!e.rixe) {
      e.rixe = { cible: null, posture: 'approche', minuterie: 0, pret: hash2(e.id, 0x51C0) % f.cadence_images,
                 derive: 0, deriveT: 0, tourneT: tourneDe(e, f, 0), esquives: 0, vuArmer: false };
    }
    return e.rixe;
  }

  /** Ceux qui visent la meme cible, ranges par identifiant : leur rang donne leur place sur le cercle. */
  function assaillants(cible, f) {
    return Entites.pietonsAutour(cible.x, cible.y, f.cercle_px * 8).filter(function (q) {
      return q.rixe && q.rixe.cible === cible && EN_COMBAT[q.etat];
    }).sort(function (a, b) { return a.id - b.id; });
  }

  /** Sa place : sur le cercle, a son rang. L'angle de depart est celui du PREMIER du rang, vu de la cible —
      le cercle se forme la ou ils sont, il ne les arrache pas de leur cote de la rue. */
  function place(e, cible, f) {
    const tous = assaillants(cible, f);
    const n = Math.max(1, tous.length), rang = Math.max(0, tous.indexOf(e));
    const tete = tous[0] || e;
    const a = angleVers(cible.x, cible.y, tete.x, tete.y) + rang * 2 * Math.PI / n + e.rixe.derive;
    return { x: cible.x + Math.cos(a) * f.cercle_px, y: cible.y + Math.sin(a) * f.cercle_px };
  }

  /** La cible arme un coup, a portee de lui : il se degage — une fois sur `esquive_pct`, et une seule decision
      par coup (`vuArmer` retombe quand la cible n'arme plus). */
  function esquive(e, cible, d, f) {
    const arme = cible.etat === 'attaque' && cible.phase === 'anticipation' && cible.arc;
    if (!arme) { e.rixe.vuArmer = false; return false; }
    if (e.rixe.vuArmer || d > (cible.arc.portee || 18) + f.esquive_marge_px) return false;
    e.rixe.vuArmer = true;
    if (hash2(e.id, e.t) % 100 >= f.esquive_pct) return false;
    e.rixe.esquives++;
    return true;
  }

  function reculer(r, f) { r.posture = 'recul'; r.minuterie = f.recul_images; }

  /** Une image de combat contre `cible`, a `vitesse` (celle de sa course). Rend vrai si un coup est parti. */
  function maj(e, cible, vitesse) {
    const f = fiche(), r = etat(e, f);
    r.cible = cible;
    // ⚠️ Il regarde SA CIBLE, meme en reculant : `majPieton` le tourne sinon dans le sens de son pas, et un
    // homme qui se degage tournerait le dos a celui qu'il vient de frapper. Deux images : ca s'eteint seul
    // quand le cerveau ne le mene plus.
    e.faceVers = cible; e.faceT = 2;
    const dx = cible.x - e.x, dy = cible.y - e.y, d = Math.hypot(dx, dy) || 1;
    if (r.pret > 0) r.pret--;
    if (r.posture !== 'recul' && esquive(e, cible, d, f)) reculer(r, f);
    if (r.posture === 'recul') {
      if (--r.minuterie <= 0) r.posture = 'approche';
      e.vx = -dx / d * vitesse * f.recul_allure;
      e.vy = -dy / d * vitesse * f.recul_allure;
      return false;
    }
    // Le pas de cote : il tourne autour de sa cible, de temps en temps, d'un cote ou de l'autre.
    if (--r.tourneT <= 0) {
      r.derive = (hash2(e.id, e.t) & 1 ? 1 : -1) * f.tourne_rad;
      r.deriveT = f.pas_images;
      r.tourneT = tourneDe(e, f, e.t);
    }
    if (r.deriveT > 0 && --r.deriveT === 0) r.derive = 0;
    // ⚠️ LA PORTEE PRIME SUR LA PLACE : sa place peut tomber dans un mur (la cible y est adossee) — a portee et
    // pret, il frappe d'ou il est.
    if (d <= f.portee_px && r.pret <= 0) {
      e.vx = 0; e.vy = 0;
      if (Combat.frapper(e, false)) { r.pret = cadenceDe(e, f, e.t); reculer(r, f); return true; }
    }
    const p = place(e, cible, f);
    const px = p.x - e.x, py = p.y - e.y, dp = Math.hypot(px, py);
    if (dp > 2) {
      const allure = Math.min(1, dp / 12);          // il ralentit en arrivant : pas de va-et-vient sur sa place
      e.vx = px / dp * vitesse * allure;
      e.vy = py / dp * vitesse * allure;
    } else { e.vx = 0; e.vy = 0; }
    return false;
  }

  return { maj: maj, assaillants: assaillants };
})();
