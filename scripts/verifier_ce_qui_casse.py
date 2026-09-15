#!/usr/bin/env python3
"""Ce qui casse — un decor destructible sur la fiche doit l'etre DANS LE JEU.

La fiche d'un decor (`DECORS`, dans `static/js/sprites.js`) dit ce qu'on peut
lui faire. Trois mots, et ils se tiennent :

    `arrete: n`  il ARRETE un char sous la masse `n` — un arbre, une fontaine,
                 un camion-restaurant. Il encaisse les balles, il ne tombe
                 JAMAIS : c'est ce qui fait un abri dans une fusillade.
    `casse: f`   il CEDE sous un char lance, qui garde la fraction `f` de sa
                 vitesse — un banc, une poubelle, un lampadaire.
    `pv: n`      ce qu'il faut lui mettre a l'ARME pour l'abattre : balles,
                 explosion, feu.

⚠️ **Pourquoi ce juge existe.** Jusqu'au 15 sept. 2026, `Entites.briser` n'avait
qu'UN SEUL appelant — le char lance (`Vehicules.heurterDecor`). Les balles
traversaient le decor sans le voir (`majProjectiles` ne s'arretait que sur une
facade), l'explosion d'un char ne filtrait que `q.vivant` — ce que le decor
n'est pas — et le brasier d'un molotov non plus. On vidait un chargeur dans un
lampadaire et il ne bronchait pas. Rien ne rougissait : la fiche disait
« casse », et personne ne verifiait que quelqu'un s'en servait.

⚠️ Et l'autre moitie, plus sournoise : un `buisson` et une `corde_a_linge`
declaraient `casse` avec `solide: false`. L'index du decor ne prenait QUE le
solide, et c'est dans cet index que le char cherche ce qu'il renverse. Deux
fiches qui se disaient destructibles depuis toujours, et que rien au monde ne
pouvait toucher. Une fiche n'est pas une garantie — ce juge en fait une.

Ce qu'il exige, du catalogue :

1. une fiche `solide: true` declare `arrete` ou `casse` — sinon elle est
   FANTOME pour les chars : l'autobus la traverse sans ralentir ;
2. `casse` et `pv` vont ensemble, dans les deux sens — ce qui tombe sous un
   char tombe sous une arme, et rien ne s'use a l'arme sans ceder au char ;
3. `arrete` n'a jamais de `pv` — il encaisse, il ne tombe pas ;
4. jamais `arrete` ET `casse` sur la meme fiche : on ne saurait pas laquelle
   gagne.

Et du cablage, parce qu'une fiche sans appelant ne vaut rien :

5. `Entites.endommagerDecor` existe et s'exporte ;
6. les trois armes s'en servent — la balle et le feu (`combat.js`), l'explosion
   (`vehicules.js`) ;
7. le char garde le sien : `Entites.briser` reste appele depuis `vehicules.js`.

Trois facons de l'appeler, comme ses voisins `verifier_carte_du_depot.py` et
`verifier_table_des_jalons.py` :

    python scripts/verifier_ce_qui_casse.py              # le depot
    python scripts/verifier_ce_qui_casse.py --fichier F  # ne dit rien si F n'est pas en cause
    python scripts/verifier_ce_qui_casse.py --commit     # ce que l'index va commiter
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SPRITES = "static/js/sprites.js"
ENTITES = "static/js/entites.js"
COMBAT = "static/js/combat.js"
VEHICULES = "static/js/vehicules.js"

#: Ecrire dans l'un de ces quatre fichiers peut casser l'invariant ; ailleurs,
#: le juge se tait.
SURVEILLES = (SPRITES, ENTITES, COMBAT, VEHICULES)

#: Les fiches qui ne sont pas du mobilier : un effet, un rendu, un objet de
#: mission. Elles n'ont ni a arreter un char ni a tomber sous une balle.
#: ⚠️ Tenir cette liste COURTE. Chaque nom qu'on y pose est un decor de plus
#: que personne ne pourra jamais casser — c'est exactement la panne qu'on juge.
HORS_MOBILIER = {
    "debris",     # ce qui RESTE d'un decor casse
    "ombre",      # pose sous les entites
    "remous",     # l'eau qui bouge
    "paquet",     # une livraison, pas un meuble
    "affiche",    # peinte sur un mur
}


# --- Lire le catalogue ------------------------------------------------------


def _sans_bruit(texte: str) -> str:
    """Le meme texte, chaines et commentaires remplaces par des blancs.

    ⚠️ On remplace au lieu de supprimer : les positions ne bougent pas, donc on
    peut decouper le texte D'ORIGINE avec les indices trouves ici. Un `{` dans
    une chaine de peintre (`'#3a3d44'`) ne doit pas compter comme une accolade,
    et un `}` en commentaire non plus.
    """
    sortie = list(texte)
    i, n = 0, len(texte)
    while i < n:
        c = texte[i]
        if c in "'\"`":
            j = i + 1
            while j < n:
                if texte[j] == "\\":
                    j += 2
                    continue
                if texte[j] == c:
                    break
                j += 1
            for k in range(i, min(j + 1, n)):
                if sortie[k] != "\n":
                    sortie[k] = " "
            i = j + 1
            continue
        if c == "/" and i + 1 < n and texte[i + 1] == "/":
            j = texte.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                sortie[k] = " "
            i = j
            continue
        if c == "/" and i + 1 < n and texte[i + 1] == "*":
            j = texte.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if sortie[k] != "\n":
                    sortie[k] = " "
            i = j
            continue
        i += 1
    return "".join(sortie)


def _corps_de_l_objet(texte: str, depart: int) -> tuple[int, int]:
    """Les bornes de l'objet dont l'accolade ouvrante est a `depart`."""
    profondeur = 0
    for i in range(depart, len(texte)):
        if texte[i] in "{[(":
            profondeur += 1
        elif texte[i] in "}])":
            profondeur -= 1
            if profondeur == 0:
                return depart + 1, i
    raise ValueError("accolade jamais refermee")


CLE = re.compile(r"([A-Za-z_$][\w$]*)\s*:")


def _paires(propre: str, brut: str, debut: int, fin: int) -> dict[str, str]:
    """Les `cle: valeur` du PREMIER niveau de l'objet `[debut, fin)`."""
    paires: dict[str, str] = {}
    profondeur = 0
    i = debut
    while i < fin:
        c = propre[i]
        if c in "{[(":
            profondeur += 1
            i += 1
            continue
        if c in "}])":
            profondeur -= 1
            i += 1
            continue
        if profondeur == 0:
            m = CLE.match(propre, i)
            if m:
                j = m.end()
                niveau = 0
                while j < fin:
                    d = propre[j]
                    if d in "{[(":
                        niveau += 1
                    elif d in "}])":
                        if niveau == 0:
                            break
                        niveau -= 1
                    elif d == "," and niveau == 0:
                        break
                    j += 1
                paires[m.group(1)] = brut[m.end():j].strip()
                i = j
                continue
        i += 1
    return paires


