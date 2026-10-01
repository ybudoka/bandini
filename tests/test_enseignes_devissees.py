"""Les enseignes qu'on dévisse la nuit (P4, des choses à collectionner, vague 5) : douze néons, chacun au bout d'une
devanture qui porte son nom, choisis par une règle qui LIT la ville finie — sans un dé, sans rien y poser ; leur
catalogue voyage avec les collections, et rien dans les définitions ni dans la carte.
"""

import copy
import json
import os

from app import audio, carte, collectionner, decoration, devisser, recherche
from tests import villes


def _ville():
    return villes.generer()


def test_douze_enseignes_qui_se_lisent_et_se_dessinent():
    slugs = [e["slug"] for e in devisser.ENSEIGNES]
    assert len(slugs) == 12 and len(set(slugs)) == 12
    for e in devisser.ENSEIGNES:
        assert len(e["grille"]) == 7 and all(len(r) == 5 for r in e["grille"]), e["slug"]
        lettres = {c for r in e["grille"] for c in r} - {"."}
        assert lettres and lettres <= set(e["palette"]), f"{e['slug']} : une couleur sans palette"
        assert len(e["lignes"]) == 2 and all(len(lg) <= 48 for lg in e["lignes"]), e["slug"]
        assert e["textes"], e["slug"]
    # Une ou deux par district de commerces, et jamais plus.
    par = {}
    for e in devisser.ENSEIGNES:
        par[e["district"]] = par.get(e["district"], 0) + 1
    assert set(par.values()) <= {1, 2} and len(par) == 7, par


def test_chacune_pend_au_bout_d_une_devanture_qui_porte_son_nom():
    v = _ville()
    places = {p["slug"]: p for p in v["collections"]["enseignes"]}
    assert set(places) == {e["slug"] for e in devisser.ENSEIGNES}, "une enseigne n'a pas trouvé sa devanture"
    devs = {(d["x"], d["y"]): d for d in v["devantures"]}
    vus = set()
    for e in devisser.ENSEIGNES:
        p = places[e["slug"]]
        d = devs.get((p["x"], p["y"]))
        assert d and d["texte"] in e["textes"], f"{e['slug']} : pas sur une devanture « {e['textes'][0]} »"
        assert d["pancarte"] and p["pancarte"] == d["pancarte"] and p["l"] == d["l"], e["slug"]
        assert p["district"] == e["district"], f"{e['slug']} pend dans {p['district']}, pas dans {e['district']}"
        assert (p["x"], p["y"]) not in vus
        vus.add((p["x"], p["y"]))


def test_elles_ne_touchent_a_rien_et_ne_tirent_aucun_de(monkeypatch):
    """La règle LIT les devantures : la ville est la même avant et après, et deux poses donnent la même chose.
    ⚠️ Jugé PENDANT la génération (un espion), pas sur la ville du cache : celle-là est déjà passée par la règle."""
    vu = {}
    vraie = devisser.poser

    def espion(v):
        vu["avant"] = json.dumps(v, sort_keys=True)
        vu["copie"] = copy.deepcopy(v)
        out = vraie(v)
        vu["apres"] = json.dumps(v, sort_keys=True)
        return out

    monkeypatch.setattr(devisser, "poser", espion)
    v = carte.generer()
    # ⚠️ Des booléens, pas deux chaînes de plusieurs Mo : pytest en calculerait le diff pendant des minutes.
    intacte = vu["avant"] == vu["apres"]
    assert intacte, "poser les enseignes a touché la ville"
    pareilles = vraie(vu["copie"]) == v["collections"]["enseignes"]
    assert pareilles, "deux poses de la même ville ne donnent pas les mêmes enseignes"


def test_son_district_d_abord_puis_l_ordre_de_lecture():
    """Trois BINGO dans la ville : celui du Faubourg l'emporte, même s'il vient après les autres en lisant ; une
    devanture sans pancarte n'en porte pas ; et une ville qui n'a pas le nom laisse l'enseigne sans place."""
    zones = [{"slug": "quais", "x": 0, "y": 0, "l": 50, "h": 50}, {"slug": "faubourg", "x": 50, "y": 0, "l": 50, "h": 50}]

    def dev(x, y, texte, pancarte=1):
        return {"x": x, "y": y, "l": 4, "texte": texte, "pancarte": pancarte}

    ville = {"zones": zones, "devantures": [dev(5, 5, "BINGO"), dev(60, 9, "BINGO", 0), dev(70, 20, "BINGO"),
                                             dev(80, 30, "BINGO")]}
    places = {p["slug"]: p for p in devisser.poser(ville)}
    assert (places["bingo"]["x"], places["bingo"]["y"]) == (70, 20)
    assert places["bingo"]["district"] == "faubourg"
    assert "rialto" not in places
    # Sans celle du Faubourg, la première ailleurs, en lisant.
    ville["devantures"] = [dev(5, 5, "BINGO"), dev(3, 40, "BINGO")]
    assert (devisser.poser(ville)[0]["x"], devisser.poser(ville)[0]["y"]) == (5, 5)


def test_elles_voyagent_avec_les_collections_et_nulle_part_ailleurs(paquets):
    defs = paquets.definitions.corps.decode("utf-8")
    ville = paquets.carte.corps.decode("utf-8")
    col = json.loads(paquets.collections.corps)
    for e in devisser.ENSEIGNES:
        assert e["lignes"][0] not in defs and e["lignes"][0] not in ville, f"{e['slug']} pèse sur le premier écran"
    liste = col["enseignes"]["liste"]
    assert [f["slug"] for f in liste] == [e["slug"] for e in devisser.ENSEIGNES], "l'ordre du mur a changé"
    assert all(isinstance(f.get("x"), int) for f in liste)
    assert col["enseignes"]["regle"]["delit"] == "effraction"


def test_la_regle_tient_a_la_police_et_a_la_planque():
    d = recherche.DELITS[devisser.REGLE["delit"]]
    assert d["etoiles"] == 1 and d["temoin"], "dévisser une enseigne : une étoile, et il faut un témoin"
    mur = [t for t in decoration.TROPHEES if t["famille"] == "enseignes"]
    assert [(t["slug"], t["palier"]) for t in mur] == [("mur_enseignes", 1)]
    assert all("mur_enseignes" in places for places in decoration.PLACES.values())
    assert set(devisser.REGLE["paliers"]) == {"6", "12"} and devisser.REGLE["vis"] == 4 and devisser.REGLE["crans"] == 4


def test_le_son_de_la_vis_est_un_son_de_lieu_qui_a_son_fichier():
    assert "devisser" in audio.LIEUX["collections"]
    racine = os.path.join(os.path.dirname(__file__), "..", "static", "audio")
    assert os.path.exists(os.path.join(racine, "devisser-1.mp3"))


def test_l_export_garde_celles_sans_place_au_catalogue():
    out = collectionner.exporter({"cartes": [], "enseignes": [{"slug": "bingo", "x": 3, "y": 4, "l": 4, "pancarte": 1,
                                                                 "district": "faubourg"}]})
    liste = {f["slug"]: f for f in out["enseignes"]["liste"]}
    assert len(liste) == 12 and liste["bingo"]["x"] == 3 and "x" not in liste["rialto"]
