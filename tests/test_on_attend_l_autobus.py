"""On attend l'autobus (M12) : les réglages que Python donne au navigateur."""

import re
from pathlib import Path

from app import autobus

ENTITES = (Path(__file__).resolve().parent.parent / "static" / "js" / "entites.js").read_text(encoding="utf-8")


def test_on_nait_a_l_abribus_hors_de_l_ecran_et_dans_la_bulle():
    """La vue fait 480 × 270 : au-delà de 276 px du joueur, on est forcément dehors.
    Et un passant au-delà de la bulle d'oubli serait effacé à l'image suivante."""
    a = autobus.ATTENTE
    oubli = int(re.search(r"BULLE_OUBLI = (\d+)", ENTITES).group(1))
    demi_diagonale = (240 ** 2 + 135 ** 2) ** 0.5
    assert demi_diagonale < a["naissance_min_px"] < a["naissance_max_px"] < oubli


def test_les_reglages_de_l_attente_tiennent_debout():
    a, h = autobus.ATTENTE, autobus.HORAIRE
    assert 1 <= a["par_abri"] <= 3, "plus de trois, c'est une file, pas un abribus"
    assert 0 < a["part_nuit"] < a["part"] <= 1, "la nuit, moins de monde"
    assert 1 <= a["arrets_min"] <= a["arrets_max"], "on ne descend pas là où l'on est monté"
    assert a["montee_images"] + 40 < h["arret_images"], "le temps de s'avancer et de monter, portes ouvertes"
    assert 0 < a["pas_px"] <= 1.2, "on marche jusqu'à la porte, on ne s'y téléporte pas"


def test_le_paquet_porte_l_attente():
    from app import carte
    ville = carte.generer()
    assert ville["autobus"]["attente"] == autobus.ATTENTE
