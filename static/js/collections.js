/* Bandini — des choses à collectionner (P4, docs/jalons/des-choses-a-collectionner-et-la-planque-qu-on-decore.md).

   Vague 1 : LES CARTES DE HOCKEY de la Ligue de Baie-des-Brumes, saison 1974-75 — quarante cartes, cinq par
   district, chacune dans un recoin que `app/collectionner.py` a choisi par une règle sur la ville finie (sans
   un dé). Par terre, une petite carte aux couleurs de l'équipe ; toutes les trois secondes, un scintillement.
   On la ramasse en marchant dessus, à pied : 25 $, un son, une ligne au carnet, et une prime aux paliers.

   ⚠️ LE CATALOGUE ARRIVE À PART (`/api/collections`) : ni les définitions ni la carte n'avaient la place. Il
   se demande juste après les définitions, en arrière-plan (`charger`), comme les notes de la musique ; tant
   qu'il n'est pas là, il n'y a rien à trouver ni à compter — mais ce qu'on a trouvé reste dans la partie.

   ⚠️ RIEN AU DÉMARRAGE : une carte par terre n'est pas une entité, elle se PEINT (`dessiner`). Un décor de
   plus au chargement décale le numéro de tout ce qui naît ensuite (« décor eager décale les identifiants »).

   ⚠️ LE NUMÉRO EST LE NOM : `partie.collections.cartes` garde `{ numero: { jour, source } }`. Le marché aux
   puces (sa ligne) vendra celle qui manque par `donner(numero, 'puces')` — jamais par un index. */

