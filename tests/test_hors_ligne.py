"""Installable, et jouable hors ligne — le travailleur, sa coquille et ses sons.

Demande de Martin : « est-ce compliqué de faire du jeu une webapp installable ? », puis
« jouable hors ligne ».

Les premiers juges lisent ce que le serveur sert. Les derniers ouvrent un vrai Chromium,
laissent le travailleur s'installer, puis COUPENT le reseau — ou mettent le serveur en
panne : la ville doit s'ouvrir quand meme. Chacun a son temoin, la meme page sans
travailleur, qui, elle, ne s'ouvre pas : sans lui, un juge vert ne dirait rien.
"""

import html
import json
import os
import re
import shutil
import subprocess
import threading
from pathlib import Path

import pytest
from werkzeug.serving import make_server

from app import create_app, hors_ligne
from config import Config

RACINE = Path(__file__).resolve().parent.parent
AUDIO = RACINE / "static" / "audio"
OBLIGATOIRE = os.environ.get("BANDINI_TESTS_OBLIGATOIRES") == "1"


def config_du_travailleur(client) -> dict:
    corps = client.get("/travailleur.js").get_data(as_text=True)
    return json.loads(re.match(r"const HORS_LIGNE = (.*);\n", corps).group(1))


# --- Ce que le serveur sert ----------------------------------------------------------------


def test_le_travailleur_est_servi_a_la_racine_et_jamais_fige(client):
    """⚠️ A la racine : un travailleur ne controle que son dossier, et `/static/js/` n'est
    pas la page. Et revalide a chaque visite : nginx garde `/static/` sept jours, un
    travailleur fige une semaine se refermerait sur la session suivante."""
    reponse = client.get("/travailleur.js")
    assert reponse.status_code == 200
    assert reponse.mimetype == "text/javascript"
    assert reponse.headers["Cache-Control"] == "no-cache"
    etag = reponse.headers["ETag"].strip('"')
    assert client.get("/travailleur.js", headers={"If-None-Match": f'"{etag}"'}).status_code == 304
    # nginx compresse et marque l'ETag faible en passant : le navigateur le renvoie tel quel.
    assert client.get("/travailleur.js", headers={"If-None-Match": f'W/"{etag}"'}).status_code == 304
    assert config_du_travailleur(client)["empreinte"] == etag
    page = client.get("/").get_data(as_text=True)
    assert 'data-url-travailleur="/travailleur.js"' in page


def test_la_coquille_est_tout_ce_que_la_page_demande(client):
    """⚠️ La coquille est LUE dans la page rendue : un script de plus dans `index.html`
    et une liste tenue a la main l'oublierait — hors ligne, la ville resterait au
    chargement, et rien ne rougirait en ligne. Chaque adresse doit aussi repondre :
    une seule qui manque, et le travailleur refuse de s'installer (`addAll`)."""
    page = client.get("/").get_data(as_text=True)
    demandes = {html.unescape(u) for u in re.findall(r'\s(?:src|href)="(/[^"]*)"', page)}
    coquille = config_du_travailleur(client)["coquille"]
    assert coquille[0] == "/"
    assert demandes and demandes <= set(coquille), demandes - set(coquille)
    scripts = [u for u in coquille if "/static/js/" in u]
    assert len(scripts) == int(re.search(r'data-scripts="(\d+)"', page).group(1))
    assert not any("travailleur.js" in u for u in coquille), "le travailleur ne se garde pas lui-meme"
    for adresse in coquille:
        assert client.get(adresse).status_code == 200, adresse


def test_les_paquets_se_demandent_par_leur_empreinte(client):
    """⚠️ Un paquet garde qui ne correspond plus aux scripts ne ressemble pas a un bogue
    de cache : il ressemble a un bogue de jeu. Les deux paquets se demandent donc par
    leur empreinte (`?e=`, que le serveur ignore) — c'est la cle du cache, et une page
    n'y retrouve que la ville de SA construction."""
    page = client.get("/").get_data(as_text=True)
    coquille = config_du_travailleur(client)["coquille"]
    for nom, route in (("definitions", "/api/definitions"), ("carte", "/api/carte")):
        adresse = re.search(rf'data-url-{nom}="([^"]+)"', page).group(1)
        etag = client.get(route).headers["ETag"].strip('"')
        assert adresse == f"{route}?e={etag}", adresse
        assert adresse in coquille
        assert client.get(adresse).get_data() == client.get(route).get_data()


