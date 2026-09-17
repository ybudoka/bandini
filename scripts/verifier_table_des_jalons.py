#!/usr/bin/env python3
"""La table des jalons — six colonnes, et personne ne la reduit a trois en passant.

`docs/plan.md` ouvre sur « Etat des jalons » : une ligne par morceau de travail,
divisee en `Jalon | Etat | Date | Prio | Genre | Notes`. C'est le tableau de bord
des sessions — plusieurs Claude ecrivent dans le meme arbre, et cette table est le
seul endroit ou elles se voient.

Une session qui ajoute sa ligne recopie souvent la forme qu'elle a en tete, pas
celle du fichier : elle ecrit `| Mon jalon | **P2** **correctif**, **en cours**
(14 sept.) | ... |` — trois colonnes dans une table qui en compte six. Markdown
ne s'en plaint pas, il avale la ligne et la rend de travers ; la table perd sa
division sans qu'un test rougisse. Ce detecteur l'attrape.

Il juge la FORME, jamais le fond : ni l'ordre des lignes, ni les dates, ni qui a
raison sur une priorite. Ce qu'il exige :

1. six colonnes par ligne, pas une de plus, pas une de moins ;
2. un etat connu (`livré`, `livrée`, `en cours`, `à faire`), precede de son icone :
   ✅ pour ce qui est livre, ⬜ pour tout le reste ;
3. une date `JJ mois AAAA` ou `—`, et jamais une date restee collee dans l'etat ;
4. une prio `P1` a `P4` ou `—` ;
5. un genre `ajout`, `correctif` ou `—`.

Appele de trois facons, comme son voisin `verifier_carte_du_depot.py` :

    python scripts/verifier_table_des_jalons.py              # tout le plan
    python scripts/verifier_table_des_jalons.py --fichier F  # ne dit rien si F n'est pas le plan
    python scripts/verifier_table_des_jalons.py --commit     # ce qui part au commit
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PLAN = "docs/plan.md"
TITRE = "## État des jalons"
ENTETE = "| Jalon | État | Date | Prio | Genre | Notes |"

COLONNES = 6

ETATS = ("livré", "livrée", "en cours", "à faire")
# L'icone devant l'etat (demande de Martin, 17 sept. 2026) : un crochet pour ce qui
# est livre, une case vide pour le reste — la colonne se lit d'un coup d'oeil.
ICONE_LIVRE = "✅"
ICONE_AUTRE = "⬜"
MOIS = (
    "janv.",
    "févr.",
    "mars",
    "avril",
    "mai",
    "juin",
    "juill.",
    "août",
    "sept.",
    "oct.",
    "nov.",
    "déc.",
)
DATE = re.compile(r"^\d{1,2} (?:" + "|".join(map(re.escape, MOIS)) + r") \d{4}$")
PRIO = re.compile(r"^\*\*P[1-4]\*\*$")
GENRE = re.compile(r"^(?:ajout|\*\*correctif\*\*)$")
# une date entre parentheses, la ou elle ne devrait plus etre depuis qu'il y a
# une colonne Date : « **livré** (14 sept. 2026) »
DATE_COLLEE = re.compile(r"\(\s*\d{1,2} (?:" + "|".join(map(re.escape, MOIS)) + r")")


def _dedans(texte: str) -> str:
    """Le corps d'une cellule, sans le gras ni les espaces."""
    return texte.strip().strip("*").strip()


def _icone(etat: str) -> tuple[str | None, str]:
    """L'icone en tete de la cellule d'etat (ou None), et ce qui la suit."""
    for icone in (ICONE_LIVRE, ICONE_AUTRE):
        if etat.startswith(icone):
            return icone, etat[len(icone) :].strip()
    return None, etat


def table(corps: str) -> list[tuple[int, str]]:
    """Les lignes de la table des jalons, numerotees (1-based) comme dans le fichier.

    La table est celle qui suit `## État des jalons` : elle commence a la premiere
    ligne qui ouvre sur `|` et finit a la premiere qui ne le fait plus.
    """
    lignes = corps.split("\n")
    depart = next((i for i, x in enumerate(lignes) if x.strip() == TITRE), None)
    if depart is None:
        return []
    dedans = False
    trouvees = []
    for i in range(depart + 1, len(lignes)):
        ligne = lignes[i]
        if ligne.startswith("|"):
            dedans = True
            trouvees.append((i + 1, ligne))
        elif dedans:
            break
        elif ligne.startswith("## "):
            break
    return trouvees


def cellules(ligne: str) -> list[str]:
    parts = ligne.split("|")
    # `| a | b |` se coupe en ['', ' a ', ' b ', ''] : les bords ne comptent pas
    return [c.strip() for c in parts[1:-1]]


