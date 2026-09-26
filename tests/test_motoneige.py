"""La motoneige, côté Python (docs/jalons/la-motoneige.md) : sa fiche, et la course des bois de La Pointe
lue sur la ville finie."""

from app import carte, definitions, missions, motoneige, vehicules


def test_la_fiche_de_la_motoneige():
    m = vehicules.par_slug("motoneige")
    assert m["frequence"] == 0, "elle ne roule pas dans le trafic"
    assert 0 < m["hors_neige"] < 1 and all(v["hors_neige"] == 1 for v in vehicules.CATALOGUE if v["slug"] != "motoneige")
    assert m["vitesse_max"] > vehicules.par_slug("auto")["vitesse_max"], "dans la neige, elle file"
    assert m["vitesse_max"] * m["hors_neige"] < vehicules.par_slug("velo")["vitesse_max"] * 1.2, "sur l'asphalte, elle se traîne"


def test_la_course_suit_les_sentiers_du_phare_et_revient():
    v = carte.generer()
    c = motoneige.course(v)
    assert c, "pas de course : les sentiers des bois ne mènent nulle part"
    sentiers = {tuple(t) for t in v["chemins_des_bois"]}
    assert tuple(c["depart"]) in sentiers and all(tuple(b) in sentiers for b in c["balises"])
    assert c["balises"][-1] == c["depart"], "la course revient au départ"
    assert len(c["balises"]) == 2 * motoneige.COURSE["balises"]
    phare = next(p for p in v["points_interet"] if p["slug"] == "phare")
    assert abs(c["depart"][0] - phare["x"]) + abs(c["depart"][1] - phare["y"]) < 40
    assert definitions.assembler()["motoneige"] == motoneige.pour_le_navigateur(carte.exporter())


def test_le_defi_l_hiver_apres_le_tour_des_erables():
    d = next(q for q in missions.DEFIS if q["slug"] == "motoneige")
    assert d["hiver"] is True and d["conduite"] == "balises" and d["regles"]["vehicule"] == "motoneige"
    assert d["debloque"] == {"apres": ["tour_erables"]}, "un panneau ouvert dès le départ naîtrait au démarrage"
    assert 0 < d["prime"] <= 150