const Collections = (function () {
  'use strict';

  //: Le catalogue tel que `/api/collections` le sert : `{ cartes: { titre, equipes, positions, liste }, regle }`.
  let paquet = null;
  //: La demande : null | 'en cours' | 'arrive' | 'ratee' | 'etranger'.
  const demande = { etat: null, url: null, empreinte: null, essaiT: 0 };
  //: Une demande ratée se refait, au plus une fois par tant d'images (dix secondes).
  const REESSAI_IMAGES = 600;
  //: Le scintillement dure tant d'images.
  const ECLAT_IMAGES = 14;

  // --- Le catalogue ---------------------------------------------------------------------------------

  //: La fenêtre du navigateur (le banc en pose une fausse) : c'est elle qui a `fetch`.
  let fenetre = null;

  /** Va chercher le catalogue. `empreinte` : celle que les définitions nomment (`collections_empreinte`). */
  function charger(w, url, empreinte) {
    fenetre = w || null;
    demande.url = url || null; demande.empreinte = empreinte || null;
    tenter();
  }

  function tenter() {
    if (!demande.url || demande.etat === 'en cours' || demande.etat === 'arrive' || demande.etat === 'etranger') return;
    if (!fenetre || !fenetre.fetch) return;
    demande.etat = 'en cours';
    demande.essaiT = B.t || 0;
    fenetre.fetch(demande.url)
      .then(function (r) { if (!r.ok) throw new Error('collections ' + r.status); return r.json(); })
      .then(function (p) {
        // ⚠️ Un déploiement tombé entre les deux requêtes : ces cartes-là seraient celles d'une autre ville.
        if (!p || !p.cartes || (demande.empreinte && p.empreinte !== demande.empreinte)) { demande.etat = 'etranger'; return; }
        paquet = p;
        demande.etat = 'arrive';
        // Ses sons voyagent avec lui (`audio.LIEUX_A_PART`) : ils rejoignent le paquet des définitions.
        if (p.sons) Son.Lieu.declarer(p.sons);
      })
      .catch(function () { demande.etat = 'ratee'; });
  }

  /** Une demande ratée se refait, sans marteler un réseau coupé. */
  function reclamer() {
    if (demande.etat === 'ratee' && (B.t || 0) - demande.essaiT >= REESSAI_IMAGES) { demande.etat = null; tenter(); }
  }

  /** Pose le catalogue tel quel (le banc, un essai). */
  function poser(p) { paquet = p || null; demande.etat = p ? 'arrive' : null; if (p && p.sons) Son.Lieu.declarer(p.sons); }
  function catalogue() { return paquet; }
  function etatDeLaDemande() { return demande.etat; }

  // --- Les cartes -----------------------------------------------------------------------------------

  function cartes() { return (paquet && paquet.cartes && paquet.cartes.liste) || []; }
  function regle() { return (paquet && paquet.regle) || {}; }
  function equipe(district) { return (paquet && paquet.cartes && paquet.cartes.equipes[district]) || null; }
  function position(abrev) { return (paquet && paquet.cartes && paquet.cartes.positions[abrev]) || abrev; }
  function fiche(numero) { return cartes().find(function (c) { return c.numero === Number(numero); }) || null; }

  /** Ce qu'on a trouvé d'une famille (`cartes`, `bebelles`) : un objet par numéro ou par slug. */
  function famille(nom) {
    const p = B.partie;
    if (!p) return {};
    if (!p.collections || typeof p.collections !== 'object') p.collections = { cartes: {}, bebelles: {} };
    if (!p.collections[nom] || typeof p.collections[nom] !== 'object') p.collections[nom] = {};
    return p.collections[nom];
  }
  function album() { return famille('cartes'); }
  function trouvee(numero) { return !!album()[numero]; }
  /** Combien on en a, parmi celles du catalogue (une carte retirée ne compte plus). */
  function nombre() { return cartes().filter(function (c) { return trouvee(c.numero); }).length; }
  function total() { return cartes().length; }

  /** Les équipes, dans l'ordre du catalogue : `{ district, nom, couleurs, n, total }`. */
  function parEquipe() {
    const out = [];
    for (const c of cartes()) {
      let e = out.find(function (q) { return q.district === c.district; });
      if (!e) {
        const eq = equipe(c.district) || { nom: c.district.toUpperCase(), couleurs: ['#888888', '#eeeeee'] };
        e = { district: c.district, nom: eq.nom, couleurs: eq.couleurs, n: 0, total: 0 };
        out.push(e);
      }
      e.total++;
      if (trouvee(c.numero)) e.n++;
    }
    return out;
  }

  /** Celles qu'on voit et qu'on ramasse : en ville seulement, ni dans une pièce ni dans un bloc. ⚠️ La
      place est dans le catalogue (`x`, `y`, en tuiles de la VILLE) — jamais `Monde.carte`, qui est le bloc. */
  function aTrouver() {
    if (B.interieur || B.bloc) return [];
    return cartes().filter(function (c) { return typeof c.x === 'number' && !trouvee(c.numero); });
  }
  function pixels(c) { return { x: c.x * TT + 8, y: c.y * TT + 10 }; }

  // --- Les bebelles (vague 3) ------------------------------------------------------------------------

  //: Douze curiosités cachées dans les endroits durs (`app/collectionner.py`, `BEBELLES`) : le bout de l'île, le
  //: fond de l'aéroport (on y saute), le fond du rang et du ciné-parc (des BLOCS), le coin le plus loin de chaque
  //: district. ⚠️ Le SLUG est le nom — `partie.collections.bebelles[slug]` —, et l'ORDRE du catalogue est la place
  //: sur l'étagère de la planque (`Decoration`).
  function bebelles() { return (paquet && paquet.bebelles && paquet.bebelles.liste) || []; }
  function regleBebelles() { return (paquet && paquet.bebelles && paquet.bebelles.regle) || {}; }
  function bebelle(slug) { return bebelles().find(function (b) { return b.slug === slug; }) || null; }
  function rangBebelle(slug) { return bebelles().findIndex(function (b) { return b.slug === slug; }); }
  function bebelleTrouvee(slug) { return !!famille('bebelles')[slug]; }
  function nombreBebelles() { return bebelles().filter(function (b) { return bebelleTrouvee(b.slug); }).length; }
  function totalBebelles() { return bebelles().length; }
  /** L'étagère : un bit par bebelle trouvée, dans l'ordre du catalogue (la pose du dessin de l'étagère). */
  function masqueBebelles() {
    let m = 0;
    bebelles().forEach(function (b, i) { if (bebelleTrouvee(b.slug)) m |= 1 << i; });
    return m;
  }

  /** Celles qu'on voit et qu'on ramasse ICI : dans la ville, celles de la ville ; dans un bloc, celles de CE bloc
      (leur place est en tuiles du bloc) ; jamais dans une pièce. */
  function bebellesATrouver() {
    if (B.interieur) return [];
    const ici = B.bloc ? B.bloc.slug : null;
    return bebelles().filter(function (b) { return typeof b.x === 'number' && (b.bloc || null) === ici && !bebelleTrouvee(b.slug); });
  }

  /** Le dessin d'une bebelle : sa grille (6 × 7) et sa palette, `ech` pixels par case. `ombre` : toute la
      silhouette dans cette couleur (le contour d'hiver). */
  function peindreBebelle(ctx, b, x, y, ech, ombre) {
    const g = b.grille || [];
    for (let iy = 0; iy < g.length; iy++) {
      const r = g[iy];
      for (let ix = 0; ix < r.length; ix++) {
        const c = r[ix];
        if (c === '.') continue;
        ctx.fillStyle = ombre || b.palette[c] || '#ff00ff';
        ctx.fillRect(x + ix * ech, y + iy * ech, ech, ech);
      }
    }
    B.stats.rects += 8;
  }

  /** `slug` entre sur l'étagère. `source` : `rue`, `puces`, `debug`. La prime, le son, le carnet, les paliers. */
  function donnerBebelle(slug, source, silence) {
    const b = bebelle(slug), p = B.partie;
    if (!b || !p || bebelleTrouvee(b.slug)) return false;
    famille('bebelles')[b.slug] = { jour: p.jour, source: source || 'rue' };
    if (silence) return true;
    const r = regleBebelles(), n = nombreBebelles(), N = totalBebelles();
    if (r.prime) Missions.encaisser(r.prime, 'BEBELLE', true);
    Son.SFX.bebelle();
    Hud.message('BEBELLE ' + n + '/' + N + ' — ' + b.nom + (r.prime ? ' (+' + r.prime + ' $)' : ''), 240);
    Histoire.noter('BEBELLE : ' + b.nom + ' — SUR L’ÉTAGÈRE DE LA PLANQUE', false);
    const palier = (r.paliers || {})[String(n)];
    if (palier) {
      Missions.encaisser(palier, 'COLLECTION', true);
      const complet = n === N;
      const titre = complet ? 'L’ÉTAGÈRE EST PLEINE' : n + ' BEBELLES';
      Son.SFX.reel_bebelles();
      Hud.prime({ montant: palier, titre: titre, quoi: 'COLLECTION', bonus: 0, palier: Missions.palierDePrime(palier) });
      Histoire.noter((complet ? 'LES DOUZE BEBELLES SONT SUR L’ÉTAGÈRE' : n + ' BEBELLES') + ' — ' + palier + ' $', true);
    }
    return true;
  }

  // --- Donner une carte : la rue, le debug, et un jour le marché aux puces ---------------------------

  /** `numero` entre dans l'album. `source` : `rue` (on l'a ramassée), `puces` (achetée), `debug`. Rend
      false si elle y était déjà ou n'existe pas. La prime, le son, le carnet et les paliers suivent. */
  function donner(numero, source, silence) {
    const c = fiche(numero), p = B.partie;
    if (!c || !p || trouvee(c.numero)) return false;
    album()[c.numero] = { jour: p.jour, source: source || 'rue' };
    if (silence) return true;
    const r = regle(), n = nombre(), N = total();
    if (r.prime) Missions.encaisser(r.prime, 'CARTE DE HOCKEY', true);
    Son.SFX.carte_hockey();
    Hud.message('CARTE ' + n + '/' + N + ' — ' + c.nom + (r.prime ? ' (+' + r.prime + ' $)' : ''), 220);
    Histoire.noter('CARTE DE HOCKEY N° ' + c.numero + ' : ' + c.nom, false);
    const palier = (r.paliers || {})[String(n)];
    if (palier) {
      Missions.encaisser(palier, 'COLLECTION', true);
      const complet = n === N;
      const titre = complet ? 'L’ALBUM EST COMPLET' : n + ' CARTES DE HOCKEY';
      Son.SFX.orgue_arena();
      Hud.prime({ montant: palier, titre: titre, quoi: 'COLLECTION', bonus: 0, palier: Missions.palierDePrime(palier) });
      Histoire.noter((complet ? 'L’ALBUM DE LA LIGUE EST COMPLET' : n + ' CARTES DE HOCKEY') + ' — ' + palier + ' $', true);
    }
    return true;
  }

  // --- La boucle -------------------------------------------------------------------------------------

  //: Les sons des cartes (`audio.LIEUX.collections`) se chargent quand une carte qui manque est à moins de
  //: tant de pixels — un écran : on l'entendra avant de la ramasser.
  const SONS_A_PX = 480;

  function majSons(j) {
    if ((B.t || 0) % 30 !== 0 || !j) return;
    if (aTrouver().concat(bebellesATrouver()).some(function (c) { const q = pixels(c); return Math.abs(q.x - j.x) < SONS_A_PX && Math.abs(q.y - j.y) < SONS_A_PX; })) {
      Son.Lieu.charger('collections');
    }
  }

  function maj() {
    reclamer();
    const j = B.joueur;
    majSons(j);
    if (!B.partie || !j || j.dansVehicule || j.hospitalise || B.menu || B.cinema || B.scene) return;
    const r = regle().rayon_px || 12;
    for (const c of aTrouver()) {
      const q = pixels(c);
      if (Math.abs(j.x - q.x) > r || Math.abs(j.y - q.y) > r) continue;
      if (dist2(j.x, j.y, q.x, q.y) > r * r) continue;
      j.animT = 12; j.animType = 'ramasse';
      donner(c.numero, 'rue');
      return;                       // une par image : deux messages ne s'écrasent pas
    }
    for (const b of bebellesATrouver()) {
      const q = pixels(b);
      if (dist2(j.x, j.y, q.x, q.y) > r * r) continue;
      j.animT = 12; j.animType = 'ramasse';
      donnerBebelle(b.slug, 'rue');
      return;
    }
  }

  // --- Le dessin : une petite carte par terre, et son éclat -----------------------------------------

  /** La carte, `l` × `h` pixels par case, aux couleurs de son équipe : le bord blanc, le fond du chandail,
      la bande, et le joueur en ombre. `ech` = la taille d'un pixel (1 par terre, 5 au carnet). */
  function peindreCarte(ctx, c, x, y, ech) {
    const eq = equipe(c.district), fond = eq ? eq.couleurs[0] : '#666666', bande = eq ? eq.couleurs[1] : '#dddddd';
    const px = function (couleur, ix, iy, l, h) { ctx.fillStyle = couleur; ctx.fillRect(x + ix * ech, y + iy * ech, (l || 1) * ech, (h || 1) * ech); };
    // 7 × 9 : le carton blanc, la photo, la bande du nom.
    px('#f4efe2', 0, 0, 7, 9);
    px(fond, 1, 1, 5, 5);
    px('#1c1a22', 3, 2, 1, 1);            // la tête
    px(bande, 2, 3, 3, 2);                // le chandail
    px('#1c1a22', 1, 4, 1, 2);            // le bâton
    px(bande, 1, 7, 5, 1);                // la bande du nom
    B.stats.rects += 6;
  }

  //: ⚠️ L'HIVER (30 sept. 2026, Martin : « la carte blanche se perd sur la neige ») : un carton crème sur la
  //: neige, c'est un carton blanc sur du blanc — on ne voyait plus que la photo, un point de couleur. Tant que
  //: la neige tient (`Saisons.enHiver`, la même règle que les capotes relevées), la carte a un CONTOUR sombre
  //: (le petit creux qu'elle fait dans la neige) et son éclat passe du blanc à l'OR, qui se lit sur le blanc.
  const HIVER = { contour: '#3a3442', eclat: 'rgba(255,178,40,1)' };
  //: ⚠️ LA NUIT (jamais regardée avant le 30 sept.) : la nuit se pose PAR-DESSUS la ville (`Base.fin`), l'éclat
  //: s'y éteignait avec la carte. Il allume donc, le temps de briller, une petite lampe (`lampes`) — un éclat
  //: dans le noir toutes les trois secondes, pas une carte qui luit : rien entre deux éclats.
  const LUEUR = { rayon: 16, alpha: 0.8, nuit: 0.2 };

  //: Le décalage de l'éclat : une carte par son numéro, une bebelle par son rang (jamais deux ensemble).
  function decalage(c) { return c.numero ? c.numero * 37 : 17 + (rangBebelle(c.slug) + 1) * 53; }

  function eclatA(c) {
    const periode = Math.max(60, (regle().scintille_s || 3) * 60);
    const t = ((B.t || 0) + decalage(c)) % periode;
    return t < ECLAT_IMAGES ? (t < ECLAT_IMAGES / 2 ? t : ECLAT_IMAGES - t) : -1;
  }

  /** L'éclat : une croix de lumière au coin (`ex`, `ey`), qui grandit puis s'éteint. */
  function peindreEclat(ctx, k, ex, ey, hiver) {
    const bras = k > 4 ? 3 : k > 2 ? 2 : 1;
    ctx.fillStyle = hiver ? HIVER.eclat : 'rgba(255,250,210,0.95)';
    ctx.fillRect(ex, ey - bras, 1, bras * 2 + 1);
    ctx.fillRect(ex - bras, ey, bras * 2 + 1, 1);
    B.stats.rects += 2;
  }

  function dessiner(ctx, cam) {
    const liste = aTrouver();
    if (!liste.length && !bebellesATrouver().length) return;
    const hiver = typeof Saisons !== 'undefined' && Saisons.enHiver();
    for (const c of liste) {
      const q = pixels(c);
      const x = Math.round(q.x - cam.x - 3), y = Math.round(q.y - cam.y - 4);
      if (x < -12 || y < -12 || x > VW + 12 || y > VH + 12) continue;
      // Par terre, un peu de biais : l'ombre, puis la carte à l'échelle 1 (une tuile en fait 16).
      ctx.fillStyle = 'rgba(0,0,0,0.28)';
      ctx.fillRect(x + 1, y + 9, 7, 1);
      if (hiver) { ctx.fillStyle = HIVER.contour; ctx.fillRect(x - 1, y - 1, 9, 11); B.stats.rects++; }
      peindreCarte(ctx, c, x, y, 1);
      // ⚠️ L'ÉCLAT, discret : quelques images toutes les trois secondes, pas deux cartes à la fois (décalé
      // par le numéro). Une croix de lumière au coin, qui grandit puis s'éteint.
      const k = eclatA(c);
      if (k >= 0) peindreEclat(ctx, k, x + 6, y, hiver);
    }
    // LES BEBELLES : debout par terre, leur ombre ; l'hiver, leur silhouette cernée de sombre (le bonhomme blanc,
    // le chat blanc et le cendrier se perdaient sur la neige comme la carte).
    for (const b of bebellesATrouver()) {
      const q = pixels(b);
      const x = Math.round(q.x - cam.x - 3), y = Math.round(q.y - cam.y - 6);
      if (x < -12 || y < -12 || x > VW + 12 || y > VH + 12) continue;
      ctx.fillStyle = 'rgba(0,0,0,0.3)';
      ctx.fillRect(x, y + 7, 6, 1);
      if (hiver) {
        for (const d of [[-1, 0], [1, 0], [0, -1], [0, 1]]) peindreBebelle(ctx, b, x + d[0], y + d[1], 1, HIVER.contour);
      }
      peindreBebelle(ctx, b, x, y, 1);
      const k = eclatA(b);
      if (k >= 0) peindreEclat(ctx, k, x + 5, y, hiver);
    }
  }

  /** La nuit, l'éclat d'une carte allume une petite lampe le temps qu'il dure (`Base.fin` les pose PAR-DESSUS
      la nuit) ; le jour, rien. En coordonnées d'écran, comme les citrouilles. */
  function lampes(cam) {
    if (typeof Monde === 'undefined' || !Monde.ambianceVue || Monde.ambianceVue().alpha <= LUEUR.nuit) return [];
    const out = [];
    for (const c of aTrouver().concat(bebellesATrouver())) {
      const k = eclatA(c);
      if (k < 0) continue;
      const q = pixels(c), x = q.x - cam.x + 3, y = q.y - cam.y - 4;
      if (x < -20 || y < -20 || x > VW + 20 || y > VH + 20) continue;
      const f = Math.min(1, (k + 1) / (ECLAT_IMAGES / 2));
      out.push({ x: x, y: y, r: LUEUR.rayon, c: 'rgba(255,236,170,' + (LUEUR.alpha * f).toFixed(2) + ')' });
    }
    return out;
  }

  // --- Le debug : aller à une carte qui manque -------------------------------------------------------

  /** La plus proche de (x, y) en pixels, parmi celles qui manquent et ont une place. */
  function plusProche(x, y) {
    let meilleure = null, d = Infinity;
    for (const c of cartes()) {
      if (typeof c.x !== 'number' || trouvee(c.numero)) continue;
      const q = pixels(c), dd = dist2(x, y, q.x, q.y);
      if (dd < d) { d = dd; meilleure = c; }
    }
    return meilleure;
  }

  /** Toutes, d'un coup, en silence (TRICHES) : l'album rempli, sans prime ni paliers. */
  function toutes() {
    let n = 0;
    for (const c of cartes()) if (donner(c.numero, 'debug', true)) n++;
    return n;
  }

  /** Toutes les bebelles, d'un coup, en silence (TRICHES) : l'étagère pleine, sans prime. */
  function toutesLesBebelles() {
    let n = 0;
    for (const b of bebelles()) if (donnerBebelle(b.slug, 'debug', true)) n++;
    return n;
  }

  function oublier() {}

  return { charger, reclamer, poser, catalogue, etatDeLaDemande, cartes, regle, equipe, position, fiche, trouvee, nombre, total,
           parEquipe, aTrouver, pixels, donner, maj, peindreCarte, dessiner, lampes, plusProche, toutes, oublier,
           famille, bebelles, regleBebelles, bebelle, rangBebelle, bebelleTrouvee, nombreBebelles, totalBebelles, masqueBebelles,
           bebellesATrouver, peindreBebelle, donnerBebelle, toutesLesBebelles };
})();
