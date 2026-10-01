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
      // ⚠️ Le tireur n'est pas sur le cercle (il tient SA distance) : il n'y prend pas de place.
      return q.rixe && q.rixe.cible === cible && EN_COMBAT[q.etat] && !q.armeDeGang;
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
    r.vu = B.t;          // il est du combat en cours (`enDeroute` : un cadavre, lui, ne l'est plus)
    // Sa cible bouge-t-elle ? Lu a SA POSITION d'une image a l'autre, pas a son `vx` (le joueur, un agent et
    // un passant ne l'ecrivent pas tous au meme moment).
    const bouge = r.cible === cible && Math.hypot(cible.x - r.cx, cible.y - r.cy) > f.bouge_px;
    r.cible = cible; r.cx = cible.x; r.cy = cible.y;
    // ⚠️ Il regarde SA CIBLE, meme en reculant : `majPieton` le tourne sinon dans le sens de son pas, et un
    // homme qui se degage tournerait le dos a celui qu'il vient de frapper. Deux images : ca s'eteint seul
    // quand le cerveau ne le mene plus.
    e.faceVers = cible; e.faceT = 2;
    // LES RENFORTS (vague 4) : s'il perd, il crie, et des siens accourent ; LE MORAL (vague 3) : blesse au contact,
    // ou son camp a moitie a terre, il se sauve.
    appeler(e, cible);
    if (lache(e, cible)) return false;
    // L'ARME DE SON GANG (vague 2) : il la degaine au premier echange, et se bat en tireur ou en lanceur.
    if (armer(e)) return majTir(e, cible, vitesse, r);
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

  // --- Vague 2 : l'arsenal et la fusillade ----------------------------------------------------------------

  function tir() { return B.defs.rixes.tir; }

  // --- Vague 3 : le moral et les blesses ----------------------------------------------------------------------

  function moral() { return B.defs.rixes.moral; }

  /** Est-il BLESSE (sous `blesse_part` de sa vie) ? */
  function blesse(e) { return e.vie < e.vieMax * moral().blesse_part; }

  /** Ne lache jamais : il est la pour ca (un homme de mission, un allie), ou c'est l'ecole (un Mante). */
  function tenace(e) { return !!(e.cible || e.allie || e.personnage || e.techniques); }

  // --- Vague 4 : les renforts -------------------------------------------------------------------------------

  function renforts() { return B.defs.rixes.renforts; }

  /** Combien des siens sont a terre dans le combat en cours (le compte de `enDeroute`). */
  function aTerreDansSonCamp(e) {
    const M = moral();
    let n = 0;
    for (const q of Entites.autour(e.x, e.y, M.camp_px, function (c) { return c.type === 'pieton'; })) {
      if (q === e || q.gang !== e.gang || !q.rixe || !(B.t - q.rixe.vu <= M.camp_images)) continue;
      if (!q.vivant || q.etat === 'assomme') n++;
    }
    return n;
  }

  /** Une place pour les renforts : marchable, HORS DE L'ECRAN, a `distance_px` de lui, et a moins de
      `joueur_max_px` du JOUEUR (la bulle d'oubli : une rixe s'allume a 300-500 px de lui, et ses renforts naissaient
      au-dela — effaces a l'image meme). Cherchee dans l'ordre, jamais au de : d'abord la direction du joueur, puis de
      part et d'autre (seize directions, trois distances). */
  function placeDesRenforts(e) {
    const R = renforts(), d = R.distance_px, j = B.joueur, jmax2 = R.joueur_max_px * R.joueur_max_px;
    const a0 = j ? angleVers(e.x, e.y, j.x, j.y) : 0;
    for (let k = 0; k < 16; k++) {
      const a = a0 + (k % 2 ? 1 : -1) * Math.ceil(k / 2) * Math.PI / 8;
      for (const r of [d[0], (d[0] + d[1]) / 2, d[1]]) {
        const x = e.x + Math.cos(a) * r, y = e.y + Math.sin(a) * r;
        if (j && dist2(x, y, j.x, j.y) > jmax2) continue;
        if (Monde.marchablePieton(Math.floor(x / TT), Math.floor(y / TT)) && !Entites.visibleAEcran(x, y, 24)) {
          return { x: Math.floor(x / TT) * TT + 8, y: Math.floor(y / TT) * TT + 8 };
        }
      }
    }
    return null;
  }

  /** IL APPELLE LES SIENS, une fois (`e.appele`) : quand il perd — blesse, ou un des siens a terre. Jusqu'a
      `max_par_appel` des siens naissent hors de l'ecran (le plafond : `max_par_combat` renforts vivants de son gang
      a `zone_px`) et accourent — contre toi, ou dans la rixe, contre son rival. Une fois sur `en_char_sur`, un char
      aux couleurs du gang est gare sur la voie la plus proche : ils en descendent. ⚠️ Jamais un homme de mission,
      un allie, un Mante ; jamais dedans, ni pendant la paix du Boss. Rend le nombre de renforts. */
  function appeler(e, cible) {
    const R = renforts();
    if (e.appele || e.renfort || tenace(e) || e.mission || B.interieur || B.bloc || (B.partie && B.partie.boss) || !e.gang) return 0;
    // ⚠️ PENDANT UNE MISSION (un homme de mission debout), un membre ordinaire n'appelle pas non plus : ses renforts
    // changeaient la difficulte des missions reglee au banc (la relecture de la vague 4).
    if (B.mission && B.mission.entites && B.mission.entites.some(function (q) {
      return q.cible && q.vivant && q.etat !== 'assomme';
    })) return 0;
    if (!blesse(e) && !aTerreDansSonCamp(e)) return 0;
    e.appele = true;
    e.appelT = e.t;
    Entites.bulle(e, R.cris[hash2(e.id, e.t) % R.cris.length], { duree: 90 });
    // ⚠️ La grille est refaite a la fin de chaque appel (`Entites.indexer`) : un deuxieme appel a la meme image
    // compte les renforts du premier.
    const deja = Entites.autour(e.x, e.y, R.zone_px, function (q) {
      return q.type === 'pieton' && q.renfort && q.gang === e.gang && q.vivant;
    }).length;
    const n = Math.min(R.max_par_appel, R.max_par_combat - deja);
    const bande = ((B.defs.pietons && B.defs.pietons.gangs) || []).find(function (g) { return g.slug === e.gang; });
    const arch = bande && Entites.archetype(bande.pieton);
    let lieu = n > 0 && arch ? placeDesRenforts(e) : null;
    if (!lieu) return 0;
    if (hash2(e.id, 0xCA2) % R.en_char_sur === 0) {
      const rue = Monde.routeLaPlusProche(lieu.x, lieu.y, 4);
      if (rue && !Entites.visibleAEcran(rue.x, rue.y, 24)) {
        const v = Vehicules.creer('auto', rue.x, rue.y, angleVers(rue.x, rue.y, e.x, e.y),
                                  { etat: 'stationne', couleur: Territoires.couleurDe(e.gang) });
        if (v) v.renforts = true;
      }
    }
    // ⚠️ Une RIXE, c'est une cible qui n'est pas le joueur — pas `e.bagarre`, qui reste vrai apres la rixe : un
    // ancien rixeur qui t'attaquait appelait des renforts qui partaient frapper un passant de l'autre gang.
    const rixe = cible !== B.joueur;
    for (let i = 0; i < n; i++) {
      const q = Entites.creerPieton(lieu.x + (i - (n - 1) / 2) * 14, lieu.y, arch);
      if (!q) continue;
      q.renfort = true; q.metier = 'bagarre'; q.cri = 90;
      if (rixe) { q.bagarre = true; q.etat = 'bagarre'; q.bagarreT = e.bagarreT || 900; q.rival = cible; }
      else q.etat = 'attaque_joueur';
    }
    Entites.indexer();
    return n;
  }

  /** SON CAMP a-t-il perdu `deroute_part` des siens ? Les membres de son gang qui se sont battus (`e.rixe`), a
      `camp_px` — debout ou a terre, morts compris (`Entites.autour` les garde, pas `pietonsAutour`) — mais du
      combat EN COURS (`rixe.vu`, a `camp_images`) : un mort garde son `e.rixe` et reste dans la grille, et il
      mettait en deroute le premier Cravate frais venu t'attaquer a cote. */
  function enDeroute(e) {
    const M = moral();
    let total = 0, aTerre = 0;
    for (const q of Entites.autour(e.x, e.y, M.camp_px, function (c) { return c.type === 'pieton'; })) {
      if (q.gang !== e.gang || !q.rixe || !(B.t - q.rixe.vu <= M.camp_images)) continue;
      total++;
      if (!q.vivant || q.etat === 'assomme') aTerre++;
    }
    return total >= 2 && aTerre >= total * M.deroute_part;
  }

  /** Il lache le combat : il se sauve devant `cible`, en criant un mot de la fiche (a l'empreinte). */
  function sauver(e, cible, mots, boite) {
    e.etat = 'fuit'; e.menace = cible; e.minuterie = B.defs.pietons.reactions.fuite_secondes * 60; e.cri = 120;
    e.bagarre = false; e.rival = null; e.avantLeCoup = null;
    if (boite) e.boite = true;
    // Il vient d'appeler les siens (`appeler`) : c'est ce cri-la qu'on lit, pas celui de sa fuite.
    if (e.appelT !== e.t) Entites.bulle(e, mots[hash2(e.id, e.t) % mots.length], { duree: 90 });
  }

  /** LE MORAL. Rend vrai s'il lache le combat (il fuit, et le cerveau n'a plus rien a decider). Le tireur blesse,
      lui, ne lache pas : il recule au fond de sa fourchette (`majTir`). */
  function lache(e, cible) {
    if (tenace(e)) return false;
    const M = moral();
    if (enDeroute(e)) { sauver(e, cible, M.deroute_mots, blesse(e)); return true; }
    if (blesse(e) && !armer(e)) { sauver(e, cible, M.blesse_mots, true); return true; }
    return false;
  }

  /** L'ARME DE SON GANG, un sur `part_armee`, a l'empreinte de son identifiant : toujours le meme homme, toujours la
      meme arme (`armeDeGang`, qui la retient — `null` : il n'en a pas). Jamais un homme de mission (il garde l'arme
      que sa mission lui donne), un allie, ni un Mante (l'ecole, pas les balles). Rend vrai s'il l'a en main. */
  function armer(e) {
    if (e.armeDeGang !== undefined) return !!e.armeDeGang && e.arme === e.armeDeGang;
    const R = B.defs.rixes, slug = e.gang && R.arsenal[e.gang];
    const arme = !!slug && !e.cible && !e.personnage && !e.allie && !e.techniques
      && hash2(e.id, 0xA5E1) % R.part_armee === 0;
    e.armeDeGang = arme ? slug : null;
    if (arme) e.arme = slug;
    return arme;
  }

  /** Un ABRI : la tuile marchable la plus proche de lui (a `abri_tuiles` au plus) d'ou la cible NE LE VOIT PAS
      (`Monde.ligneLibre`), dans sa fourchette de distance (`fourchette` : celle du moment — blesse, il la veut plus
      loin). `null` s'il n'y en a pas. ⚠️ Parcours dans l'ordre des
      tuiles, jamais au de. */
  function abriPour(e, cible, fourchette) {
    const T = tir(), f = fourchette || T.distances[e.arme];
    if (!f) return null;
    const tx0 = Math.floor(e.x / TT), ty0 = Math.floor(e.y / TT), n = T.abri_tuiles;
    let meilleur = null, dMin = Infinity;
    for (let ty = ty0 - n; ty <= ty0 + n; ty++) {
      for (let tx = tx0 - n; tx <= tx0 + n; tx++) {
        if (!Monde.marchablePieton(tx, ty)) continue;
        const x = tx * TT + 8, y = ty * TT + 8, dc = Math.hypot(cible.x - x, cible.y - y);
        if (dc < f[0] || dc > f[1] + TT) continue;
        const d = dist2(x, y, e.x, e.y);
        if (d >= dMin || Monde.ligneLibre(x, y, cible.x, cible.y)) continue;
        dMin = d; meilleur = { x: x, y: y };
      }
    }
    return meilleur;
  }

  function marcher(e, vers, vitesse) {
    const dx = vers.x - e.x, dy = vers.y - e.y, d = Math.hypot(dx, dy);
    if (d <= 3) { e.vx = 0; e.vy = 0; return; }
    e.vx = dx / d * vitesse; e.vy = dy / d * vitesse;
  }

  /** Il tient sa fourchette : il recule si la cible est trop pres, avance si elle est trop loin — ou s'il ne la
      voit pas. Rend vrai s'il est en place, la cible en vue. */
  function tenirSaDistance(e, cible, f, vitesse) {
    const dx = cible.x - e.x, dy = cible.y - e.y, d = Math.hypot(dx, dy) || 1;
    const vue = Monde.ligneLibre(e.x, e.y, cible.x, cible.y);
    if (d < f[0]) { e.vx = -dx / d * vitesse; e.vy = -dy / d * vitesse; return false; }
    if (d > f[1] || !vue) { e.vx = dx / d * vitesse; e.vy = dy / d * vitesse; return false; }
    e.vx = 0; e.vy = 0;
    return true;
  }

  /** Combien de balles dans cette salve : 2 a 4 a l'empreinte — ou, a la mitraillette, ce que tient la rafale. */
  function salveDe(e, r, arme) {
    const T = tir();
    if (arme.auto) return Math.max(2, Math.floor(T.rafale_images / arme.cadence));
    return T.salve[0] + hash2(e.id, 0x5A1E + r.salves) % (T.salve[1] - T.salve[0] + 1);
  }

  /** Une image de fusillade. Le TIREUR : leve l'arme (`lever_images`) avant sa premiere balle ; tient sa distance,
      la cible en vue ; tire une salve ; rentre a l'abri (ou garde sa distance) le temps `entre_salves_images` ;
      recharge son chargeur vide. Le LANCEUR (la cloche du Molotov) : se place a sa distance de chute, lance, se
      sauve `fuite_images` ; ses bouteilles lancees, il finit aux poings. Rend vrai si un coup est parti. */
  function majTir(e, cible, vitesse, r) {
    const T = tir(), arme = Combat.armeDef(e.arme), f0 = T.distances[e.arme];
    // BLESSE (vague 3), le tireur ne lache pas : il recule au fond de sa fourchette, la moitie haute.
    const f = blesse(e) && !tenace(e) ? [(f0[0] + f0[1]) / 2, f0[1]] : f0;
    if (r.balles === undefined) {
      r.balles = arme.chargeur || 1; r.tir = 'expose';
      r.salve = 0; r.salves = 0; r.prochain = 0; r.pause = 0; r.recharge = 0; r.abri = null;
      lever(e, r);
    } else if (e.t - r.derniere > T.retour_images) {
      // Revenu au combat apres l'avoir lache (trop loin, en fuite) : il RELEVE l'arme, il ne tire pas d'emblee.
      lever(e, r);
    }
    r.derniere = e.t;
    if (r.balles <= 0) {
      // ⚠️ Plus de bouteilles : il finit AUX POINGS, et redevient un homme du cercle.
      if (arme.cloche) { e.arme = 'poings'; e.armeDeGang = null; e.vx = 0; e.vy = 0; return false; }
      if (!r.recharge) r.recharge = e.t + T.recharge_images;
      if (e.t < r.recharge) { seMettreAlAbri(e, cible, f, vitesse, r); return false; }
      r.balles = arme.chargeur; r.recharge = 0; r.tir = 'expose';
    }
    if (r.tir === 'fuite') {
      const dx = e.x - cible.x, dy = e.y - cible.y, d = Math.hypot(dx, dy) || 1;
      e.vx = dx / d * vitesse; e.vy = dy / d * vitesse;
      if (e.t >= r.pause) r.tir = 'expose';
      return false;
    }
    if (r.tir === 'abri') {
      seMettreAlAbri(e, cible, f, vitesse, r);
      if (e.t >= r.pause) r.tir = 'expose';
      return false;
    }
    // ⚠️ COLLE A LUI (sous sa fourchette) : il recule en tirant a bout portant, sans attendre sa levee — sinon,
    // coince contre un mur, il restait plante sans rien faire. Pas le lanceur : il se brulerait.
    // ⚠️ Le seuil d'ORIGINE (`f0`) : blesse, sa fourchette commence plus loin, et il tirait « a bout portant » a
    // 75 px au lieu de reculer.
    const colle = !arme.cloche && Math.hypot(cible.x - e.x, cible.y - e.y) < f0[0]
      && Monde.ligneLibre(e.x, e.y, cible.x, cible.y);
    const enPlace = tenirSaDistance(e, cible, f, vitesse);
    if (!(enPlace || colle) || (e.t < r.leve && !colle) || e.t < r.prochain) return false;
    if (!Combat.tirer(e, arme, cible)) return false;
    r.balles--; r.salve++;
    e.ballesDeGang = r.balles;     // l'arme lachee les garde, meme apres la rixe (`finirLaBagarre` vide `e.rixe`)
    r.prochain = e.t + arme.cadence;
    if (arme.cloche) {
      // ⚠️ Le geste du lanceur est COURT : `tirer` le fige le temps de la cadence (40 images), et il ne se
      // sauverait qu'une fois la bouteille cassee.
      e.phaseT = Math.min(e.phaseT, 8);
      r.tir = 'fuite'; r.pause = e.t + T.fuite_images; r.salve = 0;
    } else if (r.salve >= salveDe(e, r, arme)) {
      r.tir = 'abri'; r.pause = e.t + T.entre_salves_images; r.salve = 0; r.salves++;
      r.abri = abriPour(e, cible, f);
    }
    return true;
  }

  /** Il LEVE L'ARME, et ca se voit : une replique criee (le signal pour rouler), le temps de la levee. */
  function lever(e, r) {
    const T = tir(), mots = T.lever_mots;
    r.leve = e.t + T.lever_images;
    if (mots && mots.length) Entites.bulle(e, mots[hash2(e.id, e.t) % mots.length], { duree: T.lever_images + 20 });
  }

  function seMettreAlAbri(e, cible, f, vitesse, r) {
    if (r.abri) marcher(e, r.abri, vitesse);
    else tenirSaDistance(e, cible, f, vitesse);
  }

  return { maj: maj, assaillants: assaillants, armer: armer, abriPour: abriPour, blesse: blesse };
})();
