"""Le tronc du tutoriel (m1, m2, m3), allongé — JOUÉ de l'intro à la prime, étapes neuves comprises.

« Des missions plus longues » (Martin, 22 sept. 2026) : plus d'étapes, des trajets plus loin, plus de
dialogue. Les juges de structure disent qu'une étape existe ; ils ne la jouent pas. Ici, chaque étape se
joue avec ce que le jeu fait vraiment : on MARCHE jusqu'au garage et à l'hôpital (un chemin de piéton,
tuile par tuile), on parle à Marco et à Ginette AU BOUTON, on monte au bouton, on ROULE jusqu'au phare
de La Pointe par les rues (le pont compris), et les étoiles tombent toutes seules, hors de vue — rien
n'est remis à zéro à la main.

⚠️ m1 est la première minute du joueur : chaque étape neuve n'y demande qu'UNE chose, et facile — parler
à quelqu'un qui est déjà là, semer UNE étoile. Le juge le mesure (une étoile, tombée en moins de 40 s).
"""

OUTILS = """
  function passer(L, o) {
    let n = 0;
    while ((L.B.scene || L.B.cinema) && n < 6000) { o.frame(1); if (L.B.cinema && n % 30 === 0) L.Histoire.suivante(); n++; }
  }
  function boite(L) {
    const c = L.B.cinema;
    return c ? { partie: c.partie, qui: c.lignes[0].qui, slug: c.lignes[0].slug } : null;
  }
  function etape(L) { return L.B.partie.mission ? L.B.partie.mission.etape : null; }
  function fermer(L) { let g = 0; while (L.B.cinema && g < 100) { L.Histoire.suivante(); g++; } }
  function faites(L, slugs) { slugs.forEach(function (s) { L.B.partie.missionsFaites[s] = 1; }); }
  function paiements(L) {
    const liste = [], vrai = L.Missions.encaisser;
    L.Missions.encaisser = function (montant, raison) { liste.push(montant); return vrai.apply(null, arguments); };
    return liste;
  }
  function hommes(L, e) {
    return L.B.mission.entites.filter(function (h) { return h.type === 'pieton' && h.cible && h.etape === e && !h.porteLaCaisse; });
  }
  // Un chemin tuile par tuile (BFS), à pied ou en char.
  function chemin(L, de, a, enChar) {
    const TT = L.TT, M = L.Monde, W = M.carte.w, H = M.carte.h;
    const sx = Math.floor(de.x / TT), sy = Math.floor(de.y / TT), gx = Math.floor(a.x / TT), gy = Math.floor(a.y / TT);
    // Le décor solide (poteaux, bancs, bornes) arrête le joueur sans que la grille le dise.
    const plein = new Set();
    for (const e of L.B.entites) if (e.type === 'decor' && e.solide) {
      const r = (e.r || 4) + 6;
      for (let y = Math.floor((e.y - r) / TT); y <= Math.floor((e.y + r) / TT); y++)
        for (let x = Math.floor((e.x - r) / TT); x <= Math.floor((e.x + r) / TT); x++) plein.add(y * W + x);
    }
    const passe = enChar ? function (x, y) { return !M.bloque(x, y, M.MASQUE_VEHICULE) && !M.estEau(x, y) && !plein.has(y * W + x); }
                         : function (x, y) { return !M.bloque(x, y, M.MASQUE_PIETON) && !M.estEau(x, y) && !plein.has(y * W + x); };
    const prev = new Int32Array(W * H).fill(-1), q = [sy * W + sx];
    prev[sy * W + sx] = sy * W + sx;
    let bout = -1, meilleur = 1e9;
    for (let i = 0; i < q.length; i++) {
      const k = q[i], x = k % W, y = (k / W) | 0, d = Math.abs(x - gx) + Math.abs(y - gy);
      if (d < meilleur) { meilleur = d; bout = k; }
      if (d === 0) break;
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = x + dx, ny = y + dy, n = ny * W + nx;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H || prev[n] >= 0 || !passe(nx, ny)) continue;
        prev[n] = k; q.push(n);
      }
    }
    const pts = [];
    for (let k = bout; k !== prev[k]; k = prev[k]) pts.push({ x: (k % W) * TT + 8, y: ((k / W) | 0) * TT + 8 });
    return { pts: pts.reverse(), reste: meilleur };
  }
  // Avancer le long d'un chemin à `pas` px par image (le char, s'il y en a un, porte le joueur), en
  // fermant les répliques qui s'ouvrent ; on s'arrête quand l'objectif change.
  function suivre(L, o, pts, pas, jusqua) {
    const j = L.B.joueur, v = j.dansVehicule;
    let n = 0;
    for (const p of pts) {
      for (let k = 0; k < 60; k++) {
        const qui = v || j, d = Math.hypot(p.x - qui.x, p.y - qui.y);
        if (d < 2) break;
        const s = Math.min(pas, d);
        qui.x += (p.x - qui.x) / d * s; qui.y += (p.y - qui.y) / d * s;
        if (v) { v.angle = Math.atan2(p.y - v.y, p.x - v.x) || v.angle; v.vitesse = 0.3; j.x = v.x; j.y = v.y; }
        o.frame(1); n++;
        if (L.B.cinema) fermer(L);
        if (etape(L) !== jusqua) return n;
      }
    }
    if (v) v.vitesse = 0;
    for (let k = 0; k < 30 && etape(L) === jusqua; k++) { o.frame(1); n++; if (L.B.cinema) fermer(L); }
    return n;
  }
  // Monter dans un char AU BOUTON (ACTION), comme le joueur.
  function monter(L, o, v) {
    const j = L.B.joueur;
    const cotes = [[0, 16], [0, -16], [16, 0], [-16, 0], [0, 22], [0, -22]];
    for (const c of cotes) {
      j.x = v.x + c[0]; j.y = v.y + c[1]; L.Entites.indexer(); o.viser(v);
      if (L.Vehicules.vehiculeSousLaMain(j) === v) break;
    }
    o.tape('KeyE', 2);
    return j.dansVehicule === v;
  }
  // Parler AU BOUTON à un personnage qui se tient en ville.
  function aborder(L, o, slug) {
    const j = L.B.joueur, p = L.Histoire.donneur(slug);
    j.x = p.x - 16; j.y = p.y; L.Entites.indexer(); o.viser(p);
    o.tape('KeyE', 2);
    return boite(L);
  }
  // Semer, pour de vrai : on ROULE vers `cible` (un agent qui enquête retrouve un char arrêté et ne le
  // lâche plus — un joueur, lui, s'en va), jusqu'à ce que les étoiles tombent hors de vue.
  function semer(L, o, cible) {
    const j = L.B.joueur, v = j.dansVehicule, e0 = L.B.recherche.etoiles;
    const pts = v && cible ? chemin(L, v, cible, true).pts : [];
    let n = 0, i = 0;
    while (L.B.recherche.etoiles > 0 && n < 60 * 120) {
      if (v && i < pts.length) {
        const p = pts[i], d = Math.hypot(p.x - v.x, p.y - v.y);
        if (d < 2) i++;
        else { const s = Math.min(2.5, d); v.x += (p.x - v.x) / d * s; v.y += (p.y - v.y) / d * s;
               v.angle = Math.atan2(p.y - v.y, p.x - v.x) || v.angle; v.vitesse = 0.3; j.x = v.x; j.y = v.y; }
      }
      o.frame(1); n++; if (L.B.cinema) fermer(L);
    }
    if (v) v.vitesse = 0;
    return { etoiles: e0, images: n, reste: L.B.recherche.etoiles, roule: i };
  }
  function finir(L, o) { for (let k = 0; k < 400 && L.B.partie.mission; k++) { o.frame(1); if (L.B.cinema) fermer(L); } passer(L, o); }
"""


