"""M10, 3e vague — la run : la contrebande de Sven, d'un district a l'autre.

Acheter bas a la cale du Norvegien (les Quais), vendre haut au comptoir d'un
commerce, au prix du jour de son district. ⚠️ Ce qui empeche la machine a
argent est juge ici : le prix monte avec la journee, le mauvais district fait
perdre, et une run complete vaut moins qu'une mission — et moins que le taxi
a l'heure.
"""

import pytest

from app import carte, economie, magasins, missions


def taxi_par_seconde() -> float:
    taxi = economie.BOULOTS["taxi"]
    return economie.gain_boulot(taxi) / (20 * taxi["etapes"])


def test_le_prix_monte_avec_la_journee():
    c = economie.CONTREBANDE
    assert 0 < c["hausse"] < 1 and c["caisses_max"] >= 4
    for slug in c["marchandises"]:
        p0, p1, p7 = (economie.prix_achat(slug, k) for k in (0, 1, c["caisses_max"] - 1))
        assert p0 == c["marchandises"][slug]["achat"]
        assert p0 < p1 < p7, slug


def test_le_mauvais_district_fait_perdre_et_le_bon_gagner():
    c = economie.CONTREBANDE
    bas, haut = c["facteur"]
    assert 0 < bas < 1 < haut
    for slug, m in c["marchandises"].items():
        assert m["vente"] * bas < m["achat"], f"{slug} : on gagne partout, ce n'est plus un commerce"
        assert m["vente"] * haut > economie.prix_achat(slug, 0), f"{slug} : on ne gagne nulle part"


def test_la_run_vaut_le_detour_mais_pas_une_mission_ni_le_taxi():
    c = economie.CONTREBANDE
    marge = economie.marge_max_run()
    assert marge > 0
    primes = [m["recompense"] for m in missions.CATALOGUE]
    assert marge < max(primes), "une run complete paie mieux que la plus grosse mission : elle vide l'histoire"
    assert marge / c["cycle_s"] < taxi_par_seconde(), "la run bat le taxi a l'heure"
    assert marge < economie.revenu_honnete_par_jour()


def test_la_cale_est_un_comptoir_des_quais():
    cale = magasins.ambulant("contrebande")
    assert cale and cale["service"] == "contrebande" and cale["sur"] == "quai"
    assert cale["districts"] == ("quais",) and cale["nombre"] == 1
    assert cale["tarif"] is None and not cale["reclame"], "pas une bouchee, pas de coupon"
    # Les comptoirs qui en prennent existent tous, et ce sont des commerces qu'on visite.
    pieces = {piece["slug"] for piece in carte._PIECES}
    for slug in economie.CONTREBANDE["comptoirs"]:
        assert slug in pieces, slug


def test_export_de_la_contrebande():
    e = economie.exporter()["contrebande"]
    assert e["marchandises"]["cigarettes"]["achat"] == economie.CONTREBANDE["marchandises"]["cigarettes"]["achat"]
    assert e["facteur"] == list(economie.CONTREBANDE["facteur"])
    assert e["comptoirs"] == list(economie.CONTREBANDE["comptoirs"])
    assert e["rayon_px"] > 0 and e["caisses_max"] == economie.CONTREBANDE["caisses_max"]


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def test_la_cale_est_posee_sur_les_planches_des_quais(ville):
    cales = [a for a in ville["ambulants"] if a["slug"] == "contrebande"]
    assert len(cales) == 1, "une cale, sur les Quais"
    x, y = cales[0]["x"], cales[0]["y"]
    sol = ville["sol"]
    assert sol[y][x] == "Q" and sol[y + 1][x] == "Q" and sol[y + 2][x] == "Q", "pas sur les planches"
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    assert chantier.district_en(x, y) == "quais"
