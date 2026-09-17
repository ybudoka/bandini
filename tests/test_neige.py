"""La tempête de neige (M12), jugée en Python : quand elle tombe, ce qu'elle fait, la charrue.

⚠️ `neige.py` ne pose rien : il règle. La tempête est une fonction du jour et de l'heure,
la charrue suit une boucle d'autobus.
"""

from __future__ import annotations

import pytest

from app import autobus, carte, neige


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def test_pas_de_tempete_le_premier_soir_et_une_tous_les_trois_jours(ville):
    t = ville["neige"]["tempete"]
    assert t["premier"] >= 2, "le premier soir d'une partie glisse déjà"
    assert 2 <= t["tous_les"] <= 7
    assert 12 <= t["debut_h"] < t["fin_h"] <= 24, "une tempête de soirée"
    assert 0 < t["montee_h"] < (t["fin_h"] - t["debut_h"]) / 2


def test_ce_que_la_neige_fait_reste_jouable(ville):
    """Elle divise l'adhérence sans la tuer, la charrue en rend l'essentiel, et le voile
    laisse voir la rue."""
    e = ville["neige"]["effets"]
    assert 0.15 <= e["adherence"] < e["adherence_deneigee"] < 1
    assert 0.3 <= e["frein"] < 1
    assert 0.4 <= e["vitesse_trafic"] < 1
    assert 0 < e["voile"] <= 0.4, "on ne voit plus la rue"
    assert e["deneige_images"] >= 1200, "la rue déblayée se recouvre en moins d'une heure de jeu"


def test_la_charrue_fait_une_boucle_par_ses_lieux(ville):
    c = ville["neige"]["charrue"]
    assert c, "la charrue n'a pas de tournée"
    boucle = autobus.derouler(c["trace"])
    assert len(boucle) >= 100
    reseau = autobus._Reseau(ville)
    n = len(boucle)
    for i in range(n):
        (x, y), (nx, ny) = boucle[i], boucle[(i + 1) % n]
        assert abs(nx - x) + abs(ny - y) == 1
    assert not set(boucle) & reseau.interdites, "la charrue passe où la ville peut fermer"
    for slug in neige.CHARRUE["passe_par"]:
        lieu = next(p for p in ville["points_interet"] if p["slug"] == slug)
        assert min(abs(x - lieu["x"]) + abs(y - lieu["y"]) for x, y in boucle) <= 20, f"la charrue ne passe pas par {slug}"


def test_la_ville_est_la_meme_avec_ou_sans_neige(ville, monkeypatch):
    monkeypatch.setattr(neige, "tracer", lambda v: None)
    sans = carte.generer()
    for cle in ville:
        if cle == "neige":
            continue
        assert sans[cle] == ville[cle], f"« {cle} » a bougé"