def test_m1_parler_a_marco_puis_semer_une_etoile_puis_livrer_sans_bosse(banc):
    """Ti-Guy au terminus : on marche au garage, on serre la main de Marco (au bouton : il se nomme), on
    prend le char dans sa ruelle, le propriétaire appelle la police (UNE étoile, Ti-Guy le dit), elle
    tombe hors de vue, et on livre au garage. 100 $, la clé de la planque."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        const argent = paiements(L);
        const ti = L.Histoire.donneur('ti_guy');
        j.x = ti.x - 16; j.y = ti.y; L.Entites.indexer();
        L.Histoire.parler('ti_guy');
        passer(L, o);
        const debut = { slug: B.partie.mission && B.partie.mission.slug, etape: etape(L) };
        const g = L.Histoire.lieu('garage');
        const aPied = chemin(L, j, g, false);
        const marche = suivre(L, o, aPied.pts, L.B.defs.recherche.vitesses.joueur_course, 0);
        const auGarage = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        const main = aborder(L, o, 'marco');
        const pendantMain = etape(L);
        fermer(L);
        const apresMain = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        const v = B.mission.vehicule;
        const versChar = chemin(L, j, v, false);
        const monte = monter(L, o, v);
        o.frame(2);
        const auVolant = { monte: monte, etape: etape(L), etoiles: B.recherche.etoiles, boite: boite(L) };
        fermer(L);
        const seme = semer(L, o, L.Histoire.lieu('hotel'));
        o.frame(2);
        const semee = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), boite: boite(L) };
        fermer(L);
        const baie = L.Histoire.lieuDeLivraison('garage');
        const route = chemin(L, v, baie, true);
        suivre(L, o, route.pts, 2.5, 4);
        v.vitesse = 0;
        finir(L, o);
        return { debut: debut, marche: marche, aPied: aPied.pts.length, auGarage: auGarage, main: main,
                 pendantMain: pendantMain, apresMain: apresMain, versChar: versChar.pts.length, auVolant: auVolant,
                 seme: seme, semee: semee, route: route.pts.length, resteRoute: route.reste,
                 fait: !!B.partie.missionsFaites.m1, argent: argent, mission: B.partie.mission };
    }""")
    assert r["debut"] == {"slug": "m1", "etape": 0}, r["debut"]
    assert r["auGarage"]["etape"] == 1 and r["auGarage"]["ligne"].startswith("PARLE À MARCO"), r["auGarage"]
    assert r["main"] == {"partie": "accueil", "qui": "marco", "slug": "marco-m1-12"}, \
        f"au bouton, Marco dit sa poignée de main (il se nomme) : {r['main']}"
    assert r["pendantMain"] == 1, "l'objectif attend la fin de sa réplique"
    assert r["apresMain"]["etape"] == 2 and r["apresMain"]["ligne"].startswith("PRENDS LE CHAR"), r["apresMain"]
    a = r["auVolant"]
    assert a["monte"] and a["etape"] == 3, f"au volant, on sème : {a}"
    assert a["etoiles"] == 1, "UNE étoile : la première minute du joueur"
    assert a["boite"] and a["boite"]["qui"] == "ti_guy" and a["boite"]["partie"] == "pendant", a["boite"]
    s = r["seme"]
    assert s["reste"] == 0 and s["images"] < 60 * 40, f"une étoile tombe vite hors de vue : {s}"
    assert r["semee"]["etape"] == 4 and r["semee"]["ligne"].startswith("RAMÈNE-LE AU GARAGE"), r["semee"]
    assert r["semee"]["boite"] and r["semee"]["boite"]["slug"] == "ti_guy-m1-11", "« Beau char! » à la livraison"
    assert r["resteRoute"] == 0, "le char rejoint le garage par les rues"
    assert r["fait"] is True and r["mission"] is None, r
    assert r["argent"] and r["argent"][0] >= 100, r["argent"]


