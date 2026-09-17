import json
import os
import shutil
import sys
import threading
from pathlib import Path

import pytest
from werkzeug.serving import make_server

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from app import create_app  # noqa: E402
from app.definitions import construire  # noqa: E402
from config import Config  # noqa: E402

from harnais_js import lancer_node  # noqa: E402

#: En CI, un test Node ou navigateur qui se saute est un test qui n'existe pas.
OBLIGATOIRE = os.environ.get("BANDINI_TESTS_OBLIGATOIRES") == "1"


class ConfigTest(Config):
    TESTING = True
    SECRET_KEY = "test"


@pytest.fixture
def app(tmp_path):
    class ConfigTmp(ConfigTest):
        DONNEES_DIR = str(tmp_path / "donnees")

    return create_app(ConfigTmp)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def racine():
    return RACINE


@pytest.fixture(scope="session")
def paquet():
    """Le paquet de definitions tel que le navigateur le recoit."""
    # ⚠️ Tel que le navigateur le TIENT : les definitions, et la carte remise
    # dedans a son arrivee (`Jeu.chargerDefinitions`). Elle voyage a part depuis
    # le 16 sept. 2026, mais aucun lecteur ne la cherche ailleurs.
    paquets = construire()
    donnees = json.loads(paquets.definitions.corps.decode("utf-8"))
    donnees["carte"] = json.loads(paquets.carte.corps.decode("utf-8"))
    return donnees


@pytest.fixture(scope="session")
def serveur(tmp_path_factory):
    """Vrai serveur HTTP, pour les tests de navigateur — port 0, jamais 5400 en dur."""

    class ConfigServeur(ConfigTest):
        DONNEES_DIR = str(tmp_path_factory.mktemp("donnees"))

    serveur_http = make_server("127.0.0.1", 0, create_app(ConfigServeur), threaded=True)
    fil = threading.Thread(target=serveur_http.serve_forever, daemon=True)
    fil.start()
    try:
        yield f"http://127.0.0.1:{serveur_http.server_port}"
    finally:
        serveur_http.shutdown()
        fil.join(timeout=5)


@pytest.fixture(scope="session")
def banc(paquet):
    """Fait tourner `corps` (une fonction JS `(L, o) => resultat`) dans le banc Node."""
    if OBLIGATOIRE and shutil.which("node") is None:
        pytest.fail("node est obligatoire (BANDINI_TESTS_OBLIGATOIRES=1) et il manque")
    prelude = (RACINE / "tests" / "banc.js").read_text(encoding="utf-8")

    def executer(corps: str, graine: int = 0x1A2B3C4D):
        script = prelude + "\nrapporter(banc(" + corps + "));\n"
        sortie = lancer_node(script, entree={"racine": str(RACINE), "defs": paquet, "graine": graine})
        return json.loads(sortie.strip().splitlines()[-1]) if sortie.strip() else None

    return executer
