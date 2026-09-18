#!/usr/bin/env python3
"""L'inventaire de la carte — `docs/carte.md` doit nommer tout ce que le code pose.

`docs/carte.md` est l'instantané humain de la ville : districts, bâtiments,
véhicules, personnages, gangs, piétons, barrières. Mais la carte se GÉNÈRE
depuis le code (`app/carte.py` et ses voisins) — c'est le code qui fait foi,
et l'inventaire peut prendre du retard dessus sans qu'aucun test rougisse :
on ajoute un bâtiment dans `SPECIAUX`, un véhicule dans le catalogue, une gang
dans `GANGS`, et `docs/carte.md` continue de mentir tranquillement.

Ce juge compare les deux. Il lit les SLUGS dans le code (le mot stable que
l'inventaire cite en backticks) et exige que chacun apparaisse dans
`docs/carte.md`. Un slug ajouté au code sans sa ligne dans l'inventaire fait
rougir ce juge. C'est le filet : le fond (noms, couleurs, notes) reste à la
main, mais la COUVERTURE est mécanique.

Ce qu'il lit, et où :

    districts    `DISTRICTS` (`app/carte.py`) → `"slug": "…"`
    bâtiments    `SPECIAUX`  (`app/carte.py`) → `"slug": "…"`
    intérieurs   `_piece("…"`               (`app/carte.py`)
    barrières    `BARRIERES` (`app/carte.py`) → `"slug": "…"`
    véhicules    `_v("…"`                   (`app/vehicules.py`)
    gangs        `GANGS`     (`app/pietons.py`) → `"slug": "…"`
    piétons      `_p("…"`                   (`app/pietons.py`)
    personnages  `PERSONNAGES` (`app/missions.py`) → `"slug": "…"`

⚠️ Il ne PARSER rien d'exécutable : il lit le texte des fichiers, comme son
voisin `verifier_ce_qui_casse.py` lit le JS — pas d'import, donc pas de
génération de carte ni de dépendance au petit déjeuner.

Trois façons de l'appeler, comme ses voisins :

    python scripts/verifier_carte_du_plan.py              # tout le dépôt
    python scripts/verifier_carte_du_plan.py --fichier F  # ne dit rien si F n'est pas en cause
    python scripts/verifier_carte_du_plan.py --commit     # ce que l'index va commiter
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

DOC = "docs/carte.md"

#: Ce qui peut changer l'inventaire : les quatre modules de données, plus le
#: document lui-même. Écrire ailleurs ne touche pas la carte.
SURVEILLES = (
    "app/carte.py",
    "app/vehicules.py",
    "app/pietons.py",
    "app/missions/__init__.py",
    DOC,
)

#: Les blocs dont on extrait `"slug": "…"` — le motif d'ouverture et, en face,
#: le fichier où il vit.
BLOCS = (
    ("app/carte.py", r"DISTRICTS\s*:\s*tuple\[dict, \.\.\.\]\s*=\s*\("),
    ("app/carte.py", r"SPECIAUX\s*:\s*dict\[str, dict\]\s*=\s*\{"),
    ("app/carte.py", r"BARRIERES\s*:\s*tuple\[dict, \.\.\.\]\s*=\s*\("),
    ("app/pietons.py", r"GANGS\s*:\s*list\[dict\]\s*=\s*\["),
    ("app/missions/__init__.py", r"PERSONNAGES\s*:\s*list\[Personnage\]\s*=\s*\["),
)

#: Les appels d'usine où le slug est le premier argument : `_piece("terminus"…)`,
#: `_v("auto"…)`, `_p("passant"…)`. Un motif par fichier.
USINES = (
    ("app/carte.py", r"\b_piece\s*\(\s*[\"']([a-z0-9_]+)[\"']"),
    ("app/vehicules.py", r"\b_v\s*\(\s*[\"']([a-z0-9_]+)[\"']"),
    ("app/pietons.py", r"\b_p\s*\(\s*[\"']([a-z0-9_]+)[\"']"),
)

SLUG = re.compile(r"[\"']slug[\"']\s*:\s*[\"']([a-z0-9_]+)[\"']")


# --- Extraire depuis le texte ---------------------------------------------


def _bloc(source: str, motif: str) -> str:
    """Le texte de `{ … }` ou `( … )` ouvert juste après `motif`, ou "". """
    m = re.search(motif, source)
    if not m:
        return ""
    i = m.end() - 1
    ouvrant, fermant = source[i], ")" if source[i] == "(" else "}"
    if ouvrant not in "({":
        return ""
    profondeur = 0
    for j in range(i, len(source)):
        if source[j] == ouvrant:
            profondeur += 1
        elif source[j] == fermant:
            profondeur -= 1
            if profondeur == 0:
                return source[i + 1:j]
    return ""


def slugs_des_sources(sources: dict[str, str]) -> dict[str, set[str]]:
    """`{ catégorie : { slug } }`, par catégorie, pour qu'on sache où il manque."""
    par_famille: dict[str, set[str]] = {}

    def ajouter(famille: str, valeur: str) -> None:
        valeur = valeur.strip()
        if valeur:
            par_famille.setdefault(famille, set()).add(valeur)

    for fichier, motif in BLOCS:
        corps = sources.get(fichier)
        if corps is None:
            continue
        bloc = _bloc(corps, motif)
        for m in SLUG.finditer(bloc):
            ajouter(fichier, m.group(1))

    for fichier, motif in USINES:
        corps = sources.get(fichier)
        if corps is None:
            continue
        for m in re.finditer(motif, corps):
            ajouter(fichier, m.group(1))

    return par_famille


