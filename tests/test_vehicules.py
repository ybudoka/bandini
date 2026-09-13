from app import vehicules


def test_slugs_uniques_et_classes_connues():
    slugs = [v["slug"] for v in vehicules.CATALOGUE]
    assert len(slugs) == len(set(slugs))
    for v in vehicules.CATALOGUE:
        assert v["classe"] in vehicules.CLASSES
        assert 0 <= v["frequence"] <= 1
        assert v["prix"] > 0 and v["vie"] > 0 and v["places"] >= 1
        assert 0 < v["vitesse_max"] <= 8
        assert 0 < v["braquage"] < 0.2
        assert v["couleurs"] and all(c.startswith("#") for c in v["couleurs"])
        assert v["phase"] in (1, 2)


def test_une_auto_de_police_et_les_quatre_de_la_v1():
    assert any(v["police"] for v in vehicules.CATALOGUE)
    assert {v["slug"] for v in vehicules.de_phase(1)} == {"auto", "taxi", "moto", "police"}
    assert vehicules.par_slug("moto")["ejecte"] is True
    assert vehicules.par_slug("inconnu") is None


def test_la_moto_est_la_plus_rapide_et_la_plus_fragile():
    moto = vehicules.par_slug("moto")
    for v in vehicules.CATALOGUE:
        if v["slug"] != "moto":
            assert moto["vitesse_max"] >= v["vitesse_max"]
            assert moto["vie"] <= v["vie"]
