/* Bandini — les blocs de carte : des morceaux de monde a part, derriere un fondu au noir.

   Demande de Martin (25 sept. 2026) : « la carte fait un black-out et charge le nouveau
   morceau, et ca continue ». Un bloc est une CARTE A PART (`app/blocs/`), servie par
   `/api/carte/bloc/<slug>` : la ville n'en bouge pas d'un octet. On y passe comme on entre
   dans une piece (`Jeu.entrer`) — la ville mise de cote, la carte chargee au noir, et au
   retour la ville telle qu'on l'a laissee — mais DEHORS : on POUSSE contre un bord de la
   carte, la ou le bloc a son passage.

   ⚠️ Vague 1 (docs/jalons/des-blocs-de-carte-en-extensions.md) : a pied. Vague 2 : au
   volant (le char et TOUT ce qui est dedans passent), a deux (le deuxieme joueur suit), et
   la police qui reprend AU BORD — ses poursuivants passent par le meme passage que toi,
   quelques secondes apres. Le trafic, les passants et la nuit du bloc : vague 3.

   ⚠️ UNE CARTE NE PEUT PAS ARRIVER EN RETARD — comme le texte d'une mission. On la demande
   d'avance, des qu'on approche du passage (`PRES`), et le passage ne s'ouvre qu'une fois
   la carte arrivee : pousser contre le bord avant, c'est pousser contre un bord. */

