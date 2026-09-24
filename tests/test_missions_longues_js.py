"""Sept missions allongées (« Des missions plus longues », Martin, 22 sept. 2026), JOUÉES au banc.

e02, f02, f03, f08, f11, r01 et s01 ont gagné deux étapes chacune — un détour, une poignée de main,
des hommes qui arrivent de loin, un fuyard, une police à semer — et des trajets à l'autre bout de la
ville. Aucune n'avait de juge qui la joue : ici chacune se joue de la première réplique à la prime,
étape par étape, étapes neuves comprises, sur le modèle de `test_cinq_missions_js.py` et
`test_dix_missions_js.py`.

Ce que ces juges font vraiment, et ce qu'ils ne font pas :

- **Les trajets se roulent** (`rouler`) : un chemin par les rues (Dijkstra, la rue d'abord, une
  cour ou un trottoir s'il le faut), le char posé tuile par tuile, une image par tuile, à petite vitesse — c'est
  l'arrivée au lieu qui fait avancer l'objectif, pas un `avancer()` du juge. La guérite de la
  fourrière se force au gaz, pour de vrai (son étoile comprise). Le nombre de tuiles
  est la longueur du trajet ; les secondes qu'on en tire (aux trois quarts de la `vitesse_max` du
  char) sont un plancher, pas un chrono d'humain.
- **Semer** se joue aussi : on laisse les étoiles tomber d'elles-mêmes (`decroitre`, hors de vue),
  la police retirée de la ville à chaque image — jamais `etoiles = 0`.
- **Rattraper un fuyard**, c'est le rejoindre quand il s'arrête (moins de 40 px, moins de 0,6 de
  vitesse — ce que `majObjectif` regarde), puis coucher le porteur et ramasser la caisse.
- **Les bagarres** : les hommes qui ARRIVENT (`loin`) sont mesurés à leur naissance (sur nous, à la
  course), puis couchés par `Entites.assommer`, comme dans les autres juges de mission.
- **Parler** passe par `Histoire.parler`, et la poignée de main dite (`accueil`) doit être la
  réplique de la cible, pas celle d'un autre.
"""

