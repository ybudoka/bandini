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

from app import create_app, pliage, statiques  # noqa: E402
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
    # ⚠️ Et DÉPLIÉE (30 sept. 2026) : elle voyage en colonnes (`app/pliage.py`), et le navigateur la déplie en
    # arrivant. Le banc, lui, la sert PLIÉE, comme le serveur (`carte_pliee`, plus bas).
    donnees["carte"] = pliage.deplier(json.loads(paquets.carte.corps.decode("utf-8")))
    # ⚠️ Et les NOTES de la musique remises a leur morceau (`Son.Notes`) : elles voyagent a
    # part depuis le 29 sept. 2026, et arrivent juste apres les definitions. Un juge qui
    # veut le paquet NU (les notes pas encore la) passe `banc(..., poser_les_notes=False)`.
    notes = json.loads(paquets.musiques.corps.decode("utf-8"))["musiques"]
    for morceau in donnees["audio"]["musiques"]:
        if morceau["slug"] in notes:
            morceau["voix"] = notes[morceau["slug"]]
    # ⚠️ Et la SUITE du paquet (`/api/suite`, 30 sept. 2026 : le Clairon, les Galeries hantées), remise dans les
    # définitions à son arrivée (`Suite.poser`), sous les mêmes clés. Un juge qui veut le paquet NU (la suite pas
    # encore là) passe `banc(..., poser_la_suite=False)`.
    for cle, valeur in json.loads(paquets.suite.corps.decode("utf-8")).items():
        if cle != "empreinte":
            donnees[cle] = valeur
    return donnees


@pytest.fixture(scope="session")
def carte_pliee(paquets):
    """La carte telle qu'elle voyage sur `/api/carte` : pliée en colonnes (`app/pliage.py`, 30 sept. 2026)."""
    return json.loads(paquets.carte.corps.decode("utf-8"))


@pytest.fixture(scope="session")
def suite_du_paquet(paquets):
    """La suite du paquet — un `/api/suite`, hors des définitions depuis le 30 sept. 2026."""
    return json.loads(paquets.suite.corps.decode("utf-8"))


@pytest.fixture(scope="session")
def notes_de_la_musique(paquets):
    """Les notes de la musique — un `/api/musiques`, hors du paquet depuis le 29 sept. 2026."""
    return json.loads(paquets.musiques.corps.decode("utf-8"))


@pytest.fixture(scope="session")
def collections_du_paquet(paquets):
    """Les collections — un `/api/collections`, hors du paquet et de la carte depuis le 30 sept. 2026 : le
    catalogue des cartes de hockey et leurs places. Le banc les sert comme le serveur."""
    return json.loads(paquets.collections.corps.decode("utf-8"))


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
def scripts_servis(tmp_path_factory):
    """Les scripts du jeu tels que le téléphone les reçoit : MAIGRES (vague 4 des districts, 1er oct. 2026 —
    `app/statiques.py`), sans commentaires ni indentation, ligne pour ligne. Le banc les joue : tous les juges JS
    jugent ce que le navigateur exécute, et une erreur nomme toujours la bonne ligne du source."""
    dossier = tmp_path_factory.mktemp("scripts_servis")
    for nom in statiques.scripts_de_la_page((RACINE / "templates" / "index.html").read_text(encoding="utf-8")):
        source = (RACINE / "static" / nom).read_text(encoding="utf-8")
        (dossier / Path(nom).name).write_text(statiques.maigrir(source), encoding="utf-8")
    return str(dossier)


@pytest.fixture(scope="session")
def banc(paquet, a_jouer, cartes_des_blocs, notes_de_la_musique, collections_du_paquet, suite_du_paquet, carte_pliee,
         scripts_servis):
    """Fait tourner `corps` (une fonction JS `(L, o) => resultat`) dans le banc Node."""
    if OBLIGATOIRE and shutil.which("node") is None:
        pytest.fail("node est obligatoire (BANDINI_TESTS_OBLIGATOIRES=1) et il manque")
    prelude = (RACINE / "tests" / "banc.js").read_text(encoding="utf-8")

    def executer(corps: str, graine: int = 0x1A2B3C4D, stockage: dict | None = None, session: dict | None = None,
                 reseau: dict | None = None, defi: dict | None = None, poser_les_missions: bool = True,
                 missions_panne: int = 0, blocs_panne: int = 0, poser_les_notes: bool = True,
                 notes_panne: int = 0, collections_panne: int = 0, poser_la_suite: bool = True,
                 suite_panne: int = 0):
        # `stockage` / `session` : ce que le navigateur gardait AVANT le chargement.
        # `reseau` : ce que /api/compte/ repond (M14) — l'ouverture part des que la
        # ville est batie, donc ses reponses se posent avant, jamais pendant.
        script = prelude + "\nrapporter(banc(" + corps + "));\n"
        # ⚠️ `poser_les_missions=False` : le catalogue part NU, et le jeu doit aller
        # chercher chaque mission — c'est ainsi qu'on juge la porte elle-meme.
        # ⚠️ LA CARTE PLIÉE, comme le serveur la sert (30 sept. 2026) : le jeu la déplie en arrivant
        # (`Pliage.deplier`), et TOUS les juges du banc jouent donc sur la ville dépliée par le navigateur.
        # ⚠️ LES SCRIPTS MAIGRES, comme le serveur les sert (1er oct. 2026) : `scripts_servis`.
        entree = {"racine": str(RACINE), "scripts": scripts_servis, "defs": {**paquet, "carte": carte_pliee}, "graine": graine,
                  "missions": a_jouer, "poser_les_missions": poser_les_missions,
                  "missions_panne": missions_panne, "blocs": cartes_des_blocs, "blocs_panne": blocs_panne,
                  # Les notes de la musique (`/api/musiques`) : le banc les sert comme le serveur.
                  # `poser_les_notes=False` les retire du paquet avant le demarrage, et
                  # `notes_panne` fait tomber les premieres demandes.
                  "notes": notes_de_la_musique, "poser_les_notes": poser_les_notes, "notes_panne": notes_panne,
                  # Les collections (`/api/collections`) : servies comme le serveur ; `collections_panne` fait
                  # tomber les premières demandes.
                  "collections": collections_du_paquet, "collections_panne": collections_panne,
                  # La suite du paquet (`/api/suite`) : servie comme le serveur. `poser_la_suite=False` retire
                  # ses clés des définitions avant le démarrage, et `suite_panne` fait tomber les premières demandes.
                  "suite": suite_du_paquet, "poser_la_suite": poser_la_suite, "suite_panne": suite_panne}
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
