"""Les arbres de rue : verts l'été, érables rouges, orange et jaunes l'automne (à l'empreinte de
leur tuile, sans dé), nus et poudrés l'hiver."""


def _cimes(banc, jour):
    return banc("""function (L) {
        L.Jeu.commencer(); L.B.partie.jour = %d; L.B.partie.heure = 0.5;
        const d = L.DECORS.arbre, out = [];
        for (let t = 0; t < d.variantes; t++) {
            const ctx = L.Base.nouveauCanvas(d.w, d.h).getContext('2d'); ctx.traces = [];
            d.peindre(ctx, d.w, d.h, t); out.push(ctx.traces.map(function (x) { return x[4]; }));
        }
        return out;
    }""" % jour)


def test_trois_teintes_d_erable_en_octobre(banc):
    oct_ = _cimes(banc, 32)
    assert len(oct_) == 3 and len({c[1] for c in oct_}) == 3, "les trois arbres d'octobre ont la même couleur"
    assert "#b8321f" in oct_[0]


def test_l_arbre_est_nu_et_poudre_en_janvier(banc):
    jan = _cimes(banc, 2)
    toutes = {c for t in jan for c in t}
    assert not toutes & {"#2f6b2a", "#b8321f", "#7a4a26"}, "une cime en janvier"
    assert "#eef2f6" in toutes, "pas de neige sur les branches"


def test_l_ete_garde_l_arbre_d_avant(banc):
    ete = _cimes(banc, 21)
    assert ete[0][:2] == ["#5a3a1a", "#2f6b2a"]


def test_la_teinte_ne_tire_aucun_de(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const arbres = L.B.entites.filter(function (e) { return e.decor === 'arbre'; });
        return Array.from(new Set(arbres.map(function (e) { return e.v; }))).sort();
    }""")
    assert r == [0, 1, 2], "les trois teintes ne sont pas toutes en ville"


def test_les_teintes_ne_deplacent_rien(banc):
    """La teinte vient de l'empreinte de la tuile (`creerDecor`, `hash2`) : avec ou sans elle, les
    mêmes entités aux mêmes numéros, aux mêmes places. ⚠️ Deux bancs : les numéros sont un compteur
    global, deux parties dans le même banc ne se comparent pas."""
    ville = """function (L) {
        const d = L.DECORS.arbre, n = d.variantes;
        if (%s) delete d.variantes;
        L.Jeu.commencer();
        return { n: n, e: L.B.entites.map(function (e) { return [e.id, e.type, Math.round(e.x), Math.round(e.y)]; }) };
    }"""
    avec, sans = banc(ville % "false"), banc(ville % "true")
    assert avec["n"] == 3 and len(avec["e"]) > 1000
    assert avec["e"] == sans["e"], "les teintes des arbres déplacent la ville"
