"""Les murs fissurés (`docs/jalons/les-explosifs.md`, vague 3b) : un mur plein, qu'on voit fissuré, qui ne cède qu'à une
explosion. ⚠️ Toujours là où il y a du sol des deux côtés : un trou dans une façade ouvrirait sur un toit."""

from app import blocs, carte
from app.blocs import villa


def _plans():
    """Chaque carte où un mur peut se poser : la ville, ses pièces, les plans des blocs."""
    ville = carte.generer()
    yield "ville", ville["sol"]
    for slug, piece in ville["interieurs"].items():
        yield slug, piece["sol"]
    for bloc in blocs.BLOCS + blocs.SOUS_SOLS:
        yield f"bloc {bloc['slug']}", blocs.sol_du_bloc(bloc)


def _sol(plan, x, y):
    if 0 <= y < len(plan) and 0 <= x < len(plan[y]):
        return not carte.LEGENDE.get(plan[y][x], {}).get("solide")
    return False


def test_le_mur_fissure_est_un_mur_plein_qu_on_voit():
    m = carte.LEGENDE["0"]
    assert m["solide"] == 1 and m["fissure"] is True
    assert [g for g, d in carte.LEGENDE.items() if d.get("fissure")] == ["0"]


def test_chaque_mur_fissure_a_du_sol_des_deux_cotes():
    vus = 0
    for nom, plan in _plans():
        for y, ligne in enumerate(plan):
            for x, g in enumerate(ligne):
                if g != "0":
                    continue
                vus += 1
                assert (_sol(plan, x - 1, y) and _sol(plan, x + 1, y)) or (_sol(plan, x, y - 1) and _sol(plan, x, y + 1)), \
                    f"{nom} : le mur fissuré {x, y} n'a pas de sol des deux côtés"
    assert vus >= 2, f"le témoin : {vus} mur(s) fissuré(s)"


def test_la_villa_du_maire_a_ses_deux_murs_fissures_au_rez():
    """Entre le salon et la salle à manger, entre la salle à manger et la cuisine — jamais vers la chambre forte."""
    poses = [(x, y) for y, ligne in enumerate(villa.PLAN) for x, g in enumerate(ligne) if g == "0"]
    assert poses == [(27, 15), (37, 19)], poses
