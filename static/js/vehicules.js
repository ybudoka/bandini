/* Bandini — vehicules : physique arcade, collisions par cercles, trafic.

   Un char est une CHAINE DE CERCLES (trois, le long de son axe) : c'est ce
   qui permet de tester un mur, un autre char ou un pieton avec la meme
   fonction, et de tourner sans boite orientee. Au-dessus de `sous_pas_px`
   par image, le deplacement est decoupe : deux cercles ne se croisent jamais
   sans se voir.

   Le trafic ne connait pas de graphe : il LIT le champ `voie` de la carte,
   tuile par tuile. Sur un croisement, il choisit une sortie ; a une ligne
   d'arret, il regarde le feu. Quand il veut tourner a gauche, il traverse le
   croisement avant de virer — parce qu'il cherche la voie dont la fleche va
   dans son sens, et qu'elle est de l'autre cote.

   Sur un boulevard (deux voies dans le meme sens), un char bloque par un
   pieton, une epave ou un char arrete ne reste pas derriere : il vise la
   tuile d'a cote et se DEPORTE, par la gauche si elle est libre. */

const Vehicules = (function () {
  'use strict';

  const ROTATIONS = 32;
  const PAS_FLECHE = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] };
  const FLECHE_DE = { '1,0': '>', '-1,0': '<', '0,-1': '^', '0,1': 'v' };

  /** Ce que le volant a de PRISE selon la vitesse relative : un peu plus au
      pas (`braquage_lent`), plein vers `braquage_plein_a`, et ce qu'il en
      reste a fond (`braquage_vite`).

      ⚠️ Ce n'est plus la vitesse de rotation, c'est un facteur sur le RAYON :
      le char tournait d'un nombre fixe de radians par image, donc le cercle
      qu'il decrivait grandissait avec la vitesse — 1,7 tuile au pas, DIX a
      fond. Une vraie auto decrit toujours le meme cercle a volant fixe ; la
      rotation est donc `vitesse / rayon_braquage`, et ceci n'ajuste que le
      rayon. */
  function courbeBraquage(t) {
    const ph = physique();
    t = borner(Math.abs(t), 0, 1);
    const plein = ph.braquage_plein_a;
    if (t <= plein) return ph.braquage_lent + (1 - ph.braquage_lent) * (t / plein);
    return 1 + (ph.braquage_vite - 1) * (t - plein) / (1 - plein);
  }

  /** Le char pivote sur son ARRIERE, pas sur son nombril : le nez balaie, le
      train arriere suit. Le centre se deplace donc quand le cap tourne — et
      seulement si la place est libre, sinon on tournerait dans un mur. */
  function pivoterSurLArriere(v, ancien) {
    const a = v.def.longueur * physique().pivot_arriere;
    const x = v.x + (Math.cos(v.angle) - Math.cos(ancien)) * a;
    const y = v.y + (Math.sin(v.angle) - Math.sin(ancien)) * a;
    if (bloqueParLesTuiles(v, x, y)) return;
    v.x = x; v.y = y;
  }

  function vehiculeDef(slug) {
    return (B.defs.vehicules || []).find(function (v) { return v.slug === slug; }) || null;
  }

  function trafic() { return B.defs.conduite.trafic; }
  function physique() { return B.defs.conduite.physique; }

  // --- Naissance ------------------------------------------------------------------

  /** LA SILHOUETTE d'un char qui nait : celle que la fiche du catalogue
      nomme, ou l'une de ses `variantes` (demande de Martin : « parfois des
      différences structurelles, pas juste la couleur »).

      ⚠️ **SANS TIRER DE DE**, comme la tete du pilote : la silhouette se lit
      sur la position de naissance (`hash2`). Un `B.rng()` ici decalait tout ce
      qui nait apres — la couleur, le pilote, l'auto-patrouille d'un juge.
      ⚠️ Et une silhouette DONNEE est gardee (`options.sprite`) : le char de la
      planque et ceux du lot reviennent tels qu'on les a laisses, pas tires a
      nouveau a leur nouvelle place. Seulement si elle appartient a CE char : un
      taxi ne revient pas en camionnette. */
  function silhouetteDe(def, x, y, options) {
    const base = SPRITES[def.sprite];
    const variantes = base && base.variantes;
    const donnee = options && options.sprite;
    // ⚠️ Une silhouette DONNEE est celle de la fiche, une de ses variantes, ou une
    // silhouette qui se declare d'elle sans jamais se tirer au sort (`de`, le tramway).
    if (donnee && (donnee === def.sprite || (variantes && variantes[donnee]) || (SPRITES[donnee] && SPRITES[donnee].de === def.sprite))) return donnee;
    if (!variantes) return def.sprite;
    const noms = Object.keys(variantes);
    const total = noms.reduce(function (t, n) { return t + variantes[n]; }, 0);
    let tirage = hash2(Math.round(y), Math.round(x)) / 4294967296 * total;
    for (const n of noms) { tirage -= variantes[n]; if (tirage < 0) return n; }
    return def.sprite;
  }

  function creer(slug, x, y, angle, options) {
    const def = vehiculeDef(slug);
    if (!def) return null;
    // ⚠️ **UNE COULEUR DONNEE NE TIRE PAS DE DE.** Ce qui nait pour le DECOR —
    // un char en panne, demain une charrue — ne doit pas decaler le hasard du
    // jeu : chaque de tire deplace tous ceux qui suivent, et quatre juges sont
    // tombes le jour ou une panne a pris un de au passage. C'est la meme lecon
    // que le pilote des deux-roues, et c'est la seule ligne qui la tient.
    const couleur = (options && options.couleur)
      || def.couleurs[Math.floor(B.rng() * def.couleurs.length)];
    const v = Entites.creer('vehicule', x, y, Object.assign({
      slug: slug, def: def, angle: angle || 0, vitesse: 0, vx: 0, vy: 0, z: 0, vz: 0,
      r: def.largeur / 2, vie: def.vie, vieMax: def.vie, couleur: couleur, swaps: nuances(couleur),
      conducteur: null, etat: 'stationne', cible: null, sens: null, sortie: null,
      patience: 0, force: 0, deportT: 0, deportFroid: 0, alarme: 0, klaxonT: 0, chocs: 0, agresseur: null,
      vole: false, aToi: false, aQui: null, laisse: false, malGareT: 0, epaveT: 0, coule: 0, solide: false, vivant: true, sprite: def.sprite, sirene: false, remorque: null, remorqueePar: null, parcouru: 0,
    }, options || {}));
    v.sprite = silhouetteDe(def, x, y, options);
    // ⚠️ UNE SILHOUETTE PEUT PORTER SA COULEUR : l'autobus scolaire est jaune,
    // quelle que soit celle tiree pour l'autobus. Le de de la couleur est tire
    // quand meme, avant — la naissance consomme le meme nombre de des pour
    // toutes les silhouettes. Une couleur DONNEE (`options.couleur`) gagne.
    const fiche = SPRITES[v.sprite];
    if (fiche && fiche.couleur && !(options && options.couleur)) { v.couleur = fiche.couleur; v.swaps = nuances(fiche.couleur); }
    // ⚠️ UN DEUX-ROUES DU TRAFIC A UN PILOTE, et il a ses propres couleurs. Le
    // cycliste etait cuit dans le velo — la meme tete pour toute la ville. Un
    // sprite qui declare une `selle` prend un passant assis dessus, tire des
    // archetypes de rue comme n'importe quel passant. Un deux-roues STATIONNE
    // n'a personne dessus : c'est ce qui le distingue d'un char qui roule.
    const sprite = SPRITES[v.sprite];
    if (sprite && sprite.selle && v.conducteur === 'trafic') {
      // ⚠️ **QUELQU'UN DE PRECIS AU VOLANT** : la fiche peut dire QUI mene le char
      // (`au_volant`, le cabriolet rose et sa conductrice) — et c'est elle, pas
      // un passant tire de la rue. Son identite voyage avec elle (`arch`) : c'est
      // ELLE que le carjacking sort de la voiture (`monter`), et pas celle qu'on
      // croit reconnaitre au slug du char — un voleur qui l'aurait prise reste un
      // voleur. Aucun de : le catalogue la nomme.
      const nommee = def.au_volant ? Entites.archetype(def.au_volant) : null;
      if (nommee && nommee.slug === def.au_volant) {
        v.pilote = { swaps: nommee.couleurs, arch: nommee.slug };
      } else {
        // ⚠️ SANS TOUCHER AUX DES DU JEU : la tete du pilote se tire de sa
        // position par `hash2`. Un `B.rng()` ici decalait tout ce qui naissait
        // apres, et un juge de police voyait son auto-patrouille naitre ailleurs.
        const arch = Entites.archetypeDeRue(x, y, hash2(Math.round(x), Math.round(y)) / 4294967296);
        v.pilote = arch ? { swaps: arch.couleurs } : null;
      }
    }
    return v;
  }

  /** Un type de char selon les poids du catalogue (phase 1 seulement).

      ⚠️ Un char `rare` ne nait QUE dans un district qui le declare (`rares` de
      la zone, pose par `carte.py`). C'est la, et pas dans sa `frequence`, que
      se joue sa rarete : un coupe sport qu'on croise dans une cour a ferraille
      n'est plus un coupe sport, c'est une auto de plus. Et c'est PYTHON qui
      decide ou — le navigateur n'a pas a savoir qu'une decapotable n'a rien a
      faire a La Shop. */
  function standingDuParc(standing) {
    const table = (B.defs.conduite && B.defs.conduite.standing) || {};
    return table[standing] || { rares: 1, usure: 1 };
  }

  function typeDeRue(zone, standing) {
    const rares = (zone && zone.rares) || [];
    // ⚠️ ET PAS DANS UNE RUE PAUVRE (4e vague des quartiers) : une decapotable
    // devant un preteur sur gages n'est plus une decapotable.
    const permis = standing === undefined ? 1 : standingDuParc(standing).rares;
    const types = B.defs.vehicules.filter(function (v) {
      if (v.phase !== 1 || v.frequence <= 0) return false;
      return !v.rare || (permis && rares.indexOf(v.slug) >= 0);
    });
    if (!types.length) return null;
    let tirage = B.rng() * types.reduce(function (s, v) { return s + v.frequence; }, 0);
    for (const v of types) { tirage -= v.frequence; if (tirage <= 0) return v; }
    return types[0];
  }

  /** LA MINOUNE D'UNE RUE PAUVRE : la carrosserie qu'il lui reste (`usure`). Elle
      ne se voit pas d'en haut — elle se SENT, au premier poteau : un char de la
      rue chic encaisse, celui-la casse. */
  function user(v, standing) {
    if (!v) return v;
    const usure = standingDuParc(standing).usure;
    if (usure >= 1) return v;
    // `usure` reste sur le char : c'est ce qui dit qu'il est NE minoune, et pas
    // qu'il s'est fait defoncer depuis (un juge les distingue).
    v.usure = usure;
    v.vie = Math.max(1, Math.round(v.vieMax * usure));
    return v;
  }

  function libreAutour(x, y, rayon) {
    return Entites.autour(x, y, rayon, function (e) { return e.type === 'vehicule' || e.type === 'joueur'; }).length === 0;
  }

  /** Une tuile de voie (fleche) dans la bulle, hors ecran, sans char dessus. */
  function placeDansLeTrafic() {
    const t = trafic(), c = Monde.carte, j = B.joueur;
    for (let essai = 0; essai < 20; essai++) {
      const a = B.rng() * Math.PI * 2;
      const d = t.naissance_px + B.rng() * (t.oubli_px - t.naissance_px - 80);
      const tx = Math.floor((j.x + Math.cos(a) * d) / TT), ty = Math.floor((j.y + Math.sin(a) * d) / TT);
      if (tx < 1 || ty < 1 || tx >= c.w - 1 || ty >= c.h - 1) continue;
      const f = Monde.fleche(tx, ty);
      if (!PAS_FLECHE[f]) continue;
      const x = tx * TT + 8, y = ty * TT + 8;
      if (Entites.visibleAEcran(x, y, 40) || !libreAutour(x, y, 48)) continue;
      const pas = PAS_FLECHE[f];
      return { x: x, y: y, angle: Math.atan2(pas[1], pas[0]), sens: f };
    }
    return null;
  }

  //: Le glyphe d'une case dit ou pointe le NEZ de l'auto garee.
  const NEZ = { '^': [0, -1], 'v': [0, 1], '<': [-1, 0], '>': [1, 0] };

  /** Une case de stationnement libre, DANS SES LIGNES : on cherche la tuile du
      fond (celle contre la ligne de nez) qui a le reste de sa case derriere
      elle, et l'auto se pose a cheval sur les deux — elle fait deux tuiles de
      long, la case aussi. */
  //: La longueur d'une case de stationnement, en pixels : deux tuiles, le
  //: gabarit d'une auto. ⚠️ Elle vient de la carte (`CASE_CREUX`), et tout ce
  //: qui la depasse ne se gare pas dedans.
  const CASE_PX = 2 * TT;

  /** `prefere` (facultatif, `garesVoulus()`) : la nuit, on rentre chez soi
      (`placeDeNuit`). Sans preference — le jour —, le tirage d'avant, au de pres. */
  function placeStationnee(prefere) {
    if (prefere && prefere.usage) return placeDeNuit(prefere);
    const t = trafic(), c = Monde.carte, j = B.joueur;
    for (let essai = 0; essai < 20; essai++) {
      const a = B.rng() * Math.PI * 2;
      const d = t.naissance_px * 0.6 + B.rng() * (t.oubli_px - t.naissance_px);
      const tx = Math.floor((j.x + Math.cos(a) * d) / TT), ty = Math.floor((j.y + Math.sin(a) * d) / TT);
      if (tx < 1 || ty < 2 || tx >= c.w - 1 || ty >= c.h - 1) continue;
      const g = Monde.glyphe(tx, ty), nez = NEZ[g];
      if (!nez) continue;
      if (Monde.glyphe(tx + nez[0], ty + nez[1]) === g) continue;     // pas le fond
      if (Monde.glyphe(tx - nez[0], ty - nez[1]) !== g) continue;     // case tronquee
      const x = (tx + 0.5 - nez[0] / 2) * TT, y = (ty + 0.5 - nez[1] / 2) * TT;
      if (Entites.visibleAEcran(x, y, 40) || !libreAutour(x, y, 40)) continue;
      return { x: x, y: y, angle: Math.atan2(nez[1], nez[0]) };
    }
    return null;
  }

  //: Les cases de la carte, par leur tuile du FOND (celle contre la ligne de
  //: nez, avec le reste de la case derriere elle) : lues une fois par carte.
  let fondsDe = null, fonds = [];
  function fondsDesCases() {
    const c = Monde.carte;
    if (fondsDe === c) return fonds;
    fondsDe = c; fonds = [];
    for (let ty = 2; ty < c.h - 1; ty++) {
      for (let tx = 1; tx < c.w - 1; tx++) {
        const g = Monde.glyphe(tx, ty), nez = NEZ[g];
        if (!nez || Monde.glyphe(tx + nez[0], ty + nez[1]) === g || Monde.glyphe(tx - nez[0], ty - nez[1]) !== g) continue;
        fonds.push({ tx: tx, ty: ty, x: (tx + 0.5 - nez[0] / 2) * TT, y: (ty + 0.5 - nez[1] / 2) * TT,
                     angle: Math.atan2(nez[1], nez[0]) });
      }
    }
    return fonds;
  }

  /** La nuit, une case libre dans l'anneau de naissance — d'abord dans une rue
      ou l'on habite, et une fois sur quelques-unes (`ailleurs`) devant un
      commerce : le bar et le depanneur ont leurs clients de nuit.

      ⚠️ **ON CHOISIT PARMI LES CASES, on ne tire pas au hasard dans l'anneau.**
      Premiere version : le tirage du jour, qui refusait les cases d'ailleurs
      pendant ses premiers essais. Or une tuile tiree au hasard n'est une case
      qu'une fois sur dix — refuser en plus faisait MOINS de chars la nuit que
      le jour (0 contre 1 en 4 000 images, le juge l'a vu). Le jour garde son
      tirage : c'est lui qui garde les des de la suite a leur place. */
  function placeDeNuit(prefere) {
    const t = trafic(), j = B.joueur;
    const min = t.naissance_px * 0.6, max = t.naissance_px * 0.6 + (t.oubli_px - t.naissance_px);
    const chez = [], ailleurs = [];
    for (const f of fondsDesCases()) {
      const d2 = dist2(f.x, f.y, j.x, j.y);
      if (d2 < min * min || d2 > max * max) continue;
      if (Entites.visibleAEcran(f.x, f.y, 40) || !libreAutour(f.x, f.y, 40)) continue;
      (Monde.usageA(f.tx, f.ty) === prefere.usage ? chez : ailleurs).push(f);
    }
    const versAilleurs = B.rng() < (prefere.ailleurs || 0);
    const liste = chez.length && !(versAilleurs && ailleurs.length) ? chez : ailleurs;
    if (!liste.length) return null;
    const f = liste[Math.floor(B.rng() * liste.length)];
    return { x: f.x, y: f.y, angle: f.angle };
  }

  /** Combien de chars garés la bulle veut à cette heure, et où d'abord.

      ⚠️ **LA NUIT, LES CHARS RENTRENT À LA MAISON** (`TRAFIC.garer_la_nuit`) :
      deux fois plus, et d'abord dans les rues où l'on habite. Le jour rend
      exactement ce qu'il rendait avant (six, n'importe où) — c'est ce qui garde
      les des de toute la suite a leur place. `estNuit(heure)` AVEC l'heure :
      c'est la nuit DEHORS, qu'on la voie ou non. */
  function garesVoulus() {
    const t = trafic(), n = t.garer_la_nuit;
    if (n && B.partie && Monde.estNuit(B.partie.heure)) return { max: n.max, usage: n.usage, ailleurs: n.ailleurs };
    return { max: t.stationnes_max, usage: null, ailleurs: 0 };
  }

  /** Comme les pietons : naitre hors champ, s'oublier hors de la bulle. */
  /** **Le char en panne** : une entrave qu'on n'a pas vue venir. Il s'arrete
      en travers d'une voie, ses feux de detresse battent, et il repart au bout
      d'une heure de jeu.

      ⚠️ Rien de neuf pour le trafic : un char arrete sur la chaussee, il sait
      deja — il se deporte (`obstacleDevant`), comme devant un pieton plante au
      milieu de la rue. C'est la difference avec le chantier du jour : celui-la
      a ses cones et sa liste validee, celle-ci n'a que ses feux.

      ⚠️ Une fois par HEURE de jeu, pas une fois par image : `B.partie.heure`
      avance de 1/`jour_secondes` par seconde, et on ne tire qu'au changement
      d'heure — sinon la ville est un garage. */
  /** Une place pour un char en panne, tiree d'une EMPREINTE et non du de du
      jeu : on tourne autour du joueur jusqu'a trouver une voie hors ecran. */
  function placeDeLaPanne(graine) {
    const t = trafic(), j = B.joueur;
    for (let essai = 0; essai < 24; essai++) {
      const h = hash2(graine, essai);
      const a = (h % 3600) / 3600 * Math.PI * 2;
      const d = t.naissance_px + ((h >> 12) % 100) / 100 * (t.oubli_px - t.naissance_px - 80);
      const x = j.x + Math.cos(a) * d, y = j.y + Math.sin(a) * d;
      const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
      const f = Monde.fleche(tx, ty);
      if (!PAS_FLECHE[f]) continue;
      const p = PAS_FLECHE[f];
      // ⚠️ **JAMAIS CONTRE UNE TRAVERSE.** La voie qui precede un passage
      // cloute est une voie comme une autre, mais une caisse de 48 px posee la
      // couvre les bandes — et elle y reste quarante minutes de jeu, la ou un
      // char au feu repart. C'est l'autre moitie de « les chars s'arretent
      // avant le passage » : le trafic n'y attend plus, encore faut-il que
      // personne n'y campe.
      const ecart = t.panne.ecart_traverse_tuiles;
      let contreUnPassage = false;
      for (let k = -ecart; k <= ecart && !contreUnPassage; k++) {
        contreUnPassage = Monde.estPassage(tx + p[0] * k, ty + p[1] * k);
      }
      if (contreUnPassage) continue;
      return { x: tx * TT + 8, y: ty * TT + 8, angle: Math.atan2(p[1], p[0]), sens: f };
    }
    return null;
  }

  function majPanne() {
    const f = trafic().panne;
    if (!f || !B.joueur || B.interieur || !B.partie) return;
    const heure = Math.floor(B.partie.heure * 24);
    if (B.panneHeure === heure) return;
    B.panneHeure = heure;
    // ⚠️ `hash2` du JOUR et de l'HEURE, pas `B.rng()` : une panne est un decor,
    // et un decor ne consomme pas un de du jeu.
    if (hash2(B.partie.jour * 31 + heure, 0x9A44E) / 4294967296 >= f.chance_par_heure) return;
    if (B.entites.some(function (e) { return e.panneT > 0; })) return;
    // ⚠️ La PLACE aussi se tire au jour et a l'heure, pas au de du jeu :
    // `placeDansLeTrafic` en consomme deux, et deux des pris pour un decor
    // decalent toute la ville.
    const place = placeDeLaPanne(hash2(B.partie.jour, heure * 7 + 3));
    if (!place || Entites.visibleAEcran(place.x, place.y, 40)) return;
    const slug = f.slugs[hash2(heure, B.partie.jour) % f.slugs.length];
    const def = vehiculeDef(slug);
    const v = creer(slug, place.x, place.y, place.angle, {
      etat: 'stationne', sens: place.sens,
      couleur: def.couleurs[hash2(B.partie.jour * 13, heure) % def.couleurs.length],
    });
    if (!v) return;
    v.vitesse = 0; v.vx = 0; v.vy = 0;
    v.panneT = Math.round(f.minutes / (24 * 60) * B.defs.economie.jour_secondes * 60);
    // ⚠️ **PAS `laisse`.** Ce mot-la veut dire « le JOUEUR l'a abandonne ici »,
    // et c'est lui seul que la fourriere suit (`majMalGares`) : marquer la
    // panne ainsi la faisait declarer MAL GAREE — le HUD nageait dans « la
    // fourriere va passer » pendant qu'un camion avait ses feux de detresse.
    // Un char en panne n'est pas mal gare : il est en panne.
  }

  function peupler() {
    const t = trafic(), j = B.joueur;
    let roulent = 0, stationnes = 0;
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const v = B.entites[i];
      if (v.type !== 'vehicule') continue;
      const loin = dist2(v.x, v.y, j.x, j.y) > t.oubli_px * t.oubli_px;
      if (loin && v.conducteur !== j && !v.mission && !v.remorqueePar && !v.remorque && !Entites.visibleAEcran(v.x, v.y, margeDOubli(v))) { Entites.retirer(v); continue; }
      if (v.etat === 'epave') continue;
      // ⚠️ **UNE PANNE N'EST PAS UN CHAR GARE** : la compter dans les places
      // de stationnement prenait une place au parc normal, donc la ville
      // faisait naitre un char de moins — et chaque naissance evitee decale
      // tous les des qui suivent. Un juge d'amuseur est tombe pour ca.
      if (v.panneT > 0) continue;
      // ⚠️ Ni une auto-patrouille garee au poste : c'est le LOT qui la fait
      // naitre (`majGaresDeService`), pas le parc de la rue — la compter
      // ferait naitre un char de moins, et les des de toute la ville glissent.
      if (v.gareDeService && v.etat === 'stationne' && !v.laisse) continue;
      // ⚠️ Un autobus de ligne n'est ni du trafic ni un char gare : c'est l'horaire
      // qui le fait naitre (`Autobus.faireNaitre`), il ne prend la place de personne.
      if (v.conducteur === 'ligne') continue;
      if (v.conducteur === 'trafic') roulent++; else if (v.conducteur !== j) stationnes++;
    }
    if (B.t % 20 !== 0) return;
    majAmarrages();
    majGaresDeService();
    const zone = Monde.zoneA(j.x, j.y);
    const voulu = Math.min(t.vehicules_max, zone ? zone.vehicules : 6) * Monde.rythme(zone);
    if (roulent < voulu) {
      const place = placeDansLeTrafic();
      if (place) {
        const rang = Monde.standingA(Math.floor(place.x / TT), Math.floor(place.y / TT));
        const type = typeDeRue(zone, rang);
        const v = type && creer(type.slug, place.x, place.y, place.angle, { conducteur: 'trafic', etat: 'roule', sens: place.sens });
        if (v) {
          user(v, rang);
          v.vitesse = v.def.vitesse_max * t.vitesse_ville * 0.5;
          // ⚠️ Le cycliste nait DEJA a la bordure : ne au milieu de sa voie, on le
          // voyait glisser vers le trottoir a chaque apparition.
          if (estVeloDuTrafic(v)) {
            const q = droiteDe(PAS_FLECHE[place.sens]);
            v.x += q[0] * t.velo.bord_px; v.y += q[1] * t.velo.bord_px;
          }
          // ⚠️ Une ambulance sur trois est EN COURSE, et on l'entend passer.
          // Les deux autres rentrent au garage : une ville ou toutes les
          // ambulances hurlent n'est pas une ville, c'est une alarme.
          if (v.def.sirene) v.sirene = B.rng() < AMBULANCE_EN_COURSE;
        }
      }
    } else if (stationnes < garesVoulus().max && B.t % 40 === 0) {
      const place = placeStationnee(garesVoulus());
      // ⚠️ IL FAUT QUE LE CHAR RENTRE DANS LA CASE. Une case fait deux tuiles,
      // soit 32 px ; la remorqueuse en fait 36. Garee la, elle depassait, le
      // garde-fou (`degager`) la poussait hors des tuiles qu'elle chevauche, et
      // elle finissait A CHEVAL SUR SES LIGNES — a un centieme de pixel pres,
      // ce qui est exactement ce qu'un juge voit et qu'un oeil ne voit pas.
      if (place) {
        // ⚠️ Et ce qui est TOUJOURS MENE (`au_volant`) ne se gare jamais : un
        // cabriolet rose vide, sans personne a en faire descendre, ne serait plus
        // le sien — il ne se croise qu'en circulation, avec sa conductrice.
        const rentre = function (t) { return t.longueur <= CASE_PX && !t.au_volant; };
        const rang = Monde.standingA(Math.floor(place.x / TT), Math.floor(place.y / TT));
        let type = typeDeRue(zone, rang);
        for (let essai = 0; essai < 6 && type && !rentre(type); essai++) type = typeDeRue(zone, rang);
        if (type && rentre(type)) {
          user(creer(type.slug, place.x, place.y, place.angle, { etat: 'stationne' }), rang);
        }
      }
    }
  }

  //: La bulle des chaloupes : un peu plus large que celle des gens (520),
  //: parce qu'une coque se voit de loin sur l'eau — rien ne la cache.
  const AMARRAGE_OUBLI = 620;

  /** LES CHALOUPES AMARREES. ⚠️ Une coque ne nait PAS dans le trafic — elle n'a
      ni voie ni trottoir a suivre, et une chaloupe sur la rue Principale est
      exactement ce que `tuileInterdite` interdit. On la trouve la ou Python l'a
      mise (`carte.amarrages` : de l'eau contre une rive batie), et nulle part
      ailleurs.

      ⚠️ Elle nait HORS CHAMP et s'oublie de loin, comme le reste : une coque
      amarree a l'autre bout de la baie ne coute rien a personne. */
  function majAmarrages() {
    const def = Monde.carte && Monde.carte.def;
    const places = (def && def.amarrages) || [];
    const j = B.joueur;
    // ⚠️ Les grands bateaux ne dependent pas des chaloupes : une ville sans
    // amarrage aurait quand meme son cargo.
    if (!places.length || !j || B.interieur) return majMouillages();
    let nees = 0;
    for (const place of places) {
      const x = place.x * TT + 8, y = place.y * TT + 8;
      const d2 = (x - j.x) * (x - j.x) + (y - j.y) * (y - j.y);
      const deja = B.entites.some(function (q) {
        return q.type === 'vehicule' && q.amarrage === place;
      });
      // ⚠️ On ne l'efface PAS soi-meme : `peupler` oublie deja tout vehicule
      // trop loin, et une deuxieme regle d'oubli aurait ete une deuxieme verite
      // a tenir a jour. On se contente de ne pas en refaire une tant qu'elle est
      // hors de portee — et une coque qu'on a prise et laissee ailleurs n'est
      // plus amarree : c'est un char gare comme un autre.
      if (d2 > AMARRAGE_OUBLI * AMARRAGE_OUBLI) continue;
      if (deja || Entites.visibleAEcran(x, y, 24)) continue;
      // ⚠️ **SA COULEUR SE TIRE A L'EMPREINTE DE L'AMARRAGE, jamais au de du
      // jeu.** `creer` prend un de pour choisir dans `def.couleurs` quand on ne
      // lui en donne pas — et onze juges sans rapport sont tombes d'un coup le
      // jour ou dix-huit chaloupes sont nees. C'est la meme lecon que le char en
      // panne, que le pilote des deux-roues, et que les enfants de la greve : ce
      // qui nait pour le DECOR ne decale pas le hasard du jeu.
      const def = vehiculeDef('bateau');
      const couleur = def.couleurs[hash2(place.x * 7919 + place.y, 0xC0C0E) % def.couleurs.length];
      const v = creer('bateau', x, y, place.angle || 0, { etat: 'stationne', couleur: couleur });
      if (v) { v.amarrage = place; nees++; }
    }
    return nees + majMouillages();
  }

  /** LES GRANDS BATEAUX A QUAI : le chalutier et le porte-conteneurs (demande de
      Martin, 21 sept. 2026). La meme regle que les chaloupes — hors champ, dans la
      bulle, une seule a la fois, la couleur a l'empreinte du mouillage —, mais la
      place est un CENTRE en pixels et un cap (`carte.mouillages`, `navires.py`) :
      une coque de dix tuiles ne se centre pas sur une tuile, et elle mouille le
      long du quai, le nez vers le chenal.

      ⚠️ **Hors champ par son BOUT, pas par son centre** : a 160 px, un centre
      juste hors de l'ecran laisse la proue dedans. La marge est la demi-longueur.
      ⚠️ Et EN DECA de l'oubli (`oubli_px`) : au-dela, `peupler` l'oublierait a
      l'image suivante et on la referait — un porte-conteneurs qui nait et meurt
      soixante fois par seconde, hors champ. */
  function majMouillages() {
    const def = Monde.carte && Monde.carte.def;
    const places = (def && def.mouillages) || [];
    const j = B.joueur;
    if (!places.length || !j || B.interieur) return 0;
    const portee = trafic().oubli_px - GAREES_MARGE;
    let nees = 0;
    for (const place of places) {
      const fiche = vehiculeDef(place.slug);
      if (!fiche) continue;
      const d2 = (place.x - j.x) * (place.x - j.x) + (place.y - j.y) * (place.y - j.y);
      if (d2 > portee * portee) continue;
      if (B.entites.some(function (q) { return q.type === 'vehicule' && q.amarrage === place; })) continue;
      if (Entites.visibleAEcran(place.x, place.y, fiche.longueur / 2 + 24)) continue;
      const couleur = fiche.couleurs[hash2(place.x * 7919 + place.y, 0xC0C0E) % fiche.couleurs.length];
      const v = creer(place.slug, place.x, place.y, place.angle || 0, { etat: 'stationne', couleur: couleur });
      if (v) { v.amarrage = place; nees++; }
    }
    return nees;
  }

  /** La marge d'oubli d'un char : ⚠️ par son BOUT. Un char de moins de 72 px garde
      les 60 px de tout le monde (les des du trafic ne bougent pas d'un cran) ; un
      porte-conteneurs, sa demi-longueur et de l'air — sinon il disparaissait la
      proue encore a l'ecran. */
  function margeDOubli(v) { return Math.max(60, v.def.longueur / 2 + 24); }

  //: La bulle des chars gares au poste. ⚠️ EN DECA de l'oubli (`oubli_px`) : au-dela,
  //: `peupler` oublierait a l'image suivante celle qu'on vient de poser, et on la
  //: reposerait — une auto-patrouille qui clignote hors champ, vingt fois par seconde.
  const GAREES_MARGE = 60;
  const NEZ_DU_SENS = { N: [0, -1], S: [0, 1], O: [-1, 0], E: [1, 0] };

  /** LES AUTOS-PATROUILLES GAREES AU POSTE. Demande de Martin (17 sept. 2026) :
      « ajoute toujours un stationnement au poste de police avec une ou des
      vehicules de police stationnes ». Python dessine le lot et dit combien de
      places sont prises (`stationnement_du_poste.garees`) ; ici on y pose le
      char de la fiche, dans ses lignes, comme `placeStationnee`.

      ⚠️ Rien n'est tire au de du jeu : la couleur est DONNEE (sinon `creer` en
      tire une), et la place est ecrite. Ce qui nait pour le decor ne decale pas
      le hasard — la lecon des chaloupes (`majAmarrages`).

      ⚠️ Garee, elle n'a pas de conducteur : ce n'est pas la police qui patrouille
      (`conducteur === 'police'`), c'est un char a voler — et l'alarme d'une
      auto-patrouille, a vingt pas du poste, se paie. Prise et laissee ailleurs,
      elle garde sa place tant qu'elle existe ; oubliee ou detruite, le lot en
      refait une, hors champ. */
  function majGaresDeService() {
    const lot = Monde.carte && Monde.carte.def && Monde.carte.def.stationnement_du_poste;
    const j = B.joueur;
    if (!lot || !j || B.interieur) return 0;
    const def = vehiculeDef(lot.vehicule);
    if (!def) return 0;
    const portee = trafic().oubli_px - GAREES_MARGE;
    let nees = 0;
    for (let i = 0; i < lot.garees && i < lot.places.length; i++) {
      const place = lot.places[i], nez = NEZ_DU_SENS[place.sens] || NEZ_DU_SENS.N;
      const x = (place.x + 0.5 - nez[0] / 2) * TT, y = (place.y + 0.5 - nez[1] / 2) * TT;
      if (dist2(x, y, j.x, j.y) > portee * portee) continue;
      if (B.entites.some(function (q) { return q.type === 'vehicule' && q.gareDeService === place; })) continue;
      if (Entites.visibleAEcran(x, y, 24) || !libreAutour(x, y, 12)) continue;
      const v = creer(lot.vehicule, x, y, Math.atan2(nez[1], nez[0]), { etat: 'stationne', couleur: def.couleurs[0] });
      if (v) { v.gareDeService = place; nees++; }
    }
    return nees;
  }

  // --- Geometrie : la chaine de cercles ------------------------------------------

  /** ⚠️ Le nombre de cercles vient de la FICHE, pas d'une constante unique.
      Il en faut au moins `longueur / largeur`, sinon deux cercles voisins
      laissent un trou et une moto entre dans l'autobus par le milieu sans que
      rien ne se touche (juge Python `test_la_chaine_de_cercles_ne_laisse_aucun_trou`).
      Les cinq de l'autobus et les quatre du camion ne sont pas un reglage de
      confort : c'est ce qui fait qu'ils ont une carrosserie. */
  function cercles(v, x, y, angle) {
    const n = v.def.cercles || physique().cercles;
    const demi = v.def.longueur / 2 - v.r;
    const out = [];
    const cx = Math.cos(angle === undefined ? v.angle : angle), cy = Math.sin(angle === undefined ? v.angle : angle);
    for (let i = 0; i < n; i++) {
      const t = n === 1 ? 0 : -demi + (2 * demi) * i / (n - 1);
      out.push({ x: (x === undefined ? v.x : x) + cx * t, y: (y === undefined ? v.y : y) + cy * t, r: v.r });
    }
    return out;
  }

  /** Les tuiles qui bloquent le char a cette place — la liste, pas un oui/non.
      C'est ce qu'il faut pour decider si un LOURD passe au travers : il faut
      les voir TOUTES avant de trancher. */
  function tuilesQuiBloquent(v, x, y) {
    const out = [];
    for (const c of cercles(v, x, y)) {
      const tx0 = Math.floor((c.x - c.r) / TT), tx1 = Math.floor((c.x + c.r) / TT);
      const ty0 = Math.floor((c.y - c.r) / TT), ty1 = Math.floor((c.y + c.r) / TT);
      for (let ty = ty0; ty <= ty1; ty++) {
        for (let tx = tx0; tx <= tx1; tx++) {
          if (tuileInterdite(v, tx, ty) || Monde.barriereBloque(v, tx, ty)) out.push([tx, ty]);
        }
      }
    }
    return out;
  }

  /** Le decor sur le chemin : ce qui ARRETE, ce qui CASSE, et ce qui n'est
      rien pour un char.

      ⚠️ Avant, le decor etait solide pour les pietons et FANTOME pour les
      chars : un autobus traversait un arbre, un kiosque et une fontaine sans
      ralentir. C'est la moitie d'un monde — et le lampadaire, lui, etait
      fantome pour tout le monde.

      Rend `'arrete'`, `'casse'` ou null. C'est la FICHE qui decide, pas le
      slug : `arrete` est la masse au-dela de laquelle ca cede, `casse` la
      fraction de vitesse qu'on garde en passant au travers. */
  function decorDevant(v, x, y) {
    const ph = physique();
    // ⚠️ Un char LENT ne casse rien et ne bute sur rien — mais il POUSSE encore une benne : la
    // poussée le ralentit sous ce seuil, et sans elle il la traverserait comme un fantôme.
    const lent = Math.hypot(v.vx, v.vy) < ph.choc_vitesse_min;
    for (const c of cercles(v, x, y)) {
      // ⚠️ 26 et pas 14 : une benne fait 30 px de large, son CENTRE est à 15 px de son bout.
      // (Le test précis, lui, est plus bas : ceci ne fait que choisir qui regarder.)
      for (const d of Entites.decorAutour(c.x, c.y, c.r + 26)) {
        if (d.brise) continue;
        const fiche = DECORS[d.decor] || {};
        // ⚠️ Une RAMPE (le tas de terre) n'est ni un mur ni un obstacle qui cède :
        // le char passe dessus, et `majTas` le fait décoller. Sans cette ligne, la
        // berline butait sur le tas et l'autobus le déracinait.
        if (fiche.rampe) continue;
        // ⚠️ Une BENNE se POUSSE : c'est sa boîte, pas un cercle, qu'on touche.
        if (fiche.poussable) {
          if (Entites.boiteTouche(d, c.x, c.y, c.r)) return { quoi: 'pousse', d: d, c: c };
          continue;
        }
        if (lent) continue;
        if (!fiche.arrete && !fiche.casse) continue;
        if (Math.hypot(d.x - c.x, d.y - c.y) > c.r + (d.r || 4)) continue;
        // ⚠️ `lourd` : il ne cede qu'a un char d'AU MOINS cette masse — le
        // guichet s'ouvre au camion, pas a la berline volee du coin. Pour
        // tout ce qui est plus leger, c'est un mur.
        if (fiche.lourd && v.def.masse < fiche.lourd) return { quoi: 'arrete', d: d };
        // ⚠️ Un lourd deracine ce qu'un leger ne fait qu'accrocher : c'est la
        // MASSE qui tranche, pas la vitesse — sinon une berline lancee
        // renverserait une fontaine.
        if (fiche.arrete && v.def.masse < fiche.arrete) return { quoi: 'arrete', d: d };
        return { quoi: 'casse', d: d, garde: fiche.casse || v.def.defonce || 0.55 };
      }
    }
    return null;
  }

  /** POUSSER UNE BENNE : la boîte est écartée du cercle qui la touche par le côté le moins
      enfoncé (comme un piéton contre un décor), et le char paie sa masse — la berline la
      pousse à petite vitesse, l'autobus la sent à peine. Rend faux si elle ne bouge pas. */
  function pousserLeDecor(v, d, c) {
    const ph = physique(), fiche = DECORS[d.decor] || {}, sol = fiche.sol;
    const dx = d.x - c.x, dy = d.y - c.y;
    const px = sol[0] + c.r - Math.abs(dx), py = sol[1] + c.r - Math.abs(dy);
    let mx = 0, my = 0;
    if (px < py) mx = (dx < 0 ? -1 : 1) * (px + 0.5); else my = (dy < 0 ? -1 : 1) * (py + 0.5);
    if (!Entites.pousserDecor(d, mx, my)) return false;
    const frein = 1 - Math.min(ph.poussee_frein_max, fiche.poussable * ph.poussee_frein / v.def.masse);
    v.vitesse *= frein; v.vx *= frein; v.vy *= frein;
    if (!d.sonT || B.t - d.sonT > 25) {
      d.sonT = B.t;
      Son.SFX.chantier('conteneur', d.x, d.y, 260);
      Entites.poussiere(d.x, d.y + 4, 2);
    }
    return true;
  }

  /** Ce qui arrive quand un char rencontre du decor. Rend vrai si la voie
      s'ouvre (le decor a cede), faux s'il faut s'arreter dessus. */
  function heurterDecor(v, x, y) {
    const rencontre = decorDevant(v, x, y);
    if (!rencontre) return true;
    // Une benne : on la pousse. Si elle ne peut pas bouger (un mur derrière, la limite de sa
    // portée), c'est un mur comme un autre.
    if (rencontre.quoi === 'pousse') {
      if (pousserLeDecor(v, rencontre.d, rencontre.c)) return true;
      rencontre.quoi = 'arrete';
    }
    if (rencontre.quoi === 'arrete') {
      // ⚠️ Le REBOND se pose ici, pas dans `heurterMur` : celui-ci ne touche
      // qu'a `v.vitesse`, et c'est l'appelant qui renverse `vx`/`vy` — pour
      // les tuiles, c'est fait axe par axe. Sans ca, le char s'ecrase sur
      // l'arbre en gardant sa vitesse reelle et le traverse quand meme.
      const ph = physique();
      heurterMur(v, Math.hypot(v.vx, v.vy));
      v.vx = -v.vx * ph.choc_rebond; v.vy = -v.vy * ph.choc_rebond;
      return false;
    }
    v.vitesse *= rencontre.garde;
    v.vx *= rencontre.garde; v.vy *= rencontre.garde;
    endommager(v, physique().defonce_degats, v.agresseur);
    Entites.briser(rencontre.d);
    Son.SFX.choc();
    if (v.conducteur === B.joueur) {
      B.cam.secousse = Math.max(B.cam.secousse, 0.45);
      Entree.vibrer(90);
      // ⚠️ Casser est un DELIT. Sans ca, defoncer devient gratuit, et un char
      // lourd vaut plus qu'un char rapide : la taxonomie a deja « conduite
      // dangereuse », avec son temoin qui rapporte.
      Police.signalerCrime('conduite_dangereuse', rencontre.d.x, rencontre.d.y,
                           Police.quelqu_un_voit(rencontre.d.x, rencontre.d.y, null));
    }
    return true;
  }

  /** Un lourd lance passe AU TRAVERS de ce qui est bas. Rend vrai si la voie
      s'est ouverte.

      ⚠️ **Tout ou rien.** On regarde d'abord TOUTES les tuiles qui bloquent :
      s'il y en a une seule qu'on ne casse pas (une façade, l'eau, du barbelé),
      le camion s'arrête comme n'importe qui. Casser « celles qu'on peut » et
      s'arrêter sur le reste laisserait un trou dans une clôture sans être
      passé — le pire des deux mondes.

      Le `defonce` de la fiche dit ce qu'il RESTE de vitesse une fois passé au
      travers : 0,75 pour le camion, 0,6 pour la remorqueuse. Un mur de clôture
      coûte donc quelque chose, sinon on le franchit sans le sentir. */
  /** Un char LANCE pousse les cones d'une barriere fermee : il passe, il y
      laisse `forcer.degats`, et l'etoile de la fiche tombe s'il y en a une.
      ⚠️ Seulement si TOUT ce qui bloque est une barriere forcable — un vrai
      mur derriere les cones reste un mur — et seulement le joueur : le trafic
      fait demi-tour (`prochaineCible`). Rend vrai si la voie s'est ouverte. */
  function forcerBarriere(v, x, y) {
    if (v.conducteur !== B.joueur || Math.hypot(v.vx, v.vy) < physique().defonce_vitesse_min) return false;
    let barriere = null;
    for (const t of tuilesQuiBloquent(v, x, y)) {
      if (tuileInterdite(v, t[0], t[1])) return false;
      const b = Monde.barriereA(t[0], t[1], 'vehicule');
      if (!b || !b.forcer) return false;
      barriere = b;
    }
    if (!barriere) return false;
    v.forceT = 240;                                   // le temps de traverser, sans repayer a l'autre bout
    if (barriere.forcer.degats) endommager(v, barriere.forcer.degats, null);
    if (barriere.forcer.etoiles) Police.etoilesAuMoins(barriere.forcer.etoiles);
    Hud.message(barriere.raison + ' — FORCÉ', 150);
    Son.SFX.choc();
    B.cam.secousse = Math.max(B.cam.secousse, 0.3);
    return true;
  }

  function defoncerDevant(v, x, y) {
    const ph = physique();
    if (!v.def.defonce || B.interieur) return false;
    // ⚠️ Le seuil se règle sur la vitesse du char : la pelle (1,3 px/image, 12 km/h) ne serait jamais
    // assez vite pour le 1,4 d'un camion — et c'est justement celle qui traverse une clôture au pas.
    // Trois quarts de sa vitesse max, sans jamais dépasser le seuil de la fiche : rien ne change pour
    // les chars plus rapides que 1,9.
    if (Math.hypot(v.vx, v.vy) < Math.min(ph.defonce_vitesse_min, v.def.vitesse_max * 0.75)) return false;
    const tuiles = tuilesQuiBloquent(v, x, y);
    if (!tuiles.length) return false;
    for (const t of tuiles) {
      const s = Monde.solidite(t[0], t[1]);
      if (s !== 3 && s !== 4) return false;      // une façade : on s'arrête
      if (Monde.estMeuble(t[0], t[1])) return false;
    }
    let casse = false;
    for (const t of tuiles) if (Monde.defoncer(t[0], t[1])) casse = true;
    if (!casse) return false;
    v.vitesse *= v.def.defonce;
    v.vx *= v.def.defonce; v.vy *= v.def.defonce;
    endommager(v, ph.defonce_degats, v.agresseur);
    Entites.poussiere(x, y, 10);
    Son.SFX.choc();
    if (v.conducteur === B.joueur) { B.cam.secousse = Math.max(B.cam.secousse, 0.5); Entree.vibrer(120); }
    return true;
  }

  /** ⚠️ **CE QUI ARRETE CETTE COQUE-CI.** Un char et un bateau ne sont pas
      arretes par les memes choses, et c'est la seule difference qui compte
      entre les deux mondes : le char est arrete par les murs et **passe** sur
      l'eau (il coule, c'est son affaire, et `majNoyade` s'en charge) ; la coque
      est arretee par **tout ce qui n'est pas de l'eau**.

      ⚠️ Ecrit ICI et pas comme un masque de `Monde` : un masque est une liste
      de ce qui bloque, et la regle du bateau est l'inverse — une liste de ce
      qui laisse passer, et elle n'a qu'une entree. La tordre en masque aurait
      demande un bit « terre » sur chaque tuile du jeu pour un seul vehicule. */
  function tuileInterdite(v, tx, ty) {
    if (v.def && v.def.eau) return !Monde.estEau(tx, ty);
    // ⚠️ Le passage d'un rideau leve, pour le seul char qu'il attend (`Monde.seuilOuvert`).
    if (Monde.seuilOuvert(v, tx, ty)) return false;
    return Monde.bloque(tx, ty, Monde.MASQUE_VEHICULE);
  }

  /** Un des cercles touche-t-il une tuile qui bloque un char ? (en l'air : non)
      `angle` : pour essayer un autre cap sans le donner au char. */
  function bloqueParLesTuiles(v, x, y, angle) {
    if (v.z > 6) return false;
    for (const c of cercles(v, x, y, angle)) {
      const tx0 = Math.floor((c.x - c.r) / TT), tx1 = Math.floor((c.x + c.r) / TT);
      const ty0 = Math.floor((c.y - c.r) / TT), ty1 = Math.floor((c.y + c.r) / TT);
      for (let ty = ty0; ty <= ty1; ty++) {
        for (let tx = tx0; tx <= tx1; tx++) {
          if (tuileInterdite(v, tx, ty) || Monde.barriereBloque(v, tx, ty)) return true;
        }
      }
    }
    return false;
  }

  // --- Le garde-fou : jamais pris dans un mur --------------------------------------

  /** De combien pousser le char pour sortir des tuiles qu'il chevauche : pour
      chaque cercle et chaque tuile, la sortie la plus courte ; par axe et par
      sens, on garde la plus longue. Nul si rien ne chevauche.

      ⚠️ Le MEME test que `bloqueParLesTuiles` — la boite du cercle contre la
      tuile, pas le cercle lui-meme. Sinon le garde-fou dirait « libre » la ou
      `avancer` dit « bloque », et c'est exactement l'ecart dans lequel un char
      reste pris. Un chevauchement de zero compte (le `floor` range la tuile
      touchee parmi celles qu'on teste), d'ou le cheveu ajoute a chaque sortie.

      ⚠️ La plus longue, pas la somme : trois cercles enfonces de 4 px dans la
      meme facade demandent 4 px, pas 12 — la somme faisait sauter le char de
      huit pixels de trop. */
  function pousseeHorsDesTuiles(v, x, y) {
    let xNeg = 0, xPos = 0, yNeg = 0, yPos = 0;
    for (const c of cercles(v, x, y)) {
      const tx0 = Math.floor((c.x - c.r) / TT), tx1 = Math.floor((c.x + c.r) / TT);
      const ty0 = Math.floor((c.y - c.r) / TT), ty1 = Math.floor((c.y + c.r) / TT);
      for (let ty = ty0; ty <= ty1; ty++) {
        for (let tx = tx0; tx <= tx1; tx++) {
          if (!tuileInterdite(v, tx, ty)) continue;
          const gauche = c.x + c.r - tx * TT, droite = (tx + 1) * TT - (c.x - c.r);
          const haut = c.y + c.r - ty * TT, bas = (ty + 1) * TT - (c.y - c.r);
          const versGauche = gauche < droite, versLeHaut = haut < bas;
          const sx = versGauche ? -(gauche + 0.01) : droite + 0.01;
          const sy = versLeHaut ? -(haut + 0.01) : bas + 0.01;
          if (Math.abs(sx) <= Math.abs(sy)) {
            if (versGauche) xNeg = Math.min(xNeg, sx); else xPos = Math.max(xPos, sx);
          } else if (versLeHaut) yNeg = Math.min(yNeg, sy); else yPos = Math.max(yPos, sy);
        }
      }
    }
    return { x: xPos + xNeg, y: yPos + yNeg };
  }

  /** ⚠️ LE GARDE-FOU (demande de Martin : « mets un garde-fou pour eviter que
      mon vehicule coince dans un mur ou un objet »).

      `avancer` teste les tuiles AVANT chaque pas ; rien ne regardait ou le
      char EST. Or trois choses l'y mettent : un autre char qui le pousse
      (`heurterVehicules` deplace sans lire les tuiles), tourner sur place
      contre une facade (la chaine de cercles pivote DANS le mur), et retomber
      d'un saut (en l'air, `bloqueParLesTuiles` dit non). Une fois dedans,
      CHAQUE direction est bloquee — meme celle qui sort — et il ne reste
      qu'a descendre du char. « Un objet », c'est pareil : borne-fontaine,
      cloture, meuble, tout ce que `MASQUE_VEHICULE` arrete.

      D'abord on POUSSE : ce que les tuiles enfoncent, quelques fois de suite.
      C'est ce qui fait qu'un char qui pivote contre un mur glisse le long au
      lieu d'y entrer. Si ca ne suffit pas (un coin, une ruelle plus etroite
      que lui, le milieu d'un toit), on le POSE a la place libre la plus
      proche, par anneaux jusqu'a `degagement_px` — a son cap, sinon au
      dernier cap ou il etait libre, sinon droit dans l'axe. Un char pose
      repart de l'arret : son elan est ce qui l'a mis la. Et si meme ca ne
      trouve rien, on n'y revient pas avant une demi-seconde : la recherche
      est chere, et le mur ne bougera pas d'ici la.

      ⚠️ **La portee est au moins la longueur du char** : un porte-conteneurs de
      dix tuiles, le nez dans une jetee, ne se degage pas a six tuiles. Pour tout ce
      qui roule en ville, `degagement_px` couvre deja le plus long (le juge) et rien
      ne change.

      ⚠️ Pas pour le trafic sur ses rails : il ne lit pas les tuiles, il suit
      sa voie, et il a son propre chien de garde (`debloquer`). Rend vrai si
      le char a bouge. */
  function degager(v) {
    if (v.z > 6) return false;                          // en l'air : on verra a l'atterrissage
    if (!bloqueParLesTuiles(v, v.x, v.y)) { v.angleLibre = v.angle; return false; }
    const ph = physique();
    const x0 = v.x, y0 = v.y;
    for (let i = 0; i < 6; i++) {
      const p = pousseeHorsDesTuiles(v, v.x, v.y);
      const n = Math.hypot(p.x, p.y);
      if (n < 0.001) break;
      const k = Math.min(1, TT / n);                    // jamais plus d'une tuile d'un coup
      v.x += p.x * k; v.y += p.y * k;
      if (!bloqueParLesTuiles(v, v.x, v.y)) return degage(v, x0, y0, false);
    }
    v.x = x0; v.y = y0;
    if (v.degagementEchecT && B.t - v.degagementEchecT < 30) return false;
    const caps = [v.angle];
    if (v.angleLibre !== undefined && Math.abs(ecartAngle(v.angle, v.angleLibre)) > 0.01) caps.push(v.angleLibre);
    const droit = Math.round(v.angle / (Math.PI / 2)) * (Math.PI / 2);
    if (caps.every(function (a) { return Math.abs(ecartAngle(a, droit)) > 0.01; })) caps.push(droit);
    const pas = ph.degagement_pas_px, portee = Math.max(ph.degagement_px, v.def.longueur);
    for (let r = 0; r <= portee; r += pas) {
      const n = r === 0 ? 1 : Math.min(32, Math.max(8, Math.round(2 * Math.PI * r / pas)));
      for (const a of caps) {
        for (let i = 0; i < n; i++) {
          const t = 2 * Math.PI * i / n;
          const x = x0 + Math.cos(t) * r, y = y0 + Math.sin(t) * r;
          if (bloqueParLesTuiles(v, x, y, a)) continue;
          v.x = x; v.y = y; v.angle = a;
          return degage(v, x0, y0, true);
        }
      }
    }
    v.degagementEchecT = B.t;
    return false;
  }

  function degage(v, x0, y0, pose) {
    v.angleLibre = v.angle;
    v.degagements = (v.degagements || 0) + 1;
    if (pose) {
      v.vitesse = 0; v.vx = 0; v.vy = 0;
      if (typeof console !== 'undefined' && console.warn) {
        console.warn('[garde-fou] ' + v.slug + '#' + v.id + ' pose a ' + Math.round(Math.hypot(v.x - x0, v.y - y0)) + ' px de la');
      }
    }
    return true;
  }

  // --- Physique -------------------------------------------------------------------

  /** Une image de conduite : gaz, frein, direction (-1..1), frein a main, et
      `reculCommeEnAvant` (l'option du joueur, voir `commandesJoueur`). */
  function majPhysique(v, cmd) {
    const d = v.def;
    if (cmd.gaz > 0) v.vitesse += d.acceleration * cmd.gaz;
    if (cmd.frein > 0) {
      if (v.vitesse > 0.15) v.vitesse -= d.frein * cmd.frein * Neige.frein(v) * Monde.freinMouille(v);
      else v.vitesse -= d.acceleration * 0.7 * cmd.frein;      // marche arriere
    }
    if (cmd.freinMain) v.vitesse *= 0.965;
    v.vitesse *= d.friction;
    v.vitesse = borner(v.vitesse, -d.vitesse_recul, d.vitesse_max);
    if (Math.abs(v.vitesse) < 0.02 && !cmd.gaz && !cmd.frein) v.vitesse = 0;
    const t = v.vitesse / d.vitesse_max;
    // ⚠️ LE VOLANT SE TOURNE, il ne se claque pas : il prend vers la consigne
    // et se recentre quand on lache. Au clavier, sans ca, chaque appui etait
    // un coup de butee a butee.
    const ph = physique();
    const consigne = borner(cmd.direction || 0, -1, 1);
    v.volant = (v.volant || 0) + (consigne - (v.volant || 0)) * (consigne ? ph.volant_prise : ph.volant_retour);
    if (Math.abs(v.volant) < 0.01) v.volant = 0;
    if (v.volant) {
      // ⚠️ `vitesse / rayon` : a volant fixe, le char decrit TOUJOURS le meme
      // cercle — c'est ce qui rend un coin de rue franchissable a toute
      // vitesse. En marche arriere, le volant s'inverse, comme une vraie auto —
      // sauf `reculCommeEnAvant` : droite reste le sens des aiguilles d'une montre.
      // ⚠️ C'est le signe de la ROTATION qui change, pas la consigne : le volant
      // est lisse, et une consigne retournee au passage a vitesse nulle le
      // faisait traverser de butee a butee — le char tournait du mauvais cote
      // au debut de chaque recul.
      const omega = Math.abs(v.vitesse) / d.rayon_braquage * courbeBraquage(t) * (cmd.freinMain ? 1.35 : 1);
      const ancien = v.angle;
      v.angle += v.volant * omega * (v.vitesse < 0 && !cmd.reculCommeEnAvant ? -1 : 1);
      pivoterSurLArriere(v, ancien);
    }
    // Adherence : la vitesse reelle glisse vers le cap. Frein a main : elle traine.
    // ⚠️ LA NEIGE DIVISE L'ADHERENCE (M12) — la police glisse comme tout le monde.
    const adh = (cmd.freinMain ? d.adherence_frein : d.adherence) * Neige.adherence(v) * Monde.adherenceMouillee(v);
    v.vx += (Math.cos(v.angle) * v.vitesse - v.vx) * adh;
    v.vy += (Math.sin(v.angle) * v.vitesse - v.vy) * adh;
    // En l'air (rampe) : on retombe.
    if (v.z > 0 || v.vz !== 0) {
      v.z += v.vz; v.vz -= physique().gravite;
      if (v.z <= 0) { v.z = 0; v.vz = 0; }
    }
  }

  /** Le deplacement, decoupe en sous-pas, avec les tuiles, les chars, les gens. */
  function avancer(v) {
    const ph = physique();
    degager(v);                                         // le garde-fou : on part d'une place libre
    const vitesse = Math.hypot(v.vx, v.vy);
    const n = Math.max(1, Math.ceil(vitesse / ph.sous_pas_px));
    const px = v.vx / n, py = v.vy / n;
    for (let i = 0; i < n; i++) {
      // Axe par axe : un mur de face arrete, un mur de cote fait glisser.
      let choc = 0;
      if (px !== 0) {
        if (bloqueParLesTuiles(v, v.x + px, v.y) || chargeBloquee(v, v.x + px, v.y)) {
          if (forcerBarriere(v, v.x + px, v.y) || defoncerDevant(v, v.x + px, v.y)) v.x += px;
          else { choc = Math.max(choc, Math.abs(v.vx)); v.vx = -v.vx * ph.choc_rebond; }
        } else v.x += px;
      }
      if (py !== 0) {
        if (bloqueParLesTuiles(v, v.x, v.y + py) || chargeBloquee(v, v.x, v.y + py)) {
          if (forcerBarriere(v, v.x, v.y + py) || defoncerDevant(v, v.x, v.y + py)) v.y += py;
          else { choc = Math.max(choc, Math.abs(v.vy)); v.vy = -v.vy * ph.choc_rebond; }
        } else v.y += py;
      }
      if (choc >= ph.choc_vitesse_min) {
        heurterMur(v, choc);
        break;
      }
      // ⚠️ Le decor APRES les tuiles : un arbre planté contre un mur ne doit
      // pas etre « casse » par un char qui bute deja sur la facade.
      if (!heurterDecor(v, v.x, v.y)) break;
      if (choc > 0) v.vitesse *= 0.5;
    }
    Entites.dansLaCarte(v);
    heurterVehicules(v);
    heurterPietons(v);
    // La rampe : on decolle a la sortie.
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    // ⚠️ Le seuil de decollage vient de Python (`saut_vitesse_min`), qui le
    // deduit de la hauteur minimale visible. L'ancien 1,5 etait ecrit ici a la
    // main : un velo a 2 px/image le passait et « sautait » de deux pixels —
    // moins que l'epaisseur de son ombre.
    if (v.z === 0 && Math.abs(v.vitesse) >= B.defs.conduite.saut_vitesse_min && Monde.estRampe(tx, ty)) {
      v.vz = Math.abs(v.vitesse) * ph.rampe_impulsion;
    }
  }

  function heurterMur(v, force) {
    const ph = physique();
    v.vitesse *= -ph.choc_rebond;
    v.chocs++;
    endommager(v, Math.round(force * ph.choc_degats_par_px), null);
    Entites.poussiere(v.x + Math.cos(v.angle) * v.def.longueur / 2, v.y + Math.sin(v.angle) * v.def.longueur / 2, 6);
    if (v.conducteur === B.joueur) {
      B.cam.secousse = Math.min(1.2, force * 0.3);
      Entree.vibrer(Math.round(force * 12));
      if (force >= ph.ejection_vitesse_min && v.def.ejecte) ejecter(B.joueur, v);
    }
    Son.SFX.choc();
  }

  function heurterVehicules(v) {
    const ph = physique();
    const miens = cercles(v);
    const portee = v.def.longueur + 20;
    for (const autre of Entites.autour(v.x, v.y, portee, function (e) { return e.type === 'vehicule' && e !== v; })) {
      // Le char au bout du cable n'est pas un obstacle : il est accroche.
      if (autre === v.remorque || autre === v.remorqueePar) continue;
      const siens = cercles(autre);
      for (const a of miens) {
        for (const b of siens) {
          const dx = b.x - a.x, dy = b.y - a.y;
          const d2 = dx * dx + dy * dy, min = a.r + b.r;
          if (d2 >= min * min || d2 === 0) continue;
          const d = Math.sqrt(d2), nx = dx / d, ny = dy / d, chevauche = min - d;
          const m1 = v.def.masse, m2 = autre.def.masse, total = m1 + m2;
          // Sur des rails : on ne se pousse pas. ⚠️ L'AUTOBUS D'UNE LIGNE AUSSI est
          // sur des rails (`Autobus.conduire`). Il n'y etait pas : un velo du trafic
          // qui perdait patience derriere lui (`force`) le poussait de deux pixels
          // pendant qu'il attendait le feu — assez pour mettre son nez dans le
          // carrefour, ou le sortir de son trace (`test_autobus_js`, 17 sept. 2026).
          const surDesRails = function (q) { return q.conducteur === 'trafic' || q.conducteur === 'ligne'; };
          if (surDesRails(v) && surDesRails(autre)) return;
          v.x -= nx * chevauche * (m2 / total); v.y -= ny * chevauche * (m2 / total);
          autre.x += nx * chevauche * (m1 / total); autre.y += ny * chevauche * (m1 / total);
          const relatif = (v.vx - autre.vx) * nx + (v.vy - autre.vy) * ny;
          // ⚠️ Le trafic ne s'entretue pas : deux chars sur leurs rails qui se
          // frolent a un coin se poussent, sans degats. Les chocs qui comptent
          // sont ceux ou le joueur est au volant d'un des deux.
          const joueurImplique = v.conducteur === B.joueur || autre.conducteur === B.joueur;
          if (relatif > ph.choc_vitesse_min && joueurImplique) {
            const degats = Math.round(relatif * ph.choc_degats_par_px);
            endommager(autre, degats, v.conducteur === B.joueur ? B.joueur : null);
            endommager(v, Math.round(degats * 0.6), autre.conducteur === B.joueur ? B.joueur : null);
            v.chocs++; autre.chocs++;
            v.vx -= nx * relatif * 0.6; v.vy -= ny * relatif * 0.6;
            autre.vx += nx * relatif * 0.6 * (m1 / m2); autre.vy += ny * relatif * 0.6 * (m1 / m2);
            v.vitesse *= 0.5; autre.vitesse *= 0.7;
            Son.SFX.choc();
            if (v.conducteur === B.joueur) {
              B.cam.secousse = 0.7;
              if (autre.alarme === 0 && autre.def.alarme && !autre.conducteur) declencherAlarme(autre);
              if (relatif > 2) Police.signalerCrime('conduite_dangereuse', v.x, v.y, Police.quelqu_un_voit(v.x, v.y, null));
            }
            if (autre.conducteur === 'trafic') autre.klaxonT = 30;
          }
          return;   // un contact par image suffit
        }
      }
    }
  }

  /** Les gens : bouscules a basse vitesse, renverses au-dela. Les enfants,
      eux, ne sont que bouscules — c'est la regle. */
  function heurterPietons(v) {
    const ph = physique();
    const vitesse = Math.hypot(v.vx, v.vy);
    for (const c of cercles(v)) {
      for (const p of Entites.autour(c.x, c.y, c.r + 8, function (e) {
        return (e.type === 'pieton' || (e.type === 'joueur' && !e.dansVehicule)) && e.vivant;
      })) {
        const dx = p.x - c.x, dy = p.y - c.y;
        const d = Math.hypot(dx, dy) || 1, min = c.r + p.r;
        if (d >= min) continue;
        const nx = dx / d, ny = dy / d;
        p.x = c.x + nx * min; p.y = c.y + ny * min;
        // ⚠️ PAS HORS DE LA CARTE : un char gare qui chevauche le joueur au ras du
        // bord nord le poussait a y = -3,5, dans le « mur » du dehors (le singe l'a
        // trouve, graine 1, le 21 sept. 2026). La meme borne que pour tout ce qui marche.
        Entites.dansLaCarte(p);
        // ⚠️ UNE AUTO DE PATROUILLE NE RENVERSE PAS SES AGENTS : elle les pousse
        // hors de sa carrosserie, c'est tout. L'equipage descend d'une auto
        // arretee (`Police.commandes`) ; ceci n'est que le filet — un agent reste
        // au flanc d'une auto qui repart, une autre patrouille le frole.
        if (v.conducteur === 'police' && p.agent) continue;
        if (vitesse >= ph.renverse_vitesse_min && !p.intouchable && p.etat !== 'assomme') {
          const degats = Math.round(vitesse * ph.renverse_degats_par_px);
          const avant = p.vivant;
          Entites.blesser(p, degats, v.conducteur === B.joueur ? B.joueur : v, {
            renverse: true, angle: Math.atan2(v.vy, v.vx), saigne: 60,
          });
          p.vx = v.vx * 1.2; p.vy = v.vy * 1.2;
          v.vitesse *= 0.85;
          if (v.conducteur === B.joueur && p.type === 'pieton') {
            const type = (avant && !p.vivant) ? 'renversement_mortel' : 'renversement';
            Police.signalerCrime(type, p.x, p.y, Police.quelqu_un_voit(p.x, p.y, p));
            B.cam.secousse = 0.5;
          }
        } else if (p.type === 'pieton' && vitesse > 0.3 && p.etat === 'flane') {
          p.etat = 'fuit'; p.menace = v; p.minuterie = 90; p.cri = 60;
        }
      }
    }
  }

  // --- Degats, feu, explosion ------------------------------------------------------

  /** Un char ASSURE qui disparait — brule, plie, coule — ouvre une
      reclamation (`Missions.charPerdu`). Ecrit une fois : les trois sorties
      du monde passent ici, sinon la fraude ne marcherait qu'a l'explosion. */
  function perdu(v) {
    if (v.assure && typeof Missions !== 'undefined' && Missions.charPerdu) Missions.charPerdu(v);
  }

  /** La triche VEHICULES INVINCIBLES (`Hud.menuDebug`) : le char que le JOUEUR
      CONDUIT — pas le trafic, pas la police, pas le fuyard d'une mission qu'il
      faut justement abimer. ⚠️ `B.joueur &&` : un char gare a `conducteur ===
      null` serait sinon « conduit » par un joueur qui n'existe pas encore. */
  function blinde(v) {
    return triche('vehicules') && !!B.joueur && v.conducteur === B.joueur;
  }

  function endommager(v, degats, source) {
    if (v.etat === 'epave' || degats <= 0 || blinde(v)) return;
    v.vie -= degats;
    if (source) v.agresseur = source;
    if (v.vie > 0) return;
    // ⚠️ Ce qui n'a pas de reservoir ne brule pas et n'explose pas : ca se
    // PLIE. C'est la fiche qui le dit (`reservoir`), pas un `slug === 'velo'`
    // cache ici — le jour ou une trottinette arrive, elle se plie toute seule.
    if (v.def.reservoir === false) plier(v); else exploser(v);
  }

  /** Un char sans reservoir a zero PV : il tombe sur le cote, tordu, et c'est
      tout. Pas de feu, pas de fumee, pas de secousse, pas de deflagration —
      et surtout AUCUN DELIT : on renversait un velo, et la police arrivait
      pour une explosion a deux etoiles. */
  function plier(v) {
    v.etat = 'epave';
    perdu(v);
    // ⚠️ Le cable lache : sans ca, un char reste accroche a une carcasse
    // que plus personne ne met a jour, et le trafic ne l'oublie jamais.
    if (v.remorque) decrocher(v);
    if (v.remorqueePar) decrocher(v.remorqueePar);
    v.vie = 0;
    v.vitesse = 0; v.vx = 0; v.vy = 0;
    v.plie = true;
    v.swaps = nuances('#4a4a52');
    v.angle += (B.rng() - 0.5) * 1.6;      // il gît de travers : on voit qu'il est tombe
    v.epaveT = physique().epave_secondes * 60;
    v.alarme = 0;
    for (let i = 0; i < 8; i++) {
      const a = B.rng() * Math.PI * 2, s = 0.4 + B.rng();
      Entites.particule(v.x, v.y, Math.cos(a) * s, Math.sin(a) * s * 0.6, 16 + B.rng() * 10, '#8a8a8a', 1, 0.06);
    }
    Son.SFX.choc();
    if (v.conducteur && v.conducteur !== 'trafic') descendre(v.conducteur, true);
    if (v.conducteur === 'trafic') v.conducteur = null;
  }

  /** Un char du trafic qui nous passe pres : on l'entend passer, une fois. */
  function bruitDePassage(v) {
    const j = B.joueur;
    if (!j || v.conducteur !== 'trafic' || Math.abs(v.vitesse) < 0.8) return;
    const d2 = dist2(v.x, v.y, j.x, j.y);
    if (d2 > 90 * 90) { v.passeT = 0; return; }
    if (v.passeT > 0) { v.passeT--; return; }
    v.passeT = 240;
    const slug = v.def.classe === 'velo' ? 'sonnette' : (v.def.classe === 'moto' ? 'passage_moto' : 'passage_auto');
    Son.jouerA(slug, v.x, v.y, 160);
  }

  /** Un char dans l'eau COULE. ⚠️ Et il est PERDU : on ne le retrouve ni au
      fond, ni a la fourriere. Sinon couler devient le moyen commode de se faire
      rembourser une epave — on pousse sa carcasse a l'eau et on va la racheter
      au lot pour le prix d'un remorquage.

      ⚠️ Le BATEAU, lui, flotte, et c'est sa fiche qui le dit (`eau`, deja la
      pour sa friction et son adherence). Une classe ecrite ici en aurait fait
      une deuxieme verite a tenir a jour. */
  function majNoyade(v) {
    const n = B.defs.recherche.nage;
    if (v.def.eau || !Monde.estEau(Math.floor(v.x / TT), Math.floor(v.y / TT))) {
      v.coule = 0;
      return false;
    }
    // ⚠️ Couler, c'est DISPARAITRE : une triche qui laisse la baie manger le char
    // n'est pas invincible. Il roule sur l'eau, sans un remous.
    if (blinde(v)) { v.coule = 0; return false; }
    if (!v.coule) {
      Entites.remous(v.x, v.y, 14);
      // ⚠️ Il entrait dans l'eau SANS UN BRUIT : le HUD ecrivait « IL COULE —
      // SORS » et l'oreille n'avait rien entendu — or c'est l'oreille qui
      // aurait du le dire la premiere. Le char du joueur a droit au son avec
      // son filet ; celui du voisin est POSE dans le monde, comme un passage.
      if (v.conducteur === B.joueur) { Son.SFX.char_a_l_eau(); Hud.message('IL COULE — SORS', 180); }
      else Son.jouerA('plongeon', v.x, v.y, 420);
    }
    // ⚠️ `(v.coule || 0) + 1`, jamais `v.coule++` : sur un char qui n'a jamais
    // touche l'eau le compteur n'existe pas, `undefined++` rend NaN, et NaN
    // n'est plus petit que rien — le char coulait A LA PREMIERE IMAGE, sans
    // qu'on ait le temps d'en sortir. C'est le juge qui l'a dit.
    v.coule = (v.coule || 0) + 1;
    // Il s'enfonce : il ralentit vite, et l'eau bout autour.
    v.vitesse *= 0.9; v.vx *= 0.9; v.vy *= 0.9;
    if (B.t % 5 === 0) Entites.remous(v.x + (B.rng() - 0.5) * 10, v.y + (B.rng() - 0.5) * 6, 2);
    // L'eau bout autour pendant qu'il s'enfonce — trois secondes, et on les
    // entend : c'est le temps qu'on a pour sortir.
    if (B.t % 20 === 0) Son.jouerA('nage', v.x, v.y, 300);
    if (v.coule < n.coule_s * 60) return false;
    // Au fond, et le dernier glouglou avec.
    //
    // ⚠️ `v.conducteur === 'joueur'` — la chaîne — N'ETAIT JAMAIS VRAI : partout
    // ailleurs le conducteur est l'ENTITE (`v.conducteur = j` dans `monter`), et
    // seul le trafic porte une chaîne. Trois lignes en dependaient, et le
    // silence n'etait pas la pire : « IL COULE — SORS » ne s'affichait jamais,
    // et surtout le joueur reste dans un char RETIRE des entites — sonde du
    // 14 sept. 2026 : `dansVehicule` pointe un char absent, `nage` est faux, et
    // il ne bouge plus d'un pixel. Couler dans son char etait un cul-de-sac.
    const j = B.joueur;
    if (v.conducteur === B.joueur) Son.SFX.couler();
    else Son.jouerA('couler', v.x, v.y, 420);
    if (j && j.dansVehicule === v) {
      descendre(j, true);
      j.x = v.x; j.y = v.y;
      j.nage = true;
      Entites.remous(j.x, j.y, 16);
      Hud.message('LE ' + v.def.nom.toUpperCase() + ' A COULÉ', 240);
    }
    Entites.remous(v.x, v.y, 18);
    perdu(v);
    Entites.retirer(v);
    return true;
  }

  /** Un NID-DE-POULE sous les roues : ca secoue, ca coute deux points de
      carrosserie, et on l'entend. ⚠️ Un repit apres chaque nid : sans lui, un
      char lent le paie a chaque image de la tuile, et un nid devient un piege
      au lieu d'un cahot. */
  function majNidDePoule(v) {
    const ph = physique();
    if (v.nidT > 0) { v.nidT--; return; }
    if (v.z > 2 || Math.hypot(v.vx, v.vy) < 0.8 || B.interieur) return;
    if (!Monde.nidDePoule(Math.floor(v.x / TT), Math.floor(v.y / TT))) return;
    v.nidT = ph.nid_repit_images;
    endommager(v, ph.nid_degats, null);
    Son.SFX.nid_de_poule();
    if (v.conducteur === B.joueur) {
      B.cam.secousse = Math.max(B.cam.secousse, ph.nid_secousse);
      Entree.vibrer(60);
    }
  }

  /** Une PLAQUE D'ACIER sous les roues (la tranchée d'un chantier) : ça claque et
      ça secoue, et ça ne coûte RIEN — un nid-de-poule est un accident, une plaque
      est un décor qu'on sent. ⚠️ Même règle de répit que les nids (sans lui un char
      lent la claquerait à chaque image de la tuile), et le claquement part POSÉ
      là où roule le char : le trafic aussi claque, et s'entend à la distance. Ce
      qui secoue la caméra, lui, est le char du joueur. */
  function majPlaque(v) {
    const ph = physique();
    if (v.plaqueT > 0) { v.plaqueT--; return; }
    if (v.z > 2 || Math.hypot(v.vx, v.vy) < 0.8 || B.interieur) return;
    if (!Monde.plaqueDAcier(Math.floor(v.x / TT), Math.floor(v.y / TT))) return;
    v.plaqueT = ph.plaque_repit_images;
    Son.SFX.chantier('plaque', v.x, v.y, 300);
    if (v.conducteur === B.joueur) {
      B.cam.secousse = Math.max(B.cam.secousse, ph.plaque_secousse);
      Entree.vibrer(40);
    }
  }

  /** Un TAS DE TERRE sous les roues (le chantier) : une rampe naturelle. Le char
      décolle doucement, ne perd ni vitesse ni carrosserie, et retombe plus loin.

      ⚠️ Le saut est PLAFONNÉ, il ne se mesure pas (`tas_hauteur_max` : moins que les
      6 px au-delà desquels un char passe AU-DESSUS des tuiles) : un mur retient
      toujours ce qui retombe, et un tas au bord d'un lot ne lance personne dans une
      façade. Même répit que les nids, et seulement au sol : en l'air, rien. */
  function majTas(v) {
    const ph = physique();
    if (v.tasT > 0) { v.tasT--; return; }
    if (v.z > 0 || v.vz !== 0 || v.rails || B.interieur) return;
    const vit = Math.hypot(v.vx, v.vy);
    if (vit < ph.tas_vitesse_min) return;
    for (const c of cercles(v, v.x, v.y)) {
      for (const d of Entites.decorAutour(c.x, c.y, c.r + 26)) {
        const fiche = DECORS[d.decor] || {};
        if (!fiche.rampe || d.brise) continue;
        if (Math.hypot(d.x - c.x, d.y - c.y) > c.r + fiche.rampe) continue;
        v.vz = Math.min(vit, ph.tas_vitesse_max) * ph.tas_impulsion;
        v.tasT = ph.tas_repit_images;
        Entites.poussiere(v.x, v.y, 5);
        Son.SFX.chantier('tas', v.x, v.y, 300);
        if (v.conducteur === B.joueur) {
          B.cam.secousse = Math.max(B.cam.secousse, ph.tas_secousse);
          Entree.vibrer(30);
        }
        return;
      }
    }
  }

  /** L'heure de la panne finie, le char s'en va — il s'efface, faute de savoir
      rentrer au garage tout seul.

      ⚠️ **MAIS PAS SOUS CELUI QUI LE TIENT.** Le compte a rebours retirait le
      char de la ville sans regarder qui etait dedans : on montait dans la
      remorqueuse en panne, et elle disparaissait sous le joueur — qui restait
      accroche (`dansVehicule`) a une entite absente de `B.entites`, donc plus
      mise a jour ni dessinee : invisible, immobile, et rien pour le lui dire.
      La charge sur la fourche et un char de mission s'en allaient pareil.

      ⚠️ **Tenu, il cesse simplement d'ETRE EN PANNE** (`panneT` est deja a zero
      ici : ses feux s'eteignent) et redevient un char ordinaire — c'est
      `peupler` qui l'oubliera, loin et hors champ, comme tous les autres. La
      liste est exactement la sienne, et ce n'est pas un hasard : « qui tient ce
      char ? » n'a pas deux reponses selon qui pose la question. */
  function majFinDePanne(v) {
    if (--v.panneT > 0) return;
    if (v.conducteur === B.joueur || v.remorque || v.remorqueePar || v.mission) return;
    Entites.retirer(v);
  }

  function majEtatDuChar(v) {
    const ph = physique();
    bruitDePassage(v);
    majNidDePoule(v);
    majPlaque(v);
    majTas(v);
    if (v.forceT > 0) v.forceT--;
    if (v.panneT > 0) majFinDePanne(v);
    if (majNoyade(v)) return;
    if (v.etat === 'epave') {
      if (v.epaveT > 0) v.epaveT--;
      // ⚠️ Une carcasse fume — sauf celle qui n'avait rien a bruler. Un velo
      // plie sur le trottoir ne degage pas une colonne de fumee noire.
      if (v.def.reservoir !== false && B.t % 6 === 0) Entites.particule(v.x + (B.rng() - 0.5) * 14, v.y - 4, (B.rng() - 0.5) * 0.3, -0.2, 40, '#3a3a3a', 2, -0.01);
      return;
    }
    const part = v.vie / v.vieMax;
    // ⚠️ Sans reservoir, pas de feu ni de fumee : un velo cabosse au bord du
    // trottoir ne s'enflamme pas tout seul, et rien ne le ronge jusqu'a zero.
    const brule = v.def.reservoir !== false;
    if (brule && part < ph.feu_sous) {
      if (B.t % 3 === 0) Entites.particule(v.x + (B.rng() - 0.5) * 10, v.y - 6, (B.rng() - 0.5) * 0.4, -0.5, 18, B.rng() < 0.5 ? '#ff8c1a' : '#ffd23a', 2, -0.02);
      if (B.t % 60 === 0) endommager(v, ph.feu_degats_par_seconde, v.agresseur);
    } else if (brule && part < ph.fumee_sous && B.t % 8 === 0) {
      Entites.particule(v.x + (B.rng() - 0.5) * 8, v.y - 6, (B.rng() - 0.5) * 0.3, -0.3, 30, '#8a8a8a', 2, -0.01);
    }
    if (v.alarme > 0) {
      v.alarme--;
      if (v.alarme % 40 === 0) Son.SFX.klaxon();
    }
    if (v.klaxonT > 0) { v.klaxonT--; if (v.klaxonT === 29) avertir(v); }
    soignerAuVolant(v);
  }

  // --- Le crochet de la remorqueuse ------------------------------------------------

  /** Le char qu'on peut accrocher : le plus proche DERRIERE soi, sans
      conducteur, dans `crochet_portee_px`. ⚠️ Derriere : un crochet est a
      l'arriere, et il faut donc reculer dessus — c'est le geste qui rend la
      remorqueuse autre chose qu'un camion. */
  function aCrocher(v) {
    const ph = physique();
    const ax = v.x - Math.cos(v.angle) * v.def.longueur / 2;
    const ay = v.y - Math.sin(v.angle) * v.def.longueur / 2;
    let meilleur = null, dMin = ph.crochet_portee_px * ph.crochet_portee_px;
    for (const e of Entites.autour(ax, ay, ph.crochet_portee_px + 30, function (q) { return q.type === 'vehicule'; })) {
      if (e === v || e.remorqueePar || e.remorque || e.conducteur) continue;
      const d = dist2(e.x, e.y, ax, ay);
      if (d < dMin) { dMin = d; meilleur = e; }
    }
    return meilleur;
  }

  /** Accrocher, ou decrocher si on traine deja quelque chose. ⚠️ UN SEUL a la
      fois : c'est la fiche qui le dit, et c'est ce qui empeche le train de
      douze chars qu'on ne saurait plus arreter. */
  function basculerCrochet(v) {
    if (v.remorque) { decrocher(v); return false; }
    const cible = aCrocher(v);
    if (!cible) { Hud.message('RIEN À ACCROCHER DERRIÈRE'); return false; }
    v.remorque = cible;
    cible.remorqueePar = v;
    cible.alarme = 0;
    Son.SFX.choc();
    Hud.message(cible.def.nom.toUpperCase() + ' ACCROCHÉ');
    return true;
  }

  function decrocher(v) {
    const t = v.remorque;
    v.remorque = null;
    if (!t) return;
    t.remorqueePar = null;
    // ⚠️ La fourche redescend : sans ca, le char reste en l'air, son ombre
    // decollee — et `bloqueParLesTuiles` le laisse traverser les murs, parce
    // qu'un char a plus de six pixels d'altitude est repute en plein saut.
    t.z = 0;
    Son.SFX.porte('vehicule');    // le crochet qui lache : de la tole, comme une portiere
  }

  /** Ou la charge se pose, exactement. ⚠️ UNE FOURCHE N'A PAS DE JEU : c'est
      un point fixe derriere la remorqueuse, dans SON axe — pas un point vers
      lequel on tire. Le jeu du cable est precisement ce qui trahissait la
      corde, bien avant qu'on regarde le dessin.

      ⚠️ Et ce qui a un `plateau` (la moto, le velo — c'est `vehicules.py` qui
      le dit) monte EN ENTIER : centre sur la remorqueuse, pas accroche
      derriere. On ne leve pas un deux-roues par l'avant, on le charge. */
  function placeDeLaCharge(v, t) {
    const ph = physique();
    if (t.def.plateau) {
      // Sur le plateau : legerement en arriere du centre, dans l'axe.
      const d = v.def.longueur * 0.18;
      return { x: v.x - Math.cos(v.angle) * d, y: v.y - Math.sin(v.angle) * d,
               angle: v.angle, z: ph.plateau_leve_px };
    }
    const d = ph.crochet_jeu_px + (v.def.longueur + t.def.longueur) / 2;
    return { x: v.x - Math.cos(v.angle) * d, y: v.y - Math.sin(v.angle) * d,
             angle: v.angle, z: ph.crochet_leve_px };
  }

  /** La charge passe-t-elle si la remorqueuse va la ? ⚠️ C'est la question que
      le cable permettait de ne pas poser : il s'etirait, et l'auto au bout
      traversait le mur. Rigide, la reponse change — LA REMORQUEUSE NE PASSE
      PAS. Le meme « tout ou rien » que `defoncerDevant`.

      Une charge SUR LE PLATEAU, elle, ne touche plus la route : c'est de la
      cargaison, et rien ne l'arrete. */
  function chargeBloquee(v, x, y, angle) {
    const t = v.remorque;
    if (!t || t.def.plateau) return false;
    const faux = { x: x, y: y, angle: angle === undefined ? v.angle : angle,
                   def: v.def, z: 0 };
    const place = placeDeLaCharge(faux, t);
    return bloqueParLesTuiles(t, place.x, place.y, place.angle);
  }

  function majCrochet(v) {
    const t = v.remorque;
    if (!t) return;
    if (!t.actif || t.remorqueePar !== v) { v.remorque = null; return; }
    const place = placeDeLaCharge(v, t);
    // ⚠️ Zero ecart : elle ne SUIT pas, elle EST posee. Un char qui rattrape
    // son point d'attache image apres image se traine toujours un peu de biais
    // — et ce biais-la est exactement ce qui fait « corde ».
    t.vx = place.x - t.x; t.vy = place.y - t.y;
    t.vitesse = v.vitesse;
    t.x = place.x; t.y = place.y;
    t.angle = place.angle;
    // ⚠️ `z`, c'est l'avant leve : `dessinerUn` sait deja dessiner plus haut en
    // laissant l'ombre au sol (il le fait pour les sauts). Deux pixels, et on
    // voit la fourche — sans un seul cap de sprite en plus.
    t.z = place.z;
    Entites.dansLaCarte(t);
  }

  /** L'ambulance rend des PV a qui la conduit — `soigne` de la fiche, en PV
      par seconde.

      ⚠️ Elle ne RESSUSCITE personne : un mort reste mort, et le boulot est
      perdu. C'est la seule chose que la fiche disait et qu'il fallait tenir —
      sinon l'ambulance devient la sortie de secours de toutes les fusillades,
      et l'hopital ne veut plus rien dire. */
  function soignerAuVolant(v) {
    if (!v.def.soigne || B.t % 60 !== 0) return;
    const c = v.conducteur;
    if (!c || c === 'trafic' || c === 'police' || !c.vivant) return;
    if (c.vie <= 0 || c.vie >= c.vieMax) return;
    c.vie = Math.min(c.vieMax, c.vie + v.def.soigne);
    if (c === B.joueur) B.partie.vie = c.vie;
  }

  function exploser(v) {
    const ph = physique();
    v.etat = 'epave';
    perdu(v);
    // ⚠️ Le cable lache : sans ca, un char reste accroche a une carcasse
    // que plus personne ne met a jour, et le trafic ne l'oublie jamais.
    if (v.remorque) decrocher(v);
    if (v.remorqueePar) decrocher(v.remorqueePar);
    v.vie = 0;
    v.vitesse = 0; v.vx = 0; v.vy = 0;
    v.swaps = Object.assign(nuances('#2a2a2a'), { v: '#1a1a1e', l: '#2a2a2a', t: '#2a2a2a', x: '#2a2a2a', y: '#2a2a2a', G: '#1a1a1e', B: '#2a2a2a', M: '#2a2a2a' });
    v.epaveT = ph.epave_secondes * 60;
    v.alarme = 0;
    for (let i = 0; i < 40; i++) {
      const a = B.rng() * Math.PI * 2, s = 1 + B.rng() * 3;
      Entites.particule(v.x, v.y, Math.cos(a) * s, Math.sin(a) * s * 0.6, 30 + B.rng() * 20, i % 3 ? '#ff8c1a' : '#3a3a3a', 2 + (i % 2), 0.1);
    }
    Entites.decal(v.x, v.y, 'impact');
    Son.SFX.explosion();
    B.cam.secousse = Math.max(B.cam.secousse, 1.2);
    const coupable = v.agresseur === B.joueur ? B.joueur : null;
    for (const e of Entites.autour(v.x, v.y, ph.explosion_rayon_px, function (q) { return q !== v && q.vivant; })) {
      const d = Math.hypot(e.x - v.x, e.y - v.y);
      const part = 1 - d / ph.explosion_rayon_px;
      if (e.type === 'vehicule') endommager(e, Math.round(ph.explosion_degats * part), coupable);
      else if (e.type === 'pieton' || e.type === 'joueur') {
        if (e.dansVehicule === v) descendre(e, true);
        Entites.blesser(e, Math.round(ph.explosion_degats * part), coupable || v, { renverse: true, angle: angleVers(v.x, v.y, e.x, e.y), saigne: 120 });
      }
    }
    // ⚠️ Le DECOR aussi. `Entites.autour(..., q.vivant)` ne le voit pas — le
    // decor ne vit pas — et une explosion qui laisse le lampadaire debout au
    // milieu du cratere ne se croit pas une seconde.
    for (const d of Entites.decorAutour(v.x, v.y, ph.explosion_rayon_px)) {
      if (d.brise) continue;
      const part = 1 - Math.hypot(d.x - v.x, d.y - v.y) / ph.explosion_rayon_px;
      if (part <= 0) continue;
      Entites.endommagerDecor(d, Math.round(ph.explosion_degats * part));
    }
    if (v.conducteur && v.conducteur !== 'trafic') descendre(v.conducteur, true);
    if (v.conducteur === 'trafic') { v.conducteur = null; }
    if (coupable) {
      Police.signalerCrime('explosion', v.x, v.y, true);
      Entites.alerter(v.x, v.y, coupable, 3);
    }
  }

  function declencherAlarme(v) {
    // ⚠️ `alarme_s` de la fiche : la berline de luxe hurle deux fois et demie
    // plus longtemps que les autres. C'est le prix de la meilleure revente.
    v.alarme = (v.def.alarme_s || physique().alarme_secondes) * 60;
    Son.SFX.klaxon();
    // L'alarme est un canal de detection : qui l'entend le sait.
    const rayon = B.defs.recherche.vision.alarme_rayon * TT;
    const entendue = Entites.pietonsAutour(v.x, v.y, rayon).some(function (e) { return e.etat !== 'assomme'; });
    return entendue;
  }

  // --- Monter, descendre, ejecter ---------------------------------------------------

  function vehiculeSousLaMain(j) {
    const portee = physique().portee_monter_px;
    let meilleur = null, dMin = Infinity;
    // ⚠️ Une rame de tramway ne se vole pas : sur ses rails, elle n'irait nulle part
    // ailleurs, et hors de ses rails ce n'est plus un tramway. On y MONTE a l'arret.
    for (const v of Entites.autour(j.x, j.y, portee + 20, function (e) { return e.type === 'vehicule' && e.etat !== 'epave' && !e.rails; })) {
      for (const c of cercles(v)) {
        const d = Math.hypot(c.x - j.x, c.y - j.y) - c.r;
        if (d < dMin && d <= portee && faceA(j, c.x, c.y)) { dMin = d; meilleur = v; }
      }
    }
    return meilleur;
  }

  function monter(j, v) {
    if (!v || v.etat === 'epave' || j.dansVehicule) return false;
    // Le volant part droit : on n'herite pas du braquage de celui d'avant.
    v.volant = 0;
    // ⚠️ ON NE MONTE PAS DANS UN CHAR REMORQUE. Rien ne l'interdisait, et ce
    // serait la facon la plus courte de casser la physique : deux conducteurs,
    // deux volontes, un seul lien rigide. Et le refus SE DIT — une porte qui ne
    // s'ouvre pas sans un mot se lit comme un bogue.
    if (v.remorqueePar) { Hud.message('IL EST SUR LA FOURCHE'); return false; }
    let crime = null, vu = false;
    if (v.conducteur === 'trafic' && v.def.classe === 'velo') {
      // On prend le velo au cycliste : il tombe, il a tout vu, il le dit.
      // ⚠️ C'est CELUI QUI ETAIT DESSUS qui tombe : il garde ses couleurs. Un
      // cycliste tire au hasard a la chute aurait change de tete en touchant
      // le sol.
      const arch = Entites.archetypeDeRue(v.x, v.y, hash2(Math.round(v.x), Math.round(v.y)) / 4294967296);
      const cycliste = Entites.creerPieton(v.x, v.y + 10,
        v.pilote && v.pilote.swaps ? Object.assign({}, arch, { couleurs: v.pilote.swaps }) : arch);
      v.pilote = null;
      cycliste.etat = 'temoin'; cycliste.menace = j; cycliste.minuterie = 600; cycliste.cri = 120;
      cycliste.recul = 14; cycliste.vx = 0; cycliste.vy = 1.5;
      crime = 'vol_vehicule'; vu = true;
    } else if (v.conducteur === 'trafic' || v.conducteur === 'ligne') {
      // Carjacking : le conducteur sort, temoigne, et fuit. Pas besoin de temoin :
      // la victime en est un.
      // ⚠️ Sur une MOTO, on VOIT celui qui est dessus : c'est lui qui descend,
      // avec ses couleurs, et il quitte la selle. Sans `v.pilote = null`, le
      // joueur le cachait tant qu'il roulait et il reapparaissait assis sur la
      // moto des qu'on en descendait.
      // ⚠️ **C'EST CELUI QUI CONDUIT QUI DESCEND** : la conductrice du cabriolet, en
      // robe rose, et pas un passant tire au hasard qui aurait ses couleurs. Elle
      // dit son identite (`pilote.arch`) ; un pilote sans nom — le trafic ordinaire,
      // le voleur d'une moto — reste un passant de la rue.
      const arch = v.pilote && v.pilote.arch ? Entites.archetype(v.pilote.arch) : Entites.archetypeDeRue();
      const victime = Entites.creerPieton(v.x + Math.cos(v.angle + Math.PI / 2) * 14, v.y + Math.sin(v.angle + Math.PI / 2) * 14,
        v.pilote && v.pilote.swaps ? Object.assign({}, arch, { couleurs: v.pilote.swaps }) : arch);
      v.pilote = null;
      victime.etat = 'temoin'; victime.menace = j; victime.minuterie = 600; victime.cri = 120;
      crime = 'carjacking'; vu = true;
    } else if (v.conducteur === null && !v.vole && !v.aToi) {
      // ⚠️ `aToi` : un char PAYE devant un guichet. Sans lui, racheter le sien
      // a la fourriere puis monter dedans etait un `vol_vehicule` — et le
      // comptoir ne servait plus a rien : autant sauter la cloture.
      crime = 'vol_vehicule';
      vu = Police.quelqu_un_voit(v.x, v.y, null);
      if (v.def.alarme && declencherAlarme(v)) vu = true;
    }
    // Changer de char hors de vue : la police perd ta trace d'une etoile.
    const r = B.recherche, deg = B.defs.recherche.deguisement;
    if (r.etoiles > 0 && r.vu > deg.vehicule_s * 60) { r.etoiles = Math.max(0, r.etoiles - deg.vehicule_etoiles); r.vu = 0; Hud.message('ILS T’ONT PERDU DE VUE'); }
    v.conducteur = j; v.etat = 'roule'; v.vole = v.vole || !!crime; v.cible = null;
    v.laisse = false; v.malGareT = 0;              // on le reprend : le chrono repart de zero
    j.dansVehicule = v;
    // ⚠️ Le dernier char conduit, pour la fourriere : la police te SORT
    // du char avant de t'arreter, donc a l'arrestation `dansVehicule` est
    // deja nul — sans ce souvenir, on ne saisirait jamais rien.
    j.dernierVehicule = v; j.dessine = false; j.vx = 0; j.vy = 0;
    j.x = v.x; j.y = v.y;
    if (crime) { Police.signalerCrime(crime, v.x, v.y, vu); B.partie.stats.volees++; }
    // ⚠️ L'etiquette du bouton tactile suit l'avertisseur : SIRENE, SONNETTE, KLAXON.
    Entree.contexte(v.def.sirene ? 'vehicule_sirene' : v.def.klaxon === 'sonnette' ? 'vehicule_sonnette' : 'vehicule');
    bruitDeMontee(v);
    if (v.def.classe !== 'velo') Son.boucle(boucleDeMoteur(v), true, 0.6);
    if (v.def.radio) { Son.Ambiance.arreter(); Son.Radio.jouer(v.def.radio); }
    Hud.message(v.def.nom.toUpperCase());
    return true;
  }

  /** La boucle de moteur d'un char — ou d'une COQUE. ⚠️ La chaloupe de la
      3e vague tournait au ralenti d'une AUTO : un hors-bord n'a ni boite ni
      silencieux, il cogne et il crachote, et c'est le seul moteur du jeu qu'on
      entende par-dessus de l'eau. Le reste ne change pas : meme montee dans les
      tours, meme hauteur qui suit la vitesse. */
  function boucleDeMoteur(v) { return v.def.classe === 'bateau' ? 'moteur_bateau' : 'moteur'; }

  /** Le bruit de la montee, et de la descente : la portiere d'un char — ou
      la bequille et le cadre d'une moto et d'un velo, qu'on enfourche.
      ⚠️ La FICHE decide (`portieres`, `vehicules.py`), pas un
      `slug === 'velo'` ici. */
  function bruitDeMontee(v) {
    if (v.def.portieres) Son.SFX.porte('vehicule'); else Son.SFX.enfourcher();
  }

  /** L'avertisseur du char, au bouton du klaxon : le klaxon, ou la sonnette
      d'un velo. ⚠️ C'est la fiche qui le nomme (`klaxon`, `vehicules.py`),
      et c'est un effet de `Son.SFX` — le trafic impatient passe par ici aussi.

      ⚠️ Retour de Martin : « réduit un peu les klaxon des voiture qui passe ».
      Celui du trafic partait au PLEIN volume, ou que soit le char : mesure au
      bord d'une rue du centre, 1 a 6 klaxons par minute, les deux tiers d'un
      char hors de l'ecran. Il suit donc la regle des coups des autres
      (`Son.depuis`) : muet hors champ, plus doux de loin. Le sien, au volant,
      reste plein volume. */
  function avertir(v) {
    const effet = Son.SFX[v.def.klaxon] || Son.SFX.klaxon;
    Son.depuis(v.conducteur === B.joueur ? B.joueur : v, effet);
  }

  /** Descendre : a gauche si c'est libre, sinon a droite, sinon derriere. */
  function descendre(j, force) {
    // ⚠️ UN PASSAGER DESCEND D'UN AUTOBUS, IL NE LE GARE PAS : la suite met le
    // char a l'arret, « laisse » pour la fourriere, et abandonne le boulot.
    if (j && j.passager) return Autobus.descendre(j, force);
    const v = j.dansVehicule;
    if (!v) return false;
    if (!force && Math.abs(v.vitesse) > 1.2) { v.vitesse *= 0.8; return false; }
    // ⚠️ SOUS LE TOIT D'UN GARAGE, les portieres donnent sur des murs : on ne descend
    // pas (on recule d'abord), et si on y est force — vendu chez Ti-Guy, une epave —
    // on ressort a pied par-dessous le rideau, dans la baie.
    const rideau = Monde.rideauDe(v);
    if (rideau && !force) { Hud.message('RECULE D’ABORD — T’ES SOUS LE TOIT'); return false; }
    const cotes = [v.angle + Math.PI / 2, v.angle - Math.PI / 2, v.angle + Math.PI];
    let pose = false;
    if (rideau) { const baie = Monde.baieDeLaPorteDeGarage(rideau); j.x = baie.x; j.y = baie.y; pose = true; }
    for (const a of (pose ? [] : cotes)) {
      const x = v.x + Math.cos(a) * (v.def.largeur / 2 + 8), y = v.y + Math.sin(a) * (v.def.largeur / 2 + 8);
      if (!Monde.bloque(Math.floor(x / TT), Math.floor(y / TT), Monde.MASQUE_PIETON)) { j.x = x; j.y = y; pose = true; break; }
    }
    if (!pose) { j.x = v.x; j.y = v.y + v.def.largeur; }
    v.conducteur = null;
    // ⚠️ UNE EPAVE RESTE UNE EPAVE. `exploser` et `plier` posent l'epave PUIS
    // font descendre celui qui etait au volant : ecrire `stationne` ici rendait
    // une carcasse. On y remontait, elle sautait une deuxieme fois, et une
    // mission dont le char venait d'exploser sous le joueur ne le voyait pas.
    if (v.etat !== 'epave') {
      v.etat = 'stationne';
      // ⚠️ « Laisse » : un char que LE JOUEUR a garé. La fourriere ne remorque
      // que ceux-la — remorquer le trafic viderait les rues sans que personne
      // comprenne pourquoi, et le juge du trafic le verrait avant le joueur.
      // Une epave, elle, n'est garee par personne.
      v.laisse = true;
    }
    j.dansVehicule = null; j.dessine = true;
    // ⚠️ Le meme appui ne doit pas nous faire REMONTER dans la meme image :
    // la fin de maj() regarde aussi le bouton ACTION.
    j.descenduT = B.t;
    Entites.dansLaCarte(j);
    Entree.contexte('pied');
    // ⚠️ LES DEUX, et pas seulement celui du char qu'on quitte : si la fiche
    // changeait de camp entre la montee et la descente (une coque remorquee,
    // un char devenu epave), le moteur resterait allume pour toujours a
    // l'autre bout de la ville. Eteindre ce qui ne joue pas ne coute rien.
    Son.boucle('moteur', false);
    Son.boucle('moteur_bateau', false);
    Son.Radio.arreter();
    // ⚠️ On ne relance pas l'ambiance unique : `Son.Chef` reprend la main a
    // la prochaine image, avec la musique du district ou l'on descend.
    Son.Chef.maj();
    if (!force) bruitDeMontee(v);
    if (typeof Missions !== 'undefined' && Missions.boulot) Missions.boulot.abandonner('BOULOT ABANDONNÉ');
    return true;
  }

  function ejecter(j, v) {
    const ph = physique();
    const vitesse = Math.hypot(v.vx, v.vy);
    descendre(j, true);
    j.x = v.x + Math.cos(v.angle) * (v.def.longueur / 2 + 6);
    j.y = v.y + Math.sin(v.angle) * (v.def.longueur / 2 + 6);
    j.vx = Math.cos(v.angle) * vitesse * 0.8; j.vy = Math.sin(v.angle) * vitesse * 0.8;
    j.roule = 18; j.invincible = 0;
    Entites.dansLaCarte(j);
    Entites.blesser(j, Math.round(vitesse * ph.renverse_degats_par_px * 0.5), null, { renverse: true, angle: v.angle });
    Hud.message('ÉJECTÉ !');
  }

  // --- Trafic : lire la carte, choisir, freiner ---------------------------------------

  function centre(tx, ty) { return { x: tx * TT + 8, y: ty * TT + 8, tx: tx, ty: ty }; }

  /** Peut-on sortir du croisement dans ce sens depuis cette tuile ? On avance
      tant qu'on est sur du '+' (le carrefour, ses passages pietons) et on veut
      trouver une voie dont la fleche va dans NOTRE sens — pas a contresens. */
  function peutSortir(tx, ty, sens, v) {
    const pas = PAS_FLECHE[sens];
    let x = tx, y = ty;
    for (let i = 0; i < 9; i++) {
      x += pas[0]; y += pas[1];
      // ⚠️ **UNE SORTIE BARREE N'EST PAS UNE SORTIE** (15 sept. 2026). Une
      // barriere fermee n'etait consultee que sur les voies : un char qui
      // abordait le pont DEPUIS LA BOITE du croisement sortait dessus sans
      // que rien ne le lui demande — et une fois sur le tablier il etait
      // DEDANS, donc exempte, et il traversait tout du long. Le juge du
      // demi-tour l'a attrape le jour ou les des ont change sa route ; le
      // trou, lui, etait la depuis le premier jour des barrieres.
      if (v && Monde.barriereBloque(v, x, y)) return false;
      const f = Monde.fleche(x, y);
      if (f === sens) return true;
      if (f !== '+') return false;
    }
    return false;
  }

  /** Cette sortie part-elle d'ici, ou d'une tuile plus loin TOUT DROIT dans la
      boite (`cap`) ? C'est la question que le tirage ne pose pas : une sortie
      que la boite n'a pas se decouvre au fond, et on y arrive trop tard. */
  function sortieDevant(tx, ty, cap, sens, v) {
    const p = PAS_FLECHE[cap];
    let x = tx, y = ty;
    for (let i = 0; i < 9 && Monde.fleche(x, y) === '+'; i++) {
      if (peutSortir(x, y, sens, v)) return true;
      x += p[0]; y += p[1];
    }
    return false;
  }

  /** Le trafic devant une barriere fermee fait DEMI-TOUR : la voie d'en face
      la plus proche, ou l'arret sur place s'il n'y en a pas. ⚠️ Sans ca, les
      chars s'empilaient devant les cones du pont jusqu'a la fin des temps. */
  function demiTour(v, tx, ty, p) {
    const arriere = FLECHE_DE[(-p[0]) + ',' + (-p[1])];
    let meilleur = null, coutMin = Infinity;
    for (let dy = -3; dy <= 3; dy++) {
      for (let dx = -3; dx <= 3; dx++) {
        if (Monde.fleche(tx + dx, ty + dy) !== arriere) continue;
        const cout = dx * dx + dy * dy;
        if (cout < coutMin) { coutMin = cout; meilleur = centre(tx + dx, ty + dy); }
      }
    }
    v.sortie = null;
    if (!meilleur) { v.attendFeu = true; return centre(tx, ty); }
    v.sens = arriere;
    return meilleur;
  }

  /** Le penchant de l'heure : positif le matin (on converge vers le coeur),
      negatif le soir (on s'en disperse), zero le reste du temps. */
  function pointeDuMoment() {
    const p = trafic().pointe;
    if (!p) return 0;
    const h = B.partie ? B.partie.heure : 0.5;
    if (h >= p.matin[0] && h < p.matin[1]) return p.penchant;
    if (h >= p.soir[0] && h < p.soir[1]) return -p.penchant;
    return 0;
  }

  /** Ou attendre pour que le NEZ touche la ligne d'arret, et pas un pixel de
      plus loin.

      ⚠️ **C'EST TOUTE LA FICHE « Les chars s'arretent avant le passage ».**
      La cible d'attente etait le CENTRE de la tuile de la ligne ; depuis que le
      trottoir fait une tuile, la traverse est collee a cette ligne, et tout ce
      qui depasse les huit pixels d'avant du char etait peint sur les bandes —
      mesure : 4,9 px pour une berline, 10 pour une remorqueuse, 12 pour un
      camion, et l'autobus couvrait la traverse entiere. On vise donc la ligne
      elle-meme (le bord LOIN de la tuile d'arret) moins la demi-longueur.

      ⚠️ **Jamais derriere soi** : arrive trop vite, ou surpris par un feu qui
      tourne, un char s'arrete OU IL EST. Un char qui recule devant un feu
      rouge n'existe pas dans la vraie rue, et il reculerait dans celui qui le
      suit. */
  function pointDArret(v, sx, sy, p) {
    const demi = v.def.longueur / 2;
    let x = sx * TT + 8 + p[0] * (8 - demi), y = sy * TT + 8 + p[1] * (8 - demi);
    if ((x - v.x) * p[0] + (y - v.y) * p[1] < 0) { x = v.x; y = v.y; }
    return { x: x, y: y, tx: sx, ty: sy };
  }

  /** On ne freine pas SEC a la vue du rouge : on GLISSE jusqu'a la ligne. La
      vitesse voulue fond avec ce qui reste a parcourir — sans elle, un long
      char, qui voit le feu une tuile avant la ligne, s'arreterait la ou il l'a
      vu, et la file entiere reculerait d'une tuile. */
  function approcheDeLaLigne(v) {
    if (!v.cible) return 0;
    const t = trafic();
    // ⚠️ **ET ON NE PEUT PAS DEPASSER LA LIGNE EN GLISSANT** : `rouler` avance
    // de `min(distance, vitesse)`, et la cible est le point d'arret lui-meme.
    // C'est ce qui a permis de JETER le garde qu'on avait ecrit ici (« ne pas
    // glisser dans le char d'en avant ») : aucune mutation ne le rougissait, et
    // pour cause — deux chars ne visent jamais le meme point d'arret, la
    // distance de securite les separe d'une tuile et demie bien avant.
    const reste = Math.hypot(v.cible.x - v.x, v.cible.y - v.y);
    // ⚠️ **SOUS LE PIXEL, ON EST ARRIVE.** Une vitesse proportionnelle au reste
    // ne l'atteint jamais tout a fait : elle le divise par quatre a chaque
    // image, et le char rampe des centiemes de pixel pour toujours. Or « a
    // l'arret complet » est ce qui fait tourner le compte du STOP
    // (`vitesse < 0,05`) — le char repartait donc six images trop tot, et le
    // juge du STOP de M3 l'a attrape. Un pixel, c'est arrive.
    if (reste < 1) return 0;
    return Math.min(t.approche_vitesse, reste * t.approche_part);
  }

  /** Faut-il attendre avant d'entrer dans le croisement ? Le feu, le panneau
      STOP (ou le clignotant rouge de la nuit), puis la boite libre — dans cet
      ordre, et c'est la SEULE lecture des trois. La ligne d'arret la fait sous
      ses roues ; la tuile d'avant la fait pour les longs chars, qui doivent
      freiner plus tot. */
  function attendreALaLigne(v, sens, inter) {
    const feu = inter ? Monde.feuDeCirculation(inter, sens) : 'vert';
    if (feu === 'rouge' || feu === 'jaune') { v.attenteBoite = 0; return true; }
    // Un STOP : le panneau — ou, la nuit, le feu qui CLIGNOTE ROUGE. On
    // s'immobilise d'abord, puis on repart : un clignotant n'est pas un mur,
    // et sans cette ligne le trafic de nuit attendait la fin des temps.
    if (inter && (inter.stop === sens || feu === 'clignote_rouge')) {
      if (v.stopT === undefined) v.stopT = trafic().arret_images;
      // ⚠️ Le compte ne tourne qu'a l'ARRET complet : sinon on comptait le
      // freinage et le char repartait sans s'etre vraiment immobilise.
      if (Math.abs(v.vitesse) < 0.05) v.stopT = Math.max(0, v.stopT - 1);
      if (v.stopT > 0) return true;
    }
    // ⚠️ Feu vert ou stop, on ne S'ENGAGE que si la boite est libre : deux
    // chars qui tournent a gauche de bouts opposes se retrouvaient nez a nez
    // au milieu, chacun attendant l'autre. Un croisement, un char a la fois.
    // Passe un long moment (un char stationne dans la boite), on y va quand meme.
    if (inter && !croisementLibre(inter, v)) {
      v.attenteBoite = (v.attenteBoite || 0) + 1;
      if (v.attenteBoite < trafic().patience_images * 2) return true;
    }
    return false;
  }

  /** La ligne d'arret de la tuile suivante, si elle est POUR NOUS — avec le
      croisement qu'elle garde. C'est elle qui permet de freiner AVANT d'entrer
      sur la ligne, et donc a un autobus de 48 px de s'y arreter le nez dessus.

      ⚠️ **UNE TUILE SUFFIT, ET C'EST MESURE — parce que le feu se relit a chaque
      image.** Le plus long du parc fait 48 px : son point d'arret tombe pile au
      centre de la tuile d'avant, donc il le voit venir des qu'il y met les
      roues. On a essaye d'en guetter deux ; aucune mutation ne rougissait, et
      une regle qu'aucun juge ne tient est une regle qu'on ne garde pas. Le jour
      ou un char plus long arrivera, c'est le juge du catalogue entier
      (`test_chaque_char_du_catalogue_s_arrete_le_nez_a_la_ligne`) qui le dira. */
  function ligneDevant(v, tx, ty, p) {
    const sx = tx + p[0], sy = ty + p[1];
    if (Monde.fleche(sx, sy) !== 'S' || Monde.sensArret(sx, sy) !== v.sens) return null;
    return { tx: sx, ty: sy, inter: Monde.intersectionA(sx + p[0], sy + p[1]) };
  }

  // --- Le velo : a la bordure, a gauche pour tourner a gauche, et hors de la rue -------
  //
  // ⚠️ Martin (21 sept. 2026) : « les velos peuvent passer dans les parcs, les
  // trottoirs, et restent souvent sur la bordure de la route, sauf pour virage a
  // gauche ». Le velo du trafic roulait au MILIEU de sa voie, comme une auto de
  // huit pixels de large, et ne quittait jamais les fleches. C'est toujours un
  // char sur des rails : on ne touche qu'aux CIBLES qu'on lui donne.
  //
  // ⚠️ **AUCUN DE.** Ou il tourne, s'il monte sur le trottoir, quel parc il
  // traverse : tout se lit a l'empreinte du cycliste et de l'endroit (`hash2`).

  /** Un velo que le TRAFIC mene. ⚠️ La classe, pas le slug — et pas celui du
      joueur, ni un fuyard de mission (`poursuite`), qui brule tout. */
  function estVeloDuTrafic(v) {
    return !!v.def && v.def.classe === 'velo' && v.conducteur === 'trafic' && !v.poursuite && !!trafic().velo;
  }

  /** Le hasard d'UN cycliste a UN endroit : stable, et gratuit pour les des du jeu. */
  function empreinteVelo(v, a, b) { return hash2((v.id * 7919 + a) | 0, b | 0) / 4294967296; }

  /** A droite de ce sens (on roule a droite) : le pas vers le trottoir. */
  function droiteDe(p) { return [-p[1], p[0]]; }

  //: Le bras d'un croisement par ou l'on SORT dans ce sens.
  const BRAS_DU_SENS = { '^': 'N', 'v': 'S', '<': 'O', '>': 'E' };

  /** Ou ce cycliste ira au croisement qu'il a devant : tout droit, a droite, a
      gauche — dans l'ordre ou il les essaiera. Les memes parts ET le meme repli
      que le reste du trafic (`prochaineCible`, la boite : « tout droit, sinon a
      gauche »), mais tirees a l'empreinte, et d'abord parmi les bras qui
      EXISTENT : se ranger a gauche devant un T sans gauche, c'est se ranger pour
      rien. La boite, elle, prend ensuite la premiere de la liste qui en part
      (`sortieDevant`). */
  function ordreDuVelo(v, inter, sens) {
    const p = PAS_FLECHE[sens];
    const vers = { droit: sens, droite: FLECHE_DE[(-p[1]) + ',' + p[0]], gauche: FLECHE_DE[p[1] + ',' + (-p[0])] };
    const tirage = empreinteVelo(v, inter.x * 4099 + inter.y, 17);
    const ordre = tirage < 0.55 ? ['droit', 'gauche', 'droite'] : tirage < 0.78 ? ['droite', 'droit', 'gauche'] : ['gauche', 'droit', 'droite'];
    const bras = inter.bras || 'NSOE';
    return ordre.filter(function (c) { return bras.indexOf(BRAS_DU_SENS[vers[c]]) >= 0; }).concat(
      ordre.filter(function (c) { return bras.indexOf(BRAS_DU_SENS[vers[c]]) < 0; }));
  }

  /** L'intention du cycliste au prochain croisement — lue AVANT la ligne
      d'arret, a `virage_tuiles` : c'est ce qui lui laisse le temps de se ranger
      a gauche. On l'oublie des qu'on a traverse la boite. */
  function intentionDuVelo(v, tx, ty, p) {
    if (v.intention && v.intention.dedans) v.intention = null;
    if (v.intention) return v.intention;
    const n = trafic().velo.virage_tuiles;
    for (let k = 1; k <= n; k++) {
      const sx = tx + p[0] * k, sy = ty + p[1] * k, f = Monde.fleche(sx, sy);
      if (f === 'S') {
        if (Monde.sensArret(sx, sy) !== v.sens) return null;
        const inter = Monde.intersectionA(sx + p[0], sy + p[1]);
        if (!inter) return null;
        v.intention = { inter: inter, sens: v.sens, ordre: ordreDuVelo(v, inter, v.sens), dedans: false };
        return v.intention;
      }
      if (f !== v.sens) return null;        // la voie finit ou tourne : rien de droit devant
    }
    return null;
  }

  /** +1 : a la bordure (a droite). -1 : a gauche — il va tourner a gauche, et
      il roule encore dans le sens d'ou il arrive (la boite comprise, jusqu'au
      virage). */
  function coteDuVelo(v) {
    const i = v.intention;
    return i && i.ordre[0] === 'gauche' && v.sens === i.sens ? -1 : 1;
  }

  /** La cible, tassee vers la bordure (ou vers la ligne du milieu).

      ⚠️ **SUR PLACE, IL GARDE SON COTE.** Une cible a moins d'un pixel devant
      — ou derriere — est le point d'arret d'un velo arrive a la ligne : la
      tasser le ferait glisser de travers au feu, et la laisser au milieu de la
      voie le ramenait au milieu, trois pixels en crabe, le temps du rouge. On
      la pose sur SA ligne a lui. */
  function aLaBordure(v, c) {
    if (!c || v.horsRue) return c;
    const p = PAS_FLECHE[v.sens];
    if (!p) return c;
    const q = droiteDe(p);
    if ((c.x - v.x) * p[0] + (c.y - v.y) * p[1] <= 1) {
      const lat = (v.x - c.x) * q[0] + (v.y - c.y) * q[1];
      return { x: c.x + q[0] * lat, y: c.y + q[1] * lat, tx: c.tx, ty: c.ty };
    }
    const d = trafic().velo.bord_px * coteDuVelo(v);
    return { x: c.x + q[0] * d, y: c.y + q[1] * d, tx: c.tx, ty: c.ty };
  }

  /** Le pas lateral vers la voie qu'il VEUT : celle du trottoir d'ordinaire,
      celle du milieu s'il va tourner a gauche. null s'il y est deja, ou si la
      voisine n'est pas libre. Les memes gardes que le deport (`voieDeDepassement`) :
      la voisine et la tuile d'apres dans notre sens, pas de barriere. */
  function voieDuVelo(v, tx, ty, p) {
    if (v.deportFroid > 0 || v.deportT > 0) return null;       // il vient de contourner quelque chose
    const d = droiteDe(p), c = coteDuVelo(v), q = [d[0] * c, d[1] * c];
    if (Monde.fleche(tx + q[0], ty + q[1]) !== v.sens) return null;
    if (Monde.fleche(tx + q[0] + p[0], ty + q[1] + p[1]) !== v.sens) return null;
    if (Monde.barriereBloque(v, tx + q[0], ty + q[1]) || Monde.barriereBloque(v, tx + q[0] + p[0], ty + q[1] + p[1])) return null;
    return voieLibre(v, tx + q[0], ty + q[1], p) ? q : null;
  }

  /** Une tuile ou un velo roule hors de la chaussee : le trottoir (pas la
      traverse, qui est de la route) et l'allee de parc — ni l'herbe, ou l'on
      seme les arbres, les bancs et les buissons, ni l'abord, ou se range le
      mobilier. Jamais le coin d'un croisement (ses poteaux, ses traverses), et
      rien de pose dessus : sur des rails, il passerait au travers. */
  function roulableHorsRue(tx, ty) {
    const c = Monde.carte;
    if (!c || tx < 1 || ty < 1 || tx >= c.w - 1 || ty >= c.h - 1) return false;
    if (Monde.bloque(tx, ty, Monde.MASQUE_VEHICULE) || Monde.intersectionA(tx, ty)) return false;
    if (Monde.glyphe(tx, ty) !== 'g' && !Monde.estTrottoir(tx, ty)) return false;
    const x = tx * TT + 8, y = ty * TT + 8;
    for (const d of Entites.decorAutour(x, y, 20)) {
      if (!d.brise && Math.hypot(d.x - x, d.y - y) < 8 + (d.r || 4)) return false;
    }
    return true;
  }

  /** Un parc de l'autre cote du trottoir : la pelouse ou l'allee, une ou deux tuiles derriere. */
  function parcDerriere(rx, ry, d) {
    for (let k = 1; k <= 2; k++) {
      const g = Monde.glyphe(rx + d[0] * k, ry + d[1] * k);
      if (g === ',' || g === 'g') return true;
    }
    return false;
  }

  /** Un bout de trottoir : tout droit le long de la voie, de `trottoir_tuiles[0]`
      a ce qu'il y a (au plus `trottoir_tuiles[1]`), et on redescend UNE tuile plus
      loin, dans la meme voie. ⚠️ On s'arrete avant le coin : la traverse est de
      la route, et un velo qui descend sur un passage pieton descend dans les
      jambes de ceux qui traversent. */
  function boutDeTrottoir(v, tx, ty, p) {
    const f = trafic().velo, d = droiteDe(p);
    const chemin = [];
    for (let k = 1; k <= f.trottoir_tuiles[1]; k++) {
      const sx = tx + d[0] + p[0] * k, sy = ty + d[1] + p[1] * k;
      if (!roulableHorsRue(sx, sy) || !Monde.estTrottoir(sx, sy)) break;
      if (Monde.fleche(tx + p[0] * k, ty + p[1] * k) !== v.sens) break;
      if (Monde.fleche(tx + p[0] * (k + 1), ty + p[1] * (k + 1)) !== v.sens) break;
      chemin.push(centre(sx, sy));
    }
    const min = f.trottoir_tuiles[0];
    if (chemin.length < min) return null;
    const n = min + Math.floor(empreinteVelo(v, tx * 3 + 1, ty * 5 + 2) * (chemin.length - min + 1));
    const bout = chemin.slice(0, n), dernier = bout[bout.length - 1];
    return { chemin: bout, retour: { tx: dernier.tx - d[0], ty: dernier.ty - d[1], sens: v.sens } };
  }

  /** Un segment roule-t-il tout du long sur des tuiles hors rue ? On echantillonne
      l'axe et ses deux bords (un velo fait huit pixels de large). */
  function segmentRoulable(a, b) {
    const n = Math.ceil(Math.hypot(b.x - a.x, b.y - a.y) / 4);
    const l = Math.hypot(b.x - a.x, b.y - a.y) || 1, nx = -(b.y - a.y) / l * 3, ny = (b.x - a.x) / l * 3;
    for (let i = 0; i <= n; i++) {
      const x = a.x + (b.x - a.x) * i / n, y = a.y + (b.y - a.y) * i / n;
      for (const s of [0, 1, -1]) {
        if (!roulableHorsRue(Math.floor((x + nx * s) / TT), Math.floor((y + ny * s) / TT))) return false;
      }
    }
    return true;
  }

  /** Le chemin, sans ses marches d'escalier : d'un point, on vise le plus loin
      qu'on voit en ligne droite. Sur des rails, un chemin de tuile en tuile fait
      zigzaguer le velo en travers de la place du parc. */
  function lisser(chemin) {
    const out = [];
    let i = 0;
    while (i < chemin.length - 1) {
      let j = chemin.length - 1;
      while (j > i + 1 && !segmentRoulable(chemin[i], chemin[j])) j--;
      out.push(chemin[j]);
      i = j;
    }
    return out;
  }

  /** La traversee d'un parc, depuis la tuile de trottoir `(rx, ry)` : par ses
      allees, jusqu'a un trottoir d'une AUTRE rue, et la voie ou redescendre.

      ⚠️ Un Dijkstra a seaux (les couts sont 2 et 3 : l'allee coute moins que le
      trottoir, donc on passe PAR le parc plutot qu'autour), plafonne. On garde
      les bouts qui ont vu au moins `parc_allees_min` tuiles d'allee, et parmi
      les plus longs dans le parc, on en prend un a l'empreinte.

      ⚠️ **ON REDESCEND A LA SORTIE DE L'ALLEE**, sur la premiere tuile de
      trottoir (`trottoir === 1`). La premiere version choisissait n'importe quel
      bout de trottoir apres le parc : le velo sortait, longeait le trottoir cinq
      tuiles a rebours, et repartait sur la chaussee dans l'autre sens. */
  function traverseeDuParc(v, rx, ry) {
    const f = trafic().velo, w = Monde.carte.w;
    const depart = ry * w + rx;
    const vu = new Map([[depart, { cout: 0, parent: -1, allees: 0, trottoir: 1 }]]);
    const seaux = [[depart]];
    let noeuds = 0;
    const bouts = [];
    for (let cout = 0; cout < seaux.length && noeuds < f.noeuds_max; cout++) {
      for (const cle of seaux[cout] || []) {
        const n = vu.get(cle);
        if (n.cout !== cout) continue;
        noeuds++;
        const tx = cle % w, ty = Math.floor(cle / w);
        // Un bout : du trottoir qui borde une voie dont c'est la DROITE, avec de quoi redescendre.
        if (n.allees >= f.parc_allees_min && n.trottoir === 1 && Monde.estTrottoir(tx, ty)) {
          for (const sens of ['>', '<', '^', 'v']) {
            const q = PAS_FLECHE[sens], d = droiteDe(q), lx = tx - d[0], ly = ty - d[1];
            if (Monde.fleche(lx, ly) === sens && Monde.fleche(lx + q[0], ly + q[1]) === sens) {
              bouts.push({ cle: cle, allees: n.allees, retour: { tx: lx, ty: ly, sens: sens } });
            }
          }
        }
        for (const q of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
          const nx = tx + q[0], ny = ty + q[1];
          if (!roulableHorsRue(nx, ny)) continue;
          const allee = Monde.glyphe(nx, ny) === 'g';
          const c2 = cout + (allee ? 2 : 3), k = ny * w + nx;
          const deja = vu.get(k);
          if (deja && deja.cout <= c2) continue;
          vu.set(k, { cout: c2, parent: cle, allees: n.allees + (allee ? 1 : 0), trottoir: allee ? 0 : n.trottoir + 1 });
          (seaux[c2] = seaux[c2] || []).push(k);
        }
      }
    }
    if (!bouts.length) return null;
    const mieux = bouts.reduce(function (m, b) { return Math.max(m, b.allees); }, 0);
    const retenus = bouts.filter(function (b) { return b.allees * 5 >= mieux * 4; });
    const b = retenus[Math.floor(empreinteVelo(v, rx, ry) * retenus.length)];
    const tuiles = [];
    for (let cle = b.cle; cle !== -1; cle = vu.get(cle).parent) tuiles.push(centre(cle % w, Math.floor(cle / w)));
    tuiles.reverse();
    return { chemin: lisser(tuiles), retour: b.retour };
  }

  /** Il quitte la chaussee : un chemin de points, et ou redescendre au bout. */
  function partirHorsRue(v, chemin, retour) {
    if (!chemin || !chemin.length) return null;
    v.horsRue = { chemin: chemin, i: 0, retour: retour, attente: 0 };
    v.deportT = 0; v.sortie = null; v.enBoite = null; v.intention = null;
    v.horsRues = (v.horsRues || 0) + 1;
    return cibleHorsRue(v);
  }

  /** Le point suivant du chemin, puis la descente dans la voie — quand elle est
      libre, ou quand il a assez attendu (sur des rails, le trafic ne se pousse
      pas : au pire il se frole). */
  function cibleHorsRue(v) {
    const h = v.horsRue, f = trafic().velo;
    if (h.i < h.chemin.length) return h.chemin[h.i++];
    const r = h.retour, p = PAS_FLECHE[r.sens];
    if (!voieLibre(v, r.tx, r.ty, p) && ++h.attente < f.attente_images) return { x: v.x, y: v.y };
    v.horsRue = null;
    v.horsRueFroid = B.t + f.repos_images;
    v.sens = r.sens;
    return aLaBordure(v, centre(r.tx + p[0], r.ty + p[1]));
  }

  /** Monter sur le trottoir, depuis la voie du bord : pour traverser le parc
      qu'on longe, pour un bout de trottoir, ou parce qu'un char arrete bouche la
      voie (`coince`). null s'il reste sur la chaussee. ⚠️ Jamais s'il va
      tourner a gauche : il est range de l'autre cote. */
  function monterSurLeTrottoir(v, tx, ty, p, coince) {
    const f = trafic().velo;
    if (v.mission || (v.horsRueFroid || 0) > B.t || coteDuVelo(v) < 0) return null;
    const d = droiteDe(p), rx = tx + d[0], ry = ty + d[1];
    if (!Monde.estTrottoir(rx, ry) || !roulableHorsRue(rx, ry)) return null;
    if (!coince && parcDerriere(rx, ry, d) && empreinteVelo(v, tx, ty) < f.parc_chance) {
      const t = traverseeDuParc(v, rx, ry);
      if (t) return partirHorsRue(v, t.chemin, t.retour);
    }
    if (coince ? empreinteVelo(v, 3, 7) >= f.coince_part : empreinteVelo(v, ty, tx) >= f.trottoir_chance) return null;
    const t = boutDeTrottoir(v, tx, ty, p);
    return t ? partirHorsRue(v, t.chemin, t.retour) : null;
  }

  function prochaineCible(v) {
    if (v.horsRue && estVeloDuTrafic(v)) { v.attendFeu = false; v.guetteLigne = false; return cibleHorsRue(v); }
    const c = cibleDeLaVoie(v);
    return estVeloDuTrafic(v) ? aLaBordure(v, c) : c;
  }

  function cibleDeLaVoie(v) {
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    const f = Monde.fleche(tx, ty);
    v.attendFeu = false;
    v.guetteLigne = false;
    if (PAS_FLECHE[f]) {
      v.sens = f; v.sortie = null;
      v.enBoite = null;                              // on rend le croisement
      const p = PAS_FLECHE[f];
      if (estVeloDuTrafic(v)) intentionDuVelo(v, tx, ty, p);
      if (v.conducteur === 'trafic' && Monde.barriereBloque(v, tx + p[0], ty + p[1])) {
        // ⚠️ **On SE DEPORTE avant de faire demi-tour.** Une voie fermee laisse
        // sa voisine ouverte : y faire demi-tour serait absurde, et toute la
        // rue rebrousserait chemin pour trois cones. C'est la voie d'a cote qui
        // tranche, pas le genre de la barriere — un pont barre n'en a pas.
        if (changerDeVoie(v)) return v.cible;
        return demiTour(v, tx, ty, p);
      }
      // ⚠️ **LA LIGNE SE GUETTE UNE TUILE EN AVANCE.** Un char de 48 px a deja
      // couvert la traverse quand son centre arrive sur la ligne : il doit
      // s'arreter AVANT d'y entrer. L'autobus de M9 le faisait deja pour lui
      // seul ; c'est la meme regle, pour tout le parc, et elle ne coute rien
      // aux courts (leur point d'arret tombe dans la tuile d'arret).
      const ligne = !v.poursuite && ligneDevant(v, tx, ty, p);
      if (ligne) {
        v.guetteLigne = true;                        // on relit le feu a chaque image
        if (attendreALaLigne(v, v.sens, ligne.inter)) {
          v.attendFeu = true;
          return pointDArret(v, ligne.tx, ligne.ty, p);
        }
      }
      if (estVeloDuTrafic(v)) {
        // ⚠️ Le trottoir d'abord : il ne se tasse pas dans la voie du milieu
        // pour remonter sur le trottoir a la tuile d'apres.
        const hors = !ligne && monterSurLeTrottoir(v, tx, ty, p, false);
        if (hors) return hors;
        const q = voieDuVelo(v, tx, ty, p);
        if (q) return centre(tx + q[0] + p[0], ty + q[1] + p[1]);
      }
      return centre(tx + p[0], ty + p[1]);
    }
    if (f === 'S') {
      const sens = Monde.sensArret(tx, ty) || v.sens;
      v.sens = sens;
      const p = PAS_FLECHE[sens];
      if (v.conducteur === 'trafic' && Monde.barriereBloque(v, tx + p[0], ty + p[1])) {
        // ⚠️ **On SE DEPORTE avant de faire demi-tour.** Une voie fermee laisse
        // sa voisine ouverte : y faire demi-tour serait absurde, et toute la
        // rue rebrousserait chemin pour trois cones. C'est la voie d'a cote qui
        // tranche, pas le genre de la barriere — un pont barre n'en a pas.
        if (changerDeVoie(v)) return v.cible;
        return demiTour(v, tx, ty, p);
      }
      const inter = Monde.intersectionA(tx + p[0], ty + p[1]);
      if (v.poursuite) {                             // sirene : feux, stops et boite, on brule tout
        v.attenteBoite = 0; v.stopT = undefined; v.enBoite = inter || null;
        return centre(tx + p[0], ty + p[1]);
      }
      if (attendreALaLigne(v, sens, inter)) { v.attendFeu = true; return pointDArret(v, tx, ty, p); }
      v.attenteBoite = 0;
      v.stopT = undefined;
      v.enBoite = inter || null;                     // on prend le croisement
      if (inter) noterLaBoite(v, inter);
      return centre(tx + p[0], ty + p[1]);
    }
    if (f === '+') {
      if (!v.sens) v.sens = FLECHE_DE[Math.round(Math.cos(v.angle)) + ',' + Math.round(Math.sin(v.angle))] || '>';
      const droit = v.sens;
      const p = PAS_FLECHE[droit];
      const droite = FLECHE_DE[(-p[1]) + ',' + p[0]], gauche = FLECHE_DE[p[1] + ',' + (-p[0])];
      const vers = { droit: droit, droite: droite, gauche: gauche };
      // Au premier '+', on decide ou l'on va : tout droit, a droite, a gauche —
      // et on le garde EN SENS ABSOLUS pour toute la boite.
      // ⚠️ Une preference relative (« a gauche ») relue a chaque tuile par
      // rapport au cap du moment fait tourner a gauche, puis a gauche du
      // nouveau cap, puis encore : le char faisait le tour de la boite sans
      // fin. Martin l'a vu, et le juge des boites en trouvait 1858 cas.
      // ⚠️ Le cycliste sait deja ou il va : il l'a lu avant la ligne, et c'est
      // pour ca qu'il s'est range a gauche (`intentionDuVelo`).
      const intention = estVeloDuTrafic(v) && v.intention && v.intention.inter === Monde.intersectionA(tx, ty) ? v.intention : null;
      if (intention) intention.dedans = true;
      if (!v.sortie) {
        let ordre;
        if (intention) {
          ordre = intention.ordre.slice();
        } else if (v.poursuite && B.joueur) {
          // En poursuite : la sortie qui rapproche le plus du joueur, d'abord.
          // En fuite (le fuyard de M2) : celle qui en eloigne le plus.
          const j = B.joueur, signe = v.fuite ? -1 : 1;
          ordre = ['droit', 'droite', 'gauche'].sort(function (a, b) {
            const qa = PAS_FLECHE[vers[a]], qb = PAS_FLECHE[vers[b]];
            return signe * (dist2((tx + qa[0] * 4) * TT, (ty + qa[1] * 4) * TT, j.x, j.y) - dist2((tx + qb[0] * 4) * TT, (ty + qb[1] * 4) * TT, j.x, j.y));
          });
        } else {
          // ⚠️ LES HEURES DE POINTE ONT UNE DIRECTION. Le rythme dit COMBIEN de
          // chars roulent, jamais OU ils vont. Le matin on converge vers le
          // coeur, le soir on s'en disperse — en PONDERANT la sortie, jamais en
          // touchant au champ de direction, qui est fixe et juge.
          //
          // ⚠️ `penchant` est la PART des chars qui suivent le mouvement : le
          // reste tire au sort comme toujours. Sans ce partage, toute la ville
          // roule dans le meme sens et ce n'est plus une heure de pointe, c'est
          // une evacuation.
          const penchant = pointeDuMoment();
          if (penchant && B.rng() < Math.abs(penchant)) {
            const c = Monde.coeurDeLaVille(), signe = penchant > 0 ? 1 : -1;
            ordre = ['droit', 'droite', 'gauche'].sort(function (a, b) {
              const qa = PAS_FLECHE[vers[a]], qb = PAS_FLECHE[vers[b]];
              return signe * (dist2((tx + qa[0] * 6) * TT, (ty + qa[1] * 6) * TT, c.x, c.y)
                            - dist2((tx + qb[0] * 6) * TT, (ty + qb[1] * 6) * TT, c.x, c.y));
            });
          } else {
            // ⚠️ « Tout droit, SINON A GAUCHE » : au pied d'un T, ou tout droit
            // n'existe pas, c'est le repli qui decide. Il a toujours ete la
            // gauche (le char traversait la boite et prenait ce qu'il trouvait
            // au fond) ; `sortieDevant` le rend explicite sans rien changer au
            // partage des T.
            const tirage = B.rng();
            ordre = tirage < 0.55 ? ['droit', 'gauche', 'droite'] : tirage < 0.78 ? ['droite', 'droit', 'gauche'] : ['gauche', 'droit', 'droite'];
          }
        }
        v.sortie = ordre.map(function (choix) { return vers[choix]; });
      }
      // 1. La sortie voulue, si elle part d'ici. Sinon on traverse la boite
      //    tout droit jusqu'a la voie d'ou elle part : un virage a droite se
      //    prend a l'entree de la boite, un virage a gauche au fond.
      // ⚠️ **LA SORTIE VOULUE EST CELLE QUE LA BOITE A** (21 sept. 2026, retour
      // de Martin au coin en L des Quais). Le tirage ne sait rien de la boite :
      // dans un coin en L, un char qui descendait du nord en voulant « tout
      // droit » traversait jusqu'a la rangee du bord de l'eau, n'y trouvait pas
      // de sortie, et zigzaguait — ouest, nord, ouest. 24 entrees de boite sur
      // 2 238, toutes dans les onze coins en L. On prend donc la premiere de la
      // liste qui part d'ici ou de plus loin tout droit.
      const voulu = v.sortie.find(function (sens) { return sortieDevant(tx, ty, droit, sens, v); }) || v.sortie[0];
      if (peutSortir(tx, ty, voulu, v)) {
        const q = PAS_FLECHE[voulu];
        v.sens = voulu;
        return centre(tx + q[0], ty + q[1]);
      }
      if (Monde.fleche(tx + p[0], ty + p[1]) === '+') return centre(tx + p[0], ty + p[1]);
      // 2. Au fond de la boite sans la sortie voulue : les autres, dans l'ordre.
      for (const sens of v.sortie.slice(1)) {
        if (peutSortir(tx, ty, sens, v)) {
          const q = PAS_FLECHE[sens];
          v.sens = sens;
          return centre(tx + q[0], ty + q[1]);
        }
      }
      // 3. N'importe quelle sortie d'ici fera (a droite, a gauche du cap).
      for (const sens of [droite, gauche]) {
        if (peutSortir(tx, ty, sens, v)) {
          const q = PAS_FLECHE[sens];
          v.sens = sens; v.sortie = null;
          return centre(tx + q[0], ty + q[1]);
        }
      }
      // 4. Aucune sortie depuis cette rangee : on se decale DANS la boite
      //    (vers la droite d'abord) jusqu'a en trouver une. ⚠️ Jamais « la
      //    voie la plus proche » ici : elle ramenait dans la boite.
      for (const sens of [droite, gauche]) {
        const q = PAS_FLECHE[sens];
        if (Monde.fleche(tx + q[0], ty + q[1]) === '+') { v.sens = sens; return centre(tx + q[0], ty + q[1]); }
      }
      // 5. Boite d'une tuile sans issue : demi-tour sur place.
      const arriere = FLECHE_DE[(-p[0]) + ',' + (-p[1])];
      v.sens = arriere; v.sortie = null;
      return centre(tx - p[0], ty - p[1]);
    }
    // Hors route : on cherche la voie la plus proche.
    return voieLaPlusProche(v, tx, ty);
  }

  /** La voie la plus proche qui MENE QUELQUE PART : sa fleche continue sur
      une voie (pas dans une boite), elle ne pointe pas vers nous, et une voie
      dans notre rangee ou notre colonne passe avant une voie en diagonale. */
  function voieLaPlusProche(v, tx, ty) {
    let meilleur = null, coutMin = Infinity, sens = null;
    for (let dy = -3; dy <= 3; dy++) {
      for (let dx = -3; dx <= 3; dx++) {
        const g = Monde.fleche(tx + dx, ty + dy);
        if (!PAS_FLECHE[g]) continue;
        const q = PAS_FLECHE[g];
        if (tx + dx + q[0] === tx && ty + dy + q[1] === ty) continue;           // elle pointe vers nous
        if (!PAS_FLECHE[Monde.fleche(tx + dx + q[0], ty + dy + q[1])]) continue;   // elle ne continue pas
        const cout = dx * dx + dy * dy + (dx !== 0 && dy !== 0 ? 6 : 0);
        if (cout < coutMin) { coutMin = cout; meilleur = centre(tx + dx, ty + dy); sens = g; }
      }
    }
    if (meilleur) v.sens = sens;
    return meilleur;
  }

  /** Personne dans le croisement (a part nous) ? Un char qui s'y est engage
      le RESERVE (`enBoite`) jusqu'a ce qu'il en ressorte : le suivant ne se
      contente pas de regarder la boite, il attend que la place soit rendue. */
  function croisementLibre(inter, v) {
    const cx = (inter.x + inter.l / 2) * TT, cy = (inter.y + inter.h / 2) * TT;
    const rayon = Math.max(inter.l, inter.h) * TT / 2 + 2 * TT + 12;      // la boite ET ses passages
    const approche = rayon + APPROCHE_TRAM_TUILES * TT;
    for (const e of Entites.autour(cx, cy, approche, function (q) { return q.type === 'vehicule' && q !== v && q.etat !== 'epave'; })) {
      if (e.enBoite === inter) return false;
      // ⚠️ LE TRAFIC CEDE AU TRAMWAY (M12) : on ne s'engage pas dans une boite vers
      // laquelle roule une rame. Elle a ses rails, elle ne se range pas.
      if (e.rails && !v.rails && !(e.arretT > 0)) {
        const dx = cx - e.x, dy = cy - e.y;
        if (dx * Math.cos(e.angle) + dy * Math.sin(e.angle) > -TT && dx * dx + dy * dy < approche * approche) return false;
        continue;
      }
      // ⚠️ Un autobus de ligne attend a la ligne d'arret comme le trafic : il n'est
      // pas « un char stationne dans la boite », sinon tout le carrefour l'attend.
      if (e.conducteur !== 'trafic' && e.conducteur !== 'ligne' && dist2(e.x, e.y, cx, cy) < rayon * rayon) return false;   // le joueur, un char stationne
    }
    return true;
  }

  //: Jusqu'a combien de tuiles d'une boite une rame qui arrive la reserve.
  const APPROCHE_TRAM_TUILES = 4;

  // --- Le deport : se tasser dans la voie d'a cote -----------------------------------
  //
  // Une rue a deux voies (un boulevard : `RUES_V`/`RUES_H` a 8) a DEUX tuiles
  // cote a cote portant la meme fleche. Un char coince derriere un pieton
  // arrete au milieu de la chaussee, une epave ou le char du joueur n'a alors
  // aucune raison d'attendre : il se deporte, comme dans la vraie rue. Sur une
  // rue a deux voies (largeur 6), il n'y a pas de voisine dans notre sens, et
  // tout ce code se tait.

  /** La voie d'a cote est-elle degagee ? On regarde un couloir qui va de DEUX
      tuiles derriere a `depassement_tuiles` devant : un char qui arrive vite
      par derriere dans cette voie compte autant qu'un char arrete dedans. Les
      echantillons se chevauchent (un par tuile, rayon 13 px), le couloir est
      donc continu : le centre d'un char ne peut pas s'y glisser entre deux. */
  function voieLibre(v, tx, ty, p) {
    const avant = trafic().depassement_tuiles;
    for (let k = -2; k <= avant; k++) {
      const x = (tx + p[0] * k) * TT + 8, y = (ty + p[1] * k) * TT + 8;
      const gene = Entites.autour(x, y, TT * 0.8, function (e) {
        return e !== v && (e.type === 'vehicule'
          || ((e.type === 'pieton' || e.type === 'joueur') && e.vivant && !e.dansVehicule));
      });
      if (gene.length) return false;
    }
    return true;
  }

  /** Le pas lateral vers une voie parallele libre — a GAUCHE d'abord (on
      depasse par la gauche), a droite sinon. null s'il n'y en a pas.

      ⚠️ On exige que la voisine ET la tuile suivante portent notre fleche :
      c'est ce qui interdit de se deporter juste avant une ligne d'arret ou
      dans une boite de croisement, ou le deport couperait la trajectoire de
      quelqu'un qui a la priorite. */
  function voieDeDepassement(v, tx, ty) {
    const p = PAS_FLECHE[v.sens];
    if (!p) return null;
    for (const q of [[p[1], -p[0]], [-p[1], p[0]]]) {
      if (Monde.fleche(tx + q[0], ty + q[1]) !== v.sens) continue;
      if (Monde.fleche(tx + q[0] + p[0], ty + q[1] + p[1]) !== v.sens) continue;
      // ⚠️ Une voie BARREE n'est pas une voie ou se deporter : sans ca, un char
      // quitte le chantier pour entrer dans le chantier d'a cote.
      if (Monde.barriereBloque(v, tx + q[0], ty + q[1])) continue;
      if (Monde.barriereBloque(v, tx + q[0] + p[0], ty + q[1] + p[1])) continue;
      if (!voieLibre(v, tx + q[0], ty + q[1], p)) continue;
      return q;
    }
    return null;
  }

  /** Viser la voie d'a cote, une tuile plus loin : les rails font le reste —
      le char y glisse en diagonale et, arrive au centre, `prochaineCible`
      relit la fleche sous lui et continue tout droit dans sa nouvelle voie. */
  function changerDeVoie(v) {
    if (v.deportT > 0) return true;                      // deja en train de se tasser
    if (v.deportFroid > 0) return false;                 // on vient de le faire : pas de zigzag
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    if (Monde.fleche(tx, ty) !== v.sens) return false;   // en boite ou a l'arret : pas ici
    const q = voieDeDepassement(v, tx, ty);
    if (!q) return false;
    const p = PAS_FLECHE[v.sens];
    v.cible = centre(tx + q[0] + p[0], ty + q[1] + p[1]);
    v.deportT = trafic().depassement_images;
    v.deports = (v.deports || 0) + 1;
    return true;
  }

  /** Quelque chose devant ? Rend la distance, ou Infinity. */
  function obstacleDevant(v) {
    const t = trafic();
    const portee = t.regard_tuiles * TT;
    const cx = Math.cos(v.angle), cy = Math.sin(v.angle);
    const ax = v.x + cx * (v.def.longueur / 2 + portee / 2), ay = v.y + cy * (v.def.longueur / 2 + portee / 2);
    let dMin = Infinity;
    // ⚠️ UNE RAME NE S'ARRETE PAS POUR TOI (M12) : ni pour le joueur, ni pour son char.
    const toi = v.rails && B.joueur, tonChar = toi && B.joueur.dansVehicule;
    for (const e of Entites.autour(ax, ay, portee / 2 + 16, function (q) {
      if (toi && (q === toi || q === tonChar)) return false;
      // ⚠️ LA CHARRUE POUSSE LES CHARS MAL GARES (M12) : un char sans conducteur n'est
      // pas un obstacle pour elle, c'est de la neige de plus.
      if (v.charrue && q.type === 'vehicule' && !q.conducteur) return false;
      return q !== v && ((q.type === 'vehicule') || ((q.type === 'pieton' || q.type === 'joueur') && q.vivant && !q.dansVehicule));
    })) {
      const dx = e.x - v.x, dy = e.y - v.y;
      const devant = dx * cx + dy * cy;                 // projection sur l'axe
      const cote = Math.abs(-dx * cy + dy * cx);         // ecart lateral
      // ⚠️ La tolerance laterale doit rester SOUS l'ecart entre deux voies
      // (16 px) : avec +2 px de marge, le char d'en face, sur la voie d'a
      // cote, comptait comme un obstacle — et tout le monde s'arretait nez a
      // nez. C'etait l'embouteillage de Martin.
      if (devant < v.def.longueur / 2 - 4 || cote > v.def.largeur / 2 + (e.r || 5) * 0.8) continue;
      if (e.type === 'vehicule' && Math.abs(e.vitesse) > 0.3) {
        const face = Math.cos(e.angle) * cx + Math.sin(e.angle) * cy;
        if (face < -0.5 && cote > 6) continue;         // il vient en face, dans sa voie : rien a craindre
      }
      if (devant < dMin) dMin = devant - v.def.longueur / 2;
    }
    // ⚠️ Et le SIGNALEUR d'un chantier, quand sa palette dit ARRÊT : le même
    // freinage que pour un piéton planté sur la voie, à la distance où il est.
    // (Infinity la plupart du temps : aucun chantier ne le fait parler.)
    return Math.min(dMin, Chantiers.signalDevant(v));
  }

  /** Le chien de garde du trafic : dix secondes sans bouger, sans feu rouge
      devant, c'est un char coince — quelle qu'en soit la cause. On le recale
      au centre de la voie la plus proche dans son sens, cap redressé,
      croisement rendu. Martin en a vu trois de travers dans une boîte ;
      plutôt que courir après chaque cause, on garantit la sortie. */
  /** Une attente LEGITIME : un vrai feu rouge, un stop qui s'egrene, ou une
      boite qu'un autre char n'a pas encore rendue.

      ⚠️ Elle est BORNEE, sinon elle serait une excuse a tout : un feu rouge
      dure au plus 480 images, l'attente de boite au plus `patience x 2`. Un
      char pris pour de vrai n'est jamais dans un de ces trois cas bien
      longtemps — et on ne compte pas contre lui le temps ou il a raison
      d'attendre. (C'est ce qui mordait a tort : 480 images de feu rouge PUIS
      110 d'attente de boite faisaient 600, et le chien sautait sur un char
      parfaitement sage.) */
  function attenteLegitime(v) {
    if (!v.attendFeu) return false;
    if (v.stopT !== undefined && v.stopT > 0) return true;
    if (v.attenteBoite > 0) return v.attenteBoite < trafic().patience_images * 2;
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    const p = PAS_FLECHE[v.sens] || [0, 0];
    // ⚠️ **A UNE TUILE OU A DEUX.** Depuis que le nez s'arrete a la ligne, un
    // long char attend sur la tuile d'AVANT la ligne d'arret : le croisement
    // est alors deux tuiles plus loin. Cherche a une seule, cette fonction
    // rendait faux, l'attente au feu rouge cessait d'etre legitime, et le chien
    // de garde teleportait un autobus parfaitement poli.
    for (let k = 1; k <= 2; k++) {
      const inter = Monde.intersectionA(tx + p[0] * k, ty + p[1] * k);
      if (inter) return !Monde.feuVert(inter, v.sens);
    }
    return false;
  }

  function debloquer(v) {
    const immobile = Math.abs(v.vx) + Math.abs(v.vy) < 0.05 && !attenteLegitime(v);
    v.immobileT = immobile ? (v.immobileT || 0) + 1 : 0;
    // ⚠️ « Sur place » : il bouge, mais n'avance pas (un va-et-vient entre
    // deux cibles). Il n'est jamais immobile, le compteur ci-dessus ne le
    // voit pas ; la capture de Martin, elle, le montrait bien. On compare a
    // l'endroit ou il etait il y a dix secondes. Seul un vrai feu rouge excuse.
    // ⚠️ Et il excuse TOUTE la fenetre, pas seulement l'image ou l'on compare :
    // un taxi reste 600 images au feu derriere une moto qui attend la boite, il
    // repart, et la comparaison tombait juste apres — « dix secondes au meme
    // endroit », et on le teleportait au milieu de la voie. Une attente legitime
    // remet donc l'ancrage a zero (graine 5 de `test_trace_js`, 16 sept. 2026).
    if (attenteLegitime(v)) v.ancrage = null;
    if (!v.ancrage || B.t - v.ancrage.t >= 600) {
      if (v.ancrage && !attenteLegitime(v) && dist2(v.x, v.y, v.ancrage.x, v.ancrage.y) < 24 * 24) v.surPlace = (v.surPlace || 0) + 1;
      else v.surPlace = 0;
      v.ancrage = { x: v.x, y: v.y, t: B.t };
    }
    if (v.immobileT < 600 && !v.surPlace) return false;
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    v.etatBloque = etatCourt(v);                   // ce qu'il attendait, avant qu'on efface tout
    const voie = voieLaPlusProche(v, tx, ty);
    v.cible = null; v.sortie = null; v.enBoite = null; v.stopT = undefined; v.attenteBoite = 0; v.attendFeu = false;
    v.patience = 0; v.force = 90; v.immobileT = 0; v.surPlace = 0; v.ancrage = null; v.debloques = (v.debloques || 0) + 1;
    if (voie) {
      // ⚠️ Recale sur la chaussee, le velo a fini son tour de trottoir. Sans voie
      // a portee (au milieu du parc), il le garde : son chemin l'y ramene.
      v.horsRue = null; v.intention = null;
      v.x = voie.x; v.y = voie.y;
      const q = PAS_FLECHE[v.sens] || [1, 0];
      v.angle = Math.atan2(q[1], q[0]);
    }
    return true;
  }

  function majConducteur(v) {
    // ⚠️ **LE TRAFIC NE NAVIGUE PAS.** Il roule sur des rails et ne lit aucune
    // tuile (`maj` : `v.x += v.vx`) — c'est ce qui l'empeche de couper les
    // coins, et c'est aussi ce qui laisse passer une coque : `tuileInterdite`,
    // la seule regle qui tient une chaloupe sur l'eau, n'est jamais consultee
    // sur des rails. Une coque confiee au trafic montait sur la voie la plus
    // proche (`voieLaPlusProche`, trois tuiles) et roulait dans la ville. Le
    // voleur de char ne lui en confie plus (`Entites.majVolDeChar`) ; ceci est
    // pour le prochain qui le ferait : elle reste la ou elle est, sans personne.
    if (v.def.eau) { v.conducteur = null; v.etat = 'stationne'; v.vitesse = 0; v.vx = 0; v.vy = 0; return; }
    const t = trafic();
    if (debloquer(v)) return;
    if (v.deportT > 0 && --v.deportT === 0) v.deportFroid = t.depassement_images;
    if (v.deportFroid > 0) v.deportFroid--;
    // L'escorte (Ti-Guy, M4) : elle te suit, et t'attend quand elle t'a rejoint.
    if (v.escorte && B.joueur && dist2(v.x, v.y, B.joueur.x, B.joueur.y) < 70 * 70) { rouler(v, 0); return; }
    if (!v.cible || (v.attendFeu && !v.cible.tx)) v.cible = prochaineCible(v);
    if (!v.cible) { majPhysique(v, { gaz: 0, frein: 1, direction: 0 }); return; }
    // On attend (feu rouge, stop), ou la ligne est en vue : on redemande chaque
    // image, et on glisse jusqu'a elle — le nez dessus, pas un pixel de plus loin.
    // ⚠️ **LA LIGNE EN VUE SE RELIT A CHAQUE IMAGE**, et pas seulement au centre
    // de chaque tuile. Entre deux lectures il se passe une tuile entiere : la
    // boite se fermait dans cet intervalle, le char etait deja engage quand il
    // l'apprenait, et il s'arretait ou il etait — quatre pixels de traverse pour
    // une remorqueuse, mesures. Un conducteur regarde le feu, il ne le consulte
    // pas tous les seize pixels.
    if (v.attendFeu || v.guetteLigne) {
      v.cible = prochaineCible(v);
      if (v.attendFeu) { rouler(v, approcheDeLaLigne(v)); return; }
      if (!v.cible) return;
    }
    const dx = v.cible.x - v.x, dy = v.cible.y - v.y;
    if (dx * dx + dy * dy < 36) {
      // Arrive : si c'etait la voie d'a cote, le deport est fini et on s'interdit
      // le suivant un moment — sinon un char zigzague entre deux voies.
      if (v.deportT > 0) { v.deportT = 0; v.deportFroid = t.depassement_images; }
      v.cible = prochaineCible(v);
      if (!v.cible) return;
      // ⚠️ L'IMAGE OU L'ON VOIT LE ROUGE COMPTE. Elle tombait dans la conduite
      // ordinaire et le char avancait encore d'un pas plein — assez pour poser
      // le nez dans la traverse qu'on vient de decider de ne pas mordre.
      if (v.attendFeu) { rouler(v, approcheDeLaLigne(v)); return; }
    }
    const voulu = angleVers(v.x, v.y, v.cible.x, v.cible.y);
    const ecart = ecartAngle(v.angle, voulu);
    let vitesseVoulue = v.def.vitesse_max * (v.poursuite ? 0.85 : t.vitesse_ville) * Neige.vitesseTrafic();   // sirene : bien plus vite
    // ⚠️ On ralentit AVANT le coin, pas dedans : a 2,2 px/image le rayon de
    // braquage fait 3,6 tuiles, et un coin de rue en demande 1,5 — le char
    // ratait son virage et finissait sur le trottoir d'en face.
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    const ici = Monde.fleche(tx, ty);
    const p = PAS_FLECHE[v.sens] || [0, 0];
    const devant = Monde.fleche(tx + p[0] * 2, ty + p[1] * 2);
    if (ici === '+' || ici === 'S' || devant === '+' || devant === 'S') vitesseVoulue = Math.min(vitesseVoulue, v.poursuite ? 1.5 : 1.1);
    if (Math.abs(ecart) > 0.5) vitesseVoulue = Math.min(vitesseVoulue, 0.8);
    // ⚠️ Hors de la rue, un velo va AU PAS : sous la vitesse qui renverse, et
    // assez lent pour s'arreter derriere un passant (`trottoir_vitesse`).
    const velo = estVeloDuTrafic(v) ? t.velo : null;
    if (velo && v.horsRue) vitesseVoulue = Math.min(vitesseVoulue, velo.trottoir_vitesse);
    const obstacle = obstacleDevant(v);
    const proche = obstacle < t.distance_securite_px;
    // Et il SONNE a celui qu'il a devant — un coup, pas une rafale.
    if (velo && v.horsRue && obstacle < t.distance_securite_px * 2 && (v.sonnetteT || 0) <= B.t) {
      v.klaxonT = 30; v.sonnetteT = B.t + velo.sonnette_images;
    }
    // ⚠️ On decide de se tasser DE LOIN (deux fois la distance de securite),
    // pas au dernier moment : a une tuile du pieton, le deport serait un coup
    // de volant a 45 degres. De loin, la diagonale se voit venir.
    const deport = obstacle < t.distance_securite_px * 2 && changerDeVoie(v);
    if (proche && !deport) {
      vitesseVoulue = 0;
      v.patience++;
      // ⚠️ COINCE DERRIERE UN CHAR ARRETE, un cycliste sur deux monte sur le
      // trottoir et le longe (`coince_part`, a l'empreinte) ; l'autre attend.
      if (velo && !v.horsRue && v.patience === velo.coince_images) {
        const p = PAS_FLECHE[v.sens];
        const hors = p && Monde.fleche(tx, ty) === v.sens && monterSurLeTrottoir(v, tx, ty, p, true);
        if (hors) { v.cible = hors; v.patience = 0; }
      }
      if (v.patience > t.patience_images) { v.force = 90; v.patience = 0; v.klaxonT = 30; }
    } else {
      if (obstacle < t.distance_securite_px * 2) vitesseVoulue *= 0.5;
      // ⚠️ Tant qu'on longe l'obstacle, on reste SOUS la vitesse qui renverse :
      // on contourne un pieton plante sur la chaussee, on ne le fauche pas.
      if (deport && proche) vitesseVoulue = Math.min(vitesseVoulue, physique().renverse_vitesse_min * 0.9);
      v.patience = 0;
    }
    if (v.force > 0) { v.force--; vitesseVoulue = Math.max(vitesseVoulue, v.def.vitesse_max * 0.25); }
    void ecart;
    rouler(v, vitesseVoulue);
  }

  /** Le trafic est SUR DES RAILS : il avance vers le centre de sa tuile cible,
      accelere et freine comme un char, mais ne connait pas le braquage.

      ⚠️ C'est ce qui l'empeche de couper les coins. Avec la physique du
      joueur, un char a 1,1 px/image a un rayon de braquage d'une tuile et
      demie : il ratait un virage sur deux et finissait sur le trottoir d'en
      face. Ici il tourne AU centre de la tuile, comme un tramway. */
  function rouler(v, vitesseVoulue) {
    const d = v.def;
    if (v.vitesse < vitesseVoulue) v.vitesse = Math.min(vitesseVoulue, v.vitesse + d.acceleration * 1.5);
    else v.vitesse = Math.max(vitesseVoulue, v.vitesse - d.frein * 1.5);
    if (!v.cible) { v.vx = 0; v.vy = 0; return; }
    const dx = v.cible.x - v.x, dy = v.cible.y - v.y;
    const dist = Math.hypot(dx, dy);
    if (dist < 0.01 || v.vitesse <= 0) { v.vx = 0; v.vy = 0; return; }
    const pas = Math.min(dist, v.vitesse);
    v.vx = dx / dist * pas; v.vy = dy / dist * pas;
    // Le cap suit la route, en douceur : on VOIT le char tourner.
    const voulu = Math.atan2(dy, dx);
    v.angle += ecartAngle(v.angle, voulu) * 0.3;
  }

  // --- Le joueur au volant ----------------------------------------------------------

  function commandesJoueur(v) {
    const axe = Entree.axe;
    const clavierHaut = Entree.bas('haut'), clavierBas = Entree.bas('bas');
    let gaz = clavierHaut ? 1 : 0, frein = clavierBas ? 1 : 0;
    if (axe.source !== 'clavier') { if (axe.y < -0.2) gaz = Math.max(gaz, -axe.y); if (axe.y > 0.2) frein = Math.max(frein, axe.y); }
    gaz = Math.max(gaz, Entree.gaz); frein = Math.max(frein, Entree.frein);
    const direction = axe.source === 'clavier' ? (Entree.bas('droite') ? 1 : 0) - (Entree.bas('gauche') ? 1 : 0) : borner(axe.x * 1.3, -1, 1);
    // L'option ne vaut que pour le joueur : la police et le trafic gardent l'auto.
    return { gaz: gaz, frein: frein, direction: direction, freinMain: Entree.bas('esquive'),
             reculCommeEnAvant: !!B.options.reculCommeEnAvant };
  }

  //: Les mains hors du volant : le char de l'atelier ne bouge pas (`Missions.majGarage`).
  const POINT_MORT = { gaz: 0, frein: 0, direction: 0, freinMain: false };

  function majJoueur(j) {
    const v = j.dansVehicule;
    if (v.etat === 'epave') { descendre(j, true); return; }
    // ⚠️ SOUS LE RIDEAU, ON NE CONDUIT PAS : il descend, le pistolet siffle, il remonte.
    // Tant que dure l'atelier, le char est a l'arret et le volant ne repond pas.
    if (v.atelier) { v.vitesse = 0; v.vx = 0; v.vy = 0; }
    majPhysique(v, v.atelier ? POINT_MORT : commandesJoueur(v));
    if (Entree.neuf('attaque')) {
      // ⚠️ Un char a sirene n'a pas de klaxon sous le pouce : il a sa sirene.
      // Le boulot, lui, se prend au meme bouton — dans une ambulance, on
      // repond a l'appel et on part la sirene allumee, d'un seul geste.
      //
      // ⚠️ MAIS SEULEMENT QUAND ON L'ALLUME (retour de Martin). Le geste
      // inverse veut dire « j'ai fini », pas « donne-m'en un autre » : eteindre
      // sa sirene en sortant de l'hopital rappelait aussitot une ambulance,
      // et on repartait sans l'avoir demande.
      const allume = v.def.sirene && !v.sirene;
      if (v.def.sirene) { v.sirene = !v.sirene; Son.SFX.touche(); } else v.klaxonT = 30;
      // ⚠️ Sur la remorqueuse, le meme bouton accroche et decroche : le boulot
      // de remorquage EST le crochet, il n'y a pas deux gestes a apprendre.
      if (v.def.crochet) basculerCrochet(v);
      if ((!v.def.sirene || allume) && typeof Missions !== 'undefined' && Missions.boulot) Missions.boulot.klaxon(v);
    }
    if (Entree.neuf('action') && !B.cinema && !v.atelier) descendre(j, false);   // (pendant un dialogue, ACTION passe la replique)
    if (Entree.neuf('arme')) {
      const station = Son.Radio.suivante();
      const def = station ? Son.Radio.station(station) : null;
      Hud.message(def ? 'RADIO : ' + def.nom.toUpperCase() : 'RADIO ÉTEINTE');
    }
    // Le moteur monte dans les tours.
    if (v.def.classe !== 'velo') Son.reglerBoucle(boucleDeMoteur(v), 0.35 + Math.abs(v.vitesse) / v.def.vitesse_max * 0.5, 0.7 + Math.abs(v.vitesse) / v.def.vitesse_max * 0.9);
  }

  // --- Boucle -------------------------------------------------------------------------

  //: A quelle distance on entend encore une sirene. Au-dela, elle se tait —
  //: sinon la moindre poursuite a l'autre bout du district hurle dans le
  //: casque, et une sirene qu'on entend toujours ne veut plus rien dire.
  const SIRENE_PORTEE_PX = 460;
  //: Une ambulance sur trois qui naît dans le trafic est EN COURSE. Les deux
  //: autres rentrent au garage : une ville ou toutes les ambulances hurlent
  //: n'est pas une ville, c'est une alarme.
  const AMBULANCE_EN_COURSE = 1 / 3;

  /** La boucle qui va avec ce char. ⚠️ DEUX sirenes, pas une : celle de la
      police monte et descend sans s'arreter, celle d'une ambulance fait deux
      notes, plus haut et plus lent. Les confondre, c'est ne pas savoir qui
      arrive derriere soi — et c'est toute la difference entre se ranger et
      se sauver. */
  function boucleDeSirene(v) { return v.def.police ? 'sirene' : 'sirene_ambulance'; }

  //: Ce que le melangeur a demande a `Son`, par boucle : 0 = eteinte.
  const sirenes = { sirene: 0, sirene_ambulance: 0 };

  /** Les sirenes : une boucle par sorte, au volume du char le plus proche qui
      la fait hurler.

      ⚠️ Avant, il n'y en avait qu'une, allumee a volume fixe des qu'une
      auto-patrouille chassait, et **jamais** pour une ambulance — dont la
      fiche declare pourtant `sirene: true` depuis M9. Au volant, on n'en avait
      aucune : on conduisait une ambulance en silence. */
  function majSirenes() {
    const j = B.joueur;
    const voulu = { sirene: 0, sirene_ambulance: 0 };
    if (j && !B.interieur) {
      for (const v of B.entites) {
        if (v.type !== 'vehicule' || v.etat === 'epave' || !v.sirene) continue;
        // Au volant, on l'a sur le toit : plein volume, sans distance.
        const d = v.conducteur === j ? 0 : Math.hypot(v.x - j.x, v.y - j.y);
        const part = Math.max(0, 1 - d / SIRENE_PORTEE_PX);
        const slug = boucleDeSirene(v);
        if (part > voulu[slug]) voulu[slug] = part;
      }
    }
    for (const slug in voulu) {
      const part = voulu[slug] > 0.02 ? voulu[slug] : 0;
      const avant = sirenes[slug] || 0;
      // ⚠️ Le melangeur retient CE QU'IL A DEMANDE, il ne lit pas l'etat de
      // `Son`. Un mp3 absent (ou un navigateur sans geste) laisse
      // `boucleActive` a faux pour toujours : s'y fier, c'est redemander la
      // meme boucle soixante fois par seconde sans jamais s'en rendre compte.
      if (part && !avant) Son.boucle(slug, true, part);
      else if (part) Son.reglerBoucle(slug, part);
      else if (avant) Son.boucle(slug, false);
      sirenes[slug] = part;
    }
  }

  function maj() {
    majPanne();
    const j = B.joueur;
    if (!j || B.interieur) { majSirenes(); return; }
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const v = B.entites[i];
      if (v.type !== 'vehicule') continue;
      // ⚠️ A BORD DU TRAVERSIER, un char ne roule pas, ne brule pas et ne coule pas :
      // la coque le porte au-dessus de l'eau (`Traversier.maj` le pose au pixel).
      if (v.aBord) continue;
      majEtatDuChar(v);
      if (v.etat === 'epave') { if (v.epaveT <= 0 && !Entites.visibleAEcran(v.x, v.y, 40)) Entites.retirer(v); continue; }
      // ⚠️ UNE CHARGE NE CONDUIT PAS. `majCrochet` vient de la POSER, au pixel
      // et au cap ; la laisser ensuite passer par `majPhysique` et `avancer`,
      // c'est lui faire refaire sa propre physique par-dessus — elle se
      // degageait des tuiles, rebondissait sur les murs et repartait de biais,
      // exactement le jeu qu'on venait d'enlever. C'est la remorqueuse qui
      // refuse de passer la ou sa charge ne passe pas (`chargeBloquee`), pas la
      // charge qui se debat.
      if (v.remorqueePar) continue;
      const x0 = v.x, y0 = v.y;
      if (v.conducteur === j) majJoueur(j);
      else if (v.conducteur === 'trafic') majConducteur(v);
      else if (v.conducteur === 'ligne') Autobus.conduire(v);
      else if (v.conducteur === 'police') { const c = Police.commandes(v); if (c === 'rails') majConducteur(v); else majPhysique(v, c); }
      else majPhysique(v, { gaz: 0, frein: 0, direction: 0 });
      // La chasse finie, la sirene de l'auto-patrouille se tait.
      if (v.conducteur === 'police') v.sirene = B.recherche.etoiles > 0;
      if (v.conducteur === 'trafic' || v.conducteur === 'ligne' || (v.conducteur === 'police' && v.surRails)) {
        v.x += v.vx; v.y += v.vy;
        heurterVehicules(v);
        heurterPietons(v);
        if (B.options.trace) majTrace(v);
      } else if (Math.abs(v.vx) + Math.abs(v.vy) > 0.01 || v.z > 0) avancer(v);
      else { heurterPietons(v); degager(v); }             // a l'arret, mais quelqu'un a pu le pousser
      // La distance ROULEE, pas la vitesse : c'est elle qui tourne les pedales.
      // Un velo pousse contre un mur a de la vitesse et ne pedale pas.
      v.parcouru += Math.hypot(v.x - x0, v.y - y0);
      if (v.conducteur === j) { j.x = v.x; j.y = v.y; j.angle = v.angle; }
      // ⚠️ LA CHARGE SE POSE APRES QUE LA REMORQUEUSE A BOUGE, jamais avant.
      // Placee au debut de l'image, elle l'etait d'apres la position de
      // l'image PRECEDENTE : l'ecart respirait alors de la distance parcourue
      // dans l'image — deux pixels a vitesse de croisiere, et c'est exactement
      // le jeu qu'une corde a et qu'une fourche n'a pas. Le juge l'a vu.
      majCrochet(v);
    }
    // Les autobus : ceux que l'horaire fait naitre, et le passager qui suit le sien.
    Autobus.maj();
    peupler();
    majSirenes();
    // ⚠️ LA PORTE GAGNE SUR LA PORTIERE (bug de Martin : devant le garage,
    // avec un char gare devant, « ENTRER » faisait monter dans le char). La
    // meme pression d'ACTION est lue ici APRES `Combat.maj`, dans la meme
    // image : si elle a deja ouvert un menu ou lance le fondu d'une porte,
    // elle est depensee. Un menu et un fondu figent tout le jeu (`Jeu.maj`) ;
    // la portiere d'a cote ne fait pas exception — sinon on passait la porte
    // deja au volant, et `Jeu.entrer` refusait.
    if (!j.dansVehicule && !j.manege && Entree.neuf('action') && !j.roule && j.descenduT !== B.t && !B.cinema && !B.menu && !B.transition && !B.piratage) {
      const v = vehiculeSousLaMain(j);
      if (v && !Missions.interagir(j)) monter(j, v);
    }
  }

  // --- La trace : le trajet de chaque char, valide par le jeu lui-meme ----------------------
  //
  // Idee de Martin : plutot que de deviner au banc pourquoi un char reste pris,
  // le jeu DESSINE ses trajets (option TRACE, ou ?trace=1) et se surveille :
  // chien de garde declenche, char qui repasse dans la meme boite, char hors
  // de la chaussee. Chaque anomalie garde le trajet des huit dernieres secondes
  // et s'affiche en rouge sur place — une capture d'ecran suffit a la raconter.

  const TRACE_POINTS = 120, TRACE_TOUTES_LES = 4, TRACE_ANOMALIES_MAX = 30, TRACE_MONTRE = 600;
  let boitesId = 0;

  function noterLaBoite(v, inter) {
    inter.id = inter.id || ++boitesId;
    v.boites = v.boites || [];
    v.boites.push({ id: inter.id, t: B.t });
    if (v.boites.length > 8) v.boites.shift();
  }

  function anomalie(v, quoi, etat) {
    const a = { t: B.t, quoi: quoi, slug: v.slug, id: v.id, x: v.x, y: v.y, tx: Math.floor(v.x / TT), ty: Math.floor(v.y / TT),
                etat: etat || etatCourt(v), points: (v.trace || []).slice() };
    B.trace.anomalies.push(a);
    B.trace.total++;
    if (B.trace.anomalies.length > TRACE_ANOMALIES_MAX) B.trace.anomalies.shift();
    if (typeof console !== 'undefined' && console.warn) console.warn('[trace] ' + quoi + ' — ' + v.slug + '#' + v.id + ' en (' + a.tx + ',' + a.ty + ') ' + a.etat);
    return a;
  }

  /** L'etat d'un char de trafic en trois lettres : ce qu'il attend, depuis combien de temps. */
  function etatCourt(v) {
    let e = v.attendFeu ? 'FEU' : v.stopT !== undefined ? 'STOP' : v.attenteBoite > 0 ? 'BOITE' : v.deportT > 0 ? 'DEPORT' : v.enBoite ? 'DANS' : 'ROULE';
    if (v.immobileT > 60) e += ' ' + Math.round(v.immobileT / 60) + 'S';
    return e;
  }

  /** A chaque image, pour un char du trafic : le trajet, et les trois verifications. */
  function majTrace(v) {
    if (B.t % TRACE_TOUTES_LES === 0) {
      v.trace = v.trace || [];
      v.trace.push({ x: v.x, y: v.y });
      if (v.trace.length > TRACE_POINTS) v.trace.shift();
    }
    // 1. Le chien de garde a du le deplacer : les rails ont failli.
    if ((v.debloques || 0) > (v.traceDebloques || 0)) { v.traceDebloques = v.debloques; anomalie(v, 'CHIEN DE GARDE', v.etatBloque); }
    // 2. Il repasse dans la meme boite : il tourne en rond.
    if (v.boites && v.boites.length >= 3) {
      const dernier = v.boites[v.boites.length - 1];
      const memes = v.boites.filter(function (b) { return b.id === dernier.id && dernier.t - b.t < 1200; }).length;
      if (memes >= 3 && v.traceRond !== dernier.t) { v.traceRond = dernier.t; anomalie(v, 'TOURNE EN ROND'); }
    }
    // 3. Il roule hors de la chaussee.
    const tx = Math.floor(v.x / TT), ty = Math.floor(v.y / TT);
    // ⚠️ Un velo parti sur le trottoir ou au parc (`horsRue`) y est de son plein gre.
    const surRoute = Monde.estChaussee(tx, ty) || Monde.estRampe(tx, ty) || Monde.estPassage(tx, ty) || !!v.horsRue;
    v.horsVoieT = surRoute ? 0 : (v.horsVoieT || 0) + 1;
    if (v.horsVoieT === 90) anomalie(v, 'HORS VOIE');
  }

  /** Les anomalies encore fraiches (dix secondes) — ce que l'ecran montre. */
  function anomaliesFraiches() {
    return B.trace.anomalies.filter(function (a) { return B.t - a.t < TRACE_MONTRE; });
  }

  function dessinerTrace(ctx, vue) {
    const cx = vue.x, cy = vue.y;
    ctx.lineWidth = 1;
    for (const v of B.entites) {
      if (v.type !== 'vehicule' || (v.conducteur !== 'trafic' && v.conducteur !== 'police') || !v.trace) continue;
      if (!Entites.visibleAEcran(v.x, v.y, 80)) continue;
      const bloque = v.immobileT > 120;
      ctx.strokeStyle = bloque ? '#ff5a4e' : v.attendFeu || v.stopT !== undefined || v.attenteBoite > 0 ? '#ffd23a' : '#5fe08a';
      ctx.beginPath();
      v.trace.forEach(function (q, i) { if (i === 0) ctx.moveTo(q.x - cx, q.y - cy); else ctx.lineTo(q.x - cx, q.y - cy); });
      ctx.stroke();
      if (v.cible && v.cible.tx !== undefined) {           // ou il veut aller
        ctx.strokeStyle = '#7fc4ff';
        ctx.beginPath(); ctx.moveTo(v.x - cx, v.y - cy); ctx.lineTo(v.cible.tx * TT + 8 - cx, v.cible.ty * TT + 8 - cy); ctx.stroke();
      }
      if (v.sortie && v.sortie.tx !== undefined) {         // la sortie qu'il a choisie
        ctx.fillStyle = '#7fc4ff'; ctx.fillRect(v.sortie.tx * TT + 6 - cx, v.sortie.ty * TT + 6 - cy, 4, 4); B.stats.rects++;
      }
      Atlas.texte(ctx, etatCourt(v), Math.round(v.x - cx - 10), Math.round(v.y - cy - 16), bloque ? '#ff5a4e' : '#ffffff', 1);
    }
    for (const a of anomaliesFraiches()) {
      if (!Entites.visibleAEcran(a.x, a.y, 80)) continue;
      ctx.strokeStyle = '#ff5a4e';
      ctx.beginPath();
      a.points.forEach(function (q, i) { if (i === 0) ctx.moveTo(q.x - cx, q.y - cy); else ctx.lineTo(q.x - cx, q.y - cy); });
      ctx.stroke();
      if ((B.t >> 3) % 2 === 0) { ctx.beginPath(); ctx.arc(a.x - cx, a.y - cy, 12, 0, Math.PI * 2); ctx.stroke(); }
      Atlas.texte(ctx, a.quoi, Math.round(a.x - cx - 20), Math.round(a.y - cy + 14), '#ff5a4e', 1);
    }
  }

  /** Le bilan de la trace : ce que le HUD ecrit, ce qu'un test verifie. */
  function bilanTrace() {
    const chars = B.entites.filter(function (v) { return v.type === 'vehicule' && v.conducteur === 'trafic'; });
    return { chars: chars.length, immobiles: chars.filter(function (v) { return v.immobileT > 120; }).length,
             anomalies: B.trace.anomalies.length, total: B.trace.total, fraiches: anomaliesFraiches().length };
  }

  // --- Les feux et les stops, comme du mobilier ---------------------------------------

  /** Le coin de trottoir libre le plus proche : pas la borne-fontaine, pas le
      pied du lampadaire, et — si on lui passe la carte des poteaux — pas dans
      un poteau deja plante.

      ⚠️ `decorAutour` ne voit QUE le decor solide (`grilleFixe`) : un feu n'y
      entre jamais. C'est pour ca que les 124 feux de chars se sont retrouves
      a la tuile pres dans un poteau pieton. Le decor solide ne suffit pas a
      dire « la place est prise ». */
  function coinLibre(tx, ty, poteaux) {
    const essais = [[tx, ty], [tx + 1, ty], [tx, ty - 1], [tx - 1, ty], [tx, ty + 1], [tx + 1, ty - 1]];
    for (const c of essais) {
      if (Monde.glyphe(c[0], c[1]) !== '.') continue;
      if (poteaux && poteaux.has(c[0] + ',' + c[1])) continue;
      if (Entites.decorAutour(c[0] * TT + 8, c[1] * TT + 8, 10).length) continue;
      return c;
    }
    return [tx, ty];
  }

  /** Les QUATRE coins d'un croisement a feux, et l'axe que chacun montre.

      ⚠️ Un tricolore ne montre qu'UNE rue — c'est ce qu'est un tricolore. Il
      faut donc que de n'importe quelle approche, un feu de SON axe soit en
      face. L'astuce tient a une diagonale : nord-est et sud-ouest portent le
      nord-sud, nord-ouest et sud-est l'est-ouest. Qui arrive du sud a le
      nord-est et le nord-ouest devant lui — donc un « ns » ; qui arrive de
      l'ouest a le nord-est et le sud-est — donc un « eo ». Les deux coins
      d'en face sont toujours d'une diagonale et de l'autre, et un juge le
      verifie pour les quatre approches.

      ⚠️ Et c'est aussi ce qui donne au croisement son QUATRIEME poteau. On
      n'en posait que deux (« les lampadaires ont les autres »), et il
      manquait donc un feu a deux coins sur quatre. */
  function COINS(inter) {
    // ⚠️ Le BRAS part vers le croisement, donc AU-DESSUS DE LA CHAUSSEE : les
    // coins de l'est le tendent vers l'ouest, ceux de l'ouest vers l'est. Une
    // potence qui porte a faux au-dessus du trottoir ne sert a personne.
    return [[inter.x + inter.l, inter.y - 1, 'ns', -1],          // nord-est
            [inter.x - 1, inter.y + inter.h, 'ns', 1],           // sud-ouest
            [inter.x - 1, inter.y - 1, 'eo', 1],                 // nord-ouest
            [inter.x + inter.l, inter.y + inter.h, 'eo', -1]];   // sud-est
  }

  //: Combien de traverses un seul mat porte : DEUX, celles qui se croisent a
  //: son coin. Au-dela, c'est que la grappe n'est pas un coin.
  const TRAVERSES_PAR_MAT = 2;

  //: A quelle distance deux poteaux sont « le meme coin » : UNE tuile.
  //: ⚠️ Ce n'est pas un reglage de gout, c'est une MESURE : a chaque
  //: croisement de la ville, les poteaux se groupaient par deux, et les 174
  //: paires etaient a une tuile l'une de l'autre — pas une seule a deux. Une
  //: tuile, c'est deux metres et demi : dans la vraie vie, ces deux tetes-la
  //: sont sur le meme mat, et c'est ce qui faisait « trop de poteaux ».
  const MEME_COIN = 1;

  /** Le mat du coin `tx, ty` qui peut encore prendre une traverse, ou null.
      La tuile elle-meme d'abord — un feu de chars y est deja — puis l'anneau
      d'une tuile autour. */
  function matDuCoin(poteaux, inter, tx, ty) {
    for (let d = 0; d <= MEME_COIN; d++) {
      for (let dy = -d; dy <= d; dy++) {
        for (let dx = -d; dx <= d; dx++) {
          if (Math.max(Math.abs(dx), Math.abs(dy)) !== d) continue;
          const e = poteaux.get((tx + dx) + ',' + (ty + dy));
          if (e && e.inter === inter && e.traverses && e.traverses.length < TRAVERSES_PAR_MAT) return e;
        }
      }
    }
    return null;
  }

  function creerSignalisation() {
    const carte = Monde.carte;
    // ⚠️ LES POTEAUX DES CHARS D'ABORD, et c'est ce qui empeche d'en planter
    // deux au meme endroit. `coinLibre` vise le coin nord-est et le coin
    // sud-ouest du croisement — precisement les bouts de traverse ou
    // `carte.py` a deja pose un feu pieton — et il ne les voit pas, parce
    // qu'il n'ecarte que le decor SOLIDE (`grilleFixe`), ou un feu n'entre
    // jamais. Les 124 feux de chars etaient donc plantes DANS un poteau
    // pieton, a la tuile pres : 124 sur 124. Tant que les lanternes n'etaient
    // pas peintes, deux poteaux noirs l'un dans l'autre ne se voyaient pas.
    const poteaux = new Map();
    carte.intersections.forEach(function (inter) {
      if (inter.feux) {
        for (const coin of COINS(inter)) {
          const c = coinLibre(coin[0], coin[1]);
          // ⚠️ LE MAT SE PLANTE AU BORD DE SA TUILE, DU COTE DE LA RUE, pas en
          // son milieu. Le bras porte a faux sur 13 px ; depuis le centre
          // (+8), dix de ces treize restaient au-dessus du TROTTOIR et la tete
          // n'etait pas sur la chaussee — elle etait a cote. Colle au bord, le
          // bras passe la bordure a trois pixels et pend au-dessus de la voie,
          // ce qu'une potence est censee faire.
          const e = Entites.creer('feu', c[0] * TT + (coin[3] > 0 ? TT - 3 : 3), c[1] * TT + 15,
                                  { inter: inter, axe: coin[2], bras: coin[3], traverses: [], r: 2, solide: false });
          poteaux.set(c[0] + ',' + c[1], e);
        }
      } else if (inter.stop) {
        const coins = { '<': [inter.x + inter.l, inter.y - 1], '>': [inter.x - 1, inter.y + inter.h],
                        'v': [inter.x - 1, inter.y - 1], '^': [inter.x + inter.l, inter.y + inter.h] };
        const c = coinLibre(coins[inter.stop][0], coins[inter.stop][1]);
        poteaux.set(c[0] + ',' + c[1], Entites.creer('stop', c[0] * TT + 8, c[1] * TT + 15,
                                                     { inter: inter, decor: 'stop', r: 2, solide: false }));
      }
    });
    // ⚠️ LES FEUX PIETONS VIENNENT DE LA CARTE, pas d'un coin devine ici. Leur
    // place se lit sur la TRAVERSE — un a chaque bout, et le sens du passage
    // avec (`carte.py`, `feux_pietons`). Les deviner depuis la boite du
    // croisement, comme on le fait pour les feux des chars, c'est se tromper
    // des que la traverse ne tombe pas ou l'on croit.
    //
    // ⚠️ ET LA TETE SE POSE SUR LE MAT QUI EST DEJA LA. Un vrai carrefour ne
    // plante pas deux poteaux a un metre l'un de l'autre : la tete des chars
    // regarde la rue, celle des pietons regarde la traverse, et elles
    // partagent le mat. Ecarter le feu des chars d'une tuile aurait fait un
    // poteau DE PLUS a regarder, au lieu d'un de moins.
    //
    // ⚠️ ET PAS DE CHAMP `decor` SUR UN FEU. Il y en avait un, et il a rendu
    // les feux MUETS depuis le jour ou on les a poses : `Entites.dessiner`
    // teste `if (e.decor)` AVANT `if (e.type === 'feu')`, donc la branche
    // generique gagnait, peignait le boitier cuit — et s'en allait. Le champ
    // ne servait a rien d'autre (un feu n'est pas solide, il n'entre donc
    // jamais dans `grilleFixe`, et `dessinerFeu` nomme sa propre fiche) : il
    // ne faisait que masquer le peintre.
    (carte.def.feux_pietons || []).forEach(function (f) {
      const inter = Monde.intersectionA(f.x, f.y);
      if (!inter || !inter.feux) return;
      const mat = matDuCoin(poteaux, inter, f.x, f.y);
      if (mat) { mat.traverses.push(f.sens); return; }
      poteaux.set(f.x + ',' + f.y,
                  Entites.creer('feu_pieton', f.x * TT + 8, f.y * TT + 15,
                                { inter: inter, traverses: [f.sens], r: 1, solide: false }));
    });
  }

  // --- Les ampoules, et la lumiere qu'elles jettent -----------------------------------

  //: Une phase, c'est DEUX couleurs et pas une : l'AMPOULE (ce qu'on peint
  //: dans la scene), et la LUMIERE qu'elle jette (ce que `Base.fin` ajoute
  //: par-dessus la nuit, en `lighter`). La seconde tire vers le blanc et
  //: deborde de l'ampoule — une lampe n'est pas de la peinture.
  //:
  //: ⚠️ Sans elle, un feu ne recoit que la MULTIPLICATION du voile de nuit,
  //: comme une brique : a minuit le vert (46, 204, 113) tombe a (16, 76, 57),
  //: et le blanc qui dit MARCHE (242, 242, 242) a (86, 90, 122) — plus sombre
  //: qu'un trottoir de midi.
  //:
  //: ⚠️ Et une phase a une FORME, parce qu'un feu quebecois en a une : le
  //: rouge est CARRE, le jaune un LOSANGE, le vert un CERCLE (voir
  //: `DECORS.feu`). `rang` est sa place dans le boitier horizontal, de gauche
  //: a droite — l'ordre est celui de la rue, pas celui du code.
  const PHASES_FEU = {
    rouge: { rang: 0, forme: 'carre',   ampoule: '#e74c3c', coeur: '#ffc9bd', lumiere: 'rgba(255,105,85,0.50)' },
    jaune: { rang: 1, forme: 'losange', ampoule: '#f39c12', coeur: '#ffe3a6', lumiere: 'rgba(255,190,90,0.52)' },
    vert:  { rang: 2, forme: 'cercle',  ampoule: '#2ecc71', coeur: '#ccffdf', lumiere: 'rgba(110,255,165,0.50)',
             coin: '#1d7a45' },
    // ⚠️ La nuit : la MEME lentille, mais qui pulse. C'est la seule difference
    // — un clignotant qui changerait aussi de place dans le boitier ne se
    // lirait plus comme le feu qu'on connait.
    clignote_jaune: { rang: 1, forme: 'losange', ampoule: '#f39c12', coeur: '#ffe3a6', lumiere: 'rgba(255,190,90,0.52)', clignote: true },
    clignote_rouge: { rang: 0, forme: 'carre',   ampoule: '#e74c3c', coeur: '#ffc9bd', lumiere: 'rgba(255,105,85,0.50)', clignote: true },
  };

  /** Une lampe qui clignote est-elle ALLUMEE en ce moment ? */
  function pulse() {
    return Math.floor(B.t / trafic().clignotant_images) % 2 === 0;
  }

  //: De quelle couleur se lit chaque etat du feu pieton. ⚠️ LE BLANC QUI
  //: MARCHE, L'ORANGE QUI ARRETE : deux couleurs qu'on distingue d'un coup
  //: d'oeil a cette taille, et qui ne se confondent avec aucune des trois du
  //: feu des chars — on ne doit pas avoir a se demander lequel on regarde.
  const PHASES_FEU_PIETON = {
    blanc:  { ampoule: '#f2f2f2', coeur: '#ffffff', lumiere: 'rgba(220,235,255,0.55)' },
    degage: { ampoule: '#f39c12', coeur: '#ffe3a6', lumiere: 'rgba(255,190,90,0.58)' },
    rouge:  { ampoule: '#c0392b', coeur: '#ff9c8a', lumiere: 'rgba(255,90,75,0.52)' },
  };

  //: Le seuil de la brune. ⚠️ C'est CELUI DES LAMPADAIRES, au pixel pres
  //: (`Monde.lampesVisibles`) : deux seuils voudraient dire deux reponses a
  //: « fait-il noir ? », et la deuxieme serait fausse un jour.
  const BRUNE = 0.2;
  const LAMPES_FEUX_MAX = 24;

  //: Le RAYON d'un halo de feu. ⚠️ PETIT, et c'est la moitie du travail : le
  //: lampadaire fait 44 px parce qu'il eclaire une rue, un feu fait sept
  //: parce qu'il ne s'eclaire que lui-meme. A dix, les deux ampoules du feu
  //: des chars — cinq pixels d'ecart — additionnaient assez de rouge et de
  //: vert pour rendre du BLANC, et on ne lisait plus laquelle etait laquelle.
  const RAYON_LAMPE = 7;

  /** Les lampes des feux de l'image en cours, ramassees EN DESSINANT.

      ⚠️ Pourquoi la, et pas en balayant la ville : `carte.lampes` est une
      liste FIXE qu'on peut parcourir, les feux sont 482 poteaux (124 pour les
      chars, 358 pour les pietons) dont la couleur change a chaque phase. Les
      passer en revue par image pour trouver les trente de l'ecran, ce serait
      payer la ville entiere pour en eclairer trente. `dessinerFeu` est deja
      appele UNE FOIS PAR FEU VISIBLE : c'est la, et nulle part ailleurs, que
      la lampe se pose.

      ⚠️ Et la liste se vide TOUTE SEULE : elle porte son numero d'image
      (`B.image`, l'horloge de l'oeil). Une liste qu'un dessin remplit et
      qu'un autre module doit penser a vider fuit le jour ou quelqu'un dessine
      sans composer. */
  const lampesFeux = { image: -1, liste: [], allume: false };

  function allumerLaLampe(x, y, c) {
    if (lampesFeux.image !== B.image) {
      lampesFeux.image = B.image;
      lampesFeux.liste.length = 0;
      // L'heure ne se demande qu'UNE FOIS par image, pas une fois par ampoule.
      lampesFeux.allume = Monde.ambiance().alpha >= BRUNE;
    }
    if (!lampesFeux.allume || lampesFeux.liste.length >= LAMPES_FEUX_MAX) return;
    lampesFeux.liste.push({ x: x, y: y, r: RAYON_LAMPE, c: c });
  }

  /** Ce que `jeu.js` donne a `Base.fin` — vide des qu'on change d'image. */
  function lampesDesFeux() { return lampesFeux.image === B.image ? lampesFeux.liste : []; }

  //: **LES PHARES** (la nuit a ses habitudes). Un char qu'on MENE allume ses
  //: lampes — ses phares luisent, ses feux arriere rougeoient — et ses phares BAS
  //: jettent un faisceau sur la chaussee devant lui. Un char gare est eteint :
  //: c'est ce qui dit, de loin, lequel va bouger. Ramasses EN DESSINANT, comme
  //: les feux de circulation, et pour la meme raison : `dessinerUn` ne passe que
  //: sur les chars de l'ecran.
  //:
  //: ⚠️ **LES LAMPES VIENNENT DE LA MACHINE** (retour de Martin : « ajuste
  //: correctement les phares pour tous les types de véhicules le soir »). Il n'y
  //: avait qu'un halo rond, 16 px devant le nez, le meme pour le velo et pour
  //: l'autobus : il debordait sur la caisse et derriere elle, un camion n'avait
  //: qu'un feu arriere au milieu, et le chalutier roulait avec des phares d'auto.
  //: Chaque machine declare deja ou sont ses lampes — ses pieces `l` et `t`, ce
  //: qu'elle peint — : les lire, c'est les poser au pixel pres pour toutes les
  //: silhouettes, et pour celles qui viendront.
  //:
  //: Le FAISCEAU de chaque classe : `portee` (px devant les phares), `ouverture`
  //: (ce qu'il gagne de chaque cote au bout de sa portee) et `force`. ⚠️ `null`,
  //: aucun : un bateau n'eclaire pas l'eau devant lui, il montre ses feux de
  //: navigation. Une classe ABSENTE n'en a pas non plus — et un juge exige que
  //: chaque classe du catalogue y soit, pour que ce soit une decision.
  const FAISCEAUX = {
    auto:   { portee: 56, ouverture: 13, force: 0.36 },
    camion: { portee: 68, ouverture: 16, force: 0.38 },
    moto:   { portee: 54, ouverture: 10, force: 0.34 },
    velo:   { portee: 26, ouverture: 5, force: 0.20 },
    bateau: null,
  };
  //: Un phare BAS eclaire la chaussee ; un phare HAUT — le feu de mat d'un
  //: bateau, les feux d'arret de l'autobus scolaire — ne fait que luire.
  const PHARE_BAS_Z = 10;
  //: La lueur sur chaque lampe peinte : petite, comme celle d'un feu de
  //: circulation (`RAYON_LAMPE`) — une lampe ne s'eclaire qu'elle-meme.
  const LUEURS = { l: { rayon: 5, alpha: 0.55, defaut: '#fff3b0' }, t: { rayon: 5, alpha: 0.5, defaut: '#ff4b3e' } };
  //: ⚠️ LE PLAFOND COMPTE DES CHARS. Il comptait des lampes — douze, deux par
  //: char : passe six chars a l'ecran, les suivants roulaient eteints. Un char de
  //: ville en allume cinq (un faisceau, deux phares, deux feux) ; l'autobus
  //: scolaire et le cabriolet sept. Des places gardees pour le char du joueur :
  //: c'est lui qu'on regarde.
  const CHARS_ECLAIRES_MAX = 14;
  const LAMPES_PAR_CHAR_MAX = 7;
  const LAMPES_PHARES_MAX = CHARS_ECLAIRES_MAX * LAMPES_PAR_CHAR_MAX;
  //: ⚠️ LE SOIR, LE FAISCEAU MONTE AVEC LA NUIT. Allume a la brune (18 h 40), il
  //: jetait deja toute sa force sur une chaussee a peine assombrie : des cones
  //: blancs sur une rue encore orangee. Il part du tiers (`FAISCEAU_A_LA_BRUNE`)
  //: et n'a toute sa force qu'a la nuit faite (`NUIT_FAITE`, l'ambiance de 21 h).
  //: Les LUEURS, elles, sont pleines des qu'on allume : une lampe allumee se
  //: voit, soir ou pas.
  const FAISCEAU_A_LA_BRUNE = 0.35;
  const NUIT_FAITE = 0.62;
  const lampesPhares = { image: -1, liste: [], allume: false, fondu: 1 };

  /** Les lampes d'une silhouette, lues UNE FOIS dans sa machine : ou elles sont
      (`u` vers l'avant, `w` vers la droite, `z` en hauteur, en px), et la
      couleur de leur lueur, tiree de la palette — le phare jaunatre d'une
      vieille auto, le feu rouge qu'elle peint. `bas` : le milieu et la
      demi-largeur des phares BAS, d'ou part le faisceau (null s'il n'y en a pas).

      ⚠️ Une piece de lampe a trois formes : `bloc` (ses trois faces, dont une
      au moins est `l` ou `t` — le phare de la moto a le dessus noir), `point`
      (le feu du velo, au bout du porte-bagages) et `tube`. */
  const lampesDesMachines = new Map();
  function lampesDeLaMachine(nom) {
    if (lampesDesMachines.has(nom)) return lampesDesMachines.get(nom);
    const def = SPRITES[nom];
    const liste = [];
    for (const p of (def && def.machine ? def.machine.pieces : [])) {
      let lettre = null, u = 0, w = 0, z = 0;
      if (p[0] === 'bloc') {
        lettre = [p[4], p[5], p[6]].find(function (ch) { return ch === 'l' || ch === 't'; }) || null;
        u = (p[1][0] + p[1][1]) / 2; w = (p[2][0] + p[2][1]) / 2; z = (p[3][0] + p[3][1]) / 2;
      } else if (p[0] === 'point') {
        lettre = p[2]; u = p[1][0]; w = p[1][1]; z = p[1][2];
      } else if (p[0] === 'tube') {
        lettre = p[3]; u = (p[1][0] + p[2][0]) / 2; w = (p[1][1] + p[2][1]) / 2; z = (p[1][2] + p[2][2]) / 2;
      }
      if (lettre !== 'l' && lettre !== 't') continue;
      const lueur = LUEURS[lettre];
      liste.push({ u: u, w: w, z: z, lettre: lettre, r: lueur.rayon,
                   c: rgba((def.pal && def.pal[lettre]) || lueur.defaut, lueur.alpha) });
    }
    const bas = liste.filter(function (l) { return l.lettre === 'l' && l.z < PHARE_BAS_Z; });
    if (bas.length) {
      const ws = bas.map(function (l) { return l.w; });
      const w0 = Math.min.apply(null, ws), w1 = Math.max.apply(null, ws);
      liste.bas = { u: Math.max.apply(null, bas.map(function (l) { return l.u; })),
                    w: (w0 + w1) / 2, demi: (w1 - w0) / 2 };
    } else liste.bas = null;
    liste.profondeur = (def && def.machine && def.machine.profondeur) || 1;
    lampesDesMachines.set(nom, liste);
    return liste;
  }

  function rgba(hex, a) {
    const n = parseInt(hex.slice(1), 16);
    return 'rgba(' + (n >> 16 & 255) + ',' + (n >> 8 & 255) + ',' + (n & 255) + ',' + a + ')';
  }

  /** Jusqu'ou le faisceau porte avant un MUR — et un toit compte pareil : les
      deux partagent la meme solidite (1), comme pour `Jeu.ligneLibre`. Un char
      gare contre un mur, ou une ruelle qui tourne, ne doit pas jeter sa lumiere
      A TRAVERS (retour de Martin : « les phares ne doivent pas passer au
      travers des toits »).

      ⚠️ Depuis le PHARE (`x0`, `y0`), pas depuis le centre du char : un phare
      pres du trottoir voit le mur d'a cote une demi-tuile avant celui du
      centre. Marche par quarts de tuile — assez fin pour ne pas sauter un mur
      d'une tuile a un angle serre — et rend la distance JUSTE AVANT le mur, pas
      dedans. */
  function porteeLibre(x0, y0, ca, sa, portee) {
    const pas = TT / 4;
    for (let d = pas; d < portee; d += pas) {
      if (Monde.solidite(Math.floor((x0 + ca * d) / TT), Math.floor((y0 + sa * d) / TT)) === 1) return d - pas;
    }
    return portee;
  }

  function allumerLesPhares(v, cx, cy) {
    if (lampesPhares.image !== B.image) {
      lampesPhares.image = B.image;
      lampesPhares.liste.length = 0;
      const noir = Monde.ambiance().alpha;
      lampesPhares.allume = noir >= BRUNE;
      lampesPhares.fondu = FAISCEAU_A_LA_BRUNE + (1 - FAISCEAU_A_LA_BRUNE)
        * Math.max(0, Math.min(1, (noir - BRUNE) / (NUIT_FAITE - BRUNE)));
    }
    if (!lampesPhares.allume || !v.conducteur || v.etat === 'epave' || v.panneT > 0 || !v.def) return;
    const lampes = lampesDeLaMachine(v.sprite);
    const faisceau = lampes.bas ? FAISCEAUX[v.def.classe] || null : null;
    const n = lampes.length + (faisceau ? 1 : 0);
    const plafond = v.conducteur === B.joueur ? LAMPES_PHARES_MAX : LAMPES_PHARES_MAX - LAMPES_PAR_CHAR_MAX;
    if (!n || lampesPhares.liste.length + n > plafond) return;
    // ⚠️ Le cap DESSINE, pas `v.angle` : le toit est cuit au cran le plus
    // proche, et une lueur posee au cap exact glisserait a cote de sa lampe.
    const cap = capDe(v.angle) * Math.PI * 2 / ROTATIONS - Math.PI / 2;
    const ca = Math.cos(cap), sa = Math.sin(cap), k = lampes.profondeur;
    if (faisceau) {
      // ⚠️ AU SOL (`v.y`, pas `v.y - v.z`) : la flaque de lumiere est sur la
      // chaussee, comme l'ombre, meme quand le char saute. Et ECRASEE comme
      // elle (`p`) : le sol se voit de biais. Il part des phares, pas de
      // devant le nez — ce qui s'allume derriere les phares, c'est la caisse.
      const b = lampes.bas, sol = ombreDe(v);
      // Le phare, en VRAI monde (non ecrase) : c'est depuis la, et dans le cap
      // dessine, qu'on marche pour trouver le premier mur devant lui.
      const ox = v.x + b.u * ca - b.w * sa, oy = v.y + b.u * sa + b.w * ca;
      const portee = porteeLibre(ox, oy, ca, sa, faisceau.portee);
      lampesPhares.liste.push({
        x: ox - cx, y: v.y + (b.u * sa + b.w * ca) * k - cy,
        a: cap, p: sol ? sol.profondeur : k, r: portee,
        cone: [b.demi + 1, b.demi + 1 + faisceau.ouverture * (portee / faisceau.portee)],
        c: 'rgba(255,236,190,' + (faisceau.force * lampesPhares.fondu).toFixed(3) + ')', faisceau: v,
      });
    }
    const x0 = v.x - cx, y0 = v.y - v.z - cy;
    for (const l of lampes) {
      const lampe = { x: x0 + l.u * ca - l.w * sa, y: y0 + (l.u * sa + l.w * ca) * k - l.z, r: l.r, c: l.c };
      if (l.lettre === 't') lampe.arriere = v; else lampe.phare = v;
      lampesPhares.liste.push(lampe);
    }
  }

  /** Ce que `jeu.js` donne a `Base.fin` — vide des qu'on change d'image. */
  function lampesDesPhares() { return lampesPhares.image === B.image ? lampesPhares.liste : []; }

  /** Une ampoule allumee : le pourtour de la phase, un COEUR plus pale, et la
      lampe qu'elle jette a la brune.

      ⚠️ C'est le coeur qui dit « allumee » ; la couleur, elle, ne dit que
      LAQUELLE. Un carre vert plat reste un carre vert — en plein jour, ou le
      halo ne se compose pas, c'est la seule chose qui distingue une ampoule
      d'une pastille peinte, et la seule qui tienne dans trois pixels. */
  function ampoule(ctx, x, y, w, h, phase) {
    ctx.fillStyle = phase.ampoule; ctx.fillRect(x, y, w, h);
    ctx.fillStyle = phase.coeur;
    ctx.fillRect(x + ((w - 1) >> 1), y + ((h - 1) >> 1), w > 3 ? 2 : 1, h > 3 ? 2 : 1);
    allumerLaLampe(x + w / 2, y + h / 2, phase.lumiere);
    B.stats.rects += 2;
  }

  /** Les tetes pieton d'un boitier : une, ou DEUX cote a cote quand le coin
      sert deux traverses. `x` est le BORD GAUCHE du boitier et `large` sa
      largeur — c'est l'appelant qui les calcule, parce qu'une potence et un
      poteau isole ne les posent pas au meme endroit.

      ⚠️ A deux, les ampoules retrecissent a trois pixels et tombent a un
      pixel de chaque bord. Sur une potence, ca les met AUX MEMES COLONNES que
      les lentilles des chars juste au-dessus : le mat devient une pile de
      boitiers dont les feux s'alignent, et c'est ce qui le fait lire comme UN
      poteau plutot que comme deux colles. A quatre pixels chacune, elles se
      toucheraient — et deux rouges qui se touchent, c'est un seul rectangle
      rouge.

      ⚠️ Le SENS DES CHARS de la rue qu'on traverse, lu comme `traverseeSure`
      le lit : « = » barre une rue est-ouest. Deux endroits qui traduisent le
      meme glyphe, c'etait un endroit de trop — il n'y en a plus qu'un. */
  function tetesDeTraverse(ctx, x, y, large, inter, traverses) {
    ctx.fillStyle = '#2c2c30';
    ctx.fillRect(x, y, large, 7);
    B.stats.rects++;
    const deux = traverses.length > 1, cote = deux ? 3 : 4;
    for (let i = 0; i < traverses.length; i++) {
      const etat = Monde.feuPieton(inter, traverses[i] === '=' ? '>' : '^');
      // Le degagement CLIGNOTE : un orange fixe se lit comme « attends », un
      // orange qui bat se lit comme « finis, mais ne pars plus ». ⚠️ Et la
      // LAMPE S'ETEINT AVEC L'AMPOULE, puisqu'on saute avant de la poser : un
      // orange qui bat a l'oeil et brille en continu au sol, c'est pire qu'un
      // clignotant qui ne clignote pas.
      if (etat === 'degage' && (B.t >> 3) % 2 === 0) continue;
      const col = deux ? (i === 0 ? x + 1 : x + large - 1 - cote) : x + ((large - cote) >> 1);
      ampoule(ctx, col, y + 1, cote, 5, PHASES_FEU_PIETON[etat] || PHASES_FEU_PIETON.rouge);
    }
  }

  /** Une abscisse du gabarit, retournee quand le bras part vers l'ouest.
      ⚠️ Le MEME calcul que `peindreFeu` dans sprites.js, et c'est voulu : le
      boitier est cuit, la lentille vive se peint par-dessus, et si les deux ne
      retournaient pas pareil elle s'allumerait a cote de son trou. */
  function miroir(x, l, bras) { return bras > 0 ? x : DECORS.feu.w - x - l; }

  /** LA lentille allumee — il n'y en a qu'une a la fois, c'est tout l'objet
      d'un tricolore. `x, y` : son coin.

      ⚠️ La FORME se peint ici, pas dans la fiche : c'est elle qui change. Le
      carre est plein, le losange est une croix (cinq pixels sur neuf : a
      trois pixels, c'est tout ce qu'un losange peut etre), et le cercle est
      un carre dont les QUATRE COINS sont adoucis vers un vert sombre — c'est
      la facon dont le pixel art arrondit, et la seule qui distingue un rond
      d'un carre a cette taille. */
  function lentille(ctx, x, y, phase) {
    ctx.fillStyle = phase.ampoule;
    if (phase.forme === 'losange') {
      ctx.fillRect(x + 1, y, 1, 3); ctx.fillRect(x, y + 1, 3, 1);
      B.stats.rects += 2;
    } else {
      ctx.fillRect(x, y, 3, 3);
      B.stats.rects++;
    }
    if (phase.forme === 'cercle') {
      ctx.fillStyle = phase.coin;
      ctx.fillRect(x, y, 1, 1); ctx.fillRect(x + 2, y, 1, 1);
      ctx.fillRect(x, y + 2, 1, 1); ctx.fillRect(x + 2, y + 2, 1, 1);
      B.stats.rects += 4;
    }
    // Le coeur : c'est lui qui dit « allumee », la couleur ne dit que laquelle.
    ctx.fillStyle = phase.coeur; ctx.fillRect(x + 1, y + 1, 1, 1);
    B.stats.rects++;
    allumerLaLampe(x + 1.5, y + 1.5, phase.lumiere);
  }

  /** Un feu : un boitier cuit avec ses trois douilles eteintes, UNE lentille
      allumee par-dessus — et, quand le coin sert aussi des traverses, leurs
      tetes sur le MEME MAT (voir `creerSignalisation`).

      ⚠️ La couleur vient de `Monde.feuDeCirculation`, celle-la meme dont
      `feuVert` decoule et a laquelle le trafic obeit (`prochaineCible`). Le
      feu ne peut donc pas montrer une couleur qu'un char ne respecte pas :
      c'est la meme phrase lue deux fois, jamais deux phrases. */
  function dessinerFeu(ctx, e, cx, cy) {
    const d = DECORS.feu, droite = e.bras > 0;
    const poteau = droite
      ? Atlas.cuirePeintre('decor|feu', d.w, d.h, d.peindre)
      : Atlas.cuirePeintre('decor|feu|miroir', d.w, d.h, d.peindreMiroir);
    const ancre = droite ? d.ancre : d.ancreMiroir;
    const x = Math.round(e.x - ancre[0] - cx), y = Math.round(e.y - ancre[1] - cy);
    ctx.drawImage(poteau, x, y);
    const phase = PHASES_FEU[Monde.feuDeCirculation(e.inter, e.axe === 'ns' ? '^' : '>')];
    // Le clignotant s'eteint une pulsation sur deux : la douille reste, la
    // lumiere part — c'est ce qui se voit de loin sur une ville deserte.
    if (!phase.clignote || pulse()) {
      lentille(ctx, x + miroir(d.lentilles[phase.rang], d.lentilleCote, e.bras), y + d.lentilleY, phase);
    }
    // ⚠️ Le boitier des tetes pieton se peint ICI, pas dans la fiche cuite :
    // un mat n'en porte pas toujours, et une boite noire pendue a une potence
    // qui n'a pas de traverse est un defaut qu'on ne voit qu'au bon coin de la
    // ville. Elles pendent du MEME BORD que le bras, sous lui.
    if (e.traverses.length) {
      const large = e.traverses.length > 1 ? d.boitier.l : 7;
      tetesDeTraverse(ctx, x + miroir(d.tete.x, large, e.bras), y + d.tete.y, large, e.inter, e.traverses);
    }
    B.stats.images++;
  }

  function dessinerFeuPieton(ctx, e, cx, cy) {
    const d = DECORS.feu_pieton;
    const poteau = Atlas.cuirePeintre('decor|feu_pieton', d.w, d.h, d.peindre);
    const x = Math.round(e.x - d.ancre[0] - cx), y = Math.round(e.y - d.ancre[1] - cy);
    ctx.drawImage(poteau, x, y);
    // ⚠️ LE RECOURS, et il sert rarement : une traverse dont aucun coin n'a de
    // mat a portee plante son propre poteau. Il est plus petit qu'une potence
    // et sa tete est CENTREE sur lui — c'est un poteau, pas un bras.
    const large = e.traverses.length > 1 ? 10 : d.w;
    tetesDeTraverse(ctx, x + ((d.w - large) >> 1), y, large, e.inter, e.traverses);
    B.stats.images++;
  }

  // --- Dessin --------------------------------------------------------------------------

  /** L'ombre au sol d'un char : ou elle tombe, quelle taille elle fait,
      comment elle est tournee et a quel point elle est noire.

      ⚠️ **Elle existe TOUT LE TEMPS, pas seulement en vol** — c'est le filet
      de la refonte des vehicules. Le jour ou le char sera dessine de profil,
      il ne montrera plus ses 28 px de longueur en s'eloignant : un objet de
      14 px de large, et son encombrement disparait de l'ecran. Or se garer
      dans une case, juger l'espace entre deux chars, reculer dans une ruelle,
      tout ca se joue A L'OEIL.

      ⚠️ Et elle a l'EMPREINTE DU CATALOGUE, la meme que la physique : ce qu'on
      voit est exactement ce qui bloque.

      ⚠️ Les nombres viennent de la fiche (`vehicules.OMBRE`) : ils etaient
      ecrits en dur ici, et une ombre qu'on ne peut pas regler depuis la fiche
      est un dessin qui decide de lui-meme comment la ville est eclairee.

      ⚠️ **LE SOL SE VOIT DE BIAIS** (`profondeur`) : un char debout ne montre
      plus sa longueur quand il roule vers le nord — son dessin fait 16 px de
      large et 11 px de haut — et l'ombre s'etalait sur les 28 px pleins de
      l'empreinte : une langue noire de quinze pixels devant lui, qu'on lisait
      comme une remorque. L'axe qui s'enfonce dans l'ecran est donc ECRASE, du
      meme biais que l'ombre d'un passant (`DECORS.ombre`, 12 x 6 pour un corps
      rond) — un seul biais pour toute la ville, et un juge tient les deux
      d'accord. L'empreinte en X ne bouge pas : c'est l'axe que le dessin
      montre. L'ecrasement est applique AU DESSIN (`dessinerUn`), apres la
      rotation : `l` et `h` restent l'empreinte du catalogue.

      ⚠️ Depuis la VUE PLONGEANTE, le dessin de dos ne fait plus 11 px de haut :
      il porte la longueur du char. L'ecrasement de l'ombre, lui, ne bouge pas —
      c'est le SOL qui se voit de biais, pas la caisse. Ce qui a change avec la
      vue plongeante, c'est ou le dessin se POSE (`solDeLaPose`).

      En montant, elle RETRECIT, elle S'ECHAPPE vers le sud-est (la lumiere
      vient du nord-ouest, comme pour les facades) et elle palit — c'est elle
      qui RACONTE la hauteur, et c'est pour ca qu'un saut se voit. Au sol, elle
      ne tombe QU'A L'EST : rien ne depasse devant les roues d'un char pose. */
  function ombreDe(v) {
    if (!v || !v.def) return null;
    const f = (B.defs.conduite && B.defs.conduite.ombre) || null;
    if (!f) return null;
    const z = Math.max(0, v.z || 0);
    const haut = Math.min(1, z / f.z_haut);              // 0 au sol, 1 tres haut
    const fuite = z * f.ecart_par_z;
    return {
      x: v.x + f.ecart_est + fuite, y: v.y + f.ecart_sud + fuite, angle: v.angle || 0,
      l: Math.max(4, Math.round(v.def.longueur * (1 - haut * f.retrait_max))),
      h: Math.max(3, Math.round(v.def.largeur * (1 - haut * f.retrait_max))),
      profondeur: f.profondeur,
      part: Math.max(0, f.part - haut * f.part_en_vol),
    };
  }

  //: ⚠️ UN SEUL OBJET, reutilise a chaque image : `faceDe` est appele pour
  //: chaque char visible, soixante fois par seconde. Un objet neuf par appel,
  //: c'est du ramassage de miettes pour rien.
  const _cap = { angle: 0, face: 'bas' };

  /** LE SENS OU IL REGARDE, en quatre faces. C'est la pose du CAVALIER, pas
      celle de la caisse : la machine, elle, tourne d'un cap continu (`capDe`).

      ⚠️ **LA MEME REGLE QUE LA FACE D'UN PASSANT, ET LE MEME CODE.** `regarder`
      porte deja le seuil (`Math.abs(dx) >= Math.abs(dy)`) ; deux jeux de
      seuils auraient fini par diverger, et celui qui est assis sur la moto
      aurait tourne la tete a un cap ou le passant a cote de lui ne tourne pas
      la sienne. */
  function faceDe(v) {
    Entites.regarder(_cap, Math.cos(v.angle), Math.sin(v.angle));
    return _cap.face;
  }

  /** LE CAP DESSINE : le cran (0 a ROTATIONS - 1) le plus proche de `v.angle`.

      ⚠️ **C'est ici que se joue « le char tourne comme son ombre »** (retour de
      Martin : « le pilotage des vehicules est vraiment impossible maintenant,
      il faut que le vehicule tourne vraiment comme l'ombre le fait »). Un char
      DEBOUT n'avait que quatre dessins — profil, dos, face — pour un cap
      continu : l'ombre pivotait sous lui a chaque image, le dessin attendait
      45 degres et CLAQUAIT. Au volant, on ne voyait plus ou on pointait, on le
      lisait sur l'ombre. Trente-deux crans, c'est moins de 6 degres d'ecart :
      le volant se voit.

      ⚠️ Le dessin de base pointe au NORD (`Atlas.toitDe`) et l'angle du moteur
      compte 0 a l'EST : d'ou le quart de tour. */
  function capDe(angle) {
    let i = Math.round((angle + Math.PI / 2) / (Math.PI * 2) * ROTATIONS) % ROTATIONS;
    if (i < 0) i += ROTATIONS;
    return i;
  }

  /** LE POINT AUTOUR DUQUEL LE DESSIN TOURNE, dans la grille du sprite.

      ⚠️ C'est le centre de l'EMPREINTE DU CATALOGUE, pas celui de la grille :
      l'ancre d'un sprite de char est sa ligne de sol (il reste deux rangees
      vides sous les roues), et tourner autour du milieu de la grille aurait
      fait tanguer le char d'un pixel a chaque cran. La meme empreinte que la
      physique et que l'ombre — ce qui tourne a l'ecran est exactement ce qui
      tourne dans la rue, et un char se gare toujours dans ses lignes. */
  function centreDuToit(v) {
    const def = SPRITES[v.sprite];
    return [def.ancre[0], def.ancre[1] + 1 - v.def.longueur / 2];
  }

  /** Les couleurs de celui qui est SUR le deux-roues — ou DANS la chaloupe —,
      ou null s'il n'y a personne : le joueur quand c'est lui, le pilote du
      trafic sinon. Une epave n'a personne dessus — il est tombe. ⚠️ C'est la
      `selle` de la fiche qui dit qu'on voit celui qui la mene, pas sa classe :
      un char ferme la cache, une coque la declare.

      ⚠️ Le pilote du trafic ne se peint que tant que le TRAFIC conduit. Un
      deux-roues que son pilote a quitte — le fuyard qui tombe de sa moto, un
      chemin de demain qui oublierait d'effacer `v.pilote` — n'a plus personne
      dessus, et c'est la seule ligne qui le garantit pour tous. */
  function cavalierDe(v) {
    const def = SPRITES[v.sprite];
    if (!def || !def.selle || v.etat === 'epave' || v.plie) return null;
    if (v.conducteur === B.joueur) return B.joueur.swaps || null;
    if (v.conducteur !== 'trafic') return null;
    return (v.pilote && v.pilote.swaps) || null;
  }

  /** Le passant assis sur ce deux-roues, et OU le poser.

      ⚠️ **Sa selle est un point de la MACHINE : elle tourne avec elle.** La
      fiche la donne depuis la ligne de sol du dessin vu d'en haut, donc a
      `longueur / 2 + dy` du centre, vers la queue. Posee sans tourner, elle
      laissait le cycliste assis au nord de son velo des qu'il roulait vers le
      sud.

      ⚠️ Sa POSE, elle, reste en quatre faces : c'est un corps, pas une
      carrosserie. Personne n'est dessine d'en haut dans Bandini — ni le
      joueur, ni les passants, ni celui qui pedale.

      ⚠️ Et c'est la pose qui ROULE, pas la pose assise : assis sur une chaise,
      il avait les fesses a la hauteur des moyeux, les mains sur les genoux et
      les pieds dans le vide. Les pedales tournent avec la distance roulee
      (`pedale` du sprite) ; sans pedales — la moto —, la premiere image. */
  function imageDuCavalier(def, v, swaps) {
    const cuit = Atlas.cuire('joueur', SPRITES.joueur, swaps);
    const face = faceDe(v);
    // ⚠️ La POSTURE est celle de la fiche : on ne mene pas une chaloupe comme on
    // enfourche une moto — assis au fond, la main a la barre (`posture`).
    const poses = cuit.poses[(def.posture || 'roule') + '_' + face] || cuit.poses['assis_' + face] || cuit.poses.assis_bas;
    if (!poses) return null;
    const image = def.pedale ? Math.floor((v.parcouru || 0) / def.pedale) % poses.length : 0;
    const selle = def.selle || [0, 0];
    const recul = v.def.longueur / 2 + selle[1];
    const ca = Math.cos(v.angle), sa = Math.sin(v.angle);
    // ⚠️ **ECRASE SUR L'AXE NORD-SUD, comme la machine** (`profondeur`) : le banc
    // de poupe est a 8 px du milieu de la coque, et pose sans le biais du sol,
    // le barreur vu de dos s'asseyait deux pixels derriere son banc.
    const K = (def.machine && def.machine.profondeur) || 1;
    return { canvas: poses[image],
             x: v.x - ca * recul - sa * selle[0] - cuit.ancre[0],
             y: v.y + (-sa * recul + ca * selle[0]) * K - cuit.ancre[1] };
  }

  //: Un battement de gyrophare, en images : un peu plus de quatre eclats par
  //: seconde de chaque couleur. ⚠️ Plus vite qu'un feu qui clignote
  //: (`clignotant_images`) : un gyrophare qui bat au rythme d'un feu jaune se
  //: lit comme un feu jaune.
  const GYROPHARE_IMAGES = 7;

  /** Les couleurs d'un char A CETTE IMAGE : les siennes, et ses gyrophares
      allumes en alternance quand ils tournent (`gyrophares` de la fiche).

      ⚠️ Un seul objet par phase, garde sur le char : l'atlas range ses cuissons
      par couleurs, et deux objets neufs a chaque image, c'est deux
      `JSON.stringify` pour rien — le canevas, lui, est deja cuit. */
  function swapsDuMoment(v, def) {
    const g = def.gyrophares;
    if (!g) return v.swaps;
    const tourne = g.quand === 'sirene' ? !!v.sirene : g.quand === 'remorque' ? !!v.remorque : false;
    if (!tourne) return v.swaps;
    if (!v.gyro || v.gyro.base !== v.swaps) {
      const phase = function (p) { return Object.assign({}, v.swaps, { a: g.a[p], b: g.b[1 - p] }); };
      v.gyro = { base: v.swaps, phases: [phase(0), phase(1)] };
    }
    return v.gyro.phases[Math.floor(B.t / GYROPHARE_IMAGES) % 2];
  }

  function dessinerUn(ctx, v, cx, cy) {
    const def = SPRITES[v.sprite];
    if (!def) return;
    // ⚠️ **LES FEUX DE DETRESSE** d'un char en panne : deux ambres qui battent
    // aux quatre coins de sa caisse. C'est tout ce qui le distingue d'un char
    // mal gare — et c'est exactement ce qu'on veut dire.
    if (v.panneT > 0 && Math.floor(B.t / trafic().panne.detresse_images) % 2 === 0) {
      const demi = v.def.longueur / 2, cote = v.def.largeur / 2;
      const ca = Math.cos(v.angle), sa = Math.sin(v.angle);
      ctx.fillStyle = '#ffb02e';
      for (const [dx, dy] of [[demi, cote], [demi, -cote], [-demi, cote], [-demi, -cote]]) {
        ctx.fillRect(Math.round(v.x + dx * ca - dy * sa - cx) - 1,
                     Math.round(v.y + dx * sa + dy * ca - v.z - cy) - 1, 2, 2);
      }
      B.stats.rects += 4;
    }
    const ombre = ombreDe(v);
    if (ombre) {
      // ⚠️ ORIENTEE COMME LE CHAR. Une tache alignee sur les axes ne dit rien
      // de la place qu'il prend : c'est justement l'encombrement qu'on rend a
      // l'oeil, et un autobus en travers de la rue n'a pas la meme empreinte
      // qu'un autobus dans sa voie.
      // ⚠️ ET ECRASEE SUR L'AXE NORD-SUD : le sol se voit de biais. L'ordre
      // compte — on ECRASE APRES avoir tourne (`scale` avant `rotate` dans la
      // pile, donc applique apres elle), sinon un char en diagonale verrait son
      // empreinte cisaillee au lieu d'etre posee a plat.
      ctx.save();
      ctx.translate(Math.round(ombre.x - cx), Math.round(ombre.y - cy));
      ctx.scale(1, ombre.profondeur);
      ctx.rotate(ombre.angle);
      ctx.fillStyle = 'rgba(0,0,0,' + ombre.part.toFixed(2) + ')';
      ctx.fillRect(-ombre.l / 2, -ombre.h / 2, ombre.l, ombre.h);
      ctx.restore();
      B.stats.rects++;
    }
    // ⚠️ **UN SEUL DESSIN, ET IL TOURNE** : le toit, cuit au cap le plus proche
    // et centre sur son empreinte — donc sur `v.x`, `v.y`, la ou l'ombre est
    // posee et la ou les cercles de collision sont. Ce qu'on voit tourner est
    // ce qui bloque.
    allumerLesPhares(v, cx, cy);
    const toit = Atlas.cuireCap(v.sprite, def, swapsDuMoment(v, def), ROTATIONS, capDe(v.angle), centreDuToit(v));
    const demi = toit.width / 2;
    ctx.drawImage(toit, Math.round(v.x - demi - cx), Math.round(v.y - v.z - demi - cy));
    B.stats.images++;
    // ⚠️ Et le cavalier PAR-DESSUS, toujours : vu d'en haut, celui qui est
    // assis sur la machine est au-dessus d'elle, quel que soit son cap.
    const swaps = cavalierDe(v);
    const cavalier = swaps ? imageDuCavalier(def, v, swaps) : null;
    if (cavalier) {
      ctx.drawImage(cavalier.canvas, Math.round(cavalier.x - cx), Math.round(cavalier.y - v.z - cy));
      B.stats.images++;
    }
  }

  return {
    ROTATIONS, courbeBraquage, vehiculeDef, creer, peupler, majGaresDeService, typeDeRue, cercles, bloqueParLesTuiles, chargeBloquee, decorDevant, heurterDecor, pousserLeDecor, degager, defoncerDevant, sirenes, aCrocher, basculerCrochet, decrocher,
    majPhysique, avancer, endommager, exploser, declencherAlarme,
    vehiculeSousLaMain, monter, descendre, ejecter,
    prochaineCible, peutSortir, obstacleDevant, majConducteur, commandesJoueur, rouler,
    pointDArret, approcheDeLaLigne, placeDeLaPanne, placeStationnee, garesVoulus,
    voieDeDepassement, voieLibre, changerDeVoie,
    estVeloDuTrafic, intentionDuVelo, coteDuVelo, aLaBordure, voieDuVelo, roulableHorsRue, boutDeTrottoir, traverseeDuParc, monterSurLeTrottoir,
    croisementLibre, creerSignalisation, pointeDuMoment, majNidDePoule, majPlaque, majTas, majPanne, majAmarrages, majMouillages, tuileInterdite, dessinerFeu, dessinerFeuPieton, lampesDesFeux, lampesDesPhares, maj, dessinerUn, swapsDuMoment, ombreDe, faceDe, capDe, centreDuToit, cavalierDe, imageDuCavalier,
    majTrace, dessinerTrace, bilanTrace, etatCourt,
  };
})();
