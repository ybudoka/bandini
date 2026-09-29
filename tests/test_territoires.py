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


def test_chaque_gang_exporte_ses_tags_et_la_place_qu_il_leur_faut():
    """Vague 3 : le navigateur tague un coin pris sans mesurer un texte — il reçoit, pour chaque mot, le nombre de
    tuiles de mur qu'il lui faut (le plus petit qui le tient, trois au plus). Chaque gang a un mot d'UNE tuile : un
    mur seul peut porter sa signature."""
    from app import devantures

    tags = territoires.pour_le_navigateur()["tags"]
    assert set(tags) == set(devantures.TAGS_GANG)
    for gang, mots in tags.items():
        for mot, n in mots:
            assert 1 <= n <= territoires.TAG_TUILES_MAX, (gang, mot, n)
            assert devantures.tient_en(mot, n, 16, marge=0) and not devantures.tient_en(mot, n - 1, 16, marge=0), mot
        assert any(n == 1 for _, n in mots), gang
