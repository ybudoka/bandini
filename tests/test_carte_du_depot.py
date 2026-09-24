"""La carte du depot — `docs/architecture.md` nomme chaque fichier, ou la prochaine session ne le trouve pas.

Le detecteur vit dans `scripts/verifier_carte_du_depot.py` : les gardes Claude
Code (`.claude/settings.json`) l'appellent a l'ecriture d'un fichier et avant
`git commit`, ce test l'appelle sur tout le depot — c'est le dernier filet, en
CI. Un seul detecteur pour les trois : un second qui divergerait du premier
finirait par laisser passer ce que l'autre refuse.

Le premier juge lit le VRAI plan et les VRAIS fichiers suivis par git. Les
autres jugent le detecteur lui-meme, sur un petit plan d'essai — parce qu'un
juge qui passe parce que le detecteur ne detecte rien serait pire qu'aucun.
"""

import importlib.util
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPT = RACINE / "scripts" / "verifier_carte_du_depot.py"


def _charger():
    spec = importlib.util.spec_from_file_location("verifier_carte_du_depot", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


carte = _charger()

PLAN_D_ESSAI = """# Plan

## Architecture

### Côté Python (`app/`)

| Module | Contenu | Tests |
|---|---|---|
| `carte.py` | la ville | `test_carte.py` |

### Côté JS (`static/js/`)

| # | Fichier | Rôle |
|---|---|---|
| 1 | `base.js` | le socle |

## Arborescence du dépôt

```
run.py  pyproject.toml (name bandini)
app/  __init__.py carte.py
      bd.py (M14 — à venir)
static/audio/  (les mp3)
static/js/ (voir le tableau ci-dessus)
tests/  test_carte.py
```

## Jalons
"""

FICHIERS = [
    "run.py",
    "pyproject.toml",
    "app/__init__.py",
    "app/carte.py",
    "static/audio/coup.mp3",
    "static/js/base.js",
    "tests/test_carte.py",
]


def test_la_carte_du_depot_est_a_jour():
    """Le vrai plan contre les vrais fichiers suivis : ce qui manque est nomme."""
    problemes = carte.verifier_tout()
    assert problemes == [], "\n".join(problemes)


def test_une_carte_a_jour_ne_dit_rien():
    assert carte.verifier(FICHIERS, PLAN_D_ESSAI) == []


def test_un_fichier_neuf_hors_carte_se_voit():
    problemes = carte.verifier(FICHIERS + ["tests/test_neuf.py"], PLAN_D_ESSAI)
    assert problemes == ["tests/test_neuf.py : absent de l'arborescence"]


def test_un_module_python_veut_aussi_sa_ligne_au_tableau():
    plan = PLAN_D_ESSAI.replace(
        "app/  __init__.py carte.py", "app/  __init__.py carte.py journal.py"
    )
    problemes = carte.verifier(FICHIERS + ["app/journal.py"], plan)
    assert problemes == ["app/journal.py : sans ligne dans le tableau « Côté Python »"]


def test_un_script_js_se_declare_au_tableau_seulement():
    problemes = carte.verifier(FICHIERS + ["static/js/hud.js"], PLAN_D_ESSAI)
    assert problemes == ["static/js/hud.js : sans ligne dans le tableau « Côté JS »"]
    plan = PLAN_D_ESSAI.replace(
        "| 1 | `base.js` | le socle |", "| 1 | `base.js` | le socle |\n| 2 | `hud.js` | le HUD |"
    )
    assert carte.verifier(FICHIERS + ["static/js/hud.js"], plan) == []


def test_le_dossier_audio_se_couvre_d_un_seul_trait():
    fichiers = FICHIERS + ["static/audio/pas.mp3", "static/audio/voix/ti_guy-m1-1.mp3"]
    assert carte.verifier(fichiers, PLAN_D_ESSAI) == []
    plan = PLAN_D_ESSAI.replace("static/audio/  (les mp3)\n", "")
    assert carte.verifier(fichiers, plan) == [
        "static/audio/ : le dossier n'est pas dans l'arborescence"
    ]


def test_un_fichier_disparu_est_perime_sauf_s_il_est_a_venir():
    sans_run = [f for f in FICHIERS if f != "run.py"]
    assert carte.verifier(sans_run, PLAN_D_ESSAI) == [
        "encore sur la carte, plus dans le dépôt : run.py"
    ]
    # bd.py est sur la ligne « (M14 — à venir) » : il n'existe pas encore, et c'est dit.
    assert "bd.py" not in " ".join(carte.verifier(FICHIERS, PLAN_D_ESSAI))


def test_sans_section_arborescence_la_carte_le_dit():
    problemes = carte.verifier(["run.py"], "# Plan\n\nrien\n")
    assert problemes and "introuvable" in problemes[0]
