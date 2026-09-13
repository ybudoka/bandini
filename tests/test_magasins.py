from app import armes, magasins, vehicules


def test_magasins():
    slugs = [m["slug"] for m in magasins.CATALOGUE]
    assert len(slugs) == len(set(slugs))
    types = {m["type"] for m in magasins.CATALOGUE}
    assert {"armurerie", "vetements", "garage"} <= types
    for m in magasins.CATALOGUE:
        assert m["type"] in magasins.TYPES
        if m["type"] == "armurerie":
            for slug in m["articles"] + m["munitions"]:
                assert armes.par_slug(slug), slug
            for slug in m["munitions"]:
                assert armes.par_slug(slug)["chargeur"], slug
        if m["type"] == "garage":
            for slug in m["articles"]:
                assert vehicules.par_slug(slug), slug


def test_tenues():
    assert magasins.TENUES[0]["prix"] == 0
    assert len({t["slug"] for t in magasins.TENUES}) == len(magasins.TENUES)


def test_les_ambulants_pointent_vers_des_tarifs_qui_existent():
    from app import economie

    for commerce in magasins.AMBULANTS:
        assert commerce["tarif"] in economie.TARIFS, commerce["slug"]
        assert economie.TARIFS[commerce["tarif"]] > 0
        if commerce["gain_pv"]:
            assert commerce["gain_pv"] in economie.TARIFS
            assert 0 < economie.TARIFS[commerce["gain_pv"]] <= 100
        assert commerce["sur"] in ("trottoir", "stationnement")
        assert 1 <= commerce["nombre"] <= 6
        if commerce["heures"]:
            debut, fin = commerce["heures"]
            assert 0 <= debut < 1 and 0 <= fin < 1


def test_les_slugs_ambulants_sont_uniques():
    slugs = [c["slug"] for c in magasins.AMBULANTS]
    assert len(slugs) == len(set(slugs))
