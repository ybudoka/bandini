/* Bandini — ça travaille : les chantiers, joués jour après jour.

   ⚠️ Python décide (`app/chantiers.py`) : quels bâtiments, les tuiles de chacune
   des cinq phases, où travaillent les machines — et toute la géométrie s'y juge
   phase par phase. Ce script ne fait que POSER la phase du jour.

   ⚠️ Et il ne la pose JAMAIS sous les yeux du joueur. Une phase qui avance change
   des tuiles, recuit des morceaux et remplace des machines : vu en direct, c'est
   un bâtiment qui s'évapore d'une image à l'autre. On attend donc que le chantier
   soit hors de l'écran — et que personne ne se tienne dans son empreinte, parce
   que le neuf remonte des murs exactement là où l'on marchait la veille.

   2e vague : le chantier TRAVAILLE — la boule frappe le mur, la pelle racle, on
   l'entend avant de le voir, et il se tait la nuit (`travailler`).

   3e vague : il DÉBORDE de sa palissade et il prend du monde. La tranchée ouverte
   dans la rue d'en face (des plaques d'acier qui claquent sous les roues, puis
   l'asphalte refait) et l'équipe : des ouvriers plantés au poste que Python leur
   a choisi, qui regardent passer.

   7e vague : de nouveaux chantiers QUAND LES PREMIERS SONT FINIS. Un chantier DORMANT
   (`d.ouvre` : le jour où il ouvre) laisse sa maison telle quelle — pas une planche, pas
   un panneau, pas un homme — et s'éveille à la maison condamnée, hors de vue, comme
   toute autre phase.

   8e vague : la PELLE se conduit (l'étage 2 du plan). Le décor animé de la phase « rasé » cède sa
   place à un vrai char, `pelleteuse`, quand on monte dedans — plus de godet qui racle, plus de son.

   9e vague : la CABINE DE LA GRUE. Elle ne roulera jamais : on monte dedans, on tourne la flèche
   (gauche, droite), et ACTION redescend. Ce n'est pas un char, c'est un MODE : `j.manege`, le nom
   que toutes les gardes du jeu connaissent déjà (plus de combat, plus de marche, plus d'invite).

   4e vague : le SIGNALEUR — un homme sur le trottoir, au bout amont de la tranchée,
   dont la palette alterne ARRÊT et LENTEMENT. Le trafic de sa voie obéit à ARRÊT
   (`signalDevant`, lu par `Vehicules.obstacleDevant`). */

