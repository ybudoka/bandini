/* Bandini — le tripot du sous-sol du Dragon d'or : la BARBOTTE du Pouce (docs/jalons/le-casino-du-petit-canton.md,
   vague 4). Les regles sont a Python (`app/tripot.py`, `B.defs.tables_de_jeu.tripot`) ; ici, on joue le coup.
   Chaque fonction qui decide d'un gain a son JUMEAU en Python, et un juge les compare tirage pour tirage
   (`test_tripot_js.py`).

   La barbotte : deux des, quatre coups POUR (3-3, 5-5, 6-6, 5-6), quatre CONTRE (1-1, 2-2, 4-4, 1-2), le reste
   se relance ; le Pouce prend sa piastre, cinq pour cent de chaque gain. Honnete, elle rend 97,5 %.

   ⚠️ LA MAISON TRICHE, ET CA SE VOIT : a partir de 500 $, le Pouce glisse souvent ses DES PIPES sur le feutre,
   contre le cote que tu as pris — plus JAUNES que les vrais (de la vieille ivoire). Une fois ses des poses
   (MISER), on peut LANCER quand meme, CHANGER DE COTE (ses pipes jouent pour toi), ou DENONCER LES DES (justes :
   il te rend ta mise et te laisse tranquille jusqu'a demain ; faux : les gros bras te sortent). Il se MEFIE
   (`mefiance`, cinq crans en bas du menu) : a cent, les gros bras te raccompagnent par la porte d'en arriere, et
   l'escalier te reste ferme une semaine. Pas une etoile : dans un tripot, on n'appelle pas la police.

   ⚠️ LE HASARD EST A LA TABLE : un coup se tire d'un generateur seme par la graine de la partie, le numero du
   coup et le SEL du tripot — jamais `B.rng()`. Un coup joue ne decale pas un de du reste du jeu.

   ⚠️ LA PREUVE ET LA REPRISE (l'arc d'Irene, c02 a c04) se lisent dans les regles, jamais dans un nom de mission :
   pendant un objectif `obtenir` dont la `table` est le tripot (`preuve`), on peut GLISSER TES DES — ses pipes
   dans ta manche, une paire honnete sur le feutre ; et quand la mission de `reprise` est faite, le tripot a
   change de mains : plus de Pouce, plus de gros bras, jamais de pipes, et le vieux Chan tient la table.

   ⚠️ LE GAIN EST PAYE TOUT DE SUITE, EN SILENCE, et ANNONCE quand les des s'arretent (la regle des tables : payer
   a la fin de l'animation, c'etait ne jamais payer qui ferme le menu pendant que les des roulent). Les animations
   se comptent en IMAGES DESSINEES : un menu ouvert fige `B.t`. */

