#!/usr/bin/env python3
"""La carte du depot — `docs/architecture.md` la porte, ce script verifie qu'elle est a jour.

La carte, c'est trois choses dans `docs/architecture.md` (le plan, lui, ne garde plus que
ce qui reste a faire — fragmente le 20 sept. 2026) : l'**arborescence** (section
« Arborescence du depot », le bloc ``` ), le tableau « Cote Python » (une ligne
par module d'`app/`) et le tableau « Cote JS » (une ligne par script de
`static/js/`). C'est par la qu'une session reprend le travail — et c'est ce
qu'on oublie : le 13 sept. 2026, trois tests, deux scripts et quatre modules
Python existaient sans y etre. Une carte qui ne nomme pas un fichier, c'est
un fichier que la prochaine session ne trouvera pas.

Trois facons de l'appeler :

    verifier_carte_du_depot.py                   # tout le depot (CI, test)
    verifier_carte_du_depot.py --fichier CHEMIN  # ces fichiers (garde a l'ecriture)
    verifier_carte_du_depot.py --commit          # ce que l'index va commiter (garde au commit)

⚠️ Les gardes Claude Code (`.claude/settings.json`) appellent les deux
dernieres : a l'ecriture d'un fichier, puis avant `git commit`. Le test
`tests/test_carte_du_depot.py` appelle la premiere : c'est le dernier filet, en
CI. Les trois passent par les MEMES fonctions — un second detecteur qui
diverge du premier finit par ne plus rien garantir des deux cotes.

Les regles, pour qu'on sache quoi ecrire :

- un fichier suivi par git est sur la carte si son nom apparait dans
  l'arborescence (« tests/  test_x.py » ou « deploy/  nginx/x.conf.example ») ;
- un module `app/x.py` veut EN PLUS sa ligne dans le tableau « Cote Python »
  (`__init__.py` en est dispense) ; un script `static/js/x.js` se declare
  dans le tableau « Cote JS » seulement, l'arborescence renvoie au tableau ;
- un dossier de ressources (`static/audio/`) se couvre d'un seul trait : son
  nom suffit, on ne liste pas 95 mp3 ;
- ce qui est sur la carte et plus dans le depot est perime — sauf un fichier
  **a venir**, qui se note avec son jalon entre parentheses sur la meme ligne
  (« bd.py comptes.py (M14 — …) ») : c'est ce qui l'excuse d'etre absent.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
#: Le document qui porte la carte : « Architecture » (les deux tableaux) et « Arborescence du dépôt ».
PLAN = "docs/architecture.md"

TITRE_ARBORESCENCE = "## Arborescence du dépôt"
TITRE_PYTHON = "### Côté Python"
TITRE_JS = "### Côté JS"

#: Ces dossiers se couvrent d'un seul trait : leur nom dans l'arborescence suffit.
COUVERTS_PAR_DOSSIER = ("static/audio/", "app/missions/", "docs/jalons/")

#: Ce qui, dans l'arborescence, ressemble a un fichier (pour le sens inverse :
#: « encore sur la carte, plus dans le depot »).
EXTENSION = re.compile(
    r"\.(py|js|mjs|cjs|html|md|sh|yml|yaml|css|svg|toml|txt|lock|json|example|conf)$"
)
#: Une ligne qui porte un jalon entre parentheses decrit des fichiers a venir.
A_VENIR = re.compile(r"\(M\d")
PONCTUATION = "(),;:«»`*"


# --- Lire la carte ---------------------------------------------------------------------


def section(texte: str, titre: str) -> str:
    """Le corps d'une section, de son titre au prochain titre de meme niveau ou plus haut."""
    lignes = texte.splitlines()
    niveau = len(titre) - len(titre.lstrip("#"))
    debut = next((i for i, ligne in enumerate(lignes) if ligne.startswith(titre)), None)
    if debut is None:
        return ""
    fin = len(lignes)
    for j in range(debut + 1, len(lignes)):
        ligne = lignes[j]
        if ligne.startswith("#") and len(ligne) - len(ligne.lstrip("#")) <= niveau:
            fin = j
            break
    return "\n".join(lignes[debut + 1 : fin])


def bloc_arborescence(texte: str) -> str:
    """Le bloc ``` de la section « Arborescence » — vide si la section ou le bloc manque."""
    corps = section(texte, TITRE_ARBORESCENCE)
    morceaux = corps.split("```")
    return morceaux[1] if len(morceaux) >= 3 else ""


def jetons(bloc: str) -> set:
    """Les mots du bloc, debarrasses de la ponctuation qui les entoure."""
    return {mot.strip(PONCTUATION) for mot in bloc.split()} - {""}