OUTILS = """
  function passer(L, o) {
    let n = 0;
    while ((L.B.scene || L.B.cinema) && n < 6000) { o.frame(1); if (L.B.cinema && n % 30 === 0) L.Histoire.suivante(); n++; }
  }
  function boite(L) {
    const c = L.B.cinema;
    if (!c) return null;
    const l = c.lignes[Math.max(0, c.i)];
    return { partie: c.partie, qui: l.qui, texte: l.texte, slug: l.slug };
  }
  // La réplique qui s'ouvre au changement d'étape (`pendant` : elle part à l'image d'après) :
  // on la lit, puis on la ferme — sinon `B.cinema` fige `majObjectif` en silence.
  function ecouter(L, o) {
    for (let k = 0; k < 3 && !L.B.cinema; k++) o.frame(1);
    const b = boite(L); fermer(L); return b;
  }
  function etape(L) { return L.B.partie.mission ? L.B.partie.mission.etape : null; }
  function fermer(L) { let g = 0; while (L.B.cinema && g < 100) { L.Histoire.suivante(); g++; } }
  function faites(L, slugs) { slugs.forEach(function (s) { L.B.partie.missionsFaites[s] = 1; }); }
  function heure(L, nuit) {
    let h = L.B.partie.heure;
    for (let k = 0; k < 400 && L.Monde.estNuit(h) !== nuit; k++) h = (h + 0.005) % 1;
    L.B.partie.heure = h;
  }
  function paiements(L) {
    const liste = [], vrai = L.Missions.encaisser;
    L.Missions.encaisser = function (montant, raison) { liste.push(montant); return vrai.apply(null, arguments); };
    return liste;
  }
  function hommes(L, etape) {
    const j = L.B.joueur;
    return L.B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible && !e.porteLaCaisse && e.etape === etape; })
      .map(function (e) { return { e: e, d: Math.round(Math.hypot(e.x - j.x, e.y - j.y)), etat: e.etat, arme: e.arme || null, vie: e.vieMax }; });
  }
  function finir(L, o) { for (let k = 0; k < 400 && L.B.partie.mission; k++) { o.frame(1); fermer(L); } passer(L, o); }
  // Poser le joueur à côté de quelqu'un (à pied), comme on s'avance pour lui parler.
  function aCote(L, e) {
    const j = L.B.joueur;
    if (j.dansVehicule) L.Vehicules.descendre(j, true);
    j.x = e.x - 16; j.y = e.y; L.Entites.indexer();
  }
  function monterDans(L, o, v) {
    const j = L.B.joueur;
    j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
    L.Vehicules.monter(j, v); L.Entites.indexer();
    o.frame(2);
  }
  // ⚠️ Le chemin par les RUES : un Dijkstra où la rue (`estRoute`) coûte 1 et le reste de ce
  // qu'un char peut rouler (une cour, un stationnement, un trottoir) coûte 4 — un trajet en ligne
  // droite par les parcs mentirait sur la longueur, et un char qui dort dans une cour doit
  // pouvoir en sortir. Une barrière qu'on FORCE (la guérite de la fourrière) se traverse : c'est
  // `rouler` qui la force pour de vrai, au gaz.
  function chemin(L, x0, y0, x1, y1, r) {
    const M = L.Monde, c = M.carte, TT = L.TT, w = c.w, h = c.h;
    const sx = Math.floor(x0 / TT), sy = Math.floor(y0 / TT), gx = Math.floor(x1 / TT), gy = Math.floor(y1 / TT);
    function cout(tx, ty) {
      if (tx < 1 || ty < 1 || tx >= w - 1 || ty >= h - 1 || M.estEau(tx, ty)) return 0;
      if (M.bloque(tx, ty, M.MASQUE_VEHICULE)) {
        const b = M.barriereA(tx, ty, 'vehicule');
        return b && b.forcer ? 1 : 0;
      }
      return M.estRoute(tx, ty) ? 1 : 4;
    }
    const dist = new Float64Array(w * h).fill(Infinity), prec = new Int32Array(w * h).fill(-1);
    const tas = [];   // un tas binaire de [distance, indice]
    function pousser(d, i) {
      tas.push([d, i]);
      for (let k = tas.length - 1; k > 0;) { const q = (k - 1) >> 1; if (tas[q][0] <= tas[k][0]) break; [tas[q], tas[k]] = [tas[k], tas[q]]; k = q; }
    }
    function tirer() {
      const haut = tas[0], bas = tas.pop();
      if (tas.length) {
        tas[0] = bas;
        for (let k = 0; ;) {
          const a = 2 * k + 1, b = a + 1; let m = k;
          if (a < tas.length && tas[a][0] < tas[m][0]) m = a;
          if (b < tas.length && tas[b][0] < tas[m][0]) m = b;
          if (m === k) break; [tas[m], tas[k]] = [tas[k], tas[m]]; k = m;
        }
      }
      return haut;
    }
    const s = sy * w + sx;
    dist[s] = 0; prec[s] = s; pousser(0, s);
    let fin = -1;
    while (tas.length) {
      const [d, i] = tirer();
      if (d > dist[i]) continue;
      const tx = i % w, ty = (i - tx) / w;
      if (Math.hypot(tx - gx, ty - gy) <= r) { fin = i; break; }
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = tx + dx, ny = ty + dy, n = ny * w + nx, k = cout(nx, ny);
        if (!k || d + k >= dist[n]) continue;
        dist[n] = d + k; prec[n] = i; pousser(d + k, n);
      }
    }
    if (fin < 0) return null;
    const tuiles = [];
    for (let i = fin; ; i = prec[i]) { tuiles.push({ x: (i % w) * TT + 8, y: Math.floor(i / w) * TT + 8, tx: i % w, ty: Math.floor(i / w) }); if (prec[i] === i) break; }
    return tuiles.reverse();
  }
  // Rouler jusqu'à `l` (à `r` tuiles près) dans le char où l'on est : une tuile par image, à
  // petite vitesse (plus vite, un coin de mur éjecte le joueur). S'arrête dès que l'objectif
  // change — c'est l'ARRIVÉE qui le fait avancer. Les répliques qui s'ouvrent en route se passent.
  // Devant une barrière fermée, on met le gaz pour de vrai : `forcerBarriere` la force (ses
  // dégâts, son étoile), comme au volant.
  function rouler(L, o, l, r) {
    const B = L.B, M = L.Monde, j = B.joueur, v = j.dansVehicule, e0 = etape(L);
    const p = chemin(L, v.x, v.y, l.x, l.y, r);
    if (!p) return { tuiles: null, secondes: null, arrive: false, de: [Math.floor(v.x / L.TT), Math.floor(v.y / L.TT)], dans: !!j.dansVehicule };
    const vueEnRoute = [], forcees = [];
    for (let k = 1; k < p.length && etape(L) === e0 && B.partie.mission; k++) {
      const angle = Math.atan2(p[k].y - p[k - 1].y, p[k].x - p[k - 1].x);
      const b = M.barriereA(p[k].tx, p[k].ty, 'vehicule');
      if (b && M.bloque(p[k].tx, p[k].ty, M.MASQUE_VEHICULE)) {
        // Au gaz, droit dessus, jusqu'à ce que le char soit passé (ou qu'il rebondisse).
        v.angle = angle; v.vitesse = 3; v.vx = Math.cos(angle) * 3; v.vy = Math.sin(angle) * 3;
        for (let g = 0; g < 20 && Math.hypot(v.x - p[k].x, v.y - p[k].y) > 6; g++) { v.vitesse = 3; o.frame(1); fermer(L); }
        forcees.push({ slug: b.slug, passe: Math.hypot(v.x - p[k].x, v.y - p[k].y) <= 12, forceT: v.forceT || 0 });
      }
      v.angle = angle;
      v.x = p[k].x; v.y = p[k].y; v.vitesse = 0.5; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y;
      L.Entites.indexer();
      o.frame(1);
      if (B.cinema) { vueEnRoute.push(boite(L)); fermer(L); }
    }
    for (let k = 0; k < 60 && etape(L) === e0 && B.partie.mission; k++) { v.vitesse = 0; v.vx = 0; v.vy = 0; o.frame(1); fermer(L); }
    return { tuiles: p.length, secondes: Math.round(p.length * L.TT / (0.75 * v.def.vitesse_max) / 60),
             arrive: etape(L) !== e0, vueEnRoute: vueEnRoute, forcees: forcees };
  }
  // La longueur d'un trajet d'AVANT (celui que la mission faisait), sans le rouler.
  function longueur(L, a, b, r) { const p = chemin(L, a.x, a.y, b.x, b.y, r); return p ? p.length : null; }
  // Semer pour de vrai : hors de vue, les étoiles tombent une à une. La police quitte la ville
  // à chaque image (sinon un agent qui passe nous revoit, et le juge tiendrait à la graine).
  function semer(L, o) {
    const B = L.B, e0 = etape(L), depart = B.recherche.etoiles;
    let i = 0;
    for (; i < 60 * 120 && etape(L) === e0 && B.partie.mission; i++) {
      B.entites.filter(function (e) {
        return e.agent || e.type === 'helico' || (e.type === 'vehicule' && e.conducteur === 'police');
      }).forEach(function (e) { L.Entites.retirer(e); });
      o.frame(1); fermer(L);
    }
    return { depart: depart, secondes: Math.round(i / 60), seme: etape(L) !== e0, etoiles: B.recherche.etoiles };
  }
  // Rattraper le fuyard : il file, on le laisse filer, puis on le rejoint quand il s'arrête.
  function rattraper(L, o, images) {
    const B = L.B, j = B.joueur, f = B.mission && B.mission.fuyard;
    if (!f) return null;
    let dMax = 0;
    for (let k = 0; k < images; k++) { o.frame(1); fermer(L); dMax = Math.max(dMax, Math.hypot(f.x - j.x, f.y - j.y)); }
    f.vitesse = 0; f.vx = 0; f.vy = 0;
    if (j.dansVehicule) L.Vehicules.descendre(j, true);
    j.x = f.x + 24; j.y = f.y; L.Entites.indexer();
    o.frame(2);
    const tombe = !!B.mission.fuyardTombe;
    const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
    if (porteur) L.Entites.assommer(porteur);
    o.frame(2);
    const caisse = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
    if (caisse) { j.x = caisse.x; j.y = caisse.y; L.Entites.indexer(); }
    o.frame(2);
    return { fuit: Math.round(dMax), tombe: tombe, porteur: !!porteur, caisse: !!caisse };
  }
  function debut(L) {
    L.Jeu.commencer(); L.graine(6);
    const B = L.B; B.joueur.invincible = 1e6;
    faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm50', 'm6', 'f01', 'e01']);
  }
"""

