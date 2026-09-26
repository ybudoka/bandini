"""La tempête de verglas, côté Python (docs/jalons/la-tempete-de-verglas.md) : ses nombres se tiennent,
ses quartiers existent, et le paquet la porte au navigateur."""

from app import carte, definitions, economie, vehicules, verglas


def test_trois_jours_jamais_au_debut_et_la_glace_fond_le_soir():
    t = verglas.TEMPETE
    assert t["jours"] == 3
    assert t["premier"] >= 3, "la glace le premier soir : on n'a pas encore appris la ville"
    assert t["tous_les"] > 10 * t["jours"], "un événement rare, pas une saison"
    assert 0 < t["arrive_h"] < t["fond_h"] < 24


def test_la_glace_retire_et_la_police_tarde():
    e = verglas.EFFETS
    for cle in ("adherence", "frein", "vitesse_trafic", "vision_police"):
        assert 0 < e[cle] < 1, cle
    assert e["retard_police"] > 1
    assert 0 < e["nuit_noire"] < 0.3 and 0 < e["reflet"] < 0.2 and 0 < e["vernis"] < 0.5, "on doit encore voir la rue"


def test_les_quartiers_au_noir_existent_et_chaque_jour_en_eteint():
    districts = {z.get("district") for z in carte.generer()["zones"]}
    p = verglas.PANNES
    assert set(p["quartiers"]) <= districts, set(p["quartiers"]) - districts
    assert len(p["par_jour"]) == verglas.TEMPETE["jours"]
    assert all(1 <= n < len(p["quartiers"]) for n in p["par_jour"]), "un jour sans noir, ou toute la ville au noir"


def test_le_clairon_et_le_paquet():
    c = verglas.CLAIRON
    assert c["veille"] == c["veille"].upper() and c["pendant"] == c["pendant"].upper().replace("{QUARTIERS}", "{quartiers}")
    assert "{quartiers}" in c["pendant"]
    assert definitions.assembler()["verglas"] == verglas.pour_le_navigateur()


def test_les_generatrices_tiennent_l_economie():
    f = economie.BOULOTS["generatrices"]
    taxi = economie.gain_boulot(economie.BOULOTS["taxi"])
    assert taxi <= economie.gain_boulot(f) <= 4 * taxi
    assert vehicules.par_slug("camion")["boulot"] == "generatrices"
    assert economie.PALIERS["generatrices"][0]["compte"] <= 5, "trois jours tous les quarante : des paliers courts"
