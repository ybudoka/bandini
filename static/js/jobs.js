/* LES PETITES JOBS (M16, arc T, 1er oct. 2026 — Martin : « un passant qui donne une job »).

   Un passant ORDINAIRE — pas un personnage de l'histoire : un banlieusard aux Érables, un débardeur aux Quais —
   te repère, s'approche, te hèle (sa bulle, sa voix de passant), et te propose une courte mission. ACTION à côté de
   lui : son intro, et la job commence, sans téléphone. Une mission qui a la clé `passant` (`missions.py`) ne
   s'offre JAMAIS autrement : ni au téléphone, ni au carnet, ni par une bulle de donneur (`Histoire.disponibles`).

   ⚠️ IL NAÎT À L'EMPREINTE. Ni dé ni numéro de la ville : son numéro vient de la plage à part
   (`Entites.enDehorsDeLaSuite`), les deux dés de `creerPieton` d'un dé PRÊTÉ (`sansLeDe`), sa tenue de la garde-robe
   de son archétype à l'empreinte de la demi-journée, et sa place d'une spirale sans dé autour du joueur. La ville
   d'une partie où il se présente est la même, au tirage près, que celle où il ne se présente pas.

   ⚠️ LA CADENCE : une job à la fois, jamais pendant une mission (ni un défi, une poursuite, une sonnerie), à pied, et
   une offre par DEMI-JOURNÉE au plus (`partie.jobOfferte`), une minute et demie au moins après la dernière mission.
   Ce sont des rencontres, pas un tableau de bord (la fiche de l'arc T). Une offre qu'on ne prend pas (on s'en va, on
   ne lui parle pas) ne se perd pas : la job reviendra une autre demi-journée. */