const Tripot = (function () {
  'use strict';

  function regles() { return B.defs.tables_de_jeu.tripot; }

  //: Le slug de la piece du sous-sol, et le sel de son hasard (ni celui des tables, ni celui du videopoker).
  const SALLE = 'nord_tripot', SEL = 0x3C6EF372;
  //: Combien d'images durent la main du Pouce qui pose les des, et chaque lancer (relances comprises).
  const ANIME = { main: 26, lancer: 11 };
  //: L'ivoire des des : les vrais sont blancs, les pipes JAUNES — c'est tout ce qui les trahit.
  const IVOIRE = { vrai: '#efe6d0', pipe: '#e4c86a' };

  // --- Les regles : les jumeaux de `tripot.py` ------------------------------------------------------------

  /** La face d'un de d'un tirage `u` dans [0, 1) : honnete (`poids` nul), ou pipe. */
  function face(u, poids) {
    if (!poids) return 1 + Math.floor(u * 6);
    let total = 0;
    for (const p of poids) total += p;
    const k = u * total;
    let cumul = 0;
    for (let i = 0; i < poids.length; i++) { cumul += poids[i]; if (k < cumul) return i + 1; }
    return poids.length;
  }

  function dans(liste, a, b) {
    const lo = Math.min(a, b), hi = Math.max(a, b);
    return liste.some(function (p) { return p[0] === lo && p[1] === hi; });
  }
  /** Ce que deux des disent : 'pour', 'contre', ou null (on relance). */
  function coup(a, b) {
    const r = regles();
    if (dans(r.pour, a, b)) return 'pour';
    if (dans(r.contre, a, b)) return 'contre';
    return null;
  }

  /** Lance jusqu'au coup qui decide, deux tirages par lancer : { cote (null : main nulle), paires }. */
  function jet(tirages, poids) {
    const paires = [];
    for (let k = 0; k < regles().relances; k++) {
      const a = face(tirages[2 * k], poids), b = face(tirages[2 * k + 1], poids);
      paires.push([a, b]);
      const c = coup(a, b);
      if (c) return { cote: c, paires: paires };
    }
    return { cote: null, paires: paires };
  }

  function pipe(mise, u) { const p = regles().pipes; return mise >= p.seuil && u < p.chance; }
  function poidsContre(pari) { return pari === 'pour' ? regles().pipes.contre : regles().pipes.pour; }
  function gain(pari, cote, mise) {
    if (cote === null) return mise;
    return pari === cote ? mise + Math.round(mise * (1 - regles().piastre)) : 0;
  }
  function mefianceApres(m, evenement) { return Math.min(150, m + regles().mefiance[evenement]); }

  // --- Ce que la partie garde ---------------------------------------------------------------------------

  /** La mise et le pari choisis, les coups du jour, la mefiance du Pouce et le jour ou il te rouvre (`barre`),
      le jour ou il te laisse tranquille (`tranquille`, apres une denonciation juste). La mefiance fond de
      `oubli` par jour. */
  function etat() {
    const p = B.partie, r = regles();
    const e = p.tripot = p.tripot || { mise: r.mises[0], pari: 'pour', jour: p.jour || 0, coups: 0, total: 0,
                                       mefiance: 0, vu: p.jour || 0, barre: 0, tranquille: -1, sorties: 0 };
    const jour = p.jour || 0;
    if (jour > e.vu) { e.mefiance = Math.max(0, e.mefiance - r.mefiance.oubli * (jour - e.vu)); e.vu = jour; }
    if (e.jour !== jour) { e.jour = jour; e.coups = 0; }
    return e;
  }

  // --- La preuve (c02) et la reprise (c04) : ce que les regles en disent (`preuve`, `reprise`) ------------

  /** L'objectif en cours qui veut la preuve a cette table (`obtenir`, `table: 'tripot'`, l'objet de `preuve`). */
  function objectifDeLaTable() {
    const pr = regles().preuve, m = B.partie && B.partie.mission;
    const o = m && typeof Histoire !== 'undefined' ? Histoire.objectif() : null;
    return pr && o && o.type === 'obtenir' && o.table === 'tripot' && o.objet === pr.objet ? o : null;
  }
  function aLaPreuve() { const pr = regles().preuve; return !!(pr && B.partie.objets && B.partie.objets[pr.objet] > 0); }
  /** Irene t'envoie chercher ses des : l'escalier et la table ne te refusent pas, quoi que le Pouce en pense. */
  function enMission() { return !!objectifDeLaTable() && !aLaPreuve(); }
  /** LE TRIPOT A CHANGE DE MAINS : la mission de `reprise` est faite (c04). */
  function repris() {
    const r = regles().reprise, p = B.partie;
    return !!(r && p && p.missionsFaites && p.missionsFaites[r.apres]);
  }

  function barre() { if (repris() || enMission()) return false; return etat().barre > (B.partie.jour || 0); }
  function joursBarre() { return Math.max(0, etat().barre - (B.partie.jour || 0)); }
  function dansLaSalle() { return !!(B.interieur && B.interieur.slug === SALLE); }

  /** Le coup en cours (`B.tripot`) : `phase` (joue, fin), `n`, `pipes`, `poids`, `pari`, `mise`, `images`. */
  function enCours() { return B.tripot || null; }

  function hasard(n) { return mulberry(((B.graine | 0) ^ Math.imul(n + 1, SEL)) >>> 0); }

  /** Le coup numero `n` : le premier tirage dit si le Pouce pipe, les suivants font les lancers. */
  function tirages(n) {
    const rng = hasard(n), u = rng(), liste = [];
    for (let k = 0; k < 2 * regles().relances; k++) liste.push(rng());
    return { u: u, liste: liste };
  }

  // --- Jouer un coup ------------------------------------------------------------------------------------

  /** MISER : la mise part, et le Pouce pose ses des — les vrais, ou ses pipes. Rend false si on refuse. */
  function miser() {
    const r = regles(), e = etat(), p = B.partie;
    if (barre()) { Hud.message('LE POUCE NE TE SERT PLUS'); Son.SFX.erreur(); return false; }
    // ⚠️ La sortie a la mise suivante, jamais au milieu d'un coup : on a vu le resultat du dernier.
    if (!repris() && e.mefiance >= r.mefiance.sortir) { sortir(r.mefiance.barre_jours, 'LES GROS BRAS TE RACCOMPAGNENT · LE POUCE NE VEUT PLUS TE VOIR D’UNE SEMAINE'); return false; }
    if (e.coups >= r.par_jour && !triche('machines') && !enMission()) { Hud.message('LE POUCE FERME SA TABLE POUR TOI AUJOURD’HUI'); Son.SFX.erreur(); return false; }
    if (p.argent < e.mise) { Hud.message('PAS ASSEZ D’ARGENT'); Son.SFX.erreur(); return false; }
    if (!Missions.payer(e.mise, 'LA BARBOTTE')) return false;
    Son.SFX.jetons();
    e.coups++;
    const n = e.total++, t = tirages(n);
    // ⚠️ Repris, le tripot ne pipe plus jamais : c'est tout ce qu'Irene a change a la table.
    const pipes = !repris() && e.tranquille !== (p.jour || 0) && pipe(e.mise, t.u);
    B.tripot = { phase: 'joue', n: n, pipes: pipes, poids: pipes ? poidsContre(e.pari) : null, pari: e.pari,
                 depart: e.pari, mise: e.mise, tirages: t.liste, images: 0, fin: 0, retourne: false, glisse: false };
    return true;
  }

  /** LANCER : les des roulent jusqu'au coup qui decide. Paye tout de suite, annonce a l'arret. */
  function lancer() {
    const t = enCours(), e = etat();
    if (!t || t.phase !== 'joue') return false;
    const j = jet(t.tirages, t.poids), g = gain(t.pari, j.cote, t.mise);
    t.phase = 'fin'; t.fin = t.images; t.paires = j.paires; t.cote = j.cote;
    Son.SFX.des_barbotte();
    if (g > 0) Missions.encaisser(g, null, true);
    // Il a vu le manege : gagner avec SES des, apres avoir change de cote.
    if (t.pipes && t.retourne && g > t.mise) e.mefiance = mefianceApres(e.mefiance, 'gagne');
    const nom = j.cote === null ? 'MAIN NULLE' : (j.cote === 'pour' ? 'POUR' : 'CONTRE') + ' · '
      + j.paires[j.paires.length - 1].join('-') + (j.paires.length > 1 ? ' · ' + (j.paires.length - 1) + ' RELANCE' + (j.paires.length > 2 ? 'S' : '') : '');
    t.resultat = { nom: nom, gain: g, mise: t.mise };
    t.annonce = false;
    return true;
  }

  /** CHANGER DE COTE, une fois ses des poses. Sur des pipes, il le voit — une fois par coup. */
  function changer() {
    const t = enCours(), e = etat();
    if (!t || t.phase !== 'joue') return false;
    t.pari = t.pari === 'pour' ? 'contre' : 'pour';
    if (t.pipes && !t.retourne) { t.retourne = true; e.mefiance = mefianceApres(e.mefiance, 'retourner'); }
    Son.SFX.jetons();
    return true;
  }

  /** GLISSER TES DES (c02, `preuve`) : ses pipes dans ta manche, une paire honnete sur le feutre. Il ne voit rien
      — c'est son propre truc. Le coup se joue avec des des honnetes, et la preuve est dans le sac (l'objectif
      `obtenir` avance a la sortie, comme tout objectif : dans une piece, `majObjectif` dort). */
  function glisser() {
    const t = enCours(), o = objectifDeLaTable(), pr = regles().preuve;
    if (!t || t.phase !== 'joue' || !t.pipes || t.glisse || !o || aLaPreuve()) return false;
    t.glisse = true; t.pipes = false; t.poids = null;
    if (!B.partie.objets) B.partie.objets = {};
    B.partie.objets[pr.objet] = 1;
    Son.SFX.jetons();
    Hud.message(o.nom || pr.nom, 200);
    const pouce = lePouce();
    if (pouce) Entites.bulle(pouce, 'TIENS. ILS SONT BEN BLANCS, À SOIR.', { duree: 240 });
    return true;
  }

  /** DENONCER LES DES. Justes : la mise rendue, et la paix jusqu'a demain — il s'en souviendra. Faux : dehors. */
  function denoncer() {
    const t = enCours(), e = etat(), r = regles(), p = B.partie;
    if (!t || t.phase !== 'joue') return false;
    t.phase = 'fin'; t.fin = t.images; t.paires = []; t.cote = null; t.denonce = true;
    const pouce = lePouce();
    if (t.pipes) {
      Missions.encaisser(t.mise, null, true);
      e.mefiance = mefianceApres(e.mefiance, 'denoncer');
      e.tranquille = p.jour || 0;
      t.resultat = { nom: 'LES DÉS SONT PIPÉS · LE POUCE TE REND TA MISE', gain: t.mise, mise: t.mise };
      if (pouce) Entites.bulle(pouce, 'ÇA S’EST GLISSÉ TOUT SEUL, MON AMI.', { duree: 240 });
      t.annonce = false;
      return true;
    }
    t.resultat = { nom: 'DES DÉS HONNÊTES', gain: 0, mise: t.mise };
    t.annonce = true;
    if (pouce) Entites.bulle(pouce, 'ICI, ON ACCUSE PAS POUR RIEN.', { duree: 240 });
    sortir(r.mefiance.faux_jours, 'LES GROS BRAS TE SORTENT · ON ACCUSE PAS LE POUCE POUR RIEN · REVIENS DEMAIN');
    return true;
  }

  /** LA SORTIE : les gros bras te raccompagnent par la porte d'en arriere, et l'escalier te reste ferme `jours`.
      ⚠️ Pas une etoile : dans un tripot, on n'appelle pas la police. */
  function sortir(jours, message) {
    const e = etat(), p = B.partie;
    e.sorties++;
    e.barre = Math.max(e.barre, (p.jour || 0) + jours);
    e.mefiance = 0;
    Son.SFX.erreur();
    if (B.menu) Hud.fermerMenu();
    const gb = B.entites.find(function (q) { return q.grosBras && q.vivant; });
    if (gb) Entites.bulle(gb, 'DEHORS, MON CHAMPION.', { duree: 200 });
    Hud.message(message, 300);
    if (dansLaSalle()) Jeu.sortir();
  }

  /** Quand les des s'arretent : le gain qui sonne, ou ce que la table garde. */
  function annoncer(t) {
    if (t.annonce || !t.resultat) return;
    t.annonce = true;
    const r = t.resultat;
    if (r.gain > r.mise) { Son.SFX.gain_machine(); Hud.message('+' + (r.gain - r.mise) + ' $ · ' + r.nom); }
    else if (r.gain === r.mise) Hud.message(r.nom);
    else Hud.message(r.nom + (repris() ? ' · LA TABLE GARDE TES ' : ' · LE POUCE GARDE TES ') + r.mise + ' $');
  }

  // --- Le menu ------------------------------------------------------------------------------------------

  function ligneAChoix(libelle, valeurs, cle, noms) {
    const e = etat();
    const i = Math.max(0, valeurs.indexOf(e[cle]));
    const ajuster = function (s) { e[cle] = valeurs[(valeurs.indexOf(e[cle]) + s + valeurs.length) % valeurs.length]; Son.SFX.menu(); };
    return { libelle: libelle, detail: noms[i], ajuster: ajuster, faire: function () { ajuster(1); return false; } };
  }

  function lignes() {
    const t = enCours(), e = etat(), r = regles(), p = B.partie;
    if (t && t.phase === 'joue') {
      const l = [{ libelle: 'LANCER', detail: t.pari === 'pour' ? 'POUR' : 'CONTRE', faire: function () { lancer(); return curseurApres(); } },
                 { libelle: 'CHANGER DE CÔTÉ', detail: t.pari === 'pour' ? 'VERS CONTRE' : 'VERS POUR', faire: function () { changer(); Hud.rafraichirMenu(); return false; } }];
      // Repris, il n'y a plus rien a denoncer : les des sont blancs.
      if (!repris()) l.push({ libelle: 'DÉNONCER LES DÉS', faire: function () { denoncer(); return curseurApres(); } });
      // La preuve d'Irene : seulement quand ses pipes sont sur le feutre, et qu'on est venu pour eux.
      if (t.pipes && !t.glisse && enMission()) {
        // ⚠️ Sans `detail` : la colonne (176 px) n'a pas la place d'un mot de plus après le libellé (vu à la capture).
        l.push({ libelle: 'GLISSER TES DÉS',
                 faire: function () { glisser(); Hud.rafraichirMenu(); if (B.menu) B.menu.curseur = 0; return false; } });
      }
      return l;
    }
    const reste = r.par_jour - e.coups;
    return [ligneAChoix('PARI', ['pour', 'contre'], 'pari', ['POUR', 'CONTRE']),
            ligneAChoix('MISE', r.mises, 'mise', r.mises.map(function (m) { return m + ' $'; })),
            { libelle: 'MISER', detail: e.mise + ' $', actif: (reste > 0 || triche('machines')) && p.argent >= e.mise,
              faire: function () { miser(); return curseurApres(); } }];
  }

  /** Apres un geste, le curseur va ou le pouce voudra aller : LANCER si le coup attend, MISER sinon. */
  function curseurApres() {
    const t = enCours();
    if (B.menu) B.menu.curseur = t && t.phase === 'joue' ? 0 : lignes().length - 1;
    return false;
  }

  function enAttente() {
    const t = enCours();
    return t && t.phase === 'fin' && t.resultat && !t.annonce ? t.resultat.gain : 0;
  }

  function menu() {
    const r = regles(), e = etat(), p = B.partie;
    const reste = Math.max(0, r.par_jour - e.coups), libre = triche('machines');
    const m = { titre: repris() ? r.reprise.titre : 'LA BARBOTTE DU POUCE', sur: (p.argent - enAttente()) + ' $', items: lignes(), largeur: 440, hauteur: 214,
                colonne: 176,
                aide: 'RETOUR ' + r.retour + ' % · ' + (libre ? 'SANS LIMITE' : reste + ' COUP' + (reste > 1 ? 'S' : '') + ' AUJOURD’HUI'),
                dessiner: function (ctx, x, y) { dessiner(ctx, x, y); },
                maj: function (menu) { majMenu(menu); } };
    const t = enCours();
    m.curseur = t && t.phase === 'joue' ? 0 : m.items.length - 1;
    return m;
  }

  function majMenu(m) {
    const item = m.items[m.curseur];
    if (!item || !item.ajuster) return;
    const s = Entree.neuf('gauche') ? -1 : Entree.neuf('droite') ? 1 : 0;
    if (!s) return;
    item.ajuster(s);
    Hud.rafraichirMenu();
  }

  // --- Le dessin, a droite de la liste ------------------------------------------------------------------

  const ENCRE = { or: '#e8b33c', gris: '#8a8698', papier: '#efe6d0', rouge: '#c0392b', noir: '#1b1b24', feutre: '#23422e' };
  const FACES = [null, ['...', '.#.', '...'], ['#..', '...', '..#'], ['#..', '.#.', '..#'], ['#.#', '...', '#.#'],
                 ['#.#', '.#.', '#.#'], ['#.#', '#.#', '#.#']];

  /** Un de de 20 x 20 dans son IVOIRE : blanc, ou jaune (les pipes). Les points de 4 x 4, separes. */
  function de(ctx, x, y, f, ivoire) {
    ctx.fillStyle = '#3a3450'; ctx.fillRect(x - 1, y - 1, 22, 22);
    ctx.fillStyle = ivoire; ctx.fillRect(x, y, 20, 20);
    ctx.fillStyle = ENCRE.noir;
    FACES[f].forEach(function (ligne, yy) {
      for (let xx = 0; xx < 3; xx++) if (ligne[xx] === '#') ctx.fillRect(x + 2 + xx * 6, y + 2 + yy * 6, 4, 4);
    });
  }

  function titre(ctx, s, x, y, c) { Atlas.texte(ctx, s, x, y, c || ENCRE.gris, 1); }

  /** Le feutre : la planche du fond (ou les des rebondissent), les deux des, la main du Pouce qui les pose ;
      a droite, les coups qui gagnent de chaque cote ; en bas, la mefiance du Pouce. */
  function dessiner(ctx, x, y) {
    const t = enCours(), x0 = x + 190, y0 = y + 30;
    const depuis = t ? t.images++ : 0;
    ctx.fillStyle = ENCRE.feutre; ctx.fillRect(x0 - 6, y0 - 6, 244, 150);
    ctx.fillStyle = '#4a2e1a'; ctx.fillRect(x0 - 6, y0 - 6, 244, 6);           // la planche du fond
    ctx.fillStyle = '#6b4a2a'; ctx.fillRect(x0 - 6, y0 + 142, 244, 2);
    const ivoire = t && t.pipes ? IVOIRE.pipe : IVOIRE.vrai;
    let fini = true, faces = [5, 6];
    if (t && t.phase === 'fin' && t.paires && t.paires.length) {
      // Les lancers, un a un — les huit derniers au plus : une barbotte qui relance vingt fois ne fait pas
      // attendre vingt fois.
      const montre = t.paires.slice(-8), avant = t.paires.length - montre.length;
      const k = Math.min(montre.length - 1, Math.floor((depuis - t.fin) / ANIME.lancer));
      faces = montre[k];
      fini = depuis - t.fin >= ANIME.lancer * montre.length;
      if (!fini) { const dx = Math.round(Math.sin(depuis * 1.7) * 4); de(ctx, x0 + 22 + dx, y0 + 30, faces[0], ivoire); de(ctx, x0 + 56 - dx, y0 + 36, faces[1], ivoire); }
      else { de(ctx, x0 + 22, y0 + 34, faces[0], ivoire); de(ctx, x0 + 56, y0 + 34, faces[1], ivoire); }
      titre(ctx, 'LANCER ' + (avant + k + 1) + (fini && t.cote ? ' · ' + (t.cote === 'pour' ? 'POUR' : 'CONTRE') : ''), x0, y0 + 64,
            fini ? ENCRE.papier : ENCRE.gris);
    } else if (t && t.phase === 'joue') {
      de(ctx, x0 + 22, y0 + 34, 5, ivoire); de(ctx, x0 + 56, y0 + 34, 6, ivoire);
      // LA MAIN DU POUCE qui pose les des : elle passe sur le feutre, de gauche a droite, et les laisse.
      if (depuis < ANIME.main) {
        const hx = x0 + Math.round((depuis / ANIME.main) * 110) - 20;
        ctx.fillStyle = '#c98d66'; ctx.fillRect(hx, y0 + 26, 34, 26); ctx.fillRect(hx + 30, y0 + 30, 10, 6);
        ctx.fillStyle = '#9a7a2a'; ctx.fillRect(hx - 14, y0 + 24, 16, 30);    // la manche du veston moutarde
      }
      titre(ctx, 'TON PARI : ' + (t.pari === 'pour' ? 'POUR' : 'CONTRE'), x0, y0 + 64, ENCRE.or);
    } else {
      de(ctx, x0 + 22, y0 + 34, 5, IVOIRE.vrai); de(ctx, x0 + 56, y0 + 34, 6, IVOIRE.vrai);
    }
    const tx = x0 + 120;
    titre(ctx, 'POUR', tx, y0 + 4, ENCRE.or); titre(ctx, '3-3 5-5 6-6 5-6', tx, y0 + 14, ENCRE.papier);
    titre(ctx, 'CONTRE', tx, y0 + 30, ENCRE.or); titre(ctx, '1-1 2-2 4-4 1-2', tx, y0 + 40, ENCRE.papier);
    titre(ctx, 'LE RESTE SE RELANCE', tx, y0 + 56);
    titre(ctx, 'GAGNÉ : 1 POUR 1', tx, y0 + 70, ENCRE.papier);
    titre(ctx, repris() ? regles().reprise.piastre : 'LE POUCE PREND 5 %', tx, y0 + 80);
    titre(ctx, 'MISES DE ' + regles().mises[0] + ' À ' + regles().mises[regles().mises.length - 1] + ' $', x0, y0 + 124);
    dessinerMefiance(ctx, x + 12, y + 128);
    if (t && t.phase === 'fin') {
      if (B.menu) B.menu.sur = (B.partie.argent - (t.resultat && !fini ? t.resultat.gain : 0)) + ' $';
      if (fini) {
        annoncer(t);
        const g = t.resultat.gain, m = t.resultat.mise;
        Atlas.texte(ctx, t.resultat.nom, x0, y0 + 150, g > m ? ENCRE.or : ENCRE.gris, 1);
        Atlas.texte(ctx, g > m ? '+' + (g - m) + ' $' : g === m ? 'MISE RENDUE' : 'PERDU', x + 12, y + 150, g > m ? ENCRE.or : ENCRE.gris, 1);
      }
    }
    B.stats.rects += 40;
  }

  /** La mefiance du Pouce : cinq crans qui s'allument, vert, jaune, rouge, et son nom. */
  function dessinerMefiance(ctx, x, y) {
    // Repris : plus personne ne se mefie de toi. On lit a la place qui tient la table.
    if (repris()) { Atlas.texte(ctx, regles().reprise.croupier.toUpperCase(), x, y, ENCRE.gris, 1); return; }
    const r = regles().mefiance, m = etat().mefiance, crans = Math.min(5, Math.ceil(5 * m / r.sortir));
    const couleur = m >= 60 ? '#e04030' : m >= 25 ? '#e8b33c' : '#5aa05a';
    for (let k = 0; k < 5; k++) { ctx.fillStyle = k < crans ? couleur : '#3a3450'; ctx.fillRect(x + k * 7, y + 1, 5, 3); }
    Atlas.texte(ctx, 'LE POUCE', x + 40, y, crans > 0 ? couleur : ENCRE.gris, 1);
    B.stats.rects += 6;
  }

  // --- La salle -----------------------------------------------------------------------------------------

  function lePouce() { return B.entites.find(function (e) { return e.pouce && e.vivant; }) || null; }

  /** Sur le feutre de la barbotte : la planche du fond, deux des, les jetons. ⚠️ Par-dessus le sol, jamais cuit. */
  function dessinerSalle(ctx, vue) {
    if (!dansLaSalle()) return;
    const pt = (B.interieur.points || []).find(function (p) { return p.type === 'barbotte'; });
    if (!pt) return;
    const x = pt.x * TT - Math.round(vue.x), y = (pt.y - 1) * TT - Math.round(vue.y);
    ctx.fillStyle = '#4a2e1a'; ctx.fillRect(x - 30, y + 1, 76, 3);                 // la planche
    const t = enCours(), ivoire = t && t.pipes && t.phase === 'joue' ? IVOIRE.pipe : IVOIRE.vrai;
    ctx.fillStyle = ivoire; ctx.fillRect(x + 2, y + 12, 4, 4); ctx.fillRect(x + 9, y + 14, 4, 4);
    ctx.fillStyle = '#1b1b24'; ctx.fillRect(x + 3, y + 13, 1, 1); ctx.fillRect(x + 5, y + 15, 1, 1); ctx.fillRect(x + 11, y + 16, 1, 1);
    ctx.fillStyle = '#c0392b'; ctx.fillRect(x - 22, y + 20, 4, 3); ctx.fillStyle = '#2a5ab8'; ctx.fillRect(x - 17, y + 20, 4, 3);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(x + 28, y + 20, 4, 3);
    B.stats.rects += 10;
  }

  /** LA SALLE ENFUMEE, par-dessus les gens : le noir des coins (un voile), la lumiere de la lampe qui pend
      au-dessus de la barbotte, et la fumee qui traine — des nappes qui derivent d'apres `B.t`, sans un de. */
  function dessinerFumee(ctx, vue) {
    if (!dansLaSalle()) return;
    const w = Monde.carte.w * TT, h = Monde.carte.h * TT;
    const ox = -Math.round(vue.x), oy = -Math.round(vue.y);
    const pt = (B.interieur.points || []).find(function (p) { return p.type === 'barbotte'; });
    // La lampe pend au-dessus du MILIEU du feutre (la table fait deux rangees : celle du point et celle d'au-dessus).
    const lx = ox + (pt ? pt.x * TT + 8 : w / 2), ly = oy + (pt ? pt.y * TT : h / 2);
    // Le noir : toute la salle dans la penombre, et plus noir encore dans les coins — sauf le trou de la lampe.
    const g = ctx.createRadialGradient(lx, ly, 24, lx, ly, 300);
    g.addColorStop(0, 'rgba(10,6,8,0.05)');
    g.addColorStop(0.3, 'rgba(10,6,8,0.5)');
    g.addColorStop(1, 'rgba(6,4,8,0.82)');
    ctx.fillStyle = g; ctx.fillRect(ox, oy, w, h);
    // La lampe, vue d'en haut : un abat-jour vert au-dessus du feutre, son ampoule, et un halo chaud.
    ctx.fillStyle = 'rgba(255,214,140,0.12)'; ctx.fillRect(lx - 40, ly - 18, 80, 36);
    ctx.fillStyle = '#16361f'; ctx.fillRect(lx - 7, ly - 4, 14, 8);
    ctx.fillStyle = '#2a5a36'; ctx.fillRect(lx - 6, ly - 3, 12, 2);
    ctx.fillStyle = '#ffe4a0'; ctx.fillRect(lx - 2, ly - 1, 4, 3);
    // La fumee qui traine : des nappes grises, larges, qui derivent lentement et respirent — dans les murs.
    const t = B.t || 0, x0 = TT, x1 = w - TT - 70, y0 = TT, y1 = h - 2 * TT;
    for (let k = 0; k < 9; k++) {
      const sx = x0 + ((k * 97 + t * (0.12 + (k % 3) * 0.05)) % Math.max(1, x1 - x0));
      const sy = y0 + ((k * 53) % Math.max(1, y1 - y0)) + Math.sin(t * 0.01 + k) * 6;
      const a = 0.09 + 0.04 * Math.sin(t * 0.013 + k * 1.7);
      ctx.fillStyle = 'rgba(190,184,176,' + a.toFixed(3) + ')';
      ctx.fillRect(ox + Math.round(sx), oy + Math.round(sy), 70, 10);
      ctx.fillRect(ox + Math.round(sx) + 14, oy + Math.round(sy) - 5, 44, 6);
    }
    B.stats.rects += 24;
  }

  // --- La porte, l'escalier, les gros bras ----------------------------------------------------------------

  /** L'escalier du sous-sol, quand le Pouce ne veut plus te voir : le gros bras d'en haut te refuse. */
  function refuseLEscalier(point) {
    if (!point || point.vers !== SALLE || !barre()) return false;
    const n = joursBarre(), gb = B.entites.find(function (q) { return q.grosBras && q.vivant; });
    Son.SFX.erreur();
    Hud.message(n > 1 ? 'LE POUCE NE VEUT PLUS TE VOIR · ENCORE ' + n + ' JOURS' : 'LE POUCE NE VEUT PLUS TE VOIR · REVIENS DEMAIN', 200);
    if (gb) Entites.bulle(gb, n > 1 ? 'TA FACE, ON LA CONNAÎT, MON CHAMPION.' : 'PAS CE SOIR, MON CHAMPION.', { duree: 200 });
    return true;
  }

  /** La porte du sous-sol, dans la grande salle (`tripot.PORTE`, une barriere de la piece). */
  function porte() {
    if (!B.interieur || B.interieur.slug !== 'nord_casino') return null;
    return (Monde.carte.def.barrieres || []).find(function (b) { return b.slug === 'tripot'; }) || null;
  }

  /** Chaque image : la rumeur de la salle enfumee ; le mot du gros bras d'en haut, une fois par visite ; et qui
      frappe le Pouce ou un gros bras ne redescend pas d'une semaine. */
  function maj() {
    const dedans = dansLaSalle();
    Son.SFX.tripot_salle(dedans ? 1 : 0);
    if (!B.interieur) { B.tripotDit = null; B.tripotChan = null; return; }
    const pb = porte(), j = B.joueur;
    if (pb && j && B.tripotDit !== B.interieur) {
      const gb = B.entites.find(function (q) { return q.grosBras && q.vivant; });
      if (gb && Math.hypot(j.x - (pb.x + 0.5) * TT, j.y - (pb.y + 0.5) * TT) < 4 * TT) {
        B.tripotDit = B.interieur;
        Entites.bulle(gb, Monde.barriereFermee(pb) ? 'SUR INVITATION.' : 'LE JETON? DESCENDS.', { duree: 220 });
      }
    }
    // Repris : le vieux Chan le dit, une fois par visite, quand on s'approche du feutre.
    if (dedans && j && B.tripotChan !== B.interieur) {
      const chan = B.entites.find(function (q) { return q.chan && q.vivant; });
      if (chan && Math.hypot(j.x - chan.x, j.y - chan.y) < 4 * TT) {
        B.tripotChan = B.interieur;
        Entites.bulle(chan, regles().reprise.bulle, { duree: 240 });
      }
    }
    if (!dedans && !pb) return;
    for (const e of B.entites) {
      if (!(e.grosBras || e.pouce) || e.frappe) continue;
      if (e.menace !== B.joueur || (e.vivant && e.vie >= e.vieMax)) continue;
      e.frappe = true;
      sortir(regles().mefiance.barre_jours, 'TU AS FRAPPÉ LES GENS DU POUCE · L’ESCALIER T’EST FERMÉ UNE SEMAINE');
    }
  }

  return { regles, face, coup, jet, pipe, poidsContre, gain, mefianceApres, etat, barre, enCours, tirages, miser, lancer,
           changer, denoncer, glisser, repris, enMission, menu, dessiner, dessinerSalle, dessinerFumee, refuseLEscalier, porte, maj, IVOIRE, SALLE };
})();
