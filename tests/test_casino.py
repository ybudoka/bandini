"""Le casino du Dragon d'or, sur la carte (docs/jalons/le-casino-du-petit-canton.md, vague 1).

Un lieu garanti de la bande nord, au Petit-Canton, au nord de la place du marché : sa porte donne sur la rue
qui longe la place ; sa grande salle a dix-huit machines à sous et quatre vidéopokers ; son enseigne est la
sienne. La ville d'avant n'en sait rien (`test_canton`, `test_nord`).
"""

import pytest

from app import carte, casino, nord


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


def test_le_dragon_d_or_est_au_petit_canton_face_a_la_place(ville):
    portes = [p for p in ville["portes"] if p["lieu"] == "nord_casino"]
    assert len(portes) == 1 and portes[0]["interieur"] == "nord_casino", portes
    porte = portes[0]
    assert nord.LECTEUR.district_en(porte["x"], porte["y"]) == "canton"
    # La place du marché est de l'autre côté de la rue : son pavé commence à moins de dix tuiles au sud.
    ch = nord._bande()
    k = next(k for k, r in enumerate(nord.district("canton")["plan"]) if "o" in r)
    assert 0 < ch.yb[k] - porte["y"] < 10, (porte, ch.yb[k])
    points = [p for p in ville["points_interet"] if p["slug"] == "nord_casino"]
    assert len(points) == 1 and points[0]["famille"] in carte.FAMILLES_DE_LIEU
    enseignes = [d for d in ville["devantures"] if d["texte"] == "DRAGON D'OR"]
    assert len(enseignes) == 1


def test_un_grand_casino_et_sa_salle_a_la_mesure(ville):
    """Grand : trente-deux tuiles de façade. Et la salle en a autant, plancher pour plancher."""
    porte = next(p for p in ville["portes"] if p["lieu"] == "nord_casino")
    assert porte["vitrine"][1] >= 30, porte
    assert carte.mesures_de_la_suite("nord_casino", ville["interieurs"]) == (porte["vitrine"][1], 9)


def test_la_salle_a_ses_machines(ville):
    salle = ville["interieurs"]["nord_casino"]
    assert salle["slug"] == casino.PIECE["slug"]
    points = salle["points"]
    sous = [p for p in points if p["type"] == "machine_a_sous"]
    poker = [p for p in points if p["type"] == "videopoker"]
    assert len(sous) == 18 and len(poker) == 4, (len(sous), len(poker))
    assert "$" in carte.LEGENDE and carte.LEGENDE["$"]["meuble"]


def test_rien_du_casino_dans_la_ville_d_avant():
    avant = carte.generer(nord=False)
    assert not [p for p in avant["portes"] if "casino" in p["lieu"]]
    assert "nord_casino" not in avant["interieurs"]