def test_m2_les_renforts_puis_l_hopital_et_ginette_puis_la_caisse_rendue(banc):
    """Madame Thibodeau : deux Cravates aux poings, le fuyard en moto, puis DEUX de plus qui arrivent de
    loin (aux poings eux aussi), puis l'hôpital à pied — Ginette se nomme à la poignée de main —, puis
    le thé au kiosque. 150 $, le bâton."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1']);
        const argent = paiements(L);
        const th = L.Histoire.donneur('thibodeau');
        j.x = th.x - 16; j.y = th.y; L.Entites.indexer();
        L.Histoire.parler('thibodeau');
        passer(L, o);
        for (let k = 0; k < 10 && !hommes(L, 0).length; k++) o.frame(1);
        hommes(L, 0).forEach(function (h) { L.Entites.assommer(h); });
        o.frame(2); fermer(L);
        const fuyard = { etape: etape(L), moto: !!B.mission.fuyard };
        const moto = B.mission.fuyard;
        moto.vie = moto.vieMax * 0.3;
        o.frame(2); fermer(L);
        const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
        if (porteur) L.Entites.assommer(porteur);
        o.frame(2);
        const caisse = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
        if (caisse) { j.x = caisse.x; j.y = caisse.y; L.Entites.indexer(); }
        o.frame(2);
        const renforts = { etape: etape(L), boite: boite(L) };
        fermer(L); o.frame(2);
        const deux = hommes(L, 2).map(function (h) {
            return { d: Math.round(Math.hypot(h.x - j.x, h.y - j.y)), etat: h.etat, arme: h.arme || null, vie: h.vieMax };
        });
        hommes(L, 2).forEach(function (h) { L.Entites.assommer(h); });
        o.frame(2);
        const hopital = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), boite: boite(L) };
        fermer(L);
        const h = L.Histoire.lieu('hopital');
        const aPied = chemin(L, j, h, false);
        const marche = suivre(L, o, aPied.pts, L.B.defs.recherche.vitesses.joueur_course, 3);
        const arrive = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), d: Math.round(Math.hypot(j.x - h.x, j.y - h.y)), n: marche, len: aPied.pts.length, int: !!B.interieur, vie: j.vie, etat: j.etat, att: B.mission && B.mission.attend, cin: !!B.cinema, sc: !!B.scene, menu: B.menu && B.menu.titre };
        const main = aborder(L, o, 'ginette');
        fermer(L); o.frame(2);
        const the = { etape: etape(L), boite: boite(L) };
        fermer(L);
        const retour = chemin(L, j, L.Histoire.donneur('thibodeau'), false);
        suivre(L, o, retour.pts, L.B.defs.recherche.vitesses.joueur_course, 5);
        const t2 = L.Histoire.donneur('thibodeau');
        j.x = t2.x - 16; j.y = t2.y; L.Entites.indexer();
        finir(L, o);
        return { fuyard: fuyard, renforts: renforts, deux: deux, hopital: hopital, aPied: aPied.pts.length,
                 resteHopital: aPied.reste, marche: marche, arrive: arrive, main: main, the: the,
                 retour: retour.pts.length, fait: !!B.partie.missionsFaites.m2, batte: !!B.partie.armes.batte,
                 argent: argent };
    }""")
    assert r["fuyard"] == {"etape": 1, "moto": True}, r["fuyard"]
    assert r["renforts"]["etape"] == 2, f"la caisse ramassée, les renforts : {r['renforts']}"
    assert r["renforts"]["boite"] and r["renforts"]["boite"]["qui"] == "thibodeau", r["renforts"]
    assert len(r["deux"]) == 2, r["deux"]
    for hh in r["deux"]:
        assert 100 <= hh["d"] <= 260, f"ils arrivent de loin, pas sur nous ({hh['d']} px)"
        assert hh["etat"] == "attaque_joueur" and hh["arme"] is None and hh["vie"] == 55, hh
    assert r["hopital"]["etape"] == 3 and r["hopital"]["ligne"].startswith("VA TE FAIRE SOIGNER"), r["hopital"]
    assert r["hopital"]["boite"] and r["hopital"]["boite"]["qui"] == "thibodeau"
    assert r["resteHopital"] <= 3, "l'hôpital se rejoint à pied (le décor devant la porte compris)"
    assert r["arrive"]["etape"] == 4 and r["arrive"]["ligne"].startswith("PARLE À GINETTE"), str(r["arrive"])
    assert r["main"] == {"partie": "accueil", "qui": "ginette", "slug": "ginette-m2-14"}, r["main"]
    assert r["the"]["etape"] == 5 and r["the"]["boite"] and r["the"]["boite"]["qui"] == "thibodeau", r["the"]
    assert r["fait"] is True and r["batte"] is True and r["argent"] == [150], r


