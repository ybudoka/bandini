from app import armes


def test_les_poings_d_abord_et_gratuits():
    premiere = armes.CATALOGUE[0]
    assert premiere["slug"] == "poings" and premiere["prix"] == 0 and premiere["type"] == "melee"


def test_catalogue_coherent():
    slugs = [a["slug"] for a in armes.CATALOGUE]
    assert len(slugs) == len(set(slugs))
    for a in armes.CATALOGUE:
        assert a["type"] in armes.TYPES
        assert a["degats"] >= 0 and a["portee"] > 0 and a["cadence"] >= 1
        if a["type"] == "tir":
            assert a["chargeur"] and a["munitions_max"] and a["chargeur"] <= a["munitions_max"]
            assert a["vitesse_projectile"] > 0
        if a["type"] == "melee":
            assert a["chargeur"] is None
        if a["usures"]:
            assert a["prix"] == 0, "une arme improvisee ne s'achete pas"


def test_les_prix_montent_dans_l_ordre_d_achat():
    prix = [a["prix"] for a in armes.achetables()]
    assert prix == sorted(prix)
    assert armes.par_slug("fusil")["plombs"] == 6
    assert armes.ORDRE_CYCLE[0] == "poings"


def test_chaque_arme_a_son_son():
    """Un son PAR ARME : jusqu'au 13 sept. 2026, tout jouait le coup de poing,
    le pistolet et le fusil compris. Le slug doit exister au catalogue audio
    (`test_audio` verifie de son cote que le navigateur a l'effet, avec repli)."""
    from app import audio

    for a in armes.CATALOGUE:
        assert a["son"] in audio.SLUGS, f"{a['slug']} : son {a['son']!r} inconnu de audio.CATALOGUE"
    assert armes.par_slug("poings")["son"] == "coup", "les poings gardent le coup de poing"
    sons = [a["son"] for a in armes.CATALOGUE]
    assert len(sons) == len(set(sons)), "deux armes qui font le meme bruit : on ne sait pas laquelle on tient"
