"""Les 4 roues : la fiche et les places (docs/jalons/les-4-roues.md, vague 1).

Martin (28 sept. 2026) : rapide hors route — « les chars ralentissent », pas lui ; stable ; deux places ; il
saute ; garé dans les Friches et au chalet du rang.
"""

import math

from app import carte, quatre_roues, vehicules
from app.blocs import rang


def test_sa_fiche_dit_ce_que_martin_a_demande():
    q, moto = vehicules.par_slug("quatre_roues"), vehicules.par_slug("moto")
    assert q["hors_route"] == 1.0, "le 4 roues garde tout son élan sur la terre"
    assert q["vitesse_max"] < moto["vitesse_max"], "un peu moins vite qu'une moto sur l'asphalte"
    assert q["places"] == 2
    assert isinstance(q["ejecte"], float) and q["ejecte"] > vehicules.PHYSIQUE["ejection_vitesse_min"], \
        "stable : on n'en tombe qu'en frappant fort"
    assert q["frequence"] == 0.0, "il ne roule pas dans le trafic"


def test_les_chars_ralentissent_hors_route_et_pas_lui():
    """Martin : « les chars ralentissent ». Une auto garde deux tiers de son allure sur la terre, un camion
    moins, une moto un peu plus ; ce qui flotte n'y va pas ; le 4 roues et la motoneige gardent tout."""
    par = {v["slug"]: v["hors_route"] for v in vehicules.CATALOGUE}
    assert par["auto"] < 1 and par["camion"] < par["auto"] < par["moto"] < 1, par
    assert par["quatre_roues"] == 1.0 and par["motoneige"] == 1.0
    assert all(v["hors_route"] == 1.0 for v in vehicules.CATALOGUE if v["eau"])


def test_trois_dans_les_friches_a_cote_d_un_cabanon():
    from app import nord
    ville = carte.exporter()
    places = ville["quatre_roues"]
    assert len(places) == quatre_roues.COMBIEN, places
    cabanons = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] == "cabanon"}
    pris = {(d["x"], d["y"]) for d in ville["decor"]}
    for p in places:
        assert nord.LECTEUR.district_en(p["x"], p["y"]) == "friches", p
        assert carte.LEGENDE[ville["sol"][p["y"]][p["x"]]].get("terre"), p
        assert (p["x"], p["y"]) not in pris, f"un 4 roues sur un décor : {p}"
        assert any(abs(p["x"] - cx) + abs(p["y"] - cy) <= 2 for cx, cy in cabanons), f"loin de tout cabanon : {p}"
    assert "quatre_roues" not in carte.generer(nord=False), "la ville d'avant n'en sait rien"


def test_le_tien_attend_au_chalet_loin_de_la_place_du_char():
    """⚠️ À plus de 48 px de la place du char : la planque garde tout ce qui s'y gare (`garderLesCharsDesPlanques`)."""
    q, char = rang.BLOC["quatre_roues"], rang.BLOC["planque"]["char"]
    assert math.hypot(q["x"] - char["x"], q["y"] - char["y"]) * carte.TUILE_PX > 48
    assert carte.LEGENDE[rang.PLAN[q["y"]][q["x"]]].get("terre"), q
