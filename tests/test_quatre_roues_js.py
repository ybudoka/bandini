"""Les 4 roues, au banc (docs/jalons/les-4-roues.md, vague 1) : la terre qui ralentit les chars et pas lui,
le choc qui éjecte d'une moto et pas d'un 4 roues, et les 4 roues des Friches qui naissent à l'approche sans
rien déplacer."""

TERRE = """
  function tuileDe(L, veutTerre) {
    const M = L.Monde, c = M.carte;
    for (let ty = 120; ty < c.h; ty++) for (let tx = 0; tx < c.w; tx++) {
      if (veutTerre ? M.estTerre(tx, ty) : M.estRoute(tx, ty)) return { x: tx * 16 + 8, y: ty * 16 + 8 };
    }
    return null;
  }
"""


def test_sur_la_terre_une_auto_ralentit_et_le_4_roues_non(banc):
    r = banc("function (L, o) {" + TERRE + """
        L.Jeu.commencer();
        const V = L.Vehicules, terre = tuileDe(L, true), route = tuileDe(L, false), out = {};
        for (const slug of ['auto', 'camion', 'moto', 'quatre_roues']) {
            const v = V.creer(slug, terre.x, terre.y, 0, { etat: 'stationne', couleur: '#ffffff' });
            out[slug] = { terre: V.allureDuSol(v) };
            v.x = route.x; v.y = route.y;
            out[slug].route = V.allureDuSol(v);
            L.Entites.retirer(v);
        }
        return out;
    }""")
    for slug in ("auto", "camion", "moto", "quatre_roues"):
        assert r[slug]["route"] == 1, r
    assert r["auto"]["terre"] < 0.8 and r["camion"]["terre"] < r["auto"]["terre"] < r["moto"]["terre"] < 1, r
    assert r["quatre_roues"]["terre"] == 1, r


def test_le_meme_choc_ejecte_de_la_moto_et_pas_du_4_roues(banc):
    """À 3,6 px par image dans une façade : le pilote de la moto vole (seuil de tout le monde, 2,6) ; celui du
    4 roues reste dessus (son seuil à lui)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, M = L.Monde, c = M.carte, j = B.joueur;
        let mur = null;
        for (let ty = 130; ty < c.h && !mur; ty++) for (let tx = 5; tx < c.w - 5 && !mur; tx++) {
            if (M.glyphe(tx, ty) === 'F' && M.estRoute(tx, ty + 2) && M.estRoute(tx, ty + 3) && !M.estRoute(tx, ty)) mur = { tx: tx, ty: ty };
        }
        const out = {};
        for (const slug of ['moto', 'quatre_roues']) {
            if (j.dansVehicule) L.Vehicules.descendre(j, true);
            j.intouchable = true;
            const v = L.Vehicules.creer(slug, mur.tx * 16 + 8, (mur.ty + 2) * 16 + 4, -Math.PI / 2,
                                        { etat: 'stationne', couleur: '#ffffff' });
            j.x = v.x + 10; j.y = v.y; L.Entites.indexer();
            L.Vehicules.monter(j, v); L.Entites.indexer();
            v.vitesse = 3.6;
            for (let k = 0; k < 20; k++) o.frame(1);
            out[slug] = { dedans: j.dansVehicule === v };
            if (j.dansVehicule) L.Vehicules.descendre(j, true);
            L.Entites.retirer(v);
        }
        return out;
    }""")
    assert r["moto"]["dedans"] is False, f"le témoin ne mord pas : la moto n'a pas éjecté {r}"
    assert r["quatre_roues"]["dedans"] is True, r


def test_les_4_roues_des_friches_naissent_a_l_approche_sans_rien_deplacer(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, Q = L.QuatreRoues, j = B.joueur;
        const au_demarrage = B.entites.filter(function (e) { return e.slug === 'quatre_roues'; }).length;
        const p = L.Monde.carte.def.quatre_roues[0];
        j.x = p.x * 16 + 8 + 380; j.y = p.y * 16 + 8; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        L.graine(5); const temoin = B.rng(); L.graine(5);
        B.t = 60 * Math.ceil(B.t / 60) + 23; Q.maj();
        const v = Q.la('friches:0');
        return { au_demarrage: au_demarrage, la: !!v, id: v ? v.id : 0, etat: v && v.etat, reste: v && v.resteGare,
                 tx: v ? Math.floor(v.x / 16) : null, ty: v ? Math.floor(v.y / 16) : null, p: p,
                 apres: B.rng(), temoin: temoin, deux: (Q.maj(), B.entites.filter(function (e) { return e.placeQuad === 'friches:0'; }).length) };
    }""")
    assert r["au_demarrage"] == 0, "un 4 roues au démarrage : le hasard du départ bouge"
    assert r["la"] and r["etat"] == "stationne" and r["reste"], r
    assert (r["tx"], r["ty"]) == (r["p"]["x"], r["p"]["y"]), r
    assert r["id"] >= 1e9, "il a pris un numéro de la suite de la ville"
    assert r["apres"] == r["temoin"], "sa naissance a tiré un dé du jeu"
    assert r["deux"] == 1, "un deuxième est né sur la même place"
