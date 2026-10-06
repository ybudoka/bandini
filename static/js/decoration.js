/* Bandini — la planque qu'on décore (P4, docs/jalons/des-choses-a-collectionner-et-la-planque-qu-on-decore.md).

   Vague 2. Une planque vide au début, pleine à la fin : les TROPHÉES de l'album (le cadre des dix cartes, le
   grand cadre des vingt-cinq, la coupe de la Ligue) viennent d'eux-mêmes au palier ; les MEUBLES se commandent au
   catalogue Beausoleil, sur la table (le point `catalogue`), et arrivent le lendemain. Le juke-box joue les
   stations de la radio.

   ⚠️ UNE PLACE ÉCRITE PAR PIÈCE (`app/decoration.py`, `PLACES`) : la planque de Rocco et le chalet du rang ont
   chacune la leur — le même mécanisme sert aux deux. Rien au dé.

   ⚠️ CE QUI SE POSE NAÎT EN ENTRANT, NUMÉROTÉ À PART (`Entites.enDehorsDeLaSuite`) : des décors de la pièce,
   créés par `meubler` quand on y entre. Une partie sans rien dans sa planque n'en crée aucun.

   ⚠️ LE CATALOGUE voyage avec les collections (`/api/collections`, `Collections.catalogue().planque`). */

