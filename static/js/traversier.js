/* Bandini — le traversier : Les Quais ↔ La Pointe, a l'heure (M12).

   Demande du plan : « Les Quais ↔ La Pointe, a l'heure, quatre chars a bord, il part
   sans toi. »

   ⚠️ PYTHON TROUVE LES QUAIS, ICI ON TRAVERSE. Les deux escales, la coque et
   l'horaire viennent du paquet (`carte.traversier`, `app/traversier.py`). La place
   du bateau ne depend que de l'heure de la partie (`placeA`) — comme les autobus et
   la rame du metro : rien a simuler, rien a oublier, et deux rives voient le meme
   traversier a la meme heure.

   ⚠️ ON MONTE EN ROULANT, PAS AU BOUTON. A quai, le PONT est une vraie tuile : la
   carte le marque sol carrossable (`poser`), on y entre en char ou a pied par le
   bout de rue qui y touche. A l'heure du depart, tout ce qui est SUR LE PONT part
   avec lui (`embarquer`) — et ce qui n'y est pas reste a quai : il part sans toi.
   Pendant la traversee, ce qui est a bord suit la coque au pixel et ne fait rien
   d'autre (`Vehicules.maj` et `Entites.majJoueur` le sautent) ; a l'autre quai, le
   pont redevient une tuile, et on en sort comme on y est entre.

   ⚠️ ET LA CARTE EST RENDUE TELLE QU'ELLE ETAIT. Chaque tuile que `poser` change est
   notee, et `lever` la remet — le juge compare la carte avant et apres un
   aller-retour, octet par octet. */

