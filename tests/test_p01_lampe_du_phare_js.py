"""p01, « La lampe du phare » (Ovila), jouée de l'appel à la récompense — elle n'avait aucun juge
de banc. Allongée le 22 sept. 2026 (Martin : « des missions plus longues ») : un extincteur à
la Shop après le bâton, et les Skateux qui reviennent en bande au phare, une fois la lampe
calée. Chaque étape se joue : la marche jusqu'au phare suit la terre ferme, tuile par tuile."""

OUTILS = """
  function fermer(L) { let g = 0; while (L.B.cinema && g < 200) { L.Histoire.suivante(); g++; } }
  function passer(L, o) {
    let n = 0;
    while ((L.B.scene || L.B.cinema) && n < 6000) { o.frame(1); if (L.B.cinema && n % 30 === 0) L.Histoire.suivante(); n++; }
  }
  function etape(L) { return L.B.partie.mission ? L.B.partie.mission.etape : null; }
  function images(L, o, n) { for (let k = 0; k < n; k++) { o.frame(1); fermer(L); } }
  // À pied jusqu'à `cible`, par la terre ferme (4-voisins) : rend le nombre de tuiles, ou -1.
  function marcher(L, o, cible, rayon) {
    const j = L.B.joueur, W = L.Monde.carte.w, H = L.Monde.carte.h;
    const d = new Int32Array(W * H).fill(-1), sx = Math.floor(j.x / 16), sy = Math.floor(j.y / 16);
    const file = [sx + sy * W]; d[file[0]] = file[0];
    let but = -1;
    for (let k = 0; k < file.length && but < 0; k++) {
      const i = file[k], x = i % W, y = (i - x) / W;
      if (Math.hypot(x * 16 + 8 - cible.x, y * 16 + 8 - cible.y) < rayon) { but = i; break; }
      [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (s) {
        const nx = x + s[0], ny = y + s[1], q = nx + ny * W;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H || d[q] >= 0) return;
        if (L.Monde.estEau(nx, ny) || L.Monde.bloque(nx, ny, L.Monde.MASQUE_PIETON)) return;
        d[q] = i; file.push(q);
      });
    }
    if (but < 0) return -1;
    const pas = []; for (let c = but; c !== d[c]; c = d[c]) pas.push(c);
    pas.reverse();
    for (let k = 0; k < pas.length; k++) {
      const x = pas[k] % W; j.x = x * 16 + 8; j.y = (pas[k] - x) / W * 16 + 8; j.vx = 0; j.vy = 0;
      if (k % 4 === 3) { L.Entites.indexer(); o.frame(1); fermer(L); if (!L.B.partie.mission) break; }
    }
    L.Entites.indexer(); images(L, o, 3);
    return pas.length;
  }
  function coucher(L, o) {
    const e0 = etape(L);
    const eux = L.B.mission.entites.filter(function (e) { return e.cible && e.etape === e0 && e.vivant; });
    eux.forEach(function (e) { L.Entites.assommer(e); });
    images(L, o, 4);
    return eux.length;
  }
"""


def test_p01_le_baton_l_extincteur_le_skateux_le_phare_et_sa_bande(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'].forEach(function (s) { B.partie.missionsFaites[s] = 1; });
        B.partie.armes.batte = { mun: null };            // ce que m2 donne (`donne.arme`)
        const argent = [], vrai = L.Missions.encaisser;
        L.Missions.encaisser = function (montant) { argent.push(montant); return vrai.apply(null, arguments); };
        const vu = {};
        L.Histoire.commencer('p01'); passer(L, o); images(L, o, 3);
        vu.baton = etape(L);                                   // 1 : le bâton est déjà dans le sac
        vu.ligne = L.Histoire.ligneObjectif();
        B.partie.objets.cafe = true; images(L, o, 3);          // une bouchée ne compte pas
        vu.apresCafe = etape(L);
        L.Combat.ramasserArme('extincteur', 100); images(L, o, 3);   // ce que fait le comptoir
        vu.skateux = etape(L);                                 // 2 : le Skateux qui rôde
        vu.couche = coucher(L, o);
        vu.phare = etape(L);                                   // 3 : au phare, chrono
        const phare = L.Histoire.resoudre('phare', L.Histoire.courante());
        const t0 = B.t;
        vu.tuiles = marcher(L, o, phare, 5 * 16);
        vu.bande = etape(L);                                   // 4 : il revient avec ses amis
        vu.images = B.t - t0;
        const amis = B.mission.entites.filter(function (e) { return e.cible && e.etape === 4 && e.vivant; });
        vu.amisPres = amis.map(function (e) { return Math.round(Math.hypot(e.x - j.x, e.y - j.y)); });
        vu.couches = coucher(L, o);
        images(L, o, 60); passer(L, o);
        return { vu: vu, fait: !!B.partie.missionsFaites.p01, argent: argent, extincteur: !!B.partie.armes.extincteur,
                 mission: B.partie.mission, msg: B.msg };
    }""")
    vu = r["vu"]
    # ⚠️ m2 donne le bâton : pour qui a joué le tronc, l'objectif 0 est fait d'avance.
    assert vu["baton"] == 1 and vu["ligne"].startswith("ACHÈTE UN EXTINCTEUR"), r
    assert vu["apresCafe"] == 1, "une bouchée ne fait pas avancer `acheter`"
    assert vu["skateux"] == 2 and vu["couche"] == 1 and vu["phare"] == 3, r
    assert vu["tuiles"] > 0 and vu["bande"] == 4, "on n'arrive pas au phare à pied : %s" % r
    assert vu["couches"] == 3 and all(d < 16 * 16 for d in vu["amisPres"]), "la bande n'arrive pas au phare : %s" % r
    assert r["fait"] and r["argent"] == [100] and r["extincteur"], r
