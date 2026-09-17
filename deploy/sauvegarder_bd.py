#!/usr/bin/env python3
"""Le vidage quotidien de la base de Bandini — lance par `bandini-sauvegarde-bd.timer`.

Une base de donnees sans copie de surete est une perte de donnees qui attend sa
date (M14). Une copie par jour, les sept dernieres gardees.

⚠️ `Connection.backup`, jamais une copie du fichier : en WAL, les dernieres
transactions vivent dans `bandini.sqlite3-wal`, a cote. Un `cp` du fichier seul
rend une base qui a l'air saine et qui a perdu ses dernieres parties — ou une
base corrompue, si un worker ecrivait pendant la copie.

⚠️ La bibliotheque standard seulement : il tourne avec le `python3` du serveur,
pas avec le venv d'une release qui peut disparaitre entre deux deploiements.

    python3 deploy/sauvegarder_bd.py --donnees /srv/bandini/shared/donnees \\
        --copies /srv/bandini/shared/copies
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import date
from pathlib import Path

#: ⚠️ Le meme nom que `app/bd.py` (`FICHIER`) — `tests/test_bd.py` le verifie.
FICHIER = "bandini.sqlite3"
GARDER = 7


def sauvegarder(
    donnees: Path, copies: Path, garder: int = GARDER, jour: date | None = None
) -> Path | None:
    """Copie la base du jour dans `copies`, et n'y garde que les `garder` dernieres.

    Rend le chemin de la copie, ou None s'il n'y a pas encore de base (aucun compte).
    """
    source = Path(donnees) / FICHIER
    if not source.exists():
        return None
    copies = Path(copies)
    copies.mkdir(parents=True, exist_ok=True)
    cible = copies / f"bandini-{(jour or date.today()).isoformat()}.sqlite3"
    temporaire = cible.with_name(cible.name + ".tmp")
    temporaire.unlink(missing_ok=True)

    lecture = sqlite3.connect(source, timeout=30)
    try:
        ecriture = sqlite3.connect(temporaire)
        try:
            lecture.backup(ecriture)
            verdict = ecriture.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            ecriture.close()
    finally:
        lecture.close()
    if verdict != "ok":
        temporaire.unlink(missing_ok=True)
        raise RuntimeError(f"{source} : la copie ne passe pas integrity_check ({verdict})")
    # Le nom ne prend la place d'une copie saine qu'une fois la nouvelle verifiee.
    temporaire.replace(cible)

    # Les noms portent la date ISO : l'ordre alphabetique est l'ordre des jours.
    for vieille in sorted(copies.glob("bandini-????-??-??.sqlite3"))[:-garder]:
        vieille.unlink()
    return cible


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--donnees", type=Path, required=True)
    parser.add_argument("--copies", type=Path, required=True)
    parser.add_argument("--garder", type=int, default=GARDER)
    args = parser.parse_args(argv)
    copie = sauvegarder(args.donnees, args.copies, args.garder)
    print(copie if copie else f"{args.donnees / FICHIER} : pas encore de base, rien a copier")
    return 0


if __name__ == "__main__":
    sys.exit(main())