def test_les_sons_du_travailleur_sont_ceux_du_dossier(client):
    """Les mp3 servis, et leur poids — c'est ce que la ligne des OPTIONS annonce avant
    de les telecharger. ⚠️ Pas `audio/reserve/` : il n'est pas servi au jeu."""
    sons = config_du_travailleur(client)["audio"]
    assert sons["dossier"] == "/static/audio/"
    sur_disque = sorted(f.name for f in AUDIO.glob("*.mp3"))
    assert [f["nom"] for f in sons["fichiers"]] == sur_disque
    assert len(sur_disque) > 100
    for f in sons["fichiers"][:5]:
        assert f["octets"] == (AUDIO / f["nom"]).stat().st_size


def test_l_empreinte_suit_le_contenu(tmp_path):
    """Le cache de la coquille se nomme par l'empreinte, jamais par la version : elle
    change quand la page change (une version, un script), quand un son change de
    poids — et pas autrement."""
    (tmp_path / "a.mp3").write_bytes(b"123")
    page = '<script src="/static/js/jeu.js?v=1.0.0"></script>'
    _, une = hors_ligne.travailleur(page, "/", tmp_path, "/static/audio/")
    _, meme = hors_ligne.travailleur(page, "/", tmp_path, "/static/audio/")
    _, version = hors_ligne.travailleur(page.replace("1.0.0", "1.0.1"), "/", tmp_path, "/static/audio/")
    (tmp_path / "a.mp3").write_bytes(b"1234")
    _, son = hors_ligne.travailleur(page, "/", tmp_path, "/static/audio/")
    assert une == meme
    assert len({une, version, son}) == 3


def test_la_coquille_ne_garde_rien_d_une_autre_origine():
    page = ('<link href="https://fonts.example/x.css"><script src="//cdn.example/y.js"></script>'
            '<img src="relatif.png"><img src="/static/img/logo.svg?v=1&amp;x=2"><img src="/static/img/logo.svg?v=1&amp;x=2">')
    assert hors_ligne.coquille(page, "/") == ["/", "/static/img/logo.svg?v=1&x=2"]


def test_le_travailleur_servi_se_lit(client, tmp_path):
    """Le fichier et son en-tete forment UN script valide : une faute ici, et le navigateur
    refuse le travailleur sans rien dire a la page."""
    node = shutil.which("node")
    if node is None:
        if OBLIGATOIRE:
            pytest.fail("node est obligatoire (BANDINI_TESTS_OBLIGATOIRES=1) et il manque")
        pytest.skip("node absent")
    fichier = tmp_path / "travailleur.js"
    fichier.write_bytes(client.get("/travailleur.js").get_data())
    sortie = subprocess.run([node, "--check", str(fichier)], capture_output=True, text=True)
    assert sortie.returncode == 0, sortie.stderr


def test_sans_travailleur_la_ligne_des_options_le_dit(banc):
    """Sous le banc (ou en http sur le reseau local) il n'y a pas de travailleur : la
    ligne existe, dit INDISPONIBLE et ne se choisit pas — le jeu se joue comme avant."""
    r = banc("""(L) => {
        const m = L.Hud.menuOptions();
        const i = m.items.find(function (x) { return x.libelle === 'LES SONS HORS LIGNE'; });
        m.maj();
        return { detail: i.detail, actif: i.actif };
    }""")
    assert r == {"detail": "INDISPONIBLE", "actif": False}


# --- Dans un vrai navigateur ------------------------------------------------------------


class Interrupteur:
    """Le site, avec un interrupteur de panne : `panne = 502` rend ce que Caddy rend quand
    l'application ne repond plus. Compte les requetes qui l'ont touche."""

    def __init__(self, app):
        self.app, self.panne, self.requetes = app, None, 0

    def __call__(self, environ, start_response):
        self.requetes += 1
        if self.panne:
            start_response(f"{self.panne} Panne", [("Content-Type", "text/plain")])
            return [b"le serveur est en panne"]
        return self.app(environ, start_response)


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    class ConfigHorsLigne(Config):
        TESTING = True
        SECRET_KEY = "test"
        DONNEES_DIR = str(tmp_path_factory.mktemp("donnees"))

    interrupteur = Interrupteur(create_app(ConfigHorsLigne))
    serveur_http = make_server("127.0.0.1", 0, interrupteur, threaded=True)
    fil = threading.Thread(target=serveur_http.serve_forever, daemon=True)
    fil.start()
    interrupteur.url = f"http://127.0.0.1:{serveur_http.server_port}/"
    try:
        yield interrupteur
    finally:
        serveur_http.shutdown()
        fil.join(timeout=5)


