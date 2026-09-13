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


def test_une_auto_de_police_les_quatre_de_la_v1_et_le_velo():
    assert any(v["police"] for v in vehicules.CATALOGUE)
    assert {v["slug"] for v in vehicules.de_phase(1)} == {"auto", "taxi", "moto", "velo", "police"}
    assert vehicules.par_slug("moto")["ejecte"] is True
    assert vehicules.par_slug("velo")["ejecte"] is True, "on tombe d'un velo au premier choc"
    assert vehicules.par_slug("velo")["radio"] is None, "un velo n'a pas de radio"
    assert vehicules.par_slug("velo")["frequence"] > 0, "il faut des cyclistes dans la rue"
    assert vehicules.par_slug("inconnu") is None


def test_la_moto_est_la_plus_rapide_et_le_velo_le_plus_fragile():
    moto, velo = vehicules.par_slug("moto"), vehicules.par_slug("velo")
    for v in vehicules.CATALOGUE:
        assert moto["vitesse_max"] >= v["vitesse_max"], v["slug"]
        assert velo["vie"] <= v["vie"], v["slug"]
    assert velo["vitesse_max"] < moto["vitesse_max"] / 2, "un velo ne suit pas une moto"


def test_le_trafic_et_la_physique_sont_bornes():
    t, ph = vehicules.TRAFIC, vehicules.PHYSIQUE
    assert 1 <= t["vehicules_max"] <= 30 and 0 <= t["stationnes_max"] <= 20
    assert 0.2 <= t["vitesse_ville"] <= 1.0
    assert t["feu_vert_images"] > t["feu_orange_images"] > 0
    assert t["naissance_px"] < t["oubli_px"]
    assert 0 < ph["sous_pas_px"] <= 4, "un sous-pas plus grand qu'un rayon traverse les murs"
    assert ph["cercles"] >= 2
    assert 0 < ph["choc_vitesse_min"] < ph["ejection_vitesse_min"]
    assert 0 < ph["renverse_vitesse_min"] < 3
    assert 0 < ph["feu_sous"] < ph["fumee_sous"] < 1
    assert ph["explosion_degats"] >= 50 and ph["explosion_rayon_px"] >= 32
    assert 0 < ph["choc_rebond"] < 1


def test_le_sous_pas_ne_traverse_jamais_un_char():
    """⚠️ Le sous-pas doit rester plus petit que le demi-largeur du char le
    plus etroit : sinon, a pleine vitesse, deux cercles se croisent sans se
    voir et la moto passe a travers l'autobus."""
    plus_etroit = min(v["largeur"] for v in vehicules.de_phase(1))
    assert vehicules.PHYSIQUE["sous_pas_px"] <= plus_etroit / 2
