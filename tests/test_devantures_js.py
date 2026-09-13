"""Les devantures vues du jeu : elles se peignent, et elles se peignent ENTIERES.

⚠️ Le piege du decor en morceaux : la ville est peinte par carres de 16 tuiles,
mis en cache. Une enseigne de cinq tuiles peut tomber a cheval sur deux carres —
si on ne la range que dans le premier, elle est coupee net au milieu d'un mot.
"""


def test_le_paquet_porte_les_devantures(banc):
    r = banc("""function (L, o) {
        const c = L.B.defs.carte, d = L.B.defs.devantures;
        return { devantures: c.devantures.length, graffitis: c.graffitis.length,
                 genres: d.genres.length, couleurs: d.couleurs_tag.length,
                 premier: c.devantures[0] };
    }""")
    assert r["devantures"] >= 60
    assert r["graffitis"] >= 15
    assert r["genres"] >= 5
    assert r["couleurs"] >= 3
    for clef in ("x", "y", "l", "genre", "texte", "pancarte"):
        assert clef in r["premier"], r["premier"]


def test_chaque_devanture_est_rangee_dans_tous_ses_morceaux(banc):
    """⚠️ Le juge du debordement : une enseigne a cheval doit se retrouver dans
    les DEUX morceaux, sinon la moitie du nom manque."""
    r = banc("""function (L, o) {
        const carte = L.B.carte, MORCEAU = 16;
        let aCheval = 0, mal = 0;
        L.B.defs.carte.devantures.forEach(function (d) {
            const m0 = Math.floor(d.x / MORCEAU), m1 = Math.floor((d.x + d.l - 1) / MORCEAU);
            const r0 = Math.floor(d.y / MORCEAU), r1 = Math.floor((d.y + 1) / MORCEAU);
            if (m0 !== m1 || r0 !== r1) aCheval++;
            for (let my = r0; my <= r1; my++) {
                for (let mx = m0; mx <= m1; mx++) {
                    const liste = carte.devantures.get(mx + ',' + my) || [];
                    if (liste.indexOf(d) < 0) mal++;
                }
            }
        });
        return { aCheval: aCheval, mal: mal };
    }""")
    assert r["aCheval"] > 0, "aucune enseigne a cheval : le juge ne prouve rien"
    assert r["mal"] == 0, f"{r['mal']} morceaux oublient une enseigne qui les traverse"


def test_peindre_une_rue_commercante_ne_plante_pas(banc):
    """On se plante devant la plus large des enseignes et on laisse tourner :
    c'est le chemin qui peint le morceau, le texte et la pancarte."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = L.B.defs.carte.devantures.slice().sort(function (a, b) { return b.l - a.l; })[0];
        const j = L.B.joueur;
        j.x = (d.x + d.l / 2) * 16; j.y = (d.y + 3) * 16;
        L.Entites.indexer(); L.Monde.centrerCamera(j.x, j.y);
        const avant = L.B.stats.rects;
        o.frame(6);
        return { texte: d.texte, rects: L.B.stats.rects - avant,
                 morceaux: L.B.carte.morceaux.size, etat: L.B.etat };
    }""")
    assert r["etat"] == "jeu"
    assert r["morceaux"] > 0
    assert r["rects"] > 0, "rien n'a ete dessine"


def test_peindre_un_mur_tague_ne_plante_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const g = L.B.defs.carte.graffitis[0];
        const j = L.B.joueur;
        j.x = g.x * 16; j.y = (g.y + 3) * 16;
        L.Entites.indexer(); L.Monde.centrerCamera(j.x, j.y);
        o.frame(6);
        return { texte: g.texte, etat: L.B.etat, morceaux: L.B.carte.morceaux.size };
    }""")
    assert r["etat"] == "jeu"
    assert r["morceaux"] > 0
    assert r["texte"]


def test_les_vitrines_eclairent_la_nuit(banc):
    """Une lampe de vitrine est BASSE et COURTE : si elle portait aussi loin
    qu'un lampadaire, cent dix-huit d'entre elles noieraient la nuit."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const lampes = L.B.carte.lampes;
        const vitrines = lampes.filter(function (l) { return l.r < 44; });
        const lampadaires = lampes.filter(function (l) { return l.r === 44; });
        return { vitrines: vitrines.length, lampadaires: lampadaires.length,
                 rayonMax: Math.max.apply(null, vitrines.map(function (l) { return l.r; })),
                 couleur: vitrines[0] && vitrines[0].c };
    }""")
    assert r["vitrines"] >= 60, r
    assert r["lampadaires"] > 0
    assert r["rayonMax"] < 44, "une vitrine ne doit pas porter aussi loin qu'un lampadaire"
    assert "rgba" in (r["couleur"] or "")
