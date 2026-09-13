import json

from app import definitions


def test_le_paquet_est_deterministe():
    a, b = definitions.construire(), definitions.construire()
    assert a.corps == b.corps
    assert a.etag == b.etag
    assert len(a.etag) == 16


def test_le_paquet_reste_leger():
    paquet = definitions.construire()
    assert paquet.taille < 200_000, f"{paquet.taille} octets : la carte enfle"


def test_l_empreinte_change_avec_le_contenu(monkeypatch):
    avant = definitions.construire().etag
    monkeypatch.setattr(definitions.economie, "ARGENT_DEPART", 51)
    assert definitions.construire().etag != avant


def test_le_paquet_contient_tout(paquet):
    for cle in ("version", "empreinte", "tuile_px", "vehicules", "armes", "ordre_armes", "economie",
                "recherche", "carte", "missions", "defis", "types_objectifs", "magasins", "tenues"):
        assert cle in paquet, cle
    assert json.dumps(paquet)  # serialisable
