"""Les décapotables l'hiver, au banc (docs/jalons/les-decapotables-l-hiver.md).

Demande de Martin (29 sept. 2026) : « penses au décapotable l'hiver ». Tant que la neige
tient (`Saisons.enHiver`), la sport et le cabriolet rose roulent CAPOTE RELEVÉE, et on ne
voit plus qui les mène ; la conductrice, volée, descend en tuque et en bottes. Au dégel,
tout se rouvre. Ces juges regardent ce que le jeu PEINT : le dessin que `dessinerUn` cuit,
la grille projetée à chaque cap, et le corps que `Jeu.rendre()` demande à l'atlas.
"""

# ⚠️ Le jour 1 est le 1er janvier (la neige tient), le jour 21 est en juillet, le 14 au
# printemps (la neige est fondue) et le 39 en décembre (elle est revenue).
HIVER, ETE, PRINTEMPS, DECEMBRE = 1, 21, 14, 39

DECOR = """
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const ctx = L.Base.ecran();
"""


def test_la_capote_se_releve_quand_la_neige_tient(banc):
    """Le dessin cuit par `dessinerUn` est celui de la capote l'hiver (sous son propre nom
    de cache, sinon l'atlas rendrait l'image d'été) et celui de l'habitacle ouvert le reste
    de l'année. ⚠️ C'est la NEIGE qui décide, pas le mois : la capote retombe au printemps
    et revient en décembre. Et un char fermé ne change pas pour autant : la berline reste la
    berline."""
    r = banc("""function (L, o) {""" + DECOR + """
        const cuits = [], vrai = L.Atlas.cuireCap;
        L.Atlas.cuireCap = function (nom, def) { cuits.push({ nom: nom, hiver: def === (L.SPRITES[nom.split('~')[0]] || {}).hiver }); return vrai.apply(this, arguments); };
        const out = {};
        [""" + f"{HIVER}, {ETE}, {PRINTEMPS}, {DECEMBRE}" + """].forEach(function (jour) {
            L.B.partie.jour = jour;
            out[jour] = { enHiver: L.Saisons.enHiver() };
            ['sport', 'cabriolet', 'auto'].forEach(function (slug) {
                const v = L.Vehicules.creer(slug, j.x + 40, j.y, 0, { etat: 'stationne' });
                cuits.length = 0;
                L.Vehicules.dessinerUn(ctx, v, 0, 0);
                out[jour][slug] = cuits.slice();
                L.Entites.retirer(v);
            });
        });
        L.Atlas.cuireCap = vrai;
        return out;
    }""")
    for jour, neige in ((HIVER, True), (ETE, False), (PRINTEMPS, False), (DECEMBRE, True)):
        assert r[str(jour)]["enHiver"] is neige, f"jour {jour} : la neige tient-elle ? {r[str(jour)]['enHiver']}"
        for slug in ("sport", "cabriolet"):
            vu = r[str(jour)][slug]
            attendu = [{"nom": slug + "~hiver", "hiver": True}] if neige else [{"nom": slug, "hiver": False}]
            assert vu == attendu, f"jour {jour}, la {slug} est peinte {vu} (attendu {attendu})"
        assert r[str(jour)]["auto"] == [{"nom": "auto", "hiver": False}], \
            f"jour {jour} : la berline n'a pas de capote à relever : {r[str(jour)]['auto']}"


def test_sous_la_capote_on_ne_voit_plus_les_sieges(banc):
    """À chacun des 32 caps, la grille projetée de la capote ne laisse voir AUCUN pixel des
    sièges (`u`) : la toile couvre l'habitacle d'un bout à l'autre. (Pas le plancher `i` : on
    le voit déjà l'été par les passages de roue, à côté des moyeux.)
    ⚠️ Ce juge est né d'une capture : la pente arrière passait sous le haut des dossiers,
    et on les voyait percer la toile. L'été, les sièges se voient — c'est une décapotable."""
    r = banc("""function (L, o) {
        const out = {};
        ['sport', 'cabriolet'].forEach(function (slug) {
            const n = L.Vehicules.ROTATIONS;
            const compter = function (def) {
                const par = [];
                for (let i = 0; i < n; i++) {
                    const g = L.Atlas.projeter(def.machine, i * Math.PI * 2 / n - Math.PI / 2, def.w);
                    let k = 0;
                    g.forEach(function (ligne) { for (const ch of ligne) if (ch === 'u') k++; });
                    par.push(k);
                }
                return par;
            };
            const toile = function (def) {
                let k = 0;
                L.Atlas.projeter(def.machine, 0, def.w).forEach(function (ligne) { for (const ch of ligne) if (ch === 'q') k++; });
                return k;
            };
            out[slug] = { hiver: compter(L.SPRITES[slug].hiver), ete: compter(L.SPRITES[slug]),
                          toile: toile(L.SPRITES[slug].hiver), selle: !!L.SPRITES[slug].hiver.selle };
        });
        return out;
    }""")
    for slug, vu in r.items():
        perces = [i for i, k in enumerate(vu["hiver"]) if k]
        assert not perces, f"la {slug} : les sièges percent la capote aux caps {perces} ({vu['hiver']})"
        assert all(k > 0 for k in vu["ete"]), f"la {slug} l'été : on ne voit plus ses sièges ({vu['ete']})"
        assert vu["toile"] >= 30, f"la {slug} : la toile ne fait que {vu['toile']} pixels de profil"
        assert not vu["selle"], f"la {slug} l'hiver a une selle : on verrait qui conduit à travers la toile"


