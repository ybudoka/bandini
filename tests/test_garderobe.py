"""La garde-robe : des squelettes qu'on habille (catalogue Python).

Demande de Martin (22 sept. 2026) : « des squelettes qu'on habille, ce qui donne une presque
infinité d'habillement », « plusieurs types de squelettes pour les types de personnes ».
Le dessin est jugé dans `test_garderobe_js.py`.
"""

import re
from pathlib import Path

from app import garderobe, missions, pietons, visages

JS = (Path(__file__).resolve().parent.parent / "static" / "js" / "garderobe.js").read_text(encoding="utf-8")


def test_chaque_garde_robe_habille_un_archetype_au_corps_commun():
    archs = {a["slug"]: a for a in pietons.CATALOGUE}
    for slug in garderobe.GARDE_ROBES:
        assert slug in archs, f"garde-robe pour personne : {slug}"
        assert archs[slug]["sprite"] == "joueur", f"{slug} a un corps dessiné à la main"


def test_les_garde_robes_piochent_dans_les_listes_fermees():
    for slug, g in garderobe.GARDE_ROBES.items():
        assert set(g["squelettes"]) <= set(garderobe.SQUELETTES), slug
        assert set(g["coiffures"]) <= set(garderobe.COIFFURES), slug
        assert set(g["hauts"]) <= set(garderobe.HAUTS), slug
        assert set(g["bas"]) <= set(garderobe.BAS), slug
        assert set(g["chapeaux"]) <= set(garderobe.CHAPEAUX) - {"aucun"}, slug
        assert set(g["motifs"]) <= set(garderobe.MOTIFS), slug
        assert set(g["souliers"]) <= set(garderobe.SOULIERS), slug
        assert set(g["accessoires"]) <= set(garderobe.ACCESSOIRES), slug
        assert all(0 < p <= 1 for p in g["accessoires"].values()), slug
        for famille in g["couleurs_haut"] + g["couleurs_bas"] + g["couleurs_chapeau"]:
            assert famille == "gang" or famille in garderobe.COULEURS, (slug, famille)
        assert 0 <= g["chapeau_chance"] <= 1
        assert not g["chapeaux"] or g["chapeau_chance"] > 0


def test_un_gang_garde_sa_couleur():
    """On reconnaît un gang dans la rue à sa couleur : la garde-robe ne la tire pas."""
    robes = garderobe.exporter()["garde_robes"]
    for a in pietons.CATALOGUE:
        if a["gang"] and a["slug"] in robes:
            assert robes[a["slug"]]["haut_fixe"] == a["couleurs"]["c"], a["slug"]


def test_chaque_personnage_a_sa_tenue_et_le_chapeau_de_son_portrait():
    tenues = garderobe.exporter()["personnages"]
    assert set(tenues) == {p["slug"] for p in missions.PERSONNAGES}
    for p in missions.PERSONNAGES:
        t = tenues[p["slug"]]
        assert t["squelette"] in garderobe.SQUELETTES and t["coiffure"] in garderobe.COIFFURES
        assert t["haut"] in garderobe.HAUTS and t["bas"] in garderobe.BAS
        assert t["chapeau"] in garderobe.CHAPEAUX and set(t["accessoires"]) <= set(garderobe.ACCESSOIRES)
        assert t["couleur_haut"] == p["couleurs"]["c"] and t["peau"] == p["couleurs"]["s"]
        # Un chapeau au portrait, un chapeau dans la rue — et inversement.
        assert (visages.VISAGES[p["slug"]]["chapeau"] != "aucun") == (t["chapeau"] != "aucun"), p["slug"]
    assert tenues["bouchard"]["chapeau"] == "kepi"
    assert tenues["mo"]["chapeau"] == "tuque"
    assert tenues["bonimenteur"]["chapeau"] == "canotier"


def test_le_dessin_connait_chaque_piece():
    """Une pièce que Python nomme et que `garderobe.js` ne dessine pas serait invisible."""
    for chapeau in garderobe.CHAPEAUX:
        if chapeau != "aucun":
            assert re.search(rf"^\s+{chapeau}: ", JS, re.M), f"chapeau « {chapeau} » sans dessin"
    for mot in (garderobe.COIFFURES + garderobe.HAUTS + garderobe.BAS + garderobe.SOULIERS
                + garderobe.ACCESSOIRES + garderobe.MOTIFS + garderobe.SQUELETTES):
        if mot in ("courte", "uni", "pantalon", "souliers", "chandail", "homme"):
            continue   # le squelette tel quel
        assert re.search(rf"['.]{mot}\b|\b{mot}:", JS), f"« {mot} » : garderobe.js ne le dessine nulle part"


def test_le_paquet_porte_la_garde_robe(paquet):
    assert set(paquet["garderobe"]["garde_robes"]) == set(garderobe.GARDE_ROBES)
