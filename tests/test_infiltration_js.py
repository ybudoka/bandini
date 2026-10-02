"""L'infiltration au banc (docs/jalons/infiltration-portes-verrouillees-et-gardes-prives.md) : la villa du
maire (`app/blocs/villa.py`), ses gardes de ronde (`Police.garder`), ses escaliers et ses cadres de caméra
(`Infiltration`, `Monde.cibleCamera`), ses serrures (`carte.BARRIERES`, condition `objet`), l'objectif
`obtenir` — et les trois infiltrations JOUÉES de bout en bout. Depuis le 2 oct. 2026, v01, v02 et v03 sont les trois
actes d'UN chapitre, _Une nuit à la villa_ (`nuit_a_la_villa`, docs/jalons/des-missions-en-chapitres.md, vague V) :
chaque acte commence par le saut au chemin de la villa (`sur_place` sur son marqueur), et chaque juge le reprend là où
une vieille partie le reprendrait (les actes d'avant faits, la clé au sac).

⚠️ **UN PASSE-MURAILLE N'EST PAS UN JOUEUR.** Le marcheur du banc (`aller`) avance au pas du joueur
(1,2 px par image) d'une tuile à la suivante d'un chemin où l'on marche (les murs, les clôtures et les
serrures fermées arrêtent ; les escaliers mènent à leur autre bout), et il ATTEND, ou recule, quand un
garde le verrait — c'est tout ce qu'un joueur prudent fait. Les gardes, eux, marchent pour vrai, et
regardent pour vrai : le banc ne les touche jamais. Le vol se fait au bouton (ACTION dans le dos), le
piratage au clavier (le pilote de `test_piratage_js.py`), l'entrée et la sortie du bloc en poussant contre
le bord.
"""

import json

from outils_missions import outils

from app.blocs import villa