#: Les prérequis de chaque mission, marqués faits au départ (le téléphone reste libre de sonner :
#: ses appels se ferment comme les autres répliques).


def _jouer(banc, corps):
    return banc("function (L, o) {" + OUTILS + corps + "}")


def test_e02_la_biere_passe_par_le_phare_seme_la_patrouille_et_finit_chez_ti_paul(banc):
    """Ti-Paul : le camion de bière dort aux Quais ; deux caisses pour le gardien du phare (le bout
    est de La Pointe), une patrouille qui trouve la bière louche, puis le dépanneur (le bout ouest
    des Érables). Deux fois la ville au lieu d'une."""
    r = _jouer(banc, """
        debut(L);
        const B = L.B, j = B.joueur, argent = paiements(L);
        const ti = L.Histoire.donneur('tipaul');
        aCote(L, ti);
        const parle = L.Histoire.parler('tipaul');
        passer(L, o);
        // La réplique PENDANT du premier objectif se dit, l'intro finie (« Douce, douce! »).
        const douce = ecouter(L, o);
        const v = B.mission.vehicule, cantine = L.Histoire.lieu('cantine');
        const camion = { slug: v.slug, d: Math.round(Math.hypot(v.x - cantine.x, v.y - cantine.y)) };
        const avant = longueur(L, v, L.Histoire.lieuDeLivraison('depanneur'), 4);
        monterDans(L, o, v);
        const phare = ecouter(L, o);
        const monte = etape(L);
        const t1 = rouler(L, o, L.Histoire.lieu('phare'), 5);
        const apresPhare = { boite: ecouter(L, o), etape: etape(L), etoiles: B.recherche.etoiles };
        const s = semer(L, o);
        const t2 = rouler(L, o, L.Histoire.lieuDeLivraison('depanneur'), 3);
        finir(L, o);
        return { parle: parle, douce: douce, camion: camion, monte: monte, phare: phare, t1: t1, apresPhare: apresPhare, s: s, t2: t2,
                 avant: avant, fait: !!B.partie.missionsFaites.e02, argent: argent };
    """)
    assert r["parle"] and r["camion"]["slug"] == "camion", r
    assert r["douce"] and r["douce"]["texte"].startswith("Douce, douce"), r["douce"]
    assert r["monte"] == 1 and r["phare"]["qui"] == "tipaul" and "La Pointe" in r["phare"]["texte"], r
    assert r["t1"]["arrive"], f"le camion n'arrive pas au phare : {r['t1']}"
    assert r["apresPhare"]["etape"] == 2 and r["apresPhare"]["etoiles"] >= 1, "au phare, une patrouille : %s" % r["apresPhare"]
    assert r["apresPhare"]["boite"]["texte"].startswith("Une patrouille"), r["apresPhare"]
    assert r["s"]["seme"] and r["s"]["etoiles"] == 0, f"la patrouille ne lâche pas : {r['s']}"
    assert r["t2"]["arrive"] and r["fait"] is True, r
    assert r["argent"] and r["argent"][0] in (250, 375), r["argent"]
    assert r["t1"]["tuiles"] + r["t2"]["tuiles"] > 1.5 * r["avant"], "le détour allonge vraiment le trajet : %s" % r
    print("e02", {"avant_tuiles": r["avant"], "phare": r["t1"]["tuiles"], "depanneur": r["t2"]["tuiles"],
                  "s": [r["t1"]["secondes"], r["s"]["secondes"], r["t2"]["secondes"]], "prime": r["argent"]})


