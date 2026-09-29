"""La pluie de Baie-des-Brumes (`app/pluie.py`) : des averses au printemps et à l'automne, des orages
l'été, jamais l'hiver — des données seulement ; le navigateur en tire le temps qu'il fait."""

from app import pluie


def test_les_averses_et_les_orages_tiennent_dans_la_journee():
    for nom, r in (("averses", pluie.AVERSES), ("orages", pluie.ORAGES)):
        assert 0 < r["chance"] < 1, nom
        assert 0 <= r["debut_h"][0] < r["debut_h"][1] and r["duree_h"][0] < r["duree_h"][1], nom
        assert r["debut_h"][1] + r["duree_h"][1] <= 23.5, f"{nom} : une pluie qui passerait minuit"
        assert 0 < r["montee_h"] < r["duree_h"][0] / 2, nom
    assert pluie.AVERSES["sel"] != pluie.ORAGES["sel"]


def test_la_pluie_glisse_moins_que_la_neige():
    e = pluie.EFFETS
    assert 0.7 <= e["adherence"] < 1 and 0.7 <= e["frein"] < 1
    assert e["feuilles_adherence"] <= e["adherence"], "les feuilles mouillées glissent plus que l'asphalte mouillé"
    assert 0.8 <= e["gadoue"]["adherence"] < 1
    assert 0 < e["flaques"]["part"] < 0.1, "une rue de flaques n'est plus une rue"


def test_dans_le_paquet(paquet):
    assert paquet["pluie"] == pluie.pour_le_navigateur()
