"""Le train : la clé `train` de la carte (docs/jalons/le-train.md)."""

import json

import pytest

from app import carte, train
from tests import villes


@pytest.fixture(scope="module")
def ville():
    return villes.generer()


def test_la_carte_a_son_train(ville):
    t = ville["train"]
    assert t["rang"] == 6 and t["tunnel"] == ville["relief"]["montagnes"]["x"] == 419
    assert t["viaduc"] == [96, 284] and [g[0] for g in t["gares"]] == ["Les Friches", "Petit-Canton", "Gare centrale"]


def test_les_passages_sont_les_rues_croisees_au_sol(ville):
    t, rang = ville["train"], ville["voie"][6]
    rues = []
    x = 0
    while x < t["tunnel"]:
        if rang[x] != ".":
            x0 = x
            while rang[x] != ".":
                x += 1
            if not (t["viaduc"][0] <= x0 <= t["viaduc"][1]):
                rues.append([x0, x - 1])
        else:
            x += 1
    assert t["passages"] == rues == [[1, 4], [353, 354], [414, 417]]


def test_sous_le_viaduc_les_rues_restent_ouvertes(ville):
    t = ville["train"]
    haut = range(t["viaduc"][0] + t["rampe"], t["viaduc"][1] - t["rampe"] + 1)
    assert len(t["piliers"]) >= 12
    for x in t["piliers"]:
        assert x in haut
        assert ville["voie"][6][x] == "." and ville["sol"][6][x] != ".", f"un pilier sur la rue ou le trottoir : {x}"
    # Chaque rue que le tablier enjambe garde toutes ses tuiles libres au rang 6.
    for x in haut:
        if ville["voie"][6][x] != ".":
            assert x not in t["piliers"]


def test_le_train_ne_deplace_rien(monkeypatch):
    avec = carte.generer()
    monkeypatch.setattr(train, "poser", lambda ville: None)
    sans = carte.generer()
    assert sans["train"] is None
    for cle in avec:
        if cle != "train":
            assert json.dumps(avec[cle], sort_keys=True) == json.dumps(sans[cle], sort_keys=True), cle


def test_poser_ne_tire_rien_et_redit_la_meme_chose(ville):
    import copy
    assert train.poser(copy.deepcopy(ville)) == train.poser(copy.deepcopy(ville)) == ville["train"]
    source = open(train.__file__, encoding="utf-8").read()
    assert "random" not in source and "Des" not in source and "graine" not in source


def test_sans_la_bande_pas_de_train():
    assert "train" not in villes.generer(nord=False)
