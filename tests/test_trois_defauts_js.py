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


def test_action_parle_a_la_personne_meme_avec_un_char_a_portee(banc):
    """Soupçonné au banc de q02 (22 sept. 2026) : « à 36 px d'un char, ACTION remonte dedans au lieu
    de parler ». Rejoué le 25 sept. : faux — la personne passe avant la portière (`Missions.interagir`
    d'abord, `vehicules.js` ensuite). Ce qui arrivait : le camion garé collé REPOUSSAIT le joueur hors
    de portée de voix. Ce juge tient l'ordre : le char ET Ti-Paul sous la main, c'est Ti-Paul."""
    r = banc("""function (L, o) {
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'].forEach(function (s) { B.partie.missionsFaites[s] = 1; });
        L.Histoire.commencer('q02'); B.cinema = null; B.scene = null;
        const v = B.mission.vehicule, ti = L.Histoire.donneur('tipaul');
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); o.frame(2);
        while (B.cinema) L.Histoire.suivante();
        // Garé juste derrière Ti-Paul, dans l'axe : on le regarde, lui ET le camion.
        v.x = ti.x + 12; v.y = ti.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); o.frame(1);
        L.Vehicules.descendre(j); L.Entites.indexer(); o.frame(2);
        j.x = ti.x - 20; j.y = ti.y; L.Entites.indexer();
        o.touche('KeyD'); o.frame(2); o.relacher('KeyD'); o.frame(1);
        const deux = { perso: !!L.Histoire.personnageSousLaMain(j), char: L.Vehicules.vehiculeSousLaMain(j) === v };
        o.tape('KeyE', 2); o.frame(2);
        const c = B.cinema;
        return { deux: deux, monte: j.dansVehicule === v, qui: c && c.lignes[c.i] ? c.lignes[c.i].qui : null };
    }""")
    assert r["deux"] == {"perso": True, "char": True}, f"le cas n'est pas posé : {r}"
    assert r["monte"] is False and r["qui"] == "tipaul", r
