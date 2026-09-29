"""Le bus du Petit-Canton : la ligne 4 (docs/jalons/le-quartier-chinois.md, étape 2, vague B).

⚠️ Le juge qui tient le reste : ajoutée APRÈS la bande, sur la carte finie, elle ne change rien aux trois lignes
d'avant — ni leurs arrêts (leurs numéros compris), ni leur tracé.
"""

from unittest import mock

import pytest

from app import autobus, bus_du_canton, carte, nord


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


def _ligne4(ville):
    return next(ligne for ligne in ville["autobus"]["lignes"] if ligne["numero"] == 4)


def test_la_ligne_4_va_du_terminus_au_casino_par_la_rue_principale(ville):
    ligne, arrets = _ligne4(ville), ville["autobus"]["arrets"]
    assert ligne["nom"] == "Le Petit-Canton" and ligne["a_part"] is True and ligne["autobus"] >= 2
    noms = [arrets[i]["nom"] for i, _k in ligne["arrets"]]
    assert any(n.startswith("Terminus") for n in noms), noms
    assert "Casino du Dragon d'or" in noms, noms
    # Par la rue principale du quartier : son tracé passe sous l'arche.
    arche = ville["canton"]["arches"][0]
    tuiles = set(autobus.derouler(ligne["trace"]))
    assert any((x, arche["y"]) in tuiles for x in range(arche["x"], arche["x"] + arche["l"])), "pas sous l'arche"
    # Des arrêts dans la bande : le quartier est desservi.
    assert sum(1 for i, _k in ligne["arrets"] if arrets[i]["y"] < nord.DECALAGE_NORD) >= 3


def test_elle_ne_change_rien_aux_trois_lignes_d_avant(ville):
    """Sans elle, les mêmes arrêts aux mêmes numéros, les mêmes lignes ; ses arrêts neufs prennent les numéros
    SUIVANTS, et ses abribus sont au bout du décor, dans la bande."""
    with mock.patch.object(bus_du_canton, "tracer", lambda ville, n: None):
        sans = carte.generer()
    avec = carte.generer()
    n = len(sans["autobus"]["arrets"])
    assert avec["autobus"]["arrets"][:n] == sans["autobus"]["arrets"]
    assert avec["autobus"]["lignes"][:-1] == sans["autobus"]["lignes"]
    neufs = sorted({i for i, _k in avec["autobus"]["lignes"][-1]["arrets"] if i >= n})
    assert neufs == list(range(n, len(avec["autobus"]["arrets"]))), neufs
    assert avec["decor"][:len(sans["decor"])] == sans["decor"], "le décor d'avant a bougé"
    ajoutes = avec["decor"][len(sans["decor"]):]
    assert ajoutes and all(d["y"] < nord.DECALAGE_NORD and d["type"].startswith(("abribus", "banc")) for d in ajoutes)


def test_ses_arrets_ont_des_noms_uniques(ville):
    noms = [a["nom"] for a in ville["autobus"]["arrets"]]
    assert len(noms) == len(set(noms))
