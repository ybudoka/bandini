def test_accueil(client):
    reponse = client.get("/")
    assert reponse.status_code == 200
    html = reponse.get_data(as_text=True)
    assert 'id="toile"' in html
    assert "/api/definitions" in html
    assert 'id="tactile"' in html
    assert 'data-etat="chargement"' in html


def test_sante(client):
    donnees = client.get("/sante").get_json()
    assert donnees["ok"] is True
    assert donnees["version"].count(".") == 2


def test_definitions_avec_etag(client):
    reponse = client.get("/api/definitions")
    assert reponse.status_code == 200
    assert reponse.mimetype == "application/json"
    etag = reponse.headers["ETag"]
    assert etag.startswith('"') and len(etag) == 18
    paquet = reponse.get_json()
    assert paquet["empreinte"] == etag.strip('"')
    assert len(paquet["vehicules"]) >= 4
    assert paquet["carte"]["largeur"] > 0

    revalide = client.get("/api/definitions", headers={"If-None-Match": etag})
    assert revalide.status_code == 304
    assert revalide.headers["ETag"] == etag


def test_api_scores(client):
    assert client.get("/api/scores").get_json() == {"scores": []}

    refus = client.post("/api/scores", json={"pseudo": "", "fortune": 1, "missions": 0,
                                             "proprietes": 0, "duree_s": 10})
    assert refus.status_code == 400
    assert "pseudo" in refus.get_json()["erreur"]

    ok = client.post("/api/scores", json={"pseudo": "Léa", "fortune": 1230, "missions": 0,
                                          "proprietes": 1, "duree_s": 600})
    assert ok.status_code == 201
    assert ok.get_json()["rang"] == 1
    assert client.get("/api/scores").get_json()["scores"][0]["pseudo"] == "Léa"


def test_corps_trop_gros(client):
    gros = client.post("/api/scores", data="x" * 20_000, content_type="application/json")
    assert gros.status_code == 413


def test_404(client):
    reponse = client.get("/nulle-part")
    assert reponse.status_code == 404
    assert "Cul-de-sac" in reponse.get_data(as_text=True)


def test_statiques(client, racine):
    html = client.get("/").get_data(as_text=True)
    import re

    scripts = re.findall(r"/static/js/([a-z_]+\.js)", html)
    assert len(scripts) >= 10
    for nom in scripts:
        assert client.get(f"/static/js/{nom}").status_code == 200, nom
        assert (racine / "static" / "js" / nom).exists()
    assert client.get("/static/css/styles.css").status_code == 200
    assert client.get("/static/img/favicon.svg").status_code == 200
