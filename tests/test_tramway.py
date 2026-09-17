"""Le tramway (M12), jugé en Python : sa voie double, ses arrêts, son horaire.

⚠️ `tramway.py` ne pose rien : il trace. Ces juges relisent la boucle qu'il rend avec
leurs propres yeux — dans le sens du trafic partout sauf aux deux passages de voie, la
même rue à l'aller et au retour, rien de fermable, des arrêts au bord du trottoir.
"""

from __future__ import annotations

import time

import pytest

from app import autobus, carte, tramway


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


@pytest.fixture(scope="module")
def boucle(ville):
    return autobus.derouler(ville["tramway"]["trace"])


def _sens(ville, x, y):
    f = ville["voie"][y][x]
    if f in autobus.PAS:
        return autobus.PAS[f]
    if f == "S":
        return autobus.PAS.get(ville["arrets"].get(f"{x},{y}", ""))
    return None


def test_la_voie_roule_dans_le_sens_du_trafic_sauf_aux_deux_terminus(ville, boucle):
    """Chaque pas va d'une tuile à sa voisine ; la tuile d'arrivée roule dans ce sens
    (ou c'est une boîte) — sauf exactement DEUX pas : le passage d'une voie à l'autre au
    bout de l'aller, et au bout du retour, entre deux voies opposées de la même rue."""
    n = len(boucle)
    assert n >= 100
    passages = []
    for i in range(n):
        (x, y), (nx, ny) = boucle[i], boucle[(i + 1) % n]
        d = (nx - x, ny - y)
        assert abs(d[0]) + abs(d[1]) == 1, f"la voie saute de {(x, y)} à {(nx, ny)}"
        if ville["voie"][ny][nx] == "+" or _sens(ville, nx, ny) == d:
            continue
        passages.append(i)
        a, b = _sens(ville, x, y), _sens(ville, nx, ny)
        assert a is not None and b is not None and a == (-b[0], -b[1]), f"pas à contresens en {(nx, ny)}"
        assert d not in (a, b) and (-d[0], -d[1]) not in (a, b), "un passage de voie qui n'est pas de côté"
    assert len(passages) == 2, f"{len(passages)} pas hors du sens du trafic : {passages}"
    assert passages[0] == ville["tramway"]["aller"] - 1, "le premier passage n'est pas au bout de l'aller"


def test_l_aller_et_le_retour_partagent_la_rue(ville, boucle):
    """Chaque tuile de l'aller a, à sa gauche, une tuile du retour : c'est une voie
    DOUBLE — pas deux lignes qui se séparent au premier carrefour."""
    aller = ville["tramway"]["aller"]
    sur_la_boucle = set(boucle)
    for i in range(aller - 1):
        (x, y), (nx, ny) = boucle[i], boucle[i + 1]
        d = (nx - x, ny - y)
        g = (d[1], -d[0])
        assert (x + g[0], y + g[1]) in sur_la_boucle, f"pas de voie de retour à côté de {(x, y)}"


def test_rien_de_fermable_sur_les_rails(ville, boucle):
    """Ni fermeture, ni entrave, ni barrière, ni pont, ni aqueduc : une rame ne se
    détourne pas."""
    reseau = autobus._Reseau(ville)
    assert not set(boucle) & reseau.interdites


def test_du_faubourg_au_quai_du_traversier(ville, boucle):
    t = ville["tramway"]
    lieu = next(p for p in ville["points_interet"] if p["slug"] == tramway.DEPART)
    depart = boucle[0]
    assert abs(depart[0] - lieu["x"]) + abs(depart[1] - lieu["y"]) <= 2 * tramway.RAYON_BOUT
    quai = ville["traversier"]["escales"][0]["acces"][0]
    bout = boucle[t["aller"] - 1]
    assert abs(bout[0] - quai[0]) + abs(bout[1] - quai[1]) <= 2 * tramway.RAYON_BOUT
    noms = [a[3] for a in t["arrets"]]
    assert "Quai du traversier" in noms, noms


