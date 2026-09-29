"""Le tronc, allongé (« Des missions plus longues », Martin, 22 sept. 2026) — m1 à m6 et m97, JOUÉS
au banc, étapes neuves comprises.

## Le tutoriel : m1, m2, m3

Plus d'étapes, des trajets plus loin, plus de dialogue. Les juges de structure disent qu'une étape existe ; ils ne la jouent pas. Ici, chaque étape se
joue avec ce que le jeu fait vraiment : on MARCHE jusqu'au garage et à l'hôpital (un chemin de piéton,
tuile par tuile), on parle à Marco et à Ginette AU BOUTON, on monte au bouton, on ROULE jusqu'au phare
de La Pointe par les rues (le pont compris), et les étoiles tombent toutes seules, hors de vue — rien
n'est remis à zéro à la main.

⚠️ m1 est la première minute du joueur : chaque étape neuve n'y demande qu'UNE chose, et facile — parler
à quelqu'un qui est déjà là, semer UNE étoile. Le juge le mesure (une étoile, tombée en moins de 40 s).

## m4, m5, m6, m97

Chacune a gagné des étapes (un détour à l'autre bout de la ville, une poursuite, une bagarre, un
retour), et chaque étape neuve a sa réplique `pendant`. Les juges de structure disent que c'est
câblé ; ici, chaque mission se joue de la poignée de main (ou du `parler` au donneur) à la prime,
étape par étape et DANS L'ORDRE — les étapes neuves comprises, chacune par ce qui l'accomplit en jeu :
le char qu'on conduit jusqu'au lieu, les hommes qui ARRIVENT de loin et qu'on couche, le fuyard
qu'on rattrape et la caisse qu'on ramasse, les poches vidées par-derrière, le donneur rejoint.
Les trajets sont téléportés (le banc n'a pas de pilote) ; les étoiles des `semer` d'avant ce passage
tombent à la main, comme dans `test_cinq_missions_js.py`.

Les deux moitiés gardent chacune leurs aides (`OUTILS_TUTORIEL`, `OUTILS`) : `boite`,
`paiements`, `hommes` et `finir` n'y regardent pas la même chose.
"""

from outils_missions import outils

