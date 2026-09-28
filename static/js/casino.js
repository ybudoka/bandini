/* Bandini — le casino du Dragon d'or, au Petit-Canton (docs/jalons/le-casino-du-petit-canton.md, vague 1).

   La MACHINE A SOUS : trois rouleaux, un bras. Les regles sont a Python (`machine_a_sous.py`,
   `B.defs.machine_a_sous`) ; ici, on tire le bras. Et le PORTIER, planté devant la porte du casino.

   ⚠️ SON HASARD EST A ELLE, comme celui du videopoker : l'arret des rouleaux se tire d'un generateur seme par
   la graine de la partie et le numero du tour (`arretDuTour`), jamais `B.rng()` — un tour joue ne decale pas
   un seul de du reste du jeu, et le meme tour revient au meme numero.

   ⚠️ UN MENU, PAS UN ECRAN A PART (la regle du videopoker) : TIRER LE BRAS est une ligne ; les rouleaux et la
   table des gains se DESSINENT a cote (`dessiner`).

   ⚠️ LE PORTIER NAIT A LA DEMANDE, quand on approche du casino, et renait s'il a ete oublie : ne pas le poser
   au demarrage, c'est ne pas deplacer un numero d'entite ni un tirage du depart — le Petit-Canton est dans la
   bulle de naissance du terminus. Et il nait HORS DE LA SUITE, avec un de PRETE. */

