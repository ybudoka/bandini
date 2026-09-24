"""Le defi du jour (M14, 5e vague) : le serveur dit quel defi est celui d'aujourd'hui.

Le jeu a six defis (`missions.DEFIS`) : un panneau ou un comptoir, un chrono, une prime — et
la prime ne se paie qu'UNE fois. Le defi du jour est l'un d'eux, **designe par la date**, le
meme pour tout le monde : c'est le serveur qui tient l'horloge, parce qu'un jeu qui tourne dans
le navigateur ne doit pas decider seul du jour qu'on est (un telephone dont l'horloge avance
d'une nuit n'a pas le meme « aujourd'hui » que l'ordinateur).

⚠️ **Il n'y a PAS de classement** : le tableau des scores est parti le 17 sept. 2026, a la
demande de Martin, et le « classement du jour » de la fiche partait avec lui. Ce qui reste du
defi du jour est ce que personne n'a retire : une date, un defi, et une prime qui se gagne
chaque jour.

⚠️ **La graine du jour ne sert qu'a CHOISIR.** La fiche disait que `/api/defi` « donne la
graine du jour » ; or les six defis sont deterministes (ni `B.rng` ni `hash2` : une rampe, un
circuit, une livraison, trois jeux d'adresse a cibles fixes) — un nombre de plus dans la
reponse n'aurait aucun lecteur. On ne livre pas un champ que personne ne lit.

⚠️ **Une rotation, pas un tirage.** `(jour - EPOQUE) % n` : chaque defi revient tous les `n`
jours, jamais deux fois de suite, et le resultat ne depend d'aucun hasard — ni de
`PYTHONHASHSEED` (le piege de `ci-pile-ou-face`) ni du processus : deux workers gunicorn
repondent la meme chose. Ajouter un defi au catalogue le fait entrer dans la rotation ; le
jour du deploiement, le defi du jour peut alors changer — c'est pourquoi le jeu ne paie qu'UNE
prime par jour, quel que soit le defi (`defiDuJour.date`, cote jeu).
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import missions

#: Le jour bascule a minuit HEURE DE QUEBEC — pas a minuit UTC, qui tombe a 20 h en ete : un
#: joueur du soir verrait « demain » avant d'avoir fini sa soiree.
FUSEAU = "America/Toronto"

#: Le premier jour de la rotation : le defi du jour est alors le PREMIER du catalogue.
EPOQUE = date(2026, 9, 20)

_journal = logging.getLogger(__name__)


def _fuseau() -> tzinfo:
    """Le fuseau de Quebec — ou, si la base des fuseaux du systeme manque (`tzdata` n'est pas
    une dependance du projet), l'heure normale de l'Est, avec un avertissement.

    ⚠️ Le repli decale la bascule d'une heure en ete (a 1 h au lieu de minuit) : c'est un jour
    qui se change une heure plus tard, pas un defi qui plante ou qui differe d'un worker a
    l'autre. Mieux qu'un 500 sur une route que le titre appelle a chaque chargement.
    """
    try:
        return ZoneInfo(FUSEAU)
    except ZoneInfoNotFoundError:
        _journal.warning("fuseau %s introuvable : repli sur UTC-5 (le jour bascule a 1 h en ete)", FUSEAU)
        return timezone(timedelta(hours=-5), "EST")


def jour_de(maintenant: datetime | None = None) -> date:
    """La date, a Quebec, de cet instant (par defaut : maintenant). `maintenant` porte son fuseau."""
    fuseau = _fuseau()
    if maintenant is None:
        return datetime.now(fuseau).date()
    if maintenant.tzinfo is None:
        raise ValueError("un instant sans fuseau ne dit pas quel jour il est")
    return maintenant.astimezone(fuseau).date()


def rotation() -> list[dict]:
    """Les defis qui tournent : ceux qu'on a des le depart (sans `debloque`).

    ⚠️ Un defi qui se DEBLOQUE (les dix-huit du 23 sept. 2026) n'entre pas dans la rotation :
    le serveur ne connait pas la partie, et il designerait a un joueur neuf un defi qu'il ne
    voit meme pas encore. Et la rotation d'avant ne bouge pas d'un jour."""
    return [d for d in missions.DEFIS if not d.get("debloque")]


def defi_du(jour: date) -> str:
    """Le slug du defi de ce jour : une rotation sur le catalogue, jamais un tirage."""
    catalogue = rotation()
    return catalogue[(jour - EPOQUE).days % len(catalogue)]["slug"]


def aujourdhui(maintenant: datetime | None = None) -> dict:
    """Ce que rend `/api/defi` : la date (celle du serveur) et le slug du defi du jour."""
    jour = jour_de(maintenant)
    return {"date": jour.isoformat(), "defi": defi_du(jour)}