OUTILS_TUTORIEL = outils("passer", "etape", "fermer", "faites") + """
  function boite(L) {
    const c = L.B.cinema;
    return c ? { partie: c.partie, qui: c.lignes[0].qui, slug: c.lignes[0].slug } : null;
  }
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
    r = banc("function (L, o) {" + OUTILS_TUTORIEL + """
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
    r = banc("function (L, o) {" + OUTILS_TUTORIEL + """
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
    r = banc("function (L, o) {" + OUTILS_TUTORIEL + """
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


# --- m4, m5, m6, m97 ----------------------------------------------------------------------------

OUTILS = outils("passer", "etape", "fermer", "faites", "heure", "paiements", "ici", "finir") + """
  function boite(L) {
    const c = L.B.cinema, l = c && c.lignes[Math.max(0, c.i)];
    return l ? { partie: c.partie, qui: l.qui, slug: l.slug, telephone: l.telephone } : null;
  }
  function hommes(L, etape) {
    const j = L.B.joueur;
    return L.B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible && e.etape === etape && e.vivant; })
      .map(function (e) { return { e: e, d: Math.round(Math.hypot(e.x - j.x, e.y - j.y)) }; });
  }
  // Une image, puis la réplique `pendant` qu'elle ouvre (le cas échéant), relevée et fermée.
  function pas(L, o, n) {
    let b = null;
    for (let k = 0; k < (n || 3); k++) { o.frame(1); if (!b && L.B.cinema) b = boite(L); fermer(L); }
    return b;
  }
  // Le char de la mission au pixel d'un lieu, le joueur au volant, arrêté.
  function garer(L, v, l) {
    const j = L.B.joueur;
    v.x = l.x; v.y = l.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y; L.Entites.indexer();
  }
"""


def test_m4_le_lunch_du_sergent_la_fourriere_les_cravates_puis_les_cles(banc):
    """Bouchard, au casse-croûte (son alibi est le `pendant` de l'objectif 0 : le moteur ne le dit pas
    encore après une intro, ce juge ne l'attend pas) ; de nuit, l'auto-patrouille au poste, Ti-Guy derrière ; semée, on la mène à la fourrière (à l'autre
    bout de la ville) pour ses plaques ; larguée au garage, deux Cravates arrivent les poings nus pour
    la prendre ; couchés, on rapporte les clés au casse-croûte : 400 $."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur, M = L.Monde; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3']);
        const argent = paiements(L);
        heure(L, false);
        o.entrer(M.carte.portes.find(function (p) { return p.lieu === 'casse_croute'; }));
        const parle = L.Histoire.parler('bouchard');
        passer(L, o);
        pas(L, o, 5);
        o.sortir();
        const out = { parle: parle, slug: B.partie.mission && B.partie.mission.slug };
        // 0. Au poste, de nuit.
        const poste = L.Histoire.lieu('poste');
        ici(L, poste); o.frame(3);
        out.jour = { etape: etape(L), attend: B.mission.attend };
        heure(L, true);
        ici(L, poste);
        pas(L, o);
        out.poste = etape(L);
        // 1. L'auto-patrouille.
        const v = B.mission.vehicule;
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        out.tiGuy = pas(L, o);
        out.semer = { etape: etape(L), etoiles: B.recherche.etoiles, escorte: !!B.mission.escorte };
        // 2. Semée (le banc ne pilote pas une poursuite : les étoiles tombent à la main).
        B.recherche.etoiles = 0; B.recherche.vu = 0;
        out.fourriere = { pendant: pas(L, o), etape: etape(L), ligne: L.Histoire.ligneObjectif(),
                          gps: (L.Histoire.cible() || {}).nom || null };
        // 3. À la fourrière, au volant : on n'y descend pas.
        const f = L.Histoire.lieu('fourriere'), g = L.Histoire.lieu('garage');
        out.loin = Math.round(Math.hypot(f.x - poste.x, f.y - poste.y) / L.TT);
        garer(L, v, f);
        out.garage = { etape: etape(L), dans: j.dansVehicule === v };
        pas(L, o);
        out.garage.etape = etape(L);
        // 4. Larguée au garage.
        garer(L, v, L.Histoire.lieuDeLivraison('garage'));
        const tiGuy2 = pas(L, o);
        const deux = hommes(L, 5);
        out.cravates = { etape: etape(L), pendant: tiGuy2, dehors: !j.dansVehicule,
                         arrivent: deux.map(function (h) { return { d: h.d, etat: h.e.etat, arme: h.e.arme || null, vie: h.e.vieMax }; }) };
        // 5. On les couche.
        deux.forEach(function (h) { L.Entites.assommer(h.e); });
        const cles = pas(L, o);
        out.cles = { etape: etape(L), pendant: cles, ligne: L.Histoire.ligneObjectif() };
        // 6. Les clés, au casse-croûte.
        ici(L, L.Histoire.lieu('casse_croute'));
        finir(L, o);
        out.fait = !!B.partie.missionsFaites.m4; out.ami = !!B.partie.sergentAmi;
        out.argent = argent.map(function (a) { return a.montant; });
        out.garageLoin = Math.round(Math.hypot(f.x - g.x, f.y - g.y) / L.TT);
        return out;
    }""")
    assert r["parle"] is True and r["slug"] == "m4", r
    assert r["jour"] == {"etape": 0, "attend": "ATTENDS LA NUIT"}
    assert r["poste"] == 1
    assert r["tiGuy"] and r["tiGuy"]["qui"] == "ti_guy", r["tiGuy"]
    assert r["semer"] == {"etape": 2, "etoiles": 2, "escorte": True}
    f = r["fourriere"]
    assert f["etape"] == 3 and f["ligne"].startswith("PASSE PAR LA FOURRIÈRE"), f
    assert f["pendant"] and f["pendant"]["qui"] == "bouchard" and f["pendant"]["telephone"] is True, f
    assert f["gps"] == "Fourrière municipale", "le GPS mène à la fourrière"
    assert r["loin"] >= 150 and r["garageLoin"] >= 150, f"un vrai détour : {r['loin']} et {r['garageLoin']} tuiles"
    assert r["garage"] == {"etape": 4, "dans": True}, "à la fourrière, on reste au volant ; ensuite, le garage"
    c = r["cravates"]
    assert c["etape"] == 5 and c["dehors"], c
    assert c["pendant"] and c["pendant"]["qui"] == "ti_guy", c
    assert len(c["arrivent"]) == 2, c
    for h in c["arrivent"]:
        assert 100 <= h["d"] <= 260 and h["etat"] == "attaque_joueur", f"ils arrivent de loin, sur nous ({h})"
        assert h["arme"] is None and h["vie"] == 70, "deux petits, les poings nus"
    k = r["cles"]
    assert k["etape"] == 6 and k["ligne"].startswith("RAPPORTE LES CLÉS"), k
    assert k["pendant"] and k["pendant"]["qui"] == "bouchard", k
    assert r["fait"] is True and r["ami"] is True and r["argent"] == [400]


