"""Un char qui coule pour vrai (docs/jalons/un-char-qui-coule-pour-vrai.md).

_Martin (30 sept. 2026) :_ « améliore l'animation des véhicules qui coulent ». Le char restait
entier, en pleines couleurs, pendant trois secondes, puis disparaissait d'un coup : le dessin ne
lisait jamais `v.coule`. Tranché : il s'enfonce peu à peu, le nez en premier, des ronds dans
l'eau et un gros glouglou, une tache d'huile qui reste.

⚠️ Ce qui se juge ici, c'est la MÉCANIQUE du dessin (l'état du naufrage, la trace au fond, le
hasard intact) ; l'œil, lui, se juge sur une capture Chromium.
"""

from test_eau_son_js import RIVE

#: Un char posé dans la baie, à quatre tuiles de la rive, et le joueur sur la rive à côté.
#: ⚠️ Le joueur tout près : loin, `peupler` oublierait le char avant qu'il coule.
AU_BORD = """
        L.Jeu.commencer();
        L.graine(31);
        const j = L.B.joueur, c = L.Monde.carte, TT = L.TT;
        """ + RIVE + """
        j.x = rive.x * TT + 8; j.y = rive.y * TT + 8;
        const v = L.Vehicules.creer('auto', (rive.x + 4) * TT + 8, rive.y * TT + 8, 0, { etat: 'stationne' });
        L.Entites.indexer();
        L.Monde.centrerCamera(v.x, v.y);
"""


def test_le_nez_plonge_avant_l_arriere(banc):
    """La ligne de flottaison court de l'avant vers l'arrière : ce qui est devant est sous l'eau.
    Le char pâlit, rapetisse et perd son ombre ; hors de l'eau, rien du tout."""
    r = banc("""function (L, o) {
        """ + AU_BORD + """
        const duree = L.B.defs.recherche.nage.coule_s * 60, out = { sec: L.Naufrage.etat(v) };
        out.etats = [0.05, 0.3, 0.6, 0.85, 0.99].map(function (u) {
            v.coule = Math.max(1, Math.round(u * duree));
            return L.Naufrage.etat(v);
        });
        out.longueur = v.def.longueur;
        return out;
    }""")
    assert r["sec"] is None, f"un char au sec a un état de naufrage : {r['sec']}"
    e, demi = r["etats"], r["longueur"] / 2
    lignes = [x["ligne"] for x in e]
    assert lignes == sorted(lignes, reverse=True), f"la ligne ne recule pas vers l'arrière : {lignes}"
    assert demi * 0.5 < lignes[0] <= demi, f"au début, seul le nez est sous l'eau : {lignes[0]} (demi {demi})"
    assert lignes[-1] <= -demi, f"à la fin, tout le char est sous l'eau : {lignes[-1]}"
    for cle in ("echelle", "dessus", "dessous", "ombre"):
        suite = [x[cle] for x in e]
        assert suite == sorted(suite, reverse=True), f"{cle} ne décroît pas : {suite}"
    assert e[0]["dessus"] > 0.9 and e[0]["echelle"] > 0.97, f"il commence à peine : {e[0]}"
    assert all(x["dessous"] < x["dessus"] for x in e), "le dessous de l'eau est plus net que le dessus"
    assert e[-1]["dessous"] < 0.05, f"au fond, on le voit encore : {e[-1]}"
    assert e[1]["ombre"] < 0.3, f"l'ombre reste sur l'eau : {e[1]}"


def test_au_fond_une_tache_d_huile_qui_s_efface(banc):
    """Au fond : une trace de naufrage, là où il a coulé, qui s'efface d'elle-même ; rien dans
    une nouvelle partie."""
    r = banc("""function (L, o) {
        """ + AU_BORD + """
        const out = { avant: L.Naufrage.traces().length };
        let sombre = -1;
        for (let i = 0; i < 400 && sombre < 0; i++) { o.frame(1); if (L.B.entites.indexOf(v) < 0) sombre = i; }
        out.sombre = sombre;
        const t = L.Naufrage.traces();
        out.apres = t.length;
        out.ecart = t.length ? Math.round(Math.hypot(t[0].x - v.x, t[0].y - v.y)) : -1;
        // L'image du fond se dessine sans broncher, la bulle et la tache comprises.
        L.Jeu.rendre();
        out.dessinees = L.Naufrage.dessinerSol(o.ctx, L.B.cam);
        for (let i = 0; i < L.Naufrage.DUREE + 5; i++) o.frame(1);
        out.plusTard = L.Naufrage.traces().length;
        return out;
    }""")
    assert r["avant"] == 0, "une trace de naufrage avant tout naufrage"
    assert r["sombre"] >= 170, f"le char n'a pas coulé : le juge ne prouve rien ({r['sombre']})"
    assert r["apres"] == 1, f"au fond, pas de trace de naufrage : {r['apres']}"
    assert r["ecart"] <= 2, f"la tache n'est pas là où il a coulé : {r['ecart']} px"
    assert r["dessinees"] == 1, f"la tache à l'écran ne se dessine pas : {r['dessinees']}"
    assert r["plusTard"] == 0, f"la tache ne s'efface jamais : {r['plusTard']}"


def test_la_tache_reste_dehors(banc):
    """Une tache dans la ville ne se dessine pas dans une pièce, et une nouvelle partie l'oublie."""
    r = banc("""function (L, o) {
        """ + AU_BORD + """
        L.Naufrage.poser(v);
        const out = { dehors: L.Naufrage.dessinerSol(o.ctx, L.B.cam) };
        L.B.interieur = { id: 'banc' };
        out.dedans = L.Naufrage.dessinerSol(o.ctx, L.B.cam);
        L.B.interieur = null;
        L.Jeu.commencer();
        out.partieNeuve = L.Naufrage.traces().length;
        return out;
    }""")
    assert r["dehors"] == 1, f"le juge ne prouve rien : la tache ne se dessine pas dehors ({r['dehors']})"
    assert r["dedans"] == 0, "la tache de la baie se dessine dans une pièce"
    assert r["partieNeuve"] == 0, "une nouvelle partie hérite de la tache d'huile"


def test_couler_ne_tire_aucun_de_de_plus(banc):
    """⚠️ Le dessin du naufrage et sa trace se tirent à l'empreinte : le même naufrage, dessin
    compris, tire exactement les mêmes dés du jeu, le module coupé ou non. Un banc neuf de
    chaque côté : une deuxième partie dans le même banc ne part pas du même état."""
    def tirages(coupe):
        return banc("""function (L, o) {
            """ + AU_BORD + """
            L.Naufrage.couper(""" + ("true" if coupe else "false") + """);
            const vrai = L.B.rng;
            let n = 0;
            L.B.rng = function () { n++; return vrai(); };
            let sombre = -1;
            for (let i = 0; i < 400 && sombre < 0; i++) {
                o.frame(1); L.Jeu.rendre();
                if (L.B.entites.indexOf(v) < 0) sombre = i;
            }
            for (let i = 0; i < 60; i++) { o.frame(1); L.Jeu.rendre(); }
            return { n: n, sombre: sombre, traces: L.Naufrage.traces().length };
        }""")
    coupe, vrai = tirages(True), tirages(False)
    assert vrai["traces"] == 1 and coupe["traces"] == 0, f"la coupure ne coupe rien : {coupe} {vrai}"
    assert vrai["sombre"] == coupe["sombre"], f"le char ne coule plus à la même image : {coupe} {vrai}"
    assert vrai["n"] == coupe["n"], f"le naufrage tire des dés du jeu : {coupe} {vrai}"
