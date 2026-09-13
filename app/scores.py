"""Le tableau des meilleurs scores — un fichier JSON, rien de plus.

Pas de base de donnees : quelques dizaines d'entrees, ecrites rarement. Le
fichier est reecrit en entier a chaque ajout, sous un verrou de processus ET un
verrou de fichier (gunicorn a deux workers).

Ce qui est garde : un pseudo court, la fortune, les missions faites, les
proprietes possedees, la duree de la partie. Rien qui identifie une personne.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from . import economie, missions

NB_GARDES = 50
NB_AFFICHES = 10
PSEUDO_MAX = 16
DUREE_MAX = 7 * 24 * 3600

#: Lettres (accents compris), chiffres, espace, tiret, souligne. Rien d'autre :
#: le pseudo est reaffiche a tout le monde.
_PSEUDO = re.compile(r"^[\w \-]{1,16}$", re.UNICODE)

_verrou = threading.Lock()


class ScoreInvalide(ValueError):
    pass


def _entier(donnees: dict, cle: str, minimum: int, maximum: int) -> int:
    valeur = donnees.get(cle)
    if not isinstance(valeur, int) or isinstance(valeur, bool):
        raise ScoreInvalide(f"{cle} : entier attendu")
    if not minimum <= valeur <= maximum:
        raise ScoreInvalide(f"{cle} : entre {minimum} et {maximum}")
    return valeur


def valider(donnees: object) -> dict:
    """Rend un score propre, ou leve ScoreInvalide."""
    if not isinstance(donnees, dict):
        raise ScoreInvalide("corps attendu : un objet JSON")

    pseudo = str(donnees.get("pseudo", "")).strip()
    pseudo = re.sub(r"\s+", " ", pseudo)
    if not _PSEUDO.match(pseudo):
        raise ScoreInvalide(f"pseudo : 1 à {PSEUDO_MAX} lettres, chiffres, espaces ou tirets")

    fortune = _entier(donnees, "fortune", 0, economie.FORTUNE_MAX)
    faites = _entier(donnees, "missions", 0, max(0, len(missions.CATALOGUE)))
    proprietes = _entier(donnees, "proprietes", 0, len(economie.PROPRIETES))
    duree = _entier(donnees, "duree_s", 1, DUREE_MAX)

    # Vraisemblance, pas anti-triche : un navigateur bidouille peut envoyer ce
    # qu'il veut, mais pas plus vite que le jeu ne peut donner.
    if fortune > economie.ARGENT_DEPART + economie.GAIN_MAX_PAR_SECONDE * duree:
        raise ScoreInvalide("fortune : invraisemblable pour cette durée")

    return {"pseudo": pseudo, "fortune": fortune, "missions": faites,
            "proprietes": proprietes, "duree_s": duree}


def _cle(score: dict) -> tuple:
    return (-score.get("fortune", 0), -score.get("missions", 0),
            score.get("duree_s", DUREE_MAX), score.get("date", ""))


class Tableau:
    def __init__(self, dossier: str | os.PathLike) -> None:
        self.dossier = Path(dossier)
        self.fichier = self.dossier / "scores.json"

    def _lire_sans_verrou(self) -> list[dict]:
        if not self.fichier.exists():
            return []
        try:
            contenu = json.loads(self.fichier.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return []
        if not isinstance(contenu, list):
            return []
        return [s for s in contenu if isinstance(s, dict)]

    def meilleurs(self, n: int = NB_AFFICHES) -> list[dict]:
        with _verrou:
            scores = self._lire_sans_verrou()
        scores.sort(key=_cle)
        return scores[:n]

    def ajouter(self, donnees: object) -> tuple[dict, int]:
        """Ajoute un score. Rend (score, rang 1-based dans le tableau garde)."""
        score = valider(donnees)
        score["date"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        self.dossier.mkdir(parents=True, exist_ok=True)
        verrou_fichier = self.dossier / ".scores.lock"

        with _verrou, open(verrou_fichier, "w") as fd:
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                scores = self._lire_sans_verrou()
                scores.append(score)
                scores.sort(key=_cle)
                scores = scores[:NB_GARDES]
                temporaire = self.fichier.with_suffix(".json.tmp")
                temporaire.write_text(
                    json.dumps(scores, ensure_ascii=False, indent=1), encoding="utf-8"
                )
                os.replace(temporaire, self.fichier)
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)

        rang = next((i + 1 for i, s in enumerate(scores) if s is score), 0)
        return score, rang
