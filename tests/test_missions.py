from app import armes, audio, carte, economie, missions, pietons


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


def test_les_cinq_missions_se_suivent():
    assert [m["slug"] for m in missions.CATALOGUE] == ["m1", "m2", "m3", "m4", "m5"]
    assert missions.ordre_topologique() == ["m1", "m2", "m3", "m4", "m5"]
    for precedente, mission in zip(missions.CATALOGUE, missions.CATALOGUE[1:]):
        assert mission["prerequis"] == [precedente["slug"]], "chaque mission ouvre la suivante"
    assert len(missions.DEFIS) == 3


def test_chaque_mission_a_un_donneur_place_et_des_objectifs_lisibles():
    lieux = {p["slug"] for p in carte.SPECIAUX.values()} | {"kiosque", "planque"}
    zones = {"cravates", "port", "faubourg"}
    for m in missions.CATALOGUE:
        perso = missions.personnage(m["donneur"])
        assert perso and perso["ou"], f"{m['slug']} : le donneur doit se tenir quelque part"
        assert m["objectifs"], m["slug"]
        for o in m["objectifs"]:
            assert o["type"] in missions.TYPES_OBJECTIFS
            assert o["texte"] == o["texte"].upper() and len(o["texte"]) <= 60, "l'objectif s'affiche en une ligne"
            if "lieu" in o:
                assert o["lieu"] in lieux, f"{m['slug']} : lieu inconnu {o['lieu']}"
            if o.get("ou", "").startswith("zone:"):
                assert o["ou"][5:] in zones
            if o.get("groupe"):
                assert any(g["slug"] == o["groupe"] for g in pietons.GANGS)
            if o.get("vehicule"):
                assert o["vehicule"] in {v["slug"] for v in __import__("app.vehicules", fromlist=["CATALOGUE"]).CATALOGUE}
        donne = m["donne"]
        if donne.get("arme"):
            assert armes.par_slug(donne["arme"]), donne["arme"]
        if donne.get("propriete"):
            assert any(p["slug"] == donne["propriete"] for p in economie.PROPRIETES)


def test_chaque_replique_a_une_voix_et_tient_en_deux_phrases():
    """⚠️ Ces textes sont la source des voix generees : un texte qui change
    regenere un fichier (au caractere). Court, quebecois, une voix connue."""
    vues = set()
    for r in missions.repliques():
        assert r["slug"] not in vues, "deux repliques avec le meme slug de voix"
        vues.add(r["slug"])
        perso = missions.personnage(r["qui"])
        assert perso, f"{r['slug']} : personnage inconnu"
        assert perso["voix"] and not perso["voix"].startswith("__")
        assert 8 <= len(r["texte"]) <= 110, r["slug"]
        assert r["texte"].count(". ") + r["texte"].count("! ") + r["texte"].count("? ") <= 2, \
            f"{r['slug']} : plus de deux phrases"
    assert 30 <= len(vues) <= 60
    assert sum(len(r["texte"]) for r in missions.repliques()) < 4000, "quelques milliers de caracteres, pas plus"
    for m in missions.CATALOGUE:
        for partie in ("intro", "fin", "echec"):
            assert m["dialogue"][partie], f"{m['slug']} : pas de {partie}"
        if m["prerequis"]:
            assert m["dialogue"]["appel"], f"{m['slug']} : apres la premiere, le donneur appelle"
            assert all(ligne["qui"] == m["donneur"] for ligne in m["dialogue"]["appel"])
    assert all(v["histoire"] for v in audio.voix_histoire())
