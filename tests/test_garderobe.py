"""La garde-robe : des squelettes qu'on habille (catalogue Python).

Demande de Martin (22 sept. 2026) : « des squelettes qu'on habille, ce qui donne une presque
infinité d'habillement », « plusieurs types de squelettes pour les types de personnes ».
Le dessin est jugé dans `test_garderobe_js.py` — chaque pièce de chaque liste, sur chaque squelette
(`test_chaque_piece_change_le_dessin_sur_chaque_squelette`).
"""

from app import garderobe, missions, pietons, visages


def test_chaque_garde_robe_habille_un_archetype_au_corps_commun():
    archs = {a["slug"]: a for a in pietons.CATALOGUE}
    for slug in garderobe.GARDE_ROBES:
        assert slug in archs, f"garde-robe pour personne : {slug}"
        assert archs[slug]["sprite"] == "joueur", f"{slug} a un corps dessiné à la main"


def test_les_garde_robes_piochent_dans_les_listes_fermees():
    for slug, g in garderobe.GARDE_ROBES.items():
        assert set(g["squelettes"]) <= set(garderobe.SQUELETTES), slug
        assert set(g["coiffures"]) <= set(garderobe.COIFFURES), slug
        assert set(g["hauts"]) <= set(garderobe.HAUTS), slug
        assert set(g["bas"]) <= set(garderobe.BAS), slug
        assert set(g["chapeaux"]) <= set(garderobe.CHAPEAUX) - {"aucun"}, slug
        assert set(g["motifs"]) <= set(garderobe.MOTIFS), slug
        assert set(g["souliers"]) <= set(garderobe.SOULIERS), slug
        assert set(g["accessoires"]) <= set(garderobe.ACCESSOIRES), slug
        assert all(0 < p <= 1 for p in g["accessoires"].values()), slug
        for famille in g["couleurs_haut"] + g["couleurs_bas"] + g["couleurs_chapeau"]:
            assert famille == "gang" or famille in garderobe.COULEURS, (slug, famille)
        assert 0 <= g["chapeau_chance"] <= 1
        assert not g["chapeaux"] or g["chapeau_chance"] > 0


def test_un_gang_garde_sa_couleur():
    """On reconnaît un gang dans la rue à sa couleur : la garde-robe ne la tire pas."""
    robes = garderobe.exporter()["garde_robes"]
    for a in pietons.CATALOGUE:
        if a["gang"] and a["slug"] in robes:
            assert robes[a["slug"]]["haut_fixe"] == a["couleurs"]["c"], a["slug"]


def test_chaque_personnage_a_sa_tenue_et_le_chapeau_de_son_portrait():
    tenues = garderobe.exporter()["personnages"]
    assert set(tenues) == {p["slug"] for p in missions.PERSONNAGES}
    for p in missions.PERSONNAGES:
        t = tenues[p["slug"]]
        assert t["squelette"] in garderobe.SQUELETTES and t["coiffure"] in garderobe.COIFFURES
        assert t["haut"] in garderobe.HAUTS and t["bas"] in garderobe.BAS
        assert t["chapeau"] in garderobe.CHAPEAUX and set(t["accessoires"]) <= set(garderobe.ACCESSOIRES)
        assert t["couleur_haut"] == p["couleurs"]["c"] and t["peau"] == p["couleurs"]["s"]
        # Un chapeau au portrait, un chapeau dans la rue — et inversement.
        assert (visages.VISAGES[p["slug"]]["chapeau"] != "aucun") == (t["chapeau"] != "aucun"), p["slug"]
    assert tenues["bouchard"]["chapeau"] == "kepi"
    assert tenues["mo"]["chapeau"] == "tuque"
    assert tenues["bonimenteur"]["chapeau"] == "canotier"


def test_le_paquet_porte_la_garde_robe(paquet):
    assert set(paquet["garderobe"]["garde_robes"]) == set(garderobe.GARDE_ROBES)


def test_chaque_tenue_de_rosa_est_une_piece_qu_on_enfile():
    from app import magasins
    for t in magasins.TENUES:
        assert t["emplacement"] in magasins.PLACES, t["slug"]
        piece = t["piece"]
        if t["emplacement"] == "tete":
            assert set(piece) == {"chapeau"} and piece["chapeau"] in garderobe.CHAPEAUX[1:], t["slug"]
        elif t["emplacement"] == "pieds":
            assert set(piece) == {"souliers"} and piece["souliers"] in garderobe.SOULIERS[1:], t["slug"]
        elif t["emplacement"] == "taille":
            assert set(piece) == {"accessoires"} and set(piece["accessoires"]) <= set(garderobe.ACCESSOIRES), t["slug"]
        elif t["emplacement"] == "main":
            assert piece == {"objet": "parapluie"}, t["slug"]
        else:
            assert piece["haut"] in garderobe.HAUTS, t["slug"]
            assert piece.get("motif", "uni") in garderobe.MOTIFS
            assert set(piece.get("accessoires", [])) <= set(garderobe.ACCESSOIRES)
    foire = next(t for t in magasins.TENUES if t.get("prime") == "foire")
    assert foire["emplacement"] == "tete", "la casquette de la foire se porte sur la tête"
    assert sum(1 for t in magasins.TENUES if t["emplacement"] == "tete" and t["prix"]) >= 5, "Rosa vend des chapeaux"


def test_l_agent_et_le_garde_gardent_leur_uniforme():
    robes = garderobe.exporter()["garde_robes"]
    archs = {a["slug"]: a for a in pietons.CATALOGUE}
    assert robes["policier"]["haut_fixe"] == archs["policier"]["couleurs"]["c"]
    assert robes["garde"]["haut_fixe"] == archs["garde"]["couleurs"]["c"]
    assert robes["policier"]["chapeaux"] == ["kepi"] and robes["policier"]["chapeau_chance"] == 1.0


def test_rosa_habille_l_hiver():
    """Martin (30 sept. 2026) : des bottes d'hiver et de loup marin, cinq tuques de plus, des ceintures, la
    fléchée, un parapluie — chacun à SA place, et la vieille tuque de Rocco qui ne se vend pas."""
    from app import magasins
    par = {}
    for t in magasins.TENUES:
        if t["prix"]:
            par.setdefault(t["emplacement"], []).append(t["slug"])
    assert {"bottes_hiver", "loup_marin"} <= set(par["pieds"])
    assert {"ceinture", "ceinture_flechee"} <= set(par["taille"]) and par["main"] == ["parapluie"]
    tuques = [t for t in magasins.TENUES if t["emplacement"] == "tete" and t["piece"]["chapeau"].startswith("tuque")]
    assert sum(1 for t in tuques if t["prix"]) == 6, "la rouge, et cinq de plus"
    rocco = next(t for t in magasins.TENUES if t["slug"] == "tuque_rocco")
    assert rocco["prix"] is None and rocco.get("prime"), "la tuque de Rocco se donne, elle ne se vend pas"
    assert list(magasins.PLACES) == ["corps", "tete", "pieds", "taille", "main"]