def test_m5_la_chef_des_quais_la_caisse_des_cravates_file_puis_la_cantine(banc):
    """Josée : les trois coins, le chef ; puis leur trésorier file en char avec la caisse — on le
    rattrape (on le cabosse), un Cravate en descend avec elle, on le couche, on la ramasse ; la police
    semée, la caisse va derrière la cantine des Quais (à l'autre bout de la ville), puis la planque."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur, M = L.Monde; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4']);
        const argent = paiements(L);
        o.entrer(M.carte.portes.find(function (p) { return p.lieu === 'bar'; }));
        const parle = L.Histoire.parler('josee');
        passer(L, o);
        pas(L, o);
        o.sortir();
        const out = { parle: parle, slug: B.partie.mission && B.partie.mission.slug };
        // 0. Les trois coins.
        hommes(L, 0).forEach(function (h) { L.Entites.assommer(h.e); });
        const chef = pas(L, o);
        out.chef = { etape: etape(L), pendant: chef };
        // 1. Le chef.
        const lui = B.mission.entites.find(function (e) { return e.chef; });
        ici(L, { x: lui.x - 30, y: lui.y });
        L.Entites.assommer(lui);
        const tresorier = pas(L, o);
        const v = B.mission.fuyard;
        out.fuyard = { etape: etape(L), pendant: tresorier, char: v ? v.slug : null, file: v ? v.fuite : null,
                       d: v ? Math.round(Math.hypot(v.x - j.x, v.y - j.y)) : null, ligne: L.Histoire.ligneObjectif() };
        // 2. On le rattrape : cabossé à mort, il s'arrête, et un Cravate en descend avec la caisse.
        o.frame(60);
        v.vie = Math.floor(v.vieMax * 0.4);
        o.frame(2);
        const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
        out.caisse = { tombe: !!B.mission.fuyardTombe, porteur: !!porteur, etat: porteur ? porteur.etat : null, etape: etape(L) };
        ici(L, { x: porteur.x - 20, y: porteur.y });
        L.Entites.assommer(porteur);
        o.frame(2);
        const c = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
        out.caisse.parTerre = !!c;
        ici(L, c);
        pas(L, o);
        out.semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        // 3. Semée.
        B.recherche.etoiles = 0; B.recherche.vu = 0;
        const cantine = pas(L, o);
        out.cantine = { etape: etape(L), pendant: cantine, ligne: L.Histoire.ligneObjectif(),
                        loin: Math.round(Math.hypot(L.Histoire.lieu('cantine').x - L.Histoire.lieu('bar').x,
                                                    L.Histoire.lieu('cantine').y - L.Histoire.lieu('bar').y) / L.TT) };
        // 4. Derrière la cantine.
        ici(L, L.Histoire.lieu('cantine'));
        const soeur = pas(L, o);
        out.planque = { etape: etape(L), pendant: soeur };
        // 5. La planque.
        ici(L, L.Histoire.lieu('planque'));
        finir(L, o);
        out.fait = !!B.partie.missionsFaites.m5; out.bar = !!B.partie.proprietes.bar;
        out.argent = argent.map(function (a) { return a.montant; });
        return out;
    }""")
    assert r["parle"] is True and r["slug"] == "m5", r
    assert r["chef"]["etape"] == 1 and r["chef"]["pendant"]["qui"] == "josee", r["chef"]
    f = r["fuyard"]
    assert f["etape"] == 2 and f["ligne"].startswith("RATTRAPE LA CAISSE"), f
    assert f["pendant"] and f["pendant"]["qui"] == "josee" and f["pendant"]["telephone"] is True, f
    assert f["char"] == "auto" and f["file"] is True and f["d"] < 250, f"le trésorier file en char, d'à côté ({f})"
    k = r["caisse"]
    assert k["tombe"] and k["porteur"] and k["etat"] == "fuit" and k["etape"] == 2, k
    assert k["parTerre"], "couché, le porteur lâche la caisse"
    assert r["semer"] == {"etape": 3, "etoiles": 3}, "la caisse ramassée, la police"
    c = r["cantine"]
    assert c["etape"] == 4 and c["ligne"].startswith("CACHE LA CAISSE"), c
    assert c["pendant"] and c["pendant"]["qui"] == "josee", c
    assert c["loin"] >= 120, f"la cantine est à l'autre bout de la ville ({c['loin']} tuiles du bar)"
    assert r["planque"]["etape"] == 5 and r["planque"]["pendant"]["qui"] == "josee", r["planque"]
    assert r["fait"] is True and r["bar"] is True and r["argent"] == [800]


