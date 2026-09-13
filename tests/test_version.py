"""Le numero de version — celui que le pied de page annonce.

Il ne se tape pas a la main : le crochet `scripts/git-hooks/post-commit` le
pose dans le commit lui-meme, au niveau que le message annonce. Ce fichier
garde les deux moities de cette promesse :

- **le calcul** (quel niveau, quel numero suivant) — des fonctions pures ;
- **la plomberie git**, mesuree dans un VRAI depot temporaire. C'est la moitie
  qui ne se relit pas : un `git add` dans un crochet `commit-msg` a l'air de
  marcher et pose en realite le fichier dans le commit SUIVANT. Rien, dans le
  code, ne montre cette difference — seul un depot d'essai la revele.
"""

import os
import shutil
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import version as v  # noqa: E402

CROCHET = Path(__file__).resolve().parent.parent / "scripts" / "git-hooks" / "post-commit"


# --- Le niveau annonce par le message ---------------------------------------

@pytest.mark.parametrize(
    "message, attendu",
    [
        ("feat: la melodie", v.MINEUR),
        ("feat(menu): une rangee a la fois", v.MINEUR),
        ("fix: une suite se lit d'un trait", v.CORRECTIF),
        ("perf: moins de confettis", v.CORRECTIF),
        ("feat!: le menu change de forme", v.MAJEUR),
        ("feat(menu)!: le menu change de forme", v.MAJEUR),
        ("fix!: la voix ne dit plus les slugs", v.MAJEUR),
        # La rupture peut s'annoncer en pied de message plutot qu'en entete.
        ("feat: nouvel age\n\nBREAKING CHANGE: les etoiles gardees changent de cle", v.MAJEUR),
        # Ce qui ne change rien pour l'enfant ne change rien au numero.
        ("docs: reprise du travail", v.AUCUN),
        ("chore: menage", v.AUCUN),
        ("test: le menu ne se recharge pas", v.AUCUN),
        ("refactor: moteur", v.AUCUN),
        ("style: alignement", v.AUCUN),
        ("ci: navigateur", v.AUCUN),
        # ⚠️ Un message libre ne doit RIEN declencher : c'est ce qui protege les
        # fusions, dont le message n'a jamais de type.
        ("Merge branch 'dev' into main", v.AUCUN),
        ("correction du menu", v.AUCUN),
        ("", v.AUCUN),
    ],
)
def test_le_niveau_se_lit_dans_le_message(message, attendu):
    assert v.niveau_du_message(message) == attendu


# --- Le numero suivant ------------------------------------------------------

@pytest.mark.parametrize(
    "version, niveau, attendu",
    [
        ("1.4.2", v.MINEUR, "1.5.0"),
        ("1.4.2", v.CORRECTIF, "1.4.3"),
        ("1.4.2", v.MAJEUR, "2.0.0"),
        ("1.4.2", v.AUCUN, "1.4.2"),
        # ⚠️ Tant que le majeur vaut 0, une rupture n'avance que le mineur :
        # passer a 1.0.0 est une decision, pas un « ! » dans un message.
        ("0.3.7", v.MAJEUR, "0.4.0"),
        ("0.3.7", v.MINEUR, "0.4.0"),
        ("0.3.7", v.CORRECTIF, "0.3.8"),
    ],
)
def test_le_numero_suivant_remet_a_zero_ce_qui_est_en_dessous(version, niveau, attendu):
    assert v.prochaine(version, niveau) == attendu


# --- Le fichier -------------------------------------------------------------

def test_la_version_lue_est_bien_celle_du_toml(racine):
    """⚠️ Le garde-fou du raccourci.

    `app/version.py` lit `pyproject.toml` a l'expression reguliere, et non
    avec `tomllib` — parce qu'un crochet git n'a pas de Python garanti recent.
    Ce test est ce qui empeche ce raccourci de diverger du vrai TOML.
    """
    attendu = tomllib.loads((racine / "pyproject.toml").read_text(encoding="utf-8"))
    assert v.lire() == attendu["project"]["version"]
    assert v.VERSION == attendu["project"]["version"]


def test_ecrire_ne_touche_qu_a_la_ligne_de_version(racine, tmp_path):
    """Les commentaires du pyproject disent pourquoi les bornes sont ce qu'elles
    sont. Une reecriture du TOML entier les balaierait."""
    copie = tmp_path / "pyproject.toml"
    copie.write_text((racine / "pyproject.toml").read_text(encoding="utf-8"), encoding="utf-8")
    avant = copie.read_text(encoding="utf-8").splitlines()

    v.ecrire("9.8.7", copie)

    apres = copie.read_text(encoding="utf-8").splitlines()
    assert v.lire(copie) == "9.8.7"
    assert len(avant) == len(apres)
    differentes = [(a, b) for a, b in zip(avant, apres) if a != b]
    assert len(differentes) == 1, "une seule ligne devait bouger"
    ancienne, nouvelle = differentes[0]
    assert ancienne.startswith("version = ")
    assert nouvelle == 'version = "9.8.7"'


