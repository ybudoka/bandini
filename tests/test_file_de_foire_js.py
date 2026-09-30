"""La file pour entrer à la foire (`static/js/file_de_foire.js`) — docs/jalons/une-file-pour-entrer-a-la-foire.md.

Martin (30 sept. 2026) : « je veux une file de personnes qui attendent pour entrer à la foire quand c'est ouvert »,
« je veux que la clôture soit infranchissable », « mets aussi des câbles de gestion de file ». Tranché : la
longueur suit l'heure, la file avance (le premier paie et entre), un zigzag de câbles sur le trottoir, le joueur
peut couper et ça chiale sans étoile ; le grillage ne s'enjambe plus, l'arche se force encore.

⚠️ Chaque banc pose l'ÉTÉ (`jour = 22`, juillet — la foire ferme l'hiver) et garde le joueur en vie et sans
dette (les hommes de Sal, mémoire « un juge de couleur pose sa saison »).
"""

from app import audio

PRELUDE = """
    function preparer(L, o, heure) {
        L.Jeu.commencer();
        const p = L.B.partie;
        p.jour = 22; p.dette = 0; p.heure = heure / 24;
        L.B.joueur.invincible = 1e9;
        return L.Monde.carte.def.file_de_foire;
    }
    // Loin de l'arche, mais dans le rayon de la foire : le serpentin est hors de l'écran.
    function auLoin(L, f) {
        const j = L.B.joueur;
        j.x = (f.x + 2) * L.TT + 8; j.y = (f.y + 26) * L.TT + 8;
        L.Monde.majCamera && L.Monde.majCamera();
    }
    // Juste devant l'arche, sur le trottoir : on voit le serpentin.
    function devant(L, f) {
        const j = L.B.joueur;
        j.x = (f.x - 1) * L.TT + 8; j.y = (f.y + 3) * L.TT + 4;
        L.Monde.majCamera && L.Monde.majCamera();
    }
"""


def test_la_longueur_de_la_file_suit_l_heure(banc, paquet):
    """Une douzaine en fin d'après-midi, deux le matin, personne à 3 h — et on la trouve déjà là en arrivant."""
    fiche = paquet["carte"]["file_de_foire"]
    r = banc("""function (L, o) {
        %s
        const out = {};
        for (const h of [17, 9, 3, 13]) {
            const f = preparer(L, o, h);
            auLoin(L, f);
            o.frame(4);
            out[h] = { n: L.FileDeFoire.gens().length, voulus: L.FileDeFoire.voulus(),
                       capacite: L.FileDeFoire.capacite() };
        }
        return out;
    }""" % PRELUDE)
    par_heure = fiche["par_heure"]
    for h in (17, 9, 3, 13):
        assert r[str(h)]["voulus"] == min(par_heure[h], r[str(h)]["capacite"]), r
        assert r[str(h)]["n"] == r[str(h)]["voulus"], f"à {h} h : {r[str(h)]}"
    assert r["17"]["capacite"] >= max(par_heure), "le serpentin ne tient pas la file de pointe"
    assert r["17"]["n"] >= 10 and r["3"]["n"] == 0 and r["9"]["n"] == 2


def test_la_file_avance_la_tete_entre_et_devient_la_foule(banc):
    """Le premier passe l'arche et va flâner dans la foire ; un autre arrive au bout. Personne ne recule,
    personne ne se colle (10 px, `demeler`), personne ne sort du chemin — ni dans la rue."""
    r = banc("""function (L, o) {
        %s
        const f = preparer(L, o, 17);
        auLoin(L, f);
        o.frame(4);
        const avant = L.FileDeFoire.gens().slice();
        devant(L, f);
        const entres = [], problemes = [];
        let arrives = 0;
        const vus = new Set(avant.map(function (e) { return e.id; }));
        for (let i = 0; i < 1500; i++) {
            const s0 = new Map(L.FileDeFoire.gens().map(function (e) { return [e.id, e.fileS]; }));
            o.frame(1);
            const g = L.FileDeFoire.gens();
            g.forEach(function (e, k) {
                if (!vus.has(e.id)) { vus.add(e.id); arrives++; }
                if (s0.has(e.id) && e.fileS < s0.get(e.id) - 1e-6) problemes.push('recule ' + e.id);
                if (k > 0 && Math.hypot(e.x - g[k - 1].x, e.y - g[k - 1].y) < 10) problemes.push('colle ' + e.id);
                if (L.Monde.estRoute(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT))) problemes.push('rue ' + e.id);
            });
            avant.forEach(function (e) {
                if (e.foire && e.metier === 'forain' && entres.indexOf(e) < 0) entres.push(e);
            });
        }
        return { entres: entres.length, arrives: arrives, problemes: problemes.slice(0, 5),
                 dedans: entres.every(function (e) {
                     return L.Monde.dansLaFoire(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT)); }),
                 reste: L.FileDeFoire.gens().length };
    }""" % PRELUDE)
    assert r["entres"] >= 4, f"la tête n'entre pas : {r}"
    assert r["dedans"], "un de la file est « entré » sans être dans la foire"
    assert r["arrives"] >= 3, f"personne n'arrive au bout de la file : {r}"
    assert not r["problemes"], r["problemes"]
    assert r["reste"] >= 8, r