def test_sous_la_capote_on_ne_voit_plus_la_conductrice(banc):
    """Le cabriolet du trafic se peint avec sa conductrice par-dessus (deux images) l'été ;
    l'hiver, la toile la cache : une seule image, et `cavalierDe` ne rend personne. Le
    joueur qui la conduit l'hiver, pareil."""
    r = banc("""function (L, o) {""" + DECOR + """
        const vrai = ctx.drawImage, images = function (v) {
            let n = 0;
            ctx.drawImage = function () { n++; };
            L.Vehicules.dessinerUn(ctx, v, 0, 0);
            ctx.drawImage = vrai;
            return n;
        };
        const v = L.Vehicules.creer('cabriolet', j.x + 40, j.y, 0, { conducteur: 'trafic', etat: 'roule' });
        const out = {};
        [""" + f"{HIVER}, {ETE}" + """].forEach(function (jour) {
            L.B.partie.jour = jour;
            out[jour] = { images: images(v), cavalier: L.Vehicules.cavalierDe(v) !== null };
        });
        v.conducteur = j;
        L.B.partie.jour = """ + str(HIVER) + """;
        out.joueur = { images: images(v), cavalier: L.Vehicules.cavalierDe(v) !== null };
        return out;
    }""")
    assert r[str(ETE)] == {"images": 2, "cavalier": True}, f"l'été, on ne la voit pas au volant : {r[str(ETE)]}"
    assert r[str(HIVER)] == {"images": 1, "cavalier": False}, f"l'hiver, on la voit à travers la toile : {r[str(HIVER)]}"
    assert r["joueur"] == {"images": 1, "cavalier": False}, f"le joueur se voit à travers la toile : {r['joueur']}"


def _vole_en(banc, jour):
    """Le joueur vole le cabriolet du trafic ce jour-là : qui en descend, et quel corps
    `Jeu.rendre()` demande pour elle à l'atlas."""
    return banc("""function (L, o) {""" + DECOR + """
        L.B.partie.jour = """ + str(jour) + """;
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        const v = L.Vehicules.creer('cabriolet', j.x + 20, j.y, 0, { conducteur: 'trafic', etat: 'roule' });
        L.Entites.indexer();
        L.Vehicules.monter(j, v);
        const elle = L.B.entites.find(function (e) { return e.type === 'pieton' && e.sprite === 'conductrice'; });
        const noms = [], vrai = L.Atlas.cuire;
        L.Atlas.cuire = function (nom) { noms.push(nom); return vrai.apply(this, arguments); };
        L.Jeu.rendre();
        L.Atlas.cuire = vrai;
        return { sortie: !!elle, corps: noms.filter(function (n) { return n.indexOf('conductrice') === 0; }) };
    }""")


def test_l_hiver_elle_descend_en_tuque(banc):
    """Volée l'hiver, la conductrice sort du cabriolet et `Jeu.rendre()` la peint avec son
    corps d'hiver (`conductrice~hiver` : la tuque à pompon, le col, les manches, les bottes) ;
    l'été, en robe. Et le corps d'hiver est TIRÉ de la robe : mêmes poses, même taille, la
    même ancre — seules la tête, le col, les bras et les jambes changent."""
    hiver, ete = _vole_en(banc, HIVER), _vole_en(banc, ETE)
    assert hiver["sortie"] and ete["sortie"], f"le carjacking ne l'a pas fait descendre : {hiver}, {ete}"
    assert "conductrice~hiver" in hiver["corps"], f"l'hiver, elle est peinte {hiver['corps']}"
    assert "conductrice" not in hiver["corps"], "l'hiver, on la peint encore en robe d'été"
    assert ete["corps"] and set(ete["corps"]) == {"conductrice"}, f"l'été, elle est peinte {ete['corps']}"
    f = banc("""function (L, o) {
        const ete = L.SPRITES.conductrice, hiver = ete.hiver;
        const forme = function (f) {
            const o = {};
            for (const p in f.poses) o[p] = f.poses[p].map(function (g) { return [g.length, g[0].length]; });
            return o;
        };
        const lignes = hiver.poses.bas[0];
        return {
            memeForme: JSON.stringify(forme(ete)) === JSON.stringify(forme(hiver)),
            memeAncre: JSON.stringify(ete.ancre) === JSON.stringify(hiver.ancre),
            tuque: lignes.slice(0, 3).join('').replace(/[^qQf]/g, '').length,
            bottes: (lignes[13] + lignes[14]).indexOf('s') < 0,
            couche: JSON.stringify(hiver.poses.couche) === JSON.stringify(ete.poses.couche),
        };
    }""")
    assert f["memeForme"] and f["memeAncre"], "le corps d'hiver n'a pas la forme de la robe : elle sauterait"
    assert f["tuque"] >= 12, f"la tuque ne couvre que {f['tuque']} pixels du crâne"
    assert f["bottes"], "l'hiver, elle a encore les jambes nues"
    assert f["couche"], "par terre, la tuque tombe : `couche` reste celle de la robe"
