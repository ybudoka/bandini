"""La ville s'agrandit au nord (docs/jalons/la-ville-s-agrandit-au-nord.md)."""

from app import carte


def test_le_chantier_lit_sa_trame_et_pas_les_globales():
    """Une autre trame passée en paramètre bâtit une autre ville, même si les globales ne bougent pas."""
    trame = {"colonnes": (10, 10), "rangees": (10,), "rues_v": (4, 4, 4), "rues_h": (4, 4),
             "districts": ({"slug": "essai", "nom": "Essai", "bx": 0, "by": 0, "gang": None,
                            "gang_nom": None, "brume": False, "pietons": 0, "vehicules": 0, "police": 0,
                            "rythme": (0.1, 1.0, 1.0), "rares": (), "plan": ("hh",), "standing": ("==",)},),
             "standing": ("==",)}
    ch = carte._Chantier(("hh",), 1, trame=trame)
    assert (ch.largeur, ch.hauteur) == (32, 18)
    assert ch.district_en(5, 5) == "essai"


# --- La bande, bâtie à part (tâche 3) --------------------------------------------------------

def _bande():
    from app import nord
    return nord.batir_la_bande()


def _dans(ch, slug, o):
    from app import nord
    x0, _y0, large, _h = ch.rect_district(nord.district(slug))
    return x0 <= o["x"] < x0 + large and o["y"] < nord.DECALAGE_NORD


def test_la_bande_fait_110_rangees_plus_la_couture_et_la_largeur_de_la_trame():
    from app import nord
    ch = _bande()
    assert ch.hauteur == nord.DECALAGE_NORD + 6 and ch.largeur == 419


def test_trois_districts_dans_la_bande_avec_leur_gang():
    from app import nord
    assert [(d["slug"], d["gang"]) for d in nord.DISTRICTS_NORD] == [
        ("friches", "chevreuils"), ("canton", "cravates"), ("gare", "boulonneux")]


def test_la_gare_a_ses_voies_ses_wagons_et_son_poste():
    from app import nord
    ch = _bande()
    x0, y0, large, _h = ch.rect_district(nord.district("gare"))
    zone = ["".join(ch.sol[y][x0:x0 + large]) for y in range(y0, nord.DECALAGE_NORD)]
    assert sum(ligne.count("T") for ligne in zone) > 200, "des voies ferrées"
    # Les wagons : du toit de tôle SUR une rangée de voie (les hangars de la gare en ont aussi, à côté).
    assert sum(ligne.count("B") for ligne in zone if "T" in ligne) > 30, "des wagons"
    postes = [p for p in ch.portes if p["interieur"] == "nord_aiguillage"]
    assert len(postes) == 1 and ch.marchable_en(postes[0]["x"], postes[0]["y"] + 1)
    assert "nord_aiguillage" in ch.pieces


def test_le_canton_n_a_que_des_terrains_a_batir():
    ch = _bande()
    assert not [p for p in ch.portes if _dans(ch, "canton", p)], "personne n'y habite encore"
    pancartes = [d for d in ch.decor if d["type"] == "pancarte_a_batir" and _dans(ch, "canton", d)]
    assert len(pancartes) >= 20, len(pancartes)


def test_les_friches_ont_leurs_carcasses_et_pas_une_porte():
    ch = _bande()
    assert [d for d in ch.decor if d["type"] == "carcasse" and _dans(ch, "friches", d)]
    assert not [p for p in ch.portes if _dans(ch, "friches", p)]


def test_tout_ce_que_la_bande_nomme_commence_par_nord():
    ch = _bande()
    assert all(k.startswith("nord_") for k in ch.pieces)
    assert all(p["interieur"].startswith("nord_") and p["lieu"].startswith("nord_") for p in ch.portes)


def test_la_bande_ne_tire_rien_de_la_ville():
    """Même graine, même bande ; et bâtir la bande ne change pas la ville."""
    avant = carte.generer()
    a, b = _bande(), _bande()
    assert a.sol == b.sol and a.decor == b.decor
    assert carte.generer()["sol"] == avant["sol"]


# --- La translation (tâche 4) ----------------------------------------------------------------

def _ville_d_avant():
    return carte.generer(nord=False)


def _decalee(ville):
    import copy
    from app import nord
    v = copy.deepcopy(ville)
    nord.decaler(v, nord.DECALAGE_NORD)
    return v


def test_une_cle_inconnue_fait_echouer_la_translation():
    import copy
    import pytest
    from app import nord
    v = copy.deepcopy(_ville_d_avant())
    v["cle_neuve"] = [{"x": 1, "y": 1}]
    with pytest.raises(KeyError, match="cle_neuve"):
        nord.decaler(v, 1)


