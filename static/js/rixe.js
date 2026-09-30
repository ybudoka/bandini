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

  /** L'etat du combattant, cree au premier appel. `pret` est une ECHEANCE sur son horloge (`e.t`), pas un compte
      a rebours : `e.t` avance meme en plein geste, alors que le cerveau, lui, n'est pas appele pendant le coup —
      un compte a rebours ajoutait le geste a la cadence (70 images entre deux elans au lieu de 40).
      ⚠️ Elle part DECALEE a l'empreinte : six hommes nes a la meme image ont la meme horloge, et sans ce decalage
      ils frappent a la meme image. */
  function etat(e, f) {
    if (!e.rixe) {
      e.rixe = { cible: null, posture: 'approche', minuterie: 0, pret: e.t + hash2(e.id, 0x51C0) % f.cadence_images,
                 derive: 0, deriveT: 0, tourneT: tourneDe(e, f, 0), esquives: 0, vuArmer: false, coince: 0 };
    }
    return e.rixe;
  }

  /** Ceux qui visent la meme cible, ranges par identifiant : leur rang donne leur place sur le cercle. */
  function assaillants(cible, f) {
    return Entites.pietonsAutour(cible.x, cible.y, f.cercle_px * 8).filter(function (q) {
      return q.rixe && q.rixe.cible === cible && EN_COMBAT[q.etat];
    }).sort(function (a, b) { return a.id - b.id; });
  }

  function surLeCercle(cible, a, f) {
    return { x: cible.x + Math.cos(a) * f.cercle_px, y: cible.y + Math.sin(a) * f.cercle_px, a: a };
  }

  /** Sa place : une des `places` du cercle, a son rang. L'angle de depart est celui du PREMIER du rang, vu de
      la cible — le cercle se forme la ou ils sont, il ne les arrache pas de leur cote de la rue.
      ⚠️ ON NE COMPTE QUE LES PLACES LIBRES : une cible adossee a une facade n'a pas de place derriere elle, et
      celui qui y etait envoye cognait d'ou il etait — du meme cote que les autres (au banc, le joueur de depart
      est justement contre un mur). Les assaillants se repartissent donc sur ce qui reste, d'un bout a l'autre de
      l'arc : trois devant un mur s'ouvrent en eventail, pas en paquet sur un bord. */
  function place(e, cible, f) {
    const tous = assaillants(cible, f);
    const n = Math.max(1, tous.length), rang = Math.max(0, tous.indexOf(e));
    const tete = tous[0] || e;
    const base = angleVers(cible.x, cible.y, tete.x, tete.y);
    const libres = [];
    for (let k = 0; k < f.places; k++) {
      const a = base + k * 2 * Math.PI / f.places;
      if (!placeMuree(surLeCercle(cible, a, f))) libres.push(a);
    }
    if (!libres.length) return surLeCercle(cible, base + e.rixe.derive, f);
    // Le PREMIER garde la place d'ou il arrive (sinon, seul, il ferait le tour de sa cible pour rien) ; les
    // autres s'etalent a partir de lui — sur le tour entier s'il est libre, sur l'arc qui reste s'il y a un mur.
    const L = libres.length;
    const k = L === f.places ? Math.round(rang * L / n) : (n > 1 ? Math.round(rang * (L - 1) / (n - 1)) : 0);
    return surLeCercle(cible, libres[Math.min(L - 1, k)] + e.rixe.derive, f);
  }

  /** Ou marcher pour gagner sa place. ⚠️ EN CONTOURNANT : une place de l'autre cote de la cible, prise en ligne
      droite, passe A TRAVERS elle — on s'y cogne, et on reste du meme cote que les autres. On avance donc sur le
      cercle, d'au plus `contourne_rad` a la fois. */
  function etape(e, cible, p, f) {
    const ici = angleVers(cible.x, cible.y, e.x, e.y);
    const ecart = Math.atan2(Math.sin(p.a - ici), Math.cos(p.a - ici));
    if (Math.abs(ecart) <= f.contourne_rad) return p;
    return surLeCercle(cible, ici + Math.sign(ecart) * f.contourne_rad, f);
  }

  /** Sa place tombe-t-elle dans un mur (la cible y est adossee) ? Alors il cogne d'ou il est. */
  function placeMuree(p) {
    return !Monde.marchablePieton(Math.floor(p.x / TT), Math.floor(p.y / TT));
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
    // Sa cible bouge-t-elle ? Lu a SA POSITION d'une image a l'autre, pas a son `vx` (le joueur, un agent et
    // un passant ne l'ecrivent pas tous au meme moment).
    const bouge = r.cible === cible && Math.hypot(cible.x - r.cx, cible.y - r.cy) > f.bouge_px;
    r.cible = cible; r.cx = cible.x; r.cy = cible.y;
    // ⚠️ Il regarde SA CIBLE, meme en reculant : `majPieton` le tourne sinon dans le sens de son pas, et un
    // homme qui se degage tournerait le dos a celui qu'il vient de frapper. Deux images : ca s'eteint seul
    // quand le cerveau ne le mene plus.
    e.faceVers = cible; e.faceT = 2;
    const dx = cible.x - e.x, dy = cible.y - e.y, d = Math.hypot(dx, dy) || 1;
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
    const p = place(e, cible, f);
    const dp = Math.hypot(p.x - e.x, p.y - e.y);
    // COINCE : a portee, loin de sa place, et il n'en approche plus (des corps la tiennent — le demelage ne
    // laisse jamais deux corps sous 10 px). Au siege de m98, six allies et six Cravates autour de toi : les
    // Cravates attendaient une place qui ne se liberait jamais, et ne frappaient presque plus.
    r.coince = d <= f.portee_px && dp > f.place_px && r.dpAvant !== undefined && dp > r.dpAvant - 0.3 ? r.coince + 1 : 0;
    r.dpAvant = dp;
    // Il frappe DE SA PLACE — sinon, arrive du meme cote que les autres, il cognerait des qu'a portee et n'en
    // ferait jamais le tour. ⚠️ Sauf une place dans un mur (la cible y est adossee), ou une cible qui BOUGE : sa
    // place bouge avec elle, il ne l'atteignait presque jamais (au siege de m98, les allies tombaient de 47
    // coups a 18) — a portee, il frappe d'ou il est.
    if (d <= f.portee_px && e.t >= r.pret && (dp <= f.place_px || bouge || r.coince >= f.coince_images || placeMuree(p))) {
      e.vx = 0; e.vy = 0;
      if (Combat.frapper(e, false)) { r.pret = e.t + cadenceDe(e, f, e.t); reculer(r, f); return true; }
    }
    const vers = etape(e, cible, p, f);
    const px = vers.x - e.x, py = vers.y - e.y, dv = Math.hypot(px, py);
    if (dv > 2) {
      const allure = Math.min(1, dv / 12);          // il ralentit en arrivant : pas de va-et-vient sur sa place
      e.vx = px / dv * vitesse * allure;
      e.vy = py / dv * vitesse * allure;
    } else { e.vx = 0; e.vy = 0; }
    return false;
  }

  return { maj: maj, assaillants: assaillants };
})();