def test_m6_le_tour_du_proprietaire_le_pickpocket_le_piquet_puis_le_brouillard(banc):
    """Josée présente la ville : Ti-Paul (puis les poches de SON pickpocket, par-derrière), Lulu à la
    cantine, Raymonde (puis trois Boulonneux qui arrivent sur son piquet, poings nus), Ovila au phare
    (qui a vu une auto sans phares) — et on revient au Brouillard : 300 $ et quatre numéros."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur, M = L.Monde; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5']);
        const argent = paiements(L);
        function porte(lieu) { return M.carte.portes.find(function (p) { return p.lieu === lieu; }); }
        function serrer(slug) {
            const b = { avant: etape(L), rendu: L.Histoire.parler(slug), boite: boite(L) };
            fermer(L);
            b.pendant = pas(L, o);
            b.apres = etape(L);
            return b;
        }
        o.entrer(porte('bar'));
        const parle = L.Histoire.parler('josee');
        passer(L, o);
        pas(L, o, 5);
        const out = { parle: parle, slug: B.partie.mission && B.partie.mission.slug };
        o.sortir();
        // 0. Ti-Paul, dehors.
        const ti = L.Histoire.donneur('tipaul');
        ici(L, { x: ti.x - 16, y: ti.y });
        out.tipaul = serrer('tipaul');
        // 1. Son pickpocket, par-derrière (le patron de f07).
        const victime = B.mission.entites.find(function (e) { return e.pickpocket === true; });
        out.poches = { la: !!victime, argent: victime ? victime.argent : null, ligne: L.Histoire.ligneObjectif() };
        victime.angle = 0;
        j.x = victime.x - 12; j.y = victime.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
        out.poches.vole = L.Combat.pickpocket(j);
        out.poches.lulu = pas(L, o);
        out.poches.apres = etape(L);
        out.poches.vide = victime.argent;
        // 2. Lulu, dedans.
        o.entrer(porte('cantine'));
        out.lulu = serrer('lulu');
        o.sortir();
        // 3. Raymonde, dehors — puis les Boulonneux.
        const ray = L.Histoire.donneur('raymonde');
        ici(L, { x: ray.x - 16, y: ray.y });
        out.raymonde = serrer('raymonde');
        const trois = hommes(L, 4);
        out.piquet = { etape: etape(L), ligne: L.Histoire.ligneObjectif(),
                       arrivent: trois.map(function (h) { return { d: h.d, etat: h.e.etat, arme: h.e.arme || null, vie: h.e.vieMax, gang: h.e.gang }; }) };
        trois.forEach(function (h) { L.Entites.assommer(h.e); });
        out.piquet.pendant = pas(L, o);
        out.piquet.apres = etape(L);
        // 5. Ovila, dedans, au phare — à l'autre bout de la ville.
        o.entrer(porte('phare'));
        out.ovila = serrer('ovila');
        o.sortir();
        out.ligneRetour = L.Histoire.ligneObjectif();
        const phare = L.Histoire.lieu('phare'), bar = L.Histoire.lieu('bar');
        out.loin = Math.round(Math.hypot(phare.x - bar.x, phare.y - bar.y) / L.TT);
        // 6. Le Brouillard.
        ici(L, bar);
        finir(L, o);
        out.fait = !!B.partie.missionsFaites.m6;
        out.argent = argent.map(function (a) { return a.montant; });
        return out;
    }""")
    assert r["parle"] is True and r["slug"] == "m6", r
    t = r["tipaul"]
    assert t["rendu"] and t["boite"]["partie"] == "accueil" and t["boite"]["qui"] == "tipaul", t
    assert t["avant"] == 0 and t["apres"] == 1, t
    assert t["pendant"] and t["pendant"]["qui"] == "tipaul" and t["pendant"]["telephone"] is False, t
    p = r["poches"]
    assert p["la"] and p["argent"] > 0 and p["ligne"].startswith("VIDE LES POCHES DU PICKPOCKET"), p
    assert p["vole"] is True and p["vide"] == 0 and p["apres"] == 2, p
    assert p["lulu"] and p["lulu"]["qui"] == "tipaul", p
    lu = r["lulu"]
    assert lu["boite"]["qui"] == "lulu" and lu["avant"] == 2 and lu["apres"] == 3, lu
    ra = r["raymonde"]
    assert ra["boite"]["qui"] == "raymonde" and ra["avant"] == 3 and ra["apres"] == 4, ra
    assert ra["pendant"] and ra["pendant"]["qui"] == "raymonde" and ra["pendant"]["telephone"] is False, ra
    q = r["piquet"]
    assert q["etape"] == 4 and q["ligne"].startswith("REPOUSSE LES BOULONNEUX"), q
    assert len(q["arrivent"]) == 3, q
    for h in q["arrivent"]:
        assert 100 <= h["d"] <= 260 and h["etat"] == "attaque_joueur", f"ils arrivent de loin, sur nous ({h})"
        assert h["arme"] is None and h["vie"] == 80, "les poings nus"
    assert q["apres"] == 5 and q["pendant"] and q["pendant"]["qui"] == "raymonde", q
    ov = r["ovila"]
    assert ov["boite"]["qui"] == "ovila" and ov["avant"] == 5 and ov["apres"] == 6, ov
    assert ov["pendant"] and ov["pendant"]["qui"] == "ovila", ov
    assert r["ligneRetour"].startswith("RETOURNE AU BROUILLARD")
    assert r["loin"] >= 200, f"du phare au Brouillard, l'autre bout de la ville ({r['loin']} tuiles)"
    assert r["fait"] is True and r["argent"] == [p["argent"], 300], "les poches du pickpocket, puis la prime"


