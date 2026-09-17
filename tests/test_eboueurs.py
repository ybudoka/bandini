"""Les éboueurs (M12), jugés en Python : la tournée, ses bacs, son horaire.

⚠️ Python trace, le navigateur roule — comme les autobus, et sous les mêmes juges :
chaque pas permis par les flèches, jamais sur ce que la ville peut fermer. Et la
tournée ne pose RIEN dans la ville : ses bacs naissent dans le navigateur.
"""

import copy

import pytest

from app import autobus, carte, eboueurs


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


def tournee(ville):
    return autobus.derouler(ville["eboueurs"]["trace"])


def test_la_tournee_obeit_aux_fleches_et_evite_ce_qui_ferme(ville):
    tuiles = tournee(ville)
    assert len(tuiles) > 200, "une tournée qui fait le tour d'un quartier"
    for i, (x, y) in enumerate(tuiles):
        suivante = tuiles[(i + 1) % len(tuiles)]
        assert suivante in carte.suivre_voie(ville, x, y), f"pas {i} : {(x, y)} -> {suivante}"
    reseau = autobus._Reseau(ville)
    dedans = sorted(set(tuiles) & reseau.interdites)
    assert not dedans, f"la tournée passe sur {len(dedans)} tuiles que la ville peut fermer : {dedans[:3]}"


def test_les_bacs_sont_au_bord_du_trottoir_loin_des_carrefours(ville):
    """Un bac par cinq pas au plus, sur le trottoir à droite du camion, jamais sur un
    meuble, un abribus ou le pas d'une porte, et jamais près d'une boîte : le camion
    s'arrêterait dans le carrefour."""
    tuiles, points = tournee(ville), ville["eboueurs"]["points"]
    reseau = autobus._Reseau(ville)
    assert len(points) >= eboueurs.MIN_BACS
    occupe = {(d["x"], d["y"]) for d in ville["decor"]}
    for rang in range(len(ville["autobus"]["arrets"])):
        d = autobus.detail(ville, rang)
        occupe |= {tuple(d["quai"]), tuple(d["abri"])}
    portes = {(p["x"], p["y"] + 1) for p in ville["portes"]}
    n = len(tuiles)
    precedent = None
    for i, bx, by in points:
        x, y = tuiles[i]
        dx, dy = autobus.PAS[ville["voie"][y][x]]
        assert (bx, by) == (x + autobus.a_droite(dx, dy)[0], y + autobus.a_droite(dx, dy)[1]), (i, bx, by)
        assert ville["sol"][by][bx] == ".", f"bac hors du trottoir en {(bx, by)}"
        assert (bx, by) not in occupe and (bx, by) not in portes, (bx, by)
        assert not any(tuiles[(i + k) % n] in reseau.boites
                       for k in range(-eboueurs.LOIN_DES_BOITES, eboueurs.LOIN_DES_BOITES + 1)), i
        if precedent is not None:
            assert i - precedent >= eboueurs.PAS_ENTRE_BACS, (precedent, i)
        precedent = i


def test_la_tournee_ne_pose_rien_dans_la_ville(ville, monkeypatch):
    """Sans éboueurs, la ville est la même : tracer ne pose rien, ne tire rien, et ne
    touche pas à ce qu'il lit."""
    avant = copy.deepcopy(ville)
    eboueurs.tracer(ville)
    assert ville == avant, "tracer a modifié la ville qu'il lisait"
    avec = carte.generer()
    monkeypatch.setattr(eboueurs, "tracer", lambda v: None)
    sans = carte.generer()
    assert avec["eboueurs"] and sans["eboueurs"] is None
    sans.pop("eboueurs"), avec.pop("eboueurs")
    assert sans == avec


def test_l_horaire_de_la_collecte_tient_debout():
    h = eboueurs.HORAIRE
    assert h["sortis_des"] < h["debut"] < h["fin"] < h["rentres_a"], "les bacs sortent avant le camion et rentrent après"
    assert 0 < h["leve_images"] < h["arret_images"]
    demi_diagonale = (240 ** 2 + 135 ** 2) ** 0.5
    assert demi_diagonale < h["naissance_min_px"] < h["naissance_max_px"] < 520
