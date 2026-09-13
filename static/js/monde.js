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
  const MASQUE_VEHICULE = MUR | EAU | BASSE | GRILLAGE | BARBELE;
  // ⚠️ Le masque des CHEMINS a pied, et il n'est pas celui des corps : un
  // grillage s'enjambe, donc un chemin peut le traverser — plus cher qu'une
  // tuile normale (`COUT_GRILLAGE`), jamais gratuitement. Si le A* s'arretait
  // aux clotures comme les corps, la premiere cloture venue gagnerait toutes
  // les poursuites : on enjambe, et les agents restent plantes de l'autre cote.
  const MASQUE_A_PIED = MUR | EAU | BARBELE;

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
        if (ligne[x] === 'd' || ligne[x] === 'D') portesFermees.push({ x: x, y: y });
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
      for (let y = inter.y - 2; y < inter.y + inter.h + 2; y++) {
        for (let x = inter.x - 2; x < inter.x + inter.l + 2; x++) croisements.set(x + ',' + y, inter);
      }
    });
    carte = {
      def: def, w: w, h: h, sol: def.sol, voie: def.voie, legende: def.legende,
      // Le plancher d'une piece : ce qu'on peint SOUS les meubles (null dehors).
      plancher: def.plancher || null,
      solide: solide, route: route, passage: passage, portesFermees: portesFermees,
      morceaux: new Map(), visibles: new Set(),
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
      points: def.points_interet || [],
      zones: def.zones || [],
      apparition: def.apparition,
      pxW: w * TT, pxH: h * TT,
      devantures: indexerParMorceau(def.devantures || [], function (d) {
        // Le mur ET la tuile de trottoir sous lui (la pancarte y pend).
        return [d.x, d.y, d.l, 2];
      }),
      // Les logements : meme regle, l'escalier de fer descend sur le trottoir.
      residences: indexerParMorceau(def.residences || [], function (r) {
        return [r.x, r.y, r.l, 2];
      }),
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
  /** Une tuile qu'un pieton peut fouler en flanant : ni mur, ni eau, ni chaussee. */
  function marchablePieton(tx, ty) { return !bloque(tx, ty, MASQUE_PIETON) && !estChaussee(tx, ty); }
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

  /** Le feu est-il vert pour qui roule dans ce sens vers ce croisement ?
      ⚠️ Un croisement en T ou en L n'a pas de feu : on y passe a vue. */
  function feuVert(inter, sens) {
    if (!inter || !inter.feux) return true;
    const t = B.defs.conduite.trafic;
    const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
    const phase = (B.t + inter.decalage) % cycle;
    const nordSud = sens === '^' || sens === 'v';
    const moitie = phase < cycle / 2;
    // Premiere moitie : nord-sud roule. L'orange ferme la fin de chaque moitie.
    const dansMoitie = moitie ? phase : phase - cycle / 2;
    if (dansMoitie >= t.feu_vert_images) return false;
    return nordSud === moitie;
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
    const w = carte.w, cout = coutCloture();
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
        const cle = ny * w + nx, g = c.g + (solidite(nx, ny) === 4 ? cout : 1);
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
  const GRAINS_DE_TOIT = 4;

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

  /** La variante d'une tuile : ce que son peintre a besoin de savoir de ses
      voisines. Passage pieton, case de stationnement, rampe et cloture en ont
      une ; les autres se contentent d'un bruit stable. */
  function varianteDeTuile(g, tx, ty) {
    if (CASES[g]) return varianteDeCase(g, tx, ty);
    if (g === 'p') return hash2(tx, ty) % USURES;
    if (g === 'R' || g === 'J') return varianteDeRampe(g, tx, ty);
    const p = carte.legende[g];
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
    // ⚠️ L'ombre des murs d'abord : elle se peint SOUS les enseignes (une ombre
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
      if (l.x < cx - l.r || l.x > cx + VW + l.r || l.y < cy - l.r || l.y > cy + VH + l.r) continue;
      out.push({ x: l.x - cx, y: l.y - cy, r: l.r, c: l.c });
      if (out.length >= 25) break;
    }
    return out;
  }

  return {
    MUR, EAU, BASSE, GRILLAGE, BARBELE, MASQUE_PIETON, MASQUE_VEHICULE, MASQUE_A_PIED, MORCEAUX_MAX,
    charger, entrer, changerPiece, restaurer, glyphe, solidite, bloque, defoncer, estEnjambable, estCloture, estToit, varianteDeCloture, varianteDeToit, varianteDePente, estRoute, estPassage, estChaussee, marchablePieton, estMeuble,
    ligneLibre, porteA, porteDevant, zoneA, fleche, sensArret, intersectionA, feuVert, estRampe, varianteDePassage, varianteDeCase, varianteDeRampe,
    dessinerSol, centrerCamera, majCamera, majHeure, ambiance, estNuit, rythme, heureTexte, lampesVisibles,
    miniCarte, couleurMini, chemin, demanderChemin, majChemins,
    get carte() { return carte; }, get cheminsEnAttente() { return fileChemins.length; },
  };
})();
