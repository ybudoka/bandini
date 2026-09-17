"""La nuit de déneigement (M12), jugée en Python : son calendrier et ses panneaux.

« La veille d'une opération, un feu orange clignote sur le panneau de la rue :
interdiction de stationner cette nuit-là, et ce qui reste dans la rue part au lot. »
"""

from __future__ import annotations

import pytest

from app import carte


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def test_elle_s_annonce_bien_avant_la_nuit_ou_n_arrive_pas(ville):
    """⚠️ Le juge du plan : « la nuit de déneigement s'annonce la veille ou n'arrive pas ».
    L'annonce tombe le même jour que l'opération, au moins six heures avant ; l'opération
    finit le matin, avant l'annonce suivante ; et jamais un soir de tempête."""
    n, t = ville["neige"]["deneigement"], ville["neige"]["tempete"]
    assert n["debut_h"] - n["annonce_h"] >= 6, "on n'a pas le temps de lire le panneau"
    assert 0 < n["fin_h"] < n["annonce_h"] < n["debut_h"] < 24
    assert n["apres_tempete_jours"] >= 1
    assert t["tous_les"] > n["apres_tempete_jours"] + 1, "une opération tomberait un soir de tempête"


def test_chaque_secteur_a_ses_panneaux_sur_ses_trottoirs(ville):
    n = ville["neige"]["deneigement"]
    decor = {(d["x"], d["y"]) for d in ville["decor"]}
    portes = {(p["x"], p["y"] + 1) for p in ville["portes"]}
    for secteur in n["secteurs"]:
        zones = [z for z in ville["zones"] if z.get("district") == secteur]
        panneaux = n["panneaux"][secteur]
        assert len(panneaux) >= 8, f"{secteur} : {len(panneaux)} panneaux, on ne les verrait pas"
        for x, y in panneaux:
            assert ville["sol"][y][x] == ".", f"{secteur} : un panneau hors du trottoir en {(x, y)}"
            assert (x, y) not in decor and (x, y) not in portes
            assert any(z["x"] <= x < z["x"] + z["l"] and z["y"] <= y < z["y"] + z["h"] for z in zones)
