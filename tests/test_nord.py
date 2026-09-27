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