def test_f02_gilles_regarde_ailleurs_les_boulonneux_arrivent_et_gus_a_son_stock(banc):
    """Gus : la fourrière de nuit, Gilles à la guérite (payé pour regarder ailleurs, il le dit), le
    camion, les Boulonneux qui arrivent de loin sur la cargaison, puis l'armurerie."""
    r = _jouer(banc, """
        debut(L);
        const B = L.B, j = B.joueur, argent = paiements(L);
        aCote(L, L.Histoire.donneur('gus'));
        const parle = L.Histoire.parler('gus');
        passer(L, o);
        heure(L, true);
        const four = L.Histoire.lieu('fourriere');
        const aller = longueur(L, L.Histoire.lieu('armurerie'), four, 5);
        j.x = four.x; j.y = four.y; L.Entites.indexer();
        o.frame(3);
        const gus = ecouter(L, o);
        const aLaGuerite = etape(L);
        const avant = { etape: etape(L) };
        aCote(L, L.Histoire.donneur('gilles'));
        const rendu = L.Histoire.parler('gilles');
        const accueil = boite(L);
        fermer(L);
        const apresGilles = etape(L);
        const v = B.mission.vehicule;
        monterDans(L, o, v);
        const monte = etape(L);
        const trois = hommes(L, 3);
        const pendant = ecouter(L, o);
        trois.forEach(function (h) { L.Entites.assommer(h.e); });
        o.frame(2); fermer(L);
        const apresBagarre = etape(L);
        if (!j.dansVehicule) monterDans(L, o, v);
        const t = rouler(L, o, L.Histoire.lieuDeLivraison('armurerie'), 3);
        finir(L, o);
        return { parle: parle, gus: gus, aLaGuerite: aLaGuerite, rendu: rendu, accueil: accueil, apresGilles: apresGilles,
                 monte: monte, trois: trois.map(function (h) { return { d: h.d, etat: h.etat, vie: h.vie }; }),
                 pendant: pendant, apresBagarre: apresBagarre, t: t, aller: aller, fait: !!B.partie.missionsFaites.f02, argent: argent };
    """)
    assert r["parle"] and r["aLaGuerite"] == 1, r
    assert r["gus"] and r["gus"]["qui"] == "gus" and "Gilles" in r["gus"]["texte"], r["gus"]
    assert r["rendu"] is True and r["accueil"]["partie"] == "accueil" and r["accueil"]["qui"] == "gilles", r["accueil"]
    assert r["accueil"]["texte"].startswith("C'est Gilles"), "Gilles se nomme à la poignée de main"
    assert r["apresGilles"] == 2 and r["monte"] == 3, r
    assert len(r["trois"]) == 3, r["trois"]
    for h in r["trois"]:
        assert 100 <= h["d"] <= 260 and h["etat"] == "attaque_joueur", f"ils arrivent de loin, sur nous : {h}"
    assert r["pendant"]["qui"] == "gus" and r["pendant"]["texte"].startswith("Des Boulonneux"), r["pendant"]
    assert r["apresBagarre"] == 4
    assert r["t"]["arrive"] and r["fait"] is True and r["argent"][0] in (350, 525), (r["t"], r["fait"], r["argent"])
    print("f02", {"fourriere": r["aller"], "armurerie": r["t"]["tuiles"], "s": r["t"]["secondes"], "prime": r["argent"]})


