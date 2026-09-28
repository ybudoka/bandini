"""Des statues dans les parcs, côté navigateur : on les voit, on s'y cogne, on lit leur plaque.

⚠️ La plaque se juge PAR LE BOUTON (`o.tape('KeyE')`), comme les autres gestes du décor
(`test_interactions_js.py`) : la chaîne d'ACTION affame ce qui la suit.
"""

import json

from app import interactions, statues

TYPES = list(statues.TYPES)


def test_chaque_statue_se_peint_et_prend_son_numero_a_part(banc):
    """⚠️ Posées sur la ville finie, elles naissent au démarrage : sans `horsSuite`, chacune décalerait d'un
    cran le numéro de tout ce qui naît après elle — passants, chars, la cadence de la police."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const types = %s, res = {};
        for (const t of types) {
            const f = L.DECORS[t];
            if (!f) { res[t] = { fiche: false }; continue; }
            const c = L.Atlas.cuirePeintre('decor|' + t, f.w, f.h, f.peindre);
            const ids = L.B.entites.filter(function (e) { return e.type === 'decor' && e.decor === t; })
                                   .map(function (e) { return e.id; });
            res[t] = { fiche: true, solide: !!f.solide, arrete: f.arrete || 0, largeur: c.width, ids: ids };
        }
        return res;
    }""" % json.dumps(TYPES))
    for t in TYPES:
        assert r[t]["fiche"], f"{t} n'a pas de dessin"
        assert r[t]["solide"] and r[t]["arrete"] > 0, f"{t} ne s'arrête pas : on traverserait le bronze"
        assert r[t]["largeur"] > 0
        assert r[t]["ids"], f"aucun {t} dans la ville"
        assert all(i >= 1e9 for i in r[t]["ids"]), f"{t} prend un numéro dans la suite de la ville : {r[t]['ids']}"


def test_on_lit_la_plaque_une_ligne_par_pression_et_on_recommence(banc):
    c = interactions.LIRE
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, res = {};
        function nettoyer() {
            for (const e of L.Entites.autour(j.x, j.y, 100, function (q) { return q.type === 'pieton' || q.type === 'vehicule'; })) L.Entites.retirer(e);
            L.Entites.indexer();
        }
        function suivant() { const t = L.B.t; for (let k = 0; k < 6 && L.B.t === t; k++) o.frame(1); nettoyer(); }
        for (const t of %s) {
            const d = L.B.entites.find(function (e) { return e.type === 'decor' && e.decor === t; });
            if (!d) { res[t] = null; continue; }
            j.x = d.x; j.y = d.y + 18; j.vx = 0; j.vy = 0; j.roule = 0;
            L.Monde.centrerCamera(j.x, j.y); nettoyer(); o.viser(d);
            L.Missions.majInvite(j);
            const lu = { invite: L.B.invite, lignes: [] };
            for (let k = 0; k < 5; k++) { o.tape('KeyE'); lu.lignes.push(L.B.msg); suivant(); }
            res[t] = lu;
        }
        return res;
    }""" % json.dumps(TYPES))
    for t in TYPES:
        plaque = c["plaques"][t]
        assert r[t], f"aucun {t} devant lequel se planter"
        assert r[t]["invite"] == c["invite"], f"devant {t}, l'invite dit « {r[t]['invite']} »"
        attendu = [plaque[k % len(plaque)] for k in range(5)]
        assert r[t]["lignes"] == attendu, f"{t} : {r[t]['lignes']}"


def test_chaque_ligne_de_plaque_tient_dans_le_toast(banc):
    """Le toast du HUD est une ligne à l'échelle 2, centrée, avec six pixels de marge de chaque côté
    (`Hud.dessinerMessage`) : une ligne plus large sortirait de l'écran."""
    lignes = [ligne for p in statues.exporter().values() for ligne in p]
    r = banc("""function (L, o) {
        return %s.map(function (l) { return { l: l, px: L.Atlas.largeurTexte(l, 2) + 12, ecran: L.VW }; });
    }""" % json.dumps(lignes, ensure_ascii=False))
    for m in r:
        assert m["px"] <= m["ecran"], f"« {m['l']} » fait {m['px']} px, l'écran {m['ecran']}"