def fiches(source: str) -> dict[str, dict[str, str]]:
    """Le catalogue `DECORS` tel qu'il est ecrit : nom -> { cle: valeur brute }."""
    propre = _sans_bruit(source)
    m = re.search(r"\bconst\s+DECORS\s*=\s*\{", propre)
    if not m:
        return {}
    debut, fin = _corps_de_l_objet(propre, m.end() - 1)
    catalogue: dict[str, dict[str, str]] = {}
    for nom, valeur in _paires(propre, source, debut, fin).items():
        if valeur.startswith("{"):
            interieur = propre.find(valeur[:1], source.find(valeur, debut))
            d, f = _corps_de_l_objet(propre, interieur)
            catalogue[nom] = _paires(propre, source, d, f)
    return catalogue


def _nombre(valeur: str | None) -> float | None:
    if valeur is None:
        return None
    try:
        return float(valeur)
    except ValueError:
        return None


# --- Juger ------------------------------------------------------------------


def juger_le_catalogue(source: str) -> list[str]:
    reproches = []
    catalogue = fiches(source)
    if not catalogue:
        return [
            f"{SPRITES} : impossible de lire `const DECORS = {{ … }}`.\n"
            "  Le juge ne sait plus ou regarder — a-t-il ete renomme ou deplacé ?"
        ]

    for nom, fiche in sorted(catalogue.items()):
        if nom in HORS_MOBILIER:
            continue
        arrete = _nombre(fiche.get("arrete"))
        casse = _nombre(fiche.get("casse"))
        pv = _nombre(fiche.get("pv"))
        solide = fiche.get("solide", "false").strip() == "true"

        if arrete is not None and casse is not None:
            reproches.append(
                f"{SPRITES} : `DECORS.{nom}` porte `arrete` ET `casse`.\n"
                "  On ne saurait pas lequel gagne quand un char arrive. Un seul des deux."
            )
        elif arrete is None and casse is None and solide:
            reproches.append(
                f"{SPRITES} : `DECORS.{nom}` est `solide: true` mais ne déclare ni `arrete` ni `casse`.\n"
                "  Il est FANTÔME pour les chars : l'autobus le traverse sans ralentir, et rien\n"
                "  ne le renverse jamais. Un décor solide arrête (`arrete: masse`) ou cède\n"
                "  (`casse: fraction` + `pv`)."
            )

        if casse is not None and pv is None:
            reproches.append(
                f"{SPRITES} : `DECORS.{nom}` cède sous un char (`casse`) mais n'a pas de `pv`.\n"
                "  Aucune arme ne peut donc l'abattre : on lui vide un chargeur dessus et il\n"
                "  ne bronche pas. L'échelle se lit en balles de pistolet (30 points)."
            )
        if pv is not None and casse is None:
            reproches.append(
                f"{SPRITES} : `DECORS.{nom}` a des `pv` mais pas de `casse`.\n"
                "  Il tomberait à l'arme et résisterait à un camion lancé — c'est l'inverse\n"
                "  du bon sens. `pv` accompagne `casse`, jamais seul."
            )
        if pv is not None and arrete is not None:
            reproches.append(
                f"{SPRITES} : `DECORS.{nom}` porte `arrete` ET `pv`.\n"
                "  Ce qui arrête un char ENCAISSE : il ne tombe jamais. Sinon la rue se\n"
                "  démonte au pistolet et il ne reste plus un seul abri."
            )
        if pv is not None and pv <= 0:
            reproches.append(
                f"{SPRITES} : `DECORS.{nom}` a `pv: {fiche.get('pv')}`.\n"
                "  Zéro point de vie, c'est un décor qui tombe avant d'être touché."
            )

    return reproches


