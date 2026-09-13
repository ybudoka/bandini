import pytest

from app import carte, economie


@pytest.mark.parametrize("argent", [0, 10, 500, 100_000])
@pytest.mark.parametrize("casier", [0, 1, 5, economie.CASIER_MAX, 99])
def test_l_amende_ne_depasse_jamais_l_argent_ni_le_zero(argent, casier):
    for etoiles in range(0, 7):
        a = economie.amende(argent, etoiles, casier)
        assert 0 <= a <= argent


def test_l_amende_monte_avec_les_etoiles_et_le_casier():
    riche = 10**9
    for casier in range(economie.CASIER_MAX):
        assert economie.amende(riche, 1, casier) <= economie.amende(riche, 1, casier + 1)
    for etoiles in range(1, 5):
        assert economie.amende(riche, etoiles, 0) < economie.amende(riche, etoiles + 1, 0)
    assert economie.amende(riche, 1, 0) == 60
    assert economie.amende(riche, 5, 2) == 2000


def test_le_pot_de_vin_tente_au_premier_delit():
    assert economie.pot_de_vin(1, 0) < economie.amende(10**9, 1, 0)
    assert economie.POT_DE_VIN_ACCEPTE[1] > economie.POT_DE_VIN_ACCEPTE[3] > economie.POT_DE_VIN_ACCEPTE[4]


def test_l_hopital_a_un_plancher_et_un_plafond():
    assert economie.facture_hopital(0) == 0
    assert economie.facture_hopital(100) == 30
    assert economie.facture_hopital(2000) == 200
    assert economie.facture_hopital(10**6) == 500


def test_prix_de_vente():
    assert economie.prix_vente(600, 100, 100, 0) == 150
    assert economie.prix_vente(600, 50, 100, 0) == 75
    assert economie.prix_vente(600, 100, 100, 5) == 0
    assert economie.prix_vente(600, 100, 0, 0) == 0


def test_les_proprietes():
    slugs = [p["slug"] for p in economie.PROPRIETES]
    assert len(slugs) == len(set(slugs))
    lieux = {p["slug"] for p in carte.exporter()["points_interet"]}
    for p in economie.PROPRIETES:
        assert p["prix"] > 0 and p["revenu_par_jour"] > 0
        assert 10 <= economie.retour_sur_investissement_min(p) <= 200
        if p["phase"] == 1 and p["lieu"] in lieux:
            pass  # place sur la carte ; le vrai Faubourg (M1) rendra ce test strict
    assert economie.FORTUNE_MAX >= 3 * sum(p["prix"] for p in economie.PROPRIETES)


def test_export():
    e = economie.exporter()
    assert len(e["amendes"]) == 5 and len(e["amendes"][0]) == economie.CASIER_MAX + 1
    assert e["amendes"][0][0] == 60
    assert e["pots_de_vin"][0][0] == economie.pot_de_vin(1, 0)
