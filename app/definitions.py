"""Le paquet de definitions — tout ce que le navigateur recoit, en une requete.

Construit UNE fois au demarrage : les catalogues ne changent pas sous un
processus lance. L'`etag` est une empreinte du contenu : un navigateur qui a
deja le paquet revalide gratuitement (304), et sa sauvegarde locale sait si le
catalogue a change depuis (un vehicule possede qui n'existe plus, par exemple).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from . import armes, audio, carte, economie, journal, magasins, missions, pietons, recherche, vehicules
from .version import VERSION


def assembler() -> dict:
    return {
        "version": VERSION,
        "tuile_px": carte.TUILE_PX,
        "audio": audio.exporter(),
        "vehicules": vehicules.CATALOGUE,
        "conduite": vehicules.exporter_conduite(),
        "armes": armes.CATALOGUE,
        "ordre_armes": armes.ORDRE_CYCLE,
        "economie": economie.exporter(),
        "recherche": recherche.exporter(),
        "pietons": pietons.exporter(),
        "carte": carte.exporter(),
        "missions": missions.CATALOGUE,
        "defis": missions.DEFIS,
        "personnages": missions.PERSONNAGES,
        "types_objectifs": list(missions.TYPES_OBJECTIFS),
        "journal": journal.REGLES,
        "magasins": magasins.CATALOGUE,
        "ambulants": magasins.AMBULANTS,
        "tenues": magasins.TENUES,
    }


def empreinte(corps: bytes) -> str:
    return hashlib.sha256(corps).hexdigest()[:16]


@dataclass(frozen=True)
class Paquet:
    corps: bytes
    etag: str

    @property
    def taille(self) -> int:
        return len(self.corps)


def construire() -> Paquet:
    donnees = assembler()
    # Sans l'empreinte d'abord : elle depend du reste, on l'ajoute apres.
    brut = json.dumps(donnees, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    etag = empreinte(brut.encode("utf-8"))
    donnees["empreinte"] = etag
    corps = json.dumps(donnees, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return Paquet(corps=corps.encode("utf-8"), etag=etag)
