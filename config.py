"""Configuration de Bandini.

La partie (argent, casier, planque, missions faites) vit dans le `localStorage`
du navigateur, et c'est lui qui joue. Le serveur garde, depuis M14, les comptes
et leurs parties dans une base SQLite sous `DONNEES_DIR` — rien d'autre. Un
compte n'est qu'une synchronisation.
"""

from __future__ import annotations

import glob
import os
import socket
from pathlib import Path
from urllib.parse import urlparse

RACINE = Path(__file__).resolve().parent

#: Ce qui, modifie, change le serveur qui tourne. Le reste de la racine ne le
#: redemarre pas : voir `ce_que_le_rechargeur_ignore`.
CE_QUI_REDEMARRE_LE_SERVEUR = ("app", "config.py", "run.py")


def port_de_dev() -> int:
    """Port du serveur local — source unique, lu a l'appel pour voir le .env.

    5400 : 5200 est le site de jeux, 5300 est Auto Évasion, sur la meme machine.
    """
    explicite = (os.getenv("APP_PORT") or os.getenv("FLASK_RUN_PORT") or "").strip()
    if explicite.isdigit():
        return int(explicite)

    base_url = (os.getenv("APP_BASE_URL") or "").strip()
    if base_url:
        port = urlparse(base_url).port
        if port:
            return port

    return 5400


def ce_que_le_rechargeur_ignore(racine: Path = RACINE) -> set[str]:
    """Les `exclude_patterns` du rechargeur de Werkzeug : tout sauf `app/`, `config.py`, `run.py`.

    ⚠️ Sans `watchdog`, Werkzeug surveille chaque `.py` sous `sys.path` — et la
    racine du depot y est, c'est le dossier de `run.py`. Un juge ecrit dans
    `tests/` par une autre session redemarrait donc Flask, et le jeu ouvert
    dans Chrome perdait son serveur. On liste ce qui compte plutot que ce qui
    ne compte pas : un dossier ajoute a la racine est ignore des le demarrage
    suivant. `templates/` et `static/` n'ont pas besoin de redemarrage (Jinja
    relit ses gabarits en debug, et le statique est servi tel quel).
    """
    motifs: set[str] = set()
    for entree in racine.iterdir():
        if entree.name in CE_QUI_REDEMARRE_LE_SERVEUR:
            continue
        # Les motifs sont des fnmatch : un `[` dans le chemin serait une classe.
        chemin = glob.escape(str(entree))
        motifs.add(chemin)
        motifs.add(chemin + os.sep + "*")
    return motifs


def hote_est_local(hote: str) -> bool:
    """Vrai si le serveur n'ecoute que la machine.

    ⚠️ C'est la seule condition qui allume la console interactive de Werkzeug
    (`use_debugger`) : un shell Python ouvert a tout le reseau de la maison
    n'a rien a faire la. Depuis que `APP_HOST` vaut `0.0.0.0` par defaut, cette
    reponse est `False` la plupart du temps — c'est voulu.
    """
    return hote.strip().strip("[]") in ("127.0.0.1", "localhost", "::1")


def adresses_du_reseau_local() -> list[str]:
    """Les adresses IPv4 de cette machine sur le reseau de la maison, sans le loopback.

    ⚠️ Werkzeug en annonce une seule, et elle peut mentir : il la trouve en
    ouvrant une socket vers une adresse privee quelconque (`get_interface_ip`),
    donc c'est l'adresse de la route par defaut. Avec un VPN monte, c'est celle
    du tunnel (`10.x`) qu'il imprime — que le telephone du salon ne joint
    **pas**. Le nom de la machine, lui, resout vers les vraies interfaces.
    """
    adresses: list[str] = []
    try:
        _, _, trouvees = socket.gethostbyname_ex(socket.gethostname())
    except OSError:  # pas de resolution du nom de la machine (docker, CI)
        trouvees = []

    for adresse in trouvees:
        # 127.x : la machine elle-meme ; 169.254.x : une interface sans bail DHCP.
        if not adresse.startswith(("127.", "169.254.")) and adresse not in adresses:
            adresses.append(adresse)

    if adresses:
        return adresses

    # Repli : l'adresse source que le systeme choisit pour sortir. C'est le
    # coup de Werkzeug — faute de mieux quand le nom ne resout rien.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as prise:
        try:
            prise.connect(("10.253.155.219", 58162))
        except OSError:
            return []
        adresse = prise.getsockname()[0]
    return [adresse] if not adresse.startswith("127.") else []


def _flag(name: str, default: bool = False) -> bool:
    valeur = (os.getenv(name) or "").strip().lower()
    if not valeur:
        return default
    return valeur in {"1", "true", "yes", "on", "oui"}


#: Ce qui n'est PAS un secret : le defaut ci-dessous, et celui de `.env.example`.
CLES_DE_DEVELOPPEMENT = ("cle-de-developpement-a-changer", "change-cette-cle")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cle-de-developpement-a-changer")

    SITE_NAME = os.getenv("SITE_NAME", "Bandini")
    SITE_TAGLINE = os.getenv("SITE_TAGLINE", "Baie-des-Brumes t'attend. La police aussi.")
    SITE_AUTEUR = os.getenv("SITE_AUTEUR", "Martin Gagné")

    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5400")

    # Servi en https, c'est la production : le cookie d'appareil y est `Secure`, et
    # la cle de developpement y est refusee au demarrage. ⚠️ Pas `FLASK_DEBUG` :
    # `.env.example` le met a false, et le serveur du salon refuserait de partir.
    PRODUCTION = APP_BASE_URL.startswith("https://")

    # Ou vit la base SQLite des comptes. Relatif a la racine du projet si ce n'est pas absolu.
    DONNEES_DIR = str((RACINE / os.getenv("DONNEES_DIR", "donnees")).resolve())

    SEND_FILE_MAX_AGE_DEFAULT = int(os.getenv("STATIC_MAX_AGE", "0"))

    # Un appel de compte pese a peine plus que quelques dizaines d'octets. La
    # seule exception, une partie qui monte, releve sa borne dans sa route
    # (`comptes.PARTIE_MAX_OCTETS`).
    MAX_CONTENT_LENGTH = 16 * 1024

    DEBUG = _flag("FLASK_DEBUG", False)