def test_f03_la_caisse_de_rosa_ses_chums_la_robe_a_l_hotel_puis_la_boutique(banc):
    """Rosa : le Chevreuil en berline (rattrapé, la caisse ramassée), deux de ses chums à mains nues
    qui arrivent de loin, la robe de mariée à l'Hôtel Bandini (le bout sud-ouest), puis la boutique
    (le nord-est) : la berline du Chevreuil sert de taxi."""
    r = _jouer(banc, """
        debut(L);
        const B = L.B, j = B.joueur, argent = paiements(L);
        const rosa = L.Histoire.donneur('rosa');
        aCote(L, rosa);
        const parle = L.Histoire.parler('rosa');
        passer(L, o);
        const f = B.mission.fuyard;
        const ra = rattraper(L, o, 150);
        const apresCaisse = etape(L);
        const deux = hommes(L, 1);
        const pendant1 = ecouter(L, o);
        j.x = j.x + 0; deux.forEach(function (h) { L.Entites.assommer(h.e); });
        o.frame(2);
        const pendant2 = ecouter(L, o);
        const apresBagarre = etape(L);
        monterDans(L, o, f);
        const t1 = rouler(L, o, L.Histoire.lieu('hotel'), 3);
        const pendant3 = ecouter(L, o);
        const aLHotel = etape(L);
        const t2 = rouler(L, o, L.Histoire.lieu('vetements'), 3);
        aCote(L, L.Histoire.donneur('rosa'));
        finir(L, o);
        return { parle: parle, ra: ra, apresCaisse: apresCaisse, deux: deux.map(function (h) { return { d: h.d, etat: h.etat, arme: h.arme, vie: h.vie }; }),
                 pendant1: pendant1, pendant2: pendant2, apresBagarre: apresBagarre, t1: t1, pendant3: pendant3, aLHotel: aLHotel,
                 t2: t2, fait: !!B.partie.missionsFaites.f03, argent: argent };
    """)
    assert r["parle"] and r["ra"]["fuit"] > 60 and r["ra"]["tombe"] and r["ra"]["caisse"], r["ra"]
    assert r["apresCaisse"] == 1 and len(r["deux"]) == 2, r
    for h in r["deux"]:
        assert 100 <= h["d"] <= 260 and h["etat"] == "attaque_joueur", h
        assert h["arme"] is None and h["vie"] == 60, "des Chevreuils à mains nues, comme e01"
    assert r["pendant1"]["qui"] == "rosa" and r["pendant1"]["texte"].startswith("Ses petits amis"), r["pendant1"]
    assert r["apresBagarre"] == 2 and r["pendant2"]["texte"].startswith("Tant qu'à y être"), r
    assert r["t1"]["arrive"] and r["aLHotel"] == 3, r["t1"]
    assert r["pendant3"]["texte"].startswith("La mariée a appelé"), r["pendant3"]
    assert r["fait"] is True and r["argent"] == [250], r
    print("f03", {"hotel": r["t1"]["tuiles"], "boutique": r["t2"]["tuiles"], "s": [r["t1"]["secondes"], r["t2"]["secondes"]]})