def juger(corps: str) -> list[str]:
    """Les reproches, un par ligne fautive. Vide = la table tient."""
    lignes = table(corps)
    if not lignes:
        return [f"{PLAN} : pas de section « {TITRE.lstrip('# ')} », ou pas de table dessous."]

    reproches = []
    numero_entete, entete = lignes[0]
    if entete.strip() != ENTETE:
        reproches.append(
            f"{PLAN}:{numero_entete} : l'en-tête de la table a changé.\n"
            f"  attendu : {ENTETE}\n"
            f"  trouvé  : {entete.strip()}"
        )

    for numero, ligne in lignes[2:]:  # [0] l'en-tete, [1] le separateur
        cols = cellules(ligne)
        jalon = cols[0] if cols else "?"
        if len(cols) != COLONNES:
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » a {len(cols)} colonnes, il en faut {COLONNES}.\n"
                f"  La table est « {ENTETE.strip('|').strip()} ».\n"
                "  Une ligne comme « | Mon jalon | **P2** **correctif**, **en cours** (14 sept.\n"
                "  2026) | … | » est l'ANCIENNE forme : sépare l'état, la date, la prio et le\n"
                "  genre en quatre cellules."
            )
            continue

        _, etat, date, prio, genre, _ = cols

        icone, sans_icone = _icone(etat)
        # le plus long d'abord : « livrée » commence aussi par « livré »
        connu = next(
            (e for e in sorted(ETATS, key=len, reverse=True) if _dedans(sans_icone).startswith(e)),
            None,
        )
        if connu is None:
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » a l'état « {etat} ».\n"
                f"  Les états connus : {', '.join(ETATS)}."
            )
        else:
            attendue = ICONE_LIVRE if connu.startswith("livr") else ICONE_AUTRE
            if icone != attendue:
                manque = "sans son icône" if icone is None else "avec la mauvaise icône"
                reproches.append(
                    f"{PLAN}:{numero} : « {jalon} » a l'état « {etat} », {manque}.\n"
                    f"  {ICONE_LIVRE} devant « livré », {ICONE_AUTRE} devant « en cours » et « à faire » :"
                    f" « {attendue} **{connu}** »."
                )
        if DATE_COLLEE.search(etat):
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » garde sa date dans l'état (« {etat} »).\n"
                "  La date a sa colonne depuis qu'elle est divisée — mets-la là, pas ici."
            )
        if date != "—" and not DATE.match(date):
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » a la date « {date} ».\n"
                "  Il faut « 14 sept. 2026 » (jour, mois abrégé, année) ou « — »."
            )
        if prio != "—" and not PRIO.match(prio):
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » a la prio « {prio} ».\n"
                "  Il faut **P1** à **P4**, ou « — » pour une ligne livrée avant M9."
            )
        if genre != "—" and not GENRE.match(genre):
            reproches.append(
                f"{PLAN}:{numero} : « {jalon} » a le genre « {genre} ».\n"
                "  Il faut « ajout » ou « **correctif** » (le préfixe du commit décide)."
            )

    return reproches


def _racine(depart: Path) -> Path:
    sortie = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=depart,
        capture_output=True,
        text=True,
    )
    return Path(sortie.stdout.strip()) if sortie.returncode == 0 else depart


def _corps_au_commit(racine: Path) -> str | None:
    """Le plan tel qu'il partirait au commit (l'index), ou None s'il n'y est pas."""
    sortie = subprocess.run(
        ["git", "show", f":{PLAN}"],
        cwd=racine,
        capture_output=True,
        text=True,
    )
    return sortie.stdout if sortie.returncode == 0 else None


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--fichier", help="ne juge que si ce fichier est le plan")
    analyseur.add_argument("--commit", action="store_true", help="juge l'index, pas le disque")
    analyseur.add_argument("--cwd", default=".", help="où chercher le dépôt")
    args = analyseur.parse_args()

    racine = _racine(Path(args.cwd).resolve())

    if args.fichier:
        vise = Path(args.fichier).resolve()
        if vise != (racine / PLAN).resolve():
            return 0

    if args.commit:
        corps = _corps_au_commit(racine)
        if corps is None:  # le plan n'est pas dans ce commit : rien a juger
            return 0
    else:
        plan = racine / PLAN
        if not plan.exists():
            return 0
        corps = plan.read_text(encoding="utf-8")

    reproches = juger(corps)
    if not reproches:
        return 0

    print("La table des jalons a perdu sa division :\n", file=sys.stderr)
    for reproche in reproches:
        print(f"  {reproche}\n", file=sys.stderr)
    print(
        "  La légende au-dessus de la table dit ce que chaque colonne porte.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
