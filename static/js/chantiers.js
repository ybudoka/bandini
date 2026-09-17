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
   l'entend avant de le voir, et il se tait la nuit (`travailler`). */

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
      `chantiers.phase_du_jour` en Python : un juge les compare. */
  function phaseVoulue(d) {
    const jour = (B.partie && B.partie.jour) || 1;
    const ecoules = Math.max(0, jour - debut());
    return Math.min(d.phases.length - 1, d.decalage + Math.floor(ecoules / d.pas));
  }

  // --- Poser une phase ---------------------------------------------------------------

  /** Écrit la phase dans la ville : tuiles, tableaux dérivés, portes des gens,
      lumières, machines, et le cache de morceaux autour. */
  function appliquer(ch, phase) {
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
    poserLesMachines(ch, phase);
    degager(ch);
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
    Entites.reindexerDecor();
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
      return { def: d, posee: -1, machines: [], tuiles: tuilesDe(d) };
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
    travailler();
    if (B.interieur) return;
    if (--attente > 0) return;
    attente = CADENCE;
    for (const ch of liste) {
      const voulue = phaseVoulue(ch.def);
      if (voulue === ch.posee) continue;
      if (enVue(ch, voulue) || quelquUnDedans(ch)) continue;
      appliquer(ch, voulue);
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
    ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(x + 1, y + 1, larg, 9);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(x, y, larg, 9);
    ctx.fillStyle = '#1a1712'; ctx.fillRect(x, y, larg, 1); ctx.fillRect(x, y + 8, larg, 1);
    Atlas.texte(ctx, texte, x + 3, y + 2, '#1a1712', 1);
  }

  /** Ce que le chantier ajoute au morceau, selon sa phase posée. */
  function peindre(ctx, mx, my) {
    const ox = mx * 16, oy = my * 16;
    for (const ch of liste) {
      const d = ch.def;
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
    CADENCE, PORTEE_SON, PORTEE_BOULE, CONTACT_X, CONTACT_Y, demarrer, maj, efface, peindre, phaseVoulue, travailler,
    get liste() { return liste; },
    get journal() { return journal; },
    // Pour les juges : poser une phase comme le ferait la journée.
    appliquer: function (i, phase) { appliquer(liste[i], phase); },
  };
})();
