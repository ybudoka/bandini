/* Bandini — l'Halloween (docs/jalons/les-quatre-saisons-realistes.md, lot 3).

   Tout octobre, des citrouilles sur les perrons, allumees la nuit. Le 31 (jour 33 de l'annee du jeu,
   `Calendrier.estLe('halloween')`), les fenetres prennent des lumieres orange et violettes, un passant
   sur trois sort deguise, des bandes d'enfants vont de porte en porte, et une maison des Erables est
   hantee de 18 h a minuit.

   ⚠️ RIEN DE POSE (la recette des Fetes) : les citrouilles sont PEINTES a cote des portes des logements
   (`B.defs.carte.residences`, a l'empreinte du logement) et triees avec les gens ; les lumieres sont la
   COULEUR des lampes qui existent ; rien ne bouche une porte, rien ne reste en novembre. Aucun de. */

const Halloween = (function () {
  'use strict';

  //: Le tri du dessin : apres le sapin des Fetes.
  const ID_TRI = 1e9 + 710;

  function donnees() { return B.defs && B.defs.halloween; }

  /** Octobre (les citrouilles) ce jour-la ? */
  function octobreA(jour) { return typeof Calendrier !== 'undefined' && Calendrier.mois(jour) === 'octobre'; }
  function octobre() { return !!B.partie && octobreA(B.partie.jour); }

  /** Le soir du 31 a cette heure (0 a 1 de la journee), des `des_h` : le 31 et l'heure passee. */
  function soirA(jour, heure, desH) {
    return typeof Calendrier !== 'undefined' && Calendrier.estLe('halloween', jour) && heure * 24 >= desH;
  }

  //: Les citrouilles de la ville, calculees une fois (les residences ne bougent pas).
  let lesCitrouilles = null, deQui = null;

  /** Les citrouilles : { x, y (pied, en px), r (le logement) } — un logement sur `part`, a l'empreinte
      du logement, a cote de sa porte (du cote ou il reste du mur), sur le trottoir au pied du mur. */
  function citrouilles() {
    const d = donnees(), res = B.defs && B.defs.carte && B.defs.carte.residences;
    if (!d || !res) return [];
    if (lesCitrouilles && deQui === res) return lesCitrouilles;
    const c = d.citrouilles, out = [], m = maisonPorte();
    for (const r of res) {
      if (hash2(r.x * 31 + c.sel, r.y) % 1000 >= c.part * 1000) continue;
      if (m && r.y === m.y && r.x + (r.porte || 0) === m.x) continue;   // la maison hantee a SA grosse citrouille
      const porte = r.x + (r.porte || 0), cote = (r.porte || 0) + 1 < r.l ? porte + 1 : porte - 1;
      out.push({ x: cote * TT + 8, y: (r.y + 1) * TT + 4, r: r });
    }
    lesCitrouilles = out; deQui = res;
    return out;
  }

  /** La nuit qu'on voit (les citrouilles s'allument quand les lampadaires s'allument). */
  function nuit() { return Monde.ambianceVue().alpha > 0.2; }

  function dehors() { return !B.interieur && !B.bloc; }

  /** Les citrouilles se trient avec les gens et les chars par leur pied. */
  function ajouterVisibles(visibles, cx, cy) {
    if (!octobre() || !dehors()) return;
    const allumee = nuit(), p = maisonPorte();
    if (p) {
      const x = p.x * TT + 8 + 12, y = (p.y + 1) * TT + 6;
      if (x > cx - 30 && y > cy - 30 && x < cx + VW + 30 && y < cy + VH + 30) {
        visibles.push({ id: ID_TRI, vivant: true, x: x, y: y,
                        peindreFoire: function (ctx) { peindreCitrouille(ctx, x - Math.round(cx), y - Math.round(cy), allumee, 2); } });
      }
    }
    for (const c of citrouilles()) {
      if (c.x < cx - 20 || c.y < cy - 20 || c.x > cx + VW + 20 || c.y > cy + VH + 20) continue;
      if (typeof Chantiers !== 'undefined' && Chantiers.efface(c.r.x, c.r.y)) continue;
      const x = c.x, y = c.y;
      visibles.push({ id: ID_TRI, vivant: true, x: x, y: y,
                      peindreFoire: function (ctx) { peindreCitrouille(ctx, x - Math.round(cx), y - Math.round(cy), allumee, 1); } });
    }
  }

  /** Une citrouille, son pied en (x, y) a l'ecran ; `echelle` 2 pour la grosse de la maison hantee.
      Allumee : le visage brille. */
  function peindreCitrouille(ctx, x, y, allumee, echelle) {
    const k = echelle || 1, r = function (dx, dy, w, h) { ctx.fillRect(x + dx * k, y + dy * k, w * k, h * k); };
    ctx.fillStyle = 'rgba(0,0,0,0.25)'; r(-5, -1, 10, 2);
    ctx.fillStyle = '#e07b1a'; r(-4, -7, 8, 6); r(-5, -6, 10, 4);
    ctx.fillStyle = '#b85a10'; r(-1, -7, 1, 6); r(-4, -3, 8, 1);
    ctx.fillStyle = '#4a6b2a'; r(0, -9, 1, 2);
    if (allumee) {
      ctx.fillStyle = '#ffd84a'; r(-3, -6, 2, 1); r(1, -6, 2, 1); r(-2, -4, 4, 1);
    } else {
      ctx.fillStyle = '#5a2e0a'; r(-3, -6, 2, 1); r(1, -6, 2, 1); r(-2, -4, 4, 1);
    }
    B.stats.rects += 9;
  }

  /** La lueur des citrouilles, la nuit. */
  function lampes(cam) {
    const d = donnees();
    if (!d || !octobre() || !dehors() || !nuit()) return [];
    const c = d.citrouilles, out = [], coul = 'rgba(' + c.lueur.join(',') + ',' + c.force + ')';
    for (const p of citrouilles()) {
      if (typeof Chantiers !== 'undefined' && Chantiers.efface(p.r.x, p.r.y)) continue;
      const x = p.x - cam.x, y = p.y - 4 - cam.y;
      if (x < -40 || y < -40 || x > VW + 40 || y > VH + 40) continue;
      out.push({ x: x, y: y, r: c.rayon, c: coul });
      if (out.length >= 12) break;
    }
    return out;
  }

  /** La couleur d'une fenetre ou d'une vitrine le soir du 31, ou null : a l'empreinte de sa tuile. */
  function couleur(l) {
    const d = donnees();
    if (!d || !B.partie || !l || !soirA(B.partie.jour, B.partie.heure, d.lumieres.des_h)) return null;
    if (d.lumieres.sortes.indexOf(l.sorte) < 0) return null;
    const cs = d.lumieres.couleurs, c = cs[hash2(l.tx || 0, (l.ty || 0) + 0x4A11) % cs.length];
    return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + d.lumieres.force + ')';
  }

  // --- Les deguises du 31 --------------------------------------------------------------------

  //: Les costumes : ce qu'ils changent a une tenue (la peau, le squelette et la coiffure restent).
  //: `fantome` : le drap blanc — la capuche, la robe et la peau du meme blanc.
  const COSTUMES = {
    sorciere: { chapeau: 'sorciere', couleur_chapeau: '#1c1426', accent: '#7a3aa8', haut: 'robe', couleur_haut: '#2a1a3a',
                motif: 'uni', couleur_bas: '#2a1a3a', accessoires: [] },
    fantome: { chapeau: 'capuche', couleur_chapeau: '#eef0f4', haut: 'robe', couleur_haut: '#eef0f4', motif: 'uni',
               couleur_bas: '#eef0f4', peau: '#eef0f4', cheveux: '#eef0f4', couleur_souliers: '#eef0f4', accessoires: [] },
    squelette: { chapeau: 'aucun', haut: 'chandail', couleur_haut: '#141418', motif: 'os', bas: 'pantalon',
                 couleur_bas: '#141418', peau: '#e8e4dc', accessoires: [] },
    citrouille: { chapeau: 'tuque', couleur_chapeau: '#3a6b2a', accent: '#3a6b2a', haut: 'coton_ouate',
                  couleur_haut: '#e07b1a', motif: 'uni', bas: 'pantalon', couleur_bas: '#1a1a1a', accessoires: [] },
  };

  /** Une tenue habillee en `costume` (le reste de la tenue garde sa personne). */
  function habillerEn(tenue, costume) { return Object.assign({}, tenue, COSTUMES[costume] || {}); }

  /** Le costume de ce passant le soir du 31, ou null : un passant sur `part`, a l'empreinte de son
      numero — jamais un membre de gang ni un personnage (on doit les reconnaitre). */
  function costumeDe(e) {
    const d = donnees();
    // ⚠️ On doit RECONNAITRE la police, les gangs, les commis, les gens de metier et ceux d'une mission (la
    // relecture : un agent sur trois poursuivait le joueur en sorciere).
    if (!d || !B.partie || !e || e.type !== 'pieton' || !e.tenue) return null;
    if (e.agent || e.gang || e.metier || e.commerce || e.mission || e.personnage || e.cible) return null;
    const g = d.deguises;
    if (!soirA(B.partie.jour, B.partie.heure, g.des_h)) return null;
    const h = hash2(e.id, g.sel);
    if (h % 1000 >= g.part * 1000) return null;
    return g.costumes[(h >>> 12) % g.costumes.length];
  }

  //: La tenue du costume, cuite une fois par passant (le meme objet d'une image a l'autre).
  const habilles = new WeakMap();

  /** La tenue a dessiner : le costume le soir du 31, la tenue de tous les jours sinon. */
  function tenueDe(e) {
    const c = costumeDe(e);
    if (!c) return e.tenue;
    const deja = habilles.get(e);
    if (deja && deja.c === c && deja.de === e.tenue) return deja.t;
    const t = habillerEn(e.tenue, c);
    habilles.set(e, { c: c, de: e.tenue, t: t });
    return t;
  }

  // --- Les enfants qui passent l'Halloween ---------------------------------------------------

  //: Les enfants se deguisent par leurs couleurs (l'enfant est dessine a la main, sans garde-robe).
  const COSTUMES_ENFANT = {
    sorciere: { c: '#2a1a3a', h: '#1c1426', p: '#2a1a3a' },
    fantome: { c: '#eef0f4', h: '#eef0f4', p: '#eef0f4', s: '#eef0f4' },
    squelette: { c: '#141418', p: '#141418', s: '#e8e4dc' },
    citrouille: { c: '#e07b1a', h: '#3a6b2a', p: '#1a1a1a' },
  };

  //: Les bandes en cours : { enfants (le chef d'abord, les autres le suivent), cible, faites, pauseT }.
  let bandes = [], derniereNaissance = -Infinity;

  function enfantsA(jour, heure) {
    const d = donnees(), e = d && d.enfants, h = heure * 24;
    return !!e && typeof Calendrier !== 'undefined' && Calendrier.estLe('halloween', jour) && h >= e.des_h && h < e.jusqu_h;
  }

  /** La prochaine porte a citrouille du chef : la plus proche qu'il n'a pas faite, a portee. */
  function prochaineCitrouille(b) {
    const chef = b.enfants[0];
    let mieux = null, dm = 320 * 320;
    for (const c of citrouilles()) {
      if (b.faites.indexOf(c) >= 0) continue;
      const d = (c.x - chef.x) * (c.x - chef.x) + (c.y - chef.y) * (c.y - chef.y);
      if (d < dm) { dm = d; mieux = c; }
    }
    return mieux;
  }

  function viser(b) {
    const c = prochaineCitrouille(b), chef = b.enfants[0];
    b.cible = c ? { x: c.x, y: c.y + 10, cit: c } : null;
    if (c) { chef.etat = 'cap'; chef.cap = { x: b.cible.x, y: b.cible.y }; chef.capT = 0; }
  }

  /** Une bande nait HORS DE L'ECRAN, au pied d'une citrouille de 220 a 480 px du joueur. ⚠️ `creerPieton`
      tire son de (sa bourse, sa direction) : les enfants ne naissent que le 31 au soir, dans les quartiers
      de maisons, et seulement la ou le joueur est. */
  function faireNaitre(d) {
    const j = B.joueur, cs = [];
    for (const c of citrouilles()) {
      const dd = Math.hypot(c.x - j.x, c.y - j.y);
      if (dd >= 220 && dd <= 480 && !Entites.visibleAEcran(c.x, c.y, 20)) cs.push(c);
    }
    if (!cs.length) return;
    const t = B.t || 0, e = d.enfants, c = cs[hash2(t, e.sel) % cs.length];
    const n = e.taille[0] + hash2(t, e.sel + 1) % (e.taille[1] - e.taille[0] + 1);
    const arch = Entites.archetype('enfant'), b = { enfants: [], cible: null, faites: [], pauseT: 0 };
    for (let k = 0; k < n; k++) {
      const x = c.x + (k - 1) * 7, y = c.y + 12 + (k & 1) * 4;
      const enfant = Entites.creerPieton(x, y, arch);
      enfant.costume = d.deguises.costumes[hash2(enfant.id, d.deguises.sel) % d.deguises.costumes.length];
      enfant.swaps = Object.assign({}, enfant.swaps || {}, COSTUMES_ENFANT[enfant.costume]);
      if (k > 0) enfant.suit = b.enfants[0];
      b.enfants.push(enfant);
    }
    bandes.push(b);
    viser(b);
  }

  /** Toutes les 15 images : les bandes vont de citrouille en citrouille, s'arretent le temps de dire
      leur mot, et rentrent HORS DE L'ECRAN quand l'heure est passee ou le joueur trop loin. */
  function maj() {
    const d = donnees();
    if (!d || !B.partie || !B.joueur) return;
    majMaison();
    const t = B.t || 0;
    if (t % 15 !== 0) return;
    majSons(d, t);
    const soir = enfantsA(B.partie.jour, B.partie.heure), j = B.joueur, e = d.enfants;
    for (const b of bandes) {
      const chef = b.enfants[0];
      // ⚠️ DEDANS (une piece, un bloc), la ville et ses enfants attendent dehors (`B.exterieur`) : on n'y
      // touche pas. Et une bande que la ville a RETIREE (`peupler` oublie ce qui est loin) libere sa place.
      if (B.interieur || B.bloc) continue;
      if (!chef || !chef.vivant || B.entites.indexOf(chef) < 0) { b.enfants.forEach(Entites.retirer); b.fini = true; continue; }
      if (!soir || b.rentre || Math.hypot(chef.x - j.x, chef.y - j.y) > 700) {
        if (!Entites.visibleAEcran(chef.x, chef.y, 40)) { b.enfants.forEach(Entites.retirer); b.fini = true; }
        continue;
      }
      if (b.pauseT > 0) { b.pauseT -= 15; if (b.pauseT <= 0) viser(b); continue; }
      if (b.cible && Math.hypot(chef.x - b.cible.x, chef.y - b.cible.y) <= 16) {
        Entites.bulle(chef, e.mots[hash2(chef.id, b.faites.length) % e.mots.length], { duree: 90 });
        b.faites.push(b.cible.cit);
        b.cible = null;
        chef.etat = 'arret'; chef.minuterie = 90; chef.vx = 0; chef.vy = 0; chef.face = 'haut';
        b.pauseT = 90;
        continue;
      }
      // Rendu (le chemin barre : `cap` renonce), ou rien de vise : la suivante.
      if (!b.cible || chef.etat !== 'cap') {
        if (b.cible) b.faites.push(b.cible.cit);
        viser(b);
        if (!b.cible) b.rentre = true;           // plus une citrouille a portee : la bande rentre (hors champ)
      }
    }
    bandes = bandes.filter(function (b) { return !b.fini; });
    if (!soir || B.interieur || B.bloc) return;
    const z = Monde.zoneA(j.x, j.y);          // en pixels
    if (!z || e.districts.indexOf(z.district) < 0) return;
    if (bandes.length >= e.bandes_max || t - derniereNaissance < 180) return;
    derniereNaissance = t;
    faireNaitre(d);
  }

  function bandesEnCours() { return bandes; }

  //: La derniere demande des sons, et le dernier rire de sorciere.
  let sonsDemandes = -Infinity, dernierRire = -Infinity;

  /** Le soir du 31 : les sons se chargent (une fois toutes les 300 images, pas a chaque image) ; une
      sorciere qui passe pres du joueur ricane, au plus une fois toutes les dix secondes. */
  function majSons(d, t) {
    if (typeof Son === 'undefined' || !soirA(B.partie.jour, B.partie.heure, d.deguises.des_h)) return;
    if (Son.Lieu && t - sonsDemandes >= 300) { sonsDemandes = t; Son.Lieu.charger('halloween'); }
    if (B.interieur || t - dernierRire < 1500 || !Son.SFX || !Son.SFX.rire_sorciere) return;   // 25 s : cinq heures de soiree
    const j = B.joueur;
    for (const q of Entites.pietonsAutour(j.x, j.y, 160) || []) {
      if (costumeDe(q) !== 'sorciere' || hash2(t, q.id) % 4) continue;
      dernierRire = t; Son.SFX.rire_sorciere(q.x, q.y);
      break;
    }
  }

  /** La musique d'Halloween, dehors le soir du 31 (des 18 h, avec la maison hantee). */
  function musiqueDehors() {
    const d = donnees();
    return !!(d && B.partie && !B.interieur && !B.bloc && soirA(B.partie.jour, B.partie.heure, d.maison.des_h));
  }

  /** Une partie recommencee : les bandes d'une autre partie s'oublient. */
  function oublier() { bandes = []; derniereNaissance = -Infinity; visite = null; sonsDemandes = -Infinity; dernierRire = -Infinity; }

  // --- La maison hantee ------------------------------------------------------------------------

  //: La porte de la maison (calculee une fois), et la visite en cours : { t, eteintes, fantome, poste,
  //: revient, postes, sac, pres, dits }.
  let laPorte = null, dePortes = null, visite = null;

  /** Le district d'une tuile de la VILLE (ses zones, meme dans une piece ou un bloc — `Monde.zoneA` lit la
      carte ou l'on est, et une partie qui se reveille au chalet aurait perdu la maison pour la session). */
  function districtDeLaVille(tx, ty) {
    const zs = (B.defs && B.defs.carte && B.defs.carte.zones) || [];
    let d = null;
    for (const z of zs) if (tx >= z.x && tx < z.x + z.l && ty >= z.y && ty < z.y + z.h) d = z.district;
    return d;
  }

  /** La maison hantee : le PLUS GRAND logement qu'on visite dans les Erables (a surface egale, par
      rangee puis colonne) — une maison qui existe deja, choisie une fois pour toutes, sans de. ⚠️ Le
      premier venu faisait six tuiles sur cinq : un fantome n'avait nulle part ou se montrer. */
  function maisonPorte() {
    const d = donnees(), portes = B.defs && B.defs.carte && B.defs.carte.portes;
    if (!d || !portes) return null;
    if (dePortes === portes) return laPorte;
    const logements = portes.filter(function (p) {
      const quoi = String(p.interieur || p.lieu || '');
      if (quoi.indexOf('logement') !== 0) return false;
      return districtDeLaVille(p.x, p.y) === d.maison.district;
    });
    const inter = B.defs.carte.interieurs || {};
    const surface = function (p) { const i = inter[p.interieur]; return i ? i.largeur * i.hauteur : 0; };
    logements.sort(function (a, b) { return surface(b) - surface(a) || a.y - b.y || a.x - b.x; });
    laPorte = logements[0] || null; dePortes = portes;
    return laPorte;
  }

  function hanteeA(jour, heure) {
    const d = donnees(), m = d && d.maison, h = heure * 24;
    return !!m && typeof Calendrier !== 'undefined' && Calendrier.estLe('halloween', jour) && h >= m.des_h && h < m.jusqu_h;
  }

  /** Est-on DANS la maison ? Le logement ou l'on est entre par sa porte (`B.exterieur` la garde). */
  function dansLaMaison() {
    const p = maisonPorte(), ex = B.exterieur;
    // ⚠️ Le rez-de-chaussee seulement : a l'etage (`changerEtage`), `B.exterieur` reste le meme.
    return !!(p && B.interieur && B.interieur.slug === p.interieur && ex && ex.x === p.x * TT + 8 && ex.y === (p.y + 1) * TT + 10);
  }

  function annee() { return Math.floor((B.partie.jour - 1) / (B.defs.calendrier ? B.defs.calendrier.annee : 40)); }

  function murmurer(cle) {
    const d = donnees();
    if (!visite || visite.dits[cle] || !d.murmures[cle]) return;
    visite.dits[cle] = true;
    Hud.message(d.murmures[cle].toUpperCase(), 180);
    if (typeof Son !== 'undefined' && Son.Voix && Son.Voix.parler) Son.Voix.parler('halloween-' + cle, {});
  }

  /** Les places du fantome et du sac, lues dans la piece : des tuiles ou l'on marche, a l'empreinte ;
      le sac, la plus loin de l'entree. */
  function lirePiece(entree) {
    const c = Monde.carte, postes = [];
    let sac = null, dmax = -1;
    for (let y = 1; y < c.h - 1; y++) for (let x = 1; x < c.w - 1; x++) {
      if (!Monde.marchablePieton(x, y)) continue;
      const dd = Math.abs(x - entree.x) + Math.abs(y - entree.y);
      if (dd > dmax) { dmax = dd; sac = { x: x * TT + 8, y: y * TT + 10 }; }
      if (dd >= 2) postes.push({ x: x * TT + 8, y: y * TT + 8, h: hash2(x, y + 0x6057) });
    }
    postes.sort(function (a, b) { return a.h - b.h; });       // un ordre a l'empreinte : il saute d'un coin a l'autre
    return { postes: postes, sac: sac };
  }

  /** Chaque image, dans la maison le 31 au soir : les lumieres s'eteignent une a une, le fantome se
      montre et s'evanouit quand on l'approche, et le sac de bonbons attend au fond. */
  function majMaison() {
    const d = donnees();
    if (!d || !B.partie || !dansLaMaison() || !hanteeA(B.partie.jour, B.partie.heure)) { visite = null; return; }
    const m = d.maison, j = B.joueur;
    if (!visite) {
      const lu = lirePiece({ x: Math.floor(j.x / TT), y: Math.floor(j.y / TT) });
      visite = { t: 0, eteintes: 0, fantome: null, poste: 0, revient: 0, postes: lu.postes, sac: lu.sac, pres: false, dits: {} };
      if (typeof Son !== 'undefined') {
        if (Son.Voix && Son.Voix.chargerHistoire) Son.Voix.chargerHistoire('halloween');   // sa banque de voix, en entrant
        if (Son.SFX && Son.SFX.porte_grince) Son.SFX.porte_grince();
      }
      murmurer('entree');
    }
    visite.t++;
    if (visite.eteintes < m.lumieres && visite.t >= (visite.eteintes + 1) * m.lumiere_s * 60) {
      visite.eteintes++;
      if (typeof Son !== 'undefined' && Son.SFX && Son.SFX.interrupteur) Son.SFX.interrupteur();
      if (visite.eteintes === 2) murmurer('lumiere');
    }
    if (visite.eteintes >= 1) {
      if (visite.fantome) {
        if (Math.hypot(visite.fantome.x - j.x, visite.fantome.y - j.y) < m.fantome_px) {
          visite.fantome = null; visite.revient = m.fantome_revient_s * 60;
          if (typeof Son !== 'undefined' && Son.SFX && Son.SFX.souffle_fantome) Son.SFX.souffle_fantome();
          murmurer('fantome');
        }
      } else if (--visite.revient <= 0 && visite.postes.length) {
        for (let k = 0; k < visite.postes.length; k++) {
          const p = visite.postes[(visite.poste + k) % visite.postes.length];
          if (Math.hypot(p.x - j.x, p.y - j.y) > m.fantome_px * 1.5) { visite.fantome = { x: p.x, y: p.y }; visite.poste += k + 1; break; }
        }
      }
    }
    const s = sac();
    if (s) {
      const pres = Math.hypot(s.x - j.x, s.y - j.y) < 20;
      // ⚠️ Le murmure d'abord, l'invite ENSUITE : un seul message a l'ecran (`B.msg`), le dernier gagne.
      if (pres && !visite.pres) { murmurer('sac'); Hud.message('UN SAC DE BONBONS… (ACTION)', 150); }
      visite.pres = pres;
      if (pres && Entree.neuf('action')) {
        B.partie.halloweenAn = annee();
        Missions.encaisser(m.prime, 'LES BONBONS DE LA MAISON HANTÉE');
        murmurer('bonbons');
      }
    }
  }

  /** Le sac de bonbons (s'il n'est pas deja pris cette annee), ou null. */
  function sac() {
    return visite && visite.sac && B.partie && B.partie.halloweenAn !== annee() ? visite.sac : null;
  }

  /** Le noir qui gagne, le fantome et le sac — PAR-DESSUS la scene (`Base.ecran()`, apres `Base.fin`) :
      une piece n'a pas de nuit a elle. */
  function dessinerDedans(ctx, vue) {
    if (!visite || !dansLaMaison()) return;
    const m = donnees().maison, j = B.joueur, px = j.x - vue.x, py = j.y - vue.y;
    const s = sac();
    if (s) {
      const x = Math.round(s.x - vue.x), y = Math.round(s.y - vue.y);
      ctx.fillStyle = '#e07b1a'; ctx.fillRect(x - 4, y - 7, 8, 7);
      ctx.fillStyle = '#b85a10'; ctx.fillRect(x - 4, y - 7, 8, 1);
      ctx.fillStyle = '#101018'; ctx.fillRect(x - 2, y - 5, 1, 1); ctx.fillRect(x + 1, y - 5, 1, 1); ctx.fillRect(x - 1, y - 3, 2, 1);
    }
    const a = Math.min(0.88, visite.eteintes / m.lumieres * 0.88);
    if (a > 0) {
      const g = ctx.createRadialGradient(px, py, 16, px, py, 80);
      g.addColorStop(0, 'rgba(4,4,10,0)');
      g.addColorStop(1, 'rgba(4,4,10,' + a.toFixed(2) + ')');
      ctx.fillStyle = g; ctx.fillRect(0, 0, VW, VH);
    }
    const f = visite.fantome;
    if (f) {
      // Le fantome : un drap blanc qui flotte, deux trous noirs — il se voit dans le noir.
      const x = Math.round(f.x - vue.x), y = Math.round(f.y - vue.y + Math.sin(visite.t / 14) * 2);
      ctx.fillStyle = 'rgba(238,240,248,0.85)';
      ctx.fillRect(x - 5, y - 14, 10, 12); ctx.fillRect(x - 4, y - 16, 8, 2); ctx.fillRect(x - 6, y - 4, 12, 3);
      ctx.fillRect(x - 6, y - 1, 3, 2); ctx.fillRect(x - 1, y - 1, 3, 2); ctx.fillRect(x + 4, y - 1, 2, 2);
      ctx.fillStyle = '#101018'; ctx.fillRect(x - 3, y - 12, 2, 3); ctx.fillRect(x + 1, y - 12, 2, 3);
      B.stats.rects += 9;
    }
  }

  /** Le Clairon de la veille. */
  function ligneDuClairon() {
    const d = donnees(), p = B.partie;
    if (!d || !p || typeof Calendrier === 'undefined' || !Calendrier.estLe('halloween', p.jour + 1)) return null;
    return d.clairon;
  }

  return { donnees, octobreA, octobre, soirA, citrouilles, ajouterVisibles, peindreCitrouille, lampes, couleur,
           ligneDuClairon, habillerEn, costumeDe, tenueDe, maj, oublier, bandes: bandesEnCours,
           maisonPorte, dansLaMaison, sac, dessinerDedans, musiqueDehors, visite: function () { return visite; } };
})();
