"""Les Galeries de la Baie, le centre d'achat hanté, au banc (docs/jalons/le-centre-d-achat-hante.md) : on y
entre par le bord ouest des Érables ; le jour, des gens et des comptoirs ; la nuit, personne — les lumières
s'éteignent une à une, la voix au haut-parleur sait où tu es, le gardien s'évanouit quand on approche, et
l'objet perdu du rayon 4 se rapporte une fois par nuit."""

from app.blocs import galeries

OUTILS = """
  const TT = 16;
  async function laisserArriver(L, o) { for (let i = 0; i < 6; i++) { o.frame(1); await o.attendre(); } }
  async function entrer(L, o, heure) {
    const B = L.B, j = B.joueur, p = B.defs.blocs.find(function (b) { return b.slug === 'galeries'; }).passage;
    B.partie.heure = heure / 24;
    if (B.menu) L.Hud.fermerMenu();
    j.x = TT + 8; j.y = (p.de + 2) * TT + 8; L.Entites.indexer();
    await laisserArriver(L, o);
    o.touche('KeyA');
    for (let i = 0; i < 120 && !B.transition; i++) o.frame(1);
    o.relacher('KeyA');
    for (let i = 0; i < 100; i++) o.frame(1);
    await laisserArriver(L, o);
    for (let i = 0; i < 20; i++) o.frame(1);
    const porte = L.Monde.carte.def.portes.find(function (q) { return q.interieur === 'galeries'; });
    if (!porte) return false;
    j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    return !!B.interieur;
  }
  function gens(L) { return L.B.entites.filter(function (e) { return e.type === 'pieton' && e !== L.B.joueur; }).length; }
  function aller(L, tx, ty) { const j = L.B.joueur; j.x = tx * TT + 8; j.y = ty * TT + 8; L.Entites.indexer(); }
"""


def test_le_jour_du_monde_la_nuit_personne(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        const jour = { entre: await entrer(L, o, 13), bloc: B.bloc && B.bloc.slug, piece: B.interieur && B.interieur.slug, gens: gens(L), visite: !!L.Galeries.visite };
        L.Jeu.sortir(); o.fondu(); for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
        const V = L.Son.Voix; V.demandees.length = 0;
        B.partie.heure = 23 / 24;
        const porte = L.Monde.carte.def.portes.find(function (q) { return q.interieur === 'galeries'; }), j = B.joueur;
        j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
        L.Jeu.entrer(porte); o.fondu(); for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
        o.frame(3);
        return { jour: jour, nuit: { gens: gens(L), visite: !!L.Galeries.visite, voix: V.demandees.slice() } };
    }""")
    j = r["jour"]
    assert j["entre"] and j["bloc"] == "galeries" and j["piece"] == "galeries", j
    assert j["gens"] >= 3 and not j["visite"], f"le jour, un centre d'achat ordinaire : {j}"
    n = r["nuit"]
    assert n["gens"] == 0 and n["visite"], f"la nuit, personne — et la hantise : {n}"
    assert "galeries-entree" in n["voix"], n


def test_les_lumieres_s_eteignent_une_a_une_et_la_voix_sait_ou_tu_es(banc):
    h = galeries.HANTISE
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, G = L.Galeries, V = L.Son.Voix;
        await entrer(L, o, 23);
        o.frame(2);
        const s = B.defs.galeries.hantise.lumiere_s * 60, eteintes = [];
        aller(L, 12, 6);
        for (let k = 0; k < 5; k++) { for (let i = 0; i < s; i++) o.frame(1); eteintes.push(G.visite.eteintes); }
        V.demandees.length = 0;
        aller(L, 15, 3); o.frame(2); aller(L, 9, 3); o.frame(2); aller(L, 2, 8); o.frame(2);
        return { eteintes: eteintes, voix: V.demandees.slice() };
    }""")
    assert r["eteintes"] == [1, 2, 3, 4, 4][: len(r["eteintes"])] and h["lumieres"] == 4, r
    for coin in ("fontaine", "escalier", "rayon"):
        assert f"galeries-{coin}" in r["voix"], (coin, r["voix"])


def test_le_gardien_s_evanouit_quand_on_approche_et_revient_ailleurs(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, G = L.Galeries, V = L.Son.Voix, h = B.defs.galeries.hantise;
        await entrer(L, o, 23);
        aller(L, 12, 6);
        for (let i = 0; i < h.lumiere_s * 60 * 2 + 10; i++) o.frame(1);
        const g1 = G.visite.gardien && { x: G.visite.gardien.x, y: G.visite.gardien.y };
        const loin = g1 ? Math.round(Math.hypot(g1.x - B.joueur.x, g1.y - B.joueur.y)) : 0;
        V.demandees.length = 0;
        B.joueur.x = g1.x + 10; B.joueur.y = g1.y; L.Entites.indexer(); o.frame(2);
        const parti = !G.visite.gardien, voix = V.demandees.slice();
        for (let i = 0; i < (h.gardien_revient_s + 1) * 60; i++) o.frame(1);
        const g2 = G.visite.gardien && { x: G.visite.gardien.x, y: G.visite.gardien.y };
        return { g1: g1, loin: loin, parti: parti, voix: voix, g2: g2, px: h.gardien_px };
    }""")
    assert r["g1"] and r["loin"] > r["px"] * 2, f"le gardien ne se montre pas, ou trop près : {r}"
    assert r["parti"] and "galeries-gardien" in r["voix"], r
    assert r["g2"] and r["g2"] != r["g1"], f"il ne revient pas, ou revient à la même place : {r}"


def test_l_objet_perdu_une_fois_par_nuit(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, o0 = { x: 2, y: 9 };
        await entrer(L, o, 23);
        o.frame(2);
        const argent = B.partie.argent;
        aller(L, o0.x, o0.y); o.frame(2); o.tape('KeyE', 1); o.frame(2);
        const premier = B.partie.argent - argent;
        o.tape('KeyE', 1); o.frame(2);
        const second = B.partie.argent - argent - premier;
        return { premier: premier, second: second };
    }""")
    assert r["premier"] == galeries.HANTISE["recompense"] and r["second"] == 0, r
