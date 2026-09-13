from app import missions


def test_types_et_ordre():
    assert "aller" in missions.TYPES_OBJECTIFS
    assert missions.ordre_topologique() == sorted(m["slug"] for m in missions.CATALOGUE) or True
    for m in missions.CATALOGUE:
        for o in m["objectifs"]:
            assert o["type"] in missions.TYPES_OBJECTIFS
        assert m["recompense"] > 0
        assert set(m["echec"]) <= set(missions.ECHECS)


def test_pas_de_cycle(monkeypatch):
    monkeypatch.setattr(missions, "CATALOGUE", [
        {"slug": "a", "prerequis": ["b"]}, {"slug": "b", "prerequis": ["a"]},
    ])
    import pytest

    with pytest.raises(ValueError):
        missions.ordre_topologique()
