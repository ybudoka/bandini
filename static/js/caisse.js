/* Bandini — la caisse populaire de La Shop, et le CASSE de l'arc X (docs/jalons/m16-cent-missions.md, vague 15).
   Python pose la caisse et la dessine (`app/caisse.py`) ; ici, on joue ce que les missions y font.

   ⚠️ DANS UNE PIECE, `majObjectif` DORT : un objectif `obtenir` dont la `table` est la caisse avance a la SORTIE, quand
   l'objet est dans le sac. C'est ce module qui l'y met, et il ne lit aucun slug de mission : il lit l'OBJET de
   l'objectif en cours (`OBJETS`, la copie de `caisse.OBJETS`, qu'un juge compare).

   - `plan_caisse` (le REPERAGE, x01) : rester pres de la voute le temps de compter ses boulons.
   - `bordereau` (la LIVRAISON, x03) : le colis au gerant, EN UNIFORME DE LIVREUR — le vigile s'habitue a ta face.
   - `sacs_caisse` (le COUP, x04) : ACTION a la voute, le gerant tourne la minuterie — une minute a tenir pendant que
     l'alarme sonne et que les gardes du fourgon entrent par la porte — puis les sacs de la paie.

   ⚠️ CE QU'ON A PREPARE CHANGE LE COUP, et ca se lit sur toi, pas dans un nom de mission : sans l'uniforme de livreur,
   Fernand te reconnait en entrant (deux etoiles, et il te saute dessus) ; le coupe du x02 et les repliques de Josee
   sont des objectifs et des repliques `si`/`sauf` (`Histoire.tenu`). Sans arme a feu, la minute se fait aux poings.

   ⚠️ RIEN AU DE : les gardes naissent a la porte sous un generateur a l'empreinte de leur vague (`sansLeDe`) — un
   casse joue ne decale pas un tirage du reste du jeu. */

