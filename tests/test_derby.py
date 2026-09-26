"""Le derby de démolition, côté Python (docs/jalons/le-derby-de-demolition-a-la-foire.md) : l'arène se
lit sur la ville finie sans rien y poser, à côté de la foire et hors de tout ; le défi se tient."""

from app import carte, definitions, derby, economie, missions


def _ville():
    return carte.generer()


def test_l_arene_est_du_gazon_libre_a_cote_de_la_foire_et_hors_de_tout():
    v = _ville()
    a = derby.arene(v)
    assert a, "pas d'arène : le derby n'a nulle part où se jouer"
    f = v["foire"]
    enclos = {(x, s[0]) for s in v["foire_enclos"] for x in range(s[1], s[2] + 1)}
    decor = {(d["x"], d["y"]) for d in v["decor"]}
    for y in range(a["y"], a["y"] + a["h"]):
        for x in range(a["x"], a["x"] + a["l"]):
            assert v["sol"][y][x] == ",", (x, y, v["sol"][y][x])
            assert (x, y) not in enclos and (x, y) not in decor, (x, y)
    assert a["x"] >= f["x"] + f["l"], "l'arène déborde sur la foire à pied"
    assert abs((a["x"]) - (f["x"] + f["l"])) < derby.ARENE["portee"], "l'arène n'est pas à côté de la foire"
    p = a["panneau"]
    assert not (a["x"] <= p["x"] < a["x"] + a["l"] and a["y"] <= p["y"] < a["y"] + a["h"]), "le panneau est dans l'arène"


def test_l_arene_ne_deplace_rien_et_voyage_au_navigateur():
    """⚠️ Elle se LIT : la ville d'avant et d'après sont les mêmes, et deux lectures donnent la même."""
    v = _ville()
    avant = repr(v)
    a, b = derby.arene(v), derby.arene(v)
    assert repr(v) == avant and a == b
    assert definitions.assembler()["derby"] == derby.pour_le_navigateur(carte.exporter())


def test_le_defi_se_joue_le_soir_s_ouvre_apres_la_galerie_et_paie_modestement():
    d = next(q for q in missions.DEFIS if q["slug"] == "derby")
    assert d["soir"] is True and d["conduite"] == "derby"
    assert d["debloque"] == {"apres": ["tir"]}, "un panneau ouvert dès le départ naîtrait au démarrage"
    r = d["regles"]
    assert d["chrono_s"] == r["temps_s"] + r["attente_s"], "deux chronos à l'écran qui ne disent pas la même chose"
    taxi = economie.BOULOTS["taxi"]
    taxi_a_l_heure = economie.gain_boulot(taxi) / (20 * taxi["etapes"]) * 3600
    assert 0 < d["prime"] <= 150 and d["prime"] < taxi_a_l_heure
    assert len(derby.BAZOUS) >= r["bazous"] + 1