def _objets_xy(o, chemin=()):
    """Chaque objet {x, y} de la carte, par son chemin — sauf les pièces (leurs coordonnées sont à elles)."""
    if isinstance(o, dict):
        if isinstance(o.get("x"), int) and isinstance(o.get("y"), int):
            yield chemin, o["y"]
        for k, v in o.items():
            if chemin == () and k == "interieurs":
                continue
            yield from _objets_xy(v, chemin + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _objets_xy(v, chemin + (i,))


def test_chaque_objet_xy_descend_de_110_tuiles_ou_de_110_x_16_pixels():
    from app import nord
    avant = _ville_d_avant()
    apres = dict(_objets_xy(_decalee(avant)))
    vus = 0
    for chemin, y in _objets_xy(avant):
        attendu = y + nord.DECALAGE_NORD * (carte.TUILE_PX if chemin[0] == "mouillages" else 1)
        if chemin[:2] == ("relief", "montagnes"):
            attendu = y                                   # les montagnes grandissent vers le haut
        assert apres[chemin] == attendu, chemin
        vus += 1
    assert vus > 3000, vus


def test_le_sol_de_la_ville_d_avant_est_identique_110_rangees_plus_bas():
    from app import nord
    avant = _ville_d_avant()
    v = _decalee(avant)
    n = nord.DECALAGE_NORD
    assert v["sol"][n:] == avant["sol"] and v["voie"][n:] == avant["voie"]
    assert v["hauteur"] == avant["hauteur"] + n and v["grille"]["y0"] == n
    assert v["relief"]["montagnes"]["h"] == avant["relief"]["montagnes"]["h"] + n


def test_les_paires_descendent_aussi():
    from app import nord
    avant = _ville_d_avant()
    v, n = _decalee(avant), nord.DECALAGE_NORD
    assert v["autobus"]["lignes"][0]["trace"][0][1] == avant["autobus"]["lignes"][0]["trace"][0][1] + n
    assert v["autobus"]["lignes"][0]["arrets"] == avant["autobus"]["lignes"][0]["arrets"], "des indices"
    assert v["tramway"]["arrets"][0][2] == avant["tramway"]["arrets"][0][2] + n
    assert v["tramway"]["trace"][0][1] == avant["tramway"]["trace"][0][1] + n
    assert v["eboueurs"]["points"][0][2] == avant["eboueurs"]["points"][0][2] + n
    assert v["eboueurs"]["trace"][0][1] == avant["eboueurs"]["trace"][0][1] + n
    assert v["neige"]["charrue"]["trace"][0][1] == avant["neige"]["charrue"]["trace"][0][1] + n
    assert v["chemins_des_bois"][0][1] == avant["chemins_des_bois"][0][1] + n
    assert v["foire_enclos"][0][0] == avant["foire_enclos"][0][0] + n
    assert v["train_de_foire"]["voie"][0][1] == avant["train_de_foire"]["voie"][0][1] + n
    assert v["train_de_foire"]["quai"][2] == avant["train_de_foire"]["quai"][2] + n
    assert v["montagne_russe"]["voie"][0][1] == avant["montagne_russe"]["voie"][0][1] + n * carte.TUILE_PX
    assert v["montagne_russe"]["supports"][0][2] == avant["montagne_russe"]["supports"][0][2] + n
    assert v["aeroport"]["axes"][0][1] == avant["aeroport"]["axes"][0][1] + n
    assert v["aeroport"]["axes"][0][3] == avant["aeroport"]["axes"][0][3] + n
    assert v["aeroport"]["plan"][1] == avant["aeroport"]["plan"][1] + n
    assert v["aeroport"]["balises"][0][1] == avant["aeroport"]["balises"][0][1] + n
    assert v["aeroport"]["peints"][0][2] == avant["aeroport"]["peints"][0][2] + n
    assert v["aeroport"]["portes_peintes"][0][1] == avant["aeroport"]["portes_peintes"][0][1] + n
    assert v["aeroport"]["pont"]["piles"][0][1] == avant["aeroport"]["pont"]["piles"][0][1] + n
    assert v["aeroport"]["masque"]["carte_h"] == avant["aeroport"]["masque"]["carte_h"] + n
    assert v["traversier"]["escales"][0]["acces"][0][1] == avant["traversier"]["escales"][0]["acces"][0][1] + n
    c0 = next(c for c in avant["chantiers"] if isinstance(c.get("tranchee"), list))
    c1 = next(c for c in v["chantiers"] if c["id"] == c0["id"])
    assert c1["tranchee"][0][1] == c0["tranchee"][0][1] + n and c1["signaleur"][1] == c0["signaleur"][1] + n
    x, y = next(iter(avant["arrets"])).split(",")
    assert f"{x},{int(y) + n}" in v["arrets"]
