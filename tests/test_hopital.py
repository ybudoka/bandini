"""L'hopital qui soigne du monde : plus grand, un etage, des malades, une salle d'attente.

Demande de Martin (16 sept. 2026) : « l'hopital devrait etre plus grand et avec
des malades, une salle d'attente, des solutes, machines de sante. »

⚠️ Mesure avant : l'hopital faisait 11 x 8 tuiles, deux lits de bois, trois
chaises et pas un malade. Ces juges tiennent la promesse de la demande, et la
regle qui la rend honnete : chaque malade est couche dans un lit, pas debout a
cote. (Ses machines distributrices, elles, se jugent avec les autres :
`test_distributrices.py`.)
"""

import pytest

from app import carte


def _suite_de_l_hopital():
    return [carte.INTERIEURS[s] for s in carte.suite_de("hopital")]


def test_l_hopital_est_plus_grand_et_a_un_etage():
    """⚠️ 54 tuiles de plancher avant. Plus grand en PROFONDEUR et par un etage :
    l'ilot fait douze tuiles de large, et une piece a exactement les mesures de
    son batiment (`test_la_piece_a_les_mesures_de_son_batiment`)."""
    suite = _suite_de_l_hopital()
    assert len(suite) >= 2, "l'hopital n'a plus d'etage"
    plancher = sum(large * haut for large, haut in (carte.mesures_de(p) for p in suite))
    assert plancher >= 3 * 54, f"{plancher} tuiles de plancher"


def test_l_hopital_a_des_malades_couches_dans_des_lits():
    malades = [(p, g) for p in _suite_de_l_hopital() for g in p["gens"] if g["qui"] == "malade"]
    assert len(malades) >= 6, f"{len(malades)} malades"
    for piece, g in malades:
        sol = piece["sol"]
        assert sol[g["y"]][g["x"]] == "r" and sol[g["y"] + 1][g["x"]] == "r", (piece["slug"], g)
    lits = sum(1 for p in _suite_de_l_hopital() for y, ligne in enumerate(p["sol"])
               for x, glyphe in enumerate(ligne) if glyphe == "r" and p["sol"][y - 1][x] != "r")
    assert len(malades) == lits, "un lit d'hopital vide, ou deux malades dans le meme"


def test_chaque_malade_a_son_solute_et_son_moniteur():
    """Le materiel est AU CHEVET : la potence a l'ouest de la tete de lit (son
    tube file vers l'est), l'ecran a l'est."""
    for piece in _suite_de_l_hopital():
        sol = piece["sol"]
        for g in piece["gens"]:
            if g["qui"] != "malade":
                continue
            x, y = g["x"], g["y"]
            assert sol[y][x - 1] == "i", f"{piece['slug']} : pas de solute au chevet en {x},{y}"
            assert sol[y][x + 1] == "q", f"{piece['slug']} : pas de moniteur au chevet en {x},{y}"


def test_l_hopital_a_une_salle_d_attente_pleine():
    urgence = carte.INTERIEURS["hopital"]
    chaises = sum(ligne.count("h") for ligne in urgence["sol"])
    patients = [g for g in urgence["gens"] if g["qui"] == "patient"]
    assert chaises >= 12, f"{chaises} chaises"
    assert len(patients) >= 5, f"{len(patients)} patients"
    assert len(patients) < chaises, "une salle d'attente sans une chaise libre"
    assert any(g["qui"] == "soignant" for g in urgence["gens"]), "personne au triage"
    assert any(p["type"] == "soigner" for p in urgence["points"])


@pytest.mark.parametrize("qui, plan, bien, mal, reproche", [
    # Un malade au PIED du lit : la tete tomberait sur la couverture.
    ("malade", "BBBBBB\nB r  B\nB r  B\nB    B\nBBDBBB", (2, 1), (2, 2), "pied du lit"),
    # Un patient debout au milieu de la salle d'attente.
    ("patient", "BBBBBB\nB hh B\nB    B\nB    B\nBBDBBB", (3, 1), (3, 2), "n'est pas sur"),
])
def test_le_plan_refuse_un_malade_ou_un_patient_mal_pose(qui, plan, bien, mal, reproche):
    """⚠️ La regle est jugee AU CHARGEMENT, par `_piece` : on juge donc le juge.
    Le meme plan passe avec la personne bien posee — sinon on attraperait une
    autre faute et on croirait tenir celle-ci."""
    def poser(x, y):
        return carte._piece("essai", "Essai", plan, sol="u", points=(carte._pt("soigner", 4, 2),),
                            gens=carte._gens((qui, x, y)))
    assert poser(*bien)["gens"] == [{"qui": qui, "x": bien[0], "y": bien[1]}]
    with pytest.raises(ValueError, match=reproche):
        poser(*mal)
