"""L'inventaire de la carte — `docs/carte.md` cite tout slug du code, ou il ment.

Le detecteur vit dans `scripts/verifier_carte_du_plan.py`. Ce test l'appelle
sur le VRAI depot : c'est le dernier filet, en CI — un bâtiment, une gang, un
vehicule ou un pieton ajoute au code sans sa ligne dans l'inventaire fait
echouer la suite. Les autres juges du fichier verifient le detecteur lui-meme
sur un petit depot d'essai, parce qu'un juge qui passe parce que le detecteur
ne detecte rien serait pire qu'aucun.
"""

import importlib.util
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPT = RACINE / "scripts" / "verifier_carte_du_plan.py"


def _charger():
    spec = importlib.util.spec_from_file_location("verifier_carte_du_plan", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


juge = _charger()


def test_le_depot_reel_est_a_jour():
    """Le vrai depot : docs/carte.md tient le suivi du code, à ce commit-ci."""
    sources = juge.sources(RACINE, commit=False)
    reproches = juge.juger(sources)
    assert not reproches, "\n".join(reproches)


# --- Le juge lui-même, sur un dépôt d'essai --------------------------------


def _doc_avec(*slugs: str) -> str:
    lignes = ["# Inventaire de la ville", ""]
    lignes += [f"Une brique `{s}` dont on parle." for s in slugs]
    return "\n".join(lignes)


def _source_carte(slug_extra: str | None = None) -> str:
    specials = ['"T": {"slug": "terminus", "nom": "Terminus"}']
    if slug_extra:
        specials.append(f'"Z": {{"slug": "{slug_extra}", "nom": "Zoo"}}')
    return (
        "DISTRICTS: tuple[dict, ...] = (\n"
        '    {"slug": "faubourg", "nom": "Le Faubourg"},\n'
        ")\n"
        "SPECIAUX: dict[str, dict] = {\n"
        + ",\n".join(specials)
        + "\n}\n"
        "BARRIERES: tuple[dict, ...] = (\n"
        '    {"slug": "pont", "nom": "Le pont"},\n'
        ")\n"
        'def _piece(slug, *a): pass\n'
        '_piece("kiosque", "Kiosque")\n'
    )


def _facade() -> dict[str, str]:
    """Un petit dépôt où TOUS les slugs de code sont cités — le juge doit être vert."""
    return {
        "app/carte.py": _source_carte(),
        "app/vehicules.py": '_v("auto", "Berline", "auto")\n',
        "app/pietons.py": '_p("passant", "Passant")\n'
        "GANGS: list[dict] = [\n"
        '    {"slug": "cravates", "nom": "Les Cravates"},\n'
        "]\n",
        "app/missions/__init__.py": 'PERSONNAGES: list[Personnage] = [\n'
        '    {"slug": "ti_guy", "nom": "Ti-Guy"},\n'
        "]\n",
        "docs/carte.md": _doc_avec(
            "terminus", "faubourg", "pont", "kiosque", "auto", "passant", "cravates", "ti_guy"
        ),
    }


def test_un_depot_au_complet_est_vert():
    assert juge.juger(_facade()) == []


def test_un_slug_ajoute_sans_sa_ligne_rougit():
    sources = _facade()
    sources["app/carte.py"] = _source_carte("zoo")  # un bâtiment neuf, pas dans le doc
    reproches = juge.juger(sources)
    assert any("`zoo`" in r for r in reproches)


def test_un_doc_dont_le_slug_a_ete_renomme_rougit():
    sources = _facade()
    # Le code renomme le garage en « atelier » : l'inventaire cite toujours `garage`,
    # donc `atelier` manque.
    sources["app/carte.py"] = _source_carte().replace("terminus", "atelier")
    reproches = juge.juger(sources)
    assert any("`atelier`" in r for r in reproches)


def test_le_juge_rougit_sans_rien_lire():
    # Des sources présentes mais vides de slugs : un bloc renommé, pas une ville vide.
    sources = juge.juger({
        "app/carte.py": "x = 1\n",
        "app/vehicules.py": "x = 1\n",
        "app/pietons.py": "x = 1\n",
        "app/missions/__init__.py": "x = 1\n",
        "docs/carte.md": "# vide\n",
    })
    assert any("aucun slug" in r for r in sources)


def test_le_juge_signal_un_fichier_manquant():
    sources = _facade()
    del sources["app/missions/__init__.py"]
    reproches = juge.juger(sources)
    assert any("app/missions/__init__.py" in r for r in reproches)