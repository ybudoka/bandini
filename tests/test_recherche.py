from app import recherche


def test_paliers_contigus_et_monotones():
    assert [p["etoiles"] for p in recherche.PALIERS] == list(range(6))
    zero = recherche.PALIERS[0]
    assert zero["agents_pied"] == 0 and zero["autos"] == 0 and not zero["tirent"]
    for a, b in zip(recherche.PALIERS, recherche.PALIERS[1:]):
        assert b["agents_pied"] >= a["agents_pied"]
        assert b["autos"] >= a["autos"]
        assert b["decroissance_s"] > a["decroissance_s"]
        assert b["tirent"] >= a["tirent"]
    assert recherche.PALIERS[5]["barrages"] and recherche.PALIERS[5]["helico"]
    assert recherche.ETOILES_MAX == 5


def test_delits():
    for nom, d in recherche.DELITS.items():
        assert d["etoiles"] >= 1, nom
        assert isinstance(d["temoin"], bool)
    assert recherche.DELITS["mort_policier"]["etoiles"] > recherche.DELITS["mort_pieton"]["etoiles"]
    assert recherche.DELITS["carjacking"]["temoin"] is False


def test_vision():
    for genre in ("policier", "auto_police", "pieton", "helico"):
        v = recherche.VISION[genre]
        assert 0 < v["angle"] <= 180
        assert v["nuit"] <= v["jour"]
    assert recherche.VISION["alarme_rayon"] > 0


def test_export_complet():
    e = recherche.exporter()
    for cle in ("paliers", "delits", "vision", "temoins", "deguisement", "vitesses", "tuile_px"):
        assert cle in e
    assert e["vitesses"]["joueur_sprint"] > e["vitesses"]["policier"] > e["vitesses"]["pieton_course"]
