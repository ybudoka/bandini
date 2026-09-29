"""Les territoires des gangs : la carte des îlots (docs/jalons/les-territoires-des-gangs-bougent.md, vague 1)."""

from app import carte, pietons, territoires


def test_chaque_gang_a_son_district_et_son_coeur_dans_sa_cour():
    t = territoires.pour_le_navigateur()
    # ⚠️ Les gangs de la VILLE D'AVANT : les Mantes (le Petit-Canton, la bande nord) n'en sont pas, pour cette vague.
    villes = {d["slug"] for d in carte.DISTRICTS}
    gangs = {g["slug"]: g for g in pietons.GANGS if g["district"] in villes}
    assert {d["gang"] for d in t["districts"]} == set(gangs), "un gang sans district, ou l'inverse"
    for d in t["districts"]:
        assert gangs[d["gang"]]["district"] == d["slug"], d["slug"]
        coeur = t["coeurs"][d["gang"]]
        assert coeur, f"{d['gang']} n'a pas de cœur"
        for bx, by in coeur:
            assert d["bx"] <= bx < d["bx"] + len(d["plan"][0]) and d["by"] <= by < d["by"] + len(d["plan"]), (bx, by)
            assert carte.PLAN[by][bx] in "g<^", (d["gang"], bx, by, carte.PLAN[by][bx])
    r = t["regles"]
    assert 0 < r["coup"] < r["regain"] < r["marge"] < r["force"]


def test_le_paquet_porte_les_territoires():
    from app import definitions
    assert definitions.construire().definitions.taille > 0
    assert "territoires" in __import__("json").loads(definitions.construire().definitions.corps)["pietons"]
