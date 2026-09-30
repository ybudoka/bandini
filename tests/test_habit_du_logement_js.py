"""L'habit du logement (docs/jalons/des-interieurs-fideles-a-l-exterieur.md, vagues 2 et 3) : on pousse la porte d'une
maison pauvre, on entre chez un pauvre ; d'une maison cossue, chez un cossu ; d'une villa, dans une villa. Le
navigateur le lit DEHORS, à la résidence de la porte (`Monde.materiauxDuLogement`), jamais au dé."""

#: L'habit attendu, par ce qu'on voit dehors. ⚠️ En toutes lettres, pas relu dans `monde.js` : un juge qui relit
#: la table qu'il juge ne rougit jamais.
ATTENDU = {"villa": "villa", "-": "logement_pauvre", "+": "logement_cossu", "=": "piece"}
#: Les quartiers qui accrochent quelque chose au mur (vague 3).
QUARTIERS = {"canton", "quais", "faubourg", "erables", "gare", "pointe"}

LOGEMENTS = """
        const c = L.Monde.carte.def, out = [];
        for (const p of c.portes) {
            const piece = p.interieur && c.interieurs[p.interieur];
            if (!piece || piece.porte !== 'maison') continue;
            const res = c.residences.find(function (q) { return q.y === p.y && p.x >= q.x && p.x < q.x + q.l; });
            if (!res) continue;
            const z = c.zones.find(function (q) { return q.district && p.x >= q.x && p.x < q.x + q.l && p.y >= q.y && p.y < q.y + q.h; });
            const m = L.Monde.materiauxDuLogement(p, piece) || {};
            out.push({ slug: p.interieur, dehors: res.villa ? 'villa' : (res.standing || '='), district: z && z.district,
                       etages: res.etages || 1, B: m.B, W: m.W, D: m.D, t: m.t || null, l: m.l || null });
        }
"""


def test_chaque_logement_porte_l_habit_de_sa_facade(banc):
    r = banc("function (L, o) {" + LOGEMENTS + "return out; }")
    genres = {q["dehors"] for q in r}
    assert {"villa", "-", "+", "="} <= genres, f"le témoin n'a pas tous les dehors : {genres}"
    for q in r:
        habit = ATTENDU[q["dehors"]]
        assert q["B"].split("~")[0] == habit and q["B"] == q["W"] == q["D"], q
        assert q["l"] == (None if habit == "piece" else habit), q


def test_le_quartier_s_accroche_au_mur_et_le_genre_se_lit_au_plancher(banc):
    """Vague 3 : le mur porte le quartier de la porte (`~canton`…) ; le plancher dit le genre — le marbre de la
    villa, la moquette du bungalow (un seul étage), le plancher de l'habit d'un plex."""
    r = banc("function (L, o) {" + LOGEMENTS + "return out; }")
    vus = set()
    for q in r:
        attendu = q["district"] if q["district"] in QUARTIERS else None
        assert q["B"] == ATTENDU[q["dehors"]] + ("~" + attendu if attendu else ""), q
        vus.add(q["district"])
        habit = ATTENDU[q["dehors"]]
        sol = "villa" if q["dehors"] == "villa" else "moquette" if q["etages"] < 2 else (None if habit == "piece" else habit)
        assert q["t"] == sol, q
    assert {"canton", "faubourg", "erables", "gare"} <= vus, vus
    assert any(q["t"] == "moquette" for q in r), "le témoin n'a pas de bungalow"