def jetons_de_fichiers(bloc: str) -> set:
    """Les jetons qui ressemblent a un fichier, hors lignes « a venir »."""
    resultat = set()
    for ligne in bloc.splitlines():
        if A_VENIR.search(ligne):
            continue
        for jeton in jetons(ligne):
            if EXTENSION.search(jeton):
                resultat.add(jeton)
    return resultat


class Carte:
    """La carte telle que le texte de `docs/architecture.md` la porte."""

    def __init__(self, texte: str) -> None:
        self.bloc = bloc_arborescence(texte)
        self.jetons = jetons(self.bloc)
        self.python = section(texte, TITRE_PYTHON)
        self.js = section(texte, TITRE_JS)

    def nomme(self, chemin: str) -> bool:
        base = chemin.rsplit("/", 1)[-1]
        return any(j == base or j.endswith("/" + base) for j in self.jetons)


# --- Juger -------------------------------------------------------------------------------


def _dossier_couvrant(chemin: str) -> str | None:
    return next((d for d in COUVERTS_PAR_DOSSIER if chemin.startswith(d)), None)


def problemes_du_fichier(chemin: str, carte: Carte) -> list:
    """Ce qui manque a la carte pour ce fichier — vide s'il y est."""
    if not carte.bloc:
        return [f"{chemin} : la section « {TITRE_ARBORESCENCE[3:]} » de {PLAN} est introuvable"]
    base = chemin.rsplit("/", 1)[-1]
    dossier = _dossier_couvrant(chemin)
    if dossier:
        if dossier in carte.jetons:
            return []
        return [f"{dossier} : le dossier n'est pas dans l'arborescence"]

    problemes = []
    if chemin.startswith("static/js/") and chemin.endswith(".js"):
        if f"`{base}`" not in carte.js:
            problemes.append(f"{chemin} : sans ligne dans le tableau « {TITRE_JS[4:]} »")
        return problemes

    if not carte.nomme(chemin):
        problemes.append(f"{chemin} : absent de l'arborescence")
    if chemin.startswith("app/") and chemin.endswith(".py") and base != "__init__.py":
        if f"`{base}`" not in carte.python:
            problemes.append(f"{chemin} : sans ligne dans le tableau « {TITRE_PYTHON[4:]} »")
    return problemes


def perimes(fichiers: list, carte: Carte) -> list:
    """Les noms de l'arborescence qui ne correspondent plus a aucun fichier."""
    bases = {f.rsplit("/", 1)[-1] for f in fichiers}
    return sorted(
        j for j in jetons_de_fichiers(carte.bloc) if j.rsplit("/", 1)[-1] not in bases
    )


def verifier(
    fichiers: list, texte_plan: str, *, inverse: bool = True, presents: list | None = None
) -> list:
    """Tous les ecarts entre ces fichiers et cette carte, dans un ordre stable.

    `fichiers` doivent etre sur la carte ; le sens inverse (perime) se juge
    contre `presents` — par defaut les memes, mais le depot reel passe aussi
    les fichiers pas encore suivis : un test qu'on vient d'ecrire et de porter
    sur la carte n'est pas perime parce que `git add` n'est pas encore fait.
    """
    carte = Carte(texte_plan)
    problemes = []
    dossiers_vus = set()
    for chemin in sorted(fichiers):
        dossier = _dossier_couvrant(chemin)
        if dossier:
            if dossier in dossiers_vus:
                continue
            dossiers_vus.add(dossier)
        problemes.extend(problemes_du_fichier(chemin, carte))
    if inverse:
        for jeton in perimes(fichiers if presents is None else presents, carte):
            problemes.append(f"encore sur la carte, plus dans le dépôt : {jeton}")
    return problemes


# --- Git ---------------------------------------------------------------------------------


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(RACINE), *args], capture_output=True, text=True, check=True
    ).stdout


def fichiers_suivis() -> list:
    """Ce que git suit (index compris) : c'est ca qui doit etre sur la carte."""
    return [ligne for ligne in _git("ls-files").splitlines() if ligne]


def fichiers_presents() -> list:
    """Suivis ET pas encore suivis (hors ignores) : ce qui existe vraiment dans l'arbre."""
    sortie = _git("ls-files", "--cached", "--others", "--exclude-standard")
    return [ligne for ligne in sortie.splitlines() if ligne]