def test_le_verrou_uv_porte_le_meme_numero_que_le_pyproject(racine):
    """⚠️ Les deux fichiers doivent s'accorder, comme requirements.txt et
    pyproject.toml. Un `uv.lock` en retard n'a l'air de rien : le premier
    `uv run` le corrige tout seul, et ce numero part ensuite dans un commit
    qui n'a rien a voir."""
    verrou = (racine / "uv.lock").read_text(encoding="utf-8")
    nom = tomllib.loads((racine / "pyproject.toml").read_text(encoding="utf-8"))["project"]["name"]
    assert f'name = "{nom}"\nversion = "{v.VERSION}"' in verrou


def test_ecrire_repose_le_verrou_sans_toucher_aux_dependances(racine, tmp_path):
    """Le verrou porte une cinquantaine de lignes `version = ...` — une par
    dependance. Une seule doit bouger."""
    for nom in ("pyproject.toml", "uv.lock"):
        (tmp_path / nom).write_text((racine / nom).read_text(encoding="utf-8"), encoding="utf-8")
    avant = (tmp_path / "uv.lock").read_text(encoding="utf-8").splitlines()

    v.ecrire("9.8.7", tmp_path / "pyproject.toml")

    apres = (tmp_path / "uv.lock").read_text(encoding="utf-8").splitlines()
    differentes = [(a, b) for a, b in zip(avant, apres) if a != b]
    assert differentes == [(f'version = "{v.VERSION}"', 'version = "9.8.7"')]
    # ⚠️ Et le vrai verrou du depot n'a pas bouge : il est cherche a cote du
    # pyproject qu'on lui passe, jamais a la racine du projet.
    assert f'version = "{v.VERSION}"' in (racine / "uv.lock").read_text(encoding="utf-8")


def test_ecrire_refuse_un_fichier_sans_ligne_de_version(tmp_path):
    """Mieux vaut une erreur qu'un fichier repose sans le numero demande."""
    faux = tmp_path / "pyproject.toml"
    faux.write_text("[project]\nname = 'rien'\n", encoding="utf-8")
    with pytest.raises(ValueError):
        v.ecrire("1.0.0", faux)


# --- Le pied de page --------------------------------------------------------

def test_le_pied_de_page_signe_et_date_le_site(client):
    """La version, le concepteur et le droit d'auteur, sur la page du jeu.
    Lus du site, pas recopies ici."""
    page = client.get("/").get_data(as_text=True)
    assert f"v{v.VERSION}" in page
    assert "Martin Gagné" in page
    assert str(date.today().year) in page


# --- La plomberie git -------------------------------------------------------

exige_git = pytest.mark.skipif(shutil.which("git") is None, reason="git absent")


def depot(tmp_path, racine):
    """Un vrai depot git, avec le vrai crochet et un vrai `app/version.py`."""
    (tmp_path / "app").mkdir()
    shutil.copy(racine / "app" / "version.py", tmp_path / "app" / "version.py")
    (tmp_path / "scripts" / "git-hooks").mkdir(parents=True)
    shutil.copy(CROCHET, tmp_path / "scripts" / "git-hooks" / "post-commit")
    os.chmod(tmp_path / "scripts" / "git-hooks" / "post-commit", 0o755)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "essai"\nversion = "0.1.0"\n', encoding="utf-8"
    )
    # Un verrou d'uv comme le vrai : plusieurs paquets, dont le projet.
    (tmp_path / "uv.lock").write_text(
        '[[package]]\nname = "flask"\nversion = "3.1.0"\n\n'
        '[[package]]\nname = "essai"\nversion = "0.1.0"\nsource = { virtual = "." }\n',
        encoding="utf-8",
    )

    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "essai@example.com")
    git(tmp_path, "config", "user.name", "Essai")
    git(tmp_path, "config", "commit.gpgsign", "false")
    git(tmp_path, "config", "core.hooksPath", "scripts/git-hooks")
    git(tmp_path, "add", ".")
    # Le tout premier commit ne passe pas par le crochet : sinon il poserait
    # une version pour l'installation du depot lui-meme.
    git(tmp_path, "commit", "-q", "-m", "chore: depart", crochet=False)
    return tmp_path


def git(depot_path, *arguments, crochet=True):
    environnement = dict(os.environ)
    if not crochet:
        environnement["JEUX_MALINS_VERSION"] = "1"
    resultat = subprocess.run(
        ["git", *arguments],
        cwd=depot_path,
        env=environnement,
        capture_output=True,
        text=True,
    )
    assert resultat.returncode == 0, f"git {' '.join(arguments)} : {resultat.stderr}"
    return resultat.stdout