OUTILS = outils("fermer", "passer", "etape") + (
    "  const LIEUX_VILLA = " + json.dumps(villa.LIEUX) + ", SERRURES_VILLA = " + json.dumps(villa.SERRURES) + ";\n"
) + """
  const TT = 16;
  const CACHETTES = [];   // où le banc s'est caché (les sondes le lisent)
  async function laisserArriver(L, o) { for (let i = 0; i < 6; i++) { o.frame(1); await o.attendre(); } }
  function nuit(L) { L.B.partie.heure = 23 / 24; }
  function commencer(L, o, slug) { L.Histoire.commencer(slug); L.B.cinema = null; L.B.scene = null; o.frame(2); fermer(L); }
  /** Le chapitre de la villa, à l'acte où la partie en est : le saut de son marqueur (fondu, la nuit, le chemin),
      puis l'étape `e` — le premier objectif de l'acte après l'« aller » de nuit, fait en arrivant. */
  async function aLActe(L, o, e) {
    commencer(L, o, 'nuit_a_la_villa');
    await jusqua(L, o, e);
    return !!(L.B.bloc && L.B.bloc.slug === 'villa');
  }
  /** Jouer jusqu'à l'étape `e`, et que le saut d'un marqueur soit fini — ⚠️ la carte du bloc se charge par le
      réseau (`Blocs.charger`) : le fondu l'attend, et le banc doit la laisser arriver (`o.attendre`). */
  async function jusqua(L, o, e) {
    for (let k = 0; k < 2400 && etape(L) !== null && (etape(L) < e || L.B.transition); k++) { o.frame(1); await o.attendre(); fermer(L); }
    fermer(L);
    return etape(L);
  }

  /** Passer dans la villa : au bout de la rue du bord ouest des Érables, on pousse vers l'ouest. */
  async function entrerALaVilla(L, o) {
    const B = L.B, j = B.joueur, p = B.defs.blocs.find(function (b) { return b.slug === 'villa'; }).passage;
    if (B.menu) L.Hud.fermerMenu();
    j.x = TT + 8; j.y = (p.de + 2) * TT + 8; L.Entites.indexer(); L.Monde.centrerCamera(j.x, j.y);
    await laisserArriver(L, o);
    o.touche('KeyA');
    for (let i = 0; i < 120 && !B.transition; i++) o.frame(1);
    o.relacher('KeyA');
    for (let i = 0; i < 200 && (B.transition || !B.bloc); i++) o.frame(1);
    for (let i = 0; i < 4; i++) { o.frame(1); fermer(L); }
    return !!(B.bloc && B.bloc.slug === 'villa');
  }

  /** Ressortir en ville : au bout du chemin, on pousse vers l'est. */
  function sortirDeLaVilla(L, o) {
    const B = L.B, j = B.joueur;
    j.x = 70 * TT + 8; j.y = 21 * TT + 8; L.Entites.indexer();
    o.touche('KeyD');
    for (let i = 0; i < 120 && !B.transition; i++) { o.frame(1); fermer(L); }
    o.relacher('KeyD');
    for (let i = 0; i < 200 && (B.transition || B.bloc); i++) { o.frame(1); fermer(L); }
    return !B.bloc;
  }

  function fiche(L) { return L.B.bloc && L.B.bloc.def.bloc; }
  function garde(L, slug) { return L.Infiltration.gardes().find(function (g) { return g.gardeSlug === slug; }) || null; }
  function tuileDe(e) { return { x: Math.floor(e.x / TT), y: Math.floor(e.y / TT) }; }

  /** L'autre bout d'un escalier dont (x, y) est une marche, ou null. */
  function saut(L, x, y) {
    for (const e of (fiche(L) || {}).escaliers || []) {
      for (const paire of [[e.a, e.b], [e.b, e.a]]) {
        if (paire[0].tuiles.some(function (t) { return t[0] === x && t[1] === y; })) return { x: paire[1].arrivee[0], y: paire[1].arrivee[1] };
      }
    }
    return null;
  }

  /** Le chemin (tuiles) d'ici à là, où un piéton marche : ni mur, ni clôture, ni arbre, ni serrure
      fermée — et un escalier mène à son autre bout. */
  function chemin(L, de, vers) {
    const M = L.Monde, c = M.carte;
    const arbres = new Set(((L.B.bloc && L.B.bloc.def.decor) || []).filter(function (d) { return d.type === 'arbre'; })
      .map(function (d) { return d.x + ',' + d.y; }));
    const ok = function (x, y) {
      return x >= 0 && y >= 0 && x < c.w && y < c.h && !M.bloque(x, y, M.MASQUE_PIETON)
        && !M.barriereA(x, y, 'pieton') && !arbres.has(x + ',' + y);
    };
    const cle = function (t) { return t.x + ',' + t.y; };
    const prec = new Map([[cle(de), null]]), file = [de];
    while (file.length) {
      const t = file.shift();
      if (t.x === vers.x && t.y === vers.y) break;
      const voisines = [{ x: t.x + 1, y: t.y }, { x: t.x - 1, y: t.y }, { x: t.x, y: t.y + 1 }, { x: t.x, y: t.y - 1 }];
      const s = saut(L, t.x, t.y);
      if (s) voisines.push(s);
      for (const v of voisines) {
        if (prec.has(cle(v)) || !ok(v.x, v.y)) continue;
        prec.set(cle(v), t); file.push(v);
      }
    }
    if (!prec.has(cle(vers))) return null;
    const out = [];
    for (let t = vers; t && cle(t) !== cle(de); t = prec.get(cle(t))) out.unshift(t);
    return out;
  }

  /** Un garde te verrait-il ici, maintenant ou dans un instant ? Son cône (avec de la marge) jusqu'à
      7 tuiles, regardé dans le sens où il marche ET dans celui qu'il prendra à son prochain point de
      ronde, s'il y arrive (il s'y tourne, et il balaie) ; et tout ce qui est à moins de 2,5 tuiles.
      `sauf` : celui dont on fait les poches — lui, on l'approche par-derrière. */
  function danger(L, x, y, sauf) {
    const regles = (fiche(L) && fiche(L).regles_des_gardes) || { balaye_deg: 35 };
    const demi = (50 + 12) * Math.PI / 180, balaye = regles.balaye_deg * Math.PI / 180;
    for (const g of L.Infiltration.gardes()) {
      if (!g.vivant || g.etat === 'assomme') continue;
      const d = Math.hypot(g.x - x, g.y - y);
      if (d > 7 * TT || !L.Monde.ligneLibre(g.x, g.y, x, y)) continue;
      if (g !== sauf && d < 2.5 * TT) return true;
      const caps = [[g.angle, 0]];
      const pt = g.ronde[(g.rondeI || 0) % g.ronde.length];
      if (pt.length > 2 && (g.pauseT > 0 || Math.hypot(pt[0] * TT + 8 - g.x, pt[1] * TT + 8 - g.y) < 3 * TT)) {
        caps.push([pt[2] * Math.PI / 180, balaye]);
      }
      const vers = Math.atan2(y - g.y, x - g.x);
      for (const c of caps) {
        let e = Math.abs(vers - c[0]) % (2 * Math.PI);
        if (e > Math.PI) e = 2 * Math.PI - e;
        if (e < demi + c[1]) return true;
      }
    }
    return false;
  }

  /** Attendre (sans bouger) que `pret()` soit vrai. */
  function attendre(L, o, pret, max) {
    for (let n = 0; n < (max || 9000); n++) { fermer(L); if (pret()) return true; o.frame(1); }
    return false;
  }

  /** Un pas pour s'éloigner du garde le plus proche, si le sol le permet. */
  function fuir(L, j) {
    const gs = L.Infiltration.gardes().filter(function (g) { return g.vivant; });
    if (!gs.length) return false;
    gs.sort(function (a, b) { return Math.hypot(a.x - j.x, a.y - j.y) - Math.hypot(b.x - j.x, b.y - j.y); });
    const g = gs[0], d = Math.hypot(j.x - g.x, j.y - g.y) || 1;
    const nx = j.x + (j.x - g.x) / d * 1.2, ny = j.y + (j.y - g.y) / d * 1.2;
    if (L.Monde.bloque(Math.floor(nx / TT), Math.floor(ny / TT), L.Monde.MASQUE_PIETON)) return false;
    j.x = nx; j.y = ny; L.Entites.regarder(j, j.x - g.x, j.y - g.y);
    return true;
  }

  /** Une tuile qu'un garde regarderait en se retournant : à moins de 7 tuiles de lui, sans mur entre. */
  function exposee(L, x, y) {
    return L.Infiltration.gardes().some(function (g) {
      return g.vivant && g.etat !== 'assomme' && Math.hypot(g.x - x, g.y - y) < 7 * TT && L.Monde.ligneLibre(g.x, g.y, x, y);
    });
  }

  /** Une tuile SURVEILLÉE : un point de la ronde d'un garde (tous les points, tuile par tuile, le long de
      chaque segment) la voit à moins de `SURVEILLANCE` tuiles, sans mur entre. Ce qui ne l'est pas est une
      vraie cachette : aucun garde n'y regarde jamais, où qu'il soit dans sa ronde. */
  const SURVEILLANCE = 6;
  let surveillees = null;
  function surveillee(L, tx, ty) {
    if (!surveillees) {
      surveillees = [];
      for (const g of fiche(L).gardes) {
        const r = g.ronde, pts = [];
        for (let k = 0; k < r.length; k++) {
          const a = r[k], b = r[(k + 1) % r.length], n = Math.max(1, Math.abs(b[0] - a[0]) + Math.abs(b[1] - a[1]));
          for (let q = 0; q <= n; q++) pts.push([(a[0] + (b[0] - a[0]) * q / n) * TT + 8, (a[1] + (b[1] - a[1]) * q / n) * TT + 8]);
        }
        surveillees.push(pts);
      }
    }
    const x = tx * TT + 8, y = ty * TT + 8;
    return surveillees.some(function (pts) {
      return pts.some(function (p) { return Math.hypot(p[0] - x, p[1] - y) < SURVEILLANCE * TT && L.Monde.ligneLibre(p[0], p[1], x, y); });
    });
  }

  /** ⚠️ SE CACHER (la villa barbelée, 30 sept. 2026) : quand un garde tient le passage — le corridor du 2e,
      qu'il parcourt d'un bout à l'autre —, attendre ou reculer ne suffit plus : il revient. Un joueur se glisse
      dans la pièce d'à côté et le laisse passer. La cachette : une tuile à `rayon` pas au plus, qu'on rejoint
      sans entrer dans un cône, qu'aucune ronde ne surveille (`surveillee`) et d'où aucun garde ne nous voit —
      la plus près du but. */
  function cachette(L, de, vers, rayon) {
    const M = L.Monde, c = M.carte, cle = function (t) { return t.x + ',' + t.y; };
    const vues = new Map([[cle(de), 0]]), file = [de];
    let mieux = null, score = Infinity;
    while (file.length) {
      const t = file.shift(), n = vues.get(cle(t));
      if (!exposee(L, t.x * TT + 8, t.y * TT + 8) && !surveillee(L, t.x, t.y)) {
        const s = Math.abs(t.x - vers.x) + Math.abs(t.y - vers.y) + n * 0.5;
        if (s < score) { score = s; mieux = t; }
      }
      if (n >= rayon) continue;
      for (const v of [{ x: t.x + 1, y: t.y }, { x: t.x - 1, y: t.y }, { x: t.x, y: t.y + 1 }, { x: t.x, y: t.y - 1 }]) {
        if (vues.has(cle(v)) || v.x < 0 || v.y < 0 || v.x >= c.w || v.y >= c.h) continue;
        if (M.bloque(v.x, v.y, M.MASQUE_PIETON) || M.barriereA(v.x, v.y, 'pieton') || saut(L, v.x, v.y)) continue;
        if (danger(L, v.x * TT + 8, v.y * TT + 8)) continue;
        vues.set(cle(v), n + 1); file.push(v);
      }
    }
    return mieux;
  }

  /** Marcher jusqu'à la tuile `vers`, au pas, en se cachant. Rend vrai une fois arrivé (ou `fini()`). */
  function aller(L, o, vers, max, fini) {
    const B = L.B, j = B.joueur;
    let ch = chemin(L, tuileDe(j), vers), i = 0, attente = 0, cache = null;
    if (!ch) return 'pas de chemin';
    for (let n = 0; n < (max || 20000); n++) {
      fermer(L);
      if (fini && fini()) return true;
      if (B.transition || B.piratage) { o.frame(1); continue; }
      const ici = tuileDe(j);
      if (cache && (danger(L, j.x, j.y) || exposee(L, cache.x * TT + 8, cache.y * TT + 8) && danger(L, cache.x * TT + 8, cache.y * TT + 8))) {
        // Un garde vient vers la cachette : en chercher une autre, d'ici.
        cache = cachette(L, ici, vers, 16);
        if (cache && cache.x === ici.x && cache.y === ici.y && danger(L, j.x, j.y)) cache = null;
      }
      if (cache) {
        // En route vers la cachette, ou dedans : on en sort quand le chemin d'ici est libre.
        const ch2 = chemin(L, ici, vers);
        if (ch2 && ch2.length && !danger(L, ch2[0].x * TT + 8, ch2[0].y * TT + 8)
            && (ici.x === cache.x && ici.y === cache.y) && !danger(L, ch2[Math.min(2, ch2.length - 1)].x * TT + 8, ch2[Math.min(2, ch2.length - 1)].y * TT + 8)) {
          cache = null; ch = ch2; i = 0; attente = 0; continue;
        }
        if (ici.x !== cache.x || ici.y !== cache.y) {
          const vc = chemin(L, ici, cache);
          const t = vc && vc.length ? vc[0] : cache, dx = t.x * TT + 8 - j.x, dy = t.y * TT + 8 - j.y, d = Math.hypot(dx, dy) || 1;
          j.x += dx / d * Math.min(d, 1.2); j.y += dy / d * Math.min(d, 1.2); j.vx = 0; j.vy = 0;
          L.Entites.regarder(j, dx, dy);
        } else { j.vx = 0; j.vy = 0; }
        o.frame(1); continue;
      }
      for (let k = i; k < Math.min(ch.length, i + 3); k++) if (ch[k].x === ici.x && ch[k].y === ici.y && k > i) { i = k; break; }
      if (i >= ch.length) return true;
      const t = ch[i], cx = t.x * TT + 8, cy = t.y * TT + 8, dx = cx - j.x, dy = cy - j.y, d = Math.hypot(dx, dy);
      if (d < 2.5) { i++; if (i >= ch.length) return true; continue; }
      if (d > 3 * TT) { ch = chemin(L, ici, vers); i = 0; if (!ch) return 'perdu'; continue; }
      if (danger(L, cx, cy)) {
        if (++attente > 180) {
          const c = cachette(L, ici, vers, 16);
          attente = 0;
          if (c && (c.x !== ici.x || c.y !== ici.y)) { cache = c; CACHETTES.push({ de: ici, a: c, t: B.t }); continue; }
        }
        if (danger(L, j.x, j.y)) {
          // On recule d'un pas vers la tuile d'avant ; au début du chemin, on s'éloigne du garde.
          const r = i >= 2 ? ch[i - 2] : null;
          if (r) {
            const rx = r.x * TT + 8 - j.x, ry = r.y * TT + 8 - j.y, rd = Math.hypot(rx, ry);
            if (rd < 2.5) { i--; continue; }
            j.x += rx / rd * Math.min(rd, 1.2); j.y += ry / rd * Math.min(rd, 1.2);
            o.frame(1); continue;
          }
          if (fuir(L, j)) { o.frame(1); continue; }
        }
        j.vx = 0; j.vy = 0; o.frame(1); continue;
      }
      attente = 0;
      const pas = Math.min(d, 1.2);
      j.x += dx / d * pas; j.y += dy / d * pas; j.vx = 0; j.vy = 0;
      L.Entites.regarder(j, dx, dy);
      o.frame(1);
    }
    return 'trop long';
  }

  /** Faire les poches d'un garde, par-derrière, au bouton. On l'attend CACHÉ (`cache`, une tuile hors
      de sa vue — le chemin public, derrière la palissade) ; on sort quand il marche une longue ligne
      droite et nous tourne le dos ; on le rattrape, ACTION ; et au moindre coin, on retourne se cacher. */
  function voler(L, o, slug, cache, max) {
    const B = L.B, j = B.joueur;
    const pas = function (v) {
      const dx = v.x - j.x, dy = v.y - j.y, dd = Math.hypot(dx, dy);
      if (dd < 0.5) return;
      j.x += dx / dd * Math.min(dd, 1.2); j.y += dy / dd * Math.min(dd, 1.2); j.vx = 0; j.vy = 0;
      L.Entites.regarder(j, dx, dy);
    };
    const versLaCache = function () {
      const ch = chemin(L, tuileDe(j), cache);
      if (ch && ch.length) pas({ x: ch[0].x * TT + 8, y: ch[0].y * TT + 8 });
    };
    for (let n = 0; n < (max || 30000); n++) {
      fermer(L);
      const g = garde(L, slug);
      if (!g || !g.porteObjet) return true;
      if (!B.partie.mission) return false;
      const d = Math.hypot(g.x - j.x, g.y - j.y);
      let dos = Math.abs(Math.atan2(j.y - g.y, j.x - g.x) - g.angle) % (2 * Math.PI);
      if (dos > Math.PI) dos = 2 * Math.PI - dos;
      if (d < 17 && dos > 2.4 && g.pauseT === 0) { L.Entites.regarder(j, g.x - j.x, g.y - j.y); o.tape('KeyE', 1); continue; }
      const pt = g.ronde[(g.rondeI || 0) % g.ronde.length];
      const loinDuCoin = Math.hypot(pt[0] * TT + 8 - g.x, pt[1] * TT + 8 - g.y);
      // Assez de ligne droite devant lui pour qu'on le rattrape avant qu'il se retourne.
      const bon = g.pauseT === 0 && loinDuCoin > (d / (1.2 - 0.45)) * 0.45 + 3 * TT && !danger(L, j.x, j.y, g);
      if (!bon) { versLaCache(); o.frame(1); continue; }
      const bx = g.x - Math.cos(g.angle) * 12, by = g.y - Math.sin(g.angle) * 12;
      const ch = d > 2 * TT ? chemin(L, tuileDe(j), tuileDe({ x: bx, y: by })) : null;
      const cible = ch && ch.length ? { x: ch[0].x * TT + 8, y: ch[0].y * TT + 8 } : { x: bx, y: by };
      const dx = cible.x - j.x, dy = cible.y - j.y, dd = Math.hypot(dx, dy) || 1;
      if (danger(L, j.x + dx / dd * 1.2, j.y + dy / dd * 1.2, g)) { versLaCache(); o.frame(1); continue; }
      pas(cible);
      o.frame(1);
    }
    return false;
  }

  /** Par le trou de la palissade : le long du dehors, au nord, loin du garde de la grille. */
  function parLeTrou(L, o) {
    for (const t of [{ x: 66, y: 3 }, { x: 20, y: 3 }]) { const r = aller(L, o, t, 8000); if (r !== true) return r; }
    return true;
  }

  /** Jusqu'au trou, dehors (le chemin public), et attendre que le garde du jardin soit de l'autre côté
      de la maison — au nord-est, qui descend — pour entrer. C'est ce que fait un joueur : regarder,
      puis y aller. */
  function entrerParLeTrou(L, o) {
    const r = parLeTrou(L, o);
    if (r !== true) return r;
    const pret = attendre(L, o, function () { const g = garde(L, 'jardin'); return g.x > 44 * TT && g.y < 12 * TT && g.y > 6 * TT; }, 12000);
    if (!pret) return 'le garde ne passe jamais';
    return aller(L, o, { x: 20, y: 5 }, 8000);
  }

  /** Ressortir par le trou, et revenir au chemin — jusqu'à `fini()`. */
  function ressortir(L, o, fini) {
    for (const t of [{ x: 20, y: 5 }, { x: 20, y: 3 }, { x: 66, y: 3 }, { x: 66, y: 21 }]) {
      const r = aller(L, o, t, 40000, fini);
      if (r !== true) return r;
      if (fini()) return true;
    }
    return fini() ? true : 'pas fini';
  }

  /** Un lieu de la villa, en tuiles (`villa.LIEUX`). */
  function lieu(L, slug) { const l = LIEUX_VILLA[slug]; return { x: l.x, y: l.y }; }
  /** La serrure d'un lieu de la villa : la tuile de sa porte (`villa.SERRURES`). */
  function serrure(L, slug) { return SERRURES_VILLA.find(function (s) { return s.slug === slug; }); }

  function etat(L) {
    const B = L.B;
    return { etape: etape(L), mission: B.partie.mission ? B.partie.mission.slug : null, etoiles: B.recherche.etoiles,
             bloc: B.bloc ? B.bloc.slug : null, objets: Object.assign({}, B.partie.objets),
             faites: Object.keys(B.partie.missionsFaites || {}).filter(function (s) { return s[0] === 'v'; }),
             j: tuileDe(B.joueur) };
  }
"""

