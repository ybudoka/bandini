"""Des étages dedans aussi (docs/jalons/des-etages-dedans-aussi.md) : le navigateur peint les étages que Python a
comptés (`au_dessus`), sans les recompter — et on y monte."""


def test_le_navigateur_peint_ce_que_python_a_compte(banc):
    """⚠️ On FAUSSE la donnée : si le JS recompte, il ne la suit pas."""
    r = banc("""function (L) {
        const M = L.Monde, c = M.carte, f = [];
        for (const r of c.def.residences) { r.au_dessus = (r.x + r.y) % 3; delete r.elargi; delete r.murEtendu; }
        for (const d of c.def.devantures) { d.au_dessus = (d.x + d.y) % 3; delete d.hauts; }
        for (const r of c.def.residences) if (M.logementElargi(r).hauts !== r.au_dessus) f.push(['r', r.x, r.y]);
        for (const d of c.def.devantures) if (M.etagesDuCommerce(d) !== d.au_dessus) f.push(['d', d.x, d.y]);
        return f;
    }""")
    assert r == [], r[:5]


def test_on_monte_au_dernier_etage_et_on_redescend_au_bouton(banc):
    """Chaque porte à trois niveaux : debout sur la marche, ACTION (`utiliserPoint`) monte, monte, redescend,
    redescend — même quand les deux escaliers d'un étage du milieu se touchent (une petite pièce)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const I = L.Monde.carte.def.interieurs, j = L.B.joueur, parcours = [];
        const portes = L.Monde.carte.portes.filter(function (p) { return p.interieur && I[p.interieur + '_haut2']; });
        for (const porte of portes) {
            if (L.B.interieur) L.Jeu.quitterLaPiece();
            o.entrer(porte);
            const vus = [L.B.interieur.slug];
            for (const sens of ['monte', 'monte', 'descend', 'descend']) {
                const p = L.B.interieur.points.find(function (q) { return q.type === 'escalier' && !!q.descend === (sens === 'descend'); });
                if (!p) { vus.push('pas d\\'escalier qui ' + sens); break; }
                j.x = p.x * 16 + 8; j.y = p.y * 16 + 8;
                L.Missions.utiliserPoint(j); L.Jeu.finirTransition();
                vus.push(L.B.interieur.slug);
            }
            parcours.push({ rez: porte.interieur, vus: vus });
        }
        // ⚠️ La pièce du DESSOUS ne tient pas à l'ordre des clés : à l'envers, l'étage du dessus (dont l'escalier
        // descend vers le milieu) viendrait en premier.
        if (L.B.interieur) L.Jeu.quitterLaPiece();
        const def = L.Monde.carte.def, inverse = {};
        for (const k of Object.keys(def.interieurs).reverse()) inverse[k] = def.interieurs[k];
        def.interieurs = inverse;
        for (const p of parcours) p.dessous = L.Histoire.pieceDessous(p.rez + '_haut');
        return parcours;
    }""")
    assert len(r) >= 5, f"{len(r)} portes à trois niveaux"
    for p in r:
        rez = p["rez"]
        assert p["vus"] == [rez, rez + "_haut", rez + "_haut2", rez + "_haut", rez], p
        assert p["dessous"] == rez, p