def commiter(depot_path, message, fichier="jeu.py"):
    (depot_path / fichier).write_text(message, encoding="utf-8")
    git(depot_path, "add", fichier)
    git(depot_path, "commit", "-q", "-m", message)


def version_du_depot(depot_path):
    return v.lire(depot_path / "pyproject.toml")


@exige_git
def test_le_crochet_pose_la_version_dans_le_commit_lui_meme(tmp_path, racine):
    """⚠️ Le coeur de l'affaire. Le numero doit etre DANS le commit, pas dans le
    suivant : c'est exactement la ou un crochet `commit-msg` echoue."""
    d = depot(tmp_path, racine)

    commiter(d, "feat: un nouveau jeu")
    assert version_du_depot(d) == "0.2.0"
    fichiers = git(d, "show", "--format=", "--name-only", "HEAD").split()
    # ⚠️ Le verrou d'uv part DANS le meme commit : laisse en arriere, le premier
    # `uv run` le corrigerait tout seul et salirait l'arbre de travail.
    assert "pyproject.toml" in fichiers and "uv.lock" in fichiers
    verrou = (d / "uv.lock").read_text(encoding="utf-8")
    assert 'name = "essai"\nversion = "0.2.0"' in verrou
    assert 'name = "flask"\nversion = "3.1.0"' in verrou

    commiter(d, "fix: une consigne muette")
    assert version_du_depot(d) == "0.2.1"

    commiter(d, "docs: une note")
    assert version_du_depot(d) == "0.2.1"
    assert "pyproject.toml" not in git(d, "show", "--format=", "--name-only", "HEAD")

    # Le depot reste propre : rien ne traine hors du commit.
    assert git(d, "status", "--porcelain") == ""


@exige_git
def test_un_amend_ne_fait_pas_avancer_la_version_deux_fois(tmp_path, racine):
    """Retoucher un commit n'est pas le refaire — sinon trois `--amend` sur un
    `feat:` feraient trois versions pour un seul changement."""
    d = depot(tmp_path, racine)
    commiter(d, "feat: un nouveau jeu")

    (d / "jeu.py").write_text("retouche", encoding="utf-8")
    git(d, "add", "jeu.py")
    git(d, "commit", "-q", "--amend", "--no-edit")

    assert version_du_depot(d) == "0.2.0"


@exige_git
def test_le_crochet_ne_touche_pas_a_un_pyproject_deja_modifie(tmp_path, racine):
    """Le `--amend --only` prend le fichier tel qu'il est dans l'arbre de
    travail : il emporterait une modification que personne n'a demande de
    commiter."""
    d = depot(tmp_path, racine)
    texte = (d / "pyproject.toml").read_text(encoding="utf-8")
    (d / "pyproject.toml").write_text(texte + '\ndescription = "en cours"\n', encoding="utf-8")

    commiter(d, "feat: un nouveau jeu")

    assert version_du_depot(d) == "0.1.0"
    assert "pyproject.toml" not in git(d, "show", "--format=", "--name-only", "HEAD")
    assert "description" in (d / "pyproject.toml").read_text(encoding="utf-8")


@exige_git
def test_un_commit_partiel_n_emporte_pas_le_reste_de_l_index(tmp_path, racine):
    """`git commit -- un_fichier` laisse le reste prepare dans l'index. Un
    `--amend` sec, lui, l'emporterait tout entier dans le commit."""
    d = depot(tmp_path, racine)
    (d / "a.py").write_text("a", encoding="utf-8")
    (d / "b.py").write_text("b", encoding="utf-8")
    git(d, "add", "a.py", "b.py")

    git(d, "commit", "-q", "-m", "feat: seulement a", "--", "a.py")

    fichiers = git(d, "show", "--format=", "--name-only", "HEAD").split()
    assert sorted(fichiers) == ["a.py", "pyproject.toml", "uv.lock"]
    assert git(d, "status", "--porcelain") == "A  b.py\n"


@exige_git
def test_une_fusion_ne_fait_pas_avancer_la_version(tmp_path, racine):
    """Un commit de fusion n'apporte rien en propre — et les commits fusionnes
    portent deja leur numero.

    ⚠️ Le message dit ici « feat » exprimes : c'est ce qu'ecrivent les gens
    (« feat: integre la branche du menu »), et c'est le seul moyen d'eprouver
    le garde-fou plutot que de le contourner par un message sans type.
    """
    d = depot(tmp_path, racine)
    git(d, "checkout", "-q", "-b", "cote")
    commiter(d, "feat: un jeu de cote")
    apres_branche = version_du_depot(d)

    git(d, "checkout", "-q", "-")
    git(d, "merge", "--no-ff", "--no-commit", "cote")
    git(d, "commit", "-q", "-m", "feat: fusion de la branche cote")

    assert version_du_depot(d) == apres_branche
