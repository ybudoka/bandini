/* BISCUIT, LE CHIEN DE MME BEAULIEU (M16, e03 — 1er oct. 2026 ; la fiche : « Biscuit te suit dans les Érables »).

   Avant e03, il s'est sauvé : c'est la mission (`chercher` avec `bete`, `Histoire.majFugue`). Après, il est aux pieds de
   sa maîtresse, devant le dépanneur — assis, la queue qui balaie le trottoir. Et il t'a adopté : à pied, passe près de
   lui, et il te suit dans les Érables, au trot, sur tes talons. Monte en char, sors des Érables ou éloigne-toi trop
   d'elle, et il retourne s'asseoir à ses pieds.

   ⚠️ UN PIÉTON PEINT EN BÊTE (`e.bete`, `Entites.poseDePietonBete`), intouchable, sans le sou. ⚠️ IL NAÎT À L'EMPREINTE
   (le motif du passant des petites jobs, `jobs.js`) : un numéro hors de la suite (`Entites.enDehorsDeLaSuite`), les deux
   dés de `creerPieton` d'un dé PRÊTÉ. La ville d'une partie où il est là est la même que celle où il n'est pas.

   Qui a un chien, et après quelle mission : la fiche du personnage (`chien`, `missions.PERSONNAGES`) — aucun slug ici. */