PILOTE = """
    function piloter(L, o) {
        const TOUCHE = { haut: 'KeyW', bas: 'KeyS', gauche: 'KeyA', droite: 'KeyD' };
        const C = L.Circuit;
        let tenue = null;
        const tenir = function (t) { if (tenue !== t) { if (tenue) o.relacher(tenue); if (t) o.touche(t); tenue = t; } };
        const p = L.B.piratage.circuit.plan;
        for (let i = 1; i < p.solution.length && L.B.piratage; i++) {
            const cx = (p.solution[i].c + 0.5) * C.CASE, cy = (p.solution[i].r + 0.5) * C.CASE;
            for (let k = 0; k < 60 && L.B.piratage; k++) {
                const e = L.B.piratage.circuit, dx = cx - e.x, dy = cy - e.y;
                if (Math.abs(dx) < C.VITESSE / 2 + 0.05 && Math.abs(dy) < C.VITESSE / 2 + 0.05) break;
                tenir(Math.abs(dx) >= C.VITESSE / 2 + 0.05 ? (dx > 0 ? TOUCHE.droite : TOUCHE.gauche) : (dy > 0 ? TOUCHE.bas : TOUCHE.haut));
                o.frame(1);
            }
        }
        for (let k = 0; k < 40 && L.B.piratage; k++) { tenir(TOUCHE.droite); o.frame(1); }
        tenir(null);
    }
"""


