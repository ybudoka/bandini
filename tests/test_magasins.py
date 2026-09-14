from app import armes, magasins, recherche, vehicules


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
        if commerce["gain_souffle"]:
            assert commerce["gain_souffle"] in economie.TARIFS
            assert 0 < economie.TARIFS[commerce["gain_souffle"]] <= recherche.VITESSES["endurance"]
        assert commerce["effet"] in (None, *magasins.EFFETS)
        assert commerce["sur"] in ("trottoir", "stationnement")
        assert 1 <= commerce["nombre"] <= 6
        if commerce["districts"]:
            from app import carte
            connus = {d["slug"] for d in carte.DISTRICTS}
            assert set(commerce["districts"]) <= connus, commerce["slug"]
        if commerce["reclame"]:
            assert len(commerce["reclame"]) <= 24, "un boniment tient dans une bulle"
        if commerce["heures"]:
            debut, fin = commerce["heures"]
            assert 0 <= debut < 1 and 0 <= fin < 1


def test_les_slugs_ambulants_sont_uniques():
    slugs = [c["slug"] for c in magasins.AMBULANTS]
    assert len(slugs) == len(set(slugs))


def test_ce_qui_se_mange_redonne_du_souffle():
    """Un kiosque a manger rend de la vie ET du souffle.

    Sans le souffle, un kiosque ne sert a rien la ou on en a besoin : en
    poursuite, la seule facon de reprendre son endurance etait de s'arreter
    de courir. Le journal, lui, ne se mange pas.
    """
    for commerce in magasins.AMBULANTS:
        if commerce["service"] == "manger":
            assert commerce["gain_pv"] and commerce["gain_souffle"], commerce["slug"]
        else:
            assert not commerce["gain_souffle"], commerce["slug"]


def test_seul_le_cafe_reveille():
    reveillent = [c["slug"] for c in magasins.AMBULANTS if c["effet"] == "cafe"]
    assert reveillent == ["cafe"], "l'effet du cafe ne s'achete qu'au cafe"