def test_m3_la_boite_au_phare_puis_le_client_de_la_police_seme_puis_le_taxi_rendu(banc):
    """Marco : le taxi, trois courses (le client de la troisième est de la police), puis la boîte du
    coffre au phare de La Pointe — à l'autre bout de la ville, par le pont —, puis le client qui a suivi
    (UNE étoile, qui tombe hors de vue), puis le taxi rendu au garage. 200 $."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2']);
        const argent = paiements(L);
        const marco = L.Histoire.donneur('marco');
        j.x = marco.x - 16; j.y = marco.y; L.Entites.indexer();
        L.Histoire.parler('marco');
        passer(L, o);
        const v = B.mission.vehicule;
        const monte = monter(L, o, v);
        o.frame(2); fermer(L);
        const courses = { monte: monte, etape: etape(L) };
        // Les trois courses ne sont pas neuves : le compteur des boulots, le client à la troisième.
        L.Missions.boulot.faits.taxi = (L.Missions.boulot.faits.taxi || 0) + 2;
        // ⚠️ Sans client assis, la machine des boulots remet son étape à zéro dans l'image : on
        // la tient « en route » le temps que le compteur de la mission lise la troisième course.
        Object.defineProperty(L.Missions.boulot, 'etape', { get: function () { return 'route'; }, set: function () {}, configurable: true });
        o.frame(2);
        delete L.Missions.boulot.etape; L.Missions.boulot.etape = null;
        const client = boite(L);
        fermer(L);
        L.Missions.boulot.faits.taxi += 1;
        o.frame(2);
        const phare = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), boite: boite(L) };
        fermer(L);
        const p = L.Histoire.lieu('phare');
        const route = chemin(L, v, p, true);
        const roule = suivre(L, o, route.pts, 2.5, 2);
        const auPhare = { etape: etape(L), etoiles: B.recherche.etoiles, ligne: L.Histoire.ligneObjectif(),
                          dans: j.dansVehicule === v };
        const seme = semer(L, o, L.Histoire.lieuDeLivraison('garage'));
        o.frame(2);
        const semee = { etape: etape(L), boite: boite(L) };
        fermer(L);
        const retour = chemin(L, v, L.Histoire.lieuDeLivraison('garage'), true);
        suivre(L, o, retour.pts, 2.5, 4);
        v.vitesse = 0;
        finir(L, o);
        return { courses: courses, client: client, phare: phare, route: route.pts.length, resteRoute: route.reste,
                 roule: roule, auPhare: auPhare, seme: seme, semee: semee, retour: retour.pts.length,
                 resteRetour: retour.reste, fait: !!B.partie.missionsFaites.m3, argent: argent };
    }""")
    assert r["courses"] == {"monte": True, "etape": 1}, r["courses"]
    assert r["client"] and r["client"]["qui"] == "civil", r["client"]
    assert r["phare"]["etape"] == 2 and r["phare"]["ligne"].startswith("PORTE LA BOÎTE"), r["phare"]
    assert r["phare"]["boite"] and r["phare"]["boite"]["qui"] == "marco", r["phare"]
    assert r["resteRoute"] == 0 and r["route"] >= 250, f"le phare est loin, et s'atteint en char : {r['route']} tuiles"
    a = r["auPhare"]
    assert a["etape"] == 3 and a["etoiles"] == 1 and a["dans"], f"au phare, le client a suivi : {a}"
    assert r["seme"]["reste"] == 0 and r["seme"]["images"] < 60 * 40, r["seme"]
    assert r["semee"]["etape"] == 4 and r["semee"]["boite"] and r["semee"]["boite"]["qui"] == "marco", r["semee"]
    assert r["resteRetour"] == 0
    assert r["fait"] is True and r["argent"] == [200], r