def test_la_villa_a_ses_gardes_et_ils_font_leur_ronde(banc):
    """En entrant, la relève : chaque garde de la fiche au début de sa ronde, un vigile (`garde`, son cône
    à lui) ; et ils marchent — le garde du jardin a quitté son premier point, celui du hall tient son
    poste. Une deuxième visite ne les double pas."""
    from app.blocs import villa
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); nuit(L);
        const entre = await entrerALaVilla(L, o);
        const B = L.B, j = B.joueur;
        const au = function () { return L.Infiltration.gardes().map(function (g) { return { slug: g.gardeSlug, x: g.x, y: g.y,
                                  genre: g.genreVision, agent: !!g.agent }; }); };
        const depart = au();
        j.x = 66 * TT + 8; j.y = 21 * TT + 8; L.Entites.indexer();     // sur le chemin : public, et loin d'eux
        for (let k = 0; k < 900; k++) { o.frame(1); fermer(L); }
        const apres = au();
        const sorti = sortirDeLaVilla(L, o);
        const rentre = await entrerALaVilla(L, o);
        return { entre: entre, sorti: sorti, rentre: rentre, depart: depart, apres: apres, n2: L.Infiltration.gardes().length,
                 etoiles: B.recherche.etoiles };
    }""")
    assert r["entre"] and r["sorti"] and r["rentre"], r
    assert [g["slug"] for g in r["depart"]] == [g["slug"] for g in villa.GARDES]
    assert all(g["genre"] == "garde" and g["agent"] for g in r["depart"])
    for g in villa.GARDES:
        p = g["ronde"][0]
        d = next(q for q in r["depart"] if q["slug"] == g["slug"])
        assert (int(d["x"] // 16), int(d["y"] // 16)) == (p[0], p[1]), f"{g['slug']} ne naît pas au début de sa ronde"
    avant = {g["slug"]: g for g in r["depart"]}
    bouge = {g["slug"]: abs(g["x"] - avant[g["slug"]]["x"]) + abs(g["y"] - avant[g["slug"]]["y"]) for g in r["apres"]}
    assert bouge["jardin"] > 100, f"le garde du jardin ne fait pas sa ronde : {bouge}"
    assert bouge["hall"] < 20, f"le garde du hall quitte son poste : {bouge}"
    assert r["n2"] == len(villa.GARDES), "une deuxième visite double les gardes"
    assert r["etoiles"] == 0, "personne ne devait nous voir sur le chemin"


def test_un_garde_qui_te_voit_hesite_puis_donne_l_alerte(banc):
    """Planté dans le cône d'un garde, sur le terrain privé : d'abord le « ? » — il s'arrête et regarde
    (`soupcon`), sans étoile ; puis l'alerte, une étoile et il court. Dans son DOS, rien, jamais ; et sur
    le chemin public, devant la grille, rien non plus."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); nuit(L);
        await entrerALaVilla(L, o);
        const B = L.B, j = B.joueur, g = garde(L, 'corridor');
        // Dans son dos : 3 tuiles derrière lui, dans le corridor du rez-de-chaussée.
        const dans = function (dx) { g.ronde = [[Math.floor(g.x / TT), Math.floor(g.y / TT), 0]]; g.pauseS = 99; g.pauseT = 0;
                                     j.x = g.x + dx; j.y = g.y; L.Entites.indexer(); };
        L.Entites.regarder(g, 1, 0); dans(-3 * TT);
        let dos = 0; for (let k = 0; k < 300; k++) { o.frame(1); fermer(L); L.Entites.regarder(g, 1, 0); if (B.recherche.etoiles > 0) dos++; }
        // Devant lui, à 4 tuiles.
        dans(4 * TT);
        const suite = [];
        for (let k = 0; k < 200 && B.recherche.etoiles === 0; k++) { o.frame(1); fermer(L); suite.push(g.soupcon > 0 ? 1 : 0); }
        const soupconAvant = suite.indexOf(1), alerte = suite.length;
        return { dos: dos, soupconAvant: soupconAvant, alerte: alerte, etoiles: B.recherche.etoiles, etat: g.etat };
    }""")
    assert r["dos"] == 0, "un garde voit dans son dos"
    assert r["soupconAvant"] >= 0 and r["soupconAvant"] < r["alerte"] - 10, f"pas de « ? » avant l'alerte : {r}"
    assert r["etoiles"] >= 1 and r["etat"] == "poursuit", f"le garde n'a pas donné l'alerte : {r}"


def test_on_n_est_jamais_vu_en_arrivant_par_un_escalier(banc):
    """On monte à l'aveugle : l'étage d'en haut ne se voit pas d'en bas (les cadres de la caméra). Arriver
    en haut d'un escalier doit donc être un REFUGE — on y regarde où sont les gardes avant de bouger.
    Le garde de l'étage descendait le couloir au tapis jusqu'à deux tuiles de l'arrivée, en la regardant :
    un quart de sa ronde, on débouchait dans sa lampe, et l'alerte partait 25 images après le fondu (la
    partie de Martin, v02 ratée deux fois, jour 552). Planté à chaque arrivée, deux rondes complètes de
    chaque garde : personne ne le soupçonne même."""
    from app.blocs import villa
    arrivees = [b["arrivee"] for e in villa.ESCALIERS for b in (e["a"], e["b"])]
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); nuit(L);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        await entrerALaVilla(L, o);
        const vus = [];
        for (const a of """ + json.dumps(arrivees) + """) {
          B.recherche.etoiles = 0; B.recherche.vu = 0;
          L.Infiltration.releve();
          j.x = a[0] * TT + 8; j.y = a[1] * TT + 8; j.vx = 0; j.vy = 0; L.Entites.indexer();
          for (let k = 0; k < 12000; k++) {
            o.frame(1); fermer(L);
            const g = L.Infiltration.gardes().find(function (q) { return q.soupcon > 0 || q.etat === 'poursuit'; });
            if (g || B.recherche.etoiles) {
              vus.push({ arrivee: a, garde: g ? g.gardeSlug : null, image: k, a: tuileDe(g || j) });
              break;
            }
          }
        }
        return vus;
    }""")
    assert r == [], f"un garde voit l'arrivée d'un escalier : {r}"


