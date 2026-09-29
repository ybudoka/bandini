import json
import os
import shutil
import sys
import threading
from pathlib import Path
from unittest import mock

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


def _creer_app(config, paquets):
    """`create_app`, sans rebâtir le paquet : il reprend celui de la session.

    ⚠️ `create_app` appelle `construire()` — une ville, les définitions, un paquet
    par mission, sept secondes — et la fixture `app` vit le temps d'UN juge :
    l'audit du 27 sept. 2026 en comptait une quarantaine de constructions
    identiques. Le paquet ne dépend que du code, pas de la config du juge."""
    with mock.patch("app.construire", lambda: paquets):
        return create_app(config)


@pytest.fixture
def app(tmp_path, paquets):
    class ConfigTmp(ConfigTest):
        DONNEES_DIR = str(tmp_path / "donnees")

    return _creer_app(ConfigTmp, paquets)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def racine():
    return RACINE


@pytest.fixture(scope="session")
def paquets():
    """UNE construction pour toute la session : `construire()` batit une ville, et
    deux villes baties separement pourraient ne pas etre la meme."""
    return construire()


@pytest.fixture(scope="session")
def paquet(paquets):
    """Le paquet de definitions tel que le navigateur le recoit."""
    # ⚠️ Tel que le navigateur le TIENT : les definitions, et la carte remise
    # dedans a son arrivee (`Jeu.chargerDefinitions`). Elle voyage a part depuis
    # le 16 sept. 2026, mais aucun lecteur ne la cherche ailleurs.
    donnees = json.loads(paquets.definitions.corps.decode("utf-8"))
    donnees["carte"] = json.loads(paquets.carte.corps.decode("utf-8"))
    # ⚠️ Et les NOTES de la musique remises a leur morceau (`Son.Notes`) : elles voyagent a
    # part depuis le 29 sept. 2026, et arrivent juste apres les definitions. Un juge qui
    # veut le paquet NU (les notes pas encore la) passe `banc(..., poser_les_notes=False)`.
    notes = json.loads(paquets.musiques.corps.decode("utf-8"))["musiques"]
    for morceau in donnees["audio"]["musiques"]:
        if morceau["slug"] in notes:
            morceau["voix"] = notes[morceau["slug"]]
    return donnees


@pytest.fixture(scope="session")
def notes_de_la_musique(paquets):
    """Les notes de la musique — un `/api/musiques`, hors du paquet depuis le 29 sept. 2026."""
    return json.loads(paquets.musiques.corps.decode("utf-8"))


@pytest.fixture(scope="session")
def a_jouer(paquets):
    """Tout ce que chaque mission demande pour se jouer — un `/api/mission/<slug>`.

    ⚠️ Hors du paquet depuis le 24 sept. 2026 : il etait au-dessus de ses deux plafonds.
    Le banc les sert comme le serveur ; voir `banc.js`.
    """
    return {slug: json.loads(p.corps.decode("utf-8")) for slug, p in paquets.a_jouer.items()}


@pytest.fixture(scope="session")
def cartes_des_blocs(paquets):
    """La carte de chaque bloc de carte — un `/api/carte/bloc/<slug>`. Le banc les sert
    comme le serveur ; voir `banc.js`."""
    return {slug: json.loads(p.corps.decode("utf-8")) for slug, p in paquets.blocs.items()}


@pytest.fixture(scope="session")
def serveur(tmp_path_factory, paquets):
    """Vrai serveur HTTP, pour les tests de navigateur — port 0, jamais 5400 en dur."""

    class ConfigServeur(ConfigTest):
        DONNEES_DIR = str(tmp_path_factory.mktemp("donnees"))

    serveur_http = make_server("127.0.0.1", 0, _creer_app(ConfigServeur, paquets), threaded=True)
    fil = threading.Thread(target=serveur_http.serve_forever, daemon=True)
    fil.start()
    try:
        yield f"http://127.0.0.1:{serveur_http.server_port}"
    finally:
        serveur_http.shutdown()
        fil.join(timeout=5)


@pytest.fixture(scope="session")
def banc(paquet, a_jouer, cartes_des_blocs, notes_de_la_musique):
    """Fait tourner `corps` (une fonction JS `(L, o) => resultat`) dans le banc Node."""
    if OBLIGATOIRE and shutil.which("node") is None:
        pytest.fail("node est obligatoire (BANDINI_TESTS_OBLIGATOIRES=1) et il manque")
    prelude = (RACINE / "tests" / "banc.js").read_text(encoding="utf-8")

    def executer(corps: str, graine: int = 0x1A2B3C4D, stockage: dict | None = None, session: dict | None = None,
                 reseau: dict | None = None, defi: dict | None = None, poser_les_missions: bool = True,
                 missions_panne: int = 0, blocs_panne: int = 0, poser_les_notes: bool = True,
                 notes_panne: int = 0):
        # `stockage` / `session` : ce que le navigateur gardait AVANT le chargement.
        # `reseau` : ce que /api/compte/ repond (M14) — l'ouverture part des que la
        # ville est batie, donc ses reponses se posent avant, jamais pendant.
        script = prelude + "\nrapporter(banc(" + corps + "));\n"
        # ⚠️ `poser_les_missions=False` : le catalogue part NU, et le jeu doit aller
        # chercher chaque mission — c'est ainsi qu'on juge la porte elle-meme.
        entree = {"racine": str(RACINE), "defs": paquet, "graine": graine,
                  "missions": a_jouer, "poser_les_missions": poser_les_missions,
                  "missions_panne": missions_panne, "blocs": cartes_des_blocs, "blocs_panne": blocs_panne,
                  # Les notes de la musique (`/api/musiques`) : le banc les sert comme le serveur.
                  # `poser_les_notes=False` les retire du paquet avant le demarrage, et
                  # `notes_panne` fait tomber les premieres demandes.
                  "notes": notes_de_la_musique, "poser_les_notes": poser_les_notes, "notes_panne": notes_panne}
        if stockage is not None:
            entree["stockage"] = stockage
        if session is not None:
            entree["session"] = session
        if reseau is not None:
            entree["reseau"] = reseau
        if defi is not None:
            entree["defi"] = defi
        sortie = lancer_node(script, entree=entree)
        return json.loads(sortie.strip().splitlines()[-1]) if sortie.strip() else None

    return executer
