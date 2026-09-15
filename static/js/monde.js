/* Bandini — monde : la carte active, les collisions, la camera, l'heure.

   La carte vient du serveur (paquet `carte`) : lignes de glyphes + legende.
   Ici on en derive des tableaux types (solidite, route) et un cache de rendu
   par morceaux de 16x16 tuiles, peints une fois. */

const Monde = (function () {
  'use strict';

  const MORCEAU = 16;                 // tuiles par cote d'un morceau
  const MORCEAU_PX = MORCEAU * TT;
  // ⚠️ Le Faubourg fait 77 morceaux ; a 256x256 en RGBA, tout gardez-vous
  // coute 20 Mo de canevas — un telephone rend l'ame bien avant. On n'en garde
  // que le tour de l'ecran (9 visibles au pire), avec de la marge pour ne pas
  // repeindre a chaque pas de cote.
  const MORCEAUX_MAX = 24;
  // Masques de collision, un bit par sorte d'obstacle (voir `solidite`).
  const MUR = 1, EAU = 2, BASSE = 4, GRILLAGE = 8, BARBELE = 16;
  // ⚠️ Le CORPS d'un pieton ne franchit aucune cloture : il s'arrete dessus.
  // Avant, `f` etait solide 3 (BASSE) et ce masque ne la voyait pas — une
  // cloture n'arretait que les chars, et a pied on la traversait sans meme
  // ralentir. C'est ce qui la rendait muette.
  const MASQUE_PIETON = MUR | EAU | GRILLAGE | BARBELE;
  // ⚠️ LE NAGEUR NE VOIT PAS L'EAU. C'est le masque du joueur et des agents —
  // eux seuls entrent dans la baie. Les passants gardent `MASQUE_PIETON` : un
  // flaneur qui part se baigner parce que son errance l'y a mene, c'est le
  // genre de chose qu'on ne voit qu'en jeu, et il n'y a rien a y gagner.
  const MASQUE_NAGEUR = MUR | GRILLAGE | BARBELE;
  // ⚠️ Un char NE FLOTTE PAS : il entre dans l'eau, et il coule (voir
  // `vehicules.js`). Le masque le laisse donc passer — c'est le fond de la
  // baie qui l'arrete, pas une facade invisible au bord de l'eau.
  const MASQUE_VEHICULE = MUR | BASSE | GRILLAGE | BARBELE;
  // ⚠️ Le masque des CHEMINS a pied, et il n'est pas celui des corps : un
  // grillage s'enjambe, donc un chemin peut le traverser — plus cher qu'une
  // tuile normale (`COUT_GRILLAGE`), jamais gratuitement. Si le A* s'arretait
  // aux clotures comme les corps, la premiere cloture venue gagnerait toutes
  // les poursuites : on enjambe, et les agents restent plantes de l'autre cote.
  // ⚠️ L'eau n'y est plus non plus : un agent nage derriere toi, sinon l'eau
  // devient l'exploit anti-police le plus simple du jeu — deux pas dans la baie
  // et on est intouchable. Elle se PAIE, comme le grillage (`coutEau`) : la
  // traversee d'un chenal reste un detour cher, la baie reste impensable.
  const MASQUE_A_PIED = MUR | BARBELE;

  const SORTES_DE_LAMPE = {
    poteau: { dy: 2, c: 'rgba(255,214,130,0.55)' },
    vitrine: { dy: 6, c: 'rgba(255,226,170,0.34)' },
    fenetre: { dy: 8, c: 'rgba(255,212,150,0.22)' },
  };

  let carte = null;

  function charger(def) {
    const w = def.largeur, h = def.hauteur;
    const solide = new Uint8Array(w * h);
    const route = new Uint8Array(w * h);
    const passage = new Uint8Array(w * h);     // passage pieton : route ET trottoir
    const portesFermees = [];                   // les « d » : par ou les gens rentrent chez eux
    for (let y = 0; y < h; y++) {
      const ligne = def.sol[y];
      for (let x = 0; x < w; x++) {
        const p = def.legende[ligne[x]] || {};
        solide[y * w + x] = p.solide || 0;
        route[y * w + x] = p.route ? 1 : 0;
        passage[y * w + x] = (p.route && p.trottoir) ? 1 : 0;
        // ⚠️ Le GLYPHE reste avec la porte : un `d` est un LOGEMENT (battant
        // sombre, pas de poignee de laiton, aucune enseigne) et un `D` mene a
        // un interieur. Les gens passent les deux ; le joueur, seulement les
        // `D` — et le dessin le dit deja, c'est ce qui rend la regle lisible.
        if (ligne[x] === 'd' || ligne[x] === 'D') portesFermees.push({ x: x, y: y, glyphe: ligne[x] });
      }
    }
    const portes = new Map();
    (def.portes || []).forEach(function (p) { portes.set(p.x + ',' + p.y, p); });
    // Chaque tuile de croisement connait son croisement : un char a la ligne
    // d'arret demande a QUEL feu il obeit.
    // ⚠️ La boite inclut les PASSAGES PIETONS (deux tuiles de chaque cote) :
    // un pieton au bord du passage demande, lui aussi, a quel feu il obeit.
    const croisements = new Map();
    (def.intersections || []).forEach(function (inter, i) {
      inter.i = i;
      inter.decalage = hash2(inter.x, inter.y) % 600;
      inter.feux = inter.bras.length >= 4;
      // Un T : la rue qui s'arrete (la tige) a un STOP. Son approche est le
      // sens qui va de la tige vers le croisement.
      inter.stop = null;
      if (inter.bras.length === 3) {
        const manquant = 'NSOE'.split('').find(function (b) { return inter.bras.indexOf(b) < 0; });
        inter.stop = { N: '^', S: 'v', O: '<', E: '>' }[manquant];   // bras manquant N → la tige est S → on arrive en montant
      }
      // ⚠️ LA LARGEUR DU TROTTOIR VIENT DU PAQUET, elle ne s'ecrit pas ici.
      // C'etait deux litteraux — « pour inclure les passages pietons, deux
      // tuiles de chaque cote » — alors que la traverse fait exactement
      // `TROTTOIR` tuiles de profond, par construction : c'est la meme
      // constante des deux cotes. Le jour ou elle bougera, Python dessinera
      // des traverses d'une tuile et ce JS en aurait reclame deux : un pieton
      // demanderait a quel feu obeir en se tenant sur la chaussee, et un char
      // lirait un croisement la ou il n'y en a plus.
      const bord = (def.grille && def.grille.trottoir) || 2;
      for (let y = inter.y - bord; y < inter.y + inter.h + bord; y++) {
        for (let x = inter.x - bord; x < inter.x + inter.l + bord; x++) croisements.set(x + ',' + y, inter);
      }
    });
    carte = {
      def: def, w: w, h: h, sol: def.sol, voie: def.voie, legende: def.legende,
      // Le plancher d'une piece : ce qu'on peint SOUS les meubles (null dehors).
      plancher: def.plancher || null,
      solide: solide, route: route, passage: passage, portesFermees: portesFermees,
      morceaux: new Map(), visibles: new Set(),
      // Les battants qui s'ouvrent : hors du cache de morceaux (voir `ouvrirPorte`).
      battants: new Map(),
      portesParTuile: portes, mini: null, croisements: croisements, arrets: def.arrets || {},
      intersections: def.intersections || [],
      // ⚠️ Trois sortes de lumiere, et elles ne se ressemblent pas : le
      // LAMPADAIRE (haut, large, blanc-jaune), la VITRINE (basse et chaude,
      // un reflet sur le trottoir) et la FENETRE d'un logement (faible, dans
      // le mur — on doit deviner qu'il y a quelqu'un, pas lire son journal).
      lampes: (def.lampes || []).map(function (l) {
        const sorte = SORTES_DE_LAMPE[l.c] || SORTES_DE_LAMPE.poteau;
        return { x: l.x * TT + 8, y: l.y * TT + sorte.dy, r: l.r || 44, c: sorte.c };
      }),
      portes: def.portes || [],
      rampes: def.rampes || [],
      // La cour du lot, ses cases et sa grille : c'est `Missions` qui y range
      // les chars saisis (null dans un interieur).
      fourriere: def.fourriere || null,
      points: def.points_interet || [],
      zones: def.zones || [],
      apparition: def.apparition,
      pxW: w * TT, pxH: h * TT,
      devantures: indexerParMorceau(def.devantures || [], function (d) {
        // ⚠️ TROIS rangees : la tuile de toit AU-DESSUS du mur (l'enseigne y
        // monte, voir FACADES.enseigne), le mur, et le trottoir sous lui (la
        // pancarte y pend). Sans la premiere, une enseigne assise sur la
        // premiere rangee d'un morceau perdait sa moitie haute a la couture.
        return [d.x, d.y - 1, d.l, 3];
      }),
      // Les logements : meme regle, l'escalier de fer descend sur le trottoir.
      residences: indexerParMorceau(def.residences || [], function (r) {
        return [r.x, r.y, r.l, 2];
      }),
      // ⚠️ LA FOSSE D'UN ARBRE DE RUE. Demande de Martin : « les arbres qui
      // sont sur un trottoir doivent avoir un petit rond de terre à leur
      // pied ». Un arbre planté dans le béton sans rien à son pied, c'est un
      // arbre POSÉ sur le trottoir — et c'est ce qu'on voyait sur la place
      // publique du Faubourg. C'est la LÉGENDE qui décide (`terre`), pas le
      // dessin : le gazon, le sable et l'allée de parc n'ont rien à découper.
      // ⚠️ Et c'est une COUCHE PEINTE, pas un décor de plus : elle se cuit avec
      // le morceau, sous tout le reste, et rien ne s'y cogne. Un rond de terre
      // redessiné à chaque image sous chaque arbre de rue coûterait cher pour
      // ce qu'il dit — et il passerait par-dessus les pieds de celui qui
      // marche juste au nord de l'arbre.
      fosses: indexerParMorceau((def.decor || []).filter(function (d) {
        if (d.type !== 'arbre') return false;
        return !(def.legende[def.sol[d.y][d.x]] || {}).terre;
      }), function (d) { return [d.x, d.y, 1, 2]; }),
      graffitis: indexerParMorceau(def.graffitis || [], function () { return [0, 0, 1, 1]; }),
      // Ce qu'un toit porte : une tuile chacun, meme regle d'index.
      toits: indexerParMorceau(def.toits || [], function () { return [0, 0, 1, 1]; }),
    };
    B.carte = carte;
    return carte;
  }

  /** Entre dans une piece : on garde la ville de cote et on charge la petite
      carte ASCII de l'interieur (meme legende, aucune voie, aucune lampe). */
  function entrer(porte) {
    const ville = carte;
    const commune = ville.def.interieurs[porte.interieur];
    if (!commune) return null;
    // ⚠️ Le nom vient de la PORTE quand elle en porte un : dix-huit commerces
    // partagent la meme piece, et le bandeau qu'on vient de lire dans la rue
    // est la seule chose qui les distingue. D'ou la COPIE : renommer la piece
    // du catalogue renommerait les dix-sept autres.
    const inte = Object.assign({}, commune, { nom: porte.nom || commune.nom });
    const def = {
      slug: inte.slug, nom: inte.nom, largeur: inte.largeur, hauteur: inte.hauteur, sol: inte.sol,
      plancher: inte.plancher,
      voie: inte.sol.map(function (l) { return '.'.repeat(l.length); }), legende: ville.legende,
      portes: [{ x: inte.sortie.x, y: inte.sortie.y, interieur: null, lieu: 'sortie' }],
      lampes: [], decor: [], zones: [], points_interet: [], intersections: [], arrets: {},
      apparition: { joueur: inte.apparition }, interieurs: {}, ambulants: [],
    };
    charger(def);
    carte.interieur = inte;
    carte.ville = ville;
    carte.porte = porte;
    return carte;
  }

  /** Monte (ou descend) d'un etage : on change de piece sans ressortir.

      ⚠️ La ville et la PORTE d'ou l'on vient ne bougent pas : c'est par elles
      qu'on ressortira, meme trois etages plus haut. Un escalier qui rechargeait
      la ville aurait remis le joueur sur le trottoir a chaque marche. */
  function changerPiece(slug) {
    if (!carte || !carte.interieur || !carte.ville) return null;
    const ville = carte.ville, porte = carte.porte;
    carte = ville;
    B.carte = ville;
    // ⚠️ Sans le nom : l'etage a le sien (« Un logement, en haut »), et c'est
    // la seule facon de savoir qu'on a change de plancher.
    return entrer(Object.assign({}, porte, { interieur: slug, nom: null }));
  }

  /** Ressort : la ville reprend sa place telle qu'on l'a laissee (morceaux
      cuits compris — rien a repeindre). */
  function restaurer(ville) {
    carte = ville;
    B.carte = ville;
    return ville;
  }

  function glyphe(tx, ty) {
    if (!carte || tx < 0 || ty < 0 || tx >= carte.w || ty >= carte.h) return 'B';
    return carte.sol[ty][tx];
  }
  function solidite(tx, ty) {
    if (!carte || tx < 0 || ty < 0 || tx >= carte.w || ty >= carte.h) return 1;
    return carte.solide[ty * carte.w + tx];
  }
  function bloque(tx, ty, masque) {
    const s = solidite(tx, ty);
    if (s === 1) return (masque & MUR) !== 0;
    if (s === 2) return (masque & EAU) !== 0;
    if (s === 3) return (masque & BASSE) !== 0;
    if (s === 4) return (masque & GRILLAGE) !== 0;
    if (s === 5) return (masque & BARBELE) !== 0;
    return false;
  }
  /** Un lourd passe AU TRAVERS d'un obstacle bas : la tuile tombe, et le sol
      de ses voisines prend sa place. Rend vrai si quelque chose a cede.

      ⚠️ **Jamais une façade** (`solide 1`), jamais l'eau, jamais le barbelé, et
      jamais un meuble : la ville tient par ses murs — les juges de connexité,
      les intérieurs et les devantures en dépendent, et un trou dans un mur
      ouvrirait sur un toit. Ce qui se défonce, c'est ce qui est BAS : la
      borne-fontaine (3), le grillage et la palissade (4).

      ⚠️ Et le glyphe de remplacement se LIT DANS LES VOISINES. Une clôture
      entre un gazon et un trottoir laisse du gazon ou du trottoir — jamais une
      tuile inventée. C'est ce qui évite un glyphe « décombres » de plus, avec
      son peintre, son entrée de légende et son octet dans le paquet : le trou
      dans une clôture, c'est la clôture qui manque, pas des gravats. */
  function defoncer(tx, ty) {
    const s = solidite(tx, ty);
    if (s !== 3 && s !== 4) return false;
    if (estMeuble(tx, ty)) return false;
    // Le sol d'à côté : on préfère ce qui n'est pas de la chaussée (une
    // clôture borde une cour bien plus souvent qu'une rue).
    let remplacant = null, secours = null;
    for (const d of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
      const vx = tx + d[0], vy = ty + d[1];
      if (solidite(vx, vy) !== 0) continue;
      const g = glyphe(vx, vy);
      if (estRoute(vx, vy)) { if (!secours) secours = g; continue; }
      remplacant = g;
      break;
    }
    remplacant = remplacant || secours;
    if (!remplacant) return false;
    const p = carte.legende[remplacant] || {};
    const ligne = carte.sol[ty];
    carte.sol[ty] = ligne.slice(0, tx) + remplacant + ligne.slice(tx + 1);
    const i = ty * carte.w + tx;
    carte.solide[i] = p.solide || 0;
    carte.route[i] = p.route ? 1 : 0;
    carte.passage[i] = (p.route && p.trottoir) ? 1 : 0;
    // ⚠️ Les morceaux VOISINS aussi : une clôture lit ses voisines pour savoir
    // comment se peindre (`varianteDeCloture`), donc en casser une change le
    // dessin des deux d'à côté — qui peuvent être dans un autre morceau.
    for (let dy = -1; dy <= 1; dy++) {
      for (let dx = -1; dx <= 1; dx++) {
        carte.morceaux.delete(Math.floor((tx + dx) / MORCEAU) + ',' + Math.floor((ty + dy) / MORCEAU));
      }
    }
    return true;
  }

  /** Une cloture qui s'enjambe a cette tuile — grillage ou palissade de bois
      (voir `Entites.enjamber`). Le barbele, lui, ne s'enjambe pas. */
  function estEnjambable(tx, ty) { return solidite(tx, ty) === 4; }
  function estRoute(tx, ty) {
    if (!carte || tx < 0 || ty < 0 || tx >= carte.w || ty >= carte.h) return false;
    return carte.route[ty * carte.w + tx] === 1;
  }
  function estPassage(tx, ty) {
    if (!carte || tx < 0 || ty < 0 || tx >= carte.w || ty >= carte.h) return false;
    return carte.passage[ty * carte.w + tx] === 1;
  }
  /** La chaussee nue : la ou un pieton n'a rien a faire. */
  function estChaussee(tx, ty) { return estRoute(tx, ty) && !estPassage(tx, ty); }
  /** L'abord : la couronne d'un bloc, entre ses murs et le trottoir. On y
      marche, mais c'est un debordement — la dalle est prioritaire. */
  function estAbord(tx, ty) { return !!((carte && carte.legende[glyphe(tx, ty)] || {}).abord); }
  function estTrottoir(tx, ty) { return !!((carte && carte.legende[glyphe(tx, ty)] || {}).trottoir) && !estRoute(tx, ty); }
  /** Une tuile qu'un pieton peut fouler en flanant : ni mur, ni eau, ni chaussee.
      ⚠️ Elle garde l'eau MEME depuis qu'on nage : ce qui flane ne se baigne
      pas, et les juges de connexite s'appuient dessus — si l'eau reliait les
      rives, `composantes_marchables` ne dirait plus rien du tout. */
  function marchablePieton(tx, ty) { return !bloque(tx, ty, MASQUE_PIETON) && !estChaussee(tx, ty); }
  /** De l'eau : on y nage, on y coule, et un char s'y enfonce. */
  function estEau(tx, ty) { return solidite(tx, ty) === 2; }
  /** Un meuble (table, comptoir, lit...) : un pieton PASSE dessus — la legende
      ne l'arrete pas — mais personne n'a a s'y tenir debout. */
  function estMeuble(tx, ty) { return !!((carte && carte.legende[glyphe(tx, ty)] || {}).meuble); }

  /** Ligne de vue entre deux points (pixels) : rien de MUR entre les deux. */
  function ligneLibre(x0, y0, x1, y1) {
    let tx = Math.floor(x0 / TT), ty = Math.floor(y0 / TT);
    const fx = Math.floor(x1 / TT), fy = Math.floor(y1 / TT);
    const dx = Math.abs(fx - tx), dy = Math.abs(fy - ty);
    const sx = tx < fx ? 1 : -1, sy = ty < fy ? 1 : -1;
    let err = dx - dy, n = dx + dy + 1;
    while (n-- > 0) {
      if (solidite(tx, ty) === 1) return false;
      if (tx === fx && ty === fy) return true;
      const e2 = err * 2;
      if (e2 > -dy) { err -= dy; tx += sx; }
      if (e2 < dx) { err += dx; ty += sy; }
    }
    return true;
  }

  //: Combien d'images un battant met a s'ouvrir, et combien il reste ouvert.
  //: ⚠️ Assez lent pour qu'on VOIE la porte bouger, assez court pour qu'un
  //: passant n'attende pas sur le trottoir.
  const BATTANT_OUVRE = 12, BATTANT_TIENT = 26;

  /** Ouvre le battant de cette tuile (ou rallonge son ouverture).

      ⚠️ **Une porte animee ne peut pas etre une tuile.** Le sol est CUIT dans
      le morceau de 256 px : repeindre un morceau a chaque image pour un
      battant tuerait le cache qui tient le rythme sur telephone. Le battant
      est donc un petit dessin pose PAR-DESSUS, et seulement pour les portes a
      l'ecran — il y en a une poignee. C'est la meme lecon que les feux pour
      pietons : le poteau est une entite, la traverse est une tuile. */
  function ouvrirPorte(tx, ty) {
    if (!carte) return null;
    const cle = tx + ',' + ty;
    let b = carte.battants.get(cle);
    if (!b) {
      b = { x: tx, y: ty, t: BATTANT_OUVRE + BATTANT_TIENT };
      carte.battants.set(cle, b);
      return b;
    }
    // ⚠️ Redemander une porte DEJA EN TRAIN DE S'OUVRIR ne la remet pas a
    // zero : un pieton qui attend devant appelle a chaque image, et le battant
    // restait alors fige au premier pixel — il ne s'ouvrait jamais.
    if (b.t > BATTANT_TIENT) return b;
    b.t = BATTANT_TIENT;                 // elle se refermait : on la retient ouverte
    return b;
  }

  /** De 0 (fermee) a 1 (grande ouverte). `t` descend : il s'ouvre au debut,
      il tient, puis il se referme sur ses dernieres images. */
  function battant(tx, ty) {
    const b = carte && carte.battants.get(tx + ',' + ty);
    if (!b || b.t <= 0) return 0;
    if (b.t > BATTANT_TIENT) return (BATTANT_OUVRE + BATTANT_TIENT - b.t) / BATTANT_OUVRE;
    return Math.min(1, b.t / BATTANT_OUVRE);
  }

  function majBattants() {
    if (!carte) return;
    for (const b of carte.battants.values()) {
      if (b.t > 0) b.t--;
      else carte.battants.delete(b.x + ',' + b.y);
    }
  }

  /** Le battant, par-dessus le sol : un rectangle sombre qui s'efface en
      s'ouvrant, et le noir de l'interieur derriere. */
  function dessinerBattants(ctx, cam) {
    if (!carte || !carte.battants.size) return;
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const b of carte.battants.values()) {
      const x = b.x * TT - cx, y = b.y * TT - cy;
      if (x < -TT || x > VW || y < -TT || y > VH) continue;
      const p = battant(b.x, b.y);
      if (p <= 0) continue;
      ctx.fillStyle = '#100c0a';                       // le dedans, dans l'ombre
      ctx.fillRect(x + 4, y + 3, 8, 13);
      const reste = Math.max(0, Math.round(8 * (1 - p)));
      if (reste > 0) {
        ctx.fillStyle = '#3d2a1c';
        ctx.fillRect(x + 4, y + 3, reste, 13);
      }
      B.stats.rects += 2;
    }
  }

  /** Une porte a cette tuile ? (index : on interroge a chaque image) */
  function porteA(tx, ty) {
    return carte.portesParTuile.get(tx + ',' + ty) || null;
  }

  function fleche(tx, ty) {
    if (!carte || tx < 0 || ty < 0 || tx >= carte.w || ty >= carte.h) return '.';
    return carte.voie[ty][tx];
  }

  /** Le sens d'une ligne d'arret ('>' '<' '^' 'v'), ou null. */
  function sensArret(tx, ty) { return carte.arrets[tx + ',' + ty] || null; }

  function intersectionA(tx, ty) { return carte.croisements.get(tx + ',' + ty) || null; }

  /** De quelle couleur est le feu pour qui roule dans ce sens vers ce
      croisement : 'vert', 'jaune' ou 'rouge'.

      ⚠️ C'EST LA SEULE SOURCE, et c'est voulu. `feuVert` en decoule, le
      DESSIN du tricolore en decoule, et le trafic obeit a `feuVert` : une
      lanterne ne peut donc pas montrer une couleur que le char ne respecte
      pas. Le jour ou ca fera deux fonctions, elles divergeront — c'est
      exactement ce qui etait arrive au feu pieton, qui relisait `!feuVert`
      au lieu d'avoir sa propre regle et se trompait d'un temps.

      ⚠️ Un croisement en T ou en L n'a pas de feu : on y passe a vue, donc
      'vert'. */
  function feuDeCirculation(inter, sens) {
    if (!inter || !inter.feux) return 'vert';
    const t = B.defs.conduite.trafic;
    const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
    const phase = (B.t + inter.decalage) % cycle;
    const nordSud = sens === '^' || sens === 'v';
    const moitie = phase < cycle / 2;
    // Premiere moitie : nord-sud roule. Ce n'est pas mon tour : rouge, tout du long.
    if (nordSud !== moitie) return 'rouge';
    // Mon tour : vert, puis le jaune qui ferme la moitie.
    const dansMoitie = moitie ? phase : phase - cycle / 2;
    return dansMoitie >= t.feu_vert_images ? 'jaune' : 'vert';
  }

  /** Le feu est-il vert pour qui roule dans ce sens vers ce croisement ?
      ⚠️ Le JAUNE n'est pas vert : un char qui arrive a la ligne d'arret sur
      le jaune s'arrete. C'est ce qui donne au degagement du feu pieton son
      sens — sans ca, le croisement ne se viderait jamais. */
  function feuVert(inter, sens) { return feuDeCirculation(inter, sens) === 'vert'; }

  /** Le feu PIETON d'un croisement, pour qui traverse la rue ou les chars
      vont dans le sens `sens`. Rend 'blanc' (on s'engage), 'degage' (on ne
      s'engage plus, on finit) ou 'rouge'.

      ⚠️ IL SE TROMPAIT D'UN TEMPS. `traverseeSure` lisait `!feuVert(...)`, qui
      est vrai pendant l'ORANGE aussi : les pietons s'engageaient exactement
      quand les chars accelerent pour vider le croisement — le pire moment du
      cycle. Un feu pieton ne s'allume pas au rouge : il s'eteint AVANT que les
      chars repartent, et c'est ce degagement qui manquait.

      ⚠️ Aucun etat a garder : comme `feuVert`, c'est une pure fonction de `B.t`
      et du decalage du croisement. Trois cent cinquante poteaux ne coutent donc
      rien de plus qu'un. */
  function feuPieton(inter, sens) {
    if (!inter || !inter.feux) return 'aucun';
    const t = B.defs.conduite.trafic;
    const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
    const phase = (B.t + inter.decalage) % cycle;
    const nordSud = sens === '^' || sens === 'v';
    const moitie = phase < cycle / 2;
    const dansMoitie = moitie ? phase : phase - cycle / 2;
    // L'orange, des deux cotes : personne ne s'engage.
    if (dansMoitie >= t.feu_vert_images) return 'rouge';
    // Le vert de MA rue : les chars passent, j'attends.
    if (nordSud === moitie) return 'rouge';
    // Le vert d'en face : je marche — sauf sur la fin, le degagement.
    const reste = t.feu_vert_images - dansMoitie;
    return reste <= t.feu_pieton_degagement_images ? 'degage' : 'blanc';
  }

  function estRampe(tx, ty) {
    const p = carte && carte.legende[glyphe(tx, ty)];
    return !!(p && p.rampe);
  }

  /** La porte collee a la tuile ou se tient `e` : au nord dehors (une facade),
      au sud dedans (la sortie est sur le mur du bas). Jamais les deux. */
  function porteDevant(e) {
    const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
    return porteA(tx, ty - 1) || porteA(tx, ty + 1);
  }

  /** La zone nommee qui contient ce point (la derniere gagne : la plus precise). */
  function zoneA(x, y) {
    let trouvee = null;
    for (const z of carte.zones) {
      if (x >= z.x * TT && x < (z.x + z.l) * TT && y >= z.y * TT && y < (z.y + z.h) * TT) trouvee = z;
    }
    return trouvee;
  }

  // --- Chemins : un A* a budget --------------------------------------------------------
  //: Les demandes font la file ; on en sert DEUX par image, chacune plafonnee a
  //: 800 noeuds — un chemin introuvable ne doit pas geler l'image. Le demandeur
  //: repart en ligne droite en attendant (`repli`).

  const fileChemins = [];
  const BUDGET_PAR_IMAGE = 2, NOEUDS_MAX = 800;
  //: Ce que coute une tuile de cloture dans un chemin a pied, en tuiles de
  //: marche. ⚠️ Il vient du paquet (`recherche.clotures`) : la duree de
  //: l'enjambee et son prix dans le chemin doivent rester la MEME decision, et
  //: le jour ou l'un bouge sans l'autre, un agent choisit la cloture pour
  //: gagner du temps qu'il ne gagne pas.
  function coutCloture() {
    const c = B.defs && B.defs.recherche && B.defs.recherche.clotures;
    return (c && c.cout_chemin_tuiles) || 5;
  }
  //: Ce que coute une tuile d'EAU dans un chemin a pied. ⚠️ Meme raison que la
  //: cloture : sans prix, le plus court chemin couperait par la baie a chaque
  //: fois, et un agent traverserait a la nage ce qu'un homme met une minute a
  //: contourner. Huit tuiles de marche — le chenal du pont coute alors quatre-
  //: vingt-huit tuiles de detour, ce qui est a peu pres le tour par le pont.
  function coutEau() {
    const n = B.defs && B.defs.recherche && B.defs.recherche.nage;
    return (n && n.cout_chemin_tuiles) || 8;
  }

  /** Demande un chemin en tuiles de (x0,y0) a (x1,y1) en pixels ; `fait(chemin)`
      recoit une liste de {x, y} (pixels, centres de tuiles) ou null. */
  function demanderChemin(x0, y0, x1, y1, masque, fait) {
    fileChemins.push({ x0: x0, y0: y0, x1: x1, y1: y1, masque: masque, fait: fait });
  }

  function majChemins() {
    for (let n = 0; n < BUDGET_PAR_IMAGE && fileChemins.length; n++) {
      const d = fileChemins.shift();
      d.fait(chemin(d.x0, d.y0, d.x1, d.y1, d.masque));
    }
  }

  /** A* sur la grille (4 voisins), synchrone, plafonne. Rend des centres de
      tuiles en pixels, depart exclu, ou null si trop loin / bloque. */
  function chemin(x0, y0, x1, y1, masque) {
    const sx = Math.floor(x0 / TT), sy = Math.floor(y0 / TT), gx = Math.floor(x1 / TT), gy = Math.floor(y1 / TT);
    if (!carte || bloque(gx, gy, masque)) return null;
    if (sx === gx && sy === gy) return [];
    const w = carte.w, cout = coutCloture(), coutE = coutEau();
    const ouvert = [{ x: sx, y: sy, g: 0, f: Math.abs(gx - sx) + Math.abs(gy - sy) }];
    const vu = new Map();      // cle -> { g, parent }
    vu.set(sy * w + sx, { g: 0, parent: -1 });
    let noeuds = 0;
    while (ouvert.length) {
      // Le plus prometteur : une file simple suffit a 800 noeuds.
      let mi = 0;
      for (let i = 1; i < ouvert.length; i++) if (ouvert[i].f < ouvert[mi].f) mi = i;
      const c = ouvert.splice(mi, 1)[0];
      if (c.x === gx && c.y === gy) {
        const out = [];
        let cle = gy * w + gx;
        while (cle !== sy * w + sx) {
          out.push({ x: (cle % w) * TT + 8, y: Math.floor(cle / w) * TT + 8 });
          cle = vu.get(cle).parent;
        }
        return out.reverse();
      }
      if (++noeuds > NOEUDS_MAX) return null;
      for (const d of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = c.x + d[0], ny = c.y + d[1];
        if (nx < 0 || ny < 0 || nx >= carte.w || ny >= carte.h || bloque(nx, ny, masque)) continue;
        // ⚠️ Une cloture que le masque laisse passer se PAIE : c'est une
        // seconde en haut d'un grillage ou d'une palissade, pas un pas. Sans ce
        // cout, le chemin le plus court passerait toujours par-dessus les
        // clotures — et un agent ferait le tour de la ville en escaladant.
        const sn = solidite(nx, ny);
        const cle = ny * w + nx, g = c.g + (sn === 4 ? cout : sn === 2 ? coutE : 1);
        const deja = vu.get(cle);
        if (deja && deja.g <= g) continue;
        vu.set(cle, { g: g, parent: c.y * w + c.x });
        ouvert.push({ x: nx, y: ny, g: g, f: g + Math.abs(gx - nx) + Math.abs(gy - ny) });
      }
    }
    return null;
  }

  // --- Rendu du sol ---------------------------------------------------------------

  /** Un passage pieton fait deux tuiles de large, mais ses bandes n'en
      couvrent que les deux tiers (21 px), collees au croisement. Le peintre
      doit donc savoir s'il est la tuile INTERIEURE (bandes pleines) ou
      l'EXTERIEURE (un bout de bande du cote du croisement) : on le lit dans
      ses voisines — l'interieure touche la boite (voie « + »), l'exterieure
      touche une voie (fleche ou ligne d'arret).
      0 = pleine, 1 = exterieure a l'ouest/au nord, 2 = exterieure a l'est/au sud. */
  function varianteDePassage(g, tx, ty) {
    if (g === '=') {
      if (glyphe(tx + 1, ty) === '=' && fleche(tx - 1, ty) !== '+') return 1;
      if (glyphe(tx - 1, ty) === '=' && fleche(tx + 1, ty) !== '+') return 2;
      return 0;
    }
    if (g === ':') {
      if (glyphe(tx, ty + 1) === ':' && fleche(tx, ty - 1) !== '+') return 1;
      if (glyphe(tx, ty - 1) === ':' && fleche(tx, ty + 1) !== '+') return 2;
      return 0;
    }
    return hash2(tx, ty) % 4;
  }

  //: Ou pointe le nez de l'auto, pour chaque glyphe de case, et le pas qui va
  //: vers le FOND de la case.
  const CASES = { '^': [0, -1], 'v': [0, 1], '<': [-1, 0], '>': [1, 0] };

  //: ⚠️ Huit usures d'asphalte, pas quatre. Une fissure est un dessin, pas du
  //: bruit : avec quatre variantes on la reconnait d'une tuile a l'autre, et
  //: le stationnement se met a montrer sa grille en diagonale.
  const USURES = 8;

  /** La variante d'une case de stationnement, lue dans ses voisines :
      bit 0 = tuile du FOND (celle qui porte le butoir),
      bit 1 = derniere case de la rangee (elle ferme son cote),
      bits 2 et au-dela = l'usure (huit), stable par position.

      ⚠️ C'est le VOISINAGE qui decide, jamais le generateur : une rangee de
      cases est une bande d'un seul glyphe, et c'est ce qui permet d'en peindre
      une de trois tuiles de creux le jour ou on en voudra une. */
  function varianteDeCase(g, tx, ty) {
    const pas = CASES[g];
    if (!pas) return 0;
    const fond = glyphe(tx + pas[0], ty + pas[1]) !== g ? 1 : 0;
    // Le cote « suivant » d'une rangee : l'est pour les cases debout, le sud
    // pour les couchees. La derniere case ferme la rangee de ce cote-la.
    const cx = pas[0] === 0 ? 1 : 0, cy = pas[0] === 0 ? 0 : 1;
    const derniere = glyphe(tx + cx, ty + cy) !== g ? 2 : 0;
    return fond + derniere + (hash2(tx, ty) % USURES) * 4;
  }

  //: Les quatre cotes, dans l'ordre des sens d'une rampe : 0 est, 1 sud,
  //: 2 ouest, 3 nord.
  const COTES = [[1, 0], [0, 1], [-1, 0], [0, -1]];

  /** La variante d'une rampe : deux tuiles, un PIED (« R ») et une LEVRE
      (« J »). Le peintre doit savoir dans quel sens ca grimpe et laquelle des
      deux moities il peint — il le lit dans la voisine : le pied cherche sa
      levre, la levre cherche son pied. Rend sens * 2 + levre, le sens allant
      TOUJOURS du pied vers la levre.

      ⚠️ Meme regle que les cases : c'est le VOISINAGE qui decide, jamais le
      generateur. Une rampe se deplace d'une tuile sans que le dessin bouge. */
  function varianteDeRampe(g, tx, ty) {
    const partenaire = g === 'R' ? 'J' : 'R';
    for (let i = 0; i < 4; i++) {
      if (glyphe(tx + COTES[i][0], ty + COTES[i][1]) !== partenaire) continue;
      return ((g === 'R' ? i : (i + 2) % 4) * 2) + (g === 'J' ? 1 : 0);
    }
    return g === 'J' ? 1 : 0;             // une moitie orpheline : vers l'est
  }

  //: Combien de grains differents pour un meme toit. ⚠️ La tuile est cuite par
  //: (glyphe, variante) : sans un grain DANS la variante, toutes les tuiles d'un
  //: toit etaient rigoureusement identiques — c'est une moitie de ce qui faisait
  //: « une texture, pas un toit ».
  //: ⚠️ HUIT, pas quatre. Quatre suffisaient a casser l'uniformite d'un toit
  //: de commerce ; un entrepot de La Shop, lui, en couvre trois cents tuiles
  //: d'un seul tenant, et quatre grains sur trois cents font un papier peint
  //: qu'on lit d'un bout a l'autre du quartier. Les quatre grains de plus
  //: portent l'USURE (`toitPlat`) : une membrane rapiecee, une flaque, une
  //: coulee de rouille sous un event.
  const GRAINS_DE_TOIT = 8;

  /** La variante d'un toit plat : les quatre bits des cotes ou il S'ARRETE
      (1 nord, 2 est, 4 sud, 8 ouest), et le grain par-dessus.

      ⚠️ « S'arrete » veut dire : la voisine n'est pas le MEME toit. Deux
      batiments mitoyens portent donc un bord chacun — c'est ce qui les separe a
      l'oeil, et c'est pour ca que le generateur refuse de couvrir deux voisins
      de la meme matiere. */
  function varianteDeToit(g, tx, ty) {
    const bord = (glyphe(tx, ty - 1) !== g ? 1 : 0) | (glyphe(tx + 1, ty) !== g ? 2 : 0)
      | (glyphe(tx, ty + 1) !== g ? 4 : 0) | (glyphe(tx - 1, ty) !== g ? 8 : 0);
    return bord + 16 * (hash2(tx, ty) % GRAINS_DE_TOIT);
  }

  /** La variante d'un toit a deux versants : le bord, et le VERSANT — 0 nord,
      1 la ligne de faite, 2 sud.

      ⚠️ Le versant se COMPTE dans les voisines : combien de tuiles du meme toit
      au nord, combien au sud. C'est ce qui fait apparaitre la faite toute seule
      la ou les deux pentes se rencontrent, sans qu'une tuile ait besoin de
      savoir qu'elle est au milieu — et sans une seule donnee de plus dans le
      paquet. La course est bornee : un toit plus haut que ca n'existe pas. */
  function varianteDePente(g, tx, ty) {
    const bord = (glyphe(tx, ty - 1) !== g ? 1 : 0) | (glyphe(tx + 1, ty) !== g ? 2 : 0)
      | (glyphe(tx, ty + 1) !== g ? 4 : 0) | (glyphe(tx - 1, ty) !== g ? 8 : 0);
    let nord = 0, sud = 0;
    while (nord < 12 && glyphe(tx, ty - 1 - nord) === g) nord++;
    while (sud < 12 && glyphe(tx, ty + 1 + sud) === g) sud++;
    const versant = nord === sud ? 1 : (nord < sud ? 0 : 2);
    return bord + 16 * versant;
  }

  /** Un toit a cette tuile ? (les quatre couvertures) */
  function estToit(tx, ty) {
    const p = carte.legende[glyphe(tx, ty)];
    return !!(p && p.toit);
  }

  /** Une cloture a cette tuile ? (grillage, palissade ou barbele) */
  function estCloture(tx, ty) { const s = solidite(tx, ty); return s === 4 || s === 5; }

  /** La variante d'une cloture : le masque des cotes ou elle CONTINUE — 1 nord,
      2 est, 4 sud, 8 ouest.

      ⚠️ C'est ce qui lui donne son sens. Les trois peintres ne savaient dessiner
      qu'est-ouest, alors une cloture nord-sud etait une pile de panneaux vus de
      face (« les clotures qui sont nord-sud ne sont pas dans le bon sens »). Et
      le remede etait deja ecrit trois fois dans le fichier : passages pietons,
      cases de stationnement et rampes lisent deja leurs voisines.

      ⚠️ Les trois clotures se continuent l'une l'autre : un grillage qui se
      poursuit en barbele est une seule ligne, et elle doit se dessiner comme
      telle — c'est la geometrie qui compte ici, pas la matiere. */
  function varianteDeCloture(tx, ty) {
    return (estCloture(tx, ty - 1) ? 1 : 0) | (estCloture(tx + 1, ty) ? 2 : 0)
      | (estCloture(tx, ty + 1) ? 4 : 0) | (estCloture(tx - 1, ty) ? 8 : 0);
  }

  /** La variante d'un meuble en BLOC (lit, table, tapis, machine — la fiche dit
      `bloc`) : le masque des cotes ou le MEME glyphe continue — 1 nord, 2 est,
      4 sud, 8 ouest, la meme lecture que la cloture — et un grain par-dessus
      (bits 4 et 5), stable par position.

      ⚠️ Un lit fait deux tuiles sur deux, un billard quatre sur deux, un tapis
      trois sur trois, et leurs peintres ne savaient pas qu'ils avaient des
      voisines : chaque tuile dessinait son oreiller, son plateau, son galon,
      ses boulons. Un lit etait quatre lits d'une place colles (« 2 ou 4 cases
      avec chacune leur oreiller »), un billard huit tabourets, un tapis trois
      chemins de couloir. Avec le masque, ce qui marque un BOUT (tete de lit,
      chant du plateau, galon, boulon, ombre) ne va qu'aux tuiles ou le bloc
      s'arrete, et le reste court d'une tuile a l'autre. Le corollaire, garde
      par un juge des plans : deux blocs du meme glyphe ne se touchent jamais —
      colles, ils seraient peints comme un seul. */
  function varianteDeBloc(g, tx, ty) {
    return (glyphe(tx, ty - 1) === g ? 1 : 0) | (glyphe(tx + 1, ty) === g ? 2 : 0)
      | (glyphe(tx, ty + 1) === g ? 4 : 0) | (glyphe(tx - 1, ty) === g ? 8 : 0)
      | 16 * (hash2(tx, ty) % 4);
  }

  //: Combien d'usures differentes pour un SOL D'ILOT. ⚠️ SEIZE, et c'est la
  //: meme lecon que l'asphalte du stationnement deux ecrans plus haut : « une
  //: fissure est un dessin, pas du bruit ; avec quatre variantes on la
  //: reconnait d'une tuile a l'autre ». Sauf qu'ici ca porte bien plus loin :
  //: le trottoir, l'herbe et la ruelle font 43 % de la ville a eux trois
  //: (28 %, 10,5 %, 4,7 %) et ils se peignaient avec QUATRE tuiles de seize
  //: pixels, repetees d'un bout a l'autre du Faubourg. De loin, ce n'etait pas
  //: un sol, c'etait du papier peint.
  const USURES_DE_SOL = 16;

  //: Les sols qui font le dedans d'un pate de maisons — plus le sable de la
  //: greve, qui s'aplatissait de la meme facon et pour la meme raison.
  const SOLS_D_ILOT = { '.': true, ',': true, 'x': true, 'g': true, 's': true };

  /** La variante d'un sol d'ilot : son usure, et — pour le trottoir — la place
      de la tuile dans sa DALLE.

      ⚠️ Le trottoir peignait son joint sur CHAQUE tuile, en haut et a gauche :
      un trait tous les seize pixels dans les deux sens, sur le quart de la
      ville. Ce qu'on lisait alors, c'etait la grille de la carte. Une dalle de
      beton fait deux tuiles de cote ; chaque tuile lit sa parite pour savoir de
      quel coin de dalle elle est, et ne peint que les joints qui la regardent —
      la meme regle que la case de stationnement, qui ne peint que sa ligne de
      gauche pour ne pas doubler celle de sa voisine. */
  function varianteDeSol(g, tx, ty) {
    const usure = hash2(tx, ty) % USURES_DE_SOL;
    if (g !== '.') return usure;
    return (tx & 1) | ((ty & 1) << 1) | (usure << 2);
  }

  /** La variante d'une tuile : ce que son peintre a besoin de savoir de ses
      voisines. Passage pieton, case de stationnement, rampe et cloture en ont
      une ; les autres se contentent d'un bruit stable. */
  function varianteDeTuile(g, tx, ty) {
    if (CASES[g]) return varianteDeCase(g, tx, ty);
    if (g === 'p') return hash2(tx, ty) % USURES;
    if (SOLS_D_ILOT[g]) return varianteDeSol(g, tx, ty);
    if (g === 'R' || g === 'J') return varianteDeRampe(g, tx, ty);
    const p = carte.legende[g];
    if (p && p.bloc) return varianteDeBloc(g, tx, ty);
    if (p && p.cloture) return varianteDeCloture(tx, ty);
    if (p && p.pente) return varianteDePente(g, tx, ty);
    if (p && p.toit) return varianteDeToit(g, tx, ty);
    return varianteDePassage(g, tx, ty);
  }

  /** Range des poses par morceau. ⚠️ Une pose qui deborde est rangee dans TOUS
      les morceaux qu'elle touche : chacun en peindra la part qui le regarde, et
      une enseigne a cheval sur deux morceaux n'est pas coupee en deux. */
  function indexerParMorceau(poses, boite) {
    const index = new Map();
    poses.forEach(function (pose) {
      const b = boite(pose);
      const x0 = b[0] || pose.x, y0 = b[1] || pose.y;
      const m0x = Math.floor(x0 / MORCEAU), m0y = Math.floor(y0 / MORCEAU);
      const m1x = Math.floor((x0 + b[2] - 1) / MORCEAU), m1y = Math.floor((y0 + b[3] - 1) / MORCEAU);
      for (let my = m0y; my <= m1y; my++) {
        for (let mx = m0x; mx <= m1x; mx++) {
          const cle = mx + ',' + my;
          const liste = index.get(cle);
          if (liste) liste.push(pose); else index.set(cle, [pose]);
        }
      }
    });
    return index;
  }

  function genresDevanture() {
    return (B.defs && B.defs.devantures && B.defs.devantures.genres) || [];
  }

  function mursDeResidence() {
    return (B.defs && B.defs.devantures && B.defs.devantures.murs) || [];
  }

  function ferDesEscaliers() {
    return (B.defs && B.defs.devantures && B.defs.devantures.fer)
      || { barreau: '#3d4348', marche: '#8a8f94', arete: '#adb2b6', ombre: 'rgba(0,0,0,0.35)' };
  }

  function couleursTag() {
    return (B.defs && B.defs.devantures && B.defs.devantures.couleurs_tag) || ['#d34f3a'];
  }

  function peindreMorceau(mx, my) {
    const c = Base.nouveauCanvas(MORCEAU_PX, MORCEAU_PX);
    const ctx = c.getContext('2d');
    for (let j = 0; j < MORCEAU; j++) {
      for (let i = 0; i < MORCEAU; i++) {
        const tx = mx * MORCEAU + i, ty = my * MORCEAU + j;
        if (tx >= carte.w || ty >= carte.h) continue;
        const g = carte.sol[ty][tx];
        // ⚠️ Le plancher d'abord, sous les meubles : une chaise, une table ou
        // une plante ne remplit pas sa tuile, et ce qui reste serait du VIDE —
        // c'est-a-dire du noir. (Vu en plein visage : chaque table du bar avait
        // un cadre noir, et la plante etait posee dans un trou.)
        if (carte.plancher && (carte.legende[g] || {}).meuble) {
          const fond = TUILES[carte.plancher] || TUILES[','];
          ctx.drawImage(Atlas.cuireTuile(carte.plancher, varianteDeTuile(carte.plancher, tx, ty), fond), i * TT, j * TT);
        }
        const peintre = TUILES[g] || TUILES[','];
        const tuile = Atlas.cuireTuile(g, varianteDeTuile(g, tx, ty), peintre);
        ctx.drawImage(tuile, i * TT, j * TT);
      }
    }
    peindreDevantures(ctx, mx, my);
    return c;
  }

  /** Les enseignes, les logements et les tags, par-dessus les tuiles du morceau. */
  function peindreDevantures(ctx, mx, my) {
    const cle = mx + ',' + my;
    const ox = mx * MORCEAU, oy = my * MORCEAU;
    // Les fosses d'arbre AVANT tout : c'est du sol. L'ombre d'un mur tombe
    // dessus comme sur le reste du trottoir, elle ne passe pas dessous.
    const fosses = carte.fosses && carte.fosses.get(cle);
    if (fosses) {
      fosses.forEach(function (f) {
        FACADES.fosseDArbre(ctx, (f.x - ox) * TT + 8, (f.y - oy) * TT + 15);
      });
    }

    // ⚠️ L'ombre des murs ENSUITE : elle se peint SOUS les enseignes (une ombre
    // par-dessus une pancarte donnerait une pancarte sale) et sous tout le
    // reste. Un batiment ne projetait rien, et une ville sans ombre est plate.
    // ⚠️ On commence a j = -1, une rangee AU-DESSUS du morceau : l'ombre d'un mur
    // tombe sur la tuile du dessous, et celle d'un mur assis sur la derniere
    // rangee du morceau voisin appartient a CELUI-CI. Sans ca, une bande de
    // trottoir sur seize n'avait pas d'ombre — et c'est la couture qui se voit.
    for (let j = -1; j < MORCEAU; j++) {
      for (let i = 0; i < MORCEAU; i++) {
        const tx = ox + i, ty = oy + j;
        if (solidite(tx, ty) !== 1 || estToit(tx, ty)) continue;      // un MUR, pas un toit
        if (solidite(tx, ty + 1) === 1) continue;                      // il n'y a pas de rue dessous
        FACADES.ombreDeMur(ctx, i * TT, (j + 1) * TT);
      }
    }
    const genres = genresDevanture();
    const devantures = carte.devantures && carte.devantures.get(cle);
    if (devantures && genres.length) {
      devantures.forEach(function (d) {
        const g = genres[d.genre] || genres[0];
        FACADES.devanture(ctx, d, g, (d.x - ox) * TT, (d.y - oy) * TT);
      });
    }
    const residences = carte.residences && carte.residences.get(cle);
    const murs = mursDeResidence();
    if (residences && murs.length) {
      const fer = ferDesEscaliers();
      residences.forEach(function (r) {
        FACADES.residence(ctx, r, murs[r.mur % murs.length], fer, (r.x - ox) * TT, (r.y - oy) * TT);
      });
    }
    const toits = carte.toits && carte.toits.get(cle);
    if (toits) {
      toits.forEach(function (t) { FACADES.toiture(ctx, t, (t.x - ox) * TT, (t.y - oy) * TT); });
    }
    const tags = carte.graffitis && carte.graffitis.get(cle);
    if (tags) {
      const couleurs = couleursTag();
      tags.forEach(function (gr) {
        FACADES.graffiti(ctx, gr, couleurs[gr.couleur % couleurs.length],
                         (gr.x - ox) * TT, (gr.y - oy) * TT);
      });
    }
  }

  function dessinerSol(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    const m0x = Math.floor(cx / MORCEAU_PX), m0y = Math.floor(cy / MORCEAU_PX);
    const m1x = Math.floor((cx + VW - 1) / MORCEAU_PX), m1y = Math.floor((cy + VH - 1) / MORCEAU_PX);
    carte.visibles.clear();
    for (let my = m0y; my <= m1y; my++) {
      for (let mx = m0x; mx <= m1x; mx++) {
        if (mx < 0 || my < 0 || mx * MORCEAU >= carte.w || my * MORCEAU >= carte.h) continue;
        const cle = mx + ',' + my;
        let m = carte.morceaux.get(cle);
        if (m) carte.morceaux.delete(cle);          // re-insere = le plus frais
        else m = peindreMorceau(mx, my);
        carte.morceaux.set(cle, m);
        carte.visibles.add(cle);
        ctx.drawImage(m, mx * MORCEAU_PX - cx, my * MORCEAU_PX - cy);
        B.stats.images++;
      }
    }
    oublierLesVieuxMorceaux();
    B.stats.morceaux = carte.morceaux.size;
  }

  /** Jette les morceaux les plus anciens, jamais un morceau a l'ecran. */
  function oublierLesVieuxMorceaux() {
    if (carte.morceaux.size <= MORCEAUX_MAX) return;
    for (const cle of carte.morceaux.keys()) {
      if (carte.morceaux.size <= MORCEAUX_MAX) break;
      if (!carte.visibles.has(cle)) carte.morceaux.delete(cle);
    }
  }

  // --- Mini-carte -----------------------------------------------------------------

  /** Une couleur par FAMILLE de tuile, lue dans la legende : un glyphe ajoute
      demain apparait tout seul sur la mini-carte. */
  function couleurMini(glyphe) {
    const p = carte.legende[glyphe] || {};
    if (p.solide === 2) return '#24506f';
    if (p.solide === 1) return '#4a3f3f';
    // Une cloture se voit sur la carte : elle dit qu'une cour est fermee. Le
    // barbele tire vers le rouge — c'est le seul qu'on ne passe pas.
    if (p.cloture) return p.cloture === 'barbele' ? '#8a5b5b' : '#7d7a6a';
    if (p.route) return '#34373d';
    if (p.trottoir) return '#8a877c';
    if (p.abord) return '#6d665a';
    if (p.herbe) return '#3f6b33';
    if (p.ruelle) return '#4a4741';
    return '#6b5a3a';
  }

  /** La ville entiere, une tuile = un pixel. Cuite une fois : 18 000 rectangles
      au chargement valent mieux que 64x48 relus a chaque image. */
  function miniCarte(laquelle) {
    const k = laquelle || carte;                  // la ville, meme quand on est dedans
    if (k.mini) return k.mini;
    const c = Base.nouveauCanvas(k.w, k.h);
    const ctx = c.getContext('2d');
    for (let y = 0; y < k.h; y++) {
      const ligne = k.sol[y];
      let debut = 0, couleur = couleurMini(ligne[0]);
      for (let x = 1; x <= k.w; x++) {
        const suivante = x < k.w ? couleurMini(ligne[x]) : null;
        if (suivante !== couleur) {
          ctx.fillStyle = couleur;
          ctx.fillRect(debut, y, x - debut, 1);
          debut = x; couleur = suivante;
        }
      }
    }
    k.mini = c;
    return c;
  }

  // --- Camera ---------------------------------------------------------------------

  /** Une carte plus petite que l'ecran (une piece) se centre : la camera
      prend alors une valeur negative, et le sol se dessine au milieu. */
  function cibleCamera(x, y) {
    return {
      x: carte.pxW < VW ? (carte.pxW - VW) / 2 : borner(x - VW / 2, 0, carte.pxW - VW),
      y: carte.pxH < VH ? (carte.pxH - VH) / 2 : borner(y - VH / 2, 0, carte.pxH - VH),
    };
  }

  function centrerCamera(x, y) {
    const c = cibleCamera(x, y);
    B.cam.x = c.x; B.cam.y = c.y;
  }

  function majCamera() {
    const j = B.joueur;
    if (!j) return;
    let avanceX = 0, avanceY = 0;
    if (j.dansVehicule) {
      const v = j.dansVehicule, f = Math.min(1, Math.abs(v.vitesse || 0) / 4);
      avanceX = Math.cos(v.angle) * 48 * f; avanceY = Math.sin(v.angle) * 48 * f;
    } else { avanceX = j.vx * 14; avanceY = j.vy * 14; }
    const cible = cibleCamera(j.x + avanceX, j.y + avanceY);
    B.cam.x += (cible.x - B.cam.x) * 0.12;
    B.cam.y += (cible.y - B.cam.y) * 0.12;
    if (B.cam.secousse > 0) B.cam.secousse *= 0.9;
  }

  // --- Heure et ambiance ---------------------------------------------------------------

  //: [heure 0..1, teinte, alpha]. 0 = minuit, 0.5 = midi.
  const TEINTES = [
    [0.00, [26, 32, 80], 0.72], [0.22, [26, 32, 80], 0.66], [0.30, [255, 150, 90], 0.22],
    [0.38, [255, 255, 255], 0.0], [0.72, [255, 255, 255], 0.0], [0.80, [255, 130, 70], 0.28],
    [0.88, [40, 40, 100], 0.62], [1.00, [26, 32, 80], 0.72],
  ];

  function majHeure() {
    const p = B.partie;
    if (!p || !B.defs) return;
    const parImage = 1 / (B.defs.economie.jour_secondes * 60);
    p.heure += parImage;
    if (p.heure >= 1) { p.heure -= 1; p.jour += 1; if (typeof Missions !== 'undefined' && Missions.nouveauJour) Missions.nouveauJour(); }
  }

  function ambiance(heure) {
    if (carte && carte.interieur && heure === undefined) return { teinte: 'rgb(255,255,255)', alpha: 0 };
    const h = heure === undefined ? (B.partie ? B.partie.heure : 0.5) : heure;
    let a = TEINTES[0], b = TEINTES[TEINTES.length - 1];
    for (let i = 0; i < TEINTES.length - 1; i++) {
      if (h >= TEINTES[i][0] && h <= TEINTES[i + 1][0]) { a = TEINTES[i]; b = TEINTES[i + 1]; break; }
    }
    const t = b[0] === a[0] ? 0 : (h - a[0]) / (b[0] - a[0]);
    const r = Math.round(lerp(a[1][0], b[1][0], t)), g = Math.round(lerp(a[1][1], b[1][1], t)), bl = Math.round(lerp(a[1][2], b[1][2], t));
    return { teinte: 'rgb(' + r + ',' + g + ',' + bl + ')', alpha: lerp(a[2], b[2], t) };
  }

  function estNuit() { return ambiance().alpha > 0.4; }

  /** Le facteur de foule d'un quartier a cette heure-ci : (nuit, matin, soir).

      ⚠️ C'est ce qui empeche les cinq districts d'etre le meme district a cinq
      endroits. La Shop se vide a la noirceur (0,15), les Quais grouillent au
      matin (1,4), la banlieue dort. Le jour reste la reference : 1. */
  function rythme(zone) {
    const r = zone && zone.rythme;
    if (!r) return 1;
    const h = B.partie ? B.partie.heure : 0.5;
    if (h >= 0.82 || h < 0.25) return r[0];
    if (h < 0.42) return r[1];
    if (h < 0.70) return 1;
    return r[2];
  }

  function heureTexte() {
    const h = B.partie ? B.partie.heure : 0.5;
    const minutes = Math.floor(h * 24 * 60);
    const hh = Math.floor(minutes / 60), mm = minutes % 60;
    return (hh < 10 ? '0' : '') + hh + ':' + (mm < 10 ? '0' : '') + mm;
  }

  function lampesVisibles(cam) {
    // Les lampadaires n'eclairent qu'a la brune : en plein jour, rien.
    if (!carte || ambiance().alpha < 0.2) return [];
    const out = [];
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const l of carte.lampes) {
      if (l.eteinte) continue;             // son poteau est a terre
      if (l.x < cx - l.r || l.x > cx + VW + l.r || l.y < cy - l.r || l.y > cy + VH + l.r) continue;
      out.push({ x: l.x - cx, y: l.y - cy, r: l.r, c: l.c });
      if (out.length >= 25) break;
    }
    return out;
  }

  return {
    MUR, EAU, BASSE, GRILLAGE, BARBELE, MASQUE_PIETON, MASQUE_NAGEUR, MASQUE_VEHICULE,
    MASQUE_A_PIED, MORCEAUX_MAX, estEau,
    charger, entrer, changerPiece, restaurer, glyphe, solidite, bloque, defoncer, estEnjambable,
    ouvrirPorte, battant, majBattants, dessinerBattants, BATTANT_OUVRE, estCloture, estToit, varianteDeCloture, varianteDeBloc, varianteDeToit, varianteDePente, estRoute, estPassage, estChaussee, estAbord, estTrottoir, marchablePieton, estMeuble,
    ligneLibre, porteA, porteDevant, zoneA, fleche, sensArret, intersectionA, feuDeCirculation, feuVert, feuPieton, estRampe, varianteDeTuile, varianteDeSol, varianteDePassage, varianteDeCase, varianteDeRampe, USURES_DE_SOL,
    dessinerSol, centrerCamera, majCamera, majHeure, ambiance, estNuit, rythme, heureTexte, lampesVisibles,
    miniCarte, couleurMini, chemin, demanderChemin, majChemins,
    get carte() { return carte; }, get cheminsEnAttente() { return fileChemins.length; },
  };
})();