def test_la_palissade_est_barbelee_et_n_a_que_deux_entrees():
    """Martin (30 sept. 2026) : « la villa devrait avoir des clôtures barbelées ». Tout le tour du terrain privé
    est de la palissade barbelée (`'`, solidité 5 : elle ne s'enjambe plus), sauf deux passages — le trou où
    manque une planche, au nord, et la grille, qui a son garde."""
    from app import carte
    x0, y0, larg, haut = villa.PRIVE[0]
    tour = {(x, y0) for x in range(x0, x0 + larg)} | {(x, y0 + haut - 1) for x in range(x0, x0 + larg)}
    tour |= {(x0, y) for y in range(y0, y0 + haut)} | {(x0 + larg - 1, y) for y in range(y0, y0 + haut)}
    ouvertes = {(x, y) for x, y in tour if carte.LEGENDE[villa.PLAN[y][x]].get("solide", 0) == 0}
    assert ouvertes == {(20, 4), (59, 20), (59, 21), (59, 22), (59, 23)}, sorted(ouvertes)
    fermees = {villa.PLAN[y][x] for x, y in tour - ouvertes}
    assert fermees == {"'"}, f"le tour n'est pas tout en palissade barbelée : {fermees}"
    assert carte.LEGENDE["'"]["solide"] == 5 and "'" not in carte.ENJAMBABLES


def test_une_haie_de_cedres_cache_et_ne_se_traverse_pas(banc):
    """Les cachettes du jardin (Martin, 30 sept. 2026 : « vois si des endroits pour se cacher sont requis » —
    dehors, rien ne coupait la vue d'un garde). Une haie coupe la vue comme un mur (`Monde.ligneLibre`), et on
    ne passe pas au travers. La poche du trou : deux bouts de haie de chaque côté de (20, 5)."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); nuit(L);
        await entrerALaVilla(L, o);
        const M = L.Monde, c = function (t) { return t * TT + 8; };
        return { aTravers: M.ligneLibre(c(16), c(5), c(20), c(5)), aCote: M.ligneLibre(c(16), c(6), c(20), c(6)),
                 bloque: M.bloque(18, 5, M.MASQUE_PIETON) };
    }""")
    assert r["aTravers"] is False, "la haie ne cache pas"
    assert r["aCote"] is True, "le juge ne mord pas : la vue est coupée même sans haie"
    assert r["bloque"], "on traverse la haie"


def test_la_nuit_tient_dans_la_villa(banc):
    """Martin (30 sept. 2026) : dix-sept gardes, et une infiltration prudente durait plus qu'une nuit — l'aube
    tombait en pleine mission (de jour, un garde voit plus loin). Dans la villa, de nuit, l'heure ne bouge
    plus ; de jour, elle avance ; et dehors, la nuit repart."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); nuit(L);
        const B = L.B;
        await entrerALaVilla(L, o);
        B.joueur.x = 66 * TT + 8; B.joueur.y = 21 * TT + 8; L.Entites.indexer();   // sur le chemin, loin des gardes
        const h0 = B.partie.heure;
        for (let k = 0; k < 1200; k++) { o.frame(1); fermer(L); }
        const nuitDedans = B.partie.heure - h0;
        B.partie.heure = 13 / 24;
        for (let k = 0; k < 1200; k++) { o.frame(1); fermer(L); }
        const jourDedans = B.partie.heure - 13 / 24;
        B.partie.heure = 22 / 24;   // pas 23 h : une heure plus tard, on passerait minuit
        const sorti = sortirDeLaVilla(L, o);
        const h1 = B.partie.heure;
        for (let k = 0; k < 1200; k++) { o.frame(1); fermer(L); }
        return { nuitDedans: nuitDedans, jourDedans: jourDedans, sorti: sorti, nuitDehors: B.partie.heure - h1 };
    }""")
    assert r["nuitDedans"] == 0, f"la nuit ne tient pas dans la villa : {r}"
    assert r["jourDedans"] > 0, f"le jour s'arrête aussi dans la villa : {r}"
    assert r["sorti"] and r["nuitDehors"] > 0, f"dehors, la nuit ne repart pas : {r}"


def test_la_porte_de_service_ne_s_ouvre_qu_avec_la_cle(banc):
    """La serrure du bloc (`carte.BARRIERES`, condition `objet`) : sans la clé, on s'y bute et on lit
    pourquoi ; la clé dans le sac, on passe. Au clavier, en poussant."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.B.partie.heure = 13 / 24;
        await entrerALaVilla(L, o);
        const B = L.B, j = B.joueur;
        L.Infiltration.gardes().forEach(function (g) { L.Entites.retirer(g); });   // on juge la porte, pas les gardes
        const pousser = function () {
          j.x = 20 * TT + 8; j.y = 36 * TT + 8; L.Entites.indexer(); B.msg = null;
          o.touche('KeyW'); for (let k = 0; k < 90; k++) o.frame(1); o.relacher('KeyW'); o.frame(1);
          return { y: Math.floor(j.y / TT), msg: B.msg ? B.msg.texte || B.msg : null };
        };
        const sans = pousser();
        B.partie.objets.cle_villa = 1;
        const avec = pousser();
        return { sans: sans, avec: avec };
    }""")
    assert r["sans"]["y"] >= 35, f"sans la clé, on est entré : {r}"
    assert "CLÉ" in str(r["sans"]["msg"]), f"la porte ne dit pas pourquoi : {r}"
    assert r["avec"]["y"] <= 33, f"avec la clé, la porte reste fermée : {r}"


