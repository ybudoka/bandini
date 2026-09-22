"""LE DICTIONNAIRE DE PRONONCIATION — comment une voix dit un mot, sans changer le mot.

Les règles vivent dans `prononciation.pls` (le format W3C qu'ElevenLabs lit) :
un mot tel qu'on l'écrit, et l'orthographe qu'on veut ENTENDRE.

    affiché : « Prenez donc la rue des Érables. »
    entendu : « Prenez don la rue des Érables. »

⚠️ **Martin, 22 sept. 2026** : « crée moi un dictionnaire pour mon jeu » (les
*pronunciation dictionaries* d'ElevenLabs). C'est la troisième voie que
`docs/ecrire-un-accent.md` § 5 laissait fermée : réécrire « donc » en « don » dans
le texte, le juge mot à mot le refuse (la voix doit dire les mêmes mots que la
boîte). Ici, le texte et le `jeu=` ne bougent pas : ElevenLabs substitue de SON
côté, au moment de générer.

⚠️ **Le dictionnaire se téléverse, puis se désigne.** ElevenLabs le garde sous un
identifiant et une version ; `prononciation.json` note lesquels, et l'empreinte du
`.pls` qu'on a envoyé. Tant que l'empreinte colle, on réutilise ; dès que le `.pls`
change, `scripts/audio_elevenlabs.py` en téléverse un neuf avant la première voix.
Le téléversement est gratuit, la voix ne l'est pas.
"""

from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

FICHIER = Path(__file__).with_name("prononciation.pls")

#: Ce qui a été téléversé : `{"empreinte", "id", "version_id"}`. Versionné, pour
#: que toutes les sessions désignent le même dictionnaire au lieu d'en créer un
#: chacune.
TELEVERSE = Path(__file__).with_name("prononciation.json")

#: Le nom du dictionnaire chez ElevenLabs (on le retrouve sous ce nom dans l'interface).
NOM = "Bandini — le parler de Baie-des-Brumes"

ESPACE = "http://www.w3.org/2005/01/pronunciation-lexicon"
_NS = {"pls": ESPACE}


def regles() -> list[tuple[str, str]]:
    """(mot écrit, mot entendu), dans l'ordre du fichier — l'ordre compte : la première qui colle gagne."""
    racine = ET.parse(FICHIER).getroot()
    return [(lexeme.findtext("pls:grapheme", namespaces=_NS),
             lexeme.findtext("pls:alias", namespaces=_NS))
            for lexeme in racine.findall("pls:lexeme", _NS)]


def empreinte() -> str:
    return hashlib.sha256(FICHIER.read_bytes()).hexdigest()[:16]


def televerse() -> dict | None:
    """Le dictionnaire à désigner, s'il a été téléversé DANS SA VERSION ACTUELLE ; sinon rien."""
    try:
        note = json.loads(TELEVERSE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return note if note.get("empreinte") == empreinte() and note.get("id") else None


def noter(identifiant: str, version: str | None) -> dict:
    note = {"empreinte": empreinte(), "id": identifiant, "version_id": version}
    TELEVERSE.write_text(json.dumps(note, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return note


def _motif(mot: str) -> str:
    # ⚠️ Comme ElevenLabs (word_boundaries) : un mot entier, jamais un morceau —
    # « Roy » ne touche pas « Royal », ni « run » « [running] ».
    return rf"(?<!\w){re.escape(mot)}(?!\w)"


def touches(texte: str) -> list[str]:
    """Les mots de ce texte qu'une règle change, dans l'ordre du dictionnaire."""
    return [mot for mot, _ in regles() if re.search(_motif(mot), texte)]


def entendu(texte: str) -> str:
    """Ce que la voix dira — le texte après les règles. ⚠️ Une seule passe, la
    première règle qui colle gagne : un alias ne se fait pas réécrire à son tour."""
    table = regles()
    if not table:
        return texte
    alias = dict(table)
    return re.sub("|".join(_motif(mot) for mot, _ in table), lambda m: alias[m.group(0)], texte)