def test_le_serpentin_arrete_les_autres_et_laisse_l_arche_libre(banc):
    """Le zigzag de câbles se contourne (par la rue) : ses tuiles arrêtent un passant et un char. Les deux
    colonnes ouest de l'arche restent libres — c'est par là qu'on passe, et qu'on coupe la file."""
    r = banc("""function (L, o) {
        %s
        const f = preparer(L, o, 17);
        const M = L.Monde, b = M.barrieres().find(function (q) { return q.slug === 'foire'; });
        const bloque = [];
        for (let y = f.y; y < f.y + f.h; y++) for (let x = f.x; x < f.x + f.l; x++) {
            bloque.push(M.bloque(x, y, M.MASQUE_PIETON) && M.bloque(x, y, M.MASQUE_VEHICULE));
        }
        const libres = [];
        for (let x = b.x; x < f.x; x++) libres.push(!M.bloque(x, f.y, M.MASQUE_PIETON) && !M.bloque(x, f.y + 1, M.MASQUE_PIETON));
        return { bloque: bloque, libres: libres, colonne: f.x === b.x + b.l - 1,
                 cloture: bloque.length ? M.estCloture(f.x, f.y) : null, cables: L.FileDeFoire.cables().length };
    }""" % PRELUDE)
    assert all(r["bloque"]) and len(r["bloque"]) >= 6, r
    assert r["libres"] and all(r["libres"]), r
    assert r["colonne"], "la file ne sort pas par la colonne est de l'arche"
    assert r["cloture"] is False, "le serpentin se peindrait comme un grillage"
    assert r["cables"] >= 6


def test_couper_la_file_fait_chialer_sans_etoile(banc):
    """Le joueur passe l'arche devant tout le monde : quelqu'un de la file le lui dit, en bulle (et à voix
    haute), une réplique de la file — pas d'étoile, et pas deux fois de suite."""
    textes = {v["texte"] for v in audio.voix_de_la_file()}
    assert len(textes) == 6
    r = banc("""function (L, o) {
        %s
        const f = preparer(L, o, 17);
        auLoin(L, f);
        o.frame(4);
        const p = L.B.partie, j = L.B.joueur, b = L.Monde.barrieres().find(function (q) { return q.slug === 'foire'; });
        p.billets = { foire: p.jour };
        L.B.recherche.etoiles = 0;
        function passer() {
            for (let y = (b.y + 3) * L.TT + 8; y > (b.y - 2) * L.TT; y -= 2) {
                j.x = b.x * L.TT + 8; j.y = y; o.frame(1);
            }
        }
        passer();
        const bulles = L.FileDeFoire.gens().filter(function (e) { return e.bulle; }).map(function (e) { return e.bulle.texte; });
        // Ressortir et repasser tout de suite : elle ne rechiale pas.
        for (let y = (b.y - 2) * L.TT; y < (b.y + 3) * L.TT; y += 2) { j.y = y; o.frame(1); }
        L.FileDeFoire.gens().forEach(function (e) { e.bulle = null; });
        passer();
        const encore = L.FileDeFoire.gens().filter(function (e) { return e.bulle; }).length;
        return { bulles: bulles, etoiles: L.B.recherche.etoiles, encore: encore };
    }""" % PRELUDE)
    assert len(r["bulles"]) == 1, r
    assert r["bulles"][0] in textes, r
    assert r["etoiles"] == 0, "couper la file coûte une étoile"
    assert r["encore"] == 0, "la file chiale à chaque passage"


def test_la_file_se_vide_quand_on_s_en_va(banc):
    """Loin de la foire, plus de file : ceux qu'on ne voit pas s'en vont (rien ne s'accumule)."""
    r = banc("""function (L, o) {
        %s
        const f = preparer(L, o, 17);
        auLoin(L, f);
        o.frame(4);
        const n = L.FileDeFoire.gens().length;
        const j = L.B.joueur;
        j.y += 60 * L.TT;
        L.Monde.majCamera && L.Monde.majCamera();
        o.frame(3);
        return { n: n, apres: L.FileDeFoire.gens().length,
                 restes: L.B.entites.filter(function (e) { return e.enFile; }).length };
    }""" % PRELUDE)
    assert r["n"] > 0 and r["apres"] == 0 and r["restes"] == 0, r
