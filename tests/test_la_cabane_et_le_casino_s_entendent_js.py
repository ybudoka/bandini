"""La cabane et le casino s'entendent, au banc (docs/jalons/la-cabane-et-le-casino-s-entendent.md) : le
violoneux de la cabane, la calèche qu'on entend rouler et ses chevaux qui hennissent quand on monte,
l'évaporateur qui bout au temps des sucres ; la salle du Dragon d'or, sa musique, la machine à sous qui sonne
son bras et ses gains, le vidéopoker qui donne. Chaque son est ÉCOUTÉ par un espion posé sur `Son.SFX`."""

from app import audio, musique

ESPION = """
  const TT = 16;
  function espion(L) {
    const appels = [];
    Object.keys(L.Son.SFX).forEach(function (nom) {
      const vrai = L.Son.SFX[nom];
      L.Son.SFX[nom] = function () { appels.push([nom].concat(Array.from(arguments))); return vrai.apply(null, arguments); };
    });
    return appels;
  }
  function derniers(appels, nom) { return appels.filter(function (a) { return a[0] === nom; }); }
  function dernier(appels, nom) { const l = derniers(appels, nom); return l.length ? l[l.length - 1][1] : null; }
"""

RANG = """
  async function laisserArriver(L, o) { for (let i = 0; i < 6; i++) { o.frame(1); await o.attendre(); } }
  async function auRang(L, o, jour, heure) {
    const B = L.B, j = B.joueur, p = B.defs.blocs.find(function (b) { return b.slug === 'rang'; }).passage;
    B.partie.jour = jour; B.partie.heure = heure / 24;
    if (B.menu) L.Hud.fermerMenu();
    j.x = TT + 8; j.y = (p.de + 1) * TT + 8; L.Entites.indexer();
    await laisserArriver(L, o);
    o.touche('KeyA');
    for (let i = 0; i < 120 && !B.transition; i++) o.frame(1);
    o.relacher('KeyA');
    for (let i = 0; i < 100; i++) o.frame(1);
    await laisserArriver(L, o);
    for (let i = 0; i < 20; i++) o.frame(1);
    if (B.menu) L.Hud.fermerMenu();
  }
  function poser(L, x, y) { const j = L.B.joueur; j.x = x; j.y = y; j.vx = 0; j.vy = 0; L.Entites.indexer(); }
"""

DEDANS = """
  function dedans(L, o, lieu, point) {
    const B = L.B, j = B.joueur, M = L.Monde;
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === lieu && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    const pt = B.interieur.points.find(function (q) { return q.type === point; });
    j.x = pt.x * 16 + 8; j.y = (pt.y + 1) * 16 + 8; j.angle = -Math.PI / 2; L.Entites.indexer();
    o.frame(2);
    return pt;
  }
"""


def test_les_recettes_sont_la_et_le_violoneux_ne_joue_pas_dans_la_rue():
    for slug in ("caleche", "hennissement", "evaporateur", "casino_salle", "bras_machine", "gain_machine",
                 "jackpot", "videopoker_donne", "roulette_bille", "cartes_donnees", "jetons", "des_sic_bo"):
        e = audio.par_slug(slug)
        assert e, f"{slug} : pas de recette"
        assert audio.chemin(e, 1).exists(), f"{slug} : pas de fichier"
    for slug in ("caleche", "evaporateur", "casino_salle"):
        assert audio.par_slug(slug)["boucle"], f"{slug} doit boucler : il se tient à la distance"
    for slug in ("cabane_violon", "com_casino"):
        assert audio.piece_par_slug(slug) and audio.chemin_musique(slug).exists(), slug
        assert any(m["slug"] == slug for m in musique.exporter()), f"{slug} : pas de filet en notes"
    # Le violoneux joue À LA CABANE : un guitariste du Faubourg ne tombe jamais sur sa toune.
    assert "cabane_violon" not in [s["slug"] for s in musique.RUE]
    assert musique.MUSIQUES_DE_COMMERCE["nord_casino"] == "com_casino"


