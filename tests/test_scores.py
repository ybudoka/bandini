import json

import pytest

from app import economie
from app.scores import ScoreInvalide, Tableau, valider

BON = {"pseudo": "Rocco", "fortune": 500, "missions": 0, "proprietes": 0, "duree_s": 120}


def test_valider_nettoie_le_pseudo():
    assert valider({**BON, "pseudo": "  Léa   Tremblay "})["pseudo"] == "Léa Tremblay"


@pytest.mark.parametrize(
    "donnees",
    [
        None,
        [],
        {**BON, "pseudo": ""},
        {**BON, "pseudo": "<script>"},
        {**BON, "pseudo": "x" * 17},
        {**BON, "fortune": -1},
        {**BON, "fortune": "3"},
        {**BON, "fortune": True},
        {**BON, "fortune": economie.FORTUNE_MAX + 1},
        {**BON, "missions": 99},
        {**BON, "proprietes": 99},
        {**BON, "duree_s": 0},
        # Invraisemblable : un million en dix secondes.
        {**BON, "fortune": 1_000_000, "duree_s": 10},
    ],
)
def test_valider_refuse(donnees):
    with pytest.raises(ScoreInvalide):
        valider(donnees)


def test_tableau_trie_par_fortune_puis_missions(tmp_path):
    tableau = Tableau(tmp_path / "d")
    tableau.ajouter({**BON, "pseudo": "a", "fortune": 500})
    tableau.ajouter({**BON, "pseudo": "b", "fortune": 900})
    _, rang = tableau.ajouter({**BON, "pseudo": "c", "fortune": 900, "duree_s": 60})
    assert rang == 1  # meme fortune, plus vite
    assert [s["pseudo"] for s in tableau.meilleurs()] == ["c", "b", "a"]


def test_tableau_ne_garde_que_les_meilleurs(tmp_path):
    tableau = Tableau(tmp_path / "d")
    for i in range(60):
        tableau.ajouter({**BON, "pseudo": f"j{i}", "fortune": i})
    contenu = json.loads((tmp_path / "d" / "scores.json").read_text())
    assert len(contenu) == 50
    assert contenu[0]["fortune"] == 59


def test_fichier_corrompu_ne_plante_pas(tmp_path):
    dossier = tmp_path / "d"
    dossier.mkdir()
    (dossier / "scores.json").write_text("{pas du json")
    tableau = Tableau(dossier)
    assert tableau.meilleurs() == []
    tableau.ajouter(BON)
    assert len(tableau.meilleurs()) == 1
