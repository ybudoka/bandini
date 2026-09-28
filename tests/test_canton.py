"""Le Petit-Canton, étape 2 : le quartier (docs/jalons/le-quartier-chinois.md).

Martin (27 sept. 2026) : « rue principale + place », des enseignes bilingues « avec idéogrammes
stylisés », et deux vagues — ici la première : les bâtiments, les enseignes et leurs plaques.

⚠️ Le juge qui tient tout le reste : bâtir le quartier ne déplace RIEN de la bande — les Friches et la
Gare gardent leurs tirages à l'unité près, parce que chaque îlot du quartier se bâtit avec SES dés
(`nord._ChantierNord._a_ses_des`).
"""

import copy

import pytest
import villes

from app import carte, devantures, nord


def _bande_avec(plan_du_canton=None):
    """La bande, bâtie à neuf — avec un autre plan pour le canton si on le demande (le témoin)."""
    if plan_du_canton is None:
        return nord.batir_la_bande()
    districts = copy.deepcopy(nord.DISTRICTS_NORD)
    canton = next(d for d in districts if d["slug"] == "canton")
    canton["plan"] = plan_du_canton
    canton["standing"] = tuple("=" * len(r) for r in plan_du_canton)
    plan = carte._assembler(districts)
    trame = dict(nord.TRAME_NORD, districts=districts,
                 standing=carte._assembler_le_standing(districts, plan))
    avant = nord.PLAN_NORD, nord.TRAME_NORD
    nord.PLAN_NORD, nord.TRAME_NORD = plan, trame
    try:
        return nord.batir_la_bande()
    finally:
        nord.PLAN_NORD, nord.TRAME_NORD = avant


@pytest.fixture(scope="module")
def bande():
    return _bande_avec()


def _rect(ch):
    return ch.rect_district(nord.district("canton"))


def _dans_le_canton(ch, o):
    x0, _y0, large, _h = _rect(ch)
    return x0 <= o["x"] < x0 + large and o["y"] < nord.DECALAGE_NORD


def test_la_rue_principale_ses_logements_et_sa_place(bande):
    """Des commerces, des logements, une place : c'est un quartier, pas une rangée de décor."""
    devs = [d for d in bande.devantures if _dans_le_canton(bande, d)]
    logements = [r for r in bande.residences if _dans_le_canton(bande, r)]
    assert len(devs) >= 15 and len(logements) >= 40, (len(devs), len(logements))
    plan = nord.district("canton")["plan"]
    assert sum(r.count("o") for r in plan) == 1, "une place du marché"
    # La rue principale : les deux colonnes d'îlots de part et d'autre sont commerçantes d'un bout à l'autre —
    # le casino du Dragon d'or compris (`casino.CASINO_DU_PLAN`, au nord de la place).
    from app import casino
    assert all(r[3] in "c" and r[4] in "co<" + casino.CASINO_DU_PLAN for r in plan), plan


def test_ses_enseignes_sont_les_siennes_et_tiennent_dans_leur_bandeau(bande):
    # Les siennes, et celles de ses lieux garantis (le Dragon d'or : `devantures.ENSEIGNES`).
    siens = {t for t, _g in devantures.COMMERCES["canton"]} | {t for t, _g in devantures.ENSEIGNES.values()}
    devs = [d for d in bande.devantures if _dans_le_canton(bande, d)]
    ailleurs = sorted({d["texte"] for d in devs} - siens)
    assert not ailleurs, f"des enseignes d'un autre quartier au Petit-Canton : {ailleurs}"
    for texte, _g in devantures.COMMERCES["canton"]:
        assert devantures.tient_en(texte, 4), texte


def test_chaque_commerce_du_quartier_porte_sa_plaque_et_seulement_lui(bande):
    """Deux idéogrammes par plaque, de vrais caractères de cinq sur cinq, tirés à la position."""
    for d in bande.devantures:
        if _dans_le_canton(bande, d):
            assert 0 <= d.get("ideo", -1) < len(devantures.PAIRES), d
        else:
            assert "ideo" not in d, f"une plaque hors du Petit-Canton : {d}"
    for paire in devantures.PAIRES:
        for car in paire:
            rangs = devantures.IDEOGRAMMES[car]
            assert len(rangs) == 5 and all(len(r) == 5 and set(r) <= {"#", "."} for r in rangs), car
    assert len({tuple(v) for v in devantures.IDEOGRAMMES.values()}) == len(devantures.IDEOGRAMMES)