const Chantiers = (function () {
  'use strict';

  //: On ne vérifie qu'une image sur trente : une phase qui attend peut attendre
  //: une demi-seconde de plus, et la ville n'a rien à gagner à être sondée
  //: soixante fois par seconde pour un changement qui arrive tous les trois jours.
  const CADENCE = 30;
  //: La marge autour de la vue. ⚠️ Plus haute au NORD : la grue à tour monte à
  //: plus de cinq tuiles au-dessus de son pied, et sa flèche se voit bien avant
  //: le chantier lui-même.
  const MARGE_PX = 40;
  const MARGE_NORD_PX = 96;
  //: Ce qui empêche une phase de se poser : un CORPS dans l'empreinte. Les
  //: objets par terre, eux, sont poussés dehors (voir `degager`).
  const CORPS = { joueur: 1, pieton: 1, agent: 1, vehicule: 1 };

  //: ⚠️ LE CHANTIER S'ENTEND. Portées en px : au-delà, rien ne part. Deux
  //: chantiers sont à 48 tuiles l'un de l'autre, on n'en entend donc jamais deux.
  //: La boule porte plus loin : c'est le coup qui fait tourner la tête.
  const PORTEE_SON = 340;
  const PORTEE_BOULE = 460;
  const PORTEE_RUMEUR = 380;
  //: Ce qu'on ne VOIT pas venir revient sur une horloge : [son, période en
  //: images, décalage]. Le godet et la boule, eux, partent au geste qu'on voit.
  const HORLOGES = {
    1: [['marteau_piqueur', 610, 150]],
    2: [['marteau_piqueur', 700, 420], ['bip_recul', 760, 60]],
    3: [['marteau', 170, 40], ['scie', 820, 300]],
  };
  //: La pelle racle à chaque tour de bras (54 images) ; son godet de deux
  //: secondes n'en suit qu'un sur trois, sinon il se marche dessus.
  const GODET_TOURS = 3;
  //: Au coup de boule, le point de contact : le bord du mur, à 24 px du centre de
  //: la machine (deux tuiles moins une demi — voir `BOULE` dans `sprites.js`), et
  //: 20 px au-dessus de son pied, là où pend la boule.
  const CONTACT_X = 24, CONTACT_Y = 20;
  //: L'équipe regarde le joueur passer, de plus près que ça ; sinon elle regarde sa
  //: machine.
  const REGARD = 90;
  //: ⚠️ LE SIGNALEUR. Sa palette est un décor à deux poses (`panneau_signaleur`) et
  //: c'est la POSE qui décide : 0 = ARRÊT, 1 = LENTEMENT. Il voit venir le trafic de
  //: plus loin qu'un piéton : six tuiles. ⚠️ Et l'ARRÊT dure trois secondes, pas plus
  //: (`anime` 180 images) : la patience du trafic est de 200 images, au-delà il
  //: force le passage — un arrêt plus long qu'elle ne serait pas obéi.
  const PALETTE = 'panneau_signaleur';
  const POSE_ARRET = 0;
  const PORTEE_SIGNAL_TUILES = 6;

  const PAS_SIGNAL = { '<': -1, '>': 1 };

  let liste = [];                  // { def, posee, machines, tuiles:Set }
  let effacees = new Set();        // « x,y » des tuiles dont le bâtiment est tombé
  let attente = 0;
  //: Ce qui est parti, pour les juges : { son, t, x, y }. Les quarante derniers.
  const journal = [];

  function cle(x, y) { return x + ',' + y; }

  function tuilesDe(d) {
    const s = new Set();
    d.masque.forEach(function (rangee, j) {
      for (let i = 0; i < rangee.length; i++) if (rangee[i] === 'X') s.add(cle(d.x + i, d.y + j));
    });
    return s;
  }

  function debut() {
    const p = B.partie;
    return (p && p.chantiers && typeof p.chantiers.debut === 'number') ? p.chantiers.debut : 1;
  }

  /** La phase qu'un chantier doit montrer aujourd'hui — la même formule que
      `chantiers.phase_du_jour` en Python : un juge les compare. ⚠️ -1 : il n'a pas ouvert. */
  function phaseVoulue(d) {
    const jour = (B.partie && B.partie.jour) || 1;
    const ecoules = Math.max(0, jour - debut());
    const ouvre = d.ouvre || 0;
    if (ecoules < ouvre) return -1;
    return Math.min(d.phases.length - 1, d.decalage + Math.floor((ecoules - ouvre) / d.pas));
  }

  /** Ce que montre un chantier posé : sa phase, ou -1 s'il dort. (`posee` d'un dormant est 0 :
      la ville du générateur — c'est le sol de la phase 0 — mais sans rien peindre dessus.) */
  function etat(ch) { return ch.dort ? -1 : ch.posee; }

  // --- Poser une phase ---------------------------------------------------------------

  /** Écrit la phase dans la ville : tuiles, tableaux dérivés, portes des gens,
      lumières, machines, et le cache de morceaux autour. */
  function appliquer(ch, phase) {
    // ⚠️ -1 : le chantier dort. Le sol est celui de la phase 0 (celui du générateur), et plus
    // rien ne se pose — `peindre` saute un dormant, `equiper` ne trouve ni homme ni poste.
    ch.dort = phase < 0;
    phase = Math.max(0, phase);
    const carte = Monde.carte, d = ch.def, rangees = d.phases[phase].sol;
    for (let j = 0; j < d.h; j++) {
      const y = d.y + j, ligne = carte.sol[y];
      carte.sol[y] = ligne.slice(0, d.x) + rangees[j] + ligne.slice(d.x + d.l);
      for (let i = 0; i < d.l; i++) {
        // ⚠️ Les trois tableaux que `Monde.charger` tire du sol, et SEULEMENT
        // eux : c'est le même chemin qu'une clôture qu'on défonce.
        const p = carte.legende[rangees[j][i]] || {}, k = y * carte.w + d.x + i;
        carte.solide[k] = p.solide || 0;
        carte.route[k] = p.route ? 1 : 0;
        carte.passage[k] = (p.route && p.trottoir) ? 1 : 0;
      }
    }
    // ⚠️ Les portes par où les gens rentrent chez eux ne se RETIRENT pas de leur
    // liste : `Entites.porteQuiSert` relit la tuile, et une maison rasée n'avale
    // donc plus personne. Retirer ou réordonner la liste déplaçait tout ce qui y
    // tire au sort — la foule naissait ailleurs, à l'autre bout de la ville.
    // (Une porte ne se crée jamais : le neuf n'a qu'une porte peinte.)
    ch.posee = phase;
    effacer();
    // ⚠️ Les morceaux AUTOUR aussi : l'ombre d'un mur tombe une tuile au sud, et
    // une façade se lit dans ses voisines. Une rangée de marge sur chaque bord,
    // deux au sud.
    const m0x = Math.floor((d.x - 1) / 16), m1x = Math.floor((d.x + d.l) / 16);
    const m0y = Math.floor((d.y - 1) / 16), m1y = Math.floor((d.y + d.h + 1) / 16);
    for (let my = m0y; my <= m1y; my++) {
      for (let mx = m0x; mx <= m1x; mx++) carte.morceaux.delete(mx + ',' + my);
    }
    carte.mini = null;
    poserLaTranchee(ch, phase);
    poserLesMachines(ch, phase);
    retirerLEquipe(ch);
    degager(ch);
  }

  /** La tranchée du jour : les plaques d'acier claquent tant qu'elles sont posées,
      et le morceau de rue se recuit pour que la couche peinte suive. ⚠️ Elle ne
      change AUCUNE tuile : ce qu'un char sent vient de `carte.plaques`, ce qu'on
      voit de `peindre`. */
  function poserLaTranchee(ch, phase) {
    const carte = Monde.carte, d = ch.def;
    if (!carte.plaques) carte.plaques = new Set();
    const plaquee = d.phases[phase].tranchee === 'plaques';
    for (const t of d.tranchee || []) {
      if (plaquee) carte.plaques.add(cle(t[0], t[1])); else carte.plaques.delete(cle(t[0], t[1]));
      carte.morceaux.delete(Math.floor(t[0] / 16) + ',' + Math.floor(t[1] / 16));
    }
  }

  /** La phase change, l'équipe aussi : celle d'hier s'en va (le chantier est hors
      de vue, personne ne la voit partir) et `equiper` fait naître celle du jour. */
  function retirerLEquipe(ch) {
    for (const e of B.entites.slice()) if (e.equipeDe === ch.def.id) Entites.retirer(e);
    ch.equipe = [];
    ch.signaleur = null;
    lacherLaPalette(ch);
  }

  /** Les tuiles dont le bâtiment est tombé : ce qu'on y peignait (façade de
      logement, équipement de toit, tag) et les fenêtres qui s'y allumaient
      appartenaient à la maison, pas au chantier. */
  function effacer() {
    effacees = new Set();
    for (const ch of liste) {
      if (ch.posee >= 1) ch.tuiles.forEach(function (t) { effacees.add(t); });
    }
    for (const l of Monde.carte.lampes) {
      l.demolie = effacees.has(cle(Math.floor(l.x / TT), Math.floor(l.y / TT)));
    }
  }

  /** La fiche de décor d'une machine : la grue à boule qui frappe à l'OUEST est
      le miroir de l'autre (`sens`, dit par Python). */
  function decorDe(m) { return m.sens < 0 ? m.type + '_ouest' : m.type; }

  function poserLesMachines(ch, phase) {
    ch.machines.forEach(function (e) { Entites.retirer(e); });
    ch.machines = ch.def.phases[phase].machines.map(function (m) {
      const fiche = DECORS[decorDe(m)] || {};
      return Entites.creer('decor', m.x * TT + 8, m.y * TT + 15, {
        decor: decorDe(m), r: fiche.r === undefined ? 3 : fiche.r, solide: !!fiche.solide,
        // ⚠️ `machineDe`, PAS `chantier` : le chantier DU JOUR de M12 (la voie en
        // reparation) marque deja ses ouvriers `chantier`, et compte « qui
        // travaille » avec `q.chantier && q.vivant`. Une grue marquee pareil
        // passait pour un ouvrier, et l'equipe de la voie ne naissait plus.
        dessine: true, v: 0, machineDe: ch.def.id, frappe: m.frappe || null, sens: m.sens || 1,
      });
    });
    poserLaBenne(ch, phase);
    Entites.reindexerDecor();
  }

  /** La BENNE, tant qu'il y a des machines (phases 1 à 3) : posée chez elle, à la tuile que
      Python a choisie. ⚠️ À chaque phase elle est retirée et REPOSÉE — c'est ce qui la remet
      chez elle quand on l'a poussée, et ce qui l'ôte du chemin du neuf. Elle se pousse
      (`Entites.pousserDecor`) mais ne se tient pas dans `machines` : la pelle ne travaille pas
      avec elle, et la boucle du chantier n'a rien à lui demander. */
  function poserLaBenne(ch, phase) {
    if (ch.conteneur) Entites.retirer(ch.conteneur);
    ch.conteneur = null;
    const maison = ch.def.conteneur;
    if (!maison || !ch.def.phases[phase].machines.length) return;
    const fiche = DECORS.conteneur, x = maison[0] * TT + 8, y = maison[1] * TT + 15;
    ch.conteneur = Entites.creer('decor', x, y, {
      decor: 'conteneur', r: fiche.r, solide: true, dessine: true, v: 0, conteneurDe: ch.def.id, chez: { x: x, y: y },
    });
  }

  /** Ce qui traîne par terre dans l'empreinte (une arme lâchée, un paquet)
      ressort devant la porte du neuf : sinon il finit muré, et le jeu montre
      une arme qu'on ne ramassera jamais. */
  function degager(ch) {
    const d = ch.def, sol = Monde.carte.sol;
    const porte = d.phases[d.phases.length - 1].porte;
    const dehors = { x: porte[0] * TT + 8, y: (porte[1] + 1) * TT + 8 };
    for (const e of B.entites) {
      if (e.type === 'decor' || e.type === 'ambulant' || CORPS[e.type]) continue;
      const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
      if (!ch.tuiles.has(cle(tx, ty))) continue;
      if ((Monde.carte.legende[sol[ty][tx]] || {}).solide) { e.x = dehors.x; e.y = dehors.y; }
    }
  }

  // --- Quand poser -------------------------------------------------------------------

  function enVue(ch, voulue) {
    const cam = B.cam, d = ch.def;
    const dedans = function (x0, y0, x1, y1) { return x1 > cam.x && x0 < cam.x + VW && y1 > cam.y && y0 < cam.y + VH; };
    if (dedans(d.x * TT - MARGE_PX, d.y * TT - MARGE_NORD_PX, (d.x + d.l) * TT + MARGE_PX, (d.y + d.h) * TT + MARGE_PX)) return true;
    // ⚠️ LES MACHINES DÉBORDENT de l'empreinte : la flèche de la grue passe 48 px
    // à côté de sa tuile. Celles d'aujourd'hui et celles de demain — une grue
    // qui s'évapore ou qui surgit, c'est pareil à l'écran.
    for (const phase of [ch.posee, voulue]) {
      if (phase < 0) continue;
      for (const m of d.phases[phase].machines) {
        const f = DECORS[decorDe(m)];
        if (!f) continue;
        const x0 = m.x * TT + 8 - f.ancre[0], y0 = m.y * TT + 15 - f.ancre[1];
        if (dedans(x0 - 8, y0 - 8, x0 + f.w + 8, y0 + f.h + 8)) return true;
      }
    }
    // ⚠️ La tranchée est dans la rue, à cinq ou huit tuiles de la façade : des
    // plaques qui surgissent ou une rue refaite d'un coup se voient tout autant.
    // (Elle ne change qu'entre certaines phases : ailleurs, elle n'attend pas.)
    const change = (ch.posee < 0 ? null : d.phases[ch.posee].tranchee) !== d.phases[Math.max(0, voulue)].tranchee;
    if (change) {
      for (const t of d.tranchee || []) {
        if (dedans(t[0] * TT - 8, t[1] * TT - 8, (t[0] + 1) * TT + 8, (t[1] + 1) * TT + 8)) return true;
      }
    }
    return false;
  }

  function quelquUnDedans(ch) {
    for (const e of B.entites) {
      if (!CORPS[e.type] || e.vivant === false) continue;
      const r = e.r || 5;
      // ⚠️ Les quatre coins du corps, pas son centre : un char garé à cheval sur
      // la limite du terrain se ferait couper en deux par un mur neuf.
      for (const dx of [-r, r]) {
        for (const dy of [-r, r]) {
          if (ch.tuiles.has(cle(Math.floor((e.x + dx) / TT), Math.floor((e.y + dy) / TT)))) return true;
        }
      }
    }
    return false;
  }

  /** Au début d'une partie : TOUT se pose tout de suite. Personne n'a encore
      rien vu, et la ville doit être celle du jour avant la première image. */
  function demarrer() {
    const def = Monde.carte && Monde.carte.def;
    liste = ((def && def.chantiers) || []).map(function (d) {
      return { def: d, posee: -1, dort: false, machines: [], equipe: [], signaleur: null, panneau: null, conteneur: null, tuiles: tuilesDe(d) };
    });
    attente = 0;
    for (const ch of liste) appliquer(ch, phaseVoulue(ch.def));
    // Une sauvegarde prise sur un terrain rasé, rouverte quand le neuf est
    // debout : le joueur reparaîtrait dans le mur.
    const j = B.joueur;
    if (j) {
      for (const ch of liste) {
        const tx = Math.floor(j.x / TT), ty = Math.floor(j.y / TT);
        if (ch.tuiles.has(cle(tx, ty)) && Monde.solidite(tx, ty) === 1) {
          const porte = ch.def.phases[ch.def.phases.length - 1].porte;
          j.x = porte[0] * TT + 8; j.y = (porte[1] + 1) * TT + 8;
          Monde.centrerCamera(j.x, j.y);
        }
      }
    }
  }

  function maj() {
    if (!liste.length) return;
    piloter();
    travailler();
    regarder();
    if (B.interieur) return;
    if (--attente > 0) return;
    attente = CADENCE;
    for (const ch of liste) {
      const voulue = phaseVoulue(ch.def);
      if (voulue === etat(ch)) continue;
      if (enVue(ch, voulue) || quelquUnDedans(ch)) continue;
      appliquer(ch, voulue);
    }
    equiper();
  }

  // --- L'équipe -----------------------------------------------------------------------

  /** Qui de l'équipe est encore là : une passe sur les entités, une fois par
      cadence. (La distance les oublie, un coup de feu les fait détaler.) */
  function reperer() {
    const parId = {};
    for (const ch of liste) { ch.equipe = []; ch.signaleur = null; parId[ch.def.id] = ch; }
    for (const e of B.entites) {
      if (e.equipeDe === undefined || !e.vivant) continue;
      const ch = parId[e.equipeDe];
      if (!ch) continue;
      // L'homme de la palette est de l'équipe (il naît et rentre avec elle), mais il
      // n'est pas au terrain : `regarder` ne le tourne pas vers le joueur.
      if (e.posteDe === 'signal') ch.signaleur = e; else ch.equipe.push(e);
    }
  }

  /** La palette suit son homme : posée dans sa main quand il naît, retirée quand
      il rentre — jamais une palette qui dit ARRÊT toute seule sur un trottoir. */
  function tenirLaPalette(ch) {
    const e = ch.signaleur;
    if (!e || !e.vivant || B.entites.indexOf(e) < 0) { lacherLaPalette(ch); return; }
    if (ch.panneau && B.entites.indexOf(ch.panneau) >= 0) return;
    // Dans sa main droite, un pixel plus bas que lui : elle se dessine DEVANT lui.
    ch.panneau = Entites.creer('decor', e.x + 6, e.y + 1, {
      decor: PALETTE, r: 0, solide: false, dessine: true, v: 0, palette: ch.def.id,
    });
    Entites.reindexerDecor();
  }

  function lacherLaPalette(ch) {
    if (ch.panneau) Entites.retirer(ch.panneau);
    ch.panneau = null;
  }

  /** Le jour, chaque poste de la phase a son homme ; la nuit, ou sur un chantier
      sans équipe, ils rentrent — hors de l'écran seulement, personne ne les voit
      disparaître. */
  function equiper() {
    const jour = !Monde.estNuit();
    reperer();
    for (const ch of liste) {
      const phase = ch.posee < 0 ? null : ch.def.phases[ch.posee];
      const postes = phase ? (phase.equipe || []) : [];
      const s = ch.def.signaleur;
      // Il sert tant que les plaques sont posées : cela se lit dans la phase (`tranchee`).
      const signale = !!(jour && s && phase && phase.tranchee === 'plaques');
      if (jour && postes.length) {
        // Les nouveaux venus se comptent tout de suite : `regarder` les orienterait
        // sinon une cadence trop tard.
        if (Entites.naitreLEquipe(ch.def.id, postes)) reperer();
      } else {
        for (const e of ch.equipe) if (!Entites.visibleAEcran(e.x, e.y, 24)) Entites.retirer(e);
      }
      if (signale) {
        if (Entites.naitreLEquipe(ch.def.id, [s], 'signal')) reperer();
      } else if (ch.signaleur && !Entites.visibleAEcran(ch.signaleur.x, ch.signaleur.y, 24)) {
        Entites.retirer(ch.signaleur);
        ch.signaleur = null;
      }
      tenirLaPalette(ch);
    }
  }

  // --- La pelle qu'on conduit --------------------------------------------------------------------

  /** La pelle du chantier — le décor animé qui travaille — à portée de main, ou null. ⚠️ Comme toutes
      les fonctions « sous la main » : on la mesure au bord de sa boîte (`sol`), et il faut lui faire
      face (`faceA`) — le bouton ne promet que ce qu'il fera. Le décor brisé n'est plus une pelle. */
  function pelleSousLaMain(j) {
    if (!j || j.dansVehicule || B.interieur) return null;
    for (const ch of liste) {
      for (const m of ch.machines) {
        if (m.decor !== 'pelleteuse' || m.brise) continue;
        const sol = DECORS.pelleteuse.sol;
        const dx = Math.max(Math.abs(j.x - m.x) - sol[0], 0), dy = Math.max(Math.abs(j.y - m.y) - sol[1], 0);
        if (Math.hypot(dx, dy) <= 24 && faceA(j, m.x, m.y)) return { ch: ch, d: m };
      }
    }
    return null;
  }

  function inviteMonter(j) { return pelleSousLaMain(j) ? 'MONTER : PELLETEUSE' : null; }

  /** On monte : le décor est retiré du chantier (`machines`, pour que `travailler` ne fasse plus
      racler un godet qui n'est plus là) et un vrai char naît à sa place, que `Vehicules.monter` prend
      comme n'importe quel char garé — y compris le délit : les hommes du chantier regardent.
      ⚠️ Une couleur DONNÉE (`couleur`) : le tirage d'une couleur consommerait un dé du jeu. */
  function monterDansLaPelle(j, cible) {
    const d = cible.d;
    cible.ch.machines = cible.ch.machines.filter(function (m) { return m !== d; });
    Entites.retirer(d);
    Entites.reindexerDecor();
    const v = Vehicules.creer('pelleteuse', d.x + 4, d.y - 8, 0, {
      etat: 'stationne', couleur: Vehicules.vehiculeDef('pelleteuse').couleurs[0], pelleDe: cible.ch.def.id,
    });
    Entites.indexer();
    Vehicules.degager(v);
    Vehicules.monter(j, v);
    return true;
  }

  // --- La cabine de la grue ------------------------------------------------------------------

  //: Un tour complet en une seconde et demie : 16 poses (`DECORS.grue.variantes`), une tous les 5,6
  //: images à pleine vitesse. Le stick dose : à mi-course, la moitié.
  const GRUE_POSES_PAR_IMAGE = 0.18;

  /** La grue du chantier à portée de main, ou null : mêmes règles que la pelle. */
  function grueSousLaMain(j) {
    if (!j || j.dansVehicule || j.manege || B.interieur) return null;
    for (const ch of liste) {
      for (const m of ch.machines) {
        if (m.decor !== 'grue' || m.brise) continue;
        const sol = DECORS.grue.sol;
        const dx = Math.max(Math.abs(j.x - m.x) - sol[0], 0), dy = Math.max(Math.abs(j.y - m.y) - sol[1], 0);
        if (Math.hypot(dx, dy) <= 24 && faceA(j, m.x, m.y)) return { ch: ch, d: m };
      }
    }
    return null;
  }

  function inviteGrue(j) { return grueSousLaMain(j) ? 'MONTER : GRUE' : null; }

  /** On monte : `j.manege` (quoi: 'grue') — le joueur disparaît dans la cabine, immobile au pied du
      mât. La grue, elle, garde sa pose du moment (`poseManuelle`) au lieu de tourner toute seule. */
  function monterDansLaGrue(j, cible) {
    const d = cible.d, f = DECORS.grue;
    j.manege = { quoi: 'grue', d: d, monteT: B.t, z: 0 };
    j.dessine = false; j.vx = 0; j.vy = 0;
    j.x = d.x; j.y = d.y + 4;
    d.poseManuelle = Entites.poseDuDecor(f, B.t, false);
    Hud.message('LA FLÈCHE : GAUCHE, DROITE — ACTION POUR DESCENDRE', 240);
    return true;
  }

  /** On redescend, au pied du mât. `force` : ailleurs qu'à l'arrêt (mort, pièce, grue tombée). */
  function descendreDeLaGrue(j, force) {
    const m = j.manege;
    if (!m || m.quoi !== 'grue') return false;
    delete m.d.poseManuelle;                      // elle reprend SON travail, tout de suite
    j.manege = null;
    j.dessine = true; j.vx = 0; j.vy = 0;
    j.descenduT = B.t;
    if (!force) j.y += 14;
    Entites.dansLaCarte(j);
    return true;
  }

  /** À chaque image : la flèche suit le stick, ACTION descend. ⚠️ Et une grue dont plus personne ne tient
      les commandes (le joueur est mort, sorti, ou descendu par un autre chemin — `Foire.descendre` lâche
      `j.manege` sans nous le dire) reprend SON travail : `poseManuelle` ne survit pas à son pilote. */
  function piloter() {
    const j = B.joueur;
    const m = j && j.manege && j.manege.quoi === 'grue' ? j.manege : null;
    for (const ch of liste) {
      for (const e of ch.machines) if (e.poseManuelle !== undefined && (!m || m.d !== e)) delete e.poseManuelle;
    }
    if (!m) return;
    const d = m.d;
    if (!j.vivant || B.interieur || B.entites.indexOf(d) < 0 || d.brise) { descendreDeLaGrue(j, true); return; }
    j.x = d.x; j.y = d.y + 4; j.vx = 0; j.vy = 0;
    if (B.t !== m.monteT && Entree.neuf('action')) { descendreDeLaGrue(j, false); return; }
    const f = DECORS.grue;
    // La pose est un nombre à virgule tant qu'on tourne, et `poseDuDecor` en lit l'entier.
    m.cap = ((m.cap === undefined ? d.poseManuelle : m.cap) + Entree.axe.x * GRUE_POSES_PAR_IMAGE + f.variantes) % f.variantes;
    d.poseManuelle = Math.floor(m.cap);
  }

  /** ⚠️ CE QUE LE TRAFIC LIT : à quelle distance de son nez le signaleur dit-il
      ARRÊT ? Infinity si rien ne l'arrête. Lu par `Vehicules.obstacleDevant`, donc
      par la même conduite que pour un piéton planté sur la voie — et le même
      freinage.

      Il ne parle qu'à SA voie (la rangée de la tranchée, dans son sens), pas à ce
      qui est passé devant lui, pas au-delà de six tuiles, jamais à une rame ni à
      une poursuite (la police ne s'arrête pas pour un signaleur), et seulement quand
      sa palette dit ARRÊT — la même pose que celle qu'on voit. */
  function signalDevant(v) {
    if (v.rails || v.poursuite) return Infinity;
    for (const ch of liste) {
      const e = ch.signaleur, s = ch.def.signaleur;
      if (!e || !ch.panneau || !s) continue;
      if (Entites.poseDuDecor(DECORS[PALETTE], B.t, false) !== POSE_ARRET) continue;
      // Sa voie : la rangée de la tranchée, juste sous lui — et son sens se lit sur la
      // carte (`voie`), Python ne l'envoie pas.
      const sens = Monde.fleche(s[0], s[1] + 1);
      if (v.sens !== sens || Math.floor(v.y / TT) !== s[1] + 1 || !PAS_SIGNAL[sens]) continue;
      const devant = (e.x - v.x) * PAS_SIGNAL[sens];
      if (devant <= 0 || devant > PORTEE_SIGNAL_TUILES * TT + v.def.longueur / 2) continue;
      return devant - v.def.longueur / 2;
    }
    return Infinity;
  }

  /** Il regarde passer : à moins de `REGARD` px, le visage tourné vers le joueur,
      sinon vers sa machine. ⚠️ Chaque image, et sur les seuls hommes de la dernière
      passe (`reperer`) : deux ou trois entités par chantier, pas toute la ville. */
  function regarder() {
    const j = B.joueur;
    if (!j) return;
    for (const ch of liste) {
      // Le signaleur regarde la ROUTE : il est au nord de la voie, le trafic vient d'en bas.
      if (ch.signaleur && ch.signaleur.vivant && ch.signaleur.etat === 'fige') ch.signaleur.face = 'bas';
      const m = ch.machines[0];
      for (const e of ch.equipe) {
        if (!e.vivant || e.etat !== 'fige') continue;
        const versLui = Math.hypot(j.x - e.x, j.y - e.y) < REGARD || !m;
        const dx = (versLui ? j.x : m.x) - e.x, dy = (versLui ? j.y : m.y) - e.y;
        e.face = Math.abs(dx) >= Math.abs(dy) ? (dx > 0 ? 'droite' : 'gauche') : (dy > 0 ? 'bas' : 'haut');
      }
    }
  }

  // --- Le chantier travaille ---------------------------------------------------------

  function noter(son, x, y) {
    journal.push({ son: son, t: B.t, x: Math.round(x), y: Math.round(y) });
    if (journal.length > 40) journal.shift();
  }

  function jouer(son, x, y, portee) {
    noter(son, x, y);
    Son.SFX.chantier(son, x, y, portee || PORTEE_SON);
  }

  /** La distance du joueur au rectangle du chantier (0 dedans). */
  function distance(d, j) {
    const x0 = d.x * TT, x1 = (d.x + d.l) * TT, y0 = d.y * TT, y1 = (d.y + d.h) * TT;
    return Math.hypot(Math.max(x0 - j.x, 0, j.x - x1), Math.max(y0 - j.y, 0, j.y - y1));
  }

  /** Le coup de boule : le son, la poussière et les éclats au bord du mur, et
      la rue qui tremble si on est tout près. ⚠️ Pas de `B.rng` : un coup de
      boule tous les trois secondes décalerait tout ce que la ville tire au sort,
      et les juges qui en dépendent tomberaient au hasard d'une promenade. */
  function frapper(ch, e) {
    const x = e.x + CONTACT_X * e.sens, y = e.y - CONTACT_Y;
    jouer('boule', x, y, PORTEE_BOULE);
    const cam = B.cam;
    if (x > cam.x - 16 && x < cam.x + VW + 16 && y > cam.y - 16 && y < cam.y + VH + 16) {
      for (let k = 0; k < 18; k++) {
        // ⚠️ `>>>` et pas `>>` : `hash2` rend un entier SANS signe, et `>>` le
        // relit signé — la moitié des éclats partaient en colonne vers le ciel.
        const h = hash2(B.t + k * 31, ch.def.id * 977 + k);
        const brique = k % 3 === 0;
        // Tout part DU mur, vers la boule. Les briques retombent vite ; la
        // poussière, plus grosse, flotte une seconde et se pose — c'est elle
        // qu'on voit, un éclat de deux pixels ne dure qu'un battement de cils.
        // (Plus légère encore, elle monterait en colonne : on dirait un feu.)
        const vx = -e.sens * (0.2 + (h % 13) / 13) * (brique ? 1.6 : 0.7);
        const vy = ((h >>> 5) % 11 - 5) / (brique ? 12 : 20);
        Entites.particule(x - e.sens * 2, y + ((h >>> 9) % 13) - 6, vx, vy,
                          brique ? 22 + (h >>> 13) % 16 : 45 + (h >>> 13) % 30,
                          brique ? '#8c4a3c' : (k % 2 ? '#b9ae9a' : '#9a9080'), brique ? 2 : 3,
                          brique ? 0.22 : 0.06);
      }
    }
    const j = B.joueur;
    if (j) {
      const dj = Math.hypot(x - j.x, y - j.y);
      if (dj < 96) B.cam.secousse = Math.max(B.cam.secousse || 0, 0.3 * (1 - dj / 96));
    }
  }

  /** À chaque image : les gestes qu'on voit, les sons qu'on ne voit pas, la
      rumeur du plus proche. ⚠️ Et RIEN la nuit ni dans une pièce : les machines
      s'arrêtent à leur pose de repos (`Entites.poseDuDecor`), et le chantier se
      tait avec elles. */
  function travailler() {
    const j = B.joueur;
    if (B.interieur || !j || Monde.estNuit()) { Son.SFX.rumeur_chantier(0); return; }
    // ⚠️ `B.t + 1` : `maj` tourne AVANT que l'image avance, et c'est l'image
    // suivante qui se peint. Le coup part avec la pose qu'on voit.
    const t = B.t + 1;
    let rumeur = 0;
    for (const ch of liste) {
      const d = ch.def;
      if (ch.posee < 1 || ch.posee > 3) continue;
      const loin = distance(d, j);
      if (loin > PORTEE_BOULE) continue;
      rumeur = Math.max(rumeur, 1 - loin / PORTEE_RUMEUR);
      for (const e of ch.machines) {
        const f = DECORS[e.decor];
        if (!f || !f.anime || t % f.anime !== 0) continue;
        const pose = Entites.poseDuDecor(f, t, false);
        if (f.frappe !== undefined && e.frappe && pose === f.frappe) frapper(ch, e);
        if (f.racle !== undefined && pose === f.racle && t % (f.anime * f.variantes * GODET_TOURS) === 0) {
          jouer('godet', e.x + 18, e.y - 6);
        }
      }
      if (loin > PORTEE_SON) continue;
      const cx = (d.x + d.l / 2) * TT, cy = (d.y + d.h / 2) * TT;
      for (const [son, periode, decalage] of HORLOGES[ch.posee] || []) {
        if ((t + d.id * 97) % periode !== decalage) continue;
        // Le marteau n'est pas une machine : un coup sur quatre ne vient pas.
        if (son === 'marteau' && hash2(Math.floor(t / periode), d.id) % 4 === 0) continue;
        jouer(son, cx, cy);
      }
    }
    Son.SFX.rumeur_chantier(rumeur);
  }

  // --- La couche peinte --------------------------------------------------------------

  function efface(x, y) { return effacees.has(cle(x, y)); }

  //: ⚠️ LA OU LA FACADE PEINT SES FENETRES. Une maison de la ville ne montre pas
  //: ses fenetres par ses tuiles (`W`) mais par sa facade de logement
  //: (`FACADES.residence`, rez-de-chaussee a 11 px du haut du mur). Clouer les
  //: planches au milieu de la tuile, c'etait les clouer sur la brique a cote
  //: d'une fenetre restee intacte — la capture le montrait.
  const FENETRE_Y = 11, FENETRE_H = 5;

  function planche(ctx, x, y) {
    ctx.fillStyle = '#2b2734';
    ctx.fillRect(x + 3, y + FENETRE_Y + 1, 10, FENETRE_H - 1);
    ctx.fillStyle = '#8a6a3f';
    ctx.fillRect(x + 2, y + FENETRE_Y + 1, 12, 1);
    ctx.fillRect(x + 2, y + FENETRE_Y + 3, 12, 1);
    ctx.fillStyle = '#a07c4b';
    for (let k = 0; k < 10; k++) ctx.fillRect(x + 3 + k, y + FENETRE_Y + 1 + Math.floor(k * 0.4), 1, 1);
  }

  /** Un panneau de chantier : jaune, bordé de noir, le mot en noir. ⚠️ Il pend
      AU MUR, sur la rangée de façade : c'est là que le regard va chercher un
      nom depuis que les devantures existent. */
  function panneau(ctx, texte, cx, y) {
    const larg = Atlas.largeurTexte(texte, 1) + 6;
    const x = Math.round(cx - larg / 2);
    // ⚠️ 12 de haut, pas 9 : l'accent de « À DÉMOLIR » se dessine trois rangs
    // au-dessus de la lettre, et tombait dans le liseré noir. Le panneau
    // grandit VERS LE HAUT : son bas et son mot restent où ils pendaient.
    const haut = y - 3;
    ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(x + 1, haut + 1, larg, 12);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(x, haut, larg, 12);
    ctx.fillStyle = '#1a1712'; ctx.fillRect(x, haut, larg, 1); ctx.fillRect(x, haut + 11, larg, 1);
    Atlas.texte(ctx, texte, x + 3, y + 2, '#1a1712', 1);
  }

  /** Deux plaques d'acier boulonnées sur la coupe : l'asphalte ouvert autour, la
      couture entre les plaques, l'éclat du haut, l'ombre du bas, les rivets. `n`
      tuiles de large, en (x, y) du morceau. */
  function plaques(ctx, x, y, n) {
    const w = n * TT;
    ctx.fillStyle = '#17181c'; ctx.fillRect(x, y + 1, w, 14);
    ctx.fillStyle = '#7e858d'; ctx.fillRect(x + 1, y + 2, w - 2, 12);
    ctx.fillStyle = '#a3abb3'; ctx.fillRect(x + 1, y + 2, w - 2, 1);
    ctx.fillStyle = '#4b5158'; ctx.fillRect(x + 1, y + 13, w - 2, 1);
    for (let i = 0; i < n; i++) {
      const px = x + i * TT;
      if (i) { ctx.fillStyle = '#5b626a'; ctx.fillRect(px - 1, y + 2, 2, 12); }
      ctx.fillStyle = '#c3c9cf';
      for (const [rx, ry] of [[3, 4], [12, 4], [3, 11], [12, 11]]) ctx.fillRect(px + rx, y + ry, 1, 1);
    }
    // Le ruban de danger, aux deux bouts de la coupe : jaune et noir.
    for (const bout of [x, x + w - 2]) {
      for (let k = 0; k < 6; k++) {
        ctx.fillStyle = k % 2 ? '#1a1712' : '#e8b33c';
        ctx.fillRect(bout, y + 2 + k * 2, 2, 2);
      }
    }
  }

  /** L'asphalte refait : un carré plus noir que la rue autour, ses joints scellés
      et deux ou trois cailloux. Ça ne sert à rien du tout, et c'est ce qui rend
      le reste crédible. */
  function rapiece(ctx, x, y, n) {
    const w = n * TT;
    ctx.fillStyle = '#25262c'; ctx.fillRect(x, y + 1, w, 14);
    ctx.fillStyle = '#191a1f';
    ctx.fillRect(x, y + 1, w, 1); ctx.fillRect(x, y + 14, w, 1);
    ctx.fillRect(x, y + 1, 1, 14); ctx.fillRect(x + w - 1, y + 1, 1, 14);
    ctx.fillStyle = '#31333a';
    for (let k = 0; k < n * 5; k++) {
      const h = hash2(x + k * 13, y + k * 7);
      ctx.fillRect(x + 2 + h % (w - 4), y + 3 + (h >>> 8) % 10, 1, 1);
    }
  }

  /** La tranchée du chantier, sur CHAQUE morceau qu'elle touche : la toile coupe
      ce qui dépasse. Elle est dans la rue, loin de l'empreinte du bâtiment — d'où
      son propre test, avant celui de la façade. */
  function tranchee(ctx, ch, ox, oy) {
    const d = ch.def, t = d.tranchee;
    if (!t || !t.length || ch.posee < 0) return;
    const sorte = d.phases[ch.posee].tranchee;
    if (!sorte) return;
    const x = t[0][0] - ox, y = t[0][1] - oy;
    if (x + t.length < 0 || x > 16 || y < 0 || y >= 16) return;
    (sorte === 'plaques' ? plaques : rapiece)(ctx, x * TT, y * TT, t.length);
  }

  /** Ce que le chantier ajoute au morceau, selon sa phase posée. */
  function peindre(ctx, mx, my) {
    const ox = mx * 16, oy = my * 16;
    for (const ch of liste) {
      const d = ch.def;
      if (ch.dort) continue;                      // rien n'a commencé : la maison est celle de tous les jours
      tranchee(ctx, ch, ox, oy);
      if (d.x + d.l < ox - 1 || d.x > ox + 16 || d.y + d.h + 2 < oy - 1 || d.y - 1 > oy + 16) continue;
      const px = (d.x - ox) * TT, py = (d.y - oy) * TT;
      const phase = ch.posee, sol = d.phases[phase].sol;
      // La rangée de façade qui donne sur la rue : la dernière du rectangle.
      const bas = d.h - 1;
      if (phase === 0) {
        // Toutes les fenetres du rez-de-chaussee qui donnent sur la rue — les
        // portes, elles, restent des portes (condamnees, mais des portes).
        for (let i = 0; i < d.l; i++) {
          const g = sol[bas][i];
          if (d.masque[bas][i] !== 'X' || g === 'd' || g === 'D' || g === 'G') continue;
          if (Monde.solidite(d.x + i, d.y + bas + 1) !== 0) continue;
          planche(ctx, px + i * TT, py + bas * TT);
          // Une tuile VITRINE porte sa propre fenetre, plus haut dans le mur.
          if (g === 'W') {
            const x = px + i * TT, y = py + bas * TT;
            ctx.fillStyle = '#2b2734'; ctx.fillRect(x + 3, y + 3, 10, 9);
            ctx.fillStyle = '#8a6a3f'; ctx.fillRect(x + 2, y + 4, 12, 2); ctx.fillRect(x + 2, y + 8, 12, 2);
          }
        }
        panneau(ctx, d.phases[0].panneau, px + d.l * TT / 2, py + bas * TT + 3);
      } else if (phase === 1 || phase === 2) {
        // ⚠️ Le mur que la boule frappe porte ses coups : un trou dans la brique
        // et des fissures qui en partent, sur la tuile du contact et celle du
        // dessus. Peint une fois, dans le morceau.
        const boule = phase === 1 && d.phases[1].machines.find(function (m) { return m.frappe; });
        if (boule) {
          const s = boule.sens, mx = boule.frappe[0], my = boule.frappe[1];
          for (const [ty, haut] of [[my, 0], [my - 1, 1]]) {
            const x = (mx - ox) * TT + (s > 0 ? 0 : TT - 6), y = (ty - oy) * TT;
            ctx.fillStyle = '#2b2734';
            ctx.fillRect(x + (s > 0 ? 0 : 2), y + 5 + haut * 3, 4, 5 - haut * 2);
            ctx.fillStyle = '#1a1712';
            const bord = s > 0 ? x + 4 : x + 1;
            ctx.fillRect(bord, y + 3 + haut, 1, 3); ctx.fillRect(bord + s, y + 2 + haut, 1, 2);
            ctx.fillRect(bord, y + 10, 1, 3); ctx.fillRect(bord + s, y + 12, 1, 2);
          }
        }
        // Des briques et des éclats de béton : de la friche où il y avait une
        // maison hier ne se confond pas avec un terrain vague.
        for (let j = 0; j < d.h; j++) {
          for (let i = 0; i < d.l; i++) {
            if (d.masque[j][i] !== 'X' || sol[j][i] !== ';') continue;
            const h = hash2(d.x + i, d.y + j);
            ctx.fillStyle = h % 3 ? '#8c4a3c' : '#9a9689';
            ctx.fillRect(px + i * TT + (h % 11) + 1, py + j * TT + ((h >>> 4) % 11) + 2, 3, 2);
            ctx.fillStyle = '#6e3a30';
            ctx.fillRect(px + i * TT + ((h >>> 8) % 9) + 4, py + j * TT + ((h >>> 12) % 9) + 5, 2, 2);
          }
        }
      } else if (phase === 3) {
        // L'échafaudage : des montants et deux planchers le long de la rue.
        for (let i = 0; i < d.l; i++) {
          if (d.masque[bas][i] !== 'X') continue;
          const x = px + i * TT, y = py + bas * TT;
          ctx.fillStyle = '#7a7d82';
          ctx.fillRect(x + 1, y, 1, 16); ctx.fillRect(x + 14, y, 1, 16);
          ctx.fillStyle = '#b8863a';
          ctx.fillRect(x, y + 4, 16, 2); ctx.fillRect(x, y + 11, 16, 2);
        }
      } else if (phase === d.phases.length - 1) {
        const porte = d.phases[phase].porte;
        const x = (porte[0] - ox) * TT, y = (porte[1] - oy) * TT;
        // Une porte peinte, fermée : le neuf n'a pas encore d'intérieur, alors
        // pas de poignée dorée — elle ne promet pas qu'on entre.
        ctx.fillStyle = '#3a3a44'; ctx.fillRect(x + 3, y + 5, 10, 11);
        ctx.fillStyle = '#2b2734'; ctx.fillRect(x + 4, y + 6, 8, 10);
        ctx.fillStyle = 'rgba(255,255,255,0.10)'; ctx.fillRect(x + 5, y + 7, 2, 7);
        panneau(ctx, d.phases[phase].panneau, px + d.l * TT / 2, py + bas * TT - 6);
      }
    }
  }

  return {
    CADENCE, PORTEE_SON, PORTEE_BOULE, CONTACT_X, CONTACT_Y, REGARD, demarrer, maj, efface, peindre, phaseVoulue, etat, travailler, equiper, signalDevant, pelleSousLaMain, inviteMonter, monterDansLaPelle, grueSousLaMain, inviteGrue, monterDansLaGrue, descendreDeLaGrue, PORTEE_SIGNAL_TUILES,
    get liste() { return liste; },
    get journal() { return journal; },
    // Pour les juges : poser une phase comme le ferait la journée.
    appliquer: function (i, phase) { appliquer(liste[i], phase); },
  };
})();