#: Le cablage : ce qui doit appeler quoi, et la phrase qui dit pourquoi.
CABLAGE = (
    (
        ENTITES,
        r"function\s+endommagerDecor\s*\(",
        "`Entites.endommagerDecor` n'existe plus.",
        "C'est le seul chemin d'une arme vers le décor. Sans lui, la fiche `pv` ne veut\n"
        "  plus rien dire et on revient au lampadaire qui encaisse un chargeur.",
    ),
    (
        ENTITES,
        r"\bendommagerDecor\s*,",
        "`endommagerDecor` n'est plus exporté par `Entites`.",
        "Il est déclaré mais personne hors du module ne peut l'appeler.",
    ),
    (
        COMBAT,
        r"Entites\.endommagerDecor\s*\(",
        "Aucune arme ne mord le décor dans `combat.js`.",
        "La balle (`mordreLeDecor`) et le feu (`majBrasiers`) doivent l'appeler : sans ça,\n"
        "  un projectile retraverse le mobilier urbain comme avant le 15 sept. 2026.",
    ),
    (
        VEHICULES,
        r"Entites\.endommagerDecor\s*\(",
        "L'explosion n'emporte plus le décor dans `vehicules.js`.",
        "`Entites.autour(…, q.vivant)` ne voit pas le décor : il faut la boucle sur\n"
        "  `decorAutour` dans `exploser`, sinon le lampadaire reste debout dans le cratère.",
    ),
    (
        VEHICULES,
        r"Entites\.briser\s*\(",
        "Le char ne casse plus le décor (`Entites.briser` dans `vehicules.js`).",
        "C'est le chemin d'origine — `heurterDecor`. Les `casse` des fiches en dépendent.",
    ),
)


def juger_le_cablage(sources: dict[str, str]) -> list[str]:
    reproches = []
    for fichier, motif, quoi, pourquoi in CABLAGE:
        source = sources.get(fichier)
        if source is None:
            continue
        if not re.search(motif, source):
            reproches.append(f"{fichier} : {quoi}\n  {pourquoi}")
    return reproches


def juger(sources: dict[str, str]) -> list[str]:
    reproches = []
    if SPRITES in sources:
        reproches += juger_le_catalogue(sources[SPRITES])
    reproches += juger_le_cablage(sources)
    return reproches


# --- Lire le depot ----------------------------------------------------------


def _racine(depart: Path) -> Path:
    sortie = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=depart,
        capture_output=True,
        text=True,
    )
    return Path(sortie.stdout.strip()) if sortie.returncode == 0 else depart


def _au_commit(racine: Path, chemin: str) -> str | None:
    """Le fichier tel qu'il partirait au commit (l'index), ou None s'il n'y est pas."""
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
    analyseur.add_argument("--cwd", default=".", help="où chercher le dépôt")
    args = analyseur.parse_args()

    racine = _racine(Path(args.cwd).resolve())

    if args.fichier:
        vise = Path(args.fichier).resolve()
        if not any(vise == (racine / chemin).resolve() for chemin in SURVEILLES):
            return 0

    reproches = juger(sources(racine, args.commit))
    if not reproches:
        return 0

    print("Un décor se dit destructible et ne l'est pas :\n", file=sys.stderr)
    for reproche in reproches:
        print(f"  {reproche}\n", file=sys.stderr)
    print(
        "  La légende au-dessus de `const DECORS` dit ce que `arrete`, `casse` et `pv`\n"
        "  portent chacun, et pourquoi ils vont par paires.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
