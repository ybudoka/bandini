"""Le 1er juillet, jour du déménagement, côté ville (docs/jalons/le-1er-juillet-jour-du-demenagement.md) :
les camions se garent à cheval sur le trottoir, jamais sur la chaussée ni devant une porte ; les meubles
à côté ; pas dans une rue cossue ; et le boulot tient l'économie."""

import pytest
import villes

from app import calendrier, carte, demenagement, economie


@pytest.fixture(scope="module")
def ville():
    return villes.exporter()


@pytest.fixture(scope="module")
def places(ville):
    return demenagement.places(ville, carte.LEGENDE)


def test_le_jour_est_le_1er_juillet_du_calendrier():
    assert demenagement.JOUR == calendrier.DATES["demenagement"]


def test_les_camions_sont_sur_le_trottoir_loin_des_portes_et_ecartes(ville, places):
    P = places
    sol, legende = ville["sol"], carte.LEGENDE
    assert len(P["camions"]) >= 8, P["camions"]
    decor = {(d["x"], d["y"]) for d in ville["decor"]}
    for cx, cy in P["camions"]:
        for x in (cx - 1, cx, cx + 1):
            fiche = legende[sol[cy][x]]
            assert fiche.get("trottoir") and not fiche.get("route"), f"un camion mord sur « {sol[cy][x]} » en {x, cy}"
            assert sol[cy - 1][x] not in "Dd", f"un camion devant une porte en {x, cy}"
            assert (x, cy) not in decor
    for i, a in enumerate(P["camions"]):
        for b in P["camions"][i + 1:]:
            assert abs(a[0] - b[0]) + abs(a[1] - b[1]) >= demenagement.ECART


def test_les_meubles_sur_le_trottoir_et_pas_dans_une_rue_cossue(ville, places):
    P = places
    sol, legende = ville["sol"], carte.LEGENDE
    assert P["meubles"] and {m[2] for m in P["meubles"]} <= set(demenagement.MEUBLES)
    assert len({m[2] for m in P["meubles"]}) >= 4, "tout le monde jette le même sofa"
    for x, y, _ in P["meubles"]:
        assert legende[sol[y][x]].get("trottoir") and not legende[sol[y][x]].get("route")
    cossues = [r for r in ville["residences"] if r.get("standing") == "+"]
    for cx, cy in P["camions"]:
        assert not any(r["y"] + 1 == cy and r["x"] <= cx - 2 <= r["x"] + r["l"] + 2 and abs(r["x"] + r["porte"] - cx) <= 2
                       for r in cossues), (cx, cy)


def test_sans_de_la_meme_ville_donne_les_memes_places(places):
    assert demenagement.places(villes.exporter(), carte.LEGENDE) == places


def test_le_demenageur_roule_en_camion_et_paie_ses_bosses():
    """Le gain (entre le taxi et quatre fois le taxi) est jugé pour TOUS les boulots par
    `test_economie::test_chaque_boulot_vaut_la_peine_sans_ecraser_les_autres`."""
    b = economie.BOULOTS["demenagement"]
    assert b["vehicule"] == "camion"
    assert b["malus_choc"] >= 0.3, "des boîtes de vaisselle : une bosse doit coûter"
