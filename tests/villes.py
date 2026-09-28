"""La ville des juges : générée UNE fois par processus, rendue en copie à chaque appel.

`carte.generer()` coûte six ou sept secondes, et l'audit du 27 sept. 2026 en a
compté environ deux cents dans la suite — la même ville, régénérée fichier après
fichier, juge après juge. Ce module la garde : la première demande la génère, les
suivantes la reçoivent en une copie (0,02 s).

⚠️ **UNE COPIE À CHAQUE APPEL, jamais l'objet gardé.** Un juge qui pose un char,
retire une porte ou vide une rangée travaille sur SA ville ; sans la copie, il
salirait celle de tous les juges qui passent après lui dans le même processus —
et un juge vert ou rouge selon l'ordre de la suite est pire qu'un juge lent.

⚠️ **Jamais sous un `monkeypatch` du jeu.** Le cache ne sait pas qu'on a remplacé
`chantiers.tirer` ou `mobilier.semer` : il rendrait la ville d'AVANT le patch. Un
juge qui compare « avec » et « sans » appelle `carte.generer()` lui-même.

Les trois étages, comme le jeu les bâtit : `generer` (la ville nue, une graine,
avec ou sans la bande nord), `exporter` (la ville qui part au navigateur, légende
et familles comprises), `assembler` (tout le paquet de définitions). Chacun a son
cache : `exporter` et `assembler` ne sont pas bâtis à partir de `generer` ici, pour
ne pas recopier leur recette — un étage de plus coûte une génération par
processus, une fois.
"""

from __future__ import annotations

import functools
import pickle

from app import carte, definitions


@functools.cache
def _generee(plan: tuple[str, ...], graine: int, nord: bool) -> bytes:
    return pickle.dumps(carte.generer(plan, graine, nord=nord), protocol=pickle.HIGHEST_PROTOCOL)


@functools.cache
def _exportee() -> bytes:
    return pickle.dumps(carte.exporter(), protocol=pickle.HIGHEST_PROTOCOL)


@functools.cache
def _assemblee() -> bytes:
    return pickle.dumps(definitions.assembler(), protocol=pickle.HIGHEST_PROTOCOL)


def generer(plan: tuple[str, ...] = carte.PLAN, graine: int = carte.GRAINE, nord: bool = True) -> dict:
    """`carte.generer(plan, graine, nord=nord)`, en copie."""
    return pickle.loads(_generee(tuple(plan), graine, nord))


def exporter() -> dict:
    """`carte.exporter()`, en copie."""
    return pickle.loads(_exportee())


def assembler() -> dict:
    """`definitions.assembler()`, en copie."""
    return pickle.loads(_assemblee())