const Decoration = (function () {
  'use strict';

  // --- Les dessins : des décors de la pièce (`DECORS`), peints ici -------------------------------------------

  //: Les couleurs des huit équipes, dans l'ordre du catalogue : les cartes des cadres. (Un repli si l'album
  //: n'est pas arrivé : le cadre se peint quand même.)
  function couleursDesCartes() {
    const eq = Collections.catalogue() && Collections.catalogue().cartes && Collections.catalogue().cartes.equipes;
    const out = eq ? Object.keys(eq).map(function (d) { return eq[d].couleurs[0]; }) : [];
    return out.length ? out : ['#7a4a2a', '#6e1e2e', '#4e555e', '#1e3a6e', '#2e7a78', '#5e3a78', '#b02a22', '#2a2a2e'];
  }

  function px(ctx, c, x, y, l, h) { ctx.fillStyle = c; ctx.fillRect(x, y, l || 1, h || 1); }

  function peindreCadre(ctx, bois, filet, fond, cols, rangs, pas) {
    const l = 2 + cols * pas + 1, h = 2 + rangs * (pas + 1) + 1;
    px(ctx, bois, 0, 0, l, h);
    px(ctx, filet, 1, 1, l - 2, h - 2);
    px(ctx, fond, 2, 2, l - 4, h - 4);
    const c = couleursDesCartes();
    let k = 0;
    for (let j = 0; j < rangs; j++) for (let i = 0; i < cols; i++) {
      const x = 2 + i * pas + 1, y = 2 + j * (pas + 1) + 1;
      px(ctx, '#f4efe2', x, y, pas - 1, pas);           // le carton
      px(ctx, c[k++ % c.length], x, y + 1, pas - 1, pas - 2);   // la photo, aux couleurs de l'équipe
    }
  }

  //: Où chaque objet se tient dans sa tuile vient de Python (`decoration.POSES`, `poses` du catalogue) ; ce qui
  //: se tient `sol` est `solide` ici.
  const DESSINS = {
    cadre_dix: { w: 16, h: 12, ancre: [8, 14], r: 0, solide: false, peindre: function (ctx) {
      peindreCadre(ctx, '#5b3920', '#8a5a30', '#23331f', 5, 2, 3);
    } },
    cadre_vingt_cinq: { w: 20, h: 16, ancre: [10, 15], r: 0, solide: false, peindre: function (ctx) {
      peindreCadre(ctx, '#b8902c', '#e8c860', '#1c2a44', 5, 3, 4);
    } },
    // La coupe de la Ligue : de l'argent, deux anses, un socle de bois. Sur la table.
    coupe_album: { w: 12, h: 14, ancre: [6, 15], r: 0, solide: false, peindre: function (ctx) {
      px(ctx, '#4a2e18', 3, 11, 6, 3); px(ctx, '#6a4424', 3, 11, 6, 1);           // le socle
      px(ctx, '#9aa0a8', 5, 8, 2, 3);                                              // la tige
      px(ctx, '#c8ccd4', 2, 1, 8, 7); px(ctx, '#eef0f4', 3, 2, 2, 5);              // la coupe, son reflet
      px(ctx, '#7a808a', 2, 7, 8, 1);
      px(ctx, '#c8ccd4', 0, 2, 2, 1); px(ctx, '#c8ccd4', 0, 3, 1, 3); px(ctx, '#c8ccd4', 0, 5, 2, 1);   // les anses
      px(ctx, '#c8ccd4', 10, 2, 2, 1); px(ctx, '#c8ccd4', 11, 3, 1, 3); px(ctx, '#c8ccd4', 10, 5, 2, 1);
      px(ctx, '#d8b04a', 4, 12, 4, 1);                                              // la plaque
    } },
    // La lampe à lave : le verre rouge où les bulles montent (quatre poses, lentes).
    lampe_lave: { w: 7, h: 13, ancre: [3, 14], r: 0, solide: false, variantes: 4, anime: 24,
      peindre: function (ctx, w, h, v) {
        px(ctx, '#3a3a44', 1, 10, 5, 3); px(ctx, '#5a5a66', 2, 10, 3, 1);          // le pied
        px(ctx, '#3a3a44', 2, 0, 3, 1);                                              // le chapeau
        px(ctx, '#e2542a', 1, 1, 5, 9); px(ctx, '#f07a3a', 2, 1, 1, 9);             // le verre
        const y = [7, 5, 3, 2][v || 0], y2 = [3, 7, 6, 4][v || 0];
        px(ctx, '#ffd23a', 3, y, 2, 2); px(ctx, '#ffd23a', 2, y2, 2, 1);            // la lave
      } },
    // Le juke-box : l'arche chromée, les lumières qui tournent. Debout contre le mur.
    jukebox: { w: 14, h: 22, ancre: [7, 20], r: 6, sol: [6, 4], solide: true, variantes: 4, anime: 10,
      peindre: function (ctx, w, h, v) {
        const feux = ['#ff4a4a', '#ffd23a', '#4ad0ff', '#7aff6a'];
        px(ctx, '#5a2a1a', 1, 5, 12, 17); px(ctx, '#7a3a22', 2, 5, 10, 16);        // le meuble
        px(ctx, '#d8dce4', 2, 1, 10, 4); px(ctx, '#d8dce4', 1, 3, 12, 3);          // l'arche de chrome
        px(ctx, feux[(v || 0) % 4], 3, 2, 8, 2);                                     // les lumières
        px(ctx, feux[((v || 0) + 1) % 4], 1, 6, 1, 12); px(ctx, feux[((v || 0) + 2) % 4], 12, 6, 1, 12);
        px(ctx, '#1c1a22', 4, 7, 6, 4); px(ctx, '#e8e2c8', 5, 8, 4, 2);            // la vitre des disques
        px(ctx, '#2a2a30', 4, 13, 6, 5);                                             // la grille du haut-parleur
        for (let i = 0; i < 3; i++) px(ctx, '#6a6a74', 5, 14 + i * 2, 4, 1);
        px(ctx, '#3a1a10', 1, 21, 12, 1);
      } },
    // L'aquarium : Gérald, le poisson rouge, qui fait ses longueurs (quatre poses).
    aquarium: { w: 14, h: 16, ancre: [7, 14], r: 6, sol: [6, 4], solide: true, variantes: 4, anime: 20,
      peindre: function (ctx, w, h, v) {
        px(ctx, '#3a2a1e', 1, 10, 12, 6); px(ctx, '#4e3a28', 2, 11, 10, 4);        // le meuble
        px(ctx, '#2a2a30', 0, 1, 14, 10);                                            // le cadre
        px(ctx, '#3a86b8', 1, 2, 12, 8); px(ctx, '#5aa6d8', 1, 2, 12, 1);          // l'eau, la surface
        px(ctx, '#c8b070', 1, 9, 12, 1); px(ctx, '#3a9a4a', 3, 6, 1, 3); px(ctx, '#3a9a4a', 10, 5, 1, 4);   // le gravier, les algues
        const fx = [3, 6, 8, 5][v || 0], fy = [4, 5, 4, 6][v || 0];
        px(ctx, '#ff8a1a', fx, fy, 3, 2); px(ctx, '#ff8a1a', (v || 0) < 2 ? fx - 1 : fx + 3, fy, 1, 2);   // Gérald
        px(ctx, '#d8f0ff', 11, (v || 0) % 2 ? 3 : 5, 1, 1);                          // une bulle
      } },
    // Le téléviseur à oreilles de lapin : le meuble de bois, l'écran qui grésille.
    televiseur: { w: 14, h: 18, ancre: [7, 16], r: 6, sol: [6, 4], solide: true, variantes: 2, anime: 8,
      peindre: function (ctx, w, h, v) {
        px(ctx, '#9a9aa4', 4, 0, 1, 4); px(ctx, '#9a9aa4', 9, 0, 1, 4); px(ctx, '#9a9aa4', 5, 3, 1, 1); px(ctx, '#9a9aa4', 8, 3, 1, 1);
        px(ctx, '#2a2a30', 6, 3, 2, 2);                                              // les oreilles de lapin
        px(ctx, '#6a4424', 0, 5, 14, 11); px(ctx, '#7e5430', 1, 5, 12, 1);         // le meuble
        px(ctx, '#1c1c22', 1, 6, 9, 7);
        px(ctx, v ? '#8ab0c8' : '#a8c8d8', 2, 7, 7, 5);                              // l'écran
        px(ctx, v ? '#c8e0ec' : '#6a90a8', 3, 8 + (v ? 1 : 2), 5, 1);               // la ligne qui roule
        px(ctx, '#d8b04a', 11, 7, 2, 2); px(ctx, '#d8b04a', 11, 10, 2, 2);          // les boutons
        px(ctx, '#3a2414', 1, 16, 2, 2); px(ctx, '#3a2414', 11, 16, 2, 2);          // les pattes
      } },
    // Le sofa à carreaux, dos au mur du bas... tourné vers la télé.
    sofa: { w: 28, h: 15, ancre: [14, 13], r: 8, sol: [12, 4], solide: true, peindre: function (ctx) {
      px(ctx, '#7a1e1e', 0, 3, 28, 12);                                              // le fond rouge
      for (let y = 3; y < 15; y += 4) for (let x = 0; x < 28; x += 4) px(ctx, '#2e5a2a', x, y, 2, 2);   // les carreaux
      for (let x = 0; x < 28; x += 2) px(ctx, '#a83a2a', x, 5, 1, 1);
      px(ctx, '#5a1414', 0, 0, 4, 15); px(ctx, '#5a1414', 24, 0, 4, 15);          // les bras
      px(ctx, '#8a2a24', 4, 9, 20, 1);                                               // l'assise
      px(ctx, '#2a1a10', 2, 14, 2, 1); px(ctx, '#2a1a10', 24, 14, 2, 1);
    } },
    // Le tapis tressé : l'ovale de guenilles, à plat devant la porte.
    tapis_tresse: { w: 16, h: 10, ancre: [8, -3], r: 0, solide: false, peindre: function (ctx) {
      const anneaux = ['#6a3a22', '#b8864a', '#3a5a7a', '#c8a060', '#8a2a2a'];
      for (let i = 0; i < anneaux.length; i++) {
        const k = i;
        px(ctx, anneaux[i], 2 + k, k, 12 - 2 * k, 10 - 2 * k);
        px(ctx, anneaux[i], k, 2 + k, 16 - 2 * k, 6 - 2 * k);
      }
    } },
  };
  // L'ALBUM DES LIEUX COMPLET (le photographe, `photos.ALBUM`) : dix cartes postales sous verre, chacune son ciel et
  // la couleur de son lieu — le phare rouge, l'aéroport gris, le Dragon d'or…
  DESSINS.cadre_lieux = { w: 18, h: 12, ancre: [9, 14], r: 0, solide: false, peindre: function (ctx) {
    const lieux = ['#c0392b', '#8a8f94', '#d8a83a', '#e8e2d0', '#3a6a9a', '#6a4a3a', '#a83a7a', '#e8e8e8', '#2e7d4f', '#d8782a'];
    px(ctx, '#2a2a30', 0, 0, 18, 12); px(ctx, '#5a5a66', 1, 1, 16, 10); px(ctx, '#e8e2c8', 2, 2, 14, 8);
    for (let i = 0; i < 10; i++) {
      const x = 2 + (i % 5) * 3, y = 2 + Math.floor(i / 5) * 4;
      px(ctx, '#8ac0e0', x, y, 2, 2);                       // le ciel de la carte
      px(ctx, lieux[i], x, y + 2, 2, 1);                    // le lieu
    }
  } };
  // LE PORTRAIT (le photographe) : tiré au studio, la tenue et la coupe du jour (`partie.portrait`), dans un cadre
  // doré. ⚠️ Ses couleurs se lisent à la peinture ; sa POSE (`v`) en est l'empreinte, pour que le cache le recuise.
  DESSINS.portrait = { w: 12, h: 14, ancre: [6, 15], r: 0, solide: false, variantes: 4096, peindre: function (ctx) {
    const t = (B.partie && B.partie.portrait) || {};
    px(ctx, '#b8902c', 0, 0, 12, 14); px(ctx, '#e8c860', 1, 1, 10, 12);
    px(ctx, '#3a5a8a', 2, 2, 8, 10);                                                   // le fond du studio
    px(ctx, t.haut || '#c0392b', 3, 9, 6, 3);                                          // les épaules
    px(ctx, t.peau || '#e8b088', 4, 5, 4, 4);                                          // la face
    px(ctx, '#101018', 5, 6, 1, 1); px(ctx, '#101018', 7, 6, 1, 1);                    // les yeux
    px(ctx, t.cheveux || '#3a2a1a', 4, 4, 4, 1); px(ctx, t.cheveux || '#3a2a1a', 3, 5, 1, 2);   // la coupe
    if (t.chapeau) px(ctx, t.chapeau, 3, 3, 6, 2);                                      // le chapeau du jour
  } };
  // L'ÉTAGÈRE DES BEBELLES (vague 3) : trois tablettes de quatre, en pin foncé, contre le mur du bas — deux tuiles.
  // ⚠️ Sa POSE est l'étagère elle-même : un bit par bebelle trouvée, dans l'ordre du catalogue
  // (`Collections.masqueBebelles`) — chaque étagère différente se cuit une fois, comme une pose de manège.
  DESSINS.etagere_bebelles = { w: 32, h: 30, ancre: [16, 26], r: 8, sol: [15, 4], solide: true, variantes: 4096,
    peindre: function (ctx, w, h, v) {
      px(ctx, '#3e2616', 0, 0, 32, 30); px(ctx, '#6a4424', 0, 0, 32, 2);          // le bâti, le dessus
      px(ctx, '#2a1a10', 2, 2, 28, 27);                                             // le fond
      for (let i = 0; i < 3; i++) px(ctx, '#8a5a30', 2, 2 + i * 9 + 8, 28, 1);    // les tablettes
      px(ctx, '#2a1a10', 0, 29, 32, 1);
      const liste = typeof Collections !== 'undefined' ? Collections.bebelles() : [];
      for (let i = 0; i < liste.length && i < 12; i++) {
        if (!((v || 0) & (1 << i))) continue;
        Collections.peindreBebelle(ctx, liste[i], 3 + (i % 4) * 7, 2 + Math.floor(i / 4) * 9 + 1, 1);
      }
    } };
  // LE MUR DES ENSEIGNES (vague 5) : un panneau perforé appuyé au mur, trois rangées de quatre crochets — chaque
  // enseigne dévissée y pend, le même néon que sur la rue (`Devisser.peindreNeon`). ⚠️ Sa POSE est le mur lui-même : un
  // bit par enseigne, dans l'ordre du catalogue (`Devisser.masque`), comme l'étagère des bebelles.
  DESSINS.mur_enseignes = { w: 34, h: 32, ancre: [17, 28], r: 8, sol: [15, 4], solide: true, variantes: 4096,
    peindre: function (ctx, w, h, v) {
      px(ctx, '#4a3626', 0, 0, 34, 32); px(ctx, '#6e5236', 0, 0, 34, 1);          // le cadre, son arête
      px(ctx, '#b89a6a', 1, 1, 32, 30);                                             // le panneau perforé
      for (let y = 3; y < 31; y += 3) for (let x = 2; x < 33; x += 3) px(ctx, '#8a7048', x, y, 1, 1);   // ses trous
      px(ctx, '#2a1e14', 0, 31, 34, 1);
      const liste = typeof Devisser !== 'undefined' ? Devisser.liste() : [];
      for (let i = 0; i < 12; i++) {
        const x = 1 + (i % 4) * 8, y = 1 + Math.floor(i / 4) * 10;
        px(ctx, '#5c5e66', x + 3, y, 1, 1);                                         // le crochet
        if (!liste[i] || !((v || 0) & (1 << i))) continue;
        Devisser.peindreNeon(ctx, liste[i], x, y + 1, 1);
      }
    } };
  //: Posés dans le catalogue commun des décors : le moteur les peint comme les autres (`Entites.dessiner`).
  if (typeof DECORS !== 'undefined') for (const nom in DESSINS) DECORS[nom] = DESSINS[nom];

  // --- Le catalogue (arrivé avec les collections) ----------------------------------------------------

  function donnees() { const c = Collections.catalogue(); return (c && c.planque) || null; }
  function meubles() { const d = donnees(); return (d && d.meubles) || []; }
  function trophees() { const d = donnees(); return (d && d.trophees) || []; }
  function places(piece) { const d = donnees(); return (d && d.places && d.places[piece]) || null; }
  function meuble(slug) { return meubles().find(function (m) { return m.slug === slug; }) || null; }

  /** Les meubles de la partie, par pièce : `p.meubles[piece][slug] = { jour }` — le jour de la commande. */
  function commandes(piece) {
    const p = B.partie;
    if (!p) return {};
    if (!p.meubles || typeof p.meubles !== 'object') p.meubles = {};
    if (!p.meubles[piece] || typeof p.meubles[piece] !== 'object') p.meubles[piece] = {};
    return p.meubles[piece];
  }
  /** Livré : commandé AVANT aujourd'hui (le camion passe le lendemain matin). */
  function livre(piece, slug) { const c = commandes(piece)[slug]; return !!c && B.partie.jour > c.jour; }
  function commande(piece, slug) { return !!commandes(piece)[slug]; }

  /** Ce qui se tient dans la pièce `piece`, dans l'ordre : les trophées atteints, puis les meubles livrés. */
  function presents(piece) {
    const ici = places(piece);
    if (!ici) return [];
    const out = [];
    for (const t of trophees()) {
      const n = t.famille === 'bebelles' ? Collections.nombreBebelles() : t.famille === 'cartes' ? Collections.nombre()
        : t.famille === 'enseignes' && typeof Devisser !== 'undefined' ? Devisser.nombre()
        : t.famille === 'lieux' && typeof Photos !== 'undefined' ? Photos.album().a.length : 0;
      if (n >= t.palier && ici[t.slug]) out.push(t.slug);
    }
    for (const m of meubles()) if (livre(piece, m.slug) && ici[m.slug]) out.push(m.slug);
    return out;
  }

  // --- Entrer : meubler la pièce -----------------------------------------------------------------------

  function pose(slug) { const d = donnees(); return (d && d.poses && d.poses[slug]) || 'sol'; }

  function yDeLaPose(pose, ty) {
    return pose === 'mur' || pose === 'plat' ? ty * TT + 1 : pose === 'table' ? ty * TT + 10 : ty * TT + 12;
  }

  /** On entre dans `piece` (`B.interieur`) : ses objets naissent, numérotés à part, et le juke-box devient un
      point (ACTION). Rend les entités posées. */
  function meubler(piece) {
    if (!piece || !places(piece.slug)) return [];
    const ici = places(piece.slug), posees = [];
    Entites.enDehorsDeLaSuite(function () {
      for (const slug of presents(piece.slug)) {
        const d = DESSINS[slug], o = ici[slug];
        if (!d || !o) continue;
        // Un objet de `l` tuiles se pose au milieu de ses tuiles ; l'étagère porte ce qu'on a trouvé (sa pose).
        posees.push(Entites.creer('decor', o.x * TT + (o.l || 1) * 8, yDeLaPose(pose(slug), o.y), {
          decor: slug, r: d.r || 0, solide: !!d.solide, dessine: true, deLaPlanque: true,
          v: slug === 'etagere_bebelles' ? Collections.masqueBebelles() : slug === 'mur_enseignes' ? Devisser.masque()
            : slug === 'portrait' ? empreintePortrait() : 0,
        }));
      }
    });
    // ⚠️ Le juke-box se TOUCHE : un point de plus, sur une COPIE de la liste (la pièce du catalogue sert à
    // toutes les portes qui la partagent).
    if (posees.some(function (e) { return e.decor === 'jukebox'; })) {
      piece.points = (piece.points || []).concat([{ type: 'jukebox', x: ici.jukebox.x, y: ici.jukebox.y }]);
    }
    if (posees.length) Entites.reindexerDecor();
    return posees;
  }

  // --- Le juke-box ---------------------------------------------------------------------------------------

  //: Il joue : la radio s'arrête quand on sort de la planque.
  let joue = false;

  /** ACTION au juke-box : la station suivante, puis le silence, puis la première (`Son.Radio.suivante`). */
  function jukebox() {
    const station = Son.Radio.suivante();
    joue = !!station;
    const s = station && Son.Radio.station(station);
    Hud.message(s ? 'JUKE-BOX : ' + String(s.nom || station).toUpperCase() : 'JUKE-BOX : SILENCE', 150);
    return true;
  }

  function maj() {
    if (joue && (!B.interieur || !places(B.interieur.slug))) { joue = false; Son.Radio.arreter(); }
  }

  // --- Le catalogue Beausoleil --------------------------------------------------------------------------

  function menuCatalogue() {
    const p = B.partie, piece = B.interieur && B.interieur.slug;
    const ici = places(piece) || {};
    const items = meubles().filter(function (m) { return m.ou.indexOf('catalogue') >= 0 && ici[m.slug]; }).map(function (m) {
      const deja = commande(piece, m.slug), arrive = deja && livre(piece, m.slug);
      return { libelle: m.nom, detail: arrive ? 'À TOI' : deja ? 'LIVRÉ DEMAIN' : m.prix + ' $', texte: m.texte,
               actif: !deja && p.argent >= m.prix, faire: function () { commander(m.slug); return false; } };
    });
    if (!items.length) items.push({ libelle: 'LE CATALOGUE N’EST PAS ENCORE ARRIVÉ', actif: false });
    const menu = { titre: 'LE CATALOGUE BEAUSOLEIL', sur: p.argent + ' $', largeur: 320, items: items, aide: '' };
    // La ligne du catalogue, sous la liste : celle du meuble sous le curseur.
    menu.maj = function (m) { const i = m.items[m.curseur || 0]; m.aide = (i && i.texte) || 'LIVRÉ LE LENDEMAIN'; };
    menu.maj(menu);
    return menu;
  }

  /** Commander `slug` pour la planque où l'on est : payé tout de suite, livré le lendemain. */
  function commander(slug) {
    const piece = B.interieur && B.interieur.slug;
    return livrerA(piece, slug, meuble(slug) && meuble(slug).prix, 'COMMANDÉ AU CATALOGUE');
  }

  /** L'empreinte du portrait (ses couleurs), sur 12 bits : la pose sous laquelle il se cuit. */
  function empreintePortrait() {
    const t = (B.partie && B.partie.portrait) || {};
    const texte = [t.peau, t.cheveux, t.haut, t.chapeau].join('|');
    let h = 0;
    for (let i = 0; i < texte.length; i++) h = (h * 31 + texte.charCodeAt(i)) >>> 0;
    return h % 4096;
  }

  /** Le portrait se tire AU STUDIO : la tenue et la coupe d'aujourd'hui (`Garderobe.duJoueur`), gardees dans la partie. */
  function tirerLePortrait() {
    const p = B.partie, tn = Garderobe.duJoueur(p, B.defs);
    p.portrait = { peau: tn.peau, cheveux: tn.cheveux, haut: tn.couleur_haut, jour: p.jour,
                   chapeau: tn.chapeau && tn.chapeau !== 'aucun' ? tn.couleur_chapeau : null };
  }

  /** Acheter `slug` au prix `prix` et le faire livrer le lendemain dans la planque `piece` : le catalogue (la planque
      où l'on est), et le comptoir d'un magasin de meubles (`Missions.menuComptoir` : celle de Rocco). */
  function livrerA(piece, slug, prix, carnet) {
    const p = B.partie, m = meuble(slug);
    if (!m || !piece || !places(piece) || commande(piece, slug)) return false;
    if (!Missions.payer(prix, m.nom)) return false;
    commandes(piece)[slug] = { jour: p.jour };
    if (slug === 'portrait') tirerLePortrait();
    Hud.message(m.nom + ' — LIVRÉ DEMAIN', 160);
    Histoire.noter(carnet + ' : ' + m.nom, false);
    return true;
  }

  /** Le lever du jour (`Missions.nouveauJour`) : ce qui arrive aujourd'hui se dit. */
  function nouveauJour() {
    const p = B.partie;
    if (!p || !p.meubles) return [];
    const arrives = [];
    for (const piece in p.meubles) for (const slug in p.meubles[piece]) {
      if (p.meubles[piece][slug].jour === p.jour - 1) { const m = meuble(slug); if (m) arrives.push(m.nom); }
    }
    if (arrives.length) {
      Hud.message('LIVRAISON À LA PLANQUE : ' + arrives.join(', '), 220);
      Histoire.noter('LIVRÉ À LA PLANQUE : ' + arrives.join(', '), false);
    }
    return arrives;
  }

  function oublier() { if (joue) Son.Radio.arreter(); joue = false; }

  return { DESSINS, donnees, pose, meubles, meuble, trophees, places, presents, livre, commande, meubler, jukebox, maj,
           menuCatalogue, commander, livrerA, nouveauJour, oublier };
})();
