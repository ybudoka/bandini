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

#: Le commentaire qui ouvre la RÉSERVE du `.pls` : les règles d'en dessous attendent
#: une réplique qui dise leur mot (les prochaines missions). Au-dessus, chaque règle
#: touche une réplique qu'on entend déjà — le juge l'exige, pour qu'une faute de frappe
#: dans un mot ne passe pas en silence.
MARQUE_RESERVE = "EN RÉSERVE"


def _lexemes() -> list[tuple[str, str, bool]]:
    """(mot écrit, mot entendu, en réserve), dans l'ordre du fichier."""
    parseur = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    racine = ET.parse(FICHIER, parseur).getroot()
    resultat, reserve = [], False
    for noeud in racine:
        if noeud.tag is ET.Comment:
            reserve = reserve or MARQUE_RESERVE in (noeud.text or "")
        elif noeud.tag == f"{{{ESPACE}}}lexeme":
            resultat.append((noeud.findtext("pls:grapheme", namespaces=_NS),
                             noeud.findtext("pls:alias", namespaces=_NS), reserve))
    return resultat


def regles() -> list[tuple[str, str]]:
    """(mot écrit, mot entendu), dans l'ordre du fichier — l'ordre compte : la première qui colle gagne."""
    return [(mot, alias) for mot, alias, _ in _lexemes()]


def en_reserve() -> set[str]:
    """Les mots des règles qui attendent leur réplique."""
    return {mot for mot, _, reserve in _lexemes() if reserve}


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


def _tout() -> re.Pattern | None:
    table = regles()
    return re.compile("|".join(_motif(mot) for mot, _ in table)) if table else None


def touches(texte: str) -> list[str]:
    """Les mots de ce texte qu'une règle change VRAIMENT, dans l'ordre du dictionnaire.
    ⚠️ Même passe qu'`entendu` : dans « Ti-Guy », « Guy » n'est pas touché, « Ti-Guy » l'a pris."""
    motif = _tout()
    pris = {m.group(0) for m in motif.finditer(texte)} if motif else set()
    return [mot for mot, _ in regles() if mot in pris]


def entendu(texte: str) -> str:
    """Ce que la voix dira — le texte après les règles. ⚠️ Une seule passe, la
    première règle qui colle gagne : un alias ne se fait pas réécrire à son tour."""
    motif = _tout()
    if motif is None:
        return texte
    alias = dict(regles())
    return motif.sub(lambda m: alias[m.group(0)], texte)
