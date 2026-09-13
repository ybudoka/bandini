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
