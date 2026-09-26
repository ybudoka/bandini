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
  //: ⚠️ LE PLAFOND DE LA FOULE, et il vient de monter de 22 a 28 — demande de
  //: Martin : « plus de gens en centre-ville et moins en peripherie ». Le
  //: nombre de piétons d'un district est dans `carte.py`, mais il passe par
  //: `Math.min(MAX_PIETONS, ...)` : le Faubourg en demandait 26 et n'en avait
  //: jamais plus de 22, c'est-a-dire que le centre-ville etait plafonne et que
  //: les Quais, avec leur rythme du matin (x 1,4), etaient DENSER que lui. Le
  //: chiffre du quartier ne voulait plus rien dire. Les quatre autres districts
  //: ont baisse pour payer celui-ci : c'est la repartition qui change, et le
  //: budget d'image qui tient.
  const MAX_PIETONS = 28, MAX_PARTICULES = 300, MAX_DECALS = 150;
  //: Jusqu'ou chercher du decor solide autour de soi. ⚠️ La recherche est un
  //: CERCLE et l'empreinte une BOITE : il faut couvrir le coin de la boite la
  //: plus grosse, sinon le camion-restaurant n'est meme pas trouve et on lui
  //: passe au travers sans un seul test. Un juge refait le calcul sur chaque
  //: decor solide — ajouter un decor plus large sans monter ce chiffre tombe.
  //: 30 depuis les manèges de la foire a l'echelle de la grande roue (le
  //: plancher du carrousel : 26 x 8 de demi-boite).
  const PORTEE_DECOR = 30;
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
    // ⚠️ On LACHE ceux qui le regardaient. Un badaud garde un lien vers
    // l'artiste qu'il regarde (`attroupe`) : sans cette ligne, il garderait un
    // lien vers quelqu'un qui n'est plus dans la ville — rien a lire dedans,
    // mais l'objet reste accroche pour toute la partie, et `garnirLeCercle`
    // croit encore qu'il est pris.
    if (e.type === 'pieton' && e.metier && SPECTACLES.indexOf(e.metier) >= 0) {
      for (const q of B.entites) {
        if (q.attroupe === e) { q.attroupe = null; }
        if (q.versLeCercle === e) { q.versLeCercle = null; q.cap = null; }
      }
    }
    e.attroupe = null; e.versLeCercle = null;
  }

  function vider() {
    B.entites.length = 0;
    if (B.betes) B.betes.length = 0;
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
      // ⚠️ LES BETES N'ENTRENT DANS AUCUN INDEX DE PERSONNES, et ce n'est pas un
      // detail de rangement : indexees, elles se faisaient DEMELER avec la foule
      // (`demeler` ecarte ce qui se chevauche), les passants bougeaient
      // autrement, et `majPieton` ne tirait plus les memes des. Trois juges sans
      // rapport sont tombes — le pickpocket, le budget de la foule et le
      // trottoir — alors que les betes elles-memes ne tirent pas un seul de.
      // Un goeland n'est pas quelqu'un : on lui marche a travers.
      if (!e.actif || e.type === 'decor' || e.type === 'bete' || e.type === 'ballon') continue;
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

  /** LES JOUEURS de la partie, dans l'ordre : le premier, puis le deuxieme si
      la coop est la et qu'il tient debout. Tout ce qui se fait « pour chaque
      joueur » (le combat, les entrees, la camera) passe par ici plutot que par
      `B.joueur` — c'est la meme porte qu'ouvrira une coop en ligne. */
  function joueurs() {
    const out = [];
    if (B.joueur) out.push(B.joueur);
    if (B.coop && B.coop.entite && B.coop.entite.vivant) out.push(B.coop.entite);
    return out;
  }
  function estJoueur(e) { return !!e && e.type === 'joueur'; }

  function pietonsAutour(x, y, rayon) {
    return autour(x, y, rayon, function (e) { return e.type === 'pieton' && e.vivant; });
  }

  // --- Naissance ------------------------------------------------------------------

  function creerJoueur(x, y) {
    const p = B.partie;
    const j = creer('joueur', x, y, {
      r: 5, sprite: 'joueur', swaps: apparenceDuJoueur(p, B.defs),
      // Habille (`Garderobe`) : son linge, sa coupe ET son chapeau.
      tenue: typeof Garderobe !== 'undefined' ? Garderobe.duJoueur(p, B.defs) : null,
      // ⚠️ `vieMax` N'EST PLUS UN LITTERAL : les paliers d'ambulance le font
      // monter (+10 % a dix transports, +25 % a vingt-cinq). C'est le seul
      // avantage de palier qui ne se lise pas au moment de s'en servir — une
      // barre de vie se decide a la naissance.
      vie: p.vie, vieMax: Math.round(100 * Missions.avantage('vie', 1)),
      endurance: 100, surplus: 0, cafeine: 0, arme: p.arme || 'poings',
      dansVehicule: null, flagrant: 0, pasDist: 0, coupT: 0, charge: 0, roule: 0,
      cible: null,
      // Sa SOURCE d'entrees (`Entree.SOURCE1`) : le clavier, la manette ou le
      // doigt — et en coop, celui des deux appareils que l'option lui donne.
      // Voir la note des sources dans `entree.js` : c'est par la que passera
      // un jour un joueur distant.
      entree: typeof Entree !== 'undefined' ? Entree.SOURCE1 : null,
    });
    B.joueur = j;
    return j;
  }

  /** Le deuxieme joueur de la coop locale : meme sprite, meme linge que le
      premier, pour qu'on le reconnaisse tout de suite comme « l'autre toi »
      plutot que comme un passant de plus. */
  //: Un linge d'une autre couleur que toutes les tenues en vente (rouge,
  //: bleu, noir, gris, orange — voir `TENUES` dans `app/magasins.py`) : au
  //: premier coup d'œil, « l'autre toi » reste l'autre, quelle que soit la
  //: tenue du joueur 1. Retour de Martin, 22 sept. : « je veux une
  //: distinction pour différencier les joueurs ».
  const COULEUR_COOP_JOUEUR2 = '#16a085';

  /** ⚠️ UN VRAI JOUEUR, PAS UN PIETON DEGUISE — c'est le remaniement du
      22 sept. (« 2 vrais joueurs »), et il tient dans le `type`.

      L'essai en faisait un `pieton` marque `coopJoueur2`, et tout ce que le
      jeu reserve au joueur se demandait « est-ce LE joueur ? » : ses coups ne
      portaient jamais (`Combat.arcDeMelee` interdit pieton contre pieton), la
      police ne voyait pas ses crimes, il ne nageait pas, ne roulait pas, ne
      sprintait pas. Le meme `type` le fait passer par `majJoueur` comme le
      premier — une seule fonction pour les deux, et c'est la SOURCE
      D'ENTREES qu'il porte (`entree`) qui les distingue, plus le code.

      Ce qui lui reste en propre tient en une marque, `coopJoueur2` :
      l'ombre verte, et les trois gestes du joueur 1 (changer de scene,
      lancer une mission, conduire — Martin, 22 sept. : « les 2 personnages
      doivent pouvoir faire toutes les memes actions sauf ce qui change de
      scene et lancer des missions ou conduire »). */
  function creerJoueur2(x, y) {
    const p = B.partie;
    const swaps = Object.assign({}, apparenceDuJoueur(p, B.defs), { c: COULEUR_COOP_JOUEUR2 });
    const vieMax = Math.round(100 * Missions.avantage('vie', 1));
    return creer('joueur', x, y, {
      r: 5, sprite: 'joueur', swaps: swaps, coopJoueur2: true,
      entree: typeof Entree !== 'undefined' ? Entree.SOURCE2 : null,
      vie: vieMax, vieMax: vieMax,
      endurance: 100, surplus: 0, cafeine: 0, arme: 'poings',
      dansVehicule: null, flagrant: 0, pasDist: 0, coupT: 0, charge: 0, roule: 0,
      cible: null, etat: 'flane', dir: 0, butT: 0, cri: 0,
      // ⚠️ Deja invincible A LA NAISSANCE, pas seulement a la premiere image :
      // sans ca, une image separe la creation du premier rechargement, et un
      // coup porte pile a ce moment-la passerait.
      invincible: 60,
    });
  }

  function creerDecor(def) {
    grilleFixe.clear();
    (def.decor || []).forEach(function (d) {
      const fiche = DECORS[d.type] || {};
      const e = creer('decor', d.x * TT + 8, d.y * TT + 15, {
        decor: d.type, r: fiche.r === undefined ? 3 : fiche.r, solide: !!fiche.solide,
        // ⚠️ `invisible` : un decor qui ARRETE sans se peindre lui-meme — le pied
        // de la montagne russe, peint avec toute la structure (`Foire`).
        dessine: !fiche.invisible,
        // ⚠️ UNE VARIANTE PAR TUILE, et tiree a l'EMPREINTE de la tuile — jamais
        // au de du jeu : un decor qui consomme `B.rng()` decale tout ce qui
        // suit, et cette lecon-la a deja fait tomber quatre juges sans rapport.
        // Le mecanisme existait pour les DECALS (`d.v`) ; les parasols rayes
        // sont la premiere fiche de decor a en avoir besoin.
        v: fiche.variantes ? hash2(d.x * 7919 + d.y, 0x5A11) % fiche.variantes : 0,
      });
      // ⚠️ `estIndexable`, PAS `e.solide` : c'etait le second exemplaire de la
      // regle, et il a survecu au premier correctif. Un buisson restait hors
      // de l'index a la construction de la ville — donc invisible au char
      // comme a la balle — alors que `reindexerDecor` l'y remettait apres le
      // premier bris. Deux copies d'une regle, c'est une regle qui derive.
      if (estIndexable(e)) ajouterA(grilleFixe, e);
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
  /** `hasard` (optionnel, dans [0, 1[) remplace le de du jeu. ⚠️ Pour un
      choix COSMETIQUE — la tete du pilote d'une moto du trafic — on ne
      consomme pas `B.rng()` : chaque de tire pour un decor decale tous ceux
      qui suivent, et une auto-patrouille naissait ailleurs parce qu'un motard
      avait choisi ses cheveux. `hash2` de la position fait un tirage stable et
      gratuit. */
  function archetypeDeRue(x, y, hasard) {
    const zone = Monde.zoneA(x, y);
    const district = zone ? zone.district : null;
    const ordinaires = B.defs.pietons.catalogue.filter(function (p) {
      return p.frequence > 0 && !p.gang && (!p.districts || p.districts.indexOf(district) >= 0);
    });
    const de = (hasard === undefined || hasard === null) ? B.rng() : hasard;
    let tirage = de * ordinaires.reduce(function (s, p) { return s + p.frequence; }, 0);
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
    // L'HABIT : une tenue tiree dans la garde-robe de l'archetype (`Garderobe`), ou celle qu'on
    // lui donne (`arch.tenue` : un personnage, un passant qui descend de l'autobus).
    // ⚠️ A L'EMPREINTE de son identifiant, JAMAIS `B.rng()` : un de de plus par naissance
    // decalerait tout ce que la ville tire ensuite. `swaps` suit la tenue : ce qui lit encore
    // ses couleurs (le cavalier d'une moto) le voit habille pareil.
    let tenue = arch && arch.tenue ? arch.tenue
      : (typeof Garderobe !== 'undefined' ? Garderobe.tirer(p.slug, hash2(e.id, 0x7e4e)) : null);
    // ⚠️ Des COULEURS IMPOSEES sans tenue (un pilote d'avant la garde-robe, une robe que la
    // mission choisit) : la tenue tiree les prend. Sans ca, celui qu'on jette de sa moto se
    // relevait en quelqu'un d'autre.
    const imposees = !!(tenue && !(arch && arch.tenue) && arch && arch.couleurs && archetype(p.slug) &&
                        arch.couleurs !== archetype(p.slug).couleurs);
    if (imposees) {
      const c = arch.couleurs;
      tenue = Object.assign({}, tenue, { couleur_haut: c.c || tenue.couleur_haut, cheveux: c.h || tenue.cheveux,
                                         peau: c.s || tenue.peau, couleur_bas: c.p || tenue.couleur_bas });
    }
    if (tenue) { e.tenue = tenue; e.swaps = imposees ? arch.couleurs : Garderobe.couleurs(tenue); }
    // ⚠️ Une fille de la Brume TIENT SON COIN : sans poste, elle se remettait
    // a flaner comme n'importe qui au bout de dix secondes, et le seul indice
    // qui restait etait sa robe. On reconnait d'abord celle qui ATTEND.
    if (p.metier === 'compagnie') e.poste = { x: x, y: y };
    // L'homme-sandwich aussi tient un poste — plus large (six tuiles) : un
    // solliciteur fait les cent pas devant son kiosque, il n'attend pas.
    if (p.metier === 'reclame') {
      e.poste = { x: x, y: y };
      e.posteRayon = (B.defs.reclame && B.defs.reclame.poste_rayon_px) || POSTE_RAYON;
      e.heures = p.heures || null;
      e.repos = 0;
    }
    // Une mere ne sort pas sans son petit : il la suit, et il detale avec elle.
    if (p.accompagne) {
      const petit = creerPieton(x + 10, y + 4, archetype(p.accompagne));
      // ⚠️ IL NAIT A COTE D'ELLE, ET PERSONNE NE VERIFIAIT LA TUILE. Une mere
      // nee au ras d'un mur posait son enfant DANS le mur — et de la, il ne
      // pouvait plus sortir : le masque du pieton ne laisse pas sortir d'une
      // facade plus qu'il n'y laisse entrer. On le remet alors SUR sa mere,
      // qui est sur une tuile valable par construction ; la foule les demele a
      // l'image suivante.
      if (Monde.bloque(Math.floor(petit.x / TT), Math.floor(petit.y / TT), Monde.MASQUE_PIETON)) {
        petit.x = x; petit.y = y;
      }
      petit.suit = e;
      e.petit = petit;
    }
    // ⚠️ IL ENTRE DANS L'INDEX EN NAISSANT. `placeLibre` ne lit que `grille`,
    // et `grille` ne se refait qu'une fois par image : deux naissances dans la
    // MEME image ne se voyaient donc pas l'une l'autre. C'est ce qui arrivait
    // a l'image 1 — `peupler()` posait un passant, `Police.peuplerAgents()`
    // regardait un index d'ou il manquait, et l'agent naissait sur le passant,
    // au pixel pres (9 px de chevauchement pour deux corps de 10). Seuls
    // `peuplerDabord` et les hommes-sandwichs indexaient leurs naissances ;
    // maintenant c'est la naissance elle-meme qui le fait, pour tout le monde.
    ajouterA(grille, e);
    return e;
  }

  //: Ou un corps couche dans un lit pose ses PIEDS (l'ancre), depuis le haut de
  //: la tuile de tete : au bas de la tuile, pour que sa tete tombe sur
  //: l'oreiller. Le malade et le joueur reveille a l'hopital, le meme chiffre.
  const PIEDS_ALITE = 15;

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
      const arch = archetypeDedans(g);
      if (!arch) continue;
      const couche = g.qui === 'malade', assis = g.qui === 'patient' || g.qui === 'avocat';
      // ⚠️ Le malade, le patient et l'avocat naissent DANS leur meuble (`carte.ASSIS_OU_COUCHE`),
      // et pas au centre de la tuile : un corps couche pose ses PIEDS (l'ancre)
      // au bas de la tuile de tete, pour que sa tete tombe sur l'oreiller ; un
      // corps assis pose les siens au bord de l'assise, sa tete devant le dossier.
      const y = g.y * TT + (couche ? PIEDS_ALITE : (assis ? 14 : 8));
      const e = creerPieton(g.x * TT + 8, y, arch);
      e.face = 'bas';
      // Le commis ne quitte pas sa caisse, la soignante son triage ; le client, lui, magasine.
      if (g.qui === 'commis' || g.qui === 'soignant') e.poste = { x: e.x, y: e.y };
      // ⚠️ `fige`, la regle du donneur : il TIENT sa place (on le bouscule, il y
      // revient) et il ne se retourne pas — c'est ce qui garde un malade couche
      // et un patient ou un avocat assis. Qu'on le frappe, et il redevient un
      // passant : il se leve et il se sauve, en jaquette s'il le faut.
      if (couche || assis) {
        e.etat = 'fige';
        e.plante = { x: e.x, y: e.y };
        e.face = couche ? 'alite' : 'assis_bas';
        e.alite = couche;
      }
    }
    indexer();
  }

  /** Qui naît dans une piece, selon ce que le plan demande.

      ⚠️ Le malade porte la jaquette de l'archetype `malade`, mais la TETE et la
      PEAU d'un passant du quartier (`archetypeDeRue`, a l'empreinte de sa tuile
      — pas au de du jeu) : six malades a la meme tete dans six lits, ce serait
      une seule image collee six fois. Le patient, lui, attend dans son linge de
      tous les jours ; un corps qui ne sait pas s'asseoir (l'enfant, les sortes
      a leur sprite) cede sa chaise a un passant ordinaire. */
  function archetypeDedans(g) {
    if (g.qui === 'commis') return archetype('commis');
    if (g.qui === 'soignant') return archetype('soignante');
    if (g.qui === 'avocat') return archetype('avocat');
    const hasard = (hash2(g.x * 131 + g.y, 0xD0C) % 1000) / 1000;
    if (g.qui === 'malade') {
      const jaquette = archetype('malade'), rue = archetypeDeRue(g.x * TT, g.y * TT, hasard);
      return Object.assign({}, jaquette, { couleurs: Object.assign({}, jaquette.couleurs, { h: rue.couleurs.h, s: rue.couleurs.s }) });
    }
    if (g.qui === 'patient') {
      const rue = archetypeDeRue(g.x * TT, g.y * TT, hasard);
      return (rue.sprite === 'joueur' && !rue.accompagne) ? rue : archetype('passant');
    }
    return archetypeDeRue(g.x * TT, g.y * TT);
  }

  /** Rebatit l'index fixe a partir des entites presentes (retour de l'interieur). */
  //: Le plafond de debris. ⚠️ Ce sont des ENTITES : elles comptent dans le
  //: budget d'image comme tout le reste. Une nuit a tout casser doit tenir le
  //: rythme, donc les plus vieux debris disparaissent en premier.
  //: Combien de temps une borne defoncee crache : dix secondes. ⚠️ Assez pour
  //: qu'on la voie de loin et qu'on revienne voir, pas assez pour que la rue
  //: reste une fontaine jusqu'au lendemain — le decor, lui, ne repousse qu'au
  //: `nouveauJour()`, mais l'eau, elle, s'arrete.
  const JET_EAU_IMAGES = 600;
  //: Jusqu'ou une gerbe de borne s'entend. C'est fort, une borne ouverte.
  const JET_EAU_PORTEE = 260;

  const DEBRIS_MAX = 40;

  //: Ce qui se ramasse par terre et se dessine par son NOM d'objet, pas par une
  //: arme : la liasse d'un guichet, et ce qu'une distributrice defoncee crache.
  const OBJETS_PAR_TERRE = { billets: true, monnaie: true, canette: true, sac: true };

  /** Une ARME mord le decor : la balle, l'explosion, le feu. Rend vrai s'il
      est tombe de ce coup-ci.

      ⚠️ C'est le SECOND chemin vers `briser`, et il a manque longtemps. Jusqu'au
      15 sept. 2026, `briser` n'avait qu'un seul appelant — le char lance
      (`Vehicules.heurterDecor`) — et un lampadaire encaissait un chargeur entier
      sans bouger : la balle traversait le decor, l'explosion d'un char ne
      filtrait que `q.vivant`, le brasier non plus. Un char couche d'un coup ;
      une arme USE, et c'est `pv` qui dit combien.

      ⚠️ Ce qui porte `arrete` (un arbre, une fontaine, un camion-restaurant) n'a
      PAS de `pv` et ne tombe donc jamais : il encaisse. C'est voulu — une rue
      qu'on demonte au pistolet n'offre plus un seul abri, et les kiosques
      ambulants sont des commerces, pas des cibles. `scripts/verifier_ce_qui_casse.py`
      tient les deux moities de cette regle.

      ⚠️ Les PV vivent sur l'ENTITE, pas sur la fiche : deux poubelles de la meme
      rue s'usent chacune de son cote, et `reparerLeDecor` les oublie au matin. */
  function endommagerDecor(e, degats) {
    if (!e || e.type !== 'decor' || e.brise) return false;
    const fiche = DECORS[e.decor] || {};
    if (!fiche.pv) return false;
    if (e.pv === undefined) e.pv = fiche.pv;
    e.pv -= Math.max(1, Math.round(degats));
    if (e.pv > 0) { poussiere(e.x, e.y, 2); return false; }
    return briser(e);
  }

  /** Casser un decor : il tombe, il laisse des debris, et il sort de l'index
      fixe.

      ⚠️ `grilleFixe` est l'index « qui ne bouge jamais » — c'est ce qui rend
      le decor gratuit par image. Casser, c'est l'en sortir : on reindexe AU
      BRIS, jamais par image.

      ⚠️ Et un lampadaire a terre NE S'ALLUME PLUS. Sa lumiere vit dans
      `carte.lampes`, a part de son poteau : casser l'un sans eteindre l'autre
      donnerait un halo qui flotte au-dessus de rien — exactement le genre de
      chose qu'on ne voit qu'en jouant, la nuit. */
  function briser(e) {
    if (!e || e.type !== 'decor' || e.brise) return false;
    e.brise = true;
    e.solide = false;
    e.dessine = false;
    eteindreLaLampe(e);
    const d = creer('decor', e.x, e.y, {
      // ⚠️ `debris: true` ET `ne: B.t` separes : l'image de naissance vaut
      // ZERO au premier instant d'une partie, et `if (e.debris)` laissait
      // alors passer le premier morceau casse du jeu.
      decor: 'debris', r: (DECORS.debris || {}).r || 4, solide: false, dessine: true,
      debris: true, ne: B.t,
    });
    // Les plus vieux debris s'en vont : le plafond tient le budget d'image.
    const tous = B.entites.filter(function (q) { return q.type === 'decor' && q.debris; });
    if (tous.length > DEBRIS_MAX) {
      tous.sort(function (a, b) { return a.ne - b.ne; });
      for (let i = 0; i < tous.length - DEBRIS_MAX; i++) retirer(tous[i]);
    }
    reindexerDecor();
    poussiere(e.x, e.y, 8);
    // Le decor qui cede s'ENTEND, de la ou il est (`Son.SFX.bris`). La borne,
    // le guichet et les distributrices ont le leur, plus bas.
    if (typeof Son !== 'undefined') Son.depuis(e, function () { Son.SFX.bris(e.decor); });
    // ⚠️ UN GUICHET DEFONCE REPAND SA CAISSE — et c'est un delit a deux
    // etoiles, quoi qu'il l'ait ouvert (un camion, l'explosion d'a cote, un
    // chargeur entier) : la caisse est par terre, tout le monde l'a vu.
    if (e.decor === 'guichet' && typeof Missions !== 'undefined' && Missions.guichetCasse) Missions.guichetCasse(e);
    // ⚠️ UNE DISTRIBUTRICE DEFONCEE CRACHE sa monnaie et ses canettes — quoi
    // qui l'ait ouverte, comme le guichet. C'est la fiche qui le dit
    // (`distributrice: sorte`), pas le nom du decor.
    if ((DECORS[e.decor] || {}).distributrice && typeof Missions !== 'undefined' && Missions.distributriceCassee) {
      Missions.distributriceCassee(e);
    }
    // ⚠️ UNE BORNE-FONTAINE DEFONCEE CRACHE. C'est la seule raison d'en avoir
    // fait un decor cassable : une tuile ne peut ni tomber ni gicler. Le jet
    // est une ENTITE INVISIBLE qui vit ses dix secondes et crache des
    // particules — le meme patron que le brasier du Molotov, et la meme raison
    // : on ne repeint pas une tuile a chaque image pour un effet qui passe.
    if (e.decor === 'borne_fontaine') {
      creer('jet_eau', e.x, e.y, { minuterie: JET_EAU_IMAGES, dessine: false, solide: false, r: 0 });
      // ⚠️ Le bouchon et l'eau qui s'ouvre — PAS le choc : celui-la appartient
      // a ce qui l'a defoncee, et le char le joue deja a la meme image.
      Son.SFX.borne_cassee();
    }
    void d;
    return true;
  }

  /** La lampe d'un poteau tombe : on la coupe, sans la perdre. */
  function eteindreLaLampe(e) {
    const c = Monde.carte;
    if (!c || !c.lampes) return;
    for (const l of c.lampes) {
      if (l.eteinte) continue;
      if (Math.abs(l.x - e.x) <= 10 && Math.abs(l.y - e.y) <= 22) { l.eteinte = true; break; }
    }
  }

  /** Le lendemain, la ville est reparee. ⚠️ Rien ne repousse dans la minute :
      ce qu'on a casse reste casse jusqu'a `nouveauJour()`, et le quartier
      porte ses blessures — c'est ce qui fait qu'une nuit de folie SE VOIT le
      matin. */
  /** RELEVER un decor casse, tout de suite : ce que le forain fait de ses
      cibles entre deux parties (`Histoire.commencerDefi`).

      ⚠️ La meme remise a neuf que le matin (`reparerLeDecor`), pour UNE piece.
      Sans elle, une galerie de tir jouee deux fois dans la journee serait un
      defi qu'on ne peut plus gagner : ses cibles sont par terre, et le matin
      est loin. */
  function releverDecor(e) {
    if (!e || e.type !== 'decor') return false;
    e.pv = undefined;
    if (!e.brise) return false;
    const fiche = DECORS[e.decor] || {};
    e.brise = false;
    e.dessine = true;
    e.solide = !!fiche.solide;
    reindexerDecor();
    return true;
  }

  function reparerLeDecor() {
    let remis = 0;
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const e = B.entites[i];
      if (e.type !== 'decor') continue;
      if (e.debris) { retirer(e); continue; }
      // ⚠️ Ce qu'une arme a ENTAME sans l'abattre se referme aussi. Le test
      // `if (!e.brise) continue` sautait ces decors-la : un poteau a demi
      // troue par une balle du mardi serait tombe d'une seule balle le
      // vendredi, et le quartier se serait use tout seul, sans que personne
      // n'y touche.
      e.pv = undefined;
      if (!e.brise) continue;
      const fiche = DECORS[e.decor] || {};
      e.brise = false;
      e.dessine = true;
      e.solide = !!fiche.solide;
      remis++;
    }
    const c = Monde.carte;
    if (c && c.lampes) for (const l of c.lampes) l.eteinte = false;
    reindexerDecor();
    return remis;
  }

  /** ⚠️ L'index fixe prend le decor solide ET ce qui CASSE sans etre solide.
      Un buisson et une corde a linge declarent `casse` depuis toujours, mais
      `solide: false` les tenait HORS de l'index — et `decorDevant` comme la
      balle cherchent la-dedans. Resultat : deux fiches qui se disaient
      destructibles et que rien au monde ne pouvait toucher. Ce qui traverse un
      buisson, ce n'est pas l'index qui le dit, c'est `bloquerParDecor`, qui
      relit `solide` juste apres. */
  function estIndexable(e) {
    if (e.type !== 'decor' && e.type !== 'ambulant') return false;
    if (e.solide) return true;
    return !e.brise && !!(DECORS[e.decor] || {}).casse;
  }

  function reindexerDecor() {
    grilleFixe.clear();
    for (const e of B.entites) if (estIndexable(e)) ajouterA(grilleFixe, e);
  }

  /** La boîte d'un décor (`sol`, en demi-côtés) touche-t-elle le cercle (x, y, r) ?
      La même arithmétique que `bloquerParDecor` : on ressort par le côté le moins enfoncé. */
  function boiteTouche(d, x, y, r) {
    const sol = (DECORS[d.decor] || {}).sol || [d.r || 4, d.r || 4];
    return sol[0] + r - Math.abs(x - d.x) > 0 && sol[1] + r - Math.abs(y - d.y) > 0;
  }

  /** ⚠️ POUSSER UN DÉCOR (la benne d'un chantier) : le déplacer de (mx, my), s'il le peut.
      Le décor ne bougeait JAMAIS (voir l'index fixe) : celui-ci est le seul qui bouge, et il
      tient l'index à jour LUI-MÊME — sans quoi les piétons continueraient de buter sur
      l'endroit qu'il a quitté et de traverser celui où il est.

      Il refuse — et le char qui pousse est alors arrêté comme devant un mur — dès que le
      décor : s'éloigne de plus de `portee` px de chez lui (`d.chez`), entre dans une tuile
      solide (les quatre coins de sa boîte), ou en chevauche un autre décor solide. Rend vrai
      s'il a bougé. */
  function pousserDecor(d, mx, my) {
    const fiche = DECORS[d.decor] || {};
    if (!fiche.poussable || d.brise) return false;
    if (!d.chez) d.chez = { x: d.x, y: d.y };
    const nx = d.x + mx, ny = d.y + my, sol = fiche.sol || [d.r, d.r];
    if (Math.max(Math.abs(nx - d.chez.x), Math.abs(ny - d.chez.y)) > (fiche.portee || 0)) return false;
    for (const sx of [-1, 1]) {
      for (const sy of [-1, 1]) {
        if (Monde.solidite(Math.floor((nx + sx * sol[0]) / TT), Math.floor((ny + sy * sol[1]) / TT)) !== 0) return false;
      }
    }
    for (const o of decorAutour(nx, ny, sol[0] + 24)) {
      if (o === d || !o.solide || o.brise) continue;
      const so = (DECORS[o.decor] || {}).sol || [o.r || 4, o.r || 4];
      if (Math.abs(nx - o.x) < sol[0] + so[0] && Math.abs(ny - o.y) < sol[1] + so[1]) return false;
    }
    const ancienne = cle(d.x, d.y);
    d.x = nx; d.y = ny;
    if (cle(nx, ny) !== ancienne) {
      const liste = grilleFixe.get(ancienne);
      if (liste) {
        const i = liste.indexOf(d);
        if (i >= 0) liste.splice(i, 1);
        if (!liste.length) grilleFixe.delete(ancienne);
      }
      ajouterA(grilleFixe, d);
    }
    return true;
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
  /** Une porte par laquelle les gens passent.

      ⚠️ Toutes n'ont pas le meme sens. Un `d` est un LOGEMENT : les gens y
      rentrent chez eux, et le dessin le dit deja (battant sombre, aucune
      poignee de laiton, aucune enseigne) — le joueur apprend a ne pas essayer.
      Un `D` mene a un interieur : un commerce n'avale personne quand il est
      FERME, et le poste de police et l'hopital ne sont pas des allees et
      venues de passants. ⚠️ Et la planque de Rocco, JAMAIS : c'est chez le
      joueur. */
  function porteQuiSert(porte) {
    if (!porte) return false;
    // ⚠️ LA TUILE D'ABORD. La liste des portes se lit au chargement, et depuis
    // les chantiers le sol change en cours de partie : une maison rasee n'avale
    // plus personne. On ne retire pas la porte de la liste — son ORDRE compte
    // pour tout ce qui y tire au sort, et le reordonner faisait naitre la foule
    // ailleurs, a l'autre bout de la ville (mesure : trois juges sans rapport).
    if (Monde.glyphe(porte.x, porte.y) !== porte.glyphe) return false;
    if (porte.glyphe === 'd') return true;                 // un logement : toujours
    const p = Monde.porteA(porte.x, porte.y);
    if (!p || !p.lieu) return true;
    if (p.lieu === 'planque') return false;                // chez le joueur
    if (p.lieu === 'poste' || p.lieu === 'hopital') return false;
    // ⚠️ Un commerce FERME n'avale personne — mais les interieurs n'ont PAS
    // d'heures declarees : seuls les kiosques de rue (`ambulants`) en ont. La
    // nuit tient donc lieu de fermeture, avec la seule exception qui compte —
    // le bar, qui vit justement la nuit. Le jour ou `carte.INTERIEURS` portera
    // des heures, ces deux lignes deviendront `Missions.ouvert(...)`.
    if (p.lieu === 'bar') return true;
    return !Monde.estNuit();
  }

  function placeDeNaissance() {
    const carte = Monde.carte;
    // ⚠️ On naissait deja sur un pas de porte une fois sur trois — mais
    // SEULEMENT HORS ECRAN. Ce n'etait pas une sortie, c'etait une naissance
    // deguisee en sortie : son seul interet aurait ete d'etre vue. La regle
    // « hors ecran » saute ici, et le pieton nait DANS la porte, invisible, le
    // temps que le battant s'ouvre.
    if (B.rng() < 0.34 && carte.portesFermees.length) {
      for (let essai = 0; essai < 8; essai++) {
        const porte = carte.portesFermees[Math.floor(B.rng() * carte.portesFermees.length)];
        if (!porteQuiSert(porte)) continue;
        const x = porte.x * TT + 8, y = (porte.y + 1) * TT + 8;
        if (dist2(x, y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI) continue;
        if (!Monde.marchablePieton(porte.x, porte.y + 1)) continue;
        if (!placeLibre(x, y)) continue;
        return { x: x, y: y, porte: porte };
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

  //: Les voies ou un char roule droit : ni le carrefour (`+`), ni la ligne d'arret.
  const VOIES_DROITES = { '<': 1, '>': 1, '^': 1, 'v': 1 };

  /** Une place AU BORD DE LA ROUTE, hors ecran : une tuile de trottoir collee a
      une voie ou roule un char. C'est la qu'on attend un taxi.

      ⚠️ Demande de Martin (17 sept. 2026) : « il faut que les clients attendent
      sur le bord de la route ». Le client naissait par `placeDeNaissance` — un
      pas de porte, ou n'importe quelle tuile marchable hors route : un parc,
      une ruelle, une arriere-cour. Le taxi klaxonnait pour quelqu'un qu'il ne
      pouvait pas aller chercher.

      `atteint(tx, ty)` dit si le char qui vient chercher le client rejoint
      cette voie : depuis l'ile, le trottoir d'en face est a portee de klaxon et
      pas de roues. Le tirage se fait sur TOUTES les places de la couronne, pas
      au hasard d'un angle : une rue entre les blocs est une ligne mince, et un
      angle tire au hasard tombe le plus souvent dans un bloc. Si la couronne de
      naissance n'en a pas, on cherche deux fois plus loin — le client ne
      s'oublie pas (`peupler`).
      Rend `{ x, y, rue: { x, y } }` (le centre de la voie), ou null. */
  function placeAuBordDeLaRoute(atteint) {
    const carte = Monde.carte, j = B.joueur;
    const couronnes = [[BULLE_NAISSANCE, BULLE_OUBLI - 60], [BULLE_NAISSANCE, 2 * BULLE_OUBLI]];
    for (const c of couronnes) {
      const rt = Math.ceil(c[1] / TT), jx = Math.floor(j.x / TT), jy = Math.floor(j.y / TT);
      const places = [];
      for (let ty = Math.max(1, jy - rt); ty <= Math.min(carte.h - 2, jy + rt); ty++) {
        for (let tx = Math.max(1, jx - rt); tx <= Math.min(carte.w - 2, jx + rt); tx++) {
          const x = tx * TT + 8, y = ty * TT + 8, d2 = dist2(x, y, j.x, j.y);
          if (d2 < c[0] * c[0] || d2 > c[1] * c[1]) continue;
          if (!Monde.estTrottoir(tx, ty) || !Monde.marchablePieton(tx, ty)) continue;
          const rue = [[1, 0], [-1, 0], [0, 1], [0, -1]].find(function (d) {
            const nx = tx + d[0], ny = ty + d[1];
            return VOIES_DROITES[Monde.fleche(nx, ny)] && Monde.estChaussee(nx, ny) && atteint(nx, ny);
          });
          if (!rue) continue;
          if (Monde.porteA(tx, ty - 1)) continue;             // on ne bouche pas une porte
          places.push({ x: x, y: y, rue: { x: (tx + rue[0]) * TT + 8, y: (ty + rue[1]) * TT + 8 } });
        }
      }
      // ⚠️ Les tests couteux APRES le tirage : l'ecran, la foule, le decor.
      while (places.length) {
        const k = Math.floor(B.rng() * places.length), p = places[k];
        places[k] = places[places.length - 1]; places.pop();
        if (visibleAEcran(p.x, p.y, 24) || !placeLibre(p.x, p.y)) continue;
        if (decorAutour(p.x, p.y, 8).some(function (d) { return d.solide && !d.brise; })) continue;
        return p;
      }
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
    const voulu = Math.min(MAX_PIETONS, zone ? zone.pietons : 12) * Monde.rythme(zone) * 0.6;
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
    naitreLesHommesSandwichs(true);
    indexer();
  }

  /** Est-on dans ses heures ? `heures` = [debut, fin] sur la journee ramenee
      a 0..1, et le creneau peut passer minuit (`pietons.travaille_a`). */
  function enService(heures) {
    if (!heures) return true;
    const h = B.partie ? B.partie.heure : 0.5;
    return heures[0] < heures[1] ? (h >= heures[0] && h < heures[1]) : (h >= heures[0] || h < heures[1]);
  }

  // --- Trois sortes de gens, et ce qu'elles FONT ----------------------------------

  /*: ⚠️ UNE SORTE = UN CORPS + UNE ROUTINE. Le corps est dans `sprites.js`, le
    metier dans `pietons.py` — et c'est ICI que la sorte existe vraiment. La
    ville avait 24 archetypes pour quatre corps, et sur six metiers, DEUX
    faisaient quelque chose : les autres etaient des nombres. Une sorte qui ne
    fait rien est un costume, et le depot a deja paye ce defaut une fois. */
  const SORTES = ['musicien', 'amuseur', 'jongleur', 'echassier', 'exhibitionniste',
                  'contractuelle', 'touriste', 'ivrogne', 'jogger', 'facteur',
                  'crieur', 'laveur', 'pickpocket', 'camelot'];

  //: LES AMUSEURS DE RUE — les quatre qui font un NUMERO et qu'on regarde.
  //: ⚠️ Ils partagent un plafond au lieu d'en avoir un chacun, et c'est la
  //: seule facon de tenir « toujours entre 3 et 5 personnes autour » (demande
  //: de Martin) : quatre sortes a deux exemplaires, ce sont huit artistes dans
  //: la bulle, donc de vingt-quatre a quarante spectateurs — pour un budget de
  //: foule de vingt-huit. Le cercle serait reste vide, et la rue n'aurait plus
  //: eu un seul passant qui passe.
  const SPECTACLES = ['musicien', 'amuseur', 'jongleur', 'echassier'];

  //: Combien de chaque sorte vivent dans la bulle du joueur, au plus.
  const SORTES_MAX = 2;

  /** L'ordre dans lequel on essaie de faire naitre les sortes, les AMUSEURS
      MELANGES.

      ⚠️ Ils partagent un plafond de deux : pris dans l'ordre de la liste, ce
      seraient toujours les deux premiers — le musicien et le mime — et le
      jongleur comme l'echassier ne naitraient JAMAIS. Quatre sortes dessinees,
      deux qu'on voit : c'est exactement le defaut qu'on repare. */
  function ordreDesSortes() {
    const amuseurs = SPECTACLES.slice();
    for (let i = amuseurs.length - 1; i > 0; i--) {
      const k = Math.floor(B.rng() * (i + 1));
      const t = amuseurs[i]; amuseurs[i] = amuseurs[k]; amuseurs[k] = t;
    }
    let n = 0;
    return SORTES.map(function (slug) {
      return SPECTACLES.indexOf(slug) >= 0 ? amuseurs[n++] : slug;
    });
  }

  /** Elles naissent aux coins de rue, pas dans la foule : `frequence` vaut
      zero au catalogue, exactement comme l'homme-sandwich. */
  function naitreLesSortes() {
    if (!B.joueur || B.interieur) return 0;
    const zone = Monde.zoneA(B.joueur.x, B.joueur.y);
    let nes = 0;
    for (const slug of ordreDesSortes()) {
      const arch = archetype(slug);
      if (!arch || arch.slug !== slug) continue;
      // ⚠️ CHACUNE A SES QUARTIERS, et c'est la fiche qui le dit. Un touriste
      // dans La Shop et un facteur sur le port, c'est huit sortes partout
      // pareilles — de la figuration, donc. Un quartier se reconnait aussi a
      // qui y marche.
      if (arch.districts && (!zone || arch.districts.indexOf(zone.district) < 0)) continue;
      // ⚠️ ET SES HEURES (la nuit a ses habitudes). Le crieur ne travaille que le
      // matin (`heures`) — et il naissait quand meme a deux heures du matin, pour
      // hurler la manchette a une rue vide. `enService` est celui de l'homme-sandwich.
      if (!enService(arch.heures)) continue;
      // ⚠️ DEUX pour celles qui tiennent un poste, UNE pour celles qui
      // marchent. Un spectacle est plante quelque part : il en faut deux pour
      // avoir une chance d'en croiser un. Une sorte qui marche, elle, traverse
      // toute la bulle — une suffit a la voir, et deux ne font que grossir la
      // figuration (le budget de la bagarre le compte).
      const spectacle = SPECTACLES.indexOf(slug) >= 0;
      // ⚠️ LES AMUSEURS PARTAGENT UN PLAFOND (voir `SPECTACLES`) : un seul de
      // chaque, et deux en tout. C'est ce qui les garde rares — donc remarques
      // — et c'est surtout ce qui laisse de la place dans le budget de la foule
      // pour les trois a cinq personnes qui doivent etre autour de chacun.
      const combien = spectacle ? 1 : (arch.vitesse > 0 ? 1 : SORTES_MAX);
      const deja = B.entites.filter(function (q) { return q.type === 'pieton' && q.arch === slug && q.vivant; }).length;
      if (deja >= combien) continue;
      if (spectacle && artistes() >= reglesSpectacle().artistes_max) continue;
      // ⚠️ UN AMUSEUR NE SE POSE PAS N'IMPORTE OU. `placeDeNaissance` rend la
      // premiere tuile marchable venue hors de l'ecran — c'est-a-dire souvent
      // une ruelle, un devant de hangar, un bout de trottoir entre deux
      // poubelles. Le numero etait bon, l'endroit ne l'etait pas, et personne
      // ne venait le voir. `carte.scenes` donne les endroits ou le monde PASSE
      // ET S'ARRETE : la place publique, les parcs, le terminus d'autobus, le
      // trottoir devant les commerces.
      const place = spectacle ? sceneLibre(zone) : placeDeNaissance();
      if (!place || visibleAEcran(place.x, place.y, 24)) continue;
      // ⚠️ ET SON STANDING, a l'endroit ou elle se pose (4e vague des quartiers) :
      // un touriste ne flane pas au pied des plex du port, un ivrogne ne dort pas
      // dans la rue chic. Le district se lit au joueur (c'est sa bulle), le
      // standing a la TUILE : deux blocs voisins n'ont pas le meme.
      if (arch.standings) {
        const rang = Monde.standingA(Math.floor(place.x / TT), Math.floor(place.y / TT));
        if (arch.standings.indexOf(rang) < 0) continue;
      }
      const e = creerPieton(place.x, place.y, arch);
      if (!e) continue;
      // ⚠️ Qui tient un poste se lit dans la FICHE (`vitesse: 0`), pas dans
      // une liste de slugs : le musicien et l'amuseur ne bougent pas, les six
      // autres marchent. Une liste ici aurait fait mentir `pietons.py` a la
      // sixieme sorte.
      if (arch.vitesse > 0) { e.etat = 'flane'; }
      else { e.etat = 'fige'; e.face = 'bas'; e.plante = { x: e.x, y: e.y }; }
      if (spectacle) ouvrirLeSpectacle(e);
      nes++;
    }
    return nes;
  }

  // --- Les amuseurs de rue : un numero, et du monde autour ------------------------

  /*: ⚠️ Retour de Martin : « presentement ils ne font rien et sont ennuyants ».
    Il a raison, et la fiche d'origine le disait deja : le musicien devait
    « jouer — et ca s'entend », l'amuseur devait faire un NUMERO. Ce qui a ete
    livre : deux corps a `vitesse: 0` envoyes dans `attrouper`, une fonction qui
    ne touche QU'AUX BADAUDS et ne change rien a l'artiste. Ils tenaient l'image
    zero de leur sprite du debut a la fin de la partie — `imageDe` choisit son
    image d'apres la distance parcourue, et un corps immobile n'en parcourt
    aucune.

    Et l'attroupement etait une CHANCE, pas une regle : il fallait qu'un passant
    entre de lui-meme dans les 46 pixels. Dans une rue vide, personne ; et ceux
    qui s'arretaient repartaient au bout de quelques secondes sans etre
    remplaces. Le juge du banc posait lui-meme quatre badauds avant de mesurer —
    c'est-a-dire qu'il mesurait l'attroupement d'une foule qu'il avait fabriquee. */

  /** Une scene libre du quartier ou l'on est, hors champ, dans la bulle.

      ⚠️ On prefere la MEILLEURE (`valeur` : la place publique avant le
      trottoir), et on ne reprend pas celle d'un artiste deja installe — deux
      numeros a trois tuiles l'un de l'autre ne font pas deux spectacles, ils
      font une cohue, et leurs deux cercles se disputent les memes passants. */
  function sceneLibre(zone) {
    const scenes = (B.defs.carte && B.defs.carte.scenes) || [];
    if (!scenes.length || !zone) return null;
    const ecart = (B.defs.pietons.spectacle && B.defs.pietons.spectacle.rayon_px) || 46;
    let meilleure = null, valeurMax = -1;
    for (const s of scenes) {
      if (s.district !== zone.district) continue;
      const x = s.x * TT + 8, y = s.y * TT + 8;
      const d2 = dist2(x, y, B.joueur.x, B.joueur.y);
      if (d2 > BULLE_OUBLI * BULLE_OUBLI || d2 < 48 * 48) continue;
      if (visibleAEcran(x, y, 24)) continue;
      if (!placeLibre(x, y)) continue;
      let prise = false;
      for (const q of B.entites) {
        if (q.type !== 'pieton' || !q.vivant || SPECTACLES.indexOf(q.metier) < 0) continue;
        if (dist2(q.x, q.y, x, y) < (ecart * 2) * (ecart * 2)) { prise = true; break; }
      }
      if (prise) continue;
      // ⚠️ A valeur egale, la plus proche : on veut le spectacle du coin de
      // rue ou l'on est, pas celui de l'autre bout du quartier.
      const note = s.valeur * 1e9 - d2;
      if (note > valeurMax) { valeurMax = note; meilleure = { x: x, y: y }; }
    }
    return meilleure;
  }

  /** Les reglages du spectacle, lus dans la fiche (`pietons.SPECTACLE`).
      ⚠️ Jamais ecrits ici : « toujours entre 3 et 5 » est une demande de
      Martin, elle doit se relire — et se changer — dans la source de verite. */
  function reglesSpectacle() {
    return (B.defs.pietons && B.defs.pietons.spectacle) || {};
  }

  function artistes() {
    let n = 0;
    for (const q of B.entites) {
      if (q.type === 'pieton' && q.vivant && SPECTACLES.indexOf(q.metier) >= 0) n++;
    }
    return n;
  }

  /** Il s'installe : sa toune s'il en joue une, et son premier public.

      ⚠️ LE PUBLIC NAIT AVEC LUI, et c'est ce qui rend « toujours » vrai. Un
      artiste nait HORS CHAMP (`naitreLesSortes` le refuse a l'ecran) : on peut
      donc lui asseoir son minimum de badauds sur-le-champ, sans que personne
      ne les voie apparaitre. Sans ca, le premier joueur a tourner le coin
      trouvait un jongleur tout seul, et l'attroupement mettait le temps que
      des passants veuillent bien traverser la rue. */
  function ouvrirLeSpectacle(e) {
    if (e.metier === 'musicien') {
      // ⚠️ Sa toune est tiree A LA NAISSANCE et ne change plus : un musicien
      // qui change de morceau quand on revient le voir n'est plus un musicien,
      // c'est un poste de radio.
      const pieces = (B.defs.audio.musiques || []).filter(function (m) {
        return m.slug.indexOf('rue_') === 0;
      });
      if (pieces.length) e.toune = pieces[Math.floor(B.rng() * pieces.length)].slug;
    }
    const r = reglesSpectacle();
    const mini = r.minimum || 3;
    // ⚠️ `badauds`, pas `cercleEtChemin` : a l'ouverture on veut des gens
    // ASSIS, pas des gens en route. Compter les seconds faisait ouvrir le
    // numero devant deux personnes en attendant le troisieme — et le joueur
    // qui marchait droit vers l'artiste arrivait pile pendant ces trois
    // secondes-la.
    for (let i = 0; i < mini * 3 && badauds(e).length < mini; i++) {
      if (!garnirLeCercle(e, true)) break;
    }
  }

  /** Une place libre dans le cercle, autour de l'artiste. Rend null s'il n'y a
      pas de trottoir de libre — un cercle dans un mur n'est pas un cercle. */
  function placeDansLeCercle(e) {
    const r = reglesSpectacle();
    const rayon = r.cercle_px || 24, jeu = r.cercle_jeu_px || 8;
    for (let essai = 0; essai < 14; essai++) {
      const angle = B.rng() * Math.PI * 2;
      const d = rayon + B.rng() * jeu;
      const x = e.x + Math.cos(angle) * d, y = e.y + Math.sin(angle) * d;
      const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
      if (!Monde.marchablePieton(tx, ty) || Monde.estPassage(tx, ty)) continue;
      if (!placeLibre(x, y)) continue;
      return { x: x, y: y };
    }
    return null;
  }

  /** Qui regarde ce numero, en ce moment. */
  function badauds(e) {
    const r = reglesSpectacle();
    const portee = Math.max(r.rayon_px || 46, (r.cercle_px || 24) + (r.cercle_jeu_px || 8) + 16);
    const out = [];
    for (const q of pietonsAutour(e.x, e.y, portee + 24)) {
      if (q.attroupe === e && q.vivant && q.etat === 'arret') out.push(q);
    }
    return out;
  }

  /** Le cercle PLUS ceux qui marchent vers lui.

      ⚠️ C'est ce compte-la qui decide s'il faut recruter, et pas `badauds` :
      quelqu'un qui traverse la rue pour venir voir est deja invite. Sans lui,
      on en appelait un de plus a chaque image de `majSortes` tant que le
      premier n'etait pas arrive — six personnes convoquees pour trois places,
      et la rue se vidait autour. */
  function cercleEtChemin(e) {
    let n = badauds(e).length;
    for (const q of B.entites) {
      if (q.versLeCercle === e && q.vivant && q.etat === 'cap') n++;
    }
    return n;
  }

  /** Un spectateur de plus. `force` : on le FAIT NAITRE s'il n'y en a pas a
      recruter — sinon « toujours 3 a 5 » redevient un voeu.

      ⚠️ On ne fait naitre personne SOUS LES YEUX DU JOUEUR : la place du
      cercle doit etre hors de l'ecran. Si elle ne l'est pas, on recrute plus
      loin et le badaud MARCHE jusqu'au cercle (`cap`) — quelques secondes, et
      c'est bien mieux qu'un corps qui se materialise a trois tuiles. */
  function garnirLeCercle(e, force) {
    const r = reglesSpectacle();
    const portee = r.rayon_px || 46;
    // 1. Le plus simple : quelqu'un passe a portee. On le prend.
    for (const q of pietonsAutour(e.x, e.y, portee)) {
      if (!recrutable(q, e)) continue;
      if (!Monde.ligneLibre(q.x, q.y, e.x, e.y)) continue;
      return asseoir(q, e);
    }
    const place = placeDansLeCercle(e);
    if (!place) return false;
    // 2. A L'OUVERTURE, ON INSTALLE. ⚠️ Un artiste nait toujours hors champ
    // (`naitreLesSortes` le refuse a l'ecran), donc son cercle l'est aussi :
    // on peut y poser quelqu'un qui passait plus loin sans que personne ne le
    // voie se deplacer. Sans ce raccourci, le premier joueur a tourner le coin
    // trouvait un jongleur tout seul — le public mettait les quatre secondes
    // qu'il faut pour traverser cent trente pixels a pied, et « toujours »
    // devenait « au bout d'un moment ».
    if (force) {
      // ⚠️ DANS TOUTE LA BULLE, pas seulement dans le coin. Sur cent trente
      // pixels a la ronde il n'y a souvent qu'une ou deux personnes de libres
      // — les autres regardent deja le numero d'a cote — et l'artiste ouvrait
      // devant une personne. On va chercher plus loin : ca ne coute rien (le
      // budget de la foule ne bouge pas, on DEPLACE quelqu'un) et personne ne
      // le voit, puisqu'on ne prend que ceux qui sont hors champ.
      for (const q of pietonsAutour(e.x, e.y, BULLE_OUBLI)) {
        if (!recrutable(q, e) || visibleAEcran(q.x, q.y, 16)) continue;
        q.x = place.x; q.y = place.y;
        ajouterA(grille, q);          // il a change de case : l'index doit le savoir
        return asseoir(q, e);
      }
    }
    // 3. Sinon il MARCHE jusqu'au cercle — quelques secondes, et c'est bien
    // mieux qu'un corps qui se materialise a trois tuiles du joueur.
    // ⚠️ SAUF A L'OUVERTURE : un badaud en chemin n'est pas un badaud assis, et
    // l'artiste ouvrirait devant deux personnes en attendant le troisieme.
    // Hors champ, on n'a pas a faire marcher qui que ce soit.
    if (!force) for (const q of pietonsAutour(e.x, e.y, portee * 3)) {
      if (!recrutable(q, e)) continue;
      q.etat = 'cap'; q.cap = { x: place.x, y: place.y }; q.capT = 0;
      q.versLeCercle = e;
      return true;
    }
    // 4. La rue est vide : il en NAIT un. Hors champ, toujours.
    // ⚠️ ET DANS LE BUDGET DE LA FOULE. Un badaud est un passant comme un
    // autre : le faire naitre hors du compte, c'est deux artistes qui ajoutent
    // dix personnes par-dessus le plafond du quartier. Quand le budget est
    // plein, il y a par definition du monde a recruter — les etapes 1 a 3
    // trouvent quelqu'un, et cette derniere ne sert plus a rien.
    if (foule() >= fouleVoulue()) return false;
    if (!force && visibleAEcran(place.x, place.y, 16)) return false;
    // ⚠️ JAMAIS QUELQU'UN QUI VIENT AVEC. `archetypeDeRue` peut rendre la mere,
    // et une mere fait naitre son petit avec elle : le badaud qu'on ajoutait
    // pour tenir le budget en ajoutait DEUX, et la foule passait le plafond du
    // quartier. Un spectateur est quelqu'un qui s'arrete, et quelqu'un qui
    // s'arrete ne traine pas un enfant par la main.
    let arch = archetypeDeRue(place.x, place.y);
    for (let essai = 0; essai < 6 && arch && arch.accompagne; essai++) {
      arch = archetypeDeRue(place.x, place.y);
    }
    if (!arch || arch.accompagne) return false;
    const ne = creerPieton(place.x, place.y, arch);
    if (!ne) return false;
    return asseoir(ne, e);
  }

  /** Peut-on l'arracher a ce qu'il fait pour le planter devant un numero ?

      ⚠️ `arret` AUSSI, pas seulement `flane` : un flaneur fait des pauses tout
      seul, et celui qui trainait deja a cote du jongleur restait le seul de la
      rue a ne pas le regarder. ⚠️ Et jamais quelqu'un qui a un METIER — le
      jogger a des ecouteurs, la contractuelle a un char a verbaliser, et un
      artiste ne va pas regarder le voisin.

      ⚠️ ET ON NE VOLE PAS LE PUBLIC DU VOISIN (`!q.attroupe`). C'etait permis,
      et ca ne se voyait pas : deux artistes naissent dans le meme quartier, le
      second n'a personne de libre a portee, alors il recrutait les trois
      badauds du premier — qui se retrouvait SEUL au milieu de sa scene, et n'en
      retrouvait plus jamais. Un numero sans personne, c'est exactement ce que
      Martin a signale ; le faire arriver a coups de regles neuves aurait ete
      une belle facon de ne rien reparer du tout. */
  function recrutable(q, e) {
    return q !== e && q.vivant && !q.metier && !q.personnage && !q.mission && !q.porteBut
      && !q.suit && !q.petit && !q.attroupe && !q.versLeCercle
      && (q.etat === 'flane' || q.etat === 'arret');
  }

  /** Il se plante et il regarde. Rend faux si le cercle est deja plein.

      ⚠️ LE MAXIMUM SE TIENT ICI, a l'unique endroit ou quelqu'un entre dans un
      cercle. `garnirLeCercle` comptait deja avant d'appeler du monde, mais
      celui qui MARCHE vers le cercle arrive plus tard — et s'il arrive apres
      que deux autres se soient assis, il faisait un sixieme. « Entre 3 et 5 »
      a deux bouts, et le second est aussi une demande de Martin : au-dela, on
      ne voit plus le numero, on voit un dos. */
  function asseoir(q, e) {
    const r = reglesSpectacle();
    if (badauds(e).length >= (r.maximum || 5)) {
      q.versLeCercle = null;
      if (q.etat === 'cap') { q.etat = 'flane'; q.cap = null; }
      return false;
    }
    const patience = r.patience_images || [420, 1080];
    q.etat = 'arret';
    q.attroupe = e;
    q.versLeCercle = null;
    q.cap = null;
    q.vx = 0; q.vy = 0;
    q.minuterie = patience[0] + Math.floor(B.rng() * Math.max(1, patience[1] - patience[0]));
    regarder(q, e.x - q.x, e.y - q.y);
    // ⚠️ Un badaud qui regarde un spectacle REGARDE : il temoigne mieux que le
    // meme passant qui marchait en pensant a autre chose. C'est ce qui fait de
    // l'attroupement l'endroit de la rue ou il ne faut pas sortir une arme.
    q.probaTemoin = Math.min(1, (q.probaTemoin || 0.3) + (r.temoin_bonus || 0.4));
    return true;
  }

  /** Il en a assez vu : il applaudit, laisse une piece, et s'en va. */
  function quitterLeSpectacle(q, e) {
    const r = reglesSpectacle();
    q.attroupe = null;
    if (!e || !e.vivant) return;
    if (B.rng() < (r.applaudit_chance || 0.5)) {
      const mots = paroles(e.metier).bravo;
      if (mots && mots.length) {
        bulle(q, mots[Math.floor(B.rng() * mots.length)], { duree: r.applaudit_images || 40 });
      }
    }
    // ⚠️ L'ARGENT CHANGE DE POCHE POUR DE VRAI, comme pour le pickpocket :
    // sinon le chapeau n'est qu'une animation, et fouiller l'artiste
    // rapporterait la meme chose qu'il ait joue ou non.
    if (q.argent > 0 && B.rng() < (r.piece_chance || 0.45)) {
      const piece = r.piece || [1, 5];
      const sou = Math.min(q.argent, piece[0] + Math.floor(B.rng() * Math.max(1, piece[1] - piece[0] + 1)));
      q.argent -= sou;
      e.argent += sou;
      e.chapeauT = r.applaudit_images || 40;
    }
  }

  /** Le numero, une fois par image de `majSortes`.

      ⚠️ C'est ICI que l'artiste existe. Les quatre partagent la meme routine
      parce qu'ils font la meme chose — un numero, et du monde autour — et que
      ce qui les distingue (les balles, les echasses, la guitare) est dans le
      SPRITE, pas dans le code. */
  function majSpectacle(e) {
    if (e.etat !== 'fige') { e.poseFixe = null; return; }
    const r = reglesSpectacle();
    const arrive = (r.cercle_px || 24) + (r.cercle_jeu_px || 8) + 6;
    for (const q of B.entites) {
      // Ceux qui sont partis d'eux-memes (leur minuterie est tombee) : on les
      // libere, ils applaudissent, et le cercle se regarnit a leur place.
      if (q.attroupe === e && (!q.vivant || q.etat !== 'arret')) quitterLeSpectacle(q, e);
      // Ceux qui MARCHENT vers le cercle : arrives, ils s'arretent et regardent.
      // ⚠️ Sans ce palier, ils poussaient dans l'artiste image apres image —
      // `cap` les ramene dedans, `demeler` les ressort. C'est la meme lecon que
      // le pickpocket a deja payee une fois.
      if (q.versLeCercle !== e) continue;
      if (!q.vivant || q.etat !== 'cap') { q.versLeCercle = null; continue; }
      if (Math.hypot(q.x - e.x, q.y - e.y) <= arrive) asseoir(q, e);
    }
    const vus = badauds(e);
    const attendus = cercleEtChemin(e);
    const mini = r.minimum || 3, maxi = r.maximum || 5;
    // ⚠️ ON APPELLE LA RELEVE AVANT QUE LA PLACE SE LIBERE. Un remplacant met
    // deux a quatre secondes a traverser la rue : attendre que le cercle tombe
    // a deux pour l'appeler, c'est deux secondes a deux — et « toujours entre
    // 3 et 5 » devient « la plupart du temps ». On compte donc ceux qui seront
    // ENCORE LA quand il arrivera, plus ceux qui sont deja en chemin.
    const releve = r.releve_images || 200;
    let tiennent = 0;
    for (const q of vus) if (q.minuterie > releve) tiennent++;
    if (attendus - vus.length + tiennent < mini) garnirLeCercle(e, false);
    // ⚠️ ET LE DERNIER NE PART PAS AVANT QUE LA RELEVE SOIT LA. C'est ce qui
    // fait la difference entre « presque toujours trois » et TOUJOURS : la
    // releve met deux a quatre secondes a traverser la rue, parfois n'arrive
    // jamais (une ruelle vide), et sans cette regle le cercle tombait a deux
    // une fois sur seize. Quelqu'un qui reste un peu plus longtemps parce
    // qu'ils ne sont plus que trois, c'est exactement ce que fait une vraie
    // foule — on ne laisse pas un artiste tout seul.
    //
    // ⚠️ **ON COMPTE LES PARTANTS, PAS LE CERCLE**, et c'est la correction du
    // 16 sept. 2026. La regle ne regardait personne tant qu'ils etaient
    // QUATRE (`vus.length <= mini`) — or `majSpectacle` ne tourne qu'une image
    // sur quinze, et deux minuteries peuvent tomber dans le meme intervalle. A
    // quatre, deux partants : le tour suivant trouvait le cercle a DEUX, et il
    // etait trop tard pour retenir qui que ce soit. Mesure du banc : trente et
    // une images a deux spectateurs sous les yeux du joueur. On retient donc
    // les partants les plus presses, un par un, jusqu'a ce que ceux qui restent
    // fassent le minimum — et pas un de plus : un badaud retenu pour rien est
    // un badaud qui ne rend jamais sa place.
    //
    // ⚠️ Et ce n'etait PAS un defaut de la carte, meme si c'est un changement
    // de carte qui l'a fait tomber : mesure a l'appui, le meme juge sur six
    // graines de partie passait sur quatre AVANT le changement (77, 79, 80, 82)
    // et sur quatre APRES (78, 79, 80, 81). Le cercle tenait par chance ; il
    // tient maintenant par construction.
    const sursis = r.sursis_images || 30;
    const partants = vus.filter(function (q) { return q.minuterie <= sursis; });
    partants.sort(function (a, b) { return a.minuterie - b.minuterie; });
    let retenus = 0;
    for (const q of partants) {
      if (vus.length - partants.length + retenus >= mini) break;
      q.minuterie += releve;
      retenus++;
    }
    // ⚠️ On n'en prend un de plus au-dela du minimum qu'a l'occasion : sans ce
    // frein, le cercle collait au maximum en permanence et la rue se vidait de
    // ses passants pour remplir quatre cercles.
    if (vus.length > mini && attendus < maxi && B.rng() < 0.2) garnirLeCercle(e, false);
    animerLArtiste(e, vus.length);
    if (e.chapeauT > 0) e.chapeauT -= 15;
  }

  /** Il BOUGE. ⚠️ Le defaut que Martin a vu, et le plus simple a dire :
      `imageDe` choisit son image d'apres la DISTANCE PARCOURUE, et un corps a
      `vitesse: 0` n'en parcourt aucune — il tombait donc sur l'image zero, la
      meme, toute la partie. Une image IMPOSEE (`poseFixe`, deja la pour le
      manteau de l'exhibitionniste) et un compteur : le numero tourne. */
  function animerLArtiste(e, combien) {
    const r = reglesSpectacle();
    const parPose = (r.images_par_pose && r.images_par_pose[e.metier]) || 20;
    const suite = (r.poses && r.poses[e.metier]) || [0, 1, 2, 3];
    // ⚠️ Le musicien gratte EN MESURE : son image vient du sequenceur, pas
    // d'un compteur invente par le dessin. Une main qui gratte a cote du temps
    // s'entend autant qu'elle se voit.
    if (e.metier === 'musicien' && e.toune && typeof Son !== 'undefined' && Son.Rue.jouee === e.toune) {
      const sur = Son.Rue.surLeTemps();
      e.poseFixe = sur < 0.34 ? 0 : (sur < 0.67 ? 1 : 2);
      return;
    }
    e.poseFixe = suite[Math.floor(e.t / Math.max(1, parPose)) % suite.length];
    // Le mime salue quand il a du monde ; seul, il fait son mur.
    if (e.metier === 'amuseur' && combien < 1 && e.poseFixe === 3) e.poseFixe = 1;
  }

  /** La musique de la rue, UNE FOIS PAR IMAGE.

      ⚠️ PAS dans `majSortes`, qui ne tourne qu'une image sur quinze. Deux
      raisons, et les deux s'entendent : le volume suit la DISTANCE, et un
      volume qui ne se recalcule que quatre fois par seconde saute par marches
      quand on marche vers le musicien ; surtout, `Son.Rue` se tait des que
      plus personne ne demande — a une demande sur quinze images, la toune
      s'arretait et repartait sans arret.

      ⚠️ Un seul musicien sonne a la fois — LE PLUS PROCHE. Dix musiciens
      feraient dix sequenceurs, et deux tounes a trente pixels l'une de l'autre
      ne font pas de la musique, elles font du bruit. On le cherche donc ici,
      une fois, plutot que de laisser chaque musicien se comparer aux autres. */
  function laMusiqueDeLaRue() {
    const j = B.joueur;
    if (!j || typeof Son === 'undefined' || B.interieur) return;
    let proche = null, dMin = Infinity;
    for (const q of B.entites) {
      if (q.type !== 'pieton' || q.metier !== 'musicien' || !q.vivant || !q.toune) continue;
      if (q.etat !== 'fige') continue;              // assomme, il ne joue plus
      const d = Math.hypot(q.x - j.x, q.y - j.y);
      if (d < dMin) { dMin = d; proche = q; }
    }
    if (proche) majMusique(proche, dMin);
  }

  /** Sa toune, et elle sort DE LUI : plus on s'approche, plus c'est fort. */
  function majMusique(e, d) {
    const j = B.joueur;
    const r = (B.defs.pietons && B.defs.pietons.musicien) || {};
    const portee = r.portee_px || 260, plein = r.plein_px || 40;
    if (d >= portee) return;
    const proche = d <= plein ? 1 : 1 - (d - plein) / (portee - plein);
    Son.Rue.demander(e.toune, proche * (r.volume === undefined ? 0.75 : r.volume));
    // Le titre, quand on s'arrete devant lui. ⚠️ Sans ca, cinq morceaux
    // differents et rien pour dire qu'ils le sont : on n'entend pas un
    // catalogue, on entend une toune.
    const pres = r.titre_px || 56;
    if (d < pres && !j.dansVehicule && !e.titreDit) {
      const def = (B.defs.audio.musiques || []).find(function (m) { return m.slug === e.toune; });
      if (def) Hud.message('\u266A ' + def.nom.toUpperCase(), r.titre_images || 180);
      e.titreDit = true;
    } else if (d > pres * 2) {
      // On s'en va : la prochaine fois qu'on revient, il redit ce qu'il joue.
      e.titreDit = false;
    }
  }

  /** Ce que chaque sorte fait, une fois par image.

      ⚠️ Le musicien et l'amuseur ATTIRENT — et un attroupement est une foule
      de temoins : faire un coup devant l'amuseur, c'est dix temoins d'un seul
      geste. Ce n'est pas du decor, c'est l'endroit de la rue ou il ne faut pas
      sortir une arme. */
  function majSortes() {
    if (B.interieur || B.t % 15 !== 0) return;
    for (const e of B.entites) {
      if (e.type !== 'pieton' || !e.vivant || e.etat === 'assomme') continue;
      // Passe ses heures, une sorte rentre — hors de l'ecran (le crieur, le camelot).
      // ⚠️ Les heures se lisent sur l'ARCHETYPE : une sorte ne les porte pas sur elle.
      const sorte = SORTES.indexOf(e.arch) >= 0 ? archetype(e.arch) : null;
      if (sorte && sorte.heures && !enService(sorte.heures)) { rentrerHorsChamp(e); continue; }
      // ⚠️ On aiguille sur le METIER, pas sur le slug : c'est le metier qui
      // est le crochet declare dans `pietons.py`, et c'est lui qui dit ce que
      // la sorte FAIT. Un slug ne dit que comment on l'appelle.
      if (SPECTACLES.indexOf(e.metier) >= 0) majSpectacle(e);
      else if (e.metier === 'exhibitionniste') majManteau(e);
      else if (e.metier === 'contractuelle') majContravention(e);
      else if (e.metier === 'touriste') majPhoto(e);
      else if (e.metier === 'ivrogne') majIvrogne(e);
      else if (e.metier === 'facteur') majTournee(e);
      else if (e.metier === 'crieur') majCrieur(e);
      else if (e.metier === 'laveur') majLaveur(e);
      else if (e.metier === 'pickpocket') majPickpocket(e);
      else if (e.metier === 'baigneur') majPlage(e);
      else if (e.metier === 'camelot') majCamelot(e);
      else if (e.metier === 'forain') majForain(e);
      else if (e.metier === 'mascotte') majMascotte(e);
    }
  }

  /** Il ouvre son manteau au passage de quelqu'un : on crie, on fuit. ⚠️ Et un
      agent qui le voit L'ARRETE, lui — la seule fois ou la police s'occupe de
      quelqu'un d'autre que le joueur. C'est un gag, et c'est ce gag qui la
      rend credible : elle n'existe pas que pour toi. */
  function majManteau(e) {
    if (e.manteauT > 0) { e.manteauT--; if (e.manteauT === 0) e.poseFixe = null; return; }
    const agent = pietonsAutour(e.x, e.y, 70).find(function (q) { return q.agent && q.vivant; });
    if (agent) {
      // Pris sur le fait : il detale, et l'agent le suit.
      e.etat = 'fuit'; e.menace = agent; e.minuterie = 600; e.cri = 90;
      agent.but = { x: e.x, y: e.y };
      return;
    }
    // ⚠️ `arret` AUSSI, pas seulement `flane` — c'est la MEME lecon que pour
    // l'attroupement, et elle s'etait reglee a un seul endroit. Un flaneur fait
    // des pauses tout seul (une fois sur trois, `majPieton`) : celle qui
    // s'arretait pile devant lui etait la seule de la rue a ne rien voir, et il
    // attendait qu'elle reparte pour ouvrir son manteau a quelqu'un d'autre.
    const proche = pietonsAutour(e.x, e.y, 40).find(function (q) {
      return q !== e && q.vivant && !q.metier && (q.etat === 'flane' || q.etat === 'arret');
    });
    if (!proche || !Monde.ligneLibre(e.x, e.y, proche.x, proche.y)) return;
    e.manteauT = 90;
    e.poseFixe = 1;                            // la deuxieme image : le manteau OUVERT
    e.vx = 0; e.vy = 0;
    regarder(e, proche.x - e.x, proche.y - e.y);
    proche.etat = 'fuit'; proche.menace = e; proche.minuterie = 240; proche.cri = 120;
    bulle(proche, '!');
  }

  /** Les mots d'une sorte, lus dans la fiche. ⚠️ Jamais ecrits ici : voir
      `pietons.PAROLES`. Un mot en dur dans le JS est un mot que personne ne
      peut relire depuis la source de verite. */
  function paroles(metier) {
    const p = B.defs.pietons.paroles;
    return (p && p[metier]) || {};
  }

  //: Jusqu'ou une sorte va chercher ce qui l'interesse (un char mal gare, une
  //: porte a desservir), en pixels.
  const PORTEE_SORTE = 150;

  /** Le char mal gare le plus proche qui n'a pas encore sa contravention.

      ⚠️ La regle du mal-gare est celle de `Missions.malGare` — la MEME que
      celle de la fourriere, pas une deuxieme ecrite ici. Deux regles qui
      disent « mal gare » se contrediraient le jour ou l'une bouge, et le
      joueur verrait une contravention sur un char que personne ne remorque. */
  function charAVerbaliser(e) {
    let meilleur = null, dMin = PORTEE_SORTE * PORTEE_SORTE;
    for (const v of B.entites) {
      if (v.type !== 'vehicule' || v.contravention || !v.laisse) continue;
      const d = dist2(v.x, v.y, e.x, e.y);
      if (d >= dMin || !Missions.malGare(v)) continue;
      dMin = d; meilleur = v;
    }
    return meilleur;
  }

  /** Elle verbalise. ⚠️ C'est elle qui rend « mal gare » VISIBLE : jusqu'ici
      un message du HUD annoncait la remorqueuse, et rien, dans la rue, ne
      disait pourquoi le char allait disparaitre. Un avertissement qu'on lit
      sans voir personne l'ecrire se retient moins bien qu'une femme en
      uniforme plantee devant son capot. */
  function majContravention(e) {
    if (e.ticketT > 0) {
      e.ticketT -= 15;
      if (e.ticketT <= 0) { e.ticketT = 0; e.etat = 'flane'; e.cap = null; }
      return;
    }
    if (e.etat !== 'flane' && e.etat !== 'cap') return;
    const v = charAVerbaliser(e);
    if (!v) { if (e.etat === 'cap') { e.etat = 'flane'; e.cap = null; } return; }
    if (Math.hypot(v.x - e.x, v.y - e.y) > 22) {
      e.etat = 'cap'; e.cap = { x: v.x, y: v.y }; e.capT = 0;
      return;
    }
    e.etat = 'arret'; e.minuterie = 150; e.cap = null;
    e.ticketT = 150; e.vx = 0; e.vy = 0;
    regarder(e, v.x - e.x, v.y - e.y);
    v.contravention = (v.contravention || 0) + 1;
    bulle(e, paroles('contractuelle').verbalise, { duree: 150 });
    papier(v.x, v.y);
    if (visibleAEcran(v.x, v.y, 60)) {
      Hud.message((paroles('contractuelle').verbalise || '') + ' — ' + v.def.nom.toUpperCase(), 180);
    }
  }

  /** Le papillon blanc sous l'essuie-glace. */
  function papier(x, y) {
    for (let i = 0; i < 4; i++) {
      particule(x + (B.rng() - 0.5) * 6, y - 2, (B.rng() - 0.5) * 0.5, -0.3 - B.rng() * 0.3,
                30 + B.rng() * 20, '#ffffff', 2, 0.04);
    }
  }

  /** Il leve la tete devant une vitrine et il photographie.

      ⚠️ Son interet n'est pas le flash : c'est qu'il REGARDE. `temoin: 1.0`
      dans la fiche — le seul de la ville — donc faire un coup devant lui,
      c'est se faire voir a coup sur. Et il est lent : on ne le seme pas en
      marchant. */
  function majPhoto(e) {
    if (e.repos > 0) { e.repos -= 15; return; }
    if (e.etat !== 'flane') return;
    const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
    let vitrine = null;
    for (let dy = -3; dy <= -1 && !vitrine; dy++) {
      for (let dx = -1; dx <= 1; dx++) {
        if (Monde.glyphe(tx + dx, ty + dy) === 'W') { vitrine = true; break; }
      }
    }
    if (!vitrine) return;
    e.etat = 'arret'; e.minuterie = 120; e.vx = 0; e.vy = 0;
    e.face = 'haut';
    e.repos = 600;
    flash(e.x, e.y - 8);
  }

  function flash(x, y) {
    for (let i = 0; i < 10; i++) {
      const a = B.rng() * Math.PI * 2, v = 0.3 + B.rng() * 0.9;
      particule(x, y, Math.cos(a) * v, Math.sin(a) * v * 0.6, 8 + B.rng() * 6, '#ffffff', 2, 0);
    }
  }

  /** Il zigzague, il tombe tout seul, il insulte la rue. ⚠️ Et il NE FUIT PAS
      (voir `alerter`) : c'est le seul de la ville, et c'est ce qui le rend
      dangereux pour lui-meme. Une rue ou tout le monde detale de la meme
      facon n'a qu'une reaction. */
  function majIvrogne(e) {
    if (e.etat !== 'flane') return;
    if (e.fetard) chicaner(e);
    if (e.etat !== 'flane') return;
    // ⚠️ UN COMPTE A SOI, jamais `e.t % 60`. `majSortes` ne tourne qu'une image
    // sur quinze et `e.t` compte depuis la NAISSANCE : les deux ne tombent
    // ensemble que si l'on est ne sur un multiple de quinze. Un ivrogne ne du
    // mauvais pied n'aurait jamais trebuche de sa vie — et rien ne l'aurait
    // dit, parce que « il tombe rarement » et « il ne tombe jamais » se
    // ressemblent beaucoup.
    e.soulT = (e.soulT || 0) + 15;
    if (e.soulT < 60) return;
    e.soulT = 0;
    const chute = B.defs.pietons.reactions.ivrogne_chute;
    if (B.rng() < (chute === undefined ? 0.06 : chute)) {
      // Il tombe. Personne ne l'a touche.
      e.etat = 'assomme';
      e.minuterie = 120 + Math.floor(B.rng() * 180);
      poussiere(e.x, e.y, 4);
      return;
    }
    // Le fetard du last call CHANTE au lieu d'insulter : a l'empreinte du fetard
    // et de l'instant, pas au de — ce qu'il chante ne change rien au jeu.
    const lc = e.fetard && B.defs.nuit && B.defs.nuit.last_call;
    if (lc) {
      const h = hash2(e.id * 7919 + B.t, 0x1A57C);
      if (h % 1000 < lc.chante * 1000) bulle(e, lc.chansons[(h >>> 10) % lc.chansons.length], { duree: 120 });
      return;
    }
    const mots = paroles('ivrogne').insultes;
    if (mots && mots.length && B.rng() < 0.14) {
      bulle(e, mots[Math.floor(B.rng() * mots.length)], { duree: 90 });
    }
  }

  /** **LA CHICANE** : on frôle un fetard du last call, il se retourne. Une fois
      par fetard ; une part d'entre eux passe aux poings (`attaque_joueur`, comme
      une Cravate sur son territoire). A l'empreinte du fetard, jamais au de. */
  function chicaner(e) {
    const c = B.defs.nuit && B.defs.nuit.last_call && B.defs.nuit.last_call.chicane, j = B.joueur;
    if (!c || e.chicane || !j || !j.vivant || j.dansVehicule || B.cinema) return;
    if (dist2(e.x, e.y, j.x, j.y) > c.portee_px * c.portee_px) return;
    e.chicane = true;
    const h = hash2(e.id, 0xC41CA);
    regarder(e, j.x - e.x, j.y - e.y);
    bulle(e, c.mots[h % c.mots.length], { duree: 100 });
    if ((h >>> 10) % 1000 < c.part * 1000) { e.etat = 'attaque_joueur'; e.cri = 90; }
  }

  /** **LE LAST CALL** (la nuit a ses habitudes) : a 3 h, chaque bar de la bulle
      (`nuit.last_call.bars`) laisse sortir sa grappe de fetards — une fois par bar
      et par nuit. Nes DANS LA PORTE, qui s'ouvre : comme le flaneur qui sort de
      chez lui, on les voit sortir, on ne les voit pas apparaitre. ⚠️ Combien, a
      l'empreinte du jour et du bar : aucun de du jeu ne sert a les compter. */
  function naitreLeLastCall() {
    const lc = B.defs.nuit && B.defs.nuit.last_call, p = B.partie, j = B.joueur;
    if (!lc || !p || !j || B.interieur) return 0;
    if (p.heure < lc.heure || p.heure >= lc.jusqu_a) return 0;
    const arch = archetype('ivrogne');
    if (!arch) return 0;
    const faits = B.lastCall || (B.lastCall = {});
    let nes = 0;
    lc.bars.forEach(function (bar, k) {
      const cle = p.jour + ':' + k;
      if (faits[cle]) return;
      const x = bar.x * TT + 8, y = bar.y * TT + 8;
      if (dist2(x, y, j.x, j.y) > lc.portee_px * lc.portee_px) return;
      if (!Monde.marchablePieton(bar.x, bar.y)) return;
      faits[cle] = true;
      const n = lc.fetards[0] + hash2(p.jour, k * 131 + 7) % (lc.fetards[1] - lc.fetards[0] + 1);
      Monde.ouvrirPorte(bar.porte[0], bar.porte[1]);
      for (let i = 0; i < n; i++) {
        // En grappe devant la porte : un pas de cote chacun, pas tous sur la meme tuile.
        const dx = ((i % 3) - 1) * 10, dy = Math.floor(i / 3) * 8;
        const e = creerPieton(x + dx, y + dy, arch);
        if (!e) continue;
        e.fetard = true;
        e.etat = 'flane';
        e.sortie = { x: bar.porte[0], y: bar.porte[1], t: 0 };
        nes++;
      }
    });
    if (nes) indexer();
    return nes;
  }

  /** La porte la plus proche qu'il n'a pas encore desservie. */
  function prochainePorte(e) {
    const carte = Monde.carte;
    if (!carte || !carte.portesFermees.length) return null;
    const faites = e.tournee || (e.tournee = []);
    let meilleure = null, dMin = PORTEE_SORTE * PORTEE_SORTE;
    for (const porte of carte.portesFermees) {
      const x = porte.x * TT + 8, y = (porte.y + 1) * TT + 8;
      const d = dist2(x, y, e.x, e.y);
      if (d >= dMin || faites.indexOf(porte) >= 0) continue;
      if (Monde.glyphe(porte.x, porte.y) !== porte.glyphe) continue;   // rasee (chantier)
      if (!Monde.marchablePieton(porte.x, porte.y + 1)) continue;
      dMin = d; meilleure = porte;
    }
    return meilleure;
  }

  /** Sa tournee : d'une porte a l'autre. ⚠️ Il N'ENTRE PAS, et c'est toute la
      difference avec le flaneur qui rentre chez lui — celui-la disparait
      derriere le battant, le facteur reste dehors et passe au suivant. */
  function majTournee(e) {
    if (e.livreT > 0) {
      e.livreT -= 15;
      if (e.livreT <= 0) { e.livreT = 0; e.etat = 'flane'; }
      return;
    }
    if (e.etat === 'cap' && e.cap && e.porteTournee) {
      if (Math.hypot(e.cap.x - e.x, e.cap.y - e.y) > 14) return;
      Monde.ouvrirPorte(e.porteTournee.x, e.porteTournee.y);
      e.tournee.push(e.porteTournee);
      e.porteTournee = null; e.cap = null;
      e.etat = 'arret'; e.minuterie = 80; e.vx = 0; e.vy = 0;
      e.face = 'haut';
      e.livreT = 80;
      bulle(e, paroles('facteur').livre, { duree: 80 });
      return;
    }
    if (e.etat !== 'flane') return;
    e.tourneeT = (e.tourneeT || 0) + 15;      // un compte a soi : voir `majIvrogne`
    if (e.tourneeT < 45) return;
    e.tourneeT = 0;
    const porte = prochainePorte(e);
    if (!porte) { if (e.tournee && e.tournee.length > 6) e.tournee.length = 0; return; }
    e.porteTournee = porte;
    e.cap = { x: porte.x * TT + 8, y: (porte.y + 1) * TT + 8 };
    e.capT = 0; e.etat = 'cap';
  }

  /** Qui a fini sa journee s'en va — HORS DE L'ECRAN, jamais sous nos yeux. Par
      `entre` (retire a l'image suivante) : on est dans la boucle de `majSortes`. */
  function rentrerHorsChamp(e) {
    if (visibleAEcran(e.x, e.y, 40)) return;
    e.etat = 'entre'; e.minuterie = 1; e.vx = 0; e.vy = 0;
  }

  /** Le perron le plus proche qu'il n'a pas encore servi — d'abord dans une rue ou
      l'on habite : le Clairon se lit au dejeuner, pas au comptoir. */
  function prochainPerron(e) {
    const carte = Monde.carte;
    if (!carte || !carte.portesFermees.length) return null;
    const faites = e.tournee || (e.tournee = []);
    const portee = PORTEE_SORTE * PORTEE_SORTE;
    let chez = null, dChez = portee, autre = null, dAutre = portee;
    for (const porte of carte.portesFermees) {
      const px = porte.x * TT + 8, py = (porte.y + 1) * TT + 8;
      const d = dist2(px, py, e.x, e.y);
      if (d >= portee || faites.indexOf(porte) >= 0) continue;
      if (Monde.glyphe(porte.x, porte.y) !== porte.glyphe) continue;   // rasee (chantier)
      if (!Monde.marchablePieton(porte.x, porte.y + 1)) continue;
      // ⚠️ Un perron qu'il VOIT : `cap` marche en ligne droite, et le premier camelot
      // restait dix secondes le nez contre le mur d'une cour, a viser la porte d'en face.
      if (!Monde.ligneLibre(e.x, e.y, px, py)) continue;
      if (Monde.usageA(porte.x, porte.y) === 'residentiel') { if (d < dChez) { dChez = d; chez = porte; } }
      else if (d < dAutre) { dAutre = d; autre = porte; }
    }
    return chez || autre;
  }

  /** **LE CAMELOT DU CLAIRON** (la nuit a ses habitudes). Il va de perron en perron
      et y LANCE le journal — un rouleau qui reste sur le seuil jusqu'a ce qu'on le
      rentre (`nuit.CAMELOT.rentre_a`). ⚠️ Il n'ouvre aucune porte : c'est toute la
      difference avec le facteur, qui fait battre les portes une a une. */
  function majCamelot(e) {
    // ⚠️ Un perron qu'il n'atteint pas (`cap` renonce au bout de dix secondes) se
    // RAYE de la tournee : sinon il le rechoisissait, le plus proche, sans fin.
    if (e.perron && (e.etat !== 'cap' || !e.cap)) { e.tournee.push(e.perron); e.perron = null; }
    if (e.lanceT > 0) {
      e.lanceT -= 15;
      if (e.lanceT <= 0) { e.lanceT = 0; e.etat = 'flane'; }
      return;
    }
    if (e.etat === 'cap' && e.cap && e.perron) {
      if (Math.hypot(e.cap.x - e.x, e.cap.y - e.y) > 18) return;
      const p = e.perron;
      poserLeJournal(p.x * TT + 8, (p.y + 1) * TT + 3);
      e.tournee.push(p);
      e.perron = null; e.cap = null;
      e.etat = 'arret'; e.minuterie = 20; e.vx = 0; e.vy = 0;
      e.face = 'haut';
      e.lanceT = 20;
      const c = B.defs.nuit && B.defs.nuit.camelot;
      if (c && hash2(e.id, e.tournee.length) % 1000 < c.parle * 1000) bulle(e, paroles('camelot').lance, { duree: 70 });
      return;
    }
    if (e.etat !== 'flane') return;
    const p = prochainPerron(e);
    if (!p) { if (e.tournee && e.tournee.length > 12) e.tournee.length = 0; return; }
    e.perron = p;
    e.cap = { x: p.x * TT + 8, y: (p.y + 1) * TT + 8 };
    e.capT = 0; e.etat = 'cap';
  }

  /** Le journal sur le perron : un decalque, qui porte son JOUR — rentre a l'heure
      dite (`rentrerLesJournaux`). Aucun de : sa pose se lit a sa place. */
  function poserLeJournal(x, y) {
    if (B.decals.length >= MAX_DECALS) B.decals.shift();
    B.decals.push({ x: x, y: y, type: 'journal', v: hash2(Math.floor(x), Math.floor(y)) % 4,
                    jour: B.partie ? B.partie.jour : 0 });
  }

  /** On a rentre le journal : passe l'heure (`rentre_a`), ou le lendemain, ceux
      qu'on ne voit pas s'en vont. Sous nos yeux, il attend qu'on regarde ailleurs. */
  function rentrerLesJournaux() {
    const c = B.defs.nuit && B.defs.nuit.camelot, p = B.partie;
    if (!c || !p || !B.decals.length) return;
    // Il passe avant 6 h 30 : a partir de `rentre_a`, tout journal du jour est rentre.
    const tard = p.heure >= c.rentre_a;
    for (let i = B.decals.length - 1; i >= 0; i--) {
      const d = B.decals[i];
      if (d.type !== 'journal') continue;
      if (!(tard || d.jour !== p.jour) || visibleAEcran(d.x, d.y, 16)) continue;
      B.decals.splice(i, 1);
    }
  }

  /** IL HURLE CE QUE TU AS FAIT HIER.

      ⚠️ C'est tout l'interet du personnage, et ca ne coute rien : la manchette
      du Clairon existe deja (`journal.py` compare les statistiques du jour a
      celles d'hier), elle est calculee au reveil et gardee dans la partie. Le
      crieur ne fait que la dire tout haut, au coin de la rue. Tuer trois
      personnes un soir, c'est l'entendre le lendemain matin.

      ⚠️ Il LIT `derniereManchette`, il ne la recalcule pas : `manchetteDuJour`
      remet le compteur d'hier a zero au passage. Un crieur qui l'appellerait
      effacerait la memoire du journal a chaque cri. */
  function majCrieur(e) {
    if (e.crieT > 0) { e.crieT -= 15; return; }
    if (e.etat !== 'fige') return;
    const m = B.partie && B.partie.derniereManchette;
    const mot = (m && m.titre) || paroles('crieur').appel;
    if (!mot) return;
    e.crieT = 300;
    bulle(e, mot, { duree: 210 });
  }

  /** Le char arrete le plus proche : c'est la que le laveur travaille. */
  function charArrete(e) {
    let meilleur = null, dMin = PORTEE_SORTE * PORTEE_SORTE;
    for (const v of B.entites) {
      if (v.type !== 'vehicule' || v.etat === 'epave' || v.lave) continue;
      if (Math.abs(v.vitesse) > 0.25) continue;                 // il roule : pas touche
      if (!Monde.estRoute(Math.floor(v.x / TT), Math.floor(v.y / TT))) continue;
      const d = dist2(v.x, v.y, e.x, e.y);
      if (d < dMin) { dMin = d; meilleur = v; }
    }
    return meilleur;
  }

  /** IL TRAVAILLE AU FEU ROUGE.

      ⚠️ C'est son crochet, et c'est la meme horloge que les feux pour pietons :
      un char ARRETE, c'est quinze secondes de travail, et un char qui repart le
      laisse le chiffon en l'air. Sans cette contrainte, il laverait des chars
      en pleine rue a soixante kilometres a l'heure — ce serait une animation,
      pas un metier. */
  function majLaveur(e) {
    if (e.laveT > 0) {
      e.laveT -= 15;
      // Le feu passe au vert, le char s'en va : on n'a pas fini, tant pis.
      if (e.laveT <= 0 || !e.charLave || Math.abs(e.charLave.vitesse) > 0.4) {
        if (e.charLave) e.charLave.lave = true;
        e.laveT = 0; e.charLave = null; e.etat = 'flane'; e.repos = 600;
      } else if (e.laveT % 30 === 0) {
        mousse(e.charLave.x, e.charLave.y - 4);
      }
      return;
    }
    if (e.repos > 0) { e.repos -= 15; return; }
    if (e.etat !== 'flane' && e.etat !== 'cap') return;
    const v = charArrete(e);
    if (!v) { if (e.etat === 'cap') { e.etat = 'flane'; e.cap = null; } return; }
    if (Math.hypot(v.x - e.x, v.y - e.y) > 24) {
      e.etat = 'cap'; e.cap = { x: v.x, y: v.y }; e.capT = 0;
      return;
    }
    e.etat = 'arret'; e.minuterie = 240; e.cap = null;
    e.laveT = 240; e.charLave = v; e.vx = 0; e.vy = 0;
    regarder(e, v.x - e.x, v.y - e.y);
    bulle(e, paroles('laveur').propose, { duree: 150 });
    mousse(v.x, v.y - 4);
  }

  /** L'eau savonneuse sur le pare-brise. */
  function mousse(x, y) {
    for (let i = 0; i < 5; i++) {
      const a = B.rng() * Math.PI * 2, v = 0.2 + B.rng() * 0.7;
      particule(x, y, Math.cos(a) * v, Math.sin(a) * v * 0.6, 14 + B.rng() * 8, '#eef6fb', 1, 0.03);
    }
  }

  /** IL VOLE LES AUTRES — la ville coupable d'elle-meme.

      ⚠️ Un crime que TU n'as pas commis, une victime qui crie, et un agent qui
      arrete quelqu'un d'autre que toi. C'est le deuxieme apres l'homme au
      manteau, et les deux ensemble disent la meme chose : la police n'existe
      pas que pour le joueur.

      ⚠️ Il vole DANS LE DOS, comme le joueur le fait (`pickpocket_dos_degres`
      dans la fiche) : de face, on se ferait prendre. Et la victime perd son
      argent POUR DE VRAI — sinon le vol n'est qu'une animation, et fouiller le
      corps d'un vole rapporterait quand meme. */
  function majPickpocket(e) {
    if (e.voleT > 0) { e.voleT -= 15; if (e.voleT <= 0) { e.voleT = 0; e.etat = 'flane'; } return; }
    if (e.repos > 0) { e.repos -= 15; return; }
    // Un agent a cote : on ne travaille pas sous le nez de la police.
    if (pietonsAutour(e.x, e.y, 80).some(function (q) { return q.agent && q.vivant; })) {
      if (e.etat === 'cap') { e.etat = 'flane'; e.cap = null; }
      e.repos = 300;
      return;
    }
    if (e.etat !== 'flane' && e.etat !== 'cap') return;
    const cible = pietonsAutour(e.x, e.y, PORTEE_SORTE).find(function (q) {
      return q !== e && q.vivant && !q.metier && !q.agent && !q.intouchable
        && q.argent > 0 && (q.etat === 'flane' || q.etat === 'arret');
    });
    if (!cible) { if (e.etat === 'cap') { e.etat = 'flane'; e.cap = null; } return; }
    // ⚠️ DIX-HUIT PIXELS, pas quatorze : `demeler` ecarte deux corps de dix
    // pixels de rayon, et la victime marche. A quatorze, il restait a treize ou
    // quinze pendant trois cents images sans jamais passer sous la barre — il
    // suivait sa victime sans jamais la voler, et de loin ca ressemblait a un
    // vol qui n'arrive pas.
    if (Math.hypot(cible.x - e.x, cible.y - e.y) > 18) {
      e.etat = 'cap'; e.cap = { x: cible.x, y: cible.y }; e.capT = 0; e.capVite = true;
      return;
    }
    e.capVite = false;
    // ⚠️ DANS LE DOS : le meme angle que pour le joueur, lu dans la fiche.
    const dos = B.defs.pietons.reactions.pickpocket_dos_degres * Math.PI / 180;
    const vers = Math.atan2(e.y - cible.y, e.x - cible.x);
    const regarde = { bas: Math.PI / 2, haut: -Math.PI / 2, gauche: Math.PI, droite: 0 }[cible.face] || 0;
    let ecart = vers - regarde;
    while (ecart > Math.PI) ecart -= 2 * Math.PI;
    while (ecart < -Math.PI) ecart += 2 * Math.PI;
    if (Math.abs(ecart) < Math.PI - dos / 2) return;            // il me verrait
    e.argent = (e.argent || 0) + cible.argent;
    cible.argent = 0;
    e.voleT = 90; e.etat = 'arret'; e.minuterie = 90; e.cap = null; e.repos = 900;
    poussiere(cible.x, cible.y - 4, 3);
    // La victime s'en apercoit : elle crie, elle fuit, et c'est LUI la menace.
    cible.etat = 'fuit'; cible.menace = e; cible.minuterie = 300; cible.cri = 120;
    bulle(cible, paroles('pickpocket').au_voleur, { duree: 120 });
    // ⚠️ Et un agent qui passe l'arrete, LUI : c'est le meme gag que l'homme
    // au manteau, et c'est lui qui rend la police credible.
    const agent = pietonsAutour(e.x, e.y, 120).find(function (q) { return q.agent && q.vivant; });
    if (agent) { e.etat = 'fuit'; e.menace = agent; e.minuterie = 600; e.cri = 90; agent.but = { x: e.x, y: e.y }; }
    // ⚠️ Et parfois, un passant qui a vu la scene de loin te confond (M12).
    else Police.crimeDAutrui('pickpocket', cible.x, cible.y, e);
  }

  /** Il ouvre la portiere et il s'en va avec. ⚠️ Le voleur DISPARAIT dans le
      char : le jeu ne sait pas dessiner quelqu'un au volant d'un char du
      trafic, et un conducteur invisible est exactement ce que le trafic est
      deja. Ce qui reste, c'est un char qui demarre tout seul sous les yeux de
      la rue — et c'est ca qu'on voulait voir.

      ⚠️ **Sauf sur un DEUX-ROUES** (retour de Martin : « un voleur qui vole
      une moto n'apparait pas dessus »). Un deux-roues du trafic MONTRE son
      pilote (`Vehicules.cavalierDe` lit `v.pilote`) : sans lui, la moto volee
      partait vide, ce que le trafic ne fait jamais. C'est le voleur qui monte
      en selle, avec SES couleurs — et c'est lui qui en descend si le joueur
      la lui prend (`Vehicules.monter`). */
  function emporterLeChar(e, v) {
    const f = B.defs.pietons.vol_de_char;
    v.conducteur = 'trafic';
    // ⚠️ IL PART D'UN STATIONNEMENT, PAS D'UN RAIL : tant qu'il n'a pas
    // rejoint une tuile de la voirie, `avancer` (collision aux tuiles) le
    // conduit au lieu du saut en ligne droite du trafic sur rails — sinon
    // il traverse tout ce qui se trouve entre sa place et la rue (`maj`,
    // Vehicules).
    v.horsReseau = true;
    v.etat = 'roule';
    v.vole = true;
    const selle = SPRITES[v.sprite] && SPRITES[v.sprite].selle;
    if (selle) v.pilote = { swaps: e.swaps, tenue: e.tenue || null };
    v.sens = Monde.fleche(Math.floor(v.x / TT), Math.floor(v.y / TT)) || v.sens;
    v.alarme = 0;
    // ⚠️ La rue le voit partir — et c'est LUI la menace, pas le joueur. On
    // n'appelle PAS `Police.signalerCrime` : la police du jeu est centree sur
    // le joueur, et signaler le geste d'un autre lui mettrait une etoile.
    const vu = pietonsAutour(v.x, v.y, 120).filter(function (q) { return q !== e && q.vivant && !q.metier; });
    if (vu.length) bulle(vu[0], paroles('pickpocket').au_voleur, { duree: 120 });
    alerter(v.x, v.y, e, f.peur);
    // ⚠️ Et parfois, c'est toi qu'on a vu partir avec (M12) : le crime d'autrui.
    Police.crimeDAutrui('vol_vehicule', v.x, v.y, e);
    Son.SFX.porte('vehicule');
    retirer(e);
  }

  /** **Un vol de char sous tes yeux.** ⚠️ Il se voit, ou il n'a pas lieu : un
      vol hors champ est du travail qu'on fait pour personne. On ne le tente
      donc que sur un char A L'ECRAN, avec un passant ordinaire a portee.

      ⚠️ Le tirage se fait a l'EMPREINTE de la minute, jamais au de du jeu :
      c'est la lecon du pilote des deux-roues et celle du char en panne — un
      de pris ici decale tout ce qui suit, et quatre juges tombent. */
  function majVolDeChar() {
    const f = B.defs.pietons && B.defs.pietons.vol_de_char;
    if (!f || !B.joueur || B.interieur || !B.partie) return 0;
    const minute = Math.floor(B.partie.heure * 24 * 60);
    if (B.volMinute === minute) return 0;
    B.volMinute = minute;
    if (hash2(B.partie.jour * 1441 + minute, 0x5C0F) / 4294967296 >= f.chance_par_minute) return 0;
    if (B.entites.some(function (q) { return q.etat === 'vole_un_char'; })) return 0;
    // Un char gare, a portee de vue, que personne ne conduit — et pas celui du
    // joueur : se faire voler le sien sans un mot serait une punition, pas une
    // scene de rue.
    const chars = B.entites.filter(function (q) {
      return q.type === 'vehicule' && !q.conducteur && q.etat !== 'epave' && !q.mission
        // ⚠️ Ni celui du joueur, ni celui qu'il a LAISSE quelque part : un char
        // abandonne appartient a la fourriere, pas aux voleurs — deux systemes
        // qui se disputent le meme char, c'est l'un des deux qui ment.
        && q !== B.joueur.dernierVehicule && !q.laisse && !(q.panneT > 0)
        // ⚠️ Ni un char qui ATTEND le joueur a sa place (le camion de creme glacee, celui
        // d'asphalte : `resteGare`) — il n'y en a qu'un, et vole il ne revient pas.
        && !q.resteGare
        // ⚠️ **Ni une COQUE** (retour de Martin, capture a l'appui : « un
        // bateau sur la route ?? »). Une chaloupe amarree est `stationne` comme
        // une auto garee, et pour un passant du quai c'etait le premier char a
        // l'ecran : il l'emportait, le trafic la prenait en main, et le trafic
        // roule sur des rails sans lire une tuile — elle montait sur la voie la
        // plus proche et faisait sa tournee. On vole un char, pas un bateau.
        && !(q.def && q.def.eau)
        && dist2(q.x, q.y, B.joueur.x, B.joueur.y) < f.rayon_px * f.rayon_px
        && visibleAEcran(q.x, q.y, 0);
    });
    if (!chars.length) return 0;
    const char = chars[0];
    // Le voleur : un passant ORDINAIRE a portee — pas un agent, pas un
    // marchand, pas quelqu'un de l'histoire.
    const voleur = pietonsAutour(char.x, char.y, f.rayon_px).find(function (q) {
      return q.vivant && !q.metier && !q.gang && !q.personnage && !q.mission
        && !q.intouchable && q.etat === 'flane';
    });
    if (!voleur) return 0;
    voleur.etat = 'vole_un_char';
    voleur.charVise = char;
    voleur.voleChar = f.marche_images;
    return 1;
  }

  // --- Les betes : la vie qui n'est pas humaine ----------------------------
  //: ⚠️ **ELLES NE COMPTENT POUR RIEN.** Ni temoins, ni victimes, ni foule :
  //: `type: 'bete'` n'est ni `pieton` ni `joueur`, donc l'arc de melee ne les
  //: voit pas (`arcDeMelee` ne prend que ces deux-la), `alerter` et
  //: `pietonsAutour` non plus, `foule()` ne les compte pas, et rien de ce qui
  //: fait un crime ne peut les atteindre. Un goeland qu'on pourrait tuer serait
  //: une CIBLE — et une cible demande un score, un crime, un juge. Un goeland
  //: qui s'envole est un decor qui a peur de vous.
  //:
  //: ⚠️ Et elles partent AVANT qu'on les touche : leur distance de fuite est
  //: plus grande que la portee de tout ce qui pourrait les atteindre. C'est ce
  //: qui evite d'avoir a repondre a « que se passe-t-il si je lui roule dessus » :
  //: on n'y arrive pas.

  //: ⚠️ **ELLES NE SONT PAS DANS `B.entites`, et c'est la seule facon de tenir
  //: la promesse de la fiche.** Les sortir de l'index des gens ne suffisait pas :
  //: mesure, un juge du trottoir qui compte un TAUX sur cent essais tombait de
  //: 75 % a 2 % rien qu'en les laissant vivre dans la liste du monde — sans
  //: qu'aucune d'elles ne tire un seul de (verifie par attribution de pile). Une
  //: bete qui « ne compte pour rien » ne doit pas etre dans la liste de ce qui
  //: compte : ni parcourue, ni oubliee, ni demelee, ni indexee avec le reste.
  let idDeBete = 0;
  function betes() { if (!B.betes) B.betes = []; return B.betes; }

  /** Chacune chez soi : le goeland au bord de l'eau, le chat dans les ruelles.
      Sans ca ce ne sont pas deux betes, c'est deux dessins du meme animal. */
  function chezElle(espece, tx, ty) {
    if (!Monde.marchablePieton(tx, ty)) return false;
    if (espece === 'chat' || espece === 'raton') return Monde.glyphe(tx, ty) === 'x';   // la ruelle
    const g = Monde.glyphe(tx, ty);
    if (g !== 's' && g !== 'Q') return false;                            // le sable, le quai
    for (let d = 1; d <= 3; d++) {
      if (Monde.estEau(tx + d, ty) || Monde.estEau(tx - d, ty)
          || Monde.estEau(tx, ty + d) || Monde.estEau(tx, ty - d)) return true;
    }
    return false;
  }

  /** ⚠️ Elle naissent SANS TIRER UN DE : on balaie la bulle en anneaux de tuiles,
      du plus proche au plus loin, et la premiere case qui convient gagne. La
      lecon a ete payee trois fois cette semaine — la derniere fois, le
      pickpocket avait cesse de voler parce que des enfants naissaient au hasard. */
  function naitreLesBetes() {
    const f = B.defs.pietons && B.defs.pietons.betes;
    if (!f || !B.joueur || B.interieur) return 0;
    let nes = 0;
    // ⚠️ LA NUIT A SES HABITUDES : le raton ne sort que la nuit (`heures`), et la
    // nuit le goeland dort — il n'en nait plus (`goeland_dort`).
    const nuit = B.partie && Monde.estNuit(B.partie.heure);
    for (const espece of ['goeland', 'chat', 'raton']) {
      const fiche = f[espece];
      if (!fiche) continue;
      if (fiche.heures && !enService(fiche.heures)) continue;
      if (espece === 'goeland' && nuit && f.goeland_dort) continue;
      const deja = betes().filter(function (q) { return q.espece === espece; }).length;
      if (deja >= fiche.combien) continue;
      const place = placeDeBete(espece, f.rayon_px);
      if (!place) continue;
      betes().push({
        type: 'bete', espece: espece, decor: espece, x: place.x, y: place.y,
        r: 0, solide: false, id: ++idDeBete, t: 0,
        v: 0, humeur: 'pose', minuterie: 1, vx: 0, vy: 0, altitude: 0, fuite: 0,
      });
      nes++;
    }
    return nes;
  }

  function placeDeBete(espece, rayon) {
    const j = B.joueur, t = Math.floor(rayon / TT);
    const jx = Math.floor(j.x / TT), jy = Math.floor(j.y / TT);
    for (let d = 3; d <= t; d++) {
      for (let k = -d; k <= d; k++) {
        for (const [tx, ty] of [[jx + k, jy - d], [jx + k, jy + d], [jx - d, jy + k], [jx + d, jy + k]]) {
          if (!chezElle(espece, tx, ty)) continue;
          const x = tx * TT + 8, y = ty * TT + 8;
          if (dist2(x, y, j.x, j.y) > rayon * rayon) continue;
          if (visibleAEcran(x, y, 16)) continue;
          return { x: x, y: y };
        }
      }
    }
    return null;
  }

  /** Le raton qui sort de la poubelle qu'on fouille, et qui file a l'oppose du
      joueur (`interactions.js`). ⚠️ Il ne se pose pas : il PART. */
  function fairePartirUnRaton(x, y) {
    const f = B.defs.pietons && B.defs.pietons.betes, fiche = f && f.raton;
    if (!fiche || !B.joueur) return null;
    const e = {
      type: 'bete', espece: 'raton', decor: 'raton', x: x, y: y, r: 0, solide: false,
      id: ++idDeBete, t: 0, v: 0, humeur: 'pose', minuterie: 1, vx: 0, vy: 0, altitude: 0, fuite: 0, libre: true,
    };
    betes().push(e);
    sEnvoler(e, fiche, B.joueur);
    return e;
  }

  function oublier(e) {
    const i = betes().indexOf(e);
    if (i >= 0) B.betes.splice(i, 1);
  }

  /** Toutes les betes, une image. */
  // --- L'orignal de La Pointe -------------------------------------------------------------
  //: docs/jalons/l-orignal-de-la-pointe.md. Une bete rare et enorme sur les sentiers du bois de
  //: La Pointe (`carte.chemins_des_bois`), la nuit : il va au pas d'une tuile de sentier a une
  //: autre, se FIGE dans les phares d'un char qui vient vers lui, et ne bouge plus. Un coup de
  //: klaxon le fait fuir ; le frapper aussi (`Vehicules`, le char presque detruit).
  //:
  //: ⚠️ C'est un DECOR, pas une bete de `B.betes` : les betes sont hors de `B.entites` pour qu'aucun
  //: char ne les touche, et celle-ci, justement, on la frappe. Il tient l'index fixe a jour lui-meme
  //: a chaque pas (`deplacerOrignal`), comme la benne qu'on pousse.
  //:
  //: ⚠️ Ni sa venue ni ses pas ne tirent `B.rng()` : l'empreinte de la nuit (`orignalDeLaNuit`) et
  //: celle de ses pas (`hash2(id, pas)`). Et il ne nait qu'a l'approche du joueur, hors champ.

  function ficheOrignal() { return B.defs.pietons && B.defs.pietons.betes && B.defs.pietons.betes.orignal; }
  function cheminsDesBois() { return (Monde.carte && Monde.carte.def && Monde.carte.def.chemins_des_bois) || []; }

  /** La nuit en cours a-t-elle son orignal, et sur quelle tuile de sentier ? Une nuit appartient au
      jour ou elle commence. null sinon. */
  function orignalDeLaNuit() {
    const f = ficheOrignal(), c = cheminsDesBois(), p = B.partie;
    if (!f || !c.length || !p) return null;
    const nuit = p.heure >= f.heures[0] ? p.jour : p.jour - 1;
    if (hash2(nuit, f.sel) / 4294967296 >= f.chance_par_nuit) return null;
    return { nuit: nuit, tuile: c[hash2(nuit, f.sel + 1) % c.length] };
  }

  function deplacerOrignal(o, nx, ny) {
    const ancienne = cle(o.x, o.y);
    o.x = nx; o.y = ny;
    if (cle(nx, ny) !== ancienne) {
      const liste = grilleFixe.get(ancienne);
      if (liste) {
        const i = liste.indexOf(o);
        if (i >= 0) liste.splice(i, 1);
        if (!liste.length) grilleFixe.delete(ancienne);
      }
      ajouterA(grilleFixe, o);
    }
  }

  /** La prochaine tuile de sentier ou il va : a moins de cinq tuiles, choisie a l'empreinte de ses pas. */
  function prochainPasDeLOrignal(o) {
    const c = cheminsDesBois(), m = o.orignal, tx = Math.floor(o.x / TT), ty = Math.floor(o.y / TT);
    const proches = c.filter(function (t) { const d = Math.max(Math.abs(t[0] - tx), Math.abs(t[1] - ty)); return d >= 2 && d <= 5; });
    m.pas = (m.pas || 0) + 1;
    const t = proches.length ? proches[hash2(o.id, m.pas) % proches.length] : [tx, ty];
    m.but = { x: t[0] * TT + 8, y: t[1] * TT + 8 };
  }

  /** Il detale, loin de `menace`, et fache. */
  function faireFuirLOrignal(o, menace) {
    const m = o.orignal;
    if (m.etat === 'fuit') return;
    m.etat = 'fuit';
    const a = Math.atan2(o.y - menace.y, o.x - menace.x);
    m.fuite = { dx: Math.cos(a), dy: Math.sin(a) };
  }

  /** Une image de l'orignal : sa venue, ses pas, les phares, le klaxon, la fuite. */
  function majOrignal() {
    const f = ficheOrignal(), j = B.joueur;
    if (!f || !j || B.interieur || B.bloc) return;
    let o = B.orignal;
    if (o && B.entites.indexOf(o) < 0) o = B.orignal = null;
    if (!o) {
      if (B.t % 30 !== 0 || !enService(f.heures)) return;
      const soir = orignalDeLaNuit();
      if (!soir || B.partie.orignalVu === soir.nuit) return;           // une fois par nuit
      const x = soir.tuile[0] * TT + 8, y = soir.tuile[1] * TT + 8;
      if (dist2(x, y, j.x, j.y) > f.bulle_px * f.bulle_px || visibleAEcran(x, y, 24)) return;
      const fiche = DECORS.orignal || {};
      o = creer('decor', x, y, { decor: 'orignal', r: fiche.r || 9, solide: true, dessine: true,
                                 orignal: { etat: 'marche', nuit: soir.nuit, pas: 0 } });
      ajouterA(grilleFixe, o);
      B.orignal = o;
      B.partie.orignalVu = soir.nuit;
      prochainPasDeLOrignal(o);
      return;
    }
    const m = o.orignal, v = j.dansVehicule;
    // Le klaxon, a portee : il fuit (`Vehicules`, `klaxonT` a 30 au coup, 29 l'image d'apres).
    if (v && v.klaxonT === 29 && dist2(o.x, o.y, v.x, v.y) < f.klaxon_px * f.klaxon_px) faireFuirLOrignal(o, v);
    if (m.etat === 'marche') {
      // FIGE DANS LES PHARES : un char qui roule VERS lui, tout pres, la nuit.
      if (v && Monde.estNuit() && dist2(o.x, o.y, v.x, v.y) < f.phares_px * f.phares_px) {
        const vit = Math.hypot(v.vx, v.vy);
        if (vit > 0.3 && ((o.x - v.x) * v.vx + (o.y - v.y) * v.vy) / (vit * Math.hypot(o.x - v.x, o.y - v.y) || 1) > 0.8) {
          m.etat = 'fige';
          return;
        }
      }
      const dx = m.but.x - o.x, dy = m.but.y - o.y, d = Math.hypot(dx, dy);
      if (d < 1) { prochainPasDeLOrignal(o); return; }
      const pas = Math.min(d, f.vitesse);
      if (dx) o.decor = dx < 0 ? 'orignal_g' : 'orignal';
      deplacerOrignal(o, o.x + dx / d * pas, o.y + dy / d * pas);
      return;
    }
    if (m.etat === 'fuit') {
      o.decor = m.fuite.dx < 0 ? 'orignal_g' : 'orignal';
      deplacerOrignal(o, o.x + m.fuite.dx * f.fuite_vitesse, o.y + m.fuite.dy * f.fuite_vitesse);
      if (dist2(o.x, o.y, j.x, j.y) > f.oubli_px * f.oubli_px && !visibleAEcran(o.x, o.y, 32)) { retirer(o); B.orignal = null; }
    }
  }

  function majLesBetes() {
    const liste = betes();
    for (let i = liste.length - 1; i >= 0; i--) { liste[i].t++; majBete(liste[i]); }
  }

  /** Une bete par image : elle vaque, et elle part quand on approche. */
  function majBete(e) {
    const f = B.defs.pietons.betes, fiche = f[e.espece];
    const j = B.joueur;
    if (!fiche || !j) { oublier(e); return; }
    // Oubliee de loin, comme tout le reste — mais plus tot : une bete qu'on ne
    // voit pas ne sert a rien, et elle ne doit pas peser sur le budget d'images.
    if (dist2(e.x, e.y, j.x, j.y) > f.oubli_px * f.oubli_px) { oublier(e); return; }
    if (e.fuite > 0) { majFuite(e, fiche); return; }
    // ⚠️ ELLE PART AVANT QU'ON LA TOUCHE. Un char qui fonce compte double : ce
    // qui arrive vite se voit venir de plus loin.
    const menace = j.dansVehicule ? j.dansVehicule : j;
    // ⚠️ LA CONFIANCE DU CHAT (`confiance_px`, 2e vague, 22 sept. 2026) : au pas, sans
    // arme, sans char — un chat laisse approcher bien plus près, assez pour le caresser
    // (`Interactions.caresserSousLaMain`). Courir (`Entree.bas('esquive')`), sortir une
    // arme ou monter en char, et il redevient aussi farouche qu'avant. `e.confiance` est
    // lu par `Interactions` : ce n'est confiant que si la bête ET la portée le disent —
    // s'approcher DOUCEMENT d'un goéland ne le rend pas plus caressable, il n'a pas la clé.
    e.confiance = fiche.confiance_px !== undefined && menace === j
      && (!j.arme || j.arme === 'poings') && !Entree.bas('esquive');
    const portee = (e.confiance ? fiche.confiance_px : fiche.fuite_px) * (j.dansVehicule ? 1.6 : 1);
    if (dist2(e.x, e.y, menace.x, menace.y) < portee * portee) { sEnvoler(e, fiche, menace); return; }
    if (--e.minuterie > 0) { avancerLaBete(e, fiche); return; }
    // Elle change d'idee : elle se pose, ou elle fait quelques pas.
    const tirage = hash2(e.id * 2654435761 + B.t, 0x8E7E5);
    const bouge = e.humeur !== 'marche' && (tirage & 1) === 0;
    if (bouge) {
      e.humeur = 'marche';
      const dur = e.espece === 'chat' ? fiche.marche_images : fiche.marche_images;
      e.minuterie = dur[0] + (tirage >>> 8) % (dur[1] - dur[0]);
      const a = ((tirage >>> 16) % 360) * Math.PI / 180;
      e.vx = Math.cos(a) * fiche.pas; e.vy = Math.sin(a) * fiche.pas;
      e.v = 1;
    } else {
      e.humeur = 'pose';
      const dur = e.espece === 'goeland' ? fiche.picore_images : fiche.assis_images;
      e.minuterie = dur[0] + (tirage >>> 8) % (dur[1] - dur[0]);
      e.vx = 0; e.vy = 0;
      // Le goeland picore une image sur deux ; le chat, assis, ne bouge pas.
      e.v = e.espece === 'goeland' ? ((B.t >> 5) & 1) : 0;
    }
    avancerLaBete(e, fiche);
  }

  /** Elle marche, et elle ne quitte pas son coin : le sable pour l'un, la
      ruelle pour l'autre. Butee, elle se repose plutot que de pousser un mur. */
  function avancerLaBete(e, fiche) {
    if (e.humeur !== 'marche') {
      if (e.espece === 'goeland' && e.v !== 2) e.v = ((B.t >> 5) & 1);
      return;
    }
    const nx = e.x + e.vx, ny = e.y + e.vy;
    if (!chezElle(e.espece, Math.floor(nx / TT), Math.floor(ny / TT))) {
      e.humeur = 'pose'; e.minuterie = 60; e.vx = 0; e.vy = 0; e.v = 0;
      return;
    }
    e.x = nx; e.y = ny;
    // Au pas aussi, il va dans le sens ou il marche, et ses pattes suivent la distance.
    e.foulee = (e.foulee || 0) + Math.hypot(e.vx, e.vy);
    e.dir = directionDeBete(e);
    void fiche;
  }

  /** Le depart. ⚠️ Le goeland S'ELEVE (l'altitude est un decalage de DESSIN, pas
      une position : rien ne se cogne dans un oiseau) ; le chat file au ras du
      sol. Tous deux s'en vont a l'oppose de ce qui les a derangés. */
  function sEnvoler(e, fiche, menace) {
    const dx = e.x - menace.x, dy = e.y - menace.y, norme = Math.hypot(dx, dy) || 1;
    const vite = e.espece === 'goeland' ? fiche.envol_vitesse : fiche.detale_vitesse;
    e.vx = dx / norme * vite; e.vy = dy / norme * vite;
    e.fuite = e.espece === 'goeland' ? fiche.envol_images : fiche.detale_images;
    e.humeur = 'part';
    e.v = 2;
    if (e.espece === 'goeland') return;
    // ⚠️ LES BÊTES QUI SE SAUVENT POUR VRAI : il se ramasse, puis il prend son elan
    // (`majFuite`) — et une bouffee de poussiere part de ses pattes arriere. A
    // l'empreinte de la bete et de l'instant : un decor ne tire pas de de.
    e.sursaut = fiche.sursaut_images || 0;
    e.elan = 0;
    e.dir = directionDeBete(e);
    for (let k = 0; k < 3; k++) {
      const h = hash2(e.id * 31 + k, B.t);
      particule(e.x - dx / norme * 4, e.y + 2, -dx / norme * 0.5 + ((h % 21) - 10) / 40, -0.1 - (h >>> 8) % 10 / 40,
                12 + (h >>> 12) % 8, '#b9b2a4', 1, 0.02);
    }
  }

  //: Ce qui dessine une bete qui BOUGE : le peintre de son espece (`sprites.js`).
  const BETES_QUI_BOUGENT = { chat: 'chat_bouge', raton: 'raton_bouge' };

  /** Vers ou elle va, en quatre : de profil a gauche ou a droite, de dos vers le haut,
      de face vers le bas. ⚠️ Avec une PRISE : on garde son sens tant que l'autre axe ne
      l'emporte pas nettement — sans elle, une course en diagonale clignotait d'un
      profil a un dos a chaque image. */
  function directionDeBete(e) {
    const ax = Math.abs(e.vx), ay = Math.abs(e.vy);
    if (ax < 1e-6 && ay < 1e-6) return e.dir || 'droite';
    const garde = { droite: e.vx > 0, gauche: e.vx < 0, bas: e.vy > 0, haut: e.vy < 0 };
    if (e.dir && garde[e.dir]) {
      const horiz = e.dir === 'droite' || e.dir === 'gauche';
      if ((horiz ? ax : ay) >= 0.8 * (horiz ? ay : ax)) return e.dir;
    }
    return ax > ay ? (e.vx > 0 ? 'droite' : 'gauche') : (e.vy > 0 ? 'bas' : 'haut');
  }

  /** Ce qu'on dessine d'une bete qui bouge, ou null (assise, posee — ou un goeland) :
      le decor, l'allure, la direction et l'image. ⚠️ L'image se lit a la DISTANCE
      parcourue (`foulee`), pas a l'horloge : une bete bloquee ne court pas sur place. */
  function poseDeBete(e) {
    const decor = BETES_QUI_BOUGENT[e.espece];
    if (!decor) return null;
    const allure = e.fuite > 0 ? (e.sursaut > 0 ? 'sursaut' : 'fuit') : (e.humeur === 'marche' ? 'marche' : null);
    if (!allure) return null;
    const fiche = B.defs.pietons.betes[e.espece] || {};
    const cycle = (fiche.foulee_px && fiche.foulee_px[allure]) || 24;
    const image = allure === 'sursaut' ? 0 : Math.floor((e.foulee || 0) / (cycle / 4)) % 4;
    const dir = e.dir || 'droite';
    return { decor: decor, allure: allure, dir: dir, image: image, cle: allure + '|' + dir + '|' + image };
  }

  /** Une tuile ou une bete qui se sauve peut poser la patte. */
  function libreAuxPattes(x, y) { return Monde.marchablePieton(Math.floor(x / TT), Math.floor(y / TT)); }

  function majFuite(e, fiche) {
    // Le chat et le raton COURENT (`majCourse`) ; le goeland s'envole.
    if (e.espece !== 'goeland') { majCourse(e, fiche); return; }
    e.fuite--;
    e.x += e.vx; e.y += e.vy;
    // Il monte, puis il plane. L'altitude ne sert qu'au dessin.
    e.altitude = Math.min(fiche.montee_px, e.altitude + 0.5);
    e.v = 2;
    if (e.fuite <= 0) oublier(e);
  }

  /** ⚠️ LES BÊTES QUI SE SAUVENT POUR VRAI (Martin, 22 sept. 2026). Avant : une image
      fixe qui glissait a pleine vitesse des la premiere image, et qui DISPARAISSAIT net
      des qu'elle quittait sa ruelle — sous nos yeux. Maintenant :
      - elle se RAMASSE (`sursaut`), puis ACCELERE (`elan`) ;
      - un mur, elle le LONGE (on garde l'axe qui passe ; sinon un quart de tour, du cote
        qui l'eloigne du joueur) — elle ne le traverse ni ne s'y evapore ;
      - elle peut quitter sa ruelle en fuyant : elle court ou elle peut ;
      - sa fuite finie, elle ne s'efface que HORS DE L'ECRAN ; sous nos yeux elle court
        encore, et coincee, elle s'assoit la ou elle est. */
  function majCourse(e, fiche) {
    e.v = 2;
    if (e.sursaut > 0) { e.sursaut--; return; }
    e.elan = Math.min(1, (e.elan || 0) + 1 / (fiche.elan_images || 1));
    const k = e.elan * (2 - e.elan);               // elle part vite, puis elle tient sa vitesse
    let nx = e.x + e.vx * k, ny = e.y + e.vy * k;
    if (!libreAuxPattes(nx, ny)) {
      if (libreAuxPattes(nx, e.y)) { ny = e.y; e.vy = 0; e.vx = Math.sign(e.vx) * fiche.detale_vitesse; }
      else if (libreAuxPattes(e.x, ny)) { nx = e.x; e.vx = 0; e.vy = Math.sign(e.vy) * fiche.detale_vitesse; }
      else {
        // Un coin : un quart de tour, du cote qui l'eloigne du joueur.
        const j = B.joueur, gx = -e.vy, gy = e.vx;
        const versJ = j ? (gx * (j.x - e.x) + gy * (j.y - e.y)) : 0;
        const s = versJ > 0 ? -1 : 1;
        e.vx = gx * s; e.vy = gy * s;
        nx = e.x; ny = e.y;
      }
    }
    const fait = Math.hypot(nx - e.x, ny - e.y);
    e.foulee = (e.foulee || 0) + fait;
    e.x = nx; e.y = ny;
    e.dir = directionDeBete(e);
    e.fuite--;
    e.coinceT = fait < 0.3 ? (e.coinceT || 0) + 1 : 0;
    if (e.fuite > 0) return;
    if (!visibleAEcran(e.x, e.y, 16)) { oublier(e); return; }
    if (e.coinceT < 30) { e.fuite = 1; return; }
    // Coincee sous nos yeux : elle s'assoit, et elle reprend sa vie de bete.
    e.fuite = 0; e.humeur = 'pose'; e.v = 0; e.vx = 0; e.vy = 0; e.coinceT = 0;
    const dur = fiche.assis_images || [120, 240];
    e.minuterie = dur[0] + hash2(e.id, B.t) % Math.max(1, dur[1] - dur[0]);
  }

  // --- La foule de la foire ------------------------------------------------
  //: ⚠️ « UNE FOIRE, C'EST BEAUCOUP DE CHOSES ET BEAUCOUP DE MONDE » — Martin,
  //: devant une foire a trois passants. La foule de la rue nait au hasard dans
  //: la bulle du joueur et TRAVERSE la foire ; celle-ci nait DANS la foire, y
  //: reste, et y fait ce qu'on fait dans une foire : aller d'un kiosque a
  //: l'autre, s'arreter devant, regarder. Les mascottes, elles, deambulent et
  //: saluent.
  //:
  //: ⚠️ Rien ne se tire au de du jeu ICI : la place se trouve en balayant le
  //: rectangle de la foire, le kiosque vise se tire a l'empreinte du passant et
  //: de l'instant. (`creerPieton` en tire deux pour la bourse et la direction —
  //: comme pour les enfants de la greve, ca ne joue qu'a portee de la foire.)

  /** Une tuile marchable de la foire, hors champ et libre. On balaie le
      rectangle depuis un point de depart qui tourne avec le temps : la foule ne
      nait pas toujours au meme coin. */
  function placeDansLaFoire(r, k) {
    const n = r.l * r.h, depart = hash2(B.t, 0xF0 + k) % n;
    for (let i = 0; i < n; i += 3) {
      const c = (depart + i * 7) % n;
      const tx = r.x + (c % r.l), ty = r.y + Math.floor(c / r.l);
      if (!Monde.marchablePieton(tx, ty) || !Monde.dansLaFoire(tx, ty)) continue;
      const x = tx * TT + 8, y = ty * TT + 8;
      // ⚠️ A PORTEE DU JOUEUR : `peupler` oublie tout passant au-dela de la bulle
      // (520 px). Nee au bout de la foire, la foule etait effacee a l'image
      // suivante — la capture ne comptait que six forains sur trente voulus.
      if (dist2(x, y, B.joueur.x, B.joueur.y) > 470 * 470) continue;
      if (visibleAEcran(x, y, 20) || !placeLibre(x, y)) continue;
      return { x: x, y: y };
    }
    return null;
  }

  function naitreLaFoire() {
    const f = B.defs.pietons && B.defs.pietons.foule_de_foire;
    const def = Monde.carte && Monde.carte.def;
    const r = def && def.foire;
    const j = B.joueur;
    if (!f || !r || !j || B.interieur) return 0;
    // La distance du joueur au BORD de la foire, pas a son centre : elle fait
    // quatre-vingts tuiles de long, et on doit la trouver pleine en y arrivant.
    const bx = Math.max(r.x * TT, Math.min(j.x, (r.x + r.l) * TT));
    const by = Math.max(r.y * TT, Math.min(j.y, (r.y + r.h) * TT));
    if (dist2(bx, by, j.x, j.y) > f.rayon_px * f.rayon_px) return 0;
    let forains = 0, mascottes = 0;
    for (const q of B.entites) {
      if (q.type !== 'pieton' || !q.vivant) continue;
      if (q.metier === 'forain') forains++;
      else if (q.metier === 'mascotte') mascottes++;
    }
    const costumes = B.defs.pietons.catalogue.filter(function (p) { return p.metier === 'mascotte'; });
    let nes = 0;
    for (let k = 0; k < f.par_battement; k++) {
      const mascotte = k === 0 && mascottes < f.mascottes && costumes.length > 0;
      if (!mascotte && forains >= f.forains) break;
      const place = placeDansLaFoire(r, k);
      if (!place) break;
      const arch = mascotte ? costumes[mascottes % costumes.length]
        : archetypeDeRue(place.x, place.y, hash2(place.x * 31 + place.y, B.t) / 4294967296);
      const e = creerPieton(place.x, place.y, arch);
      if (!e) continue;
      // ⚠️ Un METIER, pas un costume : chacun a sa routine (`majForain`,
      // `majMascotte`), et il ne compte pas dans la foule de la rue.
      e.metier = mascotte ? 'mascotte' : 'forain';
      e.foire = true;
      ajouterA(grille, e);
      if (mascotte) mascottes++; else forains++;
      nes++;
    }
    return nes;
  }

  /** Arrive a destination : on s'arrete, et on regarde ce qu'on est venu voir. */
  function arriveALaFoire(e, f) {
    if (e.etat !== 'cap' || !e.cap) return false;
    if (dist2(e.x, e.y, e.cap.x, e.cap.y) > 14 * 14 && e.capT < 540) return false;
    const t = hash2(e.id * 2654435761 + B.t, 0xF0A1E);
    e.etat = 'arret';
    e.minuterie = f.arret_images[0] + t % (f.arret_images[1] - f.arret_images[0]);
    e.vx = 0; e.vy = 0;
    e.cap = null;
    if (e.regarde) regarder(e, e.regarde.x - e.x, e.regarde.y - e.y);
    return true;
  }

  /** Un point de la foire ou aller, a portee de marche (`cap` renonce au-dela
      de 340 px). Pour un forain : le comptoir d'un kiosque proche, trois fois
      sur quatre ; sinon un bout d'allee. */
  function destinationDeFoire(e, versUnKiosque) {
    const def = Monde.carte.def, r = def.foire;
    const t = hash2(e.id * 2654435761 + B.t, 0xF0A1D);
    if (versUnKiosque) {
      const proches = (def.kiosques_de_foire || []).filter(function (k) {
        return dist2(k.x * TT + 8, k.y * TT + 8, e.x, e.y) < 280 * 280;
      });
      if (proches.length) {
        const k = proches[t % proches.length];
        // ⚠️ DEVANT le comptoir : il est toujours peint face au sud, donc on se
        // tient sur la tuile du dessous — pour un kiosque du rang nord, c'est
        // l'allee elle-meme, et c'est la que la foule s'amasse.
        const decale = ((t >>> 8) % 21) - 10;
        return { x: k.x * TT + 8 + decale, y: (k.y + 1) * TT + 8,
                 regarde: { x: k.x * TT + 8, y: k.y * TT } };
      }
    }
    for (let essai = 0; essai < 12; essai++) {
      const u = hash2(t, essai);
      const tx = Math.floor(e.x / TT) + (u % 31) - 15;
      const ty = Math.floor(e.y / TT) + ((u >>> 8) % 11) - 5;
      if (tx < r.x || tx >= r.x + r.l || ty < r.y || ty >= r.y + r.h) continue;
      if (Monde.glyphe(tx, ty) !== 'g' || !Monde.marchablePieton(tx, ty) || !Monde.dansLaFoire(tx, ty)) continue;
      return { x: tx * TT + 8, y: ty * TT + 8, regarde: null };
    }
    return null;
  }

  function allerA(e, d) {
    e.cap = { x: d.x, y: d.y };
    e.regarde = d.regarde;
    e.capT = 0; e.capVite = false;
    e.etat = 'cap';
    e.poseFixe = null;
  }

  /** LE FORAIN : un kiosque, un arret devant, le kiosque suivant. */
  function majForain(e) {
    const f = B.defs.pietons.foule_de_foire;
    if (!Monde.carte.def.foire) return;
    if (arriveALaFoire(e, f)) return;
    if (e.etat !== 'flane') return;          // il regarde, il a peur, il temoigne
    const t = hash2(e.id * 2654435761 + B.t, 0xF0A1C);
    const d = destinationDeFoire(e, (t & 3) !== 0);
    if (d) allerA(e, d);
  }

  /** LA MASCOTTE : elle deambule dans l'allee, s'arrete, et SALUE — les bras
      leves, deux images qui alternent (`mascotte`, poses 3 et 4 de `bas`). */
  function majMascotte(e) {
    const f = B.defs.pietons.foule_de_foire;
    if (!Monde.carte.def.foire) return;
    if (e.etat === 'arret') {
      e.face = 'bas';
      e.poseFixe = 3 + (Math.floor(e.t / f.salut_images) % 2);
      return;
    }
    if (arriveALaFoire(e, f)) { e.face = 'bas'; return; }
    if (e.etat !== 'flane') { e.poseFixe = null; return; }
    const d = destinationDeFoire(e, false);
    if (d) allerA(e, d);
  }

  // --- Les enfants de la greve ---------------------------------------------
  //: ⚠️ **JOUER, C'EST UN `metier`, PAS UN COSTUME.** La regle des sortes de
  //: gens est ecrite trois fois dans `pietons.py`, et le depot l'a deja payee
  //: avec les filles de la Brume : une sorte sans routine est un deguisement.
  //: L'enfant existe depuis la v1 et n'a jamais rien fait d'autre que marcher.
  //:
  //: ⚠️ Ce ne sont PAS tous les enfants de la ville : ceux-la naissent sur la
  //: greve et y restent. Donner un `metier` a l'archetype les sortirait tous de
  //: la foule et rendrait muette la mere qui promene le sien.

  /** Les baigneurs de la plage, dans la bulle du joueur : les enfants qui jouent
      et les grands qui se font bronzer. Ils naissent hors champ, sur une plage
      DECLAREE (`plageEn`), et s'oublient comme tout le monde quand on s'eloigne.

      ⚠️ **Deux plafonds, pas un.** Retour de Martin : « des gens s'il y a
      beaucoup de place ». Un plafond commun laissait les premiers nes prendre
      toutes les places, et la plage n'avait qu'un seul age. On fait naitre celui
      des deux groupes qui est le plus loin de son compte. */
  function naitreLesEnfantsDeLaPlage() {
    const f = B.defs.pietons && B.defs.pietons.plage;
    // La nuit, personne ne se baigne : la plage a ses heures (`PLAGE.heures`).
    if (!f || !B.joueur || B.interieur || !enService(f.heures)) return 0;
    const baigneurs = B.entites.filter(function (q) { return q.metier === 'baigneur' && q.vivant; });
    const petits = baigneurs.filter(function (q) { return q.sprite === 'enfant'; }).length;
    const grands = baigneurs.length - petits;
    const noms = f.adultes_archetypes || [];
    const maxGrands = noms.length ? (f.adultes || 0) : 0;
    const veutPetit = petits < f.enfants;
    const veutGrand = grands < maxGrands;
    if (!veutPetit && !veutGrand) return 0;
    const petit = veutPetit && (!veutGrand || petits * maxGrands <= grands * f.enfants);
    // ⚠️ Pas de de ici non plus : le grand qui nait est le suivant de la liste.
    const arch = petit ? archetype('enfant') : archetype(noms[grands % noms.length]);
    if (!arch) return 0;
    const place = placeDeGreve(f.rayon_px);
    if (!place) return 0;
    const e = creerPieton(place.x, place.y, arch);
    if (!e) return 0;
    e.metier = 'baigneur';
    e.jeu = null;
    e.jeuT = 0;
    ajouterA(grille, e);
    return 1;
  }

  // --- Les enfants a velo ------------------------------------------------------------

  //: ⚠️ Martin (21 sept. 2026) : « je veux aussi des enfants a velo, seulement sur
  //: trottoir, casque, parc ». Ce ne sont pas des chars : ce sont des passants
  //: (`metier: 'cycliste'`) qui flanent plus vite, sur un corps a eux
  //: (`SPRITES.enfant_velo`), et a qui la rue est INTERDITE — pas seulement la
  //: chaussee, comme a tout le monde : la traverse aussi. Un enfant a velo reste
  //: sur son ilot, le trottoir, l'abord et le parc.

  /** Une tuile ou un enfant a velo peut rouler : le trottoir, l'abord, la
      pelouse et l'allee d'un parc. ⚠️ Ni la chaussee ni le passage pieton
      (`estRoute` les prend tous les deux), ni la ruelle, ni le sable. */
  function roulableEnfant(tx, ty) {
    if (Monde.estRoute(tx, ty) || Monde.bloque(tx, ty, Monde.MASQUE_PIETON)) return false;
    const g = Monde.glyphe(tx, ty);
    return Monde.estTrottoir(tx, ty) || Monde.estAbord(tx, ty) || g === ',' || g === 'g';
  }

  /** Il ne descend pas sur la rue, meme en detalant : on coupe le pas qui l'y
      menerait, axe par axe — il longe la bordure au lieu de la franchir.

      ⚠️ **ET LE COIN EN DIAGONALE.** Les deux axes, pris chacun seul, tombaient
      sur du trottoir ; le pas entier, lui, tombait sur la traverse d'en biais —
      au coin d'un ilot, en detalant. Le juge l'a vu deux fois en 800 releves.

      ⚠️ Et s'il y est quand meme (un char l'a pousse, la foule l'a demele), il
      en SORT : vers la tuile roulable la plus proche, a son allure. Sans ca, la
      regle qui le garde sur le trottoir le gardait sur la traverse. */
  function resterSurLeTrottoir(e) {
    const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
    if (!roulableEnfant(tx, ty)) {
      // Le bord le plus PROCHE d'une tuile roulable, pas son centre : pousse d'un
      // pixel sur la traverse, il remonte d'un pixel — viser le centre de la
      // tuile du coin l'envoyait contre le poteau du feu, qui le renvoyait.
      let meilleur = null;
      for (let r = 1; r <= 3 && !meilleur; r++) {
        for (let dy = -r; dy <= r; dy++) {
          for (let dx = -r; dx <= r; dx++) {
            if (Math.max(Math.abs(dx), Math.abs(dy)) !== r || !roulableEnfant(tx + dx, ty + dy)) continue;
            const x0 = (tx + dx) * TT, y0 = (ty + dy) * TT;
            const gx = Math.min(Math.max(e.x, x0 + e.r + 1), x0 + TT - e.r - 1) - e.x;
            const gy = Math.min(Math.max(e.y, y0 + e.r + 1), y0 + TT - e.r - 1) - e.y;
            const d = Math.hypot(gx, gy);
            if (!meilleur || d < meilleur.d) meilleur = { gx: gx, gy: gy, d: d };
          }
        }
      }
      if (meilleur) {
        const n = meilleur.d || 1, allure = Math.min(meilleur.d, Math.max(Math.hypot(e.vx, e.vy), B.defs.recherche.vitesses.pieton));
        e.vx = meilleur.gx / n * allure; e.vy = meilleur.gy / n * allure;
      }
      return;
    }
    const bord = e.r + 2;
    const x1 = Math.floor((e.x + e.vx + Math.sign(e.vx) * bord) / TT), y1 = Math.floor((e.y + e.vy + Math.sign(e.vy) * bord) / TT);
    if (e.vx && !roulableEnfant(x1, ty)) e.vx = 0;
    if (e.vy && !roulableEnfant(tx, y1)) e.vy = 0;
    if (e.vx && e.vy && !roulableEnfant(x1, y1)) e.vy = 0;
  }

  /** `fn` jouee avec un de PRETE : la file du jeu ne bouge pas d'un tirage.
      ⚠️ La meme que celle des gens qui attendent l'autobus (`Autobus`) :
      `creerPieton` tire deux des, et une naissance de decor ne doit pas
      deplacer tout ce qui nait apres elle. */
  function sansLeDe(graine, fn) {
    const de = B.rng;
    let s = graine >>> 0;
    B.rng = function () { s = hash2(s + 1, 0x5EED); return (s % 100000) / 100000; };
    try { return fn(); } finally { B.rng = de; }
  }

  /** Une tuile de trottoir ou de parc, dans la bulle et hors champ, dans un
      quartier qui en veut. ⚠️ Aucun de : on balaie en spirale, comme pour la
      greve, en commencant par un cote qui tourne avec l'heure. */
  function placeDEnfantAVelo(rayon, arch) {
    const c = Monde.carte, j = B.joueur;
    if (!c) return null;
    const t = Math.floor(rayon / TT);
    const jx = Math.floor(j.x / TT), jy = Math.floor(j.y / TT);
    const tour = Math.floor(B.t / 60) % 4;
    for (let d = 4; d <= t; d++) {
      for (let k = -d; k <= d; k++) {
        const cotes = [[jx + k, jy - d], [jx + d, jy + k], [jx - k, jy + d], [jx - d, jy - k]];
        for (let n = 0; n < 4; n++) {
          const tx = cotes[(n + tour) % 4][0], ty = cotes[(n + tour) % 4][1];
          if (!roulableEnfant(tx, ty)) continue;
          const x = tx * TT + 8, y = ty * TT + 8;
          if (dist2(x, y, j.x, j.y) > rayon * rayon) continue;
          const zone = Monde.zoneA(x, y);
          if (arch.districts && (!zone || arch.districts.indexOf(zone.district) < 0)) continue;
          if (visibleAEcran(x, y, 24) || !placeLibre(x, y)) continue;
          return { x: x, y: y, tx: tx, ty: ty };
        }
      }
    }
    return null;
  }

  /** Les enfants a velo de la bulle : le jour (`heures`), dans leurs quartiers
      (`districts`), `combien` au plus. Le casque, le cadre et le chandail se
      lisent a l'empreinte de la tuile ou il nait. */
  function naitreLesEnfantsAVelo() {
    const f = B.defs.pietons && B.defs.pietons.enfants_a_velo;
    const arch = archetype('enfant_velo');
    if (!f || !arch || arch.slug !== 'enfant_velo' || !B.joueur || B.interieur) return 0;
    if (!enService(arch.heures)) return 0;
    const n = B.entites.filter(function (q) { return q.type === 'pieton' && q.arch === 'enfant_velo' && q.vivant; }).length;
    if (n >= f.combien) return 0;
    const place = placeDEnfantAVelo(f.rayon_px, arch);
    if (!place) return 0;
    const h = hash2(place.tx, place.ty);
    const e = sansLeDe(h, function () { return creerPieton(place.x, place.y, arch); });
    if (!e) return 0;
    e.swaps = Object.assign({}, arch.couleurs, {
      e: f.casques[h % f.casques.length],
      v: f.cadres[(h >>> 8) % f.cadres.length],
      c: f.chandails[(h >>> 16) % f.chandails.length],
    });
    return 1;
  }

  /** Une tuile d'une plage declaree, dans la bulle et hors champ.

      ⚠️ **ELLE NE TIRE PAS UN SEUL DE.** Premiere version jetee : elle tirait
      quarante couples au hasard dans `B.rng()`, et **le pickpocket a cesse de
      voler** — un juge qui ne parle pas de plage, tombe parce que chaque de
      consomme decale tous ceux qui suivent. C'est la troisieme fois de la
      semaine que cette lecon se presente (le pilote des deux-roues, le char en
      panne) ; ici elle a ete payee au juge, pas en jeu. On BALAIE donc la bulle
      en spirale de tuiles, et l'endroit ne depend que de la geographie. */
  function placeDeGreve(rayon) {
    const c = Monde.carte, j = B.joueur;
    if (!c) return null;
    const t = Math.floor(rayon / TT);
    const jx = Math.floor(j.x / TT), jy = Math.floor(j.y / TT);
    // Du plus proche au plus loin : le premier sable hors champ gagne.
    for (let d = 4; d <= t; d++) {
      for (let k = -d; k <= d; k++) {
        for (const [tx, ty] of [[jx + k, jy - d], [jx + k, jy + d], [jx - d, jy + k], [jx + d, jy + k]]) {
          if (Monde.glyphe(tx, ty) !== 's' || !Monde.marchablePieton(tx, ty)) continue;
          const x = tx * TT + 8, y = ty * TT + 8;
          if (dist2(x, y, j.x, j.y) > rayon * rayon) continue;
          if (visibleAEcran(x, y, 24) || !placeLibre(x, y)) continue;
          if (!plageEn(tx, ty)) continue;
          return { x: x, y: y };
        }
      }
    }
    return null;
  }

  /** La plage DECLAREE qui porte cette tuile (`carte.PLAGES`), ou null.

      ⚠️ **Pas « du sable pres de l'eau »** — c'etait la premiere regle, et elle
      faisait naitre des enfants sur le bord d'un etang de parc et sur les bandes
      de trois tuiles qui longeaient toute la baie. La carte dit ou sont les
      plages ; le deviner ici serait une deuxieme verite. */
  function plageEn(tx, ty) {
    const def = Monde.carte && Monde.carte.def;
    for (const p of (def && def.plages) || []) {
      if (tx >= p.x && tx < p.x + p.l && ty >= p.y && ty < p.y + p.h) return p;
    }
    return null;
  }

  /** Les serviettes et les chaises longues de la ville, lues une fois dans la
      carte. ⚠️ Pas dans l'index du decor : elles ne sont ni solides ni
      cassables, et `estIndexable` les laisse dehors expres. */
  let litsDeLaCarte = null, litsDe = null;
  function lits() {
    const def = Monde.carte && Monde.carte.def;
    if (litsDe !== def) {
      litsDe = def;
      litsDeLaCarte = ((def && def.decor) || []).filter(function (d) {
        return d.type === 'serviette' || d.type === 'chaise_longue';
      });
    }
    return litsDeLaCarte;
  }

  /** La serviette ou la chaise longue libre la plus proche, a portee. */
  function litLibre(e, portee) {
    let meilleur = null, dMin = portee * portee;
    for (const d of lits()) {
      const x = d.x * TT + 8, y = d.y * TT + 8;
      const q = dist2(e.x, e.y, x, y);
      if (q >= dMin) continue;
      const pris = B.entites.some(function (o) {
        return o !== e && o.vivant && o.metier === 'baigneur' && o.lit === d;
      });
      if (!pris) { dMin = q; meilleur = d; }
    }
    return meilleur;
  }

  /** Un autre coin de la MEME plage, ou l'on arrive sans se mouiller.

      ⚠️ A l'empreinte du baigneur et de l'instant, jamais au de du jeu — la
      meme lecon que `placeDeGreve`. Et le chemin se verifie : un bout de plage
      en pointe laisse une anse d'eau entre deux coins de sable, et y marcher
      droit, c'est une promenade dans la baie. */
  function coinDePlage(e) {
    const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
    const p = plageEn(tx, ty);
    if (!p) return null;
    for (let k = 0; k < 6; k++) {
      const h = hash2(e.id * 40503 + B.t + k * 7919, 0x9A6E5);
      const cx = p.x + h % p.l, cy = p.y + (h >>> 11) % p.h;
      if (Monde.glyphe(cx, cy) !== 's' || !Monde.marchablePieton(cx, cy)) continue;
      const pas = Math.max(Math.abs(cx - tx), Math.abs(cy - ty)) * 2;
      let sec = true;
      for (let i = 1; i < pas && sec; i++) {
        const mx = Math.floor((tx + 0.5) + (cx - tx) * i / pas), my = Math.floor((ty + 0.5) + (cy - ty) * i / pas);
        if (Monde.glyphe(mx, my) !== 's') sec = false;
      }
      if (sec) return { x: cx * TT + 8, y: cy * TT + 8 };
    }
    return null;
  }

  /** La plage ferme (`PLAGE.heures`) : on sort de l'eau, on range ses affaires,
      et on s'en va.

      ⚠️ **HORS DE L'ECRAN, JAMAIS SOUS NOS YEUX** — comme le marchand d'un
      kiosque qui ferme. Un baigneur qu'on regarde marche (il sort de l'eau s'il
      y est, puis il flane et quitte le sable) ; celui qu'on ne voit pas est deja
      rentre. Aucun de. ⚠️ Par `entre` (retire a l'image suivante, comme qui
      passe une porte), pas par `retirer` : on est ici DANS la boucle de
      `majSortes`, et un `splice` en plein parcours sauterait le suivant. */
  function plierBagage(e) {
    quitterLeJeu(e);
    if (!visibleAEcran(e.x, e.y, 40)) { e.etat = 'entre'; e.minuterie = 1; e.vx = 0; e.vy = 0; return; }
    const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
    if (!Monde.estEau(tx, ty)) return;
    // Le sable le plus proche : les quatre voisins d'abord, puis les diagonales.
    // ⚠️ Un decor SOLIDE sur la tuile (une table de pique-nique, une chaise de
    // sauveteur) lui barrait la seule sortie : il restait plante dans l'eau, `cap`
    // repousse par la table a chaque pas. On prend une tuile ou il peut poser le pied.
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1]]) {
      const cx = tx + dx, cy = ty + dy;
      if (Monde.estEau(cx, cy) || !Monde.marchablePieton(cx, cy)) continue;
      const x = cx * TT + 8, y = cy * TT + 8;
      if (decorAutour(x, y, 20).some(function (d) {
        return d.solide && dist2(d.x, d.y, x, y) < (d.r + e.r + 2) * (d.r + e.r + 2);
      })) continue;
      // ⚠️ Six pixels AU-DELA du centre, comme `bordDeLEau` dans l'autre sens :
      // `cap` s'arrete a 12 px de son but, et vise au centre, il restait les
      // pieds dans l'eau (le juge l'a vu).
      e.cap = { x: x + dx * 6, y: y + dy * 6 }; e.capT = 0; e.etat = 'cap';
      return;
    }
  }

  /** La routine : trois jeux, et on en change. */
  function majPlage(e) {
    const f = B.defs.pietons.plage;
    if (!enService(f.heures)) { plierBagage(e); return; }
    if (e.etat !== 'flane' && e.etat !== 'arret' && e.etat !== 'cap' && e.etat !== 'fige') {
      // Il a peur, il temoigne, il fuit : le jeu s'arrete, il reste un enfant.
      quitterLeJeu(e);
      return;
    }
    if (e.jeu && --e.jeuT > 0) { majJeu(e, f); return; }
    quitterLeJeu(e);
    // ⚠️ On choisit parmi ce qui est LA : un enfant qui « joue au chateau »
    // sans chateau a portee est un enfant plante devant rien.
    // ⚠️ Et chacun son age : le chateau est aux petits, le soleil aux grands.
    const petit = e.sprite === 'enfant';
    const choix = [];
    const chateau = petit ? chateauLePlusProche(e, f.chateau_px) : null;
    if (chateau) choix.push('chateau');
    const lit = petit ? null : litLibre(e, f.bronzer_px || 0);
    if (lit) choix.push('bronzer');
    const bord = bordDeLEau(e);
    if (bord) choix.push('baignade');
    // Et on se promene : sans ca, un baigneur qui n'a rien a portee se remettait
    // a flaner comme un passant, et flaner mene hors du sable.
    const ailleurs = coinDePlage(e);
    if (ailleurs) choix.push('promenade');
    const copain = B.entites.find(function (q) {
      if (q === e || q.metier !== 'baigneur' || !q.vivant || q.jeu) return false;
      const d = dist2(q.x, q.y, e.x, e.y);
      // Assez pres pour se voir, assez loin pour que le ballon VOLE.
      return d < f.ballon_px * f.ballon_px && d > f.ballon_min_px * f.ballon_min_px;
    });
    if (copain) choix.push('ballon');
    if (!choix.length) return;
    // ⚠️ Meme raison : a l'empreinte de l'enfant et de l'instant, pas au de.
    const tirage = hash2(e.id * 2654435761 + B.t, 0x71A6E);
    e.jeu = choix[tirage % choix.length];
    e.jeuT = f.jeu_images[0] + (tirage >>> 8) % (f.jeu_images[1] - f.jeu_images[0]);
    if (e.jeu === 'chateau') { e.cap = { x: chateau.x, y: chateau.y }; e.capT = 0; e.etat = 'cap'; }
    else if (e.jeu === 'baignade') { e.cap = bord; e.capT = 0; e.etat = 'cap'; e.barbote = true; }
    else if (e.jeu === 'bronzer') {
      e.lit = lit;
      e.jeuT = f.bronzer_images[0] + (tirage >>> 8) % (f.bronzer_images[1] - f.bronzer_images[0]);
      e.cap = { x: lit.x * TT + 8, y: lit.y * TT + 8 }; e.capT = 0; e.etat = 'cap';
    }
    else if (e.jeu === 'promenade') { e.cap = ailleurs; e.capT = 0; e.etat = 'cap'; }
    else { lancerLeBallon(e, copain, f); }
  }

  function quitterLeJeu(e) {
    if (e.ballon) { retirer(e.ballon); e.ballon = null; }
    if (e.copain) { e.copain.copain = null; e.copain.ballon = null; e.copain = null; }
    e.jeu = null; e.barbote = false; e.poseFixe = null; e.lit = null;
  }

  /** Le chateau de sable le plus proche, encore debout. */
  function chateauLePlusProche(e, portee) {
    let meilleur = null, dMin = portee * portee;
    for (const d of decorAutour(e.x, e.y, portee)) {
      if (d.decor !== 'chateau_sable' || d.brise) continue;
      const q = dist2(e.x, e.y, d.x, d.y);
      if (q < dMin) { dMin = q; meilleur = d; }
    }
    return meilleur;
  }

  /** La PREMIERE tuile d'eau devant lui, et pas une de plus.

      ⚠️ **UN ENFANT NE SE NOIE PAS.** Mesure, pour ne pas s'attribuer un
      correctif : aucun pieton ne se noie dans le jeu — le souffle et `noyade`
      n'existent que pour le joueur. Ce n'est donc pas une reparation, c'est une
      garantie qu'on EPINGLE, pour le jour ou quelqu'un donnera du souffle aux
      passants. */
  function bordDeLEau(e) {
    const f = B.defs.pietons.plage;
    const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
    // ⚠️ Toute la profondeur d'une plage (`carte.PLAGES`, huit tuiles) : a
    // quatre, qui jouait au fond du sable ne voyait jamais l'eau.
    for (let d = 1; d <= 9; d++) {
      for (const [cx, cy] of [[tx + d, ty], [tx - d, ty], [tx, ty + d], [tx, ty - d]]) {
        if (!Monde.estEau(cx, cy)) continue;
        // La PREMIERE : celle qui a de la terre juste derriere elle. Une tuile
        // d'eau entouree d'eau est le large. ⚠️ CEINTURE, pas correctif : la
        // plus proche depuis le sable a toujours de la terre derriere elle, et
        // neutraliser ce test ne fait tomber aucun juge.
        const rx = cx - Math.sign(cx - tx), ry = cy - Math.sign(cy - ty);
        if (Monde.estEau(rx, ry)) continue;
        // ⚠️ ON VISE UN PEU PLUS LOIN QUE LE CENTRE, et c'est `cap` qui l'exige :
        // il s'arrete a 12 px de son but (un palier ecrit pour que le pickpocket
        // cesse de pousser dans sa victime). Une tuile fait 16 px : vise au
        // centre, l'enfant s'immobilise AVANT d'y entrer — mesure, aucun des
        // quatre ne s'est mouille les pieds une seule fois en 1 800 images, et
        // le juge passait a vide parce qu'il ne mesurait que « il n'est pas alle
        // trop loin ». Six pixels au-dela, et il pose le pied dans l'eau.
        const vers = { x: Math.sign(cx - tx), y: Math.sign(cy - ty) };
        return { x: cx * TT + 8 + vers.x * 6, y: cy * TT + 8 + vers.y * 6, tx: cx, ty: cy };
      }
    }
    void f;
    return null;
  }

  function majJeu(e, f) {
    if (e.jeu === 'chateau') {
      // Il y revient, et si le chateau n'y est plus il s'en cherche un autre.
      const chateau = chateauLePlusProche(e, f.chateau_px);
      if (!chateau) { quitterLeJeu(e); return; }
      const loin = dist2(e.x, e.y, chateau.x, chateau.y) > 18 * 18;
      if (loin) { e.cap = { x: chateau.x, y: chateau.y }; e.etat = 'cap'; return; }
      // Plante devant, tourne vers lui : il le rebatit. ⚠️ Pas de pose
      // ACCROUPIE — le corps de l'enfant n'en a pas, et en inventer une ici
      // serait un dessin que personne d'autre ne peut relire. `poseFixe` tient
      // seulement l'image immobile, sinon un corps a l'arret clignote.
      e.etat = 'arret';
      e.minuterie = f.accroupi_images[0];
      e.vx = 0; e.vy = 0;
      regarder(e, chateau.x - e.x, chateau.y - e.y);
      e.poseFixe = 0;
    } else if (e.jeu === 'baignade') {
      const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
      if (Monde.estEau(tx, ty)) {
        // ⚠️ IL S'ARRETE LA. Pas de deuxieme tuile : on barbote au bord, on ne
        // nage pas. S'il derive vers le large, il revient.
        e.etat = 'arret';
        e.minuterie = 30;
        e.vx = 0; e.vy = 0;
        if (e.t % 24 === 0) remous(e.x, e.y, 3);
        // ⚠️ CEINTURE, pas correctif (voir `bordDeLEau`) : rien ne le pousse au
        // large aujourd'hui, et neutraliser ce retour ne fait tomber aucun juge.
        const dehors = bordDeLEau(e);
        if (trop_loin(e, f) && dehors) { e.cap = dehors; e.etat = 'cap'; }
      } else {
        const bord = bordDeLEau(e);
        if (!bord) { quitterLeJeu(e); return; }
        e.cap = bord; e.capT = 0; e.etat = 'cap';
      }
    } else if (e.jeu === 'ballon') {
      majBallon(e);
    } else if (e.jeu === 'bronzer') {
      const lit = e.lit;
      if (!lit) { quitterLeJeu(e); return; }
      const x = lit.x * TT + 8, y = lit.y * TT + 8;
      if (dist2(e.x, e.y, x, y) > 14 * 14) {
        if (e.etat !== 'cap') { e.cap = { x: x, y: y }; e.capT = 0; e.etat = 'cap'; }
        return;
      }
      // Au soleil, sur sa serviette. ⚠️ Pas de pose COUCHEE : le corps commun
      // n'en a pas, et celle de l'assomme dirait autre chose qu'une sieste.
      e.etat = 'arret'; e.minuterie = 40; e.vx = 0; e.vy = 0;
      regarder(e, 0, 1);
      e.poseFixe = 0;
    } else if (e.jeu === 'promenade') {
      const arrive = !e.cap || dist2(e.x, e.y, e.cap.x, e.cap.y) <= 14 * 14;
      if (e.etat === 'cap' && !arrive) return;
      // Arrive, ou il a renonce : il regarde la mer un moment, puis il rechoisit.
      e.etat = 'arret'; e.minuterie = 90; e.vx = 0; e.vy = 0; e.cap = null;
      e.jeuT = Math.min(e.jeuT, 6);
    }
  }

  /** Est-il alle plus loin que la premiere tuile d'eau ? */
  function trop_loin(e, f) {
    const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
    for (const [cx, cy] of [[tx + 1, ty], [tx - 1, ty], [tx, ty + 1], [tx, ty - 1]]) {
      if (!Monde.estEau(cx, cy)) return false;      // il touche encore la terre
    }
    void f;
    return true;                                    // de l'eau tout autour : c'est le large
  }

  /** Deux enfants et un ballon qui va de l'un a l'autre. C'est tout, et ca
      suffit — un decor qui BOUGE se voit de trois ecrans. */
  function lancerLeBallon(e, copain, f) {
    e.copain = copain; copain.copain = e;
    copain.jeu = 'ballon'; copain.jeuT = e.jeuT;
    const b = creer('ballon', (e.x + copain.x) / 2, (e.y + copain.y) / 2, {
      // `decor` pour le DESSIN seulement : il passe par la branche du decor et
      // n'entre dans aucun index — rien ne se cogne dedans, il vole.
      decor: 'ballon', r: 3, solide: false, dessine: true, a: e, b: copain, vers: copain, pause: 0,
    });
    e.ballon = b; copain.ballon = b;
  }

  /** Les deux enfants se font face pendant que le ballon fait la navette. */
  function majBallon(e) {
    const b = e.ballon, copain = e.copain;
    if (!b || !b.actif || !copain || !copain.vivant || copain.metier !== 'baigneur') {
      quitterLeJeu(e);
      return;
    }
    e.etat = 'arret'; e.minuterie = 20; e.vx = 0; e.vy = 0;
    regarder(e, copain.x - e.x, copain.y - e.y);
  }

  /** ⚠️ LE BALLON VOLE DANS LA BOUCLE DES ENTITES, pas dans la routine. Les
      routines des sortes de gens battent une image sur quinze (`majSortes`) —
      c'est le bon rythme pour DECIDER, et le pire qui soit pour un objet qui
      traverse l'air : mesure, le ballon ne bougeait que 13 images sur 400, et
      il sautait par a-coups d'un quart de seconde. */
  function majBallonVol(b) {
    const f = B.defs.pietons && B.defs.pietons.plage;
    const cible = b.vers;
    if (!f || !cible || !cible.vivant || !b.a || !b.b) { retirer(b); return; }
    if (b.pause > 0) { b.pause--; return; }
    const dx = cible.x - b.x, dy = cible.y - b.y, norme = Math.hypot(dx, dy) || 1;
    if (norme < 10) {
      b.vers = cible === b.a ? b.b : b.a;            // il renvoie
      b.pause = f.ballon_pause;
      return;
    }
    b.x += dx / norme * f.ballon_vitesse;
    b.y += dy / norme * f.ballon_vitesse;
  }

  /** LA GERBE D'UN BRIS D'AQUEDUC.

      ⚠️ Ce n'est PAS un effet de plus : c'est le `jet_eau` de la borne-fontaine
      defoncee, tel quel — il crache ses gouttes vers le haut et il TIENT son
      souffle (`Son.SFX.borne_jet`, une fois par image, a distance). Un bris
      d'aqueduc est cette gerbe-la, en pleine rue et pour une heure de jeu. La
      seule chose qu'on ajoute ici est de la faire vivre tant que le bris coule.

      ⚠️ Une seule a la fois, et seulement quand le joueur est a portee : une
      gerbe qui crache deux particules par image a l'autre bout de la ville est
      du travail qu'on fait pour personne. */
  function majAqueduc() {
    if (!B.joueur || B.interieur || !Monde.brisDAqueduc) return 0;
    const b = Monde.brisDAqueduc();
    const deja = B.entites.find(function (q) { return q.type === 'jet_eau' && q.aqueduc; });
    if (!b) { if (deja) retirer(deja); return 0; }
    const x = b.x * TT + 8, y = b.y * TT + 8;
    const loin = dist2(x, y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI;
    if (deja && !loin && deja.x === x && deja.y === y) {
      // On la RENOUVELLE au lieu de la laisser mourir : le `jet_eau` de la
      // borne s'eteint au bout de ses dix secondes, et un bris coule une heure
      // de jeu. ⚠️ Ce n'est PAS ce qui empeche l'eau de s'arreter — la branche
      // d'a cote en refait une a l'image meme ou l'autre meurt, et un juge qui
      // regarde chaque image ne voit aucun creux sans cette ligne. Elle evite
      // de jeter et refaire une entite toutes les dix secondes, rien de plus.
      deja.minuterie = JET_EAU_IMAGES;
    } else {
      if (deja) retirer(deja);
      if (loin) return 0;
      creer('jet_eau', x, y, { minuterie: JET_EAU_IMAGES, dessine: false, solide: false, r: 0, aqueduc: true });
    }
    // ⚠️ Et on se mouille en passant. La gerbe se voit et s'entend de loin,
    // mais rien ne disait qu'on avait les pieds DEDANS : c'est le seul retour
    // qu'on ait a pied, et sans lui la flaque n'etait qu'une tache peinte.
    const j = B.joueur, portee = ((b.flaque || 2) + 0.5) * TT;
    if (!j.dansVehicule && j.vivant && dist2(j.x, j.y, x, y) < portee * portee) remous(j.x, j.y, 3);
    return 1;
  }

  // --- La bagarre de gangs a leur frontiere ------------------------------------------------
  //: ⚠️ L'AUTRE MOITIE DE « LA VILLE EST COUPABLE D'ELLE-MEME ». Le vol de char
  //: se passe de travers du joueur ; celui-ci se passe SANS lui. Deux gangs se
  //: tombent dessus la ou leurs districts se touchent — `pietons.frontieres()`
  //: donne la ligne, le navigateur y trouve les deux trottoirs.
  //:
  //: ⚠️ Ce qui a coute cher n'est pas la rixe : c'est que TROIS mecanismes du
  //: depot ne connaissaient qu'une seule reponse a la violence, « s'en prendre
  //: au joueur ». `alerter` retournait contre lui toute gang a portee, `blesser`
  //: faisait de meme du blesse, et `majAttaque` y ramenait tout pieton qui
  //: finissait son coup. Chacun a maintenant son juge.

  /** Est-il en train de se battre avec l'autre gang, en ce moment meme ?

      ⚠️ Le coup lui-meme est un ETAT ('attaque', les trois temps de `Combat`) :
      ne tester que 'bagarre' aurait laisse passer les images ou l'homme frappe
      — et ce sont justement celles-la qui appellent `alerter`. */
  function enPleineRixe(e) {
    return e.etat === 'bagarre' || (e.etat === 'attaque' && e.avantLeCoup === 'bagarre');
  }

  /** Le rival le plus proche : quelqu'un de l'AUTRE gang, venu pour la meme
      rixe, encore debout. */
  function rivalDe(e, f) {
    let meilleur = null, dMin = f.rival_px * f.rival_px;
    for (const q of pietonsAutour(e.x, e.y, f.rival_px)) {
      if (!q.bagarre || !q.vivant || q.etat === 'assomme' || !q.gang || q.gang === e.gang) continue;
      const d = dist2(e.x, e.y, q.x, q.y);
      if (d < dMin) { dMin = d; meilleur = q; }
    }
    return meilleur;
  }

  /** Le trottoir le plus proche de la ligne, du cote demande : -1 vers l'ouest
      (ou le nord), +1 vers l'est (ou le sud).

      ⚠️ On cherche EN TRAVERS et pas en couronne : la frontiere passe au milieu
      d'une rue, et `trottoirLePlusProche` aurait aussi bien rendu le trottoir
      d'en face — les deux camps seraient nes du meme bord. */
  function bordDeLaFrontiere(ligne, le, sens, recul) {
    const vertical = ligne.axe === 'v';
    for (let k = 1; k <= recul; k++) {
      const tx = vertical ? ligne.x + sens * k : le;
      const ty = vertical ? le : ligne.y + sens * k;
      if (Monde.marchablePieton(tx, ty)) return { tx: tx, ty: ty };
    }
    return null;
  }

  /** Une frontiere a portee de vue, avec un trottoir de chaque bord. */
  function frontiereProche(x, y, f) {
    const lignes = (B.defs.pietons && B.defs.pietons.frontieres) || [];
    const jx = Math.floor(x / TT), jy = Math.floor(y / TT);
    for (const ligne of lignes) {
      const vertical = ligne.axe === 'v';
      const debut = vertical ? ligne.y : ligne.x;
      // Le point de la ligne le plus proche du joueur, sans sortir du segment.
      const le = Math.min(debut + ligne.long - 1, Math.max(debut, vertical ? jy : jx));
      const cx = (vertical ? ligne.x : le) * TT + 8, cy = (vertical ? le : ligne.y) * TT + 8;
      const d = Math.hypot(cx - x, cy - y);
      // ⚠️ Assez pres pour qu'on la voie se battre, assez loin pour que
      // personne n'apparaisse sous les yeux du joueur : une rixe hors champ est
      // du travail fait pour personne (la lecon du vol de char), une rixe qui
      // se materialise dans son dos est un bogue qu'il voit.
      if (d > f.rayon_px || d < f.trop_pres_px) continue;
      const a = bordDeLaFrontiere(ligne, le, -1, f.recul_tuiles);
      const b = bordDeLaFrontiere(ligne, le, 1, f.recul_tuiles);
      if (a && b) return { ligne: ligne, a: a, b: b };
    }
    return null;
  }

  /** Deux gangs se tombent dessus a leur frontiere. Rend le nombre d'hommes nes. */
  function allumerLaBagarre(f) {
    const lieu = frontiereProche(B.joueur.x, B.joueur.y, f);
    if (!lieu) return 0;
    const gangs = (B.defs.pietons && B.defs.pietons.gangs) || [];
    const vertical = lieu.ligne.axe === 'v';
    let nes = 0;
    for (const cote of ['a', 'b']) {
      const slug = lieu.ligne[cote];
      const bande = gangs.find(function (q) { return q.slug === slug; });
      const arch = bande && archetype(bande.pieton);
      if (!arch) continue;
      const bord = lieu[cote];
      for (let k = 0; k < f.membres; k++) {
        // Ils s'etalent LE LONG de la rue, pas en travers : un camp est une
        // ligne qui fait face a l'autre, pas une grappe.
        const glisse = (k - (f.membres - 1) / 2) * f.ecart_px;
        const px = bord.tx * TT + 8 + (vertical ? 0 : glisse);
        const py = bord.ty * TT + 8 + (vertical ? glisse : 0);
        if (!Monde.marchablePieton(Math.floor(px / TT), Math.floor(py / TT))) continue;
        // ⚠️ PERSONNE N'APPARAIT A L'ECRAN. La fenetre de la fiche l'assure
        // depuis la LIGNE, mais on nait sur le trottoir — jusqu'a six tuiles en
        // deca —, et c'est cet ecart-la qui ramenerait un homme dans la vue.
        if (visibleAEcran(px, py, 24)) continue;
        const e = creerPieton(px, py, arch);
        if (!e) continue;
        e.bagarre = true;
        // ⚠️ ILS NE SONT PAS LA FOULE : ils sont venus pour ca, comme l'ouvrier
        // a son chantier et l'homme-sandwich a son poste. Sans cette marque, six
        // hommes de plus passent par-dessus le plafond de passants — et le juge
        // de la foule a deja attrape exactement cette faute, une fois.
        e.metier = 'bagarre';
        e.etat = 'bagarre';
        e.bagarreT = f.duree_images;
        e.rival = null;
        e.cri = 90;
        nes++;
      }
    }
    if (nes) indexer();
    return nes;
  }

  /** Il n'y a plus personne en face, ou le temps est fait : on s'en va. */
  function finirLaBagarre(e) {
    e.etat = 'flane';
    e.rival = null;
    e.vx = 0; e.vy = 0;
  }

  /** Une rixe par minute de jeu, au plus, et jamais deux a la fois.

      ⚠️ Une minute de jeu dure un tiers de seconde : ce passage-ci, toutes
      les 30 images, en voit une neuve a chaque fois. C'est donc DEUX TIRAGES
      PAR SECONDE, et `chance_par_minute` se lit a cette cadence-la
      (`pietons.BAGARRE`, et son juge).

      ⚠️ Le tirage se fait a l'EMPREINTE de la minute, jamais au de du jeu : un
      decor qui consomme `B.rng()` decale tous les des qui suivent, et cette
      lecon-la a fait tomber quatre juges sans rapport le jour du char en panne. */
  function majBagarre() {
    const f = B.defs.pietons && B.defs.pietons.bagarre;
    if (!f || !B.joueur || B.interieur || !B.partie) return 0;
    const minute = Math.floor(B.partie.heure * 24 * 60);
    if (B.rixeMinute === minute) return 0;
    B.rixeMinute = minute;
    // Une seule a la fois : deux rixes dans la meme rue, ce n'est plus une ville
    // qui vit, c'est une ville en guerre.
    if (B.entites.some(function (q) { return q.bagarre && q.vivant; })) return 0;
    if (hash2(B.partie.jour * 1451 + minute, 0xBA6A) / 4294967296 >= f.chance_par_minute) return 0;
    return allumerLaBagarre(f);
  }

  /** Les hommes-sandwichs : un par poste (`carte.reclames`), le jour, dans la
      bulle du joueur. Il nait A SON POSTE et hors champ — sauf au premier
      instant d'une partie (`dabord`), ou personne ne regarde encore — et il
      s'oublie comme tout le monde quand on s'eloigne : le poste le refait
      naitre quand on revient. Le boniment qu'il crie est celui de son kiosque
      (`ambulants[].reclame`) ; un kiosque qui n'en a pas ne recrute pas. */
  function naitreLesHommesSandwichs(dabord) {
    const def = Monde.carte && Monde.carte.def, arch = archetype('homme_sandwich');
    if (!def || !def.reclames || !arch || !B.joueur || !enService(arch.heures)) return 0;
    let nes = 0;
    for (const poste of def.reclames) {
      const x = poste.x * TT + 8, y = poste.y * TT + 8;
      if (dist2(x, y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI) continue;
      if (!dabord && visibleAEcran(x, y, 24)) continue;
      if (B.entites.some(function (q) { return q.type === 'pieton' && q.reclame === poste && q.vivant; })) continue;
      if (!placeLibre(x, y)) continue;
      const commerce = (B.defs.ambulants || []).find(function (c) { return c.slug === poste.commerce; });
      const e = creerPieton(x, y, arch);
      e.reclame = poste;
      e.kiosque = poste.commerce;
      e.boniment = (commerce && commerce.reclame) || '';
      ajouterA(grille, e);
      nes++;
    }
    return nes;
  }

  /** Les ouvriers du chantier du jour : un ou deux, plantes sur la voie
      fermee, dans la bulle du joueur.

      ⚠️ **INTOUCHABLES, comme les enfants.** Un chantier ou l'on fauche
      l'equipe au premier passage n'est pas un chantier, c'est une cible — et
      la ville n'a rien a gagner a ca. C'est une propriete de l'ENTITE, pas de
      l'archetype : un ouvrier qui rentre chez lui, lui, est un passant comme
      un autre.

      ⚠️ Et ils ne comptent pas dans la foule : ils ont un poste, comme
      l'homme-sandwich. */
  function naitreLesOuvriers() {
    const b = Monde.entraveDuJour && Monde.entraveDuJour();
    const arch = archetype('ouvrier');
    if (!b || b.slug !== 'entrave' || !arch || !B.joueur || B.interieur) return 0;
    const x = (b.x + b.l / 2) * TT, y = (b.y + b.h / 2) * TT;
    if (dist2(x, y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI) return 0;
    const deja = B.entites.filter(function (q) { return q.chantier && q.vivant; }).length;
    if (deja >= 2) return 0;
    let nes = 0;
    for (let k = deja; k < 2; k++) {
      // Le long de la voie fermee, un par bout.
      const px = b.l > b.h ? (b.x + (k ? b.l - 1 : 0)) * TT + 8 : (b.x + b.l / 2) * TT;
      const py = b.h > b.l ? (b.y + (k ? b.h - 1 : 0)) * TT + 8 : (b.y + b.h / 2) * TT;
      if (visibleAEcran(px, py, 24)) continue;
      const e = creerPieton(px, py, arch);
      e.chantier = true;
      e.intouchable = true;
      e.metier = 'chantier';
      e.etat = 'fige';
      e.face = 'bas';
      e.plante = { x: e.x, y: e.y };
      nes++;
    }
    if (nes) indexer();
    return nes;
  }

  /** L'ÉQUIPE d'un chantier (3e vague de « Ça travaille ») : un ouvrier planté sur
      chacun des postes que Python a choisis (`chantiers._postes`), tant que le
      joueur est dans la bulle et que le poste est hors de l'écran.

      ⚠️ **INTOUCHABLES, comme les ouvriers de la voie fermée** — et pour la même
      raison : une équipe qu'on fauche au premier passage est une cible. Et ils ne
      comptent pas dans la foule (`metier`) : ils ont un poste. Mais ⚠️ ils ne se
      marquent PAS `chantier` : `naitreLesOuvriers` compte « qui travaille » avec
      `q.chantier && q.vivant`, et l'équipe d'une voie fermée ne naîtrait plus.
      `equipeDe` porte l'id du chantier, `posteDe` le numéro du poste : c'est ce
      qui dit qu'un poste est pris. */
  function naitreLEquipe(id, postes, nom) {
    const arch = archetype('ouvrier');
    if (!arch || !B.joueur || B.interieur) return 0;
    let nes = 0;
    postes.forEach(function (p, k) {
      // Le poste de la palette s'appelle `'signal'` (4e vague) : il ne se confond
      // pas avec les postes numérotés de l'équipe du terrain.
      const poste = nom === undefined ? k : nom;
      const x = p[0] * TT + 8, y = p[1] * TT + 8;
      if (dist2(x, y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI) return;
      if (visibleAEcran(x, y, 24)) return;
      if (B.entites.some(function (q) { return q.equipeDe === id && q.posteDe === poste && q.vivant; })) return;
      const e = creerPieton(x, y, arch);
      e.metier = 'chantier';
      e.intouchable = true;
      e.etat = 'fige';
      e.face = 'bas';
      e.plante = { x: e.x, y: e.y };
      e.equipeDe = id;
      e.posteDe = poste;
      nes++;
    });
    if (nes) indexer();
    return nes;
  }

  /** Combien de flaneurs la rue veut, ici et maintenant.

      ⚠️ ECRIT UNE FOIS. `peupler` avait son calcul ; l'attroupement, qui fait
      NAITRE des badauds quand la rue est vide, aurait eu le sien — et deux
      regles qui disent « combien de monde » se contredisent le jour ou l'une
      bouge. Le juge de la foule (`test_la_rue_se_peuple_puis_s_oublie`) a
      attrape exactement ca : trente et une personnes pour un plafond de
      vingt-huit, parce que le cercle naissait EN DEHORS du budget. */
  function fouleVoulue() {
    const zone = B.joueur ? Monde.zoneA(B.joueur.x, B.joueur.y) : null;
    return Math.min(MAX_PIETONS, zone ? zone.pietons : 12) * Monde.rythme(zone);
  }

  /** Combien de flaneurs vivent dans la bulle en ce moment. */
  function foule() {
    let n = 0;
    for (const e of B.entites) if (e.type === 'pieton' && e.vivant && !e.metier) n++;
    return n;
  }

  // ⚠️ LA BRUME N'EST PAS UNE FOULE (Martin, 21 sept. 2026 : treize filles en
  // grappe sur le quai). Elle a un `metier`, donc `foule` ne la compte pas, et
  // elle ne rentre jamais par une porte : sans plafond a elle, chaque passant
  // qui rentrait chez lui la nuit laissait une chance sur cinq d'une fille de
  // plus, et aucune ne repartait. Quelques-unes dans la bulle, chacune son coin
  // (dix tuiles, un tiers d'ecran).
  const BRUME_MAX = 3, BRUME_ECART = 160;

  /** Une fille neuve peut-elle prendre un coin ici ? Pas si la bulle en a deja
      assez, ni si une autre tient le coin d'a cote. Ne tire aucun de. */
  function coinDeBrumeLibre(x, y) {
    let n = 0;
    for (const e of B.entites) {
      if (e.type !== 'pieton' || e.metier !== 'compagnie' || !e.vivant) continue;
      if (++n >= BRUME_MAX) return false;
      const coin = e.poste || e;
      if (dist2(coin.x, coin.y, x, y) < BRUME_ECART * BRUME_ECART) return false;
    }
    return true;
  }

  /** Garde la rue peuplee : on nait hors champ, on s'oublie hors de la bulle. */
  function peupler() {
    let vivants = 0;
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const e = B.entites[i];
      if (e.type !== 'pieton') continue;
      const loin = dist2(e.x, e.y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI;
      // Les personnages de l'histoire, les figurants d'une mission, les
      // marchands derriere leur comptoir et le client d'un boulot ne s'oublient
      // pas : ils attendent. ⚠️ Le client s'oubliait : on prenait le mauvais
      // coin de rue pour le rejoindre, et la course tombait « IL N'EST PLUS LA ».
      // ⚠️ Le marchand s'oubliait comme un passant : on debarquait de l'autobus
      // et les neuf comptoirs de la ville se vidaient a la premiere image.
      if (loin && !e.personnage && !e.mission && !e.commerce && !e.client && !visibleAEcran(e.x, e.y, 40)) {
        // ⚠️ Un enfant oublie EMPORTE son ballon : sans ca, la balle reste a
        // voler toute seule au bord de l'eau, pour toujours.
        if (e.metier === 'baigneur') quitterLeJeu(e);
        retirer(e); continue;
      }
      if (e.vivant && !e.metier) vivants++;
    }
    // Les hommes-sandwichs ne comptent pas dans la foule : ils ont un poste.
    if (B.t % 30 === 0) naitreLesHommesSandwichs(false);
    if (B.t % 30 === 0) majKiosques();
    if (B.t % 45 === 0) naitreLesOuvriers();
    if (B.t % 60 === 0) naitreLesEnfantsDeLaPlage();
    if (B.t % 60 === 30) naitreLesEnfantsAVelo();
    if (B.t % 30 === 0) naitreLaFoire();
    if (B.t % 40 === 0) naitreLesBetes();
    if (B.t % 30 === 0) majVolDeChar();
    if (B.t % 30 === 0) majBagarre();
    if (B.t % 30 === 0) majAqueduc();
    if (B.t % 90 === 0) naitreLesSortes();
    if (B.t % 30 === 0) naitreLeLastCall();
    if (B.t % 120 === 0) rentrerLesJournaux();
    majSortes();
    // ⚠️ Une part de l'oubli passe par les PORTES : sinon la ville se vide
    // toujours de la meme facon (par distance) et on n'aurait ajoute qu'une
    // animation. Un flaneur sur le retour se choisit une porte et rentre.
    if (B.t % 45 === 0) quelquUnRentre();
    const zone = Monde.zoneA(B.joueur.x, B.joueur.y);
    if (vivants >= fouleVoulue() || B.t % 12 !== 0) return;
    const place = placeDeNaissance();
    if (!place) return;
    // ⚠️ Ne dans la porte : le battant s'ouvre AVANT qu'on le voie sortir.
    const sortie = place.porte
      ? { x: place.porte.x, y: place.porte.y, t: 0 } : null;
    if (sortie) Monde.ouvrirPorte(sortie.x, sortie.y);
    // La nuit, pres du bar et du port, la Brume a ses habituees. ⚠️ Le coin se
    // lit APRES le de : un refus retombe sur la naissance ordinaire, qui tire
    // ce qu'elle tirait deja.
    const nuit = Monde.estNuit();
    if (nuit && zone && zone.brume && B.rng() < 0.18 && coinDeBrumeLibre(place.x, place.y)) {
      const fille = archetype('racoleuse');
      if (fille) {
        const e = creerPieton(place.x, place.y, fille);
        e.etat = 'arret';
        e.minuterie = 600;
        if (sortie) e.sortie = sortie;
        return;
      }
    }
    // Sur le territoire d'une gang, ce sont ses membres qui trainent dehors.
    const gang = zone && zone.gang && !(B.partie && B.partie.faubourgLibere) && B.rng() < 0.5
      ? (B.defs.pietons.gangs.find(function (g) { return g.slug === zone.gang; }) || null)
      : null;
    const ne = creerPieton(place.x, place.y, gang ? archetype(gang.pieton) : null);
    if (ne && sortie) ne.sortie = sortie;
  }

  /** Un flaneur qui se choisit une porte et rentre chez lui.

      ⚠️ C'est ce qui remplace une part de l'oubli par distance. Sans ca, la
      ville se viderait toujours de la meme facon — par eloignement — et on
      n'aurait ajoute qu'une animation.

      Le RYTHME s'en sert : on sort le matin, on rentre le soir. `B.partie.heure`
      va de 0 a 1 sur la journee. */
  function quelquUnRentre() {
    const carte = Monde.carte, j = B.joueur;
    if (!j || B.interieur || !carte.portesFermees.length) return null;
    const heure = (B.partie && B.partie.heure) || 0;
    // Le soir et la nuit, on rentre ; au petit matin, presque personne.
    const envie = heure > 0.66 || heure < 0.2 ? 0.55 : heure > 0.45 ? 0.25 : 0.08;
    if (B.rng() > envie) return null;
    const flaneurs = B.entites.filter(function (e) {
      return e.type === 'pieton' && e.vivant && e.etat === 'flane'
        && !e.metier && !e.personnage && !e.mission && !e.porteBut && !e.sortie;
    });
    if (!flaneurs.length) return null;
    const e = flaneurs[Math.floor(B.rng() * flaneurs.length)];
    return envoyerAUnePorte(e) ? e : null;
  }

  /** Envoie quelqu'un vers la porte ouvrable la plus proche. Rend faux s'il n'y
      en a aucune a portee.

      ⚠️ Extrait de `quelquUnRentre` pour LE STOOL : lui ne rentre pas souper,
      il va se servir du telephone — mais c'est exactement le meme trajet, et
      deux facons de marcher vers une porte auraient fini par diverger. */
  function envoyerAUnePorte(e) {
    const carte = Monde.carte;
    if (!e || !carte.portesFermees || !carte.portesFermees.length) return false;
    let meilleure = null, dMin = 260 * 260;
    for (const porte of carte.portesFermees) {
      const d = dist2(porte.x * TT + 8, (porte.y + 1) * TT + 8, e.x, e.y);
      if (d >= dMin || !porteQuiSert(porte)) continue;
      if (!Monde.marchablePieton(porte.x, porte.y + 1)) continue;
      dMin = d; meilleure = porte;
    }
    if (!meilleure) return false;
    e.porteBut = meilleure; e.porteT = 0; e.porteBloque = 0;
    return true;
  }

  /** Les paquets caches qu'on n'a pas encore ramasses. */
  function creerPaquets(def) {
    (def.paquets || []).forEach(function (q) {
      if (B.partie.paquets[q.numero]) return;
      creer('paquet', q.x * TT + 8, q.y * TT + 12, { numero: q.numero, r: 4, solide: false, decor: 'paquet', dessine: true });
    });
  }

  //: Le marchand a les pieds 11 px au-dessus de l'ancre de son kiosque : le
  //: comptoir couvre ses jambes, ses yeux passent sous le toit (voir
  //: `cabane_fruits_de_mer`, sprites.js).
  const VENDEUR_DERRIERE = 11;

  /** Les kiosques et les camions de la carte, avec quelqu'un derriere — s'ils
      sont ouverts. Personne ne regarde encore : le marchand d'un kiosque ouvert
      est deja a son comptoir. */
  function creerAmbulants(def) {
    (def.ambulants || []).forEach(function (a) {
      const commerce = (B.defs.ambulants || []).find(function (c) { return c.slug === a.slug; });
      if (!commerce) return;
      const fiche = DECORS[commerce.sprite] || {};
      const etal = creer('ambulant', a.x * TT + 8, a.y * TT + 15, {
        decor: commerce.sprite, slug: a.slug, r: fiche.r === undefined ? 10 : fiche.r,
        solide: true, dessine: true, vendeur: null,
      });
      ajouterA(grilleFixe, etal);
      if (enService(commerce.heures)) posterLeVendeur(etal);
    });
  }

  function posterLeVendeur(etal) {
    const vendeur = creerPieton(etal.x, etal.y - VENDEUR_DERRIERE, archetype('vendeur'));
    vendeur.etat = 'fige';
    vendeur.face = 'bas';
    vendeur.commerce = etal.slug;
    etal.vendeur = vendeur;
    return vendeur;
  }

  /** ⚠️ UN KIOSQUE FERME N'A PERSONNE DERRIERE. Retour de Martin, capture a
      l'appui (17 sept. 2026) : la cabane a fruits de mer fermee, et son
      marchand au comptoir. Il y etait pose au chargement et n'en partait
      jamais ; ACTION repondait « FERME » a quelqu'un qui attendait de servir.

      A la fermeture, il plie bagage. Hors champ, il s'efface ; sous nos yeux,
      il s'en va a pied vers une porte, et la foule l'oublie ensuite comme un
      passant. A l'ouverture, un marchand revient — HORS CHAMP seulement :
      personne ne nait sous le regard, et un kiosque qu'on fixe a l'heure
      d'ouvrir reste vide tant qu'on le fixe.

      ⚠️ Le lien passe par le KIOSQUE (`etal.vendeur`), pas par le slug : trois
      kiosques a hot-dogs portent le meme. Et un marchand couche ou en fuite se
      detache aussi a la fermeture : sans ca, le kiosque dont on a assomme le
      vendeur restait vide pour toute la partie. */
  function majKiosques() {
    for (let i = 0; i < B.entites.length; i++) {
      const etal = B.entites[i];
      if (etal.type !== 'ambulant') continue;
      const commerce = (B.defs.ambulants || []).find(function (c) { return c.slug === etal.slug; });
      const ouvert = enService(commerce && commerce.heures);
      const v = etal.vendeur;
      if (!ouvert && v) {
        etal.vendeur = null;
        v.commerce = null;
        if (!v.vivant || v.etat !== 'fige') continue;
        if (!visibleAEcran(v.x, v.y, 24)) { retirer(v); i = B.entites.indexOf(etal); continue; }
        v.etat = 'flane';
        v.plante = null;
        v.allure = 1;
        envoyerAUnePorte(v);
      } else if (ouvert && !v && !visibleAEcran(etal.x, etal.y - VENDEUR_DERRIERE, 24)) {
        posterLeVendeur(etal);
      }
    }
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
  /** Une tuile qui arrete CETTE entite : le sol, ou une barriere fermee
      qu'elle aborde de l'exterieur (`Monde.barriereBloque`). */
  function bloquePour(e, tx, ty, masque) { return Monde.bloque(tx, ty, masque) || Monde.barriereBloque(e, tx, ty); }

  function deplacerCercle(e, dx, dy, masque) {
    const r = e.r;
    if (dx !== 0) {
      e.x += dx;
      const ty0 = Math.floor((e.y - r) / TT), ty1 = Math.floor((e.y + r - 0.01) / TT);
      if (dx > 0) {
        const tx = Math.floor((e.x + r) / TT);
        for (let ty = ty0; ty <= ty1; ty++) if (bloquePour(e, tx, ty, masque)) { e.x = tx * TT - r - 0.01; break; }
      } else {
        const tx = Math.floor((e.x - r) / TT);
        for (let ty = ty0; ty <= ty1; ty++) if (bloquePour(e, tx, ty, masque)) { e.x = (tx + 1) * TT + r + 0.01; break; }
      }
    }
    if (dy !== 0) {
      e.y += dy;
      const tx0 = Math.floor((e.x - e.r) / TT), tx1 = Math.floor((e.x + e.r - 0.01) / TT);
      if (dy > 0) {
        const ty = Math.floor((e.y + r) / TT);
        for (let tx = tx0; tx <= tx1; tx++) if (bloquePour(e, tx, ty, masque)) { e.y = ty * TT - r - 0.01; break; }
      } else {
        const ty = Math.floor((e.y - r) / TT);
        for (let tx = tx0; tx <= tx1; tx++) if (bloquePour(e, tx, ty, masque)) { e.y = (ty + 1) * TT + r + 0.01; break; }
      }
    }
    bloquerParDecor(e);
  }

  function bloquerParDecor(e) {
    for (const d of decorAutour(e.x, e.y, e.r + PORTEE_DECOR)) {
      if (d === e) continue;
      // ⚠️ L'index porte maintenant du NON solide (voir `estIndexable`) : on
      // traverse un buisson comme avant, on ne se cogne que sur du solide.
      if (!d.solide) continue;
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
    // Le petit train de la foire : il roule, donc il n'est pas dans l'index du
    // decor — mais on ne passe pas au travers d'un wagon non plus.
    Foire.bloquer(e);
  }

  // --- La foule ne se traverse pas -------------------------------------------------

  /** Debout dans la foule : ni mort, ni assomme, ni au volant. ⚠️ On marche
      SUR un cadavre — c'est deja la regle du tri au dessin — alors un corps a
      terre ne pousse personne et ne se fait pousser par personne. */
  /** A-t-il les pieds dans l'eau ? ⚠️ On le LIT sous ses pieds a chaque image,
      on ne le retient pas dans un drapeau : un etat qu'il faut penser a remettre
      a zero est un etat qu'on oublie de remettre a zero, et le joueur serait
      reste nageur sur le trottoir. */
  function dansLEau(e) {
    return Monde.estEau(Math.floor(e.x / TT), Math.floor(e.y / TT));
  }

  /** Les eclaboussures : a l'entree dans l'eau, et pendant qu'on nage. */
  function remous(x, y, nombre) {
    for (let i = 0; i < nombre; i++) {
      const a = B.rng() * Math.PI * 2, v = 0.3 + B.rng() * 1.1;
      particule(x, y, Math.cos(a) * v, Math.sin(a) * v * 0.5,
                12 + B.rng() * 10, i % 3 ? '#cfe6f4' : '#8ab4cc', 1, 0.05);
    }
  }

  /** Met `e.nage` a jour, et fait le bruit et les remous a l'image ou il ENTRE
      dans l'eau. Rend true cette image-la.

      ⚠️ UN SEUL ENDROIT, et c'est tout l'interet : `police.js` pose lui aussi
      `a.nage` avant de deplacer son agent (il lui faut le masque du nageur tout
      de suite). Quand chacun lisait la transition de son cote, le premier la
      mangeait — et l'agent qui se jetait a l'eau derriere toi le faisait sans
      un bruit.

      ⚠️ Le son est POSE dans le monde (`jouerA`) : celui qui plonge a dix
      tuiles ne s'entend pas comme celui qui plonge a tes pieds. Le joueur, lui,
      a son propre plongeon dans `majJoueur` — avec son filet synthetise. */
  function mouiller(e) {
    const avant = e.nage;
    e.nage = dansLEau(e);
    if (!e.nage || avant) return false;
    remous(e.x, e.y, 8);
    Son.jouerA('plongeon', e.x, e.y);
    return true;
  }

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
    // ⚠️ Couche dans son lit, le joueur ne se fait pas sortir du lit a coups
    // d'epaule : c'est lui qui se leve, et seulement quand il pousse le stick.
    if ((e.alite || e.assis) && e.type === 'joueur') return false;
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
      const x0 = e.x, y0 = e.y;
      deplacerCercle(e, e.pousseX * k, e.pousseY * k, Monde.MASQUE_PIETON);
      dansLaCarte(e);
      // ⚠️ La foule ne pousse pas l'enfant a velo sur la rue. Au coin, ceux qui
      // attendent la traverse le serraient contre le poteau du feu, et il finissait
      // un pixel sur les bandes, coince la : il garde sa place, l'autre cede.
      if (e.metier === 'cycliste' && roulableEnfant(Math.floor(x0 / TT), Math.floor(y0 / TT))
          && !roulableEnfant(Math.floor(e.x / TT), Math.floor(e.y / TT))) { e.x = x0; e.y = y0; }
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
    // Une barriere fermee s'enjambe aussi — apres avoir pousse une seconde,
    // et l'etoile tombe a la retombee (`majEnjambe`).
    let barriere = Monde.barriereEnjambable(e, tx, ty);
    if (!Monde.estEnjambable(tx, ty) && !barriere) return null;
    // Derriere la cloture : une tuile ou l'on peut retomber. Deux grillages
    // colles ne s'enjambent pas d'un coup — on en franchit un, puis l'autre.
    const ax = tx + sx, ay = ty + sy;
    if (Monde.bloque(ax, ay, Monde.MASQUE_PIETON)) return null;
    // ⚠️ RESQUILLER : enjamber la palissade de la foire sans billet coute ce que
    // coute de forcer l'arche, a la retombee (`majEnjambe`).
    if (!barriere && e === B.joueur && Monde.resquille) barriere = Monde.resquille(tx, ty, ax, ay);
    return { sx: sx, sy: sy, tx: tx, ty: ty, ax: ax, ay: ay, barriere: barriere };
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
                  x0: e.x, y0: e.y, x1: x1, y1: y1, barriere: c.barriere || null };
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
    if (part >= 1) {
      e.enjambe = null; e.z = 0; Son.SFX.pas();
      // La retombee de l'autre cote d'une barriere : c'est la que ca se paie.
      if (en.barriere) {
        e.forceT = 30; e.buteT = 0;
        if (e === B.joueur) {
          if (en.barriere.forcer && en.barriere.forcer.etoiles) Police.etoilesAuMoins(en.barriere.forcer.etoiles);
          Hud.message(en.barriere.raison + ' — FRANCHI', 150);
        }
      }
    }
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

  /** A bout de souffle, on coule. ⚠️ Et on coule COMME ON TOMBE :
      `Missions.hopital` fait deja tout — la facture, la police remise a zero, le
      boulot abandonne, le fondu et le reveil. Une deuxieme facon de perdre
      connaissance aurait sa propre facture, ses propres oublis, et le jour ou
      l'une des deux change, l'autre ment. */
  function noyade(j) {
    remous(j.x, j.y, 16);
    // Le moment le plus grave que l'eau produit : il ne peut pas etre muet.
    Son.SFX.couler();
    j.vx = 0; j.vy = 0;
    // ⚠️ LE DEUXIEME JOUEUR NE VA PAS A L'URGENCE : elle change de scene, et
    // une scene est au joueur 1 (Martin, 22 sept.). Il boit la tasse, on le
    // repose au sec, K.-O. — comme un coup de trop (`blesser`, `majJoueur`).
    if (j !== B.joueur) {
      const sec = trottoirLePlusProche(Math.floor(j.x / TT), Math.floor(j.y / TT));
      if (sec) { j.x = sec.x; j.y = sec.y; }
      j.nage = false;
      j.endurance = B.defs.recherche.vitesses.endurance;
      assommer(j);
      return;
    }
    Missions.hopital(null);
  }

  // --- Joueur ---------------------------------------------------------------------------

  /** Couche le joueur dans un lit, la tete sur l'oreiller de la tuile (tx, ty) —
      la tuile de TETE, celle ou naît le malade (`carte.ASSIS_OU_COUCHE`).

      ⚠️ C'est le corps du malade, trait pour trait : la pose `alite`, les pieds
      a `PIEDS_ALITE`, pas d'ombre sur la couverture (`dessiner`), et personne ne
      le pousse hors du lit (`cede`). Ce qui le leve, c'est `majJoueur`. */
  function coucher(j, tx, ty) {
    j.x = tx * TT + 8; j.y = ty * TT + PIEDS_ALITE;
    j.vx = 0; j.vy = 0; j.roule = 0;
    // ⚠️ Le coup qui nous a mis a terre laisse un `recul`, et le joueur ne le
    // decompte nulle part : couche avec, on dormait PENCHE de 0,22 rad,
    // en travers de l'oreiller.
    j.recul = 0;
    j.nage = false;                    // on a coule : le remous resterait sous le lit
    j.face = 'alite';
    j.alite = { x: tx, y: ty };
  }

  /** Se lever : les pieds A COTE du lit, du cote ou l'on pousse (dx, dy).

      ⚠️ Un meuble n'arrete personne (`Monde.estMeuble` : on PASSE dessus). Sans
      ce pas de cote, on se levait debout sur l'oreiller et on quittait le lit en
      marchant sur la couverture. On prend donc, autour des tuiles du lit, la
      tuile de plancher la plus avancee dans le sens de la poussee — a egalite,
      la premiere, pour que le banc ne tire pas a pile ou face.

      ⚠️ Seulement si l'on est ENCORE dans ce lit : ailleurs (la piece a change
      sous nous), les tuiles autour de `lit` sont celles d'une autre carte. */
  function seLever(j, dx, dy) {
    const lit = j.alite;
    j.alite = null;
    j.face = 'bas';
    if (!lit || Math.floor(j.x / TT) !== lit.x || Math.floor(j.y / TT) !== lit.y) return;
    const glyphe = Monde.glyphe(lit.x, lit.y);
    let pied = lit.y;
    while (Monde.estMeuble(lit.x, pied + 1) && Monde.glyphe(lit.x, pied + 1) === glyphe) pied++;
    const cx = (lit.x + 0.5) * TT, cy = (lit.y + pied + 1) / 2 * TT;
    let place = null, meilleur = -Infinity;
    function essayer(tx, ty) {
      if (Monde.bloque(tx, ty, Monde.MASQUE_PIETON) || Monde.estMeuble(tx, ty)) return;
      const s = ((tx + 0.5) * TT - cx) * dx + ((ty + 0.5) * TT - cy) * dy;
      if (s > meilleur) { meilleur = s; place = { x: tx, y: ty }; }
    }
    for (let ty = lit.y; ty <= pied; ty++) { essayer(lit.x - 1, ty); essayer(lit.x + 1, ty); }
    essayer(lit.x, pied + 1);
    if (place) { j.x = place.x * TT + 8; j.y = place.y * TT + 8; }
    regarder(j, dx, dy);
  }

  function majJoueur(j) {
    // ⚠️ LES ENTREES VIENNENT DU JOUEUR QU'ON AVANCE, pas du module : en coop,
    // cette meme fonction fait marcher les deux, chacun sur son appareil
    // (`Entree.SOURCE1`/`SOURCE2`). Un joueur sans source, c'est le jeu a un :
    // on retombe sur `Entree`, ou tout se confond comme avant.
    const ent = j.entree || Entree;
    // ⚠️ Le `recul` d'un coup recu se decompte ICI, avant tout retour : seuls
    // les pietons le faisaient, et le joueur restait penche de 0,22 rad a vie
    // (retour de Martin : « mon personnage est croche »).
    if (j.recul > 0) j.recul--;
    if (j.dansVehicule) return;
    // ⚠️ LE DEUXIEME JOUEUR TOMBE K.-O., IL NE VA PAS A L'HOPITAL (`blesser`) :
    // l'urgence CHANGE DE SCENE, et une scene appartient au joueur 1. Il reste
    // couche le temps du compte, puis se releve a mi-vie, invincible une
    // seconde et demie — un joueur a terre attend son partenaire, il ne met
    // pas fin a la partie.
    if (j.etat === 'assomme') {
      j.vx = 0; j.vy = 0;
      if (--j.minuterie <= 0) {
        j.etat = 'flane'; j.face = 'bas';
        j.vie = Math.round(j.vieMax / 2);
        j.invincible = 90;
      }
      return;
    }
    // Il tient quelqu'un (SAISIR) : il ne marche pas. ⚠️ SOUS le compte du K.-O. :
    // au-dessus, un deuxieme joueur assomme en pleine prise ne se relevait jamais.
    if (j.prise) { j.vx = 0; j.vy = 0; return; }
    // ⚠️ A bord du traversier, on regarde passer la baie : la coque nous porte, et
    // l'eau sous le pont n'est pas une raison de nager (`Traversier.maj`).
    if (j.aBord) { j.vx = 0; j.vy = 0; j.nage = false; return; }
    // ⚠️ Assis dans un manège, c'est lui qui nous porte (`Foire.maj`).
    if (j.manege) { j.vx = 0; j.vy = 0; return; }
    if (majEnjambe(j)) return;                        // en haut d'une cloture : rien d'autre
    // ⚠️ La ROUE D'ARMES le cloue comme un dialogue : une seule direction et
    // un seul role a la fois — sans ca, choisir son arme au stick ferait
    // MARCHER le personnage vers son choix, au ralenti et sans le vouloir.
    // C'est aussi ce qui fait le prix de la roue : on est debout, immobile.
    // ⚠️ LE PIRATAGE CLOUE COMME LA ROUE D'ARMES : le stick choisit une
    // direction de sequence, pas un pas — s'il faisait aussi marcher le
    // personnage, on sortirait du terminal des le premier essai.
    // ⚠️ Une EPREUVE D'ADRESSE aussi (`Adresse`) : les ratons et la radio se jouent a la croix.
    if (B.cinema || B.roue || B.piratage || B.epreuve) { j.vx = 0; j.vy = 0; return; }   // on ecoute, on choisit, on pirate ou on joue
    // ⚠️ ASSIS SUR UN BANC — comme le lit, c'est le stick qui leve (`Interactions.majAssis`) ;
    // tant qu'on est assis rien ne bouge, et le pas qui suit un lever est le notre, dans la meme image.
    if (j.assis && typeof Interactions !== 'undefined' && Interactions.majAssis(j)) return;
    // ⚠️ COUCHE DANS UN LIT — le reveil a l'hopital : rien ne bouge tant qu'on
    // ne pousse pas, et la PREMIERE poussee leve. On marche dans la meme image,
    // depuis le pas de cote que `seLever` vient de poser.
    if (j.alite) {
      if (!(ent.axe.mag > 0)) { j.vx = 0; j.vy = 0; return; }
      seLever(j, ent.axe.x, ent.axe.y);
    }
    const v = B.defs.recherche.vitesses;
    const eau = B.defs.recherche.nage;
    const axe = ent.axe;
    // ⚠️ L'EAU N'EST PLUS UN MUR. Le joueur et les agents portent le masque du
    // nageur — eux seuls entrent dans la baie — et c'est le SOUFFLE qui decide
    // jusqu'ou. Voir `recherche.NAGE` : les deux nombres se jugent contre la
    // geographie, pas au gout.
    const nageait = j.nage;
    j.nage = dansLEau(j);
    // ⚠️ On entre ET on sort. L'entree jouait `choc` — la TOLE FROISSEE d'un
    // accident de char, le seul son d'eau que le jeu ait jamais eu — et la
    // sortie ne jouait rien du tout. C'est le meme plongeon des deux cotes ;
    // en sortant, une brassee suffit : on quitte l'eau, on ne la frappe pas.
    if (j.nage && !nageait) { remous(j.x, j.y, 10); Son.SFX.plongeon(); }
    else if (!j.nage && nageait) { remous(j.x, j.y, 6); Son.SFX.nage(); }
    if (j.roule > 0) {                       // roulade : on ne se dirige plus
      j.roule--;
      deplacerCercle(j, j.vx, j.vy, Monde.MASQUE_NAGEUR);
      dansLaCarte(j);
      auLarge(j);
      if (j.roule === 0) j.invincible = 6;
      return;
    }
    // ⚠️ TROIS vitesses, un seul bouton — et la COURSE EST LA VITESSE PAR
    // DEFAUT. Martin l'a dit : « on court quand meme tout le temps, avec la
    // grandeur de la carte. » Pousser le pouce a fond, ou n'importe quelle
    // touche de direction, c'est courir ; l'effleurer, c'est marcher ; le
    // bouton, c'est SPRINTER, et lui seul coute du souffle.
    const veutSprinter = ent.bas('esquive');
    const marche = axe.source !== 'clavier' && axe.mag < 0.6;
    let vitesse = marche ? v.joueur_marche : v.joueur_course;
    // ⚠️ Le cafe allonge le sprint, il ne l'accelere PAS : `joueur_sprint`
    // reste ce qu'il est, seule la DEPENSE baisse. La minuterie, elle,
    // s'ecoule dans `Missions.maj` — meme au volant.
    const cafe = j.cafeine > 0 ? B.defs.economie.cafe.depense : 1;
    // ⚠️ ON A PIED DANS LA PREMIERE TUILE. Demande de Martin : « la premiere
    // case de l'eau ne prend pas d'energie ni ne noie. » L'eau n'avait qu'une
    // profondeur — le souffle partait au premier pixel mouille, et immobile au
    // bord de la greve on coulait en 3,3 s. C'est un BORD qui manquait, celui
    // que « L'eau n'est plus un mur » promettait et n'a jamais pose : un pas
    // hors du sable ne doit pas etre un pas vers l'hopital, et l'enfant qui
    // barbote a cote de nous ne risque rien depuis le premier jour.
    // ⚠️ Ce n'est pas un abri : l'eau basse est un lisere d'une tuile, a un pas
    // de la terre — la police y arrive a pied, et elle nage pour la suite.
    const aPied = j.nage && Monde.eauBasse(Math.floor(j.x / TT), Math.floor(j.y / TT));
    if (j.nage) {
      // On patauge : c'est lent, et ca fait des remous — mais debout.
      vitesse = eau.vitesse;
      if (j.t % 9 === 0) remous(j.x, j.y + 2, 1);
    }
    if (j.nage && !aPied) {
      // ⚠️ Nager COUTE MEME IMMOBILE : on ne fait pas la planche dans la baie
      // de Baie-des-Brumes. Sans ca, s'arreter au milieu de l'eau serait un
      // moyen de refaire son souffle a l'abri de la police.
      const cout = eau.souffle_par_image * cafe;
      const surSurplus = Math.min(j.surplus || 0, cout);
      j.surplus = (j.surplus || 0) - surSurplus;
      j.endurance = Math.max(0, j.endurance - (cout - surSurplus));
      if (j.endurance <= 0 && (j.surplus || 0) <= 0) { noyade(j); return; }
    } else if (veutSprinter && !j.nage && axe.mag > 0 && (j.endurance > 0 || j.surplus > 0)) {
      vitesse = v.joueur_sprint;
      // ⚠️ Le SURPLUS part en premier : c'est la seule part de cette barre
      // qu'on ne peut pas reprendre en s'arretant, donc la seule qui vaille ce
      // qu'on l'a payee au comptoir. La base, elle, remonte toute seule.
      const cout = v.endurance_par_image * cafe;
      const surSurplus = Math.min(j.surplus || 0, cout);
      j.surplus = (j.surplus || 0) - surSurplus;
      j.endurance = Math.max(0, j.endurance - (cout - surSurplus));
    } else {
      // ⚠️ La regeneration ne touche JAMAIS au surplus : c'est ce qui fait la
      // difference entre une barre qui se remplit seule et une avance achetee.
      j.endurance = Math.min(v.endurance, j.endurance + v.endurance_par_image * 0.6);
    }
    if (j.etat === 'attaque' && !j.nage) vitesse *= 0.45;    // on frappe en marchant, pas en courant
    // ⚠️ On ne court pas avec quelqu'un dans les bras. Sans ca, le bouclier
    // humain devenait la meilleure facon de traverser la ville : plus vite que
    // la police et a l'abri de ses balles.
    if (j.otage) vitesse *= B.defs.recherche.bouclier.vitesse;
    const mag = axe.source === 'clavier' ? axe.mag : Math.min(1, axe.mag * 1.15);
    j.vx = axe.x * vitesse * mag;
    j.vy = axe.y * vitesse * mag;
    if (axe.mag > 0) regarder(j, axe.x, axe.y);
    // ⚠️ LE COURANT DU LARGE REFUSÉ (`auLarge`) : le temps qu'il nous ramène, on nage
    // où il veut, le dos tourné à l'île — c'est le « tourner de bord » du nageur.
    if (j.courant && j.courant.t > 0) {
      j.courant.t--;
      j.vx = j.courant.x * vitesse; j.vy = j.courant.y * vitesse;
      regarder(j, j.courant.x, j.courant.y);
    }
    // Pousser contre un grillage, c'est vouloir l'enjamber : une seconde en
    // haut, sans frapper, sans tirer, sans courir — et une cible immobile.
    if (axe.mag > 0 && !j.nage && enjamber(j, j.vx, j.vy)) { return; }
    const avant = { x: j.x, y: j.y };
    deplacerCercle(j, j.vx, j.vy, Monde.MASQUE_NAGEUR);
    dansLaCarte(j);
    auLarge(j);
    if (j.buteImage !== B.t) j.buteT = 0;              // on a lache la barriere
    if (j.forceT > 0) j.forceT--;
    const d = Math.hypot(j.x - avant.x, j.y - avant.y);
    j.anim.dist += d;
    j.pasDist += d;
    // Un pas sur le trottoir, une BRASSEE dans l'eau — et la brassee est plus
    // longue : a 1 px par image, une toutes les 14 px sonnerait comme une
    // machine a laver. A 34, il en part une et demie par seconde.
    if (j.pasDist > (j.nage ? 34 : 14)) { j.pasDist = 0; if (j.nage) Son.SFX.nage(); else Son.SFX.pas(); }
    if (j.invincible > 0) j.invincible--;
    if (j.flagrant > 0) j.flagrant--;
    if (j.saigne > 0) saigner(j);
  }

  //: Combien d'images le courant ramène le nageur que la ligne a arrêté.
  const COURANT_IMAGES = 45;

  /** ⚠️ LE LARGE REFUSÉ, À LA NAGE (`Monde.retenirAuLarge`) : la ligne arrête le
      nageur comme la coque, puis le courant le ramène vers la rive — la travée
      manquante du pont de l'aéroport ne se nage plus jusqu'au bout. */
  function auLarge(j) {
    const s = Monde.retenirAuLarge(j);
    if (!s) return;
    j.courant = { x: s.x, y: s.y, t: COURANT_IMAGES };
    Monde.avertirDuLarge('nage');
  }

  // --- Pietons --------------------------------------------------------------------------

  const DIRECTIONS = [[1, 0], [0, 1], [-1, 0], [0, -1]];

  // Jusqu'ou une fille de la Brume s'ecarte du coin qu'elle tient (3 tuiles).
  // L'homme-sandwich a le sien, plus large, dans `magasins.RECLAME`.
  const POSTE_RAYON = 48;

  /** L'homme-sandwich te repere et vient te solliciter — sauf s'il vient de
      le faire (`repos`), que tu es au volant, qu'on te parle deja, ou qu'un
      mur vous separe. Il regarde une image sur dix : c'est un solliciteur,
      pas un radar. Et passe ses heures, il rentre : la pancarte reste au
      kiosque, personne ne crie « approchez » a minuit. */
  function solliciter(e) {
    const r = B.defs.reclame, j = B.joueur;
    if (!enService(e.heures)) { e.etat = 'entre'; e.minuterie = 40; e.face = 'haut'; return; }
    if (e.repos > 0) { e.repos--; return; }
    if (e.t % 10 !== 0 || !r || !j || !j.vivant || j.dansVehicule || B.cinema || joueurCourt()) return;
    const portee = r.rayon_tuiles * TT;
    if (dist2(e.x, e.y, j.x, j.y) >= portee * portee || !Monde.ligneLibre(e.x, e.y, j.x, j.y)) return;
    e.etat = 'aborde'; e.butT = 0; e.abordeT = 0;
  }

  /** ⚠️ Le solliciteur n'aborde que celui qui FLANE. Quelqu'un qui court a
      autre chose a faire — et un homme-sandwich qui se jette dans les jambes
      d'un joueur au sprint le ralentissait de dix pour cent (un juge de cafe
      l'a mesure) : la police le rattrapait a cause d'une pancarte. */
  function joueurCourt() {
    const j = B.joueur;
    return !!j && Math.hypot(j.vx, j.vy) > B.defs.recherche.vitesses.joueur_marche + 0.05;
  }

  /** L'indice de DIRECTIONS le plus proche d'un vecteur. */
  function directionVers(dx, dy) {
    if (Math.abs(dx) > Math.abs(dy)) return dx > 0 ? 0 : 2;
    return dy > 0 ? 1 : 3;
  }

  /** La dalle continue-t-elle par la ? LA TUILE VOISINE, pas un bord de corps.

      ⚠️ La flanerie sonde `e.x + dir * (e.r + 4)` — le bord du corps. Pour un
      ENFANT (r = 4), ces huit pixels depuis le milieu d'une tuile de seize
      retombent PILE sur la bordure, et vers l'ouest ou le nord le plancher
      rend la tuile qu'on occupe DEJA. Sondee ainsi, la dalle repondait
      toujours oui derriere soi, le demi-tour etait toujours accepte, et deux
      enfants sur quatorze restaient a trembler sur leur pas de porte. Un
      voisinage se compte en tuiles. */
  function dalleDans(tx, ty, k) {
    const d = DIRECTIONS[k];
    const ax = tx + d[0], ay = ty + d[1];
    return Monde.estTrottoir(ax, ay) && !Monde.bloque(ax, ay, Monde.MASQUE_PIETON);
  }

  /** Vers ou se tourne celui qui RENONCE A DEBORDER sur l'abord : la ou la
      dalle continue. Le demi-tour d'abord — c'est l'ancienne regle, et elle
      vaut partout ou le trottoir continue derriere soi.

      ⚠️ **LE DEMI-TOUR SEUL EST UN PIEGE**, et il tenait des passants devant
      les portes POUR TOUJOURS. `carte.py` pave l'abord jusqu'a la dalle sous
      chaque porte : le pas d'une porte est donc UNE tuile de trottoir entre
      deux tuiles d'abord. Est et ouest y debordent tous les deux, le demi-tour
      renvoyait de l'un a l'autre, et chaque renoncement remet `butT` a trente
      images — le flaneur ne retirait donc JAMAIS sa direction au sort. Il
      tremblait sur place a deux pixels pres, le sud libre devant lui.

      Mesure : douze passants poses sur douze pas de porte, onze n'avaient pas
      quitte leur tuile au bout de 1200 images. Et une naissance sur trois se
      fait sur un pas de porte (`placeDeNaissance`) : ils s'y empilaient. */
  function versLaDalle(e, tx, ty) {
    const demiTour = (e.dir + 2) % 4;
    if (dalleDans(tx, ty, demiTour)) return demiTour;
    const choix = [];
    for (let k = 0; k < 4; k++) if (k !== e.dir && k !== demiTour && dalleDans(tx, ty, k)) choix.push(k);
    // ⚠️ **PAS UN SEUL DE.** Le hasard de la ville est une file PARTAGEE, et
    // des juges la comptent (`test_une_panne_ne_tire_pas_un_seul_de_du_jeu`) :
    // un de de plus tire ici decale tout ce qui le suit — l'attroupement, le
    // budget d'une bagarre, la panne d'un char. Son age en images departage
    // aussi bien, et il ne coute rien.
    return choix.length ? choix[e.t % choix.length] : demiTour;
  }

  //: Le va-et-vient des portes, en images.
  const SORTIE_IMAGES = 26;

  /** Sortir d'une porte, ou y rentrer. Rend vrai si le pieton est occupe.

      ⚠️ **Une sortie visible est ce qui justifie qu'une porte s'ouvre**, et une
      porte qui s'ouvre est ce qui rend la sortie croyable. Les deux ensemble,
      ou ni l'une ni l'autre. */
  function majPorte(e) {
    if (e.sortie) {
      // Il vient de naitre DANS la porte : invisible tant qu'elle s'ouvre,
      // puis il avance d'une tuile et elle se referme derriere lui.
      e.sortie.t++;
      const ouvert = Monde.battant(e.sortie.x, e.sortie.y);
      e.dessine = ouvert > 0.35;
      if (e.sortie.t > SORTIE_IMAGES) { e.sortie = null; e.dessine = true; return false; }
      if (e.dessine) {
        e.vx = 0; e.vy = B.defs.recherche.vitesses.pieton * e.allure;
        deplacerCercle(e, e.vx, e.vy, masqueDe(e));
        regarder(e, 0, 1);
      }
      return true;
    }
    if (!e.porteBut) return false;
    // ⚠️ UN HOMME ASSOMME NE CONTINUE PAS SON CHEMIN. Ca ne comptait guere tant
    // qu'il s'agissait de rentrer souper ; depuis le stool, c'est la seule
    // facon de l'arreter avant le telephone — et il marchait jusqu'a la porte
    // les yeux fermes.
    if (e.etat === 'assomme') { e.porteBut = null; return false; }
    const p = e.porteBut;
    const cible = { x: p.x * TT + 8, y: (p.y + 1) * TT + 8 };
    const d = Math.hypot(cible.x - e.x, cible.y - e.y);
    if (d > 260 || ++e.porteT > 900) { e.porteBut = null; return false; }   // il a change d'idee
    if (d > 6) {
      const vitesse = B.defs.recherche.vitesses.pieton * e.allure;
      e.vx = (cible.x - e.x) / d * vitesse; e.vy = (cible.y - e.y) / d * vitesse;
      const avant = { x: e.x, y: e.y };
      deplacerCercle(e, e.vx, e.vy, masqueDe(e));
      regarder(e, e.vx, e.vy);
      // Bloque par la foule ou un banc : on renonce plutot que de pietiner.
      if (Math.hypot(e.x - avant.x, e.y - avant.y) < 0.05 && ++e.porteBloque > 60) e.porteBut = null;
      return true;
    }
    // Arrive : la porte s'ouvre, ET IL DISPARAIT SEULEMENT UNE FOIS OUVERTE.
    Monde.ouvrirPorte(p.x, p.y);
    if (Monde.battant(p.x, p.y) < 0.9) { e.vx = 0; e.vy = 0; return true; }
    // ⚠️ C'est ICI que le telephone du stool sonne au poste : sur le seuil, une
    // fois la porte ouverte, pas une image avant. Tant qu'on le voit encore,
    // on peut encore le payer ou l'assommer.
    if (e.stool) Police.appelDuStool(e);
    retirer(e);
    return true;
  }

  /** Le masque d'un corps depend d'OU IL EST, pas de qui il est.

      ⚠️ Celui qui a les pieds dans l'eau doit pouvoir EN SORTIR. Un agent lance
      a la nage derriere le joueur, revenu a `flane`, se serait retrouve fige au
      milieu de la baie pour toujours : le masque du pieton ne laisse pas sortir
      de l'eau plus qu'il n'y laisse entrer. Les passants, eux, n'y entrent
      jamais — `marchablePieton` garde l'eau, et leur flanerie s'y arrete. */
  function masqueDe(e) {
    // ⚠️ `barbote` : un enfant de la greve entre dans la PREMIERE tuile d'eau,
    // et le masque du pieton l'en empeche (l'eau y est un mur). C'est la seule
    // porte qu'on lui ouvre ; `majJeu` le ramene des qu'il n'a plus de terre
    // sous la main, et un juge tient qu'il ne va jamais plus loin.
    return (e.nage || e.agent || e.barbote || e.type === 'joueur') ? Monde.MASQUE_NAGEUR : Monde.MASQUE_PIETON;
  }

  function majPieton(e) {
    const v = B.defs.recherche.vitesses;
    const reactions = B.defs.pietons.reactions;
    if (!e.vivant) { if (e.saigne > 0) e.saigne--; return; }
    // Assis dans le char du joueur (celui qu'on escorte, `Histoire.majProtege`) :
    // il va ou le char va, et rien d'autre — `dessine` est faux, et `blesser`
    // ne touche pas qui est dedans.
    if (e.dansVehicule) { e.x = e.dansVehicule.x; e.y = e.dansVehicule.y; e.vx = 0; e.vy = 0; return; }
    // Tenu par le joueur (une prise), ou en l'air (une projection) : `techniques.js`
    // le mene, rien d'autre ne bouge.
    if (e.vol || e.tenu) { e.vx = 0; e.vy = 0; return; }
    // ⚠️ Lu sous les pieds a chaque image, pour tout le monde : c'est ce qui
    // decide du masque, du dessin, et de la vitesse d'un agent a la nage.
    mouiller(e);
    if (e.saigne > 0) saigner(e);
    if (majEnjambe(e)) return;         // il passe par-dessus une cloture : rien d'autre
    if (majPorte(e)) return;           // il sort d'une porte, ou il y rentre

    // ⚠️ `suit` PASSE AVANT `fige` : un donneur est fige (il tient son poste),
    // et celui qu'on escorte en est un. La branche du poste sortait la premiere
    // et le ramenait a sa place a chaque image — le Bonimenteur de p14 restait
    // plante a l'arche, a cote du joueur qui devait l'emmener (22 sept. 2026).
    if (e.etat === 'fige' && !e.suit) {
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
        deplacerCercle(e, dx / loin * pas, dy / loin * pas, masqueDe(e));
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
        // ⚠️ `vitesseSuite` : celui qu'on escorte court comme le joueur sprinte
        // (`Histoire`, `proteger`) — plafonne a `pieton_course`, il se laissait
        // distancer, et le premier coin de mur le perdait pour de bon.
        const vitesse = e.vitesseSuite || Math.min(v.pieton_course, v.pieton * e.allure * 1.6);
        e.vx = dx / norme * vitesse;
        e.vy = dy / norme * vitesse;
      } else { e.vx = 0; e.vy = 0; }
      deplacerCercle(e, e.vx, e.vy, masqueDe(e));
      dansLaCarte(e);
      e.anim.dist += Math.abs(e.vx) + Math.abs(e.vy);
      regarder(e, e.vx, e.vy);
      return;
    }
    if (e.etat === 'assomme') {
      // ⚠️ UNE CIBLE DE MISSION COUCHEE RESTE COUCHEE tant que la mission dure :
      // le K.-O. compte comme un mort au compteur de l'objectif. Elle se relevait
      // au bout de 5 s et s'enfuyait — le « 1/6 » redevenait « 0/6 », et il
      // fallait coucher les six Cravates de M5, sur trois coins, en 5 s.
      // `nettoyer` lui retire `cible` a la fin : elle se releve alors.
      if (!e.cible && --e.minuterie <= 0) { e.etat = 'fuit'; e.minuterie = reactions.fuite_secondes * 60; e.face = 'bas'; }
      return;
    }
    if (e.metier === 'reclame' && (e.etat === 'flane' || e.etat === 'arret')) solliciter(e);
    if (e.recul > 0) {
      e.recul--;
      deplacerCercle(e, e.vx, e.vy, masqueDe(e));
      e.vx *= 0.82; e.vy *= 0.82;
      dansLaCarte(e);
      return;
    }

    // Pousse sur la rue, l'enfant a velo n'y souffle pas : il en sort d'abord.
    if (e.etat === 'arret' && e.metier === 'cycliste' && !roulableEnfant(Math.floor(e.x / TT), Math.floor(e.y / TT))) {
      e.etat = 'flane'; e.butT = 0;
    }
    let vitesse = v.pieton * e.allure;
    // ⚠️ On nage a la vitesse de la nage, agent compris : un policier qui
    // traverserait le chenal aussi vite qu'il court sur le quai ferait de l'eau
    // un raccourci pour lui et un cul-de-sac pour le joueur.
    if (e.nage) vitesse = Math.min(vitesse, B.defs.recherche.nage.vitesse);
    if (e.etat === 'temoin' && e.vers && e.vers.vivant) {
      // Le temoin court VERS l'agent qu'il a repere, pour lui raconter.
      vitesse = v.pieton_course * e.allure;
      // ⚠️ IL FAUT S'ARRETER LA quand la minuterie tombe : la ligne suivante
      // lisait `e.vers.x` sur le `e.vers` qu'on venait de mettre a zero, et le
      // jeu plantait. Une seule image sur des milliers — celle ou le temoin
      // finit sa course exactement pendant qu'il court — donc invisible jusqu'a
      // ce qu'un singe tombe dessus.
      if (--e.minuterie <= 0) {
        e.etat = 'flane'; e.cri = 0; e.vers = null;
        e.vx = 0; e.vy = 0;
      } else {
        const dx = e.vers.x - e.x, dy = e.vers.y - e.y;
        const norme = Math.hypot(dx, dy) || 1;
        e.vx = dx / norme * vitesse;
        e.vy = dy / norme * vitesse;
      }
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
    } else if (e.etat === 'vole_un_char') {
      // Il marche droit sur le char qu'il a repere, d'un pas presse. ⚠️ Il
      // RENONCE : le char peut partir, exploser, ou quelqu'un monter dedans —
      // et un voleur qui poursuit un char pour l'eternite n'est pas un voleur,
      // c'est un bogue qui marche.
      const f = B.defs.pietons.vol_de_char, cible = e.charVise;
      if (!cible || !cible.actif || cible.conducteur || cible.etat === 'epave' || --e.voleChar <= 0) {
        e.etat = 'flane'; e.charVise = null; e.vx = 0; e.vy = 0;
        return;
      }
      vitesse = v.pieton_course * e.allure * 0.9;
      const dx = cible.x - e.x, dy = cible.y - e.y, norme = Math.hypot(dx, dy) || 1;
      e.vx = dx / norme * vitesse;
      e.vy = dy / norme * vitesse;
      if (norme < f.portee_px) emporterLeChar(e, cible);
    } else if (e.etat === 'bagarre') {
      // ⚠️ IL VISE QUELQU'UN D'AUTRE QUE LE JOUEUR, et c'est tout ce qui
      // manquait a la ville : `attaque_joueur` ne savait viser que lui. Il
      // marche sur son rival, s'arrete a portee de poing, et cogne a la cadence
      // de la fiche.
      //
      // ⚠️ ET LA RIXE FINIT — au bout de son temps, ou des qu'il ne reste plus
      // personne debout en face. Deux survivants qui se tapent dessus jusqu'a la
      // fin des temps ne sont pas une bagarre : c'est un decor qui grince.
      const f = B.defs.pietons.bagarre;
      if (--e.bagarreT <= 0) { finirLaBagarre(e); return; }
      if (!e.rival || !e.rival.vivant || e.rival.etat === 'assomme'
          || dist2(e.x, e.y, e.rival.x, e.rival.y) > f.rival_px * f.rival_px) {
        e.rival = rivalDe(e, f);
      }
      if (!e.rival) { finirLaBagarre(e); return; }
      vitesse = v.pieton_course * e.allure;
      const dx = e.rival.x - e.x, dy = e.rival.y - e.y, norme = Math.hypot(dx, dy) || 1;
      if (norme > f.portee_px) {
        e.vx = dx / norme * vitesse;
        e.vy = dy / norme * vitesse;
      } else {
        e.vx = 0; e.vy = 0;
        regarder(e, dx, dy);
        if (e.t % f.cadence_images === 0) {
          Combat.frapper(e, false);
          // ⚠️ Tu passais par la : un passant te prend pour un des leurs (M12).
          Police.crimeDAutrui('coup_pieton', e.x, e.y, e);
        }
      }
    } else if (e.etat === 'attaque') {
      // ⚠️ ON NE FLANE PAS PENDANT QU'ON FRAPPE — et c'est un vrai trou, pas un
      // detail de la rixe. `Combat.frapper` ecrase l'etat par 'attaque' le temps
      // des trois temps du coup ; faute d'une branche a lui, le frappeur tombait
      // dans le DERNIER `else`, celui qui flane, et pouvait decider de s'arreter
      // en plein geste. `majAttaque` refuse alors de continuer (l'etat n'est plus
      // 'attaque') : le coup reste en suspens pour toujours, et l'homme repart
      // faire autre chose. Une gang qui attaquait le joueur le faisait deja —
      // elle ne le montrait pas, parce qu'elle y revenait toute seule.
      // Ici on ne fait que tenir sa place : les trois temps appartiennent a
      // `Combat.majAttaque`, et on plante ses pieds pour cogner.
      e.vx = 0; e.vy = 0;
      return;
    } else if (e.etat === 'aborde') {
      // Le solliciteur vient vers toi, d'un pas decide — jamais en courant :
      // on doit pouvoir le semer en marchant, sinon c'est une poursuite.
      const r = B.defs.reclame, j = B.joueur;
      const dx = j.x - e.x, dy = j.y - e.y, norme = Math.hypot(dx, dy) || 1;
      // On lache prise : le joueur court, il est loin, un mur ou la chaussee
      // barre le chemin, ou ca fait quatre secondes qu'on n'arrive pas.
      const ax = Math.floor((e.x + dx / norme * (e.r + 4)) / TT), ay = Math.floor((e.y + dy / norme * (e.r + 4)) / TT);
      if (!j.vivant || j.dansVehicule || joueurCourt() || norme > r.rayon_tuiles * TT * 1.5
          || Monde.estChaussee(ax, ay) || ++e.abordeT > 240) {
        e.etat = 'flane'; e.repos = Math.round(r.repos_images / 4); e.vx = 0; e.vy = 0;
        return;
      }
      if (norme <= r.portee_px) {
        e.etat = 'boniment'; e.minuterie = r.boniment_images; e.vx = 0; e.vy = 0;
        regarder(e, dx, dy);
        bulle(e, e.boniment, { duree: r.boniment_images });
        Son.Voix.dire('crieur', e.x, e.y);
        return;
      }
      e.vx = dx / norme * vitesse;
      e.vy = dy / norme * vitesse;
    } else if (e.etat === 'boniment') {
      // Il te tient le crachoir : plante devant toi, la pancarte en avant. Tu
      // t'eloignes, il se tait ; il a fini, il te laisse la paix un moment.
      const r = B.defs.reclame, j = B.joueur, portee = r.rayon_tuiles * TT;
      e.vx = 0; e.vy = 0;
      regarder(e, j.x - e.x, j.y - e.y);
      if (--e.minuterie <= 0 || dist2(e.x, e.y, j.x, j.y) > portee * portee) {
        e.etat = 'flane'; e.repos = r.repos_images; taire(e);
      }
      return;
    } else if (e.etat === 'cap' && e.cap) {
      // ⚠️ UN ETAT POUR ALLER QUELQUE PART. Flaner suit une direction jusqu'a
      // ce qu'elle ne mene plus nulle part ; la contractuelle et le facteur,
      // eux, ont un ENDROIT ou aller — le char mal gare, la prochaine porte de
      // la tournee. Sans cet etat, il aurait fallu les faire tomber dessus par
      // hasard, et une routine qui depend du hasard n'est pas une routine.
      const dx = e.cap.x - e.x, dy = e.cap.y - e.y, norme = Math.hypot(dx, dy) || 1;
      // On renonce : trop loin, ou ca fait dix secondes qu'on n'y arrive pas.
      // Meme filet que `majPorte`, et pour la meme raison — un pieton coince
      // contre un banc ne doit pas y rester pour toujours.
      // ⚠️ `capVite` : celui qui RATTRAPE quelqu'un doit aller plus vite que
      // lui. Le pickpocket marche 10 % plus vite qu'un passant — a ce
      // rythme-la, il gagne cinq centiemes de pixel par image et met une
      // minute et demie a couvrir trente pixels. Il ne volait jamais personne,
      // et rien ne le disait : on le voyait suivre.
      const pas = e.capVite ? v.pieton_course * e.allure : vitesse;
      if (norme > 340 || ++e.capT > 600) { e.etat = 'flane'; e.cap = null; e.capVite = false; e.vx = 0; e.vy = 0; }
      // ⚠️ ARRIVE, ON S'ARRETE. Sans ce palier, le pickpocket poussait dans sa
      // victime image apres image : `cap` le ramenait dedans, `demeler` le
      // ressortait, et les deux corps restaient enfonces l'un dans l'autre
      // trois images d'affilee. Douze pixels, c'est sous le seuil de toutes les
      // routines (le facteur a 14, la contractuelle 22, le laveur 24) : chacune
      // se declenche quand meme, a la prochaine image de `majSortes`.
      else if (norme <= 12) { e.vx = 0; e.vy = 0; }
      else { e.vx = dx / norme * pas; e.vy = dy / norme * pas; }
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
          const rayonPoste = e.posteRayon || POSTE_RAYON;
          const rentre = e.poste && dist2(e.x, e.y, e.poste.x, e.poste.y) > rayonPoste * rayonPoste;
          // L'homme-sandwich, lui, marche plus qu'il n'attend : une pancarte
          // qui bouge se voit de plus loin qu'une pancarte plantee.
          // ⚠️ LE JOGGER NE S'ARRETE JAMAIS : ni pour souffler, ni pour
          // regarder un amuseur (`attrouper` ecarte deja les metiers). Des
          // ecouteurs sur les oreilles, et il passe — c'est sa routine, et
          // c'est une routine en creux : ce qu'il ne fait pas.
          if (!rentre && e.metier !== 'jogger'
              && B.rng() < (e.poste ? (e.metier === 'reclame' ? 0.3 : 0.65) : 0.3)) {
            e.etat = 'arret';
            e.minuterie = 50 + Math.floor(B.rng() * 160);
            e.butT = e.poste ? 30 : 90;
            e.vx = 0; e.vy = 0;
            return;
          }
          // Une porte juste au nord ? Une fois sur douze, on rentre.
          // ⚠️ SAUF UN HOMME DE MISSION (retour de Martin, 21 sept. 2026 : « la
          // derniere cravate a trouver n'apparait pas »). Une Cravate de M5 qui
          // flanait sous une porte y entrait : sortie de la ville, elle restait
          // comptee debout, la mission bloquait a 5/6 et la fleche montrait la
          // porte. ⚠️ Teste APRES le de : il se tire comme avant, et la ville
          // d'une mission reste celle d'hier.
          const g = Monde.glyphe(tx, ty - 1);
          if ((g === 'd' || g === 'D') && !e.metier && !e.suit && !e.petit && B.rng() < 0.08 && !e.mission) {
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
        // ⚠️ L'enfant a velo ne descend meme pas sur la traverse : pour lui, toute
        // la rue est un mur (`roulableEnfant`).
        if (Monde.estChaussee(ax, ay) || Monde.bloque(ax, ay, Monde.MASQUE_PIETON)
            || (e.metier === 'cycliste' && !roulableEnfant(ax, ay))) {
          e.dir = (e.dir + (B.rng() < 0.5 ? 1 : 3)) % 4;      // on tourne, on ne fonce pas
          e.butT = e.poste ? 30 : 60 + Math.floor(B.rng() * 120);
          e.vx = 0; e.vy = 0;
          return;
        }
        // ⚠️ LA DALLE EST PRIORITAIRE : sur le trottoir, on renonce le plus
        // souvent a en descendre vers l'abord (la couronne du bloc) — c'est un
        // debordement, pas un deuxieme trottoir. Le taux est dans la fiche
        // (`pietons.REACTIONS.abord_renonce`) ; on y va quand meme parfois,
        // sinon une dalle d'une tuile serait une file indienne.
        if (Monde.estAbord(ax, ay) && Monde.estTrottoir(tx, ty) && !e.porteBut
            && B.rng() < reactions.abord_renonce) {
          e.dir = versLaDalle(e, tx, ty);                       // on reste sur la dalle
          e.butT = 30 + Math.floor(B.rng() * 60);
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
        // ⚠️ L'IVROGNE ZIGZAGUE : sa direction est bonne, sa trajectoire ne
        // l'est pas. C'est le seul de la ville a ne pas marcher droit, et ca
        // le nomme d'aussi loin que sa bouteille — un corps qu'on reconnait a
        // sa demarche avant de voir ses pixels.
        if (e.metier === 'ivrogne') {
          const a = Math.sin(e.t / 22) * 0.9, vx = e.vx, vy = e.vy;
          e.vx = vx * Math.cos(a) - vy * Math.sin(a);
          e.vy = vx * Math.sin(a) + vy * Math.cos(a);
        }
      }
    }
    const avant = { x: e.x, y: e.y };
    const cycliste = e.metier === 'cycliste';
    const surLeTrottoir = cycliste && roulableEnfant(Math.floor(e.x / TT), Math.floor(e.y / TT));
    if (cycliste) resterSurLeTrottoir(e);
    deplacerCercle(e, e.vx, e.vy, masqueDe(e));
    dansLaCarte(e);
    // ⚠️ La regle dure de l'enfant a velo : un pas qui le mettrait sur la rue ne
    // se fait pas. `resterSurLeTrottoir` le prevoit ; ceci le garantit, quoi qu'ait
    // fait la glissade le long d'un mur ou d'un banc.
    if (surLeTrottoir && !roulableEnfant(Math.floor(e.x / TT), Math.floor(e.y / TT))) { e.x = avant.x; e.y = avant.y; }
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

  // --- Les bulles de bande dessinee --------------------------------------------------------

  //: ⚠️ Le jeu avait deja deux pastilles de 8 px au-dessus des tetes — le « ! »
  //: du temoin, le trait de la peur (`cri`). Elles disent un ETAT D'ESPRIT ;
  //: elles ne peuvent pas dire un MOT, et c'est le mot qui manquait : un
  //: personnage plante dans un coin de piece ne s'adresse a personne, on passe
  //: devant lui sans le voir. Une bulle, elle, INTERPELLE.
  //:
  //: ⚠️ Le texte ne s'invente PAS ici : il descend de `missions.py` comme
  //: toutes les repliques du jeu (`personnages[].heler`). Cette fonction-ci ne
  //: sait que dessiner.
  // ⚠️ 12 et pas 11 : l'accent se dessine trois rangs AU-DESSUS de la lettre.
  // A 11 (texte a 3 du haut), il touchait le trait de la boite, de la meme
  // encre, et « DÉJÀ » portait deux bosses sur le cadre.
  const BULLE_H = 12;                    // 5 px de police, 4 de marge en haut (l'accent), 3 en bas
  const BULLE_QUEUE = 3;                 // la pointe qui designe celui qui parle
  const BULLE_DESSUS = 30;               // du sol de l'entite au haut de la boite
  const BULLE_FOND = '#efe6d0', BULLE_ENCRE = '#1a1a22';

  /** Pose (ou garde) la bulle de quelqu'un. `duree` en images, 0 = jusqu'a ce
      qu'on la taise. Un texte vide efface la bulle : c'est la facon normale de
      la retirer quand il n'y a plus rien a dire.

      ⚠️ Reposer LE MEME mot ne remet pas l'horloge a zero — sinon la bulle
      d'un donneur, reposee a chaque image par `Histoire.maj`, resterait figee
      a la premiere image de son animation, pour toujours. */
  function bulle(e, texte, options) {
    if (!e) return null;
    const o = options || {};
    // ⚠️ Le mot est garde TEL QU'IL EST ECRIT dans `missions.py`, accents
    // compris : `Atlas.texte` les dessine au-dessus de la lettre.
    const mot = String(texte || '').trim();
    if (!mot) { e.bulle = null; return null; }
    if (e.bulle && e.bulle.texte === mot) { e.bulle.duree = o.duree || 0; return e.bulle; }
    e.bulle = { texte: mot, t: 0, duree: o.duree || 0,
                fond: o.fond || BULLE_FOND, encre: o.encre || BULLE_ENCRE };
    return e.bulle;
  }

  function taire(e) { if (e) e.bulle = null; }

  function majBulle(e) {
    const b = e.bulle;
    b.t++;
    if (b.duree && b.t >= b.duree) e.bulle = null;
  }

  /** La boite, sa queue, son mot — au-dessus de la tete, en pixels entiers.

      ⚠️ Elle se dessine APRES tout le monde (deuxieme passe dans `dessiner`) :
      dans une piece, le commis ou un client passe devant le donneur une fois
      sur deux, et une bulle a moitie cachee par une nuque ne se lit plus. */
  function dessinerBulle(ctx, e, cx, cy) {
    const b = e.bulle;
    const large = Atlas.largeurTexte(b.texte, 1) + 8;
    // Elle monte d'un coup en arrivant, puis elle respire : un mot qui apparaît
    // fige se lit comme un meuble de plus.
    const monte = b.t < 6 ? 6 - b.t : 0;
    const flotte = Math.round(Math.sin(b.t / 18) * 1.2) - monte;
    const x = Math.round(e.x - large / 2 - cx);
    const y = Math.round(e.y - BULLE_DESSUS + flotte - cy);
    // ⚠️ La queue tombe sur la TETE de celui qui parle, pas sur un coin de la
    // boite : au fond du casse-croute, le joueur se tient a deux pas du
    // sergent, et une queue decalee de dix pixels donnait sa replique au
    // mauvais personnage.
    const qx = Math.round(e.x - cx) - 1;
    ctx.fillStyle = b.encre;
    ctx.fillRect(x, y - 1, large, BULLE_H + 2);         // le haut et le bas
    ctx.fillRect(x - 1, y, large + 2, BULLE_H);         // les deux cotes (coins coupes)
    for (let i = 0; i < BULLE_QUEUE; i++) ctx.fillRect(qx, y + BULLE_H + i, BULLE_QUEUE + 2 - i, 1);
    ctx.fillStyle = b.fond;
    ctx.fillRect(x, y, large, BULLE_H);
    for (let i = 0; i < BULLE_QUEUE - 1; i++) ctx.fillRect(qx + 1, y + BULLE_H + i, BULLE_QUEUE - 1 - i, 1);
    Atlas.texte(ctx, b.texte, x + 4, y + 4, b.encre, 1);
    B.stats.rects += 5;
  }

  /** Peut-on s'engager sur ce passage ? Au feu : quand les chars de cette rue
      sont au rouge. Sans feu : quand aucun char n'approche. */
  function traverseeSure(tx, ty, dir) {
    const inter = Monde.intersectionA(tx, ty);
    // Le passage « = » barre une rue est-ouest : les chars y roulent en > <.
    const sensChars = Monde.glyphe(tx, ty) === '=' ? '>' : '^';
    // ⚠️ `feuPieton`, pas `!feuVert` : le second est vrai pendant l'ORANGE, et
    // les pietons s'engageaient donc pile quand les chars accelerent pour vider
    // le croisement. On ne s'engage QUE sur le blanc — le degagement laisse
    // finir ceux qui sont deja dedans (on ne teste qu'a l'entree du passage).
    if (inter && inter.feux) return Monde.feuPieton(inter, sensChars) === 'blanc';
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
      // ⚠️ CEUX QUI SE BATTENT DEJA NE LEVENT PAS LA TETE. Chaque coup d'une
      // rixe passe par ici, et la seule reponse qu'`alerter` connaisse pour une
      // gang est « attaquer le joueur » : sans cette ligne, six hommes qui se
      // tapaient dessus se retournaient tous contre lui au premier poing.
      if (enPleineRixe(e)) continue;
      if (!Monde.ligneLibre(e.x, e.y, x, y)) continue;
      // ⚠️ L'IVROGNE NE FUIT PAS. Il n'a pas peur : il n'a rien compris, et il
      // repond. C'est le seul de la ville — une rue ou tout le monde detale de
      // la meme facon n'a qu'une seule reaction, et on cesse de la voir.
      if (e.metier === 'ivrogne') {
        const mot = (B.defs.pietons.paroles.ivrogne || {}).sans_peur;
        if (mot) bulle(e, mot, { duree: 90 });
        e.cri = 90;
        continue;
      }
      if (e.intouchable) {                       // l'enfant ne fait que detaler
        e.etat = 'fuit'; e.menace = menace; e.minuterie = reactions.fuite_secondes * 90; e.cri = 120;
        continue;
      }
      // ⚠️ ON NE RIPOSTE QUE CONTRE LE JOUEUR, parce que `attaque_joueur` ne
      // sait viser que lui. Quand la menace est quelqu'un d'AUTRE — une rixe
      // entre gangs, un voleur qui part avec un char, un char du trafic qui
      // renverse un passant —, le courage ne peut pas se traduire en riposte :
      // se jeter sur le joueur pour un coup qu'il n'a pas donne n'est pas du
      // courage, c'est un bogue. On s'ecarte, comme les autres.
      const contreLeJoueur = menace === B.joueur;
      if (e.gang && gravite >= 1 && contreLeJoueur) { e.etat = 'attaque_joueur'; e.cri = 90; continue; }
      if (e.courage > 0 && B.rng() < e.courage * 0.5 && gravite >= 2 && contreLeJoueur) {
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
      if (e.vie <= 0 && e.vivant) {
        if (e === B.joueur) Missions.hopital(e.menace);
        else if (e.type === 'joueur') assommer(e);
        else tuer(e, e.menace);
      }
    }
  }

  /** Blesse une entite. Rend true si le coup a porte. */
  function blesser(e, degats, source, options) {
    const opts = options || {};
    if (!e.vivant || e.invincible > 0) return false;
    // ⚠️ ON NE BLESSE QUE DES GENS. `creer` donne `vivant: true` a TOUT ce qu'il
    // fabrique — c'est le defaut du constructeur — si bien qu'un goeland, un
    // ballon ou une gerbe d'eau se laissaient « blesser » : 99 points de degats
    // sur un oiseau qui n'a pas de vie a perdre. Un goeland qu'on peut tuer est
    // une CIBLE, et une cible demande un score, un crime, un juge.
    if (e.type !== 'pieton' && e.type !== 'joueur') return false;
    // ⚠️ DEUX JOUEURS NE SE FRAPPENT PAS — Martin, 22 sept. : « il ne faut pas
    // qu'il puisse se frapper mutuellement ». Ecrit ICI, au seul passage de
    // toute blessure du jeu, plutot qu'arme par arme : le poing, la balle, la
    // grenaille, le brasier et le char conduit par l'autre (`Vehicules`
    // signale alors `B.joueur` comme source) y passent tous. Une coop ou on
    // se tue entre partenaires est une coop qui dure une minute.
    if (e.type === 'joueur' && source && source.type === 'joueur') return false;
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
    // ⚠️ RIEN N'ATTEINT QUI EST ASSIS DANS UN CHAR — retour de Martin : « quand
    // on est dans un voiture ou autre, il ne faut pas que les pietons puisse
    // nous faire du domage ». Un passant cognait a travers la portiere et une
    // balle traversait la tole comme si elle n'etait pas la.
    //
    // ⚠️ LA REGLE EXISTAIT DEJA, ecrite une fois pour le feu : un brasier mord
    // le CHAR et saute qui est dedans (`Combat.majBrasiers`). Elle vit
    // desormais ICI, au seul endroit par ou passe toute blessure du jeu,
    // plutot qu'en trois exemplaires dans `Combat` — un poing, une balle, une
    // grenaille, et le prochain qui s'ajoutera.
    //
    // ⚠️ Ce qui SORT du char descend AVANT de blesser, et c'est ce qui rend la
    // ligne sans danger : l'explosion fait `descendre` celui qui est dedans
    // avant de le souffler, l'ejection aussi, et le char qui renverse quelqu'un
    // ne regarde que ceux qui marchent.
    if (e.dansVehicule) return false;
    e.vie -= degats;
    e.menace = source || e.menace;
    e.recul = Math.max(e.recul, opts.renverse ? 22 : 8);
    const angle = opts.angle === undefined ? angleVers(source ? source.x : e.x, source ? source.y : e.y, e.x, e.y) : opts.angle;
    const poussee = opts.renverse ? 3.2 : 1.4;
    e.vx = Math.cos(angle) * poussee;
    e.vy = Math.sin(angle) * poussee;
    // ⚠️ Une projection ASSOMME sans faire saigner (`sans_sang`) : c'est ce qui la
    // fait valoir moins d'etoiles que cogner. Un etranglement (`silencieuse`) ne
    // crie pas et n'alerte personne : `Police.quelqu_un_voit` decide seul du crime
    // (docs/jalons/les-techniques-d-arts-martiaux.md).
    if (opts.saigne && !opts.sans_sang) e.saigne = Math.min(B.defs.pietons.reactions.saignement_images, opts.saigne);
    if (e !== B.joueur && !opts.sans_sang) sang(e.x, e.y, opts.saigne ? 6 : 3);
    // Le grognement vient de celui qui encaisse : muet hors de l'ecran, plus
    // fort a mesure qu'on s'approche (retour de Martin, 16 sept. 2026).
    if (!opts.silencieuse) Son.depuis(e, Son.SFX.touche);
    if (e.vie <= 0 && e === B.joueur) {
      Missions.hopital(source);
    } else if (e.vie <= 0 && e.type === 'joueur') {
      assommer(e);                      // le deuxieme joueur : K.-O., voir `majJoueur`
    } else if (e.vie <= 0) {
      if (opts.assomme) assommer(e);
      else tuer(e, source);
    } else if (e.type === 'pieton') {
      if (opts.silencieuse) return true;
      alerter(e.x, e.y, source, 2);
      // ⚠️ CELUI QUI SE BAT DEJA NE SE RETOURNE PAS CONTRE LE JOUEUR : le
      // premier coup d'une rixe envoyait les deux camps sur lui, et il n'avait
      // rien fait — il passait par la. Mais si c'est LUI qui cogne, la regle
      // ordinaire reprend, et la gang lui tombe dessus comme chez elle.
      if (e.etat !== 'attaque_joueur' && !(enPleineRixe(e) && source !== B.joueur)) {
        e.etat = (e.courage > 0 && B.rng() < e.courage) ? 'attaque_joueur' : 'fuit';
        e.minuterie = B.defs.pietons.reactions.fuite_secondes * 60;
        e.avantLeCoup = null;      // il ne reprendra pas ce qu'il faisait
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
      // ⚠️ LE COMPTEUR EST CELUI DU JOUEUR, pas celui de la ville. `stats.tues`
      // tire la manchette du Clairon (`journal.REGLES` : « UN MORT DANS LA
      // RUE », « NUIT ROUGE AU FAUBOURG ») et le bilan de fin de mission :
      // creditier le joueur d'une rixe qu'il a regardee de loin — ou d'un
      // passant qu'un char du trafic a fauche — est un mensonge imprime.
      if (source === B.joueur) B.partie.stats.tues++;
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

  // La fille de la Brume t'accoste de plus loin qu'un passant qui te frole
  // (trois tuiles), et pas deux fois en moins d'une demi-minute.
  const BRUME_PORTEE = 48, BRUME_REPOS = 1800, BRUME_BULLE = 150;

  /** La fille de la Brume t'accoste quand tu passes pres de son coin : un mot
      dans une bulle, et sa voix. Jamais deux fois de suite la meme replique,
      jamais quand elle fuit ou qu'elle est assommee, jamais en char.

      ⚠️ Elle a un `metier`, et `rumeurEtRepliques` saute tout piéton qui en a
      un : c'est pour ca qu'elle n'a jamais rien dit avant le 13 sept. 2026
      (demande de Martin), alors que la regex des voix de femmes la nommait.
      Rend vrai si elle a parle. */
  function accosterDepuisLaBrume(j) {
    for (const e of pietonsAutour(j.x, j.y, BRUME_PORTEE)) {
      if (e.metier !== 'compagnie' || !e.vivant || e.etat === 'fuit' || e.etat === 'assomme') continue;
      if (e.accosteT !== undefined && B.t - e.accosteT < BRUME_REPOS) continue;
      const replique = Son.Voix.choisir('brume', e.derniereReplique);
      if (!replique) return false;
      e.accosteT = B.t;
      e.derniereReplique = replique.slug;
      regarder(e, j.x - e.x, j.y - e.y);
      bulle(e, replique.texte, { duree: BRUME_BULLE });
      Son.Voix.dire('brume', e.x, e.y, replique.slug);
      return true;
    }
    return false;
  }

  /** La foule qu'on entend, et le passant qui nous dit un mot en nous frolant. */
  function rumeurEtRepliques() {
    const j = B.joueur;
    if (B.t % 15 === 0) {
      // ⚠️ LA RUE SE TAIT DEVANT UNE ARME, et c'est l'ajout le moins cher de
      // toute la vague : `Son.Rumeur` reglait deja son volume sur le nombre de
      // gens autour — il ne manquait qu'une RAISON de le faire tomber. Au
      // volant, non : on ne voit pas ce que tu tiens.
      if (!j.dansVehicule && j.arme && j.arme !== 'poings') Son.Rumeur.taire();
      Son.Rumeur.maj(pietonsAutour(j.x, j.y, 200).filter(function (e) { return !e.metier; }).length);
    }
    if (j.dansVehicule) return;
    if (accosterDepuisLaBrume(j)) return;
    // ⚠️ PARLER EST UNE CHANCE, PAS UNE CERTITUDE. Un passant qui parle chaque
    // fois qu'on le frole rend huit repliques fatigantes bien avant qu'elles
    // soient usees — la plupart des gens qu'on croise ne disent rien.
    const chance = ((B.defs.audio && B.defs.audio.parole) || {}).chance;
    for (const e of pietonsAutour(j.x, j.y, 30)) {
      if (e.metier || e.intouchable || e.etat === 'assomme' || e.etat === 'fuit' || e.etat === 'temoin' || e.aParle) continue;
      e.aParle = true;
      if (B.rng() > (chance === undefined ? 0.35 : chance)) break;
      const femme = /passante|dame|mere|racoleuse|conductrice/.test(e.arch);
      Son.Voix.dire(femme ? 'femme' : 'homme', e.x, e.y);
      break;
    }
  }

  // --- Boucle ---------------------------------------------------------------------------

  function maj() {
    indexer();
    let actifs = 0;
    //: La gerbe la plus proche, en force (0 = aucune a portee). ⚠️ Le souffle
    //: d'une borne est un son CONTINU : on le TIENT apres la boucle, une fois
    //: par image, au lieu de le rejouer — il rejouait le choc d'un accident de
    //: char toutes les 24 images pendant dix secondes.
    let jetProche = 0;
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const e = B.entites[i];
      if (!e.actif) continue;
      e.t++;
      if (e.animT > 0) e.animT--;
      if (e.bulle) majBulle(e);
      if (e.type === 'joueur') majJoueur(e);
      else if (e.type === 'pieton') { majPieton(e); actifs++; }
      else if (e.type === 'ballon') majBallonVol(e);
      else if (e.type === 'jet_eau') {
        // La gerbe : deux gouttes par image, vers le haut, qui retombent.
        if (e.minuterie-- <= 0) { retirer(e); continue; }
        for (let k = 0; k < 2; k++) {
          const a = (B.rng() - 0.5) * 1.6;
          particule(e.x + (B.rng() - 0.5) * 4, e.y - 4, Math.sin(a) * 1.1, -0.35 - B.rng() * 0.3,
                    18 + B.rng() * 14, B.rng() < 0.4 ? '#cfe6f5' : '#7fb6d9', 2, 0.16);
        }
        // ⚠️ Le souffle ne se REJOUE pas : il se TIENT (`Son.SFX.borne_jet`,
        // une fois par image, apres la boucle). Ici on ne fait que dire
        // laquelle des gerbes s'entend le plus fort.
        jetProche = Math.max(jetProche, 1 - Math.hypot(e.x - B.joueur.x, e.y - B.joueur.y) / JET_EAU_PORTEE);
      }
      else if (e.type === 'ramassage'
               && (e.t > 3600 || dist2(e.x, e.y, B.joueur.x, B.joueur.y) > BULLE_OUBLI * BULLE_OUBLI)) {
        retirer(e);
      }
    }
    Son.SFX.borne_jet(jetProche);
    majLesBetes();
    majOrignal();
    // ⚠️ Apres que tout le monde a bouge, et sur un index REFAIT : `indexer()`
    // date du debut de l'image, et demeler la foule sur des positions perimees
    // laisse passer exactement les paires qui viennent de se rejoindre.
    indexer();
    demeler();
    majParticules();
    // ⚠️ Un bloc de carte dit s'il a des passants (`bloc.gens`) : la clairiere d'essai n'en
    // a pas — sans cette garde, un livreur et un policier de la ville y naissaient.
    const personneIci = B.bloc && !B.bloc.def.bloc.gens;
    if (B.joueur && !B.interieur && !personneIci) { peupler(); semerDesArmesDeFortune(); rumeurEtRepliques(); }
    laMusiqueDeLaRue();
    B.stats.actifs = actifs;
  }

  // --- Dessin ------------------------------------------------------------------------------

  /** Le nom de la pose a dessiner : la marche, ou le coup qui part. */
  function nomDePose(e) {
    // Une TECHNIQUE (`techniques.js`) : la pose cle de son etape — `debout` est la
    // marche, `frappe` la pose de coup d'avant, le reste `tech_<pose>_<face>`.
    // La prise (SAISIR) : on tient l'autre a deux mains, tant qu'aucun coup ne part.
    if (e.prise && e.etat !== 'attaque') return 'tech_saisie_' + e.face;
    if (e.etat === 'attaque' && e.techPose) {
      if (e.techPose === 'debout') return e.face;
      return (e.techPose === 'frappe' ? 'frappe_' : 'tech_' + e.techPose + '_') + e.face;
    }
    if (e.etat === 'attaque' && e.phase && e.phase !== 'anticipation') return 'frappe_' + e.face;
    // Un GESTE de scene (`Scenes`) : `geste_montrer_bas`, `geste_donner_droite`...
    // Un sprite qui ne l'a pas retombe sur sa face (`imageDe`).
    if (e.geste) return 'geste_' + e.geste + '_' + e.face;
    return e.face;
  }

  function imageDe(e) {
    // Une TENUE (`Garderobe`) : un squelette habille, cuit pose par pose. Sinon, le sprite
    // dessine a la main et ses echanges de palette, comme toujours.
    const habille = e.tenue && typeof Garderobe !== 'undefined' ? Garderobe.cuire(e.tenue) : null;
    const def = habille || SPRITES[e.sprite];
    if (!def) return null;
    const cuit = habille || Atlas.cuire(e.sprite, def, e.swaps);
    const voulu = nomDePose(e);
    // ⚠️ Un sprite dessine a la main n'a pas les poses des techniques : il frappe
    // comme avant (`frappe_<face>`), plutot que de marcher en donnant un coup de pied.
    const repli = e.techPose && e.techPose !== 'debout' && cuit.poses['frappe_' + e.face] ? 'frappe_' + e.face : null;
    const nom = cuit.poses[voulu] ? voulu : (repli || (cuit.poses[e.face] ? e.face : 'bas'));
    const poses = cuit.poses[nom];
    const bouge = Math.abs(e.vx) + Math.abs(e.vy) > 0.05;
    // ⚠️ Une foulee de 9 px, pas 7 : a 7, les jambes tournaient plus vite que
    // le corps n'avancait et tout le monde avait l'air de courir.
    let i = bouge ? [0, 1, 0, 2][Math.floor(e.anim.dist / 9) % 4] : 0;
    // ⚠️ Une image IMPOSEE, quand le corps n'est pas une marche : les deux
    // images de l'homme au manteau sont « ferme » et « OUVERT », pas deux pas.
    // Sans ca, son geste ne se voyait jamais — il est immobile en le faisant,
    // et l'immobile tombe toujours sur l'image zero.
    if (e.poseFixe !== null && e.poseFixe !== undefined) i = e.poseFixe;
    // ⚠️ La pose « gauche » est le miroir de « droite », mais la main n'est
    // decrite QUE du cote droit : sans ce repli, l'arme disparaissait des que
    // le joueur marchait vers la gauche (Martin).
    const miroir = nom.endsWith('gauche');
    const main = def.mains ? (def.mains[miroir ? nom.slice(0, -6) + 'droite' : nom] || null) : null;
    return { canvas: poses[Math.min(i, poses.length - 1)], ancre: cuit.ancre, pose: nom, main: main, miroir: miroir, largeur: cuit.w };
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
    // Projete (`techniques.js`) : il tourne en l'air, `z` le souleve.
    if (e.vol) {
      p.rot = e.vol.tours * Math.PI * 2 * (e.vol.t / e.vol.duree) * e.vol.sens;
      return p;
    }
    if (e.roule > 0) {
      p.rot = (1 - e.roule / Combat.ROULADE_IMAGES) * Math.PI * 2 * (cx >= 0 ? 1 : -1);
      return p;
    }
    if (e.animT > 0 && e.animType === 'ramasse') { p.dy = 3; p.echelleY = 0.78; }
    if (e.recul > 0 && e.vivant && e.etat !== 'assomme') p.rot = (e.vx >= 0 ? 1 : -1) * 0.22;   // il chancelle
    const arme = Combat.armeDef(e.arme || 'poings') || Combat.armeDef('poings');
    // L'elan d'une technique vient de son etape (`app/techniques.py`) : `dx` le
    // long du regard, `dy` vers le bas, `z` en l'air, `rot` dans le sens du regard.
    const tech = e.etat === 'attaque' && e.technique ? Techniques.def(e.technique) : null;
    if (tech) {
      const et = tech.temps[e.techEtape] || tech.temps[0];
      p.dx += Math.round(cx * et.dx); p.dy += Math.round(cy * et.dx * 0.6) + et.dy - et.z;
      p.rot += et.rot * (cx >= 0 ? 1 : -1);
    } else if (e.etat === 'attaque' && e.phase && arme) {
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
    // ⚠️ `EN_MAIN` d'abord : le poing americain se ramasse en arme et se tient
    // en bout de poing. Sa propre cle au cache — jamais celle du sol.
    const sprite = p.arme.sprite;
    const image = EN_MAIN[sprite]
      ? Atlas.cuirePeintre('main|' + sprite, 16, 10, EN_MAIN[sprite])
      : Atlas.cuirePeintre('objet|' + sprite, 16, 10, function (g, w, h) {
        OBJETS[OBJETS[sprite] ? sprite : 'defaut'](g, w, h);
      });
    const mx = img.miroir ? (img.largeur - 1 - img.main[0]) : img.main[0];
    let angle = img.miroir ? Math.PI - img.main[2] : img.main[2];
    // Un bout de trois pixels tourne de biais n'est plus qu'une tache : au
    // repos, la main penche (0,9 rad de cote). Un dessin de main se tient donc
    // au quart de tour le plus proche.
    if (EN_MAIN[sprite]) angle = Math.round(angle / (Math.PI / 2)) * (Math.PI / 2);
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
  //: De combien un nageur s'enfonce, en pixels. ⚠️ Assez pour que les jambes
  //: disparaissent (le corps fait treize pixels, les jambes en font trois), pas
  //: assez pour couper le visage — c'est lui qui dit dans quel sens on nage.
  const SOUS_L_EAU = 5;

  function dessinerCorps(ctx, e, img, p, cx, cy) {
    const x = e.x - cx + p.dx, y = e.y - e.z - cy + p.dy;
    if (e.nage && !p.rot && p.echelleY === 1) {
      // ⚠️ On coupe A LA SOURCE, pas avec un `clip` : un `clip` coute un
      // `save`/`restore` par nageur et par image, et le dessin de la ville est
      // deja ce qui tient le rythme sur telephone.
      const haut = Math.max(1, img.canvas.height - SOUS_L_EAU);
      ctx.drawImage(img.canvas, 0, 0, img.canvas.width, haut,
                    Math.round(x - img.ancre[0]), Math.round(y - img.ancre[1]),
                    img.canvas.width, haut);
      return;
    }
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

  /** Les betes se dessinent avec le decor : meme porte (une fiche de `DECORS`,
      cuite par variante), mais leur propre liste. ⚠️ `altitude` est un decalage
      de DESSIN : le goeland qui s'envole monte a l'ecran et reste, pour tout le
      reste du jeu, la ou il etait. */
  function dessinerBetes(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const e of betes()) {
      // Une bete qui BOUGE (le chat, le raton) a son peintre de mouvement : l'allure, le
      // sens et l'image de sa foulee (`poseDeBete`). Assise, c'est son dessin d'avant.
      const pose = poseDeBete(e);
      const nom = pose ? pose.decor : e.decor, v = pose ? pose.cle : e.v;
      const d = DECORS[nom];
      if (!d) continue;
      if (e.x < cx - 40 || e.x > cx + VW + 40 || e.y < cy - 40 || e.y > cy + VH + 40) continue;
      const c = Atlas.cuirePeintre('decor|' + nom + '|' + v, d.w, d.h,
                                   function (g, w, h) { d.peindre(g, w, h, v); });
      ctx.drawImage(c, Math.round(e.x - d.ancre[0] - cx),
                    Math.round(e.y - d.ancre[1] - (e.altitude || 0) - cy));
      B.stats.images++;
    }
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

  /** La pose d'un decor ANIME a l'image `t` (par defaut, celle qui va se peindre).

      ⚠️ `travaille: 'jour'` : une machine de chantier s'arrete la nuit, a sa pose
      de repos (0) — et c'est cette fonction que `chantiers.js` relit pour savoir
      quand la boule frappe. Deux formules, et le coup partirait dans le vide. */
  function poseDuDecor(d, t, nuit) {
    if (!d.anime) return 0;
    if (d.travaille === 'jour' && (nuit === undefined ? Monde.estNuit() : nuit)) return 0;
    return Math.floor((t === undefined ? B.t : t) / d.anime) % d.variantes;
  }

  /** L'anneau de la cible verrouillee (`Combat.majCible`) : un repere carre qui
      respire au-dessus de la tete, dans le monde — pour VOIR qui on vise,
      pas seulement le sentir a la maniere dont on frappe. */
  function dessinerCible(ctx, cam) {
    const c = B.joueur && B.joueur.cible;
    if (!c || !c.vivant) return;
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    const x = Math.round(c.x - cx), y = Math.round(c.y - 20 - cy);
    const r = 5 + Math.round(Math.sin((B.image % 40) / 40 * Math.PI) * 2);
    ctx.fillStyle = '#ff5a3c';
    ctx.fillRect(x - r, y - r, r * 2 + 1, 1);
    ctx.fillRect(x - r, y + r, r * 2 + 1, 1);
    ctx.fillRect(x - r, y - r, 1, r * 2 + 1);
    ctx.fillRect(x + r, y - r, 1, r * 2 + 1);
    B.stats.rects += 4;
  }

  function dessiner(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    const visibles = [];
    const nuit = Monde.estNuit();
    for (const e of B.entites) {
      if (!e.dessine) continue;
      // ⚠️ UN DECOR SORT DE LA LISTE PAR SON DESSIN, pas par son pied. La marge
      // fixe (40 px, 48 au nord et au sud) coupait la grue a tour — 112 px de
      // large, 90 au-dessus de sa tuile — alors que sa fleche etait encore a
      // l'ecran : elle apparaissait d'un coup en montant la rue.
      // (Les feux ont leur propre peintre, plus grand que leur fiche : marge fixe.)
      const fiche = e.decor && e.type !== 'feu' && e.type !== 'feu_pieton' && DECORS[e.decor];
      if (fiche) {
        const x0 = e.x - fiche.ancre[0], y0 = e.y - fiche.ancre[1] - (e.altitude || 0);
        if (x0 + fiche.w < cx - 4 || x0 > cx + VW + 4 || y0 + fiche.h < cy - 4 || y0 > cy + VH + 4) continue;
      } else if (e.x < cx - 40 || e.x > cx + VW + 40 || e.y < cy - 48 || e.y > cy + VH + 48) continue;
      visibles.push(e);
    }
    // ⚠️ Les morts d'abord : un cadavre se fait marcher dessus, il ne cache
    // jamais un vivant.
    // ⚠️ UNE CHARGE SE PEINT APRES SA REMORQUEUSE. Le tri va du nord au sud ;
    // une moto posee sur le plateau a presque la meme hauteur que le camion, et
    // un demi-pixel decidait alors si on la voyait ou si elle disparaissait
    // dessous. On lui donne donc la profondeur de son porteur, plus un cheveu :
    // elle est toujours au-dessus, quel que soit le cap.
    // ⚠️ LE TRAIN ET LA MONTAGNE RUSSE DE LA FOIRE se trient avec le reste — un
    // wagon passe devant un passant ou derriere, selon sa rangee — mais ils ne
    // sont PAS dans `B.entites` (la lecon des betes). `Foire` ajoute ce qui est
    // a l'ecran, et chacun porte son peintre.
    if (!B.interieur) { Foire.ajouterVisibles(visibles, cx, cy); Traversier.ajouterVisibles(visibles, cx, cy); }
    const profond = function (e) { return e.remorqueePar ? e.remorqueePar.y + 0.5 : e.y; };
    visibles.sort(function (a, b) {
      return (a.vivant ? 1 : 0) - (b.vivant ? 1 : 0) || profond(a) - profond(b) || a.id - b.id;
    });
    B.stats.entites = visibles.length;
    const ombre = Atlas.cuirePeintre('ombre', DECORS.ombre.w, DECORS.ombre.h, DECORS.ombre.peindre);
    // ⚠️ La coop locale (essai) : « je verrais aussi comme distinction l'ombre
    // du personnage de couleur différente, vu qu'on peut s'habiller en
    // boutique » (Martin, 22 sept.) — le linge change au comptoir, l'ombre
    // jamais : un second repere qui tient quoi qu'on porte. Meme teal que
    // `COULEUR_COOP_JOUEUR2` (#16a085 = rgb(22,160,133)), juste plus opaque
    // qu'un noir a 30 % pour rester lisible a cette taille (12x6 px).
    const ombreCoop = Atlas.cuirePeintre('ombre_coop', DECORS.ombre.w, DECORS.ombre.h, function (ctx, w, h) {
      ctx.fillStyle = 'rgba(22,160,133,0.55)'; ctx.fillRect(2, 0, 8, 6); ctx.fillRect(0, 1, 12, 4);
    });
    const eauRemous = Atlas.cuirePeintre('remous', DECORS.remous.w, DECORS.remous.h, DECORS.remous.peindre);
    const bulles = [];
    for (const e of visibles) {
      // ⚠️ LES PEINTRES NOMMES D'ABORD, la branche generique ensuite. Dans
      // l'autre sens, un `decor` pose sur une entite qui a deja son peintre
      // l'EFFACE en silence : c'est ce qui est arrive aux feux, muets d'un
      // bout a l'autre de la ville parce qu'ils portaient `decor: 'feu'`.
      if (e.peindreFoire) { e.peindreFoire(ctx); continue; }
      if (e.type === 'feu') { Vehicules.dessinerFeu(ctx, e, cx, cy); continue; }
      if (e.type === 'feu_pieton') { Vehicules.dessinerFeuPieton(ctx, e, cx, cy); continue; }
      if (e.decor) {                 // decor ET commerces ambulants
        const d = DECORS[e.decor];
        if (!d) continue;
        // ⚠️ `anime` : le decor qui TOURNE. `variantes` sert alors de POSE et
        // non de couleur — la pose avance avec le temps au lieu d'etre tiree a
        // l'empreinte de la tuile. C'est l'etage 1 des machines de chantier :
        // une articulation, pas dix — chaque pose est cuite UNE fois et reste
        // en cache, donc un manège qui tourne coute quatre canevas, pas un par
        // image.
        // ⚠️ `poseManuelle` : la grue qu'un joueur pilote (`Chantiers.piloter`) ne tourne plus toute
        // seule, elle prend la pose qu'on lui donne — jour ou nuit.
        const pose = e.poseManuelle !== undefined ? e.poseManuelle : d.anime ? poseDuDecor(d, B.t, nuit) : e.v;
        const c = d.variantes
          ? Atlas.cuirePeintre('decor|' + e.decor + '|' + pose, d.w, d.h,
                               function (g, w, h) { d.peindre(g, w, h, pose); })
          : Atlas.cuirePeintre('decor|' + e.decor, d.w, d.h, d.peindre);
        // ⚠️ CE QUI FLOTTE TANGUE. Un rond immobile sur l'eau se lit comme une
        // tache de peinture ; deux pixels de houle, et c'est une bouee. Le
        // mouvement est dans le DESSIN et pas dans `e.y` : la bouee est amarree,
        // et ce qui la heurte doit la trouver ou elle est.
        const houle = d.flotte ? Math.sin(e.t / 26 + e.x * 0.07) * 1.5 : 0;
        // ⚠️ L'ALTITUDE EST UN DECALAGE DE DESSIN, pas une position : le goeland
        // qui s'envole monte a l'ecran et reste, pour tout le reste du jeu, la ou
        // il etait. Rien ne se cogne dans un oiseau, donc rien n'a besoin de
        // savoir a quelle hauteur il vole.
        const vol = e.altitude || 0;
        ctx.drawImage(c, Math.round(e.x - d.ancre[0] - cx), Math.round(e.y - d.ancre[1] + houle - vol - cy));
        B.stats.images++;
        continue;
      }
      if (e.type === 'vehicule') {
        // ⚠️ UN CHAR QUI PASSE LE SEUIL D'UN GARAGE disparait sous le linteau, puis
        // derriere les lames qui descendent : on le peint, moins ce qui est au-dessus
        // du bas du rideau dans le passage (le reste de l'ecran, tout entier).
        // ⚠️ La zone vient de `Monde.sousLeToit` : ses lampes lisent la meme.
        const rideau = Monde.rideauPres(e);
        if (rideau) {
          const z = Monde.sousLeToit(rideau);
          ctx.save();
          ctx.beginPath();
          ctx.rect(0, 0, VW, VH);
          ctx.rect(z.x0 - cx, z.y0 - cy, z.x1 - z.x0, Math.max(0, z.y1 - z.y0));
          ctx.clip('evenodd');
          Vehicules.dessinerUn(ctx, e, cx, cy);
          ctx.restore();
        } else Vehicules.dessinerUn(ctx, e, cx, cy);
        continue;
      }
      if (e.type === 'ramassage' && e.objet === 'caisse') {
        const d = DECORS.caisse;
        const c = Atlas.cuirePeintre('decor|caisse', d.w, d.h, d.peindre);
        ctx.drawImage(c, Math.round(e.x - d.ancre[0] - cx), Math.round(e.y - d.ancre[1] + Math.sin(e.t / 14) * 1.5 - cy));
        B.stats.images++;
        continue;
      }
      if (e.type === 'ramassage' && OBJETS_PAR_TERRE[e.objet]) {
        const c = Atlas.cuirePeintre('objet|' + e.objet, 16, 10, function (g, w, h) { OBJETS[e.objet](g, w, h); });
        ctx.drawImage(c, Math.round(e.x - 8 - cx), Math.round(e.y - 8 + Math.sin(e.t / 14) * 1.5 - cy));
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
      // ⚠️ Un nageur n'a pas d'ombre au sol, il a un REMOUS — et son corps est
      // coupe a la ligne d'eau (`dessinerCorps`). Les deux ensemble : une tete
      // sans remous sur la baie ne se voit pas, et un corps entier sur l'eau a
      // l'air de marcher dessus.
      if (e.vivant && e.nage) {
        ctx.drawImage(eauRemous, Math.round(e.x - 7 - cx), Math.round(e.y - 3 - cy));
        B.stats.images++;
      } else if (e.vivant && !(e.alite && (e.etat === 'fige' || e.type === 'joueur'))) {
        // ⚠️ Pas d'ombre sous un malade couche : elle tomberait au milieu de la
        // couverture, une tache grise en travers du lit.
        ctx.drawImage(e.coopJoueur2 ? ombreCoop : ombre, Math.round(e.x - 6 - cx), Math.round(e.y - 3 - cy));
      }
      if (e.invincible > 0 && (e.invincible >> 2) % 2 === 0) continue;
      const p = pose(e);
      // L'arme passe DERRIERE le corps quand on regarde vers le haut.
      const derriere = e.face === 'haut';
      if (derriere) dessinerArme(ctx, e, img, p, cx, cy);
      dessinerCorps(ctx, e, img, p, cx, cy);
      if (!derriere) dessinerArme(ctx, e, img, p, cx, cy);
      B.stats.images += 2;
      // Un mot a dire l'emporte sur la pastille : on ne porte pas deux bulles.
      // ⚠️ Sauf pendant un dialogue : quelqu'un te PARLE, dans la boite en bas
      // de l'ecran — personne ne t'interpelle par-dessus.
      if (e.bulle && e.vivant) { if (!B.cinema) bulles.push(e); continue; }
      // La bulle du temoin : on doit VOIR qu'on a ete vu.
      if (e.cri > 0 && e.vivant) {
        const bulle = Atlas.cuirePeintre('bulle|' + (e.etat === 'temoin' ? 't' : 'p'), 8, 10, function (g, w, h) {
          BULLES[e.etat === 'temoin' ? 'temoin' : 'peur'](g, w, h);
        });
        ctx.drawImage(bulle, Math.round(e.x - 4 - cx), Math.round(e.y - 26 - cy));
        B.stats.images++;
      }
    }
    for (const e of bulles) dessinerBulle(ctx, e, cx, cy);
  }

  return {
    orignalDeLaNuit, majOrignal, faireFuirLOrignal,
    CELLULE, BULLE_NAISSANCE, BULLE_OUBLI, MAX_PIETONS, MAX_DECALS, MAX_PARTICULES, PORTEE_DECOR,
    creer, retirer, vider, creerJoueur, creerJoueur2, joueurs, estJoueur, creerDecor, creerAmbulants, majKiosques, creerPaquets, creerPieton, reindexerDecor,
    briser, endommagerDecor, reparerLeDecor, releverDecor, DEBRIS_MAX,
    peuplerInterieur, PIEDS_ALITE, coucher, seLever,
    archetype, archetypeDeRue,
    indexer, autour, decorAutour, pietonsAutour, placeDeNaissance, placeAuBordDeLaRoute, porteQuiSert, quelquUnRentre, envoyerAUnePorte, peupler, peuplerDabord,
    naitreLesSortes, majSortes, SORTES, SPECTACLES, badauds, artistes, ouvrirLeSpectacle,
    naitreLesHommesSandwichs, enService, solliciter,
    semerDesArmesDeFortune, visibleAEcran,
    plageEn, litLibre, coinDePlage,
    deplacerCercle, dansLaCarte, regarder, majJoueur, majPieton, maj, demeler, deboutDansLaFoule, pasDeDemele, mouiller,
    enjamber, majEnjambe, clotureDevant, reglesCloture,
    blesser, assommer, tuer, alerter, lacherArme, traverseeSure, trottoirLePlusProche, naitreLesOuvriers, naitreLEquipe, pousserDecor, boiteTouche, majVolDeChar, emporterLeChar,
    majBagarre, allumerLaBagarre, frontiereProche, rivalDe, enPleineRixe, majAqueduc, JET_EAU_IMAGES,
    naitreLesEnfantsDeLaPlage, majPlage, plierBagage, naitreLeLastCall, chicaner, majCamelot, prochainPerron,
    poserLeJournal, rentrerLesJournaux, fairePartirUnRaton, bordDeLEau, chateauLePlusProche, majBallonVol, lancerLeBallon,
    naitreLesEnfantsAVelo, placeDEnfantAVelo, roulableEnfant, resterSurLeTrottoir,
    naitreLesBetes, majBete, majLesBetes, chezElle, placeDeBete, betes, dessinerBetes, poseDeBete, directionDeBete, sEnvoler,
    naitreLaFoire, majForain, majMascotte, placeDansLaFoire, destinationDeFoire,
    bulle, taire, dessinerBulle, dansLEau, remous, noyade, masqueDe, mousse,
    particule, sang, poussiere, decal, majParticules,
    dessiner, dessinerDecals, dessinerParticules, dessinerCible, imageDe, nomDePose, pose, poseDuDecor,
  };
})();