def index_du_commit() -> list:
    """(statut, chemin) de ce que `git commit` emporterait : A, M, D, R…"""
    resultat = []
    for ligne in _git("diff", "--cached", "--name-status", "-M").splitlines():
        if not ligne:
            continue
        morceaux = ligne.split("\t")
        statut, chemin = morceaux[0][0], morceaux[-1]
        resultat.append((statut, chemin))
    return resultat


def plan_dans_index() -> str:
    """Le plan tel qu'il partira dans le commit (l'index, qui vaut HEAD s'il n'a pas bouge)."""
    try:
        return _git("show", f":{PLAN}")
    except subprocess.CalledProcessError:
        return ""


def plan_dans_l_arbre() -> str:
    chemin = RACINE / PLAN
    return chemin.read_text(encoding="utf-8") if chemin.exists() else ""


# --- Les trois entrees -------------------------------------------------------------------


def verifier_tout() -> list:
    """Tout le depot contre le plan de l'arbre de travail (le test, la CI)."""
    return verifier(fichiers_suivis(), plan_dans_l_arbre(), presents=fichiers_presents())


def verifier_fichiers(chemins: list) -> list:
    """Ces fichiers-la contre le plan de l'arbre de travail (la garde a l'ecriture).

    Toucher au plan lui-meme revient a verifier tout : on vient de redessiner
    la carte, on veut savoir ce qui y manque encore.
    """
    relatifs = []
    for chemin in chemins:
        p = Path(chemin)
        if p.is_absolute():
            try:
                p = p.resolve().relative_to(RACINE)
            except ValueError:
                continue  # hors du depot : pas notre affaire
        relatifs.append(p.as_posix())
    if PLAN in relatifs:
        return verifier_tout()
    texte = plan_dans_l_arbre()
    return verifier([r for r in relatifs if r != PLAN], texte, inverse=False)


def verifier_commit() -> list:
    """L'index contre le plan de l'index (la garde avant `git commit`).

    ⚠️ C'est la version INDEXEE du plan qui compte : celle de l'arbre de travail
    peut nommer le fichier sans partir dans le commit. Quand c'est le cas, on le
    dit, et le remede tient en un `git add docs/architecture.md`.
    """
    index = index_du_commit()
    if not index:
        return []
    ajoutes = [c for s, c in index if s in "AMR"]
    retires = [c for s, c in index if s == "D"]
    texte_index = plan_dans_index()
    problemes = verifier(ajoutes, texte_index, inverse=False)
    carte_index = Carte(texte_index)
    for chemin in retires:
        if carte_index.nomme(chemin):
            problemes.append(f"encore sur la carte, plus dans le dépôt : {chemin}")
    if problemes and (RACINE / PLAN).exists():
        texte_arbre = plan_dans_l_arbre()
        carte_arbre = Carte(texte_arbre)
        deja_dans_l_arbre = not verifier(ajoutes, texte_arbre, inverse=False) and not any(
            carte_arbre.nomme(c) for c in retires
        )
        if deja_dans_l_arbre and texte_arbre != texte_index:
            problemes.append(
                f"{PLAN} les nomme dans l'arbre de travail mais pas dans l'index : "
                f"`git add {PLAN}` pour que la carte parte avec ce commit"
            )
    return problemes


def main(argv: list | None = None) -> int:
    parseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    groupe = parseur.add_mutually_exclusive_group()
    groupe.add_argument("--fichier", nargs="+", metavar="CHEMIN", help="ces fichiers seulement")
    groupe.add_argument("--commit", action="store_true", help="ce que l'index va commiter")
    parseur.add_argument("--cwd", default=None, help="d'ou la commande part (garde au commit)")
    args = parseur.parse_args(argv)

    if args.cwd:
        try:
            Path(args.cwd).resolve().relative_to(RACINE)
        except ValueError:
            return 0  # un commit dans un autre depot : pas notre carte

    if args.fichier:
        problemes = verifier_fichiers(args.fichier)
    elif args.commit:
        problemes = verifier_commit()
    else:
        problemes = verifier_tout()

    if problemes:
        print(f"La carte du dépôt ({PLAN}) n'est pas à jour :", file=sys.stderr)
        for probleme in problemes:
            print(f"  - {probleme}", file=sys.stderr)
        print(
            f"Mets-la à jour dans {PLAN} — « Arborescence du dépôt » pour un fichier, "
            "le tableau « Côté Python » ou « Côté JS » pour un module ; un fichier à venir "
            "se note avec son jalon entre parenthèses sur la même ligne.",
            file=sys.stderr,
        )
        return 1

    if not args.fichier and not args.commit:
        print(f"{len(fichiers_suivis())} fichiers suivis, tous sur la carte.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