def test_l_escalier_mene_a_l_etage_et_la_camera_reste_dans_son_cadre(banc):
    """Poser le pied sur le grand escalier du hall : au noir, on est à l'étage ; la caméra ne sort
    jamais du cadre de l'étage (on ne voit pas le terrain), et redescendre ramène au hall."""
    from app.blocs import villa
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.B.partie.heure = 13 / 24;
        await entrerALaVilla(L, o);
        const B = L.B, j = B.joueur;
        L.Infiltration.gardes().forEach(function (g) { L.Entites.retirer(g); });
        j.x = 41 * TT + 8; j.y = 13 * TT + 8; L.Entites.indexer();
        o.touche('KeyW'); for (let k = 0; k < 60 && !B.transition; k++) o.frame(1); o.relacher('KeyW');
        for (let k = 0; k < 120 && B.transition; k++) o.frame(1);
        for (let k = 0; k < 60; k++) o.frame(1);
        const haut = { j: tuileDe(j), cam: { x: B.cam.x, y: B.cam.y } };
        // Au coin nord-est de l'étage : sans son cadre, la caméra montrerait la cave (à l'est) et le
        // terrain (au nord).
        j.x = 34 * TT + 8; j.y = 48 * TT + 8; L.Entites.indexer();
        for (let k = 0; k < 90; k++) o.frame(1);
        haut.coin = { x: B.cam.x, y: B.cam.y };
        j.x = 18 * TT + 8; j.y = 66 * TT + 8; L.Entites.indexer();
        j.x = 17 * TT + 8; j.y = 66 * TT + 8; L.Entites.indexer();
        o.touche('KeyS'); for (let k = 0; k < 60 && !B.transition; k++) o.frame(1); o.relacher('KeyS');
        for (let k = 0; k < 120 && B.transition; k++) o.frame(1);
        return { haut: haut, bas: tuileDe(j) };
    }""")
    ex, ey = villa.ESCALIERS[0]["b"]["arrivee"]
    assert r["haut"]["j"] == {"x": ex, "y": ey}, r
    cx, cy, cl, ch = villa.CADRES[1]
    cam = r["haut"]["cam"]
    assert cx * 16 <= cam["x"] <= (cx + cl) * 16 - 480 and cy * 16 <= cam["y"] <= (cy + ch) * 16 - 270, \
        f"la caméra de l'étage sort de son cadre : {cam}"
    coin = r["haut"]["coin"]
    assert coin["x"] <= (cx + cl) * 16 - 480 and coin["y"] >= cy * 16, f"au coin de l'étage, la caméra en sort : {coin}"
    bx, by = villa.ESCALIERS[0]["a"]["arrivee"]
    assert r["bas"] == {"x": bx, "y": by}, r


def test_le_gps_vise_le_passage_en_ville_et_le_garde_dans_la_villa(banc):
    """`obtenir` + `garde` (v01) : en ville, la flèche vise le passage de la villa (le lieu n'a pas de
    pixel en ville) ; dans la villa, le garde qui a la clé."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); nuit(L);
        // L'acte 1, sans laisser jouer son marqueur (son saut nous mettrait dans la villa) : l'étape du vol, en ville.
        L.Histoire.commencer('nuit_a_la_villa'); L.B.cinema = null; L.B.scene = null;
        L.B.partie.mission.etape = 2;
        const p = L.B.defs.blocs.find(function (b) { return b.slug === 'villa'; }).passage;
        const enVille = L.Histoire.cible();
        await entrerALaVilla(L, o);
        L.B.partie.mission.etape = 2;
        o.frame(2); fermer(L);
        const g = garde(L, 'jardin'), dedans = L.Histoire.cible();
        return { enVille: enVille, passage: { x: 16, y: (p.de + p.l / 2) * 16 }, dedans: dedans, g: { x: g.x, y: g.y }, porte: g.porteObjet };
    }""")
    v = r["enVille"]
    assert v and abs(v["x"] - r["passage"]["x"]) <= 16 and abs(v["y"] - r["passage"]["y"]) <= 16, r
    assert r["porte"] == "cle_villa", "le garde du jardin n'a pas la clé pendant l'acte 1 (v01)"
    assert abs(r["dedans"]["x"] - r["g"]["x"]) < 2 and abs(r["dedans"]["y"] - r["g"]["y"]) < 2, r


def test_acte_1_on_vole_la_cle_du_garde_du_jardin_sans_se_faire_voir(banc):
    """L'acte 1 (v01), joué : le saut de son marqueur, de nuit, au chemin ; par le trou de la palissade ; dans le dos
    du garde du jardin, ACTION — la clé ; ressortir par le chemin. Aucune étoile, la clé reste dans le sac, l'acte paie
    sa prime (500 $), v01 est faite — et l'acte 2 s'ouvre au chemin, dans la même nuit : Bouchard."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); nuit(L);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        const avant = B.partie.argent, heure = B.partie.heure;
        const t = { entre: await aLActe(L, o, 2) };
        t.apresEntree = etat(L);
        t.trou = parLeTrou(L, o);
        t.vol = voler(L, o, 'jardin', { x: 20, y: 3 });
        t.apresVol = etat(L);
        t.sortie = ressortir(L, o, function () { return etape(L) >= 4; });
        t.argent = B.partie.argent - avant;
        await jusqua(L, o, 6);
        t.fin = etat(L);
        t.nuit = L.Monde.estNuit(B.partie.heure);
        t.donneur = L.Chapitres.donneurDe(L.Histoire.courante());
        return t;
    }""")
    assert r["entre"], r
    assert r["apresEntree"]["etape"] == 2 and r["apresEntree"]["bloc"] == "villa", \
        f"le saut de l'acte 1 pose au chemin, de nuit, et l'« aller » se fait en arrivant : {r['apresEntree']}"
    assert r["trou"] is True, r
    assert r["vol"] is True and r["apresVol"]["objets"].get("cle_villa") == 1, r
    assert r["apresVol"]["etoiles"] == 0 and r["apresVol"]["etape"] == 3, r
    assert r["sortie"] is True and "v01" in r["fin"]["faites"], (r["apresVol"], r["fin"])
    assert r["fin"]["objets"].get("cle_villa") == 1, "la clé ne reste pas dans le sac"
    assert r["argent"] == 500, r
    assert r["fin"]["mission"] == "nuit_a_la_villa" and r["fin"]["etape"] == 6 and r["fin"]["bloc"] == "villa", \
        f"l'acte 2 s'ouvre dans la villa : {r['fin']}"
    assert r["nuit"] and r["donneur"] == "bouchard", r


def test_acte_2_le_dossier_du_bureau_d_en_haut(banc):
    """L'acte 2 (v02), joué là où une vieille partie le reprend (v01 faite, la clé au sac) : le saut au chemin ; la clé
    ouvre la porte de service ; la cuisine, le corridor, le hall, le grand escalier ; à l'étage, le bureau du maire et
    son dossier (ramassé en marchant dessus) ; redescendre et ressortir sans une étoile. L'acte paie sa prime (700 $)
    et efface deux pages du casier, et l'acte 3 s'ouvre au chemin : Sven."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); nuit(L);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        B.partie.missionsFaites.v01 = 1; B.partie.objets.cle_villa = 1; B.partie.casier = 5;
        const avant = B.partie.argent;
        const t = { entre: await aLActe(L, o, 6) };
        t.debut = etat(L);
        t.trou = entrerParLeTrou(L, o);
        t.service = aller(L, o, { x: 20, y: 32 }, 20000, function () { return etape(L) >= 7; });
        t.apresService = etat(L);
        t.dossier = aller(L, o, lieu(L, 'villa_bureau'), 60000, function () { return etape(L) >= 8; });
        t.apresDossier = etat(L);
        t.sortie = ressortir(L, o, function () { return etape(L) >= 9; });
        await jusqua(L, o, 11);
        t.fin = etat(L);
        t.casier = B.partie.casier;
        t.argent = B.partie.argent - avant;
        t.donneur = L.Chapitres.donneurDe(L.Histoire.courante());
        return t;
    }""")
    assert r["entre"] and r["debut"]["etape"] == 6, r["debut"]
    assert r["trou"] is True, r
    assert r["service"] is True and r["apresService"]["etape"] == 7 and r["apresService"]["etoiles"] == 0, r
    assert r["dossier"] is True and r["apresDossier"]["objets"].get("dossier_bouchard") == 1, r
    assert r["apresDossier"]["etoiles"] == 0, r
    assert r["sortie"] is True and "v02" in r["fin"]["faites"], r
    assert r["casier"] == 3 and r["argent"] == 700, r
    assert r["fin"]["etape"] == 11 and r["fin"]["bloc"] == "villa" and r["donneur"] == "sven", r["fin"]


def test_acte_3_la_chambre_forte_au_piratage(banc):
    """L'acte 3 (v03), le dernier, joué là où une vieille partie le reprend : la cave par l'escalier de la cuisine ; le
    terminal, piraté au clavier — le code dans le sac, la porte de la chambre forte s'ouvre ; le grand livre ;
    ressortir sans une étoile, puis le rapporter à Sven : le chapitre est fait."""
    r = banc("async function (L, o) {" + OUTILS + PILOTE + """
        L.Jeu.commencer(); nuit(L);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        B.partie.missionsFaites.v01 = 1; B.partie.missionsFaites.v02 = 1; B.partie.objets.cle_villa = 1;
        const t = { entre: await aLActe(L, o, 11) };
        const porte = serrure(L, 'villa_voute');
        t.fermeeAvant = !!L.Monde.barriereA(porte.x, porte.y, 'pieton');
        t.trou = entrerParLeTrou(L, o);
        t.terminal = aller(L, o, lieu(L, 'villa_terminal'), 60000);
        // Pirater quand personne ne regarde.
        for (let k = 0; k < 3000 && danger(L, j.x, j.y); k++) { o.frame(1); fermer(L); }
        o.tape('KeyE', 2);
        t.ouvert = !!B.piratage;
        if (B.piratage) piloter(L, o);
        fermer(L); o.frame(1); fermer(L);
        t.apresPiratage = etat(L);
        t.fermeeApres = !!L.Monde.barriereA(porte.x, porte.y, 'pieton');
        t.livre = aller(L, o, lieu(L, 'villa_voute'), 20000, function () { return etape(L) >= 13; });
        t.apresLivre = etat(L);
        t.sortie = ressortir(L, o, function () { return etape(L) >= 14; });
        t.dehors = sortirDeLaVilla(L, o);
        const sven = L.Histoire.donneur('sven');
        if (sven) { j.x = sven.x + 14; j.y = sven.y; L.Entites.indexer(); }
        for (let k = 0; k < 300 && B.partie.mission; k++) { o.frame(1); fermer(L); }
        t.fin = etat(L);
        return t;
    }""")
    assert r["entre"] and r["trou"] is True, r
    assert r["fermeeAvant"], "la chambre forte est ouverte avant le piratage"
    assert r["terminal"] is True and r["ouvert"], f"le piratage ne s'ouvre pas au terminal : {r}"
    assert r["apresPiratage"]["objets"].get("code_voute") == 1 and r["apresPiratage"]["etape"] == 12, r
    assert not r["fermeeApres"], "le code est dans le sac et la chambre forte reste fermée"
    assert r["livre"] is True and r["apresLivre"]["objets"].get("grand_livre") == 1, r
    assert r["apresLivre"]["etoiles"] == 0, r
    assert r["sortie"] is True and r["dehors"], r
    assert "v03" in r["fin"]["faites"] and r["fin"]["mission"] is None, r


def test_un_acte_rate_fait_retomber_ce_qu_il_avait_fait_prendre_puis_on_le_reprend(banc):
    """Vu avec le dossier en poche : l'acte 2 (v02) est raté (`etoile`), le dossier retombe — la clé, venue de l'acte 1,
    reste ; c'est l'échec de Bouchard qu'on entend. Puis le menu : REPRENDRE L'ACTE 2 — le saut ramène au chemin de
    la villa, de nuit, à la porte de service à ouvrir de nouveau, la clé toujours en poche."""
    from outils_missions import PLUS_LONGUES
    r = banc("async function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); nuit(L);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        B.partie.missionsFaites.v01 = 1; B.partie.objets.cle_villa = 1;
        await aLActe(L, o, 6);
        B.partie.mission.etape = 8; B.partie.objets.dossier_bouchard = 1;
        L.Police.etoilesAuMoins(1);
        for (let k = 0; k < 120 && B.partie.mission; k++) { o.frame(1); ecouter(L); }
        const rate = { mission: B.partie.mission, objets: Object.assign({}, B.partie.objets) };
        for (let k = 0; k < 2400 && (B.transition || B.cinema || !B.menu); k++) { o.frame(1); await o.attendre(); ecouter(L); }
        const menu = B.menu ? B.menu.items.map(function (i) { return i.libelle; }) : null;
        const item = B.menu.items.find(function (x) { return x.libelle.indexOf('REPRENDRE') === 0; });
        if (item.faire(item) !== false && B.menu) L.Hud.fermerMenu();
        for (let k = 0; k < 2400 && (B.transition || etape(L) === null || etape(L) < 6); k++) { o.frame(1); await o.attendre(); ecouter(L); }
        fermer(L);
        return { rate: rate, menu: menu, echec: dites.filter(function (d) { return d.indexOf('echec:') === 0; }),
                 repris: Object.assign(etat(L), { nuit: L.Monde.estNuit(B.partie.heure), gardee: !!B.partie.mission.gardee }) };
    }""")
    assert r["rate"]["mission"] is None, "vu, et l'infiltration continue"
    assert "dossier_bouchard" not in r["rate"]["objets"] and r["rate"]["objets"].get("cle_villa") == 1, r["rate"]
    assert r["echec"] == ["echec:bouchard:4"], f"l'échec de Bouchard, pas celui de Josée : {r['echec']}"
    assert r["menu"][:2] == ["REPRENDRE L'ACTE 2", "PLUS TARD"], r["menu"]
    rp = r["repris"]
    assert rp["mission"] == "nuit_a_la_villa" and rp["etape"] == 6 and rp["bloc"] == "villa", rp
    assert rp["nuit"] and rp["gardee"] and rp["etoiles"] == 0 and rp["objets"].get("cle_villa") == 1, rp


