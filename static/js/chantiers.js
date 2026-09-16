/* Bandini — ça travaille : les chantiers, joués jour après jour.

   ⚠️ Python décide (`app/chantiers.py`) : quels bâtiments, les tuiles de chacune
   des cinq phases, où travaillent les machines — et toute la géométrie s'y juge
   phase par phase. Ce script ne fait que POSER la phase du jour.

   ⚠️ Et il ne la pose JAMAIS sous les yeux du joueur. Une phase qui avance change
   des tuiles, recuit des morceaux et remplace des machines : vu en direct, c'est
   un bâtiment qui s'évapore d'une image à l'autre. On attend donc que le chantier
   soit hors de l'écran — et que personne ne se tienne dans son empreinte, parce
   que le neuf remonte des murs exactement là où l'on marchait la veille. */

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

  let liste = [];                  // { def, posee, machines, tuiles:Set }
  let effacees = new Set();        // « x,y » des tuiles dont le bâtiment est tombé
  let attente = 0;

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

  function poserLesMachines(ch, phase) {
    ch.machines.forEach(function (e) { Entites.retirer(e); });
    ch.machines = ch.def.phases[phase].machines.map(function (m) {
      const fiche = DECORS[m.type] || {};
      return Entites.creer('decor', m.x * TT + 8, m.y * TT + 15, {
        decor: m.type, r: fiche.r === undefined ? 3 : fiche.r, solide: !!fiche.solide,
        // ⚠️ `machineDe`, PAS `chantier` : le chantier DU JOUR de M12 (la voie en
        // reparation) marque deja ses ouvriers `chantier`, et compte « qui
        // travaille » avec `q.chantier && q.vivant`. Une grue marquee pareil
        // passait pour un ouvrier, et l'equipe de la voie ne naissait plus.
        dessine: true, v: 0, machineDe: ch.def.id,
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

  function enVue(d) {
    const cam = B.cam;
    const x0 = d.x * TT - MARGE_PX, x1 = (d.x + d.l) * TT + MARGE_PX;
    const y0 = d.y * TT - MARGE_NORD_PX, y1 = (d.y + d.h) * TT + MARGE_PX;
    return x1 > cam.x && x0 < cam.x + VW && y1 > cam.y && y0 < cam.y + VH;
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
    if (B.interieur || !liste.length) return;
    if (--attente > 0) return;
    attente = CADENCE;
    for (const ch of liste) {
      const voulue = phaseVoulue(ch.def);
      if (voulue === ch.posee) continue;
      if (enVue(ch.def) || quelquUnDedans(ch)) continue;
      appliquer(ch, voulue);
    }
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
        // Des briques et des éclats de béton : de la friche où il y avait une
        // maison hier ne se confond pas avec un terrain vague.
        for (let j = 0; j < d.h; j++) {
          for (let i = 0; i < d.l; i++) {
            if (d.masque[j][i] !== 'X' || sol[j][i] !== ';') continue;
            const h = hash2(d.x + i, d.y + j);
            ctx.fillStyle = h % 3 ? '#8c4a3c' : '#9a9689';
            ctx.fillRect(px + i * TT + (h % 11) + 1, py + j * TT + ((h >> 4) % 11) + 2, 3, 2);
            ctx.fillStyle = '#6e3a30';
            ctx.fillRect(px + i * TT + ((h >> 8) % 9) + 4, py + j * TT + ((h >> 12) % 9) + 5, 2, 2);
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
    CADENCE, demarrer, maj, efface, peindre, phaseVoulue,
    get liste() { return liste; },
    // Pour les juges : poser une phase comme le ferait la journée.
    appliquer: function (i, phase) { appliquer(liste[i], phase); },
  };
})();
