"""Les techniques d'arts martiaux — le catalogue (voir docs/jalons/les-techniques-d-arts-martiaux.md)."""

import re
from pathlib import Path

from app import techniques

RACINE = Path(__file__).resolve().parent.parent


def test_slugs_uniques_et_gestes_connus():
    slugs = [t["slug"] for t in techniques.CATALOGUE]
    assert len(slugs) == len(set(slugs))
    for t in techniques.CATALOGUE:
        assert t["geste"] in techniques.GESTES, t["slug"]
        assert t["style"] in techniques.STYLES, t["slug"]


def test_une_seule_etape_active_par_technique():
    for t in techniques.CATALOGUE:
        actives = [e for e in t["temps"] if e["actif"]]
        assert len(actives) == 1, t["slug"]
        for e in t["temps"]:
            assert e["pose"] in techniques.POSES, (t["slug"], e["pose"])
            assert e["images"] >= 1


def test_pas_deux_techniques_sur_le_meme_geste_et_le_meme_rang():
    vus = set()
    for t in techniques.CATALOGUE:
        cle = (t["geste"], t["rang"])
        assert cle not in vus, cle
        vus.add(cle)


def test_la_chaine_des_tapes_est_continue_et_commence_gratuite():
    rangs = [t["rang"] for t in techniques.chaine()]
    assert rangs == list(range(1, len(rangs) + 1))
    assert all(t["gratuite"] for t in techniques.chaine()[:3])


def test_les_cours_ont_un_prix_la_rue_est_gratuite():
    for t in techniques.CATALOGUE:
        if t["style"] == "rue":
            assert t["gratuite"] and t["prix"] == 0, t["slug"]
        else:
            assert not t["gratuite"] and t["prix"] > 0, t["slug"]


def test_aucune_portee_au_dela_de_ce_que_l_ecran_montre():
    base = (RACINE / "static" / "js" / "base.js").read_text(encoding="utf-8")
    vue = int(re.search(r"^const VW = (\d+);", base, re.M).group(1))
    for t in techniques.CATALOGUE:
        assert 0 < t["portee"] <= vue // 2, t["slug"]


def test_le_paquet_porte_les_techniques():
    from app import definitions
    assert definitions.assembler()["techniques"] == techniques.CATALOGUE