def test_f08_la_cle_chez_rosa_la_fourriere_la_police_le_phare_puis_le_garage(banc):
    """Marco : la clé chez Rosa (elle la gardait pour la lancer par la tête de Rocco), la fourrière
    de nuit, la berline, la police semée, un dernier tour par le phare de La Pointe, le garage."""
    r = _jouer(banc, """
        debut(L);
        faites(L, ['f02', 'f03']);
        const B = L.B, j = B.joueur, argent = paiements(L);
        const intro = [];
        L.Histoire.demarrer('f08');
        for (let n = 0; n < 6000 && (B.scene || B.cinema); n++) {
          o.frame(1);
          const b = boite(L); if (b && intro.indexOf(b.texte) < 0) intro.push(b.texte);
          if (B.cinema && n % 30 === 0) L.Histoire.suivante();
        }
        const legs = { rosa: longueur(L, L.Histoire.lieu('garage'), L.Histoire.lieu('vetements'), 5),
                       fourriere: longueur(L, L.Histoire.lieu('vetements'), L.Histoire.lieu('fourriere'), 5),
                       avant: longueur(L, L.Histoire.lieu('fourriere'), L.Histoire.lieuDeLivraison('garage'), 3) };
        aCote(L, L.Histoire.donneur('rosa'));
        const rendu = L.Histoire.parler('rosa');
        const accueil = ecouter(L, o);
        const apresRosa = etape(L);
        heure(L, true);
        const four = L.Histoire.lieu('fourriere');
        j.x = four.x; j.y = four.y; L.Entites.indexer();
        o.frame(3); fermer(L);
        const v = B.mission.vehicule;
        monterDans(L, o, v);
        const police = ecouter(L, o);
        const monte = { etape: etape(L), etoiles: B.recherche.etoiles };
        const s = semer(L, o);
        const phare = ecouter(L, o);
        const t1 = rouler(L, o, L.Histoire.lieu('phare'), 5);
        const auPhare = etape(L);
        const t2 = rouler(L, o, L.Histoire.lieuDeLivraison('garage'), 3);
        finir(L, o);
        return { intro: intro, rendu: rendu, accueil: accueil, apresRosa: apresRosa, police: police, monte: monte, s: s,
                 phare: phare, t1: t1, auPhare: auPhare, t2: t2, legs: legs, fait: !!B.partie.missionsFaites.f08, argent: argent };
    """)
    assert any("Rosa" in t for t in r["intro"]), f"Marco envoie chez Rosa dès l'intro : {r['intro']}"
    assert r["rendu"] and r["accueil"]["partie"] == "accueil" and r["accueil"]["qui"] == "rosa", r["accueil"]
    assert r["accueil"]["texte"].startswith("C'est Rosa"), r["accueil"]
    assert r["apresRosa"] == 1, r
    assert r["monte"] == {"etape": 3, "etoiles": 1}, r["monte"]
    assert r["police"]["qui"] == "marco" and r["police"]["texte"].startswith("Ça klaxonne"), r["police"]
    assert r["s"]["seme"], r["s"]
    assert r["phare"]["texte"].startswith("Fais-y faire un tour par le phare"), r["phare"]
    assert r["t1"]["arrive"] and r["auPhare"] == 5, r["t1"]
    assert r["t2"]["arrive"] and r["fait"] is True and r["argent"] == [300], r
    print("f08", {"legs": r["legs"], "phare": r["t1"]["tuiles"], "garage": r["t2"]["tuiles"],
                  "s": [r["s"]["secondes"], r["t1"]["secondes"], r["t2"]["secondes"]]})


