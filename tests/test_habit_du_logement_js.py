"""L'habit du logement (docs/jalons/des-interieurs-fideles-a-l-exterieur.md, vague 2) : on pousse la porte d'une
maison pauvre, on entre chez un pauvre ; d'une maison cossue, chez un cossu ; d'une villa, dans une villa. Le
navigateur le lit DEHORS, à la résidence de la porte (`Monde.materiauxDuLogement`), jamais au dé."""

#: L'habit attendu, par ce qu'on voit dehors. ⚠️ En toutes lettres, pas relu dans `monde.js` : un juge qui relit
#: la table qu'il juge ne rougit jamais.
ATTENDU = {"villa": "villa", "-": "logement_pauvre", "+": "logement_cossu", "=": None}


def test_chaque_logement_porte_l_habit_de_sa_facade(banc):
    r = banc("""function (L, o) {
        const c = L.Monde.carte.def, out = [];
        for (const p of c.portes) {
            const piece = p.interieur && c.interieurs[p.interieur];
            if (!piece || piece.porte !== 'maison') continue;
            const res = c.residences.find(function (q) { return q.y === p.y && p.x >= q.x && p.x < q.x + q.l; });
            if (!res) continue;
            const m = L.Monde.materiauxDuLogement(p, piece);
            out.push({ slug: p.interieur, dehors: res.villa ? 'villa' : (res.standing || '='), B: m && m.B, t: m && m.t, l: m && m.l });
        }
        return out;
    }""")
    genres = {q["dehors"] for q in r}
    assert {"villa", "-", "+", "="} <= genres, f"le témoin n'a pas tous les dehors : {genres}"
    for q in r:
        assert q["B"] == q["t"] == q["l"] == ATTENDU[q["dehors"]], q


def test_on_entre_dans_son_habit_et_l_etage_le_garde(banc):
    """Pour de vrai, par la porte : la pièce chargée porte l'habit ; l'étage du haut (par l'escalier : la même
    porte) aussi ; et un commerce garde le plâtre des pièces."""
    r = banc("""function (L, o) {
        L.Jeu.commencer(); if (L.B.menu) L.Hud.fermerMenu(); o.frame(2);
        const c = L.Monde.carte.def, out = {};
        function porteDe(dehors, etage) {
            return c.portes.find(function (p) {
                const piece = p.interieur && c.interieurs[p.interieur];
                if (!piece || piece.porte !== 'maison') return false;
                const res = c.residences.find(function (q) { return q.y === p.y && p.x >= q.x && p.x < q.x + q.l; });
                if (!res || (res.villa ? 'villa' : (res.standing || '=')) !== dehors) return false;
                return !etage || !!c.interieurs[p.interieur + '_haut'];
            });
        }
        function dedans(p) {
            const j = L.B.joueur;
            j.x = p.x * 16 + 8; j.y = (p.y + 1) * 16 + 10; L.Entites.indexer();
            L.Jeu.entrer(p);
            for (let n = 0; n < 240 && !(L.B.interieur && L.B.interieur.slug === p.interieur); n++) o.frame(1);
            for (let n = 0; n < 60; n++) o.frame(1);
            const m = L.Monde.carte.materiaux || {};
            return { slug: L.B.interieur && L.B.interieur.slug, B: m.B, t: m.t };
        }
        function sortir() { L.Jeu.sortir(); for (let n = 0; n < 120 && L.B.interieur; n++) o.frame(1); for (let n = 0; n < 30; n++) o.frame(1); }
        const pauvre = porteDe('-', true);
        out.pauvre = dedans(pauvre);
        L.Monde.changerPiece(pauvre.interieur + '_haut');
        const m = L.Monde.carte.materiaux || {};
        out.haut = { B: m.B, t: m.t };
        L.Monde.changerPiece(pauvre.interieur);
        sortir();
        out.villa = dedans(porteDe('villa')); sortir();
        out.ordinaire = dedans(porteDe('=')); sortir();
        const commerce = c.portes.find(function (p) { const q = p.interieur && c.interieurs[p.interieur]; return q && q.porte === 'commerce'; });
        out.commerce = dedans(commerce);
        return out;
    }""")
    assert r["pauvre"]["B"] == r["pauvre"]["t"] == "logement_pauvre", r
    assert r["haut"]["B"] == "logement_pauvre", f"l'étage n'a pas l'habit du bas : {r}"
    assert r["villa"]["B"] == r["villa"]["t"] == "villa", r
    assert r["ordinaire"]["B"] == "piece" and r["ordinaire"].get("t") is None, r
    assert r["commerce"]["B"] == "piece", r


def test_chaque_habit_a_ses_peintres_et_ne_ressemble_pas_au_platre(banc):
    r = banc("""function (L, o) {
        function fond(cle, v) {
            const c = o.doc.createElement('canvas').getContext('2d'); c.traces = [];
            L.TUILES[cle](c, v, 16);
            return c.traces.length && c.traces[0][4];
        }
        const out = {};
        for (const m of ['logement_pauvre', 'logement_cossu', 'villa']) {
            for (const g of ['B', 'W', 'D', 't', 'l']) {
                const cle = g + '@' + m;
                out[cle] = L.TUILES[cle] ? fond(cle, 0) : null;
            }
        }
        out.platre = fond('B@piece', 0); out.bois = fond('t', 0);
        return out;
    }""")
    for m in ("logement_pauvre", "logement_cossu", "villa"):
        for g in "BWDtl":
            assert r[f"{g}@{m}"] is not None, f"{g}@{m} n'a pas de peintre"
        assert r[f"B@{m}"] != r["platre"] and r[f"t@{m}"] != r["bois"], (m, r)
