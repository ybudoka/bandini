"""La navette de l'Île-aux-Corneilles (docs/jalons/l-ile-aux-corneilles.md, troisième vague).

Un deuxième bateau, pas une troisième escale : le traversier des Quais à La Pointe ne change pas (ses juges).
"""

from unittest import mock

import pytest

from app import carte, ile, navette, traversier


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


def test_des_quais_a_la_jetee_de_l_ile(ville):
    n = ville["navette"]
    assert n, "pas de navette"
    a, b = n["escales"]
    assert a["district"] == "quais" and b["district"] == ile.ILE["slug"] and b["nom"] == ile.ILE["nom"]
    # À l'île, on débarque sur des planches de quai, et nulle part ailleurs.
    assert b["acces"] and all(ville["sol"][y][x] == "Q" for x, y in b["acces"]), b["acces"]
    assert n["decalage_h"] == 1.0, "elle part quand le traversier arrive"


def test_elle_ne_croise_ni_le_traversier_ni_rien_a_quai(ville):
    """Son couloir est de l'eau, ne passe ni sur le traversier ni sur son débarcadère ; ses débarcadères sont
    libres de tout décor (rien ne s'y pose, rien ne s'y déplace)."""
    n, t = ville["navette"], ville["traversier"]
    a, b = n["escales"]
    eau = lambda x, y: ville["sol"][y][x] == "~"  # noqa: E731
    for x0, y0, x1, y1 in traversier.balayage(a, b):
        assert all(eau(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)), (x0, y0)
    du_traversier = set().union(*(traversier.debarcadere(q) for q in t["escales"]))
    du_traversier |= {(x, y) for x0, y0, x1, y1 in traversier.balayage(*t["escales"])
                      for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    sien = {(x, y) for x0, y0, x1, y1 in traversier.balayage(a, b) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    assert not sien & du_traversier
    occupees = {(d["x"], d["y"]) for d in ville["decor"]}
    for q in (a, b):
        assert not traversier.debarcadere(q) & occupees, q


def test_elle_n_ajoute_que_sa_cle():
    with mock.patch.object(navette, "tracer", lambda v: None):
        sans = carte.generer()
    avec = carte.generer()
    for cle in avec:
        if cle != "navette":
            assert avec[cle] == sans[cle], f"« {cle} » a bougé"