def test_f11_mado_tient_trente_secondes_les_cravates_tombent_le_troisieme_file_avec_la_caisse(banc):
    """Mado : trente secondes de négociation (jouées image par image), deux Cravates qui arrivent de
    loin, un troisième qui file en berline avec la caisse, rattrapé ; on la rapporte à Mado."""
    r = _jouer(banc, """
        debut(L);
        const B = L.B, j = B.joueur, argent = paiements(L);
        const mado = L.Histoire.donneur('mado');
        aCote(L, mado);
        const parle = L.Histoire.parler('mado');
        passer(L, o);
        const t0 = B.t;
        let n = 0;
        for (; n < 60 * 40 && etape(L) === 0; n++) { o.frame(1); if (B.cinema) break; }
        const tenu = Math.round((B.t - t0) / 60);
        const deux = hommes(L, 1);
        const pendant1 = ecouter(L, o);
        j.x = mado.x + 300; j.y = mado.y; L.Entites.indexer();
        deux.forEach(function (h) { L.Entites.assommer(h.e); });
        o.frame(2);
        const pendant2 = ecouter(L, o);
        const apresBagarre = { etape: etape(L), fuyard: !!(B.mission && B.mission.fuyard) };
        const ra = rattraper(L, o, 200);
        const pendant3 = ecouter(L, o);
        const aRapporter = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        aCote(L, L.Histoire.donneur('mado'));
        finir(L, o);
        return { parle: parle, tenu: tenu, deux: deux.map(function (h) { return { d: h.d, etat: h.etat }; }), pendant1: pendant1,
                 pendant2: pendant2, apresBagarre: apresBagarre, ra: ra, pendant3: pendant3, aRapporter: aRapporter,
                 fait: !!B.partie.missionsFaites.f11, argent: argent };
    """)
    assert r["parle"] and 29 <= r["tenu"] <= 32, f"trente secondes tenues : {r['tenu']}"
    assert len(r["deux"]) == 2 and all(100 <= h["d"] <= 260 for h in r["deux"]), r["deux"]
    assert r["pendant1"]["qui"] == "mado" and r["pendant1"]["texte"].startswith("Bougez pas"), r["pendant1"]
    assert r["apresBagarre"] == {"etape": 2, "fuyard": True}, r["apresBagarre"]
    assert r["pendant2"]["texte"].startswith("Le troisième se sauve"), r["pendant2"]
    assert r["ra"] and r["ra"]["fuit"] > 60 and r["ra"]["tombe"] and r["ra"]["caisse"], r["ra"]
    assert r["aRapporter"]["etape"] == 3 and r["aRapporter"]["ligne"].startswith("RAPPORTE LA CAISSE"), r["aRapporter"]
    assert r["pendant3"]["texte"].startswith("Reviens au casse-croûte"), r["pendant3"]
    assert r["fait"] is True and r["argent"] == [200], r


def test_r01_le_carnet_rattrape_roy_semee_puis_le_coffre_de_l_hotel_sans_une_etoile(banc):
    """Bouchard (dedans) : le poste de nuit, l'agent véreux rattrapé sans une étoile, l'inspectrice
    Roy semée, puis le carnet caché à l'Hôtel Bandini — au bout sud-ouest, dans la berline de
    l'agent — toujours sans une étoile. La fin se dit au casse-croûte."""
    r = _jouer(banc, """
        debut(L);
        const B = L.B, j = B.joueur, argent = paiements(L);
        L.Histoire.demarrer('r01');
        passer(L, o);
        heure(L, true);
        const poste = L.Histoire.lieu('poste');
        const avant = longueur(L, poste, L.Histoire.lieu('casse_croute'), 3);
        j.x = poste.x; j.y = poste.y; L.Entites.indexer();
        o.frame(3);
        const pendant1 = ecouter(L, o);
        const f = B.mission.fuyard;
        const ra = rattraper(L, o, 200);
        const etoilesRattrape = B.recherche.etoiles;
        const apresCarnet = { etape: etape(L), etoiles: B.recherche.etoiles };
        const pendant2 = ecouter(L, o);
        const s = semer(L, o);
        const pendant3 = ecouter(L, o);
        monterDans(L, o, f);
        const t = rouler(L, o, L.Histoire.lieu('hotel'), 3);
        const etoilesEnRoute = B.recherche.etoiles;
        finir(L, o);
        return { pendant1: pendant1, ra: ra, etoilesRattrape: etoilesRattrape, apresCarnet: apresCarnet, pendant2: pendant2, s: s,
                 pendant3: pendant3, t: t, etoilesEnRoute: etoilesEnRoute, avant: avant,
                 fait: !!B.partie.missionsFaites.r01, argent: argent };
    """)
    assert r["pendant1"]["qui"] == "bouchard" and r["pendant1"]["texte"].startswith("Il roule vers le pont"), r["pendant1"]
    assert r["ra"]["tombe"] and r["ra"]["caisse"], r["ra"]
    assert r["apresCarnet"] == {"etape": 2, "etoiles": 1}, f"le carnet, puis Roy : une étoile, posée par la mission {r}"
    assert r["pendant2"]["texte"].startswith("Roy t'a vu partir"), r["pendant2"]
    assert r["s"]["seme"] and r["s"]["depart"] == 1, r["s"]
    assert r["pendant3"]["texte"].startswith("Pas au poste"), r["pendant3"]
    assert r["t"]["arrive"] and r["etoilesEnRoute"] == 0, f"jusqu'à l'hôtel sans une étoile : {r['t']}"
    assert r["fait"] is True and r["argent"] == [300], r
    print("r01", {"avant": r["avant"], "hotel": r["t"]["tuiles"], "s": [r["s"]["secondes"], r["t"]["secondes"]]})