def test_batir_le_quartier_ne_deplace_rien_de_la_bande(bande):
    """⚠️ Le témoin : la bande d'avant, le canton en terrains à bâtir. Hors du rectangle du canton
    (couronne comprise), la même bande à la tuile près, et les mêmes objets."""
    temoin = _bande_avec(("bbbbbbbb",) * 7)
    x0, y0, large, haut = _rect(bande)
    dans = lambda x, y: x0 - 1 <= x < x0 + large + 1 and y0 - 1 <= y < y0 + haut + 1  # noqa: E731
    for y in range(bande.hauteur):
        for x in range(bande.largeur):
            if not dans(x, y):
                assert bande.sol[y][x] == temoin.sol[y][x], (x, y, bande.sol[y][x], temoin.sol[y][x])
    for cle in ("decor", "portes", "lampes", "devantures", "residences", "toits"):
        a = [o for o in getattr(bande, cle) if not dans(o["x"], o["y"])]
        b = [o for o in getattr(temoin, cle) if not dans(o["x"], o["y"])]
        assert a == b, cle
    # Et le témoin mord : son canton n'a rien de bâti.
    assert not [p for p in temoin.portes if _dans_le_canton(temoin, p)]


def test_ses_portes_restent_eparpillees(bande):
    """Le juge de la ville (`test_carte.test_la_ville_est_irreguliere`) à la mesure du quartier : 29 portes
    dans 149 colonnes, le hasard seul en mettrait ~26 dans des colonnes distinctes. Deux tiers au moins, et
    jamais plus de trois portes dans la même colonne — une pile, c'est un damier qui commence."""
    from collections import Counter
    portes = [p for p in bande.portes if _dans_le_canton(bande, p)]
    colonnes = Counter(p["x"] for p in portes)
    assert len(colonnes) >= len(portes) * 2 / 3, (len(colonnes), len(portes))
    assert max(colonnes.values()) <= 3, colonnes.most_common(3)


# --- Vague B : l'arche et les lanternes (`app/canton.py`) ----------------------------------------------

@pytest.fixture(scope="module")
def ville():
    return villes.exporter()


def test_l_arche_ouvre_la_rue_principale_sur_la_couture(ville):
    """Une arche, au bout sud de la rue principale, à deux rangées de la couture : ses piliers sur les deux
    trottoirs, solides, et jamais dans le devant d'une porte."""
    from app import canton, devants
    n = nord.DECALAGE_NORD
    x0, large = canton.rue_principale(nord._bande(), nord.district("canton"))
    assert ville["canton"]["arches"] == [{"x": x0, "y": n - canton.RECUL_DE_L_ARCHE, "l": large,
                                         "paire": canton.PAIRE_DE_L_ARCHE}]
    piliers = [d for d in ville["decor"] if d["type"] == "pilier_arche"]
    assert sorted((d["x"], d["y"]) for d in piliers) == [(x0, n - 2), (x0 + large - 1, n - 2)]
    assert "pilier_arche" in carte.DECOR_SOLIDE
    larges, _pas = devants.devants(ville)
    for d in piliers:
        assert ville["sol"][d["y"]][d["x"]] == ".", d
        assert (d["x"], d["y"]) not in larges, f"un pilier devant une porte : {d}"
    # La chaussée entre les piliers reste une chaussée : l'arche enjambe la rue, elle ne la ferme pas.
    assert all(ville["voie"][n - 2][x] != "." for x in range(x0 + 1, x0 + large - 1))


def test_les_lanternes_passent_au_dessus_de_la_rue_et_s_allument(ville):
    """Des cordes d'un trottoir à l'autre, au-dessus de la rue principale seulement (jamais d'un
    croisement, où elles cacheraient les feux), et une lueur rouge sous chacune."""
    from app import canton
    n = nord.DECALAGE_NORD
    x0, large = canton.rue_principale(nord._bande(), nord.district("canton"))
    cordes = ville["canton"]["lanternes"]
    assert len(cordes) >= 10, len(cordes)
    carrefours = {(x, y) for i in ville["intersections"]
                  for x in range(i["x"], i["x"] + i["l"]) for y in range(i["y"], i["y"] + i["h"])}
    for c in cordes:
        assert (c["x"], c["l"]) == (x0, large) and 0 <= c["y"] < n - canton.RECUL_DE_L_ARCHE, c
        assert ville["sol"][c["y"]][c["x"]] == "." and ville["sol"][c["y"]][c["x"] + large - 1] == ".", c
        assert not any((x, c["y"]) in carrefours for x in range(c["x"], c["x"] + large)), f"sur un croisement : {c}"
    lueurs = [lp for lp in ville["lampes"] if lp.get("c") == "lanterne"]
    assert sorted((lp["x"], lp["y"]) for lp in lueurs) == sorted((c["x"] + large // 2, c["y"]) for c in cordes)
