"""Les blocs de carte (vague 1) : un morceau de monde à part, servi à part, qui ne change
pas un octet de la ville. Voir `app/blocs/` et `docs/jalons/des-blocs-de-carte-en-extensions.md`."""

import json

import pytest

from app import blocs, create_app, definitions, hors_ligne
from conftest import ConfigTest


@pytest.mark.parametrize("bloc", blocs.BLOCS, ids=lambda b: b["slug"])
def test_chaque_bloc_tient_debout(bloc, paquet):
    """Son plan, ses glyphes, son retour qui se marche et qu'on rejoint à pied depuis
    l'arrivée — et son passage, dans la VILLE, sur une tuile qui se marche."""
    assert blocs.erreurs(bloc, paquet["carte"]) == []


def test_un_bloc_mal_fait_se_voit():
    """Le juge mord : un retour muré et un passage en pleine façade."""
    mauvais = dict(blocs.BLOCS[0], retour={"bord": "sud", "de": 0, "l": 3}, passage={"bord": "nord", "de": 0, "l": 1})
    ville = {"largeur": 3, "hauteur": 1, "sol": ["FFF"]}
    fautes = blocs.erreurs(mauvais, ville)
    assert any("retour ne se marche pas" in f for f in fautes), fautes
    assert any("passage en ville ne se marche pas" in f for f in fautes), fautes


def test_un_bloc_ne_change_pas_un_octet_de_la_ville(monkeypatch, paquets):
    """⚠️ LA PROMESSE DES BLOCS : la ville n'en sait rien. Bâtie sans aucun bloc, sa carte
    a exactement la même empreinte."""
    monkeypatch.setattr(blocs, "BLOCS", [])
    sans = definitions.construire()
    assert sans.carte.etag == paquets.carte.etag
    assert sans.blocs == {}


def test_la_carte_d_un_bloc_se_sert_a_part_et_se_revalide():
    client = create_app(ConfigTest).test_client()
    for bloc in blocs.BLOCS:
        r = client.get(f"/api/carte/bloc/{bloc['slug']}")
        assert r.status_code == 200 and r.headers["ETag"]
        corps = r.get_json()
        assert corps["bloc"]["slug"] == bloc["slug"] and corps["largeur"] == len(bloc["plan"][0])
        assert client.get(f"/api/carte/bloc/{bloc['slug']}",
                          headers={"If-None-Match": r.headers["ETag"]}).status_code == 304
    assert client.get("/api/carte/bloc/nulle-part").status_code == 404


def test_le_paquet_nomme_les_passages_et_pas_les_cartes(paquet):
    """Le paquet dit OÙ passer ; la carte du bloc voyage à part, à la demande."""
    assert [b["slug"] for b in paquet["blocs"]] == [b["slug"] for b in blocs.BLOCS]
    for b in paquet["blocs"]:
        assert set(b) == {"slug", "nom", "passage", "panneau"}
    assert paquet["blocs_empreinte"]


def test_le_gabarit_des_blocs_est_dans_la_page_et_hors_de_la_coquille():
    client = create_app(ConfigTest).test_client()
    page = client.get("/").get_data(as_text=True)
    assert 'data-url-bloc="/api/carte/bloc/SLUG?e=' in page
    assert not any("/api/carte/bloc/" in a for a in hors_ligne.coquille(page, "/"))


def test_la_carte_d_un_bloc_a_ce_que_monde_charger_lit():
    for bloc in blocs.BLOCS:
        c = blocs.carte_du_bloc(bloc)
        for cle in ("sol", "voie", "legende", "decor", "apparition", "portes", "lampes", "zones",
                    "points_interet", "intersections", "arrets", "interieurs", "ambulants", "bloc"):
            assert cle in c, f"{bloc['slug']} : « {cle} » manque"
        assert len(c["voie"]) == c["hauteur"] and len(c["voie"][0]) == c["largeur"]
        json.dumps(c)
