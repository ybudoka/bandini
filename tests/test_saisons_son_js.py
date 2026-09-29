"""Le son des saisons (les quatre saisons, lot 5 ; `Saisons.sonA`, `Saisons.majSon`) : une ambiance par
saison, dehors, en fondu enchaîné d'une saison à l'autre — une pure fonction du jour, de l'heure, de la
pluie et de la pièce."""

from app import audio, saisons


def test_quatre_ambiances_en_boucle_chacune_son_lieu():
    slugs = set(saisons.SON["ambiances"].values())
    assert slugs == {"saison_hiver", "saison_printemps", "saison_ete", "saison_automne"}
    assert set(saisons.SON["ambiances"]) == set(saisons.PALETTES), "une palette sans ambiance"
    par_slug = {e["slug"]: e for e in audio.CATALOGUE}
    for s in slugs:
        assert par_slug[s]["boucle"] and audio.LIEUX[s] == [s]


def test_la_bonne_ambiance_a_chaque_saison(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const S = L.Saisons, fort = function (j, h) {
            const v = S.sonA(j, h === undefined ? 0.5 : h, false, 0, 0);
            return Object.keys(v).filter(function (k) { return v[k] > 0; }).map(function (k) { return [k, v[k]]; });
        };
        return { janvier: fort(2), avril: fort(14), juillet: fort(21), aout: fort(26), octobre: fort(31), novembre: fort(36),
                 nuit: fort(21, 0.95), dedans: Object.values(S.sonA(21, 0.5, true, 0, 0)).filter(function (v) { return v > 0; }).length,
                 pluie: S.sonA(14, 0.5, false, 1, 0).saison_printemps, tempete: S.sonA(2, 0.5, false, 0, 1).saison_hiver,
                 transition: fort(37, 0.5) };
    }""")
    for mois, slug in (("janvier", "saison_hiver"), ("avril", "saison_printemps"), ("juillet", "saison_ete"),
                       ("aout", "saison_ete"), ("octobre", "saison_automne"), ("novembre", "saison_automne")):
        assert [k for k, _ in r[mois]] == [slug], f"{mois} : {r[mois]}"
    plein = r["juillet"][0][1]
    assert r["nuit"][0][1] < plein * 0.6, "la nuit n'est pas plus douce"
    assert r["dedans"] == 0, "on entend la saison dans une pièce"
    assert r["pluie"] < plein * 0.5 and r["tempete"] < plein * 0.5, "la saison couvre la pluie ou la tempête"
    assert {k for k, _ in r["transition"]} == {"saison_automne", "saison_hiver"}, "pas de fondu de novembre à l'hiver"


def test_le_fondu_glisse_d_une_image_a_l_autre_sans_de(banc):
    """Pendant la transition de novembre à l'hiver, image par image par la boucle du son : l'ambiance de
    l'hiver monte, celle de l'automne descend, jamais d'un saut ; et aucun dé n'est tiré."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const S = L.Son, Sa = L.Saisons, B = L.B, lieux = [], allumees = {};
        S.Lieu.charger = function (l) { lieux.push(l); };
        S.boucle = function (slug, actif) { allumees[slug] = actif; };
        S.boucleActive = function (slug) { return !!allumees[slug]; };
        S.reglerBoucle = function () {};
        let des = 0; const rng = B.rng; B.rng = function () { des++; return rng(); };
        B.partie.jour = 36; B.partie.heure = 0.5;
        for (let k = 0; k < 600; k++) { B.t++; Sa.majSon(); }
        const automneAvant = Sa.sonJoue.saison_automne;
        let saut = 0, prec = null, pire = null;
        // De la fin de novembre au plein hiver, une heure de jeu par pas de 60 images.
        for (let h = 0; h < 72; h++) {
            B.partie.jour = 37 + Math.floor(h / 24); B.partie.heure = (h % 24) / 24;
            for (let k = 0; k < 60; k++) {
                B.t++; Sa.majSon();
                const v = Sa.sonJoue;
                if (prec) saut = Math.max(saut, Math.abs(v.saison_hiver - prec[0]), Math.abs(v.saison_automne - prec[1]));
                prec = [v.saison_hiver, v.saison_automne];
            }
        }
        B.rng = rng;
        const apres = JSON.parse(JSON.stringify(Sa.sonJoue));
        // Dedans : tout se tait, doucement.
        B.interieur = { slug: 'x' };
        for (let k = 0; k < 600; k++) { B.t++; Sa.majSon(); }
        const dedans = Math.max.apply(null, Object.values(Sa.sonJoue));
        B.interieur = null;
        return { automneAvant: automneAvant, apres: apres, saut: saut, des: des, lieux: lieux, allumees: allumees, dedans: dedans };
    }""")
    assert r["automneAvant"] > 0.2, "l'automne ne s'entend pas en novembre"
    assert r["apres"]["saison_hiver"] > 0.2 and r["apres"]["saison_automne"] < 0.01
    assert r["saut"] < 0.02, f"un saut de {r['saut']:.3f} d'une image à l'autre"
    assert r["des"] == 0
    assert "saison_automne" in r["lieux"] and "saison_hiver" in r["lieux"] and "saison_ete" not in r["lieux"]
    assert r["dedans"] == 0 and not any(r["allumees"].values()), "une ambiance reste allumée dans une pièce"


def test_la_boucle_du_jeu_fait_entendre_la_saison(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        if (L.Hud.fermerMenu) L.Hud.fermerMenu();
        const S = L.Son, allumees = {};
        S.Lieu.charger = function () {};
        S.boucle = function (slug, actif) { allumees[slug] = actif; };
        S.boucleActive = function (slug) { return !!allumees[slug]; };
        S.reglerBoucle = function () {};
        L.B.partie.jour = 21; L.B.partie.heure = 0.5;
        o.frame(120);
        return allumees;
    }""")
    assert r.get("saison_ete"), f"la boucle du jeu n'allume pas l'ambiance de l'été : {r}"