const Traversier = (function () {
  'use strict';

  //: Le tri du dessin : la coque se range avec le reste par sa ligne de flottaison
  //: NORD, pour que ce qui est a bord (plus au sud) se peigne par-dessus.
  const ID_TRI = 1e9 + 500;

  //: A combien de pixels d'un bout de quai on lit l'horaire au HUD.
  const PORTEE_INFO_PX = 5 * 16;

  //: Au-dela, ce qui etait a bord a ete deplace par autre chose (une scene, la
  //: mort, l'hopital) : on le lache au lieu de le ramener de force sur le pont.
  const DECROCHE_PX = 40;

  //: Jusqu'ou on entend la corne.
  const PORTEE_CORNE_PX = 900;

  let prepare = null, source = null;
  //: Le quai ou la coque est posee, et ce que `poser` a change dans la carte.
  let pose = null;
  //: Ce qui est a bord : { e, dx, dy, x, y } — le decalage sur le pont, et la
  //: derniere place ou on l'a mis (pour voir s'il a ete deplace par autre chose).
  const bord = [];
  //: Faux tant qu'on n'a pas vu une premiere image : la corne ne sonne pas au chargement.
  let vu = false;

  function donnees() {
    const def = B.defs && B.defs.carte;
    const brut = def && def.traversier;
    if (!brut) return null;
    if (source === brut) return prepare;
    source = brut;
    const c = brut.coque;
    prepare = {
      coque: c, horaire: brut.horaire,
      largeurPx: c.longueur * TT, hauteurPx: c.largeur * TT,
      escales: brut.escales.map(function (q, k) {
        return { k: k, nom: q.nom, district: q.district, x: q.x, y: q.y, cote: q.cote, acces: q.acces,
                 px: q.x * TT, py: q.y * TT };
      }),
    };
    return prepare;
  }

  // --- L'horaire -----------------------------------------------------------------------

  /** Ou en est le traversier a cette heure de la journee (0 a 1). Pure.
      ⚠️ Depart des Quais aux heures PAIRES, de La Pointe aux heures IMPAIRES :
      [0, T) la traversee aller, [T, P/2) a quai en face, [P/2, P/2 + T) le retour,
      [P/2 + T, P) a quai aux Quais. `reste_h` : avant le prochain changement. */
  function etatA(heure) {
    const d = donnees();
    if (!d) return null;
    const h = d.horaire, P = h.periode_h, demi = P / 2, T = h.traversee_h;
    const t = ((heure * 24) % P + P) % P;
    if (t < T) return { phase: 'traverse', de: 0, vers: 1, u: t / T, reste_h: T - t };
    if (t < demi) return { phase: 'quai', escale: 1, reste_h: demi - t };
    if (t < demi + T) return { phase: 'traverse', de: 1, vers: 0, u: (t - demi) / T, reste_h: demi + T - t };
    return { phase: 'quai', escale: 0, reste_h: P - t };
  }

  /** La part du chemin faite a `u` de la traversee : il prend de la vitesse, file,
      et freine en arrivant (un trapeze de vitesse — pas un saut au quai). */
  function avance(u, elan) {
    const vmax = 1 / (1 - elan);
    if (u < elan) return vmax * u * u / (2 * elan);
    if (u > 1 - elan) return 1 - vmax * (1 - u) * (1 - u) / (2 * elan);
    return vmax * (u - elan / 2);
  }

  /** Le coin nord-ouest de la coque, en pixels, a cette heure — et l'etat. */
  function placeA(heure) {
    const d = donnees(), s = etatA(heure);
    if (!s) return null;
    if (s.phase === 'quai') { const q = d.escales[s.escale]; return { x: q.px, y: q.py, etat: s }; }
    const a = d.escales[s.de], b = d.escales[s.vers], f = avance(s.u, d.horaire.elan);
    return { x: a.px + (b.px - a.px) * f, y: a.py + (b.py - a.py) * f, etat: s };
  }

  function imagesParHeure() { return B.defs.economie.jour_secondes * 60 / 24; }

  // --- Le pont, a quai -----------------------------------------------------------------

  /** Une tuile du pont (et pas de la cabine), a quai en `q` ? */
  function tuileDuPont(q, tx, ty) {
    const d = donnees(), col = tx - q.x, r = ty - q.y;
    return col >= 0 && col < d.coque.longueur && r >= 0 && r < d.coque.largeur && r !== d.coque.cabine;
  }

  /** La coque accoste : ses tuiles deviennent du sol. Le pont se roule ; la cabine est
      un mur. ⚠️ Le pont est aussi CHAUSSEE (`route`) : un flaneur de la rive n'y
      descend pas se promener, il resterait a bord sans le savoir. */
  function poser(k) {
    const d = donnees(), q = d.escales[k], c = Monde.carte, sauve = [];
    for (let r = 0; r < d.coque.largeur; r++) {
      for (let col = 0; col < d.coque.longueur; col++) {
        const i = (q.y + r) * c.w + q.x + col;
        sauve.push([i, c.solide[i], c.route[i], c.passage[i]]);
        const pont = r !== d.coque.cabine;
        c.solide[i] = pont ? 0 : 1;
        c.route[i] = pont ? 1 : 0;
        c.passage[i] = 0;
      }
    }
    pose = { carte: c, k: k, sauve: sauve };
  }

  /** La coque largue les amarres : la carte redevient exactement ce qu'elle etait. */
  function lever() {
    if (!pose) return;
    const c = pose.carte;
    for (const s of pose.sauve) { c.solide[s[0]] = s[1]; c.route[s[0]] = s[2]; c.passage[s[0]] = s[3]; }
    pose = null;
  }

  /** Le bout de quai le plus proche : la ou l'on remet quelqu'un qui descend. */
  function quaiLePlusProche(q, x, y) {
    let mieux = null, dMin = Infinity;
    for (const t of q.acces) {
      const px = t[0] * TT + 8, py = t[1] * TT + 8, d2 = (px - x) * (px - x) + (py - y) * (py - y);
      if (d2 < dMin) { dMin = d2; mieux = { x: px, y: py }; }
    }
    return mieux;
  }

  // --- Le depart et l'arrivee ------------------------------------------------------------

  function aBord(e) { return !!(e && e.aBord); }

  /** L'heure du depart : ce qui est sur le pont part. Le joueur et les chars restent
      a bord ; un passant ou un agent pose le pied sur le quai — il n'a pas pris de
      billet, il s'etait egare. */
  function embarquer(k) {
    const d = donnees(), q = d.escales[k], j = B.joueur;
    let joueur = false;
    for (const e of B.entites) {
      if (!e.vivant && e.type !== 'vehicule') continue;
      const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
      if (!tuileDuPont(q, tx, ty)) continue;
      if (e.type === 'vehicule' || e === j) {
        if (e.aBord) continue;
        e.aBord = true;
        e.vx = 0; e.vy = 0;
        if (e.type === 'vehicule') e.vitesse = 0;
        bord.push({ e: e, dx: e.x - q.px, dy: e.y - q.py, x: e.x, y: e.y });
        if (e === j || (j && j.dansVehicule === e)) joueur = true;
      } else if (e.type === 'pieton' || e.type === 'police') {
        const p = quaiLePlusProche(q, e.x, e.y);
        if (p) { e.x = p.x; e.y = p.y; e.vx = 0; e.vy = 0; }
      }
    }
    // Au volant : le joueur n'est pas sur la liste, son char l'y met.
    if (j && j.dansVehicule && j.dansVehicule.aBord && !j.aBord) {
      j.aBord = true;
      bord.push({ e: j, dx: j.x - q.px, dy: j.y - q.py, x: j.x, y: j.y });
      joueur = true;
    }
    if (joueur) {
      const vers = d.escales[1 - k];
      Hud.message('EN ROUTE POUR ' + vers.nom.toUpperCase());
      // ⚠️ Sa musique de PONT : la station qui attendait le traversier depuis M9.
      Son.Radio.jouer('traversier');
    }
  }

  /** Ce qui est a bord suit la coque, au pixel. */
  function suivre(ici) {
    const j = B.joueur;
    for (let i = bord.length - 1; i >= 0; i--) {
      const b = bord[i], e = b.e;
      const parti = e !== j && B.entites.indexOf(e) < 0;
      const deplace = Math.hypot(e.x - b.x, e.y - b.y) > DECROCHE_PX;
      if (parti || deplace || (e === j && !e.vivant)) { e.aBord = false; bord.splice(i, 1); continue; }
      e.x = ici.x + b.dx; e.y = ici.y + b.dy;
      e.vx = 0; e.vy = 0;
      if (e.type === 'vehicule') e.vitesse = 0;
      b.x = e.x; b.y = e.y;
    }
    // Au volant, le joueur est ou est son char, a l'image pres.
    if (j && j.aBord && j.dansVehicule && j.dansVehicule.aBord) { j.x = j.dansVehicule.x; j.y = j.dansVehicule.y; }
  }

  /** A quai : tout le monde descend — c'est-a-dire que plus rien n'est tenu. */
  function debarquer(k) {
    const d = donnees(), j = B.joueur;
    let joueur = false;
    for (const b of bord) { if (b.e === j) joueur = true; b.e.aBord = false; }
    bord.length = 0;
    if (!joueur) return;
    Hud.message(d.escales[k].nom.toUpperCase());
    const v = j.dansVehicule;
    if (v && v.def && v.def.radio) Son.Radio.jouer(v.def.radio);
    else { Son.Radio.arreter(); Son.Chef.maj(); }
  }

  function corne(q) {
    const x = q.px + donnees().largeurPx / 2, y = q.py + TT;
    if (Son.SFX.corne) Son.SFX.corne(x, y, PORTEE_CORNE_PX);
  }

  // --- A chaque image ------------------------------------------------------------------

  function maj() {
    const d = donnees(), p = B.partie;
    if (!d || !p || B.interieur || !Monde.carte) return;
    // La ville a ete rechargee (une partie chargee) : la carte neuve n'a rien a rendre.
    if (pose && pose.carte !== Monde.carte) { pose = null; for (const b of bord) b.e.aBord = false; bord.length = 0; }
    const ici = placeA(p.heure), s = ici.etat;
    const escale = s.phase === 'quai' ? s.escale : null;
    const premiereImage = !vu;
    vu = true;
    // 1. Le depart : ce qui est sur le pont part avec lui.
    if (pose && pose.k !== escale) {
      const k = pose.k;
      embarquer(k);
      lever();
      if (!premiereImage) corne(d.escales[k]);
    }
    // 2. Ce qui est a bord suit la coque — a quai compris, pour arriver pile.
    suivre(ici);
    // 3. L'arrivee : le pont redevient une tuile, et plus rien n'est tenu.
    if (escale !== null && !pose) {
      poser(escale);
      if (bord.length) debarquer(escale);
      if (!premiereImage) corne(d.escales[escale]);
    }
  }

  /** Remet tout a zero (nouvelle partie, partie chargee). */
  function oublier() {
    lever();
    for (const b of bord) b.e.aBord = false;
    bord.length = 0;
    vu = false;
  }

  // --- Ce que le HUD en dit ---------------------------------------------------------------

  function heureTexte(h) {
    const hh = ((Math.round(h) % 24) + 24) % 24;
    return (hh < 10 ? '0' : '') + hh + ':00';
  }

  function dureeTexte(heures) {
    const s = Math.max(0, Math.round(heures * imagesParHeure() / 60));
    return s < 60 ? Math.max(1, s) + ' S' : Math.round(s / 60) + ' MIN';
  }

  /** L'escale dont on est a deux pas, ou null. */
  function escaleIci(j) {
    const d = donnees();
    if (!d || !j || B.interieur) return null;
    for (const q of d.escales) {
      for (const t of q.acces) {
        if (Math.hypot(t[0] * TT + 8 - j.x, t[1] * TT + 8 - j.y) <= PORTEE_INFO_PX) return q;
      }
      if (j.x >= q.px && j.x < q.px + d.largeurPx && j.y >= q.py && j.y < q.py + d.hauteurPx) return q;
    }
    return null;
  }

  /** La ligne du bas de l'ecran : a bord, quand on arrive ; au quai, quand il part. */
  function texteDInfo(j) {
    const d = donnees(), p = B.partie;
    if (!d || !j || !p || B.interieur) return null;
    const s = etatA(p.heure);
    if (j.aBord && s.phase === 'traverse') {
      return 'TRAVERSIER · ' + d.escales[s.vers].nom.toUpperCase() + ' DANS ' + dureeTexte(s.reste_h);
    }
    const q = escaleIci(j);
    if (!q) return null;
    const vers = d.escales[1 - q.k].nom.toUpperCase();
    if (s.phase === 'quai' && s.escale === q.k) return 'TRAVERSIER POUR ' + vers + ' · DÉPART DANS ' + dureeTexte(s.reste_h);
    // Le prochain depart d'ici : les heures paires aux Quais, impaires en face.
    const h = p.heure * 24, P = d.horaire.periode_h, decale = q.k * P / 2;
    const prochain = Math.floor((h - decale) / P + 1) * P + decale;
    return 'TRAVERSIER POUR ' + vers + ' · DÉPART ' + heureTexte(prochain);
  }

  // --- Le dessin ---------------------------------------------------------------------------

  function peindreCoque(ctx, x0, y0, s) {
    const d = donnees(), L = d.largeurPx, H = d.hauteurPx, C = d.coque.cabine * TT;
    const nuit = Monde.estNuit();
    const quai = s.phase === 'quai';
    // Le sillage, derriere la poupe, quand il file.
    if (!quai) {
      const sens = d.escales[s.vers].px > d.escales[s.de].px ? -1 : 1;
      const queue = sens < 0 ? x0 : x0 + L;
      ctx.fillStyle = 'rgba(235,244,248,0.55)';
      for (let k = 0; k < 7; k++) {
        const ox = queue + sens * (4 + k * 6) - (sens < 0 ? 4 : 0), ecart = 3 + k * 2;
        ctx.fillRect(ox, y0 + H / 2 - ecart, 4, 1);
        ctx.fillRect(ox, y0 + H / 2 + ecart, 4, 1);
      }
    }
    // La coque : un double-bout (il ne fait jamais demi-tour), les coins rognes.
    ctx.fillStyle = '#1d2230'; ctx.fillRect(x0 + 2, y0, L - 4, H); ctx.fillRect(x0, y0 + 2, L, H - 4);
    ctx.fillStyle = '#b8342c'; ctx.fillRect(x0 + 2, y0 + H - 4, L - 4, 3);          // la ligne de flottaison
    ctx.fillStyle = '#eeeae0'; ctx.fillRect(x0 + 2, y0 + H - 6, L - 4, 2);
    // Le pont : l'acier gris, deux voies, quatre places.
    ctx.fillStyle = '#7d828b'; ctx.fillRect(x0 + 2, y0 + 1, L - 4, C - 1);
    ctx.fillStyle = '#e2b53c';
    for (let x = x0 + 6; x < x0 + L - 6; x += 8) ctx.fillRect(x, y0 + TT - 1, 4, 1);    // entre les voies
    ctx.fillRect(x0 + L / 2, y0 + 2, 1, C - 4);                                       // quatre places
    // Les rampes aux deux bouts, rayees.
    for (const bx of [x0 + 1, x0 + L - 4]) {
      for (let y = y0 + 2; y < y0 + C - 1; y += 4) {
        ctx.fillStyle = '#e2b53c'; ctx.fillRect(bx, y, 3, 2);
        ctx.fillStyle = '#23252b'; ctx.fillRect(bx, y + 2, 3, 2);
      }
    }
    // Le garde-corps du nord.
    ctx.fillStyle = '#d8d4c8'; ctx.fillRect(x0 + 5, y0, L - 10, 1);
    // La cabine : blanche, une rangee de hublots, la cheminee au milieu.
    const cy = y0 + C;
    ctx.fillStyle = '#cfcabd'; ctx.fillRect(x0 + 10, cy - 3, L - 20, 5);             // le toit
    ctx.fillStyle = '#eeeae0'; ctx.fillRect(x0 + 10, cy + 2, L - 20, H - C - 8);     // la face
    ctx.fillStyle = nuit ? '#f2d27a' : '#35607c';
    for (let x = x0 + 14; x < x0 + L - 14; x += 7) ctx.fillRect(x, cy + 4, 4, 3);
    ctx.fillStyle = '#b8342c'; ctx.fillRect(x0 + L / 2 - 4, cy - 9, 8, 7);
    ctx.fillStyle = '#1d2230'; ctx.fillRect(x0 + L / 2 - 4, cy - 10, 8, 2);
    // Des bouees aux deux bouts de la cabine.
    ctx.fillStyle = '#e2672c'; ctx.fillRect(x0 + 11, cy + 3, 2, 3); ctx.fillRect(x0 + L - 13, cy + 3, 2, 3);
    // Des gens au bastingage de la cabine : combien, c'est la traversee qui le dit.
    // ⚠️ Le compte change A QUAI (a l'heure moins vingt), jamais en pleine traversee.
    const voyage = Math.floor(B.partie.jour * 24 + B.partie.heure * 24 + 0.2);
    const n = hash2(voyage, 41) % 4;
    for (let k = 0; k < n; k++) {
      const px = x0 + 18 + ((hash2(voyage, k) % (L - 36)) >> 0);
      ctx.fillStyle = ['#c24a3a', '#3a6fb0', '#e0c35a', '#5a8a4a'][hash2(k, voyage) % 4];
      ctx.fillRect(px, cy - 6, 3, 3);
      ctx.fillStyle = '#e6c9a8'; ctx.fillRect(px, cy - 8, 3, 2);
    }
    // Les feux de route, la nuit : rouge a babord, vert a tribord, blanc au mat.
    if (nuit) {
      ctx.fillStyle = '#ff5a4e'; ctx.fillRect(x0 + 3, y0 + 3, 2, 2);
      ctx.fillStyle = '#5fe08a'; ctx.fillRect(x0 + L - 5, y0 + 3, 2, 2);
      ctx.fillStyle = '#ffffff'; ctx.fillRect(x0 + L / 2 - 1, cy - 13, 2, 2);
    }
    B.stats.rects += 40;
  }

  /** Le panneau du quai : bleu, un bateau blanc, sur un poteau. */
  function peindrePanneau(ctx, x, y) {
    ctx.fillStyle = '#4a4d55'; ctx.fillRect(x, y - 12, 1, 12);
    ctx.fillStyle = '#1f4f8a'; ctx.fillRect(x - 6, y - 20, 13, 9);
    ctx.fillStyle = '#eeeae0'; ctx.fillRect(x - 4, y - 15, 9, 2); ctx.fillRect(x - 3, y - 13, 7, 1); ctx.fillRect(x - 1, y - 18, 2, 3);
    B.stats.rects += 5;
  }

  /** Comme la foire : la coque et les panneaux se trient avec les passants et les
      chars, mais ne sont pas dans `B.entites`. */
  function ajouterVisibles(visibles, cx, cy) {
    const d = donnees(), p = B.partie;
    if (!d || !p) return;
    const ici = placeA(p.heure);
    const x0 = Math.round(ici.x), y0 = Math.round(ici.y);
    if (x0 + d.largeurPx + 48 > cx && x0 - 48 < cx + VW && y0 + d.hauteurPx > cy - 16 && y0 - 16 < cy + VH) {
      visibles.push({ id: ID_TRI, vivant: true, x: x0, y: y0 - 0.5,
                      peindreFoire: function (ctx) { peindreCoque(ctx, x0 - Math.round(cx), y0 - Math.round(cy), ici.etat); } });
    }
    d.escales.forEach(function (q, k) {
      // Le panneau se plante a cote du premier bout de quai — pas dessus : les chars y passent.
      const t = q.acces[0];
      const sx = (t[0] - (q.cote === 'nord' ? 1 : 0)) * TT + 8;
      const sy = (t[1] - (q.cote === 'nord' ? 0 : 1)) * TT + 12;
      if (sx < cx - 16 || sx > cx + VW + 16 || sy < cy - 8 || sy > cy + VH + 24) return;
      visibles.push({ id: ID_TRI + 1 + k, vivant: true, x: sx, y: sy,
                      peindreFoire: function (ctx) { peindrePanneau(ctx, sx - Math.round(cx), sy - Math.round(cy)); } });
    });
  }

  /** La traversee sur la grande carte : un pointille bleu d'un quai a l'autre. */
  function dessinerSurLaCarte(ctx, pos) {
    const d = donnees();
    if (!d) return;
    const a = d.escales[0], b = d.escales[1];
    const pa = pos(a.px + d.largeurPx / 2, a.py + TT), pb = pos(b.px + d.largeurPx / 2, b.py + TT);
    const n = Math.max(Math.abs(pb.x - pa.x), Math.abs(pb.y - pa.y), 1);
    ctx.fillStyle = '#8fc6ea';
    for (let k = 0; k <= n; k += 3) ctx.fillRect(Math.round(pa.x + (pb.x - pa.x) * k / n), Math.round(pa.y + (pb.y - pa.y) * k / n), 1, 1);
    for (const p of [pa, pb]) { ctx.fillStyle = '#101018'; ctx.fillRect(p.x - 2, p.y - 2, 5, 5); ctx.fillStyle = '#8fc6ea'; ctx.fillRect(p.x - 1, p.y - 1, 3, 3); }
    B.stats.rects += Math.ceil(n / 3) + 4;
  }

  return {
    donnees, etatA, placeA, avance, maj, oublier, aBord, texteDInfo, escaleIci, ajouterVisibles, dessinerSurLaCarte,
    get pose() { return pose; }, get bord() { return bord.slice(); },
  };
})();