const Blocs = (function () {
  'use strict';

  const TT = 16;
  //: A cette distance du passage (en tuiles), on demande la carte du bloc d'avance.
  const PRES = 14;
  //: Pousser contre le bord : a moins de tant de pixels du bord de la carte. Longer le
  //: trottoir de ceinture (le joueur au centre de sa tuile, a 8 px) ne declenche rien.
  const BORD_PX = 6;
  //: Ou l'on reapparait en revenant : juste en deca du seuil, sinon on repartirait.
  const RECUL_PX = 8;
  //: Recherche, les poursuivants passent le passage tant d'images apres toi (trois
  //: secondes) — et jamais plus de trois.
  const DELAI_POURSUIVANTS = 180;
  const POURSUIVANTS_MAX = 3;
  //: Apres une demande ratee, on attend tant d'images avant de redemander. ⚠️ Sans ce
  //: delai, un reseau mort etait redemande A CHAQUE IMAGE — soixante requetes par seconde
  //: tant qu'on restait pres du passage.
  const RELANCE = 300;

  let fenetre = null;
  let gabarit = '/api/carte/bloc/SLUG';
  const cartes = {};      // slug -> la carte du bloc, une fois arrivee
  const enRoute = {};     // slug -> vrai pendant qu'elle vole (on ne la demande jamais deux fois)
  const ratee = {};       // slug -> l'image (`B.t`) de la derniere demande ratee
  //: slug -> ce qu'on a laisse dans le bloc (ses arbres, le char gare devant le chalet) :
  //: un bloc se souvient le temps de la partie, comme la ville (`Jeu.quitterLeBloc`).
  let memoire = {};

  function init(w, racine) {
    fenetre = w;
    const g = racine && racine.dataset && racine.dataset.urlBloc;
    if (g) gabarit = g;
  }

  function liste() { return (B.defs && B.defs.blocs) || []; }

  /** Demande la carte d'un bloc — une fois. ⚠️ Un reseau qui tombe OUBLIE la demande :
      on redemandera en repassant, le passage n'est pas ferme pour la partie. */
  function charger(slug) {
    if (cartes[slug] || enRoute[slug] || !fenetre || !fenetre.fetch) return;
    if (ratee[slug] !== undefined && B.t - ratee[slug] < RELANCE) return;
    enRoute[slug] = true;
    fenetre.fetch(gabarit.replace('SLUG', slug))
      .then(function (r) { if (!r.ok) throw new Error('bloc ' + slug + ' : ' + r.status); return r.json(); })
      .then(function (d) { cartes[slug] = d; delete enRoute[slug]; delete ratee[slug]; })
      .catch(function () { delete enRoute[slug]; ratee[slug] = B.t; });
  }

  /** Les bornes (en tuiles) d'une ouverture sur un bord, dans une carte de `w` x `h`. */
  function bornes(o, w, h) {
    if (o.bord === 'nord') return { x0: o.de, x1: o.de + o.l, y0: 0, y1: 1 };
    if (o.bord === 'sud') return { x0: o.de, x1: o.de + o.l, y0: h - 1, y1: h };
    if (o.bord === 'ouest') return { x0: 0, x1: 1, y0: o.de, y1: o.de + o.l };
    return { x0: w - 1, x1: w, y0: o.de, y1: o.de + o.l };
  }

  /** A quelle distance du bord `e` le touche : un pieton a son rayon, un char a sa
      DEMI-LONGUEUR (mesure au banc : l'auto s'arrete a 14 px du bord nord, le camion a 20,
      la moto a 10, le velo a 8 — la moitie de leur `longueur`). ⚠️ Un char qui longe le
      bord n'y presente que sa demi-largeur : il ne passe pas, c'est voulu. */
  function marge(e) {
    if (e && e.type === 'vehicule') {
      const d = Vehicules.vehiculeDef(e.slug);
      // ⚠️ PLUS UNE IMAGE DE ROUTE (27 sept. 2026) : le rang s'ouvre au bout d'une vraie rue, et on y
      // entre lancé. Le choc contre le bord se joue dans la physique, AVANT cette image : une moto à
      // 2,7 px/image touchait le bord et éjectait son pilote, qui passait seul, sans elle.
      return (d && d.longueur ? d.longueur / 2 : 14) + 2 + Math.abs(e.vitesse || 0);
    }
    return BORD_PX;
  }

  /** Qui passe le bord pour le joueur : son char s'il conduit, lui sinon. */
  function porteur(j) { return (j && j.dansVehicule) || j; }

  /** `e` (un pieton, ou le char qu'on conduit) pousse-t-il contre ce bord, dans l'ouverture ?

      ⚠️ Un CHAR doit aussi lui FAIRE FACE (a 45 degres pres) : sur le trottoir de ceinture,
      une auto qui longe le bord roule a 8 px de lui, sous son seuil de demi-longueur — sans
      cette condition, on passait en roulant le long du trottoir. */
  function contreLeBord(o, carte, e) {
    const w = carte.w, h = carte.h, b = bornes(o, w, h), m = marge(e);
    if (e.type === 'vehicule') {
      const dehors = capVersLInterieur(o) + Math.PI;
      const ecart = Math.atan2(Math.sin(e.angle - dehors), Math.cos(e.angle - dehors));
      if (Math.abs(ecart) > Math.PI / 4) return false;
    }
    const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
    if (o.bord === 'nord' || o.bord === 'sud') {
      if (tx < b.x0 || tx >= b.x1) return false;
      return o.bord === 'nord' ? e.y <= m : e.y >= h * TT - m;
    }
    if (ty < b.y0 || ty >= b.y1) return false;
    return o.bord === 'ouest' ? e.x <= m : e.x >= w * TT - m;
  }

  /** Le point ou l'on revient par cette ouverture : au meme endroit le long du bord (on
      ressort la ou l'on est entre, `le_long`), en deca du seuil de `e` — un char recule
      de sa demi-longueur, sinon il repartirait aussitot. */
  function recul(o, carte, e, leLong) {
    const w = carte.w * TT, h = carte.h * TT, b = bornes(o, carte.w, carte.h);
    const d = marge(e) + RECUL_PX;
    const borne = function (v, a0, a1) { return Math.max(a0 * TT + 4, Math.min(a1 * TT - 4, v)); };
    const long = leLong === undefined ? (o.bord === 'nord' || o.bord === 'sud' ? e.x : e.y) : leLong;
    if (o.bord === 'nord') return { x: borne(long, b.x0, b.x1), y: d };
    if (o.bord === 'sud') return { x: borne(long, b.x0, b.x1), y: h - d };
    if (o.bord === 'ouest') return { x: d, y: borne(long, b.y0, b.y1) };
    return { x: w - d, y: borne(long, b.y0, b.y1) };
  }

  /** Le cap qui tourne le dos a ce bord : vers l'interieur de la carte. */
  function capVersLInterieur(o) {
    return { nord: Math.PI / 2, sud: -Math.PI / 2, ouest: 0, est: Math.PI }[o.bord];
  }

  /** Ou l'on reviendra en ville en sortant de ce bloc : juste en deca de son passage (`recul`) — ou, pour un
      SOUS-SOL (pas de passage, un `seuil`), devant son rideau, a quatre tuiles de la facade (la chaussee), le nez
      vers la rue (`cap`). Null si le rideau n'est pas dans la carte courante. */
  function retourEnVille(b, e) {
    if (b.passage) return recul(b.passage, Monde.carte, e);
    const pg = b.seuil && Monde.porteDeGarage(b.seuil);
    if (!pg) return null;
    const baie = Monde.baieDeLaPorteDeGarage(pg);
    return { x: baie.x, y: baie.y + 2 * TT + 8, cap: Math.PI / 2 };
  }

  /** Le centre d'une ouverture, en pixels — ce que le GPS vise pour ressortir. */
  function centre(o, carte) {
    const b = bornes(o, carte.w, carte.h);
    return { x: (b.x0 + b.x1) / 2 * TT, y: (b.y0 + b.y1) / 2 * TT };
  }

  function pres(o, carte, j) {
    const c = centre(o, carte);
    return Math.hypot(c.x - j.x, c.y - j.y) < PRES * TT;
  }

  /** Une image : on demande d'avance, et on passe quand on pousse contre le bord. */
  function maj() {
    if (B.etat !== 'jeu' || B.transition || B.interieur || B.cinema || B.scene) return;
    const j = B.joueur;
    if (!j || j.vie <= 0) return;
    majPoursuivants();
    const e = porteur(j);
    if (B.bloc) {
      const bb = B.bloc.def.bloc;
      // ⚠️ UN RETOUR QUI MÈNE À UN AUTRE BLOC (`vers` : le −2 du sous-sol remonte au −1) ne ramène pas en ville.
      if (contreLeBord(bb.retour, Monde.carte, e)) {
        if (bb.retour.vers) passerLaRampe(bb.retour); else Jeu.sortirDuBloc();
        return;
      }
      // Ses rampes vers un autre bloc (le −1 descend au −2) — une rampe fermee (sa grille) ne mene nulle part.
      for (const o of bb.rampes || []) {
        if (contreLeBord(o, Monde.carte, e) && (typeof Souterrain === 'undefined' || Souterrain.rampeOuverte(o))) { passerLaRampe(o); return; }
      }
      return;
    }
    for (const b of liste()) {
      if (!b.passage || !pres(b.passage, Monde.carte, j)) continue;
      charger(b.slug);
      if (cartes[b.slug] && contreLeBord(b.passage, Monde.carte, e)) {
        Jeu.entrerDansLeBloc(b, cartes[b.slug], recul(b.passage, Monde.carte, j));
        return;
      }
    }
  }

  /** Une rampe d'un bloc a l'autre : on arrive a son `arrivee`, tourne vers l'interieur (le dos a la rampe d'en
      face), et les pneus crissent en echo sur le beton. */
  function passerLaRampe(o) {
    if (B.transition) return;
    const cap = capVersLInterieur(o);
    if (typeof Son !== 'undefined' && Son.SFX.rampe) Son.SFX.rampe();
    Jeu.changerDeBloc(o.vers, { x: o.arrivee.x * TT + 8, y: o.arrivee.y * TT + 8 }, cap);
  }

  /** Recherche, on passe un bord : les agents d'avant restent de leur cote, et ceux qui te
      suivent passent PAR LE MEME BORD, `DELAI_POURSUIVANTS` images apres toi. Pose au noir
      par `Jeu` (`B.passagePolice`) ; ils naissent ici, dans la carte ou l'on est arrive. */
  function majPoursuivants() {
    const pp = B.passagePolice;
    if (!pp || B.t < pp.t) return;
    B.passagePolice = null;
    if (B.recherche.etoiles <= 0) return;
    const j = B.joueur;
    for (let i = 0; i < pp.n; i++) {
      const a = Police.creerAgent(pp.x + (i - (pp.n - 1) / 2) * 14, pp.y, 'poursuit');
      a.but = { x: j.x, y: j.y };
    }
    B.recherche.dernierVu = { x: pp.x, y: pp.y, t: B.t };
  }

  /** La poursuite qui reprendra au bord `o` de la carte courante (au noir, en passant). */
  function poursuiteAuBord(o, carte) {
    const r = B.recherche;
    if (r.etoiles <= 0) { B.passagePolice = null; return; }
    const c = recul(o, carte, { type: 'pieton', x: centre(o, carte).x, y: centre(o, carte).y });
    B.passagePolice = { t: B.t + DELAI_POURSUIVANTS, n: Math.min(POURSUIVANTS_MAX, r.etoiles), x: c.x, y: c.y };
    r.dernierVu = { x: c.x, y: c.y, t: B.t };
  }

  /** Les ouvertures a signaler dans la carte courante : en ville, les passages ; dans un
      bloc, son retour. Chacune avec son mot et le sens ou l'on pousse. */
  function ouvertures() {
    if (B.bloc) {
      const def = B.bloc.def.bloc;
      return [{ o: def.retour, mot: def.panneau || 'VILLE', nom: 'Vers la ville' }];
    }
    // ⚠️ Un sous-sol (le garage souterrain) n'a pas de passage : aucune plaque en ville.
    return liste().filter(function (b) { return b.passage; })
      .map(function (b) { return { o: b.passage, mot: b.panneau || 'CHEMIN', nom: b.nom }; });
  }

  /** Le centre de la plaque d'une ouverture : A PLAT, dans la tuile du bord, au milieu de
      l'ouverture — on marche dessus. ⚠️ Pas un poteau : l'ouverture est sur la PREMIERE
      rangee de la carte, et la camera ne monte pas plus haut — un panneau plante la
      depassait du monde, coupe. Et pas a cote : au bord du chemin, les arbres la cachaient. */
  function piedDuPanneau(o, carte) {
    const c = centre(o, carte);
    if (o.bord === 'nord') return { x: c.x, y: 3 };
    if (o.bord === 'sud') return { x: c.x, y: carte.h * TT - 13 };
    if (o.bord === 'ouest') return { x: 20, y: c.y - 5 };
    return { x: carte.w * TT - 20, y: c.y - 5 };
  }

  /* ⚠️ LES CHEMINS DU BLOC (la route en lacets du rang, docs/jalons/une-route-en-lacets-vers-le-chalet.md) :
     un ruban de gravier au bord LISSE, par-dessus des tuiles `§` peintes en herbe. Appele juste apres
     `Monde.dessinerSol`, donc SOUS la neige, le verglas et les traces de pneus : l'hiver le blanchit comme
     le reste. Le grain est celui du `g` des allees, en motif ancre au monde (il ne glisse pas avec la
     camera). */
  //: La lisiere d'herbe foulee deborde du ruban de tant de pixels de chaque cote.
  const LISIERE_PX = 6;
  //: Les ornieres : a cette part de la demi-largeur, de chaque cote du milieu.
  const ORNIERES = 0.45;
  let motif = null;
  function motifDuChemin(ctx) {
    if (motif) return motif;
    const c = document.createElement('canvas');
    c.width = c.height = 4 * TT;
    const g = c.getContext('2d');
    for (let j = 0; j < 4; j++) for (let i = 0; i < 4; i++) {
      g.save(); g.translate(i * TT, j * TT); TUILES['g'](g, hash2(i, j) & 15, TT); g.restore();
    }
    motif = ctx.createPattern(c, 'repeat');
    return motif;
  }
  /** La meme courbe, decalee de `d` pixels sur sa normale (les ornieres). */
  function decaler(pts, d) {
    return pts.map(function (p, i) {
      const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
      const dx = b[0] - a[0], dy = b[1] - a[1], n = Math.hypot(dx, dy) || 1;
      return [p[0] - dy / n * d, p[1] + dx / n * d];
    });
  }
  function trait(ctx, pts, largeur, style) {
    ctx.strokeStyle = style; ctx.lineWidth = largeur; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.stroke();
  }
  function dessinerChemins(ctx, cam) {
    const b = B.bloc && B.bloc.def && B.bloc.def.bloc;
    if (B.interieur || !b || !b.chemins || !b.chemins.length) return;
    ctx.save();
    ctx.translate(-Math.round(cam.x), -Math.round(cam.y));      // tout en pixels du monde : le motif s'y ancre
    for (const ch of b.chemins) {
      if (!ch.ornieres) {
        const d = ch.largeur_px / 2 * ORNIERES;
        ch.ornieres = [decaler(ch.points, -d), decaler(ch.points, d)];
      }
      trait(ctx, ch.points, ch.largeur_px + 2 * LISIERE_PX, 'rgba(58,82,40,0.30)');   // l'herbe foulee
      trait(ctx, ch.points, ch.largeur_px, motifDuChemin(ctx));                       // le gravier
      for (const o of ch.ornieres) trait(ctx, o, 3, 'rgba(126,110,78,0.55)');        // les ornieres
      B.stats.rects += 4;
    }
    ctx.restore();
  }

  /** Une plaque de bois, le mot, et une fleche vers le bord : on sait ou pousser. */
  function dessiner(ctx, cam) {
    if (B.interieur || !Monde.carte) return;
    for (const u of ouvertures()) {
      const p = piedDuPanneau(u.o, Monde.carte);
      const larg = Atlas.largeurTexte(u.mot, 1) + 12;
      // La plaque s'etend VERS l'interieur de la carte a l'est, pour ne pas en sortir.
      const px = Math.round(p.x - larg / 2 - cam.x);
      const py = Math.round(p.y - cam.y);
      if (px < -60 || px > VW + 60 || py < -20 || py > VH + 20) continue;
      ctx.fillStyle = '#4a3218'; ctx.fillRect(px - 1, py - 1, larg + 2, 12);    // le cadre
      ctx.fillStyle = '#8a5a2b'; ctx.fillRect(px, py, larg, 10);               // la planche
      ctx.fillStyle = '#b07a3e'; ctx.fillRect(px, py, larg, 1);
      Atlas.texte(ctx, u.mot, px + 2, py + 3, '#f4e4c1', 1);
      // La fleche, vers le bord ou l'on pousse.
      const fx = px + larg - 7, fy = py + 5;
      ctx.fillStyle = '#f4e4c1';
      if (u.o.bord === 'nord') { ctx.fillRect(fx + 2, fy - 3, 1, 6); ctx.fillRect(fx + 1, fy - 2, 3, 1); ctx.fillRect(fx, fy - 1, 5, 1); }
      else if (u.o.bord === 'sud') { ctx.fillRect(fx + 2, fy - 3, 1, 6); ctx.fillRect(fx + 1, fy + 1, 3, 1); ctx.fillRect(fx, fy, 5, 1); }
      else if (u.o.bord === 'ouest') { ctx.fillRect(fx - 1, fy, 6, 1); ctx.fillRect(fx, fy - 1, 1, 3); ctx.fillRect(fx + 1, fy - 2, 1, 5); }
      else { ctx.fillRect(fx - 1, fy, 6, 1); ctx.fillRect(fx + 4, fy - 1, 1, 3); ctx.fillRect(fx + 3, fy - 2, 1, 5); }
      B.stats.rects += 9;
    }
    dessinerCheminees(ctx, cam);
  }

  /** Les cheminées du bloc où l'on est (le chalet du rang), en pixels : le haut de la souche. */
  function cheminees() {
    const b = B.bloc && B.bloc.def && B.bloc.def.bloc;
    return (b && b.cheminees) || [];
  }

  /** La souche de pierre, sur le toit : deux tuiles de large, un peu plus haute que large pour
      qu'on la voie DEBOUT sur le versant, son chapeau de pierre plate, et l'ombre qu'elle jette
      sur les bardeaux. Peinte par-dessus le toit (le plan n'en sait rien). */
  function dessinerCheminees(ctx, cam) {
    for (const c of cheminees()) {
      if (c.genre === 'tole' || c.genre === 'lanterneau') { dessinerEvaporateur(ctx, cam, c); continue; }
      const x = Math.round(c.x * TT - cam.x) + 3, y = Math.round(c.y * TT - cam.y) - 4, l = c.l * TT - 6, h = TT + 2;
      if (x < -40 || x > VW + 40 || y < -40 || y > VH + 40) continue;
      ctx.fillStyle = 'rgba(0,0,0,0.30)'; ctx.fillRect(x + 3, y + h, l, 5);            // l'ombre sur le toit
      ctx.fillStyle = '#6e685e'; ctx.fillRect(x, y, l, h);                            // le mortier
      const teintes = ['#8f897d', '#a39c8e', '#7d776c', '#9a8a70'];
      for (let r = 0; r * 4 < h; r++) {                                               // les pierres, en quinconce
        for (let k = 0; k * 6 < l + 6; k++) {
          const px = x + k * 6 - (r % 2 ? 3 : 0);
          const x0 = Math.max(px + 1, x), x1 = Math.min(px + 6, x + l);
          if (x1 <= x0) continue;
          ctx.fillStyle = teintes[(r * 3 + k) % teintes.length];
          ctx.fillRect(x0, y + r * 4 + 1, x1 - x0, Math.min(3, h - r * 4 - 1));
        }
      }
      ctx.fillStyle = '#5a534a'; ctx.fillRect(x - 1, y - 2, l + 2, 3);               // le chapeau
      ctx.fillStyle = '#b3ada2'; ctx.fillRect(x - 1, y - 2, l + 2, 1);
      ctx.fillStyle = '#1b1614'; ctx.fillRect(x + 3, y - 1, l - 6, 2);               // la bouche, noire de suie
      B.stats.rects += 6;
    }
  }

  /** La cabane à sucre (docs/jalons/la-cabane-a-sucre-pour-vrai.md) : la cheminée de TÔLE de l'évaporateur
      (un tuyau noir, son chapeau chinois), et le LANTERNEAU du faîte — la petite toiture à persiennes d'où
      sort la vapeur du sirop qui bout. */
  function dessinerEvaporateur(ctx, cam, c) {
    const x = Math.round(c.x * TT - cam.x), y = Math.round(c.y * TT - cam.y), l = c.l * TT;
    if (x < -60 || x > VW + 60 || y < -60 || y > VH + 60) return;
    if (c.genre === 'tole') {
      ctx.fillStyle = 'rgba(0,0,0,0.30)'; ctx.fillRect(x + 8, y + 12, 5, 6);            // l'ombre
      ctx.fillStyle = '#2a2c30'; ctx.fillRect(x + 5, y - 10, 5, 22);                    // le tuyau
      ctx.fillStyle = '#4a4d54'; ctx.fillRect(x + 5, y - 10, 1, 22);
      ctx.fillStyle = '#3a3d44'; ctx.fillRect(x + 4, y + 2, 7, 1); ctx.fillRect(x + 4, y - 4, 7, 1);   // les brides
      ctx.fillStyle = '#1b1c20'; ctx.fillRect(x + 2, y - 14, 11, 2); ctx.fillRect(x + 4, y - 16, 7, 2);  // le chapeau
      B.stats.rects += 8;
      return;
    }
    // Le lanterneau : un petit toit sur des persiennes, à cheval sur le faîte.
    ctx.fillStyle = 'rgba(0,0,0,0.28)'; ctx.fillRect(x + 4, y + 12, l - 2, 4);
    ctx.fillStyle = '#6b4a2a'; ctx.fillRect(x + 2, y + 2, l - 4, 10);                   // les planches
    ctx.fillStyle = '#2e1d10'; for (let k = 0; k < 3; k++) ctx.fillRect(x + 4, y + 4 + k * 3, l - 8, 1);   // les persiennes
    ctx.fillStyle = '#5a534a'; ctx.fillRect(x, y - 2, l, 5);                            // son toit
    ctx.fillStyle = '#7d766b'; ctx.fillRect(x, y - 2, l, 1);
    B.stats.rects += 7;
  }

  /** Une cheminée fume-t-elle ? Celles de la cabane seulement quand on fait bouillir (`Cabane`). */
  function fume(c) { return !c.sucres || (typeof Cabane !== 'undefined' && Cabane.onFaitBouillir()); }

  //: La vapeur du lanterneau : plus de bouffées, plus blanches, plus grosses, et qui montent plus vite.
  const VAPEUR = { bouffees: 12, vie: 130, monte: 70, derive: 30, rayon: 16 };

  //: La fumée : combien de bouffées à la fois, leur vie (en images), combien elles montent et
  //: dérivent (le vent vient de l'ouest), et leur plus grand rayon.
  const FUMEE = { bouffees: 8, vie: 170, monte: 56, derive: 46, rayon: 10 };
  /** La fumée qui sort de la cheminée : des bouffées grises qui montent, grossissent, dérivent vers
      l'est et s'effacent. ⚠️ D'après `B.t` seulement — jamais un dé : deux images pareilles, deux
      fumées pareilles, et le banc la juge. Au-dessus des toits et des gens (`Jeu.rendre`). */
  function dessinerFumees(ctx, cam) {
    for (const c of cheminees()) {
      if (!fume(c)) continue;
      const F = c.genre === 'lanterneau' ? VAPEUR : FUMEE;
      const teinte = c.genre === 'lanterneau' ? '245,245,242,' : c.genre === 'tole' ? '150,150,152,' : '205,205,200,';
      const bx = c.x * TT + c.l * TT / 2 - cam.x, by = c.y * TT - (c.genre === 'tole' ? 16 : 6) - cam.y;
      if (bx < -80 || bx > VW + 80 || by < -120 || by > VH + 40) continue;
      for (let i = 0; i < F.bouffees; i++) {
        const p = (((B.t || 0) + i * F.vie / F.bouffees) % F.vie) / F.vie;   // 0 à la bouche, 1 dissipée
        const x = bx + F.derive * p * p + Math.sin(p * 6 + i) * 2 + (c.genre === 'lanterneau' ? ((i * 7) % 5 - 2) * c.l * 2 * (1 - p) : 0);
        const y = by - F.monte * p;
        const r = 2 + (F.rayon - 2) * p;
        const a = (c.genre === 'lanterneau' ? 0.7 : 0.55) * (1 - p) * Math.min(1, p * 6);
        ctx.fillStyle = 'rgba(' + teinte + a.toFixed(3) + ')';
        ctx.fillRect(Math.round(x - r), Math.round(y - r * 0.8), Math.round(2 * r), Math.round(1.6 * r));
        ctx.fillRect(Math.round(x - r * 0.7), Math.round(y - r), Math.round(1.4 * r), Math.round(2 * r));
        B.stats.rects += 2;
      }
    }
  }

  const SENS = { nord: 'LE NORD', sud: 'LE SUD', est: "L'EST", ouest: "L'OUEST" };

  /** Pres d'un panneau, la ligne du bas dit ou il mene et comment y aller. */
  function texteDInfo(j) {
    if (!j || B.interieur || !Monde.carte) return null;
    for (const u of ouvertures()) {
      const p = piedDuPanneau(u.o, Monde.carte);
      if (Math.abs(p.x - j.x) + Math.abs(p.y - j.y) > 4 * TT) continue;
      return (u.nom + ' : pousse vers ' + SENS[u.o.bord]).toUpperCase();
    }
    return null;
  }

  /** Ce qu'on laisse dans un bloc en le quittant. */
  function garder(slug, entites) { memoire[slug] = entites; }

  /** Ce qu'on y avait laisse, ou null la premiere fois — et on le reprend (il revient dans
      `B.entites`, il ne reste pas a deux endroits). */
  function souvenir(slug) {
    const s = memoire[slug] || null;
    delete memoire[slug];
    return s;
  }

  /** Ce qu'on a laisse dans un bloc, sans le reprendre — ce que la sauvegarde regarde. */
  function enMemoire(slug) { return memoire[slug] || null; }

  /** Une partie qui commence ne se souvient d'aucun bloc. */
  function oublier() { memoire = {}; B.passagePolice = null; }

  /** Le reveil d'une partie endormie dans un bloc (`partie.bloc`, la planque du chalet) :
      au noir TOUT DE SUITE, le noir tient le temps que sa carte arrive (`Jeu.transiter`,
      `attente`), puis on est dans le bloc, a l'endroit ou l'on s'est couche. ⚠️ Si elle
      n'arrive pas (hors ligne, un bloc retire), on se reveille au passage EN VILLE : la
      sauvegarde y a pose `p.x`/`p.y`, et c'est la que `commencer` nous a mis. */
  function reprendre(ou) { return sauter(ou.slug, { x: ou.x, y: ou.y }); }

  /** Passe dans le bloc `slug` depuis la ville, d'ou qu'on y soit, au noir : le noir tient
      le temps que sa carte arrive, puis on est a `ici` dans le bloc (a son arrivee sans
      `ici`), et `apres()` se joue. Le retour se fait a son passage, comme si on y etait
      entre. Le reveil au chalet (`reprendre`) et la triche ENDROITS CLÉS passent par ici. */
  function sauter(slug, ici, apres) {
    const b = liste().find(function (q) { return q.slug === slug; });
    if (!b) return false;
    charger(b.slug);
    Jeu.transiter([1, 0, 24], function () {
      if (entrerAuNoir(b.slug, ici) && apres) apres();
    }, null, function () { return !cartes[b.slug]; });
    return true;
  }

  /** Au noir : passe dans le bloc `slug` si sa carte est la, a `ici` (a son arrivee sans lui).
      Rend false sans rien faire si la carte manque ou qu'on est deja dans un bloc. `sauter` et
      les missions sur place (`SurPlace.sauter`, qui tient son propre fondu) passent par ici. */
  function entrerAuNoir(slug, ici) {
    const b = liste().find(function (q) { return q.slug === slug; }), def = cartes[slug];
    if (!b || !def || B.bloc) return false;
    const retour = retourEnVille(b, B.joueur);
    if (!retour) return false;
    Jeu.passerDansLeBloc(b, def, retour, ici || null);
    return true;
  }

  /** Ce que le GPS vise dans un bloc : la sortie, vers la ville. */
  function cibleDeSortie() {
    if (!B.bloc) return null;
    const r = B.bloc.def.bloc.retour, c = centre(r, Monde.carte);
    return { x: c.x, y: c.y, nom: r.vers ? 'Vers la rampe' : 'Vers la ville', couleur: '#7fc4ff' };
  }

  return { dessinerFumees, cheminees, fume, FUMEE, VAPEUR, init, maj, charger, liste, sauter, entrerAuNoir, contreLeBord, recul, retourEnVille, marge, porteur, capVersLInterieur, poursuiteAuBord,
           garder, souvenir, enMemoire, oublier, reprendre,
           cibleDeSortie, dessiner, dessinerChemins, texteDInfo, DELAI_POURSUIVANTS,
           get cartes() { return cartes; }, BORD_PX, PRES, RELANCE };
})();
