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
      return (d && d.longueur ? d.longueur / 2 : 14) + 2;
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
      if (contreLeBord(B.bloc.def.bloc.retour, Monde.carte, e)) Jeu.sortirDuBloc();
      return;
    }
    for (const b of liste()) {
      if (!pres(b.passage, Monde.carte, j)) continue;
      charger(b.slug);
      if (cartes[b.slug] && contreLeBord(b.passage, Monde.carte, e)) {
        Jeu.entrerDansLeBloc(b, cartes[b.slug], recul(b.passage, Monde.carte, j));
        return;
      }
    }
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
    return liste().map(function (b) { return { o: b.passage, mot: b.panneau || 'CHEMIN', nom: b.nom }; });
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
  function reprendre(ou) {
    const b = liste().find(function (q) { return q.slug === ou.slug; });
    if (!b) return false;
    charger(b.slug);
    Jeu.transiter([1, 0, 24], function () {
      const def = cartes[b.slug];
      if (!def || B.bloc) return;
      Jeu.passerDansLeBloc(b, def, recul(b.passage, Monde.carte, B.joueur), { x: ou.x, y: ou.y });
    }, null, function () { return !cartes[b.slug]; });
    return true;
  }

  /** Ce que le GPS vise dans un bloc : la sortie, vers la ville. */
  function cibleDeSortie() {
    if (!B.bloc) return null;
    const c = centre(B.bloc.def.bloc.retour, Monde.carte);
    return { x: c.x, y: c.y, nom: 'Vers la ville', couleur: '#7fc4ff' };
  }

  return { init, maj, charger, liste, contreLeBord, recul, marge, porteur, capVersLInterieur, poursuiteAuBord,
           garder, souvenir, enMemoire, oublier, reprendre,
           cibleDeSortie, dessiner, texteDInfo, DELAI_POURSUIVANTS,
           get cartes() { return cartes; }, BORD_PX, PRES, RELANCE };
})();
