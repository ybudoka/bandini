/* Bandini — entites : une structure, un tableau, un tri par y.

   (x, y) est le point de contact au sol (les pieds). `r` est le rayon du
   cercle au sol pour les collisions. `z` est la hauteur (sauts, rampes) : y
   de tri = y, y de dessin = y - z.

   ⚠️ Tout ce qui bouge passe par le HACHAGE SPATIAL : chercher qui est a
   portee en parcourant les 300 entites de la carte coutait 300 tests par
   entite et par image. La grille de 64 px ramene ca a une poignee. Elle est
   REBATIE a chaque image plutot que tenue a jour : une entite qui bouge sans
   prevenir la grille est un bogue invisible, et 300 insertions ne coutent
   rien. */

const Entites = (function () {
  'use strict';

  const CELLULE = 64;
  //: Le monde vit dans une bulle autour du joueur : on peuple au-dela de
  //: l'ecran, on oublie plus loin encore. Entre les deux, personne n'apparait
  //: ni ne disparait sous les yeux du joueur.
  const BULLE_NAISSANCE = 300, BULLE_OUBLI = 520;
  const MAX_PIETONS = 22, MAX_PARTICULES = 300, MAX_DECALS = 150;
  //: Jusqu'ou chercher du decor solide autour de soi. ⚠️ La recherche est un
  //: CERCLE et l'empreinte une BOITE : il faut couvrir le coin de la boite la
  //: plus grosse, sinon le camion-restaurant n'est meme pas trouve et on lui
  //: passe au travers sans un seul test. Un juge refait le calcul sur chaque
  //: decor solide — ajouter un decor plus large sans monter ce chiffre tombe.
  const PORTEE_DECOR = 24;
  //: Se demeler de la foule : jusqu'ou chercher ses voisins (le plus gros
  //: rayon humain est 5 : 12 couvre large). Le pas, lui, se calcule — voir
  //: `pasDeDemele`, il depend de la vitesse des jambes les plus rapides.
  const RAYON_FOULE = 12;
  //: De combien on peut bousculer quelqu'un qui tient son poste avant qu'il
  //: devienne un mur. ⚠️ Assez pour qu'on se faufile (un corps fait 10 px de
  //: large), pas assez pour qu'on promene un donneur de mission a l'autre bout
  //: de la ville — au-dela, il ne cede plus, et il revient des qu'on le lache.
  const ECART_PLANTE = 10;

  let suivantId = 1;
  //: Deux index : le decor ne bouge JAMAIS (bati une fois, a la creation) et
  //: tout le reste est rebati a chaque image.
  //: ⚠️ Melanger les deux coutait 270 insertions par image — et surtout, un
  //: index vide hors de la boucle laissait traverser les arbres en silence.
  const grille = new Map();
  const grilleFixe = new Map();

  function cle(x, y) { return Math.floor(x / CELLULE) + ',' + Math.floor(y / CELLULE); }

  function ajouterA(index, e) {
    const k = cle(e.x, e.y);
    const liste = index.get(k);
    if (liste) liste.push(e); else index.set(k, [e]);
  }

  function creer(type, x, y, extra) {
    const e = {
      id: suivantId++, type: type, x: x, y: y, vx: 0, vy: 0, r: 5, z: 0, vz: 0,
      angle: 0, face: 'bas', etat: 'flane', t: 0,
      vie: 100, vieMax: 100, vivant: true,
      sprite: null, swaps: null, anim: { i: 0, dist: 0 },
      actif: true, dessine: true, solide: false,
      invincible: 0, recul: 0, saigne: 0, minuterie: 0, menace: null,
    };
    if (extra) Object.assign(e, extra);
    B.entites.push(e);
    return e;
  }

  function retirer(e) {
    const i = B.entites.indexOf(e);
    if (i >= 0) B.entites.splice(i, 1);
  }

  function vider() {
    B.entites.length = 0;
    B.particules.length = 0;
    B.decals.length = 0;
    B.joueur = null;
    grille.clear();
    grilleFixe.clear();
  }

  // --- Hachage spatial ------------------------------------------------------------

  function indexer() {
    grille.clear();
    for (const e of B.entites) {
      if (!e.actif || e.type === 'decor') continue;
      ajouterA(grille, e);
    }
  }

  /** Parcourt un index autour d'un point et rend ce qui passe le filtre. */
  function chercher(index, x, y, rayon, filtre) {
    const out = [];
    const c0x = Math.floor((x - rayon) / CELLULE), c1x = Math.floor((x + rayon) / CELLULE);
    const c0y = Math.floor((y - rayon) / CELLULE), c1y = Math.floor((y + rayon) / CELLULE);
    const r2 = rayon * rayon;
    for (let cy = c0y; cy <= c1y; cy++) {
      for (let cx = c0x; cx <= c1x; cx++) {
        const liste = index.get(cx + ',' + cy);
        if (!liste) continue;
        for (const e of liste) {
          if (dist2(e.x, e.y, x, y) > r2) continue;
          if (filtre && !filtre(e)) continue;
          out.push(e);
        }
      }
    }
    return out;
  }

  /** Ce qui BOUGE dans un rayon (px) : joueur, pietons, objets, projectiles. */
  function autour(x, y, rayon, filtre) { return chercher(grille, x, y, rayon, filtre); }

  /** Le decor solide dans un rayon — index fixe, donc jamais perime. */
  function decorAutour(x, y, rayon) { return chercher(grilleFixe, x, y, rayon, null); }

  function pietonsAutour(x, y, rayon) {
    return autour(x, y, rayon, function (e) { return e.type === 'pieton' && e.vivant; });
  }

  // --- Naissance ------------------------------------------------------------------

  function creerJoueur(x, y) {
    const p = B.partie;
    const j = creer('joueur', x, y, {
      r: 5, sprite: 'joueur', swaps: apparenceDuJoueur(p, B.defs),
      vie: p.vie, vieMax: 100, endurance: 100, cafeine: 0, arme: p.arme || 'poings',
      dansVehicule: null, flagrant: 0, pasDist: 0, coupT: 0, charge: 0, roule: 0,
    });
    B.joueur = j;
    return j;
  }

  function creerDecor(def) {
    grilleFixe.clear();
    (def.decor || []).forEach(function (d) {
      const fiche = DECORS[d.type] || {};
      const e = creer('decor', d.x * TT + 8, d.y * TT + 15, {
        decor: d.type, r: fiche.r === undefined ? 3 : fiche.r, solide: !!fiche.solide,
        dessine: true,
      });
      if (e.solide) ajouterA(grilleFixe, e);
    });
  }

  function archetype(slug) {
    const cat = B.defs.pietons.catalogue;
    for (const p of cat) if (p.slug === slug) return p;
    return cat[0];
  }

  /** Un passant au hasard, tire selon les poids du catalogue.

      ⚠️ Les passants de QUARTIER (`districts`) ne naissent que chez eux : un
      debardeur sur les quais, un banlieusard aux Erables. Sans cela les cinq
      districts sont le meme district repeint cinq fois. */
  function archetypeDeRue(x, y) {
    const zone = Monde.zoneA(x, y);
    const district = zone ? zone.district : null;
    const ordinaires = B.defs.pietons.catalogue.filter(function (p) {
      return p.frequence > 0 && !p.gang && (!p.districts || p.districts.indexOf(district) >= 0);
    });
    let tirage = B.rng() * ordinaires.reduce(function (s, p) { return s + p.frequence; }, 0);
    for (const p of ordinaires) {
      tirage -= p.frequence;
      if (tirage <= 0) return p;
    }
    return ordinaires[0];
  }

  function creerPieton(x, y, arch) {
    const p = arch || archetypeDeRue(x, y);
    const bourse = Math.round(p.argent[0] + B.rng() * (p.argent[1] - p.argent[0]));
    const e = creer('pieton', x, y, {
      r: p.sprite === 'enfant' ? 4 : 5, sprite: p.sprite || 'joueur', swaps: p.couleurs,
      arch: p.slug, gang: p.gang, metier: p.metier || null,
      vie: p.vie, vieMax: p.vie, allure: p.vitesse, courage: p.courage,
      probaTemoin: p.temoin, argent: bourse, arme: p.arme || null,
      intouchable: !!p.intouchable,
      etat: 'flane', dir: Math.floor(B.rng() * 4), butT: 0, cri: 0,
    });
    // ⚠️ Une fille de la Brume TIENT SON COIN : sans poste, elle se remettait
    // a flaner comme n'importe qui au bout de dix secondes, et le seul indice
    // qui restait etait sa robe. On reconnait d'abord celle qui ATTEND.
    if (p.metier === 'compagnie') e.poste = { x: x, y: y };
    // Une mere ne sort pas sans son petit : il la suit, et il detale avec elle.
    if (p.accompagne) {
      const petit = creerPieton(x + 10, y + 4, archetype(p.accompagne));
      petit.suit = e;
      e.petit = petit;
    }
    return e;
  }

  /** Les gens d'une piece : le commis a son poste, les clients qui flanent.

      ⚠️ Ils naissent a l'entree et meurent a la sortie — `B.entites` est
      remplace des deux cotes de la porte (`Jeu.entrer`/`Jeu.sortir`), alors il
      n'y a rien a nettoyer. Et `peupler()` ne tourne pas dedans : personne
      d'autre n'apparaîtra dans le dos du joueur pendant qu'il magasine.

      ⚠️ Le CLIENT est tire dans les passants ordinaires : dans une piece, la
      zone est vide, donc `archetypeDeRue` rend ceux de partout. C'est ce qui
      fait qu'on ne croise pas le meme figurant dans les vingt commerces. */
  function peuplerInterieur(piece) {
    if (!piece || !piece.gens) return;
    for (const g of piece.gens) {
      const arch = g.qui === 'commis' ? archetype('commis') : archetypeDeRue(g.x * TT, g.y * TT);
      if (!arch) continue;
      const e = creerPieton(g.x * TT + 8, g.y * TT + 8, arch);
      e.face = 'bas';
      // Le commis ne quitte pas sa caisse ; le client, lui, magasine.
      if (g.qui === 'commis') e.poste = { x: e.x, y: e.y };
    }
    indexer();
  }

  /** Rebatit l'index fixe a partir des entites presentes (retour de l'interieur). */
  function reindexerDecor() {
    grilleFixe.clear();
    for (const e of B.entites) if ((e.type === 'decor' || e.type === 'ambulant') && e.solide) ajouterA(grilleFixe, e);
  }

  /** Y a-t-il deja quelqu'un debout ici ? ⚠️ Les deux branches de
      `placeDeNaissance` rendent un CENTRE DE TUILE : deux naissances sur la
      meme tuile, c'est le meme pixel — deux corps parfaitement confondus
      (mesure : deux agents nes l'un dans l'autre a l'image 31, 10 px de
      chevauchement). La foule se demele bien toute seule ensuite, mais on ne
      devrait pas naitre a demeler. */
  function placeLibre(x, y) {
    return autour(x, y, 11, deboutDansLaFoule).length === 0;
  }

  /** Une tuile ou un pieton peut naitre : marchable, hors chaussee, hors ecran.
      Une fois sur trois, il SORT D'UNE PORTE — la ville a des dedans. */
  function placeDeNaissance() {
    const carte = Monde.carte;
    if (B.rng() < 0.34 && carte.portesFermees.length) {
      for (let essai = 0; essai < 8; essai++) {
        const porte = carte.portesFermees[Math.floor(B.rng() * carte.portesFermees.length)];
        const x = porte.x * TT + 8, y = (porte.y + 1) * TT + 8;
        if (dist2(x, y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI) continue;
        if (visibleAEcran(x, y, 24) || !Monde.marchablePieton(porte.x, porte.y + 1)) continue;
        if (!placeLibre(x, y)) continue;
        return { x: x, y: y };
      }
    }
    for (let essai = 0; essai < 24; essai++) {
      const angle = B.rng() * Math.PI * 2;
      const rayon = BULLE_NAISSANCE + B.rng() * (BULLE_OUBLI - BULLE_NAISSANCE - 60);
      const x = B.joueur.x + Math.cos(angle) * rayon;
      const y = B.joueur.y + Math.sin(angle) * rayon;
      const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
      if (tx < 1 || ty < 1 || tx >= carte.w - 1 || ty >= carte.h - 1) continue;
      if (Monde.solidite(tx, ty) !== 0 || Monde.estRoute(tx, ty)) continue;
      if (visibleAEcran(x, y, 24)) continue;
      if (!placeLibre(tx * TT + 8, ty * TT + 8)) continue;
      return { x: tx * TT + 8, y: ty * TT + 8 };
    }
    return null;
  }

  function visibleAEcran(x, y, marge) {
    const m = marge || 0;
    return x > B.cam.x - m && x < B.cam.x + VW + m && y > B.cam.y - m && y < B.cam.y + VH + m;
  }

  /** Au premier instant d'une partie, la rue est deja vivante : on peuple
      AUSSI l'ecran, une seule fois — personne ne voit apparaitre qui que ce
      soit, le voile du titre n'est pas encore tombe. */
  function peuplerDabord() {
    const zone = Monde.zoneA(B.joueur.x, B.joueur.y);
    const voulu = Math.min(MAX_PIETONS, (zone ? zone.pietons : 12) * Monde.rythme(zone)) * 0.6;
    // ⚠️ L'index d'abord, et tenu a jour a chaque naissance : sans lui
    // `placeLibre` ne voit personne, et la foule de depart nait empilee sur
    // quelques tuiles (elle se demele ensuite, mais on la voit le faire).
    indexer();
    for (let essai = 0; essai < 80 && B.entites.filter(function (e) { return e.type === 'pieton' && !e.metier; }).length < voulu; essai++) {
      const a = B.rng() * Math.PI * 2, d = 40 + B.rng() * 260;
      const tx = Math.floor((B.joueur.x + Math.cos(a) * d) / TT), ty = Math.floor((B.joueur.y + Math.sin(a) * d) / TT);
      if (!Monde.marchablePieton(tx, ty) || Monde.estPassage(tx, ty)) continue;
      if (!placeLibre(tx * TT + 8, ty * TT + 8)) continue;
      ajouterA(grille, creerPieton(tx * TT + 8, ty * TT + 8, null));
    }
    indexer();
  }

  /** Garde la rue peuplee : on nait hors champ, on s'oublie hors de la bulle. */
  function peupler() {
    let vivants = 0;
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const e = B.entites[i];
      if (e.type !== 'pieton') continue;
      const loin = dist2(e.x, e.y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI;
      // Les personnages de l'histoire et les figurants d'une mission ne s'oublient pas : ils attendent.
      if (loin && !e.personnage && !e.mission && !visibleAEcran(e.x, e.y, 40)) { retirer(e); continue; }
      if (e.vivant && !e.metier) vivants++;
    }
    const zone = Monde.zoneA(B.joueur.x, B.joueur.y);
    const voulu = Math.min(MAX_PIETONS, (zone ? zone.pietons : 12) * Monde.rythme(zone));
    if (vivants >= voulu || B.t % 12 !== 0) return;
    const place = placeDeNaissance();
    if (!place) return;
    // La nuit, pres du bar et du port, la Brume a ses habituees.
    const nuit = Monde.estNuit();
    if (nuit && zone && zone.brume && B.rng() < 0.18) {
      const fille = archetype('racoleuse');
      if (fille) {
        const e = creerPieton(place.x, place.y, fille);
        e.etat = 'arret';
        e.minuterie = 600;
        return;
      }
    }
    // Sur le territoire d'une gang, ce sont ses membres qui trainent dehors.
    const gang = zone && zone.gang && !(B.partie && B.partie.faubourgLibere) && B.rng() < 0.5
      ? (B.defs.pietons.gangs.find(function (g) { return g.slug === zone.gang; }) || null)
      : null;
    creerPieton(place.x, place.y, gang ? archetype(gang.pieton) : null);
  }

  /** Les paquets caches qu'on n'a pas encore ramasses. */
  function creerPaquets(def) {
    (def.paquets || []).forEach(function (q) {
      if (B.partie.paquets[q.numero]) return;
      creer('paquet', q.x * TT + 8, q.y * TT + 12, { numero: q.numero, r: 4, solide: false, decor: 'paquet', dessine: true });
    });
  }

  /** Les kiosques et les camions de la carte, avec quelqu'un derriere. */
  function creerAmbulants(def) {
    (def.ambulants || []).forEach(function (a) {
      const commerce = (B.defs.ambulants || []).find(function (c) { return c.slug === a.slug; });
      if (!commerce) return;
      const fiche = DECORS[commerce.sprite] || {};
      creer('ambulant', a.x * TT + 8, a.y * TT + 15, {
        decor: commerce.sprite, slug: a.slug, r: fiche.r === undefined ? 10 : fiche.r,
        solide: true, dessine: true,
      });
      ajouterA(grilleFixe, B.entites[B.entites.length - 1]);
      const vendeur = creerPieton(a.x * TT + 8, a.y * TT + 4, archetype('vendeur'));
      vendeur.etat = 'fige';
      vendeur.face = 'bas';
      vendeur.commerce = a.slug;
    });
  }

  /** Des armes de fortune trainent partout : un cone de chantier, une
      bouteille, une pelle. C'est ce qui permet de se battre sans rien acheter
      — et elles cassent au bout de quelques coups. */
  function semerDesArmesDeFortune() {
    if (B.t % 90 !== 0) return;
    let trainent = 0;
    for (const e of B.entites) if (e.type === 'ramassage' && e.fortune) trainent++;
    if (trainent >= 3) return;
    const fortunes = B.defs.armes.filter(function (a) { return a.usures > 0 && a.prix === 0; });
    if (!fortunes.length) return;
    const place = placeDeNaissance();
    if (!place) return;
    const arme = fortunes[Math.floor(B.rng() * fortunes.length)];
    creer('ramassage', place.x, place.y, {
      r: 4, objet: 'arme', arme: arme.slug, munitions: arme.chargeur, fortune: true, t: 0,
    });
  }

  // --- Deplacement avec collisions --------------------------------------------------

  /** Deplace un cercle (approche par boite) contre les tuiles, axe par axe. */
  function deplacerCercle(e, dx, dy, masque) {
    const r = e.r;
    if (dx !== 0) {
      e.x += dx;
      const ty0 = Math.floor((e.y - r) / TT), ty1 = Math.floor((e.y + r - 0.01) / TT);
      if (dx > 0) {
        const tx = Math.floor((e.x + r) / TT);
        for (let ty = ty0; ty <= ty1; ty++) if (Monde.bloque(tx, ty, masque)) { e.x = tx * TT - r - 0.01; break; }
      } else {
        const tx = Math.floor((e.x - r) / TT);
        for (let ty = ty0; ty <= ty1; ty++) if (Monde.bloque(tx, ty, masque)) { e.x = (tx + 1) * TT + r + 0.01; break; }
      }
    }
    if (dy !== 0) {
      e.y += dy;
      const tx0 = Math.floor((e.x - e.r) / TT), tx1 = Math.floor((e.x + e.r - 0.01) / TT);
      if (dy > 0) {
        const ty = Math.floor((e.y + r) / TT);
        for (let tx = tx0; tx <= tx1; tx++) if (Monde.bloque(tx, ty, masque)) { e.y = ty * TT - r - 0.01; break; }
      } else {
        const ty = Math.floor((e.y - r) / TT);
        for (let tx = tx0; tx <= tx1; tx++) if (Monde.bloque(tx, ty, masque)) { e.y = (ty + 1) * TT + r + 0.01; break; }
      }
    }
    bloquerParDecor(e);
  }

  function bloquerParDecor(e) {
    for (const d of decorAutour(e.x, e.y, e.r + PORTEE_DECOR)) {
      if (d === e) continue;
      const fiche = DECORS[d.decor];
      const dx = e.x - d.x, dy = e.y - d.y;
      const sol = fiche && fiche.sol;
      if (sol) {
        // Une boite : on ressort par le cote le moins enfonce (voir DECORS).
        const px = sol[0] + e.r - Math.abs(dx), py = sol[1] + e.r - Math.abs(dy);
        if (px <= 0 || py <= 0) continue;
        if (px < py) e.x = d.x + (dx < 0 ? -1 : 1) * (sol[0] + e.r);
        else e.y = d.y + (dy < 0 ? -1 : 1) * (sol[1] + e.r);
        continue;
      }
      const min = e.r + d.r;
      const d2 = dx * dx + dy * dy;
      if (d2 >= min * min || d2 === 0) continue;
      const dist = Math.sqrt(d2);
      e.x = d.x + dx / dist * min;
      e.y = d.y + dy / dist * min;
    }
  }

  // --- La foule ne se traverse pas -------------------------------------------------

  /** Debout dans la foule : ni mort, ni assomme, ni au volant. ⚠️ On marche
      SUR un cadavre — c'est deja la regle du tri au dessin — alors un corps a
      terre ne pousse personne et ne se fait pousser par personne. */
  function deboutDansLaFoule(e) {
    return e.actif && e.vivant && !e.dansVehicule && e.etat !== 'assomme'
      && (e.type === 'pieton' || e.type === 'joueur');
  }

  /** De combien on se degage par image. ⚠️ Ce plafond doit passer DEVANT les
      jambes les plus rapides du jeu, sinon il se retourne contre lui-meme :
      fixe a 1,5 px, il arretait bien le joueur qui MARCHE (1,2 px/image) et
      laissait passer celui qui SPRINTE (2,1) — courir devenait un moyen de
      traverser les gens, et on entrait dans le vendeur en tenant MAJ. */
  function pasDeDemele() {
    const v = B.defs.recherche.vitesses;
    return Math.max(v.joueur_sprint, v.policier, v.pieton_course) + 0.4;
  }

  /** Se laisse-t-il pousser ? Tout le monde, sauf celui qui tient un poste et
      s'en trouve deja trop loin : passe ECART_PLANTE, il devient un mur — sans
      quoi on pourrait promener un personnage d'histoire jusqu'au port. */
  function cede(e) {
    if (e.etat !== 'fige') return true;
    if (!e.plante) return true;
    return dist2(e.x, e.y, e.plante.x, e.plante.y) < ECART_PLANTE * ECART_PLANTE;
  }

  /** ⚠️ Personne ne traverse personne. Sans cette passe, deux passants qui se
      croisent se superposent EXACTEMENT : on voit une tete a quatre bras, et
      une foule tient sur une tuile. Mesure avant correctif, en marchant deux
      minutes dans la ville : 1032 paires enfoncees l'une dans l'autre en 960
      images, jusqu'a 9,9 px — deux corps de 10 px parfaitement confondus.

      ⚠️ On POUSSE, on ne teleporte pas : la separation est plafonnee a
      `pasDeDemele()` px par image. Deux passants nes au meme endroit se
      degagent alors en glissant, comme une foule le fait, au lieu de se
      detacher d'un coup. Et la poussee passe par `deplacerCercle` : sinon on
      se pousse mutuellement DANS un mur, ce qui est pire que se chevaucher.

      ⚠️ Celui qui tient un poste (le vendeur, le donneur devant sa porte) se
      laisse bousculer de quelques pixels et rentre chez lui tout seul — voir
      `cede` et la branche `fige` de majPieton. */
  function demeler() {
    const gens = [];
    for (const e of B.entites) if (deboutDansLaFoule(e)) gens.push(e);
    for (const e of gens) { e.pousseX = 0; e.pousseY = 0; }
    for (const e of gens) {
      for (const autre of autour(e.x, e.y, e.r + RAYON_FOULE, deboutDansLaFoule)) {
        // ⚠️ Une paire, une fois — mais le tour de TOUT LE MONDE, fige compris :
        // en sautant le fige ici, la moitie des paires (celles ou son id vient
        // en premier) n'etait jamais examinee, et on entrait dans le vendeur.
        if (autre.id <= e.id) continue;
        const min = e.r + autre.r;
        let dx = e.x - autre.x, dy = e.y - autre.y;
        let d = Math.hypot(dx, dy);
        if (d >= min) continue;
        if (d < 0.001) {
          // Pile l'un sur l'autre : il faut choisir un sens, et toujours le
          // meme — le banc est un juge, il ne tire pas a pile ou face.
          dx = ((e.id + autre.id) % 2) ? 1 : 0; dy = 1 - dx; d = 1;
        }
        // Chacun sa moitie ; celui qui ne bougera pas laisse la sienne a l'autre.
        const chevauche = min - d;
        const pourE = cede(autre) ? chevauche / 2 : chevauche;
        const pourAutre = cede(e) ? chevauche / 2 : chevauche;
        e.pousseX += dx / d * pourE; e.pousseY += dy / d * pourE;
        autre.pousseX -= dx / d * pourAutre; autre.pousseY -= dy / d * pourAutre;
      }
    }
    const pas = pasDeDemele();
    for (const e of gens) {
      if (!cede(e) || (e.pousseX === 0 && e.pousseY === 0)) continue;
      const n = Math.hypot(e.pousseX, e.pousseY);
      const k = n > pas ? pas / n : 1;
      deplacerCercle(e, e.pousseX * k, e.pousseY * k, Monde.MASQUE_PIETON);
      dansLaCarte(e);
    }
  }

  // --- Enjamber une cloture ------------------------------------------------------------

  /*: Enjamber, c'est une capacite de TOUT LE MONDE — le joueur, un agent, un
    gardien. ⚠️ Si le grillage n'etait un cout que pour le joueur, la premiere
    cloture venue deviendrait l'exploit qui gagne toutes les poursuites : on
    enjambe, et les agents restent plantes de l'autre cote. Le prix est donc un
    seul chiffre, en donnees (`recherche.clotures`), lu ici comme par l'A*. */
  function reglesCloture() {
    return (B.defs && B.defs.recherche && B.defs.recherche.clotures)
      || { enjambe_images: 48, cout_chemin_tuiles: 5, hauteur_px: 5 };
  }

  /** La cloture qu'on pousse, dans le sens du mouvement, et ou l'on retombe —
      ou null s'il n'y a rien a enjamber (ou rien derriere).

      ⚠️ UN SEUL axe, le dominant : une enjambee en diagonale retomberait entre
      deux tuiles, et le corps finirait dans le coin d'un mur. */
  function clotureDevant(e, dx, dy) {
    if (!dx && !dy) return null;
    const sx = Math.abs(dx) >= Math.abs(dy) ? Math.sign(dx) : 0;
    const sy = sx === 0 ? Math.sign(dy) : 0;
    const tx = Math.floor((e.x + sx * (e.r + 2)) / TT), ty = Math.floor((e.y + sy * (e.r + 2)) / TT);
    if (!Monde.estEnjambable(tx, ty)) return null;
    // Derriere la cloture : une tuile ou l'on peut retomber. Deux grillages
    // colles ne s'enjambent pas d'un coup — on en franchit un, puis l'autre.
    const ax = tx + sx, ay = ty + sy;
    if (Monde.bloque(ax, ay, Monde.MASQUE_PIETON)) return null;
    return { sx: sx, sy: sy, tx: tx, ty: ty, ax: ax, ay: ay };
  }

  /** Commence l'enjambee si une cloture est devant. Rend true si elle commence. */
  function enjamber(e, dx, dy) {
    if (e.enjambe || e.dansVehicule || !e.vivant) return false;
    const c = clotureDevant(e, dx, dy);
    if (!c) return false;
    const regles = reglesCloture();
    // ⚠️ La retombee est CENTREE sur la tuile d'arrivee dans l'axe traverse, et
    // bornee dans l'autre : sans ca, un corps qui chevauche deux tuiles de
    // travers retombe a moitie dans le mur d'a cote.
    const cx = c.ax * TT + 8, cy = c.ay * TT + 8;
    const marge = TT / 2 - e.r - 0.01;
    const x1 = c.sx ? cx : borner(e.x, cx - marge, cx + marge);
    const y1 = c.sy ? cy : borner(e.y, cy - marge, cy + marge);
    e.enjambe = { t: 0, duree: regles.enjambe_images, haut: regles.hauteur_px,
                  x0: e.x, y0: e.y, x1: x1, y1: y1 };
    e.vx = 0; e.vy = 0;
    e.charge = 0;
    if (e.etat === 'attaque') { e.etat = 'flane'; e.phase = null; }
    regarder(e, c.sx, c.sy);
    Son.SFX.pas();
    return true;
  }

  /** Avance l'enjambee. Rend true tant qu'elle dure : l'appelant ne fait RIEN
      d'autre cette image-la — on est immobile en haut d'une cloture, et c'est
      exactement ce qui fait le prix d'un raccourci. */
  function majEnjambe(e) {
    const en = e.enjambe;
    if (!en) return false;
    en.t++;
    const part = Math.min(1, en.t / en.duree);
    e.x = en.x0 + (en.x1 - en.x0) * part;
    e.y = en.y0 + (en.y1 - en.y0) * part;
    // Une cloche : on monte, on passe, on redescend. C'est le seul signe visible
    // que le corps est EN HAUT de quelque chose.
    e.z = Math.round(Math.sin(part * Math.PI) * en.haut);
    e.vx = 0; e.vy = 0;
    if (part >= 1) { e.enjambe = null; e.z = 0; Son.SFX.pas(); }
    return true;
  }

  function dansLaCarte(e) {
    const c = Monde.carte;
    e.x = borner(e.x, e.r, c.pxW - e.r);
    e.y = borner(e.y, e.r, c.pxH - e.r);
  }

  function regarder(e, dx, dy) {
    if (dx === 0 && dy === 0) return;
    e.angle = Math.atan2(dy, dx);
    e.face = Math.abs(dx) >= Math.abs(dy) ? (dx > 0 ? 'droite' : 'gauche') : (dy > 0 ? 'bas' : 'haut');
  }

  // --- Joueur ---------------------------------------------------------------------------

  function majJoueur(j) {
    if (j.dansVehicule) return;
    if (majEnjambe(j)) return;                        // en haut d'une cloture : rien d'autre
    if (B.cinema) { j.vx = 0; j.vy = 0; return; }     // quelqu'un lui parle : il ecoute
    const v = B.defs.recherche.vitesses;
    const axe = Entree.axe;
    if (j.roule > 0) {                       // roulade : on ne se dirige plus
      j.roule--;
      deplacerCercle(j, j.vx, j.vy, Monde.MASQUE_PIETON);
      dansLaCarte(j);
      if (j.roule === 0) j.invincible = 6;
      return;
    }
    const veutCourir = Entree.bas('esquive') || (axe.source !== 'clavier' && axe.mag > 0.85);
    let vitesse = v.joueur_marche;
    // ⚠️ Le cafe allonge la course, il ne l'accelere PAS : `joueur_sprint`
    // reste ce qu'il est (2,1 contre 1,9 au policier), seule la DEPENSE baisse.
    // La minuterie, elle, s'ecoule dans `Missions.maj` — meme au volant.
    const cafe = j.cafeine > 0 ? B.defs.economie.cafe.depense : 1;
    if (veutCourir && axe.mag > 0 && j.endurance > 0) {
      vitesse = v.joueur_sprint;
      j.endurance = Math.max(0, j.endurance - v.endurance_par_image * cafe);
    } else {
      j.endurance = Math.min(v.endurance, j.endurance + v.endurance_par_image * 0.6);
    }
    if (j.etat === 'attaque') vitesse *= 0.45;    // on frappe en marchant, pas en courant
    const mag = axe.source === 'clavier' ? axe.mag : Math.min(1, axe.mag * 1.15);
    j.vx = axe.x * vitesse * mag;
    j.vy = axe.y * vitesse * mag;
    if (axe.mag > 0) regarder(j, axe.x, axe.y);
    // Pousser contre un grillage, c'est vouloir l'enjamber : une seconde en
    // haut, sans frapper, sans tirer, sans courir — et une cible immobile.
    if (axe.mag > 0 && enjamber(j, j.vx, j.vy)) { Hud.message('PAR-DESSUS'); return; }
    const avant = { x: j.x, y: j.y };
    deplacerCercle(j, j.vx, j.vy, Monde.MASQUE_PIETON);
    dansLaCarte(j);
    const d = Math.hypot(j.x - avant.x, j.y - avant.y);
    j.anim.dist += d;
    j.pasDist += d;
    if (j.pasDist > 14) { j.pasDist = 0; Son.SFX.pas(); }
    if (j.invincible > 0) j.invincible--;
    if (j.flagrant > 0) j.flagrant--;
    if (j.saigne > 0) saigner(j);
  }

  // --- Pietons --------------------------------------------------------------------------

  const DIRECTIONS = [[1, 0], [0, 1], [-1, 0], [0, -1]];

  // Jusqu'ou une fille de la Brume s'ecarte du coin qu'elle tient (3 tuiles).
  const POSTE_RAYON = 48;

  /** L'indice de DIRECTIONS le plus proche d'un vecteur. */
  function directionVers(dx, dy) {
    if (Math.abs(dx) > Math.abs(dy)) return dx > 0 ? 0 : 2;
    return dy > 0 ? 1 : 3;
  }

  function majPieton(e) {
    const v = B.defs.recherche.vitesses;
    const reactions = B.defs.pietons.reactions;
    if (!e.vivant) { if (e.saigne > 0) e.saigne--; return; }
    if (e.saigne > 0) saigner(e);
    if (majEnjambe(e)) return;         // il passe par-dessus une cloture : rien d'autre

    if (e.etat === 'fige') {
      // ⚠️ Fige veut dire « il tient son poste », pas « c'est un poteau ». Un
      // donneur vraiment immobile bouche la rue POUR TOUJOURS : l'agent lance
      // aux trousses du joueur venait buter sur Ti-Guy et y restait — 260
      // images sur place, l'arrestation n'arrivait jamais. On se laisse donc
      // bousculer de quelques pixels (voir ECART_PLANTE), et on rentre.
      if (!e.plante) e.plante = { x: e.x, y: e.y };
      const dx = e.plante.x - e.x, dy = e.plante.y - e.y;
      const loin = Math.hypot(dx, dy);
      if (loin > 0.3) {
        const pas = Math.min(loin, v.pieton);
        deplacerCercle(e, dx / loin * pas, dy / loin * pas, Monde.MASQUE_PIETON);
      }
      e.vx = 0; e.vy = 0;
      return;
    }
    if (e.agent && Police.gere(e)) return;               // il poursuit, il enquete : la police le dirige
    // Le petit colle a sa mere : il ne flane jamais tout seul.
    if (e.suit && e.suit.vivant && e.etat !== 'fuit') {
      const ecart = B.defs.pietons.reactions.suite_distance_px;
      const dx = e.suit.x - e.x, dy = e.suit.y - e.y;
      const norme = Math.hypot(dx, dy);
      if (norme > ecart) {
        const vitesse = Math.min(v.pieton_course, v.pieton * e.allure * 1.6);
        e.vx = dx / norme * vitesse;
        e.vy = dy / norme * vitesse;
      } else { e.vx = 0; e.vy = 0; }
      deplacerCercle(e, e.vx, e.vy, Monde.MASQUE_PIETON);
      dansLaCarte(e);
      e.anim.dist += Math.abs(e.vx) + Math.abs(e.vy);
      regarder(e, e.vx, e.vy);
      return;
    }
    if (e.etat === 'assomme') {
      if (--e.minuterie <= 0) { e.etat = 'fuit'; e.minuterie = reactions.fuite_secondes * 60; e.face = 'bas'; }
      return;
    }
    if (e.recul > 0) {
      e.recul--;
      deplacerCercle(e, e.vx, e.vy, Monde.MASQUE_PIETON);
      e.vx *= 0.82; e.vy *= 0.82;
      dansLaCarte(e);
      return;
    }

    let vitesse = v.pieton * e.allure;
    if (e.etat === 'temoin' && e.vers && e.vers.vivant) {
      // Le temoin court VERS l'agent qu'il a repere, pour lui raconter.
      vitesse = v.pieton_course * e.allure;
      if (--e.minuterie <= 0) { e.etat = 'flane'; e.cri = 0; e.vers = null; }
      const dx = e.vers.x - e.x, dy = e.vers.y - e.y;
      const norme = Math.hypot(dx, dy) || 1;
      e.vx = dx / norme * vitesse;
      e.vy = dy / norme * vitesse;
    } else if (e.etat === 'fuit' || e.etat === 'temoin') {
      vitesse = v.pieton_course * e.allure;
      if (--e.minuterie <= 0) { e.etat = 'flane'; e.cri = 0; }
      const menace = e.menace || B.joueur;
      const dx = e.x - menace.x, dy = e.y - menace.y;
      const norme = Math.hypot(dx, dy) || 1;
      e.vx = dx / norme * vitesse;
      e.vy = dy / norme * vitesse;
    } else if (e.etat === 'attaque_joueur') {
      vitesse = v.pieton_course * e.allure;
      const dx = B.joueur.x - e.x, dy = B.joueur.y - e.y;
      const norme = Math.hypot(dx, dy) || 1;
      if (norme > 260) { e.etat = 'flane'; }
      e.vx = dx / norme * vitesse;
      e.vy = dy / norme * vitesse;
      if (norme < 18 && e.t % 40 === 0) Combat.frapper(e);
    } else if (e.etat === 'arret') {
      // On s'arrete : on regarde une vitrine, on attend quelqu'un, on respire.
      e.vx = 0; e.vy = 0;
      if (--e.minuterie <= 0) e.etat = 'flane';
      return;
    } else if (e.etat === 'entre') {
      // Il rentre chez lui : un pas vers la porte, et il n'est plus la.
      e.vx = 0; e.vy = -vitesse;
      if (--e.minuterie <= 0) { retirer(e); return; }
    } else {
      // Un Cravate sur son territoire : le joueur arme au poing, c'est une provocation.
      if (e.gang && !e.cible && B.joueur.arme !== 'poings' && !B.joueur.dansVehicule && e.t % 15 === 0
          && dist2(e.x, e.y, B.joueur.x, B.joueur.y) < (6 * TT) * (6 * TT) && Monde.ligneLibre(e.x, e.y, B.joueur.x, B.joueur.y)) {
        const zone = Monde.zoneA(e.x, e.y);
        if (zone && zone.gang === e.gang) { e.etat = 'attaque_joueur'; e.cri = 90; }
      }
      // Flaner : on suit une direction jusqu'a ce qu'elle ne mene plus nulle part.
      const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
      if (Monde.estChaussee(tx, ty)) {
        // Pousse sur la chaussee (par un char) : on regagne le trottoir le plus proche.
        const refuge = trottoirLePlusProche(tx, ty);
        if (refuge) {
          const dx = refuge.x - e.x, dy = refuge.y - e.y, n = Math.hypot(dx, dy) || 1;
          e.vx = dx / n * v.pieton_course; e.vy = dy / n * v.pieton_course;
        }
      } else {
        if (e.butT-- <= 0) {
          // Celle qui tient un poste (la Brume) s'arrete deux fois plus
          // souvent, et repart vers son lampadaire des qu'elle s'en eloigne.
          const rentre = e.poste && dist2(e.x, e.y, e.poste.x, e.poste.y) > POSTE_RAYON * POSTE_RAYON;
          if (!rentre && B.rng() < (e.poste ? 0.65 : 0.3)) {
            e.etat = 'arret';
            e.minuterie = 50 + Math.floor(B.rng() * 160);
            e.butT = e.poste ? 30 : 90;
            e.vx = 0; e.vy = 0;
            return;
          }
          // Une porte juste au nord ? Une fois sur douze, on rentre.
          const g = Monde.glyphe(tx, ty - 1);
          if ((g === 'd' || g === 'D') && !e.metier && !e.suit && !e.petit && B.rng() < 0.08) {
            e.etat = 'entre'; e.minuterie = 40; e.face = 'haut';
            return;
          }
          e.dir = rentre ? directionVers(e.poste.x - e.x, e.poste.y - e.y) : Math.floor(B.rng() * 4);
          // ⚠️ Celle qui tient un poste redecide vite : une flanerie de 330
          // images l'emmenait a l'autre bout de la rue avant qu'elle songe
          // seulement a revenir.
          e.butT = e.poste ? 30 : 90 + Math.floor(B.rng() * 240);
        }
        const dir = DIRECTIONS[e.dir];
        // ⚠️ La regle de la ville : on ne pose pas le pied sur la chaussee.
        // On traverse au passage, et seulement quand c'est sur.
        const ax = Math.floor((e.x + dir[0] * (e.r + 4)) / TT), ay = Math.floor((e.y + dir[1] * (e.r + 4)) / TT);
        if (Monde.estChaussee(ax, ay) || Monde.bloque(ax, ay, Monde.MASQUE_PIETON)) {
          e.dir = (e.dir + (B.rng() < 0.5 ? 1 : 3)) % 4;      // on tourne, on ne fonce pas
          e.butT = e.poste ? 30 : 60 + Math.floor(B.rng() * 120);
          e.vx = 0; e.vy = 0;
          return;
        }
        if (Monde.estPassage(ax, ay) && !Monde.estPassage(tx, ty) && !traverseeSure(ax, ay, dir)) {
          e.vx = 0; e.vy = 0;                                   // on attend au bord
          e.anim.dist = 0;
          return;
        }
        e.vx = dir[0] * vitesse;
        e.vy = dir[1] * vitesse;
      }
    }
    const avant = { x: e.x, y: e.y };
    deplacerCercle(e, e.vx, e.vy, Monde.MASQUE_PIETON);
    dansLaCarte(e);
    const bouge = Math.hypot(e.x - avant.x, e.y - avant.y);
    e.anim.dist += bouge;
    if (bouge < 0.2 && e.etat === 'flane') e.butT = 0;      // bloque : on change d'idee
    else if (bouge < 0.2) { e.dir = Math.floor(B.rng() * 4); e.vx = 0; e.vy = 0; }
    regarder(e, e.vx, e.vy);
    if (e.cri > 0) e.cri--;
  }

  /** La tuile de trottoir (ou d'herbe) la plus proche, en pixels. */
  function trottoirLePlusProche(tx, ty) {
    for (let r = 1; r <= 4; r++) {
      for (let dy = -r; dy <= r; dy++) {
        for (let dx = -r; dx <= r; dx++) {
          if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
          if (Monde.marchablePieton(tx + dx, ty + dy)) return { x: (tx + dx) * TT + 8, y: (ty + dy) * TT + 8 };
        }
      }
    }
    return null;
  }

  /** Peut-on s'engager sur ce passage ? Au feu : quand les chars de cette rue
      sont au rouge. Sans feu : quand aucun char n'approche. */
  function traverseeSure(tx, ty, dir) {
    const inter = Monde.intersectionA(tx, ty);
    // Le passage « = » barre une rue est-ouest : les chars y roulent en > <.
    const sensChars = Monde.glyphe(tx, ty) === '=' ? '>' : '^';
    if (inter && inter.feux) return !Monde.feuVert(inter, sensChars);
    const portee = B.defs.conduite.trafic.priorite_pieton_px;
    return autour(tx * TT + 8, ty * TT + 8, portee, function (q) {
      return q.type === 'vehicule' && q.etat !== 'epave' && Math.abs(q.vitesse) > 0.2;
    }).length === 0;
  }

  /** Un coup, une chute, un cri : qui voit ca prend peur (ou s'approche). */
  function alerter(x, y, menace, gravite) {
    const reactions = B.defs.pietons.reactions;
    // Un enfant prend peur de bien plus loin que les grandes personnes.
    const rayonMax = Math.max(reactions.peur_rayon_tuiles, reactions.enfant_peur_tuiles) * TT;
    const recent = B.crimes.length ? B.crimes[B.crimes.length - 1] : null;
    const crime = recent && B.t - recent.t <= 1 ? recent : null;   // le crime qu'on vient de signaler
    for (const e of pietonsAutour(x, y, rayonMax)) {
      const rayon = (e.intouchable ? reactions.enfant_peur_tuiles : reactions.peur_rayon_tuiles) * TT;
      if (dist2(e.x, e.y, x, y) > rayon * rayon) continue;
      if (e === menace || e.etat === 'assomme' || e.agent) continue;   // l'agent ne fuit pas : la police le dirige
      if (!Monde.ligneLibre(e.x, e.y, x, y)) continue;
      if (e.intouchable) {                       // l'enfant ne fait que detaler
        e.etat = 'fuit'; e.menace = menace; e.minuterie = reactions.fuite_secondes * 90; e.cri = 120;
        continue;
      }
      if (e.gang && gravite >= 1) { e.etat = 'attaque_joueur'; e.cri = 90; continue; }
      if (e.courage > 0 && B.rng() < e.courage * 0.5 && gravite >= 2) {
        e.etat = 'attaque_joueur'; e.cri = 90; continue;
      }
      if (e.etat !== 'fuit' && e.etat !== 'temoin') {
        e.etat = B.rng() < e.probaTemoin ? 'temoin' : 'fuit';
        if (e.etat === 'temoin' && crime && !e.crime) e.crime = crime;   // il a quelque chose a raconter
        e.menace = menace;
        e.minuterie = reactions.fuite_secondes * 60;
        e.cri = 120;
      }
    }
  }

  function saigner(e) {
    const reactions = B.defs.pietons.reactions;
    e.saigne--;
    if (e.saigne % 60 === 0) {
      e.vie -= reactions.degats_saignement;
      goutte(e.x, e.y);
      if (e.vie <= 0 && e.vivant) { if (e.type === 'joueur') Missions.hopital(e.menace); else tuer(e, e.menace); }
    }
  }

  /** Blesse une entite. Rend true si le coup a porte. */
  function blesser(e, degats, source, options) {
    const opts = options || {};
    if (!e.vivant || e.invincible > 0) return false;
    // ⚠️ RIEN n'atteint un enfant : ni un poing, ni une balle, ni un char. Le
    // jeu est adulte, pas ca. Il prend peur et il court, point.
    if (e.intouchable) {
      e.etat = 'fuit';
      e.menace = source;
      e.minuterie = B.defs.pietons.reactions.fuite_secondes * 90;
      e.cri = 120;
      alerter(e.x, e.y, source, 1);
      return false;
    }
    e.vie -= degats;
    e.menace = source || e.menace;
    e.recul = Math.max(e.recul, opts.renverse ? 22 : 8);
    const angle = opts.angle === undefined ? angleVers(source ? source.x : e.x, source ? source.y : e.y, e.x, e.y) : opts.angle;
    const poussee = opts.renverse ? 3.2 : 1.4;
    e.vx = Math.cos(angle) * poussee;
    e.vy = Math.sin(angle) * poussee;
    if (opts.saigne) e.saigne = Math.min(B.defs.pietons.reactions.saignement_images, opts.saigne);
    if (e !== B.joueur) sang(e.x, e.y, opts.saigne ? 6 : 3);
    Son.SFX.touche();
    if (e.vie <= 0 && e.type === 'joueur') {
      Missions.hopital(source);
    } else if (e.vie <= 0) {
      if (opts.assomme) assommer(e);
      else tuer(e, source);
    } else if (e.type === 'pieton') {
      alerter(e.x, e.y, source, 2);
      if (e.etat !== 'attaque_joueur') {
        e.etat = (e.courage > 0 && B.rng() < e.courage) ? 'attaque_joueur' : 'fuit';
        e.minuterie = B.defs.pietons.reactions.fuite_secondes * 60;
      }
    }
    return true;
  }

  function assommer(e) {
    e.vie = 1;
    e.etat = 'assomme';
    e.face = 'couche';
    e.minuterie = B.defs.pietons.reactions.ko_images;
    e.vx = 0; e.vy = 0;
    if (e.arme) lacherArme(e);
  }

  function tuer(e, source) {
    if (!e.vivant) return;
    e.vivant = false;
    e.vie = 0;
    e.etat = 'mort';
    e.face = 'couche';
    e.solide = false;
    e.vx = 0; e.vy = 0;
    sang(e.x, e.y, 14);
    if (e.arme) lacherArme(e);
    if (e.type === 'pieton') {
      B.partie.stats.tues++;
      alerter(e.x, e.y, source, 3);
      if (source === B.joueur) {
        if (e.agent) Police.signalerCrime('mort_policier', e.x, e.y, true);
        else Police.signalerCrime('mort_pieton', e.x, e.y, Police.quelqu_un_voit(e.x, e.y, e));
      }
    }
  }

  function lacherArme(e) {
    const def = Combat.armeDef(e.arme);
    if (!def || def.prix === 0 && def.slug === 'poings') { e.arme = null; return; }
    creer('ramassage', e.x + (B.rng() - 0.5) * 8, e.y + 4, {
      r: 4, objet: 'arme', arme: e.arme, munitions: def.chargeur, t: 0, solide: false,
    });
    e.arme = null;
  }

  // --- Particules, sang, decalques ----------------------------------------------------

  function particule(x, y, vx, vy, vie, couleur, taille, gravite) {
    if (B.particules.length >= MAX_PARTICULES) B.particules.shift();
    B.particules.push({ x: x, y: y, z: 4, vx: vx, vy: vy, vz: 1.2, vie: vie, vieMax: vie,
                        c: couleur, s: taille || 1, g: gravite === undefined ? 0.22 : gravite });
  }

  function sang(x, y, nombre) {
    if (!B.options.sang) { poussiere(x, y, 3); return; }
    for (let i = 0; i < nombre; i++) {
      const a = B.rng() * Math.PI * 2, v = 0.4 + B.rng() * 1.6;
      particule(x, y, Math.cos(a) * v, Math.sin(a) * v * 0.6, 18 + B.rng() * 14, '#8e1b1b', 1);
    }
    if (nombre >= 6) decal(x, y, 'sang');
  }

  function goutte(x, y) {
    if (!B.options.sang) return;
    particule(x, y, 0, 0.2, 20, '#8e1b1b', 1);
    if (B.rng() < 0.4) decal(x, y, 'goutte');
  }

  function poussiere(x, y, nombre) {
    for (let i = 0; i < nombre; i++) {
      const a = B.rng() * Math.PI * 2;
      particule(x, y, Math.cos(a) * 0.6, Math.sin(a) * 0.4, 14, '#b9b2a4', 1);
    }
  }

  function decal(x, y, type) {
    if (!B.options.sang && type !== 'impact') return;
    if (B.decals.length >= MAX_DECALS) B.decals.shift();
    B.decals.push({ x: x, y: y, type: type, v: Math.floor(B.rng() * 4) });
  }

  function majParticules() {
    for (let i = B.particules.length - 1; i >= 0; i--) {
      const p = B.particules[i];
      p.x += p.vx; p.y += p.vy;
      p.z += p.vz; p.vz -= p.g;
      if (p.z <= 0) { p.z = 0; p.vz = 0; p.vx *= 0.6; p.vy *= 0.6; }
      if (--p.vie <= 0) B.particules.splice(i, 1);
    }
  }

  /** La foule qu'on entend, et le passant qui nous dit un mot en nous frolant. */
  function rumeurEtRepliques() {
    const j = B.joueur;
    if (B.t % 15 === 0) Son.Rumeur.maj(pietonsAutour(j.x, j.y, 200).filter(function (e) { return !e.metier; }).length);
    if (j.dansVehicule) return;
    for (const e of pietonsAutour(j.x, j.y, 30)) {
      if (e.metier || e.intouchable || e.etat === 'assomme' || e.etat === 'fuit' || e.etat === 'temoin' || e.aParle) continue;
      e.aParle = true;
      const femme = /passante|dame|mere|racoleuse/.test(e.arch);
      Son.Voix.dire(femme ? 'femme' : 'homme', e.x, e.y);
      break;
    }
  }

  // --- Boucle ---------------------------------------------------------------------------

  function maj() {
    indexer();
    let actifs = 0;
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const e = B.entites[i];
      if (!e.actif) continue;
      e.t++;
      if (e.animT > 0) e.animT--;
      if (e.type === 'joueur') majJoueur(e);
      else if (e.type === 'pieton') { majPieton(e); actifs++; }
      else if (e.type === 'ramassage'
               && (e.t > 3600 || dist2(e.x, e.y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI)) {
        retirer(e);
      }
    }
    // ⚠️ Apres que tout le monde a bouge, et sur un index REFAIT : `indexer()`
    // date du debut de l'image, et demeler la foule sur des positions perimees
    // laisse passer exactement les paires qui viennent de se rejoindre.
    indexer();
    demeler();
    majParticules();
    if (B.joueur && !B.interieur) { peupler(); semerDesArmesDeFortune(); rumeurEtRepliques(); }
    B.stats.actifs = actifs;
  }

  // --- Dessin ------------------------------------------------------------------------------

  /** Le nom de la pose a dessiner : la marche, ou le coup qui part. */
  function nomDePose(e) {
    if (e.etat === 'attaque' && e.phase && e.phase !== 'anticipation') return 'frappe_' + e.face;
    return e.face;
  }

  function imageDe(e) {
    const def = SPRITES[e.sprite];
    if (!def) return null;
    const cuit = Atlas.cuire(e.sprite, def, e.swaps);
    const voulu = nomDePose(e);
    const nom = cuit.poses[voulu] ? voulu : (cuit.poses[e.face] ? e.face : 'bas');
    const poses = cuit.poses[nom];
    const bouge = Math.abs(e.vx) + Math.abs(e.vy) > 0.05;
    // ⚠️ Une foulee de 9 px, pas 7 : a 7, les jambes tournaient plus vite que
    // le corps n'avancait et tout le monde avait l'air de courir.
    const i = bouge ? [0, 1, 0, 2][Math.floor(e.anim.dist / 9) % 4] : 0;
    // ⚠️ La pose « gauche » est le miroir de « droite », mais la main n'est
    // decrite QUE du cote droit : sans ce repli, l'arme disparaissait des que
    // le joueur marchait vers la gauche (Martin).
    const miroir = nom.endsWith('gauche');
    const main = def.mains ? (def.mains[miroir ? nom.slice(0, -6) + 'droite' : nom] || null) : null;
    return { canvas: poses[Math.min(i, poses.length - 1)], ancre: cuit.ancre, pose: nom, main: main, miroir: miroir };
  }

  // --- La pose : ce que le corps fait en plus de marcher ---------------------------

  /** Pure : (entite) -> { dx, dy, rot, echelleY, arme }. L'elan d'un coup
      (on recule, on se jette, on revient), le chancellement quand on est
      touche, la roulade qui tourne, le dos qui se courbe pour ramasser — et
      l'ARME tenue, qui se dessine dans la main de la pose (le bras, lui, est
      dans le sprite : la pose de coup le tend).

      ⚠️ Tout part d'ici, et rien d'autre ne connait ces chiffres : un test
      lit la pose sans dessiner, et le dessin ne fait qu'appliquer. */
  function pose(e) {
    const p = { dx: 0, dy: 0, rot: 0, echelleY: 1, arme: null };
    const cx = Math.cos(e.angle), cy = Math.sin(e.angle);
    if (e.roule > 0) {
      p.rot = (1 - e.roule / Combat.ROULADE_IMAGES) * Math.PI * 2 * (cx >= 0 ? 1 : -1);
      return p;
    }
    if (e.animT > 0 && e.animType === 'ramasse') { p.dy = 3; p.echelleY = 0.78; }
    if (e.recul > 0 && e.vivant && e.etat !== 'assomme') p.rot = (e.vx >= 0 ? 1 : -1) * 0.22;   // il chancelle
    const arme = Combat.armeDef(e.arme || 'poings') || Combat.armeDef('poings');
    if (e.etat === 'attaque' && e.phase && arme) {
      const elan = e.phase === 'anticipation' ? -2 : (e.phase === 'actif' ? 3 : 1);
      p.dx += Math.round(cx * elan); p.dy += Math.round(cy * elan * 0.6);
    }
    // L'arme se voit dans la main, au repos comme au coup : on sait ce qu'on tient.
    if (arme && arme.slug !== 'poings' && e.vivant && !e.dansVehicule && e.etat !== 'assomme') p.arme = arme;
    return p;
  }

  /** L'arme dans la main de la pose : `img.main` = [x, y, angle] dans la grille. */
  function dessinerArme(ctx, e, img, p, cx, cy) {
    if (!p.arme || !img.main) return;
    const image = Atlas.cuirePeintre('objet|' + p.arme.sprite, 16, 10, function (g, w, h) {
      OBJETS[OBJETS[p.arme.sprite] ? p.arme.sprite : 'defaut'](g, w, h);
    });
    const mx = img.miroir ? (SPRITES[e.sprite].w - 1 - img.main[0]) : img.main[0];
    const angle = img.miroir ? Math.PI - img.main[2] : img.main[2];
    const x = Math.round(e.x - cx + p.dx - img.ancre[0] + mx), y = Math.round(e.y - e.z - cy + p.dy - img.ancre[1] + img.main[1]);
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    if (img.miroir) ctx.scale(1, -1);
    ctx.drawImage(image, -2, -5);
    ctx.restore();
    B.stats.images++;
  }

  /** Le corps, avec sa pose : decale, penche, tourne, tasse. */
  function dessinerCorps(ctx, e, img, p, cx, cy) {
    const x = e.x - cx + p.dx, y = e.y - e.z - cy + p.dy;
    if (!p.rot && p.echelleY === 1) {
      ctx.drawImage(img.canvas, Math.round(x - img.ancre[0]), Math.round(y - img.ancre[1]));
      return;
    }
    ctx.save();
    ctx.translate(Math.round(x), Math.round(y));
    if (p.rot) ctx.rotate(p.rot);
    if (p.echelleY !== 1) ctx.scale(1, p.echelleY);
    ctx.drawImage(img.canvas, -img.ancre[0], -img.ancre[1]);
    ctx.restore();
  }

  function dessinerDecals(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const d of B.decals) {
      if (d.x < cx - 16 || d.x > cx + VW + 16 || d.y < cy - 16 || d.y > cy + VH + 16) continue;
      const image = Atlas.cuirePeintre('decal|' + d.type + '|' + d.v, 16, 12, function (c, w, h) {
        DECALS[d.type](c, d.v, w, h);
      });
      ctx.drawImage(image, Math.round(d.x - 8 - cx), Math.round(d.y - 6 - cy));
      B.stats.images++;
    }
  }

  function dessinerParticules(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const p of B.particules) {
      const x = Math.round(p.x - cx), y = Math.round(p.y - p.z - cy);
      if (x < -4 || y < -4 || x > VW + 4 || y > VH + 4) continue;
      ctx.globalAlpha = Math.min(1, p.vie / (p.vieMax * 0.4));
      ctx.fillStyle = p.c;
      ctx.fillRect(x, y, p.s, p.s);
      B.stats.rects++;
    }
    ctx.globalAlpha = 1;
  }

  function dessiner(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    const visibles = [];
    for (const e of B.entites) {
      if (!e.dessine) continue;
      if (e.x < cx - 40 || e.x > cx + VW + 40 || e.y < cy - 48 || e.y > cy + VH + 48) continue;
      visibles.push(e);
    }
    // ⚠️ Les morts d'abord : un cadavre se fait marcher dessus, il ne cache
    // jamais un vivant.
    visibles.sort(function (a, b) {
      return (a.vivant ? 1 : 0) - (b.vivant ? 1 : 0) || a.y - b.y || a.id - b.id;
    });
    B.stats.entites = visibles.length;
    const ombre = Atlas.cuirePeintre('ombre', DECORS.ombre.w, DECORS.ombre.h, DECORS.ombre.peindre);
    for (const e of visibles) {
      if (e.decor) {                 // decor ET commerces ambulants
        const d = DECORS[e.decor];
        if (!d) continue;
        const c = Atlas.cuirePeintre('decor|' + e.decor, d.w, d.h, d.peindre);
        ctx.drawImage(c, Math.round(e.x - d.ancre[0] - cx), Math.round(e.y - d.ancre[1] - cy));
        B.stats.images++;
        continue;
      }
      if (e.type === 'vehicule') { Vehicules.dessinerUn(ctx, e, cx, cy); continue; }
      if (e.type === 'feu') { Vehicules.dessinerFeu(ctx, e, cx, cy); continue; }
      if (e.type === 'ramassage' && e.objet === 'caisse') {
        const d = DECORS.caisse;
        const c = Atlas.cuirePeintre('decor|caisse', d.w, d.h, d.peindre);
        ctx.drawImage(c, Math.round(e.x - d.ancre[0] - cx), Math.round(e.y - d.ancre[1] + Math.sin(e.t / 14) * 1.5 - cy));
        B.stats.images++;
        continue;
      }
      if (e.type === 'ramassage') {
        const def = Combat.armeDef(e.arme);
        const c = Atlas.cuirePeintre('objet|' + (def ? def.sprite : 'poings'), 16, 10, function (g, w, h) {
          OBJETS[def && OBJETS[def.sprite] ? def.sprite : 'defaut'](g, w, h);
        });
        const flotte = Math.sin(e.t / 14) * 1.5;
        ctx.drawImage(c, Math.round(e.x - 8 - cx), Math.round(e.y - 8 + flotte - cy));
        B.stats.images++;
        continue;
      }
      const img = imageDe(e);
      if (!img) continue;
      if (e.vivant) ctx.drawImage(ombre, Math.round(e.x - 6 - cx), Math.round(e.y - 3 - cy));
      if (e.invincible > 0 && (e.invincible >> 2) % 2 === 0) continue;
      const p = pose(e);
      // L'arme passe DERRIERE le corps quand on regarde vers le haut.
      const derriere = e.face === 'haut';
      if (derriere) dessinerArme(ctx, e, img, p, cx, cy);
      dessinerCorps(ctx, e, img, p, cx, cy);
      if (!derriere) dessinerArme(ctx, e, img, p, cx, cy);
      B.stats.images += 2;
      // La bulle du temoin : on doit VOIR qu'on a ete vu.
      if (e.cri > 0 && e.vivant) {
        const bulle = Atlas.cuirePeintre('bulle|' + (e.etat === 'temoin' ? 't' : 'p'), 8, 10, function (g, w, h) {
          BULLES[e.etat === 'temoin' ? 'temoin' : 'peur'](g, w, h);
        });
        ctx.drawImage(bulle, Math.round(e.x - 4 - cx), Math.round(e.y - 26 - cy));
        B.stats.images++;
      }
    }
  }

  return {
    CELLULE, BULLE_NAISSANCE, BULLE_OUBLI, MAX_PIETONS, MAX_DECALS, MAX_PARTICULES, PORTEE_DECOR,
    creer, retirer, vider, creerJoueur, creerDecor, creerAmbulants, creerPaquets, creerPieton, reindexerDecor,
    peuplerInterieur,
    archetype, archetypeDeRue,
    indexer, autour, decorAutour, pietonsAutour, placeDeNaissance, peupler, peuplerDabord,
    semerDesArmesDeFortune, visibleAEcran,
    deplacerCercle, dansLaCarte, regarder, majJoueur, majPieton, maj, demeler, deboutDansLaFoule, pasDeDemele,
    enjamber, majEnjambe, clotureDevant, reglesCloture,
    blesser, assommer, tuer, alerter, lacherArme, traverseeSure, trottoirLePlusProche,
    particule, sang, poussiere, decal, majParticules,
    dessiner, dessinerDecals, dessinerParticules, imageDe, nomDePose, pose,
  };
})();
