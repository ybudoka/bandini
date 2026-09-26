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
    // ⚠️ LA FOIRE LA NUIT. Une guirlande a chaque kiosque, en trois couleurs qui
    // alternent — une foire eteinte a 21 h 50, c'etait la capture de Martin.
    foire_jaune: { dy: 0, c: 'rgba(255,214,110,0.62)' },
    foire_rose: { dy: 0, c: 'rgba(255,120,190,0.52)' },
    foire_bleue: { dy: 0, c: 'rgba(120,190,255,0.50)' },
    // ⚠️ LES BALISES DE LA PISTE : une petite lueur froide, au ras du sol. La nuit,
    // c'est tout ce qu'on voit de l'aeroport depuis La Pointe — deux pointilles.
    balise: { dy: 8, c: 'rgba(200,225,255,0.55)' },
  };

  let carte = null;

  //: Les nids-de-poule, indexes une fois : « x,y » -> vrai. Les lire dans un
  //: tableau a chaque image pour chaque char, c'est quatre-vingt-dix
  //: comparaisons par char et par image, pour une tuile.
  //: ⚠️ L'index vit SUR LA CARTE (`carte.nids`), pas dans le module. Une piece
  //: passe par `charger`, qui le remplacait par le sien (vide), et `restaurer` ne
  //: rend que la carte : jusqu'au 17 sept. 2026, entrer dans n'importe quel
  //: batiment effacait tous les nids de la ville jusqu'au rechargement.
  function nidDePoule(tx, ty) { return !!(carte && carte.nids && carte.nids.has(tx + ',' + ty)); }

  //: LE NID-DE-POULE SE VOIT (26 sept. 2026). La carte en posait et le char les sentait — et la chaussee
  //: restait lisse a l'ecran : on les subissait sans jamais les voir venir. Trois trous, tires a
  //: l'EMPREINTE de la tuile : un bord casse plus clair, le fond sombre, une fissure qui part.
  const NIDS = [
    ['....hhhh....', '..hhooooh...', '.hooooooohh.', 'hoooooooooh.', '.hooooooohh.', '..hhhooohc..', '.....hh..c..', '..........c.'],
    ['...hhh......', '.hhoooh.....', 'hoooooohh...', 'hoooooooohh.', '.hhooooooooh', '...hhooooohh', '.c...hhhhh..', 'c...........'],
    ['.....hhh....', '..hhhoooh...', '.hoooooooh..', '.hoooooooh..', 'c.hooooohh..', '.c.hhhhh....', '..c.........', '............'],
  ];
  const TONS_DU_NID = { h: '#6b6d74', o: '#1b1c21', c: '#2b2c31' };

  function peindreNid(v) {
    return function (ctx) {
      const m = NIDS[v];
      for (let y = 0; y < m.length; y++) {
        for (let x = 0; x < m[y].length; x++) {
          const t = TONS_DU_NID[m[y][x]];
          if (!t) continue;
          ctx.fillStyle = t; ctx.fillRect(x + 2, y + 4, 1, 1);
        }
      }
      ctx.fillStyle = 'rgba(120,150,190,0.35)'; ctx.fillRect(5, 7, 3, 1);   // un reste d'eau qui brille
    };
  }

  /** Les nids de la carte a l'ecran, par-dessus la chaussee (sous les rails, les chars et les gens). */
  function dessinerNids(ctx, cam) {
    if (!carte || !carte.nids || !carte.nids.size) return;
    let n = 0;
    for (const cle of carte.nids) {
      const i = cle.indexOf(','), tx = +cle.slice(0, i), ty = +cle.slice(i + 1);
      const x = tx * TT - cam.x, y = ty * TT - cam.y;
      if (x < -TT || y < -TT || x > VW || y > VH) continue;
      const v = hash2(tx, ty) % NIDS.length;
      ctx.drawImage(Atlas.cuirePeintre('nid|' + v, TT, TT, peindreNid(v)), Math.round(x), Math.round(y));
      n++;
    }
    B.stats.images = (B.stats.images || 0) + n;
  }

  //: Les PLAQUES D'ACIER des tranchées de chantier (`chantiers.js` les pose et les
  //: retire avec la phase du jour) : même règle que les nids, l'index vit SUR LA
  //: CARTE, et « x,y » -> vrai.
  function plaqueDAcier(tx, ty) { return !!(carte && carte.plaques && carte.plaques.has(tx + ',' + ty)); }

  //: Le STANDING d'une tuile (des quartiers qu'on reconnait) : 'cossu',
  //: 'ordinaire', 'pauvre', ou null sur l'eau et dans une piece. ⚠️ Python l'a
  //: DECIDE (`carte.STANDING`, une lettre par bloc) ; ici on le lit, avec la meme
  //: coupe au milieu de chaque rue (`_Chantier.standing_en`), et un juge tient
  //: que les deux disent la meme chose tuile pour tuile.
  //: ⚠️ Il vit sur la CARTE, pas dans le module : une piece recharge le module
  //: (`entrer` passe par `charger`) et `restaurer` ne rend que la carte.
  const STANDINGS = { '+': 'cossu', '=': 'ordinaire', '-': 'pauvre' };
  function coupes(blocs, rues) {
    const sortie = [0];
    let x = 0;
    for (let i = 0; i < blocs.length; i++) {
      if (i > 0) sortie.push(x + Math.floor(rues[i] / 2));
      x += rues[i] + blocs[i];
    }
    return sortie;
  }
  function somme(nombres) { return nombres.reduce(function (s, n) { return s + n; }, 0); }
  function rang(bornes, v) {
    let i = 0;
    while (i + 1 < bornes.length && bornes[i + 1] <= v) i++;
    return i;
  }
  /** La lettre de ce bloc dans une grille du paquet (`standing`, `usage`). */
  function lettreDuBloc(nom, tx, ty, laquelle) {
    const k = laquelle || carte;
    const q = k && k.quartiers;
    // ⚠️ HORS DE LA TRAME, PAS DE QUARTIER : la carte a grandi sous elle (l'aeroport),
    // et `rang` rendait la derniere rangee de blocs a tout ce qui est plus bas — la
    // mer au sud des Quais etait « pauvre ». Python rend None au meme endroit.
    if (!q || !q[nom] || tx < 0 || ty < 0 || tx >= Math.min(k.w, q.w) || ty >= Math.min(k.h, q.h)) return null;
    return q[nom][rang(q.y, ty)][rang(q.x, tx)];
  }
  function standingA(tx, ty, laquelle) {
    return STANDINGS[lettreDuBloc('standing', tx, ty, laquelle)] || null;
  }

  //: L'USAGE d'une tuile (2e vague) : 'commercial', 'residentiel', 'industriel',
  //: 'parc', 'port', 'eau', ou null dans une piece. Meme grille, meme coupe ; la
  //: lettre se traduit par la table du paquet (`carte.zonage`), jamais ici.
  function usageA(tx, ty, laquelle) {
    const k = laquelle || carte;
    const lettre = lettreDuBloc('usage', tx, ty, k);
    return (lettre && k.quartiers.usages[lettre]) || null;
  }

  //: Ce que le PEINTRE du sol doit savoir du quartier, en quatre bits : l'usage
  //: (1 commercial, 2 residentiel, 3 industriel, 0 le reste) et le standing
  //: (1 cossu, 2 pauvre, 0 ordinaire). ⚠️ Une couche PEINTE : le glyphe ne change
  //: pas, la solidite non plus — seule la tuile cuite qu'on colle dessus.
  const CODE_D_USAGE = { commercial: 1, residentiel: 2, industriel: 3 };
  const CODE_DE_STANDING = { cossu: 1, pauvre: 2 };
  function codeDeQuartier(tx, ty) {
    return (CODE_D_USAGE[usageA(tx, ty)] || 0) | ((CODE_DE_STANDING[standingA(tx, ty)] || 0) << 2);
  }

  //: Le coeur de la ville — la zone vers laquelle le trafic du matin converge
  //: (`trafic.pointe.vers`). Cherche une fois : les zones ne bougent pas.
  //: ⚠️ Toujours celui de la VILLE, et garde sur elle : demande depuis une
  //: piece, il se cherchait dans la piece (aucune zone) et y restait.
  function coeurDeLaVille() {
    const ville = carte.ville || carte;
    if (ville.coeur) return ville.coeur;
    const slug = B.defs.conduite.trafic.pointe.vers;
    const z = (ville.zones || []).find(function (q) { return q.slug === slug; });
    ville.coeur = z ? { x: (z.x + z.l / 2) * TT, y: (z.y + z.h / 2) * TT } : { x: ville.pxW / 2, y: ville.pxH / 2 };
    return ville.coeur;
  }

  //: **LE DEVANT D'UNE PORTE** : trois tuiles dans l'axe, une de chaque cote — la
  //: fenetre que la ville tient libre (`app/devants.py`) et que ce qu'une mission
  //: pose (un donneur, des hommes de main, un panneau) ne prend pas non plus.
  //: ⚠️ La fenetre vient du PAQUET (`def.devant`), elle ne s'ecrit pas ici : deux
  //: chiffres qui divergent, et la ville degage une zone que le jeu remplit.
  //: Une piece n'en a pas (`def.devant` absent) : un ensemble vide.
  function devantsDePortes(def, portesVues) {
    const devants = new Set();
    const fen = def.devant;
    if (!fen) return devants;
    (def.devantures || []).concat(def.residences || []).forEach(function (f) {
      for (let i = 0; i < f.motifs.length; i++) if (f.motifs[i] === 'P') portesVues.push({ x: f.x + i, y: f.y });
    });
    for (const p of portesVues) {
      for (let dy = 1; dy <= fen.profondeur; dy++) {
        for (let dx = -fen.cote; dx <= fen.cote; dx++) devants.add((p.x + dx) + ',' + (p.y + dy));
      }
    }
    return devants;
  }

  function charger(def) {
    const w = def.largeur, h = def.hauteur;
    const solide = new Uint8Array(w * h);
    const route = new Uint8Array(w * h);
    const passage = new Uint8Array(w * h);     // passage pieton : route ET trottoir
    const portesFermees = [];                   // les « d » : par ou les gens rentrent chez eux
    const portesVues = [];                      // toutes celles qu'on VOIT : D, d, G (et les peintes, plus bas)
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
        if (ligne[x] === 'd' || ligne[x] === 'D' || ligne[x] === 'G') portesVues.push({ x: x, y: y });
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
      devants: devantsDePortes(def, portesVues),
      morceaux: new Map(), visibles: new Set(),
      // Les battants qui s'ouvrent : hors du cache de morceaux (voir `ouvrirPorte`).
      battants: new Map(),
      // Les rideaux de garage : meme regle, et ils se souviennent de leur hauteur.
      // ⚠️ `baie` : les rangees de toit derriere le rideau, ou le char se cache
      // (Python la garantit, le navigateur ne la devine pas). `admis`, `dedans`,
      // `phase` : l'atelier (`Missions.majGarage`).
      portesGarage: (def.portes_garage || []).map(function (p) {
        return { x: p.x, y: p.y, l: p.l, lieu: p.lieu, baie: p.baie || 0, genre: p.genre || 'garage',
                 ouverture: 0, tient: 0, servi: null, admis: null, dedans: null, phase: null, t: 0, refuse: null };
      }),
      // La barriere coulissante du lot du poste : `cle`, le char pour qui elle s'ouvre.
      coulissantes: coulissantesDe(def),
      portesParTuile: portes, mini: null, croisements: croisements, arrets: def.arrets || {},
      nids: new Set((def.nids_de_poule || []).map(function (n) { return n.x + ',' + n.y; })), coeur: null,
      plaques: new Set(),
      quartiers: def.grille && def.grille.standing ? {
        standing: def.grille.standing, usage: def.grille.usage || null,
        usages: Object.keys(def.zonage || {}).reduce(function (m, slug) { m[def.zonage[slug].lettre] = slug; return m; }, {}),
        x: coupes(def.grille.colonnes, def.grille.rues_v), y: coupes(def.grille.rangees, def.grille.rues_h),
        w: somme(def.grille.colonnes) + somme(def.grille.rues_v), h: somme(def.grille.rangees) + somme(def.grille.rues_h),
      } : null,
      intersections: def.intersections || [],
      // ⚠️ Trois sortes de lumiere, et elles ne se ressemblent pas : le
      // LAMPADAIRE (haut, large, blanc-jaune), la VITRINE (basse et chaude,
      // un reflet sur le trottoir) et la FENETRE d'un logement (faible, dans
      // le mur — on doit deviner qu'il y a quelqu'un, pas lire son journal).
      lampes: (def.lampes || []).map(function (l) {
        const sorte = SORTES_DE_LAMPE[l.c] || SORTES_DE_LAMPE.poteau;
        // ⚠️ `panne` : un lampadaire de rue pauvre qui n'eclaire plus (3e vague).
        // `gresille` : un autre qui hoquette (la nuit a ses habitudes).
        const lampe = { x: l.x * TT + 8, y: l.y * TT + sorte.dy, r: l.r || 44, c: sorte.c, panne: !!l.panne,
                        gresille: !!l.gresille, tx: l.x, ty: l.y };
        if (l.c === 'fenetre') heuresDeLaFenetre(lampe);
        return lampe;
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
      // Les MATERIAUX d'une carte de bloc (`app/blocs/`) : un glyphe peint autrement que
      // dans la ville — les `F`, `W` et `D` du chalet du rang sont en BOIS ROND. Le glyphe
      // reste le meme (la porte s'ouvre et se franchit comme toutes les autres) ; seul le
      // peintre change (`TUILES['F@bois_rond']`).
      materiaux: def.materiaux || null,
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

  // --- Les zones conditionnelles : une porte, une condition, un prix ---------------------
  //: ⚠️ Tout vient de la fiche (`carte.BARRIERES`, dans le paquet). Seule la
  //: COURONNE du rectangle arrete, et seulement quand on vient de l'exterieur :
  //: qui est dedans quand elle se ferme en sort librement — c'est ce qui fait
  //: qu'une barriere bloque sans jamais enfermer.

  //: **L'ENTRAVE DU JOUR.** Python a calcule la liste des voies qu'on peut
  //: fermer sans couper la ville ; la graine du JOUR en tire une, et la ville
  //: change d'un jour a l'autre sans qu'on regenere une seule tuile.
  //:
  //: ⚠️ `hash2(jour, ...)`, jamais `B.rng()` : un decor qui change la ville ne
  //: consomme pas un de du jeu — c'est la lecon des pilotes de deux-roues.
  //: ⚠️ Et elle se garde pour la journee : `barrieres()` est relu a chaque
  //: deplacement de chaque char, et rebatir l'objet a chaque appel coute plus
  //: cher que tout le reste du mecanisme.
  let entraveJour = { jour: -1, b: null };
  function entraveDuJour() {
    const def = carte && carte.def;
    const voies = (def && def.entraves) || [];        // une voie fermee
    const rues = (def && def.fermetures) || [];       // la rue entiere barree
    const total = voies.length + rues.length;
    if (!total) return null;
    const jour = B.partie ? B.partie.jour : 0;
    if (entraveJour.jour !== jour) {
      // ⚠️ `ecartee` : Python a marque celles qui tombent devant une porte
      // (`app/devants.py`). On tire dans la liste ENTIERE — une entree de moins
      // rebattrait tous les jours —, puis on passe a la suivante tant que celle-ci
      // est ecartee. Le jour dont le tirage ne tombait pas sur elles ne change pas.
      const tous = voies.concat(rues);
      // ⚠️ UNE SEULE PAR JOUR, et c'est ce qui evite d'avoir a juger les
      // COMBINAISONS : deux fermetures prises separement dans une liste valide
      // peuvent, ensemble, isoler un bloc. Une seule, et la question ne se pose
      // pas.
      let i = hash2(jour, 9173) % total;
      for (let k = 0; k < total && tous[i].ecartee; k++) i = (i + 1) % total;
      if (tous[i].ecartee) { entraveJour = { jour: jour, b: null }; return null; }   // toutes ecartees
      const rue = i >= voies.length;
      const c = tous[i];
      const f = (rue ? def.fermeture : def.entrave) || {};
      entraveJour = { jour: jour, b: {
        slug: rue ? 'rue_barree' : 'entrave',
        nom: rue ? 'Une rue barrée' : 'Un chantier',
        x: c.x, y: c.y, l: c.l, h: c.h, sens: c.sens || null,
        arrete: ['vehicule'], condition: { toujours: true },
        forcer: { degats: f.degats || 8 },
        raison: f.raison || 'TRAVAUX',
        decor: rue ? 'barricade' : 'cones',
        // ⚠️ Une rue barree bloque TOUT son rectangle, pas sa seule couronne :
        // une chaussee de quatre tuiles de large aurait laisse passer le monde
        // par le milieu. Une cour, elle, garde sa couronne — on y circule une
        // fois dedans.
        plein: rue, existant: false,
      } };
    }
    return entraveJour.b;
  }

  /** De quel cote envoyer celui qui se bute a une rue barree : on cherche, a
      gauche puis a droite de son axe, la chaussee la plus proche. Rend -1, 1
      ou 0 (aucune — le panneau se tait plutot que de mentir). */
  function cotePourLeDetour(b, tx, ty) {
    const vertical = b.h >= b.l;
    // ⚠️ ON REGARDE AU CROISEMENT, PAS DANS L'AXE DE LA RUE BARREE. La rue qui
    // sert de detour ne passe pas a cote du chantier : elle croise la rue
    // barree a son bout. On sort donc du rectangle par le bon bout, puis on
    // cherche la chaussee de part et d'autre — chercher sur place ne trouvait
    // jamais rien, et le panneau se taisait partout.
    const sortie = vertical ? (ty === b.y ? -1 : 1) : (tx === b.x ? -1 : 1);
    const ox = vertical ? tx : tx + sortie * 3;
    const oy = vertical ? ty + sortie * 3 : ty;
    for (let d = 1; d <= 6; d++) {
      const gauche = vertical ? estRoute(ox - d, oy) : estRoute(ox, oy - d);
      const droite = vertical ? estRoute(ox + d, oy) : estRoute(ox, oy + d);
      // ⚠️ A un CARREFOUR, les deux cotes se valent — et une fleche qui se
      // tait parce qu'elle hesite est un panneau pour rien. Quand les deux
      // mènent quelque part, on montre la DROITE : c'est le detour le plus sur
      // qu'on puisse conseiller sans connaitre ou va celui qui lit.
      if (gauche || droite) return gauche && !droite ? -1 : 1;
    }
    return 0;
  }

  /** Le panneau : une plaque orange sur son piquet, et la fleche du detour. */
  function panneauDetour(ctx, px, py, vers) {
    ctx.fillStyle = '#3a3d44'; ctx.fillRect(px + 7, py - 2, 2, 8);      // le piquet
    ctx.fillStyle = '#101018'; ctx.fillRect(px + 1, py - 10, 14, 9);    // le fond
    ctx.fillStyle = '#d98324'; ctx.fillRect(px + 2, py - 9, 12, 7);     // la plaque
    ctx.fillStyle = '#101018';
    // La fleche, dans le sens du detour : une hampe et une pointe.
    const x0 = vers > 0 ? px + 4 : px + 7;
    ctx.fillRect(x0, py - 6, 5, 2);
    for (let k = 0; k < 3; k++) {
      ctx.fillRect(vers > 0 ? px + 10 - k : px + 4 + k, py - 7 - k + 1, 1, 1 + k * 2);
    }
  }

  //: **LE BRIS D'AQUEDUC** — l'entrave qu'on n'a pas vue venir, deuxieme
  //: maniere. Le char en panne s'arrete en travers d'une voie ; ici c'est la
  //: chaussee elle-meme qui lache. Elle ne se tire pas a l'aube comme l'entrave
  //: du jour : elle arrive a une HEURE, elle coule presque une heure, et elle
  //: s'arrete quand la ville trouve la vanne.
  //:
  //: ⚠️ Le tirage se fait a l'EMPREINTE de l'heure (`hash2`), jamais au de du
  //: jeu : la lecon du char en panne, qui avait fait tomber quatre juges.
  //:
  //: ⚠️ Et le trou ne fait QU'UNE TUILE. C'est ce qui le rend inoffensif pour
  //: la connexite des rues sans avoir a rappeler le juge de M1 : la tuile a, par
  //: construction, une voisine parallele qui va dans le meme sens (`carte.aqueducs`),
  //: donc le champ de direction ne bouge pas d'une fleche. La flaque deborde
  //: autour, mais elle ne fait que se VOIR.
  let brisEnCours = { cle: null, b: null };
  function brisDAqueduc() {
    const def = carte && carte.def;
    const liste = (def && def.aqueducs) || [];
    const f = def && def.aqueduc;
    if (!liste.length || !f || !B.partie) return null;
    const jour = B.partie.jour, minute = B.partie.heure * 24 * 60;
    const cle = jour * 1440 + Math.floor(minute);
    if (brisEnCours.cle === cle) return brisEnCours.b;
    brisEnCours = { cle: cle, b: null };
    // ⚠️ UN BRIS NE DEBORDE PAS SUR L'HEURE SUIVANTE, et c'est la fiche qui
    // le garantit : `minutes` vaut moins de 60, un juge Python le tient, et
    // sans cette borne deux bris se chevaucheraient — « une conduite lache »
    // deviendrait « la ville fuit de partout ». On ne regarde donc qu'une
    // heure : celle-ci.
    const heure = Math.floor(minute / 60);
    const ecoule = minute - heure * 60;
    if (ecoule >= f.minutes) return null;
    const graine = jour * 1607 + heure;
    if (hash2(graine, 0xA9DE) / 4294967296 >= f.chance_par_heure) return null;
    // ⚠️ `ecartee` : le bris qui tombe devant une porte (`app/devants.py`) passe au suivant.
    let i = hash2(graine, 0x5EA0) % liste.length;
    for (let k = 0; k < liste.length && liste[i].ecartee; k++) i = (i + 1) % liste.length;
    if (liste[i].ecartee) return null;
    const c = liste[i];
    brisEnCours.b = {
      slug: 'aqueduc', nom: "Un bris d'aqueduc",
      x: c.x, y: c.y, l: 1, h: 1,
      // ⚠️ Il arrete les CHARS et pas les JAMBES : on traverse la gerbe a pied,
      // on se mouille, et on passe. Un trou d'eau qui arreterait tout le monde
      // serait un mur, et la ville n'en a pas.
      arrete: ['vehicule'], condition: { toujours: true },
      forcer: { degats: f.degats }, raison: f.raison,
      decor: null, plein: true, existant: false, flaque: f.flaque,
    };
    return brisEnCours.b;
  }

  /** L'eau repandue autour d'un bris : un film sur la chaussee, plus epais au
      centre, avec un miroitement qui avance. ⚠️ Elle ne fait que SE VOIR — seul
      le trou arrete un char. */
  function dessinerFlaque(ctx, cam, b) {
    const r = b.flaque || 2;
    ctx.save();
    for (let ty = b.y - r; ty <= b.y + r; ty++) {
      for (let tx = b.x - r; tx <= b.x + r; tx++) {
        const d = Math.hypot(tx - b.x, ty - b.y);
        if (d > r + 0.2 || !estRoute(tx, ty)) continue;
        const px = tx * TT - cam.x, py = ty * TT - cam.y;
        if (px < -TT || py < -TT || px > VW || py > VH) continue;
        ctx.globalAlpha = Math.max(0.08, 0.44 - d * 0.11);
        ctx.fillStyle = '#2a5b78';
        ctx.fillRect(px, py, TT, TT);
        // La ride claire qui avance : c'est elle qui fait que l'eau COULE au
        // lieu d'etre une tache peinte sur l'asphalte.
        const onde = Math.sin(B.t * 0.07 + (tx * 2 + ty) * 0.9);
        if (onde > 0.55) {
          ctx.globalAlpha = Math.max(0.05, 0.3 - d * 0.07);
          ctx.fillStyle = '#9fd0e6';
          ctx.fillRect(px + 2, py + (onde > 0.85 ? 9 : 5), TT - 4, 2);
        }
      }
    }
    ctx.restore();
  }

  function barrieres() {
    const fixes = (carte && carte.def && carte.def.barrieres) || [];
    const jour = entraveDuJour(), bris = brisDAqueduc();
    if (!jour && !bris) return fixes;
    return fixes.concat(jour ? [jour] : []).concat(bris ? [bris] : []);
  }

  /** Fermee MAINTENANT ? La condition se lit dans la partie, jamais ici. */
  function barriereFermee(b) {
    if (b.existant) return false;                     // jouee ailleurs (la guerite : `majFourriere`)
    const c = b.condition || {}, p = B.partie;
    // L'entrave du jour est, par definition, celle d'aujourd'hui : elle est fermee.
    if (c.toujours) return true;
    if (c.apres) return !(p && p.missionsFaites && p.missionsFaites[c.apres]);
    if (c.heure === 'jour') return estNuit();
    if (c.heure === 'nuit') return !estNuit();
    if (c.jour_tire) return (hash2(p ? p.jour : 0, c.jour_tire.sel || 7) % 100) < (c.jour_tire.chance || 0) * 100;
    // ⚠️ UNE BARRIERE QUI SE PAIE (l'arche de la foire) : fermee tant qu'on n'a
    // pas son billet DU JOUR. Un billet par journee, pas par passage — une foire
    // qui refacture chaque aller-retour au hot-dog d'en face est un peage.
    if (c.payer) return !(p && p.billets && p.billets[c.payer] === p.jour);
    // ⚠️ UNE VRAIE SERRURE (infiltration) : fermee tant qu'on n'a pas l'objet —
    // une cle trouvee ou volee, dans `partie.objets` comme n'importe quel item
    // (le skimmer). ⚠️ Elle ne se CONSOMME pas : une cle de mission ouvre sa
    // porte tant qu'on la garde, elle ne se depense pas comme un billet.
    if (c.objet) return !(p && p.objets && p.objets[c.objet] > 0);
    return false;
  }

  /** Cette tuile est-elle DANS l'enceinte de la foire (a l'interieur de sa
      palissade) ? Les bandes viennent de Python (`foire_enclos`). */
  function dansLaFoire(tx, ty) {
    const bandes = (carte && carte.def && carte.def.foire_enclos) || [];
    for (const b of bandes) if (b[0] === ty && tx >= b[1] && tx <= b[2]) return true;
    return false;
  }

  /** ⚠️ RESQUILLER. La palissade de la foire s'enjambe comme toutes les clotures
      du jeu — on ne l'a pas rendue infranchissable, ce serait un mur qui ment.
      Mais la retombee DANS la foire sans billet coute ce que coute de forcer
      l'arche : c'est le prix de ne pas payer le prix. Rend la barriere de la
      foire, ou null (on a son billet, ou on retombe dehors). */
  function resquille(tx, ty, ax, ay) {
    if (!dansLaFoire(ax, ay) || dansLaFoire(tx, ty)) return null;
    const b = barrieres().find(function (q) { return q.condition && q.condition.payer === 'foire'; });
    return b && barriereFermee(b) ? b : null;
  }

  function dansLeRect(b, tx, ty) { return tx >= b.x && tx < b.x + b.l && ty >= b.y && ty < b.y + b.h; }
  function surLaCouronne(b, tx, ty) {
    return dansLeRect(b, tx, ty) && (tx === b.x || tx === b.x + b.l - 1 || ty === b.y || ty === b.y + b.h - 1);
  }

  /** La barriere fermee dont la couronne couvre cette tuile et qui arrete
      cette sorte (`pieton` / `vehicule`) — ou null. */
  function barriereA(tx, ty, sorte) {
    for (const b of barrieres()) {
      if (b.arrete.indexOf(sorte) < 0 || !barriereFermee(b)) continue;
      if (!(b.plein ? dansLeRect(b, tx, ty) : surLaCouronne(b, tx, ty))) continue;
      return b;
    }
    return null;
  }

  /** Cette entite, en voulant entrer sur cette tuile, se bute-t-elle a une
      barriere ? Dedans, ou en train de la forcer (`forceT`), non. Le joueur
      qui se bute lit la raison, et pousse (`buteT`) : c'est ce qui ouvre
      l'enjambee. */
  function barriereBloque(e, tx, ty) {
    if (!e || !barrieres().length || e.forceT > 0) return false;
    const sorte = e.type === 'vehicule' ? 'vehicule' : 'pieton';
    const b = barriereA(tx, ty, sorte);
    if (!b || dansLeRect(b, Math.floor(e.x / TT), Math.floor(e.y / TT))) return false;
    if (b.condition && b.condition.payer) {
      // ⚠️ ON RESSORT LIBREMENT : `dedans` dit de quel cote est la foire, et qui
      // en vient passe sans rien payer — une barriere qui se paie ne doit pas
      // enfermer celui qui a resquille, seulement lui faire payer l'entree.
      const ligne = Math.floor(e.y / TT);
      if ((b.dedans === 'N' && ligne < b.y) || (b.dedans === 'S' && ligne >= b.y + b.h)) return false;
      // Le JOUEUR a pied paie en passant : pas de menu, pas d'arret — on se bute
      // a l'arche et le billet se prend, comme a un tourniquet.
      if (e === B.joueur && typeof Missions !== 'undefined' && Missions.payer(b.prix || 0, 'BILLET DE FOIRE')) {
        B.partie.billets = B.partie.billets || {};
        B.partie.billets[b.condition.payer] = B.partie.jour;
        return false;
      }
    }
    e.bute = b;
    if (e.buteImage !== B.t) { e.buteImage = B.t; e.buteT = (e.buteT || 0) + 1; }
    if ((e === B.joueur || e.conducteur === B.joueur) && typeof Hud !== 'undefined' && B.t - (B.buteMsgT || -999) >= 90) {
      B.buteMsgT = B.t;
      Hud.message(b.raison, 90);
      if (typeof Son !== 'undefined') Son.SFX.erreur();
    }
    return true;
  }

  /** La barriere qu'un pieton peut enjamber ici : fermee, forcable, devant
      lui depuis l'exterieur — et seulement apres avoir POUSSE une seconde
      (`buteT`), le temps de lire la raison. Une etoile ne tombe pas par
      accident. */
  function barriereEnjambable(e, tx, ty) {
    if (!e || e.type === 'vehicule' || !(e.buteT >= 45)) return null;
    const b = barriereA(tx, ty, 'pieton');
    if (!b || !b.forcer || dansLeRect(b, Math.floor(e.x / TT), Math.floor(e.y / TT))) return null;
    return b;
  }

  function barrieresFermees() { return barrieres().filter(barriereFermee); }

  /** Ce qui ferme se VOIT : des cones sur la couronne d'un pont, une chaine
      sur des poteaux autour d'une cour. Rien sur ce qui est deja un mur. */
  function dessinerBarrieres(ctx, cam) {
    for (const b of barrieresFermees()) {
      // Un bris ne se pose pas : il gicle. Pas de cones, pas de barricade — de
      // l'eau, et la gerbe que `Entites` fait cracher par-dessus.
      if (b.slug === 'aqueduc') { dessinerFlaque(ctx, cam, b); continue; }
      if (!b.decor) continue;
      for (let ty = b.y; ty < b.y + b.h; ty++) {
        for (let tx = b.x; tx < b.x + b.l; tx++) {
          if (solidite(tx, ty)) continue;
          // Une rue barree porte sa barricade AUX DEUX BOUTS, pas sur toute sa
          // longueur : on ferme une rue par ses extremites, on ne la cloture pas.
          const bout = b.h >= b.l ? (ty === b.y || ty === b.y + b.h - 1)
                                  : (tx === b.x || tx === b.x + b.l - 1);
          if (b.plein ? !bout : !surLaCouronne(b, tx, ty)) continue;
          const px = tx * TT - cam.x, py = ty * TT - cam.y;
          if (px < -TT || py < -TT || px > cam.w + TT || py > cam.h + TT) continue;
          if (b.decor === 'barricade') {
            // ⚠️ **LE DETOUR SE LIT.** Une rue barree sans detour affiche n'est
            // pas une entrave, c'est un piege : on arrive, on ne passe pas, et
            // rien ne dit par ou aller. Le panneau se pose au-dessus de la
            // barricade et sa fleche montre le cote ou la rue continue.
            const vers = cotePourLeDetour(b, tx, ty);
            if (vers) panneauDetour(ctx, px, py, vers);
            // Une barricade : deux traverses barrees d'orange et de blanc, sur
            // deux pieds. Elle se lit en travers de la rue, de loin.
            ctx.fillStyle = '#3a3d44'; ctx.fillRect(px + 2, py + 9, 2, 5); ctx.fillRect(px + 12, py + 9, 2, 5);
            for (let k = 0; k < 4; k++) {
              ctx.fillStyle = k % 2 ? '#efe6d0' : '#d98324';
              ctx.fillRect(px + k * 4, py + 4, 4, 3);
              ctx.fillStyle = k % 2 ? '#d98324' : '#efe6d0';
              ctx.fillRect(px + k * 4, py + 8, 4, 2);
            }
          } else if (b.decor === 'levante') {
            // ⚠️ LA BARRIERE LEVANTE d'une guerite : un bras raye rouge et blanc en
            // travers de la rue, et son socle au bout ouest. On lit « contrôle »,
            // pas « chantier » — ce n'est pas la meme promesse.
            if (tx === b.x) {
              ctx.fillStyle = '#3a3d44'; ctx.fillRect(px + 1, py + 3, 5, 11);
              ctx.fillStyle = '#e8b33c'; ctx.fillRect(px + 2, py + 4, 3, 2);
            }
            for (let k = 0; k < 4; k++) {
              ctx.fillStyle = k % 2 ? '#efe6d0' : '#c0392b';
              ctx.fillRect(px + k * 4, py + 7, 4, 3);
            }
            ctx.fillStyle = 'rgba(11,10,18,0.3)'; ctx.fillRect(px, py + 10, TT, 1);
          } else if (b.decor === 'cones') {
            for (const ox of [2, 9]) {
              ctx.fillStyle = '#d98324'; ctx.fillRect(px + ox + 1, py + 5, 3, 7); ctx.fillRect(px + ox, py + 11, 5, 2);
              ctx.fillStyle = '#efe6d0'; ctx.fillRect(px + ox + 1, py + 8, 3, 1);
            }
          } else {
            const horizontal = ty === b.y || ty === b.y + b.h - 1;
            ctx.fillStyle = '#3a3d44';
            if (horizontal) ctx.fillRect(px, py + 9, TT, 1); else ctx.fillRect(px + 7, py, 1, TT);
            ctx.fillStyle = '#5a5d64'; ctx.fillRect(px + 6, py + 4, 3, 8);
            ctx.fillStyle = '#8b8f96'; ctx.fillRect(px + 6, py + 4, 3, 1);
          }
        }
      }
    }
  }
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
  //: Les quatre voisines d'une tuile, en croix.
  const CROIX = [[1, 0], [-1, 0], [0, 1], [0, -1]];
  /** DE L'EAU BASSE : de l'eau qui touche la terre — la premiere tuile, celle
      ou l'on a encore pied. On n'y depense pas son souffle et on ne s'y noie
      pas (`majJoueur`).

      ⚠️ **Elle se LIT dans la carte, elle ne se marque pas.** Un glyphe de
      haut-fond serait une deuxieme verite a tenir a jour : la moindre retouche
      de la cote — et la cote bouge a chaque graine — le ferait mentir sans
      qu'aucun juge rougisse. Quatre voisines en croix, la MEME mesure que
      l'enfant de la greve qui barbote (`Entites.trop_loin`) : si les deux
      devaient un jour differer, c'est que l'une des deux aurait tort.

      ⚠️ Hors carte n'est pas de la terre. La baie touche le bord du monde, et
      compter le vide comme une rive ferait un haut-fond du large. */
  function eauBasse(tx, ty) {
    if (!estEau(tx, ty)) return false;
    for (const [dx, dy] of CROIX) {
      const nx = tx + dx, ny = ty + dy;
      if (!carte || nx < 0 || ny < 0 || nx >= carte.w || ny >= carte.h) continue;
      if (!estEau(nx, ny)) return true;
    }
    return false;
  }
  // --- LE SON DU BORD DE L'EAU ---------------------------------------------------------
  //
  // ⚠️ **Une plage muette est un dessin de plage.** La grève est meublée depuis
  // le 16 sept. (174 meubles), les enfants y jouent, une coque y est amarrée —
  // et on pouvait s'asseoir sur le sable sans entendre une seule vague.
  //
  // ⚠️ Ça vit ICI et pas dans `son.js` : le volume des vagues est une question
  // de CARTE (« où est l'eau ? »), et `son.js` ne connaît pas la ville.

  //: Au-delà, on n'entend plus la baie (en tuiles) ; à une tuile, on a les
  //: pieds dedans et ça joue plein.
  const VAGUES_TUILES = 9;
  const VAGUES_PLEIN = 1;
  //: Ce que le volume rattrape par image. ⚠️ Le volume GLISSE : on ne cherche
  //: l'eau qu'une image sur quinze (289 tuiles par recherche, ça ne se paie pas
  //: soixante fois par seconde), et un volume qui saute d'un palier toutes les
  //: quinze images s'entend comme un bouton qu'on tourne.
  const VAGUES_PAS = 0.02;
  let vaguesVolume = 0, vaguesVoulu = 0;

  /** À combien de tuiles est l'eau la plus proche (distance de l'échiquier),
      ou null au-delà de `rmax`. Anneau par anneau : on s'arrête au premier. */
  function eauLaPlusProche(tx, ty, rmax) {
    for (let r = 0; r <= rmax; r++) {
      for (let dy = -r; dy <= r; dy++) {
        for (let dx = -r; dx <= r; dx++) {
          if (Math.abs(dx) !== r && Math.abs(dy) !== r) continue;
          if (estEau(tx + dx, ty + dy)) return r;
        }
      }
    }
    return null;
  }

  /** Les vagues, à chaque image. ⚠️ Dedans, la baie se tait : une porte, c'est
      une porte — et le volume repart de zéro, sinon il redescendrait en
      glissant pendant qu'on est au comptoir. */
  function majSonDuBord() {
    if (typeof Son === 'undefined') return;
    const j = B.joueur;
    if (!j || B.interieur) { vaguesVoulu = 0; vaguesVolume = 0; Son.SFX.vagues(0); return; }
    if (B.t % 15 === 0) {
      const r = eauLaPlusProche(Math.floor(j.x / TT), Math.floor(j.y / TT), VAGUES_TUILES);
      vaguesVoulu = r === null ? 0
        : r <= VAGUES_PLEIN ? 1
        : 1 - (r - VAGUES_PLEIN) / (VAGUES_TUILES - VAGUES_PLEIN);
    }
    vaguesVolume += Math.max(-VAGUES_PAS, Math.min(VAGUES_PAS, vaguesVoulu - vaguesVolume));
    Son.SFX.vagues(vaguesVolume);
  }

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

  // --- Les portes de garage : un rideau qui se leve tout seul ---------------------------
  //
  // Demande de Martin (17 sept. 2026) : « il faut une vraie porte de garage ou on
  // stationne pour vendre ou faire des missions. la porte ouvre seule des qu'on est
  // devant en voiture ». La tuile `G` reste un MUR pour tout le monde ; ce qui bouge,
  // c'est le rideau, peint par-dessus le sol comme un battant. Qui le leve, c'est
  // `Missions.majGarage`.
  //
  // ⚠️ ET ON ENTRE (21 sept. 2026 : « des portes de garage qu'on peut vraiment
  // entrer. pour permettre de semer la police en voiture »). Rideau leve, le char
  // ADMIS — celui du joueur, et lui seul — passe le seuil : la rangee du rideau et
  // les `baie` rangees de toit derriere cessent d'etre un mur POUR LUI
  // (`seuilOuvert`, lu par `Vehicules.tuileInterdite`). Pour les autres, le toit
  // reste un toit : l'auto-patrouille qui suit s'arrete devant, et la ligne de vue
  // (`ligneLibre`) ne traverse pas plus un rideau qu'un mur.

  //: Combien d'images le rideau met a monter (ou a descendre), et combien il reste
  //: leve une fois le char parti. ⚠️ Assez lent pour qu'on le VOIE monter — c'est
  //: tout l'effet —, assez vif pour qu'un char qui arrive au pas ne s'arrete pas
  //: devant un rideau encore baisse.
  const RIDEAU_MONTE = 30, RIDEAU_TIENT = 45;

  function portesDeGarage() { return (carte && carte.portesGarage) || []; }
  function porteDeGarage(lieu) { return portesDeGarage().find(function (p) { return p.lieu === lieu; }) || null; }

  /** Ce pixel est-il DEVANT le rideau : sur sa largeur (plus `marge` tuiles de
      chaque cote), et a `profondeur` tuiles au plus de la facade ? */
  function devantLaPorteDeGarage(pg, x, y, profondeur, marge) {
    const m = marge || 0;
    return x >= (pg.x - m) * TT && x < (pg.x + pg.l + m) * TT &&
           y >= (pg.y + 1) * TT && y < (pg.y + 1 + profondeur) * TT;
  }

  /** Le milieu de la place devant le rideau : ou l'on gare, ou l'on livre. */
  function baieDeLaPorteDeGarage(pg) { return { x: (pg.x + pg.l / 2) * TT, y: (pg.y + 2) * TT }; }

  /** Ce pixel est-il SOUS LE LINTEAU : dans la rangee du rideau, ou dans les rangees
      de toit derriere lui ? */
  function dansLePassage(pg, x, y) {
    return x >= pg.x * TT && x < (pg.x + pg.l) * TT && y >= (pg.y - pg.baie) * TT && y < (pg.y + 1) * TT;
  }

  /** Le rideau sous lequel ce char a le nez — ou le centre —, ou null. */
  function rideauDe(v) {
    const portes = portesDeGarage();
    for (let i = 0; i < portes.length; i++) if (portes[i].baie && dansLePassage(portes[i], v.x, v.y)) return portes[i];
    return null;
  }

  /** Ce char est-il A L'ABRI : sous le toit d'un garage, rideau pas encore leve ?
      ⚠️ Personne ne le voit alors — ni l'helico, qui voit d'en haut a travers tout
      sauf un toit, ni l'auto-patrouille garee devant le rideau, qui « sent » le
      joueur a 60 px (`Police.commandes`). Sans ca, cinq etoiles ne tomberaient
      jamais dans la cachette d'un bungalow. */
  function abrite(v) {
    const pg = v ? rideauDe(v) : null;
    return !!pg && pg.dedans === v && pg.ouverture < 1;
  }

  /** Le rideau dont ce char est ASSEZ PRES pour y avoir le nez : dans ses colonnes,
      du fond de la baie a deux tuiles devant. C'est ce que le dessin decoupe. */
  function rideauPres(v) {
    const portes = portesDeGarage();
    for (let i = 0; i < portes.length; i++) {
      const pg = portes[i];
      if (!pg.baie || v.x < pg.x * TT || v.x >= (pg.x + pg.l) * TT) continue;
      if (v.y >= (pg.y - pg.baie) * TT && v.y < (pg.y + 3) * TT) return pg;
    }
    return null;
  }

  /** ⚠️ **LA TUILE QUI S'OUVRE POUR UN SEUL CHAR.** Le passage d'un rideau n'est pas
      un mur pour le char qu'il a ADMIS, tant que le rideau est leve — ou tant que ce
      char est l'atelier en cours (`dedans`), sinon le rideau qui retombe le
      pousserait dehors (`Vehicules.degager` lit la meme regle). Pour tout autre char,
      et pour ce char-la une fois reparti, c'est un toit. */
  function seuilOuvert(v, tx, ty) {
    const portes = portesDeGarage();
    for (let i = 0; i < portes.length; i++) {
      const pg = portes[i];
      if (pg.admis !== v || !pg.baie) continue;
      if (tx >= pg.x && tx < pg.x + pg.l && ty <= pg.y && ty >= pg.y - pg.baie) return pg.ouverture >= 1 || pg.dedans === v;
    }
    return false;
  }

  /** La ligne, en pixels du monde, SOUS laquelle on voit ce qui passe le seuil : le
      bas du rideau (le linteau, rideau leve). Au-dessus, le char est sous le toit —
      ou derriere les lames. ⚠️ Le meme calcul que `dessinerPortesDeGarage`. */
  function basDuRideau(pg) { return pg.y * TT + 3 + Math.round((TT - 4) * (1 - pg.ouverture)); }

  /** Ce que le toit d'un garage CACHE, en pixels du monde : les colonnes du passage, du
      fond de la baie jusqu'au bas du rideau. ⚠️ LA MEME ZONE pour le dessin du char
      (`Entites.dessiner` la decoupe) et pour ses lampes (`Vehicules.allumerLesPhares` n'y
      allume rien) : les lampes se composent par-dessus toute l'image (`Base.fin`), et un
      char cache sous le toit y jetait ses phares et ses feux arriere A TRAVERS le toit
      (retour de Martin, 22 sept. 2026 : « on devrait rien voir »). */
  function sousLeToit(pg) {
    return { x0: pg.x * TT, x1: (pg.x + pg.l) * TT, y0: (pg.y - pg.baie) * TT, y1: basDuRideau(pg) };
  }
  function cacheSousLeToit(pg, x, y) {
    if (!pg) return false;
    const z = sousLeToit(pg);
    return x >= z.x0 && x < z.x1 && y >= z.y0 && y < z.y1;
  }

  /** On est devant : le rideau monte (ou reste leve) pour `RIDEAU_TIENT` images. */
  function leverLaPorteDeGarage(pg) { pg.tient = RIDEAU_TIENT; }

  /** Rend vrai si un rideau vient de se mettre en marche — c'est la qu'il grince. */
  function majPortesDeGarage() {
    let part = false;
    for (const pg of portesDeGarage()) {
      const voulu = pg.tient > 0 ? 1 : 0;
      if (pg.tient > 0) pg.tient--;
      if (pg.ouverture === voulu) continue;
      if (pg.ouverture === 1 - voulu) part = true;
      pg.ouverture = voulu ? Math.min(1, pg.ouverture + 1 / RIDEAU_MONTE)
                           : Math.max(0, pg.ouverture - 1 / RIDEAU_MONTE);
    }
    return part;
  }

  /** Le rideau et le garage derriere, par-dessus le sol. ⚠️ Il couvre TOUTE la
      baie, ferme compris : le dessin cuit dessous est un rideau d'une tuile par
      glyphe, et deux rideaux cote a cote ne font pas une porte de garage. */
  function dessinerPortesDeGarage(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const pg of portesDeGarage()) {
      const x = pg.x * TT - cx + 1, y = pg.y * TT - cy + 2, l = pg.l * TT - 2, h = TT - 2;
      if (x + l < 0 || x > VW || y + h < 0 || y > VH) continue;
      ctx.fillStyle = '#3b3d42';                        // les montants et le linteau
      ctx.fillRect(x, y, l, h);
      ctx.fillStyle = '#141218';                        // le dedans, dans l'ombre
      ctx.fillRect(x + 1, y + 1, l - 2, h - 1);
      ctx.fillStyle = '#2c2a31';                        // le beton du plancher, qu'on devine
      ctx.fillRect(x + 1, y + h - 3, l - 2, 3);
      ctx.fillStyle = '#e0b43a';                        // la bande jaune du seuil
      ctx.fillRect(x + 1, y + h - 1, l - 2, 1);
      const rideau = Math.round((h - 2) * (1 - pg.ouverture));
      let rects = 4;
      if (rideau > 0) {
        ctx.fillStyle = '#8a8d93';
        ctx.fillRect(x + 1, y + 1, l - 2, rideau);
        ctx.fillStyle = '#6a6d73';                      // les lames
        for (let k = y + 2; k < y + 1 + rideau; k += 2) { ctx.fillRect(x + 1, k, l - 2, 1); rects++; }
        ctx.fillStyle = '#4a4c52';                      // la barre du bas, et sa poignee
        ctx.fillRect(x + 1, y + rideau, l - 2, 1);
        ctx.fillRect(x + (l >> 1) - 2, y + rideau - 1, 4, 1);
        rects += 3;
      }
      B.stats.rects += rects;
    }
  }

  // --- La barriere coulissante : le lot du poste ne s'ouvre qu'aux siens ------------------
  //
  // Demande de Martin (23 sept. 2026) : « le poste de police doit etre completement
  // cloture barbele pour ne pas qu'on vole les autos. cree une nouvelle cloture
  // coulissante ». La tuile `Z` est du BARBELE (solidite 5) tant qu'elle n'est pas
  // grande ouverte : ni a pied, ni en char, et un lourd ne la defonce pas. Ce qui
  // l'ouvre, c'est une auto-patrouille CONDUITE (`cle`) qui arrive devant — par la
  // police, ou par le joueur qui en a vole une ailleurs. Garee, elle n'a personne au
  // volant : c'est tout le point, on ne sort pas celles du lot.
  //
  // ⚠️ ELLE NE SE REFERME JAMAIS SUR QUELQU'UN. Tant qu'un char ou un pieton touche
  // sa rangee, elle reste ouverte — sinon la tuile redeviendrait solide sous ses
  // roues, et `Vehicules.degager` le jetterait d'un cote ou de l'autre.

  //: Combien d'images le panneau met a glisser, combien il reste ouvert une fois
  //: la cle partie, et jusqu'ou la cle se sent : en travers, la largeur de la
  //: barriere et une demi-tuile ; en long, deux tuiles dedans (l'allee) et deux
  //: dehors (l'abord et le trottoir). ⚠️ PAS la chaussee : une patrouille qui passe
  //: dans la rue n'ouvre pas le lot a qui attend devant.
  const COULISSE_GLISSE = 50, COULISSE_TIENT = 60, COULISSE_DEDANS = 2, COULISSE_DEHORS = 2;

  function coulissantesDe(def) {
    const lot = def.stationnement_du_poste;
    if (!lot || !lot.barriere) return [];
    const b = lot.barriere;
    return [{ x: b.x, y: b.y, l: b.l, cle: lot.vehicule, ouverture: 0, tient: 0, libre: false }];
  }
  function barrieresCoulissantes() { return (carte && carte.coulissantes) || []; }

  /** Ce char a-t-il la CLE de cette barriere : le bon modele, quelqu'un au volant,
      et le nez dans la zone qui la commande ? */
  function aLaCle(b, v) {
    if (v.type !== 'vehicule' || v.slug !== b.cle || !v.conducteur || v.etat === 'epave') return false;
    return v.x >= (b.x - 0.5) * TT && v.x < (b.x + b.l + 0.5) * TT &&
           v.y >= (b.y - COULISSE_DEDANS) * TT && v.y < (b.y + 1 + COULISSE_DEHORS) * TT;
  }

  /** Quelqu'un (char, pieton, joueur) touche-t-il la rangee de la barriere ? */
  function quelquUnDessous(b) {
    const x0 = b.x * TT, x1 = (b.x + b.l) * TT, y0 = b.y * TT, y1 = (b.y + 1) * TT;
    return B.entites.some(function (e) {
      if (e.type !== 'vehicule' && e.type !== 'pieton' && e.type !== 'joueur') return false;
      if (e.dansVehicule) return false;                 // son char compte pour lui
      const r = e.type === 'vehicule' ? e.def.longueur / 2 : (e.r || 6);
      return e.x + r > x0 && e.x - r < x1 && e.y + r > y0 && e.y - r < y1;
    });
  }

  /** La tuile de la barriere : barbele, ou libre. ⚠️ Libre seulement GRANDE ouverte —
      un char ne se faufile pas dans un panneau a moitie tire. */
  function poserLaCoulissante(b, libre) {
    b.libre = libre;
    for (let i = 0; i < b.l; i++) carte.solide[b.y * carte.w + b.x + i] = libre ? 0 : 5;
  }

  /** Rend vrai si un panneau vient de se mettre en marche — c'est la qu'il grince. */
  function majBarrieresCoulissantes() {
    let part = false;
    for (const b of barrieresCoulissantes()) {
      if (B.entites.some(function (v) { return aLaCle(b, v); })) b.tient = COULISSE_TIENT;
      const voulu = b.tient > 0 || (b.ouverture > 0 && quelquUnDessous(b)) ? 1 : 0;
      if (b.tient > 0) b.tient--;
      if (b.ouverture !== voulu) {
        if (b.ouverture === 1 - voulu && Entites.visibleAEcran((b.x + b.l / 2) * TT, b.y * TT, TT * 2)) part = true;
        b.ouverture = voulu ? Math.min(1, b.ouverture + 1 / COULISSE_GLISSE)
                            : Math.max(0, b.ouverture - 1 / COULISSE_GLISSE);
      }
      if ((b.ouverture >= 1) !== b.libre) poserLaCoulissante(b, b.ouverture >= 1);
    }
    return part;
  }

  /** Le panneau, par-dessus le rail : il glisse vers l'EST et rentre derriere son
      poteau — on ne voit que ce qui reste en travers de l'allee. */
  function dessinerBarrieresCoulissantes(ctx, cam) {
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const b of barrieresCoulissantes()) {
      const x = b.x * TT - cx, y = b.y * TT - cy, l = b.l * TT;
      if (x + l < 0 || x > VW || y + TT < 0 || y > VH || b.ouverture >= 1) continue;
      ctx.save();
      ctx.beginPath(); ctx.rect(x, y - 2, l, TT + 2); ctx.clip();
      TUILES.Z.panneau(ctx, x + Math.round(l * b.ouverture), y, l);
      ctx.restore();
      B.stats.rects += 12;
    }
  }

  /** Cette tuile est-elle DEVANT une porte (le pas, l'axe a trois tuiles, ses flancs) ? */
  function devantDUnePorte(tx, ty) { return !!carte && carte.devants.has(tx + ',' + ty); }

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
  /** La nuit, les feux CLIGNOTENT. ⚠️ C'est une pure fonction de l'HEURE,
      comme le reste du cycle : rien a garder, et trois cent cinquante poteaux
      ne coutent pas une image de plus. */
  function feuxClignotent() {
    const t = B.defs.conduite.trafic;
    const h = B.partie ? B.partie.heure : 0.5;
    const a = t.clignotant_depuis, b = t.clignotant_jusqu_a;
    return a < b ? (h >= a && h < b) : (h >= a || h < b);
  }

  /** Qui passe et qui s'arrete quand ca clignote : **l'ARTERE passe**, et
      l'artere est la rue la plus LARGE du croisement — `l` est la largeur de
      la rue nord-sud, `h` celle de l'est-ouest. A egalite c'est le nord-sud
      qui tranche : il faut une reponse, et la meme a chaque image. */
  function arterePasse(inter, sens) {
    return (sens === '^' || sens === 'v') === (inter.l >= inter.h);
  }

  function feuDeCirculation(inter, sens) {
    if (!inter || !inter.feux) return 'vert';
    // ⚠️ La nuit : l'artere clignote jaune (on passe), la rue secondaire
    // clignote rouge (un STOP — `prochaineCible` le traite comme le panneau).
    if (feuxClignotent()) return arterePasse(inter, sens) ? 'clignote_jaune' : 'clignote_rouge';
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
  function feuVert(inter, sens) {
    const c = feuDeCirculation(inter, sens);
    // Le jaune CLIGNOTANT laisse passer ; le jaune fixe, non. Ce n'est pas la
    // meme phrase : l'un dit « attention », l'autre « ca ferme ».
    return c === 'vert' || c === 'clignote_jaune';
  }

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
    // ⚠️ La nuit, le bonhomme s'eteint avec le cycle : plus de signal, on
    // traverse a vue (`traverseeSure` reprend la main). Un feu pieton qui
    // continuerait son cycle pendant que les chars clignotent mentirait.
    if (feuxClignotent()) return 'aucun';
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

  /** La porte collee a la tuile ou se tient `e` : au nord dehors (une facade), au
      sud dedans (la sortie est sur le mur du bas). Jamais les deux.

      ⚠️ DEHORS, IL FAUT LA REGARDER : le dos tourne a la porte, il n'y en a pas, et
      l'invite « ENTRER » comme ACTION passent par ici. ⚠️ DEDANS, NON — c'est
      l'exception de la sortie : en entrant on regarde vers le fond de la piece, la
      porte est dans le dos, et c'est le jeu qui nous y a mis. Sortir reste le
      geste vif du bloquant du 13 sept. 2026 (« chez Ti-Paul, il est impossible de
      sortir »), pas un demi-tour a deviner. */
  function porteDevant(e) {
    const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
    for (const dy of [-1, 1]) {
      const porte = porteA(tx, ty + dy);
      if (porte && (B.interieur || faceA(e, (tx + 0.5) * TT, (ty + dy + 0.5) * TT))) return porte;
    }
    return null;
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

  // --- Chemins de char, par la chaussee (courses) ---------------------------------------
  //: Un second A*, reserve aux CHARS : la chaussee seule (`estRoute`), pas la
  //: grille du pieton — sinon le trace d'une course couperait tout droit par
  //: les parcs et les cours (Martin, 21 sept. 2026 : « des fleches lumineuses
  //: sur la route qui trace le chemin de la course »). Il sert au depart d'une
  //: course, une fois par troncon de circuit — jamais a chaque image.

  //: ⚠️ Un troncon traverse un quartier entier (des milliers de tuiles de
  //: chaussee) : le tas ouvert est un vrai tas, pas la file lineaire de l'A*
  //: des pietons, dont le cout grimperait au carre du nombre de noeuds.
  const NOEUDS_MAX_ROUTE = 30000;
  //: Ce qu'un pas coute EN PLUS : a contre-sens de la voie (on roule a droite,
  //: et le trace aussi), et quand on tourne (sans ca, une rue de six tuiles se
  //: descend en escalier d'une voie a l'autre, et les fleches regardent de cote).
  const COUT_CONTRE_SENS = 3, COUT_VIRAGE = 1;
  const CONTRE_SENS = { '1,0': '<', '-1,0': '>', '0,1': '^', '0,-1': 'v' };

  /** Une vraie rue : de la chaussee qui a une voie, et un sens. ⚠️ La cour de
      la fourriere et celle de l'usine sont de la chaussee sans voie (`.`), et
      elles ne touchent aucune rue — un circuit qui partirait de la ne
      sortirait jamais de la cour. */
  function estVoie(tx, ty) { return estRoute(tx, ty) && '<>^v'.indexOf(fleche(tx, ty)) >= 0; }

  /** La tuile qui passe `garde` la plus proche de (tx, ty), en spirale,
      jusqu'a `rayon` tuiles — un depart se pose devant une porte, jamais sur
      la route elle-meme. */
  function procheRoute(tx, ty, rayon, garde) {
    const ok = garde || estRoute;
    if (ok(tx, ty)) return { x: tx, y: ty };
    for (let r = 1; r <= rayon; r++) {
      for (let dx = -r; dx <= r; dx++) {
        for (let dy = -r; dy <= r; dy++) {
          if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
          if (ok(tx + dx, ty + dy)) return { x: tx + dx, y: ty + dy };
        }
      }
    }
    return null;
  }

  /** Le centre (en pixels) de la tuile de RUE (une voie, un sens) la plus
      proche de (x, y), ou null : l'ancre d'un circuit de course. */
  function routeLaPlusProche(x, y, rayon) {
    const t = procheRoute(Math.floor(x / TT), Math.floor(y / TT), rayon, estVoie);
    return t ? { x: t.x * TT + 8, y: t.y * TT + 8 } : null;
  }

  /** Un tas binaire de noeuds, trie sur `f`. */
  function tasPousser(tas, n) {
    tas.push(n);
    let i = tas.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (tas[p].f <= tas[i].f) break;
      const t = tas[p]; tas[p] = tas[i]; tas[i] = t; i = p;
    }
  }
  function tasTirer(tas) {
    const haut = tas[0], bas = tas.pop();
    if (tas.length) {
      tas[0] = bas;
      let i = 0;
      for (;;) {
        const g = 2 * i + 1, d = g + 1;
        let m = i;
        if (g < tas.length && tas[g].f < tas[m].f) m = g;
        if (d < tas.length && tas[d].f < tas[m].f) m = d;
        if (m === i) break;
        const t = tas[m]; tas[m] = tas[i]; tas[i] = t; i = m;
      }
    }
    return haut;
  }

  /** Un chemin de char, en tuiles de chaussee seulement : des centres de
      tuiles en pixels, du premier pas jusqu'a la tuile de route la plus
      proche de l'arrivee — ou null si l'une des deux n'a pas de route a
      portee, ou si aucune chaussee ne les relie. */
  function cheminRoute(x0, y0, x1, y1) {
    if (!carte) return null;
    const depart = procheRoute(Math.floor(x0 / TT), Math.floor(y0 / TT), 10);
    const arrivee = procheRoute(Math.floor(x1 / TT), Math.floor(y1 / TT), 10);
    if (!depart || !arrivee) return null;
    if (depart.x === arrivee.x && depart.y === arrivee.y) return [];
    const w = carte.w, h = carte.h, cleDepart = depart.y * w + depart.x;
    const tas = [];
    tasPousser(tas, { x: depart.x, y: depart.y, g: 0, f: Math.abs(arrivee.x - depart.x) + Math.abs(arrivee.y - depart.y), dx: 0, dy: 0 });
    const vu = new Map();
    vu.set(cleDepart, { g: 0, parent: -1 });
    let noeuds = 0;
    while (tas.length) {
      const c = tasTirer(tas);
      if (c.g > vu.get(c.y * w + c.x).g) continue;   // une entree perimee du tas
      if (c.x === arrivee.x && c.y === arrivee.y) {
        const out = [];
        for (let cle = arrivee.y * w + arrivee.x; cle !== cleDepart; cle = vu.get(cle).parent) {
          out.push({ x: (cle % w) * TT + 8, y: Math.floor(cle / w) * TT + 8 });
        }
        return out.reverse();
      }
      if (++noeuds > NOEUDS_MAX_ROUTE) return null;
      for (const d of CROIX) {
        const nx = c.x + d[0], ny = c.y + d[1];
        if (nx < 0 || ny < 0 || nx >= w || ny >= h || !estRoute(nx, ny)) continue;
        let g = c.g + 1;
        if (fleche(nx, ny) === CONTRE_SENS[d[0] + ',' + d[1]]) g += COUT_CONTRE_SENS;
        if ((c.dx || c.dy) && (c.dx !== d[0] || c.dy !== d[1])) g += COUT_VIRAGE;
        const cle = ny * w + nx, deja = vu.get(cle);
        if (deja && deja.g <= g) continue;
        vu.set(cle, { g: g, parent: c.y * w + c.x });
        tasPousser(tas, { x: nx, y: ny, g: g, f: g + Math.abs(arrivee.x - nx) + Math.abs(arrivee.y - ny), dx: d[0], dy: d[1] });
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
  function estCloture(tx, ty) {
    const s = solidite(tx, ty);
    // ⚠️ Une barriere coulissante OUVERTE reste une cloture pour le dessin : sinon le
    // poteau d'a cote, recuit pendant qu'elle est ouverte, perdrait son bras.
    return s === 4 || s === 5 || glyphe(tx, ty) === 'Z';
  }

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
  const SOLS_D_ILOT = { '.': true, ',': true, ';': true, 'x': true, 'g': true, 's': true };

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
    // ⚠️ Le quartier AU-DESSUS de l'usure (bits 6 a 9) : le trottoir d'une rue
    // commercante, d'une cour d'usine et d'une rue chic ne se peignent pas pareil.
    return (tx & 1) | ((ty & 1) << 1) | (usure << 2) | (codeDeQuartier(tx, ty) << 6);
  }

  /** La variante d'un ABORD : son usure (bits 0 a 3) et son quartier (4 a 7).
      ⚠️ Il tirait `hash2 % 4` comme un passage pieton, et son peintre lisait
      `(v >> 2) + 1` — toujours 1 : les milliers d'abords de la ville portaient
      exactement le meme grain. */
  function varianteDAbord(tx, ty) {
    return (hash2(tx, ty) % USURES_DE_SOL) | (codeDeQuartier(tx, ty) << 4);
  }

  /** La variante d'une tuile de VOIE (le petit train de la foire) : de quel
      cote la voie continue (1 nord, 2 est, 4 sud, 8 ouest — la lecture de la
      cloture), 16 si une allee la croise (un passage a niveau), et le grain du
      gazon dessous. */
  function varianteDeRail(tx, ty) {
    const est = function (x, y) { return glyphe(x, y) === 'T'; };
    const m = (est(tx, ty - 1) ? 1 : 0) | (est(tx + 1, ty) ? 2 : 0) | (est(tx, ty + 1) ? 4 : 0) | (est(tx - 1, ty) ? 8 : 0);
    // ⚠️ Des DEUX cotes : l'allee centrale vient buter contre la voie sans la
    // traverser (derriere, c'est la palissade), et des planches y inviteraient
    // a passer.
    const croise = m === 10 ? (glyphe(tx, ty - 1) === 'g' && glyphe(tx, ty + 1) === 'g')
      : m === 5 ? (glyphe(tx - 1, ty) === 'g' && glyphe(tx + 1, ty) === 'g') : false;
    return m | (croise ? 16 : 0) | ((hash2(tx, ty) % USURES_DE_SOL) << 5);
  }

  /** La variante d'une tuile : ce que son peintre a besoin de savoir de ses
      voisines. Passage pieton, case de stationnement, rampe et cloture en ont
      une ; les autres se contentent d'un bruit stable. */
  function varianteDeTuile(g, tx, ty) {
    if (CASES[g]) return varianteDeCase(g, tx, ty);
    if (g === 'T') return varianteDeRail(tx, ty);
    if (g === 'p') return hash2(tx, ty) % USURES;
    if (SOLS_D_ILOT[g]) return varianteDeSol(g, tx, ty);
    if (g === '_') return varianteDAbord(tx, ty);
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
        const mat = carte.materiaux && carte.materiaux[g];
        const cle = mat && TUILES[g + '@' + mat] ? g + '@' + mat : g;
        const peintre = TUILES[cle] || TUILES[','];
        const tuile = Atlas.cuireTuile(cle, varianteDeTuile(g, tx, ty), peintre);
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
        // ⚠️ Une facade de logement dont le batiment est en chantier : elle est
        // tombee avec les murs (voir `Chantiers.efface`).
        if (Chantiers.efface(r.x, r.y)) return;
        FACADES.residence(ctx, r, murs[r.mur % murs.length], fer, (r.x - ox) * TT, (r.y - oy) * TT);
      });
    }
    const toits = carte.toits && carte.toits.get(cle);
    if (toits) {
      toits.forEach(function (t) {
        if (!Chantiers.efface(t.x, t.y)) FACADES.toiture(ctx, t, (t.x - ox) * TT, (t.y - oy) * TT);
      });
    }
    const tags = carte.graffitis && carte.graffitis.get(cle);
    if (tags) {
      const couleurs = couleursTag();
      tags.forEach(function (gr) {
        if (Chantiers.efface(gr.x, gr.y)) return;
        FACADES.graffiti(ctx, gr, couleurs[gr.couleur % couleurs.length],
                         (gr.x - ox) * TT, (gr.y - oy) * TT);
      });
    }
    // Le chantier par-dessus tout : ses planches et son panneau pendent AU MUR.
    Chantiers.peindre(ctx, mx, my);
    // L'aeroport : la piste, ses avions, et le pont qui s'arrete au-dessus de l'eau.
    Aeroport.peindre(ctx, mx, my);
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

  //: ⚠️ CE QUE LA CARTE NE MONTRE PAS ENCORE : l'ile de l'aeroport, jusqu'au pont
  //: fini (demande de Martin). Python donne le rectangle, la mission qui le leve et
  //: la hauteur de la carte connue (`def.aeroport.masque`) ; ici on ne fait que lire
  //: la partie. La couleur de l'eau, parce que c'est ce qu'on croit y voir.
  const EAU_MINI = '#24506f';
  function masqueDeLaCarte(laquelle) {
    const k = laquelle || carte;
    const m = k && k.def && k.def.aeroport && k.def.aeroport.masque;
    if (!m) return null;
    const p = B.partie;
    return p && p.missionsFaites && p.missionsFaites[m.apres] ? null : m;
  }
  /** Cette tuile est-elle cachee sur la carte ? */
  function masquee(tx, ty, laquelle) {
    const m = masqueDeLaCarte(laquelle);
    return !!m && tx >= m.x && tx < m.x + m.l && ty >= m.y && ty < m.y + m.h;
  }
  /** La couleur d'une tuile sur la carte : celle de son sol, ou l'eau si elle est cachee. */
  function couleurMiniA(tx, ty, laquelle) {
    const k = laquelle || carte;
    return masquee(tx, ty, k) ? EAU_MINI : couleurMini(k.sol[ty][tx]);
  }
  /** La hauteur de carte que la grande carte montre : celle qu'on CONNAIT tant que
      l'ile est cachee (sous elle, il n'y a que de l'eau a montrer, et la ville garde
      son echelle) — sauf si le joueur est lui-meme plus bas : on ne le perd pas. */
  function hauteurConnue(laquelle, yJoueur) {
    const k = laquelle || carte;
    const m = masqueDeLaCarte(k);
    if (!m || !m.carte_h || (yJoueur !== undefined && yJoueur >= m.carte_h * TT)) return k.h;
    return Math.min(k.h, m.carte_h);
  }

  //: ⚠️ LE LARGE REFUSÉ (demande de Martin, 22 sept. 2026 : « même en bateau on ne
  //: puisse pas aller à l'île de l'aéroport avant que le pont soit réparé, une barrière
  //: invisible nous fait tourner de bord avant qu'on puisse voir l'île »). Tant que
  //: l'île est cachée sur la carte, elle l'est aussi à l'écran : le rectangle du masque,
  //: élargi de ce que la caméra montre AU PLUS LOIN de celui qu'elle suit — la demi-vue,
  //: son avance au volant (`AVANCE_CAMERA`) et une tuile pour la secousse —, ne se
  //: franchit pas. Python dit quoi cacher, jusqu'à quand, et ce que le HUD dit alors
  //: (`aeroport.MASQUE`) ; la portée de la vue, elle, est une affaire de caméra.
  const LARGE_MARGE_PX = TT;
  //: ⚠️ LA LISIÈRE : on ne franchit jamais la ligne de plus d'une image de char lancé,
  //: et c'est ce qu'on rend. Plus loin dedans, c'est qu'on y était déjà — une vieille
  //: sauvegarde prise sur l'île — et l'on circule, comme derrière une barrière.
  const LARGE_LISIERE_PX = TT;
  /** Le large refusé, en px ({ x0, y0, x1, y1 }), ou null : le pont est fini, ou l'on
      est dans une pièce. */
  function largeRefuse(laquelle) {
    const m = masqueDeLaCarte(laquelle);
    if (!m) return null;
    const px = VW / 2 + AVANCE_CAMERA + LARGE_MARGE_PX, py = VH / 2 + AVANCE_CAMERA + LARGE_MARGE_PX;
    return { x0: m.x * TT - px, y0: m.y * TT - py, x1: (m.x + m.l) * TT + px, y1: (m.y + m.h) * TT + py };
  }
  function dansLeLarge(z, x, y) { return x >= z.x0 && x < z.x1 && y >= z.y0 && y < z.y1; }

  /** Par où s'éloigner du large refusé : pour un point DEHORS, à moins de `marge` px
      de lui, la direction unitaire qui en sort (du point du large le plus proche vers
      lui). Null ailleurs, et dedans. */
  function sortieDuLarge(x, y, marge) {
    const z = largeRefuse();
    if (!z || dansLeLarge(z, x, y)) return null;
    const dx = x - borner(x, z.x0, z.x1), dy = y - borner(y, z.y0, z.y1), d = Math.hypot(dx, dy);
    return d > 0 && d <= marge ? { x: dx / d, y: dy / d } : null;
  }

  /** ⚠️ LA LIGNE. `e` (le joueur, ou le char qu'il conduit) vient de bouger : s'il est
      entré dans le large refusé — de moins que la lisière —, il ressort par le bord le
      plus proche, sur un seul axe : comme contre un mur, on glisse le long. Rend la
      direction de sortie ({ x, y }) quand la ligne a mordu, sinon null. ⚠️ Sans
      mémoire du pas d'avant : un char qui pivote sur son arrière (`pivoterSurLArriere`)
      ou qu'un autre pousse y entre aussi, sans passer par `avancer`. */
  function retenirAuLarge(e) {
    const z = largeRefuse();
    if (!z || !dansLeLarge(z, e.x, e.y)) return null;
    const g = e.x - z.x0, d = z.x1 - e.x, h = e.y - z.y0, b = z.y1 - e.y, p = Math.min(g, d, h, b);
    if (p > LARGE_LISIERE_PX) return null;
    if (p === g) { e.x = z.x0 - 0.01; return { x: -1, y: 0 }; }
    if (p === d) { e.x = z.x1; return { x: 1, y: 0 }; }
    if (p === h) { e.y = z.y0 - 0.01; return { x: 0, y: -1 }; }
    e.y = z.y1;
    return { x: 0, y: 1 };
  }

  /** Le HUD dit pourquoi, une fois par demi-tour : `sorte` est `coque` ou `nage`. */
  function avertirDuLarge(sorte) {
    const m = masqueDeLaCarte();
    if (!m || !m.raisons || typeof Hud === 'undefined' || B.t - (B.largeMsgT || -999) < 120) return;
    B.largeMsgT = B.t;
    Hud.message(m.raisons[sorte], 120);
  }

  /** Cette vue (le coin nord-ouest de la caméra, en px) montre-t-elle une tuile cachée ?
      Pour le mode photo, qui promène la caméra loin du joueur : il ne va pas où l'œil ne
      va pas. */
  function vueSurLeMasque(cx, cy) {
    const m = masqueDeLaCarte();
    if (!m) return false;
    return cx + VW > m.x * TT && cx < (m.x + m.l) * TT && cy + VH > m.y * TT && cy < (m.y + m.h) * TT;
  }

  /** La ville entiere, une tuile = un pixel. Cuite une fois : 18 000 rectangles
      au chargement valent mieux que 64x48 relus a chaque image.
      ⚠️ Recuite quand le masque tombe (le pont de l'aeroport fini) : la cle dit
      avec quel masque elle a ete peinte. */
  function miniCarte(laquelle) {
    const k = laquelle || carte;                  // la ville, meme quand on est dedans
    const cle = masqueDeLaCarte(k) ? 'masquee' : 'entiere';
    if (k.mini && k.miniCle === cle) return k.mini;
    const c = Base.nouveauCanvas(k.w, k.h);
    const ctx = c.getContext('2d');
    // ⚠️ Le masque se lit UNE fois, pas par tuile : 127 000 tuiles au premier dessin
    // de la mini-carte, et la premiere image du jeu les attend.
    const m = masqueDeLaCarte(k);
    for (let y = 0; y < k.h; y++) {
      const ligne = k.sol[y];
      const x0 = m && y >= m.y && y < m.y + m.h ? m.x : k.w, x1 = m ? m.x + m.l : 0;
      const couleurEn = function (x) { return x >= x0 && x < x1 ? EAU_MINI : couleurMini(ligne[x]); };
      let debut = 0, couleur = couleurEn(0);
      for (let x = 1; x <= k.w; x++) {
        const suivante = x < k.w ? couleurEn(x) : null;
        if (suivante !== couleur) {
          ctx.fillStyle = couleur;
          ctx.fillRect(debut, y, x - debut, 1);
          debut = x; couleur = suivante;
        }
      }
    }
    k.mini = c;
    k.miniCle = cle;
    return c;
  }

  /** La couleur du ZONAGE d'une tuile sur la carte plein ecran : celle de son
      usage (`carte.zonage`), ou null sur la chaussee et le trottoir — le calque
      teint les blocs, pas les rues, sinon on ne lit plus la trame. */
  function couleurDeZonage(tx, ty, laquelle) {
    const k = laquelle || carte;
    const p = k.legende[k.sol[ty][tx]] || {};
    if (p.route || p.trottoir) return null;
    const usage = usageA(tx, ty, k);
    const fiche = usage && k.def.zonage && k.def.zonage[usage];
    return fiche ? fiche.couleur : null;
  }

  /** Le calque entier, une tuile = un pixel, cuit une fois comme la mini-carte. */
  function calqueDeZonage(laquelle) {
    const k = laquelle || carte;
    if (k.calque !== undefined) return k.calque;
    if (!k.quartiers || !k.quartiers.usage) { k.calque = null; return null; }
    const c = Base.nouveauCanvas(k.w, k.h);
    const ctx = c.getContext('2d');
    for (let y = 0; y < k.h; y++) {
      let debut = 0, couleur = couleurDeZonage(0, y, k);
      for (let x = 1; x <= k.w; x++) {
        const suivante = x < k.w ? couleurDeZonage(x, y, k) : undefined;
        if (suivante !== couleur) {
          if (couleur) { ctx.fillStyle = couleur; ctx.fillRect(debut, y, x - debut, 1); }
          debut = x; couleur = suivante;
        }
      }
    }
    k.calque = c;
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

  /** Les bornes que `B.cam.{x,y}` ne depasse jamais — le meme calcul que
      `cibleCamera`, exposees pour le mode photo (M14) : la camera s'y
      detache du joueur, mais reste dans la ville. */
  function limitesCamera() {
    return {
      xMin: carte.pxW < VW ? (carte.pxW - VW) / 2 : 0, xMax: carte.pxW < VW ? (carte.pxW - VW) / 2 : carte.pxW - VW,
      yMin: carte.pxH < VH ? (carte.pxH - VH) / 2 : 0, yMax: carte.pxH < VH ? (carte.pxH - VH) / 2 : carte.pxH - VH,
    };
  }

  //: De combien la camera regarde DEVANT le char lance (px, a pleine vitesse). ⚠️ Le
  //: large refuse s'en sert (`largeRefuse`) : c'est ce qu'elle montre au plus loin du
  //: joueur. A pied, `vx × 14` reste en dessous — la nage (1 px/image) fait 14, la
  //: roulade (3,4) 47,6.
  const AVANCE_CAMERA = 48;

  //: La coop locale (essai) : au-dela de cette distance (px) entre les deux
  //: joueurs, on ramene le deuxieme vers le premier — une LAISSE, pas un
  //: zoom arriere. ⚠️ Le zoom arriere a ete essaye (Martin, 22 sept. 2026) et
  //: retire : la camera zoomait, mais le sol et les entites ne se dessinent
  //: QUE dans la fenetre normale (480×270 — `Monde.dessinerSol`,
  //: `Entites.visibleAEcran` et consorts bornent tout sur `VW`/`VH` en dur,
  //: pas sur ce que la camera montre) — zoomer aurait exige de reecrire le
  //: culls dans plusieurs modules pour un essai qui reste RISQUE. La laisse
  //: est le choix simple : ⚠️ assez court pour tenir dans 480×270 avec de la
  //: marge (le decalage du HUD, le temps que la camera rattrape le milieu),
  //: a revoir au prochain essai si ça serre trop.
  const LAISSE_COOP = 130;

  /** La camera de la coop locale (M14, essai) : le MILIEU des deux joueurs.
      `LAISSE_COOP` les empeche de trop s'eloigner — sans elle, l'un des deux
      sortirait de l'ecran. */
  function majCameraCoop(j, e2) {
    const dx = e2.x - j.x, dy = e2.y - j.y, dist = Math.hypot(dx, dy);
    if (dist > LAISSE_COOP) {
      const t = LAISSE_COOP / dist;
      e2.x = j.x + dx * t;
      e2.y = j.y + dy * t;
    }
    const mx = (j.x + e2.x) / 2, my = (j.y + e2.y) / 2;
    const cible = cibleCamera(mx, my);
    B.cam.x += (cible.x - B.cam.x) * 0.12;
    B.cam.y += (cible.y - B.cam.y) * 0.12;
    if (B.cam.secousse > 0) B.cam.secousse *= 0.9;
  }

  function majCamera() {
    const j = B.joueur;
    if (!j) return;
    if (B.coop && B.coop.entite && B.coop.entite.vivant) { majCameraCoop(j, B.coop.entite); return; }
    let avanceX = 0, avanceY = 0;
    if (j.dansVehicule) {
      const v = j.dansVehicule, f = Math.min(1, Math.abs(v.vitesse || 0) / 4);
      avanceX = Math.cos(v.angle) * AVANCE_CAMERA * f; avanceY = Math.sin(v.angle) * AVANCE_CAMERA * f;
    } else { avanceX = j.vx * 14; avanceY = j.vy * 14; }
    // ⚠️ Assis dans un manège qui MONTE (la montagne russe), on regarde le chariot,
    // pas le sol sous lui : cent cinquante pixels, c'est plus de la moitié de l'écran.
    if (j.manege) avanceY -= j.manege.z || 0;
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

  /** ⚠️ Sans argument, c'est la nuit QU'ON VOIT : dans une piece, jamais
      (`ambiance` eclaire l'interieur). Avec une heure, c'est la nuit DEHORS —
      ce que le lit doit savoir, lui qui est toujours dans une piece. */
  function estNuit(heure) { return ambiance(heure).alpha > 0.4; }

  /** Le moment de la journee, pour l'icone du HUD : 'nuit', 'aube', 'jour' ou
      'crepuscule'. ⚠️ Lu sur la teinte du ciel, pas sur des heures a part : la
      lune apparait quand `estNuit` le dit (les barrieres, les fenetres, la
      police suivent la meme regle), et l'aube et le crepuscule sont les heures
      ou la ville se teinte d'orange. ⚠️ C'est l'heure DEHORS, meme dans une
      piece : `ambiance(h)` avec une heure ne regarde pas les murs. */
  function periode(heure) {
    const h = heure === undefined ? (B.partie ? B.partie.heure : 0.5) : heure;
    const a = ambiance(h).alpha;
    if (a > 0.4) return 'nuit';
    if (a > 0.1) return h < 0.5 ? 'aube' : 'crepuscule';
    return 'jour';
  }

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

  //: **LA NUIT A SES HABITUDES : LES FENETRES S'ETEIGNENT UNE A UNE.** Chacune a
  //: son coucher et son lever (`nuit.FENETRES`), lus a l'empreinte de sa tuile —
  //: jamais au de du jeu. Poses une fois, au chargement de la carte.
  function heuresDeLaFenetre(l) {
    const f = B.defs && B.defs.nuit && B.defs.nuit.fenetres;
    if (!f) return;
    const h = hash2(l.tx, l.ty);
    l.coucher = (f.coucher[0] + (h % 1000) / 1000 * (f.coucher[1] - f.coucher[0])) % 1;
    l.lever = f.lever[0] + ((h >>> 10) % 1000) / 1000 * (f.lever[1] - f.lever[0]);
  }

  /** La fenetre dort-elle a cette heure ? Entre son coucher et son lever — qui
      peut passer minuit. Une fenetre sans heures (pas de fiche) ne dort jamais. */
  function fenetreEteinte(l, heure) {
    if (l.coucher === undefined) return false;
    const h = heure === undefined ? (B.partie ? B.partie.heure : 0.5) : heure;
    return l.coucher < l.lever ? (h >= l.coucher && h < l.lever) : (h >= l.coucher || h < l.lever);
  }

  /** Le lampadaire qui grésille est-il noir a cette image ? Par SALVES
      (`nuit.LAMPADAIRES`) : la plupart du temps il tient, puis il hoquette. A
      l'empreinte de la lampe et de `B.t` — un decor ne tire pas de de. */
  function gresilleEteint(l, t) {
    const g = B.defs && B.defs.nuit && B.defs.nuit.lampadaires;
    if (!g || !l.gresille) return false;
    const temps = t === undefined ? B.t : t;
    const salve = hash2(Math.floor(temps / g.salve_images), l.tx * 31 + l.ty) % 1000 < g.part_des_salves * 1000;
    if (!salve) return false;
    return hash2(Math.floor(temps / g.clignote_images), l.tx + l.ty * 17) % 1000 < g.part_eteinte * 1000;
  }

  // --- Les rues mouillees (la nuit a ses habitudes : l'arroseuse) ----------------------

  //: « tx,ty » -> l'instant (`B.t`) ou l'arroseuse y est passee.
  const mouillees = new Map();

  function dureeMouillee() {
    const a = B.defs && B.defs.nuit && B.defs.nuit.arroseuse;
    return a ? Math.round(a.mouille_minutes / (24 * 60) * B.defs.economie.jour_secondes * 60) : 0;
  }

  /** L'arroseuse passe : sa tuile et ses voisines sont mouillees — la chaussee
      seulement, le trottoir ne compte pas pour un char. */
  function mouiller(tx, ty, largeur) {
    const l = largeur || 0;
    for (let dy = -l; dy <= l; dy++) for (let dx = -l; dx <= l; dx++) {
      if (estRoute(tx + dx, ty + dy)) mouillees.set((tx + dx) + ',' + (ty + dy), B.t);
    }
  }

  /** ⚠️ Un instant « dans le futur » (une partie recommencee remet `B.t` a zero)
      ne mouille rien : la rue d'une autre partie est seche. */
  function mouillee(tx, ty) {
    const t = mouillees.get(tx + ',' + ty);
    return t !== undefined && B.t >= t && B.t - t < dureeMouillee();
  }

  /** Ce que la rue mouillee laisse de l'adherence d'un char, et de son freinage. */
  function adherenceMouillee(v) {
    const a = B.defs.nuit && B.defs.nuit.arroseuse;
    return a && mouillee(Math.floor(v.x / TT), Math.floor(v.y / TT)) ? a.adherence : 1;
  }
  function freinMouille(v) {
    const a = B.defs.nuit && B.defs.nuit.arroseuse;
    return a && mouillee(Math.floor(v.x / TT), Math.floor(v.y / TT)) ? a.frein : 1;
  }

  function oublierLesRuesMouillees() { mouillees.clear(); }

  /** L'asphalte mouille : plus sombre, et un reflet. Une couche PEINTE par-dessus le
      sol, qui ne touche a rien. Ce qui a seche s'oublie en passant. */
  function dessinerMouille(ctx, cam) {
    if (!mouillees.size) return;
    const duree = dureeMouillee(), cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const [cle, t] of mouillees) {
      if (B.t < t || B.t - t >= duree) { mouillees.delete(cle); continue; }
      const i = cle.indexOf(','), tx = +cle.slice(0, i), ty = +cle.slice(i + 1);
      const x = tx * TT - cx, y = ty * TT - cy;
      if (x < -TT || y < -TT || x > VW || y > VH) continue;
      // Elle seche : le dernier quart de sa duree, la tache pâlit.
      const reste = Math.min(1, (duree - (B.t - t)) / (duree * 0.25));
      // ⚠️ Ce qui dit « mouille », c'est le REFLET, pas le sombre : assombrir un
      // asphalte deja noir ne se voyait pas (capture). Un voile bleute, et des
      // miroitements en tirets, a l'empreinte de la tuile.
      ctx.fillStyle = 'rgba(30,52,86,' + (0.26 * reste).toFixed(3) + ')';
      ctx.fillRect(x, y, TT, TT);
      const h = hash2(tx, ty);
      ctx.fillStyle = 'rgba(205,225,255,' + (0.38 * reste).toFixed(3) + ')';
      ctx.fillRect(x + (h % 9), y + ((h >>> 4) % 13), 6, 1);
      ctx.fillRect(x + ((h >>> 8) % 11), y + ((h >>> 12) % 13) + 1, 4, 1);
      ctx.fillRect(x + ((h >>> 16) % 13), y + ((h >>> 20) % 14), 2, 1);
      B.stats.rects += 4;
    }
  }

  function lampesVisibles(cam) {
    // Les lampadaires n'eclairent qu'a la brune : en plein jour, rien.
    if (!carte || ambiance().alpha < 0.2) return [];
    const out = [];
    const cx = Math.round(cam.x), cy = Math.round(cam.y);
    for (const l of carte.lampes) {
      if (l.eteinte) continue;             // son poteau est a terre
      if (l.panne) continue;               // une rue pauvre : personne ne change l'ampoule
      if (l.demolie) continue;             // sa fenetre est tombee avec le batiment (chantier)
      if (fenetreEteinte(l)) continue;     // on est couche, chez nous (la nuit a ses habitudes)
      if (gresilleEteint(l)) continue;     // l'ampoule hoquette
      if (Verglas.lampeAuNoir(l)) continue; // le verglas a fait tomber les fils : le quartier est au noir
      if (l.x < cx - l.r || l.x > cx + VW + l.r || l.y < cy - l.r || l.y > cy + VH + l.r) continue;
      out.push({ x: l.x - cx, y: l.y - cy, r: l.r, c: l.c });
      if (out.length >= 25) break;
    }
    return out;
  }

  return {
    MUR, EAU, BASSE, GRILLAGE, BARBELE, MASQUE_PIETON, MASQUE_NAGEUR, MASQUE_VEHICULE,
    MASQUE_A_PIED, MORCEAUX_MAX, estEau, eauBasse, eauLaPlusProche, majSonDuBord,
    charger, entrer, changerPiece, restaurer, glyphe, solidite, bloque, defoncer, estEnjambable,
    barrieres, barriereFermee, barriereA, barriereBloque, barriereEnjambable, barrieresFermees, dessinerBarrieres,
    brisDAqueduc, dansLaFoire, resquille,
    feuxClignotent, arterePasse, nidDePoule, dessinerNids, plaqueDAcier, standingA, usageA, couleurDeZonage, calqueDeZonage, coeurDeLaVille, entraveDuJour, cotePourLeDetour,
    ouvrirPorte, battant, majBattants, dessinerBattants, BATTANT_OUVRE,
    portesDeGarage, porteDeGarage, devantLaPorteDeGarage, baieDeLaPorteDeGarage, leverLaPorteDeGarage, majPortesDeGarage, dessinerPortesDeGarage, RIDEAU_MONTE, RIDEAU_TIENT,
    dansLePassage, rideauDe, rideauPres, seuilOuvert, basDuRideau, sousLeToit, cacheSousLeToit, abrite,
    barrieresCoulissantes, majBarrieresCoulissantes, dessinerBarrieresCoulissantes, COULISSE_GLISSE, COULISSE_TIENT,
estCloture, estToit, varianteDeCloture, varianteDeRail, varianteDeBloc, varianteDeToit, varianteDePente, estRoute, estPassage, estChaussee, estAbord, estTrottoir, marchablePieton, estMeuble,
    ligneLibre, porteA, porteDevant, devantDUnePorte, zoneA, fleche, sensArret, intersectionA, feuDeCirculation, feuVert, feuPieton, estRampe, varianteDeTuile, varianteDeSol, varianteDePassage, varianteDeCase, varianteDeRampe, USURES_DE_SOL,
    dessinerSol, centrerCamera, majCamera, limitesCamera, majHeure, ambiance, estNuit, periode, rythme, heureTexte, lampesVisibles, fenetreEteinte, gresilleEteint, mouiller, mouillee, adherenceMouillee, freinMouille, dessinerMouille, oublierLesRuesMouillees,
    miniCarte, couleurMini, couleurMiniA, masqueDeLaCarte, masquee, hauteurConnue, chemin, demanderChemin, majChemins,
    largeRefuse, sortieDuLarge, retenirAuLarge, avertirDuLarge, vueSurLeMasque, AVANCE_CAMERA,
    cheminRoute, routeLaPlusProche,
    get carte() { return carte; }, get cheminsEnAttente() { return fileChemins.length; },
  };
})();
