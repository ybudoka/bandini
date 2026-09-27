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
