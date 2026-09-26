"""La Saint-Jean, côté Python (docs/jalons/la-saint-jean-sur-la-baie.md) : la rue du défilé est une rue que
la carte sait déjà barrer sans couper la ville, dans le Faubourg ; le soir tient dans la journée."""

from app import calendrier, carte, definitions, saint_jean


def test_la_rue_du_defile_est_une_fermeture_du_faubourg_qui_n_enferme_rien():
    v = carte.exporter()
    r = saint_jean.rue_du_defile(v)
    assert r, "pas de rue pour le défilé"
    rues = [{k: f[k] for k in ("x", "y", "l", "h")} for f in v["fermetures"] if not f.get("ecartee")]
    assert r in rues, "le défilé ferme une rue que le juge de connexité n'a pas vue"
    z = next(q for q in v["zones"] if q.get("district") == "faubourg" and q.get("slug") == "faubourg")
    assert z["x"] <= r["x"] and r["x"] + r["l"] <= z["x"] + z["l"] and z["y"] <= r["y"] and r["y"] + r["h"] <= z["y"] + z["h"]
    assert max(r["l"], r["h"]) >= saint_jean.DEFILE["ecart_tuiles"] * 2, "trop courte pour un défilé"


def test_le_soir_de_la_fete_et_le_paquet():
    h = saint_jean.HORAIRE
    assert 17 <= h["defile"][0] < h["defile"][1] <= h["feux"][0] < h["feux"][1] <= 24
    assert calendrier.mois(calendrier.DATES["saint_jean"]) == "juin"
    assert definitions.assembler()["saint_jean"] == saint_jean.pour_le_navigateur(carte.exporter())
