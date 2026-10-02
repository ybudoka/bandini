"""Les territoires des gangs : la carte des îlots (docs/jalons/les-territoires-des-gangs-bougent.md, vague 1)."""

from app import carte, mantes, nord, pietons, territoires


def test_chaque_gang_a_son_district_et_son_coeur_dans_sa_cour():
    t = territoires.pour_le_navigateur()
    # Les gangs de la VILLE D'AVANT, et les Mantes du Petit-Canton (vague 4, jugées à part plus bas).
    villes = {d["slug"] for d in carte.DISTRICTS}
    gangs = {g["slug"]: g for g in pietons.GANGS if g["district"] in villes | {"canton"}}
    assert {d["gang"] for d in t["districts"]} == set(gangs), "un gang sans district, ou l'inverse"
    for d in t["districts"]:
        if d["slug"] == "canton":
            continue
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
    assert set(tags) == set(devantures.TAGS_GANG) | {"mantes"}
    for gang, mots in tags.items():
        for mot, n in mots:
            assert 1 <= n <= territoires.TAG_TUILES_MAX, (gang, mot, n)
            assert devantures.tient_en(mot, n, 16, marge=0) and not devantures.tient_en(mot, n - 1, 16, marge=0), mot
        assert any(n == 1 for _, n in mots), gang



# --- La vague 4 : les Mantes du Petit-Canton --------------------------------------------------------------------


def test_le_petit_canton_entre_par_le_nord_en_rangees_negatives():
    """La bande nord a SES rangées, mais les mêmes colonnes : le Canton prend les rangées −7 à −1, et sa rangée du bas
    touche celle du haut du Faubourg, colonne pour colonne — la couture, face aux Cravates."""
    t = territoires.pour_le_navigateur()
    c = next(d for d in t["districts"] if d["slug"] == "canton")
    n = len(nord.RANGEES_NORD)
    assert c["gang"] == "mantes" and c["by"] == -n and c["plan"] == list(nord.district("canton")["plan"])
    assert t["nord"] == {"rangees": list(nord.RANGEES_NORD), "rues_h": list(nord.RUES_H_NORD)}
    assert nord.TRAME_NORD["colonnes"] == carte.COLONNES and nord.TRAME_NORD["rues_v"] == carte.RUES_V
    f = next(d for d in t["districts"] if d["slug"] == "faubourg")
    assert f["by"] == 0 and c["bx"] == f["bx"] and len(c["plan"][-1]) == len(f["plan"][0]), "la couture, colonne pour colonne"
    # Les Friches et la Gare restent hors du jeu : leurs gangs ne s'étendent pas au nord.
    assert not any(d["by"] < 0 and d["slug"] != "canton" for d in t["districts"])


def test_le_coeur_des_mantes_est_le_coin_de_leur_ecole():
    t = territoires.pour_le_navigateur()
    c, n = nord.district("canton"), len(nord.RANGEES_NORD)
    attendu = sorted([c["bx"] + i, c["by"] + j - n] for i in range(*mantes.ZONE["colonnes"])
                     for j in range(*mantes.ZONE["rangees"]))
    assert sorted(t["coeurs"]["mantes"]) == attendu and attendu


def test_les_mots_des_mantes_ne_touchent_pas_aux_tags_de_la_ville():
    """⚠️ La ville cuit ses tags avec `devantures.TAGS_GANG` : les Mantes n'y entrent pas (des murs changeraient)."""
    from app import devantures
    assert "mantes" not in devantures.TAGS_GANG
    assert [m for m, _ in territoires.pour_le_navigateur()["tags"]["mantes"]] == list(territoires.TAGS_DES_MANTES)
