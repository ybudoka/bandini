"""Le temps des Fêtes, côté Python (docs/jalons/le-temps-des-fetes.md) : décembre, le sapin sur une place du
Faubourg, et les dindes qui tiennent l'économie."""

from app import calendrier, carte, definitions, economie, fetes


def test_decembre_et_le_sapin_du_faubourg():
    assert fetes.jours() and all(calendrier.mois(j) == "decembre" for j in fetes.jours())
    v = carte.exporter()
    s = fetes.sapin(v)
    assert s and any(q["x"] == s["x"] and q["y"] == s["y"] and q["district"] == "faubourg" for q in v["scenes"])
    assert definitions.assembler()["fetes"] == fetes.pour_le_navigateur(v)


def test_les_dindes_tiennent_l_economie():
    f = economie.BOULOTS["dindes"]
    taxi = economie.gain_boulot(economie.BOULOTS["taxi"])
    assert taxi <= economie.gain_boulot(f) <= 4 * taxi and f["vehicule"] == "camion"