def test_la_carte_ne_montre_que_l_etage_ou_l_on_est(banc):
    """Martin (30 sept. 2026) : « je ne veux pas voir tous les étages d'un coup ». La grande carte (N) et
    la mini-carte ne montrent que le CADRE du joueur — le rez-de-chaussée, l'étage, la cave, le 2e étage ou le
    sous-sol — avec les
    lieux de cet étage-là seulement, et le titre le nomme. Ni le train ni rien de la ville par-dessus."""
    from app.blocs import villa
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.B.partie.heure = 13 / 24;
        await entrerALaVilla(L, o);
        const B = L.B, j = B.joueur;
        L.Infiltration.gardes().forEach(function (g) { L.Entites.retirer(g); });
        let trainSurLaCarte = 0;
        const train = L.Train.dessinerSurLaCarte;
        L.Train.dessinerSurLaCarte = function () { trainSurLaCarte++; return train.apply(this, arguments); };
        const regarder = function (x, y) {
          j.x = x * TT + 8; j.y = y * TT + 8; L.Entites.indexer(); L.Monde.centrerCamera(j.x, j.y);
          o.frame(2); fermer(L);
          const mini = JSON.parse(JSON.stringify(L.Hud.marqueurs().mini));
          o.tape('KeyN'); o.frame(2);
          const carte = JSON.parse(JSON.stringify(L.Hud.marqueurs().carte || null));
          const ouverte = B.etat === 'carte';
          o.tape('KeyN'); o.frame(2); fermer(L);
          return { mini: mini, carte: carte, ouverte: ouverte };
        };
        const out = { rez: regarder(66, 21), etage: regarder(18, 66), cave: regarder(40, 67),
                      second: regarder(3, 90), sousSol: regarder(39, 74) };
        out.train = trainSurLaCarte;
        return out;
    }""")
    attendus = {"rez": (0, ["villa_chemin", "villa_service"]), "etage": (1, []), "cave": (2, []),
                "second": (3, ["villa_bureau"]), "sousSol": (4, ["villa_terminal", "villa_voute"])}
    for nom, (i, lieux) in attendus.items():
        v = r[nom]
        cx, cy, cl, ch = villa.CADRES[i]
        assert v["ouverte"], f"{nom} : la carte ne s'ouvre pas"
        assert v["carte"]["partie"] == [cx, cy, cl, ch], f"{nom} : la carte montre {v['carte']['partie']}, pas l'étage"
        assert v["carte"]["etage"] == villa.NOMS_DES_CADRES[i], v["carte"]
        assert sorted(v["carte"]["lieux"]) == lieux, f"{nom} : des lieux d'un autre étage sur la carte : {v['carte']['lieux']}"
        sx, sy, sl, sh = v["mini"]["source"]
        assert cx <= sx and sx + sl <= cx + cl and cy <= sy and sy + sh <= cy + ch, \
            f"{nom} : la mini-carte déborde de l'étage : {v['mini']}"
    assert r["train"] == 0, "le train de la ville se dessine sur la carte de la villa"


def test_un_objectif_a_un_autre_etage_se_vise_par_son_escalier(banc):
    """Le GPS dans la villa : ce qui est à un autre étage se vise par l'escalier à prendre DANS l'étage
    où l'on est — sinon la flèche pointait à travers les murs, vers un étage qu'on ne voit pas. Au même
    étage, l'objectif lui-même. De la cave à l'étage, on repasse par le rez-de-chaussée."""
    from app.blocs import villa
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); nuit(L);
        const B = L.B, j = B.joueur;
        B.partie.missionsFaites.v01 = 1; B.partie.objets.cle_villa = 1;
        await entrerALaVilla(L, o);
        L.Infiltration.gardes().forEach(function (g) { L.Entites.retirer(g); });
        L.Histoire.commencer('nuit_a_la_villa'); B.cinema = null; B.scene = null;   // l'acte 2, sans son saut
        const vise = function (etape, x, y) {
          B.partie.mission.etape = etape;
          j.x = x * TT + 8; j.y = y * TT + 8; L.Entites.indexer();
          const c = L.Histoire.cible();
          return c ? { x: Math.floor(c.x / TT), y: Math.floor(c.y / TT), nom: c.nom } : null;
        };
        const out = {};
        out.dossierDuRez = vise(7, 42, 17);        // le dossier est à l'étage : le grand escalier du hall
        out.dossierDeLEtage = vise(7, 18, 60);     // à l'étage : l'escalier de la bibliothèque, qui monte au 2e
        out.dossierDuSecond = vise(7, 3, 90);      // au 2e : le bureau
        out.dossierDeLaCave = vise(7, 45, 64);     // de la cave : remonter à la cuisine d'abord
        out.sortieDeLEtage = vise(8, 30, 52);      // ressortir : redescendre
        out.sortieDuSecond = vise(8, 20, 80);      // du 2e : redescendre à l'étage
        return out;
    }""")
    hall, etage = villa.ESCALIERS[0]["a"], villa.ESCALIERS[0]["b"]
    cave = villa.ESCALIERS[1]["b"]
    bibliotheque, palier = villa.ESCALIERS[2]["a"], villa.ESCALIERS[2]["b"]
    assert (r["dossierDuRez"]["x"], r["dossierDuRez"]["y"]) in {tuple(t) for t in hall["tuiles"]}, r
    assert "ÉTAGE" in r["dossierDuRez"]["nom"], r
    bx, by = villa.LIEUX["villa_bureau"]["x"], villa.LIEUX["villa_bureau"]["y"]
    assert (r["dossierDeLEtage"]["x"], r["dossierDeLEtage"]["y"]) in {tuple(t) for t in bibliotheque["tuiles"]}, r
    assert "2E ÉTAGE" in r["dossierDeLEtage"]["nom"], r
    assert (r["dossierDuSecond"]["x"], r["dossierDuSecond"]["y"]) == (bx, by), r
    assert (r["sortieDuSecond"]["x"], r["sortieDuSecond"]["y"]) in {tuple(t) for t in palier["tuiles"]}, r
    assert (r["dossierDeLaCave"]["x"], r["dossierDeLaCave"]["y"]) in {tuple(t) for t in cave["tuiles"]}, r
    assert (r["sortieDeLEtage"]["x"], r["sortieDeLEtage"]["y"]) in {tuple(t) for t in etage["tuiles"]}, r


