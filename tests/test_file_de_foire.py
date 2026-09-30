"""La file pour entrer à la foire, côté Python : le rectangle du serpentin, et le grillage qui ne s'enjambe plus
(docs/jalons/une-file-pour-entrer-a-la-foire.md ; le navigateur : `test_file_de_foire_js.py`)."""

import pytest
import villes

from app import carte


@pytest.fixture(scope="module")
def ville():
    return villes.exporter()


def test_le_serpentin_est_sous_la_colonne_est_de_l_arche(ville):
    """Sous l'arche, du côté est : les deux autres colonnes restent libres (on y passe, on y coupe la file).
    Un nombre IMPAIR de couloirs : la tête sort au nord, l'entrée tombe au sud, sur le trottoir."""
    f = ville["file_de_foire"]
    b = next(x for x in ville["barrieres"] if x["slug"] == "foire")
    assert (f["x"], f["y"]) == (b["x"] + b["l"] - 1, b["y"] + b["h"])
    assert f["l"] % 2 == 1 and f["l"] >= 3
    assert f["h"] == carte.FOIRE["file"]["rangees"]
    assert len(f["par_heure"]) == 24 and max(f["par_heure"]) > 0 and min(f["par_heure"]) == 0


def test_le_serpentin_ne_prend_ni_la_rue_ni_un_decor(ville):
    """Sur l'herbe et le trottoir, rien dessus — la colonne d'arrivée comprise. Et au nord, le grillage : on ne
    sort du serpentin que par l'arche."""
    f, sol = ville["file_de_foire"], ville["sol"]
    decor = {(d["x"], d["y"]) for d in ville["decor"]}
    for y in range(f["y"], f["y"] + f["h"]):
        for x in range(f["x"], f["x"] + f["l"] + 1):
            g = sol[y][x]
            assert carte.solidite(g) == 0 and not carte.routier(g) and carte.marchable(g), (x, y, g)
            assert (x, y) not in decor, (x, y)
    assert all(sol[f["y"] - 1][x] == carte.GRILLAGE_DE_FOIRE for x in range(f["x"] + 1, f["x"] + f["l"])), (
        "au nord d'un couloir, autre chose que le grillage")


def test_le_grillage_de_la_foire_ne_s_enjambe_pas():
    """« Je veux que la clôture soit infranchissable. » Le même grillage à voir, la solidité du barbelé."""
    fiche = carte.LEGENDE[carte.GRILLAGE_DE_FOIRE]
    assert fiche["cloture"] == "grillage" and carte.solidite(carte.GRILLAGE_DE_FOIRE) == 5
    assert not carte.franchissable(carte.GRILLAGE_DE_FOIRE)
    assert carte.GRILLAGE_DE_FOIRE not in carte.ENJAMBABLES and carte.GRILLAGE_DE_FOIRE not in carte.CLOTURES
