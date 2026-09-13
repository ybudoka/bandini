"""La version du site — un seul numero, une seule ligne.

Elle vit dans `pyproject.toml` (`[project] version`) et nulle part ailleurs.
C'est le seul fichier qui remplisse les deux conditions : il est **deja** la
reference du paquet, et le deploiement l'embarque (`git archive HEAD`), donc
le serveur peut le lire sans avoir le depot git sous la main.

Ce module tient les deux bouts du meme numero :

- **le site le lit** au demarrage (`VERSION`) pour le poser en pied de page ;
- **le commit le pose**, via `scripts/git-hooks/post-commit`, qui execute ce
  fichier (`python3 app/version.py --appliquer`).

⚠️ **Le niveau ne se choisit pas a la main, il se DEDUIT du message de
commit** — qui suit deja Conventional Commits (`feat:`, `fix:`, `feat!:`).
C'est la meme raison qui fait nommer le cache hors-ligne par une empreinte du
contenu plutot que par un numero : un numero qu'on incremente a la main est un
numero qu'on oublie, et il ment ensuite sans que rien ne le signale.

⚠️ **Aucune dependance, et pas meme `tomllib`** : ce fichier est aussi execute
par un crochet git, qui n'a aucun environnement garanti — ni le venv du projet,
ni un `python3` recent (celui de macOS est en 3.9, sans `tomllib`). D'ou la
lecture par expression reguliere ; `tests/test_version.py` la compare a ce que
`tomllib` lit vraiment, sinon ce raccourci divergerait en silence.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PYPROJET = RACINE / "pyproject.toml"

#: `version = "1.2.3"`, la ligne entiere. L'ancre de debut de ligne suffit a
#: epargner `target-version` et `requires-python`, qui ne commencent pas par
#: « version ».
_LIGNE = re.compile(r'^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"[ \t]*$', re.MULTILINE)

#: `name = "jeux-educatifs"` — la premiere du fichier, celle du `[project]`.
_NOM = re.compile(r'^name\s*=\s*"([^"]+)"[ \t]*$', re.MULTILINE)

#: L'entete d'un commit conventionnel : `type(portee)!: sujet`.
_ENTETE = re.compile(r"^(?P<type>[a-z]+)(?:\([^)]*\))?(?P<rupture>!)?:")

#: La rupture peut aussi s'annoncer en pied de message (Conventional Commits).
_RUPTURE = re.compile(r"^BREAKING[ -]CHANGE\s*:", re.MULTILINE)

MAJEUR = "majeur"
MINEUR = "mineur"
CORRECTIF = "correctif"
AUCUN = "aucun"

#: Type de commit -> niveau. ⚠️ Ce qui n'est PAS dans cette table ne touche pas
#: au numero : `docs:`, `chore:`, `test:`, `style:`, `ci:`, `build:`,
#: `refactor:`. Une version qui avance pour une virgule dans un README ne veut
#: plus rien dire — or elle sert justement a repondre « qu'est-ce qui tourne
#: en ligne ? ».
NIVEAUX = {
    "feat": MINEUR,
    "fix": CORRECTIF,
    "perf": CORRECTIF,
}


def niveau_du_message(message: str) -> str:
    """Le niveau annonce par un message de commit — `majeur`, `mineur`... ."""
    lignes = message.strip().splitlines()
    if not lignes:
        return AUCUN

    trouve = _ENTETE.match(lignes[0])
    if not trouve:
        # « Merge branch... », un message libre : rien d'annonce, rien de pose.
        return AUCUN

    if trouve.group("rupture") or _RUPTURE.search(message):
        return MAJEUR

    return NIVEAUX.get(trouve.group("type"), AUCUN)


def prochaine(version: str, niveau: str) -> str:
    """Le numero suivant. Rend le meme si le niveau ne demande rien."""
    majeur, mineur, correctif = (int(nombre) for nombre in version.split("."))

    if niveau == MAJEUR:
        # ⚠️ Tant que le majeur vaut 0, une rupture n'avance que le mineur
        # (semver §4) : passer a 1.0.0 veut dire « le site est stable », et
        # c'est une decision qui se prend — pas un « ! » tape dans un message
        # un mardi soir. Le jour venu, on ecrit 1.0.0 a la main dans
        # pyproject.toml et la regle s'efface d'elle-meme.
        if majeur == 0:
            return f"0.{mineur + 1}.0"
        return f"{majeur + 1}.0.0"

    if niveau == MINEUR:
        return f"{majeur}.{mineur + 1}.0"

    if niveau == CORRECTIF:
        return f"{majeur}.{mineur}.{correctif + 1}"

    return version


def lire(chemin: Path = PYPROJET) -> str:
    """Le numero ecrit dans `pyproject.toml`."""
    trouve = _LIGNE.search(chemin.read_text(encoding="utf-8"))
    if not trouve:
        raise ValueError(f'aucune ligne « version = "x.y.z" » dans {chemin}')
    return ".".join(trouve.groups())


def ecrire(version: str, chemin: Path = PYPROJET) -> None:
    """Repose le numero — et rien d'autre des fichiers ne bouge.

    Une reecriture du TOML entier (lecture puis serialisation) reformaterait
    les commentaires et l'ordre des tables : ce fichier en est plein, et ils
    disent pourquoi les bornes sont ce qu'elles sont.

    ⚠️ **Le verrou d'uv porte le meme numero** et se repose donc en meme temps.
    Sans lui, chaque commit laisserait un `uv.lock` perime : le premier `uv
    run` venu le corrigerait tout seul, salissant l'arbre de travail sans
    raison visible — et ce numero-la finirait dans un commit qui n'a rien a
    voir. Le verrou est cherche **a cote du pyproject** et non a la racine du
    projet : sinon un appel sur une copie temporaire reecrirait le vrai.

    ⚠️ Les deux substitutions sont faites AVANT la premiere ecriture : si la
    seconde echouait, le pyproject serait deja repose et les deux fichiers se
    contrediraient — exactement ce que cette fonction existe pour eviter.
    """
    texte = chemin.read_text(encoding="utf-8")
    nouveau, remplacees = _LIGNE.subn(f'version = "{version}"', texte, count=1)
    if remplacees != 1:
        raise ValueError(f'aucune ligne « version = "x.y.z" » dans {chemin}')

    a_ecrire = {chemin: nouveau}

    verrou = chemin.parent / "uv.lock"
    if verrou.exists():
        a_ecrire[verrou] = _verrou_repose(verrou, _nom_du_projet(texte), version)

    for fichier, contenu in a_ecrire.items():
        fichier.write_text(contenu, encoding="utf-8")


def _nom_du_projet(texte_pyprojet: str) -> str:
    trouve = _NOM.search(texte_pyprojet)
    if not trouve:
        raise ValueError('aucune ligne « name = "..." » dans le pyproject')
    return trouve.group(1)


def _verrou_repose(verrou: Path, nom: str, version: str) -> str:
    """Le `uv.lock`, numero du projet remis a jour.

    ⚠️ Le fichier porte une cinquantaine de lignes `version = ...`, une par
    dependance : seule celle qui SUIT `name = "<le projet>"` nous regarde.
    D'ou l'ancrage sur les deux lignes ensemble.
    """
    texte = verrou.read_text(encoding="utf-8")
    cible = re.compile(
        r'^(name = "' + re.escape(nom) + r'"\nversion = ")\d+\.\d+\.\d+(")',
        re.MULTILINE,
    )
    nouveau, remplacees = cible.subn(rf"\g<1>{version}\g<2>", texte, count=1)
    if remplacees != 1:
        raise ValueError(f"aucun bloc « {nom} » dans {verrou}")
    return nouveau


def appliquer(message: str, chemin: Path = PYPROJET) -> str:
    """Pose le numero qu'annonce ce message. Rend "" si rien ne bouge."""
    ancienne = lire(chemin)
    nouvelle = prochaine(ancienne, niveau_du_message(message))
    if nouvelle == ancienne:
        return ""
    ecrire(nouvelle, chemin)
    return nouvelle


#: Lu UNE fois au demarrage : le fichier ne change plus sous un processus deja
#: lance, et chaque requete qui le relirait paierait un acces disque pour un
#: numero qui ne bouge pas.
VERSION = lire()


if __name__ == "__main__":
    # Appele par le crochet git. Le message arrive sur l'entree standard : le
    # passer en argument obligerait le crochet a le mettre entre guillemets, et
    # un message de commit contient tout ce qu'un shell interprete.
    if "--appliquer" in sys.argv[1:]:
        pose = appliquer(sys.stdin.read())
        if pose:
            print(pose)
    else:
        print(VERSION)
