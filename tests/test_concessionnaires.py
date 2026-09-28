"""Les concessionnaires : Prestige Automobiles aux Érables, Chez Ti-Pout dans les Friches
(docs/jalons/les-concessionnaires-le-neuf-aux-erables-l-usage-dans-les-friches.md).

Martin (28 sept. 2026) : « je veux un vendeur de voitures neuves dans un quartier riche avec plusieurs voitures
dans le stationnement et un vendeur de voitures usagées dans un quartier plus pauvre ou industriel ».

Ici, la ville : où ils sont, leur lot, ce qu'ils vendent, et qu'ils ne déplacent rien. Les chars qui naissent et
qui sonnent se jugent au banc (`test_concessionnaires_js.py`).
"""

import json
from functools import lru_cache
from unittest import mock

from app import carte, concessionnaires, nord, vehicules


@lru_cache(maxsize=1)
def _ville():
    return carte.generer()


def _lot(ville, slug):
    return next((lot for lot in ville.get("concessionnaires") or [] if lot["slug"] == slug), None)


def _porte(ville, slug):
    return next((p for p in ville["portes"] if p.get("interieur") == slug), None)


def _sans_des():
    """Un dé tiré lève : la place se MESURE, elle ne se tire pas."""
    leve = AssertionError("un de tire")
    return (mock.patch.object(carte.Des, "suivant", side_effect=leve),
            mock.patch.object(carte.Des, "chance", side_effect=leve),
            mock.patch.object(carte.Des, "entier", side_effect=leve))


# --- Prestige Automobiles -----------------------------------------------------------------------


def test_le_salon_est_aux_erables_en_cossu():
    ville = _ville()
    assert _lot(ville, "prestige"), "pas de Prestige Automobiles"
    porte = _porte(ville, "prestige")
    assert porte and porte["lieu"] == "prestige"
    assert nord.LECTEUR.district_en(porte["x"], porte["y"]) == "erables"
    assert nord.LECTEUR.standing_en(porte["x"], porte["y"]) == "cossu"
    piece = ville["interieurs"]["prestige"]
    assert "commis" in [g["qui"] for g in piece["gens"]]
    # La porte s'ouvre sur du marchable : on sort sur le trottoir, pas dans un mur.
    assert carte.solidite(ville["sol"][porte["y"] + 1][porte["x"]]) == 0


def test_le_lot_du_salon_est_garni():
    ville = _ville()
    lot, porte = _lot(ville, "prestige"), _porte(ville, "prestige")
    sol = ville["sol"]
    assert len(lot["garees"]) >= 6, "« plusieurs voitures dans le stationnement »"
    for place in lot["places"]:
        assert place["sens"] == "N"
        assert sol[place["y"]][place["x"]] == sol[place["y"] + 1][place["x"]] == "^", place
    # La place en face de la porte reste libre : c'est la qu'on se gare pour entrer acheter.
    en_face = min(range(len(lot["places"])), key=lambda i: abs(lot["places"][i]["x"] - porte["x"]))
    assert en_face not in lot["garees"]
    assert len(lot["stock"]) == len(lot["places"])


def test_le_stock_du_neuf():
    lot = _lot(_ville(), "prestige")
    assert {s["slug"] for s in lot["stock"]} <= {"sport", "luxe", "auto"}
    assert lot["usure"] == 1.0 and lot["alarme"] is True and lot["genre"] == "neuf"
    catalogue = {v["slug"]: v["prix"] for v in vehicules.CATALOGUE}
    assert all(s["prix"] == catalogue[s["slug"]] for s in lot["stock"]), "le neuf se vend au prix du catalogue"


def test_le_stock_de_l_usage_coute_quarante_pour_cent():
    lot = _lot(_ville(), "ti_pout")
    catalogue = {v["slug"]: v["prix"] for v in vehicules.CATALOGUE}
    assert all(s["prix"] == round(catalogue[s["slug"]] * 0.4) for s in lot["stock"])


def test_on_achete_au_comptoir():
    """Chaque pièce a son point `concession`, qui nomme SON lot : c'est lui qui vend."""
    ville = _ville()
    for slug in ("prestige", "ti_pout"):
        points = ville["interieurs"][slug]["points"]
        assert [(p["type"], p.get("lot")) for p in points] == [("concession", slug)], points


def test_le_salon_ne_tire_aucun_de():
    original = concessionnaires.poser_le_salon

    def surveille(chantier, ville):
        a, b, c = _sans_des()
        with a, b, c:
            return original(chantier, ville)

    with mock.patch.object(concessionnaires, "poser_le_salon", surveille):
        ville = carte.generer(nord=False)
    assert _lot(ville, "prestige")