def test_les_arrets_au_bord_du_trottoir_espaces_et_loin_des_abribus(ville, boucle):
    t = ville["tramway"]
    n = len(boucle)
    reseau = autobus._Reseau(ville)
    abribus = [autobus.detail(ville, k)["quai"] for k in range(len(ville["autobus"]["arrets"]))]
    decor = {(d["x"], d["y"]) for d in ville["decor"]}
    indices = [a[0] for a in t["arrets"]]
    assert len(indices) >= 4 and indices == sorted(indices)
    assert len({a[3] for a in t["arrets"]}) == len(t["arrets"]), "deux arrêts du même nom"
    for i, x, y, nom in t["arrets"]:
        assert tuple(boucle[i]) == (x, y)
        d = autobus.PAS[ville["voie"][y][x]]
        assert reseau.longe_le_trottoir(x, y) and (x, y) not in reseau.boites, nom
        rx, ry = autobus.a_droite(*d)
        assert ville["sol"][y + ry][x + rx] == "." and (x + rx, y + ry) not in decor, f"{nom} : le quai n'est pas libre"
        assert all(abs(x + rx - qx) + abs(y + ry - qy) >= tramway.LOIN_DES_ABRIBUS for qx, qy in abribus), nom
    # ⚠️ Les quatre terminus (le premier et le dernier arrêt de chaque voie) se posent
    # d'abord, où qu'ils tombent ; les autres se tiennent à `ECART_ARRETS` de tous.
    aller = t["aller"]
    moities = ([i for i in indices if i < aller], [i for i in indices if i >= aller])
    terminus = {k for m in moities if m for k in (min(m), max(m))}
    for i in indices:
        if i in terminus:
            continue
        for k in indices:
            if k != i:
                assert min((i - k) % n, (k - i) % n) >= tramway.ECART_ARRETS, f"arrêts {i} et {k} trop proches"


def test_la_ville_est_la_meme_avec_ou_sans_tramway(ville, monkeypatch):
    monkeypatch.setattr(tramway, "tracer", lambda v: None)
    sans = carte.generer()
    for cle in ville:
        if cle == "tramway":
            continue
        assert sans[cle] == ville[cle], f"« {cle} » a bougé"


def test_le_trace_ne_ralentit_pas_la_ville(ville):
    debut = time.perf_counter()
    tramway.tracer(ville)
    assert time.perf_counter() - debut < 0.5


def _copie(ville):
    """Une copie qu'on peut salir : le décor et les abribus seulement."""
    return {**ville, "decor": list(ville["decor"]),
            "autobus": {**ville["autobus"], "arrets": list(ville["autobus"]["arrets"])}}


def test_un_arret_ne_se_pose_ni_sur_un_meuble_ni_pres_d_un_abribus(ville, boucle):
    """⚠️ La graine livrée n'a aucun arrêt de tramway que ces deux règles écartent : on
    salit une copie de la ville à la place d'un arrêt (un meuble sur son quai, puis un
    abribus sur sa voie) et l'arrêt doit partir."""
    t = ville["tramway"]
    rails = tramway._Rails(ville)
    i, x, y, _nom = t["arrets"][2]
    d = autobus.PAS[ville["voie"][y][x]]
    rx, ry = autobus.a_droite(*d)
    meuble = _copie(ville)
    meuble["decor"].append({"type": "banc", "x": x + rx, "y": y + ry})
    assert i not in [a[0] for a in tramway._arrets(meuble, rails, boucle, t["aller"])], "un arrêt sur un meuble"
    abri = _copie(ville)
    abri["autobus"]["arrets"].append({"x": x, "y": y, "nom": "Un abribus"})
    poses = tramway._arrets(abri, rails, boucle, t["aller"])
    assert all(abs(px - x) + abs(py - y) >= tramway.LOIN_DES_ABRIBUS for _k, px, py in poses), "un arrêt collé à un abribus"