def test_on_entre_dans_son_habit_et_l_etage_le_garde(banc):
    """Pour de vrai, par la porte : la pièce chargée porte l'habit ; l'étage du haut (par l'escalier : la même
    porte) aussi ; et un commerce prend celui de sa devanture (vague 4)."""
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
        // Les murs habillés lisent leur plinthe et leurs seize bruits de position (`varianteDeTuile`) : le mur
        // du fond a le plancher au sud, et l'objet du quartier a de quoi varier.
        const k = L.Monde.carte, bruits = new Set(), fautes = [];
        function mur(x, y) { return x < 0 || y < 0 || x >= k.w || y >= k.h || 'BWD'.indexOf(k.sol[y][x]) >= 0; }
        let fond = 0;
        for (let y = 0; y < k.h; y++) for (let x = 0; x < k.w; x++) {
            const g = k.sol[y][x];
            if ('BWD'.indexOf(g) < 0) continue;
            const v = L.Monde.varianteDeTuile(g, x, y);
            const cotes = (mur(x, y - 1) ? 0 : 1) | (mur(x + 1, y) ? 0 : 2) | (mur(x, y + 1) ? 0 : 4) | (mur(x - 1, y) ? 0 : 8);
            if ((v & 15) !== cotes || (v >> 4) > 15) fautes.push([g, x, y, v, cotes]);
            if (y === 0 && (v & 4)) fond++;
            bruits.add(v >> 4);
        }
        out.variantes = { fond: fond, bruits: bruits.size, largeur: k.w, fautes: fautes.slice(0, 4) };
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
    assert r["pauvre"]["B"].split("~")[0] == r["pauvre"]["t"] == "logement_pauvre", r
    assert r["haut"]["B"] == r["pauvre"]["B"], f"l'étage n'a pas l'habit du bas : {r}"
    assert not r["variantes"]["fautes"], r["variantes"]
    assert r["variantes"]["fond"] >= r["variantes"]["largeur"] - 3 and r["variantes"]["bruits"] > 4, r["variantes"]
    assert r["villa"]["B"].split("~")[0] == r["villa"]["t"] == "villa", r
    assert r["ordinaire"]["B"].split("~")[0] == "piece", r
    assert r["commerce"]["B"].endswith("_commerce"), f"un commerce entre dans l'habit de sa devanture : {r}"


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


def test_chaque_quartier_accroche_son_objet_au_mur_du_fond(banc):
    """L'objet du quartier se peint sur le mur du FOND (le plancher au sud), jamais sur un mur de côté ; et chaque
    quartier en a au moins deux, lus à la position."""
    r = banc("""function (L, o) {
        function dessin(cle, v) {
            const c = o.doc.createElement('canvas').getContext('2d'); c.traces = [];
            L.TUILES[cle](c, v, 16);
            return c.traces;
        }
        function traces(cle, v) { return dessin(cle, v).length; }
        const out = {};
        for (const d of %s) {
            const base = traces('B@piece', 4 | (1 << 4)), formes = new Set();
            let fond = 0, cote = 0;
            for (let h = 0; h < 16; h++) {
                const n = traces('B@piece~' + d, 4 | (h << 4));
                if (n > traces('B@piece', 4 | (h << 4))) { fond++; formes.add(JSON.stringify(dessin('B@piece~' + d, 4 | (h << 4)).slice(traces('B@piece', 4 | (h << 4))))); }
                if (traces('B@piece~' + d, 2 | (h << 4)) > traces('B@piece', 2 | (h << 4))) cote++;
            }
            out[d] = { fond: fond, cote: cote, formes: formes.size, base: base,
                       fenetre: L.TUILES['W@piece~' + d] === L.TUILES['W@piece'] };
        }
        return out;
    }""" % sorted(QUARTIERS))
    for d, q in r.items():
        assert q["fond"] >= 3 and q["cote"] == 0, (d, q)
        assert q["formes"] >= 2, f"{d} n'accroche qu'une seule chose : {q}"
        assert q["fenetre"], f"{d} : la fenêtre change de peintre"


#: Vague 4 : les quartiers dont un COMMERCE accroche un objet de commerce au mur du fond.
QUARTIERS_DU_COMMERCE = {"canton", "quais", "faubourg", "erables", "shop", "gare", "friches", "pointe"}