const Biscuit = (function () {
  'use strict';

  //: À pied, plus près que ça de lui, il se lève et te suit.
  const ADOPTE_PX = 2.5 * TT;
  //: Il te lâche si tu t'éloignes de sa maîtresse de plus que ça (il ne quitte pas son coin de rue pour toujours).
  const LAISSE_PX = 24 * TT;
  //: Revenu à moins de ça d'elle, il reprend sa place à ses pieds.
  const ASSIS_PX = 3.5 * TT;

  /** Le dé PRÊTÉ (le motif de `Jobs` et d'`Histoire`) : `creerPieton` en tire deux, la ville n'en saura rien. */
  function sansLeDe(graine, fn) {
    const de = B.rng;
    let s = graine >>> 0;
    B.rng = function () { s = hash2(s + 1, 0x5EED); return (s % 100000) / 100000; };
    try { return fn(); } finally { B.rng = de; }
  }

  /** Les personnages qui ont un chien rentré au bercail (`chien` : la mission qui le ramène, faite). */
  function maitres() {
    return (B.defs.personnages || []).filter(function (p) { return p.chien && Histoire.faite(p.chien); });
  }

  /** Il naît à ses pieds, à droite d'elle, à l'empreinte. */
  function naitre(m, p) {
    const base = Entites.archetype('passant');
    const arch = Object.assign({}, base, { accompagne: null, argent: [0, 0], intouchable: true, tenue: null });
    const graine = hash2(p.slug.length * 131 + p.slug.charCodeAt(0), 0xB15C);
    const e = Entites.enDehorsDeLaSuite(function () {
      return sansLeDe(graine, function () { return Entites.creerPieton(m.x + 12, m.y + 4, arch); });
    });
    e.bete = 'chien'; e.maitre = m; e.chienDe = p.slug; e.nomDeMission = 'BISCUIT';
    e.etat = 'fige'; e.plante = { x: m.x + 12, y: m.y + 4 }; e.courage = 0; e.cri = 0;
    Entites.indexer();
    return e;
  }

  /** Le chien de `p`, s'il est en ville. */
  function chienDe(p) {
    return B.entites.find(function (e) { return e.chienDe === p.slug && e.vivant; }) || null;
  }

  //: Un pas de piste tous les tant de pixels ; au-delà de tant de pas, les plus vieux s'effacent.
  const PAS_DE_PISTE = 12, PISTE_MAX = 300;

  /** ⚠️ IL MARCHE SUR TES PAS, PAS EN LIGNE DROITE (le motif de l'escorté, `Histoire.suivreLaPiste`) : en ligne droite,
      l'abribus et l'édicule du métro devant le dépanneur l'arrêtaient à cinq tuiles derrière toi. Là où tu as mis les
      pieds, il y a de la place pour lui. */
  function suivreLaPiste(c, j) {
    const piste = c.piste || (c.piste = []);
    const bout = piste.length ? piste[piste.length - 1] : null;
    if (!bout || Math.hypot(j.x - bout.x, j.y - bout.y) > PAS_DE_PISTE) piste.push({ x: j.x, y: j.y, vivant: true });
    if (piste.length > PISTE_MAX) piste.shift();
    if (Math.hypot(c.x - j.x, c.y - j.y) < 3 * TT) { piste.length = 0; c.suit = j; return; }
    const atteint = B.defs.pietons.reactions.suite_distance_px + 4;
    while (piste.length > 1 && Math.hypot(c.x - piste[0].x, c.y - piste[0].y) < atteint) piste.shift();
    c.suit = piste[0] || j;
  }

  /** Une image : il naît à ses pieds, il t'adopte, il te suit, il rentre. */
  function maj() {
    const j = B.joueur;
    if (!B.partie || !j || B.interieur || B.bloc) return;
    for (const p of maitres()) {
      const m = B.entites.find(function (e) { return e.personnage === p.slug && e.vivant; }) || null;
      let c = chienDe(p);
      // Sa maîtresse n'est pas en ville (trop loin, partie, en mission ailleurs) : lui non plus.
      if (!m) { if (c) Entites.retirer(c); continue; }
      if (!c) c = naitre(m, p);
      c.maitre = m;
      const dJ = Math.hypot(c.x - j.x, c.y - j.y), dM = Math.hypot(j.x - m.x, j.y - m.y);
      const zone = Monde.zoneA(j.x, j.y), memeCoin = zone && zone.district === (Monde.zoneA(m.x, m.y) || {}).district;
      const libre = !j.dansVehicule && j.vivant && !B.partie.mission && memeCoin && dM < LAISSE_PX;
      if (c.suiveur) {
        // Il te suit tant que tu marches dans son coin : sinon, il rentre — PAR OÙ IL EST VENU (`chemin`, ses propres
        // pas à rebours : l'édicule du métro est entre elle et la rue, en ligne droite il s'y collait).
        if (!libre) {
          c.suiveur = false; c.piste = null; c.vitesseSuite = null;
          c.retour = (c.chemin || []).slice().reverse().concat([{ x: m.x + 12, y: m.y + 4, vivant: true }]);
          c.chemin = null;
        } else {
          const bout = c.chemin && c.chemin[c.chemin.length - 1];
          if (!c.chemin) c.chemin = [];
          if (!bout || Math.hypot(c.x - bout.x, c.y - bout.y) > PAS_DE_PISTE) c.chemin.push({ x: c.x, y: c.y, vivant: true });
          if (c.chemin.length > PISTE_MAX) c.chemin.shift();
          suivreLaPiste(c, j);
        }
        continue;
      }
      if (c.retour) {
        // Il rentre, pas à pas ; le dernier, c'est sa place à ses pieds.
        const atteint = B.defs.pietons.reactions.suite_distance_px + 4;
        while (c.retour.length > 1 && Math.hypot(c.x - c.retour[0].x, c.y - c.retour[0].y) < atteint) c.retour.shift();
        if (c.retour.length <= 1 && Math.hypot(c.x - m.x, c.y - m.y) < ASSIS_PX) {
          c.retour = null; c.suit = null; c.etat = 'fige'; c.plante = { x: m.x + 12, y: m.y + 4 }; c.vx = 0; c.vy = 0;
        } else c.suit = c.retour[0];
        continue;
      }
      if (libre && dJ < ADOPTE_PX) {
        c.suiveur = true; c.suit = j; c.plante = null; c.piste = [];
        c.vitesseSuite = B.defs.recherche.vitesses.joueur_sprint;
        Entites.bulle(c, 'WOUF!', { duree: 60 });
      }
    }
  }

  return { maj, maitres, chienDe, ADOPTE_PX, LAISSE_PX };
})();