def test_la_caleche_s_entend_rouler_et_les_chevaux_hennissent_quand_on_monte(banc):
    r = banc("async function (L, o) {" + ESPION + RANG + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cabane;
        await auRang(L, o, 12, 13);
        const appels = espion(L);
        const c0 = C.caleche();
        // Arrêtée à son arrêt, tout près : on ne l'entend pas rouler.
        poser(L, c0.x + C.CAISSE.l + 10, c0.y);
        o.frame(1);
        const arretee = dernier(appels, 'caleche');
        o.tape('KeyE', 1);
        const hennit = derniers(appels, 'hennissement').length;
        let aBordMax = 0;
        for (let k = 0; k < 200 && B.joueur.manege; k++) { o.frame(1); if (C.caleche().roule) aBordMax = Math.max(aBordMax, dernier(appels, 'caleche')); }
        // Descendu de force, loin de la calèche qui roule : elle se tait à la distance.
        C.descendre(B.joueur, true);
        const c = C.caleche();
        poser(L, c.x + 2000, c.y);
        o.frame(2);
        const loin = dernier(appels, 'caleche');
        return { arretee: arretee, hennit: hennit, aBordMax: aBordMax, loin: loin };
    }""")
    assert r["arretee"] == 0, r
    assert r["hennit"] >= 1, "on monte dans la calèche sans que les chevaux s'entendent"
    assert r["aBordMax"] > 0.5, f"à bord, la calèche qui roule ne s'entend pas : {r}"
    assert r["loin"] == 0, r


def test_l_evaporateur_bout_au_temps_des_sucres_et_se_tait_l_hiver(banc):
    r = banc("async function (L, o) {" + ESPION + RANG + """
        L.Jeu.commencer();
        const B = L.B, C = L.Cabane;
        const vus = {};
        for (const jour of [12, 2]) {
          await auRang(L, o, jour, 13);
          const appels = espion(L);
          const porte = (L.Monde.carte.def.portes || []).find(function (p) { return p.lieu === 'cabane'; });
          poser(L, porte.x * TT + 8, (porte.y + 2) * TT + 8);
          o.frame(2);
          const pres = dernier(appels, 'evaporateur');
          poser(L, porte.x * TT + 8 - 400, (porte.y + 2) * TT + 8);
          o.frame(2);
          vus[jour] = { bout: C.onFaitBouillir(), pres: pres, loin: dernier(appels, 'evaporateur'),
                        toune: (C.gens().find(function (e) { return e.toune; }) || {}).toune || null };
          L.Jeu.retourTitre(); L.Jeu.commencer();
        }
        return vus;
    }""")
    printemps, hiver = r["12"], r["2"]
    assert printemps["bout"] and printemps["pres"] > 0.3, r
    assert printemps["loin"] == 0, r
    assert printemps["toune"] == "cabane_violon", f"le musicien de la cabane joue encore le reel du trottoir : {r}"
    assert not hiver["bout"] and hiver["pres"] == 0, r


def test_la_salle_du_casino_s_entend_dedans_et_se_tait_dehors(banc):
    r = banc("function (L, o) {" + ESPION + DEDANS + """
        L.Jeu.commencer();
        const B = L.B;
        const appels = espion(L);
        dedans(L, o, 'nord_casino', 'machine_a_sous');
        o.frame(2);
        const dans = dernier(appels, 'salle_du_casino');
        const musique = B.defs.audio.musiques_de_commerce.nord_casino;
        L.Jeu.quitterLaPiece(); o.fondu();
        for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
        o.frame(2);
        return { dans: dans, dehors: dernier(appels, 'salle_du_casino'), musique: musique };
    }""")
    assert r["dans"] == 1 and r["dehors"] == 0, r
    assert r["musique"] == "com_casino", r


def test_la_machine_a_sous_sonne_son_bras_et_ses_gains(banc):
    r = banc("function (L, o) {" + ESPION + DEDANS + """
        L.Jeu.commencer();
        const B = L.B, K = L.Casino;
        B.partie.argent = 100000;
        dedans(L, o, 'nord_casino', 'machine_a_sous');
        const appels = espion(L);
        const tours = [];
        for (let k = 0; k < K.regles().tours_par_jour; k++) {
          const avant = appels.length;
          if (!K.tirer()) break;
          const sons = appels.slice(avant).map(function (a) { return a[0]; });
          tours.push({ gain: B.machineASous.resultat.gain, sons: sons });
        }
        const v = appels.length;
        L.Missions.donnerAuVideopoker();
        const donne = appels.slice(v).map(function (a) { return a[0]; });
        return { tours: tours, donne: donne };
    }""")
    assert r["tours"], r
    for t in r["tours"]:
        assert "bras_machine" in t["sons"], t
        gagne = "gain_machine" in t["sons"] or "jackpot" in t["sons"]
        assert gagne == (t["gain"] > 0), f"un tour qui paie sonne son gain, un tour perdu non : {t}"
    assert any(t["gain"] > 0 for t in r["tours"]), "aucun tour gagnant : le juge n'a rien entendu sonner"
    assert "videopoker_donne" in r["donne"], r
