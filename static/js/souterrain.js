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

  /** Ce bloc-ci est-il le sous-sol ? */
  function est(slug) { return slug === SLUG; }

  /** Y est-on ? */
  function ici() { return !!(B.bloc && B.bloc.slug === SLUG); }

  //: Les cases d'un niveau, et de tout le sous-sol (`app/blocs/souterrain.py`, les memes nombres).
  const PAR_NIVEAU = 10, CASES_MAX = 20;

  /** Les cases ouvertes : dix par niveau achete. */
  function ouvertes() { return PAR_NIVEAU * ((B.partie.souterrain && B.partie.souterrain.niveaux) || 1); }
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

  /** Reecrit `partie.souterrain.cases` d'apres les chars de `entites` : chacun sur SA case s'il y est (et qu'elle
      est ouverte et libre), les autres — laisses dans l'allee — gares par Ti-Guy sur la premiere case libre. Une
      epave ne se range pas. Rend ce qui n'est pas un char : ce que le bloc peut garder (`Blocs.garder`).
      ⚠️ Ne retire rien : la sauvegarde l'appelle en plein sous-sol, les chars restent ou ils sont. */
  function ranger(entites, def) {
    const cases = def.bloc.souterrain.cases, n = ouvertes();
    const neuf = [];
    for (let k = 0; k < CASES_MAX; k++) neuf.push(null);
    const reste = [], sansPlace = [];
    for (const e of entites) {
      if (e.type !== 'vehicule') { reste.push(e); continue; }
      if (e.etat === 'epave') continue;
      const k = caseSous(cases, e);
      if (k >= 0 && k < n && !neuf[k]) neuf[k] = fiche(e); else sansPlace.push(e);
    }
    for (const e of sansPlace) {
      let k = 0;
      while (k < n && neuf[k]) k++;
      if (k < n) neuf[k] = fiche(e);
    }
    B.partie.souterrain.cases = neuf;
    return reste;
  }

  /** Pose les chars ranges sur leurs cases, a la descente. ⚠️ `couleur` DONNEE a `Vehicules.creer` : un char ne
      sans couleur tire un de, et tout le hasard de la partie glisse. */
  function garnir(def) {
    const cases = def.bloc.souterrain.cases, n = ouvertes();
    B.partie.souterrain.cases.forEach(function (c, k) {
      if (!c || k >= n || !cases[k] || !Vehicules.vehiculeDef(c.slug)) return;
      const q = cases[k];
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
    return Blocs.sauter(SLUG, null, null);
  }

  //: Le fondu de l'ascenseur : celui d'un etage (`Jeu`, FONDU_ETAGE).
  const FONDU_ASCENSEUR = [20, 16];

  /** De la piece du garage, a pied : au noir, la piece se quitte et le sous-sol se charge, et l'on sort de
      l'ascenseur du −1. Le noir tient le temps que la carte arrive (`attente`). */
  function descendreAPied() {
    if (!Missions.possede(Missions.proprieteDe('garage'))) {
      Hud.message('LE SOUS-SOL EST AU PROPRIO — ACHÈTE LE GARAGE', 150); Son.SFX.erreur();
      return true;
    }
    // Comme au rideau : pas de police au sous-sol, on ne l'y amene pas (`Blocs.poursuiteAuBord` la ferait suivre).
    if (B.recherche.etoiles > 0) { Hud.message('SÈME LA POLICE D’ABORD', 150); Son.SFX.erreur(); return true; }
    Blocs.charger(SLUG);
    Jeu.transiter([1, 0, 24], function () {
      const def = Blocs.cartes[SLUG];
      if (!def) return;
      Jeu.quitterLaPiece();
      const s = def.bloc.souterrain.ascenseur;
      if (Blocs.entrerAuNoir(SLUG, { x: (s.x + s.l / 2) * TT, y: s.y * TT + 8 })) Entites.regarder(B.joueur, 0, -1);
    }, null, function () { return !Blocs.cartes[SLUG]; });
    return true;
  }

  /** Du sous-sol, a pied : au noir, on range ses chars (`Jeu.revenirEnVille` → `quitterLeBloc`), et l'on sort de
      l'ascenseur de la piece du garage. */
  function monterAPied() {
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
  function agir(j) { return sousLaMain(j) ? monterAPied() : false; }

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
      return;
    }
    if (B.interieur && B.interieur.slug === 'garage') {
      const pt = (B.interieur.points || []).find(function (p) { return p.type === 'ascenseur'; });
      if (pt) portes(ctx, Math.round(pt.x * TT - cam.x), Math.round((pt.y - 1) * TT - cam.y), TT);
    }
  }

  /** Deux battants d'acier brosse, leur joint, et le bouton allume. */
  function portes(ctx, x, y, l) {
    ctx.fillStyle = '#5d6168'; ctx.fillRect(x + 1, y + 1, l - 2, TT - 2);
    ctx.fillStyle = '#8a9099'; ctx.fillRect(x + 2, y + 2, l / 2 - 3, TT - 4); ctx.fillRect(x + l / 2 + 1, y + 2, l / 2 - 3, TT - 4);
    ctx.fillStyle = '#2b2e33'; ctx.fillRect(x + l / 2 - 1, y + 2, 2, TT - 4);
    ctx.fillStyle = '#f5c542'; ctx.fillRect(x + l - 3, y + TT / 2 - 1, 2, 2);
    B.stats.rects += 5;
  }

  return { SLUG, PAR_NIVEAU, CASES_MAX, est, ici, ouvertes, occupees, plein, fiche, ranger, garnir, refus, descendre,
           descendreAPied, monterAPied, sousLaMain, invite, agir, dessiner };
})();
