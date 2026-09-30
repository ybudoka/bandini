"""Des bagarres de gangs vivantes, et armées — la fiche (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md)."""

from pathlib import Path

import villes

from app import rixes

RIXE_JS = Path(__file__).resolve().parent.parent / "static" / "js" / "rixe.js"


def test_la_fiche_du_contact_se_tient():
    """Des chiffres qui se contredisent font un combat qui grince."""
    f = rixes.CONTACT
    assert 0 < f["cercle_px"] < f["portee_px"], "sa place doit être à portée de coup"
    assert 0 <= f["cadence_ecart"] < f["cadence_images"]
    # Il revient de son recul AVANT son prochain coup : sinon il frappe dans le vide, de loin.
    assert f["recul_images"] < f["cadence_images"] - f["cadence_ecart"]
    assert 0 < f["recul_allure"] <= 1
    assert 0 < f["tourne_min"] <= f["tourne_max"]
    assert 0 < f["pas_images"] < f["tourne_min"], "un pas de côté plus long que l'attente entre deux"
    assert 0 <= f["esquive_pct"] <= 100


def test_le_paquet_porte_la_fiche_des_rixes():
    """⚠️ « Une fiche que le navigateur ne lisait pas » — le dépôt a payé ce défaut huit fois."""
    assert villes.assembler()["rixes"] == rixes.exporter()


def test_le_cerveau_ne_tire_aucun_de_du_jeu():
    """⚠️ Un dé tiré ici décalerait tout le hasard de la ville : tout se lit à l'empreinte."""
    source = RIXE_JS.read_text(encoding="utf-8")
    assert "B.rng" not in source and "Math.random" not in source
