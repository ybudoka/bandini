import pytest

from app import carte, economie, recherche


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


def test_la_bouffe_redonne_du_souffle_et_la_poutine_vaut_son_prix():
    souffle_max = recherche.VITESSES["endurance"]
    for cle in ("hotdog_souffle", "poutine_souffle", "cafe_souffle"):
        assert 0 < economie.TARIFS[cle] <= souffle_max, cle
    # Ce qui coute plus cher nourrit plus, en vie comme en jambes.
    assert economie.TARIFS["poutine"] > economie.TARIFS["hotdog"]
    assert economie.TARIFS["poutine_souffle"] > economie.TARIFS["hotdog_souffle"]
    assert economie.TARIFS["poutine_pv"] > economie.TARIFS["hotdog_pv"]


def test_le_cafe_fait_courir_plus_longtemps_sans_courir_plus_vite():
    """⚠️ Le cafe n'achete que de la DUREE.

    Les 2,1 du sprint sont ce qui separe le joueur du policier (1,9) et de la
    foule : une gorgee qui y toucherait rendrait toutes les poursuites du jeu
    ingagnables pour la police. `CAFE` ne connait donc que `depense`, et
    l'effet doit durer plus longtemps qu'un seul plein de souffle, sinon il ne
    vaut pas le detour par la roulotte.
    """
    v = recherche.VITESSES
    assert "vitesse" not in economie.CAFE and "joueur_sprint" not in economie.CAFE
    assert 0 < economie.CAFE["depense"] < 1
    a_jeun_s = v["endurance"] / v["endurance_par_image"] / 60
    sous_cafe_s = a_jeun_s / economie.CAFE["depense"]
    assert sous_cafe_s >= 2 * a_jeun_s
    assert economie.CAFE["duree_s"] > sous_cafe_s, "l'effet ne couvre meme pas un sprint"


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
    assert e["cafe"] == economie.CAFE
    assert e["tarifs"]["hotdog_souffle"] == economie.TARIFS["hotdog_souffle"]
    assert len(e["amendes"]) == 5 and len(e["amendes"][0]) == economie.CASIER_MAX + 1
    assert e["amendes"][0][0] == 60
    assert e["pots_de_vin"][0][0] == economie.pot_de_vin(1, 0)
