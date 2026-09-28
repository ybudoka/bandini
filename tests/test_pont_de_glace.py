"""Le pont de glace, côté Python (docs/jalons/le-pont-de-glace.md) : le chemin se lit sur la ville finie
sans la toucher — de l'eau entre l'île et une terre qui mène à une route — et le grand froid est en hiver."""

import villes

from app import calendrier, carte, pont_de_glace


def test_le_chemin_est_de_l_eau_de_l_ile_a_une_route():
    v = villes.generer()
    c = pont_de_glace.chemin(v, carte.LEGENDE)
    assert c, "pas de chemin : la baie ne prendrait nulle part"
    sol, ile = v["sol"], v["ile"]
    assert all(sol[y][x] == "~" for x, y in c["tuiles"]), "le chemin gèle autre chose que de l'eau"
    o, e = c["ouest"], c["est"]
    assert ile["x"] <= o["x"] < ile["x"] + ile["l"] and ile["y"] <= o["y"] < ile["y"] + ile["h"], "il ne part pas de l'île"
    assert sol[o["y"]][o["x"]] != "~" and sol[e["y"]][e["x"]] != "~"
    assert any(carte.LEGENDE.get(sol[e["y"]][e["x"] + k], {}).get("route") for k in range(pont_de_glace.CHEMIN["route_a"])), (
        "de l'autre côté, pas de route : on n'y va pas en char")
    assert c["sapins"] and all(sol[y][x] == "~" and [x, y] not in c["tuiles"] for x, y in c["sapins"])


def test_le_chemin_ne_touche_pas_la_ville_et_voyage_au_navigateur():
    v = villes.generer()
    avant = repr(v)
    assert pont_de_glace.chemin(v, carte.LEGENDE) == pont_de_glace.chemin(v, carte.LEGENDE)
    assert repr(v) == avant
    assert villes.assembler()["pont"] == pont_de_glace.pour_le_navigateur(villes.exporter(), carte.LEGENDE)


def test_le_grand_froid_est_en_hiver_et_jamais_le_premier_jour():
    jours = pont_de_glace.FROID["jours"]
    assert min(jours) >= 2 and all(calendrier.saison(j) == "hiver" for j in jours)
    assert 0 < pont_de_glace.FROID["degel_h"] < 24 and pont_de_glace.FROID["craque_s"] > 1