def test_rater_une_mission_ne_fait_pas_perdre_la_cle_d_une_autre(banc):
    """Deux missions donnent la clé de la porte de service (v01 au garde du jardin, e07 au chauffeur).
    Rater e07 avec la clé de v01 dans le sac l'effaçait : v02 et v03 ne s'ouvraient plus (la partie de
    Martin, jour 479). Elle reste ; celle qu'on vient de voler pendant la mission ratée, elle, retombe.
    Et une partie qui l'a perdue ainsi la retrouve au chargement."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); nuit(L);
        const B = L.B, out = {};
        // e07 est l'acte 3 des Chevreuils (2 oct. 2026) : e04 et e06 faits, le chapitre part à l'acte 3.
        B.partie.missionsFaites.e04 = 1; B.partie.missionsFaites.e06 = 1; B.partie.missionsFaites.v01 = 1; B.partie.objets.cle_villa = 1;
        commencer(L, o, 'les_chevreuils');
        L.Histoire.echouer('essai'); o.frame(2); fermer(L);
        out.apresE07 = Object.assign({}, B.partie.objets);
        delete B.partie.missionsFaites.v01; delete B.partie.objets.cle_villa;
        // v01 est l'acte 1 de la nuit à la villa (2 oct. 2026) : sans laisser jouer son saut.
        L.Histoire.commencer('nuit_a_la_villa'); B.cinema = null; B.scene = null; B.partie.mission.etape = 2;
        B.partie.objets.cle_villa = 1;                  // volée pendant l'acte
        L.Histoire.echouer('essai'); o.frame(2); fermer(L);
        out.apresV01 = Object.assign({}, B.partie.objets);
        const perdue = { missionsFaites: { v01: 463 }, objets: { skimmer: 0 } };
        out.reparee = L.Sauvegarde.completer(perdue, B.defs).objets;
        out.neuve = L.Sauvegarde.completer({ missionsFaites: {}, objets: {} }, B.defs).objets;
        return out;
    }""")
    assert r["apresE07"].get("cle_villa") == 1, f"rater e07 a fait perdre la clé de v01 : {r}"
    assert "cle_villa" not in r["apresV01"], f"la clé volée pendant une mission ratée reste : {r}"
    assert r["reparee"].get("cle_villa") == 1, f"une partie qui a perdu la clé ne la retrouve pas : {r}"
    assert "cle_villa" not in r["neuve"], r
