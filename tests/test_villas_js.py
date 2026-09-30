"""Le jardin de la villa, côté navigateur (docs/jalons/des-etages-pour-vrai-des-maisons-de-luxe-et-des-terrains-clotures.md,
vague 4) : la fontaine et les piliers du portail se peignent, arrêtent, et prennent leur numéro à part ; la piscine
creusée peint sa margelle au bord seulement, et sa bâche l'hiver."""

import json

JARDIN = ["fontaine_villa", "pilier_portail_o", "pilier_portail_e"]


def test_le_jardin_se_peint_arrete_et_prend_son_numero_a_part(banc):
    """⚠️ Posés sur la ville finie, ils naissent au démarrage : sans `horsSuite`, chacun décalerait d'un cran le
    numéro de tout ce qui naît après lui (la leçon des statues)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const res = {};
        for (const t of %s) {
            const f = L.DECORS[t];
            if (!f) { res[t] = { fiche: false }; continue; }
            const c = L.Atlas.cuirePeintre('decor|' + t, f.w, f.h, f.peindre);
            const ids = L.B.entites.filter(function (e) { return e.type === 'decor' && e.decor === t; })
                                   .map(function (e) { return e.id; });
            res[t] = { fiche: true, solide: !!f.solide, arrete: f.arrete || 0, largeur: c.width, ids: ids };
        }
        return res;
    }""" % json.dumps(JARDIN))
    for t in JARDIN:
        assert r[t]["fiche"], f"{t} n'a pas de dessin"
        assert r[t]["solide"] and r[t]["arrete"] > 0, f"{t} ne s'arrête pas : on traverserait la pierre"
        assert r[t]["largeur"] > 0
        assert r[t]["ids"], f"aucun {t} dans la ville"
        assert all(i >= 1e9 for i in r[t]["ids"]), f"{t} prend un numéro dans la suite de la ville : {r[t]['ids']}"


def test_la_piscine_creusee_peint_sa_margelle_au_bord_et_sa_bache_l_hiver(banc):
    r = banc("""function (L, o) {
        const MARGELLE = '#e3dfd3', res = {};
        function peindre(v, hiver) {
            const c = o.doc.createElement('canvas').getContext('2d');
            c.traces = [];
            const avant = L.Saisons.enHiver;
            L.Saisons.enHiver = function () { return hiver; };
            try { L.TUILES['?'](c, v, 16); } finally { L.Saisons.enHiver = avant; }
            return c.traces;
        }
        for (const [nom, v, hiver] of [['seule', 0, false], ['milieu', 15, false], ['nord_est', 12, false], ['hiver', 0, true]]) {
            const t = peindre(v, hiver);
            res[nom] = { fond: t[0] && t[0][4], margelles: t.filter(function (q) { return q[4] === MARGELLE; }).length,
                         echelle: t.some(function (q) { return q[4] === '#c9d2d8'; }) };
        }
        return res;
    }""")
    assert r["seule"]["margelles"] == 4 and r["seule"]["echelle"], r
    assert r["milieu"]["margelles"] == 0 and not r["milieu"]["echelle"], "une tuile du milieu n'a pas de bord"
    assert r["nord_est"]["margelles"] == 2 and r["nord_est"]["echelle"], "le coin nord-est : deux bords et l'échelle"
    assert r["hiver"]["fond"] != r["seule"]["fond"] and not r["hiver"]["echelle"], "l'hiver : la bâche"
