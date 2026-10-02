/* Bandini — le grand garage souterrain, sous le Garage Rocco Bandini (docs/jalons/le-grand-garage-souterrain.md).

   Martin, 30 sept. 2026 : « le garage Bandini doit pouvoir stocker des vehicules que nous pourrons reprendre
   apres dans un grand garage souterrain ». Un BLOC DE CARTE sans passage en ville (`app/blocs/souterrain.py`) :
   on y descend au volant par le rideau de Ti-Guy (DESCENDRE AU SOUS-SOL), ou a pied par l'ascenseur de la piece
   du garage ; on remonte la rampe, et on est devant le rideau.

   ⚠️ LES CHARS RANGES VIVENT DANS LA PARTIE (`partie.souterrain.cases`), JAMAIS DANS LA MEMOIRE DU BLOC :
   `garnir` les pose a chaque descente, `ranger` les reecrit en remontant et a chaque sauvegarde. La ville oublie
   un char gare loin (`Vehicules.peupler`) ; celui-ci, jamais. */

const Souterrain = (function () {
  'use strict';

  const TT = 16;
  const SLUG = 'souterrain';
  //: Ses niveaux : le −1 (le bloc `souterrain`) et le −2 (`souterrain_2`, vague 2), deux blocs a part.
  const NIVEAUX = ['souterrain', 'souterrain_2'];

  /** Ce bloc-ci est-il un niveau du sous-sol ? */
  function est(slug) { return NIVEAUX.indexOf(slug) >= 0; }

  /** Y est-on ? */
  function ici() { return !!(B.bloc && est(B.bloc.slug)); }

  /** Les niveaux achetes (1, ou 2 une fois le −2 ouvert). */
  function niveaux() { return (B.partie.souterrain && B.partie.souterrain.niveaux) || 1; }

  /** Une rampe interieure se prend-elle ? Celle qui descend au −2 a sa grille tant qu'il n'est pas achete. */
  function rampeOuverte(o) { return !o.achat || niveaux() >= o.achat; }

  //: Les cases d'un niveau, et de tout le sous-sol (`app/blocs/souterrain.py`, les memes nombres).
  const PAR_NIVEAU = 10, CASES_MAX = 20;

  /** Les cases ouvertes : dix par niveau achete. */
  function ouvertes() { return PAR_NIVEAU * niveaux(); }
  /** Les cases ouvertes ou dort un char. */
  function occupees() { return B.partie.souterrain.cases.slice(0, ouvertes()).filter(Boolean).length; }
  function plein() { return occupees() >= ouvertes(); }

  /** Ce qu'on ecrit d'un char : comme le char de la planque, sans position. */
  function fiche(v) {
    return { slug: v.slug, sprite: v.sprite, couleur: v.couleur, vie: v.vie, vole: !!v.vole, aToi: !!v.aToi, mods: Garage.fiche(v) };
  }

  /** La case (son rang) sous le centre de ce char, ou -1. */
  function caseSous(cases, v) {
    for (let k = 0; k < cases.length; k++) {
      const q = cases[k];
      if (v.x >= q.x * TT && v.x < (q.x + q.l) * TT && v.y >= q.y * TT && v.y < (q.y + q.h) * TT) return k;
    }
    return -1;
  }

  /** Reecrit, dans `partie.souterrain.cases`, les cases de CE niveau d'apres les chars de `entites` : chacun sur SA
      case s'il y est (et qu'elle est ouverte et libre), les autres — laisses dans l'allee — gares par Ti-Guy sur la
      premiere case libre de ce niveau, sinon de l'autre. Les cases de l'autre niveau ne bougent pas. Une epave ne se
      range pas. Rend ce qui n'est pas un char : ce que le bloc peut garder (`Blocs.garder`).
      ⚠️ Le rang d'une case dans la partie est son numero moins un (`q.n − 1` : P11 est le rang 10).
      ⚠️ Ne retire rien : la sauvegarde l'appelle en plein sous-sol, les chars restent ou ils sont. */
  function ranger(entites, def) {
    const cases = def.bloc.souterrain.cases, n = ouvertes();
    const neuf = B.partie.souterrain.cases.slice();
    while (neuf.length < CASES_MAX) neuf.push(null);
    const ceux = cases.map(function (q) { return q.n - 1; });
    for (const k of ceux) neuf[k] = null;
    const reste = [], sansPlace = [];
    for (const e of entites) {
      if (e.type !== 'vehicule') { reste.push(e); continue; }
      if (e.etat === 'epave') continue;
      const i = caseSous(cases, e), k = i >= 0 ? ceux[i] : -1;
      if (k >= 0 && k < n && !neuf[k]) neuf[k] = fiche(e); else sansPlace.push(e);
    }
    for (const e of sansPlace) {
      let k = ceux.find(function (r) { return r < n && !neuf[r]; });
      if (k === undefined) { k = 0; while (k < n && neuf[k]) k++; }
      if (k < n) neuf[k] = fiche(e);
    }
    B.partie.souterrain.cases = neuf;
    return reste;
  }

  /** Pose les chars ranges sur leurs cases, a la descente. ⚠️ `couleur` DONNEE a `Vehicules.creer` : un char ne
      sans couleur tire un de, et tout le hasard de la partie glisse. */
  function garnir(def) {
    const n = ouvertes();
    def.bloc.souterrain.cases.forEach(function (q) {
      const k = q.n - 1, c = B.partie.souterrain.cases[k];
      if (!c || k >= n || !Vehicules.vehiculeDef(c.slug)) return;
      const v = Vehicules.creer(c.slug, (q.x + q.l / 2) * TT, (q.y + q.h / 2) * TT, q.cap,
                                { etat: 'stationne', sprite: c.sprite, couleur: c.couleur });
      if (!v) return;
      if (c.couleur) v.swaps = nuances(c.couleur);
      Garage.poser(v, c.mods);
      v.vie = Math.max(1, c.vie || v.vieMax); v.vole = !!c.vole; v.aToi = !!c.aToi;
      // Comme le char d'une planque : l'hiver, le balayage des deux-roues remisees ne l'emporte pas.
      v.aLaPlanque = true;
    });
  }

  /** Pourquoi ce char ne descend pas — la raison, telle qu'elle s'ecrit a la ligne du menu — ou null. */
  function refus(v) {
    if (!Missions.possede(Missions.proprieteDe('garage'))) return 'ACHÈTE LE GARAGE D’ABORD';
    if (B.recherche.etoiles > 0) return 'SÈME LA POLICE D’ABORD';
    if (v.mission || v.aQui) return 'CE CHAR-LÀ N’EST PAS À TOI';
    if (v.def && v.def.eau) return 'UN BATEAU ? DANS UN GARAGE ?';
    if (v.remorque) return 'DÉCROCHE CE QUE TU TIRES D’ABORD';
    if (plein()) return 'SOUS-SOL PLEIN — ' + occupees() + '/' + ouvertes();
    return null;
  }

  /** DESCENDRE AU SOUS-SOL, du menu du rideau : l'atelier se defait (s'il tenait le char sous le toit), le char est
      « servi » (le menu ne le rattrape pas en remontant), et le bloc se charge au noir. ⚠️ Pendant le fondu, le
      jeu est fige (`Jeu.maj`) : le rideau n'a rien a garder. */
  function descendre(v, pg) {
    const r = refus(v);
    if (r) { Hud.message(r, 150); Son.SFX.erreur(); return false; }
    if (pg && pg.dedans === v) { pg.dedans = null; pg.phase = null; pg.admis = null; }
    v.atelier = null;
    if (pg) pg.servi = v;
    Son.SFX.rampe();
    return Blocs.sauter(SLUG, null, null);
  }

  //: Le fondu de l'ascenseur : celui d'un etage (`Jeu`, FONDU_ETAGE).
  const FONDU_ASCENSEUR = [20, 16];

  /** Devant l'ascenseur d'un niveau, en pixels : la rangee ou l'on attend, au milieu des portes. */
  function devantLAscenseur(def) {
    const s = def.bloc.souterrain.ascenseur;
    return { x: (s.x + s.l / 2) * TT, y: s.y * TT + 8 };
  }

  /** Les arrets de l'ascenseur, d'ou l'on est (`ici` : 'garage', ou le slug d'un niveau) : un menu une fois le −2
      ouvert (GARAGE · −1 · −2, l'arret courant eteint) ; sinon l'aller simple, comme a la vague 1. */
  function ascenseur(depuis) {
    if (niveaux() < 2) return depuis === 'garage' ? allerA(NIVEAUX[0]) : monterAPied();
    const arrets = [['GARAGE', 'garage'], ['SOUS-SOL −1', NIVEAUX[0]], ['SOUS-SOL −2', NIVEAUX[1]]];
    Hud.ouvrirMenu({ titre: 'L’ASCENSEUR', largeur: 220, hauteur: 90, items: arrets.map(function (a) {
      const la = a[1] === depuis;
      return { libelle: a[0], detail: la ? 'ICI' : '', actif: !la, faire: function () {
        Hud.fermerMenu();
        if (a[1] === 'garage') monterAPied(); else allerA(a[1]);
        return false;
      } };
    }) });
    return true;
  }

  /** De la piece du garage, a pied : au noir, la piece se quitte et le sous-sol se charge, et l'on sort de
      l'ascenseur du −1 (ou du −2). Le noir tient le temps que la carte arrive (`attente`). */
  function descendreAPied() {
    if (!Missions.possede(Missions.proprieteDe('garage'))) {
      Hud.message('LE SOUS-SOL EST AU PROPRIO — ACHÈTE LE GARAGE', 150); Son.SFX.erreur();
      return true;
    }
    // Comme au rideau : pas de police au sous-sol, on ne l'y amene pas (`Blocs.poursuiteAuBord` la ferait suivre).
    if (B.recherche.etoiles > 0) { Hud.message('SÈME LA POLICE D’ABORD', 150); Son.SFX.erreur(); return true; }
    return ascenseur('garage');
  }

  /** L'ascenseur vers un niveau : de la piece du garage (on la quitte au noir), ou de l'autre niveau (au noir, d'un
      bloc a l'autre, `Jeu.changerDeBloc`). On sort devant ses portes, tourne vers l'allee. */
  function allerA(slug) {
    Blocs.charger(slug);
    Son.SFX.ascenseur();
    if (B.bloc) {
      return Jeu.changerDeBloc(slug, function (def) { return devantLAscenseur(def); }, -Math.PI / 2);
    }
    Jeu.transiter([1, 0, 24], function () {
      const def = Blocs.cartes[slug];
      if (!def) return;
      Jeu.quitterLaPiece();
      if (Blocs.entrerAuNoir(slug, devantLAscenseur(def))) Entites.regarder(B.joueur, 0, -1);
    }, null, function () { return !Blocs.cartes[slug]; });
    return true;
  }

  /** AGRANDIR LE SOUS-SOL, au comptoir de Ti-Guy (la piece du garage) : la ligne du menu, ou null quand elle n'a
      rien a faire la (le garage n'est pas a toi, ou le −2 est deja ouvert). Le prix vient d'`economie.TARIFS`. */
  function itemAgrandir() {
    if (niveaux() >= 2 || !Missions.possede(Missions.proprieteDe('garage'))) return null;
    const prix = B.defs.economie.tarifs.sous_sol_2;
    return { libelle: 'AGRANDIR LE SOUS-SOL', detail: prix + ' $ — LE −2, DIX CASES', actif: B.partie.argent >= prix,
             faire: function () {
               if (!Missions.payer(prix, 'LE −2')) { Son.SFX.erreur(); return false; }
               B.partie.souterrain.niveaux = 2;
               Hud.message('LE −2 EST À TOI — LA GRILLE EST LEVÉE', 180);
               Missions.sauvegarderPartie();
               return true;
             } };
  }

  /** Du sous-sol, a pied : au noir, on range ses chars (`Jeu.revenirEnVille` → `quitterLeBloc`), et l'on sort de
      l'ascenseur de la piece du garage. */
  function monterAPied() {
    Son.SFX.ascenseur();
    Jeu.transiter(FONDU_ASCENSEUR, function () {
      Jeu.revenirEnVille();
      const porte = (Monde.carte.def.portes || []).find(function (q) { return q.lieu === 'garage' && q.interieur; });
      const piece = porte && Jeu.chargerPiece(porte);
      if (!piece) return;
      const j = B.joueur, pt = (piece.interieur.points || []).find(function (p) { return p.type === 'ascenseur'; });
      if (pt) { j.x = pt.x * TT + 8; j.y = (pt.y + 1) * TT + 8; }
      Entites.regarder(j, 0, 1);
      Monde.centrerCamera(j.x, j.y);
      Hud.message(piece.interieur.nom.toUpperCase(), 120);
    });
    return true;
  }

  /** Au sous-sol, a pied, dans la rangee devant les portes de l'ascenseur ? */
  function sousLaMain(j) {
    if (!ici() || !j || j.dansVehicule) return false;
    const s = B.bloc.def.bloc.souterrain.ascenseur, tx = Math.floor(j.x / TT), ty = Math.floor(j.y / TT);
    return ty === s.y && tx >= s.x && tx < s.x + s.l;
  }
  function invite(j) { return sousLaMain(j) ? 'L’ASCENSEUR' : null; }
  function agir(j) { return sousLaMain(j) ? ascenseur(B.bloc.slug) : false; }

  /** Les numeros des cases (P1…), et les portes de l'ascenseur : en bas, sur le mur sud (les `D` du plan sont
      deja des portes de platre, on y ajoute l'acier et le bouton) ; en haut, sur le mur nord de la piece du garage,
      au-dessus du point `ascenseur`. Rien ailleurs. */
  function dessiner(ctx, cam) {
    if (ici()) {
      const s = B.bloc.def.bloc.souterrain;
      s.cases.forEach(function (q) {
        // Le numero du cote de l'allee : au pied des cases du nord, en tete de celles du sud.
        const x = Math.round((q.x + q.l / 2) * TT - cam.x) - 6;
        const y = Math.round((q.cap < 0 ? (q.y + q.h) * TT - 12 : q.y * TT + 5) - cam.y);
        if (x < -20 || x > VW + 20 || y < -20 || y > VH + 20) return;
        Atlas.texte(ctx, 'P' + q.n, x, y, '#f4e4c1', 1);
      });
      const a = s.ascenseur;
      portes(ctx, Math.round(a.x * TT - cam.x), Math.round((a.y + 1) * TT - cam.y), a.l * TT);
      // Une rampe interieure : son etiquette (« −2 ») toujours, et ses barreaux tant que le −2 n'est pas achete.
      for (const o of B.bloc.def.bloc.rampes || []) grille(ctx, o, cam, !rampeOuverte(o));
      return;
    }
    if (B.interieur && B.interieur.slug === 'garage') {
      const pt = (B.interieur.points || []).find(function (p) { return p.type === 'ascenseur'; });
      if (pt) portes(ctx, Math.round(pt.x * TT - cam.x), Math.round((pt.y - 1) * TT - cam.y), TT);
    }
  }

  /** L'etiquette d'une rampe interieure (« −2 »), et des barreaux d'acier sur son ouverture si elle est `fermee`. */
  function grille(ctx, o, cam, fermee) {
    const w = Monde.carte.w, h = Monde.carte.h, vertical = o.bord === 'est' || o.bord === 'ouest';
    const x0 = (o.bord === 'est' ? w - 1 : o.bord === 'ouest' ? 0 : o.de) * TT - cam.x;
    const y0 = (o.bord === 'sud' ? h - 1 : o.bord === 'nord' ? 0 : o.de) * TT - cam.y;
    const L = o.l * TT;
    ctx.fillStyle = '#3b3f46';
    if (fermee && vertical) { ctx.fillRect(Math.round(x0 + 6), Math.round(y0), 4, L); for (let k = 2; k < L; k += 5) ctx.fillRect(Math.round(x0 + 2), Math.round(y0 + k), 12, 2); }
    else if (fermee) { ctx.fillRect(Math.round(x0), Math.round(y0 + 6), L, 4); for (let k = 2; k < L; k += 5) ctx.fillRect(Math.round(x0 + k), Math.round(y0 + 2), 2, 12); }
    Atlas.texte(ctx, '−2', Math.round(x0 - (vertical ? 12 : -L / 2 + 4)), Math.round(y0 + (vertical ? L / 2 - 3 : 18)), '#f5c542', 1);
    B.stats.rects += 6;
  }

  /** Chaque image : les sons du sous-sol se chargent dans la piece du garage ou en bas (`audio.LIEUX`), et les
      neons bourdonnent tant qu'on y est. */
  function majSon() {
    const garage = B.interieur && B.interieur.slug === 'garage';
    if (ici() || garage) Son.Lieu.charger('souterrain');
    Son.SFX.neons(ici() ? 1 : 0);
  }

  /** Deux battants d'acier brosse, leur joint, et le bouton allume. */
  function portes(ctx, x, y, l) {
    ctx.fillStyle = '#5d6168'; ctx.fillRect(x + 1, y + 1, l - 2, TT - 2);
    ctx.fillStyle = '#8a9099'; ctx.fillRect(x + 2, y + 2, l / 2 - 3, TT - 4); ctx.fillRect(x + l / 2 + 1, y + 2, l / 2 - 3, TT - 4);
    ctx.fillStyle = '#2b2e33'; ctx.fillRect(x + l / 2 - 1, y + 2, 2, TT - 4);
    ctx.fillStyle = '#f5c542'; ctx.fillRect(x + l - 3, y + TT / 2 - 1, 2, 2);
    B.stats.rects += 5;
  }

  return { SLUG, NIVEAUX, PAR_NIVEAU, CASES_MAX, est, ici, niveaux, rampeOuverte, ouvertes, occupees, plein, fiche, ranger,
           garnir, refus, descendre, descendreAPied, monterAPied, allerA, ascenseur, itemAgrandir, sousLaMain, invite, agir,
           dessiner, majSon };
})();
