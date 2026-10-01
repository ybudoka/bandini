"""Les fichiers statiques à l'empreinte de LEUR contenu : `?v=<empreinte>`, plus la version du site.

La vague 3 de « Charger les districts autour du joueur » (docs/jalons/charger-les-districts-autour-du-joueur.md,
1er oct. 2026). Mesuré sous Chromium, réseau « 3G rapide » et processeur ×4 : **les scripts du jeu font 93 % de
ce qui voyage avant l'écran titre** (1,56 Mo sur le fil, 10 s sur 12,6) — la carte et les définitions, 108 Ko.
Et ils portaient tous `?v=<version>` : la version monte à chaque commit `feat:`/`fix:`, donc chaque mise en ligne
changeait l'adresse des 87 scripts, et le téléphone les retéléchargeait TOUS, même ceux qui n'avaient pas changé
d'un octet (nginx les garde pourtant sept jours, `expires 7d`).

Ici, chaque adresse porte l'empreinte de son PROPRE fichier : une mise en ligne qui touche trois scripts n'en
fait repartir que trois, et le cache du navigateur rend les 84 autres sans même demander.

⚠️ L'empreinte se relit quand le fichier change sous le serveur (date et taille) : le serveur de dev ne
redémarre pas pour un script (`run.py`), et une adresse figée servirait l'ancien fichier du cache.
⚠️ Le gabarit garde le texte `filename='js/…'` : le banc d'essai (`tests/banc.js`), le compte de la barre
(`routes._scripts_du_jeu`) et la coquille hors ligne (`hors_ligne.coquille`) lisent la liste là.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from threading import Lock

#: Assez pour qu'une collision n'arrive jamais entre deux versions d'un même fichier.
LONGUEUR = 12


class Empreintes:
    """`empreintes("js/jeu.js")` → l'empreinte du fichier, relue seulement s'il a changé sur le disque."""

    def __init__(self, dossier: Path):
        self.dossier = Path(dossier)
        self._connues: dict[str, tuple[tuple[int, int], str]] = {}
        self._verrou = Lock()

    def __call__(self, nom: str) -> str:
        chemin = self.dossier / nom
        etat = chemin.stat()
        cle = (etat.st_mtime_ns, etat.st_size)
        connue = self._connues.get(nom)
        if connue and connue[0] == cle:
            return connue[1]
        empreinte = hashlib.sha256(chemin.read_bytes()).hexdigest()[:LONGUEUR]
        with self._verrou:
            self._connues[nom] = (cle, empreinte)
        return empreinte