def test_chaque_commerce_porte_l_habit_de_sa_devanture_et_son_quartier(banc):
    """Le commerce derrière une devanture : les murs du standing de la devanture, l'objet de commerce de son
    quartier ; un lieu fait à la main (sans devanture) garde son plâtre."""
    r = banc("""function (L, o) {
        const c = L.Monde.carte.def, out = [];
        for (const p of c.portes) {
            const piece = p.interieur && c.interieurs[p.interieur];
            if (!piece || piece.materiaux) continue;
            if (piece.porte !== 'commerce') {
                // Une pièce qui n'est pas un commerce (le phare derrière sa devanture : un logement) n'en prend
                // jamais l'habit.
                if (L.Monde.materiauxDuCommerce(p, piece)) out.push({ slug: p.interieur, faute: 'pas un commerce' });
                continue;
            }
            const d = c.devantures.find(function (q) { return q.y === p.y && p.x >= q.x && p.x < q.x + q.l; });
            const z = c.zones.find(function (q) { return q.district && p.x >= q.x && p.x < q.x + q.l && p.y >= q.y && p.y < q.y + q.h; });
            const m = L.Monde.materiauxDuCommerce(p, piece) || {};
            out.push({ slug: p.interieur, devanture: !!d, standing: d ? (d.standing || '=') : null, district: z && z.district,
                       B: m.B || null, W: m.W || null, D: m.D || null, t: m.t || null });
        }
        return out;
    }""")
    assert not [q for q in r if q.get("faute")], [q for q in r if q.get("faute")]
    r = [q for q in r if not q.get("faute")]
    avec = [q for q in r if q["devanture"]]
    assert len(avec) >= 40, len(avec)
    for q in r:
        if not q["devanture"]:
            assert q["B"] is None, f"un lieu fait à la main a pris un habit : {q}"
            continue
        habit = ATTENDU[q["standing"]]
        attendu = (habit + "~" + q["district"] + "_commerce" if q["district"] in QUARTIERS_DU_COMMERCE
                   else None if habit == "piece" else habit)
        assert q["B"] == q["W"] == q["D"] == attendu and q["t"] is None, q
    assert {q["standing"] for q in avec} >= {"-", "=", "+"}, "le témoin n'a pas tous les standings"


def test_une_boutique_n_a_ni_drap_ni_chaine(banc):
    """La vitrine d'une boutique pauvre est une vitrine nue, sa porte une porte de bois ; le mur du fond porte un
    objet de commerce, jamais le crucifix ni la photo de famille."""
    r = banc("""function (L, o) {
        function dessin(cle, v) {
            const c = o.doc.createElement('canvas').getContext('2d'); c.traces = [];
            L.TUILES[cle](c, v, 16);
            return c.traces;
        }
        const drap = dessin('W@logement_pauvre', 0).some(function (q) { return q[4] === '#e4ddcb'; });
        const out = { drapChezSoi: drap, boutiques: {} };
        for (const d of %s) {
            const cle = 'logement_pauvre~' + d + '_commerce';
            const w = dessin('W@' + cle, 0), porte = dessin('D@' + cle, 0);
            const formes = new Set();
            for (let h = 0; h < 16; h++) {
                const t = dessin('B@' + cle, 4 | (h << 4)), n = dessin('B@logement_pauvre', 4 | (h << 4)).length;
                if (t.length > n) formes.add(JSON.stringify(t.slice(n)));
            }
            out.boutiques[d] = { drap: w.some(function (q) { return q[4] === '#e4ddcb'; }),
                                 chaine: porte.some(function (q) { return q[4] === '#9a9a9e'; }), formes: Array.from(formes) };
        }
        const chezSoi = new Set();
        for (const d of ['canton', 'quais', 'faubourg', 'erables', 'gare', 'pointe']) {
            for (let h = 0; h < 16; h++) {
                const t = dessin('B@piece~' + d, 4 | (h << 4)), n = dessin('B@piece', 4 | (h << 4)).length;
                if (t.length > n) chezSoi.add(d + JSON.stringify(t.slice(n)));
            }
        }
        out.crucifix = Array.from(chezSoi).filter(function (f) { return f.indexOf('faubourg') === 0 && f.indexOf('#4a2e1e') >= 0; });
        return out;
    }""" % sorted(QUARTIERS_DU_COMMERCE))
    assert r["drapChezSoi"], "le juge ne voit plus le drap du logement pauvre : il ne mord plus"
    for d, q in r["boutiques"].items():
        assert not q["drap"] and not q["chaine"], (d, q)
        assert len(q["formes"]) >= 2, f"{d} : {len(q['formes'])} objet(s) de commerce"
    crucifix = r["crucifix"][0][len("faubourg"):]
    assert crucifix not in r["boutiques"]["faubourg"]["formes"], "le crucifix est accroché dans une boutique"