def test_m97_marco_te_vend_les_chiens_le_phare_le_taxi_puis_marco_en_personne(banc):
    """Marco, au garage : « Tiens, les voilà » — quatre Cravates arrivent de loin dès la fin de l'intro (le
    « Rien de personnel » de Marco est le `pendant` de l'objectif 0 : pas encore dit après une intro, ce
    juge ne l'attend pas) ; couchés, cinq
    étoiles ; semées, Ovila appelle du phare (il se nomme : sa première réplique de la mission) ; au
    phare, le taxi repart, on le rattrape, on reprend la caisse ; puis on retourne voir Marco, et la
    fin se dit DEVANT lui."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        // m97 exige la fin de l'arc F (f12, Martin, 29 sept. 2026).
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm50', 'f01', 'f02', 'f03', 'f06', 'f08', 'f09', 'f10', 'f12']);
        // `exige: {liberes: 3}` : trois districts libérés (la forme de `tenirExige`, test_missions_en_scene_js).
        B.partie.libere = ((L.Monde.carte.def && L.Monde.carte.def.districts) || []).map(function (q) { return q.slug; }).slice(0, 3);
        const argent = paiements(L);
        const marco = L.Histoire.donneur('marco');
        ici(L, { x: marco.x - 16, y: marco.y });
        const parle = L.Histoire.parler('marco');
        passer(L, o);
        const out = { parle: parle, slug: B.partie.mission && B.partie.mission.slug };
        // 0. Les chiens de Bouchard arrivent.
        pas(L, o, 5);
        const quatre = hommes(L, 0);
        out.chiens = { etape: etape(L), ligne: L.Histoire.ligneObjectif(),
                       arrivent: quatre.map(function (h) { return { d: h.d, etat: h.e.etat }; }) };
        quatre.forEach(function (h) { L.Entites.assommer(h.e); });
        const cours = pas(L, o);
        out.semer = { etape: etape(L), etoiles: B.recherche.etoiles, pendant: cours };
        // 2. Semée.
        B.recherche.etoiles = 0; B.recherche.vu = 0;
        const ovila = pas(L, o);
        out.phare = { etape: etape(L), pendant: ovila, ligne: L.Histoire.ligneObjectif(),
                      texte: L.B.defs.missions.find(function (m) { return m.slug === 'm97'; }).dialogue.pendant
                          .filter(function (l) { return l.qui === 'ovila'; }).map(function (l) { return l.texte; }) };
        // 3. Au phare, à l'autre bout de la ville.
        const phare = L.Histoire.lieu('phare'), garage = L.Histoire.lieu('garage');
        out.loin = Math.round(Math.hypot(phare.x - garage.x, phare.y - garage.y) / L.TT);
        ici(L, phare);
        const repart = pas(L, o);
        const v = B.mission.fuyard;
        out.taxi = { etape: etape(L), pendant: repart, char: v ? v.slug : null, file: v ? v.fuite : null,
                     d: v ? Math.round(Math.hypot(v.x - j.x, v.y - j.y)) : null };
        // 4. On le rattrape, on reprend la caisse.
        o.frame(60);
        v.vie = Math.floor(v.vieMax * 0.4);
        o.frame(2);
        const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
        ici(L, { x: porteur.x - 20, y: porteur.y });
        L.Entites.assommer(porteur);
        o.frame(2);
        const c = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
        ici(L, c);
        const garageDit = pas(L, o);
        out.retour = { etape: etape(L), pendant: garageDit, ligne: L.Histoire.ligneObjectif() };
        // 5. Devant Marco.
        const m2 = L.Histoire.donneur('marco');
        ici(L, { x: m2.x - 16, y: m2.y });
        const fin = [];
        for (let k = 0; k < 400 && B.partie.mission; k++) o.frame(1);
        for (let n = 0; (B.scene || B.cinema) && n < 6000; n++) {
            o.frame(1);
            const b = boite(L);
            if (b && (!fin.length || fin[fin.length - 1].slug !== b.slug)) fin.push(b);
            if (B.cinema && n % 30 === 0) L.Histoire.suivante();
        }
        out.fin = fin;
        out.fait = !!B.partie.missionsFaites.m97;
        out.argent = argent.map(function (a) { return a.montant; });
        return out;
    }""")
    assert r["parle"] is True and r["slug"] == "m97", r
    c = r["chiens"]
    assert c["etape"] == 0 and c["ligne"].startswith("COUCHE LES CHIENS"), c
    assert len(c["arrivent"]) == 4, c
    for h in c["arrivent"]:
        assert 100 <= h["d"] <= 260 and h["etat"] == "attaque_joueur", f"ils arrivent de loin, sur nous ({h})"
    s = r["semer"]
    assert s["etape"] == 1 and s["etoiles"] == 5 and s["pendant"] and s["pendant"]["qui"] == "marco", s
    p = r["phare"]
    assert p["etape"] == 2 and p["ligne"].startswith("VA AU PHARE"), p
    assert p["pendant"] and p["pendant"]["qui"] == "ovila" and p["pendant"]["telephone"] is True, p
    assert "Ovila" in p["texte"][0], "sa première réplique de la mission le nomme"
    assert r["loin"] >= 200, f"le phare est à l'autre bout de la ville ({r['loin']} tuiles du garage)"
    t = r["taxi"]
    assert t["etape"] == 3 and t["char"] == "taxi" and t["file"] is True and t["d"] < 250, t
    assert t["pendant"] and t["pendant"]["qui"] == "ovila", t
    rt = r["retour"]
    assert rt["etape"] == 4 and rt["ligne"].startswith("RETOURNE RÉGLER ÇA AVEC MARCO"), rt
    assert rt["pendant"] and rt["pendant"]["qui"] == "marco" and rt["pendant"]["telephone"] is True, rt
    assert [b["qui"] for b in r["fin"]] == ["marco"] * 3, r["fin"]
    assert not any(b["telephone"] for b in r["fin"]), f"la fin se dit devant lui : {r['fin']}"
    assert r["fait"] is True and r["argent"] == [150]
