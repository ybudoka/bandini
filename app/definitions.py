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

from . import (armes, audio, carte, devantures, economie, journal, magasins, manettes,
               missions, pietons, recherche, vehicules)
from .version import VERSION


def assembler() -> dict:
    # ⚠️ Les frontieres de gangs tiennent des DEUX fiches et d'aucune seule :
    # les rectangles de districts viennent de `carte`, qui ne sait pas qui tient
    # quoi ; les gangs viennent de `pietons`, qui ne sait pas ou sont les
    # rectangles. On les marie ICI, une fois, et le navigateur lit le resultat
    # au lieu de le recalculer — « une fiche que le navigateur ne lisait pas »
    # a son symetrique, « un calcul que Python ne pouvait pas juger ».
    ville = carte.exporter()
    gens = pietons.exporter()
    gens["frontieres"] = pietons.frontieres(ville)
    return {
        "version": VERSION,
        "tuile_px": carte.TUILE_PX,
        "audio": audio.exporter(),
        "vehicules": vehicules.CATALOGUE,
        "conduite": vehicules.exporter_conduite(),
        "armes": armes.CATALOGUE,
        "ordre_armes": armes.ORDRE_CYCLE,
        "armes_regles": armes.REGLES,
        "economie": economie.exporter(),
        "recherche": recherche.exporter(),
        "pietons": gens,
        "manettes": manettes.exporter(),
        "devantures": devantures.exporter(),
        "carte": ville,
        "missions": missions.CATALOGUE,
        "defis": missions.DEFIS,
        "personnages": missions.PERSONNAGES,
        # Les quatre phrases de l'ouverture, avec leur slug de voix : le
        # navigateur les lit, il ne refait pas la regle du slug.
        "ouverture": missions.repliques_ouverture(),
        "types_objectifs": list(missions.TYPES_OBJECTIFS),
        "journal": journal.REGLES,
        "journal_speciales": journal.SPECIALES,
        "journal_lecons": journal.LECONS,
        "marche_noir": magasins.MARCHE_NOIR,
        "magasins": magasins.CATALOGUE,
        "ambulants": magasins.AMBULANTS,
        "reclame": magasins.RECLAME,
        "comptoirs": magasins.COMPTOIRS,
        "tenues": magasins.TENUES,
        "coiffures": magasins.COIFFURES,
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