@pytest.fixture
def ville(site):
    site.panne = None
    yield site
    site.panne = None


def ouvrir(browser, url, travailleur=True):
    contexte = browser.new_context(service_workers="allow" if travailleur else "block")
    page = contexte.new_page()
    page.erreurs = []
    page.on("pageerror", lambda e: page.erreurs.append(str(e)))
    page.goto(url)
    page.wait_for_selector('#bandini[data-etat="titre"]', timeout=20000)
    if travailleur:
        # Il s'installe apres `load`, remplit la coquille, puis prend la page (`clients.claim`).
        page.wait_for_function("navigator.serviceWorker.controller !== null", timeout=20000)
    return contexte, page


def test_la_ville_s_ouvre_quand_le_reseau_se_tait(browser, ville):
    """Premiere visite en ligne ; puis plus de reseau, et on recharge : la ville arrive a
    l'ecran titre sans qu'une seule requete touche le serveur. Temoin : la meme page sans
    travailleur ne se recharge pas."""
    contexte, page = ouvrir(browser, ville.url)
    # Et installable : c'est Chromium qui le dit (le manifeste, les icones, la page).
    cdp = contexte.new_cdp_session(page)
    assert cdp.send("Page.getInstallabilityErrors")["installabilityErrors"] == []
    contexte.set_offline(True)
    avant = ville.requetes
    page.reload()
    page.wait_for_selector('#bandini[data-etat="titre"]', timeout=20000)
    assert ville.requetes == avant, "hors ligne, rien n'a du toucher le serveur"
    assert page.erreurs == []
    contexte.close()

    temoin, page = ouvrir(browser, ville.url, travailleur=False)
    temoin.set_offline(True)
    with pytest.raises(Exception):
        page.reload()
    temoin.close()


def test_un_serveur_en_panne_n_empeche_pas_la_ville(browser, ville):
    """⚠️ Pas seulement « pas de reseau » : un 502 derriere Caddy (l'application
    tombee, un deploiement qui redemarre) est une reponse, pas une panne de reseau. Le
    travailleur doit la traiter comme un silence. Temoin : sans lui, la page de panne."""
    contexte, page = ouvrir(browser, ville.url)
    ville.panne = 502
    page.reload()
    page.wait_for_selector('#bandini[data-etat="titre"]', timeout=20000)
    assert page.erreurs == []
    contexte.close()

    ville.panne = None
    temoin, page = ouvrir(browser, ville.url, travailleur=False)
    ville.panne = 502
    page.reload()
    assert "en panne" in page.content()
    temoin.close()


def test_les_sons_se_gardent_d_un_coup_et_se_jouent_hors_ligne(browser, ville):
    """La ligne des OPTIONS annonce ce qu'il reste a telecharger ; ACTION les garde tous ;
    elle dit OUI ; et hors ligne, un son qu'on n'a jamais joue se charge quand meme."""
    contexte, page = ouvrir(browser, ville.url)
    page.wait_for_function("HorsLigne.etat !== null", timeout=10000)
    ligne = """() => BANDINI.Hud.menuOptions().items.find(function (x) { return x.libelle === 'LES SONS HORS LIGNE'; })"""
    avant = page.evaluate(f"() => {{ const i = ({ligne})(); return {{ detail: i.detail, actif: i.actif !== false }}; }}")
    assert avant["actif"] and re.fullmatch(r"\d+ MO", avant["detail"]), avant
    page.evaluate(f"() => ({ligne})().faire({{}})")
    page.wait_for_function("HorsLigne.etat.sons === HorsLigne.etat.total && !HorsLigne.etat.en_cours",
                           timeout=60000)
    assert page.evaluate("HorsLigne.detail()") == "OUI"

    contexte.set_offline(True)
    nom = sorted(AUDIO.glob("*.mp3"))[-1]
    octets = page.evaluate("f => fetch(f).then(r => r.arrayBuffer()).then(b => b.byteLength)",
                           f"/static/audio/{nom.name}")
    assert octets == nom.stat().st_size
    contexte.close()