# --- Juger ------------------------------------------------------------------


def juger(sources: dict[str, str]) -> list[str]:
    manquants = [c for c in SURVEILLES if c not in sources]
    reproches = [
        f"{c} : introuvable.\n"
        "  Le juge ne peut pas vérifier ce fichier — a-t-il été renommé ou déplacé ?"
        for c in manquants
    ]

    if DOC not in sources:
        if not reproches:
            reproches.append(f"{DOC} : introuvable.")
        return reproches

    doc = sources[DOC]
    par_famille = slugs_des_sources(sources)

    # ⚠️ Le juge doit avoir LIRE quelque chose : des sources présentes mais
    # vides de slugs, c'est un bloc renommé, pas une ville vide.
    total = sum(len(v) for v in par_famille.values())
    if total == 0:
        if not reproches:
            reproches.append(
                "aucun slug n'a pu être lu dans les sources.\n"
                "  Le juge n'a rien trouvé à comparer — les blocs (`DISTRICTS`, `SPECIAUX`,\n"
                "  `GANGS`, `PERSONNAGES`…) ont-ils été renommés ou réécrits ?"
            )
        return reproches

    for famille in sorted(par_famille):
        for slug in sorted(par_famille[famille]):
            # Le slug se cite en backticks dans l'inventaire : `terminus`.
            if f"`{slug}`" not in doc:
                reproches.append(
                    f"{DOC} : le slug `{slug}` (dans {famille}) n'apparaît pas.\n"
                    "  Une brique de la ville a été ajoutée ou renommée dans le code sans\n"
                    "  être répercutée dans l'inventaire de la carte. Ajoute sa ligne\n"
                    "  (et son nom, sa couleur, sa note) dans `docs/carte.md`."
                )

    return reproches


# --- Lire le dépôt ----------------------------------------------------------


def _racine(depart: Path) -> Path:
    sortie = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=depart,
        capture_output=True,
        text=True,
    )
    return Path(sortie.stdout.strip()) if sortie.returncode == 0 else depart


def _au_commit(racine: Path, chemin: str) -> str | None:
    sortie = subprocess.run(
        ["git", "show", f":{chemin}"],
        cwd=racine,
        capture_output=True,
        text=True,
    )
    return sortie.stdout if sortie.returncode == 0 else None


def sources(racine: Path, commit: bool) -> dict[str, str]:
    lues = {}
    for chemin in SURVEILLES:
        if commit:
            corps = _au_commit(racine, chemin)
        else:
            fichier = racine / chemin
            corps = fichier.read_text(encoding="utf-8") if fichier.exists() else None
        if corps is not None:
            lues[chemin] = corps
    return lues


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--fichier", help="ne juge que si ce fichier est en cause")
    analyseur.add_argument("--commit", action="store_true", help="juge l'index, pas le disque")
    analyseur.add_argument("--cwd", default=None, help="où chercher le dépôt (défaut : le sien)")
    args = analyseur.parse_args()

    racine = _racine(Path(args.cwd).resolve()) if args.cwd else RACINE

    if args.fichier:
        vise = Path(args.fichier).resolve()
        if not any(vise == (racine / chemin).resolve() for chemin in SURVEILLES):
            return 0

    reproches = juger(sources(racine, args.commit))
    if not reproches:
        return 0

    print("L'inventaire de la carte est en retard sur le code :\n", file=sys.stderr)
    for reproche in reproches:
        print(f"  {reproche}\n", file=sys.stderr)
    print(
        "  `docs/carte.md` est l'instantané de la ville : tout slug du code doit y\n"
        "  être cité. Ajoute la ligne manquante, puis relance ce juge.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())