def test_le_salon_ne_deplace_rien(monkeypatch):
    """La ville d'avant, identique hors du Salon : on AJOUTE une porte, une devanture, un point et une pièce au
    bout de leurs listes, et les tuiles changent dans la cour seulement."""
    avec = carte.generer(nord=False)
    monkeypatch.setattr(concessionnaires, "poser_le_salon", lambda chantier, ville: None)
    sans = carte.generer(nord=False)
    touchees = ("sol", "portes", "devantures", "interieurs", "points_interet", "concessionnaires", "decor", "lampes")
    for cle in avec:
        if cle in touchees:
            continue
        assert json.dumps(avec[cle], sort_keys=True) == json.dumps(sans[cle], sort_keys=True), cle
    for cle in ("portes", "devantures", "points_interet"):
        assert avec[cle][:len(sans[cle])] == sans[cle], cle
        assert len(avec[cle]) == len(sans[cle]) + 1, cle
    assert set(avec["interieurs"]) - set(sans["interieurs"]) == {"prestige"}
    cour = _lot(avec, "prestige")["cour"]
    for y, (a, b) in enumerate(zip(avec["sol"], sans["sol"])):
        for x, (ga, gb) in enumerate(zip(a, b)):
            if ga != gb:
                assert cour["x"] <= x < cour["x"] + cour["l"] and cour["y"] <= y < cour["y"] + cour["h"], (x, y)


def test_sans_stationnement_pas_de_salon(monkeypatch):
    monkeypatch.setattr(concessionnaires, "SALON_CASES_MIN", 99)
    ville = carte.generer(nord=False)
    assert not _lot(ville, "prestige")
    assert not _porte(ville, "prestige")


# --- Chez Ti-Pout ---------------------------------------------------------------------------------


def test_ti_pout_est_dans_les_friches():
    ville = _ville()
    assert _lot(ville, "ti_pout"), "pas de Chez Ti-Pout"
    porte = _porte(ville, "ti_pout")
    assert porte and porte["lieu"] == "ti_pout"
    assert nord.LECTEUR.district_en(porte["x"], porte["y"]) == "friches"
    assert nord.LECTEUR.standing_en(porte["x"], porte["y"]) == "pauvre"
    assert "commis" in [g["qui"] for g in ville["interieurs"]["ti_pout"]["gens"]]
    assert carte.solidite(ville["sol"][porte["y"] + 1][porte["x"]]) == 0


def test_la_cour_de_ti_pout():
    """Un grillage tout autour, une trouée au sud qui donne sur le trottoir, des chars sur le gravier."""
    ville = _ville()
    lot, sol = _lot(ville, "ti_pout"), ville["sol"]
    c = lot["cour"]
    x0, y0, x1, y1 = c["x"], c["y"], c["x"] + c["l"] - 1, c["y"] + c["h"] - 1
    tour = ([(x, y0) for x in range(x0, x1 + 1)] + [(x0, y) for y in range(y0, y1 + 1)]
            + [(x1, y) for y in range(y0, y1 + 1)])
    assert all(sol[y][x] == "f" for x, y in tour), "le grillage a un trou"
    bas = sol[y1][x0:x1 + 1]
    trouee = [x0 + i for i, g in enumerate(bas) if g != "f"]
    assert len(trouee) == 5 and trouee == list(range(trouee[0], trouee[0] + 5)), bas
    assert all(carte.solidite(sol[y1 + 1][x]) == 0 for x in trouee), "la trouée donne sur un mur"
    assert len(lot["garees"]) >= 5
    for place in lot["places"]:
        autre = place["y"] - 1 if place["sens"] == "S" else place["y"] + 1
        assert sol[place["y"]][place["x"]] == sol[autre][place["x"]] == "g", place
    assert {s["slug"] for s in lot["stock"]} <= {"auto", "camion"}
    assert lot["usure"] == 0.6 and lot["alarme"] is False and lot["genre"] == "usage"


def test_ti_pout_ne_tire_aucun_de():
    original = concessionnaires.poser_ti_pout

    def surveille(ville):
        a, b, c = _sans_des()
        with a, b, c:
            return original(ville)

    with mock.patch.object(concessionnaires, "poser_ti_pout", surveille):
        ville = carte.generer()
    assert _lot(ville, "ti_pout")


def test_ti_pout_ne_deplace_rien(monkeypatch):
    """⚠️ La cour se choisit SANS décor ni lampe dedans : ces listes-là ne bougent pas non plus (le jeu tire
    dans le décor par son index)."""
    avec = carte.generer()
    monkeypatch.setattr(concessionnaires, "poser_ti_pout", lambda ville: None)
    sans = carte.generer()
    touchees = ("sol", "portes", "devantures", "interieurs", "points_interet", "concessionnaires", "lampes")
    for cle in avec:
        if cle in touchees:
            continue
        assert json.dumps(avec[cle], sort_keys=True) == json.dumps(sans[cle], sort_keys=True), cle
    # La lampe de la vitrine de la roulotte, et rien d'autre, s'ajoute au bout.
    for cle in ("portes", "devantures", "points_interet", "concessionnaires", "lampes"):
        assert avec[cle][:len(sans[cle])] == sans[cle], cle
        assert len(avec[cle]) == len(sans[cle]) + 1, cle
    cour = _lot(avec, "ti_pout")["cour"]
    for y, (a, b) in enumerate(zip(avec["sol"], sans["sol"])):
        for x, (ga, gb) in enumerate(zip(a, b)):
            if ga != gb:
                assert cour["x"] <= x < cour["x"] + cour["l"] and cour["y"] <= y < cour["y"] + cour["h"], (x, y)


def test_la_ville_d_avant_n_a_pas_ti_pout():
    assert not _lot(carte.generer(nord=False), "ti_pout")
