"""Trois défauts vus au banc en jouant les missions plus longues (25 sept. 2026)."""


def test_une_boutique_nommee_par_son_genre_a_sa_fleche(banc):
    """⚠️ Rouge avant : `boutique:artisan` cherchait « ARTISAN » dans le TEXTE des enseignes, où il
    n'est jamais — c'est le genre de la devanture (la quincaillerie). f04 et p01 n'avaient ni
    flèche ni coupe d'intro. La flèche mène à une devanture de CE genre, qu'on peut visiter."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const genres = L.B.defs.devantures.genres.map(function (g) { return g.slug; });
        const devs = L.Monde.carte.def.devantures, TT = 16;
        function vue(ou) {
            const p = L.Histoire.resoudre(ou, { donneur: 'ovila' });
            if (!p) return null;
            const d = devs.find(function (q) {
                return Math.abs((q.x + q.l / 2) * TT + 8 - p.x) < 1 && Math.abs((q.y + 1) * TT + 8 - p.y) < 1; });
            return { genre: d ? genres[d.genre] : null, porte: d ? d.porte : null };
        }
        return { artisan: vue('boutique:artisan'), industrie: vue('boutique:industrie'),
                 // Un mot pris dans une vraie enseigne : ce chemin-là marche encore.
                 texte: L.Histoire.resoudre('boutique:' + devs.find(function (q) { return q.texte; }).texte.split(' ')[0], {}) };
    }""")
    assert r["artisan"] == {"genre": "artisan", "porte": 1}, r
    assert r["industrie"] == {"genre": "industrie", "porte": 1}, r
    assert r["texte"] is not None, "un mot d'enseigne se trouve encore par son texte"


def test_acheter_ce_qu_on_a_deja_le_dit(banc):
    """⚠️ p01 demande d'acheter un bâton ; m2 l'a déjà donné, et le comptoir affiche « DÉJÀ À
    TOI ». L'étape passait sans un mot. Elle passe encore — on ne rachète pas ce qu'on a — mais
    le jeu le dit. Et acheter pour vrai ne le dit pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B;
        ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'].forEach(function (s) { B.partie.missionsFaites[s] = 1; });
        B.partie.armes.batte = { munitions: 0 };
        L.Histoire.commencer('p01');
        B.cinema = null; B.scene = null;
        for (let k = 0; k < 5; k++) o.frame(1);
        const deja = { etape: B.partie.mission.etape, msg: B.msg };
        B.msg = '';
        B.partie.armes.extincteur = { munitions: 100 };
        // La réplique PENDANT de l'étape neuve ouvre sa boîte : on la laisse se dire.
        for (let k = 0; k < 400 && B.partie.mission.etape === 1; k++) {
            if (B.cinema) L.Histoire.suivante();
            o.frame(1);
        }
        return { deja: deja, achat: { etape: B.partie.mission.etape, msg: B.msg } };
    }""")
    assert r["deja"]["etape"] == 1 and r["deja"]["msg"] == "DÉJÀ DANS TES POCHES", r
    assert r["achat"]["etape"] == 2 and r["achat"]["msg"] != "DÉJÀ DANS TES POCHES", r