const Jobs = (function () {
  'use strict';

  //: Pas d'offre avant tant d'images sans mission (le chargement, une mission finie ou ratée) : une minute et demie.
  const PAS_AVANT = 90 * 60;
  //: Où il apparaît : entre tant et tant de tuiles du joueur, sur un trottoir d'où il peut marcher jusqu'à lui.
  const LOIN_MIN = 7, LOIN_MAX = 11;
  //: Il hèle à cette distance (sa bulle, sa voix) — assez près pour qu'on l'entende, assez loin pour le voir venir.
  const HELE_PX = 13 * TT;
  //: Il s'arrête à cette distance du joueur : en deçà de celle où l'on se parle (`RAYON_PARLER` de `histoire.js`,
  //: 22 px) — la foule le décolle d'un ou deux pixels en attendant, et ACTION doit encore le trouver.
  const PRES_PX = 16;
  //: Il renonce : trop loin, ou trente secondes qu'il attend qu'on lui parle.
  const RENONCE_PX = 18 * TT, ATTENTE = 30 * 60;
  //: Ce qu'il dit en s'en allant, sans voix (une bulle) — on l'a laissé en plan.
  const TANT_PIS = 'Laisse faire.';

  //: ⚠️ La cadence vit dans `B.jobRepos` : l'image avant laquelle aucun passant ne se présente — `PAS_AVANT` après le
  //: chargement (`B.t` repart de zéro), puis après chaque image où une mission tournait.

  function p() { return B.partie; }
  function demiJournee() { return B.partie.jour * 2 + (B.partie.heure >= 0.5 ? 1 : 0); }
  function mission(slug) { return (B.defs.missions || []).find(function (m) { return m.slug === slug; }) || null; }

  /** Les jobs qu'un passant peut offrir maintenant : prérequis faits, pas faites, pas fermées, `exige` tenu. */
  function offertes() {
    const q = p();
    return (B.defs.missions || []).filter(function (m) {
      return m.passant && !q.missionsFaites[m.slug] && (q.fermees || []).indexOf(m.slug) < 0 &&
        m.prerequis.every(function (s) { return !!q.missionsFaites[s]; }) && Histoire.exigeTenu(m.exige);
    });
  }

  /** `fn` jouée avec un dé PRÊTÉ (le motif d'`Autobus` et d'`Entites`) : la file du jeu ne bouge pas d'un tirage. */
  /** ⚠️ LES PETITES JOBS VOYAGENT PLIÉES (`missions.jobs_pour_le_navigateur`, l'ordre de `CHAMPS_D_UNE_JOB`) : à
      l'arrivée du paquet, on les remet dans le catalogue — une fois, sans doublon —, et tout le reste du jeu (le
      carnet, la triche, `Histoire.mission`) les trouve là comme les autres. Rend `defs`. */
  function deplier(defs) {
    if (!defs || !Array.isArray(defs.jobs) || defs.jobsDepliees) return defs;
    const missions = defs.missions || (defs.missions = []);
    const deja = {};
    missions.forEach(function (m) { deja[m.slug] = true; });
    defs.jobs.forEach(function (j) {
      if (!Array.isArray(j) || deja[j[0]]) return;
      missions.push({ slug: j[0], titre: j[1], donneur: j[2], recompense: j[3], passant: j[4], prerequis: j[5] || [] });
    });
    defs.jobsDepliees = true;
    return defs;
  }

  function sansLeDe(graine, fn) {
    const de = B.rng;
    let s = graine >>> 0;
    B.rng = function () { s = hash2(s + 1, 0x5EED); return (s % 100000) / 100000; };
    try { return fn(); } finally { B.rng = de; }
  }

  /** Qui, et où : `{ archetype, district }` — le catalogue porte « archétype@district » (`*` : partout), la mission
      chargée le passant entier (`missions._au_catalogue`, `pour_jouer`). */
  function fiche(m) {
    const pa = m && m.passant;
    if (!pa) return null;
    if (typeof pa === 'object') return { archetype: pa.archetype, district: pa.district || null };
    const deux = String(pa).split('@');
    return { archetype: deux[0], district: deux[1] && deux[1] !== '*' ? deux[1] : null };
  }

  /** Le district sous le joueur (null hors de tout district). */
  function districtDe(x, y) { const z = Monde.zoneA(x, y); return z ? z.district : null; }

  /** La job d'ici : parmi les offertes, celles de ce district (ou de partout) — une à l'empreinte de la
      demi-journée. Null s'il n'y en a pas. */
  function choisir(district) {
    const liste = offertes().filter(function (m) { const f = fiche(m); return !f.district || f.district === district; });
    return liste.length ? liste[hash2(demiJournee(), 0x7B05) % liste.length] : null;
  }

  /** Un pas de piéton entre deux tuiles, en ligne droite, sans mur : il peut venir jusqu'à nous. */
  function ligneLibre(x0, y0, x1, y1) {
    const n = Math.ceil(Math.hypot(x1 - x0, y1 - y0) / 8);
    for (let k = 1; k < n; k++) {
      const x = x0 + (x1 - x0) * k / n, y = y0 + (y1 - y0) * k / n;
      if (Monde.bloque(Math.floor(x / TT), Math.floor(y / TT), Monde.MASQUE_PIETON)) return false;
    }
    return true;
  }

  /** Où il apparaît : une spirale sans dé, dont le premier cap tourne avec l'empreinte — un trottoir (ni la chaussée,
      ni le pas d'une porte, ni l'eau), du même district, d'où il marche jusqu'à nous en ligne droite. */
  function place(j, graine, district, pres) {
    const tx0 = Math.floor(j.x / TT), ty0 = Math.floor(j.y / TT), depart = hash2(graine, 0x51) % 24;
    for (let r = pres ? 2 : LOIN_MIN; r <= (pres ? 6 : LOIN_MAX); r++) {
      for (let k = 0; k < 24; k++) {
        const a = (depart + k) / 24 * Math.PI * 2;
        const tx = tx0 + Math.round(Math.cos(a) * r), ty = ty0 + Math.round(Math.sin(a) * r);
        if (!Monde.marchablePieton(tx, ty) || Monde.estChaussee(tx, ty) || Monde.estEau(tx, ty) || Monde.devantDUnePorte(tx, ty)) continue;
        const x = tx * TT + 8, y = ty * TT + 8;
        if (district && districtDe(x, y) !== district) continue;
        if (!ligneLibre(x, y, j.x, j.y)) continue;
        return { x: x, y: y };
      }
    }
    return null;
  }

  /** Il naît, à l'empreinte (voir l'en-tête), et se met en marche vers le joueur. */
  function poser(m, pres) {
    const j = B.joueur;
    const graine = hash2(demiJournee(), hash2(m.slug.length, m.slug.charCodeAt(m.slug.length - 1)));
    // `pres` (la triche, les bancs) : à deux pas, où qu'on soit — sinon de son district, et le temps de le voir venir.
    const f = fiche(m);
    const l = place(j, graine, pres ? null : f.district, pres);
    if (!l) return null;
    const base = Entites.archetype(f.archetype);
    // ⚠️ Sans son petit (`accompagne`, la mère) : il naîtrait avec elle, au numéro de la ville. Sans le sou et
    // intouchable, comme un personnage : on ne détrousse pas celui qui vient nous offrir une job.
    const arch = Object.assign({}, base, {
      accompagne: null, argent: [0, 0], intouchable: true,
      tenue: typeof Garderobe !== 'undefined' ? Garderobe.tirer(base.slug, hash2(graine, 0x7e4e)) : null,
    });
    const e = Entites.enDehorsDeLaSuite(function () {
      return sansLeDe(graine, function () { return Entites.creerPieton(l.x, l.y, arch); });
    });
    e.personnage = m.donneur; e.job = m.slug; e.cri = 0;
    e.etat = 'cap'; e.cap = { x: j.x, y: j.y }; e.capT = 0;
    B.job = { slug: m.slug, e: e, t: B.t, phase: 'approche', hele: false };
    Histoire.charger(m.slug);
    return e;
  }

  /** Le peut-il, maintenant ? Une job à la fois, jamais pendant une mission, un défi, une poursuite ou une
      sonnerie ; à pied, dehors, dans un district ; une offre par demi-journée, et pas trop tôt. */
  function peutSePresenter() {
    const q = p(), j = B.joueur;
    if (!q || !j || B.job || q.mission || B.interieur || B.bloc || B.scene || B.cinema || B.menu) return false;
    if (B.finEnAttente || B.sonnerie || B.defi || B.epreuve || B.conduite || B.rue || j.dansVehicule || !j.vivant) return false;
    if ((B.recherche && B.recherche.etoiles) || 0) return false;
    if (B.t < (B.jobRepos === undefined || B.jobRepos === null ? PAS_AVANT : B.jobRepos)) return false;
    return q.jobOfferte !== demiJournee();
  }

  /** Le hèlement : sa bulle (le texte de `hele`), et sa voix de passant. */
  function heler(job, m) {
    job.hele = true;
    const l = m.dialogue && m.dialogue.hele && m.dialogue.hele[0];
    if (!l) return;
    Son.Voix.chargerHistoire(m.slug);
    Son.Voix.parler(Histoire.slugDeVoix(m, 'hele', 0), {});
  }

  /** Ce que dit sa bulle : son hèlement tant qu'il t'offre la job, son mot de personnage quand la job attend qu'on
      revienne le voir (`retourner`), rien sinon. */
  function bulle(e) {
    const job = B.job, m = job && job.e === e ? mission(job.slug) : null;
    if (!m) { Entites.bulle(e, ''); return; }
    const l = m.dialogue && m.dialogue.hele && m.dialogue.hele[0];
    const perso = Histoire.personnage(m.donneur);
    if (job.phase === 'approche' || job.phase === 'attend') { Entites.bulle(e, job.hele ? (l ? l.texte : perso.heler) : ''); return; }
    const o = Histoire.objectif();
    Entites.bulle(e, job.phase === 'pris' && o && o.type === 'retourner' ? perso.heler : '');
  }

  /** Il s'en va : redevenu un passant comme les autres, il flâne, et la ville l'oubliera quand on sera loin. */
  function partir(job, mot) {
    const e = job.e;
    B.job = null;
    if (!e) return;
    e.job = null; e.personnage = null; e.plante = null; e.cap = null; e.suit = null;
    e.etat = 'flane'; e.intouchable = false;
    Entites.bulle(e, mot || '', mot ? { duree: 150 } : undefined);
  }

  /** On lui parle (ACTION, `Histoire.parler`) : la job qu'il offre, s'il en offre une ; null sinon. */
  function offreDe(slug) {
    const job = B.job;
    if (!job || p().mission || !job.e || job.e.personnage !== slug) return null;
    if (job.phase !== 'approche' && job.phase !== 'attend') return null;
    const m = mission(job.slug);
    if (!m || offertes().indexOf(m) < 0) return null;
    prendre(job);
    return m;
  }

  /** La job est prise : il s'arrête là où il est, et son intro va se dire. */
  function prendre(job) {
    job.phase = 'prend'; job.t = B.t;
    const e = job.e;
    e.etat = 'fige'; e.plante = { x: e.x, y: e.y }; e.cap = null; e.vx = 0; e.vy = 0;
  }

  /** Une image : il approche, il attend, il s'en va — ou la job tourne, et c'est la mission qui le mène. */
  function suivre(job) {
    const e = job.e, j = B.joueur, q = p(), pm = q.mission;
    if (!e || B.entites.indexOf(e) < 0 && !B.interieur) { B.job = null; return; }
    if (pm && pm.slug === job.slug) { job.phase = 'pris'; return; }
    // La job vient de finir (réussie ou ratée) : sa fin se dit d'abord, puis il s'en va.
    if (job.phase === 'pris') { if (!B.finEnAttente && !B.cinema && !B.scene) partir(job); return; }
    // Son intro part (le texte arrive, la scène joue) : on lui laisse dix secondes.
    if (job.phase === 'prend') { if (B.t - job.t > 600) partir(job); return; }
    // Une autre mission a commencé (le téléphone, un autre donneur) : il n'insiste pas.
    if (pm || B.interieur) { partir(job); return; }
    const m = mission(job.slug);
    const d = Math.hypot(e.x - j.x, e.y - j.y);
    if (d > RENONCE_PX || B.t - job.t > ATTENTE) { partir(job, TANT_PIS); return; }
    if (!job.hele && d < HELE_PX && m && m.dialogue) heler(job, m);
    if (job.phase === 'approche') {
      if (d <= PRES_PX + 4) { job.phase = 'attend'; e.etat = 'fige'; e.plante = { x: e.x, y: e.y }; e.cap = null; e.vx = 0; e.vy = 0; }
      else {
        // Il vient À CÔTÉ de nous, pas dedans : un piéton s'arrête à douze pixels de son cap (`Entites`), le cap est
        // donc à quatre pixels de nous — il s'arrête à seize, à portée de parole.
        e.etat = 'cap'; e.capT = 0;
        e.cap = { x: j.x + (e.x - j.x) / d * (PRES_PX - 12), y: j.y + (e.y - j.y) / d * (PRES_PX - 12) };
      }
    } else if (job.phase === 'attend' && d > PRES_PX * 4) {
      job.phase = 'approche'; e.plante = null;
    }
    if (job.phase === 'attend') e.face = Math.abs(j.x - e.x) >= Math.abs(j.y - e.y) ? (j.x > e.x ? 'droite' : 'gauche') : (j.y > e.y ? 'bas' : 'haut');
  }

  function maj() {
    const q = p();
    if (!q || !B.joueur) return;
    if (q.mission) B.jobRepos = B.t + PAS_AVANT;
    if (B.job) { suivre(B.job); return; }
    if (!peutSePresenter()) return;
    const m = choisir(districtDe(B.joueur.x, B.joueur.y));
    // ⚠️ L'offre de la demi-journée est faite dès qu'on a choisi — même si aucun trottoir ne s'y prête : sinon on la
    // rechercherait à chaque image.
    if (!m) return;
    q.jobOfferte = demiJournee();
    poser(m);
  }

  /** (Triche, bancs) Le passant de la job `slug` se présente MAINTENANT, à côté du joueur — sans regarder la
      cadence ni ce qui est offert. */
  function offrir(slug, pres) {
    const m = mission(slug);
    if (!m || !m.passant || !B.joueur) return null;
    if (B.job) partir(B.job);
    const e = poser(m, pres) || null;
    // À deux pas (la triche, les bancs) : il attend là, on n'a qu'à lui parler.
    if (e && pres) { B.job.phase = 'attend'; B.job.hele = true; e.etat = 'fige'; e.plante = { x: e.x, y: e.y }; e.cap = null; }
    return e;
  }

  /** Une nouvelle partie, un rechargement : personne ne t'attend. */
  function oublier() { B.job = null; B.jobRepos = null; }

  return { maj, deplier, fiche, offertes, choisir, offreDe, bulle, offrir, oublier, demiJournee, PAS_AVANT, LOIN_MIN, LOIN_MAX, PRES_PX };
})();