def test_s01_ti_paul_sait_tout_la_remorqueuse_les_boulonneux_reviennent_puis_le_lot(banc):
    """Gilles : Ti-Paul d'abord (au bout ouest, il sait qui a pris la remorqueuse), la remorqueuse en
    zone des Boulonneux, les Boulonneux qui reviennent la chercher, puis la route du lot."""
    r = _jouer(banc, """
        debut(L);
        faites(L, ['f02']);
        const B = L.B, j = B.joueur, argent = paiements(L);
        aCote(L, L.Histoire.donneur('gilles'));
        const intro = [];
        const parle = L.Histoire.parler('gilles');
        for (let n = 0; n < 6000 && (B.scene || B.cinema); n++) {
          o.frame(1);
          const b = boite(L); if (b && intro.indexOf(b.texte) < 0) intro.push(b.texte);
          if (B.cinema && n % 30 === 0) L.Histoire.suivante();
        }
        const slug = B.partie.mission && B.partie.mission.slug;
        const zone0 = L.Histoire.resoudre('zone:boulonneux', L.Histoire.courante());
        const legs = { tipaul: longueur(L, L.Histoire.lieu('fourriere'), L.Histoire.lieu('depanneur'), 5),
                       zone: longueur(L, L.Histoire.lieu('depanneur'), zone0, 8),
                       avant: longueur(L, L.Histoire.lieu('fourriere'), zone0, 8) };
        aCote(L, L.Histoire.donneur('tipaul'));
        const rendu = L.Histoire.parler('tipaul');
        const accueil = ecouter(L, o);
        o.frame(2);
        const pendant1 = ecouter(L, o);
        const apresTiPaul = etape(L);
        const v = B.mission.vehicule;
        const zone = L.Histoire.resoudre('zone:boulonneux', L.Histoire.courante());
        monterDans(L, o, v);
        const trois = hommes(L, 2);
        const pendant2 = ecouter(L, o);
        const monte = etape(L);
        trois.forEach(function (h) { L.Entites.assommer(h.e); });
        o.frame(2); fermer(L);
        const apresBagarre = etape(L);
        if (!j.dansVehicule) monterDans(L, o, v);
        const t = rouler(L, o, L.Histoire.lieuDeLivraison('fourriere'), 3);
        finir(L, o);
        return { parle: parle, slug: slug, intro: intro, rendu: rendu, accueil: accueil, pendant1: pendant1, apresTiPaul: apresTiPaul,
                 dZone: Math.round(Math.hypot(v.x - zone.x, v.y - zone.y)), monte: monte,
                 trois: trois.map(function (h) { return { d: h.d, etat: h.etat }; }), pendant2: pendant2, apresBagarre: apresBagarre,
                 t: t, legs: legs, fait: !!B.partie.missionsFaites.s01, argent: argent };
    """)
    assert r["parle"] and r["slug"] == "s01", r
    assert any("Ti-Paul" in t for t in r["intro"]), f"Gilles envoie chez Ti-Paul dès l'intro : {r['intro']}"
    assert r["rendu"] and r["accueil"]["partie"] == "accueil" and r["accueil"]["qui"] == "tipaul", r["accueil"]
    assert r["accueil"]["texte"].startswith("Salut, l'ami, c'est Ti-Paul"), r["accueil"]
    assert r["apresTiPaul"] == 1 and r["pendant1"]["qui"] == "gilles", r
    assert r["monte"] == 2 and len(r["trois"]) == 3, r
    for h in r["trois"]:
        assert 100 <= h["d"] <= 260 and h["etat"] == "attaque_joueur", h
    assert r["pendant2"]["texte"].startswith("Ils reviennent la chercher"), r["pendant2"]
    assert r["apresBagarre"] == 3
    assert r["t"]["arrive"] and r["fait"] is True and r["argent"] == [250], (r["t"], r["fait"], r["argent"])
    print("s01", {"legs": r["legs"], "fourriere": r["t"]["tuiles"], "s": r["t"]["secondes"]})
