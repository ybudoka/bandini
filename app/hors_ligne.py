"""Installable, et jouable hors ligne : le travailleur (service worker) et ce qu'il garde.

Demande de Martin : « est-ce compliqué de faire du jeu une webapp installable ? »,
puis « jouable hors ligne ».

Le travailleur, c'est `static/js/travailleur.js` ; ce module-ci lui pose devant
`HORS_LIGNE`, ce qu'il doit savoir de CETTE construction du site :

- **la coquille** — ce que la page d'accueil demande pour arriver a l'ecran titre.
  ⚠️ Elle est LUE DANS LA PAGE RENDUE, jamais ecrite a la main : un script de plus
  dans `index.html`, et une liste tenue a cote l'oublierait — la ville ne
  s'ouvrirait plus hors ligne, sans que rien ne rougisse en ligne ;
- **les sons** — les mp3 du dossier, avec leur poids : ils se gardent a l'usage, et
  « tous d'un coup » est un bouton des OPTIONS (14 Mo sur un forfait cellulaire ne
  s'avalent pas en silence) ;
- **l'empreinte** — un sha256 de tout ce qui precede ET du code du travailleur. Elle
  nomme le cache de la coquille : le cache se nomme par son CONTENU, jamais par la
  version (voir `version.py`, qui dit pourquoi un numero ment).

⚠️ Le travailleur est servi a la RACINE (`routes.travailleur`) : il ne controle que
son dossier, et `/static/` n'est pas la page. Et en `no-cache` : nginx garde
`/static/` sept jours, et un travailleur fige une semaine se referme sur la session
suivante.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

#: Le code du travailleur, lu a chaque demande : le serveur de dev ne redemarre
#: pas pour un fichier JS (`run.py`), et un travailleur en retard d'une edition
#: ferait chercher une panne qui n'existe pas.
SOURCE = Path(__file__).resolve().parent.parent / "static" / "js" / "travailleur.js"

#: Tout ce que la page demande par un attribut : ses scripts, sa feuille, ses
#: images, son manifeste — et les deux paquets que `jeu.js` va chercher.
_ADRESSES = re.compile(r'\s(?:src|href|data-url-definitions|data-url-carte)="([^"]+)"')


def coquille(page: str, accueil: str) -> list[str]:
    """Les adresses de la page, dans l'ordre, sans doublon ni rien d'une autre origine."""
    vues: list[str] = [accueil]
    for brute in _ADRESSES.findall(page):
        adresse = html.unescape(brute)
        morceaux = urlsplit(adresse)
        if morceaux.scheme or morceaux.netloc or not adresse.startswith("/"):
            continue
        if adresse not in vues:
            vues.append(adresse)
    return vues


def sons(dossier: Path, url_dossier: str) -> dict:
    """Les mp3 servis, avec leur poids : ce que « tous d'un coup » telechargerait.

    ⚠️ `iterdir()` ne descend pas : `audio/reserve/` n'est pas servi au jeu."""
    fichiers = sorted((f for f in dossier.iterdir() if f.is_file() and f.suffix == ".mp3"),
                      key=lambda f: f.name) if dossier.is_dir() else []
    return {
        "dossier": url_dossier,
        "fichiers": [{"nom": f.name, "octets": f.stat().st_size} for f in fichiers],
    }


def travailleur(page: str, accueil: str, dossier_audio: Path, url_audio: str) -> tuple[str, str]:
    """Le corps du travailleur et son empreinte."""
    source = SOURCE.read_text(encoding="utf-8")
    config = {"accueil": accueil, "coquille": coquille(page, accueil),
              "audio": sons(dossier_audio, url_audio)}
    brut = json.dumps(config, ensure_ascii=False, sort_keys=True)
    empreinte = hashlib.sha256((brut + "\n" + source).encode("utf-8")).hexdigest()[:16]
    config["empreinte"] = empreinte
    entete = "const HORS_LIGNE = " + json.dumps(config, ensure_ascii=False, sort_keys=True) + ";\n"
    return entete + source, empreinte