const Casino = (function () {
  'use strict';

  function regles() { return B.defs.machine_a_sous; }

  /** Les rouleaux en slugs : le paquet les envoie en chiffres (l'index du symbole, `machine_a_sous.py`). */
  let rouleauxLus = null, rouleauxDe = null;
  function rouleaux() {
    const r = regles();
    if (rouleauxDe !== r) {
      rouleauxDe = r;
      rouleauxLus = r.rouleaux.map(function (bande) { return Array.from(bande).map(function (c) { return r.symboles[+c]; }); });
    }
    return rouleauxLus;
  }

  /** Le compteur de la partie : `jour`, `tours` joues ce jour-la, et `total` (le numero du prochain tour). */
  function compteur() {
    const p = B.partie;
    p.machine_a_sous = p.machine_a_sous || { jour: p.jour, tours: 0, total: 0 };
    if (p.machine_a_sous.jour !== p.jour) { p.machine_a_sous.jour = p.jour; p.machine_a_sous.tours = 0; }
    return p.machine_a_sous;
  }

  /** L'arret des trois rouleaux au tour numero `n` : trois slugs de symbole. ⚠️ Un sel a lui (pas celui du
      videopoker) : la main numero 3 et le tour numero 3 ne tirent pas le meme hasard. */
  function arretDuTour(n) {
    const rng = mulberry(((B.graine | 0) ^ Math.imul(n + 1, 2246822519)) >>> 0);
    return rouleaux().map(function (rouleau) { return rouleau[Math.floor(rng() * rouleau.length)]; });
  }

  /** Le gain de ces trois symboles (un slug de `gains`), ou null — le jumeau de `machine_a_sous.evaluer`,
      et un juge les compare sur les 8 000 arrets. */
  function evaluerRouleaux(a) {
    const gains = regles().gains;
    for (const g of gains) {
      if (g.trois && a[0] === g.trois && a[1] === g.trois && a[2] === g.trois) return g.slug;
    }
    const cerises = a.filter(function (s) { return s === 'cerise'; }).length;
    if (cerises === 2) return 'deux_cerises';
    if (cerises === 1 && a[0] === 'cerise') return 'premiere_cerise';
    return null;
  }

  /** Ce que rend cet arret, en dollars (0 : la mise est perdue). */
  function gainDe(a) {
    const r = regles(), slug = evaluerRouleaux(a);
    const g = r.gains.find(function (q) { return q.slug === slug; });
    return g ? g.paie * r.mise : 0;
  }

  /** TIRER LE BRAS : la mise part, les rouleaux s'arretent, l'arret paie selon la table. */
  function tirer() {
    const r = regles(), c = compteur();
    if (c.tours >= r.tours_par_jour) { Hud.message('LA MACHINE A ASSEZ MANGÉ POUR AUJOURD’HUI'); Son.SFX.erreur(); return false; }
    if (!Missions.payer(r.mise, 'MACHINE À SOUS')) { Hud.message('PAS ASSEZ D’ARGENT'); Son.SFX.erreur(); return false; }
    const arret = arretDuTour(c.total);
    c.total++; c.tours++;
    const slug = evaluerRouleaux(arret), gain = gainDe(arret);
    const g = r.gains.find(function (q) { return q.slug === slug; });
    B.machineASous = { arret: arret, images: 0, resultat: { slug: slug, nom: g ? g.nom : 'RIEN', gain: gain } };
    if (gain > 0) Missions.encaisser(gain, g.nom);
    else Hud.message('RIEN — LA MACHINE GARDE TES ' + r.mise + ' $');
    return true;
  }

  function menu() {
    const r = regles(), c = compteur(), p = B.partie;
    const reste = Math.max(0, r.tours_par_jour - c.tours);
    return { titre: 'MACHINE À SOUS', sur: p.argent + ' $', largeur: 440, hauteur: 214, colonne: 176,
             items: [{ libelle: 'TIRER LE BRAS', detail: r.mise + ' $', actif: p.argent >= r.mise && reste > 0,
                       faire: function () { tirer(); return false; } }],
             aide: 'RETOUR ' + r.retour + ' % · ' + reste + ' TOUR' + (reste > 1 ? 'S' : '') + ' AUJOURD’HUI',
             dessiner: dessiner };
  }

  //: Les symboles en pixels, 5 × 5, et leur couleur.
  const DESSINS = {
    cerise: { c: '#c0392b', p: ['..##.', '.#..#', '#...#', '##.##', '##.##'] },
    citron: { c: '#e8d23a', p: ['.###.', '#####', '#####', '#####', '.###.'] },
    prune: { c: '#7a3a9a', p: ['..#..', '.###.', '#####', '#####', '.###.'] },
    cloche: { c: '#e8b33c', p: ['..#..', '.###.', '.###.', '#####', '..#..'] },
    bar: { c: '#1b1b24', p: ['#####', '.....', '#####', '.....', '#####'] },
    sept: { c: '#c0392b', p: ['#####', '...#.', '..#..', '.#...', '.#...'] },
    dragon: { c: '#2e8a4a', p: ['##..#', '.####', '..##.', '.####', '#...#'] },
  };

  /** Les trois rouleaux, a droite de la liste, et la table des gains dessous. Pendant une demi-seconde apres
      le bras, les rouleaux DEFILENT, puis s'arretent un a un. ⚠️ Comptes en IMAGES DESSINEES, pas en `B.t` :
      un menu ouvert fige le jeu, et les rouleaux defilaient pour toujours (vu a la capture). */
  function dessiner(ctx, x, y) {
    const r = regles(), m = B.machineASous;
    const x0 = x + 190, y0 = y + 30, L = 56, H = 56, pas = 64;
    const depuis = m ? m.images++ : 999;
    for (let i = 0; i < 3; i++) {
      const cx = x0 + i * pas;
      ctx.fillStyle = '#e0b040'; ctx.fillRect(cx - 2, y0 - 2, L + 4, H + 4);
      ctx.fillStyle = '#efe6d0'; ctx.fillRect(cx, y0, L, H);
      let slug = m ? m.arret[i] : null;
      if (m && depuis < 12 + i * 8) {                     // il defile encore
        const rouleau = rouleaux()[i];
        slug = rouleau[Math.floor(depuis / 2 + i * 5) % rouleau.length];
      }
      if (!slug) continue;
      const d = DESSINS[slug];
      ctx.fillStyle = d.c;
      for (let yy = 0; yy < 5; yy++) {
        for (let xx = 0; xx < 5; xx++) if (d.p[yy][xx] === '#') ctx.fillRect(cx + 13 + xx * 6, y0 + 10 + yy * 6, 6, 6);
      }
    }
    const gagne = m && depuis >= 28 ? m.resultat.slug : null;
    r.gains.forEach(function (g, i) {
      const yy = y0 + H + 12 + i * 10, couleur = g.slug === gagne ? '#e8b33c' : '#8a8698';
      const montant = g.paie * r.mise + ' $';
      Atlas.texte(ctx, g.nom, x0, yy, couleur, 1);
      Atlas.texte(ctx, montant, x0 + 3 * pas - 8 - Atlas.largeurTexte(montant, 1), yy, couleur, 1);
    });
    if (m && depuis >= 28) {
      const t = m.resultat.gain > 0 ? m.resultat.nom + ' · +' + m.resultat.gain + ' $' : 'RIEN CETTE FOIS';
      Atlas.texte(ctx, t, x + 12, y + 50, m.resultat.gain > 0 ? '#e8b33c' : '#8a8698', 1);
    }
    B.stats.rects += 90;
  }

  // --- Le portier ------------------------------------------------------------------------------------------

  //: A quelle distance du casino (en tuiles) le portier nait, et tous les combien d'images on regarde.
  const PORTIER = { portee: 30, pas: 30 };

  function porteDuCasino() {
    if (B.bloc || !Monde.carte || !Monde.carte.def) return null;
    return (Monde.carte.def.portes || []).find(function (p) { return p.lieu === 'nord_casino'; }) || null;
  }

  /** `fn` jouee avec un de PRETE (le meme que `Entites.sansLeDe`) : la file du jeu ne bouge pas d'un tirage. */
  function sansLeDe(graine, fn) {
    const de = B.rng;
    let s = graine >>> 0;
    B.rng = function () { s = hash2(s + 1, 0x5EED); return (s % 100000) / 100000; };
    try { return fn(); } finally { B.rng = de; }
  }

  function portier() {
    return B.entites.find(function (e) { return e.portierCasino && e.vivant; }) || null;
  }

  /** Le portier, a deux tuiles a l'est de la porte, sur le trottoir, face a la rue — jamais DANS le devant
      de la porte. Nait quand le joueur approche, si personne ne tient le poste. */
  function maj() {
    if (B.interieur || (B.t || 0) % PORTIER.pas !== 0) return;
    const porte = porteDuCasino(), j = B.joueur;
    if (!porte || !j) return;
    const px = (porte.x + 2) * TT + 8, py = (porte.y + 1) * TT + 8;
    if (Math.hypot(j.x - px, j.y - py) > PORTIER.portee * TT || portier()) return;
    const arch = Entites.archetype('gardien');
    if (!arch) return;
    const g = Entites.enDehorsDeLaSuite(function () {
      return sansLeDe(hash2(porte.x, porte.y), function () { return Entites.creerPieton(px, py, arch); });
    });
    if (!g) return;
    g.etat = 'fige'; g.face = 'bas'; g.gardien = true; g.portierCasino = true; g.poste = { x: px, y: py };
  }

  // --- La marquise ----------------------------------------------------------------------------------------

  //: La marquise de neon au-dessus de la porte : combien de tuiles de large, et ses couleurs.
  const MARQUISE = { tuiles: 12, fond: '#5a0c0a', cadre: '#e0b040', lettres: '#ffd24a', ampoule: '#fff1b0',
                     eteinte: '#8a5a20', ombre: 'rgba(0,0,0,0.30)' };

  /** LA MARQUISE DU DRAGON D'OR : un grand panneau de neon rouge et or pose sur le haut de la facade, au-dessus
      de la porte, son nom en grandes lettres et des ampoules qui chassent tout autour (d'apres `B.t`, sans de).
      ⚠️ Au-dessus des gens (`Jeu.rendre`) : elle deborde sur le toit, et on passe dessous. En ville seulement. */
  function dessinerMarquise(ctx, cam) {
    if (B.interieur) return;
    const porte = porteDuCasino();
    if (!porte) return;
    const large = MARQUISE.tuiles * TT, haut = 26;
    const x = Math.round((porte.x + 0.5) * TT - large / 2 - cam.x), y = porte.y * TT - haut - 2 - cam.y;
    if (x > VW + 20 || x + large < -20 || y > VH + 20 || y + haut < -20) return;
    ctx.fillStyle = MARQUISE.ombre; ctx.fillRect(x + 3, y + 3, large, haut);
    ctx.fillStyle = MARQUISE.cadre; ctx.fillRect(x, y, large, haut);
    ctx.fillStyle = MARQUISE.fond; ctx.fillRect(x + 2, y + 2, large - 4, haut - 4);
    const texte = "DRAGON D'OR", l = Atlas.largeurTexte(texte, 2);
    Atlas.texte(ctx, texte, Math.round(x + (large - l) / 2) + 1, y + 9, 'rgba(0,0,0,0.5)', 2);
    Atlas.texte(ctx, texte, Math.round(x + (large - l) / 2), y + 8, MARQUISE.lettres, 2);
    // Les ampoules : une sur trois allumee, et l'allumee avance d'une place toutes les huit images.
    const tour = Math.floor((B.t || 0) / 8) % 3;
    let k = 0;
    for (let i = 3; i < large - 3; i += 6, k++) {
      ctx.fillStyle = (k % 3) === tour ? MARQUISE.ampoule : MARQUISE.eteinte;
      ctx.fillRect(x + i, y + 3, 2, 2); ctx.fillRect(x + i, y + haut - 5, 2, 2);
    }
    B.stats.rects += 8 + 2 * k;
  }

  return { regles, compteur, arretDuTour, evaluerRouleaux, gainDe, tirer, menu, dessiner, maj, portier, dessinerMarquise };
})();