const Caisse = (function () {
  'use strict';

  //: Le slug de la piece (`caisse.SLUG`).
  const SLUG = 'caisse_pop';
  //: Ce que chaque objet de mission demande ici — la copie de `caisse.OBJETS` (`test_caisse_js.py` les compare).
  const OBJETS = Object.freeze({ plan_caisse: 'reperage', bordereau: 'livraison', sacs_caisse: 'coup' });
  //: La tenue que le vigile ne regarde plus (x03 la remet, `magasins.TENUES`).
  const TENUE = 'livreur';
  //: ⚠️ Lus par le navigateur seulement : ils vivent ici (le paquet des definitions est a son plafond). Images a 60/s.
  const REGLES = Object.freeze({
    // Le reperage : tant d'images a moins de tant de pixels de la voute.
    reperage_images: 120, reperage_px: 40,
    // La livraison : le gerant a portee de main.
    gerant_px: 26,
    // Le coup : la minuterie de la voute (secondes), les etoiles de l'alarme, celles d'un vigile qui te reconnait.
    minuterie_s: 60, etoiles_alarme: 3, etoiles_reconnu: 2,
    // Les gardes du fourgon, par vagues : a tant de secondes de la minuterie, tant d'hommes a la porte.
    vagues: [{ a_s: 12, n: 2 }, { a_s: 30, n: 2 }, { a_s: 46, n: 2 }],
    // Leur fiche : le corps du garde, la matraque, un peu moins de vie qu'un agent.
    garde_vie: 80,
    // Toutes les tant de secondes, le compte a rebours au bandeau.
    annonce_s: 15,
  });
  const BULLES = Object.freeze({
    reconnu: 'HÉ! TOI, T’ES PAS LIVREUR!',
    salut_livreur: 'SALUT LE JEUNE.',
    livraison_refusee: 'VOUS ÊTES QUI, VOUS?',
    livraison: 'UN COLIS? SIGNEZ ICI… MERCI.',
    reperage: 'JE PEUX VOUS AIDER, MONSIEUR?',
    minuterie: 'OK! OK! LA MINUTERIE… ÇA PREND UNE MINUTE!',
    caissiere: 'PAS DE TROUBLE, PAS DE TROUBLE!',
    ouverte: 'PRENEZ-LES! PRENEZ-LES!',
    garde: 'BOUGE PUS!',
  });

  function ici() { return !!(B.interieur && B.interieur.slug === SLUG); }
  function possede(objet) { return !!(B.partie && B.partie.objets && B.partie.objets[objet] > 0); }

  /** L'objectif en cours qui se joue a la caisse (`obtenir`, `table: 'caisse'`), ou null. */
  function objectif() {
    if (!B.partie || !B.partie.mission || typeof Histoire === 'undefined') return null;
    const o = Histoire.objectif();
    return o && o.type === 'obtenir' && o.table === 'caisse' && OBJETS[o.objet] ? o : null;
  }

  function gerant() { return B.entites.find(function (e) { return e.gerant && e.vivant; }) || null; }
  function vigile() { return B.entites.find(function (e) { return e.vigile && e.vivant && e.etat !== 'assomme'; }) || null; }
  function voute() { return ((B.interieur && B.interieur.points) || []).find(function (p) { return p.type === 'voute'; }) || null; }
  function centre(p) { return { x: p.x * TT + 8, y: p.y * TT + 8 }; }

  function sansLeDe(graine, fn) {
    const de = B.rng;
    let s = graine >>> 0;
    B.rng = function () { s = hash2(s + 1, 0x5EED); return (s % 100000) / 100000; };
    try { return fn(); } finally { B.rng = de; }
  }

  function reveiller(e) {
    if (!e || !e.vivant || e.etat === 'assomme') return;
    e.plante = null; e.etat = 'attaque_joueur'; e.cri = 90;
    Entites.bulle(e, BULLES.garde, { duree: 120 });
  }

  function donner(objet, nom) {
    if (!B.partie.objets) B.partie.objets = {};
    B.partie.objets[objet] = 1;
    Hud.message(nom || objet.toUpperCase(), 200);
    if (objet === 'sacs_caisse') Son.SFX.argent(); else Son.SFX.ramasse();
  }

  /** L'etat du passage en cours (null dehors) : `mode`, `phase` (`calme`, `minuterie`, `ouverte`, `vide`), le compte
      `t`, les vagues deja entrees, et si le vigile t'a reconnu. Il se perd a la sortie : un coup ressorti les mains
      vides se recommence. */
  function etat() { return B.casse || null; }

  function entrer(o) {
    const c = B.casse = { mode: o ? OBJETS[o.objet] : null, phase: 'calme', t: 0, vagues: 0, reconnu: false, vu: 0 };
    if (!o || possede(o.objet)) return c;
    const f = vigile(), livreur = Histoire.porteLaTenue(TENUE);
    if (c.mode === 'coup' && !livreur) {
      // SANS L'UNIFORME, Fernand te connait pas : il crie, la caissiere pese sur l'alarme, et il te saute dessus.
      c.reconnu = true;
      if (f) { reveiller(f); Entites.bulle(f, BULLES.reconnu, { duree: 150 }); }
      Police.etoilesAuMoins(REGLES.etoiles_reconnu);
      Son.SFX.alarme_commerce();
      Hud.message('LE GARDE T’A RECONNU — PAS D’UNIFORME', 200);
    } else if (f && livreur && (c.mode === 'coup' || c.mode === 'livraison')) {
      Entites.bulle(f, BULLES.salut_livreur, { duree: 120 });
    }
    return c;
  }

  /** Les gardes du fourgon : `n` hommes par la PORTE D'EN ARRIERE (`piece.arriere`, au bout de l'allee derriere les
      guichets) — le fourgon decharge par la ruelle. Faute d'elle, par la porte d'entree. */
  function vague(k, n) {
    const piece = B.interieur, ar = piece.arriere, m = Histoire.courante();
    const dedans = ar ? (ar.x === 0 ? 1 : -1) : 0;
    const x0 = ar ? (ar.x + dedans) * TT + 8 : piece.apparition.x * TT + 8, y0 = ar ? ar.y * TT + 8 : piece.apparition.y * TT + 4;
    sansLeDe(hash2(0xCA15E, k), function () {
      for (let i = 0; i < n; i++) {
        const e = Entites.creerPieton(ar ? x0 + dedans * i * 14 : x0 + (i - (n - 1) / 2) * 14, y0, Entites.archetype('garde'));
        e.vie = e.vieMax = REGLES.garde_vie; e.arme = 'batte'; e.courage = 1; e.temoin = 0;
        e.mission = m ? m.slug : null; e.gardeDuFourgon = true;
        reveiller(e);
      }
    });
    Entites.indexer();
    Hud.message('LES GARDES DU FOURGON!', 150);
  }

  /** -1 derriere le comptoir, 1 devant, 0 dans sa rangee (la porte battante). */
  function cote(y, b) { return y < b.y * TT ? -1 : y >= (b.y + 1) * TT ? 1 : 0; }

  /** ⚠️ UN PIETON NE CHERCHE PAS SON CHEMIN : il court droit sur toi (`attaque_joueur`). Le comptoir des guichets
      barre la piece d'un mur a l'autre — Fernand restait colle au comptoir pendant toute la minute, et les gardes du
      fourgon de l'autre bord. Qui doit changer de cote passe par la PORTE BATTANTE (`piece.battante`) : trois pas
      (`cap`), puis il reprend l'attaque. */
  function guider(e, j, b) {
    if (e.chemin && e.chemin.length) {
      if (e.etat !== 'cap' && e.etat !== 'attaque_joueur') { e.chemin = null; return; }   // frappe, assomme : il oublie
      const c = e.chemin[0];
      // ⚠️ 14 et pas 10 : l'etat `cap` s'arrete a 12 px de son but (`entites.js`) — a 10, il attendait pour toujours.
      if (Math.hypot(c.x - e.x, c.y - e.y) < 14) e.chemin.shift();
      if (!e.chemin.length) { e.chemin = null; e.cap = null; e.etat = 'attaque_joueur'; return; }
      e.etat = 'cap'; e.cap = e.chemin[0]; e.capVite = true; e.capT = 0;
      return;
    }
    const ce = cote(e.y, b), cj = cote(j.y, b);
    if (e.etat !== 'attaque_joueur' || !ce || !cj || ce === cj) return;
    const gx = b.x * TT + 8;
    e.chemin = [{ x: gx, y: (b.y + ce) * TT + 8 }, { x: gx, y: b.y * TT + 8 }, { x: gx, y: (b.y - ce) * TT + 8 }];
    guider(e, j, b);
  }

  function maj() {
    if (!ici()) { B.casse = null; return; }
    if (B.cinema || B.menu) return;
    const b = B.interieur.battante;
    if (b) for (const e of B.entites) if (e.type === 'pieton' && e.vivant && (e.vigile || e.gardeDuFourgon)) guider(e, B.joueur, b);
    const o = objectif();
    let c = B.casse;
    if (!c) c = entrer(o);
    if (!o || possede(o.objet)) {
      // Les sacs pris : l'alarme sonne toujours, la police attend dehors — elle ne t'oublie pas dans la caisse.
      if (c.mode === 'coup' && c.phase !== 'calme') B.recherche.vu = 0;
      return;
    }
    const j = B.joueur;
    if (c.mode === 'reperage') {
      const v = voute();
      if (!v) return;
      const p = centre(v);
      if (Math.hypot(j.x - p.x, j.y - p.y) < REGLES.reperage_px) {
        if (++c.vu === 1) Hud.message('COMPTE LES BOULONS… PAS DE PRESSE', 120);
        if (c.vu >= REGLES.reperage_images) {
          donner(o.objet, o.nom);
          const g = gerant();
          if (g) Entites.bulle(g, BULLES.reperage, { duree: 150 });
        }
      }
      return;
    }
    if (c.mode !== 'coup' || c.phase === 'calme') return;
    // L'ALARME SONNE TANT QU'ON EST LA : dedans, d'habitude, on se fait oublier (`Police.decroitre`) — pas ici.
    B.recherche.vu = 0;
    if (c.phase !== 'minuterie') return;
    c.t++;
    const s = c.t / 60;
    while (c.vagues < REGLES.vagues.length && s >= REGLES.vagues[c.vagues].a_s) {
      vague(c.vagues, REGLES.vagues[c.vagues].n);
      c.vagues++;
    }
    const reste = Math.ceil(REGLES.minuterie_s - s);
    if (c.t % (REGLES.annonce_s * 60) === 0 && reste > 0) Hud.message('LA VOÛTE S’OUVRE DANS ' + reste + ' S', 120);
    if (s >= REGLES.minuterie_s) {
      c.phase = 'ouverte';
      const g = gerant();
      if (g) Entites.bulle(g, BULLES.ouverte, { duree: 150 });
      Son.SFX.porte('commerce');
      Hud.message('LA VOÛTE EST OUVERTE — PRENDS LES SACS', 200);
    }
  }

  /** LA VOUTE (le point `voute`) : demarrer le coup, prendre les sacs — ou, sans mission, une porte d'acier. */
  function agir(j, point) {
    const o = objectif(), c = B.casse || entrer(o);
    if (!o || c.mode !== 'coup' || possede(o.objet)) {
      Hud.message('LA VOÛTE : UNE MINUTERIE. SEUL LE GÉRANT L’OUVRE.', 150);
      Son.SFX.erreur();
      return true;
    }
    if (c.phase === 'calme') {
      c.phase = 'minuterie'; c.t = 0;
      const g = gerant();
      if (g) { Entites.bulle(g, BULLES.minuterie, { duree: 180 }); g.vx = 0; g.vy = 0; }
      for (const e of B.entites) {
        if (e.type !== 'pieton' || !e.vivant || e === g || e === j) continue;
        if (e.vigile) reveiller(e);
        else if (e.poste && !e.gerant) Entites.bulle(e, BULLES.caissiere, { duree: 150 });
        else if (!e.gerant) { e.etat = 'fuit'; e.menace = j; e.minuterie = 600; }
      }
      Police.etoilesAuMoins(REGLES.etoiles_alarme);
      Son.SFX.alarme_commerce();
      Hud.message('L’ALARME! TIENS UNE MINUTE', 200);
      return true;
    }
    if (c.phase === 'minuterie') {
      Hud.message('LA VOÛTE S’OUVRE DANS ' + Math.ceil(REGLES.minuterie_s - c.t / 60) + ' S', 90);
      return true;
    }
    if (c.phase === 'ouverte') {
      c.phase = 'vide';
      donner(o.objet, o.nom);
      Hud.message((o.nom || 'LES SACS') + ' — SORS!', 200);
      return true;
    }
    return true;
  }

  /** Le gerant a portee de main, quand il y a un colis a lui livrer (la LIVRAISON) : il passe avant la voute. */
  function gerantSousLaMain(j) {
    const o = objectif();
    if (!ici() || !o || OBJETS[o.objet] !== 'livraison' || possede(o.objet)) return null;
    const g = gerant();
    return g && Math.hypot(g.x - j.x, g.y - j.y) < REGLES.gerant_px ? g : null;
  }

  function livrer(j) {
    const g = gerantSousLaMain(j), o = objectif();
    if (!g || !o) return false;
    if (!Histoire.porteLaTenue(TENUE)) {
      Entites.bulle(g, BULLES.livraison_refusee, { duree: 150 });
      Hud.message('ENFILE L’UNIFORME DE LIVREUR', 150);
      Son.SFX.erreur();
      return true;
    }
    Entites.bulle(g, BULLES.livraison, { duree: 150 });
    const f = vigile();
    if (f) Entites.bulle(f, BULLES.salut_livreur, { duree: 120 });
    donner(o.objet, o.nom);
    return true;
  }

  /** L'invite d'ACTION, dedans — dans l'ordre d'`utiliserPoint`. */
  function invite(j) {
    if (!ici()) return null;
    if (gerantSousLaMain(j)) return 'LIVRER LE COLIS';
    const o = objectif(), c = B.casse, v = voute();
    if (!o || OBJETS[o.objet] !== 'coup' || !v || possede(o.objet)) return null;
    const p = centre(v);
    if (Math.hypot(j.x - p.x, j.y - p.y) > 1.6 * TT + 8) return null;
    return !c || c.phase === 'calme' ? 'LA MINUTERIE!' : c.phase === 'ouverte' ? 'PRENDRE LES SACS' : null;
  }

  /** La porte d'en arriere, peinte sur son mur (une piece n'a qu'une porte-tuile) : le metal gris, la barre. */
  function dessinerPorteArriere(ctx, vue) {
    const ar = B.interieur.arriere;
    if (!ar) return;
    const x = Math.round(ar.x * TT - vue.x), y = Math.round(ar.y * TT - vue.y);
    ctx.fillStyle = '#4a4e54'; ctx.fillRect(x + 2, y, 12, TT);
    ctx.fillStyle = '#7a8088'; ctx.fillRect(x + 3, y + 1, 10, TT - 1);
    ctx.fillStyle = '#c8ccd0'; ctx.fillRect(x + 4, y + 8, 8, 2);                  // la barre panique
    ctx.fillStyle = '#c0392b'; ctx.fillRect(x + 6, y + 2, 4, 2);                  // la petite lumiere rouge
  }

  /** Au-dessus de la voute, pendant le coup : le compte a rebours de la minuterie, en rouge. */
  function dessiner(ctx, vue) {
    if (!ici()) return;
    dessinerPorteArriere(ctx, vue);
    const c = B.casse, v = voute();
    if (!c || c.phase !== 'minuterie' || !v) return;
    const reste = Math.max(0, Math.ceil(REGLES.minuterie_s - c.t / 60));
    const x = v.x * TT + 8 - vue.x, y = (v.y - 1) * TT - 10 - vue.y;
    ctx.save();
    ctx.fillStyle = 'rgba(20,10,10,0.75)'; ctx.fillRect(Math.round(x) - 12, Math.round(y) - 6, 24, 11);
    ctx.fillStyle = (c.t >> 4) % 2 ? '#ff5a4a' : '#ffd0c8';
    ctx.font = '8px monospace'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(String(reste), Math.round(x), Math.round(y));
    ctx.restore();
  }

  return { SLUG, OBJETS, TENUE, REGLES, BULLES, ici, objectif, etat, maj, agir, gerantSousLaMain, livrer, invite, dessiner };
})();
